# CX + Gemini Runner Review Results

**Date:** 6 April 2026, 16:15 BST
**Reviewed by:** CX (GPT-5.4 via OpenRouter) + Gemini (3.1 Pro via Google API)
**Targets:** `bench/run_exp35_policy_engine.py`, `bench/run_exp36_evidence.py`
**Method:** Sequential CDSFL FFF review (CX then Gemini for each runner)

---

## Summary

| Metric | Value |
|--------|-------|
| Total unique findings | 11 |
| Confirmed (genuine bugs) | 1 |
| Refuted (code is correct) | 9 |
| Hallucinated (code doesn't exist) | 1 |
| Genuine finding rate | 9% |

---

## Findings Triage

### Confirmed

| Finding | Reviewers | Severity | Description |
|---------|-----------|----------|-------------|
| Alias map not scoped by model_id | Gemini (×2) | 1.0 | `_alias_map[finding.finding_id]` without model prefix — Model B's "F001" overwrites Model A's, corrupting canonical registry |

### Refuted

| Finding | Reviewers | Claim | Reality |
|---------|-----------|-------|---------|
| MERGE marks target not duplicate | CX (×2), Gemini (×2) | MERGE C0001 inverts merge | `_resolve_merge_source()` adds verdict to source; `_update_finding_statuses` marks source as MERGED |
| Convergence gate 2-round check | CX (×2), Gemini (×1) | Only novelty checked for 2 rounds | `gate_history` tracks combined boolean; consecutive check enforces all 5 conditions |
| Resume doesn't restore registry | CX (×2) | Fresh registry after resume | `runner_state.json` persists + restores registry, novelty, gamma, gate history |
| Gamma uses first/last only | CX (×2) | Not log-log regression | Both runners use full log-log regression over all cumulative points |
| Contested state machine incomplete | CX (×1) | CONFIRMED despite CHALLENGE | `unresolved_challenges` guard blocks promotion |
| Verdict-only creates fake findings | CX (×1) | Fallback fires on verdicts | `_has_verdicts` check prevents fallback |
| No OPEN→UNCONFIRMED finalization | CX (×1) | Missing end-of-run pass | Finalization pass exists at experiment end |
| Verdict regex too strict | Gemini (×1) | No leading whitespace | Regex includes `\s*` pattern |

### Hallucinated / Not Applicable

| Finding | Reviewers | Issue |
|---------|-----------|-------|
| Popper C(H,E) rates > 1.0 | Gemini (×1) | No such code exists in runner |
| SUPERSEDES not implemented | CX, Gemini | Removed from Exp 36 entirely |

---

## Fix Applied

**Alias map scoping** — 4 changes per runner (8 total):

1. `register()`: `self._alias_map[f"{model_id}:{finding.finding_id}"] = canonical_id`
2. `lookup_alias()`: accepts `(model_id, local_id)`, looks up `f"{model_id}:{local_id}"`
3. `_resolve_merge_source()`: calls `registry.lookup_alias(model_id, local_id)`
4. Main loop: `registry.lookup_alias(f.model_id, f.finding_id)`

**Verification:** 688 tests pass, both files parse cleanly.

---

## Per-Reviewer Performance

| Reviewer | Findings | Confirmed | False Positive Rate |
|----------|----------|-----------|---------------------|
| CX (Exp 35) | 5 | 0 | 100% |
| Gemini (Exp 35) | 2 | 1 | 50% |
| CX (Exp 36) | 7 | 0 | 100% |
| Gemini (Exp 36) | 5 | 1 | 80% |

Gemini identified the only genuine bug. CX produced exclusively false positives across both reviews. This is consistent with the Exp 34 observation that different models have sharply different strengths: Gemini was the only effective challenger in that experiment too.
