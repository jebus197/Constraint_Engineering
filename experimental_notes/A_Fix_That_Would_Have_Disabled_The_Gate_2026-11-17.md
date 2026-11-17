# A fix that would have disabled the gate

**17 November 2026, 06:50 GMT**

## Summary

A repair that looked like a readability improvement would have turned this project's only mechanical commit refusal into a rubber stamp. It was caught by the rule that forces a failable check before a change is presented, and it was never applied. The defect it exposed is not the repair but the absence of any test able to notice it: of the 3 test files that run `hooks/pre-commit` as a subprocess, **0 observe the hook's verdict on its own guard board**. A replacement check that does observe it was built, runs in 1.47 s, and goes red on 5 of 5 mutations. The batch was committed at `725ec976` after 3 boards, 2 of which refused.

## The board, and why its silence mattered

Every commit runs a board of guard tests first. It now holds **313 files and 5,124 tests** and takes about 43 minutes. A standing directive requires any running process to have a terminal showing its full current output. Until this week the board satisfied none of that: `sv` captured the whole run and released it at the end, so a 43-minute wait produced 33 bytes and no reasons.

That was repaired in 2 parts, and part 2 is now confirmed in production — the board that refused this batch delivered its refusal as readable streamed text naming 6 failing guards with their assertion messages. Streaming is wired at **exactly 1 of 24** `_git` call sites, confirmed by an AST pass rather than by reading, so the other 23 are unchanged by construction.

## What part 2 did not cover

`hooks/pre-commit:1037` runs the board from a single line:

```sh
OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1)
CODE=$?
```

A command substitution cannot emit anything until the child exits, so of a 43-minute board the test phase is silent by construction. What streaming made visible is the hook's own narration, which is the first 2 minutes. Observed live: the log stood at 75 lines for 37 minutes while pytest ran.

The capture is not gratuitous. Lines 1044–1097 post-process `OUT` to print the failing lines and the assertion text *first*, because `tail -25` on this machine returns 25 lines of temp-directory cleanup noise and 0 lines naming the failure. Any repair must keep `OUT` byte-exact.

## The one line that would have broken the gate

Piping through `tee` restores liveness — first output at **1.3034 s mean of a 7.4 s run** over 5 repeats, against *never* for the current form, with `OUT` preserved identically at 13,381 bytes.

It also breaks the gate. A shell reports the exit status of the **last** pipeline element, which is `tee`, and `tee` succeeds whatever pytest did:

| form | failing tree | passing tree |
|---|---|---|
| current | `CODE=1` | `CODE=0` |
| `\| tee /dev/stderr` | **`CODE=0`** | `CODE=0` |

So a red board would be recorded as passing and the commit would proceed. `set -o pipefail` restores the 1, but the hook declares `#!/bin/sh` and `pipefail` is not POSIX — it works here only because this machine's `/bin/sh` is bash in sh-mode, a portability regression against the project's own reproducibility claim.

**A first probe produced a false negative and is kept.** With 3 tests, every arm appeared to emit only at the end, which reads as streaming being impossible. 3 tests emit 3 bytes of progress against a 4–8 KiB pipe buffer, so no repair could have looked alive at that size. The probe's *volume* made the result.

## The replacement, verified on 4 properties

A temp file plus a background `tail -f` removes the pipeline, so `$?` stays pytest's own.

| property | result |
|---|---|
| exit code correct | **6 of 6** across 3 repeats each of a passing and failing tree |
| first output | 1.37 s of a 7.5 s run, 185 lines |
| capture intact | 13,381 bytes passing, 14,057 failing, failure text present |
| portability | no dependence on a non-POSIX shell feature |

**Composability was tested and declined.** `tee` plus `PYTHONUNBUFFERED=1` gave 1.2659 against 1.3034 s mean; Mann-Whitney U = 15.0, p = 0.690476; Welch t = 1.0314, p = 0.349968; mean difference −0.0375 s with a 95% interval of [−0.1089, +0.0338] containing 0. The composed form is not shown better, and the standard requires that it demonstrably beat either part alone. With n = 5 this is *no difference demonstrated*, not proven equality.

## The defect underneath, and a claim that was wrong twice

The refusal reading the board's status is `cheap-guards-red` at `hooks/pre-commit:1104`. How many tests exercise it was answered wrongly twice before execution settled it, and both wrong answers are recorded because the conclusion survived while the reason did not.

- **Version 1** — 0 tests *reach* the line. From a grep using one invocation shape, which missed a file.
- **Version 2** — 1 reaches it but asserts only the success direction.
- **Settled by running it** — that test caps the hook at 900 s while the board takes ~2,718 s, so it raises `TimeoutExpired` and `returncode` is never read.

The position that stands:

| test file | asserts | stops at |
|---|---|---|
| `test_precommit_restages_repairs_2026-09-11.py` | `returncode == 1` | `stage0-restage-helper-missing`, line 734 |
| `test_a_refusal_records_why_2026-11-09.py` | status ≠ 0 | `guard-file-missing`, line 829 |
| `test_desktop_mirrors_stay_current_2026-09-10.py` | `returncode == 0` ×4 | times out at 900 s, never arrives |

**71 of 81 recorded boards exceed that 900 s cap — 0.876543**, Wilson [0.787449, 0.931539], Clopper-Pearson [0.784655, 0.939180] on 2 routes agreeing to 0.00e+00. z3 returns `unsat` for the proposition that any existing test could catch the change; a SymPy check of the line numbers independently confirms the 2 early refusals stop short of the board.

The change would have passed all 17,832 tests while disabling the gate.

## B203, raised separately

That third cause is its own defect with its own fix: a guard capping the hook at 900 s while its board runs 2,718 s cannot complete, and the ledger dates the first such failure to 2026-11-09. It is **outgrown, not broken** — its predicate is still right; the subject grew past its window.

The repair has a precedent one file away. `test_precommit_gate_cost_2026-09-10.py` does not type its bound: `BOARD_BUDGET_SECONDS = _recorded_board_budget()` derives it from the same ledger, returning **5,746 s = 3.21× the mean board, with 0 of 81 boards exceeding it**. The typed 900 s is **0.50×** that mean. The 2 bounds differ by a factor of **6.3844**, and only the derived one tracks what it bounds.

A second instance was found in the same pass and is recorded with it: `test_the_long_nested_test_raises_its_own_limit_rather_than_the_global_one` is red, **and red at HEAD too** — verified in a clean worktree — so it is one of the full suite's 32 failures and not from this batch.

## The panel scorer refused to score its own round, correctly

The instrument comparing the free panel's recommendations against this session's refused to emit any figure. It replayed the option shuffle over the **live** decisions file, which is sound only while that file still holds what the seats saw — and 3 recommendations had been corrected after scoring.

It now reads the letters from the **frozen** dispatched brief and a frozen record of this session's picks, pinned to a source commit and a blob digest. Both rounds recover **19 of 19**, with 0 of 19 disagreeing on their first 24 characters. A structural fact surfaced in the same repair: the joint brief carries **0** lettered options, because it puts each seat's prior answer in front of it instead, so letters named in a joint reply refer to the *blind* round's options. An instrument looking for them in the joint brief reported all 19 as missing — which is what happened. It now resolves a joint round from its blind parent.

The delivered figures are unchanged and now reproduce permanently: **12 of 19** where both seats chose this session's option, **14 of 19** where at least 1 did.

## A guard accusing correct prose

The shouted-word check in `test_a_response_is_not_a_ruling_2026-11-09.py` treats any `.isupper()` token as shouting. It was flagging bare entry codes — which Rule 32 positively *requires* beside their descriptor — and the capitalised article opening a sentence. Over 15 derived sentences it flagged **2 tokens, 0 genuine**. The narrowed form still catches `STILL OWED`, `OPEN` and `BLOCKED` on positive controls. The check already spared tokens containing a backtick, underscore, slash, hyphen or paren, so sparing identifiers was its own intent; the plain `B202` shape was simply missed.

## What a cheap pre-flight is worth

2 boards refused before the 3rd passed, at 45.30 and 45.27 minutes, producing nothing.

| subset | cost | break-even catch rate | verdict |
|---|---|---|---|
| 4 files, 88 tests | 122.64 s | **0.143139** (~1 refusal in 7) | can pay for itself |
| 16 files, 2,255 tests | 1,044.15 s | **1.218680** | **unreachable** — above 1 |

From the ledger, **39 of 81 determinate boards refused — 0.481481**, Wilson [0.375996, 0.588644]. Against a mean board of ~1,792 s, the wide subset would have to catch *more than all* refusals to break even, so it is refused on arithmetic, not taste. 2 routes agree on both ratios.

**Measured:** the costs in seconds, and the refusal rate of 0.481481. **Not measured:** the catch rate — the 4 files were chosen *after* seeing which guards refused, so no predictive claim is made. Producer: `scripts/what_a_cheap_preflight_is_worth_2026-11-17.py`.

## What was committed

The batch landed at the third board — **42.98 min, 5,111 passed, 0 failed** — from the night's first green pre-flight. 65 files changed, 17,413 insertions. 2 new guards were added to the hook's own `GUARDS` list, taking it from **311 → 313 files** and **5,106 → 5,124 tests**, because one of them had been described in the record as "on the board" while wired to nothing — the same failure the first board refused over when 4 new measurement scripts reached no test at all.

## What is still open

**1 decision**, and it is not whether the replacement works: whether a streaming test phase is worth a temp file and a background process at all, given the final verdict and curated failure text arrive either way. The directive behind the original request was that a running process be watchable; whether 5,124 progress markers are worth watching is the founder's call. The replacement check is **not** conditional on that ruling and should land regardless, because it takes the number of tests observing the board's verdict from **0 to 5**.

Written under CDSFL note standard v1.9 (1 November 2026).
