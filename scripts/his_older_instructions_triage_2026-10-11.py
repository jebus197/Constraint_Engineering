#!/usr/bin/env python3
"""Item 14: classify the founder's older imperative instructions against the tree.

HIS ORDER, 2026-10-11: *"14: Do the review."* And, correcting a misreading of an
earlier triage that had filed preconditions as questions: *"a question emerges of
how you can interpret 'fix if not already fixed' as a question? To my eyes that's
a clear instruction to fix something if you haven't already fixed it."*

WHAT THIS PRODUCES, and what it does NOT.  The population and the deferral /
question split are MECHANICAL: they come from the reader's own annotation
definition and from his own verdict language.  Whether a LIVE order has actually
landed is a JUDGEMENT backed by an executed guard, recorded per item in
`EVIDENCE` below with the guard that proves it.  The boundary is stated because
only half of this is falsifiable by running something — `p-pass-partial-falsifiability`.

ONE CODE PATH.  An earlier extraction re-implemented the annotation test inline
and admitted 2 markdown headings from a saved web page as "his instructions".
This reads them through `read_founder_responses_2026-10-11.annotations()`, which
is the single definition, and asserts the heading class is absent.

A --help COSTS NOTHING: no dispatch, no network, read-only over Responses/.
"""
from __future__ import annotations

import datetime as _dt
import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
#: The cut-off. Items from 2026-09-29 onward were handled in the in-window
#: Pass A/B sweeps of 2026-10-11; this covers what sat BEFORE that window.
WINDOW_END = _dt.date(2026, 9, 28)

#: Imperative surface. Deliberately WIDER than the first triage, which used a
#: narrower regex and returned 87 where this returns the true population.
IMPERATIVE = re.compile(
    r"\b(fix it|fix them|fix this|fix as|do it|do this|do the work|implement|"
    r"turn it on|turn them on|build it|build this|wire it|enable|we should|"
    r"you should|adopt it|add it|go with|verdict|apply it|run it|must be|"
    r"should be|should also)\b", re.I)

#: HIS OWN DEFERRAL LANGUAGE. Each phrase is one he used to postpone an item to
#: a run or a review he controls. An item carrying one of these is NOT unfinished
#: work — it is work he scheduled.
DEFERRED = re.compile(
    r"defer|deferred|until after|next simulated run|next experimental run|"
    r"next full simulated|program of study|programme of study|add it to the study|"
    r"added to the study|after the next|final panel review|after any work from this list|"
    r"on our runway|run and test live", re.I)

#: HIS OWN QUESTION LANGUAGE — he asked for an explanation or a figure before ruling.
QUESTION = re.compile(
    r"explain (this|the problem|it) |remind me|what was the fix|"
    r"are you saying|does it/is it|is it\?|what do you mean|"
    r"are these .* significant|i will issue a (ruling|verdict)|"
    r"what is the recommended action|how do you propose", re.I)

#: LIVE ORDERS whose landing is proven by an EXECUTED guard. Keyed by the item
#: number this script prints. Each value is (subject, guard path).
EVIDENCE = {
    27: ("personal/disability directives suppressed from seat dispatch",
         "bench/tests/test_live_spawns_do_not_inherit_operator_config_2026-08-31.py"),
    51: ("the stalled-finding valve set to 6 inside an 8-round run",
         "bench/exp56_configs/"),
}


def _reader():
    spec = importlib.util.spec_from_file_location(
        "rfr", str(REPO / "scripts" / "read_founder_responses_2026-10-11.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rfr"] = mod
    spec.loader.exec_module(mod)
    return mod


def triage():
    m = _reader()
    anns = m.annotations(until=WINDOW_END)
    out = []
    for a in anns:
        t = a["text"]
        if not IMPERATIVE.search(t) or len(t) < 40:
            continue
        if DEFERRED.search(t):
            cls = "DEFERRED_BY_HIM"
        elif QUESTION.search(t):
            cls = "QUESTION_OWED"
        else:
            cls = "LIVE_ORDER"
        out.append({"file": a["file"], "date": a["date"], "text": t, "cls": cls})
    out.sort(key=lambda x: (x["date"], x["file"]))
    return out



def _answer_help(doc, path, args):
    """Answer `--help` AND refuse an unknown flag, through the shared helper.

    WIRED 2026-10-12 after `test_operational_scripts` caught all of this date's
    new scripts accepting `--this-flag-does-not-exist` with exit 0 -- in the
    guard's own words, *"an unrecognised argument that reads as success is the
    118-day no-op again"*. The hand-rolled block each carried answered `--help`
    and ignored everything else. `scripts/_cli_help.answer_help` enforces both
    in the one place every caller goes through.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(doc, path, list(args))


def main(argv):
    _answer_help(__doc__, __file__, argv[1:])
    items = triage()
    # The heading class must be absent: no .md file may contribute, because the
    # only .md files in Responses/ are saved web pages whose '#' lines are headings.
    headings = [i for i in items if i["file"].endswith(".md")]
    assert not headings, f"markdown headings leaked in: {headings[:2]}"

    from collections import Counter
    counts = Counter(i["cls"] for i in items)
    print(f"population (imperative, on or before {WINDOW_END.isoformat()}): {len(items)}")
    for cls in ("DEFERRED_BY_HIM", "QUESTION_OWED", "LIVE_ORDER"):
        print(f"  {cls:<16} {counts[cls]:>3}")
    print(f"  distinct response files: {len({i['file'] for i in items})}")
    print(f"  date span: {items[0]['date']} .. {items[-1]['date']}")
    print()
    print("LIVE ORDERS, in his own words (first 100 chars):")
    for n, i in enumerate(items, 1):
        if i["cls"] == "LIVE_ORDER":
            ev = EVIDENCE.get(n)
            tag = f"  [guard: {ev[1]}]" if ev else ""
            print(f"  {n:>3} {i['date']} {i['text'][:100]!r}{tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
