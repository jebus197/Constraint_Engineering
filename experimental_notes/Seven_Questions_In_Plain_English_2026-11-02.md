# 7 QUESTIONS ANSWERED IN PLAIN ENGLISH, 2 November 2026

2026-11-02 12:42 UTC. Written under note standard v1.9.

Of the 14 questions the founder raised in his annotated replies of 1 November, 7 say in substance that he cannot tell what is being asked of him. That is not a reading failure on his part. It is a writing failure in the reports, and it is the complaint his annotation about printing issue codes without explanation makes directly. This file answers those 7 without using an internal identifier as though it were a subject, and each answer ends with a recommendation measured against 1 of the 3 formal project standards.



## QUESTION 1. WHAT IS THE ROLE LAYER, AND WHAT DOES 1 DIMENSION OR 2 MEAN

The role layer is a new section of the project's configuration system that records what job each model is being asked to do in an experiment. The configuration system already existed and already had 4 sections, arranged so that a narrow setting can tighten a broad rule but can never loosen it: section 1 holds the rules that apply to everything, section 2 holds per subject area, section 3 holds per task, and section 4 holds per model. The role layer is section 5, and it was built on 2 November.

The question about dimensions is this, and it is 1 question with 2 possible answers. A model in an experiment can be described in 2 different ways at once. The first way is WHERE it sits: is it 1 of several equal participants, or is it the model running the experiment. The second way is WHAT IT DOES: is it sorting findings into categories, is it writing falsifiers, is it reviewing. The design question is whether those 2 descriptions belong on 1 list or on 2 separate lists.

What is actually needed from him is 1 word: ONE or TWO. If the answer is 1 list, then being an orchestrator and being a classifier are entries on the same list and a model has exactly 1 of them. If the answer is 2 lists, a model has a position AND a function, and can be an orchestrator that also classifies.

His own view, given on 1 November, is that the distinction may not be real: he wrote that a classifier is clearly both a position and a function and that separating them may make no sense. That is a third answer, and it is correct. It says: use 1 list, because the 2 descriptions are not actually separable in practice.


**RECOMMENDATION, against the SIMPLEST SUFFICIENT standard. Adopt 1 list, which is his own reading. It is the smallest change: the role layer is already built and takes 1 list of names without modification, so choosing 1 list requires no further code at all, while choosing 2 lists requires a second list, a rule for how the 2 combine, and a guard for the combinations that make no sense. Nothing already built has to be withdrawn either way, so the choice is additive under both answers and simplest sufficient under his.**



## QUESTION 2. WHY ARE ROLE NAMES CALLED SPELLINGS, AND WHAT IS THE 4TH

Because the code does not use his names. He uses worker, classifier and orchestrator. Searching the live code for every place a model is given a role returns 6 different words: model, participant, player, player manager, tool and user. None of those 6 is worker, classifier or orchestrator.

So the word spellings was a way of avoiding saying that the code and the vocabulary disagree, and it was the wrong word to use. The honest statement is that there are 6 role words in the code, 3 role words in the design, and 0 overlap between them. The 4 that were called undeclared spellings are participant, player, player manager and model, which are the 4 that appear in the running code and in no stated vocabulary.

What the models recommended, when the joint panel reviewed it: 2 dimensions and 1 layer. That is, keep position and function as separate descriptions but store them in a single configuration section rather than 2. That recommendation and his own reading disagree, which is information rather than a problem: the panel split position from function, he did not.


**RECOMMENDATION, against the ADDITIVE standard. Map the 6 code words onto whichever vocabulary he chooses, and keep all 6 working while doing it. Removing a role word that running code passes would break the experiments that pass it, and the additive standard permits a removal only with a committed measurement showing the replacement is better on a named property. No such measurement exists for any of the 6.**



## QUESTION 3. WHAT ARE THE SEAT DESIGNS, AND WHAT DOES 44 REFER TO

When a model on the panel is asked to propose a repair, it works inside a private copy of the project and writes real files there: scripts, tests, modules. Those files are preserved so the work can be audited later. 44 is the number of such files that were written, preserved, and never brought into the main project.

So the question put to him was whether to go through those 44 and decide which are worth adopting, or to leave them as a record of what was proposed. He has already answered a closely related question about a similar store of 40 unapplied repairs, and his answer was to triage them, with the reasoning that there is no point doing work that then gets routinely ignored.

A caution on the number, because it was measured and the measurement was wrong once. An earlier attempt to triage these returned the verdict superseded for 27 of 27 artefacts, which looked like a complete answer and was not: the preserved copies live inside the project's own log directory, so a search pattern matched each artefact against itself. A verdict that never varies is the cheapest available sign that a check is broken.


**RECOMMENDATION, against the ADDITIVE standard. Triage them in 1 pass, recording a verdict against each and applying none. 2 of the 40 in the sibling store turned out to contain real defects nobody was looking for, which is evidence the store is not inert. Keeping files nothing reaches is not additive, because an addition nothing reaches is not an addition.**



## QUESTION 4. WHAT IS THE TYPE CHECKER CONFIGURATION

A type checker is a tool that reads code without running it and reports places where a value of the wrong kind is being used, for example where text is passed to something expecting a number. The project has 1 installed.

It was reporting almost nothing, and the reason was not that the code is clean. The tool stopped after the second file it examined, because 2 different module names in the project resolve to the same file on disk and the tool treats that as an error worth stopping for. So its silence was a crash, not a pass.

With that fixed it examines 704 files and reports 1,050 findings about this project's own code across 276 files, plus a further 1,205 complaints about missing descriptions in other people's libraries, which are reported separately and not counted against the project. The work is smaller than 1,050 suggests: 44 of the 276 affected files hold half of all findings and the worst 10 hold about a quarter.

He has already ruled on this, on 1 November: enable it as its own task. It is enabled, it has a per file ratchet so that fixing 1 file cannot pay for a new error in another, and it stays out of the commit check until it is clear.


**RECOMMENDATION, against the SIMPLEST SUFFICIENT standard. Nothing further is needed from him. The remaining question he asked, whether the task has been run, is answered: it is enabled and its first measurement is the figure above. Fixing the 44 heavy files first addresses half the findings for a sixth of the file count, which is the smallest change that addresses the bulk of the problem.**



## QUESTION 5. IS THE BLOCKED RUN A MISSING FALSIFIER ISSUE, AND WOULD REPAIRING IT UNBLOCK THE RUN

Yes to the first, and no to the second, and the reason no is good news.

The run in question is the study run of 3 October. It holds 75 findings. 73 of them resolved. 2 did not: 1 at severity 0.45 and 1 at severity 0.50. Both are below the critical threshold, so the first half of the release condition is satisfied for both. Neither is released, because the second half requires the severity to be PROVEN below the threshold, and proving it means running the finding's falsifier, which is a small piece of code that demonstrates the defect.

Both of those 2 findings carry a falsifier of 0 characters. There is no code to run, so nothing can be proven, so neither is released, so the run never reached a release and ran to its round limit instead.

Repairing those 2 falsifiers would unblock that archived run, and it is not the repair to make. The reason those 2 were never served a falsifier was a dispatch fault, and that fault was repaired on 12 October. The run is from 3 October, so it predates its own repair by 9 days. Calling the live decision functions on both findings today returns admit for both. The fault is already fixed in the code that would run today.

So the answer to what would unblock it is: re run it. Nothing needs building. He has already ruled that, on 1 November, with the instruction to re run it under full monitoring discipline. That re run was done on 2 November and it converged at round 5 of a 12 round budget.


**RECOMMENDATION, against the SIMPLEST SUFFICIENT standard. Treat the archived run as superseded by its re run rather than repairing 2 falsifiers in a record that is now 30 days old. Writing 2 falsifiers by hand would be work on a historical artefact, where the re run tests the repaired code path itself, which is the question anyone would actually want answered.**



## QUESTION 6. DO THE TICKET CATEGORIES MATCH ESTABLISHED CONVENTION, AND WOULD THEY HINDER ADOPTION

This is his question and it is fair. The project's ticket store uses 5 short labels of his own devising, covering a question, a feature request, a proposed fix, a discussion, and a statement needing action.

The honest answer is that it is not known, and it should not be guessed. The comparison that would settle it is specific and cheap: take the category sets of 3 or 4 widely used issue trackers, and measure how much of this project's vocabulary maps onto them and how much does not. Established trackers do carry close equivalents for some of it. A feature request is a near universal category. A proposed fix maps onto what most trackers call a patch or a pull request. A question is a standard label in several. A statement needing action has no obvious equivalent, and a discussion maps onto a separate facility rather than a ticket type in most tools.

What makes the question worth answering rather than dismissing is the adoption risk he named. If a researcher has to learn 5 unfamiliar 2 letter labels before they can file anything, that is a cost at exactly the moment they are deciding whether to continue.


**RECOMMENDATION, against the SIMPLEST SUFFICIENT standard. Keep the short labels as the internal identity, because the ticket identity is computed from the label and changing a label would change every identity already assigned, and add a display name for each that uses the conventional word. That is the smallest change that removes the learning cost without touching anything the stored records depend on. No composability claim is made, because nothing has measured a display mapping against simply renaming the labels.**



## QUESTION 7. IS POSITION AGAINST FUNCTION A QUESTION ABOUT COMPOSABILITY

He asked this directly, and the answer is no, and the distinction matters because the word has a precise meaning in this project.

Composability, in his own definition, is a claim that 2 solutions combined demonstrably perform better than either alone, and it requires a measurement to support it. Where a single solution performs as well or better, that single solution is preferred. That is a statement about repairs, not about vocabulary.

Position against function is a question about whether 2 descriptions are 1 thing or 2 things. Nothing is being combined, so there is nothing for a measurement to compare. Calling it a composability question would be using the word in the weaker sense his definition excludes, which is the sense 10 of 10 earlier uses in these reports took.

What his instinct is right about, though, is the underlying point. He wrote that trying to separate function from position, and preferring either, makes no actual sense. That is an argument that the 2 descriptions are inseparable, and if they are inseparable then there is only 1 list. That is question 1, and his reasoning there is what settles it.


**RECOMMENDATION. No recommendation against a standard is offered here, because this is a definitional question rather than a repair, and attaching a formal standard to it would be false rigour. The answer is simply that the word composability does not apply, and that his reasoning points to 1 list.**



## WHAT IS OWED HIM AFTER THIS FILE

1 word on question 1: a single list, or 2 separate lists. Everything in the role work rides on it, and under either answer no existing code is withdrawn.

Nothing on questions 4 and 5, which are already ruled and already done.

A verdict on question 3, triage or leave, where the recommendation is triage.

And nothing is owed on questions 2, 6 and 7 beyond reading them, because each carries a recommendation that stands unless he disagrees.

Written under CDSFL note standard v1.9 (1 November 2026).
