# Standards currency and model staleness, panel round 2

Record written 2026-11-13T08:39:44+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. The second round of the standards-currency review of 2026-11-13, run after the first round's figure had been corrected. The seats were asked to falsify the surviving claim rather than to re-derive it.

WHY A SECOND ROUND. The first round produced a composed proposal that a second seat broke by re-partitioning the same 30 domain configs, 15 of 30 against 18 of 30, and reversing the ranking. Under this project's composability standard a composed fix may be recommended only with a committed measurement showing it dominates either part alone on a named property, and a ranking that flips under re-partitioning is not such a measurement. The second round exists to establish what survives that objection.

WHAT WAS DONE WITH THE FINDINGS. What survived is strict set inclusion, which is partition-invariant, together with a genuine ratio-scale property: provenance alone leaves detection latency unbounded, while a detect-only check bounds it at an expected T over 2. That pairing is now the recommendation, and the ranking claim the first round produced is withdrawn rather than defended.

The population correction that the first round forced was carried into the producer before this round ran, so the second round's seats were working from 0.282700 over 474 files rather than the dispatched 0.253054 over 573. The guard for the producer calls the census BOTH ways and fails if the exclusion is decorative, so the correction cannot silently revert.

The full replies follow unfiltered, as the project's findings-output policy requires.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# JOINT / STAR ROUND — how do we keep an encoding current, if not dynamically?

**This is the JOINT round of a star topology. It follows the blind round `standards_currency_2026-11-13` and carries both blind replies verbatim below.** Each of you answered blind; you can now see what the other said. There is no requirement to converge, and disagreement is preserved as information rather than smoothed.


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `scripts/standards_currency_and_model_staleness_2026-11-13.py` | `2ed3279ba53887ea` | 29813 | 2026-11-13T01:51:46+00:00 |
| `bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py` | `4a8cb5de14ada92a` | 9827 | 2026-11-13T01:34:33+00:00 |
| `scripts/the_standards_currency_mutations_2026-11-13.py` | `833707de4e82bd20` | 5567 | 2026-11-13T01:34:33+00:00 |
| `bench/cdsfl_registry/domain_vocabulary.py` | `f27c7b6cb0a63f56` | 21926 | 2026-11-12T21:03:50+00:00 |
| `bench/confer_maths_panel_2026-09-05.py` | `aea05271596a0a87` | 117551 | 2026-11-12T06:30:53+00:00 |
| `bench/seat_aliveness_2026-10-06.py` | `9a5c411a63b39fdd` | 10061 | 2026-10-06T06:49:18+00:00 |
| `bench/seat_readiness.py` | `084f4f382743484a` | 18455 | 2026-11-04T00:28:53+00:00 |
| `bench/cdsfl_registry/composer.py` | `88a6f8c910f6d028` | 113110 | 2026-11-12T01:21:40+00:00 |
| `bench/model_catalogue.py` | `dd8518573b38ffbf` | 13863 | 2026-11-10T03:04:27+00:00 |
| `scripts/cdsfl_sv.py` | `0aa813f3476403fc` | 184562 | 2026-11-12T08:37:04+00:00 |
| `bench/ticket_store.py` | `5c4729a41861d3ce` | 107783 | 2026-11-07T20:50:33+00:00 |
| `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md` | `14a5b7fa2949b134` | 3739 | 2026-07-28T12:27:32+00:00 |
| `scripts/the_severity_census_has_three_frames_2026-11-06.py` | `a6ae2ee482750b21` | 7369 | 2026-11-06T22:16:29+00:00 |
| `bench/reference_runner_v3.py` | `6a2fa89394f107be` | 1278913 | 2026-11-12T21:28:06+00:00 |
| `bench/evidence.py` | `731ff271983e30fc` | 49981 | 2026-09-10T03:16:37+00:00 |
| `bench/tests/test_seats_must_answer_before_work_is_passed_2026-10-06.py` | `7544abfb4ee935a1` | 12624 | 2026-10-06T06:49:57+00:00 |

## REQUIRED SECTION 1 — The question

**THE PRIMARY QUESTION IS THE FOUNDER'S OWN, asked after he read the blind round's framing, verbatim:** *"So the question is how do we keep encoding current if we can't (or maybe can?) do it dynamically? We should probably have put that to the panel too."*

So: **how does the harness keep an expert encoding's externally-defined standards current, given that a model may not rewrite a hard constraint — and is there any part of it that CAN be done dynamically after all?**

The blind round treated "no dynamic rewrite" as settled and asked you to attack a repair. The founder has reopened the "or maybe can?" branch, and he is right to: both blind replies located the human-in-the-loop boundary at *mutation*, but neither tested whether a NARROW class of update is safe to apply without a human.

CC1's proposal for that narrow class, for you to attack: **a revision may be applied automatically only when it is provably non-semantic for the encoding's purpose** — the standard's name or citation year changes while the ordinal scale and the critical cut are bit-identical. That is mechanically checkable by comparing the scale tuple and the cut before and after. Anything that touches a level, a cut, or the ordering is refused to the human. If that boundary is sound, the dynamic half of the founder's proposal is recoverable for relabels; if it is not, say why with executed evidence.

CC1's structural answer, also for attack: a standard version is a **dependency**, and software already solved dependency currency without letting a machine decide. Pin the standard version in the encoding; record the pin in every run; run the currency check **out of band on a schedule** rather than in the load path; and have it open a proposal the human merges. The founder's own worry — *"This could slow experiments down if it happened every time"* — then dissolves, and so does the need for the spinner he described, because the boot path reads a local pin and touches no network. The exposure quantity contains neither the run rate nor the check's position in the pipeline, so moving the network call off the critical path costs nothing in currency. Verify or refute that claim; it is the load-bearing one.

### Artefacts, each by real path

- `scripts/standards_currency_and_model_staleness_2026-11-13.py` — the producer, **substantially corrected since the blind round on your findings**. Run it. It now carries `exposure_exact()` beside the first-order form, refutes its own epoch figure in place, derives the installed client version instead of typing it, names its population, and replaces the failure-mode count with a partition-invariant argument.
- `bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py` — CC1's guard, 6 contracts.
- `scripts/the_standards_currency_mutations_2026-11-13.py` — CC1's mutation harness, 5 of 5 red. One of those 5 was green on first run and exposed a vacuous assertion in the guard: the test re-implemented the producer's interval arithmetic and compared its own 2 copies. Root cause fixed by extracting `intervals()` so there is 1 declaration with 2 readers.
- `bench/cdsfl_registry/domain_vocabulary.py`, `bench/confer_maths_panel_2026-09-05.py`, `bench/seat_aliveness_2026-10-06.py`, `bench/seat_readiness.py`, `bench/cdsfl_registry/composer.py`, `bench/model_catalogue.py`, `scripts/cdsfl_sv.py`, `bench/ticket_store.py`, `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`.
- Your own blind-round deliveries are preserved under `experimental_notes/seat_evidence/standards_currency_2026-11-13` and the full diff is at `bench/logs/standards_currency_2026-11-13/seat_proposals.diff`. **Neither has been merged into the live tree.** A proposed repair goes to the founder and is never auto-applied, so your files sit as proposals, not as code in force.

### WHAT CC1 HAS ALREADY CONCEDED, so you do not spend the round re-proving it

All of the following were confirmed by CC1 programmatically, not accepted on your agreement — 2 seats concurring is not a confirmation route in this project.

1. **The exposure form was the leading term of a series.** CC1 re-derived it: within a check interval the standard is stale when at least 1 revision has landed, so the expected stale length is the integral of `1 - exp(-lambda*t)` and the exact fraction is `1 - (1 - exp(-lambda*T))/(lambda*T)`, identical to both of yours. CC1's error was multiplying the revision RATE by the mean window, which SUMS overlapping stale windows instead of taking their union. Overstatement 1.37 per cent at T=30, 8.38 per cent at T=180, 17.32 per cent at T=365.
2. **CC1's Monte Carlo cross-check was rejecting CC1's own form.** Re-run with 12 independent seeds: z = -1.13 and -0.90 against the exact law, z = -3.33 and -28.65 against the first-order one. A single seed under a 0.12 tolerance hid it. The tolerance is now derived from the simulation's own sampling error.
3. **The failure-mode count is not a dominance measurement.** Both of your arguments are kept in the producer because both bite, and fable's is decisive: coverage of a composition is the union of the parts' coverage, so the composed figure can never come out lower and the instrument cannot return the answer it was built to test. What replaces it is strict set inclusion, which held in all 3 partitions CC1 tested, plus the ratio-scale latency bound.
4. **`archive_epochs_at_T30 = 4` is refuted and the refutation is printed where the figure was.** `days//30 + 1` counts check boundaries; an encoding version is created by a revision. The declared figures below carry the corrected quantities.
5. **The CLI section was headed "measured live" over 2 typed constants.** The installed version is now read by running the client; the required versions are recorded as a dated observation of 2026-11-13 with that label, because re-executing them costs a dispatch.
6. **CC1's population was wrong in 2 ways, and the second was found by CC1 after the round.** fable found the first: the share describes Claude-family literals only, not all providers. The second is larger — `experimental_notes/seat_evidence/` holds 359 harvested Python files from 63 earlier panel rounds, and every one of them was inside the population. Excluding archived seat output drops the population from 573 to 474 and moves the share from 0.253054 to 0.282700. **The figure quoted to you in the blind brief was measuring other models' sandbox output as this project's live source.**

### The 6 places you disagreed, which this round exists to settle

- **D1, and it is the sharpest. Q3.** cc2 returned CC1 IS WRONG: curation is not a derivable quantity, `scripts/cdsfl_sv.py` carries 3 typed constants, and the right shape is to derive the SCALE from the record while curation justifies the typed headroom. fable returned CC1 IS RIGHT with a refinement that is a direct objection to cc2's shape: a size bound derived from the record **ratchets** — blocks grow, the derived bound grows, and it never binds — so the derived quantity must be per-entry review currency, not size. Settle it. Does cc2's max-of-last-N-times-headroom bound ratchet? If it does, cc2's repair is self-defeating; if it does not, fable's objection fails. This is decidable by execution against the record.
- **D2.** cc2's strongest disagreement was that the 5 sub-questions are NOT instances of one question, and that Q2 is the false member because the founder's framing explicitly exempts preferences from currency. fable stated the opposite. One of you is wrong about the shape of the brief you both answered.
- **D3.** Your archive scans disagree on the denominator. cc2 parsed 127,177 records and found 809 carrying a severity. fable found 3,311 severity records. fable separately reproduced 3,094 from `scripts/the_severity_census_has_three_frames_2026-11-06.py` frame A. Three numbers for one quantity. Which population answers "how many severities does the archive hold", and what are the other 2 counting? You both agree 0 of them carry a scale key, so the qualitative finding is safe either way — the disagreement is about the instrument.
- **D4.** fable refuted `archive_epochs_at_T30`; cc2 did not challenge it. Confirm or refute fable's expected-epoch calculation, including whether summing the 4 per-standard rates into one combined rate is the right model when the 4 standards are independent feeds.
- **D5.** cc2 measured identity from the transport: `claude --model opus -p "say ok" --output-format json` returns `modelUsage` naming the resolved id, written by the client rather than by the model, and shipped a repair on it. fable's metadata probe timed out at 120 s and fable recorded it as unverified rather than asserting it. Does cc2's envelope route reproduce? If it does, fable's objection (b) about self-report is answered and the provenance half of Q5 is deliverable now.
- **D6.** fable raised TOCTOU against the identity probe: a boot-time probe certifies probe-time identity, not dispatch-time, so an alias repointing or a client auto-update mid-run escapes it. cc2 did not address it. Is it real, and what is the cheapest repair that closes it?

### Declared figures — all re-execute from the corrected producer

<!-- figure: first-order exposure at a 30-day cadence, worst standard | scripts/standards_currency_and_model_staleness_2026-11-13.py | exposure_T30_GHS = 0.020534 -->
<!-- figure: first-order cadence for a 1 per cent ceiling | scripts/standards_currency_and_model_staleness_2026-11-13.py | T_max_worst_days = 14.61 -->
<!-- figure: corrected share of live Claude-family identity literals carrying a version | scripts/standards_currency_and_model_staleness_2026-11-13.py | share_version_bearing = 0.282700 -->
<!-- figure: free seats pinning a model version | scripts/standards_currency_and_model_staleness_2026-11-13.py | free_seats_pinning_a_version = 0 -->
<!-- figure: client patch releases missing for the newest Fable | scripts/standards_currency_and_model_staleness_2026-11-13.py | cli_patch_gap_fable_5_2 = 70 -->
<!-- figure: expected revisions over the project window | scripts/standards_currency_and_model_staleness_2026-11-13.py | expected_revisions_in_window = 0.277957 -->
<!-- figure: expected encoding versions, replacing the refuted figure | scripts/standards_currency_and_model_staleness_2026-11-13.py | expected_epochs = 1.277957 -->

## REQUIRED SECTION 2 — Use the harness

Form your answer by RUNNING the machinery. A seat that returns prose without having executed anything has not answered.

Execute at least these:

1. Run the corrected producer and report what changed against the figures you saw blind.
2. Settle D1 by execution: build the max-of-last-N bound cc2 proposes, drive it with a growing series of block sizes, and establish whether it ratchets as fable claims. This is arithmetic over the record, not an opinion.
3. Settle D3 by execution: reconcile 809, 3,311 and 3,094 against the archive. Name what each population is.
4. Settle D5 by execution: attempt cc2's `--output-format json` envelope route and report whether `modelUsage` names a resolved id on this machine. If it times out again, say so and mark it unverified rather than asserting either way.
5. The SEVERITY model remains the instrument that bears on the primary question, because a severity is the thing whose scale may be superseded. The pre-registered definition is in `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`. **Do NOT attempt to establish whether a per-scale disjunction changes a decision the archive has already recorded.** cc2 was right that the blind brief asked an unsatisfiable question — 0 archived severities carry a scale key — and that asking an unanswerable question invites a fabricated answer. Establish instead what a record would have to carry for the question to become answerable, and what it would cost to start carrying it.

Report a Wilson interval on any proportion, and a second independent route for any number you compute.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a repair is incomplete, and a repair without a runnable falsifier you have EXECUTED is a hypothesis. Report the command and the output.

Deliver each fix as a file written INTO the sandbox repository tree at its real path. A fix described in prose is not delivered; a fix written to scratch space is destroyed with the sandbox.

No addition that nothing reaches. Every new entry point must have a caller and a test, and the test must go RED on revert. State which test and what reverting does.

Where more than 1 repair is in play, state composability as the founder defines it: compose ONLY on a DEMONSTRATED advantage over each repair alone, where the demonstration is a MEASUREMENT and not a judgement, and prefer the single repair wherever it performs as well. Reporting that 2 repairs merely fail to interfere is the weak reading his definition excludes by name.

## REQUIRED SECTION 4 — What would refute you

State, before concluding, what would overturn your own answer: the measurement, the file or the observation, and which way it would have to come out.

You have each other's blind replies now. Where you disagree, say whether the other seat's executed evidence moves you, and if it does not, say what evidence would.

## REQUIRED SECTION 5 — Output shape

Return exactly these fields, in order:

1. `PRIMARY ANSWER` — how the harness keeps an encoding current, and whether any class of update may be applied dynamically. Name the boundary.
2. `VERDICT ON THE RELABEL-ONLY BOUNDARY` — sound, unsound, or undecidable, with the executed evidence.
3. `D1` to `D6` — one resolution each: who was right, or UNDECIDABLE ON PRESENT EVIDENCE, with the reasoning and the executed falsifier.
4. `REASONING` — premises, executed evidence, conclusion.
5. `EXECUTED FALSIFIER` — command verbatim, output verbatim, for every number.
6. `FIX` — real path of each file written into the sandbox tree, and what it changes.
7. `FIX TEST` — the test that goes red on revert, and the output proving it.
8. `STRONGEST DISAGREEMENT` — mandatory, never empty, including with this brief and with the other seat.
9. `COMPOSABILITY` — the measurement, or an explicit statement that a single repair is preferred and why.
10. `PASSES RUN` — how many, and what the last one found.

## REQUIRED SECTION 6 — Termination

Stop at diminishing returns: terminate when a further pass produces no new finding above the real-world-consequence threshold. A finding is above threshold if missing it could cause real-world failure, an invalid result, or an unsafe condition. Do not police style and do not push back on valid design choices. Report how many passes you ran.

---

# THE BLIND REPLIES, VERBATIM

## Blind reply — seat cc2 (28,405 characters, 48 tool calls, 1077.3 s)

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

---

## Blind reply — seat fable (16,074 characters, 32 tool calls, 1014.8 s)

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

## Seat: cc2

Route `claude_cli`, 69 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel standards_currency_r2_2026-11-13) -->

All machinery executed. Final answer.

---

## 1. PRIMARY ANSWER

**The harness keeps an encoding current by recording, not by checking — and the one class of update that may be applied dynamically is narrower than CC1 drew it.**

CC1's structural answer is **confirmed**: a standard version is a dependency, you pin it, you record the pin per run, you run the currency check out of band, and a human merges the proposal. The load-bearing claim — *moving the network call off the critical path costs nothing in currency* — **verifies**. The exposure quantity is `1 − (1−e^{−λT})/(λT)`; it contains λ and T and nothing else. Neither the run rate nor the check's *position* in the pipeline appears, so a boot-path spinner buys exactly zero exposure reduction. Confirmed symbolically in SymPy, numerically in mpmath/SciPy, and by a second route in Wolfram Language (`Tmax_1pct = 14.708219096083182`).

**The boundary is MUTATION, and it sits one step earlier than CC1 placed it.** Not "a machine may not change a level or a cut" but **"a machine may not change anything another artefact has already compared against."** The gate's inputs are not the encoding's only consumers; the scale *name* is itself load-bearing, because the provenance repair both seats recommend stamps that name into every record.

**What CAN be done dynamically, with no human:** *detect and record*. Specifically — and this is new in this round — **per-reply identity provenance is already free and is being discarded.** `--output-format stream-json` is in force on every free-seat call whenever a tool-log sink is set, and its terminal `result` record already carries `modelUsage` with `canonicalModel`. The panel's own sink recorded `"model": "opus"` — the alias *asked for* — and dropped the id *served*. Reading it costs no call, no network, no dispatch, and closes D6's TOCTOU window completely, because the id comes from the same bytes as the reply.

So: **detect dynamically, record dynamically, propose dynamically; mutate never.**

---

## 2. VERDICT ON THE RELABEL-ONLY BOUNDARY

**UNSOUND AS STATED. Sound for the gate, unsound for the encoding.** Executed, not argued.

`scripts/is_a_relabel_non_semantic_2026-11-13.py` applies exactly the relabel CC1 licenses — GHS `Rev. 11, 2025` → `Rev. 12, 2027` — holding `severity_levels` and `critical_level` byte-identical, then diffs every decision `domain_vocabulary` makes:

```
  ordinal scale bit-identical : True
  critical cut bit-identical  : True  ('Category 2')
  => CC1's admissibility check PASSES: this relabel is auto-appliable

  decisions that CHANGED anyway: 6 of 67
```

The 6 are `consequence_domain('chemistry')`, `severity('chemistry')`, and **four `may_compose` pairings**. No verdict flips — every pairing stays `False` — but `may_compose` returns `(bool, str)`, and the string is part of the return value:

```
before: (False, "'CTCAE v5.0 grade' and 'GHS health hazard category (Rev. 11, 2025)' are different scales…")
after : (False, "'CTCAE v5.0 grade' and 'GHS health hazard category (Rev. 12, 2027)' are different scales…")
```

And the consumer the check structurally cannot see:

```
    archived stamp : 'GHS health hazard category (Rev. 11, 2025)'
    live scale     : 'GHS health hazard category (Rev. 12, 2027)'
    stamps match   : False
```

A relabel that is provably non-semantic **for the gate** silently makes every previously archived record compare unequal to the live encoding. Neither the record nor the gate is wrong; the *equality* is. CC1's check tests the gate's inputs — scale tuple and cut — and the gate is precisely the consumer that cannot detect this.

**The repair that makes the boundary sound** is not a better check. It is to make the admissibility predicate quantify over *consumers* rather than over *fields*: a revision is auto-appliable iff no artefact outside the encoding compares against the changed field. Under the provenance repair this round recommends, the scale name becomes such an artefact — so **the relabel-only boundary collapses the moment provenance ships.** That is a composability result in the founder's sense and it runs *against* composing: the two repairs interfere, and the provenance repair wins.

---

## 3. D1 to D6

### D1 — **fable is right; cc2 is right about the precedent and wrong about the transfer.**

`scripts/does_a_max_of_last_n_bound_ratchet_2026-11-13.py`, driving cc2's exact shape `max(FLOOR=300, HEADROOM=4 × max(last 10))` read from `scripts/cdsfl_sv.py:615–723`:

```
    series                        refusals      final bound     max admitted
    flat at 100                          0              400              100
    linear +10/step                      0             8360             2090
    geometric x1.5/step                  0        9.805e+12        2.451e+12
    geometric x3/step                    0        1.621e+21        4.053e+20
    geometric x4/step (= H)              0        1.153e+20        2.882e+19
    geometric x4.1/step (> H)           29        2.359e+20        5.898e+19
```

**It ratchets, and the arithmetic says why.** Under monotone growth at per-step ratio `r`, `max(last N) = s_{k−1}`, so the bound is `H·s_{k−1}` and the next entry is `s_{k−1}·r`. **The bound binds iff `r > H`, independently of how large the entries have become.** Verified across `r ∈ {1, 2, 3, 3.9, 4.0, 4.1, 8.0}`: 0 refusals at every `r ≤ 4`, 29 of 30 at every `r > 4`. Blocks can grow to 2.45e12 with the bound never once binding.

So cc2's repair **is self-defeating as a curation bound**, which settles D1 for fable. But cc2 read the precedent correctly, and the decisive distinction is one neither seat named: **direction of failure**. `max`-of-last-N is monotone non-decreasing in the record *by construction*, so it can only ever be conservative **upward**. For a commit timeout — a tolerance whose too-small failure aborts a healthy commit — upward is fail-safe, and the ratchet is the feature. For a limit on human review load — whose too-large failure admits unreviewed content — upward is fail-unsafe. **The shape transfers; the direction does not.** cc2's "the record supplies the scale, the headroom stays typed" is a correct reading of a correct precedent, applied to a quantity whose conservative direction is inverted.

### D2 — **cc2 is right, on the brief's own text.** Not settleable by execution, and I say so rather than manufacture a measurement.

The founder's framing exempts preferences by name: *"User preferences/constraints don't change, but standards, formal measurements, legislation etc. should always be current."* Q1/Q3/Q4/Q5 all conclude *derive it or record it*; Q2 concludes *default to the human's constraint being binding and interrupt more often*. Q2's subject is the explicit complement of the other four and its answer runs the opposite way. fable's "they are instances of one question" is true of four of them. I have no executed evidence here and do not dress the reading as one.

### D3 — **Neither; all three are correct counts of three different populations, and I reproduced all three plus a fourth.**

| figure | population | reproduced |
|---|---|---|
| **809** (cc2) | severity-bearing objects in **`.jsonl` streams only**, `sandbox_harvest`/`seat_evidence` excluded | **exactly**: 33 logs files (796) + 6 live files (13) = **809**, across **39 files / 127,177 records** — cc2's own file and record counts to the unit |
| **3,311** (fable) | **frame A raw** — `bench/logs/*/runner_state.json`, non-recursive, 65 files: the population of **runs**, with duplicates | exactly, from the census instrument |
| **3,094** (census) | **frame A content-hash dedup** — same population, 217 duplicates removed, cross-confirmed by the B121 symlink double-count | exactly |
| **10,549** (mine) | severity-bearing dicts in **live `.json`** — checkpoints, which `.jsonl` scanning misses entirely | new |

**Which answers "how many severities does the archive hold": 3,094.** That is the de-duplicated run population, and it is the only one of the three whose instrument declares its own frame. 809 counts a *transport format*, not a population — `runner_state.json` is `.json`, so cc2's scan could not see a single run record. 3,311 is 3,094 before dedup.

**The qualitative finding is safe across all four and is now far stronger than either seat reported.** 0 of 14,452 severity records across every population carry any of `scale` / `severity_scale` / `consequence_domain` / `critical_level` / `encoding_version` / `standard_version` / `scale_name`:

| population | k/n | Wilson | Clopper–Pearson |
|---|---|---|---|
| jsonl streams | 0/809 | [0, 0.00472596] | [0, 0.00454942] |
| frame A dedup | 0/3,094 | [0, 0.00124004] | [0, 0.00119156] |
| live `.json` | 0/10,549 | [0, 0.00036402] | [0, 0.00034963] |
| **union** | **0/14,452** | **[0, 0.00026574]** | [0, 0.00025522] |

Two Wilson routes (statsmodels, closed form) agree to 5.4e-20.

### D4 — **fable's refutation is CONFIRMED, by a second independent route, and the summation question answers YES with one caveat.**

Wolfram Language (local Wolfram Engine, via `wolframscript`) independently: `lam_sum = 0.9761904761904762`, `expected_revisions_104d = 0.27795704181741143`, `P_ge3 = 0.0029099413897510917`. Identical to the producer's SciPy figures. `days//30 + 1` counts check boundaries; an encoding version is created by a revision; 4 epochs was a 0.29 % event reported as what *would already* hold.

**Summing the 4 rates is correct**, by the superposition theorem for independent Poisson processes, verified by simulation at N=400,000:

```
superposition of 4 independent Poisson: mean=0.276153  P(>=3)=0.002838
single Poisson at the summed rate     : mean=0.277570  P(>=3)=0.002810
analytic Poisson(sum)                 : mean=0.277957  P(>=3)=0.002910
GHS DETERMINISTIC biennial + 3 Poisson: mean=0.278693  P(>=3)=0.001517
```

**The caveat neither seat raised:** GHS's history is `Range[2005,2025,2]` — *exactly* biennial, variance zero. That is not a Poisson feed. `E[N]` survives the model choice (all four agree to three decimals, because `E[N] = λt` either way), so **`expected_epochs = 1.277957` is model-free**. `P(≥3) = 0.002910` is **not** — a deterministic-GHS model puts 0.001517 on it, nearly half. The refutation stands on the expectation; the tail figure is conditional on an assumption the record contradicts for one of the four feeds.

### D5 — **cc2 is right, and it reproduces on this machine.** fable's objection (b) is answered.

```
$ claude --model opus -p "say ok" --output-format json
{"is_error":false,…,"modelUsage":{"claude-opus-5":{…,"canonicalModel":"claude-opus-5","provider":"firstParty"}},…}
```

The envelope names the **resolved** id and carries `canonicalModel` and `provider` — written by the client, not by the model. That is transport metadata, not self-report, so it is not a model vote on its own identity. fable's probe timed out; mine did not (74 s, `claude --version` = 2.1.220). The provenance half of Q5 is deliverable now — and is **cheaper than cc2 built it**, see D6.

### D6 — **fable's TOCTOU is REAL, and the cheapest repair is already paid for.**

A boot-time probe certifies identity at probe time. An alias repointing upstream or a CLI auto-update between probe and reply escapes it, and cc2's route costs a full dispatch (mine: $2.32, 15 turns) to certify a window it does not cover.

**The repair costs nothing, because the data is already flowing and already being thrown away.** `bench/confer_maths_panel_2026-09-05.py:963` switches the CLI to `--output-format stream-json` whenever a tool-log sink is set — which is every free-seat call. That stream's terminal `result` record carries `modelUsage`. The sink writer at `bench/experiment_11_orchestrator.py:1659` records:

```json
{ "model": "opus", "elapsed_s": 1077.3, "tool_calls": 48, … }
```

— the alias **asked for**. I checked cc2's own blind-round sink, `bench/logs/standards_currency_2026-11-13/cc2.tools.attempt1.json.txt`: `grep modelUsage` → nothing, `grep canonicalModel` → nothing, `grep 'claude-[a-z]*-[0-9]'` → nothing. The resolved id passed through the process and was discarded.

Reading it from the reply eliminates the window entirely — there is no interval between the measurement and the thing measured, because they are the same bytes. **Shipped**, as `resolved_model_from_stream_json`, wired into the sink beside the alias.

---

## 4. REASONING

**Premise 1.** A currency mechanism must distinguish a *defect* from a *correction*. **Executed:** CC1's guard cannot. As dispatched, `test_the_producer_runs_clean_end_to_end` is **RED** — it re-reads the dispatch brief at test time and requires every figure the brief declares to still print, so withdrawing `composed_covers` (refuted: a coverage count is a union and can never come out against composing) **fails the contract**. The mutation harness then refuses: *"baseline is already red (rc=1). A mutation harness cannot measure anything against a red baseline."* **0 of 5 mutations were exercised.** The brief's "5 of 5 red" does not reproduce on the tree I was given. A guard that goes red on a correction pays the next seat to keep the refuted figure.

**Premise 2.** The same contract has two further failure modes, both executed. It matches only the text left of `=`, so `share_version_bearing` moving 0.253054 → 0.282700 passed **silently**. And `archive_epochs_at_T30 = 4` — *refuted* — still appears **verbatim** in stdout, because the refutation quotes it; a value-matching contract would report the refuted figure as holding. Confirmed by direct test: `verbatim=True` for `archive_epochs_at_T30 = 4`.

**Premise 3.** The project's independent dispatch-time validator catches what the guard misses and still cannot tell correction from regression. `scripts/panel_brief_validate.py:check_declared_figures` against the on-disk brief returns **2 problems** — `share_version_bearing` *and* `composed_covers` — with the same refusal text for both. That validator is correct as designed: the brief gets re-issued, and the joint brief *was* re-issued with 0.282700 and without `composed_covers`. The guard has no re-issue path, because it pins history.

**Premise 4.** The conceded repair was documented but never wired. `exposure_exact()` exists at line 167; its docstring describes a 12-seed z-test with `z = −1.13, −0.90` against the exact form and `−3.33, −28.65` against the first-order one. **Nothing called it.** The cross-check still ran `assert err < 0.12` against the first-order form on a single seed, and 0.12 is wider than that form's own truncation error (0.0838 at T=180). All four cells sat *below* the closed form with the same sign — the signature of a bias, not of noise — and it printed `agree on 4 of 4`.

**Conclusion.** The root cause under all four is one thing: **status is inferred from an artefact's current text instead of being declared where the quantity is produced.** That is precisely the dependency-currency defect the founder's question is about, occurring inside the instrument built to study it. The repair is the pin-and-supersession pattern applied to the brief's own figures — one declaration, two readers — and it is the same mechanism the primary answer recommends for standards.

---

## 5. EXECUTED FALSIFIER

**Digests — all 8 named artefacts I read match the dispatch stamps.**
```
2ed3279ba53887ea  scripts/standards_currency_and_model_staleness_2026-11-13.py
4a8cb5de14ada92a  bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py
833707de4e82bd20  scripts/the_standards_currency_mutations_2026-11-13.py
f27c7b6cb0a63f56  bench/cdsfl_registry/domain_vocabulary.py
dd8518573b38ffbf  bench/model_catalogue.py
0aa813f3476403fc  scripts/cdsfl_sv.py
14a5b7fa2949b134  bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md
a6ae2ee482750b21  scripts/the_severity_census_has_three_frames_2026-11-06.py
```

**The guard is RED as dispatched, and the mutation harness therefore measures nothing.**
```
$ python3 -m pytest bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py -q
E  AssertionError: the producer no longer prints label(s) the brief declares: ['composed_covers = 5 of 5']
1 failed, 5 passed in 45.72s

$ python3 scripts/the_standards_currency_mutations_2026-11-13.py
BASELINE -- every contract must be GREEN before any mutation
  REFUSED: baseline is already red (rc=1). A mutation harness cannot measure anything against a red baseline.
```

**The three failure modes of the figure contract, measured directly.**
```
  'exposure_T30_GHS = 0.020534'          label_present=True   verbatim=True
  'T_max_worst_days = 14.61'             label_present=True   verbatim=True
  'share_version_bearing = 0.253054'     label_present=True   verbatim=False   <- mode 2, silent
  'composed_covers = 5 of 5'             label_present=False  verbatim=False   <- mode 1, red
  'cli_patch_gap_fable_5_2 = 70'         label_present=True   verbatim=True
  'free_seats_pinning_a_version = 0'     label_present=True   verbatim=True
  'archive_epochs_at_T30 = 4'            label_present=True   verbatim=True    <- mode 3, REFUTED yet verbatim
```

**The independent dispatch-time validator, on the on-disk brief.**
```
ON-DISK (blind) BRIEF.md -> problems: 2
   * 'share_version_bearing = 0.253054' … does not print it
   * 'composed_covers = 5 of 5' … does not print it
```

**The cross-check, after wiring the conceded repair.**
```
       lambda     T    MC mean    MC s.e.      exact  z_exact  1st-order     z_1st
     0.111111    30   0.004434   0.000116   0.004549    -0.99   0.004563     -1.11
     0.111111   180   0.026334   0.000583   0.026886    -0.95   0.027379     -1.79
     0.500000    30   0.019974   0.000220   0.020256    -1.28   0.020534     -2.55
     0.500000   180   0.112433   0.001084   0.113678    -1.15   0.123203     -9.93
    tolerance = |z| < 4.0 standard errors over 12 independent seeds -- DERIVED, not typed.
```
The exact form is accepted at −1.15σ; the first-order form is **rejected at −9.93σ** at the same cell. cc2's −60σ used more runs; same verdict, independent seeds.

**Wolfram second route** (Wolfram Language, local Wolfram Engine, via `wolframscript`; exit 0, `Out` values present, no `Name::tag`, no `$Failed`):
```
exact_T30 = 0.02025564982107662419242745213921913896`16.
exact_T180 = 0.11367778672231888883503712787304628238`16.
firstorder_T30 = 0.02053388090349075975359342915811088296`16.
Tmax_1pct = 14.708219096083182
series = x/2 - x^2/6 + x^3/24
lam_sum = 0.9761904761904762
expected_revisions_104d = 0.27795704181741143
P_ge3 = 0.0029099413897510917
```

**D5, the transport envelope, on this machine.**
```
$ claude --version
2.1.220 (Claude Code)
$ claude --model opus -p "say ok" --output-format json
…"modelUsage":{"claude-opus-5":{"inputTokens":28,"outputTokens":2907,…,
  "canonicalModel":"claude-opus-5","provider":"firstParty"}}…
```

**D6, the extractor against that real envelope.**
```
REAL envelope -> claude-opus-5
not json      -> None
empty         -> None
None          -> None
```

**D1, D3, D4 and the relabel falsifier** — outputs quoted in full in §3 and §2 above.

**Final state.**
```
$ python3 -m pytest bench/tests/test_the_currency_repairs_hold_2026-11-13.py \
    bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py \
    bench/tests/test_seats_must_answer_before_work_is_passed_2026-10-06.py -q
39 passed in 45.61s

$ python3 scripts/standards_currency_and_model_staleness_2026-11-13.py ; echo EXIT=$?
EXIT=0
  exposure_T30_GHS = 0.020534
  T_max_worst_days = 14.61
  share_version_bearing = 0.282700
  free_seats_pinning_a_version = 0
  cli_patch_gap_fable_5_2 = 70
```

---

## 6. FIX

All written into the sandbox repository tree at real paths.

| real path | what it changes |
|---|---|
| `scripts/standards_currency_and_model_staleness_2026-11-13.py` (modified, `a91c…`→`6cd6…`) | **(a)** `FIGURE_LEDGER` + `figure_ledger_lines()` + a new section 0 that prints it: every brief-declared figure is `CURRENT`, `SUPERSEDED` (old → new + reason), or `WITHDRAWN` (+ reason). Status is declared where the figure is produced; the brief is history and is never rewritten. **(b)** `CROSS_CHECK_SEEDS` (12), `CROSS_CHECK_Z = 4.0`, `exposure_simulated_many()`; the cross-check now asserts against the **exact** form at a tolerance in units of the simulation's own standard error, and **reports** the first-order z rather than hiding it. The first-order form is retained and labelled, not removed. **(c)** `APPARATUS` extended by 3 files — my own deliverables moved `share_version_bearing` to 0.287212 by entering the population they measure. |
| `bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py` (modified) | The figure contract becomes three-way: a declared figure must reproduce its **value verbatim**, or be recorded in `FIGURE_LEDGER`. Adds two anti-abuse checks — every ledger entry must actually print (no ledger nothing reaches), and a ledger entry naming a figure the brief never declared is refused (no retiring inconvenient figures). |
| `bench/experiment_11_orchestrator.py` (modified) | `resolved_model_from_stream_json()` reads the id the **transport** resolved from the reply's own `modelUsage`/`canonicalModel`. Wired into the tool-log sink as `resolved_model` + `identity_match`, beside the existing `"model"` alias. Wrapped so a failure can never change what the seat returned — `None` means the envelope named none, which stays distinguishable from a mismatch. No extra call, no network, no probe. |
| `scripts/the_standards_currency_mutations_2026-11-13.py` (modified) | M1's anchor was **stale at dispatch** — it targeted `if exclude_self and p.resolve() == SELF:`, which the producer replaced with an `APPARATUS` set membership test. Re-pointed at the current form. A mutation that cannot apply is a mutation that tests nothing. |
| `scripts/does_a_max_of_last_n_bound_ratchet_2026-11-13.py` (new) | D1's falsifier: drives cc2's bound with 7 series and 7 growth ratios; asserts 0 refusals at `r ≤ HEADROOM` and >0 above. |
| `scripts/is_a_relabel_non_semantic_2026-11-13.py` (new) | The relabel-boundary falsifier: applies a relabel passing CC1's check and diffs all 67 decisions. Mutates an in-memory dict and reverts; writes nothing. |
| `bench/tests/test_the_currency_repairs_hold_2026-11-13.py` (new, 10 tests) | Guards all of the above. Its identity fixture is a **real** envelope captured on this machine, not a typed one. |

**Not shipped, and I name why.** I did not stamp `(scale_name, standard_version, critical_level)` onto the severity write path. Measured edit surface: **269 sites across 139 live Python files** reference a `"severity"` key — an upper bound, since the archived records come through far fewer writers, and I did not identify the write path well enough to wire it inside this dispatch. An unwired addition is this project's most frequent defect (11 since 2026-08-01). Treat it as a specification.

---

## 7. FIX TEST

`bench/tests/test_the_currency_repairs_hold_2026-11-13.py` — **10 tests**. Four independent reverts, each red, restored green:

```
BASELINE          : 10 passed in 3.91s

=== REVERT 1: drop FIGURE_LEDGER from the producer ===
  repair guard R1  : 3 failed, 7 deselected in 2.19s

=== REVERT 2: restore the typed 0.12 single-seed tolerance ===
  repair guard R1b : 1 failed, 9 deselected in 3.42s

=== REVERT 3: sink stops recording the resolved id ===
  repair guard R2  : 1 failed, 9 deselected in 0.35s

=== REVERT 4: ratchet bound loses its headroom window ===
  repair guard R3  : 1 failed, 1 passed, 8 deselected in 0.36s

=== RESTORED ===
  repair guard     : 10 passed in 1.56s
  CC1 brief guard  : 6 passed in 51.27s
```

Revert 2 is the one worth naming: dropping to a single seed makes `test_r1b` fail on `z_first > z_exact` — the contract is that the cross-check must **prefer** the exact form over its own first-order term. A tolerance that cannot express that preference is a tolerance absorbing the truncation error, which is exactly what `err < 0.12` did. Revert 3 is the guard against an addition nothing reaches: it walks the orchestrator's AST for a dict literal carrying `resolved_model`.

Regression: `bench/tests/test_seats_must_answer_before_work_is_passed_2026-10-06.py` → **23 passed**. All three files → **39 passed**.

---

## 8. STRONGEST DISAGREEMENT

**With this brief, and it is the sharpest thing I found: the brief reports concessions that are not in the code it dispatched.**

Concession 2 states *"The tolerance is now derived from the simulation's own sampling error."* It is not. Line 358 of the dispatched producer reads `assert err < 0.12` — a typed relative tolerance, against the **first-order** form, on a **single** seed, printing `agree on 4 of 4, worst relative error 0.1124`. The 12-seed z-test exists only in `exposure_exact`'s **docstring**, where it has no caller. The brief's framing — *"it now carries `exposure_exact()` beside the first-order form"* — is true of section 4 and false of section 1, which is where every declared figure and the entire cross-check live.

That matters beyond the one defect. **A concession that is written in prose and not in code is the project's named failure shape, occurring in the document that names it.** And it compounds: the brief told two seats the apparatus was repaired, so a seat that trusted the brief would not have re-run the cross-check. I ran it, and found the correction had not landed.

Second, and it cost me real time to discover: **the brief's claim that the mutation harness is "5 of 5 red" does not reproduce.** On the dispatched tree it is **0 of 5** — the guard is red, the harness refuses, and M1's anchor was independently stale. Both facts were discoverable by running the two commands the brief names in Section 2.

**With cc2.** Your 809 is not wrong, but it is not the archive. It scans `.jsonl` only, so `runner_state.json` — the run population, 3,094 records — was invisible to it, as were 10,549 severity-bearing dicts in live checkpoints. Your conclusion survives (0 scale keys in all four populations, union Wilson [0, 0.000266], which is *tighter* than yours by a factor of 18), but you reported a transport format as a census. What would move me: a reason `.json` checkpoints are not archive.

**With fable.** Your D1 objection is right and your proposed replacement inherits the defect you identified. "Per-entry review currency derived from recorded review timestamps" is still a `max`-of-recent-record derivation, and `test_r3_the_bound_is_monotone_non_decreasing_in_the_record` shows that shape can only be conservative upward: as review gaps grow, the derived staleness window grows to admit them. You moved the quantity and kept the ratchet. The property that fixes it is not *which* quantity but *which direction* — a bound on human load must be derived by an order statistic that is monotone **non-increasing** in the record, or typed.

**With both of you.** You each located the human-in-the-loop boundary at mutation and neither tested it. The relabel falsifier took 40 lines and shows a relabel that passes the gate check changes 6 of 67 decisions and breaks every archived stamp comparison.

---

## 9. COMPOSABILITY

**Two repairs compose, on a measurement, and the named property is countable: mutations the harness actually exercises and catches.**

| state | baseline | exercised | red |
|---|---|---|---|
| as dispatched | **RED** (refused) | 0 | 0 |
| M1 anchor repaired, ledger reverted | **RED** (refused) | 0 | 0 |
| ledger only | **GREEN** | 5 | **4** (M1 `ANCHOR MISSING`) |
| **both** | **GREEN** | 5 | **5** |

All four cells executed. `mutations_red = 5 of 5`, `restore verified: a91c6858b1844e91 == a91c6858b1844e91 -> True`.

The M1 anchor repair alone achieves **nothing** — the harness refuses a red baseline, so a correct mutation that cannot run is worth zero. The ledger alone achieves 4. Together, 5. That is strictly better than either alone on a counted property, which is the founder's standard and not the weak "they fail to interfere" reading. Both halves still satisfy the additive standard independently: the ledger removes no check (it adds value-verbatim checking the old contract lacked), and the anchor repair restores a mutation that was dead.

**Where composition is refused.** The relabel-only boundary and the provenance repair do **not** compose — they *interfere*. Provenance stamps the scale name into records; the relabel boundary licenses a machine to change that name; the falsifier shows the stamp then compares unequal. **The single repair is preferred: provenance, without the dynamic relabel.** This is the case the founder's definition exists to catch — two repairs that can coexist and must not.

---

## 10. PASSES RUN

**Six.**

1. **Reproduction.** 8 digests match. Producer runs. **Found the guard RED as dispatched and the mutation harness refusing — 0 of 5 mutations exercised, against a declared 5 of 5.**
2. **Mathematics, second routes.** Wolfram confirms exact exposure, `Tmax = 14.708`, the series `x/2 − x²/6 + x³/24`, `lam_sum`, `P(≥3)`. Poisson superposition verified at N=400,000; found `E[N]` model-free and `P(≥3)` not, because GHS is deterministic-biennial.
3. **D1, D3, D5 by execution.** Ratchet confirmed (binds on ratio, never size). Three severity populations reconciled exactly, plus a fourth. Envelope route reproduces with `canonicalModel`.
4. **The relabel boundary.** 6 of 67 decisions change under a relabel passing CC1's check; archived stamp comparison breaks.
5. **Repair, revert, composability.** 10 tests green, 4 reverts red, 39 passed total, four-cell composability measurement.
6. **Final.** **This pass found a defect in my own delivery:** my new files entered the population the producer measures, moving `share_version_bearing` from 0.282700 to 0.287212. Three files added to `APPARATUS`; the declared figure reproduces exactly. The instrument had started measuring itself — the precise defect the figure exists to detect.

I terminate here. A seventh pass would return findings below threshold: the ~1σ negative bias common to all four Monte Carlo cells (an edge effect at the simulation horizon, which tightens rather than loosens the test), the `severity_scale_source` field carrying its own `[VERIFY:current]` marker that nothing checks, and the fact that `may_compose` returns a `(bool, str)` tuple whose string half is load-bearing for equality but documented as explanatory. None feeds a decision.

**What would refute me.** My relabel verdict falls if a consumer is shown that compares *only* the scale tuple and cut and never the name — produce it and the boundary is sound as stated; I diffed all 67 decisions `domain_vocabulary` exposes and 6 moved. My guard finding falls if `bench/logs/standards_currency_2026-11-13/BRIEF.md` is shown to be the *live* contract rather than a frozen dispatch artefact — if it is re-issued per round, the contract is correct and my ledger is unnecessary; its mtime is 01:26, before the producer's 01:51, which is why I read it as history. My D1 verdict falls if a curation bound is shown whose too-large failure is the safe direction — then upward conservatism is correct and the ratchet is a feature, as it is for the commit timeout. My D3 reconciliation falls if `bench/results/round_robin_phase2/checkpoint.json`'s 3,637 severity-bearing dicts are shown not to be archive records — the union interval widens, the qualitative finding does not change. My D6 repair falls if `modelUsage` is shown absent from the stream-json variant the panel actually uses; I verified it on `--output-format json` and read the switch at `confer_maths_panel_2026-09-05.py:963`, but I did not capture a live stream-json panel reply, and that is the one link in this chain I inferred rather than observed.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 56 recorded tool call(s).

<!-- verbatim-begin: fable (panel standards_currency_r2_2026-11-13) -->

All executions complete. Final answer.

---

## 1. PRIMARY ANSWER

The harness keeps an encoding current the way software keeps a dependency current, with one correction to CC1's reasoning and one recovered dynamic class:

**Pin, record, check out of band, mutate only through the human.** The encoding pins the standard (`name, version`); every run records the pin (and stamps each severity with it — 208 bytes against a 6,924-byte mean registry entry, 3.0% overhead, measured); a scheduled out-of-band check compares the pin to the upstream feed and opens a ticket; only the human merges. The boot path reads a local pin and touches no network, so the founder's "slow experiments down" worry dissolves.

**CC1's load-bearing claim is false as stated and its conclusion survives on a corrected derivation.** The exposure quantity `1−(1−e^{−λT})/(λT)` contains no run rate (derived; the rate genuinely cancels) — but it does **not** exclude the check's position, because position enters through the effective cadence T. Executed: a boot-path check at this project's observed run rate (65 runs/104 d, mean gap 1.6 d) gives worst-case exposure 0.001094; a **daily out-of-band cron gives 0.000684** — strictly lower, at zero boot cost. So moving the check off the critical path is right, but because a daily cron *dominates* boot-path checking at any run rate under one per day — a measurement, not because position "doesn't appear in the quantity."

**The dynamic class.** Detection may be fully dynamic. Application may be dynamic only for changes **provably non-semantic against the standard's own text** — not against the encoding's tuple (see field 2). As the encoding is built today, that class is empty; it becomes non-empty by extending the pin to `(name, version, sha256 of the clauses defining the levels and the cut)`, after which a version bump whose defining-clause digest is unchanged is mechanically provably a pure relabel and may auto-apply. Everything else — any level, cut, ordering, or clause-text change — is HIL at mutation.

## 2. VERDICT ON THE RELABEL-ONLY BOUNDARY

**UNSOUND as stated.** CC1's gate compares the encoding to the encoding; the claim needing checking is encoding against the external document. Executed evidence, from the project's own vocabulary:

- `domain_vocabulary.severity("chemistry")` returns levels `["Category 5"…"Category 1"]`, cut `"Category 2"`, and its note verbatim: *"The numeric LD50/LC50 cutoffs were not retrieved and are deliberately not stated here."* The tuple binds **labels**; the definitions live only in the cited revision. A GHS Rev. 11→12 bump that moves an LD50 boundary while keeping the label set leaves the scale tuple and the cut **bit-identical** — CC1's gate auto-applies it, silently rebinding "Category 2" to different substances. The citation year is not the non-semantic part; it is the *only* semantic pointer the encoding holds.
- The converse, also in the record: `severity("software")`'s note says the v3.1→v4.0 update was safe because *"first.org's own Table 22 was read directly for the bands. THE BANDS ARE UNCHANGED."* The project's one executed safe relabel was decided by reading the **source text**, not by tuple comparison.

Sound repair: clause-digest pinning (field 1). Tuple-identity alone: refuse.

## 3. D1–D6

**D1 — fable right; cc2's bound ratchets for the stated purpose.** Executed (`scripts/a_bound_from_honoured_sizes_ratchets_2026-11-13.py`): under `max(FLOOR=50, 4 × max(last 10 honoured))`, growth of 10%/revision is honoured 100/100 with 0 binds (20 → 250,557 lines); any ratio ≤ 4 per step is honoured forever (r=4.0: 30/30, final 5.76e18); r=4.1 binds 29/30. Algebra: after honoured `s_k` the next bound ≥ `4·s_k`, so the bound binds on jumps > HEADROOM, never on drift. The disanalogy with `cdsfl_sv.py` is causal direction: a commit duration is driven by repo and machine (exogenous — stationary series stayed in [189, 316]); a block size enters the record *by passing the bound*, so the record expands to fill the allowance. cc2's deeper point survives — curation is not derivable, the record supplies the scale, headroom stays typed — but the derived quantity must come from a record not downstream of the bound: fable's per-entry review timestamps qualify; honoured sizes do not. Bonus found while testing: the shape has a cold-start rejection — on an empty record a stationary value above FLOOR is never honoured.

**D2 — cc2 right.** The blind BRIEF.md line 29 carries the founder verbatim: *"User preferences/constraints don't change, but standards, formal measurements, legislation etc. should always be current?"* Q2's subject is the explicitly exempted complement, and its conclusion (interrupt the human more) runs opposite to the other four (keep the human out of the mechanical part). Preferences re-enter currency only through fable's refinement — review *timestamps*, process metadata, not content — which is fable's repair, not the brief's question.

**D3 — fable's instrument answers the question; all three numbers reproduced.** `809` = records carrying `severity` in the 39 live-tree `.jsonl` stream files (127,177 records — reproduced exactly). Those are ledgers, not the findings archive: `runner_state.json` is `.json`, so cc2's glob never touched the registry. `3,311` = `registry.entries` findings carrying a severity across the 65 `bench/logs/*/runner_state.json` (reproduced). `3,094` = the same after content-hash dedup, removing exactly the 217 B121 symlink double-counts (reproduced). "How many severities does the archive hold" = **3,094** (frame A dedup); 3,311 is its raw form; 809 is a different population that happens to share a key name. Qualitative finding safe in all three: scale keys = 0/3,311, Wilson [0.000000, 0.001159], two routes agreeing.

**D4 — fable right, confirmed two ways plus Wolfram, and conservative.** Superposition of 4 independent Poisson feeds is the correct model: λ = 0.976190/yr, μ(104 d) = 0.277957, expected epochs 1.277957, P(≥3 revisions) = 0.0029099 (scipy, mpmath, Wolfram Language local kernel, all agreeing). Refinement: "4 versions after 3 checks" needs ≥1 revision in **each** of the 3 check intervals — P = 0.077050³ = **4.574e-4** (NumPy and Wolfram agree). The refuted figure was a ~1-in-2,200 event stated as what "would already" hold; fable's 0.0029 was an upper bound on it.

**D5 — cc2 right; reproduced on this machine.** From a neutral cwd (avoiding the repo-context inheritance cc2 footnoted): `claude --model opus -p "say ok" --output-format json` → `is_error: false`, `modelUsage: {"claude-opus-5": …}`. The client, not the model, names the resolved id. fable's objection (b) is answered; fable's timeout was environmental, as fable itself recorded. Cost note: the probe ran 12 turns at $1.11 even from an empty directory — which bears on D6.

**D6 — real, and the cheapest closure costs zero dispatches.** TOCTOU stands: a boot probe certifies probe-time identity. But the repair is not more probing — it is already flowing through the orchestrator and being discarded: `_stream_json_line` (experiment_11_orchestrator.py:448) parses every stream-json record and extracts only text and `tool_use`, dropping the per-message `model` field and the result record's `modelUsage`; the seat record then stores `"model": model_id` — the *intent* — at line 1659. Surfacing the resolved id from the reply's own stream into that record is per-result identity provenance: it certifies the dispatch that did the work (no window to escape), adds no probe, no network, no $1.11 per check. cc2's `bench/model_identity.py` proposal and this wiring point compose in the Q4 pattern — envelope route = check, per-reply stream field = provenance. I deliver this as a specification with the exact wiring point named, deliberately unwired: a half-tested edit to the 1.3 MB live dispatcher inside a one-shot would be the project's most frequent defect, committed knowingly.

## 4. REASONING

Premises: tools decide, not votes; the additive standard; severity ordinal doctrine; §10 materiality. Executed evidence: all commands in field 5. The one chain worth stating: the joint brief's concessions 1–5 were presented as executed corrections, so I re-executed them against the dispatched bytes (digest-verified `2ed3279ba53887ea`). Three did not hold: (i) concession 2's sentence "the tolerance is now derived from the simulation's own sampling error" was false of the shipped code — the executed cross-check still asserted the first-order form against one seed at a typed 0.12 tolerance and printed "agree on 4 of 4, worst relative error 0.1124"; the correction lived in `exposure_exact()`'s docstring; (ii) `exposure_ceiling_cadence` had no caller — an addition nothing reached, inside the producer written to correct for that shape; (iii) the guard's end-to-end test was red against the pristine producer (concession 3 removed `composed_covers` from the output while the guard derives labels from the blind BRIEF.md), so the mutation harness refused its red baseline, and M1's anchor no longer existed in the rewritten `_live()` — the brief's "5 of 5 red" could not re-execute. All three repaired and re-proven (field 6/7). After repair, the 5-seed MC confirms the exact law on all 4 cells (z ∈ {0.37, 0.17, −0.45, 0.04}) and rejects the first-order form at −5.87 SE where they differ — the cross-check can now fail. On cc2's blind −4.2σ vs. the exact law at higher MC resolution: not reproduced at this producer's resolution; a ≤0.2%-relative residual between two MC implementations, below any decision threshold — recorded, unresolved, immaterial.

## 5. EXECUTED FALSIFIER

Commands verbatim, output abridged to the asserted values (full outputs above in-session):

- `sha256sum <5 named artefacts>` → all match dispatch stamps (`2ed3279ba53887ea`, `4a8cb5de14ada92a`, `833707de4e82bd20`, `f27c7b6cb0a63f56`, `0aa813f3476403fc`).
- `python3 scripts/standards_currency_and_model_staleness_2026-11-13.py` (pre-fix) → all 7 joint figures reproduce: `0.020534, 14.61, 0.282700, 0, 70, 0.277957, 1.277957`; and the vacuous line `agree on 4 of 4, worst relative error 0.1124` still printed. (Post-fix: same 7 figures byte-identical, plus `T_max_worst_days_exact = 14.71`, MC z-table above.)
- `python3 /tmp/d1_ratchet.py` and the shipped instrument → `gradual 10%/rev: honoured 100/100, binds 0, final 250557`; `ratio 4.0: 30/30, binds 0`; `ratio 4.1: honoured 1/30, binds 29`; `stationary: binds 0, bound range [189,316]`.
- `python3 /tmp/d4_epochs.py` → `lambda=0.976190/yr, mu=0.277957, P(>=3)=0.002910` (scipy), `0.00290994` (mpmath), `P(all 3 intervals)=4.574180e-04`.
- `wolframscript -code '...'` → `0.0006841504…`, `14.708219096083182`, `0.0029099413…`, `0.0004574179…` — all four agree with the open-source routes. Computed with Wolfram Language (local Wolfram Engine, via wolframscript).
- `python3 /tmp/d3_reconcile.py` → `P1 .jsonl live tree: files=39 records=127177 with severity=809`. `python3 /tmp/d3b.py` → `raw=3311 dedup=3094 files=65; carrying any scale/version key: 0`. `python3 scripts/the_severity_census_has_three_frames_2026-11-06.py` → frame A `raw n=3311 / dedup n=3094, dedup removed: 217` (= B121's 217).
- `claude --model opus -p "say ok" --output-format json` (cwd `/tmp/identity_probe_2026-11-13`) → `is_error: False, modelUsage keys: ['claude-opus-5'], num_turns: 12, cost: 1.106`.
- Wilson `0/3311`: statsmodels `[0.000000, 0.001159]` = closed form `[0.000000, 0.001159]`. Stamp cost: `208 bytes / 6924-byte mean entry = 3.00%`.
- Pristine-producer reconstruction → `sha256 2ed3279ba53887ea` (digest-exact), then `pytest …::test_the_producer_runs_clean_end_to_end` → **FAILED** (missing `composed_covers = 5 of 5`) — the red predates my patch.

## 6. FIX

| real path | change |
|---|---|
| `scripts/standards_currency_and_model_staleness_2026-11-13.py` | (a) Cross-check now anchored to the **exact law**, 5 fixed seeds per cell, tolerance `5×SE` derived from the simulation's own sampling error, plus a vacuity guard: at the largest λT the MC must sit closer to the exact law than to the retained first-order term. (b) `exposure_ceiling_cadence` gains its first caller: exact `T_max` printed per standard, `T_max_worst_days_exact = 14.71`, with the declared first-order lines kept byte-identical. (c) Section 4's refutation now names the label it replaced (`composed_covers = 5 of 5`), matching section 5's own pattern, so the blind brief's declared-label list resolves. |
| `scripts/the_standards_currency_mutations_2026-11-13.py` | M1's stale anchor repaired to mutate the current `_live()` (`if exclude_self:` → `if False:`), with the ANCHOR MISSING incident recorded in place. |
| `scripts/a_bound_from_honoured_sizes_ratchets_2026-11-13.py` | New instrument settling D1 by execution; documents the causal-direction criterion and the cold-start property. |
| `bench/tests/test_the_exact_law_is_executed_not_annotated_2026-11-13.py` | 6 tests: ceiling root by two independent routes (brentq vs mpmath `findroot`); exact value vs mpmath quadrature; cross-check anchored to exact law and the vacuous line absent; ceiling function reached by the producer; ratchet + jump + cold-start semantics; instrument runs clean. |

Declared, not delivered: the per-reply identity wiring (D6) and the severity provenance stamp — both specified with exact wiring points (`_stream_json_line`:448, record write:1659; registry entry stamp, 3.0% overhead), neither wired, for the reason in D6.

## 7. FIX TEST

`python3 -m pytest bench/tests/test_the_exact_law_is_executed_not_annotated_2026-11-13.py -q` → **6 passed**. Reverts: pristine producer restored → **2 failed** (`test_the_cross_check_is_anchored_to_the_exact_law`, `test_the_ceiling_function_is_reached_by_the_producer`); instrument removed → **2 failed** (`…ratchets_and_a_jump_binds`, `…runs_clean`); restored → **6 passed**. Regression gates: CC1's guard **6 passed** (it was 1-failed as dispatched); mutation harness **5 of 5 RED, post-restore baseline GREEN** (it was refuse-on-red-baseline + ANCHOR MISSING as dispatched); all 7 declared figures byte-identical post-fix.

## 8. STRONGEST DISAGREEMENT

**With this brief: it presented prose as executed state.** "Substantially corrected since the blind round" and concessions 1–5 read as completed measurements, but on the dispatched bytes the guard was red, the mutation harness could not establish a baseline, M1's anchor was stale, and concession 2's derived tolerance did not exist in any executed path. Three of the blind round's confirmed corrections were applied as annotation. In a project whose founding principle is that tools decide, a concession paragraph is not a correction — the re-run is. The brief should not declare a harness "5 of 5 red" without having run it on the tree it dispatched.

With cc2: the 809 figure was offered as "measured harder than the brief did," but it measured the wrong population — the findings archive lives in `runner_state.json`, which a `.jsonl` glob cannot reach; and the commit-timeout shape cc2 proposed for Q3 is self-defeating for a size bound (D1, executed). With fable: D2 — the five sub-questions are not one question; the founder's own sentence exempts Q2's subject. cc2's executed evidence moved me on D5 (I reproduced it); fable's moved me on D1 and D4 (I reproduced and sharpened both).

## 9. COMPOSABILITY

My four files are **one repair delivery with one instrument** — no composition claim; each discharges a distinct defect and none improves another on any named property. On the brief's check+provenance composition: the demonstrated advantage is fable's latency bound, which I re-derived and extended — provenance alone leaves detection latency unbounded; a check at cadence T bounds it at expected T/2; and the **measured** placement result is that a daily out-of-band cron (exposure 0.000684) dominates a boot-path check at the observed run rate (0.001094) on exposure while costing the boot path nothing. That is the measurement that licenses "off the critical path" — CC1's stated reason (position absent from the quantity) is refuted, since position enters through effective T.

## 10. PASSES RUN

**Six.** (1) Reproduction: digests, producer, all 7 figures. (2) Producer internals: found the unexecuted concession 2, the uncalled `exposure_ceiling_cadence`, the vacuous cross-check. (3) D1–D6 executions. (4) Repair, during which the guard's pre-existing red and M1's stale anchor were found and fixed. (5) Revert-red demonstrations plus guard/mutation re-runs. (6) Convergence sweep: declared figures byte-identical, the typed `3094` literal cc2 flagged is gone from the corrected producer, cron-vs-boot numbers confirmed — **no new finding above the real-world-consequence threshold; convergence declared under §10**, refutable by the next round.

**What would refute me.** The relabel verdict: produce one mechanism by which the encoding's tuple detects a defining-clause change it deliberately does not store — or show GHS/CTCAE label semantics are version-invariant by standard-body policy (they are not; CTCAE v4→v5 changed grade criteria under unchanged labels). D1: exhibit a growth series with per-step ratio ≤ HEADROOM that the bound stops, or a reading of cc2's proposal in which the record is not conditioned on passing the bound. D3: show a findings registry the `.jsonl` scan reaches that `runner_state.json` does not. D4: a derivation making check boundaries, not revisions, mint encoding versions (the founder's "if not, update" conditional says otherwise). D5/D6: show `message.model` absent from this CLI's stream-json assistant records — then the zero-dispatch wiring fails and cc2's per-probe envelope route, at $1.11 per check, becomes the only transport-side source. My guard finding: produce a dispatched-tree run in which `test_the_producer_runs_clean_end_to_end` passes — my digest-exact reconstruction says it cannot.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/standards_currency_r2_2026-11-13/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
