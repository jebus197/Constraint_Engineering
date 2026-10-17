#!/usr/bin/env python3
"""B25: derive the SET of his annotations a task entry actually cites.

WHY THIS EXISTS. Entry C0 reports an audit of 302 of his annotations finding 20
confirmed gaps, 12 of them rulings never carried out. That audit produced the
whole C-series. It NAMES NO PRODUCING SCRIPT, so its figures are a claim about
evidence rather than evidence -- the shape his ruling of 2026-09-04 forbids --
and its coverage cannot be mapped onto the register's 318 UNCONFIRMED
annotation tickets. The register's window holds 306 against C0's claimed 302,
and those 4 cannot be identified, because a count cannot say WHICH items it
covered and a set can.

WHAT THIS DOES INSTEAD OF RESURRECTING C0's VERDICTS. It does not try to
re-derive what the audit concluded, which would be guessing at a judgement
nobody recorded. It derives a DIFFERENT fact that is checkable from committed
artefacts: WHICH annotations a task-list entry quotes. An entry that quotes his
words under a heading such as HIS WORDS or HIS RULING is tracking that
annotation, and anyone can verify the match by reading both.

THREE OUTCOMES, AND THE MIDDLE ONE IS THE POINT.

  CITED       -- the annotation's text appears inside a task-list entry, and
                 the annotation is distinctive enough that the match means
                 something. The entry that cites it is named, so a register
                 close can carry a verification anyone can check.
  UNDECIDABLE -- the annotation is too short to attribute. His verdicts repeat
                 verbatim: "Same answer", "Same answers!", "Do it." A substring
                 match on those proves nothing, because several different
                 annotations share one text. Calling them CITED would be the
                 flattering direction, and C0 itself records that a first
                 attempt to answer him failed in exactly that direction when a
                 word-overlap measure reported 198 of 199 covered while
                 answering the wrong question.
  NOT CITED   -- distinctive and absent. These are the genuine remainder.

THE DISTINCTIVENESS THRESHOLD IS REPORTED AT SEVERAL VALUES rather than picked
and hidden, because a threshold chosen to make a figure look good is a tuned
constant pretending to be a finding.

Costs nothing: reads local text and dispatches to no model.

Usage:
  which_annotations_are_cited_by_an_entry_2026-10-17.py
  which_annotations_are_cited_by_an_entry_2026-10-17.py --min-tokens 8
  which_annotations_are_cited_by_an_entry_2026-10-17.py --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
READER = ROOT / "scripts" / "read_founder_responses_2026-10-11.py"
WINDOW_FROM = "2026-10-01"
DEFAULT_MIN_TOKENS = 6


def _reader():
    spec = importlib.util.spec_from_file_location("_fr", READER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _norm(text: str) -> str:
    return " ".join(str(text).split()).strip().lower()


def _proportion(k, n):
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    if n == 0:
        return None
    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": 100.0 * k / n,
            "wilson": (w[0] * 100, w[1] * 100),
            "cp": (b[0] * 100, b[1] * 100),
            "agrees": abs(b[1] - cp_hi) < 1e-9}


def _say(label, p):
    if p is None:
        print(f"  {label}: no denominator")
        return
    print(f"  {label}: {p['k']} of {p['n']} = {p['pct']:.4f}%")
    print(f"      Wilson [{p['wilson'][0]:.4f}%, {p['wilson'][1]:.4f}%]  "
          f"Clopper-Pearson [{p['cp'][0]:.4f}%, {p['cp'][1]:.4f}%]  "
          f"scipy agrees {p['agrees']}")


def entry_bodies() -> dict:
    """Each task entry's own text, keyed by identifier."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import task_list_markers as markers
    lines = LIST.read_text(encoding="utf-8").splitlines()
    out = {}
    for entry in markers.parse_entries():
        out[entry.ident] = _norm(lines[entry.line_no - 1])
    return out


def classify(min_tokens: int = DEFAULT_MIN_TOKENS) -> dict:
    reader = _reader()
    bodies = entry_bodies()
    rows = [r for r in reader.annotations()
            if str(r.get("date", "")) >= WINDOW_FROM]

    #: HOW MANY ANNOTATIONS SHARE ONE TEXT. A text carried by more than 1
    #: annotation cannot be attributed by matching it, however long it is.
    seen = {}
    for r in rows:
        seen.setdefault(_norm(r["text"]), []).append(r)

    cited, undecidable, absent = [], [], []
    for r in rows:
        text = _norm(r["text"])
        tokens = len(text.split())
        duplicated = len(seen[text]) > 1
        if tokens < min_tokens or duplicated:
            undecidable.append((r, "too short" if tokens < min_tokens
                                else f"text shared by {len(seen[text])} annotations"))
            continue
        where = [ident for ident, body in bodies.items() if text in body]
        if where:
            cited.append((r, sorted(where)))
        else:
            absent.append(r)
    return {"rows": rows, "cited": cited, "undecidable": undecidable,
            "absent": absent, "min_tokens": min_tokens}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--min-tokens", type=int, default=DEFAULT_MIN_TOKENS,
                        help=f"below this, an annotation is UNDECIDABLE rather "
                             f"than cited (default {DEFAULT_MIN_TOKENS})")
    parser.add_argument("--json", action="store_true",
                        help="emit the sets as JSON for a register close")
    args = parser.parse_args(argv)

    res = classify(args.min_tokens)
    rows = res["rows"]
    if not rows:
        print("  no annotations in the window; nothing to classify.")
        return 1

    if args.json:
        print(json.dumps({
            "window_from": WINDOW_FROM,
            "min_tokens": res["min_tokens"],
            "cited": [{"file": r["file"], "text": r["text"][:200],
                       "entries": w} for r, w in res["cited"]],
            "undecidable": [{"file": r["file"], "text": r["text"][:200],
                             "why": why} for r, why in res["undecidable"]],
            "absent": [{"file": r["file"], "text": r["text"][:200]}
                       for r in res["absent"]],
        }, indent=2))
        return 0

    print(f"HIS ANNOTATIONS DATED {WINDOW_FROM} OR LATER")
    print(f"  annotations in the window : {len(rows)}")
    print(f"  C0 claimed it audited     : 302")
    print(f"  difference                : {abs(302 - len(rows))}")
    print("  The difference is why a count cannot be reconciled: it cannot say")
    print("  WHICH items it covered. What follows is a SET, derived from")
    print("  committed artefacts, so every row can be checked by reading 2")
    print("  files.")

    print(f"\nTHE SETS, at a distinctiveness threshold of {res['min_tokens']} tokens")
    _say("CITED by a task entry", _proportion(len(res["cited"]), len(rows)))
    _say("UNDECIDABLE, cannot be attributed",
         _proportion(len(res["undecidable"]), len(rows)))
    _say("NOT CITED, distinctive and absent",
         _proportion(len(res["absent"]), len(rows)))

    print("\n  WHY SOME ARE UNDECIDABLE, by reason:")
    reasons = {}
    for _, why in res["undecidable"]:
        key = "too short" if why == "too short" else "text repeats"
        reasons[key] = reasons.get(key, 0) + 1
    for key, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"    {n:>4}  {key}")
    print("  His verdicts repeat verbatim, so a substring match on a short one")
    print("  proves nothing. Calling those CITED would be the flattering")
    print("  direction, and C0 records that a first attempt to answer him")
    print("  failed in exactly that direction.")

    print("\nTHE THRESHOLD, REPORTED RATHER THAN HIDDEN")
    for t in (4, 6, 8, 12):
        r = classify(t)
        print(f"  min_tokens={t:<3} cited={len(r['cited']):<4} "
              f"undecidable={len(r['undecidable']):<4} "
              f"absent={len(r['absent'])}")
    print("  A threshold chosen to make a figure look good is a tuned constant")
    print("  pretending to be a finding, so the whole curve is printed.")

    print("\n  SAMPLE OF THE NOT-CITED SET, which is the genuine remainder:")
    for r in res["absent"][:6]:
        print(f"    {r['file'][:44]:<44} {r['text'][:62]!r}")

    print("\nTHIS IS NOT A COVERAGE MEASURE, AND THE FIGURE MUST NOT BE READ")
    print("AS ONE. An instruction of his acted on at the time leaves NO ENTRY")
    print("BEHIND, so 'not cited by an entry' does not mean 'not done'. Reading")
    print("the not-cited proportion as a backlog of unhandled instructions")
    print("would be answering the wrong question, which is the error entry C0")
    print("records of its own first attempt: a word-overlap measure reported")
    print("198 of 199 of his verdicts covered, survived a control test, and")
    print("still answered the wrong question, because whether his topic words")
    print("appear somewhere says nothing about whether he was acted on.")
    print("  WHAT THE REMAINDER NEEDS is the audit C0 performed and did not")
    print("  record: a judgement per annotation. No script can supply it,")
    print("  which is why this one does not claim to.")

    print("\nWHAT THIS LICENSES AND WHAT IT DOES NOT")
    print("  LICENSES: closing the CITED tickets with a verification naming the")
    print("  entry that quotes them, which anyone can check.")
    print("  DOES NOT LICENSE: closing the UNDECIDABLE or NOT CITED sets. The")
    print("  first cannot be attributed and the second is not tracked at all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
