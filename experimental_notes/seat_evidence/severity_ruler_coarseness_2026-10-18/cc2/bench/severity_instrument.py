# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_ruler_coarseness_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 079c8f663bd5e94846eddc3e3f2b92f53d14337e3153eea6ab5e4dad4bc88359
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The instrument-noise half of the severity ruler (C4, free panel 2026-10-18).

WHAT THIS ADDS, AND WHY THE EXISTING RULER CANNOT ADD IT. The gate decides
criticality with the indicator `1[severity >= CRITICAL_SEVERITY_THRESHOLD]`.
`docs/MATHEMATICAL_APPENDIX.md` line 765 measures the per-assignment noise in
that severity number at **sigma = 0.1419**, bootstrap 95% CI [0.1241, 0.1575],
from 273 duplicate pairs the runner itself ruled identical, against an audit
band 0.09 wide; 82 of 273 identical defects, 30.04%, Wilson [24.9%, 35.7%],
landed on opposite sides of 0.7. An indicator applied to a quantity with that
much noise discards exactly the information that decides the gate: it rounds a
coin toss at 0.70 to a certainty, and it rounds a 0.69 to a zero.

`effective_severity` does NOT address this, and the direction in which it fails
to is worth stating precisely because it is the opposite of the intuitive one.
With `_SEVERITY_SPEC["on"]` True, `effective_severity = asserted * V` with
V in {0.0, 0.5, 1.0}; since sup(asserted) = 1 and 1 * 0.5 = 0.5 < 0.7, the
predicate `effective_severity >= 0.7` is IDENTICALLY
`V == 1.0 and asserted >= 0.7`. Proved by z3 (`Not(equivalence)` is unsat) and
independently by Wolfram Language (`Reduce[ForAll[{a}, 0<=a<=1, a/2 < 7/10]]`
returns True). So the specification does not carry the asserted number's
ordering through to the gate with its noise intact -- it moves the ENTIRE
unresolved population to the non-critical side and the ordering within that
population stops reaching the decision at all. Section 7.7's own caution 1
records the same collapse algebraically.

THE REPAIR, AND IT IS ONE FORMULA. Replace the indicator with its expectation
under the measured noise:

    w(f) = P(true severity >= theta | asserted)  =  Phi((sev - theta) / sigma)

and report the per-round sum of `w` as the EXPECTED novel-critical count. Four
properties, each derived rather than asserted (SymPy, re-checked in Wolfram
Language):

  1. `Phi(theta) = 1/2` EXACTLY, for every sigma > 0. A finding sitting on the
     line contributes half a critical, which is what a coin toss is worth.
  2. `w` is strictly increasing in severity (derivative
     `sqrt(2) exp(-(sev-theta)^2 / 2 sigma^2) / (2 sqrt(pi) sigma) > 0`), so the
     ordering the asserted number carries is preserved, not flattened.
  3. **The current ruler is the sigma -> 0+ member of this family.**
     `lim_{sigma->0+} Phi((sev-theta)/sigma)` is 1 for sev > theta and 0 for
     sev < theta -- the indicator exactly. So this NESTS the live ruler rather
     than replacing it, which is what makes it additive: `sigma=0.0` reproduces
     the existing series value-for-value, and
     `bench/tests/test_the_severity_ruler_instrument_noise_2026-10-18.py`
     executes that equality over every archived catalogue rather than asserting it.
  4. Section 7.7's KEY PROPERTY is preserved EXACTLY, not approximately. A
     REFUTED finding is annihilated by an explicit short-circuit to 0.0, because
     `Phi((0 - 0.7)/0.1419) = 4.1e-7` is small but NOT zero, and "nearly
     annihilated" is not the appendix's property.

DIRECTION OF EFFECT ON CONVERGENCE, WHICH THE BRIEF REQUIRES BE STATED. The
soft quiescence test `all(w_r < 0.5)` is ONE-WAY: it can refuse a convergence
the hard rule permits, and it can NEVER permit one the hard rule refuses.
Proof: if any countable finding has `sev >= theta` and is not REFUTED then
`w >= Phi(0) = 1/2` by properties 1-2, so the round sum is `>= 0.5` and the
soft test fails. Hence `soft_quiescent => hard_quiescent`. Measured over the 19
archived catalogues with at least 3 rounds: the two verdicts differ on 5,
26.3158%, Wilson [11.4817%, 48.6676%], and ALL 5 differ in the strict
direction; 0 of 19 became easier, Wilson [0.0%, 16.8151%]. So the instrument
noise does not merely exist, it changes the quiescence picture on about a
quarter of this project's own runs, and only ever toward more work.

SECOND, INDEPENDENT BENEFIT -- A GAMMA THAT IS DEFINED WHERE THE HARD ONE IS
NOT. `_estimate_gamma` returns the 0.0 sentinel when the critical series sums
to zero, and 0.0 sits in the worst `GAMMA_BANDS` interpretation ("Gamma
disagrees with state closure -- recommend HIL audit"). 4 of the 19 archived
runs have an identically-zero hard critical series and therefore an UNDEFINED
gamma_critical reported as 0.0; the soft series is non-degenerate on all 4 and
yields 0.4769, 0.4757, 0.6819 and 0.7369. That is the brief's "across a broad
range of scenarios and not only the one it was tuned on": the hard ruler has no
resolution at all in the regime where no finding crosses 0.7, which is a common
regime, and this instrument does.

DIAGNOSTIC ONLY AT THIS COMMIT, STATED PLAINLY. Nothing here changes a verdict.
`gamma_threshold_profile` calls it and the result is written into every report,
so it is wired to a caller and executed by a test -- but promoting it to a
DECIDING gate needs an end-to-end measurement on a live run, which one panel
seat cannot commit. The 5 flips above are the evidence for taking that step,
not the step itself.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Sequence

#: The severity instrument's measured per-assignment noise.
#: `docs/MATHEMATICAL_APPENDIX.md` line 765: sigma = 0.1419, bootstrap 95% CI
#: [0.1241, 0.1575], from 273 duplicate pairs in which 2 different models
#: independently scored the same defect. NOT a tuned constant -- a measurement,
#: and the CI travels with it so a consumer can see its width.
SEVERITY_INSTRUMENT_SIGMA = 0.1419
SEVERITY_INSTRUMENT_SIGMA_CI = (0.1241, 0.1575)

#: Below this, `critical_weight` returns the exact indicator instead of Phi.
#: Guards the sigma -> 0+ limit from a division by zero AND makes the nesting
#: property (3) executable at sigma = 0.0 rather than merely approached.
_SIGMA_FLOOR = 1e-12


def critical_weight(
    entry: Dict[str, Any],
    threshold: float,
    sigma: float = SEVERITY_INSTRUMENT_SIGMA,
) -> float:
    """P(true severity >= threshold | asserted severity), under measured noise.

    Returns 0.0 EXACTLY for a REFUTED falsifier verdict -- section 7.7's key
    property, applied by short-circuit rather than left to Phi's tail, which is
    4.1e-7 at severity 0 and not 0.

    At `sigma <= _SIGMA_FLOOR` returns the live ruler's own indicator, so the
    existing behaviour is the sigma = 0 member of this family and not a separate
    code path that could drift from it.
    """
    if str(entry.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
        return 0.0
    sev = float(entry.get("severity") or 0.0)
    if sigma <= _SIGMA_FLOOR:
        return 1.0 if sev >= threshold else 0.0
    return 0.5 * (1.0 + math.erf((sev - threshold) / (sigma * math.sqrt(2.0))))


def expected_critical_series(
    entries: Iterable[Dict[str, Any]],
    max_round: int,
    non_novel_statuses: Iterable[str],
    threshold: float,
    sigma: float = SEVERITY_INSTRUMENT_SIGMA,
) -> List[float]:
    """Per-round EXPECTED novel-critical count, same population as the hard one.

    Deliberately mirrors `_settled_novelty_series`' admission rules exactly --
    `open_since_round` in range, status not in the non-novel terminal set -- so
    that the only difference between the two series is the indicator-versus-Phi
    substitution. A second, independently-written population filter would make
    any difference between the series unattributable.
    """
    skip = {str(s) for s in non_novel_statuses}
    out = [0.0] * (int(max_round) + 1)
    for e in entries:
        if not isinstance(e, dict):
            continue
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if str(e.get("status")) in skip:
            continue
        out[int(r)] += critical_weight(e, threshold, sigma)
    return out


def tail_is_quiescent_soft(tail: Sequence[float]) -> bool:
    """Fewer than one EXPECTED novel critical per round, across the tail.

    The cut is 0.5 and it is DERIVED, not chosen: 0.5 is the rounding boundary
    of a count, so `< 0.5` is exactly "the most likely number of novel criticals
    this round is zero". It introduces no tunable parameter, which matters
    because a tunable cut here would be a second hidden gate.

    One-way by construction -- see the module docstring's proof: a single
    countable finding at or above the threshold forces the sum to >= 0.5, so
    this never permits a convergence the hard rule refuses.
    """
    return bool(tail) and all(float(c) < 0.5 for c in tail)


def instrument_noise_profile(
    entries: Iterable[Dict[str, Any]],
    max_round: int,
    non_novel_statuses: Iterable[str],
    threshold: float,
    estimate_gamma,
    min_rounds: int = 3,
    sigma: float = SEVERITY_INSTRUMENT_SIGMA,
) -> Dict[str, Any]:
    """The reported block: soft series, soft gamma, soft tail, and the delta.

    `estimate_gamma` is passed IN rather than imported, so this reads the SAME
    estimator the live gate uses instead of a second copy that could disagree
    with it -- the failure `gamma_threshold_profile` records in its own comment
    about a reimplemented gate.
    """
    vals = list(entries)
    soft = expected_critical_series(
        vals, max_round, non_novel_statuses, threshold, sigma)
    hard = expected_critical_series(
        vals, max_round, non_novel_statuses, threshold, 0.0)
    tail_n = 3
    soft_tail = soft[-tail_n:] if len(soft) >= tail_n else list(soft)
    hard_tail = hard[-tail_n:] if len(hard) >= tail_n else list(hard)
    soft_quiet = tail_is_quiescent_soft(soft_tail)
    hard_quiet = bool(hard_tail) and all(c == 0 for c in hard_tail)
    return {
        "sigma": sigma,
        "sigma_ci": list(SEVERITY_INSTRUMENT_SIGMA_CI),
        "sigma_basis": ("docs/MATHEMATICAL_APPENDIX.md line 765 -- 273 duplicate "
                        "pairs scored by 2 different models, bootstrap 95% CI"),
        "expected_critical_series": [round(c, 4) for c in soft],
        "hard_critical_series_at_sigma_zero": [int(c) for c in hard],
        "gamma_critical_soft": round(float(estimate_gamma(soft, min_rounds)), 4),
        "gamma_critical_hard": round(float(estimate_gamma(
            [int(c) for c in hard], min_rounds)), 4),
        "expected_critical_tail": [round(c, 4) for c in soft_tail],
        "tail_is_quiescent_soft": soft_quiet,
        "tail_is_quiescent_hard": hard_quiet,
        # The whole point, in one field: did the instrument's own noise change
        # the quiescence picture the gate reads?
        "quiescence_verdict_differs": bool(soft_quiet != hard_quiet),
        "direction": ("soft is STRICTER (refuses a tail the hard rule calls quiet)"
                      if hard_quiet and not soft_quiet else
                      "soft agrees with hard" if soft_quiet == hard_quiet else
                      "IMPOSSIBLE: soft permitted what hard refused -- the "
                      "one-way property is violated, see module docstring"),
        "IS_DIAGNOSTIC": ("Changes no verdict at this commit. The live gate still "
                          "decides on the hard indicator at "
                          "CRITICAL_SEVERITY_THRESHOLD."),
    }
