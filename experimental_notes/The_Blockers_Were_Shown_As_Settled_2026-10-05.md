# Two findings, and one withdrawn recommendation — 2026-10-05 01:18 BST

Audience: a reproducing engineer. The plain-English companion for a non-coding reader is `~/Desktop/CDSFL_tts/Blockers_Shown_As_Settled_2026-10-05.txt`. Every figure below carries the committed script that produced it.

---

## The finding

`FindingRegistry.build_summary` in `bench/reference_runner_v3.py` renders `UNCONFIRMED` findings inside a section headed:

```
--- SETTLED (n) (do not re-describe) ---
These findings are confirmed, closed, or merged. Do not CHALLENGE or re-describe them.
To reopen, issue REOPEN <ID> with specific new evidence.
```

`UNCONFIRMED` is the **only** status that `FindingRegistry.unverified_critical_count` — the A4 convergence fail-safe — treats as a blocker. Both facts were established by calling the two methods over every status in `FINDING_STATUS_VOCABULARY`, not by reading either: of 12 statuses, `UNCONFIRMED` is the single one that is simultaneously rendered under SETTLED and returns a non-zero A4 count.

So every finding standing between a run and its conclusion was presented to every model, every round, as confirmed, closed or merged, with challenge explicitly forbidden.

**Measured over the archive**, by `scripts/the_blockers_are_shown_as_settled_2026-10-05.py`: **175 of 175 attributed blockers were rendered under SETTLED — 100.0000%, Wilson [97.8520%, 100.0000%]** — across **22 of 59 archived registries, 37.2881%, Wilson [26.0840%, 50.0464%]**. Both intervals were computed twice, by `statsmodels.stats.proportion.proportion_confint` and by an independent closed form using `scipy.stats.norm.ppf`, agreeing to better than 1e-6.

Blockers are attributed by **leave-one-out** on each real registry rather than by a status predicate. That matters: the first version of the script used a status-and-`verified` predicate and reported blockers in runs whose A4 count was 0, because the counter applies conditions beyond those two fields. Under leave-one-out the attributed total is 175 and the sum of the counter's own returns is also 175, so the attribution carries no interaction slack.

---

## Why no earlier test caught it

Both halves were individually correct and each described itself consistently. A source-text assertion over either passes. This is the exact condition the `execute-do-not-grep` directive names, and it is the fifth defect in this project found by executing two forms against each other rather than reading them.

The word was also **overloaded, and only one use was wrong.** `gamma_critical` reaches the convergence gate through `_settled_novelty_series`, which partitions on `_NON_NOVEL_TERMINAL_STATUSES` and reads neither `compact_statuses` nor `build_summary`. That path already excluded `UNCONFIRMED` from "settled" and is correct — `bench/tests/test_a4_verifier_failsafe.py` records exactly that at its line 206. The arithmetic and the prose disagreed about one word, and the prose was the wrong one.

---

## Three mechanisms, one blind spot

The mislabelling was not the only thing routing around this class of finding. Three independent mechanisms did:

1. **`build_summary`** labelled them SETTLED and forbade challenge. This note.
2. **`_apply_routing`** refused them. Its candidate test at `bench/reference_runner_v3.py:6879` requires `severity >= CRITICAL_SEVERITY_THRESHOLD` (0.7), while the A4 counter has **no severity test at all** in its executable statements — the removal from commit `6c10fe4`, 2026-09-06, still stands. Proved by calling the counter: a lone finding at severity 0.45 returns a count of 1. Producer: `scripts/the_counter_and_the_router_disagree_2026-10-05.py`. Measured: **803 of 1424 residuals sit below the router's threshold, 56.3904%, Wilson [53.8010%, 58.9455%]**, and **316 of those 803 were never offered to a model in-round, 39.3524%, Wilson [36.0318%, 42.7744%]** (`scripts/why_the_blockers_were_never_offered_2026-10-05.py`).
3. **`_post_convergence_sweep`** was the only machinery that serviced them, and it runs after `converged` is assigned. Of its 5 disposition channels, **0 were exclusive to it** except the id-addressed `FALSIFIER: <id>` re-attachment parse, which had exactly 1 site repo-wide, inside the sweep. Producer: `scripts/sweep_channels_are_post_verdict_2026-10-05.py`.

That is why the closing sweep looked like an afterthought. It is the only mechanism in the schema that does not believe the "settled" label, which is why it is the only one that resolves these findings.

**A design that was refuted before it was built.** The cheapest repair would have been to parse id-addressed falsifiers already arriving in round replies. Measured: **0 of 3473 archived round-reply files carry the form, Wilson [0.0000%, 0.1105%]**; 14 carry a bare label with no fenced payload, 0.4031%, Wilson [0.2403%, 0.6755%]. Producer: `scripts/in_round_falsifiers_are_discarded_2026-10-05.py`. The form is produced only when something asks for it, so there was no free gain to take.

---

## What was built

**1. The `UNRESOLVED` section.** `unresolved_statuses = ("UNCONFIRMED",)` is split out of `compact_statuses`, and its findings render under a header that states they are not settled, names them with their severities, and asks for a runnable falsifier addressed by finding id. The status partition remains complete and non-overlapping.

**2. `record_in_round_falsifier_reattachments`.** The sweep's one exclusive capability, inside the round loop, wired at the call site beside `record_in_round_withdrawals` and persisted to the state payload as `round_falsifier_reattachments`. Dispositions mirror the sweep exactly so the two cannot drift: CONFIRMED resolves and sets `verified`; REFUTED below the critical threshold resolves REFUTED; REFUTED at or above it is recorded as computed evidence and retires nothing, per the founder ruling of 2026-08-03; anything else stays queued and is counted.

**The governing invariant, which restates the founder's 2026-07-28 anti-gaming guard rather than relaxing it: a finding leaves the blocker count on EXECUTED evidence only.** `reverify_falsifier` runs the supplied code. Reasoned prose is recorded by `record_in_round_withdrawals` and moves no status. Convergence cannot be bought with an assertion.

**Monotonicity is proved, not assumed**, because the structural guarantee of running after the verdict is given up. Verified three independent ways by `scripts/in_round_clearance_is_monotone_2026-10-05.py`: z3 returns **unsat** on the attempt to find any assignment raising the count; a SymPy bound confines the per-finding delta to {-1, 0} so the total supremum is 0; and **248 transitions were executed against the shipped counter with 0 raising the blocker count**. `record_in_round_falsifier_reattachments` can therefore never block a run that would otherwise have converged, nor reverse a verdict. It can only make convergence easier, which is the intended effect.

**Inert on every archived run by construction.** The parser's trigger appears in 0 of 3473 archived replies, so it cannot change any archived result.

---

## Guards

| File | Tests | Mutation check |
|---|---|---|
| `bench/tests/test_a_blocker_is_never_shown_as_settled_2026-10-05.py` | 15 passed, 11 skipped | returning `UNCONFIRMED` to `compact_statuses` fails **6 of 15**, including the general invariant |
| `bench/tests/test_in_round_falsifier_clears_only_on_execution_2026-10-05.py` | 17 passed | accepting a bare label fails 2; retiring a critical on refutation fails 2 |

The first file holds a property that generalises past the one status that was wrong: **for every status in the vocabulary, if a single-finding registry of that status returns a non-zero A4 count, that finding must not render inside the SETTLED section.** An anti-vacuity test asserts the blocking set is non-empty and contains `UNCONFIRMED`, so the parametrised invariant cannot pass by skipping everything.

**One pre-existing guard was amended, and the amendment was itself mutation-checked.** `bench/tests/test_status_partition_covers_everything_2026-08-30.py::test_the_three_lists_are_all_present` asserted set equality on exactly 3 bucket names, so a fourth failed it although the property the file exists to protect still held. It is now a subset check over the 3 original names and renamed accordingly; deleting `hidden_statuses` — the failure it was written against — still fails it, verified by executing that mutation. The file's completeness and non-overlap tests are generic over the partition and passed over 4 buckets unchanged.

Regression at the time of writing: 138 passed, 11 skipped across the 8 test files touching `build_summary`, the A4 fail-safe, the gate, the settled criterion and rho. The full board was launched at 00:40 BST to `bench/logs/_suite/full_suite_2026-10-05_2026-10-05_004000.log` and had not finished.

---

## Bearing on prior work

**Both panel seats' repairs were downstream of this.** The cc2 and fable proposals of 2026-10-03 each read evidence attached to the blocking findings, and the adjudication recorded that neither could change a live run because the evidence did not exist until the sweep wrote it. That remains true, and it is now a second-order point: the panel was never asked to produce such evidence in-round, because the findings were labelled settled.

**Founder rulings 1 and 2 are still open and are not superseded.** The severity gate's restoration to the A4 counter (ruling 1) and the choice of convergence-blocker repair (ruling 2) remain the founder's. This work changes neither counter nor router predicate.

---

## Finding 2 — the capability ladder has been inert in every simulated run

`bench/routing.py` carries a capability ladder validated on Exp 42: weak SOURCE models resolved **0 of 7** of the hardest residuals, a strong writer resolved **6 of 7**, and the 2-rung ladder reached **7 of 7**. `DEFAULT_FALSIFIER_STRENGTH = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek")` is ordered by measured falsifier-confirm rates, and the file carries a ★-marked founder observation that this order "decides which model is asked to resolve the hardest findings, so a contaminated confirm rate contaminates the MECHANICS, not just the write-up."

**It climbs nothing in simulation.** Measured by execution in `scripts/what_the_sim_runner_never_carried_over_2026-10-05.py`: `rank_falsifier_writers` correctly returns `['Codex-SIM', 'CC2-SIM', 'ChatGPT-SIM', 'Gemini-SIM', 'Fable-SIM']` for a `DeepSeek-SIM` finding, and a uniform simulated panel answers **all 5 rungs with 1 distinct model**. `resolve_via_routing` climbs, logs rungs, and can record "ladder exhausted", while being structurally incapable of its purpose.

**This is the second time this mechanism has been found inert in simulation.** `bench/routing.py` ~:90 records the first: a `-SIM` label did not match the bare vendor names, `ranked` came out EMPTY, and routing "exercised the unknown-model fallback instead of the ranked ladder Bench Run 2 will run -- so ladder ORDER was unrehearsed by every simulation." That was fixed 2026-08-30. The seat-identity cause beneath it was not, and after the fix the ladder *looked* correct in the logs.

**No config diff can find this.** The ladder was armed in configuration throughout. It was inert in fact. Only calling the code shows it — `execute-do-not-grep` again.

---

## The carry-over audit

Producer: `scripts/what_the_sim_runner_never_carried_over_2026-10-05.py`. The simulated runner sets **29 of 93** `RunnerConfig` fields explicitly, leaving 64 at defaults. Compared field-by-field against all **49** committed real-experiment configs.

Six fields were armed in a real config and not in the sim. Three were then checked by execution and adjudicated **not** gaps:

| Field | Verdict |
|---|---|
| `burst_mode` | deliberate, documented at the construction site under the 2026-08-30 parity comment |
| `panel_cwd` | set at runtime (`run_simulated_experiment.py:724`), invisible to a static diff |
| `target_kind` | auto-detected — `detect_target_kind` returns `('python_module', 'suffix .py')` and `('prose', 'suffix .md')` when called. Blank is correct by design under task A1, "Config declares intent; the harness enforces." |

**Three genuine gaps remain, none mentioned anywhere in the simulated runner:**

| Field | Armed in | Note |
|---|---|---|
| `immune_memory_enabled` | 13 of 49 | documented maths-model component (appendix S1.5). The post-Exp-45 decision was to enable it live for the arc. The separate `immune_memory_consume_rk0` was deliberately left off to preserve factorial independence; that reasoning does not cover the recording half. |
| `hardened_gate_enabled` | 4 of 49 | read at `reference_runner_v3.py:17351` |
| `apply_fixes_back_enabled` | 1 of 49 | rewrites the reviewed target between rounds; plausibly correct to leave off in a simulation, but never stated |

A further 25 fields are armed in the sim and absent from the real configs. That direction is legitimate and largely documented — the sim exists to stress machinery the real run may not reach, and several were armed on the founder's 2026-09-21 instruction to "enable it all now and test it in the next simulated run".

**This is a recurring class, not a new worry.** The 2026-08-30 CC2 review found the sim config differed from the real exp45 on *every value examined*, its own comment recording that "each difference let the simulation behave in a way the run it is compared against structurally could not": `earliest_stop_round` (only 1 of 2 convergence gates ever exercised), `stall_gamma_*` (the sim could halt on a path the real run cannot reach), `merge_arbitration` (a second seam path permanently dark). With the ladder, that is **3 recorded instances of the same class**.

---

## The withdrawn recommendation

The earlier recommendation to run the 3 convergence runs with uniform seats is **withdrawn**. It was wrong on three counts:

1. **It treated validated functionality as new.** The ladder dates from June 2026 and was validated on real experimental data.
2. **It inverted the simulated runner's purpose.** The sim exists so functionality is exercised cheaply before the paid panel. Disabling a facility during the runs designed to test it moves the discovery into a paid run. This also contradicts the founder's NOW-6 ruling of 2026-09-21: *"If they have the potential to meet our additive standard, but we don't know yet how well they will work (or at all), then that is what the simulated runs and programme of study are for!"*
3. **The confound argument fails on its own terms.** Only arm5, the paired baseline, is seat-mix sensitive, and it is confounded only if the arms *differ*. Applying the same mix to both removes it entirely.

A further point the founder did not need to make: **6 identical seats is not a simulation of the real panel.** The real panel is 5 or 6 vendors of measurably different strength, so a uniform simulated panel cannot exercise the routing ladder at all — one of the main mechanisms the simulation exists to rehearse.

**The ladder should be ON for the runs.**

---

## A related pattern, conceded

The founder noted a prior occasion of proposing to remove severity machinery. The record supports it. The severity test was removed from `unverified_critical_count` in commit `6c10fe4` on 2026-09-06 and **rejected the same day at 22:15**. It is still removed — confirmed tonight by AST over the counter's executable statements and by calling it: a lone finding at severity 0.45 returns a count of 1. **That rejected change has never been reverted.**

---

## Three self-inflicted failures, repaired

The full board finished **11 failed**. An earlier progress report in-session said 0, read from a 65%-complete run; that was premature and wrong. **3 of the 11 were caused by this session's own work** and are repaired.

| # | Guard | Cause | Repair |
|---|---|---|---|
| 1 | `test_fresh_clone_is_actually_run_2026-09-11.py::test_no_script_uses_both` | 8 new `scripts/*_2026-10-05.py` each defined a local `answer_help` that built an argparse parser; the project reserves that name for `_cli_help.answer_help`, which answers `--help` first and hides argparse's flag list | renamed to `_parse_args` in all 8 |
| 2 | `test_operational_scripts.py::test_no_bare_or_silently_swallowed_exception_handlers` | `except Exception: pass` inside the leave-one-out blocker attribution — "the failure leaves no trace anywhere" | failures collected into `probe_errors` and reported; output states whether the attribution is complete or a lower bound (it reports 0, so complete) |
| 3 | `test_source_text_and_neighbour_audit_2026-09-11.py::test_the_class_has_not_grown_silently` | source-text assertion census 80 → 83 | all 3 **converted to executing checks**, not deleted; census back to exactly 80 with 0 of mine |

**FOLLOW before the rename.** `test_help_never_acts_2026-09-11.py::test_every_script_that_writes_answers_help` *requires* the name, so renaming could have broken it. It only flags scripts that WRITE, and its own message says "or give the script a parser". These are read-only and all carry parsers. 631 neighbouring tests passed after the rename.

**The conversions are strictly stronger than what they replaced.** Two now read `run_experiment.__code__.co_names` and `.co_consts` — a comment or a commented-out call cannot appear in compiled output — with a control assertion proving the probe is not blind. The third runs the launcher's `--help` as a subprocess and additionally asserts an unknown `--seat-models` value is **refused**, so a typo cannot silently fall back to uniform seats and disable the ladder. Each was mutation-checked: 2 tests fail per mutation.

### An instrument defect found while fixing

The producer of the "175 of 175" headline was substring-matching finding ids against the rendered SETTLED block. Unsound twice over: an id can appear there for unrelated reasons (a `merged_into` pointer), and once the measured defect was repaired the script returned **21 of 175** instead of 175. A figure whose producer stops producing it is back to being a claim about evidence. It now tests exact membership of a pinned `HISTORICAL_SETTLED_STATUSES` set and reproduces **175 of 175** exactly, while stating plainly that the defect is fixed in the current checkout.

---

## The fingerprint proposal

Full text: `experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`. Summary: add a provenance-gated falsification rate to the capability fingerprint, record it in shadow, compute a shadow ranking beside `DEFAULT_FALSIFIER_STRENGTH` every run, and promote it to ordering the ladder only on evidence of non-distortion. The frozen order is retained as prior and cold-start fallback; nothing is removed.

**Stated first, not buried: the selection effect.** The ladder routes findings weak models could not resolve to strong models, so a strong model is measured against a harder population and its provenance-clean confirm proportion is depressed by the very fact that it is trusted. Uncorrected, a measured ladder could demote exactly the models it should promote and feed that back into the next assignment. Four mitigations are set out; the recommendation is first-pass-only measurement, with its limitation stated — it measures something slightly different from what the ladder does.

**The provenance gate is load-bearing.** Exp 55: one model scored 2 of 2 CONFIRMED with both falsifiers DETACHED (opening nothing, restating the document from memory); another scored 0 of 2 with genuine readers that ERRORed on a missing file. A naive confirm-rate ranking inverts the correct order. `scripts/competence_provenance.py` becomes a gate on pool entry.

**It cannot be validated in simulation as things stand** — the simulated panel is flat at p = 0.6987 against the real panel's p = 2.213e-59.

---

## The full mixed-capability inventory, checked by execution

A facility can be armed in config and inert in fact, so each was called rather than read.

| Facility | State | Note |
|---|---|---|
| capability ladder (`routing_enabled`) | **on** | but ordering a flat set; capped at `routing_max_rungs=2` of 5 — principled, since Exp 42 reached 7/7 on 2 rungs |
| capability fingerprints | **written live every round** | consumed by `burst_planner.py` / `_should_decompose`; **not read by the ladder** |
| ITC adaptive recovery | **always on** | called unconditionally at `reference_runner_v3.py:16999`; no config flag, so it cannot have been silently disabled |
| burst / decomposition (`burst_mode`) | **OFF in sim**, default `auto` | documented under the 2026-08-30 parity work. Worth revisiting: burst is fingerprint-driven, so it is itself a mixed-capability facility and is currently unexercised |
| closing sweep | **on**, 1 round | and as of tonight its distinctive capability also runs in-round |
| `immune_memory_enabled` | **off** | gap — 13 of 49 real configs |
| `hardened_gate_enabled` | **off** | gap — 4 of 49 |
| `apply_fixes_back_enabled` | **off** | gap — 1 of 49; plausibly correct, never stated |

## Where the cost increase came from

Settled earlier in the session. Producer: `scripts/where_the_plan_went_2026-10-04.py`.

Total dispatches per active day **fell** to **0.3872x** the earlier rate. But the simulated share of dispatches carrying a reply rose from **6.6959%**, Wilson [6.0633%, 7.3894%], to **100%**, Wilson [95.5765%, 100%]. Because every simulated seat was answered by the most expensive model available, **Max-plan dispatches per active day rose 5.7828x while total activity fell**. The mix changed, not the volume.

**The remedy is the seat map** — which is the same change that restores the capability ladder. The cost fix and the fidelity fix are one change, not two competing ones.

---

## The free panel found 3 real faults

2 free seats, **0 paid dispatches**. Fable returned in 1108.2s / 74 tool calls / 12,711 chars; cc2 timed out at the 1800s cap on attempt 1 and was on retry when this was written. Full verbatim reply preserved at `experimental_notes/seat_evidence/fingerprint_ladder_review_2026-10-05/fable_FULL_REPLY.md`, with all delivered files alongside.

**Fault 1 — a coverage claim was wrong.** "The sibling guard still covers these scripts" is false: `test_every_script_that_writes_answers_help` never examines them, because `WRITES=False` for all 8, so they are outside its population by design. The rename is safe because the harm class does not apply, not because coverage persisted. Coverage was structural-only until the seat delivered an executing test.

**Fault 2 — the swallowed failure survived one loop up.** `except Exception: continue` at the RUN level dropped an entire registry from the attribution with no trace while it stayed in `runs_total`, and the script still printed "the attribution is complete" — a claim computed from `probe_errors` alone, which never sees that path. The suite's swallow-guard only flags handlers whose body is entirely `pass`, so `continue` escaped it. **Verified and repaired**; completeness now requires both lists empty; 175 of 175 still reproduces.

**Fault 3 — the seat map did not fix the ladder, and this corrects Finding 2 above.** `routing_max_rungs=2`, and for every source seat those 2 rungs come from {Codex-SIM, CC2-SIM, ChatGPT-SIM}, all of which my map put on `opus`. **0 of 6 source seats got a climb between different models.** "2 distinct models across 5 rungs" was true but the 2nd model sat at rungs 4–5, never reached.

### The seat's own repair was then falsified, and the result is better than either

Mapping `Codex-SIM → fable` gives 5 of 6 mixed — but rung 1 is the *strongest* writer and `resolve_via_routing` stops on the first CONFIRMED, so all 5 run `(weak, strong)`: **0 of 6 in the ladder's own direction.** It would rehearse an algorithm the real run does not execute.

Two further corrections surfaced while checking it. My "6 of 6" was computed against a map that was never shipped — **my own new guard caught it by failing**. And the shipped map had `DeepSeek-SIM`, the measured-weakest vendor (28% confirm rate, ranked last), on the **strong** model, contradicting the project's own validated ordering.

**What holds:** `DeepSeek-SIM → fable` (a correction *toward* faithfulness) plus `routing_max_rungs=4` **for simulated runs only**. Measured: **6 of 6 mixed, 6 of 6 correctly directed.** Real configs untouched; the extra rungs land on the cheaper model and are reached only for findings rungs 1–2 failed to resolve. Pinned by `bench/tests/test_the_exercised_ladder_prefix_is_mixed_2026-10-05.py`, which carries anti-vacuity probes for both defects.

### On the proposal

- **First-pass-only is rejected, correctly.** Its premise — "a common population by construction" — is false: each model writes first-pass falsifiers for *its own* findings, and the populations differ at p = 2.213e-59, which is **this report's own measurement refuting its own recommendation**. The seat proposes randomising a small audit fraction of rung assignments instead: the only option measuring the ladder's construct on an assignment the ranking did not make.
- **The provenance gate is insufficient, demonstrated twice.** `falsifier_style` is a source-text regex: a decoy `open("/dev/null")`, or the token `open(` **in a comment**, both classify as "reads". And UNSAFE aggregates per *model*, not per confirmation. A sound gate needs execution-derived provenance (recorded file opens, or perturbed-target invariance). The seat also notes `test_nothing_imports_either_script_into_the_runner` pins that script as RECORD ONLY — promoting it to a gate overturns a pinned decision and must say so.
- **A better composition than mine:** frozen order stays the decider; the measured rate runs as CUSUM drift detection only; an alarm triggers re-running an Exp-42-style fixed-residual probe; **only the probe reorders**. "Rate = tripwire, probe = decider."
- **The fingerprint store erases run provenance on every save** — all 11 profiles carry one experiment name and timestamp, because `_save_fingerprints` writes back every loaded profile. The proposed dimension would land in a store where "which run measured this" is already unanswerable.

---

## Why the seats time out — and it is not cc2

cc2 failed **both** attempts: **0 chars, 0 tool calls, 3628.5s**, against fable's 12,711 chars and 74 tool calls. It did not run out of clock doing the work; it produced nothing. **The panel is therefore single-seat, so there is no inter-seat disagreement to preserve** — a real limitation on the review above.

Producer: `scripts/why_cc2_times_out_2026-10-05.py`, over 137 archived `claude_cli` seat replies.

| Question | Test | Result |
|---|---|---|
| Is cc2 slower than fable? | Mann-Whitney, U = 2258.0 | **p = 0.4031 — no.** Medians 809.5s vs 720.7s; independent rank computation agrees |
| Does cc2 fail more than fable overall? | Fisher / Barnard | **p = 0.7183 / 0.6179 — no** |
| …recently? | Fisher / Barnard | **p = 1.0000 / 0.8396 — no** |
| Has the failure rate risen? | Fisher / Barnard | **p = 0.046723 / 0.044514 — yes**, and for *both* seats (cc2 4.08%→15.00%, fable 2.08%→10.00%) |

**The diagnostic fact: the failures are not independent.** Of the 5 rounds that lost a seat, **3 lost both**, at near-identical durations — 1956.0/1956.2, 902.0/902.0, 18.7/18.8 seconds. Against an independence model at the measured per-seat rate, 3 of 5 gives **p = 1.556646e-07** (scipy, and Wolfram independently 1.556646484375e-07). Two separate processes do not fail within 0.2s of each other by chance.

**The cause that fits all of it.** Both free seats authenticate against the *same* subscription, and the dispatcher submitted the whole roster to `ThreadPoolExecutor(max_workers=len(MODELS))` — so both called `claude -p` in the same instant. Shared resource, simultaneous demand. It also explains the rise as briefs grew heavier, and tonight's shape: one seat completing fully while the other produced nothing.

**The change.** Seats sharing a subscription are dispatched one at a time in roster order; seats on other routes still run concurrently with each other and with that group. Nothing dropped, no capability removed. Cost is wall clock for the free panel only — the sum rather than the max of 2 seats — against a measured ~1-in-8 recent loss of a whole seat. Guard: `bench/tests/test_shared_subscription_seats_are_serialised_2026-10-05.py`, 6 tests, which *executes the shipped scheduling block* rather than restating it; the mutation fails 4 of 6, and an anti-vacuity probe proves the recorder can see an overlap.

**Confidence, stated plainly: hypothesis with strong correlational support, not a demonstrated cure.** It has not been tested by running a panel both ways. Until that measurement exists this is a scheduling decision with a stated reason.

Also found: `elapsed_s` is not always numeric — one record carries `'long-retry'`, which crashed the first version of the measuring script. Non-numeric entries are now counted and reported rather than crashed on or silently dropped.

---

## The joint (star) round — the second seat corrected both the first seat and CC1

Protocol, per the founder: **blind round each, then a joint round once the blind replies are in**, as the runners do. That had not been followed and had to be pointed out.

**A blind cc2 round proved impossible.** The brief asks the seat to review work done the same night, so the sandbox must contain that work — and that work had been annotated with fable's findings. Removing the contamination removes the subject matter. **Blindness has a shelf life: every blind reply must be collected BEFORE any is written into the tree.** Writing up at 03:12 closed cc2's blind window.

The first containment fix purged by **path**, reported 0 survivors, and left fable's whole verdict readable through 2 documents named for their subject. The guard now checks **content**, derives phrases from the replies themselves, removes carriers, and refuses the sandbox rather than returning one that looks blind. 15 tests; mutation fails 5; anti-vacuity holds that a path-only purge leaves the verdict readable.

**cc2 succeeded when dispatched alone** (17,462 chars, 71 tool calls) having failed twice when dispatched alongside fable — consistent with the contention hypothesis, though n=1 and it still needed 2 attempts.

### Against CC1

| # | Finding | Status |
|---|---|---|
| 1 | **The source-text census was reported at 80 with "0 of mine" while it was 81 and its guard was RED.** The extra assertion was added by the containment test, written *after* the count was taken. Measured, tree changed, stale figure reported. | **Verified and repaired** — converted to executing checks; census genuinely 80; the AST form now also catches a *new* unwired call site, which a literal count could not |
| 2 | **`routing_max_rungs=4` was a parity break, and its property is not dispatched.** 0 of 288 config files pin the budget. `resolve_via_routing` stops at the first CONFIRMED — verified: a rung-1 success dispatches `['A']` only. Rung 3 runs at ~2.75% / 0.79%. | **Verified and reverted** to an opt-in `--routing-max-rungs`; parity is the default |
| 3 | **`competence_provenance.py` credits the falsifier to the model that *reported* the finding, not the one that *wrote* it.** 1370 of 16500 archived entries carry `resolved_by_routing`; 8.3% credit the wrong model — flattering exactly the models the ladder demotes. | Seat-repaired; **not yet accepted into the live tree** |

cc2's charge on (2) is fair and I concede it plainly: **I used stop-on-first-CONFIRMED to falsify fable's map, then failed to apply it to my own.** The 6-of-6 figure counted prefixes, not dispatches. What survives is cc2's exhaustive derivation that **0 of 64 two-model maps reach 6-of-6 at budget 2, ceiling 5 of 6** — so a deeper budget is genuinely required, and is now asked for rather than imposed. The `DeepSeek-SIM → fable` correction stands on its own merits.

### Against the fable seat

- **`co_consts` — fable was wrong and my original note was right.** Tuple membership is element equality, not substring: a docstring containing the token does **not** satisfy it. Fable corrected a correct statement into an incorrect one. The real false pass is narrower and cc2 named it.
- **The randomised audit fraction** is the right identification strategy but **unpriced and not deployable** — routing fires rarely, so a random subset of a rare event cannot reach a usable sample. cc2 proposes the Exp-42 fixed residual set, which is a common population *by construction*.
- **"burst_mode off is no longer defensible" is premature by one dependency** — burst is fingerprint-driven, and the fingerprint has no verification dimension, so arming it now rehearses a planner reading the wrong inputs.

**This is what running without compelled convergence is for.** One seat produced a strong review containing 2 errors; the joint round caught both, found 3 further faults in my work, and surfaced a defect in a third script neither had examined.

---

## Open for the founder

1. **Should `_post_convergence_sweep` also move to before the verdict is recorded?** It costs no extra dispatch, since the sweep already runs. It changes the 2026-07-28 guard that the sweep "runs strictly after the verdict", which is the founder's to relax.
2. **Should `ESCALATED` and `WITHHELD` leave the SETTLED block too?** Both are rendered as "confirmed, closed, or merged" and neither is. Neither is an A4 blocker, so this is correctness rather than convergence.
3. **A defect in a recovery instrument.** `scripts/cdsfl_recover.py`'s LATEST EXPERIMENT block reported `exp55_v3_control` from 23 August during the restore at 00:23 BST, while the newest archived run is `study_run1b` from 3 October. It selects by experiment number rather than recency, so a recovering agent reads 6-week-old state as current.

Recorded in `experimental_notes/STUDY_IN_FLIGHT.json` as measurement `in_round_clearance`, which carries items 1 and 2 in its `open_for_the_founder` field.

---

Written under CDSFL note standard v1.7.
