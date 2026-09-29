# Blind Panel: The Adaptive Distributed-Compute Specification

Record written 2026-09-29T14:37:36+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

Blind round on the adaptive distributed-compute design specification (2026-09-14), run with the 2 FREE seats only and 0 spend. The brief was written to the locked template after the validator refused a first draft lacking a named instrument, a fix requirement, a delivery path and a termination criterion. Anti-anchor check on the finished brief: the terms naming the already-known defects occur 0 times in it.

The panel reproduced both of CC1's prior findings independently and added 4 more, of which F4 -- that the additive allocation objective is TWO-SIGNED, with its sign boundary floored at RK0_PI_BASE = 0.5 -- was found by cc2 alone, after cc2 refuted its own first version of that claim mid-run.

The round's most valuable output was cc2's stated disagreement with the brief's own framing: the specification transcribed the mathematics CORRECTLY and the canon moved underneath it, so the structural defect is the absence of any mechanism that would detect canon drift in a layer consuming it by reference.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# BLIND REVIEW: the adaptive distributed-compute design specification

## SECTION 1 — The question

**Is the adaptive distributed-compute design specification sound enough to place on this project's runway, and where are its defects?**

Artefact under review, by path:

> `/Users/georgejackson/Developer_Projects/Responses/Codex, ChatGPT & Grok resources/adaptive_distributed_compute_design_spec.md`

624 lines, dated **2026-09-14**. It proposes an allocation and topology layer above CDSFL's canonical model: a task is compiled into a graph of bounded work units, and a scheduler decides which model configuration to dispatch to which unit, scoring candidates by predicted reduction in residual risk per unit of constrained resource. It explicitly claims to CONSUME the canonical mathematics without redefining it.

The founder is deciding whether it is viable, where it belongs on the runway, and whether it earns a paid experiment of its own.

**This is a BLIND round.** You are not being shown anyone else's analysis and you are not being asked whether you agree with anything. Under this project's standing rule, findings are confirmed by programs or by the founder, never by models agreeing with one another. Find what is wrong. If something that looked suspect turns out sound, say that too — a round that returns only complaints has been obliging, not sceptical.

## SECTION 2 — Use the harness

Form your answer by RUNNING the machinery, not by describing it.

**`sigma` and `nu` are the instruments that bear hardest on this question.** The specification's §6.1 writes its own transcription of the three-phase update in terms of `sigma` (fix efficacy) and `nu` (re-injection). The live implementation is `bench/reference_runner_v3.py:compute_rk`. **Call that function and call the specification's §6.1 form on the same inputs, and compare the outputs.** Reading both formulas and judging them similar is not the check; two transcriptions can each be internally consistent and still disagree. What `sigma` and `nu` should tell you is whether the specification's predicted state is the state this project's runner actually produces, across the range of both parameters and not only at their endpoints.

**`S_k` bears on §6.1's closing claim** that a candidate which cannot satisfy an applicable verification gate receives zero verified-risk-reduction credit. `compute_sk` is live. Check whether that claim is consistent with how `S_k = A·E` actually behaves.

**Wilson** governs every proportion you report. Any rate needs an interval, and any computational claim needs two independent tools agreeing.

Also available and expected where they can decide something: SymPy, z3, mpmath, SciPy, statsmodels, NumPy as PRIMARY, with Wolfram through the gate on your PATH as a secondary cross-verification falsifier. Where Wolfram is unavailable to you, fall back to the open-source set.

**Check the dates.** `docs/MATHEMATICAL_APPENDIX.md` was revised after 2026-09-14. `git log` on it is available to you and is evidence.

## SECTION 3 — Produce a fix, and test it

A finding without a fix is half an answer. A fix without a falsifier you have EXECUTED is a hypothesis.

Report the exact command you ran and the output you saw.

**Deliver every fix as a file, written INTO the sandbox repository tree at a real path.** A fix described in prose is not delivered, and a fix written to scratch space is destroyed when the sandbox is torn down.

- A defect in **this project's own code or documents** — fix it at its real path (`docs/MATHEMATICAL_APPENDIX.md`, `bench/...`, `scripts/...`).
- A defect in **the specification** — the specification lives outside the repository, so deliver the corrected passage to `experimental_notes/panel_fixes_adaptive_spec_2026-09-29/<your-seat-name>.md`, quoting the original text and giving the replacement, with the section number.
- A falsifier you write goes to `scripts/` with a dated name and must run.

## SECTION 4 — What would refute you

Before you conclude, state for each finding what evidence would overturn it. A verdict with no stated refutation condition is an opinion.

This applies to your own measurements. **If you measure a rate by sampling a parameter space, the number is a property of your sampling distribution as much as of the thing measured.** State the distribution you sampled from, and say whether the operationally relevant distribution is known. If it is not, say so rather than letting an assumed prior stand in for it.

## SECTION 5 — Output shape

Per finding:

- **claim** — stated so it could be wrong;
- **section** — where in the specification it bites;
- **evidence** — the command run and its output, verbatim;
- **verdict** — HOLDS, PARTIAL or REFUTED;
- **fix** — the path you wrote it to;
- **falsifier** — the command, and its executed result;
- **what would refute me**.

Then, once:

- **what I did NOT check**, named explicitly;
- **where I could not decide**, and why;
- **my strongest disagreement with this brief's own framing.**

## SECTION 6 — Termination

Stop on diminishing returns: when a further pass produces no new finding above the threshold of real-world consequence. **State how many passes you ran.**

Four areas are UNEXAMINED by any prior assessment — not cleared, unexamined — and are the most likely place for a new finding:

1. **The cost, latency and human-burden model** (§6.4): `λ_t`, `λ_h`, `β`, and the exploration term `e_mu = sqrt(log(1+N_u)/(1+n_mu))`. Is it well-posed? Are the units coherent? What happens at `N_u = 0`?
2. **Whether the task compiler is buildable** (§4.1, §7.1 step 2): it must produce a work graph, validate acyclicity, prove coverage of HARD constraints and assign interface ownership. Specification, or wish?
3. **Sample-size adequacy** (§9.3): a staged curve at 1, 2, 4, 8, 16, 32 workers, "at least three independently seeded runs per condition", six control conditions. What power does that design actually have?
4. **Whether the promotion gates are checkable** (§9.4): Library → Shadow → Controlled live → Operational. Could a program evaluate each gate's criterion, or does it need a judgement the document never specifies?

## Constraints

You are in a sandbox copy. Do not attempt to modify the canonical tree. Spend nothing. Dispatch no models.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 32 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel adaptive_spec_blind_2026-09-29) -->

## VERDICT

**The specification is sound enough for the runway, at Phase B.** Its mathematical discipline is real: it refuses to redefine the canonical model, pre-registers genuinely disconfirming rules (§12), and correctly shelves `_load_balancer.py`. Six defects bite; five are in §6. Two are load-bearing. None is fatal. **It earns a paid experiment — Phase D, not Phase E.**

**4 passes run.** Pass 3 refuted one of my own claims (below). Pass 5 produced nothing above threshold.

Producer for every number: `scripts/adaptive_spec_falsifiers_2026-09-29.py` — 9 checks, all executed, check 7 a control that HELD.

---

### F1 — §6.1 writes `ν̂` as a free parameter; `compute_rk` derives it from `σ`

**claim** No constant `ν̂` reproduces the live runner across `σ`, because `nu_eff = 1-(1-nu_b)(1-(1-sk)nu_f)` is a *function of* `sk` — and `sk` is the same slot as `σ` (runner's comment: *"Phase 2: Resolution (S_k replaces sigma)"*).

**evidence**
```
 sigma  runner compute_rk  nu_eff implied
  0.00           0.620000        0.240000
  1.00           0.441176        0.050000
nu_eff spread over sigma in [0,1]: 0.190000
best constant nu_hat = 0.1375, sup|spec-runner| = 0.051471
```
**verdict HOLDS.** The spec's parameter space is larger than the reachable set, and it drops the coupling that makes a weak fix doubly penalised — so it **over-rewards low-`σ̂` candidates**.
**fix** `experimental_notes/panel_fixes_adaptive_spec_2026-09-29/opus-blind-seat.md` FIX 1.
**what would refute me** A caller that passes `nu_b`, `nu_f` per configuration rather than as policy constants; or a ruling that `ν̂` is a *forecast of* `nu_eff` rather than an independent estimate.

---

### F2 — §6.1's "zero verified-risk-reduction credit" is **negative** credit in its own formula

**claim** Substituting `σ=0` into §6.1's own `R_next` gives `g = ν(R−1) < 0` — a penalty, not zero.

**evidence** SymPy → `nu*(R - 1)`. z3 on `g ≥ 0` anywhere in `(0,1)³` → **unsat**. Wolfram `Reduce` → **False** (*computed with Wolfram Language*).
```
runner compute_rk(0.5, 0.30, sk=0.0) = 0.620000   g = -0.120000
live REJECTED  apply_sk_to_rk        = 0.500000  <- R_k unchanged
live NO_SCORE  apply_sk_to_rk        = 0.500000  <- "zero MOVEMENT, not a zero SCORE"
```
**verdict HOLDS.** The runner avoids the penalty only by **never calling `compute_rk`** on a non-admissible outcome. The spec conflates three states the runner keeps distinct, and — worse — never links `σ̂` to `S_k`, so a candidate whose gate product will be 0 can carry `σ̂=0.9` and win the dispatch. **The "hard qualification boundary" has no formal expression in the score.**
**fix** FIX 2 — carry the tri-state; move the exclusion into §6.5's `x_mu=0` constraint where a program can check it.
**what would refute me** A reading of "credit" as a reporting ledger rather than as `g`. But §6.4 consumes `g`, so the score is still unguarded.

---

### F3 — §6.1/§6.4 rank candidates on the wrong branch quantity, and it **inverts orderings**

**claim** `g = R − R_next` is the negative-branch blend `A`; a dispatch is chosen *before* the branch is known, so the decision quantity is `M = R(1−qσ)` (`compute_rk_expectation`). Because `A − M = σqR²(1−q)/(1−qR)` depends on `(q,σ)`, the substitution is not rank-preserving.

**evidence**
```
strictly-ordered pairs : 64979
ranking inversions     : 1537
inversion rate         : 2.3654%  Wilson 95% [2.2513%, 2.4851%]
m1=(q=0.05,σ=0.10): g_A=-0.109501  g_M=-0.108553
m2=(q=0.35,σ=0.05): g_A=-0.111169  g_M=-0.108517
spec §6.4 dispatches m1; pre-branch expectation prefers m2
z3: exists a point with A < M -> unsat
```
Wolfram: `Resolve[ForAll[...], A − M ≥ 0] → True` (*computed with Wolfram Language*).

**Sampling distribution, stated:** uniform on `q,σ ∈ {0.05,…,0.95}` (19×19), `R=0.5`, shipped `ν`. **Not** the operational distribution, which is unknown. The rate is a property of this grid.

**verdict HOLDS — and the spec is not culpable.** `git log docs/MATHEMATICAL_APPENDIX.md` shows **7 commits after 2026-09-14**, two on this exact quantity: `d6eeb90 2026-09-29 "explorer A-vs-M"` and `b509a44 2026-09-21 "I attacked the maths model's Phase 2 and lost"`. **The appendix moved under the spec, on the one equation it depends on most.** That is the real cost of consuming a live model by reference.
**fix** FIX 3 (rank on `M`, report both, gate on neither) **plus** a repo-side additive entry at `docs/MATHEMATICAL_APPENDIX.md:270` — the appendix already says `A` is wrong for a *stopping* decision and nowhere says it is wrong for a *routing* decision. No gate or shipped number changes.
**what would refute me** A demonstration that the operational `(q,σ)` distribution is concentrated where the inversion set is empty; or a ruling that gate-compatibility requires `A` for routing too.

---

### F4 — §6.5's objective does what §6.7.1 forbids, and the bias is **two-signed**

**claim** With `r_u ∈ {2,3}` the objective sums gains of configurations on the *same* unit. The update composes multiplicatively in the **odds**, so the true joint gain is the single-pass gain at `q_eff`.

**PASS 3 REFUTED MY FIRST VERSION OF THIS.** I claimed the sum always overstates. Wolfram: `Resolve[ForAll[..., gap > 0]] → **False**`. Repaired by deriving the exact boundary:

**evidence**
```
SymPy: T(T(R,q1),q2) - T(R, 1-(1-q1)(1-q2)) = 0        <- odds composition, exact
sign boundary R* = (1-sqrt(1-q_eff))/q_eff   limits: 1/2 -> 1;  gap at R=R* : 0
R=1/2 (== RK0_PI_BASE): g1+g2 = 1/3, g_joint = 3/10  -> OVERSTATES 11.11%
R=9/10 (above R*=2/3): 0.163636 vs 0.207692          -> UNDERSTATES 21.21%
z3: any point with R<=1/2 failing to overstate -> unsat
z3: any point at all where it understates      -> sat
grid {0.05..0.95}^3: overstates 71.35% Wilson [70.27%, 72.41%]; understates 28.65%
LIVE, §6.2's own numbers: g_A+g_B=0.188661 vs joint 0.173507  -> +8.73%
```
Wolfram confirmed `gap>0` for all `R ≤ 1/2` → **True** (*computed with Wolfram Language*).

**verdict HOLDS (sharper than claimed).** `RK0_PI_BASE = 0.5` sits **exactly on the boundary's floor**, so an additive allocator over-buys redundancy early and under-buys it on units that accrued risk through re-injection. A two-signed bias is worse than one-signed: it cannot be treated as a conservative bound.
**fix** FIX 4 — compose over the selected set; add the overlap relation as a **solver constraint** so §6.7.1 is enforced, not remembered. Greedy survives: the composed form is still submodular at fixed `R`.
**what would refute me** A ruling that `r_u ≥ 2` always means *distinct claim surfaces* — but then §6.7.1's overlap clause has nothing to forbid.

---

### F5 — §6.4: exploration is **off** when uncertainty is greatest; the score is unit-dependent

**claim (a)** `e_mu = sqrt(log(1+N_u)/(1+n_mu))` is identically 0 at `N_u=0`. **(b)** `score = g/D + βe` is not invariant under a change of cost unit.

**evidence**
```
N_u=   0   n=0:0.0000  n=1:0.0000  n=5:0.0000
e_mu == 0 for EVERY n_mu when N_u=0 : True
β=0.0010 : dollars picks A (0.020560 vs 0.016482); cents picks B (0.000760 vs 0.001632) -> flip=True
β=0.1000 : dollars picks B; cents picks B -> flip=False
EXACT flip band for this pair: beta in (0.000054, 0.005423)
dollars-vs-cents ranking flips: 44782 / 200000 = 22.39% Wilson 95% [22.21%, 22.57%]
```
**verdict (a) HOLDS. (b) PARTIAL** — my first instance (`β=0.10`) did **not** flip; the flip is a ~100-fold band in `β` whose *location* moves with the currency unit. **Sampling distribution, stated:** `g~U(0.001,0.05)`, `D~U(0.05,5.0)`, `n~U{0..19}`, `N_u~U{1..49}`, `β~log-uniform(1e-4,1)`, 200 000 draws, seed 20260929. **That is my prior, not the operational one.** The qualitative point is unit-analytic and survives any box: `β` silently carries units of risk-per-currency, and §6.4 says fix it before a run without saying in what.

On (a): a never-tried configuration (`n=0`) and a saturated one (`n=49`) get **the same bonus: zero** — precisely when §6.3 says the intervals are widest. Standard UCB either keeps a global count ≥1 or forces one pull per arm; this has neither.
**fix** FIX 5 — move the bonus into the **numerator** (one unit for the whole score), use `log(2+N_u)`, and add the property test `e(N=0,n=0) > e(N=0,n=49)`, which the specified form fails.
**what would refute me** For (a): an initialisation convention setting `N_u ≥ 1`. For (b): a policy declaring `β` in risk-per-currency with the currency pinned.

---

### F6 — §9.2/§9.3 cannot resolve the difference they are built to test; §9.4's live gates are not program-evaluable

**evidence** (statsmodels `TTestIndPower`, two-sample t, α=0.05)
```
 n/arm  power@d=0.8  power@d=1.5  min detectable d @80%
     3       0.1193       0.2932                  3.071
    20       0.6934       0.9961                  0.909
Bonferroni α=0.05/15 (6 conditions -> 15 comparisons) at n=3 : d = 6.401
SE(V_n - V_(n-1)) at 3 runs/arm = 0.8165*sigma; sign undetermined below 1.600*sigma
§9.4: program-evaluable gates: 2 of 4
'threshold' appears 4 times; NUMERIC values attached: 0
§4.2 compiler: DECIDABLE 3 of 5; requiring an unspecified oracle 2 of 5
     ("entail" 0 occurrences, "decidab" 0 occurrences in 624 lines)
```
**verdict HOLDS.** §9.2 says three runs are needed *"before comparing small differences"* — **three runs cannot compare small differences at all**. And the two gates that authorise going live are the two with no predicate: "matched-budget improvement" names no statistic, threshold or interval; "replicated benefit" has no `k`. Deferring thresholds is legitimate in a design brief; presenting them in a table headed *"Promotion evidence"* is not.
**fix** FIX 6 — pre-register effect size, `n`, multiplicity and the variance estimate's provenance; report `MarginalVerifiedYield` with an interval; make each gate a predicate over stored artefacts.
**what would refute me** A named variance estimate from archived runs showing the real effect is `d > 3`. That would also mean the comparison is not close and the panel question is already settled.

---

## SOUND — recorded because a round of only complaints has been obliging, not sceptical

1. **§6.2's arithmetic is exact.** `257/400 = 0.6425`, marginal `77/400 = 0.1925`, in SymPy rationals. The marginal-gain principle it illustrates is the right one.
2. **§6.3's refusal to manufacture a scalar correlation correction is correct** and matches the appendix's own Ising branch and its stated data-hunger.
3. **§6.6 is honestly hedged** — submodularity claimed for `D_u(n)`, no global optimisation guarantee claimed for the full objective.
4. **The task compiler is buildable for 3 of its 5 obligations, and I implemented each to confirm it**: Kahn separates a DAG from a cycle, dangling deps are set membership, interface ownership is an arity check. It is a specification for three fifths and a wish for two fifths — a scoping problem, not a fatal one.
5. **§10's ruling on `_load_balancer.py` is correct** and consistent with the additive standard: shelved, not live, replacement with committed invariants.
6. **§12 is the best part of the document.** Rule 2 concedes the scheduler in advance if the flat panel is not beaten at matched budget.

---

## What I did NOT check, named

§3/§5 topology diagrams for feasibility; §4.3 `EvidencePacket` against the live `bench/dm/` packet builders; §4.4's forbidden transitions as a reachability property; §8's 10 invariants individually (I classified them as property-testable, I did not write the properties); §6.3's Ising normalisation `Z` and whether `ψ_ab` is identifiable at panel sizes ≤ 32; whether `D(n)` as the spec writes it matches `bench/DISTRIBUTED_COMPUTE_PROTOCOL.md`; §11's Phase-A dependency on Exp 56; the full test suite (instructed not to).

## Where I could not decide

**The operational distribution over `(q, σ, R)`.** Every rate I report — 2.37%, 71.35%, 22.39% — is a property of a grid or box I chose. `RK0_PI_BASE = 0.5` is the one operationally pinned value, and it happens to sit at the floor of F4's sign boundary, which is why I lean on it rather than on the grid. Whether F3's 2.37% is 0% or 40% in practice is **undecided**, and I decline to let my flat prior stand in for it. F3's *existence* is derived; its *rate* is not.

**Whether F2 is a defect or a wording gap.** If "credit" means only the reporting ledger, the sentence is defensible. §6.4 consumes `g`, so the score is unguarded either way — but the severity differs and I cannot settle which reading the author intended.

## My strongest disagreement with this brief's framing

The brief directs me to check whether §6.1's transcription matches `compute_rk` — and it does not, which is F1. But **that framing understates the problem by treating the canonical model as a fixed target.** `git log` shows the appendix changed **7 times in the 15 days after the spec was written**, twice on the exact quantity §6.1 transcribes. So F3 is not a transcription error at all: the spec transcribed correctly and the canon moved. Asking "does the spec match the runner?" produces a finding against the spec when the structural defect is in the **coupling**: a layer that declares it "CONSUMES the canonical mathematics without redefining it" has silently taken on the canon's revision rate as a dependency, and neither document names the mechanism that would catch it. The cheap mitigation is one line in §6.1 — pin the consumed appendix by commit hash and execute the transcription against `compute_rk` in CI, so the next appendix revision breaks a test instead of quietly invalidating a scheduler. I would rather the founder buy that line than any of my other five fixes.

---

**Delivered (sandbox tree, real paths):**
- `scripts/adaptive_spec_falsifiers_2026-09-29.py` — 9 checks, runs, exit 0, prints `FALSIFIED`
- `experimental_notes/panel_fixes_adaptive_spec_2026-09-29/opus-blind-seat.md` — 447 lines, 6 fixes with original + replacement text per section
- `docs/MATHEMATICAL_APPENDIX.md:270` — additive entry: the A-vs-M gap breaks a *ranking*, not only a level

**Regression:** `python3 -m pytest bench/tests/test_rk_expectation_companion_2026-09-29.py bench/tests/test_explorer_branch_table_2026-09-29.py -q` → `32 passed in 2.96s`. Nothing removed, nothing disabled. Wolfram computed on all four calls (local kernel, exit 0, `Out` values present, no `Name::tag`, no `$Failed`).

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 24 recorded tool call(s).

<!-- verbatim-begin: fable (panel adaptive_spec_blind_2026-09-29) -->

All cross-checks agree (scipy noncentral-t power 0.7989 ≈ 0.8 at d = 3.0662, n = 3; hand-Wilson ≡ statsmodels). Final report.

---

# BLIND REVIEW — adaptive distributed-compute design spec (2026-09-14)

**Verdict on the question asked:** The specification is **sound in architecture and discipline, and defective in its mathematical transcriptions at exactly the points it claims to consume the canonical model**. It earns a place on the runway at **Phase B (substrate) only**, and it does **not** earn a paid experiment until §6.1 and §6.4 are repaired — because the scheduler's scoring core, as written, predicts a state the runner does not produce and ranks by a quantity the project's own appendix has since ruled wrong for pre-dispatch decisions. All fixes are delivered and all falsifiers executed.

**Note on blindness:** canonical commit `ea43d3f` (today) contains the founder's own assessment of this spec. I used the canonical git history for **dates only** and did not read that assessment.

## Findings

### F-1 — §6.1's re-injection phase is not the operational update law it claims to consume — **HOLDS**

- **claim:** The spec's `R_next = [σ̂R_det + (1−σ̂)R](1−ν̂) + ν̂` with a free per-configuration ν̂ cannot reproduce `compute_rk`, whose ν_eff = 1−(1−ν_b)(1−(1−S_k)ν_f) is **coupled to fix efficacy** (`cdsfl_operational.md` §3 lines 159–165 — the operational law).
- **evidence:** `python3 scripts/panel_adaptive_spec_falsifiers_2026-09-29.py` → `F1a max |diff| = 0.00e+00` when ν̂=ν_eff(σ) (the forms are algebraically identical then); `F1b best constant nu-hat=0.14, max |diff|=0.0736; |diff|>0.01 at 522/729 grid pts (rate 0.716, Wilson95 [0.682,0.748])`. SymPy: spec−runner = (ν̂−ν_eff)(1−R_base); Wolfram Language returned `0` for the same difference (local kernel, exit 0). Sub-defect: spec form is 0/0 at q̂R=1; `compute_rk` guards it (F1d).
- **fix:** `experimental_notes/panel_fixes_adaptive_spec_2026-09-29/fable.md` Fix 1.
- **falsifier:** the script above; exit 0, all 16 checks reproduced.
- **what would refute me:** a passage in the spec (I found none; §6.7.5 treats σ and ν as separately fit) declaring ν̂_muk to be an estimator of ν_eff(σ̂) with the (ν_b, ν_f, σ̂) functional form and the ν_b+ν_f≤1 rescaling; or a founder ruling that the appendix's plain-ν Stage 5 form, not the runner's bounded form, is the layer schedulers must predict.

### F-2 — §6.1's closing S_k claim ("zero credit") contradicts the shipped tri-state — **HOLDS**

- **claim:** A candidate failing an **applicable** gate receives **negative** credit, not zero: only NO_SCORE (no applicable gate) is zero movement.
- **evidence:** `F2: gate-failed: R 0.5 -> 0.6200 (credit -0.1200, NEGATIVE); NO_SCORE: R 0.5 -> 0.5000 (credit exactly 0)` — run against shipped `compute_rk` and `apply_sk_to_rk`, whose docstring makes the distinction the A2 design point. A scheduler crediting zero under-penalises configurations that produce inadmissible fixes and will over-dispatch them.
- **fix:** fable.md Fix 2. **falsifier:** F2, executed above.
- **what would refute me:** evidence that the intended dispatch flow never applies the R_k update to a gate-failed candidate (i.e. REJECTED never reaches `compute_rk` with sk=0 in the operational runner) — I did not trace every call path; if REJECTED is also zero-movement in practice, the finding downgrades to a wording defect.

### F-3 — §6.1's routing estimator uses the gate's conditional blend where the canonical maths (revised *after* the spec) requires the pre-branch expectation — **HOLDS**

- **claim:** g_muk = R − R_next(blend) is the wrong decision quantity for choosing a dispatch *before* the outcome branch is known; the appendix entries of 2026-09-21/2026-09-29 and shipped `compute_rk_expectation` ("the quantity an explorer needs BEFORE a run") establish E[improvement] = Rq̂σ̂(1−ν̂_eff) − ν̂_eff(1−R) as the correct one. This is a **dating** defect: the spec (09-14) predates the ruling (`git log docs/MATHEMATICAL_APPENDIX.md`: `8a0952a 2026-09-18`, `b509a44…0a4a491 2026-09-21`, `ea43d3f 2026-09-29`).
- **evidence (all against shipped functions):** `F3c` conditional gain at R=0.99, q=0.3 is 0.004225 vs expectation 0.2970 — **70.3×** understatement, reproducing the appendix's figures; premature-stop band bites §7.1 step 9. `F3a` ranking reversal at R=0.9: spec's g prefers X(q=.9,σ=.4) 0.1262>0.0509, expectation prefers Y(q=.5,σ=.8) 0.3195>0.2545. SymPy+Wolfram: blend-gain = σqR(1−R)/(1−qR) (ranks by σq/(1−qR)), expectation-gain = Rqσ (ranks by σq). `F3b` reversal rate 619/20000 = **3.09%**, Wilson95 [2.86%, 3.34%] — under a **uniform** draw on (R,q,σ)²; the operationally relevant distribution is unknown, and reversals concentrate at high R, where dispatch matters most.
- **fix:** fable.md Fix 3. **falsifier:** F3a–c, executed.
- **what would refute me:** a founder ruling that the router must predict the *recorded* (gated) state rather than the decision-theoretic expectation — that would make the spec self-consistent but would re-import the premature-stop pathology the appendix documents; or a demonstration that under the operational (R,q,σ) distribution reversal probability is negligible *and* stopping decisions never occur above R\*.

### F-4 — §6.4's dispatch policy is not well-posed — **HOLDS**

- **claim:** (a) e_mu = √(log(1+N_u)/(1+n_mu)) is identically **0 at N_u=0** — zero exploration exactly at maximum ignorance; (b) score → ∞ as denominator → 0 (no cost floor); (c) units incoherent: g/(money) plus a dimensionless βe requires β to carry [risk-reduction/money], unstated.
- **evidence:** `F4a e_mu at N_u=0: [0.0, 0.0, 0.0]`; `F4b scores at c=1e-3,1e-6,1e-9: [100.0, 1e5, 1e8]`. Units defect is derivational: λ_t, λ_h convert t, h to money, so denominator is money; numerator dimensionless risk-reduction; βe added to a [1/money] ratio.
- **fix:** fable.md Fix 4 (bonus into the numerator, declared c_floor, cold-start-positive e_mu, published units for λ_t, λ_h, β). **falsifier:** F4a/F4b, executed.
- **what would refute me:** a reading of N_u under which the first allocation already makes N_u≥1 for *scoring* purposes before any m is chosen (the spec says "completed allocations", so no); for (c), a published units convention elsewhere in the spec — there is none.

### F-5 — §9.3's design has power only for enormous effects — **PARTIAL**

- **claim:** n=3 per condition ⇒ minimum detectable effect **d ≈ 3.07** (α=.05, power .8), **d ≈ 4.80** Bonferroni-corrected over the 5 control comparisons; a 3/3 proportion carries Wilson95 [0.439, 1.000]. "At least three runs … before comparing small differences" installs a floor that will be read as adequacy; small differences need n ≈ 17–23 per condition at d=1.
- **evidence:** `F5a MDE = 3.07; Bonferroni d = 4.80`; cross-verified independently: scipy noncentral-t power at d=3.0662, n=3 → **0.7989**; hand-Wilson ≡ statsmodels `(0.4385, 1.0)`. PARTIAL because the spec says "at least" and never claims adequacy — the defect is the absent MDE statement, not a false one.
- **fix:** fable.md Fix 5. **falsifier:** F5a/F5b + the scipy cross-check, executed.
- **what would refute me:** a pre-registered analysis plan elsewhere in the programme specifying per-condition n from an expected effect size — none exists in the document.

### F-6 — §9.4: two of four promotion gates are not machine-checkable — **PARTIAL**

- **claim:** Library and the invariant halves of Shadow/Controlled-live are programmatically evaluable; "counterfactual comparison", "matched-budget improvement" and "replicated benefit" name no metric, threshold, replication count, or test — a program cannot return PASS/FAIL on them.
- **evidence:** textual; §9.1/§9.3 supply usable statistics (primary outcome, MarginalVerifiedYield) that §9.4 never binds to the gates.
- **fix:** fable.md Fix 6 (concrete criteria binding each gate to §9.1/§9.3 statistics with pre-frozen thresholds). **falsifier:** none executable against prose; the fix's criteria are themselves programmatic, which is the point.
- **what would refute me:** any sentence in the spec binding a gate to a named statistic and threshold. §9.3's "pre-registered criterion is met" comes closest but names no criterion.

### F-7 — §4.1: the task compiler is buildable as a **validator**, not as the **prover** the text implies — **PARTIAL**

- **claim:** Acyclicity, dependency closure, interface ownership, hashing: mechanical. "Checked for coverage of HARD constraints" is decidable only as a syntactic mapping (h ∈ H ↦ ≥1 unit); whether a unit's oracle actually tests h has no oracle in the document; and the duplication check has no admissible identity mechanism, given §8 invariant 8 prohibits lexical similarity alone.
- **evidence:** textual analysis of §4.1/§4.2/§8; no counter-passage defines "coverage" or the identity mechanism for *proposed* units.
- **fix:** fable.md Fix 7 (syntactic-coverage wording, REFUSE-to-dispatch on uncovered constraints, §8-invariant-8 identity for dedup). **what would refute me:** a definition of constraint coverage or unit identity anywhere in the spec.

### Sound, and said so

- **§6.2 D(n)** is a faithful transcription of PAPER.md Part XIII's general multi-class form, worked example exact (`F6`: 257/400 = 0.6425, increment 77/400 = 0.1925, Fraction arithmetic); the conditional-increment Δ(m|A) is the right generalisation of Part XIII's marginal gain. (The appendix's Part XII extension adds an o_ik overlap matrix, in place since 2026-03-19; the spec's §6.3 handles correlation separately and correctly, so this is presentation, not defect.)
- **§6.3 Ising transcription** matches appendix §0.1 term for term; the f_a rename *avoids* the appendix's own overload of q (failure prob in §0.1 vs detection operationally). Refusing early ψ fitting is consistent with the appendix's n≥3 normalisation finding.
- **q̂ = η̂d̂p̂** matches `compute_rk_with_eta_channel` (q = η_combined·d·p), and the ban on a second novelty multiplier matches the m_div-on-η_int-only channel rule.
- **§6.6** correctly claims submodularity only for fixed-event coverage; **§6.5/§10** feasibility-refusal and load-balancer reading match the additive standard and the shelving record.

## What I did NOT check

The §4.3/§4.4 state machine against `bench/dm` vocabulary; §8 invariants 7–10 against existing provenance machinery; §5.2's diversity-vector calibration claims; whether §9.2's six conditions are mutually confounded; every call path by which SK_REJECTED reaches (or does not reach) `compute_rk` (bears on F-2's severity); the full test suite (prohibited); Exp 56 scope-boundary appropriateness.

## Where I could not decide

Whether F-3 is a defect *in the spec* or a spec-appendix **race**: the spec was arguably correct on 2026-09-14 under the then-current appendix gloss, and the appendix moved under it on 09-21/09-29. The defect is real either way — the document on the runway today mis-specifies the router — but attribution (author error vs. canonical drift) is the founder's call. Also: the operational (R, q, σ) distribution is unknown, so my 3.09% reversal rate and 71.6% mispredict rate are properties of uniform sampling, not of production traffic.

## Strongest disagreement with the brief's framing

The brief directs the σ/ν comparison as if the spec's transcription might disagree with `compute_rk` *pointwise as formulas*. It doesn't — with ν̂ bound to ν_eff(σ̂) they are the same function to 0.0 (F1a, SymPy, Wolfram). The real defect is **parametric**, not algebraic: the spec frees a parameter the runner couples. A panel that only diffed outputs at matched parameters would have declared them identical and missed the finding; a panel that only read the formulas would have called them different and overstated it. The instrument that decided was the *calibration* question — can any constant ν̂ track ν_eff(σ)? (No: max error 0.0736.) Secondly: the brief's "Wilson governs every proportion" is right but insufficient here — the binding caveat on my rates is the unknown sampling distribution, which no interval repairs.

## Termination

**3 passes.** Pass 1: spec, runner, operational directives, appendix + its post-09-14 history. Pass 2: executed falsifiers (16 checks, exit 0; SymPy + Wolfram + scipy/statsmodels cross-checks). Pass 3: sweep of §4.4, §6.5, §8, §9.1, §12–14 produced nothing above the material threshold (worst candidates: MarginalVerifiedYield's C_n−C_{n−1}=0 division; TOOL_REFUTED's路径 through INTEGRATION_CHECK — both below consequence threshold). Converged: no new material finding in pass 3; declared per §10 with the evidence above, refutable by the runner's independent re-execution of `scripts/panel_adaptive_spec_falsifiers_2026-09-29.py`.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/adaptive_spec_blind_2026-09-29/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
