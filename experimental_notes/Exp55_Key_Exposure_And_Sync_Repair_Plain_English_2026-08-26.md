# Experiment 55's answers were on the public repository three days before it ran

2026-08-26, 00:34 BST (UTC+1)

## The short version

The rule that has been stopping this project from publishing its work named the wrong file.

That rule sits as item 2 of the operational tracker's five things that must not be got wrong, and it reads: *never push this branch*. Its stated reason was that Experiment 55's scorer key was tracked in the repository, so pushing would publish it. The key was indeed tracked. But a second file sitting beside it, the ground truth file for the same control target, states the same two defects in the same terms, and that file was committed to the **public main branch on 20 August 2026 at 01:21 BST**. The target document itself is public too. Both Experiment 55 runs started on 23 August. The answers were public three days before the experiment ran.

The key was split out of the target document on 23 August, and that split was correct and necessary: it removed the answers from the file the runner reads whole and places in the panel prompt, which is the exposure that cost Experiments 48 and 49 their place in every headline figure. It was simply not sufficient, and nothing in the record said so.

The consequence is that the Experiment 55 target is spent. A re-run needs a new target.

## What the public file actually contains

It names both defects by identifier and by type. **CT-01** is described as a reasoning defect with a true conclusion: the Nyquist criterion is misquoted, and the correct form requires the sampling rate to exceed *twice* the maximum frequency rather than merely exceed the maximum frequency. **CT-02** is described as an inference defect with a true premise: a frequency resolution of 1.5625 Hz is computed correctly, and the conclusion that this resolves features 1 Hz apart does not follow from it.

The scorer key that the *never push* rule was protecting says the same two things at greater length. It adds the worked arithmetic — that the real threshold is 360 Hz and the document's 400 Hz exceeds it, so CT-01's conclusion happens to hold while its justification does not. It names no defect the public file does not already name.

Two further fields go beyond the answers. One states which single edit would appear to cure both defects at once. The other names the disagreement between two panel models that the control was built to settle. Those describe the experiment's design and what a particular result would prove, which is more than a bare answer key gives away.

## How this was established

Four checks, each repeatable from the repository root.

1. Asking git whether the ground truth file exists on the public branch returns success, so it is reachable from main and not merely from a local branch.
2. The commit that added it is dated 2026-08-20 01:21:53 BST.
3. That commit is confirmed as an ancestor of the public branch, which distinguishes genuinely published from merely committed locally.
4. The two Experiment 55 log directories carry timestamps in their names showing runs beginning 23 August at 14:46 and 15:39.

## Neither run reached round 1

Both directories hold 18 files. The highest round artefact in either is round 0. Neither contains a final report. So Experiment 55 produced no result to protect, and a re-run was needed on those grounds alone, quite apart from the exposure.

## What a model saw without opening anything

The round 0 record from CC2 in the first run contains two statements worth separating.

The first is CC2 stating, unprompted, that it did not open either the key or the ground truth file, because this is a blind review and reading the key would void the comparison. That is a model's own claim about its own conduct. It is recorded as *no evidence of access*, not as evidence of abstention, following the standing rule never to accept a model's word about its own behaviour.

The second statement is the more useful one, because it required no access at all. CC2 observed that the presence of a file named ground truth implies a scored expected-defect set exists, and that any edit must be weighed against it. A model reading nothing but the directory listing inferred the shape of the scoring. That is the same inference class already catalogued for Experiments 48, 49 and 50, where the number of planted items equalled the number of sections minus one, so the design was inferable without touching a key at all.

## What has been changed

Both files now live in a folder called `CDSFL_experiment_keys`, sitting alongside the repository rather than inside it, outside any git tree. That folder carries a README recording why the target is spent, so a future reader who finds the key does not assume the target is still usable.

The repository's ignore rules now refuse any file matching `*_KEY.md`, `*_GROUND_TRUTH.json` or `*_ANSWER_KEY*`. That stops the class recurring by accident rather than by vigilance.

No Python file anywhere in the repository references either path — checked rather than assumed — so removing them breaks nothing.

Item 2 of the operational tracker has been rewritten from *never push this branch* into a statement of what is actually true.

## What has not been changed, and needs a ruling

History was not rewritten. The key remains reachable in the commit that introduced it on the working branch, and the ground truth remains reachable on main, where it is already published.

Removing the key from the branch's history was attempted and refused by this environment's command guard, which treats history rewriting as destructive. That refusal is reasonable, and the decision belongs to the founder in any case, because the rewrite is not free: **18 of the branch's 59 commits are cited by their hash** in the project's markdown, most of them in the current-state document. Rewriting changes every one of those hashes. They can be remapped mechanically from the rewrite's own record of old hash to new hash, but that is work and it needs verifying rather than assuming.

The weight of the decision depends on where the work is meant to land. Pushing the working branch as a branch leaves the key reachable only from a side branch. Merging it into main makes the key reachable from the **public default branch**. The second is materially worse even though the information it holds is already public, because a file named `SCORER KEY` in the default branch's history is a different statement about how this project operates than the same facts sitting in a file named ground truth.

## Why the repository has not been in sync

The founder's question was why a push does not leave local and remote fully in sync, since that is the point of the entire exercise.

The save routine pushes whatever branch happens to be checked out. It then reported the outcome as two lines: the state of the remote *before* the save, and a yes/no for whether a push happened. Neither is the state *after* the save. A push that pushed a branch nobody reads produced exactly the same two lines as a push that put the work where the public could see it.

The routine now measures again after pushing. Run against the current tree it reports that the working branch does not exist on the remote at all, that this is a **failed measurement rather than evidence the push worked**, and that public main is 58 commits behind. It adds that pushing the working branch does not update main, and that anyone reading the public repository sees main and not this branch.

That is the answer. Nothing was failing in the push itself. The branch had never been pushed at all, and even a successful push would have left the public repository stale while reporting success. The same mechanism left main 16 days stale in August 2026, which the save routine's own source comments already record.

A divergence that cannot be measured is now reported as unmeasurable and rendered as NOT VERIFIED — never as zero, and never as *in sync*. A failed check that reads as a pass is the defect class this project keeps rediscovering.

Nine tests hold this in place, run against a real bare git remote rather than a mock. They cover the synced case, the ahead case, the never-pushed case and the side-branch gap, and they assert that those verdicts differ from one another, which is the property that matters. Three deliberate breaks — forcing the in-sync answer true, reporting the never-pushed case as zero divergence, and dropping the main-gap measurement — fail 1, 3 and 1 tests respectively.

## A claim withdrawn

On 25 August this assistant wrote, both in a test file and in a note on the founder's desk, that supersession across documents is not mechanically detectable and is not attempted, and that the defect found on 24 August would still not be caught. The founder asked whether that was certain.

It was too strong. Supersession *in general* is not detectable. The defect in question was not general. The runway document asserted a hold and **named** the file holding the decisions, and that named file had carried the heading *founder rulings* for two days. Both halves are machine-readable, so the pair is detectable.

A checker now detects that pair, and fires on the real historical file recovered from the commit before the correction. Its first version also fired on the onboarding document at line 514, which is a genuine hold naming a genuine file, recorded inside a dated entry from 22 April with four months of later entries beneath it. A record of what was pending in April is not a claim that it is pending now. Rather than exclude that document, which would have silenced the check, the tool follows the document's own convention: a hold counts as live only inside the newest dated entry, or inside no entry at all, which is where the runway's banner sits.

It is commissioned rather than asserted: one known-bad fixture, three known-good ones, plus the real historical file. Three deliberate breaks fail 5, 5 and 3 tests. The residual limit, stated narrowly this time: a hold that names no file, or that paraphrases the decision list instead of pointing at it, remains invisible.

## Test state

The full suite at 00:30 BST on 26 August returns **3878 passed, 1 failed, 35 skipped, in 255 seconds**.

The single failure is a guard reporting correctly rather than a fault. Editing the operational tracker left its Desktop copy behind, and the drift guard added on 25 August detected it. That copy cannot be refreshed from this process: overwriting an existing file on the Desktop is refused by this environment, measured 6 times out of 6 on 25 August, while creating a new file there succeeds. The repository copy is canonical by the founder's ruling of 6 August, so the canonical copy is correct and the convenience copy is stale. Refreshing it needs a single copy command run by the founder.

## Recommendation

One path, not a menu. Remove the key from the working branch's history, remap the 18 hash citations from the rewrite's own record and verify every one still resolves, then merge the branch into main and push. That leaves the public repository current, the project's full commit history intact, and no file named as a scorer key anywhere in the default branch. It needs the founder to permit the history rewrite, because this environment refuses it.

Experiment 55 needs a new target regardless of that decision.

Written under CDSFL note standard v1.6 (24 August 2026).
