# Completed Divergence Study — single root cause, and the scaling architecture

2026-06-03 03:40 BST. Constraint Engineering / CDSFL. Solo forensic study completed to high confidence (founder-directed); supersedes the partial `Project_Divergence_Analysis_2026-06-03.md` framing of "two divergences" — they collapse to one root cause plus one resolved confusion. Panel falsification (`pr`) follows.

## Headline

The project has **one** root divergence, not a mess: **truth came to be decided by discussion (model voting / forced consensus) instead of by tools and the maths model.** Every symptom chased over five months is a face of that single regression. Critically, the *correct* pattern already exists in the codebase for the maths model — the fix is to propagate it, and to drop the consensus machinery. The "more compute should scale" question is **not** a contradiction with the founding paper; it is a granularity/decomposition question, and it is answerable.

## Finding 1 — Timeline (git archaeology, 498 commits, 2026-03-12 → 06-03)

- The review/verdict concept is **day one** (`f3ba111`, 2026-03-12, "3-tier review model with confer escalation").
- Core machinery accreted late March / early April: immune pipeline + convergence detector (`2026-04-02`), insect-brain dynamic management (`04-04`), Bugzilla CLOSED-status FSM (`04-06`), maths model R_k wired at **Exp 37, which converged** (`04-09`).
- **"Compelled convergence" first appears 2026-05-10 — a late desperation patch (5 commits total).** This confirms the founder's recollection: consensus-forcing was reached for in desperation when disagreement became painful, ~2 months in, not part of the original design.
- The CT verification agent was committed `2026-04-02` explicitly as **"investigator not judge."** The tool-grounding intent was there from the start; it drifted into voting in implementation, not by design.

## Finding 2 — The maths model IS used, and the correct verification pattern already exists

- The operational directive (R_k self-assessment, MUST-compute) is appended to **every** model prompt (`reference_runner_v2.py:2538`). Real Exp 42 outputs carry 12–96 R_k/risk tokens per model — the maths model is **not** abandoned (the founder's specific worry is unfounded).
- The runner computes R_k **independently** (`compute_rk`, a pure deterministic detection→resolution→re-injection function) and **validates the model's self-reported R_k against its own recomputation** (`model_rk` vs `recomputed_rk`, `reference_runner_v2.py:4114`).
- **Therefore the founder's ideal pattern — model reasons and self-reports, runner independently verifies as a failsafe against false reporting — already exists, for the maths model.** The drift is that **per-finding claims** (specific code/STEM assertions) never got the same treatment: the CT/B-Cell tool layer fails to ground them ("CT v2: 0 verdicts," "cannot ground claim in source AST"), so they fall to CONFIRM/CHALLENGE voting. There are **two levels of mechanical truth** and only one is wired: convergence-level (R_k, working) vs per-finding (tools, broken → voted).

## Finding 3 — The scaling "contradiction" is dissolved (SymPy/NumPy-verified)

The earlier "Divergence 1" (review-coverage vs decomposition as competing architectures) was a conflation. Verified:
- Marginal coverage Δ(n) = p·(1−p)ⁿ decays geometrically; optimal panel n\* = 4 (ε=0.05) to 6 (ε=0.01) for p=0.5 — matching PAPER §Part XIII's "3–6."
- Monoculture collapse is real: ρ→1 ⇒ D(50)≈D(1)=0.40; low ρ ⇒ D(5)=0.92. Consensus-forcing (high ρ) destroys the heterogeneity premium — the founder's observed "5 ≈ 1."
- **Scale = number of UNITS, not panel size.** 1000 models as 200 units × 5 = 200× throughput; 1000 on one unit ≈ D(6) (wasted). Part XIII's small-n governs the **panel per unit**; scale comes from **decomposition** (number of units). The founder's "problem design / granularity" reframe is mathematically consistent — there is **no contradiction**.

## Finding 4 — Distributed-compute precedent maps directly (BOINC / ZetaGrid)

- **BOINC** (SETI@home etc.) validates work units by **replication + quorum-consensus** ("best 2 of 3") precisely **because volunteer clients are unverifiable black boxes** (hardware faults, malice, crashes) — there is no tool to check a raw computation, so it takes a vote. **This is the exact analogue of CDSFL's voting committee.**
- **CDSFL's core innovation is that it does NOT need the vote** — it injects intelligence *and* tools, so a unit's result can be **verified directly** rather than decided by quorum. The current system regressed to BOINC's consensus while discarding its own advantage. The founder's "we should never have needed a show of hands" is exactly correct: BOINC needs consensus (unverifiable); CDSFL replaces it with verification.
- **ZetaGrid** (2001–2005, largest distributed project of its time, checked 10¹³ Riemann zeros) is the literal precedent for the founder's Riemann example: decompose the zeros into independent **height-range work units**, validate by **recomputation/overlap (not voting)**, Popperian falsification **native** (one misaligned zero disproves the Riemann Hypothesis).

## Finding 5 — Fit-for-purpose: honestly still open for STEM

The maths-model lineage (C(n) → F_n → R_n → recursive → three-phase) is computationally verified (SymPy, Wolfram) and confer-validated for **internal consistency**. But the record is honest (PAPER §627, §914) that **whole-system STEM generality is an open, testable question** (Bench Run 2), not yet proven — current models are coding-optimised generalists, not domain specialists. So "fit for coding AND STEM" is partly supported (structure generalises; 10-domain benchmark) but not established.

## The single root cause, stated once

**Truth-by-discussion replaced truth-by-tools.** The verifier can't ground prose → falls back to voting; models aren't compelled to attach tool-grounding to findings → claims arrive unverifiable → voted on; compelled convergence forces agreement → monoculture collapse (5≈1); models framed as endless bug-hunters → never converge on a built solution. One disease, four faces. And it is a *regression to the BOINC quorum model* in a system whose entire reason to exist is that it can do better (intelligence + tools).

## Recommended fixes (high confidence)

1. **Propagate the proven pattern.** Extend the R_k verification pattern (model self-reports → runner independently re-runs/verifies as failsafe) to **per-finding claims**: a critical finding carries a runnable check; the runner runs it. Remove CONFIRM/CHALLENGE voting as a truth-decider. (This is the correct form of the "layer 2" fix.)
2. **Remove consensus-forcing.** Retire "compelled convergence" as a truth mechanism (keep it, if anywhere, only as a confer-time convenience, never in experiments). Convergence = mechanical exhaustion of genuine tool-surviving findings + checks pass — **not** agreement. Preserve disagreement (low ρ).
3. **Reframe the model directive to the objective.** Models must know they are *building/solving a thing and confirming it works* (with native intelligence + tool-grounded claims), not enumerating every fault forever. The GTA-2 point: tell a model to build, it builds; tell it to hunt bugs, it hunts forever.
4. **Then design the decomposition/recombination layer — the Global Mind.** Architecture: decompose a STEM problem into independent units (BOINC/ZetaGrid work units; for Riemann: zero-ranges, lemmas, proof-strategy branches) → small heterogeneous panel **per unit** (Part XIII n≈3–6) using intelligence → **tool-verify each unit (not vote)** → recombine partial results (Folding@home assembles short trajectories via Markov State Models; ZetaGrid collates ranges). Existing CDSFL mechanics (falsification, the maths model, convergence-as-exhaustion, persistence) are useful **at the unit level**; what is missing is the decompose→distribute→recombine **orchestration** layer.

## Confidence and conflation check

High confidence; no remaining conflation I can identify. The two-divergence framing collapses to: **one root cause** (truth-by-discussion) + **one resolved confusion** (granularity, not contradiction — SymPy-verified). The genuinely **open** items are honest and named: (a) the decomposition/recombination orchestration is unbuilt and non-trivial; (b) multi-solution selection (when several tool-passing solutions exist) needs a criterion and may not resolve until Bench Run 2; (c) whole-system STEM generality is unproven pending Bench Run 2.

## For the panel (`pr`) to falsify, not confirm

Attack these specifically: (1) Is "truth-by-discussion" really the *single* root cause, or am I collapsing distinct failures? (2) Does the R_k "pattern already exists" claim actually transfer to per-finding claims, or is per-finding verification fundamentally harder (un-toolable claims)? (3) Is the BOINC-quorum analogy sound, or does multi-model *reasoning* (unlike raw compute) genuinely need a consensus step that tools can't replace? (4) Is the decompose→tool-verify→recombine architecture viable for a problem like Riemann, or does intelligence-bearing decomposition have failure modes BOINC never faced (e.g. sub-problems that aren't independent, recombination that isn't mechanical)?

Written under CDSFL note standard v1.2 (14 May 2026).
