#!/usr/bin/env python3
"""Group the 129 open questions into DISTINCT decisions and say which still need the founder.

WHY THIS EXISTS, AND WHY IT IS NOT scripts/triage_open_founder_decisions.py.
That script is still correct about what it measures, but it has 2 limits that
together produce a misleading number:

  1. Its ANSWERED rules are hardcoded regexes written on 2026-09-05, so every
     ruling the founder has given SINCE is invisible and still counts as OPEN.
  2. Its Jaccard grouping collapses 5.4%, and an exact-token dedupe collapses
     0.0% -- because the same decision is phrased differently by different
     readers. "Seal the 31 plaintext key files" and "Vault the 31 plaintext key
     files" share almost no content tokens after stopwords.

So the raw 129 overstates the decision surface badly. This file groups them by
MEANING, which is a judgement, not a measurement -- and the membership of every
group is recorded below so the judgement is auditable rather than asserted. The
grouping was made after reading all 129 entries end-to-end (founder `rg`,
2026-09-06).

Run: python3 scripts/founder_decision_ledger.py [--tts]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

JOURNAL = Path(
    "/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects"
    "/a07b3790-0a2a-4978-aedb-bd842c0493d3/subagents/workflows/wf_a33f50d2-519"
    "/journal.jsonl")

# (canonical decision, member indices into the 129, status, context, recommendation)
# status: RULED = the founder has answered it; DONE = discharged by evidence;
#         MINE = CC1 work needing no ruling; OPEN = still needs the founder.
GROUPS = [
 ("The S_k fix-acceptance gate: repair, remove, or leave", [10,55,69,98,114], "RULED",
  "Shipped threshold is below the true break-even at 297 of 297 settings.",
  "Founder ruled 2026-09-06: run the simulation with corrected values; study it after."),
 ("Push main to the public remote", [102], "DONE", "", "origin/main == HEAD, 0 ahead."),
 ("Appendix L38, the G_n reduction row, the spliced illustration", [103,104,105], "DONE", "",
  "All 3 applied, tested, and reproduced by committed scripts."),
 ("Commission severity calibration and stall-based termination", [8,100], "RULED", "",
  "Founder ruled: turn on and observe. 20 end-to-end tests exist, ON vs OFF."),
 ("The lapsed Codex/ChatGPT seat contrast", [5,61,96], "RULED", "",
  "Founder ruled 2026-09-04 'Approved, do as you suggest'. Specified as S1, NOT YET APPLIED."),
 ("Held-out status of exp50, exp51, exp52", [18,79], "RULED", "",
  "Founder: 'That we should run them.'"),
 ("Was the maths model refuted, or CC1's test?", [51,119], "DONE", "",
  "CC1's test. 3 of 15 assertions subtracted an expression from itself."),
 ("What the appendix tests actually conclude, and were they panel-checked", [52,53,120,121], "DONE","",
  "Answered and panel-confirmed."),
 ("State the discharge rule and its alternative", [54,122], "DONE", "",
  "Both written out in full in the 2026-09-05 note."),
 ("Adopt nu_eff = nu/|D|", [106], "DONE", "",
  "REFUTED twice, both Wolfram-verified. Closed."),
 ("The Wolfram Engine licence expiry", [19,63,109], "RULED", "",
  "Founder ruled 2026-09-06: set a reminder. Done, fires 2026-09-09."),
 ("Where the Reduction Criterion belongs", [64,115,124], "RULED", "",
  "Founder: put it to CC2 and Fable; references section deferred to discussion."),
 ("Run one-model-direct versus one-model-with-agents", [3], "RULED", "",
  "Founder approved. 3 configs built and validated, NOT LAUNCHED."),
 ("Who adjudicates the rubric's clauses", [101,112,118,123], "DONE", "",
  "Nobody does: it is a 4-way schema lookup. The FORWARD fix is separate, below."),
 ("Revive the six-model paid panel", [117], "RULED", "",
  "Founder: 'can wait until the morning.' Still deferred, costs money."),

 ("Restart or resume Exp 53, the zero-plant control", [26,91], "OPEN",
  "PAUSED mid-run at 4 rounds. This one leg blocks Exp 50, 51, 52 and BR2.",
  "RESTART. The 13 'irreducible' items were locked by the broken gate, so a resume carries a known artefact into the one experiment that measures what a panel leaves behind."),
 ("Does the rubric or the number govern severity, going forward", [9], "OPEN",
  "They disagree on 45.56% of judgeable cases and 77.1% of those have no executable falsifier.",
  "Put it to CC2 and Fable as you already directed, then apply what survives testing."),
 ("Who authors exp52's planted set, and the reseed", [17,76], "OPEN",
  "The old answer key is in git history. You ruled the exposure overstated; the reseed is still not done.",
  "CC1 authors it mechanically from the catalogue, and you spot-check. Reseed before Exp 52, not before Exp 53."),
 ("Do reviewing models keep Write and Edit access", [7], "OPEN",
  "Panel agents were caught editing the repo mid-run twice.",
  "Keep access, measure disclosure. You already approved this shape once; it needs confirming."),
 ("The 9 configuration gates no configuration enables", [6,67], "OPEN",
  "Dead switches: either they are wired or they are noise.",
  "Wire the 2 that have tests, delete the other 7."),
 ("Is the queue alarm's HALT intended, or should it be veto-only", [31,85], "OPEN",
  "It halted both Exp 55 attempts at round 1, which is why nothing has run for 12 days.",
  "Veto-only. A halt at round 1 destroys the run to protect a bound of 2."),
 ("Should a missed canary BLOCK convergence", [46,71], "OPEN", "",
  "No. Report the missed-canary count as a detection-rate measure; blocking makes convergence hostage to how well the seeding was done."),
 ("Exclude target-independent falsifiers from the corpus", [45,72], "OPEN",
  "8 are provably target-independent out of 372.",
  "Exclude the 8, keep the rest, and record why."),
 ("Merge semantics: fold, or delete-with-pointer", [11,15,43,77], "OPEN",
  "G7's merge path is dead code; genuine merging needs building, not enabling.",
  "Delete-with-pointer. Reversible, and it never destroys a finding."),
 ("Seal the 31 plaintext key files", [12,70,74], "OPEN",
  "Needs your passphrase; I cannot do it.",
  "Do it before any paid run. Commands are in the 2026-08-28 note."),
 ("Rotate the Zenodo token and fix the .env quoting", [97], "OPEN",
  "Your own hands. The token value has a leading space.",
  "Rotate at your convenience; nothing blocks on it."),
 ("Set hasTrustDialogAccepted in ~/.claude.json", [33], "OPEN",
  "A workspace-trust setting. Yours to make, not mine.",
  "Your call entirely. I have no view."),
 ("Discard the uncommitted temporary worktree", [4,68,95,129], "OPEN",
  "Already checked: the rejected alternative fix was preserved as a diff.",
  "Discard. Nothing useful is in it."),
 ("The critical-severity ceiling", [30], "OPEN", "", "Leave as is until the simulated run gives data."),
 ("Fix the block[:200] description truncation mid-arc", [20,81], "OPEN",
  "Truncation loses finding detail across the whole archive.",
  "Fix it now, before the simulated run, so the run's records are complete."),
 ("Adjudicate the 120 to 133 dropped similarity pairs", [21,82], "OPEN",
  "Already measured: 0 are HIL-irreducible; 85 of 133 have tool evidence.",
  "No adjudication needed. Supply 17 fixes, repair 11 equipment cases, record 4 containments."),
 ("Re-run Exp 48 and 49 under the new design", [48], "OPEN", "Costs money.",
  "Not yet. Wait for the simulated run."),
 ("Materiality of the C0015 and C0017 footnotes", [40,88], "OPEN",
  "2 grounded-but-unconfirmed footnotes from the Exp 41c convergence.",
  "Confirm them as iteration, not fundamental. They do not flip the convergence."),
 ("Implement gamma unification", [14,87,89], "OPEN",
  "Panel-endorsed, uncoded. Report the headline gamma on the genuine-critical series.",
  "Do it, but AFTER the simulated run, since it touches convergence machinery."),
 ("Spend one paid sentinel dispatch before a paid run", [32,86], "OPEN",
  "Confirms a model actually reads the new sentinel markers.",
  "Yes, but only once the simulated run is clean. One dispatch, not a panel."),
 ("Give DeepSeek a text-protocol tool fallback, or leave it unverified", [108], "OPEN", "",
  "Give it the fallback. An unverified seat in a 5-seat panel is worse than a slower one."),
 ("Account for the 6th panel seat whose outcome is never reported", [110], "OPEN", "",
  "Drop it from the record. It is CX2 and it has never been wired."),
 ("Severity is a model vote, not a tool (FW.7)", [93], "OPEN",
  "A model-assigned float currently gates convergence, which the no-voting rule forbids.",
  "Replace with the consequence-class rubric. This is the same decision as the rubric one above."),
 ("Exp 54 Cell A entry-method decision", [41], "OPEN", "", "Defer until Exp 53 completes."),
 ("Record the archive decryption instructions", [78], "OPEN",
  "One copy system-wide, unversioned on the Desktop.",
  "Yes, record them. A single unversioned copy is a real loss risk."),
 ("Relabel the 37 finding IDs reading CC2_F001 rather than CC2-SIM_F001", [73], "OPEN",
  "A provenance defect: simulated agents labelled as the real model.",
  "Relabel. This is the standing no-fake-model-labels rule."),
 ("Author the 5 unwritten prose targets", [29], "OPEN", "", "CC1 authors, you spot-check one."),
 ("The sweep cannot clear a critical (38 sub-criticals stuck)", [27], "OPEN", "",
  "Investigate during the simulated run rather than ruling blind."),
 ("The falsifier guard-versus-broken ERROR classes", [44], "OPEN",
  "16 of 25 unexplained.", "Investigate during the simulated run."),
 ("The arc-wide routing character class", [47], "OPEN", "", "Low stakes. CC1 decides unless you object."),
 ("Residual key exposure via the assistant's own session store", [49], "OPEN",
  "OS-level sandbox question.", "Raise it when we next touch keys; not blocking."),
 ("Materiality review of findings against TRUE claims", [50], "OPEN",
  "11 Exp 49, 6 Exp 48, 2 Exp 47 HIL residuals.", "CC1 drafts, you confirm in one pass."),
 ("The superseded Popper and Framework TTS drafts", [90], "OPEN", "", "Archive, never delete."),
 ("FW.6 harvested historical revisions as a recall target", [92], "OPEN",
  "Blocked on securing the 676-commit branch.", "Defer past BR2."),
 ("Confine real runs so panel agents cannot write to the canonical repo", [94], "OPEN",
  "Agents were caught editing the repo mid-run, twice.",
  "Do it before the next paid run. This is a containment fix, not a preference."),
 ("The open-topology anti-dispute safeguard", [39], "OPEN", "Named a real gap.", "Defer past BR2."),
 ("The A1 directive-pruning cuts plus ablation", [36,37], "OPEN", "", "Defer past BR2."),
 ("dm consolidation steps 2 to 6 plus rename", [38], "OPEN", "", "Defer past BR2."),
 ("The 18 May definitional confer's one-month PoC plan", [16], "OPEN", "",
  "Superseded by the current runway. Close it."),
 ("The 8 decisions in Handover Decisions 2026-08-24", [80], "OPEN",
  "A nested batch I have not opened.", "I open and summarise them before you rule."),
 ("The 6 decisions in Overnight Decisions Index 2026-08-12", [83], "OPEN",
  "A nested batch I have not opened.", "I open and summarise them before you rule."),
 ("The DECISIVE form of the false-CONFIRMED discrimination control", [24,84], "OPEN", "",
  "Defer until Exp 53 completes."),
 ("Disposition of ruling 1, prose-similarity and hierarchical novelty", [25], "OPEN", "", "Defer past BR2."),
 ("Spot-check the Open Brain record classification", [22], "OPEN", "", "One 5-minute pass when convenient."),
 ("Why ChatGPT and Codex are not separately available via OpenRouter", [127], "OPEN",
  "This is the seat-duplication finding in another form.",
  "Same answer as the seat contrast: restore one shell-bearing seat, or declare 4 architectures."),
 ("Does the rho = 0.564 scaling figure require action", [126], "OPEN", "", "No action. It is a measurement, not a defect."),
 ("Is the additional panel briefed on new mathematics as well as the gate", [111], "OPEN", "", "Yes. Brief both."),
 ("The three-model panel's scope", [75], "OPEN", "", "Same scope as the 2026-09-06 panels: solutions, not only faults."),
 ("How the past rubric data should be recorded", [113], "OPEN",
  "The conflict exists in archived data and nothing reports it.",
  "Record the conflict in the mathematical appendix and the reproducing guide, as you sketched on 2026-09-04."),

 ("Adopt the discharge rule, and pick which of the 2 refinements", [99,107], "OPEN",
  "You said we should build it, test it, and use it if it helps. What is still unpicked is WHICH refinement.",
  "Adopt the rule with the scope-declared-before-the-claim refinement, and leave empirical fits on their existing vocabulary."),
 ("The exp52 re-authoring three-model confer", [13], "OPEN",
  "Whether CC1, CC2 and Fable jointly re-author exp52's target.",
  "Yes, and run it on the free seats. It costs nothing and exp52 needs a clean target."),
 ("Reload the Open Brain launchd bridge", [23], "MINE", "", ""),
 ("CC1 answer/report/confirm items", [1,2,28,34,35,42,56,57,58,59,60,62,65,66,116,125,128], "MINE", "", ""),
]


def main() -> int:
    raw = []
    for line in JOURNAL.read_text().splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "result":
            continue
        r = d.get("result")
        if isinstance(r, dict) and "tasks" in r:
            raw += [t for t in (r.get("tasks") or [])
                    if t.get("founder_authority") == "OPEN_QUESTION"]

    covered = sorted({i for _, m, _, _, _ in GROUPS for i in m})
    missing = [i for i in range(1, len(raw) + 1) if i not in covered]
    counts = {}
    for _, m, st, _, _ in GROUPS:
        counts[st] = counts.get(st, 0) + 1

    print(f"raw OPEN_QUESTION entries        : {len(raw)}")
    print(f"distinct decisions after grouping: {len(GROUPS)}")
    print(f"collapse                         : {100*(1-len(GROUPS)/len(raw)):.1f}%")
    print(f"entries covered                  : {len(covered)} of {len(raw)}")
    if missing:
        print(f"  UNCOVERED (grouping is incomplete): {missing}")
    print()
    for st, label in (("OPEN", "STILL NEED YOUR RULING"), ("RULED", "you have already ruled"),
                      ("DONE", "discharged by evidence"), ("MINE", "CC1 work, no ruling needed")):
        print(f"  {label:32s} {counts.get(st, 0)}")

    if "--tts" in sys.argv:
        print("\n" + "=" * 60)
        n = 0
        for title, _, st, ctx, rec in GROUPS:
            if st != "OPEN":
                continue
            n += 1
            print(f"\n{n}. {title}.")
            if ctx:
                print(f"   {ctx}")
            print(f"   My recommendation: {rec}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
