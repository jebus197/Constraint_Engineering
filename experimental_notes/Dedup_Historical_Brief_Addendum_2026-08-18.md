# ADDENDUM TO THE DEDUP HISTORICAL BRIEF

**Companion to `experimental_notes/Dedup_Historical_Brief_2026-08-17.md`.**
**Prepared 2026-08-18T08:23+01:00. Verified against HEAD `f53c276` (working tree clean).**

## Scope

The brief maps the *convergence* side of duplicate handling: eight live mechanisms, the closed-doors list, thresholds, and the operating characteristic of the identity rule. It is accurate on that scope and nothing in it is retracted here.

This addendum covers six things it does not cover. It does not restate the eight mechanisms, FELM, the MinHash-on-finding-pairs refutation, the embedding refutations, or the threshold audit. Where a claim here bears on one of those, it is flagged as a correction and the correction is stated, not smoothed.

Archive scope for every recomputed number below, unless stated otherwise: **27 run directories carrying a `*_report.json` with a registry, 2030 canonical entries**, excluding `bench/logs/exp36_evidence_latest/` which is a byte-duplicate of `exp36_evidence_20260407T004931Z`. Internal sweeps quote 2247 entries / 287 MERGED (including the duplicate) and 2315 / 210 (a wider scope that also reads `runner_state.json`-only runs). All three are correct at their own scope. Record the scope with the number.

Everything marked **[executed]** was produced by running the live functions from `bench/reference_runner_v2.py` at HEAD against a five-model `RunnerConfig`. Everything marked **[recomputed]** was measured from `bench/logs/` this session. No live experiment was run and no paid dispatch occurred.

---

# A. THE BUGZILLA STATE MACHINE AS A DUPLICATE-HANDLING DESIGN

## A.1 What it was designed to do

`bench/directives/universal/cdsfl_operational.md:299-320` gives the lifecycle every model is shown every round, and states its purpose in the project's own words at `:317-320`: *"This is the loop closure that makes the panel actually saturate. Without verified fixes transitioning to CLOSED, the panel rediscovers the same findings indefinitely. With them, the active pool drains."* The duplicate arm is one line of that machine: `DUPLICATE -> MERGED into the canonical entry` (`:309`), reinforced at `:334` — *"Findings shown as MERGED have been folded into a canonical entry. That canonical entry is the live target for any additional verdicts."*

`bench/directives/universal/cdsfl_topology_formal.md:100-132` formalises it. T3 specifies preconditions (target and source both in `B.entries` with status in `{OPEN, CONFIRMED, CONTESTED}`), the effect (`source.status ← MERGED`, `source.merged_into ← target`, `target.status UNCHANGED`), the directionality rule, the source-identity resolution, and an anti-loop invariant: `∀ f: f.merged_into ≠ f.canonical_id` and *"The merge graph must be acyclic (a DAG, not a cycle)"*.

That is a complete and careful design. What follows is what runs.

## A.2 DUPLICATE is a state on the designed path that no code ever writes

The word appears in eleven terminal-status sets across the runner (`reference_runner_v2.py:1189`, `:1207`, `:1280`, `:1413`, `:2829`, `:3468`, `:3597`, `:3746`, `:4106`, `:4135`, `:9420`) and in the state machine printed to the panel at `:1305`. Every `registry.resolve(...)` call site in the file passes one of OPEN, REOPENED, CONTESTED, CONFIRMED, CLOSED, UNCONFIRMED, REFUTED or MERGED. None passes DUPLICATE. **[recomputed]** Archive-wide status tally over 2030 entries: `CLOSED 721, UNCONFIRMED 556, CONFIRMED 500, MERGED 201, OPEN 32, REFUTED 20, DUPLICATE 0`.

The brief records that zero at §1.7 and reads it correctly as evidence that immune-pipeline DUPLICATE verdicts never reach a registry status. The stronger reading is available: **the zero is produced by construction, not by absence of duplicates.** Counting DUPLICATE entries in the archive measures nothing about duplicate incidence. It measures that no code writes the value. The one line that renders it — `"(N findings hidden: refuted or duplicate)"` at `:1398-1399`, filtering `hidden_statuses = ("REFUTED", "DUPLICATE")` at `:1280` — can only ever count REFUTED.

## A.3 Five code paths may declare a duplicate. None requires evidence, and only one validates the target

| path | file:line | quorum | target validated | evidence retained |
|---|---|---|---|---|
| panel MERGE quorum | `reference_runner_v2.py:1785-1809` | ≥2 distinct models | **no** | **no** (overwritten) |
| G7 arbitration | `:1698-1725`, resolve at `:1707` | 3 of 5 vote | **no** | vote record only |
| small-panel single vote | `:1856-1866` | **1 model** | **no** | **no** |
| routing ladder | `:3243-3246` | Jaccard ≥ 0.85 | **no** | `routing_duplicate_of` |
| CC2v verification | `:6360-6366` | 1 model, conf ≥ 0.7 | **yes** (`:6361`) | discarded (see below) |

The panel path — which produces almost all merges — destroys the model's stated justification. `reference_runner_v2.py:8909-8910` replaces the verdict evidence with the runner-synthesised literal `f"merged_into={canonical_id}"`. Note also that the prompt's format block at `:5067-5068` gives CHALLENGE an explicit `| [evidence]` slot and gives MERGE none: `MERGE C0001 <- [your_finding_id] — same root cause, combining`.

The consequence for any future audit: **the archives cannot answer whether a single one of the 201 merges was substantively correct**, because nothing retains the reasoning. CC2v is worse in one respect — `_verification_step` resolves the status without ever calling `add_verdict`, so **[recomputed]** across all 2030 entries there are **zero verdicts attributed to model `CC2v`**, while the round-level `verification.duplicates` field sums to **30**. Thirty terminal duplicate decisions with no recorded author, confidence or justification on the entry itself.

MERGE verdicts are also never aged out — the only pruning is the G7 KEEP_DISTINCT branch at `:1716-1719` — so a two-model quorum can be assembled from votes many rounds apart. **[executed]** One MERGE vote at round 1 left an entry OPEN through fourteen `_update_finding_statuses` calls; a second vote at round 15 completed the quorum and the entry merged. **[recomputed]** Archived instance: `exp40_gate` C0002 took its votes from ChatGPT at round 5 and Gemini at round 15 and merged at round 15.

## A.4 The panel's duplicate channel is not lossy — it is inverted

`_resolve_merge_source` (`reference_runner_v2.py:1533-1545`) extracts the source id from the verdict evidence with `re.search(r'(?:F|C)(\d+)', evidence)` and looks up `alias_map[f"{model_id}:{local_id}"]`. `FindingRegistry.register` (`:1053`) stores that key as `f"{model_id}:{finding.finding_id}"` — and `finding_id` was **already model-prefixed by the parser** at `bench/runner_core.py:916` (`full_id = finding_id if finding_id.startswith(f"{model_id}_") else f"{model_id}_{finding_id}"`). The stored key is `Codex:Codex_F001`; the lookup key is `Codex:F001`. The two formats can never meet, and prefixing the source in the verdict does not help because the regex extracts `F001` out of `Codex_F001` too.

**[executed]** at HEAD:

```
parsed finding_id: ['Codex_F001']
alias_map: {'Codex:Codex_F001': 'C0001'}
_resolve_merge_source('F001 - same root cause')  -> None
_resolve_merge_source('Codex_F001 same')         -> None
_resolve_merge_source('C0001 same')              -> 'C0001'
```

The caller does not drop an unresolved MERGE. `reference_runner_v2.py:8906-8912` falls through to `registry.add_verdict(canonical_id, model_id, "CONFIRM", round_idx, evidence)`. **A model saying "these two are the same finding" is recorded as "I independently verify this finding is real", on the merge target.** That spurious CONFIRM then enters `confirm_models - {entry["source_model"]}` at `:1962` and counts toward the two-independent-model quorum at `:1968-1969`. Duplicate pressure is converted into corroboration pressure.

**Correction to the internal sweep that found this.** The CONFIRM fallback is not a runner invention — it is mandated by the spec. `cdsfl_topology_formal.md:126-127`: *"source_canonical = alias_map[m, F_local] / If source_canonical is undefined: treat as CONFIRM on target."* The defect is that the key mismatch makes the fallback fire on **every** local-id merge, which the spec plainly did not intend. The repair is prefix normalisation in `_resolve_merge_source`, not deletion of the fallback.

**[recomputed]** Re-parsing the archived per-model response files with the runner's own `_parse_verdicts`, deduplicated by (run, round, model):

- Seven location-keyed live runs (exp42-lk, 44, 45, 46, 47, 48, 49): **68 MERGE lines emitted, 25 resolvable by canonical id, 43 recast as CONFIRM (63%)**.
- `exp40_gate`: **507 MERGE lines, 389 resolvable, 118 recast (23%)** — reproducing the internal sweep's figure exactly. The rate is lower there because models in that run happened to write canonical-to-canonical references.

The prompt teaches the failing form. `reference_runner_v2.py:5068` instructs `MERGE C0001 <- [your_finding_id]`, and `:5069` separately instructs *"Reference findings by CANONICAL ID"* — two instructions that contradict each other on exactly the field that decides whether the merge resolves.

## A.5 MERGED folds nothing into the canonical entry

`FindingRegistry.resolve` (`reference_runner_v2.py:1113-1121`) sets `status` and `merged_into`. That is all. No severity propagates, no verdicts transfer, no description or evidence is appended.

**[executed]** A 0.95-severity entry carrying two CONFIRM verdicts, merged by two distinct models into a 0.40-severity entry: the target's severity is unchanged at 0.40, its verdict count is unchanged at 0, its description is unchanged, and `open_crit_high_count()` returns 0. The critical is gone from the gate and nothing inherited it.

The directive tells the panel the opposite every round (`cdsfl_operational.md:334`). A merged finding's accumulated corroboration is deleted, not folded, and merging a critical into a sub-critical removes the criticality from the gate entirely.

## A.6 No target validation, no cycle guard, and both have bitten

Nothing on the panel path tests that the merge target exists, that it is still live, or that the merge graph stays acyclic. `registry.resolve(canonical_id, "MERGED", round_idx, merged_into=top_target)` is called at `:1707`, `:1806`, `:1856` and `:1860` with the target taken from a regex over verdict evidence (`:1786-1789`); the only rejection is the literal sentinel `"__unknown__"` at `:1849`. Direct self-merge is blocked at `:8908` by `source != canonical_id`, so one-cycles cannot form on that path — but two-cycles and chains into already-MERGED targets can, and the main pass short-circuits on MERGED at `:1769` so a merged entry can never re-enter play.

**[executed]** Two entries at 0.72 and 0.88, each merged into the other on successive rounds: both end MERGED with mutual pointers, `open_crit_high_count() = 0`, `contested_count(3) = 0`, `irreducible_queue_count() = 0`, and **both are listed in the SETTLED "do not re-describe" block of `build_summary(3)`**. The panel is told the matter is settled and pointed at a dead entry.

**[executed]** Two votes naming `C9999` on a registry containing only `C0001`: status MERGED, `merged_into` `C9999`, `'C9999' in registry.entries` False.

**[recomputed]** Of 201 archived MERGED entries: **62 point at a target that is itself MERGED**, **0 dangle**, **1 self-merges**, and **8 entries lie on a directed cycle across three runs**:

- `exp36_evidence_20260407T004931Z` — two cycles spanning `C0011 ↔ C0028` and `C0176 → C0184 → C0194 → C0176`.
- `exp40_gate_20260514T020550Z` — `C0002` (sev 0.72, opened r0, MERGED at r15 → C0023) ↔ `C0023` (sev 0.88, opened r1, MERGED at r24 → C0002), with `C0033` (sev 0.82, MERGED at r5 → C0023) attached. All three are above `CRITICAL_SEVERITY_THRESHOLD = 0.7` (`:4024`). C0023 alone carries 27 verdicts spanning rounds 2-14. That run went 29 rounds with `converged_at = None`.
- `exp37_evidence_20260409T050932Z` — `C0105`, severity 0.86, `merged_into: C0105`. This violates T3's anti-loop invariant literally (`cdsfl_topology_formal.md:130`). It came from the LLM Dedup Assessor at confidence 0.95 (`bench/logs/exp37_live.log`: `dedup: C0105 -> DUPLICATE of C0105`), whose apply path at `bench/cc2_manager.py:1152-1163` has no self-check even though the pre-filter at `:826-827` excludes the finding itself. The entry is also not a finding — its stored description begins `FINDING_ID: C0086 / SEVERITY: 0.86 / ... / FIND: CONFIRM C0086`, a verdict block parsed as a finding.

Because MERGED is stripped from the gating series (`:4134-4136`), a mutual merge does not consolidate a defect. It deletes it from the convergence count with no surviving canonical entry.

**Latent, not active:** zero archived MERGED entries point at a non-existent id. The reason to fix it anyway is that the project's own regression tests assert the unsafe behaviour — `bench/tests/test_runner_status_transitions.py:317-336` merges into `"C0002"`, which those fixtures never register, and asserts `status == "MERGED"`. A future validity check would be reported as a test failure.

## A.7 The single-model escape hatch promises a reversion that does not exist

`reference_runner_v2.py:1858-1866` merges on one vote when the external panel is smaller than two and writes `hil_reason` = *"Single-model merge (small panel, N external models). Reversion available."* Line `:1864` is the sole occurrence of "Reversion" in the file, and no unmerge mechanism exists anywhere. Structurally it cannot: `:1769-1779` short-circuits on MERGED, and only CLOSED has a REOPEN transition. The HIL is told there is a safety net for a decision the machinery has made irreversible. The project's own test (`test_runner_status_transitions.py:337-347`) asserts the merge and checks only the flag.

## A.8 What MERGED actually does, end to end

One thing. It removes the entry from `_NON_NOVEL_TERMINAL_STATUSES`-filtered series (`:4134-4136`), so the finding leaves the γ input and the `g_3` novelty count; and it removes the entry from `open_crit_high_count` (`:1137`), `contested_count` (`:1207`) and `irreducible_queue_count` (`:1189`). It changes nothing about the surviving entry. **The duplicate arm of the state machine is, in implementation, a delete with a pointer attached.**

## A.9 Is the path exercised at all? Barely, and least where it matters most

**[recomputed]** MERGED share of registry entries, pre- versus post-location-keying:

| era | run | MERGED / entries |
|---|---|---|
| pre | exp36 | 86 / 217 (39.6%) |
| pre | exp40_gate | 53 / 296 (17.9%) |
| pre | exp37 | 16 / 222 (7.2%) |
| pre | exp38 | 6 / 169 (3.6%) |
| modern | exp42-lk | 0 / 52 |
| modern | exp44 | 1 / 82 |
| modern | exp45 | 2 / 39 |
| modern | exp46 | 0 / 27 |
| modern | exp47 | 1 / 70 |
| modern | exp48 | 2 / 37 |
| modern | exp49 | 5 / 38 |
| modern | exp53 | 1 / 40 |

Roughly 2-3% in the era that produces today's results, against 12.67%-23% duplicate incidence in the real Bugzilla corpora the project's own external benchmarking note cites (`experimental_notes/Similarity_Function_External_Benchmarking_2026-08-16.md:36`). The panel emitted 68 MERGE lines across those runs and 43 of them were converted into corroboration. The Bugzilla duplicate path is not currently doing the work the design assigned it.

## A.10 EXTEND — the schema's alternative to duplicating — is parsed, stored, displayed, and read by nothing

`_VERDICT_RE` accepts `CONFIRM|CHALLENGE|EXTEND|MERGE|REOPEN` (`:1503`). `_update_finding_statuses` branches on MERGE, REOPEN, CONFIRM and CHALLENGE. There is no `"EXTEND"` string literal anywhere in `reference_runner_v2.py`. Yet EXTEND is precisely what the prompt offers instead of filing a duplicate: `:5067` — *"check the registry — CONFIRM or EXTEND instead of duplicating"* — and `:5076` — `EXTEND C0001 | [new consequence or edge case]`.

**[recomputed]** Archive verdict tally: `CONFIRM 4470, MERGE 693, CHALLENGE 649, EXTEND 183, REOPEN 21`. **183 occasions on which a model did what the schema asked instead of duplicating, and the schema did nothing with it.**

---

# B. THE MATHEMATICAL MODEL

*This is the section the founder asked for. Direct answer first.*

## B.1 The appendix never defines what makes two findings the same

`docs/MATHEMATICAL_APPENDIX.md` (2019 lines, last substantive change 2026-06-02, commit `8f1c305`) defines no finding object, no identity relation and no equivalence relation over findings. It uses "novel", "duplicate", "unique" and "post-dedup" as though they were grounded, and they are not. The single place it names a relation, it names one that does not exist in the document:

- `:1730` (§7.13, κ_set) — *"those not equivalent to any prior finding under the ≈ relation"*. **[recomputed]** The token `≈ relation` occurs exactly once in the entire file and is never defined.
- `:868` (§7.1a, ρ) — *"novel(t) is the count of findings in round t that are not duplicates of any prior finding"*. "Duplicate" is not defined.
- `:1131` (§7.9, capability fingerprint) — the A component is specified only as *"Post-dedup, post-verification count"*. No dedup rule is given.
- §7.5, §7.6 and §8.2 take intersections, differences and unions over a finding space that is never defined.
- The Notation Summary (`:1871-1983`) lists `s(f1,f2)` and has **no entry for a sameness, identity or equivalence relation**.

Deduplication is an unmodelled primitive. That is the root defect, and it is invisible from inside any single section — which is presumably how an eight-round, six-model, thirty-nine-check coherence audit passed it. Each equation is coherent *given* a sameness relation. None supplies one.

## B.2 What the appendix does have, and why it is not enough

§1.3 is the closest approach. `:1350` defines `s(f1,f2) = (1−β)·content_sim + β·b_class` with `β = 0.2`, `CLASS_BONUS = 0.3`, range `[0, 0.86]` at `:1372`, and a named implementation. That is a **graded score, not an equivalence relation.** Turning it into a relation requires `tau_sim`. **[recomputed]** `tau_sim` occurs three times in the appendix — `:1380`, `:1430`, `:1835` — always as something to be calibrated later, never with a value, and it is absent from the Notation Summary.

Meanwhile the live system carries at least four different values of it at four stages: `bench/dm/_types.py:85` (0.33, lexical), `:88` (0.55, embedding, selected by `bench/dm/_similarity.py:206-231`), `docs/GLOSSARY.md:201` (NK cell, 0.50), and 0.20 for stem signatures (`reference_runner_v2.py:4186`). `docs/GLOSSARY.md:259` warns readers not to confuse two of them. Four thresholds; one undefined symbol in the model.

## B.3 Which quantities inherit the gap

Twenty-three named quantities are functions of a deduplicated count, a set cardinality, or a cross-set operation. Three of them gate live runs.

**Direct — a dedup decision is the input:** η novelty `:198` and `q = η·d·p` `:207`, hence `R_det`/`R_base`/`R_k(i)` `:209`/`:213`/`:218` — the entire unified self-assessment equation; η_int `:263`; η_combined `:260`; ρ `:866`; ρ̄₃ and churn(t) `:872-876`; κ_set `:1728` and `:1408`; κ_rate `:1734`; κ(r) `:1746` and the convergence predicate `:1752`; γ_hat `:1760`; γ = 1 − β via λ(t) `:817`; λ_itc `:846`; A and C in the capability fingerprint `:1131-1132`; Y(t) = N(t)·H̄(t) `:903`.

**Cross-set — requires identity *across models or rounds*:** F_conv `:993`; O_A `:997`; S_sync `:1003`; M_suppress `:1019`; Δ_adopt / Δ_drop `:1054-1060`; Δ̄ `:1071`; κ_adopt `:1740`; Y_union and both emergence conditions `:1272`/`:1278`/`:1280`; δ_ij NMI `:524`.

**Count-ratio — inherits via numerator or denominator:** φ_fmt `:484`; η_dec `:462`; Ŝ_H `:119` and S_sync^emp `:1039`; N_k / c_freq `:1475-1480`; σ `:1215`; D_n, D* `:1191`/`:1203`.

The cross-set family degenerates under the reference runner's identity. `reference_runner_v2.py:8852` keys registration on `(model_id, finding_id)`, so a cross-model echo always mints a separate canonical entry, `C_A ∩ C_B = ∅` always, `O_A = 1` by the empty-set convention at `:999`, `S_sync = 0` by construction, and `|⋃ F_i| = Σ|F_i|`. These metrics do not fail loudly. They return their all-clear value.

**Scope correction to the internal sweep that reported this.** It is a runner-level regression, not a model-level impossibility. `bench/run_round_robin.py:300-321` keys defect identity on `structural_canon_hash(finding)` and `:3248-3280` deduplicates *within a round across models* before taking the set difference. §7.5 was calibrated on that bench. See D.7.

## B.4 What this means for γ-based convergence claims

γ is not a property of a run. It is a property of a run **and** a sameness relation, and the relation is not in the model.

**[recomputed]** Holding the estimator, the round count and the finding population fixed, and changing only the sameness relation — from the runner's settled ID-proxy series (`_settled_novelty_series`, `:4139-4165`) to the location-keyed series the same reports already store (`location_crit_shadow_history`):

| run | criticals, ID-proxy | criticals, location | γ_crit ID-proxy | γ_crit location | spread |
|---|---|---|---|---|---|
| exp42-lk | 40 | 17 | **0.6068** | 0.6866 | +0.080 |
| exp44 | 34 | 12 | **0.4532** | 0.5735 | +0.120 |
| exp45 | 12 | 4 | **0.6213** | 1.0000 | +0.379 |
| exp46 | 12 | 6 | **0.3357** | 0.5793 | +0.244 |
| exp47 | 42 | 12 | **0.3668** | 0.6993 | +0.333 |
| exp48 | 31 | 11 | **0.8847** | 0.8756 | −0.009 |
| exp49 | 30 | 17 | **0.8293** | 0.7728 | −0.057 |

The bolded column reproduces each run's own recorded `gamma_critical_history` final value **exactly, to four decimal places, in all seven runs**, so the recomputation is faithful and the comparison is like-for-like.

Read the consequential rows. **exp46 converged on `CRITICAL_QUIESCENCE_CONVERGED ... gamma_critical=0.336 >= 0.3`** — a margin of 0.036 over the threshold that 19 configs set. Under the location-keyed population of the same run, from the same registry, γ is 0.579. **exp47 converged at 0.367**; the same run under the other relation reads 0.699. Two runs whose convergence verdict rests on a number that moves by 0.24 and 0.33 when you change a definition the mathematical model does not contain.

The zero-tail behaviour splits the same way. exp42's ID-proxy critical series `[20,4,8,3,4,1,0]` reaches zero once; the location series `[10,1,5,1,0,0,0]` reaches zero three times. At the default `gamma_alt_consecutive_zero_crit = 3` one relation converges that run and the other does not, from identical data.

**The honest statement for any paper or claim built on γ:** γ measures the decay of a count, and this project has never written down what the count counts. Every γ figure in the record is conditional on an identity rule that lives only in code, and the two rules in code disagree by up to 0.38 on the project's own runs.

## B.5 Neither live sameness relation appears anywhere in the appendix

Since June 2026 the count side of the convergence gate has been decided by code-location keying, with an unlocated-finding fallback on hard-token Jaccard at 0.20 (`reference_runner_v2.py:4262-4313`, `:4193-4259`, `:4186`; `bench/convergence_location.py:473-480`). **[recomputed]** grep across the appendix for "location" returns only §1.2 `:342-344` (an FFAFP admissibility field — *"a specific location in the code (file, function, line)"*) and §2 `:436`/`:444`. No stem signature. No hard tokens. No location keying.

The timing makes this a gap rather than an omission: the appendix last changed 2026-06-02 (`8f1c305`); the first location-keyed live run is `exp42_composer_locationkey_live_20260609T165146Z`, seven days later; `bench/convergence_location.py` last changed 2026-08-17. **The appendix has not been touched in the two and a half months during which the operative sameness relation was built, armed and revised.**

## B.6 The appendix's own grounded machinery is not on the runner's path

§1.3 similarity, §1.4 continuous suppression and the §7.13 κ family are the one place the model does ground duplicate detection in something computable. All three live in `bench/dm/_convergence.py`. **[recomputed]** `grep -ic kappa bench/reference_runner_v2.py` returns **0**; `ConvergenceDetector` is never referenced; `compute_metrics` and `check_convergence` are never called. §1.4's suppression weight `w(f)`, which `:1406` and `:1424` say enters "the kappa_set numerator only", reaches nothing in a live run.

The detector is nonetheless *fed*: `bench/insect_brain.py:888` inside `persist` (called at `reference_runner_v2.py:8972`) and `:1404` in `signal_complete` (called at `:9842`), which writes `final_kappa` into `completion_signal.json` for every run. So its verdict reaches a published artefact and no decision. See D.8 for what that artefact has been saying.

Two further drifts worth recording because they will mislead a reader:

- §7.13 `:1734` specifies `κ_rate(r) = 1 − λ̂(r)/(λ̂(1) + ε)`, an initial-round baseline. `bench/dm/_convergence.py:310` implements `clamp(1 - lambda_novel(r) / lambda_peak, 0, 1)` with the peak taken over rounds 0..r, changed 2026-05-22. The appendix was never updated.
- §7.10 `:1150` still lists ρ as *"Pending implementation (Task 3 runner fix)"* and `docs/GLOSSARY.md:93` as *"Not yet formalised in the Mathematical Appendix"*, while §7.1a formalises it and `reference_runner_v2.py:1611` implements it with the appendix's own θ_ρ = 0.25 — and it **blocks convergence** on two paths (`:3618-3619`, `:3924-3929`).

κ_set also carries two incompatible notions of sameness inside one formula. §1.4 `:1390` says continuous suppression *"replaces the binary duplicate/novel decision with a smooth weight function"*. It does not — it moves the cliff up one layer. `κ_set(r) = 1 − Σ(w_c · Sev_novel_c)/(Σ Sev_cum + ε)` still needs a binary novel/not-novel partition to know which classes to sum over, and `bench/dm/_convergence.py:185-218` makes that partition with a hard threshold (`if self.similarity_fn(member, prev_f) >= self._tau_sim(): is_novel = False`) on the same score the graded weight uses. Both the cliff and the smoothing are live, on one number.

## B.7 §1.4's permutation-invariance requirement is violated by a live gating path

`docs/MATHEMATICAL_APPENDIX.md:1412-1416` records order-dependence as Error 2 and states the requirement plainly: *"the same set of findings should produce the same convergence assessment regardless of arrival order. Top-k selection is permutation-invariant by construction."*

`_unlocated_novelty_key` (`reference_runner_v2.py:4254-4259`) is greedy first-match over an insertion-ordered bucket list: `for key, prev in buckets: if signature_similarity(sig, prev) >= _UNLOCATED_MERGE_THRESHOLD: return key`. Buckets are appended in iteration order, sorted by `(open_since_round, str(canonical_id))` at `:4293-4296`. **[recomputed]** At the repo's own threshold with the repo's own metric, three signatures with J(A,B) = 0.000 and J(A,C) = J(B,C) = 0.250 yield two novel buckets under orders ABC/ACB/BAC/BCA and one under CAB/CBA. Same three findings, two different novelty counts, decided by which model happened to get the lower canonical id.

This is demonstrated structurally, not observed: the brief notes at §1.4 that no archived run postdates the 2026-08-08 arming, and that is confirmed. The relevant unknown is how many criticals per round land in the unlocated bucket. `convergence_location.py`'s own coverage figure (161/165 located, 97.6%) suggests it is small, but 4 of 165 is not zero and the bucketer is on the gate.

## B.8 The η fork — real, and correctly de-prioritised

The appendix contains an unresolved question about repeated detection. §1.4 `:1420-1424` forbids a similarity-derived suppression weight from entering `q_eff`, because down-weighting a repeated finding penalises corroboration, and records that violating it produced a 113× residual-risk error. §1.1 `:198`/`:207` then defines η, also a similarity-against-priors quantity, and puts it into `q_eff`, where a restated finding gives η ≈ 0 and the Bayesian update is suppressed entirely (`:244`, reduction row: *"η = 0 | q = 0, R unchanged | Redundant finding adds nothing"*).

**The same physical event — a second model reporting the same defect — is corroboration under §0.1/§1 and redundancy under §1.1, and the appendix never says which reading applies when.** The corroboration side is sound and explicitly built for the repeated-detection case, including the correlated case: `:19` Branch 1 `C(n) = 1 − ∏q_i`, `:29` Branch 2 with pairwise coupling ψ_ij, `:38` the SymPy-verified boundedness constraint, `:40` the selection criterion naming confer rounds. §2 `:532` even supplies the observable estimator. The machinery exists and nothing connects it to η.

**One internal sweep quantified the divergence at 3.64× after one repeat and 14.85× after two, and called it "Error 1 in a different coat". Both framings are corrected here.** The prohibition at `:1420-1424` names `w(f)` specifically and scopes itself to suppression weights with top-k semantics; η is a distinct construct with its own stated rationale, so this is an ambiguity, not a literal self-contradiction or a repeat of a fixed error. More decisively, the divergence is hypothetical about a channel that has never carried a value — see C.6. **Wire η first, then measure. Do not fund an experiment on this fork before then; today it would measure a constant.** The same applies to the missing Stage 4→5 derivation (`:194-235` gives parameter descriptions and a boundary-condition reduction table, and no derivation, at the step that introduces η — against `:178-182`, which does derive Stage 3→4 and records SymPy and Wolfram verification).

## B.9 What a reader should take from Section B

The founder's framing — that a very large part of the schema mechanism was built with duplicate and novelty detection in mind — is confirmed at the model level and is, if anything, understated: 23 named quantities depend on a deduplicated count. What is missing is not machinery. The machinery is extensive and mostly careful. What is missing is the one definition all of it rests on.

---

# C. SPEC REQUIREMENTS THE IMPLEMENTATION VIOLATES, RANKED BY CONSEQUENCE

## C.1 T5's γ input is not post-deduplication, and the two sides of the two-sided gate read different populations

`cdsfl_topology_formal.md:210-215`: *"n_r MUST be canonical novel findings (post-deduplication, post-alias-resolution), NOT raw parsed findings. Using raw findings inflates the series with rediscoveries and cross-model echoes, producing a γ that does not correspond to the Duane reliability growth model."*

**This is the item to fix first, and it is the one an internal sweep got backwards.** That sweep filed the γ path as WORKS_AS_INTENDED "in the strong form" and attached an instruction — *"it should not be disturbed by any repair to the items above"*. The instruction is wrong and is withdrawn here.

`_settled_novelty_series` (`reference_runner_v2.py:4139-4165`) filters on **status only**: the four values in `_NON_NOVEL_TERMINAL_STATUSES` at `:4134-4136`. It performs no content comparison, and `bench/dm/_similarity.finding_similarity` is never called on the γ path. "Post-deduplication" therefore holds only to the extent the MERGE channel works — and A.4 shows that channel is 63% inverted and produces 0-5 merges per modern run. A cross-model echo that no model files a MERGE verdict on is counted as novel, which is exactly the contaminant T5 names.

The archived refutation is direct. **[recomputed]** In exp44, entries **C0016 (r1), C0029 (r2) and C0042 (r3)** carry **byte-identical 152-character descriptions** (*"`EvidenceBundle` provides a `save_json` method... but lacks a corresponding `load_json` or `from_dict` method to read them back"*), all three CLOSED, all three counted as novel. Their alias chain is the mechanism caught in the act: `Gemini:Gemini_F006 → C0016`, `Gemini:Gemini_C0016 → C0029`, `Gemini:Gemini_C0029 → C0042` — each round's re-file cites the canonical id it was issued the round before. *Precision note the sweeps missed:* these three sit at severity 0.60, so they inflate `gamma_all` and the `g_3` novel count, not `gamma_critical`.

The second half of this item is the part no sweep but one reached, and it is structural. The location-keyed series overwrites `novel_critical_history[-1]` at `:9297` and **only** that. `gamma_critical` is computed independently from the settled series at `:9322`. The function's own docstring says so at `:4276-4277`: *"It does NOT touch gamma_critical, which is computed independently from the settled series."* So the two-sided gate compares a γ computed over echo-inflated entries against a count computed over location-deduplicated ones, and its convergence-reason string calls them *"the two sides of the same diminishing-returns measure"* (`:4003-4005`). The B.4 table is the size of that mismatch: on exp47 the two populations differ 42 to 12.

Separately, T5's own three-tier γ schedule (`:217-224`) is unreachable by configuration. **[recomputed]** Every Exp 42-49 config sets `gamma_telemetry_only_until` at 20 against `max_rounds` 16 (exp42 non-live: 14 against 12), so `_check_gamma_gate` (`:1597-1609`) returns `("telemetry", True)` on every round of every run. What actually gates is `gamma_critical` against `gamma_alt_threshold` 0.30 — a severity-filtered variant T5 does not define, documented only in a code docstring and config prose. The founder's standing directive that gamma is load-bearing is honoured in substance; the gating quantity is simply not the one the topology spec defines.

## C.2 T3's merge-source resolution is unreachable for the syntax the prompt teaches

`cdsfl_topology_formal.md:124-127` against `reference_runner_v2.py:1533-1545` / `:1053` / `bench/runner_core.py:916`. Full treatment at A.4. Consequence: 43 of 68 modern MERGE lines and 118 of 507 exp40_gate MERGE lines become CONFIRM verdicts on the merge target, feeding the OPEN → CONFIRMED quorum at `:1968-1969`.

## C.3 T3's preconditions and T2's merge invariant are unenforced on every path but one

`cdsfl_topology_formal.md:110-111` (target must exist and be live), `:129-131` (acyclic), T2 `:89` (`f.status = MERGED → target.status ≠ MERGED`). Only `_verification_step` validates, at `:6361`. Full treatment and archive evidence at A.6.

## C.4 T4's `g_3` gate counts each model's report of the same defect separately, against a threshold of 2

`cdsfl_topology_formal.md:155` defines `g_3(r) ≡ novel_count(r) ≤ MAX_NOVEL_FINDINGS`; T5 defines novel as canonical post-deduplication. The implementation feeds the all-severity settled series into `_evaluate_gate_conditions` (`:9339-9340`), checked at `:3644` against `cfg.max_novel_findings`, default **2** (`:483`). A five-model panel that all notice one defect contributes up to 5 to a gate whose ceiling is 2. The gate is measuring panel size times agreement.

**[recomputed]** exp47's as-run all-severity settled series is `[11,6,5,4,6,6,5,6,3,2,4,3,1,3]`; twelve of fourteen rounds exceed the ceiling (ten if rounds 0-1 are excluded — an internal sweep quoted the smaller figure without saying so). That run took 14 rounds and never converged through the state gate. exp44 converged via STATE_CONVERGED at round 12 with the reason string recording `novel=2`, exactly at threshold.

## C.5 ρ is described to models as a semantic measurement it is not, and it is the pre-reconciliation value

The brief covers the first half at §1.11 and §5, and is right. Two things it does not cover.

**First, the ordering.** `_compute_rho` is called at `:8890` and `rho_history.append(rho_current)` at `:8891`. **Both** corrections land afterwards — the γ-input correction at `:8952-8968` and the settled overwrite at `:9264-9269`, 374 lines later in the same loop body. `rho_history[-1]` therefore permanently holds the fully raw pre-reconciliation ratio, and that is exactly what `:8698` and `:8710` render back to the panel next round as *"ρ (discovery efficiency / semantic novelty rate)"*, with the graduated interpretation text at `:8736-8753`. γ sees the settled series; the panel sees the raw one.

**Second, one internal sweep asserted that same-round merges are "caught by the in-round correction". They are not** — 38 of 201 archived merges are same-round, and none of them reaches the number shown to the panel either. The correction only affects `rho_avg` from the *following* round, via the mutated `novelty_counts[r]`.

Because `rho_churn` blocks the state gate (`:3618-3619`) and the critical-quiescence path (`:3924-3929`), an overstated ρ tells the panel there is more new ground than there is, in the rounds where duplicate pressure is highest. **[recomputed]** exp44 round 10 showed the panel ρ = 0.700 (7 of 10 raw) against a settled novel count of 2 for the same round — a true value of 0.200, below the 0.25 churn threshold.

## C.6 §15 and §1.2 both forbid exactly what the runner does with η

`cdsfl_operational.md:572-578` (FFAFP q_retest): *"η comes from similarity computation against prior findings (not self-assessment). d comes from tool output. p comes from domain configuration or persistent memory."* `docs/MATHEMATICAL_APPENDIX.md:368` hardens it: *"None of these factors may be model self-assessments."*

**[recomputed]** `grep -rn model_params bench/ --include='*.py'` returns three lines: a read at `reference_runner_v2.py:7526`, a comment at `:7536` (*"because model_params is never populated"*), and the same read in the v1 runner. Nothing writes it. So `q = meta.get("q", 0.5)` returns the literal **0.5** for every finding, every round, every run, and the call site at `:7594-7600` passes `eta_int=q, m_div=1.0, d=1.0, p=1.0`.

The archive signature confirms it: across all `sk_result` rows carrying an `R_new`, the overwhelming majority are the identical value 0.366667, and every row that differs has `sk < 1.0` — fix quality is the only source of variation and novelty contributes to none of it. Where a model *does* self-report η, `_RK_RE_ETA` (`:7240-7241`) extracts it by regex and `_validate_rk_computation` is documented as *"Advisory only — logs discrepancies, never rejects findings."*

**The one appendix constraint written to stop duplicate detection from becoming a self-report is not enforced, and the channel it governs has never carried a value.**

## C.7 T10's §18 admissibility gate does not gate, and its isomorphism suppression compares the wrong pairs

`cdsfl_topology_formal.md:406-412` specifies an admissibility gate at immune-pipeline ingress and pairwise isomorphism suppression `∀ (f_i, f_j) ∈ B.entries`, concluding at `:426` that *"§18 non-compliant findings do not reach CONFIRMED status"*. The divergence pass runs at `reference_runner_v2.py:9515-9565`, after registration (`:8854`) and after `_update_finding_statuses` (`:8917`), and its own comment at `:9496` reads *"Logging-only — does not gate admission or R_k."* **[recomputed]** `eta_int_modulator`, the function T10 assigns the four compliance tiers to, has **no call site** outside `bench/verify_round2_implementation.py` (a standalone checker) and tests; `:7596` passes the literal `m_div=1.0`.

The comparison scope is also wrong. `bench/dm/_divergence.py` compares primary-versus-alternative (`score_isomorphism`, `:329`) and sibling-versus-sibling (`:564-615`) — never blackboard entry against blackboard entry. The brief notes this at §1.13 and §4.11; the addition here is that the modulator has no consumer at all, so the whole apparatus is disconnected rather than merely mis-scoped.

## C.8 §16's mandatory NOVELTY block is never parsed

`cdsfl_operational.md:658-668` makes the per-finding NOVELTY block mandatory for Stage-6 runs, carrying ν_k with rationale, c_ext with sources, H/H_max and citations; the runner demands it at `:8495-8501`, marked *"(MANDATORY, Stage 6 §16)"*. **[recomputed]** grep for NOVELTY across `bench/runner_core.py` and `bench/dm/` returns only `bench/dm/_feedback.py:587`, where the token is a **section-boundary terminator** in a regex — a delimiter, not an extractor. The ν_k that reaches `compute_rk_with_eta_channel` comes from `nu_k_by_finding`, supplied by the ouroboros cell (`:9103`), not from anything the model reported. See F.5 for what that value actually is.

## C.9 The two specs disagree on the status set, and the novelty filter arbitrates

`cdsfl_topology_formal.md:59` fixes `Status ∈ {OPEN, CONFIRMED, CONTESTED, MERGED, UNCONFIRMED}` and `:91` requires every finding to end CONFIRMED, MERGED or UNCONFIRMED. `cdsfl_operational.md:299-309` adds CLOSED, REOPENED and DUPLICATE; the implementation adds REFUTED (`:1469`). No directive reconciles them, so `_NON_NOVEL_TERMINAL_STATUSES` (`:4134-4136`) makes a call T2 never authorised: MERGED, DUPLICATE, UNCONFIRMED and REFUTED are stripped from the γ and `g_3` input, while **CLOSED counts as novel**. That is a defensible reading — a CLOSED finding is a verified real discovery — but it is the implementation deciding. **[recomputed]** CLOSED is the dominant end state at 721 of 2030, and it is precisely the one T2 omits, so on T2's terms every archived run ended in a state the FSM does not admit.

## C.10 A model citing a canonical id inside a finding block spawns a fresh canonical entry whose alias contains the id it echoes

The prompt instructs *"Reference findings by CANONICAL ID (C0001, C0002, ...)"* at `:5069`. When that reference lands inside a FINDING block rather than a verdict line, the parser prefixes it (`runner_core.py:916`) to `Gemini_C0016`, the alias key becomes `Gemini:Gemini_C0016`, no match is found, and a new canonical entry is registered and counted as novel. `runner_core.py:908-914` already drops a *pure* verdict line parsed as a finding; nothing catches the mixed case.

**[recomputed]** Across the 27 registries, **195 entries carry a `source_alias` whose trailing token is an existing canonical id in the same registry, and 132 of those (67.7%) were counted as novel.** Worst affected: exp37 29/222, exp41 25/79, exp40_gate 23/296, exp44 22/82, exp38 19/169, exp42-lk 13/52. Honest bound: median lexical similarity between the echo and the entry it names is low, so most are not verbatim re-files and some are verdict or review prose mis-parsed as findings — a parser-boundary problem as much as a dedup one. Either way, **the runner is holding the canonical id of the entry being echoed and never tests it**, while `_resolve_merge_source` already performs exactly that membership test at `:1543` for verdicts. An internal sweep quoted 238 across 19 runs; my clean-scope recount is 195 across 27.

---

# D. PRE-EXP-40 HISTORY

## D.1 Tier 0 has never changed

Exact `(model_id, finding_id)` match is not a runner-v2 invention. It is byte-for-byte the same construct in every runner the project has shipped: `bench/run_exp33_endocrine.py:240-262`, `run_exp34_endocrine.py:241`, `run_exp35_policy_engine.py:264`, `run_exp36_evidence.py:273-295`, `run_exp37_evidence.py:289`, `bench/reference_runner.py:329`, `reference_runner_v2.py:1050-1100`. The call sites share the same two-branch new-or-CONFIRM shape (`run_exp36_evidence.py:2971-2981`, `reference_runner_v2.py:8852`).

Nothing about the pre-location-keying era was different **at the point where identity is decided**. The similarity machinery of that era — NK cell, ConvergenceDetector, Dedup Assessor — sat downstream of registration and could only reject or annotate, never merge two entries into one.

## D.2 No two findings have ever been merged into one canonical entry, in any run, in the whole archive

**[recomputed]** In every archived registry carrying an `alias_map`, `len(alias_map) == len(entries)` and the maximum number of aliases pointing at any one canonical id is **1**. The alias map is a bijection in every run from exp33 to exp53. `source_aliases` is initialised to a single-element list at every `register()` site and no code path ever appends to it (writers: `reference_runner_v2.py:1057`, `run_exp33_endocrine.py:250`, `run_exp34_endocrine.py:246`, `run_exp35_policy_engine.py:264`, `run_exp36_evidence.py:283`, `run_exp37_evidence.py:289`, `reference_runner.py:329`, `reprocess_exp33.py:71` — all the literal `[finding.finding_id]` initialiser; sole reader `reference_runner_v2.py:7589`).

**The formal spec's "post-alias-resolution" input series has never existed at any point in the project's history**, not merely since runner v2.

## D.3 The merge rate collapsed by an order of magnitude at the era boundary, and nobody recorded it

See the table at A.9. Roughly two entries in five merged in Exp 36; roughly one per run merges now. The panel is being asked to improve duplicate detection on a system whose only surviving merge channel is near-dormant.

## D.4 The Dedup Assessor's outcome measurement exists, and it is worse than "unmeasured"

The brief says at §3.5 that the LLM adjudicator *"was dropped without a recorded outcome measurement"*. The measurement is recoverable from `bench/logs/exp37_live.log`.

**[recomputed]** Exp 37 ran **35 adjudications: 19 DUPLICATE, 16 NOVEL — a 54.3% duplicate rate**. Sixteen were applied. All sixteen merged entries were critical-severity (0.83-1.00) and every merge confidence was 0.88-0.98, i.e. above the 0.85 short-circuit at `bench/cc2_manager.py:937-943`, so **CC2v verification never ran on a single one of them**. One of the three unapplied was blocked only because the model named a target id that does not exist in the run (C0191 → C1002; the registry runs C0001-C0222). And Exp 37's registry records 16 MERGED entries with **zero model-cast MERGE verdicts**, so all sixteen came from the assessor.

The honest characterisation: a single Haiku call, unreviewed, terminally resolved sixteen criticals, and its observed failure modes in that one run were a hallucinated target and a self-merge (A.6). Anyone proposing to restore an LLM adjudicator is proposing to restore this, and should say what they would measure differently.

## D.5 Exp 33 lost 83% of its findings and all 47 of its model-cast MERGE verdicts to the parser

The live run recorded 84 findings, 32 registry entries, CONFIRM-only verdicts and every entry left OPEN. Offline reprocessing of the same raw responses (`bench/reprocess_exp33.py`) recovered **499 findings — the live run parsed 16.8% of what the models produced — and 47 MERGE, 82 CHALLENGE and 43 EXTEND verdicts the live run never saw** (`bench/logs/exp33_endocrine_20260405T110345Z/reprocessed_report.json`: `delta_findings 415`, `verdict_totals {CONFIRM 282, CHALLENGE 82, EXTEND 43, MERGE 47}`, `registry_final_state {OPEN 499}`, `gamma_final 0.1548`).

The earliest MERGE-verdict channel existed in the prompts and produced output; the runner discarded it wholesale. The reprocessed report sits beside the original and no note supersedes the live figures.

## D.6 The only cross-model duplicate ground truth this project has ever had is an Exp 30 artefact nobody uses

`bench/logs/exp30_deduped_bugs.json` clusters 316 findings into 83 bugs — a 3.8:1 collapse — each cluster carrying its contributing models, rounds, max severity, description and selected fix. **[recomputed]** 51 clusters are multi-finding, **39 span two or more models**, sizes reach 23, 21 and 16, 46 clusters are critical-severity, 45 carry a code fix.

It is the only artefact anywhere in the archive recording which findings *from different models* are the same defect, and it was adjudicated by humans and agents during the Exp 30 fix application rather than by any similarity function. Its sole consumer is `bench/run_exp31.py:782-807`, which reads it to tell models what was already fixed. No clustering script for it exists in the repository, so its provenance and error rate cannot be reconstructed from the code. It appears nowhere in the brief.

**If a labelled cross-model dedup set is wanted, this is 39 multi-model clusters already sitting on disk** — subject to establishing how it was produced, which needs the commit `47c62b3` session record or the founder.

## D.7 The round-robin bench runner had genuine cross-model, cross-round deduplication, and it was never carried forward

`bench/run_round_robin.py:300-321` keys defect identity on `_defect_key(task_id, constraint_class, claim, finding)`, which prefers `structural_canon_hash(finding)` — the 4-tuple `(artifact, assumption, violation_mode, witness)` canonicalisation — and falls back to a hash of the normalised claim only when the structural fields are empty. `:3248-3280` deduplicates **within a round across models** (*"the same HARD claim found by both models counts once"*, `:3255-3259`) and then computes novelty by set difference against all previously seen keys (`:3277`).

**This is the only cross-model deduplication this project has ever run in production**, and it is materially what the brief's §4.1 unanimous panel recommendation — structured value emission — asks to build. It was never carried into `reference_runner.py` or `reference_runner_v2.py`. It ran at scale: `bench/results/round_robin_phase2/decay_analysis.json` covers 78 runs across four conditions.

It also inherits the one canonicalisation defect the project has already proven with an executed falsifier — alphabetical intra-field token sorting (`bench/cdsfl_registry/refinements.py:130`), which collapses non-commutative claims. The brief covers that defect at §3.7. What the brief does not say is that the mechanism carrying it is also the best cross-model dedup the project has built.

## D.8 The similarity function is saturated on this project's own data, and the archive dates the discontinuity to the minute

**[recomputed]** With `sentence-transformers` 2.4.0 live and all-MiniLM-L6-v2 loading, running `ConvergenceDetector._compute_equivalence_classes` over archived registry descriptions at the shipped `tau_sim_embed = 0.55` produces **one class per run**: exp36 216 → 1, exp41 79 → 1, exp44 79 → 1, exp49 38 → 1. A threshold sweep finds no usable plateau (exp36: 1 class at 0.60, 6 at 0.70, 37 at 0.75, 161 at 0.80, 216 singletons at 0.90). The lexical backend at its own default is the opposite failure: 192 classes with 182 singletons. Removing entries whose descriptions are parser-substituted schema headers changes nothing, so the collapse is not a truncation artefact.

The artefact that records it is `final_kappa` in `completion_signal.json`. **[recomputed]** It is varied and informative-looking for all **20 runs from Exp 29 to Exp 41** (0.0 to 0.8944 — exp36 0.8002, exp41 0.1348) and then **exactly 1.0000 for all 12 runs from exp41c onward, without exception**: exp41c, exp42 ×4, exp43, exp44, exp45, exp46, exp47, exp48, exp49.

The commit that did it is `0901fd5`, *"convergence-detector fixes + 5-model confer verification (founder-directed)"*, **2026-05-22 20:11:18 +0100**. `exp41_convergence` started 02:10Z that morning and reads 0.1348. `exp41c_first_principles` started 19:48:36Z = 20:48 BST — **37 minutes after the commit** — and reads 1.0000. Every run since is 1.0000.

The fix was correct in direction and moved the threshold from far below the noise floor to just inside it. It converted under-merging into total collapse: a run with one cumulative equivalence class has no novel classes, so κ_set is identically 1 and the severity veto can never fire. **A five-model confer-verified fix saturated the metric it repaired, and because `reference_runner_v2.py` never reads kappa (`grep -c` = 0), nothing noticed for three months.** `DetectorHealthMonitor` (`bench/dm/_immune.py:218-244`) exists to alarm on precisely this and is dormant with the rest of `dm/`.

Related and unfixed: the NK cell's `tau_sim = 0.50` was calibrated on 2026-04-06 against the formula `0.3 + 0.7·J` (commit `e293fca`), under which 0.50 does require J ≥ 0.2857 — the code comment's arithmetic was right when written. On 2026-04-12 commit `0dc6ab7` replaced that with `0.8·content + 0.2·b_class` **and** made embedding cosine the default content term, under the same import name. The NK threshold was not touched and its comment was not updated. It is stale at HEAD in three places (`bench/immune_agents.py:3075-3077`, `:4317-4319`, `:5576-5578`). The `effective_tau_sim` commit message treated the hardcoded 0.50 as a safe harbour — *"Live experiments unaffected — immune pipeline already hardcoded 0.50"* — which is exactly why it went unfixed. Section E.4 measures what it does.

## D.9 Exp 36's "17:1 dedup ratio" is a mislabel

The record's headline numbers are real: 452 raw findings against 153 canonical entries at R22, rising to 701 raw and 217 canonical by the R45 close, against roughly nine actual bugs. But **[recomputed]** the collapse from raw to canonical is produced entirely by the exact-id branch at the registration site (`bench/run_exp36_evidence.py:2971-2981`): a model resubmitting its own `F007` is recorded as a CONFIRM on the existing entry. No similarity function participated. The note's own sentence *"the dedup engine failed to collapse them"* is correct but understated — **the dedup engine was never on that path**, and is not on it today. Any inference from 17:1 about how well semantic dedup performed in that era is unsupported. (Note claims: `Exp36_Ground_Truth_Reference_2026-04-08.md:89-91`, `:246`, `:258`; `Exp36_Design_Analysis_2026-04-07.md:41`, which names the NK cell as the dedup engine.)

The "roughly nine actual bugs" figure is itself an unverified note claim; verifying it means adjudicating 217 entries.

## D.10 The last natural convergences were state-based and pre-date the γ gate

**[recomputed]** Exp 29 converged at R8 on `kappa_converged(0.960)`; Exp 36 at R45 and Exp 37 at R15 on STATE_CONVERGED. From the γ-alt gate onward (commit `834e65c`, 2026-04-17) convergence became unreachable: exp38, both exp39_0_gate runs, exp40_gate, exp40_slice_admissibility_hardened, exp40_slice_records and exp41 all record `converged_at: null`. Exp 40's main gate run went 29 rounds and 417 findings; Exp 41 went 12 rounds with gamma_crit pinned at 0.0.

`experimental_notes/Exp41_Convergence_Investigation_2026-05-22.md:58-62` isolates the cause as a panel producing critical-severity findings at a flat rate — 24 settled criticals on a bounded 438-line module — feeding a rate gate that only passes if discovery decelerates. This is Exp 36's churn seen through a different instrument: Exp 36's gate could not see the churn, Exp 40/41's gate could see nothing but the churn. That is the shape of the problem location keying was built to solve.

---

# E. WHAT THE SCHEMA WAS BUILT TO DO ABOUT NOVELTY, AND WHERE IT HAS DIVERGED

## E.1 The founder's claim is measurable, not impressionistic

**[recomputed]** Of the 920 lines of `cdsfl_operational.md` from the first heading onward, **336 (36.5%) sit in four sections whose subject is recognising repeats**: §8 Discovery Efficiency and Depletion (76 lines, `:344-419`), §13 Per-Round Operational Data (17, `:482-498`), §16 Stage 6 Literature-Calibrated Extension (103, `:602-704`), §18 Divergence Directive (140, `:793-932`). Novelty is additionally load-bearing inside §2 (the mandatory NOVELTY block), §3 (η as one of three factors of q), §6 (η estimation — *"Check the registry"*), §7.1 (the lifecycle exists to stop rediscovery), §15 (q_retest requires η from similarity) and §17 (NEAR-DUPLICATE is one of four action-precedence classes). Twelve of eighteen numbered sections carry novelty content; only §1, §4, §5, §11, §12 and §14 carry none.

## E.2 The convergence apparatus is a novelty detector with a stopping rule attached

Round 0 is dispatched with no registry summary at all (`:8693`), so round-0 findings are an independent baseline and "novel" thereafter means "novel relative to what you were shown". Four of the five primary gate conditions (`:3605-3668`) are novelty-derived: ρ churn, `novel_this_round > max_novel`, the γ gate, and open critical/high stability. Only the contested count is not. γ is a per-round quantity by construction — log-log regression of cumulative novel count against round number — so the round *is* the unit of the decay curve.

## E.3 Where intent and behaviour have diverged

**The registry summary carries its novelty purpose in a comment and three renderings work against it.** `build_summary` states at `:1285-1289` that the header exists so models *"understand which findings are still in play... Without this, models would rediscover and re-describe canonical entries indefinitely"*, and instructs *"do not re-describe"* at `:1332` and `:1384-1388`. It is the only instrument the panel has for the η judgement §6 demands. Active findings show `description[:120]` (`:1355`), overflow and settled show `[:80]` (`:1379`, `:1395`), only the top 20 by severity get full detail (`:1272`), and REFUTED and DUPLICATE entries are hidden entirely (`:1280`, `:1398-1399`) — so a claim another model already got refuted is invisible to the rest of the panel. The 500-character stored cap the brief flags at §1.15 was raised to 2000 at commit `f53c276` (2026-08-17); that commit records the cap having clipped 661 of 2247 archived descriptions.

**Severity decides which novelty the gate can see, and it is self-reported.** The two-sided gate counts criticals only (≥ 0.70, `:4024`, `:4304`), and severity is a number the model writes and the runner stores verbatim (`:1058`). `_apply_severity_calibration` (`:4091-4127`) is default-off **and demotion-only** — it can move an over-rated critical below the threshold and has no path to promote an under-rated one. Both asymmetries point the same way: a genuine critical filed at 0.65 is invisible to the count side, and calibration's only possible effect on convergence is to bring it forward.

**`flaw_class` is populated and wired to the cross-run novelty prior, and the read half has never fired.** The write half works — π_mem is recorded from Exp 47 onward. **[recomputed]** No config sets `immune_memory_consume_rk0`, and `rk0_source` is absent from every `sk_result` in the archive: `R_old` is the uniform 0.5 in every case. Worse, `bench/state/` at HEAD contains exactly one file, 1061 bytes, and it is `immune_memory.json` with `"experiment_count": 3`, `"source_hash": null`, and **no `experiment_ids` key at all** — so the duplicate guard at `bench/dm/_memory.py:232-238` cannot recognise a single one of its own sources. The code says so itself, in a docstring added by adversarial verification on 2026-08-12 (`:177-195`), including the measured effect: *"re-recording Exp 47 lifted flaw class 1's confirmed count from 56.90 to 92.49 with no error raised"*, and *"Backfilling `experiment_ids` into a legacy file closes the gap."* **It has not been backfilled.** `bench/exp53_configs/53_control_zero_live.json` sets `immune_memory_enabled: true` under a fixed experiment name and Exp 53 has two run directories. Also relevant: the recorder walks `registry.entries` and increments per-flaw-class counters on CONFIRMED/CLOSED (`:9968-9981`), so cross-model echoes enter the cross-experiment prior as independent evidence — and π_mem is already saturated at 0.964 and 0.972 on three runs.

**The only live model-facing anti-rediscovery instruction omits most of what it should list.** `build_prior_fix_summary` (`bench/dm/_round_context.py:30-105`) injects *"PRIOR FIXES APPLIED (N)... Do not re-surface any of the above"* into every dispatch; it is default-on (`reference_runner_v2.py:550-552`) and all 27 configs mentioning it set it true. Its status filter at `:66` admits only `CONFIRMED` and `RESOLVED`. **`RESOLVED` is a status from the round-robin runner and does not exist in the reference-runner FSM** — zero occurrences in the whole archive. `CLOSED`, the reference runner's actual terminal status, is not in the set. **[recomputed]** That omits **721 CLOSED against 500 CONFIRMED — 59.0% of all resolved findings are absent from the do-not-repeat list**. Separately, the recency filter reads `entry['round_closed']` falling back to `entry['round']` then to −1 (`:68`); **[recomputed]** **0 of 2030 archived entries carry either key**, so the guard at `:68` never excludes anything, the secondary sort key is constant, and every fix renders to the panel as having closed at round −1.

**The one round-scheduled instruction that tells models to close duplicates fires in the last three rounds, and the modern converging set never reaches it.** `build_consolidation_preamble` (`_round_context.py:108-144`) emits *"3. Close genuine duplicates with MERGE verdicts"* only when `round_idx >= max_rounds - consolidation_rounds` (`:130-133`), wired at `reference_runner_v2.py:8765-8770`, default 3. **[recomputed]** Of 19 archived Exp 40-53 runs, **9 reached the window and 10 did not** — and the entire modern converging set is in the "did not" column: exp42-lk (ran 7 of 16), exp44 (13, window opens at 13), exp45 (4), exp46 (6), exp48 (6), exp49 (7). **A run that converges early is a run in which the duplicate-closing instruction is never issued**, which is exactly the condition under which duplicate pressure is highest.

**§8.2 suspicious fast convergence is a reasoning instruction with no mechanism.** `cdsfl_operational.md:391-416` tells models that cross-model agreement is not independent corroboration when models share training priors and asks them to say so when detected. No code detects or scores it. The nearest structural analogue is the CONFIRMED transition, which does enforce independence (`:1960-1970`) — but that guards against self-confirmation, not correlated priors. Two of the five panel seats share a model identifier (`docs/ARCHITECTURE.md:35`), which is the condition §8.2 describes and nothing measures.

**`docs/ARCHITECTURE.md:308` drops η from the equation it summarises** — *"Each model computes q = d_ik · p_ik per round... then R_k(i) = R_det · (1 − ν_k) + ν_k"* — against `cdsfl_operational.md:114`'s `q = η · d · p`, and reuses ν for the re-injection term when the directive's §9 note at `:434-440` explicitly warns *"Do not conflate them"*. In one sentence the canonical architecture document omits the novelty factor from the detection term and reuses the novelty symbol for the re-injection term. This is the document a new reader is pointed at after the glossary.

## E.4 CORRECTION TO THE BRIEF §1.9: the NK duplicate flag does not merely report — it empties the immune pipeline

The brief states at `:111` that in runner v2 the NK cell *"cannot change the registry... Its one behavioural effect is the feedback channel (§1.10)"* and at `:130` that it *"decides indirectly — on model behaviour, not on state."* The first half is right: it cannot change the **registry**. The second is wrong about the pipeline.

`helper_t_v2` converts `is_duplicate` into a terminal verdict at `bench/immune_agents.py:4550-4554` (`# Auto-reject duplicates` → `final_verdicts[fid] = "DUPLICATE"`), and the response builder at `:5948` admits only `("CONFIRMED", "UNCERTAIN", "UNSCORED")` into `filtered` and everything else goes to `rejected` at `:5953`. `observation_only` is never passed by the runner (`reference_runner_v2.py:9017` calls `brain.run_immune_pipeline(findings)` with one argument; the default is `False`), so the filter is live.

**[recomputed]** Across the seven modern runs plus both exp53 directories, **37 of 44 archived immune rounds record `rejection_rate = 1.0` with `filtered_findings = []`**. Round 0 passes 1-3 findings; **every round from 1 onward, in every run, passes zero**:

```
exp44  r0 0.727/3 filtered, then r1-r11 all 1.0 / 0 filtered
exp45  r0 0.818/2, r1-r2 1.0/0
exp46  r0 0.875/1, r1-r4 1.0/0
exp47  r5-r12 all 1.0/0
exp48  r0 0.926/2, r1-r4 1.0/0
exp49  r0 0.926/2, r1-r5 1.0/0
exp53  r0 0.818/2 and 0.889/1, then 1.0/0
```

Three consequences the brief does not carry:

1. **Real tool verdicts are computed and discarded.** The specialist cells run in parallel on the original triaged list while NK v2 works on a deep copy (`immune_agents.py:5690-5693`, the MF-20 race fix), and the flags are adopted afterwards at `:5845-5846`. So the tools do run and their output is overwritten at synthesis. In exp49, 38 of 40 findings ended DUPLICATE while carrying non-NK tool verdicts; exp48 recorded a `stoichiometric_balance` REJECTED at confidence 0.9 on a finding filed as DUPLICATE.
2. **The programmatic fix-verification channel has been starved since Exp 44.** `fix_candidates = [f for f in filtered if f.proposed_fix.strip()]` (`:5981`) feeds `evaluate_fixes` at `:5984-5988`, the mechanism that sets `finding.verified = True` and drives the bug-closed gate. With `filtered` empty from round 1, it has had nothing to evaluate. The high `verified` counts in the reports (exp44 65/82, exp47 64/70, exp49 33/38) come from a different path: `reference_runner_v2.py:9058-9062` reads `f.verified`, which `bench/runner_core.py:513-517` parses from the **model's own `VERIFIED: TRUE` field**.
3. **The autoimmune brake carries a carve-out that exempts exactly this.** `regulatory_t_v2` at `immune_agents.py:4711-4726`: when the removal rate exceeds `max_rejection_rate` (0.65) **and** `rejected == 0`, it logs `depletion_high_duplicate_rate` and, in its own comment, *"intentionally NOT appending to `reasons`"* — because *"All removals are duplicates — depletion, not autoimmune."* The design intent is sound. But DUPLICATE is not REJECTED, so a round in which the similarity function rejects **everything** cannot raise the flag, and the archive shows exactly that: exp44 rounds 1-2 and 4-9, exp47 rounds 5-11, exp49 rounds 1-5 all sit at rejection_rate 1.0 with `autoimmune_flag = False`.

This does not overturn the brief's central point — none of it reaches the registry, and archive-wide registry DUPLICATE status remains 0. It changes what the 90-95% DUPLICATE rate at §1.9 *means*: it is not an unused measurement, it is the reason the immune pipeline currently verifies nothing.

## E.5 §17 NEAR-DUPLICATE is the one content-based novelty signal that reaches the panel, and it works

`cdsfl_operational.md:739-744` routes the pipeline's duplicate flags into the next round's prompt as an imperative — demonstrate distinctness or withdraw. `bench/dm/_feedback.py:295-302` ingests and `:468-477` renders `NEAR-DUPLICATE: cosine X to Y`; `reference_runner_v2.py:5699-5724` builds the pairs. It is live, it is cross-model, and rendered-line counts are substantial (Exp 40 263, Exp 43 121, Exp 42 107, Exp 44 79, Exp 47 77). This is the schema's novelty design working as written, with one boundary the brief already states at §1.10: it changes what a model is told, never what any counter counts. Whether models actually withdraw when flagged is unmeasured and is the cheapest remaining test in this addendum.

---

# F. OUROBOROS AND NEAR-DUPLICATE DOCUMENTS — A DIFFERENT PROBLEM

## F.1 The distinction, stated precisely

Everything in the brief concerns **finding-pair identity**: given two paragraphs of prose written by models about one target artefact, decide whether they name the same defect. The population is small (165 criticals archive-wide, 13,530 pairs, computed exactly in 15 ms), the signatures are sparse (median 4 hard tokens), sameness is a **causal** question about defects, and there is no external identifier.

The ouroboros path poses a different question: **document identity**. Given two retrieval records, decide whether they are the same published work. That population is bibliographic. It has stable external identifiers (DOI, arXiv id, PMID), titles and author lists, canonical metadata, and sameness is a **referential** question with a ground truth that exists outside the system. Its failure modes are version drift (v1 vs v2), venue drift (preprint vs publisher HTML), and index overlap between databases that mirror each other.

**The MinHash/LSH refutation in brief §2.3 does not transfer, and neither do the embedding refutations in §2.2.** Both were measured on finding pairs and both were killed by properties specific to that population:

- **Scale.** §2.3's reopening condition is explicit — the argument becomes real past roughly 2000 items in one comparison set. That threshold was correct for findings. It is also correct here and equally unmet: **[recomputed]** the entire archive holds **145 paper records**. Neither method is needed at this scale, but that is a *shared* conclusion, not a transferred one.
- **Sparsity.** §2.3 killed MinHash on this project's data because the signatures have a median of 4 tokens, so Jaccard takes only a few discrete values and the 1/√k error scaling plateaus. **Paper records are not sparse** — titles, authors and abstracts run to hundreds of tokens. The specific measurement that killed MinHash does not apply to this population.
- **Semantics.** §2.4 refuted the paraphrase argument by showing `stem_signature` extracts numbers and identifiers, which have no synonyms. Titles do have synonyms and translations and truncations. The refutation's own mechanism does not carry over.
- **Ground truth.** For findings, sameness is unresolvable without counterfactual repair (brief §6.2). For documents, a DOI settles it.

**The correct statement is: the finding-pair conclusions are sound and out of scope for the document path, and the document path has never been measured at all.** Anyone reasoning "MinHash was refuted here, therefore we need nothing for papers" is transferring a result across a population boundary the measurements do not cross.

## F.2 What the paper path actually does about identity

Exact hash, at document level — tier 0 again. `build_brief_prompt_section` deduplicates admitted briefs on `key = rec.get("source_hash") or rec.get("source_ref") or rec.get("title")` (`bench/ouroboros_cell.py:1648`, `seen` set at `:1636`), where `source_hash` is a SHA-256 of the **full extracted text** (`:1442-1443`). Two renderings of one work hash differently and both are admitted. There is no title normalisation and no DOI normalisation on this path (`_normalise_doi` exists at `:1142` and is used only for Unpaywall lookup). The comment at `:1632-1635` records the defect being caught in the first live proof run — *"the block listed one arXiv paper twice as [1] and [2]"*.

**There is no cross-round retrieval memory at all.** `run_between_rounds` builds a fresh `OuroborosShadowLog` per call (`:749`, `:769`) and appends to `self._round_logs` (`:743`, `:780`, `:821`); nothing reads prior rounds' papers, and the caller passes only the current round's briefs (`reference_runner_v2.py:6095-6096`).

**[recomputed]** Across all 82 archived `ouroboros_shadow_r*.json` files: **145 paper records retrieved, 100 distinct titles per run — 45 (31.0%) are repeat retrievals within the same run.** Worst affected is exp47 at 42 records against 22 distinct titles (47.6% repeats), with *"supersymmetry anomalies in new minimal supergravity"* retrieved in **8 rounds of 14** and *"a typology of data anomalies"* in 5. exp46, exp48 and exp49 each show 21 records against 16 distinct.

Cross-source duplication is latent rather than observed: no archived round returned the same title from two different sources. But nothing in `_fetch_metadata` (`:941-1006`) or the `_query_arxiv` / `_query_semantic_scholar` / `_query_openalex` trio (`:1010`, `:1032`, `:1094`) would detect it if they did, and Semantic Scholar and OpenAlex both index arXiv.

Two `_ouroboros` config keys are read by nothing in all 13 configs carrying the block: `max_papers_per_round` and `contact_email`. `grep -rn max_papers_per_round bench/ --include='*.py'` returns nothing, and the constructor call at `reference_runner_v2.py:6051-6062` passes only `shadow`, `allowed_sources` and `reader_backend`. `max_papers_per_round` is the retrieval-volume cap — the one knob that would bound duplicate retrieval. Unpaywall consequently goes out under the placeholder default `cdsfl-ouroboros@constraint-engineering.local` (`ouroboros_cell.py:718`).

## F.3 c_ext treats three overlapping bibliographic databases as independent

`bench/dm/_shadow_stage6.py:340-346` computes `c_ext_raw = 1 - Π(1 - c_s)` — a noisy-OR, i.e. exactly the independence assumption — then applies one flat global discount `GAMMA_SRC = 0.7` (`:228`, labelled "calibration target"). `_track_source_cooccurrence` (`:638-686`) exists precisely to replace it; its docstring says *"post-experiment estimation of pairwise source correlation, which could replace the global gamma_src discount with per-pair weights."* **[recomputed]** `grep -rn source_cooccurrence bench/ --include='*.py'` returns exactly one hit outside the defining file, in `bench/tests/test_generic_location_bucket.py:387`, a name-presence assertion. `GAMMA_SRC` appears nowhere outside its own module and test.

The appendix's §0.1 Branch 2 ψ_ij machinery is the principled home for correlated detection and is not connected to it — the same disconnection as B.8, in a second place.

Two narrower defects in the same function: `_estimate_source_coverage` (`:436-473`) keys on `meta.get("source")`, the *requested* source, while `_fetch_metadata:975-982` records the actual fallback chain in a different field, `fetched_via` — so an arXiv query answered by OpenAlex is scored with arXiv's `DEFAULT_SOURCE_RECALL` of 0.4 (`:220`). And `seen_sources` at `:442-448` keeps only the first query per source name, so with the runner's default two sources and three queries per round, the third query's results never enter coverage.

## F.4 ν_k, the literature-novelty term, is a round-level constant

`_estimate_retrieval_sparsity(self, finding, o1_metadata)` is declared with a `finding` argument at `bench/dm/_shadow_stage6.py:477-479` and **its body never references it** (`:490-505`): the value is a four-step ladder on `total_results = sum(m.get("results_count", 0) for m in o1_metadata)`. Every finding in a round receives the identical ν_k, and the identical c_ext, which is computed once per round at `:338-346`.

**[recomputed]** Across every `stage6_calibration_r*.json` in `bench/logs/` — **26 runs, 202 rounds, 1726 per-finding rows — the number of rounds in which `nu_k_proxy` or `c_ext` varies within the round is zero.** Round values land exactly on the ladder: ν_k ∈ {0.2, 0.4, 0.5, 0.8}, c_ext ∈ {0.0, 0.28, 0.35, 0.448, 0.49}.

The runner's own comment at `reference_runner_v2.py:6166-6169` asserts the opposite — *"c_ext is a property of the SEARCH... nu_k IS per-finding, so it is carried per finding_id"* — and `_w["nu_k_by_finding"]` at `:6192-6194` is a dict every value of which is the same number.

**In the project's favour:** the function's own docstring is honest and explicit — *"WARNING: This is NOT a novelty measurement. It conflates at least four quantities: search volume, query breadth, field publication density, and actual novelty... The field name 'nu_k_proxy' is retained for data compatibility but this proxy measures retrieval sparsity only. Production nu_k requires embedding-based semantic similarity."* The gap is that the runner comment and the directive do not carry that warning forward.

## F.5 The causal loop nobody has connected: duplicate detection starves the literature cell of targets

`_select_targets` (`bench/ouroboros_cell.py:825-868`) derives finding-level targets only from `final_verdicts` entries equal to `"UNCERTAIN"` (`:857-864`). Section E.4 shows those verdicts are ~100% DUPLICATE from round 1 onward. The remaining source is the macrophage anomaly label the runner synthesises at `reference_runner_v2.py:6070-6072`: `f"round_{round_idx}_anomalies:{last['anomaly_count']}"`.

**[recomputed]** Classifying all 58 archived queries: **44 (75.9%) target `round_N_anomalies` labels and 14 target `uncertain_finding:`** — and in each modern run exactly one finding-derived target appears, always round 0, the only round with a non-empty `filtered`. There are 29 distinct query strings across the archive and the most frequent are *"round 0 anomalies"*, *"round 1 anomalies"*, *"round 2 anomalies"*.

The worked case, verbatim from `bench/logs/exp46_stage6_locationkey_live_20260728T103151Z/ouroboros_shadow_r02.json`: target `round_2_anomalies:2`, source arxiv, query `"round 2 anomalies"`, status live, 3 results, the first being *"ALOHA 2: An Enhanced Low-Cost Hardware for Bimanual Teleoperation"*. The target under review that round was `bench/dm/_shadow_stage6.py`.

**The literature-novelty channel §16 introduced specifically to catch rediscovery of published work — citing Hossenfelder (2026) on the Erdős-problem rediscoveries at `cdsfl_operational.md:608-612` — is being fed by a search whose query is a round number, because the duplicate detector consumed its only real input.** That is one causal chain running from a saturated similarity threshold, through the immune pipeline, into the external-novelty apparatus.

## F.6 Scope note: none of this has reached a model prompt or an R_k

Neither `inject_brief` nor `c_ext_enabled` is set by any config in the repository, so no retrieved paper has entered a panel prompt and no c_ext has reached R_k. **[recomputed]** `sk_result.c_ext` and `sk_result.nu_k` are absent from every archived entry, and they are written only when `c_ext > 0.0` (`reference_runner_v2.py:7602`) — the channel has never carried a non-zero value in a completed run.

Everything in Section F is therefore armed but not consuming, two boolean flags away, in configs that already carry the block. That is the right time to fix it: **a document-identity rule needs a DOI/arXiv-id normalisation and a cross-round retrieval cache, and both are cheap, deterministic and untouched by anything the brief refutes.**

---

# G. WHAT THE REFUTATION PASS KILLED, AND WHERE THE RECORD DISAGREES

Recorded so it is not inherited.

1. **REFUTED and withdrawn:** the claim that γ's input satisfies T5's post-deduplication constraint "in the strong form", filed as WORKS_AS_INTENDED by two independent sweeps and carrying the instruction *"it should not be disturbed by any repair to the items above"*. See C.1. The exp44 byte-identical triplicate refutes it directly, and the instruction pointed a reader away from the item that most needs fixing.

2. **RE-SCOPED:** the MERGE → CONFIRM recast is **mandated by the spec** (`cdsfl_topology_formal.md:126-127`) as the undefined-source fallback. The defect is the alias-key format making the fallback universal, not the fallback existing. The repair target is `_resolve_merge_source`, not the caller.

3. **DE-PRIORITISED:** the η corroboration/redundancy fork (B.8) and the missing Stage 4→5 derivation. Both concern a channel `model_params` has never populated. Wire η, then measure.

4. **SCOPED:** "every cross-model set operation is degenerate under the implemented identity" is true of the reference runner and false of `run_round_robin.py` (D.7). Stated unscoped it reads as a model-level impossibility when it is a runner-level regression.

5. **Scope reconciliation, not disagreement:** archive totals of 2030 / 2247 / 2315 entries and 201 / 287 / 210 MERGED all appear in the internal record. They differ by whether `exp36_evidence_latest` (a byte-duplicate directory) and `runner_state.json`-only runs are included. Every number in this addendum uses the 27-run / 2030-entry scope.

6. **Numeric corrections made here:** exp47's location-keyed critical total is **12**, not 11. Canonical-id echo entries are **195 across 27 runs** on this scope, not 238 across 19. CLOSED omitted from the prior-fix list is **59.0%**, not 61.6%. The `g_3` gate check is at `:3644`, not `:3729`. The exp42 γ spread of 0.0798 is about 80% of the narrowest `GAMMA_BANDS` interval, not wider than it. One sweep reported reconstruction drift in exp44's γ at rounds 7-8; my full-series recompute reproduces the recorded `gamma_critical_history` exactly at every index in all seven runs tested, so the drift was in that sweep's method.

---

# H. OPEN ITEMS

Stated as open rather than smoothed. Each would change or sharpen something above.

1. **No live replay.** Every behavioural claim was produced by executing the real functions against a five-model `RunnerConfig` or by replaying archived registries. The archives corroborate all of them except the phantom merge target, which has zero archived occurrences and is reported as latent on that basis.

2. **Whether any of the 201 merges was substantively correct is unanswerable from the archive**, because `:8909` overwrites the model's evidence. Not "unmeasured" — unrecoverable in principle without re-running.

3. **Exp 50-52 have no run archive**, and Exp 29-32 reports carry no `registry` block, so no merge or alias measurement extends earlier than Exp 33. Runs before that use different report schemas and were sampled, not mined.

4. **`exp30_deduped_bugs.json` has no clustering script in the repository.** Its 39 multi-model clusters are the project's only cross-model duplicate labels and cannot be used as ground truth until the procedure that produced them is reconstructed.

5. **The behavioural effect of §17 NEAR-DUPLICATE is unmeasured.** Delivery is confirmed at volume; whether flagged models withdraw, re-argue distinctness, or ignore the flag has not been read out of the next round's responses. This is the cheapest open test here.

6. **The 195 canonical-id echoes are unclassified** between genuine re-files and verdict or review prose mis-parsed as findings. The split determines whether C.10 is primarily a parser fix or a dedup fix.

7. **How many criticals per round land in the unlocated bucket is unknown**, so the permutation-invariance violation at B.7 is demonstrated structurally and not sized. `convergence_location.py`'s 97.6% location coverage suggests the population is small.

8. **Ouroboros cross-source duplication is latent.** Zero archived rounds returned one title from two sources, on 145 records with one paper actually read per query (`ouroboros_cell.py:1424`). The absence of a normalisation step is structural; the incidence at scale is unmeasured.

9. **Not read end to end:** `bench/dm/_role_assignment.py`, `_load_balancer.py`, `_failure_handler.py`, `_fsm.py`, `_validation.py`, `_events.py`, `_sk_format.py`, `_directive_sections.py` (grepped for dedup and novelty vocabulary, nothing above noise), and `PAPER.md` (targeted grep only).

10. **The "roughly nine actual bugs" figure for Exp 36** is a note claim, not verified here. Verifying it means adjudicating 217 entries and is the right work if the 17:1 mislabel at D.9 bears on a decision.
