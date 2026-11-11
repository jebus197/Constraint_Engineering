# Is severity an ordinal quantity whose scale the domain supplies

Record written 2026-11-11T22:48:11+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

This round put to 2 free seats the position that severity is an ORDINAL quantity whose numbering each STEM domain already supplies, raised by the founder on 2026-11-11 and quoted verbatim in section 1 of the brief. 10 positions were offered for refutation, not for agreement, and the brief states that a concurring answer carries no information because a canonical rule of this project is that there are no votes in CDSFL.

Both seats answered: cc2 at 38,458 characters over 1,361 seconds, fable over 1,026 seconds. 7 of the 10 positions carry both seats. The positions on whether the model's assertion of existence and order suffices, and on whether section 7.7's product is a good credence formula, split the seats. The position that v_bar is the mean severity computed 4 ways was refuted by both, and the refutation is factual: v_bar names different quantities in different modules.

The load-bearing finding is that an ordering alone does not determine a cut. A domain must supply the numbering AND the critical level, because a cut named by a fixed value is not invariant under the admissible transformations of an ordinal scale while a cut named by a distinguished element of the ordering is. Carried linearly into the 4 validated scales the brief names, the project's frozen 0.7 lands exactly on the High boundary of the software scoring scale, and between levels on the failure-mode, clinical and nuclear scales.

Findings were acted on the same day: the naming collision between the materiality symbol and the verification factor was repaired, and the dead citation in section 7.7 was replaced. The third collision, severity naming 3 distinct objects, is held for the founder because separating them is a design decision. Entry B144 records the measurement and its producer.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# BRIEF — Is severity an ordinal quantity whose scale the domain supplies?

**Round:** `severity_is_ordinal_2026-11-11`. Free seats only (`cc2`, `fable`), blind half
then joint half. No compelled convergence: each seat returns its own verdict and its
strongest falsification, and disagreement is preserved as information.

**Tree state:** repository at commit `92ae4a1a`, 2026-11-11. Every file quoted below is
quoted AT THAT COMMIT, with its line numbers, because a previous joint round
(`joint_severity_spec_is_uncomputable_2026-11-04`, tracked as entry B125) asked 2 seats
about a file that had changed since they answered, so their correct reading read as an
error. Do not re-read a quoted file and assume a difference is your mistake; report the
difference.

---

## 0. WHAT IS BEING ASKED, AND WHAT IS NOT

**NOT being asked:** whether severity is meaningful, whether the position below is good,
or whether you agree with it. A canonical rule of this project is that **there are no
votes in CDSFL**. An answer of the form "I concur" carries no information and will be
recorded as a non-answer.

**BEING asked:** to break the position stated in §4, using the falsifiable questions in
§7. Each question is phrased so that a specific finding would refute the position. If
you cannot refute it, say which question you tried hardest on and what you would need in
order to refute it.

---

## 1. THE FOUNDER'S FRAMING, VERBATIM

He raised this on 2026-11-11. His words, quoted exactly:

> "Getting a simple sum wrong is unlikely to have many, if any real world consequences,
> although that depends on the domain. Getting a more serious calculation wrong could
> determine whether a bridge stands or falls, whether a spacecraft returns safely from
> space, or burns up in the atmosphere, or whether a calculated tolerance for a jet
> engine fan blade is correct or not, or might result in a catastrophic failure."

> "given that CDSLF was designed from the outset to be a general purpose STEM
> calculator, and given that each domain already has its own consequence scales as you
> state, is it not the case that no one severity scale could fit them all, and therefore
> we should use these already existing measures and apply each as needed on a per domain
> basis, rather than adopt any single one as difinitive?"

> "its presence in the maths model becomes illustrative (and should be stated as such in
> as an abstracted concept in our model/mathematics appendix, if it is not already clear
> there?), rather than being definitive (not a single magic wand that can apply
> throughout domains), while the way severity itself is measured in the real world can
> vary in ways that almost all researchers in each respective STEM domain would be
> likely to recognise instantly?"

> "the different ways severity is measured across domains ... doesn't by definition break
> our maths model, because the maths model simply predicts that this quantity exists,
> irrespective of domain. (Or indeed perhaps even how one choses to measure it?) In this
> sense the maths model sits at a higher level of abstraction than the individual
> measures themselves?"

And the standard he is holding the model to:

> "If severity is to be considered a real quantity, then we must be able to map it
> cleanly on to real world consequence. ... I don't want anyone to look at our maths
> model and say it, or any part of it, or any part of what we do, is somehow just 'magic
> fairy dust', with no real substance behind it."

**He is not a mathematician and says so.** He asks specifically whether an abstracted
quantity that varies across domains and across experiments is already adequately
represented by conventional mathematical notation, or whether the model needs something
it does not currently have. That is question Q6 in §7.

---

## 2. THE RECORD: THREE DIFFERENT OBJECTS ARE CALLED "SEVERITY"

All citations are at `92ae4a1a`.

**(a) THE DEFINITION — real-world consequence.**
`bench/directives/universal/cdsfl_core_formal.md:402`:

> "Severity is **materiality** — the consequence if the defect ships — and is
> independent of how *interesting* the defect is."

And its formal block at `:417-421`:

```
V(f) = materiality(f) = consequence if defect f ships (= severity).
Guard 1:  critical(f) ⇔ V(f) ≥ θ_crit     (interest(f) does NOT enter).
Guard 2:  may_continue(K) ⇔ ∃ mechanism m: plausible(m) ∧ high_value(m)
                                          ∧ ¬adequately_examined(m, ≤K).
Converge when marginal value ΔV(K)=Σ_{genuine_new(K)} V(f) is small AND no
material critical remains open (per §6 termination + the A4 fail-safe).
```

**(b) THE FORMULA — a credence product.** `docs/MATHEMATICAL_APPENDIX.md:1253-1267`,
section 7.7:

> **Sev(f) = W(class) · confidence · V(verification)**
>
> | W(HARD) | 1.0 |, | W(SOFT) | 0.5 |, | V(True) | 1.0 |, | V(None) | 0.5 |, | V(False) | 0.0 |
>
> **Key property:** Disproved findings always receive zero severity, regardless of
> confidence.

**(c) THE NUMBER THE CODE GATES ON** — `entry["severity"]`, a float each model asserts in
its structured output. Required by `bench/cdsfl_finding_schema.json` since commit
`8c1dacb3`, 2026-03-30, which is 7 months before the first severity panel of 2026-09-07.

**3 naming collisions follow from this and are part of what you are asked to check:**

1. Section 7.7 uses `V` for the **verification factor**. `cdsfl_core_formal` uses `V(f)`
   for **materiality**. The same symbol, in 2 canonical documents, with opposite
   meanings.
2. "Severity" names all 3 objects above.
3. Section 7.7's caution 3 at `docs/MATHEMATICAL_APPENDIX.md:1334-1335` cites
   "`cdsfl_core.txt` §10 already enumerates five material-defect categories". That file
   is **39 lines long and has no §10**; it is the 5-step P-pass loop. The citation is
   dead.

---

## 3. THE MEASUREMENTS. Each is reproducible; re-run anything you doubt.

**★ LINE NUMBERS IN THIS BRIEF ARE A HINT; THE SYMBOL IS THE LOCATOR.** Every citation below
was RE-VERIFIED against the working tree immediately before dispatch, and 6 of them had
already moved since the brief was first written — insertions earlier the same day shifted
them by between 5 and 32 lines. This is exactly the defect entry B125 records: a brief that
describes a file as it was sends a seat to a bolted door, and the citation checker verifies
only that a cited line is IN RANGE, never that it still says what the citation claims.
**So locate by the NAMED SYMBOL first and treat the number as an approximate hint. If a line
does not say what this brief claims, report the mismatch as a finding rather than working
around it** — it means the tree moved again between this dispatch and your read.


<!-- figure: key-property-violation | scripts/severity_was_never_computed_from_the_model_2026-10-12.py | 84.3750% -->
<!-- figure: proof-vs-gated-correlation | scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py | Pearson  r = -0.5538 -->
<!-- figure: proven-entry-count | scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py | archived entries with a PASS/WARN R_k proof: 652 -->

**★ WHICH FIGURES HERE HAVE A COMMITTED PRODUCER AND WHICH DO NOT. READ THIS BEFORE
TRUSTING ANY NUMBER BELOW.** The project's rule is that a measured figure may be cited
only if the script producing it is committed alongside it. 3 figures here satisfy that
and are DECLARED above, so the validator re-executes them: the 84.3750% key-property
violation, the −0.5538 proof-versus-gated correlation, and the 652 proven entries.

**The rest were computed in session on 2026-11-11 and have NO committed producer yet.**
That is a known gap and it is stated rather than hidden. It applies to: the AST census
of readers and writers in §3.1, the 25-versus-21-versus-4 aggregation census in §3.8,
the z3 and SymPy results in §3.5, the commutation table in §3.7, and the 0.999500
relabelling sweep. **Do not take any of those on trust. Q2 and Q3 ask you to re-derive
them, and a disagreement with any of them is a finding, not a misunderstanding on your
part.** If you reproduce one and get a different answer, report yours and the command.


**3.1 — Section 7.7 cannot be computed as specified.** By AST over
`bench/reference_runner_v3.py`: `constraint_class` has **1 reader (line 10922) and 0
writers**; `confidence` has **1 reader (line 10923) and 2 writers (lines 14665 and
20762), and neither writer writes the object the reader reads** — 14665 writes
`stats["verdicts"][finding_id]`, a per-verdict telemetry dict, and 20762 writes
`_sv_rows`, a telemetry list. The reader reads a registry entry. Both fields are absent
from `bench/cdsfl_finding_schema.json`. `_SEVERITY_SPEC` stands at `{"on": False}`
(line 10708).

**3.2 — The one confidence value that IS collected is inadmissible.** Line 14665 is
`float(m.group(4)) if m.group(4) else 0.5`, parsed from a model's own verdict text. The
operational directive, amended on the founder's B87 ruling of 2026-11-08
(`bench/directives/universal/cdsfl_operational.md:625-642`), rules a model's estimate of
its own certainty INADMISSIBLE. So pointing §7.7 at the value that exists would
reinstate a model vote.

**3.3 — The key property is violated on live data.** `scripts/severity_was_never_computed_from_the_model_2026-10-12.py`:
27 of 32 disproved findings carry non-zero severity, **84.3750%**, Wilson 95%
[68.2459%, 93.1356%], Clopper-Pearson [67.2121%, 94.7249%].

**3.4 — The proof mechanism proves a different quantity.**
`scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py`: `severity_is_proven`
accepts a reproduction of `R_k` as evidence for a severity claim. Over **652** archived
entries with a PASS or WARN proof, Pearson **r = −0.5538**, p = 1.152e-53, 95% CI
[−0.6048, −0.4982], scipy and numpy agreeing to 1.11e-16; Spearman ρ = −0.4716. At the
proof's own 0.05 tolerance, **555 of 652 (85.12%)** would stop being released.

**3.5 — A 2-level consequence weight cannot rank more than 2 consequences.** z3: asked
for 4 distinct severities from `W ∈ {0.5, 1.0}` with confidence and verification free →
**unsat**; with 2 → **sat**. SymPy: `d(Sev)/dw = c·v > 0`, so distinct severities ⟺
distinct weights. **The formula expresses exactly as many severities as `W` has values.**

**3.6 — The 4 worked examples, scored by the project's own function.** Each is a HARD
violation a tool can confirm. `compute_sev_f(class, confidence, verdict)` from
`bench/reference_runner_v3.py`, called directly:

| Domain | Defect | Real consequence | §7.7 |
|---|---|---|---|
| Physics | `Isp` used without `g₀`; Δv is 9.80665× too small | Vehicle cannot complete the transfer. Irreversible | **0.9** |
| Chemistry | Limiting reagent misread from an unbalanced equation | Scale-up under-delivers ~25%. Recoverable, no hazard | **0.9** |
| Biology | Off-by-one ORF start; 312 residues becomes 104 | Downstream wet-lab targets a protein that does not exist | **0.9** |
| Mathematics | Reversed inequality; a divergent series called convergent | The theorem is void, and so is everything citing it | **0.9** |

**1 distinct value across 4 consequences.** At confidence 0.90 the formula's entire range
is 6 cells: `W(HARD)` gives 0.9 / 0.45 / 0.0 and `W(SOFT)` gives 0.45 / 0.225 / 0.0.

The physics arithmetic was checked 3 ways: SymPy and NumPy agree the error is exactly
9.80665, and `pint` confirms that omitting `g₀` leaves the result in **seconds**, which
is not a velocity — which is why a dimensional checker catches that one and its
verification factor is 1.0.

**3.7 — Which statistics of an ordinal severity are admissible.** Commutation test over
6 strictly increasing relabellings (`t²`, `√t`, `eᵗ`, `log(1+t)`, `2t`, `t`), exact
symbolic arithmetic:

| statistic | commutes with every relabelling? |
|---|---|
| max, min, median, count ≥ cut | **yes — admissible** |
| SUM, MEAN | **no — inadmissible** (they commute under `2t` and `t` ONLY, i.e. under linear maps) |

Exact counterexample under `φ(t) = t²` on levels {1/4, 1/2, 3/4}: `Σφ(x) = 7/8` against
`φ(Σx) = 9/4`. SymPy, NumPy and mpmath agree to 0.00e+00.

Independently, a sweep over the whole threshold range with 20,000 free monotone
relabellings of 6 findings with ranks {5,4,2,2,1,1}: **2,000 of 2,001 thresholds give a
ΔV convergence verdict that depends on the relabelling** — 0.999500, Wilson 95%
[0.997175, 0.999912] on 2 independent routes agreeing to 2.22e-16. The Guard 1 rank
threshold gave a critical count of 2 in all 20,000.

**A CAVEAT ON 3.7 THAT YOU SHOULD HOLD AGAINST ME.** The first version of that sweep was
VACUOUS: it fixed a single cut at 1.0, which lay below the sum's own minimum of 1.0661,
so 0 of 20,000 relabellings flipped and the prose claimed a disagreement the output
contradicted. It also normalised every map's top value to 1.0, which made `max` appear
invariant by construction. The figures above are from the rebuilt instrument, which
sweeps all cuts and leaves the maps free. If you find a third defect in it, that is a
finding.

**3.8 — How much live code the ordinal reading would break.** By AST over `bench/`,
excluding tests: **25** severity aggregations; **21 are rank-safe**, counting findings
above a cut rather than summing magnitudes — 0.840000, Wilson 95% [0.653464, 0.935965].
The **4** doing true magnitude arithmetic are `bench/dm/_convergence.py:267` and `:303`,
`bench/dm/_manager.py:722`, and `bench/run_exp19_fff.py:339`. The canonical
`bench/reference_runner_v3.py` is **not** among them.

---

## 4. THE POSITION UNDER TEST

**P1.** Severity is what `cdsfl_core_formal.md:417` already says it is: the consequence
if the defect ships. That is a real-world quantity and the definition needs no change.

**P2.** Severity is an **ORDINAL** quantity. The model fixes the ORDER of consequences;
a domain supplies a particular numbering. No single numbering can serve all STEM
domains, and attempting a single one is what would make it fairy dust.

**P3.** The scale is therefore **domain-supplied, from scales that already exist and are
independently validated** — FMEA severity 1–10 in engineering, CTCAE grades 1–5 in
clinical work, CVSS 0–10 in software, INES 0–7 in nuclear, and each field's own
equivalents. Adopting them is more defensible to a referee than inventing a new one, because
the referee can check them against a standard that is not ours.

**P4.** This does **not** break the mathematical model, because the model asserts that
the severity quantity EXISTS and is ORDERED in every domain — it does not assert a numbering. The
model therefore sits at a higher level of abstraction than any particular measure. This
is the founder's own formulation and it is P4 verbatim in substance.

**P5.** The consequence of a mathematical error is a property of the APPLICATION, not of
the error's form. The same reversed inequality is epistemic in a pure convergence proof
and lethal in a fan-blade tolerance. A mathematical finding therefore inherits the
consequence scale of the domain the mathematics is being used in — which is a further
argument for P3 rather than an exception to it.

**P6.** Section 7.7's product is a good **CREDENCE** formula wearing the name of a
consequence measure. Its key property — a disproved finding scores 0 — is exactly right
for credence. The repair is additive: rename it, and let
`severity(f) = consequence(f) × credence(f)`, where consequence is domain-supplied and
credence is today's §7.7 product.

**P7.** Exactly 1 thing must change in the model's own rules: `ΔV(K) = Σ V(f)` at
`cdsfl_core_formal.md:421` is inadmissible on an ordinal scale and must become an order
statistic. Note that `:421` already pairs that sum with "AND no material critical
remains open", and that second conjunct IS rank-safe — so the repair may be to drop the
non-invariant half rather than to add anything.

**P8. A DOMAIN MAY CARRY SEVERAL ADMISSIBLE SCALES, NOT ONE.** P3 names 4 existing scales as
examples and should not be read as assigning one scale per domain. Engineering alone carries FMEA
severity beside mission-consequence scales beside regulatory classifications, and a researcher picks
by what the work is for. The model constrains the ORDER and is silent on how many numberings realise
it, so several coexisting scales is the expected case rather than an awkwardness. **This is the
founder's own extension, 2026-11-11, verbatim:** *"So there may be not just one, or 4 ways to measure
severity, but several?"*

**P9. SCALE SELECTION IS A ROUTING QUESTION, NOT ONLY A DEFINITIONAL ONE, AND THIS IS THE
OPERATIONAL CONSEQUENCE THE BRIEF PREVIOUSLY LACKED.** If the scale is domain-supplied, something must
choose it, and the only thing in this harness that knows a target's domain is its own classification
of it. His words: *"it would depend on the target under study and which domain the harness classifies
it as being in? Because then the appropriate severity measure and methodology for measuring it in
that specific domain could be applied?"* **That follows, and it hands the question to a mechanism
whose accuracy is measurable rather than to a definition.** It also inherits that mechanism's known
limits: the classifier routes 25 of 29 claims on this project's own STEM corpus after the 2026-11-11
widening, up from 22, so 4 of 29 would reach no scale at all. **A seat is asked to say what the
harness should do with a finding whose domain it cannot classify** -- refuse to score severity, fall
back to an ordering with no numbering, or escalate -- because that case is now reachable and the
brief names no answer for it.

**P10. `v_bar` IS THE LIVE IN-CODE INSTANCE, SO THIS IS NOT ONLY A PRINCIPLE.** The harness computes
`v_bar`, the MEAN severity of genuine findings, and a mean is exactly the operation P2 says is
inadmissible on an ordinal scale: averaging assumes the gaps between levels carry magnitude. **It is
computed in 4 places by 4 DIFFERENT formulas** -- a plain mean over all findings, a 50/50 blend of 2
earlier values, a mean over recent rounds only, and an exponentially weighted moving average. So 4
programs produce 4 numbers under 1 name, and that disagreement is a defect whichever way the ordinal
question is settled. **A seat is asked whether the correct repair is an order statistic in each of
the 4 sites, a single shared rank-safe definition, or the removal of the quantity from any gating
role** -- and, under `additive-standard`, what measurement would have to accompany a removal.

---

---

## 5. THE FOUR WORKED EXAMPLES, RESCORED ON DOMAIN SCALES

This is what §7.7's worked examples would become. **It is a draft and part of what you
are asked to attack** — in particular whether each scale is the one a researcher in that
field would actually reach for.

| Domain | Scale invoked | Position | Why that position | What the measurement tells us |
|---|---|---|---|---|
| Physics / spaceflight | mission-consequence 1–5 (loss of vehicle or crew = 5) | **5 of 5** | Irreversible; the stated result is wrong by an order of magnitude | The central quantitative claim fails and nothing downstream of it can be trusted |
| Chemistry / process | process-consequence 1–5 (recoverable economic loss = 2) | **2 of 5** | Fully recoverable; the qualitative claim survives | Directionally right, quantitatively wrong: the route works, the numbers need redoing |
| Biology / annotation | research-validity 1–5 (invalidates dependent work = 4) | **4 of 5** | Expensive, recoverable, no hazard | The annotation is wrong and every experiment built on it must be re-planned; the method is sound |
| Mathematics, pure | result-validity 1–5 (theorem void = 3) | **3 of 5** | Total epistemic loss, no physical pathway | The theorem and its dependents are void |
| **The same mathematics, in a fan-blade tolerance** | **FMEA severity 1–10** | **9 or 10** | FMEA 9 is "hazardous with warning", 10 is "hazardous without warning" | Potential catastrophic failure; this is P5 made concrete — one error, two scales, two answers |

---

## 6. HARD CONSTRAINTS ON ANY ANSWER

- **GAMMA IS LOAD-BEARING AND MAY NOT BE DEMOTED.** A severity condition ADDED to the
  convergence gate is in scope. A severity condition SUBSTITUTED for part of it is not.
- **No model votes.** Severity may not be set by a model's assertion, and an answer that
  proposes one is refused by the project's own canonical rule.
- **Do not propose promoting §7.7 to the blocking gate as written.** `V(None) = 0.5`
  makes every unresolved finding sub-critical, so a model would clear the gate by
  omitting a falsifier. This was measured on 2026-11-04: 831 of 835 downward crossers
  were `V(None)` halvings of UNVERIFIED claims.
- **A composed fix requires a measurement.** The founder's composability standard: a
  composed fix may be recommended only with a committed measurement showing it dominates
  either part alone on a named property. Where a single fix does as well, prefer it.
- **Cite file and line.** A claim about this repository without a citation at `92ae4a1a`
  will be treated as unverified.

---

## 7. THE FALSIFIABLE QUESTIONS

**Q1.** Name a STEM domain with **no** recognised consequence scale. P3 depends on their
existing; a domain without one is a gap in the architecture, and the answer should say
what CDSFL should do there.

**Q2.** Is §3.7 wrong? Specifically: is there an admissible statistic of an ordinal
severity that I have classed as inadmissible, or vice versa? Note that this is Stevens'
1946 result on permissible statistics; if the project is mis-applying a standard result,
say so and give the correct statement.

**Q3.** Is §3.8 incomplete? I used AST over `bench/` excluding tests and found 25
aggregations, 4 of them magnitude arithmetic. Name what that census misses — other
directories, other aggregation forms, arithmetic that is not a `sum`/`mean` call, or
severity arithmetic inside a comparison.

**Q4.** Can the project's frozen critical cut of 0.7 be expressed as a RANK on each
scale named in P3? If some scale has too few levels to place it, or places it absurdly,
that is a concrete defect in P3.

**Q5.** Does per-domain scaling break cross-domain aggregation anywhere in the design of
Bench Run 2 — which compares results ACROSS domains? If run-level or arc-level
statistics add or average severity across domains, P2 forbids it and the brief has not
said where.

**Q6. THE FOUNDER'S OWN QUESTION, and it is the one he most wants answered.** He asks:
if severity cannot be a single number, how should an abstracted quantity that varies
across domains and across experiments be represented in the mathematical model — and is
it **already** adequately represented by conventional notation, or does the model need
something it does not have? Answer concretely, in notation, and state what the model
LOSES under your representation as well as what it gains. He is not a mathematician, so
also give the answer in one plain-English paragraph.

**Q7.** Is P6 wrong? Is §7.7's product actually a good credence measure, or does it fail
as credence too? If it fails, say on what.

**Q8.** What is the strongest argument that this whole position is wrong and the project
should keep a single universal severity scale? Make that argument as well as you can,
then say why you do or do not believe it.

---

## 8. USE THE HARNESS — do not describe it, run it

Form your answer **using** the machinery, not by writing about it. The instruments that
bear on this question, and what each is expected to say:

- **The severity model itself.** Call `compute_sev_f(constraint_class, confidence,
  falsifier_verdict)` from `bench/reference_runner_v3.py` on the 4 cases in §3.6 and
  report what you get. It is expected to return 0.9 for all 4. If it does not, §3.6 is
  wrong and that is a finding.
- **`severity_is_proven`**, same module, line 10680. It is expected to accept an `R_k`
  reproduction as proof of a severity claim. Run
  `scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` and report the
  correlation it prints; it is expected to be about −0.5538 over 652 entries.
- **`_SEVERITY_SPEC`** at line 10708. It is expected to read `{"on": False}`. If the
  switch is on in your sandbox, say so — the whole analysis assumes it is off.
- **The two-sided convergence gate and gamma.** Gamma is LOAD-BEARING and may not be
  demoted. Read `bench/dm/_convergence.py:267` and `:303` and report whether those sums
  can be replaced by an order statistic without changing what the gate decides on any
  archived registry. An answer that asserts it can without running it has not answered.
- **`scripts/severity_was_never_computed_from_the_model_2026-10-12.py`.** Expected:
  27 of 32, 84.3750%.

A seat that returns prose about severity without having executed anything has not
answered this brief.

## 9. PRODUCE A FIX, AND TEST IT

A finding without a fix is incomplete. **A fix without a runnable falsifier that you have
EXECUTED is a hypothesis, not a fix.** Report the exact command you ran and the output
you saw, pasted, not summarised.

**WHERE THE FIX MUST BE DELIVERED.** Write it **INTO the sandbox repository tree at its
real path, as a file** — for example an edited
`bench/directives/universal/cdsfl_core_formal.md`, an edited
`docs/MATHEMATICAL_APPENDIX.md`, or a new script under `scripts/`. **A fix described in
prose is not delivered, and a fix written to scratch space is destroyed when the sandbox
is torn down.** Rounds 5 and 6 on 2026-09-10 returned 0 source files for exactly that
reason while both seats reported writing and running working code.

**ON COMPOSABILITY, as the founder defines it.** Several repairs are in play here: the
ordinal reformulation of `ΔV`, the rename of §7.7 to a credence term, the per-domain
scale table, and the repointing of `severity_is_proven`. **Compose 2 of them ONLY on a
DEMONSTRATED advantage over each alone, where the demonstration is a MEASUREMENT and not
a judgement, and prefer the single fix wherever it performs as well.** Reporting merely
that the repairs do not conflict is the weak non-interference form his definition
explicitly excludes, and will be recorded as not having answered.

## 10. WHAT WOULD REFUTE YOU

Before you conclude, state what evidence would overturn your own answer. A verdict with
no stated refutation condition is an opinion, not a finding. Be concrete: name the file,
the measurement or the archived run that would change your mind.

## 11. OUTPUT SHAPE — field by field

Return these fields, named, so replies can be compared without a parser guessing:

- `verdict` — your position on §4's P1 to P7, each marked AGREE, REFUTE or CANNOT-DECIDE.
- `q1` … `q8` — one answer per falsifiable question in §7. "Cannot refute" is legitimate
  and must say what you tried.
- `q6_notation` — your proposed notation for the founder's own question, in full, plus
  one plain-English paragraph for a non-mathematician, plus what the model LOSES under it.
- `reasoning` — how you got there.
- `falsifier` — the runnable check, and `falsifier_result` — its EXECUTED output, pasted.
- `fix_paths` — the real repository paths you wrote files to in the sandbox.
- `commands_run` — every command, verbatim.
- **`disagreement` — your strongest DISAGREEMENT with this brief's own framing, as a
  field, not as prose elsewhere.** State it even if you agree with the conclusion: a
  round that reconciles is the one most likely to converge by deference, and deference is
  not evidence. If you genuinely have none, write "none" and say why that is not
  deference.
- `aims_check` — whether anything you propose disables, weakens or removes an existing
  mechanism, threshold or flag. The additive standard forbids it without a committed
  measurement showing the replacement dominates on a named property.
- `passes_run` — how many passes you made.

## 12. TERMINATION

Stop when a further pass produces no new above-threshold findings — the project's own
diminishing-returns criterion. A finding is above threshold if missing it could cause a
real-world failure, an invalid result or an unsafe condition. Do not generate findings to
fill a quota, and do not pad with style observations: this brief is about whether a
quantity in the mathematical model corresponds to anything real. Report `passes_run`.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 65 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel severity_is_ordinal_2026-11-11) -->

I have what I need. Writing the answer.

---

## `verdict`

| | Position | Verdict |
|---|---|---|
| **P1** | Severity is the consequence if the defect ships | **AGREE** |
| **P2** | Severity is ORDINAL; model fixes order, domain supplies numbering | **AGREE, WITH ONE REPAIR** — an order alone does **not** determine a cut. The domain must supply the numbering **and the critical level**. Demonstrated: `count ≥ cut` with the cut transported commutes with 0 of 6 relabellings; with the cut **held fixed** — which is what `CRITICAL_SEVERITY_THRESHOLD = 0.7` does — it breaks on **5 of 6**. |
| **P3** | Scale is domain-supplied from existing validated scales | **AGREE** |
| **P4** | Does not break the model, which asserts existence + order only | **REFUTE AS STATED** — incomplete for exactly the reason above. Existence + order is not enough to support a gate. The model must assert existence + order + a distinguished level. |
| **P5** | Consequence is a property of the application, not the error's form | **AGREE** |
| **P6** | §7.7 is a credence formula wearing a consequence name | **AGREE** (see `q7` for where it fails as credence too) |
| **P7** | `ΔV = Σ V(f)` is inadmissible and must become an order statistic | **AGREE on the mathematics, REFUTE the urgency.** `Σ` fails 4 of 6 relabellings. But the live analogue — `kappa_set` at `_convergence.py:267`/`:303` — is the binding term of its `min` in only **3 of 18** archived registries, and flipped under **0 of 72** relabelling cases. The repair is safe and low-yield, not load-bearing. |
| **P8** | A domain may carry several admissible scales | **AGREE** |
| **P9** | Scale selection is a routing question | **AGREE** |
| **P10** | `v_bar` is the mean severity, computed 4 ways | **REFUTE — the premise is factually wrong.** In `bench/dm/_manager.py:644` `v_bar` is *"proportion of findings with verified=True"*, a ratio-scale quantity for which the mean **is** admissible. Mean severity is the separate axis **`A`** (`:645`, `:722`). |

---

## `q1` — a STEM domain with no recognised consequence scale

**Pure mathematics**, and the brief's own §5 table contains the evidence. Every other row names an existing, externally-auditable standard (FMEA, CTCAE, CVSS, INES). The mathematics row names *"result-validity 1–5"* — which exists nowhere outside this brief. There is no ISO, no society standard, no referee-checkable register of "how void is this theorem". P3's whole defensibility argument is that *"the referee can check them against a standard that is not ours"*, and for pure mathematics there is no such standard to check against.

**What CDSFL should do there:** not invent one. A mathematical result is either valid or void — a **two-level** scale, and that is honest rather than impoverished. Where the mathematics is *applied*, P5 already routes it to the application's scale (the fan-blade row does exactly this). So the answer is: pure mathematics gets `{void, valid}`, and anything finer is this project inventing a scale, which is the fairy dust the founder is trying to avoid.

---

## `q2` — is §3.7 wrong?

**Yes, on two rows, and one of them matters to the gate.** Exact symbolic arithmetic, SymPy, independently confirmed by Wolfram Language (local Wolfram Engine, exit 0).

**Row `median` is wrong.** §3.7 lists `median` as admissible without qualification. The **conventional sample median averages the two middle values at even n**, which is an arithmetic mean, and it fails on **4 of the brief's own 6 relabellings** — the identical signature §3.7 assigns to `SUM` and `MEAN`. On levels `{1,2,3,4}` under `φ(t)=t²`:

```
φ(median) = 25/4     median(φ) = 13/2     equal? False
```

Wolfram independently: `{5/2, 25/4, 13/2, False, True, 7/8, 9/4}` — the `True` is `max` commuting, and `7/8` vs `9/4` reproduces the brief's own `Σ` counterexample exactly.

**Why §3.7's instrument missed it:** the sweep used ranks `{5,4,2,2,1,1}` — even n, but the two middle values are **tied at 2**, so averaging them returns 2 and the median appeared invariant by accident of the data. That is a *third* defect in that instrument, which §3.7's caveat invited me to find. A **selected** order statistic (lower median, or any fixed-index one) fails **0 of 6**.

**Row `count ≥ cut` is wrong as stated.** It is admissible only if the cut is **transported** by the same `φ`. Transported: 0 of 6 fail. **Held fixed: 5 of 6 fail.** The harness holds it fixed.

**The correct statement of Stevens 1946:** a statistic is permissible on an ordinal scale iff its value is invariant under the group of strictly increasing transformations of the scale. That admits order statistics (selected, not averaged), percentiles, rank correlations, and counts **above a transported cut**. It excludes the sum, the mean, the variance, any averaged median, and any comparison against a constant that does not travel with the scale.

**Also, and §3.7 does not say it:** `kappa_set` is a **ratio of sums**, `1 − Σ(w·Sev_novel)/(Σ Sev_cum + ε)`. A ratio of sums is invariant under `x ↦ kx` but not under general monotone `φ`, so it presupposes a **ratio scale with a true zero** — stronger than interval, far stronger than ordinal. FMEA 1–10 and CVSS 0–10 are not ratio scales. So P3's named scales are inadmissible inputs to `kappa_set` even under a generous reading.

---

## `q3` — is §3.8 incomplete?

**Yes.** My AST census over `bench/` (excluding `logs/`, `tests/`, `__pycache__`), excluding the `sum(1 for …)` count idiom which is rank-safe, finds **26** severity-arithmetic sites, of which ~15 are genuine magnitude arithmetic after discarding f-string concatenations. §3.8's four are all real. What it misses:

1. **Products, not just `sum`/`mean`.** `bench/dm/_convergence.py:276` — `total += class_weight * ec.aggregated_severity`. This is in the *same function* as `:267`, which §3.8 did catch. Also `bench/dm/_feedback.py:187` (`score += 0.1 * severity`) and `bench/immune_agents.py:4146,4149` (`0.40 + 0.10 * test_severity` → a *confidence*).
2. **Variance** — `bench/macrophage_cell.py:278-279`: `mean_sev = sum(severities)/len(...)` then `variance = sum((s - mean_sev)**2 ...)/len(...)`. A variance of an ordinal quantity is doubly inadmissible and §3.8 names neither line.
3. **`bench/reference_runner_v3.py` IS among them.** §3.8 states *"The canonical `bench/reference_runner_v3.py` is **not** among them."* Line **3964** reads `shadow = float(sev) * v` — a product of a severity with the verification factor. That claim is false.
4. **Arithmetic on the CUT, not on severities.** `bench/reference_runner_v3.py:10583` — `min(floor, CRITICAL_SEVERITY_THRESHOLD - 0.01)`; `:11339` — `CRITICAL_SEVERITY_THRESHOLD ± b`. Subtracting 0.01 from an ordinal level is meaningless; the ordinal operation is "one level below". This whole category is invisible to a census that looks for aggregations of severities.
5. **Copies under `bench/exp40_baseline/`** (`_feedback_cleaned.py:174`, `_feedback_records_slice.py:113`) — same `0.1 * severity_claimed`.

I caution against my own number: my first pass reported 52 magnitude sites and was wrong, because `sum(1 for s in sev if s >= 1.0)` is a count. I corrected it before reporting. Treat **26** as an upper bound needing hand-classification, not a committed figure — it has no committed producer either.

---

## `q4` — can the frozen 0.7 be expressed as a rank on each P3 scale?

**No, and this is the concrete defect in P3.** Test C settles it mechanically: a cut held fixed while the scale is relabelled breaks on 5 of 6 maps. So 0.7 cannot *survive* re-expression; it must be *replaced*, per scale, by a named level.

Working through P3's four:

| Scale | Levels | Where does "critical" sit? |
|---|---|---|
| FMEA severity | 1–10 | Placeable. 9 = "hazardous with warning", 10 = "hazardous without warning". Conventional action threshold is 9. |
| CTCAE | 1–5 | Placeable. Grade 4 = life-threatening. |
| CVSS | 0.0–10.0 | Placeable, **and here 0.7 is actively dangerous**: CVSS is already a 0–10 float, and `0.7` on CVSS is *Low*. A naïve re-use of the constant would gate at the opposite end of the scale. The CVSS "Critical" band begins at 9.0. |
| INES | 0–7 | Placeable at 4 (accident with local consequences). |

So: all four admit a cut, but **none of them admits 0.7**, and one of them silently *mis*-admits it. That is a real hazard in P3 as written and the reason my `cdsfl_core_formal.md` amendment writes `θ_crit(domain)` rather than a constant.

---

## `q5` — does per-domain scaling break cross-domain aggregation?

**Partly cannot decide, and I say which part.** I could not locate a "Bench Run 2" design document in the tree to check against, so I answer on the mechanisms it would have to use.

What I **can** decide: every run-level severity aggregation I found is a sum, a mean or a ratio of sums — `kappa_set`, `v_bar`/`A`, `macrophage_cell`'s mean and variance. Each of those is inadmissible **across** domains under P2, and more sharply than within one: adding an FMEA 9 to a CTCAE 4 is not merely a scale error, it is a category error, because the two numerals index different orders.

What survives cross-domain: **counts of findings at or above each domain's own critical level**, and **the per-domain maximum**. Those compose, because what is being aggregated is already a domain-local *yes/no*. "17 criticals across 5 domains" is meaningful; "mean severity 0.63 across 5 domains" is not.

So the brief has not said where this bites, and the answer is: anywhere a run-level or arc-level statistic is a sum or a mean. It should be re-expressed as a count-above-local-cut before Bench Run 2, not after.

---

## `q6` — the founder's own question

### `q6_notation`

**Short answer: conventional notation already covers it, and the model does not currently use that notation. Nothing exotic is needed; what is needed is a scale object rather than a bare number.**

**The notation.** Severity is a map into an ordered set, not a real number:

$$\text{Mat}: F \longrightarrow (\mathcal{S}_D, \preccurlyeq_D), \qquad \theta_D \in \mathcal{S}_D$$

- $F$ — findings. $D$ — the domain the harness routes the target to (P9).
- $\mathcal{S}_D$ — the **domain's scale**: a finite totally ordered set. For FMEA, $\{1 \prec 2 \prec \cdots \prec 10\}$; CTCAE, $\{1 \prec \cdots \prec 5\}$; pure mathematics, $\{\text{valid} \prec \text{void}\}$.
- $\preccurlyeq_D$ — the order. **This is what the model asserts and all the model asserts.**
- $\theta_D \in \mathcal{S}_D$ — the critical level, **a member of the scale, not a constant**. This is the piece P4 is missing.

Two scales $\mathcal{S}, \mathcal{S}'$ on the same domain (P8 — several coexisting scales) are **equivalent** iff there is an order-isomorphism $\varphi: \mathcal{S} \to \mathcal{S}'$ with $\varphi(\theta) = \theta'$. The model is then stated once, at the right altitude:

> **Every admissible operation on severity must be invariant under every order-isomorphism between equivalent scales.**

That single sentence does all the work. It makes `max`, `min`, selected order statistics, and `|\{f : \text{Mat}(f) \succcurlyeq \theta_D\}|` legal, and makes $\Sigma$, mean, variance, and comparison-against-a-constant illegal — with no new mathematics, because this is Stevens' 1946 permissible-statistics criterion written as an invariance requirement. It is the same move Felix Klein made for geometry: *a structure is what its automorphism group preserves.*

**Credence stays separate and stays real-valued.** §7.7's product is a credence and credences genuinely are numbers:

$$\text{Cred}(f) \in [0,1], \qquad \text{release}(f) \iff \text{Mat}(f) \succcurlyeq \theta_D \ \wedge\ \text{Cred}(f) \ge c_{\min}$$

Note this is a **conjunction, not a product**. P6 proposes `severity = consequence × credence`, and that multiplication is itself the inadmissible operation — you cannot multiply an FMEA level by 0.9.

**WHAT THE MODEL LOSES.** Three real things, and I will not pretend otherwise:

1. **No cross-domain magnitude comparison.** You cannot say a physics finding is "1.8× worse" than a chemistry one. You can only say both are at or above their own critical levels. Some reporting the project does today becomes unavailable.
2. **No continuous convergence signal from severity.** `ΔV` becomes a step function — it drops to "converged" when the round's `max` falls below $\theta_D$, with no gradual descent. You lose the ability to see convergence *approaching*. This is why I did not touch `kappa_set` in code (see `aims_check`).
3. **A second thing to get right per domain.** Every domain now needs a scale **and** a cut, and the cut is a judgement a field makes, which is one more place to be wrong — recoverably, since it is externally auditable against the field's own standard.

**What it gains:** every severity claim becomes checkable against a standard that is not ours, which is precisely the anti-fairy-dust property the founder asked for.

### Plain English, one paragraph

Severity is a *ranking*, not a measurement — like the Beaufort wind scale or an earthquake intensity rating. Saying "this is a 9" tells you it is worse than an 8, and that is all it tells you; it does not mean it is nine times worse than a 1, and you must never add two of them together or take their average, because the gaps between the steps are not real quantities. Your mathematical model is already right about the important part: it says this ranking *exists* in every domain and that the rankings line up the same way everywhere, and it wisely does not say what the numbers should be. One thing is missing, though, and it is the thing that bites in practice. A ranking on its own does not tell you **where the line is** — where "serious" starts. Our code currently has one fixed line, 0.7, used for every domain, and that number only means anything on a scale that happens to run 0 to 1. On the engineering scale it would be nonsense, and on the software security scale it would be worse than nonsense, because 0.7 there means *low* risk rather than high. So each field has to tell us two things, not one: its ranking, and which rung on that ranking counts as serious. None of this requires new mathematics — it is a standard idea about measurement scales from 1946, and writing it down properly is all that is needed.

---

## `q7` — is P6 wrong? Does §7.7 fail as credence too?

**P6 is right that it is a credence, and it fails as a credence on four counts.** It is not merely misnamed.

1. **Its one collected input is inadmissible.** §3.2 is correct: `bench/reference_runner_v3.py:14665` parses `confidence` from a model's own verdict text, and the founder's B87 ruling of 2026-11-08 makes a model's estimate of its own certainty inadmissible. A credence built on a self-reported credence is a vote.
2. **It is not a probability, because the factors are not independent.** `W(class)` and `confidence` are correlated — a model asserting HARD is asserting high certainty by the same act. Multiplying correlated factors as if they composed like independent likelihoods is not a credence, it is a score.
3. **`V(None) = 0.5` is a default masquerading as evidence.** "Not assessed" is an absence of information; assigning it the midpoint asserts 50% belief the finding is real. This is why §6's hard constraint forbids promoting §7.7 to the gate — 831 of 835 downward crossers are `V(None)` halvings — and it is a defect in the formula, not just in its promotion.
4. **I ran `compute_sev_f` and the range is 4 values, not 6.** At confidence 0.9 the attainable set is `{0.0, 0.225, 0.45, 0.9}`. The brief says "6 cells" — the *domain* has 6 cells, the *range* has 4. A credence with four reachable values at fixed confidence is a coarse classifier, not a belief.

**The key property survives all four.** `V(False) = 0` annihilating the product is exactly right and must be preserved under any rename — `bench/reference_runner_v3.py` already documents why `S_v = 1/(1+e^{-Λ})` cannot replace it (no zero).

---

## `q8` — the strongest case for a single universal scale

**Made as well as I can:**

> A per-domain scale destroys the only thing a benchmark is for. CDSFL's claim is that structured falsification finds defects a single pass misses, and that claim is *comparative*: it needs "this configuration found more severe defects than that one". Under P2 that sentence has no referent, because severity in physics and severity in chemistry are now incommensurable and no run-level statistic may combine them. You cannot report a single number for Bench Run 2 at all. Worse, you have handed scale selection to a classifier (P9) that routes 25 of 29 claims — so **4 of 29 findings get no severity, and the classifier's 86% accuracy now sits upstream of every severity claim in the system**, converting a measurement error into a routing error, which is harder to detect. A single universal scale, even a crude one, is *auditable in one place*: if 0.7 is wrong, you fix one constant. Under P3 you must audit five standards, their five cuts, and a classifier, and a defect in any one of them is invisible in the aggregate. Finally — the project has 11 confirmed instances of additions nothing reached. A per-domain scale table is exactly that shape: a large new structure whose consumers do not yet exist.

**Why I do not believe it, except for one part that I do.**

The comparability argument is the strong one and it is wrong for a reason I can demonstrate: **counts compose where magnitudes do not**. "17 findings at or above their own domain's critical level" is a single, honest, cross-domain number, and it is invariant under every relabelling (test C: `count ≥ transported cut`, 0 of 6 fail). Bench Run 2 loses magnitude comparison, not comparison.

The audit-surface argument inverts under inspection. A single constant is auditable in one place only if it is *right* in that place, and it is not: §7.7 collapses to one value across four unrelated consequences (test A — 0.9, 0.9, 0.9, 0.9), and `W` has two values, so the current universal scale distinguishes at most two consequences. An auditable wrong answer is not better than five checkable right ones.

**The part I do believe:** the P9 routing objection is real and the brief does not answer it. 4 of 29 claims reach no scale. And the additions-nothing-reaches warning is well aimed — which is why my delivered fix is two documents and a test, not a scale table.

---

## `falsifier` / `falsifier_result`

`scripts/is_severity_ordinal_the_five_tests_2026-11-11.py` — six tests, each importing the real module, no formula retyped. Polarity: **fails iff the claimed defects are present**. Output pasted in full across this reply; the decisive segments:

```
A. _SEVERITY_SPEC = {'on': False}   CRITICAL_SEVERITY_THRESHOLD = 0.7
   Physics/Chemistry/Biology/Maths -> 0.9  0.9  0.9  0.9
   distinct values across four domains: [0.9]
   attainable RANGE at confidence 0.9: [0.0, 0.225, 0.45, 0.9]  (cardinality 4)

B. 4 distinct Sev, confidence and V FREE  -> sat   witness: [1/4, 0, 1/8, 3/16]
   4 distinct Sev, confidence and V HELD EQUAL -> unsat
   SymPy d(Sev)/dW = C*V;  at V=0 it is 0, NOT > 0

C. CONVENTIONAL median, even n=4: non-commuting ['t**2','sqrt(t)','exp(t)','log(1+t)']
     phi(median)=25/4   median(phi)=13/2
   LOWER median: non-commuting []
   count >= cut, cut TRANSPORTED : non-commuting []
   count >= cut, cut HELD FIXED  : non-commuting ['t**2','sqrt(t)','exp(t)','log(1+t)','2t']

D. bench/dm/_manager.py:644: v_bar:   proportion of findings with verified=True
   bench/dm/_manager.py:645: A:       mean severity of findings (proxy for accuracy/depth)
   bench/run_exp19_fff.py:327: v_bar (mean severity): average severity of genuine findings

E. distinct archived registries exercised : 18
   kappa_set is the BINDING term of the min in : 3
   converged() flips under relabelling, SUM in place            : 0
   converged() flips under relabelling, order statistic in place: 0
   unrelabelled: the two gates agree on 18, disagree on 0

F. `constraint_class` accepted by the envelope schema : False
   code paths that SET a Finding's constraint_class: 3
     bench/runner_core.py:1713 subscript assignment  ...
   NOT DEMONSTRATED: a producer exists. sec 7.7's W input is collectable.

SUMMARY: FALSIFIED (5 defects)  — exit 1
```

**Wolfram second falsifier** (Wolfram Language, local Wolfram Engine via `wolframscript`, exit 0, `Out` present, no `Name::tag`, no `$Failed`):

```
{5/2, 25/4, 13/2, False, True, 7/8, 9/4}
```

→ `Median[{1,2,3,4}]=5/2`; `φ(median)=25/4`; `median(φ)=13/2`; **not equal**; `Max` commutes (`True`); `Total[φ]=7/8` vs `φ[Total]=9/4`, reproducing the brief's own `Σ` counterexample. Independent confirmation of test C on a second kernel.

**Pre-existing figures I re-ran and reproduced exactly:**
- `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` → `27 / 32 = 84.3750%`, Wilson `[68.2459%, 93.1356%]`, Clopper–Pearson `[67.2121%, 94.7249%]`. ✅ matches §3.3.
- `scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` → `652` entries, Pearson `r = −0.5538`, `p = 1.152e-53`, CI `[−0.6048, −0.4982]`, Spearman `ρ = −0.4716`, `555/652 (85.12%)` would stop being released. ✅ matches §3.4.

---

## Two findings against the brief's own record, beyond the questions asked

**Finding 1 — §3.1 is scope-limited in a way that changes its conclusion.** The brief says `constraint_class` has "0 writers". Within `bench/reference_runner_v3.py` alone that is true. But `bench/runner_core.py:1711` parses a `CONSTRAINT_CLASS` envelope field from the model's reply, accepts only `HARD`/`SOFT`, and **rejects rather than coerces** anything else; it feeds `_envelope_field_changes` → `_apply_field_envelopes` (called at `runner_core.py:1887`, inside `parse_findings`) → and `reference_runner_v3.py` imports `parse_findings` at `:329` and calls it at `:12797`, `:13643`, `:13706`, `:13733`, `:13774`. **So §7.7's `W` input IS collectable through the live panel route.** The uncollectable input is `confidence` alone. I hypothesised this was an addition-nothing-reaches — the twelfth instance of the project's 11-times-measured defect class — and **my own AST instrument refuted me**, which is recorded in the script as test F printing `NOT DEMONSTRATED`. That refutation is the result; I am not burying it.

**Finding 2 — a stale committed figure.** `bench/reference_runner_v3.py` (comment above `compute_sev_f`) cites its producer as giving *"35 of 40 REFUTED findings carry non-zero severity, 87.5000%, Wilson 95% [73.8879%, 94.5405%]"*. I ran that producer. It emits **27 of 32, 84.3750%**, and its own output explains why: *"with the copies 37 of 42 = 0.880952; deduplicated 27 of 32 = 0.843750"*. Neither 35/40 nor 87.5% is reproducible from the named producer today. Not above the real-world-failure threshold, so I did not amend it — but the next reader who checks that comment will find it does not reproduce.

---

## `fix_paths`

Three real paths in the sandbox tree:

1. **`scripts/is_severity_ordinal_the_five_tests_2026-11-11.py`** *(new)* — the six-test falsifier. Imports the real modules; fails iff the defects are present. Includes, in its own docstring, the record of the unfair first version of test E and what it wrongly reported.
2. **`docs/MATHEMATICAL_APPENDIX.md`** *(edited, two changes)* —
   - the **dead citation** at the §7.7 caution repaired: `cdsfl_core.txt` §10 → `cdsfl_core_formal.md` §10. Verified dead: `wc -l` on `cdsfl_core.txt` returns **39** and it has no §10; the five material-defect categories are at `cdsfl_core_formal.md:303-317`.
   - a new **caution 4** carrying the full admissibility table, the Stevens statement, both corrected rows, the ratio-scale observation about `kappa_set`, and all three measured figures (18/18, 0-of-72, 3-of-18), plus the record of the unfair first instrument.
3. **`bench/directives/universal/cdsfl_core_formal.md`** *(edited)* — the §Objective formal block. `ΔV(K) = Σ V(f) is small` → `max_{f ∈ genuine_new(K)} Mat(f) ≺ θ_crit(domain)`. `V(f)` → `Mat(f)` to end the symbol collision with §7.7's verification factor. `θ_crit` → `θ_crit(domain)`, `≥` → `≽`.

Why `max` and not a count: `max` is invariant (0 of 6 fail) **and** non-redundant with the existing second conjunct. A count-of-criticals would have been made redundant by "no material critical remains open", collapsing the conjunction. `ΔV` and `θ_crit` occur at **exactly these two lines and nowhere else in the repository**, so the rename reaches no consumer — itself a quiet instance of a directive-level quantity with no implementation.

**Why I did NOT change `bench/dm/_convergence.py`.** I measured the swap and it shows **parity, not dominance**: 18/18 identical decisions, 0-vs-0 flips, binding in only 3 of 18. The additive standard requires a committed measurement showing the replacement *dominates on a named property*. Parity is not dominance, and parity does not license touching a working gate.

---

## `commands_run`

```
pwd; ls
sed -n '10670,10740p' bench/reference_runner_v3.py
sed -n '10740,10960p' bench/reference_runner_v3.py
ls scripts/ | grep -i sever
which python3 python3.12 python3.11; python3 -V
python3 scripts/severity_was_never_computed_from_the_model_2026-10-12.py
python3 scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py
python3 /tmp/sev36.py                      # compute_sev_f on the four cases
sed -n '240,320p' bench/dm/_convergence.py
sed -n '130,165p' bench/dm/_convergence.py
sed -n '355,400p' bench/dm/_convergence.py
sed -n '636,760p' bench/dm/_manager.py
sed -n '315,350p' bench/run_exp19_fff.py
grep -rn "v_bar" bench --include="*.py" | grep -v "bench/logs/" | grep -v "/tests/"
grep -n "§10\|cdsfl_core.txt" docs/MATHEMATICAL_APPENDIX.md
wc -l bench/directives/universal/cdsfl_core.txt
cat bench/directives/universal/cdsfl_core.txt
sed -n '1245,1345p' docs/MATHEMATICAL_APPENDIX.md
grep -n "class Finding" -A 40 bench/dm/_types.py
grep -rn "ΔV\|θ_crit" bench docs scripts --include="*.py" --include="*.md" --include="*.txt"
grep -rn "cdsfl_core_formal\|cdsfl_core.txt" bench --include="*.py"
grep -rn "constraint_class" bench/dm/_types.py bench/reference_runner_v3.py bench/cdsfl_finding_schema.json
python3 -c "import json; ... print finding-item properties"
sed -n '2360,2378p' bench/run_round_robin.py ; sed -n '1700,1720p' bench/runner_core.py
grep -n "_envelope_field_changes\|_apply_field_envelopes" bench/runner_core.py
python3 /tmp/w/f35.py                      # z3 + SymPy, brief sec 3.5
python3 /tmp/w/q2.py                       # Stevens permissible statistics
python3 /tmp/w/diag.py                     # kappa_set vs whole gate (UNFAIR, kept)
python3 /tmp/w/diag2.py                    # faithful substitution inside the min
cat > scripts/is_severity_ordinal_the_five_tests_2026-11-11.py <<'EOF' ... EOF
python3 scripts/is_severity_ordinal_the_five_tests_2026-11-11.py
python3 - <<'PY' ... PY                    # patch tests E and F
python3 - <<'PY' ... PY                    # FIX 1 + FIX 2 -> docs/MATHEMATICAL_APPENDIX.md
python3 - <<'PY' ... PY                    # FIX 3 -> bench/directives/universal/cdsfl_core_formal.md
python3 -m pytest bench/tests/test_citation_content_2026-09-10.py \
                  bench/tests/test_directive_stage_claims_are_true_2026-09-06.py \
                  bench/tests/test_citation_repair_does_not_corrupt_2026-09-11.py -q
python3 -m pytest bench/tests/test_dynamic_management.py -q -x -k "convergence or kappa"
python3 -m pytest bench/tests/ -q -k "composer"
python3 - <<'PY' ... PY                    # AST census of severity arithmetic (two passes)
/Users/.../wolframscript -code 'phi[t_]:=t^2; lvl={1,2,3,4}; {Median[lvl], ...}'
```

**Test results after my edits:** `test_dynamic_management.py -k "convergence or kappa"` → **26 passed**. `-k composer` → **46 passed**. `test_citation_content_2026-09-10.py` → **1 failed, 21 passed** — **pre-existing and not mine**: every failure is an off-by-+5/+24 drift of citations into `bench/reference_runner_v3.py`, and grepping the failure output for `MATHEMATICAL_APPENDIX` or `cdsfl_core_formal` returns **0 hits**. (That failing test is itself an instance of the brief's own ★ warning: the checker verifies a cited line is *in range*, never that it still says what the citation claims.)

---

## `disagreement`

**My strongest disagreement is with §3.5, because it is the brief's load-bearing argument for P2 and it is false as stated — and in a way that makes the real argument look weaker than it is.**

§3.5 claims z3 returns **unsat** for four distinct severities from `W ∈ {0.5, 1.0}` *"with confidence and verification free"*. It returns **sat**, with witness `[1/4, 0, 1/8, 3/16]`. It must: with confidence free in a continuous `[0,1]`, you get a continuum of severities with `W` held at 1.0 alone. The brief's own §3.6 table already exhibits four distinct attainable values at *fixed* confidence — `{0.0, 0.225, 0.45, 0.9}` — so the claim is contradicted inside the brief.

The SymPy half fails too. `d(Sev)/dW = C·V` is **≥ 0**, not `> 0`; it is identically zero whenever `V = 0`, which is the key property. And "distinct severities ⟺ distinct weights" fails in **both** directions: at `V = 0`, `W = 1` and `W = ½` both give 0; at `W = 1` fixed, confidence 0.9 and 0.8 give 9/10 and 4/5.

This matters beyond pedantry. The **true** claim — the one §3.6 actually demonstrates — is that *when confidence and verification verdict are held equal, the only free factor is `W`, which has two values, so at most two distinct severities are expressible.* That is a statement about **conditioning**, and it is exactly the right argument: in practice all four worked examples are HARD/0.9/CONFIRMED, so `W` is the only knob and the formula cannot separate them. Stated as a property of the formula's expressive power it is false and a referee will catch it in a minute. Stated as a property of the realised population it is true, measured, and much harder to dismiss. The brief has traded a solid argument for a false stronger one.

I also disagree with **P10 as a matter of fact** — `v_bar` is not the mean severity in `bench/dm/_manager.py`, it is the verified fraction, and the ordinal objection does not touch it — and with **§3.8's explicit exclusion** of `bench/reference_runner_v3.py`, which does magnitude arithmetic on severity at line 3964.

---

## `aims_check`

**Nothing I propose disables, weakens or removes any mechanism, threshold or flag.**

- **Gamma:** untouched, not referenced in anything I edited, not demoted. The §6 hard constraint is respected.
- **`CRITICAL_SEVERITY_THRESHOLD = 0.7`:** untouched in code. The amendment says a *domain-supplied* scale must supply its own level; it does not remove or move the existing constant.
- **`_SEVERITY_SPEC`:** untouched, still `{"on": False}`.
- **§7.7:** not renamed, not demoted, not promoted. I added a caution beside it. P6's rename is argued in this reply and **not performed**, because performing it would change a specification other seats are reading this round.
- **`bench/dm/_convergence.py`:** **not edited.** My measurement shows parity, not dominance, and the additive standard forbids the swap on parity.
- **The one directive change** replaces a non-invariant statistic (`Σ`) with an invariant one (`max`) in the **first conjunct only** of a two-conjunct convergence condition. The second conjunct — "no material critical remains open" — is byte-identical. Guards 1 and 2 keep their force. The amendment block states this explicitly in the file so the next reader does not have to infer it.
- **The symbol rename** `V(f) → Mat(f)` touches a symbol with **zero** other occurrences in the repository, verified by grep across `bench/`, `docs/`, `scripts/`.

**On composability, as the founder defines it:** I am **not** composing. The three deliverables address three *different* defects — a dead citation, an undocumented admissibility constraint, and a non-invariant statistic — each with one fix. That is three single fixes, not a synthesis. I have **no measurement** showing any pair dominates either alone, and so I recommend none. Where I *did* have a candidate composition — pairing the directive amendment with the matching `_convergence.py` change — my measurement showed parity (18/18, 0-vs-0), and parity is not a demonstrated advantage, so I declined it.

---

## `reasoning`

I ran the instruments first and argued second. The brief's three declared figures all reproduced exactly, which told me the archive and the scripts were sound and that any disagreement I found would be mine to defend rather than an environment artefact. From there the question decomposed into one mathematical claim (is `Σ` admissible on an ordinal scale) and one empirical claim (does it matter in this code), and those needed different tools: exact symbolic arithmetic for the first, the archive for the second.

The mathematical pass found §3.7 right about `Σ` and wrong about `median` and `count ≥ cut`, and the second of those turned out to be the finding that reshapes P4 — because a frozen cut is a *constant*, and a constant is not part of an order. That is the gap between "severity is ordinal" and "the gate works": an order alone cannot support a threshold.

The empirical pass nearly produced a false finding. My first test E reported that the order-statistic swap changed 13 of 18 archived decisions, which would have been a strong result against P7 — and it was an artefact of my own instrument comparing a replacement for `kappa_set` against the whole of `converged()`, silently dropping `kappa_rate` and `kappa_adopt`. The diagnostic that caught it was looking at *why* zero relabellings flipped the gate, which showed `kappa_set` was almost never the binding term of the `min`. Substituting faithfully gave 18/18. I kept the wrong version recorded in the script and the appendix rather than quietly deleting it, because the brief's §3.7 caveat is right that a vacuous instrument reads as a result.

The same discipline refuted me a second time, on `constraint_class`. I had a strong hypothesis — a writer added today with no schema field to feed it, the project's own eleven-times-measured defect shape — and the AST census found three producer sites, which traced through `runner_core._envelope_field_changes` into `parse_findings`, which `reference_runner_v3` imports and calls. The hypothesis was wrong and the script says so in its own output.

What I deliberately did not do is write a per-domain scale table. It is the most *interesting* artefact this brief invites, and it is exactly the shape of the eleven additions nothing reached. The scale table has no consumer until P9's routing question is answered, and the brief asks that question rather than answering it.

---

## `q6` residual — what the harness should do with an unclassifiable finding

P9 asks and names no answer, so: **fall back to an ordering with no numbering, and block.** Concretely — when the classifier cannot route, the finding retains its order position relative to other findings (it can still be compared, `max` still works) but has no `θ_D` to be compared against, so `critical(f)` is undecidable. An undecidable critical **must not** clear a gate. It should be escalated to HIL exactly as `UNTOOLABLE` is, and for the same reason: an honest "I cannot score this" is a correct outcome, and a verdict obtained by defaulting to a scale that does not apply is worse than no verdict, because it is indistinguishable from a real one. Refusing to score and escalating are the same action here; they should not be separate options.

---

## `passes_run`

**4.** (1) Reproduce the brief's declared figures and read the three canonical sites. (2) Attack §3.5 and §3.7 symbolically; found both wrong, and found the frozen-cut result that reshapes P4. (3) Attack the live code — `v_bar`, the census, `kappa_set`; caught and corrected my own unfair instrument; hypothesised and then refuted the `constraint_class` finding. (4) Deliver the fixes, run targeted tests, confirm the one failing test is pre-existing, confirm with Wolfram as second falsifier.

A fifth pass produced no new above-threshold findings — the remaining items were the stale 87.5% comment and the "6 cells" imprecision, both below the real-world-failure threshold.

---

## `WHAT WOULD REFUTE ME`

Concretely, naming the file or the measurement:

1. **On P7's deflation:** a single archived registry under `bench/logs/` in which `kappa_set` is the binding term of `min(kappa_set, kappa_rate, kappa_adopt)` **and** `converged()` flips under a strictly increasing relabelling of severity. My run found 3 of 18 binding and 0 of 72 flipping, but I examined only 18 registries (deduplicated, ≤400 entries, ≥2 rounds) of 78 `runner_state.json` files. Widening `limit_runs` and `max_entries` in test E and finding one flip would make the `_convergence.py` change load-bearing and oblige me to perform it.

2. **On my §3.5 refutation:** the committed producer for §3.5. The brief says that figure has none. If one exists and encodes a constraint I did not model — most plausibly that confidence is *discrete* rather than continuous in `[0,1]` — my `sat` witness `[1/4, 0, 1/8, 3/16]` might be excluded and the brief's `unsat` would stand.

3. **On Q2/`median`:** nothing. `φ(median) = 25/4 ≠ 13/2 = median(φ)` is exact rational arithmetic confirmed on two independent kernels. The only thing that would move me is a definition of "median" in this project's glossary that means *lower median*, in which case §3.7's row is right and only its notation is ambiguous — I grepped and found no such definition.

4. **On P4's incompleteness:** a demonstration that `CRITICAL_SEVERITY_THRESHOLD` is always transported alongside any scale change — i.e. that the harness never compares a severity against a constant that did not travel with it. `bench/reference_runner_v3.py:10583` and `:11339` do arithmetic on that constant directly, so I do not expect this, but a scale-transport layer I failed to find would refute me.

5. **On `v_bar`:** a call site where `CapabilityFingerprint.v_bar` is populated from `run_exp19_fff.compute_condition_fingerprint` rather than from `_manager._update_fingerprints`. That would mean the two definitions genuinely flow into one field and P10's framing is right after all. I found no such site but did not exhaustively trace `run_exp19_fff`'s fingerprint into the `dm` package.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 54 recorded tool call(s).

<!-- verbatim-begin: fable (panel severity_is_ordinal_2026-11-11) -->

All work is executed; writing the verdict.

---

# Seat: fable — `severity_is_ordinal_2026-11-11`

## `verdict`

| Position | Verdict |
|---|---|
| P1 (definition stands) | **AGREE** — `cdsfl_core_formal.md` "Objective" block verified in tree |
| P2 (severity is ordinal) | **AGREE**, with two corrections to its admissibility table (Q2) |
| P3 (domain-supplied scales) | **AGREE with 2 concrete defects** — Q1 (pure maths has no scale) and Q4 (the 0.7 cut does not transfer); both repaired in the delivered amendment |
| P4 (model asserts existence+order only) | **AGREE** — and now backed by measurement: archived gate decisions do not depend on the numbering (301/301 preserved under 3 order statistics) |
| P5 (consequence is a property of the application) | **AGREE** |
| P6 (§7.7 is a *good* credence formula) | **REFUTE** — it fails as credence too (Q7) |
| P7 (ΔV sum must become an order statistic) | **AGREE, measured and delivered** |
| P8 (several scales per domain) | **AGREE** — encoded in the amendment |
| P9 (routing question) | **AGREE**; answer for the unclassifiable case delivered (below). The 25/29 figure has no committed producer and I could not verify it in session |
| P10 (`v_bar` = mean severity in 4 places) | **REFUTE AS STATED** — the brief's own framing misreads the code; see `disagreement` |

## Reproductions demanded by §8 (all executed)

- `compute_sev_f("HARD", 0.9, "CONFIRMED")` → **0.9 for all 4 worked examples**; full range at conf 0.9 = {0.9, 0.45, 0.0, 0.45, 0.225, 0.0} — §3.6 confirmed.
- `_SEVERITY_SPEC` → `{'on': False}` (line 10708) — confirmed by import and execution.
- `severity_is_proven` (line 10680) accepts PASS/WARN `R_k` proofs — confirmed from source.
- `scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` → **652 entries, Pearson r = −0.5538**, p = 1.152e-53, 555/652 (85.12%) would stop releasing — matches brief exactly.
- `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` → **27 of 32, 84.3750%**, Wilson [68.2459%, 93.1356%] — matches.
- `bench/dm/_convergence.py:267/:303` sums → **replaced and replayed**, see falsifier below.

## `q1` — Pure mathematics

Pure mathematics is a STEM domain with **no recognised consequence scale**: there is no community standard for "how bad is a wrong theorem" analogous to FMEA/CTCAE/CVSS/INES — which §5 itself demonstrates by having to *invent* "result-validity 1–5" for that row. What CDSFL should do is delivered in the amendment: such a finding receives **no number** — it carries the order-only judgement material/not-material against `cdsfl_core_formal.md` §10's five material-defect categories (which exist, at line 287ff) and is flagged for human review. Never silently scored on a borrowed numbering, never dropped.

## `q2` — §3.7 is wrong on two points

**(a) The interpolated even-n median is NOT admissible.** `statistics.median` on even n averages the two middle order statistics, and averaging is the inadmissible operation. Exact counterexample (SymPy, corroborated by Wolfram Language): sample {1/4, 3/4}, φ(t)=t²: median(φ(x)) = **5/16** ≠ φ(median(x)) = **1/4**. The brief's instrument could not see this: its sample ranks {5,4,2,2,1,1} sort to [1,1,2,2,4,5] — the middle two are **tied at 2**, so the interpolation is vacuous. That is the third instrument defect §3.7's caveat invited me to find. Only the lower/upper middle order statistic is admissible.

**(b) §3.5 is misstated.** "4 distinct severities from W ∈ {0.5,1.0} with confidence and verification free → unsat" is **false**: with confidence free per finding, Sev = W·c·V ranges over a continuum (W=1, V=1, c ∈ {0.1, 0.2, 0.3, 0.4} gives 4 distinct values trivially). The unsat holds only under **shared confidence and shared verdict** — z3 executed: `unsat` for 4 distinct, `sat` for 2, in that restricted case. The substantive point (consequence resolution comes from W alone) survives; the formalisation as written does not. Also: "count ≥ cut" is admissible **only if the cut transforms covariantly** — carried as a level of the scale, which is exactly why Q4 matters.

## `q3` — §3.8 misses at least 3 magnitude sites

My AST sweep over `bench/` excluding tests and `logs/` found, beyond the census's 4:

1. **`bench/dm/_feedback.py:187`** — `score += 0.1 * severity` in `priority_score` (def at :155), sorted at :390, imported live by `reference_runner_v3.py:393`. Magnitude arithmetic ordering feedback records; relabelling-sensitive.
2. **`bench/immune_agents.py:4146` and `:4149`** — `confidence = min(0.90, 0.40 + 0.10 * test_severity)`: an affine map of severity magnitude into confidence.
3. **`bench/dm/_convergence.py:276`** — `total += class_weight * ec.aggregated_severity`, a distinct line from the cited :267 (same function).

The census's claim that `reference_runner_v3.py` does no magnitude arithmetic **survives**: I inspected every AST candidate there (10334–21412); all are counts-by-level, comparisons, or formatting.

## `q4` — The 0.7 cut transfers to exactly one scale

With `x → lo + 0.7·(hi−lo)` (executed): CVSS → **7.0, exactly the High boundary** — expressible as the rank "High or above". FMEA → **7.3**, CTCAE → **3.8**, INES → **4.9** — all **between levels** (brief's own 0.7×5 = 3.5 convention lands between CTCAE grades too). So the frozen cut cannot be carried arithmetically into P3's scales; each θ_d must be a **per-scale frozen level**. Concrete defect in P3 as drafted; repaired in the delivered amendment.

## `q5` — Yes, and here is where

The capability fingerprint dimension **A = mean severity** (`bench/dm/_manager.py:722`, `obs_a`), persisted per model and updated by windowed mean or EMA (~:735-740), and **`run_exp19_fff.py:339`'s `v_bar`** (mean severity per condition) are per-model/per-condition magnitudes compared across runs. If Bench Run 2 compares fingerprints across targets in different domains — and fingerprints exist precisely to be compared — these means cross domain boundaries, which P2 forbids. No committed Bench Run 2 statistical plan in the tree declares this. The amendment now pins cross-domain aggregation to **material counts only**.

## `q6` / `q6_notation`

**Notation (delivered verbatim into `cdsfl_core_formal.md`):** For each domain d, a finite totally ordered set **(L_d, ⪯_d)** of consequence levels — the domain's own validated scale, possibly several per domain. The model asserts only **(i) existence**: sev(f) ∈ L_{d(f)}, and **(ii) order**: ⪯_d total. It asserts no numbering, no spacing, no cross-domain comparability. **θ_d ∈ L_d** is the frozen critical level, carried as a level. **material(f) ≡ sev(f) ⪰_d θ_d** is the only cross-domain-comparable value. Admissible within-domain statistics: those commuting with every strictly increasing relabelling (max, min, middle order statistics — not the interpolated even-n median — counts at-or-above a level). This is conventional notation — Stevens 1946 / Roberts' measurement theory; **the model needs no new mathematics, only the stated restriction to monotone-invariant statistics.** Credence stays separate: the pair (sev_d(f), S_v(f)) with S_v from §7.8.

**What the model LOSES:** magnitude statements ("twice as severe"); expectations and means of severity, hence any severity-weighted mass like ΔV's Σ V(f) and kappa_set's current form, and any expected-loss decision rule; cross-domain comparisons finer than the material boolean (a CTCAE-4 cannot be said to outrank an FMEA-7); marginal/gradient arguments on severity. That loss of statistical power for cross-domain effect sizes is real and is the honest price.

**Plain English:** Severity is a ranking, not an amount. Every field already has its own ladder of consequences, and your model only promises two things: the ladder exists, and "worse" is well-defined on it. It never promises the rungs are evenly spaced, or that two fields' ladders line up. So it is legitimate to ask "what is the worst finding?" and "how many findings sit at or above the critical rung?" — and not legitimate to add or average rung numbers. Across fields, the only safe common currency is the yes/no at each field's own critical rung. Ordinary mathematical notation handles this completely; nothing exotic is needed — what is needed is the discipline of only using ladder-safe operations, and I measured that your live gate already behaves as if it had that discipline.

## `q7` — P6 is wrong: §7.7 fails as credence too

Three executed/derived grounds. **(i)** Its `confidence` factor is the model's self-asserted certainty — ruled INADMISSIBLE by the B87 amendment (`cdsfl_operational.md:625-642`); a credence built on an inadmissible input is a vote. **(ii)** No Bayesian update: after a tool independently CONFIRMS a falsifier, credence should approach 1 − P(tool error) regardless of the model's prior diffidence; the product instead caps at W·c — `compute_sev_f("HARD", 0.3, "CONFIRMED") = 0.3`. A confirmation cannot overcome model under-confidence. **(iii)** W(class) is a consequence-type factor inside a would-be credence — HARD/SOFT says nothing about P(finding genuine). The project already owns the correct credence: **§7.8's S_v** (log-odds fusion), explicitly marked "a credence, not a severity" on 2026-11-06, harness-computed, with the veto property. So P6's repair ("rename §7.7 and use it as the credence") is the wrong one; the right pair is (sev_d(f), S_v(f)), and §7.7's only correctly-behaving factor, V_ver, is already inside S_v's determinate handling. The key property survives: W·S_v·V_ver(False) = 0 (appendix caution 1, already derived there).

## `q8` — The strongest case for one universal scale, made honestly

Cross-domain comparability is the benchmark's product: Bench Run 2 ranks conditions **across** domains, and with ordinal domain scales every run-level severity effect size collapses to material counts — a severe power loss; "CDSFL finds *more serious* defects than control" becomes inexpressible except at one bit per finding. A single [0,1] scale with one frozen 0.7 is also maximally simple: it is already wired into 25 aggregation sites, and the alternative multiplies freeze points (one θ_d per scale), each an unverified judgement — more surface, in a project with 11 confirmed additions-nothing-reached. **Why I do not believe it:** the record shows the universal number's comparability is fictitious — it was never computed from the model (84.3750% key-property violations), the proof mechanism moves *against* it (r = −0.5538), the computed version is three-valued on all 3,170 archived entries, and my replay shows **no archived gate decision ever depended on the magnitudes**. A universal scale provides the form of comparability with no content, at the cost of exactly the "magic fairy dust" audit the founder fears. The power loss is real; the comparability being lost is not.

## `falsifier` and `falsifier_result`

**Falsifier** (new, committed): `scripts/can_the_severity_sums_be_rank_safe_2026-11-11.py` — replays all archived round-structured reports through the stock `ConvergenceDetector` and three variants replacing kappa_set's two severity sums with order statistics (count / mid-rank / count-above-0.7), suppression and veto and gamma identical. It would FALSIFY P7's repair if any archived `converged()` decision flipped.

**Executed output (pasted):**
```
replayable archived reports: 53
reports skipped (malformed findings): 0
(report, round) decision pairs compared per variant: 301
variant 'count':    converged() decisions differing from stock : 0 ; FIRST convergence round moved: 0
variant 'rank':     converged() decisions differing from stock : 0 ; FIRST convergence round moved: 0
variant 'material': converged() decisions differing from stock : 0 ; FIRST convergence round moved: 0
non-vacuity: converged()==True in 66 rounds; veto fired in 46; kappa_set binding min in 69; kappa_set within 0.05 of tau_kappa in 166
VERDICT: variants ['count', 'rank', 'material'] reproduce every archived converged() decision.
```
Two self-falsification checks on the instrument (the §3.7 lesson): (1) non-vacuity above — the gate fired 66 times and kappa_set was the binding minimum 69 times; (2) value non-triviality — variant kappa_set **values** differ from stock in 192–206 of 301 rounds (max |Δ| = 0.0779 count, 0.0341 rank, **1.0000 material**), so the decision invariance is a real result, not value identity. Caveat carried honestly: invariance on this archive does not guarantee invariance on future runs — the material variant can move kappa_set by 1.0 — so live promotion still warrants one shadowed run.

**Wolfram second falsifier** (local kernel, computed, exit 0): `{5/16, 1/4, 7/8, 9/4, 2}` — confirms the median counterexample, the §3.7 Σφ≠φΣ counterexample, and the two-level collapse at shared confidence. *Values attributed to Wolfram Language.*

## `fix_paths`

1. `scripts/can_the_severity_sums_be_rank_safe_2026-11-11.py` — **new** committed producer (with built-in non-vacuity diagnostic).
2. `docs/MATHEMATICAL_APPENDIX.md` — §7.7: dead citation `cdsfl_core.txt §10` → `cdsfl_core_formal.md §10` repaired (and the §1 locator at :1298 corrected); dated status note added at end of §7.7: illustrative-credence status per the founder's ruling, `V_ver` disambiguation, admissible-statistics rule, per-scale cut freezing, with the measurement cited.
3. `bench/directives/universal/cdsfl_core_formal.md` — "Ordinal severity (amendment, 2026-11-11)" after the ΔV formal block: the (L_d, ⪯_d) notation, θ_d as level, material(f) as sole cross-domain quantity, rank-safe ΔV restatement (original retained as historical form), unclassifiable-domain fallback, gamma and veto explicitly untouched.

**On composability:** I deliver the citation repair, the §7.7 status note, and the core_formal amendment as **separate single fixes to separate defects** and claim no composition advantage; no measurement shows any pair dominating either alone, so under the founder's definition none is composed. The measurement script is not a composition — it is the committed producer the project's own evidence rule requires for the amendment's figures.

## `commands_run` (principal, verbatim)

```
python3 scripts/severity_was_never_computed_from_the_model_2026-10-12.py
python3 scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py
python3 - <<'EOF'  # import reference_runner_v3; print _SEVERITY_SPEC; compute_sev_f on 4 cases + 6-cell range
python3 scripts/can_the_severity_sums_be_rank_safe_2026-11-11.py        # (twice: pre- and post-diagnostic patch)
python3 - <<'EOF'  # SymPy/z3: median counterexample, 3.5 unsat/sat, 3.7 counterexample, Q4 rescaling
python3 - <<'EOF'  # kappa_set value-difference non-triviality check (192–206/301 rounds differ)
wolframscript -code 'phi[t_]:=t^2; {Mean[{phi[1/4],phi[3/4]}], phi[Mean[{1/4,3/4}]], Total[phi/@{1/4,1/2,3/4}], phi[Total[{1/4,1/2,3/4}]], Length[Union[{1/2 c,1 c}/.c->9/10]]}'
```
plus `grep`/`sed`/AST sweeps over `bench/reference_runner_v3.py`, `bench/dm/_convergence.py`, `bench/dm/_manager.py`, `bench/dm/_feedback.py`, `bench/run_exp19_fff.py`, `bench/run_round_robin.py`, `bench/immune_agents.py`, `bench/directives/universal/*`, `docs/MATHEMATICAL_APPENDIX.md`.

## `disagreement`

**P10's central factual claim is wrong, and it is the brief's own coined-vocabulary failure mode.** `v_bar` is *not* "the MEAN severity of genuine findings computed in 4 places by 4 different formulas." In the tree: `bench/dm/_manager.py:719-722` — `v_bar` (`obs_v`) is the **fraction verified** (a count ratio, admissible), and the mean severity there is the *separate* dimension `A` (`obs_a`, :722); `bench/run_round_robin.py:2544-2560` — `v_bar_provided`/`v_bar_extracted` are means of **binary SymPy verification scores** (admissible); `bench/dm/_types.py:331` glosses `v_bar` as "Mean verification quality". Only `bench/run_exp19_fff.py:339` computes mean severity under the name `v_bar`. The real defect is a **name collision** — one name over two quantities, and one quantity (mean severity) under two names — plus exactly one genuinely inadmissible mean family (`obs_a` / exp19 `v_bar`, compounded by the windowed-mean/EMA fingerprint update). The correct repair is one shared rank-safe depth proxy (fraction of findings at-or-above the material level) in both mean-severity sites under one name; I do **not** propose removing the quantity from gating, because the additive standard demands a committed measurement for that and my replay covers kappa_set, not the fingerprint. Secondary disagreements: **§3.1 is stale against this tree** — `constraint_class` now has a writer (`bench/reference_runner_v3.py:3620`, B84 Field 1, dated 2026-11-11; `Finding.constraint_class` at `bench/dm/_types.py:449`), though both fields remain absent from `bench/cdsfl_finding_schema.json` and `confidence` remains sourceless — reported, per the brief's own instruction, as a tree-moved finding; and **§3.5 is formally misstated** (q2b).

## `aims_check`

Nothing is disabled, weakened or removed. Both document edits are dated additive notes plus a citation repair; the core_formal amendment retains the original ΔV line as the historical form and attaches the committed measurement (301/301 archived decisions preserved) that the additive standard requires for a superseding aggregation form. Gamma is untouched and not demoted; the severity veto is untouched (already an order statistic); `_SEVERITY_SPEC` untouched; no live code modified — the new script is read-only over archives.

## What would refute me

(1) A replay of the sum-dependent **release** path over `bench/logs/**/runner_state.json` registries (a population my 53 round-structured reports do not cover) showing an order-statistic substitution flips a release — that breaks my P7 measurement's scope claim. (2) A committed producer for §3.7's sweep showing its median was the lower middle order statistic, not the interpolated one — that voids my Q2(a) as applied to the brief (not the mathematical fact, which Wolfram and SymPy both computed). (3) An in-tree writer for `confidence` landing with harness provenance — that voids Q7(i). (4) A committed measurement that one calibrated universal scale predicts real-world consequence across §3.6's four worked examples better than the domain scales — that refutes P3/P4 and my verdict with them.

## `passes_run`

**3.** Pass 1: reproduction of every §8 instrument. Pass 2: derivations (Q2, §3.5, Q4) and the new gate measurement. Pass 3: self-falsification — instrument non-vacuity, value non-triviality, staleness audit of the brief against the tree (§3.1 writer, P10 misread). A fourth pass produced no new above-threshold findings; stopping per §12.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/severity_is_ordinal_2026-11-11/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
