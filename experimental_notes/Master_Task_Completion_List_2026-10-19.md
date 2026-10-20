# Master task completion list — every question answered, 2026-10-19

*Master task completion list. How the work went, and an answer to every question the founder asked across the 6 annotated reply files.*

2026-10-19, written through the morning.

## HOW IT WENT, IN SHORT

The work divides into 3 parts. The first was the founder's new command, qs, which marks a question and gives it a hashed identity in the project register exactly as a feature request or a proposed fix already had. That was built first on his instruction, and building it immediately exposed a defect that would have made it useless on the day it shipped. The second part was answering his questions, 27 of which were harvested from his annotations once that defect was fixed. The third was checking, by execution rather than by reading, whether the things he was told were fixed actually are.

The honest headline is that the mechanisms caught more faults than the author did. 3 commit refusals, 2 guard failures and 1 escaped mutation all came from checks rather than from inspection, and 4 separate errors in the author's own measuring instruments were found while measuring something else. That pattern is now the most reliable finding in the project: the code under test is in better condition than the instruments used to examine it.

## THE NEW COMMAND, AND THE DEFECT IT UNCOVERED

qs is live. A question now carries its own hashed identity, distinct from the same sentence recorded as a proposed fix, because the identity digest includes the kind. That distinction matters rather than being tidy: answering a question does not build the fix, so the 2 must not collapse into 1 record. A question is tied to what it asks about through the fields that already existed, namely the task entry, the exact code identifiers, and the file and position of the annotation, so no change to the record format was needed. 15 tests hold it and 3 deliberate breakages each turn it red.

Then the defect. The harvester reported that 0 annotations carried a marker, while the founder's files carried 30. He writes a marker on its own line below the annotation it belongs to, like this: a line beginning with a hash opens his comment, then a blank line, then the bare word qs. An annotation is recognised by its leading hash and a marker line has none, so the marker was never part of any annotation's text, and scanning that text for one could never find it. Measured across every reply file: 30 markers, 30 of them written on their own line, 0 written inline. So there is exactly 1 form to support and the rule is unambiguous. It is now fixed in the reader, which owns annotation parsing.

A second trap sat directly behind it. 28 of the founder's 37 reply files use carriage returns alone as line endings, which is 75.6757 per cent on a 95 per cent interval running from 59.8827 to 86.6386 per cent. In Python, a dollar sign in multiline mode matches at the end of the text and before a line feed, but never before a carriage return. So a marker pattern anchored that way cannot fire in 3 quarters of his files even when the marker is present in the text. Routing the work through the reader, which splits lines in a way that handles all 3 conventions, avoids that rather than patching around it.

The founder was also right about pr. The stop gate was counting a kind called pr, which has never existed. The kind is pf, renamed before the harvester shipped precisely because pr is already his panel review command. So that figure has read 0 since the day it was written, whatever the register held. Corrected, with qs added alongside.

## CAN HIS RESPONSES BE PARSED IN FULL, WHICH HE ASKED DIRECTLY

**THE ISSUE.** Parsing his annotated replies has failed 3 times, and after each repair it was reported as fully fixed.

**HIS QUESTION.** He asked whether the parsing problem is genuinely fixed, noting that it was blamed on his use of Word, then apparently discounted and blamed on the parser instead, and he instructed that extraction must be made complete.

**THE ANSWER.** It now parses in full, and that is a measurement rather than a claim. A new producer checks 4 properties against the raw bytes of every file: that each annotated file decodes, that every annotation present in the raw text is returned, that no annotation loses characters, and that every own-line marker is attached to its annotation. It reports 644 of 644 annotations, which is 100 per cent on an interval from 99.4070 to 100 per cent across 90 annotated files, and 30 of 30 markers. 7 tests hold it, and it goes red the moment any of the 4 stops holding.

On the Word question the record differs from his recollection in one specific way, and it is worth stating plainly. The reader written on the 11th of October states both halves in a single paragraph: that his move from rich text to plain text is the proximate cause and is not his fault, that Word's plain text encoding rather than the file extension is the defect, and that the fix therefore belongs in the reader and he changes nothing. Those were one position with 2 parts, not a diagnosis made and then withdrawn. It cannot be ruled out that something looser was said in conversation at the time, and if so that was imprecision on the author's part.

Where he is straightforwardly right is the claim of completeness. 3 separate gaps have now been found. On the 11th of October, decoding, which made 15 of 40 annotated files invisible and hid 221 of his responses. On the 13th, truncation, where one annotation returned 97 of its 1,053 characters and lost the operative clause. And on the 19th, today, the markers, 30 of them. Each repair was real. The common fault is not any of those bugs but that completeness was never itself measured, so the scope of each repair kept being reported as the whole. That is now a standing measurement, which is the only form of the claim that can be checked.

A NOTE ON THE AUTHOR'S OWN INSTRUMENTS WHILE BUILDING THAT MEASUREMENT. The first version read rich text files as plain bytes and reported the reader as lossy when the reader was correct. The second counted every markdown heading in a saved web page as one of his missing annotations. The third applied a markdown heading rule to his plain text files and so rejected 8 real annotations, including his trailing hash convention where he wrote, in the last morning report I said, followed by a hash. 3 false alarms about the reader, all of them the author's, each caught by looking at what the check actually matched rather than at what it concluded.

**RECOMMENDATION.** None needed. The measurement is committed and guarded.

## THE OPERATIONAL DIRECTIVES, WHICH HE ASKED ABOUT TWICE

**THE ISSUE.** A report of the 17th of October told him that the operational directive loses 38,339 of its 46,374 characters, which is 82.6735 per cent, and a parked item told him every model receives about 9 per cent of it as a dump of configuration flags.

**HIS QUESTION.** He asked whether this had really not been fixed, since the 2 of them had already agreed that the operational directives should reach every model in full without truncation, and whether the parked status meant it was merely queued.

**THE ANSWER.** It was fixed, on his own ruling of the 14th of October, 3 days before the report that told him otherwise. That report was stale when it was written, and that is the author's error rather than an outstanding defect. His ruling split 1 cap into 2 fields that mean different things. The work bound still governs the review target, the code extracts and the brief, which is the work volume the harness measures per experiment and the only quantity a cap was ever meant to limit. The specification bound is separate, and the value meaning deliver it whole is the default for every model. His words at the time were that there was never an intent, as far as he recalled, to apply cap reasoning to the core operational directives themselves, and that 7,000 or so words for a system prompt is hardly excessive for any modern model.

Verified by execution rather than by reading the comment. The specification bound is the deliver-whole value for 5 of 5 models and on the shared default. Calling the loader for each of the 5 returns 28,617 characters, identical across all 5. That is the whole specification, not the 2,503 character flag dump the parked item describes.

The parked item was still being shown to him as needing his decision, 5 days after his ruling settled it. It has been annotated with the executed evidence and moved out of that status. A second parked item, concerning a pruner that made the constraint density it optimised worse, was in the same condition and settled by his ruling of the 16th retiring the density ceiling outright. Both are now marked, and neither was deleted.

WHY THEY WERE STILL SHOWING AS LIVE. The generator that rebuilds the parked file classifies an item by looking up its task entry. 4 of the 8 live items are finding identifiers rather than task identifiers, so the generator cannot classify them at all and leaves them where they are. That is a real gap in a facility built on the 17th to prevent exactly this.

**RECOMMENDATION.** The generator should treat an unclassifiable item as a question rather than silently leaving it in the live section, so an item it cannot judge is visible as such. That is a small change and it is recorded rather than built, because it changes what he is shown.

## THE STAGGERED DISPATCH, WHICH HE ASKED WHETHER THE RUNNERS EVER GOT

**THE ISSUE.** Dispatching more than 1 model from the same vendor at the same moment caused server failures, and the fix agreed was to stagger dispatch by a few seconds rather than to run seats strictly one after another, which he judged would make large experiments impossible to complete.

**HIS QUESTION.** He asked whether this was ever implemented, whether it reached only panel reviews or the runners as well, and instructed that it should be in both, including the simulated and the real runner.

**THE ANSWER.** It reached the panel only. The panel has had a staggered dispatch since his ruling of the 8th of October. Both runners kept a mutex that was held across the whole dispatch, tool loop included, so 2 seats sharing 1 credential could never overlap and a round cost the sum of their durations rather than the longest of them. That is the behaviour he rejected in the words he used about 70, or 700, or 7000 models never completing.

For 11 days 2 guards asserted directly opposite properties on 2 modules and both were green, which is why neither side showed a problem. The panel's guard required its shared seats to overlap. The runner's guard required its shared seats not to. The runner's guard is dated 1 day before the ruling that superseded it.

This is now built in the runner. The gate is held only while a seat claims its start instant, then released, so starts sit a stagger apart and the dispatches themselves overlap. The committed measurement that licenses replacing a guarded property, over 102 archived rounds where both free seats answered, is a median wall clock of 1,779.6 seconds serialised against 984.4 seconds staggered, a mean saving of 0.4001 on a bootstrap interval from 0.3851 to 0.4147, and never slower anywhere in the record. So the stagger beats the mutex on time and loses nothing.

ON THE 3 SECONDS HE SUGGESTED. The shipped value is 20 seconds, and the reason is 2 measured bounds rather than a preference. The floor is 18.7 seconds, which is the one genuinely simultaneous failure in the whole record, occurring at the moment a session is established. The ceiling is 26.7 seconds, the shortest first-seat duration in the archive, beyond which staggering can actually be slower than serialising. 3 seconds sits below the floor and would not clear the collision the stagger exists to avoid. He may of course overrule the value; the bounds are the reason, not a preference.

12 tests hold it and 3 deliberate breakages turn it red. 1 of those escaped at first and the escape is the instructive part: setting the shipped stagger to 0 left every timing test green, because each of them substitutes its own value so the suite can run in milliseconds, and none of them could see the default. The stagger could have been switched off across the project with nothing to notice. 4 assertions now hold the default, including one requiring the runner and the panel to ship the same number, because 2 copies of 1 mechanism carrying 2 different values is how they drift apart.

**RECOMMENDATION.** Accept 20 seconds or name a different value. Nothing else is outstanding here.

## THE ROUTING LADDER, WHICH 4 OF HIS QUESTIONS TURN ON

**THE ISSUE.** The routing ladder decides which seat is asked first when a finding needs checking. He has ruled 4 times that nothing but demonstrated capability should rank a model, and the code still falls back to a frozen list of vendor names.

**HIS QUESTIONS, which were several.** He asked for a plain English explanation of what ladder membership and ladder order mean and why the distinction matters. He asked what is so special about a model's name that it can serve as a measure of performance, when a hash identifier assigned in the opening blind run of an experiment apparently cannot. He asked whether the recent work on this is safe and will work as intended. And he observed that the football analogy was only an analogy, and that the routing policy built from it should carry a technical name or be understood as a form of load balancing or routing.

**THE ANSWER, AND HIS INSTINCT IS CORRECT.** Membership means which models are on the ladder at all, that is, the roster of seats available to be asked. Order means the sequence in which they are tried. The problem is that 1 list in the code carries both meanings at once. His ruling of the 7th of October, that a particular free seat should be added to the ladder, is implemented as that seat's presence in the list, and a test checks the list has 6 entries. His ruling of the 9th of October, that there should be no distinction between models other than a ranking number, says the ORDER must come from measurement. Emptying the list to satisfy the second ruling deletes the implementation of the first. That collision is why an attempt to empty it on the 17th was reverted within the hour, and why this has sat unresolved for 10 days.

On his sharper question, a model's name is NOT a measure of performance, and neither would a hash identifier be. Both are labels. The real situation is that NO order is establishable from the evidence available, and when no order can be established, any order is arbitrary. The measurement is this: across all 3,020 archived registry entries, the only recorded quantity that measures falsification capability rather than mere productivity is the falsifier verdict. 2 seats have refuted anything at all, at 10 of 701 and 6 of 521, and 3 of the 5 paid seats have refuted nothing in 373, 366 and 342 attempts respectively. 26 refutations in the entire archive. The overall test rejects the idea that the seats are equal, with a chi-squared of 14.5802 on 4 degrees of freedom at a probability of 0.005656, so they genuinely do differ. But 0 of the 10 pairwise comparisons survives correction for multiple comparisons, and a ranking is exactly a set of pairwise orderings. So the archive supports the statement that they differ and supports no statement whatever about which is stronger.

That is why his season design is not a preference but the only sound footing. The order cannot be inherited from an archive that cannot support it, so it must be measured inside the experiment that uses it. That is built: the order is derived from the experiment's own first round and then frozen for the remainder, and a test drives it with second round evidence that would reverse the ranking to confirm it does not reshuffle.

THE RECOMMENDATION, AND IT NEEDS NO RULING FROM HIM BECAUSE IT BREAKS NEITHER OF HIS. Separate membership from order into 2 things. Membership becomes a set, which preserves his ruling of the 7th exactly. Order becomes a function of measured capability which, when no order can be established, returns the members in a stated arbitrary sequence that makes no capability claim at all. That satisfies his ruling of the 9th without deleting the implementation of the 7th, and it removes the only reason the vendor list still exists. It also moves directly toward the triviality he asked for separately, that adding or removing a model should be trivial, because membership becomes a single list with no ordering semantics attached. This is not built yet, because the whole-tree test run is currently reading those files and changing them underneath it would invalidate the measurement.

ON THE NAME. He is right that the football framing was an analogy and should not be the name of a mechanism. In standard terms this is a scheduling and routing policy with 2 parts: an eligibility set, and a priority ordering derived from observed performance with a defined fallback when the observation is not discriminating. Calling it a capability-ordered routing policy would be accurate and would stop the analogy leaking into the design.

## THE SEVERITY RULER, AND WHETHER IT SHOULD CHANGE AT ALL

**THE ISSUE.** A finding carries a severity between 0 and 1, counts as critical at or above 0.7, and the number of criticals drives the gate that decides when an experiment may stop. Repeat assessments of 1 defect wobble by about 0.14 against a decision band about 0.09 wide.

**HIS QUESTION, and it is the most interesting one he asked.** He asked whether the severity gate needs changing at all, or whether the wobble is telling us something true about severity itself. Given that severity is conceptually the risk that a fault remains after a number of passes, he asked whether it is not inherently a measure of confidence, whether it would not vary across experiments and conditions, and whether it should not fall within a dynamically calculated range rather than a single fixed value.

**THE ANSWER.** His reading is better supported by the project's own evidence than the framing the panel was given. The brief handed to the panel treated the wobble as instrument noise to be smoothed away. The archive says something stronger: an exact threshold severity of 0.7 occurs in 156 of 2,898 archived entries, which is 5.3830 per cent, because models anchor on the published cut. That is not noise around a true value. That is a population of findings about which the assessor is declining to be more precise than the published boundary, which is exactly the confidence interpretation he describes.

If severity is a confidence rather than a point measurement, then 2 things follow that neither panel seat proposed. First, the right object is an interval, and the gate's question becomes whether the interval lies clear of the threshold rather than whether a point does. Second, a finding whose interval straddles the threshold is not a measurement failure to be smoothed, it is a finding that needs another assessment, which is a routing decision the harness already knows how to make.

THE MEASUREMENT WAS THEN RUN, AND IT CORRECTS PART OF WHAT IS WRITTEN ABOVE. An earlier version of this report said the spread measurement costs nothing and is decisive, and implied it would support his reading over the brief's. Having run it, the first half is true and the second is not, and the correction is worth more than the original claim.

It took 6 attempts to make the measurement possible at all. The registry keeps 1 severity per entry and its verdict records carry none, so 0 of 8,168 verdict records hold an independent assessment. The independent severities do exist, 7,654 of them, in the per-round finding files, each tagged with the model that gave it. What is not recorded there is which findings merged into the same defect: the field meant to carry that link is present on 280 raw findings and empty on all 280. The link exists only in the registry entry's alias list, so the join has to run from the registry back to the rounds. And it must be scoped to a single run, because finding identifiers repeat in every run. Getting that wrong inflated both headline figures, and the inflated versions were in the first draft of this section.

WHAT THE CORRECTED MEASUREMENT SAYS, over 147 entries where 2 or more independent assessments of 1 defect are recoverable within a single run. The spread between assessments has a median of 0.1200 and a mean of 0.1786, against the 0.1419 the brief asserted. So the brief's noise figure is approximately right, sitting between the median and the mean, rather than understated as the earlier draft implied. His confidence reading is therefore NOT settled by this measurement, and no archive can settle it, because it is a question about what severity means rather than about how the number behaves.

BUT A MORE CONSEQUENTIAL FINDING CAME OUT OF THE SAME JOIN. The number the convergence gate reads is not traceable to the assessments beneath it. It equals the median of its inputs in 31 of 147 cases, which is 21.0884 per cent, the mean in 10.2041 per cent, the minimum in 30.6122 per cent and the maximum in 38.0952 per cent. And in 35 of 147 cases, which is 23.8095 per cent on an interval from 17.6469 to 31.3061 per cent, it lies OUTSIDE the range of its own inputs entirely: 24 of those above every assessment and 11 below every one. One archived entry carries assessments of 0.35 and 0.45 and a kept value of 0.95.

**RECOMMENDATION, REVISED.** Neither panel fix should be built until that is explained, because one of them proposes pooling the assessments into a median, and pooling into a median would change roughly 79 per cent of merged severities rather than refine them. The question to answer first is narrow and mechanical: what rule produces the kept value, and is a value outside the range of its inputs intended. Producer: scripts/is_severity_noise_or_disagreement_2026-10-19.py.

## THE QUESTION HE ASKED MOST OFTEN, IN 6 SEPARATE PLACES

**THE ISSUE.** Several reports listed faults found in the author's own measuring instruments, and described the resulting figures as corrected.

**HIS QUESTION.** He asked, repeatedly and in almost the same words each time, whether correcting a figure means the instrument that produced it was also fixed, and said plainly that by fixed he does not mean rewritten by hand, he means the source of the error repaired so it cannot repeat.

**THE ANSWER.** He is right to keep asking, because the answer differs case by case and the reports did not distinguish them. The pattern across every instance checked today is that the figure was corrected and the instrument was usually corrected with it, but the CLASS of error was not closed, which is why the same shape keeps reappearing. Today alone produced 4 fresh instances of it: 3 while building the parse measurement, and 1 where a comparison of lint counts between 2 versions of a file was invalid because the 2 were read from different directories and a path-sensitive rule fired for only one of them. That last one is the third time this specific trap has been recorded, and the code comment describing it was read on the way to falling into it again.

The honest statement is therefore this. Individual instruments are repaired. The class is not closed, and the only mechanism that has reliably caught these is comparing 2 independent forms by executing them rather than reading either. Every instrument error found today was caught that way and none was caught by inspection.

**RECOMMENDATION.** 2 things, neither built yet. First, any comparison between 2 versions of a file must be run with both at the same logical path, because at least 3 of the project's rules behave differently depending on where a file sits. Second, a measurement that reports a clean result should state what it would have reported had the code under test been broken, which is the only cheap way to detect a check that cannot fail.

## THE REQUIRED QUIET RUN, AND WHETHER 7 IS ARBITRARY

**THE ISSUE.** The number of consecutive settled rounds required before an experiment may be declared converged was raised from 3 to 7.

**HIS QUESTION.** He asked what a premature close means in this context, noted that an extra hour is a real penalty and more rounds might mean more churn, asked whether models should instead do more work per round, whether any model ever sits idle when work exists, and whether 7 should be fixed at all rather than derived from the size and complexity of the target under study.

**THE ANSWER.** A premature close means a run that was declared converged and then produced a new critical finding afterwards, so the declaration was wrong. The curve that set 7 is measured rather than chosen: 23 premature closes in 182 opportunities at a window of 3, falling to 6 in 131 at 5, and 0 in 99 at 7. 5 meets the target on the point estimate alone but its upper bound sits at 9.6324 per cent against a 5 per cent target. 7 is the first window with no premature close observed and the smallest whose upper bound meets the target. Going further actively hurts, because by 9 the upper bound rises back above target as the denominator shrinks.

On his deeper question, he is right that a fixed number is the wrong shape and the evidence above shows why: the figure was derived from one archive of one kind of target. A simple target plausibly needs fewer settled rounds than a complex one, and nothing in the current design lets it have them. Deriving the window from the target rather than fixing it is a better design and it is not built.

**RECOMMENDATION.** Keep 7 for the upcoming runs, because changing a convergence criterion between runs would make the 3 runs incomparable, which defeats the purpose of running them. Record the dynamic window as the successor design and derive it from the same curve, once there are archives from targets of more than 1 complexity to derive it from. On idle models, no measurement exists of whether a seat ever waits while work is available, and that is a genuine gap worth a cheap producer.

## THE REMAINING ANSWERS, BRIEFLY

ON WHETHER THE SECOND PANEL ROUND REACHED AN OUTCOME. It did. The 2 proposed severity fixes do not compose. Tested across 62 archived result catalogues, the natural combination changed the outcome in 0 of them and destroyed the one directional guarantee that made the smoothing fix safe to adopt at all. Both seats reached that independently, and the brief contained no instruction to agree.

ON THE FIX DESCRIBED BY A MODEL AS EQUIVALENT TO COOKING THE BOOKS. He is right that this settles the choice. A fix tuned until an archived verdict moves is fitting the gate to the archive, and the project forbids that. On the evidence, neither proposed fix should be adopted as the primary change, and his own interval framing above should be measured first. If one must be chosen, it is the pooling fix, because it reports the gate unchanged, which is the property a non-cooking fix should have.

ON FALSIFICATION IN THE CAPABILITY FINGERPRINTS. He asked whether a measure of falsification, tool use or mathematical model use should be included. It is not there. The 11 fingerprint files carry 4 fields only: the model identifier, the experiment, a timestamp, and an observed block holding capacity, attention and productivity. No field records a falsification outcome. The ladder reads falsifier verdicts from the registry instead, which is why the archive measurement above was possible at all. Adding it to the fingerprints is a sound idea and would put the capability measure where the capability record lives. Recorded as a feature request.

ON WHETHER RESTORE AFTER COMPACTION IS NOW MECHANICAL. Yes. The entry covering it is complete and committed, and the automatic restore fired at the start of this session and reported success before any other work began.

ON THE START-OF-EXPERIMENT HEALTH CHECK HE DESCRIBED AS A BIOS CHECK. It exists and it is wired. A preflight runs before dispatch at 2 separate points in the runner and refuses a launch whose machinery contradicts its target, on the stated principle that the cheapest possible discovery of a doomed configuration is before the first paid dispatch rather than at round 3 with the money spent. 13 tests hold it.

ON THE WORDS TRAP AND THIEF IN AN EARLIER REPORT. He was right to query them and the wording was poor. The shell mechanism involved is a handler registered to run when a script exits. Registering a second handler for the same event replaces the first rather than adding to it, so a later registration silently discarded an earlier one. Nothing was stolen and no security question arises. The report should have said that a later registration silently replaces an earlier one.

ON WHO MAY REJECT A PROPOSAL. He asked what happens when only he may reject, and whether that means all proposals are treated as accepted. It does not. A proposal sits OPEN until it is implemented, merged, or rejected, and OPEN is not acceptance. What the register refuses is the author of a proposal marking it rejected, because a model declining its own suggestion is not a decision. His point that this should be phrased in terms of the human in the loop rather than the founder is correct, since not every researcher using this is the founder, and the wording should change.

## WHAT NEEDS HIS RULING, AND NOTHING ELSE DOES

1. THE STAGGER VALUE. 20 seconds is shipped, bounded below by 18.7 and above by 26.7, both measured. He suggested 3, which sits below the floor. Accept 20 or name another number inside the window.

2. WHETHER A TEST MAY RUN THE COMMIT HOOK'S FULL GUARD LIST. 3 tests do, and each one runs 70 test files inside the whole-tree run. That is what deadlocked the run today, and it means any complete measurement costs 2 runs. The alternative is a nested run over a named subset, which is cheaper but no longer tests what the hook actually does.

3. THE SEVERITY RULER. His own interval framing should be measured before either panel fix is built, and the deciding measurement costs nothing. Confirmation to run that first is all that is needed.

4. THE 7 ENTRIES ALREADY AWAITING HIM from earlier work, unchanged: the number formatting rule, the save mechanism refusing its own follow-up, the credential redactor withholding an ordinary setting, the convergence mode with no consumer, the last programme measurement's cost, the guard that was red outside the guard set, and the claim channel's promotion form.

## WHAT IS STILL RUNNING, AND WHAT REMAINS

The whole-tree test run is in progress, excluding the 3 tests that run the commit hook inside it. Those 3 are measured separately. This is the first run in 382 commits that can complete, and the reason none completed before is now fully explained: a 300 second per-test limit killed 2 of them, and the third deadlocked the run by nesting a 70 file test run inside it on a machine with 1.21 gibibytes free.

Not yet done, and not blocked on him: separating ladder membership from ladder order, which breaks neither of his rulings and is held only until the test run stops reading those files. The panel reviews he asked to be gathered into fewer rounds are also held, because available memory stands below the 2 gibibyte threshold a panel round needs, and Firefox, which he suspected, is not running at all. The memory is in the browser and the desktop application, and no application other than Firefox may be closed on his behalf.

Written under CDSFL note standard v1.8.
