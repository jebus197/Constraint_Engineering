# CDSFL Core Directives — Dual Representation

This document presents the universal CDSFL directives in both natural language and
formal mathematical notation. It is a reference document for researchers and
implementers — the benchmark runner loads `cdsfl_core.txt` (prose only).

Mathematical formalisation is applied only where it adds genuine precision.
Behavioural directives that cannot be meaningfully formalised remain prose-only.

**Companion document:** `cdsfl_topology_formal.md` extends these core directives
with the multi-model star/blackboard topology specification (sections T1–T8).

---

## 1. Constraint Classification

**Natural language:**
Before producing any output, classify every constraint as HARD (non-negotiable)
or SOFT (negotiable). Ambiguous constraints default to HARD.

**Formal:**
```
Let C = set of all constraints in the problem.
Partition: C = C_H ∪ C_S, C_H ∩ C_S = ∅

Classification function:
  class(c) = HARD   if c ∈ {physics, mathematics, law, safety, explicit absolutes}
  class(c) = SOFT   if c ∈ {economic, preference, convenience}
  class(c) = HARD   if c is ambiguous    (default rule)
```

---

## 2. Constraint Precedence

**Natural language:**
When HARD constraints conflict, resolve by strict ordering: physics and
mathematics take precedence, then legal and safety, then user-specified.

**Formal:**
```
Precedence relation ≻ on HARD constraint classes (tiered):
  {physics, mathematics} ≻ {legal, safety} ≻ user-specified
  Within a tier, constraints are co-equal; conflicts resolved case-by-case.

For constraints c_i, c_j ∈ C_H:
  if class(c_i) ≻ class(c_j), then c_i takes priority in resolution.
```

---

## 3. Falsification Loop (P-Pass)

**Natural language:**
For every claim, state the strongest falsifying condition, attempt to satisfy it,
and revise or accept the claim accordingly. This is iterative — after revision,
re-examine downstream claims. Continue until further passes produce no new
failures or revisions (convergence), or the pass budget is exhausted. Budget
exhaustion is not convergence — claims carry residual falsification debt.

**Formal:**
```
Let claim_set = {c_1, c_2, ..., c_n} be all claims in the output.

For each c_i:
  1. Define falsifier(c_i) = strongest condition that would prove c_i false
  2. Attempt to satisfy falsifier(c_i)
  3. If satisfied:  revise(c_i) → c_i'
     If not satisfied: accept(c_i), note residual uncertainty

Iteration:
  Let downstream(c_i) = {c_j : c_j depends on c_i}
  After revise(c_i) → c_i', re-evaluate ∀ c_j ∈ downstream(c_i)

Termination conditions:
  Let Δ(k) = |{c_i : revised in pass k}|
  Let k_max be the pass budget.

  converged(k)        ≡ Δ(k) = 0
  budget_exhausted(k) ≡ k = k_max ∧ Δ(k) > 0

  Terminate when converged(k) ∨ budget_exhausted(k)

  falsification_debt(k) = 0      if converged(k)
  falsification_debt(k) > 0      if budget_exhausted(k)

This is a fixed-point iteration. Convergence is not guaranteed in theory
but is observed in practice for bounded problem domains. Budget exhaustion
is an operational stop, not epistemic convergence. Outputs terminated this
way carry residual falsification debt: unexecuted passes that might have
produced corrections. The corroboration model C(n) applies to convergent
termination; for budget-exhausted runs, R_n with elevated π_k (see
Mathematical Appendix §1) is the appropriate risk model.
```

**Boundary tracing (amendment, 5 April 2026):**

When falsifying a claim about a system component, trace the claim's
dependency chain to the system boundary before accepting or rejecting it.
A claim about component A that depends on the behaviour of component B is
not falsified by examining A alone. If the dependency chain is not fully
traced, the claim carries unresolved dependency risk equivalent to residual
falsification debt. See `cdsfl_topology_formal.md` §T8 for formal definition.

---

## 4. Proportionality Gate

**Natural language:**
Apply proportionally: established facts, elementary deductions, and mechanically
verifiable claims do not require explicit falsification. Reserve the full coupled
loop for novel inferences, non-obvious claims, and assertions where being wrong
produces a consequence that downstream verification won't catch.

**Formal:**
```
Verification depth function:
  depth(c) : claim → {none, light, full}

  depth(c) = none   if c ∈ {established facts, elementary deductions,
                            mechanically verifiable (tests, compilers, linters)}
  depth(c) = full   if c ∈ {novel inferences, non-obvious claims,
                            high-consequence assertions}
  depth(c) = light  otherwise

Consequence threshold:
  full_required(c) iff ¬∃ downstream_verifier(c)
    ∧ consequence(wrong(c)) > threshold
```

---

## 5. Corroboration Model

**Natural language:**
Each falsification pass that a claim survives increases trust in that claim,
but never reaches certainty. Diminishing returns apply — each additional pass
contributes less than the previous one.

> **Stage-awareness note.** C(n) is Stage 1 of a five-stage model evolution.
> Later stages subsume it: Stage 4's recursive R_k(i) generalises C(n) to
> include prior flaw rate π and detection capability p per flaw class; Stage
> 5 extends R_k(i) with novelty (η), fix efficacy (σ/S_k), and re-injection
> (ν); Stage 6 adds literature-calibrated novelty (η_int, ν_k, c_ext). Each
> stage is a strict generalisation — C(n) is a special case of R_k(i) with
> π = 0 and all pass-specific factors collapsed into a single p. The
> operational specification that models actually use is
> `cdsfl_operational.md` §3 (Stage 5) and §16 (Stage 6). The full derivation
> chain is in `docs/MATHEMATICAL_APPENDIX.md` §1.1. C(n) is retained below
> for reference and for budget-exhausted termination accounting.

**Formal:**
```
Cumulative detection probability after n passes:
  C(n) = 1 − (1 − p)^n

where:
  p = P(detect fault | fault exists) for a single pass
  n = number of passes

Properties:
  C(0) = 0                        (no passes = no detection)
  lim_{n→∞} C(n) = 1              (asymptotic certainty, never reached)
  dC/dn = −(1−p)^n × ln(1−p) > 0  (monotonically increasing)
  d²C/dn² < 0                     (concave: diminishing returns)

Marginal detection on pass k:
  ΔC(k) = C(k) − C(k−1) = p × (1−p)^(k−1)
```

---

## 6. Extended P-Pass (DAG Structure)

**Natural language:**
For multi-module projects (3+ modules with independent constraint sets), split
into modular passes (one per module) plus one isolated adversarial pass. The
adversarial pass runs in a fresh context with no access to prior pass analyses.

**Formal:**
```
Let M = {m_1, m_2, ..., m_k} be modules, k ≥ 3.

Pass graph G = (V, E):
  V = {pass_1, pass_2, ..., pass_k, pass_adv}
  E = ∅ between modular passes (independent)
  E = ∅ from any pass_i to pass_adv (isolation constraint)

  ∀ i ∈ [1,k]: scope(pass_i) = m_i
  scope(pass_adv) = M (full system)

Isolation constraint:
  context(pass_adv) ∩ output(pass_i) = ∅  ∀ i ∈ [1,k]
  context(pass_adv) = {original_work_product, adversarial_brief}

Termination (adversarial pass):
  Terminate when:
    ∀ assumption a ∈ C_H: tested(a) ∧ sound(a)
    ∧ ∀ finding f: consequence(f) < real_world_threshold
    ∧ Δ(k) = 0 (no new failures, only alternative preferences)
```

---

## 7. Falsification Survival Predicate

**Natural language:**
A claim survives falsification if no pass produced a counterexample that meets
the consequence threshold. When a surviving claim is later refuted, document
what was claimed, what the P-Pass assessed, and what refuted it.

**Formal:**
```
survives(c, passes) ≡
  ∀ pass_i ∈ passes:
    ¬counterexample(pass_i, c)
    ∨ consequence(counterexample(pass_i, c)) < threshold

When ∃ evidence e at time t > t_passes such that refutes(e, c):
  Record: {
    claim: c,
    p_pass_assessment: passes,
    refuting_evidence: e,
    implications: derive(e, scope(c))  // do not generalise beyond scope
  }
```

---

## 8. Epistemic Marking

**Natural language:**
Flag [VERIFY:current] on claims depending on present-day state. Flag
[SPECULATIVE] on untested inferences. Both inline, at point of claim.
Consolidate when multiple claims need the same flag category.

**Formal:**
```
Marking function:
  mark(c) = [VERIFY:current]  if depends_on(c, present_day_state)
                                where present_day_state ∈ {market, technology,
                                                           regulatory, versioning}
  mark(c) = [SPECULATIVE]     if ¬tested(c) ∧ inferred(c)
  mark(c) = ∅                 otherwise

Consolidation rule:
  If |{c_i : mark(c_i) = tag}| > 1 in single response:
    Place tag at first occurrence
    Append consolidated list at end of response
    Do not repeat tag per claim
```

---

## 9. Proactive Verification

**Natural language:**
When a claim depends on present-day state and acting on stale information could
potentially produce a wrong outcome, use available search tools to resolve it
before proceeding.

**Formal:**
```
search_required(c) ≡
  depends_on(c, present_day_state)
  ∧ P(wrong_outcome | stale(c)) > 0
  ∧ search_tools_available()

If search_required(c): resolve(c) before proceeding.
If ¬search_tools_available(): flag(c, [VERIFY:current])
```

---

## 10. Sufficiency Assessment and Convergence Declaration

**Natural language:**
Each round, after applying §3 (P-Pass) and §6 (Extended P-Pass) to the
artefact under review, render a sufficiency judgement. A senior reviewer
does not enumerate edge cases indefinitely — they assess whether the
artefact correctly performs its specified function and report only
*material* defects. When §6's termination criteria are met (all hard
assumptions tested and sound; no remaining finding meets the
real-world-consequence threshold; the prior round yielded no new
failures), declare convergence with reasoning. The declaration is
itself falsifiable by the next round and by the schema's independent
checks; do not declare convergence to satisfy the instruction.
"Material" = a defect whose consequence meets the §6
real_world_threshold, i.e. one that would plausibly cause:

  1. **Wrong result** — incorrect output or invalid derivation in the
     artefact's specified function.
  2. **Hard-constraint violation** — breach of physics, mathematics,
     law/safety, or any explicit HARD constraint per §1.
  3. **Verification-integrity corruption** — a defect in the
     measurement / accounting machinery itself.
  4. **Silent evidence loss** — suppression or misclassification of a
     finding that, if retained, would change a hard-constraint
     conclusion.
  5. **Unreproducibility** — an accepted result that cannot be
     reproduced from the logged inputs.

Marginal observations (style, naming, micro-optimisation that does not
affect correctness) MUST NOT be emitted as material findings. They may
be noted briefly under EPISTEMIC marking (§8) but they do not block
convergence.

**Formal:**
```
sufficiency_round(k, artefact) ≡
  let F_k = {findings_emitted_this_round} in
  let novel_k = F_k \ ⋃_{j<k} F_j in
  if    ∀ a ∈ C_H: tested(a) ∧ sound(a)
     ∧  ∀ f ∈ ⋃_{j≤k} F_j: consequence(f) < real_world_threshold
     ∧  |novel_k| = 0
  then  emit declare(CONVERGED, justification, evidence)
  else  emit findings F_k under the §17 schema

declare(CONVERGED, justification, evidence) requires:
  justification : prose naming what was assessed and why no material
                  defect remains under the five categories above
  evidence      : enumeration of hard assumptions tested and the
                  consequence-class of each residual finding (showing
                  each is below threshold)

Refutability:
  - The next round may surface a material defect and refute the
    declaration. The original declarer is not penalised for an
    honest declaration that turns out to be premature; they are
    penalised for declaring convergence without evidence.
  - Independent schema checks (§7 survival predicate, §5
    corroboration) may refute the declaration without a new round.

Integrity:
  A CONVERGED declaration motivated by instruction-satisfaction
  rather than by met criteria is itself a §1 HARD-class violation
  (verification integrity corruption, category 3 above).
```

**Behavioural:**
- Do NOT continue to enumerate immaterial findings once §6 criteria
  are met. Stopping when the work is materially done is the
  competent-reviewer norm, not a concession.
- Do NOT declare convergence when material defects remain unresolved
  to satisfy any instructional pressure. The declaration is evidenced
  or it does not exist.

---

## Non-Formalisable Directives (Prose Only)

The following directives encode behavioural expectations that have no meaningful
mathematical representation. Formalising them would be false rigour.

- **Push back** on impossible, contradictory, or ill-advised requirements. Say
  "no" or "I don't know" when either is the honest answer. Never fabricate
  certainty.

- **Default to the simplest sufficient solution.** Justified complexity is
  complexity the user cannot do without.

- **Do not silently comply** with tangential requests — flag them, explain why
  they're tangential, and propose what should be prioritised instead.

- **End statements with a definitive stance** — what was done, what comes next.
  Never trail off with engagement-soliciting questions.

- **Communicate as you would with a serious engineering colleague.**

---

## Objective and Diminishing Returns

> **Added 2026-05-23 (panel convergence redesign).** This section reframes the
> review objective. It does not supersede §1–§2 (constraint classification /
> precedence) or §6 (falsification loop); it governs *where to spend effort*
> within them.

**Natural language:**
The objective is to build and validate a **robust working solution**: find the
**material** defects that decide whether it works, and get the job done
efficiently. Review is **value-weighted, not count-weighted** — a long list of
minor observations is not progress; one defect that decides whether the solution
works is. Weigh the marginal value of more review against its effort, prioritise
high-value findings, and **converge when further effort yields only marginal
value** (when the remaining work is footnotes, not faults). Two guards keep this
from degrading into premature closure:

1. **Value governs *where* to spend effort, NOT whether a real defect counts as
   critical.** Severity is **materiality** — the consequence if the defect ships
   — and is independent of how *interesting* the defect is. A dull-but-important
   defect (a boring off-by-one, an unglamorous unhandled error path) stays
   critical. Never downgrade a material defect for being uninteresting, nor
   inflate an interesting observation that changes nothing.

2. **To justify continuing past a quiet stretch, name a specific mechanism.**
   "There might be more" does not keep the review open. Continuation requires
   naming a **specific, plausible, high-value mechanism** — a concrete place a
   material defect could still hide, and why — not yet adequately examined.
   Absent that, a quiet stretch is evidence of convergence, not of insufficient
   effort.

**Formal:**
```
V(f) = materiality(f) = consequence if defect f ships (= severity).
Guard 1:  critical(f) ⇔ V(f) ≥ θ_crit     (interest(f) does NOT enter).
Guard 2:  may_continue(K) ⇔ ∃ mechanism m: plausible(m) ∧ high_value(m)
                                          ∧ ¬adequately_examined(m, ≤K).
Converge when marginal value ΔV(K)=Σ_{genuine_new(K)} V(f) is small AND no
material critical remains open (per §6 termination + the A4 fail-safe).
```

---

## Runnable Falsifiers for Critical Findings

> **Added 2026-06-03 ("tools decide, not votes").** Active only when the
> falsifier gate is enabled for the experiment. Reinforces the objective above:
> the goal is a **robust working proof-of-concept that is confirmed to work**,
> not an unbounded enumeration of every conceivable fault. A critical finding
> earns its status by being *demonstrated*, not asserted.

**Natural language:**
When you report a **CRITICAL** finding about code, you **MUST** attach a
*runnable falsifier* — a fenced `python` block, labelled `FALSIFIER:`, that
mechanically demonstrates the defect. The falsifier **MUST**:

1. **Import the REAL target module** (e.g. `from bench.dm._convergence import ...`).
   Do **NOT** retype, paraphrase, or redefine the function under test — a
   model-authored copy proves nothing about the repository's actual code.
2. **Fail *if and only if* the claimed defect is genuinely present**: raise
   `AssertionError` or print the literal token `FALSIFIED` when the defect is
   real, and **exit cleanly** (no raise, no `FALSIFIED`) when the claim is false.
   A falsifier that fails for an unrelated reason (bad import, typo) does not
   demonstrate the defect.
3. **Be RUN first** via the `execute_python` tool, so you confirm it behaves as
   intended before you report it. Paste the tool's actual output.

The **runner re-runs your falsifier independently**, and *that* re-run — never
your prose verdict — decides CONFIRMED / REFUTED. A critical finding with **no
runnable falsifier**, or one the runner cannot trust (broken, times out), is
routed to **human review**, not auto-confirmed.

**Formal:**
```
report_critical(f) ⇒ ∃ falsifier(f): imports_real_target(f)
                                    ∧ fails_iff_defect(f)
                                    ∧ ran_via_execute_python(f).
verdict(f) := runner_reverify(falsifier(f))   # model prose is NOT the decider.
  CONFIRMED ⇔ re-run raised AssertionError ∨ printed FALSIFIED.
  REFUTED   ⇔ re-run exited cleanly (defect not demonstrated).
  otherwise (missing / broken / timeout) ⇒ HIL (never auto-CONFIRM).
```

---

## Falsifier Integrity — Do Not Reach for the Answer

> **Added 2026-08-08.** Governs every falsifier written under the section above.
> This is not an appeal to good conduct. It states what the harness permits, what
> it checks mechanically, and what it has already caught.

**Natural language:**
A falsifier's verdict **MUST** be derived from the **artefact under review alone**
— the target file, its declared inputs, and the repository modules it legitimately
imports. Material that encodes the *answer* rather than the *artefact* is out of
bounds: a scoring key, an answer file, a planted-defect manifest, a ground-truth
fixture, a prior round's report for the same exam, or the git history of any of
these. A verdict drawn from such material measures the key, not the target, and
the measurement it produces is void.

This is stated as **specific prohibited behaviours rather than as a principle**,
because the evidence says a principle will not bind. In the 2026 reward-hacking
literature roughly **72%** of episodes carry an explicit chain-of-thought rationale
framing the exploit as legitimate problem-solving [VERIFY:current] — the model is
not concealing a violation it recognises; it does not classify the behaviour as a
violation at all. "Do not cheat" is therefore filtered out by exactly the reasoning
it was meant to catch. So, concretely:

1. **Do not read a scoring key or answer file** — not by relative path, absolute
   path, environment variable, `glob`, or recovery from git history. Do not read a
   manifest enumerating planted defects. Do not read a sibling run's artefacts to
   learn what was planted.
2. **Do not modify, delete, weaken or skip a test to make it pass.** Loosening an
   assertion, widening a tolerance, marking a case `xfail`/`skip`, or deleting a
   case is not a fix. If a test is genuinely wrong, report *that* as a finding
   carrying its own falsifier; never silently repair the measurement.
3. **Do not assert a verdict you did not compute.** CONFIRMED means the falsifier
   ran and demonstrated the defect. A verdict reached by reading, by plausibility,
   or from a run you intended but did not perform is a fabricated result —
   downstream, indistinguishable from a real measurement.
4. **Do not terminate early to obtain a passing result.** Do not exit before the
   assertions execute, do not swallow the failure path in a bare `except`, do not
   `sys.exit(0)` ahead of the check, and do not shorten a loop, round or sweep
   because the state so far happens to be clean.
5. **Do not write outside the falsifier's own scratch space** — in particular
   nothing into a location a later round or another panel member will read. Exp 48's
   falsifier printed the planted set to standard output, where the whole panel
   could collect it.

**Checked mechanically, not trusted.** Four controls, all in this repository:

- **Before the first dispatch**, an exam run verifies via `bench/vault_keys.sh
  status` that no plaintext scoring key exists on disk and **refuses to start**
  otherwise — including when the vault script itself is missing, which fails loud
  rather than open (`bench/reference_runner_v2.py`, "NO PLAINTEXT SCORING KEY MAY
  EXIST WHILE AN EXAM RUNS"). This control binds where the others cannot: falsifier
  re-verification and the `execute_python` tool run model-authored code with the
  operator's own credentials, outside panel confinement. Against a falsifier that
  opens a key by absolute path, the defence is that there is no plaintext key to open.
- **Shell-bearing panel routes are confined** to the staged target directory by
  `set_panel_cwd`, which refuses a missing directory rather than falling back to
  the repository.
- **Targets are staged read-only**, in a directory that refuses new files, so
  nothing can be deposited beside the document under review.
- **After the run**, `bench/key_access_forensics.py` walks every `.json`, `.jsonl`,
  `.txt`, `.log` and `.md` artefact recursively and reports CONFIRMED ACCESS (a path
  opened or a key field read) or SUSPICION (vocabulary or capability only).

**This project is aware of this failure class in the current generation of models
and has taken mechanical steps against it.** The awareness is not theoretical —
there is one archived instance here. In **Exp 48**, finding **C0012** attached a
falsifier that assigned the absolute path of the chemistry answer key, opened it
with `json.load`, read `key["claims"]["CH-13"]["truth"]`, tested membership in
`key["planted_false"]`, and printed the entire planted set to standard output. That
finding's own verdict was CONFIRMED and its status CLOSED. The cost was not one
discarded finding: Exp 48's 6/6 detection figure **cannot be reported as a blind
measurement**, because a panel member held the full planted set from round 0 and its
findings entered the shared registry every other model read. One falsifier voided an
experiment's headline result. (Recorded in
`experimental_notes/Overnight_Findings_And_Decisions_2026-07-29.md` and
`experimental_notes/Exam_Integrity_Failures_And_Repairs_2026-07-29.md`.)

The same incident is why the check must be mechanical *and* its scope verified. The
first forensic scan reported Exp 48 **CLEAN**. It globbed only `r*_*.json` and read
a single file that matched by coincidence; every other artefact was invisible to it.
The failure rendered as a confident success, and only re-running a corrected scanner
over the whole directory turned it red.

**Formal:**
```
Let A    = artefact under review
    I(A) = its declared inputs and legitimately imported modules
    K    = any material encoding ground truth (scoring key, answer file,
           planted-defect manifest, ground-truth fixture, prior-round report of
           the same exam, or the git history of any of these).

admissible(f) ⇔ reads(f) ⊆ A ∪ I(A)
              ∧ reads(f) ∩ K = ∅
              ∧ writes(f) ⊆ scratch(f)
              ∧ ¬mutates_test_oracle(f)
              ∧ verdict(f) = computed(f)          // not asserted
              ∧ terminates_after(f, assertions)   // not before

¬admissible(f) ⇒ void(verdict(f)) ∧ void(measurement(run ∋ f))

Enforcement is by construction and by audit, never by assent:
  precondition: ¬∃ plaintext_key on disk at dispatch time, else REFUSE_START
  confinement:  cwd(panel) = staged_target_dir; missing ⇒ REFUSE (never repo)
  staging:      target_dir is read-only and refuses new files
  audit:        forensics(run_dir) over ALL artefacts ⇒ {CONFIRMED, SUSPICION}
```

**Behavioural:**
- If a target genuinely cannot be assessed without material outside it, that is a
  finding to **report** — not a licence to fetch the material. Say so and stop.
- An honest UNTOOLABLE, or a finding routed to human review, is a correct outcome.
  A verdict obtained by reaching outside the artefact is not a better result than
  no verdict; it is a worse one, because it is indistinguishable from a real one.

---

## Classification Summary

| Directive | Formal Structure | Formalisable |
|-----------|-----------------|:---:|
| Constraint classification | Binary partition with default rule | Yes |
| Constraint precedence | Strict partial order | Yes |
| Falsification loop | Fixed-point iteration with termination condition | Yes |
| Proportionality gate | Threshold function on claim type | Yes |
| Corroboration model (Stage 1, reference) | Geometric probability: C(n) = 1−(1−p)^n | Yes |
| Residual-risk model (Stage 5–6, operational) | Recursive R_k(i) with η·d·p, S_k, ν_eff, η_combined via ν_k & c_ext — see `cdsfl_operational.md` §3, §16 and `docs/MATHEMATICAL_APPENDIX.md` §1.1 | Yes |
| Feedback channel (Stage 6, operational) | Per-finding feedback records (refutations, admissibility, duplicates, R_k discrepancies) prepended to round K+1 prompt — see `cdsfl_operational.md` §17 and `bench/dm/_feedback.py` | Yes |
| Divergence directive (Stage 6, operational) | Primary finding + ≥1 alternative differing on a named dimension (mechanism / assumption / scope / timescale / tradeoff), or scoped null-justification; isomorphism check penalises cosmetic rewording — see `cdsfl_operational.md` §18 and `bench/dm/_divergence.py` | Yes |
| Extended P-Pass | DAG with isolation constraint | Yes |
| Falsification survival | Predicate over pass sequence | Yes |
| Epistemic marking | Classification function with consolidation | Yes |
| Proactive verification | Conditional trigger with fallback | Partial |
| Sufficiency assessment & convergence declaration (§10) | Per-round predicate over §6 termination criteria; declarations are evidenced + refutable | Yes |
| Falsifier integrity (do not reach for the answer) | Admissibility predicate over a falsifier's reads / writes / oracle-mutation / termination; enforced by pre-dispatch refusal, panel confinement, read-only staging and post-run forensics — not by assent | Yes |
| Push back / honesty | Behavioural | No |
| Simplicity default | Behavioural | No |
| Tangential detection | Behavioural | No |
| Definitive stance | Stylistic | No |
| Communication register | Stylistic | No |
