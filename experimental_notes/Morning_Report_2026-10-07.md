# Morning Report, the Ladder, Gamma, and What the Panel Teaches the Runners

7 October 2026, 13:45 BST, Europe London

## THE ANSWER TO THE GAMMA QUESTION, WHICH WAS THE ONE THAT MATTERED

Gamma has not been demoted. Nothing has been made recording only. The panel's remedy was not implemented, and the reason is that the evidence does not support changing gamma in either direction.

The challenge was right about something specific, and it is worth stating plainly. The panel's measurement flipped every unresolved critical finding to confirmed at the round it was already sitting in. It held the timing fixed. So it answers the question, what if these had been resolved, and not the question, what if the ladder had resolved them promptly. Prompt resolution is exactly what removing the rung limit is for.

That distinction is not theoretical. Of 210 routed resolutions in the archive, 174 landed in a later round than the one that filed them, and only 36 in the same round. The median delay is 1 round and the longest is 12. Routing today mostly defers. Exhausting the ladder is the change that could stop it deferring.

So three worlds were compared over the 33 archived runs of at least 3 rounds. The first is the world as recorded. The second is the panel's world, where the findings resolve but stay late. The third is the world the challenge describes, where they resolve and arrive earlier by the measured median delay.

Gamma falls from the first world to the second in 6 of 33 runs, which is 18.1818 percent with a 95 percent interval from 8.6108 to 34.3882 percent. It rises again from the second world to the third in 5 of 33, which is 15.1515 percent with an interval from 6.6505 to 30.9199 percent. One run that had crossed the 0.30 threshold downward comes back above it.

The direction of the challenge is therefore supported, and it is not established. Those are both true and both need saying. A 15 percent effect with an interval spanning 7 to 31 percent is a direction, not a result.

This is also not a refutation of the panel. The two measurements use different criteria over the same archive, so the fact that this one finds no threshold crossings neither confirms nor contradicts the panel's two. Presenting it as a refutation would be the kind of borrowed number this project refuses.

The sizing instinct in the challenge was also correct. Two runs out of fourteen carries an interval from 4.0094 to 39.9414 percent. An interval spanning an order of magnitude is not a basis for altering the most protected part of the model.

What is actually established is narrower than either framing. The critical gamma value is sensitive to WHEN findings resolve, so the rung budget is an undeclared input to the convergence gate. Whether exhausting the ladder raises or lowers gamma in practice is established by neither measurement, because neither models what exhaustion does to timing. The decisive evidence is a paired run, exhaustion against the limit, which is an experiment rather than a code change and belongs in the programme of study.

## ON THE SUSPICION THAT THE LADDER ORDER IS INVERTED

The order is not inverted. It runs Codex, CC2, ChatGPT, Gemini, DeepSeek, strongest first, which puts Codex at the top and DeepSeek at the bottom, matching the stated experience of the project.

But the instinct that the ordering is suspect was right, in a narrower place. With the counting defect repaired this morning, the measured confirmation rates for the live models are Codex 0.2818, Gemini 0.2644, ChatGPT 0.1567, CC2 0.1510, DeepSeek 0.1382. The two extremes agree with the frozen order. The middle does not. Gemini measures second and is ranked fourth. CC2 measures fourth and is ranked second.

## THE LADDER NOW CLIMBS, AND ITS LAST RUNG POINTS BACK AT THE SOURCE

The setting that chooses between one model for every seat and the full ladder defaulted to the single model, so the ladder was consulted by nothing. That default is now the ladder.

The simulated ladder carried 6 seats on only 2 underlying models, so it could separate 2 behaviours however many seats ran. It now carries 4. Every one of those model names was dispatched to before it was written down, each answering a 16 token probe: 6.60 seconds, 5.69, 7.24 and 3.97. A fifth candidate answered too and was deliberately excluded, because it is a routing alias that serves different models for planning and execution, so the record could not say which model actually replied. Cost moves down rather than up, since 4 of the 6 seats previously went to the most expensive model and now 2 do.

The assignment of seats to models is deliberately arbitrary, a simple rotation. It encodes no claim about capability, because the standing position is that only measured capability should matter and a name should record who did what and decide nothing else. A map that paired a seat labelled Codex with a model chosen because somebody believes Codex is strong would be precisely the defect objected to.

Two tests were asserting that defect and have been rewritten rather than weakened. One passed only because the map happened to pair like with like, so it could not tell a faithfully applied map from a lucky one. The other required three named seats to sit on the strongest model because they are, in its own words, top three vendors in the validated strength order, which is a capability claim keyed on a vendor name written into the test suite.

The last rung now points back at the source model, as instructed. It is not a blind retry. The source is handed the verdict its own attempt earned and the code that earned it, which is information it did not have the first time, and which is exactly what the ladder gives a stronger rung. On a single model roster this is the only rung there has ever been.

That change broke a hidden assumption twice, and the second time is the instructive one. The runner decided a ladder was empty by checking whether zero rungs had been tried. That was exact while every rung came from the ranked list. The new rung dispatches precisely when the list is empty, so the rungs tried became 1 and the check silently stopped firing. The finding then lost its deferral mark, never entered the irreducible queue, and the alarm that one pre-registered experiment names as its reportable outcome could not fire. One level further up, a second tally asked whether any model had been reached, which answered no exactly when the ladder was empty, and the new rung made it answer yes, so the case fell into retry a later round, which is futile when no other writer will ever exist. Both are now recorded as facts rather than inferred from counts.

## WHAT ELSE WAS FIXED

Every remaining test failure is closed, and none was re-baselined.

Two of them shared a cause worth knowing. The length of an abbreviated commit identifier is a property of the repository, not of the commit. The classifier matched archived identifiers by exact equality, and the repository has grown enough that the version control tool now prints eight characters where all 97 archived records store seven. Every comparison failed, every archived fix appeared not to apply, and 30 records collapsed from their two real causes into one vague one. Nothing about the archive changed. The cheap wrong fix was available and was refused: re-measuring the expected distribution against the broken classification would have turned both tests green and made the defect the new baseline.

A containment guard was poisoning itself. It wrote a fixed probe value into the real repository configuration and never removed it, so a single historical lapse failed it on every later run for ever. The probe value was three days old while a live test in the same minute was refused outright. The containment was working perfectly and the guard was reporting its own leftover as a current breach, which is the most expensive kind of false alarm because it makes a working control look broken.

The archive audit was walking seat scratch space and admitting a model's own synthetic test file as an archive record. A tool whose entire purpose is to refuse inferred dates was reporting an unknown age it had manufactured for itself.

The counting defect in the capability record is fixed. When a finding was routed away, the model that filed it received nothing at all, not the credit and not the failed attempt either. A model that files findings it never resolves therefore accumulated no denominator, and an empty record read as a perfect one. Counting the failure is not a penalty; routing only fires on a finding its source did not resolve, so the attempt genuinely happened. Two of eleven models change rank, and the simulated models' rates fall by roughly 0.2 to 0.3.

The runner now dispatches seats that share one subscription one at a time, as the panel already did. This became urgent the same day rather than being a standing nicety: while the simulated roster used one model the concurrency was harmless, and widening the ladder to 4 models is what made the contention reachable. Routes that do not share a subscription still run fully in parallel, which is asserted by measuring the actual time windows rather than assumed.

The six switches that are enabled in no configuration have been decided. None is dead: all six are read by live code, and five gate a real branch and have a test that turns them on, which is dormant by choice. One, the human review pause, is live in the active runner with a command line flag and two branches, and no test has ever turned it on. Its wiring is now exercised; its gate needs a real run and is recorded as outstanding rather than asserted on its source.

The tool that produced that answer was wrong once, in the dangerous direction. It counted a read as decisive only when the read itself sat inside a condition, so the ordinary pattern of assigning a value to a variable and then testing the variable scored as reading something and deciding nothing. It condemned a working switch using this project's own phrase for a dead addition. A measurement that errs toward condemning working code is worse than no measurement, because the action it recommends is destructive.

## WHAT THE PANEL TEACHES THE RUNNERS, FOR DECISION

Two lessons are already applied. Every runner now asks each model to say Ready before any work is sent, and the runner serialises models that share one subscription.

Four remain, and they are offered for decision rather than built.

First, and the strongest candidate: the panel applies a substance test to every reply and the runner applies none. The panel refuses a reply that is merely non empty, because an error string, a usage notice or a holding note is answering without answering the question. The runner accepts whatever comes back. This is the same class of defect that cost 2423 seconds for nothing, and the test already exists in the shared code.

Second, a retry must not erase the attempt it replaces. The panel now preserves each attempt, after a failed dispatch was overwritten and survived only because a sandbox copy happened to predate the overwrite. Whether the runner has the same exposure has not been measured and should be.

Third, state should be detected rather than declared. The panel used to decide whether a round was blind or joint by reading an environment variable, so forgetting the variable silently downgraded the check. It now decides from what the briefing document actually contains. The runners have several places where a mode is declared by a flag that can be forgotten.

Fourth, when two pieces of code hold an opinion about the same fact, one of them should import the other's definition rather than restate it. A briefing could declare a required field in a form that the checker reading the replies could never recognise, because the two tests about the same field were each individually correct and disagreed about what counted.

## OUTSTANDING AND NEEDING A DECISION

The paired run that would settle the gamma question, exhaustion against the limit, is an experiment and needs scheduling.

The human review pause has never had its enabled path executed.

The four panel lessons above are proposals, not changes.

Written under CDSFL note standard v1.7 (26 August 2026).
