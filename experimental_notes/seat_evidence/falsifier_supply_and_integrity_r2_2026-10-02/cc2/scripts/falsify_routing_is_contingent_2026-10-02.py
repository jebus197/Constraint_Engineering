# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 94f6495631f3e3052081887df1da45fa40b0dab712ff50b601bd169992aff75f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: part 3 of `falsify_prose_falsifier_supply_2026-09-30.py` is
TAUTOLOGICAL, and here is the contingent measurement that replaces its claim.

THE ALLEGATION, made precise. That script's part 3 is captioned "routing is a
multiplier on supply, not a substitute" and reports

    RESOLVED  no supply: 0/5   corpus supply: 5/5

from which it concludes "adding rungs cannot close this gap". But look at the two
`resolve_fn`s it drives `routing.resolve_via_routing` with:

    def untaught(model, finding):  return ""                   # ignores `model`
    def taught(model, finding):    return finding["_template"]  # ignores `model`

Neither is a function of `model`. So:

  * `untaught` returns falsy at EVERY rung. `resolve_via_routing` sets
    `last_verdict = "ERROR"` and `continue`s on empty code (bench/routing.py:163),
    so 0/5 is forced by the arm's own constancy, for any ladder of any length.
  * `taught` returns a body that part 1 of the SAME script has already shown
    CONFIRMS under the real decider. Rung 1 therefore confirms and the function
    returns early (bench/routing.py:168), so 5/5 is forced by part 1.

0/5 vs 5/5 is thus entailed by part 1 plus "resolve_via_routing forwards its
resolve_fn's output". It is a restatement of the arms' construction, and it is
true of any router with that signature -- including one that does no routing at
all. A measurement whose outcome cannot vary with the mechanism it names is not
evidence about that mechanism. Part 1 (bidirectional discrimination, 5/5) and
part 2 (0 live-path importers) are CONTINGENT and stand; only part 3's inference
is void.

WHAT IS DELIVERED, and it is an ADDITION rather than a removal. The 2026-09-30
script is EVIDENCE, rescued verbatim, and its parts 1-2 carry the root-cause
finding. Nothing here renders it redundant, so nothing is deleted. This file adds
the contingent test part 3 should have been:

  T  TAUTOLOGY DEMONSTRATED. Perturb the ladder every way it can be perturbed --
     reverse it, truncate it to one rung, fabricate rung names, sweep max_rungs
     1..5 -- and both of part 3's scores are INVARIANT. Asserted, not asserted
     about.
  C  CONTINGENT REPLACEMENT. Hold SUPPLY fixed and make it a function of `model`:
     the first rung writes a body that errors, a later rung writes the corpus
     pattern. Now `max_rungs=1` resolves 0/5 and `max_rungs=2` resolves 5/5 with
     the SAME supply function, which isolates the LADDER as the variable. This is
     the first executed evidence in the archive that climbing a rung ever
     converts a non-confirmation into a CONFIRMED.
  G  CANNOT-FAIL GUARD. A general harness that cannot fail is worse than none --
     this project shipped `check_sk_threshold` hardwired to `return True` past 321
     tests. So T asserts invariance where invariance is the defect, C asserts a
     DIFFERENCE between two ladder depths, and G re-runs C with the ladder
     dependence removed and requires the difference to VANISH. If C ever stops
     discriminating, G fails loudly instead of this script printing a reassuring
     5/5.

Exit 0 and prints the verdict; exit 1 if any property fails. No Wolfram result is
used: every quantity here is an integer count from the project's own decider.

Run:  python3 scripts/falsify_routing_is_contingent_2026-10-02.py
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench/tests/fixtures/stem"))

import stem_fixtures as SF                                    # the REAL corpus
from bench.falsifier_verify import reverify_falsifier          # the REAL decider
from bench.routing import rank_falsifier_writers, resolve_via_routing


def wilson(k: int, n: int) -> tuple[float, float, float, float]:
    """statsmodels, cross-checked against an independent mpmath closed form."""
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return float(lo_sm), float(hi_sm), float((c - h) / d), float((c + h) / d)


def pct(k: int, n: int) -> str:
    lo, hi, mlo, mhi = wilson(k, n)
    agree = abs(lo - mlo) < 1e-9 and abs(hi - mhi) < 1e-9
    return (f"{k}/{n} = {100*k/n:7.3f}%  Wilson [{100*lo:6.2f}%, {100*hi:6.2f}%]"
            f"  mpmath-agrees={agree}")


def _decide(code: str) -> str:
    return reverify_falsifier(code, repo_root=str(ROOT))


def _resolved(resolve_fn, rungs, max_rungs: int) -> int:
    n = 0
    for f in SF.FIXTURES:
        r = resolve_via_routing(
            {"finding_id": f.key, "_template": f.falsifier()},
            rungs, resolve_fn, _decide, max_rungs=max_rungs)
        n += bool(r.resolved)
    return n


# ── part 3's own two arms, verbatim in behaviour ─────────────────────────────
def untaught(model, finding):      # noqa: ARG001 - ignoring `model` IS the point
    return ""


def taught(model, finding):        # noqa: ARG001 - ignoring `model` IS the point
    return finding["_template"]


def main() -> int:
    N = len(SF.FIXTURES)
    real = rank_falsifier_writers(["Gemini-SIM", "Codex-SIM"])
    print(f"corpus fixtures: {N}   real ladder from rank_falsifier_writers: {real}")

    # ── T: the tautology ────────────────────────────────────────────────────
    print("\n== T: part 3's scores are INVARIANT under every ladder perturbation ==")
    ladders = {
        "real (as part 3 drives it)": (list(real), 2),
        "reversed": (list(reversed(real)), 2),
        "truncated to 1 rung": (list(real)[:1], 2),
        "fabricated rung names": (["NotAModel-A", "NotAModel-B"], 2),
        "max_rungs=1": (list(real), 1),
        "max_rungs=5": (list(real), 5),
        "single fabricated rung, max_rungs=1": (["NoSuchModel"], 1),
    }
    seen_untaught, seen_taught = set(), set()
    for label, (rungs, mr) in ladders.items():
        u = _resolved(untaught, rungs, mr)
        t = _resolved(taught, rungs, mr)
        seen_untaught.add(u)
        seen_taught.add(t)
        print(f"  {label:38s} no-supply {u}/{N}   corpus-supply {t}/{N}")
    print(f"  distinct no-supply scores   : {sorted(seen_untaught)}")
    print(f"  distinct corpus-supply scores: {sorted(seen_taught)}")
    tautological = (seen_untaught == {0} and seen_taught == {N})
    print(f"  TAUTOLOGY CONFIRMED (outcome independent of the ladder): {tautological}")
    print(f"    no supply   {pct(0, N)}")
    print(f"    corpus supply {pct(N, N)}")
    print("    n=5 is small and the intervals say so; the finding is the "
          "INVARIANCE, which no interval can soften.")

    # ── C: the contingent replacement ───────────────────────────────────────
    # Supply is now a FUNCTION OF THE RUNG. Rung 1's writer emits a body that the
    # real decider cannot confirm; rung 2's writer emits the corpus pattern. The
    # supply function is IDENTICAL across the two measurements below; only the
    # ladder depth moves.
    print("\n== C: hold SUPPLY fixed, move the LADDER ==")
    if len(real) < 2:
        print("  NOT MEASURABLE: the real ladder has fewer than 2 rungs")
        return 1
    weak, strong = real[0], real[1]

    def rung_dependent(model, finding):
        if model == strong:
            return finding["_template"]
        # A syntactically valid falsifier that exits cleanly: the decider must
        # read it as "defect not demonstrated", never as a confirmation.
        return "x = 1\nassert x == 1\n"

    one = _resolved(rung_dependent, real, 1)
    two = _resolved(rung_dependent, real, 2)
    print(f"  rung 1 writer = {weak} (emits a clean-exiting body)")
    print(f"  rung 2 writer = {strong} (emits the corpus pattern)")
    print(f"  max_rungs=1 resolved {pct(one, N)}")
    print(f"  max_rungs=2 resolved {pct(two, N)}")
    contingent = (one == 0 and two == N)
    print(f"  CLIMBING A RUNG CONVERTS NON-CONFIRMATION -> CONFIRMED: {contingent}")

    # ── G: the cannot-fail guard ────────────────────────────────────────────
    # Remove the rung dependence and C MUST stop discriminating. If it does not,
    # C is measuring something other than the ladder and its result is void.
    print("\n== G: cannot-fail guard -- strip the rung dependence, lose the effect ==")

    def rung_blind(model, finding):      # noqa: ARG001
        return finding["_template"]

    g1 = _resolved(rung_blind, real, 1)
    g2 = _resolved(rung_blind, real, 2)
    print(f"  rung-blind supply: max_rungs=1 -> {g1}/{N}, max_rungs=2 -> {g2}/{N}")
    guard_ok = (g1 == g2 == N)
    print(f"  GUARD HELD (no ladder effect without ladder dependence): {guard_ok}")

    print("\nVERDICT")
    print(f"  part 3 of the 2026-09-30 script is TAUTOLOGICAL : {tautological}")
    print(f"  the ladder DOES multiply supply, measured here  : {contingent}")
    print(f"  the measurement can still fail                  : {guard_ok}")
    print("  part 1 (5/5 bidirectional) and part 2 (0 live-path importers) are\n"
          "  contingent and are NOT disturbed by this finding. Nothing is removed.")
    return 0 if (tautological and contingent and guard_ok) else 1


if __name__ == "__main__":
    import argparse

    argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None).parse_args()
    raise SystemExit(main())
