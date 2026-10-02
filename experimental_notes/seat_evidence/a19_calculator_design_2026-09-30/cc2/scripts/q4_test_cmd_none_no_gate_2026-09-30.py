# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9b522479956d54cd60387c1f40e634054830cf44d3e3210e22bc0f5bc6661e4c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q4 - should `test_cmd=None` mean NO GATE rather than a substituted default,
and what is the consequence DURING A RUNNING EXPERIMENT?

Run from the repository root:

    python3 scripts/q4_test_cmd_none_no_gate_2026-09-30.py

CC1's measurement, to verify or refute: "no verdict and no R_k moves and only
the advisory number shifts 0.9782 to 1.0". This script tests the claim by
calling the live producer and the live consumer, and then enumerates what the
claim does NOT cover.
"""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import mpmath as mp                                            # noqa: E402
import sympy as sp                                             # noqa: E402

from bench.reference_runner_v3 import (                        # noqa: E402
    SK_NO_SCORE, _gates_introduced_new_defects, _run_effect_regression,
    apply_sk_to_rk,
)

mp.mp.dps = 30
PROSE = REPO / "bench/tests/fixtures/stem/docs/STR-07-REF-01.md"


def _load_arms():
    path = REPO / "bench/tools/commissioning_arms_2026-09-21.py"
    spec = importlib.util.spec_from_file_location("commissioning_arms", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["commissioning_arms"] = mod        # dataclass needs this
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    print("=" * 78)
    print("Q4  test_cmd=None -- NO GATE, OR A SUBSTITUTED DEFAULT?")
    print("=" * 78)
    print()

    # ------------------------------------------------------------------
    print("A  THE GUARD, READ BY CALLING IT (execute-do-not-grep)")
    mod = _load_arms()
    arms = {a.key: a for a in mod.ARMS}
    a4 = arms["arm4"]
    argv = a4.argv()
    print(f"      arm4.test_cmd     = {a4.test_cmd!r}")
    print(f"      arm4.argv()       = {argv}")
    emits = "--test-cmd" in argv
    print(f"      emits --test-cmd  : {emits}")
    assert not emits, "arm4 now emits --test-cmd; this script is stale"

    # END TO END: arm4's argv through the REAL parser. Not a grep.
    spec = importlib.util.spec_from_file_location(
        "rse_q4", REPO / "bench/tools/run_simulated_experiment.py")
    rse = importlib.util.module_from_spec(spec)
    sys.modules["rse_q4"] = rse
    spec.loader.exec_module(rse)
    ns4 = rse.build_parser().parse_args(argv)
    ns1 = rse.build_parser().parse_args(arms["arm1"].argv())
    print(f"      parse_args(arm4.argv()).test_cmd = {ns4.test_cmd!r}")
    print(f"      parse_args(arm1.argv()).test_cmd = "
          f"{(ns1.test_cmd or '')[:44]!r}...")
    print(f"      arm4 declines -> NO GATE  : {ns4.test_cmd is None}")
    print(f"      arm1 supplies -> gate ON  : {bool(ns1.test_cmd)}")
    assert ns4.test_cmd is None, (
        "REFUTED: argparse still substitutes a value arm4 declined to give")
    assert ns1.test_cmd, "an arm that DOES supply a command must keep it"
    print()

    # ------------------------------------------------------------------
    print("B  DOES THE SUBSTITUTED SUITE EVEN SEE THE TARGET?")
    text = PROSE.read_text(encoding="utf-8")
    cmd = ("python3 -m pytest bench/tests/test_immune_memory_consumption.py "
           "bench/tests/test_immune_memory_evaluation.py -q")
    s_real, d_real = _run_effect_regression(text, str(PROSE), cmd)
    s_dead, d_dead = _run_effect_regression("", str(PROSE), cmd)
    print(f"      prose with REAL bytes      -> score {s_real}  ({d_real})")
    print(f"      prose with bytes DESTROYED -> score {s_dead}  ({d_dead})")
    blind = (s_real == s_dead)
    print(f"      identical => the gate is BLIND to its target: {blind}")
    assert blind, "REFUTED: e2 discriminates on prose after all"
    print()

    # ------------------------------------------------------------------
    print("C  CC1's CLAIM: no verdict moves, no R_k moves, only the advisory")
    clean = {"e3_ruff": {"detail": "4 total, 0 new (baseline: 4)"},
             "e4_bandit": {"detail":
                           "0 HIGH/0 MEDIUM (baseline: 0H/0M, new: 0H/0M)"}}
    # The veto reads ONLY e3/e4 `new:` fields. Sweep e2 across its whole range
    # and show the veto output is constant.
    outs = set()
    for e2 in (None, 0.0, 0.25, 0.5, Fraction(52, 55), 0.99, 1.0):
        d = dict(clean)
        d["e2_regression"] = {"score": e2, "detail": f"{e2} (synthetic)"}
        outs.add(tuple(_gates_introduced_new_defects(d)))
    print(f"      distinct veto outputs over 7 e2 values : {len(outs)} "
          f"-> {outs}")
    assert len(outs) == 1, "REFUTED: the veto is sensitive to e2"

    r_old = 0.5
    r_new, why = apply_sk_to_rk(r_old, SK_NO_SCORE)
    print(f"      apply_sk_to_rk({r_old}, NO_SCORE) -> {r_new}   "
          f"delta = {r_new - r_old}")
    assert r_new == r_old, "REFUTED: NO_SCORE moves R_k"
    print(f"      reason returned: {why[:70]}...")

    E_with = sp.Rational(2 * 52, 55) + 1 + 2
    E_with = sp.Rational(2 * 52 + 55 * 3, 5 * 55)
    E_without = sp.Rational(1 + 2, 3)
    print(f"      E with substituted suite (4 gates, w=2,2,1,... ) = "
          f"{E_with} = {float(E_with):.6f}")
    print(f"      E without it (3 gates)                          = "
          f"{E_without} = {float(E_without):.6f}")
    fr = Fraction(2 * 52 + 55 * 3, 5 * 55)
    print(f"      cross-check Fraction {float(fr):.6f} | mpmath "
          f"{mp.nstr(mp.mpf(269) / 275, 9)}")
    assert fr == Fraction(269, 275)
    print(f"      the advisory moves UPWARD, {float(E_with):.4f} -> "
          f"{float(E_without):.4f}, when the FALSE input is removed.")
    print(f"      CC1's CLAIM IS CONFIRMED on all three counts.")
    print()

    # ------------------------------------------------------------------
    print("D  WHAT CC1's CLAIM DOES NOT COVER — the other e2 consumers")
    consumers = {
        "scripts/estimate_nu_from_archive_2026-09-21.py":
            "reads e2_regression.score from ARCHIVED entries to emit a nu "
            "lower bound; filters on ADMISSIBLE, which prose never is -- so "
            "unaffected TODAY, and affected the moment prose becomes "
            "scoreable.",
        "scripts/a19_break_even_assumes_e2_absent_2026-09-30.py":
            "counts occurrences of the 52/55 constant in the archive; its "
            "count CHANGES under this fix, by construction.",
        "scripts/scorer_discrimination_2026-09-20.py":
            "re-implements the weighted mean with its OWN hardcoded "
            "WEIGHTS['e2_regression'] = 2.0 -- a second copy of the weight "
            "that no test pins to the runner's literal.",
        "bench/tests/test_prose_acceptance_stem.py:1162":
            "asserts _prose_one_sided['computed_sk'] lies in (0, 1]. 1.0 is "
            "in range, so the test survives removal of the substituted suite.",
        "runner_state.json / checkpoint / sk_pipeline":
            "PERSISTED. A resumed run restores the registry, but the AST "
            "guard in test_immune_memory_consumption.py bounds the reader set "
            "to 4 functions, none of which reads the e2 score by name.",
    }
    for k, v in consumers.items():
        print(f"      {k}")
        print(f"         {v}")
    print()

    print("E  THE TEST CONFLICT THIS TREE ALREADY CARRIES")
    fab = REPO / "scripts/falsifier_supply_fable_2026-09-30.py"
    tst = REPO / "bench/tests/test_commissioning_arms_carry_their_settings_2026-09-21.py"
    ft = fab.read_text() if fab.exists() else ""
    tt = tst.read_text() if tst.exists() else ""
    print(f"      scripts/falsifier_supply_fable_2026-09-30.py asserts "
          f"test_cmd == '' : {'test_cmd ==' in ft or 'test_cmd==' in ft}")
    print(f"      bench/tests/...carry_their_settings asserts "
          f"--test-cmd NOT in argv : {'--test-cmd' in tt and 'not in' in tt}")
    print(f"      These two cannot both be satisfied. A committed TEST pins "
          f"the")
    print(f"      CURRENT behaviour, so the 'pass an empty string' repair is "
          f"a")
    print(f"      TEST CHANGE as well as a code change, and under "
          f"`falsifier-integrity`")
    print(f"      rule 2 that must be reported, not performed quietly.")
    print()

    print("=" * 78)
    print("POSITION: test_cmd=None must mean NO GATE. The simplest sufficient")
    print("route is to make the ABSENCE representable end to end -- argparse")
    print("default None, and argv() emitting the flag on `is not None` -- so")
    print("no layer can substitute a value the caller declined to give.")
    print("DURING A RUNNING EXPERIMENT the only movement is the advisory")
    print("number, 0.978182 -> 1.0, upward. SUGGESTED, not decided.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
