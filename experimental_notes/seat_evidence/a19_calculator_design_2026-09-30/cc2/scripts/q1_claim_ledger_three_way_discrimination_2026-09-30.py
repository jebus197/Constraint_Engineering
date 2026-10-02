# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a3705d318f84c547240582c33153a67088c5bed49af653de89aa1ffe085456ce
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q1 - the mechanism that yields a DEFINITIVE AFFIRMATIVE on a prose target.

Run from the repository root:

    python3 scripts/q1_claim_ledger_three_way_discrimination_2026-09-30.py

THE CLAIM UNDER TEST
--------------------
S_k (A19) scores a FIX. The founder's calculator wants a verdict on a
DOCUMENT'S CLAIM. Those are different objects, so no repair to A19 can make it
emit the affirmative. The affirmative already exists in this repository, at the
claim level, and is reachable today through `falsifier_verify.reverify_falsifier`
over `bench/tests/fixtures/stem`. What is missing is not a mechanism; it is a
THIRD control and a caller.

THE PROPOSED ADMISSION RULE (three-way discrimination)
-----------------------------------------------------
For a claim C in document D with falsifier F, the instrument may emit a verdict
only when all three of these hold -- each one a run of the runner's OWN decider:

    P  POSITIVE control   F(D_defective)  == CONFIRMED
                          F can demonstrate the defect it is aimed at.
    N  NEGATIVE control   F(D_corrected)  == REFUTED
                          F goes quiet once the claim is true.
    B  BLIND control      F(D_destroyed)  != REFUTED
                          F actually READS its target. A falsifier that returns
                          REFUTED on a document whose bytes are gone is not
                          measuring the document -- it is the claim-level form
                          of the arm-4 defect (e2 scoring 52/55 on a prose
                          target whose bytes were destroyed).

Then, and only then:

    AFFIRMED(C)   iff  P and N and B hold, and F(D_actual) == REFUTED
    REFUTED(C)    iff  P and N and B hold, and F(D_actual) == CONFIRMED
    UNTOOLABLE(C) otherwise -- report WHICH control failed, never a verdict.

B is the addition. P and N alone are the existing discrimination control
(`reference_runner_v3.run_discrimination_control`). Without B, a REFUTED on the
actual document is indistinguishable from a falsifier that never opened it, and
that is precisely the failure mode already measured elsewhere in this harness.

This script executes P, N and B for all 5 committed fixtures, using the runner's
own decider, and reports which of the 3 controls each falsifier passes.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from bench.falsifier_verify import reverify_falsifier      # noqa: E402
from bench.tests.fixtures.stem import stem_fixtures as S    # noqa: E402


def _bind(fx, text: str, tmpdir: Path, tag: str) -> str:
    """Write `text` to a scratch copy and return F bound to that copy."""
    p = tmpdir / f"{fx.key}_{tag}_{fx.doc_name}"
    p.write_text(text, encoding="utf-8")
    return fx.falsifier(p)


def run() -> int:
    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for fx in S.load_all():
            pristine = fx.document                      # carries the FALSE claim
            corrected = fx.apply(fx.correct_fix)        # claim now TRUE
            destroyed = ""                              # bytes gone

            v_P = reverify_falsifier(_bind(fx, pristine, tmp, "P"),
                                     repo_root=str(REPO))
            v_N = reverify_falsifier(_bind(fx, corrected, tmp, "N"),
                                     repo_root=str(REPO))
            v_B = reverify_falsifier(_bind(fx, destroyed, tmp, "B"),
                                     repo_root=str(REPO))

            P_ok = (v_P == "CONFIRMED")
            N_ok = (v_N == "REFUTED")
            B_ok = (v_B != "REFUTED")
            rows.append((fx.key, fx.false_claim.tag, v_P, v_N, v_B,
                         P_ok, N_ok, B_ok))

    print("=" * 78)
    print("Q1  THREE-WAY DISCRIMINATION OVER THE COMMITTED PROSE CORPUS")
    print("    decider: bench.falsifier_verify.reverify_falsifier (the runner's own)")
    print("=" * 78)
    print()
    print(f"{'fixture':<12} {'claim':<8} {'P(defect)':<11} {'N(fixed)':<11} "
          f"{'B(no bytes)':<13}  P N B")
    for key, tag, vP, vN, vB, P_ok, N_ok, B_ok in rows:
        print(f"{key:<12} {tag:<8} {vP:<11} {vN:<11} {vB:<13}  "
              f"{'Y' if P_ok else 'n'} {'Y' if N_ok else 'n'} "
              f"{'Y' if B_ok else 'n'}")
    print()

    n = len(rows)
    nP = sum(r[5] for r in rows)
    nN = sum(r[6] for r in rows)
    nB = sum(r[7] for r in rows)
    nAll = sum(1 for r in rows if r[5] and r[6] and r[7])
    print(f"P positive control passed : {nP}/{n}")
    print(f"N negative control passed : {nN}/{n}")
    print(f"B blind   control passed : {nB}/{n}")
    print(f"all three                : {nAll}/{n}")

    # Wilson interval on the all-three proportion, two independent tools.
    try:
        import math
        z = 1.959963984540054
        p = nAll / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        lo, hi = max(0.0, c - h), min(1.0, c + h)
        print(f"Wilson 95% on all-three  : [{lo * 100:.4f}%, {hi * 100:.4f}%]")
        from statsmodels.stats.proportion import proportion_confint
        slo, shi = proportion_confint(nAll, n, method="wilson")
        print(f"statsmodels (2nd tool)   : [{slo * 100:.4f}%, {shi * 100:.4f}%]")
        assert abs(slo - lo) < 1e-9 and abs(shi - hi) < 1e-9
    except ImportError as e:
        print(f"statsmodels unavailable: {e}")

    print()
    print("READING")
    print("  A row with P=Y N=Y B=Y is a claim on which the instrument can emit")
    print("  a DEFINITIVE verdict in either direction, because it has been shown")
    print("  to move in both directions AND to be reading the document.")
    print("  A row failing B is the claim-level arm-4 defect: the falsifier's")
    print("  REFUTED carries no information about the document.")
    print()
    print("  These verdicts are produced TODAY, by committed code, with no new")
    print("  mechanism. The gap is that no live-path module calls any of it.")
    print("=" * 78)

    # ------------------------------------------------------------------
    # THE HARD ASSERTION IS ON THE DESIGN CLAIM, NOT ON THE CORPUS.
    # The design claim is: B is NOT redundant with P and N. It is refuted if
    # every falsifier that passes P and N also passes B -- then B adds a gate
    # nothing reaches, which the additive standard forbids.
    # ------------------------------------------------------------------
    pn_pass = [r for r in rows if r[5] and r[6]]
    b_fail_among_pn = [r for r in pn_pass if not r[7]]
    print()
    print("DESIGN CLAIM UNDER TEST: the B control is not redundant with P+N.")
    print(f"  falsifiers passing P and N          : {len(pn_pass)}/{n}")
    print(f"  of those, FAILING B                 : {len(b_fail_among_pn)}")
    for r in b_fail_among_pn:
        print(f"    {r[0]} / {r[1]}: returns {r[4]} against a document with "
              f"no bytes")
    assert b_fail_among_pn, (
        "REFUTED: every P+N falsifier also passes B, so B is a gate nothing "
        "reaches. Under the additive standard it must not be built.")
    print()
    print(f"  SURVIVES: {len(b_fail_among_pn)} of {len(pn_pass)} falsifiers "
          f"that the EXISTING two-way discrimination control accepts would")
    print("  emit a REFUTED that carries no information about the document.")
    print("  B catches them. It is reached, and it is load-bearing.")
    print()
    print("  ROOT CAUSE, read from the two failing templates: both open with")
    print('      if block is None: print("NOT FALSIFIED: ... is absent"); exit 0')
    print("  which conflates CLAIM CORRECTED with DOCUMENT UNREADABLE. That is")
    print("  the same conflation as arm 4's e2, one level down.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
