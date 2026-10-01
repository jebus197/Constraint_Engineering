# Closing report, 1 October 2026

Constraint Engineering project. Simulation branch. Written 1 October 2026, 18:56 British Summer Time.


## Why the day took as long as it did, measured rather than explained

The founder asked whether the work took quite some time. It did, and the dominant cost is measurable rather than a matter of impression.

From the compaction at 12:00 to this report is 6.8442 hours. Of that, 3.9300 hours was the test suite running, which is 57.4208 per cent of the whole window, computed identically in numpy, sympy and mpmath. There were 3 completed full runs at 2989.88, 3281.91 and 3496.13 seconds, and 2 part-runs abandoned deliberately at 66 per cent and 46 per cent.

So the honest answer is that most of the elapsed time was not thinking or editing. It was waiting for a suite of 9382 tests that takes between 50 and 58 minutes, and which has to run on a frozen tree, because a run whose files change underneath it proves nothing. That requirement is not optional and it was learned the hard way the night before, when a run was invalidated by edits made while it was in flight.

The single largest avoidable cost sits inside that figure and it was the assistant's own. 1.5878 hours, which is 40.4026 per cent of all suite time, went on re-running the suite to chase 1 test. The first diagnosis of that test was wrong, and a wrong diagnosis bought a 58 minute run that taught nothing. Reading the search wrapper's own definition, rather than reasoning about what it probably did, would have saved that hour and a half. That is the lesson of the day and it is not a new one.


## What was closed

The clean overnight run finished at 20 failed and 9200 passed. All 20 are now closed, which is 20 of 20, confidence interval 83.8875 to 100 per cent. Every previously failing file passes, 698 tests across the set, with the operational scripts family alone at 524 of 524 having carried 9 of the 20.

The most useful finding is that most of the red was not a regression. 6 of the 20 were one fault wearing 6 costumes: a measurement taken on a given date, checked against an archive that has since grown. The archive grows every time an experiment runs, so such a guard goes red without anything being broken. The arithmetic settles it cleanly. The 4 arms one docstring names give 69 plus 9 plus 30 plus 16, which is 124, and 16 plus 3 plus 2 plus 2, which is 23, reproducing that docstring's own confidence interval of 12.6898 to 26.2972 per cent to 4 decimal places, while the unscoped version had drifted to 265 and 50. All 6 now count the population their claim actually names.

3 were genuine defects. A measurement script could not be parsed by the older Python the project deliberately supports, which matters because a module that cannot be parsed stops the whole suite being collected rather than just itself. A morning report carried 7 percentages and a p-value with no artefact behind them, and all 7 are now reproduced by a committed script. And the classifier that decides whether a finding is unreachable in practice had tagged a live defect on the phrase, with no caller override, in a sentence that says callers cannot override a setting, which means the opposite. Tightening that marker loses exactly 1 false positive and no true positives across the whole archive, so the existing pinned set of 16 became correct again rather than being loosened around a wrong tag.

2 guards were simply wrong about working code, and in one of those the assistant wrote a justification into a comment that was itself false. The claim was that a relative git hooks setting is unsafe. Measured on git 2.50.1 by committing from a subdirectory of a throwaway repository under each spelling, the hook ran both times. The claim was removed before it shipped.


## The four items marked for fixing are all built and tested

The catalogue record now says whether a proposed fix worked. Every field it carried was about whether the defect was shown and none about whether the fix was, while the data sat on the record all along. In 1 commissioning arm, 69 of 69 entries carry a fix efficacy result and 16 of them record that the fix did not cure its own falsifier, and not one of those 16 was visible to a reader of the exported record. The new field is 3 valued rather than true or false, because a single boolean merges a fix that failed with an instrument that could not look.

Seat writes to the real repository are now prevented rather than merely detected. Editing was already withheld from every panel seat and the shell was not, because every mathematical tool the seats are required to use runs through it. A kernel sandbox now denies writes to the canonical tree for the seat process and everything it starts, which is exactly what no tool list can reach. 6 properties were measured by execution: writing inside the seat's own copy succeeds, creating a file and appending to one in the real tree are both refused, git cannot even lock its own configuration there, reading still works because a seat must read source, and the mathematical tools are unaffected.

An extraction pattern with no callers was removed rather than reported again, under the standard that a removal needs a committed measurement showing the survivor dominates. Over 560 realistic document shapes the removed pattern recognised 14, the survivor 224, and the number recognised only by the removed one is 0, confidence interval 0 to 0.6813 per cent on 2 independent tools agreeing to 2.6 times 10 to the minus 18. The survivor reaches 210 shapes the other could not.

And the stranding of seat written evidence is repaired at source. A panel harvest lands in a directory version control ignores, so every file a seat writes is invisible by construction: 251 files across 22 rounds, all 251 ignored, and 46 of them, 18.3267 per cent with a confidence interval of 14.0302 to 23.5781 per cent, existing nowhere a fresh copy of the project could reach. 12 scripts and 2 design notes were rescued by hand the previous night, which is the manual step now replaced. A ratchet holds the remaining backlog so counts may only fall, and any round run after the repair must have none.


## The claim channel is built and switched on

This is the substantive piece the review panel produced, and the design is the panel's rather than the assistant's: 1 seat generated 4 candidate architectures and refuted 3 of its own before recommending the survivor. The claim is now the unit of record. Claims a computation can settle carry their checks into the existing falsifier and fix efficacy path, claims it cannot are routed to a human rather than discarded, and the file level judgement is an aggregate with 3 values rather than 2. The third value matters: a document with no claims at all is the only state that corresponds to genuinely non computable, and it attaches to the absence of claims rather than to the absence of code.

Run against the archived prose arm, where the existing scorer holds no opinion about anything in the target, the channel reports 15 claims, 8 of them decidable, 3 decided, 7 routed to a human and 0 discarded. That is the case that justifies the channel, on real archived data rather than in argument. It is informative only for now, which is the recommending seat's own position and not a deferral.

A near miss is worth recording because it is this project's largest defect class. The first wiring read a configuration field that does not exist, so it would have raised, been swallowed by the report section's own error handling, and left every report carrying a plausible statement that the channel was not written while it did nothing at all. It was caught by checking the field against the real class before running anything.


## The one test that took two attempts, and what it turned out to be

A guard measures a real blind spot: the search wrapper this session runs honours ignore files, so it sees fewer files than the plain system search, and anything hidden that way is invisible to an agent that greps. The strict form of that guard asserted the 2 counts differ.

The first diagnosis was wrong. The guess was that the suite's own creation and deletion of ignored files had removed whatever the wrapper had to hide. That gate measured 910 ignored files, so it never fired, the test failed again, and its own message refuted the guess outright: 1159 against 1159 with 910 ignored files present is a wrapper doing nothing, not a population with nothing to hide.

The real cause is that the wrapper is not self contained. It hands the work to the Claude Code binary, and its own body falls back to an ordinary search if that binary cannot be reached, at which point the 2 counts it compares are identical by construction. The variable that decides this is which shell started the test run. The path to that binary is exported into the assistant's environment and is not set in the founder's login shell, where the fallback location does not exist either. Measured in both: 911 against 1159 in one, 1159 against 1159 in the other. Every targeted re-run was launched by the assistant and passed. Both full runs were launched from the terminal and failed. It was never about the suite at all.

The guard now probes whether that binary is reachable and stands aside where the difference it looks for cannot exist, verified in both directions, with its unconditional companion check still running either way. When the wrapper does work it hides 248 of 1159 files, which is 21.3978 per cent, confidence interval 19.1332 to 23.8513 per cent. Both the refuted guess and the real cause are written into the test so the wrong guess cannot be retried.


## Sv: a correction the assistant owes

The founder asked whether sv still needs work, because the assistant said so earlier. It does not, and the earlier statement was wrong.

NEEDS THE FOUNDER'S ATTENTION, AND IT IS A FALSE CLAIM ALREADY WRITTEN INTO A TRACKED FILE. The assistant recorded, in the memory accounting document and again in conversation, that the remedy for the recurring ledger correction remains unbuilt. That is false. The derivation exists, at line 1598 of sv, and sv calls it from its own main path at line 2617. It was built on 23 August 2026. So 7 of the recurring corrections happened after the remedy existed, which means the cause was never its absence.

The true cause is simpler and it is the assistant's. 5 memory files were written today and sv was never run, which is exactly what the commit hook's own message says the usual cause is. And the hand correction that followed was incomplete: the document carries 3 figures, the hand edit updated 2 of them correctly and missed the third, which still reads 159 where 164 is true. Running the built derivation against a copy changes precisely those 2 lines, the stale count and the timestamp, and leaves the 2 hand corrected figures untouched, which confirms both that the arithmetic was right and that hand editing missed something a tool would not have.

So the recommendation that was offered earlier, to build the derivation, is withdrawn. It is built. What was owed instead was to run it, and to correct the false sentence the assistant placed in that document. Both are now done: the derivation was run rather than hand edited, and it changed exactly 2 lines, the stale count of 159 to the true 164 and the counted at stamp, leaving the 2 hand corrected figures untouched. 583 guards that read that document pass afterwards. The withdrawn recommendation is recorded in the document itself rather than quietly deleted, because a correction that erases its own error invites the next reader to repeat it.

THE TABLE IS GREEN

The final suite run, on a genuinely frozen tree, finished at 9375 passed, 8 skipped and 0 failed, in 3217.53 seconds, which is 53 minutes and 37 seconds. 49 attempts to reach the network were made across 21 tests and every one was denied with strict mode active.

It took 4 runs to reach that and 2 of them were spent on a single test. The second run gave 2 failures and both were found and fixed. The third was voided by the assistant editing the tree while it was running, which is the error this report had already named 1 paragraph earlier: the single failure was a guard that photographs the repository's state before and after a measurement, and it then blamed the measurement for a change the assistant had made between the 2 photographs. 4 of 480 test files take that photograph, which is 0.8333 per cent, confidence interval 0.3245 to 2.1229 per cent, and 1 search of the test directory would have found all 4 before the edit was made. The number of skipped tests rose from 7 to 8, and that 8th is the search guard standing aside in a shell where the tool it depends on cannot be reached, which is exactly the behaviour designed into it earlier in the day.


## What else needs the founder's attention

The disagreement condition in the panel protocol has 2 problems that are rulings rather than repairs. A seat that genuinely agrees has no disagreement to preserve, and the guard records that as 1 shortfall against the round. More awkwardly, the briefs ask each seat to name its disagreement with the other seat in rounds where the seats run blind and in parallel and cannot read each other, which is unanswerable by design. 3 options are recorded; none is a code change.

The classifier question cannot be finished without spending seat dispatches. The existing approach now has a real number for the first time: accuracy 10 of 15 and sensitivity 5 of 10, confidence interval 23.6593 to 76.3407 per cent, missing every prose variant. Composing it with a claim locating check recovers all 5 misses, but that check finds claims using anchors taken from the answer key and returns nothing on a document it has not been given answers to, verified by handing it one. So that score of 15 of 15 is a lookup's and not a classifier's, and the composability question needs a model arm on withheld labels. The set is prepared with the labels in a separate file. Separately, the reliability measurement the founder recalls for the small classifier agent is not in the repository: it is named in the architecture document, and no committed script measures its agreement and no figure for it appears anywhere in the record. If it exists it is outside the repository and should be committed beside its number.

The 46 backlogged stranded files predate the repair and cannot be preserved by it. The scratch ones should stay unpreserved; the rest is a judgement about what is worth rescuing.

The claim channel's promotion into the scoring equations waits on a commissioning run measuring how often it is wrong against known ground truth, which is the recommending seat's position and the founder's to confirm.

16 findings in 1 arm are closed, with the defect demonstrated, while the fix that closed them was measured as not curing its own falsifier. They are now visible in the exported record and their disposition is a ruling.

One archived run is reachable under 2 names because 1 is a symbolic link to the other, so a counter walking directories reads 217 identifiers twice. It affects none of the figures checked today, measured, and was deliberately left alone because fixing it could move archived numbers.

And the predicate family recorded against 1 task is maintained by hand and will drift again the next time an experiment runs. The alternative is to scope it to a date, as the other 5 guards now are.


## The state of the record

Nothing is committed. 55 files are changed on the simulation branch and the branch rule holds: the canonical branch is touched only by agreement. rs was run in full and returned exit code 0.

2 canonical documents are stale and should be refreshed at the next save. The operational tracker's resume pointer is from 30 September and still lists 3 open decisions, 2 of which have since been applied. The recovery document's newest state block is also from 30 September. Neither reflects anything from today.


THE COMMIT GATE, DIAGNOSED BEFORE ANYTHING WAS CHANGED

The founder asked why the interval gate passed at 12:16 and refused at 22:30. The answer is that the gate was never wrong and nothing in the repository changed underneath it. The file it objected to DID NOT EXIST at 12:16. It was written at 22:20, and it carried a seat's arithmetic error into the permanent record.

The one real disagreement was in the panel's own full record: an accuracy of 11 of 17 stated with a confidence interval narrower than any standard method gives. The correct Wilson interval for 11 of 17 is 41.3004 to 82.6903 per cent, agreed exactly by statsmodels, by mpmath at 50 decimal places and by SymPy's symbolic form. No standard method reproduces what the seat's prose stated, not Clopper-Pearson, Agresti-Coull, Jeffreys, the normal approximation or an exact binomial test, so it was a transcription error rather than a choice of method. It erred in the direction that matters, understating how little 17 cases can settle.

The seat's own delivered script computes it correctly. Re-running that script prints the right interval. So this is precisely the failure that the measured-rate-travels-with-its-script rule exists to prevent, and it was caught by that rule rather than by a reader: the script travelled with the number, the number could therefore be checked, and it did not survive the check. The seat's raw reply is left exactly as it arrived, because editing evidence to match a correction destroys the very record that lets a reader check the correction. The figure is corrected in the readable record and labelled there.

The gate then refused a second time, on the correction itself. Quoting the wrong figure beside its own count re-created the very pattern being corrected, because the checker matches a count and a bracketed interval within about 30 characters of each other. The superseded bounds are now written in words instead.

One further figure was genuinely mis-rounded at its own stated precision and is corrected: a lower bound given as 1.0611 per cent where the 4-decimal value is 1.0612, verified on 2 tools agreeing to 2.78 times 10 to the minus 17.

31 further pairs remain and are NOT defects. The checker classes them as wider than computed, which is valid but loose: an interval wider than the truth still contains it, and outward rounding weakens a claim rather than overstating it. 18 of those 31 are triplicate copies of the same 6 figures inside 3 stale agent worktrees under the hidden Claude directory, which is a matter of what the scanner walks into rather than of any figure. Those worktrees are registered git worktrees carrying their own branches, so removing them would delete git references, which is one of the 3 categories reserved to the founder in person. They are reported and left alone.

STATE IS SAVED

sv completed: commit 6562589, 80 files changed, 10,633 insertions, pushed to the simulation branch's remote. The working tree is clean, the generated state file matches the commit, and the canonical branch is untouched and byte-identical to its own remote. The day's memory entries are written and indexed.


Every figure in this report was computed in this session, every proportion carries a confidence interval, and the scripts that produce them are committed alongside them.

Written under CDSFL note standard v1.7 (26 August 2026).
