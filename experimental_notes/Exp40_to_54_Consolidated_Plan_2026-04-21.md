# CDSFL Consolidated Plan — Canonical Source of Truth

**Date:** 2026-04-21 15:40 BST
**Status:** Canonical SST plan for Experiments 40 through 54. Supersedes prior scratch notes.
**Branch:** `exp39-experimental` at HEAD `616ad43` (re-audit recommit pending).
**Runner:** `bench/reference_runner_v2.py` (v2, 4922 lines, active for Exp 40–54). `bench/reference_runner.py` (v1) retained only as frozen Exp 38/39 historical baseline.

This plan is the single authoritative document for the 15-experiment arc. The plan contains **15 experiments**: **14 component studies (Exp 40–53)** each examining a distinct aspect of the framework, and **1 integration experiment (Exp 54)**. "Exp 54" is never "the next experiment after Exp 40" — thirteen component experiments (Exp 41–53) intervene.

---

## 1. Standing constraints

| ID | Constraint | Source | Status |
|----|------------|--------|--------|
| S1 | `bench/reference_runner.py` (v1) is frozen on disk as Exp 38/39 historical baseline only. | Plan 17 April 2026; memory `feedback_runner_v1_v2.md` | Enforced |
| S2 | `bench/reference_runner_v2.py` (v2, 4922 lines) is the Exp 40–54 runner. Must be named as v2 explicitly in any Exp 40+ reference. | Plan 17 April; memory `feedback_runner_v1_v2.md` | Enforced |
| S3 | `eta_int_modulator` wired into `compute_rk` from Exp 40 onward via F2 (overrides original 17 April deferral to Exp 54; subordinate to shadow-promotion-now policy). | Pre-launch audit 20 April; plan §2 F2 | Pending activation |
| S4 | Specialist cells mathematics, statistics, biology, information_science are `live_operational`. K (physics), L (chemistry), M (engineering) are `shadow_integrated`. | `bench/immune_agents.py:334` `LIVE_SPECIALIST_DOMAINS` frozenset | Enforced; K/L/M pending promotion under §5 below |
| S5 | Cell types ≠ tools. Cell types are dispatch units (`CellType` enum in `bench/immune_agents.py:210`). Tools are verifier primitives (~20 entries in `bench/cdsfl_registry/tool_manifest.toml`). A B-Cell specialist routes claims across multiple tools per `bench/cdsfl_registry/domains/immune/<domain>.toml`. "Biology specialist biopython routing" is a category error. | Memory `feedback_bcell_not_tool.md` | Enforced |
| S6 | 2×2 factorial stays at Exp 54 (study-design decision, not deferral). §17 and §18 live from Exp 40 onward. | Plan 17 April; §4 Exp 54 | Enforced |
| S7 | Topology: star (each panel model talks only to CC1; no cross-model leakage). | Plan 17 April; all confer scripts | Enforced |
| S8 | Compelled convergence: panel produces single unified position per topic; no menu-for-hub. CC1 MUST NOT synthesise "consensus" from a split in its own head. | Memory `feedback_compelled_convergence.md` (with CC1-synthesis clause 21 April) | Enforced |
| S9 | Shadow-promotion-now is the default (activate shadow elements now unless demonstrably harmful). Conditionally safe: each promoted component must pass a non-distortion check against the `40_gate.json` pass_condition before live activation. | Memory `feedback_shadow_promotion_now.md` | Enforced |
| S10 | `40_gate.json` pass_condition is the sole Exp 40 acceptance gate: `γ ≥ 0.30 OR 3 consecutive rounds with 0 novel CRITICAL findings`. γ-alt via `reference_runner_v2._check_gamma_alt_convergence` at line 1064. | `bench/exp40_configs/40_gate.json`; re-audit 20 April | Enforced |
| S11 | Stage 6 orthogonality: R_k measures validity; ν_k measures novelty; c_ext measures search quality. Three independent reporting dimensions — never collapsed into a single score before reporting. | Canonical Stage 6 model; `docs/MATHEMATICAL_APPENDIX.md` | Enforced |
| S12 | Lessons-forward chain: each experiment's lessons fold into the next experiment's runner configuration, not back into v2's runtime logic during the current run. Cross-experiment interactions that would distort Exp 54 factorial attribution need explicit handling (see Gate C threshold-freeze). | Plan 17 April; Round 1 RQ2 fold-in | Enforced |
| S13 | Divergence modulator `m_div ∈ {1.00, 0.85, 0.70, 0.60}`. `eta_int_modulated = m_div · eta_int`; `eta_combined = eta_int_modulated · (1 − c_ext(1 − ν_k))`. `m_div` MUST NOT act as a pre-factor on R_k, MUST NOT count toward ν_k. `w(f)` in `q_eff` forbidden. | Canonical Stage 6 model | Enforced |

---

## 2. The 15-experiment arc — per-experiment rows

Pass criteria default to the `40_gate.json` pattern: `γ ≥ 0.30 OR 3 consecutive rounds with 0 novel CRITICAL`; topology=star; max_rounds=8; earliest_stop=3. Row-specific pass criteria override where named.

| # | Experiment | Target article | Specialist focus | State entering | Carried from | Named risks | Pass criterion (if differs from default) |
|---|------------|----------------|-------------------|----------------|---------------|-------------|------------------------------------------|
| 1 | **Exp 40 — Infrastructure Gate** | `bench/dm/_feedback.py` (§17 module, ~22K chars) | All live specialists; §17 parser first live exercise | F1–F4 folded in; D/E/F/J live; K/L/M shadow; §17, §18 default-on; `eta_int_modulator` wired via F2 | arc head | Parse yield under new wrapper; specialist cell sanity on first live run; first live exercise of §17 admissibility parser (39 tests pass offline, zero live data) | default + **Gate C preflight** for §17 admissibility parser (added 21 April, RQ1 fold-in) |
| 2 | **Exp 41 — Mathematics Specialist** | `bench/dm/_convergence.py` or `bench/dm/_suppression.py` | Mathematics B-Cell specialist routes mathematical claims via `sympy + dimensional_analysis + uncertainty_propagation` per `domains/immune/mathematics.toml`. **§6c BINDING PRE-ENTRY ACTIONS (2026-05-16 neutral confer): (1) enable `merge_arbitration_enabled=true` in the Exp 41 config — G7 first-exercise context + run the §6b G7 close-criterion integration test; (2) read the R17–R21 `_finding_id_collisions` accumulator — if any `cross_model=True`, implement UUID-namespace before Exp 41 (co-test with G7); (3) implement in-round reformat re-dispatch ONLY if the R17–R21 post-mortem shows material non-stale malformed extract failures under 1e. See §6c for the technical rationale behind each.** | Exp 40 fixes folded; G7 enabled + §6c actions discharged; mathematics specialist live-validated | Exp 40 bugs; §17 parse-yield lessons; R_k wrapper behaviour; §6c deferred-item evidence | Over-routing (Exp 36 pattern); silence on non-mathematical claims; SymPy sandbox edge cases missed by F1 regression; G7 first-live-exercise integration faults | Mathematics specialist verdict count > 0 on SymPy-verifiable target claim; no specialist routing errors; G7 live-exercise produces no wrong-merge against fix-verification |
| 3 | **Exp 42 — Expert Encodings S_k** | `bench/cdsfl_registry/composer.py` | Composer / S_k admissibility across vendor encodings | Mathematics calibration from Exp 41 applied | Exp 40–41; mathematics thresholds | S_k format mismatch across vendors; composer finding IDs triggering parser false-positives | S_k ADMISSIBLE rate > 0 across all panel vendors on encoded-fix targets |
| 4 | **Exp 43 — Macrophage Admissibility** | `bench/immune_agents.py` macrophage subsection (~20K chars bounded unit) | Macrophage verdict wiring; admissibility signal generation | Macrophage verdict wiring fix (Item 1B.1) confirmed on synthetic data | Exp 40–42; AUTOIMMUNE_REJECTION vs DEPLETION_EXPECTED split (Item 1C.1) | False autoimmune flags in late rounds; verdict wiring regression under live load | Non-zero Macrophage observations across ≥ 3 rounds; AUTOIMMUNE_REJECTION fires only on content-rejection, not duplicate-rejection |
| 5 | **Exp 44 — Composition Test** | Synthetic composition of 41 + 42 + 43 outputs (mechanical interface check, no new target) | Cross-module interface validation | Three specialist-or-cell modules live-validated | All prior; all specialist calibrations | Interface mismatch between math specialist, composer, Macrophage; shared state pollution | Composed outputs pass type checks; convergence signal on synthetic data |
| 6 | **Exp 45 — Statistics Specialist** | `bench/dm/_memory.py` (beta-binomial memory, CUSUM drift) | Statistics B-Cell specialist routes statistical claims via `statsmodels + scipy + uncertainty_propagation` per `domains/immune/statistics.toml` | Composition lessons from 44 | Prior; statistics specialist `scipy.stats` routing | CUSUM threshold miscalibration; statistics specialist confusing point-estimate claims with distributional claims | Statistics specialist verdict count > 0 on distributional target claim |
| 7 | **Exp 46 — CS/Software Specialist** | `bench/dm/_divergence.py` (§18 module, ~20K chars) | Information-science / CS specialist; §18 module as test article | §18 live since Exp 40; first time §18 module is also the test article | Prior; any §18 divergence-directive issues surfaced 40–45 | Self-referential confound (the module being tested IS the directive mechanism); recidivism detection self-loop | Convergence; recidivism detection (Item 1E.9) confirmed; no circular attribution |
| 8 | **Exp 47 — Biology Specialist** | Synthesised minimal native biology module (15–25K chars, purpose-built) — committed 21 April (RQ6 5/5 convergence: no suitable native module, synthesis preferred over adapter to preserve Stage 6 orthogonality between c_ext and target validity) | Biology B-Cell specialist routes mathematical claims via `sympy + biological_sequence + dimensional_analysis`; logical via `z3`; statistical via `statsmodels + scipy + uncertainty_propagation` per `domains/immune/biology.toml` | Prior lessons applied | Prior; biology specialist multi-tool routing | Target must contain falsifiable biological claims amenable to biopython sequence verification and other tools in the domain config; specialist silence if synthesised content leans on metaphor rather than mechanism | Biology specialist verdict count > 0 on a native biology claim embedded in the synthesised target; synthesis justified against Part 3 selection criteria |
| 9 | **Exp 48 — Information Science Specialist** | `bench/evidence.py` (641 LOC, ~23K chars, confirmed right-sized) | Information-science B-Cell specialist | Prior lessons applied | Prior | Information science specialist overlap with mathematics specialist on probabilistic claims; evidence module self-test artefacts | Information science specialist verdict count > 0; no specialist-to-specialist routing conflict |
| 10 | **Exp 49 — Cross-domain Synthesis** | Synthetic integration of 41 + 45 + 46 outputs (mathematics + statistics + CS) | Cross-specialist routing thresholds | Three live specialists calibrated | All prior | Integration emits contradictions under competing specialist verdicts; Macrophage unable to arbitrate multi-specialist disagreement | Integration without unresolvable contradiction; convergence signal. **Post-Exp-49 reorder review:** if tier inconsistencies surface, revisit three alternative orderings raised 21 April (Gemini §18-first; ChatGPT swap 46/48; DeepSeek stats adjacent to 41) — default is retain current |
| 11 | **Exp 50 — Microglia** | `bench/dm/_shadow_stage6.py` (self-referential calibration module) | Microglia; Stage 6 calibrator shadow-log audit | Prior lessons; Stage 6 calibrator shadow-log audit fix (Item 2.3) applied | Prior; Ouroboros query-quality fix (Item 1E.8) prerequisite | Calibrator inputs garbage-in-garbage-out if Ouroboros query quality regressed; self-referential feedback loop | Calibrator produces `(ν_k_proxy, c_ext, H_ratio)` triples with ≥ 2 distinct values across rounds |
| 12 | **Exp 51 — Physics Shadow (K)** | Synthesised minimal native physics module (15–25K chars, purpose-built) — committed 21 April (RQ6a 5/5 NO native convergence; DeepSeek composer.py candidate withdrawn after specialist agreed `bench/cdsfl_registry/composer.py` lacks physics-relevant dimensional density; synthesis preferred over adapter to preserve Stage 6 orthogonality) | Physics B-Cell specialist (K, shadow): routes mathematical claims via `sympy + dimensional_analysis + astronomical`; per `domains/immune/physics.toml` | Prior; K shadow built functional per Item 1E.4 | Prior; pint + astropy.units dimensional-analysis routing | Shadow verdict noise; false dimensional-analysis alarms on code-only claims; synthesis must embed falsifiable physics claims (kinematics, conservation laws, dimensional consistency) that exercise the pint + astropy + sympy toolset | Physics shadow logs verdicts without affecting pipeline; verdict rate within expected range (tentatively 0.1–0.5 per finding for physics-tagged claims) |
| 13 | **Exp 52 — Chemistry Shadow (L)** | Synthesised minimal native chemistry module (15–25K chars, purpose-built) — committed 21 April (RQ6 5/5 convergence) | Chemistry B-Cell specialist (L, shadow): routes chemical-structure claims via `chemistry_structure` (RDKit); dimensional via `dimensional_analysis`; per `domains/immune/chemistry.toml` | Prior; L shadow built functional per Item 1E.4 | Prior; RDKit stoichiometry routing | Synthesised SMILES content must exercise RDKit parse + stoichiometry path without triggering noise on valid molecules; chemistry shadow silent on non-molecular claims (baseline) | Chemistry shadow logs verdicts; SMILES validity gate fires appropriately |
| 14 | **Exp 53 — Engineering Shadow (M)** | Synthesised minimal native engineering module (15–25K chars, purpose-built) — committed 21 April (RQ6 5/5 convergence) | Engineering B-Cell specialist (M, shadow): routes mathematical via `sympy + uncertainty_propagation + dimensional_analysis`; per `domains/immune/engineering.toml` | Prior; M shadow built functional per Item 1E.4 | Prior; safety-factor calculation routing | Synthesised content must embed falsifiable engineering claims (load factors, material tolerances) that exercise safety-factor routing; false positives without structural context remain baseline concern | Engineering shadow logs verdicts |
| 15 | **Exp 54 — Integration run with 2×2 factorial** | TBC — candidate: `bench/reference_runner_v2.py` itself (runner-tests-runner meta-test) | Full system, factorial attribution | All 40–53 fixes folded; `eta_int_modulator` live since Exp 40 (F2); all thresholds **frozen** per Gate C threshold-freeze; frozen thresholds applied identically across Cells A/B/C/D | All lessons from the 14-experiment arc | Factorial attribution confounded if §17 and §18 co-live for 14 prior experiments (tier calibration settled — mitigated by threshold-freeze); Cell A data quality — not merely integrity but confound-by-runner-evolution (Gemini RQ3 minority position) | All four cells complete under frozen thresholds; attribution via two-way ANOVA or equivalent GLM. Contrasts: §17 main = (B+D)/2 − (A+C)/2; §18 main = (C+D)/2 − (A+B)/2; interaction = (D−C) − (B−A). **Cell A integrity 3-layer strategy:** (1) archive integrity check — γ trajectory from Exp 36–38 archive reproduces within tolerance; (2) Fallback 1 (Gemini): fresh Cell A run at Exp 54 codebase with §17/§18 off; (3) Fallback 2 (DeepSeek): sensitivity analysis bounding via Cell B/C early rounds, report interaction-only |

**[Correction 2026-08-05.]** Row 2 above offers `bench/dm/_suppression.py` as an alternative Exp 41 target. **`bench/dm/_suppression.py` was never created** — not moved, not deleted: no path of that name exists at any commit in this repository's history (`git log --all --name-only --format="" | grep -i suppress` returns nothing), so there is no live path to redirect a reader to. Exp 41 ran against `bench/dm/_convergence.py`; the three Exp 41 configs (`bench/exp41_configs/41_convergence.json`, `41b_first_principles.json`, `41c_first_principles_run.json`) name that module and no suppression module. Suppression logic lives inside existing files (`bench/dm/_convergence.py`, `bench/dm/_immune.py`), never in one of its own. The row is left intact as the record of a target choice still open on 2026-04-21. Separately, `bench/exp54_configs/` in row 17 of §4 (Shadow element status) is correctly marked *(to be created)* / *not present* and remains so — that is a forward-looking item, not a dead reference.

**Exp 54 factorial cells:**
- **Cell A:** Exp 36–38 baseline archive (§17 off, §18 off) — subject to 3-layer integrity strategy above.
- **Cell B:** §17 on, §18 off.
- **Cell C:** §17 off, §18 on.
- **Cell D:** both on (current state from Exp 40 onward).

---

## 2a. Target-article scope briefs (Exp 47, 51, 52, 53)

Round 2 closed the Exp 47/51/52/53 target-article question with 5/5 convergence on **minimal native synthesis** — short modules, 15–25K characters each, written for the purpose, one per experiment. Each module must embed falsifiable claims that exercise the routed specialist tool set for its domain; adapting third-party content was rejected because it would conflate **c_ext** (a search-quality metric that measures how well the loop explores the claim space) with **target-module validity** (whether the article under review is sound in its domain), which are intended to be orthogonal variables in the experiment design.

The 15–25K character budget comfortably accommodates 4–6 distinct claim clusters per module. Each cluster names its falsifiability route (which tools in the B-Cell specialist's `tool_manifest.toml` routing would be expected to fire) and includes at least one intentionally false claim so the specialist has something to reject; a module that produces only confirmations tells the panel nothing about discriminative capacity.

### Exp 47 — Biology (native synthesis, ~15–25K chars)

Biology B-Cell specialist routes per `domains/immune/biology.toml`: mathematical → `sympy + biological_sequence + dimensional_analysis`; logical → `z3`; statistical → `statsmodels + scipy + uncertainty_propagation`.

Claim clusters:
1. **Sequence-validity claims.** DNA / RNA / protein sequences with assertions about validity, GC content, open reading frames, stop-codon positions. Falsifiability route: `biopython` `Seq` operations + regex cross-check.
2. **Dimensional claims.** Molar mass, concentration, reaction-rate kinetics with explicit units. Falsifiability route: `pint` dimensional analysis.
3. **Statistical-distribution claims.** Allele frequency, Hardy–Weinberg equilibrium, χ² goodness-of-fit. Falsifiability route: `scipy.stats` + `statsmodels` cross-check.
4. **Mathematical claims.** Logistic-growth ODE with specific parameters, population-dynamics fixed points. Falsifiability route: `sympy` + optional `scipy.integrate` numerical cross-check.
5. **Logical claims.** Boolean relationships among gene-expression, regulatory, or pathway states. Example: "if gene A is overexpressed then gene B is repressed" rendered as `¬(A ∧ B)`; or "operon X is active iff (regulator Y is bound) and not (repressor Z is bound)". Falsifiability route: `z3` constraint solving against the stated propositional structure. *(Cluster added 2026-05-10 after Round 2 panel review: 4/5 models flagged that the original 4-cluster brief did not exercise the biology specialist's `z3` routing path declared in `domains/immune/biology.toml`.)*
6. **At least one intentionally false claim** for specialist-rejection test. Example, corrected after Round 2: a DNA sequence labelled as a complete open reading frame for a named protein, where translation of the stated nucleotides produces a premature stop codon that contradicts the labelled protein length. The codon error attaches to the nucleotide-level claim, not to the protein sequence itself; protein sequences (amino-acid strings) do not contain codons, so the original "protein sequence with invalid codons" framing was a category error.

### Exp 51 — Physics (native synthesis, ~15–25K chars)

Physics B-Cell specialist routes per `domains/immune/physics.toml`: mathematical → `sympy + dimensional_analysis + z3 + astronomical`; logical → `z3 + sympy`; statistical → `statsmodels + scipy + uncertainty_propagation`. *(Routing text corrected 2026-05-13 per Round 3 verification against the source TOML, which routes both mathematical and logical claims to z3; the prior brief text omitted z3.)* Specialist is K, shadow until Exp 51 live-flip.

Claim clusters:
1. **Kinematics claims.** Projectile motion, orbital period, free-fall timing with specific numerical values. Falsifiability route: `sympy` symbolic + `pint` dimensional + `astropy.constants` cross-check.
2. **Conservation laws.** Energy conservation in elastic collisions, momentum in two-body scattering, charge invariance under named transformations. Falsifiability route: `sympy` + numerical bounds via `scipy`.
3. **Dimensional consistency.** F = ma verification, P = W/t, specific relativistic-limit sanity checks. Falsifiability route: `pint` + `astropy.units` cross-check.
4. **Special-function claims.** Specific integrals, series expansions of physical quantities, asymptotic limits. Falsifiability route: `sympy` + `mpmath` (arbitrary-precision cross-check).
5. **Logical / conservation-violation claims.** Propositional structures the specialist can test for unsatisfiability via z3. Example: "energy in = energy out + dissipation; dissipation asserted negative" — z3 derives the contradiction. Other candidates: forbidden-transition selection rules in atomic spectra; causality violations under named coordinate transformations. Falsifiability route: `z3` constraint satisfaction. *(Cluster added 2026-05-13 per Round 3 — physics.toml routes both mathematical and logical claims to z3; the original four-cluster brief did not exercise this routing.)*
6. **At least one intentionally false claim** (e.g. a kinetic-energy formula missing the ½ factor) for specialist-rejection test.

### Exp 52 — Chemistry (native synthesis, ~15–25K chars)

Chemistry B-Cell specialist routes per `domains/immune/chemistry.toml`: chemical-structure claims via `chemistry_structure` (RDKit); dimensional via `dimensional_analysis`. Specialist is L, shadow until Exp 52 live-flip.

Claim clusters:
1. **SMILES validity.** Valid and invalid SMILES strings with assertions about parse success and molecular identity. Falsifiability route: `rdkit.Chem.MolFromSmiles` + regex structural cross-check.
2. **Stoichiometry.** Balanced-equation claims with coefficient-sum assertions. Falsifiability route: `rdkit` + `stoichiometric_balance` (the manifest entry in `bench/cdsfl_registry/tool_manifest.toml` for atom-balance verification; `collections.Counter` is the underlying stdlib primitive used inside the routed tool, but the brief names the manifest entry, not the primitive). *(Tool name corrected 2026-05-13 per Round 3 5/5 convergence.)*
3. **Molecular-weight claims.** Specific molecules with stated molecular weights in g/mol. Falsifiability route: `rdkit` `Descriptors.MolWt` + `pint` dimensional check.
4. **Functional-group identification.** SMARTS-pattern claims for carbonyl, hydroxyl, amine presence. Falsifiability route: `rdkit` substructure matching.
5. **At least one intentionally false claim** (e.g. an unbalanced equation claimed as balanced) for specialist-rejection test.

### Exp 53 — Engineering (native synthesis, ~15–25K chars)

Engineering B-Cell specialist routes per `domains/immune/engineering.toml`: mathematical → `sympy + dimensional_analysis + linear_programming`; logical → `z3`; statistical → `statsmodels + scipy + uncertainty_propagation`. *(Routing text corrected 2026-05-13 per Round 3 verification against the source TOML, which routes mathematical claims to linear_programming and does NOT include astropy or astronomical; the prior brief text was inaccurate.)* Specialist is M, shadow until Exp 53 live-flip.

Claim clusters:
1. **Load-factor calculations.** Beam deflection, column buckling, stress–strain with specific numerical values. Falsifiability route: `sympy` + `pint` (via `dimensional_analysis`) + `uncertainties` propagation.
2. **Material-tolerance claims.** Stated tolerance ranges for yield strength, fatigue limit, with uncertainty propagation. Falsifiability route: `uncertainties` package + `scipy` for confidence bounds.
3. **Safety-factor routing.** Nominal load vs. worst-case load with specific safety-factor values. Falsifiability route: manual formula re-derivation (`sympy`) + dimensional check (`pint`).
4. **Dimensional consistency across subsystems.** Units across mechanical, thermal, electrical domains. Falsifiability route: `pint` (via `dimensional_analysis`). *(`astropy.units` removed 2026-05-13 per Round 3 5/5 convergence — not declared in `engineering.toml` routing path.)*
5. **Optimisation / constrained-design claims.** Linear-programming claims about load distribution, resource allocation, or material selection under explicit constraints. Example: "minimise mass subject to safety-factor ≥ 1.5, deflection ≤ δ_max, cost ≤ budget" with stated optimal vertex. Falsifiability route: `linear_programming` (PuLP). *(Cluster added 2026-05-13 per Round 3 — engineering.toml routes mathematical claims to linear_programming; the original four-cluster brief did not exercise this routing.)*
6. **At least one intentionally false claim** (e.g. a safety factor stated as dimensionless but computed with non-cancelling units, or an LP solution claimed optimal that violates one of the stated constraints) for specialist-rejection test.

### Drafting cadence and storage

Each module drafts ahead of its experiment's entry, not at entry. Draft files land under `bench/cdsfl_registry/targets/` (directory created on first module draft): `targets/exp47_biology.md`, `targets/exp51_physics.md`, `targets/exp52_chemistry.md`, `targets/exp53_engineering.md`. Each draft reviewed against Part 3 selection criteria (claim density, falsifiability coverage, no metaphor, one intentional false claim) before insertion into its experiment run.

**[Correction 2026-08-12.]** All four filenames in the sentence above —
`targets/exp47_biology.md`, `targets/exp51_physics.md`, `targets/exp52_chemistry.md`
and `targets/exp53_engineering.md` — are dead, and they are dead for two independent
reasons: the domain-to-experiment mapping moved, and the files that were eventually
written have since been removed from the tree on a founder ruling. **First, none of
these four names was ever used.** `git log --all
--name-only --format="" | grep 'cdsfl_registry/targets/.*\.md'` returns exactly
seven paths, and the target modules among them are `exp48_chemistry.md`,
`exp49_engineering.md`, `exp50_physics.md`, `exp51_biology.md`, `exp52_factorial.md`
and `exp53_zone_controller.md`. Biology landed at Experiment 51, not 47; physics at
50, not 51; chemistry at 48, not 52; engineering at 49, not 53; Experiment 52 became
the 2×2 factorial capstone and Experiment 53 the zero-plant control. Experiment 47
was re-scoped away from an exam article altogether and ran against an in-repository
module (`bench/exp47_configs/47_divergence_locationkey_live.json`). **Second, the six
files that did exist were deleted from the working tree** in commit `ddd74bd`
("Founder ruling: passphrase-sealed keys and targets out of the repository"),
which replaced them with `bench/cdsfl_registry/targets/MANIFEST.md`. So even a
reader who corrected the names would find nothing at HEAD. The exposure position for
those articles is recorded in that MANIFEST, not here. The sentence is left intact
as the record of the drafting plan as it stood on 2026-04-21.

---

## 3. Fold-in consolidation across all review rounds

Rounds 1–4 of the pre-launch panel review (commit `b3d9420`) were **reverted** at `5c81f33` on 20 April 2026 after the "v1 preservation" framing was identified as a category error between v1 (historical) and v2 (active). The re-audit under corrected framing is the authoritative source for pre-launch fold-ins.

Five review events inform the current plan. Fold-in status below.

| Round | Date | Script / document | Status | Material fold-ins |
|-------|------|-------------------|--------|-------------------|
| Pre-launch audit Rounds 1–4 | 18–20 April | Commit `b3d9420` (reverted `5c81f33`) | **Reverted** — v1 preservation framing refuted | None retained. All poisoned artefacts removed (memory files `project_exp40_prelaunch_lock.md`, `feedback_runner_preservation.md` deleted; TTS files purged). |
| Pre-launch re-audit Round 1 (corrected framing) | 20 April 17:42 BST | `bench/logs/confer_exp40_reaudit_round1/combined_20260420T164144Z.json` | Closed | F1 SymPy sandbox restoration (`immune_agents.py:977`); F2 1E.10 wrapper activation (`reference_runner_v2.py:3510`) — 4/5 activate; F3 debug q-composition assertion; F4 closure-state stratification lexicon (library_complete / shadow_integrated / live_operational); K/L/M shadow-promotion flagged (4/5 activate now, founder decision) |
| Reaudit verified outcome | 20 April | `experimental_notes/Exp40_Reaudit_Verified_Outcome_2026-04-20.md` | Closed | Programmatic verification of all fold-ins; 1620-case identity test for F2 wrapper at `m_div=1.0`; `FindingFeedback` field coverage confirmed superset of proposed 4/5-field minima (no schema change needed); 10-field reason-trace schema rejected 5/5; 4 predicate families rejected 5/5 as gates |
| Plan review Round 1 | 21 April 11:14–11:17 BST | `bench/confer_exp40to54_consolidated_plan_review_2026-04-21.py`; outcome `experimental_notes/Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md` | Closed — splits surfaced; Round 2 dispatched (see §6) | RQ1: Gate C preflight for §17 admissibility parser at `bench/dm/_feedback.py`. RQ2: pre-Exp-54 threshold-freeze (admissibility, severity, tier). RQ3: 3-layer Cell A integrity strategy. RQ4: shadow-promotion-now bounding condition (non-distortion check against pass_condition). RQ6: minimal-native-module synthesis for Exp 47/52/53; Exp 51 conditional on composer.py verification |
| Plan review Round 2 | 21 April 17:32–17:34 BST (dispatch timestamp 20260421T163249Z) | `bench/confer_exp40to54_plan_review_round2_2026-04-21.py`; logs `bench/logs/confer_exp40to54_plan_review_round2_2026-04-21/`; outcome `experimental_notes/Exp40_to_54_Plan_Review_Panel_Round2_Outcome_2026-04-21.md` | **Closed** — 5/5 converged on RQ2, RQ4, RQ5, RQ6a, RQ6b; 3 NO + 1 YES + 1 YES on RQ1 (Codex preflight YES held as Gate C step, DeepSeek alt fixes withdrawn); 3-NO / 2 YES-conditional residual split on RQ3 (operational, not methodological; founder decides) | RQ1: F1–F4 sufficient + Codex preflight retained as Gate C verification (not F-item). RQ2: pre-Exp-54 threshold-freeze unanimous (5/5). RQ3: narrow split; both sides agree runner-version confound matters — disagreement is whether to test archive first or skip to fresh run. RQ4: CONDITIONALLY SAFE with non-distortion check unanimous (5/5). RQ5: retain current ordering (5/5 NO reorder). RQ6: synthesise minimal native modules for all four target articles — Exp 47 biology, Exp 51 physics, Exp 52 chemistry, Exp 53 engineering (5/5). |

**Items explicitly NOT folded in:**

| # | Item | Source | Reason not folded |
|---|------|--------|-------------------|
| N1 | DeepSeek §17 `[VERIFY:current]` flag handling | Round 1 RQ1 YES (DeepSeek only) | Speculative without evidence of current misclassification |
| N2 | DeepSeek §18 cosmetic-rewrite suppression | Round 1 RQ1 YES (DeepSeek only) | Speculative without evidence of current misclassification |
| N3 | Gemini reordering — §18 target to Exp 41 | Round 1 RQ5 YES (Gemini only) | Three incompatible YES proposals; no convergence; retain current ordering, carry as Exp 49 post-mortem watch item |
| N4 | ChatGPT reordering — swap Exp 46/48 | Round 1 RQ5 YES (ChatGPT only) | Same as N3 |
| N5 | DeepSeek reordering — Exp 45 adjacent to Exp 41 | Round 1 RQ5 YES (DeepSeek only) | Same as N3; proposed re-ordering does not tighten any stated hard dependency |
| N6 | 10-field reason-trace schema | Reverted Round 1–4 + Re-audit RQ2 | 5/5 reject; existing `FindingFeedback` fields cover the 4/5-field minima as supersets |
| N7 | Conditional novelty ceiling as runtime guard | Re-audit RQ4 | 5/5 against runtime; 3/5 permit post-hoc sanity computation; operationally identical for Exp 40 |
| N8 | Four predicate families as acceptance gates | Re-audit RQ3 | 5/5 across all four (math-path fidelity, correction fidelity, counterfactual sensitivity, convergence stability) NOT a gate; `40_gate.json` pass_condition is sole gate |

---

## 4. Shadow element status — 17 rows

Every element in the system with a `library_complete / shadow_integrated / live_operational` state below. F4 three-state lexicon applied from `resources/ONBOARDING.md` CDSFL schema index. "Non-distortion evidence" column names the artefact that satisfies the S9 bounding condition for promotion.

| # | Element | Site | Current state | Proposed state (pre Exp 40) | Non-distortion evidence | Promotion action |
|---|---------|------|---------------|------------------------------|--------------------------|------------------|
| 1 | F1 SymPy sandbox allow-list | `bench/immune_agents.py:977` | **broken** (empty `global_dict`; every SymPy verdict currently UNCERTAIN) | live_operational | Regression: `diff(x**2, x) == 2*x` returns 2x; RCE negative test: `__import__('os').system('id')` rejected | D2.SMT — expand `global_dict` allow-list (Integer, Float, Rational, Symbol, Add, Mul, Pow, pi, E, oo, sqrt, Eq, Gt, Lt, Ge, Le, log, exp); keep `builtins={}`; add regression test |
| 2 | F2 1E.10 wrapper activation | `bench/reference_runner_v2.py:3510` call site; wrapper at `:3177` | library_complete (wrapper exists, not called) | live_operational (identity mode) | 1620-case identity test at `m_div=1.0` against Exp 39 baseline, within `1e-9`; wrapper confirmed mathematically transparent for Exp 40 | D2.1E10 — swap `compute_rk(R_old, q, sk, nu_b, nu_f)` for `compute_rk_with_eta_channel(R_old, sk, eta_int=q, m_div=1.0, c_ext=0.0, nu_k=0.0, d=1.0, p=1.0, nu_b, nu_f)`; Exp 39 regression dry-run; flip `eta_int_modulator_wired_into_compute_rk: true` in `40_gate.json` |
| 3 | F3 Debug channel assertion | `bench/reference_runner_v2.py:3510` (one line under `DEBUG_CHANNEL_CHECK` flag) | not present | shadow_integrated (under debug flag for Exp 40 only) | Assertion passes on Exp 39 regression rerun | D2.debug — add `assert abs(q - eta_int*(1 - c_ext*(1 - nu_k))*d*p) < 1e-9` under flag; enabled for Exp 40; evaluate cost vs signal in post-mortem |
| 4 | F4 Closure-state lexicon | `resources/ONBOARDING.md` | **library_complete** (lexicon defined, not applied as labels) | live_operational (applied as labels to every schema element) | Documentation-only; no runtime gate | F4 documentation pass before Exp 40 launch |
| 5 | D — Mathematics specialist | `bench/immune_agents.py:334` `LIVE_SPECIALIST_DOMAINS`; `domains/immune/mathematics.toml` | live_operational | live_operational | n/a (already live) | n/a |
| 6 | E — Statistics specialist | Same; `domains/immune/statistics.toml` | live_operational | live_operational | n/a | n/a |
| 7 | F — Biology specialist | Same; `domains/immune/biology.toml` (routes mathematical → sympy + biological_sequence + dimensional_analysis; logical → z3; statistical → statsmodels + scipy + uncertainty_propagation) | live_operational | live_operational | n/a | n/a |
| 8 | J — Information-science specialist | Same; `domains/immune/information_science.toml` | live_operational | live_operational | n/a | n/a |
| 9 | K — Physics specialist | Same; `domains/immune/physics.toml` | **shadow_integrated** | shadow_integrated until Exp 51 (with enriched audit logging from Exp 40) | Shadow-round logs from Exp 40 onward must show no case where K verdict would have changed the `40_gate.json` pass_condition outcome if applied live | D2.KLM step 1 — enrich shadow-audit logging at `bench/immune_agents.py:5328-5399` to retain verdict content (not only count); flip to live_operational at Exp 51 if non-distortion holds |
| 10 | L — Chemistry specialist | Same; `domains/immune/chemistry.toml` | **shadow_integrated** | Same as K | Same as K, evaluated at Exp 52 | Same mechanism as K, evaluated at Exp 52 |
| 11 | M — Engineering specialist | Same; `domains/immune/engineering.toml` | **shadow_integrated** | Same as K | Same as K, evaluated at Exp 53 | Same mechanism as K, evaluated at Exp 53 |
| 12 | §17 feedback directive | `bench/dm/_feedback.py` | live_operational (since Exp 39) | live_operational | 39 offline tests pass; live Gate C preflight for admissibility parser at Exp 40 launch | Gate C preflight per Round 1 RQ1 fold-in |
| 13 | §18 divergence directive | `bench/dm/_divergence.py` | live_operational (since Exp 39) | live_operational | Offline tests pass; recidivism detection (Item 1E.9) evaluated at Exp 46 self-referential test | No pre-Exp-40 action; recidivism check lives at Exp 46 |
| 14 | Stage 6 calibrator | `bench/dm/_shadow_stage6.py` | shadow_integrated (produces `(ν_k_proxy, c_ext, H_ratio)` triples to logs) | shadow_integrated | Pipeline-neutral (logs-only); promotion gated on Exp 50 data | No pre-Exp-40 action; promotion candidate evaluated at Exp 50 post-mortem |
| 15 | Ouroboros query-quality fix | `bench/dm/_shadow_stage6.py` (shadow calibrator hook) | shadow_integrated (calibrator hooked 14 April) | shadow_integrated | Prerequisite for Exp 50 Microglia — cross-verified at Exp 50 entry gate | No pre-Exp-40 action; verified at Exp 50 entry |
| 16 | Gate C preflight (§17 admissibility parser) | `bench/dm/_feedback.py` live-path preflight | not present | shadow_integrated (preflight step at Exp 40 launch) | Live parsing behaviour matches offline-tested behaviour | Add preflight step to Exp 40 launcher; runs before first live dispatch |
| 17 | Gate C threshold-freeze (Exp 54) | `bench/exp54_configs/` (to be created) | not present | live_operational at Exp 54 launch | Frozen thresholds applied identically across Cells A/B/C/D; calibration drift from co-live §17+§18 during Exp 40–53 prevented from contaminating single-channel main-effect attribution | Threshold-freeze step added to Exp 54 Gate C checklist; action item lands at Exp 53 post-mortem |

**Summary by state (pre-Exp-40-launch):**
- live_operational: 6 (D, E, F, J, §17, §18)
- shadow_integrated → live_operational on F1/F2/F3/F4 fold-in: 4 (F1, F2, F3, F4)
- remaining shadow_integrated through component experiments: 6 (K, L, M, Stage 6 calibrator, Ouroboros, Gate C preflight)
- live_operational at Exp 54 only: 1 (threshold-freeze)

---

## 5. Residual founder-decision items (pre Exp 40 launch)

Three items require explicit founder authorisation before Exp 40 launches. The re-audit and Round 1 converged on panel positions; the shadow-promotion-now policy recommends activation; the bounding condition (S9) requires non-distortion evidence per element. Each item is listed with its current state, the panel convergence, the non-distortion evidence, and the proposed action.

| Item | Site | Panel (re-audit + Round 1) | Non-distortion evidence | Recommended action |
|------|------|----------------------------|--------------------------|---------------------|
| **SMT sandbox fix (F1)** | `bench/immune_agents.py:977` | 5/5 for activate (3 NOT REQ / 2 REQ on label; action convergence) | Regression test (derivative + RCE negative test) satisfies bounding condition | **Activate pre-launch** |
| **1E.10 wrapper activation (F2)** | `bench/reference_runner_v2.py:3510` | 4/5 for activate (Gemini dissent on "required"; algebraic identity verified; dissent resolved in Gemini's direction by 1620-case test) | 1620-case identity at `m_div=1.0` within `1e-9`; R_k discrepancy §17 feedback class independent of `:3510` call site | **Activate pre-launch (identity mode)** |
| **K/L/M live-promotion (S4 expansion)** | `bench/immune_agents.py:334` `LIVE_SPECIALIST_DOMAINS` | 4/5 shadow-promote now; 5/5 NOT REQUIRED. Round 2 RQ4 5/5 CONDITIONALLY SAFE: non-distortion check against `40_gate.json` pass_condition is a hard precondition for the frozenset flip. | **Enriched shadow-audit logging landed 21 April** at `bench/immune_agents.py:5400-5428` — structured per-verdict detail (claim_id, verdict, severity, tool_used, evidence excerpt) now written to `_shadow_log`. Measurement pending Exp 40 onward. Non-distortion metric: do shadow K/L/M verdicts duplicate, contradict, or extend the core-cell verdicts in a way that would change the `γ ≥ 0.30 OR 3 consecutive rounds 0-novel-CRITICAL` outcome? | **Hold frozenset flip; enriched logging live; measure across Exp 40–50 rounds; flip K at Exp 51 / L at Exp 52 / M at Exp 53 if non-distortion holds for that domain** |

The third item is the textbook case for the S9 policy: activate audit enrichment now (so data is captured from Exp 40 onward), measure non-distortion across rounds, flip the frozenset once the bounding condition is demonstrably satisfied. Step 1 (enrich logging) is complete as of 21 April 17:44 BST.

---

## 6. Round 2 outcome and residual items

Round 1 produced splits on every RQ. CC1 MUST NOT synthesise "consensus" from a 3-2 or 2-3 split in its own head (memory `feedback_compelled_convergence.md`, CC1-synthesis clause added 21 April). Round 2 dispatched 21 April 15:40 BST, 5-model responses received 17:32–17:34 BST, yield-or-refute per RQ. Every model gave one definitive position per RQ — no new alternatives emerged.

### Round 2 converged positions (per-RQ)

| RQ | Round 1 split | Round 2 outcome | Fold-in action |
|----|----------------|------------------|-----------------|
| RQ1 — Unaddressed fix against `40_gate.json` | 3 NO / 2 YES | 3/5 yield to Codex preflight YES (Gate C, not F-item); 2/5 yield to NO (F1–F4 sufficient). DeepSeek's flag-handling and cosmetic-rewrite suppression withdrawn as speculative. | F1–F4 retained as the only F-items. Gate C preflight for §17 admissibility parser added to Exp 40 launcher. |
| RQ2 — Cross-experiment interaction | 3 YES / 2 NO | 5/5 YES — threshold-freeze required pre-Exp-54. CC2 yielded on detection-≠-freezing distinction; DeepSeek yielded on S_k–Microglia interaction being a different concern. | Admissibility, severity, tier thresholds frozen before Exp 54 factorial; identical frozen thresholds applied across Cells A/B/C/D. |
| RQ3 — Exp 54 attribution sufficiency | 4 YES-conditional / 1 NO | **Residual split** — 3 yield to Gemini NO (fresh run required unconditionally); 2 hold YES-conditional (expanded integrity check with fresh-run fallback). Both sides agree runner-version confound is real. | Founder decides. Recommendation: Cell A 3-layer strategy already in §2 Exp 54 row covers both paths — (1) archive integrity, (2) fresh run fallback, (3) sensitivity bounding — is operationally compatible with either position. |
| RQ4 — Shadow-promotion-now offsetting risk | 2 SAFE / 3 CONDITIONALLY SAFE | 5/5 CONDITIONALLY SAFE with non-distortion check. Gemini and DeepSeek yielded on the silent-coupling counterexample. | Bounding condition in S9 ratified. K/L/M enriched shadow-audit logging landed 21 April (see §5); frozenset flip held pending measurement. |
| RQ5 — Ordering of Exp 41–53 | 2 NO / 3 YES (incompatible) | 5/5 NO reorder — retain current ordering. Three mutually incompatible YES proposals could not converge on a single alternative; none tightened stated hard dependencies. | Current ordering retained. Alternative proposals carried as Exp 49 post-mortem watch-items only. |
| RQ6a — Exp 51 physics target | 4 NO native / 1 YES (DeepSeek composer.py) | 5/5 NO native. DeepSeek withdrew composer.py claim on own reread — file handles framework routing and composition, not physics reasoning. | Synthesised minimal native physics module (§2 Exp 51 row). |
| RQ6b — Fallback for Exp 47/52/53 | 3 synth / 1 adapter / 1 synth-with-physics-exception | 5/5 synthesise. Codex yielded on orthogonality argument — adapter conflates `c_ext` (search quality) with target-module validity. | Minimal native synthesis committed for all four target articles (Exp 47, 51, 52, 53). |

### Residual: RQ3 founder-decision

The narrow split on RQ3 is operational (test archive usability first vs. skip to fresh run), not methodological. Both positions share the premise that the v2 runner's evolution since Exp 38/39 creates a real confound for Cell A reproducibility. The 3-layer Cell A strategy in §2's Exp 54 row is compatible with either resolution — it names the integrity check as Layer 1 and the fresh run as Layer 2. Founder selects which layer is authoritative at Exp 54 entry. No Round 3 panel is required.

### CC2 in Round 2

CC2 (Opus 4.6 via CLI piped mode) timed out 3× at 300s each in the post-compaction re-dispatch run (162751Z tag). The Round 2 outcome recorded above is from the earlier successful dispatch (163249Z tag) where all 5 models returned responses. The CC2 timeout in the repeat run does not invalidate the already-captured Round 2 convergence.

---

## 6a. Exp 39 → Exp 40 gap-closure list

Nine residual gap items are carried forward from Exp 38/39 and subsequent pre-launch confer rounds. Each item gets FFAFP (Find–Follow–Analyse–Fix–P-pass) and multi-tool cross-verification where computational. The table below names the current state, whether the item blocks Exp 40 launch, the scheduled close trigger, and the FFAFP status at the time of writing. **Closed** in this context means fix applied, regression test added (where applicable), and the change committed.

| # | Gap | Current state | Pre-Exp-40 blocker? | Scheduled close trigger | FFAFP status | Cross-reference |
|---|-----|----------------|----------------------|-------------------------|--------------|-----------------|
| G1 | Gate C preflight wiring into Exp 40 launcher | Specified in §6 Round 2 fold-in; not wired | **Yes** | Pre-Exp-40 launch | CLOSED | §6 RQ1 / §4 row 12 |
| G2 | K/L/M shadow-audit regression test | Enriched JSON logging landed 21 April; no pytest coverage | No | Pre-Exp-40 launch | CLOSED | §6 RQ4 / §4 rows 9–11 |
| G3 | Ouroboros query-quality calibrator test harness | Zero pytest coverage; prerequisite for Exp 50 self-referential calibration module | No (Exp 50 blocker) | Pre-Exp-50 prep | CLOSED | §2 Exp 50 row / Item 1E.8 |
| G4 | `open_crit_high_count()` REOPENED-status handling | Partial fix applied; no REOPENED regression test | No (v2 correctness) | Pre-Exp-40 launch | CLOSED | Runner v2 correctness |
| G5 | `contested_count()` `grace_period` parameter wiring | Parameter in signature; call-site hardcodes `grace=2` | No (v2 correctness) | Pre-Exp-40 launch | CLOSED | Runner v2 correctness |
| G6 | Specialist-to-specialist verdict-conflict resolution | No arbitration mechanism in v2; Exp 49 cross-domain synthesis assumes one | No (Exp 49 blocker) | Exp 44 post-mortem → Exp 49 prep | Scheduled | §2 Exp 49 row |
| G7 | MERGE deadlock auto-arbitration | D2 escalation only; no auto-merge path | No (Exp 44 boundary concern) | Exp 44 post-mortem | Scheduled | §2 Exp 44 row |
| G8 | Burst-mode Phase 0 convergence override | Not folded; burst mode disabled for Exp 40 | No | Future burst experiment (not scheduled in current 15-arc) | Scheduled | Out-of-arc |
| G9 | F4 closure-state labels applied across all schema elements | Lexicon defined 20 April; applied inconsistently across `resources/ONBOARDING.md` CDSFL schema index | No (documentation) | Pre-Exp-40 launch (ONBOARDING sweep) | CLOSED | §4 row 4 / §6 RQ1 |

**Multi-tool cross-verification pairings, per gap.** Each computational gap gets at least two relevant tools during FFAFP. Pairings called out here align with the standing multi-tool rule (see project CLAUDE.md § Local Tool Constraint Box). G1: AST inspection of `bench/reference_runner_v2.py` launcher + pytest call-path regression. G2: pytest + AST schema check on emitted JSON. G3: pytest + SymPy (for symbolic forms of expected (ν_k_proxy, c_ext, H_ratio) triples) + mpmath numerical cross-check. G4: pytest + `inspect` signature verification. G5: pytest + `inspect` + `dis` for call-site verification that `grace_period` is honoured. G6, G7, G8: scheduled — multi-tool pairings to be nailed down at their respective close triggers. G9: documentation-only; no computational cross-verification.

**Pre-Exp-40 launch path.** Of the nine gaps, G1, G2, G4, G5, and G9 must close before Exp 40 launch. G1 is the operational blocker (Gate C preflight is a hard requirement per §6 RQ1). G2 protects the K/L/M shadow-audit evidence that Round 2's non-distortion check depends on. G4 and G5 are runner v2 correctness items carried from v1-to-v2 porting. G9 is the ONBOARDING label-application sweep that completes the F4 documentation pass landed earlier in the arc.

**Post-launch path.** G3 closes before Exp 50's self-referential Stage 6 calibrator runs (Ouroboros query quality is the named Item 1E.8 prerequisite). G6 and G7 close at the Exp 44 post-mortem because Exp 44 is the first experiment that forces multi-specialist composition to hit live edge cases. G8 is out-of-arc — the current 15-experiment design does not exercise burst mode — and remains documented for a later burst experiment.

**Update 22 April 2026 (overnight shift).** G1, G2, G3, G4, G5, and G9 closed during the 21–22 April overnight shift. Gate C preflight now wired into `bench/launch_exp40.py` with six new tests; K/L/M shadow-audit enriched logging pinned by eleven tests at `bench/tests/test_shadow_audit_klm.py` (fix applied to dict-comp key binding at `bench/immune_agents.py:5411-5421`); Stage 6 calibrator harness pinned by eighteen tests with SymPy-verified delta + noisy-OR identities at `bench/tests/test_shadow_stage6_calibrator.py`; `open_crit_high_count()` REOPENED regression pinned by eleven tests at `bench/tests/test_open_crit_high_count_v2.py` (no fix required; the 22 April `_NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")` literal was already correct); `contested_count()` grace-period behaviour pinned by ten tests at `bench/tests/test_contested_count_v2.py` (parameter respected; no fix required); ONBOARDING closure-state lexicon section added. Full per-item FFAFP traces are in the operational plan `Completed in current window` log. The three remaining gaps — G6, G7, G8 — retain `Scheduled` status; their explicit trigger specifications follow in §6b.

## 6b. Scheduled trigger specifications (G6, G7, G8)

Each scheduled gap carries (a) the upstream event that moves it from `Scheduled` to active FFAFP, (b) the multi-tool cross-verification pairings to apply on activation, and (c) the minimum evidence threshold for the close verdict. A reader looking for the next agent's instructions for these three gaps should match on (a) first; if the entry event has not yet happened, no action is due.

**G6 — Specialist-to-specialist verdict-conflict resolution.**
- *Entry trigger.* **Primary: Exp 49 post-mortem** (cross-domain synthesis experiment), which by construction forces the math + stats + CS specialists to co-rule on shared claims and is the first experiment in the arc that structurally produces multi-specialist verdict co-rule. **Early-observation checkpoint: Exp 44 post-mortem** — Exp 44 is a composition test on math-specialist + composer + macrophage outputs and does not dispatch multiple B-Cell specialists on the same `Finding`, so multi-specialist conflict is not expected to surface there; the Exp 44 logs are nevertheless parsed in case any anomalous cross-specialist path is exercised. Trigger fires on first observed verdict conflict (ACCEPT vs REJECT, ACCEPT vs ABSTAIN, or REJECT vs ABSTAIN) across the two candidate experiments. *Reworded 2026-05-13 per Round 3 5/5 convergence — primary trigger updated to align with the structural reality that multi-specialist co-rule first occurs at Exp 49.*
- *Multi-tool pairings on activation.* pytest (unit tests for the arbitration rule); AST inspection of `bench/reference_runner_v2.py` to locate the dispatch point where two `CellVerdict` results meet; `inspect` to pin the signature of any new arbitration callable; trace-log parsing (pandas optional, plain string matching sufficient) to confirm the conflict cases in the post-mortem evidence set.
- *Close criterion.* (i) Explicit arbitration rule implemented and documented (probabilistic-weighted on `confidence`, precedence-by-domain-priority, or escalate-to-D2 fallback — decision delegated to the post-mortem); (ii) regression test covering the three conflict patterns above plus at least one three-specialist extension; (iii) integration test dispatching two specialists on a synthetic conflict claim and checking the arbitrated outcome; (iv) `_confer_log` extended with a `conflict_outcome` field so downstream replay can distinguish primary vs arbitrated verdicts.

**G7 — MERGE deadlock auto-arbitration.**
- *Entry trigger.* **Primary: Exp 49 post-mortem** (cross-domain synthesis experiment) identifying at least one MERGE deadlock event in the trace log — defined as two specialists each holding a verdict whose combination the current D2 escalation rule cannot resolve into a single unified claim within the round budget. Trace-log field: existing `merge_state` or equivalent escalation marker in `bench/reference_runner_v2.py`. **Early-observation checkpoint: Exp 44 post-mortem** — same rationale as G6 (Exp 44 dispatches a single B-Cell specialist plus the composer plus the macrophage; multi-specialist MERGE deadlock is not structurally possible there); Exp 44 logs are nevertheless parsed in case any anomalous merge path is exercised. Trigger migrates onward to Exp 54 integration if Exp 49 produces no deadlock. *Reworded 2026-05-13 per Round 3 5/5 convergence — primary trigger updated to align with the structural reality that multi-specialist MERGE first occurs at Exp 49.*
- *Multi-tool pairings on activation.* pytest (unit tests); AST inspection of the MERGE path in `bench/reference_runner_v2.py`; `inspect` for any new `resolve_merge` callable; trace-log parsing to build a deadlock taxonomy (minimum three observed patterns before arbitration is designed, to avoid fitting the rule to a single case).
- *Close criterion.* (i) Auto-merge rule specified (probabilistic-weighted, explicit-precedence, or fallback-to-split-claim — decision delegated to the post-mortem evidence); (ii) unit test per taxonomy entry; (iii) integration test running both specialists on a synthetic deadlock claim with the arbitrated outcome pinned; (iv) documentation of the deadlock taxonomy in `docs/ARCHITECTURE.md` under the MERGE-path section.

**G8 — Burst-mode Phase 0 convergence override.**
- *Entry trigger.* Authorisation of a future burst-mode experiment. NOT in the current 15-experiment Exp 40–54 arc by design — burst mode is disabled for every experiment in the arc, so the gap remains documented rather than active. The trigger is external to the arc: a new experiment proposal that explicitly enables burst-mode dispatch, or a post-mortem from a non-burst experiment that argues burst would have helped.
- *Multi-tool pairings on activation.* pytest (unit tests for both burst and non-burst dispatch paths); AST inspection of `RunnerConfig` and the burst-dispatch path in `bench/reference_runner_v2.py`; `inspect` for signature stability of any new `burst_convergence_override` callable.
- *Close criterion.* (i) Burst-mode convergence-override flag added to `RunnerConfig` with documented default (`False` to preserve the current arc's behaviour); (ii) regression test covering both the flag-off path (identical to current behaviour) and the flag-on path (override behaviour specified at experiment entry); (iii) documentation of the override semantics in `docs/ARCHITECTURE.md` under a new burst-mode subsection.

The three entries above all leave the specific arbitration / override rule unspecified at design time. This is deliberate: the correct rule depends on the empirical patterns the post-mortems expose, and pre-specifying the rule before the evidence exists would violate the Popperian discipline the project runs under. Each gap's "arbitration rule" is therefore a placeholder to be filled in from evidence, not a pre-registered algorithm to be verified against evidence.

## 6c. Timing decisions — 2026-05-16 neutral re-confer (binding)

The Exp 40 continuation produced the G7 deadlock evidence; the G7 *mechanism* was subsequently designed from that evidence and implemented (`bench/merge_arbitration.py`, 18 tests incl. 8 adversarial vote distributions, runner integration `_try_merge_arbitration`, config keys in `40_gate.json` default-disabled). The §6b "specify the rule from evidence" placeholder for G7 is therefore satisfied — what remained was a pure *enablement-timing* question, plus two related hardening items. A first confer (2026-05-15) reached 5/5 but its questions presupposed deferral; a neutral re-confer (2026-05-16, five-model star, latest CDSFL schema, deferral required to be technically earned + located here) produced the following **binding timing decisions**. These are not gap-closure triggers (§6b) — they are when-to-act decisions, recorded so the agent at each named juncture acts without re-deriving them.

- **G7 merge-arbitration enablement → DEFER to Exp 41.** Vote 3 NOW / 2 DEFER; resolved on the technically-soundest argument under P-pass, not the count. *Technical reason:* the aggregation logic is adversarially tested, but the candidate-set construction inside `_try_merge_arbitration` (building the candidate list from live `registry.entries`) has never executed against a live registry — the 18 tests stub dispatch with hand-built candidate sets. A bug there yields a *wrong* ≥3/5 majority → `registry.resolve(..., "MERGED", merged_into=WRONG)` → a silent wrong-merge that corrupts the registry and the convergence signal R17–R21 exists to measure. This is asymmetric against the bounded, logged, non-corrupting cost of re-observing known deadlocks, and is precisely the "faked-results" integrity risk the founder named. *Action at Exp 41:* enable `merge_arbitration_enabled=true` in the Exp 41 config (single-specialist, low-MERGE, cheap-failure first-exercise context); G7 stays config-disabled for Exp 40 R17–R21. Exp 41 is also where the §6b G7 close-criterion integration test is run against the now-implemented mechanism.

- **UUID-namespace finding-ID isolation → DEFER to pre-Exp 41, collision-evidence-gated.** Vote 2 NOW / 3 DEFER; substance (1a structural validation ≠ UUID-namespace; the `{f.finding_id: f for f in findings}` collision-overwrite is a real, separate, still-open silent-data-loss bug 1a does not close) was confirmed 5/5. *Technical reason for deferring the rewrite:* the collision is real in principle but **unobserved in any run**; the finding-ID convention is model-prefixed (`CC2_F001` ≠ `Gemini_F001`) so a true collision needs same-model-same-fid-same-round; UUID-namespace touches every canonical-ID keying site = an architectural change that destabilises the 229-test baseline immediately before a resume, for an unevidenced defect — which the project's own Popperian discipline forbids (evidence before architectural action). *Evidence gate (implemented 2026-05-16):* an observation-only finding-ID collision detector (`bench/dm/_feedback.detect_finding_id_collisions`, accumulator `_finding_id_collisions`, cleared at experiment start) instruments R17–R21. *Action at Exp 41 entry:* read the R17–R21 collision accumulator. If any `cross_model=True` collision was logged, implement UUID-namespace before Exp 41 (it co-tests with G7 enablement — both touch the reconciliation pipeline). If none, the deferral is evidence-justified and UUID-namespace remains deferred with the detector left in place as a standing tripwire.

- **In-round reformat re-dispatch → DEFER to Exp 41, R17–R21-evidence-gated.** Vote 4 DEFER / 1 NOW. *Technical reason:* Fix 1e (next-round strengthened STRUCTURE_VIOLATION reformat, implemented) preserves correctness — a malformed fix is rejected and re-requested next round, not silently incorporated. A one-round-delayed finding is **still present for the subsequent round's novelty calculation** (γ-alt triggers on the decay rate over consecutive zero-novel-CRITICAL rounds, not absolute finding count) — the delay shifts timing, it does not remove findings; permanent loss is the Q2 collision bug, not the reformat delay. An in-round re-dispatch adds a re-entrant model-call path inside the reconciliation close path — disproportionate ordering/idempotence/loop risk for a timing optimisation, not a correctness fix. *Action at Exp 41:* implement in-round dispatch **only if** the R17–R21 post-mortem shows a material residual rate of *non-stale* malformed extract failures persisting under 1e (stale findings are out of scope for both mechanisms — the fix text itself is obsolete).

*Methodology note (standing, adopted 2026-05-16).* Fix-timing confers must not present deferral as the baseline. The required question form is: "Is the fix technically sound? WHEN — implement now, or defer? If defer, the specific technical reason (not 'caution') AND the named experiment so it is marked here in §6c." A leading question that contains the answer yields agreement-amplified consensus that cannot be trusted for the timing decision. The 2026-05-15 → 2026-05-16 re-confer is the worked example: the biased round was unanimous defer on all three; the neutral round split 3-2 / 2-3 / 4-1 and reversed the working model's own G7 position under adversarial test.

**Note on G6 / G7 trigger expectations (added 2026-05-10 after Round 2 panel review).** Round 2 surfaced a substantive observation, principally from DeepSeek V4 Pro and corroborated by inspection of the per-experiment matrix: Exp 44 is a synthetic composition test that combines outputs from the mathematics specialist (Exp 41), the encodings composer (Exp 42), and the macrophage admissibility cell (Exp 43). It does not exercise multiple B-Cell specialists co-ruling on the same `Finding`, and is therefore structurally unlikely to produce specialist-to-specialist verdict conflicts (G6) or MERGE deadlocks between specialists (G7). The first experiment in the arc that *does* force multi-specialist co-rule by design is Exp 49 (cross-domain synthesis: math + stats + CS specialists on shared claims). The migration clauses in the G6 and G7 entries above already handle this case — the trigger migrates to Exp 49 if Exp 44 produces no qualifying evidence, and the gap stays open until evidence appears. Read the Exp 44 entries as early-observation checkpoints rather than as the realistic primary trigger; Exp 49 is the realistic primary. No code change is required: the trigger logic, evidence threshold, and migration are already correct in the §6b text above. This note exists to align reader expectations with the experiment design.

---

## 7. Appendix A — canonical file layout

| Artefact | Path |
|----------|------|
| Runner v1 (frozen Exp 38/39 baseline) | `bench/reference_runner.py` |
| Runner v2 (Exp 40–54 active, 4922 lines) | `bench/reference_runner_v2.py` |
| Exp 40 launcher | `bench/launch_exp40.py` |
| Exp N launcher (N ≥ 40) | `bench/launch_exp{N}.py` |
| Exp N config | `bench/exp{N}_configs/*.json` |
| Exp N logs | `bench/logs/exp{N}_*/` |
| Exp N post-mortem (repo) | `experimental_notes/Exp{N}_PostMortem_{DATE}.md` |
| Exp N post-mortem (TTS) | `~/Desktop/CDSFL_tts/Exp{N}_PostMortem_{DATE}.txt` |
| Canonical 17 April execution plan | `experimental_notes/Exp40_to_54_Execution_Plan_2026-04-17.md` |
| Consolidated 21 April plan (in-repo) | `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` |
| **This canonical SST plan** | `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md` |
| Pre-launch panel audit (short) | `experimental_notes/Exp40_Pre_Launch_Panel_Audit_2026-04-20.md` |
| Re-audit verified outcome | `experimental_notes/Exp40_Reaudit_Verified_Outcome_2026-04-20.md` |
| Plan review Round 1 outcome | `experimental_notes/Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md` |
| Plan review Round 2 dispatch | `bench/confer_exp40to54_plan_review_round2_2026-04-21.py` |
| Plan review Round 2 logs | `bench/logs/confer_exp40to54_plan_review_round2_2026-04-21/` |
| Tool manifest | `bench/cdsfl_registry/tool_manifest.toml` (~20 tools) |
| Per-domain immune configs | `bench/cdsfl_registry/domains/immune/<domain>.toml` |
| Live specialist frozenset | `bench/immune_agents.py:334` `LIVE_SPECIALIST_DOMAINS` |

## Appendix B — `40_gate.json` pass_condition reference

From `bench/exp40_configs/40_gate.json` (current state on branch `exp39-experimental`):

```
gamma_threshold: 0.30
consecutive_zero_novel_critical_rounds_for_pass: 3
topology: star
max_rounds: 8
earliest_stop_round: 3
eta_int_modulator_wired_into_compute_rk: false   # flipped true by F2
live_specialist_cells: [mathematics, statistics, biology, information_science]
functional_shadow_cells: [physics, chemistry, engineering]
```

F2 flips `eta_int_modulator_wired_into_compute_rk` to `true` after Exp 39 regression through the wrapped path succeeds at `m_div=1.0`.

## Appendix C — tool / cell type architecture

Three distinct architectural layers. Conflating them is the standing error.

1. **Cell types** (dispatch units) — `CellType` enum at `bench/immune_agents.py:210`: `DENDRITIC, CYTOTOXIC_T, B_CELL, NK_CELL, HELPER_T, REGULATORY_T`. B-Cell has specialist variants (v1 baseline, v2 AST-grounded, specialist dispatch). Each cell returns a `CellVerdict`. `LIVE_SPECIALIST_DOMAINS` at `:334` controls which specialist domains contribute to Helper-T synthesis.
2. **Tools** (verifier primitives) — ~20 entries in `bench/cdsfl_registry/tool_manifest.toml`: `sympy, z3, statsmodels, scipy, dimensional_analysis (pint), uncertainty_propagation (uncertainties), stoichiometric_balance, linear_programming (PuLP), astronomical (astropy), chemistry_structure (RDKit), biological_sequence (Biopython), ml_claim (sklearn), graph_property (NetworkX), type_checker (mypy), lint_check (ruff), security_scan (bandit), bytecode_analysis (dis), symbolic_execution (crosshair), deepseek_formal`. Each maps to a `_verify_<name>` function.
3. **Domain configs** — `bench/cdsfl_registry/domains/immune/<domain>.toml`: per domain declares which tools a specialist routes claims to, grouped by `claim_type` (MATHEMATICAL, LOGICAL, CODE_STRUCTURAL, CODE_BEHAVIORAL, STATISTICAL). Example: biology → mathematical: `sympy + biological_sequence + dimensional_analysis`; logical: `z3`; statistical: `statsmodels + scipy + uncertainty_propagation`.

A claim enters, Dendritic triages to a `ClaimType`, B-Cell specialist dispatch looks up the domain config, reads the tool list for that claim type, and calls the corresponding verifier functions. A cell is never equivalent to one tool; a cell dispatches claims across a set of tools per its domain's config.

## Section 8 — Forward-looking founder decisions to revisit

Five decisions carry forward from Round 2 closure. None is a pre-launch blocker — F1 (SMT sandbox), F2 (1E.10 wrapper), F3 (debug assertion removal) have all landed, K/L/M shadow-audit enrichment is integrated, Round 2 closed via compelled convergence. Each decision requires a founder call at a concrete future trigger. Recorded here as a consolidated decision register; each item anchors back to the section of this plan that carries the full detail.

1. **Experiment 40 launch approval.** With F1/F2/F3 landed, K/L/M enriched, and Round 2 closed, the Exp 40 launch gate moves to founder go/no-go. Trigger: this plan review. Anchors: §5 (pre-launch residuals now resolved), §6 (Round 2 outcome).

2. **Experiment 54 Cell A layer selection.** Research Question 3 closed with a 3:2 residual split on whether Layer 1 (archive-first integrity check with fresh-run fallback) or Layer 2 (fresh-run unconditional) is authoritative for Cell A. The three-layer Cell A strategy in §2 is operationally compatible with either resolution. Trigger: Exp 54 entry, after Exp 40–53 complete. Anchors: §6 (RQ3 residual), §2 (Exp 54 row).

3. **Target-article construction for Experiments 47, 51, 52, 53.** Round 2 converged 5/5 on minimal native synthesis rather than adapter wrapping. Four short native target modules remain to be constructed at approximately 15–25K characters per domain — physics for Exp 51, plus the three domains for Exp 47, 52, 53. Trigger: before each experiment in the 47/51/52/53 sequence; Exp 47 is the first such trigger. Anchors: §2 (per-experiment rows for 47/51/52/53), §3 (RQ 6a, RQ 6b).

4. **Gate C admissibility-parser preflight scheduling.** Round 2 folded Codex's §17 preflight in as a Gate C step rather than an F item. The preflight must be wired into the Exp 40 launcher before first run. Trigger: Exp 40 launcher integration, pre-launch. Anchors: §3 (RQ 1 fold-in), §4 row 16.

5. **Pre-Experiment-54 threshold freeze.** Round 2 closed 5/5 that admissibility, severity, and tier thresholds must be frozen before the Exp 54 factorial, identical across Cells A, B, C, D. Trigger: between Exp 53 close and Exp 54 entry. Anchors: §3 (RQ 2 fold-in), §4 row 17.

No additional panel work is required to resolve any of these. Decisions 2, 4, 5 are scoped in-plan; decisions 1 and 3 are approval/execution gates.

---

**End of canonical plan.** Changes land here after Round 2 convergence and after any code changes (D2.SMT, D2.1E10, D2.debug, D2.KLM) are verified by the full `bench/tests/` suite. sv commits both this document (via Desktop copy + in-repo companion) and any code changes in a single atomic commit per the sv protocol.
