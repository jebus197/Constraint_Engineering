# Ouroboros and Self-Improvement — Full Assessment

2026-07-08 · branch `exp39-experimental` · founder-ordered assessment ahead of Experiment 43

Two read-only code+doc audits (file:line-referenced) establish the current state of the ouroboros cell, its original design intent across three generations, the state of the self-improvement machinery, and an evidence-grounded judgment on the "first light" aspiration. Part 7 is a staged, integration-test-gated fix proposal. Part 8 lists documentation divergences requiring founder decision.

## 1. Summary of findings

- The **live ouroboros cell fetches 500-character abstracts, discards them, wires to nothing, and contributes a hardcoded zero to the convergence maths.** It is not a broken feature; it is unbuilt construction on top of working plumbing.
- The word "ouroboros" names **three different design generations**; the founder's "original full model" is the 12 April self-improvement loop, which — critically — **already forbade autonomous writeback and required cross-path verification to prevent self-confirming loops.**
- `apply_fixes_back` writes a **sandboxed, gated, default-off working copy, never live source.** No autonomous self-modification path exists, by design.
- **The "first light" / recursive-self-improvement-to-negligible-human aspiration is not reachable by completing what exists, is contrary to the design's own predictions, and was already disconfirmed by the project's own experiment** (`EXPERIMENTAL_RESULTS.md:876`). The achievable and designed target is *minimal-HIL* (human as rare final falsifier). The scaling dream lives only in architecture (B), which was never built or modelled — genuinely open, but a different project.

## 2. Ouroboros — verified current state (`bench/ouroboros_cell.py`, 710 lines)

- **Fetches abstracts only.** The live path `run_between_rounds` → `_fetch_metadata` (`:179`, `:366`) returns title + authors + abstract **truncated to 500 chars** from arXiv (`:434`), Semantic Scholar (`:456`), OpenAlex (`:518`). No PDF download or text extraction exists anywhere in the file.
- **The full-text chain is dead code.** `full_text_for_doi` (`:590`) and `_unpaywall_oa_pdf` (`:576`) are called only by themselves and a test; the live path never invokes them; and even they return a **URL string, not fetched content**. CORE is named in docstrings but has no fetcher.
- **It discards what it fetches.** `_generate_candidates` (`:608`) ignores the fetched metadata argument entirely and emits placeholder strings (`"Shadow candidate for target: {target}"`, `:631`) with `source_diversity=0.0`.
- **Output terminates in shadow logs.** Single call site `_run_shadow_cells` (`reference_runner_v2.py:3518`), run after the main pipeline ("zero verdict effect", `:5875`). The return value becomes `shadow_data["ouroboros"]` (counts only) and a disk log; `shadow_cell_data` reaches `round_data["shadow_cells"]` telemetry (`:6302`) and nothing else. It never reaches `_build_prompt` or model dispatch. **The loop-close does not exist.**
- **The maths ignores it by hardcode.** The live R_k close runs `compute_rk_with_eta_channel` with **`c_ext=0.0, nu_k=0.0` hardcoded** (`reference_runner_v2.py:4930`, "F2 identity mode"), so the entire literature/novelty channel contributes identically zero to convergence. The prompt even instructs models to "set c_ext = 0 explicitly" if they didn't do their own search (`:5449`) — novelty is model-self-reported, independent of ouroboros.
- **Stage-6 connection is weak and logged-only.** `dm/_shadow_stage6.py` reads only `source/status/results_count` from the ouroboros log (`:444`), not the abstract text; computes `c_ext` and `nu_k_proxy`; and writes them to telemetry. They never enter `q`, `R_k`, or any gate.
- **Tests confirm by omission.** `test_ouroboros_query_quality.py` pins the real query-cleaning; `test_shadow_stage6_calibrator.py` pins the calibrator's SymPy-verified internal maths; `test_ouroboros_fulltext.py` mocks the dead full-text path. **Nothing tests full-paper retrieval or literature-reaching-a-model, because neither is built.**

Founder's two recollections — both **confirmed**: (A) fetches headers/leads not full papers; (B) feeds nothing back to the models.

## 3. Ouroboros — original design intent (three generations)

1. **Literature-novelty cell** (current `README.md:259`, `ARCHITECTURE.md:134`) — the narrow, shipped meaning; the hollow one in Part 2.
2. **Self-review of the system's own code** (`Exp38_Ouroboros_Findings_2026-04-11.md:1`, "Ouroboros: Self-Review of Reference Runner") — the panel turned on the project's own source. **This one is genuinely running:** Exp 41/42/43 target `dm/_convergence.py`, `composer.py`, `macrophage_cell.py`. Bounded, human-gated, real. This is the honest core of the self-improvement story.
3. **The "snake eats tail" self-improvement loop** (`Macrophage_Ouroboros_Split_2026-04-12.md:24`) — the fullest vision: fetch external evidence → emit candidate claims with full provenance → a B-Cell verifies via a **strictly different evidence path** (`:37`, *"prevents epistemic closure / self-confirming loops"*) → Policy-Engine gates → adopt. **Design-critical:** `:53` — *"No automatic writeback from fetched evidence into live config."* Even the fullest original vision was gated, cross-verified, and human-anchored, precisely to prevent a self-confirming spiral.

## 4. `apply_fixes_back` — no autonomous self-modification exists

`_apply_back_setup` (`reference_runner_v2.py:2899`) creates a **per-run working copy; the repo file is never modified** (`:2900`). Promotion is gated on AST-parse + the **full canonical test suite green** in a throwaway clone (`_apply_back_gate`, `:2944`), only for `CLOSED` findings, and is **default-off** (`:370`). Exp 41 ran it off deliberately (static target). A human folds results back to the repo afterward. There is no autonomous write-to-live-source path anywhere in the design.

## 5. The self-improvement judgment (grounded in the project's own record)

The design predicts **bounded convergence, not takeoff**: `EXPERIMENT_DESIGN.md:130` ("self-improvement ... bounded by the diminishing returns curve"); `PAPER.md:979` ("converge rather than explode"). The one experiment that tested self-improvement **disconfirmed it**: `EXPERIMENTAL_RESULTS.md:876` — *"The self-improvement prediction is not confirmed ... better described as environment-mediated improvement — CDSFL improves the input to each model — rather than model self-improvement."* No document contains "first light" or a "critical mass" end-state.

**HIL is retained by design; minimal-HIL ≠ zero-HIL.** `README.md:411`: the HIL is "the final decision authority ... No panel finding is auto-applied to live artefacts without HIL approval." The chair is defined "by function rather than by species" — a *non-human* occupant is contemplated, the *role* never removed. The two HIL-reduction mechanisms (exception-based escalation; per-finding immune quality-gating) reduce HIL *volume*, not the role.

**Judgment:** "first light" as recursive self-improvement to discountable-human is not reachable by finishing architecture (A), is contrary to the design's predictions, and was already falsified by the project's own experiment. The reachable, designed, worth-finishing target is **minimal-HIL: the founder as rare final falsifier, not constant hand-holder** — a genuine and novel contribution (a multi-vendor falsification panel converging on tool-grounded verdicts with a mathematical stopping rule) that stands independent of ouroboros. This is not my opinion over the founder's; it is the project's own record over the current aspiration.

## 6. The (A) vs (B) fork (`Project_Divergence_Analysis_2026-06-03.md`; `PAPER.md` Part XIII)

- **(A) Many models reviewing one artefact — built, papered.** Value is *better, not faster*; saturates at **n ≈ 3–6** with steep diminishing returns; monoculture collapse at ρ=1 gives `D(n)=D(1)`. "1000 reviewing one thing ≈ 5" is the model's own prediction — this is mathematically the wrong place to look for scaling.
- **(B) Distributed problem-decomposition at scale — the real "Global Mind": never designed, unbuilt, unmodelled.** Honest caveat: (B) is **not refuted, just never attempted** (Part XIII is a review-coverage model; it may be silent on (B), not against it). If the scaling dream lives anywhere, it lives in (B) — a new architecture and research effort, not a fix to this arc.

## 7. Fix proposal — enable ouroboros to its *April* spec (staged, each integration-test-gated)

Honest framing first: this makes the review **better-informed** (external-literature grounding for novelty). It **does not** move the needle on first light or autonomy. It is a bounded capability add to architecture (A), built to the founder's own gated, anti-closure April design.

- **Stage 0 (housekeeping).** Fix the `_last_shadow_log` early-return bug (`ouroboros_cell.py:209`); reconcile the doc divergences in Part 8. *Gate: existing tests green.*
- **Stage 1 (full-text retrieval).** Add a body fetch+parse behind `full_text_for_doi`: Unpaywall OA PDF → download → extract text (PDF→text), hard-timeout-bounded, Sci-Hub off by default, cite the original DOI. *Gate: a test that a known-OA DOI yields extracted body text, not a URL.*
- **Stage 2 (content-derived candidates).** Rewrite `_generate_candidates` to build candidate claims from the fetched abstracts/bodies (not placeholders), with real `source_diversity`. *Gate: a test that a fetched paper produces a candidate claim referencing its content.*
- **Stage 3 (the loop-close, shadow→live).** Inject fetched literature into `_build_prompt` for the next round, gated. *Gate (the anti-shadow-drift rule): an integration test proving a model prompt contains a fetched abstract AND a resulting finding cites it — nothing counts as "done" until a fetched paper changes a real decision.*
- **Stage 4 (the April anti-closure guard).** A fetched candidate must be verified by a B-Cell via a **different evidence path** before adoption, PE-gated (`Macrophage_Ouroboros_Split_2026-04-12.md:37`, `:53`). *Gate: a test that a candidate failing cross-path verification is rejected, not adopted.*
- **Stage 5 (c_ext live).** Replace the hardcoded `c_ext=0, nu_k=0` (`reference_runner_v2.py:4930`) with Stage-6's live estimates, behind the two-sided gate. *Gate: a live run where a non-zero c_ext demonstrably changes a verdict or score — with a null-test that it does not distort a clean run.*

**Sequencing recommendation vs Exp 43:** Exp 43 (`macrophage_cell.py`) is software-domain and has no `_ouroboros` in its config, so ouroboros is *moot* for it. Building ouroboros is best done **after** Exp 43 (it gets genuinely exercised on the bio/STEM experiments, Exp 47+), so Exp 43 stays directive-identical to Exp 42. The founder previously asked for the assessment *before* Exp 43 — delivered here; the *build* is best deferred.

## 8. Documentation divergences (founder decision)

- **D-doc-1:** `MATHEMATICAL_APPENDIX.md §8.7` (`:1768`) still describes ouroboros as the pre-split pipeline monitor ("macrophage mode / microglia mode"), a role the 12 April split moved to the Macrophage cell — contradicting `ARCHITECTURE.md:134-140`. **Stale canonical maths; recommend reconcile.**
- **D-doc-2:** "ouroboros" scope drifted across three generations without the docs reconciling. Recommend a one-paragraph note in ARCHITECTURE/GLOSSARY naming the three senses.
- **D-doc-3:** the consensus-voting drift (`Project_Divergence_Analysis_2026-06-03.md:37`) still undercuts even (A) where the tool layer fails to ground a claim; the CONFIRM-only falsifier gate is the fix and is largely built, but the layer-2 verifier is still open (task #7). Recommend confirming this is closed before any (A)-coverage claim is published.

These are flagged, not fixed — canonical/maths docs await founder direction before edit.

Written under CDSFL note standard v1.2 (14 May 2026).
