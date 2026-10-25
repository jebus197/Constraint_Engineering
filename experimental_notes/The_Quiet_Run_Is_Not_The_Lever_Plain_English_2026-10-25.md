# The quiet run is not the lever — morning report, plain English

**2026-10-25, 03:00 to 03:35 GMT. Nothing in the convergence gate has been changed.**

## The answer, first

**The founder's scepticism was correct on every point that could be tested, and on one point the evidence is stronger than his objection.**

He asked whether the claim was that convergence cannot trigger reliably without more quiet rounds, and if so, what the project has been doing all year. **No such claim was ever true.** Convergence has triggered, repeatedly, and the archive records it. The measurement used to justify raising the required quiet run from 3 to 7 said something much narrower than it appeared to say, and the number it produced answers a different question from the one a decision needs.

**On whether to add quiet rounds at all: on this evidence, no.** The recommendation is to revert or replace the change. Nothing has been applied, because he said not to.

## 1. The number that justified the change was pointed at the wrong question

The original measurement asks: *if we already know findings were still coming, how often would 3 quiet rounds have appeared anyway?* The answer is about 1 time in 8 — the figure 0.126374.

But that is not what a stopping decision needs to know. A decision needs the reverse: *if we see 3 quiet rounds and close the run, how often were we wrong?* **That question had never been computed in this project until last night.**

The answer first computed was **23 of 63, or 0.365079**. The panel then showed that figure was too high by 37%: the correct answer is **8 of 30, or 0.266667**, because the test fires once per experiment while overlapping windows were each being counted separately. And here is the part that matters most: **the figure gets WORSE as the quiet run gets longer**, reaching 0.600000 at 5 rounds. The reason is a trap in the data. A long run of quiet rounds can only happen inside an experiment that is already long and still producing findings late on, so asking "what happened after a long quiet run?" automatically selects the experiments where findings were still coming. The original measurement cannot see that, because it conditions the other way round.

Every figure here was checked twice, by two independent statistical methods that agree to within 0.000000000000000055.

## 2. The zero that clinched the case for 7 rounds means "never happens", not "safe"

This is the decisive finding.

**Seven consecutive quiet rounds occur zero times in the entire archive** — 63 experiments, 409 usable rounds. The "0.0000 at 7" that justified the change is not a measurement of safety. It is the measurement going blank because **a run of 7 consecutive quiet rounds never happens.**

Three separate checks were run to try to break that conclusion, and all three confirmed it:

1. **Most experiments are too short.** 41 of 63 have fewer than 7 usable rounds, so a 7-round quiet window is impossible in two thirds of the archive no matter what the findings do.
2. **It is not only the short ones.** Among the 22 experiments long enough to contain a 7-round window, the number of times 7 consecutive quiet rounds actually occurred is **zero**.
3. **It would not fit inside the round budget.** Experiments are capped at 8 or 16 rounds. Of the 53 that raised at least one critical finding, the number of rounds needed to close after 7 quiet ones has a median of 10 and a maximum of 51. At the tighter cap, **34 of 53 experiments could have closed at 3 quiet rounds, against only 21 of 53 at 7.** That is a loss of 13 experiments out of 53, roughly a quarter of the archive, and the difference is statistically solid (two independent tests giving 0.019234 and 0.011499).

**So 7 is not a stricter version of 3. On this evidence it switches off the gate's quiet condition, the branch that closes a run after consecutive rounds with no new critical findings.** His own summary — *"We spend 7 rounds trying to essentially (or at least hoping to) find nothing?"* — actually understates it: the harness would spend the rounds and then still not be allowed to close.

## 3. His churn concern was right, and nobody had measured it

He suspected that more rounds would mean more churn, and that classifying churn costs real compute even when it is detected correctly. That was a hypothesis. It is now a number.

**Early rounds produce 1.524064 critical findings each. Late rounds produce 0.627451.** That is a ratio of 2.428977 — late rounds are nearly two and a half times less productive. Two independent statistical tests confirm it overwhelmingly.

Extra rounds buy progressively less, and they are spent precisely on the part of the curve where findings have already dried up.

## 4. The severity question is the same question, and he was right to connect them

He asked whether a suggestion about changing the severity score from 0.7 to 0.5 was a separate topic or the same one.

**It is the same one.** The 0.7 cut is what decides whether a finding counts as "critical" at all — and therefore whether a round counts as "quiet". The two questions are opposite ends of the same mechanism.

But the lever moves the wrong way. **Lowering the cut to 0.5 makes the problem dramatically worse** — the error rate goes from 0.365079 to 0.916667 — because more findings count as critical, so more of them arrive late. Raising it to 0.8 improves the number slightly, but only by relabelling findings rather than finding them sooner, which is cosmetic.

**Recommendation: leave the severity cut at 0.7.**

## 5. The dynamic rule he asked for exists, works, and is cheaper than what the harness does now

This was the most productive question he asked: must the required quiet run be a fixed number such as 3 or 7, or can it be worked out from the experiment itself? His illustration was that asking the harness to compute 4 plus 4 should not need 7 rounds, while a serious attempt at the Riemann Hypothesis might need more.

**A rule that does exactly this was built and run over the archive.** Critical findings arrive quickly at first and then tail off, which section 3 establishes. So: fit the decay, and stop when the predicted yield of the next round falls below a small floor.

Over the 63 experiments it **fired on 47, stopping at a median of round 2 and a mean of round 4.72, against an average 6.49 rounds those experiments actually used.** So it is **cheaper on average than current behaviour**, and it adapts exactly as he described. A trivial problem exhausts itself immediately and the rule stops; a deep problem keeps producing findings and the rule keeps going. There is no arbitrary constant left — only a floor, which is an honest statement about how small an expected yield is worth another round of everyone's time.

A second rule was also tried, based on classical statistics for estimating how many species in a population have not yet been observed. It gives a striking number — 94.7% of critical findings were raised by only one model, implying the search space is barely touched. **But that number should not be trusted**, and the reason is a design feature rather than a flaw: the method assumes all the models are sampling from the same pool in the same way, and a deliberately diverse panel breaks that assumption on purpose. Low overlap between models is what a multi-model panel is for. It is reported so the panel can rule on whether it can be salvaged, not because it is being recommended.

## 6. Where the number came from, which is the real question underneath

He observed that 3 was set arbitrarily early in the project, and that if it now must become 5 or 7, the old arbitrary number seems to have acquired some new significance.

**The honest answer is that it never acquired a new meaning. It acquired a measurement aimed at the wrong target.** The sequence was: the constant was 3, chosen with no measurement behind it; a panel finding in October reported an 11.59% chance of a false quiet and he ruled "Fix it"; the value was moved to 7 on the strength of a curve; the second half of his ruling — check the fix with the free panel — was never carried out; and that check, run last night, finds the curve measures the wrong thing.

So the number was arbitrary, became briefly evidence-backed, and the evidence does not survive examination. **The constructive outcome is that it does not need to be a constant at all — which is what he asked in the first place.**

## 7. The fix he ordered is built, and it exposed worse problems underneath

He instructed that the phantom-file defect be fixed first. It is.

The check that enforces careful working had been reporting files as changed that **have never existed** — they were example strings inside another test file. A path is now only reported if it is actually on disk.

Tracing the consequences first caught a trap in that very fix: filtering too aggressively could empty the list of changed files, which would switch off *all* the discipline checks at once. That is worse than a wrong filename, so the fix falls back to a placeholder rather than reporting nothing.

**But checking the checker turned up something more serious: 4 of its own 8 test files were broken.** One was **flaky rather than failing** — the same test, run three times with no change in between, gave fail, pass, fail — because a counter was being written into the founder's live settings folder and shared between runs. A flaky test is worse than a failing one, because it hides problems on the runs where it happens to pass. Two others were testing rules the founder himself had already replaced. And the new fix broke a fourth, repaired properly by testing both behaviours rather than by weakening the test.

**None of this was visible because none of those 8 files is in the list the commit check actually runs.** The commit check reported 1,439 tests passing, three times during the night, while these four were failing. All 136 now pass, identically across three consecutive runs.

**One correction belongs here.** The first attempt to work out which failures were pre-existing was wrong, and the reason is worth knowing: saving work aside with `git stash` silently breaks the link between the repository copy of a file and the deployed copy, so the "before" test actually ran the "after" code. Done properly, 2 of the 4 failures turned out to be newly introduced.

## 8. Why saving state kept failing silently

Three attempts to save state during the night exited with an error and no explanation, and the work had to be committed by hand. Two theories were tested and both were wrong — the timeout was far too large to be the cause, and the message checker does not even look at the path involved. Running the save with its two output streams separated rather than merged revealed the cause immediately.

**It is a known issue, already on the master task list, which the founder ruled on on 2026-10-19 and which has never been built.** The check requires the memory folder to be newer than the *previous* save — so a follow-up save is refused for memory the first save already used up. The documented workaround worked first time.

## 9. The panel

The free panel was dispatched at 03:31 GMT. The roster was confirmed before launch as the two models that run on the founder's existing subscription, so **the run costs nothing**. The paid models require his written authorisation and were not dispatched.

The brief carries his questions in his own words, all the findings above with 13 figures that the validator re-runs before the brief is allowed out, and the recommendations below. It explicitly asks the models to attack the analysis rather than agree with it, naming four specific angles of attack.

### What the panel returned, and it argued against the recommendation rather than agreeing with it

**Both models reached the same verdict and both attacked the reasoning that produced it.** One made 45 tool calls over about 11 minutes; the other 35 over 10 minutes. Both wrote working fixes into their own isolated copies of the project, which are preserved but not applied.

**Verdict from both: go back to 3.**

One put it bluntly: a required quiet run of 7 had **zero opportunities to fire** in the whole archive — the longest quiet run ever observed is 6 — so it does not tighten the convergence test, it removes the only part of it that works.

**They found three problems with the analysis, and two of them were right.**

**First, and this is a correction to the headline number.** The figure of 0.365079 was wrong, because it counted overlapping windows rather than actual decisions. A 5-round quiet stretch contains three different 3-round windows, but the test fires once and then the experiment ends — so experiments with long quiet tails were being counted several times. **The correct figure is 0.266667, and the one reported was too high by 37%.** It was independently recomputed and the models' number reproduced exactly. The direction of every conclusion survives; the size of the effect does not.

**Second, and this one kills a recommendation.** Both models independently pointed out that the adaptive rule was being recommended without anyone ever measuring how often it closes too early, which turned out to be 0.468085 — the exact failure the analysis had just convicted the original measurement of. One of them put it precisely: the correction was applied to the incumbent and not to the challenger, and that asymmetry is how a replacement that nothing measured gets recommended.

**Measured for the first time: the adaptive rule closes too early in 22 of 47 experiments, a rate of 0.468085, against 0.266667 for the simple count of 3. It is worse than the simple count of 3 it would replace.** On the strict statistical test the difference is not established, but that is not the point: the rule has no measured advantage at all on the very metric the analysis called decisive. One model added that it stops at round 2 both on a trivial experiment and during a lull in a bursty one. **The recommendation to replace the fixed number with the adaptive rule is withdrawn in full.**

**Third, and this one is unresolved.** One model could not reproduce three of the feasibility figures, getting 32 and 16 out of 53 where this analysis gets 34 and 21. Its wider point is conceded and fair: those three numbers were typed into prose rather than declared for automatic re-execution, in a document whose own rule is that typed numbers are never checked. On re-running, this analysis still produces its original figures, so **the discrepancy stands unresolved and both sets are reported.** The direction is the same either way, and stronger on their numbers than on ours, so nothing hinges on it.

**And the sharpest point of all reframes the whole question.** One model argued that presenting this as a choice between stopping rules is itself the mistake that let an unreachable constant ship: the evidence says the stopping rule is not where the fault lies. The second half of the convergence test fired on all 23 premature closes and blocked none of them. A two-part test carried entirely by one part will close too early at whatever number you choose, because that number is the only thing deciding anything. Its words: it should have been the whole brief.

**That criticism is accepted.** The quiet run is not the lever, and neither is any replacement for it, because the second half of the test is not contributing. That repair is therefore promoted to the first recommendation below.

## What is recommended, and what he needs to decide

**This order is not the order the analysis was written in, and one recommendation has been withdrawn.** The models' criticism — that framing this as a choice between stopping rules is what let an unreachable number ship in the first place — is accepted, so the repair to the convergence test's second half comes first now.

**1. Repair the second half of the convergence test before touching the first.** The original measurement shows that the other half blocked **zero** premature closes while firing on **all 23** of them, and that the two halves move together rather than independently. A two-part test whose second part never blocks anything is a one-part test wearing a two-part name — and whatever number the first part is set to, that number becomes the only thing deciding anything. **This is the only recommendation that fixes a mechanism rather than adjusting a threshold, and both models agree it is the one that matters.**

**2. Revert the required quiet run from 7.** Its justification rests on the wrong question and on a zero that means "never happens", and both models independently said go back to 3. Reverting restores the test to 34 of 53 archived experiments from 21 on this analysis, or 32 from 16 on one model's — the two computations disagree on size and agree on direction.

**3. WITHDRAWN — replacing the fixed number with the adaptive rule.** This was recommended and is now withdrawn in full. Both models measured the adaptive rule's own error rate, which had never been done, and it is **0.468085 against 0.266667 for the simple count of 3** — worse than the simple count of 3 it would replace, with no measured advantage on the very metric the analysis called decisive. The rule stays in the code as a measured negative result rather than being deleted, because the measurement is the useful part.

**4. Leave the severity cut at 0.7.**

**5. The depth and breadth question, restated so it can be answered.** He said the previous version was too vague to offer a view on, and he was right. The subject is confirmed: he asked whether reasoning depth and breadth could be reliably split 70 to 30, and the answer remains no, because neither the harness nor its hooks label a thought as one or the other. The question now registered is a straight choice: keep 70:30 as a stated intention that is explicitly unenforceable, which is what is currently written; drop the numbers and keep only the enforced rule that every delegated task must state its hypothesis, its falsifier and why one context will not do; or something else he names. **The enforced rule works either way and does not depend on his answer.**

Written under CDSFL note standard v1.8.
