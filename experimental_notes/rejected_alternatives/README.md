# Rejected alternatives, preserved as diffs

An implementation that was considered and **not taken** is evidence about a decision. Deleting it leaves the decision recorded with only one side visible, and a later reader cannot see what was weighed.

## `falsifier_verify_worktree_allowlist_alternative_2026-08-30.diff`

The alternative fix for the worktree integrity guard, proposed by cc2 on the repair-loop panel of 2026-08-30 and **rejected**. It adds `_main_work_tree()`, resolving the canonical work tree via `git rev-parse --git-common-dir` and widening the allowlist of paths a model-authored falsifier may read.

**Why it was rejected, and what was done instead:** widening that allowlist enlarges what a model-written falsifier can reach. The conservative route was taken instead — `bench/falsifier_verify.py:385-412` resolves the canonical repository explicitly via `CDSFL_CANONICAL_REPO`, closing the same defect without widening anything. The defect it closes is real and was measured: 17 of 469 rejections where the guard's own test expects 2, which is 3.62%, Wilson [2.28%, 5.73%].

The diff is `repo → worktree`, so lines marked `+` are the rejected alternative's and lines marked `-` are what ships.

**Provenance.** Recovered 2026-09-05 from `/private/tmp/cdsfl_review_89557`, a review worktree the founder ruled should be tidied away ("Do the housekeeping. Tidy home = a tidy mind."). The worktree also held `bench/reference_runner_v2.py`, which needed no preservation: it is in git history across 112 commits and was renamed to v3 in `ce08914`.

Written under CDSFL note standard v1.7 (26 August 2026).
