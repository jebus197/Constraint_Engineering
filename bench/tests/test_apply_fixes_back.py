"""Regression tests for the Exp 40 plan-C apply-verified-fixes-back
(2026-05-16, founder-directed structural cure).

Contract: when enabled, a finding that reached full BUGZILLA close has
its SEARCH/REPLACE patch promoted into a PER-RUN working copy that the
next round reviews — but ONLY if the cumulative working copy still
passes the full canonical suite (the C0001 collation lesson: the
run-time S_k score tolerates regressions). Promotion is idempotent
across rounds; rejected fixes stay CLOSED in the registry but are NOT
applied to the artefact; the repo file is never written.

The real sandbox+suite gate is exercised end-to-end by
bench/exp40_fix_collation.py (pristine passes, C0001 correctly
rejected). These tests stub the gate to validate the promote LOGIC
(eligibility, cumulative application, idempotence, applied/rejected
tracking, working-copy write) deterministically and fast.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

import bench.reference_runner_v3 as rr


class _Cfg:
    def __init__(self, enabled, seed="", test_cmd="pytest -q"):
        self.apply_fixes_back_enabled = enabled
        self.apply_fixes_back_seed = seed
        self.test_cmd = test_cmd


class _Reg:
    def __init__(self, entries):
        self.entries = entries


def _fix(search, replace, path="_t.py"):
    return f"<<<< SEARCH {path}\n{search}\n====\n{replace}\n>>>> REPLACE"


@pytest.fixture(autouse=True)
def _restore_ctx():
    saved = dict(rr._APPLY_BACK_CTX)
    yield
    rr._APPLY_BACK_CTX.clear()
    rr._APPLY_BACK_CTX.update(saved)


def test_setup_disabled_returns_original_path(tmp_path):
    tgt = tmp_path / "_t.py"
    tgt.write_text("A = 1\n")
    out = rr._apply_back_setup(_Cfg(False), tgt, tmp_path / "logs")
    assert out == tgt
    assert rr._APPLY_BACK_CTX == {}


def test_setup_enabled_creates_working_copy(tmp_path):
    tgt = tmp_path / "_t.py"
    tgt.write_text("A = 1\nB = 2\n")
    logs = tmp_path / "logs"
    out = rr._apply_back_setup(_Cfg(True), tgt, logs)
    assert out == logs / "working" / "_t.py"
    assert out.read_text() == "A = 1\nB = 2\n"
    assert tgt.read_text() == "A = 1\nB = 2\n"  # pristine untouched
    assert rr._APPLY_BACK_CTX["enabled"] is True
    assert rr._APPLY_BACK_CTX["pristine_path"] == tgt


def test_setup_seeded_from_baseline(tmp_path):
    tgt = tmp_path / "_t.py"
    tgt.write_text("ORIGINAL\n")
    seed = tmp_path / "cleaned.py"
    seed.write_text("SEEDED_CLEAN\n")
    out = rr._apply_back_setup(_Cfg(True, seed=str(seed)), tgt,
                               tmp_path / "logs")
    assert out.read_text() == "SEEDED_CLEAN\n"


def test_promote_applies_green_rejects_regressing_idempotent(
        tmp_path, monkeypatch):
    tgt = tmp_path / "_t.py"
    tgt.write_text("A = 1\nB = 2\n")
    rr._apply_back_setup(_Cfg(True), tgt, tmp_path / "logs")

    # Gate stub: red iff the candidate source contains "BAD".
    monkeypatch.setattr(
        rr, "_apply_back_gate",
        lambda src, rel, tc: (("BAD" not in src),
                              "ok" if "BAD" not in src else "suite_fail:x"))

    reg = _Reg({
        "C1": {"status": "CLOSED",
               "proposed_fix": _fix("A = 1", "A = 11")},      # green
        "C2": {"status": "CLOSED",
               "proposed_fix": _fix("B = 2", "B = BAD")},      # regresses
        "C3": {"status": "OPEN",
               "proposed_fix": _fix("A = 1", "A = 9")},        # not closed
        "C4": {"status": "CLOSED", "proposed_fix": ""},        # no fix
    })

    new_src = rr._apply_back_promote(reg, round_idx=2)
    assert new_src is not None
    assert "A = 11" in new_src and "BAD" not in new_src
    assert rr._APPLY_BACK_CTX["applied"] == ["C1"]
    rej = {cid for cid, _ in rr._APPLY_BACK_CTX["rejected"]}
    assert "C2" in rej and "C3" not in rej and "C4" not in rej
    # working copy written; pristine still untouched
    assert (tmp_path / "logs" / "working" / "_t.py").read_text() == new_src
    assert tgt.read_text() == "A = 1\nB = 2\n"

    # Idempotent: a second call promotes nothing new.
    assert rr._apply_back_promote(reg, round_idx=3) is None
    assert rr._APPLY_BACK_CTX["applied"] == ["C1"]


def test_promote_noop_when_disabled():
    rr._APPLY_BACK_CTX.clear()
    assert rr._apply_back_promote(_Reg({}), round_idx=1) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
