# Run 5 Analysis — Baseline Confer (Self-Referential)

**Date:** 1 April 2026, 15:44 UTC
**Duration:** 8,155 seconds (~2h 16m)
**Rounds:** 5 (R0 blind + R1–R4 adaptive)
**Models:** CC2 (Opus 4.6), Codex (GPT-5.4), ChatGPT (GPT-5.4), Gemini (3.1 Pro), DeepSeek (Reasoner)
**Target:** `dynamic_management.py` immune response layer (the code governing the models' own dispatch)

## 1. Headline Numbers

| Metric | Value |
|--------|-------|
| Total findings (reported) | 121 |
| Total findings (corrected — see §3) | **155** |
| Duane γ | 0.112 |
| Popper C(H,E) | 0.847 (strong corroboration) |
| Cognitive yield per round | 15.93 → 11.3 → 15.57 → 10.57 → 16.28 |
| Convergence | **Not reached** (γ = 0.112, threshold = 0.5) |

The system did not converge. γ = 0.112 means vocabulary is still growing rapidly — the models kept finding genuinely new things. The oscillating cognitive yield (no monotonic decline) reinforces this: the immune layer has substantial undiscovered surface area.

## 2. Per-Model Performance

### Reported vs Corrected Finding Counts

| Model | R0 | R1 | R2 | R3 | R4 | Total (reported) | Total (corrected) |
|-------|----|----|----|----|----|----|------|
| CC2 | 16 | 12 | 14 | 11 | 12 | **65** | 65 |
| Codex | 5 | 5 | 5 | 2 | 4 | **21** | 21 |
| ChatGPT | 1 | 1 | 1 | 1 | 1 | **5** | **34** |
| Gemini | 4 | 2 | 1 | 2 | 4 | **13** | 13 |
| DeepSeek | 3 | 1 | 5 | 2 | 6 | **17** | 17 |

### CC2 (Opus 4.6) — Dominant performer

65 findings across 5 rounds. Consistent output (11–16 per round). No timeouts,
no fallbacks needed. Single-turn dispatch via OpenRouter worked every time.
CC2 received the full prompt directly — the immune extraction (271K → 115K chars)
plus composed directives kept it within context. CC2 produced the most detailed
FFF-structured findings, with explicit FIND/FIX/FOLLOW sections and line
references. This is the model that set the quality bar.

### Codex (GPT-5.4 via CLI) — Reliable after fallback

21 findings. Timed out at 600s in R1 and R2 (both on the full immune prompt).
Both times the multi-turn decomposed fallback fired and recovered: 4 chunks
delivered, 5 findings each time. In R3–R4, sub-area rotation kicked in (the
prompt exceeded threshold), routing Codex to smaller slices (LoadBalancing,
Persistence). No timeouts in R3–R4 once sub-area rotation was active.

**Multi-turn fallback worked exactly as designed.** Without it, Codex would
have produced 0 findings in R1 and R2 — the fallback recovered 10 findings
that would have been lost. The fallback added ~630s and ~880s overhead
respectively, but delivered.

Coherence budget warnings appeared every round for Codex
(`density=0.0287, budget=0.012`). Two directive families were pruned each time:
`software_distributed::intra` and `software_distributed`. This means Codex
operated with a reduced directive set throughout — it never received the full
CDSFL situation directive. Despite this, it still produced substantive findings,
particularly on the Persistence and LoadBalancing sub-areas in later rounds.

### ChatGPT (GPT-5.4 via OpenRouter) — Parser bug masked output

**Reported: 5 findings. Actual: 34 findings.**

This is the most significant operational finding from Run 5. ChatGPT
consistently produced well-structured JSON arrays (5–10 objects per round)
with proper FINDING_ID, SEVERITY, FLAW_CLASS, DESCRIPTION fields. The
parser failed to recognise JSON-formatted output:

- The tuple parser expects `(F001, 0.9, ...)` — ChatGPT uses `[{"FINDING_ID": ...}]`
- The marker parser expects `FINDING_ID: IM_F001` — ChatGPT uses `"FINDING_ID": "IM_F001"` (JSON quotes around the key break the regex)
- The parser fell through to the unstructured fallback, creating 1 generic finding per round

ChatGPT also produced `_FOLLOW` companion entries for each finding (FFF pattern),
bringing total JSON objects to 34 base findings + follow-ups across 5 rounds.
Response times were fast (49–83s) and consistent. No timeouts.

**This is a parser bug, not a model performance issue.** ChatGPT's actual
contribution is comparable to Codex. Fixing the parser to handle JSON arrays
would recover ~29 lost findings from this run alone.

### Gemini (3.1 Pro) — Steady, low-volume

13 findings. Response times ranged from 268s to 354s — the slowest model
per-finding but always completed within timeout. Gemini produced fewer
findings but at higher average quality (longer descriptions, more specific
line references). Sub-area rotation activated in R4 when the prompt grew
past Gemini's threshold. Coherence budget was fine (no pruning).

### DeepSeek (Reasoner) — Improving trajectory

17 findings, with a notable upward trend: 3 → 1 → 5 → 2 → 6. DeepSeek
required decomposition every round (`DISPATCH BLOCKED` in R0, coherence
budget exceeded in all rounds, sub-area rotation from R1 onward). Reasoning
tokens were substantial (14–29K chars of reasoning per response), indicating
genuine deep analysis even on smaller sub-areas.

DeepSeek's R4 was its best round (6 findings), suggesting that as the
sub-area rotation reached Persistence (a more constrained subsystem), its
reasoning-heavy approach found more traction.

## 3. Script and Infrastructure Performance

### Multi-turn Decomposed Fallback

- **Fired:** 2 times (Codex R1, Codex R2)
- **Recovery rate:** 2/2 (100%)
- **Overhead:** 626s and 882s respectively
- **Findings recovered:** 10 (5 + 5)
- **Verdict:** Working as designed. Without this infrastructure, Run 5 would
  have lost 10 findings and Codex would have been 50% less productive.

### No-Exclusion Policy

- **Fired:** Round 2 — the immune layer attempted to ABORT CC2 and EXCLUDE
  all four other models simultaneously
- **Actions intercepted:** ABORT × 1 (CC2), EXCLUDE × 4 (Codex, ChatGPT,
  Gemini, DeepSeek)
- **Override:** All 5 models added to `pre_decompose_models` set
- **Verdict:** Critical safeguard. The immune layer, reviewing its own code,
  reached a state where it wanted to kill every model — a direct consequence
  of the self-referential test design. Without no-exclusion, Run 5 would have
  terminated at Round 2 with 76 findings instead of 121 (155 corrected).

This is the ouroboros biting. The models found enough flaws in the immune
layer that the immune layer's own escalation logic fired against all of them.
The no-exclusion policy correctly identified this as a feature of the test
design, not a genuine system failure.

### FSM Terminal State Guard

- **Fired:** Round 3 and Round 4
- **Reason:** `TerminationReason.FAILURE` — the FSM entered terminal state
  after the immune layer's mass-exclusion attempt
- **Guard behaviour:** Caught the RuntimeError, logged it, saved checkpoint,
  continued without DM feedback
- **Verdict:** Working as designed. The Run 4 crash that killed the previous
  experiment at Round 3 has been fixed. The guard preserved data and allowed
  the run to continue for 2 more rounds, producing 45 additional findings
  (18 + 27).

### Coherence Budget

Codex and DeepSeek consistently exceeded their coherence budgets. Two
directive families were pruned each time. This is a known constraint of
smaller-context models receiving complex situation directives. The pruning
did not prevent either model from producing findings, but it means they
operated under a reduced CDSFL specification. Whether this affected finding
quality is unknown without a controlled comparison.

### Sub-Area Rotation

Activated automatically when prompts exceeded model thresholds:
- Codex: from R0 onward (Detection → Response → Immune → LoadBalancing → Persistence)
- DeepSeek: from R0 onward (Detection → Response → Integration → LoadBalancing → Persistence)
- Gemini: R4 only (Persistence)
- ChatGPT: R3–R4 (Immune → Immune)
- CC2: all rounds on full immune layer (no rotation needed — large enough context)

The rotation ensured all sub-areas received coverage across models and rounds,
even when individual models couldn't handle the full prompt.

## 4. Immune/Adaptive Layer Performance (Self-Review)

The models found 121 (155 corrected) issues in the immune layer itself. The
most frequently targeted subsystems:

- **FailureHandler** — escalation logic, lifetime counting vs windowed counting,
  idempotency issues, role downgrade propagation
- **DetectorHealthMonitor** — effective_window growth bug (backwards persistence
  sensitivity), remediation chain boundaries, false positive rate computation
- **Remediation chains** — missing definitions, pathology_key omissions, chain
  exhaustion boundary conditions
- **Self-diagnosis** — candidate ordering violates simplest-sufficient principle

The immune layer's own escalation logic was the most attacked surface. Multiple
models independently found that `FailureHandler.get_recovery()` uses lifetime
failure counts rather than windowed counts, causing transient failures to
accumulate permanently. This is a genuine architectural flaw — the same
windowing approach used in UNDERPERFORM detection should apply to escalation.

The effective_window growth bug (IM_F003 from CC2 R0) is particularly notable:
the persistence multiplier makes the window LARGER for persistent pathologies,
which is the exact opposite of the intended behaviour. Persistent pathologies
should trigger faster detection, not slower.

## 5. FFF Effectiveness

### Structured FFF (explicit Find-Fix-Follow sections)

CC2 and Codex consistently produced structured FFF output with clearly
delineated FIND, FIX, and FOLLOW sections. CC2's findings included inline
diff-style code patches and downstream impact analysis. Codex (via multi-turn
fallback) also produced FFF when given the situation directive's FFF
instruction in the final chunk.

ChatGPT produced FFF naturally — each finding has a base entry and a `_FOLLOW`
companion documenting downstream consequences. This is structurally correct FFF
even though the parser didn't recognise it.

### Implicit FFF

Gemini and DeepSeek produced findings with PROPOSED_FIX fields but did not
always include explicit FOLLOW sections. DeepSeek's reasoning chain (visible
in the reasoning tokens) shows FFF-like iteration internally, but the output
condensed it into FIND + FIX.

### Assessment

FFF worked well where models received the full situation directive (CC2,
Codex via fallback). Models that received pruned directives (DeepSeek) or
operated on sub-areas (all except CC2) produced FFF less consistently. The
directive composition layer should consider FFF instruction preservation as a
hard constraint during coherence budget pruning.

## 6. Key Findings for Immediate Action

1. **Parser bug (ChatGPT JSON format):** Fix `parse_findings()` to handle
   JSON array responses. This recovers ~29 lost findings from Run 5 and
   prevents systematic under-counting of any model using JSON output format.

2. **effective_window growth direction:** The persistence multiplier is
   backwards. Multiple models flagged this independently. Should be division,
   not multiplication, plus a cap at 2× base_window.

3. **Lifetime vs windowed escalation:** `FailureHandler.get_recovery()` uses
   lifetime failure counts. Should window to recent rounds, matching the
   approach already used for UNDERPERFORM detection.

4. **No-exclusion was load-bearing:** Without it, the run dies at R2. For
   future self-referential tests, no-exclusion is mandatory infrastructure.

5. **FSM terminal guard was load-bearing:** Without it, the run dies at R3.
   Both safeguards validated.

## 7. Scope for Improvement

- **Parser robustness:** Add JSON array detection as a first-pass parser
  before tuple and marker parsers. This is the highest-value fix — it
  recovers the most data.
- **CX timeout tuning:** 600s is too short for Codex on full immune prompts.
  The multi-turn fallback adds 600–900s. Either increase the primary timeout
  to 900s or pre-decompose Codex by default for prompts > 100K chars.
- **Coherence budget for FFF:** Ensure FFF instructions survive directive
  pruning. Currently `software_distributed` families get pruned, which may
  include FFF-relevant content.
- **DeepSeek dispatch efficiency:** DeepSeek was blocked or decomposed every
  round. Its token limit relative to prompt size means it always needs sub-area
  rotation. Pre-computing the routing rather than blocking-then-decomposing
  would save one round-trip.
- **Convergence target:** γ = 0.112 after 5 rounds is far from the 0.5
  threshold. Either the immune layer needs many more rounds to converge, or
  the convergence threshold should be reconsidered for self-referential tests
  where the target code is inherently complex.

## 8. Statistical Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| γ (Duane) | 0.112 | Very far from convergence — rich unexplored surface |
| C(H,E) | 0.847 | Strong Popper corroboration vs control baseline |
| P(E\|H) | 24.2 findings/round | High detection rate |
| P(E) | 2.0 findings/round | Control baseline (Bench Run 1) |
| Cognitive yield | oscillating (10.6–16.3) | No monotonic decline — not exhausted |

The non-convergence and oscillating cognitive yield together indicate that 5
rounds is insufficient for this target. The immune layer at ~115K chars with
multiple interacting subsystems (detection, remediation, failure handling,
self-diagnosis, persistence) has a vulnerability surface that requires either
more rounds or a more targeted per-subsystem approach to reach convergence.
