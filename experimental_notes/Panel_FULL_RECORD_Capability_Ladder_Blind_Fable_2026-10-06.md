# Capability Ladder As A Measured Statistic, blind round, fable seat

Record written 2026-10-06T07:04:34+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. A design question, not a patch: what the capability routing ladder should rank on, now that the founder has ruled it must become a measured statistic rather than a frozen list of vendor names. His words, 2026-10-06: "The routing ladder should be a measured statistic, not simply a list of named vendors based on what you, or I may have read about them on the internet", and "The system shouldn't care at all what a model is called, only what it can be statistically demonstrated to have done." He also ruled the rung cap out entirely: "I don't think there should be a cap at all. If it's a measured statistic, along with capability fingerprinting then the problem should run until it is either resolved, or the ladder is exhausted."

The brief put 6 questions: what the statistic should be, how to handle the selection effect created by routing only firing on unresolved criticals, what bounds spend once the cap is gone, whether routing should be resource-aware, who performs reproducibility checking, and what the brief itself had missed.

WHY A BLIND ROUND FIRST. Star topology, on the founder's standing ruling: a blind round for each seat, then a joint round once every blind round is in. The 2 free seats, fable and cc2, received a byte-identical brief and neither could reach the other's reply. Blindness was verified by measurement rather than assumed from the configuration flag: 0 files in cc2's sandbox carried any of 4 distinctive phrases from this round's reply, and this round's directory was purged from cc2's copy of the evidence tree while the live tree carried it in 4 files. 0 paid dispatches.

WHAT WAS DONE WITH THE FINDINGS. The seat's central objection was accepted and it changes the design question. The heterogeneity figure the brief leaned on, chi-square 280.0138 on 4 degrees of freedom, p = 2.213221e-59, measures per-round FINDING RATE, which is productivity, and not falsification capability. Ranking the ladder on it would put the most productive model first, and that is the model Experiment 55 showed confirming 2 of 2 findings with falsifiers that never read their target. Wiring the ladder to the live capability fingerprint as currently written would therefore reproduce the exact inversion that the provenance gate in scripts/competence_provenance.py exists to prevent, which is crediting a routed confirmation to the model that failed to produce a working test. The cc2 seat reached the same conclusion independently and blind.

2 of the seat's measured claims were already repaired in the live tree before the round closed, and the seat said so: the provenance gate now credits the model that WROTE a routed falsifier rather than the model that filed the finding, and the rung-cap coercion that made exhaustion inexpressible through configuration is removed.

NOTHING THE SEAT DELIVERED WAS MERGED. Fixes are suggested to the human in the loop and never applied automatically. The seat's files are preserved under the seat evidence directory for review.

STILL OPEN AND CARRIED TO THE JOINT ROUND. The seat deliberately did NOT implement the founder's route-back-to-itself ruling for single-seat panels, on the ground that it collides with a pre-registered outcome of experiment 56, and it flagged that as a human decision rather than acting on a verbatim instruction. That judgement is recorded as the seat made it and is for the founder to settle.

## Seats and cost

1 seat(s): `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Design brief — what should decide which model is asked to do the hardest work?

This is a BLIND round. Answer independently. A joint round follows once every blind
reply is in. Your task is to find what is WRONG and to propose what should be built,
not to confirm what exists.

## The situation, measured

`bench/routing.py` routes an unresolved critical finding to progressively stronger
models. It ranks on `DEFAULT_FALSIFIER_STRENGTH = ("Codex","CC2","ChatGPT","Gemini",
"DeepSeek")` — a frozen 5-tuple of VENDOR NAMES derived from Exp 42 in June 2026 and
never re-derived. Its own docstring says it orders "by capability fingerprint"; the
word `fingerprint` appears exactly ONCE in that file, in that docstring, and the code
reads no fingerprint.

Separately `_update_observed_fingerprint` writes a live per-model profile every round,
consumed by `burst_planner.py`. The glossary defines that profile as (D, v-bar, A, C)
including a VERIFICATION score. The 15 fields actually written contain **no
verification score and no coverage dimension** — only context capacity and raw
productivity.

Measured facts you may rely on (verify any you doubt; producers named):
- Real panel finding rates differ: chi-square 280.0138, df 4, p = 2.213221e-59.
  Simulated panel does not: chi-square 3.0084, df 5, p = 0.6987.
  `scripts/the_sim_panel_is_not_heterogeneous_2026-10-05.py`
- `routing_max_rungs` defaults to 2; 0 of 288 config files pin it. `resolve_via_routing`
  STOPS at the first CONFIRMED, so rung 3 runs only when rungs 1 and 2 both failed.
- `competence_provenance.py` credits a confirmation to the model that REPORTED the
  finding, not the one that WROTE the falsifier: 1370 of 16500 archived entries carry
  `resolved_by_routing`, 8.3% credited to the model that failed to write a working test.
- On Exp 55 one model scored 2 of 2 CONFIRMED with falsifiers that opened nothing and
  restated the document from memory; another scored 0 of 2 with genuine readers that
  ERRORed. A naive confirm-rate ranking inverts the correct order.

## The founder's ruling, verbatim

*"The routing ladder should be a measured statistic, not simply a list of named vendors
based on what you, or I may have read about them on the internet. In that sense, our
runners shouldn't care if a particularly named vendor model is available or not. It
should just shunt data around the system based on the performance of all models
(regardless if they are simulated or real) that may be available to the system."*

*"The system shouldn't care at all what a model is called, only what it can be
statistically demonstrated to have done, as per its capability fingerprint. So it
shouldn't matter if all the models are different, or all the models are the same, or if
they are all models from a single vendor, or even a single model operating on its own
(in which case the ladder would just route the issue back to itself and would have
another go at resolving it by using the rest of the machinery of the harness.)"*

*"I don't think there should be a cap at all. If it's a measured statistic, along with
capability fingerprinting then the problem should run until it is either resolved, or
the ladder is exhausted. (No more models to try.)"*

On resources: *"cost in terms of tokens required and tokens that will be used over any
given problem set. That then becomes an issue of load balancing... Problems then get
routed to models with enough capability, AND sufficient resources given the opening
problem set, rather than risking exhausting models due to poor resource/problem
allocation."*

On reproducibility: the project's goal is a STEM calculator — problem in, definitive
repeatable answer out. He asks whether reproducibility should be a separate step
performed by the models, by the human, or both.

## Answer these, each explicitly

1. **What should the ladder rank on?** Name the quantity, its estimator, its minimum
   sample, and what happens to a model with no history. It must be vendor-agnostic and
   must degrade sensibly to a 1-model panel.
2. **The selection effect.** The ladder sends HARD findings to strong models, so their
   success rate is depressed by being trusted. Earlier proposals: measure first attempts
   only (rejected — populations differ at p = 2.2e-59); randomise an audit fraction
   (right identification, but routing fires rarely — is it deployable?); keep the frozen
   order as decider with the rate only as a drift alarm. Which, or what else?
3. **Removing the rung cap.** The founder wants exhaustion, not a fixed budget. What
   stops that becoming unbounded spend, and what is the correct stopping rule?
4. **Resource-aware routing.** Should token budget enter the routing decision alongside
   capability? If so, how, without making a cheap model the default answer?
5. **Reproducibility.** Should it be a separate verification step? Whose?
6. **What have we missed?** Anything in this design that cannot work, or that conflicts
   with the project's additive standard or its no-model-voting rule.

## Deliver your proposal as a FILE

Write any design or repair INTO the sandbox repository tree at its real path, plus any
script you used to check a claim, so it can be re-run. Prose left in the reply is
destroyed at teardown.

## State what would REFUTE you

For each position, name the measurement, file or command whose output would change
your answer. A position with no refutation condition is an opinion.

## Termination

Stop when further work produces no new above-threshold findings — a finding is above
threshold if missing it could cause a real-world failure or a wrong experimental
conclusion. An early stop with a stated reason beats padding.

Include a section headed `## Disagreement` with a real body.

## The mathematical instruments this question touches, and what they should tell you

**gamma** is the decay curve and is LOAD-BEARING — an active convergence condition, not
a report. The two-sided gate requires BOTH `gamma_critical >= 0.30` AND K consecutive
zero-new-critical rounds. A routing change that alters which findings get resolved
alters the critical series, so it moves gamma. Say what your design does to gamma.

**severity** decides in 22 distinct functions across 33 live sites and weights L_n. The
A4 fail-safe now exempts a sub-critical finding ONLY when `severity_is_proven` holds —
the model reproduced its own R_k from its own stated inputs. Any capability statistic
you propose must say whether it is gated the same way, because an UNPROVEN number
opening a gate is the model vote this project forbids.

**Wilson** intervals are required on every proportion you report, and every computed
claim must be cross-verified with at least 2 tools. A capability estimator built on
small per-model samples lives or dies on its interval width — state it.

**rho** is discovery efficiency and **S_k** classifies a FIX, not a claim. If your
estimator reuses either, say which and why it is the right construct.

## Output shape — return exactly these fields

- `## Position` — one paragraph per numbered question, 1 through 6, each answered
  explicitly and separately.
- `## The quantity` — the estimator in full: formula, inputs, minimum sample, cold-start
  behaviour, and its behaviour on a 1-model panel.
- `## What it does to gamma` — the effect on the critical series and the two-sided gate.
- `## Measurements` — every figure with its Wilson interval and the 2 tools that agree.
- `## Delivered files` — paths written into the sandbox tree.
- `## What would refute me` — per position.
- `## Disagreement` — a real body; "none" only if you genuinely have none, said so.


<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 50 recorded tool call(s).

<!-- verbatim-begin: fable (panel capability_ladder_design_blind_2026-10-06) -->

## Position

**1 — What the ladder should rank on.** The glossary's own promised-but-never-written verification dimension `v-bar`: P(admissible CONFIRMED | re-verified falsifier attempt written by model m), credited to the model that **wrote** the falsifier (`resolved_by_routing or source_model` — the runner's own `_falsifier_owner` rule at `reference_runner_v3.py:5437`), where admissible means `reverify_falsifier` returned CONFIRMED **and** the falsifier read the target (the `competence_provenance.py` provenance class), never INTEGRITY_VIOLATION or NON_DISCRIMINATING. Estimator: Jeffreys Beta(1/2,1/2) posterior over admissible **routed** attempts; rank by posterior mean; minimum sample n_min = 5 before the routed posterior alone crosses a non-overlap boundary; no history → prior mean 0.500, ranking the unknown writer between measured-strong and measured-weak — a strict generalisation of `rank_falsifier_writers`' existing ranked+extras rule. Vendor names appear nowhere in the arithmetic; the `-SIM` base normalisation is kept. On a 1-model panel the posterior is the prior and the ladder is the single writer (see Q6 for the route-back-to-self conflict).

**2 — The selection effect.** Condition on the item, not the population. The ladder generates same-finding pairs for free: rung k+1 attempts exactly what rungs 1..k failed, so (B confirms what A failed) is a decisive pairwise win at **any** difficulty mix — difficulty cancels because the item is identical. Decisive pairs order writers inside credible-interval overlap, where selection bias actually bites; both-fail ties are excluded (they inform about the finding, not the pair). First-attempts-only stays rejected; the random audit is right in principle but not deployable as primary — routing fires on 8.3% of archived entries (1370/16500, Wilson95 [0.0789, 0.0873]), and an audit fraction of that stream starves. Instead, the always-on round-stratum falsifier gate (every model's own falsifiers, re-verified every round, selection-free) is the **drift alarm**; the frozen tuple is demoted from decider to deterministic tie-breaker, because its own evidence was never rung-separated: at Exp-42's n≈20 per model, the top-4 Wilson intervals all overlap (Codex [0.699,0.972], CC2 [0.531,0.888], ChatGPT [0.433,0.819], Gemini [0.584,0.919]); only DeepSeek-last [0.145,0.519] is separated.

**3 — Removing the rung cap.** Exhaustion is roster-bounded by construction: one attempt per distinct feasible writer per finding **content-revision** (re-admission only when the finding changed — corrected copy, new evidence), then HIL. Cross-round retry stays confined to transport faults. The spend guard is the Q4 per-finding routing token budget, with budget exhaustion recorded under `routing_deferred_reason` so it can never masquerade as model failure and contaminate v-bar. I proved mechanically that the founder's ruling is currently **inexpressible**: `int(getattr(cfg, "routing_max_rungs", 2) or 2)` coerces both 0 and None to 2, and 0/288 configs pin the field (Wilson95 [0.0000, 0.0132]). Delivered: `max_rungs=None` exhaustion sentinel in `resolve_via_routing` and corrected runner wiring, default 2 unchanged — byte-identical until a config opts in.

**4 — Resource-aware routing.** Yes, as a **feasibility filter, never a ranking term**. Stage 1 ranks purely on v-bar; stage 2 walks the ranked list and skips a rung only when the live fingerprint says the attempt can't fit (`measured_attention_span`/`compression_threshold` — fields `burst_planner.py` already consumes, so this composes with a demonstrated consumer rather than adding a parallel structure) or can't be afforded (estimated attempt cost > remaining budget/quota). Every skip is recorded with its reason. Cost can veto but never score, so a cheap model can never become the default answer — it is only reached when stronger rungs are infeasible, and the record says so.

**5 — Reproducibility.** A separate step, **mechanical, owned by the harness**. `reverify_falsifier` already is reproduction-by-tool; for the STEM-calculator goal, a shipped result carries a replay bundle (falsifier + inputs + environment pin) the runner re-executes N=2 times in fresh scratch; non-reproducing verdicts route to HIL as nondeterministic. Models must not attest their own reproduction — that is a vote. The human audits provenance and forensics; HIL re-derivation is the terminal rung only.

**6 — What's missed.** (a) **The brief's own heterogeneity figure does not license the current fingerprint.** p = 2.21e-59 is on *finding rate* — productivity. The live fingerprint's only discriminating statistic today is that productivity, and ranking on it puts Gemini first (3.646 findings/round, highest of 5) — the model Exp 55 showed confirming 2/2 with detached falsifiers. Wiring the ladder to the fingerprint **as currently written** reproduces exactly the inversion `competence_provenance.py` exists to prevent; the fingerprint must gain admissibility-gated v-bar first. (b) **Crediting was wrong at the measurement layer**: every archived `resolved_by_routing` entry disagrees with the `source_model` key by construction (`route()` excludes the source) — measured 248/248 on the pre-refresh archive slice, 17/17 (Wilson95 [0.8157, 1.0000]) on the current one; `scripts/competence_provenance.py` repaired. (c) **The archive cannot back-derive the statistic**: 100% of multi-rung routing records (87/87 pre-refresh; 12/12, Wilson95 [0.7575, 1.0000], current) carry only the last rung's label — per-writer denominators and pairs were unrecordable; `RoutingResult.attempts` closes this forward. (d) **No-model-voting compliance**: v-bar is built solely from tool verdicts plus mechanical admissibility, and is gated the way `severity_is_proven` gates A4 — an unproven confirmation never enters the numerator; an integrity violation quarantines the writer's statistic (UNSAFE TO RANK ON, enforced at update time). (e) **A real conflict to decide by human, not by code**: the founder's route-back-to-itself ruling vs. exp56's 1-seat arm, whose **pre-registered** reportable outcome depends on the existing empty-ladder `routing_deferred` path. I did not patch it; silently implementing the ruling would change a pre-registered outcome mid-experiment.

## The quantity

v-bar(m): posterior mean (k + ½)/(n + 1) of Beta(½ + k, ½ + n − k), k = admissible CONFIRMED, n = admissible routed attempts by writer m, 95% equal-tailed CrI from Beta quantiles. Round-stratum evidence enters only as a weak prior capped at 2 pseudo-observations (c = min(0.1, 2/n_round)). Order inside CrI overlap: (1) same-finding decisive pairs when ≥5 connect the two writers, (2) the frozen tuple as tie-break, (3) label sort — fully deterministic. Minimum sample n_min = 5; cold start = mean 0.500, CrI [0.002, 0.998], placed between measured-strong and measured-weak. 1-model panel: posterior = prior, ladder = the single writer, stopping rule = exhausted after its attempt → HIL.

## What it does to gamma

`gamma_critical` is estimated over the **settled** critical series and the two-sided gate also requires no unverified critical pending. This design changes settlement, not discovery: exhaustion settles criticals that today stall at rung 2, so the pending side of the gate opens earlier, and convergence is reached by resolving more criticals — never by discarding them. The statistic reads tool verdicts and is read only by rung order: one-way coupling, nothing written into the critical series or either gate side. `test_routing_cannot_flatten_gamma_2026-09-09` passed unchanged on the patched tree (pre-refresh run; the file was removed by the mid-dispatch sandbox re-staging, noted below).

## Measurements

All computed by `scripts/ladder_statistic_demonstration_2026-10-06.py`; every proportion by statsmodels + closed-form Wilson (asserted to agree); posteriors by closed form + scipy.stats.beta; third check via Wolfram Language (local Wolfram Engine): Wilson lower bound for 248/248 → 0.9847465, Jeffreys mean 6/7 → 0.8125, CrI [0.4992, 0.9841] — all agree with the Python tools.

- Routed-resolution crediting disagrees with `source_model`: 248/248 = 100% (Wilson95 [0.9847, 1.0000]) pre-refresh; 17/17 (Wilson95 [0.8157, 1.0000]) current slice.
- Multi-rung records lacking per-rung attempts: 87/87 (Wilson95 [0.9577, 1.0000]) pre-refresh; 12/12 (Wilson95 [0.7575, 1.0000]) current.
- Routing share of archive: 1370/16500 = 8.30% (Wilson95 [0.0789, 0.0873]).
- Configs pinning `routing_max_rungs`: 0/288 (Wilson95 [0.0000, 0.0132]); `int(0 or 2) = 2` proven live.
- Exp-42 order's rung separation at n=20: top-4 intervals overlap (values in Position 2); only DeepSeek separated.
- Heterogeneity re-run: real panel χ² = 280.0138, df 4, p = 2.213221e-59; simulated χ² = 3.0084, df 5, p = 0.6987 (NumPy + scipy agree) — on **finding rate**, not falsification capability.
- Tests: 74 targeted tests passed pre-refresh (9 routing/provenance files); after the harness re-staged the sandbox mid-dispatch (03:35, removing most test files and shrinking `bench/logs/`), my delivered test file still passes 6/6 against the patched modules.

## Delivered files

- `experimental_notes/Proposal_Capability_Ladder_Measured_Statistic_2026-10-06.md` — the full design.
- `scripts/ladder_statistic_demonstration_2026-10-06.py` — re-runnable evidence for every figure above.
- `bench/routing.py` — additive: `RoutingResult.attempts` per-rung (model, verdict); `max_rungs=None` exhaustion sentinel; default behaviour byte-identical.
- `bench/reference_runner_v3.py` — `routing_history.attempts` telemetry; `routing_max_rungs` null/0 → exhaustion sentinel (default 2 unchanged).
- `scripts/competence_provenance.py` — crediting repaired to the falsifier's writer.
- `bench/tests/test_routing_attempts_and_exhaustion_2026-10-06.py` — 6 tests wiring every new surface.

## What would refute me

Per position, as committed in the proposal doc: (1) a paired same-roster run where the v-bar-ordered ladder resolves fewer routed criticals per dispatch than the frozen order (compare `routing_history.attempts` success-at-rung-1 across arms); (2) a pairwise ranking disagreeing with the marginal routed posterior on interval-separated writers; (3) any `max_rungs=None` run producing > |roster|−1 attempts per finding revision (check `rungs_tried` vs `rungs_available`); (4) >5% wrongful skips once skip reasons are recorded; (5) a shipped result whose N=2 replay diverges but HIL finds the verdict correct; (6) a provenance-admissible ranking from a clean run still inverting a known-strong/weak pair — would show admissibility gating is insufficient. For the crediting claim specifically: a single archived entry where `resolved_by_routing == source_model` refutes the by-construction argument (`python3 scripts/ladder_statistic_demonstration_2026-10-06.py`, part 1).

## Disagreement

I disagree with two things the brief leans toward. First, with reading the p = 2.2e-59 heterogeneity as evidence that the live fingerprint can drive the ladder: that statistic measures productivity, and the most productive model on it is the one Exp 55 caught confirming with detached falsifiers — wiring the ladder to the current fingerprint would be the measured inversion, not the measured ladder. Second, with the implied choice among the three Q2 options: all three accept that the deciding sample is the routed stream's marginal rate, and the correct move is to change the *conditioning* (same-finding pairs), not the sampling. I also deliberately did **not** implement the founder's route-back-to-self for 1-seat panels, despite the verbatim ruling, because it collides with exp56's pre-registered outcome — that is a human decision, and a seat implementing it silently would be convergence to instruction rather than to evidence. The frozen tuple is retained as tie-breaker, not deleted: demotion is justified by a committed measurement (interval overlap at n=20); deletion is not, since no replacement yet has a single recorded routed attempt — the additive standard cuts both ways.

Stopping here: the remaining observations (e.g. the 0.85 Jaccard dedup threshold being a non-tool decider) are already flagged and withheld from merge in the runner — below the material threshold.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/capability_ladder_design_blind_2026-10-06/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
