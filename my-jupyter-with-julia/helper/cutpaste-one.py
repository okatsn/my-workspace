#!/usr/bin/env python3
"""
cutpaste-one.py

Execute exactly one CUTPASTE operation in the current workspace.

Examples:

    python cutpaste-one.py 044 --dry-run
    python cutpaste-one.py 044

"044" expands to "logseq-migrate-044".

Semantics:

    move:
        destination HERE line -> exact bytes between BEGIN and END
        source BEGIN..END      -> deleted

    copy:
        destination HERE line -> exact bytes between BEGIN and END
        source BEGIN line      -> deleted
        source END line        -> deleted
        source payload         -> retained exactly

    drop:
        source BEGIN..END      -> deleted
        HERE                   -> must not exist

The script performs byte-level operations. It does not parse or normalize text.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
}

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")

ATTR_RE = re.compile(
    r"""(?<!\S)([A-Za-z][A-Za-z0-9_-]*)=(?:"([^"]*)"|'([^']*)'|([^\s]+))"""
)

ANY_MARKER_RE = re.compile(rb"CUTPASTE:(BEGIN|END|HERE):([A-Za-z0-9_.-]+)")


class CutPasteError(RuntimeError):
    pass


@dataclass(frozen=True)
class Occurrence:
    kind: str
    path: Path
    line_no: int

    # Byte offsets covering the complete marker line,
    # including its line ending when present.
    start: int
    end: int

    attrs: dict[str, str]


@dataclass(frozen=True)
class Patch:
    start: int
    end: int
    replacement: bytes
    why: str


def die(message: str) -> None:
    raise CutPasteError(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute one CUTPASTE operation exactly."
    )

    parser.add_argument(
        "id",
        help="numeric suffix such as 044, or a full CUTPASTE ID",
    )

    parser.add_argument(
        "--prefix",
        default="logseq-migrate-",
        help="prefix for numeric IDs; default: logseq-migrate-",
    )

    parser.add_argument(
        "--root",
        default=".",
        help="workspace root; default: current directory",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and report without modifying files",
    )

    return parser.parse_args()


def normalize_id(raw: str, prefix: str) -> str:
    if raw.isdigit():
        cid = f"{prefix}{raw.zfill(3)}"
    else:
        cid = raw

    if not ID_RE.fullmatch(cid):
        die(f"invalid CUTPASTE id: {cid!r}")

    return cid


def iter_files(root: Path):
    """
    Walk deterministically.

    Symlinks are not followed or edited.
    """

    for dirpath, dirnames, filenames in os.walk(
        root,
        followlinks=False,
    ):
        dirnames[:] = sorted(
            d
            for d in dirnames
            if d not in SKIP_DIRS and not Path(dirpath, d).is_symlink()
        )

        for name in sorted(filenames):
            path = Path(dirpath, name)

            if path.is_symlink() or not path.is_file():
                continue

            yield path


def parse_attrs(
    line: bytes,
    marker_end: int,
    path: Path,
    line_no: int,
) -> dict[str, str]:

    try:
        suffix = line[marker_end:].decode("utf-8")
    except UnicodeDecodeError as exc:
        die(f"{path}:{line_no}: marker line is not valid UTF-8: {exc}")

    result: dict[str, str] = {}

    for match in ATTR_RE.finditer(suffix):
        key = match.group(1)

        value = next(item for item in match.groups()[1:] if item is not None)

        if key in result:
            die(f"{path}:{line_no}: duplicate attribute {key!r}")

        result[key] = value

    return result


def find_occurrences(
    root: Path,
    cid: str,
) -> tuple[list[Occurrence], dict[Path, bytes]]:

    token = cid.encode("utf-8")

    target_re = re.compile(
        rb"CUTPASTE:(BEGIN|END|HERE):" + re.escape(token) + rb"(?![A-Za-z0-9_.-])"
    )

    found: list[Occurrence] = []
    cache: dict[Path, bytes] = {}

    for path in iter_files(root):
        data = path.read_bytes()

        if token not in data or b"CUTPASTE:" not in data:
            continue

        cache[path] = data

        offset = 0

        for line_no, line in enumerate(
            data.splitlines(keepends=True),
            1,
        ):
            matches = list(target_re.finditer(line))

            if len(matches) > 1:
                die(f"{path}:{line_no}: target ID occurs more than once on one line")

            if matches:
                match = matches[0]

                attrs = parse_attrs(
                    line,
                    match.end(),
                    path,
                    line_no,
                )

                found.append(
                    Occurrence(
                        kind=match.group(1).decode("ascii"),
                        path=path,
                        line_no=line_no,
                        start=offset,
                        end=offset + len(line),
                        attrs=attrs,
                    )
                )

            offset += len(line)

    return found, cache


def root_rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def normalize_marker_path(
    raw: str,
    attribute: str,
) -> str:

    p = PurePosixPath(raw)

    if p.is_absolute() or ".." in p.parts:
        die(f"unsafe {attribute}= path: {raw!r}")

    normalized = p.as_posix()

    if normalized in ("", "."):
        die(f"empty {attribute}= path")

    return normalized


def check_source_regions_well_formed(
    data: bytes,
    path: Path,
) -> None:
    """
    Verify that BEGIN/END regions in the source file do not
    nest or overlap.

    This checks all CUTPASTE IDs, not merely the requested one.
    """

    active: str | None = None

    for line_no, line in enumerate(
        data.splitlines(keepends=True),
        1,
    ):
        matches = list(ANY_MARKER_RE.finditer(line))

        region_matches = [m for m in matches if m.group(1) in (b"BEGIN", b"END")]

        if len(region_matches) > 1:
            die(f"{path}:{line_no}: multiple BEGIN/END markers on one line")

        if not region_matches:
            continue

        match = region_matches[0]

        kind = match.group(1).decode("ascii")
        rid = match.group(2).decode("ascii")

        if kind == "BEGIN":
            if active is not None:
                die(
                    f"{path}:{line_no}: "
                    f"nested/overlapping region: "
                    f"{rid} begins inside {active}"
                )

            active = rid

        else:
            if active is None:
                die(f"{path}:{line_no}: END:{rid} has no active BEGIN")

            if active != rid:
                die(f"{path}:{line_no}: END:{rid} closes BEGIN:{active}")

            active = None

    if active is not None:
        die(f"{path}: unterminated BEGIN:{active}")


def apply_patches(
    original: bytes,
    patches: list[Patch],
    path: Path,
) -> bytes:

    ordered = sorted(
        patches,
        key=lambda p: (p.start, p.end),
    )

    # Verify that no edits overlap.
    for first, second in zip(
        ordered,
        ordered[1:],
    ):
        if second.start < first.end:
            die(f"overlapping edits in {path}: {first.why!r} and {second.why!r}")

    result = original

    # Apply from right to left so original offsets remain valid.
    for patch in reversed(ordered):
        result = result[: patch.start] + patch.replacement + result[patch.end :]

    return result


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fsync_dir(path: Path) -> None:
    """
    Best-effort directory fsync on POSIX so the rename is durable.
    """

    if os.name == "nt":
        return

    fd = os.open(path, os.O_RDONLY)

    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(
    path: Path,
    data: bytes,
    mode: int,
) -> None:
    """
    Write a temporary file beside the destination, then atomically
    replace that one file.
    """

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.cutpaste-",
        dir=path.parent,
    )

    tmp = Path(tmp_name)

    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())

        os.chmod(tmp, mode)

        # Atomic for this individual file because tmp is created
        # in the same directory/filesystem.
        os.replace(tmp, path)

        fsync_dir(path.parent)

    except BaseException:
        try:
            tmp.unlink(missing_ok=True)
        finally:
            raise


def main() -> int:
    args = parse_args()

    root = Path(args.root).resolve()

    if not root.is_dir():
        die(f"workspace root is not a directory: {root}")

    cid = normalize_id(
        args.id,
        args.prefix,
    )

    found, cache = find_occurrences(
        root,
        cid,
    )

    by_kind = {
        kind: [item for item in found if item.kind == kind]
        for kind in ("BEGIN", "END", "HERE")
    }

    if len(by_kind["BEGIN"]) != 1:
        die(f"{cid}: expected exactly 1 BEGIN, found {len(by_kind['BEGIN'])}")

    if len(by_kind["END"]) != 1:
        die(f"{cid}: expected exactly 1 END, found {len(by_kind['END'])}")

    begin = by_kind["BEGIN"][0]
    end = by_kind["END"][0]

    if begin.path != end.path:
        die(f"{cid}: BEGIN and END are in different files")

    if begin.start >= end.start:
        die(f"{cid}: END appears before BEGIN")

    op = begin.attrs.get("op")

    if op not in {"move", "copy", "drop"}:
        die(f"{begin.path}:{begin.line_no}: op must be move, copy, or drop; got {op!r}")

    expected_here_count = 0 if op == "drop" else 1

    if len(by_kind["HERE"]) != expected_here_count:
        die(
            f"{cid}: op={op} requires "
            f"{expected_here_count} HERE marker(s), "
            f"found {len(by_kind['HERE'])}"
        )

    source = begin.path
    source_data = cache[source]

    check_source_regions_well_formed(
        source_data,
        source,
    )

    #
    # This is the important operation:
    #
    # payload is EXACTLY the byte sequence between the complete
    # BEGIN marker line and the complete END marker line.
    #
    payload = source_data[begin.end : end.start]

    #
    # Refuse to move/copy/drop another live CUTPASTE marker.
    #
    nested_marker = ANY_MARKER_RE.search(payload)

    if nested_marker:
        die(
            f"{cid}: payload contains another CUTPASTE marker "
            f"({nested_marker.group(0).decode('ascii')}); "
            "refusing"
        )

    patches: dict[Path, list[Patch]] = {}
    originals: dict[Path, bytes] = {}

    def add_patch(
        path: Path,
        patch: Patch,
    ) -> None:

        if path not in originals:
            originals[path] = cache[path] if path in cache else path.read_bytes()

        patches.setdefault(
            path,
            [],
        ).append(patch)

    #
    # Source-side operation.
    #
    if op in {"move", "drop"}:
        add_patch(
            source,
            Patch(
                start=begin.start,
                end=end.end,
                replacement=b"",
                why=f"remove {op} source region",
            ),
        )

    else:
        # copy:
        # preserve payload exactly;
        # remove only the marker lines.
        add_patch(
            source,
            Patch(
                start=begin.start,
                end=begin.end,
                replacement=b"",
                why="remove source BEGIN marker",
            ),
        )

        add_patch(
            source,
            Patch(
                start=end.start,
                end=end.end,
                replacement=b"",
                why="remove source END marker",
            ),
        )

    destination: Path | None = None

    #
    # Destination-side operation.
    #
    if op in {"move", "copy"}:
        to_raw = begin.attrs.get("to")

        if not to_raw:
            die(f"{begin.path}:{begin.line_no}: op={op} requires to=")

        # The #Heading fragment is planning metadata.
        # The physical HERE marker is authoritative.
        to_file = normalize_marker_path(
            to_raw.split("#", 1)[0],
            "to",
        )

        here = by_kind["HERE"][0]
        destination = here.path

        actual_to = root_rel(
            root,
            destination,
        )

        if actual_to != to_file:
            die(f"{cid}: to= says {to_file!r}, but HERE is in {actual_to!r}")

        from_raw = here.attrs.get("from")

        if not from_raw:
            die(f"{here.path}:{here.line_no}: HERE requires from=")

        actual_from = root_rel(
            root,
            source,
        )

        normalized_from = normalize_marker_path(
            from_raw,
            "from",
        )

        if normalized_from != actual_from:
            die(f"{cid}: from= says {from_raw!r}, but BEGIN is in {actual_from!r}")

        seq = here.attrs.get("seq")

        if seq is None or not seq.isdigit() or int(seq) < 1:
            die(f"{here.path}:{here.line_no}: HERE requires positive integer seq=")

        #
        # Replace the COMPLETE HERE LINE by the payload.
        #
        add_patch(
            destination,
            Patch(
                start=here.start,
                end=here.end,
                replacement=payload,
                why="replace HERE with exact source payload",
            ),
        )

    #
    # Compute every resulting file completely in memory before
    # making any filesystem changes.
    #
    outputs = {
        path: apply_patches(
            originals[path],
            file_patches,
            path,
        )
        for path, file_patches in patches.items()
    }

    print(f"ID:          {cid}")
    print(f"op:          {op}")
    print(f"source:      {root_rel(root, source)}")

    if destination is not None:
        print(f"destination: {root_rel(root, destination)}")

    print(f"payload:     {len(payload)} bytes")
    print(f"sha256:      {sha256(payload)}")

    for path in sorted(
        outputs,
        key=lambda p: root_rel(root, p),
    ):
        print(f"will write:  {root_rel(root, path)}")

    if args.dry_run:
        print("DRY RUN: validation passed; no files changed")
        return 0

    #
    # Optimistic concurrency check.
    #
    # If an editor or another agent changed any touched file after
    # our preflight scan, refuse to continue.
    #
    for path, original in originals.items():
        if path.read_bytes() != original:
            die(
                f"{root_rel(root, path)} changed during "
                "preflight; aborting before writes"
            )

    modes = {path: stat.S_IMODE(path.stat().st_mode) for path in outputs}

    written: list[Path] = []

    try:
        for path in sorted(
            outputs,
            key=lambda p: root_rel(root, p),
        ):
            #
            # Check once more immediately before this file is
            # replaced.
            #
            if path.read_bytes() != originals[path]:
                die(f"{root_rel(root, path)} changed concurrently; aborting")

            atomic_write(
                path,
                outputs[path],
                modes[path],
            )

            written.append(path)

        #
        # Exact post-write verification.
        #
        for path, expected in outputs.items():
            actual = path.read_bytes()

            if actual != expected:
                die(f"post-write verification failed for {root_rel(root, path)}")

    except BaseException:
        #
        # Best-effort rollback for ordinary exceptions.
        #
        # A process kill, OS crash, or power failure cannot be made
        # transactionally atomic across multiple independent files;
        # Git should be the recovery boundary for that case.
        #
        for path in reversed(written):
            try:
                atomic_write(
                    path,
                    originals[path],
                    modes[path],
                )
            except BaseException as rollback_error:
                print(
                    f"ROLLBACK FAILED for {path}: {rollback_error}",
                    file=os.sys.stderr,
                )

        raise

    print("OK: operation applied and byte-for-byte post-write verification passed")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except CutPasteError as exc:
        print(
            f"ERROR: {exc}",
            file=os.sys.stderr,
        )
        raise SystemExit(2)
