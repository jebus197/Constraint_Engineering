Experiment 44 Result. Clean Convergence, First Time, Zero Residue

2026-07-27, 05:15 BST.


Summary

Experiment 44 converged cleanly at round 12, on the first attempt, with every finding in the registry resolved to a terminal state and an empty residual queue. This is the clean, blue water convergence the programme has been working toward: the first run in the project's history to reach its formal convergence endpoint with zero open, zero unconfirmed, and zero contested findings remaining. The five mechanical fixes designed after Experiment 43 did exactly what the pre-registered prediction said they would, and the one fault class that blocked Experiment 43 never appeared. Total wall clock was about three point seven hours, from 01:27 to 05:08 BST. The founder had designated this run as the decision point on funding the remainder of the experimental arc.


The Headline Numbers

The run reviewed the evidence layer module, about 23 thousand characters, under the same instrument as the two prior landmark experiments, with the five fixes as the only declared changes.

Eighty two findings were registered across thirteen rounds. At convergence, sixty three were closed with verified fixes, thirteen were confirmed by runnable demonstration, one was merged as a duplicate, and five were refuted. Nothing was left open, nothing unconfirmed, nothing contested. Six items exhausted the full escalation ladder and sit in the small guarded queue for human review, which is the designed role of the human as final falsifier. The residual queue of un-demonstrated low-severity items, the new mechanism from fix one, finished empty.

The convergence gate passed all its conditions together for three consecutive rounds, ten, eleven, and twelve. At the end, the critical decay measure, gamma critical, stood at 0.453, well above the 0.30 threshold, and the location keyed count of new critical findings had been zero for five consecutive rounds. Both sides of the two sided gate, the decay curve and the strict zero count, agreed, as the mathematical model says they should.


The Fixes Performed As Registered

The pre-registered prediction was clean convergence within the round budget with no low-severity item blocking the gate. That is what happened, and the mechanisms can be watched working in the log.

The fault class that blocked Experiment 43, an undemonstrated low-severity item counted as contested, never occurred, and the residual queue built to catch it finished empty. When a genuine critical with an untestable claim appeared at round seven, it was counted as contested, correctly, protected at full weight, routed up the ladder of stronger models, and, when the ladder was exhausted, placed in the guarded human review queue, after which the gate closed around it. That is the exact designed behaviour, distinguishing genuine disputes from unfalsified noise.

The location key, the mechanism that cured the earlier duplicate counting failure, was seen doing its job at round ten: a critical that a model re-raised under a new identifier was recognised as a re-find by its code location and correctly not counted as novel. The capability routing ladder resolved eleven findings by handing them to stronger writers during the run. Two attempts to reopen long-closed findings were logged for human review while their verified fixes stood.


What This Result Establishes

Three experiments now form a sequence. Experiment 42 proved the convergence instrument on one module after the duplicate counting cure. Experiment 43 generalised the instrument to a second module but was denied formal convergence by one mechanical artifact. Experiment 44, with that artifact fixed, delivered the complete result on a third independent module: formal convergence, zero residue, first attempt, no human intervention during the run.

The pattern the project predicted is holding: each experiment's faults have been mechanical, bounded, and fixable, the fix each time is smaller than the last, and this run needed no fix at all. The mathematics has not been the problem at any point. The diminishing returns principle at the heart of the model was visible in the raw data of this run, with finding counts falling from eleven at the start to two or three per round at the end, and the decay curve flattening exactly as the theory describes.

One review question for the founder: the six items in the guarded human queue await adjudication, and the post-run materiality review should confirm none of them hides a genuine critical. That review, plus the committed audit of remaining shadow code, are the queued next steps. The cost of the run is estimated at twenty to thirty dollars against the earlier estimate band; the exact figure is on the provider dashboard.

The founder's stated decision now falls due: this was the run set to determine whether funding the remainder of the arc, roughly five more experiments at similar cost, makes sense. The result it was waiting on has arrived, and it is the clean one.



## Correction and reframe (10:45–11:15 BST, post-run investigation)

**The "6 irreducible HIL items awaiting review" line above was WRONG — a stale-flag counting artifact, corrected as follows.** Registry provenance shows all six were RESOLVED BY THE PANEL ITSELF via later-round routing (`resolved_by_routing`: Codex ×3, CC2 ×2, ChatGPT ×1) — each ended CLOSED with a CONFIRMED runnable falsifier and verified fix. Genuinely-open irreducible items: **ZERO**. The stale `irreducible_escalation`/`hil_escalated` stamps (set when an early-round ladder failed, never cleared on later success) and the unfiltered `irreducible_queue_count()` produced the false "6". Both defects fixed + test-pinned (commit `84a372b`); on the gamma-alt path the stale count could have FALSELY refused a genuine convergence — a latent false-blocker now removed.

**The corrected headline is therefore stronger:** 82 of 82 findings decided by tools and panel; zero left to the human; zero genuinely irreducible; the only human-review items are two REOPEN attempts (audit-trail review, not pending work). By all reasonable measures this is the project's cleanest convergence: no compelled convergence, no hacks, no compromises — the two-sided gate closed because the mathematics and the experiment genuinely agreed.

**Gemini C0007–C0009 empty descriptions RESOLVED:** Gemini's round-0 response was 12,197 chars of well-formed JSON — not empty. The parser's JSON path mapped only `DESCRIPTION` and dropped Gemini's FFF key `FIND`; content was present, harvest incomplete (the recurring Gemini parse-loss class). Fixed + test-pinned in `84a372b`.

Written under CDSFL note standard v1.2 (14 May 2026).
