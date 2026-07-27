#!/usr/bin/env python3
r"""Build a static dependency graph for a LaTeX main file.

Supported direct commands:
  \input, \include, \subfile, \subfileinclude
  \import, \subimport, \inputfrom, \subinputfrom
  \bibliography, \addbibresource (only with --bib)

This is deliberately a static parser. It accepts literal file names and warns
about malformed or dynamic arguments instead of guessing. Macro expansion,
conditional execution, TEXINPUTS, and arbitrary TeX programming cannot be
modeled completely without running a TeX engine.

# Readable nested Markdown
python3 latex_dependency_graph.py main.tex

# Include bibliography resources
python3 latex_dependency_graph.py --bib main.tex

# Graphviz DOT
python3 latex_dependency_graph.py -f dot -o dependencies.dot main.tex
dot -Tsvg dependencies.dot -o dependencies.svg

# Mermaid Markdown
python3 latex_dependency_graph.py -f mermaid -o dependencies.md main.tex

# Suitable for CI: warnings cause exit status 2
python3 latex_dependency_graph.py --strict main.tex

# Add a directory corresponding to a project-specific TeX search path
python3 latex_dependency_graph.py --search-dir shared main.tex

# Disable source-directory fallback for stricter root-based resolution
python3 latex_dependency_graph.py --no-source-fallback main.tex

"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import tempfile
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Optional, Sequence, Set, Tuple

TEX_SUFFIXES = {".tex", ".ltx"}
SINGLE_COMMANDS = ("subfileinclude", "subfile", "include", "input")
IMPORT_COMMANDS = ("subinputfrom", "inputfrom", "subimport", "import")
BIB_COMMANDS = ("bibliography", "addbibresource")

SINGLE_RE = re.compile(
    r"\\(?P<cmd>subfileinclude|subfile|include|input)(?![A-Za-z@])"
    r"(?:\s*\{(?P<braced>[^{}]*)\}|\s*\"(?P<quoted>[^\"]+)\"|"
    r"\s+(?P<bare>[^\s%{}]+))",
    re.DOTALL,
)
IMPORT_RE = re.compile(
    r"\\(?P<cmd>subinputfrom|inputfrom|subimport|import)\*?(?![A-Za-z@])"
    r"\s*\{(?P<directory>[^{}]*)\}\s*\{(?P<target>[^{}]*)\}",
    re.DOTALL,
)
BIB_RE = re.compile(
    r"\\(?P<cmd>bibliography|addbibresource)(?![A-Za-z@])"
    r"\s*(?:\[[^\]]*\]\s*)?\{(?P<target>[^{}]*)\}",
    re.DOTALL,
)
TOKEN_RE = re.compile(
    r"\\(?P<cmd>subfileinclude|subfile|include|input|subinputfrom|inputfrom|"
    r"subimport|import|bibliography|addbibresource)(?![A-Za-z@])"
)
LITERAL_ENV_RE = re.compile(
    r"\\begin\s*\{(?P<env>verbatim\*?|Verbatim|lstlisting|minted|comment|"
    r"filecontents\*?)\}",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Reference:
    command: str
    line: int
    target: str
    directory: str = ""


@dataclass(frozen=True)
class Edge:
    source: Path
    target: Path
    command: str
    line: int


@dataclass
class Node:
    path: Path
    status: str = "ok"  # ok, missing, unreadable
    parseable: bool = True


@dataclass
class Graph:
    root: Path
    nodes: Dict[Path, Node] = field(default_factory=dict)
    adjacency: DefaultDict[Path, List[Edge]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_node(self, path: Path, status: str, parseable: bool) -> None:
        old = self.nodes.get(path)
        if old is None:
            self.nodes[path] = Node(path, status, parseable)
        else:
            if old.status == "ok" and status != "ok":
                old.status = status
            old.parseable = old.parseable or parseable


class Diagnostics:
    def __init__(self) -> None:
        self.count = 0
        self._seen: Set[Tuple[str, int, str]] = set()

    def warn(self, message: str, path: Optional[Path] = None, line: int = 0) -> None:
        key = (str(path) if path else "", line, message)
        if key in self._seen:
            return
        self._seen.add(key)
        self.count += 1
        where = ""
        if path is not None:
            where = str(path) + (f":{line}" if line else "") + ": "
        print(f"{where}warning: {message}", file=sys.stderr)

    @staticmethod
    def error(message: str, path: Optional[Path] = None) -> None:
        where = f"{path}: " if path is not None else ""
        print(f"{where}error: {message}", file=sys.stderr)


def blank_non_newlines(text: str) -> str:
    return "".join(ch if ch in "\r\n" else " " for ch in text)


def strip_comments(text: str) -> str:
    """Remove unescaped TeX comments while preserving offsets and line numbers."""
    output: List[str] = []
    for line in text.splitlines(keepends=True):
        cut: Optional[int] = None
        for i, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            j = i - 1
            while j >= 0 and line[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                cut = i
                break
        if cut is None:
            output.append(line)
        else:
            output.append(line[:cut] + blank_non_newlines(line[cut:]))
    return "".join(output)


def strip_literal_regions(text: str, path: Path, diag: Diagnostics) -> str:
    """Ignore common literal/code regions so examples do not become dependencies."""
    chars = list(text)
    pos = 0
    while True:
        match = LITERAL_ENV_RE.search(text, pos)
        if match is None:
            break
        env = match.group("env")
        end_re = re.compile(rf"\\end\s*\{{{re.escape(env)}\}}")
        end_match = end_re.search(text, match.end())
        end = end_match.end() if end_match else len(text)
        if end_match is None:
            diag.warn(
                f"unterminated literal environment {env!r}; ignored to end of file",
                path,
                text.count("\n", 0, match.start()) + 1,
            )
        chars[match.start():end] = blank_non_newlines(text[match.start():end])
        pos = end

    cleaned = "".join(chars)
    chars = list(cleaned)
    pos = 0
    verb_re = re.compile(r"\\verb\*?")
    while True:
        match = verb_re.search(cleaned, pos)
        if match is None or match.end() >= len(cleaned):
            break
        delimiter = cleaned[match.end()]
        if delimiter.isspace():
            pos = match.end() + 1
            continue
        end = cleaned.find(delimiter, match.end() + 1)
        if end < 0:
            diag.warn(
                "unterminated \\verb command",
                path,
                cleaned.count("\n", 0, match.start()) + 1,
            )
            end = len(cleaned) - 1
        chars[match.start():end + 1] = blank_non_newlines(cleaned[match.start():end + 1])
        pos = end + 1
    return "".join(chars)


def canonical(path: Path, diag: Diagnostics) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError as exc:
        diag.warn(f"cannot canonicalize path: {exc}", path)
        return Path(os.path.abspath(path))


def unique_paths(paths: Iterable[Path]) -> List[Path]:
    result: List[Path] = []
    seen: Set[Path] = set()
    for path in paths:
        if path not in seen:
            seen.add(path)
            result.append(path)
    return result


class LaTeXParser:
    def __init__(
        self,
        root_dir: Path,
        diag: Diagnostics,
        *,
        include_bib: bool,
        search_dirs: Sequence[Path],
        source_fallback: bool,
    ) -> None:
        self.root_dir = root_dir
        self.diag = diag
        self.include_bib = include_bib
        self.search_dirs = list(search_dirs)
        self.source_fallback = source_fallback
        self.cache: Dict[Path, Optional[List[Reference]]] = {}

    def read(self, path: Path) -> Optional[str]:
        try:
            data = path.read_bytes()
        except OSError as exc:
            self.diag.warn(f"cannot read file: {exc}", path)
            return None
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            self.diag.warn(
                f"not valid UTF-8 at byte {exc.start}; parsing as Latin-1",
                path,
            )
            return data.decode("latin-1")

    def literal(self, raw: str, path: Path, line: int, command: str) -> Optional[str]:
        value = re.sub(r"\s+", " ", raw).strip()
        if not value:
            self.diag.warn(f"empty argument to \\{command}", path, line)
            return None
        if value.startswith("|"):
            self.diag.warn(
                f"pipe/shell input is not treated as a file dependency: {value!r}",
                path,
                line,
            )
            return None
        if "\x00" in value or any(ch in value for ch in "\\#{}$"):
            self.diag.warn(
                f"dynamic or escaped path is not resolved: {value!r}",
                path,
                line,
            )
            return None
        return value

    def parse(self, path: Path) -> Optional[List[Reference]]:
        if path in self.cache:
            return self.cache[path]
        text = self.read(path)
        if text is None:
            self.cache[path] = None
            return None

        text = strip_literal_regions(strip_comments(text), path, self.diag)
        matches: List[Tuple[int, Reference]] = []
        parsed_starts: Set[int] = set()

        for match in IMPORT_RE.finditer(text):
            command = match.group("cmd")
            line = text.count("\n", 0, match.start()) + 1
            directory_raw = re.sub(r"\s+", " ", match.group("directory")).strip()
            directory = ""
            if directory_raw:
                checked = self.literal(directory_raw, path, line, command)
                if checked is None:
                    parsed_starts.add(match.start())
                    continue
                directory = checked
            target = self.literal(match.group("target"), path, line, command)
            parsed_starts.add(match.start())
            if target is not None:
                matches.append((match.start(), Reference(command, line, target, directory)))

        for match in SINGLE_RE.finditer(text):
            command = match.group("cmd")
            line = text.count("\n", 0, match.start()) + 1
            raw = match.group("braced") or match.group("quoted") or match.group("bare") or ""
            target = self.literal(raw, path, line, command)
            parsed_starts.add(match.start())
            if target is not None:
                matches.append((match.start(), Reference(command, line, target)))

        if self.include_bib:
            for match in BIB_RE.finditer(text):
                command = match.group("cmd")
                line = text.count("\n", 0, match.start()) + 1
                raw_targets = (
                    match.group("target").split(",")
                    if command == "bibliography"
                    else [match.group("target")]
                )
                parsed_starts.add(match.start())
                for raw in raw_targets:
                    target = self.literal(raw, path, line, command)
                    if target is not None:
                        matches.append((match.start(), Reference(command, line, target)))

        enabled = set(SINGLE_COMMANDS) | set(IMPORT_COMMANDS)
        if self.include_bib:
            enabled |= set(BIB_COMMANDS)
        for token in TOKEN_RE.finditer(text):
            if token.group("cmd") in enabled and token.start() not in parsed_starts:
                self.diag.warn(
                    f"unsupported, nested, or non-literal syntax for \\{token.group('cmd')}",
                    path,
                    text.count("\n", 0, token.start()) + 1,
                )

        matches.sort(key=lambda item: item[0])
        refs = [ref for _, ref in matches]
        self.cache[path] = refs
        return refs

    def command_search_dirs(self, source: Path, command: str) -> List[Path]:
        current = source.parent
        if command in {"import", "inputfrom"}:
            dirs = [self.root_dir, *self.search_dirs]
        elif command in {"subimport", "subinputfrom"}:
            dirs = [current, *self.search_dirs]
        else:
            dirs = [self.root_dir]
            if self.source_fallback and current != self.root_dir:
                dirs.append(current)
            dirs.extend(self.search_dirs)
        return unique_paths(canonical(path, self.diag) for path in dirs)

    def resolve(self, source: Path, ref: Reference) -> Tuple[Path, bool]:
        default_ext = ".bib" if ref.command in BIB_COMMANDS else ".tex"
        target_text = str(Path(ref.directory) / ref.target) if ref.directory else ref.target
        target = Path(target_text)

        if target.is_absolute():
            bases: List[Tuple[Path, Optional[Path]]] = [(target, None)]
            search_dirs: List[Path] = []
        else:
            search_dirs = self.command_search_dirs(source, ref.command)
            bases = [(directory / target, directory) for directory in search_dirs]

        candidates: List[Tuple[Path, Optional[Path]]] = []
        seen: Set[Path] = set()
        for base, origin in bases:
            variants = [base] + ([base.with_suffix(default_ext)] if not base.suffix else [])
            for variant in variants:
                path = canonical(variant, self.diag)
                if path not in seen:
                    seen.add(path)
                    candidates.append((path, origin))

        existing = [(path, origin) for path, origin in candidates if path.is_file()]
        if existing:
            chosen, origin = existing[0]
            if len(existing) > 1:
                self.diag.warn(
                    f"ambiguous dependency {target_text!r}; using {chosen}; other matches: "
                    + ", ".join(str(path) for path, _ in existing[1:]),
                    source,
                    ref.line,
                )
            if (
                origin == canonical(source.parent, self.diag)
                and source.parent != self.root_dir
                and search_dirs
                and search_dirs[0] == self.root_dir
            ):
                self.diag.warn(
                    f"resolved {target_text!r} relative to the including file; "
                    "this relies on source-relative/import-path semantics",
                    source,
                    ref.line,
                )
            return chosen, True

        first = bases[0][0]
        missing = canonical(
            first.with_suffix(default_ext) if not first.suffix else first,
            self.diag,
        )
        self.diag.warn(
            f"dependency not found for \\{ref.command}: {target_text!r}; expected {missing}",
            source,
            ref.line,
        )
        return missing, False


def build_graph(main_file: Path, parser: LaTeXParser) -> Graph:
    graph = Graph(main_file)
    graph.add_node(main_file, "ok", True)
    queue = deque([main_file])
    parsed: Set[Path] = set()
    seen_edges: Set[Tuple[Path, Path, str]] = set()

    while queue:
        source = queue.popleft()
        if source in parsed:
            continue
        parsed.add(source)
        refs = parser.parse(source)
        if refs is None:
            graph.nodes[source].status = "unreadable"
            continue

        for ref in refs:
            target, exists = parser.resolve(source, ref)
            parseable = target.suffix.lower() in TEX_SUFFIXES
            graph.add_node(target, "ok" if exists else "missing", parseable)
            edge_key = (source, target, ref.command)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                graph.adjacency[source].append(
                    Edge(source, target, ref.command, ref.line)
                )
            if exists and parseable and target not in parsed:
                queue.append(target)
    return graph


def display_path(path: Path, root_dir: Path) -> str:
    try:
        return Path(os.path.relpath(path, root_dir)).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def warn_cycles(graph: Graph, diag: Diagnostics) -> None:
    color: Dict[Path, int] = {}
    parent: Dict[Path, Path] = {}
    warned: Set[Tuple[Path, Path]] = set()

    for start in graph.nodes:
        if color.get(start, 0):
            continue
        color[start] = 1
        stack: List[Tuple[Path, int]] = [(start, 0)]
        while stack:
            node, index = stack[-1]
            children = [
                edge.target
                for edge in graph.adjacency.get(node, [])
                if graph.nodes[edge.target].status == "ok"
                and graph.nodes[edge.target].parseable
            ]
            if index >= len(children):
                color[node] = 2
                stack.pop()
                continue
            child = children[index]
            stack[-1] = (node, index + 1)
            state = color.get(child, 0)
            if state == 0:
                parent[child] = node
                color[child] = 1
                stack.append((child, 0))
            elif state == 1 and (node, child) not in warned:
                warned.add((node, child))
                chain = [node]
                cursor = node
                while cursor != child and cursor in parent:
                    cursor = parent[cursor]
                    chain.append(cursor)
                chain.reverse()
                chain.append(child)
                diag.warn(
                    "dependency cycle detected: "
                    + " -> ".join(display_path(path, graph.root.parent) for path in chain)
                )


def render_markdown(graph: Graph) -> str:
    lines: List[str] = []
    expanded: Set[Path] = set()
    stack: List[Tuple[Path, int, Optional[Edge], frozenset[Path]]] = [
        (graph.root, 0, None, frozenset())
    ]
    while stack:
        path, depth, incoming, ancestors = stack.pop()
        node = graph.nodes[path]
        label = display_path(path, graph.root.parent)
        context = f" [\\{incoming.command}, line {incoming.line}]" if incoming else ""
        indent = "  " * depth
        if path in ancestors:
            lines.append(f"{indent}- `{label}`{context} (cycle to ancestor)")
            continue
        if path in expanded:
            lines.append(f"{indent}- `{label}`{context} (already expanded)")
            continue
        status = f" ({node.status})" if node.status != "ok" else ""
        lines.append(f"{indent}- `{label}`{context}{status}")
        if node.status != "ok" or not node.parseable:
            continue
        expanded.add(path)
        next_ancestors = ancestors | {path}
        for edge in reversed(graph.adjacency.get(path, [])):
            stack.append((edge.target, depth + 1, edge, next_ancestors))
    return "\n".join(lines)


def dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def ordered_nodes(graph: Graph) -> List[Path]:
    return [graph.root] + sorted(
        (path for path in graph.nodes if path != graph.root), key=str
    )


def render_dot(graph: Graph) -> str:
    paths = ordered_nodes(graph)
    ids = {path: f"n{i}" for i, path in enumerate(paths)}
    lines = [
        "digraph LaTeXDependencies {",
        "  rankdir=LR;",
        '  node [shape=box, style="filled,rounded", fillcolor="#eef2f5"];',
    ]
    for path in paths:
        node = graph.nodes[path]
        attrs = [f'label="{dot_escape(display_path(path, graph.root.parent))}"']
        if path == graph.root:
            attrs += ['fillcolor="#d4edda"', 'color="#28a745"']
        elif node.status == "missing":
            attrs += ['fillcolor="#ffe6e6"', 'color="#d9534f"']
        elif node.status == "unreadable":
            attrs += ['fillcolor="#fff3cd"', 'color="#856404"']
        lines.append(f"  {ids[path]} [{', '.join(attrs)}];")
    for source in paths:
        for edge in graph.adjacency.get(source, []):
            label = dot_escape(f"\\{edge.command}:{edge.line}")
            lines.append(f'  {ids[source]} -> {ids[edge.target]} [label="{label}"];')
    lines.append("}")
    return "\n".join(lines)


def render_mermaid(graph: Graph) -> str:
    paths = ordered_nodes(graph)
    ids = {path: f"n{i}" for i, path in enumerate(paths)}
    lines = ["```mermaid", "flowchart TD"]
    for path in paths:
        label = html.escape(display_path(path, graph.root.parent), quote=True)
        lines.append(f'  {ids[path]}["{label}"]')
    for source in paths:
        for edge in graph.adjacency.get(source, []):
            lines.append(f"  {ids[source]} -->|{edge.command}:{edge.line}| {ids[edge.target]}")
    lines += [
        "  classDef root fill:#d4edda,stroke:#28a745,stroke-width:2px",
        "  classDef missing fill:#ffe6e6,stroke:#d9534f,stroke-width:2px",
        "  classDef unreadable fill:#fff3cd,stroke:#856404,stroke-width:2px",
        f"  class {ids[graph.root]} root",
    ]
    missing = [ids[path] for path in paths if graph.nodes[path].status == "missing"]
    unreadable = [ids[path] for path in paths if graph.nodes[path].status == "unreadable"]
    if missing:
        lines.append(f"  class {','.join(missing)} missing")
    if unreadable:
        lines.append(f"  class {','.join(unreadable)} unreadable")
    lines.append("```")
    return "\n".join(lines)


def atomic_write(path: Path, text: str) -> None:
    parent = path.parent
    if not parent.is_dir():
        raise OSError(f"output directory does not exist: {parent}")
    temp_name: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        if temp_name is not None:
            try:
                Path(temp_name).unlink(missing_ok=True)
            except OSError:
                pass
        raise


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a LaTeX dependency tree or graph.")
    parser.add_argument("main_file", type=Path)
    parser.add_argument(
        "-f", "--format", choices=("markdown", "dot", "mermaid"), default="markdown"
    )
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--bib", action="store_true", help="include .bib dependencies")
    parser.add_argument(
        "--search-dir",
        action="append",
        default=[],
        type=Path,
        metavar="DIR",
        help="additional search directory; may be repeated",
    )
    parser.add_argument(
        "--no-source-fallback",
        action="store_true",
        help="do not search relative to the including file after the main-file directory",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit with status 2 if any warning is emitted",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    diag = Diagnostics()
    try:
        main_file = args.main_file.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        diag.error(f"cannot resolve main file: {exc}", args.main_file)
        return 1
    if not main_file.is_file():
        diag.error("main path is not a regular file", main_file)
        return 1
    try:
        main_file.read_bytes()
    except OSError as exc:
        diag.error(f"cannot read main file: {exc}", main_file)
        return 1

    root_dir = main_file.parent
    search_dirs: List[Path] = []
    for raw in args.search_dir:
        candidate = raw if raw.is_absolute() else root_dir / raw
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            diag.warn(f"search directory is unavailable: {exc}", candidate)
            continue
        if not resolved.is_dir():
            diag.warn("search path is not a directory", resolved)
            continue
        search_dirs.append(resolved)

    parser = LaTeXParser(
        root_dir,
        diag,
        include_bib=args.bib,
        search_dirs=search_dirs,
        source_fallback=not args.no_source_fallback,
    )
    graph = build_graph(main_file, parser)
    warn_cycles(graph, diag)

    if args.format == "dot":
        output = render_dot(graph)
    elif args.format == "mermaid":
        output = render_mermaid(graph)
    else:
        output = render_markdown(graph)

    try:
        if args.output:
            output_path = canonical(args.output, diag)
            if output_path in graph.nodes:
                diag.error("refusing to overwrite a source dependency", output_path)
                return 1
            atomic_write(output_path, output + "\n")
            print(f"Dependencies written to {output_path}", file=sys.stderr)
        else:
            print(output)
    except OSError as exc:
        diag.error(f"cannot write output: {exc}", args.output)
        return 1

    if diag.count:
        print(f"{diag.count} warning(s) emitted", file=sys.stderr)
    return 2 if args.strict and diag.count else 0


if __name__ == "__main__":
    raise SystemExit(main())
