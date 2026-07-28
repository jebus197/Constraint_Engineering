# Pre-Registration — Critical / Structural Finding Definition (F6)

**PRE-REGISTERED 2026-05-18. FROZEN. Do not edit after the first
hardened-gate run.** Any change after that date is a new pre-registration
with its own dated file; the diff between pre-registration commit and
analysis commit is the hostile-reviewer audit trail.

## Why this exists

The runner used a bare `severity >= 0.7` constant as the
critical/structural boundary. The mathematical appendix documents
severity thresholds 0.0 / 0.3 / 0.5; 0.7 was an undocumented code
convention (F6). An undocumented numeric gate is indefensible to a
hostile reviewer and is the single largest cooking vector identified by
the 2026-05-17 γ-hardening confer and the 2026-05-18 definitional
confer (both unanimous on this point). This file fixes the definition
**by consequence**, in advance, so the convergence verdict cannot be
obtained by moving a number after seeing results.

## The definition (authoritative; the rubric governs, the number encodes it)

A finding is **CRITICAL / STRUCTURAL** if and only if, left unresolved,
it would plausibly cause at least one of:

1. **Wrong result** — a mathematically or logically incorrect output, or
   an invalid derivation, in the artefact's intended function.
2. **Hard-constraint violation** — breach of a physical law, a
   mathematical truth, a logical contradiction in the core constraints,
   a safety/legal absolute, or any explicit HARD constraint per the
   CDSFL constraint taxonomy.
3. **Verification-integrity corruption** — a defect in the convergence,
   reconciliation, severity, or novelty accounting itself (i.e. a bug
   that changes the *measurement* of convergence, not just the artefact).
4. **Silent evidence loss** — loss, suppression, or misclassification of
   a finding that would, if retained, change a hard-constraint
   conclusion.
5. **Unreproducibility** — an accepted result that cannot be
   reproduced from the logged inputs and fixes.

A finding is **NON-CRITICAL** (refinement / diagnostic only) if its
resolution would not change any of the above: stylistic edits, naming,
non-fatal micro-optimisation, comment phrasing, presentation, or any
change that leaves the artefact's correctness, the hard-constraint
conclusions, and the verification accounting unchanged.

## Numeric encoding (operational proxy, NOT the definition)

`CRITICAL_SEVERITY_THRESHOLD = 0.7`. The numeric `severity >= 0.7`
remains the runner's operational proxy for the rubric above. The rubric
is authoritative: where a model's numeric tag and the rubric disagree
on a finding that materially affects the convergence verdict, the
rubric governs and the adjudication is logged with its rationale
against the five clauses above. The post-mortem must report, per run:
the count of findings where rubric and numeric disagreed, and the
verdict's sensitivity to that disagreement. γ is additionally reported
at 0.5 / 0.6 / 0.7 / 0.8 so a reviewer sees the full threshold profile,
not a single chosen point.

## Anti-cooking conditions (binding)

- This file is committed before the first hardened-gate run; not edited
  after.
- The convergence verdict is computed on the SETTLED post-reconciliation
  registry (F4), never the live-at-round transient.
- The gate is the conjunction (γ-critical sustained AND zero-novel-
  critical), not the loose OR.
- All-severity γ is reported as a diagnostic and never hidden; the
  scope claim is explicitly "critical/structural convergence on the
  named artefact", never "total exhaustion".
- The verdict must be reproducible by a hostile reviewer from the
  logged registry, fixes, severity adjudications, and γ script.

Written under CDSFL note standard v1.2 (14 May 2026).
