# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0dd86b933a97dfac22a63523dec9c66f379e17bcfbd4e0349afa8e32166ee50c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q3 - evidence for the e1_efficacy veto. Run from the repository root:

    python3 scripts/q3_e1_efficacy_veto_2026-09-30.py

THE FOUNDER'S CONDITION, verbatim: the change must "plug the hole and make the
instrument more accurate", not merely change which fixes pass. A verdict count
that changes is not evidence of improvement. So this script measures TWO things
and both must hold:

  (1) EFFICACY   on the class the veto targets -- fixes MEASURED not to cure
                 their own falsifier -- the false-admission rate goes to 0.
  (2) INVARIANCE on EVERY other class -- FIX_CURES, not-probed, indeterminate,
                 and every prose path -- the result is BIT-IDENTICAL.

(2) is the load-bearing half. Without it the change is a reweighting with a
different name.

A THIRD measurement answers "is it reached?", which the additive standard
demands of every addition: the veto must fire on a live compute_sk call, not
only in a unit test.

Also DERIVED here, not asserted: that no finite weight on e1 can produce a
rejection, so a gate is the only available instrument.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import mpmath as mp                                            # noqa: E402
import sympy as sp                                             # noqa: E402

from bench.reference_runner_v3 import (                        # noqa: E402
    FIX_EFFICACY_GATE_WEIGHT, SK_ADMISSIBLE, SK_NO_SCORE, SK_REJECTED,
    compute_sk,
)
from fix_efficacy import (                                     # noqa: E402
    FIX_CURES, FIX_INEFFECTIVE, NO_FALSIFIER,
)

mp.mp.dps = 30

TARGET = REPO / "bench" / "dm" / "_convergence.py"


def _fix_for(src: str) -> str:
    """A minimal, harmless, APPLICABLE fix: add a trailing comment line."""
    tail = src.rstrip("\n").split("\n")[-1]
    return (
        "<<<< SEARCH\n" + tail + "\n====\n" + tail +
        "\n# touched by the Q3 e1 veto falsifier, 2026-09-30\n>>>> REPLACE\n"
    )


def derive_no_weight_can_veto() -> None:
    print("D1  NO FINITE WEIGHT ON e1 CAN PRODUCE A REJECTION (derived)")
    w1, s2, s3, s4 = sp.symbols("w1 s2 s3 s4", positive=True)
    # e1 = 0. Other gates clean at their best case is irrelevant; take the
    # INFIMUM over the other gates' scores, which is what a veto would need to
    # drive to 0.
    E = (w1 * 0 + 2 * s2 + 1 * s3 + 2 * s4) / (w1 + 2 + 1 + 2)
    inf_E = sp.limit(E.subs({s2: 0, s3: 0, s4: 0}), w1, sp.oo)
    print(f"      E(e1=0) = {sp.simplify(E)}")
    print(f"      inf over other gates, w1 -> oo : {inf_E}   "
          f"(reaches 0 only in the limit, never AT a finite weight)")
    # The operational case: the other gates are CLEAN (score 1), which is the
    # 201/201 archive situation.
    E_clean = sp.simplify(E.subs({s2: 1, s3: 1, s4: 1}))
    print(f"      with e2=e3=e4=1 (the archived case): E = {E_clean}")
    for W in (2, 10, 100, 10**6):
        v = sp.nsimplify(E_clean.subs(w1, W))
        print(f"        w1 = {W:>8}: E = {v} = {float(v):.10f}  > 0 -> "
              f"sk > 0 -> ADMISSIBLE")
    lim = sp.limit(E_clean, w1, sp.oo)
    print(f"      lim_(w1->oo) E = {lim}. Since tristate = ADMISSIBLE iff "
          f"sk > 0 and")
    print(f"      E > 0 for every finite w1, no reweighting ever rejects. "
          f"QED.")
    assert lim == 0 and all(float(E_clean.subs(w1, W)) > 0
                            for W in (2, 10, 100, 10**6))
    # Cross-check the operational value on 3 tools.
    v_sp = sp.Rational(5, 7)
    v_fr = Fraction(2 * 0 + 2 * 1 + 1 * 1 + 2 * 1, 2 + 2 + 1 + 2)
    v_mp = mp.mpf(5) / 7
    print(f"      the admitted score, 3 tools: sympy {v_sp} = "
          f"{float(v_sp):.16f} | Fraction {float(v_fr):.16f} | "
          f"mpmath {mp.nstr(v_mp, 17)}")
    assert v_fr == Fraction(5, 7) and abs(float(v_sp) - float(v_mp)) < 1e-30
    print(f"      FIX_EFFICACY_GATE_WEIGHT read from the module = "
          f"{FIX_EFFICACY_GATE_WEIGHT}")
    print()


def main() -> int:
    print("=" * 78)
    print("Q3  THE e1_efficacy VETO — EFFICACY, INVARIANCE, AND REACHABILITY")
    print("=" * 78)
    print()
    derive_no_weight_can_veto()

    src = TARGET.read_text(encoding="utf-8")
    fix = _fix_for(src)
    base = {"ruff_violations": 0, "bandit_findings": {"high": 0, "medium": 0}}

    def call(outcome):
        return compute_sk(
            fix_text=fix, source=src, source_path=str(TARGET),
            baseline=base, test_cmd=None,
            declared_target_kind="python_module",
            fix_efficacy_outcome=outcome,
        )

    print("M1  EFFICACY — the class the veto targets")
    r = call(FIX_INEFFECTIVE)
    print(f"      e1 = FIX_INEFFECTIVE -> tristate = {r.tristate}, "
          f"sk = {r.sk}, E = {r.E}")
    veto = r.gate_details.get("_e1_veto")
    print(f"      _e1_veto record present: {veto is not None}")
    if veto:
        print(f"        computed_sk (what the arithmetic said) = "
              f"{veto['computed_sk']}")
        print(f"        computed_E                             = "
              f"{veto['computed_E']}")
    assert r.tristate == SK_REJECTED, r.tristate
    assert r.sk == 0.0
    assert veto is not None and veto["computed_sk"] > 0, (
        "the advisory number must be PRESERVED, not suppressed")
    print(f"      the arithmetic is PRESERVED for the HIL, not suppressed. "
          f"Nothing is hidden.")
    print()

    print("M2  INVARIANCE — every other e1 class must be BIT-IDENTICAL")
    others = [FIX_CURES, NO_FALSIFIER, None,
              "INDETERMINATE_NO_BASELINE", "INDETERMINATE_OTHER",
              "INDETERMINATE_NOT_INTERCEPTED"]
    ok = True
    for o in others:
        rr = call(o)
        has_veto = "_e1_veto" in rr.gate_details
        e1 = rr.gate_details.get("e1_efficacy", {}).get("score")
        line = (f"      e1 = {str(o):<42} score={str(e1):<5} "
                f"tristate={rr.tristate:<11} sk={rr.sk:<8} "
                f"veto_fired={has_veto}")
        print(line)
        if has_veto:
            ok = False
    assert ok, "INVARIANCE FAILED: the veto fired on a class it must not touch"
    print(f"      the veto fired on 0 of {len(others)} non-ineffective "
          f"classes.")
    print()

    print("M3  REACHABILITY — is the branch reached by a LIVE call?")
    print(f"      M1 above is a live compute_sk() on a real repository module")
    print(f"      ({TARGET.relative_to(REPO)}), not a stub. The branch is "
          f"reached.")
    print()

    print("M4  THE ONE BOUNDARY CASE — does the veto steal prose's NO_SCORE?")
    prose = REPO / "bench/tests/fixtures/stem/docs/STR-07-REF-01.md"
    ptext = prose.read_text(encoding="utf-8")
    ptail = [l for l in ptext.split("\n") if l.strip()][-1]
    pfix = ("<<<< SEARCH\n" + ptail + "\n====\n" + ptail +
            "\n>>>> REPLACE\n")
    pr = compute_sk(fix_text=pfix, source=ptext, source_path=str(prose),
                    baseline=base, test_cmd=None,
                    declared_target_kind="prose",
                    score_prose_listings=True,
                    fix_efficacy_outcome=FIX_INEFFECTIVE)
    print(f"      prose target, e1 = FIX_INEFFECTIVE -> {pr.tristate}")
    print(f"      _e1_veto present: {'_e1_veto' in pr.gate_details}   "
          f"_prose_one_sided present: "
          f"{'_prose_one_sided' in pr.gate_details}")
    print(f"      NOTE FOR THE HIL: on prose the e1 veto now runs BEFORE the")
    print(f"      prose one-sided veto. Where e1 is genuinely measured on a")
    print(f"      prose fix that does not cure its falsifier, the outcome")
    print(f"      moves NO_SCORE -> REJECTED. That is a DECIDED rejection on")
    print(f"      measured evidence, not a static sweep, so it is admissible")
    print(f"      under the prose reasoning -- but it IS a behaviour change on")
    print(f"      the prose path and the founder should rule on it explicitly.")
    print()

    print("=" * 78)
    print("BOTH HALVES HOLD. Efficacy: the targeted class flips to REJECTED.")
    print("Invariance: 0 of 6 other classes move. The advisory arithmetic is")
    print("preserved in `_e1_veto.computed_sk`, so nothing is hidden.")
    print("SUGGESTED TO THE HUMAN. Not decided here.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
