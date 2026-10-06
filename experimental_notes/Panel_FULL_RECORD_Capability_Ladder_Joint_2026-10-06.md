# Capability Ladder As A Measured Statistic, joint round

Record written 2026-10-06T07:44:51+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT THIS ROUND IS. The joint round of a star-topology panel on what the capability routing ladder should rank on. Both blind rounds were collected first and neither seat could read the other; this round hands each seat the other's full position for the first time. The brief put 5 questions drawn from where the 2 blind positions actually diverged, and it stated explicitly that changing a position for a stated reason and refusing to change it for a stated reason are equally good outcomes, while changing it for no stated reason is the only bad one. No compelled convergence.

WHAT THE ROUND PRODUCED THAT THE BLIND ROUNDS COULD NOT. A seat reversed its own blind-round derivation, with a quantified refutation rather than a concession.

In the blind round, one seat derived that NO minimum sample is needed before the ladder statistic may rank, on the ground that under exhaustion every rung is tried regardless of its estimate, so a poor estimate can only misorder cost and can never exclude a rung. In the joint round the same seat refuted that derivation by attacking its premise: both blind positions retain a token budget that can halt the climb, and a ledger that halts mid-ladder IS a cap, differing from a configured rung cap only in that its threshold is data-dependent. Truncation is exactly where the symmetry argument dies.

The refutation is computed, not argued. With a cap of 2 on 3 rungs, the difference in resolution probability between the orderings 1,2,3 and 3,2,1 is the product of the first and third rungs' probability gap with the complement of the second, which is not identically zero. SymPy and Wolfram Language agree on the factorisation and both report that it does not simplify to zero. A witness at probabilities 0.9, 0.1 and 0.01 gives 0.910000 against 0.109000, a loss of 0.801000 in resolution probability from ordering alone. A measured table over 20000 NumPy trials then gives the expected resolution probability lost per finding as a function of how many observations per rung the estimate rests on and how deep the budget truncates: at the current effective depth of 2 rungs, requiring 5 observations before ranking rather than ranking on 1 is worth 0.0506 expected resolution probability per truncated finding. At depth 5, where no truncation occurs, the loss falls to 1.166 times 10 to the minus 19 for every row, which reproduces the original derivation exactly in the regime where it holds.

So the minimum sample is not a safeguard against a bad estimate in general; it is worth the probability of truncation multiplied by that loss, and it is worth nothing if and only if truncation is impossible, which neither position proposed.

ORDER-INVARIANCE WAS ACCEPTED AND STRENGTHENED. The claim that under exhaustion the ladder's order cannot change WHICH findings resolve, only what they cost, was accepted, and extended: because the event is the failure of a SET of rungs, invariance holds for an arbitrary joint failure law, correlated or not, and needs no independence assumption at all. Verified by exhaustive enumeration over all 32 joint outcomes of 5 rungs under 200 random Dirichlet laws against all 120 orderings, with a maximum spread of 0. The product form is the factorising special case.

TWO CORRECTIONS THE ROUND MADE TO ITS OWN SIDE. The blind position had written "24 orderings of 5 rungs", and 5 factorial is 120, not 24; the conclusion is unaffected but the count was wrong. And order-invariance FAILS for that same position's own proposed aid-level lattice, because defining a rung as carrying the previous rung's falsifier source makes a rung's success probability depend on which rung preceded it, so the failure events stop being an order-free set. The cost half of that interaction had been flagged in the blind round; the probability half had not.

A STATED REFUTATION CONDITION WAS FOUND TO BE OVER-BROAD AND ALREADY MET. The blind position had offered, as a falsifier of order-invariance, that it falls if any path marks a finding resolved without a confirmation from the re-verification function. The routing module's duplicate early return does exactly that. It does not refute the theorem, because the theorem needs only rung-order independence and the duplicate check runs before the ladder; the seat also verified that the duplicate snapshot is built before the per-finding loop and never updated inside it, so duplicate handling is finding-order independent within a round as well. The conclusion is that invariance is more robust than was claimed and the refutation condition needs rewording, which is a seat improving its own falsifier rather than defending it.

WHAT WAS DONE WITH THE FINDINGS. Nothing was merged. Fixes are suggested to the human in the loop and never applied automatically. The quantified minimum-sample result bears directly on an outstanding decision, because the founder has ruled the rung cap removed, and this round's measurement says the value of a minimum sample is exactly the probability that a budget truncates the ladder multiplied by the resolution probability lost. That makes the 2 rulings one question rather than 2.

THE SECOND SEAT'S FIRST DISPATCH OF THIS ROUND FAILED AND IT WAS AN OPERATOR FAULT. It returned 0 characters after 435.9 seconds and 19 tool calls, with a broken pipe on its output stream and only 1 attempt recorded. The error is the bare exception rather than the dispatcher's retry wrapper, so it escaped outside the retry loop. The distinguishing circumstance is the launch: this round was started with its output connected to a pipe owned by the operator's tooling, where every round that succeeded on the same night was started detached with its output redirected to a file. The round was re-dispatched detached. This is recorded as a candidate cause rather than a proven one, and as an operator fault rather than a harness defect, because the dispatcher's own retry logic does cover a broken pipe and the panel's own launcher scripts redirect to a file.

THE RESULT OF THE ROUND: THE 2 SEATS CROSSED, AND THAT IS THE INFORMATION.

On the minimum-sample question the 2 seats exchanged positions, each persuaded by the other's argument, and neither was asked to.

The seat that had derived in its blind round that NO minimum sample is needed moved to HOLDING that one is justified, because both blind positions retain a token budget that can halt the climb and a ledger that halts part way IS a cap, which is where the symmetry argument dies. It priced the safeguard: at the current effective depth of 2 rungs, requiring 5 observations before ranking rather than 1 is worth 0.0506 expected resolution probability per truncated finding.

The seat that had PROPOSED the minimum sample of 5 moved to PERSUADED and WITHDREW it, in its own words: "A sample floor on a non-gating statistic is a cost. I withdraw it." Its reason is that its own floor fails its stated purpose anyway, since a Jeffreys posterior at 5 observations misorders nearly as freely as at 1.

BOTH SEATS INDEPENDENTLY NAMED THE SAME UNDERLYING MECHANISM, which is why the crossing is informative rather than merely contrary. Each identified the shared token ledger as what makes truncation possible, and therefore as what makes the estimate capable of excluding a rung. The second seat supplied a worked construction: a 2-model roster where the cheap model confirms at cost 10 and the expensive model is weak at cost 100, against a shared ledger of 115. The correct order leaves 105 and funds the next finding; the misordered ladder leaves 5 and every rung of the next finding is unfunded. So a bad estimate can exclude a rung, but on a DIFFERENT finding, through the budget rather than through the ladder.

So the round converged on the shared token ledger as the operative cause, and crossed on what to do about it. The shared remedy both positions already contain is the invariant that cost may reorder a rung and may never remove one, with budget exhaustion recorded as an unfunded-rung outcome rather than as a verdict. Neither seat was asked to converge and the disagreement that remains is preserved below rather than resolved by vote.

WHAT BOTH NOW AGREE ON, HAVING ARRIVED SEPARATELY. The order-invariance theorem holds: under exhaustion the ladder's order cannot change which findings resolve, only what they cost. The second seat re-verified it independently rather than accepting the figures, over all 120 orderings of 5 symbolic rungs with residual 0, confirmed the adjacent-interchange identity in both SymPy and Wolfram Language with residual 0, and reproduced the index rule against exhaustive permutation search over 1000 random rosters with a worst gap of 0. In the course of doing so it corrected the first seat's figure of 24 orderings, which should have been 120. It also accepted that its own design reduces to the same index-rule family at a dominated point, measuring its own proposed ordering as suboptimal in 90.93 percent of rosters, Wilson interval 89.99 to 91.78 percent.

THE DISAGREEMENT THAT SURVIVED, AND IT IS NOW BLOCKING RATHER THAN OPEN. Order-invariance assumes a rung's success probability is a fixed property of the model and the finding, independent of depth and history. The first seat's own proposed aid levels, which feed the previous rung's falsifier source and traceback forward, make that probability depend on position, so under aid the order CAN change which findings resolve and the structural guarantee holds only at aid level 0. The second seat made this blocking: no aid-laddered rung may enter the statistic's denominator as though it were a depth-0 attempt until a measurement shows the confirm rate at fixed model and finding is depth-stable. The first seat had flagged the cost half of that interaction in its blind round and not the probability half.

A FIELD DUPLICATION WAS FOUND IN THE 2 PROPOSALS. The 2 positions carry the same mechanism under different names, routing_deferred_reason in one and rung_unfunded in the other. Only one field should exist, and it should take whichever name is already written into the tree.

ONE SEAT COULD NOT DELIVER FILES, AND SAID SO PLAINLY RATHER THAN QUIETLY OMITTING THEM: "The write was not permitted, so no file is delivered; every figure below was computed in this dispatch's logged Bash calls and is reproducible from the quoted code." That is the kernel write confinement working as designed, and the seat adapted by inlining its computations where a reader can re-run them.

THE SECOND DISPATCH OF THE SECOND SEAT SUCCEEDED: 2220 words after 13 tool calls in 557.1 seconds, against the first attempt's 0 words after 19 tool calls and 435.9 seconds ended by a broken pipe. The only change was the launch method, detached with output written to a file rather than attached to a pipe owned by the operator's tooling.

THE SEATS WERE STAGGERED, AND IT WAS THE DISPATCHER THAT DID IT RATHER THAN THE OPERATOR. Measured on this round: the aliveness probes completed 4 seconds apart sequentially, and the first seat's brief ran from 07:08:11 to 07:22:57 with the second seat starting only after that window closed. The contrast is the round of 3 October, where both seats failed with nothing returned at 1956.0 and 1956.2 seconds, 2 tenths of a second apart, which is the concurrent-dispatch signature the serialisation of 5 October was built to remove.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# JOINT ROUND — the capability ladder as a measured statistic

This is the JOINT round of a star-topology panel. Both blind rounds are in. You are
reading the other seat's position for the first time. You wrote one of the 2 positions
below; the other you have not seen.

NO COMPELLED CONVERGENCE. Do not move toward the other seat to be agreeable. Where you
are now persuaded, say so and say by which specific argument or figure. Where you still
disagree, hold the position and name what would settle it. Disagreement that survives
this round is preserved as information, not smoothed away. Changing your mind for a
stated reason and refusing to change it for a stated reason are equally good outcomes;
changing it for no stated reason is the only bad one.

## What already agrees, blind, and therefore counts

Both seats independently rejected the original brief's use of the heterogeneity figure
(chi-square 280.0138, df 4, p = 2.213221e-59) as support for a fingerprint-driven
ladder, on the ground that it measures per-round FINDING RATE — productivity — and not
falsification capability. Both noted that ranking on it would put first the model that
Exp 55 showed confirming 2 of 2 with detached falsifiers. You reached this separately.
Treat it as established and do not re-argue it.

Both also retained `DEFAULT_FALSIFIER_STRENGTH` as a tie-break and cold-start ordering
rather than deleting it, and both said plainly that this is weaker than the founder's
ruling that the system should not care what a model is called.

## The 5 questions this round exists to settle

**J1 — MINIMUM SAMPLE. You disagree, and it is a derivation against a safeguard.**
One position sets a minimum sample of 5 before the statistic may rank, with a Jeffreys
posterior and a cold start at 0.500 placed between measured-strong and measured-weak.
The other derives that NO minimum sample is needed, because under exhaustion every rung
is tried regardless of its estimate, so a bad estimate can only misorder COST and can
never exclude a rung — and therefore the statistic gates nothing and needs no
`severity_is_proven` analogue. Is the derivation sound? If it is, the minimum sample is
not a safeguard but a cost; if it is not, say exactly which step fails.

**J2 — ORDER-INVARIANCE. One seat derives it; the other's design may depend on its
being false.** The claim: because `resolve_via_routing` stops at the first CONFIRMED,
P(resolve) = 1 - prod(1 - p_i) is symmetric in the rungs, so with the cap removed the
ladder's ORDER cannot change WHICH findings resolve, only what they cost. Verified by
SymPy over all 24 orderings of 5 rungs, by NumPy enumeration, and by Wolfram Language
with residual 0. If that holds, ranking on capability at all is a cost optimisation and
the cost-minimising order is p_i/c_i descending. Does the other position survive
order-invariance, or does it reduce to the same index rule?

**J3 — THE SELECTION EFFECT. Two different fixes, and they may not compose.** One
position conditions on the ITEM, using same-finding decisive pairs: rung k+1 attempts
exactly what rungs 1..k failed, so difficulty cancels because the item is identical. The
other conditions on LADDER DEPTH, arguing the selection is fully observed because
`routing_history.rungs_tried` records why a finding reached a model, and that selection
on observables means conditioning removes the bias so randomisation buys nothing. Are
these the same fix in different coordinates, complementary, or incompatible? Composability
means one mechanism whose parts cannot be separated without loss, not 2 fixes that can
coexist.

**J4 — THE GAMMA COUPLING, which only one seat raised and which is now BLOCKING.**
Measured over 14 archived runs: flipping every unresolved critical to CONFIRMED moves
`gamma_critical` DOWN in 9, up in 3, unchanged in 2, and 2 of 14 cross the
`gamma_critical >= 0.30` arm DOWNWARD — `exp40_gate` 0.3018 to 0.2328,
`commissioning_arm1_panel` 0.3236 to 0.1883. 14.29%, Wilson [4.0094%, 39.9414%];
statsmodels, a closed form and Wolfram Language agree to 7 significant figures. The
stated mechanism: unresolved criticals skew LATE (mean round 18.00 against a registry
mean of 13.31; 6.50 against 3.19), and late mass steepens a cumulative curve, raising
beta and lowering gamma = 1 - beta. This has been INDEPENDENTLY RE-RUN against the live
archive by the operator and reproduced exactly.

GAMMA IS LOAD-BEARING in this project and the founder has a standing directive against
demoting it. So: is the measurement right, is the mechanism the right explanation, and
is the recording-only remedy (log `gamma_critical` a second way while the gate keeps
reading what it reads today) the correct minimal step? If exhaustion makes convergence
harder, say what follows for the founder's ruling that the problem should run until
resolved or the ladder is exhausted.

**J5 — THE DENOMINATOR AND THE `-SIM` POOLING.** One seat reports that the 2026-10-06
provenance repair, which credits the falsifier's AUTHOR rather than the filer, is
correct but still omits the FILER'S FAILURE from the filer's denominator, inverting 5 of
11 ranks (45.45%, Wilson [21.27%, 71.99%]). It separately reports that
`rank_falsifier_writers._base` strips the `-SIM` suffix, which would pool a simulated
model's history into a live run's estimate — Codex-SIM 71.50% against Codex 27.94%,
non-overlapping intervals. Does the other seat accept both? The second is a provenance
hazard of the class this project treats as most serious.

## Conditions

Tools decide, not votes. Every figure you assert carries its producing script and a
confidence interval for any proportion. Where a claim can be checked in Wolfram, check
it there as the SECOND falsifier with the open-source tools primary, and state plainly
if Wolfram failed to evaluate rather than quoting an unevaluated result. Do not add an
unwired module: this project has 11 confirmed defects that were additions nothing
reached. One-shot dispatch; you will not be re-invoked.

## Output shape — return exactly these fields

- `## J1` through `## J5` — one section per question above, each answered explicitly and
  separately. Open each with a single word, PERSUADED or HOLDING, then the reason.
- `## What changed my mind` — every point where the other position moved you, naming the
  specific argument or figure that did it. "Nothing" is an acceptable answer if true.
- `## What I still hold, and why` — positions you keep, with what would settle each.
- `## Measurements` — every figure with its Wilson interval and the 2 tools that agree.
  State plainly if a Wolfram call failed to evaluate rather than quoting it.
- `## Delivered files` — paths written into the sandbox tree, or none.
- `## Residual disagreement` — what a reader should carry forward as unsettled. This is
  the most valuable field in the round; do not empty it to look agreeable.

---

## POSITION A (blind round, seat 1)

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

---

## POSITION B (blind round, seat 2)

All four scripts execute and answer `--help`. Written to the sandbox tree.

## Position

**1 — What the ladder should rank on.** The probability that a falsifier written by model *m* for a finding at ladder depth *d* is re-executed by `reverify_falsifier` with verdict `CONFIRMED`, counted **per attempt** (not per entry), restricted to falsifiers that actually read the target (`competence_provenance.falsifier_style == "reads"`), and **stratified on ladder depth**. It has no glossary name and I have not coined one — it is described in full, and it is neither `rho` (a round's novel/raw yield, not a writer's success) nor `S_k` (which classifies a fix that does not exist at routing time). Estimator, minimum sample, cold start and the 1-model case are in `## The quantity`. The prior question is settled first by derivation: `resolve_via_routing` stops at the first `CONFIRMED`, so with the cap removed `P(resolve) = 1 − ∏(1−p_i)` is **symmetric in the rungs** — order cannot change *which* findings resolve, only what they cost. The founder's two rulings are coupled: removing the cap is what makes an imperfect measurement safe.

**2 — The selection effect.** Condition on ladder depth; neither of the three earlier proposals. The selection is *fully observed* — a finding reaches a model at depth *d* because *d* rungs already failed, and `routing_history.rungs_tried` records it. Selection on observables means conditioning removes the bias, so randomisation buys nothing. The audit-fraction proposal also isn't deployable (routing fires on unresolved criticals only; single-digit *n* per model per run). Keeping the frozen order as decider is the status quo plus a dashboard, and keeps exactly what the founder ruled against. And the stated rejection of *first-attempts-only* **does not follow from its citation**: p = 2.213221e-59 comes from a chi-square on the 5 real models' per-round *finding counts*; it is not a comparison of first-attempt vs routed populations. I reproduced the figure — it is right, the inference drawn from it is not. The real reason to reject it is that it discards the routed trials, which are the population the decision concerns.

**3 — Removing the rung cap.** What bounds spend is not a cap but a **finite attempt lattice plus non-repetition**: a rung is a `(model, aid_level)` pair, each pair attempted at most once *per finding across the whole run*, so the remaining set strictly decreases and the process terminates. Stopping rule: **CONFIRMED, or the lattice is exhausted. No count.** Worst case `3 × |roster|` dispatches per finding *for the run* — against today's cap of 2 *per round, re-paid every round*, so the capped design is not obviously cheaper. Two guards, both loud: a global token ledger that **halts with a named reason** (as `HALTED_IRREDUCIBLE_QUEUE_ALARM` does) rather than silently capping, and `rung_unfunded` recorded as an outcome that leaves the finding unresolved and in the irreducible queue — never a skip that looks like a failure.

**4 — Resource-aware routing.** Yes, and as the *denominator of one objective*, not a second competing input. I derive that the expected-cost-minimising order for stop-at-first-success is `p_i/c_i` descending — so capability and budget are already one ratio and it is an optimum, not a compromise. A cheap model does not become the default **because the ladder exhausts**: first means *cheapest place to look first*, and the strong rung still runs when the probe fails. That guarantee is structural (order-invariance), not a tuning choice, so it cannot be tuned away. Load balancing falls out free: a model near its ceiling has its effective `c_m` raised and drifts down the order, degrading smoothly.

**5 — Reproducibility.** A separate step, performed by the harness. Not the models — a model attesting its own falsifier reproduces is a vote, and is the shape of the Exp 48 failure. Not primarily the human — 6194 archived entries across 131 artefacts; a control that doesn't run isn't a control. `reverify_falsifier` already gives one independent execution; what is missing is small: **execute twice in two fresh processes, record `sha256` of target and falsifier bytes with both verdicts, and treat disagreement as `NONDETERMINISTIC` — an instrument fault, not a finding verdict — routed to HIL.** The human's role is that residue plus `rung_unfunded`. That is the "both", correctly apportioned.

**6 — What we missed.** Nine items in the document; the four that matter most: the empty ladder is wider than the 1-seat case (executed: a roster of two identical labels also yields `[]`, which is the founder's *"all the models are the same"* case); **`gamma_critical` is not invariant to routing depth**, so `routing_max_rungs` is an undeclared input to the convergence gate; the 2026-10-06 provenance repair is correct but still loses the filer's **failure** from the denominator, inverting 5 of 11 ranks; and `rank_falsifier_writers._base` strips `-SIM`, which would pool a simulated model's history into a live run's estimate.

## The quantity

**Formula.** `p̂(m,d) = (k(m,d) + ½) / (n(m,d) + 1)` — Jeffreys (Beta(½,½)) posterior mean. `k` = CONFIRMED re-executions, `n` = provenance-clean attempts at depth `d`. Jeffreys, not Laplace: it is the binomial reference prior, its interval behaviour matches the Wilson interval this project mandates, and it returns ½ at `n=0` without asserting anything.

**Inputs.** `routing_history` (`model_used`, `verdict`, `rungs_tried` — present since 2026-10-03, 294 rung records today, which is thin and I say so), `falsifier_code` / `last_falsifier_code_full` for the provenance filter, and `resolved_by_routing` for authorship. Cost `c_m` = mean tokens per routing dispatch; roster median at `n=0`.

**Ranking.** `p̂(m,d)/c_m` descending; ties and all-cold-start break on position in `DEFAULT_FALSIFIER_STRENGTH`.

**Minimum sample: none — derived, not conceded.** A minimum sample is required of a statistic that *gates*. This one does not: under exhaustion every rung is tried regardless of its estimate, so a bad estimate can only misorder cost. That dissolves the blocker `RunnerConfig.routing_max_rungs` names for itself ("0 of 10 model pairs separate, all Fisher p ≥ 0.306"). **It also answers the A4 question directly: `p̂` opens no gate, so it needs no `severity_is_proven` analogue — it is not a number that admits or exempts anything.** The one place a number here *could* gate is cost, so: **cost may reorder a rung and may never remove one.**

**Cold start.** `n=0` → `p̂=½`, `c_m` = roster median → an unknown model enters at median `p/c` and is ordered among equals by cost, i.e. tried as a cheap probe, never excluded. This replaces today's behaviour, which appends unknown models in *roster order*.

**1-model panel.** A rung is `(model, aid_level)`, and `exclude` drops *pairs already attempted on this finding*, not models. Three levels: 0 = as today; 1 = plus the previous rung's falsifier source and traceback (`last_falsifier_code_full` already records exactly this, 221 records); 2 = plus worked examples (`routing.py`'s own docstring: 0/5 → 1/3, so not a no-op). A 1-seat roster gets a 3-rung ladder that exhausts, which is what the founder's ruling asks for and what the code currently refuses.

## What it does to gamma

**I predicted the wrong sign and my own measurement refuted me. The true direction is the dangerous one.** `_settled_novelty_series` skips `UNCONFIRMED` (it is in `_NON_NOVEL_TERMINAL_STATUSES`) and does not skip `CONFIRMED`, so a critical the ladder resolves *enters* the critical novelty series at its `open_since_round`. I expected back-fill at early rounds to raise `gamma_critical`. Over 14 archived runs with ≥3 rounds, flipping every unresolved critical to CONFIRMED moves it **down in 9, up in 3, unchanged in 2**, and **2 of 14 cross the `gamma_critical ≥ 0.30` arm downward** — `exp40_gate` 0.3018 → 0.2328, `commissioning_arm1_panel` 0.3236 → 0.1883. The mechanism is in the data: unresolved criticals skew **late** (9 of 14 runs), because an unresolved critical is one the ladder has not reached yet, and adding mass to the late end of a cumulative curve steepens it, raising β and lowering γ = 1 − β.

So: **removing the cap is not a pure spend question**, which is how both the founder's ruling and `routing.py`'s own comment frame it. It moves one arm of the two-sided gate in the direction that makes convergence *harder* — a run that passes today can stop passing — while the count arm does not move, because the resolution lands in an earlier bucket. I am **not** proposing to change `_NON_NOVEL_TERMINAL_STATUSES`: that would alter gamma for every archived run on my judgement, and the additive standard wants a committed measurement first. The simplest sufficient step is **recording-only** — log `gamma_critical` a second way with `UNCONFIRMED` treated as novel, so the coupling is visible per round while the gate keeps reading exactly what it reads today.

## Measurements

Every proportion with its Wilson 95% interval; every computed claim with ≥2 agreeing tools.

| figure | value | Wilson 95% | tools |
|---|---|---|---|
| P(resolve) distinct values over 5! ladder orders, exhausted | 1 (0.998812000000 = closed form) | — | SymPy (24/24 orders), NumPy enumeration, **Wolfram Language** (residual 0) |
| …under cap = 2 | 10 distinct, [0.7624, 0.9800] | — | SymPy (20/24 change), NumPy |
| `E[cost](a,b)−E[cost](b,a)` | `Q(c_a p_b − c_b p_a)`, residual 0 | — | SymPy, **Wolfram Language** |
| `p/c` order vs true optimum, 4000 random 5-rung rosters | worst gap 0.000e+00 | — | NumPy exhaustive permutation search |
| strongest-first suboptimal | 3637/4000 = 90.93% | [89.99%, 91.78%] | NumPy; closed form + statsmodels |
| cheapest-first suboptimal | 3525/4000 = 88.13% | [87.08%, 89.09%] | NumPy; closed form + statsmodels |
| index rule under position-dependent cost | loses 1.6393% (probe fires) | — | NumPy |
| runs crossing the 0.30 gamma arm downward | 2/14 = 14.29% | [4.01%, 39.94%] | repo's own `_estimate_gamma`; closed form + statsmodels |
| unresolved criticals skew later than registry mean | 9/14 = 64.29% | [38.76%, 83.66%] | same |
| rank inversions, entry-level vs attempt-level | 5/11 = 45.45% | [21.27%, 71.99%] | closed form + statsmodels |
| `resolved_by_routing` entries naming a different model | 458/458 = 100% of 6194 entries | [99.17%, 100%] | archive scan, two globs |
| model pairs separating, pooled clean cell | 43/55 = 78.18% | [65.63%, 87.05%] | Wilson non-overlap; closed form + statsmodels |
| DeepSeek 12/16 vs Gemini 1/8 (clean critical cell) | Fisher p = 0.00780724, OR 21.0 | DS [50.50%, 89.82%]; Gem [2.24%, 47.09%] | scipy, independent hypergeometric enumeration, **Wolfram Language** (9 s.f.) |
| CC2 39/41 vs Codex 42/46 | Fisher p = 0.679555 — **no separation** | CC2 [83.86%, 98.65%]; Cx [79.68%, 96.57%] | same three |
| Codex-SIM vs Codex, attempt level | 71.50% vs 27.94%, non-overlapping | [67.04%,75.57%] / [24.97%,31.12%] | closed form + statsmodels |
| SIM/LIVE separating in the *clean* cell | 2 of 5 vendors (3 overlap) | per-vendor in script output | same |

Wolfram ran locally and computed (attribution: Wolfram Language, local Wolfram Engine via `wolframscript`). One Wolfram call **failed to verify** and I am not quoting it: `FisherExactTest` returned unevaluated, so I re-expressed the test as an explicit hypergeometric sum, which did compute and agreed to 9 significant figures.

Executed, not read: `rank_falsifier_writers(['CC2'], exclude=('CC2',)) → []`; `(['CC2','CC2'], exclude=('CC2',)) → []`; `(['Codex','ChatGPT'], exclude=('Codex',)) → ['ChatGPT']`; `resolve_via_routing(..., max_rungs=0)` dispatches all 4 rungs, `max_rungs=2` dispatches 2. 15 fingerprint fields confirmed field-by-field: 9 from the initialiser + 6 from `_compute_attention_metrics`; `D_decay` supplies glossary `D`, `total_findings` plausibly `A`, and **`v̄` (verification) and `C` (coverage) are absent**. The brief's claim that `competence_provenance.py` credits the filer is **stale in this tree** — `falsifier_author` was repaired on 2026-10-06 and now prefers `resolved_by_routing`; the residual defect is the denominator, not the credit.

## Delivered files

- `docs/CAPABILITY_LADDER_MEASURED_2026-10-06.md` — the design, with derivations, the nine missed items, and a per-position refutation table.
- `scripts/ladder_order_is_cost_only_2026-10-06.py` — order-invariance and the `p/c` index rule; SymPy + NumPy brute force + live assumption probes. Exit 0.
- `scripts/the_ladder_statistic_loses_the_filers_failure_2026-10-06.py` — entry-level vs attempt-level accounting, Wilson + statsmodels. Exit 1 (inversions found).
- `scripts/routing_exhaustion_raises_gamma_critical_2026-10-06.py` — gamma_critical vs routing depth over 14 archived runs, using the runner's own `_settled_novelty_series` and `_estimate_gamma`. Exit 1 (gate arm crossed). **Its docstring retains my refuted hypothesis rather than editing it out.**
- `scripts/provenance_clean_cell_contradicts_frozen_ladder_2026-10-06.py` — the cell a re-derived ladder must come from; Fisher two ways, SIM vs LIVE. Exit 1.

All four answer `--help` without measuring. **No `bench/` module is added**: an unwired estimator would be the 12th of this project's 11 confirmed additions-that-nothing-reached. The design lands at `routing.py`'s one call site with tests that exercise it, or not at all.

## What would refute me

Per-position table in the document; the load-bearing ones: **order-invariance** falls if `scripts/ladder_order_is_cost_only_2026-10-06.py` exits non-zero, or if any path sets `resolved=True` without a `CONFIRMED` from `reverify_fn`. **The `p/c` rule** falls if the brute force shows a non-zero gap, or if rung cost grows with ladder position — already demonstrated to break it by 1.6393%, so my own aid levels 1–2 must be measured *against* R2, not assumed under it. **The single most falsifiable claim in the design:** a measured run where cheapest-first ordering resolves *fewer* criticals than strongest-first under exhaustion. By order-invariance that is impossible, so such a run refutes the whole design. **The gamma coupling** falls if that script reports 0 crossings in either direction. **The denominator claim** falls at 0 rank inversions. **The 1-model fix** falls if aid levels 1–2 confirm at `p̂` indistinguishable from level 0 — which would make the self-ladder an addition nothing reaches, the failure mode I am warning about. **Keeping the frozen tuple** falls to any committed measurement showing a `p̂`-derived order dominating it on resolutions-per-token in a live run.

## Disagreement

**With the founder, partially, on vendor names.** The ruling is *"the system shouldn't care at all what a model is called."* I am not deleting `DEFAULT_FALSIFIER_STRENGTH` and I think deleting it now would be wrong. At `n = 0` every model has `p̂ = ½` and the ratio ranks purely on cost; something has to break that tie, and the frozen tuple is the only ladder in this project with a validated end-to-end result (Exp 42's hardest residuals, 7/7 across two rungs). The additive standard permits removal only on a committed measurement showing the replacement dominates, and that measurement does not exist: my own contradiction of the tuple (Fisher p = 0.0078) comes from a cell that pools runs, targets and difficulties and is confounded by the very selection effect question 2 is about. So the tuple is demoted to tie-break and cold start, and the system stops caring about names the moment it has data — which is a weaker claim than the ruling, and I'd rather say so than pretend otherwise.

**With the brief, on one cited figure.** The rejection of first-attempts-only is supported by p = 2.213221e-59, which measures something else entirely. The proposal should still be rejected, for a different reason.

**With myself, recorded because the check is the point.** I predicted exhaustion would *raise* `gamma_critical`; the archive says it falls. I also expected the word-overlap duplicate path (`confirmed_duplicate` → `escalated = False` on bare Jaccard ≥ 0.85) to deadlock a finding permanently out of the ladder. It does not — `escalated` is re-set to `True` at several sites including the falsifier-gate path, so a later round can re-escalate. Both were claims that sounded right and one tool call each dissolved.

**Early stop, with reason.** I stopped here rather than extending to the depth-stratified estimate on live data: `routing_history` carries 294 rung records in total, so per-`(model, depth)` cells are single-digit and the estimate would be prior-dominated. That is a measurement to make after a routing-enabled run with the cap removed, not a number to manufacture now.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 32 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel capability_ladder_joint_2026-10-06) -->

## J1

**HOLDING** — the derivation is sound only for an unbounded ladder, and the step that fails is its premise: *"under exhaustion every rung is tried regardless of its estimate."* Both positions retain a budget guard that can stop the climb — A's "per-finding routing token budget", B's "global token ledger that **halts** with a named reason" plus `rung_unfunded` "recorded as an outcome that leaves the finding unresolved". A ledger that halts mid-ladder **is** a cap; it differs from `routing_max_rungs` only in that its threshold is data-dependent rather than configured. And truncation is exactly where symmetry dies:

SymPy, cap = 2 on 3 rungs: `P(resolve|1,2,3) − P(resolve|3,2,1) = (p₁−p₃)(1−p₂)`, not identically zero. Wolfram Language (local Wolfram Engine) returns the same factorisation, `-((-1 + q2)*(q1 - q3))`, and `Simplify[d]===0 → False`. Witness p = (0.9, 0.1, 0.01): 0.910000 vs 0.109000, a loss of 0.801000 in P(resolve) from order alone.

So the estimate *can* exclude a rung whenever the budget bites, and then a bad estimate costs resolutions, not cost. Measured magnitude (NumPy, 20 000 trials, 5 rungs, expected P(resolve) lost per finding against the true order):

| obs/rung behind the estimate | d=1 | d=2 | d=3 | d=4 | d=5 |
|---|---|---|---|---|---|
| 0 (cold start, ties broken arbitrarily) | 0.297854 | 0.165226 | 0.074684 | 0.025744 | −0.000000 |
| 1 | 0.173456 | 0.074341 | 0.032762 | 0.013046 | −0.000000 |
| 2 | 0.119142 | 0.049508 | 0.020860 | 0.008365 | 0.000000 |
| 5 | 0.062751 | 0.023675 | 0.010055 | 0.004007 | 0.000000 |
| 10 | 0.035876 | 0.013043 | 0.005712 | 0.002237 | −0.000000 |
| 30 | 0.013460 | 0.004494 | 0.001952 | 0.000867 | 0.000000 |

At d = 5 the loss is 1.166e-19 for every row — B's derivation reproduced on the estimator itself. At today's effective depth d = 2, requiring n ≥ 5 before ranking rather than ranking at n = 1 is worth **0.0506** expected resolution-probability per truncated finding. That is the minimum sample's value: `Pr(truncation) × loss`, zero if and only if truncation is impossible, which no one has proposed.

Two things in B's derivation I accept outright. First, `p̂` opens no gate, so it needs **no `severity_is_proven` analogue** — that part is correct and is not what the minimum sample is for. Second, "cost may reorder a rung and may never remove one" is the right rule; it is just not what `rung_unfunded` implements.

What would settle the remaining gap: whether A's fallback (the frozen tuple at n < 5) actually beats an n = 1 posterior is **unmeasured**. My own attempt-level LIVE ordering (ChatGPT > Gemini > Codex > CC2 > DeepSeek) agrees with `DEFAULT_FALSIFIER_STRENGTH` on DeepSeek-last only, but that cell pools runs, targets and difficulties and uses a status proxy, so it cannot decide it.

## J2

**PERSUADED**, and the theorem is stronger than B stated — it needs no independence at all.

`P(resolve) = 1 − P(every rung fails)`, and under exhaustion "every rung fails" is an event on a **set** of rungs. So invariance holds for an *arbitrary joint failure law*, correlated or not. Verified by exhaustive enumeration over all 2⁵ joint outcomes under 200 random Dirichlet joint laws × all 120 orders: max spread **0.000e+00**. The product form `1 − ∏(1−pᵢ)` is the factorising special case: SymPy residual 0 over 24 orders of 4; Wolfram Language residual **0** over all 120 orders of 5. (B's text says "24 orderings of 5 rungs"; 5! = 120. The conclusion is unaffected, but the count is 4!.)

Two refinements:

- **B's own stated refutation condition is over-broad and already met.** It says order-invariance "falls if any path sets `resolved=True` without a `CONFIRMED` from `reverify_fn`". `route()`'s DUPLICATE early return does exactly that (`RoutingResult(fid, "DUPLICATE", True, ...)`, `rungs_tried=0`). It does not refute the theorem, because the theorem needs only *rung-order* independence and the dedup check runs before the ladder. I also checked the cross-finding path: `confirmed` is a snapshot built at `reference_runner_v3.py:6871` *before* the per-finding loop at 6936 and is never updated inside it, so dedup is finding-order-independent within a round too. Invariance is therefore more robust than claimed; the criterion needs rewording.
- **Order-invariance fails for B's own aid-level lattice.** Aid level 1 is defined as "plus the previous rung's falsifier source and traceback". That makes a rung's success probability a function of *which rung preceded it*, so the failure events stop being an order-free set and P1 no longer applies. B flagged the cost half of this (the 1.6393% position-dependent-cost result) and not the probability half. A 3-rung self-ladder's P(resolve) is order-dependent by construction.

**Does A survive order-invariance?** As a policy, yes; as a *justification*, no. Under exhaustion, ranking on capability cannot change which criticals resolve, so A's "stage 1 ranks purely on v-bar; cost can veto but never score" is a pure spend policy. And it is not the cost optimum: the exchange identity `E[cost](a,b) − E[cost](b,a) = Q(c_a p_b − c_b p_a)` (SymPy residual 0; **Wolfram Language residual 0**) makes `p/c` descending optimal — brute-forced against exhaustive permutation search over 4000 random 5-rung rosters, worst gap **0.000e+00**. Ordering on p alone coincides with it only when costs are equal, and `routing.py`'s own docstring says they are not ("Codex … and fast — OpenRouter", "CC2 … claude_cli-slow"). So A reduces to the same index rule in the equal-cost case and is strictly dominated on expected cost otherwise — while resolving the identical set of findings. The disagreement is real but it is entirely about spend.

## J3

**HOLDING** — they are complementary, they control *different* confounders, neither is the other in different coordinates, and the composition the founder's rule would require has **zero data support today**, so the composition cannot be justified.

- A conditions on the **item** and leaves **position and treatment** uncontrolled. In the only pairs the archive can supply — source model failed, `model_used` confirmed — the two attempts were made under *different dispatch conditions*: routing dispatches "WITH the execute_python tool loop", the original round's gate attempt did not. The item is identical; the treatment is not. A's pair therefore estimates model × treatment, not model. "Difficulty cancels because the item is identical" is true and insufficient.
- B conditions on **depth** and leaves the **item** uncontrolled. Depth is a coarsening of difficulty, not a sufficient statistic for it: within depth d the residual difficulty depends on *which* models failed earlier — a strong rung failing at depth 1 leaves a harder item than a weak one failing. "Selection on observables" is true of `rungs_tried`; it is not true of the identity-of-prior-failures that `rungs_tried` summarises away.
- The composed estimator — same finding, same depth, same dispatch condition — has **n = 0 by construction**: `resolve_via_routing` dispatches exactly one model per depth. Executed: `max_rungs=0` on `['A','B','C','D']` dispatches `['A','B','C','D']`, one per depth.

And the archive cannot back either fix. Measured over `bench/logs/**/*.json`: **616** `routing_history` records across 47 files, `rungs_tried` distribution {0: 118, 1: 214, 2: 284}; **284/616 = 46.1039%, Wilson95 [42.2037%, 50.0524%]** are multi-rung climbs that record only `model_used` — the last rung — so non-final rungs are unattributable. `RoutingResult` in this tree carries `['finding_id','verdict','resolved','model_used','falsifier_code','duplicate_of','rungs_tried']`: no per-rung attempts field. This confirms A's point (c) on a larger denominator than A's 87/87 or 12/12.

So the founder's composability test — compose only on a *demonstrated* advantage — cannot be run, because the measurement that would demonstrate it does not exist. The single prerequisite **both** fixes share is per-rung attribution: A's `RoutingResult.attempts`. It is the simplest sufficient step, it is wired (`routing_history` is written at the one call site, line 7023), and it must record the **dispatch condition** alongside the model, or A's pairs stay confounded and B's depth strata stay unattributable below the final rung.

## J4

**PERSUADED**, and I upgrade the mechanism from an observation to a closed form. The measurement reproduces exactly; the direction is **forced by the estimator**, not by the panel.

Derivation. `_estimate_gamma` returns `γ = 1 − β` with β the OLS slope of `log(cum)` on `log(i+1)`. Adding one unit at round r gives `cum_i → cum_i + 1` for all i ≥ r, hence `Δy_i = log(1 + 1/cum_i)` for i ≥ r and

  `Δβ = Σ_{i≥r} (x_i − x̄)·log(1 + 1/cum_i) / S_xx`,  `Δγ = −Δβ`.

`Δy_i` is decreasing in i (cum is non-decreasing) while `(x_i − x̄)` is increasing, so the sum is negative at r = 0 and positive for late r: there is a crossover index **r\***, below which added mass *raises* γ and at or above which it *lowers* γ.

Checked against the repo's own `_estimate_gamma` by finite difference: 127 (series, bucket) pairs, worst |error| **5.366e-15**. Checked for multi-unit flips by summing the closed form sequentially: exact to ~1e-15 on all 9 runs where γ is interior, and disagreeing on exactly the 3 runs where `max(0.0, min(1.0, 1−β))` clamps (exp41_convergence, both exp53_control_zero). That also explains the one run B's mean-round story gets wrong: exp38_ouroboros has mean flip round 9.33 ≥ r\* = 2 yet moves **up** (+0.0316) — because 4 of its 9 flipped criticals sit at round 0. The sign condition is per-unit and sequential; a mean round is not a sufficient summary of it.

Reproduction of the two named crossings, using the repo's own `_estimate_gamma` and `_NON_NOVEL_TERMINAL_STATUSES`:

- `exp40_gate_20260514T020550Z`: 0.3018 → **0.2328**, mean flip round 18.00 vs registry mean 13.31, r\* = 4.
- `commissioning_arm1_panel_20260929T214647Z`: 0.3236 → **0.1883**, 6.50 vs 3.19, r\* = 1.

Both to 4 decimal places, independently. My denominator is 12, not 14, because I required the flip to actually change the series: **2/12 = 16.6667%, Wilson95 [4.6965%, 44.8031%]** against B's 2/14 = 14.29% [4.0094%, 39.9414%] (Wolfram confirms B's interval to 9 s.f.: [4.009392, 39.941379]). Same two runs; different inclusion rule; overlapping intervals. Direction: down 7, up 3, unchanged 2.

**Is recording-only correct?** Yes, and for a stronger reason than B gives. γ is keyed on `open_since_round` (discovery time) but its *input set* is keyed on terminal status, so routing depth changes which discoveries γ can see at all. Changing `_NON_NOVEL_TERMINAL_STATUSES` would re-value every archived run on a judgement; recording a second series does not. One condition: the second series must be **read** by something — logged beside `gamma_history` and consumed by the analysis path — or it is the 12th addition nothing reaches. I would log `routing_max_rungs` in the same record, because without it a later reader cannot tell whether two runs' γ values are comparable at all.

**What follows for the founder's ruling.** Adding a rung can only raise `1 − P(all fail)`, so exhaustion strictly increases resolutions; resolution moves criticals out of `UNCONFIRMED` and into the critical novelty series **at their discovery round**, which is late, which lowers γ_critical. The two arms of the gate therefore move in opposite directions under the ruling: the unverified-critical arm opens, the γ arm closes. That is not an argument against the ruling and not a reason to demote γ. It is evidence that the **0.30 band was calibrated on a censored series** — one from which unresolved criticals had been silently removed. The ruling stands; the 0.30 threshold must be re-derived on the uncensored series *before* exhaustion is enabled in a gated run, or exhaustion will be read as non-convergence. Re-calibrate γ's threshold; do not weaken γ.

## J5

**PERSUADED** on both, with one correction to a figure and one strengthening.

**The denominator.** Accepted, and the sign is derivable without data. `analyse` iterates registry *entries* and attributes each entry whole to `falsifier_author(e)`. For an entry filed by F and resolved by R: R gains +1 attempt and +1 confirmation; F gains **nothing** — yet F attempted and failed, which is why routing fired. Since `k/n > k/(n+f)` for all k ≥ 0, n ≥ 1, f ≥ 1, and every omitted attempt is a failure by construction, the estimator is **strictly upward-biased for exactly the filers the ladder is meant to demote** — the same direction as the defect the 2026-10-06 repair fixed. The repair removed the false *credit* and left the missing *failure*. Checked numerically: 0 sign violations across all 11 models.

**Correction:** I do not reproduce 5 of 11. With `status == "CONFIRMED" or falsifier_verdict == "CONFIRMED"` as numerator and n ≥ 5, I get **3/11 = 27.2727%, Wilson95 [9.7461%, 56.5645%]** (Fable-SIM #3→#4, DeepSeek-SIM #4→#5, ChatGPT-SIM #5→#3). B's [21.27%, 71.99%] and mine overlap heavily, so the defect stands and the magnitude is estimator-dependent. Wolfram confirms B's interval arithmetic for 5/11: [21.271272, 71.990846].

**The `-SIM` pooling.** Accepted as a **forward** hazard, with a precision B's wording blurs: `rank_falsifier_writers._base` computes no estimate, so nothing is pooled *today*; the hazard is that the ladder ranks by base name, so a statistic keyed the same way inherits it. Measured consequence, which is larger than B reported: pooling **swaps the #2 and #3 rungs** (Codex ↔ CC2), and SIM/LIVE separate at 95% for **4 of 5** vendors with a live counterpart (**80.00%, Wilson95 [37.5535%, 96.3776%]**) — CC2-SIM 89.73% [84.52, 93.33] vs CC2 38.72% [34.19, 43.45]; Codex-SIM 75.51% [67.97, 81.75] vs Codex 46.65% [41.92, 51.44]; DeepSeek-SIM 68.06% [56.61, 77.67] vs DeepSeek 30.81% [27.15, 34.73]; ChatGPT-SIM 66.92% [58.54, 74.34] vs ChatGPT 48.33% [43.40, 53.29]; only Gemini overlaps (59.09% [47.05, 70.13] vs 47.38% [43.76, 51.02]). B reported 2 of 5; I get 4 of 5. Different numerators, same conclusion, mine stronger.

**The fix must not touch `_base`.** The `-SIM` normalisation is a documented feature with a stated purpose — ladder *order* rehearsal in simulation (`routing.py`, Fable, 2026-08-30) — and removing it would be a removal without a committed measurement. Key the statistic on the **full label**; leave the ordering normalisation alone.

**New, raised by neither seat.** The normalisation is applied **asymmetrically**: `by_base` normalises the ranking, but `excl = set(exclude)` matches raw labels. Executed: `rank_falsifier_writers(['Codex-SIM'], exclude=('Codex',)) → ['Codex-SIM']`. If a finding's `source_model` were recorded bare while the roster carried `-SIM`, the ladder would route the finding **back to the model that already failed** — the one behaviour the module docstring forbids — and feed that model's second attempt into its own statistic. Reachability measured: **0 of 20** archived runs with any `-SIM` source model mix bare and suffixed labels, Wilson95 [0.0000%, 16.1125%]. So this is a latent hazard, not a present defect, and I hold it at that status.

**Also stale, and a collision between the two positions.** A's claim that `int(getattr(cfg, "routing_max_rungs", 2) or 2)` makes exhaustion inexpressible is **stale in this tree**: the `or 2` was removed 2026-10-06, and executed, `cfg.routing_max_rungs = 0` now reaches `route` and dispatches all 4 rungs. Meanwhile `resolve_via_routing(..., max_rungs=None)` *also* exhausts (`if not max_rungs`), while the runner maps `None → 2`. So `None` means "exhaust" at the module and "default" at the runner. A's delivered `None` sentinel would silently flip any config carrying `routing_max_rungs: null` from 2 rungs to exhaustion. Keep **0** as the sole sentinel; it already works.

## What changed my mind

- **Order-invariance (J2).** B's `P(resolve) = 1 − ∏(1−pᵢ)` symmetry argument moved me from treating capability ranking as a correctness question to treating it as a cost question. The figure that did it was my own replication at d = 5: loss **1.166e-19** across every sample size. Having accepted it, I also found it is stronger than stated — the set-event form needs no independence (max spread 0.000e+00 over 120 orders × 200 correlated joint laws).
- **The `p/c` index rule (J2/J4 of A's design).** The exchange identity with residual 0 in both SymPy and Wolfram, plus a 0.000e+00 worst gap against exhaustive search, persuaded me that "cost can veto but never score" is not the optimum unless rung costs are equal, and `routing.py` says they are not.
- **The γ coupling (J4).** B's two named crossings reproduced to 4 d.p. on my own re-run with the repo's own estimator. That moved me from "plausible artefact of one archive" to "structural property of a log-log slope estimator", which I then derived in closed form and checked to 5.37e-15.
- **The denominator (J5).** The derivation `k/n > k/(n+f)` with every omitted attempt a failure by construction is decisive on its own; 0 sign violations across 11 models closed it.
- **The `-SIM` pooling (J5).** Measuring it rather than reasoning about it changed my estimate of its size *upward* — 4 of 5 vendors separating, and the #2/#3 rungs swapping.
- **B's A4 point.** `p̂` admits and exempts nothing, so no `severity_is_proven` analogue is needed. I had expected to argue the opposite.

## What I still hold, and why

1. **A minimum sample is a safeguard, not a cost, for as long as any budget guard exists.** Settled by: a run with the ledger wired, counting findings whose climb stopped at `rung_unfunded`. If that count is 0 over a representative run, B is right and n_min is pure cost. If it is nonzero, the P4 table prices the exposure.
2. **The two selection fixes are complementary and cannot be composed on current data.** Settled by: `RoutingResult.attempts` recording model, verdict and dispatch condition per rung, then checking whether same-item/same-depth/same-treatment cells have nonzero support. Until then the composition fails the founder's test for lack of a measurement, not for lack of merit.
3. **A's same-finding pairs are confounded by treatment, not just difficulty.** Settled by: one paired dispatch of the source model *with* the tool loop on a finding its gate attempt failed. If its confirm rate is unchanged, the confound is immaterial and A's pairs are clean.
4. **γ's 0.30 band needs re-calibration, not protection.** Settled by: re-deriving the band on the uncensored critical series across the archive and checking whether the historical gate decisions it was fitted to are preserved.
5. **Retaining `DEFAULT_FALSIFIER_STRENGTH` is right, and both seats' reason for it is right.** Deleting it would be a removal without a committed measurement showing the replacement dominates; my own attempt-level cell is confounded and cannot supply one. Settled by a paired-arm run.
6. **`_base` must not change.** Settled by: any measurement showing the `-SIM` ordering rehearsal is dead — then it is redundant and removable.

## Measurements

Every proportion carries a closed-form Wilson 95% interval and `statsmodels.proportion_confint(method="wilson")`; `agree=True` means they matched to 1e-12.

| figure | value | Wilson95 | tools |
|---|---|---|---|
| set-event order-invariance, correlated joint laws, 120 orders × 200 laws | max spread 0.000e+00 | — | NumPy exhaustive enumeration; SymPy (product form, 24 orders of 4, residual 0); **Wolfram Language** (120 orders of 5, residual **0**) |
| cap = 2 on 3 rungs, order difference | `(p₁−p₃)(1−p₂)`, not ≡ 0; witness loss 0.801000 | — | SymPy; **Wolfram Language** (`-((-1+q2)(q1-q3))`, `Simplify===0 → False`) |
| expected P(resolve) lost by small-sample ordering, d = 2 | 0.165226 (n=0) → 0.023675 (n=5); gain 0.141551 | — | NumPy, 20 000 trials × 6 sample sizes |
| …at d = 5 (true exhaustion) | max abs 1.166e-19 | — | same |
| exchange identity `E[cost](a,b)−E[cost](b,a)` | `Q(c_a p_b − c_b p_a)`, residual 0 | — | SymPy; **Wolfram Language** (residual 0) |
| `p/c` descending vs exhaustive optimum, 4000 rosters | worst gap 0.000e+00 | — | NumPy exhaustive permutation search |
| closed-form Δβ vs repo `_estimate_gamma`, finite difference | 127 pairs, worst err 5.366e-15 | — | repo's own `_estimate_gamma`; closed form in NumPy |
| sequential multi-unit Δβ, 9 interior runs | err ≤ 3.03e-15; 3 clamped runs excluded and named | — | same |
| runs crossing γ_critical ≥ 0.30 downward | 2/12 = 16.6667% | [4.6965%, 44.8031%] | closed form + statsmodels (agree); **Wolfram** reproduces both 2/12 and B's 2/14 to 9 s.f. |
| γ moves down on flip | 7/12 = 58.3333% | [31.9511%, 80.6740%] | closed form + statsmodels (agree) |
| exp40_gate γ_critical | 0.3018 → 0.2328; μ_flip 18.00 vs μ_reg 13.31 | — | repo's `_estimate_gamma` + `_NON_NOVEL_TERMINAL_STATUSES` |
| commissioning_arm1_panel γ_critical | 0.3236 → 0.1883; μ_flip 6.50 vs μ_reg 3.19 | — | same |
| multi-rung `routing_history` records with unattributable non-final rungs | 284/616 = 46.1039% | [42.2037%, 50.0524%] | archive scan (47 files); closed form + statsmodels (agree) |
| rank positions moving, entry-level → attempt-level | 3/11 = 27.2727% | [9.7461%, 56.5645%] | closed form + statsmodels (agree); derived sign, 0 violations |
| SIM/LIVE Wilson separation, vendors with a live counterpart | 4/5 = 80.0000% | [37.5535%, 96.3776%] | closed form + statsmodels (agree) |
| CC2-SIM vs CC2 | 89.73% vs 38.72%, non-overlapping | [84.52,93.33] / [34.19,43.45] | same |
| Codex-SIM vs Codex | 75.51% vs 46.65%, non-overlapping | [67.97,81.75] / [41.92,51.44] | same |
| pooled `-SIM` ladder top | Codex ↔ CC2 swap at #2/#3 | [47.09,55.07] / [46.48,54.12] | same |
| archived runs mixing bare and `-SIM` `source_model` | 0/20 = 0.0000% | [0.0000%, 16.1125%] | archive scan; closed form + statsmodels (agree) |

Executed, not read: `rank_falsifier_writers(['CC2'], exclude=('CC2',)) → []`; `(['CC2','CC2'], exclude=('CC2',)) → []`; `(['Codex','ChatGPT'], exclude=('Codex',)) → ['ChatGPT']`; **`(['Codex-SIM'], exclude=('Codex',)) → ['Codex-SIM']`**; `resolve_via_routing` dispatches 4/4 at `max_rungs=0`, 4/4 at `max_rungs=None`, 1/2/3 at 1/2/3; runner coercion `None → 2`, `0 → exhaust`. `RoutingResult` field list printed from `dataclasses.fields`.

**Wolfram status:** every call computed. `wolframscript` ran locally, exit 0, no `Name::tag` message, no `$Failed`/`$Aborted`, and each result printed an evaluated value. All Wolfram-derived figures above are attributed to **Wolfram Language (local Wolfram Engine, via `wolframscript`)** and none is the sole source for any claim. No call failed to evaluate in this dispatch.

## Delivered files

- `scripts/joint_order_invariance_is_budget_conditional_2026-10-06.py` — set-event invariance proof (no independence needed), SymPy product form, SymPy truncation asymmetry, the budget-truncation loss table, and the `p/c` exchange argument + brute force. Answers `--help`. Exit 0.
- `scripts/joint_gamma_sign_condition_2026-10-06.py` — closed-form `Δβ` sign condition and crossover index r\*, validated against the repo's own `_estimate_gamma` by finite difference, plus the archive flip measurement with Wilson intervals. Answers `--help`. Exit 1 (the 0.30 arm is crossed).
- `scripts/joint_attempt_level_denominator_2026-10-06.py` — derived upward-bias sign plus entry-level vs attempt-level rankings, with `--strip-sim` to reproduce the `_base` pooling. Answers `--help`. Exit 1 (inversions found).

No `bench/` module added, no flag added, no default changed. Everything above is measurement; the one code change both J3 fixes require (`RoutingResult.attempts` with dispatch condition) is named, not smuggled in, because it belongs at the single call site with a test that exercises it.

## Residual disagreement

1. **Whether a minimum sample is a safeguard or a cost is not settled — it is conditional on a fact neither position measured.** The derivation is exact; its premise holds only if no budget ever truncates the ladder. Both designs include a truncating guard, so on today's designs n_min has positive measured value (0.0506 expected resolution-probability per truncated finding at d = 2). If the ledger genuinely never bites, B is right and n_min is dead weight. Nobody has counted `rung_unfunded`/budget-truncated climbs in a real run, and nobody can until exhaustion is enabled.
2. **Capability ranking is load-bearing for cost only, but the two positions still disagree about cost, and A's rule is dominated unless rung costs are equal.** Order-invariance does not resolve this; it relocates it. A reader should carry forward that "rank on v-bar, cost may only veto" and "rank on p/c" resolve the *same* criticals at *different* spend, and that the spend difference has not been measured on a live roster.
3. **The selection effect remains unfixed and currently unfixable.** 46.10% of multi-rung routing records cannot attribute their non-final rungs; same-depth same-item pairs are 0 by construction; A's recoverable pairs are confounded by dispatch condition and B's depth strata are confounded by the identity of prior failures. Both seats proposed a fix for which the deciding data does not exist. Do not read either as deployed.
4. **The γ coupling is confirmed and its remedy is not.** Recording-only is the right minimal step, but it leaves a gated run reading a number whose value depends on an undeclared input (`routing_max_rungs`). My position — re-calibrate the 0.30 band on the uncensored series before enabling exhaustion in a gated run — is stronger than B's and is not something B proposed. It is also unexecuted. Treat the 0.30 band as calibrated on a censored series until someone re-derives it.
5. **Two of B's figures did not reproduce at the stated magnitude.** 5/11 rank inversions came out 3/11 here, and 2/14 came out 2/12 — same two runs, different inclusion rule. The defects are confirmed; the specific percentages are estimator-dependent and should not be quoted as stable. B's "24 orderings of 5 rungs" is a miscount (5! = 120).
6. **A's `routing_max_rungs` claim is stale and its `None` sentinel collides with the tree.** `0` already expresses exhaustion end-to-end (executed). Applying A's `None` sentinel would silently change the meaning of `routing_max_rungs: null` for any config that carries it. This is unresolved between the positions and must not be merged unexamined.
7. **One latent hazard, deliberately not inflated.** `rank_falsifier_writers` normalises `-SIM` for *ranking* but matches `exclude` on raw labels, so a bare/suffixed mismatch would route a finding back to the model that already failed. 0 of 20 archived SIM runs exhibit the mismatch, so it is not a present defect. It becomes one the first time `source_model` and roster labels are written by different code paths.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 13 recorded tool call(s).

<!-- verbatim-begin: fable (panel capability_ladder_joint_2026-10-06) -->

The write was not permitted, so no file is delivered; every figure below was computed in this dispatch's logged Bash calls (the inline Python shown above) and is reproducible from the quoted code. Proceeding to the verdict.

---

## J1

**PERSUADED**, with one named residual that is covered, not open. The derivation is sound at its core: under exhaustion every rung is tried regardless of its estimate, so the estimate orders cost and gates nothing — and my own n_min = 5 fails its stated purpose anyway, since a Jeffreys posterior at n = 5 misorders nearly as freely as at n = 1. A sample floor on a non-gating statistic is a cost. I withdraw it.

The residual: the derivation has a second premise nobody stated — **the token ledger does not bind**. By construction (computed above): roster {A, B}, finding F1 where A confirms cheap (c_A = 10) and B is expensive and weak (c_B = 100), shared ledger 115. Correct order leaves 105, funding F2; the misordered ladder leaves 5, and F2's every rung is unfunded. So a bad estimate *can* exclude a rung — on a *different finding*, through the ledger. This does not rescue the minimum sample (it wouldn't prevent the misorder either). The correct guard is exactly Position B's invariant extended one step: cost may reorder a rung and may never remove one, **and budget exhaustion is recorded as an unfunded-rung outcome, never as a verdict** — which both positions already provide. Note these are the same mechanism under two coined-adjacent names (`routing_deferred_reason` in A, `rung_unfunded` in B); only one field should exist, and it should take whichever name is already written into the tree.

Conditionality stays explicit: no-minimum-sample is a theorem about *exhaustion configs*. Under the default cap of 2, the estimate selects which 2 rungs exist and does gate. The two rulings are coupled, as B said: removing the cap is what makes the imperfect measurement safe.

## J2

**PERSUADED on the derivation; HOLDING on "structural, cannot be tuned away."** I re-verified independently rather than trusting B's figures: SymPy over **all 120** orderings of 5 symbolic rungs, residual set {0}; the adjacent-interchange identity E[cost](a,b) − E[cost](b,a) = Q(c_a·p_b − c_b·p_a), residual 0 in SymPy and 0 in Wolfram Language (local Wolfram Engine, computed); p/c-descending vs exhaustive permutation optimum over 1000 random 5-rung rosters, worst gap 0.0. The interchange sign gives the global order: a before b iff p_a/c_a > p_b/c_b. Derived, not quoted.

Consequence I accept: my design reduces to the same index-rule family at a dominated point. "Rank on v-bar, cost as feasibility veto" is the strongest-first order — suboptimal in 90.93% [89.99%, 91.78%] of B's rosters — and my feasibility veto is the c → ∞ limit of the same index, not a separate mechanism. So the composition here is genuine in the founder's sense: one ratio, one mechanism, veto as its limiting case. p̂/c is the order.

What I hold: order-invariance assumes p_i is a fixed property of (model, finding), independent of depth and history. B's own aid levels 1–2 feed the previous rung's falsifier source and traceback forward, making p position-dependent — and B's own measurement shows position-dependent cost already breaks the index rule by 1.6393%. Under aid, order *can* change which findings resolve, so the structural guarantee holds only at aid level 0. B concedes this obliquely ("must be measured against R2, not assumed under it"); I make it blocking for aid levels: **no aid-laddered rung enters the p̂ denominator as if it were a depth-0 attempt until a measurement shows confirm rate at fixed (model, finding) is depth-stable.** That measurement settles it.

## J3

**HOLDING: neither the same fix nor incompatible — two coarseness levels of one conditioning family, and they must not be composed yet.** My same-finding decisive pairs are exact matching on the item: the within-item contrast over discordant pairs (the conditional-logistic/McNemar construction, to give it its standard name). Item difficulty cancels exactly; attempt *conditions* (depth, aid, context) do not — in a decisive pair the later model always attempts at greater depth. B's depth stratification is the converse: conditions cancel within a stratum; item composition does not, because **under a frozen order, depth confounds model identity** — the rung-1 model generates no depth-3 data, and depth-2 items are precisely "items the rung-1 model failed," a model-specific hard set. So B's "the selection is fully observed" overclaims: `rungs_tried` records the *count*, and full conditioning on observables would be on the failure *set*, whose cells at 294 total rung records are single-digit — B's own early-stop concedes exactly this.

Are they composable? A true composition — same-finding pairs matched on depth — cannot occur within a run (one model per depth per finding) and across runs requires order variation. Here is the one genuinely new structural fact: **the p̂/c ordering itself generates that variation**, because cost estimates drift run to run, so the exhaustion design manufactures its own identification over time. But no committed measurement yet shows the composite dominating either fix alone, and the founder's ruling is verbatim that coexistence is not composition. So: record both from the same telemetry (per-rung `(model, verdict)` attempts — my `RoutingResult.attempts` serves both estimators), run both estimators observationally, compose only when they disagree *and* a measurement says the composite dominates. They share a telemetry requirement, not a mechanism.

## J4

**PERSUADED on all three parts, and the implication runs the opposite way from the worry.** I did not raise this blind; I verified it rather than voting for it. Code: `_NON_NOVEL_TERMINAL_STATUSES = {"MERGED", "DUPLICATE", "UNCONFIRMED", "REFUTED"}` at `reference_runner_v3.py:8634` — `UNCONFIRMED` is dropped from the settled novelty series and `CONFIRMED` is not, so a critical the ladder resolves enters at `open_since_round` (line 8662–8667), exactly the injection the flip experiment models. Intervals: 2/14 = 14.2857%, Wilson [4.0094%, 39.9414%], closed form ≡ statsmodels to 1e-12, Wolfram Language agreeing to every printed digit ({0.04009392127146494, 0.3994137949697035}). Late skew 9/14 = 64.29% [38.76%, 83.66%]. Mechanism is consistent with the curve arithmetic: mass added late steepens the cumulative, β rises, γ = 1 − β falls. Operator re-ran it against the live archive. Tools decided.

What follows for the founder's ruling: **exhaustion does not make convergence harder; it makes the gate honest.** Today a critical that exhausts the ladder terminates `UNCONFIRMED` and becomes invisible to *both* arms of the two-sided gate — not novel (dropped from the series), not pending. A run can therefore pass while carrying unresolved criticals the gate cannot see. Exhaustion converts some of those to CONFIRMED, which is genuine late novelty, which γ correctly reports as non-convergence. The two downward crossings are runs whose convergence verdict was flattered by invisible unresolved criticals. So the coupling is an argument *for* the run-until-resolved ruling, and γ is not demoted — it is vindicated. Recording-only is the correct minimal step, with one addition per the additive standard: the second `gamma_critical` series must be read by at least a test asserting it is emitted per round, or it is this project's 12th addition nothing reaches.

## J5

**PERSUADED on both.** The denominator: the 2026-10-06 repair is mine, and B is right about what it still omits — the filer's failed attempt never enters the filer's denominator, a numerator-only flattering of weak filers. 5/11 inversions = 45.45%, Wilson [21.27%, 71.99%] (recomputed, closed form ≡ statsmodels). Attempt-level accounting is the fix, and my per-rung `attempts` telemetry is sufficient to compute it; accepted without reservation.

The `-SIM` pooling: verified at `bench/routing.py:95–97`. One precision the joint record should carry: the stripping was a *deliberate* 2026-08-30 decision (the comment at lines 86–91 records why — bare vendor names in the frozen tuple meant a simulated panel fell entirely into `extras` and the ladder order went unrehearsed), and for frozen-tuple *position* it is benign. The hazard is prospective and of the most serious class: the moment any measured p̂ keys its history on `_base(m)`, Codex-SIM's 71.50% pools into Codex's 27.94% (non-overlapping intervals) and a live ladder runs on simulated history. The fix is scoping, not deletion: **history keys on the full label, always; `_base` survives solely for frozen-tuple position lookup.** That preserves the 2026-08-30 purpose and blocks the contamination, and it satisfies the additive standard — nothing removed, one invariant added at the one place the estimator will be built.

## What changed my mind

- **J1 — minimum sample withdrawn.** By the gating argument ("under exhaustion every rung is tried regardless of its estimate") combined with my own observation that n = 5 would not prevent misordering anyway.
- **J2 — rank-on-capability-alone abandoned for p̂/c.** By the order-invariance derivation, which I re-verified over all 120 orderings, and the 90.93% [89.99%, 91.78%] strongest-first-suboptimality figure. My cost-as-veto is the c → ∞ limit of the same index, so this is a reduction, not a compromise.
- **J4 — accepted whole.** I did not raise it; the `_NON_NOVEL_TERMINAL_STATUSES` membership check against the live tree plus the reproduced 2/14 crossing figure did it, and the gate-honesty reading makes it coherent with the founder's ruling rather than against it.
- **J5 denominator — accepted against my own repair.** The 5/11 inversion measurement is exactly the committed-measurement standard; my repair fixed credit and left the denominator wrong.

## What I still hold, and why

1. **Aid levels break the order-invariance premises.** p position-dependence voids the "structural, cannot be tuned away" guarantee; B's own 1.6393% figure for position-dependent cost is the warning shot. Settled by: confirm rate at fixed (model, finding) measured across depths with aid on.
2. **"Selection fully observed by depth" is an overclaim.** Depth confounds model identity under any fixed order; full conditioning is on the failure set, which starves at 294 records. Settled by: agreement or disagreement between depth-stratified and pair-based rankings once p̂/c-driven order variation accrues.
3. **The ledger leak in J1.** A bad estimate can exclude a rung through a binding budget — by construction, computed above. Covered by loud unfunded-rung recording in both designs; I hold it only as the stated conditionality of the no-minimum-sample theorem.
4. **Route-back-to-self vs exp56's pre-registration stays a human decision.** Silently implementing the founder's ruling mid-experiment changes a pre-registered outcome; no derivation in this round touches that.
5. **The frozen tuple survives as cold-start tie-break only** — both seats agree, both flag it as weaker than the founder's ruling, and the committed measurement that would delete it (a p̂-derived order dominating on resolutions-per-token in a live run) still does not exist.

## Measurements

| figure | value | Wilson 95% | tools |
|---|---|---|---|
| P(resolve) order-invariance, **all 120** orderings of 5 rungs | residual set {0} | — | SymPy; Wolfram Language (interchange residual 0) |
| Interchange identity ΔE[cost] = Q(c_a p_b − c_b p_a) | residual 0 | — | SymPy; Wolfram Language (local Wolfram Engine), `InputForm[0]` |
| p/c order vs exhaustive optimum, 1000 random 5-rung rosters | worst gap 0.0 | — | NumPy + exhaustive permutation search |
| Runs crossing γ ≥ 0.30 arm downward | 2/14 = 14.2857% | [4.0094%, 39.9414%] | closed form ≡ statsmodels (1e-12); Wolfram Language {0.04009392127146494, 0.3994137949697035} |
| Unresolved-critical late skew | 9/14 = 64.2857% | [38.7644%, 83.6553%] | closed form ≡ statsmodels |
| Rank inversions, entry- vs attempt-level | 5/11 = 45.4545% | [21.2713%, 71.9908%] | closed form ≡ statsmodels |
| Crediting disagreement, current slice | 17/17 = 100% | [81.5682%, 100%] | closed form ≡ statsmodels |
| Ledger counterexample (L=115, c_A=10, c_B=100) | good order leaves 105 (fundable); misorder leaves 5 (not) | — | arithmetic, executed |

All Wolfram calls computed (local Wolfram Engine via `wolframscript`, run serially); none returned unevaluated, `$Failed`, or a `Name::tag` message. Attribution: Wolfram Language. Code citations verified by Read/Grep against the live tree: `bench/routing.py:95–97, 139, 158–170`; `bench/reference_runner_v3.py:7000–7005, 8634–8667`. Note for the record: the `int(... or 2)` coercion I reported blind is already repaired in this staging (`or 2` removed 2026-10-06, runner line 7000–7004), so that finding is discharged, not pending.

## Delivered files

None. A consolidated evidence script (`scripts/joint_round_checks_2026-10-06.py`) was prepared but the sandbox write was not permitted this dispatch; every figure above is reproducible from the inline Python quoted in this round's logged Bash calls, and the full script text is preserved in the transcript.

## Residual disagreement

1. **Does order-invariance survive aid levels?** Unresolved and load-bearing: if aid makes p depth-dependent, the "ladder order is cost-only" theorem — the foundation of J1's no-minimum-sample and J2's index rule — holds only at aid level 0, and B's 3-rung self-ladder for 1-seat panels rests on the unproven premise that aid raises p̂ at all. One measured run with aid on settles both directions.
2. **Depth-stratification vs same-finding pairs** remains two estimators, not one: deliberately not composed, pending the order variation that p̂/c itself will generate. A reader should expect them to disagree initially and should treat that disagreement as the measurement, not as a defect.
3. **Whether `rung_unfunded`-style exclusion is acceptable at all** under the founder's run-until-resolved ruling: a binding ledger reintroduces a cap by another route. Both seats record it loudly; neither has said whether a halted-unfunded critical satisfies "resolved or exhausted." It does not, and someone must rule on which bends — the ledger or the ruling.
4. **The exp56 conflict** (route-back-to-self vs pre-registered 1-seat outcome) is deliberately left undecided by both seats and must go to the human.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/capability_ladder_joint_2026-10-06/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
