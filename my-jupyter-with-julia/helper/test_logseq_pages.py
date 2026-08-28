#!/usr/bin/env python3
"""
Behavior tests for:

    python logseq_refs.py GRAPH journals JOURNAL...

Usage:
    python test_logseq_pages.py
    python test_logseq_pages.py /path/to/logseq_refs.py

The test creates a temporary Logseq graph and runs the real CLI as a
subprocess, so it tests user-visible behavior rather than implementation
details.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


UTILITY = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else Path("logseq_refs.py").resolve()
)

# Prevent unittest from interpreting the utility path as a test name.
sys.argv = [sys.argv[0]]


class PagesCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        if not UTILITY.is_file():
            self.fail(
                f"Utility not found: {UTILITY}\n"
                "Run as:\n"
                "  python test_logseq_pages.py /path/to/logseq_refs.py"
            )

        self.tmp = tempfile.TemporaryDirectory()
        self.graph = Path(self.tmp.name)
        (self.graph / "pages").mkdir()
        (self.graph / "journals").mkdir()

        self._write(
            "pages/Finite Element Method.md",
            """
            alias:: [[FEM]]

            - FEM page body.
            """,
        )
        self._write(
            "pages/Finite Volume Method.md",
            """
            - alias::[[FVM]]

            - FVM page body.
            """,
        )
        self._write(
            "pages/Discontinuous Galerkin.md",
            """
            alias:: [[discontinuous-galerkin]]

            - DG page body.
            """,
        )
        self._write(
            "pages/digital twins.md",
            """
            - Digital twins page body.
            """,
        )
        self._write(
            "pages/conference___EGU26.md",
            """
            - Conference page body.
            """,
        )
        self._write(
            "pages/Not Referenced.md",
            """
            - This page should never appear.
            """,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, relative_path: str, content: str) -> Path:
        path = self.graph / relative_path
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
        return path

    def _journal(self, name: str, content: str) -> Path:
        return self._write(f"journals/{name}.md", content)

    def _run(self, *journals: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(UTILITY),
                str(self.graph),
                "journals",
                *(str(p) for p in journals),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_direct_wikilink_prints_page(self) -> None:
        journal = self._journal(
            "2026-05-01",
            """
            - Compare [[Finite Element Method]] with other methods.
            """,
        )

        result = self._run(journal)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[[Finite Element Method]]", result.stdout)
        self.assertIn("FEM page body.", result.stdout)

    def test_alias_resolves_to_canonical_page(self) -> None:
        journal = self._journal(
            "2026-05-02",
            """
            - [[FEM]] and [[FVM]] are both useful.
            - Also see [[discontinuous-galerkin]].
            """,
        )

        result = self._run(journal)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[[Finite Element Method]]", result.stdout)
        self.assertIn("[[Finite Volume Method]]", result.stdout)
        self.assertIn("[[Discontinuous Galerkin]]", result.stdout)

    def test_duplicate_refs_print_page_once_across_multiple_journals(self) -> None:
        j1 = self._journal(
            "2026-05-03",
            """
            - [[FEM]]
            - [[Finite Element Method]]
            """,
        )
        j2 = self._journal(
            "2026-05-04",
            """
            - Again: [[FEM]]
            """,
        )

        result = self._run(j1, j2)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("[[Finite Element Method]]"), 1)
        self.assertEqual(result.stdout.count("FEM page body."), 1)

    def test_tag_can_resolve_to_page(self) -> None:
        journal = self._journal(
            "2026-05-05",
            """
            - Session notes #conference/EGU26
            """,
        )

        result = self._run(journal)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[[conference/EGU26]]", result.stdout)
        self.assertIn("Conference page body.", result.stdout)

    def test_unresolved_reference_is_ignored(self) -> None:
        journal = self._journal(
            "2026-05-06",
            """
            - [[Does Not Exist]]
            - [[FEM]]
            """,
        )

        result = self._run(journal)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Does Not Exist", result.stdout)
        self.assertIn("[[Finite Element Method]]", result.stdout)

    def test_refs_inside_fenced_and_inline_code_are_ignored(self) -> None:
        journal = self._journal(
            "2026-05-07",
            r"""
            - Real ref: [[FEM]]
            - Inline code: `[[FVM]]`

            ```text
            [[Discontinuous Galerkin]]
            ```
            """,
        )

        result = self._run(journal)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[[Finite Element Method]]", result.stdout)
        self.assertNotIn("[[Finite Volume Method]]", result.stdout)
        self.assertNotIn("[[Discontinuous Galerkin]]", result.stdout)

    def test_unreferenced_pages_are_not_printed(self) -> None:
        journal = self._journal(
            "2026-05-08",
            """
            - [[digital twins]]
            """,
        )

        result = self._run(journal)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[[digital twins]]", result.stdout)
        self.assertNotIn("[[Not Referenced]]", result.stdout)
        self.assertNotIn("This page should never appear.", result.stdout)


class PagesInterfaceEquivalenceTests(unittest.TestCase):
    def setUp(self) -> None:
        if not UTILITY.is_file():
            self.fail(
                f"Utility not found: {UTILITY}\n"
                "Run as:\n"
                "  python test_logseq_pages_01.py /path/to/logseq_refs.py"
            )

        self.tmp = tempfile.TemporaryDirectory()
        self.graph = Path(self.tmp.name)
        (self.graph / "pages").mkdir()
        (self.graph / "journals").mkdir()

        # The fixture intentionally includes aliases and repeated references so
        # exact stdout comparison also guards ordering and deduplication.
        self._write(
            "pages/Finite Element Method.md",
            """
            alias:: [[FEM]]

            - FEM page body.
            """,
        )
        self._write(
            "pages/Finite Volume Method.md",
            """
            alias:: [[FVM]]

            - FVM page body.
            """,
        )
        self._write(
            "pages/Discontinuous Galerkin.md",
            """
            alias:: [[discontinuous-galerkin]]

            - DG page body.
            """,
        )
        self._write(
            "pages/digital twins.md",
            """
            - Digital twins page body.
            """,
        )

        self.j1 = self._journal(
            "2026-07-06",
            """
            - Day one: [[FEM]] and [[digital twins]].
            """,
        )
        self.j2 = self._journal(
            "2026-07-07",
            """
            - Day two: [[FVM]] and duplicate [[Finite Element Method]].
            """,
        )
        self.j3 = self._journal(
            "2026-07-08",
            """
            - Day three: [[discontinuous-galerkin]].
            """,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, relative_path: str, content: str) -> Path:
        path = self.graph / relative_path
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
        return path

    def _journal(self, date: str, content: str) -> Path:
        return self._write(f"journals/{date}.md", content)

    def _run(self, *pages_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(UTILITY),
                str(self.graph),
                "journals",
                *pages_args,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def assertSameBehavior(
        self,
        left: subprocess.CompletedProcess[str],
        right: subprocess.CompletedProcess[str],
    ) -> None:
        """Assert complete user-visible equivalence of two invocations."""
        self.assertEqual(
            left.returncode,
            right.returncode,
            msg=(
                "return codes differ\n"
                f"left stderr:\n{left.stderr}\n"
                f"right stderr:\n{right.stderr}"
            ),
        )
        self.assertEqual(left.stdout, right.stdout, "stdout differs")
        self.assertEqual(left.stderr, right.stderr, "stderr differs")

    def test_date_range_equals_explicit_contiguous_journals(self) -> None:
        """The exact interface equivalence described in the usage contract."""
        ranged = self._run(
            "--from",
            "2026-07-06",
            "--to",
            "2026-07-08",
        )
        explicit = self._run(
            "journals/2026-07-06.md",
            "journals/2026-07-07.md",
            "journals/2026-07-08.md",
        )

        self.assertSameBehavior(ranged, explicit)
        self.assertEqual(ranged.returncode, 0, ranged.stderr)

    def test_path_endpoint_range_equals_explicit_contiguous_journals(self) -> None:
        """Path-form --from/--to endpoints are equivalent to explicit files."""
        ranged = self._run(
            "--from",
            "journals/2026-07-06.md",
            "--to",
            "journals/2026-07-08.md",
        )
        explicit = self._run(
            "journals/2026-07-06.md",
            "journals/2026-07-07.md",
            "journals/2026-07-08.md",
        )

        self.assertSameBehavior(ranged, explicit)

    def test_range_equals_explicit_with_include_self(self) -> None:
        """Selection syntax must not affect --include-self output."""
        ranged = self._run(
            "--from",
            "2026-07-06",
            "--to",
            "2026-07-08",
            "--include-self",
        )
        explicit = self._run(
            "journals/2026-07-06.md",
            "journals/2026-07-07.md",
            "journals/2026-07-08.md",
            "--include-self",
        )

        self.assertSameBehavior(ranged, explicit)

    def test_range_with_missing_day_equals_explicit_existing_files(self) -> None:
        """A range selects existing journals within it, not nonexistent dates."""
        # Create a second range with an intentional hole at 2026-07-11.
        j10 = self._journal("2026-07-10", "- [[FEM]]\n")
        j12 = self._journal("2026-07-12", "- [[FVM]]\n")

        ranged = self._run(
            "--from",
            "2026-07-10",
            "--to",
            "2026-07-12",
        )
        explicit = self._run(
            str(j10.relative_to(self.graph)),
            str(j12.relative_to(self.graph)),
        )

        self.assertSameBehavior(ranged, explicit)

    def test_date_and_path_endpoint_ranges_are_equivalent(self) -> None:
        """Both supported endpoint spellings select the same journals."""
        dates = self._run(
            "--from",
            "2026-07-06",
            "--to",
            "2026-07-08",
        )
        paths = self._run(
            "--from",
            "journals/2026-07-06.md",
            "--to",
            "journals/2026-07-08.md",
        )

        self.assertSameBehavior(dates, paths)

    def test_absolute_and_graph_relative_explicit_paths_are_equivalent(self) -> None:
        """Explicit journal selection should not depend on path spelling."""
        relative = self._run(
            "journals/2026-07-06.md",
            "journals/2026-07-07.md",
            "journals/2026-07-08.md",
        )
        absolute = self._run(str(self.j1), str(self.j2), str(self.j3))

        self.assertSameBehavior(relative, absolute)


if __name__ == "__main__":
    unittest.main(verbosity=2)
