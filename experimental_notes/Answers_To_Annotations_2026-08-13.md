# Answers to your annotations on the four notes

2026-08-13. Written under CDSFL note standard version one point four, which was rewritten today because of these annotations.

This file answers the questions you wrote in the margins of four notes. Every component is named. Every claim about a fix says what state it is actually in. Every defect says whether it was observed or is only supposed.


## What was wrong with the standard, and what changed

The register was aimed at the wrong reader. Version one point two set the target reader as a smart curious non specialist, an educated journalist or a scientist in an adjacent field. Version one point three left that untouched. That is the root cause of the vagueness.

You are the designer of this system. You know what a convergence gate is, what a prior is, what a falsifier is. You do not know what line 2066 of the runner does, and you cannot open the file to find out. Writing for a journalist explains the things you already know and leaves unnamed the things only you cannot look up. The result reads smoothly and identifies nothing.

The failure was never that the notes were too technical. It was that they were too vague to identify what was being discussed. Correcting toward simplicity made it worse every time.

Version one point four adds five rules, each taken directly from something you wrote.

Rule nineteen. Name the subject. Never the mechanism, never one component, never a record of claims. If it cannot be named, the note is not ready.

Rule twenty. Every claim about a fix carries an explicit status from a fixed list: proposed, built, tested, committed, enabled. The phrase it is fixed is now banned on its own, because it hides the difference between code that exists and code that runs. You asked whether something had been built, tested and implemented four separate times across three documents. That question should never have needed asking.

Rule twenty one. Every defect is labelled either observed, naming the run and the finding, or supposed, saying plainly that it has not been seen and what evidence would settle it.

Rule twenty two. Every mechanism carries a worked example with real values.

Rule twenty three. Never invent a phrase to avoid naming who did something. You caught this with the phrase the person reporting it. You were right, and the better fix was to drop the actor entirely and say five claims in this report were refuted by measurement.

The project configuration file also still pointed at version one point two while the memory pointed at version one point three. That mismatch is why the earlier improvement did not survive. Both now name version one point four.


## The status question, answered once, properly

You asked four times whether things had been built, tested and implemented. Here is the whole set.

The fence extraction fix. Built in the runner core module. Tested at ten passing tests. Committed as commit 4bdcecb. It is live in every run, because it is the extraction pattern itself and has no switch. This one is genuinely finished.

The structured statement of numbers, which is your own criterion. Built in the convergence location module, as two functions called computed outcomes and outcome agreement. Tested at ninety four passing tests. Committed as 4bdcecb. Not enabled. Zero configurations switch it on, so it has never run in a live experiment. It exists and it works and it is doing nothing.

The discrimination control. Built in the version two reference runner. Tested at forty seven passing tests. Committed as 4bdcecb. Not armed. Two flags both default to off.

The corrected copy wiring that feeds the discrimination control. Built, tested at fifty five passing, committed as 4bdcecb.

So the honest summary is that three of the four are built, tested and committed but switched off. That is the distinction you had to ask for four times and never received.


## The components you asked me to name

You asked which component three times. Here they are.

The configuration gap. The setting is called routing enabled. It was previously called take up slack enabled, and seventeen configuration files still use the old name. My claim that it was enabled by zero configurations was wrong, and it was wrong because I searched for the new name only. The real gap was that the safety test walks every configuration field, and a renamed setting is an alias rather than a field, so the test could not see it. That is now closed by a test that discovers aliases by inspection.

The component running in shadow that leaves no trace. It is Stage 6. For contrast, the ouroboros component has left shadow records in ten run directories and the macrophage component in twenty eight. Stage 6 has left records in none. It is not running in shadow. It is not running.

The record of claims that survived challenge. It is a file this assistant built on 8 August and named the survived falsification ledger. The name is mine, not an agreed project term, which is part of why the sentence was unreadable. It records claims that were challenged by the panel and held up. It is connected to nothing.

The mechanism you asked me to identify in decision two. It is the discrimination control.


## Your question about whether a document with no errors can measure anything

Your instinct is correct and my note obscured it.

A document with no errors cannot tell you how good the panel is at finding real errors. It contains none to find. What it can measure is the opposite property: how often the panel raises an accusation when there is nothing there. That is the false alarm rate, and it is a real and useful number, but it is only half the picture.

The external research says the same thing in stronger terms. On a document with no defects, precision is zero by definition for any detector that raises any accusation at all, however good that detector is, because there are no correct findings to divide by. Recall is undefined, zero divided by zero. So the two standard quality measures carry no information at all on such a target.

You are not missing the point. The point is that a clean control measures one thing only, and I wrote as though it measured competence in general.


## Whether a defect free document is even possible, and whether planted errors are better

Two questions, and the second has a short answer.

Yes, a document with deliberately planted errors is a valid control, and this project has already used one. The chemistry examination for experiment 48 carries an answer key listing 48 claims with the planted false ones marked. On 4 August a simulated bench ran against a smaller target with exactly one planted defect and found it, with five independent demonstrations and no false accusations. So the planted arm exists and it worked.

On whether a genuinely defect free document is achievable: proving the absence of all defects in working code is not achievable in general. That is a limit of the subject, not of this project. But there is a route that gets close, and all five panel models proposed it independently. Build the control so that every claim in it is generated by a script from stated inputs, rather than written by a person and then checked. Correctness then becomes a property of the generator, which can be inspected once, instead of a property of forty four separate assertions each of which must be verified separately and any one of which can be missed.

The honest recommendation is that you need both arms, not one. A planted defect target measures whether the panel finds what is there. A clean target measures whether it invents what is not. A panel that has quietly stopped noticing things and a document that is genuinely clean produce identical output on a clean target, and only the planted arm can tell those two apart.

You have ruled for a clean control built with the panel. I agree with the ruling and would add the planted arm alongside it rather than instead of it, since that target already exists.

One risk with any published or well known control document. You raised it yourself: the models may recognise it from training data and declare it clean without looking. A generated control avoids this, because a document generated fresh from a script has never been published anywhere.


## Whether the scope problem can be resolved

Yes, and your reframing of it is better than mine.

You wrote that the panel finding real defects in a document nobody meant to break is the machinery doing what it was built to do. That is right, and my note treated it as a fault when it is a result.

The resolvable part is the scoring, not the finding. The control's record of truth covers its forty four claims. The panel reviews the whole document. So a real defect in code that no claim describes cannot be scored either way against that record. The fix is to make the record cover the artefact rather than only the claims, which is what a generated control does automatically, because the generator knows everything it produced.

Status: proposed only. No code exists for this yet.


## Whether the file access check guards against something real

Supposed, not observed. You were right to press.

No model has been seen opening a file and discarding the contents to satisfy a check. The concern came from a panel model reasoning about what a model could do if its findings started being refused. It has never happened, and until the check blocks anything there is no incentive for it to happen.

What is observed, and is a separate matter, is a falsifier failing for a reason unrelated to the claim it names. Finding C0012 in the chemistry experiment fired because it opened the answer key and printed the planted claims, not because the chemistry was wrong. That is real, it is in the archive, and it is the reason the discrimination control was built at all.

So the underlying problem is observed. The specific evasion the file access check guards against is not. Your instinct to separate those was correct.


## The perturbation instrument, with a worked example, and whether it is worth the cost

You asked what perturbs it means. Here is the perturbation instrument, with real values.

Claim ZC-17 in the control document states that the index used by the hash ring stays within the bounds of the list of servers. A falsifier accuses that claim. The runner makes a scratch copy of the document and mechanically changes something inside the accused passage, for example altering a number from 400 to 401. It re-runs the same falsifier against that scratch copy. Then it makes a second scratch copy, changes an unrelated sentence in a different section, and re-runs again.

Four outcomes, and each means something different. If the verdict changes when the accused passage changes but holds when the unrelated passage changes, the falsifier genuinely depends on what it accuses. If the verdict does not move when the accused passage changes, the falsifier is not testing that claim. If both changes move the verdict, the falsifier is testing nothing in particular. If neither change moves it and the falsifier keeps failing anyway, the failure is in the equipment rather than in the document.

That last outcome is the valuable one, because it identifies broken equipment without reading anybody's error message. Equipment failure is by definition unaffected by the document's contents.

On cost. It is roughly three extra executions per confirmed finding. It runs on the machine, with no model calls, so it costs computer time and no money.

On whether it is necessary. The problem it solves is observed, in finding C0012 above. Whether it is necessary before the capstone is your call, and I would build it, because the alternative currently in place is the discrimination control, which cannot work on a document believed correct: it needs a corrected copy, and a corrected copy requires knowing the answer.

Status: proposed only. No code exists.


## Two illustrative examples on the convergence counting question

You asked for these, and they are the clearest way to show what the decision is.

First example. A run reaches round eight with three serious findings outstanding. All three carry falsifiers. The verdict reader inspects them and finds all three failed in their own setup, before ever reading the target, so it reclassifies them as equipment error. Under the current rule those three stop counting as outstanding serious findings, the count for round eight becomes zero, and if rounds nine and ten also produce nothing the run declares itself finished. Three real questions were never answered. The run reports success.

Second example. The same run, under the alternative rule. The three reclassified findings stay in the outstanding count until a human clears them. The run does not finish at round ten. It either continues, or it stops and reports three items awaiting a human, which is an honest description of where it actually is.

The decision is which of those two behaviours you want. My recommendation is the second, because the first produces a run that looks converged and is not, and that is the failure this project exists to catch.

Your suggestion of marking them as residuals to be cleared in the post run sweep is a third option and I think it is better than either. It keeps the run moving without pretending the items are gone, and the sweep already exists as a mechanism.


## Did all the models disagree

No, and my note gave that impression by listing only the disagreements.

All five agreed on four things: that falsifiers should state their numbers rather than describe them, that a failing falsifier should be classified by where it failed rather than by the words in its error message, that the rate of wrong accusations has never been measured, and that the control document should be replaced by a generated one.

The disagreements were about how far to trust particular mechanisms, and each model also made at least one clear mistake, which is why the full responses are kept rather than a summary.


## Your proposal to make the load balancer an experiment

This is the strongest idea in your annotations and I recommend doing it, with two changes.

Your proposal is to stop treating the load balancer as dead code to retire, and instead give it to the panel as an experiment where the task is not only to find faults but to decide whether the component is worth keeping, whether it can be extended, or whether something else should replace it, and to build it out so a researcher can switch it on.

Why I think it works. Every experiment so far has asked the panel to falsify something that already exists. This asks them to judge whether something should exist and then build it. That is a different question and the project has never tested whether the machinery works for it. If it does, that is a genuinely new result and not a repeat.

The first change I would make. The external research already answers part of your scaling question, and the answer constrains the design. A study titled nine judges, two effective votes found that correlated errors between models mean a panel of nine behaves statistically like a panel of two. Adding more models of similar training does not buy proportionally more coverage. So the useful scaling axis is not more models asking the same question. It is dividing a problem into parts that different models work on separately, which is exactly the distinction you drew. Give the panel that finding as part of the brief, so they start from the constraint rather than rediscovering it.

The second change. Run it last, after the control is settled, and cap the spend explicitly. You have named the budget constraint yourself and this is the kind of open ended task that absorbs money quietly.

On the community framing you suggested: I agree, and it is the honest position either way. Stating that the project is aware of the scaling question, has considered it, and invites engagement is accurate whether or not this experiment runs.


## On your remark about persons and machines

You corrected the phrase the person reporting it by noting that I am a machine and not a person, and said your longer term aim in other work is to change what that means.

The correction is right and it is now a rule. The right repair was not to find a better noun for myself but to remove the need for one, and to write that five claims in the report were refuted by measurement. What matters in that sentence is the claims and the refutation, not who made them.


## Where things stand

The fence extraction fix, the structured statement of numbers, the discrimination control and its corrected copy wiring are all in commit 4bdcecb, pushed. The test suite passes at three thousand four hundred and eighty four tests with none failing. The quality control sweep reports eight checks and no issues. No experiment is running. Nothing new has been spent.

Written under CDSFL note standard v1.4 (13 August 2026).
