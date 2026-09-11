# Panel round 15: what two independent models found wrong with five repairs

11 September 2026, 12:42 BST (Europe/London)

*Plain-English companion to `Panel_Round15_FULL_RECORD_2026-09-11.md`, which carries both
models' replies verbatim. This version omits internal labels and file paths; the technical
record keeps them.*



## Why this round was called

A single defect had turned up 15 times in one working session. The shape is always the same: a checking tool understands one written form of what it is looking for, does not understand a second form that means exactly the same, and therefore reports that it found nothing. A report of nothing looks identical whether it means "there is nothing there" or "I could not see it". That is what makes this defect expensive.

Three of the five repairs under review were themselves tools built to catch that defect. A tool that carries the fault it exists to detect is the worst case of all, so the round was dispatched to two models to attack the repairs rather than to confirm them.

Both models ran on the existing subscription. No paid dispatch occurred. Each worked in its own private copy of the project, an arrangement adopted earlier the same day, so that neither could see or disturb the other's work.


## What they concluded

Both returned a split verdict, and on substantially the same grounds. Both agreed that two of the five repairs close the holes they name. Both found a third repair bypassable, and both picked out the same bypass as the sharpest finding of the round. Both found a fourth repair still broken, for the same reason.

Neither softened its disagreement to match the other, which is the point of running them without compelled agreement.


## The sharpest finding: a guard that switched itself off

Earlier that morning a test run in a throwaway copy of the project had overwritten a file the founder reads daily, replacing 34,082 bytes of current content with 27,669 bytes of an older version. A guard was written to prevent that.

The guard's first question was whether the folder it was about to write was the founder's own. If it was not, the guard concluded that a rehearsal was in progress and allowed the write without asking anything further.

That first question has a wrong answer under one common circumstance. When a command is run with elevated privileges, this operating system keeps the original user's home folder setting while changing the numeric identity of the user to the administrative one. The guard then looks up the administrative user's folder, finds it is not the folder it was about to write, concludes a rehearsal is in progress, and permits everything. Its two remaining checks are never reached.

So the guard disabled itself precisely on the most privileged kind of run there is. It failed in the permissive direction, which is the worse of the two: a throwaway copy gets through rather than the founder's own work being blocked. Both models found this independently.

Two further ways round it followed from the same design. A throwaway copy living somewhere other than the usual scratch area, in a home folder or on an external drive, satisfied neither remaining check and reproduced the original accident exactly. And when a certain environment setting is absent, the scratch area resolves to a different location, so a copy in the usual place escaped the check entirely.

The repair makes the decision depend only on values handed to it, rather than on whatever the surrounding environment happens to say. That change is what made the three failing cases reachable by a test at all. The rehearsal exemption now requires the target folder to have been moved into the scratch area rather than merely to be different. When the identity of the user cannot be established, the guard refuses rather than permits. And a small marker file now records which single copy of the project is allowed to write those files, so any second copy is turned away by name.

One limit remains and is written into a test rather than left for a reader to discover. If no marker file has been placed, a copy living outside the scratch area is still admitted.


## Counting is not the same as knowing the order

The project has a mechanism that lets a review record be stored without editing what a model actually said. Passages are marked off, and the writing checker leaves marked passages alone.

A check written the same morning compared how many opening marks there were with how many closing marks. Both models showed that comparison answers the wrong question. A closing mark that closes nothing, followed later by an opening mark that nothing closes, gives one of each. The two totals match while a passage is genuinely left open, and everything after it is genuinely exempted from checking, in silence.

Worse, a closing mark and an opening mark inside the same paragraph ended the exemption instead of restarting it, because the old method kept a single yes-or-no flag per paragraph and applied the closing one last no matter where it actually sat. The consequence is the opposite of the intended one: a model's quoted words were then checked as though they were the project's own writing, which is the exact outcome the exemption exists to prevent. Two opening marks in one paragraph were counted as one.

The repair reads the marks in the order they appear, and every part of the checker that needs an answer now reads that same one, so the exemption and the check can no longer disagree about what a mark means.


## What was done with the findings

Every finding was reproduced locally before anything was changed. That is a standing rule rather than a courtesy: a repair proposed by another model is a hypothesis until it has been run, exactly as one written locally is.

All eight defects were confirmed. None was refuted. One attack that the briefing itself invited was refuted: the suggestion that a structural warning attached to the first paragraph could be swallowed by a passage opening there. It cannot, because the warning is attached after the exempt passages are set aside rather than before.

Two findings were against work done only hours earlier and are worth naming plainly. A safety check written that morning failed in every throwaway copy made in the usual scratch area, which is exactly where the reproducibility harness makes its copies, so it had also been contaminating a separate record of intermittent failures sitting beside it. And a test written to prove a rule was asymmetric left a deliberately broken version alive: it covered three of the four cases in the table, and the missing one was the case the broken version changed.


## Two measurements, and they do not deserve the same confidence

Both models reproduced the round's two headline figures independently, and both made the same point about how to read them.

The first figure rests on 121 observations, and the range of uncertainty around it is about 8 percentage points wide. That is narrow enough to act on.

The second rests on 8 observations. Its range runs from roughly 14 percent to roughly 69 percent, which covers both "a rare intermittent fault" and "fails about half the time". Treating that as a settled rate rather than as a description of 8 runs would be an over-reading, and both models said so without being prompted twice.

A third defect was found in the review machinery itself. The harness that runs the project's tests in a throwaway copy reported which test had failed and nothing else. An intermittent fault reproduced during this round for the first time since extra diagnostic information had been added to it for exactly that purpose, and the harness discarded that information. It now keeps the full output and says where it put it.

Written under CDSFL note standard v1.7 (26 August 2026).
