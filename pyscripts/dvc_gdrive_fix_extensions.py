#!/usr/bin/env python3
"""Repair DVC gdrive cache objects that carry a stray file extension.

Background
----------
DVC stores cache objects at ``<root>/files/md5/<2 hex>/<30 hex>`` (directory
manifests additionally end with a literal ``.dir``). After a manual Google
Drive migration, some objects were renamed to ``<30 hex>.png`` (Drive's web
uploader appends an extension guessed from the content). DVC looks objects up
by exact name, so these objects are invisible to ``dvc pull``.

What this script does
---------------------
1. SCAN (read-only): list ``files/md5/<2 hex>/*`` only, never anything else.
   Every object is classified, and a *plan* is built:
     - rename ``<30 hex>.<ext>`` -> ``<30 hex>``, only if Drive's own
       ``md5Checksum`` equals ``<folder><30 hex>`` and no object with the
       target name exists;
     - trash (optional, ``--trash-duplicates``) a stray-extension object that
       is a byte-identical duplicate of an existing correctly named object.
   Anything else (duplicate Drive names, checksum mismatch, odd names,
   conflicting duplicates) is reported as a finding and never touched.
2. The plan is written to a file. Without ``--apply`` the script stops here.
3. APPLY (``--apply``): after an interactive typed confirmation, exactly the
   confirmed plan is executed (never re-discovered). Before each action the
   object is re-fetched by ID and its name, parent folder, checksum and
   trashed state must still match the plan; a rename also re-checks that the
   target name is still free. Each action is journaled (JSONL, fsynced). The
   run stops at the first failure unless ``--continue-on-error`` is given.

Renames are metadata-only (``files.patch``); content is never re-uploaded.
Trashing is reversible; nothing is ever hard-deleted.

Usage
-----
    pip install pydrive2

    # Inspect only
    python scripts/dvc_gdrive_fix_extensions.py \\
        --credentials ~/.cache/pydrive2fs/<client_id>/default.json \\
        --root-id <remote folder id>

    # Rename (canary: first 5 only); add --trash-duplicates to also trash
    python scripts/dvc_gdrive_fix_extensions.py ... --apply --limit 5

Afterwards validate with ``dvc status -c`` and ``dvc pull``.
Exit code is non-zero if anything needs attention (findings or failures).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import random
import re
import sys
import time
import uuid
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

FOLDER_MIME = "application/vnd.google-apps.folder"
HEX2_RE = re.compile(r"^[0-9a-f]{2}$")
HEX30_RE = re.compile(r"^[0-9a-f]{30}$")
# Exactly one extension; "<30 hex>.dir.png" deliberately does not match.
CANDIDATE_RE = re.compile(r"^([0-9a-f]{30})\.[^./]+$")

RETRY_CODES = {429, 500, 502, 503, 504}
RATE_LIMIT_REASONS = {"rateLimitExceeded", "userRateLimitExceeded", "sharingRateLimitExceeded", "backendError"}
MAX_RETRIES = 5


class FatalError(RuntimeError):
    """Setup/validation problem; the run must stop."""


class DriftError(RuntimeError):
    """The remote no longer matches the plan; the action was not performed."""


@dataclass
class Action:
    kind: str  # "rename" | "trash"
    folder: str
    folder_id: str
    file_id: str
    old_name: str
    new_name: str  # rename target; for trash, the surviving object's name
    md5: str
    survivor_id: Optional[str] = None


# ---------------------------------------------------------------- Drive helpers


def build_drive(credentials_path: Path):
    from oauth2client.client import OAuth2Credentials
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive

    try:
        creds = OAuth2Credentials.from_json(credentials_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise FatalError(f"Cannot load credentials from {credentials_path}: {exc}") from exc
    if not creds.refresh_token or not creds.client_id:
        raise FatalError(f"{credentials_path} has no refresh_token/client_id.")

    gauth = GoogleAuth()
    gauth.settings["save_credentials"] = False
    gauth.credentials = creds
    try:
        gauth.Refresh()
    except Exception as exc:  # noqa: BLE001
        raise FatalError(f"Failed to refresh Drive credentials: {exc}") from exc
    return GoogleDrive(gauth)


def _retryable(exc) -> bool:
    code = exc.error.get("code", 0)
    if code == 403:
        reason = (exc.error.get("errors") or [{}])[0].get("reason")
        return reason in RATE_LIMIT_REASONS
    return code in RETRY_CODES


def with_retry(func, *args, **kwargs):
    """Retry transient Drive API errors with jittered exponential backoff."""
    from pydrive2.files import ApiRequestError

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except ApiRequestError as exc:
            if attempt == MAX_RETRIES or not _retryable(exc):
                raise
            delay = 1.5 * 2 ** (attempt - 1) * random.uniform(0.5, 1.5)
            print(f"  [retry] Drive API error, attempt {attempt}/{MAX_RETRIES}, sleeping {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)


def list_query(drive, query: str) -> list[dict]:
    def _run():
        out = []
        for page in drive.ListFile({"q": query, "maxResults": 1000}):
            out.extend(page)
        return out

    return with_retry(_run)


def list_children(drive, parent_id: str) -> list[dict]:
    return list_query(drive, f"'{parent_id}' in parents and trashed = false")


def find_unique_folder(drive, parent_id: str, name: str) -> str:
    hits = [
        c for c in list_children(drive, parent_id)
        if c["title"] == name and c.get("mimeType") == FOLDER_MIME
    ]
    if len(hits) != 1:
        raise FatalError(f"Expected exactly one folder '{name}' under {parent_id}, found {len(hits)}.")
    return hits[0]["id"]


def fetch(drive, file_id: str):
    f = drive.CreateFile({"id": file_id})
    with_retry(f.FetchMetadata, fields="title,md5Checksum,parents,labels")
    return f


def check_state(drive, file_id: str, *, name: str, parent_id: str, md5: str, trashed: bool = False):
    """Re-fetch an object by ID and require it to still match the plan."""
    f = fetch(drive, file_id)
    actual = {
        "name": f.get("title"),
        "parents": [p["id"] for p in f.get("parents", [])],
        "md5": f.get("md5Checksum"),
        "trashed": bool(f.get("labels", {}).get("trashed")),
    }
    expected = {"name": name, "parents": [parent_id], "md5": md5, "trashed": trashed}
    if actual != expected:
        raise DriftError(f"object {file_id} changed since the scan: expected {expected}, found {actual}")
    return f


# ------------------------------------------------------------------------ scan


def scan(drive, md5_id: str):
    """Read-only. Returns (plan, findings, counts)."""
    plan: list[Action] = []
    findings: list[dict] = []
    counts: Counter = Counter()

    top = list_children(drive, md5_id)
    folders = [t for t in top if t.get("mimeType") == FOLDER_MIME and HEX2_RE.match(t["title"])]
    for t in top:
        if t not in folders:
            findings.append({"kind": "unexpected_entry", "folder": "", "name": t["title"], "file_id": t["id"],
                             "detail": "Not a two-hex folder directly under files/md5."})
    dup_folders = [n for n, c in Counter(f["title"] for f in folders).items() if c > 1]
    if dup_folders:
        raise FatalError(f"Duplicate folder names under files/md5: {dup_folders}. Resolve manually first.")
    print(f"Scanning {len(folders)} folders under files/md5 ...")

    for sf in folders:
        folder, folder_id = sf["title"], sf["id"]
        children = list_children(drive, folder_id)
        by_title = defaultdict(list)
        for c in children:
            by_title[c["title"]].append(c)

        for c in children:
            name = c["title"]
            counts["entries"] += 1

            def finding(kind, detail, **extra):
                findings.append({"kind": kind, "folder": folder, "name": name, "file_id": c["id"],
                                 "detail": detail, **extra})

            if len(by_title[name]) > 1:
                finding("duplicate_name", "Several Drive objects share this name in the folder.")
            elif HEX30_RE.match(name):
                counts["ok"] += 1
            elif name.endswith(".dir") and HEX30_RE.match(name[:-4]):
                counts["ok_dir"] += 1
            elif not (m := CANDIDATE_RE.match(name)):
                finding("unrecognized_name", "Does not look like a DVC cache object.")
            else:
                stem, expected = m.group(1), folder + m.group(1)
                actual = c.get("md5Checksum")
                targets = by_title.get(stem, [])
                if actual != expected:
                    finding("checksum_mismatch", "Drive md5 does not match the hash implied by the path.",
                            expected_md5=expected, actual_md5=actual)
                elif len(targets) > 1:
                    finding("target_ambiguous", "Several objects already have the target name.")
                elif targets:
                    t = targets[0]
                    if t.get("md5Checksum") == actual and t.get("fileSize") == c.get("fileSize"):
                        counts["duplicates"] += 1
                        plan.append(Action("trash", folder, folder_id, c["id"], name, stem, expected, t["id"]))
                    else:
                        finding("duplicate_conflict", "Target name exists with different content.",
                                survivor_id=t["id"])
                else:
                    counts["renames"] += 1
                    plan.append(Action("rename", folder, folder_id, c["id"], name, stem, expected))

    plan.sort(key=lambda a: (a.kind, a.folder, a.old_name, a.file_id))
    return plan, findings, counts


# ----------------------------------------------------------------------- apply


def execute(drive, a: Action) -> None:
    if a.kind == "rename":
        f = check_state(drive, a.file_id, name=a.old_name, parent_id=a.folder_id, md5=a.md5)
        taken = list_query(drive, f"'{a.folder_id}' in parents and title = '{a.new_name}' and trashed = false")
        if taken:
            raise DriftError(f"target name '{a.new_name}' now exists in folder {a.folder}")
        f["title"] = a.new_name
        with_retry(f.Upload)
        check_state(drive, a.file_id, name=a.new_name, parent_id=a.folder_id, md5=a.md5)
    else:
        f = check_state(drive, a.file_id, name=a.old_name, parent_id=a.folder_id, md5=a.md5)
        check_state(drive, a.survivor_id, name=a.new_name, parent_id=a.folder_id, md5=a.md5)
        with_retry(f.Trash)
        check_state(drive, a.file_id, name=a.old_name, parent_id=a.folder_id, md5=a.md5, trashed=True)


class Journal:
    """Append-only JSONL, flushed and fsynced per record so a crash leaves a trail."""

    def __init__(self, path: Path):
        self._f = open(path, "a", encoding="utf-8")

    def write(self, **record) -> None:
        record["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._f.write(json.dumps(record) + "\n")
        self._f.flush()
        os.fsync(self._f.fileno())

    def close(self) -> None:
        self._f.close()


def apply_plan(drive, selected: list[Action], journal: Journal, continue_on_error: bool) -> int:
    failures = 0
    for seq, a in enumerate(selected, 1):
        journal.write(seq=seq, state="start", **asdict(a))
        try:
            execute(drive, a)
        except Exception as exc:  # noqa: BLE001 - any failure is journaled and loud
            failures += 1
            journal.write(seq=seq, state="failed", file_id=a.file_id, error=f"{type(exc).__name__}: {exc}")
            print(f"  [FAILED] {a.kind} {a.folder}/{a.old_name}: {exc}", file=sys.stderr)
            if not continue_on_error:
                print("Stopping at the first failure (use --continue-on-error to override).", file=sys.stderr)
                break
        else:
            journal.write(seq=seq, state="done", file_id=a.file_id)
            print(f"  [{seq}/{len(selected)}] {a.kind}: {a.folder}/{a.old_name}")
    return failures


# ------------------------------------------------------------------------ main


def positive_int(text: str) -> int:
    value = int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--credentials", required=True, type=Path,
                   help="Path to the cached PyDrive2/DVC OAuth credentials JSON (never pass tokens inline).")
    p.add_argument("--root-id", required=True, help="Folder ID of the DVC gdrive remote (the id in gdrive://<id>).")
    p.add_argument("--apply", action="store_true", help="Perform the plan. Default is dry-run.")
    p.add_argument("--trash-duplicates", action="store_true",
                   help="With --apply, also move verified duplicates to Drive's Trash (reversible).")
    p.add_argument("--limit", type=positive_int, help="Execute only the first N planned actions (canary run).")
    p.add_argument("--continue-on-error", action="store_true", help="Do not stop at the first failed action.")
    p.add_argument("--log-dir", type=Path, default=Path("."), help="Where plan/journal files go (default: cwd).")
    args = p.parse_args()

    try:
        drive = build_drive(args.credentials)
        account = drive.GetAbout()["user"]["emailAddress"]
        root = fetch(drive, args.root_id)
        md5_id = find_unique_folder(drive, find_unique_folder(drive, args.root_id, "files"), "md5")
        print(f"Account: {account}\nRemote root: '{root['title']}' ({args.root_id})")
        plan, findings, counts = scan(drive, md5_id)
    except FatalError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2

    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:6]
    args.log_dir.mkdir(parents=True, exist_ok=True)
    plan_path = args.log_dir / f"dvc_gdrive_fix_{run_id}.plan.json"
    plan_path.write_text(json.dumps({
        "root_id": args.root_id, "account": account, "counts": dict(counts),
        "findings": findings, "plan": [asdict(a) for a in plan],
    }, indent=2), encoding="utf-8")

    print(f"\nentries={counts['entries']} ok={counts['ok']} ok_dir={counts['ok_dir']} "
          f"planned_renames={counts['renames']} verified_duplicates={counts['duplicates']} "
          f"findings={len(findings)}")
    for f in findings:
        print(f"  [{f['kind'].upper()}] {f['folder']}/{f['name']} (id={f['file_id']}): {f['detail']}")
    print(f"Plan written to: {plan_path}")

    selected = [a for a in plan if a.kind == "rename" or args.trash_duplicates]
    if args.limit:
        selected = selected[: args.limit]
    needs_attention = bool(findings)

    if not args.apply or not selected:
        if args.apply:
            print("Nothing to apply.")
        return 1 if needs_attention else 0

    if not sys.stdin.isatty():
        print("FATAL: --apply needs an interactive terminal for confirmation.", file=sys.stderr)
        return 2
    n_ren = sum(a.kind == "rename" for a in selected)
    phrase = f"CONFIRM {n_ren} RENAMES" + (f" AND {len(selected) - n_ren} TRASHES" if args.trash_duplicates else "")
    print(f"\nAbout to modify '{root['title']}' as {account}: {n_ren} rename(s), {len(selected) - n_ren} trash(es).")
    if input(f"Type exactly: {phrase}\n> ").strip() != phrase:
        print("Confirmation did not match; nothing was changed.", file=sys.stderr)
        return 2

    journal_path = args.log_dir / f"dvc_gdrive_fix_{run_id}.journal.jsonl"
    journal = Journal(journal_path)
    try:
        failures = apply_plan(drive, selected, journal, args.continue_on_error)
    finally:
        journal.close()
    print(f"\nJournal: {journal_path}\nfailures={failures}")
    if failures or needs_attention:
        return 1
    print("Done. Validate with: dvc status -c  and  dvc pull")
    return 0


if __name__ == "__main__":
    sys.exit(main())
