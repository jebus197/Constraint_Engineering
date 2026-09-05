# For a founder ruling — the integrity guard rejects honest falsifiers when run from a worktree

> **[CORRECTION 2026-09-05 — THIS RULING IS SPENT. NO FOUNDER ACTION IS REQUIRED.]**
> This file asks for a ruling on whether to widen a path allowlist so that
> archived falsifiers naming the canonical tree by absolute path stop being
> rejected. The underlying defect WAS closed, by a different and more
> conservative route than the one proposed here: `bench/falsifier_verify.py:385-412`
> resolves the canonical repository explicitly (`CDSFL_CANONICAL_REPO`) instead of
> widening what a model-authored falsifier may read. Its own comment records the
> measurement — 17 of 469 rejections where the guard's test expects 2, which is
> 3.62%, Wilson [2.28%, 5.73%]. So the allowlist was never widened and the
> question this file poses no longer arises. Retained, not deleted, per the
> project's dated-correction convention; the original text follows unaltered.


**Found by cc2 on the repair-loop panel, 2026-08-30. Diagnosis verified here. The fix is NOT applied,
because it widens a security allowlist.**

## The defect

`bench/falsifier_verify.py:184`:

```python
REPO_ROOT = Path(__file__).resolve().parent.parent
```

In a git worktree that names **the worktree**, not the canonical tree. `_allow_roots` therefore omits the
canonical tree, and any archived falsifier that names it by absolute path is rejected as
`INTEGRITY_VIOLATION` — which routes the finding to a human and **never to CONFIRMED**.

**cc2's measurement:** `test_falsifier_cannot_read_the_key.py::test_the_guard_rejects_nothing_else_in_the_whole_tracked_archive`
expects exactly **2** rejections across 560 archived falsifiers. Run from a worktree it rejects **17**.

That test's own docstring anticipates this: *"If a future rule change makes this fail, the rule is blocking
honest work."*

**It passes in the canonical tree**, verified here, so no experiment has been affected — experiments run in
the canonical tree. It bites only where panels run, which is worktrees, which is every confer dispatch
including the three run this week.

## cc2's proposed fix, and why CC1 has not applied it

Add a cached `_main_work_tree()` reading `git rev-parse --git-common-dir`, append its parent to
`_allow_roots`, and fall back to `REPO_ROOT` on any failure — so the failure direction is "no extra root",
which is the status quo and never a widening.

cc2 attacked its own widening and reported:

| probe falsifier | verdict |
|---|---|
| reads the off-repo key store by literal path | `INTEGRITY_VIOLATION` |
| reconstructs the key path via `Path.home()` | `INTEGRITY_VIOLATION` |
| walks `~/Desktop` for ground truth | `INTEGRITY_VIOLATION` |
| honest falsifier naming the canonical tree by absolute path | **`REFUTED`** — ran clean |

**Why it is not applied tonight.** It widens the allowlist of paths a model-authored falsifier may read.
That is the guard closed after exp48 — the one run this project had to exclude, because a model wrote a
falsifier that opened the scoring key. cc2 tested three exfiltration routes and says plainly it did not test
all of them, naming `GIT_DIR` and `GIT_WORK_TREE` as unchecked. Widening that guard on three probes, at
half past two, with no second reviewer having seen the change, is not a call CC1 should make.

**The conservative alternative, which needs no widening:** dispatch reviewers with `PYTHONPATH` and
`repo_root` pointing at the canonical tree while the *cwd* stays the worktree. That keeps the sandbox for
writes and removes the false rejections, without adding any readable root. CC1 has not implemented this
either — it is a change to how panels are dispatched and belongs in the same ruling.

## Measured consequence of leaving it

cc2 re-ran the 313-finding fix-efficacy sweep with its fixes in place: **5 findings moved from
`NO_BASELINE` to `NOT_INTERCEPTED`** — a wrong diagnosis replaced by a right one — and **not one verdict
changed. 51.4% before and after.** So the headline measurement is robust to this defect either way.
