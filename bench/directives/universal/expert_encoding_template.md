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
# product (geometric mean or raw product depending on calibration).
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
# 3. FIX FORMAT
# -------------------------------------------------------------------------
# How models must structure proposed fixes in this domain. The format must
# be machine-parseable and directly evaluable by the tool gate pipeline.
# Natural language descriptions are NOT acceptable as the primary fix
# representation — they may accompany a structured fix as commentary only.

# [FIX FORMAT]
# <specification of the machine-readable fix format for this domain>

# -------------------------------------------------------------------------
# 4. TOOL MAPPING
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
# 5. DOMAIN-SPECIFIC S* GUIDANCE
# -------------------------------------------------------------------------
# The break-even threshold S* = (nu_b + nu_f - q·R) / nu_f is computed
# from the current system state. However, domains may have structural
# reasons to set a FLOOR on S* (minimum acceptable fix quality) or to
# provide guidance on typical nu_b and nu_f ranges.

# [S* GUIDANCE]
# Typical nu_b range: <range and rationale>
# Typical nu_f range: <range and rationale>
# Recommended S* floor: <value and rationale>

# -------------------------------------------------------------------------
# 6. DOMAIN-SPECIFIC LIMITATIONS
# -------------------------------------------------------------------------
# What this encoding does NOT cover. What classes of fix cannot be
# tool-verified in this domain and must be escalated to human review.

# [SOLUTION VERIFICATION LIMITATIONS]
# <what cannot be automatically verified>
