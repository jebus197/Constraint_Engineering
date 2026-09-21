"""S_k must measure what the appendix says S_k is. Executed, never grepped.

THE DEFECT THESE TESTS PIN, measured 2026-09-20 over the whole archive by
`scripts/scorer_discrimination_2026-09-20.py`.

`docs/MATHEMATICAL_APPENDIX.md` line 214 defines sigma as *"Does the proposed fix
actually resolve the detected flaw?"* and line 377 admits sigma only when it
compares pre-fix against post-fix tool output. `compute_rk` fills that slot with
`sk` term for term. But every gate feeding `sk` measured ABSENCE OF HARM -- does
the suite still pass, did the fix add lint findings, did it add security findings
-- and none asked whether the flaw was gone.

Measured consequence across the 135 archived entries carrying both a verdict and
a fix-efficacy probe result: 104 fixes that cure their own falsifier had mean
sk = 0.950140 and 31 that do not had mean sk = 0.950206, the FAILING ones scoring
marginally higher, with identical medians at 0.978200. Mann-Whitney p = 0.678,
Welch t p = 0.992, Kolmogorov-Smirnov p = 0.852 -- 3 tests, none rejecting, plus a
seeded 20,000-resample permutation test at p = 0.627. **31 of 31 fixes measured
NOT to cure their own falsifier were admitted**, Wilson [88.9745%, 100.0000%].

THE INSTRUMENT ALREADY EXISTED. `bench/fix_efficacy.py`'s probe applies the fix to
a disposable copy and re-runs the finding's OWN falsifier against it, which is
exactly the comparison line 377 requires. It was "contributory, never gating" and
its only consumer was a model-facing feedback line. The repair wires the
measurement the project already takes into the number the appendix says it is.

WHY THESE TESTS CALL RATHER THAN READ. A test asserting on the SOURCE TEXT of the
scorer would assert only that the scorer describes itself consistently, and this
defect was 2 modules describing themselves correctly and disagreeing with each
other. 5 of the 8 tests below fail against the parent commit.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[1]
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import reference_runner_v3 as R  # noqa: E402
from fix_efficacy import (  # noqa: E402
    FIX_CURES,
    FIX_INEFFECTIVE,
    INDETERMINATE,
    NO_BASELINE,
    NO_FALSIFIER,
    NO_FIX,
    NOT_INTERCEPTED,
)

TARGET = "bench/_sk_efficacy_probe_target.py"
SOURCE = 'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
GOOD_FIX = (
    "<<<< SEARCH\n"
    'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
    "====\n"
    'def divide(a, b):\n    """Guarded."""\n    if b == 0:\n'
    '        raise ValueError("b must be non-zero")\n    return a / b\n'
    ">>>> REPLACE"
)
UNPARSEABLE_FIX = (
    "<<<< SEARCH\n"
    'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
    "====\n"
    'def divide(a, b:\n    """Unbalanced paren."""\n    return a / b\n'
    ">>>> REPLACE"
)


@pytest.fixture(scope="module")
def baseline():
    return R._capture_baseline(SOURCE, source_path=TARGET)


def _score(baseline, outcome=None, fix=GOOD_FIX):
    return R.compute_sk(
        fix, SOURCE, TARGET, baseline=baseline, fix_efficacy_outcome=outcome
    )


def test_a_fix_that_does_not_cure_its_falsifier_scores_below_one_that_does(baseline):
    """The separation the archive did not have. RED against the parent."""
    cures = _score(baseline, FIX_CURES)
    fails = _score(baseline, FIX_INEFFECTIVE)
    assert cures.sk > fails.sk, (
        "S_k gives a fix measured NOT to cure its own falsifier a score no lower "
        f"than one that does: {cures.sk} vs {fails.sk}. That is the defect."
    )
    assert cures.gate_details["e1_efficacy"]["score"] == 1.0
    assert fails.gate_details["e1_efficacy"]["score"] == 0.0


def test_the_separation_is_the_gate_weight_and_not_an_accident(baseline):
    """The gap must be the weight's share of E, recomputed independently."""
    cures = _score(baseline, FIX_CURES)
    fails = _score(baseline, FIX_INEFFECTIVE)
    # e1=2, e2 unavailable (no test_cmd), e3=1, e4=2 -> W = 5
    expected_gap = R.FIX_EFFICACY_GATE_WEIGHT / (
        R.FIX_EFFICACY_GATE_WEIGHT + 1.0 + 2.0
    )
    assert cures.sk - fails.sk == pytest.approx(expected_gap, abs=5e-4), (
        f"gap {cures.sk - fails.sk} does not match the declared weight share "
        f"{expected_gap}"
    )


@pytest.mark.parametrize(
    "outcome",
    [NO_FALSIFIER, INDETERMINATE, NO_BASELINE, NOT_INTERCEPTED, NO_FIX,
     "some unknown string from a future version", None],
    ids=["no_falsifier", "indeterminate", "no_baseline", "not_intercepted",
         "no_applicable_fix", "unknown_string", "none"],
)
def test_a_non_verdict_outcome_is_unavailable_and_never_a_zero(baseline, outcome):
    """An instrument that could not look must not be read as a reading.

    This is the project's `Wolfram: a failed call is NOT a result` rule applied at
    a second site. Scoring 0 here would punish a fix for the probe's silence and
    would push `nu_eff` to its MAXIMUM, fabricating re-injection risk.
    """
    r = _score(baseline, outcome)
    assert r.gate_details["e1_efficacy"]["score"] is None, (
        f"{outcome!r} was read as a verdict"
    )
    unchanged = _score(baseline, None)
    assert r.sk == unchanged.sk


def test_an_unsupplied_outcome_leaves_the_score_exactly_as_it_was(baseline):
    """Backward compatibility, executed: 902 archived verdicts must not move."""
    r = _score(baseline, None)
    assert r.sk == 1.0 and r.tristate == R.SK_ADMISSIBLE
    assert r.gate_details["e1_efficacy"]["score"] is None
    assert "e1_efficacy" in (r.gate_details.get("_unavailable") or [])


def test_the_runner_call_site_actually_passes_the_probe_outcome():
    """THE WIRING, CALLED rather than read.

    A gate wired to nothing is not additive. This drives the real evaluator with
    2 registry entries differing ONLY in their recorded probe outcome and
    requires the scores to differ. Grepping the call site could not establish
    this; a typo in the keyword would still grep green.
    """
    registry = R.FindingRegistry()
    for cid, outcome in (("C-CURES", FIX_CURES), ("C-FAILS", FIX_INEFFECTIVE)):
        registry.entries[cid] = {
            "status": "OPEN",
            "proposed_fix": GOOD_FIX,
            "fix_efficacy": {"outcome": outcome},
            "severity": "critical",
            "model": "SIM-A",
            "round": 0,
        }
    baseline = R._capture_baseline(SOURCE, source_path=TARGET)
    R._evaluate_sk_for_findings(
        registry, SOURCE, TARGET, baseline, round_idx=0, test_cmd=None,
    )
    cures = registry.entries["C-CURES"]["sk_result"]["sk"]
    fails = registry.entries["C-FAILS"]["sk_result"]["sk"]
    assert cures > fails, (
        "the evaluator produced the same score for a fix that cures its own "
        f"falsifier and one that does not ({cures} vs {fails}) -- the outcome is "
        "not reaching compute_sk"
    )


def test_sk_fills_the_appendix_sigma_slot_term_for_term():
    """`R_base = sigma*R_det + (1-sigma)*R_old` is why this gate matters at all.

    Verified symbolically against `compute_rk`'s own arithmetic, so that if the
    resolution phase is ever re-derived the reason for the gate travels with it.
    """
    sympy = pytest.importorskip("sympy")
    R_old, q, sk = sympy.symbols("R_old q sk", nonnegative=True)
    R_det = R_old * (1 - q) / (1 - q * R_old)
    appendix_R_base = sk * R_det + (1 - sk) * R_old
    # compute_rk, executed at concrete points, must agree with the appendix form
    # once re-injection is switched off (nu_b = nu_f = 0 leaves R_k == R_base).
    for r0, qq, ss in ((0.5, 0.3, 1.0), (0.5, 0.3, 0.0), (0.8, 0.6, 0.4)):
        expected = float(appendix_R_base.subs({R_old: r0, q: qq, sk: ss}))
        got = R.compute_rk(r0, qq, ss, nu_b=0.0, nu_f=0.0)
        assert got == pytest.approx(expected, abs=1e-12), (
            f"compute_rk no longer implements the appendix resolution phase at "
            f"(R_old={r0}, q={qq}, sk={ss}): {got} vs {expected}"
        )


def test_a_rejection_names_the_gate_that_failed_and_why(baseline):
    """RED against the parent: the message could never name a gate.

    Every gate is recorded as a dict, and `v == 0` on a dict is False, so the
    failed-gate list was ALWAYS empty and every rejection read "hard gate
    returned 0" while the details held the exact parse error.
    """
    r = R.compute_sk(UNPARSEABLE_FIX, SOURCE, TARGET, baseline=baseline)
    assert r.tristate == R.SK_REJECTED
    entry = {"sk_result": {"tristate": r.tristate, "gate_details": r.gate_details}}
    text = " ".join(R._rejection_lines(entry))
    assert "g1_ast" in text or "g2_compile" in text, text
    assert "never closed" in text, (
        "the rejection discarded the only part a model could act on: " + text
    )


def test_a_probe_verdict_alone_can_carry_a_terminal_status_and_that_is_deliberate():
    """A BEHAVIOUR CHANGE, PINNED SO IT IS A DECISION RATHER THAN AN ACCIDENT.

    When `e2`, `e3` and `e4` are all unavailable, `compute_sk` previously had no
    effect gate at all and returned ESCALATE, whose message reads *"the evidence
    gates went silent"*. With `e1_efficacy` available that sentence is false:
    an instrument DID speak. So a probe verdict alone now produces a terminal
    status -- ADMISSIBLE on FIX_CURES, REJECTED on FIX_INEFFECTIVE.

    WHY THIS DOES NOT BREAK T04, the rule that *"an equipment failure can no
    longer write a terminal status"*. FIX_INEFFECTIVE is a VERDICT by
    `fix_efficacy.ProbeResult.is_verdict`'s own definition, and every one of the
    5 equipment outcomes returns None from the gate and is excluded from the
    mean. The rule is respected by construction rather than by care.

    MEASURED REACH: 0 of 1,247 archived records, Wilson [0.0000%, 0.3071%]. All
    154 archived ESCALATE records have every effect gate silent and NONE carries
    a probe verdict, so this reclassifies nothing that already exists. It is a
    latent path, and it is pinned here rather than left to be discovered.
    """
    source = 'def divide(a, b):\n    """BUG."""\n    return a / b\n'
    fix = (
        "<<<< SEARCH\n"
        'def divide(a, b):\n    """BUG."""\n    return a / b\n'
        "====\n"
        'def divide(a, b):\n    """Guarded."""\n    if b == 0:\n'
        '        raise ValueError("b")\n    return a / b\n'
        ">>>> REPLACE"
    )
    # baseline=None and no test_cmd: e2, e3 and e4 are all unavailable.
    silent = R.compute_sk(fix, source, TARGET, baseline=None)
    assert silent.tristate == R.SK_ESCALATE, (
        "with no gate at all the fail-safe must still be ESCALATE"
    )
    cures = R.compute_sk(
        fix, source, TARGET, baseline=None, fix_efficacy_outcome=FIX_CURES)
    fails = R.compute_sk(
        fix, source, TARGET, baseline=None, fix_efficacy_outcome=FIX_INEFFECTIVE)
    assert cures.tristate == R.SK_ADMISSIBLE and cures.sk == 1.0
    assert fails.tristate == R.SK_REJECTED and fails.sk == 0.0
