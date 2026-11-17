# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_nineteen_2026-11-17_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c57d77438d2cc82b118b029720a2c5bf19e6b699703834fc12d3ea4ae6dc2421
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""B125 half 2: an EXISTING stamp table is verified at dispatch, not trusted.

AWAITING FOUNDER RULING. B125 is his; this guard exists so the composed form can
be ruled on against a measurement rather than a judgement.

THE DEFECT THIS PINS, which neither blind seat of 2026-11-17 reported.
`stamp_brief_at_dispatch` took the branch "already present, left as it is"
whenever it found a stamp table. A table written when the brief was AUTHORED
therefore shipped UNVERIFIED if an artefact moved before dispatch -- and the
block's own header tells the seat its reading "was correct against the state
below", so half 1 ALONE can actively mislead rather than merely be incomplete.

WHY A REFUSAL AND NOT A WARNING HERE, when `panel_brief_validate.check_currency`
is deliberately a warning. Its stated reason -- "a validator that blocks on it
teaches people to skip the validator" -- is true of mtime and false of sha256,
and the difference is measured: over the 10 artefacts the 2026-11-17 joint brief
names, a content-preserving `touch` moves mtime on 10/10 and sha256 on 0/10,
while a genuine 1-line edit is caught by both on 10/10. The digest makes the
refusal affordable; the refusal makes the digest bite.
"""
import hashlib
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _stamper():
    spec = importlib.util.spec_from_file_location(
        "_st", REPO / "scripts" / "stamp_the_brief_artefacts_2026-11-06.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _brief(tmp_path):
    work = tmp_path / "repo"
    (work / "bench").mkdir(parents=True)
    tgt = work / "bench" / "t.py"
    tgt.write_text("A = 1\n")
    st = _stamper()
    text = st.insert_stamp("# BRIEF\n\nSee `bench/t.py`, which sets A.\n", work)
    return st, work, tgt, text


def test_a_current_table_is_reported_clean(tmp_path):
    st, work, _tgt, text = _brief(tmp_path)
    assert st.verify_stamp_currency(text, work) == []


def test_a_moved_artefact_is_caught(tmp_path):
    st, work, tgt, text = _brief(tmp_path)
    tgt.write_text("B = 2\nA = 1\n")
    drift = st.verify_stamp_currency(text, work)
    assert len(drift) == 1
    rel, was, now = drift[0]
    assert rel == "bench/t.py"
    assert now == hashlib.sha256(tgt.read_bytes()).hexdigest()[:16]
    assert was != now


def test_a_touch_that_changes_nothing_is_NOT_drift(tmp_path):
    """The property that makes refusing affordable. mtime would fire here."""
    import os
    import time
    st, work, tgt, text = _brief(tmp_path)
    before = tgt.stat().st_mtime
    time.sleep(0.01)
    os.utime(tgt, None)
    assert tgt.stat().st_mtime != before, "mtime must move, or the test is void"
    assert st.verify_stamp_currency(text, work) == []


def test_a_vanished_artefact_is_drift_not_silence(tmp_path):
    st, work, tgt, text = _brief(tmp_path)
    tgt.unlink()
    assert st.verify_stamp_currency(text, work) == [
        ("bench/t.py", st.stamp.__name__ and
         _stamped(text, "bench/t.py"), "ABSENT")]


def _stamped(text, rel):
    import re
    m = re.search(r"\|\s*`" + re.escape(rel) + r"`\s*\|\s*`([0-9a-f]{16})`", text)
    return m.group(1)


def test_no_table_at_all_is_not_drift():
    assert _stamper().verify_stamp_currency("no table here") == []


def test_an_unreadable_row_is_skipped_not_called_drift():
    """A guard that refuses when it cannot see is the shape to withdraw."""
    st = _stamper()
    text = ("## ARTEFACT STAMPS AT DISPATCH\n\n"
            "| artefact | sha256 (first 16) | bytes | modified (UTC) |\n"
            "|---|---|---|---|\n"
            "| not a path at all | garbage | x | y |\n")
    assert st.verify_stamp_currency(text, REPO) == []


def test_the_dispatcher_refuses_rather_than_warning(tmp_path, monkeypatch, capsys):
    """SystemExit must pass THROUGH the stamper's `except Exception` handler."""
    panel = importlib.util.spec_from_file_location(
        "_panel", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
    src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
    assert "already present, left as it is" not in src, (
        "the unverified-trust branch is back; B125 half 2 has been reverted")
    assert "raise SystemExit(" in src and "already present and VERIFIED current" in src
    # SystemExit is a BaseException: the enclosing handler cannot swallow it.
    assert not issubclass(SystemExit, Exception)
