# Consolidated report: all work from 2026-11-02T09:40 to 2026-11-04T00:22

**This is the technical companion to `~/Desktop/CDSFL_tts/Consolidated_Report_Since_Yesterday_Morning_2026-11-04.txt`.** The spoken copy carries the prose and omits every path and identifier so that a text-to-speech reader does not have to pronounce them. This copy restores them, and adds the producer behind each figure so any number here can be re-executed rather than trusted.

**Window:** 2026-11-02T09:40:10Z to 2026-11-04T00:22, which is 38 h 42 m. **23 messages** from the founder, **34 commits**.

---

## 1. The central finding: his mid-turn words are stored where no instrument looked

**The question it answers is his, asked repeatedly**, most recently as *"your occasional tendency ... to skip over things and to appear at times to be unable to parse plain English"*, with the worry that *"we may be pursuing increasingly 'esoteric' solutions to a fundamentally basic problem"*. The worry was correct. The cause is not comprehension.

**How the harness stores it.** A message typed while a turn is already running is recorded as:

| field | at the prompt | mid-turn |
|---|---|---|
| `type` | `"user"` | `"queue-operation"` |
| text location | `message.content` | **top-level `content`** |
| `message` dict | present | **absent** |
| `promptSource` | `"sdk"` | **absent** |
| delivery to the model | the user turn | `<system-reminder>`, `renderedRole: "system"` |

A second entry of `type: "attachment"` carries the same text as `attachment.queued_command`, and a third `queue-operation` records `operation: "remove"` with `reason: "absorbed_mid_turn"`.

**The measurement.** Producer: `scripts/his_messages.py` (its `census()`), guard `bench/tests/test_his_words_are_read_from_both_records_2026-11-03.py`.

| | count |
|---|---|
| distinct messages of his, union of both records | **1,421** |
| recorded both ways | 1,120 |
| recorded only as `type: "user"` | 95 |
| **recorded only as `queue-operation`** | **206** |

**206 of 1,421 = 0.144968**, Wilson 95% [0.127620, 0.164231], Clopper-Pearson [0.127060, 0.164358], 2 implementations agreeing to 2.8e-17. Excluded as not his writing: 3,230 entries across 7 named predicates (3,060 task notifications, 97 compaction summaries, 62 interrupt markers, 6 local commands, 5 `cy` heartbeats).

**Every transcript consumer in the repository read the first shape only:** `scripts/harvest_tickets_2026-10-17.py`, `scripts/a_compaction_summary_can_invent_his_question_2026-11-03.py`, `scripts/depth_and_breadth_are_measurable_2026-10-25.py`, `scripts/founder_decision_ledger.py`, `scripts/pass_b_his_rulings_2026-10-11.py`, `scripts/the_chat_half_was_blind_2026-10-28.py`, `scripts/triage_open_founder_decisions.py`, `hooks/ffafp_audit.py`.

### 1.1 A claim of mine withdrawn under `failure-later-refutation-protocol`

**Claimed** (2026-11-03, `scripts/a_compaction_summary_can_invent_his_question_2026-11-03.py`): a compaction summary INVENTED his question about `v_bar`; **0 of 1,719** typed messages and 0 of 839 annotations, against 4 summary hits as the anti-vacuity control.

**Refuted by:** his message at **2026-11-03T03:56:55**, *"What is v-bar? I have never heard of it before? Is it part of the mathematical model?"*, typed mid-turn.

**What the original pass had assessed, and it was not careless:** a 3-way partition, a 2-sided prediction so a broken search could not produce a negative, the regex pinned both ways, and the prefilter proved lossless against an exhaustive decode. **All of that held and all of it guarded the SEARCH. None of it asked whether the instrument was pointed at EVERYTHING.** The anti-vacuity control was satisfied by summary text, so it could never have surfaced this.

**Corrected run:** `1 of 1421 = 0.000704`, Wilson [0.000124, 0.003975]; verdict `HE DID WRITE IT -- the summary was faithful.`

**A second error inside the first correction, stated because it cut the other way:** teaching `_partition` the queue record took the denominator from 1,719 to **5,463**, because a raw row count double-counts every mid-turn message and admits the harness's own queued notifications. The denominator now comes from `his_messages.distinct()` and reads 1,421. And the control line printed `0 in anything he wrote` unconditionally, 1 line below the verdict it contradicted.

**Memory corrected:** `feedback_a_compaction_summary_can_invent_his_question_2026-11-03.md` rewritten to record the withdrawal; the `MEMORY.md` pointer rewritten.

### 1.2 And he annotated nothing in this window

Newest file he has written in: `Responses/Closing_Report_2026-11-01.txt`, 2026-11-01 21:20. **0 annotations since 2026-11-02.** So every instruction in this window arrived through chat — the one half that was blind to his mid-turn messages. The 2 findings are the same finding.

---

## 2. The shape of the work, before the list of it

Across the **213 files** the 34 commits touched (`git diff --name-only e4b83b25~32 e4b83b25` plus tonight's 2):

| area | files | share | Wilson 95% |
|---|---|---|---|
| instrument: producer (`scripts/`) | 87 | 0.408451 | [0.344628, 0.475517] |
| documentation | 55 | 0.258216 | [0.204091, 0.320908] |
| instrument: guard (`bench/tests/`) | 43 | 0.201878 | [0.153473, 0.260846] |
| **product: harness code** | **12** | 0.056338 | [0.032518, 0.095877] |
| run artefact | 10 | 0.046948 | [0.025698, 0.084250] |
| ticket store data | 3 | 0.014085 | [0.004801, 0.040584] |
| **product: gate/hook** | **2** | 0.009390 | [0.002579, 0.033583] |

**PRODUCT: 14 of 213 = 0.065728**, Wilson [0.039553, 0.107289]. **INSTRUMENT: 130 of 213 = 0.610329**, Wilson [0.543435, 0.673313].

The 14 product files: `bench/cdsfl_registry/composer.py`, `bench/cdsfl_registry/models/Fable.toml`, `bench/fix_comparator.py`, `bench/model_admission.py`, `bench/openrouter_tools.py`, `bench/proof_verify.py`, `bench/reference_runner_v3.py`, `bench/runner_core.py`, `bench/seat_readiness.py`, `bench/tools/cy_actuator_2026-11-03.py`, `bench/tools/run_simulated_experiment.py`, `bench/ux_backend_2026-10-20.py`, `hooks/cy_monitor_gate.py`, `hooks/work_not_narrate.py`.

**This partly supports his own suspicion**, raised 2026-11-02: *"there has been no significant drama, is probably attributable to the fact that you haven't actually done very much of the agreed work?"* The fair reading is that the work was real and was overwhelmingly measurement and guarding rather than new capability.

**Where the errors were.** Producer: `scripts/how_many_of_the_nights_errors_were_instruments_2026-11-03.py`. **16 of 18 recorded errors were in INSTRUMENTS, not subjects: 0.888889**, Wilson [0.672002, 0.968980], Clopper-Pearson [0.652880, 0.986249]. 1 PROCESS, 1 SUBJECT. Stated limit: it counts errors that were RECORDED, so it describes the written record and not every mistake made.

---

## 3. Tonight's repairs

### 3.1 B106 — `test_a_tracked_row_whose_entry_is_open_has_not_settled_its_ticket` refused his own `reopen`

`test_a_tracked_row_whose_entry_is_open_has_not_settled_its_ticket` in `bench/tests/test_every_annotation_verdict_names_its_evidence_2026-10-17.py` tested `store.unconfirmed()` — 1 status — where its own docstring and assertion say *"their tickets have been SETTLED anyway"*. Settled is the complement of LIVE.

**Proved 2 ways:** set algebra gives `settled & live == {}` and `settled | live == STATUSES`; z3 returns `unsat` for both *a status is both* and *a status is neither*. The 2 formulations differ on 6 statuses — CONTESTED, CORROBORATED, OPEN, REOPENED, UNDECIDED, WITHHELD — all LIVE.

**Dominance, as a widening requires:** `{s : new(s) and not old(s)}` is **EMPTY**, so 6 false-positive classes removed, **0 true positives lost**. `live` and not `not settled`, because a row with no ticket is in neither set and the weaker reading would excuse it.

**Realised only on his escalation:** 0 of 93 TRACKED rows before the reopen; **1 of 93 = 0.010753**, Wilson [0.001901, 0.058419], after.

**A claim of mine refuted by FOLLOW before the edit:** the preceding session stated a simulated reopen cleared the guard. Executed on a copy of `bench/tickets/tickets.jsonl`, it did not.

Producer `scripts/a_guard_cannot_refuse_his_own_remedy_2026-11-03.py`; guard `bench/tests/test_a_guard_cannot_refuse_his_own_remedy_2026-11-03.py`, 10 tests, **6 mutations red**, every restore sha256-verified.

### 3.2 B103 — 7 reds in the 54 guards outside the commit gate

`hooks/pre-commit` states its own scope: *"SO THE SCOPE IS THE GUARDS WRITTEN SINCE 2026-10-29"*. **104** guard files carry such a name; **49** were in `GUARDS`; **55** were not. Running all 55: **5 failed, 646 passed, 1 skipped, 292.97 s**. Repairing 2 exposed 2 more, so 7 in total.

| # | file | cause |
|---|---|---|
| 1,2 | `test_a_bare_clock_is_dated_from_the_header_2026-11-03.py` | probes added hours to wall-clock `now`, which wraps past midnight after 21:00 |
| 3 | `scripts/a_bare_clock_was_dated_from_the_mtime_2026-11-03.py` | same defect in its own self-check; exited 1 |
| 4 | `test_an_interval_rests_on_two_routes_2026-11-03.py` | `what_a_simulated_run_would_actually_test_2026-11-03.py` had Wilson on statsmodels alone |
| 5 | `test_tonights_producers_are_reached_2026-11-03.py` | 13 producers in neither list; 12 predate the addition that exposed them |
| 6 | `score_the_orchestrator_arm_2026-11-03.py` | exit 2 is correct: it needs `--run` or `--survey`. Now listed with its flag |
| 7 | `why_the_responses_reader_crossed_its_budget_2026-11-03.py` | exit 1 was the morning's PNG fix LANDING, not a fault |

**The clock defect, driven at 8 hours of the day:** ACCUSE at 00, 06, 10, 14, 18, 21; SILENT at 22 and 23. **Nothing in `note_vagueness_lint.future_stamp` was wrong** — repairing it to satisfy the probe would have broken correct code. The probes now pin the write time with `os.utime`, and a new test drives all 24 hours and **asserts the 2 wrap-around hours are SILENT** rather than skipping them, because at 22:00 and 23:00 a bare clock 2 hours ahead falls on the next day and a same-day prose date cannot express it.

### 3.3 The severity / residual-risk conflation, bounded

He disowned it on 2026-11-02: *"I have clearly been conflating these two terms a lot recently. I hope that conflation has not been reflected in your work?"* and *"the fault was entirely mine"*.

**Measured over 5,026 files:** 32 lines place the 2 terms within 80 characters; **7 of 32 = 0.218750**, Wilson [0.110238, 0.387550], also attribute a definition to him. Of those 7: 4 are notes reporting this defect, 1 is his own instruction quoted on the task list, 2 are a panel seat's tool input. **1 was live**, `scripts/can_the_carry_latch_the_gate_at_one_2026-10-31.py:6`, and it is removed.

**0 behaviour affected.** `docs/MATHEMATICAL_APPENDIX.md` §7.7 gives `Sev(f) = W(class) · confidence · V(verification)` with no residual-risk term; `R_k` is the recursive reduction quantity; `residual_risk` appears as a code identifier in 6 places, 4 of them test names about the appendix's reduction properties. Grok's §4 reaches the same separation independently.

---

## 4. His v-bar question, answered — and it is larger than B94 states

**`v̄` IS in the mathematical model:** `docs/MATHEMATICAL_APPENDIX.md` §7.9, 1 of the 4 components of the capability fingerprint `(D_decay, v̄, A, C)`, and a factor in `w(y) = v̄(y) · u_qual(y) · (1 − S_sync(y))` at line 1207. §7.9 defines it as **mean verification score**; line 1461 as **verified findings / total findings at round r**.

**Executed on the same 5 synthetic findings** (2 verified, severities spread, 3 flaw classes):

| component | appendix §7.9 | `bench/dm/_manager.py` (live) | `bench/run_exp19_fff.py` |
|---|---|---|---|
| `D_decay` | decay rate, §7.1 model fit | `duplicates / len(findings)` | `1/rounds` normalised |
| **`v̄`** | mean verification score | **fraction verified → 0.4** | **mean severity → 0.5** |
| **`A`** | total novel verified findings (a COUNT → 2) | **mean severity → 0.5** | **mean abstraction index → 0.38** |
| `C` | `A` / estimated total real findings | flaw classes / total → 0.375 | flaw classes / 8 → 0.375 |

So the live manager computes `v̄` as the appendix intends; `run_exp19_fff.py` does not; and **`A` is a different quantity in all 3 places**, with the appendix's version an integer count that neither code path computes. This is decision 13 / entry B94, and it is wider than that entry currently records.

---

## 5. A finding he asked to be told about: the list's branching ratio

Producer `scripts/task_list_burndown_2026-09-11.py`.

| | added | closed | R | 95% interval on R | exact test vs R=1 |
|---|---|---|---|---|---|
| 2026-10-29 (recorded) | — | — | 0.782051 | upper bound **0.990540** | — |
| before tonight's 5 entries | 181 | 206 | 0.8786 | [0.7198, **1.0725**] | p = 0.222421 |
| after tonight's 5 entries | 186 | 207 | **0.8986** | [0.7374, **1.0950**] | p = 0.313037 |

**The point estimate is still subcritical.** What has changed is that the 95% upper bound exceeds 1, so termination can no longer be *asserted*, and the exact test does not reject R = 1. **Tonight's entries are not the cause: the bound was already 1.0725 before them.** The crossing happened during the 1st–3rd November burst.

The guard reporting it, `bench/tests/test_task_list_burndown_2026-09-11.py`, is **not** among the gate's files, which is why it has said so since at least 2026-11-01 unread. Same structural cause as decision 16.

---

## 6. Boards and commits

| board | result |
|---|---|
| gate's 121 guards + the 54 outside it | **3,102 passed, 12 skipped, 0 failed, 883.61 s**, exit 0 |
| commit `36fd3ec9` gate | 2,442 passed, 11 skipped, 0 failed, 560.23 s; ratchet held 24 → 24 |
| commit `eb90d92d` gate | 2,454 passed, 11 skipped, 0 failed, 581.69 s |

**2 commit attempts were refused, both for faults of mine, both corrected rather than bypassed:** B106's `evidence:` field named a producer under `scripts/` where a DONE marker must name files the suite collects; and the pre-commit note-lint ratchet, which refuses a commit whose staged note carries more findings than the same file at HEAD, went 24 to 25 on 1 unnamed subject in a sentence added minutes earlier.

**Neither commit is pushed**, on his standing policy restated tonight. The branch is level with `origin/sim/shakedown-2026-09-29` at `e4b83b25` (2026-11-03 16:19).

**The full suite is a separate matter and is stated rather than glossed.** `resources/suite_record.json` records 2026-11-01T22:08 at commit `8e00f791`: 14,378 passed, **9 failed, 2 errors**, 6,104.54 s. Re-running those 11 named tests tonight: **6 still red, 5 since fixed**. 1 of the 6 was mine (the gate-cost declaration, now refreshed to 122 files / 2,465 tests) and 1 is the branching ratio above. **The gate is green; the gate is 122 of 806 test files.**

---

## 7. What is owed

**By him: 19 decisions**, all in `experimental_notes/Decisions_Awaiting_You_2026-11-03.txt` and its byte-identical mirror at `~/Desktop/CDSFL_tts/`. Both decision surfaces agree on all 19 — z3 bijection `True`, SymPy `FiniteSet` equality `True` (`scripts/do_the_two_decision_surfaces_agree_2026-11-01.py`). The 5 added tonight are 15 (the mid-turn record), 16 (whether the gate should grow), 17 (the asterisks), 18 (which identifier a spoken report carries) and 19 (whether a list that may not terminate is acceptable, and that it was hidden from you).

**Plus 2 SUPPRESSED questions**, which are worse than repetition because repetition is visible and suppression is not. `scripts/how_many_decisions_actually_need_him_2026-11-01.py` finds 2 entries whose live asks are hidden from the generated decision list by a `ruled:` date that PREDATES them: **B13** (ruled 2026-10-17, later addition 2026-10-18) and **B21** (ruled 2026-10-17, later additions 2026-10-31, 2026-11-01, 2026-11-02).

**By me:** the second panel (`BRIEF_stem.md`, validated, 0 lint findings, awaiting dispatch); the 5 remaining reds outside the gate; and B20, which he placed at the bottom of the list himself.

---

## 8. Triage of the open list

246 entries: **23 live** (22 open, 1 blocked), 210 done, 4 deferred, 9 withdrawn. The word *open* carried 2 meanings across the 2 surfaces that report it until tonight; both now state the breakdown. Of the 17 open before tonight, `scripts/how_many_decisions_actually_need_him_2026-11-01.py` classifies **14 as genuinely owed to him**, 5 as presented to him but not his, 1 (C0001) as released by another, and B22 as *"asking a go-ahead his standing rule grants"* — which is why the panel was dispatched without asking.

**B83 and B84 were wrongly triaged as completable unsupervised earlier tonight**, and both say `NEEDS HIS RULING` in their own text: B83 because storing the discrimination-control outcome changes what the runner writes into the archive days after a run finished, and B84 for the same reason about a pre-run target description.

---

## 9. Panel in flight

`bench/logs/severity_spec_is_uncomputable_2026-11-04/BRIEF.md`, free seats `cc2` and `fable`, blind round, both ALIVE on attempt 1, both past 40 tool calls. Subject: whether §7.7's `Sev(f)` is computable as specified. **The panel has since returned and it refuted the brief's framing on 3 counts; §10 below records the outcome.**

A terminal tailed the run live, per `cy`.

---

## 10. Panel result: both seats refuted the brief, and they disagree with each other

**Dispatched** `cc2` (11,407 chars, 782.0 s, 4 passes) and `fable` (8,345 chars, 696.2 s, 5 passes), blind round, 0 paid seats, exit 0. 15 files proposed in the seat copies, untested and not applied. Full record: `experimental_notes/Panel_FULL_RECORD_Severity_Spec_2026-11-04.md`.

**Both reached the same verdict — `NOT_AS_SPECIFIED` — and disagreed about why, which is what no-compelled-convergence is for.**

### 10.1 What they refuted in my brief, and what I verified

| claim in my brief | seat | verdict | my own check |
|---|---|---|---|
| §7.7 key property violated on **37 of 42**, 88.0952% | fable | **REFUTED: triple-counts 5 findings** | **CONFIRMED EXACTLY** |
| `confidence` is refused by policy, so the 2 documents contradict | cc2 | **REFUTED: they agree** | see 10.3 |
| `_sk_admits` in `bench/reference_runner_v3.py` | fable | **REFUTED: no such function** | **CONFIRMED, 0 definitions** |
| 0 of 3,298 entries carry `confidence` | both | stale denominator | **3,170 distinct; cc2's 3,691 is inflated the same way** |

**The figure defect, reproduced independently before adoption.** `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` globbed `bench/logs/**/runner_state.json`: **77** files, **10** of them under `sandbox_harvest/` — the directory a PANEL RUN writes to preserve what its seats produced. Content-hash deduplication leaves **67** distinct registries. The 5 REFUTED findings of `commissioning_arm1_panel_20260929T214647Z` each entered the tally 3 times:

```
with the copies : 37 of 42 = 0.880952, Wilson [0.749996, 0.948062]
deduplicated    : 27 of 32 = 0.843750, Wilson [0.682459, 0.931356]
42 = 32 + 2*5    37 = 27 + 2*5     both exact to the integer
```

**A panel's own evidence-preservation step corrupted the measurement a later panel was convened to examine.** Repaired: the producer deduplicates by content hash and PRINTS the skip. `docs/MATHEMATICAL_APPENDIX.md` §7.10 corrected, including the earlier 35 of 40 / 87.5000%, which carries the same defect and is superseded rather than stale.

### 10.2 Where the seats disagree with EACH OTHER, which is the information

**On whether dropping `confidence` is safe, they measured opposite signs.**

- **cc2**: recomputing as `asserted · V` moves the critical partition on 29 of 78 runs and **flips the real gate on 11 of 78 — 14.1026%, Wilson [8.0610%, 23.5140%] — every one False→True**, i.e. manufacturing convergences, all through the vacuous-curve branch. Derived why: severity ∈ [0,1] and the cut is 0.7, so `sev/2 ≥ 0.7` needs `sev ≥ 1.4`; SymPy returns 7/5 and Wolfram `Reduce` returns `False`. `V(None)=0.5` makes **every** unresolved finding sub-critical — the exact population the A4 fail-safe exists to block on.
- **fable**: recomputing as `compute_sev_f(class, confidence, verdict)` moves the partition on 588 entries and **flips 12 of 46 verdict-bearing runs, every one True→False**, i.e. preventing convergences.

They substituted **different severity definitions**, which explains the sign. **★ THIS FRAMING WAS MINE AND THE JOINT ROUND SUPERSEDED IT — see `Panel_FULL_RECORD_Severity_Joint_2026-11-04.md`.** I recorded it as "opposite failure modes depending on the substitution". Measured on 1 archive through the real gate, `fable`'s substitution produces **both** signs: 11 False→True (the same runs as `cc2`) **plus** 12 True→False. `fable` withdrew its own direction claim — the 11 manufactured flips all occur in runs carrying 0 entries with any `falsifier_verdict`, and its "verdict-bearing" denominator of 46 excluded exactly that population by construction. So it is not 2 options with opposite failure modes; it is 2 options of which **the first carries both failure modes and the second carries 1**, and the restricted annihilator flips **0 of 67**, Wilson [0.0000%, 5.4226%].

### 10.3 The disagreement I cannot settle from the replies alone

cc2 says `cdsfl_operational.md:773` forbids confidence only as a **rebuttal to a tool verdict** — it sits under *Action precedence → 1. REFUTED by tool* and reads *"Assertions that 'my reasoning is sound' without tool receipts are inadmissible"* — and that §7.7 **implements** that by setting confidence's weight to 0 exactly where a tool refuted (`V(False)=0`). On that reading the documents agree and B87's central claim dissolves.

fable says the contradiction is real, citing **§15 `d_tool`** (quantities come from tool execution, *"not from self-assessed confidence"*) as an independent prohibition, plus the action-precedence item.

**They cite different clauses — and the joint round settled it AGAINST BOTH.** `fable` quoted both with line numbers and conceded by reading: §15's `d_tool` at lines 600-606 scopes its prohibition to **the detection probability `d` entering `q = η · d · p`**, the §15 preamble at line 578 scopes all 5 constraints to the `R_k` update, and lines 773-775 forbid confidence as a **rebuttal**. Those are the only 2 occurrences of `confidence` in the directive. **Severity is not `d` and `Sev(f)` is not a factor of `q`, so B87's letter-level conflict dissolves.** `cc2` also rejected its own round-1 claim that the documents are "in exact agreement", which overstated the other way. What survives for him is **1 precisely named unlegislated case**: model self-assessed confidence as an input to a harness-computed severity that reaches a convergence gate. §7.7 includes it; `d_tool`'s rationale extends to it only by analogy, and an analogy is not a directive. Reading R1 (silence permits it) is what the text supports; reading R2 (`d_tool` states a principle instanced at `d`) is a design judgement he may adopt.

### 10.4 Findings neither B87 nor the brief contained

- **A second partition reader**: `_corroborated_novelty_series` at `bench/reference_runner_v3.py:11104`, with an identical raw-severity read. cc2 found it only because its patch refused to apply on a unique match.
- **`compute_sev_f` / `stamp_sev_f` already exist**, wired into the round loop at line 20523, tested, default-off, with reader-side support for both missing factors (fable). So "add the HARD/SOFT field" needs a **writer**, not a build.
- **`effective_severity` + `RunnerConfig.severity_spec_enabled`** were built 2026-10-15, so "§7.7 gates nothing" overstates: the promotion reaches **1 of the 2** severity consumers that decide convergence (cc2).
- **The key property may not be unconditionally desirable at the gate that blocks a run from converging** (fable): Exp 42 measured 2 of 3 REFUTED criticals as falsely REFUTED, so full §7.7 compliance at the gate would have released real defects. It is a scoring-layer property.
- **cc2's recommended fix and its refusal to compose**: the restricted annihilator-only form (`V=0 ⇒ 0`, other values untouched) flips **0 of 78**, Wilson [0.0000%, 4.6938%], and dominates the full product on manufactured convergences, **0 against 11**. It therefore declined to add a vacuous-curve guard, citing his composability rule — the single fix performs strictly better alone.

### 10.5 What the seats say would refute them

cc2 names its weakest joint itself: its fix treats `REFUTED` as permanent annihilation, and it did **not** measure REFUTED→CONFIRMED transitions on a single canonical id. If that count exceeds 0 the fix must read the latest verdict. It also states that all 78 replays hold `unresolved_critical=0` and `contested=0`, so a live run with either above 0 could flip where the replay does not.

**Nothing from either seat is applied.** The proposals sit in `bench/logs/severity_spec_is_uncomputable_2026-11-04/seat_proposals.diff`, untested in this tree, and `fixes-to-HIL-only` means they reach him before they reach the runner.

---

## 11. A second route by which a sandbox copy reaches the canonical record

**Found while reading a staged file list, immediately after the figure defect above taught me to look.** `git add -A` staged 2 files from the joint panel's sandbox harvest, both copies of `experimental_notes/data/morning_report_decisions.json` written by a seat. `bench/logs/**` is gitignored, so they should have been invisible.

**The admitting mechanism is 1 line.** `.gitignore:50` reads `!bench/logs/**/*report*.json` — a negation that un-ignores any JSON with `report` in its name anywhere under `bench/logs`, presumably so run report files stay tracked. It also matches a seat's copy of a canonical data file, because the filename contains `report`.

**Measured, and the honest reading is that the harm is LATENT:**

| | |
|---|---|
| tracked files under `bench/logs` | 6,520 |
| of those, inside a `sandbox_harvest` | **5** |
| of those, copies of a file that also exists canonically | **1** (`experimental_notes/data/morning_report_decisions.json`) |
| readers of that file that use a recursive glob | **0** — all 10 name an exact path |

**So nothing reads the stray copy and nothing is currently wrong.** It is recorded because the mechanism is not hypothetical: the 88.0952% defect in section 10 was caused by exactly this shape, a recursive glob under `bench/logs` picking up sandbox copies of `runner_state.json`. A single reader added later with `rglob` would reach the stray copy.

**The fix is 1 line and it is his**, because it changes what the repository tracks: tighten the negation so it cannot reach inside a `sandbox_harvest`. The 2 files staged tonight were unstaged rather than committed.

---

Written under CDSFL note standard v1.9 (1 November 2026).
