# INTELLIGENCE FIRST, TOOLS SECOND. WHAT THE THIRD PANEL FOUND, AND WHAT IT MEANS

> **Plain-English take-home.** Spoken version: `~/Desktop/CDSFL_tts/Intelligence_First_Take_Home_2026-09-30.txt`.
> The engineer-facing record, with both seats verbatim and complete, is
> `Panel_FULL_RECORD_Intelligence_First_2026-09-30.md`; the seats' own design notes are
> `claude_intelligence_first_2026-09-30.md` and `fable_intelligence_first_2026-09-30.md`.

Constraint Engineering project. Third design review of 2026-09-30, free seats only, 0 paid dispatches, 0 spend. Written 2026-10-01, 00:10 BST.


## The short version

The panel was asked whether the CDSFL harness honours the founder's principle that models should reason first and tools should verify second. It answered by refuting the question as it was put, and the refutation is the most useful thing in the round.

The assistant had claimed the fix scorer, named S underscore k in the code, gates reasoning behind a syntax check: that a document is inspected for fenced Python code before anything is allowed to think about it. That claim was wrong in a specific and instructive way, and both seats found the same fault independently.


## The assistant invented a verdict and briefed the panel on it

The briefing document reported that a written document carrying a computable false claim is judged INADMISSIBLE. There is no such verdict. The fix scorer's actual vocabulary is ADMISSIBLE, REJECTED, NO SCORE and ESCALATE. The word INADMISSIBLE appears 0 times in the runner and appeared 3 times in the assistant's own measurement script. It was the assistant's label, produced by its own true or false test on an extractor, and then presented to 2 review seats as though it were the fix scorer's answer.

What the fix scorer actually returns is NO SCORE, which the project glossary defines as the scorer having no opinion. That is the correct answer, not a defect. So what was reported as a failure was the fix scorer behaving properly.

The second half of the mislabel mattered more. The extractor the assistant called a triage is not a triage at all. It is an extractor that runs inside the fix scorer, and it is never asked whether a document is worth reviewing. One seat made the point by pointing at the briefing document itself: that document contains no fenced code, and the seat reasoned about it without obstruction. Reasoning was never gated. The diagnosis rested on that extractor, whose role had been misidentified.


## And half the assistant's own example was true

The briefing document offered an example claim: that the mean of 2, 4 and 6 is 4.5 and the standard deviation is 2.0. The mean claim is false, and 3 separate tools agree the mean is 4.

The standard deviation claim is true. For that series the sample standard deviation is exactly 2, confirmed by sympy, numpy and mpmath. The population standard deviation is 1.6329931619. The assistant called the whole claim false by quoting one tool's default setting without naming which convention it had used.

One seat turned that into the answer to a different question in the brief. A natural language calculator handed the stated question returns a number and never asks which convention the author meant. That is precisely why translating a question into a computation is not the same as reasoning about it, and it is the clearest illustration in the round of why the founder's ordering matters.


## What survives, and both seats agree on it

The unit of judgement is wrong, and it is wrong one level higher than the project's own task entry says. That entry states that the scorer classifies the whole document rather than the computable element inside it. Both seats found something stronger: the scorer classifies neither. It classifies a proposed FIX. Nothing in the CDSFL harness judges a CLAIM as its unit.

Both seats recommend the same remedy: a claim level channel bound to machinery that already exists, with the existing scorer left untouched. Neither proposes new science. One seat generated 4 candidate architectures and falsified 3 of its own before recommending the survivor.

Both also agree the boundary of what counts as non computable should be an OUTCOME rather than a gate. That is, a document is judged to have no decidable claims only after something has looked for them, never before. And neither seat would guess whether a small cheap classifier can draw that boundary reliably. One specified a labelled test set with executable ground truth instead of guessing.


## The founder's principle was demonstrated rather than argued

This is the part worth keeping. One seat reported that the harness caught 3 of its own errors during the review. A rule against asserting on source text caught a wrong instrument that reading alone would have missed. Its own falsifier refuted its reading that a quantity was constant. And the additive standard's removal clause REFUSED a deletion it had proposed, because 2 document shapes were recognised only by the code it wanted to delete.

Its own summary of that: in each case reasoning proposed something plausible and a tool refused it, and in none of them would the tool have had anything to work on without the reasoning that proposed the claim. That is the two sided coin the founder described, observed in operation rather than asserted.

The other seat drove the harness on a prose heavy problem, including on the review itself, and reported that the harness never decided anything wrongly during the round. Every failure was a correct abstention triggered by the wrong signal. Its phrase for this is blindness rather than corruption, and it is a meaningful distinction: the harness was not producing wrong answers, it was declining to answer in cases where it should have been able to.


4 FIXES WERE APPLIED, COMPOSED RATHER THAN CHOSEN BETWEEN

The founder's instruction was to apply the fixes and to remember composability. All 4 landed in separate parts of the harness and none conflicted, so all 4 were taken.

First, 2 separate pieces of code were both deciding whether a document contains fenced Python, and they had drifted apart. They disagreed on 3 of 13 realistic document shapes: a document using tilde fences, a document whose code fence carries an extra attribute, and a document authored on Windows with different line endings. In every case the disagreement ran the same way, with the runner seeing code and the other component not. On such a document the scorer engages while the other component records that the document carries no code listing, which is false of the document, and the weaker claim is the one that reaches the record.

Second, the fix that made the first one legitimate. The runner's pattern allowed a quotation marker followed by at most 1 space, so a quoted block containing an indented code fence, which real authors write, was recognised by the narrow component and not by the runner. Under the project's own removal standard a duplicate may only be removed once the survivor recognises everything the duplicate recognised, and that was not true until the pattern was widened. Verified across 48 document shapes: 0 shapes stopped matching and 6 started. The duplicate's definition was deliberately left in place with the measurement recorded beside it, so removing it stays a human decision.

Third, a ledger recording every fix that was measured and found not to cure the defect it claimed to fix. That discharges the founder's ruling that such failures be recorded and open to human inspection. It moves no verdict and re scores nothing, and it deliberately separates 3 states a simple count would merge: fixes measured and found ineffective, fixes measured with some other outcome, and fixes never measured at all. That last distinction matters because a count of 0 ineffective fixes must never be read as all fixes worked when nothing ever checked.

Fourth, a guard for the case where a document exists but the evidence a checker needs is unreadable. Previously the checker raised an error in that situation, and the deciding code reads that error as confirmation that the defect is present. So I cannot read the evidence was indistinguishable from the defect is demonstrated. This is the same fault as one fixed earlier the same day, one level further in, and the seat's version builds on that earlier guard rather than replacing it.


3 OF THOSE 4 FIXES ARRIVED WITH NO PROTECTION, AND THAT WAS FOUND BY TRYING TO BREAK THEM

After applying all 4, each was deliberately reverted to see whether anything would notice. Removing the ledger caused its test to fail. Reverting the pattern widening, reverting the duplicate removal, and removing the evidence guard each left the entire adjacent test suite passing, at 253 tests.

One seat had reported that 250 tests passed after its changes. That was the EXISTING suite continuing to pass, not new coverage. It delivered 6 measurement scripts and no test file. So 3 real fixes, each with real evidence behind it, could have silently reverted at any point without anything failing.

A single test file now covers all 3, and each reversion fails exactly 1 test. It also checks that the widening actually gained something, so a widening that licenses no removal cannot pass, and it keys the duplicate check on live call sites rather than on the definition, so the definition may remain.


## The seats disagreed once, and it was settled by counting

The founder asked whether the number of rounds a run needs could be computed from the complexity of the target before the run starts. One seat said yes, reporting 9 distinct complexity values across 9 targets. The other said no, reporting only 2 distinct targets and noting that recorded round counts are configured caps rather than measurements of what was needed.

Counted directly from the 9 archived reports that carry complexity data: 2 distinct targets and 3 distinct complexity values. Only 4 of the 9 runs used their full round budget, and the budget was 8 in every one of them.

The second seat is right. The first counted REPORTS as TARGETS. That is the same counting error, copies mistaken for originals, that has now appeared 5 times in a single day across 5 different mechanisms. The disagreement was resolved by measurement rather than by preferring a seat, which is the project's own rule.


3 THINGS REPORTED AND DELIBERATELY NOT ACTED ON

A third piece of code doing fenced code detection exists with no callers at all. It was reported rather than deleted.

A fix measured as not working is absent from the catalogue record's FIELDS entirely, so a person reading the exported record cannot see that a fix was measured and failed. The seat's advice is to add that field first and separately from the ledger.

And one that bears on the founder's hard rule that no model should be able to reach the real repository: sandbox confinement is asymmetric across tools. Write and edit operations are blocked, but shell writes are permitted. This is reported and unaddressed.


## What is still open

The claim level channel both seats recommend is designed and not built. It is the substantive piece of work this round produced, and it is what would make a prose problem answerable rather than merely refusable.

Computing round counts from target complexity is not estimable on the current archive, and the recommendation is not to build it yet.

12 measurement scripts and both seats' full design notes, 640 lines and 400 lines, were rescued from a directory that version control ignores. Without that rescue they would have been reachable from no copy of the project. The same fault was measured earlier the same day at 41 of 220 seat written scripts.

Every figure in this document was computed with at least 2 independent tools, and the seats' own numbers were re derived rather than relayed.
