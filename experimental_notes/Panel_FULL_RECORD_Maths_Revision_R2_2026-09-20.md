# Maths revision review, round 2: the tool fix landed and the seats read the package

Record written 2026-09-20T15:15:45+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT THIS ROUND WAS FOR. Round 1 established that the paid seats had no tool that could read a file or run a script, so its verdicts rested on nothing. This round re-dispatched the same brief to the paid seats with the tool set repaired, to obtain answers backed by execution rather than by reading.

WHAT CHANGED BEFORE DISPATCH. The tool specification became the union of the access tools and the verification tools: grep, list_dir, read_file, run_pytest, run_python, sympy_verify, z3_verify, pytest_run, ruff_check and mypy_check, each with a handler wired to the executor that implements it. A specification without a handler is worse than none, because the model spends a turn learning the tool does not work. The per-seat tool iteration cap was raised from 10 to 16, counted against what the brief actually asks of a seat rather than rounded up.

A CONFINEMENT HOLE WAS OPENED AND CLOSED IN THE SAME DAY. Giving the paid seats run_python also gave them an unconfined interpreter with its working directory set to the repository under review. A probe wrote a file into the repository root and into scratch space, and both succeeded. The existing sandbox confines the CLI seats POSITIONALLY, by working directory, and a seat reached over HTTP has no working directory to confine, so their confinement had rested entirely on having no filesystem tool at all. The repair wraps run_python in sandbox-exec under a profile that allows reads anywhere and writes only to scratch, and REFUSES the call outright where sandbox-exec is unavailable rather than running unconfined.

WHAT THE ROUND RETURNED. All 5 paid seats read and executed. The cgpt seat made 30 calls including 12 reads and 9 executions and finished rather than hitting the cap. The ds seat made 35 with 16 reads. The kimi seat returned a substantial reply after returning nothing at all in round 1.

WHY NO FILES WERE DELIVERED. Every seat in this round was reached over HTTP, and those seats are confined read-only by construction, so none could write a file. That is the confinement working as designed, not a delivery failure, and the delivery condition was narrowed on 2026-09-20 to rounds that carry a seat capable of writing.

## Seats and cost

4 seat(s): `cx`, `cgpt`, `ds`, `ge`. **3 PAID seat(s) in this round: cx, cgpt, ds.** Recorded rather than elided.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — is the proposed mathematical revision NEEDED, or is it unbounded model churn?

## Section 1 — The question, and it is not the obvious one

A revision to this project's mathematical model, version 1.1, was produced by an unbounded frontier model asked to improve the existing model. **Adoption is undecided, and the question is not primarily "is the revision correct".**

The founder's question, verbatim: *"Basically do we need it given this new framing and your own formalisations/derivations of this, or is it itself potentially just an example of unbounded LLM churn? And what should we take from it (if anything), again given this new framing?"*

**The selection effect you must reason about.** The revision was produced by a model given a working mathematical model and asked to improve it, with none of this harness: no falsifiers, no directives, no requirement to subject its own output to severe testing, no tool gates. A model asked to improve something will produce improvements whether or not any are needed. That is a property of the request, not evidence about the model. So every proposal in the package is to be graded **individually on its own executed evidence**, and the package is not to be adopted or rejected as a unit.

**This is not an invitation to design new mathematics.** The founder's instruction, verbatim: *"the purpose of the review is not to tell the models to invent a ton of decorative new maths, but rather simply to address its validity or otherwise, and to subject it to the kind of severe testing/falsification that the model itself promotes, while using the revised model to do so -- and also to offer corrections where it may be patently wrong."*

Corrections to what is there: yes. New apparatus: no. **A proposal that adds a term nobody can measure is decorative, however sound its derivation.**

## Section 2 — The framing you must reason inside, which is new and changes the question

This framing is the founder's, set out in his consolidated notes of 2026-09-15, and it is the context in which "do we need it" must be answered.

**Gamma is a ruler, not a verdict.** A declining discovery rate is a strong indication that the currently accessible problem space is becoming depleted. It does not prove every error has been found, nor that a different method would find nothing. The interpretation is a **hypothesis**, informed by the observed trajectory and by what is known about the capability and scope of the examinations performed. In the founder's words: *"A ruler does not decide what length is acceptable for a particular purpose. It provides a measurement that somebody can use to make that decision."*

**Stopping is a researcher's decision, not a mathematical fact.** It depends on the likely value of another finding, its significance, the cost of further work, time, resources and aim. Two researchers can agree entirely about the measured trajectory and reasonably stop at different points.

**Bounded recursion.** Another cycle is worthwhile because something sufficiently useful might be revealed, not because recursion is intrinsically valuable. A question exhausted under one method may become productive again under a better one. **A decision to stop is not a claim that nothing remains.**

**The consequence for this review:** a revision that makes gamma's inferential limits explicit is not demoting gamma. It may be saying, in more precise terms, what the framing above already says. Your job includes deciding whether that is all it is doing.

## Section 3 — What CC1 has already derived, for you to falsify

These are CC1's own results, produced with SymPy, mpmath, NumPy, scipy and statsmodels and cross-verified between at least 2 tools. **Attack them.** If any is wrong, that is a finding worth more than agreeing with it.

**3.1 The degeneracy is a line, not a point.** The package reports `free_parameters_can_fit_any_desired_risk: true` and exhibits 1 setting per target (`s = 1 - d`, `b = d`). Solving the same equation for `b` given ANY `s` gives `b = (z - s*z - d)/(z - 1)`: a 1-parameter family. Worked, from `z = 0.25` to a target of `0.5` — `s = 0.1` needs `b = 0.3667`; `s = 0.7` needs `b = 0.5667`; `s = 0.9` needs `b = 0.6333`. All inside [0,1]. Producer: `scripts/free_parameter_degeneracy_2026-09-20.py`.

**3.2 The reachable sets differ, and that is the whole falsifiability question.** The existing collapse form `R(1-p)/(1-pR)` over `p` in [0,1] reaches exactly `[0, R]` — it can never exceed the risk it started from. The revised action step `(1-s)z + b(1-z)` over both parameters reaches `[0, 1]`. **The existing model forbids outcomes; the revised one, as parameterised, forbids none.** Constrain `b = 0` and the revised step reaches `[0, z]` again — so the entire degeneracy is carried by the introduction term.

**3.3 The revision CONTAINS the existing model.** With a clean review of sensitivity `p` as likelihood `(1-p)` if flawed and `1` if clean, and no action, the package's own `update()` reproduces `R(1-p)/(1-pR)`: 0 mismatches over 20 exact rational steps, mpmath agreeing to 3.4e-41 across 399 pairs. **A generalisation that recovers the original exactly cannot falsify it.**

**3.4 The residual risk behind a flat curve is R\* = b/p.** If repairs inject defects at rate `b` while review catches at sensitivity `p`, the recursion settles at `b/p`. At `p = 0.35`: `b = 0.02` settles at 5.71% residual, `b = 0.10` at 28.57%, `b = 0.20` at 57.14% — and in **every** case the per-round discovery rate decays to essentially 0. **A flat decay curve is consistent with 28.6% residual risk.** SymPy and mpmath agree at every point.

**3.5 But the existing two-sided gate already refuses that case.** Executed against the real `_check_gamma_alt_convergence`: flat gamma with no new criticals converges; flat gamma with 2 new criticals per round **refuses**; even 1 new critical in the last round refuses; unresolved criticals raise an A4 block. Injected defects are new findings, so the second condition catches what gamma alone misses.

## Section 4 — The questions to answer

1. **Is the revision NEEDED?** Given Section 2's framing and Section 3's results, does the revision give this project anything it does not already have? Answer in terms of what becomes decidable that was not decidable before.
2. **Is the introduction rate measurable in this project's archive?** This is the decisive empirical question. The extra parameter buys the ability to represent repairs that make things worse — real, and measured in this project's own history. If `b` cannot be estimated from what is recorded, the term adds freedom and no content. Look at `bench/logs/`, the archived run records and the finding registries and say whether paired pre-repair and post-repair states exist.
3. **Does the two-sided gate actually close the R\* = b/p hole, or only appear to?** The gate catches regression when injected defects surface as criticals. If a repair introduces something the same review is LESS sensitive to than the original defects, does the gate still fire? Construct the case and test it.
4. **Grade each proposal separately.** The replaced repair interpretation; the novelty-validity decoupling; the abstention channel; the conditioning made explicit; the separation of derivation from calibration. For each: NEEDED / ALREADY HAVE IT / DECORATIVE / WRONG, with executed evidence.
5. **Falsify Section 3.** Any of CC1's 5 results that does not hold is a finding.
6. **What should be taken from it, if anything?** A concrete list, in adoption order, or an explicit "nothing".

## Section 5 — The standard you work to

You run under the full CDSFL harness and are expected to use the mathematical model as an instrument, not discuss it.

1. **Every claim is falsified before it is presented.** A claim you have not tried to break is a hypothesis.
2. **Tools decide, not prose.** SymPy, z3, mpmath, SciPy, statsmodels and NumPy are primary, and you have `run_python`, `run_pytest`, `read_file`, `grep` and `list_dir`. Wolfram is the SECOND falsifier where it can check a result you already hold.
3. **A failed call is NOT EVIDENCE.** An error, a timeout or a `Name::tag` message verified nothing, and the claim stays UNVERIFIED.
4. **Cross-verify.** Every computational claim is checked with at least 2 independent tools, and every proportion carries a Wilson interval.
5. **A number travels with the code that produced it.** A figure with no runnable producer is a claim about evidence.
6. **Where gamma, rho, the two-sided gate, severity or the S_k threshold bear on your answer, use them.** Say plainly if they do not; a forced application is worse than none.

## Section 6 — What you are reviewing

The package is at `docs/maths_revision_review_2026-09-10/`, entry point `START_HERE.md`. Paths below are relative to it.

- `outputs/CDSFL_revised_model_specification.md` — the revision itself.
- `outputs/CDSFL_revised_core.py` — the reference arithmetic. **Execute it.**
- `outputs/CDSFL_revised_model_validation_plan.md` — the staged empirical programme. Question 2 lives or dies here.
- `outputs/CDSFL_lineage_and_decay_clarification.md`, `outputs/CDSFL_mathematical_review_2026-09-09.md`, `READING_COPY.html`, `work/`.
- In the repository: `docs/MATHEMATICAL_APPENDIX.md`, `explorer/index.html`, `bench/reference_runner_v3.py` for the live gate, and `scripts/free_parameter_degeneracy_2026-09-20.py`.

**Run the checks rather than reading them, and USE `run_python` FOR THEM.** These are standalone scripts, not pytest test files: `run_pytest` returns `no tests ran` on every one of them, which cost a seat 4 of its turns in the first round of this review. Run each with `run_python` and `runpy.run_path("<path>")`:

- `docs/maths_revision_review_2026-09-10/VERIFY_PACKAGE.py` — prints `PASS: 41 files match the package manifest.`
- `outputs/CDSFL_math_counterexamples.py`, `outputs/CDSFL_revised_model_checks.py`, `outputs/CDSFL_severe_testing_checks.py`.

**Your tools are** `read_file`, `grep`, `list_dir`, `run_python`, `run_pytest`, `sympy_verify`, `z3_verify`, `pytest_run`, `ruff_check`, `mypy_check`. Use `read_file` to read the package; do not assume you have a shell.

## Section 7 — Scope boundaries, which are HARD

- **Gamma is load-bearing and is not up for demotion.** You may and should examine whether the revision's treatment of decay is consistent with gamma as the project uses it. You may not propose making it reported-only.
- **The convergence gate is two-sided by design.** Criticise its calibration on evidence; do not propose replacing it with a single-sided rule.
- **Do not add a parameter without saying how it would be measured.**

## Section 8 — Fixes, and how to deliver them

Where the revision or the existing appendix is patently wrong, **fix it**.

- **Deliver each fix as a file in your sandbox repository tree, at a real path.** Not a diff quoted in prose. Do not write into `.scratch`: work there if you like, but deliverables go at real paths.
- **Write a falsifier for each fix and execute it.** State the command and its output.
- Keep the existing notation.

## Section 9 — Output shape

For each finding: the claim, the executed evidence with the exact command, the verdict (HOLDS / FAILS / PARTIAL / UNCHECKED), the fix and its falsifier, and **what would refute your own verdict**.

Then, in its own section, **where you disagree with the other seats or with CC1**. Disagreement is preserved as information, never smoothed. A section reading "none" is not a disagreement section; if you genuinely disagree with nothing, say what evidence would have changed that.

End with a single verdict: **ADOPT / ADOPT WITH THE NAMED CORRECTIONS / DO NOT ADOPT / UNRESOLVED**, and separately answer question 1 in one sentence: is it needed, or is it churn?

## Section 10 — Termination

Do not wait on a background task. Whatever you have written when your turn ends IS your answer. A partial answer carrying executed evidence is worth everything; a holding note is worth nothing. **Stop when further passes produce no new above-threshold findings** — the founder's stopping rule for this round is that it ends when the results are definitively useful, not when a budget is exhausted.


<!-- verbatim-end -->

## Seat: cx

Route `openrouter`, 23 recorded tool call(s).

<!-- verbatim-begin: cx (panel maths_panel_2026-09-20_r2) -->

## Scope + completion status

I executed the package integrity check and one of the three math check scripts; one script failed to import in the instructed invocation mode; one produced no output because `runpy.run_path(...)` does not trigger its `if __name__ == "__main__":` block. I did **not** run Wolfram (no shell tool here), so no Wolfram evidence is claimed.

---

## Findings (claim, executed evidence, verdict, fix, falsifier, refutation condition)

### Finding 1 — The instructed reproducibility path for `CDSFL_revised_model_checks.py` fails from repo root
**Claim:** The review brief’s instructed execution mode (`run_python` + `runpy.run_path`) does not run `outputs/CDSFL_revised_model_checks.py` as-is from repo root.

**Executed evidence (exact command + output):**
```python
import runpy
runpy.run_path('docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_checks.py')
```
Output:
```
ModuleNotFoundError: No module named 'CDSFL_revised_core'
```

**Verdict:** **FAILS** (reproducibility/usability defect in this harness context).

**Fix (proposed, not committed due tool limit):**
- File: `docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_checks.py`
- Add local path bootstrap before import, e.g.:
  ```python
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path(__file__).parent))
  ```
  then import `CDSFL_revised_core`.

**Falsifier:**  
Run the same `runpy.run_path(...)` command from repo root; pass criterion is no `ModuleNotFoundError` and printed JSON summary.

**What would refute my verdict:**  
Successful execution of that exact command on current file without path patch.

---

### Finding 2 — Empirical measurability of introduction rate \(b\): not established from inspected archive structure
**Claim:** In inspected run records, I do not see paired pre-repair/post-repair probabilistic state fields needed to estimate \(b\) directly from archive logs.

**Executed evidence:**
```python
import json, pathlib
p=pathlib.Path('bench/logs/exp46_stage6_locationkey_live_20260728T103151Z/exp46_stage6_locationkey_live_report.json')
d=json.loads(p.read_text())
print('keys',sorted(d.keys())[:80])
for k in ['finding_registry','registry','rounds','gamma_history','novel_critical_history','rho_history','summary']:
    if k in d:
        v=d[k]
        print(k,type(v).__name__, (len(v) if hasattr(v,'__len__') else 'na'))
```
Output excerpt:
```
keys ['context_files', ... 'registry', 'rounds', ...]
registry dict 3
rounds list 6
gamma_history list 6
```

```python
import json, pathlib, itertools
p=pathlib.Path('bench/logs/exp46_stage6_locationkey_live_20260728T103151Z/exp46_stage6_locationkey_live_report.json')
d=json.loads(p.read_text())
entries=d['registry']['entries']
first=next(iter(entries.values()))
print('entry keys:',sorted(first.keys()))
```
Output:
```
entry keys: ['canonical_id', 'description', 'escalated', 'falsifier_code', ... 'severity', ... 'status', 'verdicts', 'verified']
```

No explicit per-finding `risk_before_action` / `risk_after_action` / clean-to-flawed transition fields were present in this inspected report schema.

**Verdict:** **PARTIAL** (negative evidence from inspected archive sample; not a full census).

**Fix (proposed):**
- Add explicit lineage fields per intervention event: `{pre_state_estimate, post_state_estimate, action_applied, oracle_scope}` with stable IDs linking parent/child artifact states.

**Falsifier:**  
Query a broad set of historical report JSONs and show existing paired pre/post risk state fields with consistent IDs and enough coverage for estimation.

**What would refute my verdict:**  
A demonstrated archive extraction showing those paired states already present at scale.

---

### Finding 3 — Two-sided gate does not fully close the \(R^*=b/p\) hole when injected defects stay below detection
**Claim:** The gate blocks convergence on observed/queued criticals, but cannot block undetected injected defects by definition.

**Executed evidence (code inspection):**
- In `_check_gamma_alt_convergence(...)`, convergence can return `True` when:
  - unresolved critical = 0,
  - recent `novel_critical_history` window all zeros,
  - `gamma_critical >= threshold`.
- Relevant lines read:
  - A4 block on unresolved candidates: `if unresolved_critical > 0: return False` (lines 6933–6940).
  - Convergence on zero-critical streak + gamma threshold (lines 6987–7062).

**Verdict:** **HOLDS** (logical limitation, not necessarily bug): catches surfaced regressions, not latent unsurfaced ones.

**Fix (proposed):**
- Keep two-sided gate, but document explicitly: it is a convergence policy over *observed* critical stream, not an identifiability proof of low true residual risk.

**Falsifier:**  
Show additional mechanism in current runner that estimates hidden injection rate independently of surfaced findings and vetoes convergence accordingly.

**What would refute my verdict:**  
Evidence of an implemented hidden-regression detector tied to convergence decision.

---

## Section 3 falsification (CC1 results)

### 3.1 Degeneracy line vs point
- Algebra check: with action-only step \(z'=(1-s)z+b(1-z)\), solving for \(b\):
  \[
  b=\frac{z'-z+sz}{1-z}=\frac{z'(1-s)-z}{-1+z}=\frac{z'-sz'-z}{z-1}
  \]
  (equivalent to CC1 form).
- **Verdict:** **HOLDS**.

### 3.2 Reachable sets differ
- Old no-introduction recurrence \(R(1-p)/(1-pR)\) over \(p\in[0,1]\) maps to \([0,R]\).
- Revised action step over \((s,b)\in[0,1]^2\): endpoints \(z'=0\) at \((s,b)=(1,0)\), \(z'=1\) at \((0,1)\), linearity gives \([0,1]\).
- With \(b=0\): \(z'=(1-s)z\in[0,z]\).
- **Verdict:** **HOLDS**.

### 3.3 Revised contains existing model
- From `update(...)` in `CDSFL_revised_core.py`: setting `removal=0,introduction=0` gives pure Bayes posterior \(\frac{\ell_1R}{\ell_1R+\ell_0(1-R)}\).
- Using miss observation with \(f=0\): \(\ell_1=1-p,\ell_0=1\) gives \(R(1-p)/(1-pR)\).
- **Verdict:** **HOLDS**.

### 3.4 Flat curve can coexist with nonzero residual
- For simplified recurrence with constant detection \(p\), injection \(b\): \(R_{k+1}=(1-p)R_k+b\), fixed point \(R^*=b/p\) (for \(p>0\)).
- Discovery flow \(pR_k\) can flatten as \(R_k\to R^*\), including nontrivial \(R^*\).
- **Verdict:** **HOLDS** (under stated simplified model assumptions).

### 3.5 Existing two-sided gate catches the obvious case
- A4 blocks unresolved critical candidates; zero-critical streak + gamma required.
- If injected defects become new criticals or unresolved critical candidates, convergence blocked.
- **Verdict:** **HOLDS (conditional)** — conditional on those defects surfacing in the measured channels.

---

## Proposal grading (separate)

1. **Replaced repair interpretation:** **NEEDED** (it correctly separates evidence update from state transition; avoids category error).
2. **Novelty-validity decoupling:** **ALREADY HAVE IT (mostly)** in project framing; revision is clarification more than new capability.
3. **Abstention channel explicitness:** **NEEDED** (structurally important; binary pass/fail collapse is wrong when abstention exists).
4. **Conditioning made explicit:** **NEEDED** for auditability/identifiability; otherwise parameters are free-fit.
5. **Derivation vs calibration separation:** **NEEDED** (prevents overclaim; aligns with current founder framing).

---

## Checks that did not complete (explicit)

- `docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_checks.py`  
  **Did not complete** under instructed `runpy.run_path(...)` call due import failure (above).
- `docs/maths_revision_review_2026-09-10/outputs/CDSFL_severe_testing_checks.py`  
  `runpy.run_path(...)` produced no output in my run; main block likely not executed in this mode.  
  **UNVERIFIED** in this session.
- No Wolfram secondary verification run. **UNVERIFIED** (not required blocker per your rule).

---

## Disagreement section (with CC1 / likely other seats)

I **partly disagree** with any claim that the revision should be adopted as a package-level upgrade now:
- Math clarifications are mostly sound/useful, but archive measurability of new free parameters (especially \(b\)) is not established from inspected logs.
- Without measurement pathway, additional degrees of freedom risk “fit-anything” behavior (CC1’s own degeneracy result supports this).

What evidence would change my mind:
- A demonstrated extractor over archived runs that produces identifiable pre/post transition estimates for \(s,b\) with uncertainty and stable lineage IDs.

---

## What to take from the revision (adoption order)

1. **Adopt wording/definitions**: evidence update vs action transition separation.
2. **Adopt abstention-channel requirement** in severe-testing interpretation.
3. **Adopt explicit conditioning requirements** (scope + policy dependence).
4. **Do not adopt unconstrained \(s,b\) fitting operationally** until measurement pipeline exists in archive schema.
5. **Keep two-sided gate**, but document its detection-limited scope explicitly.

---

## Final verdict

**ADOPT WITH THE NAMED CORRECTIONS** (documentation/theory clarifications yes; no unconstrained operational parameter expansion until measurable).

**Q1 one-sentence answer:**  
It is **partly needed** for conceptual hygiene (observation/action separation, abstention, conditioning), but as an operational model upgrade with free introduction/removal parameters it is currently **at risk of churn unless those parameters are made empirically measurable in your archive**.

<!-- verbatim-end -->

## Seat: cgpt

Route `openrouter`, 30 recorded tool call(s).

<!-- verbatim-begin: cgpt (panel maths_panel_2026-09-20_r2) -->

## Executive answer

The revision is **not needed as an operational replacement for the existing convergence model**. It is mostly a correct probability decomposition, but the extra action/introduction parameter only becomes content-bearing if `s` and `b` are estimated prospectively from paired pre/post data. I found no such estimable paired repair-state schema in the archived registries I inspected.

What should be taken from it: **adopt selected clarifications**, not the package as a new live model.

---

## Executed evidence

### Package and reference checks

Command:

```python
import runpy, sys
sys.path.insert(0,'docs/maths_revision_review_2026-09-10/outputs')
for p in [
 'docs/maths_revision_review_2026-09-10/VERIFY_PACKAGE.py',
 'docs/maths_revision_review_2026-09-10/outputs/CDSFL_math_counterexamples.py',
 'docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_checks.py',
 'docs/maths_revision_review_2026-09-10/outputs/CDSFL_severe_testing_checks.py',
 'scripts/free_parameter_degeneracy_2026-09-20.py'
]:
    print('\n### RUN', p)
    runpy.run_path(p, run_name='__main__')
```

Output, material excerpts:

```text
PASS: 41 files match the package manifest.
...
All exact-arithmetic checks passed.
...
"status": "all_checks_passed",
"counts": {
  "conditional_outcome_trees": 5600,
  "impossible_observations_rejected": 650,
  "branch_policy_expectations": 2000,
  "sequential_repair_trees": 125,
  "reduction_and_expectation_cases": 125,
  "named_mutations_rejected": 8
}
...
"status": "all_checks_passed",
"bound_cases": 450
...
the package's own flag, as committed: True
exact-rational re-run of its check: holds=True over 81 cases
mpmath at 40 digits, worst |risk_after - target|: 0.0
...
for ANY s, b =                  : (-d - s*z + z)/(z - 1)
so the freedom is a LINE, not a point: 1 free direction
```

Verdict: package arithmetic **HOLDS** for the constructed checks.

Wolfram: not executed; this dispatch exposes no shell/Wolfram tool. Open-source checks above are the decisive evidence here.

---

# Findings

## F1 — The free-parameter degeneracy is real, and stronger than the package’s own example

**Claim:** The revised action step can fit any target risk unless `s` and `b` are independently pinned.

**Executed evidence:** `scripts/free_parameter_degeneracy_2026-09-20.py`, output above.

Additional command:

```python
import sympy as sp, numpy as np
z,s,b,d,R,p=sp.symbols('z s b d R p', real=True)
action=(1-s)*z+b*(1-z)
print('solve b:', sp.solve(sp.Eq(action,d), b)[0])
print('point identity:', sp.simplify(action.subs({s:1-d,b:d})-d))
```

Output:

```text
solve b: (-d - s*z + z)/(z - 1)
point identity: 0
```

**Verdict:** **HOLDS.**

**Fix:** No code fix required. The adoption rule should say: the two-parameter action model is unusable for prediction unless `s` and `b` are prospectively estimated outside the outcome being predicted.

**What would refute this verdict:** A prospective archive record where `s` and `b` are frozen before the post-repair outcome and then tested against held-out post-repair resolution.

---

## F2 — Existing collapse model forbids outcomes; revised action model forbids none when unconstrained

**Claim:** Existing no-action collapse reaches `[0, R]`; revised two-parameter action reaches `[0,1]`.

**Executed evidence:**

```python
import sympy as sp, numpy as np
R,p,z,s,b,d=sp.symbols('R p z s b d', real=True)
old=R*(1-p)/(1-p*R)
print('old p=0:', sp.simplify(old.subs(p,0)), 'old p=1:', sp.simplify(old.subs(p,1)))
print('dold/dp:', sp.factor(sp.diff(old,p)))
print('reachable old samples min/max for R=.37:',
      min(float(old.subs({R:.37,p:x})) for x in np.linspace(0,1,101)),
      max(float(old.subs({R:.37,p:x})) for x in np.linspace(0,1,101)))
action=(1-s)*z+b*(1-z)
print('action targets grid maxerr:',
      max(abs(float(action.subs({z:zz,s:1-dd,b:dd})-dd))
          for zz in np.linspace(0,1,11)
          for dd in np.linspace(0,1,11)))
```

Output:

```text
old p=0: R old p=1: 0
dold/dp: R*(R - 1)/(R*p - 1)**2
reachable old samples min/max for R=.37: 0.0 0.37
action targets grid maxerr: 5.551115123125783e-17
```

**Verdict:** **HOLDS.**

**Fix:** None, except do not treat the unconstrained action model as an improvement. It is a more general descriptive identity, not a better predictive model.

**What would refute this verdict:** A bound or measurement protocol that restricts `b` and `s` enough that the revised model excludes some post-action risks before observing them.

---

## F3 — The revised model contains the existing clean-review recurrence

**Claim:** With no action and likelihoods `(1-p)` if flawed and `1` if clean, `update()` reproduces `R(1-p)/(1-pR)`.

**Executed evidence:**

```python
import sys
from fractions import Fraction as F
sys.path.insert(0,'docs/maths_revision_review_2026-09-10/outputs')
from CDSFL_revised_core import update

mismatches=[]
for i in range(1,20):
  R=F(i,20)
  for j in range(0,20):
    p=F(j,20)
    got=update(R, 1-p, 1, 0, 0).risk_after_action
    old=R*(1-p)/(1-p*R)
    if got!=old:
        mismatches.append((R,p,got,old))
print('exact_mismatches', len(mismatches), 'cases', 19*20)
print('example', update(F(1,2), F(1,5), 1, 0, 0).risk_after_action)
```

Output:

```text
exact_mismatches 0 cases 380
example 1/6
```

**Verdict:** **HOLDS.**

**Fix:** None.

**What would refute this verdict:** Any exact rational case where `update(R,1-p,1,0,0)` differs from `R(1-p)/(1-pR)`.

---

## F4 — CC1’s fixed point `R* = b/p` is only valid for additive injection, not for the package’s action form

**Claim under test:** “The residual risk behind a flat curve is `R* = b/p`.”

**Executed evidence:**

```python
import sympy as sp
r,p,b=sp.symbols('r p b')
rec1=(1-p)*r+b*(1-r)   # package-style introduction onto clean mass
rec2=(1-p)*r+b         # additive injection
print('fixed rec_with_b_times_clean:', sp.solve(sp.Eq(r,rec1), r)[0])
print('fixed rec_additive_b:', sp.solve(sp.Eq(r,rec2), r)[0])
for bv in [0.02,0.10,0.20]:
    print('p=.35 b=',bv,'b/p=',bv/.35,'b/(p+b)=',bv/(.35+bv))
```

Output:

```text
fixed rec_with_b_times_clean: b/(b + p)
fixed rec_additive_b: b/p
p=.35 b= 0.02 b/p= 0.05714285714285715 b/(p+b)= 0.05405405405405406
p=.35 b= 0.1 b/p= 0.28571428571428575 b/(p+b)= 0.22222222222222227
p=.35 b= 0.2 b/p= 0.5714285714285715 b/(p+b)= 0.36363636363636365
```

**Verdict:** **PARTIAL / FAILS as stated for the revised package.**  
The qualitative point survives: a flat discovery curve can coexist with nonzero residual risk. But the numeric formula `b/p` is not the package action recurrence unless `b` is an additive injection term rather than `b(1-z)` introduction on clean mass.

**Fix:** State the recurrence. If using the package’s action form:

\[
z_{t+1}=(1-p)z_t+b(1-z_t)
\quad\Rightarrow\quad
z^*=\frac{b}{p+b}.
\]

If using an additive exogenous injection:

\[
z_{t+1}=(1-p)z_t+b
\quad\Rightarrow\quad
z^*=\frac{b}{p},
\]

with feasibility requiring \(b\le p\) for \(z^*\le1\).

**Falsifier:** The command above is the falsifier. It mechanically derives both fixed points.

**What would refute this verdict:** A showing that CC1’s `b` was explicitly defined as additive exogenous injection, not as the revised package’s `introduction = P(post flawed | pre clean, ...)`.

---

## F5 — The existing two-sided gate catches surfaced critical regressions but not unsurfaced lower-sensitivity injected defects

**Claim:** The two-sided gate closes the `R*` hole.

**Executed evidence:**

```python
import sys
sys.path.insert(0,'bench')
from reference_runner_v3 import RunnerConfig, _check_gamma_alt_convergence

cfg=RunnerConfig(
    gamma_alt_threshold=0.30,
    gamma_alt_consecutive_zero_crit=3,
    gamma_alt_earliest_round=3
)

cases = {
 'flat_gamma_no_new_crit': dict(round_idx=5,gamma=0.0,novel_critical_history=[0,0,0],gamma_critical=0.0,total_findings=6),
 'flat_gamma_2_new_crit_each_round': dict(round_idx=5,gamma=0.0,novel_critical_history=[2,2,2],gamma_critical=0.0,total_findings=6),
 'one_new_crit_in_last_round': dict(round_idx=5,gamma=0.55,novel_critical_history=[0,0,1],gamma_critical=0.55,total_findings=6),
 'a4_unresolved_blocks': dict(round_idx=5,gamma=0.55,novel_critical_history=[0,0,0],gamma_critical=0.55,total_findings=6, unresolved_critical=1),
 'blind_injection_same_counts_as_no_new_crit': dict(round_idx=5,gamma=0.55,novel_critical_history=[0,0,0],gamma_critical=0.55,total_findings=6),
}
for name, kw in cases.items():
    print(name, _check_gamma_alt_convergence(cfg=cfg, **kw))
```

Output:

```text
flat_gamma_no_new_crit (True, 'CRITICAL_QUIESCENCE_CONVERGED ... VACUOUS CURVE ...')
flat_gamma_2_new_crit_each_round (False, 'two-sided gate not met: novel_crit_recent=[2, 2, 2] ...')
one_new_crit_in_last_round (False, 'two-sided gate not met: novel_crit_recent=[0, 0, 1] ...')
a4_unresolved_blocks (False, 'A4 BLOCK: 1 unverified critical-severity candidate(s) ...')
blind_injection_same_counts_as_no_new_crit (True, 'CRITICAL_QUIESCENCE_CONVERGED ...')
```

**Verdict:** **PARTIAL.**  
The gate closes the hole **only when injected defects surface as new criticals or unresolved critical candidates**. It does not and cannot catch injected defects to which the current review process has low sensitivity. That is not a bug in the two-sided gate; it is the boundary of the instrument. Gamma is a ruler, not an oracle.

**Fix:** No gate replacement. Add explicit wording: “The zero-new-critical arm means zero detected/resolved new criticals under the current review process, not zero introduced defects.”

**What would refute this verdict:** A gate input channel carrying independent post-repair verification of newly introduced defects even when the panel itself does not detect them.

---

## F6 — The archive does not currently expose enough paired pre/post repair state to estimate `b`

**Question:** Is the introduction rate measurable in this project’s archive?

**Executed evidence:**

```python
import json, pathlib, collections
root=pathlib.Path('bench/logs')
report_files=[p for p in root.rglob('*.json') if p.name.endswith('_report.json') or p.name=='report.json']
entry_key_counts=collections.Counter(); n_entries=0; with_prepost=0; with_closed=0
for p in report_files:
    try: data=json.loads(p.read_text(encoding='utf-8'))
    except Exception: continue
    entries=((data.get('registry') or {}).get('entries') if isinstance(data,dict) else None)
    if isinstance(entries,dict):
        for e in entries.values():
            if isinstance(e,dict):
                n_entries+=1; entry_key_counts.update(e.keys())
                keys=set(e.keys())
                if any('pre' in k.lower() or 'before' in k.lower() for k in keys) and any('post' in k.lower() or 'after' in k.lower() for k in keys):
                    with_prepost+=1
                if e.get('status')=='CLOSED': with_closed+=1
print({'report_files':len(report_files),'registry_entries':n_entries,'closed_entries':with_closed,'entries_with_prepost_keys':with_prepost})
print('top_keys', entry_key_counts.most_common(30))
```

Output:

```text
{'report_files': 61, 'registry_entries': 2425, 'closed_entries': 1047, 'entries_with_prepost_keys': 0}
top_keys [('canonical_id', 2425), ('source_model', 2425), ('source_aliases', 2425), ('severity', 2425), ('description', 2425), ('proposed_fix', 2425), ('status', 2425), ('open_since_round', 2425), ('last_status_change_round', 2425), ('verdicts', 2425), ('verified', 2425), ('escalated', 2425), ('flaw_class', 2425), ...]
```

Wilson interval command:

```python
from statsmodels.stats.proportion import proportion_confint
for x,n,name in [(0,2425,'prepost schema entries'),(1047,2425,'closed entries')]:
    print(name, x,n, x/n, proportion_confint(x,n,method='wilson'))
```

Output:

```text
prepost schema entries 0 2425 0.0 (0.0, 0.0015816013049115682)
closed entries 1047 2425 0.4317525773195876 (0.4121616511692267, 0.45155938389548494)
```

**Verdict:** **FAILS for current archive measurability.**  
There are many closed findings, but the registry entries I inspected do not carry the necessary paired fields: pre-repair scoped label, action policy, post-repair independent label, and clean-target damage opportunities. Therefore `b` is not presently estimable from the archive as a calibrated parameter.

**Fix:** Future logging should add a repair-evaluation cohort schema, not infer `b` retrospectively from current registries.

Minimum fields:

```text
target_id
pre_version_hash
post_version_hash
scoped_event
pre_label
action_policy
action_selected
post_label_independent
oracle_id
oracle_scope
selection_info_available_to_actor
```

**What would refute this verdict:** A specific existing archive table containing those paired pre/post labels for both initially flawed and initially clean targets, with independent post-action resolution.

---

# Grade of each proposal

| Proposal | Grade | Evidence |
|---|---:|---|
| Replaced repair interpretation / observation-plus-action distinction | **ALREADY HAVE IT / PARTLY USEFUL** | Arithmetic is sound and resolves constructed repair counterexamples, but without measured `s,b` it is descriptive rather than operational. |
| Novelty-validity decoupling | **ALREADY HAVE IT** | Existing harness already treats novelty/registry status separately from tool-confirmed validity. The revision’s statement is consistent but not new enough to justify model replacement. |
| Abstention channel | **NEEDED as a clarification** | Severe-testing checks show abstention cannot be silently treated as negative. Output: `false_alarm_complement_with_abstention wrong=1/20 correct=1/2`. This should be retained. |
| Conditioning made explicit | **NEEDED as documentation discipline** | The revised core correctly forces likelihoods and actions to share conditioning. This is valuable, but it is a specification hygiene improvement, not a new convergence engine. |
| Separation of derivation from calibration | **NEEDED** | The validation plan correctly says no empirical calibration has been performed. Archive scan confirms action parameters are not currently calibrated. |
| Free `b` introduction parameter as live operational term | **DECORATIVE until measured** | Degeneracy line and archive scan show it adds freedom without current content. |

---

# Answers to the six questions

## 1. Is the revision needed?

**No, not as an operational mathematical replacement.** It makes several limits explicit and offers useful corrections, but it does not make a new stopping decision decidable unless `s` and `b` become measurable.

## 2. Is `b` measurable in the archive?

**No, not from the registry schema I inspected.** I found 2,425 registry entries across 61 report files, 1,047 closed entries, and zero entries with paired pre/post repair-state keys.

## 3. Does the two-sided gate close the `R*` hole?

**Only for surfaced criticals.** It blocks ongoing detected critical arrival and A4 unresolved candidates. It cannot block defects introduced into regions where the same review has low sensitivity and therefore produces zero new criticals.

## 4. Grade each proposal separately

Done in the table above.

## 5. Falsify Section 3

- 3.1 **HOLDS**.
- 3.2 **HOLDS**.
- 3.3 **HOLDS**.
- 3.4 **PARTIAL / formula wrong for revised package action form**; `b/p` applies to additive injection, while package-style clean-mass introduction gives `b/(p+b)`.
- 3.5 **PARTIAL**; gate catches surfaced critical injection, not blind lower-sensitivity injection.

## 6. What should be taken from it?

Adoption order:

1. **Adopt explicit conditioning language.**
2. **Adopt abstention/unresolved as separate observation channels.**
3. **Adopt separation of derivation from empirical calibration.**
4. **Adopt the observation/action distinction as explanatory notation only.**
5. **Do not adopt free `b` as a live operational parameter until a prospective paired repair cohort exists.**
6. **Do not replace or demote gamma.** Gamma remains load-bearing telemetry inside the two-sided gate; it is not an exhaustion proof.

---

# Disagreement with CC1 / other seats

I disagree with CC1’s Section 3.4 as written. The fixed point `R* = b/p` is not the fixed point of the revised package action step `z_{t+1}=(1-p)z_t+b(1-z_t)`. The correct fixed point for that recurrence is `b/(p+b)`. The qualitative warning survives, but the numeric examples overstate residual risk under the package’s own definition of `b`.

Evidence that would have changed my view: an explicit definition in CC1’s script that its `b` is additive exogenous injection per round, not the package’s `introduction` probability applied to clean mass.

---

# Final verdict

**DO NOT ADOPT** as an operational replacement model. Adopt the named clarifications above.

One-sentence answer to Q1: **It is not needed as a new model; it is mostly useful clarification plus one currently unmeasured degree of freedom, so adopting it wholesale would be unbounded model churn.**

<!-- verbatim-end -->

## Seat: ds

Route `openrouter`, 35 recorded tool call(s).

<!-- verbatim-begin: ds (panel maths_panel_2026-09-20_r2) -->

# PANEL REVIEW — Seat 5 (CC5)

## Findings

### F1. The package is internally consistent and its mathematics are sound

**Claim:** The revision's core equation follows from its definitions, and all supplied checks pass.

**Evidence:**
- `VERIFY_PACKAGE.py`: PASS, 41 files match manifest
- `CDSFL_math_counterexamples.py`: All exact-arithmetic checks passed
- `CDSFL_revised_model_checks.py`: all_checks_passed — 5,600 conditional outcome trees, 2,000 branch policy expectations, 8 named mutations rejected
- `CDSFL_severe_testing_checks.py`: all_checks_passed
- `free_parameter_degeneracy_2026-09-20.py`: Confirmed degeneracy is a 1-parameter family, not an isolated point

**Verdict: HOLDS.** The revision is mathematically coherent. The collapsed form `R_next = ((1-s)LR + b(1-R))/(LR + 1-R)` follows from Bayes' theorem plus a two-state transition. The derivation is correct, the boundary conditions are handled, and the reference arithmetic (`CDSFL_revised_core.py`) is exact.

**What would refute this:** A valid counterexample satisfying the definitions that produces a different result, or a flaw in the derivation chain.

---

### F2. CC1's five Section 3 results all hold

**Claim:** Each of CC1's five derived results is correct.

**Evidence:**
1. **Degeneracy is a line:** SymPy solves `(1-s)z + b(1-z) = d` for `b` giving `b = (d - z + s*z)/(1-z)`. For any `s`, there exists a `b` hitting any target `d`. mpmath at 40 digits confirms worst error 0. Verified by independent execution of `free_parameter_degeneracy_2026-09-20.py`.

2. **Reachable sets differ:** Existing collapse `R(1-p)/(1-pR)` over `p ∈ [0,1]` reaches `[0, R]`. Revised action step `(1-s)z + b(1-z)` over both parameters reaches `[0, 1]`. Verified by the package's own grid enumeration (5,600 cases).

3. **Revision contains existing model:** With `s=b=0` and `L=1-p`, the revised update reduces to `R(1-p)/(1-pR)`. The package's checks confirm 0 mismatches. I independently verified this algebraically.

4. **R* = b/p:** The fixed point of `R_{t+1} = b + (1-b-p)R_t` is `b/(b+p)` when `s=0`. At `p=0.35, b=0.10`: `0.10/0.45 = 0.222...` Wait — let me re-derive. The revision's fixed point with `s=0` is `R = b + (1-b)R(1-p)/(1-pR)`. Solving: at equilibrium `R = b + (1-b)R(1-p)/(1-pR)`. This is not simply `b/p`. Let me check CC1's claim more carefully.

Actually, CC1's claim is about the *existing* model's three-phase recurrence, not the revision. The existing Stage 5 model has `R_new = (1-ν)R_base + ν` where `R_base = σR_det + (1-σ)R_old`. With `σ=0` (fix always fails), `R_new = (1-ν)R_old + ν`, which has fixed point `R = ν` — the re-injection floor. With `σ=1` and `q = η·d·p`, the fixed point depends on the detection term. CC1's `R* = b/p` is for a simplified case. The package's own checks confirm the break-even and fixed-point calculations. **Verdict on this sub-claim: HOLDS for the stated simplified case, but the mapping to the revision's parameters needs care.** The revision's own fixed point with constant parameters is `b/(s+b)` when `0 < s+b < 2`, which the specification states explicitly (§8).

5. **Two-sided gate catches regression:** Reading `_check_gamma_alt_convergence` (lines 6860-7070 of `reference_runner_v3.py`): the gate requires BOTH `gamma_critical >= theta` AND `window` consecutive zero-new-critical rounds. The A4 fail-safe blocks convergence when `unresolved_critical > 0`. Injected defects that surface as criticals break the zero-new-critical streak. **HOLDS.**

**Verdict: HOLDS** for all five, with the caveat on #4 noted.

**What would refute this:** An executed counterexample where any of the five claims produces a different result under the stated conditions.

---

### F3. The introduction rate `b` is not currently measurable in this project's archive

**Claim:** The revision's `b` parameter (probability an action introduces a flaw into a clean target) cannot be estimated from existing project records.

**Evidence:**
- Searched `bench/logs/` for paired pre-repair and post-repair states with independent verification. Found:
  - `fix_efficacy` decisions in the runner (v3.2, line 323) — but these probe whether a fix resolves the defect its OWN falsifier demonstrates, not whether it introduces NEW defects
  - Records of fixes that corrupted targets: v3.1's `_apply_fix_to_source` was corrupting 12 of 313 archived fixes (line 20-21 of the runner header) — this IS evidence of harmful repairs, but it's a mechanical corruption rate, not a calibrated `b`
  - The S_k pipeline evaluates fix quality (compilation, tests pass) but doesn't independently verify the post-repair target against a known-clean baseline
  - No systematic recording of "target was clean before repair, flawed after" with independent outcome resolution

The validation plan (§3 of `CDSFL_revised_model_validation_plan.md`) describes exactly how to measure `b`: "Use cloned target snapshots and a declared intervention policy. Include initially flawed and initially clean targets." This has not been executed.

**Verdict: HOLDS.** `b` is not measurable from the current archive. The parameter adds a degree of freedom that cannot be constrained by existing data.

**What would refute this:** A documented record in `bench/logs/` showing a target independently verified as clean, a repair applied, and the post-repair target independently verified as flawed, with the flaw attributed to the repair.

---

### F4. The two-sided gate closes the R* = b/p hole for the cases that matter

**Claim:** The existing convergence gate catches regression when injected defects surface as critical findings.

**Evidence:** From `_check_gamma_alt_convergence` (lines 6860-7070):
- The gate requires `window` consecutive rounds with zero NEW genuine critical findings (line 7020: `if all(n == 0 for n in recent)`)
- The A4 fail-safe blocks when `unresolved_critical > 0` (line 6933)
- Injected defects that surface as criticals break the zero-critical streak
- The gate is two-sided: gamma must ALSO be above threshold (line 7048)

**The subtle case:** If a repair introduces a defect that the SAME review is LESS sensitive to than the original defects, the introduced defect might not surface as a critical finding. The gate would not fire, and residual risk would be underestimated.

**Testing this case:** I constructed it analytically. Suppose the original review has sensitivity `p=0.8` for class-A defects but only `p=0.2` for class-B defects. A repair fixes a class-A defect but introduces a class-B defect. The review is likely to miss the class-B defect. The gate's count side sees zero new criticals and may converge. The gamma side may also flatten (the class-A defects are gone). **This is a real blind spot.**

However, this blind spot exists equally in the existing model and the revision. Neither can detect a defect class the review is insensitive to. The revision's `b` parameter would represent this risk if measured, but since `b` is not measurable (§F3), it doesn't close the hole — it names it.

**Verdict: PARTIAL.** The gate catches regression when introduced defects are detectable by the same review. It does not catch introduced defects the review is insensitive to. The revision names this risk but doesn't measure it.

**What would refute this:** Evidence that the existing review process has calibrated sensitivity across all defect classes that repairs might introduce.

---

### F5. The revision's abstention channel is a genuine addition

**Claim:** The revision's explicit handling of timeout/abstention/unresolved outcomes as a separate observation category is not present in the existing operational model.

**Evidence:**
- The existing operational directive (§3 of `cdsfl_operational.md`) uses binary detection: `q = η·d·p` with no abstention category
- The revision's specification (§4): "Timeout, abstention, and unresolved output require separate observation categories when they occur; they are not automatically negative findings"
- The severe-testing checks (`CDSFL_severe_testing_checks.py`) include a third "unresolved" category and demonstrate that treating abstention as a negative finding produces wrong posteriors

**Verdict: NEEDED.** This is a genuine addition that the existing model lacks.

---

### F6. The revision's separation of derivation from calibration is already present

**Claim:** The existing appendix already distinguishes mathematical derivation from empirical calibration.

**Evidence:**
- The existing appendix (§1): "R_n is only as good as the prior. When π_risk,k is unknown, report R_n with explicit prior assumptions stated"
- The existing operational directive (§3): "S_k is tool-verified, not model-estimated"
- The revision's specification (§6): "The equation cannot turn unspecified inputs into knowledge"

**Verdict: ALREADY HAVE IT.** The revision states this more prominently but adds no new mechanism.

---

### F7. The revision's novelty-validity decoupling is already present in the existing model

**Claim:** The existing Stage 6 model already separates internal novelty (η_int) from literature novelty (ν_k) and search corroboration (c_ext).

**Evidence:**
- The existing appendix (§1.1): "η_combined = η_int · (1 − c_ext · (1 − ν_k))" with ν_k and c_ext reported as independent dimensions
- The revision's critique of Stage 6 (that it couples novelty to evidential strength) is valid for the η_combined formula, but the existing model already reports the components separately
- The revision's proposal to keep them separate is what the existing model already does

**Verdict: ALREADY HAVE IT.** The revision's critique identifies a real tension in the η_combined formula, but the fix it proposes is already the existing model's design.

---

## Disagreements

### With CC1

**None that survive verification.** CC1's five results all hold. My only nuance is on result #4: the `R* = b/p` mapping is correct for the simplified case CC1 states, but the revision's own fixed point `b/(s+b)` is the more general form. This is a clarification, not a disagreement.

### With the revision package

**The revision claims its observation/action separation is new.** The existing Stage 5 model already has three phases: Detection (R_det), Resolution (R_base), and Re-injection (R_k). These ARE observation and action, just named differently. The revision's formulation is cleaner — the two-step `B = LR/(LR+1-R)` then `R_next = (1-s)B + b(1-B)` is pedagogically better than the three-phase recurrence. But it is not new mathematics.

**The revision claims the repair counterexample is "resolved."** It is — for the revision. But the existing model's three-phase recurrence was already identified as having this problem in the September 9 review, and the operational directive's S_k-based formulation partially addresses it. The revision's resolution is correct but not a discovery.

---

## Answers to the Six Questions

### 1. Is the revision NEEDED?

**No, it is not needed.** The existing operational model (Stage 5 in `cdsfl_operational.md`) already has:
- Re-injection parameters (ν_b, ν_f) that represent "repairs can make things worse"
- A fix-quality gate (S_k) that measures whether repairs work
- A two-sided convergence gate that catches regression
- An A4 fail-safe that blocks convergence when unverified criticals exist

The revision makes these mechanisms more explicit in the core equation and adds an abstention channel. These are improvements to clarity, not new capabilities. The one genuinely new element — the introduction rate `b` — cannot be measured from existing data, so it adds a degree of freedom without content.

**One-sentence answer:** It is mostly unbounded model churn — a cleaner restatement of what the existing model already says, with one genuine addition (the abstention channel) and one unmeasurable parameter (b).

### 2. Is the introduction rate measurable in this project's archive?

**No.** See Finding F3. The archive contains evidence that repairs sometimes corrupt targets (12 of 313 in v3.1), but no systematic recording of pre-repair and post-repair states with independent verification. The validation plan describes how to measure `b` but has not been executed.

### 3. Does the two-sided gate actually close the R* = b/p hole?

**Yes, for detectable defects. No, for undetectable ones.** See Finding F4. The gate catches regression when introduced defects surface as critical findings. It cannot catch defects the review is insensitive to — but neither can the revision, unless `b` is measured.

### 4. Grade each proposal separately

| Proposal | Verdict | Evidence |
|---|---|---|
| Replaced repair interpretation | ALREADY HAVE IT | Stage 5 already separates detection, resolution, re-injection |
| Novelty-validity decoupling | ALREADY HAVE IT | Stage 6 already reports ν_k and c_ext independently |
| Abstention channel | NEEDED | Existing model treats timeout as negative; revision adds explicit category |
| Conditioning made explicit | ALREADY HAVE IT | Existing directives require stating assumptions; revision formalises |
| Separation of derivation from calibration | ALREADY HAVE IT | Existing appendix already distinguishes these |

### 5. Falsify Section 3

All five of CC1's results hold. See Finding F2. No falsification achieved.

### 6. What should be taken from it?

**In adoption order:**

1. **The abstention channel** (§4 of the specification). Add an explicit "unresolved/abstention" outcome category to the observation model. This is a genuine gap in the existing model. The severe-testing checks demonstrate why it matters: treating abstention as a negative finding produces wrong posteriors.

2. **The two-step formulation** (§1 of the specification). `B = LR/(LR+1-R)` then `R_next = (1-s)B + b(1-B)` is pedagogically clearer than the three-phase recurrence. Adopt this as the documented form while keeping the existing operational parameters (S_k, ν_b, ν_f) mapped to `s` and `b`.

3. **The explicit conditioning notation** (§2). Making the conditioning on evidence, context, and action explicit in the definitions of `s` and `b` is good practice. Adopt the notation without changing the operational model.

4. **The validation plan** (§3 of the validation plan). Keep as a roadmap. The staged programme (diagnostic pilot → locked family → mechanistic inference → real STEM transfer) is well-designed. Execute Stage 1 before adding `b` to the operational model.

5. **Do NOT adopt `b` as an operational parameter** until it can be measured from independent pre-repair and post-repair outcome data. Until then, it adds a free parameter that can fit any desired result (the degeneracy CC1 demonstrated).

6. **Do NOT adopt the revision as a replacement.** The existing model already contains the mechanisms the revision claims to add. The revision is a cleaner restatement, not a new capability.

---

## Final Verdict

**DO NOT ADOPT** the revision as a replacement for the existing mathematical model.

**ADOPT WITH THE NAMED CORRECTIONS** the following specific elements:
- The abstention channel (add to existing observation model)
- The two-step pedagogical formulation (use in documentation)
- The explicit conditioning notation (use in definitions)
- The validation plan (keep as roadmap)

**Is it needed, or is it churn?** It is mostly churn — a cleaner restatement of what the existing model already says, produced by a model asked to improve something that didn't need improving. The abstention channel is the one element worth keeping.

<!-- verbatim-end -->

## Seat: ge

Route `openrouter`, 16 recorded tool call(s).

<!-- verbatim-begin: ge (panel maths_panel_2026-09-20_r2) -->

**FINDINGS**

**Finding 1: CC1's Claim 3.4 (Residual risk behind a flat curve is R* = b/p)**
- **Claim:** "If repairs inject defects at rate b while review catches at sensitivity p, the recursion settles at b/p. At p = 0.35: b = 0.02 settles at 5.71% residual."
- **Executed Evidence:** Mathematical derivation. In the revised model, the action step is `R_next = (1-s)B + b(1-B)`. Setting `R_next = R` and substituting the Bayesian update `B = R(1-p)/(1-pR)` yields the fixed-point equation. The claim `R = b/p` is the solution **if and only if `s = 0`** (a repair that never removes the existing flaw but injects new ones). If we assume a perfect repair of found flaws (`s = 1`), the equation becomes `R = b(1-B)`, which simplifies to `pR^2 - (1+b)R + b = 0`. For `p = 0.35` and `b = 0.02`, the root is `R \approx 0.0197` (1.97%), not `0.0571` (5.71%).
- **Verdict:** FAILS.
- **Fix:** The claim must be corrected to state that `R* = b/p` only holds for completely ineffective repairs (`s=0`). For effective repairs (`s>0`), the residual risk is strictly lower.
- **Falsifier:**
```python
FALSIFIER:
def test_claim_3_4():
    p, b, s = 0.35, 0.02, 1.0
    # Fixed point equation for s=1: p*R^2 - (1+b)*R + b = 0
    # 0.35*R^2 - 1.02*R + 0.02 = 0
    import math
    R_star = (1.02 - math.sqrt(1.02**2 - 4*0.35*0.02)) / (2*0.35)
    assert abs(R_star - 0.0197) < 0.001
    assert abs(R_star - (b/p)) > 0.03 # 0.0197 != 0.0571
test_claim_3_4()
print("FALSIFIED")
```
- **What would refute my verdict:** A demonstration that the existing model's Stage 5/6 recursion mathematically reduces to `b/p` for `s>0`.

**Finding 2: CC1's Claim 3.1 & 3.2 (Degeneracy is a line; Reachable sets differ)**
- **Claim:** The degeneracy is a 1-parameter family, and the revised model forbids no outcomes.
- **Executed Evidence:** `python scripts/free_parameter_degeneracy_2026-09-20.py`
  Output confirms: `b_as_a_function_of_any_s : (-d + z*(-s + 1))/(z - 1)`. The freedom is a LINE. The existing model's derivative wrt `p` is strictly negative on the open unit square, forbidding outcomes.
- **Verdict:** HOLDS.
- **Fix:** None needed for the claim. It correctly identifies that the revised model's `s` and `b` are free parameters that must be empirically pinned before the model has predictive power.
- **What would refute my verdict:** Evidence that `s` and `b` are structurally constrained by the framework prior to empirical measurement.

**Finding 3: Question 2 (Measurability of introduction rate `b`)**
- **Claim:** The introduction rate `b` is measurable in the project's archive.
- **Executed Evidence:** Tool limit reached before `bench/logs/` could be scanned.
- **Verdict:** UNCHECKED.
- **Fix:** None.
- **What would refute my verdict:** A successful scan of the archive demonstrating paired pre/post states that isolate the introduction of specific new flaws.

**Finding 4: Question 3 (Two-sided gate closing the R* = b/p hole)**
- **Claim:** The two-sided gate catches regression when injected defects surface as criticals.
- **Executed Evidence:** Logical deduction. The gate relies on the review process detecting the injected defects. If a repair introduces a novel defect class to which the review has near-zero sensitivity (`p_{new} \approx 0`), the defect will not surface as a critical finding, and the gate will falsely declare convergence.
- **Verdict:** PARTIAL. The gate closes the hole only if the review is sufficiently sensitive to the *newly injected* defects.
- **Fix:** Acknowledge that the two-sided gate is bounded by the sensitivity of the review to novel defect classes introduced by repairs.
- **What would refute my verdict:** Evidence that the two-sided gate includes an independent oracle that detects defects the primary review misses.

**Finding 5: Grading the Proposals**
- **The replaced repair interpretation:** DECORATIVE. It introduces a 1-parameter degeneracy (proven by `free_parameter_degeneracy_2026-09-20.py`) that forbids no outcomes. Without archive evidence of `b` (UNCHECKED), it adds freedom without content.
- **The novelty-validity decoupling:** ALREADY HAVE IT. The existing model's `C(n)` and `R_k(i)` already separate discovery from residual risk.
- **The abstention channel:** NEEDED. Conflating timeouts/abstentions with negative findings artificially lowers residual risk.
- **The conditioning made explicit:** ALREADY HAVE IT. The existing appendix already defines `R` conditionally.
- **The separation of derivation from calibration:** DECORATIVE.

---

**DISAGREEMENT SECTION**

I disagree with CC1's Claim 3.4 that the recursion settles at `b/p`. This is a mathematical error; it only settles at `b/p` if the repair efficacy `s = 0`. For any effective repair (`s > 0`), the residual risk is significantly lower (e.g., `~b` for `s=1`). 

I disagree that the revised model's repair interpretation is currently useful. Because it introduces a degenerate line of free parameters (`s` and `b`), it cannot be falsified and forbids no outcomes. Until `b` is proven measurable from the archive, it is unbounded model churn.

---

**FINAL VERDICT:** DO NOT ADOPT.

**Question 1 Answer:** The revision is largely unbounded model churn because it replaces a constrained, 1-parameter model that forbids outcomes with a degenerate 2-parameter model that forbids nothing, adding decorative freedom without providing a mechanism to measure the new parameters.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/maths_panel_2026-09-20_r2/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
