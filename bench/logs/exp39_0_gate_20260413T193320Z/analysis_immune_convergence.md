# Immune Pipeline and Convergence Analysis — Exp 39-0

**Experiment:** exp39_0_gate, 6 rounds (R0-R5), terminated by wall clock cap (4388s), never converged.

---

## 1. Convergence Gate: Why Challenges Never Close

| Round | Open CRIT/HIGH | Novel | Verdict |
|-------|---------------|-------|---------|
| R0-R1 | (not checked) | 16, 9 | Too early |
| R2 | 11 | 4 | Too early |
| R3 | 16 | 9 | open_ch=16 > max=0 |
| R4 | 14 | 1 | open_ch=14 > max=0 |
| R5 | 13 | 2 | open_ch=13 > max=0 |

**Root cause:** `max_open_crit_high` defaults to 0 (`reference_runner.py` line 201). The convergence gate requires literally zero OPEN/CONTESTED/REOPENED findings with severity >= 0.7. The config does not override this. With 41 canonical entries and only 6 closures, this is structurally unreachable. The config's `_convergence_criteria.pass_condition` (`gamma >= 0.30 OR 3 consecutive rounds with 0 novel CRITICAL`) is documentation only — not implemented in code.

**Fix:** Set `max_open_crit_high` to 3-5, or implement the documented gamma-based alternative path.

---

## 2. S_k Pipeline: 0% ADMISSIBLE — The Critical Bug

Every round, every evaluated entry: "no SEARCH/REPLACE blocks found". Zero admissible across all 6 rounds.

**Root cause: Format mismatch between parser and S_k evaluator.**

The prompt (`reference_runner.py` lines 3074-3079) specifies format A:
```
<<<< SEARCH file_path
[content]
====
[content]
>>>> REPLACE
```

The `parse_findings` function in `runner_core.py` (line 670) reconstructs proposed_fix as format B:
```
<<<< SEARCH file_path
[content]
==== REPLACE
[content]
>>>>
```

The S_k evaluator's `parse_search_replace_blocks()` (`reference_runner.py` line 2094) checks `lines[i].rstrip() == "===="` for the separator — this never matches `==== REPLACE`. The closing check at line 2105 expects `>>>> REPLACE` but the stored format has bare `>>>>`.

Verified in `runner_state.json`: C0001 and C0002 both contain `==== REPLACE` separators and bare `>>>>` closers. The mismatch is deterministic and affects every finding.

**Fix:** In `parse_search_replace_blocks()`, change line 2094 to accept `====` with optional trailing text: `if lines[i].rstrip() == "====" or lines[i].rstrip().startswith("==== "):`. Also fix line 2105 to accept bare `>>>>`.

---

## 3. Immune Pipeline Flow Trace (R5)

Each step is functioning correctly in isolation:

- **Skin barrier:** 16/16 passed. Correct.
- **DC v2:** 2/16 reclassified (mathematical to code_behavioral). Reasonable for software domain.
- **LLM classifier:** 3/16 agree with regex (18.8%), 3 overrides. Low agreement is consistent across all rounds — regex default is too broad.
- **B Cell:** 0 claims checked. Correct for software domain (no mathematical claims).
- **NK v2:** 16 verdicts, 2 bugs closed. Working correctly.
- **CT v2:** 0 verdicts. Correct (no high-severity contested findings).
- **Helper T v2:** 14 findings, all DUPLICATE. Correct for R5 — models are rediscovering known bugs.
- **Reconciliation:** 14 locked (both pipelines REJECTED). Correct duplication-based removal.
- **RT v2:** AUTOIMMUNE flagged (100% removal). See Section 4.
- **Autoimmune override:** 0 resurrected. Correct — removals are legitimate duplicates.

**Assessment:** The pipeline works correctly per-step. The systemic issue is that correct duplicate detection creates a feedback loop: duplicates add CONFIRM verdicts but cannot close open entries, while the convergence gate requires 0 open entries. The system needs consensus-based closure.

---

## 4. Autoimmune Flag: Expected Depletion, Not True Autoimmune

RT v2 flags every round (R0: 75%, R1-R5: 100% removal). But the removals show `rejected=0, duplicated=N` in every case. These are genuine duplicates being correctly removed, not novel findings being falsely rejected. The 65% threshold is too aggressive for late-round depletion.

**Fix:** Split flag into AUTOIMMUNE_REJECTION (genuine) vs DEPLETION_EXPECTED (high duplicate rate with 0 rejections). Suppress when `rejected == 0 AND duplicated == total_removed`.

---

## 5. ITC Degradation

Codex and CC2 hit 5 consecutive DEGRADATION flags by R5. All suppressed by A4 gamma-aware mechanism (`rho_avg >= 0.25`). Suppression is correct — models are depleting, not degrading.

The DEGRADATION trigger is `parse_yield = findings_count / raw_finding_markers < 0.50`. In late rounds, models produce verdict-heavy output (CONFIRM/CHALLENGE), which the parser captures as verdicts not findings. This deflates parse_yield artificially.

**Fix:** Count verdicts as valid output in the parse_yield calculation.

---

## 6. Gamma Trajectory

R0/R1 are zero because `_estimate_gamma()` requires min_rounds=3 data points (line 623). With 1-2 counts, it returns 0.0. This is mathematically correct — cannot fit log-log regression with fewer than 3 points.

From R2 onwards: 0.448, 0.403, 0.432, 0.461. Healthy upward trend confirming genuine depletion. Consistently above the soft gate (0.30) and trending toward strong depletion (0.45+). Gamma would have passed convergence at every measured round. Non-convergence is entirely due to the open_ch=0 gate.

---

## 7. Novel vs Duplicate Per Round

| Round | Raw | Novel | Rho | Rho avg |
|-------|-----|-------|-----|---------|
| R0 | 16 | 16 | 1.000 | 1.000 |
| R1 | 27 | 9 | 0.333 | 0.667 |
| R2 | 14 | 4 | 0.286 | 0.540 |
| R3 | 23 | 9 | 0.391 | 0.337 |
| R4 | 15 | 1 | 0.067 | 0.248 |
| R5 | 16 | 2 | 0.125 | 0.194 |

41 canonical entries from 111 raw findings (37% yield). R4-R5 are in clear diminishing returns.

---

## Summary: Two Blocking Bugs

**P0-1: S_k format mismatch** (`reference_runner.py` line 2094 vs `runner_core.py` line 670). The separator and closer formats are incompatible between the finding parser and the S_k evaluator. 5-line fix in `parse_search_replace_blocks()`.

**P0-2: max_open_crit_high = 0** (default in RunnerConfig line 201, not overridden in config). Structurally unreachable. Set to 3-5, or implement gamma-based alternative convergence.

**P1 fixes:** Consensus-based closure for heavily-confirmed findings; split autoimmune flag for depletion vs rejection; count verdicts in ITC parse_yield; registry fix-update on duplicate.
