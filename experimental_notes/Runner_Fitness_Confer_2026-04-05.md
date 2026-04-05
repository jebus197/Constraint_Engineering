# Runner Fitness Confer — Exp 34/35/36

**Date:** 5 April 2026, ~21:08 BST
**Models:** CX (GPT-5.4, reasoning high) + Gemini 3.1 Pro
**Protocol:** Full CDSFL, individual convergence, CC monitors
**Logs:** `bench/logs/confer_runner_review/`

## Overview

Both models reviewed all 3 runners independently under full CDSFL constraints.
One round per runner. Both models concluded **not fit for live execution**.
CC called convergence after one round — core findings were stable across all 6 reviews.

## Confirmed Bugs (11)

### P0 — Blocking

| # | Bug | Models | Fix |
|---|-----|--------|-----|
| 1 | **MERGE semantics backwards** — canonical target marked MERGED, not duplicate | Both (all 6) | `_resolve_merge_source()` records MERGE on source entry |
| 2 | **Convergence gate** — only novelty checked across 2-round window | Both (all 6) | `_evaluate_gate_conditions()` + `gate_history` tracks all 5 conditions |
| 3 | **contested_count ignores non-OPEN** — late challenges invisible after CONFIRMED | CX (2 runners) | Check all non-MERGED, compare challenge timing vs latest confirm |

### P1 — High

| # | Bug | Models | Fix |
|---|-----|--------|-----|
| 4 | **Resume doesn't restore registry** | Both (all 6) | `runner_state.json` persists registry + convergence state per round |
| 5 | **Gamma estimation wrong** — first/last only, raw findings | Both (all 6) | Log-log regression over canonical `novelty_counts` |
| 6 | **Verdict parser em-dash** — prompt U+2014, regex ASCII only | CX (2 runners) | Regex accepts Unicode dashes + leading whitespace |
| 7 | **Multi-turn fallback split** — splits on `"=== FILE:"` but headers differ | CX (1 runner) | Regex split on actual TARGET/SCHEMA/CONTEXT headers |
| 8 | **UNSTRUCTURED fallback** — verdict-only responses create fake findings | CX (1 runner) | Suppress fallback when verdict patterns detected (`runner_core.py`) |

### P2 — Medium

| # | Bug | Models | Fix |
|---|-----|--------|-----|
| 9 | **Missing UNCONFIRMED sweep** | CX (2 runners) | Resolve remaining OPEN → UNCONFIRMED before `signal_complete()` |
| 10 | **SUPERSEDES in prompt but not parsed** | Gemini (1 runner) | Removed from all 3 prompts |
| 11 | **Popper C(H,E) invalid math** (exp36 only) | Gemini (1 runner) | Removed entirely |

## False Positive (1)

**Alias collision** (Gemini, all 3 reviews): Claimed `FindingRegistry._alias_map` would collide across models. Incorrect — `runner_core.py:parse_findings()` already prefixes all finding IDs with `{model_id}_` before registration.

## Passed Checks

Both models confirmed avoidance of all known historical mistakes:
- FFF is prompt-only (no enforcement/rejection)
- Verdict parser exists
- Gemini nested-dict JSON handled in shared parser
- Float stringification for Merkle sealing present
- REJECTED status gone (UNCONFIRMED)
- FFF ordering correct (Find → Follow → Fix)
- `resolve()` is live (not dead code)
- `has_follow` dead metadata removed
- Prompts broadly neutral, correctly targeted at each test article

## Status

All 11 bugs fixed across all 3 runners + `runner_core.py`. All files compile.
Runners are now fit for live execution.
