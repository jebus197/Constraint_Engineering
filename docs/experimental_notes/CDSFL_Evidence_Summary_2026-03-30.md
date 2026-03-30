# CDSFL Evidence Summary: Demonstrated Capabilities Across Experiments 0–17

**Compiled:** 30 March 2026

---

## Overview

The CDSFL project ran 18 experiments over 16 days (14–30 March 2026). It involved 5 frontier AI models from 4 independent vendors, totalling ~27,500 lines of Python infrastructure and 350 passing tests. The dynamic management layer alone grew from 3,161 to ~6,100 lines.

**Models:** Claude Opus 4.6 (CC1/CC2), Codex 5.3, Gemini 3.1 Pro, DeepSeek V3.2 Reasoner, ChatGPT 5.4.

---

## Category 1: Self-Monitoring

### Decay Curve Diagnostic
The system monitors analytical quality in real time by fitting per-round finding rates to decay curves. Genuine analysis → convergent decay. Chatbot churn → flat line. Codex on ft-001/CDSFL: `5, 3, 2, 2, 0`. DeepSeek on same task: `2, 2, 2, 2, 2`.

### Capability Fingerprinting
`(D, v̄, A, C)` fingerprint: decay rate, verification score, total verified findings, constraint coverage. Tracked per model per round.

### DetectorHealthMonitor
Level 2 immune response (Exp 12). Monitors whether convergence detectors are working — distinguishes "experiment should stop" from "instruments are broken."

### Vocabulary Novelty Tracking
CC2: 23.9% (R1) → 7.7% (R20). Early/late Jaccard overlap = 33.5% — two-thirds of late-round vocabulary was genuinely new.

### SymPy Verification
All mathematical claims in CDSFL conditions checked computationally. Codex: 100% verification (Exp 13b). DeepSeek: 0% self-verified (consistent calibration pathology).

---

## Category 2: Self-Correction

### Mid-Experiment Detector Repair (Exp 12)
Three detectors broke for three independent reasons. Kappa: Jaccard needs exact matches. Mu: rewarded model attrition. Gemini tau: threshold too aggressive. All diagnosed and fixed via 3 mid-run commits.

### DeepSeek Visible Self-Correction (Exp 11)
Only model that visibly corrected itself mid-output — 6 times, once per area. Moved from simpler formulations toward consensus through iterative refinement.

### Gemini Self-Falsification (Exp 2)
Identified 3 genuine tightening points in its own Erdős–Szekeres answer: implicit pigeonhole, enumeration vs demonstration, unstated monotonicity bridge.

### CC2 Coupled Generation-Falsification
Does not produce a first draft then review. Produces a reviewed draft with inline self-objections. Observed consistently across Exps 11, 12, 13b.

---

## Category 3: Multi-Agent Coordination

### Five-Model Distributed Compute
Exps 11–17: 5 models under identical CDSFL prompts, independent blind round → structured confer rounds.

### Blind + Confer Topology
CDSFL+HIL: 43 HARD findings vs Control: 10 (4.3× multiplier). Round 2 spike (12 findings) from cross-pollination.

### Heterogeneous Architecture Advantage (Exp 1)
Gemini found 16 novel issues that 8 rounds of CC/CX missed. Epistemic diversity ≠ redundancy.

### Four Cognitive Modes (Exp 11)
- **CC2:** Deep architecture + self-adversarial review
- **ChatGPT:** Engineering pragmatism + failure mode identification
- **Gemini:** Mathematical compression
- **DeepSeek:** Iterative refinement (most visibly Popperian)

### Confer/Defer Protocol (Exp 9)
5 deferred decisions resolved unanimously. 3 errors the non-CDSFL project manager would have committed were caught by framework-guided models.

---

## Category 4: Persistence & Memory

### Verification Chain (Exp 10)
790 lines. RFC 9162 Merkle trees, hash chains, optional Ed25519. 97 tests.

### Cross-Experiment Learning
Exp 12 → diagnosed detectors. Exp 13a → reviewed fixes. Exp 13b → validated fixes. Exp 14 → self-adaptive improvements. Exp 15 → new edge cases. Each builds on the previous.

### Hash-Chain Provenance
Every finding, round, experiment: SHA-256 hashed, chain-linked. Merkle roots per task. Corpus/directive hashes for reproducibility.

---

## Category 5: Adaptive Behaviour

### Self-Adaptive Immune Layer (Exp 14, Phases A–E)
Per-model registry Layer 4 wired. Immune feedback loop closed (`apply_diagnosis`). Per-model prompt adaptation. Area-level vocab tracking. Dispatch health monitoring with 3 new pathology types. 234 tests.

### Threshold Recalibration
τ_vocab: 0.10 → 0.04 (data-driven from Exp 13b). Sustained window: 3 → 5.

### Context Windowing
After Exp 12 lost 3/5 models to context overflow → adaptive windowing. All 5 survived Exp 13b.

### Adaptive Decomposition
Full-artifact failure → decompose into sub-areas. DeepSeek blocked in 13b blind round (P=0.000) → recovered via decomposed dispatch in R1.

---

## Category 6: Immune & Self-Repair

### Three-Layer Architecture
- **Level 1:** Convergence detectors (kappa, mu, novelty)
- **Level 2:** DetectorHealthMonitor
- **Level 3:** Self-adaptive immune layer (parameter adjustment, diagnosis application)

### Canary Tests (Exp 17)
4 preflight canaries: empty response, false positive, cascade failure, oscillation. All passing.

### Parser Yield Anomaly Detector (Exp 15)
Recovered +18 findings from Gemini/ChatGPT tuple format previously lost silently.

### Circuit Breaker Recovery (Exp 15)
Runs 1–2 killed by DeepSeek CircuitBreakerTripped. Fixed mid-experiment: catch + halved max_tokens retry. Run 3 completed.

---

## Category 7: Metacognitive Behaviour

### Second-Order Cognition
The system analyses its own analysis via decay curves, verification rates, and adoption deltas. Meets the formal MIDCA definition. Substrate-agnostic.

### Ascending Abstraction (Exp 13b)
CC2 severity increased (0.610 → 0.664) while count decreased. Fewer but deeper findings. Y(t) = 107.3.

### Self-Referential Falsification (Exp 8)
5-model blind review of the mathematical model itself. 11 genuine fixes applied. The framework improved its own mathematical foundations through its own process.

---

## Null Results & Failures

| Finding | Detail |
|---------|--------|
| Self-improvement not confirmed | CC2 abstraction: p=0.045 at 9 rounds, p=0.29 at 20. Quality ratchet is environment-mediated. |
| Population too small | 5 models from 4 vendors. Strong diversity hypothesis untested. |
| Near-ceiling tasks | Tasks likely in training data. Discrimination requires genuinely novel problems. |
| DeepSeek verification pathology | 0% self-verified across all experiments. 6/15 corroborated TRUE by peers. |
| HIL prompt narrowing | >500 chars overpowers the condition. Cap needed. |
| Phantom HARD inflation | Default constraint_class=HARD inflated Bench Run 1 counts. Fixed. |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Python (bench/) | ~27,500 lines |
| `dynamic_management.py` | ~6,100 lines |
| `verification_chain.py` | 790 lines |
| Tests | 350 passing |
| Models | 5 from 4 vendors |
| Experiments | 18 (0–17) |
| Project age | 16 days |

**Meta-trajectory:** Exp 12 → structural failures. Exp 13 → calibration errors. Exp 14 → design gaps. Exp 15 → edge cases. Each iteration finds less fundamental problems. The methodology is converging on itself.
