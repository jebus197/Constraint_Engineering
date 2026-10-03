# Close of day report, CDSFL

**3 October 2026, 03:17 BST (Europe/London)**




## Purpose

This replaces the premature report issued at 23:08 on 2 October. It covers the 3 confer rounds, the Haiku classifier test, the state of the programme of study, and the 6 decisions that now sit with the founder. It is written so those decisions can be taken without reading code.


## The headline

The merge of 2 October was sound in design and carried a false safety claim, and a 3 round panel found that by execution rather than by reading. The assistant had written that the unobserved carve out keeps blocking, so that a machine wide observer failure could not drain the convergence gate. That claim was wrong. One seat demonstrated the opposite in its own sandbox: before the fix landed, an observer failure converged a run with 0 verified criticals, the gate returning its quiescence verdict over 2 unobserved criticals. The invariant had been asserted over the predicate while the defect lived in a consumer's scope.

All 3 disputed items are now confirmed and fixed, each with a falsifier that was red before and clean after, and 301 tests pass across the touched surface.


## An honest bound on those defects

One seat supplied a measurement neither blind round stated. Across 3,246 archived registry entries, the flags at the centre of 2 of the 3 defects appear 0 times. The whole mechanism landed on 2 October and has never run. So those 2 are prospective defects rather than historical ones, at 0 of 204 unconfirmed criticals carrying the sub critical refusal shape, with a Wilson interval of 0 to 1.85 per cent. They are worth fixing because the next run will exercise them, not because they have already cost anything.


## The founder's central question is answered

The question was whether reasoning is consistently adjudicated by tools, which is the intelligence first contract. The 2 seats initially appear to disagree by a wide margin. They do not. The difference is entirely the denominator.

Measured over all accepted critical findings, 393 of 930 carry no tool verdict, which is 42.2581 per cent, Wilson 39.1216 to 45.4583 per cent. Every one of those 393 comes from 17 run directories that end before the falsifier machinery existed. Restricted to the 40 run directories that have that machinery, the figure is 0 of 537, Wilson 0 to 0.7103 per cent.

The second seat, cutting the population a different way, reports 496 of 496 accepted criticals carrying a tool record, and 493 of 496 carrying a surviving adjudication, which is 99.40 per cent, Wilson 98.24 to 99.79 per cent. It cross checked with statsmodels and with Wolfram Language through the local engine, and both agree to every printed digit.

So the contract is honoured. The earlier figure of 535 of 537 was also corrected: it is the confirmed share of findings that were already tool adjudicated, not the proportion of model reasoned findings that later received a tool, so it answered a different question from the one asked.


## One finding neither earlier round surfaced

A single record carries a confirmed status and a verified flag at severity 0.8 while standing on a falsifier the discrimination control had voided, and the model that raised the claim had withdrawn it. That is 1 case where a finding survives on a record rather than on evidence, and it was found only because a seat read the whole population rather than the summary.


## Two of the assistant's own framings were refuted

The brief asserted that the lint tools have no purchase on prose, so that something else must adjudicate there. Both seats refuted it from the decider's own structure. The adjudicator is not the lint suite. It is the function that executes falsifiers, and a prose falsifier is ordinary Python over text. The premise was wrong.

The brief also asked whether a general falsifier template should be built. Both seats independently said no, and named the standards that decide it. A general guard already exists and reaches 7.76 per cent of the population, Wilson 5.8313 to 10.2575 per cent, and adding a second unwired mechanism is the exact failure class this project has recorded 11 times. The simplest sufficient answer is to extend what already exists.


## The Haiku classifier test

The test ran on 15 documents whose labels were held in a separate file and never shown to the model. Haiku found every one of the 10 positives, including all 5 prose variants that the current approach misses completely, at a cost of 2 false positives on opinion prose. Accuracy 13 of 15 against the current approach's 10 of 15.

On the founder's composability question the answer is clean. Composing the 2 approaches produces predictions identical to Haiku alone on all 15 documents, so the composition cannot be better than the single arm, and the project's own standard then prefers the single arm. Composing is not justified here.

The honest limit is that the set is too small to make the difference statistically significant. The comparison is 5 documents to 2, giving a p value of 0.453125. Resolving it would need roughly 4 times the set.


## The programme of study, and the founder is substantially right

He asked whether the study of whether the recent fixes actually work has ever been conducted. Measured against the record: arms 1 to 4 have each run twice, and measurement 9 was genuinely commissioned and reproduced on 22 September. So some of it has happened.

But arm 5 has never run. The programme document's own words are that arm 5 is the only arm that can answer whether the work of the last 15 days helped. It specifies a paired baseline against a pre window commit of 6 September, and that commit appears nowhere as an executed run. Measurement 10, which checks whether what the launcher declares matches what actually fires, has no committed script at all. And there is no single document reporting what the study found, which is very likely why it reads as never having happened.


## The desktop notification that was never built

The founder reports that a compaction alert in macOS notifications has never worked. That is correct, and the cause is simple: no hook emits a desktop notification at all. There is no call to osascript or to any notification tool anywhere in the hook directory. What exists is a notice injected into the conversation, which since 8 September addresses the founder directly rather than only the assistant, after a measurement showed the earlier assistant only version fired 42 times over 10.69 hours and was relayed once.

A genuine pre compaction alert is also not reachable from the available hook surface, because no hook fires at compaction time. A post compaction desktop alert is reachable, because a hook fires on the next message. A turn completion alert is reachable from the stop hook. The useful version of what the founder wants is therefore 2 alerts rather than 1, and the stronger protection is not an alert at all but making the run self describing, so that whatever is lost, the recovery path names the run and the study.


## The 6 decisions awaiting the founder

1. The amendments register for figures invalidated by a rule change. Both seats independently designed the same mechanism and both independently rejected the alternative of keeping superseded rules executable forever. A committed record per ruling, accepted only when the named producer re-executes the successor value as of the brief's own date, loud, failing closed, with the archived record never edited. 3 tests remain red until this lands. The question is whether to adopt it.

2. The repointing experiment. Both seats specified it and one added the control arm that makes it interpretable, a 2 arm design where the first arm replays a falsifier unedited to control for archive decay and the second repoints it at a different target. It is read only and cheap. The question is whether to run it.

3. The discrimination control blocking flag. The programme of study records this as needing a ruling, and notes that the founder's instruction of 15 September to arm it predates a panel refutation of 12 August being carried into the flag's own documentation. This has been outstanding for 12 days.

4. Arm 5 of the programme, the paired baseline. It has never run and it is the only arm that answers the effectiveness question. The question is whether it runs as part of the restarted simulated experiment.

5. Whether to merge the 3 star round fixes, which currently exist only in the seats' sandbox copies.

6. A standing recommendation of the founder's own, made on 2 October and not yet implemented: that the false positive sweep be made able to see refused falsifiers before any rule is changed. The rule was changed that day and this was not done. Measured at the correct location, 23 of 221 routed falsifier bodies are invisible to that sweep, which is 10.4072 per cent, Wilson 7.0355 to 15.1319 per cent, and 183 of them exist only as 600 character truncations.

Written under CDSFL note standard v1.7 (26 August 2026).