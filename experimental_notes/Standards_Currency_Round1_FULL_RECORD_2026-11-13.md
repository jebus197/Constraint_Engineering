# Standards currency and model staleness, panel round 1

Record written 2026-11-13T08:39:31+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. The standards-currency measurement of 2026-11-13: the share of model-identity literals in this repository that carry a version, and what that implies for how stale the project's declared model roster is. The brief carried the figure 0.253054, 145 of 573, which was the number declared at dispatch.

WHY. The project's dispatch table names specific model versions, and a literal naming a model without a version cannot be checked for currency at all. The question put to the seats was whether a composed instrument, provenance plus detection, dominates either part alone on a named property, which is what this project's composability standard requires before a composed fix may be recommended.

WHAT WAS DONE WITH THE FINDINGS. The figure the brief declared was WRONG and the seats' work is what exposed how it moved. It was corrected 4 times in one night as successive contaminations of the population were found: the producer counted itself, then its own guard counted itself, then the panel's own harvested seat output entered the population, and finally 359 archived Python files from 63 earlier panel rounds were found to have been inside it all along. The corrected figure is 0.282700, 134 of 474, Wilson [0.244034, 0.324861], Clopper-Pearson [0.242571, 0.325565]. The producer now prints the figure BOTH ways, with and without the named apparatus exclusion, so a reader sees the size of the effect rather than a quietly smaller denominator.

A seat's substantive finding was also adopted: coverage of a composition is the union of the parts' coverage, so a composed figure can never come out lower than the better part: 2 checks covering 15 of 30 and 18 of 30 domain configs compose to at least 18 of 30, never 14. A second seat broke the first composed proposal independently by re-partitioning those same 30 configs and reversing the ranking, which is why the surviving claim is restricted to strict set inclusion plus a genuine ratio-scale property.

The full replies follow unfiltered, as the project's findings-output policy requires: the record is published whole, and any summary sits beside it rather than in place of it.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — building for limits that will relax, when the standards themselves move


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `scripts/standards_currency_and_model_staleness_2026-11-13.py` | `83b641df55bb7566` | 18354 | 2026-11-13T01:17:12+00:00 |
| `bench/cdsfl_registry/domain_vocabulary.py` | `f27c7b6cb0a63f56` | 21926 | 2026-11-12T21:03:50+00:00 |
| `bench/confer_maths_panel_2026-09-05.py` | `aea05271596a0a87` | 117551 | 2026-11-12T06:30:53+00:00 |
| `bench/seat_aliveness_2026-10-06.py` | `9a5c411a63b39fdd` | 10061 | 2026-10-06T06:49:18+00:00 |
| `bench/seat_readiness.py` | `084f4f382743484a` | 18455 | 2026-11-04T00:28:53+00:00 |
| `bench/model_catalogue.py` | `dd8518573b38ffbf` | 13863 | 2026-11-10T03:04:27+00:00 |
| `bench/cdsfl_registry/composer.py` | `88a6f8c910f6d028` | 113110 | 2026-11-12T01:21:40+00:00 |
| `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md` | `14a5b7fa2949b134` | 3739 | 2026-07-28T12:27:32+00:00 |
| `scripts/cdsfl_sv.py` | `0aa813f3476403fc` | 184562 | 2026-11-12T08:37:04+00:00 |
| `bench/ticket_store.py` | `5c4729a41861d3ce` | 107783 | 2026-11-07T20:50:33+00:00 |

## REQUIRED SECTION 1 — The question

**One question: in a harness that must still be correct in 5 to 20 years, what must be DERIVED rather than TYPED, what must be RECORDED rather than CHECKED, and where does the human-in-the-loop boundary fall when an externally-defined standard changes underneath a stored result?**

The founder's framing, verbatim, 2026-11-13: *"we are building for limitations that exist today. In 5, 10, 15 or 20 years, those limits will become progressively less pressing and less constraining for our purposes. So we should be building not just for today, but for the future also."* And the proposal that follows from it, verbatim: *"when an encoding is loaded, perhaps our classifier model (in this case Haiku) should perform an online check to ensure any encoding matches the existing formal standards, and if not update the encoding dynamically before loading it? This can be a part of the 'Bios' boot up/health check process that the harness performs before an experiment begins? User preferences/constraints don't change, but standards, formal measurements, legislation etc. should always be current? This could slow experiments down if it happened every time. So I would propose a cadence of one month between checks, in order to stay current."* Separately, on model identity: *"sometimes the model names and version numbers can become stale. So in order to fix this fully too, perhaps we can integrate a model name/version check with our aliveness check, so that the harness can stay fully current with whatever models we are using at any given point too?"*

The artefacts under review, each by real path:

- `scripts/standards_currency_and_model_staleness_2026-11-13.py` — the producer for every figure declared below. Run it.
- `bench/cdsfl_registry/domain_vocabulary.py` — resolves a task's consequence domain and its severity scale. The function `consequence_domain` returns how the scale was obtained: own, inherited, composed, or unresolved.
- `bench/confer_maths_panel_2026-09-05.py` — this dispatcher. Its seat table is bound to `_ALL` near line 474.
- `bench/seat_aliveness_2026-10-06.py` — the aliveness probe. It asks whether a route answers.
- `bench/seat_readiness.py` — asks whether a seat is configured. Neither file checks which model version answered.
- `bench/model_catalogue.py` — the generated selectable model list, with a free remote listing that is opt-in.
- `bench/cdsfl_registry/composer.py` — holds per-model calibration keyed on identity strings such as the Fable entry.
- `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md` — the pre-registered definition of a critical finding.

### The 5 sub-questions, all instances of the one question above

**Q1 — COMMENSURATION.** Exactly 4 domains in `bench/cdsfl_registry/domain_vocabulary.py` declare a consequence scale of their own: biology on CTCAE v5.0 grade with a critical cut at Grade 3, chemistry on GHS health hazard category with a critical cut at Category 2, engineering on AIAG-VDA FMEA severity 1 to 10 with a critical cut at 7, and software on CVSS v4.0 base score with a critical cut at High. All 6 pairings of those 4 are incommensurable: no common unit exists, so neither a precedence order nor a strictest-wins rule is defined across them. The other 6 domains declare no scale and inherit one, so they cannot conflict. CC1's proposal is to NEVER commensurate: carry per-domain severities side by side, each in its own named scale, and let the gate fire if any domain sits at or above its OWN critical cut, a disjunction over per-scale cuts. Attack that. Is a disjunction the right aggregator, or does it make the gate fire too readily as domains are added? What is the alternative that does not invent a mapping between CTCAE and GHS?

**Q2 — WHICH WAY THE DEFAULT POINTS.** A researcher's stored preferences must be classified HARD or SOFT. CC1's position is that the default should be MANDATORY, with latitude marked explicitly, because the costs are asymmetric: a process rule wrongly treated as soft fails silently and costs real work, while a style rule wrongly treated as mandatory costs visible rigidity that a human corrects immediately. Attack that. Is the asymmetry real, and does a mandatory-by-default rule increase or decrease the number of times a researcher is interrupted?

**Q3 — DERIVED, NOT TYPED.** A bound written as a literal constant goes stale as the thing it counts grows; a bound computed from the record does not. `scripts/cdsfl_sv.py` already derives its commit timeout from the last 10 ledger rows rather than pinning a number. The question: what is the correct derivation for a bound on a stored preference block's size, given that the usual justification — scarce context — is exactly the limit the founder says will relax? CC1's position is that the justification must move from capacity to CURATION, because curation is a human property that does not improve with hardware. Attack that.

**Q4 — HIS BIOS CURRENCY CHECK, AND ITS HARD-CONSTRAINT BOUNDARY.** Two findings CC1 believes are above threshold and wants broken:

First, a classifier that *updates the encoding dynamically before loading it* has a model editing a HARD constraint with no human in the loop. The project's standing rules are that a proposed repair goes to the human and is never auto-applied, and that a finding is confirmed programmatically or by the human and never by a model vote. A model deciding that a severity scale should change is a model vote on a hard constraint. CC1's repair is DETECT, DO NOT REWRITE: the check raises a ticket through `bench/ticket_store.py` and either refuses the run or records the suspected staleness, and the human rules.

Second, a dynamically-updating encoding BREAKS the archive. Run the producer: at the proposed cadence the record from 2026-08-01 to 2026-11-13 would already carry 4 encoding versions, and nothing stored records which version produced a given severity.

CC1's repair is a COMPOSITION, and it is offered under the founder's own standard. Compose only on a DEMONSTRATED advantage over each repair alone, where the demonstration is a measurement and not a judgement, and prefer the single repair wherever it performs as well; asking merely whether two repairs fail to interfere is the weaker reading that his definition excludes by name. The named property here is FAILURE MODES COVERED, and section 4 of the producer prints the table: a currency check alone covers 1 of 5, per-run provenance alone covers 4 of 5, and the composition covers 5 of 5. Note which way that cuts — provenance dominates the check 4 to 1, and one of the modes provenance closes is CREATED by the check. Attack the table itself: is a failure-mode count a legitimate dominance measurement, or is it a rubric wearing a number? If it is not legitimate, name the measurement that would settle it.

Then attack the cadence. The producer derives the exposure fraction, the share of runs executed under a superseded standard, in closed form; the run rate cancels, so it is a property of the cadence alone. At the worst observed revision rate, the 2-yearly one, a 30-day cadence gives the declared exposure below, and a 1 per cent exposure ceiling would require the declared interval instead. Is a 1 per cent exposure ceiling even the right objective, given that the producer's own figures are an UPPER bound on harm because they count every stale run as exposed whether or not the revision touched the clause in use?

**Q5 — MODEL IDENTITY IS THE SAME DEFECT, AND IT IS LIVE RIGHT NOW.** The founder states the current Fable release is 5.2 and instructed that the dispatch and runners be updated to match before this round. Probed live on the Max subscription through the CLI on 2026-11-13: the model identifier for Fable 5.2 is REAL — the upstream response names its own minimum CLI version — and it is UNREACHABLE from this machine, which runs CLI 2.1.220. The declared patch gap is below. Meanwhile the producer lifts this dispatcher's seat table by executing its syntax tree and finds the 2 free Max-subscription seats pin NO version at all; they name an alias that resolves to whatever the installed CLI serves. So carrying out the instruction literally would either change nothing or kill the seat. Attack the proposed repair: wire a model-identity check to the aliveness probe so that a probe reports WHICH model answered and whether the installed client can reach the intended one, and derive the identifier from a free listing rather than typing it. Where does that fail?

### Declared figures — every one re-executes from the producer

<!-- figure: exposure at a 30-day cadence, worst standard | scripts/standards_currency_and_model_staleness_2026-11-13.py | exposure_T30_GHS = 0.020534 -->
<!-- figure: cadence a 1 per cent exposure ceiling requires | scripts/standards_currency_and_model_staleness_2026-11-13.py | T_max_worst_days = 14.61 -->
<!-- figure: share of live model-identity literals carrying a version | scripts/standards_currency_and_model_staleness_2026-11-13.py | share_version_bearing = 0.253054 -->
<!-- figure: failure modes covered by the composition | scripts/standards_currency_and_model_staleness_2026-11-13.py | composed_covers = 5 of 5 -->
<!-- figure: CLI patch releases missing for the newest Fable | scripts/standards_currency_and_model_staleness_2026-11-13.py | cli_patch_gap_fable_5_2 = 70 -->
<!-- figure: free seats pinning a model version | scripts/standards_currency_and_model_staleness_2026-11-13.py | free_seats_pinning_a_version = 0 -->
<!-- figure: encoding versions the archive would already span | scripts/standards_currency_and_model_staleness_2026-11-13.py | archive_epochs_at_T30 = 4 -->

## REQUIRED SECTION 2 — Use the harness

Form your answer by RUNNING the machinery, not by describing it. A seat that returns prose without having executed anything has not answered this brief.

At minimum, execute all 3 of these:

1. Run `scripts/standards_currency_and_model_staleness_2026-11-13.py` and report what it actually printed. Do not take the declared figures on trust — they are declared so that you can refute them.
2. Import `bench/cdsfl_registry/domain_vocabulary.py` and call `consequence_domain` across every domain it knows. Establish for yourself how many declare an own scale and how many inherit. CC1 previously asserted that 6 of 10 domains have a consequence domain differing from the subject and read that as 2 competing hard constraints; executing the resolver refuted that reading, because those 6 declare no scale and inherit one. Verify or refute the corrected reading.
3. The SEVERITY model is the instrument that bears directly on Q1 and Q4. Severity is what the critical cut is applied to, and the pre-registered definition is in `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`. Establish by execution what the gate currently does when 2 domains are in play, and whether a per-scale disjunction changes any decision the archive has already recorded. A Wilson interval is expected on any proportion you report, as is a second independent route for any number you compute.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a repair is incomplete. A repair without a runnable falsifier that you have EXECUTED is a hypothesis, not a repair. Report the exact command you ran and the output you saw.

Deliver each fix as a file, written INTO the sandbox repository tree at its real path. A fix described in prose is not delivered, and a fix written to scratch space is destroyed when the sandbox is torn down.

Where more than one repair is in play, state composability as the founder defines it: compose ONLY on a DEMONSTRATED advantage over each repair alone, where the demonstration is a MEASUREMENT and not a judgement, and prefer the single repair wherever it performs as well or better. Reporting only that the repairs do not interfere is the weak reading his definition excludes.

Your repair must not be an addition that nothing reaches. Every new flag, gate, subcommand or entry point must be wired to a caller and executed by a test, and the test must go RED when the repair is reverted. State which test, and state what reverting it does.

## REQUIRED SECTION 4 — What would refute you

Before you conclude, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

State it concretely: name the measurement, the file, or the observation that would falsify your position, and say which way the result would have to come out.

If you believe one of CC1's 5 positions is wrong, say which and why, with the executed evidence. Disagreement is wanted as information and will not be smoothed into consensus. There is no requirement that the seats converge.

## REQUIRED SECTION 5 — Output shape

Return exactly these fields, in this order, so replies can be compared without a parser guessing:

1. `VERDICT` — per sub-question Q1 to Q5, one of: CC1 IS RIGHT, CC1 IS WRONG, or UNDECIDABLE ON PRESENT EVIDENCE. One line each.
2. `REASONING` — for each verdict, the derivation. Premises, then the executed evidence, then the conclusion.
3. `EXECUTED FALSIFIER` — the command you ran, verbatim, and the output you saw, verbatim. For every number you report.
4. `FIX` — the real path of each file you wrote into the sandbox tree, and what it changes.
5. `FIX TEST` — the test that goes red when the fix is reverted, and the output proving it did.
6. `STRONGEST DISAGREEMENT WITH THIS BRIEF` — mandatory, never empty. The brief's own framing may be wrong, including the claim that the 5 sub-questions are instances of one question. If you think the framing is sound, say what the weakest part of it is anyway.
7. `COMPOSABILITY` — for any 2 repairs you propose together, the measurement showing the pair beats each alone on a named property, or an explicit statement that the single repair is preferred and why.
8. `PASSES RUN` — how many falsification passes you ran, and what the last one found.

## REQUIRED SECTION 6 — Termination

Stop at diminishing returns, which is this project's own criterion: terminate when a further pass produces no new finding above the real-world-consequence threshold. A finding is above threshold if missing it could cause real-world failure, an invalid result, or an unsafe condition. Do not generate findings for their own sake, do not police style, and do not push back on valid design choices.

Report how many passes you ran. If you terminate after 1 pass, justify it.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 48 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel standards_currency_2026-11-13) -->

Premise confirmed — my first grep was too narrow. `COMMIT_TIMEOUT_LEDGER_ROWS = 10`, `rows[-10:]`, `ledger_max`, `× COMMIT_TIMEOUT_HEADROOM = 4`, floored at `300`. Note it uses **max**, an admissible order statistic — and three typed constants remain. That reshapes Q3.

---

## 1. VERDICT

| | |
|---|---|
| **Q1 — commensuration** | **CC1 IS RIGHT** — disjunction over per-scale transported cuts is the admissible aggregator (z3: `unsat`); the gate that actually ships is the inadmissible one. |
| **Q2 — default points HARD** | **CC1 IS RIGHT** on the asymmetry, but it is already the codified rule, not a proposal; the interruption-*count* question answers against CC1 (it increases). |
| **Q3 — derived, not typed** | **CC1 IS WRONG** — "curation" is not a derivable quantity; it justifies the headroom multiplier, not the bound. The record supplies the scale. |
| **Q4 — BIOS currency check** | **CC1 IS RIGHT** on both findings. The failure-mode *count* is **not** a legitimate dominance measurement (proven partition-dependent); the conclusion survives only via strict set inclusion. The 1 % ceiling is the **wrong objective**. |
| **Q5 — model identity** | **CC1 IS RIGHT**, and the hole I expected to charge it with is closable — I measured the transport-side route and shipped it. |

---

## 2. REASONING

### Q1 — CC1 IS RIGHT, and the brief understates the gap

**Premises.** Severity is ordinal (project's standing ordinal-admissibility section). An aggregator is admissible iff its verdict survives independent strictly-increasing relabelling of each domain's own scale.

**Executed evidence.** The resolver confirms the corrected reading: exactly **4 of 10** domains declare an own scale (biology/CTCAE v5.0/Grade 3, chemistry/GHS Rev. 11/Category 2, engineering/AIAG-VDA FMEA/7, software/CVSS v4.0/High); **6 of 10** return `how="unresolved"` with no application and `how="inherited"` with one. CC1's earlier reading — 6 domains as two competing hard constraints — is **refuted by execution**; `inheriting_domains()` returns exactly those 6, and they declare no scale, so they cannot conflict.

z3, over independent order-preserving relabellings:
- disjunction over each domain's **own transported** cut → `unsat` (verdict cannot flip) — **admissible**
- conjunction over the same → `unsat` — **also admissible**
- mean of two severities vs the **fixed real 0.7** → `sat`, non-degenerate witness: raw `a=1/5, b=1/10` (mean 3/20, below cut) relabels order-preservingly to `pa=9/10, pb=1/2` (mean 7/10, at cut).

**Conclusion.** The admissible aggregators are exactly the monotone Boolean functions of the per-scale indicators. Disjunction is the unique **fail-safe** member, so "is disjunction right?" is a policy question, not an admissibility one — and the brief's worry that it "fires too readily as domains are added" is bounded, not open: only 4 domains can ever contribute a disjunct, and `may_compose` is pairwise, so the fan-in is 1–2, not growing. The alternative that invents no CTCAE↔GHS mapping is conjunction or *k*-of-*n* — both admissible, both under-fire. **Report which disjunct fired**; that preserves the information commensuration would destroy.

Where the brief understates: CC1's proposal is not a change of aggregator from a neutral baseline. The gate that ships is `severity >= CRITICAL_SEVERITY_THRESHOLD = 0.7` on a dimensionless 0–1 number (`bench/reference_runner_v3.py`, duplicated in `bench/evidence.py:794`, pre-registered as "operational proxy" in `CRITICAL_DEFINITION_PREREG_2026-05-18.md`). That **already commensurates all four scales, by collapsing them**, and z3 shows that collapse is breakable. CC1 is right about the destination and the brief is too gentle about the starting point.

### Q2 — CC1 IS RIGHT on the asymmetry; the interruption claim goes the other way

**Premise.** Core directive §1 already states `class(c) = HARD if c is ambiguous (default rule)`. CC1's "position" is the project's standing rule restated — so the verdict is right by codification, not by my measurement, and I say so rather than claim evidence I did not gather.

**Derivation (mine, not measured).** Let *n_s* be soft rules wrongly HARD and *n_h* hard rules wrongly SOFT. Default-HARD maps ambiguity onto *n_s*; default-SOFT maps it onto *n_h*. Cost of a *n_s* error = one visible correction, bounded and immediate. Cost of a *n_h* error = silent failure plus rework, unbounded and discovered late. The asymmetry is real. **But** the count of visible interruptions strictly **increases** under default-HARD: it converts silent soft-treatments into surfaced ones. That is the point of it. Anyone selling mandatory-by-default as *fewer* interruptions is selling the wrong thing — it is fewer *silent failures* at the price of more *visible* ones, and the trade is only good while the correction stays cheap, which depends on latitude marking actually being honoured. I did not execute a measurement here and do not dress the derivation as one.

### Q3 — CC1 IS WRONG

**Premise.** Q3 demands a bound DERIVED, not TYPED. A justification is not a derivation.

**Executed evidence.** The cited precedent is real but not what CC1 describes. `scripts/cdsfl_sv.py` sizes its commit timeout as `max(COMMIT_TIMEOUT_FLOOR, COMMIT_TIMEOUT_HEADROOM * ledger_max)` over `rows[-COMMIT_TIMEOUT_LEDGER_ROWS:]` — with `FLOOR = 300`, `HEADROOM = 4`, `LEDGER_ROWS = 10`. So the project's own exemplar of derive-don't-type is **derived with three typed parameters**. What the record supplies is the *scale*; the policy multiplier stays typed.

Two further things fall out. First, it uses **`ledger_max`** — a selected order statistic, which is admissible under the project's own table, where a mean would not have been. Good precedent, and worth copying deliberately rather than by accident. Second, "curation is a human property that does not improve with hardware" is true and **not a bound**. It is unmeasured and unmeasurable from the record, so a number justified by it is a typed constant wearing a rationale — exactly what Q3 forbids.

**Conclusion.** The correct derivation for a preference-block bound is structurally the `commit_timeout` one: derive the *scale* from the record (the max block size actually honoured over the last *N* blocks — max, not mean), multiply by a typed headroom, floor it. Curation then justifies the **headroom**, which is where a human judgement legitimately belongs, and not the bound. CC1's instinct (the capacity justification expires) is sound; the move it proposes replaces a derivable quantity with an underivable one, which is backwards.

### Q4 — CC1 IS RIGHT on both findings; its table is not a measurement; its cadence objective is wrong

**Finding 1 (no auto-rewrite).** Sound and above threshold. A classifier that *updates the encoding dynamically before loading it* has a model mutating a HARD constraint with no human in the loop — a model vote on a hard constraint, against the standing rule that repairs go to the human. DETECT-DO-NOT-REWRITE is correct, and CC1's ticket route is the right shape.

**Finding 2 (archive-breaking).** Sound, and I measured it **harder than the brief did**. The brief says "nothing stored records which version produced a given severity". Executed over the live tree (harvests excluded): 39 `.jsonl` files, **127,177** records parsed, **809** carrying a `severity`, and **0** carrying any of `scale` / `severity_scale` / `consequence_domain` / `critical_level` / `encoding_version` / `standard_version`. Wilson on 0/809 = `[0.000000, 0.004726]` (two routes agreeing to 1.7e-18); Clopper–Pearson `[0.000000, 0.004549]`. A stored severity is a bare dimensionless number.

That result also answers Section 2 item 3, and answers it **against the brief's premise**. The brief asks whether a per-scale disjunction "changes any decision the archive has already recorded." It cannot be asked: the field the disjunction needs is absent from all 809 records. The honest answer is **NOT MEASURABLE ON THE PRESENT RECORD** — which is a stronger argument for provenance than the one the brief made.

**The table.** The count is **not** a legitimate dominance measurement — it is a rubric wearing a number, and I broke it. A count is `Σ 1[covered]`, a sum over an author-chosen partition. Two refinements of the *same* coverage reverse the ordering:

| partition | check | prov | both | winner alone |
|---|---|---|---|---|
| brief's | 1 | 4 | 5 | provenance |
| refinement A (split F1 per standard: GHS/CVSS/CTCAE/FMEA) | 4 | 4 | 8 | **tie** |
| refinement B (merge F2–F4 into the one archive consequence) | 1 | 2 | 3 | provenance |

Refinement A is not a trick: the check must detect a revision of each of the four feeds, as separable as F2/F3/F4 are from each other. So "provenance dominates the check 4 to 1" is a property of the partition.

**The conclusion survives anyway**, by a stronger and partition-invariant route: `covered(composition) = covered(check) ∪ covered(provenance)`, and `F1 ∈ check \ provenance` in **all three** partitions, so strict set inclusion holds in all three. Composition strictly dominates — as a set fact, not a count. The measurement that would settle the *ranking* is the per-mode **consequence**, each on its own named scale, **selected (max), never summed** — the project's own admissibility rule, which the count violates.

**The cadence.** No, a 1 % exposure ceiling is not the right objective, and the brief half-knows it. Two reasons, one of them new.

The closed form is the **first-order term of a series, not the quantity**. SymPy: the exact union-safe exposure is `1 − 1/(λT) + e^{−λT}/(λT)`, whose series is `λT/2 − λ²T²/6 + O(λ³)` — the producer's `2Tλ/1461` is the leading term. Bias is +1.37 % at T=30/GHS and **+8.38 %** at T=180/GHS. Direction matters and cuts in the brief's favour: the approximation *overstates* exposure, so the exact 1 % ceiling is **14.708 days**, looser than the declared 14.61. No recommendation turns on it. Confirmed three ways: mpmath 40 dps, scipy `brentq`, and Wolfram Language (local Wolfram Engine) which returned series `x/2 - x^2/6 + x^3/24`, value `0.0202556498210766`, root `14.70821909608256`.

What *does* turn on it is verification integrity. The producer advertises its Monte Carlo as an independent route "agreeing on 4 of 4, worst relative error 0.1124." At 12 seeds, 40,000 years, 2M runs the MC sits **−10.7σ** from the producer's form and **−4.2σ** from the exact form at (λ=0.5, T=30), and **−60.2σ** vs **−4.7σ** at T=180. The MC corroborates the *exact* expression and *rejects the form it is printed beside* — at a tolerance wide enough to hide it. A cross-check that cannot distinguish its own answer from one 8 % away is not a second route.

And the objective itself: the producer states its own figures are an upper bound because every stale run counts as exposed regardless of whether the revision touched the clause in use. True harm is `exposure × P(material)`, and `P(material)` is measured nowhere in the project. **Choosing a cadence against an unmeasured objective is the error, not choosing 30 days versus 14.61.** Which is the real argument for provenance over cadence: recording the standard version per run makes exposure retroactively computable, so `P(material)` becomes measurable instead of assumed. Per-run provenance is the repair that earns the cadence decision later; the cadence is a guess made now.

### Q5 — CC1 IS RIGHT, and the obvious objection to it dissolves on measurement

**Executed evidence.** The producer lifts the seat table by executing the dispatcher's syntax tree: 7 seats, 2 free `claude_cli`, **`free_seats_pinning_a_version = 0`** — `cc2` names `opus`, `fable` names `fable`, both aliases. `claude-fable-5-2` requires CLI 2.1.290; `claude --version` on this machine reports **2.1.220**; gap **70** patch releases. So the literal instruction "update the dispatch to Fable 5.2" either changes nothing (the alias already resolves to whatever is served) or pins a model this client cannot reach and kills the seat. Both findings stand.

I expected to charge CC1's repair with a real hole: "a probe reports WHICH model answered" normally means parsing the reply, and a model's self-reported version is a **model vote** on its own identity — exactly what this project forbids. I tested it instead of asserting it. `claude --model opus -p "say ok" --output-format json` returns an envelope carrying `modelUsage: {"claude-opus-5": {...}}` — the **resolved** id, written by the client, not by the model. That is a tool fact, and it closes the hole. CC1's repair is implementable without trusting self-report, and I shipped it.

Census context, independently verified: 145/573 live model-identity literals are version-bearing, `share_version_bearing = 0.253054`, Wilson `[0.219182, 0.290216]` by two routes agreeing to 2.8e-17, Clopper–Pearson `[0.217934, 0.290742]`. 77 of the 145 are in tests — a pin in a test is not a pin in a route, and the producer is right to split them.

---

## 3. EXECUTED FALSIFIER

**Digest check — all 10 artefacts match the dispatch stamps.**
```
$ sha256sum <10 artefacts> | cut -c1-16
83b641df55bb7566  scripts/standards_currency_and_model_staleness_2026-11-13.py
f27c7b6cb0a63f56  bench/cdsfl_registry/domain_vocabulary.py
aea05271596a0a87  bench/confer_maths_panel_2026-09-05.py
9a5c411a63b39fdd  bench/seat_aliveness_2026-10-06.py
084f4f382743484a  bench/seat_readiness.py
dd8518573b38ffbf  bench/model_catalogue.py
88a6f8c910f6d028  bench/cdsfl_registry/composer.py
14a5b7fa2949b134  bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md
0aa813f3476403fc  scripts/cdsfl_sv.py
5c4729a41861d3ce  bench/ticket_store.py
```

**Producer — all 7 declared figures reproduce.**
```
$ python3 scripts/standards_currency_and_model_staleness_2026-11-13.py
  exposure_T30_GHS = 0.020534
  T_max_worst_days = 14.61
  share_version_bearing = 0.253054
    Wilson statsmodels  [0.219182, 0.290216]
    Wilson hand-rolled  [0.219182, 0.290216]
  seat_rows_lifted = 7; free_claude_cli_seats = 2
  free_seats_pinning_a_version = 0
  claude-fable-5-2     needs 2.1.290  installed 2.1.220  gap =  70 patch releases
  cli_patch_gap_fable_5_2 = 70
  composed_covers = 5 of 5
  archive_epochs_at_T30 = 4 encoding versions after 3 checks
```

**Resolver — 4 own scales, 6 inherit.**
```
$ python3 -c "... dv.consequence_domain(d) for d in dv.domains() ..."
domains known = 10
biology        scale=CTCAE v5.0 grade        crit=Grade 3   how(noapp)=own
chemistry      scale=GHS health hazard category (Rev. 11, 2025) crit=Category 2 how(noapp)=own
cross_domain   scale=composed                crit=None      how(noapp)=composed
engineering    scale=AIAG-VDA FMEA severity 1-10 (2019 handbook) crit=7 how(noapp)=own
information_science scale=none               crit=None      how(noapp)=unresolved  how(app=software)=inherited
logistics      scale=none                    crit=None      how(noapp)=unresolved  how(app=software)=inherited
mathematics    scale=none                    crit=None      how(noapp)=unresolved  how(app=software)=inherited
physics        scale=none                    crit=None      how(noapp)=unresolved  how(app=software)=inherited
software       scale=CVSS v4.0 base score    crit=High      how(noapp)=own
statistics     scale=none                    crit=None      how(noapp)=unresolved  how(app=software)=inherited
how==own: ['biology','chemistry','engineering','software'] 4
inheriting_domains(): ['cross_domain','information_science','logistics','mathematics','physics','statistics'] 6
```

**Live CLI probe — the transport names the resolved model.**
```
$ claude --version
2.1.220 (Claude Code)
$ claude --model opus -p "say ok" --output-format json
{"is_error":false,...,"modelUsage":{"claude-opus-5":{"inputTokens":53,"outputTokens":9276,...
```

**My four falsifiers — 4 of 4 demonstrated.**
```
$ python3 scripts/is_a_failure_mode_count_a_dominance_measurement_2026-11-13.py
  partition                     check  prov  both  modes   winner alone
  brief's partition                 1     4     5      5     provenance
  refinement A (split F1)           4     4     8      8            tie
  refinement B (merge F2-4)         1     2     3      3     provenance
  the count's winner changes under repartition = True
  strict SET INCLUSION holds in all 3 partitions = True

  DISJUNCTION over each domain's own transported cut, flip? -> unsat
  CONJUNCTION over the same,                             flip? -> unsat
  MEAN of two severities against the FIXED real 0.7,     flip? -> sat
      raw      a=1/5 b=1/10  -> mean 3/20
      relabel pa=9/10 pb=1/2 -> mean 7/10

  records parsed                                  = 127177
  records carrying a `severity`                    = 809
  of those, carrying ANY scale/version field       = 0

  brief's form : 2*T*lambda/1461
  exact form   : 1 - 1/(T*lambda) + exp(-T*lambda)/(T*lambda)
  series       : T*lambda/2 - T**2*lambda**2/6 + O(lambda**3)
  worst relative overstatement in the table = 0.08379
falsifiers that demonstrated their claim: 4 of 4
```

**Exact ceiling, three routes.**
```
    std    lambda  T_max approx  T_max exact  delta d      rel
   FMEA  0.111111       65.7450      66.1870   0.4420 -0.00668
  CTCAE  0.142857       51.1350      51.4788   0.3438 -0.00668
   CVSS  0.222222       32.8725      33.0935   0.2210 -0.00668
    GHS  0.500000       14.6100      14.7082   0.0982 -0.00668
mpmath findroot GHS T_max = 14.7082190961
scipy  brentq  GHS T_max = 14.708219096082557

$ wolframscript -code 'Print[Normal[Series[1-(1-Exp[-x])/x,{x,0,3}]]]; lam=1/(2*36525/100); Print[N[1-(1-Exp[-lam*30])/(lam*30),15]]; Print[T/.FindRoot[...]]'
x/2 - x^2/6 + x^3/24
0.02025564982107662419242745213921913896`15.
14.70821909608255565139731741792327711491`20.
Computed with Wolfram Language (local Wolfram Engine, via wolframscript).
```

**MC rejects the form it is printed beside.**
```
   lam    T    MC mean     MC sd      exact     approx z vs exact z vs approx
 0.500   30  0.0200773 0.0001477  0.0202556  0.0205339      -4.18      -10.71
 0.500  180  0.1128790 0.0005938  0.1136778  0.1232033      -4.66      -60.23
 0.111   30  0.0044764 0.0000921  0.0045492  0.0045631      -2.74       -3.26
```

**Wilson on 0/809, two routes.**
```
archive severities carrying a scale field: 0/809 = 0.000000
   Wilson statsmodels [0.000000, 0.004726]
   Wilson hand-rolled [0.000000, 0.004726]   max|diff| = 1.735e-18
   Clopper-Pearson    [0.000000, 0.004549]
```

---

## 4. FIX

| real path | what it changes |
|---|---|
| **`bench/model_identity.py`** (new, 170 lines) | Reads the resolved model id from the **transport's** `modelUsage` envelope — never from the model's prose. `resolved_from_envelope`, `parse_required_cli`, `cli_version_gate`, `identity_verdict` → one of `match / mismatch / unreachable / unknown`. Stores **no model name and no version**: `patch_gap = 70` is derived from the refusal's own stated requirement against `claude --version`. Never raises. Reports; never repairs. |
| **`bench/seat_aliveness_2026-10-06.py`** (modified) | `AliveResult` gains `identity`; `probe_seat` gains `identity=`, `probe_roster`/`probe_models` gain `identities=`. `_identity_for` degrades a raising probe to `how="unknown"` and **never** changes `alive` — a reporting check that could refuse a live seat would be worse than the blindness it closes. `identity is None` (never ran) stays distinguishable from `how="unknown"` (ran, transport silent). Identity is not asked of a dead seat. |
| **`bench/confer_maths_panel_2026-09-05.py`** (modified) | `_identity_caller(model_id, route, timeout)` beside the existing `_probe_caller`, returning `None` for routes that cannot report identity (same None-means-unprobeable convention as `caller_for`). The preflight passes `identities=` to `probe_roster` and prints the verdict per seat, including `client short by N patch release(s)`. **Recorded, not gated.** |
| **`scripts/is_a_failure_mode_count_a_dominance_measurement_2026-11-13.py`** (new) | The four falsifiers above, re-runnable. |

I did **not** ship the standards-provenance repair, though my own measurement (0/809) makes it the dominant one. I do not know the severity write path well enough to wire it inside this dispatch, and an unwired addition is precisely this project's most frequent defect — 11 confirmed since 2026-08-01. Specification: stamp each severity record with `(scale_name, standard_version, critical_level)` at the point of judgement, so exposure becomes retroactively computable and `P(material)` becomes measurable. **Unwired and untested by me; treat it as a specification, not a delivery.**

---

## 5. FIX TEST

`bench/tests/test_model_identity_is_measured_not_self_reported_2026-11-13.py` — 20 tests, all fixtures real observations from this machine on 2026-11-13.

```
$ python3 -m pytest bench/tests/test_model_identity_is_measured_not_self_reported_2026-11-13.py -q
20 passed in 0.41s
```

Three independent reverts, each going red:

```
=== REVERT 1: remove model_identity.py ===
ERROR ... test_model_identity_is_measured_not_self_reported_2026-11-13.py
!!!!!!! Interrupted: 1 error during collection !!!!!!!

=== REVERT 2: drop identities= from the dispatcher preflight ===
FAILED ...::test_dispatcher_preflight_passes_identities_to_the_probe
1 failed, 19 passed in 0.24s

=== REVERT 3: probe_seat loses the identity parameter ===
FAILED ...::test_no_identity_probe_is_distinguishable_from_an_unknown_one
FAILED ...::test_a_failing_identity_probe_never_kills_a_live_seat
FAILED ...::test_probe_roster_threads_identities
FAILED ...::test_identity_is_not_asked_of_a_dead_seat
5 failed, 15 passed in 0.25s

=== RESTORED ===
20 passed in 0.22s
```

Revert 2 is the guard against an addition nothing reaches: it walks the dispatcher's AST for a `probe_roster` call passing `identities=` and fails if none exists. `test_self_report_is_not_accepted_as_identity` is the guard on the project's founding principle — an envelope saying `claude-opus-5` against an intent of `fable` must return `mismatch`, no matter what the reply claims.

No regression: `bench/tests/test_seats_must_answer_before_work_is_passed_2026-10-06.py` → **23 passed**; both files together → **43 passed in 0.99s**.

---

## 6. STRONGEST DISAGREEMENT WITH THIS BRIEF

**The claim that the five sub-questions are instances of one question is false, and the false part is Q2.**

Q1, Q3, Q4 and Q5 genuinely share a structure: a value that is *typed* goes stale, so derive it or record its provenance. Identity, encoding version, severity scale and size bound are all the same defect in four places, and that unification is real and useful.

Q2 is not that. A researcher's stored preference is the one thing in the brief that the founder's own framing exempts: *"User preferences/constraints don't change, but standards, formal measurements, legislation etc. should always be current."* So Q2's subject is the explicit **complement** of the other four. Worse, its answer runs the other way: Q1/Q3/Q4/Q5 all conclude "derive it or record it, keep the human out of the loop for the mechanical part," whereas Q2 concludes "default to the human's constraint being binding and interrupt them more often." Folding it in makes the round's thesis look broader than the evidence supports. Four instances of one question, plus one question about where the human sits — which is a genuinely different thing and better argued separately.

**The weakest part of the framing I agree with:** Section 2 instructs seats to establish "whether a per-scale disjunction changes any decision the archive has already recorded." That instruction is unsatisfiable, and the brief could have known it — 809 severity records, 0 scale fields. Asking a seat to execute an unanswerable check invites a fabricated answer; the seat that reports "no decisions change" has reported a measurement it did not take. The instruction should have been "establish *whether the question is answerable* from the record." That the brief's own section 5 notes "nothing in the archive records which encoding version produced a severity" while section 2 asks seats to measure across epochs anyway is an internal inconsistency, and it is the kind that produces a confident false green — exactly the Exp 48 shape the integrity directive archives.

**One smaller thing.** `sev = 3094` is a typed literal in the producer (line 358), printed as "archive severities (de-duplicated frame, B121 symlink correction)" and then used by nothing — the adjacent `cross-epoch share` is `1 - 1/epochs`, which does not reference it. In a producer whose Q3 is *derive, don't type*, and in a sandbox where the archive it counts is absent, that is a number a reader will take for a measurement. Not above the real-world threshold — it feeds no decision — but it is the brief's own thesis failing inside the brief's own instrument.

---

## 7. COMPOSABILITY

**Between my two repairs: no composition claimed. They are independent and address different sub-questions** (Q5 model identity; the falsifier script is an instrument, not a repair). Asserting they compose would be the weak "they don't interfere" reading the founder's definition excludes by name.

**On the brief's composition (currency check + per-run provenance): the demonstrated advantage does not come from the table.** The failure-mode count is partition-dependent — I reversed its ordering twice, and a count is a sum of indicators, inadmissible under the project's own rule. What survives is `covered(composition) = covered(check) ∪ covered(provenance)` with `F1 ∈ check \ provenance` in **all three** partitions tested: strict set inclusion, partition-invariant. So the composition does strictly dominate, but on a set fact, not on 5-beats-4-beats-1.

**And the single repair is strongly preferred as the first delivery.** The named property is *whether the repair's benefit is measurable at all*. Provenance makes exposure retroactively computable, which is what turns `P(material)` from an assumption into a measurement — the check's entire benefit is currently unquantifiable because `P(material)` is measured nowhere. Measured: 809 severity records, 0 carrying a scale or version field, Wilson `[0, 0.004726]`. Provenance also closes F4, a mode the **check itself creates**, so the check cannot ship alone without making the archive worse than it is today. **Order: provenance first, check second, and the check's cadence chosen from data provenance makes available** — not from a 1 % ceiling against an unmeasured objective.

---

## 8. PASSES RUN

**Five passes.**

1. Digests + producer re-execution. All 10 stamps match; all 7 declared figures reproduce.
2. Resolver across all 10 domains. Corrected reading **verified** (4 own / 6 inherit); CC1's earlier 6-as-two-hard-constraints reading **refuted**.
3. Mathematics. Exact exposure derived in SymPy; producer's form shown to be the leading series term; confirmed by mpmath, scipy and Wolfram; MC shown to reject the producer's form at 60σ while sitting 4.7σ from the exact.
4. Instruments. z3 aggregator admissibility; failure-mode count broken by repartition; archive scale-field census (0/809) with Wilson by two routes; live CLI identity probe.
5. Repair + revert. 20 new tests pass, three independent reverts each go red, 23 pre-existing aliveness tests still pass.

**What the last pass found:** the brief's premise about `scripts/cdsfl_sv.py` is correct — my first grep was too narrow and I nearly reported a false refutation of it. Reading the real code changed my Q3 verdict's *reasoning*, not its direction: the precedent uses `ledger_max` (an admissible selected order statistic, not a mean) and carries **three** typed constants (`FLOOR=300`, `HEADROOM=4`, `LEDGER_ROWS=10`). That is what establishes that a bound is never fully derived — the record supplies the scale, the headroom stays typed — which is the precise sense in which CC1's "curation" claim is misplaced rather than merely unproven.

I terminate here. A sixth pass would produce findings below the real-world-consequence threshold: the typed `sev = 3094` (feeds no decision), the producer's asymptotic `1 - 1/epochs` cross-epoch share (0.750000 vs 0.750243 exact at n=3094), and the fact that a `-p` probe in this tree inherits repo context and ran 28 turns at $3.36. All three are recorded above as observations, none is material.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 32 recorded tool call(s).

<!-- verbatim-begin: fable (panel standards_currency_2026-11-13) -->

All machinery executed, fixes shipped and proven red/green. Final answer.

---

## 1. VERDICT

- **Q1 (commensuration by disjunction):** CC1 IS RIGHT.
- **Q2 (mandatory-by-default):** CC1 IS RIGHT — on the default rule, by derivation; the interruption-count claim is derived, not measured.
- **Q3 (capacity → curation):** CC1 IS RIGHT — with one refinement: the derived quantity must be per-entry review currency, not block size.
- **Q4 (detect-don't-rewrite + provenance composition):** CC1 IS RIGHT on both repairs and the composition; **the declared figure `archive_epochs_at_T30 = 4` is REFUTED**, and the 5-of-5 table is a rubric wearing a number — the composition survives on a different, legitimate measurement.
- **Q5 (identity check wired to aliveness):** CC1 IS RIGHT in direction, incomplete as stated: the probe is the "check" column of CC1's own Q4 table; per-reply identity provenance is the dominant half, and the defect is live in `composer.py` today.

## 2. REASONING

**Q1.** Executed: all 10 domains through `consequence_domain` — exactly 4 declare an own scale (biology/CTCAE v5.0 crit Grade 3, chemistry/GHS Rev. 11 crit Category 2, engineering/FMEA-2019 crit 7, software/CVSS v4.0 crit High); 5 inherit (`resolved=False` without an application — an unresolved consequence is *named, never defaulted*), 1 composes; all 6 own-scale pairings return `may_compose = False`. The gate is ∃-quantified over HARD constraints (§1/§2): a critical on any domain's own cut *is* a hard-constraint breach under prereg clause 2, so firing on it is correct, not over-eager. The "fires too readily as domains are added" worry is bounded by construction: only the 4 own-scale domains can ever contribute independent cut events; the 6 inheritors share the application's cut and add no disjunct. The alternatives all fail: conjunction violates prereg clause 2; k-of-n is a model-vote in disguise and requires commensurating "votes"; any precedence order *is* the mapping nobody can define. For reporting (not gating), carry the (value, scale-name) vector and SELECT per scale — never sum, per the admissible-statistics table. Archive effect: 3311 severity records, **0** carry any scale key — every recorded decision was made on the prereg scalar 0.7 proxy, so a per-scale disjunction changes **no recorded decision**; there is nothing recorded on a domain scale to re-aggregate. That absence is itself the F2 gap, confirming CC1's Q4 provenance case from the Q1 side.

**Q2.** CC1's default is §1's own pre-registered rule ("ambiguous constraints default to HARD") applied to stored preferences. The asymmetry is structural: a process rule misclassified SOFT fails silently (prereg clause 4, silent evidence loss — detection unbounded); a style rule misclassified HARD produces visible rigidity corrected once, after which the explicit latitude mark persists. So interruptions under mandatory-by-default are O(#misclassified entries), one-time and decaying; silent failures under soft-by-default recur per run. That is a derivation; no in-repo preference corpus exists to measure the rates, and I say so rather than manufacture one.

**Q3.** A size bound derived from the record ratchets: blocks grow → percentile grows → the bound never binds. So "derive the bound from the record" is the wrong derivation *if the derived quantity is size*. Curation is the right justification (it does not relax with hardware), and the derived quantity it implies is **per-entry review currency** — the analogue of `cdsfl_sv.py` deriving commit timeout from the last 10 ledger rows is deriving a staleness window from recorded human-review timestamps, flagging unreviewed entries for the human (never dropping them — no-benching, applied to preferences). One attack CC1 should absorb: curation *throughput* does improve with tooling (model-assisted curation under human approval), but the approval itself stays human under the project's HIL rule, so the justification holds.

**Q4.** *Detect-don't-rewrite:* a classifier rewriting a severity encoding is a model vote on a HARD constraint and, if wrong, prereg clause 3 (verification-integrity corruption) — the repair routes through `ticket_store` and the human rules. Right, and it is the standing rule restated. *Archive figure:* `days//30 + 1` counts **check boundaries**; an encoding version is created by a **revision**. At the producer's own combined rate (0.976/yr) the expected epochs over 104 days are **1.278**, P(≥1) = 0.243, P(≥3 — needed for "4 versions") = **0.0029** (scipy, mpmath, both routes agree). The qualitative claim survives at any epoch count >1 because 3311/0 records carry no scale key — any partition is invisible — but the declared figure was a 0.3% event stated as what "would already" hold. *The table:* a failure-mode count is **not** a legitimate dominance measurement as arithmetic — it sums author-enumerated, unlike consequences with equal weights, exactly the inadmissible-sum the ordinal doctrine forbids; and "composed covers 5/5" is **trivially guaranteed** (composition coverage ⊇ union of parts coverage, always), so the table cannot come out against composition — an instrument that cannot fail is not a measurement. What *is* legitimate: the set-inclusion is weight-free, and the decision-relevant quantity is the **marginal mode** F1 against the better single repair. The measurement that settles it is the producer's own exposure quantity: provenance alone leaves staleness-detection latency unbounded (a human notices eventually, rate unmeasured); adding the detect-only check bounds it at expected T/2. A ratio-scale, derivable advantage on a named property — that, not 5-vs-4, is the founder-standard demonstration, and it comes out FOR the composition. *Cadence:* the exposure figures are computed from the first-order form; the exact law is **1 − (1−e^{−λT})/(λT)** (derived; SymPy series λT/2 − λ²T²/6…; fresh-seed Monte Carlo within +0.9% of exact and −6.9% from λT/2 at the worst cell; Wolfram Language local-kernel second check: 0.020255650, T_max 14.708 d). No verdict flips at T=30 (1.4% overstatement), but the producer's cross-check had absorbed its own 8.4% truncation error at T=180 under a widened 0.12 tolerance with a single shared seed — a defect in the measurement machinery, now fixed. A 1% exposure ceiling is the wrong objective twice over: exposure is an upper bound on harm (P(material) unmeasured, the producer says so itself), and with provenance in place a stale run is re-scorable, so exposure prices **rework**, not validity; meanwhile the check's own cost — the other side of the cadence trade — is measured nowhere. 30 days is defensible; 14.61 is not required and is in any case 14.71 exactly.

**Q5.** Live evidence, executed: installed CLI is 2.1.220 (verified, matches the producer's typed constant); `_ALL` free seats dispatch bare aliases `opus`/`fable` (read directly); `composer.py` keys calibration `"Fable": "fable_5_1"` — so if the CLI alias ever serves 5.2, fable_5_1-labelled calibration silently misapplies and nothing recorded shows it; archive `source_model` holds display labels only ('Gemini', 'CC2' — no versions). Where CC1's repair fails as stated: (a) **TOCTOU** — a boot-time probe certifies probe-time identity, not dispatch-time; alias repointing or CLI auto-update mid-run escapes it; (b) **self-report** — a probe that asks the model its name measures the model's belief; identity must come from transport metadata (my live metadata probe through the CLI timed out at 120 s in this sandbox — recorded as UNVERIFIED here, not asserted); (c) **the free listing is itself an external currency source** — deriving the identifier from it reintroduces F5 with a new upstream, so it must DETECT and ticket, never auto-rewrite the seat table (the Q4 HIL boundary again, and `model_catalogue.py` already keeps the remote listing opt-in). The structure is identical to Q4: probe = check, per-reply identity = provenance, provenance dominant, composition justified by the same exposure-window measurement. That is also my answer to the brief's one question: identity and encoding versions must be **RECORDED per result**; bounds and tolerances must be **DERIVED from the record**; and the HIL boundary falls exactly at *mutation* — a machine may detect and refuse, only a human may rewrite a hard constraint.

## 3. EXECUTED FALSIFIER

Every number, with the command and the output seen:

- `sha256sum <all 10 artefacts>` → all 10 digests match the dispatch stamps verbatim.
- `python3 scripts/standards_currency_and_model_staleness_2026-11-13.py` (pre-fix) → reproduced all 7 declared figures exactly: `exposure_T30_GHS = 0.020534`, `T_max_worst_days = 14.61`, `share_version_bearing = 0.253054`, `composed_covers = 5 of 5`, `cli_patch_gap_fable_5_2 = 70`, `free_seats_pinning_a_version = 0`, `archive_epochs_at_T30 = 4`.
- SymPy/mpmath/NumPy script (shown above) → `exact E[exposed] = 1 - 1/(T*lambda) + exp(-T*lambda)/(T*lambda)`; series `T*lambda/2 - T²lambda²/6 + O(lambda³)`; T=30: exact 0.020256 vs λT/2 0.020534 (+1.37%); T=180: 0.113678 vs 0.123203 (+8.38%); 5 fresh seeds at (0.5, 180): mean 0.114712 → +0.91% vs exact, −6.89% vs λT/2; exact T_max 14.71 d; combined λ = 0.976190/yr, `expected revisions in 104d = 0.2780`, `P(>=3)=0.002910` (scipy and mpmath identical).
- `wolframscript -code '...'` → `{0.020255649821076083, 14.708219096083182, y/2 - y^2/6}` (Wolfram Language, local Wolfram Engine — second route, agrees with SymPy/mpmath to machine precision).
- Domain enumeration script → `own: 4 ['biology','chemistry','engineering','software']`, 5 unresolved-without-application + 1 composed, all 6 own-pairings `may_compose = False`.
- Extended census script → producer population `145/573 = 0.253054`; provider-agnostic population `532 version-bearing of 960, share 0.554167, Wilson [0.522570, 0.585331]`.
- `claude --version` → `2.1.220 (Claude Code)`.
- Archive scan → `records carrying 'severity': 3311; of those, carrying any *scale* key: 0`; `source_model` values `[('Gemini',745),('DeepSeek',586),('CC2',407),…]`.
- `python3 scripts/the_severity_census_has_three_frames_2026-11-06.py` → frame A content-hash dedup `n = 3094` — the producer's typed constant reproduces from the archive.
- `claude -p 'Reply with exactly one word: Ready!' --model fable --output-format json` → **timed out after 2 m** (exit 143). Reported, not papered over.

## 4. FIX

- `scripts/standards_currency_and_model_staleness_2026-11-13.py` — adds `exposure_exact()` (the exact law, with λT/2 retained and labelled as the first-order upper bound) and `expected_archive_epochs()` (revisions, not check boundaries; prints 1.278 expected, P(≥3)=0.0029); cross-check now tests Monte Carlo against the exact form under a tolerance **derived** from the simulation's own sampling variance (5×SE — my first replacement typed 0.04 and the assert correctly rejected it, which is the thesis demonstrated on its own repair); seat-row tags use provider-agnostic `VER_ANY` (paid seats now correctly read VERSION-PINNED; `free_seats_pinning_a_version = 0` unchanged); census prose names its population (Claude-family only) beside the all-provider recount.
- `bench/seat_aliveness_2026-10-06.py` — `AliveResult` gains `model_reported`/`identity_match`; `probe_seat` accepts `intended_model` and a caller returning `(reply, model_id)`; module function `identity_match()` (alias pins nothing → containment; versioned id → normalised equality). A mismatch never kills aliveness and never benches a seat — recorded for the human. Plain-string callers keep today's behaviour byte-for-byte (23 existing tests pass). Surfacing transport metadata from the orchestrator's call functions is the owed next change, declared here rather than half-shipped.
- `bench/tests/test_standards_currency_fixes_2026-11-13.py` — the five tests below.

## 5. FIX TEST

`python3 -m pytest bench/tests/test_standards_currency_fixes_2026-11-13.py -q` → **5 passed**. Reverted both fixes by content (renamed the added functions, stripped the added fields) → **5 failed**; restored → **5 passed in 1.36s**. Regression: `bench/tests/test_seats_must_answer_before_work_is_passed_2026-10-06.py` → **23 passed**. Producer post-fix: exit 0, cross-check `agree on 4 of 4 against the EXACT form, worst relative error 0.0490` within derived tolerances. (Post-fix the census share reads 0.259386 because the fix and test files themselves add Claude-family literals to the live tree — the instrument now sits inside its own population; the 0.253054 verification was taken pre-fix.)

## 6. STRONGEST DISAGREEMENT WITH THIS BRIEF

The brief's section 3, "measured live on the Max subscription", is **typed, not measured**: `CLI_INSTALLED` and `CLI_REQUIRED` are literal constants (producer lines 70–71). I verified the installed version live (2.1.220 matches) but the required-version figures — and hence `cli_patch_gap_fable_5_2 = 70` — replay a one-time observation that this machine cannot re-execute (my probe timed out). A brief whose thesis is DERIVED-not-TYPED and RECORDED-not-CHECKED ships its model-staleness evidence as exactly the construct it indicts, and labels it "measured live". Secondarily: the five sub-questions *are* instances of one question, but the brief's dominance table is the weakest load-bearing element — an aggregator that is guaranteed to favour composition is not a measurement, and the composition deserved the honest measurement (marginal-mode exposure) it could have had.

## 7. COMPOSABILITY

My two shipped repairs are **not** composed: they fix disjoint defects in disjoint files, no property is improved by their conjunction beyond what each does alone, and each is preferred alone — claiming composition would be the weak "they coexist" reading the founder excludes. On CC1's check+provenance composition: preferred, but on the corrected ground — provenance alone leaves F1's detection latency unbounded; adding the detect-only check bounds it at expected T/2 (0.0205 exposure at T=30, worst λ, by the exact law 0.020256) — a measured advantage on a named ratio-scale property over the better single repair, which the 5-vs-4 count is not.

## 8. PASSES RUN

**4 passes.** (1) Reproduction: all 10 digests and all 7 declared figures re-executed. (2) Falsification: exact exposure law derived and triple-checked (SymPy, fresh-seed Monte Carlo, Wolfram Language local kernel), refuting the producer's closed form at large λT and its seed-correlated cross-check; epoch figure refuted (1.278 vs 4); census population mislabelling found (0.253 is Claude-family-only; all-provider 0.554, Wilson [0.523, 0.585]); archive scale-key absence and `source_model` label-only provenance confirmed. (3) Repair: fixes written, 5 tests green, revert-red demonstrated, 23-test regression clean — and this pass falsified my own first tolerance (typed 0.04 → derived 5×SE). (4) Final: end-to-end producer re-run exit 0, no new finding above the real-world-consequence threshold — the residue is footnotes (naming, prose), so I declare convergence here with the evidence above; the declaration is refutable by the next round per §10.

**Refutation conditions.** My Q4 epoch refutation falls if the proposal is read as *re-stamping the encoding on every check regardless of revision* — show one sentence in the founder's proposal mandating unconditional rewrite and 4 epochs becomes correct (his "if not, update" conditional is why I read it as revision-driven). My exact-law claim falls to any derivation or simulation showing exposure ≠ 1−(1−e^{−λT})/(λT) under Poisson revisions and periodic checks — e.g. a fresh-seed Monte Carlo mean at (0.5/yr, 180 d) settling on 0.1232 rather than 0.1137. My Q1 verdict falls if the archive is shown to contain even one decision recorded on a per-domain scale value that a disjunction would flip — the scan says zero such records exist; produce one. My Q5 verdict falls if the orchestrator's CLI route is shown to surface the resolved model id per reply already — then the provenance half is done and only the wiring to `AliveResult` remains.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/standards_currency_2026-11-13/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
