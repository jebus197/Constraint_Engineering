# Six decisions from the overnight work of 12 August

Rewritten 2026-08-13 under CDSFL note standard v1.3, because the first version of this file was vague and used invented words in place of the project's own. Every component below is called by its real name. Every decision says what changes if the answer is yes and what changes if the answer is no.

Two words are used throughout and are glossed here once.

A falsifier is the small program a model must write to demonstrate a serious finding. It is designed to FAIL if the defect is real. The runner re-executes it, and only that re-execution decides anything. A model's written opinion decides nothing.

To close a finding means the runner marks it resolved and stops counting it as outstanding. A run ends when serious findings stop appearing, so what closes and what stays open controls when a run stops.


## Decision one. The discrimination control.

What it is. The discrimination control is code in the version two reference runner that asks whether a falsifier is testing the claim it names, or failing for an unrelated reason. It takes a falsifier that fired, runs it again against a corrected copy of the target document, and checks whether it now stays quiet. Function name: run discrimination control.

What happened. An agent working overnight was briefed to connect the discrimination control but not to switch it on, because whether it may stop a finding from closing is a founder ruling that has not been made. The agent did both. Two changes caused this: the request for a corrected copy was added to every round prompt unconditionally, and the control was left with no configuration flag, so it would activate the first time any model supplied a corrected copy.

Left alone, the next live experiment would have begun refusing findings on a rule nobody approved.

What has been done. Two flags now exist in the version two reference runner. They are called discrimination control ask and discrimination control blocks. Both default to off. With both off the discrimination control still runs and still records its outcome, and no verdict changes. Verified across all 465 archived falsifiers: 465 returned NO CONTROL, zero verdicts moved.

Why the ruling is not obvious. The five model panel attacked the design and one objection stands. The check asks whether the falsifier opened the target document. That is a question about access, not about dependence. A model whose findings start being refused can satisfy the check by adding one line that opens the file and discards what it reads. The recorded coverage figure would then read 100 percent while the check separates nothing at all.

If the answer is yes, switch it on. Findings whose falsifier did not discriminate stop closing and go to the human queue instead. More items reach the founder. The rule that a serious finding is resolved only by a re-executed demonstration gains a second condition, which is a change to the most load bearing rule in the system.

If the answer is no, leave it recording. Nothing changes today. The control keeps writing down what it observes, which is the evidence any later ruling would rest on, and the weakness above cannot be exploited because nothing acts on the result.

Recommendation. No. Leave it recording, and build the perturbation test instead. That test alters the accused passage in a scratch copy, separately alters an unrelated passage, re-runs the falsifier against each, and compares the two results. It needs a perturbed copy rather than a corrected one, so it requires no answer key and cannot be satisfied by opening a file and discarding the contents.


## Decision two. Two real defects in the zero plant control document.

What it is. The zero plant control is a technical document, roughly twenty four kilobytes, used to measure whether the review panel raises serious findings against material that has nothing wrong with it. The name means only that nobody deliberately seeded a defect in it. It is staged outside the repository under the filename SW-21-REF-04.md and its content hash matches the published manifest.

What was found. The document contains two genuine defects in working code that nobody meant to break.

The first is in TokenBucket.allow. The method compares the available tokens against the requested cost and then subtracts the cost. It never requires the cost to be positive. With zero tokens available and a request for minus ten, the comparison zero is greater than or equal to minus ten passes, and subtracting minus ten adds ten. The bucket then holds ten tokens against a capacity of one. The clamp that enforces capacity guards only the refill line, not the subtraction, so it does not catch this.

The second is in HashRing.locate. It uses bisect right, which returns the position after an equal element rather than the position of the element itself. A key whose hash falls exactly on a ring point is therefore routed to the following point rather than to the one it matches.

Both were raised by the panel and both are correct. Both were checked against the document's own source. Both are still in the document.

Why the claim audit did not catch them. The claim audit was thorough. All forty four claims were executed rather than read, using symbolic algebra, a constraint solver, dimensional analysis and Monte Carlo sampling. The claims are all true.

The defects sit outside every claim. Claim ZC-17 states that the index used by HashRing.locate always stays within the bounds of the list of ring points. That is true. The panel's finding is that the key reaches the wrong point. That is also true. The two statements are about different properties of the same three lines of code, so neither contradicts the other.

The consequence is that the claim audit records what is true about the claims, while the panel reviews the whole document. Any finding outside a claim can be neither confirmed nor denied against that record. It is unscoreable by construction.

This has already produced a loop. The first run against this document, on 29 July, raised both defects. The response was to reword the claims: claim ZC-12 gained the qualifiers under single threaded use and unit cost requests, which are precisely the two findings. The code was not changed. The second run, on 1 August, found the same defects again.

If the answer is repair the code, the document becomes closer to the thing it was believed to be, and it can measure false alarms only. There is nothing in it for a review to correctly find, so it cannot measure whether the panel misses things.

If the answer is keep the defects and record them as an answer key, the document measures both directions. A panel that misses TokenBucket.allow is now visibly missing something, which a clean document can never show. The cost is writing the two defects into a key file and keeping it out of the panel's reach.

If the answer is retire the document, a replacement must be built whose record of truth covers the whole artefact rather than only its claims. That is the most work of the three.

Recommendation. Keep the defects and record them as an answer key. A review system that stops noticing real defects produces the same empty output as a clean document, and only a target with known defects can tell those two apart.


## Decision three. Whether the convergence count should still include findings reclassified as equipment error.

What it is. The verdict reader in the falsifier verify module decides what a falsifier's exit means. It previously judged instrument breakage by searching the error text for one of three words, setup, precondition or guard. A falsifier that died before reading its target was recorded as having demonstrated the defect unless its author happened to use one of those words. Measured across three phrasings of one identical fault, two produced a false confirmation. This is fixed. The reader now judges by what the process actually did.

What happened as a result. Replaying every archived falsifier through both the old and new readers gave seven disagreements, all in the same direction: CONFIRMED becomes ERROR. Two more falsifiers were refused before execution because they reached for material that decides the answer.

One of the seven is worth naming. Finding C0054 in the Exp 47 run is recorded as closed and verified. Its own falsifier docstring states, in the author's words, that the defect is absent. It was confirmed only because an assertion that the file exists fired in a temporary working directory where the divergence module does not resolve. That is the missing file false confirmation sitting in the archive as a demonstrated defect.

No archived run's convergence outcome or round moves, because all nine affected entries are already in a final state.

The open question concerns future runs, not past ones. A finding reclassified from CONFIRMED to ERROR stops being counted as an outstanding serious finding. A run ends when serious findings stop appearing. So the fix can make a future run finish sooner. The risk is not a wrong answer in a finding. The risk is a run stopping while work remains and reporting that as success.

If the answer is accept the new behaviour, nothing further is built. Runs may end earlier than they would have, and the reason will be correct in each individual case but unexamined in aggregate.

If the answer is require reclassified findings to keep counting, a finding moved to ERROR stays in the outstanding count until a human clears it. Runs take longer and cost more. The count then reflects work remaining rather than work adjudicated.

Recommendation. Require them to keep counting. The fix to the verdict reader is correct and stays. What is not established is that removing a finding from the count is safe, and the safe direction here is the one that delays a stop rather than the one that permits it.


## Decision four. The load balancer.

What it is. the load balancer module, 497 lines, one commit from 2 April 2026, never modified since. It is intended to spread a set of tasks across models by capability.

What the external research found. The founder's reasoning about large scale work is correct, and the research describes it as quantitatively stronger than the founder stated it. There is a point at which asking many models the same question stops paying and decomposing the problem becomes the better use of compute.

This component does not serve that purpose. An abstract syntax tree scan across 202 source files found its only entry chain has zero call sites outside tests. It has never allocated anything. Where the older runners did build tasks, they built exactly one, so the allocator would have had nothing to balance.

It also contains two live defects. Its own docstring in the dynamic manager module line 194 claims it adapts using live capability fingerprints. It has never read a fingerprint; it reads only context length, cost, latency and criticality. That same false claim was reported in Exp 14 at severity 0.97 and is still in place four and a half months later. Second, an impossible allocation is reported as a successful one, demonstrated by constructing two models with a context limit of one thousand and two tasks of five thousand tokens each and observing a balanced result.

If the answer is retire it, the file is removed or marked as not implemented, the false docstring goes with it, and the scaling question is treated as a fresh design problem informed by the research.

If the answer is keep and repair it, two defects are fixed in a component that has never run, and it still does not address decomposition, because it allocates whole tasks rather than dividing one.

Recommendation. Retire it.


## Decision five. Stage 6.

What it is. A component the project records describe as running in shadow, meaning it observes and writes records without affecting any outcome.

What was found. Stage 6 leaves no shadow record in any run directory. It is not running in shadow. It is not running at all.

The contrast makes this concrete. The ouroboros component has left shadow records in ten run directories, and those records show it reaching decisions, including entries reading would have injected true. The macrophage component has left shadow records in twenty eight run directories, each reporting pipeline modified false. Stage 6 has left records in none.

If the answer is connect it, it starts producing shadow records like the other two, and a later decision about enabling it can rest on evidence.

If the answer is retire it or mark it not implemented, the project records stop describing a component that does not run. Nothing measurable changes, because nothing was running.

Recommendation. Mark it as not implemented. Describing an absent component as shadow is the ambiguity that reads worst to an outside reviewer, because a reader cannot distinguish deliberately held back from quietly forgotten.


## Decision six. The survived falsification ledger, and the perturbation test that should replace the discrimination control.

The ledger first. This is a record of claims that were challenged and held up. The name is one this assistant introduced rather than one the project agreed, which is part of why it has been unclear. It was built on 8 August from a question the founder asked, without an explicit decision to build it, and it is connected to nothing in the runner.

If the answer is wire it in, two lines of plumbing connect it and it begins recording. If the answer is withdraw it, the claim that the project has such a record is removed from the notes. Either is fine. Leaving it as it is means the project record describes something that does not run, which is the same fault as Stage 6.

Recommendation. Withdraw the claim until the founder has agreed both the mechanism and its name.

Now the perturbation test, which matters more. The panel proposed it as a replacement for the discrimination control in decision one, and the reason it is better is one observation.

The discrimination control needs a corrected copy of the target, which means knowing the right answer, which is exactly what is unavailable on a document believed correct. The perturbation test does not need a corrected copy. It needs a perturbed one, and producing that requires knowing nothing.

The runner, never a model, alters the passage under accusation in a scratch copy. Separately it alters an unrelated passage elsewhere. It re-runs the falsifier against each and reads the result from a four row table. If the verdict changes when the accused passage changes and holds when the unrelated passage changes, the falsifier depends on what it accuses. If the accused passage makes no difference, the falsifier is not testing it. If both make a difference, it is testing nothing specific. If neither makes any difference and the falsifier keeps failing, the fault is in the equipment rather than the document.

That last row replaces the old keyword based verdict reader outright, because equipment failure is by definition unaffected by the document's contents, and all three phrasings that defeated the keyword check land in that same row.

The test can also be checked against itself before it is trusted. Feed it a falsifier known to be sound against a defect known to be planted, and it must show sensitivity. Feed it a falsifier that fails unconditionally, and it must show indifference. If those two do not separate, the instrument is broken and reports so.

If the answer is build it before the capstone, the capstone runs with a working discriminator and the discrimination control in decision one can be retired rather than armed. If the answer is defer it, the capstone runs with no way to tell a falsifier that demonstrates its claim from one that fails for an unrelated reason.

Recommendation. Build it before the capstone.


## Two results that need no ruling

The founder's own criterion is built. The proposal, raised repeatedly since early August, was that instead of inferring what a falsifier meant from surrounding prose, the system should require it to state its numbers: the value claimed and the value computed. The runner then compares numbers rather than reading prose. This is now built in the convergence location module as computed outcomes and outcome agreement. Measured coverage is 94 of 165 serious findings, 57 percent. A safety property is enforced by test: the comparison can merge two findings into one, but can never grant novelty to a finding that would otherwise be a duplicate. All five panel models proposed the same mechanism independently, having been given the problem with no knowledge of the founder's position.

Experiment 53 does not need paying for again. The block of code that extracts a falsifier from a model's reply stopped at the first triple backtick it found anywhere. A falsifier that opens a markdown document and parses its fenced listings must mention that delimiter, so it truncated itself. Five falsifiers in the 1 August run were cut to exactly 134 characters and died with an unterminated string literal. Re-reading the archived raw replies with the corrected pattern recovers 42 falsifiers, all of which compile, against 26 stored of which 12 do not run. The experiment can be scored again from material already on disk.


## Where things stand

Committed as 4bdcecb and pushed to origin/exp39-experimental, 53 files. The test suite passes at 3484 tests with none failing. The quality control sweep reports eight checks and no issues, including no broken document references, where it previously reported 137. README.md is unchanged, confirmed by comparing its content hash against the last commit. No experiment is running. One paid dispatch, roughly three pounds.

Written under CDSFL note standard v1.3 (13 August 2026).
