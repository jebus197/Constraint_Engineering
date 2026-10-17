#!/usr/bin/env python3
"""If `sk_score_prose_listings` defaulted to true, what would change?

TASK A19. HIS DESIGN POINT, 2026-09-10: a prose input should be marked
inadmissible *"while still solving any computationally reducible elements within
that prose! This is STEM."* The flag that does this exists, defaults to FALSE,
and the question left open was whether to flip it.

THE HISTORY MATTERS, because the answer changed. On 2026-09-22 the flag was
measured with FULL scoring and all 5 of the acceptance suite's harmful fixes
scored ADMISSIBLE above break-even and moved R_k down -- Property 1 failed 5/5,
Property 2 failed 10/10. The flag was therefore made VETO-ONLY: gates may REJECT
but never admit. On 2026-10-17 the decision was moved from the TARGET to the
individual FIX, so a fix that edits only prose is unscored even in a document
full of code.

WHAT THIS MEASURES. The suite's 5 STEM fixtures, each with a correct fix and a
harmful one, through `compute_sk` with the flag off and on.

MEASURED 2026-10-17, after both repairs:
  * fixes ADMITTED with the flag on            : 0 of 10
  * CORRECT fixes rejected with the flag on    : 0 of 5
  * HARMFUL fixes rejected with the flag on    : 3 of 5
  * harmful fixes rejected with the flag off   : 0 of 5

So the flip strictly dominates on the named property: it convicts 3 harmful
fixes the current default lets pass as unscored, and convicts no correct fix.

WHY IT IS STILL NOT FLIPPED HERE. The 3 shakedown legs that converged -- the
programme's success criterion -- all ran with the flag OFF, on a prose target.
Flipping it now would mean the next leg is not comparable with those 3, and
comparability across a programme of study is not a preference. The flip belongs
at a programme boundary, which is the founder's call, and this script exists so
that call is made against numbers.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from _cli_help import answer_help  # noqa: E402


def main() -> int:
    answer_help(__doc__, __file__)
    import bench.reference_runner_v3 as runner
    from bench.tests.test_prose_acceptance_stem import (
        FIXTURES, _fix_text, _real_baseline)

    items = list(FIXTURES.values()) if isinstance(FIXTURES, dict) \
        else list(FIXTURES)
    if not items:
        print("no acceptance fixtures loaded. Measurement void.")
        return 3

    print(f"THE ACCEPTANCE FIXTURES, {len(items)} of them, EACH WAY")
    print(f"  {'fixture':<12} {'fix':<8} {'flag OFF':<11} {'flag ON':<11} "
          f"reaches a listing")
    rows = []
    for f in items:
        for kind, patches in (("correct", f.correct_fix),
                              ("harmful", f.harmful_fix)):
            text = _fix_text(f, patches, f.doc_path)
            touches, _ = runner._fix_touches_reducible(
                text, f.document, str(f.doc_path))
            verdicts = {}
            for flag in (False, True):
                r = runner.compute_sk(
                    text, f.document, str(f.doc_path),
                    baseline=_real_baseline(f), score_prose_listings=flag)
                verdicts[flag] = r.tristate
            rows.append((f.key, kind, verdicts[False], verdicts[True], touches))
            print(f"  {f.key:<12} {kind:<8} {verdicts[False]:<11} "
                  f"{verdicts[True]:<11} {touches}")

    admitted = [r for r in rows if r[3] == runner.SK_ADMISSIBLE]
    correct_rej = [r for r in rows
                   if r[1] == "correct" and r[3] == runner.SK_REJECTED]
    harmful_rej_on = [r for r in rows
                      if r[1] == "harmful" and r[3] == runner.SK_REJECTED]
    harmful_rej_off = [r for r in rows
                       if r[1] == "harmful" and r[2] == runner.SK_REJECTED]
    n_correct = sum(1 for r in rows if r[1] == "correct")
    n_harmful = sum(1 for r in rows if r[1] == "harmful")

    print("\nWHAT FLIPPING THE DEFAULT WOULD CHANGE")
    print(f"  fixes ADMITTED with the flag on          : "
          f"{len(admitted)} of {len(rows)}")
    print(f"  CORRECT fixes rejected with the flag on  : "
          f"{len(correct_rej)} of {n_correct}")
    print(f"  HARMFUL fixes rejected with the flag on  : "
          f"{len(harmful_rej_on)} of {n_harmful}")
    print(f"  HARMFUL fixes rejected with the flag off : "
          f"{len(harmful_rej_off)} of {n_harmful}")
    if n_harmful:
        from statsmodels.stats.proportion import proportion_confint
        import scipy.stats as st
        k = len(harmful_rej_on)
        w = proportion_confint(k, n_harmful, method="wilson")
        b = proportion_confint(k, n_harmful, method="beta")
        cp_hi = 1.0 if k == n_harmful else float(
            st.beta.ppf(0.975, k + 1, n_harmful - k))
        print(f"    harmful caught: {k} of {n_harmful} = "
              f"{100*k/n_harmful:.4f}%")
        print(f"      Wilson          [{w[0]*100:.4f}%, {w[1]*100:.4f}%]")
        print(f"      Clopper-Pearson [{b[0]*100:.4f}%, {b[1]*100:.4f}%]")
        print(f"      scipy agrees on the upper bound: "
              f"{abs(b[1] - cp_hi) < 1e-9}")

    print("\nVERDICT")
    dominates = (not admitted and not correct_rej
                 and len(harmful_rej_on) > len(harmful_rej_off))
    if dominates:
        print("  the flip DOMINATES on the named property: it convicts harmful")
        print("  fixes the current default lets pass, admits nothing, and")
        print("  convicts no correct fix.")
    else:
        print("  the flip does NOT dominate; do not quote it as an improvement.")
    print("  IT IS STILL NOT APPLIED HERE. The 3 converged shakedown legs all")
    print("  ran with the flag OFF on a prose target, so flipping it now makes")
    print("  the next leg incomparable with them. The flip belongs at a")
    print("  programme boundary, which is the founder's call.")
    return 0 if dominates else 1


if __name__ == "__main__":
    raise SystemExit(main())
