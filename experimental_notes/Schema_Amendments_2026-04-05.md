# CDSFL Schema Amendments — Topology Formalisation

**Date:** 5 April 2026
**Provenance:** Runner fitness confer (CX + Gemini 3.1 Pro) → 11 implementation bugs → 6 specification gaps
**New document:** `bench/directives/universal/cdsfl_topology_formal.md`
**Core amendments:** `cdsfl_core_formal.md` §3, `cdsfl_core.txt`

## Rationale

The confer found 11 bugs in the Exp 34/35/36 runners. Six of those bugs traced to
gaps in the CDSFL specification where correct implementations could diverge because
the spec was silent or ambiguous. Two independent reviewing models and the original
code author all made the same interpretation errors — evidence that the errors
originate in the specification, not in any individual reading of it.

## New Specification: `cdsfl_topology_formal.md`

8 sections formalising the multi-model star/blackboard protocol:

| Section | What it specifies | Gap it closes |
|---------|-------------------|---------------|
| **T1** | Star/blackboard topology definition | Previously in code only, no formal spec |
| **T2** | Finding status model (FSM) | No CONTESTED state; late challenges invisible |
| **T3** | Merge contract (directionality) | Source vs target ambiguous; target got merged |
| **T4** | Convergence gate (temporal conjunction) | Consecutive window applied to 1 of 5 conditions |
| **T5** | Gamma estimation (log-log regression) | Three different computations in same repo |
| **T6** | Round taxonomy (finding/verdict/mixed) | Verdict-only responses created fake findings |
| **T7** | Durability contract (state persistence) | Resume lost canonical blackboard state |
| **T8** | P-pass boundary tracing | False positive reproduced 3× from narrow analysis |

## Core Directive Amendment

**§3 Falsification Loop — Boundary Tracing:**

> When falsifying a claim about a system component, trace the claim's
> dependency chain to the system boundary before accepting or rejecting it.
> A claim about component A that depends on the behaviour of component B is
> not falsified by examining A alone.

Added to both `cdsfl_core_formal.md` and `cdsfl_core.txt`.

## Implementation Status

All three runners (Exp 34, 35, 36) updated to match the amended schema:
- CONTESTED state in FindingRegistry status model
- `merged_into` first-class field on entries
- Gate history tracks all 5 conditions per round
- Gamma from log-log regression on canonical novelty counts
- Verdict parser accepts Unicode dashes
- Fallback suppressed on verdict-only responses
- Runner state persisted per round for resume durability

All files compile. Schema, runners, RECOVERY.md, and ONBOARDING.md are consistent.
