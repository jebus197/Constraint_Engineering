#!/usr/bin/env python3
"""A restore returns the BYTES and the MODIFICATION TIME, or it is not a restore.

DRAFTED 2026-11-22; destination `bench/tests/`, and onto the `GUARDS` list with
`bench/tests/_restore.py` which it guards.

WHY. Entry B201 found a guard that restored the bytes it mutated and left the
modification time moved, which turned a sibling currency check red on a record
whose CONTENT had not changed. It was fixed in 1 file.
`scripts/a_restore_that_moves_the_timestamp_2026-11-22.py` measures whether that
fix reached its class: of 84 guards that write a path and restore it in a
`finally`, **3 restore the timestamp and 81 do not**; **15 of those 81 mention no
temporary directory at all**. 2 of the 15 are confirmed writers, caught live
during a commit board on 2026-11-22, both writing explicit repository paths.

★ THE CASE THIS FILE EXISTS FOR IS THE 3rd ONE DOWN. A guard can assert
`path.read_bytes() == original` and be WRONG about having restored anything,
because a restore has 2 properties and that assertion covers 1. The live example
is `test_the_markdown_companion_is_generated_2026-10-30.py`, which proves the
content came back and calls `utime` 0 times. **A verified restore is still a
mutation when the verification covers half of what was changed.**

NOTHING HERE TOUCHES A REPOSITORY PATH. Every case runs under `tmp_path`, which
is the property the subject is meant to make unnecessary rather than one it is
allowed to rely on.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "bench" / "tests").is_dir():
            return cand
    fb = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
    if (fb / "bench" / "tests").is_dir():
        return fb
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()
#: A TEST SEAM, in the project's existing `CDSFL_*` style (`CDSFL_CY_LOGS`,
#: `CDSFL_BT_BOARD`), so this guard can be driven against the helper before
#: it is promoted into `bench/tests/`. It defaults to the real path, so a
#: normal run reaches exactly the file it guards.
SUBJECT = pathlib.Path(
    os.environ.get("CDSFL_RESTORE_PATH", REPO / "bench" / "tests" / "_restore.py"))
OLD_STAMP = (1_600_000_000.0, 1_600_000_000.0)
TOL = 1e-6


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("cdsfl_restore_guard", SUBJECT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_restore_guard"] = m
    spec.loader.exec_module(m)
    return m


def _aged(p: pathlib.Path, text: str) -> float:
    p.write_text(text)
    os.utime(p, OLD_STAMP)
    return p.stat().st_mtime


class TestBothPropertiesComeBack:
    def test_the_bytes_are_restored(self, mod, tmp_path):
        f = tmp_path / "a.txt"
        _aged(f, "original\n")
        with mod.restored_completely(f) as p:
            p.write_text("MUTATED\n")
        assert f.read_text() == "original\n"

    def test_the_timestamp_is_restored(self, mod, tmp_path):
        """THE POINT OF THE WHOLE FILE. B201's defect is exactly this assertion."""
        f = tmp_path / "b.txt"
        before = _aged(f, "original\n")
        with mod.restored_completely(f) as p:
            p.write_text("MUTATED\n")
        assert abs(f.stat().st_mtime - before) <= TOL, (
            "the bytes came back and the modification time did not, which is the "
            "defect B201 recorded and this helper exists to prevent")

    def test_a_byte_check_alone_would_have_passed(self, mod, tmp_path):
        """ANTI-VACUITY, and it names why the class stayed invisible.

        This drives the WEAKER assertion against a deliberately incomplete
        restore. It must PASS -- which is the point: a content check cannot see
        this defect, so a guard carrying only that check proves nothing about it.
        """
        f = tmp_path / "c.txt"
        original = b"original\n"
        f.write_bytes(original)
        os.utime(f, OLD_STAMP)
        before = f.stat().st_mtime
        # an incomplete restore: bytes only, exactly what 81 guards do today
        f.write_bytes(b"MUTATED\n")
        f.write_bytes(original)
        assert f.read_bytes() == original, "the weak check passes"
        assert abs(f.stat().st_mtime - before) > TOL, (
            "and the timestamp HAS moved, so the weak check passed over a real "
            "mutation -- if this assertion ever fails, the filesystem is not "
            "recording mtimes and the rest of this file proves nothing")


class TestTheHarderCases:
    def test_a_file_created_inside_is_removed(self, mod, tmp_path):
        f = tmp_path / "new.txt"
        with mod.restored_completely(f) as p:
            p.write_text("created inside\n")
        assert not f.exists(), (
            "the state found was ABSENT; recreating it empty would leave a path "
            "every later reader treats as real")

    def test_it_restores_through_an_exception(self, mod, tmp_path):
        f = tmp_path / "d.txt"
        before = _aged(f, "keep\n")
        with pytest.raises(RuntimeError):
            with mod.restored_completely(f) as p:
                p.write_text("broken\n")
                raise RuntimeError("boom")
        assert f.read_text() == "keep\n"
        assert abs(f.stat().st_mtime - before) <= TOL

    def test_an_untouched_file_is_left_alone(self, mod, tmp_path):
        f = tmp_path / "e.txt"
        before = _aged(f, "untouched\n")
        with mod.restored_completely(f):
            pass
        assert f.read_text() == "untouched\n"
        assert abs(f.stat().st_mtime - before) <= TOL, (
            "a restore that rewrites an unmodified file moves its timestamp for "
            "no reason, which is the same defect arriving by the other door")


class TestTheCheckerItself:
    def test_is_restored_requires_both(self, mod, tmp_path):
        f = tmp_path / "f.txt"
        original = b"original\n"
        f.write_bytes(original)
        os.utime(f, OLD_STAMP)
        st = f.stat()
        times = (st.st_atime, st.st_mtime)
        assert mod.is_restored(f, original, times)

        f.write_bytes(b"different\n")
        os.utime(f, OLD_STAMP)
        assert not mod.is_restored(f, original, times), "wrong bytes must fail"

        f.write_bytes(original)
        assert not mod.is_restored(f, original, times), "a moved mtime must fail"

    def test_a_missing_file_is_not_restored(self, mod, tmp_path):
        f = tmp_path / "gone.txt"
        assert not mod.is_restored(f, b"anything\n", OLD_STAMP)
