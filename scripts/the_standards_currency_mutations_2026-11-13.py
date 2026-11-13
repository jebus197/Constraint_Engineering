#!/usr/bin/env python3
"""Does the standards-currency guard actually go RED? 5 mutations, 1 per contract.

A passing test proves nothing until it has been made to fail. This reverts each
contract the guard claims to hold and checks the NAMED test for that contract
turns red -- not merely that something somewhere failed, which is how a mutation
harness scores itself on the wrong test.

RESTORE DISCIPLINE. `feedback_a_harness_must_restore_what_it_found_2026-11-01`: the
original bytes are held in memory and written back, then compared byte for byte.
Never `git checkout --`, which would also discard uncommitted work that was there
before this script ran. And `feedback_a_restore_is_itself_a_mutation_2026-11-01`:
the restore is verified, not assumed.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PRODUCER = REPO / "scripts" / "standards_currency_and_model_staleness_2026-11-13.py"
GUARD = "bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py"

#: (name, test to select, what to replace, replacement, why this is the right test)
MUTATIONS = [
    # ★ M1 WAS RE-ANCHORED on 2026-11-13 after `_live` was rewritten to carry an
    # explicit APPARATUS set. The old anchor named a condition that no longer
    # exists, and the harness reported ANCHOR NOT FOUND rather than passing --
    # `feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04`.
    ("M1 apparatus exclusion made decorative",
     "test_c2_the_self_exclusion_is_reachable_and_moves_the_count",
     "            if p.resolve().relative_to(REPO).as_posix() in APPARATUS:\n                return False\n",
     "            if False and p.resolve().relative_to(REPO).as_posix() in APPARATUS:\n                return False\n",
     "the flag is still accepted but never acts, so both census calls agree"),

    ("M2 seat binding name guessed again",
     "test_c3_the_seat_table_lifts_non_empty",
     '("_ALL", "SEATS", "MODELS", "_MODELS")',
     '("SEATS",)',
     "a wrong name yields 0 rows and reads exactly like an empty seat table"),

    ("M3 year length wrong in the first-order denominator",
     "test_c1_the_run_rate_cancels_out_of_the_exposure_fraction",
     "frac = sp.simplify(lam * window / sp.Rational(36525, 100))",
     "frac = sp.simplify(lam * window / sp.Rational(365, 1))",
     "365 instead of 365.25 moves the closed form off 2*lambda*T/1461"),

    ("M4 one confidence-interval route broken",
     "test_c5_both_interval_routes_agree_on_both_families",
     "    half = (z / (1 + c)) * np.sqrt(ph * (1 - ph) / n + c / (4 * n))",
     "    half = z * np.sqrt(ph * (1 - ph) / n)",
     "a naive Wald half-width inside intervals(); statsmodels, computed "
     "independently in the guard, must stop agreeing with it"),

    ("M5 a label the current brief declares stops printing",
     "test_the_producer_runs_clean_end_to_end",
     'print(f"  exposure_T30_GHS = {e30:.6f}")',
     'print(f"  exposure_at_thirty_days = {e30:.6f}")',
     "the brief declares exposure_T30_GHS; a renamed label breaks the citation"),

    ("M6 archived seat evidence re-admitted to the population",
     "test_c2_the_self_exclusion_is_reachable_and_moves_the_count",
     'or "seat_evidence" in parts):',
     '):',
     "359 harvested files from 63 earlier rounds re-enter, and the share moves "
     "from 0.282700 back toward 0.253054 -- other models' sandbox output counted "
     "as this project's source"),

    ("M7 the exact exposure law broken",
     "test_c7_the_exact_law_and_the_first_order_form_agree_in_the_limit",
     "    stale = sp.integrate(1 - sp.exp(-lam * t), (t, 0, T))",
     "    stale = sp.integrate(1 + sp.exp(-lam * t), (t, 0, T))",
     "a sign flip makes the first-order form UNDERSTATE, which is the unsafe "
     "direction, and breaks the series relation"),

    ("M8 the exposure ceiling solved for the wrong level",
     "test_c8_the_exposure_ceiling_root_is_cross_checked",
     "    f = lambda x: exposure_exact_value(lam_per_year, x) - ceiling",
     "    f = lambda x: exposure_exact_value(lam_per_year, x) - ceiling * 2",
     "the exact ceiling must exceed the first-order one; doubling the level "
     "inverts that relation"),

    # ★ M10 AND M11 ADDED 2026-11-13 after BOTH free panel seats proved, in the
    # joint round and independently of each other, that the exact law had been
    # added to this producer and left UNWIRED -- the cross-check still asserted
    # against the first-order form at a typed single-seed tolerance, and
    # `exposure_ceiling_cadence` had no caller inside the producer at all.
    ("M10 cross-check re-anchored to the first-order form",
     "test_the_producer_runs_clean_end_to_end",
     "            ex = exposure_exact_value(L, td)",
     "            ex = L * td / 2 / 365.25",
     "the vacuity guard must fire: a cross-check anchored to the first-order "
     "term cannot prefer the exact law over it, so it is not a second route"),

    ("M11 the ceiling function loses its only producer caller",
     "test_the_producer_runs_clean_end_to_end",
     "    tmax_worst_exact = exposure_ceiling_cadence(lam_worst, 0.01)",
     "    tmax_worst_exact = tmax_worst",
     "an addition nothing reaches: the exact ceiling must exceed the first-order "
     "one, and reverting to the first-order value makes that assertion fail"),

    ("M9 a retirement becomes silent",
     "test_the_producer_runs_clean_end_to_end",
     'print("  ★ THE COUNT THAT STOOD HERE IS REFUTED: `composed_covers = 5 of 5`")',
     'print("  the count below is one view of the composition")',
     "a withdrawn figure must stay recorded where it was; a silent removal is "
     "indistinguishable from a figure never claimed"),
]


def run_test(selector: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-k", selector,
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=900)
    return r.returncode, (r.stdout + r.stderr)[-400:]


def main() -> int:
    original = PRODUCER.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    print(f"subject  : {PRODUCER.relative_to(REPO)}")
    print(f"sha256   : {digest[:16]}  ({len(original)} bytes held in memory)")
    print()

    print("BASELINE -- every contract must be GREEN before any mutation")
    rc, tail = run_test(" or ".join(m[1] for m in MUTATIONS))
    if rc != 0:
        print(f"  REFUSED: baseline is already red (rc={rc}). A mutation harness "
              f"cannot measure anything against a red baseline.\n{tail}")
        return 2
    print("  baseline GREEN")
    print()

    red = 0
    results = []
    try:
        for name, selector, old, new, why in MUTATIONS:
            src = original.decode()
            if old not in src:
                print(f"  {name}: ANCHOR NOT FOUND -- the mutation could not be "
                      f"applied, so it proves nothing. Fix the anchor.")
                results.append((name, "ANCHOR MISSING"))
                continue
            PRODUCER.write_text(src.replace(old, new, 1))
            rc, tail = run_test(selector)
            ok = rc != 0
            red += ok
            results.append((name, "RED" if ok else "STILL GREEN"))
            print(f"  {name}")
            print(f"    target test : {selector}")
            print(f"    why         : {why}")
            print(f"    verdict     : {'RED (the guard caught it)' if ok else 'STILL GREEN -- THE GUARD IS BLIND HERE'}")
            if not ok:
                print(f"    tail        : {tail.strip()[:300]}")
            PRODUCER.write_bytes(original)
    finally:
        # Restore unconditionally, then VERIFY the restore.
        PRODUCER.write_bytes(original)
        back = hashlib.sha256(PRODUCER.read_bytes()).hexdigest()
        print()
        print(f"restore verified: {back[:16]} == {digest[:16]} -> {back == digest}")
        assert back == digest, "THE RESTORE FAILED -- the subject is left mutated"

    print()
    print(f"mutations_red = {red} of {len(MUTATIONS)}")
    for n, v in results:
        print(f"    {v:<14} {n}")
    print()
    print("CONFIRMING the baseline is green again after all restores")
    rc, tail = run_test(" or ".join(m[1] for m in MUTATIONS))
    print(f"  post-restore baseline: {'GREEN' if rc == 0 else f'RED (rc={rc})'}")
    if rc != 0:
        print(tail)
        return 3
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())
