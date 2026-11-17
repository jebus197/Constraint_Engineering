#!/usr/bin/env python3
"""Build a BLIND panel brief over the 19 decisions the founder owes.

★ HIS INSTRUCTION, 2026-11-16, verbatim: *"put all 19 issues to a free panel
and see what they have to say about them. What do they recommend and (without
telling them) does their recommendation match yours?"*

★ SO THE BRIEF MUST NOT CARRY MY RECOMMENDATION, AND 2 THINGS LEAK IT.
First, 17 of 58 option texts say so in words. Second, and less obviously, my
recommendation is option 1 in almost every entry, so POSITION alone would tell a
seat the answer. This script strips the first and destroys the second by
shuffling each entry's options under a fixed seed, and it REFUSES rather than
emitting a brief in which any marker survives.

★ WHAT IT CANNOT DO, STATED RATHER THAN GLOSSED. Seats work in a sandbox clone
of the repository, which contains the committed decisions file holding my
recommendations in full. Blindness here means the brief does not carry them and
the brief instructs seats not to open that file by name. It does not mean a seat
could not. The limitation is reported to him rather than hidden, and the joint
round's own record is the check: a seat echoing my wording is visible.

Writes ONE file, the BRIEF.md of the named round directory. Reads everything
else.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

OWED = ["B77", "B84", "B94", "B125", "B141", "B142", "B143", "B154", "B160",
        "B170", "B171", "B175", "B180", "B182", "B185", "B186", "B190",
        "B194", "B197"]

#: ★ NARROWED AFTER A P-PASS, 2026-11-17, BECAUSE THE FIRST VERSION CORRUPTED
#: WHAT IT WAS PROTECTING. Each alternative ended `[^.]*\.?`, which runs to the
#: next full stop, so it swallowed the clause AFTER the marker as well. Measured
#: on the live options: B175 option 3 lost 252 characters including the whole
#: argument against itself, and B94 option 1 lost 209 characters including the
#: option's own content -- "record the model's claim and the machine's
#: verification as 2 fields rather than 1" -- leaving a seat an option with no
#: proposal in it. A safeguard that destroys what it protects is worse than the
#: leak it prevents.
#:
#: So each pattern now matches the MARKER CLAUSE ONLY, bounded by a comma, colon
#: or full stop, and `DELETION_CAP` turns any over-large removal into a REFUSAL
#: rather than a silent edit.
LEAK = re.compile(
    r"(this is (?:my |the )?recommendation(?: for that half)?"
    r"|which is my recommendation"
    r"|this is the option i would take"
    r"|,? and it is the ADDITIVE \\w+"
    r"|\\bit is the (?:SIMPLEST SUFFICIENT|ADDITIVE) \\w+"
    r"|\bnot recommended\b"
    r"|\brecommended\b"
    r"|\bmy recommendation\b)", re.I)

#: A strip larger than this is not a marker removal; it is damage. Refuse.
DELETION_CAP = 80

SEED = 20261117


def entry_hash(tid_map: dict, entry: str) -> str:
    return tid_map.get(entry, "(no ticket)")


def strip_leaks(text: str, *, cap: int = DELETION_CAP) -> str:
    """Remove the recommendation marker and nothing else.

    Raises SystemExit when the removal exceeds `cap`, because a large removal
    means the pattern caught prose rather than a marker. See the note on LEAK.
    """
    out = LEAK.sub("", text)
    # Tidy what the removal leaves: a dangling connector, doubled punctuation,
    # a sentence now starting lower case.
    out = re.sub(r"(?:^|(?<=[.!?]\s))\s*(?:,|:|;|and\b|,\s*and\b)\s*", " ", out)
    out = re.sub(r"\s*[,;:]\s*(?=[.!?])", "", out)
    # ★ A REMOVAL CAN LEAVE 2 PUNCTUATION MARKS TOUCHING. Measured 2026-11-17:
    # B94 option 1 read `...reads.**,: record the model's claim` once the marker
    # between the comma and the colon was gone. Collapse any run to the last.
    for _ in range(3):
        out = re.sub(r"([,;:])\s*([,;:])", r"\2", out)
    out = re.sub(r"(\*\*)\s*:\s*(?=[A-Za-z])", r"\1 ", out)
    out = re.sub(r"(\*\*)\s*\.\s*(?=[.A-Za-z]|$)", r"\1 ", out)
    out = re.sub(r"\.\s*\.+", ".", out)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([.,;:])", r"\1", out)
    out = out.strip().lstrip(",;:").strip()
    out = re.sub(r"(^|(?<=[.!?]\s))([a-z])",
                 lambda mo: mo.group(1) + mo.group(2).upper(), out, count=1)
    removed = len(text) - len(out)
    if removed > cap:
        raise SystemExit(
            f"REFUSED: stripping removed {removed} characters from an option, "
            f"over the cap of {cap}. That is prose being eaten, not a marker.\n"
            f"  BEFORE: {text[:200]}\n  AFTER : {out[:200]}")
    return out


def headline(entry: str, tl: str) -> str:
    m = re.search(rf"^\*\*{entry}\.\s*(.{{0,160}}?)\*\*", tl, re.M | re.S)
    return (m.group(1).strip() if m else "(no headline)").replace("\n", " ")


def build(tid_map: dict) -> str:
    d = json.loads(DETAIL.read_text(encoding="utf-8"))
    tl = TASKLIST.read_text(encoding="utf-8")
    rng = random.Random(SEED)
    L: list[str] = []
    A = L.append

    A("# BRIEF — the 19 decisions the founder owes, put to the free panel blind")
    A("")
    A("## REQUIRED SECTION 1 — The question")
    A("")
    A("**For each of the 19 numbered items below, recommend ONE of its stated "
      "options, or propose a better option the list does not contain, and say "
      "which of the project's formal standards your choice rests on.** Each item "
      "is a decision the founder has not yet made. Several carry an earlier "
      "ruling of his on a DIFFERENT question; where that is so the item says so, "
      "and the question put to you is the later one.")
    A("")
    A("**THE 3 FORMAL STANDARDS, IN THE FOUNDER'S OWN WORDS. Use them by name. A "
      "verdict that recommends an option without naming the standard it rests on "
      "has not answered.**")
    A("")
    A("**1. ADDITIVE — his wording of 2026-11-16, which REFINES the standing "
      "text and is the version in force for this round:** *\"'additive' means "
      "that it must conform to the project's overall aims, objectives and "
      "specification, in addition to only applying a fix when a proposed fix can "
      "be shown to meaningfully enhance these if no previous fix exists and/or "
      "when it replaces/outperforms an existing fix, either previously in place, "
      "or proposed by you, or another model.\"* Read that as 2 clauses. A fix "
      "must FIT the project's aims, objectives and specification; and it must "
      "either fill a gap where no fix exists, or demonstrably outperform a fix "
      "that does exist — including one proposed by another seat in this very "
      "round. The standing form adds a third clause that still binds: an "
      "addition nothing reaches is not additive either, so a flag, gate or entry "
      "point with no caller and no test fails this standard as surely as a "
      "removal does.")
    A("")
    A("**2. SIMPLEST SUFFICIENT.** The smallest change that addresses the ROOT "
      "CAUSE and the downstream consequences, not the smallest change that makes "
      "a symptom go away. Complexity that cannot be done without is justified; "
      "complexity that merely could be used is not.")
    A("")
    A("**3. COMPOSABILITY — his words, 2026-10-02, verbatim:** *\"Composability "
      "doesn't mean composing two solutions just because they can be composed. "
      "It means this principle should be applied where two composed solutions "
      "demonstrably provide a better, more robust and/or more efficient solution "
      "than either fix in isolation. Where a single fix out performs a composed "
      "one, that fix should continue to be preferred. In all cases any fix "
      "should also take the first two conditions fully into consideration "
      "also.\"* **So composability is a claim that REQUIRES A MEASUREMENT.** "
      "Reporting that 2 repairs do not conflict is the weak non-interference "
      "sense his definition excludes by name, and will be recorded as not having "
      "answered. Recommend a composition only with a measurement showing it "
      "beats either part alone on a NAMED property; where a single fix does as "
      "well, prefer the single fix.")
    A("")
    A("**WHAT YOU ARE NOT TOLD, DELIBERATELY.** This brief does not carry any "
      "recommendation of mine, and the options under each item have been SHUFFLED "
      "so their order carries no signal. **Do not open "
      "`experimental_notes/Decisions_Awaiting_You_2026-11-14_GENERATED.md`, its "
      "spoken twin, or any `Morning_Report_*_GENERATED*` file**: those hold my "
      "recommendations and the point of this round is an independent answer. "
      "Everything else in the repository is yours to read and run.")
    A("")
    A("## REQUIRED SECTION 2 — Use the harness")
    A("")
    A("Form the answer by RUNNING the machinery, not by writing about it. A seat "
      "that returns prose without having executed anything has not answered. The "
      "repository holds the producers behind most of these items under "
      "`scripts/`, their guards under `bench/tests/`, the live task list at "
      "`experimental_notes/CDSFL_MASTER_TASK_LIST.md`, and the ticket register "
      "reachable through `scripts/register.py --id <hash>`. Where an item names "
      "a file, read it. Where it names a producer, run it. Where a figure in an "
      "item matters to your choice, re-derive it rather than trusting the "
      "sentence.")
    A("")
    A("**EVERY NUMBER INSIDE THE 19 ITEMS IS QUOTED, NOT DECLARED, AND THAT IS "
      "SAID HERE RATHER THAN LEFT FOR YOU TO DISCOVER.** The items below are "
      "rendered from the committed decision records, so their figures are as "
      "those records state them. They are NOT re-executed by this brief's "
      "validator, which checks declared figures only. **Treat any number in an "
      "item as a claim about evidence rather than evidence**, and where one "
      "decides your recommendation, re-derive it from the named producer and say "
      "so. A figure you could not reproduce is itself a finding worth more than "
      "the verdict it was supporting.")
    A("")
    A("## REQUIRED SECTION 3 — Produce a fix, and test it")
    A("")
    A("**For each item, deliver a verdict; where your recommendation implies code "
      "or text, WRITE IT INTO THE SANDBOX TREE at its real path.** A fix "
      "described in prose is not delivered, and a fix written to scratch space "
      "is destroyed when the sandbox is torn down. Where an item is a pure "
      "judgement with no artefact — whether a standard is adopted, whether a "
      "branch is merged — say so and give the reasoning instead; do not "
      "manufacture a file to satisfy this section.")
    A("")
    A("**A HARD CONSTRAINT ON EVERY ANSWER.** All 19 are the founder's to rule. "
      "Deliver analysis and any proposed artefact, and state plainly in each "
      "verdict that it awaits his ruling. Do not install anything as though it "
      "were settled.")
    A("")
    A("## REQUIRED SECTION 4 — What would refute you")
    A("")
    A("For each item, state the single observation that would show your "
      "recommendation wrong, and say whether the repository can produce that "
      "observation today. An item where nothing could refute your choice is an "
      "item where you are expressing a preference, and saying so plainly is a "
      "better answer than dressing it as a finding. **Where you disagree with "
      "the framing of an item — where the question as put is the wrong "
      "question — say so and give the right one. That is a finding, not a "
      "refusal.**")
    A("")
    A("## REQUIRED SECTION 5 — Output shape")
    A("")
    A("One block per item, in the order given, each carrying: the item code and "
      "hash; your chosen option letter or your own better option; the standard or "
      "standards your choice rests on, by name; the reasoning in at most a short "
      "paragraph; and your refuter. If you cannot reach a view on an item, say "
      "which item and why, rather than padding.")
    A("")
    A("**Disagreement with the brief's own framing — a REQUIRED field, and the "
      "last thing your reply must carry.** State your strongest disagreement "
      "with how this brief frames the work: an item posed as the wrong question, "
      "an option list that omits the real answer, a standard applied where it "
      "does not bear, or a figure quoted here that your own run contradicts. "
      "**Disagreement is preserved as information and is not to be smoothed: "
      "there is NO compelled convergence in this round.** A reply with nothing "
      "in this field is accepted only if you say so explicitly.")
    A("")
    A("## REQUIRED SECTION 6 — Termination")
    A("")
    A("Stop when every one of the 19 carries a verdict, a named standard and a "
      "refuter. Do not continue past that to re-examine items already settled in "
      "your own answer, and do not spend the remaining budget enumerating "
      "immaterial observations.")
    A("")
    A("---")
    A("")
    A("## THE 19 ITEMS")
    A("")

    stripped_total = 0
    for i, e in enumerate(OWED, 1):
        rec = d.get(f"task:{e}", {}) or {}
        opts = list(rec.get("options") or [])
        cleaned = []
        for o in opts:
            before = o
            o2 = strip_leaks(o)
            if o2 != before:
                stripped_total += 1
            cleaned.append(o2)
        rng.shuffle(cleaned)
        A(f"### ITEM {i}. {e} — `{entry_hash(tid_map, e)}`")
        A("")
        A(f"**Headline.** {headline(e, tl)}")
        A("")
        what = rec.get("what") or "(no authored description)"
        A(f"**What it is.** {strip_leaks(what)}")
        A("")
        why = rec.get("why") or "(no authored reason)"
        A(f"**Why it is his.** {strip_leaks(why)}")
        A("")
        owed = rec.get("still_owed") or rec.get("spoken_heading") or ""
        if owed:
            A(f"**What is actually owed from him.** {strip_leaks(str(owed))}")
            A("")
        A("**The options, shuffled.**")
        for j, o in enumerate(cleaned):
            A(f"{chr(ord('A') + j)}. {o}")
        A("")

    text = "\n".join(L) + "\n"
    leaks = LEAK.findall(text)
    if leaks:
        raise SystemExit(
            f"REFUSED: {len(leaks)} recommendation marker(s) survived the strip "
            f"and would have reached the seats: {sorted(set(map(str, leaks)))[:6]}")
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--round", required=True, help="round directory name under bench/logs/")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and validate the text, write nothing")
    a = ap.parse_args([] if argv is None else argv)

    sys.path.insert(0, str(REPO / "bench"))
    import ticket_store as ts
    tid_map: dict[str, str] = {}
    for t in ts.TicketStore().all():
        row = t if isinstance(t, dict) else getattr(t, "__dict__", {})
        tr = row.get("task_ref")
        if tr in OWED and row.get("status") not in ("CLOSED", "WITHDRAWN", "REJECTED"):
            tid_map.setdefault(tr, f"{row.get('kind')}:{row.get('tid')}")

    text = build(tid_map)
    missing = [e for e in OWED if e not in tid_map]
    print(f"  items: {len(OWED)}   hashes resolved: {len(tid_map)}   "
          f"missing: {missing or 'none'}")
    print(f"  brief length: {len(text)} chars, {len(text.splitlines())} lines")
    print("  recommendation markers surviving: 0 (the builder refuses otherwise)")
    if a.dry_run:
        print("  --dry-run: nothing written")
        return 0
    out = REPO / "bench" / "logs" / a.round
    out.mkdir(parents=True, exist_ok=True)
    (out / "BRIEF.md").write_text(text, encoding="utf-8")
    print(f"  WROTE {out / 'BRIEF.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
