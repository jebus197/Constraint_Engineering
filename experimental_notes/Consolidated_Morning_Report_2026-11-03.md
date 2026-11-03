# Consolidated Morning Report — technical companion

**3 November 2026, 04:14 GMT**

Window: 27 commits, `600598d9` (2026-11-02 00:23) to `baac39b8` (2026-11-03 03:48), 211 files. The spoken companion is `Consolidated_Morning_Report_2026-11-03.txt`; this version carries the paths, counts and producers it omits.

## 1. His 3 questions

### 1.1 What is v-bar

**It is in the mathematical model and he has met it.** `docs/GLOSSARY.md:312` defines the 4-dimensional capability profile `(D, v-bar, A, C)` with *v-bar equals verification score (fraction confirmed by SymPy or similar)*. `docs/MATHEMATICAL_APPENDIX.md` writes the symbol 12 times: the 4-tuple at line 1327, the definition table at 1332 (*Mean verification score, All findings from this model*), the weight formula at 1207 (`w(y) = v̄(y) · u_qual(y) · (1 − S_sync(y))`), and the metacognition measurement at 778.

In code, `bench/dm/_manager.py:717` computes it as the fraction of a model's findings whose `verified` flag is true; `bench/dm/_role_assignment.py:81` scores a model as the dot product of a role's weight vector with that profile, v-bar second in the tie-break.

**Why he had never seen it: the spelling.** Measured — `experimental_notes/data/morning_report_decisions.json` used `v_bar` 12 times and `v-bar` 0 times; `experimental_notes/CDSFL_MASTER_TASK_LIST.md` used `v_bar` 20 times and `v-bar` 0 times. Note standard Rule 28 requires calling a thing what he calls it. **Fixed at source**: `task:B94`'s `title` and `what` now name v-bar with its gloss and its 4-tuple on first use, and the generated report renders it.

### 1.2 Are the decisions new

**The count confusion is the larger half and it is mine.** 5 figures, 5 populations, 5 producers:

| figure | population | producer |
|---|---|---|
| 12 | OPEN entries whose own text asks him for a ruling | `which_open_entries_already_have_his_ruling_2026-10-30.py` |
| 13 | Rule 27 findings still owed in the spoken report | `b96_the_report_against_the_note_standard_2026-11-03.py` |
| 14 | numbered decision slots in the morning report | `morning_report_build_2026-10-12.py` |
| 17 | OPEN entries of any kind — what the Stop gate counts | `task_list_markers.py` via `work_not_narrate.py` |
| 19 of 22 | live entries whose next action is his | `whose_move_is_it_on_each_entry_2026-11-02.py` |

**Substantive answer: 0 of 10 entries carrying a ruling of his hide it.** Split, because the 2 cases differ in cost: **0 of 3** presented as numbered decisions, Wilson 95% [0.000000, 0.561497]; **0 of 7** not presented, Wilson [0.000000, 0.354330]. B21 acknowledges in its title, B71 and B84 in their first sentence quoting him with the date, C0001 under outstanding work — *"YOU RULED THIS ON 2026-11-01; the work is outstanding"*.

**The defect his question found.** `which_open_entries_already_have_his_ruling_2026-10-30.py` answered 0 of 12 reading commit messages only; it never read the `ruled` and `his_words` fields of the file he is shown, which hold 10 entries. Recorded as **B99**. Guard: `bench/tests/test_a_prior_ruling_is_acknowledged_2026-11-03.py`, 13 tests.

**And my first fix was wrong** — it inferred "presented" from the presence of an `options` field and read 2 fields for acknowledgement, reporting 6 of 10 unacknowledged, **all 6 false positives**. It now runs the generator and reads its output.

### 1.3 Fold-back to the simulated runner

**Yes, by construction.** `bench/tools/run_simulated_experiment.py:39` is `import reference_runner_v3 as R`, with `bench/tools/sim_dispatch_shim` layered over it. There is 1 engine, so a repair to `bench/reference_runner_v3.py` reaches simulated runs without being copied. Measured: `_exec_backed` 2 and `bugzilla_verified` 8 in the engine, 0 in the shim — the shim does not need them. The 4-runner concern concerns older siblings whose experiments have completed.

## 2. The work, by theme

| theme | representative commits |
|---|---|
| severity mechanism and its bounds | `600598d9`, `4832fedd`, `cf62c319` |
| 23 seat designs judged, 40 unadopted verdicted | `701e7afa`, `a59fc3ac`, `c1ea2443` |
| `cy` given a deadline; Stop gate timeout | `b7cf4c13` |
| the model's own `VERIFIED` flag closing findings | `a0eb9d00` |
| my own instruments | `d1ccf3c3`, `130a8a35`, `01b6e408`, `d74a8450`, `baac39b8` |
| deliverables and the note standard | `9419b4b8`, `d6ea0538` |

2 of the 27 commits were refused by the board; both refusals are recorded in their own commit messages.

## 3. The error pattern — a proxy predicate, 4 times on 2026-11-03

1. **Import count for rigour.** 4 of a discovered population of 7 passed while resting an interval on a single route; 0 do now. Reproducible at the pre-repair revision: `counting_imports_ranks_producers_backwards_2026-11-03.py --rev d6ea0538`. B97.
2. **An interval on a census.** A Wilson pair was drafted for `1 of 4` complete-enumeration runs, which would answer what fraction of composer runs carry severity 0.90. Refused; a second *route* was added instead. B98.
3. **Field presence for "presented".** 6 false positives, section 1.2 above. B99.
4. **Commit messages for "has he ruled".** The field is named `ruled`. B99.

A fifth, in a test of mine: asserting `_max_severity({"A": None, "B": 0.4}) == 0.4` is satisfied by coercing `None` to `0.0`, so it could never fail for its stated reason. **A test of a maximum cannot detect a floor inserted beneath it.**

**And 2 process errors.** The working tree was edited twice while a board ran; the first caused a genuine refusal, because `bench/tests/test_recovery_memory_doc_repairs.py` is among the board's 120 guard files and counts memory files. A heavy `pytest` was also launched alongside the board's own, on a machine measured to hold about 2 such processes.

## 4. Open guard failures, pre-existing and already his decision

`bench/tests/test_the_morning_report_is_generated_2026-10-12.py` fails 2 Rule 10 line-limit assertions. **Measured contribution of last night's change: 0 lines** — the generated report is 366 lines both at `HEAD` and with the v-bar gloss, against a ceiling of 300. This is the structural tension recorded on **B96**: Rule 10's ceiling was written for a note and this file is a generated digest whose length tracks the number of open decisions. Neither test is on the board, so no commit is refused by it.

## 5. The discussion

**Recommendation: keep the 2 simulated experiments separate.** Ground: `composability-requires-a-measurement` — a composed solution is preferred only with a committed measurement that it dominates either part alone on a named property, and no such measurement exists. Two further grounds:

- The orchestrator experiment has an **unmeasured arm** by his own design note: a repair-adjudication arm with an executable criterion, and a monitoring arm with no defined predicate. Combining would confound a measurable arm with an unmeasurable one, which is the reason that entry already gives for splitting them.
- **Attribution.** A regression suite inside an experiment whose subject may rewrite code cannot attribute a failure: the fix, or the orchestrator having changed it.

**Order: regression first on the current engine (simplest sufficient), then the orchestrator against a characterised tree.** That ordering is **additive** — it adds a known-good baseline the second experiment is measured against, at the cost of 1 extra run.

**Accepted without reservation**: the isolated sandbox the orchestrator is not told about (it will hold authority over code, and a model that can see the sandbox can reason about being observed, while the behaviour being measured is how it acts when it believes its changes are real); and **building the actuator first**, since the 13-event detector, the pulse file, the role layer, the researcher-facing backend and the fix comparator are all measured as built, and the actuator's own precondition is recorded on B20.

**Outstanding and not claimed as done**: the sketch of his interaction patterns, to serve as the management template.

## 6. Not done, and why

- **Orchestrator build not started.** His message authorises it and carries `d`, says to run experiments only on running out of independent work, and recommends a pause so this report can be read. Acting on the authorisation while ignoring its marker would be the wrong half of the instruction.
- **No experiment started.** Full `cy` — which he specifically asked not be reduced — requires a terminal held on the live output and a check about every 60 s with pause-and-analyse on anything odd. That is incompatible with starting a run at 04:00 and going quiet.
- **`sv` owed and queued**: 12 commits against a threshold of 11 derived from this repository's history.

Written under CDSFL note standard v1.9 (1 November 2026).
