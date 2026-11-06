# Free panel round — severity and residual risk — 2026-11-06

2026-11-06 21:15 GMT. 2 free seats (`cc2`, `fable`), 0 paid seats, 0 spend.

Spoken companion: `~/Desktop/CDSFL_tts/Free_Panel_Severity_Corrected_2026-11-06.txt`. That file is re-rendered rather than copied: it omits every file path, because a path read aloud by text-to-speech is noise.

## The round

| | |
|---|---|
| seats | `cc2`, `fable`, both `claude_cli`, both free on the Max subscription |
| paid seats | **0** — verified by execution, `MODELS` resolves to `FREE_SEATS` with `PANEL_ONLY` unset |
| responded | 2 of 2, all 10 required fields each |
| wall clock | 724.4 s; 20 s stagger saved 0.4182 against serial |
| brief | `experimental_notes/Brief_Severity_Corrected_2026-11-06.md`, 0 validator findings, 0 lint findings at dispatch |
| log | `bench/logs/severity_corrected_2026-11-06/` |

## 1. The brief's lead framing is refuted, by both seats independently

The brief claimed §7.7 and §7.8 of `docs/MATHEMATICAL_APPENDIX.md` contradict each other: a disproved finding scores `Sev(f) = W · confidence · V(False) = 0` under §7.7, and `S_v = 0.27289178365887046` under §7.8 Approach B.

**They do not contradict each other.** §7.11 line 1369 *conjoins* them:

> `selected(f) ≡ (Sev(f) > τ_sev) ∧ (S_v(f) ≥ 0.5) ∧ (class(f) = HARD ∨ Sev(f) > τ_soft)`

And §7.8 line 1311 sets `Λ_prior = 0` from *"uniform prior: P(claim true) = 0.5 before any verification"* — so `S_v` is a posterior **credence**, not a severity. The 0-against-0.273 gap was produced by substituting `S_v` for `confidence · V`, which no section and no code does. Checked at source: §7.7 line 1255 reads `confidence`.

## 2. The tool attribution was false, which is the worse half

The brief said the contradiction was *"verified 2026-11-05 by SymPy and z3 independently"*. Those tools verified 2 true propositions — that `V(REFUTED) = 0` makes the product 0, and that `S_v` never reaches 0. **Neither establishes that the 2 expressions denote the same quantity**, which is the step the headline needed and which is a question about §7.8's text rather than about arithmetic.

Related: [[feedback_a_verification_can_pass_for_the_wrong_reason_2026-11-02]], [[feedback_a_figure_can_answer_a_different_question_2026-10-31]].

## 3. The real defect is a naming collision

`S_v` is called "multi-verifier Bayesian **severity**" at `docs/MATHEMATICAL_APPENDIX.md:1373` and again in the glossary at `:2155`, while §7.8 derives `P(claim true)`. Folded back: a clarification stating that `S_v` is a credence and not a severity, and that the caution-1 substitution replaces `confidence` **alone** with `V` retained, so the key property survives it.

## 4. The surviving argument was strengthened into a shape theorem

For `Sev = W · B` with `W ∈ {W(SOFT), W(HARD)}` and `B ∈ [0,1]` **any** composition of belief factors:

> `Sev ≥ c` ⇔ `W = W(HARD) ∧ B ≥ c`, for every `c ∈ (W(SOFT), W(HARD)]`

Re-derived here from scratch rather than re-run: z3 returns `unsat` for the negation of both directions over all 3 variables at once; the premise is `sat`, so it is not vacuous; and at `c = 0.5` a SOFT counterexample is `sat`, so the open interval is tight. SymPy puts the SOFT supremum at `1/2`.

It is shape-quantified, so it pre-refutes repairs not yet written, including the 2026-11-04 seat's `EL = Sev · P`.

## 5. The census dispute — the seat was right, and my correction of it was not

`fable` returned **DOES NOT REPRODUCE** against the brief's `1,559 of 3,474` and was right. My first replacement figure was wrong and is withdrawn.

| population | frame | status |
|---|---|---|
| **3,170** | whole-file SHA-256 digest dedup over `logs/**/runner_state.json`, 67 distinct files | **authoritative — and it is `fable`'s figure** |
| 3,474 | no dedup at all | what the brief told the seats |
| 3,311 | 1 directory level, which **follows** `exp36_evidence_latest` and `experiment_18` | 1 run counted twice |
| 3,101 | my name-based exclusion of `harvest`/`worktree`/`sandbox` | **WITHDRAWN — over-aggressive** |

**The method already existed and is better than mine.** `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` has hashed the whole file and skipped repeat digests since 2026-10-12. That catches a copy under **any** directory name, collapses a symlink implicitly (2 paths to 1 file → 1 digest), and cannot go stale when a new harvest directory name appears — which is precisely what defeated my name list. My exclusion additionally dropped `shakedown_2026-09-29/arm1_harvest/runner_state.json`, which is not a byte-identical copy.

**And the frame defect is not a finding of this round.** That producer documents it in its own docstring, and the memory lesson [[feedback_a_safeguard_can_corrupt_what_it_protects_2026-11-04]] records it with these exact figures — 88.0952% against 84.3750%. What happened tonight is that a known, recorded, already-solved defect **recurred in 3 places at once**: the panel brief, `scripts/the_severity_census_has_three_frames_2026-11-06.py`, and the producer `cc2` delivered. The seat caught it; the record had caught it 25 days earlier. See also [[feedback_check_the_record_before_declaring_a_gap]].

**That point is now closed, and `fable` is right on both figures.** `falsifier_verdict` holds the **empty string on 305 entries**; my predicate was `is not None`, which counted a present-but-blank field as a recorded verdict. `1,602 − 305 = 1,297` exactly, so `fable`'s figure reproduces: **1,297 of 3,170 = 0.409148**, Wilson 95% [0.392152, 0.426364], Clopper-Pearson [0.391965, 0.426499], routes agreeing to 5.6e-17. Its stated 40.91% is correct.

The field's distinct values are `None` (1,568), `CONFIRMED` (1,158), `""` (**305**), `ERROR` (53), `UNTOOLABLE` (42), `REFUTED` (32), `NON_DISCRIMINATING` (8), `INTEGRITY_VIOLATION` (4). This is [[feedback_a_signal_is_not_a_measurement_2026-10-30]] in its own terms: ask what a 0 — or a blank — is a 0 of.

**Frame-independent regardless:** `confidence` present on **0** entries in all 4, Wilson 95% [0.000000, 0.001210] on the authoritative frame. "Recomputing §7.7 as written is unsatisfiable today" stands in every frame.

## 6. The brief repair is what made the delivered work exist

Section 4 did not require a fix written **into the sandbox repository tree at its real path** until it was repaired before dispatch. Folded back and passing, 60 tests:

- `scripts/no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py` (cc2)
- `scripts/the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py` (cc2)
- `bench/tests/test_no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py` (cc2)
- `bench/tests/test_severity_composition_key_property_2026-11-06.py` (fable)

`cc2`'s producer also decided a composability question by **measurement** and against composing: pairing the documentary repair with a threshold change reclassifies 0 further entries, so the single fix is preferred.

See [[feedback_a_seats_finding_can_sit_in_a_sandbox_2026-10-15]].

## 7. The seats' own guards were then mutated, and 3 of 4 mutations passed unnoticed

`scripts/the_folded_back_seat_guards_mutations_2026-11-06.py`. Only M1 was caught:

| mutation | seat guard |
|---|---|
| M1 the credence clarification deleted | **RED** |
| M2 `W(SOFT)` raised to 1.0, emptying the theorem's own interval | GREEN — missed |
| M3 `V(False)` changed to 0.1, destroying the key property a guard is *named* for | GREEN — missed |
| M4 §7.11 stops conjoining `Sev` and `S_v` — the fact that refuted the brief | GREEN — missed |

The seats pinned the prose they added, not the numbers their argument rests on — the `execute-do-not-grep` directive in its own terms. `bench/tests/test_the_severity_factor_values_are_pinned_2026-11-06.py` now pins the factor values and the conjunction, reading them out of the §7.7 table rather than assuming them. **4 of 4 mutations red.** The seats' own guard files were left unchanged so provenance stays legible.

## 8. What this changes for 2 open decisions

**B87 — whether the severity formula or the evidence rule should change.** Its framing moves: the 2 sections do not conflict, so the question is not which to amend. What remains is that the formula needs `constraint_class` and `confidence`, recorded on **0** entries, and collecting them is prior to choosing any bound.

*Recommendation.* Collect the 2 missing inputs; amend neither document. **Additive** — nothing is removed and a measurement becomes possible that is impossible today. **Simplest sufficient** — the round established neither document is wrong, so an amendment would be a change with nothing to fix. **Composability** — no composed fix is claimed; no measurement shows one dominates collection alone.

**B121 — whether to de-duplicate the severity archive and move its 2 floors.** Premise confirmed by a second route, and the entry is narrower than the defect: the symlink is 1 of at least 3 miscounting routes.

*Recommendation.* Exclude every harvest copy **and** resolve symlinks, not the 1 link the entry names. **Additive** — both floors stay as loss detectors, re-derived in the same commit. **Simplest sufficient** — the 3 routes share 1 cause, a frame that was never declared, so 1 declared frame fixes all 3. **Composability** — the 3 narrow fixes are *not* preferred to the single broader one, because the measurement shows a common cause rather than 3 independent faults.

Written under CDSFL note standard v1.9 (1 November 2026).
