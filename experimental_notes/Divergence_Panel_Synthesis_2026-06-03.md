# Divergence Panel Review (pr) — synthesis and the path forward

2026-06-03 05:20 BST. Constraint Engineering / CDSFL. Six-model panel review of the completed divergence study (`Divergence_Study_Complete_2026-06-03.md`), run WITHOUT compelled convergence (consistent with the finding that consensus-forcing is the disease). CC1 participated and synthesizes. Panel: CC2 Opus 4.8, Codex GPT-5.5 (OpenRouter), Codex CLI (CX2), Gemini 3.1 Pro, ChatGPT GPT-5.5, DeepSeek V4 Pro. Logs: `bench/logs/confer_divergence_pr_2026-06-03/`.

## Verdict

**6/6 SOUND-WITH-CAVEATS.** The single-root-cause diagnosis ("truth-by-discussion replaced truth-by-tools") is endorsed as directionally correct and central. The six models — with no compulsion to agree — **independently converged on the same forward architecture** while sharpening the diagnosis in three ways that materially improve the fix. Notably, the panel converging by itself is evidence *for* the thesis: when the question is well-posed and tool-checkable, heterogeneous models agree without being forced.

## Three sharpenings the panel added (all adopted)

**S1 — The root cause is more precisely a *semantic gap*, not a policy choice.** The system did not "choose" voting; it **permitted models to emit natural-language claims that no tool can parse**, which *forced* the fallback to an LLM-as-judge vote (Gemini, echoed by all). The fix is therefore not merely "delete the vote" but the stronger, actionable rule: **no claim exists unless it carries the executable falsifier that would refute it** (the test, the proof obligation, the certificate). This is the precise form of "active grounding": findings arrive with their own check attached; the runner runs it. This *subsumes* "delete the vote" — once every claim is tool-checkable, there is nothing left to vote on.

**S2 — Tools have a real boundary; the irreducible core is HIL, never a vote (F2, strong consensus).** The R_k verification pattern transfers only *partially*. R_k is closed-form (trivially recomputable); many genuine, important STEM findings need a *bespoke* harness, and some ("this design is fragile," "this approach won't generalise") resist mechanical decision entirely. So the prescription is: **tools decide the decidable; the genuinely-undecidable goes to HIL** — exactly the founding rule ("tools, and when tools cannot decide, the HIL"). The honest design keeps the un-toolable set *small* (most material findings are toolable) and routes it to a human, not a panel ballot.

**S3 — Deliberation is load-bearing for SEARCH, not for TRUTH (CC2's distinction — the cleanest reconciliation).** Multi-model disagreement is genuinely valuable for **hypothesis generation** — expanding *what* to check, the coverage premium (low ρ). It is *not* valid for **truth determination** — *whether* a claim holds, which tools decide. This reconciles "preserve disagreement" with "tools decide": **disagreement informs what to check; tools decide if it is true.** Keep the heterogeneous generation; remove the truth-vote.

## Design convergence — the scaling architecture (D1–D3, strong agreement)

The panel and CC1 converged on a single shape for the "Global Mind" / decomposed-STEM layer:

- **Unit of work = a conjecture-with-checkable-implications** (CC2), a *typed* WorkUnit with explicit preconditions, deliverables, validators, dependencies, and residual-risk (R_k) accounting (CX, ChatGPT). Not "solve RH" handed to 500 models — a **DAG of typed, checkable units**.
- **Per unit:** a small heterogeneous panel (Part XIII n≈3–6) *generates and falsifies* using native intelligence; each unit is **tool-verified, not voted**.
- **Recombination operator = the DAG itself.** Units compose along dependencies; R_k propagates up the graph; the **root claim converges when its residual risk is below threshold and every critical node is tool-settled.** This generalises ZetaGrid (a *flat* DAG of independent zero-ranges, conjunction-recombined) to proof-search (a *deep* DAG with dependencies). Folding@home's Markov-state recombination is the analogue for assembling many partial results into global behaviour.
- **Selection among multiple valid solutions (D2, unanimous form): lexicographic / Pareto dominance, never a ballot.** Order: (1) hard validity — passes the proof kernel / exact test / certificate; (2) lowest residual risk R_k; (3) coverage / generality; (4) simplicity. A genuine tie on all tool-grounded criteria → HIL (rare). This directly answers the founder's "five models, five solutions" problem.
- **Reusable vs domain-specific (D3, consensus):** *Reusable, domain-independent* — Popperian falsification (with executable falsifiers attached), the R_k risk model (residual risk per node, swap the tool suite per domain), convergence-as-exhaustion, persistence / Merkle sealing, the HARD/SOFT classification, the HIL role. *Coding-review-specific, do not carry over blindly* — the ruff/mypy/bandit/crosshair tool suite (replace per domain), the CT-agent's code-AST grounding (needs a per-domain analogue), and above all the **"review one artifact" framing** (replace with decompose-distribute-recombine).

## What this means, plainly

The founder's instincts were right on every substantive point, and the panel confirms it: the committee was never intended; consensus-forcing destroys the coverage value; the "more compute" question is granularity/decomposition, not a contradiction; the maths model is a tool and is in use; the runner-as-failsafe pattern already exists (for R_k) and should be propagated. The single correction the panel makes to *CC1's* framing is upward in precision: the disease is best named as **"claims were allowed to exist without their falsifiers,"** of which "truth-by-discussion" is the downstream symptom.

## Recommendations (panel-validated, ordered)

1. **Enforce the falsifier-carrying rule.** Change the finding schema + directive so a critical finding is *inadmissible without an attached, runnable falsifier* (test / proof obligation / certificate). The runner runs it; result decides. This is the correct, generalised "layer-2" fix and it dissolves the committee at the source. (Note the boundary, S2: un-toolable claims are explicitly routed to HIL, not voted.)
2. **Split generation from adjudication.** Keep multi-model, heterogeneous *generation* (disagreement = coverage). Remove multi-model *voting* on truth. Retire "compelled convergence" from experiments. Convergence = mechanical exhaustion of genuine, tool-surviving findings — not agreement.
3. **Reframe the directive to the objective** (build/solve a robust thing and confirm it, not enumerate faults forever).
4. **Prototype the decomposition layer on a contained target before scale.** Build the typed-WorkUnit DAG + lexicographic selection + R_k propagation on a *small* problem first (even the CDSFL PoC itself, or a bounded maths lemma), verify it converges by tools not votes, then scale the number of units. ZetaGrid/Folding@home are the templates; the novelty is intelligence-bearing, dependency-aware units with tool validation replacing quorum.

## Open and honest

- The decomposition/recombination orchestrator (the DAG engine) is unbuilt and is the genuinely novel, non-trivial work. The panel agrees on its *shape*; building it is the next real engineering.
- Some findings are irreducibly un-toolable → HIL. The claim is that this set is *small*, not empty. Bench Run 2 (frontier STEM problems) is the test of how small.
- Whole-system STEM generality remains unproven (PAPER §627) pending that run.

## Immediate next brick

The falsifier-carrying rule (recommendation 1) is the concrete restart of the stalled "layer-2 / tools-decide" work, now with a panel-validated specification: every critical finding must arrive with its executable check, or be explicitly routed to HIL. That is the calculator's missing piece — the step that makes "problem in → solution out" mechanical.

Written under CDSFL note standard v1.2 (14 May 2026).
