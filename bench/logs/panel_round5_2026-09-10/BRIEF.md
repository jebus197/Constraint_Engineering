# PANEL BRIEF — round 5: a definitive account of the work list, and a diagnosis of the list itself

<!-- figure: gamma at 13 passes | scripts/ffafp_cycle_gamma_2026-09-10.py | 0.294998 -->
<!-- figure: cycle series | scripts/ffafp_cycle_gamma_2026-09-10.py | [11, 4, 2, 3, 6, 2, 3, 2, 9, 10, 4, 2, 1] -->

**Declared figures above are re-executed by `scripts/panel_brief_validate.py` before dispatch.** That mechanism exists because the round-4 brief told both seats gamma was 0.451 when it was 0.415413, crossing a `GAMMA_BANDS` boundary, and both seats caught it. If a figure in this brief is wrong, say so — it has happened twice.

## SECTION 1 — The question, in the founder's own words

He asked for two things.

**First: a definitive report.** Verbatim: *"look at the canonical work list and come up with a definitive report of what has been done/verified, what remains, and what new issues your work uncovered."*

**Second, and it is the harder one:** *"But what is the problem with this work list? Why are you struggling so much? Is it too big?"*

The canonical list is `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, 508 lines, 84 entries: 22 DONE, 57 OPEN, 2 BLOCKED, 3 WITHDRAWN. Its companion is `experimental_notes/CDSFL_OUTCOMES_LOG.md`. The task-state markers are parsed by `scripts/task_list_markers.py`.

**What has already been measured, so you do not repeat it.** On 2026-09-10 an audit ran 48 agents over 2,182 tool calls, one per DONE entry, each executing the entry's named evidence rather than reading it, with an adversarial reviewer on every overstatement alleged. Result: **22 audited, 0 fully supported, 19 overstated, 3 cleared on appeal.** But the headline misleads and the correction matters:

- **22 of 22 named test files PASS.** No completion claim rests on a failing test. The fixes execute. What fails is the prose describing them.
- At sentence level, **116 of 266 checked claims do not hold — 43.61%**, Wilson [37.78%, 49.62%].
- **12 of the 19 overstatements cite evidence that is not committed to git**, 63.16%, Wilson [41.04%, 80.85%]. 35 files have been uncommitted for over 7 hours. That is 1 root cause producing 12 verdicts.
- An earlier measurement of the same property gave 11 of 19. Fisher exact p = 0.0753 against today's 19 of 22, so the rate is NOT shown to have changed.

**The assistant's own hypothesis about the list, offered so you can attack it rather than inherit it.** The list may not be too big; it may be the wrong KIND of document. It is being used at once as a work queue, an evidence archive, and a correction log, and those three have incompatible update rules — a queue should be mutable, an archive immutable, a correction log append-only. Measured: **15 of 84 entries carry 2 or more in-place correction markers**, Wilson [11.13%, 27.39%]; **entry 1.1 has been corrected 8 times and cites 5 distinct dates in a single paragraph**. Entry size does NOT predict claim failure — Spearman rho 0.4001, p = 0.06506, Kendall tau 0.3071, p = 0.05737, both above 0.05 — which is evidence AGAINST "it is too big" as the explanation.

**A classification the assistant attempted and could not complete, handed to you.** Of the 116 failed claims, a regex over the auditors' own wording put 33 as "the world moved after the claim was written" and 13 as "never true", and **left 70 of 116 unclassified, 60.3%**. That instrument is too weak to support a conclusion. Classifying those 116 properly is the single most useful thing you could do, because the remedy differs: staleness needs a binding between a claim and the revision it was true of; never-true needs a producing script.

## SECTION 2 — Use the harness

**Form your answer by RUNNING things. A reply that reasons about these files without executing them has not answered.**

- **`scripts/task_list_markers.py`** — drive `parse_entries` and `check`. Do the entry states and the Rule 20 statuses agree? An earlier audit found 5 of 21 headings stating a status that disagrees with their own marker, and `check()` reads only the marker.
- **`scripts/ffafp_cycle_gamma_2026-09-10.py`** — execute it. The cycle stop criterion is this project's two-sided gate: **gamma at or above 0.30 AND 3 consecutive zero-discovery passes.** Both sides currently FAIL. Judge whether continuing to iterate on this list is the right use of the gate at all, or whether the gate is measuring the wrong process — the series mixes discovery modes (solo passes, agent fan-outs, panel rounds), and a Duane slope assumes a stationary process.
- **Wilson intervals** — re-derive at least 2 of the proportions above independently and say whether they agree. Every proportion you report needs an interval, cross-checked with 2 tools.
- **`severity`, `S_k`, `nu`, `rho`** — the additive standard says an addition nothing reaches is not additive. Several entries add guards. Ask, for the ones you sample, whether anything reaches them.

**Run the suite** if you need its state: `python3 -m pytest bench/tests/ -q -p no:cacheprovider --netguard-strict`. It is RED by exactly 1 test, `test_precommit_gate_cost_2026-09-10.py`, which pins a count at 169 that the uncommitted work moved to 174. It takes about 16 minutes; you may prefer to sample.

## SECTION 3 — Produce a fix, and test it

The deliverable is a report, but a diagnosis without a remedy is half an answer.

**Produce a concrete fix for the list itself**, and test it. Not advice — a change someone could apply. If your remedy is to split the document, say into what, name the files, and demonstrate on at least 3 real entries what each part would hold. If your remedy is a mechanical rule, write the checker and run it.

**Report the exact command you ran and the exact output.** Where you claim a test is weak, DEMONSTRATE it: mutate the source, assert the mutation APPLIED and that it lands on a line the fixture executes, run the test, report whether it went red. A mutation that applies to the file but not the executed path reads as SURVIVED and is not one — that has happened 3 times in this programme, most recently when 8 mutation tests were found to be writing their mutants where the script could not resolve its own repository root, so every mutant died at startup and every check passed against empty output.

**Work in the sandbox copy you are given. Do not modify the canonical tree.** Note that in round 4 one seat reported the shared sandbox losing most of its `bench/` tree mid-review — 8 files against the canonical 167 — and could not attribute it. If your sandbox degrades, say so and say which of your figures were taken before it did.

## SECTION 4 — What would refute you

State, before concluding, what evidence would overturn your own answer.

Specifically: if you judge the list sound and the fault the assistant's, name what a competent worker would do differently with this exact document. If you judge the document at fault, name the cheapest change that fixes it and say what it costs. If you think "too big" IS the right answer despite rho = 0.4001 at p = 0.065, say what measurement would settle it.

## SECTION 5 — Output shape

- `verdict` — CONFIRMED / REFUTED / PARTIAL on the assistant's hypothesis that the list is the wrong kind of document rather than too big
- `done_and_verified` — which entries are genuinely complete, with the command that proves each
- `remains` — what is actually outstanding, deduplicated, in the order you would do it
- `new_issues` — what this work uncovered that is on no list
- `claim_classification` — your split of the 116 failed claims into stale-but-once-true, never-true, and other, with the method
- `list_diagnosis` — the answer to his second question
- `fix` and `falsifier_result` — the remedy you produced and the output of executing it
- `refutation_condition` — Section 4's answer
- `strongest_disagreement` — your strongest disagreement with THIS BRIEF's framing. Disagreement is preserved as information; do not converge toward the brief or toward the other seat.
- `passes_run` — how many

## SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could let a false completion claim stand, break a live run, or feed the founder a stale fact as a current one. Diminishing returns is this project's own criterion and it applies to you. Do not generate findings for their own sake and do not police style.
