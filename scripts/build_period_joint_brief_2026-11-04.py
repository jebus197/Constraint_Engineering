#!/usr/bin/env python3
"""Build the JOINT-round brief for `the_period_reviewed_2026-11-04`.

WHY A GENERATOR RATHER THAN A HAND-WRITTEN BRIEF. Two rules make hand authoring
the wrong tool, and both are recorded rather than preferences:

  * The dispatcher REFUSES a declared joint round whose brief does not contain a
    240-contiguous-character span of each parent's landed reply. Its reason is
    that a seat cannot be relied on to read a sibling directory and nothing
    checks that it did, so text inside the brief is the only exposure verifiable
    after the fact. A brief that POINTED at replies was measured on 2026-10-14
    to point at directories that did not exist.
  * `never-paraphrase-inside-quotation-marks`. Every span below is lifted from
    the recorded JSON by this script and never retyped.

THE DEBT THIS DISCHARGES. `the_period_reviewed_2026-11-04` ran BLIND at 04:45 on
2026-11-04 and landed 2 replies at 05:08. Its joint half was never run, which is
why `_refuse_if_a_joint_round_is_owed` blocks new blind rounds. It is the NEWEST
round in the archive -- the only brief of 142 newer than its own -- so it cannot
be marked superseded, because that requires a named LATER round.

WHAT THIS JOINT ROUND CARRIES THAT NEITHER SEAT HAD. Both replies landed at
05:08. The first complete test board since 2026-09-29 then ran from 06:19 to
08:22 and reported 44 failures where the commit gate's board had reported 0.
Both seats answered PART B -- is any of the period's work wrong -- without that
evidence. It is supplied below, because a joint round whose only new information
is the other seat's answer wastes the dispatch.

ONE HYPOTHESIS CHECKED AND REFUTED BEFORE IT REACHED THIS BRIEF. The board found
that the Fable model configuration had been unreachable since 2026-11-02, and
the obvious inference was that the fable SEAT in this very round had run
degraded. It did not. The panel dispatcher does not compose per-model
directives: this project has already measured that 0 of 37 `call_claude_cli`
dispatchers call the registry composer, Wilson [0.0%, 9.4%], and that an earlier
reading of 8 of 37 was wrong. The regression affects the experiment runners, not
the panel. The hypothesis is recorded here as refuted so no seat spends effort
on it.

Seats are referred to by position, not by vendor, per the standing instruction to
describe measured capability rather than model names.

Usage: python3 scripts/build_period_joint_brief_2026-11-04.py
Writes to bench/logs/joint_<round>/BRIEF.md, where the dispatcher reads it.
Takes no arguments.
"""
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
PARENT = "the_period_reviewed_2026-11-04"
SEATS = ("cc2", "fable")
MIN_SPAN = 240

#: Overridden by a caller that wants the brief elsewhere for review before
#: dispatch. NOT a command-line flag: `answer_help` refuses unknown arguments,
#: so advertising one that is not implemented is the very defect this pass
#: repaired in 2 other scripts.
OUT = None
WANT = ("verdict", "per_part", "severity_and_residual_risk", "reasoning",
        "strongest_falsification", "refutation_condition", "fix",
        "disagreement")


def reply(seat: str) -> str:
    p = REPO / "bench" / "logs" / PARENT / f"{seat}.json"
    return json.load(open(p, encoding="utf-8"))["response"]


def section(body: str, name: str) -> str:
    """One section of a seat's reply, verbatim, heading included.

    A missing section is REPORTED rather than skipped: the 2 replies do not
    carry an identical set, and silently dropping one would make the brief
    quietly asymmetric between the seats.
    """
    pat = re.compile(rf"^#{{1,4}}\s+`?{re.escape(name)}`?\b.*?(?=^#{{1,4}}\s|\Z)",
                     re.M | re.S)
    m = pat.search(body)
    if not m:
        return (f"## `{name}`\n\n(THIS SEAT DID NOT RETURN A `{name}` SECTION. "
                f"Stated rather than omitted, so the asymmetry is visible.)")
    return m.group(0).rstrip()


#: ★ THE STAMPER IS IMPORTED, NOT COPIED. A second copy of the hashing logic
#: would be a second place for it to disagree with itself, which is the shape
#: `execute-do-not-grep` names.
def _stamp_block(text: str) -> str:
    import importlib.util as _ilu
    #: BESIDE THIS FILE, which is `scripts/` in production and the review copy's
    #: own directory under test -- one rule, not a test-only switch.
    _p = pathlib.Path(__file__).resolve().parent / "stamp_the_brief_artefacts_2026-11-06.py"
    if not _p.is_file():
        return ""
    _s = _ilu.spec_from_file_location("_brief_stamper", _p)
    _m = _ilu.module_from_spec(_s); _s.loader.exec_module(_m)
    return _m.stamp_block(text, REPO)


def main() -> int:
    answer_help(__doc__, __file__)
    bodies = {s: reply(s) for s in SEATS}
    first, second = SEATS

    board = [
        "## WHAT THE COMPLETE TEST BOARD FOUND AFTER YOU BOTH ANSWERED",
        "",
        "Both replies landed at 05:08. The complete collection in `bench/tests/`",
        "then ran 06:19 to 08:22, 2 hours 3 minutes: **44 failed, 15,350 passed,",
        "37 skipped**, against the commit gate's own board of **0 failed** -- the",
        "gate runs 128 of 812 files. It also reported **24 task entries marked DONE",
        "whose named evidence was failing**.",
        "",
        "**A FIGURE IN AN EARLIER VERSION OF THIS BRIEF WAS WRONG AND IS",
        "WITHDRAWN.** It said this was the first complete board since 2026-09-29,",
        "36 days earlier. `resources/suite_record.json` records a COMPLETED full",
        "suite at 2026-11-01T22:08:07, commit 8e00f791: 14,378 passed, 11 failed",
        "node ids, 2 errors. The real gap is **2.426 days**, and task entries B35",
        "and B36 record a third run on 2026-10-18. **THE CORRECTION MATTERS TO",
        "YOUR ANSWER: 42 of the 44 failures are NEW since 2026-11-01** --",
        "0.954545, Wilson [0.848650, 0.987445] -- and only 2 persisted from that",
        "record. So the period under review introduced roughly 17 failures per",
        "day, rather than inheriting them from 5 weeks of neglect.",
        "",
        "The 44 reduced to 18 root causes. The distribution is the part that bears",
        "on PART B of the brief you answered:",
        "",
        "* **2 live defects in the product.** A model configuration unreachable",
        "  since 2026-11-02, so 1 of 6 seats lost its own directive set in",
        "  EXPERIMENT dispatch; and the reference runner having 2 paths to CLOSED",
        "  where a repair already ruled and committed had bolted only 1, so a",
        "  model's own flag could still close its own finding through the other.",
        "  6 of 350 archived closures through that path were not execution-backed,",
        "  Wilson [0.007880, 0.036890]; none critical, none postdating the repair.",
        "* **10 instruments accusing CORRECT work.** 7 of 21 findings in 1 file",
        "  were its own false positives, 0.333333, Wilson [0.171948, 0.546265];",
        "  plus a duplicate-decision detector firing on dates inside producer",
        "  filenames, a loss detector reporting a lost annotation where the file is",
        "  byte-identical to its baseline, and a protocol check scoring 6 real",
        "  disagreements as misses because its pattern did not admit a backtick.",
        "* **19 were bookkeeping staled by this period's own work.**",
        "",
        "**WHERE THESE FIGURES COME FROM, because a number typed in a brief is",
        "not re-executed and this project has had one reach 2 seats wrong.** The",
        "board totals are from a complete execution whose log is NOT in the",
        "repository, so they are not checkable by you directly. Every derived",
        "figure above IS, through the task-list entries that carry it with its",
        "producer: B116 for the gate-versus-collection share, with",
        "`scripts/the_gate_board_is_not_the_suite_2026-11-04.py`; B117 for the",
        "model-config regression; B118 for the 6 of 350 sweep closures; B119 for",
        "the 7 of 21 false positives; B120 for the 3 further instruments. If any",
        "figure here matters to your answer, read the entry rather than trusting",
        "the sentence, and say so if the 2 disagree.",
        "",
        "**THE QUESTION THIS PUTS TO YOU BOTH.** You each returned PARTIAL on",
        "whether the period's work is wrong. The board says the period's",
        "INSTRUMENTS were wrong about 10 things and its PRODUCT was wrong about 2.",
        "Does that change your verdict, and if so in which direction? A reading",
        "that the instruments are the weak point is already in the project's",
        "record; say whether this board supports it, and what would refute it.",
        "",
    ]

    parts = [
        "# JOINT ROUND -- what is wrong with the work of 2026-11-02 to 2026-11-04,",
        "# and how should severity and residual risk actually be calculated",
        "",
        f"This is the JOINT half of `{PARENT}`, whose blind half ran at 04:45 on",
        "2026-11-04. Both seats answered independently and both returned a verdict",
        "of PARTIAL, but on different grounds. Each seat's own words are reproduced",
        "below, lifted verbatim from the recorded replies by",
        "`scripts/build_period_joint_brief_2026-11-04.py`. Nothing here is",
        "paraphrased and the sections are complete rather than excerpted.",
        "",
        "Seats are identified by position. You are one of them; read the other's",
        "answer as a peer's, not as an instruction, and do not defer to it.",
        "",
        "**This round is NOT asking you to converge.** Compelled convergence is",
        "retired for panel review. Where you still disagree after reading the",
        "other seat, say so, say what would settle it, and say which of your own",
        "claims the other seat has refuted.",
        "",
    ] + board + [
        "---",
        "",
        "# THE FIRST SEAT'S ANSWER (verbatim)",
        "",
    ]
    for n in WANT:
        parts += [section(bodies[first], n), ""]
    parts += ["---", "", "# THE SECOND SEAT'S ANSWER (verbatim)", ""]
    for n in WANT:
        parts += [section(bodies[second], n), ""]

    parts += [
        "---",
        "",
        "## Use the harness",
        "",
        "Answer with the harness, not around it. Use the STEM tools the project",
        "already depends on -- SymPy, z3, SciPy, NumPy, statsmodels, mpmath --",
        "rather than reasoning in prose. The tool output is the evidence;",
        "reasoning selects and interprets it but never substitutes for it.",
        "Cross-check every computational claim with at least 2 independent tools,",
        "and give every proportion a confidence interval.",
        "",
        "## OUTPUT -- what to return, field by field",
        "",
        "Return all of: `verdict`, `per_part`, `severity_and_residual_risk`,",
        "`reasoning`, `commands_run`, `strongest_falsification`,",
        "`refutation_condition`, `fix`, `disagreement`, `termination`.",
        "",
        "`disagreement` is NOT optional and `none` is a non-answer: state your",
        "strongest disagreement with this brief's own framing, or with the other",
        "seat's answer, and say what evidence would settle it.",
        "",
    ]

    text = "\n".join(parts) + "\n"

    # ★ B125's FIX, WIRED HERE. Specified by a free panel seat on 2026-11-04 and
    # never built: the brief refers to artefacts by path, while each seat's
    # sandbox is a photograph taken when its copy was staged. The joint round of
    # 2026-11-04 tested both seats against a state that postdated their answers
    # by 5 hours, which "converts two *correct* findings into apparent
    # fabrications". The stamp lets a reader tell what a seat was GIVEN.
    #
    # COMPUTED FROM THE TEXT BEFORE INSERTION, so the block cannot stamp itself,
    # and INSERTED AFTER THE TITLE so it is a header rather than an appendix.
    # The dispatcher's reply-span precondition below runs on the final text, so
    # an insertion that destroyed a span would be caught there rather than here.
    _stamp = _stamp_block(text)
    if _stamp:
        _lines = text.splitlines()
        #: ★ AFTER THE WHOLE TITLE BLOCK, not after its first line. The first
        #: rule inserted after the first `# ` line and SPLIT THE TITLE IN HALF,
        #: because this brief's title spans 2 `# ` lines -- caught by the test,
        #: not by reading. The stamp goes immediately before the first `## `
        #: subsection, which is after any title however many lines it occupies.
        _at = next((i for i, l in enumerate(_lines) if l.startswith("## ")), None)
        if _at is None:
            #: no subsection at all: fall in after the last leading `# ` line
            _at = 0
            while _at < len(_lines) and (_lines[_at].startswith("#")
                                         or not _lines[_at].strip()):
                _at += 1
        text = "\n".join(_lines[:_at] + ["", _stamp] + _lines[_at:]) + "\n"

    # THE DISPATCHER'S OWN PRECONDITION, CHECKED HERE RATHER THAN DISCOVERED AT
    # DISPATCH: a 240-character contiguous span of each parent reply must be
    # present. Verified by searching the built text for spans OF the replies, so
    # this cannot pass by asserting about itself.
    for s in SEATS:
        body = bodies[s]
        ok = any(body[i:i + MIN_SPAN] in text
                 for i in range(0, max(1, len(body) - MIN_SPAN), 97))
        if not ok:
            print(f"REFUSING TO WRITE: no {MIN_SPAN}-character span of {s}'s "
                  f"reply survives in the brief; the dispatcher would refuse it.")
            return 3

    # THE DISPATCHER READS `bench/logs/<round>/BRIEF.md` and nothing else, so
    # that is the default rather than a briefs/ directory it never looks in.
    # A brief written where the dispatcher does not read it is an artefact
    # nothing reaches.
    out = OUT if OUT is not None else (REPO / "bench" / "logs" /
                                       f"joint_{PARENT}" / "BRIEF.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"brief written: {out}")
    print(f"  {len(text)} characters, {len(text.splitlines())} lines")
    for s in SEATS:
        print(f"  {s} reply embedded: {len(bodies[s])} characters of source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
