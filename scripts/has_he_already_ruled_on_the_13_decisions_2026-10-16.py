#!/usr/bin/env python3
"""For each of the 13 DECISIONS in the morning report, has he already ruled?

HIS QUESTION, 2026-10-16: *"Of the 13 decisions, are you certain none of these
are items I have previously ruled on? This seems an unusually large HIL queue,
which traditionally has been a strong indicator of mechanical, and/or
implementation/process failure."*

HE HAS ASKED THIS BEFORE AND AN INSTRUMENT ALREADY EXISTS. On 2026-10-13:
*"Did I not rule on these already? ... Give me a fresh morning report of anything
still requiring my ruling. Check first if I haven't ruled on them already."*
`scripts/has_he_already_ruled_on_the_parked_2026-10-13.py` was written for that
and found 14 of 21 PARKED items already settled. It covers the PARKED list only.
Nothing covered the DECISIONS list, and the decisions list was not checked before
the 13-item queue was delivered. That omission is the process failure he is
pointing at, and it is a REPEAT rather than a first occurrence.

THIS SCRIPT REUSES THE PROVEN MATCHER rather than re-implementing it: `IDENT_RE`,
`task_states()`, `annotations()` and `CLOSED_MARKERS` are imported from the
2026-10-13 instrument, including its recorded fix for "A13/A14" matching as one
token when the task list keys them separately.

WHAT IT DECIDES MECHANICALLY AND WHAT IT REFUSES TO. A task marker reading DONE
or WITHDRAWN is mechanical and decides the item. Everything else is EXTRACTED and
printed for reading, because the discriminator that matters cannot be pattern
matched: a decision body quoting "your ruling" may be quoting the ruling that
CREATED the item (context) or the ruling that SETTLES the question being asked
(already answered). Those read identically to a regex. So the script surfaces
every ruling sentence per item, with its identifiers and task states, and the
classification is made against that text rather than from recollection.

WHAT IT FOUND, 2026-10-16, AND 2 OF ITS OWN ERRORS.

  * 5 of the 13 should not have been put to him as decisions, 38.4615%, 95%
    Wilson [17.7097%, 64.4771%], Clopper-Pearson [13.8579%, 68.4222%]. 7 of 13
    were wrong AS FRAMED, 53.8462% [29.1438%, 76.7939%]. 6 are legitimately open.

  * THE IDENTIFIER CHANNEL IS BLIND. 7 of his 555 annotations carry any
    identifier at all, 1.2613%, 95% Wilson [0.6123%, 2.5803%], and all but one
    are model version numbers (5.3, 4.8, 5.5, 4.7) or "K3". Exactly ONE is a
    genuine task code. He rules in PROSE, by subject. So "0 annotation matches"
    is not evidence he has not ruled; it is evidence the matcher cannot see his
    rulings, and that bound applies to the 2026-10-13 parked script too.

  * THE MECHANICAL CAUSE IS THE MARKER SCHEMA. Across 108 task markers the
    fields are exactly `task`, `state`, `status` and `evidence`. `state` is
    lifecycle (OPEN/DONE/BLOCKED/WITHDRAWN) and `status` is build state
    (PROPOSED/BUILT/TESTED/COMMITTED/ENABLED). NOTHING records whether he has
    RULED. A ruling he gives that is not immediately executed therefore leaves
    its item indistinguishable from one he has never seen. R1 is the proof: he
    ruled "restart it" on 2026-08-07 and again on 2026-09-06, and 70 days later
    the marker still reads BLOCKED/PROPOSED and the item still presents as a
    decision.

  * 2 ERRORS OF MINE, CAUGHT BY P-PASSING THIS SCRIPT'S OWN OUTPUT. First I
    reported that 7 of 8 surfaced defects had a status saying they were closed.
    That was a SUBSTRING BUG: my closure test matched "NOT FIXED" because it
    contains "FIXED". The honest figure is 1 of 8. Second, and consequently, the
    generator's defect filter is largely behaving -- 7 of the 8 genuinely say NOT
    FIXED -- so the already-ruled items are NOT coming from that filter, and my
    first diagnosis pointed at the wrong component.

  * THE HISTORICAL COMPARISON IS WEAK AND IS LABELLED SO. The only prior figure
    available is "6 decisions" on 2026-10-13, which comes from the 2026-10-13
    script's DOCSTRING -- prose -- and the 2026-10-12 generated report could not
    be recovered from git to re-count. So 13 against 6 is quoted, not measured,
    and no growth rate should be read off it.

It dispatches nothing and costs nothing.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from _cli_help import answer_help                                  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_parked", REPO / "scripts" / "has_he_already_ruled_on_the_parked_2026-10-13.py")
_P = importlib.util.module_from_spec(_spec)
try:
    _spec.loader.exec_module(_P)
except SystemExit:
    pass

REPORT = REPO / "experimental_notes" / "Morning_Report_2026-10-16_GENERATED.md"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"

RULING_RE = re.compile(
    r"[^.]*?\b(your ruling|you ruled|he ruled|already ruled|his ruling|"
    r"founder ruling|on his instruction|on your instruction|you approved|"
    r"he approved|ruled twice|ruled it)\b[^.]*\.", re.I)


def decisions_from_report() -> dict[int, tuple[str, str]]:
    if not REPORT.is_file():
        return {}
    t = REPORT.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"\n### (\d+)\. ", t)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        body = parts[i + 1]
        # stop at the next '## ' section so section 2 is not swallowed
        body = re.split(r"\n## ", body)[0]
        out[int(parts[i])] = (body.splitlines()[0].strip(), body)
    return out


def wilson_and_cp(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, alpha=0.05, method="beta")
    import scipy.stats as st
    z = st.norm.ppf(0.975)
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    assert max(abs(lo_w - (c - h)), abs(hi_w - (c + h))) < 1e-9, "wilson routes disagree"
    return (f"{100*k/n:.4f}%  Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%] "
            f"(2 routes agree)  Clopper-Pearson [{100*lo_c:.4f}%, {100*hi_c:.4f}%]")


def main() -> int:
    items = decisions_from_report()
    states = _P.task_states()
    anns = _P.annotations()
    detail = json.loads(DETAIL.read_text()) if DETAIL.is_file() else {}

    print(f"decisions parsed: {len(items)}   task markers: {len(states)}   "
          f"annotations: {len(anns)}")
    print("=" * 78)

    decided_done, needs_reading = [], []
    for n in sorted(items):
        head, body = items[n]
        idents = [part for tok in _P.IDENT_RE.findall(head)
                  for part in tok.split("/")]
        done = [i for i in idents
                if states.get(i, ("", ""))[0] in ("DONE", "WITHDRAWN")]
        open_ = [(i, states[i]) for i in idents if i in states
                 and states[i][0] not in ("DONE", "WITHDRAWN")]
        closed_marker = [m for m in _P.CLOSED_MARKERS if m.lower() in body.lower()]
        rulings = sorted({m.group(0).strip() for m in RULING_RE.finditer(body)})
        ann_hits = [a for a in anns
                    if any(re.search(rf"\b{re.escape(i)}\b", a.get("text", ""))
                           for i in idents)] if idents else []

        print(f"\n{n:>2}. {head[:96]}")
        print(f"    identifiers      : {idents or '(none)'}")
        print(f"    task state       : "
              f"{ {i: states.get(i, ('ABSENT',''))[0] for i in idents} or '(no marker)'}")
        if done:
            print(f"    *** DONE/WITHDRAWN IN THE TASK LIST: {done} ***")
            decided_done.append(n)
        if closed_marker:
            print(f"    closed-marker in its own body: {closed_marker}")
        print(f"    his annotations naming an identifier: {len(ann_hits)}")
        if rulings:
            print(f"    RULING SENTENCES IN ITS OWN BODY ({len(rulings)}), "
                  f"for reading:")
            for r in rulings:
                print(f"      - {r[:220]}")
        else:
            print("    no ruling language in its own body")
        if n not in decided_done:
            needs_reading.append(n)

    print()
    print("=" * 78)
    print("MECHANICAL VERDICT ONLY")
    print("=" * 78)
    print(f"  decided by a DONE/WITHDRAWN task marker : {len(decided_done)} "
          f"-> {decided_done}")
    print(f"  not decidable mechanically, read above   : {len(needs_reading)}")
    if items:
        print(f"  share mechanically settled: "
              f"{wilson_and_cp(len(decided_done), len(items))}")
    print()
    print("  THIS IS NOT THE ANSWER TO HIS QUESTION. A marker decides an item;")
    print("  a quoted ruling does not, because the ruling that CREATED an item")
    print("  and the ruling that SETTLES it read identically to a regex. The")
    print("  sentences above are printed so the classification is made against")
    print("  the text rather than from recollection.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
