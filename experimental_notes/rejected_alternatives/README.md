# Rejected alternatives, preserved as diffs

An implementation that was considered and **not taken** is evidence about a decision. Deleting it leaves the decision recorded with only one side visible, and a later reader cannot see what was weighed.

## `falsifier_verify_worktree_allowlist_alternative_2026-08-30.diff`

The alternative fix for the worktree integrity guard, proposed by cc2 on the repair-loop panel of 2026-08-30 and **rejected**. It adds `_main_work_tree()`, resolving the canonical work tree via `git rev-parse --git-common-dir` and widening the allowlist of paths a model-authored falsifier may read.

**Why it was rejected, and what was done instead:** widening that allowlist enlarges what a model-written falsifier can reach. The conservative route was taken instead — `bench/falsifier_verify.py:385-412` resolves the canonical repository explicitly via `CDSFL_CANONICAL_REPO`, closing the same defect without widening anything. The defect it closes is real and was measured: 17 of 469 rejections where the guard's own test expects 2, which is 3.62%, Wilson [2.28%, 5.73%].

The diff is `repo → worktree`, so lines marked `+` are the rejected alternative's and lines marked `-` are what ships.

**Provenance.** Recovered 2026-09-05 from `/private/tmp/cdsfl_review_89557`, a review worktree the founder ruled should be tidied away ("Do the housekeeping. Tidy home = a tidy mind."). The worktree also held `bench/reference_runner_v2.py`, which needed no preservation: it is in git history across 112 commits and was renamed to v3 in `ce08914`.

Written under CDSFL note standard v1.7 (26 August 2026).

---

**FIGURE PROVENANCE, added 2026-09-10T20:55:54+01:00 under task 7.1.** **No artefact in `bench/logs` corresponds to this file**, and no committed script reproduces its figures. They are therefore **not reproducible from this repository** and must not be quoted as measurements. This is recorded rather than repaired: inventing a source would be worse than naming its absence. The file is kept intact as the record of what was written at the time.

**A NOTE ON HOW THIS BLOCK REACHED THE WRONG FILE FIRST.** The repair script matched notes by BASENAME across the whole tree, and `experimental_notes` holds 4 files called `README.md`. The block landed on `unextracted_sandbox_2026-08-30/README.md`, which carries 0 figures and 3 live scripts and needed nothing, while this file — the one the measurement had actually flagged — was left untouched. Caught immediately because the instrument still reported 1 outstanding. Matching a path by its last component is the same shape as matching a token by substring, which this project has now been bitten by 5 times.
