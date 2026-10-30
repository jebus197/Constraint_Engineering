# Answers to the 7 questions of his that nothing was tracking

2026-10-29 22:37 GMT. HEAD 5180b471. All 7 are HIS questions to me, so what they need is answers, not rulings. The consolidated report filed them under "verdicts required from you", which was a category error: by his own ruling of 2026-10-19 a question's resolution is an answer, not a build, and these run from him to me.

A note on why they looked settled. Each carries a `ruled:` date in the register. That field does not mean a ruling was given: `scripts/harvest_tickets_2026-10-17.py:405` sets `"ruled": ts[:10] if role == "user"`, so for a harvested item it is simply the date he wrote the message. `scripts/register.py:243` then prints it as ` ruled:DATE`, which makes an unanswered question look decided. That display is itself worth fixing for the `qs` kind.

---

## 1. `qs:c156469d2f14` — "There is something you feel we should discuss about this?"

He was annotating: a test written on 11 September which exists to fail if the task list stops terminating, gone red and left red deliberately.

**Answer: yes, and it is the same thing reported to him tonight.** That is the task-list termination measure. It was red on 17 October and it is red again now: new entries added per entry closed is R = 0.803797, 95% interval [0.636696, **1.014754**]. The point estimate is below 1 and a one-sided exact test rejects R = 1 at p = 0.0377, but the guard reads the upper bound, which has crossed. The cause is recording debt he asked to be recorded: 2 entries added on his instruction with 0 list entries closed. 3 further closures return the bound to 0.994885.

The discussion the test wanted is therefore live, and the recommendation stands: let it recover by closing entries, not by switching the guard to the point estimate. Loosening a guard so it passes is the move this project exists to refuse.

## 2. `qs:4691ab3af39c` — "You are assigning attributions for finding faults to me? I don't recall saying this."

**He is right. He did not say it.**

The sentence attributed to him is: *"A code comment about the symbol kappa is false by count, and the coherence penalty itself does appear in the tree inside a prompt used for a mathematics audit, which both seats' comments drop."* `experimental_notes/CDSFL_MASTER_TASK_LIST.md:1293` carries it under the heading "HIS WORDS, 2026-10-16".

Checked against the source. The sentence does occur in `Responses/READ_THIS_ONE_Decisions_2026-10-16.txt` — in the BODY of that document, which is my own report to him. His own contributions to that file are its 9 annotation lines, each prefixed with a hash, and none of them is this sentence. So the observation was mine or a seat's, written in a report addressed to him, and then quoted back as his.

This is the pattern already recorded in this project as advice acquiring his authority, and his ruling of 2026-10-19 names the discipline that should have prevented it: a quotation must be produced by reading the source and the source must be named. The attribution was produced from the document without distinguishing its body from his annotations.

**His second question, is it fixed: the substance yes, the attribution no.** The kappa and glossary work is complete. `docs/GLOSSARY.md:122` records the 2026-10-17 re-check by execution, names its producer at line 126, and 5 guard tests hold it with 4 of 4 mutations caught. What is not fixed is the credit line, and that is a 1-line correction to the task list entry, held only because a full board is mid-run against the current tree.

## 3. `qs:ff7b6d97b33d` — "Is this the same issue you raised before about a small percentage of subcritical items?"

**Answer: no, different things, and his recollection of the figures is close but not exact.**

What he was annotating is 4 faults in the register's identity and text integrity: identity digesting an entry's prose so 5 references carried 2 tickets each and 114 of 141 identities re-minted in one step; 9 of 141 titles naming a different entry; a label comparison that could never converge because a 160-character string was stored stripped to 159, rewriting 18 of 141 rows on every run of an append-only file; and 22 of 141 ticket texts reduced to stubs. That is about whether the register can name its own contents.

The subcritical-percentage question is about findings below the severity cut and what becomes of them. A different subject.

His figures, as recorded: the class debated was measured at **0.93 per cent demonstrably and at most 6.5 per cent conceivably**, with **70.43 per cent** of the population not unresolvable but unattempted. He remembered 7 per cent revised to 2 per cent, which maps onto the 6.5 and the 0.93 in the right direction and the right order of magnitude. The measurement cut against the premise of the argument it settled: the class whose size was being debated is 2 orders of magnitude smaller than the class nobody had measured.

His ruling on what to do with them, feeding them back into the harness for resolution, is recorded. Whether a mechanism now does that is NOT established by this pass and should not be claimed either way; it is the one part of this answer that needs a measurement rather than a reading.

## 4. `qs:514829474aa6` — "Is there something to be fixed here? If it means correcting 800 archived messages that is clearly a very large task. Is it done? Is it necessary?"

**Answer: the repair is done; the 800 are not a task at all; and his instinct that it would be large is right, which is part of why it is not being attempted.**

The fault: the merge resolver located a finding identifier with an unanchored search, and the label CC2 is itself a letter C followed by a digit, so the composed identifier CC2_F004 reduced to C2, which no alias key holds. The topology specification mandates reading an unresolved merge source as a confirmation on the target, so every merge that seat ever proposed was recorded as that seat agreeing the target is real. The verdict inverted rather than being lost. Measured by calling the resolver with the alias map populated as the register populates it: 2 of 12 seat labels failed, 16.6667 per cent, Clopper-Pearson [2.0863, 48.4138], and they are the same 2 he named.

**Done:** every candidate identifier in the string is now tried in the order the string gives them, so anything that resolved before resolves identically and what is added is a later attempt when an earlier candidate fails. 18 guard tests, both affected labels pinned by name so a sweep that stopped covering them could not look green, 2 of 2 mutations caught.

**Not necessary, and not possible:** a resolved merge is recorded one way and a failed one as an ordinary confirmation, indistinguishable from a genuine one. All 800 archived merge verdicts are therefore successes by construction, so the record cannot show which were inverted. Correcting them would mean deciding by guess which to rewrite, and his own standing position is that history is not to be rewritten. The honest statement is that the archive's merge verdicts from before the repair carry an unquantifiable error, and that this is recorded rather than repaired.

## 5. `qs:6a8c53b0c1bd` — "So all the recent work we did on this is safe or not? What is so special about a model's name? Did you implement this work, or do issues remain?"

**Answer: implemented, and the live path is clean. 1 vestige survives but it is inert, and the misleading part is a dangling import rather than any behaviour.**

His ruling, verbatim from his annotation on `Runway_Status_And_Is_It_Safe_To_Merge_2026-10-16.txt`: *"We normalise going forward, since recording vendor names is purely a recording statistic and has no impact on capability, or how our experiments work"*. And from the same window: *"I am not suggesting rewriting history. Just to be clear. The hashed model ID's rather than deriving capability by name is a relatively new feature."*

Capability is keyed on identity, not name, and 2 guards hold it: `bench/tests/test_capability_is_keyed_on_an_identity_not_a_name_2026-10-17.py` and `bench/tests/test_an_unregistered_seat_is_named_not_defaulted_2026-10-17.py`.

The vestige: `bench/runner_core.py:133` defines `CONVERGENCE_EXCLUDED_MODELS = {"DeepSeek"}`, a vendor name deciding whether a seat's findings count toward convergence. 19 files import it. Checked by abstract syntax tree rather than by text search, because importing a name and using it are different facts: the current runner `bench/reference_runner_v3.py` imports it at line 319 and has **0** load or assign sites for it anywhere else, and the same holds for `bench/reference_runner.py`. The only live use is `bench/run_exp12_live_wire.py:729`, a runner from the Exp 12 and 14a era, which filters findings and responses by model identifier against that set.

So in the current experimental path no vendor name excludes a seat from convergence. What remains is an import that reads as though the current runner honours a name-keyed rule when it does not, which is the unwired-addition shape rather than a live fault. Recommendation: delete the dangling imports, leave the definition in place for the Exp 12 runner that still reads it, and record why that seat was excluded in the era when it was, because the comment at the use site explains the decomposition exclusion and says nothing about the vendor exclusion.

## 6. `qs:7f90c6872fa7` — "That was only one of the fixes suggested for prose-heavy targets. Was the panel review ever done? If not you should do this too and apply the full solution."

**Partially answerable, and the honest answer is that the panel review WAS done and whether the full solution was applied is not established here.**

2 panel records exist: `experimental_notes/Panel_Review_Prose_Adaptation_2026-08-01.md` and `experimental_notes/Panel_Enforcement_Prose_FULL_RECORD_2026-08-19.md`, with a design note `Prose_Acceptance_Stage_2026-08-01.md` and its plain-English companion. On the code side the prose path is live in `bench/reference_runner_v3.py` and carries 3 guards: `test_prose_acceptance_stem.py`, `test_target_kind_and_no_score.py`, and `test_the_prose_target_is_fit_for_arm4_2026-10-14.py`.

What is NOT established: whether every element the panel named as part of the full solution is present. Establishing it means reading the 2 panel records for their enumerated recommendations and checking each against the tree, which is a bounded piece of work and is the right next step rather than a claim to make now. It should not be put to a further panel before that check, because the panel's answer already exists and the open question is whether it was implemented.

## 7. `qs:41b9aab3df0e` — "Replay is not significant. I asked if the combined design was an improvement over relying purely on your memory and the recovery resources. Should we adopt it for the project as a whole? Why would you find it useful but our models in experiments wouldn't?"

**Answer: the rhetorical question is the strongest argument in it, and it should be taken literally.**

His point is that a facility useful to the orchestrator for the same reason should be useful to a seat, and that asymmetry needs a justification rather than an assumption. There is no good justification for it. What the register gives me is a durable identity for an issue that survives rewording, a recorded state rather than an inferred state, and a refusal when work is written down without being registered. A seat in a long experiment faces exactly those 3 problems: it restates findings it has already made, it cannot tell an open item from a settled item across rounds, and nothing stops it proposing work that is already recorded.

So the recommendation is to adopt it, with 1 boundary stated plainly. The register is a RECORDING instrument, and giving seats write access to a shared register during an experiment would let 1 seat's entry shape another's reasoning, which is the blindness the design protects. The form that keeps the benefit without that cost is a per-seat register during the experiment, merged on convergence, so identity and state survive within a seat's own history and no seat reads another's.

On replay and rewriting history: agreed and not proposed. Nothing in this requires touching the existing record.

---

## What this leaves

Of the 7, 5 are answered outright, 1 (`qs:ff7b6d97b33d`) is answered with 1 named measurement still owed, and 1 (`qs:7f90c6872fa7`) is answered with a bounded check still owed. 2 corrections to the record fall out of them and are held only because a full board is running against the current tree: the kappa attribution at master task list line 1293, and the `ruled:` display for the question kind.


---

## ADDENDUM: the measurement owed on question 3, taken

Question 3 left 1 thing unestablished: whether a mechanism now does what his ruling asked, namely feed sub-critical items back to the seats for resolution instead of to him. Measured by reading the live code path rather than inferring it.

**The residual queue exists and it does something different from what he ruled.**

`bench/reference_runner_v3.py:4522` defines the residual queue: UNCONFIRMED findings below the severity cut whose falsifier errored or was absent. Its own docstring states the disposition: excluded from the contested tally, which gates convergence, and in its own words "surfaced here for logging + human review". The call site at line 9561 confirms it, in a comment written to be read: the residuals are "logged (never gate) so the review queue is explicit, not silent", with a warning when the queue exceeds 6 because a large queue signals a mechanical fault rather than genuine residue.

So the 3 things that happen to a sub-critical item with no demonstration are: it is kept out of the gate, it is written to the log, and it is put in front of a human. None of those is resolution by the harness.

**Why the difference matters rather than being a quibble.** Routing these items to human review increases the human load, and the project's stated direction is minimal human intervention. His ruling pointed the other way for exactly that reason: feed them back to the machine. The current behaviour is defensible as a fail-safe, since an item whose falsifier did not run has no evidence either way, and a machine cannot resolve it without evidence. But it is not what was ruled, and the gap had not been stated.

**The decision this leaves him.** Either the present behaviour is accepted and the ruling is recorded as superseded by the fail-safe argument, or the ruling is implemented, which means re-dispatching an un-demonstrated sub-critical to the seats in a later round rather than to him. The second is the additive option and the measurable choice: the residual queue size is already logged every round, so the effect of re-dispatch on that number would be visible immediately.

**A smaller thing found in the same pass, and it is clean.** The severity cut is duplicated across modules, which is the shape where a producer and a consumer drift apart. Checked by importing all 3 and comparing the live values rather than reading the constants: `reference_runner_v3` and `audit_closing_window` both hold 0.7 and agree. `bench/evidence.py:794` carries a comment claiming the value is kept in step there, but the module exposes no such constant at import, so the comment describes a coupling that does not exist. No drift, and 1 stale comment.

Written under CDSFL note standard v1.8 (17 October 2026).

---

## ADDENDUM 2: the check owed on question 7, taken

Question 7 asked whether the prose panel review was ever done and whether the full solution was applied, and said that if the panel had not supplied the full solution it should go to a further panel. **The review was done, the full solution is applied, and no further panel work is owed.**

**What the panel enumerated.** `experimental_notes/Panel_Review_Prose_Adaptation_2026-08-01.md:123` names the recommended work as 5 items plus 1 it explicitly defers: type detection, the refusal to launch, the offline acceptance test, turning off the scoring pipeline for a prose target, and surfacing rejection reasons to the panel. The 6th, structural quality gates for a future prose scoring stage, the panel itself placed after the immediate work, to be calibrated on local fixtures before being allowed to admit anything.

**What the tree holds.** All 5 are present in the product and each carries at least 1 guard named for prose or for a non-Python target. 11 such guard files exist: prose acceptance, target kind and no score, one-sided prose gates, low-severity injection surfaced, hard gates on a non-Python target, falsifier reaching a prose target by relative path, prose listings scoreable, prose prompt and falsifier, prose target tool bypass, prose target fitness for arm 4, and verification on a non-Python target.

**Run at HEAD 5180b471: 442 tests across those 11 files, 0 failures.**

**A correction to the method, because the first pass of this check was unsound.** The first attempt matched broad regular expressions over the tree and reported all 5 elements present. 2 of those matches were coincidental: a search for a surfaced rejection reason matched the ticket store and a divergence test, neither of which has anything to do with prose. A pattern match is not evidence that a specific recommendation was implemented. Rescoping the search to prose and then RUNNING the guards whose filenames name prose or a non-Python target is what established the answer, and it is the same lesson as `execute-do-not-grep`: the executed result is the evidence.

**The 1 thing worth his attention in it.** Item 4 is described in the panel record as disabling the scoring pipeline. Under the additive standard a disablement needs a committed measurement showing the replacement dominates. Here the justification is narrower and sound: the structural quality score, which runs from 0.0 to 1.0 over a code target, measures nothing when computed over prose, and the guard `test_target_kind_and_no_score.py` holds the property by name. It is a scope restriction on a target kind rather than the removal of a capability, which is why it does not fall foul of the rule. Stating that distinction is worth doing, because a future reader meeting the word "disabling" in the panel record would be right to challenge it.

Written under CDSFL note standard v1.8 (17 October 2026).
