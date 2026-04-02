# Recursive Falsification: The Methodology Applied to Itself and Human Input

**Date:** 2 April 2026
**Trigger:** Founder observation — existing machinery self-regulates; human input is also falsifiable
**Status:** ANALYSIS — extends adaptive immune verification design

## Observation 1: Existing Machinery Regulates the T-Cell Layer

The `DetectorHealthMonitor` metrics map directly onto the verification layer:

| Generator metric | Verification layer equivalent |
|---|---|
| kappa (inter-model agreement) | Do verification agents agree on verdicts? |
| mu (cost per finding) | Cost per verified finding |
| novelty (are findings new?) | Are verification errors new or repeated? |
| FPR (false detection rate) | How often do verifiers wrongly reject valid findings? |
| self-diagnosis | Does the verification layer detect its own degradation? |

`DetectorHealthMonitor` can be instantiated twice — once for generators,
once for verifiers. Same code, same metrics, different target population.
No new monitoring code needed.

D-decay convergence applies at every level. When γ at level N exceeds
threshold, level N is stable. The termination problem ("who verifies
the verifiers of the verifiers?") has a mathematical answer: each level
converges independently via the same Duane model.

## Observation 2: Human Input Is Also Falsifiable

The pipeline currently treats human input (task description, system
prompt, HIL guidance, design decisions) as HARD constraints. But human
input is a hypothesis, subject to framing, anchoring, availability, and
confirmation bias.

**Already demonstrated empirically:**
- **Decomposition design:** ChatGPT flagged a human-originated decomposition
  as a "completeness failure." The machine falsified a human design decision.
  Founder corrected it.
- **HIL narrowing (Confound #5):** Expert hints narrow model search space.
  Human input error, documented but not yet fixed.
- **Context injection:** Human design choice to inject all findings. Run 7b
  proved it wrong (76% noise). Models suffered from a human architectural
  decision.

The compound objective Ω is substrate-agnostic — it doesn't distinguish
between human-originated and machine-originated errors. The Duane model
measures system convergence regardless of error source.

## Convergence: The Closed Loop

The methodology applies at every level:

1. **Target code** — generators find bugs (current)
2. **Generator output** — verification agents check findings (proposed)
3. **Verification output** — meta-verifiers check verifiers (proposed)
4. **Human input** — models flag problematic design decisions (informal, not formalised)
5. **The methodology itself** — D-decay measures process convergence (implemented)

At every level: generate claim → falsify → measure error rate → converge.

## Formalising Human Input Verification

S_sync (sycophancy detection) already measures whether models under-challenge
human assumptions. Low S_sync = too much agreement = sycophancy signal.

**Proposed pre-dispatch input review:**
After founder specifies a task, before dispatch, one agent reviews the
task specification for:
- Ambiguity
- Contradictions
- Unstated assumptions
- Framing bias

Not adversarial — a quality check on input, same as quality checks on
output. Founder retains final authority, but informed authority > unchallenged
authority.

## Extrapolation

- **Code review:** Who reviews the reviewer's criteria? CDSFL: measure
  whether criteria produce convergent results.
- **Peer review:** Reviewers assumed competent. CDSFL: measure reviewer
  error rates with D-decay.
- **AI alignment:** Who verifies human preferences in training data?
  CDSFL: all claims falsifiable, including alignment targets.
- **Governance:** Standards assumed correct. CDSFL: measure whether
  standards produce convergent regulated outcomes.

**Boundary condition:** breaks down where no objective ground truth exists
(aesthetic preference, ethical judgment). There, methodology shifts from
falsification to fitness assessment per `rigour-universal`.

## Falsifiable Question

Does formalising human-input verification produce better system outcomes
than informal pushback? Testable: compare convergence rates in runs with
vs without pre-dispatch input review. If input review catches assumptions
that would otherwise waste compute (like unbounded context injection),
measurably yes.

## Implementation Note

No new code required for the self-regulating T-cell layer — instantiate
`DetectorHealthMonitor` twice. For human-input verification, add a
pre-dispatch review step using local `claude` CLI (~50 lines in runner).
