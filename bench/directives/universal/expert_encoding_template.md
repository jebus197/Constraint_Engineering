# Expert Encoding Template — Solution Verification Gates
# Version: 1.0
# Date: 9 April 2026
#
# This template extends the existing domain directive format with the S_k
# solution verification layer. Every domain directive should include these
# sections alongside the existing [HARD constraints], [SOFT constraints],
# [Verification procedures], and [Limitations] sections.
#
# The S_k framework is domain-invariant. Only the content of this template
# changes across domains. The mathematical model (R_det, S_k, nu_eff, R_new)
# remains identical regardless of domain.

# =========================================================================
# SECTION: Solution Verification Gates
# =========================================================================
#
# Purpose: Define the tool-executable gates that produce S_k scores for
# proposed fixes in this domain. S_k = A · E where:
#   A = product of hard gates (binary admissibility, any failure → S=0)
#   E = aggregated effect evidence (graded 0-1, weighted by domain)
#
# Every gate MUST map to a tool. "Model judgment" is not a gate.
# The constraint box principle applies: tool output IS the evidence.

# -------------------------------------------------------------------------
# 1. HARD GATES (Admissibility)
# -------------------------------------------------------------------------
# Binary pass/fail. If ANY hard gate fails, A=0 and the fix is rejected
# regardless of effect evidence. These are necessary conditions for a fix
# to be considered at all.
#
# Format per gate:
#   Gate ID: g1, g2, ...
#   Name: human-readable name
#   Tool: the specific tool that evaluates this gate
#   Input: what the tool receives
#   Pass condition: what constitutes pass (score = 1)
#   Fail condition: what constitutes fail (score = 0)

# [HARD GATES]
# g1: <name> — Tool: <tool> — Pass: <condition> — Fail: <condition>
# g2: ...

# -------------------------------------------------------------------------
# 2. EFFECT EVIDENCE (Graded)
# -------------------------------------------------------------------------
# Continuous scores in [0, 1]. These measure HOW WELL the fix resolves the
# target finding without introducing new problems. Aggregated as weighted
# arithmetic mean over applicable gates (renormalised weights). A single
# zero score reduces E proportionally, not to zero — if a gate is
# non-negotiable, it belongs in the hard gates (A), not here.
#
# Format per evidence score:
#   Score ID: e1, e2, ...
#   Name: human-readable name
#   Tool: the specific tool that evaluates this score
#   Input: what the tool receives
#   Scoring: how the [0,1] score is derived from tool output
#   Weight: relative importance (weights normalised at composition time)

# [EFFECT EVIDENCE]
# e1: <name> — Tool: <tool> — Scoring: <method> — Weight: <relative>
# e2: ...

# -------------------------------------------------------------------------
# 3. BASELINE CAPTURE
# -------------------------------------------------------------------------
# Effect evidence gates measure delta from baseline — only NEW failures
# introduced by the fix count against it. Pre-existing failures are
# excluded. This section defines what constitutes the baseline for each
# gate and when it is captured.
#
# Baseline is captured ONCE per evaluation cycle, BEFORE any fix is
# applied. It represents the state of the target artefact as-is. Each
# effect evidence gate must specify:
#
#   What is measured: the specific metric (e.g., violation count, test
#     pass count, finding count)
#   When captured: before fix application (mandatory), or at experiment
#     start if the metric is stable across rounds
#   How pre-existing failures are excluded: the delta formula
#     (e.g., new_violations = max(0, post_fix - baseline))
#
# If a gate cannot define a meaningful baseline (e.g., the artefact did
# not previously exist), the gate operates in absolute mode: all findings
# count. State this explicitly in the gate definition.
#
# Baseline capture must be deterministic and reproducible. If the
# baseline tool is non-deterministic (e.g., flaky tests), the encoding
# must specify how to handle variance (e.g., run N times, take worst).

# [BASELINE CAPTURE]
# <gate_id>: <what is measured> — <when captured> — <delta formula>

# -------------------------------------------------------------------------
# 4. FIX FORMAT
# -------------------------------------------------------------------------
# How models must structure proposed fixes in this domain. The format must
# be machine-parseable and directly evaluable by the tool gate pipeline.
# Natural language descriptions are NOT acceptable as the primary fix
# representation — they may accompany a structured fix as commentary only.

# [FIX FORMAT]
# <specification of the machine-readable fix format for this domain>

# -------------------------------------------------------------------------
# 5. TOOL MAPPING
# -------------------------------------------------------------------------
# Complete list of tools available for gate evaluation in this domain.
# Each tool must be:
#   - Executable without human intervention
#   - Deterministic (same input → same output)
#   - Bounded in execution time
#
# Tools that require network access, paid APIs, or human judgment are
# NOT admissible as gate evaluators. They may inform manual review but
# do not contribute to S_k.

# [TOOL MAPPING]
# <tool_name>: <import/invocation> — <what it evaluates>

# -------------------------------------------------------------------------
# 6. DOMAIN-SPECIFIC S* GUIDANCE
# -------------------------------------------------------------------------
# The break-even threshold is:
#   S* = (nu_b + nu_f − nu_b·nu_f − q·R) / (nu_f · (1 − nu_b))
# (This is the full form used in cdsfl_operational.md §4. Earlier
# drafts of this template used the approximation S* = (nu_b + nu_f − q·R)
# / nu_f, which is only accurate when nu_b ≪ 1. Use the full form.)
#
# S* is computed from the current system state. However, domains may have
# structural reasons to set a FLOOR on S* (minimum acceptable fix quality)
# or to provide guidance on typical nu_b and nu_f ranges.

# [S* GUIDANCE]
# Typical nu_b range: <range and rationale>
# Typical nu_f range: <range and rationale>
# Recommended S* floor: <value and rationale>

# -------------------------------------------------------------------------
# 7. DOMAIN-SPECIFIC LIMITATIONS
# -------------------------------------------------------------------------
# What this encoding does NOT cover. What classes of fix cannot be
# tool-verified in this domain and must be escalated to human review.

# [SOLUTION VERIFICATION LIMITATIONS]
# <what cannot be automatically verified>

# -------------------------------------------------------------------------
# 8. DOMAIN KNOWLEDGE STRUCTURE
# -------------------------------------------------------------------------
# Enriched encodings go beyond compliance rules. They capture the
# practitioner knowledge that turns a directive from "what must not be
# violated" into "how experienced practitioners actually work." Each
# encoding should address these categories where applicable:
#
# Failure mode priors: The 80/20 of what actually breaks in practice
#   in this domain. Not every possible failure — the ones that account
#   for most real-world incidents.
#
# Diagnostic heuristics: The pattern-matching that experienced
#   practitioners do instinctively. What do they check first? What
#   symptom points to what root cause?
#
# Tool-chain realism: Where standard tools in this domain
#   systematically misrepresent reality. Where simulation diverges from
#   measurement. Where the tool says "pass" but the experienced
#   practitioner says "check again."
#
# Regime boundaries: Where the textbook equation stops working and the
#   practitioner switches to a different approach. The boundary conditions
#   that separate the linear/simple regime from the non-linear/complex
#   regime in this domain.
#
# Standard gotchas: Known loopholes, misapplications, and edge cases
#   that every experienced practitioner warns about. The "everyone knows
#   this except the newcomer" knowledge.
#
# Disagreement maps: Areas where domain experts genuinely differ and
#   there is no consensus. Stating this honestly prevents false certainty
#   and identifies where independent verification is most valuable.
#
# Evidence quality grading: The difference between a code requirement,
#   a vendor recommendation, a textbook derivation, a workshop anecdote,
#   and a peer-reviewed result. Not all evidence is equal. This section
#   defines the hierarchy for this domain.
#
# Tacit sequencing: The order in which experienced practitioners check
#   things. What gets verified first? What depends on what? This is the
#   knowledge that separates efficient diagnosis from exhaustive search.
#
# Escalation triggers: The signals that tell a practitioner to stop
#   work and consult a more senior colleague or external authority. The
#   "if you see this, you're out of your depth" markers.
#
# Not every domain will have content for every category. State which
# categories are not applicable and why.

# [DOMAIN KNOWLEDGE]
# Failure mode priors: <domain-specific>
# Diagnostic heuristics: <domain-specific>
# Tool-chain realism: <domain-specific>
# Regime boundaries: <domain-specific>
# Standard gotchas: <domain-specific>
# Disagreement maps: <domain-specific>
# Evidence quality grading: <domain-specific>
# Tacit sequencing: <domain-specific>
# Escalation triggers: <domain-specific>

# -------------------------------------------------------------------------
# 9. VERIFICATION STATUS
# -------------------------------------------------------------------------
# Every encoding has a verification tier that determines how it may be
# used. Tiers are cumulative — each includes all requirements of the
# tier below it plus additional validation.
#
# SEED: Initial draft. Gates defined, no testing. Not for operational
#   use. Suitable for template validation only.
#
# DRAFT: Gates implemented and tested against synthetic examples.
#   Basic sanity confirmed. Suitable for development and debugging.
#
# CROSS-VERIFIED: Reviewed by at least two independent models under
#   structured falsification. Gate definitions challenged and refined.
#   Suitable for research benchmarking and non-safety-critical domains.
#
# CURATED: Cross-verified plus domain-specific enrichment from
#   Section 8 (Domain Knowledge Structure). Failure mode priors,
#   diagnostic heuristics, and regime boundaries populated. Suitable
#   for comprehensive benchmarking.
#
# OPERATIONAL: Curated plus validation against real-world cases. Gate
#   scores correlate with actual fix outcomes in at least one measured
#   experiment. Suitable for production advisory use.
#
# VALIDATED: Operational plus human domain expert review. A qualified
#   practitioner has confirmed that the encoding reflects genuine domain
#   practice, not just model-generated plausibility. Required for
#   safety-critical and regulatory domains.
#
# RETIRED: Superseded by a newer encoding version. Retained for
#   reproducibility of prior experiments. Not for new use.
#
# State the current tier and date. Include the evidence that supports
# the claimed tier (e.g., which experiment cross-verified, which expert
# validated).

# [VERIFICATION STATUS]
# Tier: <SEED | DRAFT | CROSS-VERIFIED | CURATED | OPERATIONAL | VALIDATED | RETIRED>
# Date: <date of last tier change>
# Evidence: <what supports this tier>

# -------------------------------------------------------------------------
# 10. EPISTEMOLOGICAL BOUNDARY
# -------------------------------------------------------------------------
# S_k measures the absence of DETECTED failure modes. It does not measure
# the absence of ALL failure modes. A high S_k means the fix passed every
# tool-executable gate in this encoding. It does not mean the fix is
# correct, safe, or optimal — only that no available tool found a problem.
#
# This distinction is structural, not a caveat. The S_k framework
# evaluates what tools can measure. Failure modes that lie outside the
# tool envelope (novel interactions, emergent behaviour, domain-specific
# judgment calls, aesthetic or ethical considerations) are invisible to
# S_k. They require human review, domain expertise, or tools that do
# not yet exist.
#
# Consumers of S_k scores must understand this boundary:
#   S_k = 1.0 means: "every gate passed" — not "the fix is perfect"
#   S_k = 0.0 means: "a gate failed" — this IS definitive (a failure
#     was detected)
#   ESCALATE means: "the tools cannot determine" — honest uncertainty,
#     not a score
#
# Over-interpreting S_k as a guarantee of correctness is a category
# error. Under-interpreting S_k = 0 is also wrong — a detected failure
# is a detected failure regardless of what else might exist.
