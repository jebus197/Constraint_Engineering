#!/usr/bin/env python3
"""Which open items go to the PANEL, and which are genuinely his -- his triage rule.

HIS INSTRUCTION, 2026-10-18: *"If tickets are genuinely computationally
irreducible and do not meet these standards, or meet our formal HIL escalation
criteria, then that's fine. I wll look at them. Otherwise feed them back to the
panel for resolution (suggesting your own fixes first) and attempt to clear as
many as possible."*

SO THE DEFAULT INVERTS. Until now an item needing a decision waited for him. He
has now said the panel is the first resort and he is the second, and that only 3
things reserve an item to him:

  (a) it is genuinely computationally IRREDUCIBLE -- no measurement could settle
      it, so no amount of seat time helps;
  (b) it does not meet the additive, simplest-sufficient or composability
      standards -- which is to say the proposal is not admissible as work;
  (c) it meets the formal HIL escalation criteria.

THE 4TH, WHICH HE DID NOT NAME AND WHICH THIS SCRIPT ADDS EXPLICITLY SO IT CAN BE
CHALLENGED: an item whose only remaining step SPENDS HIS MONEY OR HIS WEEKLY
TOKEN ALLOWANCE. A panel can rule on whether an experiment is worth running; it
cannot authorise the spend, because the resource is his. That is a reservation to
him on a different ground from (a) to (c), and it is marked separately rather
than folded into them.

EVERY CLASSIFICATION CARRIES ITS REASON, and the reasons are checkable against the
master task list rather than being a matter of taste. The script fails loudly if
an open entry has no classification, so the table cannot go stale as the board
moves.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as M  # noqa: E402

PANEL = "PANEL"
HIS_SPEND = "HIS -- spends his resources"
HIS_IRREDUCIBLE = "HIS -- computationally irreducible"
HIS_HIL = "HIS -- HIL escalation"

#: item -> (destination, my own proposed fix stated FIRST, as he required)
TRIAGE: dict[str, tuple[str, str]] = {
    "R1": (HIS_SPEND,
           "Restarting the zero-plant control is a PAID live experiment and is "
           "additionally blocked on the A1-A10 engineering gate. A panel can "
           "rule on the design; only he can authorise the spend."),
    "B34": (HIS_SPEND,
            "My fix: build the progress signal first, then accept the stagger. "
            "The measurement itself needs 47 to 109 rounds, 18.8 to 105.4 hours "
            "of his Max quota, so the SPEND is his even though the DESIGN "
            "question goes to the panel in the same brief."),
    "B24": (PANEL,
            "My fix: enforce the number rule going FORWARD only. Full "
            "retrospective enforcement takes the checker from 87 findings to "
            "roughly 16,743 across 522 of 539 notes, which is not a repair but a "
            "rewrite of the archive. The panel should say whether a "
            "going-forward ratchet is sufficient or whether the rule is worth "
            "the retrospective cost."),
    "B29": (PANEL,
            "My fix: have the save record whether its own postconditions passed, "
            "and have the memory check skip its baseline back to the last save "
            "that finished cleanly. Additive -- it replaces an inference with a "
            "recorded fact. The panel should try to break the claim that this "
            "keeps the guarantee as strong for a first save."),
    "B31": (PANEL,
            "My fix: an explicit allow-list of known-safe configuration field "
            "names, checked BEFORE the credential pattern, so the pattern is "
            "untouched and an unlisted field is still withheld. The panel should "
            "attack whether that fails safe."),
    "B33": (PANEL,
            "My fix: WIRE the hierarchical mode rather than retire it, since the "
            "location-keyed mode beside it shows the pattern works and the series "
            "is already computed on every run. Retiring is a removal needing a "
            "committed measurement. Either way the report must stop publishing a "
            "field whose name asserts the mode gates when it cannot."),
    "B13": (PANEL,
            "My fix: a missing registration should be LOUD and non-fatal, which "
            "is the 4th option his 3 did not include and which entry C18 now "
            "makes available -- record the fallback with the model's stable "
            "identity and announce it, rather than raising, refusing dispatch or "
            "deferring to a preflight. The panel should say whether a preflight "
            "dominates it."),
    "B20": (PANEL,
            "DEFERRED BY HIS OWN RULING of 2026-10-17 -- *\"I do not wish you to "
            "become too sidetracked on this specific issue\"* -- and its build "
            "half is genuinely not startable: no role layer in the policy "
            "registry, no autonomous monitoring loop, no researcher interface and "
            "no fix comparator. So Fable has nothing to orchestrate yet. "
            "★ AN AMBIGUITY IN HIS 2026-10-18 MESSAGE IS RAISED RATHER THAN "
            "RESOLVED SILENTLY: *\"where Fable will stand in as the orchestrator "
            "model in your place as we agreed\"* reads 2 ways. It may mean (1) run "
            "the simulated experiments with Fable in the bound-orchestrator role, "
            "which needs this build he deferred; or (2) let Fable take the "
            "synthesising seat in the panel reviews in place of CC1, which is "
            "runnable tonight. The 2 readings lead to materially different work, "
            "so the question is put to him in the closing report. My fix for the "
            "DESIGN half, which the panel can take now: score the orchestrator on "
            "the 1 arm that has an executable criterion -- choosing between "
            "candidate repairs, which an existing module already judges against "
            "the defect a falsifier demonstrates -- and leave the monitoring arm "
            "out until a predicate for \"something has gone wrong\" exists, "
            "because nothing anywhere specifies one."),
    "B21": (PANEL,
            "My fix: wire the 4-layer policy engine into the canonical runner "
            "using C18's loud-lookup pattern, so an unregistered model is "
            "recorded and announced rather than raising -- which is what "
            "otherwise makes this wait on B13. He asked for exactly this "
            "sequence: build it, then put the work to the free panel."),
    "B22": (PANEL,
            "No fix of mine to propose: the question is whether the harness is "
            "yet as useful across STEM as it is for code, and he directed it to a "
            "free panel explicitly. My position, stated in the brief, is that the "
            "domain layer generalises and the scoring does not."),
    "C1": (PANEL,
            "My fix: promote the claim channel as a MULTIPLIER on an existing "
            "term, following the precedent he already ruled for the section 7.7 "
            "verification factor, rather than as a new additive channel. Measured "
            "2026-10-18: the ledger's header names `target_complexity` as the "
            "precedent and 3 channels carry `informative_only = True` with 0 ever "
            "promoted, so there is no worked example to copy and the form is a "
            "model-design choice."),
    "C12": (PANEL,
            "The fix is already applied -- the required quiet run is 7 -- and he "
            "ordered the panel CHECK of it in the same breath. My position: 7 is "
            "right on the upper confidence bound, but the panel should test "
            "whether lengthening the first gate arm compensates for a second arm "
            "that blocked 0 premature windows."),
    "C15": (PANEL,
            "My fix: capability should distinguish models only by measured "
            "falsification outcomes pooled per hashed identity, which "
            "`season_strength_order` now does. The open half is what breaks the "
            "cold-start tie when no pair separates, and that is a design question "
            "both seats previously declined."),
    "C21": (PANEL,
            "My fix: none yet, and that is the point. Executed 2026-10-18, the "
            "ladder attempts a measured order and establishes none -- 0 of 3 pairs "
            "in a constructed case and 0 of 10 on the real archive -- so the "
            "frozen vendor tuple is the order actually in force. The panel should "
            "answer his own question: what breaks the tie if not a name?"),
}

#: The 4 register proposals carry no task reference. Only he may REJECT a
#: proposal, which is unchanged -- but he has now asked that the panel resolve
#: what it can first, so they are panel-bound for a RECOMMENDATION.
PROPOSALS = {
    "a SQLite indexed primary key for exact register lookups": (
        PANEL, "My position: DECLINE. The inverted word index already gives "
               "82.79x on the live store, 480.4354 ms linear against 5.8033 ms "
               "indexed, so the measured bottleneck is gone and a database adds "
               "a dependency for no named gain."),
    "a content-addressable blob store for ticket code literals": (
        PANEL, "My position: DECLINE on the simplest-sufficient standard; the "
               "store is 9.4 MB and nothing has measured a cost from literals."),
    "typed primitive wrappers on every register field": (
        PANEL, "My position: DECLINE; it adds ceremony with no defect to point "
               "at, and the additive standard asks what measurement it buys."),
    "namespace paths such as issues-open and dupes": (
        PANEL, "My position: PARTLY ACCEPT -- the subject tier already gives "
               "areas of functionality, which is what he asked for, so the "
               "namespace would duplicate it rather than add reach."),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()
    entries = {e.ident: e for e in M.parse_entries()}
    live = sorted(i for i, e in entries.items() if e.state in ("OPEN", "DEFERRED"))

    unclassified = [i for i in live if i not in TRIAGE]
    stale = [i for i in TRIAGE if i not in entries or
             entries[i].state not in ("OPEN", "DEFERRED")]

    panel = [i for i in live if TRIAGE.get(i, ("", ""))[0] == PANEL]
    his = [i for i in live if TRIAGE.get(i, ("", ""))[0].startswith("HIS")]

    print(f"live entries (OPEN or DEFERRED): {len(live)}")
    print(f"  -> PANEL: {len(panel)}  {panel}")
    print(f"  -> HIS:   {len(his)}  {his}")
    print(f"  register proposals, panel-bound for a recommendation: {len(PROPOSALS)}")
    print(f"  (only he may REJECT a proposal; that is unchanged)")
    print()
    for i in live:
        dest, fix = TRIAGE.get(i, ("UNCLASSIFIED", "no entry in the table"))
        print(f"  {i:5} {dest}")
        print(f"        {fix}")
    print()
    for title, (dest, fix) in PROPOSALS.items():
        print(f"  proposal: {title}")
        print(f"        {dest}: {fix}")
    print()
    if unclassified:
        print(f"★ UNCLASSIFIED live entries, so this triage is incomplete: {unclassified}")
    if stale:
        print(f"★ TRIAGE ROWS naming items that are no longer live: {stale}")
    if not unclassified and not stale:
        print("every live entry carries a destination and every row names a live "
              "item, so the triage is complete as of this commit.")
    return 1 if (unclassified or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
