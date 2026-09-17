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
