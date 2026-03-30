# CDSFL Round Robin Smoke Test Results

**Date:** 2026-03-21

---

## Overview

The round robin smoke test ran one frontier task — ft-001: Monotone Subsequence Bound Tightening — across four experimental conditions. Three AI models participated. Opus 4.6 acted as orchestrator and arbiter. Gemini 3.1 Pro Preview and Codex 5.3 acted as independent reviewers.

The four conditions test two variables independently: **structure** (the formal CDSFL framework) and **guidance** (domain expert input). This gives a 2×2 grid:

| Condition | Structure | Guidance |
|---|---|---|
| Control | No | No |
| HIL | No | Yes |
| CDSFL | Yes | No |
| CDSFL + HIL | Yes | Yes |

---

## Findings by Condition

**Control** found 19 issues with no structure and no guidance. However, qualitative analysis shows these are largely repetitive. Rounds 3 through 5 rehash rounds 1 and 2 with the same complaints reworded: "The proof is missing. The proof is omitted. The proof is not shown." This is churn, not depth.

**HIL** found only 2 issues. Expert guidance narrowed the search so much that structural problems were missed entirely. High confidence at 0.93 but very low coverage.

**CDSFL** found 10 issues. The formal framework catches things the expert guidance misses, but without domain knowledge it includes minor findings and cannot prioritise effectively. Average confidence 0.88.

**CDSFL + HIL** found 27 issues: 17 critical severity, 10 major, zero minor. Average confidence 0.95, the highest of all conditions. This is the strongest result by every quality measure.

---

## The Interaction Effect

The combination of framework plus guidance produces more than the sum of its parts:

- CDSFL alone: 10
- HIL alone: 2
- Together: 27 — more than 10 + 2 = 12

Under CDSFL + HIL, confer rounds produce genuinely novel findings rather than repeating earlier ones:
- Round 3 identified: "label pair uniqueness proof not at full rigour"
- Round 4 found: "pigeonhole arithmetic off-by-one conclusion unverified"
- Round 5 found: "submission not self-contained, relies on unavailable external reference"

Each round goes deeper, not wider. Under control, rounds 3 through 5 just repeat rounds 1 and 2 in different words.

---

## Methodology Activates Dormant Capability

Gemini contributed zero to three findings under Control, CDSFL, and HIL conditions. Under CDSFL + HIL it contributed nine substantive findings, including domain-specific catches:

- "Must not use by-construction to bypass structural proofs"
- "Must not conflate subsequence with contiguous substring"

The methodology transforms a weaker model from producing nothing useful to producing targeted, domain-specific analysis. **This is the most interesting qualitative finding of the smoke test.**

---

## What This Does Not Mean

- This is one task from one domain (mathematics). It is not statistically significant by any measure.
- All three models have this problem in their training data. The Erdos-Szekeres theorem is textbook material. Near-ceiling generation is expected and uninformative for capability claims.
- Opus 4.6 generates solutions and acts as arbiter. Its blind spots may propagate through the chain.

The results are encouraging. They do not say "stop." They also do not say "conclusive." The full 25-task run is required.

---

## Falsifiable Questions Generated

1. Does the CDSFL + HIL advantage persist on problems not in training data? This is the specialist gap — only humans can supply genuinely novel test cases.
2. Does the "methodology activates dormant capability" effect replicate with other weak models?
3. Is the "depth not churn" property of confer rounds specific to CDSFL + HIL, or does any structured iterative methodology produce it?
4. At what ensemble size do additional architectures stop producing novel findings?
5. Does the depth advantage hold in non-mathematical domains where hard constraint is less precisely defined?

---

## Next Step

Full run approved. 25 tasks × 4 conditions = 100 runs. Estimated 20–30 hours with checkpoint and resume across sessions.
