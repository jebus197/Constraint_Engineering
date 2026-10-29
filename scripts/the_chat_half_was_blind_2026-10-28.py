#!/usr/bin/env python3
r"""The harvester's chat half discarded 92.9% of what it was built to read.

FOUND 2026-10-28 while fixing the ticket store's over-matching on his
instruction. The over-matching had a root cause -- `from_chat` passed no anchor,
so every chat-sourced proposal reached the subject tier with no identity and was
decided on 1 shared code identifier. Repairing that exposed something larger:
`from_chat` returned 0 rows for EVERY window tried, back to 2026-08-01.

THE COUNTS BELOW MOVE BETWEEN RUNS, BY DESIGN. The transcripts grow while this
session is running, so the absolute counts are a function of when the script is
called; the RATE is stable. First run 2026-10-28: 249 of 268 discarded =
0.929104. Second run minutes later: 260 of 280 = 0.928571. Quote the rate with
its interval, never a bare count.

THE PREFILTER WAS NARROWER THAN THE DECISION IT GUARDED. It read
`r'"(fr|pf)[:\]]'` against each raw transcript line, and 3 things are wrong with
that in 1 expression:

  1. The leading double quote requires the marker to sit at the very START of a
     JSON string value, so a marker anywhere inside a longer message is invisible.
  2. `qs` and `wr` are absent -- 2 of the 4 KINDS -- so a question or a
     work-remaining marker in chat could never be harvested at all. `qs` is the
     kind he instructed on 2026-10-19.
  3. It is a SECOND predicate for a question `MARKER` already answers, free to
     drift from it. This is `execute-do-not-grep` in prefilter form.

AND FIXING IT ALONE MADE THE FUNCTION REACHABLE AND USELESS AT THE SAME TIME,
which is the part worth recording. With the prefilter corrected, 31 rows came
back for 2026-10-01 onward and 0 of 31 were a proposal: 24 were this session's
own Stop-gate output quoted back into the transcript, 3 were compaction
summaries, and 4 only CITED an existing ticket id. `MARKER` accepts `pf:`, which
is also the form of every reference to an existing ticket, so raising and citing
were conflated. A register that files its own prodding as new work is circular.

3 FILTERS WERE ADDED, none of them a tuned constant: harness echo by its own
leading prefix, citation by `kind:<hex>`, and quotation by backticked code span.
The last was found by this repair's own P-pass -- the 1 row that survived the
first 2 filters was my own message containing the literal template `[qs:...]`.

THE LOSS WAS LATENT, NOT REALISED, AND THE FIRST VERSION OF THIS FILE GOT THAT
WRONG. It led with a 0.92 discard rate as though proposals had gone missing. That
figure compares 2 RAW-LINE predicates with each other and says nothing about
proposals. Decoding every one of the 1,185 lines the permissive prefilter admits
across 249,664 lines of transcript, the number whose text actually RAISES a
marker is 0. So 0 of 0 genuine chat proposals were lost. The defect was real and
its cost was zero, and those are 2 separate facts that must not be merged.

A THIRD PREDICATE WAS NEEDED, AND THE TEST FOUND IT, NOT THE REASONING. Making
`MARKER` the prefilter was still wrong: the decision runs on DECODED text, a
prefilter on the RAW line, and MARKER requires the token to be followed by `:`,
`]`, `)`, ` - ` or end-of-string -- where the raw line has JSON's closing quote.
A message ending "... here pf" matches decoded and fails raw. A prefilter must
be a PROVABLE SUPERSET of the decision, so it is now `\b(fr|pf|qs|wr)\b`.

THE HONEST RESULT, AND IT IS NOT A SUCCESS. With all 3 filters the chat half
returns 0 rows across the whole archive, because NOBODY HAS EVER ISSUED A BARE
MARKER IN CHAT. The facility is now correct rather than blind, and those are
different states, but the capability it was justified by is still absent: the
bounded-orchestrator question it was built to catch exists in chat WITHOUT a
marker, so no marker-gated reader can reach it. Raised for his ruling.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SHIPPED_PREFILTER = re.compile(r'"(fr|pf)[:\]]', re.IGNORECASE)


def _hv():
    spec = importlib.util.spec_from_file_location(
        "ticket_harvester", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ticket_harvester"] = m
    spec.loader.exec_module(m)
    return m


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    from scipy.stats import norm
    z = float(norm.ppf(0.975))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def scan(hv) -> dict:
    """Count, over the real transcripts, what each predicate admits."""
    files = sorted(hv.TRANSCRIPTS.glob("*.jsonl")) if hv.TRANSCRIPTS.is_dir() else []
    lines = shipped = marker = 0
    size = 0
    for f in files:
        size += f.stat().st_size
        for line in f.open(errors="ignore"):
            lines += 1
            if SHIPPED_PREFILTER.search(line):
                shipped += 1
            if hv.MARKER.search(line):
                marker += 1
    lo, hi = wilson(marker - shipped, marker) if marker else (0.0, 0.0)
    return {"files": len(files), "mib": size / 1048576, "lines": lines,
            "shipped_admits": shipped, "marker_admits": marker,
            "discarded": marker - shipped,
            "discard_rate": (marker - shipped) / marker if marker else 0.0,
            "wilson95": [lo, hi]}


def classify(hv, text: str) -> str:
    if hv.HARNESS_ECHO.search(text):
        return "harness echo"
    if hv.CODE_SPAN.sub(" ", text) != text and not hv.raises_a_marker(text):
        return "quotation only"
    if hv.CITATION.search(text) and not hv.raises_a_marker(text):
        return "citation only"
    return "candidate"


def unit_checks(hv) -> list[dict]:
    """The predicate's own truth table, executed rather than described."""
    cases = [
        ("pf", "pf"), ("qs", "qs"), ("fr", "fr"), ("wr", "wr"),
        ("pf: the gate is wrong", "pf"),
        ("wr - work remaining here", "wr"),
        ("see pf:bc80040e3b48 for that", None),
        ("Stop hook feedback: pf is outstanding", None),
        ("the `[qs:...]` template", None),
        ("see `pf` marker docs", None),
        ("performance is fine", None),
        ("This session is being continued from a previous conversation pf", None),
    ]
    out = []
    for text, expect in cases:
        got = hv.raises_a_marker(text)
        out.append({"text": text, "expected": expect, "got": got,
                    "ok": got == expect})
    return out


def truth_scan(hv) -> dict:
    """How many transcript messages actually RAISE a marker. The figure that
    decides whether the defect cost anything."""
    import json
    files = sorted(hv.TRANSCRIPTS.glob("*.jsonl")) if hv.TRANSCRIPTS.is_dir() else []
    admitted = raised = lines = 0
    for f in files:
        for line in f.open(errors="ignore"):
            lines += 1
            if not hv.CANDIDATE_LINE.search(line):
                continue
            admitted += 1
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get("message") or {}
            c = msg.get("content")
            txt = c if isinstance(c, str) else " ".join(
                x.get("text", "") for x in (c or [])
                if isinstance(x, dict) and x.get("type") == "text")
            txt = " ".join(str(txt).split())
            if txt and hv.raises_a_marker(txt):
                raised += 1
    return {"lines": lines, "admitted_and_decoded": admitted,
            "messages_raising_a_marker": raised}



def retirement_check(hv) -> str:
    """★ HIS RULING WAS CONDITIONAL, AND THIS IS THE CONDITION, TESTED.

    Added 2026-10-29. His words, 2026-10-28: *"My verdict is to scrap it if it
    will add to inefficiency."* When he gave that ruling the condition could not
    be evaluated, because the chat half was BROKEN -- its prefilter was not a
    superset of its own decision, so "captures nothing useful" and "captures
    nothing at all" were indistinguishable.

    The free panel fixed the prefilter and both seats' falsifiers pass on it.
    WITH THE FILTER CORRECT, this function asks the only question his condition
    turns on: does the facility now capture anything? If it returns 0 across
    every window, the cost is real and the yield is 0, and his condition HOLDS.
    If it ever returns more than 0, the condition has stopped holding and the
    retirement should be put back to him rather than left standing.
    """
    import time
    out = ["== HIS CONDITION, TESTED WITH THE FILTER CORRECT =="]
    out.append(f"   prefilter: {hv.CANDIDATE_LINE.pattern!r}")
    total = 0
    for since in ("2026-10-28", "2026-10-01", "2026-08-01"):
        t0 = time.time()
        rows = hv.from_chat(since)
        total += len(rows)
        out.append(f"   since {since}: {len(rows)} row(s) in "
                   f"{time.time() - t0:.1f}s")
    out.append(f"   TOTAL captured across every window: {total}")
    out.append("   his condition HOLDS -- cost with 0 yield -- so `chat` is out"
               if total == 0 else
               "   ★ HIS CONDITION NO LONGER HOLDS: the facility now captures "
               "something. Put the retirement back to him.")
    out.append("   of the default. It stays reachable as `--sources chat`, "
               "because it is also the")
    out.append("   SUBJECT of this measurement and the evidence must stay "
               "reproducible.")
    return "\n".join(out) + "\n"

def main() -> int:
    # A REAL PARSER, INSIDE main(), AND THE PLACEMENT IS THE POINT.
    # A module-level `answer_help` call satisfies the writes-answer-help ratchet
    # in test_help_never_acts and BREAKS the import probe in
    # test_operational_scripts, which imports every parser-less script in a
    # subprocess with a stray argv: `answer_help` refuses the unrecognised
    # argument and the module exits 2 during import. Measured 2026-10-28, after
    # my own first fix did exactly that to 3 scripts. `answers_help` accepts "an
    # ArgumentParser constructed anywhere", so a parser HERE satisfies both:
    # `--help` is answered without running the scan, and an import reaches no
    # argv at all because main() is not called at import time.
    import argparse
    argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0]).parse_args()
    hv = _hv()
    print(retirement_check(hv))
    print("== what each predicate admits, over the real transcripts ==")
    s = scan(hv)
    print(f"   transcripts: {s['files']} file(s), {s['mib']:.1f} MiB, "
          f"{s['lines']} lines")
    print(f"   shipped prefilter admitted:  {s['shipped_admits']}")
    print(f"   MARKER (the decision) admits: {s['marker_admits']}")
    print(f"   discarded by the prefilter:   {s['discarded']} of "
          f"{s['marker_admits']} = {s['discard_rate']:.6f}  "
          f"Wilson [{s['wilson95'][0]:.6f}, {s['wilson95'][1]:.6f}]")
    print(f"   kinds the shipped prefilter could match: ['fr', 'pf'] of "
          f"{list(hv.KINDS)}")

    print("\n== and the prefilter was not the only fault ==")
    print("   with MARKER as the prefilter and NO content filters, the 31 rows "
          "for 2026-10-01 onward classified as:")
    print("   harness echo 24, compaction summary 3, citation only 4, "
          "genuine proposal 0  (recorded 2026-10-28)")

    print("\n== the predicate's truth table, executed ==")
    checks = unit_checks(hv)
    for c in checks:
        print(f"   {'OK  ' if c['ok'] else 'FAIL'} {c['text']!r:60} "
              f"-> {c['got']!r} (expected {c['expected']!r})")
    bad = [c for c in checks if not c["ok"]]
    print(f"   {len(checks) - len(bad)} of {len(checks)} pass")

    print("\n== THE FIGURE THAT DECIDES WHETHER THE DEFECT COST ANYTHING ==")
    t = truth_scan(hv)
    print(f"   lines scanned: {t['lines']}")
    print(f"   admitted by the superset prefilter and decoded: "
          f"{t['admitted_and_decoded']}")
    print(f"   messages whose text actually RAISES a marker: "
          f"{t['messages_raising_a_marker']}")
    print("   so genuine chat proposals lost to the old prefilter: "
          f"{t['messages_raising_a_marker']} of "
          f"{t['messages_raising_a_marker']}")

    print("\n== the chat half today, with every filter in place ==")
    live = {w: len(hv.from_chat(w)) for w in
            ("2026-10-20", "2026-10-01", "2026-09-01", "2026-08-01")}
    for w, n in live.items():
        print(f"   since {w}: {n} row(s)")
    print("   0 rows is CORRECT-AND-EMPTY, not blind. Nobody has issued a bare")
    print("   marker in chat. That is a question for him, not a success.")

    out = REPO / "experimental_notes" / "data" / "chat_half_blind_2026-10-28.json"
    out.write_text(json.dumps(
        {"scan": s, "unit_checks": checks, "live_rows": live,
         "classified_31_rows": {"harness_echo": 24, "compaction_summary": 3,
                                "citation_only": 4, "genuine_proposal": 0}},
        indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {out}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
