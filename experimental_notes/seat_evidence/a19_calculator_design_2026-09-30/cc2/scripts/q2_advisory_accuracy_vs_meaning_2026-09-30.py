# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2abc8b35a747058f49e6cc7e6542d8b404367a0e6dedfcb191ba71bf60808322
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q2 - make the advisory number ACCURATE and MEANINGFUL, without suppressing
it. Run from the repository root:

    python3 scripts/q2_advisory_accuracy_vs_meaning_2026-09-30.py

THE TWO PROPERTIES ARE DIFFERENT AND MUST BE MEASURED SEPARATELY.

  ACCURATE   every input measures the thing it names, and the arithmetic over
             those inputs is right. 0.9782 fails this: its e2 input scores the
             immune-memory suite, which is not the prose target. Removing that
             input yields an honestly-derived 1.0.

  MEANINGFUL the number MOVES when the thing it purports to summarise moves.
             A quantity constant across the whole space it claims to summarise
             carries zero information, whatever its provenance.

The founder's trap, stated in the brief: 1.0 is accurate and still
uninformative. This script MEASURES that -- it does not assert it -- by feeding
the instrument the committed ground truth: 5 fixes a sound reviewer should
ACCEPT and 5 a sound reviewer must REJECT, and asking whether the advisory
separates them.

DISCRIMINATION is the test for meaning, and it is the same test the falsifier
gate already applies to a falsifier. A number that cannot separate a correct
fix from a harmful one is not a score; it is a constant with a decimal point.
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from bench.reference_runner_v3 import (                          # noqa: E402
    _capture_baseline, compute_sk,
)
from bench.tests.fixtures.stem import stem_fixtures as S        # noqa: E402

#: THE BASELINE IS CAPTURED BY THE RUNNER'S OWN FUNCTION, not fabricated.
#: A hand-written {"ruff_violations": 0} would manufacture "new" diagnostics
#: for every listing the target already carries, and the rejections below would
#: be this script's artefact rather than the instrument's behaviour.
_BASE_CACHE: dict = {}


def base_for(fx):
    if fx.key not in _BASE_CACHE:
        _BASE_CACHE[fx.key] = _capture_baseline(fx.document, str(fx.doc_path))
    return _BASE_CACHE[fx.key]


def _blocks(patches) -> str:
    out = []
    for p in patches:
        out.append("<<<< SEARCH\n" + p.old + "\n====\n" + p.new
                   + "\n>>>> REPLACE\n")
    return "\n".join(out)


def advisory(fx, patches):
    """Return the advisory `computed_sk` the HIL would be shown."""
    r = compute_sk(
        fix_text=_blocks(patches), source=fx.document,
        source_path=str(fx.doc_path), baseline=base_for(fx), test_cmd=None,
        declared_target_kind="prose", score_prose_listings=True,
    )
    veto = r.gate_details.get("_prose_one_sided") or {}
    return r.tristate, veto.get("computed_sk"), veto.get("outcome")


def main() -> int:
    print("=" * 78)
    print("Q2  IS THE ADVISORY MEANINGFUL? MEASURED ON THE COMMITTED GROUND")
    print("    TRUTH: 5 fixes to ACCEPT, 5 fixes to REJECT.")
    print("=" * 78)
    print()
    print(f"{'fixture':<12} {'harm class':<44} "
          f"{'correct_fix':<14} {'harmful_fix':<14}")
    good, bad = [], []
    rows = []
    for fx in S.load_all():
        t_ok, a_ok, o_ok = advisory(fx, fx.correct_fix)
        t_no, a_no, o_no = advisory(fx, fx.harmful_fix)
        rows.append((fx.key, fx.harm_class, t_ok, a_ok, t_no, a_no))
        if a_ok is not None:
            good.append(a_ok)
        if a_no is not None:
            bad.append(a_no)
        print(f"{fx.key:<12} {fx.harm_class[:43]:<44} "
              f"{str(a_ok)+' '+str(t_ok):<14} {str(a_no)+' '+str(t_no):<14}")
    print()

    print("SEPARATION")
    print(f"  advisory on the 5 fixes a reviewer SHOULD accept : {good}")
    print(f"  advisory on the 5 fixes a reviewer MUST reject   : {bad}")
    overlap = sorted(set(good) & set(bad))
    print(f"  values occurring in BOTH sets                    : {overlap}")
    n_sep = sum(1 for g, b in zip(good, bad)
                if g is not None and b is not None and g > b)
    print(f"  fixtures where correct scores STRICTLY ABOVE harmful: "
          f"{n_sep} of {len(rows)}")
    if good and bad:
        print(f"  mean(correct) = {statistics.fmean(good):.6f}   "
              f"mean(harmful) = {statistics.fmean(bad):.6f}   "
              f"difference = {statistics.fmean(good)-statistics.fmean(bad):+.6f}")
    print()

    print("THE TRISTATE, WHICH IS WHAT ACTUALLY DECIDES")
    for key, hc, t_ok, a_ok, t_no, a_no in rows:
        flag = "SEPARATES" if t_ok != t_no else "does NOT separate"
        print(f"  {key:<12} correct -> {t_ok:<10} harmful -> {t_no:<10} "
              f"{flag}")
    t_sep = sum(1 for r in rows if r[2] != r[4])
    print(f"  the DECISION separates on {t_sep} of {len(rows)} fixtures.")
    print()

    print("=" * 78)
    print("READING")
    print("  Where the advisory takes the SAME value on a fix that should be")
    print("  accepted and a fix that must be rejected, it is not measuring the")
    print("  difference between them. Making its inputs honest (Q4) fixes its")
    print("  ACCURACY and leaves its MEANING untouched, because the inputs it")
    print("  is honest about -- ruff and bandit over fenced listings -- are not")
    print("  measuring the property in question. The harm classes here are")
    print("  SEMANTIC: the metrology harm edits a measured input so the")
    print("  document becomes self-consistent; the algorithms harm improves the")
    print("  metric under review while destroying correctness. No static sweep")
    print("  can see either.")
    print()
    print("  SO: accuracy is a repair to the INPUTS. Meaning requires a")
    print("  DIFFERENT MEASUREMENT, and the claim ledger of Q1 is one that")
    print("  demonstrably separates (5/5 on P and N).")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
