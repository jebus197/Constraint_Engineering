"""Scratch files must never be written beside a read-only staged target.

The exam targets are staged read-only in a directory set to refuse new files, so
a panel cannot drop anything beside the document it is reviewing. Four gate
helpers (compile, ruff, bandit, baseline) anchored their scratch file to the
target's own directory, which is right for a Python target inside this repository
— the tools discover pyproject.toml by walking upwards — and fatal for a staged
markdown one.

The first launch of the zero-plant control died one second in:

    PermissionError: [Errno 13] Permission denied:
      '/Users/.../CDSFL_review_targets/SW-21-REF-04/tmpkd2r728e.py'

Both controls were correct; anchoring was simply the wrong default for a target
that is not code we own. Three of the four call sites fire mid-run rather than at
startup, so the same collision would have surfaced after real money had been spent
rather than before.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from bench.reference_runner_v3 import _anchor_dir_for  # noqa: E402


class TestAnchorDir:
    def test_writable_python_target_anchors_beside_itself(self, tmp_path):
        """Config discovery must still work for a Python target we own."""
        src = tmp_path / "module.py"
        src.write_text("x = 1\n", encoding="utf-8")
        assert _anchor_dir_for(str(src)) == str(tmp_path)

    def test_markdown_target_never_anchors(self, tmp_path):
        """An exam target is not code; there is no config to discover."""
        src = tmp_path / "PX-12-REF-05.md"
        src.write_text("**PH-01.** claim\n", encoding="utf-8")
        assert _anchor_dir_for(str(src)) is None

    def test_read_only_directory_never_anchors(self, tmp_path):
        """The staged layout exactly: mode 444 file inside a mode 555 directory."""
        d = tmp_path / "SW-21-REF-04"
        d.mkdir()
        f = d / "SW-21-REF-04.py"          # .py, so only the mode can save us
        f.write_text("x = 1\n", encoding="utf-8")
        os.chmod(f, 0o444)
        os.chmod(d, 0o555)
        try:
            assert _anchor_dir_for(str(f)) is None, (
                "anchoring into a directory that refuses new files is the EPERM "
                "that killed the first control launch")
        finally:
            os.chmod(d, 0o755)

    def test_empty_source_path_is_safe(self):
        assert _anchor_dir_for("") is None

    def test_a_scratch_file_can_actually_be_created_for_a_staged_target(self, tmp_path):
        """End to end: the value returned must be usable, not merely non-crashing."""
        d = tmp_path / "BX-14-REF-04"
        d.mkdir()
        f = d / "BX-14-REF-04.md"
        f.write_text("**BI-01.** claim\n", encoding="utf-8")
        os.chmod(f, 0o444)
        os.chmod(d, 0o555)
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=True, encoding="utf-8",
                dir=_anchor_dir_for(str(f)),
            ) as tmp:
                tmp.write("x = 1\n")
                assert Path(tmp.name).parent != d
        finally:
            os.chmod(d, 0o755)


class TestNoInlinedDuplicates:
    def test_every_call_site_uses_the_helper(self):
        """Four sites had this logic inlined; a fifth was a matter of time."""
        src = Path(_root, "bench", "reference_runner_v3.py").read_text(encoding="utf-8")
        assert "anchor_dir = str(Path(source_path).parent)" not in src, (
            "an inlined anchor derivation has reappeared — route it through "
            "_anchor_dir_for so the read-only staging case stays covered")
        assert src.count("_anchor_dir_for(source_path)") >= 4
