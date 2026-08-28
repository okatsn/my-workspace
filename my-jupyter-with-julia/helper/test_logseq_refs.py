#!/usr/bin/env python3
"""
Behavior tests for:

    python logseq_refs.py GRAPH refs PAGE

Usage:
    python test_logseq_refs.py
    python test_logseq_refs.py /path/to/logseq_refs.py

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


UTILITY = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("logseq_refs.py").resolve()

# Prevent unittest from interpreting the utility path as a test name.
sys.argv = [sys.argv[0]]


class RefsCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        if not UTILITY.is_file():
            self.fail(
                f"Utility not found: {UTILITY}\n"
                "Run as:\n"
                "  python test_logseq_refs.py /path/to/logseq_refs.py"
            )

        self.tmp = tempfile.TemporaryDirectory()
        self.graph = Path(self.tmp.name)
        (self.graph / "pages").mkdir()
        (self.graph / "journals").mkdir()

        self._write(
            "pages/Finite Element Method.md",
            """
            alias:: [[FEM]]

            - Canonical FEM page.
            """,
        )
        self._write(
            "pages/Finite Volume Method.md",
            """
            alias:: [[FVM]]

            - Canonical FVM page.
            """,
        )
        self._write(
            "pages/Discontinuous Galerkin.md",
            """
            alias:: [[discontinuous-galerkin]]

            - Canonical DG page.
            """,
        )
        self._write(
            "pages/conference___EGU26.md",
            """
            - Conference page.
            """,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, relative_path: str, content: str) -> Path:
        path = self.graph / relative_path
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
        return path

    def _run(self, page: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(UTILITY),
                str(self.graph),
                "refs",
                page,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_direct_reference_prints_matching_block(self) -> None:
        self._write(
            "journals/2026-05-01.md",
            """
            - This block mentions [[Finite Element Method]].
            - This block mentions nothing relevant.
            """,
        )

        result = self._run("Finite Element Method")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- This block mentions [[Finite Element Method]].", result.stdout)
        self.assertNotIn("- This block mentions nothing relevant.", result.stdout)

    def test_alias_reference_matches_canonical_page(self) -> None:
        self._write(
            "journals/2026-05-02.md",
            """
            - Compare [[FEM]] against another method.
            """,
        )

        result = self._run("Finite Element Method")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- Compare [[FEM]] against another method.", result.stdout)

    def test_querying_by_alias_also_resolves_target(self) -> None:
        self._write(
            "journals/2026-05-03.md",
            """
            - Compare [[Finite Element Method]] against another method.
            """,
        )

        result = self._run("FEM")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- Compare [[Finite Element Method]] against another method.", result.stdout)

    def test_matching_child_block_prints_child_subtree_not_parent(self) -> None:
        self._write(
            "journals/2026-05-04.md",
            """
            - Parent A should not be printed
              - Child B mentions [[FEM]]
                - B1 belongs to the matching subtree
                - B2 also belongs to the matching subtree
              - Sibling C should not be printed
            """,
        )

        result = self._run("Finite Element Method")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- Child B mentions [[FEM]]", result.stdout)
        self.assertIn("- B1 belongs to the matching subtree", result.stdout)
        self.assertIn("- B2 also belongs to the matching subtree", result.stdout)
        self.assertNotIn("- Parent A should not be printed", result.stdout)
        self.assertNotIn("- Sibling C should not be printed", result.stdout)

    def test_reference_in_child_does_not_make_parent_match(self) -> None:
        self._write(
            "journals/2026-05-05.md",
            """
            - Parent without a ref
              continuation line belonging to parent
              - Child with [[FEM]]
            """,
        )

        result = self._run("Finite Element Method")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- Child with [[FEM]]", result.stdout)
        self.assertNotIn("- Parent without a ref", result.stdout)
        self.assertNotIn("continuation line belonging to parent", result.stdout)

    def test_matching_parent_prints_entire_subtree(self) -> None:
        self._write(
            "journals/2026-05-06.md",
            """
            - Parent mentions [[FEM]]
              - Child 1
                - Grandchild
              - Child 2
            - Unrelated sibling
            """,
        )

        result = self._run("Finite Element Method")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- Parent mentions [[FEM]]", result.stdout)
        self.assertIn("- Child 1", result.stdout)
        self.assertIn("- Grandchild", result.stdout)
        self.assertIn("- Child 2", result.stdout)
        self.assertNotIn("- Unrelated sibling", result.stdout)

    def test_tag_reference_matches_page(self) -> None:
        self._write(
            "journals/2026-05-07.md",
            """
            - EGU notes #conference/EGU26
            """,
        )

        result = self._run("conference/EGU26")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- EGU notes #conference/EGU26", result.stdout)

    def test_alias_tag_matches_aliased_page(self) -> None:
        self._write(
            "journals/2026-05-08.md",
            """
            - A block tagged #discontinuous-galerkin
            """,
        )

        result = self._run("Discontinuous Galerkin")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- A block tagged #discontinuous-galerkin", result.stdout)

    def test_refs_inside_inline_or_fenced_code_are_ignored(self) -> None:
        self._write(
            "journals/2026-05-09.md",
            r"""
            - Inline code only: `[[FEM]]`
            - Real reference: [[FVM]]

            ```text
            - [[FEM]]
            ```
            """,
        )

        result = self._run("Finite Element Method")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Inline code only", result.stdout)
        self.assertNotIn('```', result.stdout)
        self.assertNotIn("- [[FEM]]", result.stdout)

    def test_searches_both_pages_and_journals(self) -> None:
        self._write(
            "journals/2026-05-10.md",
            """
            - Journal says [[FEM]].
            """,
        )
        self._write(
            "pages/Another Topic.md",
            """
            - Page says [[FEM]].
            """,
        )

        result = self._run("Finite Element Method")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- Journal says [[FEM]].", result.stdout)
        self.assertIn("- Page says [[FEM]].", result.stdout)
        self.assertIn("journals/2026-05-10.md", result.stdout)
        self.assertIn("pages/Another Topic.md", result.stdout)

    def test_unknown_page_fails_cleanly(self) -> None:
        result = self._run("Page That Does Not Exist")

        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + result.stderr
        self.assertIn("Unknown page", combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
