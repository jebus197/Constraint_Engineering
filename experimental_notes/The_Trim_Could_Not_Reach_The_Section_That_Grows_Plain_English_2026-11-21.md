# The trim could not reach the section that grows

*21 November 2026, 18:15 GMT*

## What happened

The project keeps a small index of standing lessons that is loaded into every working session automatically. It had almost no room left: 14 characters before the save tool would start refusing to save at all. The founder's position was that this index should trim itself so that it never fills up, and that if it had stopped doing so, it needed fixing.

His account of the design turned out to be right, and the earlier diagnosis of the fault was wrong. The automatic trim has existed since early October and runs every single time the project saves state. What nobody had ever written down is which part of the index the trim is allowed to touch.

## The part that could never be reached

The index has 7 sections. One of them, holding the standing lessons, accounts for 0.810667 of its entire length. The section the trim is permitted to age out of accounts for 0.063955. So the trim was working perfectly on 0.063955 of the file while all the growth happened in the 0.810667 of it that it was forbidden to touch.

The exclusion was not an oversight. A standing lesson does not become false because it is old, and an existing check in the project asserts that those lessons are never aged out. The design decision was correct. It simply left the file with no way to stop growing.

## Why a bigger clear-out would not have worked

The founder asked that the index never fill up, which is a promise about every future day rather than about today. Treated that way it can be tested, and it was, using a constraint solver. The question put to it was whether any one-time clear-out, of any size at all, keeps the file under its limit forever. The answer is no, and a symbolic algebra system independently quantified it: emptying the index completely buys 38.38 days, because it refills at roughly 638 characters a day. A third engine was then asked the same questions and returned the same answers.

So the fix could not be a bigger clear-out. It had to be a permanent ceiling that reasserts itself every time the project saves.

## What has to be given up, and it is arithmetic rather than a choice

If lessons keep arriving and the loaded window has a fixed size, something must leave each time something arrives. There is no clever way around that. What was avoidable is losing anything: an evicted lesson is written to a companion file, the index links to it, and the project's recovery command reads that file in full. Nothing is deleted and every lesson is still in force. What is genuinely given up is that an evicted lesson is no longer in front of the model on an ordinary turn.

Because something must leave, the order in which things leave is the only real decision. 2 orders were compared on a measurable property: how many days a lesson marked as most important stays inside the loaded window. Removing the oldest first gives 15.31 days. Removing the least important first gives 8.25 days and then runs out of anything it is allowed to remove. Doing both, least important first and oldest first within each importance level, gives 19.43 days. The combination was chosen because it was measured to beat both halves, not because combining things sounds thorough.

## A second repair: the commit check can now be watched

Before any commit, the project runs 5,233 checks. That phase takes about 42 minutes and, until now, produced no visible output whatsoever while it ran, because the output was being collected into a variable rather than shown. The founder has a standing instruction that a long-running process must always have a terminal showing its current output, and this collected output was what made that impossible.

The obvious repair is a one-line change that would have quietly broken the entire safety check. Piping the output through a copying tool shows it on screen, but the shell then reports whether the copying succeeded rather than whether the checks passed, and copying always succeeds. Tested against deliberately failing runs, that version reported success every time. A failing commit would have been waved through.

3 approaches were measured on 3 things at once: whether the real pass or fail result survives, whether anything appears on screen before the end, and whether the collected text stays exactly the same, which matters because 6 later steps read it. Only 1 approach satisfied all 3, and that is the one now in place. On a real commit check a line of progress now appears roughly every 36 seconds.

## A third repair: the founder's own decision list now says what is already done

The founder reads a short list of pending decisions on his desktop. The full argument for each is kept in the repository. That split is itself his own earlier ruling: the full document ran to over 22,000 words and he said plainly that it was an impossible workload.

The problem was not that his copy is short. It was that each line said what a decision asks and never what the project's own records say about it. An item already built, tested and running looked exactly like an item waiting for a fresh decision. 10 of the 21 items waiting for him are already built, and 3 of 4 items a review panel had shown to rest on a false premise were among them. He was being asked to rule on questions that no longer existed.

Each line now carries a short clause where the records warrant it, saying that the premise is already dead or the work is already built, and that the decision is to confirm or close rather than to rule. 10 of 21 lines now carry it, at a cost of 576 characters, and nothing was cut.

## 3 defects found while trying to break the work

The safety check protecting against lost lessons refused its own first run, which is the correct way for it to fail, because adding a navigation link to the new companion file counts as a change to the set of links it is conserving.

A test harness that deliberately breaks the new code then revealed a gap in the tests rather than a weakness in itself. Breaking the branch that adds to an existing companion file left every test passing, because every test started from a clean slate and so only ever exercised the first write. In real use that branch runs on every save after the first.

The same harness found that nothing protected the founder's workload ruling: reverting his short decision list to the full document left all the tests passing, because they tested the formatting function directly and never the decision about which version actually reaches his desktop. That is now under test.

## The commit check refused all 3, and most of what it caught was this work's own

The safety check that runs before every commit took 44 minutes and then refused. It listed 18 failing checks against 5,131 that passed. That the list was readable at all is the second repair above working: the same refusal on earlier runs reached the log as 33 bytes with no reasons in it.

10 of the 18 were broken by the second repair itself, and the cause was not a flaw in the fix. It was a failure to ask, before changing a line of the commit script, what else in the project was reading that line. 5 separate checks were using it as a landmark: 1 to confirm the command's options had not changed, because 2 later text searches depend on the exact output format; 1 to confirm the cheap checks still run before the expensive ones; 1 that copies the line out, points it at a deliberately failing test, and confirms a failure still comes back as a failure; and 1 that rewrites the line into 5 broken forms and insists the previous check notices every one. 4 of the 5 were visible in the refusal text. The fifth was found only by searching the whole repository for the old wording, which is the sixth time in this project that counting the things to check has gone wrong where listing them would not have.

That fifth one could not have appeared in the refusal at all, because the file holding it is not on the list of checks the commit gate runs. Its failure took a form the gate does not report, so the count said 18 where the truth was 19. Run on its own it shows 1 failure against 31 passes. The gate's list covers 317 of the 946 test files in the project, so 629 of them are only ever reached by a full run, which takes far too long to sit in front of a commit.

The same look found something worse and more useful: the commit check had run none of this work's own 70 tests. All 4 of the new check files were missing from the gate's list. A measuring script written on 13 November exists for exactly this, against a rule that every check written since late October should be on the list, and it reported 4 of 245 missing, every one of them written that same day. The gap had been 33 of 220 a week earlier, so it had been closed down to precisely the files this work added. Nothing refuses a commit over that gap, and that is on purpose, because a check pinned to a number would have to be edited every time the number improved. The 4 files are on the list now, and their cost was measured before adding them: 70 tests in 65 seconds, about 2 and a half per cent of a run. Whether the gap should be enforced at all is a question for the founder rather than a repair, because enforcing it would move the decision about how long every future commit takes away from whoever writes the check.

A number of this work's own was also wrong, and a repository-wide consistency check found it. A confidence interval running from 0.060936 to 0.067066 had been printed beside a count of 1,566 out of 24,486 that it did not belong to. Rather than guess which half was at fault, the surrounding counts were searched: the interval was exactly right for a count taken when the file was 7 characters smaller. Both numbers were real and the pair was not. The neighbouring interval in the same sentence had been correct all along, which is the whole argument for recomputing a pair rather than reading it over and trusting it.

## What is left for the founder to decide

The permanent ceiling means a lesson drops out of the loaded window roughly every 31 days at the current rate of arrival. That is arithmetic. What is a judgement, and is not being made here, is whether that arrival rate of 5.6190 files a day should come down. 5 or 6 new lessons a day is enough that the index is now longer than can actually be used in a single session, and a shorter, more selective set might serve better than a complete one. That is a question about what the index is for, so it goes to him.

Written under CDSFL note standard v1.9 (1 November 2026).
