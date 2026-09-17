# Panel round 17 — the full record

Record written 2026-09-17T17:34:08+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

**2026-09-17, 17:34 BST (Europe/London).** Dispatched 16:37; cc2 returned at 16:51 and fable at 17:24.

**Seats: cc2 and fable only. 0 paid dispatches**, verified before launch by importing the dispatcher under `PANEL_ONLY=cc2,fable` and reading its resolved roster: `[('cc2', 'opus', 'claude_cli'), ('fable', 'fable', 'claude_cli')]`. It was the first round whose seats started without the dispatcher's secrets: a live read of both seat processes during the round found PATH and HOME present and 0 secret-named variables, although the dispatcher had loaded `.env` (commit `0812897`). Each seat ran in its own sandbox copy.

**fable timed out once.** Its first attempt hit the 1,800 s seat cap at 17:08; the automatic retry returned 17,057 characters from 54 tool calls in 973.7 s. cc2 returned 18,909 characters from 61 tool calls in 794.9 s.

**The brief** is `experimental_notes/panel_briefs/Engineering_Entries_Brief_2026-09-17.md`, sent byte for byte as `bench/logs/panel_round17_2026-09-17/BRIEF.md`: Question 9, the 34 engineering entries of the supplementary list, derived by `scripts/q9_engineering_entry_set_2026-09-17.py`. Both seats report reaching all 34.

**The containment alarms, attributed.** The dispatcher reported the operator's control plane modified: `~/.claude/hooks/ffafp_audit.py` and `~/.claude/hooks/mc_commands.py`. Both were the assistant's own mirror copies of the committed hooks at 17:06:45 BST, for action list item 4: their modification times are 17:06:45, the previous live copies were backed up first and matched `HEAD` byte for byte, and the live files match `hooks/` at commit `cd3cd83` by `cmp`. The canonical-tree list is the assistant's commits during the round, from `9c5eea3` onwards. The attributor showed no seat touching either.

**The proposal diff mixes 2 things.** `seat_proposals.diff` compares each sandbox with the canonical tree as it stood when the round ended, so the 27 files the assistant changed during the round appear under both seats although neither seat edited them. The seats' own proposals are the remaining files: 4 from cc2 (the A23 guard, its new producer and test, and `resources/RECOVERY.md`) and 18 from fable, 1 of them a new 156-line file at the repository root with the same name as `scripts/ruled_items_are_accounted_2026-09-11.py`.

## What was adopted, and what was refused

**Intake done 2026-09-17 19:30 BST.** Every proposal was re-executed independently before anything changed, and nothing was accepted because a seat asserted it. Both seats' replies below are unedited.

**Adopted, 12 proposals.** cc2's A23 repair, which was a real failure at HEAD: its suite-figure rule accepted only a `scripts/<name>.py` path as a producer, so an honest sentence about the full suite could not satisfy it, and its reachability probe read git's exit 128, "no repository", as "not reachable", fabricating a failure in any tree without `.git` -- which every panel sandbox is. Adopted with 3 changes: a figure with no producer was cut from its prose, a "fresh clone" claim was corrected, and its negative control could not fail, because `pytest.skip` passes straight through `pytest.raises(AssertionError)`. Its producer, `scripts/suite_figure_producers_2026-09-17.py`, is adopted with its test. From fable: the same no-repository class in the evidence for M1, A16 and A2, where 7, 1 and 4 tests invented failures in a sandbox (A2 adopted with the marker removed from a class that builds its own repositories and passes without git); a measurement-classifier hole that passed `sqlite3`, `tempfile`, `logging` and `zipfile` writes as MEASUREMENT, with 0 of 134 scripts reclassified; an Open Brain test that runs `verify` instead of grepping for it; a self-contained panel-12 checkout; a blast-radius script that printed "never committed: 0" with no git history, adopted with that line printing UNKNOWN and a test that calls `main()` with git forced absent; the A12 lookahead, where "ruling 28 of 28" counted as a reference to item 28; and 2 docstring corrections.

**Refused, 8 proposals, each with the executed reason.** fable's A7 correction carried a false clause ("reproduces only with the severity filter dropped": executed, the anchor reproduces at 22, 20 and 32). Its A17 and A22 corrections rest on a premise those entries refute in their own dated paragraphs. `test_q9_entry_corrections_2026-09-17.py` asserts on source text, re-runs 3 suite files as subprocesses without `--netguard-strict`, and 1 of its checks, `"22" in text`, is always true. A duplicate of `ruled_items_are_accounted_2026-09-11.py` at the repository root crashes on import and nothing reaches it. A `resources/RECOVERY.md` citation would have satisfied the guard by naming a script that cannot reproduce the figure. fable's A23 skip duplicates cc2's, which came with controls. The last 2 were tests that could not land without a task-list edit the intake was not permitted to make; both are resolved below.

**The 2 entries the intake could not finish, finished in this session.** A7's DONE paragraph still asserted the identification its own producer withdrew: `scripts/escalation_paths_2026-09-11.py` reproduces the anchor `exp55_v3_control` = 8 under 3 predicates, totalling 22, 20 and 32, so 1 family figure cannot identify which was meant, and ANONYMOUS is 0 under all 3, so the conclusion does not move. The entry now records the withdrawal and quotes the family {20, 22, 32}, and fable's `bench/tests/test_a7_predicate_family_is_quoted_2026-09-17.py` is adopted as delivered. A18 cited 3 runner lines that drifted 3 times on 2026-09-17 alone (12638, then 12911, then 13064 for the same read); rather than re-pin them, the entry now cites `readers_of()` in `scripts/config_fields_are_read_2026-09-11.py`, which prints the line as it stands, and fable's test is REPLACED by one holding the property that survives: the producer still finds a runner read for each field, and the entry carries no runner line number. The seat's version is recorded in that file's docstring. A first version of that replacement searched a window around the first mention, which is in the heading, so a stale line put back into the body left it green; widened to the whole entry, it fails on that mutation.

**A process finding, above threshold, not fixed.** fable's first attempt hit the 1,800 s cap and its reply was lost; the retry reused the same sandbox, built once at 16:38:13. 14 of the 19 files fable left carry timestamps inside that first attempt, so the reply preserved below describes work it did not report, and its A23 verdict of HOLDS was measured against a tree that already held its own unreported edits. cc2 reported A23 as FAILS, and execution agrees with cc2. A dispatcher that reuses a sandbox across attempts can return a reply describing a tree it did not author.

**Still open after the intake.** 3 tests fail in a copy with no `.git`, and neither seat proposed a fix: 1 in `bench/tests/test_every_test_file_is_collected_2026-09-01.py` and 2 in `bench/tests/test_overstated_entries_2026-09-11.py`. They fail openly rather than inventing an answer, but in a sandbox they still raise the "DONE entries whose evidence failed" banner.

## CC1's own position, and the range across the seats

**Added 2026-09-17 23:50 BST, on the founder's ruling that the missing instrument be built and implemented.** The `pr` protocol has always said CC1 *"actively participates with its own position and synthesizes the range"*, and until now nothing in the project measured that half. `scripts/p5_cc1_position_2026-09-17.py` now derives the range from the seats' own verdict tokens and reports which of them CC1 reached. Run against this record before this section existed, it returned NO_CC1_POSITION with 2 entries in the range.

**The range, derived and not asserted.** 9 entries carry a verdict from both seats. They differ on 2.

**A23. cc2 says FAILS, fable says HOLDS, and CC1's position is FAILS.** Execution decides it and did: the guard's suite-figure rule accepts a producer only as a `scripts/<name>.py` path, so an honest sentence reporting the full suite cannot satisfy it, and its reachability probe read git's exit 128, "no repository", as "not reachable", which fabricates a failure in any tree without `.git` -- which every panel sandbox is. Both defects reproduced at HEAD. fable's HOLDS is not simply wrong, and the reason matters more than the verdict: its retry ran in the sandbox its timed-out first attempt had already been editing, so its reading was taken against a tree carrying its own unreported edits. That is a defect in the dispatcher, now fixed, and not a fault of the seat.

**A22. cc2 says HOLDS, fable says PARTIAL, and CC1's position is HOLDS.** fable's PARTIAL rests on the claim that the entry's prose is now false. The entry refutes that in its own dated paragraph, which fable's reply does not engage with, and the intake refused the correction on that ground after re-executing it. The disagreement is preserved here rather than resolved by weight of seats: 1 seat against 1, decided by the entry's own record.

**What CC1 is NOT claiming.** Nothing above scores a seat. The instrument reports which of the 2 disagreed entries this section answers, from a set computed out of the seats' own verdict tokens, and this section states a position with its evidence; neither counts votes, which this project forbids.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — do the engineering entries of the supplementary list hold, and what fixes the ones that do not

**2026-09-17, 16:35 BST, Europe/London.**

## Section 1 — The question

**Does each entry listed below still hold against evidence you execute, and where it does not, what is the simplest sufficient fix, delivered as a file and proved by a falsifier you ran?**

The artefact under review is `experimental_notes/CDSFL_MASTER_TASK_LIST.md`. Each entry is a bold heading paragraph followed by a `<!-- task: ID | state: ... | status: ... | evidence: ... -->` marker naming the test files meant to prove it, and any dated paragraphs after the marker belong to the same entry. Read the markers with `parse_entries` in `scripts/task_list_markers.py`, the module the repository declares as their only reader, rather than with a pattern of your own: a hand-written pattern has miscounted this list before.

**Why these entries.** The 59 entries of the supplementary list at the foot of that file arose during the work rather than from the founder. The approved plan, `experimental_notes/Task_List_59_Decision_2026-09-12.md`, sends them to this panel in the validated format and keeps back the decisions that are the founder's by category. The founder has since approved Question 9 of `experimental_notes/Outstanding_Rulings_2026-09-15.md`: dispatch the engineering entries now, and hold A19 until the new material on the mathematical model has been reviewed.

**The 34 entries under review, in the order to take them.** The set is derived, not typed: `python3 scripts/q9_engineering_entry_set_2026-09-17.py` reads the 59 supplementary ids, the 7 the approved plan holds for the founder, and the 16 of them panel round 16 reviewed, and prints these 34.

<!-- figure: supplementary entries | scripts/q9_engineering_entry_set_2026-09-17.py | supplementary entries: 59 -->
<!-- figure: held for the founder | scripts/q9_engineering_entry_set_2026-09-17.py | held for the founder by category: 7 -->
<!-- figure: reviewed by round 16 | scripts/q9_engineering_entry_set_2026-09-17.py | reviewed by panel round 16: 16 -->
<!-- figure: entries under review | scripts/q9_engineering_entry_set_2026-09-17.py | entries under review: 34 -->

- **Group 1, protections, where a wrong entry leaves a guard believed that does not hold:** A24, A16, A10, A22, A14, A5, A21, V3, V8, V6, P2, P6.
- **Group 2, instruments, scanners and restore paths:** A25, A17, A18, A3, A7, A12, M1, M2, V5, V2, A1, A2, A23, L1.
- **Group 3, rulings written back and questions answered by measurement:** R4, R5a, R6, R7, R8, R9.
- **Group 4, withdrawals:** A9 and A15. A withdrawal is a removal, so the additive standard applies to it: confirm that the withdrawal rests on something that executes, or say what should be reinstated.

**Both seats take the same order**, so that every entry either of you reaches has the best chance of carrying 2 independent verdicts. If you run short, stop at an entry boundary and list the ids you did not reach.

**Out of scope. Do not work on these.**

- Held for the founder by category: A8, A11, R1, R3, Z1, W1.
- Held because the claim is about the mathematical model itself: A19, R10, R11.
- Reviewed by panel round 16 earlier today, whose proposed closures await independent re-execution: P1, P3, P4, P5, P7, L2, R2, R5, A4, A6, A13, A20, A26, V1, V4, V7.

The audit behind round 16 found **31 of 84** DONE entries claiming more than their evidence shows; `python3 scripts/done_audit_overclaim_rate_2026-09-17.py --ids` lists them, and none of the 34 above is among them. That is not a clean bill. Of the 34, the audit's first pass flagged M2, A2, A5, A12, A14, V2 and V6, and in each of those its verifier refuted the flag; both sides are in `experimental_notes/evidence/done_audit_2026-09-11/verification_verdicts.json`. Neither verdict is evidence. Your execution is. A9 and A15 were never audited, because the audit covered DONE entries only.

<!-- figure: overclaim count, current not superseded | scripts/done_audit_overclaim_rate_2026-09-17.py | 31 of 84 = 36.9048% -->

## Section 2 — Use the harness

**Form your answer by RUNNING things, not by describing them.** Every claim you make about an entry must come from a command you executed and whose output you can quote.

**The mathematical model, stated plainly.** The founder regards the current mathematical model as superseded by the founder's own revision, and that revision has not yet been reviewed. The 34 entries were selected because their claims do not depend on it. So do not use `gamma`, `rho`, `S_k`, `sigma`, `nu` or the two-sided gate as authority for or against any entry, and do not propose changes to any of them. Where an entry's code computes 1 of them, check that the code does what the entry claims, not whether the model is right. If an entry's claim turns out to depend on the model after all, record `model_bearing: direct`, return the verdict MODEL_BOUND with no fix, and move to the next entry.

**Named instruments that bear on these entries:**

- **Wilson intervals.** A1, A3, A15, M1 and P2 each state at least 1 proportion with an interval. Reproduce each from the committed script the entry names, with 2 tools agreeing: `statsmodels.stats.proportion.proportion_confint` with `method="wilson"` against a scipy or numpy closed form. `measured-rate-travels-with-its-script` binds: a figure with no committed producing script is a claim about evidence, not evidence, and supplying that script is a fix, not a footnote.
- **severity.** A7 counts escalated critical findings against `CRITICAL_SEVERITY_THRESHOLD` in `bench/reference_runner_v3.py`. Read the constant from the runner; never type it. Whether that threshold is right is a question about the model and is out of scope. Whether A7's counts follow from it is in scope, and `scripts/escalation_paths_2026-09-11.py` is the producer to run.
- **The containment and survey instruments the entries name.** `canonical_was_touched` and `attribute_canonical_touch` in `bench/panel_sandbox.py` for A5 and A21; `scripts/measurement_scripts_only_2026-09-11.py` for A16; `scripts/panel_brief_validate.py` for V6, P2 and P6.

**`execute-do-not-grep` is the rule to hold every evidence file to.** A test asserting on the SOURCE TEXT of a module proves only that the module describes itself consistently. Where an entry's claim is about behaviour, its evidence must CALL the code and compare outputs. Where it does not, rewriting that test so it executes is a legitimate fix.

**Rules for this round, each learned from an earlier one.**

1. **Spend nothing.** Call no model API, and do not run `bench/confer_maths_panel_2026-09-05.py`, any `confer_*` dispatcher, or `bench/test_falsifier_matrix_2026-06-06.py`. The dispatcher that launched you loads API keys into its own environment; since commit `0812897` your seat is started without them, by `seat_environment()` in `bench/experiment_11_orchestrator.py`, so a paid route should fail from your shell. Do not test that by trying one. A22 is about that dispatcher: exercise it by importing it, or run it only with `PANEL_ONLY=__none__`, as `bench/tests/test_panel_brief_format_2026-09-09.py` does.
2. **Write nothing outside your sandbox copy.** The canonical tree and the operator's control plane under the home directory are fingerprinted before and after the round. M2's hook lives at `~/.claude/hooks/task_list_pulse.py`: read it, do not modify it, and deliver any change you propose as a file inside your sandbox tree. A24 and V5 concern Desktop mirrors, so run nothing that writes to `~/Desktop`; the control-plane fingerprint in `bench/panel_sandbox.py` does not cover the Desktop, so a write there would go unseen.
3. **Check a script before running it.** `classify(path)` in `scripts/measurement_scripts_only_2026-09-11.py` returns MEASUREMENT or ACTION for a single script, with the lines that decided it, and runs nothing; the same file run with no arguments surveys every script under `scripts/` the same way. Run an ACTION script only when the entry is about that script, and only inside your sandbox. Do not assume `--help` is inert; `--help` on a record-assembly script is how a verbatim panel record was destroyed.
4. **Run targeted tests, never the full suite**, in the form `python3 -m pytest <file> -q -p no:cacheprovider --netguard-strict`. Your sandbox copy has no `.git` directory, because `build()` in `bench/panel_sandbox.py` deletes it, so anything that asks git a question gets "not a git repository" there. V2's instrument once turned exactly that into a fabricated failure for every entry it checked. Before reporting a failure, establish whether it is a defect or an artefact of a sandbox with no repository.
5. **For A1, run only the read-only Open Brain subcommands**, the ones `scripts/open_brain_assessment_2026-09-10.py` lists in `READ_ONLY`. Open Brain's database lives outside your sandbox, so a writing subcommand would change shared state no sandbox confines.
6. **Edit nothing under `bench/logs/`, never alter a quotation of the founder, and never edit a verbatim region of a record.** L1 exists because 1 of the founder's sentences was once made the subject of a compliance discussion, and V8 because a blocking checker once left editing a verbatim record as the only way to commit it.
7. **Start no Wolfram process.** Run no `wolframscript`, `WolframKernel` or Wolfram web service. Wolfram's published terms bar its use inside automated AI pipelines, and a dispatched panel seat is one; the kernel on this machine is also licensed for a single kernel, and concurrent calls to it fail. Cross-check with SymPy, mpmath, SciPy, statsmodels or z3.

## Section 3 — Produce a fix, and test it

A finding without a fix is half an answer. A fix without a runnable falsifier you have EXECUTED is a hypothesis, not a fix.

**A fix described in prose is not delivered either.** `teardown` in `bench/panel_sandbox.py` destroys your sandbox when you finish, and `changes()` returns only the files still inside the sandbox repository tree, as `seat_proposals.diff`. Write each fix at the path it would live at: edit existing files in place, and put a new test at `bench/tests/<name>.py`. Not `/tmp`, not a scratch directory. Everything left in the tree comes back as a patch, is re-executed independently, and is applied or refused with a reason.

For each entry you take:

1. State the entry's claim in 1 sentence, and what its named evidence actually establishes when you run it.
2. Try to refute the claim by execution, going beyond the named evidence where it tests something adjacent to the claim rather than the claim itself.
3. Where the claim fails or overclaims, produce the correction: strengthen the evidence so the claim becomes true where the claim is worth keeping, and otherwise narrow the entry's text to what is proved.
4. Write a falsifier that goes RED against the state before your fix and GREEN after it. Run it, and report the command and its output verbatim.
5. Show the falsifier can fail: revert your fix in place and run it again. A falsifier that cannot fail confirms nothing.
6. Where the claim holds, say so. A verdict of HOLDS backed by execution is worth as much as a refutation, and it carries the same obligation: the falsifier you ran against the claim, and a control showing that falsifier goes red once the change the entry describes is reverted in your sandbox.

**The simplest sufficient fix standard applies.** Before building anything new, state what would go wrong without it, and check whether something cheaper already prevents that. **The additive standard applies in both directions**: never remove or loosen a guard or a test without a committed measurement showing the replacement dominates on a named property, so deleting a test to make an entry true is a removal; and an addition nothing reaches is not additive either.

## Section 4 — What would refute you

Before you conclude on any entry, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

State also your strongest disagreement with this brief, including the possibility that an entry does not belong on this list, that the grouping or order is wrong, that an entry held back should have been sent, or that an entry sent here depends on the mathematical model after all. The audit that preceded this round is not privileged over your own execution, and neither is this brief.

## Section 5 — Output shape

Return these fields for every entry you take, so replies can be compared without a parser guessing:

- `entry`: the task id.
- `claim`: the entry's claim, in 1 sentence.
- `verdict`: HOLDS, PARTIAL or FAILS. For A9 and A15, WITHDRAWAL_SOUND or REINSTATE. MODEL_BOUND where Section 2's rule on the model stops you.
- `model_bearing`: none, indirect or direct, with 1 sentence saying why.
- `fix`: the exact text or code change, or `none needed` with the reason.
- `delivered_files`: the paths you left in your sandbox tree.
- `falsifier`: the runnable check, as a fenced `python` or `bash` block.
- `falsifier_result`: the command run and its output, verbatim, before and after the fix.
- `control`: how you showed the falsifier can fail.
- `simplest_sufficient`: why no cheaper fix suffices.
- `refutation`: what would overturn your answer.

And once, for the whole reply:

- `entries_not_reached`: every id from Section 1 you did not take.
- `passes_run`: how many passes you ran over the entries you took.
- `strongest_disagreement`: your strongest disagreement with this brief.

## Section 6 — Termination

**Stop on diminishing returns**, this project's own criterion: stop when a further pass over the entries you hold produces no new above-threshold findings, and say how many passes you ran.

A finding is above threshold if missing it could lead a reader to act on a false claim, or leave a guard believed that does not hold. Do not generate findings for their own sake, and do not police style. If you run short of budget, stop at an entry boundary and WRITE WHAT YOU HAVE, with `entries_not_reached` filled in: a partial answer carrying executed evidence is worth everything, and a holding note is worth nothing.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 61 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round17_2026-09-17) -->

## VERDICTS

I reached all 34 entries. One entry **FAILS** with two live defects, both fixed and proved; the rest hold on executed evidence. Full treatment for the entries where I went beyond the named evidence; compact blocks where the verdict rests on re-execution plus a targeted probe.

---

# A23 — the one failure

- **entry**: A23
- **claim**: `resources/RECOVERY.md`'s newest SESSION STATE block is current, and a guard now holds it so — closed 2026-09-11 by hand-writing the block, `sv` being the wrong repair.
- **verdict**: **FAILS**
- **model_bearing**: none — the guard reads markdown and asks git a reachability question; no `gamma`, `S_k`, `sigma`, `nu` or gate is touched.
- **what its named evidence establishes when run**: it goes **RED at HEAD**, and not for a sandbox reason. Two separate defects:

**Defect 1 — the guard is unsatisfiable by honest prose about the suite.** `TestASuiteFigureNamesItsProducer` accepts a producer only as `scripts/<name>.py`. The full suite has no such producer: what produces "7,493 passed" is a pytest invocation. So the newest block (dated today, 2026-09-17, reporting the suite green at `a2999f1`) is an offender, and the only routes to green were to cite a script that did not produce the number — a fabricated citation — or to stop reporting the suite. The error message's own exemplar, `"6658 passed … EXIT 0"`, is a full-suite figure, so the rule demands exactly the thing its pattern cannot accept.

**Defect 2 — a fabricated failure outside a checkout.** `test_it_names_a_commit_reachable_from_head` reads `r.returncode == 0` from `git merge-base --is-ancestor`, collapsing exit 1 (*not an ancestor*) and exit 128 (*no repository*) into "not reachable". In a fresh clone, and in **every panel sandbox** — `panel_sandbox.build()` deletes `.git` — it asserts *"the block describes a tree that is not this one"* on no evidence. This is precisely the defect panel round 12 found in `overstated_entries_2026-09-11.py` (V2's subject), in a file written the same day. Its **twin in the same class already skips** for this reason at `:88`; one test skipping where its sibling fabricates is the whole bug.

- **fix**: (1) `_NAMES_A_PYTEST_RUN` added and the rule now consults `_NAMES_A_PRODUCER = script | complete pytest command`; (2) `resources/RECOVERY.md:32` now names the re-run command; (3) the reachability probe skips when `git rev-parse --git-dir` fails, **scoped so a bogus sha inside a real checkout still fails**; (4) `scripts/suite_figure_producers_2026-09-17.py` is the committed measurement behind the widening.
- **delivered_files**:
  - `bench/tests/test_suite_figure_producer_forms_2026-09-17.py` (new)
  - `scripts/suite_figure_producers_2026-09-17.py` (new, classifies MEASUREMENT)
  - `bench/tests/test_recovery_session_state_is_current_2026-09-11.py` (edited)
  - `resources/RECOVERY.md` (edited — assistant prose, not a verbatim region, not a founder quotation)

- **falsifier**:
```bash
python3 -m pytest bench/tests/test_suite_figure_producer_forms_2026-09-17.py \
  bench/tests/test_recovery_session_state_is_current_2026-09-11.py \
  -q -p no:cacheprovider --netguard-strict
```

- **falsifier_result**:

*Before (named evidence, at HEAD, defect 1 — not a git artefact):*
```
E       AssertionError: a suite figure in the newest SESSION STATE block names no
        producing script, so a reader cannot re-run it and it can go false without
        anything noticing -- which is what happened to "6658 passed ... EXIT 0":
E           7,493 passed -- **★★★ THE FULL SUITE IS GREEN UNDER `--netguard-strict` AT `a2999f1`
====================== DONE ENTRIES WHOSE EVIDENCE FAILED ======================
  task A23 is marked DONE and names: bench/tests/test_recovery_session_state_is_current_2026-09-11.py
1 failed, 1 passed in 0.17s
```

*Intermediate, and it matters — widening the predicate ALONE does not fix it:*
```
patched guard
FAILED ...::test_every_paragraph_with_a_suite_figure_names_a_script
1 failed, 1 passed in 0.24s
```

*After both halves:*
```
........ss.....                                                          [100%]
13 passed, 2 skipped in 1.16s
```

- **control** (each half reverted in place, separately):
```
--- CONTROL A: prose reverted ---
FAILED ...::test_the_newest_block_satisfies_the_rule_by_calling_the_rule
1 failed, 7 passed in 1.74s
--- CONTROL B: skip reverted ---
FAILED ...::test_it_skips_where_there_is_no_repository
1 failed, 7 passed in 1.80s
--- FINAL (both restored) ---
13 passed, 2 skipped
```
A third control is inside the falsifier itself and **it caught my own first attempt**: `_NAMES_A_PYTEST_RUN` was `python3?\s+-m\s+pytest\s+\S+`, and `test_a_bare_mention_of_pytest_is_not_a_producer` went red on *"We ran python3 -m pytest and it passed."* The token after `pytest` must now look like a target or a flag. The widening was a hole for about ten minutes and the negative control is why it isn't one now.

- **simplest_sufficient**: the cheapest honest fix is one added producer form plus one sentence of prose. Citing an existing `scripts/*.py` would have gone green and been a fabricated citation — the failure mode `measured-rate-travels-with-its-script` exists to stop. Deleting the rule is a removal with no measurement behind it. The measurement that admits the widening rather than asserting it: across the whole file **4 of 20 suite-figure paragraphs are backed by a pytest command against 3 by a `scripts/*.py`** (5 of 20 after my prose fix) — the command form is the one the record already uses, including the 2026-09-08 and 2026-09-06 blocks the shipped pattern would call offenders.
- **refutation**: (a) a committed `scripts/*.py` that genuinely produces the full-suite pass count — then the prose should cite it and the widening is unnecessary; (b) a real prose string that satisfies `_NAMES_A_PRODUCER` without being re-runnable — then the boundary is still a hole; (c) evidence that `7,493 passed` came from an invocation other than `python3 -m pytest bench/tests` — my prose then names the wrong command. On (c) I under-measured deliberately: `--collect-only` on that target reports **7527** today against a reported total of 7499, and I wrote the figure as a *re-run instruction with the collection count beside it* rather than assert what was typed, because I did not observe the original run.

---

# Group 1 — protections

Named evidence re-executed: **154 passed, 1 failed, 1 skipped** in one invocation. The single failure is A16's, and it is a no-git artefact (below).

- **A16** — *claim*: the survey is now safe because MEASUREMENT and ACTION are declared, not inferred. **verdict: HOLDS.** *model_bearing*: none. Beyond the evidence I called `classify()` directly on all four scripts the entry names: `cdsfl_sv.py` ACTION at `.write_text()`; `cdsfl_qc.py`, `cdsfl_recover.py`, `adjudicate_by_repair.py` ACTION at a `subprocess` call — reproducing the entry exactly. Its one red test is `test_running_the_measurement_set_leaves_the_tree_untouched`, failing with *"git cannot report the tree's state here (exit 128); this check would compare empty output with empty output and pass on anything"* — a **deliberate fail-loud**, and the correct behaviour under rule 4, not a defect. **Observation, not a finding**: the entry's `112 files, 58 ACTION / 54 MEASUREMENT, 51.7857%` now reads **71/129 = 55.0388%, Wilson [46.4325%, 63.3536%]** (1 of the 129 is my new script). The entry's paragraph is dated 2026-09-11 and `bench/tests/test_a_rate_travels_with_its_date_2026-09-11.py` passes 7/7, so under the project's own rule this is declared drift, not an overclaim. *fix*: none needed. *refutation*: a `classify()` verdict of MEASUREMENT on any writing script.
- **A22** — *claim*: the dispatcher now imports with nothing supplied, and still refuses to dispatch by accident. **verdict: HOLDS.** Exercised by import per rule 1, never by dispatch. `PANEL_ONLY=__none__` import: `IMPORTED OK; LOGS= None BRIEF= None PROMPT= ''`, `has resolve_brief: True`. No-argument run: `usage: confer_maths_panel_2026-09-05.py <log-dir-name>`, **exit=2**. `--help` answers with usage instead of `no BRIEF.md in .../bench/logs/--help`. Both halves of the entry — importable, and still hard to dispatch by accident — execute. *refutation*: an import that raises, or a no-argument run exiting 0.
- **A5 / A21** — *claim*: the containment alarm attributes, says plainly when it cannot, and stopped crying wolf. **verdict: HOLDS.** Evidence green. Beyond it: `attribute_canonical_touch(touched, log_dir, sandbox_root=None, repo_root=None)` — the sandbox root A5 says was missing is a real parameter, which is the defect that produced the false containment failures. *refutation*: a signature without `sandbox_root`, or a replay in which a sandbox-local edit attributes.
- **A24** — the Desktop-mirror guard. **HOLDS**, evidence green. I ran nothing that writes to `~/Desktop` (rule 2), so my verdict rests on the guard's own tests rather than on live mirrors, and I say so rather than imply more.
- **A10** (git-stash ratchet), **A14** (per-seat sandboxes), **V3** (note-lint ratchet per file, exit status captured where it runs), **V8** (one `paragraphs()`, unconditional fence stripping), **V6** (`undeclared_figures()` present and importable alongside `check_declared_figures`/`check_currency`), **P2**, **P6** — **all HOLDS**, named evidence green, `model_bearing: none`. P2's `49 of 49 refused, Wilson [92.7302%, 100.0000%]` and `0 of 7, Wilson [0.0000%, 35.4330%]` reproduce to the digit under `statsmodels` and an independent closed form (agreement < 1e-12).

*falsifier for the group*: the single pytest invocation above. *control*: A23's two reverts show this harness distinguishes red from green; and A16's git probe demonstrates the suite fails loudly rather than passing vacuously when its instrument cannot answer.

---

# Group 2 — instruments

Named evidence re-executed: **131 passed, 11 failed, 1 skipped**. Of the 11 failures, **10 are no-git artefacts** and 1 was A23's real defect.

- **A1** — 77.7778% Wilson [45.2589%, 93.6775%], 24.8227% Wilson [18.4237%, 32.5571%]. Evidence green; I ran no Open Brain subcommand at all, read-only or otherwise, because the store is outside the sandbox and the evidence test already exercises the assessment. **HOLDS on its evidence**, and I mark the limit rather than claim the live store. *refutation*: a read-only subcommand count other than 9, or `list-epochs` now succeeding.
- **A2** — **HOLDS.** Five evidence files, all green.
- **A3** — **HOLDS.** `6 of 6, 100%, Wilson [60.9666%, 100.0000%]` reproduces with two tools (agreement `True`). Evidence green.
- **A7** — **HOLDS, and the producer reproduces the entry exactly.** `CRITICAL_SEVERITY_THRESHOLD` **read** from `bench/reference_runner_v3.py` (never typed) = **0.7**; `scripts/escalation_paths_2026-09-11.py` prints `22`, `11 irreducible / 8 merge deadlock / 3 stale contested`, `ANONYMOUS 0/22 = 0.0000%, Wilson [0.0000%, 14.8655%]` — which I reproduced independently (statsmodels vs closed form, agree `True`). The script also volunteers that its predicate is underdetermined by its anchor, quoting the family `{20, 22, 32}`. Whether 0.7 is the right threshold is out of scope; that A7's counts follow from it is confirmed. *refutation*: a predicate returning 25, or any escalation with no named mechanism.
- **A12** (all 15 ruled items accounted, 11 runway + 4 study), **A17** (verdict guard resolves the call by Python's scoping rule), **A18** (two of three config fields wired via `getattr(cfg, "...")`), **A25** (metamorphic false-zero probe imports the real scanners), **L1** (founder's words never counted, never gated, paraphrase still linted), **M2** (pulse hook; read, not modified) — **all HOLDS**, evidence green.
- **M1** — **HOLDS with a stated limit.** Six of its evidence tests fail in the sandbox because `scripts/task_list_entry_count_2026-09-10.py` walks all 27 revisions of the file and there is no `.git` (`build()` deletes it). Arithmetic half checked independently: `15/48 = 31.25%`, Wilson `[19.9%, 45.3%]` reproduces. The revision-history half I **could not** check here, and I decline to call it confirmed. *refutation*: running those six tests in a real checkout and finding them red there.
- **V2** — **HOLDS, and its repair is visible in its own failure.** The two red tests fail by raising `NotAGitCheckout: git ls-files exited 128 … fatal: not a git repository` — i.e. the instrument **refuses** rather than fabricating the 100% it once printed. That is V2's fix working, observed in the exact condition that produced the original defect. *refutation*: any figure emitted by that script outside a checkout.
- **V5** — **HOLDS**, evidence green. *model_bearing*: none.

---

# Group 3 — rulings written back

`bench/tests/test_rulings_written_back_2026-09-10.py` and `test_materiality_population_2026-09-10.py`: green. **R4, R5a, R7, R8, R9 — HOLDS.** R5a's null (`no single definition reproduces 11/6/2`, extended to 1,679 definitions, with a positive control) survives re-execution; its qualification about exp47's 2 being 2 *models* is carried in the entry rather than hidden.

- **R6** — **HOLDS with the same sandbox limit as M1.** Three tests fail with `assert 20605 in set()`: the git size-search returns empty with no repository. Note this is its **positive control** firing — the instrument does not report a clean result it cannot support, which is exactly what R6's entry claims for it. `35 of 39 = 89.7436%, Wilson [76.4211%, 95.9387%]` reproduces with two tools. *refutation*: those three red in a real checkout.
- *model_bearing* for the whole group: none. R4 quotes `kappa = -0.0227, Fisher p = 0.78` and names `bench/dm/_rk_proof.py`, but the entry's claim is "the ruling is written back into the documents", which is a documentation predicate, not a model predicate.

---

# Group 4 — withdrawals

- **A9** — *claim*: the removal should not happen; the file is deliberately preserved and a guard records why. **verdict: WITHDRAWAL_SOUND.** *model_bearing*: none. Checked by execution, not by reading the entry: the exemption exists verbatim in `NOT_PYTEST_MODULES` with its required reason (*"the archived artefact of what a reviewer wrote inside its sandbox … still names reference_runner_v2"*); the live copy is **159 lines** against the frozen **142**, and `python3 -m pytest bench/tests/test_repair_loop_wiring_2026-08-30.py -q` gives `8 passed in 0.61s`. Withdrawing rests on something that executes. *fix*: none needed. *refutation*: the exemption removed, or the live copy going red — then the frozen draft is the only record of those assertions and the calculus changes. **One caveat the entry should carry**: the exemption's own guard, `test_every_test_file_is_collected_2026-09-01.py`, hard-fails outside a checkout (`assert out.returncode == 0` on `git ls-files`) — the same class as A23's defect 2, though here it fails loudly rather than fabricating a verdict, so I did not spend the fix on it.
- **A15** — *claim*: the withdrawal was right; the archive is pre-fix by design and the suite pins it. **verdict: WITHDRAWAL_SOUND.** `bench/tests/test_adjudicator_rejects_errored_legs_2026-08-28.py` passes, including `test_the_archived_run_still_carries_the_defective_verdicts`. Both quoted rates reproduce with two tools: `18/133 = 13.5338%, Wilson [8.7353%, 20.3798%]` and `18/18 = 100%, Wilson [82.4121%, 100.0000%]` — statsmodels against an independent closed form, agreement `True`. *refutation*: the archive test passing after a regeneration — that would mean the pin is not pinning.

---

## Once, for the reply

**entries_not_reached**: none. All 34 carry a verdict backed by execution. Depth is uneven and stated per entry: **A23, A7, A16, A22, A9, A15, A5/A21, M1, V2, R6** were probed beyond their named evidence; the remainder rest on re-executing that evidence plus an import- or signature-level probe, which I have not dressed up as more.

**passes_run**: **2** over all 34, plus a third partial pass confined to A23 (the controls). Pass 2 produced one above-threshold finding (A23) and one demoted observation (A16's declared drift). I stopped there under Section 6: a third full pass would have been re-reading green tests, and naming "there might be more" is not a mechanism.

**strongest_disagreement**: three, in descending force.

1. **The brief misdescribes the artefact it sends, and the misdescription is the kind this repository built `task_list_markers.py` to prevent.** Section 1 says each entry "is a bold heading paragraph followed by a `<!-- task: … -->` marker". For the **59 supplementary entries that are the subject of this round**, that is false: under `# SUPPLEMENTARY LIST` they are **table rows**, `| \`A1\` | DONE | assistant | … |`, carrying no marker at all — which is exactly why `q9_engineering_entry_set` reads them with `^\| \`(ID)\` \|` and not with `parse_entries`. The bodies `parse_entries` returns are separate earlier entries that happen to share the identifiers. Both readings exist in one file, and a seat that followed the brief literally would have parsed the wrong objects. That the two happen to coincide here is luck, not design: `parse_entries` itself defines `end_of_entries` to stop bodies at the supplementary list precisely because the two regions were once confused, and `blocker_triage` already shipped a false W1 finding from that confusion.

2. **A23 should not have been sent as an engineering entry in isolation.** Its live defect is the *V2 defect class* — an instrument treating "git cannot answer" as an answer — and V2 is on the round-16 list, held back from me. A23's failure is evidence about V2's closure, since round 12's repair was written once and the same shape survived in a file written the same day. Splitting the two across rounds is why a defect can be closed and still be live three files away. **The deeper point**: the sandbox deletes `.git`, so *every* panel round runs in the condition that triggers this class, and rule 4 instructs seats to discount exactly these failures as artefacts. That instruction is right about 10 of the 11 failures I saw and wrong about one — and the one it was wrong about was a genuine live defect at HEAD. A rule that tells reviewers to discount a failure class is a place to hide a defect in that class.

3. **Nothing in the set depends on the mathematical model, and the boundary was drawn correctly**, with one entry close to the line: A7 reads `CRITICAL_SEVERITY_THRESHOLD` and R4 cites `_rk_proof.py`. Both claims are about counting and about documents, so `model_bearing: indirect` at worst, and I returned no MODEL_BOUND verdicts. On the other side, **A19 being held is the right call and R10/R11 with it** — but the three of them are held on three different grounds in the brief, and only one is stated as a founder ruling. That is worth tightening before the next dispatch.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 54 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round17_2026-09-17) -->

All 34 entries taken, all evidence executed, three defects fixed with revert-controlled falsifiers. Final report.

---

# Q9 engineering-entry review — seat verdict, 2026-09-17

**Method.** Entries read via `parse_entries` (95 entries; the 34-id set reproduced by `scripts/q9_engineering_entry_set_2026-09-17.py`, output quoted in my first command). Every named evidence file was executed with `python3 -m pytest <file> -q -p no:cacheprovider --netguard-strict`. All 12 claimed Wilson intervals reproduced with `statsmodels` `method="wilson"` against a scipy closed form, agreeing to <1e-9 and matching every entry's quoted bounds (output above). `CRITICAL_SEVERITY_THRESHOLD = 0.7` read from `bench/reference_runner_v3.py:6902`, never typed. No model API touched, no Wolfram, nothing written outside this sandbox, `~/.claude/hooks/task_list_pulse.py` read only, no Desktop write, no ACTION script run except none (I ran only MEASUREMENT-classified scripts, checked via `classify()` first).

## The three above-threshold findings

**Finding 1 — one defect class, three instances: DONE evidence that fabricates failures in a no-`.git` tree.** In this sandbox (no `.git`, by `build()`'s design):

- `test_task_list_entry_count_2026-09-10.py` (M1's evidence): **7 FAILED** with messages blaming the script ("the script that backs M1's figures…"), while `test_no_counter_reads_29_at_any_revision` **passed vacuously** — 0 revisions also prints "NONE". A fabricated failure *and* a control that cannot fail, from one missing precondition.
- `test_measurement_survey_is_safe_2026-09-11.py` (A16's evidence): **1 FAILED** on `git status` exit 128.
- `test_fresh_clone_is_actually_run_2026-09-11.py` (A2's evidence): **4 FAILED** on `git clone file://REPO` exit 128.

Each failure triggered the harness banner "task X is marked DONE and names a failing test… move the entry off DONE" — telling a ZIP/sandbox/archive reader that three sound entries are overclaims. This is task V2's class exactly, and the repository already holds the correct pattern: the desktop-mirror suite *skips with a reason* on the same precondition (quoted above). **Fix delivered:** reasoned `skipif`/`skip` preconditions in all three files, scoped to only the git-dependent classes (git-free tests still run: 23 passed in M1+A16's files post-fix, 6 passed in A2's). In a real checkout nothing is skipped, so no guard is loosened on any tree where it could ever have fired — the additive standard is satisfied in both directions.

**Finding 2 — A7's headline figure does not reproduce.** The entry says **25** archived escalated criticals with no falsifier, exp53 accounting for 10. Its own producer, run here, prints: **22** (11 irreducible_escalation + 8 merge deadlock + 3 stale contested), family **{20, 22, 32}** under candidate predicates, and *"THE ENTRY'S 25 DOES NOT REPRODUCE and its exp53 attribution cannot: that run keeps findings… with no escalation flag at all."* The evidence test passes because it pins the script, not the entry's prose — nothing bound the entry to its producer. **Fix delivered:** dated correction appended to A7 in the task list, plus a falsifier that both parses the entry *and re-runs the producer*, asserting they agree.

**Finding 3 — A17 and A22 assert present-tense defects their own passing evidence refutes.** A22: "cannot be imported at all… not touched" — I imported the dispatcher in a fresh interpreter with **no argv and no env workaround: imports clean**, exposes `main()`; bare run exits 2 with usage; `--help` answers usage (its evidence test executes all three). A17: "Worked around, not fixed" — the resolve-the-call fix exists (local-definition scoping; the evidence file documents and executes it). A reader acts on both false claims. **Fix delivered:** dated corrections appended to both entries.

**Falsifier for all fixes** (delivered at `bench/tests/test_q9_entry_corrections_2026-09-17.py`, 7 tests):

```bash
python3 -m pytest bench/tests/test_q9_entry_corrections_2026-09-17.py -q -p no:cacheprovider --netguard-strict
```

**Result after fixes:** `7 passed in 24.85s`. **Before fixes** the underlying red states are the quoted runs above (7F, 1F, 4F, and the absent corrections). **Controls, executed — each fix reverted in place, falsifier red, then restored green** (verbatim):

```
C1 M1 guard off : (1, '1 failed in 2.27s')   C1 restored : (0, '1 passed in 1.15s')
C2 A16 skip off : (1, '1 failed in 23.15s')  C2 restored : (0, '1 passed in 20.74s')
C3 A7 stripped  : (1, '1 failed in 0.26s')   C3 restored : (0, '2 passed in 2.30s')
C4 A22 stripped : (1, '1 failed, 1 passed')  C4 restored : (0, '2 passed in 0.14s')
guard off (A2)  : 1 '1 failed in 1.29s'      restored    : 0 '1 passed in 0.68s'
```

After all edits: `python3 scripts/task_list_markers.py --check` → **"task list coherent: 95 entries, 0 problems"**, and the markers' own test file still passes (27 passed).

**delivered_files** (all in-tree, will return via `changes()`): `bench/tests/test_task_list_entry_count_2026-09-10.py`, `bench/tests/test_measurement_survey_is_safe_2026-09-11.py`, `bench/tests/test_fresh_clone_is_actually_run_2026-09-11.py`, `experimental_notes/CDSFL_MASTER_TASK_LIST.md` (A7, A17, A22 corrections), `bench/tests/test_q9_entry_corrections_2026-09-17.py` (new).

## Per-entry verdicts

All `model_bearing: none` unless stated. For entries marked HOLDS, `falsifier_result` is the batch run quoted above containing that file; `control` is the named file's own executed positive/mutation controls (they ran green in my batches — e.g. A5's 9 tests with both-direction controls, A21's 3 verified-red mutations, R5a's positive control, R6's two positive controls), plus the harness's DONE-evidence banner, which I demonstrated fires on a red evidence file. `simplest_sufficient`: none needed where fix is none.

**Group 1**
- **A24** — claim: a clone's suite overwrote the founder's Desktop file; cause found and guarded. **HOLDS.** 51 passed + 1 *reasoned* git skip (the honest precedent the fixes above copy). Fake-Desktop fixtures only; real Desktop untouched. Refutation: a run of the guarded suite under a sentinel HOME rewriting a sentinel.
- **A16** — claim: the survey mixed ACTIONs into a read; declare, don't infer. **HOLDS**; classifier survey executed here: 128 scripts, ACTION share 71/128 = 55.4688%, Wilson [46.8243%, 63.7945%], two CP tools agreeing to 0.0e+00; "NOTHING WAS RUN" without `--run`; unresolvable-is-ACTION direction correct. Evidence file repaired (Finding 1). Refutation: `classify()` returning MEASUREMENT for a script that demonstrably writes.
- **A10** — claim: no live `git stash` harness; ratchet guards return. **HOLDS** (6 tests, 3 controls, passed). Refutation: a stashing harness in `scripts/` the call-matcher misses.
- **A22** — **PARTIAL** (defect was real when observed; prose now false — Finding 3, corrected). `model_bearing: none`. Refutation: the module-level `SystemExit` reappearing on clean import.
- **A14** — claim: shared sandbox couples seats; per-seat sandboxes needed. **HOLDS** — evidence executes build-per-seat, seat-prefixed diff keys, teardown, and two-builds-are-separate-trees; all passed. My own seat's isolated tree is live corroboration. Refutation: `build()` called once in `main()` with seats sharing one path.
- **A5** — claim: alarm attributes canonical touches, read≠write, sandbox-local excluded. **HOLDS** (9 tests, both-direction controls, passed). Refutation: `attribute_canonical_touch` flagging a `sed -n` read or a sandbox-local edit.
- **A21** — claim: the alarm's round-10 verdict was wrong; repaired attributor reports 0 attributable. **HOLDS** (positive controls + 3 verified-red mutations, passed). Refutation: replay of round-10 logs yielding attributable>0 under the repaired code.
- **V3** — claim: 2 lint-guard bypasses existed and are believed. **HOLDS and repaired in tree**: `hooks/pre-commit` `_lint_count` now returns the *linter's* status (the dead fail-closed branch is documented and closed at :329-341); evidence passed. Refutation: `sh -c` demonstration that `_rc` still reads the if/else.
- **V8** — claim: blocking lint forced falsifying verbatim records; exemption now scoped. **HOLDS** (evidence passed). Refutation: a verbatim-region commit refused, or the exemption leaking to non-verbatim text.
- **V6** — claim: brief figures had no guard; owed fix is figure-re-execution at validation. **HOLDS and the owed fix exists**: `check_declared_figures` re-executes declared figures; my negative control — a deliberately wrong `32 of 84` declaration — was refused verbatim: *"A number typed into a brief is a claim about evidence, not evidence"*; the correct declaration passed. This brief's own four figure declarations reproduced by my runs (59/7/16-of-31/34; 31 of 84 = 36.9048%). `model_bearing: none` (gamma appears only as the incident's subject). Refutation: a parseable wrong figure returning `[]`.
- **P2** — claim: a validated brief format now exists where 0 of 49 had one. **HOLDS** (107 passed across its two files; this dispatch is itself an instance, and its figures validate). Refutation: `panel_brief_validate.py` accepting a brief violating its own checks.
- **P6** — claim: that format is the standard for the paid panel. **HOLDS** (same evidence; the format test passed). Refutation: a paid dispatch route that bypasses validation.

**Group 2**
- **A25** — claim: 15 false-zero instances, one class. **HOLDS** (evidence passed) — and Finding 1 is instances 16-18 of the same class, in DONE evidence; the class is live.
- **A17** — **PARTIAL** (Finding 3, corrected). Refutation: the guard flagging a locally-defined non-tuple `scan()` again.
- **A18** — claim: 3 config switches read by no runner module. **HOLDS** (AST-resolved evidence passed; frozen files untouched, as the entry states). Refutation: an AST walk finding a reader of `merge_arbitration_enabled` under any name-alias.
- **A3** — claim: 6 of 6 checkable citations repaired; AST-span guard with two-direction controls. **HOLDS**; Wilson [60.9666%, 100.0000%] for 6/6 reproduced with 2 tools. Refutation: a named-symbol citation at HEAD outside its AST span.
- **A7** — **FAILS as written; corrected in place** (Finding 2). `model_bearing: indirect` — the count is parameterised by the 0.7 threshold but the claim audited is arithmetic over archives, not the model. `simplest_sufficient`: a text correction + producer-binding test; anything less leaves 25 believed, anything more re-litigates the founder's backlog decision, which stays his. Refutation: a predicate over the archives reproducing 25 with an exp53 escalation field.
- **A12** — claim: all 15 ruled items accounted, 0 of 15 unaccounted after declaration. **HOLDS** (evidence passed; 3/15 = 20.0000%, Wilson [7.0475%, 45.1854%] reproduced). Refutation: a ruled tracker item absent from both the list and A12's declaration.
- **M1** — claim: 15 of 48 = 31.25% at the pinned revisions; "29" was never a count of this file. **HOLDS on the claims; evidence repaired** (Finding 1). Wilson [19.9457%, 45.3331%] and the entry's rounded [19.9%, 45.3%] agree; revision-walk claims are executable only where history exists, which the repaired evidence now says out loud instead of failing. Refutation: `git show 4b697af:…` counting ≠15 under either pattern in a real checkout.
- **M2** — claim: pulse hook built, enabled, sharing the engine. **HOLDS**: hook exists at `~/.claude/hooks/task_list_pulse.py` (read only), registered as a UserPromptSubmit hook at `~/.claude/settings.json:42`, loads `scripts/task_list_markers.py` via importlib (its lines 42-61) — the shared engine, not a copy; marker tests passed. Refutation: the hook carrying its own parser, or absent registration.
- **V5** — claim: `rs` now offers the fresher source. **HOLDS** — evidence *executes* `first_read_lines` from `cdsfl_recover.py` and asserts the master task list and outcomes log are offered, newest first; passed. Refutation: `first_read_lines` ordering the stale tracker first again.
- **V2** — claim: the 11 overstated entries repaired, each named. **HOLDS** (evidence passed). Refutation: any of the 11 named figures still failing to reproduce from its producing script.
- **A1** — claim: 7/9 read-only subcommands functional, hash chain 24.8227%, one production caller. **HOLDS**: both Wilson intervals reproduced with 2 tools; 9 evidence tests passed. I did not re-run the assessment script — `classify()` marks it ACTION and the Open Brain DB lives outside every sandbox; the committed evidence and interval reproduction carry the verdict. `model_bearing: none`. Refutation: a second production import of `open_brain` outside `cdsfl_sv.py`, or an epochs table existing.
- **A2** — claim: fresh clone green at HEAD; five instruments guard it. **HOLDS on everything executable here**: 4 of 5 evidence files passed (109 passed, 2 reasoned skips); all 5 of its Wilson intervals reproduced; the 5th file repaired (Finding 1) so it skips honestly where it cannot clone. The clone-is-green headline itself is only assertable from a real checkout; nothing here contradicts it. Refutation: `scripts/fresh_clone_suite_2026-09-11.py` in a real checkout exiting non-zero.
- **A23** — claim: RECOVERY.md session state current with HEAD. **HOLDS** — its evidence already carries the correct no-git skip pattern and passed here. Refutation: newest block naming a commit not an ancestor of HEAD in a real checkout.
- **L1** — claim: linter never gates the founder's words. **HOLDS** (evidence passed; no founder text touched by me — my corrections quote nobody). Refutation: a lint path reachable from his input.

**Group 3** — R4, R5a, R6, R7, R8, R9 all **HOLDS**. `test_rulings_written_back` and the R5a/R6 files passed (10 tests each for R5a/R6, both with executed positive controls guarding against unfalsifiable nulls). Spot-checked by reading the targets: FW.7 row now says "RULED AND BUILT 2026-09-06/07" (R4); the sealing line in the operational plan is struck with "DONE BY THE FOUNDER HIMSELF, 2026-09-07 at 22:03" (R7); the BR2 test docstring carries his verbatim answer (R8); the load-balancer row says "SHELVED, NOT RETIRED — founder ruling" (R9). R5a's 1,679-definition null and R6's bounded-below-only blast radius are exactly what their scripts' tests pin. Refutation for the group: any target document line reverting to the superseded text, or R5a's search finding the triple.

**Group 4**
- **A9** — **WITHDRAWAL_SOUND.** Executed: live copy `bench/tests/test_repair_loop_wiring_2026-08-30.py` passes **8/8** (0.60s); the exemption exists verbatim at `test_every_test_file_is_collected_2026-09-01.py:36`; collecting `bench/tests/` reaches the live file, not the frozen draft. The refused removal would have destroyed a reviewer record — the additive standard cuts *for* this withdrawal. Refutation: the frozen draft being collected by the suite's actual invocation, or the live copy losing a test.
- **A15** — **WITHDRAWAL_SOUND.** Executed: `test_adjudicator_rejects_errored_legs_2026-08-28.py` passed, including `test_the_archived_run_still_carries_the_defective_verdicts` — the archive still holds the pre-fix verdicts, so the restoration is intact and the pin that caught the survey still bites. One note, no fix required: the withdrawn filing's "13.53%" has no producing script, but a withdrawn claim is not evidence anyone acts on. Refutation: that test failing, meaning the archive was regenerated again.

## Whole-reply fields

- **entries_not_reached**: none — all 34 taken.
- **passes_run**: 3. Pass 1: full evidence execution. Pass 2: targeted refutation and instrument reproduction (intervals, producers, imports, negative controls). Pass 3: post-fix sweep — edited files re-run, marker `--check`, falsifier suite + revert controls. Pass 3 produced no new above-threshold findings beyond the third instance of Finding 1's class, which is fixed; I stop here on diminishing returns.
- **strongest_disagreement**: Two. (1) The brief's instrument note says **A15** states "at least 1 proportion with an interval" — it does not; its only figure is the withdrawn 13.53%, no interval, no script. The interval-bearing entry the brief likely meant is **A12**, which I reproduced. Small, but a brief that validates its figures should not misattribute which entries carry them. (2) Section 3.6 asks, for every HOLDS, a control "showing that falsifier goes red once the change the entry describes is reverted" — for 32 entries that is ~32 in-place reversions of committed repairs; within a one-shot budget I substituted the named evidence files' *own executed* mutation/positive controls (which many of these files were explicitly built with) and performed true revert-controls only for the changes I authored. If the panel wants per-entry reversion controls for HOLDS verdicts, that is a second round's worth of work and should be budgeted as one. No entry sent here turned out model-bound; A7 is the closest (parameterised by the 0.7 threshold) and its arithmetic is decidable without touching the model.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round17_2026-09-17/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
