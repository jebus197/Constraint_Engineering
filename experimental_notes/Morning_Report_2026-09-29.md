# Morning Report — 2026-09-29

2026-09-29, 02:37 BST (updated 08:45 with the shakedown check)


## The Short Version

The board is green. The confirming run finished at 03:15 with 8,878 tests passing, none failing, and 6 skipped, under the strict network guard. Twelve failing tests were fixed in total, none by weakening a check, and the ten pound paid panel was not needed. The two free seats resolved everything between them.

The runway item you named is unblocked. Nothing now stands between the project and the simulated experiment plus the study of the last three weeks of fixes.


## The Finding Worth Knowing First

Three of the four board failures had a single cause that nobody was asked to look for.

Four runs from 21 and 22 September were being counted as real archive evidence. They are not real. They are simulated rehearsals, and the tool that made them says so plainly: every seat in them is a stand-in.

The mechanism is precise. The audit that decides whether a run is simulated checks each file individually, but the runner only writes its provenance markers into a run's main report. A simulated run also leaves a state dump beside that report. The state dump carries a version field, so the audit accepted it as a report; it carries none of the provenance markers, so the audit judged it real; and it sits in a directory whose name does not begin with the simulation prefix.

Those four state dumps were the newest files the audit accepted. Because they set the age baseline, the baseline moved forward by 26.3 days. The consequence is not cosmetic. It silently switched off the too-new quarantine for every control committed inside that window. One control reported itself as having run and stayed quiet, when the truth was that the archive was older than the control itself.

That is now corrected. Simulation is treated as a property of the run rather than of the file, and the effect is to make the control stricter, not looser.

One correction against myself. The brief sent to the review seats stated that none of the three remaining failures was a code defect. One of them was, and a seat said so rather than accepting the framing.


## Your Question On The Two Calculations, Answered

You asked for whatever gives the best results in both use cases: accuracy when measuring a run already spent, and predictive accuracy before one is run. That framing turned out to be the answer.

The two competing quantities are not rivals. One is the risk remaining given that a pass reported nothing. The other is the risk expected before you know what the pass will report. They are the conditional and the unconditional form of the same thing, and they stand in an exact relationship: the first equals the second divided by the probability that nothing is detected. That is confirmed symbolically and independently on Wolfram Language, and it explains the numbers that looked like a contradiction. One tenth divided by three fifths is exactly one sixth.

So the answer is the same shape as your ruling on the explorer. Prediction before a run wants the expected form, and the explorer already offers it. Measuring a run already spent wants the conditional form, because by then the branch is known.

The runner therefore keeps the conditional form for its convergence gate, unchanged, and now records the expected form beside it where nothing yet reads it. The gate function was verified byte for byte identical before and after; two functions were added and none removed.

The decisive argument against simply switching is worth stating. The expected form is always the smaller of the two. Every one of 386 recorded values in the archive would move downward. Feeding a smaller number to thresholds calibrated on a larger one would make every convergence gate in the project easier to pass. That is a silent loosening of standards dressed as a measurement improvement, and it is exactly what the additive standard forbids without evidence that the replacement is better.


## On Astra's Work

It is not churn this time, and one part of it is uncomfortable rather than merely useful.

Its brief of 21 September contains a worked table whose figures match, to the digit, figures derived independently here on 28 September after a full day's work. Its notes on the explorer also record that the old page treated a small risk change as an instruction to stop, which is precisely the defect a review seat found on the 28th and which was fixed that evening.

So it was right, and it was right a week early. That brief was in your hands on the 21st.

The useful conclusion is not about mathematics. It is that nothing in the project currently requires an external assessment to be read against the live code and then adopted, refuted, or explicitly deferred. A correct external finding can sit unactioned while the same ground is covered again from scratch. That is a gap in process, and it is the one thing from this whole exchange I would fix before the next external review arrives.

Of its three closing questions, one was already resolved on the day it was asked, with the project's own script crediting Astra by name. One is the question you have now answered. One was correct and has been overtaken. Its explorer candidate is superseded as code, since the page has changed substantially since the version it examined, but it contains one feature worth taking: a table showing both detection outcomes side by side with their probabilities and the expected result across them. That is worth having precisely because it makes the distinction in your question visible in one place.

Its wider design specification for distributed compute is careful work, explicitly not an empirical claim, and explicitly barred from the next experiment so as not to change several variables at once. It is a later concern, not a current one.


## What Needs Your Verdict

Only two things, and neither is urgent.

First, whether to take the branch table from Astra's explorer candidate. It is a small addition and it serves the question you asked directly.

Second, whether you want a rule that closes the gap between an external assessment arriving and its findings being marked against live code. The concrete proposal is that an external assessment is not considered handled until each of its findings is marked against live code as adopted, refuted, or deferred with a reason. That is a small piece of bookkeeping that would have saved a day of duplicated work.

Everything else is done and committed.


## One Honest Note

Across this stretch of work, several checks written to guard something turned out unable to fail if that thing broke. Every one was found by deliberately breaking the code and watching whether anything went red, and none by reading. The pattern was always the same: a test that re-derived a value the code already owns instead of reading it from the code.

The most instructive instance happened last night in my own favour. While testing one of the seats' fixes I edited an archived review brief, which changed its modification time. The validator immediately refused it, because that seat had built a guard against exactly that manoeuvre. The guard caught me performing the dodge it exists to prevent. I restored the file and it passed.


## One Change To The Commit Gate, For Your Ruling

A change was made to the commit-time gate and it should be reversed if you disagree, because it is yours and it costs time on every commit.

Six of the twelve failures fixed overnight were not defects in any work. They were housekeeping the project already requires: a script added without the standard help behaviour, and a review round left unmirrored and without its full record. Each was discovered roughly half an hour after the commit that caused it, because only the full test run catches them.

Three guards now run at commit time instead. The cost was measured rather than guessed: 12.8 seconds added, taking the gate from about 11 seconds to about 24. A fourth candidate was measured at 48 seconds on its own and deliberately left out, because it catches the same class as a guard costing a fifth as much. The gate's own header records the principle this respects: a gate expensive enough to be bypassed is not a gate.

Both classes were then deliberately reintroduced to confirm the gate catches them. It does, in 21 seconds rather than 33 minutes.


## The Shakedown Run Is Not Blocked, And The Plan Says Otherwise

You asked whether the study should cover the week beginning when you were first in a hotel, and whether that should be measured before fixing the itinerary. It was measured, and the answer is that your marker and the plan's existing starting point cannot be told apart.

The record places you at a hotel on 7 September, driving home at 22:03 that evening to seal the archive. The study plan's pre-window baseline is dated 6 September. Measuring the window from 6, 7 and 8 September gives 421, 384 and 368 commits, of which 56.8, 57.3 and 57.3 percent touch running code. The three confidence intervals overlap across nearly their whole range, so no starting point in that span changes what the study measures. The existing baseline is kept because the comparison arm needs a starting commit already proven runnable, and that one is.

The plan's own figures had aged by 8 days. They are refreshed in place: 345 commits and 194 touching code has become 421 and 239. A test for whether the mix had changed gives a probability of 0.88 that the difference is chance alone, so the 345 and 194 became 421 and 239 while the argument they support did not move at all.

Now the part that corrects the plan rather than confirming it.

The plan lists three things as needing your ruling before the run. Checked against the actual code and configuration, none of them blocks it.

The seat contrast arm already declares itself weak. Its own description in the launcher says it is weak by construction in simulation, because both seats are the same stand-in wearing different labels, and that it reports itself as weak. So it is safe to run and honest about what it cannot show. The only question left is whether it is worth the time, which is a judgement about value rather than a blocker.

The drift detector cannot run in any arm. All three arm configurations have the memory it depends on switched off, verified by reading them. And even where it is wired it cannot fire: a constraint solver shows that one or two moves in the same direction cannot cross its threshold and only three can, while production makes one move per flaw class per run. Replayed over 48 real cases it fired zero times. So the choice of whether to keep it or revert it is housekeeping, not a gate on the run.

~~Wolfram in panel reviews needs nothing. Denial is the standing default and no one has proposed changing it.~~ **The struck sentence is this report's original wording, kept verbatim rather than replaced, because a dated report should show what it said.** Its first clause stands and its second was FALSE; the founder caught it the same day. **[CORRECTED 2026-09-29 — THE PANEL'S POSITION WAS WRONG AND CC1 CARRIED IT AS A FOUNDER RULING.** The founder: *"There is no 'denial rule' for Wolfram. That is clearly an invention by you."* Measured the same day: `DEFAULT_POLICY` is `serial`, the live seat arguments are `('--strict-mcp-config',)` with **no** `--disallowedTools`, the serial gate sits first on every seat's `PATH`, and nothing in the repository sets `CDSFL_WOLFRAM_POLICY=deny`. **Wolfram has been enabled for command-line seats since his 2026-09-17 ruling.** A panel opinion is not a rule (`feedback_no_model_voting`); this line records what the seats said, not what is in force.]**

So the shakedown can begin whenever you want it to. What you actually have to decide is smaller than the plan implies: only whether the weak contrast arm earns its place.

One caution from the plan worth repeating, because it shapes how the results should be read. Of 84 entries marked done, 31 claim more than their evidence shows, which is 36.9 percent. Several of the entries this run leans on are among them. The study therefore reads what actually fires during the run, never what a marker claims about it.


## What Comes Next

The next runway item is the one you named: the simulated experiment, and the study of every fix made over the window above. That work is now unblocked, and the check above shows it is less blocked than the plan claimed. We have not run an experiment in some time, and the honest position is that the harness's current health is asserted by 8,800 passing tests rather than demonstrated by a completed run.

Written under CDSFL note standard v1.7 (26 August 2026).
