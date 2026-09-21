# The fix score was answering a different question from the one it was asked

20 September 2026 23:58 BST (Europe/London)

## The short version

S_k, which decides whether a proposed fix is any good, has been answering "did this fix break anything?" when the mathematical model asks it "did this fix work?". Those are different questions, and for a fix that does nothing at all they give opposite answers. A fix that changes nothing breaks nothing, so it scored perfectly.

The instrument that answers the real question already existed in the project and was already running on every eligible finding. It simply was not connected to S_k. It is connected now.

## How the two questions came apart

The appendix defines sigma as whether a proposed fix actually resolves the flaw that was detected, and it is strict about how sigma may be obtained: something must be run before the fix and again after it, and the 2 results compared. The runner's S_k fills that sigma slot in the risk equation, matching the appendix line for line.

But the 3 pieces of evidence feeding that score all ask about harm. Does the existing test suite still pass. Did the fix add new lint complaints. Did it add new security warnings. A fix can leave every one of those untouched and still not have fixed anything.

## What that looks like when you run it

4 fixes were put through the scorer. One genuinely repaired the bug. One left the bug alone and only tidied an unrelated function. One replaced division with multiplication, so every answer it returns is silently wrong. One gutted the function so it returns nothing at all.

All 4 scored exactly 1.0 and all 4 were admitted.

Adding a real test suite helps with 2 of them. The corrupting fix and the gutted one drop to 0.7333, because the suite catches them, though both are still admitted. The do-nothing fix and the real repair stay identical at 1.0, because breaking nothing is precisely what a do-nothing fix does.

## The same pattern across the archive

The project has 135 archived findings where both the fix score and a separate measurement of whether the fix actually worked were recorded. Comparing the 2:

104 fixes that did cure the problem averaged 0.950140. 31 fixes that did not cure it averaged 0.950206. The failing ones scored fractionally higher, and the middle value of each group was identical at 0.978200.

4 statistical tests were run, of 3 different kinds, and none of them could tell the 2 groups apart. Every one of the 31 fixes known not to work was admitted.

This is the underlying reason 7 independent reviewers, working without sight of each other, all reported that roughly 3 quarters of archived fixes score a perfect 1.0. That pile at the top is not a broken measurement. It is an accurate measurement of harm being read as a measurement of repair.

## Two further things the measurement turned up

The security check carries double weight, the heaviest of the 3, and returned the identical result on all 902 archived decisions: nothing found, nothing added. It is not faulty. Fed a fix that opens a shell injection it correctly drops to 0.5, and fed one that also adds an unsafe evaluation it drops to 0.3. It simply never had anything to catch, while occupying 40% of the score.

A check that always returns its best value at double weight is not a gate, it is a constant being added in. That puts a hard floor under the score: no fix, however bad, can score below 0.4 while the syntax checks pass. Both symbolic algebra and a constraint solver confirm the floor independently. Of the 2 candidate cut-offs that 4 rounds of panel review argued over, one sits below that floor and could therefore never have rejected anything at all, whatever fixes had been fed to it.

The same floor squeezes the part of the risk model that tracks new problems introduced by fixing old ones. That quantity has a designed span; the floor confines it to 60% of it, and the archive only ever used 26%.

## The repair

No new machinery was built. The existing probe takes a proposed fix, applies it to a disposable copy, and re-runs the finding's own test against that copy. That is exactly the before-and-after comparison the appendix demands. It was deliberately advisory, and the only thing it fed was a line of feedback to the model that wrote the fix.

It is now a 4th piece of evidence in the score, weighted the same as the heaviest existing one rather than higher, because the argument for giving it more is a matter of judgement and judgement is not evidence.

Only the 2 outcomes the probe itself calls verdicts are read as scores. The 5 outcomes that mean "the instrument could not look" are treated as no reading at all, and the score is computed from the remaining evidence. Reading them as zero would punish a fix for the instrument's silence, and would inflate the model's estimate of newly introduced risk. The project already has this rule for a different tool and it applies unchanged here.

## What changes

On the same 135 archived findings, the gap between fixes that worked and fixes that did not goes from effectively zero to 0.285672, and all 3 statistical tests move from unable to distinguish the groups to overwhelmingly able to. The efficacy figure handed to the risk equation for a fix known not to work drops from 0.9502 to 0.6787.

Those 31 fixes are still admitted. The gate informs S_k, it does not veto. Whether a fix that demonstrably fails its own test should be admitted at all is a separate decision, and it belongs to the founder.

## Two smaller faults found on the way

The message a model receives when its fix is rejected promised to name the check that failed, and could never do it. It tested each record against the number zero, but every record is a small structure rather than a number, so the test never matched and the message always fell back to a generic line. Meanwhile the record itself held the precise reason, in one case an unclosed bracket at a named line, and the model was shown none of it.

Separately, one of the project's own guards found a genuine problem and then crashed while describing it, because it was built to report 7 pieces of information and written to read 5. It had passed for as long as it found nothing. Both are fixed, and the 6 stale line references it had correctly identified were repaired.

## Status

Built, tested and committed. 13 tests, 12 of which fail against the previous code. Not yet exercised on a live experimental run; that comes next.

Written under CDSFL note standard v1.7 (26 August 2026).
