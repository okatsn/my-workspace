#!/usr/bin/env python3
"""Repair DVC gdrive cache objects that were accidentally renamed with a
stray file extension (e.g. ``<hash>.png`` instead of ``<hash>``) during a
manual cross-remote Google Drive migration.

Background
----------
DVC's content-addressed cache stores each file under
``<remote-root>/files/md5/<first-2-hex>/<remaining-30-hex>`` (plus a literal
``.dir`` suffix for directory manifests, which is legitimate and must never
be touched). When some of these objects were manually copied between Google
Drive accounts/folders, Drive's web uploader silently appended an extension
guessed from the file's sniffed content type (e.g. ``.png``). DVC looks up
objects by the *exact* hash string, so any suffixed object becomes invisible
to ``dvc pull`` / ``dvc fetch``, even though the bytes are present and intact.

What this script does
----------------------
1. Authenticates against the Google Drive API (v2, via PyDrive2) using an
   existing cached OAuth credentials JSON (e.g. the file DVC/PyDrive2 itself
   caches under ``~/.cache/pydrive2fs/<client_id>/default.json``).
2. Resolves ``<root-id>/files/md5`` and enumerates only its direct two-hex
   subfolders (``00``..``ff``) and their direct children. It never recurses
   or touches anything outside this subtree.
3. Classifies every child name:
     - exact 30 lowercase-hex chars              -> already correct, no-op
     - 30 hex chars + literal ``.dir``            -> legitimate dir object, no-op
     - 30 hex chars + exactly one other extension -> rename *candidate*
     - anything else (unexpected shape, e.g.
       ``<hash>.dir.png`` with two extensions)    -> anomaly, reported only
4. For every rename candidate, it asks Google Drive for that object's own
   ``md5Checksum`` and requires it to equal ``folder + stem`` (the hash the
   path implies) before doing anything. If the checksum is missing or does
   not match, the object is left completely untouched and flagged loudly for
   manual review.
5. If a sibling already has the "correct" bare-hash name, the candidate is
   never renamed over it (that would silently destroy one of the two Drive
   objects). Such cases are reported; if the duplicate's checksum+size are
   byte-identical to the correct sibling, it is additionally eligible for
   being moved to Google Drive's reversible Trash with ``--trash-duplicates``
   (never hard-deleted -- this script contains no call to ``Delete()``).
6. Renames (and trashes) are metadata-only Drive API calls
   (``files().patch()`` / ``files().trash()``); file content is never
   re-uploaded or re-downloaded.

Safety model
------------
- Dry-run by default. Nothing is ever changed unless ``--apply`` is passed.
- ``--apply`` additionally requires an interactive terminal and typing an
  exact confirmation phrase that embeds the *live* count of planned actions,
  so a stale/cached command can't blindly re-apply a plan that no longer
  matches the remote's current state.
- Every per-item API call is wrapped with bounded retries; a single failure
  never aborts the whole run, but is recorded and surfaces in the exit code.
- A full machine-readable JSON audit log (every item classified, every
  decision, every id/checksum involved) is always written, even in dry-run.
- Exit code is non-zero whenever anything exists that needs human attention
  (anomalies, checksum mismatches, duplicate conflicts, failed operations),
  so this script is safe to wire into a periodic health-check if desired.

Prerequisites
-------------
    pip install pydrive2

Usage
-----
    # Inspect only; nothing on Drive is changed.
    python scripts/dvc_gdrive_fix_extensions.py \\
        --credentials ~/.cache/pydrive2fs/<client_id>/default.json \\
        --root-id 1f4gmbAU5e6PsOzjStOz9uUSEA4lMk_GT

    # Actually rename verified candidates (interactive confirmation required).
    python scripts/dvc_gdrive_fix_extensions.py \\
        --credentials ~/.cache/pydrive2fs/<client_id>/default.json \\
        --root-id 1f4gmbAU5e6PsOzjStOz9uUSEA4lMk_GT \\
        --apply

    # Canary run: only touch the first 5 verified candidates.
    python scripts/dvc_gdrive_fix_extensions.py \\
        --credentials ... --root-id ... --apply --limit 5

    # Also move confirmed byte-identical duplicates to Drive Trash
    # (reversible; only ever used alongside --apply).
    python scripts/dvc_gdrive_fix_extensions.py \\
        --credentials ... --root-id ... --apply --trash-duplicates

After running with ``--apply``, validate end-to-end with:
    dvc status -c
    dvc pull
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

HEX2_RE = re.compile(r"^[0-9a-f]{2}$")
HEX30_RE = re.compile(r"^[0-9a-f]{30}$")
# Exactly one trailing extension with no embedded dots, e.g. "<30hex>.png".
# Deliberately does NOT match "<30hex>.dir.png" (two extensions) -- those
# are anomalies and must be reported, not guessed at.
CANDIDATE_RE = re.compile(r"^([0-9a-f]{30})\.([^./]+)$")

RETRYABLE_HTTP_CODES = {403, 408, 409, 429, 500, 502, 503, 504}
MAX_RETRIES = 5
RETRY_BASE_DELAY = 1.5


class FatalSetupError(RuntimeError):
    """Raised for configuration/auth problems that must stop the script."""


@dataclass
class LogEntry:
    folder: str
    title: str
    file_id: str
    classification: str
    detail: str
    expected_md5: Optional[str] = None
    actual_md5: Optional[str] = None
    new_name: Optional[str] = None
    sibling_id: Optional[str] = None
    action: str = "none"  # none | renamed | rename_failed | trashed | trash_failed


@dataclass
class Summary:
    total_entries: int = 0
    ok_exact: int = 0
    ok_dir: int = 0
    anomalies: int = 0
    checksum_mismatch: int = 0
    duplicate_conflict: int = 0
    duplicate_confirmed: int = 0
    rename_candidates: int = 0
    renamed: int = 0
    rename_failed: int = 0
    trashed: int = 0
    trash_failed: int = 0

    def needs_attention(self) -> bool:
        return bool(
            self.anomalies
            or self.checksum_mismatch
            or self.duplicate_conflict
            or self.rename_failed
            or self.trash_failed
        )


def load_credentials(path: Path):
    """Build PyDrive2/oauth2client credentials from a cached OAuth JSON.

    Never logs or echoes any secret contained within.
    """
    from oauth2client.client import OAuth2Credentials

    if not path.is_file():
        raise FatalSetupError(f"Credentials file not found: {path}")

    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise FatalSetupError(f"Could not read/parse credentials file {path}: {exc}") from exc

    required = ["access_token", "client_id", "client_secret", "refresh_token", "token_uri"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise FatalSetupError(
            f"Credentials file {path} is missing required field(s): {', '.join(missing)}"
        )

    return OAuth2Credentials(
        access_token=data["access_token"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        refresh_token=data["refresh_token"],
        token_expiry=data.get("token_expiry"),
        token_uri=data["token_uri"],
        user_agent=data.get("user_agent"),
    )


def build_drive(credentials_path: Path):
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive

    creds = load_credentials(credentials_path)
    gauth = GoogleAuth()
    gauth.settings["save_credentials"] = False
    gauth.credentials = creds
    try:
        gauth.Refresh()
    except Exception as exc:  # noqa: BLE001 - surface any auth failure clearly
        raise FatalSetupError(
            f"Failed to refresh Google Drive credentials from {credentials_path}: {exc}"
        ) from exc
    return GoogleDrive(gauth)


def with_retry(func, *args, description: str, **kwargs):
    """Call func(*args, **kwargs), retrying on transient Drive API errors."""
    from pydrive2.files import ApiRequestError

    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except ApiRequestError as exc:
            code = exc.error.get("code", 0) if getattr(exc, "error", None) else 0
            last_exc = exc
            if code not in RETRYABLE_HTTP_CODES or attempt == MAX_RETRIES:
                raise
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            print(
                f"  [retry] {description} failed with HTTP {code} "
                f"(attempt {attempt}/{MAX_RETRIES}); retrying in {delay:.1f}s",
                file=sys.stderr,
            )
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def find_child(drive, parent_id: str, name: str, *, expect_folder: bool) -> str:
    q = f"'{parent_id}' in parents and title = '{name}' and trashed = false"
    matches = with_retry(
        lambda: list(drive.ListFile({"q": q, "maxResults": 10}).GetList()),
        description=f"lookup '{name}' under {parent_id}",
    )
    matches = [m for m in matches if m["title"] == name]
    if expect_folder:
        matches = [m for m in matches if m.get("mimeType") == "application/vnd.google-apps.folder"]
    if not matches:
        raise FatalSetupError(f"Could not find folder '{name}' under parent id {parent_id}.")
    if len(matches) > 1:
        raise FatalSetupError(
            f"Ambiguous: found {len(matches)} items named '{name}' under parent id {parent_id}; "
            "refusing to guess which one is the DVC cache root."
        )
    return matches[0]["id"]


def list_children(drive, parent_id: str) -> list[dict]:
    def _list():
        out = []
        file_list = drive.ListFile({"q": f"'{parent_id}' in parents and trashed = false", "maxResults": 1000})
        for page in file_list:
            out.extend(page)
        return out

    return with_retry(_list, description=f"list children of {parent_id}")


def classify_and_process(
    drive,
    folder_title: str,
    children: list[dict],
    *,
    apply_renames: bool,
    trash_duplicates: bool,
    limit: Optional[int],
    counters: dict,
    log: list[LogEntry],
) -> None:
    by_title = {c["title"]: c for c in children}

    for child in children:
        title = child["title"]
        file_id = child["id"]
        counters["total_entries"] += 1

        if HEX30_RE.match(title):
            counters["ok_exact"] += 1
            continue
        if title.endswith(".dir") and HEX30_RE.match(title[:-4]):
            counters["ok_dir"] += 1
            continue

        m = CANDIDATE_RE.match(title)
        if not m or m.group(2) == "dir":
            counters["anomalies"] += 1
            log.append(
                LogEntry(
                    folder=folder_title,
                    title=title,
                    file_id=file_id,
                    classification="anomaly",
                    detail="Name does not match any recognized DVC cache object pattern; left untouched.",
                )
            )
            print(f"  [ANOMALY] {folder_title}/{title} (id={file_id}) -- not touched, needs manual review")
            continue

        stem = m.group(1)
        expected_md5 = folder_title + stem
        actual_md5 = child.get("md5Checksum")

        if not actual_md5 or actual_md5 != expected_md5:
            counters["checksum_mismatch"] += 1
            log.append(
                LogEntry(
                    folder=folder_title,
                    title=title,
                    file_id=file_id,
                    classification="checksum_mismatch",
                    detail="Drive md5Checksum missing or does not match hash implied by path; left untouched.",
                    expected_md5=expected_md5,
                    actual_md5=actual_md5,
                )
            )
            print(
                f"  [MISMATCH] {folder_title}/{title} (id={file_id}): "
                f"expected md5={expected_md5} actual={actual_md5!r} -- not touched"
            )
            continue

        sibling = by_title.get(stem)
        if sibling is not None:
            same_content = (
                sibling.get("md5Checksum") == actual_md5
                and sibling.get("fileSize") == child.get("fileSize")
            )
            if not same_content:
                counters["duplicate_conflict"] += 1
                log.append(
                    LogEntry(
                        folder=folder_title,
                        title=title,
                        file_id=file_id,
                        classification="duplicate_conflict",
                        detail=(
                            "A correctly-named sibling already exists but its checksum/size "
                            "differ from this candidate; refusing to guess. Needs manual review."
                        ),
                        expected_md5=expected_md5,
                        actual_md5=actual_md5,
                        sibling_id=sibling["id"],
                    )
                )
                print(
                    f"  [CONFLICT] {folder_title}/{title} (id={file_id}) vs existing "
                    f"{folder_title}/{stem} (id={sibling['id']}) -- content differs, not touched"
                )
                continue

            counters["duplicate_confirmed"] += 1
            entry = LogEntry(
                folder=folder_title,
                title=title,
                file_id=file_id,
                classification="duplicate_confirmed",
                detail="Byte-identical duplicate of an already correctly-named sibling.",
                expected_md5=expected_md5,
                actual_md5=actual_md5,
                sibling_id=sibling["id"],
            )
            print(
                f"  [DUPLICATE] {folder_title}/{title} (id={file_id}) duplicates "
                f"{folder_title}/{stem} (id={sibling['id']}) -- correct copy already present"
            )
            if trash_duplicates:
                if limit is not None and counters["ops_done"] >= limit:
                    entry.action = "none"
                    entry.detail += " (skipped: --limit reached)"
                elif apply_renames:
                    try:
                        gfile = with_retry(
                            lambda: drive.CreateFile({"id": file_id}),
                            description=f"load file {file_id}",
                        )
                        with_retry(gfile.Trash, description=f"trash {folder_title}/{title}")
                        entry.action = "trashed"
                        counters["trashed"] += 1
                        counters["ops_done"] += 1
                        print(f"    -> moved to Drive Trash (reversible)")
                    except Exception as exc:  # noqa: BLE001
                        entry.action = "trash_failed"
                        entry.detail += f" Trash failed: {exc}"
                        counters["trash_failed"] += 1
                        print(f"    -> FAILED to trash: {exc}", file=sys.stderr)
                else:
                    entry.detail += " (dry-run: would move to Drive Trash)"
            log.append(entry)
            continue

        # Genuine rename candidate: no collision, checksum verified.
        counters["rename_candidates"] += 1
        entry = LogEntry(
            folder=folder_title,
            title=title,
            file_id=file_id,
            classification="rename_candidate",
            detail="Checksum-verified; safe to rename to bare hash.",
            expected_md5=expected_md5,
            actual_md5=actual_md5,
            new_name=stem,
        )
        print(f"  [CANDIDATE] {folder_title}/{title} (id={file_id}) -> {folder_title}/{stem}")

        if apply_renames:
            if limit is not None and counters["ops_done"] >= limit:
                entry.detail += " (skipped: --limit reached)"
            else:
                try:
                    gfile = with_retry(
                        lambda: drive.CreateFile({"id": file_id}),
                        description=f"load file {file_id}",
                    )
                    with_retry(
                        gfile.FetchMetadata,
                        fields="title,md5Checksum,mimeType,fileSize,parents",
                        description=f"fetch metadata for {file_id}",
                    )
                    before_md5 = gfile.get("md5Checksum")
                    if before_md5 != expected_md5:
                        raise RuntimeError(
                            f"checksum changed between scan and rename "
                            f"(was {actual_md5}, now {before_md5}); aborting this rename"
                        )
                    gfile["title"] = stem
                    with_retry(gfile.Upload, description=f"rename {folder_title}/{title} -> {stem}")
                    after_md5 = gfile.get("md5Checksum")
                    if gfile.get("title") != stem or after_md5 != expected_md5:
                        raise RuntimeError(
                            f"post-rename verification failed: title={gfile.get('title')!r} "
                            f"md5={after_md5!r} (expected title={stem!r} md5={expected_md5!r})"
                        )
                    entry.action = "renamed"
                    counters["renamed"] += 1
                    counters["ops_done"] += 1
                    print("    -> renamed (metadata-only, content untouched, verified)")
                except Exception as exc:  # noqa: BLE001 - never let one bad item abort the run
                    entry.action = "rename_failed"
                    entry.detail += f" Rename failed: {exc}"
                    counters["rename_failed"] += 1
                    print(f"    -> FAILED to rename: {exc}", file=sys.stderr)
        log.append(entry)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--credentials",
        required=True,
        type=Path,
        help="Path to a cached PyDrive2/DVC OAuth credentials JSON "
        "(e.g. ~/.cache/pydrive2fs/<client_id>/default.json). Never pass tokens inline.",
    )
    parser.add_argument(
        "--root-id",
        required=True,
        help="Drive folder ID of the DVC gdrive remote root (the id in 'gdrive://<id>').",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform renames (and, with --trash-duplicates, trashing). "
        "Without this flag, the script only inspects and reports (dry-run).",
    )
    parser.add_argument(
        "--trash-duplicates",
        action="store_true",
        help="When a stray-extension object is a byte-identical duplicate of an "
        "already correctly-named sibling, move the duplicate to Drive's "
        "reversible Trash. Only takes effect together with --apply.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of mutating operations (renames + trashes) performed "
        "in this run. Useful for a small canary run before a full --apply.",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("."),
        help="Directory to write the timestamped JSON audit log into (default: current directory).",
    )
    args = parser.parse_args()

    try:
        drive = build_drive(args.credentials)
        files_id = find_child(drive, args.root_id, "files", expect_folder=True)
        md5_id = find_child(drive, files_id, "md5", expect_folder=True)
    except FatalSetupError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2

    subfolders = list_children(drive, md5_id)
    bad = [
        s
        for s in subfolders
        if not (s.get("mimeType") == "application/vnd.google-apps.folder" and HEX2_RE.match(s["title"]))
    ]
    for b in bad:
        print(
            f"  [ANOMALY] unexpected entry directly under files/md5: "
            f"{b['title']!r} (id={b['id']}, mimeType={b.get('mimeType')}) -- not touched",
            file=sys.stderr,
        )
    subfolders = [s for s in subfolders if s not in bad]
    print(f"Found {len(subfolders)} valid two-hex subfolders under files/md5 ({len(bad)} anomalies).")

    counters: dict[str, int] = {
        "total_entries": 0,
        "ok_exact": 0,
        "ok_dir": 0,
        "anomalies": len(bad),
        "checksum_mismatch": 0,
        "duplicate_conflict": 0,
        "duplicate_confirmed": 0,
        "rename_candidates": 0,
        "renamed": 0,
        "rename_failed": 0,
        "trashed": 0,
        "trash_failed": 0,
        "ops_done": 0,
    }
    log: list[LogEntry] = []

    # --- Phase 1: scan everything (read-only), to know the true scope ---
    scan_counters = dict(counters)
    scan_log: list[LogEntry] = []
    for i, sf in enumerate(subfolders, 1):
        children = list_children(drive, sf["id"])
        classify_and_process(
            drive,
            sf["title"],
            children,
            apply_renames=False,
            trash_duplicates=False,
            limit=None,
            counters=scan_counters,
            log=scan_log,
        )
        if i % 32 == 0:
            print(f"...scanned {i}/{len(subfolders)} folders")

    n_renames = scan_counters["rename_candidates"]
    n_trash = scan_counters["duplicate_confirmed"]
    print("\n=== Dry-run scan summary ===")
    for key in (
        "total_entries",
        "ok_exact",
        "ok_dir",
        "rename_candidates",
        "duplicate_confirmed",
        "duplicate_conflict",
        "checksum_mismatch",
        "anomalies",
    ):
        print(f"  {key}: {scan_counters[key]}")

    if not args.apply:
        write_log(args.log_dir, scan_counters, scan_log, applied=False)
        return 1 if Summary(**{k: v for k, v in scan_counters.items() if k != "ops_done"}).needs_attention() else 0

    # --- Phase 2: confirm, then actually apply ---
    if n_renames == 0 and not (args.trash_duplicates and n_trash):
        print("\nNothing to apply (no verified rename candidates" + (" or duplicates" if args.trash_duplicates else "") + ").")
        write_log(args.log_dir, scan_counters, scan_log, applied=False)
        return 1 if Summary(**{k: v for k, v in scan_counters.items() if k != "ops_done"}).needs_attention() else 0

    if not sys.stdin.isatty():
        print(
            "FATAL: --apply requires an interactive terminal to confirm. "
            "Refusing to run non-interactively.",
            file=sys.stderr,
        )
        return 2

    phrase = f"CONFIRM {n_renames} RENAMES"
    if args.trash_duplicates:
        phrase += f" AND {n_trash} TRASH"
    print(f"\nAbout to apply {n_renames} rename(s)" + (f" and {n_trash} trash operation(s)" if args.trash_duplicates else "") + ".")
    if args.limit is not None:
        print(f"(--limit {args.limit} caps the total mutating operations this run)")
    typed = input(f"Type exactly: {phrase}\n> ")
    if typed.strip() != phrase:
        print("Confirmation phrase did not match. Aborting without making any changes.", file=sys.stderr)
        return 2

    counters = dict(scan_counters)
    counters["ops_done"] = 0
    log = []
    for i, sf in enumerate(subfolders, 1):
        children = list_children(drive, sf["id"])
        classify_and_process(
            drive,
            sf["title"],
            children,
            apply_renames=True,
            trash_duplicates=args.trash_duplicates,
            limit=args.limit,
            counters=counters,
            log=log,
        )

    print("\n=== Apply summary ===")
    for key in ("renamed", "rename_failed", "trashed", "trash_failed"):
        print(f"  {key}: {counters[key]}")

    write_log(args.log_dir, counters, log, applied=True)
    summary = Summary(**{k: v for k, v in counters.items() if k != "ops_done"})
    if summary.needs_attention():
        print(
            "\nSome items need manual review or failed -- see the audit log. Exiting non-zero.",
            file=sys.stderr,
        )
        return 1

    print("\nDone. Now validate with: dvc status -c   and   dvc pull")
    return 0


def write_log(log_dir: Path, counters: dict, log: list[LogEntry], *, applied: bool) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = "apply" if applied else "dryrun"
    path = log_dir / f"dvc_gdrive_fix_extensions_{suffix}_{timestamp}.json"
    payload = {
        "applied": applied,
        "generated_at": timestamp,
        "summary": {k: v for k, v in counters.items() if k != "ops_done"},
        "entries": [vars(e) for e in log],
    }
    path.write_text(json.dumps(payload, indent=2))
    print(f"\nAudit log written to: {path}")
    return path


if __name__ == "__main__":
    sys.exit(main())
