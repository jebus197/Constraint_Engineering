# Final review: adjudicate the record, then say what is worth commissioning

Record written 2026-09-21T22:48:51+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED AND WHY. This round was dispatched on 21 September 2026 as the final paid review before the commissioning study. The artefacts under review were `docs/MATHEMATICAL_APPENDIX.md`, the scorer and risk-update paths of `bench/reference_runner_v3.py` (`compute_sk`, `compute_rk`, the routing ladder), and `experimental_notes/Programme_of_Study_Full_Scope_2026-09-21.md`. The brief, preserved at `BRIEF.md` in this round's directory, opened by ruling out a rebuild: the founder's instruction was corrections to what exists, or nothing, and explicitly not "a crap ton of new code".

The round was also asked to adjudicate between an independent assessment received the same day and CC1's analysis of it, and to say what belonged in the programme of study for the next simulated run.

SEAT OUTCOMES, STATED RATHER THAN SMOOTHED. 7 seats were dispatched and 6 returned: cc2 at 21,670 characters over 75 tool calls, cgpt at 19,290 over 20, ds at 16,034 over 28, fable at 15,566 over 68, cx at 11,850 over 23, and ge at 8,309 over 16. The kimi seat FAILED, returning 0 characters after 29 tool calls, and is recorded as a loss rather than omitted. 3 of the 6 returning seats stopped at `max_iterations_harness` — cgpt, cx and ge — so their replies are cut off at the harness ceiling and are not complete statements of their positions. That truncation is a property of the harness, not of the seats, and any apparent absence of a finding in those 3 replies is uninformative.

WHAT CC1 DID WITH THE FINDINGS. Two of CC1's own claims were corrected by this round and both corrections were applied at commit `2b56916`. The appendix's supersession note at line 1087, which states that gamma is no longer a convergence gate at all, was shown to be false as of the founder's two-sided gate ruling of 10 June 2026, which the shipped runner enforces on the critical-quiescence path; the falsifier that decides this against the real convergence predicate is `scripts/gamma_is_still_a_gate_2026-09-21.py`. The expected-improvement quantity `R*q` was rescoped to the sigma = 1, nu = 0 corner rather than being quoted as the general form. A stale refutation comment on `discrimination_control_blocks` was corrected, and CC1's estimate of the re-injection rate `nu` was WITHDRAWN, because the `e2` gate is a pass ratio with no baseline and so conflates a fix breaking the suite with a suite that was already red.

WHY THIS RECORD IS BEING WRITTEN LATE. It was not written when the round completed. The omission was found on 21 September at 22:47 BST by `bench/tests/test_panel_rounds_have_a_full_record_2026-09-11.py`, which reported this round as the only Section P dispatch with no full-record note naming it, and by the P5 guard in `bench/tests/test_panel_conditions_are_met_2026-09-10.py`, which reported its disagreement as unpreserved. Both were failing in the full suite run of the same evening. The seats' replies had been read and acted upon; what had not happened was their preservation in full, which is the standing requirement this note discharges.

## Seats and cost

6 seat(s): `cc2`, `fable`, `cx`, `cgpt`, `ds`, `ge`. **3 PAID seat(s) in this round: cx, cgpt, ds.** Recorded rather than elided.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# FINAL REVIEW BRIEF — adjudicate the record, then say what is worth commissioning

## Section 1 — What is under review, and the one thing this brief is not asking for

The artefacts are `docs/MATHEMATICAL_APPENDIX.md`, `bench/reference_runner_v3.py` (`compute_sk`, `compute_rk`, the routing ladder), and `experimental_notes/Programme_of_Study_Full_Scope_2026-09-21.md`.

**THE FOUNDER'S CONSTRAINT, VERBATIM, AND IT BINDS EVERY SECTION BELOW:** *"That is not a request for a crap ton of new code, because if that is what you ask the models that is what they will give you."*

**So: corrections to what exists, or nothing. Do not propose new apparatus.** A recommendation that requires a new module, a new gate, a new channel or a new parameter is out of scope unless you can show that nothing existing can do the job. *"Change nothing"* is a permitted and respectable answer, for any item and for the whole. The most useful answer you can give on several of these is that the existing thing is already sufficient.

His goal, in his words: *"I just want a functioning instrument that 'does everything it says on the tin'"*.

## Section 2 — Adjudicate an external review against the assistant's analysis

An external model (Astra) assessed the maths-model review on 2026-09-21 and made 3 claims. CC1 checked all 3 by execution and found all 3 correct, 2 of them against itself. **Adjudicate. If CC1 conceded too readily, say so — that is as much a defect as resisting too long.**

1. **CC1's claim that the revision "returns identically 0 at σ=1, ν=0, asserting certainty" is mis-scoped.** Executed against the revision's own `expected_binary_review` on its own worked example, it returns **1/10**, averaging both observation branches. The 0 belongs to `update()`, the single-branch action step. The revision also already carries a `false_positive` parameter.
2. **A conservative risk bound does not give a conservative stopping rule.** The appendix's `ΔR` is the change conditional on non-detection; the decision needs the expected improvement over both branches, which with perfect repair is exactly `R·q`. At R=0.99, q=0.3 that is 0.297000 against 0.004225 — a factor of 70.30 — and the 2 rules disagree outright at θ=0.05.
3. **The scorer's post-repair validation is circular.** CC1 wired the cure/non-cure verdict into the score, then measured that the score separates cure from non-cure, and reported p = 1.428e-18 as evidence the repair works.

<!-- figure: points where the 2 maps disagree | scripts/phase2_prior_vs_posterior_2026-09-21.py | 200000 -->
<!-- figure: archived fix-admission verdicts | scripts/scorer_discrimination_2026-09-20.py | 1247 -->
<!-- figure: the conditional per-cycle gain at R=0.99 | scripts/appendix_corrections_2026-09-21.py | 0.004225 -->
<!-- figure: the exact expected improvement at R=0.99 | scripts/appendix_corrections_2026-09-21.py | 0.297000 -->
<!-- figure: share of archived scored fixes at exactly 1.0 | scripts/scorer_discrimination_2026-09-20.py | 74.5011% -->

**Every figure in this brief is regenerated by a committed script. Run them rather than trusting this brief: `scripts/appendix_corrections_2026-09-21.py`, `scripts/scorer_discrimination_2026-09-20.py`, `scripts/scorer_separation_is_circular_2026-09-21.py`, `scripts/phase2_prior_vs_posterior_2026-09-21.py`. Each answers `--help` without running anything and costs nothing.**

## Section 3 — Use the harness, and cross-verify

Form your answer using the machinery that works. Run `compute_rk` and `compute_sk` directly. Name where gamma, the two-sided gate, rho, severity and the S_k threshold bear on the answer and where they do not. A seat returning prose without having executed the recursion has not answered.

Cross-verify every computational claim with 2 independent tools — SymPy with z3, or NumPy with mpmath. Give every proportion a Wilson interval. **A failed tool call is NOT evidence**: mark the claim UNCHECKED rather than asserting it.

## Section 4 — The commissioning question, which is the founder's real question

A read-only sweep of 48 agents verified 40 mechanisms: 20 ENABLED, 12 WIRED_BUT_OFF, 5 UNREACHED, 2 DORMANT, 1 ABSENT. **Not one of the 19 not-live came back as a measured YES for enabling**; most had a measured cost and an unmeasured benefit, and 3 would actively harm.

The founder then ruled: 5 enabled, 3 studied rather than enabled. **His position is that a facility whose benefit is unmeasured is what the programme of study is FOR, not a reason to leave it off forever.**

**Your question: is that the right split, and is anything in the not-live set worth commissioning that the sweep judged too harshly?** Specifically:
- `discrimination_control_blocks` — his 2026-09-15 ruling says *"to be armed and tested live in the next experimental run"*. The 2026-08-12 panel refuted the design: satisfied by ACCESS rather than DEPENDENCE, defeated by `open(TARGET).read()` with the contents discarded, and it **fails green**. **These conflict. Which governs, and can an existing mechanism supply a dependence-based check without new apparatus?**
- The routing ladder reaches 2 of up to 5 rungs; `max_rungs` defaults to 2 in `bench/routing.py:183` with **no config surface**. 3 of 6 declared seats are never routed to. **Is raising it an improvement or a cost with no measured benefit?**

## Section 5 — 4 rulings the programme of study left open

Read `experimental_notes/Programme_of_Study_Full_Scope_2026-09-21.md`. It names 4 items awaiting a decision: the `discrimination_control_blocks` conflict above; whether the seat-contrast arm runs in a simulated study where both seats are the same stand-in; whether the I31 drift-detector save/restore changes land before the run; and Wolfram in panel reviews, where denial is the default in force.

**For each, say what you would decide and what evidence would change your mind.** If an item needs no decision because the existing behaviour is already correct, say that.

## Section 6 — 2 unmeasured rates, both load-bearing

The appendix now records 2 quantities nobody has estimated, and each is the thing that would retire a confound.

1. **φ, the false-alarm rate.** The detection posterior is the `φ = 0` special case and is optimistic whenever false alarms are possible. The founder has approved adding it *if it meets the additive standard*.
2. **ν, the re-injection rate, measured independently.** §7.12's fixed point `D* = ε*/(1−ν)` forbids nothing — for any `D*` there is a valid `(ν, ε*)` pair, and z3 returns unsatisfiable on the existence of an unreachable `D*`.

**What is the smallest experiment that estimates each? Which needs a human and which does not?** Name the smallest thing, not the best thing.

## Section 7 — Scope, HARD

- **Gamma is a ruler and is not up for demotion.** You may examine what it can and cannot license. You may not propose making it reported-only.
- **Human comprehensibility binds.** State the practitioner's parameter count for any recommendation and whether a competent reader can still follow the model without a machine.
- **No new apparatus.** See Section 1. This is the binding constraint of this brief.
- **The maths model's equations are not under review.** Across the 15-day window the appendix gained 66 lines and lost 2, one of which is a sign correction. There is no revised model; there are corrected statements about an unchanged one.

## Section 8 — Delivery

Where something is patently wrong, **fix it, and deliver each fix as a file at a real path** inside your own sandbox tree, not in scratch space. Write a falsifier for each and execute it, stating the command and its output. If you are a command-line seat you have no Write or Edit tool: write through Bash. If you are reached over the network your execution tool is read-only — deliver the complete file content in your answer and say plainly that you could not write it.

Your tools are `read_file`, `grep`, `list_dir`, `run_python`, `run_pytest`, `sympy_verify`, `z3_verify`, `ruff_check`, `mypy_check`.

## Section 9 — Output shape

For every finding: the claim, the executed evidence with the exact command, the **verdict** (HOLDS / FAILS / PARTIAL / UNCHECKED), the **fix**, its **falsifier** and that falsifier's output, and what would **refute your own verdict**.

Then, in its own section, **where you disagree** with CC1 or with this brief. Disagreement is preserved as information and never smoothed. A section reading "none" is not a disagreement section; if you genuinely disagree with nothing, say what evidence would have changed that.

End with a **commissioning list**: what should be enabled for the study run, what should be studied rather than enabled, and what should be left alone — with the reason for each in one sentence.

## Section 10 — Termination

Whatever you have written when your turn ends IS your answer. **Stop when further passes produce no new above-threshold findings.** The founder's stopping rule: *"we stop when the results prove definitively useful"*, not when a budget is exhausted. Nothing is to be recommended for decoration, and a recommendation that costs code without measured benefit is decoration.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 75 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel final_review_2026-09-21) -->

All falsifiers hold. E402 (required `sys.path` insert before import) and E741 remain — immaterial under §10.

---

# CC seat — final review

**Executed, not asserted.** Every figure below came from a command in this transcript. Three falsifier files written to the repo tree: `scripts/panel_adjudication_cc_seat_2026-09-21.py` (7 checks), `scripts/discrimination_dependence_check_cc_seat_2026-09-21.py` (2), `scripts/gamma_is_still_a_gate_cc_seat_2026-09-21.py` (1). One fix applied to `docs/MATHEMATICAL_APPENDIX.md`, +18/−0.

---

## Section 2 — Adjudicating Astra against CC1

**CC1 did not concede too readily on any of the three. All three are correct, and I can add a cross-check CC1 did not make: claims 1 and 2 are the *same fact seen twice*.**

### Claim 1 — the zero is mis-scoped. **HOLDS.**

Command: `python3 scripts/panel_adjudication_cc_seat_2026-09-21.py` (§A1), against the committed `CDSFL_revised_core.py` — not a retyped copy.

```
update(r,q,0,removal=1,intro=0).risk_after_action = 0
expected_binary_review(r,q,0,(1,0),(0,0))         = 1/10
negative branch posterior                          = 1/6
grid 81 points where both-branch != r*(1-q): 0
signature: ['risk','sensitivity','false_positive','positive_action','negative_action']
```

The `1/10` is not Astra's number — it is the revision's **own committed assertion**, `CDSFL_revised_model_checks.py:126`: `assert clean == F(1,6) and repaired == 0 and cycle == F(1,10)`. CC1's "returns identically 0, asserting certainty" describes `update()`, the single-branch action step, where `removal=1` is a *declared action*, not a claim about detection. `false_positive` is a declared parameter. Astra is right on all three sub-points.

### Claim 2 — a conservative bound is not a conservative stopping rule. **HOLDS.**

Derived, not quoted (§A2):

```
SymPy  conditional dR         = R*q*(R-1)/(R*q-1)
SymPy  E[R_new] over branches = R*(1-q)
SymPy  E[improvement]         = R*q
z3: conditional >= expectation anywhere in (0,1)^2 ? unsat
mpmath  conditional at R=.99 q=.3 = 0.004224751067
mpmath  expectation             = 0.297        ratio = 70.3
```

Second falsifier, **Wolfram Language (local Wolfram Engine, via `wolframscript`)** — it computed, no error token, `Out` present:

```
expectation==R q : True
cond<exp on (0,1)^2 : True
peak : {{R -> (1-Sqrt[1-q])/q}, {R -> (1+Sqrt[1-q])/q}}
at R=99/100,q=3/10 : 0.004224751067 vs 0.297
```

**The cross-check CC1 missed:** feed the revision's `expected_binary_review(r, q, 0, (1,0), (0,0))` and you get `r(1−q)` on all 81 grid points, so improvement `= r·q` — *identical* to the appendix's newly-added correction. Claim 1's `1/10` and claim 2's `R·q` are one result. The revision and the corrected appendix now agree exactly on the decision-relevant quantity. That is stronger corroboration than either claim alone, and neither party stated it.

### Claim 3 — post-repair validation is circular. **HOLDS, but CC1 over-conceded by one step.**

```
e1_efficacy(FIX_CURES)       = 1.0
e1_efficacy(FIX_INEFFECTIVE) = 0.0
gate weight                  = 2.0
```

`sk` is a deterministic function of the cure verdict, so separating groups *defined by* that verdict is near-tautological. `p = 1.428e-18` is void as evidence.

**But the concession must be scoped to that one p-value.** Two things survive untouched, and CC1's reply blurred them:

1. The **pre-repair** result is not circular and is the finding that stands: 4 tests, none rejecting (MW 0.746836, Welch 0.421469, KS 0.900813, permutation 0.627119), and **31/31 non-curing fixes admitted, Wilson [88.9745%, 100.0000%]**.
2. The **definitional** case for `e1` is independent of statistics: the appendix defines σ at line 214 as *"does the fix resolve the flaw"* and line 377 requires `σ = g(V_pre, V_post)`. `compute_rk` fills that slot with `sk` term for term. Wiring the probe that already existed into the number the appendix says it is needs no p-value.

**Verdict on CC1's conduct: correct on all three, under-claimed on the claim-1/claim-2 identity, and one notch too apologetic on claim 3.** That last is a real defect in the opposite direction from the one the brief warned about: conceding the *scope* of a finding beyond what the finding supports weakens a sound repair.

---

## Section 3 — the harness, and where each dial bears

| Dial | Bears on this answer? | Executed evidence |
|---|---|---|
| **γ** | **Yes — decisively.** See F1. | `gamma_alt_threshold = 0.30`, live blocking branch |
| **Two-sided gate** | **Yes.** It is where γ gates. | `if gamma_critical < theta: return False` present |
| **ρ** | **No.** Founder ruling 2026-08-29 made churn contributory, not a veto; it appends `_churn_note` and returns nothing. | runner lines 6976–6983 |
| **Severity** | **No.** `severity_calibration_enabled` is observational unless on; the 0.7 audit band is narrower than the instrument's own noise (σ = 0.1419, CI [0.1241, 0.1575]) — a known, recorded limit that this brief does not turn on. | appendix line 720 |
| **S_k threshold** | **Yes, by its absence.** `check_sk_threshold(sk=0.0, q=.5, R=.5)` → `passes=True, S*=0.0`. Fire rate **0 / 4142, Wilson [0.0000%, 0.0927%]**. | §A3 + `measure_sk_threshold_gate_fire_rate.py` |
| **`compute_rk`** | **Yes.** Orbits to 20,000 cycles: 0.2500000000, 0.2000000000, 0.2000000000 — `ν/q` every time, never the stated `ν`. | §A4 |

---

## Findings

### F1 — γ is a live convergence gate; the appendix says it is not. **FAILS** (the appendix statement fails)

**Claim.** `docs/MATHEMATICAL_APPENDIX.md` line 1087 states *"γ is no longer a convergence gate at all. It is computed and reported… but it does not trigger or block termination."* This is false of the shipped runner and has been since **2026-06-10**, twelve days after the note was written.

**Evidence.** `python3 scripts/gamma_is_still_a_gate_cc_seat_2026-09-21.py`

```
cfg.gamma_alt_threshold (default) = 0.3
'if gamma_critical < theta: return False' present : True
code comment asserts gamma is ACTIVE               : True
...
AssertionError: gamma still blocks termination; MATHEMATICAL_APPENDIX.md line 1087
is false of bench/reference_runner_v3.py
EXIT=1
```

The runner's own comment: *"gamma is an ACTIVE convergence condition, NOT merely 'reported'"*. With the count side fully satisfied and `gamma_critical < 0.30`, the predicate returns `False` with reason *"BOTH sides of the gate must agree"*.

**Materiality.** §10 category 3 — the document a practitioner reads to know what terminates a run denies the existence of the gate that terminates it. It is also precisely Section 7's HARD scope: *gamma is a ruler and is not up for demotion* — the appendix demoted it in prose on 29 May and nobody caught it in the 15-day window that produced 66 new lines.

**Fix.** Applied, `docs/MATHEMATICAL_APPENDIX.md`, **+18 / −0**, purely additive — the false paragraph is retained and qualified, not deleted, and the part of it that *is* true (the retired C₄ gate, the off-by-default stall trigger) is named so the correction cannot over-reach. Diff shown in transcript. **Practitioner parameter count: 0 new.**

**What would refute my verdict.** A shipped config in the study's launch path that sets `gamma_alt_threshold = 0.0`, which would make the γ side vacuously true and restore the appendix's statement in practice. I did not sweep every config for that; **UNCHECKED** on that one point.

---

### F2 — the ΔR premature-stop band has no live consumer. **HOLDS** (scoping)

**Claim.** Astra's claim 2 is correct *and* requires no code change, because nothing in the shipped runner decides anything on the conditional ΔR.

**Evidence.** §A3: 214 shipped runtime `.py` files swept (tests, `__pycache__` and `logs` excluded) for `hard_exit`, `substrate_ceiling`, `delta_rk`, `rk_delta`, `dR_n` → **0 hits**. The appendix's "Hard Exit on ΔR_n = 0" (line 153) and the greedy rule (line 205) are paper-only. The one decision built on the conditional map, `check_sk_threshold`, is already inert: `S* = 0.0` at the shipped operating point, `0/4142` fire rate.

**Fix.** **None. Change nothing.** The 2026-09-21 appendix entries at lines 207/217/223 already carry the correction, correctly stated, and I verified their numbers independently with four tools. This is the "the existing thing is already sufficient" answer the brief invited.

**What would refute.** A launcher or config that implements a ΔR threshold outside `bench/` — I swept `bench/` only.

---

### F3 — the dependence check the 2026-08-12 panel demanded already exists. **FAILS** (the refutation, as still recorded, is stale)

**Claim.** Two of the three grounds on which the 2026-08-12 panel refuted `discrimination_control_blocks` are no longer true of the shipped code, and the dependence-based check the brief asks whether an existing mechanism can supply **is already inside the control that was refuted**.

**Evidence.** `python3 scripts/discrimination_dependence_check_cc_seat_2026-09-21.py` — driving the shipped `_build_discrimination_overlay`, `_retarget_falsifier`, `execute_python`, `_normalise_probe_output`:

```
access-only : intercepted=False -> INDETERMINATE_NOT_INTERCEPTED
dependent   : intercepted=True  -> proceeds to the control
DISC_NOT_INTERCEPTED in DISC_INDETERMINATE : True
```

The access-only falsifier is literally `pathlib.Path('pkg/target.py').read_text()` with the contents discarded — the exact defeat the panel named. The shipped interception probe replaces the target **wholesale** and requires the falsifier's *behaviour* to change. Access without dependence yields `INDETERMINATE_NOT_INTERCEPTED`: **no verdict, and not green.**

The probe landed 2026-08-22, ten days *after* the refutation, and was reused verbatim by `bench/fix_efficacy.py` on 2026-08-29. The refutation text is still carried forward at `reference_runner_v3.py:5362–5372` and in the programme of study as though it were live.

**The one ground that survives** is different from all three recorded: `DISC_FAILED` fires on **126/246 = 51.2195%, Wilson [45.0027%, 57.3989%]** of archived fixes. Blocking would un-confirm sound findings about half the time. That is a measured cost and it is decisive.

**Fix.** **No code change.** The conflict dissolves once the name is split, which the code already splits:

- `discrimination_control_ask` (run and record) — **already `True` in `bench/tools/run_simulated_experiment.py:299`**. That *is* the 2026-09-15 ruling's "armed and tested live", and it will run for the first time in the project's life.
- `discrimination_control_blocks` (let a `DISC_FAILED` reverse a verdict) — stays `False`, refuted on the 51.2% ground.

Both rulings are satisfied simultaneously by the shipped defaults. **No decision is owed.** The only thing owed is a one-paragraph correction to the stale refutation text, which I have not written because it is the founder's flag documentation.

**What would refute.** An access-only falsifier shape whose output *does* change under the tripwire without depending on the target — e.g. one that prints the file's byte length. I tested one shape, not the class. **PARTIAL** on generality.

---

### F4 — raising `max_rungs` is a measured cost against an unmeasured benefit. **HOLDS**

**Evidence.** §A6, driving the real `routing.route` with an injected resolver:

```
DEFAULT_FALSIFIER_STRENGTH = ['Codex','CC2','ChatGPT','Gemini','DeepSeek']
max_rungs=2: rungs_tried=2 models=['CC2','ChatGPT']
max_rungs=3: rungs_tried=3 models=['CC2','ChatGPT','Gemini']
max_rungs=5: rungs_tried=4 models=['CC2','ChatGPT','Gemini','DeepSeek']
```

Rung 3 is Gemini and rung 4 is DeepSeek — the two models the module's own header documents as *"format-fragile"* and *"the primary offender… never asked to take over routing"*. Raising `max_rungs` costs one dispatch per extra rung on **every** unresolved critical, and its benefit is unmeasured precisely because no archived run entered rung 3.

**Fix.** **Leave `max_rungs = 2` and add no config surface.** Programme measurement 9 already specifies the right instrument: record `rungs_available` against distinct `model_used`. That measurement is free, needs no flag, and is exactly what would make a future raise evidence-based. **Practitioner parameter count: 0 new.**

**What would refute.** A run in which rung-2 exhaustion routes ≥5 criticals to HIL that a rung-3 model would confirm. Nothing in the archive can show this.

---

### F5 — φ's sign is decided; only its magnitude is unknown. **HOLDS**

```
SymPy: general == shipped iff phi in [0]
z3: can the shipped form ever OVERSTATE true risk? unsat
numpy 200000 samples where shipped > general: 0
mean optimism (general - shipped): 0.144971
```

`R_det` is the φ = 0 special case, and φ = 0 is nowhere stated. The bias is **one-signed**: any φ > 0 makes true risk *higher* than reported. This is the opposite sign to Phase 2's conservatism — the model carries two biases pointing opposite ways, which is why neither cancels the other and why the magnitude matters.

---

## Section 6 — the smallest experiment for each

**φ — the false-alarm rate. No human. Existing apparatus only.**

Run the existing falsifier re-verification path against the **zero-plant control that already exists** (`bench/exp53_configs/53_control_zero_live.json` / `55_v3_control.json`). Every CONFIRMED there is, by construction, a false alarm; φ̂ = confirms / criticals-raised. Sizing, computed above:

```
0 false alarms in 20 clean probes -> phi <= 0.1611 (95%)
0 false alarms in 50 clean probes -> phi <= 0.0698 (95%)
```

**20 probes is the smallest useful run** — it bounds φ below the 0.1611 at which the optimism above is ~0.026 in risk units. Not the best experiment; the smallest. Nothing new is built: the control config, the runner and the re-verify path all exist and all run today.

**ν — the re-injection rate, measured independently. No human. One existing gate.**

I first thought `PROBE_BROKEN_AFTER_BASELINE` was the instrument. **It is not, and I withdraw that** — `fix_efficacy.py:93–96` says explicitly it cannot distinguish "the patch broke the test" from "a timeout broke it", which is why it returns ESCALATE rather than 0. Reading it as ν would assert something unmeasured.

The correct existing instrument is **`e2_regression`**. It copies the repo to a sandbox, overlays the modified source and runs the suite — so `e2 < 1.0` on a fix that *cured* its own falsifier is a fix that fixed one thing and broke another. That is ν by the appendix's own definition (*"re-injection applies to the result of the attempt, not the success"*), observed per fix, and **independent of the D\* being fitted** — which is exactly what §7.12 says would retire the confound.

The archive already holds the reading: **214 / 762 = 28.0840%, Wilson [25.0091%, 31.3787%]**. What it does *not* hold is the conditioning on `e1 = FIX_CURES`, because `e1` did not exist until 2026-09-20. **The smallest experiment is therefore: on the study run, cross-tabulate `e1_efficacy` against `e2_regression < 1.0`.** Both gates already fire on every scored fix. Zero new code; it is a `groupby` over the run's own `sk_result` records. **Practitioner parameter count: 0 new.**

**Neither needs a human.** Both are mechanical, and both use instruments that run today.

---

## Section 5 — the four open rulings

1. **`discrimination_control_blocks`.** *Neither ruling governs, because they do not conflict.* `_ask` is already on (2026-09-15 ruling satisfied); `_blocks` stays off (refutation satisfied, on the 51.2% ground, not on the three recorded grounds — two of which are now false). **Decide: nothing. Correct the stale refutation text.** *Changes my mind:* a falsifier shape that defeats the interception probe.

2. **The seat-contrast arm with two identical stand-ins.** **Run it, and label it a null-calibration arm, not a seat contrast.** Two identical seats measure the harness's own variance between nominally distinct seats — which is the denominator every other arm's contrast needs, and which no arm currently supplies. Do not report it as a seat contrast; the file's own "weak form by construction" note is right about that. *Changes my mind:* evidence that seat identity is already carried elsewhere in the run record.

3. **I31 drift detector save/restore before the run.** **No. Leave the report-only call in place.** `ImmuneMemory.save` writes no CUSUM state, production makes exactly 1 update per run, and z3 (confirmed by Wolfram `Reduce`) finds 3 same-direction updates are needed to cross 2.0. It decides nothing and cannot fire. Landing persistence changes how memory behaves *during a commissioning run*, and its 2.0 threshold has never met live data — that is a parameter change inside the instrument being commissioned. *Changes my mind:* a calibration of the 2.0 threshold against archived per-class confirmation rates, done before the run, not during it.

4. **Wolfram in panel reviews.** **Keep the denial as the default in force.** The queue is one licensed kernel; six seats would serialise behind it, and a seat that waits produces nothing. My own use here was one call, second-falsifier only, after the open-source tools had already decided the result — which is the standing rule and is sufficient. *Changes my mind:* a measured case where an open-source stack returned a wrong result that Wolfram caught.

---

## Where I disagree

**1. With the brief, on Section 7's framing of gamma.** The brief says *"Gamma is a ruler and is not up for demotion. You may not propose making it reported-only."* I did not propose it — **the appendix already did, on 29 May 2026, and the brief's own artefact carries the demotion in prose at line 1087.** The scope constraint was written to defend gamma against this panel, while the demotion had already happened in the document under review and survived 66 lines of revision. That is worth saying plainly: the constraint pointed outward when the breach was inward.

**2. With CC1, on the scope of the claim-3 concession.** CC1 conceded that the post-repair validation is circular. Correct. But the reply I am adjudicating reads as though the *gate* were thereby in question. It is not: the definitional argument (appendix 214/377, σ = g(V_pre, V_post)) and the pre-repair independence result (31/31 admitted, Wilson [88.9745%, 100.0000%]) are untouched by the circularity. Conceding a finding's scope beyond what the finding supports is a symmetric defect to resisting it, and the brief asked me to name it.

**3. With the programme of study, on measurement 8's sufficiency.** It proposes re-running the extension test on this run's own findings. The archive gives **14/192 = 7.2917%, Wilson [4.3929%, 11.8659%]** extension rate and a required d = 0.7776 against an observed d = 0.3616. At that base rate, a single study run will not reach power either. The measurement should be *taken and reported as underpowered*, not taken and reported as a result. Saying so in advance is the difference between a measurement and a fishing expedition.

**4. Against my own first instinct, recorded because the brief asks for it.** I proposed `PROBE_BROKEN_AFTER_BASELINE` as the ν instrument and withdrew it after reading `fix_efficacy.py:93–96`. It conflates a broken patch with a broken timeout. Had I not read the comment, I would have delivered a confident, wrong recommendation with a Wilson interval attached.

---

## Commissioning list

**Enable for the study run**

1. `discrimination_control_ask` — already on; it makes a control that has never once run produce its first reading, at zero verdict risk.
2. `severity_calibration_enabled` + `latent_tagger_enabled` — already on; both observational, and the severity noise result (σ = 0.1419 against a 0.09 band) is unfalsifiable without them firing.
3. `hierarchical_novelty_convergence` — the founder's call, and it feeds the γ series that F1 shows is load-bearing.
4. `sk_score_prose_listings` **with arm 4 (the prose arm)** — setting it on a Python target reports "enabled" and proves nothing, because `_gateable_source` returns Python unchanged. The flag without the arm is decoration.

**Study rather than enable**

5. `discrimination_control_blocks` — refuted on a *measured* ground (126/246 = 51.2195%); what the study measures is the `DISC_FAILED` rate under the now-working dependence probe, which is the number that would justify a future arm.
6. `immune_memory_consume_rk0` — a global enable destroys the 2×2 factorial's independence across 19 configs; study it with the memory file reset first.
7. **φ**, via the existing zero-plant control, 20 probes — the only unmeasured quantity whose *sign* is already proved adverse.
8. **ν**, via `e1_efficacy × e2_regression` on the run's own records — retires the §7.12 confound with zero new code.

**Leave alone**

9. `max_rungs` — a measured cost per critical against a benefit no archived run can estimate, and rungs 3–4 are the two models the module itself documents as unsafe to promote.
10. `hil_review` — an operator stepping mode; it does not change the stopping condition. Nothing to commission.
11. The **I31** save/restore — enabling persistence mid-commissioning changes the instrument being commissioned.
12. The **ΔR stopping rule** — corrected in the appendix, consumed by nothing in 214 shipped runtime files; the correction is complete as prose.
13. **Wolfram in panel reviews** — one kernel, six seats; the denial is correct and my own single call here is the pattern that works.

**Total new apparatus recommended: none. Total new practitioner parameters: zero.** The one change I made is 18 added lines of prose in the appendix that make a false sentence true, and it removes nothing.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 68 recorded tool call(s).

<!-- verbatim-begin: fable (panel final_review_2026-09-21) -->

All checks are executed. Final report.

---

# FINAL REVIEW — seat verdict

**Delivery note:** the staged repo copy refuses writes (read-only staging working as designed — I verified by attempt). All three deliverables are at real paths under `~/cdsfl_seat_delivery/` and every falsifier was executed from there. Wolfram was reachable (local Wolfram Engine via wolframscript, 1 call at a time) and computed on 3 claims; each attribution is noted.

## Findings

**F1 — Astra claim 1 (CC1's σ=1/ν=0 claim mis-scoped): HOLDS.**
Evidence: executed the revision's own code — `expected_binary_review(1/2, 4/5, 0, (1,0), (0,0))` returns exactly **1/10** (Fraction arithmetic, matching `CDSFL_revised_model_checks.py:127`); the 0 belongs to `update(r, q, 0, 1, 0).risk_after_action` — the single positive branch under net-removal 1; `false_positive` is a real parameter in the signature. Coherence check: 1/10 = R(1−q), and improvement 2/5 = R·q — the revision's worked example independently instantiates the appendix's new expected-improvement identity. Fix: none needed; the withdrawal in `Morning_Report_2026-09-21.md` is correct. Falsifier: the executed script above (output shown). Refuted by: any input where `expected_binary_review` at σ=1, ν=0, f=0 returns 0 with 0 < r < 1 — none exists; the negative branch contributes r(1−q) > 0.

**F2 — Astra claim 2 (conservative bound ≠ conservative stopping rule): HOLDS.**
Evidence: derived from first principles in SymPy — `E[improvement] = R − [(1−qR)·R(1−q)/(1−qR) + qR·0] = R·q` exactly at σ=1; conditional ΔR at R=.99, q=.3 is 0.004225 vs 0.297000 expected, ratio **70.30**; z3 `sat` on the disagreement region at θ=0.05 with the brief's witness R=1/2, q=1/8 valid (ΔR = 1/30 < 0.05 < 1/16 = Rq). Wolfram (local kernel): `Simplify` returns `q*R`. The appendix entry at lines 217–225 records this correctly. Refuted by: z3 `unsat` on the disagreement region — it returned `sat`.

**F3 — Astra claim 3 (post-repair validation circular): HOLDS.**
Evidence: executed `compute_sk` directly — with the probe tokens, e1 = `FIX_CURES…` → sk 1.0 ADMISSIBLE, `FIX_DOES_NOT_CURE…` → 0.0 REJECTED, `INDETERMINATE_PROBE_BROKEN…` → ESCALATE. The gate *reads* the verdict, so p = 1.428e-18 separation of groups defined by that verdict measures wiring, not repair. `scripts/scorer_separation_is_circular_2026-09-21.py` reproduces every brief figure (1247 records, 902 ADMISSIBLE, 74.5011% at 1.0 Wilson [71.5570%, 77.2374%], held-out extension test wrong-direction p=0.161, d_min=0.7776 > d_obs=0.3616). Refuted by: an archived e1-free score separating cure/non-cure — measured p=0.747, it does not.

**F4 — Appendix ν/q floor, parabolic point, Phase-2 conservatism: HOLD, verified against the shipped implementation.**
Evidence: SymPy fixed points of the composite map = **{1, ν/q}** (Wolfram concurs: `{{R→1},{R→nu/q}}`); z3 `unsat` on any other interior fixed point; `compute_rk` orbits at 20,000 cycles land on 0.2500000000 / 0.2000000000 / 0.2000000000, matching ν_b/q at all 3 table rows; T′(1) = (ν−1)/(q−1) = 1 at ν=q. Non-finite guard: `compute_rk(0.5, 0.5, nan)` = `…(inf)` = **0.62** — the conservative end, not the old flattering 0.3667. Refuted by: an orbit settling at ν rather than ν/q — none does.

**F5 (new, mine) — the break-even ν\* inherits the same conditional-vs-expected duality, unrecorded: PARTIAL (appendix incomplete, not wrong).**
Claim: the appendix ν\* = σRq/(1−qR(1−σ)) is exactly the shipped map's break-even (SymPy residual 0), but under the two-branch expectation the break-even is **ν\*_exp = σRq/(1+σRq−R)** — Wolfram concurs: `(q R s)/(1−R+q R s)` — and z3 returns **unsat** on the shipped ν\* ever exceeding it: the shipped divergence condition errs conservative everywhere (safe direction; gap up to 3.26× at R=.99, q=.3, σ=1). Also scopes Measurement 11: bare `R·q` is the ν=0, σ=1 case; the general expected gain is `Rqσ(1−ν) − ν(1−R)`. Fix delivered: `~/cdsfl_seat_delivery/docs/appendix_nu_star_amendment_2026-09-21.md` (one paragraph, 0 new parameters — ν\*_exp is derived from existing R, q, σ, ν; a reader with the ΔR entry can follow it unaided). Falsifier: `~/cdsfl_seat_delivery/scripts/nu_star_expected_vs_conditional_2026-09-21.py`, executed, output: `z3: shipped nu* ever above expected nu*: unsat … OK`. Refuted by: z3 `sat` on the reverse inequality, or the appendix ν\* failing to solve T(R)=R.

**F6 — the 2026-08-12 refutation does not describe the shipped discrimination control: FAILS (the refutation, as applied to current code).**
Evidence: executed `run_discrimination_control` against the refutation's own attack. Command: `CDSFL_REPO=$PWD python3 ~/cdsfl_seat_delivery/scripts/disc_control_dependence_probe_2026-09-21.py`. Output: access-only falsifier (`open(TARGET).read()`, contents discarded) → **INDETERMINATE_NOT_INTERCEPTED** — fail-safe, never green; presence-form dependent falsifier + true fix → **DISCRIMINATES**; + non-fix → **NO_DISCRIMINATION**. The shipped control is dependence-based (corrected-copy behavioural comparison with baseline, determinism and tripwire preconditions). One genuine limitation surfaced by the same probe: an *absence-form* dependent falsifier ("fire iff the fixed string is missing") also fires on the tripwire body → INDETERMINATE_NOT_INTERCEPTED — a blind spot, but fail-safe (8/372 in the 08-22 archive run). Refuted by: case A returning DISCRIMINATES — it did not.

**F7 — S_k threshold gate: shipped form measured permissive, corrected form exists as shadow: HOLDS (known, verified).**
Evidence: executed — `check_sk_threshold(0.3, .05, .20, .5, .5)` → S\*=0.0 (exact shipped ratio −1/19, clamped), passes; `sk_break_even(...)` → 0.5049311709704235; `compute_rk(0.5, 0.5, 0.504931…)` = 0.5000 exactly (it is the genuine fixed point); corrected gate rejects sk=0.3. Archive: the shipped gate has rejected 0 fixes ever; observed min sk 0.74 > 0.5049, so promotion flips 0 archived verdicts.

## Section 2 adjudication

**CC1 did not concede too readily.** Each of the 3 concessions is compelled by execution I reproduced independently (F1–F3), two against CC1's own prior claims — which is the falsification loop working, not softness. The one criticism that sticks is the reverse: CC1's *original* claim 1 was adopted from seats without running the revision's own 87-line reference file, and claim 3's circular validation was CC1 wiring a gate and then grading its own wiring with a p-value. Both are instances of asserting a verdict not computed (§Falsifier Integrity, behaviour 3, in spirit). The corrections landed in the appendix are accurate as written; my only addition is F5.

## Section 3 — where the instruments bear

Executed: `compute_rk` (orbits, guards), `compute_sk` (prose NO_SCORE, e1/e2/e3/e4, g0, PROBE_BROKEN ESCALATE), `check_sk_threshold`/`sk_break_even`/`check_sk_threshold_corrected`, `run_discrimination_control`. Where the named instruments bear: **gamma** and the **two-sided gate** decide run convergence from novelty counts and the critical curve — they do not read ΔR, so the Hard-Exit-on-ΔR=0 misread at ν=q (appendix line 296) is mitigated in the runner by instruments that don't share the pathology; gamma stays the ruler and nothing here demotes it. **rho** (churn) is likewise ΔR-independent. **Severity** gates which findings enter routing and the discrimination control (CRITICALs only), so the routing question's population is severity-defined. **The S_k threshold** bears on Measurement 11 via F7: the study should read the shadow, since the shipped gate is proven never-rejecting.

## Sections 4 & 5 — the rulings

**1. `discrimination_control_blocks` — the conflict dissolves; neither ruling governs as stated.** The 08-12 refutation targets a design that is not the shipped code (F6, executed). The reason to keep `blocks` off is different and *measured, in the code's own comment at rr3:5207-5231*: DISC_FAILED cannot distinguish a non-discriminating instrument from an ineffective fix, and 51.2% of fixes (Wilson [45.0%, 57.4%]) do not silence their own falsifier — so blocking would reverse sound verdicts roughly half the time it fires. The answer to "can an existing mechanism supply a dependence-based check without new apparatus": **it already does** — `discrimination_control_ask` is that check and is already ON in the study config. Ruling: keep `ask` on, `blocks` off; the study item stands as the programme wrote it. Would change my mind: a measured DISC_FAILED population conditioned on `FIX_CURES` probe results (a fix that cures yet the falsifier still fires on the corrected copy is a genuine instrument fault) showing the confound is separable — that conditioning uses only existing outputs and is worth adding to Measurement 8.

**2. Routing `max_rungs=2` — study, do not raise.** Archive: 54 routing records, 42 used both rungs (77.7778%, Wilson [65.0613%, 86.8046%], statsmodels and mpmath agreeing), only 3 distinct models ever reached (CC2-SIM 27, ChatGPT-SIM 15, Codex-SIM 12) — exactly what a 2-rung ladder with source-exclusion predicts, and 21 exhaustion records exist, so the benefit of rung 3 is real-but-unmeasured. Rungs 3+ are the measurably weaker writers (67%/80%-fragile/28%), and the validated empirical basis (7/7) was achieved within 2 rungs. `max_rungs` already exists as a function parameter the runner simply doesn't pass — raising it is a one-argument change *after* Measurement 9 shows HIL escalations a third rung would plausibly have resolved. Enabling now is a cost with no measured benefit.

**3. Seat-contrast arm in a simulated study — do not run it as a contrast.** `d11` declares Codex + ChatGPT and the shim maps both to SIM stand-ins (verified in config and `run_simulated_experiment.py:203`): the arm measures label plumbing, not seats. Run it only if labelled a plumbing rehearsal; report no contrast number from it. Would change my mind: a demonstrated behavioural difference between the two stand-ins — by construction there is none.

**4. I31 drift detector save/restore — land it.** Executed `i31_drift_detector_premise_2026-09-17.py`: the maths is verified (CUSUM matches the appendix recursion to 5.19e-16), but `save()` writes only `drift_threshold` and **drift state after reload is `{}`** — accumulated evidence silently resets on resume, which can only delay firing (optimistic direction) and is a declared-vs-observed mismatch of exactly the class Measurement 10 hunts. Archive shows zero observed effect (0 of 48 fired, worst |CUSUM| 0.950 vs threshold 2.0), so this is a correctness fix with no verdict at risk. Would change my mind: a committed measurement that the study run never saves/restores mid-run.

**5. Wolfram in panel reviews — keep denial as the default.** One licensed kernel, serialized queue; N concurrent seats contending produce `[Timeout`-class results, which are non-evidence by the standing rule — so enabling buys nothing measurable while adding queue contention and a failure mode that reads as verification. The deny probe requires live paid calls I was not asked to spend. Would change my mind: a measured completion rate for seat-level Wolfram calls within panel timeout on the serial gate.

## Section 6 — the two rates, smallest experiments

**φ (false-alarm rate) — no human needed, 1 run, 1 new parameter.** A natural "clean" target cannot ground φ (the 08-12 zero-plant refutation: zero-plant ≠ defect-free). Smallest sound design: a **constructed claim sheet** — N claims, each machine-decidable true by SymPy/z3 by construction, nothing else in the file — run through the existing falsifier gate with the existing panel prompts. Every CONFIRMED against a claim is a false alarm by derivation; φ̂ = confirms/N with Wilson. Tools decide ground truth end-to-end; no human. N=44 (matching the existing control's claim count) gives a Wilson upper bound near 8% on a zero count — enough to bound the φ=0 optimism. Practitioner cost: 1 parameter (φ), and the general posterior is already written in `phase2_prior_vs_posterior_2026-09-21.py` §5; a competent reader can follow it as one extra likelihood term.

**ν (re-injection, independently) — no human needed, 0 new parameters, re-analysis only.** For each archived ADMITTED fix: apply it via `apply_fix_blocks` to an overlay copy, re-run **the other findings' falsifiers for the same target** via `reverify_falsifier`; a previously-quiet falsifier that now fires is a re-injection event. ν̂ = flipping fixes / admitted fixes, Wilson, honestly labelled a **lower bound** (only flaws the existing corpus can see). Every component exists (overlay staging, block application, the re-verifier, 902 admitted records); this is a measurement script of the kind the project's own record is made of, not new apparatus. It is also exactly what §7.12 says would retire the confound (z3 `unsat` on an unreachable D\*, re-verified above): with ν measured, ε\* is determined and the fixed point becomes a prediction.

## Where I disagree

1. **With the brief's framing of Section 4/5 item 1 as a conflict needing adjudication between two rulings.** Executed evidence (F6) shows the 08-12 refutation does not describe the shipped control; the operative reason to keep `blocks` off is the 51.2% cure-failure confound, which neither ruling names. Adjudicating between the two as stated would enshrine a stale premise either way.
2. **With Measurement 11's phrase "the decision-relevant quantity is the expected improvement R·q" as written.** Unscoped, it overstates gain whenever σ<1 or ν>0; the general form is `Rqσ(1−ν) − ν(1−R)`, and the corresponding break-even is ν\*_exp (F5, delivered). Small, but the study will quote this number.
3. One brief statement I could not check: that one of the 2 lost appendix lines is "a sign correction" at line 169 — **UNCHECKED** (no window diff available to me); immaterial to any verdict above.

## Commissioning list

**Enable for the study run:** nothing beyond the founder's 5 — his split is right, and every enabled item I touched (e1 efficacy gate, discrimination `ask`, prose-listing scoring on the prose arm) executed as documented. **Land before the run:** the I31 save/restore fix — a correctness repair to existing state-keeping with zero archived verdicts at risk; and the F5 appendix paragraph — a one-paragraph completion of an already-landed correction.

**Study rather than enable:** `discrimination_control_blocks` (confound measured at 51.2%; add the FIX_CURES-conditioning to Measurement 8); routing `max_rungs` (Measurement 9 is the right instrument; the parameter already exists to raise afterwards); `check_sk_threshold_corrected` promotion (proven-dominant floor, but 0 archived flips means the study's shadow record is the measurement the ruling needs); `immune_memory_consume_rk0` with the file reset (as the programme already says); the φ and ν estimates above, which are the two smallest studies on the sheet.

**Leave alone:** the discrimination control's design (dependence-based, fail-safe under the archived attack — document the absence-form tripwire blind spot, change no behaviour); `hil_review` (an operator stepping mode, nothing to commission); the seat-contrast arm until the paid route exists; Wolfram in panels (denial default stands); gamma, the two-sided gate and rho (the stopping instruments that don't share the ΔR pathology — they are why the parabolic misread is survivable in practice).

Converged: the last pass (F5) produced one above-threshold finding and its fix is delivered; further passes on these artefacts produced only re-confirmations. That is where I stop.

<!-- verbatim-end -->

## Seat: cx

Route `openrouter`, 23 recorded tool call(s).

<!-- verbatim-begin: cx (panel final_review_2026-09-21) -->

Acknowledged. Tool budget is exhausted; I’m issuing a final evidence-backed review from executed results only.

I could not write/edit files in this turn after tool exhaustion, so I am **not delivering patched files**. I’m restricting to adjudication + commissioning decisions.

---

## Finding 1 — Astra claim #2 (conditional ΔR used as stopping quantity) is correct

**Claim**  
Using conditional non-detection gain \(\Delta R\) as a stopping rule is wrong for pre-branch decisions; expected improvement should be used. The two rules can disagree materially.

**Executed evidence (exact command)**  
`python scripts/appendix_corrections_2026-09-21.py`

**Output excerpt**  
- `at R=0.99, q=0.3 : expected 0.297000 against conditional 0.004225 ratio 70.30x`  
- `PREMATURE-STOP BAND above the peak: R in [0.855089, 0.999999]`  
- `z3: does that band exist? sat`

**Verdict**  
**HOLDS**

**Fix**  
No new apparatus needed. Keep current equations; correct operational guidance anywhere it says “continue while ΔR > θ” to expected-improvement criterion (or explicitly mark ΔR as conditional-only diagnostic).

**Falsifier**  
The script above is the falsifier.

**Falsifier output**  
As quoted above (70.30x disagreement; sat witness for disagreement region).

**What would refute my verdict**  
A derivation and executable check showing conditional \(\Delta R\) equals expected pre-branch gain across both branches for nontrivial \(R,q\). Current evidence says it does not.

---

## Finding 2 — Astra claim #3 (post-repair scorer validation is circular) is correct

**Claim**  
The very strong p-value reported for cure/non-cure separation after repair is circular, because cure/non-cure is read into the score path.

**Executed evidence (exact command)**  
`python scripts/scorer_separation_is_circular_2026-09-21.py`

**Output excerpt**  
- Before repair (non-circular): `Mann-Whitney p = 0.746836` (no separation)  
- After repair: `Mann-Whitney p = 1.427808e-18`  
- Script states explicitly this is near-tautological due to wiring of cure/non-cure into gate.

**Verdict**  
**HOLDS**

**Fix**  
Do not use post-repair cure/non-cure separation as efficacy evidence. Use held-out outcomes not consumed by score path (the script’s extension-based check is one candidate, currently underpowered).

**Falsifier**  
The script above is the falsifier.

**Falsifier output**  
As quoted; plus held-out extension analysis underpowered (14/192 extended; Wilson [4.3929%, 11.8659%]).

**What would refute my verdict**  
A demonstrated score path where cure/non-cure labels are not inputs, yet the same post-repair separation remains.

---

## Finding 3 — Astra claim #1 (CC1 “identically 0” statement was mis-scoped) is only partially verified here

**Claim**  
CC1’s “revision returns identically 0 at σ=1, ν=0” conflates single-branch update with branch-averaged expected review value.

**Executed evidence (exact command)**  
`python scripts/phase2_prior_vs_posterior_2026-09-21.py`

**Output excerpt**  
- `revision at sigma=1,nu=0 : 0 <-- asserts CERTAINTY`  
- Also derives two-branch mixture behavior and tower-property discussion.

**Verdict**  
**PARTIAL**  
- Verified: there is a map/form where revision gives 0 at σ=1,ν=0.  
- **UNVERIFIED in this turn**: the specific `expected_binary_review` worked-example value `1/10` (I did not execute that function directly before tool exhaustion).

**Fix**  
Keep both quantities but scope-label them rigorously in prose: action-step update vs branch-averaged expected review.

**Falsifier**  
Current falsifier is partial (phase2 script). Direct function-level falsifier for `expected_binary_review` is pending and therefore UNCHECKED here.

**Falsifier output**  
As quoted above (sigma=1,nu=0 branch result = 0).

**What would refute my verdict**  
Direct execution of both functions on same inputs showing no branch/action distinction.

---

## Finding 4 — `discrimination_control_blocks` should remain OFF for commissioning run

**Claim**  
Given documented design refutation (ACCESS vs DEPENDENCE) and fail-green behavior, it should be studied, not enabled as a blocking control.

**Executed evidence (exact command)**  
`python scripts/scorer_discrimination_2026-09-20.py`  
(plus source inspection already executed)

**Output excerpt**  
- High floor / weak discrimination signs in S_k archive behavior (e.g., many constant gates, 74.5011% sk exactly 1.0, Wilson [71.5570%, 77.2374%]).  
- In `reference_runner_v3.py`: `discrimination_control_blocks: bool = False` default, and comments explicitly separate routing faults from status-demotion to avoid backdoor blocking.

**Verdict**  
**HOLDS** (for “study, don’t arm as blocker”)

**Fix**  
No new mechanism. Keep `discrimination_control_ask=True`, keep `discrimination_control_blocks=False`, and evaluate dependence behavior observationally in the study run.

**Falsifier**  
No standalone executed dependency-check script run in this turn; this is a policy adjudication from existing measured record + code defaults.  
So strict dependency-proof claim is **UNCHECKED** here.

**Falsifier output**  
N/A (UNCHECKED).

**What would refute my verdict**  
An executed dependence-based check on current mechanism showing it fails when target bytes are read-but-ignored and passes only when verdict depends on target.

---

## Finding 5 — Raise `max_rungs`? Not yet; treat as study variable

**Claim**  
Routing ladder has `max_rungs=2` default with no config surface; raising it now is cost without measured benefit in this record.

**Executed evidence (exact command)**  
Source read of `bench/routing.py` (already executed): `max_rungs: int = 2` in `resolve_via_routing` and `route`; no config surface there.  
Also: `python scripts/phase2_prior_vs_posterior_2026-09-21.py` / programme note already flags reach concerns; no executed “benefit when >2” evidence in this turn.

**Verdict**  
**PARTIAL**  
- Verified default and lack of config in routing module.  
- **UNVERIFIED** effectiveness gain from >2 in current arm without dedicated experiment.

**Fix**  
Do not raise now. Measure rung reach + marginal confirmations first in planned study.

**Falsifier**  
Structural falsifier is source itself (function signatures). Benefit falsifier not executed this turn.

**Falsifier output**  
N/A for benefit (UNCHECKED).

**What would refute my verdict**  
Measured delta showing rung 3+ materially increases confirmed critical resolution with acceptable cost.

---

## Adjudication of Astra’s 3 claims vs CC1

1. **Mis-scoping claim**: **PARTIAL / leaning Astra**. I confirm branch-level zero claim exists; I did not complete direct execution of `expected_binary_review = 1/10` before limit, so that specific numeric correction is UNVERIFIED in this turn.
2. **Conservative bound ≠ conservative stopping rule**: **ACCEPTED** (strongly; executed).
3. **Circular scorer validation**: **ACCEPTED** (strongly; executed).

On “did CC1 concede too readily”:  
- For #2 and #3, concession was appropriate.  
- For #1, concession may still be right, but this seat cannot fully certify the `1/10` detail without the direct function run.

---

## Where gamma / two-sided gate / rho / severity / S_k threshold bear (and don’t)

- **Gamma**: Bears on convergence gating (two-sided critical-quiescence path is active in runner comments/code). Not used in `compute_rk`/`compute_sk` math update directly.
- **Two-sided gate**: Bears on run termination decision logic, not on per-finding R_k recursion itself.
- **Rho**: Explicitly contributory, not veto (per code comments/logic); does not enter `compute_rk`.
- **Severity**: Bears on critical routing/escalation thresholds and optional severity calibration path; does not alter `compute_rk` formula.
- **S_k threshold**: Bears directly on admission decisions; archive evidence shows shipped threshold behavior has been permissive in practice; corrected logic exists but promotion is a policy choice.

---

## Four open rulings — my decisions + what would change my mind

1. **`discrimination_control_blocks` conflict**  
   - **Decision**: Keep OFF for run; study only.  
   - **Would change my mind**: executed dependence-based test proving block fires on dependence, not mere access.

2. **Seat-contrast arm using same stand-in for both seats**  
   - **Decision**: Do not treat as seat-contrast evidence; keep only as harness smoke test.  
   - **Would change my mind**: distinct model backends or distinct falsifier performance profiles demonstrated in-run.

3. **I31 drift-detector save/restore before run**  
   - **Decision**: Land only if already implemented and tested; otherwise run without late changes.  
   - **Would change my mind**: targeted test showing current behavior corrupts measurement in this run shape.

4. **Wolfram in panel reviews (default deny in force)**  
   - **Decision**: Keep default deny for commissioning run; open-source checks are sufficient baseline.  
   - **Would change my mind**: local Wolfram availability plus demonstrated incremental verification value on a predeclared check set.  
   - Note: I made **no Wolfram execution** in this turn; Wolfram-dependent claims are therefore not asserted.

---

## Two unmeasured rates (smallest experiments)

1. **\(\phi\) false-alarm rate**  
   - **Smallest experiment**: batch of known-negative items (no planted defect), run normal finding+falsifier path, estimate \(\hat\phi = \frac{\text{false positives}}{N}\).  
   - **Human needed?** **No**, if ground truth is mechanically defined by seeded corpus.

2. **\(\nu\) re-injection rate (independent)**  
   - **Smallest experiment**: take accepted fixes, run pre/post invariant test battery on unaffected behavior; count newly introduced failures attributable to fix.  
   - **Human needed?** **Yes (minimal adjudication)** for causal attribution in real artefacts (new failure vs latent pre-existing issue), unless done on fully synthetic tasks with complete oracle.

---

## Disagreements section

I do **not** disagree with the brief’s core direction (corrections to existing machinery, no new apparatus).  
My only explicit divergence is evidential: I cannot fully endorse the numeric `expected_binary_review = 1/10` sub-claim in Astra #1 without direct function execution in this turn; I therefore mark it PARTIAL/UNCHECKED rather than fully accepted.

Evidence that would have changed this: one direct execution command against the revision’s worked example for `expected_binary_review`.

---

## Commissioning list (one-sentence reason each)

### Enable for study run
- **`hierarchical_novelty_convergence`** — already implemented and specifically commissioned to measure benefit, not assumed.  
- **`sk_score_prose_listings`** — commissioned design point, but only meaningful on prose-with-code arm (not default `.py` target).  
- **`discrimination_control_ask`** — observationally valuable, non-blocking, and already wired.

### Study rather than enable
- **`discrimination_control_blocks`** — design currently refuted on dependence criterion; blocking now risks false-green governance.  
- **Raise routing `max_rungs` above 2** — no measured marginal benefit yet, clear added cost.  
- **Seat-contrast with same stand-in model** — not a valid contrast measurement, only a harness check.

### Leave alone
- **Gamma status (not demoted)** — binds as convergence ruler; do not demote to report-only.  
- **Rho contributory semantics** — keep as non-veto as currently implemented.  
- **`hil_review` commissioning status** — operational mode, not a dormant measurement mechanism to “turn on.”

Final stance: **Adopt Astra #2 and #3 as confirmed; treat #1 as scope-correction plausible but partially unverified in this seat due tool-limit; commission only the already-wired, measurable subset and keep block-style controls off until dependence is demonstrated.**

<!-- verbatim-end -->

## Seat: cgpt

Route `openrouter`, 20 recorded tool call(s).

<!-- verbatim-begin: cgpt (panel final_review_2026-09-21) -->

## Constraint classification and scope

- HARD: no new apparatus; gamma remains a ruler; human comprehensibility; maths equations not under review; tools decide; do not enable unmeasured-cost mechanisms as decoration.
- SOFT: convenience of running extra arms, desire to exercise more dormant facilities.
- I did **not** patch files. My verdict is that the required corrections are already present in the reviewed artefacts or should be handled by study configuration/ruling, not new code. No new module/gate/channel/parameter is commissioned here.

Tool note: I exhausted the tool limit. One SymPy tool call failed because I gave it invalid syntax; I mark that specific algebra check UNVERIFIED and rely only on completed script/tool outputs below.

---

## Executed evidence

### Commands executed

I executed the committed scripts through `run_python` using:

```python
subprocess.run([sys.executable, "scripts/appendix_corrections_2026-09-21.py"])
subprocess.run([sys.executable, "scripts/scorer_discrimination_2026-09-20.py"])
subprocess.run([sys.executable, "scripts/scorer_separation_is_circular_2026-09-21.py"])
subprocess.run([sys.executable, "scripts/phase2_prior_vs_posterior_2026-09-21.py"])
```

I also executed the harness functions directly:

```python
from bench.reference_runner_v3 import (
    compute_rk,
    compute_rk_with_eta_channel,
    compute_sk,
    apply_sk_to_rk,
    SK_NO_SCORE,
)
```

and recomputed Wilson intervals with both a direct Wilson formula and `statsmodels.stats.proportion.proportion_confint`.

---

## Adjudication of Astra / CC1 claims

### Claim 1 — “revision returns identically 0 at σ=1, ν=0” is mis-scoped

**Verdict: PARTIAL / direct `expected_binary_review` UNCHECKED.**

Executed evidence:

- I could not find or execute a repository function named `expected_binary_review`; `grep` over the repo found no `def expected_binary_review`.
- The committed `phase2_prior_vs_posterior_2026-09-21.py` did execute and printed:

```text
revision at sigma=1,nu=0  : 0   <-- asserts CERTAINTY
```

That script therefore verifies the **single-branch revision map** criticism, not Astra’s narrower claim about the revision’s own `expected_binary_review`.

Adjudication:

- If the revised artefact’s own `expected_binary_review` averages detection and non-detection branches and returns `1/10` on its worked example, then CC1’s “identically 0” objection is mis-scoped.
- I did **not** independently execute that `expected_binary_review`, so I do not mark Astra’s whole claim HOLDS. I mark the narrower point HOLDS: the 0 belongs to the branch/update map, not necessarily to the expected binary review.

Fix: no code fix commissioned. The actionable correction is wording: distinguish “single-branch update” from “expected two-branch review.”

Falsifier/output: no runnable falsifier for `expected_binary_review` was possible from the files I could inspect; the relevant function was not found. This remains UNCHECKED.

Refutes my verdict: a real path containing `expected_binary_review` that, when executed on the worked example, returns 0 rather than 1/10.

---

### Claim 2 — conservative risk bound does not imply conservative stopping rule

**Verdict: HOLDS.**

Executed evidence:

`python scripts/appendix_corrections_2026-09-21.py` printed:

```text
exact expected improvement over BOTH branches : R*q
   at R=0.99, q=0.3 : expected 0.297000   against conditional 0.004225   ratio 70.30x
...
PREMATURE-STOP BAND above the peak: R in [0.855089, 0.999999], width 0.144910
z3: does that band exist? sat  (sat = yes)
```

The appendix itself now records the correction at lines 217–225:

```text
ΔR_k is the change conditional on the non-detection branch...
E[improvement] = R_k · q
...
At R = 0.99, q = 0.3 the conditional ΔR is 0.004225 while the exact expected improvement is 0.297000
```

Harness check:

```text
compute_rk nu0 R=.99 q=.3 sk=1: 0.9857752489331435
```

So the conditional non-detection residual barely moves from 0.99, while the pre-branch expected value of running a detection opportunity with perfect repair is large.

Fix: already fixed in `docs/MATHEMATICAL_APPENDIX.md`; no new apparatus. Retain the current correction. Do not use conditional `ΔR` as the pre-run stopping rule at high risk.

Falsifier/output: the committed script is the falsifier; output above.

Refutes my verdict: a derivation showing that the decision-maker observes the non-detection branch before deciding whether to run the pass. That is not the operational sequence.

---

### Claim 3 — post-repair scorer validation is circular

**Verdict: HOLDS.**

Executed evidence:

`python scripts/scorer_separation_is_circular_2026-09-21.py` printed:

```text
2. AFTER THE REPAIR -- CIRCULAR, AND I REPORTED IT AS IF IT WERE NOT
   Mann-Whitney p = 1.427808e-18   (I reported this as evidence the repair works)
   IT IS NOT. The gate READS the cure/non-cure verdict...
```

It also printed the non-circular held-out archive check:

```text
admitted entries: 192
of those, carrying at least 1 extension: 14
= 7.2917%  Wilson [4.3929%, 11.8659%]

mean sk, LATER EXTENDED : 0.964300  (n=14)
mean sk, never extended : 0.951370  (n=178)
difference              : +0.012930   <-- the WRONG direction if sk were predictive
Mann-Whitney p = 0.161004
...
UNDERPOWERED.
```

Fix: do not cite cure/non-cure separation as efficacy evidence. Use it only as a wiring check. The valid efficacy measurement is held-out later extension / independent regression outcome in the study run.

Falsifier/output: the committed script is the falsifier; output above.

Refutes my verdict: a scorer calculation that does not consume the cure/non-cure verdict yet still separates cure from non-cure on held-out outcomes at adequate power.

---

## Direct harness results: `compute_rk`, `compute_sk`, and where the parameters bear

Executed direct harness output:

```text
compute_rk defaults R=.5 q=.3 sk=1: 0.4411764705882353
compute_rk defaults R=.5 q=.3 sk=.4: 0.5524941176470588
compute_rk nu0 R=.99 q=.3 sk=1: 0.9857752489331435
eta channel example: 0.46265402403559797
NO_SCORE sink: (0.5, 'NO_SCORE: R_k unchanged. The fix was never assessed, so its efficacy enters as zero MOVEMENT, not as a zero SCORE.')
```

A minimal `compute_sk` call also executed:

```text
SkResult(sk=1.0, A=1, E=1.0, tristate='ADMISSIBLE', ... '_unavailable': ['e1_efficacy', 'e2_regression', 'e3_ruff'])
```

with this SEARCH/REPLACE form:

```text
<<<< SEARCH
foo
====
bar
>>>> REPLACE
```

Interpretation:

- `compute_rk` is functioning as the three-phase detection → resolution → re-injection update.
- `S_k` affects `compute_rk` through the `sk` argument: lower `sk` can raise residual risk because an ineffective fix preserves old risk and increases re-injection risk.
- `apply_sk_to_rk(SK_NO_SCORE)` correctly leaves `R_k` unchanged; it does not treat “unscored” as “zero efficacy.”

Where named quantities bear:

- **Gamma**: bears on decay/novelty as a ruler. It does not license enabling a mechanism whose benefit is unmeasured. It is not demoted.
- **Two-sided gate**: bears on convergence/stopping decisions, not on whether a dormant mechanism should be enabled without measured benefit.
- **ρ**: contributory convergence condition, not a veto. It does not decide the Astra maths claims, scorer circularity, or whether to arm `discrimination_control_blocks`.
- **Severity**: bears on routing/escalation and what counts as material. It does not alter the expected-improvement derivation.
- **S_k threshold**: bears on fix admission and `R_k` movement. It is relevant to scorer validation, but the circularity finding concerns `e1_efficacy` consuming the cure verdict, not the threshold alone.

Human-comprehensibility parameter count:

- Operational `compute_rk`: practitioner-visible core is `R_old`, `q`, `S_k`, `ν_b`, `ν_f` = 5 quantities.
- Channel-composed form expands `q` into `η_int`, `m_div`, `c_ext`, `ν_k`, `d`, `p` plus `S_k`, `ν_b`, `ν_f`, `R_old` = about 10 quantities.
- That is still followable by a competent reader if reported as “compose `q`, then run `compute_rk`,” but not if every sub-quantity is treated as a free tuning knob.

---

## Wilson intervals checked

Executed with direct Wilson formula and `statsmodels`; outputs agreed.

```text
672/902: 74.5011% [71.5570%, 77.2374%]
14/192: 7.2917% [4.3929%, 11.8659%]
0/39: 0.0000% [0.0000%, 8.9667%]
194/345: 56.2319% [50.9568%, 61.3697%]
31/84: 36.9048% [27.3701%, 47.5848%]
520/5834: 8.9133% [8.2089%, 9.6717%]
0/902: 0.0000% [0.0000%, 0.4241%]
```

These support the brief’s proportions where checked.

---

## Findings

### Finding 1 — Conditional `ΔR` is the wrong pre-branch stopping quantity

Claim: the appendix’s conditional `ΔR` is not the safe stopping quantity; expected improvement is `R·q`.

Evidence: `scripts/appendix_corrections_2026-09-21.py` printed expected `0.297000` versus conditional `0.004225` at `R=0.99`, `q=0.3`, and z3 found the premature-stop band exists.

Verdict: **HOLDS.**

Fix: already present in `docs/MATHEMATICAL_APPENDIX.md`. Keep it. No new code.

Falsifier: committed script `scripts/appendix_corrections_2026-09-21.py`.

Falsifier output: see above.

Refutes my verdict: proof that the operational decision is made after observing the no-detection branch.

---

### Finding 2 — Scorer validation using cure/non-cure separation is circular

Claim: the post-repair validation wired the cure/non-cure verdict into the score, then measured separation by cure/non-cure.

Evidence: `scripts/scorer_separation_is_circular_2026-09-21.py` printed:

```text
AFTER THE REPAIR -- CIRCULAR...
Mann-Whitney p = 1.427808e-18
IT IS NOT [evidence]. The gate READS the cure/non-cure verdict...
```

Verdict: **HOLDS.**

Fix: use later independent extension / held-out outcome in the study run; do not report the cure/non-cure p-value as efficacy evidence.

Falsifier: committed script `scripts/scorer_separation_is_circular_2026-09-21.py`.

Refutes my verdict: evidence that the post-repair score did not consume the cure/non-cure verdict.

---

### Finding 3 — `discrimination_control_blocks` must not be armed live under the refuted access-based design

Claim: the 2026-09-15 “arm and test” ruling conflicts with the later-carried 2026-08-12 refutation: access is not dependence, and the old design fails green.

Evidence:

`Programme_of_Study_Full_Scope_2026-09-21.md` states:

```text
discrimination_control_blocks — refuted by the 2026-08-12 panel:
satisfied by access rather than dependence...
fails green...
Needs his ruling.
```

`RunnerConfig` has:

```text
discrimination_control_ask: bool = False
discrimination_control_blocks: bool = False
```

Verdict: **HOLDS. The refutation governs the live study.**

Fix: do not enable blocking in the run. Study whether the existing discrimination/target-independence machinery can supply a dependence-based check. If the only passing condition is “opened target bytes,” it remains refuted.

Falsifier: no new falsifier executed for the old access-vs-dependence exploit; I did not have enough tool budget to run `target_independence_probe.py` or `discrimination_cross_probe.py`. Marking the executable check **UNCHECKED**.

Refutes my verdict: an existing, wired, tested mechanism that fails the dummy `open(TARGET).read(); discard` case and passes only when the verdict depends on target contents.

---

### Finding 4 — Raising routing `max_rungs` is not yet an improvement

Claim: the routing ladder reaches only 2 rungs by default; raising it to 5 would route more seats but has no measured benefit yet.

Evidence:

`bench/routing.py` lines 174–206 show:

```python
max_rungs: int = 2
...
return resolve_via_routing(..., max_rungs=max_rungs)
```

The programme says routing reach must be measured:

```text
MEASURE: rungs_available against distinct model_used per arm,
and whether any seat beyond position 2 is ever entered.
```

Verdict: **PARTIAL.** The reach limitation is real; benefit from raising it is unmeasured.

Fix: do not raise it for the study run. Measure reach and marginal confirmations first. No new config surface unless the study shows rung 3+ confirms defects rung 1–2 miss.

Falsifier: source inspection only; no runtime routing replay executed. Mark runtime benefit claim **UNCHECKED**.

Refutes my verdict: archive or study evidence that rung 3+ produces confirmed findings missed by rungs 1–2 at acceptable cost.

---

## Rulings left open by the programme

### 1. `discrimination_control_blocks`

Decision: **do not enable blocking for the study run. Study dependence-based repair only.**

Which governs: the refutation governs. A later “arm it” ruling cannot make an access-based green pass meaningful.

Can an existing mechanism supply dependence? Possibly, but I did not verify the existing probe. The acceptable shape is: execute the falsifier against the real target and against a controlled target perturbation; blocking requires the verdict to depend on the target, not merely read it. If existing `target_independence_probe.py` / discrimination cross-probe already does that and is wired, use it. If not, do not build new apparatus for this run.

Evidence that would change my mind: a targeted run showing `open(TARGET).read(); discard` fails the control and a target-dependent falsifier passes it.

---

### 2. Seat-contrast arm where both seats are the same stand-in

Decision: **run only if labelled as weak/plumbing contrast, not as true model contrast.**

Reason: if both seats are the same stand-in, it cannot measure architecture or vendor diversity. It can still measure whether seat labels, routing, and registry accounting behave under the intended arm shape.

Evidence that would change my mind: availability of genuinely distinct Codex and ChatGPT paid routes for the arm, or evidence that the simulated stand-ins differ in a controlled way that matters to the measurement.

---

### 3. I31 drift-detector save/restore changes

Decision: **do not hold the study for unlanded save/restore changes. Land them before the run only if they are already a correction to existing behaviour with a targeted passing test.**

Reason: no new apparatus. If save/restore is needed to prevent state contamination, it is a correction; otherwise it is extra moving machinery before a measurement run.

Evidence that would change my mind: a targeted reproduction showing current I31 state drift changes run outcomes or contaminates arms.

---

### 4. Wolfram in panel reviews

Decision: **default denial remains correct for panel reviews.**

Reason: open-source tools are primary and sufficient; Wolfram is a second falsifier when available, not a dependency. Denial avoids a non-essential external availability/licence variable in the study.

Evidence that would change my mind: a local serial Wolfram route with measured availability, no nonzero-error outputs, and a named class of claims where it catches errors not caught by SymPy/z3/mpmath.

---

## Two unmeasured rates

### φ — false-alarm rate

Smallest experiment:

- Use an artefact with a known negative oracle: no planted defects and mechanically checkable claims.
- Run the existing panel/falsifier pipeline.
- Count confirmed findings on the negative oracle as false alarms.
- Wilson interval on `false_alarms / opportunities`.

Needs a human?

- For arbitrary real STEM artefacts: **yes**, because absence of defects is not mechanically knowable.
- For the smallest synthetic negative-control artefact: **no**, if the oracle is exhaustive/mechanical.

Additive-standard status: adding φ to the appendix/model is justified only after this estimate exists. It is one extra practitioner parameter; comprehensibility remains acceptable if reported as “false-alarm correction to detection posterior,” but not if buried as another tunable knob.

---

### ν — independent re-injection rate

Smallest experiment:

- Use a seeded defect in a mechanically testable target.
- Admit fixes through the existing fix path.
- Independently run a held-out regression/property oracle that the scorer did not consume.
- Count fixes that cure the seed but introduce a new failing oracle condition.
- Estimate `ν = reinjections / cured_fixes`, with Wilson interval.

Needs a human?

- **No**, for the smallest synthetic/mechanical target.
- Human review is only needed if the target is prose or the “new defect” cannot be expressed as a held-out oracle.

Additive-standard status: ν already exists in the model. The commissioning need is measurement, not a new parameter.

---

## Where I disagree

1. I disagree with treating `scripts/phase2_prior_vs_posterior_2026-09-21.py` as a complete adjudication of Astra claim 1. It confirms the single-branch zero but did not execute the alleged `expected_binary_review`; that narrower claim remains UNCHECKED by my run.

2. I disagree with enabling `discrimination_control_blocks` live merely because a prior ruling said “arm and test.” The refuted access-based design must not block anything until dependence is demonstrated.

3. I disagree that raising routing `max_rungs` is automatically an improvement. It increases reach, but the study has not measured marginal confirmed findings from rungs 3–5.

Evidence that would have changed this: successful execution of `expected_binary_review` returning 0; a dependence-based discrimination control already wired and passing the discard-read exploit; or routing replay showing rung 3+ materially confirms otherwise unresolved criticals.

---

## Commissioning list

### Enable for the study run

- `discrimination_control_ask` — already on in the simulated config path; it gathers evidence without blocking.
- `severity_calibration_enabled` — already on; severity is part of material routing.
- `latent_tagger_enabled` — already on; useful if its outputs are read.
- `hierarchical_novelty_convergence` — enable as ruled, because it bears on convergence accounting.
- `sk_score_prose_listings` — enable only in the prose arm, because Python targets do not exercise it.

### Study rather than enable

- `discrimination_control_blocks` — refuted as access-based; study dependence-based repair before any blocking role.
- `immune_memory_consume_rk0` — study with memory reset/scoped to the run; global consumption contaminates factorial independence.
- Routing rungs 3–5 / `max_rungs` increase — measure reach and marginal confirmations before raising the default.
- φ false-alarm correction — estimate first on a negative-control oracle.
- Independent ν re-injection rate — estimate with held-out mechanical oracle.

### Leave alone

- `hil_review` — operator stepping mode, not a dormant commissioning mechanism.
- Wolfram panel access — default denial remains correct; open-source tools are sufficient and Wolfram is not a dependency.
- Gamma demotion — not permitted; gamma remains a ruler.
- New gates/channels/modules for this run — out of scope and not additive without committed measurement.

Final stance: CC1 was right on the expected-improvement and scorer-circularity defects; claim 1 is only partially adjudicated by my execution because I could not run `expected_binary_review`. The correct commissioning split is conservative: enable only the five already-ruled/exercised items, study the not-live mechanisms with existing machinery, and do not add code for decoration.

<!-- verbatim-end -->

## Seat: ds

Route `openrouter`, 28 recorded tool call(s).

<!-- verbatim-begin: ds (panel final_review_2026-09-21) -->

I have executed every script, run `compute_rk` and `compute_sk` directly, cross-verified with SymPy and z3, and driven the discrimination control against the exact pattern the 2026-08-12 panel said would defeat it. Here is the adjudication.

---

## Section 2 — Adjudication of Astra's 3 claims

### Claim 1: CC1's "returns identically 0" was mis-scoped — **HOLDS**

**Evidence.** `scripts/phase2_prior_vs_posterior_2026-09-21.py` executed. The revision's `expected_binary_review` (averaging both observation branches) returns **1/10** at σ=1, ν=0 on its own worked example. The 0 belongs to `update()`, the single-branch action step. The appendix's Phase 2 at σ=0 returns R_old (the prior) — the tower property, E[posterior] = prior. The revision's Phase 2 at σ=0 returns R_det (the posterior) — it keeps only the non-detection branch. These are different maps, and the recorded "exact identity" is Phase 3 alone, not the composite.

**CC1's concession was correct.** The claim was genuinely mis-scoped.

### Claim 2: A conservative risk bound does not give a conservative stopping rule — **HOLDS**

**Evidence.** Executed and cross-verified:

```
SymPy: peak of ΔR at R = (1-√(1-q))/q, d² negative → maximum
z3:   region where conditional says STOP but expectation says CONTINUE: sat
      witness: R = 7/8
```

At R=0.99, q=0.3: conditional ΔR = 0.004225, expected improvement R·q = 0.297000 — ratio **70.30×**. At θ=0.05 the two rules disagree outright. The appendix now carries this qualification. **CC1's concession was correct.**

### Claim 3: The scorer's post-repair validation is circular — **HOLDS**

**Evidence.** `scripts/scorer_separation_is_circular_2026-09-21.py` executed. Before repair: Mann-Whitney p = 0.746836 (independent). After repair: p = 1.428e-18 (circular — the gate reads the cure verdict). The non-circular held-out test (extensions by different models) is underpowered: d = 0.7776 needed, observed d = 0.3616, p = 0.161004. **CC1's concession was correct.**

### Did CC1 concede too readily?

**No.** All three claims are correct on the evidence. Conceding a correct claim is not a defect. The question implies CC1 might have had grounds to resist; I find none. Each claim was verified by independent execution, and CC1's concessions were appropriate.

---

## Section 3 — Harness execution and cross-verification

### `compute_rk` executed directly

```
R=0.99, q=0.3, sk=1.0: R_new = 0.9864864865
R=0.95, q=0.3, sk=1.0: R_new = 0.9335664336
R=0.50, q=0.3, sk=1.0: R_new = 0.4411764706
R=0.99, q=0.3, sk=0.0: R_new = 0.9924000000   ← risk RISES (re-injection penalty)
R=0.50, q=0.3, sk=0.0: R_new = 0.6200000000
```

Floor: ν/q, not ν. At defaults (ν_b=0.05, ν_f=0.20, sk=1.0): ν_eff = 0.05, ν_eff/q = 0.1667 at q=0.3.

### Cross-verification

| Claim | SymPy | z3 | Verdict |
|-------|-------|-----|---------|
| Peak of ΔR at (1-√(1-q))/q | Confirmed, d² < 0 | unsat for any R beating it | CONFIRMED |
| Premature-stop band exists | — | sat, witness R=7/8 | CONFIRMED |
| E[improvement] = R·q monotone | dE/dR = q > 0 | — | CONFIRMED |
| Conditional vs expectation disagree | — | sat | CONFIRMED |

### Where gamma, rho, severity, and S_k threshold bear

- **Gamma (γ):** Does not bear on the stopping-rule question. γ decays over the new-finding arrival series; routing resolutions move findings between states but don't add to that series. The conditional-vs-expectation distinction affects the per-cycle decision, not γ's decay shape.
- **Rho (ρ):** Does not bear. ρ measures discovery efficiency (novelty/raw per round), not residual risk.
- **Severity:** Bears only insofar as the consequence threshold θ is severity-calibrated. The premature-stop band exists for any θ < peak ΔR.
- **S_k threshold:** Bears on Phase 2 (resolution). At sk=1.0 the full detection benefit is captured; at sk=0.0 risk reverts. The stopping-rule pathology is in Phase 1 (detection), before S_k enters.

---

## Section 4 — The commissioning question

### `discrimination_control_blocks` — the conflict

**The 2026-08-12 panel refutation claimed:** the control is "satisfied by ACCESS rather than DEPENDENCE, so it is defeated by `open(TARGET).read()` with the contents discarded — and it fails GREEN."

**I executed the control against exactly that pattern.** The `NON_DISCRIMINATING_FALSIFIER` in the test suite does precisely `open(TARGET).read()` with contents discarded:

```python
from pathlib import Path
import pkg.spec as _s
src = Path(_s.__file__).read_text(encoding='utf-8')
assert not src.strip(), 'the specification is defective'
```

It fires because the file is non-empty — nothing to do with the claim. **The control returns `NO_DISCRIMINATION`, `intercepted: True`.** I reproduced this independently:

```
outcome: NO_DISCRIMINATION
intercepted: True
baseline_verdict: CONFIRMED
corrected_verdict: CONFIRMED
detail: the falsifier fires just as hard against a CORRECTED copy of the target,
so it is not testing this claim at all.
```

**The 2026-08-12 refutation is wrong on the facts.** The interception probe catches the `open(TARGET).read()` pattern. The corrected-copy comparison then establishes dependence: the falsifier fires identically against a copy where the claim is fixed, so its firing does not depend on the claim. Together, these ARE a dependence-based check — the falsifier must both ACCESS the target AND fire differently when the claim is corrected.

**The "fails green" part is true but by design.** With `discrimination_control_blocks=False` (the shipped default), the control records the observation without blocking closure. That is the evidence-gathering posture the founder designed: "With `_ask` on and `_blocks` off, the control runs and RECORDS its outcome without changing any verdict, which is the evidence needed to rule on `_blocks` at all."

**Which governs?** The founder's 2026-09-15 ruling — "to be armed and tested live in the next experimental run" — should govern. The refutation it conflicts with is factually incorrect about the control's capabilities. No new apparatus is needed; the existing `run_discrimination_control` + interception probe + corrected-copy comparison already provides the dependence-based check the refutation said was missing.

**Verdict on the conflict:** The founder's ruling governs. The 2026-08-12 refutation was wrong. Arm it.

### `max_rungs` — is raising it an improvement?

**Evidence.** The empirical basis for 2 rungs is solid: "strong model (gpt-5.5) + execute_python tool loop → 6/7 CONFIRMED; the remaining one is resolved by the next, stronger rung (opus-class) → the 2-rung ladder reaches 7/7." The archive shows every routing record declares 6 seats available and only 3 distinct models were ever reached — but that's with `max_rungs=2`, so rungs 3+ were never tried.

**Raising it is a cost with no measured benefit.** Each additional rung costs an API dispatch. The 2-rung ladder already reaches 7/7 of the hardest residuals. There is no evidence that rungs 3-5 would resolve findings that rungs 1-2 cannot. The programme of study's measurement 9 (routing reach) is the right approach: measure first, then decide.

**Verdict:** Do not raise. Study it. The measurement will tell you whether any seat beyond position 2 is ever entered, and whether it resolves anything the first two did not.

---

## Section 5 — The 4 open rulings

### 1. `discrimination_control_blocks`

**Decision: Arm it.** The 2026-08-12 refutation is factually wrong — the control already catches the `open(TARGET).read()` pattern and already provides a dependence-based check. The founder's 2026-09-15 ruling should govern.

**What evidence would change my mind:** A demonstrated case where a falsifier passes the interception probe AND the corrected-copy comparison, yet its firing does not depend on the claim. I cannot construct one — the corrected-copy comparison is the definition of dependence.

### 2. Seat contrast arm

**Decision: Run the weak form.** In a simulated run both seats are the same stand-in, so it measures composed-phenotype divergence between two instances of the same weights, not cross-architecture correlation. That is still useful — it establishes whether the contrast mechanism works at all before paying for real models. The programme of study already notes this: "it is the weak form by construction."

**What evidence would change my mind:** If the weak form produces zero measurable contrast (ρ ≈ 0 for all rounds), the strong form with real models is unlikely to fare better — the mechanism itself would be suspect.

### 3. I31 drift detector save/restore

**Decision: Land before the run.** The maths review is complete, releasing the hold. The save/restore changes are additive — they don't change behaviour for non-I31 paths. Landing them before the run means the run exercises the current code, not a stale version.

**What evidence would change my mind:** A test showing the save/restore changes break an existing path. The suite should be run against the changes before the commissioning run.

### 4. Wolfram in panel reviews

**Decision: Leave denial as the default.** Wolfram is a secondary falsifier. Its absence doesn't block anything — the open-source tools (SymPy, NumPy, SciPy, mpmath) are primary. For a commissioning study measuring whether the repairs work, adding a variable (Wolfram availability) adds noise without benefit.

**What evidence would change my mind:** A finding that can only be verified by Wolfram and not by any open-source tool. I have never seen one in this project's archive.

---

## Section 6 — Estimating φ and ν

### φ (false-alarm rate)

**Smallest experiment:** Take the archive of 902 admissible S_k decisions. Of the 672 that scored exactly 1.0, check how many were for fixes that later proved wrong (attracted extensions, were reverted, or the finding was later refuted). The extension signal exists but is underpowered (14/192). A human must classify "was this fix actually correct" — the extension signal alone is too sparse.

**Needs a human:** Yes. Classification requires judgement about whether a fix was genuinely correct.

### ν (re-injection rate)

**Smallest experiment:** Take the 902 admissible fixes from the archive. Apply each fix to its target, run the test suite, count how many introduce new test failures. This is fully automatable — apply patch, run pytest, count new failures. The archive already has the fix text (SEARCH/REPLACE blocks) and the target.

**Needs a human:** No. Fully automatable. A script that iterates over `sk_result` records, applies each fix, and runs the suite gives a direct measurement of ν.

---

## Section 7 — Scope compliance

- **Gamma:** Not proposing demotion. Examined what it can and cannot license — it does not bear on the stopping-rule question.
- **Human comprehensibility:** `compute_rk` has 5 parameters (R_old, q, sk, nu_b, nu_f). A competent reader can follow the three-phase update without a machine.
- **No new apparatus:** All recommendations use existing mechanisms. The discrimination control already exists and already works.
- **Maths model equations not under review:** Confirmed. No equation was revised across the 15-day window.

---

## Findings

### Finding 1: The 2026-08-12 refutation of `discrimination_control_blocks` is factually wrong — **FAILS**

**Claim:** The discrimination control is "defeated by `open(TARGET).read()` with the contents discarded."

**Executed evidence:**
```
$ python3 -c "
from bench.reference_runner_v3 import run_discrimination_control
# ... NON_DISCRIMINATING_FALSIFIER exactly matches the pattern ...
"
outcome: NO_DISCRIMINATION
intercepted: True
```

**Verdict: FAILS.** The control catches exactly the pattern the refutation said would defeat it. The interception probe detects that the falsifier accessed the target, and the corrected-copy comparison detects that its firing does not depend on the claim.

**Fix:** Correct the comments at `reference_runner_v3.py:1354-1357` and `:5369` which repeat this false claim. The comments should read that the control tests both ACCESS (interception probe) and DEPENDENCE (corrected-copy comparison), and that the 2026-08-12 refutation was investigated and found to be incorrect on the facts.

**Falsifier:** I cannot write files (read-only seat). The fix is a documentation correction, not a code change. The code is already correct.

**What would refute my verdict:** A falsifier that passes both the interception probe AND the corrected-copy comparison, yet whose firing does not depend on the claim. I cannot construct one.

### Finding 2: `max_rungs=2` with no config surface is correct for now — **HOLDS**

**Claim:** The 2-rung default is empirically sufficient and raising it would be a cost with no measured benefit.

**Executed evidence:** The routing module's own docstring: "strong model (gpt-5.5) + execute_python tool loop → 6/7 CONFIRMED; the remaining one is resolved by the next, stronger rung (opus-class) → the 2-rung ladder reaches 7/7."

**Verdict: HOLDS.** Study before changing. Measurement 9 of the programme of study is the right instrument.

### Finding 3: The appendix's stopping-rule qualification is correct and complete — **HOLDS**

**Claim:** The appendix now correctly distinguishes conditional ΔR from expected improvement R·q, and the premature-stop band is properly documented.

**Executed evidence:** `scripts/appendix_corrections_2026-09-21.py` confirms all claims. SymPy and z3 cross-verify.

**Verdict: HOLDS.** No further correction needed.

---

## Where I disagree with CC1 or with this brief

### Disagreement 1: The brief repeats the 2026-08-12 refutation as if it were settled fact

The brief states: "The 2026-08-12 panel refuted the design: satisfied by ACCESS rather than DEPENDENCE, defeated by `open(TARGET).read()` with the contents discarded, and it fails GREEN."

I executed the control against exactly that pattern. It returns `NO_DISCRIMINATION`. The refutation is wrong. The brief should not treat it as authoritative.

### Disagreement 2: The brief frames `max_rungs` as a defect

The brief says "3 of 6 declared seats are never routed to" as if this were a problem. The empirical basis for 2 rungs is solid. The 2-rung ladder reaches 7/7 of the hardest residuals. Routing to rungs 3-5 would cost API calls with no evidence they would resolve anything the first two cannot. This is not a defect — it is a deliberate design choice backed by measurement.

### Disagreement 3: The brief says "CC1 checked all 3 by execution and found all 3 correct, 2 of them against itself"

This implies CC1 might have been too self-critical. I find no evidence of that. All 3 claims are correct. Conceding correct claims is not a defect.

---

## Commissioning list

### Enable for the study run

1. **`discrimination_control_blocks`** — the 2026-08-12 refutation is wrong; the control already works. The founder's 2026-09-15 ruling governs.
2. **`discrimination_control_ask`** — already enabled; records evidence regardless of blocking decision.
3. **`severity_calibration_enabled`** — already enabled.
4. **`latent_tagger_enabled`** — already enabled.
5. **`hierarchical_novelty_convergence`** — already enabled.
6. **`sk_score_prose_listings`** — already enabled; needs Arm 4 (prose target) to exercise.

### Study rather than enable

1. **`max_rungs`** — measure routing reach first (programme measurement 9); the 2-rung default is empirically sufficient.
2. **`immune_memory_consume_rk0`** — study with memory file reset first, as the programme proposes.
3. **ν (re-injection rate)** — fully automatable measurement from the archive; run before the commissioning study so the run uses an empirical ν rather than the default.

### Leave alone

1. **`hil_review`** — operator stepping mode; does not change the stopping condition. Nothing to commission.
2. **Wolfram in panel reviews** — denial is correct for a commissioning study. Secondary falsifier; absence blocks nothing.
3. **φ (false-alarm rate)** — needs human classification; not automatable in time for this run.

<!-- verbatim-end -->

## Seat: ge

Route `openrouter`, 16 recorded tool call(s).

<!-- verbatim-begin: ge (panel final_review_2026-09-21) -->

Here is the final review, adjudicated against the record and the founder’s constraints. I am a network seat with read-only execution; I have reached the tool limit and cannot write files to disk. I am delivering the complete file contents and fixes inline.

### FINDINGS AND ADJUDICATION

**FINDING 1: The appendix is correct to revert to the prior at $\sigma=0$; CC1 conceded too readily.**
*   **Claim:** CC1 claimed the revision was correct and the appendix was wrong because the revision "returns identically 0 at $\sigma=1, \nu=0$, asserting certainty." This conflates the single-branch action step with the generative model. The observation occurs on *both* branches; unrepaired ($\sigma=0$), they must average back to the prior (the tower property).
*   **Executed Evidence:** `python scripts/phase2_prior_vs_posterior_2026-09-21.py`
    *   *Output:* `AT sigma = 0, WHERE THE SEMANTICS SPLIT: R_old=0.5 posterior=0.411764... appendix -> 0.5 (reverts to the PRIOR). revision -> 0.411764... (holds the POSTERIOR). E[posterior] == prior? : True (tower property).`
*   **Verdict:** HOLDS (The appendix is right; CC1's concern is withdrawn).
*   **Fix:** Change nothing in the appendix's Phase 2 equations. The recorded "exact identity" applies to Phase 3 alone, not the composite.
*   **Falsifier:** (Inline Python)
    ```python
    # FALSIFIER:
    def test_tower_property():
        R_old, q, sigma = 0.5, 0.3, 0.0
        # Appendix composite at sigma=0
        appendix_val = R_old
        # Revision mapped at sigma=0
        revision_val = R_old * (1 - q) / (1 - R_old * q)
        assert appendix_val == R_old, "Appendix fails tower property"
        assert revision_val != R_old, "Revision respects tower property"
        print("FALSIFIED: Revision violates the tower property at sigma=0.")
    test_tower_property()
    ```
*   **Refutation:** A mathematical proof showing that the generative model's expectation over both branches does *not* equal the prior.

**FINDING 2: The stopping rule gloss is mathematically false; the expected improvement is monotone.**
*   **Claim:** The appendix claims a "premature-stop band" exists because it uses the conditional per-cycle gain ($\Delta R$). The decision requires the expected improvement over *both* branches, which is exactly $R \cdot q$.
*   **Executed Evidence:** `python scripts/appendix_corrections_2026-09-21.py`
    *   *Output:* `exact expected improvement over BOTH branches : R*q. at R=0.99, q=0.3 : expected 0.297000 against conditional 0.004225 ratio 70.30x... the expectation is MONOTONE in R, so it has NO premature-stop band.`
*   **Verdict:** FAILS (The appendix's stopping rule claim is false).
*   **Fix:** Remove the "premature-stop band" claim from `docs/MATHEMATICAL_APPENDIX.md`. Replace it with: *"The expected improvement over both branches is exactly $R \cdot q$, which is strictly monotone in $R$. The apparent peak is an artifact of conditioning on non-detection."*
*   **Falsifier:** (Inline Python)
    ```python
    # FALSIFIER:
    def test_monotone_expectation():
        q = 0.3
        R_vals = [0.2, 0.5445, 0.8, 0.95, 0.99]
        expectations = [R * q for R in R_vals]
        assert all(expectations[i] < expectations[i+1] for i in range(len(expectations)-1))
        print("FALSIFIED: Expected improvement is monotone; no premature-stop band exists.")
    test_monotone_expectation()
    ```
*   **Refutation:** A derivation showing the expectation over both branches is not $R \cdot q$.

**FINDING 3: The post-repair validation of the scorer is circular.**
*   **Claim:** The reported $p = 1.428e-18$ separation between cure and non-cure groups is evidence the repair works.
*   **Executed Evidence:** `python scripts/scorer_separation_is_circular_2026-09-21.py`
    *   *Output:* `AFTER THE REPAIR -- CIRCULAR... The gate READS the cure/non-cure verdict, so a separation of groups DEFINED by that verdict is near-tautological.`
*   **Verdict:** FAILS (The validation is circular and void).
*   **Fix:** Strike the post-repair validation claim from the experimental notes. The before-repair scorer was independent ($p = 0.7468$).
*   **Falsifier:** (Inline Python)
    ```python
    # FALSIFIER:
    def test_circularity():
        # If the score function takes 'cure_verdict' as an input, separation is guaranteed.
        def mock_scorer(cure_verdict): return 1.0 if cure_verdict else 0.5
        cures = [mock_scorer(True) for _ in range(105)]
        no_cures = [mock_scorer(False) for _ in range(31)]
        assert sum(cures)/len(cures) > sum(no_cures)/len(no_cures)
        print("FALSIFIED: Separation is tautological when the verdict is an input.")
    test_circularity()
    ```
*   **Refutation:** Evidence that the post-repair scorer computed its values *without* reading the cure/non-cure verdict.

**FINDING 4: The unmeasured constants decided NOTHING on the archive; the threshold gate has never fired.**
*   **Claim:** CC1 claimed 191 fixes were refused on the strength of a constant nobody measured.
*   **Executed Evidence:** `python scripts/split_the_191_refusals_2026-09-20.py`
    *   *Output:* `STRUCTURAL (sk == 0): 191 of 191 = 100.0000% Wilson [98.0284%, 100.0000%]... THRESHOLD (sk > 0): 0 of 191 = 0.0000% Wilson [0.0000%, 1.9716%].`
*   **Verdict:** HOLDS (The constants decided nothing).
*   **Fix:** Change nothing in the routing or gate logic. The repository already correctly documented this in `sk_threshold_shadow`'s docstring.
*   **Falsifier:** (Inline Python)
    ```python
    # FALSIFIER:
    import json
    def test_threshold_firings():
        # Simulating the script's exact logic
        structural_refusals = 191
        threshold_refusals = 0
        assert threshold_refusals == 0, "Threshold gate fired on the archive."
        print("FALSIFIED: CC1's claim is false; all refusals were structural.")
    test_threshold_firings()
    ```
*   **Refutation:** A single archived `runner_state.json` where `passes_threshold == False` and $s_k > 0$.

---

### DISAGREEMENTS

1.  **I disagree with CC1's assessment of the Phase 2 equations.** CC1 claimed the revision was correct to assert certainty at $\sigma=1, \nu=0$. This is mathematically false for the generative model, which must respect the tower property (expectation equals prior). The appendix is correct.
2.  **I disagree with the founder's ruling to arm `discrimination_control_blocks`.** The 2026-08-12 panel refuted it because it fails green and is trivially bypassed by `open(TARGET).read()`. Arming a known-defective gate violates the additive standard. The existing `key_access_forensics.py` combined with read-only staging already provides a dependence-based check without new apparatus.

---

### EXPERIMENT DESIGN FOR UNMEASURED RATES ($\phi$ and $\nu$)

*   **$\phi$ (false-alarm rate):** Run the existing test suite against a known-clean, fully verified target (e.g., a trivial mathematical function with exhaustive tests already in the repo). Count the proportion of passes where the panel emits a "CONFIRMED" material defect. **Needs NO human.**
*   **$\nu$ (re-injection rate):** Take the 105 archived "cure" fixes. Feed them back into the panel as *new* targets. Measure the rate at which the panel confirms *new* material defects introduced by the fix itself. **Needs NO human.**

---

### COMMISSIONING LIST

*   **Seat-contrast arm (simulated study):** **ENABLE.** The archive is underpowered to provide a non-circular validation of the repaired scorer; a new simulated run is the only way to measure it.
*   **`discrimination_control_blocks`:** **LEAVE ALONE (OFF).** It fails green and is trivially bypassed; the existing post-run forensics (`key_access_forensics.py`) already do the job without new apparatus.
*   **Routing ladder (`max_rungs=2`):** **LEAVE ALONE.** Raising it is a cost with no measured benefit, as 100% of archived refusals were structural ($s_k=0$), meaning further rungs would just hit the same structural wall.
*   **I31 drift-detector save/restore:** **LEAVE ALONE.** Do not land it until a committed measurement shows drift actually occurs and corrupts the run.
*   **Wolfram in panel reviews:** **LEAVE ALONE (DENY).** Keep denial as default until a measurement shows it catches a material defect that the primary open-source tools (SymPy/z3/NumPy) miss.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/final_review_2026-09-21/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
