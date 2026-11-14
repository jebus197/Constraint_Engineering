#!/usr/bin/env python3
"""The 4 counts B181 owes: neither repair, each alone, and both.

★ WHY THIS SCRIPT EXISTS. B181, the entry on `parked_items()` being blind to
numerically-identified entries, recommends composing 2 repairs -- widening the
identifier pattern and honouring the parked file's settled boundary -- and says
so PROVISIONALLY, because `composability-requires-a-measurement` demands the 4
counts and not the argument. The entry also says *"`--measure` prints them"*.
**No such flag exists**, which was found by looking for it: `argparse` in
`scripts/morning_report_build_2026-10-12.py` declares `--since`, `--write` and
`--check` and nothing else. The promise is replaced by this producer, which is
what `measured-rate-travels-with-its-script` asks for anyway.

★ THE STANDARD BEING APPLIED, in the founder's words of 2026-10-02:
*"Composability doesn't mean composing two solutions just because they can be
composed. It means this principle should be applied where two composed
solutions demonstrably provide a better, more robust and/or more efficient
solution than either fix in isolation. Where a single fix out performs a
composed one, that fix should continue to be preferred."*

★ THE NAMED PROPERTY IS **SETTLED ITEMS SHOWN TO HIM**, and lower is better.
That is the fault B181 reports: the morning report presented him parked items
whose questions were already answered. The composition is justified only if it
shows him strictly fewer settled items than EITHER half alone.

★ AND THE MEASUREMENT MUST ALSO SHOW NOTHING LIVE IS LOST, because a repair
that drops a live item is worse than the fault. The second column counts live
items retained; it must not fall.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

# `_cli_help` lives in scripts/. Locate it rather than assume a depth, the shape
# that stopped 13 scripts importing on 2026-09-24.
#
# ★ WHY, MEASURED 2026-11-14. `scripts/measurement_scripts_only_2026-09-11.py
# --run` reported `1 of 393 did not answer --help cleanly` and this was the 1:
# it has no parser, so `--help` ran the whole measurement and exited 0. An exit
# code is not an answer -- that is the precise defect `_cli_help` was written
# for on 2026-09-11, when 30 scripts passed the same check the same way.
for _cand in (Path(__file__).resolve().parent,
              *Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"

#: The pattern BEFORE the 2026-11-13 widening: capitals required before digits.
NARROW = re.compile(r"\b([A-Z]{1,2}\d{1,4}[a-z]?)\b")


def _mrb():
    spec = importlib.util.spec_from_file_location(
        "mrb_measure", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb_measure"] = m
    spec.loader.exec_module(m)
    return m


def _headings(text: str, honour_boundary: bool) -> list[str]:
    out = []
    for line in text.splitlines():
        if honour_boundary and re.match(r"^#\s+Settled\b", line, re.I):
            break
        if line.startswith("## "):
            out.append(line[3:].strip())
    return out


def _is_settled(heading: str, states, oracle) -> bool:
    """Is this heading's question already answered, per the TASK LIST?

    ★ THE FIRST VERSION OF THIS ORACLE WAS CIRCULAR AND IS REPLACED RATHER THAN
    QUIETLY FIXED. It defined *settled* as *below the parked file's settled
    boundary*, which is one of the 2 treatments under test -- so the
    boundary-alone arm scored 0 by construction and the comparison was decided
    by the definition rather than by the data. That is the failure this project
    records as a figure answering a different question, and it would have
    produced a confident, wrong verdict on his composability standard.

    ★ THE REPLACEMENT IS INDEPENDENT OF BOTH TREATMENTS. A heading is settled
    when the task list records every entry it names as DONE or WITHDRAWN. The
    identifiers are extracted with the WIDEST available pattern for EVERY arm,
    including the arms whose own filter uses the narrow one -- the oracle must
    see what the narrow filter misses, or it cannot score the narrow filter's
    misses as misses.

    A heading naming NO known entry is NOT settled, which is the same
    conservative rule `parked_items` itself uses: absence of a marker is not
    evidence of closure.
    """
    closed = {k for k, (st, _s) in states.items() if str(st).upper() in {"DONE", "WITHDRAWN"}}
    named = set(oracle.findall(heading)) & set(states)
    return bool(named) and named <= closed


def _run(text: str, states, wide: bool, boundary: bool) -> list[str]:
    pat = _mrb_pattern if wide else NARROW
    closed = {k for k, (st, _s) in states.items() if str(st).upper() in {"DONE", "WITHDRAWN"}}
    known = set(states)
    live = []
    for h in _headings(text, boundary):
        named = set(pat.findall(h)) & known
        if named and named <= closed:
            continue
        live.append(h)
    return live


def main() -> int:
    m = _mrb()
    global _mrb_pattern
    _mrb_pattern = m._PARKED_CODE
    text = PARKED.read_text(encoding="utf-8")

    triage = importlib.util.spec_from_file_location(
        "parked_triage_measure",
        REPO / "scripts" / "has_he_already_ruled_on_the_parked_2026-10-13.py")
    tm = importlib.util.module_from_spec(triage)
    sys.modules["parked_triage_measure"] = tm
    triage.loader.exec_module(tm)
    states = tm.task_states()

    arms = [
        ("neither repair      ", False, False),
        ("widening alone      ", True, False),
        ("boundary alone      ", False, True),
        ("BOTH (composed)     ", True, True),
    ]
    print("  THE NAMED PROPERTY IS SETTLED ITEMS SHOWN TO HIM. Lower is better.")
    print(f"  {'arm':22} {'shown':>6} {'settled shown':>14} {'live shown':>11}")
    results = {}
    for label, wide, boundary in arms:
        shown = _run(text, states, wide, boundary)
        n_settled = sum(1 for h in shown if _is_settled(h, states, _mrb_pattern))
        results[label.strip()] = (len(shown), n_settled, len(shown) - n_settled)
        print(f"  {label:22} {len(shown):>6} {n_settled:>14} {len(shown)-n_settled:>11}")

    print()
    n, b, w, both = (results["neither repair"], results["boundary alone"],
                     results["widening alone"], results["BOTH (composed)"])
    print(f"  settled shown: neither {n[1]}, widening alone {w[1]}, "
          f"boundary alone {b[1]}, composed {both[1]}")
    beats_both = both[1] < w[1] and both[1] < b[1]
    ties_best = both[1] == min(w[1], b[1])
    print()
    if beats_both:
        print("  VERDICT: the COMPOSED fix dominates each half on the named property.")
        print("           Composition is justified under his 2026-10-02 standard.")
    elif ties_best:
        best = "widening alone" if w[1] <= b[1] else "boundary alone"
        print(f"  VERDICT: the composed fix only TIES the better half ({best}).")
        print("           His standard PREFERS the single fix where it performs as well,")
        print("           so composition is NOT justified on this property alone.")
    else:
        print("  VERDICT: a single fix OUTPERFORMS the composed one. Prefer the single fix.")

    print()
    live_counts = {k: v[2] for k, v in results.items()}
    lost = live_counts["neither repair"] - live_counts["BOTH (composed)"]
    print(f"  live items shown: neither {live_counts['neither repair']}, "
          f"composed {live_counts['BOTH (composed)']}  (difference {lost})")
    print("  A repair that drops a LIVE item is worse than the fault it fixes, so this")
    print("  difference is reported beside the gain rather than left to be assumed.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
