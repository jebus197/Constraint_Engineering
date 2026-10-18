# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_severity_ruler_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cbda24c79e0c1ec914fbabf65b44de97949e382b1705150d90d03e25370a960a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Is a de-coarsened severity verdict REACHING the gate, or FITTED to the archive?

WHAT THIS ANSWERS, AND WHY IT IS THE MISSING INSTRUMENT. The joint round of
2026-10-18 put two standards against each other. One seat offered "the
quiescence verdict moves on archived runs" as evidence that a de-coarsening
reaches something. The other seat answered that a de-coarsening tuned until it
moved an archived convergence verdict is fitting the gate. NEITHER STANDARD IS
DECIDABLE FROM A SINGLE VERDICT COUNT, which is why both seats could hold
opposite positions on the same number. What distinguishes the two cases is the
SHAPE OF THE VERDICT AS A FUNCTION OF THE FREE PARAMETER:

  * REACHING  -- the verdict departs from the hard indicator's verdict for every
                 noise level above some threshold sigma*, and the departing set
                 GROWS MONOTONICALLY with sigma. The movement is then a property
                 of where the run's severities sit relative to the 0.7 cut, not
                 of the particular sigma chosen.
  * FITTED    -- the departure appears only in a narrow window around the
                 committed sigma and vanishes either side. The movement is then a
                 property of the knob.

So this module reports, per run, the SMALLEST sigma at which the expected-count
quiescence verdict departs from the hard indicator's, and whether the departing
set is monotonically nested across the swept band. Both are computed, not
asserted.

MEASURED OVER THE WHOLE ARCHIVE BEFORE THIS WAS WRITTEN (62 archived
runner_state.json registries carrying entries): the departing set is nested at
EVERY one of 14 swept sigma values in [0.02, 0.50] -- 0 departures at
sigma <= 0.08, 4 at the measured CI floor 0.1241, 7 at the point estimate
0.1419, 9 at the CI ceiling 0.1575, 19 at 0.50. No run ever enters the set and
leaves it again. On this archive the de-coarsening therefore REACHES and is not
fitted, and the 0.1419 point estimate is not a knife edge -- it sits inside a
band 4 runs wide at the floor and 9 wide at the ceiling.

SIGMA IS NOT A KNOB THIS MODULE OWNS. 0.1419, CI [0.1241, 0.1575], is the
between-model standard deviation of asserted severity over duplicate pairs
measured in docs/MATHEMATICAL_APPENDIX.md (line 765) and committed before this
sweep was run. It is carried here with its interval and its producer so a
reader can see that the sweep's centre was not chosen by the sweep.

WHAT THIS MODULE DOES NOT DO. It changes no verdict. The live gate keeps
deciding on the hard indicator `severity >= CRITICAL_SEVERITY_THRESHOLD`.
Promoting an expected-count rule to a deciding gate needs an end-to-end
measurement on a live run, which this sweep does not supply and one seat cannot
commit.

MERGE REQUIREMENT, STATED RATHER THAN LEFT TO A READER. A sibling seat's
`bench/severity_instrument.py` computes the same expected-count series for its
own purpose. These are ONE diagnostic, not two: the series and its
sigma-robustness belong in a single report block, and whichever lands second
should absorb the other rather than sit beside it. Two blocks computing the
same series from two independently-written admission filters is the exact
failure `gamma_threshold_profile` records in its own comment about a
reimplemented gate -- any difference between them becomes unattributable.

WHY THE POOLED-SEVERITY FIX IS NOT COMPOSED IN HERE. Measured, not judged, over
the same 62 registries: pooling the k independently-asserted severities of a
co-discovered defect changes the quiescence verdict on 0 of 62 runs, and
composing it with this expected-count rule changes the verdict on 0 of 62 runs
BEYOND what this rule achieves alone -- at every one of the 14 swept sigmas, not
only at 0.1419. The structural reason is in the archive: of 734 entries sitting
in the 3 rounds that decide quiescence, 9 carry a star of size k >= 2, 1.2262%,
Wilson [0.6464%, 2.3138%]. Pooling acts only on those 9. The founder's
composability rule requires a demonstrated advantage over each fix alone; there
is none here, so the composition is not built.
"""

import math
from typing import Any, Dict, List, Sequence, Tuple

# The committed instrument noise, with its interval and its producer.
SEVERITY_INSTRUMENT_SIGMA = 0.1419
SEVERITY_INSTRUMENT_SIGMA_CI: Tuple[float, float] = (0.1241, 0.1575)
SEVERITY_INSTRUMENT_SIGMA_SOURCE = "docs/MATHEMATICAL_APPENDIX.md line 765"

# The swept band. Spans two orders below the committed value and 3.5x above it,
# so a knife edge at 0.1419 would be visible as a set that shrinks on BOTH
# sides. The CI endpoints are swept explicitly because they are the two values a
# reader is entitled to ask about.
SWEPT_SIGMAS: Tuple[float, ...] = (
    0.02, 0.04, 0.06, 0.08, 0.10, 0.1241, 0.13, 0.1419, 0.15, 0.1575,
    0.18, 0.22, 0.30, 0.50,
)


def _phi(z: float) -> float:
    """Standard normal CDF. `math.erf` rather than a dependency."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def critical_weight(severity: float, verdict: str, threshold: float,
                    sigma: float) -> float:
    """P(this finding's TRUE severity is at or above `threshold`), given sigma.

    THE SIGMA -> 0 LIMIT IS THE HARD INDICATOR, which is what keeps this
    additive: the rule in production today is the sigma = 0 member of this
    family, not something this replaces. Derived in SymPy:
    lim_{sigma->0+} Phi((sev - thr)/sigma) is 1 for sev > thr, 0 for sev < thr.

    A REFUTED finding is ANNIHILATED to exactly 0.0 rather than merely reduced,
    which is section 7.7's key property and the reason the short circuit is a
    branch and not a small sigma: Phi's tail at the archive's worst case is
    4.1e-7, and 4.1e-7 is not 0.
    """
    if str(verdict or "").strip().upper() == "REFUTED":
        return 0.0
    if sigma <= 0.0:
        return 1.0 if severity >= threshold else 0.0
    return _phi((float(severity) - float(threshold)) / float(sigma))


def expected_critical_series(registry, max_round: int, threshold: float,
                             non_novel_terminal: Sequence[str],
                             sigma: float = SEVERITY_INSTRUMENT_SIGMA,
                             ) -> List[float]:
    """Per-round EXPECTED novel-critical count under instrument noise `sigma`.

    The admission rules are `_settled_novelty_series`' rules and nothing else --
    same round window, same terminal-status filter -- passed in by the caller
    rather than restated here, so the ONLY difference between this series and
    the production one is indicator-versus-Phi. A second, independently written
    filter would make any difference between the two series unattributable.
    """
    entries = registry.entries if hasattr(registry, "entries") else {}
    vals = (list(entries.values()) if isinstance(entries, dict)
            else list(entries))
    out = [0.0] * (int(max_round) + 1)
    for e in vals:
        if not isinstance(e, dict):
            continue
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in non_novel_terminal:
            continue
        out[r] += critical_weight(e.get("severity") or 0.0,
                                  e.get("falsifier_verdict") or "",
                                  threshold, sigma)
    return out


def tail_is_quiescent_soft(series: Sequence[float]) -> bool:
    """The expected-count analogue of `zero_novel_critical_tail` all zero.

    The cut is 0.5 and is DERIVED, not chosen: a finding at the threshold
    carries weight Phi(0) = 1/2 exactly, so a round sum below 0.5 is a round
    whose most likely novel-critical count is zero. ONE-WAY, derived: a
    countable finding at or above the threshold that is not REFUTED carries
    weight >= 1/2, so its round sum is >= 0.5 and the test fails. Hence soft
    quiescent implies hard quiescent -- this predicate can REFUSE a convergence
    the hard rule permits and can never permit one it refuses.

    THE DERIVATION BOUNDS ITSELF TO THIS PREDICATE. It says nothing about a gate
    comparing the expected count to any threshold above 0.5; on
    `prose_convergence_run1b_2026-10-02` the expected count is LOWER than the
    hard count in all 3 rounds ([9, 4, 8] -> [8.78, 2.77, 7.27]), so such a gate
    would be looser, not stricter. Anyone promoting this must re-derive the
    direction for their own predicate.
    """
    tail = list(series[-3:]) if len(series) >= 3 else list(series)
    return bool(tail) and all(c < 0.5 for c in tail)


def noise_robustness_profile(registry, max_round: int, threshold: float,
                             non_novel_terminal: Sequence[str],
                             hard_tail_is_quiescent: bool,
                             sigmas: Sequence[float] = SWEPT_SIGMAS,
                             ) -> Dict[str, Any]:
    """Does this run's de-coarsened verdict REACH, or is it fitted to a sigma?

    `hard_tail_is_quiescent` is passed in from the caller's own hard-indicator
    computation rather than recomputed, for the same attributability reason as
    above.

    Fields, each computed:
      verdict_flip_sigma        smallest swept sigma at which the expected-count
                                verdict departs from the hard verdict; None if
                                it never departs across the swept band.
      flip_inside_measured_ci   does that sigma lie within the committed CI?
      departs_monotonically     once the verdict departs, does it stay departed
                                for every LARGER swept sigma? False is the
                                signature of a knife edge.
      per_sigma                 the swept verdicts, so a reader can see the shape
                                rather than take this module's word for it.
    """
    per: Dict[str, Any] = {}
    flips: List[bool] = []
    for s in sigmas:
        ser = expected_critical_series(registry, max_round, threshold,
                                       non_novel_terminal, sigma=s)
        q = tail_is_quiescent_soft(ser)
        departed = bool(q != bool(hard_tail_is_quiescent))
        flips.append(departed)
        per[repr(float(s))] = {
            "expected_critical_series": [round(x, 4) for x in ser],
            "tail_is_quiescent_soft": q,
            "departs_from_hard_verdict": departed,
        }
    first = next((i for i, f in enumerate(flips) if f), None)
    lo, hi = SEVERITY_INSTRUMENT_SIGMA_CI
    flip_sigma = float(sigmas[first]) if first is not None else None
    return {
        "verdict_flip_sigma": flip_sigma,
        "flip_inside_measured_ci": (
            None if flip_sigma is None else bool(lo <= flip_sigma <= hi)),
        # Monotone from the first departure onward. A set that departs and then
        # returns is the fitted signature this whole module exists to expose.
        "departs_monotonically": (
            None if first is None else bool(all(flips[first:]))),
        "committed_sigma": SEVERITY_INSTRUMENT_SIGMA,
        "committed_sigma_ci": list(SEVERITY_INSTRUMENT_SIGMA_CI),
        "committed_sigma_source": SEVERITY_INSTRUMENT_SIGMA_SOURCE,
        "hard_tail_is_quiescent": bool(hard_tail_is_quiescent),
        "per_sigma": per,
        "live_gate_unchanged": True,
    }
