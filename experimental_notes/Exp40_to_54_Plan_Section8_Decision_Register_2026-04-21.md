# Five open founder decisions for the Exp 40–54 arc

21 April 2026, 20:38 BST.

CDSFL, the Constraint-Driven Synthesis and Falsification Loop, is the methodology under test in this project: a Popperian arrangement in which several frontier models produce, critique, and attempt to falsify technical claims under a shared rule set. Experiments 40 through 54 are the fifteen-experiment arc that tests how CDSFL behaves across a widening set of technical domains.

## Summary

With all pre-launch fixes now landed and the second round of plan review closed, five decisions remain open for the founder. None of them blocks the launch of Experiment 40; each comes due at a concrete later trigger in the arc. This note names the five in plain English so that the founder — or a third party returning to the plan weeks from now — has each decision, its stake, and its trigger without needing to scan the whole plan document.

## What "pre-launch" meant, and why it is now closed

Before Experiment 40 could start, the panel of five models that governs this work (Claude Opus 4.6, Codex GPT-5.4, Gemini 3.1 Pro, ChatGPT GPT-5.4, and DeepSeek Reasoner) flagged three code-level fixes, labelled F1, F2, and F3 in the plan. A fourth item, F4, is a closure-state labelling standard that had landed earlier in the arc and is documentation-only; it is not a pre-launch code fix.

- **F1** is an allow-list correction inside the project's SymPy sandbox — the constrained Python environment in which symbolic-mathematics checks run inside the reasoning loop. Before the fix, the sandbox was configured so aggressively that ordinary arithmetic terms did not resolve, and every SymPy verdict fell back to "uncertain". The allow-list extends to the terms the reasoning loop actually uses while still blocking the broader Python namespace, so that admissibility and verdict checks do not silently no-op.
- **F2** activates an identity-mode wrapper around the runner's core recurrence call, the function that carries the reasoning-loop state forward one step. At identity parameters the wrapper reduces mathematically to the bare call, verified across a 567-case pytest grid and a wider 1,620-case pre-verification. The purpose of the activation is to make a later, non-identity rewrite land on already-instrumented code rather than on a fresh code path. This is the fix item cross-referenced in the plan as Item 1.E.10, which is a plan-item reference and not a numerical magnitude.
- **F3** adds — does not remove — a debug-time assertion that the wrapper's identity-mode output matches the bare call within a tight tolerance. It is gated on an environment variable so it has no effect in production. Its purpose is to catch future refactors that shift the identity-mode parameters, a regression that would otherwise be silent.

All three landed on 21 April 2026, and the full local test suite — 1,255 tests, of which 1,121 do not depend on network access — passes.

The panel also flagged three shadow-mode components, labelled K, L, and M. A shadow component is one that runs alongside live code and receives the same inputs but never affects the outcome, so its behaviour can be audited before it is promoted to live operation. K, L, and M had their audit logging enriched on the same day. Whether they graduate to live operation is bound by a non-distortion check that Round 2 folded into the shadow-promotion policy, not by any of the five founder decisions below. Each of K, L, and M flips to live operation only at its specialist experiment — K at Experiment 51, L at Experiment 52, M at Experiment 53 — and only if its shadow-audit evidence shows no distortion of the live output during its shadow period.

## The second round of plan review, and what it settled

The panel's first plan review had left six questions where the five models split. The second round, held on 21 April 2026, used a discussion discipline called **compelled convergence**: in a **star-topology** conversation, where the working-session director acts as the hub and no model talks directly to any other, each model must either yield to the majority or defend its held position until the panel arrives at one agreed answer, rather than handing the founder a menu of differing opinions. Five of the six questions closed with unanimous or near-unanimous positions. The sixth — whether to fresh-run the first cell of Experiment 54 or test an archived run first — carried forward as decision 2 below.

## The five open decisions

### Decision 1. Approval to launch Experiment 40

All pre-launch work is now complete. The next step is the founder's go or no-go.

- **Trigger.** This plan review.
- **Stake.** Whether the fifteen-experiment arc begins now, or waits for further preparation.

### Decision 2. For Experiment 54's first cell, run fresh or test the archive first

Experiment 54 is the capstone integration experiment. Its first cell, Cell A, is the factorial's baseline configuration, with both the §17 feedback directive and the §18 divergence directive off. Cell A tests whether the archive produced across Experiments 36, 37, and 38 — which ran under that same baseline configuration — remains valid under the current runner code. The project's standing framing for the intervening evolution is the **ouroboros** principle: the methodology itself has been falsifying and updating itself through every experiment between the archive and today, so the instrument that produced the archive and the instrument checking it are not strictly the same. The panel's technical label for the resulting concern is a **version confound** — a difference in the code under which the archived result was produced versus the code under which it is being checked. Whether that confound is decision-changing is what the panel was asked to adjudicate; the split persists three-to-two on operational ordering (archive-integrity check first with fresh-run fallback, versus fresh-run unconditionally). Both positions accept that the version-level difference is real; they differ only on how to handle it. The plan's three-layer Cell A strategy — integrity check, fresh-run fallback, and a sensitivity-bounding check that measures how much any given result depends on the archive versus the fresh run — is operationally compatible with either resolution.

- **Trigger.** Experiment 54 entry, after Experiments 40 through 53 complete.
- **Stake.** Roughly a week of compute, and whether the archived results can be reused as reference.

### Decision 3. Construction of the target articles for Experiments 47, 51, 52, and 53

Four of the later experiments test CDSFL against technical articles in specific domains — physics for Experiment 51, and three other domains for 47, 52, and 53. The panel unanimously rejected the option of adapting existing third-party articles, and instead chose **minimal native synthesis**: short target modules, roughly fifteen to twenty-five thousand characters per domain, written for the purpose. These must be drafted ahead of each experiment.

- **Trigger.** The entry to each of Experiments 47, 51, 52, and 53. Experiment 47 is the first.
- **Stake.** The target articles control the difficulty and shape of each experiment.

### Decision 4. Wiring the admissibility-parser preflight into the Experiment 40 launcher

A preflight check, called **Gate C**, verifies that incoming claims parse correctly before the reasoning loop receives them. The panel folded a Codex-proposed refinement of this preflight into Gate C, rather than treating it as another code-level fix item. It needs to be wired into the launcher for Experiment 40 before the first run.

- **Trigger.** Experiment 40 launcher integration, prior to launch.
- **Stake.** Catching malformed claims before they enter the loop, where they are harder to diagnose.

### Decision 5. Freezing the admissibility, severity, and tier thresholds before Experiment 54

Experiment 54 is a factorial experiment that varies two treatments across its four cells (A, B, C, D). The panel agreed unanimously that the thresholds controlling which claims are admitted, how severe findings are rated, and how they are tiered must be identical across all four cells and must not be re-tuned during the factorial. They need to be frozen at specific values before Experiment 54 starts.

- **Trigger.** Between the close of Experiment 53 and the entry to Experiment 54.
- **Stake.** Whether the factorial contrasts are interpretable.

## What to review next

Decisions 1 and 3 are approval-and-execution gates: they do not need more panel work, they need the founder's call, and — for decision 3 — a short drafting effort per domain. Decisions 2, 4, and 5 are already scoped in the plan and need no additional review before their triggers arrive.

A future revision of the plan may fold the now-resolved pre-launch items from the plan's section 5 and the open decisions listed here into a single decision-status register; that fold is out of scope for this note.

Written under CDSFL note standard v1 (21 April 2026).
