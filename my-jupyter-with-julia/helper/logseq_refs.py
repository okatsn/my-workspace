#!/usr/bin/env python3
"""
Small reference utility for an OG/file-based Logseq graph.

Examples
--------
# Print pages referenced by explicitly listed journals:
python logseq_refs.py . journals \
    journals/2026-05-04.md journals/2026-05-05.md

# Print pages referenced by an inclusive journal range:
python logseq_refs.py . journals --from 2026-05-04 --to 2026-05-06

# Path form is also accepted for range endpoints:
python logseq_refs.py . journals \
    --from journals/2026-05-04.md --to journals/2026-05-06.md

# Also print the selected journals themselves, before referenced pages:
python logseq_refs.py . journals \
    --from 2026-05-04 --to 2026-05-06 --include-self

# Print blocks that reference a page (canonical name or alias):
python logseq_refs.py . refs "Discontinuous Galerkin"

# Also include blocks that reference namespace children (e.g. [[chat/*]]):
python logseq_refs.py . refs "chat" --list-children

# Also print PAGE's own content before the referencing blocks:
python logseq_refs.py . refs "chat" --include-self

Run `python logseq_refs.py --help` or `... journals --help` for details.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote


WIKILINK = re.compile(r"\[\[([^\[\]]+)\]\]")
TAG = re.compile(r"(?<![\w/])#([A-Za-z0-9_.\-/]+)")
ALIAS = re.compile(r"^\s*-?\s*alias::\s*(.+?)\s*$", re.I | re.M)
BLOCK = re.compile(r"^([ \t]*)-\s+")
FENCE = re.compile(r"^\s*(?:-\s+)?(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"`+[^`\n]*`+")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEPARATOR = "=" * 78


class UserInputError(ValueError):
    pass


def norm(s: str) -> str:
    return s.strip().casefold()


def page_name_from_file(path: Path) -> str:
    """Convert an OG Logseq filename to its page name."""
    return unquote(path.stem).replace("___", "/")


def fenced_line_mask(lines: list[str]) -> list[bool]:
    """Mark lines inside ``` or ~~~ fenced code blocks."""
    mask: list[bool] = []
    open_char: str | None = None
    open_len = 0

    for line in lines:
        m = FENCE.match(line)
        if open_char is None:
            if m:
                marker = m.group(1)
                open_char, open_len = marker[0], len(marker)
                mask.append(True)
            else:
                mask.append(False)
            continue

        mask.append(True)
        if m:
            marker = m.group(1)
            if marker[0] == open_char and len(marker) >= open_len:
                open_char, open_len = None, 0

    return mask


def without_code(text: str) -> str:
    lines = text.splitlines()
    mask = fenced_line_mask(lines)
    return "\n".join(
        INLINE_CODE.sub("", line) for line, is_code in zip(lines, mask) if not is_code
    )


def refs(text: str, include_tags: bool = True) -> list[str]:
    text = without_code(text)
    result = [m.group(1).strip() for m in WIKILINK.finditer(text)]
    if include_tags:
        result.extend(m.group(1) for m in TAG.finditer(text))
    return result


def aliases(text: str) -> list[str]:
    text = without_code(text)
    result: list[str] = []

    for m in ALIAS.finditer(text):
        value = m.group(1)
        linked = WIKILINK.findall(value)
        if linked:
            result.extend(x.strip() for x in linked)
        else:
            result.extend(x.strip() for x in value.split(",") if x.strip())

    return result


class Graph:
    """Minimal page/alias index for a Logseq file graph."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.pages_dir = self.root / "pages"
        self.journals_dir = self.root / "journals"

        if not self.root.is_dir():
            raise UserInputError(f"graph directory does not exist: {self.root}")
        if not self.pages_dir.is_dir():
            raise UserInputError(f"missing pages directory: {self.pages_dir}")

        self.names: dict[str, Path] = {}
        self.canonical: dict[Path, str] = {}

        for path in sorted(
            self.pages_dir.glob("*.md"), key=lambda p: p.name.casefold()
        ):
            path = path.resolve()
            text = path.read_text(encoding="utf-8")
            canonical = page_name_from_file(path)
            self.canonical[path] = canonical

            self._register(canonical, path)
            for alias in aliases(text):
                self._register(alias, path)

    def _register(self, name: str, path: Path) -> None:
        key = norm(name)
        existing = self.names.get(key)
        if existing is not None and existing != path:
            raise UserInputError(
                f"ambiguous page name/alias {name!r}: "
                f"{self.display_path(existing)} and {self.display_path(path)}"
            )
        self.names[key] = path

    def resolve(self, name: str) -> Path | None:
        return self.names.get(norm(name))

    def display_path(self, path: Path) -> str:
        path = path.resolve()
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return str(path)


def block_ranges(text: str) -> tuple[list[str], list[tuple[int, int, int, int]]]:
    """
    Return (lines, blocks), where each block is:
      (start_line, own_content_end, subtree_end, indent)

    Bullets inside fenced code are ignored as block starts.
    """
    lines = text.splitlines(keepends=True)
    code_mask = fenced_line_mask([line.rstrip("\r\n") for line in lines])

    starts: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        # A Logseq code block may start as a list block: `- ```python`.
        # Keep that opener as a structural block boundary, but ignore all
        # other list-looking lines inside the fenced code.
        if code_mask[i] and not (BLOCK.match(line) and FENCE.match(line)):
            continue
        m = BLOCK.match(line)
        if m:
            starts.append((i, len(m.group(1).expandtabs(4))))

    blocks: list[list[int]] = []
    stack: list[int] = []

    for i, (line_no, indent) in enumerate(starts):
        while stack and indent <= blocks[stack[-1]][3]:
            blocks[stack.pop()][2] = line_no

        own_end = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        blocks.append([line_no, own_end, len(lines), indent])
        stack.append(len(blocks) - 1)

    return lines, [tuple(x) for x in blocks]


def resolve_journal_file(graph: Graph, value: str | Path) -> Path:
    """Resolve an explicit journal path relative to GRAPH when needed."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = graph.root / path
    path = path.resolve()

    if not path.is_file():
        raise UserInputError(f"journal file does not exist: {path}")
    if path.parent != graph.journals_dir.resolve() or path.suffix.lower() != ".md":
        raise UserInputError(
            f"journal must be a .md file directly inside {graph.journals_dir}"
        )
    return path


def parse_range_endpoint(graph: Graph, value: str) -> date:
    """Parse DATE, DATE.md, journals/DATE.md, or an absolute journal path."""
    raw = value.strip()

    if ISO_DATE.fullmatch(raw):
        date_text = raw
    else:
        candidate = Path(raw).expanduser()
        if candidate.suffix.lower() != ".md" or not ISO_DATE.fullmatch(candidate.stem):
            raise UserInputError(
                f"invalid journal range endpoint {value!r}; expected YYYY-MM-DD "
                "or a YYYY-MM-DD.md journal path"
            )

        if candidate.is_absolute():
            path = candidate.resolve()
        elif candidate.parent == Path("."):
            path = (graph.journals_dir / candidate.name).resolve()
        else:
            path = (graph.root / candidate).resolve()

        if path.parent != graph.journals_dir.resolve():
            raise UserInputError(
                f"range endpoint must refer to {graph.journals_dir}: {path}"
            )
        date_text = candidate.stem

    try:
        return date.fromisoformat(date_text)
    except ValueError as exc:
        raise UserInputError(f"invalid journal date: {date_text!r}") from exc


def select_journal_range(graph: Graph, start: str, end: str) -> list[Path]:
    if not graph.journals_dir.is_dir():
        raise UserInputError(f"missing journals directory: {graph.journals_dir}")

    start_date = parse_range_endpoint(graph, start)
    end_date = parse_range_endpoint(graph, end)
    if start_date > end_date:
        raise UserInputError(f"--from {start_date} is after --to {end_date}")

    selected: list[tuple[date, Path]] = []
    for path in graph.journals_dir.glob("????-??-??.md"):
        try:
            current = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if start_date <= current <= end_date:
            selected.append((current, path.resolve()))

    selected.sort(key=lambda item: item[0])
    if not selected:
        raise UserInputError(
            f"no journal files found between {start_date} and {end_date}"
        )
    return [path for _, path in selected]


def render_document(title: str, text: str, path: str | None = None) -> str:
    header = [SEPARATOR, f"[[{title}]]"]
    if path is not None:
        header.append(f"# {path}")
    header.append(SEPARATOR)

    body = text.rstrip()
    return "\n".join(header + ([body] if body else []))


def show_journals(graph: Graph, journals: list[Path], include_self: bool) -> None:
    sections: list[str] = []
    linked_pages: list[Path] = []
    seen: set[Path] = set()

    for journal in journals:
        text = journal.read_text(encoding="utf-8")

        if include_self:
            sections.append(render_document(page_name_from_file(journal), text))

        for ref in refs(text):
            target = graph.resolve(ref)
            if target is not None and target not in seen:
                seen.add(target)
                linked_pages.append(target)

    for target in linked_pages:
        sections.append(
            render_document(
                graph.canonical[target],
                target.read_text(encoding="utf-8"),
                graph.display_path(target),
            )
        )

    if sections:
        print("\n\n".join(sections))


def show_refs(
    graph: Graph,
    page: str,
    list_children: bool = False,
    include_self: bool = False,
) -> None:
    target = graph.resolve(page)
    if target is None:
        raise UserInputError(f"Unknown page: {page!r}")

    targets = {target}
    if list_children:
        prefix = f"{graph.canonical[target]}/".casefold()
        targets |= {
            path
            for path, name in graph.canonical.items()
            if name.casefold().startswith(prefix)
        }

    paths = sorted(graph.pages_dir.glob("*.md"), key=lambda p: p.name.casefold())
    if graph.journals_dir.is_dir():
        paths += sorted(
            graph.journals_dir.glob("*.md"), key=lambda p: p.name.casefold()
        )

    first = True
    if include_self:
        print(
            render_document(
                graph.canonical[target],
                target.read_text(encoding="utf-8"),
                graph.display_path(target),
            )
        )
        first = False

    for path in paths:
        path = path.resolve()
        text = path.read_text(encoding="utf-8")
        lines, blocks = block_ranges(text)

        for start, own_end, subtree_end, _indent in blocks:
            own_text = "".join(lines[start:own_end])
            if not any(graph.resolve(ref) in targets for ref in refs(own_text)):
                continue

            if not first:
                print()
            first = False
            print(f"--- {graph.display_path(path)}:{start + 1} ---")
            print("".join(lines[start:subtree_end]).rstrip())


def selected_journals(graph: Graph, args: argparse.Namespace) -> list[Path]:
    has_range = args.from_journal is not None or args.to_journal is not None

    if has_range and not (args.from_journal and args.to_journal):
        raise UserInputError("--from and --to must be supplied together")
    if has_range and args.journals:
        raise UserInputError("use either JOURNAL arguments or --from/--to, not both")
    if has_range:
        return select_journal_range(graph, args.from_journal, args.to_journal)
    if not args.journals:
        raise UserInputError("journals requires JOURNAL arguments or --from/--to")

    return [resolve_journal_file(graph, value) for value in args.journals]


def build_parser() -> argparse.ArgumentParser:
    examples = """examples:
  logseq_refs.py . journals journals/2026-05-05.md journals/2026-05-06.md
  logseq_refs.py . journals --from 2026-05-05 --to 2026-05-06
  logseq_refs.py . journals --from journals/2026-05-05.md --to journals/2026-05-06.md
  logseq_refs.py . journals --from 2026-05-05 --to 2026-05-06 --include-self
  logseq_refs.py . refs "Discontinuous Galerkin"
  logseq_refs.py . refs "chat" --list-children
  logseq_refs.py . refs "chat" --include-self
"""
    parser = argparse.ArgumentParser(
        description="Inspect references in an OG/file-based Logseq graph.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("graph", metavar="GRAPH", help="Logseq graph directory")
    commands = parser.add_subparsers(dest="command", required=True)

    journals = commands.add_parser(
        "journals",
        help="print pages referenced by journal files",
        description=(
            "Print unique pages referenced by selected journals. "
            "Use explicit JOURNAL arguments or an inclusive --from/--to range."
        ),
    )
    journals.add_argument(
        "journals",
        metavar="JOURNAL",
        nargs="*",
        help="journal path, absolute or relative to GRAPH",
    )
    journals.add_argument(
        "--from",
        dest="from_journal",
        metavar="DATE_OR_JOURNAL",
        help="inclusive range start, e.g. 2026-05-05 or journals/2026-05-05.md",
    )
    journals.add_argument(
        "--to",
        dest="to_journal",
        metavar="DATE_OR_JOURNAL",
        help="inclusive range end, e.g. 2026-05-06 or journals/2026-05-06.md",
    )
    journals.add_argument(
        "--include-self",
        action="store_true",
        help="print selected journals before the pages they reference",
    )

    backlinks = commands.add_parser(
        "refs",
        help="print blocks that reference a page",
        description="Print blocks in pages/ and journals/ that reference PAGE.",
    )
    backlinks.add_argument("page", metavar="PAGE", help="canonical page name or alias")
    backlinks.add_argument(
        "--list-children",
        action="store_true",
        help="also include blocks referencing namespace children (e.g. [[PAGE/*]])",
    )
    backlinks.add_argument(
        "--include-self",
        action="store_true",
        help="print PAGE's own content before the blocks that reference it",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        graph = Graph(args.graph)
        if args.command == "journals":
            show_journals(graph, selected_journals(graph, args), args.include_self)
        else:
            show_refs(graph, args.page, args.list_children, args.include_self)
        return 0
    except (UserInputError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
