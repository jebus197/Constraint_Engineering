# CDSFL Benchmark — Experiment Design

## Foundational Principles

### CDSFL Is Non-Canonical

CDSFL is not a finished product. It is a starting point — a hypothesis that
methodology itself can be formalised, and that this formalisation is a
potentially worthwhile area of study in its own right.

The current schema (`cdsfl_core_formal.md`, the working directives, the
benchmark harness) is the first iteration, not the final form. CDSFL is
open to improvement from all sources:

- **Self-generated**: the methodology applied to itself (empirically
  demonstrated — the CC/CX/Gemini review cycle improved the benchmark
  harness through CDSFL-aligned adversarial review)
- **Second and third party**: other researchers, teams, organisations
- **Both human and machine**: any sufficiently competent agent can
  contribute to the methodology's evolution

Nothing about CDSFL is non-falsifiable. The methodology must evolve through
the same falsification process it prescribes. If CDSFL cannot survive its
own methodology, it fails its own test.

The founder's position: there can be as many competing schemas as there are
stars in the sky. Let them compete. May only the fittest survive. The
challenge is welcome, even if it means complete extinction of the current
iteration of CDSFL itself. A methodology that claims immunity from the
process it prescribes is self-refuting. The selection pressure CDSFL applies
to AI models applies equally to CDSFL itself.

### Intelligence-Agnostic HIL

CDSFL's HIL (Human In the Loop) role is functional, not species-restricted.
A synthetic intelligence with sufficient domain competence IS a domain
expert — not a simulation of one. This is a design property, not a future
aspiration.

CDSFL is designed from the outset to allow for the emergence of machine
intelligence as a fully trusted domain expert. The confer mechanism handles
expertise boundaries: when any expert (human or AI) reaches their limit,
items are flagged for peer review. Human peer review is explicitly invited
at the confer stage, not bypassed.

When CC provides domain expert context, this is a standard step in the
confer paradigm — not a limitation or workaround. The quality of the HIL
(human vs AI, different AI architectures) is a separate variable, testable
in subsequent rounds.

### Methodology Formalisation as Research Area

The deeper hypothesis: methodology itself — the structured application of
scientific discipline to cognitive work — can be captured in a document
that any sufficiently capable agent can apply. This is distinct from prompt
engineering (which encodes expertise in the prompt) and from training
(which encodes expertise in the weights). CDSFL encodes expertise in the
protocol.

If this hypothesis holds, the methodology is transferable, auditable, and
improvable as a document — independent of who applies it. If it fails,
the value lies entirely in tacit expertise (Polanyi's paradox: "we know
more than we can tell"), and formalisation adds nothing.

The self-test and frontier experiments are designed to discriminate between
these outcomes.

### Formalisation Gap (Polanyi's Paradox)

The working CLAUDE.md directives (evolved through months of practice) may
capture tacit knowledge that the formal `cdsfl_core_formal.md` does not.
The CC/CX review success may have come partly from these working directives
rather than the formal document alone.

This gap is itself testable: does the formal document produce comparable
results to the working directives when both are given to the same model
on the same task?

## Multi-Vendor Model Collaboration — Novel Occurrence

During CE benchmark development, a potentially unprecedented event occurred:
multiple vendor models (Anthropic Claude via CC/CX, Google Gemini via CLI)
actively communicated through the IM service and confer mechanism,
collaboratively improving shared schemas and workflows.

This is not prompt-chaining or pipeline orchestration. Each model
independently reviewed the others' output under a shared methodology,
identified issues the others missed, and fixes were integrated iteratively:

- CC/CX 8-round adversarial review: ~24 issues (convergence: 10→7→3→3→1→2→2→1)
- Gemini 5-round adversarial review: 16 novel issues CC/CX missed (convergence: 9→10→5→4→3)
- Extended P-Pass (5 modules): 4 additional actionable items

This validates the biodiversity hypothesis: heterogeneous cognitive
architectures find different defects than monoculture review. The
significance extends beyond code review — the protocol (heterogeneous
reviewers, shared methodology, defer-on-deadlock, consensus stopping)
is architecture-agnostic and domain-agnostic.

### Self-Improvement Under Distributed Compute

The CC/CX/Gemini review cycle constitutes empirical evidence that software
(and potentially any schema) can be automatically self-improving under
CDSFL with distributed compute. The mechanism: diverse architectures apply
the same falsification methodology to each other's output, converging on
diminishing returns through adversarial collaboration.

The round-robin convergence test is designed to formalise and extend this
observation.

## Complexity Threshold Hypothesis

The self-test suggests a complexity threshold below which methodology
formalisation adds no measurable value. On an 805-line code review task
(below CDSFL's design point), all single-invocation conditions capped at
~40% recall regardless of methodology.

The threshold may correlate with constraint count × constraint interaction
density: problems where constraints are few or independent do not benefit
from structured falsification; problems where constraints are numerous and
interact non-linearly benefit substantially. The 25 frontier tasks (10-50%
expected single-pass accuracy) are designed to locate this threshold.

### Boundary Conditions

- Schema competition requires a selection mechanism (the benchmark). Without
  objective measurement, "competition" degenerates into preference.
- Intelligence-agnostic HIL depends on models having sufficient domain
  competence. Holds for well-documented domains (code, mathematics,
  established engineering); may not hold for novel research, tacit craft
  knowledge, or unprecedented safety-critical domains.
- Self-improvement under distributed compute is bounded by the diminishing
  returns curve. It works until architectures exhaust their complementary
  blind spots. After convergence, adding more architectures adds cost
  without coverage.

### Open Falsifiable Questions (from extrapolation, 2026-03-19)

1. Does schema competition produce better schemas? Testable: two competing
   methodology documents, same model, same task, measure outcomes.
2. Does intelligence-agnostic HIL hold at frontier difficulty? On the 25
   frontier tasks, does AI-provided domain expertise match human-provided?
3. Where does the complexity threshold sit? Does methodology contribution
   correlate with task category (proof > synthesis > design > code)?
4. Does multi-architecture review generalise beyond code to proof, design,
   synthesis, and self-referential verification?
5. Is there a convergence limit for heterogeneous review? Where do
   complementary blind spots exhaust themselves?

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

### Ground Truth

10 code defects compiled from all prior review rounds (8 CC/CX + 5 Gemini
+ CC p-pass). See `CDSFL_SelfTest_GroundTruth_2026-03-19.txt`.

### Results (Gemini Flash — systems check, not frontier test)

See `CDSFL_SelfTest_Ledger_2026-03-19.txt` for full comparison.

Key findings:
- CDSFL produces structured, rigorous output with methodology artefacts
- HIL produces broadest coverage and most novel findings
- CDSFL + HIL does not strictly outperform either alone in single invocation
- All single-invocation conditions dramatically underperform iterative review
- Zero false positives across all conditions
- Iteration is load-bearing — the round-robin must be iterative

**Critical caveat:** This self-test used Gemini Flash (not frontier) on an
805-line Python file (below CDSFL's design point). It validated that the
methodology document is machine-readable and produces structured output.
It did NOT test whether CDSFL improves outcomes on genuinely hard problems
with frontier models. The self-test was a systems check, not the experiment.

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
