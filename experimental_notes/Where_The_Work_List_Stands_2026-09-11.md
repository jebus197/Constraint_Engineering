# Where the work list stands

11 September 2026, 21:37 BST

Answering your question about progress and a completion estimate.

The short answer

Nothing on the list is waiting on me. Of 95 entries, 84 are complete, 4 are withdrawn, and the remaining 7 are all yours: 2 decisions, 4 items blocked on you, and 1 that is simply waiting for a date to pass.

The number of entries requiring work from me is zero, and has been since about a quarter past two this afternoon.

## Whether "complete" means complete

All 84 finished entries name the test files that establish them, 71 distinct files in total. Every one of those files sits inside the main test suite, and that suite ran green in a fresh copy of the repository four separate times today, at four different commits, with no failures. So the evidence behind those 84 entries is not merely present, it passes, and it passes in a clean copy rather than only on this machine.

A second check is still running as I write: independent readers going entry by entry, asking not whether each test passes but whether it actually tests what the entry claims. That is a stronger question and it is not finished yet. I will report it when it is.

## Why a completion date is the wrong shape of answer

The list is not a fixed target. 36 of its 95 entries, just under 38 percent, were created after it was first populated, because closing an entry keeps turning up defects that become entries. The 95 percent confidence range on that is 29 to 48 percent. Put another way, each nominal entry has implied about 1.6 entries of actual work.

So a burn-down estimate computed from the 21 to 44 entries a day I have been closing, and nothing else, would understate the remaining work by roughly that factor of 1.6, and quoting one would be exactly the kind of false confidence this project exists to catch.

What can honestly be said instead

Discovery of new entries is falling: 72 on the first day, which was the list being written rather than worked, then 16, then 7. Closure ran 19, then 44, then 21.

The tempting move is to fit a decay curve to that and give you a date. I will not, because it does not survive its own error bars: with two usable observations, the confidence range admits a process that does not decay at all. Two points cannot establish a rate.

What is measured, rather than projected, is that closure outpaces discovery by roughly three to one on the latest day. That is why the list converges. It is a fact about what happened, not a forecast, and there is now a test that will fail if it stops being true.

So, practically

If you rule on the 7 items that are yours, I can close whatever follows from them. Based on the measured rate, expect roughly 0.44 new entries to surface per entry closed, so the tail continues but shrinks.

Experiment 56 remains deferred by your own instruction until the rest of the list is complete, which in practice means until you have ruled.

Four of the 7 are one-word answers with a recommendation already attached. One, the prose-listing flag, is the only item the triage script classifies as genuinely blocking.

Written under CDSFL note standard v1.7, 26 August 2026.
