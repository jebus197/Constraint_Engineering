# Full record — free panel round, Phase 2 and the scorer repair, 21 September 2026

21 September 2026 02:00 BST (Europe/London). Generated 2026-09-21T01:58:47+01:00.

**Why this file exists.** The founder's standing directive: *"All P-pass results, external reviews (human or machine), and both potential and actual adversarial findings, must be presented in full and in unfiltered format ... Never summarise in place of the full output."* Both seat replies are reproduced below in their entirety, unedited.

**What this round was.** A 2-seat FREE panel — `cc2` and `fable`, both on the founder's Max subscription, dispatched with `PANEL_ONLY=cc2,fable`. **No paid seat ran and no money was spent.** The founder was asleep; the £12 ceiling for the maths review is untouched by this round.

**The question put to them.** CC1 had proposed that the appendix's Phase 2 wrongly reverts to the prior at σ = 0, discarding the evidence that produced `R_det`. The brief carried that position explicitly and invited attack on it. It also asked the seats to try to break the `e1_efficacy` scorer repair committed earlier the same night, and to answer the founder's own question about whether the review amounts to corrections and qualifications.

**The outcome, in one line.** Both seats refuted CC1 independently, by different derivations, in a single round. The appendix is right: reverting to the prior is the tower property, not a discard. And fable found a defect in CC1's scorer repair — it paid for destroying the instrument — which has since been fixed.

**Where the raw record lives.** `bench/logs/maths_panel_2026-09-21_phase2`, mirrored at `experimental_notes/evidence/panel_records_2026-09-21/maths_panel_2026-09-21_phase2`. The brief is `BRIEF.md` in that directory; seat-written files are under `sandbox_harvest`, and their proposed edits are in `seat_proposals.diff`, untested and not applied.


---

## Seat `cc2` — verbatim, 18314 characters, 30 tool calls, route `claude_cli`

<!-- verbatim-begin: cc2 -->

All evidence in. Writing my verdict.

---

# CC-free-seat — verdict

Repo: `/private/var/folders/.../cdsfl_panel_wccy85lb/repo`. All commands run from repo root. Tools used: SymPy 1.14.0, z3, NumPy 2.4.4, mpmath@40dps, pytest, and Wolfram Engine as second falsifier (local `wolframscript`, exit 0, `Out` values present, no `Name::tag`, no `$Failed` — **valid** evidence, attributed to Wolfram Language below).

---

## F1 — THE QUESTION. The appendix is right. CC1 is wrong, and wrong twice.

**Claim.** Phase 2's revert-to-prior at σ=0 is not a conflation. It is the *only* value consistent with the generative model the appendix has already committed to, and CC1's revision 1.1 violates conservation of expected evidence at σ=0 and asserts zero residual risk at σ=1.

The brief's own script ends: *"whether reverting to the prior at sigma = 0 is CORRECT … no amount of algebra decides it."* That is true of algebra **comparing the two maps**. It is not true of a derivation **from the generative model**. That is the gap I closed.

**The derivation.** `R_det = R_old(1−q)/(1−q·R_old)` is only the posterior if `P(detect|flaw)=q` and `P(detect|¬flaw)=0`. Those same assumptions force a **second branch** that the appendix never names:

| branch | probability | posterior | fix? | risk after |
|---|---|---|---|---|
| no detection | 1−q·R_old | R_det | none attempted — nothing was found | R_det |
| detection | q·R_old | **1** (no false positives) | resolves w.p. σ | 1−σ |

Mixture `= (1−q·R_old)·R_det + q·R_old·(1−σ) = R_old·(1−q·σ)`. **At σ=0 that is exactly R_old.**

CC1's premise — "the evidence still happened, a failed fix does not un-observe the pass" — is correct and is *precisely why* the answer is R_old. The observation happened on **both** branches. Sometimes it says "clean" (risk falls to R_det); sometimes it says "flaw found" (risk rises to 1). Unrepaired, those average back to R_old. That is the tower property, `E[posterior] = prior`. The appendix does not discard the observation; **CC1's revision discards the unfavourable half of it**, keeping only the branch where nothing was found.

```
$ python3 scripts/cc_free_seat_2026_09_21/f1_two_branch_derivation.py
   E[risk after resolution] = -R_old*(q*sigma - 1)      [= R_old*(1-q*sigma), SymPy residual 0]
   mixture at sigma=0        = R_old
   E[posterior over both branches] = R_old
   revision at sigma=0, nu=0 = R_old*(q - 1)/(R_old*q - 1)
   deficit vs conservation   = R_old*q*(R_old - 1)/(R_old*q - 1)
   revision at sigma=1, nu=0 = 0
ALL ASSERTIONS PASSED.
```

**The second, larger defect.** At σ=1, ν=0 the revision returns **identically 0** — for every z, q, R_old. One successful fix asserts *certainty of no residual risk*. That contradicts the appendix's own substrate ceiling (`lim R ≥ ν_k`; `lim R = π_risk,k` when capability is absent). CC1's brief does not mention this endpoint.

**Cross-verified, 3 independent tools.**
```
$ python3 scripts/cc_free_seat_2026_09_21/f2_z3_crosscheck.py
  C3 revision at sigma=0 is STRICTLY BELOW R_old (nu=0)      UNSAT -> HOLDS
  C4 revision at sigma=1,nu=0 is exactly 0                   UNSAT -> HOLDS
  C5 appendix NEVER understates risk vs exact marginal       UNSAT -> HOLDS
7/7 claims UNSAT-confirmed by z3.
```
Wolfram Language (local engine): `mixture=R - q*R*s`, `equals R(1-q s)? True`, `at s=0: R`, `revision at s=1,nu=0: 0`. Independent agreement.

**Executed on the shipped code** (Section 3's requirement):
```
$ python3 scripts/cc_free_seat_2026_09_21/f4_run_the_real_recursion.py
   R_old=0.5 q=0.7: compute_rk=0.500000000000 ... -> reverts to prior: True
   CONFIRMED IN CODE: the implementation reverts to the prior at sk=0.
```

**Verdict: HOLDS** (appendix correct). **CC1's proposed revision: FAILS.**

**Fix.** Do not change the equation. Change the *justification*, which is what invited the error — delivered at `scripts/cc_free_seat_2026_09_21/PATCH_appendix_phase2_and_floor.md`, Correction 1. Zero new parameters.

**What would refute me.** Show that R in this framework is a *trajectory-conditional* belief rather than an expectation over branches — i.e. that the cycle is only ever entered **after** a detection has occurred. Then branch B has probability 1, the post-detection posterior is 1, and the correct σ=0 value is 1, not R_old *and not R_det*. That refutes the appendix **and** CC1 together, and CC1's revision would still be the furthest from right. I checked this reading and rejected it: it makes Phase 1's `R_det` unreachable, since `R_det` is by construction the *non*-detection posterior.

---

## F2 — Where the appendix *is* approximate (and it is the safe direction)

**Claim.** Phase 2 interpolates between a quantity conditional on non-detection (σ=1) and a marginal expectation (σ=0). Those are different measures, so it is not exact except at σ=0. This is a real conflation — but not the one CC1 named, and it is harmless in direction.

`appendix − exact = σ·q·R_old²(1−q)/(1−q·R_old) ≥ 0`, UNSAT-confirmed by z3 across the cube; the shipped `compute_rk` never understated the exact mixture across 20,000 sampled points. **The composite always overstates risk.** For a safety gate that is the correct bias.

**Verdict: PARTIAL** — equation sound and deliberately conservative, documentation silent about it. Correction 1 of the patch records it. **Refuted if** someone shows a caller that treats R_k as a calibrated probability rather than a conservative bound; then the bias matters and the exact form `R_old(1−qσ)` should replace it.

---

## F3 — Section 5's theorem: derived independently, HOLDS in all four parts

```
$ python3 scripts/cc_free_seat_2026_09_21/f3_bounded_recursion_theorem.py
   f'(R) = (1-nu)*[ sigma*(1-q)/(1-q*R)^2 + (1-sigma) ]   -> STRICTLY INCREASING
   f(0) = nu   f(1) = 1                                   -> SELF-MAP of [0,1]
   odds after one cycle = O*(1-q) exactly: True
   fixed points s=1: [1, nu/q]      f'(1) = (nu-1)/(q-1)
```

- **Monotone self-map ⇒ convergence without contraction.** Holds. An order-preserving continuous self-map of `[0,1]` gives a monotone bounded orbit; monotone convergence does the rest.
- **Telescoping ⇒ `#{cycles with gain > θ} < 1/θ`.** Holds. Trivial, but true and useful.
- **The premise-inversion.** Holds, and it is the sharpest part. In odds coordinates one cycle multiplies `O` by exactly `(1−q)`, so log-odds falls by the **constant** `log(1/(1−q))` forever. Under log utility every cycle is worth the same, so the *economic* rule never fires even though `R_n → 0`. ν>0 is not what buys convergence; it is what makes the economic step terminate.
- **Critical re-injection rate.** Holds, and it is `ν* = q`. Fixed points `{1, ν/q}`; for ν>q the interior root leaves `[0,1]` and `R=1` is the only one left. Confirmed in the **shipped** code: `q=0.1, ν_b=0.3 → orbit limit 1.0000000000`.

**Does it belong in the falsifiable-claims table? Split it.** The `ν > q ⇒ certain failure` condition **yes** — it is operational, it is a hard-exit criterion, and it is mechanically testable against `compute_rk`. The monotone-convergence result **no** — it is a theorem, not a falsifiable empirical claim; it belongs in the derivation text. Putting a proof in a falsifiability table degrades the table.

**Two corrections the theorem forces on existing appendix text:**
1. **The stated floor `lim R ≥ ν_k` is loose by 1/q.** The exact attracting limit at σ=1 is `ν/q`. At q=0.2, ν=0.05 the true floor is **0.25, five times the stated 0.05**. Verified against shipped `compute_rk` to 1e-7.
2. **At ν = q exactly the fixed point is parabolic** (`f'(1)=1`), so approach to 1 is `O(1/n)`, not geometric. My first test asserted 1e-6 at 4000 iterations and **failed** — it reached 0.9953. A run at the critical rate therefore **looks like slow convergence, not divergence**, and the `ΔR_n = 0` Hard Exit will misread it. I found this by having my own falsifier break, and I kept it.

**Verdict: HOLDS**, with the floor tightened. Patch Correction 2. **Refuted if** σ is allowed to vary per cycle — my fixed-point analysis holds σ constant. With σ drifting the map is non-autonomous and `ν/q` is not a fixed point.

---

## F4 — Today's repair passes the additive standard. Credit where due.

The standard's own failure mode ("11 confirmed defects were additions that did nothing") is the first thing I tested. The gate is **not** one of them:

- populated at `reference_runner_v3.py:3760, 3781, 15554`
- consumed at the real caller `:12010` → `compute_sk(:11998)`
- executed by tests: `python3 -m pytest bench/tests/test_sk_measures_fix_efficacy_2026-09-20.py -q` → **14 passed in 10.55s**

**Verdict: HOLDS.** And the measured gain is real: the repair **lowered the structural floor under sk from 0.400000 to 0.285714** (F6). That is a committed measurement, not a judgement.

**Two specific invitations, answered:**

- **INDETERMINATE as unavailable, not 0 — correct, keep it.** All five outcomes (`NOT_INTERCEPTED`, `NO_BASELINE`, `NO_FIX`, `OTHER`, unparsed-after) are **probe** failures, not **fix** failures. Scoring a probe failure as "the fix doesn't work" fabricates evidence. Dropping it from the mean is the honest neutral. The real cost is narrower and worth recording: on those records σ reverts to harm-gates-only, i.e. the pre-repair defective behaviour. The repair is strictly better on the determinate subset and identical elsewhere — textbook additive. **Verdict: HOLDS.**
- **Terminal REJECTED where ESCALATE was returned — correct.** Since `E` is an arithmetic mean and `tristate = ADMISSIBLE if sk > 0`, `e1=0` can only produce `sk=0` when e1 is the **sole** available gate; previously `effect_gates` was empty → ESCALATE. Confirmed by construction in F5§C. Reach 0/1247, and I reproduced the brief's Wilson bound independently: **[0.0000%, 0.3071%]**. **Verdict: HOLDS.**

---

## F5 / F6 — The repair reduces the defect. It does not close it. (Material)

**Claim.** A fix **measured not to cure its own falsifier** is still admitted at sk=0.714286, and that number is handed to `compute_rk` as σ — the quantity appendix line 214 defines as *"does the proposed fix actually resolve the detected flaw?"*

```
$ python3 scripts/cc_free_seat_2026_09_21/f5_sigma_dilution.py
   scores {'e1_efficacy': 0.0, 'e2_regression': 1.0, 'e3_ruff': 1.0, 'e4_bandit': 1.0}
   E = 0.714286   sk = 0.714286   tristate = ADMISSIBLE
   sigma = 0.714286 (diluted) -> R_k = 0.410714
   sigma = 0 (what the PROBE MEASURED) -> R_k = 0.500000
   risk understated by 0.089286 (17.86% of the correct residual)
FALSIFIED: sk = 0.7143 > 0.5 ADMISSIBLE for a fix measured to cure NOTHING.
```

**Is weight 2.0 defensible?** The weight is defensible and **irrelevant**, which is the more useful answer. With three clean harm-gates, `sk = 5/(5+w)`: w=2→0.714, w=4→0.556, w=8→0.385, w=20→0.200. **No finite weight makes an arithmetic mean decisive.** The dilution is a property of the *mean*, not of the *weight*, so re-arguing 2.0 vs 4.0 cannot close it. The existing comment's reasoning ("2.0 needs no new justification because e2 and e4 already carry it") is sound and I am not attacking it.

**And worse — there is a hard floor.** Regenerating the brief's Section 4 producer rather than trusting it surfaced something the brief did not use:

```
$ python3 scripts/scorer_discrimination_2026-09-20.py
   e4_bandit  weight 2.0  ran 902  distinct values 1  min 1.0  max 1.0
        *** ZERO VARIANCE across 902 decisions — a constant, not a gate ***
```

A constant at weight 2.0 in a renormalised arithmetic mean cannot lower E — only hold it up:

```
$ python3 scripts/cc_free_seat_2026_09_21/f7_sigma_floor.py
   worst case e1=e2=e3=0, e4=1 : E = 0.285714
   z3: E < 0.285714 ?  unsat  -> FLOOR PROVED
   with e4 FREE, E ~ 0 reachable? sat
FALSIFIED: sigma floor = 0.285714 > 0 by construction.
```

So **σ ≥ 0.285714 by construction** whenever e4 is available, however badly the fix performs. `compute_rk` can never be told "this fix resolved nothing." Risk is understated by ≥0.0357 on every such cycle.

**Verdict: FAILS** — the repair is a genuine improvement that does not close its stated defect.

**Fix.** I am **not** proposing one, and that is a deliberate call against Section 7. Every route I can see is either new apparatus (a multiplicative combinator, a separate σ channel) or a removal (dropping e4's weight) — both barred, the second by the additive standard, since a committed measurement showing a replacement dominates does not exist. The one route that *is* within existing apparatus is the code's own stated remedy at `:10955` — *"If a gate is genuinely non-negotiable, it belongs in the hard gates (A)"* — because A is multiplicative and would make e1 decisive. I flag it and stop, because I cannot measure its reach from a free seat and an unmeasured behavioural change is exactly what the standard forbids. **This is the founder's call, not mine.**

**What would refute F5/F6.** A measurement showing e4_bandit varies on the *forward* corpus (the 902 are historical and Python-target-heavy). If e4 discriminates going forward, the floor vanishes — `f7` §E already shows `E ~ 0` becomes reachable the moment e4 is free. That single measurement would retire both findings.

---

## Where I disagree

**1. With CC1, on the substance.** CC1's position is stated as "the appendix conflates *the repair did not work* with *the observation did not occur*." I say the conflation runs the other way: the appendix accounts the observation on **both** branches, and the revision keeps only the favourable one. The deficit is exact and positive everywhere: `q·R_old(1−R_old)/(1−q·R_old)`. CC1's diagnosis of the *symptom* (the two maps differ; the recorded identity is narrower than written) is correct and well-executed. The *direction of error* is inverted.

**2. With CC1, on what went unexamined.** CC1's evidence is four tools deep on the σ=0 endpoint and silent on σ=1, ν=0 — where the revision returns exactly 0 and breaks the framework's own substrate ceiling. The 200,000-point sweep would not surface it: it samples the open cube, and the defect sits on a measure-zero face. This is a case where exhaustive random sampling and endpoint analysis disagree, and the endpoints won.

**3. With the brief, on Section 2's framing.** *"no amount of algebra decides it"* is too strong, and it is the sentence that kept this question open. Algebra comparing the two maps cannot decide it. Probability **from the model the appendix has already committed to** decides it in four lines. The question was not undecidable; it was under-derived.

**4. With the brief, on Section 4's emphasis.** The brief invites attack on weight 2.0 and on INDETERMINATE. Both survive. The live defect is in neither — it is the arithmetic **mean** plus a **zero-variance gate**, and `scorer_discrimination_2026-09-20.py` had already measured the zero variance without that consequence being drawn.

**5. With myself.** My first ν-threshold falsifier asserted 1e-6 and failed at the critical point. I was wrong about the convergence *rate*, not the threshold, and the parabolic-point finding exists because the falsifier broke. Reported rather than tuned away.

---

## Section 6 — the founder's question, answered directly

Yes — corrections and qualifications is the right description, and on the central point it is if anything generous to the critics rather than an understatement. The core of the model is unchanged and, having now derived it from scratch rather than read it, I think it is unchanged **because it is correct**: the three-phase recursion's most-contested line — that a failed fix returns risk to where it started — turns out to be exactly what the probability demands, not an oversight, and the proposed replacement is the thing that breaks. One line of the appendix has changed across this whole arc, the inverse sign at 169, and that was a genuine typo in a restatement rather than a flaw in the model. What Section 2 adds is not a different equation but a better *reason* for the equation already there, and that matters only because the weak reason as written successfully misled a capable reviewer. What Section 5 adds is a proof that the recursion converges, which is a new theorem *about* the model rather than a new piece *of* it — it introduces no parameter and changes no number, and its practical yield is two tightenings of existing sentences (the residual-risk floor is ν/q, not ν; and at the critical rate the system fails slowly enough to look like success). The one place I would not let the word "qualification" stand is the scorer: σ still cannot reach zero by construction, so the quantity the model calls fix efficacy is not yet measuring fix efficacy. That is a gap between the model and its instrument, not a gap in the model — which I think is precisely the distinction you were drawing.

---

## Section 7 — parameter count and comprehensibility

**Practitioner parameter count: unchanged at five — η, σ, ν, d, p.** Every recommendation I make is a documentation correction. No new flag, gate, threshold or entry point; nothing removed. A competent reader can still follow the model without a machine: the two-branch table in Correction 1 is a four-line hand calculation, and `ν* = q` is easier to remember than the break-even expression already in the text. Gamma untouched — I did not examine it, and nothing here bears on it.

## Delivered files

| path | what |
|---|---|
| `PATCH_appendix_phase2_and_floor.md` | the fix: Phase 2 justification + tightened floor |
| `f1_two_branch_derivation.py` | the derivation that settles σ=0 |
| `f2_z3_crosscheck.py` | z3 confirmation, 7/7 |
| `f3_bounded_recursion_theorem.py` | Section 5 derived from scratch |
| `f4_run_the_real_recursion.py` | shipped `compute_rk` + NumPy×mpmath |
| `f5_sigma_dilution.py`, `f7_sigma_floor.py` | the two Section 4 falsifiers |
| `f6_falsifier_for_the_patch.py` | falsifier for every claim in the patch — **all 13 OK, clean exit** |

All under `scripts/cc_free_seat_2026_09_21/`.

**Stopping here.** The last two passes produced one new above-threshold finding each (the parabolic critical point; the σ floor), and this pass produced none — the remaining items are footnotes, and I cannot name a specific unexamined mechanism where a material defect would still hide.

<!-- verbatim-end -->


---

## Seat `fable` — verbatim, 13144 characters, 29 tool calls, route `claude_cli`

<!-- verbatim-begin: fable -->

All evidence is in. Both falsifiers delivered at real paths, executed, behaving exactly as designed. Final report follows.

---

# PANEL REPORT — free seat (Claude), 2026-09-21

## F1 — THE QUESTION: the appendix's revert-to-prior at σ=0 is CORRECT. CC1's revision is the modelling error.

**Claim.** Phase 2's `R_base = σ·R_det + (1−σ)·R_old`, returning `R_old` at σ=0, is not a discard of evidence; it is the exact law-of-total-probability value. CC1's revision 1.1 conditions on the wrong event.

**Derivation (the decisive step, which no amount of map-difference numerics decides).** `R_det = R_old(1−q)/(1−q·R_old)` is the posterior **given no detection**. But a cycle containing a fix attempt contains a **detection** — a fix cannot exist for a flaw that was not found. Build the single-flaw generative cycle: flaw present w.p. `R_old`; detected w.p. `q` if present; a failed fix leaves a detected flaw in place (branch risk 1); the undetected branch carries `R_det`. Then:

```
P(flaw after cycle, σ=0) = q·R_old·1 + (1−q·R_old)·R_det = R_old   — exactly
```

The detection branch (flaw confirmed present, repair failed) exactly cancels the no-detection reassurance. **"The evidence still happened" is true, and its net effect on presence-risk is exactly zero when no fix works** — detection without removal changes where you know the flaw is (the findings registry), not whether it exists (R_k). Reverting to the prior is the theorem, not the mistake.

**Executed evidence** (`python3 - <<…` SymPy blocks above; cross-verified z3, mpmath 40 dps, Wolfram):
- SymPy: `q·R + (1−q·R)·R_det − R` simplifies to **0**. Wolfram Language (local Wolfram Engine): **0**.
- The full branch-averaged map is `R_old(1−qσ)`, and the appendix blend is **everywhere ≥ it** on the open cube: z3 `unsat` for any point where appendix < exact; mpmath 6859-point grid, 0 optimistic points. The appendix is conservative (fail-safe) at every σ, exact at σ=0.
- **The revision fails at both endpoints.** At σ=1, ν=0 it returns **0**, not `R_det` — SymPy `revision − R_det = R(1−q)/(Rq−1)`, z3 `unsat` that it is ever nonzero-free, Wolfram **0**. That breaks the appendix's verified reduction-table row 1 (Stage 5→4 nesting, η=1, σ=1, ν=0), claiming one cycle with a perfect fix drives residual risk to zero despite q<1. At σ=0 it returns `R_det < R_old` (z3: `R_det ≥ R_old` unsat on the open square) — it takes the no-detection posterior in a branch where a detection occurred, **understating risk exactly when fixes fail**, the worst direction for a verification framework.
- Implementation agrees: `compute_rk(0.5, 0.3, sk=0, nu_b=0, nu_f=0) = 0.5`; `sk=1 → 0.41176…` (= R_det).

**Verdict: HOLDS** (appendix), **FAILS** (revision 1.1 as a replacement map). **Fix: none — change nothing.** One prose defect remains in the appendix: line 229's *"the fix failed and the pre-detection risk level applies"* explains the endpoint by assertion, which is what invited CC1's misreading; the three-line total-probability derivation above would immunise it. Optional, founder's pen.

**Falsifier:** `scripts/falsifier_phase2_endpoints_2026-09-21.py` (imports real `compute_rk`, exact `Fraction` arithmetic). Output:
```
CHECK A CLEAN: appendix sigma=0 revert == exact total probability; compute_rk(0.5, 0.3, sk=0, nu=0) == 0.5
FALSIFIED (revision 1.1 as a replacement map):
  - revision(sigma=1,nu=0) = 0 != R_det = 7/17 -- Stage 5->4 nesting broken
  - revision(sigma=0,nu=0) = 7/17 < R_old = 1/2 -- understates risk when the fix failed (fail-unsafe)
```
**What would refute me:** a coherent generative model in which the cycle's fix exists *without* a detection having occurred, or a demonstration that R_k is meant as the undetected-residual ledger only — in which case σ should not appear in Phase 2 **at all** (both maps wrong), not be revised to act on z. Note CC1's revision fails under that reading too: `(1−s)z` at s=1 claims a fix to a *known* flaw eliminates *undetected* residual.

**On CC1's numerics:** all reproduced (`python3 scripts/phase2_prior_vs_posterior_2026-09-21.py`: 200000/200000 differ, max 0.959481, mean 0.124414; mpmath spot values to 40 digits identical). They establish the maps differ — never in dispute — and are silent on which is right. The narrowed identity claim (Phase-3-alone, residual 0) also reproduces: that correction to the 2026-09-20 synthesis **HOLDS**.

## F2 — Today's repair (`e1_efficacy`): direction right, headline overstated, one new defect.

**Executed** (`compute_sk` run directly on a real Python target, canonical SEARCH/REPLACE block; commands and full output above):

| scenario | sk | tristate |
|---|---|---|
| probe CURES, sole gate | 1.0 | ADMISSIBLE |
| probe INEFFECTIVE, sole gate | 0.0 | **REJECTED** (was ESCALATE) |
| probe INDETERMINATE, sole gate | 0.0 | ESCALATE |
| probe INEFFECTIVE + clean ruff+bandit | **0.6** | **ADMISSIBLE** |
| probe crashed by fix + clean ruff+bandit | **1.0** | **ADMISSIBLE** |

**(a) The 31/31 defect narrows but does not close — verdict PARTIAL.** With any other positive gate available, E = Σwᵢsᵢ/Σwᵢ > 0 ⇒ sk > 0 ⇒ ADMISSIBLE, for *any* finite e1 weight. All 31 archived non-curing fixes had positive other-gate E (mean sk 0.950206), so **all 31 remain ADMISSIBLE post-repair** (exact argument, no re-scoring needed), at sk≈0.6 rather than ≈0.95. The repair changes the σ fed to R_k, not admission — and at defaults the ν_eff coupling means sk=0.6 moves R_k *up* (0.5 → 0.516729), which is the safe direction, so the practical harm is bounded. But anyone reading the docstring's "31 of 31 … admitted, Wilson [88.9745%, 100.0000%]" as *closed by this repair* is wrong: post-repair Wilson for the same cohort is the same [88.9745%, 100.0000%]. If a probe-measured non-cure is non-negotiable, the code's own comment says where it belongs: the hard gates. That changes what reaches verdicts — founder's call; I report, not patch.

**(b) Weight 2.0 — HOLDS, with a precise statement of what it does.** The tristate is invariant to the weight (sole-gate: weight cancels, E = score; mixed: sign of E is weight-free). Weight only modulates σ: at INEFFECTIVE+clean-gates, E = 3/(w+3), so w=2 → 0.6. Anchoring to the heaviest existing weight rather than judging a new one is the additive standard applied correctly.

**(c) INDETERMINATE-as-unavailable — PARTIAL: right rule, one manufacturable outcome. This is my one new above-threshold finding.** `NO_BASELINE`, `NOT_INTERCEPTED`, `NO_FIX` are decided before or without the fix — dropping them is the project's own failed-call-is-not-a-result rule, and treating them as 0 would convert apparatus failure into refutation. But `fix_efficacy.py` line ~212 shows `INDETERMINATE_OTHER` is reached **only after a CONFIRMED baseline and interception** — i.e. the fix itself is the change that broke the probe. Dropping *that* one creates a gradient that pays for breaking the instrument: **crash the falsifier → sk 1.0; let it run and fail → sk 0.6 (+0.4)**, and downstream `compute_rk(0.5, 0.3, ·)`: crash → 0.441176 (risk *down* 0.059), honest fail → 0.516729 (risk up). In the project whose archive holds Exp 48 C0012, that gradient will be found. **Fix** (founder's call, since it changes verdicts): score post-baseline `INDETERMINATE_OTHER` as 0.0 or force ESCALATE — distinguishable by outcome string with no new apparatus. **Falsifier delivered and executed:** `scripts/falsifier_e1_indeterminate_gradient_2026-09-21.py` →
```
AssertionError: FALSIFIED: crashing the probe pays +0.4000 sk over letting it run (1.0 vs 0.6)
```
**What would refute me:** evidence that falsifier-crash-on-patched-copy occurs predominantly from equipment (timeouts, sandbox) rather than the patch — the archived 5 INDETERMINATE records' details would show it.

**(d) Terminal REJECTED on probe-alone — HOLDS.** The probe re-runs the finding's own falsifier: a mechanical instrument, which is what "tools decide, not votes" means. Reach 0/1247, Wilson [0.0000%, 0.3071%] (recomputed independently, matches). Archive stats reproduce: `python3 scripts/scorer_discrimination_2026-09-20.py` → 74.5011% of sk exactly 1.0, Wilson [71.5570%, 77.2374%]; e4_bandit zero-variance across 902 decisions.

## F3 — Section 5 theorem: derivation CONFIRMED with qualifications; it belongs in §8.5 only as its empirical consequence.

Derived, not accepted. T(R) = [σR(1−q)/(1−qR) + (1−σ)R](1−ν) + ν. **Executed:** T′·(1−qR)² = (1−ν)[σ(1−q)+(1−σ)(1−qR)²]; z3 `unsat` that T′≤0 anywhere with q<1, ν<1 — strictly increasing continuous self-map [0,1]→[ν,1]; sign of T(R)−R is orbit-invariant under monotone T, so orbits are monotone and bounded → converge, no contraction needed; gains telescope to R₀−R_∞ ≤ 1. At ν=0, σ=1 the per-cycle odds ratio is exactly (1−q) (SymPy) — constant log-odds gain forever, confirming the economic inversion. Fixed points: R=1 always, plus **R\* = ν/(q(σ(1−ν)+ν))**; R\*≥1 ⟺ **ν ≥ ν_c = qσ/(1−q(1−σ))**, and z3 confirms `unsat` for any fixed point in [0,1) above ν_c — certain failure is then the only rest point. Wolfram independently returns ν_c = qσ/(1−q+qσ). **Coherence check the appendix can cite: ν_c is exactly the appendix's own break-even ν\*(R) at R=1** (SymPy, difference 0). The implementation obeys it: orbits of `compute_rk` at sk∈{1.0, 0.6, 0.0} are all monotone, converging to 0.1667, 0.6458, 1.0000 respectively (200 iterations, executed). **Qualifications required:** q<1 strictly (at q=1 T is discontinuous at R=1) and ν<1 (T constant); the implementation's ν_eff(sk) coupling holds these per-cycle-constant, so the theorem applies cycle-wise. **Where it belongs:** §8.5 is a table of *empirical* claims with bench failure criteria; a tool-proved theorem does not fit it. Put the theorem beside the Reduction Properties table in §1.1, and add to §8.5 only its falsifiable consequence: *"runs with measured ν > qσ/(1−q(1−σ)) fail to converge below R=1; failure criterion: an archived run above ν_c whose R_k series converges to an interior value."* Parameter count: zero new parameters; a reader can follow the fixed-point argument with pencil and paper.

## F4 — The founder's question, answered directly.

Yes — with one honest asymmetry. Nothing in the model's mathematics has been found wrong beyond the one-line inverse-sign slip already fixed in commit `8a0952a`: this round's deepest challenge, the claim that Phase 2 wrongly discards evidence, was tested to destruction and the appendix **won** — its revert-to-prior at σ=0 turns out to be an exact consequence of the law of total probability, so what looked like a possible modelling error is now a derived property. The convergence theorem is genuinely new mathematics *about* the unchanged model, not a change *to* it, and today's S_k repair rewires plumbing under a σ the appendix had already defined. So "corrections and qualifications" is the right description of what changed — but it slightly undersells what happened, which is that the core survived a serious, tool-executed attempt to refute it and came out with a stronger warrant than it went in with. The one caveat: the repair as shipped still admits probe-refuted fixes when other gates are clean, and pays a fix for crashing its own probe — those are open items on the plumbing, not on the model.

## Where I disagree

1. **With CC1, on the answer itself.** The revision is not a refinement that the appendix's authors missed; it is a conditioning error — the no-detection posterior applied to a branch that contains a detection — and it fails the project's own verified reduction table at σ=1, ν=0 (returns 0). CC1's framing "a fix failing does not un-observe the pass" misidentifies *which observation* R_det encodes.
2. **With the brief's evidentiary weighting.** Section 2's 200,000-point sweep, max-gap and z3 two-state analysis are all correct and all beside the point: they prove the maps differ, which was never the question. The deciding evidence is one three-line identity the sweep cannot see. Volume of cross-verified numerics is not the same as an answer, and the brief's own closing line ("no amount of algebra decides it") is wrong in the other direction — this particular algebra *does* decide it, once the conditioning event is named.
3. **With the repair docstring's implicature.** "31 of 31 … admitted" reads as the defect this gate closes; executed, all 31 would still be admitted. The repair's real effect is on σ, and the docstring should say so.
4. I do **not** disagree with the scope rules: gamma never entered this question's decision path (it licenses nothing here — every quantity used was tool-computed, not model-asserted), and no recommendation above adds a parameter.

**Delivered files:** `scripts/falsifier_phase2_endpoints_2026-09-21.py`, `scripts/falsifier_e1_indeterminate_gradient_2026-09-21.py` — both ruff-clean, both executed, outputs pasted above. Wolfram attribution: the three quoted Wolfram results were computed with Wolfram Language (local Wolfram Engine, via wolframscript).

**Termination:** the last pass produced one above-threshold novelty (F2c); the passes after it produced only confirmations of already-derived results. Stopping here.

<!-- verbatim-end -->


---

Written under CDSFL note standard v1.7 (26 August 2026).
