# Burst Reasoning and the "Models as Neurones" Hypothesis

**Date:** 7 April 2026, ~03:24 BST. Experiment 36 Round 9 processing.

## The Observation

During Exp 36, the ITC restart_fresh mechanism produced a dramatic novelty burst. R8 generated **21 novel canonical findings** from a codebase that had already been reviewed for 7 rounds. All 5 models contributed. This is the biggest single-round discovery since the blind R0. The burst was triggered by ITC restarting all 5 models with fresh context after detecting degradation.

## The Claim

ITC restart_fresh produces "burst reasoning" — a form of attentional reset that generates novel, productive insights by freeing models from accumulated context bias. This is analogous to neuronal refractory periods and sleep consolidation in biological brains.

## P-Pass (Falsification)

**Data pattern:**
- R4 (post-change_focus): novel=1, OPEN=12. Models in steady decline.
- R5-R6 (first restart_fresh wave): novel=6, 7. Models found genuinely new things.
- R7 (between bursts): novel=2. Brief plateau.
- R8 (second restart_fresh wave, all 5 models): novel=21. Biggest discovery since R0.
- R9 (post-burst): novel=7. Elevated but declining.

**Falsification attempt 1:** Are the burst findings genuine or inflated by parser artifacts? 86 canonical from 420 lines (~1:5 ratio) is very dense. However, the dedup engine classified 21/29 raw as novel (72% novelty rate). In R1, 23 raw had 10 novel (43%). Fresh models have a *higher* novelty rate, not just more volume. The dedup has been calibrated across prior experiments.

**Falsification attempt 2:** Would the same findings have been found without restart, just later? This is the hardest to falsify. Possibly — but context accumulation creates **attentional fixation** where models keep circling the same findings rather than exploring unexplored regions. The restart breaks the fixation. Whether those findings would "eventually" emerge is moot if the attentional fixation means they never would in practice.

**Verdict:** Survives P-pass. The burst pattern is real and measurable. The mechanism (attentional reset via context clearing) is plausible and consistent with known LLM behaviour (context pollution, recency bias, prompt anchoring).

## Biological Parallels

- **Synaptic fatigue:** Neurons that fire repeatedly become less responsive. Restart_fresh is analogous to a refractory period — temporary silence that restores sensitivity.
- **Stochastic resonance:** In biological neural networks, noise (random variation) can enhance signal detection. Fresh model instances introduce variation in attention patterns that helps them "see" what fatigued instances can't.
- **Sleep consolidation:** During sleep, the brain replays and restructures learned patterns. Restart_fresh doesn't replay, but the fresh context forces the model to reconstruct its understanding from scratch, which can surface different structures.

**CDSFL functional analogues:**
| Biological System | CDSFL Component |
|---|---|
| Central nervous system | Insect brain relay/blackboard |
| Immune system | NK, B Cell, DC, Helper T, CT, RT pipeline |
| Endocrine system | Pacing signals, health monitoring |
| Autonomic nervous system | ITC adaptive recovery (change_focus/restart_fresh/strip_context) |
| Attentional gating | change_focus (redirect attention), restart_fresh (reset attention) |

## Extrapolation

**(a) What generalises:** The principle that heterogeneous agents with periodic attentional resets, operating within a shared state machine with immune-like quality control, can produce emergent discovery that exceeds any single agent's capacity. This is not just "run 5 models" — it's a system that manages model attention as a resource.

**(b) Boundary conditions:** The burst effect depends on the discovery space being rich enough to have multiple exploration paths. For a trivial problem, there's nothing for the burst to find. For an infinitely complex problem, the bursts would never converge. The sweet spot is problems with moderate complexity and multiple valid analysis angles.

**(c) New falsifiable questions:**
- Is there an optimal restart frequency? Too frequent = no time to build understanding. Too infrequent = attentional fixation.
- Does the burst magnitude scale with the number of models restarted simultaneously? (R8 restarted all 5, R5 restarted 3 — R8 had 3x the novelty.)
- Would a "partial restart" (keeping some context, clearing the rest) produce more targeted bursts?
- **[SPECULATIVE]** Could the restart_fresh mechanism be deliberately *scheduled* rather than reactively triggered by ITC? A rhythmic restart pattern might be more efficient than waiting for degradation.

**(d) The deepest implication:** The "models as neurones" vision is being demonstrated live. R8 isn't just a good round — it's evidence that **interaction architecture matters more than individual model capability**. The same models, in the same configuration, with the same code, produced dramatically different results based solely on whether their attention was reset. That's not a model property. That's a system property.
