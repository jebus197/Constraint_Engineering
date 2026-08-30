# Six Decisions. Two Of Them Block The Next Run.

2026-08-30, 22:41 BST (UTC+1)

This replaces every earlier request from today. Nothing else needs reading. Two decisions block the next simulated run, two are actions only you can perform, and two are wanted but block nothing.


## DECISION 1. THE REVIEW SANDBOX REJECTS HONEST WORK. TWO WAYS TO FIX IT.

What happens. When a reviewing model is given its own private copy of the project to work in, a safety check inside that copy wrongly concludes that archived proof-programs are trying to read files outside the project. It refuses them. The refusal sends the finding to a human instead of ever letting it be confirmed.

The scale. Across 469 archived proof-programs, the check should refuse exactly 2. Run from a private copy it refuses 17. That is 3.62 percent against an expected 0.43 percent, 95 percent confidence interval [2.28, 5.73], and the interval does not contain the expected rate, so this is not noise.

Why it matters to you now. It is the reason a reviewer reported the test suite as failing when it passes here. Experiments are unaffected, because they run in the main copy. It bites only where reviews run, which is every review this week.

Correction to something I told you earlier: I said fixing this meant rewriting 311 file paths inside the archive, which your rules forbid. That was wrong. It is a single line of code that mistakes the private copy for the main one. This was already found and written up this morning; I presented it as new, which it was not.

Option A. Change the safety check so it also recognises the main project folder. The reviewing model attacked this fix three ways and could not get through it, but it explicitly said it had not tested every route. This widens a safety boundary that was closed after the one experiment this project had to throw away, because a model wrote a proof-program that opened the scoring key.

Option B. Leave the safety boundary exactly as it is. Instead, tell the reviewer where the main project folder is when it is dispatched, while still confining everything it writes to its private copy. This removes the false refusals and widens nothing.

My recommendation is B. It fixes the same problem without touching a boundary that exists because of a real incident.


## DECISION 2. A CHECK THAT CAN UNDO A CORRECT RESULT, ON A PREMISE THAT IS A COIN TOSS.

What it does. There is a check that asks whether a proof-program fires because of the actual defect, or whether it would fire regardless. To do that it needs two things from the panel: the proof-program, and a corrected version of the file. It has never once had both, so it has never run in this project's life.

What I changed today. A setting that was supposed to ask the panel for that corrected version was written nine days ago and connected to nothing. I connected it. That part is right and stays.

The problem I then found. When the check decides a proof-program has failed to discriminate, it marks the finding as not confirmed, and that step is not optional. There is a separate switch that everyone assumed governs it, and that switch governs a different piece of code. So the undo happens regardless of the switch.

The premise it rests on is stated in the code: a finding's own proposed fix corrects that finding's own claim by construction. Measured across 246 archived findings, 126 of the proposed fixes do not silence their own proof-program. That is 51.2 percent, 95 percent confidence interval [45.0, 57.4], statistically indistinguishable from a coin toss. The code assumes it never happens.

So connecting the ask would have handed this check its missing input for the first time, and it would then have marked sound findings as unconfirmed roughly half the time it fired.

I have turned the ask back off for the simulated run. The connection itself is left in place.

Option A. Put the undo behind the switch everyone already believes governs it. The check still runs and still records what it finds, but it cannot silently reverse a result until you say so. This is the smaller change.

Option B. Leave the undo unconditional and keep the ask switched off until the underlying assumption is fixed properly. This changes no code today.

My recommendation is A. It makes the switch mean what its name says, which is also what both reviewing models assumed it already meant.


## Two Actions Only You Can Perform

The push. There are 173 commits sitting locally and nothing on the server. You ruled that this goes last. Everything is ready. The scan that looks for personal information before publishing now runs every time, after it found 21 occurrences earlier today.

The key files. 31 files holding scoring keys are still stored as plain text. Encrypting them needs a passphrase that should exist only in your head and your password manager. The three commands are already on your desk from 28 August. This has been open since then.


## Two Things I Would Like, Which Block Nothing

Fable's settings. Fable is the sixth panel member and has never had a settings file of its own, so it has been running with no per-model briefing at all. I created one today using the values from its closest sibling model, and marked clearly inside the file that they are inherited rather than measured. Confirm that is acceptable, or give me the real numbers.

The Bench Run 2 target list. Does it include any prose or markdown documents that print code listings inside them? If it does not, a piece of repair work I did today is already sufficient and needs no further attention. If it does, there is one more transport issue worth closing first.


## What Is Not In This Document

There is an older backlog of open rulings from 4 and 16 August, on description truncation and on 120 discarded similarity pairs. They are recorded in the operational plan and they do not block the next simulated run. I have deliberately not imported them here, because you asked not to be overwhelmed. Say the word and I will produce the same treatment for those separately.


## The State Of The Work

The test suite reports 4549 passed, 0 failed and 0 skipped. Skipped tests went from 34 at the start of the day to 0. All 37 agreed actions from today are closed. Three model reviews were run; the third broke two things I had built hours earlier, and both are now repaired and tested at the enforcement level rather than only at the policy level.

Answer decisions 1 and 2 and the simulated run can start.


Written under CDSFL note standard v1.7 (26 August 2026).