# Description Truncation: Three Fixes, and Why the Alarm Was Wrong

2026-08-17, 01:30 BST. Plain-English companion to the technical note.

## The short version

Three defects in how findings were stored and read are now fixed. The alarming claim that started this work, that text truncation had caused experiments to stop too early, is refuted. It was an artefact of comparing damaged text against differently damaged text.

No experiment is invalidated. Nothing needed re-running. What was needed was a re-measurement, and it is done.


## What was actually wrong

The first defect was not truncation at all. It was substitution. When the parser's pattern for finding the claim text failed, it fell back to keeping the first 200 characters of the raw block. Those first 200 characters are the schema header, reading FINDING ID, SEVERITY, then the first fragment of the claim. So the stored description was a header where the claim should have been. This fired on 15.1 percent of all finding blocks.

Three separate causes were found, each confirmed both by reading the code and by replaying it against the archive.

First, one branch of the pattern was unreachable code. It was written to mean "or the claim runs to the end of the block", and it required a newline followed by whitespace followed by the end of the text. But the block has its trailing whitespace stripped before the pattern ever runs, so that position cannot exist. The branch never executed once in the project's history.

Second, the separator list accepted only colon, equals and hyphen. One model writes a full stop after the label, another writes a dash.

Third, markdown heading style has no separator at all. Two models write the label as a heading on its own line, then the claim below it.

The second defect was a 500 character cap applied when writing to the registry. On 2026-08-16 this was reported as affecting only the stored archive. That was wrong. The same stored record is read every round by the convergence count, by the verification pass where one model casts confirm, refute, duplicate or escalate verdicts from round 6 onward, and by the routing ladder, which asks for 1200 characters and can never receive more than 500.

The third defect was in how locations are extracted. The extractor scans the whole description for symbol names. It cannot tell "the defect is at claim EN-16" from "EN-01 defines the load case". One engineering finding accused claim EN-16 of using the wrong safety factor convention, then listed four premises, EN-01, EN-03, EN-17 and EN-20, in order to derive the correct value. All five were recorded as locations that finding had accused.


## The three fixes

The first fix repairs the parser pattern. It is now anchored to the start of a line, the separator list is widened, the unreachable branch is replaced with one that works, and two field labels are added as stopping points so the claim text does not run onward into the falsifier's source code.

Measured across the 5592 archived finding blocks the parser accepts: matches rise from 4748 to 5060, that is 84.9 percent to 90.5 percent. 312 blocks recovered. Zero regressions. Of the 4748 that match both ways, 4734 are byte for byte identical. Nine gain text, two of those from a previously empty capture, going from 0 to 966 and from 0 to 3989 characters. Five shrink, and all five are corrections, where the unanchored old pattern had begun matching inside a fenced code sample and swallowed 5439 characters of Python.

Two wider versions of this fix were built and rejected on measurement. One recovered the same 312 blocks but shortened 870 descriptions that parse correctly today. The other shortened 834. The first of those was nearly shipped, because the regression check being used counted only whether a match happened, not whether text was lost. That is exactly the failure class this project exists to catch, appearing in the checking instrument itself.

The second fix recovers the damaged text. 531 archived descriptions are repaired from the raw model responses, which were always stored in full. Every join between a registry entry and a raw response is verified against the stored text before it is trusted. 471 joins that could not be verified were left alone. Nothing ambiguous was repaired.

The archived reports themselves are not modified. Repairs are written to a separate sidecar file per experiment, and every consumer must opt in to read them. Rewriting the archive in place would destroy the original state and leave no way to distinguish a repaired figure from an original one.

An early version of that repair script kept only one candidate per model and finding identifier. Models re-file the same identifier round after round, so it silently matched round zero's text to a round three entry. 23 repairs in one experiment were quietly wrong. The join succeeded and the text looked plausible. The content check is what caught it, which is the argument for having the check rather than trusting the key.

The third fix stops cited premises counting as accused locations. Symbols that appear only under a "Premises" heading are no longer flagged.

The scope of that fix was set by measurement, not by judgement. Of 2187 archived descriptions only 122, that is 5.6 percent, carry any supporting material heading at all, and the word "Evidence" accounts for 78 of them. Reading those, "Evidence" does not introduce cited background. It introduces the substantiation of the same defect at the same place, so removing it would delete real signal. The word "Premises" accounts for 35 findings, and those are the citation case.


## Why the alarm was wrong

On 2026-08-16 it was reported that two experiments had converged early because of truncation, and that one of them would not have reached convergence at all. Both claims are refuted.

The error was comparing truncated text against premise contaminated full text. The truncation had been cutting the premise list off the end of that engineering finding, so the extractor produced the right answer for the wrong reason. Repairing the truncation alone made the extraction worse, not better, because the premises then came back into view. The two defects were masking each other, which is why neither was visible alone.

With both fixes applied, the close round for each experiment is as follows. Experiment 44 closes at 8 rather than the recorded 10. Experiment 45 closes at 3, unchanged. Experiment 46 closes at 5, unchanged. Experiment 47 closes at 7 rather than the recorded 11. Experiment 48 never reaches the three quiet round condition, unchanged. Experiment 49 closes at 6, unchanged.

No run converged early. The two that move were delayed by truncation, which is the conservative direction. A finding whose locations are clipped is counted as not novel by itself, but it also withholds those locations from the running record, so later findings become more likely to count as new.

This vindicates the adversarial review panel's conclusion over the earlier one reported here. Its strongest refuter reached the same verdict by a stricter method, and that verdict was initially disputed on a coverage gap that turned out not to matter.


## The re-derived measurements

The similarity function's operating characteristic was recomputed on repaired text.

The count of critical findings is unchanged at 165. Coverage of the second tier is 160, previously 161. Coverage of the third tier rises to 110, previously 94. Same location pairs rise to 460, previously 438. Labelled pairs are 31 same defect and 296 different, previously 28 and 290. Criticals still stored truncated fall to 23 of 165, that is 14 percent, previously 81 of 165 at 49 percent. Discrimination measured as area under the curve is 0.976, previously 0.986.

Four findings survive the repair and hold on both versions of the text. The chance of wrongly merging two genuinely different findings, at the setting the system actually runs at, is 14.9 percent against 14.5 percent before. There are zero wrong separations on either version. Against the baseline it replaces, which merges every same location pair without exception, wrong merges fall from 296 to 47, a reduction of 84 percent. And the third tier changes the outcome on only 3 of 327 pairs, and is wrong on all 3.

One earlier finding dies, and it should. The 2026-08-16 note recorded a pooled association between truncation and wrong merges at a probability of 2.07 x 10⁻⁵, with an odds ratio of 10.5, flagged at the time as NOT established because it reversed when split by experiment. On repaired text it measures a probability of 0.272. The stratification was right and the pooled figure was an artefact. It is recorded rather than deleted, because a claim correctly hedged and then correctly withdrawn is worth more as a record than as a silence.


## What generalises

The useful finding underneath all of this is smaller than the alarm and more transferable.

Two defects can mask each other so completely that fixing one alone makes the measurement worse. The premise defect was invisible for as long as the truncation was cutting premise lists off the end. Anyone repairing the truncation without also finding the premise defect would have concluded, on good evidence, that their repair had broken the convergence gate.

The practical form. When a repair makes a measurement worse, that is not by itself evidence the repair is wrong. It can be evidence that the repair has uncovered a second defect the first one was hiding. Check for the second defect before reverting the first.


## What remains

The 120 unadjudicated pairs, now 133 on the repaired dataset, still need a human ruling. Machine labels cannot settle an operating point.

471 backfill joins could not be verified and were left alone. They are recoverable only by hand.

44 descriptions still contain falsifier source code, down from 190, but not yet zero.

532 blocks the parser still cannot read, mostly code fragments rather than genuine findings.

The registry cap remains at 500 characters, while the routing ladder still asks for 1200.

Written under CDSFL note standard v1.4, 13 August 2026, Rule 24 added 16 August.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
