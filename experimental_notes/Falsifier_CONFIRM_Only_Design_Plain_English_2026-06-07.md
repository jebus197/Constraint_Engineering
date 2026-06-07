# The Clean No-Faking Falsifier Gate (Plain English)

**2026-06-07 12:19 BST**

> **Correction added 12:50 BST.** The section below ("So does this finally get Experiment 42 over the line?") concluded that seven findings were irreducible exceptions a human had to rule on. That was tested afterwards and proved wrong. A capable investigator, given each of the seven, wrote and ran a correct test for every one — all seven are real defects that confirm cleanly, none genuinely resists testing. Two were simply the same defect already confirmed under another name; the other five were cases where a weak model wrote a broken test or no test at all. The human workload for these seven is zero. The earlier retry failed only because it kept asking the same weak models that had already failed; routing the test-writing to a capable model resolves them. The genuine cases where a human is irreducible are real, but they live in other kinds of code (timing/concurrency, safety, authority calls), not in these seven.

## The problem, recapped

The runner judges a claimed defect by running a little test the model wrote. A test that *raises an error* demonstrates the defect (a confirmation); a test that *exits cleanly* fails to demonstrate it (a refutation). An audit of Experiment 42 found these two outcomes are not equally trustworthy: every confirmation was correct, but a third of the refutations were wrong — real defects that a broken test waved through because the test exited cleanly for the wrong reason. A clean exit is cheap; a broken test produces one just as easily as a genuine non-defect does.

## The fix that was tried first, and failed

The obvious patch was to double-check a suspect refutation by having a second, stronger model write its own test. Tested directly — and it failed. The strong model fell into the same traps and also refuted the two real defects. A single test, however capable its author, is not a reliable check. So that idea was dropped rather than shipped.

## The design that replaced it

Stop trusting refutations on critical findings at all. A critical defect is now resolved *only* by a confirmation — the one verdict that can't be faked, because it requires the test to actively demonstrate the bug. A critical that a model fails to confirm is not dropped; it is escalated to the human. Refutations are still trusted for non-critical findings, where masking a defect doesn't matter. This removes the single place where a real critical defect could be silently faked away. The change is small, gated so unrelated experiments are untouched, and the full test suite passes.

When a critical isn't confirmed on the first try, the model gets up to three attempts, each time shown what its previous test actually did, and asked to test honestly — not pushed to confirm, which would just trade one kind of faking for another. Still unconfirmed after three tries, it goes to the human.

## What happened when this was run on the 15 stuck findings

Eight of the fifteen resolved to a genuine, demonstrated defect. Seven went to the human as honest exceptions — including two that are definitely real bugs the models simply cannot write a correct test for, and five that stayed unproven after three attempts. None were faked in either direction, and both directions were checked.

The check that mattered most was a finding the retry flipped to "confirmed" that the earlier audit had called a non-defect. On its face that looked like rigging. Verified by hand against the real code: it is a real defect after all — the function that detects hard constraint directives also fires on the mere word "hard" sitting inside a code comment, which is the same over-classification bug the audit had already confirmed in two sibling findings. The earlier audit was right only about the narrow case the code happens to handle; the retry found a real case it doesn't. The punchline: the *old* gate had been wrongly refuting this finding, which would have buried a real defect. The new gate caught it. The clean runner is not just safer in theory; it recovered a bug the old one was hiding.

## So does this finally get Experiment 42 over the line?

It gets it *to* the line honestly, and the human steps it over. Convergence needs two things: no unresolved critical defects left hanging, and the panel running quiet for three rounds with nothing new. Resolving the stuck findings handles the confirmable ones but leaves seven escalated to the human, and those seven still count as unresolved until the human rules on them. The panel going quiet is a separate matter — it was nearly there, dropping from fifteen new findings in the first round to one in the last, but never quite zero.

So the system cannot declare victory entirely on its own — and that is the honest floor, not a failure. Those seven are real, un-auto-confirmable critical findings; letting a clean exit clear them is exactly the masking just eliminated. They are the irreducible cases where a human has to look. The path is clear: the human rules on the seven, the panel quiets over a few more rounds, and Experiment 42 converges for real. No version of this converges fully by itself without faking — and faking was the one outcome ruled out from the start.

This is not another moving goalpost. It is the clean runner doing its job: confirm what can be demonstrated, refuse to fake what cannot, and hand over exactly the residue that genuinely needs a human.

---
*Written under CDSFL note standard v1.2 (14 May 2026). Technical: `Falsifier_CONFIRM_Only_Design_2026-06-07.md`. TTS: `~/Desktop/CDSFL_tts/Falsifier_CONFIRM_Only_Design_2026-06-07.txt`.*
