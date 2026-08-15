# Experiment 43, Overnight Run and Contested-Convergence Analysis

**Preserved into the repository 2026-08-06 02:15 .** Exp 43 result and the contested-convergence diagnosis. Cited as live detail by the tracker. READ WITH ITS SUCCESSOR: the FIX design it motivated was CODED on 2026-07-27 in commit `1cec60d` and shaken out by Exp 44, which converged at round 12 with zero residue. Nothing here is outstanding work.

**Provenance.** This is the plain-text text-to-speech document from `~/Desktop/CDSFL_tts/Exp43_Overnight_and_Contested_Analysis_2026-07-19.txt`,
preserved VERBATIM below rather than rewritten. It is a record, and rewriting a record is a fault in
this project. It was cited by name in `RECOVERY.md`, `CDSFL_Agent_Operational_Plan.md`
while existing on one machine's Desktop only — and `resources/RECOVERY.md` opens by promising a reader
can rebuild everything from the repository alone. That promise now holds for this document.

---

Experiment 43, Overnight Run and Contested-Convergence Analysis

2026-07-19, 09:30 BST.

Register note. This file is written at the founder's explicit request in full technical register, retaining formal CDSFL terminology rather than the usual plain-English TTS form.


Part One. What happened overnight.

The first Experiment 43 launch ran five rounds cleanly on all five panel models, CC2 via the Claude command-line subscription, ChatGPT, Codex and Gemini via OpenRouter, and DeepSeek via its direct API. During round five, OpenRouter reached credit exhaustion and returned HTTP 402, insufficient credits. Because ChatGPT, Codex and Gemini all route through OpenRouter, three of the five models failed simultaneously, and the routing failover collapsed as well. The run was paused under the cy monitoring protocol to avoid completing a degraded two-model experiment and to preserve state. All per-round checkpoints through round four were intact.

The founder topped up the OpenRouter account with one hundred dollars, bringing the balance to ninety nine dollars and eighty one cents.

Before resuming, a full integrity verification was run, on the founder's instruction, to ensure no Experiment 42 convergence failure modes and no regressions were present in the runner. Three things were confirmed. First, git was clean with no uncommitted changes to the runner or any convergence code, and all convergence machinery was committed and present, the two-sided gamma gate, the location-keyed novelty that fixed Experiment 42's cross-round deduplication failure, routing, the falsifier gate, and merge-arbitration. Second, the convergence-critical test suite passed, fifty seven tests green across the two-sided gate, location-key, routing, merge-arbitration, falsifier gate, and gate-condition modules. Third, the Experiment 43 configuration was byte-identical to the Experiment 42 landmark configuration on every operative flag.

However, the resume checkpoint was found to be contaminated. Rounds zero through four each recorded all five models. Round five recorded only three findings from two models, the survivors of the OpenRouter cascade, yet the checkpoint had marked completed round equals five. A naive resume would therefore have treated a broken two-model round as a finished five-model round and built round six on top of it. On the founder's decision, the checkpoint was discarded and Experiment 43 was re-run from the top, a fresh run directory, all rounds, the full five-model panel throughout, on the verified-clean runner and identical configuration, with the environment noise and the inherited ANTHROPIC_BASE_URL variable stripped.


Part Two. The clean re-run result.

The clean run completed fourteen rounds in about six point three hours. It did not achieve clean convergence. The convergence gate requires three consecutive gate-passing rounds, and the run never strung three together.

The important detail is that this is not a repeat of Experiment 42, and the machinery is largely vindicated. The critical over-production that prevented Experiment 42 from converging is solved on this new target. The location-keyed critical series settled to zero, zero, zero and held there from round six through round eleven, meaning the criticals genuinely converged. gamma critical engaged and held around zero point five seven, well above the zero point three zero threshold, through the back half of the run. The two-sided gate actually passed in full on two rounds, round four and round eleven, which proves the convergence machinery works end to end on a brand-new module. This is the generalisation Experiment 43 was designed to test, and it held.

What blocked the clean three-consecutive streak was a single named dimension, a residual churn of contested findings. Contested findings are findings carrying unresolved CHALLENGE verdicts, that is, model disagreement not resolved by a CONFIRM. The gamma-alt critical-quiescence check reported the criticals quiescent at zero, zero, zero from round six onward, but blocked by contested counts of one to three. Every late-round gate failure reads contested equals one, occasionally with a small novel batch of three or four. The critical side settled. The dispute side did not fully settle.

The full re-run cost thirty five dollars and thirty cents, roughly two dollars fifty per round, exactly in the projected band. The balance stands at sixty four dollars and fifty one cents.


Part Three. The contested-convergence failure mode, analysed.

Is this a new failure mode. Largely no. It is the same class of problem as Experiment 42's over-production, perpetual low-level activity preventing the strict endpoint, but now expressed in the contested dimension rather than the novel-critical dimension. Experiment 42's problem was that new criticals arose every round and never settled. The location-keyed fix solved that. What remained is a lower-level churn of contested verdicts.

Have we addressed contested before. Yes, more than once. The runner already contains a purpose-built apparatus. There is auto_resolve_contested, called each round. There is escalate_stale_contested, labelled in the source as the A3 fix, escalate stale contested findings to human-in-the-loop after a threshold, with a max_contested_rounds threshold of five. There is a grace_period of two rounds in contested_count, and the git history records a prior contested_count grace_period regression that was fixed. And there is the irreducible-escalation mechanism, which for criticals that exhaust the routing ladder marks them irreducible, counts them in a separate irreducible-queue guarded by a max_irreducible_queue cap of two, and excludes them from the blocking count so the gate can close around a small human-review queue. That last mechanism is exactly the pattern the founder described.

Why did the existing apparatus not fire this time. Two reasons, both mechanical, neither a flaw in the mathematics. First, escalate_stale_contested only triggers when one finding has been contested for five consecutive rounds. The disputes here were churning, arising and clearing within the two-round grace window, so no single finding aged to the five-round threshold, and escalation essentially never fired. Second, and more fundamental, contested_count excludes only terminal statuses, MERGED, CLOSED, REFUTED, DUPLICATE, CONFIRMED. It does not exclude human-in-the-loop-escalated items the way the irreducible-queue excludes escalated criticals. So there is an asymmetry. Ladder-exhausted criticals are pulled out of the count and the gate closes around them. Contested findings are not. The human-in-the-loop escape that exists for criticals was never extended to the contested dimension.


Part Four. Is fixing it feasible.

Yes, and it is a modest, well-precedented change, not a rebuild. The fix is exactly the founder's proposal, and it mirrors machinery that already exists for criticals. A contested finding that the tools cannot resolve, after auto_resolve_contested and after routing, should be marked as an irreducible human-in-the-loop dispute, excluded from the contested count, placed in a small contested-dispute queue guarded by a cap in the same manner as max_irreducible_queue, and flagged for human review, so that the gate, and gamma, close around that small queue rather than being blocked by it. Two adjustments implement this. First, lower or make adaptive the escalation trigger so churning disputes, not only five-round-stale ones, reach escalation. Second, make contested_count exclude human-in-the-loop-flagged contested findings, and add a small-queue cap and alarm exactly as the irreducible-critical path already does.

This is also more faithful to the founding rule, tools decide, not votes. A contested finding is a vote-standoff. Under the CDSFL design a vote-standoff the tools cannot break should be handed to the human, the final falsifier, and must not hold the gate hostage. The current behaviour, a churn of unresolved votes blocking convergence, is the one place the implementation drifts from that principle.


Part Five. Bottom line.

Experiment 43 did not cleanly converge, but it vindicated the mathematics and the location-keyed convergence instrument on a second, independent target, and it isolated the remaining gap to one specific, named, mechanical cause with a precedented fix. This is the specific-known-problem outcome, not the endless-faults outcome. Further work is bounded, not open-ended.


Written under CDSFL note standard v1.2 (14 May 2026), technical register at founder request.
