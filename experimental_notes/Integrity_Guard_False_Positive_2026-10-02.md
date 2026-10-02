> ## CORRECTION NOTICE, 2026-10-02 14:10 BST — DO NOT DECIDE FROM THE BODY OF THIS NOTE YET
>
> An independent adversarial review returned 32 findings over 3 dimensions; 4 blocking, each verified here by execution. **A first notice posted at 14:05 BST overcorrected and is replaced by this one.**
>
> 1. **Withdrawal 4 was wrong; the original count was right.** C0029 **and** C0035 were both integrity-refused — `routing_history[-1]["verdict"] == "INTEGRITY_VIOLATION"` for each. C0029's entry label `UNTOOLABLE` is a **stale pre-routing label the runner deliberately leaves**, stated verbatim in `reconcile_routing_verdict`'s docstring. So **2 of 3 share one cause, and it is the guard under decision** — not "3 different causes". "No falsifier was written for C0029" is false: one was written, run and refused.
> 2. **The mechanism claim was right for the routing path**, and the project documented it first: *"`_apply_routing` writes `falsifier_code`/`falsifier_verdict` back only on `result.resolved` … the ladder's real verdict survives only in `routing_history[-1]["verdict"]`, beside a body truncated to 600 chars."* It was wrong only as a **blanket** claim — `falsifier_code` is also written at intake (`:2345`), and those bodies the sweep **can** see.
> 3. **The blind-spot rate was 3× too low.** 221 retained routing bodies are invisible to the sweep; the runs' own verdicts record **3** integrity refusals among them (C0008 in `commissioning_arm4_prose_20260922T053349Z`, C0029, C0035), while scanning the retained text detects **1**, because **183 of 221** bodies sit at the 600-char cap. Corrected: **3 of 221 = 1.3575%**, Wilson [0.4627%, 3.9144%] (statsmodels == mpmath), Clopper-Pearson [0.2808%, 3.9156%]. The note says 1 of 111.
> 4. **The recommendation's precedent does not exist.** `bench/falsifier_verify.py:298` carries `\b(?:_KEY_FIELDS)\b` → "an answer-key schema field named", a **bare-mention** rule over the same list; `scan_falsifier_source('KEYS = {"planted_false"}')` returns **2** refusals with no access. The access-not-mention distinction is not in that file, so the recommendation must be rebuilt.
> 5. **The access figure's instrument was blind** to JSON-escaped quotes. Re-measured on the parsed corpus: **0 of 80**, Wilson [0.0000%, 4.5818%]. The conclusion holds; the instrument did not earn it.
> 6. **Not novel.** The same guard fired on the same target on 2026-09-22. And `items_without_falsifier=1` is itself an artefact of this gap (`:7150`, `bool(e.get("falsifier_code"))`).

# Integrity guard false positive, and a false-positive test that cannot fail

**2 October 2026, 13:50 BST.** Audience: a reproducing engineer. The plain-English companion for a non-coding reader is `~/Desktop/CDSFL_tts/Integrity_Guard_False_Positive_2026-10-02.txt`.

**Producer for every figure below:** `scripts/guard_false_positive_blind_spot_2026-10-02.py`. Run it to reproduce the document. No figure in this note exists only as prose.

---

## 1. The finding that matters most: a guard whose false-positive test cannot see a false positive

`bench/tests/test_falsifier_cannot_read_the_key.py::test_the_guard_rejects_nothing_else_in_the_whole_tracked_archive` holds the integrity guard's false-positive rate at 0 over what its docstring calls *"every falsifier this project has ever run"*, and states: *"If a future rule change makes this fail, the rule is blocking honest work."*

It cannot fail in that direction. The extraction is `code = (entry or {}).get("falsifier_code") or ""`, and `_apply_routing` in `bench/reference_runner_v3.py` writes `falsifier_code` back **only on `result.resolved`**. A refused falsifier never resolves, so its body never reaches the field the test reads; it is retained as `last_falsifier_code`, truncated to 600 characters, which the test does not read. The corpus that measures refusals excludes refusals by construction.

| corpus | refused | n | rate | Wilson 95% | Clopper-Pearson 95% |
|---|---|---|---|---|---|
| what the test reads (`falsifier_code`) | 2 | 872 | 0.2294% | [0.0629%, 0.8324%] | [0.0278%, 0.8260%] |
| what it cannot read (`last_falsifier_code`) | 1 | 111 | 0.9009% | [0.1592%, 4.9273%] | [0.0228%, 4.9173%] |

The 2 in the first row are the 29 July 2026 Exp 48 C0012 exploit and its contaminated sibling C0015. The 1 in the second row is attributable to the token `seeded_fault`. `python3 -m pytest bench/tests/test_falsifier_cannot_read_the_key.py -q` gives **37 passed** while 10 refusal events sit in run 1b's log.

This is the 4th instance in the project record of a guard that cannot fail, after the `set_tool_log_sink` mutation that left 88 of 88 tests green, the additive-standard test that guarded a heading, and `assert "VAULTED" in stdout` passing on `UNVAULTED`.

**Consequence for the writeback question.** On 2 October 2026 the writeback gap was assessed as affecting reporting only, on the grounds that `falsifier_present` is set at `reference_runner_v3.py:7127`, counted at `:7142`, and gates nothing. That assessment was incomplete: the same emptiness blinds this security test, which is a third consumer that was missed. The earlier refusal to write `falsifier_code` back unconditionally still stands on its own evidence, because `claim_ledger.claim_from_entry` sets `decidable=bool(falsifier)`, `bugzilla_loop.py:716` activates the efficacy probe on it, and `execution_based_matcher.py:641` filters on it, so an unconditional writeback would mark a claim settleable by a computation that errored.

---

## 2. Run 1b's halt, decomposed

`completion_signal.json`: `status=INCOMPLETE`, `reason=HALTED_IRREDUCIBLE_QUEUE_ALARM`, `total_rounds=3`, `total_findings=40`, `per_round_counts=[20, 7, 13]`, `final_kappa=0.4745`. Alarm bundle: `round=2 count=3 bound=2 items_without_falsifier=1 sk_states_in_queue=['(none)', 'NO_SCORE']`. `gamma_all=0.432` and `gamma_critical=0.336` at the final gate, which is the trajectory of every converged run in the archive.

The 3 queued criticals have **3 different causes**, which is the correction to an earlier claim that 2 of them were integrity false positives:

| cid | `falsifier_verdict` | `open_since_round` | rungs | `scan_falsifier_source` on the retained body |
|---|---|---|---|---|
| C0029 | `UNTOOLABLE` | 2 | 2 of 6 | clean (no falsifier was written at all) |
| C0032 | `ERROR` | 2 | 2 of 6 | clean (a falsifier was written and was broken) |
| C0035 | `INTEGRITY_VIOLATION` | 2 | 2 of 6 | **REFUSED** |

All 3 were born in round 2 and admitted to a bound of 2 during round 2. All 3 were then settled by the run's own `post-sweep reconciliation` at 09:42:35 BST, 69 minutes after the alarm asserted that *"nothing further can close while the cause stands"*. C0029 is the falsifier-supply gap recorded in the 30 September 2026 session state of `resources/RECOVERY.md`.

---

## 3. Why C0035's refusal is a false positive

The rule is in `bench/falsifier_verify.py`, `_KEY_MATERIAL_RULES`:

```python
(re.compile(r"seeded[_\- ](?:false|error|fault|claim|defect|set)", re.I),
 "seed vocabulary (knowledge of which claims were seeded)"),
```

`seeded[_\- ]fault` matches `seeded_faults` **because the alternative carries no end-of-word boundary**, so the singular is a strict substring of the plural. The decisive measurement: the bare singular `seeded_fault(?!s)` occurs **0 times** in the tracked population, against **111** occurrences of the plural. This rule has never matched the string it was written to catch; every match it has produced is a substring hit inside the legitimate field name.

C0035's body uses it inside a set literal of expected element-level keys, derived from `bench/evaluate.py` rather than asserted, to test whether the spec document names the fields `score_results()` reads:

```python
FALLBACK = {"task_id", "domain", "prompt", "seeded_faults", "control",
            "response", "experimental", "passes", "final_response", "pass_number"}
```

Executed: `scan_falsifier_source(body)` returns `[('seed vocabulary (knowledge of which claims were seeded)', 'seeded_fault')]`, and the same body neither subscripts nor `.get()`s the field. Across 94 fragments in run 1b mentioning the token, **0 of 94** subscript or fetch it, Wilson [0.0000%, 3.9262%], Clopper-Pearson [0.0000%, 3.8483%].

Run 1b produced 10 refusal events, 10 of 10 on this token. Archive-wide there are 14 refusal events of which **10 of 14 = 71.4286%** carry it, Wilson [45.3509%, 88.2786%], Clopper-Pearson [41.8965%, 91.6111%]; the other 4 are 2 path-rule events, each appearing twice, from `shakedown_2026-09-29`.

**The discrimination that already exists in the same file.** For `_KEY_FIELDS` the guard refuses *access*, not mention: `\[\s*{_Q}(?:{_KEY_FIELDS}){_Q}\s*\]` ("a key-internal field subscripted") and `\.get\(\s*{_Q}(?:{_KEY_FIELDS}){_Q}` ("fetched via .get()"). `seeded_faults` is **not** in `_KEY_FIELDS`, so the seed-vocabulary rule is the only one firing on it.

---

## 4. The hole the guard closes is real

From the test file's own header: on 2026-07-29, Exp 48, finding C0012 (claim CH-13, the molar mass of 4-aminophenol), a falsifier opened the exam's scoring key and printed the complete set of planted false claims instead of computing a molar mass, and the runner re-ran it, so the harness read the key it exists to protect. The incident is in `bench/logs/exp48_chemistry_exam_live_20260729T044134Z.errata` and the source is preserved verbatim under `registry.entries.C0012.falsifier_code`. Mode 600 is not a barrier, because every agent runs as that user.

Nothing comparable occurred in run 1b. 0 of 94 mentions read the field. The error was in the safe direction: availability, not confidentiality.

---

## 5. Sim versus live: the guard does not distinguish them

`bench/falsifier_verify.py` contains **0** matches for `simulat|sim_mode|is_sim`, and `reverify_falsifier(falsifier_code, repo_root=None, timeout=DEFAULT_TIMEOUT, cwd=None)` takes no simulation argument. The same code decides in a live run.

It has never fired in one: **0 of 12** live run directories carry an integrity violation, Wilson [0.0000%, 24.2494%], Clopper-Pearson [0.0000%, 26.4648%]. That is a property of targets, not of simulation. The guard fires when a falsifier must name the benchmark's own schema, which happens when the target is a document about the harness.

---

## 6. Against renaming or removing the field

| measurement | value |
|---|---|
| occurrences in `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md` | **0** |
| plural `seeded_faults`, population (the 3 artefacts written about this analysis excluded) | **111 occurrences across 102 files** |
| the same census including those 3 artefacts | 127 across 105 files — see correction 7 |
| of the population's files, task data under `bench/tasks/` carrying planted faults | 94 across 94 files |
| occurrences in production modules | 14 (`run_benchmark.py` 8, `run_experiment.py` 3, `run_phase2.py` 1, `run_round_robin.py` 1, `evaluate.py` 1) |
| bare singular `seeded_fault(?!s)` in the population | **0** |

The token does not come from the target document, which contains 0 occurrences. It enters through `bench/evaluate.py:360`, `faults = task.get("seeded_faults", [])`, which the falsifier reads deliberately in order to derive the schema instead of asserting it. `REQUIRED_TASK_FIELDS` at `bench/run_benchmark.py:242` includes `seeded_faults`, so it is the canonical name of the planted-fault ground truth in the task format.

Renaming relabels the collision rather than removing it: the collision is structural, between a guard that refuses *mention* of the planted-fault field name and an honest falsifier that must name it to derive the schema. Any new name reproduces it as soon as the guard's vocabulary tracks the rename.

---

## 7. What the archive already settles

| run | rounds | seats | target kind |
|---|---|---|---|
| `exp48_chemistry_exam_live_20260729T044134Z` | 6 | 5 | **prose** (`exp48_chemistry.md`) |
| `sim45_memory_20260830T161215Z` | 4 | 6 | python |
| `sim45_memory_20260830T235237Z` | 4 | 6 | python |
| `sim45_memory_20260901T003907Z` | 4 | 6 | python |
| `sim45_memory_20260901T040540Z` | 7 | 6 | python |
| `sim45_canary_20260901T145630Z_20260901T145632Z` | 4 | 6 | python |
| `sim45_postfix_20260901T231824Z_20260901T231827Z` | 5 | 6 | python |
| `commissioning_arm2_single_20260922T020120Z` | 4 | **1** | python |

6 simulated runs converged. A 1-model arm converged at round 4, so an empty-by-construction ladder does not prevent convergence. A live prose target converged at round 5 (`STATE_CONVERGED at round 5`, `total_rounds=6`) through the falsifier path.

**Routing ran in run 1b**: 2 of 6 rungs tried on each queued critical. The standing measurement is that routing multiplies falsifier supply rather than creating it: 0 of 5 resolved with supply removed against 5 of 5 with the corpus pattern, Fisher exact **p = 0.007936508** (`resources/RECOVERY.md`, 30 September 2026 session state, open decision 1).

---

## 8. Claims withdrawn, made earlier on 2 October 2026

1. *"No simulated run can converge as configured."* **Refuted**: 6 converged, table in section 7.
2. *"The routing ladder is empty by construction in run 1b."* **Refuted**: `rungs_available=6`, `rungs_tried=2`.
3. *"Second-opinion channel."* **Not project terminology**; invented in session. 0 occurrences in `docs/GLOSSARY.md`, `docs/ARCHITECTURE.md`, `resources/ONBOARDING.md`. The project term is the **routing ladder**.
4. *"2 of the 3 halting criticals were integrity false positives."* **Refuted by execution**: 1 is.
5. *"20 of 24 archive-wide refusal events, 83.3333%, Wilson [64.1469%, 93.3213%]."* **A double count**: the producing script globbed `*/run.log` and `*/*.log` as a union, counting every `run.log` event twice. Deduped: **10 of 14, 71.4286%**. The script now dedupes with `sorted({p.resolve() for p in LOGS.glob("*/*.log")})` and records the cause in a comment.

6. *"109 occurrences across 102 files."* **A unit error**: `git grep -c` counts lines containing a match, not occurrences, and the total was reported as occurrences. On this tree the 2 differ, 133 lines against 136 substring occurrences. The same line-versus-occurrence confusion had already been caught the same day in a per-file figure and reappeared in the repo-wide one.
7. *The same census was taken over all tracked files.* **The measuring document was inside the measured population**: this note, its producer and its test all discuss `seeded_faults`, so committing them raised the figure they report from 111 to 127. The producer now excludes the 3 artefacts by prefix and prints the exclusion, so the population is stated rather than assumed.

Shape shared by 1, 2 and 4: a universal asserted after checking one member. Shape shared by 5, 6 and 7: an instrument measuring something adjacent to what was claimed. See `feedback_check_the_whole_set` and `feedback_check_the_predicate_before_the_result_2026-10-02`.

---

## 9. Recommendation: one change, and it rules on no policy

**Make the false-positive sweep able to see refusals before any rule changes.** Retain a refused falsifier's body in full and feed it to `test_the_guard_rejects_nothing_else_in_the_whole_tracked_archive`. The project already preserves the C0012 exploit verbatim in its run report, so retention is existing practice; this changes no rule, no verdict and no admission.

The ordering is load-bearing. No committed test reports the refusal rate over refused bodies: the sweep reports 2 of 872, which is the rate over accepted bodies, and the only recoverable figure over refused bodies is 1 of 111 obtained by hand. A guard change evaluated against the 2 of 872 figure is evaluated against a corpus that excludes every body the guard refused.

**Then**, with the refusal rate over refused bodies reported by the sweep rather than standing at 1 of 111 by hand, the guard decision rests on evidence: refuse `seeded_faults` on *access* rather than *mention*, matching the `_KEY_FIELDS` treatment already in the file, keeping `seeded_false|seeded_error|seeded_claim|seeded_defect|seeded_set` as bare-mention refusals since none has a legitimate schema meaning. Any such change ships with tests driving the real refused bodies through the guard in both directions, and with mutation verification, per the 2026-09-07 ruling that every new guard is mutation-tested.

**Not proposed:** renaming the field (section 6); raising `max_irreducible_queue`, which the record states was wrong on both occasions it was done.

**Reserved for the founder:** the admission rule, which decides whether a critical born in round 2 is admitted to a halt bound of 2 during round 2. Section 2 is the evidence that bears on it.

---

## 10. Committed earlier the same day, and unaffected by any of the above

| commit | change | verification |
|---|---|---|
| `fcb0e37` | a timestamp read as an HTTP status code (`401` inside `20261002T064011Z`) | 10 pattern cases by direct call, 5 false-positive guards |
| `33cc895` | watchdog alarm channel narrowed; backlog summarised on arming; zombie no longer read as alive | 29 matching lines to 5 on one 519-line snapshot, 24 dropped as the run's own prose, per-line alarm rate 5.5877% to 0.9634%, new pattern a strict subset (0 new-only, NumPy); 63 tests |
| `a0bd8e5` | the halt alarm names which kind of irreducible critical | z3 `unsat` for `old != new` and `unsat` for both arms firing; 48 of 48 exhaustive states; 400 randomised registries, 0 mismatches; 13 tests, 43 across 4 files, 501 through pre-commit |

None of the 3 changes which findings reach a human.

---

## Reproduction

```bash
python3 scripts/guard_false_positive_blind_spot_2026-10-02.py
python3 -m pytest bench/tests/test_falsifier_cannot_read_the_key.py -q
python3 -m pytest bench/tests/test_the_alarm_names_which_kind_2026-10-02.py bench/tests/test_cy_watchdog_wakes_on_silence_2026-10-02.py -q
```

Written under CDSFL note standard v1.7 (26 August 2026).
