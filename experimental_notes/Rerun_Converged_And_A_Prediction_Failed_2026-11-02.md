# The rerun converged, a pre-registered prediction was falsified, and money was never the variable

2026-11-02T17:45 GMT. This note reports the completion of the `study_run1b` rerun, the scoring of that run against predictions committed before it launched, and the answer to the founder's standing question about what repeated passes, extra seats and paid runs buy for the severity measurement.

## 1. The rerun converged

The rerun of `study_run1b` finished at 05:08:33 after 6 rounds and 4,950 seconds of wall-clock time, which is 82.5 minutes of compute inside an 89.3 minute window. It reached `STATE_CONVERGED` at round 5 on 3 consecutive passes, with every closure condition met at once: open channels 0 and stable, novel findings 0, contested findings 0, and the convergence slope gamma at 0. The final reported gamma was 0.487 and the registry holds 30 canonical entries.

The previous attempt at this run did not converge. That failure has its own producer, `scripts/why_study_run1b_did_not_converge_2026-11-02.py`. This one did.

## 2. A pre-registered prediction was falsified, and it is reported in full

Before the run launched, 4 predictions were written to `experimental_notes/data/severity_bounds_prereg_2026-11-02.json` and committed, so that they could fail. `scripts/score_the_severity_predictions_2026-11-02.py` reads the run's own archive and scores each one against its own stated falsifier. The result:

**Prediction 1, HELD.** Severity is not constant across findings. The realised standard deviation is 0.124152 over 30 findings, with a range of 0.4000 to 0.8500. It would have been falsified by a standard deviation of 0.

**Prediction 2, NOT TESTABLE.** Among findings whose falsifier decided, confirmed severities were predicted to outrank refuted ones. The run produced 28 confirmed and 0 refuted. A prediction with no denominator is neither held nor falsified, and reporting it as held would be the flattering reading.

**Prediction 3, FALSIFIED.** At the live 0.7 critical cut, sensitivity over confirmed findings was predicted to stay above 0.5. The measured value is 0.285714 over 28 confirmed findings, against the archive's 0.7316. The prediction fails by its own stated falsifier. The archive-derived bound does not transfer to a fresh simulated run, and the claim that it would is withdrawn rather than reinterpreted.

**Prediction 4, MIS-SPECIFIED.** Its falsifier tested `severity >= 0.7` as the release rule. That is a rule the project retired: the live door's own docstring records that the real rule is the inverse and is conditional, and that the stale form stood from 2026-09-06 to 2026-10-12. The pre-registration was not rewritten to hide this, because a prediction edited after the run is worth nothing. It is reported as mis-specified, with the property it was trying to express measured beside it and labelled as a post-hoc observation.

## 3. Money was never the variable

The founder asked, verbatim: *"why is a paid run any different to a simulated one for this measurement?"* and *"Why should money be a deciding factor on whether this measurement can be made or not?"*

The answer is that it is not, and the earlier answer that implied otherwise is withdrawn. The new severity measure differs from the old measure through exactly 1 input: the verification factor V, taken from the harness's own falsifier verdict. V has 3 values, and only 1 of them changes an outcome at the critical cut: `V(False) = 0`, which annihilates the product. A finding can only take that value if its falsifier returns REFUTED.

Across every run log carrying a falsifier gate line, 13 runs in all, the gate decided 214 times. It returned REFUTED **once**. Split by cost:

- Simulated runs, 10 of them: 128 CONFIRMED, 1 REFUTED.
- Paid runs, 3 of them: 85 CONFIRMED, 0 REFUTED.
- Fisher exact test: p = 1.000000. Chi-square as the second tool: p = 1.000000.

A p-value of 1.000000 cannot distinguish the 2 groups. And the single refutation in the project's entire gate record came from a **simulated** run, not a paid run. A paid run has never produced a refutation.

So the founder's instinct is correct and the project's own archive supports it: spending money does not buy this measurement.

## 4. His shadow proposal is already the shipped configuration

He proposed: *"running both the old severity measure as live for now, and running the new severity measure in shadow for a few simulated runs, until we have enough data of the kind you say you require before we retire the old severity measure and replace it with the new one? Would that work?"*

It works, and it has been the default since 2026-10-15. `RunnerConfig.severity_spec_enabled` defaults to False, which means the old measure decides and `severity_spec_shadow()` records what the new measure would have said. The module-level mirror `_SEVERITY_SPEC` reads `{'on': False}`.

The shadow has already produced its data: 13 records across 6 run logs. What it says is that nothing moves.

- Records where the new measure changes the critical count: **0 of 13**, Wilson 95% [0.000000, 0.228095], Clopper-Pearson [0.000000, 0.247053].
- Records with any finding crossing downward: **0 of 13**, same interval.
- Verification factor totals across all 13 records: V_true 246, V_none 71, V_false **2**.
- Findings refuted, of all the shadow saw: **2 of 319** = 0.006270, Wilson [0.001720, 0.022696], Clopper-Pearson [0.000760, 0.022463].

The archive replay had predicted the new measure would move 835 of 3,298 entries downward, a 25.3% crossing rate, with the critical share falling from 41.6% to 16.3%. Live, it moves nothing, because with a refutation rate of 0.63% the verification factor almost never annihilates and the 2 measures are arithmetically indistinguishable at the cut.

**So more shadow runs will not resolve the promotion decision.** Collecting more data of the same kind produces more of the same answer. What would change the answer is a refutation rate materially above the measured 0.63%, and that is a property of the falsifiers, not of the seats, the vendors or the budget.

## 5. Three claims made during this investigation were refuted and are recorded

**Claim: "0 of 65 runs record the severity shadow."** False. It was a 0 of looking in the wrong file. `runner_state.json` has no telemetry key at all; the shadow records live in the run stdout logs as Python representations, which must be brace-matched and parsed. The real figure is 13 records across 6 logs. The project's own standing rule applies: ask what a 0 is a 0 of.

**Claim: "23 of 28 falsifiers read the original target instead of a staged copy."** False. `bench/falsifier_verify.py:224` defines `STAGED_TARGET_ROOT` as `~/CDSFL_review_targets`, so that path **is** the staged copy. The falsifiers are reading the correct file. 23 of 28 = 0.821429, Wilson [0.644086, 0.921215], name the staged root, which is right rather than wrong.

**Claim: "83.5% of falsifiers not intercepted means they ignore their targets."** Not supported. `bench/reference_runner_v3.py:990` records that the discrimination control "has never fired in the project's life" because it requires a falsifier **and** a corrected copy on the same finding, and that historically 0 of 58 entries carried both, Wilson [0.0000, 0.0621]. A control that was never fed reports not-intercepted for want of a comparison, not because the falsifier is blind.

A correlation was measured between out-of-scope path flags and not-intercepted outcomes across the 13 runs: Pearson r = 0.928710 with p = 4.559749e-06, Spearman rho = 0.835298 with p = 3.786290e-04, Kendall tau = 0.748481 with p = 1.940088e-03, and NumPy agrees with SciPy on the Pearson coefficient to 9 decimal places. All 4 runs carrying out-of-scope flags are recent, from 2026-10-15 onward, so the correlation is time-confounded and no mechanism is claimed from it.

## 6. The preflight halted on an unregistered seat, exactly as instructed

The founder's instruction, verbatim: *"If a model a researcher wishes to add fails registration, then that is a failure of both the intent to make adding a model trivial and of the mechanics I asked you to build to make this the case. So it should cause the pre-flight checks to fail and the issue should be raised loudly."*

The rerun's own log, at 03:39:24, reads: `*** SYSTEM HALTED — check 8 of 8 failed: every seat is fully registered ***`, followed by `7 check(s) passed before it; 0 did not run.` and `Investigate the failure above, then re-run.` The run proceeded only because an explicit override was supplied, and the log records that too: `POST FAILED and --ignore-post was given: proceeding anyway. The failure above is part of this run's record.`

That is the preflight registration check behaving as specified: it failed, it failed loudly, it named which tables the seat was missing from, and the override is explicit and preserved in the run's own record rather than silent. The underlying registration gap for the Fable seat was closed earlier on 2026-11-02, so a future run will not need the override.

## 7. Two defects this run exposed

**A scope check fires 100 times at its highest severity tier on a file the falsifier is required to read.** The signal is `out-of-scope path opened or listed`, recorded at CONFIRMED tier by `bench/key_access_forensics.py:943`, and it fired 100 times across 9 of the 30 findings. Every one of them is the falsifier reading the staged target root. Nothing was blocked. A CONFIRMED forensic signal that fires on correct behaviour and blocks nothing is a false positive at the tier reserved for certainty, and the project's own record holds a case where 27 of 27 false positives hid a true positive.

**The discrimination control's outcome is not persisted to the finding it concerns.** The run log reports `INDETERMINATE_NOT_INTERCEPTED` 48 times. The registry's stored `discrimination_control` field reads none for all 30 entries. So the one signal that would tell a reader whether a CONFIRMED verdict is trustworthy exists only in a text log, where no downstream consumer can compute over it. This is the simplest and most additive repair available: persist the outcome on the entry.

## 8. The commit gate has outgrown its own written limit

`hooks/pre-commit` carries this standard in its own header: *"A per-commit gate costing 11 minutes would be bypassed within a day, and a guard that gets bypassed is not a guard."* That limit is 660 seconds.

The gate measures its own duration into `.cdsfl_tmp/precommit_seconds`, and `scripts/cdsfl_sv.py` reads that figure to derive its commit timeout, which is a sound design. The commit made during this session recorded **769 seconds**, and the previous record held **800 seconds**. Those are 1.1652 and 1.2121 times the stated limit. The gate's own cost producer, `scripts/precommit_gate_cost_2026-09-10.py`, states at line 22 that the gate "takes over 11 minutes".

So the project has written down a limit, measured itself exceeding it, and has nothing that enforces it. Searching the tree, only 2 files read the duration at all: the hook that writes it and `sv`, the state saving command, which consumes it. The guard set now holds roughly 125 test files where the header's measurement was taken over 7.

The cause is structural rather than careless, and the header says so: `test_done_markers_carry_evidence` parametrises per completed task entry, so the gate's cost **grows with the task list**. It is not a fixed price.

The additive repair is not to remove guards. It is to make the cost a measured, enforced property: fail loudly when the gate exceeds its own stated limit, so the set is split deliberately into a commit-time tier and a periodic tier rather than being bypassed silently.

## 9. Assessment of the founder's 22 instructions of 2026-11-01

He asked for a full assessment of what remains outstanding from his last 2 annotated reports. The producer is `scripts/which_of_his_instructions_were_carried_out_2026-11-02.py`, and each verdict names a file that exists or does not.

**A correction first.** Earlier on 2026-11-02 the figure given to him was 13 clear instructions. There are **22**. The undercount was 9, which is 0.409091 of the set, Wilson [0.232558, 0.612652]. That count of 13 came from reading rather than from matching, which is why it is now produced by a script.

- **Carried out: 15 of 22** = 0.681818, Wilson [0.473186, 0.836394], Clopper-Pearson [0.451276, 0.861353].
- **Outstanding: 6 of 22** = 0.272727, Wilson [0.131508, 0.481517].
- **Pending a running job: 1 of 22**, now discharged by the rerun completing.

The 6 outstanding, each named by its subject rather than by a code:

1. **The severity measure's shadow half.** The new severity measure, its archive-derived bounds and a pre-registered scorer all exist. What section 4 above establishes is that no amount of further shadow running resolves the promotion, so the honest status is that his question is now answered and the decision is his to take on the evidence above.
2. **Running the type-check task over the tree.** The task exists at `scripts/type_check_task_2026-11-01.py` and is guarded. No artefact shows it has been run, which is what he asked for.
3. **Answering whether the marker vocabulary matches developer convention.** Answered in section 10 below.
4. **The fourth convergence condition on residual risk.** No difficulty estimator exists anywhere in the tree. Until such an estimator exists, the condition would be, in his own words, a round counter wearing the name of a confidence measure. Not built, and correctly not built.
5. **Retiring the explanations owed as a block.** 9 of the 11 tickets the entry names are closed or deprecated. 2 remain unconfirmed, one of them the bounded-orchestrator request he has raised 3 times. 9 of 11 = 0.818182, Wilson [0.523019, 0.948632], does not satisfy "as a block".
6. **Writing the proof and falsifier definition for him to ratify.** No definition document exists under `docs/`, `experimental_notes/` or `resources/`. He accepted the recommendation that it be written for his ratification, and it has not been written.

## 10. The marker vocabulary, and whether a developer would find it alien

He asked: *"how well do these categorisations match with established convention? Would a developer looking at these find them particularly alien? Would this potentially hinder adoption, by requiring them to learn a new vocabulary?"*

The useful distinction is between the **concepts** and the **abbreviations**, and they answer differently.

Every concept is conventional. A feature request is a first-class category in Bugzilla, GitHub Issues and Jira. A question is a standard issue label on GitHub and the organising unit of Stack Overflow and Discourse. A proposed fix is a patch or a pull request. A discussion is a GitHub Discussion. A statement requiring action is the nearest thing to a Jira task. There is no concept here that a working developer does not already hold.

The abbreviations are the project's own. `fr` is widely used and would be read correctly on sight. `qs`, `stm`, `pf` and `disc` are local shorthand and would need a legend. That legend is 5 rows long.

**Recommendation, against the 3 formal standards.** Keep the short markers, because he has stated a preference for short convenient labels and because they are an input shorthand that he types in his own annotations rather than a public vocabulary. Add a legend that renders each marker as its conventional term wherever a third party reads the output. That is the simplest sufficient fix: it changes no identity, no ticket, no stored row. It is additive: nothing is removed and the legend is reached by every third-party surface. No composition is required, and composing a rename with a legend would be strictly worse, because a rename would orphan existing rows exactly as the earlier `ds` to `disc` migration had to be handled with flat aliases.

The adoption risk is therefore low and is paid once, in a legend, rather than continuously in a vocabulary.

## Producers

- `scripts/what_actually_blocks_the_severity_promotion_2026-11-02.py` — sections 3, 4, 5, 7.
- `scripts/score_the_severity_predictions_2026-11-02.py` — section 2.
- `scripts/which_of_his_instructions_were_carried_out_2026-11-02.py` — section 9.
- `scripts/can_a_simulated_seat_ever_refute_2026-11-02.py` — the simulated against paid split.
- `scripts/precommit_gate_cost_2026-09-10.py` — section 8's gate cost.

Written under CDSFL note standard v1.9.
