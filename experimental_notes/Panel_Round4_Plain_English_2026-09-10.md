# Panel round 4, in plain English: the correction that repeated the mistake it was correcting

2026-09-10, 03:30 to 03:40 BST.

## What happened, in one paragraph

Two reviewing models were asked to check three repairs that had landed after the previous review finished. Both were told to form their answers by running the code rather than reading it, and both did: 48 and 35 recorded tool calls respectively. They agreed that two of the three repairs hold. They disagreed with the third, independently and for exactly the same reason, and the reason is uncomfortable: an entry that had just been corrected for quoting a figure against the wrong population went on to quote a second figure against that same wrong population, in the sentence doing the correcting.

## The finding both seats made without conferring

Task 2.1 tracks how many labelled code blocks a parser captures. Its original figures were wrong and were corrected an hour earlier: the number of missed blocks moved from 1,081 to 1,068. But the next clause still read "1,052 carry a description between label and fence, 97.32%, Wilson [96.17%, 98.13%]". That percentage and that interval are 1,052 divided by 1,081, not by 1,068, and they match to four decimal places. Against the corrected denominator the figures are 98.50% and Wilson [97.58%, 99.08%]. Both reviewers found this by computing both candidates and matching the interval against the text, which is a nice technique: a confidence interval is a fingerprint of the denominator that produced it.

The correction has been applied and now carries its own history, so a later reader can see that the entry was wrong twice about the same thing.

## The finding about the instrument that measures the watchdog

A second finding concerns a measurement script that reads two numbers out of the experiment runner and compares them. It read the two multipliers from the runner and then had the operator that combines them typed into the script as a literal. One reviewer changed the runner's operator from "maximum" to "minimum" in its private copy and ran the script: it reported that every seat fits comfortably, while the runner it claimed to be reading was cutting one seat's allowance from 1500 seconds to 900. An instrument that hardcodes half the expression it claims to read cannot detect that expression changing.

Worse, and this is the part that generalises: nothing anywhere executed that script. A search of the whole test tree returned one hit, a mention inside a comment. That is why the script had sat broken for a full day, in the same commit that created it, while the entry citing its figures went on citing them. Both halves are now fixed. The operator is read out of the runner, and a new test file drives the script against four different runner shapes, including one it must refuse.

## The finding about the stop criterion itself

This one matters most, because it is about how this whole programme decides when to stop.

The convergence rule has two sides that must both hold: a decay measure called gamma must reach 0.30, and three consecutive passes must find nothing. One reviewer asked whether the gamma side means what the script says it means, and demonstrated that it does not. Gamma is fitted to the running total of findings, not to the individual passes. So a single large opening round mechanically produces the shape gamma rewards, no matter what happens afterwards. Fed the series 11, 1, 2, 3, 4, 5, 6, 7, 8 (which rises for eight consecutive passes), gamma returns 0.324 and passes.

That was reproduced here against the project's own estimator and cross-checked against two independent implementations, all three agreeing to nine decimal places.

Gamma is not broken and has not been demoted. It correctly returns zero for constant discovery, for linear growth and for doubling, all of which fail the gamma side. What it is, here, is confounded by a large first pass: pass 1 contributed 11 of the first 42 findings. The repair is additive. Nothing was removed and no threshold moved. The script now prints a resurgence warning whenever the last three passes found more than the three before, states that gamma is dominated by the opening round, and says in terms that the gamma side should be read as uninformative in that situation and that the count side is carrying the gate.

The warning fires on the live series immediately: the last three passes found 21 against 11 in the three before.

## Four defects in instruments written during this same session

The reviewers did not find these; the tests written to satisfy them did, which is roughly the point.

First, eight mutation tests were vacuous. Each wrote a deliberately broken copy of a script into TMPDIR and checked that its output changed. But the scripts locate the repository relative to their own file, so every broken copy died at startup, produced no output at all, and the check "the expected figure is absent from the output" passed against an empty string. A mutant that crashes reads as caught. The copies now live beside the originals and the harness refuses any mutant that did not actually run.

Second, one mutation survived once it could really run, and it survived for a good reason: it had been aimed at a line the reported figure does not read.

Third, a measurement script printed a closing sentence containing a number typed as a literal. Disabling the flag that computes that number changed every calculated figure while the literal stayed put, so a test asserting on the sentence passed against a broken script. The sentence is now computed.

Fourth, a test asserted that a value equals zero exactly after the value had been read from a display rounded to six decimal places. The true value is 1.55 times ten to the minus 15. That is a floating point residue of no consequence, and believing the rounded display is exactly the habit this project exists to catch.

## Where the cycle stands

Ten passes recorded. The series is 11, 4, 2, 3, 6, 2, 3, 2, 9, 10. Gamma is 0.366, the gamma side passes, the count side fails, and the verdict is keep going. The last three passes found more than the three before them, which the new diagnostic now says out loud.

## One thing that could not be attributed

One reviewer reported that the shared sandbox it was working in lost most of its code partway through: 8 files where the canonical tree has 167, and a script that ran successfully at 03:33 failing to import at 03:36. It recorded its own two writes, verified both restored byte-identically, and declined to claim it knew the cause. It also declared which of its own figures were taken before that moment and therefore stand.

Both seats share one sandbox, and the other seat returned at 03:36:19. Two tasks have been filed: one to run the decisive test (build a sandbox, count the files, run the suite inside it, count again) and one to give each seat its own sandbox so that proposed edits can be attributed to the seat that made them. Neither is claimed as diagnosed.

Written under CDSFL note standard v1.7 (26 August 2026).
