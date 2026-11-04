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
Writes to bench/briefs/joint_<round>_BRIEF.md. Takes no arguments.
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
        "gate runs 128 of 811 files. It also reported **24 task entries marked DONE",
        "whose named evidence was failing**.",
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
        "## Required sections",
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

    out = OUT if OUT is not None else (REPO / "bench" / "briefs" /
                                       f"joint_{PARENT}_BRIEF.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"brief written: {out}")
    print(f"  {len(text)} characters, {len(text.splitlines())} lines")
    for s in SEATS:
        print(f"  {s} reply embedded: {len(bodies[s])} characters of source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
