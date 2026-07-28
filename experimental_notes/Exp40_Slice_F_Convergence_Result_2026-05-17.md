# Experiment 40 plan-F — Decomposed Slice Convergence Result: Post-Mortem

2026-05-17 01:30 BST

## Summary

The plan-F run converged. On the decomposed admissibility-parser slice,
with the structural cure (verified fixes applied back to a per-run
working copy), the in-round re-ask, the collision-overwrite fix, and G7
all active, the runner reached **γ-alt convergence at round 6** — three
consecutive rounds with zero novel CRITICAL findings — and stopped
early, 7 rounds into a 20-round cap. **This is the first convergence in
the entire Experiment 40 arc.** It is a genuine, defined convergence
and a clean validation of the root-cause analysis; it is also a
qualified result on the smallest target, and the qualifications are
stated in full below rather than buried.

## What converged, and the evidence it is real (not a false positive)

The R24–R28 leg produced two monitoring false positives, so this claim
was falsified hard against the authoritative report before being
recorded. It survives every check the false positives failed:

- **Authoritative field:** `converged_at = 6`, `convergence_reason =
  "GAMMA_ALT_CONVERGED: 3 consecutive rounds with zero novel CRITICAL
  (history tail=[0, 0, 0]) at round 6"` — a top-level report field, not
  a log-string heuristic.
- **The runner stopped early.** `total_rounds = 7` (R0–R6) of a
  20-round cap. The R24–R28 false positives never stopped the runner;
  this one terminated on the gate. Elapsed 5,808 s (~97 min), far below
  the 28,800 s wall-clock cap — not a timeout.
- **γ climbed, it did not plateau.** `gamma_history =
  [0.0, 0.0, 0.156, 0.135, 0.172, 0.219, 0.267]`. R24–R28 was flat at
  ≈0.05 for 25 rounds; this is qualitatively different — depletion
  accumulating, the regime the decay model associates with
  convergence.
- **The cure was actively exercised and is the plausible mechanism.**
  Four verified fixes were promoted into the working copy under the
  full-suite gate, zero rejected: `C0001` and `C0005` at round 2,
  `C0012` and `C0019` at round 3, each logged "1 block(s) applied +
  full suite green". The working copy genuinely changed (pristine 132
  lines → 135). The panel reviewed a progressively repaired artefact;
  novel CRITICAL findings fell to zero and stayed there for rounds 4,
  5, 6; γ-alt fired. This is the predicted causal chain: once the error
  space can exhaust, novelty drains and convergence occurs.
- **The in-round re-ask worked in production:** one recovery
  (`in-round re-ask [Gemini]: RECOVERED 1 findings on retry`). The
  collision-overwrite fix was active in-pipeline as a correctness
  safeguard (no collision needed handling this run).

## Qualifications (stated, not buried)

1. **Convergence was via the zero-novel-CRITICAL γ-alt path, not
   γ ≥ 0.30.** γ final = 0.267 < the 0.30 threshold; the runner logged
   "gamma: 0.267 (telemetry, passed) — Weak depletion — state closure
   may be premature". This is a real convergence by the gate wired for
   Exp 40, but the depletion magnitude is modest and the runner itself
   appends that caution. It is not γ saturation.
2. **One run, smallest slice, multiple variables changed at once.** F
   changed the target size (decomposed ~110-line slice), turned on
   apply-back, in-round re-ask, the collision fix, and used the cleaned
   baseline — all together. It validates the root-cause hypothesis and
   demonstrates the cure works; it does **not** isolate which factor is
   dominant, nor prove the general problem is solved for larger
   targets. Attributing convergence solely to apply-back would
   over-reach; the honest statement is that the combination produced
   the first arc convergence, with apply-back demonstrably exercised
   (4 promotions, working copy changed, γ rising) and consistent with
   being the key mechanism. Isolation needs the factorial follow-up the
   broader Exp 40–54 plan already provides for.
3. **Convergence ≠ all findings resolved.** Final registry: 40
   canonical — CLOSED 16, UNCONFIRMED 21, CONFIRMED 2, MERGED 1,
   **CONTESTED 0**. Convergence here means "no new critical findings
   for three consecutive rounds", not "every finding driven to
   terminal CLOSED" (21 remain UNCONFIRMED). The mid-round log line
   "Gate failed: contested=11" was a transient primary-gate check; the
   final registry has zero contested and the γ-alt gate is what
   correctly terminated.
4. **Known-inaccurate trailing string.** The runner printed
   "Experiment 40 ended without convergence (likely wall-clock)" at
   shutdown. This is the documented generic end-string bug (noted in
   the R17–R23 and R24–R28 post-mortems); it is false here. The
   authoritative record is `converged_at = 6` plus the early stop.

## Significance

This is the first convergence in the Exp 40 arc and it is evidence for
the founder's long-held position: convergence is real and was being
blocked mechanically. The R24–R28 leg (G7 on, full unfixed 621-line
artefact) was flat γ ≈ 0.05 for 25 rounds and never converged. F (small
decomposed slice + fixes actually applied back + in-round re-ask + G7 +
collision fix) converged at round 6 with γ rising 0.156→0.267 and four
fixes genuinely applied to the artefact the panel re-reviewed. The
differential is large and in the predicted direction: the dominant
blocker was that the error space never exhausted because verified fixes
were never written back. Removing that, with a right-sized target,
produced convergence.

It does not close the broader programme. It establishes, on a
controlled small target, that the diagnosed mechanism was real and the
built cure works. The next step is to widen the target and run the
factorial attribution the consolidated plan defines, to quantify how
far this scales and which factor carries it — not to declare the
general problem solved on one slice.

## Path forward (recommendation, not yet founder-approved)

1. Re-run on progressively larger slices of the cleaned baseline
   (function-group, then the full `_feedback.py`), apply-back on, to
   measure whether convergence holds as the finite error space grows.
2. Run the factorial that isolates apply-back vs decomposition vs the
   other fixes, so the causal claim is quantified not inferred.
3. Carry the C0001 / "CLOSED ≠ correct" finding into the methodology:
   the S_k admissibility threshold should not record a regressing fix
   as verified; the full-suite gate built for apply-back (plan-C) is
   the template.

## Cross-references

- Experiment 40 Remediation Build E→F Post-Mortem (2026-05-16) — the
  build this run validates.
- Experiment 40 Root Cause and Remediation Plan (2026-05-16).
- Experiment 40 R24–R28 Clean Convergence Test Post-Mortem
  (2026-05-16) — the non-converged comparator.
- Run report:
  `bench/logs/exp40_slice_admissibility_20260516T223952Z/exp40_slice_admissibility_report.json`
- Plain-English companion: Experiment 40 Slice Convergence Result —
  Plain English (2026-05-17); TTS mirror in the CDSFL TTS folder.

Written under CDSFL note standard v1.2 (14 May 2026).
