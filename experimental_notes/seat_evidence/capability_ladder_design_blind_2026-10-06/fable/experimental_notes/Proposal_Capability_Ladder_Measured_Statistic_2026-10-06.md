<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'capability_ladder_design_blind_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: f0fa53e2a0a33ef0a37719af1c93f5d186f1e70dc9ccf54f8ae7bf5618092cf4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Proposal: the ladder ranks on a measured, admissibility-gated resolution statistic

Blind-round seat proposal, capability-ladder design, 2026-10-06 (Fable seat).
Evidence script: `scripts/ladder_statistic_demonstration_2026-10-06.py` (re-runnable;
every proportion carries a Wilson interval computed by statsmodels AND the closed
form, posteriors cross-checked against scipy.stats.beta AND Wolfram Language).

## 1. The quantity the ladder ranks on

**Name.** The glossary already names it: the fingerprint's verification dimension
`v-bar` ("fraction confirmed by SymPy or similar", docs/GLOSSARY.md, "Fingerprint").
It is the one promised dimension `_update_observed_fingerprint` never writes. This
proposal defines it precisely and makes the ladder its consumer.

**Definition.** For writer m, v-bar(m) = P(admissible CONFIRMED | re-verified
falsifier attempt written by m), where:

* an ATTEMPT is any falsifier the runner's decider (`reverify_falsifier`) actually
  judged — verdicts CONFIRMED / REFUTED / ERROR / UNTOOLABLE / INTEGRITY_VIOLATION.
  Tool verdicts only; no model prose enters the event stream.
* ADMISSIBLE CONFIRMED means CONFIRMED **and** the falsifier consulted the target
  (the discrimination/provenance pass; `competence_provenance.py`'s "reads" class)
  **and** not INTEGRITY_VIOLATION and not NON_DISCRIMINATING. An INTEGRITY_VIOLATION
  additionally quarantines m's statistic for the run: UNSAFE TO RANK ON, enforced at
  update time, not by a script someone remembers to run.
* CREDIT goes to the model that WROTE the falsifier (`resolved_by_routing` first,
  else `source_model` — the runner's own `_falsifier_owner` rule). Measured on this
  sandbox's archive: 248/248 routed resolutions (Wilson95 [0.9847, 1.0000]) disagree
  with the `source_model` key, so reporter-keyed crediting is wrong on the entire
  routed subpopulation. `scripts/competence_provenance.py` is repaired accordingly.

**Two strata, two roles.**

* ROUTED stratum (attempts on another writer's unresolved critical): the DECIDER.
  Sparse but on-task — it measures exactly the job the ladder assigns.
* ROUND stratum (the falsifier gate's every-round re-verification of each model's
  own falsifiers): abundant but on a different population. It is the always-on
  DRIFT ALARM and the cold-start prior shaper; it never decides rank on its own.

**Estimator.** Jeffreys Beta(1/2, 1/2) posterior over admissible routed attempts:
posterior mean (k + 1/2)/(n + 1), 95% equal-tailed credible interval from the Beta
quantiles. The round stratum enters only as a weak prior: Beta(1/2 + c·k_r,
1/2 + c·(n_r − k_r)) with c chosen so the prior's effective weight never exceeds 2
pseudo-observations (c = min(0.1, 2/n_r)). Rank strongest-first by posterior mean.

**Ties and overlap.** Where adjacent writers' credible intervals overlap, the order
within the overlapping block is decided by, in order: (1) the same-finding pairwise
record (below) when >= 5 decisive pairs connect the two writers; (2) the frozen
Exp-42 tuple, retained SOLELY as a deterministic tie-breaker (additive standard:
nothing is removed; it is demoted from decider to tie-break because its own evidence
is interval-overlapped — at the archive's n≈20 per model, Codex [0.699, 0.972],
CC2 [0.531, 0.888], ChatGPT [0.433, 0.819], Gemini [0.584, 0.919] all overlap; only
DeepSeek-last [0.145, 0.519] is separated); (3) lexicographic label sort, so the
order is reproducible run-to-run.

**Minimum sample.** n_min = 5 admissible routed attempts before the routed posterior
alone may move a writer across a non-overlap boundary. Below n_min the interval is
wide enough that rule (1)/(2) governs anyway — the threshold makes that explicit
rather than emergent.

**Cold start.** No history at all → posterior mean 0.500, CrI [0.002, 0.998]: the
writer ranks BETWEEN measured-strong (mean > 0.5) and measured-weak (mean < 0.5).
This generalises `rank_falsifier_writers`' existing ranked+extras rule — unknown
models are tried, after the known-strong, before the known-weak — instead of the
current behaviour of appending all unknowns last.

**Vendor-agnosticism.** The statistic is keyed on the roster label (with the
existing `-SIM` base normalisation). Nothing reads a vendor name except tie-break
rule (2), which applies only to labels that happen to appear in it; all-same-vendor,
all-identical, and never-seen rosters all rank by the same arithmetic.

**1-model panel.** No pairs and no routed attempts exist; the posterior is the
prior; the ladder is the single writer. The founder's ruling says it should route
back to itself. NOTE A CONFLICT, left for the joint round rather than patched
silently: the current `routing_deferred` path (empty-ladder-by-construction) is
load-bearing for the exp56 1-seat arm's PRE-REGISTERED reportable outcome
(HALTED_IRREDUCIBLE_QUEUE_ALARM). Re-admitting the source as a self-rung implements
the ruling but changes a pre-registered outcome mid-experiment. Decide explicitly;
do not let the implementation decide.

## 2. The selection effect

The ladder sends hard findings to strong writers, so marginal success rates are
depressed by trust. The repair is not to restrict the sample (first-attempts-only
was rightly rejected; populations differ) and not to randomise an audit (routing
fires on ~8% of archived entries — 1370/16500, Wilson95 [0.0789, 0.0873] — an audit
fraction of that stream starves). The repair is to CONDITION ON THE ITEM:

* Every routed attempt is on a finding some other writer already failed. When
  writers A and B attempt the SAME finding, difficulty is identical by
  construction, so (B confirms what A failed) is a decisive pairwise win for B at
  any difficulty mix. Both-fail is a tie and carries information about the finding,
  not the pair — excluded.
* The ladder generates this paired data for free: rung k+1 attempts exactly what
  rungs 1..k failed. Removing the rung cap (Q3) INCREASES the paired sample.
* The marginal Jeffreys posterior remains the rank backbone (pairs are sparse); the
  pairwise record decides order inside interval overlap, where the selection bias
  actually bites. The round stratum, immune to routing selection, is the drift
  alarm: a writer whose round-stratum admissible confirm rate falls below its
  routed-era baseline (interval-separated) triggers re-estimation, exactly the
  drift-alarm role the earlier proposal wanted for the frozen order.

What this was missing until today: the archive records NO per-rung attempts — 87/87
multi-rung routing records (Wilson95 [0.9577, 1.0000]) carry only the last rung's
label, so neither denominators nor pairs could be built. `RoutingResult.attempts`
(bench/routing.py) and the `routing_history.attempts` field (reference_runner_v3)
now record (model, verdict) per rung. The statistic becomes computable from the
NEXT run onward; until n_min accrues, behaviour is the tie-break order, i.e. the
status quo. No measurement, no reorder.

## 3. Removing the rung cap

Exhaustion is roster-bounded, not unbounded: one attempt per distinct available
writer per finding CONTENT-REVISION (a writer is re-admitted only if the finding
changed — corrected copy accepted, new evidence attached). Stopping rule:

    resolved (admissible CONFIRMED)
    OR every feasible writer has attempted this revision -> HIL
    OR the finding's routing token budget is exhausted -> deferred, reason recorded

Cross-round retry remains only for transport faults (the existing path). Budget
exhaustion is recorded distinctly (`routing_deferred_reason`) so it can never read
as model failure and contaminate v-bar. Implemented: `max_rungs=None` sentinel in
`resolve_via_routing` (default 2 unchanged, byte-identical), and the runner coercion
`int(... or 2)` — which turned BOTH None and 0 into 2, making the no-cap ruling
inexpressible (0/288 configs pin the field; Wilson95 [0.0000, 0.0132]) — now maps
null/0 to the sentinel. Tests: bench/tests/test_routing_attempts_and_exhaustion_2026-10-06.py.

## 4. Resource-aware routing

Yes — as a FEASIBILITY FILTER, never a ranking term. Two stages: (1) rank purely on
v-bar; (2) walk the ranked list and SKIP a rung only when the live fingerprint says
the attempt cannot succeed or cannot be afforded: prompt size exceeds the writer's
`measured_attention_span`/`compression_threshold` (fields `burst_planner.py` already
consumes — composition with a demonstrated consumer, not a parallel structure), or
estimated attempt cost exceeds the writer's remaining budget/quota. Every skip is
recorded with its reason. Because cost can only veto and never score, a cheap model
can never outrank by cheapness; it is only ever reached when stronger rungs are
infeasible, and the record says so.

## 5. Reproducibility

A separate step, MECHANICAL, owned by the HARNESS. `reverify_falsifier` already is
reproduction-by-tool; for the STEM-calculator goal, a result ships only with a
replay bundle (falsifier + inputs + environment pin) that the runner re-executes
N=2 times in fresh scratch directories; a verdict that does not reproduce routes to
HIL as nondeterministic. Models must not attest their own reproduction — a model
asserting "it reproduces" is a vote. The human's role is auditing provenance and
forensics, not re-deriving results; HIL re-derivation remains the terminal rung
only for ladder-exhausted findings. (§10's material-defect category 5,
unreproducibility, already names this a hard class.)

## 6. What the brief's framing misses

* **The heterogeneity measurement does not license the fingerprint as-is.** The
  p = 2.21e-59 chi-square is on FINDING RATE — productivity. The live fingerprint's
  only discriminating statistic today is that same productivity, and ranking on it
  puts Gemini first (3.646 findings/round, highest of 5) — the model Exp 55 showed
  confirming 2/2 with detached falsifiers. Wiring the ladder to the CURRENT
  fingerprint reproduces the exact inversion `competence_provenance.py` exists to
  prevent. The fingerprint must gain the admissibility-gated v-bar BEFORE the
  ladder may read it. Productivity never enters the ladder.
* **Crediting was wrong at the measurement layer** (248/248, repaired above).
* **The archive cannot back-derive the statistic** (87/87 denominator gap; forward
  recording added). Do not bootstrap v-bar from old reports; start accruing.
* **No-model-voting compliance.** v-bar is built exclusively from tool verdicts
  plus mechanical admissibility checks, and it is gated the way severity is: as
  `severity_is_proven` keeps an unproven R_k from opening the A4 exemption, an
  unproven confirmation (no admissibility provenance) never enters the numerator,
  and an integrity violation quarantines the writer's statistic. An UNPROVEN number
  opening a gate would be the forbidden model vote; here it cannot.
* **rho and S_k are not reused.** rho measures discovery efficiency (finding
  stream), S_k classifies fixes; the ladder statistic is about falsifier RESOLUTION,
  a different event stream with its own denominator. Reusing either would import a
  population the ladder does not dispatch to.
* **The 1-seat conflict** between the founder's route-back-to-itself ruling and
  exp56's pre-registered deferral outcome (§1 above) must be decided by a human,
  explicitly.

## What this does to gamma

`gamma_critical` is estimated over the settled critical series, and the two-sided
gate also requires no unverified critical pending. Routing changes SETTLEMENT, not
discovery: removing the cap settles hard criticals that today stall at rung 2, so
the pending-unverified side of the gate opens earlier, and the settled series
completes earlier — convergence is reached by RESOLVING more criticals, never by
discarding them. The ranking statistic itself reads only tool verdicts and is read
only by rung order; it writes nothing into the critical series, the novelty counts,
or either gate side (one-way coupling). `test_routing_cannot_flatten_gamma_2026-09-09`
passes unchanged on the patched tree. Expected observable effect: a shorter tail of
`routing_deferred`/HIL criticals; `gamma_critical` values move only through the
timing of settlement, and the two-sided gate's threshold and window are untouched.

## What would refute this proposal

* Q1: a run where the v-bar-ordered ladder resolves FEWER routed criticals per
  dispatch than the frozen order on the same findings (paired, same roster) —
  command: compare `routing_history.attempts` success-at-rung-1 across arms.
* Q2: a measured same-finding pairwise ranking that DISAGREES with the marginal
  routed posterior ranking on interval-separated writers — that would show pairing
  does not cancel the selection effect and the drift alarm is mis-specified.
* Q3: an archived run where `max_rungs=None` produces more than |roster|−1 routed
  attempts for a single finding revision (would falsify the boundedness claim) —
  check `rungs_tried` vs `rungs_available` in routing_history.
* Q4: a run where the feasibility filter skips a strong writer whose attempt would
  have succeeded (measurable once skips are recorded with reasons): >5% wrongful
  skips voids the filter thresholds.
* Q5: a shipped result whose N=2 replay diverges while HIL review finds the
  original verdict correct — would show N=2 is the wrong reproduction depth.
* Q6: a provenance-admissible confirm-rate ranking from a clean run that still
  inverts a known-strong/known-weak pair would refute admissibility gating as
  sufficient, and the statistic must gain a stronger discrimination control.
