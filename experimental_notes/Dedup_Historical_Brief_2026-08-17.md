# EXP49_DEDUP — HISTORICAL BRIEF FOR THE MODEL PANEL

**Subject: duplicate / difference detection between findings in CDSFL.**
**Prepared 2026-08-17T23:23+01:00. Verified against HEAD `5354b95` (working tree clean).**

> **ADDENDUM, 2026-08-18 — read alongside this brief:** `experimental_notes/Dedup_Historical_Brief_Addendum_2026-08-18.md` (verified at HEAD `f53c276`). It covers what this brief does not: the Bugzilla state machine as a duplicate-handling design, whether the mathematical model ever grounds "same finding" (it does not, and 23 named quantities depend on it), the spec requirements the implementation violates, pre-Exp-40 history, and near-duplicate *documents* on the ouroboros path — a different population from finding pairs, where the MinHash refutation in §2.3 does not transfer.
>
> **One correction to this brief lands there:** §1.9's *"its one behavioural effect is the feedback channel"* is right about the registry and wrong about the pipeline. `helper_t_v2` converts `is_duplicate` into a terminal DUPLICATE verdict (`bench/immune_agents.py:4550-4554`) and the response builder drops it (`:5948`), so `filtered_findings` is empty in 37 of 44 archived immune rounds — which starves programmatic fix verification and the literature cell. See Addendum §E.4 and §F.5.

## How to read this

This project has been working on one question for five months: given two findings produced by different models (or the same model in different rounds) about the same target document, decide whether they name the same defect or two different defects. The answer feeds a convergence gate — get it wrong in the merge direction and a run stops while genuine defects are still arriving; get it wrong in the split direction and a run never stops.

You are being briefed because the last time this question was put to a panel, and the last time it was put to an external model, the answers included mechanisms that had already been built and measured dead. MinHash/LSH has now been proposed twice by the same source, four months apart, and killed once by measurement. Vector-embedding cosine has been proposed at least three times and is *already implemented in this codebase* and refuted on this codebase's own data. A mutation-vector method was proposed by a panel, built to that panel's design, measured at Fisher exact p = 0.71, and removed.

Every claim below carries a `file:line` or a commit hash. Where the record contradicts itself, that is said rather than smoothed. Where a number was recomputed for this brief, it is marked **[recomputed 2026-08-17]**.

Two archaeology warnings, because verification will otherwise fail:

- Commit `043a0a8` (2026-08-15, "Milestone merge") is a **squash merge with a single parent** (`f574d8c`). The entire 2026-08-04 → 08-15 dedup arc, including the FELM add (`2ce2a69`) and FELM removal (`4bdcecb`), is **not reachable from `main`**. Use `git log --all` or the `exp39-experimental` branch (107 commits ahead of main).
- Report files are named `<run_name>_report.json`, not `report.json`. `find bench/logs -name "report.json"` returns zero. Several internal sweeps cite the wrong name; the counts they quote are correct (45 `*_report.json` files, 19 for the exp4x arc, 11 for Exp 42–49).

---

# 1. WHAT DECIDES SAMENESS TODAY

There is no single similarity function. **Eight distinct mechanisms** can change whether two findings end up as one registry entry or two, or whether a finding is counted as new. Only one of them is the thing usually called "the similarity function", and it is the one that has never gated anything.

## 1.1 The default: exact identifier match (tier 0)

`bench/reference_runner_v2.py:1050-1053`, `:1109-1110`, `:8830-8853`.

A finding is new iff `(model_id, finding_id)` has not been seen. No text is compared. This produces `novelty_counts`, which is the count the state gate reads. **There is no cross-model dedup at registration**: two models describing one defect always receive two canonical IDs.

Verified example, and the cleanest single demonstration to put in front of a panel **[recomputed 2026-08-17]**: in `bench/logs/exp49_engineering_exam_live_20260729T062320Z/runner_state.json`, `C0001` (ChatGPT) and `C0011` (Codex) both accuse EN-06 of the same Euler-critical-load error (587 kN reported, ~573 kN correct). Both are CLOSED as **separate canonical entries**. `C0006`/`C0016` are the same story on EN-41's p-value. Location keying knew they shared a location; that only affects the *count*, not the registry's merge decision.

This matters against the formal spec. `bench/directives/universal/cdsfl_topology_formal.md:210-215` requires the Duane-γ input series to be "canonical novel findings (post-deduplication, post-alias-resolution)… Using raw findings inflates the series with rediscoveries **and cross-model echoes**." Cross-model echoes are exactly what the live series still carries.

## 1.2 Tier 1 — location keying. LIVE, and it is the only convergence-side rule that has ever gated.

`bench/convergence_location.py:45-77` (`target_symbols`), `:126-138` (`finding_locations`); driven from `bench/reference_runner_v2.py:4244-4295` (`_location_keyed_critical_series`), promoted into the gate at `:9270-9283`.

AST-extract the target file's function/method/class names; a critical (severity ≥ 0.7) is NEW iff it names at least one symbol no prior critical flagged. Markdown targets fall back to claim IDs matching `[A-Z]{2}-\d{2}` plus headings (`0b5b068`, 2026-07-29). Two hand-chosen constants decide what counts as a location at all: `_MIN_LEN = 4` and `_GENERIC = {main, compose, run}` (`convergence_location.py:40-41`).

Enabled in exactly **16 configs** (verified: `grep -rl '"location_keyed_convergence": *true' bench --include="*.json"` → 16). Fired as the gate in 6 completed runs.

Aggregate effect, which no note states plainly: across the 8 archived location-keyed runs, **224 critical entries collapse to 87 counted-as-new — a 61.2% merge rate**. Per run (criticals → counted): exp42 40→17, exp43 19→8, exp44 34→12, exp45 12→4, exp46 12→6, exp47 44→12, exp48 32→11, exp49 31→17.

**Its known blind spot, stated at build time and pinned by a deliberate test**: it cannot separate two genuinely different defects in the same function. It merges them by construction. That blind spot is the entire reason tiers 2 and 3 exist. Two archive cases are named: Exp 45 C0031 (severity 0.75, opened r3, converged r3) and Exp 47 C0070 (severity 0.85, opened r13, converged r13) — both arrived at a closing round with the gate tail reading `[0,0,0]` (`bench/audit_closing_window.py:1-87`).

The fraction of criticals arriving at an already-flagged location was measured at roughly 64% by one panel model and 59% by an independent recalculation. Neither is confirmed, because the runs do not record the symbol set they used. If it holds, the blind spot covers the majority of critical findings.

## 1.3 `_accusing_span` — premise exclusion, live inside tier 1

`bench/convergence_location.py:93-138`; commit `1e5de9a` (2026-08-17).

Truncates a description at a `Premises:` header before location extraction, so symbols cited as antecedents are not read as accusations. This sits *inside* `finding_locations`, which tier 1 calls at `reference_runner_v2.py:4289` — it is on the live gating path.

Deliberately narrow, and calibrated first: of 2187 archived descriptions only 122 (5.6%) carry any supporting-material header; `EVIDENCE:` is 78 of them and was measured to substantiate the same defect at the same place, so stripping it would delete real signal; `premise(s)` is 35 and is the citation case. Effect over six replays with backfilled descriptions: exp45/46/48/49 reproduce their archived close-round exactly; exp44 10→8 and exp47 11→7. **No run converged early** — truncation had been *delaying* two of them.

This is the model of how a threshold should be set in this project: measured against the archive before the code was written.

## 1.4 `_unlocated_novelty_key` — tier 2's function, live on the gate

`bench/reference_runner_v2.py:4168` (`_UNLOCATED_MERGE_THRESHOLD = 0.20`), `:4175-4241`, called from tier 1 at `:4291`.

**This corrects an anchor claim that is widely repeated.** "Tiers 2 and 3 have never gated a live run" is true of `hierarchical_novelty_convergence`. It is **not** true that no similarity threshold gates. When no AST symbol can be extracted from a critical, the fallback identity is the finding's own `stem_signature` (tier 2's function), joining an existing bucket iff Jaccard ≥ 0.20, else opening a new one; an empty signature falls back to a SHA1 of its own normalised text, never a shared constant.

It fixes a real defect: 42/288 criticals (14.6%) over 9 runs, re-measured at 50/351 (14.2%) over all 11 Exp 42–49 registries, worst case Exp 47 at 11/44 (25.0%) — every one of which had been keyed to a single shared `<generic>` bucket, so a parsing failure was silently promoted to an identity judgement.

Armed 2026-08-08. **Never exercised**: the newest live run directory is `exp53_control_zero_live_20260801T005649Z`, one week after the arming, and it has no report. Every location-keyed run in the archive predates it.

## 1.5 Routing dedup — the crudest live comparator

`bench/routing.py:76`, `:146`, `:159-161`; comparator at `bench/reference_runner_v2.py:3110-3115`; MERGED write at `:3229`.

Before an escalated critical climbs the capability ladder, it is compared against every already-CONFIRMED finding at threshold **0.85**. The comparator `_routing_similarity` is bare whitespace-split, lowercased, full-description token Jaccard — no stopwords, no stemming, no hard-token extraction. A hit writes status MERGED, which is a non-novel terminal status and therefore removes the finding from the gating series.

Enabled in 17 configs via the legacy alias `take_up_slack_enabled`. **Observed firing exactly once in the whole archive**: exp48 `C0028` → `C0002`. 0.85 raw Jaccard over multi-sentence prose is effectively unreachable. Never calibrated; the only justification anywhere is two named example pairs and two unit tests that pass the value in literally.

## 1.6 The CC2 single-model merge — no config flag, no quorum

`bench/reference_runner_v2.py:595-597` (`verification_confidence_threshold = 0.7`, batch 6, min round 6), `:6330`, `:6342-6349`.

From round ≥ 6 the six highest-severity open findings are sent to CC2, which may emit `DUPLICATE <id> OF <id> | <confidence>`. At confidence ≥ 0.7 the runner resolves the entry MERGED. **One model's stated confidence decides sameness.** No similarity function, no quorum, no tools, and no config flag — `_verification_step` is called unconditionally at `:9100`. Fired twice in the archive (one duplicate in exp44, one in exp47).

## 1.7 The model MERGE-verdict quorum — the actual producer of MERGED status

`bench/reference_runner_v2.py:1485-1496` (`_VERDICT_RE`), `:1767-1850`, `:8885-8896`.

Panel `MERGE C0001 <- F002` verdicts are grouped by parsed target. A single agreed target with ≥ 2 distinct model votes merges outright. Multiple targets with a strict plurality and ≥ 2 distinct models merges (D4). A genuine tie defers, and at `max_contested_rounds` escalates to HIL. On a panel with fewer than 2 external models, **one vote merges** with an HIL flag.

No similarity function is involved anywhere in this path. It is pure model voting, and it produced most of the archive's merges: **11 MERGED entries across the 8 location-keyed runs out of 396 registry entries (2.8%)**; 13 across all 11 Exp 42–49 reports. Full status tally over the 11: CLOSED 430, CONFIRMED 71, UNCONFIRMED 34, REFUTED 18, MERGED 13, **DUPLICATE 0**.

That zero is significant: it independently confirms that the immune pipeline's DUPLICATE verdicts never reach a registry status.

This path sits directly against the project's standing rule "findings are confirmed programmatically or by HIL, never by model vote". The rule governs *confirmation*. Merge is decided by vote.

## 1.8 G7 merge arbitration — enabled in 27 configs, never once fired

`bench/merge_arbitration.py:211-266`; wired at `bench/reference_runner_v2.py:1622-1705`, `:1803-1808`.

On the second consecutive merge defer, dispatch a single-answer query to all five panel models; ≥ 3 of 5 on one target merges, ≥ 3 of 5 KEEP_DISTINCT keeps the finding canonical, otherwise it stays deferred. Capped at 3 per round (~$1.50).

**Enabled in 27 configs** (verified: `grep -rl '"merge_arbitration_enabled": *true' bench --include="*.json"` → 27; one internal sweep says 17, another "20+"; 27 is correct). **No archived report contains an arbitration record, and `merge_defer_count` appears zero times in all 11 archived registries.** It requires ≥ 2 distinct merge targets AND ≥ 2 consecutive defers AND ≥ 2 resolvable candidates; with only 11–13 merges in the entire archive that conjunction has never been satisfied.

The null result attached to it is the most important measurement on this list for a panel. Commit `096c697` (2026-05-16), Exp 40 R24–R28 with G7 ON: it cleared **all** deadlocks including C0023's 21-round record, resolved 5/5 with zero cycles — and gamma stayed flat at ~0.05, against 0.048 with G7 OFF. **Asking models to vote on merges works perfectly and changes nothing measurable.**

## 1.9 NK Cell v2 — the immune pipeline's deduplicator, reporting only in runner v2

`bench/immune_agents.py:4314-4430` (`tau_sim = 0.50` at `:4317-4319`), intra-round comparison at `:4400-4421`; dispatched as primary at `:5746-5749`; DUPLICATE → auto-reject at `:4551-4554`. Reached from `bench/reference_runner_v2.py:8999` via `bench/insect_brain.py:1261-1312`.

Compares each new finding against all prior-round findings and against findings already accepted this round, using the sentence-embedding backend. On a hit it sets `is_duplicate`/`duplicate_of`/`similarity` and emits a DUPLICATE verdict.

**In runner v2 it cannot change the registry**: `grep -n filtered_findings bench/reference_runner_v2.py` returns nothing, and `registry.register` has already run at `:8836` before the pipeline at `:8999`. Its one behavioural effect is the feedback channel (§1.10).

**Its live operating characteristic, which nobody has written up [recomputed 2026-08-17 from `checkpoint.json`]:**

| run | findings flagged `is_duplicate` | similarity min / median / max |
|---|---|---|
| exp48 | 37 of 41 (90.2%) | 0.500 / 0.620 / 0.860 |
| exp49 | 38 of 40 (95.0%) | 0.521 / 0.607 / 0.842 |

Every round after round 0 is 100% DUPLICATE. In Exp 48 round 0, 23 of 27 findings were called intra-round duplicates of a single finding. `sentence-transformers` 2.4.0 is installed, so the embedding backend was active.

This is the strongest evidence in the repository that description-level embedding similarity is unusable on this corpus, and it is 2026-07-29 data that has never been reported. The cause is documented at `bench/dm/_similarity.py:206-231`: sentence-transformer embeddings are anisotropic; unrelated findings score ~0.48 on the blended metric, so a 0.50 cut merges nearly everything.

## 1.10 The DUPLICATE → feedback channel — the only path from any similarity function to a live model prompt

`bench/reference_runner_v2.py:5691-5724`; `bench/dm/_feedback.py:172-173`, `:185-215`, `:393`.

Each `is_duplicate` triaged finding becomes a `(fid_a, fid_b, similarity)` triple, scored `priority += 2.0 × max similarity`, and injected as an imperative into round K+1's prompt: prove distinctness or withdraw. Precedence inside a feedback record is refutation > admissibility > duplicate (`_feedback.py:139-149`). Default on.

This decides indirectly — on model behaviour, not on state. It has never suppressed the cross-round re-finds, because the flag and the novelty count are separate code paths.

## 1.11 ρ (rho) — the project's actual duplicate-rate metric. It gates, and it is described to models as something it is not.

`bench/reference_runner_v2.py:1593-1615`.

`rho = novelty_counts[-1] / raw_counts[-1]` — the alias/ID-proxy novel count over raw parsed findings. It is 1 − duplicate rate, computed with **no semantic comparison whatsoever**.

It is presented to every model in every round as "ρ (discovery efficiency / **semantic novelty rate**)" (`:8690-8693`), with messages including "⚠ HIGH REDUNDANCY … Most findings are duplicating existing registry entries" (`:8730-8737`). `rho_churn` is a failure condition of the state gate (`:3596-3600`) and sustained churn can terminate a run outright (`STALL_CONVERGED (churn)`, `:4409-4419`).

Origin: `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md:250-262` — "452 raw findings, 153 novel. 299 findings (66% of all output) were rediscoveries… rho was running at 8–25%… Gamma cannot distinguish them."

## 1.12 The gate that actually stopped the prose runs

This qualifies a reframing that circulates internally as "the similarity question does not reach the gate". Half true, and the wrong half is load-bearing.

Across all completed runs: STATE_CONVERGED closed 6, critical-quiescence closed 6, budget/stall closed 5. Both prose exams closed on **STATE_CONVERGED**, and their location-keyed critical series have no three-zero streak — `exp48 [9,0,1,0,1,0]`, `exp49 [11,3,2,1,0,0,0]` **[verified from the archived `convergence_reason` fields]**. So location keying's three-zero rule never fired on the target class the remaining arc uses.

But the state gate reads the novelty count **directly**: `bench/reference_runner_v2.py:3626` — `if novel_this_round > cfg.max_novel_findings`, with `max_novel_findings: int = 2` at `:483` and **neither exam config overriding it**. The archived reasons are exp48 "novel=1", exp49 "novel=0", exp44 "novel=2" — at the limit.

So: **tiers 2 and 3 of `convergence_location.py` do not reach the gate that stopped the prose runs. The dedup question does.** It reaches it through `novel_this_round`, through every mechanism that writes MERGED, and through ρ. A proposal that improves only the convergence-keying tier improves a path that has not fired on prose targets. A proposal that improves cross-model dedup at registration reaches the gate that has.

## 1.13 Live mechanisms that report but do not decide

- `novelty_rule_divergence` (`convergence_location.py:1072-1132`) — names findings the identity rule calls NEW that location keying would merge. **It returned `n_merged=0` on Exp 44 while a live-keyed comparison finds two.** Its `merged` list is computed against the *retired* single-bucket keying. The code names this as "this project's house failure mode, reproduced here in the safety argument itself." Also never emitted in any archived run.
- `score_isomorphism` / `near_copy_threshold = 0.98` (`bench/dm/_divergence.py:301-346`) — cross-round recidivism over *alternatives*, not findings. Its own docstring calls it "a lexical near-duplicate heuristic, not paraphrase detection".
- `isomorphism_threshold` / `sibling_isomorphism_threshold = 0.85` (`_divergence.py:223`, `:228`, `:514-543`) — decides *admissibility of alternatives*. Note the formal spec at `cdsfl_topology_formal.md:410-413` requires this test on **registry entries**; only the alternative-level version was built.
- `compute_cross_model_diversity` (`bench/dm/_diversity.py:36-90`) — template-collapse alarm at ≥ 0.85. Reached via `diversity_signal_from_round` at `reference_runner_v2.py:9542` (the inner name does not appear in the runner; grepping for it fails).
- Macrophage verdict-cluster alarm, `VERDICT_CLUSTER_THRESHOLD = 0.8` (`bench/macrophage_cell.py:126`, `:233-256`) — the existing over-merge detector. Any new rule that over-merges would show up here.
- `detect_finding_id_collisions` (`bench/dm/_feedback.py:60-107`) — observation-only by explicit contract.

## 1.14 Directive-text dedup — containment and a synonym map, already built and running

`bench/cdsfl_registry/composer.py:280-320`: `_semantically_duplicate` — "Two directives are duplicates if **Jaccard ≥ 0.85 or containment ≥ 0.95**", over `_normalise_tokens` which strips backticks and markdown, removes stopwords, **and applies a synonym table**. `compose` is imported at `reference_runner_v2.py:107` and runs every live round.

This corrects two claims made repeatedly in the internal record: that Broder containment is unbuilt, and that this project's lexical methods have no synonym handling. Both are true of the *finding* path and false of the repository. The code exists, is live, and could be lifted.

## 1.15 The input corruption still live

`bench/reference_runner_v2.py:1059` — `"description": finding.description[:500]`. Unchanged since commit `54d956e` (2026-04-17), verified present at HEAD.

**The project's own record contradicts itself here.** `bench/convergence_location.py:544-547` says of the two truncation defects "Both are now fixed". That is true of the parser (`runner_core.parse_findings`, fixed in `1e5de9a`) and **false of this one** — `git show --stat 1e5de9a` covers 40 files and does not include `reference_runner_v2.py`. `experimental_notes/Description_Truncation_Three_Fixes_2026-08-17.md:210` gets it right.

Measured impact: of 2187 archived descriptions, 661 are exactly 500 chars (this cap) and 1284 end mid-word. The CC2 verification prompt re-clips at `[:500]` (`:6271`); the routing ladder asks for `[:1200]` and can never receive more than 500. `scripts/backfill_descriptions.py` recovers the text for measurement only (531 repairs) — live runs still truncate.

---

# 2. WHAT WAS TRIED AND FAILED — THE CLOSED-DOORS LIST

Do not propose anything in this section without addressing the specific measurement that killed it.

## 2.1 FELM — Falsifier Equivalence via Local Mutation. Built to a panel's design, refuted at p = 0.71.

Built 2026-08-08 (`2ce2a69`, +724 lines, `exp39-experimental` branch only). Removed 2026-08-12 (`4bdcecb`). Retirement record retained verbatim at `bench/convergence_location.py:1136-1220`; removal enforced by `bench/tests/test_combined_identity_rule.py:203` (`test_no_felm_callable_survives`) and `:232` (the refutation text cannot be deleted).

**Design (Gemini's, panel of 2026-08-04)**: for two criticals at one location, mutate the target's AST locally, execute BOTH findings' falsifiers against the original and every mutant, compare the boolean response vectors. Hamming 0 = same defect; divergence = witness of two different defects.

**Measurement**: 351 same-location critical pairs across Exp 44–47, 16 mutants each.
- Labelled SAME (n=7): FELM diverged on **43%** (want 0%).
- Labelled DIFFERENT (n=269): FELM diverged on **52%** (want 100%).
- Fisher exact `[[3,4],[140,129]]`, odds 0.691, **p = 0.71 — no association**.
- **74 of 101 falsifiers share one identical response vector** (CONFIRMED on original and every mutant), so FELM cannot tell those 74 apart at all. Per-run distinct vectors: exp44 8/34, exp45 8/12, exp46 2/12, exp47 5/43.
- Both of the panel's own stated acceptance cases failed: exp45 C0031-vs-C0022 gave Hamming 0 at 5/12/16/40/60 mutants and at three scopes; exp47 C0070-vs-C0053 had no falsifier to execute.
- Left enabled it was also nearly **inert** — it vetoed 12/13, 3/3, 3/4 and 20/23 tier-2 splits, degenerating to location keying.

**Mechanism of failure, and this is the reusable part**: absence-of-validation defects ("does not validate decay_rate", "accepts negative counts") are the dominant critical class in this archive, and **a mutation cannot remove a check that was never written**. FELM measured shared *execution-path sensitivity*, not defect identity.

**It was not vacuous.** Positive control where the defect is *in* the code gave Hamming 3, correctly DISTINCT, and Hamming 0 on both same-defect controls. The boundary is precise: mutation-based identity works on commission defects and is blind to omission defects.

**Instrument warning**: the first mutation harness run reported 0 of 12 mutants killed everywhere because the real repo was on `sys.path[0]`, so nothing executed against a mutant. Under that fault every comparison returns Hamming 0 — and Hamming 0 was FELM's word for "same defect" (`convergence_location.py:1152-1159`). After the fix the instrument was validated (4/12 and 8/12 mutants killed by real test suites) and the mechanism still did not work. **Any mutation-based identity proposal must show its instrument can fail loudly.**

Related: an early AST mutation engine spent most of its budget mutating **docstrings** — no-op changes that look like real mutations — and reported a confident meaningless result.

## 2.2 Sentence-embedding cosine as the identity decider. Implemented, live once, refuted, still installed.

`bench/dm/_similarity.py:73-203`, added `0dc6ab7` (2026-04-12). all-MiniLM-L6-v2 cosine mapped to [0,1] plus a 0.3 flaw-class bonus at BETA = 0.2, with unigram/bigram Jaccard fallback (0.6/0.4).

**Refutation 1 (2026-06-08, `Convergence_Consolidation_Plan_2026-06-08.md:33-37`)**: Exp 42's late criticals scored 0.66–0.82 to their nearest earlier finding (all re-finds) while *unrelated* findings floor at 0.48–0.55. **The bands overlap.** No single threshold separates them, and the deduplicated convergence round is threshold-brittle: τ 0.60 → R5, 0.65 → R6, 0.70 → R11, 0.75 → never converges.

**Refutation 2 (2026-07-31, `bench/audit_closing_window.py:26-38`)**: replayed over all six completed runs, it scores the two known second-defect findings at **0.684 and 0.781** against priors at the same location — above the calibrated 0.55 cut, so it calls two genuinely different defects repeats. "Embeddings of findings about the same function in the same codebase are all close; the backend captures same topic, not same defect."

**Refutation 3 (`bench/dm/_convergence.py`, replay)**: at `tau_sim_embed = 0.55` the ConvergenceDetector over-merges Exp 42 to ~1 equivalence class per round and **falsely converges at round 2** — before a serious defect had been found at round 4. Confirmed by an independent adversarial reviewer.

**Refutation 4 (live, and previously unreported)**: §1.9 above. 90% and 95% DUPLICATE rates on the two exam runs.

Its lexical sibling `jaccard_similarity` scores the same two second-defect findings at 0.081 and 0.152 (correctly NEW) but applied across the archive **destroys convergence in all six runs**. One says everything is the same defect; the other says everything is different.

**External corroboration, peer-reviewed**: Zhang et al., ACM TOSEM 32(4), 2023 — REP, a 2011 BM25F variant, beats SABD/Siamese/DC-CNN/HINDBR on 5 of 6 projects by 22.3% average RR@10, and plain Elasticsearch full-text search beats HINDBR and DC-CNN on all six. On structured machine-generated input (SlowOps, arXiv:2412.14802) TF-IDF scores 0.96 Acc@1 and the LLM embedding is the **worst** performer at 0.93. Choosing token matching over neural methods here is close to the expected outcome, not a bold call.

## 2.3 MinHash / SimHash / LSH. Proposed twice by the same source, killed by measurement.

First proposed 2026-04-04 as MF-19 (`experimental_notes/Master_Finding_Registry_2026-04-04.md:179-185`), premised on 10,000 priors × 50 new findings = 500,000 comparisons. Re-proposed 2026-08-16 and tested at commit `f32056f` (`experimental_notes/Gemini_Duplicate_Detection_Tested_2026-08-16.md`).

**The theorem was verified independently** — true Jaccard 0.333 over 4000 hash functions gave collision rate 0.301. The mathematics is correct. The recommendation still does not apply.

- **Scale is wrong by ~3700×.** The whole archive is 165 criticals = 13,530 pairs, computed exactly in **15 ms**. The worked example assumes 10,000 documents / ~50M comparisons.
- **The 1/√k error scaling plateaus on this data.** On 300-token sets, mean absolute error falls 0.083 (16 hashes) → 0.031 (1024). On real project signatures (**median 4 tokens**) the same 64× compute buys only 0.094 → 0.068, then plateaus — because Jaccard over a 4-token set takes only a few discrete values.
- Against 1144 real archived signatures at 256 hashes: mean absolute error 0.007 but **maximum error 0.358**, against a decision boundary at 0.20–0.50 separating medians of 0.559 and 0.000. The trade is up to 0.35 of error to save 15 ms.
- **Reopening condition, stated explicitly**: exact all-pairs costs 0.16 s at 1000 findings, 0.65 s at 2000, 4.5 s at 5000. The argument becomes real past ~2000 findings in one comparison set. The largest single run to date carried 48 criticals.

## 2.4 Embeddings to cross the "semantic boundary". Refuted by executing the proposer's own example.

The standard argument is that lexical methods fail on paraphrase. Gemini's worked example was "reduced thermal load" vs "decreased heat dissipation".

Both sentences were run through the **live** signature extractor and produced the **identical** signature — tokens `{17, 2, 350, 400, ZC-17}` — Jaccard **1.000**. Control: same topic, different quantities, 0.111.

`stem_signature` (`convergence_location.py:462-472`) does not extract words. It extracts bare numbers, claim IDs matching `[A-Z]{2,3}-\d{2}`, and backticked code identifiers. **Numbers have no synonyms.** The vulnerability presented as requiring expensive machinery is a weakness of word-based n-gram matching, not of this design.

## 2.5 The ID-proxy novelty key as the convergence key. Never converges.

Superseded by location keying at `375236d` and `6817227` (2026-06-09). On Exp 42 the ID-proxy series has no zero tail at any round: `[15,10,6,3,1,0,1,0,2,1,1,0,4,4,4,0]`. The R12–14 "resurgence" of 4,4,4 criticals is **four distinct CONFIRMED defects re-found every round** (C0065=C0070=C0075; C0064=C0068=C0073; C0066=C0071=C0076=prior C0037; C0067=C0069=C0074), each counted novel each time, perpetually resetting the streak. The system substantively converged by round 5 and could not recognise it. Location keying on the same recorded registry converges at round 6.

Still the fallback: on any exception in the location-keyed block the gate silently reverts to it, with a loud warning (`reference_runner_v2.py:9284-9290`).

## 2.6 The `<generic>` single-bucket unlocated key. 14.6% of criticals mis-keyed.

Every critical from which no location could be extracted was keyed to one shared string constant, so the first such finding claimed the bucket and every later one was non-novel forever. Removed 2026-08-08. Measured at 42/288 (14.6%) over 9 runs, re-measured at 50/351 (14.2%) over all 11 Exp 42–49 registries, worst case Exp 47 at 11/44 (25.0%). Root cause: `target_symbols` extracts only AST function/method/class names, so ten distinct criticals about four different **module-level regex constants** collapsed into one.

## 2.7 tau_novelty = 0.65 → 0.40. The earliest proof that no single free-text threshold works.

Recalibrated at `fdf7978` (2026-03-29). SymPy/scipy analysis of Exp 12 rounds 0–9: genuine duplicates (same function, same bug) score **0.40–0.56**; different findings score **0.30–0.40**. The bands overlap. At 0.65, 97–100% of findings were classified novel. Exponential decay fit NR(r) = 0.183·exp(−0.374r) + 0.826, asymptote 0.826, so novelty never reaches `tau_novelty_stop = 0.15` for that artefact size.

**The project has known these bands overlap since March 2026.** The June 2026 re-measurement (0.66–0.82 vs 0.48–0.55) found the same thing with a different backend.

## 2.8 The anchorless-anchor wildcard in `quantities_agree`. Tier 3's entire operative error.

`bench/convergence_location.py:764-810`; fixed 2026-08-16 at commit `130b539`.

The previous form `if a1 and a2 and a1 != a2` let a quantity with **no anchor** match any quantity of equal value — a wildcard that inverted the module's own safety property. It caused all three of tier 3's operative errors on the archive: exp47 C0020/C0063, C0041/C0063, C0057/C0063, all labelled DIFFERENT, all merged, all caused by C0063 whose one outcome is `(0.6, '')` wildcard-matching a penalty-tier 0.6 configuration constant.

The obvious fix — a distinctiveness fallback — is **wrong**: `_distinctive(0.6)` is True. Distinctiveness answers "could this value identify a computation?", not "does this value identify *this* computation?". The fix is `if not a1 or not a2: return False`. Cost: none. Same-defect answers identical (19/0/9); different-defect false SAME 14→10; operative errors 3→0; Fisher p 1.4e-07 → 3.3e-09.

## 2.9 The `block[:200]` parser fallback — substitution, not truncation.

`bench/runner_core.py:745-870`; fixed at `1e5de9a` (2026-08-17).

The DESCRIPTION/FIND regex fell through to `block[:200]`, which does not truncate a description — it **substitutes the raw schema header for it**, so every downstream consumer read metadata as the claim, including the location-keyed convergence count and the CC2 verification prompt.

Fired on **844 of 5592 archived blocks (15.1%)**. Three independent causes, each verified: the `|$` branch was unreachable because `block.strip()` removes the trailing newline the lookahead required; the separator class excluded CC2's `FIND.` and `FIND —`; markdown `## FIND` headings had no separator at all.

After repair: matches 4748 → 5060 (84.9% → 90.5%), 312 recovered, zero regressions; of the 4748 matching both ways, 4734 byte-identical, 9 gain text, 5 shrink (all corrections). Adding FALSIFIER and TARGET_FILE as terminators cut descriptions containing their own falsifier source from 190 to 44 — those import lines were manufacturing locations the finding never claimed.

**Two wider candidates were rejected on measurement**: terminating at any ALL-CAPS label recovered the same 312 but **shortened 870 correct blocks** (`EVIDENCE:` and `IMPACT:` are part of the claim in this corpus); terminating at a code fence shortened 834. The first was nearly shipped because the regression metric counted match/no-match and was blind to text loss.

## 2.10 AND / OR combination of location and signature.

Both refuted on a constructed case with execution-proven ground truth (two distinct defects on one `dedup` listing; repairing D1 leaves D2 standing). Location alone `[1,0,0,0]` merges; signature alone at 0.10 `[1,0,0,0]` merges; AND `[1,0,0,0]` merges; OR `[1,0,0,0]` merges; **HIERARCHICAL `[2,0,0,0]` correct**.

They fail because they treat the two rules as interchangeable opinions on one question. They answer different questions: location asks "somewhere new?", signature asks "same thing?". Hierarchical composition also dissolved a threshold conflict — 0.10 maximised separation over all archive pairs (79% catch, 12% false-merge) but fails the blind-spot case; 0.20 is right within a location. Both numbers were correct for the population measured. (`resources/RECOVERY.md:493-509`.)

## 2.11 SMT / formal equivalence of two solutions.

Proposed 2026-08-16 as tier 3 of a mechanical-reduction pipeline. z3 4.16.0 is installed and routed by the 21-entry tool manifest. Closed on **problem mismatch**, not measurement: formal equivalence of two executable solutions is not the question. An accusation is not executable, and its falsifier tests whether **one** defect is real, not whether two accusations are the same accusation. (Tiers 1+2 of that same proposal — AST canonicalisation plus property-based falsification — *are* FELM, already built and refuted.)

Correction to the record: `experimental_notes/Gemini_Second_Answer_Tested_2026-08-16.md:34` claims every tool named is already routed by the tool manifest. `hypothesis` 6.151.9 is installed but is **not** among the 21 manifest entries, so property-based testing has no route.

## 2.12 Stylometry / authorship attribution.

Closed on published measurement and on sign, not on this project's data.
- **Text-length floor** is 2500–5000 words and is method-independent (Eder, DSH 2015). A finding is a paragraph — two orders of magnitude below the floor.
- **Provenance is already a label.** The runner records `source_model`. Style answers a question the system does not need to ask.
- **The expected sign is wrong.** Models are 97.1% separable on style (Sun et al., ICML 2025), so same-defect *cross-model* pairs are stylometrically maximally distant. Style would penalise exactly the pairs most worth merging.
- The Bletchley analogy that motivated the question **inverts** on primary sources: operator "fist" recognition belonged to traffic analysis and never worked well; what broke Enigma was the **crib**, a literal content anchor. `stem_signature` already implements the crib.

One structural import survives and is **unbuilt**: the bombe was a contradiction-finding machine, so the warranted mechanism is a deterministic **veto** that refuses a merge on hard contradiction (different values, incompatible units, mismatched claim IDs) regardless of Jaccard.

## 2.13 Hybrid ensembles and LLM-as-judge — but see §3.5, because this one is not as closed as the record says.

Pre-refuted by argument in the 2026-08-04 panel: every prose-derived signal is computed from a channel the reporting model fully controls, so averaging two views of an absent signal does not manufacture it; and routing identity through an LLM adjudicator is model voting on the measurement apparatus.

**This is closed on argument and policy, not on a fresh measurement — and §3.5 shows it was in fact built and run live.**

## 2.14 Other retired mechanisms, briefly

- **EMA model fingerprints (α = 0.3)**, replaced at `d52526a` (2026-03-29): EMA collapsed all dimensions to ~0 over 20 rounds (0.9 × 0.7²⁰ = 0.0007). Any proposal carrying a decaying-memory term must survive a 20-round run.
- **Predecessor-product suppression weighting**, replaced at `1a30e34` (2026-04-12): the score depended on the arrival order of findings, so the same set gave different novelty depending on which model answered first. The same day, "Corroboration Collapse" — suppression weights leaking into the denominator — was fixed by structural exclusion. Both are live hazards for any weighted-similarity proposal.
- **Signature-only (word-overlap) second-defect separator** (2026-08-03): correctly separated both constructed test cases; run against six completed experiments it **destroyed convergence in all six**, because ordinary rewording between rounds reads as a brand-new problem.
- **`SUPERSEDE`/`SUPERSEDES` protocol** — a model-side identity primitive present in Exp 30–33 prompts, killed at `bench/EXP35_PLAN.md:128` **with no measurement attached**.
- **The pooled truncation-harm association** — Fisher p = 2.07e-05, OR 10.5, retracted: on repaired text it measures p = 0.272. The stratification was right and the pooled figure was an artefact. This is the project's own precedent for the correction in §6.

---

# 3. WHAT IS BUILT BUT NEVER SWITCHED ON

## 3.1 Tiers 2 and 3 of the identity rule — built, measured, never wired to a gate

`hierarchical_novelty_convergence` is defined at `bench/reference_runner_v2.py:640`. **Its only non-test read in the entire repository is a `getattr` at `:9855` that writes a boolean into the report** (verified: `grep -rn hierarchical_novelty_convergence bench scripts --include="*.py" --include="*.json" | grep -v /tests/` returns exactly three lines — the definition, the report read, and a comment). Setting it True changes no gate, no count, and no verdict.

Zero of 43 shipped configs set it, and two tests assert that no config does (`bench/tests/test_hierarchical_novelty.py:157`, `test_combined_identity_rule.py:845`).

**Label correction**: one internal sweep files this as NEVER_BUILT. The flag, `hierarchical_novelty_series`, `novelty_rule_divergence` and the whole identity rule *are* built. The correct label is **BUILT, NEVER WIRED TO A GATE**. Promotion is unwritten code plus a re-run, not a config edit.

Worse: `RunnerConfig`'s own comment says the rule is "recorded in SHADOW on every run at no cost". It is not. `grep -rl hierarchical_crit_series bench/logs` returns **zero files**. The emission block (`:9845-9865`) was added after the last live run (Exp 49, 2026-07-29) and sits inside the terminal report block, after `signal = brain.signal_complete()` at `:9824`, computed from the final registry — so even with the flag wired it could not gate mid-run as currently placed. Every "six archived runs" figure quoted for the similarity function was computed post-hoc by `scripts/similarity_operating_characteristic.py` replaying the registries.

**Tier 2** — `stem_signature` / `signature_similarity`, `WITHIN_LOCATION_THRESHOLD = 0.20` (`convergence_location.py:459-480`). Jaccard over numbers, claim IDs, and backticked identifiers. Same-defect median 0.559 (n=28) vs different-defect 0.000 (n=290), Mann-Whitney p = 1.9e-25, coverage 161/165 criticals (97.6%). On repaired text: coverage 160, 460 pairs, AUC 0.976 CI [0.939, 0.998].

**Tier 3** — `computed_outcomes` / `outcome_agreement` (`:683-828`). Extracts `(value, anchor)` quantity pairs a finding *asserts*, masking labels first, and answers SAME / DIFFERENT / UNKNOWN. Bounded authority: it may only **merge**. Coverage 94/165 (57.0%), 110/165 on repaired text. Fisher exact on the decided 2×2 `[[0,19],[34,10]]` p = 3.3e-09.

**And this is the single most transferable lesson in the record.** Routed through `identity_decision` over the labelled pairs, tier 3 changes the outcome on **four of 412 pairs and is wrong on all four** **[recomputed 2026-08-17 on the current adjudicated set; previously recorded as 3 of 318, wrong on all 3]**. A tier justified at p = 3.3e-09 is, in operation, 0 for 4. Thirty-six green tests did not distinguish the two. The project's conclusion: *an answer distribution is not an operating characteristic, and this project had been reading one as the other.*

**The promotion currently fails its own acceptance test, and this is reported as a failure rather than smoothed** (`convergence_location.py:372-435`). Three-round tails at each run's convergence round: exp44 holds; **exp45 `[1,0,1]`, exp46 `[0,1,0]`, exp47 `[0,0,1]`, exp49 `[1,0,0]` all break**; exp48's location tail was already non-zero. Four of six broken. Of the five findings that break a tail, three are genuine second defects location keying could not see (exp45 C0014, exp45 C0031, exp47 C0070) and two are false splits (exp46 C0026, a verbose re-find diluted to 0.091 by line numbers and dates; exp49 C0037, already found as C0035 at signature 0.182, just under the cut).

## 3.2 The `dm/` package — imported and constructed, never queried

**Correction to two internal sweeps.** `bench/reference_runner_v2.py:63` does `from dynamic_management import (DynamicManager, …)` and `:8161` constructs `mgr = DynamicManager(model_specs, dm_config)`. `DynamicManager.__init__` (`bench/dm/_manager.py:112-118`) then constructs `ConvergenceDetector(self.config, similarity_fn=_finding_similarity)` and `DiminishingReturnsDetector(self.config)` **on every run**. The sweeps that say "the runner never imports this" looked at the wrong line range — the import block starts at `:53`, not `:106`.

The dormant verdict survives on substance: `grep -n "mgr\." bench/reference_runner_v2.py` returns nothing; `mgr` is only ever passed to `_should_decompose`; `process_round`, which contains the rho similarity pass at `_manager.py:692-710`, is never called. `add_round_findings` (`_convergence.py:86-109`) only stores and invalidates a cache, so no clustering is ever computed.

But the citation matters for how you read it: a panel told "the runner never imports this" will propose "wire up the existing detector" as a cheap change. It is not cheap, and the detector it would wire up is the one that falsely converged Exp 42 at round 2.

**Historical correction**: the kappa detector was **live from Exp 29 to Exp 37**, invoked every round by `run_exp29_persistence.py:844`, `run_exp30_endocrine.py:1130`, `run_exp31.py:1208`, `run_exp32.py:1400`, `run_exp33_endocrine.py:1331`, `run_exp34_endocrine.py:1492`, `run_exp35_policy_engine.py:2616`, `run_exp36_evidence.py:3169`, `run_exp37_evidence.py:3256`. It was dropped at the v1/v2 runner boundary, not designed out.

## 3.3 `LocationNoveltyTracker` — dead on the live path, but under active test

`bench/convergence_location.py:142-200`. No import anywhere in `reference_runner_v2.py`; the runner reimplements the same idea inline.

**Correction**: one internal sweep states the grep returns only the class definition, "not tests". False. Verified: `bench/tests/test_convergence_location.py` (5 references) and `bench/tests/test_convergence_location_calibration.py` (7 references) both import and instantiate it. It has a calibration suite, including `test_known_limitation_second_defect_same_function_is_missed`, which **pins the blind spot rather than fixing it**. That is materially different from "dead code" for anyone proposing to revive it.

## 3.4 Vocabulary saturation — abandoned by attrition, never refuted

`bench/dm/_diminishing_returns.py`, added `d52526a` (2026-03-29) specifically because it is "immune to the Jaccard semantic-equivalence problem that defeated kappa and novelty_rate". Measures cumulative unique-term growth; fires when growth drops below 10% for three consecutive rounds. **It compares no findings to each other at all.**

Called only from v1-era runners. **No measurement of its accuracy exists anywhere in the record.** If you propose something in this family, the honest status is "tried, never measured, then dropped" — not "refuted".

## 3.5 The Dedup Assessor — an LLM-adjudicated dedup pipeline that ran live in Exp 36 and Exp 37

`bench/cc2_manager.py`. Threshold at `:53`: `DEDUP_SIMILARITY_THRESHOLD = 0.35  # Lowered from 0.65 — Exp 36 showed 4:1 redundancy with semantic duplicates slipping through at higher thresholds`.

Two-stage: `_find_dedup_candidates` (`:810-844`) does stopword-stripped Jaccard over descriptions and keeps the top 5 above 0.35, excluding `{MERGED, REFUTED, DUPLICATE}`; `dedup_assess` (`:476-541`) sends them to Haiku under `_DEDUP_PROMPT` (`:241-257`), whose rule is "Same ROOT CAUSE = duplicate, even if described differently. Similar symptoms but different root causes = NOT duplicate", returning `DUPLICATE_OF <id> | <confidence> | <evidence>`. At `:937-943` a DUPLICATE at confidence ≥ 0.85 **short-circuits the entire verification pipeline** — CC2v never runs. Authority order at `:986-990` puts high-confidence dedup second only to tool-backed verdicts.

Wired at `bench/run_exp36_evidence.py:1157` and `bench/run_exp37_evidence.py:1185`. Not imported by `reference_runner_v2.py`.

**This corrects the record in two ways.** First, "LLM-as-judge for finding identity" is filed internally as pre-refuted by argument. It was in fact **built and run live for two experiments**. Second, its threshold carries a recorded Exp 36 calibration, making it a **fourth calibrated threshold** against the claim that exactly three were ever calibrated.

If you propose an LLM adjudicator, you are proposing to restore something that ran and was dropped without a recorded outcome measurement. Say what you would measure differently.

## 3.6 Other built-but-off mechanisms

- **`effective_tau_sim` / `tau_sim_embed = 0.55`** (`bench/dm/_similarity.py:206-231`) — a backend-aware threshold selector built to fix a false-convergence defect where `tau_sim = 0.33` sat below the embedding backend's ~0.48 anisotropy floor. Bound into `ConvergenceDetector`, which the arc runner does not drive. Live experiments were unaffected only because the immune pipeline had independently hardcoded 0.50.
- **`verification_utils.dedup_findings`** at `tau_sim = 0.8` (`bench/verification_utils.py:321-368`) — a fourth, forgotten default at a value the codebase's own comment calls unreachable. Sole importer is `run_baseline_confer.py`.
- **`Finding.dedup_of`** (`bench/dm/_types.py:421`) — a persisted duplicate pointer, serialised at `insect_brain.py:946`, `:997` and read back at `:1467`. **Nothing anywhere writes it.** It is in the checkpoint schema and in archived round JSON, always empty.
- **`bench/metacognitive_feedback.py`** — a model-facing redundancy-trend module with `_rho_trend` at `:41-68`. Zero importers.
- **`DetectorHealthMonitor`** (`bench/dm/_immune.py:218-244`) — raises WARNING→CRITICAL when "kappa stuck at ~0 for N consecutive rounds despite N findings produced", with `recommended_action` = "Similarity function may be too strict for this domain." A built self-monitor for the exact failure mode this experiment is about, dormant with the rest of `dm/`.
- **Severity calibration and the latent tagger** (`050f17c`, 2026-06-10) — the mechanism to lower an over-rated-but-real critical below 0.7 so it stops re-blocking convergence. Inert until a latent tagger sets `entry['latent']`, which is itself off with no config setting it.
- **ImmuneMemory cross-experiment prior** (`bench/dm/_memory.py:197-274`) — enabled in 11 configs, but `immune_memory_consume_rk0` defaults False (`reference_runner_v2.py:699`). Cross-*run* duplicate detection is a separate, mostly unbuilt axis.
- **Discrimination control** — refuted as a gate by CC2 in the 12 August panel because it tests **access, not dependence**: "A gate whose satisfaction condition is access rather than dependence is one line away from being defeated, and it fails green." Verified across all 465 archived falsifiers: 465 returned NO CONTROL, zero verdicts moved. Recommendation on record: leave it recording, do not arm it.

## 3.7 A live defect in the one canonicalisation scheme that does exist

`bench/cdsfl_registry/refinements.py:125-149`. Findings are canonicalised as 4-tuples `(artifact, assumption, violation_mode, witness)`, each field lowercased, stripped, and **"sort space-separated terms alphabetically within each field"**, then SHA-256'd for structural dedup — explicitly to prevent "false negatives (same finding, different wording) and false positives (different findings, similar wording)". Confirmation requires 2 distinct model families (`_MIN_INDEPENDENT_FAMILIES = 2` at `:188`).

**Exp 47 broke it, with an executed falsifier.** Finding `DeepSeek_F016` → canonical `C0058`, severity 0.72, `falsifier_verdict: CONFIRMED`, status CLOSED. The falsifier shows that alphabetical token-sorting collapses **non-commutative** statements: "alternative_a beats alternative_b" and "alternative_b beats alternative_a" produce the same tuple and the same hash, and the reversed statement is then counted as *independent peer support*. `refinements.py` has had no commit since `5b3e261` (2026-03-26), so the defect is present at HEAD.

Any proposal for typed-field canonicalisation must answer this: **order-insensitive normalisation destroys directional claims, and this project has an executed falsifier proving it on its own data.**

---

# 4. WHAT WAS RECOMMENDED AND NEVER BUILT

## 4.1 Structured value emission — the panel's single unanimous recommendation, six independent endorsements, still unbuilt

On 2026-08-12 all five panel models proposed this independently and unprompted:
- Gemini: a `verdict.json` carrying `{expected, actual}`.
- Codex: a normalised tuple `(claim_id, claimed_value, observed_value, unit, operator, tolerance)`.
- ChatGPT: `{claimed, computed, operator, units}`.
- DeepSeek: numeric extraction from stdout compared against the claim.
- CC2: an "outcome algebra" covering dedup, contradiction and independent recomputation.

Gemini re-derived it independently on 2026-08-16 as "the one genuine gap". That is six endorsements.

**Nothing in the pipeline asks a model or a falsifier to state, in a fixed field, the value it claims and the value it computed.** Tier 3 still recovers quantities from prose by regex (`convergence_location.py:683-690`).

**Naming trap.** `Path_To_BR2_And_Open_Decisions_2026-08-13.md:126` says "the structured statement of numbers is built, tested at ninety four passing tests, committed, and not enabled". That refers to **tier 3, the prose extractor**, not to structured emission. Two different things sharing one name, and conflating them is how this gap stayed open.

**Partial qualification** (§3.7): `bench/run_round_robin.py` *does* preserve structured fields through the pipeline for the `refinements.py` hash (`:139`, `:311`, `:2387`, `:3222`). So "nothing anywhere asks a model for structured fields" is too strong for the repository as a whole, though true of the Exp 40–54 runner.

**Recorded testable prediction, checkable against the archive with no live run**: tier-3 coverage should rise from 57% toward the proportion of findings asserting any quantity.

## 4.2 IDF weighting of hard tokens — called "the highest-value change available", never built

Current Jaccard treats `mm` and `6.674e-11` as equally evidential. Grounding: Fellegi–Sunter log(m/u) weights; Cohen/Ravikumar/Fienberg IJCAI-03 found TF-IDF-weighted token metrics among the best on this class of task. Deterministic, no model, computed from this project's own corpus, zero new dependencies.

**A one-query falsification test was supplied and has not been run**: plot the IDF distribution of the hard-token vocabulary. If bimodal (common units and small integers, plus a tail of rare constants and equation IDs), IDF helps substantially in the ambiguous band. If uniformly rare, it gains nothing.

## 4.3 Containment alongside Jaccard, IDF-weighted — never built for findings, and *is* built for directives

Jaccard penalises size mismatch, so a terse finding and a verbose one about the same defect score low even when one token set contains the other. Broder's containment `c(A,B) = |A ∩ B| / |A|` (SEQUENCES 1997). Raw containment is dangerous for low-cardinality findings — a finding whose only token is `10%` is contained in any long finding mentioning 10% — so the concrete recommendation is IDF-weighted containment.

Directly relevant: verbose re-finds are one of the two named false-split causes in the archive (exp46 r4 C0026 diluted to 0.091 by line numbers and dates).

**And it already exists elsewhere in this repository**: `composer.py:304` runs `containment >= 0.95` with a synonym table, live every round, on directive text.

## 4.4 Graded numeric tolerance — partially present, graded version never built

`9.8`, `9.81`, `9.807`, `9.8 m/s²` and `9.8 m s⁻²` are five distinct tokens today. Canonicalise numbers and units, then compare with graded levels (exact / within 0.1% / within 1% / different) as weighted comparison levels, Splink-style. **Critically, tolerance must be graded and never collapsing — the difference between 9.8 and 9.81 can itself be the defect.**

Present: a single binary tolerance `_OUTCOME_TOLERANCE = 1e-3` (`convergence_location.py:653`) and a hand-built compound-unit regex added because "112.15 g/mol" was parsed as "mol". No graded levels, no general unit canonicalisation.

## 4.5 The impostors method as a threshold replacement (Koppel & Winter, JASIST 2014)

Instead of thresholding `sim(A,B)` directly, ask whether A is more similar to B than to a randomly drawn crowd of impostors, repeated across randomly sampled feature subspaces. Output is calibrated against the **local difficulty** of the comparison rather than a fixed cut.

Concretely here: sample k other findings from the same round as impostors, repeatedly sample random subsets of A's hard-token set, count the fraction of trials where B is A's nearest neighbour. Fully deterministic given a seed, no embeddings, no model call. It addresses exactly the failure mode a fixed threshold has — over-merging when a round happens to contain many near-neighbours.

## 4.6 Capture–recapture reframing of the stop rule

"If I could recommend only one structural change, it is this one." Software inspection solved "when do we stop" thirty years ago: capture–recapture estimators use the **overlap** between defects found by independent reviewers to estimate remaining defect content — and the matching step in capture–recapture **is** the similarity function (Briand, IEEE TSE 2000; Petersson, JSS 2004).

It gives a confidence interval on residual defects instead of "no new findings appeared", plus a natural sensitivity analysis of estimator error against matcher error. Mostly writing, not code. It converts the similarity function from an unmotivated component into the measurable input of a well-studied estimator.

## 4.7 The deterministic contradiction veto

The one surviving structural import from the Bletchley analysis: a veto that refuses a merge on **hard contradiction** — different values for the same anchor, incompatible units, mismatched claim IDs — regardless of Jaccard. Cheap, deterministic, fails in the safe direction. Never built. Note that tier 3 already computes DIFFERENT and currently **discards it** (`convergence_location.py:903-907`: DIFFERENT is recorded as corroboration and changes no count).

## 4.8 Baselines and ablations — "the reviewer's first question", never run

Named as decisive by two independent research strands: **if plain stopword-stripped Jaccard on raw finding text scores nearly as well, the hard-token extractor earns nothing and the premise fails.** Hard tokens are also rare tokens, and rare tokens dominate Jaccard anyway.

The only baseline computed anywhere is location-keying-alone (`scripts/similarity_operating_characteristic.py:388`). **No plain-word Jaccard ablation, no TF-IDF, no BM25, no embedding-as-classifier, no LLM-judge comparison, no token-class leave-one-out.** This is the single largest unopened door in the record, and it is cheap.

## 4.9 Falsification tests written and never run

- **Same-model vs cross-model stratification** — split same-defect pairs by whether both findings came from one model. If cross-model same-defect pairs score materially lower, the reported 0.559 median is inflated and the function is weakest exactly where cross-model corroboration should be strongest. Proposed independently in two strands, described as runnable "in one query on your existing 318 pairs". Never run. The data is in `experimental_notes/data/similarity_pairs_adjudicated.json`.
- **Sparsity conditioning** — re-run the same/different comparison conditioned on both findings carrying ≥ 4 hard tokens. If the 0.559-vs-0.000 separation survives, tier 2's discrimination is real; if it collapses, the medians were a sparsity artefact of 4-token sets. Never run.
- **Tail rather than centre** — the medians describe distribution centres, but the merge decision lives in the tails. The different-defect 99th percentile against the same-defect 5th percentile is the number that determines early stopping. Never computed.
- **Structural skew of the coverage gap** — the ~2.4% zero-hard-token findings are systematically the **conceptual** ones ("the argument in section 4 is circular"), which may be the most valuable. Never checked whether the gap is random or structurally skewed.

## 4.10 Identical proposed fix as a candidate signal — cheap, deterministic, unexplored

**[recomputed 2026-08-17]** Over 24 archived `bench/logs/exp4*/runner_state.json` files: 877 registry entries carry a substantive `proposed_fix` (≥ 40 chars after whitespace normalisation); **201 pairs of distinct canonical entries propose a byte-identical repair**. Group size distribution: 36 groups of 2, four of 3, three of 4, three of 5, and one of 15.

Clean cross-model examples in the exam runs: exp49 `C0001`/`C0011` (EN-06 Euler load) and `C0006`/`C0016` (EN-41 p-value), all four CLOSED as separate canonical entries.

Caveat, stated so it can be attacked: the group of 15 is probably boilerplate, so identical-fix is a **candidate** signal rather than a decided one. But it is deterministic, costs nothing, needs no model, and is the cheap sibling of counterfactual repair — and the fingerprinting machinery exists at `bench/exp40_fix_harvest.py:19`, `:77-100`.

## 4.11 Older unbuilt proposals, for completeness

- **Idiotypic continuous suppression** (2026-04-12, ranked HIGH) — replace the hard `tau_sim` cut with proportional suppression, `weight = base × ∏(1 − sim)`. Explicitly aimed at "the documented false-duplicate problem". Never built, never measured.
- **Negative selection / full CLONALG / full DCA / Kohonen SOM** — four immune- and clustering-inspired approaches assessed 2026-04-12 and explicitly not recommended. Negative selection scales exponentially in natural language with boundary-coverage holes exactly at the boundary that matters. DCA presupposes the signal-categorisation problem rather than solving it.
- **Finding-level isomorphism suppression** — required by `cdsfl_topology_formal.md:410-413`, built only at the alternative level.

---

# 5. WHAT IS CALIBRATED VERSUS GUESSED

Every threshold that can affect a sameness decision. "Calibrated" means a recorded measurement against data produced the number. "Measured but not swept" means the separation was measured but the cut was not. "Chosen" means someone picked it.

## Calibrated against data (four, plus one calibrated design decision)

| threshold | value | calibration | status |
|---|---|---|---|
| `_UNLOCATED_MERGE_THRESHOLD` (`reference_runner_v2.py:4168`) | 0.20 | 6-run convergence-round sweep; identical for every cut in [0.15, 0.40]; at ≥ 0.50 exp46 loses convergence; exp47 moves 13→11 at 0.10 | **LIVE — the only calibrated live one** |
| `tau_sim` (`dm/_types.py:85`) | 0.33 | Run 8: max pairwise sim 0.553; 67 clusters from 339 findings, 80% churn detected | DORMANT |
| `tau_novelty` (`dm/_types.py:102`) | 0.40 | Exp 12 R8: duplicates 0.40–0.56, different 0.30–0.40 | DORMANT |
| `DEDUP_SIMILARITY_THRESHOLD` (`cc2_manager.py:53`) | 0.35 | Lowered from 0.65 on Exp 36's 4:1 redundancy | DORMANT since Exp 37 |
| `_PREMISE_HEADER` scope (`convergence_location.py:93`) | `premise(s)` only | 2187 archived descriptions; 122 carry a header, `EVIDENCE:` is 78 and stripping it would delete real signal | **LIVE** |

Honest limit on the one live calibrated threshold, recorded in the code at `reference_runner_v2.py:4158-4161`: **0.20 was swept against within-location pairs, never against the unlocated sub-population it actually serves.** And the sweep exists only as prose in a docstring — no script or test reproduces it, so it will go stale silently.

## Measured but not swept (two, both shadow)

- `WITHIN_LOCATION_THRESHOLD = 0.20` (`convergence_location.py:459`). Separation measured at p = 1.9e-25; the cut itself recorded as unswept at introduction (`9cd8f62`, verbatim: "0.10 optimal over all archive pairs, 0.20 correct within a location… within-location threshold unswept"). Later sweep on embedding labels: false-merge 16.55% at 0.15, 14.48% at 0.20, 4.14% at 0.30, 1.38% at 0.40, with recall 100% at 0.15/0.20 falling to 92.9% at 0.30 and 82.1% at 0.40. **15 of 318 labelled pairs sit exactly on 0.20**, because 1 shared token out of 3-and-3 gives exactly 0.200.
- Tier-3 constants: `_OUTCOME_TOLERANCE = 1e-3` and the `_distinctive` rule `|v| ≥ 10`. Both chosen. The distinctiveness rule is documented as insufficient by its own evidence — `_distinctive(0.6)` is True.

## Chosen, never calibrated — this is everything else the runner uses to decide sameness today

`CRITICAL_SEVERITY_THRESHOLD = 0.7` (`reference_runner_v2.py:4006`, duplicated at `audit_closing_window.py:102` and again as `LEDGER_CRITICAL_SEVERITY` at `bench/evidence.py:794-799`); routing `dup_threshold = 0.85` (`routing.py:76`); `verification_confidence_threshold = 0.7` (`reference_runner_v2.py:597`); the ≥ 2-distinct-model merge quorum; merge arbitration 3-of-5, `min_defer_count` 2, `max_per_round` 3, `tiebreaker_gamma` 0.05; NK `tau_sim = 0.50` (`immune_agents.py:3075`, `:4317`, `:5576`); `tau_sim_embed = 0.55`; `CLASS_BONUS = 0.3`, `BETA = 0.2`, unigram/bigram 0.6/0.4, empty-token fallbacks 0.5 and 0.1 (`dm/_similarity.py:37-38`, `:88-105`); `lambda_s = 1.5`, `w_floor = 0.05`, `suppression_k = 3`; `tau_kappa = 0.95`, `eta_veto = 0.9`; `_MIN_LEN = 4` and `_GENERIC = {main, compose, run}`; `dedup_findings tau_sim = 0.8`; `isomorphism_threshold` 0.85 / `near_copy_threshold` 0.98; `VERDICT_CLUSTER_THRESHOLD = 0.8`; `max_novel_findings = 2`; `gamma_alt_consecutive_zero_crit = 3`; **`EMB_SAME = 0.90` and `EMB_DIFF = 0.70`** (`scripts/similarity_operating_characteristic.py:100`), which are the bands that produce the ground truth every other figure is scored against.

## Three self-contradictions in the record that must not be inherited

1. **`docs/MATHEMATICAL_APPENDIX.md:1380` and `:1835`** assert that `tau_sim` thresholds are "calibrated empirically per experiment". Measured false: **0 of 43 shipped configs set `tau_sim`, `tau_sim_embed`, `tau_novelty`, `hierarchical_within_threshold` or any similarity threshold.** Every one runs at its module default in every experiment. `docs/GLOSSARY.md:201` and `docs/ARCHITECTURE.md:75` also present NK `tau_sim = 0.50` as the project's deduplication stage without noting it is shadow in runner v2.
2. **`tau_sim_embed = 0.55`**: `dm/_types.py:88-89` says "calibrate against Exp 38 data" (imperative — not yet done); `dm/_similarity.py:214-216` asserts it *is* calibrated. No Exp 38 calibration artefact exists. Treat it as uncalibrated.
3. **§8.1 of the operational directive tells every model, in every run, something false.** `bench/directives/universal/cdsfl_operational.md:375-384`: "The system measures genuine novelty by comparing the **content** of your findings against all prior findings using semantic similarity (not just finding IDs). Two findings about the same root cause with different labels are detected as duplicates." In runner v2, novelty is alias identity plus location keying. `:739-744` also tells models near-duplicates are flagged at "cosine ≥ τ_sim_embed", whereas the live NK threshold is 0.50 on the blended score, not 0.55.

## The threshold split that *was* a design decision, not an oversight

`bench/insect_brain.py:1296-1300`: "NK dedup threshold is decoupled from convergence tau_sim. Convergence uses 0.33 (loose: 'similar enough to cluster'). NK immune uses 0.50 (strict: 'similar enough to REJECT'). Different questions, different thresholds."

## Three copies of 0.20 exist

`WITHIN_LOCATION_THRESHOLD` (`convergence_location.py:459`), `_UNLOCATED_MERGE_THRESHOLD` (`reference_runner_v2.py:4168`), `hierarchical_within_threshold` (`reference_runner_v2.py:641`). The second is deliberately a local copy "so a future recalibration of the within-location cut cannot silently move the convergence gate". Only that one is under test for drift.

---

# 6. THE OPEN QUESTION, AND THE BAR TO BEAT

## 6.1 The question, stated precisely

Given two critical findings (severity ≥ 0.7) that name **at least one location in common** on the same target artefact, decide whether they describe the same defect or two different defects, using only what the pipeline already has or can cheaply obtain, without a model vote, and with an error profile better than what follows.

Two constraints that any answer must respect:

- **Merge errors and split errors are not symmetric.** A false merge ends a run while genuine defects are still arriving. A false split prevents a run from ever ending — that is the ID-proxy regime, which never converges. Both trivial constant rules ("always merge", "always split") are inadmissible for that reason, and both appear below as baselines only.
- **The dominant critical class in this archive is absence-of-validation.** "Does not validate X", "accepts negative Y", "no bounds check on Z". This is why mutation-based identity failed, and any execution-based proposal must say what it does with a defect that consists of code that isn't there.

## 6.2 The ground truth, and its known limits

On 2026-08-17 (commit `5354b95`) the project obtained its first **tool-decided** labels via counterfactual repair: apply finding A's proposed fix to a scratch copy of the target, re-run **both** findings' falsifiers; if B's now passes, A's repair cured B, so SAME; if B's still fails, DIFFERENT. Run in both directions and require agreement. `scripts/adjudicate_by_repair.py`.

This replaced two rejected alternatives, and the reasoning is on record: asking the founder puts a chemistry/engineering judgement in front of the one participant with no domain access; asking a model panel to vote is "the free pass the whole project exists to refuse".

A prerequisite bug had to be fixed first. The fix **emitter** (`bench/runner_core.py:886`) writes `<<<< SEARCH <path>` / `==== REPLACE` / `>>>>` while the **parser** (`bench/endocrine.py:589+`) required `====` exactly, with REPLACE on the closing line, and gated on `'SEARCH' in line`. Every runner-emitted fix failed all three conditions. The first adjudication run decided **zero** pairs. With three corrections, **129 of 153** archived fixes apply.

Verdicts as stored: SAME 23, SAME_ONE_WAY 17, DIFFERENT 10, DIFFERENT_ONE_WAY 35, UNDECIDABLE 33, DISAGREE 8, NO_BASELINE 7. **85 of 133 decided (63.9%).**

Two things about this sample that determine how the numbers below must be read **[recomputed 2026-08-17]**:

1. **All 85 repair-labelled pairs lie in the 0.70–0.90 embedding band** — the band the original benchmark silently discarded. Median embedding 0.798, zero pairs outside the band. The remaining 48 pairs of that band are still unlabelled by any method. The other 327 labelled pairs sit at ≤ 0.70 (296) or ≥ 0.90 (31), median 0.538.
2. **CC2's own decidability prediction was wrong, and it named its own kill condition.** It predicted 92.8% decidable and said "if the UNDECIDABLE rate on replay exceeds ~30%, HIL load makes the method impractical and it dies". Actual decidability 63.9%; total undecided (UNDECIDABLE + DISAGREE + NO_BASELINE) 48/133 = **36.1%**, above the line; strict UNDECIDABLE alone 33/133 = 24.8%, below it. The method survives on the narrow reading and fails on the broad one. **Nobody has ruled which reading binds.**

## 6.3 CORRECTION: the headline error rates are pooled, and the stratified numbers are much worse

**The anchor figure "85 pairs labelled by counterfactual repair, false-split 23.9%, false-merge 21.4%" is arithmetically correct but describes the wrong population.** 23.9% and 21.4% are computed over **all 412 labelled pairs** — 327 embedding-labelled plus the 85 repair-labelled. Only 85 of the 412 are repair-labelled.

Recomputed by routing every labelled pair through `CL.identity_decision` using the project's own canonical method (`scripts/similarity_operating_characteristic.py:367-386`) **[recomputed 2026-08-17, HEAD 5354b95]**:

| population | n | same | diff | false split (of same) | false merge (of diff) |
|---|---|---|---|---|---|
| ALL labelled (pooled) | 412 | 71 | 341 | 17/71 = **23.9%** | 73/341 = **21.4%** tier-2 only; 77/341 = 22.6% incl. tier 3 |
| **repair-labelled only (the hard band)** | **85** | **40** | **45** | **17/40 = 42.5%** | **29/45 = 64.4%** tier-2 only; 30/45 = 66.7% incl. tier 3 |
| embedding-labelled only (the easy bands) | 327 | 31 | 296 | 0/31 = **0.0%** | 44/296 = 14.9% tier-2 only; 47/296 = 15.9% incl. tier 3 |

This also **reconciles the disagreement between the internal sweeps**, which was left open: one sweep reproduced 23.9%/22.6% and another 23.9%/21.4%. The difference is exactly tier 3's four merges. `21.4%` counts tier-2 merges only; `22.6%` includes tier 3. Both are right about their own scope. Adding tier 3's merge authority makes the pooled false-merge rate **worse**.

Decision reasons over the 412: `signature_split` 281, `signature_merge` 127, `same_computed_outcome` 4. **All four tier-3 merges are wrong (label 0).**

**Consequently, `bench/convergence_location.py:565` — "ZERO false splits on either version", listed under "WHAT SURVIVES THE REPAIR — these are the load-bearing claims" — is falsified by the newer data.** There are 17 false splits in 40 same-defect pairs. The zero is an artefact of the embedding label source: pairs at embedding ≥ 0.90 are lexically near-identical, so tier 2 at 0.20 always clears them. The embedding label set **cannot produce a false split**.

Every one of the 17 false splits lives in the repair subset. Pooling the hard population with the easy one understates the true error by **1.8× on splits and 3.0× on merges**. This is the same pooling artefact the project already retracted once, on truncation harm (`convergence_location.py:566-572`, Fisher p = 2.07e-05 → p = 0.272 under stratification).

The external critique that "0 false splits in 28 pairs" should be stated as "below about 11%" (95% Clopper-Pearson upper bound 12.3%, rule of three 10.7%) was **right in direction and far too generous in magnitude**. The measured rate on tool-decided labels is 42.5%.

## 6.4 THE BAR TO BEAT

**On the hard band — the 85 tool-decided pairs, the only ground truth in this project not produced by another similarity function [recomputed 2026-08-17]:**

|  | tool says SAME (40) | tool says DIFFERENT (45) |
|---|---|---|
| **rule merges** (53) | 23 correct | **30 false merges** |
| **rule splits** (32) | **17 false splits** | 15 correct |

- Merge recall (same-defect pairs correctly merged): **23/40 = 57.5%**
- Split specificity (different-defect pairs correctly split): **15/45 = 33.3%**
- Merge precision: **23/53 = 43.4%**
- Overall agreement with the tool: **38/85 = 44.7%**

Against the two constant baselines on the same 85 pairs:

- **Location keying alone** (merges every same-location pair, which is what actually gates today): correct on **40/85 = 47.1%**.
- **Always split** (the ID-proxy regime): correct on **45/85 = 52.9%**.

**The full three-tier identity rule agrees with the tool on fewer of the hard pairs than either constant baseline.** That is the honest bar. It is a low one.

**On the easy bands (327 pairs) the same rule performs well**, and this is the reason it was promoted internally: it converts 249 of 296 different-defect pairs from wrong merges (location keying's behaviour) into correct splits — a **296 → 47, 84% reduction in false merges** — at the cost of zero false splits.

Pooled over all 412: the rule is right on 318 (77.2%) against location keying's 71 (17.2%). **So the rule is a large improvement where the question is easy and no improvement at all where it is hard.** A discriminator that beats it must beat it on the 85, or on the 48 still unlabelled pairs in the same band.

**Supporting operating characteristics, for context rather than as the bar:**
- Tier 2 AUC on repaired text: **0.976, 95% CI [0.939, 0.998]**, bootstrapped over findings, not pairs. Same-defect median Jaccard 0.559 (n=28) vs different-defect 0.000 (n=290).
- Tier 2 coverage: 160/165 criticals (97.6%). Tier 3 coverage: 110/165 (66.7%) on repaired text, 94/165 (57.0%) as archived.
- Tier 3 as a merge rule: recall 19/28 = 67.9%, precision 19/33 = 57.6%. Because it can only merge, **every tier-3 error is a false merge**.
- Random negatives inflate reported separation. PAWS collapses bag-of-words matchers from AUC 89.5 to 27.1. The 438-pair sample's easy negatives inflate every figure above — which is precisely what §6.3 measures directly.

## 6.5 What a proposal has to do to be taken seriously here

1. **Say which mechanism it replaces.** There are eight (§1). "Improve duplicate detection" is ambiguous between the convergence-keying tier (never gated for tiers 2–3), the NK immune dedup (live, 90–95% DUPLICATE, no published operating characteristic), the routing merge (live, fired once), the CC2 single-model merge (live, no flag), the model MERGE quorum (live, produces every MERGED status), G7 arbitration (live in 27 configs, never fired), ρ (live, gates), and registration identity (live, no cross-model dedup at all).
2. **State its operating characteristic, not its answer distribution.** How often does it change a decision, and how often is that change right? A p-value describing what a component *says* is not a measurement of what it *does*. Tier 3 was justified at p = 3.3e-09 and is 0 for 4 in operation.
3. **State how it fails.** Merge-direction or split-direction, and why that is the safe direction for this gate.
4. **State what it does with omission defects** — the dominant critical class here, and the reason FELM failed.
5. **Be checkable against the archive without a live run.** 460 same-location pairs are in `experimental_notes/data/similarity_pairs_adjudicated.json`; 85 carry tool-decided labels, 327 carry embedding labels, **48 carry none and are the hard remainder**. `scripts/similarity_operating_characteristic.py` will score any rule that exposes a decision function. Descriptions are repaired via `scripts/backfill_descriptions.py` (531 repairs); note that **live runs still truncate at 500 characters** (`reference_runner_v2.py:1059`), so a rule that needs full text needs that fixed first, and fixing it mid-arc breaks comparability of Exp 50+ with Exp 40–49 on every signature-derived measure. That ruling has not been given.

## 6.6 Open items that bear on any answer, stated as open

- **48 pairs in the 0.70–0.90 band remain unlabelled by any method.** They are 10.4% of the pair set and 36% of the hard band. Every operating point in this brief is provisional until they return. Two stratified adjudication sheets exist (`experimental_notes/data/Adjudication_10_2026-08-17.md`, `Adjudication_Sheet_20_2026-08-17.txt`) and were deliberately left unanswered rather than machine-labelled.
- **`scripts/adjudicate_by_repair.py:52-55` is stale.** Its HONEST BOUNDS says exam targets Exp 48/49 "are out of scope here", and its `TARGETS` dict lists only exp44–47. In fact **36 of the 85 repair-labelled pairs are exam pairs** (exp48 21, exp49 15) — the assumption that prose falsifiers do not read the document was measured false (25 of exp49's 33 open the target by path). Per-run repair coverage: exp44 34, exp48 21, exp49 15, exp47 7, exp45 4, exp46 4.
- **`bench/convergence_location.py:544-547` says both truncation defects "are now fixed". Only one was.**
- **The founder ruling of 2026-08-12 to "promote the combined rule before the capstone" is unexecuted and in direct opposition to two live tests** which assert that no config sets the flag. Whether the ruling was superseded by "do not promote mid-arc, it confounds the capstone's four-way comparison" or simply not executed is not written down.
- **Whether merge arbitration has ever dispatched cannot be established from the repository.** Runner stdout goes to `/tmp` and to launcher logs outside the repo, so absence of a record is weak evidence.
- **Four early NK dedup defects from 2026-04-04 were never re-verified at HEAD**: MF-12 (DUPLICATE verdicts coupled to reject weight), MF-13 (REJECTED and DUPLICATE counted differently in two places, so the autoimmune threshold trips at different points), MF-16 (vacuous truth: "duplicate of None"), MF-20 (NK and B cells share one triaged list across threads with no locks, so `is_duplicate` mutation is non-deterministic). **MF-20 would make dedup results run-order dependent.**
- **`exp53` has no report in either of its two log directories**, so it is absent from every archive-wide count in this brief.

## 6.7 Four standing rulings that constrain any answer

1. **An answer distribution is not an operating characteristic.** Whenever a component is justified by a statistic, measure separately how often it changes a decision and how often those changes are right.
2. **Nothing ships ambiguous.** Every component is either on, retired, or documented as an unused alternative *with its evidence* — otherwise a reader cannot tell "built and deliberately rejected" from "built and forgotten".
3. **An ineffective contribution is removed, not left in place.** The FELM ruling, quoted in the code at `convergence_location.py:1138-1140`: "if the model's contribution doesn't work and is ineffective, why leave it in place at all?"
4. **Tools decide, never votes.** Findings are confirmed programmatically or by HIL. Note the live tension: G7 merge arbitration is a ≥ 3-of-5 model vote on sameness enabled in 27 configs, the model MERGE quorum produces every MERGED status in the archive, and the CC2 single-model merge needs one model's confidence ≥ 0.7. The ruling governs *confirmation*; merge is currently decided by vote.

## 6.8 One historical note, offered as calibration rather than as encouragement

The last time this exact question was put to a five-model panel — 2026-08-04, genuine paid dispatch, no compelled convergence — all five agreed prose similarity is a dead end. Three concluded no reliable method exists with current signals, because sameness of defect is a causal question and descriptions, similarity scores and word overlap are all correlates of a counterfactual. Two said a method does exist and both pointed at the runnable test: one proposed mutation response signatures (became FELM, refuted at p = 0.71), the other proposed repair intervention (became counterfactual repair, now the ground truth).

**The majority verdict was wrong.** A proposal generated internally that same day — Jaccard over hard STEM tokens — beat all five panel answers on measurement: merged pairs median 0.542 vs distinct 0.000, Mann-Whitney p = 7.5e-9, 97.5% coverage (`9cd8f62`).

Also from that panel: four of five models rejected the prompt's false premise unprompted, and the one that accepted it gave the weakest answer. That is why compelled convergence is retired. Disagreement is preserved here as information, not smoothed to consensus.

Finally, the external position. After nineteen years of duplicate-bug-report research the published state of the art is RR@10 ~0.55–0.65, RR@1 ~0.35–0.42, MAP under 0.50. **There is no published benchmark for deduplicating LLM-generated review findings against a common document.** The archive is more novel than the tier.