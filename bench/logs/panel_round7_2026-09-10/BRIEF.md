# PANEL BRIEF — round 7: check this work, and DELIVER YOUR FIX AS A FILE

<!-- figure: gamma at 13 passes | scripts/ffafp_cycle_gamma_2026-09-10.py | 0.294998 -->

## SECTION 0 — READ THIS BEFORE ANYTHING ELSE. THE DELIVERY RULE HAS CHANGED.

**Founder ruling, verbatim, 2026-09-10:** *"its fine to find problems, but you must also provide (tool verified) fixes in all cases"* and *"they need to supply fixes, not just problems!"*

**A finding without a fix is not a deliverable this round. A fix described in prose is not delivered either.** Measured across panel rounds 5 and 6, in which the assistant made no concurrent edits: the seats handed back **0 source files**. Both rounds returned excellent prose and executed probes, and the code evaporated. The cause is mechanical, not yours — `bench/panel_sandbox.py:teardown` destroys the sandbox, and `changes()` only preserves files that are still **inside the sandbox repository tree** when you finish.

**So: write your fix INTO the sandbox repository tree, at the path it would live at, and leave it there.** Not `/tmp`. Not a scratch directory. If you modify an existing file, edit it in place in the sandbox. If you add a test, put it at `bench/tests/<name>.py`. Everything you leave in the tree is returned to the assistant as a patch, tested, and either applied or refused with a reason. Anything outside it is destroyed.

You may write freely inside the sandbox. It is a copy. The canonical tree is fingerprinted before and after and you cannot reach it.

## SECTION 1 — What to check

Three changes landed in the last 40 minutes, all responses to findings you made in round 6.

1. **`scripts/panel_brief_validate.py` — `check_declared_figures` hardened.** You both found it matched by substring, so a declared `0.29` reproduced against a printed `0.294998`. It now requires a whole token, delimited by anything that is not a digit, letter, dot or minus. fable's residual — that a bare `1` or `9` is a genuine token in almost any output — is closed by requiring at least 3 significant characters. Over 8 cases it now scores **8 of 8**, Wilson [67.5592%, 100.0000%], where the substring form scored **4 of 7**, Wilson [25.0458%, 84.1780%]. **And this very sentence was caught by `scripts/wilson_interval_consistency.py` before dispatch** — its first draft put the two counts side by side with only the LATTER count's interval after them, so the interval belonging to the 8-case score sat against the 7-case score. A correct interval under the wrong count, in a brief about a guard that refuses wrong numbers. Attack that too. **The check order was wrong on the first attempt and took 2 existing tests red**: the distinctiveness rule ran before the script-exists rule, so a declared figure against a missing script reported the wrong reason. Infrastructure failures now report first.

2. **`bench/tests/test_precommit_gate_cost_2026-09-10.py` — the pinned count moved 169 to 174**, because task V7 added 5 tests to one of the 6 guard files. The test went red exactly as its own docstring says it should, and the entry was corrected in the same change.

3. **`experimental_notes/CDSFL_MASTER_TASK_LIST.md` entry 1.1** — a duplicated sentence and a stale "These 4 files" were removed, both left by an earlier correction of mine.

**Attack all three.** The first is the one that matters: it is a guard whose whole job is refusing wrong numbers, and it has now been wrong twice.

## SECTION 2 — Use the harness

**Form your answer by RUNNING things.**

- **`scripts/panel_brief_validate.py`** — drive `check_declared_figures` directly. Construct declarations that SHOULD pass and that should be refused. Find one it still gets wrong. Candidates worth trying: a figure that appears only inside a longer word, a figure with a thousands separator, a negative number, a percentage sign, a figure printed only on stderr, a script that prints the figure but exits non-zero, a declaration whose script path escapes the repository with `..`.
- **`python3 -m pytest bench/tests/test_panel_brief_format_2026-09-09.py -q -p no:cacheprovider --netguard-strict`** — 29 tests. Mutate the source and prove they catch it. A mutation must be asserted APPLIED and must land on a line the fixture executes.
- **`scripts/ffafp_cycle_gamma_2026-09-10.py`** — the two-sided gate, gamma at or above 0.30 AND 3 consecutive zero-discovery passes. Both sides FAIL. The declared figure above is checked by the mechanism under review, which is circular; break the circle by deriving gamma yourself.
- Every proportion you report needs a confidence interval from 2 independent tools.

## SECTION 3 — Produce a fix, and test it

**Deliver each fix as a file in the sandbox tree.** For every defect you find:

- edit or create the file at its real path inside the sandbox;
- add or extend a test at `bench/tests/` that goes RED without your change and GREEN with it, and show both runs;
- report the exact command and output for each.

**Do not stop at one.** If your first fix reveals a second defect, fix that too. The assistant will test everything you leave and apply what holds.

**Work only inside the sandbox.** Do not modify the canonical tree.

## SECTION 4 — What would refute you

State, before concluding, what evidence would overturn your own fix. Name the case your repair does NOT cover. If you believe the hardened guard is now correct, say what input would still get past it — there is almost certainly one, and naming it is worth more than declaring victory.

## SECTION 5 — Output shape

- `verdict` — CONFIRMED / REFUTED / PARTIAL on whether the 3 changes hold
- `files_written` — every path you left in the sandbox tree, and what each does
- `findings` — file, line, severity, what is wrong, and the fix you WROTE for it
- `falsifier` and `falsifier_result` — the red-then-green runs, verbatim
- `refutation_condition` — Section 4's answer
- `strongest_disagreement` — with this brief and with the other seat. Do not converge.
- `passes_run` — how many

## SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could let a false completion claim stand, break a live run, or feed the founder a stale fact as a current one. Diminishing returns is this project's own criterion.
