# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_severity_ruler_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6eb956fb33b2fe3481bf092c5c987897bf0a224b6188e6e9b344ae0b5a996d8a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The severity ruler's instrument-noise channel: expected critical counts.

Joint round 2026-10-18. This module is the reconstruction of cc2's blind-round
fix, rebuilt after sandbox teardown and adopted by the fable seat on a
MEASUREMENT, not by deference: over 62 archived catalogues
(`scripts/do_the_two_rulers_compose_2026-10-18.py`),

  * this smoothing alone moves the production tail quiescence verdict on 7
    runs, every one in the STRICT direction (refusing a convergence the hard
    indicator permits; one-way property proved below and violated 0 times);
  * the star-median pooling ruler (fable's blind fix) moves it on 0 of 62;
  * the COMPOSITION Phi((star_median - thr) / (sigma * c_k)) moves it on 0 of
    62 beyond this fix alone, AND loses the one-way guarantee: at the decision
    line it disagrees with this ruler on exactly 14 archived entries, all 14
    falsifier-CONFIRMED criticals pulled BELOW 0.5 by co-discoverers' lower
    asserted numbers (leg3 C0006: CONFIRMED at 0.9, star [0.9, 0.45, 0.45],
    composed weight 0.0043). That is votes overriding a tool.

Under the founder's composability ruling (2026-10-02) the composition is
therefore REFUSED: no measurement shows it dominating this fix alone, and the
measurement that exists shows it strictly worse on a named property (one-way
conservatism). The pooled ruler is not promoted either (0/62 reach on the
quiescence channel).

THE RULER ITSELF. `_settled_novelty_series` decides criticality with the hard
indicator 1[severity >= 0.7] on a quantity whose per-assignment noise is
measured at sigma = 0.1419, bootstrap 95% CI [0.1241, 0.1575], from 273
duplicate pairs (docs/MATHEMATICAL_APPENDIX.md, "the instrument's noise
floor"). This module reports the indicator's EXPECTATION under that noise:

    w(f) = Phi((severity - threshold) / sigma),   REFUTED -> exactly 0.0.

Properties, each executed by the test file
`bench/tests/test_the_two_rulers_compose_2026-10-18.py`:

  * Phi(threshold) = 1/2 exactly: a finding on the line is worth a coin toss.
  * sigma -> 0 recovers the production ruler VALUE-FOR-VALUE on every
    archived catalogue (the hard indicator is the sigma=0 member of this
    family), which is what discharges the additive standard.
  * ONE-WAY: a countable entry with severity >= threshold and no REFUTED
    verdict has w >= 1/2, so a quiescent soft tail implies a quiescent hard
    tail. The smoothing can refuse a convergence the hard rule permits and
    can never permit one it refuses.

DIAGNOSTIC ONLY. The live gate keeps deciding on the hard indicator; this is
written into the report by `gamma_threshold_profile` so the reach measurement
(the 7 strict flips) can be taken on live runs before any promotion, which is
a founder decision. Promotion of ANY rule that reads these weights must
re-derive the one-way direction for its own predicate: the proof covers the
`< 0.5` quiescence test and nothing else (cc2's refutation condition 3,
blind round 2026-10-18).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

#: Per-assignment severity noise, measured from 273 duplicate pairs in which 2
#: different models independently scored the same defect. Producer:
#: docs/MATHEMATICAL_APPENDIX.md ("the instrument's noise floor"), bootstrap
#: 95% CI [0.1241, 0.1575].
SEVERITY_INSTRUMENT_SIGMA = 0.1419

#: Mirrors of the production constants. DELIBERATE mirror, not an import: a
#: module-level import of reference_runner_v3 from one of its own siblings
#: would be circular once the runner imports this module. The test file
#: asserts both mirrors equal the production values, and asserts the sigma->0
#: series equals `_settled_novelty_series` value-for-value on every archived
#: catalogue, so a drift in either constant fails loudly.
CRITICAL_SEVERITY_THRESHOLD_MIRROR = 0.7
NON_NOVEL_TERMINAL_STATUSES_MIRROR = frozenset(
    {"MERGED", "DUPLICATE", "UNCONFIRMED", "REFUTED"})


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def critical_weight(entry: dict,
                    sigma: float = SEVERITY_INSTRUMENT_SIGMA,
                    threshold: float = CRITICAL_SEVERITY_THRESHOLD_MIRROR,
                    ) -> float:
    """Expected value of the critical indicator under instrument noise.

    REFUTED short-circuits to exactly 0.0 -- the annihilation term of
    `spec_verification_factor`, held exactly rather than approximated: a
    disproved finding is worth nothing, not Phi's 4.1e-7 tail.
    """
    if str(entry.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
        return 0.0
    sev = float(entry.get("severity") or 0.0)
    if sigma <= 0.0:  # the sigma->0 member IS the production indicator
        return 1.0 if sev >= threshold else 0.0
    return _phi((sev - threshold) / sigma)


def expected_critical_series(registry, max_round: int,
                             sigma: float = SEVERITY_INSTRUMENT_SIGMA,
                             ) -> List[float]:
    """Per-round EXPECTED novel-critical counts from the settled registry.

    The population filter deliberately mirrors `_settled_novelty_series`
    admission (open_since_round window, non-novel terminal statuses), so the
    ONLY difference between the two series is indicator-versus-Phi. A second,
    independently-written filter would make any difference unattributable.
    """
    entries = registry.entries if hasattr(registry, "entries") else {}
    vals = entries.values() if isinstance(entries, dict) else entries
    s = [0.0] * (max_round + 1)
    for e in vals:
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in NON_NOVEL_TERMINAL_STATUSES_MIRROR:
            continue
        s[r] += critical_weight(e, sigma=sigma)
    return s


def tail_is_quiescent_soft(series: List[float]) -> bool:
    """all(w < 0.5) over the last-3 tail, the same window the production
    `tail_is_quiescent` reads. 0.5 = Phi(0): the most likely critical count
    in a quiet round is zero. ONE-WAY with respect to the hard tail, by the
    module docstring's derivation."""
    tail = series[-3:] if len(series) >= 3 else list(series)
    return bool(tail) and all(w < 0.5 for w in tail)


def instrument_noise_profile(registry, max_round: int) -> Dict[str, Any]:
    """The report block: both rulers' series, tails, gammas, and whether the
    quiescence verdict differs. Diagnostic; changes no verdict."""
    import reference_runner_v3 as rr  # call-time import, no circularity
    _, hard = rr._settled_novelty_series(registry, max_round)
    soft = expected_critical_series(registry, max_round)
    hard_tail = hard[-3:] if len(hard) >= 3 else list(hard)
    soft_tail = soft[-3:] if len(soft) >= 3 else list(soft)
    q_hard = bool(hard_tail) and all(c == 0 for c in hard_tail)
    q_soft = tail_is_quiescent_soft(soft)
    return {
        "sigma": SEVERITY_INSTRUMENT_SIGMA,
        "sigma_ci95": [0.1241, 0.1575],
        "sigma_producer": "docs/MATHEMATICAL_APPENDIX.md, 273 duplicate pairs",
        "expected_critical_series": [round(w, 4) for w in soft],
        "soft_tail": [round(w, 4) for w in soft_tail],
        "tail_is_quiescent_soft": q_soft,
        "tail_is_quiescent_hard": q_hard,
        "quiescence_verdict_differs": q_soft != q_hard,
        "gamma_soft": round(rr._estimate_gamma(soft), 4),
        "gamma_hard": round(rr._estimate_gamma(hard), 4),
        "one_way": "soft-quiescent implies hard-quiescent; see module docstring",
        "deciding": False,
    }
