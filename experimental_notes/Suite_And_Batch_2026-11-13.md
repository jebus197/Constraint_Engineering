# The full-suite result of 2026-11-13 and the batch that followed it

2026-11-13, 08:15 GMT

## Summary

A full-suite run of `pytest bench/tests/ -q --netguard-strict` began at
04:10:53 GMT and ended at 07:30:43 GMT: **37 failed, 17,439 passed, 38 skipped,
1 error, 11,983.09 s (3:19:43)**. The batch of 21 anchored corrections that
followed was **refused 3 times** by `hooks/pre-commit`, and every refusal caught
something real. This note records the figures, the 2 genuine defects the suite
surfaced, what each refusal caught, and what the run does **not** establish.

## The figures, each interval on 2 independent routes

| quantity | value | Wilson 95% | Clopper-Pearson 95% |
|---|---|---|---|
| failure rate, this run | 37/17,514 = 0.002113 | [0.001533, 0.002910] | [0.001488, 0.002911] |
| failure rate, baseline | 4/15,908 = 0.000251 | [0.000098, 0.000646] | [0.000069, 0.000644] |

Wilson by `statsmodels.stats.proportion.proportion_confint` and by a NumPy
closed form, agreeing to 2.168e-19. Clopper-Pearson by statsmodels and by
**mpmath bisection on the exact binomial tails**, agreeing to 4.337e-19.
`mpmath.findroot` failed twice at these parameters — the tail sits ~1e-50 from
the start point — so bisection was used, which converges because the tail is
monotone in `q`.

Baseline: 2026-11-07, commit `aea4ec9b`, recorded on a **clean** tree.

## The comparison that must not be quoted as a verdict

Fisher exact odds ratio **8.4175**, p = **3.202246e-07**; chi-square with Yates
correction **22.0729**, p = **2.624865e-06** as a second route in the same
direction. Rate ratio 8.4018×.

**This is not like for like.** The baseline ran on a clean tree; this run carried
37 uncommitted paths, and **77 of 11,345** test functions reference working-tree
state. The 8.4018x ratio measures the tree as much as the code. This is precisely why
**B165, the clean-suite measurement entry, is NOT discharged** by this run — the
sequencing error was mine, and a second clean-tree run is still owed.

The figure that **is** comparable: the suite grew **15,908 → 17,514** tests in
6 days, **+1,606 (+10.0955%)**, 267.67 tests/day.

## Two genuine defects, both repaired

### 1. A producer of mine that no test reached

`scripts/what_share_of_the_suite_does_the_board_run_2026-11-13.py`, written
hours earlier, had **0 tests naming it** —
`test_an_unreached_producer_set_cannot_grow_2026-11-08.py` reported it. This is
the symmetric half of `additive-standard`, a defect confirmed 11 times in this
project's record.

Repair: `bench/tests/test_the_board_share_producer_holds_2026-11-13.py`, 6 tests
that **execute** the producer — `board_files()` checked against an *independent*
re-read of `hooks/pre-commit` rather than against the producer's own result,
`RECORDED` checked for both superseded memory figures, `_collect()` proved on a
single file and proved to return `None` rather than guess on a bad target.
Falsified with **5 mutations, 5 of 5 red**, producer restored byte-identical
(verified, not assumed).

### 2. The declared Python floor was broken in 2 committed files

`test_python_floor_2026-09-07.py`: *2 of 1977 modules do not parse on Python
3.11*. Both `scripts/the_reached_producer_mutations_2026-11-08.py:143` and
`scripts/the_windows_work_list_2026-11-12.py:232` split an implicitly
concatenated literal **inside an f-string expression** — legal under PEP 701 from
3.12, a `SyntaxError` on the 3.11 floor. Invisible on the 3.13 interpreter
everything is developed on.

Both fixed; both rendered strings verified **byte-identical**; both now compile
under `python3.11` and `python3`. Longest new line 91 chars against an existing
93-char line, and `ruff check` passes. Neither was tonight's work and neither was
in the agreed batch — said out loud rather than slipped in.

## The 3 refusals

| attempt | refused on | what it caught |
|---|---|---|
| 1 | 3 notes worse | task list 23→25, morning report 0→6, panel note 0→1 |
| 2 | 1 note worse | task list 23→24 |
| 3 | — | note ratchet **held** (23 at HEAD, 23 staged); full board ran |

**Refusal 1 exposed a hole in my own landing kit.** Raising an entry must reach
**2** surfaces: `experimental_notes/CDSFL_MASTER_TASK_LIST.md` *and*
`bench/ticket_store.py`. `apply_entries_b175_b178.py` reached only the first.
`scripts/morning_report_build_2026-10-12.py --check` refused: *NO TICKET ID for
task:B175 … the reader meets a code with nowhere to look it up*. This is
`feedback_closing_an_entry_means_closing_its_ticket_2026-11-01` inverted. Fixed
by running `scripts/harvest_tickets_2026-10-17.py --sources task_list`, which
**derives** each identity; `--check` then returned *46 derived items, every one
with authored detail*.

**Refusal 2 exposed a recorded trap I walked into.** Comparing note findings
before/after, I copied HEAD's task list to the scratchpad and measured **360
against 25**. `scripts/note_vagueness_lint.py` applies exemptions by **logical
path** and takes `--as <path>`, which `hooks/pre-commit:900` passes and I did
not. Using the hook's own method — `git show :path` and `git show HEAD:path`
into same-named copies, linted with `--as` — gave **23 → 24**, a delta of exactly
1, named in seconds. That is
`feedback_compare_lint_counts_like_with_like_2026-10-15` (same bytes, 24 against
353), hit again 29 days later.

**A new file's baseline is 0**, so any finding in it blocks —
`feedback_a_new_files_lint_baseline_is_zero_2026-11-04`, which caused 2 of 3
refusals here.

**The hook rewrites the task list mid-board.** Every attempt printed `refreshed
CDSFL_MASTER_TASK_LIST.md (diverged)`. That is B175's own subject caught in the
act 3 times in one morning. My edits survived all 3; the list stayed coherent at
322 entries, 0 problems, verified after each.

### The 3 writing fixes the refusals forced

Each **names its subject** rather than softening the sentence: B176 now names
`ps`; B174 now names *the FIGURE* a retraction contains; `.claude/CLAUDE.md` now
names *the 13*.

## A defect in what the report prints

**B141**'s title carries 2 clauses — the descriptor rule asked for twice, **and**
9 guard files off the commit gate — while its authored detail describes only the
second. So the item asked for twice appears in the morning report under a heading
about something else.

Found by eye, so it was turned into a measurement
(`a_detail_can_describe_half_its_title_2026-11-13.py`): of 38 entries with
authored detail, **20** have a 2-clause title; the predicate flags **6 of 20 =
0.300000**, Wilson [0.145477, 0.518973]. **All 6 were then inspected.**

> **Correction, same morning.** The first inspection used a *needle test* — does
> a distinctive word of the clause appear in the detail — and reported **3 of 20
> genuinely absent (B104, B141, B159)**. That was wrong, and wrong in the way the
> instrument it was checking is wrong: a needle test cannot see a paraphrase.
> Re-classified by **reading all 6 records in full**:
>
> | entry | verdict on re-reading |
> |---|---|
> | **B141** | **genuinely absent** — the detail is wholly about `test_precommit_gate_cost_2026-09-10.py`; the descriptor rule appears nowhere |
> | B159 | **stale, not absent** — the detail names the index headroom but carries the superseded 33 |
> | B104 | covered — *"he no longer sees the generated identifiers"* |
> | B168 | covered — the declaration being read by nothing is described |
> | B176 | covered — the union closing both blind spots is described |
> | B177 | covered — *"the suite runs under a network guard that refuses subprocesses"* |

So the corrected count is **1 of 20 = 0.050000**, Wilson [0.008881, 0.236131],
Clopper-Pearson [0.001265, 0.248733] — against the predicate's unchanged raw flag
of 6 of 20.

Both figures travel together: quoting only 6 multiplies the defect sixfold,
quoting only 1 hides that the instrument over-flags.

**B159's detail is mine and is stale rather than incomplete**: its title still
reads *33 memory files are linked from nothing … and the index has no room left*,
against a measured 0 unrecallable and 102 characters of headroom. It names the
right subject with a superseded value, which the amendment fixes.

## A falsifiable prediction for the clean run

Of 37 failures, **18** printed a traceback and **19** did not. Among the 18:
**9 predicted to resolve** on committing, **9 predicted to survive** a clean
tree — 9/18 = 0.500000, Wilson [0.290310, 0.709690]. No prediction for the other
19. Written to `prediction_clean_run.json` before the clean run.

An earlier version claimed **37 of 37** and was discarded unread: it classified by
searching the 4,000 characters preceding each summary line, sweeping in
neighbouring failures, so every item matched the single word `unreached`. The
unanimity was the giveaway. The repair was to stop writing a second parser and
call the triage's own `parse_failures` / `attach_reasons` — the same
`do_not_re_derive_a_population_a_helper_defines` lesson, arriving twice in one
night.

## What is still owed

- **B165**: a clean-tree full-suite run. `clean_run_b165.sh` refuses to start on
  a dirty tree (exit 2, verified unpiped) and watches for mutations on **2**
  samples — `git status --porcelain` for content and a `find -newermt` sweep for
  mtime — because 2 derived docs were rewritten at 06:27:11 and 06:27:22 and
  **4 hypotheses for the writer were each refuted by execution**.
- **B141**: amend the detail to carry both clauses, or split the entry. Splitting
  changes an identifier he may be tracking, so that is his call.
- **B159**: refresh its stale detail title (33 → 0, and the 102-character
  headroom). **B104 needs nothing** — re-reading showed its detail already
  carries the clause.
- The morning report was **deliberately unstaged**: its remaining findings are
  bare entry codes, which *is* B141's first clause.

Written under CDSFL note standard v1.9 (1 November 2026).
