#!/usr/bin/env python3
"""Write a verdict row for each of his 31 annotations of 2026-11-08.

WHY THIS EXISTS. `bench/tests/test_every_annotation_verdict_names_its_evidence_2026-10-17.py`
refused the commit of 2026-11-08 with *31 annotation(s) in the window have no
row*, which is the mechanism recorded in `cdsfl_his_words_may_not_sit_unread_2026-10-25`
working exactly as built: his rulings were answered in CHAT and never recorded,
and a chat answer is not a record. 29 sit on
`Decisions_Awaiting_You_2026-11-08_GENERATED.txt` and 2 on
`The_Gates_Refused_3_Times_2026-11-08.txt`.

THE ALIGNMENT IS PROVED, NOT ASSUMED, which is the whole difficulty here. 22 of
the 29 read *"I accept your recommendation. stm"* verbatim, so the TEXT cannot
say which decision each belongs to -- that is precisely the condition the
`UNDECIDABLE` verdict exists for. What makes them decidable is that the file is
GENERATED with a known order: its index lists decisions 1 to 29, each naming its
entry, and his annotations follow that order. So this script does not trust the
order: for every annotation it reads the file text BEFORE that annotation and
asserts the expected entry code is the LAST one named there. If any single
assertion fails, nothing is written.

ANCHORS AND HIS WORDS COME FROM THE READER, never retyped and never grepped
(`feedback_read_his_responses_with_the_reader_2026-10-11`: 221 of 691 of his
annotations were invisible to grep).

Exit 0 when all 31 rows are written and the record's own audit covers them.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RECORD = REPO / "experimental_notes/data/annotation_verdicts_2026-10-17.json"
RESPONSES = pathlib.Path.home() / "Developer_Projects/Responses"
DEC = "Decisions_Awaiting_You_2026-11-08_GENERATED.txt"
GATES = "The_Gates_Refused_3_Times_2026-11-08.txt"
AUDITED = "2026-11-08"

T = "TRACKED"
A_ = "ACTED_ON"

#: One (entry, verdict, evidence, why) per decision, in the file's own index
#: order. The entry code is ASSERTED against the file text before each
#: annotation, so a wrong order fails loudly instead of mislabelling his words.
DECISIONS = [
 ("B20", A_, "scripts/has_the_bound_orchestrator_been_built_or_run_2026-11-02.py",
  "Answered: no, and the 2 halves are separate entries. The instrument reports 4 of 4 "
  "components built and experiment_run NEVER RUN, with 0 archived runs declaring the arm. "
  "The severity and residual-risk question is entry B53, which completed 2026-11-06 by free "
  "panel. The run is blocked by a mechanical gap named in B20 and owned by me: no invocation "
  "is both simulated and resumable, because the billing guard is an in-process getaddrinfo "
  "block that cannot survive the subprocess boundary a resume needs."),
 ("B21", A_, "scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py",
  "Answered: adding a model today means editing 12 per-model tables across 6 live-harness "
  "files plus 1 registry toml; consolidation means 1 entry in 1 place. Re-run 2026-11-08: of "
  "the 10 steps a new seat passes, 1 fails silently, 1 loudly, 8 announce their default -- the "
  "entry still says 5 of 10 and is stale. CC2's caution when this went to the panel is that a "
  "single point which still defaults silently would hide 12 misses behind 1."),
 ("B71", T, "entry B71 governs the one-file local commit; permission is now recorded",
  "He granted permission for that one file. The wiring is the entry's work and is not yet built."),
 ("B76", T, "entry B76 governs the two-sided gate",
  "He ruled that both convergence gates must agree before a run terminates, which is what his "
  "standing gamma directive already says."),
 ("B77", T, "entry B77 governs the seat-count question", "He accepted the exact version."),
 ("B79", T, "entry B79, plus the measurement that a stale key SELECTS a budget",
  "His feature request is to record dynamically which models exist and which are in use rather "
  "than renaming by hand. His reading is half right: the 3 stale keys name versions no longer in "
  "use -- CC2 keyed opus_4_6 against Opus 4.7, ChatGPT chatgpt_5_4 against GPT-5.5, DeepSeek "
  "deepseek_v3 against V4 Pro -- but a key also SELECTS a coherence and directive budget, so a "
  "dynamic registry can derive identity and cannot derive budgets. That added decision is owed to him."),
 ("B81", T, "entry B81, amended by his instruction",
  "He accepted the guard and amended it: it must report WHY the commit failed so it can be "
  "repaired. The same amendment appears again on decision 27."),
 ("B82", T, "entry B82 governs the scope check", "He accepted the recommendation."),
 ("B83", T, "entry B83 governs where the control's outcome is written",
  "He accepted the recommendation."),
 ("B84", T, "entry B84 governs the pre-run description", "He accepted the recommendation."),
 ("B87", T, "entry B87 governs the directive's refusal", "He accepted the recommendation."),
 ("B88", T, "entry B88 governs the fold-back launcher", "He accepted the recommendation."),
 ("B93", T, "entry B93 governs the role spellings", "He ruled: aliases only."),
 ("B94", T, "entry B94, with his constraint recorded",
  "He rejected the half of the recommendation that put the fingerprint choice to him: capability "
  "fingerprinting is to be done by the harness without HIL intervention, and the option is to be "
  "modified so that happens."),
 ("B96", T, "entry B96 governs the spoken renderer", "He accepted the recommendation."),
 ("B102", A_, "bench/tests/test_a_queued_marker_is_harvested_2026-11-08.py",
  "The union reader is built and committed as scripts/his_messages.py, and its guard runs the "
  "real harvester against a fixture. What remained was the entry's own status line, which still "
  "said the repair was unbuilt. The only open half is outside this repository: whether the "
  "mid-turn delivery behaviour should be raised with Anthropic, which is his to decide."),
 ("B103", T, "entry B103 governs the commit gate's cost-bounded subset",
  "He accepted the recommendation."),
 ("B104", T, "entry B104 governs which identifier a spoken report carries",
  "He accepted the recommendation."),
 ("B105", T, "entry B105, amended: a leading asterisk with no closing one",
  "He accepted the marker rule and amended the emphasis form, because a pair of asterisks can be "
  "misread. Applied to chat immediately. Whether it also governs the markdown documents, which "
  "use the paired form in thousands of places, is put to him as 1 question."),
 ("B107", T, "entry B107 governs the termination ratio", "He accepted the recommendation."),
 ("B111", A_, "scripts/how_many_of_the_nights_errors_were_instruments_2026-11-03.py",
  "Answered: retiring it removes 4 figures from 2 instruction files and changes nothing in code. "
  "The figure is 10 of 12 errors on 2026-10-11 with its interval and p-value, under 2 headings in "
  "each file, and no script reproduces any of them. The argument survives on the 2 producers that "
  "do exist: 16 of 18 errors were in the instruments, and 0 of 7 were noticed unaided."),
 ("B113", A_, "bench/tests/test_a_shell_naming_the_runner_is_not_a_run_2026-11-08.py",
  "Repaired on his word. hooks/cy_monitor_gate.py no longer reports a SHELL whose command line "
  "merely names the runner, which had refused stops twice naming the git commit shell itself. "
  "Shells are excluded rather than python required, so a runner started by another route still "
  "refuses; an unreadable comm keeps the pid. 10 tests, 4 of 4 mutations red, verified against "
  "live planted processes."),
 ("B121", T, "entry B121 governs the severity archive de-duplication",
  "He accepted the recommendation."),
 ("B123", T, "entry B123 governs the finiteness guard", "He accepted the recommendation."),
 ("B124", T, "entry B124 governs the joint round", "He accepted running the joint round."),
 ("B125", T, "entry B125 governs the joint brief's quoting",
  "He accepted the recommendation."),
 ("B128", T, "entry B128, amended by the same caveat as decision 7",
  "He accepted taking no action beyond the recorded habit, with the caveat that a refused commit "
  "must say why so it can be repaired, specifically so the repair can be made without him."),
 ("B129", T, "entry B129 governs the memory index limit",
  "He accepted raising the character limit and leaving each retirement judgement to him."),
 ("B131", T, "entry B131 governs the citation check",
  "He accepted shipping only the check on the identifier's own digits."),
]

GATES_ROWS = [
 (34, T, "entry B135, with the cause of the invisibility now measured",
  "He ruled for option 1 and against the cheaper second. Measured 2026-11-08: all 13 invisible "
  "producers are invisible for 1 reason -- the sample size is named nn in 12 of 13 and N_ in 1, "
  "and the detector's pattern requires the next character to be whitespace or a bracket. So "
  "option 2 would have been a 1-line widening reaching 13 of 13, and his ruling is still right "
  "under execute-do-not-grep: a wider pattern is still a claim about spelling. Option 1's cost is "
  "now exact: 13 files, 33 call sites, 3 of them sharing one helper shape."),
 (46, A_, "bench/tests/test_a_queued_marker_is_harvested_2026-11-08.py",
  "Answered: the guard he asked about is built, committed and green, and the reader it guards was "
  "already committed. What remained was the entry's stale status line. Nothing is skipped."),
]


def _reader():
    spec = importlib.util.spec_from_file_location(
        "_rfr", REPO / "scripts/read_founder_responses_2026-10-11.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["_rfr"] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write the rows")
    a = ap.parse_args()

    ann = [x for x in _reader().annotations() if x["file"] in (DEC, GATES)]
    dec = [x for x in ann if x["file"] == DEC]
    gat = [x for x in ann if x["file"] == GATES]
    print(f"annotations read: {len(dec)} on the decisions file, {len(gat)} on the gates note")
    if len(dec) != len(DECISIONS):
        print(f"REFUSING: {len(dec)} annotations against {len(DECISIONS)} mapped decisions")
        return 1

    raw = (RESPONSES / DEC).read_bytes().decode("cp1252", errors="replace")
    short = raw[:raw.find("DECISION 1.")]
    marks = [m.start() for m in re.finditer(r"#", short)]
    if len(marks) != len(DECISIONS):
        print(f"REFUSING: {len(marks)} '#' marks in the index against {len(DECISIONS)} decisions")
        return 1

    # ---- THE ALIGNMENT PROOF. The entry code expected for annotation i must be
    # the LAST entry code named in the index text before its mark.
    bad = []
    for i, (code, *_rest) in enumerate(DECISIONS):
        before = short[(marks[i - 1] if i else 0):marks[i]]
        named = re.findall(r"\bB\d+\b", before)
        if not named or named[-1] != code:
            bad.append((i + 1, code, named[-3:]))
    if bad:
        print("REFUSING: the order does not match the file. Nothing written.")
        for n, code, got in bad[:6]:
            print(f"  decision {n}: expected {code}, the text before his mark names {got}")
        if len(bad) > 6:
            print(f"  ... and {len(bad) - 6} more mismatch(es) withheld, of "
                  f"{len(bad)} in total")
        return 1
    print(f"alignment proved: all {len(DECISIONS)} marks follow the expected entry code")

    # ★ A 4-WORD REASON IS NOT A REASON. `test_every_row_also_says_why`
    # requires at least 5 words, and "He accepted the recommendation." is 4 --
    # 13 of my first rows were refused on it, correctly: a reader cannot check
    # a sentence that does not say WHAT was accepted. The missing half is taken
    # from the file's OWN index line rather than retyped, so the reason quotes
    # the recommendation he was answering and cannot drift from it.
    gists = {}
    for i, (code, *_r) in enumerate(DECISIONS):
        seg = short[(marks[i - 1] if i else 0):marks[i]]
        m = re.search(r"Recommended option (\d+):\s*(.+?)\s*$", seg.strip(), re.S)
        if m:
            gists[code] = (m.group(1), " ".join(m.group(2).split()))

    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    have = {r["anchor"] for r in rec["rows"]}
    new = []
    for x, (code, verdict, evidence, why) in zip(dec, DECISIONS):
        anchor = f"{x['file']}#{x.get('line_index')}"
        if anchor in have:
            continue
        full = why
        if len(why.split()) < 12 and code in gists:
            n, gist = gists[code]
            full = (f"{why} Option {n} as recorded in the file he answered: "
                    f"{gist}")
        new.append({"anchor": anchor, "audited": AUDITED, "evidence": evidence,
                    "file": x["file"], "line_index": x.get("line_index"),
                    "text": x["text"], "verdict": verdict, "why": full})
    by_line = {x.get("line_index"): x for x in gat}
    for line, verdict, evidence, why in GATES_ROWS:
        x = by_line.get(line)
        if x is None:
            print(f"REFUSING: no annotation at {GATES}#{line}")
            return 1
        anchor = f"{x['file']}#{line}"
        if anchor in have:
            continue
        new.append({"anchor": anchor, "audited": AUDITED, "evidence": evidence,
                    "file": x["file"], "line_index": line, "text": x["text"],
                    "verdict": verdict, "why": why})

    print(f"rows to add: {len(new)}")
    for r in new[:3]:
        print(f"  {r['anchor']:58s} {r['verdict']:9s} {r['text'][:40]!r}")
    if len(new) > 3:
        print(f"  ... and {len(new) - 3} more row(s) withheld from this "
              f"listing; all {len(new)} would be written")
    if not a.write:
        print("\nDRY RUN -- nothing written. Re-run with --write.")
        return 0
    rec["rows"].extend(new)
    rec["rows"].sort(key=lambda r: (r["file"], r["line_index"]))
    RECORD.write_text(json.dumps(rec, indent=2, sort_keys=True,
                                 ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWROTE {RECORD.relative_to(REPO)}: {len(rec['rows'])} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
