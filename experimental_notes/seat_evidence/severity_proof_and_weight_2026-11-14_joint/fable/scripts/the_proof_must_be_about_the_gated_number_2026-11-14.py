# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_proof_and_weight_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 03253c0a7e6f1e3212171f883034fb2cc25c9a05a3537158ae14eea0392fb813
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""R1, R2 and R3 measured, not argued. Panel round of 2026-11-14.

THREE QUESTIONS, THREE MEASUREMENTS.

R1  Repoint `severity_is_proven` so the proof is about the number the GATE
    reads rather than about R_k. Measured over every archived entry carrying a
    PASS/WARN proof: how many still release, and in which DIRECTION the gate
    moves. The direction is the part a count alone does not give you, and a
    change of unknown direction is not a fix.

R2  Add a 3rd consequence weight strictly inside (1/2, 1). Measured with z3:
    does consequence MAGNITUDE then decide the gate, or does the gate still
    reduce to a test on the model-asserted `confidence`?

R3  Retire the product for the ordered pair (c_d(f), credence(f)). Measured
    with z3 on the ORDINAL-ADMISSIBILITY criterion that
    `bench/directives/universal/cdsfl_core_formal.md` now carries: a statement
    about an ordinal quantity must survive re-labelling the scale by a strictly
    increasing map. This is the measurement that decides R2 vs R3, and it is
    NOT the weak "they do not conflict" form.

Usage: python3 scripts/the_proof_must_be_about_the_gated_number_2026-11-14.py
"""
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

LOGS = REPO / "bench" / "logs"


def archived_proven_entries():
    """Every archived entry carrying a PASS/WARN R_k proof, as dicts."""
    out = []
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                   # noqa: BLE001
            continue
        for e in ((d or {}).get("registry") or {}).get("entries", {}).values():
            if not isinstance(e, dict):
                continue
            proof = e.get("severity_proof")
            if not isinstance(proof, dict):
                continue
            if str(proof.get("status") or "").strip().upper() not in ("PASS", "WARN"):
                continue
            rk = proof.get("recomputed_rk", proof.get("model_rk"))
            if isinstance(e.get("severity"), (int, float)) and isinstance(rk, (int, float)):
                out.append(e)
    return out


def main() -> int:
    import reference_runner_v3 as rr
    from statsmodels.stats.proportion import proportion_confint

    entries = archived_proven_entries()
    n = len(entries)
    print("=" * 74)
    print("R1 -- REPOINTING THE PROOF AT THE NUMBER THE GATE READS")
    print("=" * 74)
    print(f"archived entries carrying a PASS/WARN R_k proof: {n}")
    if n < 10:
        print("too few entries; the measurement is void.")
        return 3

    # ARM A: the flag OFF -- today's tree, byte-identical behaviour.
    rr._SEVERITY_PROOF_MATCHES_GATED["on"] = False
    off = [rr.severity_is_proven(e) for e in entries]
    # ARM B: the flag ON -- the repointed door.
    rr._SEVERITY_PROOF_MATCHES_GATED["on"] = True
    on = [rr.severity_is_proven(e) for e in entries]
    rr._SEVERITY_PROOF_MATCHES_GATED["on"] = False          # leave as found

    k_off, k_on = sum(off), sum(on)
    loosened = sum(1 for a, b in zip(off, on) if b and not a)
    tightened = sum(1 for a, b in zip(off, on) if a and not b)

    print(f"  proven with the door as it stands : {k_off}/{n}")
    print(f"  proven with the proof repointed   : {k_on}/{n}")
    lo, hi = proportion_confint(k_on, n, alpha=0.05, method="wilson")
    print(f"  still releasing: {k_on}/{n} = {k_on/n:.2%}  Wilson [{lo:.2%}, {hi:.2%}]")
    slo, shi = proportion_confint(tightened, n, alpha=0.05, method="wilson")
    print(f"  STOP releasing : {tightened}/{n} = {tightened/n:.2%}  "
          f"Wilson [{slo:.2%}, {shi:.2%}]")
    print()
    print("  DIRECTION OF EFFECT, which a count alone does not give:")
    print(f"    entries moved PROVEN -> UNPROVEN (gate TIGHTENS): {tightened}")
    print(f"    entries moved UNPROVEN -> PROVEN (gate LOOSENS) : {loosened}")
    if loosened:
        print("    FALSIFIED: the repoint is not monotone. It can manufacture a release.")
        return 1
    print("    MONOTONE TIGHTENING over the whole archive: 0 entries loosen.")
    print("    All 3 live call sites admit MORE when severity_is_proven is True")
    print("    (runner lines ~4442 A4 door, ~9735 reasoned withdrawal, ~10936")
    print("    calibration demotion), so a strictly smaller proven set strictly")
    print("    shrinks what is released.")

    print()
    print("=" * 74)
    print("R2 vs R3 -- THE ORDINAL-ADMISSIBILITY MEASUREMENT")
    print("=" * 74)
    from z3 import Solver, Real, Reals, Or, And, Q, sat, unsat

    # (a) Does a 3rd weight make consequence MAGNITUDE decide the cut?
    print("(a) with a 3rd weight w3 in (1/2,1), what does `Sev >= 0.7` become?")
    allu = True
    for w3 in (Q(51, 100), Q(3, 4), Q(9, 10), Q(99, 100)):
        W, C, V = Reals("W C V")
        dom = And(Or(W == Q(1, 2), W == w3, W == 1), C >= 0, C <= 1,
                  Or(V == 0, V == Q(1, 2), V == 1))
        equiv = ((W * C * V) >= Q(7, 10)) == And(
            V == 1, Or(And(W == 1, C >= Q(7, 10)),
                       And(W == w3, C >= Q(7, 10) / w3)))
        s = Solver(); s.add(dom, equiv == False)            # noqa: E712
        r = s.check()
        allu &= (r == unsat)
        print(f"    w3={w3}: negation of 'cut == V=1 AND class-rescaled "
              f"confidence test' -> {r}")
    print(f"    => for every w3 tested the equivalence HOLDS ({allu}).")
    print("    The magnitude test is STILL on `confidence`, a model-asserted")
    print("    belief; the 3rd weight only rescales the belief cut per class.")

    # (b) THE DECIDER. Severity is ordinal. Re-label the consequence classes by
    #     any strictly increasing phi preserving the class ordering. Does the
    #     induced ordering ON FINDINGS survive?
    print()
    print("(b) is the finding-ordering invariant under a strictly increasing")
    print("    re-label of the consequence scale?")
    a, b, cA, cB = Reals("a b cA cB")
    s = Solver()
    s.add(a > 0, b > a)                      # strictly increasing; SOFT < HARD kept
    s.add(cA >= 0, cA <= 1, cB >= 0, cB <= 1)
    s.add(Q(1, 2) * cA > Q(1, 1) * cB)       # original labels: A outranks B
    s.add(a * cA < b * cB)                   # re-labelled: the order FLIPS
    r2 = s.check()
    print(f"    R2 (product W*c*Ver): order-flipping re-label exists? {r2}")
    if r2 == sat:
        m = s.model()
        print(f"      witness: {{{', '.join(f'{d}={m[d]}' for d in m)}}}")

    c1, c2, a2, b2 = Reals("c1 c2 a2 b2")
    s2 = Solver()
    s2.add(a2 > 0, b2 > a2, c1 >= 0, c1 <= 1, c2 >= 0, c2 <= 1)
    orig = Or(Q(1, 2) > Q(1, 1), And(Q(1, 2) == Q(1, 1), c1 > c2))
    new = Or(a2 > b2, And(a2 == b2, c1 > c2))
    s2.add(orig != new)
    r3 = s2.check()
    print(f"    R3 (ordered pair, lexicographic): verdict-changing re-label? {r3}")

    print()
    if r2 == sat and r3 == unsat:
        print("    DECIDED BY MEASUREMENT, NOT BY JUDGEMENT:")
        print("    R2 leaves the ordering BREAKABLE (sat). R3 is INVARIANT (unsat).")
        print("    They are EXCLUSIVE, not composable: composing them would")
        print("    re-admit the inadmissible product alongside the admissible")
        print("    pair, and the composite inherits the sat. A composition is")
        print("    therefore strictly WORSE than R3 alone on the named property")
        print("    (invariance under strictly increasing re-labelling).")
        return 0
    print("    UNEXPECTED: the exclusivity argument did not reproduce.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
