#!/usr/bin/env python3
"""PRODUCER: which written panel briefs are genuinely unrun AND still relevant?

HIS INSTRUCTION, 2026-11-01: *"You have several panel reviews outstanding too,
so you can run these in sequence (where still relevant) as we previously
recently agreed."* The parenthesis is the whole task: a brief with no replies is
not automatically outstanding, because the question it asks may have been
answered elsewhere, retired by a reframing, or ruled on by him directly.

EVERY DISPOSITION BELOW CARRIES ITS EVIDENCE. A brief is called moot only
against a named successor round, a named ruling with its file and line, or a
named closure -- never on a judgement that it feels settled.

WHY THIS MATTERS RATHER THAN BEING BOOKKEEPING. The claim-channel brief
validated clean and was 1 command from dispatch on the night of 2026-11-01. Its
question -- which of sigma, S_k or R_k the channel's verdict enters, and in what
form -- was RULED by him on 2026-10-29, 9 days after the brief was written. Two
free seats and about 15 minutes of his machine would have been spent asking a
panel something he had already decided, and the brief's own validator had
already warned that the files it describes had changed by 14,281.6 and 16,158.8
minutes. The check that caught it was reading the file the brief cites.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

FAILURES: list[str] = []


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    _check("wilson cross-check",
           abs(float((c - h) / d) - lo_sm) < 1e-9 and abs(float((c + h) / d) - hi_sm) < 1e-9,
           "statsmodels and mpmath disagree")
    return float(lo_sm), float(hi_sm)


#: DISPOSITIONS, each naming the evidence that settles it. `live` means a seat
#: should be dispatched; anything else means it should not, and says why.
DISPOSITION = {
    "general_purpose_stem_calculator_2026-10-18": (
        "RETIRED", "superseded by his reframing of the fix-outside-code question; "
        "the replacement round what_is_a_proof_outside_code_b22_2026-10-30 ran "
        "with 7 reply files, and its joint half ran on 2026-10-31"),
    "is_this_yet_a_general_purpose_stem_calculator_2026-10-29": (
        "RETIRED", "same family as the above; the replacement round ran"),
    "stem_generality_b22_2026-10-29": (
        "RETIRED", "same family as the above; the replacement round ran"),
    "three_mechanism_repairs_2026-10-18": (
        "MOOT", "all 3 defects it covers are closed and committed on his "
        "rulings of 2026-10-19"),
    "the_required_quiet_run_2026-10-18": (
        "ANSWERED ELSEWHERE", "the question whether a longer quiet run is the "
        "right lever was answered by the_quiet_run_is_not_the_lever_2026-10-25, "
        "which ran with 6 reply files"),
    "how_should_the_claim_channel_be_promoted_2026-10-20": (
        "RULED BY HIM", "he ruled the question on 2026-10-29: the annotation at "
        "line 106 of Responses/Decisions_Awaiting_You_2026-10-29.txt reads 'I "
        "accept your recommendation. fr' and sits under the recommendation at "
        "line 104, as a multiplier on R_k by analogy with section 7.7, against "
        "the question at line 102. bench/claim_ledger.py records it and states "
        "that the term and the form are both decided"),
    "panel_todays_fixes_20260906T175435Z": (
        "HISTORICAL", "its item 1 is the removal of the severity gate, which he "
        "later called a mistake and reversed; the gate was restored on "
        "2026-10-06 gated on a reproduced R_k, so reviewing the removal would "
        "review a state the tree no longer has"),
}


def main(argv=None) -> int:
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    briefs = {}
    for b in REPO.glob("bench/logs/**/BRIEF*.md"):
        d = b.parent
        if "sandbox_harvest" in str(d) or "panel_worktree" in str(d):
            continue
        replies = [f for f in d.glob("*.json")
                   if "brief" not in f.name.lower()]
        briefs[d.name] = len(replies)

    unrun = sorted(k for k, n in briefs.items() if n == 0)
    print("=" * 72)
    print("M1. WRITTEN BRIEFS WITH NO REPLY FROM ANY SEAT")
    print("=" * 72)
    print(f"brief directories found : {len(briefs)}")
    print(f"with 0 reply files      : {len(unrun)}")
    for k in unrun:
        print(f"   {k}")
    _check("some briefs are unrun", len(unrun) >= 1,
           "every brief has a reply, so there is nothing to dispose of")

    print()
    print("=" * 72)
    print("M2. DISPOSITION OF EACH, WITH ITS EVIDENCE")
    print("=" * 72)
    live, settled, unknown = [], [], []
    for k in unrun:
        if k in DISPOSITION:
            verdict, why = DISPOSITION[k]
            (live if verdict == "live" else settled).append((k, verdict, why))
        else:
            unknown.append(k)
    for k, verdict, why in settled:
        print(f"  [{verdict}] {k}")
        print(f"      {why}")
        print()
    for k in unknown:
        print(f"  [UNKNOWN] {k}")
        print("      no disposition recorded; it must be read before dispatch")
        print()
    lo, hi = wilson(len(settled), len(unrun))
    print(f"unrun briefs with a recorded disposition: {len(settled)} of "
          f"{len(unrun)}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print(f"STILL LIVE AND DISPATCHABLE: {len(live)}")
    for k, _v, _w in live:
        print(f"   {k}")

    print()
    print("=" * 72)
    print("M3. THE ANSWER TO HIS INSTRUCTION")
    print("=" * 72)
    if not live and not unknown:
        print("There is NO panel brief that is both unrun and still relevant.")
        print("His parenthesis -- where still relevant -- is doing the work: of")
        print(f"the {len(unrun)} briefs with no replies, 3 were retired by his own")
        print("reframing, 1 is moot on closures, 1 was answered by a later")
        print("round, 1 he ruled directly, and 1 reviews a state the tree no")
        print("longer has. So the correct action tonight is to dispatch NOTHING")
        print("and to say so, rather than to spend his seats demonstrating")
        print("activity.")
    else:
        print(f"{len(live) + len(unknown)} brief(s) need a seat. Dispatch in the")
        print("order they were written, which is his standing instruction.")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
