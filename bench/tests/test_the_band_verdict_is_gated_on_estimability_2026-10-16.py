#!/usr/bin/env python3
"""The boundary-band verdict must not rest on the gamma sentinel.

HIS RULING, 2026-10-16, on the 7 smaller defects including this one: *"Fix it
all."*

THE DEFECT. `_estimate_gamma` returns 0.0 for FOUR distinct reasons and only one
is a slope of 0.0; its own mirror `_gamma_is_estimable` names the other three.
`gamma_threshold_profile` compared the two band edges for equality, so two
SENTINELS compared equal and the run was reported *robust to the whole rubric
disagreement* on the strength of a quantity never measured. Measured by
`scripts/the_band_verdict_rests_on_a_sentinel_2026-10-16.py` over the archive:
**10 of 26 blocks claim `verdict_robust_to_band: true` on two 0.0 sentinels**
(38.4615%, Wilson [22.4286%, 57.4651%], Clopper-Pearson [20.2260%, 59.4292%]),
and 4 more compare a real edge against a sentinel, so **14 of 26 verdicts
carried no information** (53.8462%, Wilson [35.4579%, 71.2441%]).

WHY A FALSE "ROBUST" MATTERS MORE THAN A MISSING ONE. The disagreement it
retires is large and measured: across 286 archived findings in that band the
numeric proxy and the five-clause rubric agree on 141 of 259 judgeable cases
(54.4%), while two blind readers agreed with each other on 86 of 93 (92.5%,
Cohen's kappa 0.837). Reporting robustness there says "nothing in the disputed
band could have moved the verdict", which is exactly the question the
pre-registration demanded be kept open.

`execute-do-not-grep`: every test below CALLS `gamma_threshold_profile` against
a registry stub and reads the dictionary it returns. Nothing asserts on source.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "bench"))

import reference_runner_v3 as R  # noqa: E402

LO_KEY, HI_KEY = "0.65", "0.75"


def profile_from_series(monkeypatch, series_by_threshold):
    """Drive the REAL reporter, controlling only the novelty series it reads.

    `_settled_novelty_series` is the single input the profile derives gamma
    from, so substituting it exercises every line of the block under test while
    needing no registry fixture.
    """
    def fake(registry, max_round, severity_threshold=None):
        key = repr(float(severity_threshold))
        crit = series_by_threshold.get(key, series_by_threshold.get("*", []))
        return list(crit), list(crit)

    monkeypatch.setattr(R, "_settled_novelty_series", fake)
    return R.gamma_threshold_profile(object(), max_round=5, min_rounds=3)


#: A series with no novelty at all: `_estimate_gamma` returns the 0.0 SENTINEL
#: and `_gamma_is_estimable` is False. This is the archive's commonest case.
SENTINEL_SERIES = [0, 0, 0, 0, 0, 0]
#: A decaying series: a real slope, estimable.
REAL_SERIES = [8, 4, 2, 1, 0, 0]
#: A different real slope, so the two edges genuinely differ.
OTHER_REAL_SERIES = [2, 2, 2, 2, 1, 0]


def test_the_sentinel_series_is_not_estimable_and_the_real_one_is():
    """The premise every test below rests on, established by execution."""
    assert R._gamma_is_estimable(SENTINEL_SERIES, 3) is False
    assert R._estimate_gamma(SENTINEL_SERIES, 3) == 0.0
    assert R._gamma_is_estimable(REAL_SERIES, 3) is True
    assert R._gamma_is_estimable(OTHER_REAL_SERIES, 3) is True


def test_two_sentinels_do_not_report_a_robust_verdict(monkeypatch):
    """THE DEFECT ITSELF. Two unmeasured edges must not read as agreement."""
    out = profile_from_series(monkeypatch, {"*": SENTINEL_SERIES})
    band = out["boundary_band_sensitivity"]
    assert band["gamma_at_lower_edge"] == 0.0
    assert band["gamma_at_upper_edge"] == 0.0
    assert band["verdict_robust_to_band"] is None, (
        "two 0.0 sentinels still compare as a robust verdict. That reports the "
        "run as insensitive to a 46% rubric disagreement on the strength of a "
        "quantity that was never measured."
    )
    assert band["band_is_readable"] is False
    assert band["not_readable_because"], band


def test_one_sentinel_edge_does_not_report_a_fragile_verdict(monkeypatch):
    """The other direction: a real edge against a sentinel is not a finding.

    The pre-repair code reported FALSE here -- a false alarm, claiming the
    verdict is fragile on the basis of a number that does not exist.
    """
    out = profile_from_series(monkeypatch, {
        LO_KEY: REAL_SERIES, HI_KEY: SENTINEL_SERIES, "*": REAL_SERIES})
    band = out["boundary_band_sensitivity"]
    assert band["gamma_estimable_at_lower_edge"] is True
    assert band["gamma_estimable_at_upper_edge"] is False
    assert band["verdict_robust_to_band"] is None, band
    assert band["band_is_readable"] is False


def test_two_real_and_equal_edges_do_report_robust(monkeypatch):
    """The gate must not swallow the genuine answer it exists to protect."""
    out = profile_from_series(monkeypatch, {"*": REAL_SERIES})
    band = out["boundary_band_sensitivity"]
    assert band["band_is_readable"] is True
    assert band["gamma_at_lower_edge"] == band["gamma_at_upper_edge"]
    assert band["verdict_robust_to_band"] is True, band
    assert band["not_readable_because"] is None


def test_two_real_and_differing_edges_report_not_robust(monkeypatch):
    """And a genuine fragility must still be reported as one."""
    out = profile_from_series(monkeypatch, {
        LO_KEY: REAL_SERIES, HI_KEY: OTHER_REAL_SERIES, "*": REAL_SERIES})
    band = out["boundary_band_sensitivity"]
    assert band["band_is_readable"] is True
    assert band["gamma_at_lower_edge"] != band["gamma_at_upper_edge"], band
    assert band["verdict_robust_to_band"] is False, band


def test_the_edge_values_are_still_reported_when_unreadable(monkeypatch):
    """The inputs are not withheld, only the verdict that cannot rest on them."""
    out = profile_from_series(monkeypatch, {"*": SENTINEL_SERIES})
    band = out["boundary_band_sensitivity"]
    for key in ("gamma_at_lower_edge", "gamma_at_upper_edge", "band",
                "basis"):
        assert key in band, key
    assert band["band"] == [0.65, 0.75]


def test_estimability_is_reported_for_every_threshold(monkeypatch):
    """The flag travels with the number, so no consumer has to re-derive it."""
    out = profile_from_series(monkeypatch, {"*": SENTINEL_SERIES})
    assert out["thresholds"], out
    for key, row in out["thresholds"].items():
        if "error" in row:
            continue
        assert "gamma_is_estimable" in row, key
        assert row["gamma_is_estimable"] is False, key

    out2 = profile_from_series(monkeypatch, {"*": REAL_SERIES})
    for key, row in out2["thresholds"].items():
        if "error" in row:
            continue
        assert row["gamma_is_estimable"] is True, key


def test_the_reported_flag_agrees_with_the_predicate_itself(monkeypatch):
    """Two forms, executed against each other, so they cannot drift.

    `execute-do-not-grep`: the reporter's flag and `_gamma_is_estimable` are
    independent code paths over the same input; a test that read one of them
    could not detect them disagreeing.
    """
    for series in (SENTINEL_SERIES, REAL_SERIES, OTHER_REAL_SERIES, [0], [5, 0, 0]):
        out = profile_from_series(monkeypatch, {"*": series})
        expected = R._gamma_is_estimable(series, 3)
        for key, row in out["thresholds"].items():
            if "error" in row:
                continue
            assert row["gamma_is_estimable"] == expected, (series, key, row)


def test_the_archive_is_not_rewritten():
    """The pre-repair blocks stay as recorded; only new runs are gated.

    Goes red once a run under the repaired reporter lands, which is the signal
    to re-measure the figures in this file rather than assume they hold.
    """
    import json

    logs = REPO_ROOT / "bench" / "logs"
    if not logs.is_dir():
        pytest.skip("no archive")
    total = gated = false_robust = 0
    for path in sorted(logs.rglob("*_report.json")):
        try:
            doc = json.loads(path.read_text(errors="replace"))
        except (OSError, ValueError):
            continue

        def walk(obj):
            nonlocal total, gated, false_robust
            if isinstance(obj, dict):
                blk = obj.get("boundary_band_sensitivity")
                if isinstance(blk, dict):
                    total += 1
                    if "band_is_readable" in blk:
                        gated += 1
                    if (blk.get("gamma_at_lower_edge") == 0.0
                            and blk.get("gamma_at_upper_edge") == 0.0
                            and blk.get("verdict_robust_to_band") is True):
                        false_robust += 1
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)

        walk(doc)
    assert total >= 20, total
    assert gated == 0, (
        f"{gated} of {total} archived blocks carry the estimability gate, so a "
        f"run under the repaired reporter has landed. Re-measure the figures in "
        f"this file's docstring."
    )
    assert false_robust == 10, (
        f"the archive now shows {false_robust} false-robust blocks, not the 10 "
        f"this file records. Re-derive the measurement with its producer."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
