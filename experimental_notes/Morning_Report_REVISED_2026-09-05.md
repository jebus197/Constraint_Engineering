# Morning Report — revised for decisions

**2026-09-05, 12:40 BST (Saturday)**

**Supersedes `Morning_Report_2026-09-05.md`**, which recorded every step and correction in dense prose and is not usable for adjudication. That file is retained as the detailed record; this one is the decision surface. Spoken companion: `~/Desktop/CDSFL_tts/Morning_Report_REVISED_2026-09-05.txt`.

No new work is reported here. Same material, ordered for decisions.

---

## Part 1 — decisions waiting

| # | Decision | Why it needs you | Evidence |
|---|---|---|---|
| 1 | Adopt the discharge rule, or its alternative | Changes the verdict vocabulary | `The_Discharge_Rule_And_Its_Alternative_2026-09-05.md` |
| 2 | Correct the fix-acceptance gate's σ conflation | **Changes behaviour** — rejects 3.215% of currently-accepted fixes, Wilson [3.161%, 3.270%], every flip PASS→REJECT | `scripts/measure_sk_threshold_gate_fire_rate.py` |
| 3 | Commission 4 falsifiers → human queue to 0 | It is work, not a repair | `scripts/reproduce_rubric_human_queue_partition.py` |
| 4 | Relabel ~106 archived findings with unbacked tool-only status | Cannot be recreated, only relabelled. CONFIRMED slice: **65 of 116 = 56.0%**, Wilson [47.0%, 64.7%] | `scripts/measure_toolonly_status_without_falsifier.py` |
| 5 | Launch the D9/D11 comparison | Costs paid dispatches | `bench/exp56_configs/`, 69 tests |
| 6 | Enable either D12 setting in a real config | Changes convergence conditions — scientific decision | `test_d12_commissioning_end_to_end_2026-09-05.py` |
| 7 | Wire the FFAFP audit hook into `settings.json` | Built, tested, deliberately unwired | stanza described, not applied |
| 8 | Adopt `ν_eff = ν/\|D\|` | **The only item that changes the mathematics** | diagnosis verified by SymPy, z3, Wolfram |
| 9 | Impose a hard ceiling on agent counts | See Part 4 | measured below |

---

## Part 2 — outstanding, with a caveat that matters

A survey of every note and annotated RTF from 2026-09-02 onward produced **55 items** agreed or approved and apparently not done: **37 NOT_STARTED, 18 PARTIAL**.

> **CAVEAT.** Those verdicts were computed between 05:19 and 12:04 **while work was still landing**, so some are already stale. Of 4 spot-checked just now, **2 were already done** — including the push. The survey stored no per-verdict timestamps, so staleness cannot be bounded from the data. **Treat the list as candidates to re-check, not confirmed gaps.**

**Experiments never run** — exp50 physics, exp51 biology, the 4 exp52 factorial cells (configs exist, never launched); exp54 capstone has no config; exp55's target is spent; BR2 behind the founder's own hard stop.

**Numbers without their script** — 7 of them, including `282 of 711`, a 4.2% insufficient-fix rate, `27 tunables / 7 documented`, a 0.45 tool-check overturn rate. Each must be reproduced or withdrawn. This backlog **predates last night**.

**Machinery unwired** — no code path writes `MERGED`; counterfactual repair not connected to the merge site; spend meter unbuilt; metering not connected to the runner; fix-complexity module unwired.

**Housekeeping** — 23 note-lint findings across 5 notes from 2–3 September; 4 notes from 2 September still carry spelled-out numbers.

**The 18 PARTIAL** are mostly last night's work at *built and tested but not wired or launched*: D8 matcher, D10 catalogue, D9/D11 comparison, D11 seat-contrast restore, FFAFP audit hook.

Full list: `python3 scripts/salvage_task_reconstruction.py --json`

---

## Part 3 — completed since the last note

| Item | Status | Evidence |
|---|---|---|
| Panel rerun under working tools | **COMMITTED, VERIFIED** | 16 of 17 calls had been failing silently; after repair 49 calls, 0 errors |
| 2 appendix defects + a third found in passing | **COMMITTED, TESTED** | tests 31→35; `verify_appendix_numerical_illustration.py` reproduces all 6 rows |
| D12 commissioning | **COMMITTED, TESTED, NOT ENABLED** | 20 tests through the real launcher path, ON vs OFF |
| D13 rubric question | **ANSWERED** | nobody adjudicates; it is a schema lookup |
| Full test suite | **GREEN** | `5153 passed, 0 failed` under `--netguard-strict` |
| sv and push | **COMPLETE** | `origin/main == HEAD`, clean tree |

---

## Part 4 — three things that went wrong

Included because they bear on how much weight the numbers above carry.

**Agent count.** A survey workflow spawned **488 agents** over **4h45m** against a design of 30–50. Cause: the dedup key was the first 7 normalised words of a task title, collapsing only ~12.6%, so near-duplicates each drew their own verify agent. **Measured cost: 4,361,376 output tokens** for that job, plus **1,833,526** for the 8-agent build workflow — roughly **6.2M tokens in one night**, against a previous maximum of ~6 agents. The founder stopped it; stopping it was correct. Nothing was lost — the journal holds every completed agent's return value and `scripts/salvage_task_reconstruction.py` recovers them offline.

**The earlier report.** It catalogued every step and correction in dense prose, which is not the agreed note standard and defeats the purpose these notes serve. This file is the correction.

**Unreviewed staging.** `git add -A` swept 2 files into commits before I read them (`scripts/verify_rtf_annotation_attribution.py`, `scripts/absorb_rule_disagreement_2026-09-05.py`). Both reviewed afterwards and both sound, but the practice has stopped.

---

## Part 5 — the question that is still open

The survey was designed to end with a **completeness critic** whose only job was to report what the survey itself had missed. It never ran — the job was stopped before that phase. So *"what is still missing from Part 2?"* is genuinely unanswered, and Part 2 must not be read as complete.

Written under CDSFL note standard v1.7 (26 August 2026).
