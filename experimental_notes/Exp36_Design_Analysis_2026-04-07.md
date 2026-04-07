# Experiment 36 — Design Analysis and Next Steps

**Date:** 7 April 2026, 09:11 BST
**Scope:** Structural analysis of CC2v, Bugzilla model, immune pipeline, fix pipeline, and schema integration. Scoping for Exp 37 / resumed Exp 36.

## I. CC2v and the Bugzilla Model — Critical Design Gap

### The Finding Status Lifecycle

```
OPEN → CONFIRMED (2+ independent models verify, or CC2v confirms)
CONFIRMED + verified_fix → CLOSED (challenge-resistant, terminal)
CONFIRMED + late challenge → CONTESTED
CONTESTED → CONFIRMED (if challenge resolved)
CLOSED → REOPENED (only via explicit REOPEN + HIL escalation)
```

### The Gap: CONFIRMED ≠ CLOSED

CONFIRMED findings remain in the ACTIVE pool of the registry summary. Models see them in full detail (description, severity, verdict history, proposed fix) and can still issue CHALLENGE verdicts. Only CLOSED findings are challenge-resistant, and CLOSED requires a programmatically verified fix.

Exp 36 is a code *review*, not a code *remediation*. The runner doesn't extract, apply, or verify fixes. Findings can never reach CLOSED status. They get CONFIRMED by CC2v, stay in the ACTIVE pool, and models keep engaging with them — re-describing, re-confirming, occasionally challenging. CC2v then re-confirms the same finding it already confirmed.

**This directly explains:**
- The 17:1 dedup ratio (findings cycle through CONFIRMED but never reach CLOSED)
- CC2v single-bug-family dominance (DA-7: export_bundle confirmed 12+ times)
- 18% of CC2v slots wasted on parser artifacts (no pre-filter before CC2v queue)
- The ITC-convergence feedback loop (models keep producing output about CONFIRMED findings)

### CC2v Operational Details

- Activates at R6 (`VERIFICATION_MIN_ROUND = 6`)
- Processes 6-finding batches per round from OPEN and CONTESTED findings only
- Confidence-gated at 0.7: CONFIRM/REJECT/DUPLICATE/ESCALATE
- CONFIRM → `registry.resolve(finding_id, "CONFIRMED", round_idx)`
- REJECT → status changes to UNCONFIRMED
- DUPLICATE → status changes to MERGED
- ESCALATE → finding flagged `cc2v_escalated=True`, excluded from future batches
- CC2v does NOT select already-CONFIRMED findings for re-verification

**The safeguard exists but is insufficient:** CC2v won't re-verify CONFIRMED findings, but discovery models will keep *rediscovering* the same bug and creating new OPEN entries about it. The dedup engine (NK cell) should catch these, but with tau_sim=0.33 (v1), it misses semantically similar findings expressed in different words.

## II. The Fix Pipeline Gap

### What the Appendix Specifies

§7.12 FFF model: Find-Fix-Follow. Models should produce fixes and trace consequences. The immune pipeline's Stage 4 (programmatic fix verification via pyright/ruff/bandit) exists in the code.

### What the Runner Does

The star topology prompt asks models to find bugs, issue verdicts, and propose fixes. The "proposed_fix" field exists in findings. But the runner never:
1. Extracts the proposed fix from the finding
2. Applies it to a sandbox copy of the source
3. Runs Stage 4 verification
4. Marks the finding CLOSED on success

### What Needs to Change

To close the Bugzilla loop:
1. Extract proposed fix text from CONFIRMED findings
2. Apply to sandbox copy of the test article (evidence.py)
3. Run pyright/ruff/bandit + existing test suite
4. If verification passes: mark finding CLOSED (challenge-resistant)
5. Feed CLOSED status back to models via registry summary (already implemented — CLOSED findings appear in compact resolved section with "do not re-describe" instruction)

This would unlock the Bugzilla model's challenge-resistant gate and directly reduce churn by removing confirmed-and-fixed findings from the active discovery pool.

## III. Shadow Immune Pipeline — Activation Assessment

### Current v2 Agents (Running in Shadow/Parallel)

| Agent | v1 Status | v2 Status | Key v2 Improvement |
|-------|-----------|-----------|-------------------|
| DC (Dendritic Cell) | Active | PRIMARY | Citation-aware routing, confidence scoring |
| CT (Cytotoxic T) | Active | Parallel | Falsifier architecture (vs investigator) |
| B-Cell | Active | Parallel | AST-grounded Z3/SMT (vs abstract symbolic) |
| NK Cell | — | PRIMARY | tau_sim 0.50, intra-round dedup, bug-closed gate |
| Helper T | Active | Parallel | Two-level aggregation, asymmetric rejection barrier |
| Reg T | — | PRIMARY | Fixed proportional math |

### Additional Shadow Components (Not Yet Active)

- **Typed LLM Classifier (WP3c):** Haiku-based classification replacing DC regex. Would fix ~30% misclassification rate.
- **Formalisation Agent (WP3d):** Extracts preconditions, feeds to B-Cell for context preservation.
- **Skin Barrier:** Deterministic pre-filter dropping findings that cite non-existent code. Currently observation-only.

### Impact of Full Activation on Churn

| Problem | v2 Component That Addresses It | Expected Impact |
|---------|-------------------------------|-----------------|
| 17:1 dedup ratio | NK v2 (tau_sim 0.50 + intra-round dedup) | High — catches semantic duplicates v1 misses |
| Re-examination of confirmed bugs | NK v2 bug-closed gate | High — immediate CLOSED for verified-fix bugs |
| Parser artifacts in CC2v queue | Skin barrier active filtering | Medium — drops malformed findings before CC2v |
| DC regex misclassification (21–44%) | Typed LLM classifier | High — correct routing improves downstream verification |
| B-Cell false rejections | B-Cell v2 AST-grounded + Formalisation Agent | Medium — grounded verification reduces false negatives |
| False confirmation bias | CT v2 falsifier architecture | Medium — actively tries to disprove rather than confirm |
| Helper T aggregation bugs | Helper T v2 two-level + asymmetric barrier | Medium — rejection must overcome 0.7 barrier |

### Recommendation

Activate v2 as primary for Exp 37 / resumed Exp 36. Remove v1 cells (saves 30–60s per verification round). Enable skin barrier filtering. Make LLM classifier primary.

**Caveat:** v2 immune activation addresses *downstream* filtering (catching duplicates after models produce them). It does not address *upstream* generation (ITC feedback loop causing models to produce duplicates). Both fixes are needed.

## IV. Schema Integration Assessment

### Lessons Built Into Schema (Already Done)

- Anti-deference enforcement (Layer 1, HARD)
- Falsification required (Layer 1, HARD)
- Non-compensatory convergence (Layer 1, HARD)
- Per-domain verification rules (Layer 2)
- JSON schema payload requirements (Layer 1, HARD)
- SymPy auto-verify (Layer 1, HARD)

### Lessons Built Into Runners Only (Not Schema)

- ITC strategies (restart_fresh, change_focus)
- Finding status FSM (OPEN/CONFIRMED/CONTESTED/CLOSED)
- CC2v verification agent
- Immune pipeline version selection (v1 vs v2)
- Directed messaging protocol
- Convergence gate conditions
- Stall detector
- Endocrine health cycles

### Lessons Not Yet Built Into Either

From Exp 36 verification and design analysis:
1. Contested → HIL escalation threshold (should be schema: `convergence.contested_escalation_rounds`)
2. Discovery efficiency metric ρ (should be schema: `convergence.churn_threshold`)
3. Gamma-aware ITC threshold (runner operational logic)
4. Context windowing for long runs (runner operational logic)
5. Pre-filter before CC2v queue (runner/immune pipeline)
6. Dedup-aware CC2v (runner operational logic)
7. Fix-application pipeline (runner + immune Stage 4)
8. Per-model ρ tracking (runner operational logic)
9. Meta-cognitive decay feedback (runner prompt logic)
10. Dynamic stall detector threshold (runner operational logic)

### Deep Schema Audit Warranted?

Partially. The schema has been actively maintained (Schema_Amendments doc from 5 April covers 8 specification gaps). The bigger risk is in the mathematical appendix (5 structural gaps, not updated since 31 March) and in the runner-to-schema boundary (operational lessons that should become parameters but haven't been promoted yet). Items 1 and 2 above are clear candidates for schema promotion.

## V. Convergence Proximity and Resumption Assessment

### How Close Was Exp 36?

At R18: contested=1, novel=2, all other gate conditions satisfied. **One contested finding away from convergence.**

By R22: contested rose to 2 (wrong direction), gamma static at 0.411. The system was moving *away* from convergence due to the ITC feedback loop.

**Without contested→HIL escalation, convergence was unreachable.** The contested findings could not be resolved autonomously by the models. No number of additional rounds would have changed this.

**With contested→HIL escalation (5-round threshold):** The 1 contested finding at R18 had been contested since approximately R12. A 5-round escalation threshold would have triggered at R17, the founder would have resolved it, and the gate would have fired at R18 or R19.

### Resumption Feasibility

The runner supports `--resume` from checkpoint. Full state restoration from R22 (452 raw findings, 153 canonical entries, all registry state).

**Resumption WITHOUT fixes:** Would produce more churn. Not recommended.

**Resumption WITH fixes (recommended minimum):**
1. Contested → HIL escalation (so the founder can resolve the 2 contested findings)
2. Gamma-aware ITC threshold (so the ITC stops generating churn)
3. Dedup-aware CC2v (so CC2v stops re-confirming export_bundle)

**Estimated rounds to convergence after fixes:** 3–5 additional rounds. The contested findings would escalate to HIL immediately (they've been contested for 10+ rounds), the ITC would stop restarting models, and the gate would likely fire.

### Fresh Exp 37 vs Resumed Exp 36

| Factor | Resume Exp 36 | Fresh Exp 37 |
|--------|--------------|--------------|
| Test article | evidence.py (already well-explored) | New article (fresh discovery space) |
| Starting state | 153 canonical, 9 unique bugs known | Clean slate |
| Purpose | Validate design fixes work | Full experiment with all improvements |
| Risk | May converge too quickly (nothing left to find) | Longer run, higher cost |
| Scientific value | Tests fix effectiveness on known baseline | Tests full improved system end-to-end |

**Recommendation:** Both have value. Resume Exp 36 as a quick validation (expect 3–5 rounds), then run a fresh Exp 37 on a new test article with all 13 design improvements + v2 immune activation. The resumed Exp 36 becomes a controlled comparison: same test article, same data, different design — isolates the impact of the fixes.

## VI. CC2 Option A — The Four-Agent Model

### Agent Numbering

| Agent | Role | Status |
|-------|------|--------|
| Agent 1 | Structural — code structure, dependencies, architectural patterns | Designed, NOT coded |
| Agent 2 | Semantic — semantic correctness, type safety, semantic dependencies | Designed, NOT coded |
| Agent 3 | Integration — cross-component interactions, API contracts | Designed, NOT coded |
| Agent 4 | CC2v — between-round verification (CONFIRM/REJECT/DUPLICATE/ESCALATE) | IMPLEMENTED, operational |

### Impact of Missing Agents 1–3

Only Agent 4 was implemented for Exp 36. CC2 operated as both a general-purpose discovery model AND the Agent 4 verifier. The deep analysis showed CC2 producing only 42 raw findings (9.3% of total) — lowest of all 5 models — because of this dual role.

If Agents 1–3 existed:
- **CC2's contribution would be specialised** rather than general-purpose. A structural agent targeting structural bugs, a semantic agent targeting type safety, an integration agent targeting API contracts. Specialisation produces more targeted, less redundant findings.
- **Agent 2 (Semantic) is a code discovery agent, NOT the "semantic layer."** It would find semantic bugs in code (type safety, semantic correctness). The "semantic layer" is the immune pipeline's distributed processing of findings (NK v2 dedup, B-Cell v2 AST verification, LLM classifier, formalisation agent). These are orthogonal: Agent 2 operates on code, the semantic pipeline operates on findings. [Corrected 7 April 2026 09:33 BST — original text incorrectly conflated these.]
- **Dedup ratio would likely improve** because specialised agents produce findings in narrower categories, making the dedup engine's job easier (same-category findings are easier to cluster than cross-category reformulations).

### Implementation Note

Adding Agents 1–3 mid-experiment (during resumed Exp 36) would change experimental conditions and weaken controlled comparison. Recommended: implement for fresh Exp 37 only.

---

## VII. What the "Semantic Layer" Is

There is no single component explicitly named "semantic layer." The semantic capabilities are distributed across:

1. **NK v2 similarity-based dedup:** Jaccard similarity on tokenised descriptions (tau_sim=0.50)
2. **B-Cell v2 AST-grounded verification:** Extracts constants from actual Python AST, builds SMT-LIB strings from claims using real code values
3. **Reconciliation gate (Stage 3a.5):** When v1 AND v2 agree on a verdict, it's LOCKED (immutable)
4. **Typed LLM classifier (shadow):** Haiku-based semantic classification replacing regex patterns
5. **Formalisation agent (shadow):** Semantic extraction of preconditions from findings

Full activation of these components would create a de facto semantic processing pipeline: findings are semantically classified (LLM classifier) → semantically deduplicated (NK v2) → semantically verified against actual code (B-Cell v2 + CT v2) → semantically synthesised (Helper T v2 two-level aggregation). The "semantic layer" is the emergent capability of these components working together rather than a single named module.
