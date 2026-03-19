# CDSFL Benchmark — Experiment Design

## Self-Test (2026-03-19): Four-Condition Methodology Comparison

### Purpose

Test whether the formalised CDSFL methodology document, given to a model
autonomously, produces measurably different results than the same model
with no guidance.

### 2×2 Matrix

|  | No HIL | HIL (domain context) |
|--|--------|---------------------|
| **No methodology** | Control | HIL only |
| **Full CDSFL** | CDSFL only | CDSFL + HIL |

Plus a fifth data point: rounds 1-5 (CC-directed iterative review without
formal methodology document).

### Conditions

**Condition 1 — Control.** Gemini receives the code and a minimal prompt:
"Review for defects." No methodology. No domain context.

**Condition 2 — CDSFL only.** Gemini receives `cdsfl_core_formal.md` (276
lines, full CDSFL loop including constraint classification, falsification
iteration, proportionality gate, corroboration model, epistemic marking,
extended p-pass structure, and behavioural directives) plus the code.
Prompt is 3 sentences: "Apply the methodology." The methodology document
does the work.

**Condition 3 — HIL only.** Gemini receives domain context (what the code
is, what it does, what matters — scientific validity, data integrity,
operational reliability, reproducibility) plus the code. No methodology
document. Standard code review instruction.

**Condition 4 — CDSFL + HIL.** Gemini receives both the full methodology
document and the domain context plus the code. This is the complete CDSFL
system: formal methodology + domain expert HIL.

**Condition 5 (historical) — HIL without protocol.** Rounds 1-5 from
2026-03-18. CC wrote detailed review prompts directing Gemini to find
specific types of issues. No formal methodology document. Reclassified
as "expert guidance without protocol."

### HIL Provision

CDSFL is intelligence-agnostic: the HIL (domain expert) role is functional,
not species-restricted. A synthetic intelligence with sufficient domain
competence IS a domain expert. CC (Claude Opus) provides domain expertise
from accumulated codebase familiarity. This does not remove or supplant
human review — the confer mechanism flags items for peer review when any
expert reaches their boundary.

### Ground Truth

10 code defects compiled from all prior review rounds (8 CC/CX + 5 Gemini
+ CC p-pass). See `CDSFL_SelfTest_GroundTruth_2026-03-19.txt`.

### Results

See `CDSFL_SelfTest_Ledger_2026-03-19.txt` for full comparison.

Key findings:
- CDSFL produces structured, rigorous output with methodology artefacts
- HIL produces broadest coverage and most novel findings
- CDSFL + HIL does not strictly outperform either alone in single invocation
- All single-invocation conditions dramatically underperform iterative review
- Zero false positives across all conditions
- Iteration is load-bearing — the round-robin must be iterative

### Design Decisions (locked)

- Control is raw single-pass, no system prompt — tests model baseline
- Calibration/placebo uses same iterative machinery as CDSFL — isolates
  directive content as the variable (NOT the iteration mechanism)
- Task order randomised to prevent systematic attrition bias
- Condition order within tasks is fixed (control → CDSFL → placebo)
- Confer mechanism is condition-neutral (not CDSFL-specific language)
- Cost cap tracks API spend for benchmark models, not confer CLI costs

### What Is NOT a Defect

These are design choices that look like bugs without context:
- Placebo sharing adaptive confer mechanism (isolates directive content)
- Adversarial pass removing system prompt (prevents methodology anchoring)
- Fixed condition order within tasks (minor bias, controlled by task randomisation)
- Constant shuffle seed (deterministic, not manifest-derived — intentional)
