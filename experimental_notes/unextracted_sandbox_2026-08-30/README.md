# Unextracted sandbox work, recovered 2026-09-01

A git worktree at `/private/tmp/cdsfl_review_89557` (HEAD `657b02c`, 2026-08-30,
*"LATENT high-severity: the discrimination control wi..."*) was still registered
and still held **uncommitted work that exists nowhere else**:

- `test_repair_loop_wiring_2026-08-30.py` — **142 lines, absent from main entirely**
- `bench/falsifier_verify.py` — 43 lines not in main
- `bench/reference_runner_v2.py` — 131 lines not in main

Found while pruning worktrees after the 2026-09-01 sandboxed rehearsal. `/private/tmp`
is cleared on reboot, so this was one restart away from being lost.

**Nothing has been applied.** The founder's rule (2026-08-30) is that a sandbox is
deleted *after* its fixes are extracted, never before — so the content is preserved
here verbatim for review. `tracked_changes.patch` is `git diff` taken inside that
worktree; apply with `git apply` from the repo root if adopted.

**The worktree itself has been left in place**, unpruned, until the founder rules on
whether this work should be adopted, superseded, or discarded.

## Open question

Whether these changes were superseded by later work on the same files. Both files
were edited substantially between 2026-08-30 and 2026-09-01, so a straight apply may
conflict or may reintroduce something already fixed differently. That needs a read,
not an automatic merge.
