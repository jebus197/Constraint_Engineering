# THE BOARD-COST PANEL: A LADDER CANNOT REPLACE THE BOARD, AND THE POST-EXPERIMENT DIGEST MUST REACH OUTSIDE THE REPOSITORY

Record written 2026-11-23T22:12:18+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed, and why

The founder raised a finishing risk on 2026-11-23: commit board runs appeared to
consume most of the project's calendar time, and nothing can be committed until a
board is green. An external advisory recommended layered testing, with the full
board reserved for major milestones. The founder declined to adopt it on sight
and directed that it go to the free panel first. He also asked a question of his
own, in an addendum he wrote himself: should a full board run before each
experiment, after it, or both.

The round put 4 questions to the 2 free seats, `cc2` and `fable`, under the
standing protocol of no compelled convergence, so that disagreement is preserved
as information rather than smoothed to consensus.

## The advisory's central figure is false, and the measurement says so

The advisory states that full board wall-clock has grown past 3 hours. Over the
project's own duration ledger that is false of the instrument which gates
commits. Across 114 determinate recorded runs the longest board ever recorded is
3313 s = 55.22 min, and 0 runs reached 3 hours. Producer:
`scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py`, re-run
2026-11-23.

The 3.13 h figure belongs to the FULL SUITE of 18,419 tests, a different
instrument that does not gate commits. The advisory conflated the 2, and its
recommendation must not be adopted on that basis.

The founder's underlying concern survives the correction, and a figure that had
never been pinned anywhere is the one that governs planning: the gate REFUSES 55
of 114 = 0.482456, Wilson [0.392806, 0.573250], Clopper-Pearson [0.387886,
0.577960]. The expected number of boards needed to land 1 batch is therefore
1.932203, computed on NumPy and on an exact SymPy rational in agreement, which
puts the expected cost of landing 1 batch at 66.7596 min rather than the 34.5510
min a single board costs.

## What the panel found, and what independent execution confirmed

Seat `cc2` answered the substitution question with a measured refusal: a
diff-derived ladder selects guards by literal path, and 68 of 332 board guards
derive their subject set at runtime through `glob`, `rglob`, `iterdir` or
`os.walk`. For a newly added member of such a population the selector returns
nothing, because the guard's text contains no literal member path.

That figure was reproduced independently here against the same instrument,
`scripts/which_guards_does_this_commit_risk_2026-11-22.py`: 68 of 332 =
0.204819, Wilson [0.164902, 0.251489] on 2 agreeing routes, Clopper-Pearson
[0.162706, 0.252288].

The same night supplied a live confirmation that neither seat could have
arranged. The board run of batch 13 refused with 6 failures across 4 guard
files, and all 4 derive their populations at runtime:
`test_recovery_memory_doc_repairs.py`,
`test_panel_records_are_preserved_2026-09-11.py`,
`test_panel_rounds_have_a_full_record_2026-09-11.py` and
`test_tonights_producers_are_reached_2026-11-08.py`. Of those, 3 read a panel or
memory location. No staged file named any of them, so a diff-derived ladder
would have selected 0 of the 4. Entry B216, the pre-board ladder already selects
the guards that refuse, is therefore answered in the negative for this class of
guard, and the ladder stands as a pre-filter rather than as a substitute.

## Where testing refined the panel's own proposal

On the founder's question both seats converged, independently and from different
reasoning. Seat `cc2` judged the existing ordering right and its conditional
wrong, because the post-board is gated on a predicate nothing evaluates, and
prescribed a computed digest comparison costing seconds against a 47-min board.
Seat `fable` gave before always, after conditionally, with the condition
measured rather than assumed, through a tree digest taken before and after the
experiment, with the post-board required if and only if the digests differ.

Testing that converged proposal found it insufficient, which is the reason the
protocol requires a panel's output to be tested before adoption. Tonight's
trigger was not in the tree. The failing memory guard reads
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory`, which holds
405 files and lies OUTSIDE the repository: a digest over tracked paths cannot see
it, and a memory file written at 21:59 while the board ran from 21:12 is exactly
what turned that guard red. A tree digest would have reported no change and
skipped a post-board that was needed.

So the condition must be a digest over the populations the guards actually walk,
of which at least 1 is outside the repository, and not a digest over the tree.
That is an addition to the seats' answer rather than a correction of its
direction, and it is held here rather than built, because changing when a gate
refuses is a change to the gate.

## What remains unverified, stated as such

Both seats report that the board's own `--durations=25` table, the 1 instrument
that can attribute board time per guard, was being generated and deleted on
every one of 113 boards. The shape is consistent with this tree, where
`hooks/pre-commit:1237` exports the option and `hooks/pre-commit:1253` removes
the log. The claim has NOT been confirmed here by execution, and the retention
repair both seats delivered sits in their sandbox diffs rather than in this tree.

The 2 seats also disagree with the project's own recorded decomposition of board
growth. The record holds a total growth of 4.0172x as guard count 2.6111x times
per-guard cost 1.5385x; seat `cc2` reports 4.3357x as 1.4310x times 3.0298x over
the window the ledger actually covers. Both cannot describe the same window, and
the disagreement is preserved here rather than resolved, because an aggregate
figure without its window is not a measurement. Neither decomposition has been
re-derived against the other's window.

On the threshold question both seats refused the count as the wrong variable,
`cc2` noting that 3 of 26 recorded attempts sit at exactly 24 staged files, 1
file below a threshold of 25, while splitting a commit is free. That figure is
unverified here.

## CC1's own position

A board before an experiment and a board after it answer different questions and
are not substitutes. A board before protects the experiment's VALIDITY, because
an experiment run on a broken harness produces a result that must be discarded,
and for a paid run that spend is not recoverable. A board after protects the
RECORD, because an experiment writes artefacts into locations that board guards
walk, and those guards can turn red with no code change at all. Tonight
demonstrated the second mechanism without any experiment being run: 3 panel
directories and 1 memory file were enough.

The composition is therefore justified on a named property rather than on the
observation that both can be done: before always, at full board; after only when
a digest over the guards' own populations has changed, which is cheap to compute
and covers the case a tree digest misses. Where the digest is unchanged the
post-board is skipped, so the policy costs less than running both
unconditionally and catches a class that running only the pre-board misses.

## What is owed to the founder

The founder's ruling of 2026-11-23 already requires a full board before each
experiment, and he limited that policy to the remaining development stages. What
is owed is a decision on the post-experiment half, and on whether the digest
condition may be built, since it changes when a gate refuses. Entry B178, every
pinned commit-cost figure in both instruction files is stale, is confirmed again
by this round: the pinned mean of 1876.858696 s over 92 boards is now 2073.061404
s over 114, and the pinned refusal count of 44 of 92 is now 55 of 114.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — DRAFT: the board-cost policy, and an external advisory that is wrong on its central number

**STATUS: DISPATCHED as a JOINT round on `panel_b12_20261123T170728Z`.** The founder has NOT adopted the advisory
under discussion and has said explicitly it must not become policy until he and
I agree it is accurate and sane. This round is to test it, not to implement it.

**WHAT PROMPTED IT.** An external reviewer produced an advisory arguing that the
project's commit board has grown past 3 hours, that running it before every
commit is not standard practice, and that it should be reserved for major
milestones with cheaper layers used for ordinary batches. The founder's concern
underneath it is specific and legitimate: *that at the current rate the project
might never finish and the majority of time will be consumed by board runs.*

---

# PART 0 — THE JOINT ROUND YOU OWE, AND THE REPLY YOU HAVE NOT SEEN

**THIS IS A JOINT ROUND on `panel_b12_20261123T170728Z`.** Both seats answered
that brief BLIND, neither having seen the other. The dispatcher REFUSED to open
a new blind round while that debt stood, and it was right to: a blind reply
never cross-examined is an opinion the project must then arbitrate alone.

**WHAT HAPPENED TO YOUR Q1 FINDING, so you need not repeat work.** Both seats
independently found that `inserts` and `uses_file` were asked SEPARATELY of the
same node list, so a constant-path `sys.path.insert` was credited whenever any
unrelated preceding statement mentioned `__file__`. THAT WAS ADOPTED: commit
`fa687fda`, `bench/tests/test_help_never_acts_2026-09-11.py:249`, now
`if inserts_file_derived:`, requiring the derived name inside `call.args`.

**AND TESTING YOUR PROPOSAL FOUND SOMETHING YOU SHOULD KNOW.** Seat `fable`
named a regression test,
`test_a_decoy_derived_name_beside_a_constant_insert_is_refused`. THE FIX HAD
LANDED WITHOUT IT. Verified by execution: the shipped predicate refuses the
decoy (False) while the unmodified fixture is still credited (True), so the
repair was correct -- but nothing held the case that motivated it, and reverting
the join would have gone unnoticed. The test is now added, goes RED against the
reverted join, and the file was restored byte-identical afterwards. A fix
without its own falsifier is a defect class this project has recorded in its
own right.

**WHAT IS ASKED OF YOU NOW.** Read the other seat's complete reply below, then
answer QJ in addition to Part 1's questions.

**QJ. Where does the other seat's strongest claim fail, or where does it defeat
your own?** Name the specific claim. If you now think your own blind answer was
wrong, say so plainly -- a reversal with a reason is worth more than a defence.
If you find no genuine disagreement, say so rather than manufacturing one; a
fabricated disagreement is worse than agreement.

**2 claims the orchestrator wants pressure on**, both bearing on figures this
project relies on:
- `cc2` holds that an upper bound of 0.215311 from 0 of 14 is **not evidence at
  all**, being a function of `--interval`, a free parameter. Is that right, or
  is it evidence of a bounded kind that `cc2` has mis-filed?
- `cc2` holds that "this batch is itself 1 data point" is wrong **in the
  direction that favours the line**. Does that survive the other seat's reading?

### SEAT `cc2` — ITS COMPLETE REPLY, UNALTERED (21699 characters)

`````text
Five passes run. Both fixes are in the tree, both falsifiers DISCRIMINATE, and the targeted suite is unchanged at `3 failed, 12 passed` (the 3 failures are the absent `.git` in the staged sandbox, identical before and after my edits).

---


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `bench/tests/test_help_never_acts_2026-09-11.py` | `3250a7a577e75f90` | 31446 | 2026-11-23T20:15:32+00:00 |
| `scripts/the_insert_must_carry_the_file_2026-11-23.py` | `66af7f26d47d0b07` | 7457 | 2026-11-23T17:28:22+00:00 |
| `scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py` | `31d53477cc6b7068` | 11170 | 2026-11-23T17:28:22+00:00 |
| `scripts/the_replacement_denominator_must_be_opportunities_2026-11-23.py` | `fef0033e85eb1355` | 5179 | 2026-11-23T17:28:22+00:00 |
| `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py` | `d4c07b7eb005aa88` | 8770 | 2026-11-23T16:50:05+00:00 |
| `scripts/was_this_batch_reviewed_2026-11-22.py` | `82d12af5b65bfd59` | 6690 | 2026-11-22T01:29:39+00:00 |
| `scripts/what_is_a_significant_batch_2026-11-23.py` | `8b57505d8a9075a7` | 9182 | 2026-11-23T13:48:51+00:00 |
| `scripts/why_is_the_board_getting_slower_2026-11-23.py` | `4cb07fcc74de64f6` | 11690 | 2026-11-23T19:45:59+00:00 |
| `scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py` | `6fe0d6e59494190b` | 15746 | 2026-11-09T03:08:01+00:00 |
| `bench/tests/test_the_parked_file_regenerates_without_losing_him_2026-10-17.py` | `3cf2f518855fb60b` | 18266 | 2026-11-23T20:06:34+00:00 |

## Q1. The widened accepting predicate

**question** Is the file-derived-name rule too permissive, and is a static predicate the right instrument?

**verdict** The widening is wrong, but **not for the reason you distrust** — the defect is that `inserts` and `uses_file` are asked *separately* of the same bag of nodes and nothing requires them to be the same expression; I have a constructed source that is credited and, run as `python3 -m x --help`, **writes a file**.

**reasoning** Instrument: the real `answers_help` imported from `bench/tests/test_help_never_acts_2026-09-11.py` (digest `c129c66e1abadfea`, as dispatched), plus direct execution of a constructed script under `-m`. Lines 225–232 of the dispatched file compute `inserts` (is there *any* `sys.path.insert` before the import) and `uses_file` (is there *any* file-derived name before the import) over the same node list, then accept on `inserts and uses_file`. The insert's **arguments are never inspected**. So a constant-path insert with a file-derived name beside it for an unrelated reason is credited.

Your own discrimination case `test_a_file_derived_name_is_required_not_just_any_insert` does not catch this, and its docstring claims more than it tests: it builds its constant-path variant by *replacing* the `__file__` assignment, so `__file__` vanishes from the whole module and `uses_file` is False for a reason the realistic shape does not share. Scrub-the-module is a weaker property than insert-must-carry-the-path.

Two constructed sources, both credited by the dispatched predicate:

```
B derived-name rule only     WRITES=True  dash-m credited=True
C bare __file__ sibling      WRITES=True  dash-m credited=True
```

`C` uses **no derived name at all** — just a bare `__file__` among the preceding siblings. So the half of the widening you trust (preceding siblings) is independently sufficient to break the predicate, and the half you distrust (file-derived names) is not required. **Your self-distrust is aimed at the wrong half.**

The concrete failure, executed rather than argued:

```
--- DIRECT invocation with --help ---
usage: (help answered, nothing written)
exit=0  wrote=NO

--- python3 -m scripts.constant_insert_demo --help ---
exit=0
wrote=ORDINARY_WORK_RAN.txt
this script just wrote a file
```

**Severity.** The help-ratchet domain declares no consequence scale of its own, so per the ordinal-severity rules it **inherits the application domain's** — the panel-record corpus, whose scale this guard's own comment names ("54,480 bytes of a record the founder's own directive requires preserved verbatim"). On that inherited ordering the defect is at the critical level under §10 category 3, **verification-integrity corruption**: a defect in the measurement machinery. I will not supply a number, and I note precisely what is *not* claimed — **0 scripts in the real tree are currently affected** (measured below), so the realised loss today is zero. The defect is in the guard's future accepting behaviour, not yet in the tree.

**Is static the right instrument?** Yes, keep it static. An executing predicate costs ~18 s and needs no approximation, but it must *run 837 untrusted scripts with `--help`* to decide whether they write — the exact action the guard exists to prevent, on the exact population most likely to do it. That trades an approximation for a 19-way-door execution surface, and your own record says the flag "was never the only way in." The approximation is repairable; the execution risk is not. Repair the join.

**fix** `bench/tests/test_help_never_acts_2026-09-11.py` (post-fix sha256 `d5c314c415abd8eb366a92`) — the file-derived value must be an **argument of the insert**. 13 lines, replacing two independent `any()` calls with one that walks `call.args`. No feature removed; the residual (`str(REPO / "vendor")` is file-derived but not the script's own directory) is unchanged and now stated in the code.

**falsifier** `scripts/the_insert_must_carry_the_file_2026-11-23.py` — imports the real predicate, asserts 3 constant-path shapes REFUSED and 4 genuine shapes CREDITED including both scripts the widening was written for. Executed:

```
  must REFUSE  constant insert, derived name beside it    -> False
  must REFUSE  constant insert, bare __file__ beside it   -> False
  must REFUSE  constant insert inside the try             -> False
  must CREDIT  preceding-sibling insert via a file-derived name -> True
  must CREDIT  insert inside the try, built from __file__ -> True
  must CREDIT  the_restore_mutations_2026-11-22.py        -> True
  must CREDIT  the_majority_separation_mutations_2026-11-22.py -> True
  must CREDIT  assemble_panel_record.py                   -> True
exit=0
```

Driven through your differential rule against the pre-fix bytes:

```
  DEFECT PRESENT  exit=1  FALSIFIED-token=True  -> FAIL
                  |   CREDITED a constant-path insert: constant insert, derived name beside it
  DEFECT ABSENT   exit=0  FALSIFIED-token=False -> PASS
  target restored byte-for-byte : True
  DISCRIMINATES
```

Regression over the real population — **0 verdict flips on all 840 scripts** (recursive; `840 = your worktree 839 + my 1 new script`, which reconciles your figure exactly), and 0 dash-m offenders after the fix. The join is a pure tightening that touches no real script.

**what_would_refute_me** A real tracked script that legitimately answers `--help` under `-m` while its insert's *arguments* contain no `__file__` and no file-derived name — e.g. one that mutates `sys.path` through a helper function call, `sys.path[0:0] = [...]`, or `site.addsitedir`. My fix would wrongly accuse it. I measured 0 such scripts in 840 today; one appearing tomorrow refutes the fix, and the repair is to credit those forms explicitly rather than to un-join the conjunction.

**disagreement** Two with your framing. First, as above: you nominate the file-derived-name rule as the suspect and it is not the culprit — case `C` breaks the predicate with no derived name. Second, **your declared figure "6 of 837 at HEAD" is not re-executable by any seat in this dispatch.** The sandbox has no `.git`, so the producer refuses:

```
REFUSING: git cannot list scripts/ at HEAD: fatal: not a git repository
```

That refusal is correct behaviour — `tracked_scripts()` deliberately refuses rather than reporting 0 offenders from an empty list, which is good design. But it means your note about declaring HEAD's figure rather than the working tree's solved a validator problem while leaving the figure unverifiable *here*. I substituted a recursive glob and said so.

---

## Q2. 0 of 14, upper bound 0.215311

**question** Is that bound evidence for either conclusion?

**verdict** **Neither** — and the bound is not "weak evidence", it is **not evidence at all**: it is a function of `--interval`, a free parameter, computed over a denominator that includes trials in which the event was impossible.

**reasoning** Two instruments. SymPy, symbolically: at k=0 the Wilson upper bound simplifies to exactly `z²/(n+z²)`, verified `upper - z²/(n+z²) == 0`. Confirmed on an independent kernel — Wolfram Language (local Wolfram Engine, via `wolframscript`, exit 0, no `Name::tag`, no `$Failed`) returned `0.2153108027376358`, `0.0036109316748686583`, and `0.` for the simplification difference. That form is strictly decreasing in `n`, and `n` is the **poll count**:

```
  pairs=   14  Wilson 95% upper = 0.215311   <- your 14 pairs
  pairs=   53  upper = 0.067582   <- the SAME 106 s run at 2.0 s
  pairs= 1060  upper = 0.003611   <- the SAME 106 s run at 0.1 s
```

Identical evidence — one unchanging pid — yields any bound you like. This is not hypothetical. I ran your probe against a live pytest for **20 seconds at 1.0 s spacing**:

```
  pid-set sizes seen                            : [2]
  consecutive pairs considered                  : 19
  FULL REPLACEMENTS (both non-empty, no overlap): 0
  Wilson 95%            : [0.000000, 0.168179]   (mpmath closed form agrees to 2.78e-17)
```

**A fifth of the observation time produced a tighter bound than yours.** An interval that narrows as you look less is measuring the observer, not the world. (Your `2.78e-17` two-route agreement reproduced exactly; that part of the instrument is sound. Note also pid-set size was **2**, not 1 — so "size 1 throughout" is not an invariant of the setup.)

Second defect, falsified directly on `classify`:

```
  alternating matched/empty -- event IMPOSSIBLE in every pair -> (0, 0, 15, 15)
  alternating case: 0 of 15 pairs, Wilson 95% upper = 0.203883
```

A full replacement requires both sides non-empty *by definition*, so those 15 pairs could not have contained the event — and they produce a bound **tighter than the one you declared**. The denominator is not a risk set.

So: withhold both claims, which is the reading you said you could see and could not refute. I confirm it and strengthen the ground. But one asymmetry survives — the probe does cut against B209's *premise*, because that premise predicts churn and 0 observed changes is inconsistent with churn *during a single pytest invocation*. That is weak and it is not the same as supporting either seat.

**What would settle it.** The identified denominator is **observed set-change events**, not polls, and it must be collected where churn is possible: a real 34-minute board that spawns a pytest child per guard file, not one invocation. With 0 events observed you need `n ≥ z²(1−ε)/ε` change events: **35** for ε=0.10, **73** for ε=0.05, **381** for ε=0.01. There are 971 files in `bench/tests/`, so if a board really replaces its child per guard file, one board supplies hundreds of change events and ε=0.01 is reachable in a single board — which is exactly why observing one board is the measurement, and 14 polls of a pytest never will be.

**fix** `scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py` (post-fix sha256 `31d53477cc6b7068cc5b6d`). `classify` now also returns `opportunities` — pairs where the set actually changed with both sides non-empty. With 0 opportunities the script prints **UNIDENTIFIED** and reports no bound, showing the poll-pair figure explicitly as a diagnostic of the polling rate. **Every previously printed count is still printed**; only the claim attached to them is corrected. I also split out a branch that would otherwise have printed "Nothing matched the gate's patterns" when processes *had* matched — found in my own fix on pass 5, and it now says the honest thing: corroborates neither seat.

**falsifier** `scripts/the_replacement_denominator_must_be_opportunities_2026-11-23.py`. Executed:

```
  A/C unchanging set, 15 polls        -> classify = (0, 14, 0, 14, 0)
  C   same set, 10x the polls         -> classify = (0, 149, 0, 149, 0)
  B   alternating matched/empty       -> classify = (0, 0, 15, 15, 0)
  D   a genuine full replacement      -> classify = (1, 0, 0, 1, 1)
  E   z^2/(n+z^2) at n=14             -> 0.215311 (expected 0.215311)
exit=0
```

Poll-pairs go **14 → 149** under 10× polling while opportunities stay **0**: the invariance is the whole point. Case D is the anti-vacuity arm — the fix cannot pass by reporting 0 for everything. Differential: `DEFECT PRESENT exit=1 FALSIFIED-token=True -> FAIL`, `DEFECT ABSENT exit=0 -> PASS`, `restored byte-for-byte: True`, **DISCRIMINATES**.

**what_would_refute_me** One observed full replacement on a real board promotes the scenario from unrealised to demonstrated and makes cc2's weight the right one. Separately, if the board genuinely runs one long-lived pytest rather than a child per guard file, then B209's premise is simply false and the whole disagreement dissolves — which would make my "re-measure the premise" the wrong recommendation and "withdraw B209" the right one.

**disagreement** I reject "an upper bound that cannot exclude a rate of 0.215311 is weak evidence." It is not on the evidence axis at all. Calling it weak invites the repair "take more samples", which here makes the bound *tighter without adding information* — the worst possible outcome, because it manufactures false confidence from the same unchanging pid. I also disagree with your framing that the probe "polls the gate's own `_RUNNER_PATTERNS`, read out of the hook rather than typed" as a sufficiency argument: reading the matcher from the hook guarantees you measure the right *population*, and says nothing about whether the *denominator* is a risk set. It was not.

---

## Q3. Was the testing of the adopted proposals sufficient?

**question** What did the testing not cover; is 1-of-6 the weak point?

**verdict** **Yes, 1-of-6 is the weak point** — "0 failures in 1 trial" bounds the per-harness failure rate at ≤0.793, consistent with up to 4.76 of the 6 being broken — but the binomial framing understates the fix's *real* strength and misplaces the risk.

**reasoning** Same closed form, `z²/(n+z²)`:

```
  0 failures in 1 trial -> Wilson 95% upper = 0.793451
  i.e. consistent with up to 4.76 of the 6 repaired harnesses being broken.
  0 failures in 6 trials -> upper = 0.390334  (up to 2.34 of 6)
```

So as an independent-trials argument, running 1 of 6 is near-vacuous. But the 6 are **not independent trials**: you confirmed first that all 6 share one diagnosis (`from pathlib import Path`) and applied one fix. For a common-cause defect with a common-cause fix, one completion run is far more informative than `n=1` implies — it exercises the shared mechanism end-to-end. The residual risk is not "do 5 independent things work" but "does the shared fix interact with per-harness differences", and *that* risk is invisible to both compilation and `--help`.

Concretely, what compilation and `--help` do **not** cover, and why it matters here: `--help` exits inside the guard, before the restore path is ever entered; compilation proves the import parses. The fix was to an *import*, and the thing that import feeds is the mutate-and-restore cycle. Your 1 completion run verified restore by SHA-256 at 7 of 7 mutations RED — that is the right observable, and it is the one the other 5 have no evidence for. Note your own third recorded vacuity case was precisely a *restore* observable reading wrong. The gap is therefore in the highest-risk place, and 5 completion runs are cheap against the claim they support. Run them.

**fix** NONE. This is an assessment of your testing, not a defect in an artefact; inventing a file here would be an addition nothing reaches. The action is to execute the other 5 harnesses to completion with SHA-256 restore verification — the instrument already exists and is already proven on 1 of 6.

**falsifier** Not applicable, and I will say why rather than force one: the proposition is "5 harnesses are untested", which is a fact about what was *run*, not about code state. A differential falsifier needs a defect to toggle, and there is no defect here to toggle — your `--defect-file` arm would be byte-identical to the target and the tool would correctly refuse as vacuous. The arithmetic above is the evidence, and it is re-executable.

**what_would_refute_me** All 5 remaining harnesses running to completion with verified restore. That converts my finding to no-change-needed and moves the bound to 0.390334 — still not tight, but the right 6 of 6.

**disagreement** Your question offers 1-of-6 as the candidate weak point and it is, but you framed it as a *sampling* shortfall. It is really a **coverage** shortfall: the 5 unrun harnesses are not under-sampled, they are untested on the only observable that matters, while being fully tested on two that cannot fail informatively. `--help` exiting cleanly is close to guaranteed once the guard parses, so reporting it for 5 of 6 adds confidence that was never at risk — the same shape as Q2's tightening bound.

---

## Q4. Ledgered advisory line versus refusal

**question** What measurement decides between them?

**verdict** Decidable, and the predicate is cheap — but **this batch is not a data point for it**, and 1 commit could not settle it even if it were.

**reasoning** The hook-evaluable predicate: on every commit, append `{commit_sha, rounds_since_head, honoured: bool}` where `honoured` is true iff `rounds_since_head > 0` *or* the commit was abandoned. That is a mechanical record, needs no judgement, and yields `lapse_rate = lapses / commits`. The decision rule is a comparison of two measured quantities, not a preference: **refusal dominates iff `lapse_rate × cost(unreviewed commit) > block_rate × cost(false block)`**, where `block_rate` is the fraction of commits where the line fires and a round genuinely was not owed. Both terms come out of the same ledger.

The distinguishing outcome is sharp. Advisory-plus-ledger and refusal differ **only** in the cases where the line fires: so ledger a stretch of commits and read the `honoured` column. If `lapse_rate → 0` once the column exists — i.e. being *visible* is what fixed it — advisory suffices and refusal is strictly more surface for no gain. If lapses persist at a visible rate, observation is not sufficient and refusal is the measured answer. cc2's point that "unrecorded report was the defect rather than report itself" is testable exactly here, and that is the right reframing.

What settles it quantitatively:

```
  0 lapses in 1 commit -> Wilson 95% upper on the lapse rate = 0.793451
  prior round measured 7 of 10 lapses = 0.700, which is INSIDE [0, 0.793].
  commits needed, 0 lapses, to push the upper bound below:
    e=0.30  -> 9 commits        e=0.10  -> 35 commits
```

So ~9 ledgered commits distinguish "fixed" from "still lapsing at the prior rate", and ~35 give a usefully tight bound.

**fix** NONE. A ledger is a real addition, but writing one here would be an addition nothing reaches — it needs to be wired into the commit hook and executed by a test, and I have neither the hook's dispatch path measured nor a round's worth of commits to validate it against. Per the additive standard I decline to ship an unreached entry point; this project has done that 11 times. The measurement above is what Q4 asked for.

**what_would_refute_me** A cost asymmetry large enough to swamp the rates — if one unreviewed commit can void an experiment's headline result the way Exp 48's falsifier did, then `cost(unreviewed commit)` is so far above `cost(false block)` that refusal wins at *any* non-zero lapse rate and the ledger measurement is moot. That is a question about the cost terms, and I have not measured them; if the founder can name one voided experiment per unreviewed commit, refuse and stop measuring.

**disagreement** Strongest disagreement in this brief: **"this batch is itself 1 data point" is wrong, and it is wrong in the direction that favours the line.** The line reported and the board was killed — but it was killed by *a human reading the line and choosing to act*, after the preceding round had just measured 7 of 10 lapses and made that lapse salient. That is a data point about human attention under fresh scrutiny, not about the reporting line's efficacy. The advisory condition it would need to test is "the line reports and nobody is primed to care", which is the condition under which all 7 lapses happened and is exactly the condition this batch does not instantiate. Counting it as evidence for advisory is the Hawthorne case, and it is the same error as Q2: a measurement taken in a regime where the failure could not occur.

---

## Termination

**5 passes.** Pass 1 read the predicate and located the unjoined conjunction. Pass 2 executed the counterexample, fixed it, drove the differential. Pass 3 ran the population diff, found my own glob was top-level-only, and redid it recursively over 840 — which is also what reconciled your 839. Pass 4 found the `classify` denominator defect and derived the polling-rate artefact. Pass 5 re-read my own probe fix and found the `else` branch printing "Nothing matched" when processes had matched; fixed. A sixth pass over both fixed files produced no new above-threshold findings.

**Two above-threshold findings, both with delivered fixes and DISCRIMINATING falsifiers:**

| | file | category |
|---|---|---|
| the dash-m proxy never required the insert to carry the file-derived path | `bench/tests/test_help_never_acts_2026-09-11.py` | §10.3 verification-integrity corruption |
| the full-replacement denominator is poll count, not a risk set | `scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py` | §10.3 verification-integrity corruption |

**No composability claim is made.** The two fixes touch unrelated artefacts and there is no measurement showing a composed repair beats either alone, so per the founder's 2026-10-02 definition each stands as the single fix. Reporting that they do not interfere would be the weak form his definition excludes, and I am not reporting it.

**Q1's widening was right to be made and wrong as implemented** — it correctly stopped accusing two correct scripts, and the brief's instinct to distrust it was correct while its diagnosis of *which half* to distrust was not. The judgement you asked me to be explicit about: the wrong widening carries a severity at the critical level on the inherited application scale, but has caused **zero** realised loss in the current tree, and I would not have found it by reading — case `C` only became visible once the arguments of the insert were examined separately from the names beside it.
`````

### SEAT `fable` — ITS COMPLETE REPLY, UNALTERED (16536 characters)

`````text
All verification complete. The same 3 pre-existing failures are the sandbox's missing `.git` (the population guard refusing loudly, as designed — identical before and after my change); 13 passed, up from 12 — the +1 is my regression test. Report follows.

---

# SEAT REPORT — batch 12, 2026-11-23

**Sandbox caveat, stated once:** this sandbox stages no `.git`, so `tracked_scripts()` refuses (3 test failures, identical before and after my change — the fail-loud path working) and the brief's git-based populations (837 at HEAD / 839 worktree) are not reproducible here; my population figure is **825 by `scripts/*.py` glob**. Artefact digests at my read matched the dispatch stamps.

---

## Q1 — the widened predicate

**verdict:** The widening is **wrong as shipped** — the file-derived-name rule is a broken dataflow link, and I constructed and dynamically confirmed a source it wrongly credits; the static instrument itself is right, and I have delivered and differential-checked the tightening.

**reasoning:** `_help_calls_unreachable_under_dash_m` (lines 225–233 at dispatch) computes `inserts` and `uses_file` as **two independent `any()` scans over `before`**. Nothing requires the file-derived name to appear in the insert's argument. Constructed counterexample: a `sys.path.insert(0, '/somewhere/else')` (constant — the exact shape `test_a_file_derived_name_is_required_not_just_any_insert` exists to refuse) is credited whenever any *unrelated* preceding statement mentions `__file__` or a derived name — here `print('running from', HERE)`. Both variants (`HERE` decoy, bare `__file__` decoy) return `True` from `answers_help(…, under_dash_m=True)`. Dynamically driven under `python3 -m pkg.attack --help`: **exit 0, usage never printed, ordinary work ran and wrote a file.** The concrete failure the defect permits, named per the brief: a tracked writer of this shape passes the ratchet, and its `--help` under `-m` performs its write — the same class as the 54,480-byte record destruction of 2026-09-11, severity on this project's own scale **material** (§10 categories 1 and 4). Note the P-Pass's 5th discrimination test did not catch this because its constant-insert case *removed* the derived-name assignment entirely, so `derived` was empty — it tested the conjunction's second leg, never the broken coupling between the legs.

On the instrument question: **static is right as the per-run ratchet.** An executing predicate *runs the defect it detects* — my dynamic run wrote a file; over 837 scripts, every broken guard performs its ordinary work, and the docstring records that 15 of 17 runners once billed a live dispatch on an unrecognised argument. "18 s and no approximation" is only true in a throwaway clone, which is per-run machinery and spend-risk the static proxy avoids. The existing division — static ratchet plus one-shot executing validation in a clone — is the simplest sufficient arrangement; the fix is to repair the proxy, not replace the instrument.

**commands_run** (abridged to verdict lines; full outputs above):
```
python3 -m pytest bench/tests/test_help_never_acts_2026-09-11.py -q
  → 3 failed (git-less sandbox, fail-loud), 12 passed   [pre-fix baseline]
python3 - <<EOF  # static attack
  → ATTACK credited under -m rule: True / ATTACK2 credited: True
python3 -m pkg.attack --help   # dynamic, _cli_help beside script, constant insert
  → exit=0, FILE WRITTEN: ordinary work ran under --help
python3 -m pytest …::TestTheDashMProxyDiscriminates … -q   [post-fix]
  → 8 passed
python3 - <<EOF  # population diff, defect vs fixed, 825 scripts
  → verdict changes defect->fixed: 0; offenders 0 both ways
```

**fix:** `bench/tests/test_help_never_acts_2026-09-11.py` — replaced the two independent scans with a single `file_derived_insert` scan requiring `__file__`/a derived name **inside the insert call's arguments**, plus regression test `TestTheDashMProxyDiscriminates::test_a_decoy_derived_name_beside_a_constant_insert_is_refused` (wired: executed by the suite, 13 passed post-fix). Fixed artefact sha256 `9d9945d77cec0e8a…`. 0 verdict changes over all 825 staged scripts — the tightening touches only the decoy class, so the 2 wrongly-accused scripts stay accepted.

**falsifier:** executed via `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py --target bench/tests/test_help_never_acts_2026-09-11.py --defect-file /tmp/defect_copy_test_help.py -- python3 /tmp/q1_falsifier.py` →
```
DEFECT PRESENT  exit=1  FALSIFIED-token=True  -> FAIL
DEFECT ABSENT   exit=0  FALSIFIED-token=False -> PASS
target restored byte-for-byte : True
DISCRIMINATES
```
(The in-tree regression test could not serve as the differential falsifier — swapped to the defect copy it fails by *absence*, the tool's own vacuity case 2 — so the falsifier imports `answers_help` from the target and runs in both arms.)

**what_would_refute_me:** a driven run showing a script of the decoy shape *does* answer `--help` under `-m` (it cannot, unless `_cli_help` is importable from the constant path — in which case construct it with a path that provably isn't); or a tracked script whose verdict my tightening flips from accepted to accused while it dynamically answers `--help` under `-m` (my 0-of-825 diff says none exists today, but the HEAD/worktree git populations contain up to 14 scripts this sandbox does not stage).

**disagreement:** The brief frames the residual risk as "a name assigned from `__file__` somewhere else in the module may have nothing to do with the path being inserted." That is the *smaller* half of the defect. The larger half, which the brief does not name, is that the name needed not be in the insert **at all** — the two conditions were never conjoined on the same node. Also: the brief's "P-PASS DONE, BOTH DIRECTIONS: 5 discrimination tests, 15 passed" overstates coverage — the constant-insert test deleted the derived assignment rather than decoupling it, so the pass exercised the predicate's legs but never their coupling, and the P-Pass was green over a live material defect.

---

## Q2 — 0 of 14, upper bound 0.215311

**verdict:** The figure is arithmetically correct but bears on **neither** claim — this is a wrong-population problem, not a weak-sample problem, so both the corroboration of fable and the cut against B209's premise should be withheld.

**reasoning:** Derived, two routes plus Wolfram: Wilson upper at k=0 is z²/(n+z²) = 3.84146/17.84146 = **0.215311** (statsmodels and mpmath closed form agree to 2.78e-17; Wolfram Language, local Wolfram Engine: 0.21531080273763578). So the interval is sound. But the probe polled beside a **single plain pytest invocation** — pid-set size 1 throughout. B209's premise is churn **between pytest children across guard files during a ~34-minute board**. A stable pid within one invocation is what *both* hypotheses predict for this regime; the probe's own docstring says so ("a short run is not a commit board"). Even n → ∞ in this regime decides nothing about the board regime. Therefore: (a) "corroborates fable" — withhold; fable's claim concerns the board. (b) "cuts against B209's premise" — withhold, and this one is actively wrong as stated: a single pid during one pytest run is fully consistent with per-guard-file replacement during a board, because no guard-file boundary with a child swap was spanned. **The sample that settles it:** run `does_the_matched_set_ever_fully_replace_2026-11-23.py` for the full duration of a real commit board (~34 min at 2 s intervals ≈ 1020 polls spanning every guard-file boundary). Derived thresholds: 0 full replacements in **≥ 73** pairs bounds the rate below 0.05; in **≥ 381** pairs below 0.01; a board-length run exceeds both. One observed full replacement promotes the scenario to demonstrated and the question of weight is over.

**commands_run:**
```
python3 - <<EOF (statsmodels + mpmath)
  → [0.000000, 0.215311]; closed form agrees to 2.78e-17
  → exclude 0.05 needs n>=73; exclude 0.01 needs n>=381
wolframscript -code 'z = Quantile[NormalDistribution[], 0.975]; N[z^2/(14 + z^2), 10]'
  → 0.21531080273763578   [Wolfram Language attribution]
```

**fix:** NONE — the deliverable is the decision procedure above; the measuring instrument already exists in-tree and needs only to be run against a real board, which this sandbox cannot host.

**falsifier:** the arithmetic was differentially self-checking (two independent routes agreeing to 2.78e-17, third route Wolfram); the regime-mismatch argument is logical, not executable here, and I say so rather than fake a run.

**what_would_refute_me:** a board-length probe trace showing poll pairs that *did* span pytest-child replacements (e.g. pid-set sizes > 1 or non-identical pairs) — that would convert the 0-count into genuine evidence against realisability and my "wrong population" claim collapses; conversely a trace showing the board runs one pytest for all guard files refutes B209's premise directly and my withholding of (b) was too cautious.

**disagreement:** The brief reports the probe "AS CORROBORATING fable AND AS CUTTING AGAINST B209's OWN PREMISE." Both reports exceed the data, and the second is the worse overreach: absence of churn in a regime with no churn opportunity is not evidence about churn. The script's own printed interpretation (lines 128–137) makes the same overclaim and should be softened to name the regime.

---

## Q3 — was the adoption testing sufficient?

**verdict:** Sufficient for the help-flag property (measured on all 6) and the differential rule (validated both ways); **insufficient for the run-to-completion property, and the weak point is not the 1-of-6 sample but the extrapolation of a per-file behavioural claim from it.**

**reasoning:** "Compiles and answers `--help` writing 0 bytes" and "runs to completion with all mutations RED and SHA-256-verified restore" are different predicates, and this repository's own record proves the gap: `a_falsifier_must_disagree_with_itself_2026-11-23.py` lines 20–23 record a mutation harness in this very session that compiled, was invoked — and exited at `REFUSED: the guard is RED before any mutation`, a startup refusal that compile + `--help` cannot see, caused by a file the author was not looking at. The repair touches exactly the header region (imports/guard) where a path or ordering slip produces that failure mode. The 5 unexecuted harnesses therefore carry an evidenced, nameable risk: silent inability to run, discovered only when next needed. Cost to close: 5 clone runs, bounded and known. Alternatively, state the adopted claim honestly as "1 of 6 verified to completion" and close the other 5 on first scheduled use. What the differential-rule testing did NOT cover: its two validations (discriminates on real guard, vacuous on unrelated guard) exercise verdicts 0 and 1 but not the **inverted-sense arm** (defect-present PASS / defect-absent FAIL, lines 154–156) — no known-answer test ever drove it.

**commands_run:** the record cited was read in-tree (`Read scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py`); the 6 repaired harnesses are not identifiable in this sandbox (fixer report not staged — `grep` for the fixer and declined-file list returned no report), so I could not run the missing 5 here and say so rather than simulate it.

**fix:** NONE deliverable here — the fix is an action: run the remaining 5 repaired harnesses to completion in a throwaway clone before the run-to-completion claim is recorded for 6.

**falsifier:** for the future action, the in-tree differential tool itself is the falsifier (each harness run with one mutation un-reverted must go RED); not executable in this sandbox absent the 6 filenames.

**what_would_refute_me:** the fixer's report naming the 6 files plus 5 clean completion runs — that would show the extrapolation happened to be safe (it would not show it was *justified*, which is the finding); or evidence that the repair transform provably cannot alter pre-mutation startup (e.g. it only inserts statements inside the `__main__` guard after all preconditions), which would reduce the residual risk below material.

**disagreement:** The brief asks "is the 1-of-6 sample the weak point?" — framing it as a sample-size question invites the answer "run more." The defect is categorical, not statistical: run-to-completion was *claimed for the batch* while *measured for one member*. 6 of 6 at one property and 1 of 6 at another were reported in a single breath, and the brief's own sentence structure ("a repaired harness RAN TO COMPLETION") elides the quantifier.

---

## Q4 — ledgered advisory line vs refusal

**verdict:** The deciding measurement exists and is cheap: ledger the existing advisory line's verdict-and-outcome per significant commit, and escalate to refusal on the first recorded lapse; **0 lapses in 9 ledgered significant commits is the stopping rule that vindicates the advisory**, because its Wilson interval then excludes the measured baseline regime.

**reasoning:** The predicate a hook can evaluate is already implemented — `hooks/pre-commit` asks `was_this_batch_reviewed_2026-11-22.py` (`panel_rounds_since_HEAD == 0`, with `what_is_a_significant_batch_2026-11-23.py` scoping significance). The missing piece is one append per commit: `(commit_id, rounds_since_prev, significant?, proceeded?)`. Define a **lapse** = line reported 0 rounds on a significant commit ∧ commit proceeded ∧ no round completed before the next commit. Derived decision rule, all intervals computed above: baseline (unledgered advisory) is **7/10 lapses, Wilson [0.397, 0.892]**. A ledgered-advisory run of **0 lapses in 9** gives Wilson [0, 0.299] — **disjoint from the baseline interval**, so the ledgered advisory demonstrably dominates the unledgered one on the named property (lapse rate) and refusal's cost (blocked legitimate commits, also visible in the same ledger) is unjustified under the simplest-sufficient standard. **Any lapse ≥ 1 in the window → adopt refusal**, the escalation the hook's own comment pre-commits to. This batch's data point (reported → board killed) is 0/1, Wilson [0, 0.794] — consistent with everything, decides nothing, and I verified that rather than assuming it.

**commands_run:**
```
python3 - <<EOF (statsmodels)
  → baseline 7/10: [0.3968, 0.8922]; candidate 0/9: [0.0000, 0.2991]; disjoint: True
  → this batch 0/1: [0.0000, 0.7935] (uninformative)
```

**fix:** NONE delivered — deliberately. The ledger append belongs in `hooks/pre-commit`, which cannot execute in this git-less sandbox, so an implementation here would be an addition no test can reach — the exact 11-times-measured defect class the additive standard names. The specification above is complete enough to implement and test where a `.git` exists.

**falsifier:** for the eventual implementation: commit twice in a throwaway clone with 0 panel rounds; the ledger must gain 2 lapse rows (defect-absent arm: commit after a recorded round → 0 lapse rows). Not executable here; stated per the one-shot rule.

**what_would_refute_me:** evidence that the 7/10 baseline commits were predominantly *insignificant* batches (the baseline would then overstate the lapse rate the ledger must beat, and the 0-in-9 threshold would be miscalibrated — recompute against the significant-only baseline); or a founder ruling that any single lapse of this class is intolerable regardless of rate, which collapses the measurement into immediate refusal.

**disagreement:** The brief offers this batch as "1 data point: the line reported, and the board was killed." As computed, 0/1 carries an upper bound of 0.794 — it is consistent with a regime that lapses four times in five. Citing it as support for the auditability framing is the same shape of overclaim as Q2's: a count too small to exclude anything, narrated as if it leaned somewhere.

---

## TERMINATION

**3 passes run.** Pass 1: read artefacts, reproduce baseline, construct and dynamically confirm the Q1 counterexample. Pass 2: fix, regression test, differential vacuity check, 825-script verdict diff, Q2/Q4 derivations with second and third routes. Pass 3: full-file re-run (13 passed, same 3 sandbox-only failures as baseline), re-read of the patched region, Q3 gap check against the in-tree record — **no new above-threshold findings**. Converged under §10: the one material defect found (Q1 decoupled conjunction, categories 1/4) is fixed, tested, and differential-verified; every residual finding is below threshold or handed over with its deciding measurement named.
`````

---

# PART 1 — THE BOARD-COST POLICY

## THE ADVISORY'S CENTRAL CLAIM IS FALSE, AND THE ERROR IS A CONFLATION

Measured over the project's own duration ledger, 113 determinate runs:
**mean 34.38 min, median 34.13 min, longest board ever recorded 55.22 min, and
0 of 113 boards exceeded 3 hours.**

<!-- figure: determinate boards | scripts/why_is_the_board_getting_slower_2026-11-23.py | 113 -->
<!-- figure: mean board minutes | scripts/why_is_the_board_getting_slower_2026-11-23.py | 34.38 -->
<!-- figure: longest board minutes | scripts/why_is_the_board_getting_slower_2026-11-23.py | 55.22 -->
<!-- figure: boards over 3 hours | scripts/why_is_the_board_getting_slower_2026-11-23.py | 0 of 113 -->

**EVERY FIGURE IN THIS BRIEF WAS RE-DERIVED BEFORE DISPATCH, AND THE FIRST
ATTEMPT WAS WRONG.** The producer resolved its repository root by counting
directory levels, so when run from a scratch directory `LEDGER.is_file()` was
False, `determinate_rows()` returned [] and EVERY FIGURE IN THE PREVIOUS DRAFT
OF THIS BRIEF WAS COMPUTED ON AN EMPTY SET. Re-pointed, it finds 112 rows,
matching `scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py`
exactly. The superseded values are named here deliberately so a reader who
remembers them can see which moved: 111 runs then 112, means 34.07 then 34.19,
longest 52.4 then 52.38. THE FIGURES MOVE ON EVERY BOARD -- batch 12 landing
mid-preparation moved all 9 again -- so they are SYNCED FROM THE PRODUCER
immediately before dispatch rather than typed.

The 3.13 h figure belongs to the FULL SUITE, 18,419 tests, a different
instrument run rarely. The BOARD is 329 guards, about 5,532 tests. **The
advisory treats the 2 as 1**, and that conflation sits under its whole argument.

**ITS LAYERING RECOMMENDATION IS ALSO PARTLY ALREADY BUILT.** 3 layers exist: a
pre-board ladder derived from the staged diff (35 to 44 guards, about 5 min,
used 4 times on 2026-11-23), the board (about 47 min today), and the full suite
(3.13 h). What the advisory adds is a rule for WHEN each is required.

## BUT THE FOUNDER'S CONCERN IS CORRECT, AND THE SHARPEST FINDING IS NOT IN THE ADVISORY AT ALL

**Window 2026-11-23: 12.75 h of board wall-clock in a 20.52 h span = 0.621398
of elapsed time.** So boards did dominate the day. 9 commits landed against 16
determinate boards = 1.7778 boards per commit; refused 7 of 16 = 0.437500,
Wilson [0.230987, 0.668214].

<!-- figure: day board share | scripts/why_is_the_board_getting_slower_2026-11-23.py | 0.621398 -->
<!-- figure: boards per commit | scripts/why_is_the_board_getting_slower_2026-11-23.py | 1.7778 -->
<!-- figure: day refusal rate | scripts/why_is_the_board_getting_slower_2026-11-23.py | 0.437500 -->

**AN ARGUMENT THIS BRIEF PREVIOUSLY MADE IS WITHDRAWN, AND IT WAS MINE.** The
earlier draft said the board count was "exactly what the measured refusal rate
predicts", so no board was wasted. That is an IDENTITY, not evidence: with
`r = refused/n` and `boards_per_commit = n/commits`, `1/(1-r) = n/(n-refused)`,
and the 2 are equal whenever `commits = n - refused` -- which holds because
every board that passes yields 1 commit. SymPy returns a difference of exactly 0
under that substitution, so the match CANNOT fail and establishes nothing about
waste. The question it was standing in for is whether each REFUSAL was
necessary, which is measurable and is answered below.

**5 OF 7 REFUSALS ON 2026-11-23 WERE AVOIDABLE WITH NO REDUCTION IN GATE
STRENGTH: 3.9875 h of the 5.5606 h spent on refusals.** 0.714286, Wilson
[0.358934, 0.917781], Clopper-Pearson [0.290421, 0.963307]. The breakdown:

- **3 of 7, 2.4006 h — THE LADDER ALREADY SELECTS THOSE GUARDS.** The
  diff-derived pre-board ladder selects 47 guards and 3 of the 5 distinct guards
  that refused today are in that selection. They refused anyway because the hook
  only VERIFIES a stage-0 snapshot; nothing compels the ladder to RUN. An
  existing, measured, useful mechanism that no caller reaches is the exact shape
  `additive-standard` names as a non-addition.
- **2 of 7, 1.5869 h — A CONCURRENCY ARTEFACT, NOT A DEFECT.** Exactly 1
  overlapping board pair ran today (05:15:12-06:02:59 and 05:16:27-06:03:53,
  overlap 46.5 min) and BOTH refused naming the same guard,
  `test_the_parked_file_regenerates_without_losing_him_2026-10-17.py`. That
  guard calls `blocker_triage.park()`, which refuses while a board runs. The
  detector excludes its OWN process chain, so a lone board passes; 2 concurrent
  boards each detect the other. `park()` is the only function that raises, and
  of the 3 guards that call it, 2 already use the `CDSFL_BT_BOARD` seam -- the
  2 that test the interlock. Exactly 1 was unprotected, and it is the one that
  failed.
- **2 of 7, 1.5731 h — would need a WIDER ladder selection**, being state
  guards the diff does not name.

**ALL 5 DISTINCT NAMED GUARDS ARE GREEN NOW**, and together they run in
155.41 s = 2.5902 min, against refusing boards whose mean duration was
2859.71 s = 47.66 min, 95 per cent t-interval [45.82, 49.50] min.

**THE GROWTH IS REAL AND IS THE ADVISORY'S ONE STRONG POINT.** On 2 agreeing
routes, scipy `linregress` and statsmodels OLS agreeing to 1.33e-15: **slope
1.6606 min/day, p = 2.251202e-22, R^2 = 0.5753, 95 per cent CI on the slope
[1.3952, 1.9260] min/day.**

<!-- figure: growth slope min per day | scripts/why_is_the_board_getting_slower_2026-11-23.py | 1.6606 -->
<!-- figure: growth R squared | scripts/why_is_the_board_getting_slower_2026-11-23.py | 0.5753 -->

**SO THE ADVISORY DESCRIBES THE PROJECT'S NEAR FUTURE WHILE MIS-DESCRIBING ITS
PRESENT. The honest limit: R^2 = 0.5753 explains a little over half the
variance, so the growth is established and no dated projection is a forecast.**
A WINDOW NOTE, because the 2 are easy to conflate: 6 refusals among boards
STARTING on 2026-11-23 and 7 among boards ENDING on it, 1 having begun on
2026-11-22. Both are correct for their window.

---

## Q1. SHOULD THE BOARD BE RESERVED FOR MILESTONES, GIVEN THE LAYERS ALREADY EXIST?

The pre-board ladder already selects the guards a staged diff puts at risk, runs
in about 5 min, and caught 12 failures on 2026-11-23 that would otherwise have
cost whole boards. **The question is therefore not whether to build a cheap
layer but whether the ladder is strong enough to REPLACE a board for ordinary
batches.**

**WHAT ARGUES AGAINST IT, from this project's own record.** The ladder derives
its set from the diff, so it is blind to any guard the diff does not name. On
2026-11-23 a guard that was RED AT HEAD -- `test_help_never_acts_2026-09-11.py`
-- let a batch land, because it is ADVISORY and off the board entirely. A
selection-based layer inherits every blindness of its selector.

**THE QUESTION.** Is a diff-derived ladder a sound substitute for a full board
on an ordinary batch, and what class of regression would it structurally miss?
Name the concrete failure your answer permits.

## Q2. WHAT IS DRIVING 1.6606 MIN/DAY, AND CAN IT BE FIXED RATHER THAN ROUTED AROUND?

**PART OF THIS IS ALREADY MEASURED AND 1 HYPOTHESIS IS REFUTED.** The
leading candidate -- that guards each re-walk a growing `scripts/` directory
-- was measured: caching that walk saves about 10.25 s, which is 0.0036 of a
47 min board, and the timing interval straddles 0. The cause is therefore
NOT identified, and that is the honest state.

**This is the question I most want answered, because loosening the gate treats
the symptom.** If the growth is archive-parametrised tests whose cost scales
with the experimental archive, that is fixable at source and the policy question
largely dissolves. If it is irreducible breadth, the policy question is real.

The board emits `--durations=25` on every run, so per-test cost is already
recorded rather than needing to be guessed.

**THE QUESTION.** Decompose the growth. Is it (a) more guards on the list, (b)
existing guards getting slower as the archive grows, or (c) something else?
Give the decomposition with its producer.

## Q3. BOARD BEFORE AN EXPERIMENT, AFTER, OR BOTH?

The founder asks directly. **My position, for falsification:** BEFORE, and not
both -- unless the experiment changed code. An experiment run on unverified code
can waste far more than a board costs; an experiment that only produces data
leaves the code untouched, so a post-board re-verifies bytes nobody altered.

**THE QUESTION.** Is that right? The case I can see against it is that an
experiment's own harness may write code or configuration during a run, in which
case "did the code change" is itself a measurement rather than an assumption.

## Q4. IS A THRESHOLD OF 25 TO 30 CHANGES SAFE?

The advisory recommends a full board only after about 25 to 30 distinct
non-trivial changes accumulate. **Measured against today, a batch is 10 to 12
items**, so that threshold means roughly every 3rd batch is boarded.

**WHAT ARGUES AGAINST IT.** This project's record is that a gate which stops
refusing stops being consulted, and that a guard off the board drifts in
silence -- demonstrated the same day by a guard red at HEAD that no board ran.

**THE QUESTION.** Is a count the right threshold variable at all, or should it
be a PREDICATE over what the diff touches? State a predicate a hook could
evaluate.

---

## PRODUCE A FIX, AND TEST IT

A finding without a fix is incomplete, and a fix without a falsifier the seat
has EXECUTED is a hypothesis. Report the exact command and its output verbatim.
**Deliver your fix as a file.** Write it INTO the sandbox repository tree
at its real path. A fix described in prose is not delivered, and a fix
written to scratch space is destroyed at teardown: rounds 5 and 6 on
2026-09-10 returned 0 source files for exactly that reason while both
seats reported working code.

**Use `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py`** on any
falsifier you write, or say why it does not fit.

**Where more than 1 repair is in play, composability is a CLAIM THAT REQUIRES A
MEASUREMENT** -- compose only on demonstrated dominance over each part alone,
and prefer the single fix where it performs as well.

## WHAT WOULD REFUTE YOU

State what evidence would overturn your own answer. **And state explicitly
whether you think the external advisory should be adopted, rejected, or adopted
with the corrections above** -- the founder has asked that question and has not
decided it.

## OUTPUT SHAPE

For each of Q1 to Q4: `question`, `verdict` in 1 sentence, `reasoning` naming
the instrument you ran, `commands_run` verbatim, `fix` as a repository-relative
path or NONE, `falsifier` with the result of EXECUTING it,
`what_would_refute_me`, and `disagreement` -- your strongest disagreement with
this brief's framing, including with any figure in it. Mandatory, may not be
empty.

**Do not converge.** Disagreement is preserved as information.

## TERMINATION

Stop when a further pass produces no new above-threshold findings and state how
many passes you ran. A finding is above threshold if missing it could cause a
real-world failure, an unsafe condition, or a wrong decision by the founder.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 67 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_joint_b12_boardpolicy_20261123T201748Z) -->

**6 passes.** Sandbox caveat stated once: no `.git`, so every git-derived figure in the brief (`9 commits`, `boards per commit`, `3 of 5 refusals in the ladder's selection`) is unreproducible here and I substituted what the ledger and the hook themselves carry. Both fixes are in the tree; both falsifiers DISCRIMINATE. Wolfram ran (local Wolfram Engine, exit 0, no `Name::tag`, no `$Failed`).

---

## QJ — THE OTHER SEAT

**Where `cc2`'s strongest claim fails.** Its Q2 verdict — *"not evidence at all: it is a function of `--interval`, a free parameter"* — is **right about the mechanism and mis-filed in its conclusion**, and its own table refutes its own framing.

Derived: at k=0 the Wilson upper bound is exactly `z²/(n+z²)`, a function of **n alone**. `cc2` then writes *"A fifth of the observation time produced a tighter bound than yours… An interval that narrows as you look less is measuring the observer."* But 19 pairs over 20 s gave 0.168179 and 14 pairs over 106 s gave 0.215311 **because 19 > 14**, not because the window shrank — `z²/(19+z²) = 3.84146/22.84146 = 0.168179`, and duration does not appear. `cc2`'s own three rows (14 / 53 / 1060 pairs, *same* 106 s run) say so explicitly two paragraphs earlier. The bound narrows as you **poll more**, at any duration. So the rhetorical framing mislocates the fault, and the real fault is the one `cc2` *also* states and proves on `classify`: the denominator is poll-pairs, not opportunities. That half is correct, executable, and **sharper than my blind answer** — I said "wrong population/regime"; "the denominator is not a risk set" is the same defect stated as a predicate you can toggle. **I adopt it over my own framing.**

But "not evidence at all" is wrong as a classification. `z²/(n+z²)` *is* a valid 95% upper bound on a well-defined quantity: P(a consecutive poll pair exhibits a full replacement). That quantity is design-dependent and nobody cares about it — which makes this a **wrong-estimand** error, not a non-evidence error. The distinction is not pedantic: `cc2`'s own prescribed repair ("the denominator is observed set-change events") is itself a bound of exactly the same family, so if the first is "not evidence" the second cannot be evidence either. The admissible statement is: valid bound, mis-specified estimand, not invariant under the sampling design.

**Does "this batch is itself 1 data point is wrong in the direction that favours the line" survive my reading?** Partly — as a hypothesis, not as a finding. We agree on the bottom line (0/1 → Wilson [0, 0.7935], decides nothing; I computed that blind). `cc2` goes further: the board was killed by *a human primed by the prior round's 7/10*, so the batch was taken in a regime where the failure could not occur. That causal claim about attention has **no producer**, and `cc2` supplies none — which is the project's own `measured-rate-travels-with-its-script` violation, charged correctly elsewhere in the same reply. And it changes no decision: 0/1 already excludes nothing, so Hawthorne contamination is a second reason to discard a data point already discarded.

**One further genuine disagreement.** `cc2`'s Q4 rule — `lapse_rate × cost(unreviewed) > block_rate × cost(false block)` — is called *"a comparison of two measured quantities, not a preference."* It is not: both cost terms are unmeasured, and `cc2` concedes this later (*"I have not measured them"*). Each side is one measured factor times one unmeasured factor. That is a preference wearing an inequality.

**Where I find no disagreement, and will not manufacture one.** Q1: `cc2`'s case `C` (bare `__file__` sibling, no derived name) and my `ATTACK2` are the same counterexample to the same unjoined conjunction; we reached it independently and converge. Q3: `cc2`'s disagreement paragraph states the coverage framing I argued for. Converged on both.

---

## Q1 — SHOULD THE BOARD BE RESERVED FOR MILESTONES?

**question** Is a diff-derived ladder a sound substitute for a full board on an ordinary batch, and what class of regression would it structurally miss?

**verdict** **No** — the ladder is selection-by-literal-path, and **68 of 332 board guards (0.2048) derive their subject set at runtime**, so for a *newly added* member of such a population the selector returns nothing; I executed the real selector on one new file and it selected **0 guards**, including the guard that decides the case.

**reasoning** Instrument: the real `guards_naming` / `board_guards` imported from `scripts/which_guards_does_this_commit_risk_2026-11-22.py`, plus an AST-free source scan of all 332 board entries. `guards_naming` credits a guard iff the changed path or its basename appears **in the guard's text**. A guard that globs its population (`.glob`/`rglob`/`iterdir`/`os.walk`) contains no literal member path, so a new member cannot select it — while being exactly the member it exists to judge.

The concrete failure my answer permits, executed: stage one new producer. The ladder runs nothing; `test_help_is_answered_2026-09-11.py` is on the board and is **not** selected. A ladder-only commit of a new script whose `--help` performs its measurement therefore lands green — the 54,480-byte record class the help ratchet exists to prevent. 45 of the 68 glob `scripts/` or `bench/tests/` specifically.

Note the asymmetry that makes this worse than a coverage gap: those same population-quantified guards are the **expensive** ones (below), so a cost-driven policy routes around precisely the guards that cost the most *and* are structurally unreachable by the cheap layer.

**commands_run**
```
python3 - <<EOF   # real selector, one newly added file
staged (new file only)      : ['scripts/a_brand_new_producer_2026-11-23.py']
guards naming it            : 0
DECIDING (ladder would run) : 0 []
is the --help population guard selected?  False  (on the board: True )
EOF
python3 - <<EOF   # population scan over the real board list
board entries           : 332
population-quantified   : 68 = 0.2048
  globbing scripts/ or bench/tests/ : 45
EOF
```

**fix** NONE for the selector. Crediting all 68 on every added file costs the Sep/Oct heavy guards and I have no measurement that it beats the board it would replace; under the additive and simplest-sufficient standards I decline to ship it. The answer to Q1 is a policy answer: do not substitute. My delivered fixes are at Q2, where the measurement that *would* decide the policy was being destroyed.

**falsifier** The selector demonstration above is executable and repeatable but is not a differential falsifier: there is no defect to toggle, since the selector is behaving as designed and the blindness is a property of selection itself. I say so rather than force one; `a_falsifier_must_disagree_with_itself_2026-11-23.py` would correctly refuse it as vacuous (its own case 2).

**what_would_refute_me** A board guard set in which every population-quantified guard also enumerates its members statically — then a diff names them and the selector reaches them. Measured 68 of 332 today. Or a selector amendment that treats *added* paths as risking every guard globbing their parent directory, with a measurement showing the resulting set costs materially less than a board while catching the 2026-11-23 refusals.

**disagreement** The brief frames Q1 as ladder **strength**. The deciding property is **reachability**, and it is not a matter of degree: no amount of ladder tuning reaches a guard whose population the diff cannot name. Second, the brief's "3 of the 5 distinct guards that refused today are in that selection" rests on `staged()`, which has no input in any seat's sandbox — it is a figure no seat can check, and it is load-bearing for the brief's "5 of 7 refusals were avoidable".

---

## Q2 — WHAT IS DRIVING 1.6606 MIN/DAY?

**question** Decompose the growth: (a) more guards, (b) existing guards getting slower, or (c) something else. Give the decomposition with its producer.

**verdict** **(b), and by a factor of 2 over (a)** — over the window the ledger actually covers, board time grew **4.3357×** as guard count grew **1.4310×** and per-guard cost grew **3.0298×**; and the one instrument that could attribute it further — the board's own `--durations=25` table — **was being generated and `rm -f`'d 15 lines later on every one of 113 boards**, which is my headline finding and is now fixed.

**reasoning, four instruments.**

*1. A rival hypothesis, tested and refuted.* The regression pools passing and refusing boards. Refusing boards are **longer** by 3.2589 min (p = 0.0212, Welch t = 2.0920, p = 0.0388), but adding the refusal indicator moves the time slope only 1.6606 → 1.6395 (R² 0.5753 → 0.5954). Refusal composition is not the confounder.

*2. A second rival, also refuted.* The ledger's `seconds` is the **whole hook**, not the board, so the decomposition's numerator could have been dominated by stage-0 repairs. The one retained board log (`.cdsfl_tmp/board_census.txt`, 2026-11-21) ends `34 failed, 5129 passed, 27 skipped, 47 errors in 2615.21s (0:43:35)` against a hook mean of 43.7 min = 2622 s for that day's 3 rows → the guard pytest is **0.997** of the hook. The numerator is sound.

*3. The decomposition, now with a producer.* The hook records its `guards` covariate on only **26 of 141** rows, all at 330–331, i.e. **zero variation** — so the series the decomposition needs cannot be read off the ledger at all, which is why the earlier hand decomposition had to reach outside it. I reconstructed the series from each board guard's own filename date and **validated it where ground truth exists**: on the 2 days the hook recorded `guards`, the proxy reads exactly +1, a constant offset that cancels in a ratio. Bias stated in the code in both directions (late additions counted early; removed guards not counted).

*4. The cause is localised, and it is not what "per-guard cost" suggests.* 19 board guards sampled by cohort, one pytest process each: 2026-09 (n=6) mean **8.13 s**, 2026-10 (n=6) **4.04 s**, 2026-11 (n=6) **0.80 s**. The newest cohort is **217 of 332 guards and the cheapest by an order of magnitude**; the single most expensive guard sampled is `test_help_is_answered_2026-09-11.py` at **38.21 s**, which walks the whole `scripts/` population. So "per-guard cost rose 3×" is a *mean* effect concentrated in a handful of population-quantified guards whose cost tracks the repository — not a diffuse slowdown, and **not** more guards. Honest limit: my cohort means project only ~672 s against a 2615 s board, so the heavy tail is under-sampled and this arm localises the cause without quantifying it.

Which is exactly why the `--durations=25` table matters, and why I stopped modelling and went to look for it. It is written only into `$_CDSFL_BOARD_LOG` (hook line 1238) and `rm -f`'d at line 1253. The reader B207 was wired to feed **already exists** — `scripts/which_tests_outlive_the_global_timeout_2026-10-18.py --durations LOG`, whose `read_durations` parses pytest's `12.34s call path::test` rows. B207 closed the half where nothing emitted the table and left the half where nothing can read it: the addition still reached nothing, the class this project has measured 11 times. §10 category 4, silent evidence loss.

**commands_run**
```
python3 scripts/why_is_the_board_getting_slower_2026-11-23.py
  guards on the board NOW: 332
  -- THE DECOMPOSITION, window 2026-11-08 to 2026-11-23, 5 boards at each end --
    board minutes      11.77 -> 51.02   = 4.3357x
    guards (PROXY)     232.0 -> 332.0   = 1.4310x
    per-guard minutes  0.050718 -> 0.153665 = 3.0298x
    arithmetic check   1.4310 x 3.0298 = 4.3357 (identity, verifies nothing)
    the larger factor over this window is PER-GUARD COST

python3 - <<EOF   # rival hypothesis: refusal composition
exit!=0 n=54 mean 36.69 min ; exit==0 n=59 mean 32.27 min
Welch t: statistic=2.0919693025062904, pvalue=0.038770564098326056
A slope 1.6606  R2 0.5753
B time slope 1.6395 (p=1.93e-22)  refusal coef 3.2589 (p=0.0212)  R2 0.5954
EOF

tail -1 .cdsfl_tmp/board_census.txt
34 failed, 5129 passed, 27 skipped, 3 warnings, 47 errors in 2615.21s (0:43:35)

python3 /tmp/cohort_probe.py        # 19 guards, one pytest each
2026-09    38.21s rc=0       test_help_is_answered_2026-09-11.py
2026-11     0.57s rc=0       test_the_co_author_trailer_is_not_doubled_2026-11-14.py
  ... cohort means 8.13s / 4.04s / 0.80s for 09 / 10 / 11

wolframscript -code 'z=Quantile[NormalDistribution[],0.975]; k=54; n=113; ...'
Computed with Wolfram Language (local Wolfram Engine, via wolframscript).
{0.3880285457255058, 0.569178424724315}      # == statsmodels [0.388029, 0.569178]
```

**fix** two files, delivered into the tree:

1. **`hooks/pre-commit`** (sha256 `9845736222adcc0d`, 85559 bytes) — a retention block marked `>>> CDSFL durations retention`, inserted **above** the `rm -f`, writing the durations rows plus a board stamp to `.cdsfl_tmp/board_durations/<stamp>_<pid>.log`. One file per board, because `read_durations` keys a dict by test id and appending boards into one file would have each silently overwrite the last — so a per-board path is the whole interface and **the existing reader is unchanged**. Every command redirected, group ends `|| true`, nothing read by the refusal path: it cannot fail a commit. `bash -n` clean; the pinned `no:cacheprovider` literal is byte-identical and still at line 1238, so all 4 anchors that count it still count 1.
2. **`scripts/why_is_the_board_getting_slower_2026-11-23.py`** (sha256 `f38b926aa21e362e`) — `board_guard_count()` now uses the `GUARDS="(.*?)"` expression **already in the tree** rather than a third regex; added `guard_count_series()` and `decompose()`; labelled the withdrawn `1/(1-r)` line as the identity it is; removed every volatile figure from the docstring.

**falsifier** both executed, both driven through `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py`:

```
--- scripts/the_durations_table_is_deleted_unread_2026-11-23.py
# extracts the retention block FROM THE REAL HOOK between its markers, runs it
# under `sh` in a TemporaryDirectory against a real pytest durations table, then
# feeds whatever it wrote to the REAL read_durations imported from the real reader.
  retained files             : ['20261123T203411Z_59488.log']
  rows the REAL reader parsed: 4
  board stamp                : # board at=2026-11-23T20:34:11Z exit=1 guards=2
  the durations table survives ... Defect ABSENT.          exit=0

  DEFECT PRESENT  exit=1    FALSIFIED-token=True  -> FAIL
                  | AssertionError: no durations retention block in the hook
  DEFECT ABSENT   exit=0    FALSIFIED-token=False  -> PASS
  target restored byte-for-byte : True
  DISCRIMINATES

--- scripts/the_board_count_must_match_its_own_subject_2026-11-23.py
  1. synthetic 3-entry GUARDS block -> 3 (must be 3)
  2. real hook: producer 332 vs independent block parser 332
  3. real hook: producer 332 vs the hook own grep -c 332
  4. decomposition 1.4310 x 3.0298 = 4.3357 vs total 4.3357  window 2026-11-08..2026-11-23
  5. volatile figures in the docstring: none                exit=0

  DEFECT PRESENT  exit=1    FALSIFIED-token=True  -> FAIL
                  | AssertionError: the synthetic block of 3 guards counted as 1;
                  |   the first and/or last entry is being dropped
  DEFECT ABSENT   exit=0    FALSIFIED-token=False  -> PASS
  target restored byte-for-byte : True
  DISCRIMINATES
```

On the first drive, falsifier B failed the defect arm by **absence** (`AttributeError: no attribute 'decompose'`) — the tool's own vacuity case 2 — so the count arms that had already detected the real defect never printed. Hardened with a `hasattr` guard and re-driven; it now fails on the count defect by name. Recorded in the file, because a falsifier that dies before reporting gives the right exit code for the wrong reason.

Regression: `test_help_is_answered` + `a_help_flag_must_not_mutate_the_tree` → **38 passed**, so both new scripts answer `--help` without acting. Hook-anchored guards → **1 failed, 51 passed, 2 skipped**; the one failure is `test_the_hook_is_the_live_hook`, which asserts on `git config core.hooksPath` and fails **identically against the pristine hook** (`1 failed in 0.29s`), i.e. the sandbox's absent `.git`. Hook restored to the fixed state after that baseline, verified by digest.

**Two fixes, and I make NO composability claim.** They touch unrelated artefacts, and under the founder's 2026-10-02 definition I have no measurement showing a composed repair beats either alone. Reporting that they do not interfere is the weak form he excludes, so I am not reporting it.

**what_would_refute_me** A real board whose retained durations table shows cost spread evenly across the 332 guards rather than concentrated in the population-quantified ones — then "existing guards getting slower" is diffuse, my localisation is wrong, and the policy question becomes real breadth. Equally: if the filename-date proxy is badly wrong because guards joined the board long after being written, the 1.4310× count ratio is understated and (a) may dominate after all; the proxy is validated at only 2 points and I say so in the code. And the retention block has never run inside a real `git commit` — only its verbatim text under `sh` against real pytest output. That is the limit of my evidence.

**disagreement** The brief states: *"The board emits `--durations=25` on every run, so per-test cost is already recorded rather than needing to be guessed."* **That is false, and it is the most load-bearing error in the brief** — the table was deleted one line after being produced, 113 times, and the falsifier above demonstrates it. The brief also asserts *"PART OF THIS IS ALREADY MEASURED"* on the back of it. Second: the brief's "The BOARD is 329 guards" is wrong on three agreeing routes (332); the producer said 330, the hook's own ledger recorded 331 at 20:04 before the list gained an entry at 20:06, and the brief says 329 — **four figures for one quantity**, the board's first guard invisible to all but one of them. Third: the brief's claim-4 decomposition ("guard COUNT 126 → 329 = 2.6111× times PER-GUARD 1.5385×") took its count ratio from a **wider window than its time ratio**, which is the whole reason count appeared dominant; over one window it is not, and the "decomposes EXACTLY with an identity check" reassurance is the same vacuous self-verification the brief withdrew for `1/(1-r)` — two instances of one error class in one artefact.

---

## Q3 — BOARD BEFORE AN EXPERIMENT, AFTER, OR BOTH?

**question** Is "BEFORE, and not both — unless the experiment changed code" right?

**verdict** Right in its ordering and **wrong in its "unless"**, which makes the post-board conditional on a predicate nothing evaluates; the repair is to make "did the code change" a *computed* digest comparison that costs seconds against a 47-minute board.

**reasoning** The brief names its own counter and then leaves it as an assumption. An experiment harness in this repository writes under `bench/logs/` and `.cdsfl_tmp/`, and the pre-commit hook itself contains stage-0 repairs that **rewrite tracked files and re-stage them** — the hook's own comment records that re-staging being added because repairs were "permanently one commit behind". So a run that is nominally data-only can move tracked bytes, and the brief's "unless" is exactly the case that cannot be assumed either way.

The predicate is cheap and already has all its inputs: digest the tracked code set before the experiment, digest it after, compare. Non-equal → the post-board is owed; equal → a post-board re-verifies bytes nobody altered, and the brief's reasoning holds. That is seconds against 2860 s, so the asymmetry is ~3 orders of magnitude and the measurement is strictly cheaper than the assumption it replaces. "Both" as a standing policy is the one answer the evidence excludes: it pays the 47-minute board for a hypothesis a digest settles.

**commands_run** No new execution for this answer; it rests on the stage-0 re-staging behaviour read in `hooks/pre-commit` and on the board-cost figures measured above (mean 34.38 min over 113 runs, latest 3313 s).

**fix** NONE. The digest comparison belongs in the experiment runner's entry and exit, which cannot execute in a git-less sandbox, so shipping it here would be an addition no test can reach — the 11-times-measured class. The specification is complete enough to implement and test where a `.git` exists.

**falsifier** Not applicable and I will not force one: the proposition is about which of two policies to adopt, not about a code state, so there is no defect to toggle and the differential tool would correctly refuse the run as vacuous.

**what_would_refute_me** Evidence that the experiment harnesses provably cannot write tracked files — then "did the code change" is answerable statically and the brief's "unless" is safe as written. Or a cost measurement showing the digest comparison is not cheap relative to a board, which would be surprising at 3 orders of magnitude.

**disagreement** The brief presents its own counter-case and does not resolve it, which leaves the policy resting on an unevaluated predicate — the same shape as Q2's "already recorded". A policy whose trigger nobody computes defaults in practice to whichever branch is cheaper to skip.

---

## Q4 — IS A THRESHOLD OF 25 TO 30 CHANGES SAFE?

**question** Is a count the right threshold variable, or should it be a predicate over what the diff touches?

**verdict** **A count is the wrong variable**, and the measured distribution shows why — 3 of 26 recorded attempts sit at exactly **24** staged files, one file below a 25 threshold, and splitting a commit is free; but the deeper finding is that **no cost ceiling exists anywhere in this system**, and the one number that looks like one is a monotone function of the quantity it would bound.

**reasoning** The hook records a `staged` covariate on 26 attempts: min 4, **median 14**, mean 21.0, max 69; **7 of 26 reach 25**. The distribution clusters at 4–6, 12–15, **24**, and 38–69. A threshold at 25 cuts between the 24 cluster and the 28 cluster, so three recorded attempts miss it by one file, and any author who prefers not to be boarded splits once. A gate whose trigger is free to avoid is the brief's own cited failure mode — "a gate which stops refusing stops being consulted" — reached by a different route.

The predicate a hook *can* evaluate, and it is a predicate over what the diff touches rather than how much: **board iff the staged set contains a file that any population-quantified board guard's population includes** — i.e. a new or changed member of a globbed set (`scripts/*.py`, `bench/tests/test_*.py`), **or** the staged set contains `hooks/pre-commit` or a guard file. That is precisely the 68-guard class Q1 showed a diff-derived selector cannot reach, so it routes the one case the cheap layer is blind to onto the board and lets the ladder decide the rest. Both inputs are already in hand: the staged list, and the glob scan I executed above.

**And the finding neither the advisory nor the brief contains.** `scripts/cdsfl_sv.py::commit_timeout()` is `max(300, 4 × max(seconds over the last 10 ledger rows))`. Today that is `max(300, 4 × 3313) = 13252 s = 3.68 h`. The only ceiling in the system **tracks the quantity it bounds** and therefore can never bind. Meanwhile the hook's own header states the limit as 11 minutes = 660 s, on the founder's reasoning that "a per-commit gate costing 11 minutes would be bypassed within a day"; the latest board is 3313 s = **5.02× that stated limit**, and the mean over 113 runs is 2062.8 s = 3.13×. Nothing refuses and nothing reports on it — by design: `what_the_commit_gate_actually_costs_over_time_2026-11-08.py` says in terms that it declines to refuse because the limit is **B103**, "which is his decision", undecided since 2026-11-08.

So the founder's finishing-risk question **is B103**, and the external advisory is a wrong attempt to answer it. The decision he is being asked for is not "loosen the gate" but "what bound, against what tier split" — and the overshoot against his own stated number is now 5.02×.

A necessary caveat on the brief's refutation of the advisory: "0 of 113 boards exceeded 3 hours" is measured on a sample **right-censored by a limit derived from that same sample**. It is a correct refutation of the advisory's present-tense claim (the observed max is 55.22 min, far inside 3.68 h, and 113 of 113 completed), and it is **not** evidence about where cost is heading, because the ceiling moves with the data. This project has the error class on record (`the_cap_was_measured_on_censored_data_2026-10-08.py`).

**commands_run**
```
python3 - <<EOF   # staged-file distribution from the hook's own covariate
rows with a staged count: 26
staged files per commit attempt: min 4 median 14 mean 21.0 max 69
attempts with staged >= 25 : 7 of 26
sorted: [4,5,5,6,6,6,6,6,6,6,12,12,13,15,15,15,24,24,24,28,38,49,49,49,53,69]
EOF
python3 - <<EOF   # the only ceiling in the system
ledger max over last 10 rows = 3313 s -> commit_timeout = max(300, 4*3313) = 13252 s = 3.68 h
hook stated limit 660 s; latest board 3313 s = 5.02 x the stated limit
EOF
```

**fix** NONE delivered, deliberately. The predicate belongs in `hooks/pre-commit`'s dispatch and needs a staged list and a commit to validate against; neither exists in a git-less sandbox, so an implementation here would be an unreached entry point. The glob scan the predicate needs is executed above and is the only part that required measurement.

**falsifier** For the eventual implementation: stage a new `scripts/*.py` with no other change and the predicate must demand a board (0 guards selected by the ladder, per Q1's executed run); stage a `.md` note alone and it must not. Not executable here; stated per the one-shot rule rather than simulated.

**what_would_refute_me** A measurement showing that commits are *not* split to avoid a threshold once one exists — then a count is cheap and adequate and my objection is theoretical. Or a founder ruling fixing the cost bound directly (B103), which makes the threshold variable a downstream detail. On the ceiling finding: evidence that some other mechanism does refuse on cost, which would mean `commit_timeout`'s self-sizing is irrelevant rather than load-bearing.

**disagreement** The brief's "Measured against today, a batch is 10 to 12 items" has no producer in this sandbox; the hook's own `staged` field gives a median of 14 files and a maximum of 69, so "roughly every 3rd batch is boarded" is derived from a figure that cannot be checked here against one that can. And the brief treats "0 of 113 boards exceeded 3 hours" as settling the advisory; it settles the present tense only, on a censored sample.

---

## THE ADVISORY: REJECT, WITH ONE ELEMENT ADOPTED

**Reject the central claim.** 113 determinate boards, mean 34.38 min, median 34.13, longest ever 55.22 min, **0 over 3 hours**. The 3.13 h figure is the full suite — a different instrument. The conflation sits under the whole argument, so the argument does not survive it.

**Reject the milestone recommendation.** It would substitute a selection-based layer that is structurally blind to 68 of 332 board guards, demonstrated by execution: one new file, 0 guards selected, the deciding guard not among them. Under the additive standard a removal needs a committed measurement showing the replacement dominates on a named property. None exists, and the measurement I ran points the other way.

**Reject the 25–30 count threshold** as the variable, on the measured distribution: three attempts at exactly 24, and splitting is free.

**Adopt one element: the growth is real and the advisory is the only party that named it as the live risk.** Slope 1.6606 min/day, p = 2.251202e-22, R² = 0.5753, 95% CI [1.3952, 1.9260] on two agreeing routes. R² of 0.5753 explains a little over half the variance, so the growth is established and no dated projection is a forecast. Its cause is now decomposed — per-guard cost 3.0298× against guard count 1.4310× — and localised to population-quantified guards, with the attribution instrument unblocked rather than inferred.

**And the question actually in front of the founder is B103, not the advisory.** The hook's own stated limit is 660 s; boards run at 5.02× it; the only ceiling in the system is `4 ×` the thing it bounds. That is the decision, it has been open since 2026-11-08, and it is answerable with the durations table that will now survive the next board.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 43 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_joint_b12_boardpolicy_20261123T201748Z) -->

All verification complete. Five delivered artefacts, three falsifiers executed, two driven differentially to DISCRIMINATES, all new producer-guard entries green (6 passed). Report follows.

---

# SEAT REPORT — joint round `panel_b12_20261123T170728Z`, batch 12

**Sandbox caveat, once:** no `.git` is staged, so the 4 environmental failures in `test_todays_producers_run` and `test_the_hook_is_the_live_hook` (`git config` exits 1) are identical before and after my edits — verified by running the pre-edit guard from a temp copy: 4 failed both ways, failure set unchanged.

---

## QJ — cross-examination of seat `cc2`

**On the orchestrator's first pressure point — "0.215311 is not evidence at all."** cc2's mechanism is right and *defeats my blind framing*; its epistemic filing overshoots, and the overshoot is derivable. My blind reply let the figure stand as "arithmetically correct but about the wrong population" — cc2 showed the number itself is instrument-relative, which is stronger, and its demonstration (14→149 poll-pairs under 10× polling, opportunities fixed at 0) is the decisive one. **But "not evidence at all" is strictly mis-filed.** Derived with SymPy and confirmed on the Wolfram kernel (local Wolfram Engine via `wolframscript`, exit 0): re-expressed as a bound on the event **rate per unit time**, λ(n) = n·z²/((n+z²)·T) is monotone *increasing* in n and saturates at z²/T — the free parameter cannot push it below a fixed, interval-invariant quantity. At n=14, T=106 s the rate bound is 0.028437/s, within 1% of the exact Poisson rule-of-three ln(20)/T = 0.028262/s (Wolfram Language: `{3.8414588/T, 0.02826163, 0.02843728, 58.298}`). So the run *does* carry evidence of a bounded kind — cc2 mis-filed it — **and simultaneously cc2's practical verdict survives intact**, twice over: (i) the invariant bound permits ≤ **58.3 full replacements per mean-length board**, i.e. it excludes nothing at the decision scale; (ii) my blind point stands that it is evidence about the single-pytest regime, not the board regime. Composed correctly: *inadmissible in the per-pair coordinate cc2 attacked; admissible but decision-vacuous in the invariant coordinate; wrong-population either way.* cc2's warning that "take more samples" manufactures false confidence is exactly right *in the per-pair coordinate*; in the rate coordinate more *polls* add nothing (saturation) while more *time* genuinely does — which is why the board-length run both seats prescribed is the measurement.

**On the second pressure point — "this batch is itself 1 data point" being wrong in the direction that favours the line.** cc2's claim survives my reading, and **here I reverse**. My blind reply computed Wilson [0, 0.794] on 0/1 and called the datum "consistent with everything, decides nothing." That arithmetic implicitly treated the datum as exchangeable with the 7-of-10 baseline trials. cc2's Hawthorne argument shows it is not: the condition the advisory must survive is "the line reports and nobody is primed," and this datum was generated under maximal priming, one round after the 7/10 measurement. Under non-exchangeability my interval is not wide — it is an interval for the wrong process, the same error class as Q2. So cc2's framing is the sharper one and mine was the weaker half of a shared point. One caveat, preserved as information: cc2's causal reading ("killed by a human primed by the measurement") is itself a plausible unmeasured mechanism — which is precisely why the ledger both seats specified is the repair: it makes future data points exchangeable by construction.

**Residual genuine disagreement (small, Q3):** cc2 holds the common-cause diagnosis makes 1-of-6 "far more informative than n=1 implies." Partly — but the record's own case 2 (a harness RED before any mutation, caused by a file the author was not looking at) is a *per-harness idiosyncratic* vacuity that no common-cause argument discounts. Both seats land on "run the 5"; I hold the residual risk is per-harness, not shared-mechanism, and the evidence for that is the project's own archived case. No disagreement is manufactured beyond this: on Q1 both seats found the same unjoined conjunction blind, and the Part 0 adoption record closes it.

---

# PART 1 — THE BOARD-COST POLICY

**Advisory verdict, asked for explicitly: REJECT as written.** Its central number is false by conflation — re-executed here: **113 determinate boards, mean 34.38 min, longest ever 55.22 min, 0 of 113 over 3 hours** (the 3.13 h figure is the full suite, a different instrument). Its layering recommendation is three-quarters already built. What deserves adoption is not in the advisory: the founder's underlying concern is real (day share 0.621398 reproduced), and the measured levers are (1) the avoidable-refusal waste — 5 of 7 refusals, 3.99 h, Wilson [0.359, 0.918] — and (2) the per-guard growth, which I decomposed and delivered the instrument for below. Fix those; do not loosen the gate.

## Q1. Ladder as substitute for the board on ordinary batches?

**question** Is a diff-derived ladder a sound substitute; what class of regression would it structurally miss?

**verdict** No — a selection-based layer structurally misses regressions whose guard predicate reads repository-global state the staged diff never names, and the brief's own day demonstrates the class.

**reasoning** The ladder's selector is the diff. Three guard classes are invisible to it by construction: (i) whole-tree invariant guards (ratchets, census guards — e.g. `test_an_unreached_producer_set_cannot_grow_2026-11-08.py` fires on an *addition elsewhere*); (ii) date-driven freshness gates that go red with an empty diff; (iii) cross-file coupling where the touched file is an *input* to an untouched guard's predicate. The concrete failure my answer refuses to permit: a batch touching only `scripts/` lands via ladder while a board-only invariant guard is red — exactly the 2026-11-23 red-at-HEAD case — and the defect conflates with 2 more batches before the next "milestone" board, multiplying bisection cost; that is the 3-hour-suite problem recreated one layer down. The right wiring is ordering, not substitution: **compel the ladder to run before the board** (today 3 of 7 refusals, 2.4006 h, named guards the ladder already selects — the hook only verifies a stage-0 snapshot, so an existing measured mechanism has no caller, the exact non-addition shape). Counterfactual, computed: removing the 2 concurrency refusals (seam fix already landed in the staged guard, line 340) and converting the 3 ladder-detectable refusals to 5-min ladder refusals drops the day share **0.6213 → 0.4392** with zero reduction in gate strength.

**commands_run** (verdict lines; full outputs above)
```
python3 scripts/why_is_the_board_getting_slower_2026-11-23.py
  → 113 boards, mean 34.38, longest 55.22, 0 of 113 > 3 h; day share 0.621398; 7 of 16 refused
statsmodels: 5/7 Wilson [0.358934, 0.917781], Clopper-Pearson [0.290421, 0.963307]
counterfactual: share 0.6213 -> 0.4392
```

**fix** NONE for the ladder wiring itself — it belongs in `hooks/pre-commit`'s dispatch path ahead of the board, and the compelled-run step cannot be executed in a git-less sandbox; shipping it untested would be the 11-times-measured unreached-addition class. The specification is one sentence: before the board, run the ladder selection; refuse on ladder-red without starting the board.

**falsifier** Not applicable to a declined fix; the counterfactual arithmetic above is re-executable.

**what_would_refute_me** A measured ladder selection rule that provably supersets every guard whose predicate reads any touched path — that would make substitution sound for diff-local batches and my "never substitute" too strong. No such rule exists today; the red-at-HEAD case is its standing counterexample.

**disagreement** The brief frames Q1 as substitute-or-not. The measured answer is neither: the ladder's value today is as a *compelled pre-filter*, and the brief's own avoidable-refusal breakdown (its sharpest finding) already proves it — 2.4 h of board time was spent discovering what 3 ladder runs would have found in ~15 min.

## Q2. What drives 1.6606 min/day, and can it be fixed rather than routed around?

**question** Decompose the growth; give the decomposition with its producer.

**verdict** The current growth is **(b) — existing guards getting slower** — demonstrated inside a window where the guard count is constant, and the instrument that would attribute it per guard was being **emitted and deleted on every board**; both the measurement and the retention repair are delivered, executed, and differentially falsified.

**reasoning** The ledger supplies a controlled experiment the brief did not use: since 2026-11-22T20:13Z the hook records a `guards` field, **constant at 331 across all 19 determinate boards**. Within that window, duration still grew at **5.4980 min/day, p = 5.833e-03, R² = 0.3687, 95% CI [2.0779, 8.9181]** (scipy linregress and statsmodels OLS agreeing to 1.42e-14; Spearman ρ = 0.4404, p = 0.059 — the rank route is marginal at n=19 and I print it rather than hide it). Guard-count growth is held at zero by the data, so hypothesis (a) is excluded *for the current regime*; the recent per-guard slope is ~3.3× the historical blended 1.6606. Secondary route, same direction: retained 2026-11-17 logs show ~5106 tests in 2688 s versus the census's ~5190 in ~3100 s — tests +1.6% while time +15%, so per-*test* cost moved too. **The structural finding:** B207 wired `--durations=25`, but the table lands in `$_CDSFL_BOARD_LOG`, which the hook `rm -f`s after capturing `$OUT`, and no grep reads the durations section — 0 persisted tables exist anywhere in `.cdsfl_tmp/` (all 6 retained logs predate B207). The attribution evidence streams once to stderr and dies. Fixable rather than routed around: with tables retained, one board names the growing guards and the archive-parametrisation hypothesis is decided per guard instead of modelled. Urgency, computed: at 5.498 min/day the board crosses 60 min in **2.2 days**; at the blended 1.6606, 7.4 days.

**commands_run**
```
python3 scripts/the_growth_is_per_guard_not_more_guards_2026-11-23.py
  → 19 boards, guards CONSTANT at 331, slope 5.4980 min/day p=5.8330e-03 CI [2.0779, 8.9181]
  → attribution coverage: 0 persisted durations tables for 19 boards
python3 scripts/the_durations_table_must_survive_the_boards_cleanup_2026-11-23.py
  → OK: helper persists the table (executed, 3 arms); hook calls it above the rm   exit=0
sh -n hooks/pre-commit → parses
python3 -m pytest -q bench/tests/test_todays_producers_run_2026-11-22.py -k "..." → 6 passed
```

**fix** Three repository files, one mechanism plus one measurement: `hooks/board_durations_persist.sh` (new; POSIX helper, `stage0_restage.sh` precedent, fail-open because telemetry must never refuse a commit — a silent stop surfaces as a coverage figure, not a blocked batch); `hooks/pre-commit` (persistence call inserted between the `$OUT` capture and the `rm -f`, below `CODE=$?`); `scripts/the_growth_is_per_guard_not_more_guards_2026-11-23.py` (the producer). All wired: both scripts execute on every board via `PRODUCERS` in `bench/tests/test_todays_producers_run_2026-11-22.py`, where the second prints `FALSIFIED` and exits 1 if the hook ever stops calling the helper. No composability claim: helper+hook-call are one fix (either alone is inert); the producer is a separate measurement artefact.

**falsifier** `scripts/the_durations_table_must_survive_the_boards_cleanup_2026-11-23.py` — executes the real helper bytes in /bin/sh (3 arms: persist, append-twice, table-less log appends nothing) and checks the hook's call sits above the `rm` (positional, named as such — the hook cannot execute without `.git`; same compromise as B207's own 4 anchors). Driven through the differential rule, defect copy = hook as dispatched:
```
DEFECT PRESENT  exit=1  FALSIFIED-token=True  -> FAIL
DEFECT ABSENT   exit=0  FALSIFIED-token=False -> PASS
target restored byte-for-byte : True
DISCRIMINATES
```
Hook-anchoring guards re-run post-edit: 28 passed, 1 environmental (`git config` in git-less sandbox).

**what_would_refute_me** The next real board's persisted table showing the top-25 flat against an older table — that would mean the growth hides in the un-persisted tail below the cap, and the cap (120 lines, stated, not silent) needs raising. Or a within-window confounder: if the 19-board window's later boards systematically ran under heavier machine load, the 5.498 slope is contention, not code — the per-guard tables decide that too, because contention inflates uniformly while parametrisation growth inflates named guards.

**disagreement** The brief's sentence "per-test cost is already recorded rather than needing to be guessed" is **false as stated**: it is *emitted*, then destroyed — `rm -f "$_CDSFL_BOARD_LOG"`, with no reader of the durations section in between. Recorded-and-kept is the property that matters, and it held for 0 of 19 boards. Second figure disagreement: the brief's "329 guards" and the producer's "330" are both a systematic −2 — `board_guard_count` full-line-matched the whole hook, missing the quote-adjacent first and last entries of the `GUARDS="..."` assignment (true count at dispatch: 332; ledger's runtime count 331 predates batch 12's addition). Repaired in the producer with a 2-route agreement assertion; falsifier `scripts/the_guard_counter_must_count_the_edge_entries_2026-11-23.py` (synthetic 3-entry fixture — the defect shape as input data, not a retyped target) drove to **DISCRIMINATES**, target restored byte-identical. Below threshold — no conclusion moved, constancy was never in doubt — but three circulating values for one figure is how a brief's numbers drift.

## Q3. Board before an experiment, after, or both?

**question** Is "before, and not both unless the experiment changed code" right?

**verdict** Before always; after **conditionally, with the condition measured, not assumed** — and the measurement already exists in this project's idiom: a tree digest taken before and after the experiment, with the post-board required iff the digests differ.

**reasoning** The brief's own counter-case is correct and decides the shape: an experiment's harness may write code or configuration mid-run, so "did the code change" is an observable, not an assumption. The instrument is the restore-verification pattern already proven here (SHA-256 over the file set) — with one lesson from this repository's own record applied in reverse: the falsifier-tool docstring's case 3 records before/after hashes reading IDENTICAL while 13 writes occurred, *because the harness restores what it mutates*. For the post-board question that behaviour is exactly what you want to detect as **clean**: a harness that restores byte-identically has left nothing for a post-board to verify; one that leaves any tracked byte, new file, or config/hook change behind triggers the post-board mechanically. Digest scope must include `hooks/`, `configs/`, and untracked additions — experiments run in the live repo, where read-only staging does not protect the tree.

**commands_run** None beyond reading the in-tree record cited; this is a decision-procedure question and the arithmetic-free predicate above is the deliverable.

**fix** NONE — the digest predicate needs a real working tree and belongs beside the experiment runner; shipping it here unreached is the measured defect class. Specification: `digest := sha256 over sorted (path, sha256(content)) for all non-ignored files; post_board_required ⇔ digest_pre ≠ digest_post`.

**falsifier** For the eventual implementation: run an experiment harness rigged to drop one byte into `configs/` — the predicate must demand a post-board; run a pure-data experiment — it must not. Not executable here; stated per the one-shot rule.

**what_would_refute_me** An experiment class whose *data outputs* feed a subsequent board's guards (archive-parametrised guards reading `experimental_notes/`) — then even a byte-clean code tree changes the next board's behaviour, and the digest scope must widen to the notes the guards read, or the "after" board is owed on data grounds. Given Q2's finding that archive growth is the live growth suspect, this refutation is plausible — which is why the digest scope is declared, not implied.

**disagreement** The brief's position needs one amendment, not refutation: "unless the experiment changed code" smuggles in self-report. The project's own standard — tools decide, not votes — applies to its own workflow here: the exception clause must be a digest comparison, never a recollection that nothing was touched.

## Q4. Is a 25–30-change threshold safe?

**question** Is a count the right threshold variable, or should it be a predicate over what the diff touches?

**verdict** A count is the wrong variable on this project's own evidence — it is blind to *what* changed, and the day's record shows risk concentrates by touched surface, not by item count; the hook-evaluable predicate is below.

**reasoning** Two measured facts against the count: (i) every-3rd-batch boarding leaves up to ~2 batches of conflated unverified changes, and the same day's record shows a guard red at HEAD drifting precisely because nothing ran it — a gate that stops refusing stops being consulted; (ii) the economics the advisory computed from a 3.13 h board are off by 5.5× (mean 34.38 min), so the premise forcing rationing is false before the threshold is even designed. The predicate a hook can evaluate, in refusal order: **board REQUIRED iff** the staged diff touches `hooks/`, `bench/` (the measurement machinery — §10 category 3 surface), any `scripts/*.py` imported by a board guard, or any path read by a whole-tree invariant guard's predicate; **ladder suffices** for diff-local changes outside those surfaces; **no gate waived ever on count alone**. Every term is computable from the staged file list plus a static import walk — no judgement call at commit time. And the threshold question largely dissolves once the Q1/Q2 levers land: day share 0.44 with refusal waste removed, falling further when the growth cause is attributed and fixed at source.

**commands_run**
```
statsmodels/mpmath: advisory-premise ratio 3.13 h / 34.38 min = 5.46x
counterfactual share 0.4392 (from Q1); growth-to-60-min 2.2–7.4 days (from Q2)
```

**fix** NONE delivered — the predicate belongs in the hook's dispatch path with the Q1 ordering change and shares its untestability here; the specification above is complete enough to implement where a `.git` exists.

**falsifier** For the eventual implementation: stage a one-line change to `bench/` → predicate must demand a board; stage a one-line change to a leaf script imported by no guard → ladder must suffice. Stated, not executable here.

**what_would_refute_me** A ledgered stretch showing board-refusal causes distributed *uniformly* across touched surfaces — then surface-targeting buys nothing over a count and the simpler count wins under simplest-sufficient. Today's 7 refusals argue the opposite (2 concurrency, 3 ladder-selected guards, 2 state guards), but n=7 is one day; the refusal ledger the hook already writes (`why` field) accumulates the deciding data at zero marginal cost.

**disagreement** The brief asks whether 25–30 is "safe," accepting the advisory's framing that board frequency is the variable to ration. The measured record says the scarce resource was never board *runs* — it was board *time lost to avoidable refusals* (71.4% of refusal time, Wilson [0.359, 0.918]) and *time growth with an unread instrument*. Rationing frequency treats the symptom and reintroduces the drift the project has already paid for once.

---

## TERMINATION

**5 passes.** Pass 1: reproduced every Part 1 figure from the staged ledger (113/34.38/55.22/0-of-113, 0.621398, 7-of-16, slope 1.6606 all confirmed). Pass 2: found the constant-guard-count window in the ledger and the durations emit-then-delete gap; QJ derivations with SymPy/mpmath and Wolfram as second falsifier. Pass 3: delivered helper + hook call + producer + falsifier; differential drive → DISCRIMINATES; wired into the board's producer guard. Pass 4: re-read my own deliverables against anchoring guards (28 passed, 1 environmental); found the guard-count −2 defect across three circulating figures, fixed it, drove its falsifier → DISCRIMINATES. Pass 5: re-ran all 6 new guard entries (6 passed, 2.16 s) and re-read both edited hooks files; **no new above-threshold findings — converged under §10**, with every residual observation (Spearman marginality, the census's undated test count) stated beside the figure it qualifies rather than suppressed.

**Delivered, all in the repository tree:** `hooks/board_durations_persist.sh` (new), `hooks/pre-commit` (persistence call), `scripts/the_growth_is_per_guard_not_more_guards_2026-11-23.py` (new), `scripts/the_durations_table_must_survive_the_boards_cleanup_2026-11-23.py` (new), `scripts/the_guard_counter_must_count_the_edge_entries_2026-11-23.py` (new), `bench/tests/test_todays_producers_run_2026-11-22.py` (3 entries wired). Wolfram-derived values above are attributed to Wolfram Language (local Wolfram Engine).

**The stance the founder asked for:** reject the advisory; its central figure conflates two instruments and its remedy rations the wrong quantity. His concern is validated by measurement, and the two levers that answer it — compelled ladder-before-board ordering, and per-guard growth attribution now actually retained — keep the gate at full strength while returning, on today's numbers, ~29% of the day's elapsed time immediately and the growth curve once the first persisted table names its cause.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_joint_b12_boardpolicy_20261123T201748Z/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
