WHAT THE SESSION OF 2 TO 3 NOVEMBER 2026 FOUND WHEN IT AUDITED ITS OWN WORK

2026-11-03, 02:41 GMT

This note records a measurement of the orchestrator model's own errors during a single overnight session, and the method that found those errors. It is written for a reader outside the project. It is not a record of the project's defects, which are recorded in the master task list under the closure that rested on a model's own claim, the note checker that dated a clock from a file's timestamp, the role vocabulary, the 2 decisions left over from the closure repair, the programs that re-run a check against deliberately broken code, 1 of which hid a check it had skipped, and the spoken report's number formatting; it is a record of the defects in the instruments used to find those.

THE SHORT VERSION

The session fixed 2 live defects in the harness, found a class defect affecting 5 measurement harnesses, found a report generator that had been emitting malformed output for 2 days, and corrected an entry that described 3 missing components when only 1 was missing. Those are the results. Alongside them, the session made 8 errors of its own, each of them in an instrument rather than in a conclusion, and each found by checking the work against a rule the project had already written down rather than by reviewing whether the work looked correct.

WHAT AN INSTRUMENT ERROR MEANS HERE

A measurement in this project is made by writing a short program, running it, and quoting what that program printed. An instrument error is a case where that program answered a narrower or different question than the one it was asked, while printing an answer that looked like the right one. The conclusion drawn may still be correct. The evidence for it is not what it appears to be.

THE 8, GROUPED BY SHAPE

3 were shapes the project had not previously recorded.

The first read a printed message instead of a decision. Classifying which measurement harnesses carried a particular bug, the scan searched for a sentence those harnesses print rather than for the line of code that makes the decision. A harness that words its output differently while carrying the identical fault was therefore classified as healthy. The sweep reported 4 affected harnesses when the true number was 5.

The second sampled a verification and reported it as coverage. A commit stated that 19 of 24 quoted figures reproduced when re-run. The list of 24 had been chosen by hand, and the entries in question quote 64 figures, so the check covered 37.5 percent of them with a 95 percent confidence interval from 0.266660 to 0.497496. Completing the check gave 39 of 64, and every one of the 15 unreproduced figures in one entry failed for a single reason: no program existed that could produce them. That entry cites, in its own text, the project rule requiring exactly such a program.

The third applied a written rule outside its written scope. The session checked its own entries against a note-standard rule requiring every decision to carry a recommendation, and declared 1 entry non-compliant. The rule is explicitly gated to exclude the master task list, because applying it there is circular. The entry was compliant and the check was not.

5 were variants of shapes already on record.

A build was described as anomalously slow by reading the elapsed time of the wrong clock; that build had restarted, and the elapsed time of the restarted run was normal. A conclusion was printed as a fixed sentence directly beneath evidence that appeared to contradict it, because the sentence was written in advance rather than derived from the measurement. An authorship check compared a rendered sentence, carrying formatting the generator adds, against the raw data it came from, and attributed 1 of 4 items to the wrong author. A corrective edit examined 3 fields of a record and would have silently repaired 2 of 4 items, because 2 sat in a list the edit never looked at. And a decision to omit a required output file was announced with a reason, which felt like diligence and was not: the reason was wrong, the requirement was in writing, and nothing tested the reason.

WHAT CAUGHT THEM

Not review. The session's own reading of whether its work looked right caught none of the 8.

In order of yield, 3 things caught them. First, auditing the work against a rule the project had already written down, applied mechanically rather than interpreted. That found an entry with no producing program, 5 producing programs that no test ran, 3 fixes to a generator that nothing in the test suite reached, and the message-versus-decision classification error. Second, a hook the founder added in October, which requires that work done immediately after a context compaction be re-verified against the real project state rather than against a summary. That found 2 programs which could no longer reproduce their own published figures, and 11 violations of a numeric-formatting rule in the document the founder reads each morning. Third, a check wired into a generator so that it inspects what it has just written. That found a malformed-output defect on its first run and caught a fresh violation by the session itself on its second.

THE OPERATIONAL CONCLUSION, STATED SO IT CAN BE DISAGREED WITH

2 of the 8 were caught by a rule catching its advocate. A program written specifically to settle a missing-evidence debt was itself run by no test. 3 fixes made while citing a standard about unreached additions were reached by nothing. This is the argument for keeping such rules in files rather than in intentions: the author who has just invoked a rule is, on this evidence, no more likely to satisfy it.

The method that worked has one further condition, learned from the third error above. A rule must be read with its scope, not only its requirement. The project places its caveats in the gates, and a requirement read without its gate produces a confident accusation against correct work.

A NINTH, FOUND IN THIS NOTE WHILE WRITING IT

The first draft of this note carried a typed clock time, 9 minutes ahead of the real one. The project's rule is that a time is read from the machine's clock and never typed, and the same session had already broken that rule earlier the same night and recorded the correction. The note about instrument failures therefore contained the failure it describes, and was caught by the same linter that catches it elsewhere rather than by its author rereading it. That is the pattern holding rather than an exception to it.

THE HONEST LIMIT OF THIS NOTE

8 is a hand count over a single session, and not a proportion. No denominator is offered, because the number of measurements the session made was never tracked, and presenting 8 against an unrecorded total would be the same error this note is about. The 8 are individually verified; the pattern they form is an observation and not a measurement.

Written under CDSFL note standard v1.9 (1 November 2026).
