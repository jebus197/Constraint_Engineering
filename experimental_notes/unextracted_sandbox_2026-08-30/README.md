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

---

## Status check, 2026-09-01 (later the same day)

**The worktree is still present** at `/private/tmp/cdsfl_review_89557`, still
registered, still unpruned. The founder ruling on adoption is still open, so it
has been left alone. It remains one reboot from being lost.

**`tracked_changes.patch` no longer applies.** Checked with `git apply --check`;
it fails on both files it touches:

- `bench/falsifier_verify.py` — the file moved on after the patch was taken.
  This is the "superseded by later work" case the open question above
  anticipated, and it is not caused by anything done on 2026-09-01.
- `bench/reference_runner_v2.py` — renamed to `bench/reference_runner_v3.py`
  on 2026-09-01, so the path in the patch header no longer resolves.

The patch is kept exactly as extracted. Rewriting its paths would make it look
applicable when it is not, and would edit a record of what a reviewer actually
produced. Adopting any of it now means reading the 43 and 131 line blocks
against current `falsifier_verify.py` and `reference_runner_v3.py` and applying
by hand — which is what the open question above already said was needed.

## The test file has been integrated; the copy here stays frozen

`test_repair_loop_wiring_2026-08-30.py` sat in this directory, outside the test
suite, for two days. Seven of its eight test names appeared nowhere under
`bench/tests/`. It was integrated on 2026-09-01 as
`bench/tests/test_repair_loop_wiring_2026-08-30.py`, where it runs and passes.

The copy here is unchanged and still imports `reference_runner_v2`, which is
what the module was called when the reviewer wrote it. It is allowlisted in
`bench/tests/test_every_test_file_is_collected_2026-09-01.py` with that reason.

One assertion differs between the copies. As drafted it asserted module aliases
`rr.FE_FIX_INEFFECTIVE` and `rr.FE_FEEDBACK_LINE`, which belonged to the
reviewer's own draft of the fix-efficacy wiring. The implementation that was
adopted consults `fix_efficacy_decision()` and imports the probe lazily at the
call site, so neither alias exists in this tree and neither ever did. The live
copy asserts the property instead: that the runner reaches the probe, and that
the model is told in those words that its fix does not cure its own falsifier.

**Still open, unchanged:** whether the 43 lines in `falsifier_verify.py` and the
131 lines in the runner should be adopted, superseded, or discarded.

---

## The open question is now answered: both halves are SUPERSEDED

Assessed 2026-09-01 by reading the diff against current code rather than by
attempting to apply it. The diff is **100 insertions / 4 deletions** in the
runner and **43 insertions** in `falsifier_verify.py` — the README's earlier
"131 lines" was the raw line count, not the diff.

**The runner half — superseded by the implementation that was adopted.** The
uncommitted work is the reviewer's own draft of the fix-efficacy wiring: module
aliases `FE_FIX_INEFFECTIVE` / `FE_FEEDBACK_LINE`, a
`FIX_EFFICACY_PER_ROUND_LIMIT` of 5, and the probe called inline from the status
pass. What is in `reference_runner_v3.py` today is the same feature refactored:
`fix_efficacy_decision()` plus a lazy `from fix_efficacy import probe` at the
call site, with the same per-round limit.

The evidence is the reviewer's own tests. All eight of its commissioning tests
now run in the suite as
`bench/tests/test_repair_loop_wiring_2026-08-30.py` and pass against the adopted
code — including the two that matter most here, that an ineffective fix reaches
the model and that the probe is contributory and cannot gate anything. A draft
whose author's own tests pass against the replacement is superseded, not lost.

The single exception is the one assertion that named the aliases rather than the
behaviour. It was restated on integration; the aliases themselves are the only
thing in these 100 lines that does not exist in the tree, and nothing depends on
them.

**The `falsifier_verify.py` half — superseded by the founder's own ruling.** The
43 lines add `_main_work_tree()`, which resolves `--git-common-dir` so a run
inside a linked worktree stops raising `INTEGRITY_VIOLATION` against the
canonical tree. That is a real problem, and it was solved differently: the
founder ruled for Option B on 2026-08-30, where the panel's cwd stays the
disposable worktree and `CDSFL_CANONICAL_REPO` names the canonical one. That
ruling is live — `bench/falsifier_verify.py` reads the variable at
`_allow_roots`, and `bench/confer_panel_2026-08-28.py` sets it before dispatch.

Adopting `_main_work_tree()` now would give the same widening a second,
independent route, which is the opposite of what a confinement control wants.

**Recommendation: discard, and prune the worktree.** Neither half carries
anything the tree lacks. The worktree at `/private/tmp/cdsfl_review_89557` has
not been pruned here, because deleting it is the founder's call and it is the
only copy.
