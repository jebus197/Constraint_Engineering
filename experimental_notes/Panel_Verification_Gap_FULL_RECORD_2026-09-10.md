# Panel — the verification gap, FULL RECORD, unfiltered

Record written 2026-09-11T09:42:34+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

This round reviewed the DONE-evidence guard (task V1) and the note-lint commit guard (task V3) — the 2 mechanisms built in answer to the founder's question, verbatim: *"But you were supposed to have built a mechanism that ensured you could complete this work mechanically, and in such a way that it would survive future compaction events until all the work was complete. Did you do this?"*

The honest answer was half of it. The compaction half worked; the mechanical-completion half did not exist, because `task_list_markers.py` refused an entry only when its own 2 labels disagreed and **nothing compared a DONE marker against the repository**.

## What the round found

**BOTH SEATS RETURNED PARTIAL WITH 6 FINDINGS, AND THE WORST WAS A GUARD THAT SATISFIED ITSELF FROM ITS OWN LITERAL** — it read its own source, so the string it searched for was the string it contained. All 6 were repaired at `8f88650`, and round 4 re-ran the mutation against the repaired path: its first attempt FAILED TO APPLY because the docstring sentence wraps across lines, which is the SURVIVED-that-isn't trap, and the seat said so rather than reporting a pass. The corrected mutation went 1 failed, 80 passed.

**A CAUTION THAT APPLIES TO THIS ROUND.** Until task A20 landed on 2026-09-11, all seats shared ONE writable sandbox and ran concurrently. Agreement between seats here is not evidence of independence.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — the verification gap, its repair, and whether the repair is itself believable

## SECTION 1 — The question

**Does the new DONE-evidence guard actually close the hole that let 11 of 19 completion claims be overstated, or does it only move the hole?**

Context you need, and it is unflattering to the assistant that wrote it. On 2026-09-09 an assistant marked 19 entries DONE on `experimental_notes/CDSFL_MASTER_TASK_LIST.md`. On 2026-09-10, 18 adversarial agents re-checked all 19 by running the tests rather than reading the claims, with a second reviewer on every disputed one. **11 of 19 were overstated — 57.89%, Wilson [36.3%, 76.9%]** — 2 reviewers agreeing on every one. **One was not an overstatement but a live regression at HEAD**: task 6.3 sent every production run into a single shared directory, and its 8 tests were green throughout because every one built a fake config from `types.SimpleNamespace` instead of the real `ExperimentConfig`.

The founder's question was whether the task-list marker engine ensures the work can be completed mechanically and survives compaction. The compaction half worked. The completion half did not exist: `scripts/task_list_markers.py`'s `CONTRADICTORY` set refuses an entry only when its own 2 labels disagree, and nothing compared DONE against the repository.

Artefacts under review:

- `bench/tests/test_done_markers_carry_evidence_2026-09-10.py` — the new guard
- `scripts/task_list_markers.py` — the `MARKER` regex, now carrying an optional `evidence:` field, and `parse_entries`
- `experimental_notes/CDSFL_MASTER_TASK_LIST.md` — all 19 DONE markers now name evidence
- `hooks/pre-commit` — the note-lint guard, repaired for 2 demonstrated bypasses
- `bench/tests/test_note_lint_guard_2026-09-09.py` — both bypasses reproduced as tests
- `bench/reference_runner_v3.py` — `_find_or_create_logs_dir` and `_is_the_logs_dir_default`, the 6.3 repair

## SECTION 2 — Use the harness

**Form your answer by RUNNING the machinery, not by describing it.** A reply that reasons about these files without having executed them has not answered.

Instruments that bear on this, and what each is expected to say:

- **`task_list_markers.parse_entries`** — drive it. The `evidence:` field is OPTIONAL in the regex and REQUIRED by the guard. Show that an OPEN entry without it still parses and a DONE entry without it fails. If you can construct a marker that parses but should not, that is a finding.
- **The guard's 4 checks** — evidence named, file exists, file holds an asserting test, file inside the collected directory. **Try to defeat each.** A file that imports its assertions from elsewhere; a test function whose only assert is `assert True`; a path that starts with `bench/tests/` but resolves elsewhere via `..`; a marker whose evidence field contains a comment terminator.
- **`nu`, `sigma` and `S_k`** — the additive standard says an addition nothing reaches is not additive. This guard is itself an addition. Ask whether it is reached: does the suite collect it, and does it fail when the property is violated? The assistant ran 4 mutations and reports all caught; re-run them or invent better.
- **`gamma` and the two-sided gate** — not obviously implicated, and say so if you agree. If you can show a path by which a DONE marker's evidence affects convergence machinery, that is a finding the assistant missed.

## SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. A fix without a runnable falsifier that has been EXECUTED is a hypothesis.

**Report the exact command you ran and the exact output.** Where you propose a change, give file, line, old text, new text. Where you claim a test is weak, DEMONSTRATE it: mutate the source, assert the mutation applied AND that it lands on a line your fixture executes, run the test, report whether it went red. A mutation that applies to the file but not to the executed path reads as SURVIVED and is not one — that happened twice on 2026-09-09.

**Work in a sandbox copy. Do not modify the canonical tree.**

## SECTION 4 — What would refute you

State, before concluding, what evidence would overturn your own answer.

Specifically: if you judge the guard sufficient, name the class of overstatement it would still miss. If you judge it insufficient, name the cheapest addition that would close your objection, and say whether it is worth its cost.

## SECTION 5 — Output shape

- `verdict` — CONFIRMED / REFUTED / PARTIAL on whether the guard closes the hole
- `reasoning` — grounded in tool output you actually saw
- `findings` — each with file, line, severity, what is wrong, the fix, and the executed falsifier with its command and output
- `falsifier` and `falsifier_result` — the code you ran and what it returned
- `refutation_condition` — Section 4's answer
- `strongest_disagreement` — your strongest disagreement with THIS BRIEF's framing. Disagreement is preserved as information; do not converge toward the brief.
- `passes_run` — how many

## SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could let a false completion claim stand, or could break a live run. Do not generate findings for their own sake and do not police style.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 55 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_verification_gap_2026-09-10) -->

**verdict — PARTIAL.** The guard closes three of the four holes it claims, leaves the fourth open, and its own limit-statement test cannot fail.

## reasoning

Baseline: `python3 -m pytest -q bench/tests/test_done_markers_carry_evidence_2026-09-10.py` → `79 passed in 0.32s`. All 19 DONE markers name evidence. I ran ten mutations against the real guard.

**Caught (guard works):** evidence field stripped → RED; nonexistent file → RED; file with test functions but no real assertion → RED (`ast.get_source_segment` correctly excludes trailing comments, so my `# raises nothing` decoy failed to fool it — that check is *stronger* than the brief supposed). Deleting a marker line entirely is GREEN here but RED in `test_task_list_markers_2026-09-09.py::test_the_real_list_parses_every_entry` — closed at system level, not a finding.

**Not caught:** four.

`gamma` is unimplicated — `grep -rn "task_list_markers\|CDSFL_MASTER_TASK_LIST" bench/dm/` returns nothing; `.evidence` in `bench/dm` is a `Diagnosis` field, unrelated. I agree with the brief.

The 6.3 repair is **sound and mutation-verified**: neutering `_is_the_logs_dir_default` to reproduce the shared-directory regression leaves the original 8 tests at `8 passed, 3 deselected` — they genuinely cannot see it — while the 3 real-`ExperimentConfig` tests added on 2026-09-10 all go RED. Instrumented: mutant line executed 6×, so this is a real kill, not an unexecuted-path artefact. One residual: `test_the_runner_actually_passes_exp_config_at_the_call_site` asserts on an `inspect.getsource` substring and survived a mutation that broke the function entirely.

## findings

**F1 — `bench/tests/test_done_markers_carry_evidence_2026-09-10.py:99` — HIGH.** The collection check is a string prefix, so `..` defeats it. Evidence pointing *outside the repository* is accepted.
```
evidence string : bench/tests/../../../../../../../../../../tmp/cdsfl_probe/outside/test_outside.py
startswith bench/tests/ : True
resolves to     : /private/tmp/cdsfl_probe/outside/test_outside.py  is_file: True
M8 evidence OUTSIDE THE REPOSITORY -> GREEN  <-- HOLE | 79 passed in 0.26s
```
Fix: replace `assert f.startswith("bench/tests/")` with resolved containment — `target = (REPO / f).resolve()`, `assert collected in target.parents` where `collected = (REPO / "bench" / "tests").resolve()`.

**F2 — same file, line 85 — MEDIUM.** `assert True` satisfies "holds a real test". A file whose sole content is `def test_hollow(): assert True` → `79 passed`. Fix: in `with_assert`, skip `ast.Assert` nodes whose `.test` is a truthy `ast.Constant`.

**F3 — same file, lines 124–125 — HIGH, and this one is the project's own "a guard that cannot fail is not a guard".** `test_what_this_guard_does_not_prove_is_written_down` reads `Path(__file__).read_text()` — the file containing the needle in its own assert statement. Deleting the **entire module docstring** left it at `79 passed`. Worse, direct measurement shows the needle *never matched the prose at all*: the sentence wraps, so `ast.get_docstring(...)` gives `'does NOT prove the tests would fail against a reverted fix' -> False`. The assertion was satisfied **solely by its own source literal on line 112**. Fix: `doc = " ".join((__doc__ or "").split())`. Verified: docstring deleted → RED; widened paragraph alone deleted → RED; real file → `79 passed`.

**F4 — MEDIUM, and it is the answer to the brief's question.** Nothing binds evidence to a task. Rewriting all 19 evidence fields to name one unrelated pre-existing file:
```
M7: rewrote 19 DONE evidence fields -> all point at bench/tests/test_operational_scripts.py
    evidence guard : GREEN  (79 passed in 0.35s)
    marker  engine : GREEN  (20 passed in 0.45s)
```
This is *not* a new hole — it is the guard's declared limit — but the docstring understates it. It says the guard cannot prove a test "would fail against a reverted fix," which lets a reader believe the named file at least *concerns* the task. It does not. I widened the docstring and pinned the wider statement.

**F5 — `hooks/pre-commit:36` — HIGH, cheapest fix, largest effect.** The guard is collected by the full suite but is **not** in the commit-time guard set — the exact moment a DONE marker is written. The hook's own header records the ruling this repeats: *"The failure was never the absence of a rule or a checker; it was never running the checker."* Cost, measured under `sh` (my first timing run was void — zsh does not word-split, so `$G` was one argument and pytest errored; I re-ran and discarded it):

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| 4 guards | 0.99s | 0.89s | 0.87s |
| 6 guards | 1.50s | 1.39s | 1.56s |

+0.5s against the hook's own stated 1.00–2.02s budget. Adding `test_task_list_markers_2026-09-09.py` alongside also closes the deleted-marker case at commit time. (`2 errors` in both columns are pre-existing — the sandbox has no `.git`.)

## falsifier_result

Before/after, same battery, same guard file swapped:

| mutation | before | after |
|---|---|---|
| M3 traversal out of `bench/tests` | GREEN | **RED** |
| M4 hollow `assert True` evidence | GREEN | **RED** |
| M8 evidence outside the repository | GREEN | **RED** |
| M9 module docstring deleted | GREEN | **RED** |

Real 19 stay green throughout (`79 passed`); task list md5 `72cc03486db40614143a75cec84a61a6` unchanged; all work in the panel sandbox, canonical tree untouched.

## refutation_condition

I would be overturned if the traversal and outside-repo paths were already refused upstream — e.g. if the marker writer normalises paths before they reach the file, or a pre-existing guard rejects `..` in a marker. I grepped for callers of `task_list_markers` and found only the pulse hook and the two test files, but I did not exhaustively audit every `UserPromptSubmit` hook. I would also be overturned on F5 if a CI job runs the full suite on every push, making commit-time redundant — the sandbox has no `.git`, so I could not check for workflows.

**Class of overstatement the fixed guard still misses:** the one that caused 6.3. A DONE entry naming a real, asserting, collected, *passing* test that exercises a fake object and would stay green against the reverted fix. My mutation run on 6.3 is the existence proof — 8 such tests, all green, live regression at HEAD. Closing it needs per-task mutation testing. That is worth its cost only for the subset where being wrong ships a regression, not for all 19.

## strongest_disagreement

The brief asks whether the guard "closes the hole **or only moves it**," and that disjunction is wrong. The hole was never "DONE markers name no evidence." It was **the author of the claim is also the auditor of the claim.** Evidence-naming is self-reported; every hole I found (F1, F2, F4) is a way for the same author to satisfy the checker cheaply, and F3 is a checker that audits itself and therefore cannot fail. What actually produced the 57.89% figure was not a missing field — it was 18 adversarial agents *running the tests*. That is the mechanism that worked, and it is not what got built. My fixes raise the cost of a hollow claim; they do not change who is grading. I would rather the project measure this guard's real yield — how many DONE markers it refuses over the next month — than accept it as the answer to the founder's question.

Second, smaller: the brief calls 6.3 "a live regression at HEAD" alongside the 11 overstatements. It is a different species — the tests were honestly written and structurally blind, not overstated. Filing it under the same heading invites the wrong fix.

**passes_run — 5.**

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 39 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_verification_gap_2026-09-10) -->

Canonical mtime 01:26:57 — modified mid-session; now back to real per-task evidence (single legitimate `test_operational_scripts.py` reference at task 8.1). My controlled final measurements were all taken against this hash-pinned real list, so nothing is invalidated — and the transient state is itself evidence I'll report. All passes complete; a further sweep (γ/convergence path, 6.3 repair, note-lint repairs) produced nothing new above threshold. Final report:

---

## verdict: **PARTIAL**

The guard genuinely closes the "named nothing / named a missing file / named an assertion-free file" holes and is itself wired and red-on-violation. But **2 of its 4 checks were mechanically defeated as shipped**, and a live event during this very review demonstrated the largest residual hole (blanket irrelevant evidence) in production conditions.

## reasoning (all from executed tool output)

- **Baseline:** `python3 -m pytest bench/tests/test_done_markers_carry_evidence_2026-09-10.py -q` → `79 passed in 0.30s`. `scripts/task_list_markers.py --check` → `task list coherent: 77 entries, 0 problems`. All 19 DONE entries name evidence.
- **Parser driven with 9 adversarial constructions** (OPEN-no-evidence parses clean; DONE-no-evidence parses with `evidence=()` and — important — `check()` exit **0**, so only the pytest guard catches it; evidence containing `>` breaks the marker and is flagged "has no marker"; indented/blank-separated markers flagged; traversal path parses clean).
- **4 hostile DONE entries planted** in the sandbox list: **guard passed all 4** (`95 passed in 0.32s`), and full-tree `--collect-only` proved the X1/X2 evidence files are **never collected as tests** by the suite.
- **ν/σ (is the addition reached and does it fail on violation):** 4 mutations — strip evidence, nonexistent file, outside-dir file, no-test-function file — each verified applied by `assert old in s`, each turned the guard red (`1–2 failed`), restore → green. The guard is additive on its own terms.
- **γ / two-sided gate:** `grep -r task_list_markers|CDSFL_MASTER_TASK_LIST bench/` — matches only in `bench/tests/` and archived panel logs; nothing in `bench/dm/` or the runner reads the list. **I agree with the brief: convergence machinery is not implicated.**
- **6.3 repair:** `_is_the_logs_dir_default` compares **resolved** paths (its docstring records that the raw-string first version didn't work); `test_logs_dir_honours_the_caller_2026-09-09.py` now contains `test_the_real_ExperimentConfig_default_is_not_read_as_a_choice` importing the **real** `ExperimentConfig` — the shape the 8 SimpleNamespace tests never reached. That file + note-lint guard + marker tests: `46 passed in 11.74s`.
- **Demotion probe (withdrawn finding):** changing `state: DONE` → `Done` silently removes the entry from the guard's universe (guard: `91 passed`), but `test_the_hook_emits_the_task_line_and_exits_zero` went red — because `summarise()`'s count-sum assert crashes the pulse hook. Caught, but by an **accidental chain**; my fix makes it intentional.
- **Live concurrent-writer event:** mid-session, the canonical list's 19 evidence fields were all rewritten to `bench/tests/test_operational_scripts.py` and then restored (canonical mtime 01:26:57, caught via `diff` of my own copy; my session-start grep shows real evidence; current canonical has exactly 1 legitimate reference). [SPECULATIVE on attribution — plausibly another seat.] Materially: **that blanket rewrite passes the guard, original and hardened** — one real, collected, asserting file named as evidence for 19 unrelated tasks. The guard's relevance hole was demonstrated live, not hypothetically. My final measurements were re-taken on the verified restored list (`80 passed` ×5, hash-pinned `72cc0348…`).
- Pre-existing note: a bare root `pytest` is interrupted by 3 collection errors in quarantine/archive dirs (`bench/logs/build_experiment_2026-08-22/QUARANTINE…`, `experimental_notes/unextracted_sandbox_2026-08-30/…`) — the guard is only ever exercised by `bench/tests`-scoped runs.

## findings

**F1 — HIGH — `bench/tests/test_done_markers_carry_evidence_2026-09-10.py:99`** (check 4, path traversal). `f.startswith("bench/tests/")` accepts `bench/tests/../../scripts/pseudo_evidence_2026.py`, which resolves to `scripts/` and is never collected. **Falsifier executed:** planted entry X1 → guard `95 passed`; full-tree `--collect-only` shows the file only as a parametrize ID in another test, never as a test. **Fix (executed):** resolve the path and require `(REPO/"bench"/"tests").resolve() in p.parents` — old/new text as applied in my sandbox patch below. After fix: `FAILED …[X1]`.

**F2 — HIGH — same line** (check 4, non-collectible filename). `bench/tests/evidence_helper_2026.py` is inside the directory but matches neither `test_*.py` nor `*_test.py`, so pytest never collects it; guard passed it. **Fix (executed):** additionally require `p.name.startswith("test_") and p.suffix == ".py"`. After fix: `FAILED …[X2]`.

**F3 — MEDIUM — same file:88** (check 3, `"raises" in source`). A test whose only content is a docstring `"""this function never raises anything"""` and `pass` — **zero assertions** — passes, via the exact grep-not-parse mistake the test's own docstring warns against. **Falsifier executed:** X4 passed the shipped guard. **Fix (executed):** detect `raises`/`assertRaises`/`fail` as AST calls. After fix: `FAILED …[X4]`.

**F4 — LOW/MEDIUM — same file:87** (check 3, constant assert). `def test_vacuous(): assert True` passes. Adjacent to the stated mutation-testing limit, but constant-assert detection is one AST condition. **Fix (executed):** exclude `ast.Assert` whose test is a truthy `ast.Constant`. After fix: `FAILED …[X3]`.

**F5 — MEDIUM — `hooks/pre-commit:36-39`.** The enforcement point that failed on 2026-09-09 was commit time, and the pre-commit GUARDS list contains neither this guard nor `--check`. The guard runs in 0.25–0.44 s (measured), well inside the hook's own 1–2 s budget rationale. **Fix:** append `bench/tests/test_done_markers_carry_evidence_2026-09-10.py` to `GUARDS`. (Not executable here without a sandbox git commit cycle; the runtime cost figure is measured.)

**F6 — LOW — suite-level.** No test runs `check()` against the real list; incoherence is caught only via `summarise()`'s internal assert crashing the pulse hook (demonstrated). **Fix (executed):** added `test_the_real_list_is_coherent_by_the_markers_own_check` — under it, the `Done` demotion fails **directly**: `FAILED …::test_the_real_list_is_coherent_by_the_markers_own_check`.

## falsifier / falsifier_result

Composite, all executed in `/tmp/cdsfl_sbx_seat` (sandbox copy; canonical untouched by me):
1. Plant X1–X4 + run guard → `95 passed` (**defeats confirmed**); full-tree `--collect-only | grep` → X1/X2 never collected.
2. Apply patch (checks 3+4 hardened, coherence test added) → `4 failed, 92 passed`, failures exactly `[X1],[X2]` on collects-check and `[X3],[X4]` on asserts-check.
3. Restore canonical list → `80 passed` (×5, incl. `-p no:cacheprovider`); mutation M1 re-run → `2 failed` (still red); `Done` demotion → red on the new coherence test; final clean → `80 passed in 0.41s`.

## refutation_condition

My PARTIAL verdict is refuted if: (a) someone shows a suite/CI entry point that collects `bench/tests/../../…` or non-`test_*` filenames (then F1/F2 are not misses — I checked `pytest.ini`: no `python_files`/`testpaths` override, so I claim none exists); or (b) the project's threat model is explicitly honest-mistake-only, in which case F3/F4 fall under the already-stated mutation-testing limit and the verdict moves toward CONFIRMED. **Class the guard still misses even with my patch:** *irrelevant-but-real evidence* — a collected, asserting test that doesn't test the claimed task (demonstrated live by the blanket `test_operational_scripts.py` rewrite), and green-while-broken tests (6.3's own history). Cheapest closure of my objection: F5's one-line pre-commit addition (+0.3 s per commit — clearly worth it). Relevance itself is only closable by per-item mutation testing, which the guard correctly names as out of scope.

## strongest_disagreement

The brief frames the question as whether the guard "closes the hole." The 6.3 case in the brief's own evidence shows the dominant failure mode was **green-but-wrong tests**, not absent ones — 8 passing tests on a fake config while production broke. Every check this guard performs is static; a static guard can only ever verify that evidence *exists*, never that it *discriminates*. So the honest statement is not "hole closed" or "hole moved" but: the cheap 80% (fabricated/absent evidence) is now closed — pending my patch for the demonstrated bypasses — and the expensive 20% (non-discriminating evidence) is exactly where 6.3 lived and remains open by design. The guard's docstring says this; the brief's framing under-weights it. Secondary: a shared mutable staging tree for six concurrent seats produced a mid-review rewrite of the artefact under review — that is a panel-infrastructure defect (torn reads of the exam substrate) worth its own repair.

## passes_run

**3** (survey+attack; mutation+enforcement; fix+anomaly-resolution), plus a terminal sweep that produced no new above-threshold findings — Δ(4) = 0, converged, not budget-exhausted.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_verification_gap_2026-09-10/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
