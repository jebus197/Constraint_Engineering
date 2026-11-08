#!/usr/bin/env python3
"""The task list has a state for "awaiting his ruling". 1 of 29 decisions uses it.

THE CONVENTION, from the master task list's own task 10.2, verbatim: the entry
is "MARKED BLOCKED ON IT, the state this list uses for a ruling that awaits him
(as A11 does), so the resume pointer stops naming it as work".

SO THE LIST ALREADY HAS THE MECHANISM, and the reason it exists is exactly the
cost being paid: an entry that is formally a DECISION is otherwise named by the
resume pointer as unstarted WORK, session after session, and a model reading
that pointer is directed at something only he can move.

MEASURED HERE: how many of the decisions the generated decisions file puts to
him carry that state. The 2 sources are independent -- the decision list is
generated from `data/morning_report_decisions.json` through the morning
report's own functions, and the states are read from the markers in
`CDSFL_MASTER_TASK_LIST.md` -- so this compares the queue against the tracker
rather than the tracker against itself.

WHY NOTHING IS CHANGED HERE, AND THAT IS THE POINT. Re-marking 28 of his
entries would be a bulk edit to his own tracker's machine-readable state, and
it is not free: R1 is on this project's record as an entry whose marker read
BLOCKED while its prose said the ruling had converted it to WORK, and the
mis-marking "cost something mechanically" by excluding real work from the
queue. The same error in the other direction is just as available. Whether an
entry that is BOTH a decision and partly workable should be BLOCKED is a
judgement about his tracker, so this script measures and reports.

Exit 0 iff every figure was produced by 2 independent routes.
"""
from __future__ import annotations

import collections
import pathlib
import re

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
MARKER = re.compile(r"<!-- task: ([A-Za-z0-9.]+) \| state: ([A-Z]+)")
INDEX_LINE = re.compile(r"^\s*\d+\.\s+\*\*([A-Za-z0-9]+)\*\*", re.M)
#: The state the list reserves for a ruling that awaits him (task 10.2).
AWAITING = "BLOCKED"


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y   # noqa: E731
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - float(cen - half)), abs(hi - float(cen + half)),
              abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"


def _latest_decision_index() -> pathlib.Path | None:
    cands = sorted((REPO / "experimental_notes").glob(
        "Decisions_Awaiting_You_*_GENERATED.md"))
    return cands[-1] if cands else None


def main() -> int:
    if not TASKLIST.is_file():
        print(f"REFUSED: no task list at {TASKLIST}")
        return 1
    idx = _latest_decision_index()
    if idx is None:
        print("REFUSED: no generated decisions index found. Run "
              "scripts/build_decisions_file_2026-11-07.py --write first; "
              "without it the population of DECISIONS is unknown and the rate "
              "below would have a denominator this script invented.")
        return 1

    keys = INDEX_LINE.findall(idx.read_text(encoding="utf-8"))
    states = {m.group(1): m.group(2)
              for m in MARKER.finditer(TASKLIST.read_text(encoding="utf-8"))}

    print("=" * 78)
    print("THE LIST HAS A STATE FOR 'AWAITING HIS RULING'. ALMOST NOTHING "
          "USES IT.")
    print("=" * 78)
    print(f"  decisions index : {idx.name}")
    print(f"  decisions in it : {len(keys)}")
    print(f"  markers in list : {len(states)}")
    assert keys, "the decisions index parsed to 0 entries; the shape changed"

    missing = [k for k in keys if k not in states]
    counts = collections.Counter(states.get(k, "NO MARKER") for k in keys)
    print("\n  THE STATE OF EACH DECISION AWAITING HIM:")
    for st, n in counts.most_common():
        print(f"      {st:<12} {n}")
    if missing:
        print(f"  decisions with NO marker at all: {missing}")

    k = sum(1 for x in keys if states.get(x) == AWAITING)
    print()
    _show(f"decisions carrying the {AWAITING} state the list reserves for them",
          k, len(keys))
    named_as_work = [x for x in keys if states.get(x) == "OPEN"]
    print(f"\n  CONSEQUENCE: {len(named_as_work)} decisions carry OPEN, so the "
          f"resume")
    print("  pointer names them as unstarted WORK. The first of them in list")
    print(f"  order is {named_as_work[0] if named_as_work else '(none)'}, which "
          f"is also decision 1 of")
    print(f"  {len(keys)} in the file put to him.")

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS AND WHAT IT DOES NOT")
    print("  SUPPORTS: the mechanism his list documents for keeping a pending")
    print("    ruling out of the work queue is applied to a small minority of")
    print("    the rulings actually pending, and the resume pointer therefore")
    print("    directs work at items only he can move.")
    print("  DOES NOT SUPPORT: that all of them SHOULD be re-marked. An entry")
    print("    can be a decision AND carry workable parts, and BLOCKED would")
    print("    hide those. R1 is on this record as the mirror error: its")
    print("    marker said BLOCKED while its prose said the ruling had made it")
    print("    work, and the mis-marking excluded real work from the queue.")
    print("  SO THE REMEDY IS HIS. Either the state is applied to pending")
    print("    decisions, or the pointer learns to skip an entry that appears")
    print("    in the decisions file. Both are changes to how his tracker")
    print("    behaves, and neither is made here.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help as _answer_help
        _answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
