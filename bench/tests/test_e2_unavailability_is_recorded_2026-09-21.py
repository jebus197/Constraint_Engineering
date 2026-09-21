"""An unconsulted gate must leave a trace. Found by the cc2 seat, verified here.

THE DEFECT. `compute_sk` recorded `e2_regression` as unavailable under
`elif test_cmd:`, so the absence was logged ONLY when a test command existed and
the run failed. With no test command configured the single most informative
effect gate was dropped from the renormalised mean leaving NO entry in
`_unavailable`, and a 2-gate E is numerically indistinguishable from a 3-gate
one. A reader of the archive cannot tell which gates were consulted.

MEASURED over every archived verdict, and the seat's figures reproduce exactly:
of 902 ADMISSIBLE records, 140 have `e2_score is None`; 121 carry
`_unavailable: ['e2_regression']` and **19 carry nothing at all** -- 13.5714%,
Wilson [8.8635%, 20.2251%], cross-checked against statsmodels. All 19 read "no
test command configured", and they are not recoverable from the persisted record.

PROVENANCE. Found by the cc2 seat in the open panel round of 2026-09-20 and
delivered as a file in its own sandbox. It was reproduced independently before
being applied, because `fff-external` binds a model's proposed fix exactly as it
binds one of ours.

WHAT THIS FILE CHANGES ABOUT THE SEAT'S OWN FALSIFIER. The seat proved the
additivity half by reading `inspect.getsource(compute_sk)` and checking that no
line mentioning `unavailable_gates` also computes E. That is a statement about
how the module describes itself, and `execute-do-not-grep` exists because this
project has lost 4 defects to exactly that. The additivity is established here by
CALLING the scorer across the cases that differ and requiring the verdicts to be
identical.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[1]
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import reference_runner_v3 as R  # noqa: E402

TARGET = "bench/_e2_record_probe.py"
SOURCE = 'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
FIX = (
    "<<<< SEARCH\n"
    'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
    "====\n"
    'def divide(a, b):\n    """Guarded."""\n    if b == 0:\n'
    '        raise ValueError("b must be non-zero")\n    return a / b\n'
    ">>>> REPLACE"
)


@pytest.fixture(scope="module")
def baseline():
    return R._capture_baseline(SOURCE, source_path=TARGET)


def test_e2_unavailability_is_recorded_when_no_test_command_is_configured(baseline):
    """RED at the parent: this is the 19-record case, and it recorded nothing."""
    r = R.compute_sk(FIX, SOURCE, TARGET, baseline=baseline, test_cmd=None)
    assert r.gate_details["e2_regression"]["score"] is None
    assert "no test command" in r.gate_details["e2_regression"]["detail"]
    assert "e2_regression" in (r.gate_details.get("_unavailable") or []), (
        "e2 was dropped from the weighted mean with no entry in _unavailable, so "
        "the record cannot say which gates were consulted"
    )


def test_a_configured_but_failing_test_command_still_records(baseline):
    """The control. Green on both sides -- the fix must not have moved this."""
    r = R.compute_sk(FIX, SOURCE, TARGET, baseline=baseline,
                     test_cmd="this-binary-does-not-exist")
    assert r.gate_details["e2_regression"]["score"] is None
    assert "e2_regression" in (r.gate_details.get("_unavailable") or [])


def test_recording_an_unavailable_gate_changes_no_verdict(baseline):
    """ADDITIVITY, ESTABLISHED BY CALLING rather than by reading the source.

    E is recomputed here from the SCORED gates alone and must equal the E the
    scorer returned. If `unavailable_gates` ever reached the computation, the
    two would diverge and this fails -- which a source-text scan cannot detect,
    because a module that computes the wrong thing consistently still describes
    itself consistently.
    """
    weights = {"e1_efficacy": R.FIX_EFFICACY_GATE_WEIGHT,
               "e2_regression": 2.0, "e3_ruff": 1.0, "e4_bandit": 2.0}
    for test_cmd in (None, "this-binary-does-not-exist"):
        r = R.compute_sk(FIX, SOURCE, TARGET, baseline=baseline, test_cmd=test_cmd)
        live = [(float(r.gate_details[g]["score"]), w)
                for g, w in weights.items()
                if isinstance(r.gate_details.get(g), dict)
                and r.gate_details[g].get("score") is not None]
        total = sum(w for _, w in live)
        expected = sum((w / total) * s for s, w in live)
        assert r.E == pytest.approx(expected, abs=5e-4), (
            f"E depends on something other than the scored gates "
            f"(test_cmd={test_cmd!r}): returned {r.E}, scored gates give {expected}"
        )
        assert r.tristate == R.SK_ADMISSIBLE


def test_the_unavailable_record_names_every_gate_that_did_not_score(baseline):
    """The record must be COMPLETE, not merely non-empty.

    A record listing some unconsulted gates and not others is worse than none:
    it reads as an exhaustive list and is not one, which is how the 19 came to
    look like the 121.
    """
    r = R.compute_sk(FIX, SOURCE, TARGET, baseline=baseline, test_cmd=None)
    silent = {g for g in ("e1_efficacy", "e2_regression", "e3_ruff", "e4_bandit")
              if isinstance(r.gate_details.get(g), dict)
              and r.gate_details[g].get("score") is None}
    recorded = set(r.gate_details.get("_unavailable") or [])
    assert silent == recorded, (
        f"gates that did not score: {sorted(silent)}; "
        f"gates recorded as unavailable: {sorted(recorded)}"
    )
