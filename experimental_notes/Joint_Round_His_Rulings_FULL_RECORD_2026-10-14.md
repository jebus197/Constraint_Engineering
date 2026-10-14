# Joint round on his rulings of 2026-10-13 — FULL RECORD, unfiltered

2026-10-14T19:51:43+01:00. Branch `sim/shakedown-2026-09-29`. Round `joint_his_rulings_2026-10-13`.

**Audience: a reader who can follow a file path but was not in the session.** Both seat replies are reproduced BELOW IN FULL and unedited. Nothing here is summarised in place of the output; the summary lives in the companion note and in the chat reply, never instead of this file.

## WHAT THIS ROUND WAS AND WHY IT WAS OWED

The blind round `his_rulings_2026-10-13` collected 2 replies on 2026-10-13 and never got its joint half. Its composed fixes were applied anyway. The star topology is 2 halves and only the first had been run, so a joint round was owed under the founder's ruling of 2026-10-06 that the topology be unskippable.

**The round was dispatched twice.** The first attempt was killed 30 seconds in, because the harness printed "star topology: BLIND round" while recording "joint round": the brief POINTED at `bench/logs/his_rulings_2026-10-13/cc2/` and `fable/`, directories that do not exist, the replies being `cc2.json` and `fable.json`. The corrected brief embeds both blind replies verbatim and is 46,848 characters; `round_kind` then DETECTS it as joint rather than taking the operator's word for it.

**Seats: cc2 (Claude Opus 4.7) and fable (Fable 5.1), both free on the Max subscription. No paid dispatch occurred and none is authorised.**

| seat | chars | tool calls | elapsed | J1 | J2 | J3 | J4 |
|---|---|---|---|---|---|---|---|
| cc2 | 26,785 | 126 | 1073.2 s | CONFIRMED | CONFIRMED | CONFIRMED | PARTIAL |
| fable | 19,898 | 60 | 980.1 s | CONFIRMED | CONFIRMED-ASSUMED | CONFIRMED | PARTIAL on the premise |

## THE 4 QUESTIONS PUT TO THEM

J1. Attack the composition as a system: with the severity shadow, the single-membership queue, the retired pruner and the ablation switch all live at once, is there an interaction none of us tested?

J2. The open seat disagreement on severity, and specifically whether appendix section 7.8 Approach B's verifier table rests on MEASURED or ASSUMED rates. If assumed, substituting it relocates the vote rather than removing it.

J3. The never-routed class, on which the founder ruled: confirm or refute his claim that few such issues are genuinely computationally irreducible, and if it holds, specify the feedback mechanism precisely enough to build.

J4. That 0 of 16 headings of the core formal directive reach any seat, and whether that changes any verdict either gave in the blind round.

## FILES EACH SEAT PROPOSED, AS PATHS IN ITS OWN SANDBOX

Nothing is auto-applied. These are proposals to the human in the loop.

### cc2

- `.cdsfl_deny_canonical_writes.sb`
- `PAPER.md`
- `bench/cdsfl_registry/composer.py`
- `bench/confer_maths_panel_2026-09-05.py`
- `bench/logs/the_directive_set_and_capability_2026-10-14/BRIEF.md`
- `bench/reference_runner_v3.py`
- `bench/tests/test_a_blind_round_has_a_joint_round_2026-10-08.py`
- `bench/tests/test_the_transport_cap_names_what_it_dropped_2026-10-14.py`
- `bench/tests/test_which_core_directive_sections_reach_a_seat_2026-10-14.py`
- `docs/MATHEMATICAL_APPENDIX.md`
- `docs/experimental_notes/CDSFL_Complete_Mathematical_Framework_Technical_2026-03-27.md`
- `experimental_notes/Falsifier_Supply_Feedback_SPEC_2026-10-14.md`
- `experimental_notes/The_Directive_Set_Plain_English_2026-10-13.md`
- `scripts/approach_b_rates_are_assumed_not_measured_2026-10-14.py`
- `scripts/how_many_untoolable_were_never_attempted_2026-10-14.py`
- `scripts/panel_brief_validate.py`
- `scripts/retirement_moved_a_logged_loss_into_an_unlogged_one_2026-10-14.py`
- `scripts/the_archive_denominator_triple_counts_harvest_copies_2026-10-14.py`
- `scripts/the_joint_debt_is_discharged_by_a_directory_2026-10-14.py`

### fable

- `.cdsfl_deny_canonical_writes.sb`
- `bench/cdsfl_registry/composer.py`
- `bench/confer_maths_panel_2026-09-05.py`
- `bench/logs/the_directive_set_and_capability_2026-10-14/BRIEF.md`
- `bench/tests/test_a_blind_round_has_a_joint_round_2026-10-08.py`
- `bench/tests/test_the_manifest_records_the_length_cap_cut_2026-10-14.py`
- `docs/MATHEMATICAL_APPENDIX.md`
- `experimental_notes/Falsifier_Debt_Feedback_Spec_2026-10-14.md`
- `experimental_notes/The_Directive_Set_Plain_English_2026-10-13.md`
- `scripts/approach_b_rates_are_assumed_2026-10-14.py`
- `scripts/panel_brief_validate.py`
- `scripts/the_cap_cuts_what_the_manifest_claims_2026-10-14.py`
- `scripts/the_joint_debt_is_discharged_by_a_directory_2026-10-14.py`
- `scripts/the_untoolable_were_never_attempted_2026-10-14.py`
- `scripts/what_the_minimal_rendering_delivers_2026-10-14.py`

---

# SEAT REPLIES, VERBATIM AND COMPLETE

Each reply is reproduced EXACTLY as the seat returned it, between verbatim markers. **Nothing has been edited, reordered, shortened or corrected**, including where a seat's wording would not satisfy this project's own note standard. That standard governs prose written here for the founder; it does not govern another author's record, and altering a seat's words to satisfy it would make the record a paraphrase.

## Seat: cc2 — Claude Opus 4.7

`ok=True`, 26,785 characters, 126 tool calls, 1073.2 s, route `claude_cli`, model `cc2`.

<!-- verbatim-begin: cc2 (panel joint_his_rulings_2026-10-13) -->

Everything executed. 99 tests green across the 9 affected suites; Wolfram third-sourced the Approach B weights (exit 0, output present).

---

# JOINT ROUND — ONE SEAT'S RETURN, 2026-10-14

**Identity note, stated once.** I cannot determine from the artefacts which of the two blind replies was mine, and I am not going to guess: every verdict below is re-derived from execution in this tree, and `disagreement` is stated against the positions **as recorded in the two replies**, whichever was which.

**Tools.** SymPy, z3, statsmodels, mpmath, NumPy, SciPy primary throughout. Wolfram Language (local Wolfram Engine, `wolframscript`, exit 0, no `Name::tag`, no `$Failed`, `Out` present) third-sourced the Approach B derivation: `{6.897704943128636, -4.604169685654507, 3.619886582626985, 0.9732410714285714, 0.9989909182643794}` — agrees with SymPy and mpmath to float64 epsilon.

---

## J1 — ATTACK THE COMPOSITION, AS A SYSTEM

**item** J1
**verdict** **CONFIRMED — there is an untested interaction, and it is a silent-evidence-loss exposure created by the composition, not by either change alone.** The retirement is still right; the residual it leaves is unrecorded.

**The interaction, as a causal chain.** `_prune_for_coherence` deleted whole SOFT packets and **every deletion was recorded** in `pruned_soft`, carried into `manifest["pruned_soft"]`. The `max_directive_chars` cap in `compose` (`bench/cdsfl_registry/composer.py:1439`) also removes directive text and **recorded nothing**. It cuts the **tail**, and packet order is universal → domain → situation (`:1333-1384`), so what it drops is the per-dispatch **situation** layer: `review_target`, `code_extracts`, `adversarial_brief`. Retiring the pruner keeps every SOFT packet, so `rendered` is strictly longer and the cap fires on **more** compositions. The loss mode moved from a logged channel to an unlogged one — §10 category 4.

**evidence** `python3 scripts/retirement_moved_a_logged_loss_into_an_unlogged_one_2026-10-14.py`, 5 models × 18 domains = 90 compositions on the live `compose()`:

```
cap at :1439 fired           ON 31/90 = 34.4444% [25.4459%,44.7165%] | OFF 42/90 = 46.6667% [36.7084%,56.8978%]
text lost, pruned_soft EMPTY ON 31/90 = 34.4444%                     | OFF 42/90 = 46.6667%
situation packet DELETED     ON 35/90 = 38.8889% [29.4699%,49.2175%] | OFF  0/90 =  0.0000% [0.0000%,4.0936%]
dispatch payload tail LOST   ON 66/90 = 73.3333% [63.3802%,81.3762%] | OFF 42/90 = 46.6667%
total rendered chars         ON 457,788 | OFF 528,256   (+70,468)
chars dropped by the cap     ON  68,088 | OFF  85,031
PRODUCER vs CONSUMER on 'did the cap fire': 0/90 rows disagree
```

Producer = live `compose()`; consumer = independent recomputation from `manifest["packets"]` char counts. **They agree on all 90.** The retirement dominates on payload survival (73.3% → 46.7% lost) and on situation deletion (35/90 → 0/90) — I am not reversing it — while unlogged loss rises 31 → 42.

I corrected my own conflated metric in place: "domain packet absent" mixes *no domain directive file exists* (40/90, not a loss) with *the pruner deleted it* (3/90 ON, 0/90 OFF).

**Also executed, and it found nothing:** the severity shadow is non-mutating and idempotent. Registry JSON sha `12dd5fca85fc` before and after `severity_spec_shadow()`, queue membership `[] → []`, `unverified_critical_count 0 → 0`, two calls byte-identical. **That candidate interaction is refuted.**

**tools** live `compose()` vs manifest recomputation (agree, 0/90 disagreements); statsmodels Wilson vs hand-derived Wilson in mpmath at 40 dp (agree=True on all 10 proportions).
**interval** every proportion above: numerator/denominator/Wilson 95%, method named, both tools printed by the producer.

**falsifier** `bench/tests/test_the_transport_cap_names_what_it_dropped_2026-10-14.py`.
Red, composer patch reverted in a scratch copy: `4 failed, 3 passed` — `KeyError: 'transport_truncated_chars'`, `KeyError: 'pre_cap_chars'`.
Green, patched: `7 passed in 0.57s`. Includes an anti-vacuity test, a two-sided "no truncation ⇒ no spurious record", a byte-identity assertion on `rendered` (so the repair cannot have changed a prompt), and an additive-standard test asserting the runner reads the new key **at the dispatch site**.

**refutation** I tried to overturn my own direction claim: if pruning OFF ever produced a *shorter* pre-cap text, J1 is dead. `test_the_interaction_direction_holds` asserts it and passes; the producer confirms +70,468 chars. I also tried the shadow × queue interaction (above) and the ablation-switch double-gate (`RunnerConfig.composer_coherence_pruning` → `_COMPOSER_COHERENCE_PRUNING` → `compose`, all three now default False/consistent — no stale-mirror path found). Both returned negative.

**fix** `bench/cdsfl_registry/composer.py` (records `pre_cap_chars`, `transport_truncated_chars`, `transport_truncated_layers`; warns on the same idiom as the existing budget warning) + `bench/reference_runner_v3.py` at the live dispatch site (`_log` naming chars dropped and layers not delivered whole, explicitly `NOT counted in pruned_soft`). `rendered` is byte-identical, so **no prompt changes and no replay is invalidated**. `manifest` had **no reader anywhere in the runner** before this — a manifest-only fix would have been an addition nothing reaches, which is why the reader is at the dispatch path.

**disagreement** Neither blind reply examined the cap at all; both treated directive loss as the pruner's. I hold that the transport cap is now the *larger* loss channel and the only unlogged one. I also differ from the reply that said retirement "is replay-invalidating": the retirement changes prompts, but **recording** the cap does not, and the two should not be priced together.

**termination** Two HARD assumptions tested (cap cuts the tail; retirement lengthens the text) and both hold; producer and consumer agree on all 90 rows; two further candidate interactions probed and refuted. Stopping.

---

## J2 — THE SEVERITY DISAGREEMENT, AND APPROACH B's TABLE

**item** J2
**verdict** **CONFIRMED: the rates are ASSUMED, not measured — and worse, they are labelled "empirical" in two documents with nothing behind them.** Substituting Approach B relocates the vote from the model to the appendix's author rather than removing it. The seat disagreement about collecting the two inputs is therefore **not settled by Approach B**, and anyone citing §7.8 as "the real replacement" must now carry that.

**evidence** `python3 scripts/approach_b_rates_are_assumed_not_measured_2026-10-14.py`:

```
[1] measurement vocabulary in §7.8: ['calibrated']   <- refers to the §7.11 THRESHOLD being
                                                        calibrated to Λ_prior = 0, not to the rates
[2] producers cited in 7.8: NONE   |  producers cited in 7.7: ['scripts/the_severity_cut_collapses_the_formula_2026-10-13.py']
[3] files matching the rate triple: 20; NON-prose (data/script) files: only this script
[4] Lambda_total / C_sympy / C_dim / C_num in executable .py code: 0 implementations (all 5 hits are prose)
[5] SymPy closed form, Λ_prior=0, one verifier PASS:  S_v = TPR/(FPR + TPR)   identical to TPR/(TPR+FPR): True
    veto: |w-_SymPy| 4.6042 > sum other w+ 3.6199 -> True
    TPR at which the veto FAILS: mpmath 0.973241 / sympy 0.973241 (agree=True)
[6] z3: can the veto FAIL with every verifier better than chance? sat
    counterexample {t_s:1/2, f_s:1/4, t_d:1/2, f_d:1/4, t_n:1/2, f_n:1/4}
    do the PUBLISHED rates violate the veto? unsat (holds AT this table)
```

Three derived consequences, each a reason the substitution is not a removal of the vote:

1. **For one verifier with Λ_prior = 0, `S_v = TPR/(TPR+FPR)` exactly** — a pure function of the assumed rates, with no dependence on the claim. A lone SymPy pass gives 990/991 = 0.998991; a lone numerical pass gives 14/17 = 0.823529. Both clear the §7.11 threshold of 0.5.
2. **The "veto property" is contingent, not structural** (z3 `sat`), and fails once SymPy's assumed TPR drops below **0.973241** at FPR 0.001. The 2026-03-27 meta-test recorded exactly this and the note was never applied to §7.8.
3. The only per-tool rate tracking in the codebase, `bench/dm/_shadow_stage6.py`, **disclaims being an FPR**: "FPR = P(PASS | H_0 true) requires ground-truth labels."

**tools** SymPy (exact rationals) vs mpmath (30 dp): agree to <1e-12 on all six weights. z3 on the veto's structural status. Wolfram Language third-sourced the weights, the threshold and `S_v` (values above). statsmodels/mpmath not needed — no proportion is claimed here beyond those already reported.
**interval** No new proportion is asserted in J2. The only counts are exhaustive, not sampled: producers cited in §7.8 = 0/1; non-prose files containing the rates = 0 (excluding my own script); executable implementations of Approach A or B = 0.

**falsifier** **No red/green test, and I am saying so rather than dressing one up.** J2 is a provenance question; the falsifier is the mechanical absence check in the producer (find a producer, or there is none — the project's own standing rule makes that test executable) plus the z3 `sat` result, which would be `unsat` if the veto were structural. If anyone produces the measurement, step [3] goes non-empty and my verdict is refuted in one command.

**refutation** I tried to find the measurement: repo-wide multiline search for the rate triple, a search for any producer named for verifier rates or calibration, and an inspection of the one ground-truth candidate in the tree (`bench/seeded_defect_catalogue.py` with `bench/score_exam.py`) — its metrics are per **model run**, not per verifier, and nothing measures whether SymPy catches planted defects at 99%. No `.git`, so history could not be checked; that is a named limitation, not a result.

**fix** `docs/MATHEMATICAL_APPENDIX.md` §7.8 — provenance paragraph stating the rates are assumed, with the three derived consequences and the producer. `PAPER.md:1166` and `docs/experimental_notes/CDSFL_Complete_Mathematical_Framework_Technical_2026-03-27.md:148,154` — the word **"empirical" corrected to "ASSUMED" in place**, each with the correction stated beside it. Same intervention as the appendix status-row correction one of the blind replies made, applied to the same class of defect: a false provenance claim that survives because it reads as settled.

**disagreement** Both replies named §7.8 Approach B as the real replacement. **I now hold that it is not, as it stands** — it is a different author's number, not a tool's, and swapping it in would let "severity is tool-decided" be asserted on an unmeasured table. That is a change of position produced by the evidence, and it cuts against both blind replies, not one. On the narrower split: the seat that wanted the two inputs collected informative-only is right that the bound (W defaults HARD, V harness-owned, confidence can only lower) is worth having; the seat that said collecting them does not make severity tool-decided is right that it does not. Both are true and they are not in conflict — what is in conflict is the shared assumption that §7.8 fixes it.

**termination** The question asked — measured or assumed — is answered on four independent legs. Stop here; the next step is a measurement of verifier TPR/FPR against planted ground truth, which is an experiment, not a review finding.

---

## J3 — THE NEVER-ROUTED CLASS

**item** J3
**verdict** **CONFIRMED — his claim holds.** Genuine irreducibility is attestable for at most 6.5% and demonstrably stated for **0.93%**, while **70.43%** carry no record of any attempt and **90.35%** target a `.py` file. **PARTIAL on one half:** the archive cannot *quantify* true irreducibility, because no field records an attempt — 0 of 3,298 carry `untoolable_reason`, `irreducible_reason`, `falsifier_attempts` or `execution_log`.

**evidence** The brief's figure reproduces **exactly** through the canonical generator (`scripts/severity_was_never_computed_from_the_model_2026-10-12.py`): `1938/3298 = 58.7629%`, and the predicate is specifically `falsifier_code` absent-or-blank-after-strip (all 41 UNTOOLABLE entries store empty code, so "no falsifier OR UNTOOLABLE" is the same 1,938). Classification, exhaustive and disjoint, precedence to irreducibility first:

| class | k/1938 | % | Wilson 95% |
|---|---|---|---|
| demonstrably irreducible (a reason says so) | 18 | 0.9288% | [0.5883%, 1.4634%] |
| attempt recorded, no falsifier stored | 359 | 18.5243% | [16.8575%, 20.3156%] |
| administratively moot (merged) | 196 | 10.1135% | [8.8491%, 11.5358%] |
| **never attempted — nothing but the claim** | **1365** | **70.4334%** | **[68.3629%, 72.4231%]** |

Widest conceivable irreducible bound (any reason-bearing entry) 126/1938 = 6.5015% [5.4876%, 7.6876%]. Objective reducibility: 1751/1938 = 90.3509% [88.9554%, 91.5867%] target a `.py` file; 90.3509% carry a code reference or a numeric literal; only 41 (2.1156%) are the one prose `flaw_class`. **36/3298 = 1.0916% [0.7895%, 1.5074%]** were called UNTOOLABLE or ERROR by the machinery and later decided by a falsifier — direct instances of "never attempted, in fact toolable". Ratio never-attempted : irreducible = **75.8 : 1**.

**A side-finding I found while reproducing the denominator, and it moves the published figure.** The canonical glob has no exclusion, so it reads **harvested seat sandboxes stored under `bench/logs`**: `python3 scripts/the_archive_denominator_triple_counts_harvest_copies_2026-10-14.py` →

```
entries with numeric severity, as published : 3298
  inside harvested-sandbox copies           : 304
  distinct keys among those copies          : 152   => counted 2.0x within the copies alone
  copies also present in the clean archive  : 152 of 152
no-falsifier share, copies INCLUDED : 1938/3298 = 58.7629% [57.0736%, 60.4318%]
no-falsifier share, copies EXCLUDED : 1886/2994 = 62.9927% [61.2476%, 64.7044%]
```

152 findings are counted **three times**. The published figure is right about the files and wrong about the findings, and the direction matters: excluding copies makes the problem **larger**. I did **not** change the canonical producer — its figure is quoted across several documents and restating it is his call, not a seat's — so the script measures the contamination and leaves the decision a number.

Earlier in this turn my own first recount gave 3,515 and then 3,211; both were my glob, not the canonical one. I am reporting that rather than only the figure that worked.

**tools** statsmodels `proportion_confint(method='wilson')` vs a hand-derived Wilson in mpmath at 50 dp (normal quantile from `mpmath.erfinv`, not a tabulated 1.96), plus Clopper–Pearson from `scipy.stats.beta` for comparison. 17 proportions, worst |statsmodels − mpmath| = **1.110e-16**, agree to 1e-12. The 1,938 and 3,298 were each reproduced twice through two different code paths.
**interval** every figure above carries numerator, denominator and a 95% Wilson interval, method named.

**falsifier** `scripts/how_many_untoolable_were_never_attempted_2026-10-14.py` (both `--help` free; full key inventory printed before any count, which is what makes the PARTIAL verdict auditable) and `scripts/the_archive_denominator_triple_counts_harvest_copies_2026-10-14.py`. **No red/green unit test, stated plainly:** this is a measurement of an archive, not a code defect, so there is no unpatched tree for it to fail against.

**refutation** The cross-run route that would most strongly support his claim — findings first recorded UNTOOLABLE and later closed by a falsifier under the same dedup key — first returned **60**, and all 60 were an artefact: 82 entries carry a near-empty `description` and collided on one hash. That route now returns **0** and the retraction is printed by the script. The surviving instance count, 36, comes from a different and stricter route (an entry whose own `routing_history` logged UNTOOLABLE or ERROR and which a falsifier later decided). I am reporting the retraction because a 60 would have been the single most quotable number here.

**fix** `experimental_notes/Falsifier_Supply_Feedback_SPEC_2026-10-14.md` — the mechanism, specified against real call sites, in four parts: (1) **build the attempt record first** — `falsifier_attempt = {round, outcome, detail}`, written where `falsifier_verdict` is already written, absent reading as `NOT_ATTEMPTED` so no migration; (2) a fifth `FindingFeedback` kind **NO_FALSIFIER** in `bench/dm/_feedback.py`, ranked below REJECTED and above DUPLICATE, inheriting the existing `top_k` cap so the prompt cannot blow up; (3) the model must return **either** a runnable falsifier **or** a named `NO_TOOL_APPLIES` justification — the second is a legitimate answer and is what turns the 70.43% from silence into data; (4) **no convergence authority moves** — the record gates nothing, admits nothing, and a justification never closes a finding. The channel already exists and already does this for four other record kinds; the root cause is the missing record, not a missing loop.

**disagreement** One blind reply held that structurally-unresolvable sub-criticals belong in a report bundle with zero weight; the other that the class has no name in the machinery at all. **The measurement cuts against the premise under both:** the class whose size was being debated is 0.93% demonstrably, at most 6.5% conceivably, and the 70.43% that dominates it is not unresolvable but unattempted. I therefore differ from both on priority — the argument was about how to excuse or name a class that is two orders of magnitude smaller than the one nobody measured.

**termination** His claim is confirmed on four independent legs and the one unanswerable half is named with the key inventory that proves it unanswerable. Stopping; the next step is building Part 1, which is his to authorise.

---

## J4 — THE DIRECTIVE THAT DOES NOT ARRIVE

**item** J4
**verdict** **PARTIAL.** CONFIRMED on the delivery facts, and **sharper** than the brief: the share is exactly the recorded C0040 figure and the integrity section reaches no seat by any route. **REFUTED on one clause** — the runnable-falsifier *mandate* does reach seats, through `_gate_falsifier_directive`, not through the directive files. **It changes one of my positions and leaves the rest standing, and I say which below.**

**evidence** Executed against the live composer and the runner's own assembly:

```
cdsfl_core_formal.md on disk 27,803 chars, 15 '## ' sections
every cap: opus 12,000 / chatgpt 8,000 / codex 6,000 / gemini 8,000 / deepseek 4,000
  -> use_minimal is TRUE for every model on every compose (composer.py:592-595)
universal delivered: 2,503 chars, sha 72830fac992fe284 -- BYTE-IDENTICAL for all 5 seats
2503/27803 = 9.0026%   <- reproduces the recorded C0040 figure exactly
headings surviving in the delivered text: 0 of 15

FULL ASSEMBLY (composer rendered_text + operational directive appended uncapped) = 50,411 chars
  gate OFF : 'falsifier' 0   'FALSIFIER' 1   'FALSIFIED' 0   'execute_python' 0
  gate ON  : 'falsifier' 2   'FALSIFIER' 2   'FALSIFIED' 1   'execute_python' 1   (+641 chars)
'worked proof' : 0 in cdsfl_core_formal.md, 0 in cdsfl_operational.md  -- confirmed
'Falsifier Integrity' / 'Runnable Falsifiers' : 1 each in core_formal, 0 in operational
sections reaching a seat with the gate ON: 1 of 15 ("1. Constraint Classification",
  and only because the minimal rendering reproduces that phrase, not the section)
```

So the "falsifier appears once" in the brief is the single uppercase `FALSIFIER` in the operational file; lowercase is **0** before the gate rewrite. With `_FALSIFIER_GATE = {"on": True}` (the live default) the §2 rewrite injects the mandate — which is the clause I refute. What reaches **no** seat by **any** route is **"Falsifier Integrity — Do Not Reach for the Answer"**: do not read a scoring key, do not weaken or skip a test, do not assert a verdict you did not compute, do not terminate early. That section's own argument is that these must be stated as specific prohibited behaviours because a principle gets filtered out by the reasoning it was meant to catch — and it is the part that is not delivered.

**Does it change any verdict?** Plainly:

- **It does not change the severity derivation, the queue-membership fix, or the halt-bound measurement.** Those are algebra and harness code; what text a seat received does not enter them. Saying otherwise would be using J4 as a general-purpose doubt.
- **It does not change the pruner retirement.** The minimal rendering is keyed on `max_directive_chars`, not on `_prune_for_coherence` — the retirement producer's own Property 3 already says so, and I re-ran it to confirm. Retirement must not be read as having closed C0040. It did improve on his determinism ground, and I verified that independently: the delivered universal text is byte-identical across all five seats.
- **It does change my reading of J3, and that is a real change.** 70.43% of findings carry no falsifier and no record of an attempt, while the section defining what a falsifier must be, and the section forbidding the shortcuts around it, do not reach any seat through the directive files. Non-delivery is a live candidate cause for a rate I had been treating as a behavioural property of the models. It also reorders the J3 build: asking for compliance with an undelivered rule is not a measurement. That ordering is now written into the spec as a precondition rather than a parallel task.

**tools** live `compose()` / `_load_universal_directive` / `_gate_falsifier_directive` (execution, not grep: the gate function was **called** and its output diffed against the ungated assembly); sha256 across the five seats; independent re-run of `scripts/retiring_the_pruner_dominates_2026-10-13.py`, which confirms Property 3 ("retirement does not close C0040") in its own words.
**interval** 2503/27803 = 9.0026% — exhaustive, not sampled: both terms are byte counts of files on disk, so a confidence interval would be a category error and I am not manufacturing one. Heading survival 0/15 and section delivery 1/15 are likewise exhaustive counts. The only sampled proportions in this reply are in J1 and J3, where intervals are given.

**falsifier** `bench/tests/test_which_core_directive_sections_reach_a_seat_2026-10-14.py`, **6 passed**. **This is a pin, not a red/green falsifier, and I am not presenting it as one** — there is no patched/unpatched pair because I changed no behaviour. It is two-sided and fails in both useful directions: red if the delivered share moves off 9.0026%, red if a heading starts surviving (with the message "this is an IMPROVEMENT; replace this assertion with the positive form"), red if the gate rewrite becomes a no-op (at which point the mandate reaches nobody by any route), and red **when the integrity-delivery defect is repaired** — the message says to replace the assertion with its positive form and cite the ruling, not to delete or loosen it.

**refutation** I tried three ways to show the integrity text does arrive: the operational directive (appended in full, exempt from caps) — 0 occurrences; the gate rewrite — adds the mandate but not the integrity prohibitions; and the minimal rendering itself — 0 of 15 headings, and `"scoring key"` absent from the whole 51,052-character gated assembly. I also checked whether `use_minimal` could be false for some seat: it cannot, since 27,803 exceeds the largest cap, and the anti-vacuity test will say so the day a trim lands.

**fix** `bench/tests/test_which_core_directive_sections_reach_a_seat_2026-10-14.py` — the guard, with the measured figures in place. **No delivery fix proposed, and the reason is the standard, not caution:** what text every seat must receive is his decision; it changes every prompt and every future run's comparability; and the operational directive's uncapped route means a repair is available without touching the caps, which makes this a content decision rather than an engineering one. Choosing it quietly is how an addition nothing reaches gets born — or worse, how a prompt change nobody authorised enters the record.

**disagreement** Neither blind reply reported directive delivery at all, so there is no position to differ from here. Where I differ from the **brief**: its clause that the falsification machinery "was not reaching any seat" is too strong — the mandate arrives via the gate — and the precise, materially worse fact is that the **integrity** section arrives nowhere. I would rather the sharper claim were the one on the record.

**termination** Both HARD assumptions tested (the cap is unconditional for every model; no alternative route delivers the integrity text) and both hold. Two consecutive probes produced no new above-threshold finding. Stopping.

---

## FILES WRITTEN, ALL AT REAL PATHS IN THIS TREE

```
scripts/retirement_moved_a_logged_loss_into_an_unlogged_one_2026-10-14.py   (new, --help free, J1 producer)
scripts/approach_b_rates_are_assumed_not_measured_2026-10-14.py             (new, --help free, J2 producer)
scripts/how_many_untoolable_were_never_attempted_2026-10-14.py              (new, --help free, J3 producer)
scripts/the_archive_denominator_triple_counts_harvest_copies_2026-10-14.py  (new, --help free, J3 side-finding)
bench/cdsfl_registry/composer.py                 (J1: records the transport cap's loss; rendered unchanged)
bench/reference_runner_v3.py                     (J1: the dispatch site reads it and logs it)
bench/tests/test_the_transport_cap_names_what_it_dropped_2026-10-14.py      (new, 4 red unpatched -> 7 green)
bench/tests/test_which_core_directive_sections_reach_a_seat_2026-10-14.py   (new, 6 green, two-sided pin)
docs/MATHEMATICAL_APPENDIX.md §7.8               (J2: provenance of the TPR/FPR table + 3 derived consequences)
PAPER.md:1166                                    (J2: "empirical" -> "ASSUMED", corrected in place)
docs/experimental_notes/CDSFL_Complete_Mathematical_Framework_Technical_2026-03-27.md:148,154  (J2: same)
experimental_notes/Falsifier_Supply_Feedback_SPEC_2026-10-14.md             (new, J3 build spec)
```

**99 tests pass** across the 9 affected suites (the 3 blind-round guards, the ablation switch, the C0001 inversion guard, the alarm-kind equivalence, `target_kind_and_no_score`, and both new files). Nothing disabled, nothing removed, **no assertion weakened** — the one metric I corrected was my own, in place, and the correction made the figure smaller. All fixes are **suggested**; nothing is applied to any live configuration, and the three decisions that are his — restating the archive denominator, what text every seat must receive, and authorising the attempt record — are named as his rather than taken.

<!-- verbatim-end -->

## Seat: fable — Fable 5.1

`ok=True`, 19,898 characters, 60 tool calls, 980.1 s, route `claude_cli`, model `fable`.

<!-- verbatim-begin: fable (panel joint_his_rulings_2026-10-13) -->

All evidence is executed. Here is my joint-round return.

---

# JOINT ROUND — SEAT fable RETURN, 2026-10-14

Tooling: SymPy, z3, mpmath, NumPy, statsmodels, SciPy primary throughout; Wolfram Language (local Wolfram Engine via `wolframscript`, exit 0, `Out` present, no `Name::tag`) ran once as second falsifier on J2. All new scripts answer `--help` with a usage line. 96 tests pass across the 12 affected suites with my patch live.

---

## J1 — attack the composition

**item:** J1
**verdict:** CONFIRMED — there is an interaction none of the four fixes' tests covered: **retired pruner × the global phenotype length cap** (`compose()`, bench/cdsfl_registry/composer.py, the block commented "Apply global phenotype length cap", keyed on `PhenotypeTransform.max_directive_chars`).

**evidence (executed):** With `coherence_pruning=False` (the retired default) the composition is longer, and the cap truncates the **final render**, after packet assembly. On the real compose path, deepseek_v3 (cap 4000), situation packet attached:

```
deepseek_v3  software     False  final=4035  cap=4000  domain_text=1490/3049  situation_text=1/282  manifest=['universal','domain','situation']
deepseek_v3  mathematics  False  final=4035  cap=4000  domain_text=1490/2748  situation_text=1/282  manifest=['universal','domain','situation']
```

The domain directive is delivered at 48.9%/54.2%; the **situation packet — the per-dispatch review target, code extracts and adversarial brief — is delivered at 1 of 282 chars**, while `manifest["packets"]` lists all three at full length and `pruned_soft=[]`. The round's verification instrument cannot see this: the 0-of-50 figure in `test_falsifier_C0001_prune_inversion_2026-09-10.py` counts `"domain" not in {p.layer for p in c.packets}` — **packet membership, the layer above the cap** (verified at lines 209/250 of that file). The retirement producer's Property 3 asserts the cap is "a DIFFERENT mechanism on a DIFFERENT file" — false as stated: the C0040 *reduced rendering* is file-specific, but the line-1439 cap runs over the whole composed render.

**Scope, stated precisely:** this does **not** overturn the retirement. With pruning ON the same deepseek rows lose domain AND situation **entirely** (packet deleted); partial-by-cap dominates absent-by-pruner on every row, and the other 4 models deliver FULL text with pruning off. What it breaks is the founder's own ground for the ruling — knowability: the provenance record misstates what deepseek_v3 was fed.

**tools:** the live `compose()` re-executed over 5 models × 2 domains × 2 flag states (20 rows); binary-search prefix survival as an independent check against the end-marker test — both agree on which rows are cut. (This item is mechanism demonstration, not arithmetic; the two-tool rule is carried by producer + committed test re-executing the same path independently.)

**interval:** pruning-OFF rows where the cap cut delivered text: 2/10 = 20.0000%, Wilson [5.6682%, 50.9838%], Clopper-Pearson [2.5211%, 55.6095%] (both deepseek rows). Their packet-level 0/50 is consistent and reproduced: Wilson upper bound 7.1348%.

**falsifier:** `bench/tests/test_the_manifest_records_the_length_cap_cut_2026-10-14.py`. RED on the tree as delivered by the round: `FAILED ...::test_a_capped_composition_says_so` ("manifest carries no `length_cap` record"). GREEN after the fix: `4 passed`. The fourth test asserts the repair changed **no delivered byte** (cap slice + marker byte-identical), so replay comparability is asserted, not assumed.

**refutation:** What I tried that found nothing: (1) runner/composer flag default disagreement — `coherence_pruning=False`, `RunnerConfig.composer_coherence_pruning=False`, mirror `{"on": False}`, pass-through at :11296 all agree; (2) severity shadow × queue membership on one registry — `severity_spec_shadow()` mutates no entry and `_irreducible_queue_split` returns identically before/after (`identical: True`, `mutated: False`, executed above); (3) all 12 affected suites run together with every fix live: 96 passed.

**fix:** `bench/cdsfl_registry/composer.py` — `compose()` now stamps `manifest["length_cap"] = {fired, cap, chars_cut, packets_cut:[{layer, name, chars_delivered, chars_total}]}` with exact per-packet survival from the render offsets. Manifest-only; delivered text byte-identical (test-asserted). Producer: `scripts/the_cap_cuts_what_the_manifest_claims_2026-10-14.py` (now reports 20/20 rows truthful). Anything larger — reordering packets so the situation survives, or raising deepseek's cap — changes every deepseek prompt and belongs behind the same ablation gate as the pruner.

**disagreement:** cc2's committed producer (`the_hand_trim_closes_neither_C0040_nor_C0001_2026-10-13.py`) and the retirement producer both frame the cap as being on "a different file". That is right for the C0040 reduced rendering and the uncapped operational append, wrong for the render-wide cap — and my own blind reply carried the same conflation. Corrected here with the executed demonstration, against both seats' blind framing.

**termination:** HARD assumptions tested (flag consistency, registry non-mutation, render-layer survival, byte-identity of the repair); second pass over the composed suites produced no new above-threshold finding.

---

## J2 — Approach B: measured or assumed?

**item:** J2
**verdict:** CONFIRMED-ASSUMED — the table rates rest on **no measurement**, and the consequence is sharper than "relocates the vote": it relocates it in exactly the conflict cells and genuinely removes it in unanimous cells.

**evidence (executed):**
1. **Provenance.** Earliest occurrence: `docs/experimental_notes/CDSFL_Complete_Mathematical_Framework_Technical_2026-03-27.md:154-157`, "Empirical weights: SymPy (TPR=0.99, FPR=0.001)…" — dated **before any archived experiment**, no producer, no dataset, no interval. The appendix's "Table corrected during 5-model meta-test, 27 March 2026" fixed the weight **arithmetic** (ln(FNR/TPR)→ln(FNR/TNR)), not a rate. The project's own record then falsified the only candidate proxy: `experimental_notes/Stage6_Full_Confer_Synthesis_2026-04-14.md` — "FPR = P(PASS | H0 true) requires ground-truth labels… cannot be used for production calibration", Claim 7 "FALSIFIED by definition", 5/5 models; ground-truth labelling filed "Phase 7+". A repo-wide scan for a script computing verifier TPR/FPR from ground truth returns **NONE** (producer section 4).
2. **Derived consequence.** Weights recomputed from stated rates match the published table (SymPy == mpmath to 1e-12, all six weights). **Unanimous cells are rate-invariant:** S_v > 0.5 ⟺ Π(TPR_i/FPR_i) > 1; z3: "every ratio > 1 AND product ≤ 1" → **unsat**; SymPy log-combination agrees. **Conflict cells are decided by the assumed numbers:** SymPy-falsified + others-verified gives S_v = 0.2720 (REJECT) under the table, S_v = 0.6534 (ACCEPT) under SymPy TPR 0.95/FPR 0.01 — equally defensible absent a measurement. Same tool outputs, opposite verdicts.

**tools:** SymPy (exact rationals) and mpmath agree on all weights and both S_v values to 1e-9; z3 on the invariance; **Wolfram Language (local Wolfram Engine)**: `{0.2720427, 0.6534422, 6.897705, −4.604170}`, exit 0 — third source, agrees.

**interval:** not a sampled proportion — the claims are identities and record facts. The one countable: scripts measuring verifier rates from ground truth, 0 found (exhaustive scan of `scripts/` and `bench/` top level, printed by the producer).

**falsifier:** `scripts/approach_b_rates_are_assumed_2026-10-14.py` — asserts the weight reproduction, the z3 unsat, and `table < 0.5 < alt`; any committed measurement producing those rates, or any rate set under which the conflict cell cannot flip, turns its verdict. (Documentation fix, so the falsifier is the producer's assertions, not a pytest file; it exits non-zero on any failed assertion.)

**refutation:** I searched for a later measurement that would overturn "assumed": every TPR/FPR hit in `experimental_notes/`, `docs/`, `scripts/` traced to the 2026-03-27 assertion, the rung-promotion gate (different quantity), or the similarity benchmarking (different instrument). The Exp 48 forensics corpus contains planted-defect ground truth that *could* produce the measurement — its existence is why the fix below is a precondition, not a dead end.

**fix:** `docs/MATHEMATICAL_APPENDIX.md` — (a) a sourced caution block after the §7.8 table stating the rates are ASSUMED, the flip demonstration, and the promotion precondition: measure per-tool TPR/FPR against the archive's 1,246 CONFIRMED / 40 REFUTED runner-re-verified verdicts plus the planted-defect exams; (b) the §7.10 status row for Multi-verifier corrected from "Ready for implementation" to implementation-gated-on-measurement — the same false-status failure mode that concealed the §7.7 gap for months, closed before it repeats.

**disagreement — and this settles the open seat disagreement:** Both blind seats (cc2: "contains no model-asserted number and is the form that earns the phrase"; me: "the appendix's, verified there") treated Approach B as the ready replacement. **Both were wrong, mine included.** The corrected position: Approach B dominates model-asserted confidence in unanimous cells (tool-owned direction, provably rate-invariant) and is an author's vote in conflict cells until the rates are measured. On the original dispute — collect the two §7.7 inputs or not — the measurement dissolves it: neither the collected-informative route (mine) nor the don't-collect route (cc2's) may promote to a gate through §7.8 as it stands; the promotion path for both runs through the rate measurement.

**termination:** the provenance chain is exhausted (origin, correction note, Stage-6 falsification, repo scan); two independent derivation routes plus Wolfram agree; nothing further is decidable without running the rate measurement itself, which is an experiment the founder commissions.

---

## J3 — the never-routed class and his ruling

**item:** J3
**verdict:** CONFIRMED — his claim holds on the evidence standard, and more strongly than he stated it.

**evidence (executed):** `scripts/the_untoolable_were_never_attempted_2026-10-14.py` over all 3,298 archived registry entries (reproduces the brief's population exactly: 1,938/3,298 = 58.7629%, Wilson [57.0736%, 60.4318%]):

| bucket | k/n | Wilson 95% |
|---|---|---|
| NEVER ATTEMPTED (no code, no verdict, no routing) | 1,884/1,938 = 97.2136% | [96.3823%, 97.8582%] |
| ATTEMPTED, CODE LOST (verdict ERROR, no code) | 13/1,938 = 0.6708% | [0.3924%, 1.1443%] |
| DECLARED UNTOOLABLE | 41/1,938 = 2.1156% | [1.5633%, 2.8573%] |
| …of which the ladder was never consulted | 30/41 = 73.1707% | [58.0665%, 84.3050%] |
| **PROVED IRREDUCIBLE (ladder exhausted, no source)** | **0/1,938** | **[0%, 0.1978%]** |
| flaw_class demonstrably toolable elsewhere | 1,938/1,938 | [99.8022%, 100%] |

**Zero entries carry positive evidence of irreducibility**, every flaw class in the population has an executed falsifier somewhere in the archive, and 97.2% were simply never attempted. Also surfaced: **541 entries hold status CONFIRMED with no executed falsifier, 530 of them with no recorded adjudicator** — confirmation without a tool, which the feedback mechanism below re-enters rather than grandfathers.

**tools:** statsmodels Wilson and scipy Clopper-Pearson on every proportion (both printed, agree to <0.1pp); population reproduction cross-checked against the brief's own figure and the field-combination table (1884+13+41 = 1938, exact).

**interval:** all above; headline answer to his question: genuinely irreducible = **0 of 1,938, 95% upper bound 0.1978% (Wilson), 0.1902% (Clopper-Pearson)**; never attempted = 97.2136% [96.3823%, 97.8582%].

**falsifier:** the producer exits non-zero on assertion failure and is overturned by a single archived entry with `rungs_tried == rungs_available` and no source — none exists. For the build itself the spec names its committed tests (§5 of the spec).

**refutation:** I tried to find entries that would prove irreducibility: every UNTOOLABLE either never consulted the ladder (30) or stopped at rung 1 of several (11, matching the `arm4_untoolable_anatomy_2026-09-22.py` finding that the ladder "stops short of what it has"). I also checked whether "never attempted" could be an artefact of terminal status — 612 of the 1,884 are terminal by other adjudication, which the feedback population therefore **excludes**; the live actionable population remains >1,200.

**fix:** `experimental_notes/Falsifier_Debt_Feedback_Spec_2026-10-14.md` — build-precise and riding the existing mechanics he cited (`bench/dm/_feedback.py`, operational §17): one new record kind `FALSIFIER_DEBT`; emission predicate (LIVE statuses ∪ tool-less CONFIRMED; no code; no executed verdict; not already in the ladder); the §17-precedent imperative wording; the UNTOOLABLE acceptance rule (retires debt only when `rungs_tried == rungs_available` — measured basis 30/41 empty ladders); priority slot below refutations/admissibility; existing `top_k` cap; default-off flag in `universal.toml` wired through `build_feedback_records` with the four committed tests named. **Gates untouched — discharge is recorded only when a tool-executed verdict lands; convergence authority stays with the harness.**

**disagreement:** none with cc2 on substance (cc2's blind Item 2 did not reach this question). One with my own blind reply: I called empty-ladder deferrals "structurally unresolvable in-run." True in-run, but J3 shows in-run unresolvability was doing almost none of the work — 97.2% were never attempted at all, and the cross-round feedback channel is where they resolve. The report-side bundle I built stays correct; it is the smaller half of the answer.

**termination:** HARD assumptions tested (population reproduced exactly; every bucket a field predicate, no judgement calls); the spec is bounded by his ruling and awaits his commissioning.

---

## J4 — the directive that never arrives

**item:** J4
**verdict:** PARTIAL on the premise, CONFIRMED on the substance — and it changes **interpretations I shipped, not verdicts**.

**evidence (executed):** `scripts/what_the_minimal_rendering_delivers_2026-10-14.py`, executing the live `_load_universal_directive` for all 5 models: source 27,803 chars, 15 sections, 'falsifier' ×25 (+1 operational), 'worked proof' ×0 in either file. Delivered to **every** model: **2,503 chars, 0/15 headings, 'falsifier' ×0** — because `cdsfl_core_formal.md` exceeds even the largest cap (12,000), `_render_universal_minimal` is unconditionally what ships. All 15 sections never arrive, including *Runnable Falsifiers for Critical Findings* and *Falsifier Integrity — Do Not Reach for the Answer*. What does arrive is policy keys (`policy.constraints.falsification_required=true`) with none of the content. Measured corrections to the brief's own figures, stated rather than inherited: delivered is **2,503** not 2,734; 'falsifier' in delivered is **0** not 1; source count 25 not 24. Same conclusion, sharper numbers, producer committed.

**tools:** the live loader executed per model, cross-checked against raw file reads (regex heading extraction + char counts) — two independent routes to the same figures; both agree.

**interval:** headings delivered 0/15, Wilson [0%, 20.3883%]; chars delivered 12,515/139,015 = 9.0026% across the 5 seats, Wilson [8.8533%, 9.1542%]; models receiving any falsifier-integrity content 0/5.

**falsifier:** the producer; it is overturned by any model whose delivered packet contains a source heading or the token 'falsifier'. (I did not patch `_render_universal_minimal` to carry a falsifier-obligation block: that changes every prompt for every seat, which is precisely the replay-invalidating, ablation-gated class of change both seats parked Item-5-style. NO CODE FIX PROPOSED beyond the producer — the delivery repair belongs to the lean-vs-full ablation already gating directive edits, and interim coverage goes through the J3 feedback channel, which is measured to reach every seat.)

**refutation:** I checked whether any dispatch path bypasses the minimal rendering (a model with `format_style="full"` and a cap above the file) — none: largest cap 12,000 < 27,803, so the `use_minimal` disjunction is True for all five.

**Does it change my blind verdicts? Plainly, per item:**
- **Item 1 — verdict stands, one causal claim corrected.** My loophole framing ("a model clears the gate by never attaching a falsifier — rewarding exactly the omission the falsifier gate polices") implied model-side omission. J4 shows the omission is **harness-manufactured**: the obligation never reached any seat. The design conclusion is *strengthened* — gating on V(None) would have punished/released findings over an instruction the models never received — but my refutation line ("V(None) does not correlate with falsifier omission") is now the wrong test; the right confound is delivery, and no archived figure about model falsifier *discipline* (including the 58.7629% itself, and my 831/835 crosser decomposition's interpretation) may be read as a model property until a run with the obligation delivered exists.
- **Items 2, 3, 4 — unchanged.** Registry mechanics, queue membership, and A19 path enumeration are directive-independent code facts.
- **Item 5 — unchanged, and partially pre-reported.** My blind reply already measured the C0040 arithmetic (27,803 vs caps 4,000–12,000, "a 7× cut needed, for all 5 models, always"), so "neither of you reported" is half-true of this seat: I reported the **size** collapse, not the **content** analysis — which sections and which vocabulary die. The content fact is the material addition: the falsification framework's falsifier directives reach no seat, which is the supply-side mechanism behind J3's 97.2% never-attempted and the single strongest argument for his feedback ruling.

**disagreement:** with the joint brief's framing, not with cc2: "neither of you reported" overstates for the size half; and three of the brief's J4 figures do not reproduce (2,734/1/24 vs measured 2,503/0/25). Figures travel with producers; mine is committed.

**termination:** two consecutive passes (loader execution, raw-file cross-check) with no new above-threshold finding; the remaining action — delivering the content — is ablation-gated and his to commission.

---

## PATHS WRITTEN (all in the sandbox tree; nothing auto-applied)

```
scripts/the_cap_cuts_what_the_manifest_claims_2026-10-14.py           (J1 producer, --help free)
bench/tests/test_the_manifest_records_the_length_cap_cut_2026-10-14.py (J1 falsifier: red 1-failed pre-patch, green 4-passed post)
bench/cdsfl_registry/composer.py                                       (J1 fix: manifest["length_cap"]; no delivered byte changed, test-asserted)
scripts/approach_b_rates_are_assumed_2026-10-14.py                     (J2 producer, --help free; SymPy/z3/mpmath + Wolfram)
docs/MATHEMATICAL_APPENDIX.md                                          (J2 fix: §7.8 ASSUMED-rates caution; §7.10 status row corrected)
scripts/the_untoolable_were_never_attempted_2026-10-14.py              (J3 producer, --help free)
experimental_notes/Falsifier_Debt_Feedback_Spec_2026-10-14.md          (J3 fix: build spec on the existing §17 channel, default-off, tests named)
scripts/what_the_minimal_rendering_delivers_2026-10-14.py              (J4 producer, --help free)
```

Nothing removed, no assertion weakened; the one code change is manifest-only and byte-identity-asserted. 96 tests pass across the 12 affected suites with everything live. The three decisions that remain the founder's are named in place: commissioning the verifier-rate measurement (J2), commissioning the falsifier-debt channel (J3), and the ablation that would let the core directive actually reach a seat (J4).

<!-- verbatim-end -->

Written under CDSFL note standard v1.7 (26 August 2026).
