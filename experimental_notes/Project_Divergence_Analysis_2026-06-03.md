# Project Divergence Analysis — where CDSFL drifted from its founding paradigm

2026-06-03 02:50 BST. Constraint Engineering / CDSFL. Solo forensic analysis (founder-directed); conclusions pending an adversarial panel falsification round and a git/experiment timeline trace.

## Summary of the finding

Two distinct divergences separate the project's current behaviour from the founder's "Global Mind" vision, and they are not the same kind of thing. One is a **conflation present at the foundation** (the scaling vision describes a different architecture than the one the paper models and the system builds). The other is an **implementation drift** that violated the project's own stated truth-deciding rule. Critically, the founder's instinct that "design by committee" is the wrong paradigm is not a new realisation — it is the project's own founding principle, stated in the README and warned about in the paper's own mathematics. The vision was not lost in the theory; it was lost in the implementation.

## The original paradigm, in the founding record's own words

Three load-bearing statements anchor what CDSFL was designed to be:

1. **PAPER §Part XIII (Distributed Compute Coverage Model)** — the project's own formal model of multi-model scaling — predicts:
   - "Optimal n* should be small (typically 3–6 for moderate thresholds) because the diminishing returns curve is steep."
   - "Diminishing returns. Δ(n) is monotonically decreasing. Early architectures add the most coverage; later ones contribute progressively less."
   - Property 4: "poor orchestration allows convergence toward consensus, raising effective ρ and reducing coverage." Property 3: "Monoculture collapse. When ρ = 1, D(n) = D(1) for all n."

2. **README §8 (From Methodology to Architecture)** states the truth-deciding rule in one sentence: "The system does not rely on model consensus to decide what is true. It relies on tools, and when tools cannot decide, on the HIL."

3. **README §9** defines the source of value: "epistemic diversity as compute" — disagreement between *unlike* agents, "treated as information rather than noise."

The founding paradigm is therefore: a **small panel (n ≈ 3–6) of heterogeneous models, whose value is coverage through disagreement, where tools decide truth and the human decides only when tools cannot.** Diminishing returns are predicted, not pathological. Consensus is named as the mechanism that destroys the value (ρ → 1, monoculture collapse).

## Divergence 1 — vision conflation, present at the foundation

The current founder framing ("5 should beat 1, 1000 should beat 5, more compute = faster, else something is broken") describes a different architecture than CDSFL was designed as. Two distinct propositions have been conflated:

- **(A) Heterogeneous review / falsification of a single problem** — what the paper models and the system builds. Its value is *better* (more defect classes caught), not *faster*, and PAPER §Part XIII says it **saturates at n ≈ 3–6** with steep diminishing returns. Under this model, 1000 models reviewing one artefact is *expected* to be no better than 5, and slower. That is the model's prediction, not a malfunction.
- **(B) Distributed problem decomposition** — split a hard problem into many sub-problems, solve in parallel, recombine. This scales with compute; this is "1000 beats 5"; this is the "Global Mind." The paper does **not** model it and the system does **not** implement it. It is the dream behind the project, never designed.

The founder's computer-science intuition ("more compute → better/faster outcomes") is correct — but it holds for *decomposable* problems (B), not for *redundant review* (A). CDSFL is (A). The gap has existed since the paper, which is why no single experiment "broke" it: there was nothing to break; it was a conflation, not a regression. **This is the conclusion most in need of adversarial falsification** — specifically, the claim that PAPER §Part XIII's small-n result (a defect-detection *review* model) speaks to the *decomposition* case at all. It may be silent on (B) rather than contradicting it; the honest reading is that (B) is *unmodelled and unbuilt*, not *refuted*.

## Divergence 2 — implementation drift that betrayed the stated rule

Within architecture (A), the implementation drifted away from its own rules — the exact failure surfaced in the 2026-06-02 verifier investigation:

- README §8 says **tools decide, not consensus.** The experiment pipeline was observed resolving findings by CONFIRM/CHALLENGE model votes — a committee — because the tool layer (passive, post-hoc grounding of prose findings) fails to decide ("CT v2: 0 verdicts," "cannot ground claim in source"). The committee is not a design choice; it is the **fallback the system drops into when its tool layer cannot ground a claim** — a direct violation of the one sentence that defines how truth is decided.
- PAPER §Part XIII says **consensus raises ρ → monoculture collapse → D(n) ≈ D(1).** The system accreted consensus-forcing machinery (voting, reconciliation, "compelled convergence"). Forcing agreement is precisely the mechanism the paper says collapses 5 back toward 1. The observed "negligible benefit of 5 vs 1" is **monoculture collapse caused by orchestration that pushes models toward agreement instead of preserving their disagreement.**

The drift mechanism matches the founder's own diagnosis: gradual accretion through local problem-solving (immune voting, the kappa metrics, the gamma gate, reconciliation, the hardened gate), each layer justified on its own, while the stack as a whole moved from "tools decide, disagreement is the compute" to "models vote and we force them to agree." No global re-check against the founding paradigm was performed at any step — the "minutiae trap."

## The Global Mind is achievable, but it is a different machine

Architecture (B) is achievable and valuable, and the founder's intuition about it is sound. It rests on exactly the two properties this analysis surfaces:

1. **Claims settled by tool evidence, not discussion** — so an added model contributes coverage rather than an argument every other model must process. Discussion-based settlement is what makes the current system scale super-linearly in cost (the committee); tool-based settlement is constant per claim.
2. **Problem decomposition, not redundant review** — so an added model does different work rather than repeating the same review.

With both, "more models → faster/better" becomes true, because the system is then distributed *computation*, not distributed *deliberation*.

## Recommended fixes

1. **Restore architecture (A) to its own stated rule — tools decide.** The 2026-06-02 "layer 2" work, done correctly: critical findings carry a runnable artefact (a failing test / assertion / check); the runner runs it; the committee is removed. Immediate, scoped, and exactly README §8.
2. **Stop forcing consensus — preserve disagreement (low ρ).** Re-examine "compelled convergence" and the voting / reconciliation machinery against PAPER §Part XIII property 4. Anything pushing models toward agreement is eroding the coverage premium.
3. **Then deliberately design architecture (B)** — decomposition with tool-grounded claims as the scalable unit — as the actual Global Mind, built on a falsification core that settles claims by tools, not bolted onto the review engine.

## Status of this session's concrete work (context)

- Verifier **layer 1** (misclassification → opinion-voting) fixed and committed (HEAD `8f1c305`, local; code-path guard in `bench/immune_agents.py`; 155 focused tests pass).
- Verifier **layer 2** (CT cell runs but yields 0 parseable verdicts; B-Cell cannot ground in source AST) found, located, NOT fixed — this is the "tools decide" mechanism and the substance of fix 1 above.
- Exp 42 launched on the 5-model panel, round 0 confirmed layer 1 works and layer 2 remains, then stopped per the founder's "pause if CT yields 0 verdicts" gate. Run dir preserved.

## Open items for the next step

- Trace the git/experiment timeline to locate *when* the consensus/voting machinery accreted (validates or refutes divergence 2's "gradual drift" account).
- Put this entire thesis to the neutral panel to refute (founder-chosen "solo first, then panel-check"). The panel's brief is to break the (A)-vs-(B) distinction and the monoculture-collapse attribution, not to confirm them.

Written under CDSFL note standard v1.2 (14 May 2026).
