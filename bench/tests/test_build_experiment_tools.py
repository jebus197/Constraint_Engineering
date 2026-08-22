"""Commissioning tests for the build experiment's read-only repository tools.

read_file's DEFAULT output must be byte-for-byte identical to the file, because a
model copies from it into a SEARCH block that is matched exactly. Until 2026-08-22
the default prefixed every line with a 6-character number and two spaces; Codex
stripped the digits, kept the separator, and every line it returned carried +2
indentation. Its Python was correct and the patch was rejected as
REJECTED_PATCH_DID_NOT_APPLY -- a harness failure rendering as a model failure.

The repair was to fix the READER, not to loosen the MATCHER: a fuzzy SEARCH would
let a patch land somewhere it was never meant to, which is far worse than a
rejection.
"""
from __future__ import annotations

import pathlib

import pytest

from bench.build_experiment_tools import REPO, execute

SAMPLE = "bench/dm/_types.py"


def test_read_file_default_output_is_verbatim():
    src = (REPO / SAMPLE).read_text(encoding="utf-8")
    out = execute("read_file", {"path": SAMPLE, "start": 1, "end": 20})
    assert out in src, "default read_file output is not byte-identical to the file"


def test_numbered_output_is_opt_in_and_is_not_verbatim():
    src = (REPO / SAMPLE).read_text(encoding="utf-8")
    out = execute("read_file", {"path": SAMPLE, "start": 1, "end": 20, "numbered": True})
    assert out not in src, "numbered output must be distinguishable from raw"
    assert out.lstrip().startswith("1"), "numbered output should carry line numbers"


def test_a_slice_round_trips():
    lines = (REPO / SAMPLE).read_text(encoding="utf-8").splitlines()
    out = execute("read_file", {"path": SAMPLE, "start": 5, "end": 9})
    assert out.splitlines() == lines[4:9]


@pytest.mark.parametrize("bad", ["../../../etc/passwd", "/etc/passwd"])
def test_paths_cannot_escape_the_repository(bad):
    assert "escapes the repository" in execute("read_file", {"path": bad}) \
        or "not a file" in execute("read_file", {"path": bad})


def test_tools_are_read_only_by_construction():
    """No tool may write. The panel sandbox is a second layer, not the only one."""
    src = (REPO / "bench/build_experiment_tools.py").read_text(encoding="utf-8")
    for banned in ("write_text(", "open(", "shutil.copy", "os.remove", "unlink("):
        assert banned not in src, f"{banned!r} appears in a read-only tool module"
