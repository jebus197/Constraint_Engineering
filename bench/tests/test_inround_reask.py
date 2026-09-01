"""Regression tests for the Exp 40 plan-B in-round re-ask
(2026-05-16, founder-directed — supersedes the 1e next-round-only
deferral).

Trigger contract: enabled AND 0 findings parsed AND >= min_markers
finding-declaration markers in the raw text AND the text is a real
model response. Effect: exactly ONE re-dispatch to that model with a
STRUCTURE_VIOLATION corrective prompt; on recovery the retry output
REPLACES the round's output for that model (idempotent, no
double-count); on failure the original is returned unchanged. 1e
remains the next-round fallback.
"""
from __future__ import annotations

import pytest

import bench.reference_runner_v3 as rr


class _MC:
    label = "CC2"
    timeout = 60


@pytest.fixture(autouse=True)
def _restore_state(monkeypatch):
    # snapshot + restore the module config mirror around every test
    saved = dict(rr._INROUND_REASK)
    yield
    rr._INROUND_REASK.clear()
    rr._INROUND_REASK.update(saved)


def _patch_dispatch(monkeypatch, retry_text):
    """dispatch_to_model returns retry_text; counts calls so we can
    assert the retry is bounded to exactly one."""
    calls = {"n": 0}

    def fake_dispatch(mc, prompt, cdsfl, wall_clock_limit=None):
        calls["n"] += 1
        return retry_text, 0.1

    monkeypatch.setattr(rr, "dispatch_to_model", fake_dispatch)
    monkeypatch.setattr(rr, "_record_throughput", lambda *a, **k: None)
    return calls


# Two finding-declaration markers so raw-marker count >= default min 2.
MALFORMED = "FINDING_ID: F01 ... prose ...\nFINDING_ID: F02 ... prose ..."


def test_disabled_no_reask(monkeypatch):
    rr._INROUND_REASK.update(enabled=False, min_markers=2)
    calls = _patch_dispatch(monkeypatch, "irrelevant")
    f, t, did = rr._inround_reask(_MC(), "p", "c", 1, MALFORMED, [], 60)
    assert did is False and f == [] and t == MALFORMED and calls["n"] == 0


def test_findings_present_no_reask(monkeypatch):
    rr._INROUND_REASK.update(enabled=True, min_markers=2)
    calls = _patch_dispatch(monkeypatch, "x")
    f, t, did = rr._inround_reask(_MC(), "p", "c", 1, MALFORMED,
                                  ["existing"], 60)
    assert did is False and f == ["existing"] and calls["n"] == 0


def test_below_marker_threshold_no_reask(monkeypatch):
    rr._INROUND_REASK.update(enabled=True, min_markers=2)
    calls = _patch_dispatch(monkeypatch, "x")
    f, t, did = rr._inround_reask(_MC(), "p", "c", 1,
                                  "FINDING_ID: only one marker", [], 60)
    assert did is False and calls["n"] == 0


def test_dispatch_failed_sentinel_no_reask(monkeypatch):
    rr._INROUND_REASK.update(enabled=True, min_markers=2)
    calls = _patch_dispatch(monkeypatch, "x")
    f, t, did = rr._inround_reask(_MC(), "p", "c", 1,
                                  "__DISPATCH_FAILED__:TimeoutError", [], 60)
    assert did is False and calls["n"] == 0


def test_recovers_on_retry_replaces_output(monkeypatch):
    rr._INROUND_REASK.update(enabled=True, min_markers=2)
    calls = _patch_dispatch(monkeypatch, "GOOD_REFORMATTED_TEXT")
    monkeypatch.setattr(
        rr, "parse_findings",
        lambda label, rnd, text: (["rf1", "rf2"]
                                  if text == "GOOD_REFORMATTED_TEXT" else []))
    f, t, did = rr._inround_reask(_MC(), "p", "c", 1, MALFORMED, [], 60)
    assert did is True
    assert f == ["rf1", "rf2"]          # retry output replaces round output
    assert t == "GOOD_REFORMATTED_TEXT"
    assert calls["n"] == 1              # bounded: exactly one re-dispatch


def test_still_malformed_keeps_original_bounded(monkeypatch):
    rr._INROUND_REASK.update(enabled=True, min_markers=2)
    calls = _patch_dispatch(monkeypatch, "STILL BAD")
    monkeypatch.setattr(rr, "parse_findings", lambda label, rnd, text: [])
    f, t, did = rr._inround_reask(_MC(), "p", "c", 1, MALFORMED, [], 60)
    assert did is True                 # it did re-ask
    assert f == [] and t == MALFORMED  # original returned (no worse)
    assert calls["n"] == 1             # still bounded to one retry (no loop)


def test_retry_dispatch_exception_keeps_original(monkeypatch):
    rr._INROUND_REASK.update(enabled=True, min_markers=2)

    def boom(mc, prompt, cdsfl, wall_clock_limit=None):
        raise TimeoutError("model timed out on retry")

    monkeypatch.setattr(rr, "dispatch_to_model", boom)
    monkeypatch.setattr(rr, "_record_throughput", lambda *a, **k: None)
    f, t, did = rr._inround_reask(_MC(), "p", "c", 1, MALFORMED, [], 60)
    assert did is True and f == [] and t == MALFORMED


def test_corrective_prompt_has_structure_violation_header():
    out = rr._build_inround_reask_prompt("ORIGINAL_TASK_BODY")
    assert "STRUCTURE_VIOLATION" in out
    assert "ORIGINAL_TASK_BODY" in out
    assert out.index("STRUCTURE_VIOLATION") < out.index("ORIGINAL_TASK_BODY")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
