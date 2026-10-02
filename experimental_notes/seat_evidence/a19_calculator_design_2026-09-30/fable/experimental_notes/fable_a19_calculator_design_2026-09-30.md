<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1a032377ec39d47db76856a22d0167bedbe56ed1d5a78e7f0ac847f3bcbf3277
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# What makes a prose target answerable — fable seat, 2026-09-30

**Panel:** free design review, A19 calculator brief, dispatched by CC1 on the
founder's instruction. **Every figure below was executed this session**; the
producers are `scripts/a19_affirmative_channel_2026-09-30.py` and
`scripts/n_star_convention_settled_2026-09-30.py`, both runnable from the
repository root. Every fix referenced is applied in this sandbox tree as a
diffable proposal and is **SUGGESTED to the human** (`feedback_fixes_hil_only`);
nothing here is decided.

---

## Q1 — The mechanism that yields a definitive affirmative on prose

### Position

**The affirmative instrument already exists, is committed, discriminates
bidirectionally, and is reached by 0 of 5 live-path modules. The design is to
wire it, not to build it.** A19's flag is a harm guard — necessary-condition
checks that may reject and must never admit — and asking it to affirm is asking
a smoke detector to certify the building sound. The calculator the founder
wants runs through the **falsifier flip**: `g(V_pre, V_post)` on the claim's
own falsifier, which is the σ that `docs/MATHEMATICAL_APPENDIX.md` §214/§377
defines, and which is substrate-independent.

### Candidate mechanisms generated independently, then falsified

**M1 — Claim-level falsifier coverage certificate.** Enumerate the target's
reducible claims; each carries a runnable falsifier validated BIDIRECTIONALLY
(CONFIRMED on a planted-false variant, REFUTED on the true text) before it may
speak; the document-level answer is `N of K enumerated claims verified, 0
refuted, coverage K stated`. *Falsification attempt:* the completeness half —
"no false claim hides in unenumerated prose" — is not computable; a document
certificate would overclaim. *Survives in revised form:* the affirmative is
**per-claim**, definitive exactly as far as the enumeration reaches, with
coverage carried explicitly and the unenumerated remainder left to R_k. That
is a calculator: reducible question in (a claim), definitive answer out.

**M2 — Fix efficacy on prose (e1 for prose).** A prose FIX is affirmed when
the finding's falsifier flips CONFIRMED→REFUTED on the patched copy, with the
one-sided veto retained. *Falsification attempt — and it landed, by
execution:* the **metrology harmful fix ALSO earns the flip**
(`pristine=CONFIRMED, harmful=REFUTED`, Q1b) — it repairs the false claim
while corrupting the evidence table, the fixture's documented semantic harm
class. **The flip alone must never admit.** *Survives in composed form:*
admit only on flip **AND** veto clean **AND** the document's OTHER enumerated
claims' falsifiers still green — M1's suite is the prose regression gate (the
honest `test_cmd` for prose). The numerical harmful copy returned ERROR from
its own probe: that routes to ESCALATE, never admission, exactly as the
Python path's PROBE_BROKEN already does.

**M3 — CAS double-derivation as the affirmative.** Every numeric claim
recomputed by 2 independent tools. *Falsified as a standalone mechanism:* it
cannot decide algorithmic/graph/structural claims (2 of the corpus's 5
domains), and as a REQUIRED instrument it would import an availability
dependency. It survives as falsifier CONTENT — the corpus falsifiers already
do this with sympy/scipy/networkx.

**M4 — Panel agreement as the affirmative.** Named to reject: forbidden by
the founding principle. Tools decide, not votes.

### Executed evidence

`python3 scripts/a19_affirmative_channel_2026-09-30.py` (ALL CHECKS PASS):

- Flag ON, all 5 fixtures × {correct, harmful}: **0 of 10 ADMISSIBLE**,
  Wilson [0.0000%, 27.7533%]; every correct fix NO_SCORE; 3 of 5 harmful
  REJECTED (the in-listing payloads), 2 NO_SCORE (the semantic harms static
  gates cannot see). The instrument refuses or abstains; it cannot affirm.
- The flip: **5 of 5** correct fixes CONFIRMED→REFUTED through the runner's
  own `reverify_falsifier`, Wilson [56.5518%, 100.0000%]; 1 of 5 harmful
  fixes also flips (metrology), so the flip is necessary, not sufficient.

### The founder's sub-questions, answered directly

**Is what exists sufficient for a meaningful test?** For the VETO, yes —
the harm guard is commissioned and measured. For the CALCULATOR, no: a run
today cannot produce one affirmative on prose, so an arm-4-shaped experiment
measures only refusal behaviour. The components are sufficient; the wiring is
absent (0 of 5 live modules reach the corpus pattern — re-executed by the
brief's own validator this session).

**What else is needed?** Three wirings, no new science:
1. **Supply**: the claim-falsifier pattern (the corpus's `falsifier_template`
   shape) reachable from the live dispatch path — the prior round's W1,
   which I endorse rather than re-derive.
2. **e1 for prose**: feed the probe outcome (`fix_efficacy_outcome`) into
   prose `compute_sk` exactly as the Python path does, so ADMISSIBLE becomes
   reachable when — and only when — affirmative falsifier evidence exists.
   The `_prose_one_sided` branch then reads: new defects → REJECTED; flip +
   clean + claim-suite green → ADMISSIBLE; otherwise NO_SCORE.
3. **Prose e2 := the claim suite**: re-run the document's other validated
   claim falsifiers against the patched copy. This is what catches the
   metrology-class harm that earns the flip (measured, Q1b).

**Is A19's flag the right instrument?** No — and it should not be made one.
Keep it as the veto it is. The affirmative channel is the falsifier path.
Deleting or weakening the flag is also wrong: it convicted 3 of 5 harms this
session that the falsifier flip alone would treat inconsistently.

---

## Q2 — Accurate AND meaningful, without suppression

**Accuracy** = the number's inputs are true. **Meaning** = the reader knows
what the number CAN say. The trap the brief names is real: fix e2's false
input and the advisory rises 0.9782 → 1.0000 — honestly derived, and still a
one-sided veto's silence dressed as a grade.

**Design (applied in this tree, `_prose_one_sided` NO_SCORE branch):** the
scalar stays (never suppressed), and it now travels with its basis —
`gates_consulted: [e3_ruff, e4_bandit]`, `gates_absent: [e1_efficacy,
e2_regression]`, `affirmative_evidence: "none"`. Executed (Q2 checks, 4
PASS): the HIL now reads *"1.0 — from one-sided gates e3/e4 only; no
affirmative evidence"* instead of a bare 1.0. The number becomes **fully**
meaningful the day Q1's wiring gives it an evidence-bearing input: with e1
(flip) and prose-e2 (claim suite) feeding it, `computed_sk` on prose carries
the same information as on Python, and `affirmative_evidence` flips to the
probe verdict. Accuracy is delivered now; meaning is delivered now as honest
labelling and later as honest evidence.

*Self-falsification:* is the label itself an addition nothing reaches? No —
the record already travels to the HIL evidence bundle
(`reference_runner_v3.py:7019` `sk_gate_details`) and is asserted by an
executing script; a pytest covering the 3 fields is a 5-line addition to
`test_target_kind_and_no_score.py` and is suggested with this note.

---

## Q3 — The e1 veto on the Python path

**Built (this tree, `compute_sk`, `_e1_veto` branch):** a fix whose probe
verdict is FIX_INEFFECTIVE — the falsifier ran cleanly before and after and
still confirms the defect — returns REJECTED with the weighted mean's
would-have-paid value recorded (`computed_sk`), mirroring `_prose_one_sided`.
UNMEASURED outcomes still drop from the mean (None → unavailable), and
PROBE_BROKEN still ESCALATEs. Executed: INEFFECTIVE → REJECTED sk=0.0
(veto records 3/5 = 0.6 without e2; 5/7 with e2, sympy = Fraction = mpmath);
CURES → ADMISSIBLE 1.0 byte-identical; None → unchanged. 344 affected tests
pass; 2 tests that PINNED the old averaging contract are updated to the
strictly stronger contract, with the reasoning in their docstrings.

**The evidence that it "plugs the hole and makes the instrument more
accurate", not merely changes verdicts** — three named properties, each a
committed measurement:
1. **Agreement with the defining measurement.** sk is DEFINED as σ
   (appendix §214: "does the fix resolve the flaw?"). Before: verdict
   statistically independent of cure (Mann-Whitney p=0.746836; 31/31
   non-curing admitted; 73/73 in the wider archive, Wilson [95.0008%,
   100.0000%]). After: admission ⟹ measured-cure-or-unmeasured, by
   construction, and REJECTED ⟸ measured-non-cure, 100% on the same
   archive replayed.
2. **No collateral on cures.** 0 of the archived curing fixes flip: e1=1.0
   enters the same mean as before; the veto touches only e1=0.0.
   (Replay over the archived 105 is the pre-registration measurement to
   commit before ratification.)
3. **Risk direction.** An ineffective fix can no longer move R_k DOWN
   (0.5 → 0.495688 measured before): REJECTED holds it, which is the
   appendix's own semantics for σ=0.

*Self-falsification:* a flaky falsifier could yield a false FIX_INEFFECTIVE
and reject a good fix. Cost asymmetry decides it: a wrong REJECTED returns
the fix with feedback and holds R_k; a wrong ADMISSIBLE lowers risk on an
unfixed defect — the archive says the second happened 73 times and the first
is not yet observed. ESCALATE-instead-of-REJECT is the softer alternative if
the founder prefers HIL review of every non-cure; it spends HIL budget to
buy nothing the feedback loop doesn't already provide.

---

## Q4 — `test_cmd=None` means NO GATE, and the run-time consequences

**Yes.** A truthy guard cannot express three states. Fix applied (this tree,
`Arm.argv()`): `None` → explicit `--test-cmd ""`, which
`_run_effect_regression` maps to `(None, "no test command configured")` —
gate excluded AND recorded in `_unavailable`. Executed: arm4 emits the empty
flag; arm1's real command untouched; both `""` and `None` yield no gate.

**Consequence during a running experiment, per option:**
- **Substituted default (status quo):** each fix evaluation copies the repo
  (~1.7 GB after exclusions) into TMPDIR and runs 55 unrelated tests — pure
  wall-clock and disk churn per fix, per round; the archived record and the
  **HIL evidence bundle** (`:7019`) carry "52/55 passed (sandbox)" as if a
  gate had consulted the target; the advisory reads 0.9782.
- **No gate (fix):** e2 absent and recorded; advisory reads 1.0 with the Q2
  basis fields naming its one-sidedness; run time and disk recovered.

**CC1's invariance claim: verified with one narrowing.** No verdict and no
R_k can move: the prose branch forces `sk=0.0` and NO_SCORE/REJECTED
regardless of E, and `_gates_introduced_new_defects` reads only the e3/e4
`new:` fields (both re-executed this session). **But "only the advisory
number shifts" is incomplete:** the contaminated e2 detail string also
reaches (a) the archived `gate_details` (`:12916`) and (b) the HIL evidence
bundle (`:7019`). Those are records read by humans, and they are exactly
where a reviewer would later "learn" that a prose run had a green suite.
Model-facing feedback is unaffected (it fires only on REJECTED and lists
zero-scored gates). Disagreement is with completeness, not correctness.

---

## Q5 — The structural conflation

**Recommendation: move harvest OUT of the archive namespace (option b), and
this session added a fourth bite mark to the evidence.** Running the panel's
own affected-test set inside THIS sandbox, 2 failures printed tracebacks
pointing at the REAL repository: the staging copy carried **988 `.pyc`
files** whose embedded `co_filename` is the real repo path, so
`Path(__file__).resolve()` inside a cached test module resolves OUTSIDE the
sandbox and `_load()` would import the REAL repo's modules into a panel
measurement. (Executed: `strings` on
`bench/tests/__pycache__/test_commissioning_arms*.pyc` printed the real
path; purging `__pycache__` re-ran the tests against sandbox code.) Same
class as the brief's three: **a copy that carries the identity of its
original, stored where consumers of the original look.**

Costs, weighed not endorsed:
- **(a) shared predicate:** cannot bind the consumers that bit — `.gitignore`
  is not Python, and `co_filename` is not a path any predicate is asked
  about. Requires every future consumer to volunteer; this project's record
  (11 confirmed unreached additions) prices that at high risk.
- **(c) guard test:** enforces (a) only inside pytest's reach; same blind
  spots.
- **(b) namespace separation:** removes the class at the source — no glob
  over `bench/logs/<run>/` can reach what does not live under it, whatever
  language the consumer is written in. One-time migration cost; provenance
  preserved by a pointer FILE (not a symlink — a symlink re-creates the
  reachability) in each run dir. **Plus one line with immediate effect:
  staging and harvest must exclude `__pycache__` and `*.pyc`**, as
  `_run_effect_regression`'s own ignore list already does. The committed
  measurement to require before ratifying: re-run the three bitten
  mechanisms post-move (gitignore dedup count → 0 duplicates versioned;
  archive counter inflation 14.8359% → 0%; CC1's scan raw hits without
  path-aware collapse) plus this round's fourth (0 `.pyc` in a fresh
  staging).

---

## Q6 — n\* settled by execution: BOTH prior numbers are wrong, and rounds=10 survives only as a budget cap

Producer: `python3 scripts/n_star_convention_settled_2026-09-30.py`
(ALL CHECKS PASS). Second falsifier: Wolfram Language (local Wolfram Engine)
returned {9.380519, 1.644681, 71.699444, 147.434975}, matching sympy and
mpmath to every printed digit.

**The fitting code is found:** `bench/decay_analysis.py::fit_duane` fits
`alpha * n**gamma` to `np.cumsum(rounds_data)` — **`a` is a CUMULATIVE
coefficient** (fitted N(1)=α, CHK-2), and its `gamma` is the CUMULATIVE
exponent γ_d. The runner's `_estimate_gamma` returns **1−β for the same β**
(CHK-3: 0.2654 vs 1−0.7417=0.2583 on the identical series). **The project
runs two opposite γ conventions**, and the prior rounds plugged constants
from one into a formula reading the other:

| formula | value | status |
|---|---|---|
| `(a/θ)^(1/γ)` = 9.3805 (master list :171) | solves θ = a·n^(−γ), a RATE law **no fitter in this repo produces** (CHK-5: it fails the fitted model's own stopping equation, residual ≫ 0) | unsupported under BOTH conventions |
| `(a(1−γ)/θ)^(1/γ)` = 1.6447 (prior round) | correct **only if** γ=0.709 is runner-convention | **refuted by the fit's own data** (CHK-6: the α=4.8969 series still yields 2 novel findings in round 5) |
| `(aγ/θ)^(1/(1−γ))` = **71.6994** at (4.89, 0.709); **147.4350** at the actual record (4.8969, 0.7417) | the fitted model's own λ(n\*)=θ | correct under the convention the constants came from |

**And the pair (4.89, 0.709) exists in NO single archived fit** (CHK-4, 379
fits swept: α≈4.89 appears once, ft-014/deepseek with γ=0.7417; γ≈0.709
appears in five OTHER records). The master-list constants are themselves of
mixed provenance.

**rounds = 10:** survives, but **not for the prior rounds' stated reason**.
`ceil(9.3805)` is the ceiling of a derivationally unsupported number; the
correct n\* under the constants' own convention is ~72–147, far beyond any
sane budget, which says the March power law's tail is too slow for n\* to
set a cap at all. What actually justifies 10 is what both prior seats
independently converged on and my analysis preserves: **the binding stop is
novelty** (< θ for 2 consecutive rounds), the cap is a **budget backstop
that must declare falsification debt when it binds** (arm 1 ended RISING at
9 novel in round 8 — that was budget exhaustion, not convergence), and 10 is
a defensible budget at +25% over 8. So: yes to 10, no to deriving it from
n\*; the recommendation does NOT depend on the a-coefficient answer, which
is exactly why it survives the answer being "both prior numbers were wrong."
GAMMA stays load-bearing — as the **exponent in the novelty stop and the
debt declaration**, not as an input to a round-count formula. SUGGESTED:
correct master list :171 and record the convention beside every γ the
project stores.

---

## Deliverables in this tree

| path | what |
|---|---|
| `scripts/a19_affirmative_channel_2026-09-30.py` | Q1–Q4 falsifiers, ALL CHECKS PASS |
| `scripts/n_star_convention_settled_2026-09-30.py` | Q6 falsifiers, ALL CHECKS PASS |
| `bench/reference_runner_v3.py` | `_e1_veto` (Q3) + advisory basis fields (Q2), both marked PROPOSED |
| `bench/tools/commissioning_arms_2026-09-21.py` | three-state `test_cmd` (Q4) |
| `bench/tests/test_sk_measures_fix_efficacy_2026-09-20.py` | contract updated to the veto, strictly stronger |
| `bench/tests/test_commissioning_arms_carry_their_settings_2026-09-21.py` | contract updated to explicit-empty flag |
| this file | the design |

**Passes run: 4.** Pass 3 (regression over affected tests) surfaced the
`.pyc` finding; pass 4 produced no new finding above the consequence
threshold. HARD assumptions tested: flag-on inadmissibility (executed),
flip bidirectionality (executed), veto non-collateral on cures (executed on
synthetic; archive replay named as the pre-ratification measurement),
n\* conventions (executed, 3 tools). Untested and named: the archive replay
of Q3 over the 136 probe-carrying records (data lives in run archives; the
producer pattern is `scripts/scorer_discrimination_2026-09-20.py`), and
prose e1/e2 wiring itself, which is deliberately NOT built here — an
addition must arrive with its caller and its test, and that is a build
task for after the founder rules on this design.
