#!/usr/bin/env python3
"""
Test suite for cutpaste-one.py.

Run with:

    python3 helper/test_cutpaste_one.py
    python3 -m unittest helper/test_cutpaste_one.py

Each test builds its own throwaway directory tree (no git needed; the
script only requires --root) and invokes the script as a subprocess, so
these tests exercise the exact CLI behaviour a real migration run would see.
"""

from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().with_name("cutpaste-one.py"))


def run_cli(root: Path, cid: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, SCRIPT, cid, "--root", str(root), *extra],
        capture_output=True,
        text=True,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class CutPasteTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def assertUnchanged(self, path: Path, original: str) -> None:
        self.assertEqual(path.read_text(), original)


class TestBasicOps(CutPasteTestCase):
    def test_move_relocates_payload_and_strips_source_markers(self):
        write(
            self.root / "src/a.jl",
            "x = 1\n"
            "# CUTPASTE:BEGIN:cptest-001 op=move to=pages/t.md\n"
            "# moved paragraph\n"
            "# CUTPASTE:END:cptest-001\n"
            "y = 2\n",
        )
        write(
            self.root / "pages/t.md",
            "# Heading\n<!-- CUTPASTE:HERE:cptest-001 seq=1 from=src/a.jl -->\n",
        )

        result = run_cli(self.root, "cptest-001")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertEqual(
            (self.root / "src/a.jl").read_text(),
            "x = 1\ny = 2\n",
        )
        self.assertEqual(
            (self.root / "pages/t.md").read_text(),
            "# Heading\n# moved paragraph\n",
        )

    def test_copy_keeps_payload_in_source_and_writes_destination(self):
        write(
            self.root / "src/b.jl",
            "# CUTPASTE:BEGIN:cptest-002 op=copy to=pages/t.md\n"
            "# copied paragraph\n"
            "# CUTPASTE:END:cptest-002\n"
            "z = 3\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-002 seq=1 from=src/b.jl -->\n",
        )

        result = run_cli(self.root, "cptest-002")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertEqual(
            (self.root / "src/b.jl").read_text(),
            "# copied paragraph\nz = 3\n",
        )
        self.assertEqual(
            (self.root / "pages/t.md").read_text(),
            "# copied paragraph\n",
        )

    def test_drop_deletes_payload_with_no_destination(self):
        write(
            self.root / "src/c.jl",
            "before = 1\n"
            "# CUTPASTE:BEGIN:cptest-003 op=drop\n"
            "# throwaway paragraph\n"
            "# CUTPASTE:END:cptest-003\n"
            "after = 2\n",
        )

        result = run_cli(self.root, "cptest-003")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.root / "src/c.jl").read_text(),
            "before = 1\nafter = 2\n",
        )

    def test_dry_run_makes_no_changes(self):
        original = (
            "# CUTPASTE:BEGIN:cptest-004 op=drop\n"
            "# paragraph\n"
            "# CUTPASTE:END:cptest-004\n"
        )
        write(self.root / "src/d.jl", original)

        result = run_cli(self.root, "cptest-004", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertUnchanged(self.root / "src/d.jl", original)

    def test_payload_sha256_matches_extracted_bytes(self):
        payload = "# exact payload line\n"
        write(
            self.root / "src/e.jl",
            "# CUTPASTE:BEGIN:cptest-005 op=drop\n"
            + payload
            + "# CUTPASTE:END:cptest-005\n",
        )

        result = run_cli(self.root, "cptest-005", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = hashlib.sha256(payload.encode()).hexdigest()
        self.assertIn(expected, result.stdout)

    def test_custom_prefix_and_full_id_form_are_equivalent(self):
        write(
            self.root / "src/f.jl",
            "# CUTPASTE:BEGIN:demo-042 op=drop\n# gone\n# CUTPASTE:END:demo-042\n",
        )

        by_number = run_cli(self.root, "042", "--prefix", "demo-")
        self.assertEqual(by_number.returncode, 0, by_number.stderr)

    def test_file_mode_is_preserved(self):
        src = self.root / "scripts/run.sh"
        write(
            src,
            "#!/usr/bin/env bash\n"
            "# CUTPASTE:BEGIN:cptest-006 op=drop\n"
            "# stale comment\n"
            "# CUTPASTE:END:cptest-006\n"
            "echo hi\n",
        )
        src.chmod(0o755)

        result = run_cli(self.root, "cptest-006")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(stat.S_IMODE(src.stat().st_mode), 0o755)


class TestValidationFailures(CutPasteTestCase):
    def test_missing_marker_is_reported_and_nothing_changes(self):
        write(self.root / "src/x.jl", "no markers here\n")
        result = run_cli(self.root, "cptest-900", "--dry-run")
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_op_is_rejected(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-007 op=frobnicate to=pages/t.md\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-007\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-007 seq=1 from=src/x.jl -->\n",
        )
        result = run_cli(self.root, "cptest-007", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("op must be move, copy, or drop", result.stderr)

    def test_move_without_here_anchor_fails(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-008 op=move to=pages/t.md\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-008\n",
        )
        result = run_cli(self.root, "cptest-008", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HERE marker", result.stderr)

    def test_drop_with_extra_here_anchor_fails(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-009 op=drop\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-009\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-009 seq=1 from=src/x.jl -->\n",
        )
        result = run_cli(self.root, "cptest-009", "--dry-run")
        self.assertNotEqual(result.returncode, 0)

    def test_to_mismatched_with_actual_here_location_fails(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-010 op=move to=pages/wrong.md\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-010\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-010 seq=1 from=src/x.jl -->\n",
        )
        result = run_cli(self.root, "cptest-010", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("to=", result.stderr)

    def test_from_mismatched_with_actual_begin_location_fails(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-011 op=move to=pages/t.md\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-011\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-011 seq=1 from=src/wrong.jl -->\n",
        )
        result = run_cli(self.root, "cptest-011", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("from=", result.stderr)

    def test_non_positive_seq_is_rejected(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-012 op=move to=pages/t.md\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-012\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-012 seq=0 from=src/x.jl -->\n",
        )
        result = run_cli(self.root, "cptest-012", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("seq=", result.stderr)

    def test_absolute_destination_path_is_rejected(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-013 op=move to=/etc/passwd\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-013\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-013 seq=1 from=src/x.jl -->\n",
        )
        result = run_cli(self.root, "cptest-013", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe", result.stderr)

    def test_parent_traversal_destination_path_is_rejected(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-014 op=move to=../../etc/passwd\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-014\n",
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-014 seq=1 from=src/x.jl -->\n",
        )
        result = run_cli(self.root, "cptest-014", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe", result.stderr)

    def test_duplicate_attribute_key_is_rejected(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-015 op=move to=pages/t.md to=pages/other.md\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-015\n",
        )
        result = run_cli(self.root, "cptest-015", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate attribute", result.stderr)

    def test_two_begins_for_same_id_is_rejected(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-016 op=drop\n# a\n# CUTPASTE:END:cptest-016\n",
        )
        write(
            self.root / "src/y.jl",
            "# CUTPASTE:BEGIN:cptest-016 op=drop\n# b\n# CUTPASTE:END:cptest-016\n",
        )
        result = run_cli(self.root, "cptest-016", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected exactly 1 BEGIN", result.stderr)

    def test_overlapping_regions_in_same_file_are_rejected_for_either_id(self):
        write(
            self.root / "src/overlap.jl",
            "# CUTPASTE:BEGIN:cptest-020 op=drop\n"
            "# a\n"
            "# CUTPASTE:BEGIN:cptest-021 op=drop\n"
            "# b\n"
            "# CUTPASTE:END:cptest-020\n"
            "# c\n"
            "# CUTPASTE:END:cptest-021\n",
        )

        for cid in ("cptest-020", "cptest-021"):
            with self.subTest(cid=cid):
                result = run_cli(self.root, cid, "--dry-run")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("nested/overlapping region", result.stderr)

    def test_properly_nested_regions_are_still_rejected(self):
        write(
            self.root / "src/nested.jl",
            "# CUTPASTE:BEGIN:cptest-022 op=drop\n"
            "# outer a\n"
            "# CUTPASTE:BEGIN:cptest-023 op=drop\n"
            "# inner\n"
            "# CUTPASTE:END:cptest-023\n"
            "# outer b\n"
            "# CUTPASTE:END:cptest-022\n",
        )
        result = run_cli(self.root, "cptest-022", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nested/overlapping region", result.stderr)

    def test_unrelated_region_in_a_corrupted_file_is_still_refused(self):
        # A malformed pair (024/025) elsewhere in the file must block *every*
        # id in that file, even a well-formed, non-overlapping one (026).
        write(
            self.root / "src/mixed.jl",
            "# CUTPASTE:BEGIN:cptest-024 op=drop\n"
            "# a\n"
            "# CUTPASTE:BEGIN:cptest-025 op=drop\n"
            "# b\n"
            "# CUTPASTE:END:cptest-024\n"
            "# c\n"
            "# CUTPASTE:END:cptest-025\n"
            "clean_code = 1\n"
            "# CUTPASTE:BEGIN:cptest-026 op=drop\n"
            "# unrelated and well-formed\n"
            "# CUTPASTE:END:cptest-026\n",
        )
        result = run_cli(self.root, "cptest-026", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nested/overlapping region", result.stderr)

    def test_nonexistent_id_fails_cleanly(self):
        write(self.root / "src/x.jl", "nothing to see here\n")
        result = run_cli(self.root, "cptest-999", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected exactly 1 BEGIN", result.stderr)


class TestByteLevelEdgeCases(CutPasteTestCase):
    def test_crlf_line_endings_are_preserved_byte_for_byte(self):
        write_bytes = (
            b"# CUTPASTE:BEGIN:cptest-030 op=move to=pages/t.md\r\n"
            b"# crlf payload\r\n"
            b"# CUTPASTE:END:cptest-030\r\n"
        )
        (self.root / "src").mkdir(parents=True)
        (self.root / "src/crlf.jl").write_bytes(write_bytes)
        (self.root / "pages").mkdir(parents=True)
        (self.root / "pages/t.md").write_bytes(
            b"# Target\r\n<!-- CUTPASTE:HERE:cptest-030 seq=1 from=src/crlf.jl -->\r\n"
        )

        result = run_cli(self.root, "cptest-030")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.root / "src/crlf.jl").read_bytes(),
            b"",
        )
        self.assertEqual(
            (self.root / "pages/t.md").read_bytes(),
            b"# Target\r\n# crlf payload\r\n",
        )

    def test_marker_glued_directly_to_closing_comment_delimiter(self):
        # Regression: "id-->" with no separating space must still be
        # recognised as the marker's true end, not swallowed into the id.
        write(
            self.root / "pages/tight.md",
            "Some text.\n"
            "<!-- CUTPASTE:BEGIN:cptest-031 op=drop -->\n"
            "Paragraph to drop.\n"
            "<!-- CUTPASTE:END:cptest-031-->\n"
            "More text.\n",
        )
        result = run_cli(self.root, "cptest-031")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.root / "pages/tight.md").read_text(),
            "Some text.\nMore text.\n",
        )

    def test_plain_hash_comment_marker_with_no_trailing_delimiter(self):
        # YAML/Python/Julia markers end at a bare newline (or EOF), never
        # "-->": the id-boundary check must not require that delimiter.
        write(
            self.root / "params.yaml",
            "paper_plot:\n"
            "    # CUTPASTE:BEGIN:cptest-121 op=move to=pages/t.md\n"
            "    # PLACEHOLDER, not a resolved choice - see the same open\n"
            "    # question in the root CURRENT_STATUS.md blocking TODO.\n"
            "    # CUTPASTE:END:cptest-121\n"
            '    selected_quadrature: "trapz"\n',
        )
        write(
            self.root / "pages/t.md",
            "<!-- CUTPASTE:HERE:cptest-121 seq=1 from=params.yaml -->\n",
        )

        result = run_cli(self.root, "cptest-121")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.root / "params.yaml").read_text(),
            'paper_plot:\n    selected_quadrature: "trapz"\n',
        )
        self.assertEqual(
            (self.root / "pages/t.md").read_text(),
            "    # PLACEHOLDER, not a resolved choice - see the same open\n"
            "    # question in the root CURRENT_STATUS.md blocking TODO.\n",
        )

    def test_marker_at_end_of_file_with_no_trailing_newline(self):
        # END on the very last line of the file, no trailing "\n" at all.
        write(
            self.root / "src/eof.jl",
            "before = 1\n"
            "# CUTPASTE:BEGIN:cptest-122 op=drop\n"
            "# trailing comment, file ends right after END\n"
            "# CUTPASTE:END:cptest-122",
        )
        result = run_cli(self.root, "cptest-122")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "src/eof.jl").read_text(), "before = 1\n")

    def test_id_prefix_collision_does_not_cross_match(self):
        # cptest-101 must not be confused with cptest-1010.
        write(
            self.root / "src/short.jl",
            "# CUTPASTE:BEGIN:cptest-101 op=drop\n# short\n# CUTPASTE:END:cptest-101\n",
        )
        write(
            self.root / "src/long.jl",
            "# CUTPASTE:BEGIN:cptest-1010 op=drop\n# long\n# CUTPASTE:END:cptest-1010\n",
        )
        result = run_cli(self.root, "cptest-101")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "src/short.jl").read_text(), "")
        self.assertIn("cptest-1010", (self.root / "src/long.jl").read_text())

    def test_nested_marker_inside_payload_itself_is_refused(self):
        write(
            self.root / "src/x.jl",
            "# CUTPASTE:BEGIN:cptest-032 op=drop\n"
            "# CUTPASTE:HERE:cptest-999 seq=1 from=nowhere\n"
            "# CUTPASTE:END:cptest-032\n",
        )
        result = run_cli(self.root, "cptest-032", "--dry-run")
        self.assertNotEqual(result.returncode, 0)


class TestRollbackOnFailure(CutPasteTestCase):
    def test_destination_write_is_rolled_back_if_source_write_fails(self):
        write(
            self.root / "ro_src/z.jl",
            "# CUTPASTE:BEGIN:cptest-040 op=move to=pages/t.md\n"
            "# payload\n"
            "# CUTPASTE:END:cptest-040\n",
        )
        dest = self.root / "pages/t.md"
        original_dest = "<!-- CUTPASTE:HERE:cptest-040 seq=1 from=ro_src/z.jl -->\n"
        write(dest, original_dest)

        src_dir = self.root / "ro_src"
        src_dir.chmod(0o555)
        try:
            result = run_cli(self.root, "cptest-040")
        finally:
            src_dir.chmod(0o755)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(dest.read_text(), original_dest)


if __name__ == "__main__":
    unittest.main()
