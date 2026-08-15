# resources/MEMORY.md — Public Mirror of CC1 Persistent Memory

This file mirrors the project-scoped entries from CC1's (Claude Code,
instance 1) persistent auto-memory, to make visible what context an
assisting agent carries across sessions for the CDSFL project. It is a
sanitised subset: personal and cross-project entries are deliberately
excluded (see [MEMORY_EXCLUSIONS.md](MEMORY_EXCLUSIONS.md) for the
filter criteria and the full list of excluded entries).

The private index lives at
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`.
Entries listed here are the ones whose content is strictly project-scoped
methodology, project state, experimental results, or architectural
decision records — content that can live in public docs without
exposing personal preference, health/accessibility context, or
third-party-project material.

Where an entry's substance is already reflected in a canonical document
(`ONBOARDING.md`, `RECOVERY.md`, `docs/ARCHITECTURE.md`,
`docs/REPRODUCING.md`, `docs/MATHEMATICAL_APPENDIX.md`,
`experimental_notes/*`), this mirror links there rather than
duplicating. The goal is a transparent topography of what the agent
remembers, not a second canonical copy.

## Project State

- **Current state** — bench suite runs offline by default since 31 July 2026;
  counts live in `docs/CURRENT_STATE.md`, bound to a commit. (Was "1250 tests
  passing" — a figure from a run that included live model dispatch, and stale by
  ~850 tests when corrected on 31 July 2026.) Experiment 40 Stage 3
  substantially closed (Phase A + Phase B + docs sync). Residual:
  1E.3 flip (gated) and 1E.10 runtime assertion (Experiment 54).
  Anchored in `resources/RECOVERY.md`.
- **Experiment 40–54 plan** — canonical. 14 single-target experiments
  + Experiment 54 integration + a 2×2 factorial. Runner v2 scaffolded
  17 April 2026. Anchored in `experimental_notes/` and
  `docs/REPRODUCING.md`.
- **Post-Experiment 15 roadmap** — immune-style persistence, Policy
  Engine, bench run. Anchored in `resources/RECOVERY.md`.
- **Stop criterion** — bench must produce meaningful results without
  wasted compute; Occam's razor over endless iteration. The wider
  community has more compute to refine further.

## Experimental Design and Results

- **Experiment 36 ground truth + execution plan** — canonical 4-phase
  plan (A: resume, B: runner + CC2, C: Bench Run 2, D: docs). Five CC2
  sub-agents dispatched; see
  `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md`.
- **Experiment 36 CC2 agent performance** — Agent 1 broken, three of
  four under-routing, a fifth over-relied-upon. Fix priorities folded
  into Experiment 37.
- **CDSFL experiment plan** — 3-phase plan (floor / frontier /
  adversarial).
- **Self-test results** — 4-condition results; iteration is
  load-bearing (one shot is insufficient).
- **Gemini cross-review** — three-architecture review, biodiversity
  hypothesis, round-robin plan.
- **Intelligence-agnostic HIL** — an AI can serve as the domain expert
  in the Human-in-Loop role. The role is a tradable asset, not an
  organism type.
- **CDSFL documentation complete** — methodology docs are finalised;
  no further core additions planned.
- **Metacognitive command reference** — single-letter MC commands live
  in `docs/REPRODUCING.md` § Metacognitive Commands and the project
  `.claude/CLAUDE.md`. Keep those two copies in sync on any change.

## Architecture

- **Architecture layers** — Policy Engine, persistence, evidence, and
  UX are separate layers with clean boundaries. See
  `docs/ARCHITECTURE.md`.
- **Model panel config** — CC1 / CC2 identity, 5-model dispatch
  routes, confer shortcuts. CX/ChatGPT distinction collapsed.
- **Onboarding script dual purpose** — `scripts/cdsfl_onboard.py` is
  dual-purpose: environment bootstrap plus a dynamic prose reader that
  pulls project context from `resources/ONBOARDING.md` and the MC
  command reference from `docs/REPRODUCING.md` at runtime. `--full`
  and `--dry-run` flags available. `sv` and `qc` enforce the wiring.
  Key safety: never prints or transmits API key values.

## Mathematical Model

- **Model audit results** — executed 8 April 2026. Internal
  consistency sound (25/25). All 5 gaps confirmed. Two claims disputed
  (R²=0.985, z=3.63). Rho threshold needs calibration.
- **Unified self-assessment equation** — derived 8 April 2026. R_k(i)
  recursive form, π vanishes. Replaces C(n) in the operational
  directive. Full derivation in `docs/MATHEMATICAL_APPENDIX.md`.
- **Semantic novelty** — γ/ρ fed by `_finding_similarity()` content
  comparison, not an ID proxy. Added 9 April 2026.
- **ν_k novelty metric** — designed 14 April 2026. Two-dimensional
  (ν_k, c_ext). Two confer rounds: round 1 applied 7 corrections
  (3 hard, 4 soft), round 2 applied 8 (5 hard, 3 soft) — 15 in total.
  Shadow calibrator hooked. (The private memory entry's own summary
  line says "12 corrections", which matches neither round nor their
  sum; the per-round figures above are the ones the body of that same
  entry records, and `resources/RECOVERY.md` records the same 7 and
  5+3, itemised.)

## Methodology Feedback (applies to all work in the project)

These are operational rules CC1 follows when producing CDSFL work. The
intent is visible methodology, not internal policy.

- **Policy Engine naming** — never refer to the PolicyEngine as "the
  registry"; the PE and the registry are distinct components.
- **FFAFP protocol** — Find, Follow, Analyse, Fix, P-pass is a 5-step
  prompt pattern, not an enforcement/rejection mechanism. Supersedes
  the older FFF shorthand.
- **No model voting** — findings are confirmed programmatically or by
  a human in the loop, never by majority vote across models.
- **No framing confound** — avoid anchoring framing when dispatching a
  model panel; use neutral prompts.
- **Proactive QC** — sweep all related docs for staleness before every
  commit.
- **No model benching** — never bench, rest, or skip a model. In-turn
  context (ITC) means a fresh restart with fingerprint-informed scope,
  not a pause.
- **No prior-art multi-vendor** — the project carries no established
  precedent for multi-vendor frontier-model collaboration under
  structured falsification.
- **Narrow focus avoidance** — do not reduce system-level signals to
  single bivariate tests; compute aggregates first, then drill down.
- **Fixes are HIL-only** — fixes are *suggested* to the human in the
  loop, never auto-applied. The human makes the final decision.
- **Tool constraint box** — agents must operate within defined tools;
  the LLM interprets tool output, never substitutes for it.
- **Falsification gate** — P-pass is structurally enforced. Findings
  without P-pass are rejected. The 0–13% figure is a MEASURED FAILURE
  rate, not a target: models complied with the letter of the directive
  (FIND / FOLLOW / FIX sections present in 86–98% of outputs) while the
  observed P-pass rate across all models was 0–13%. That gap is the
  reason the gate exists.
- **No qualitative escape** — never give models a qualitative opt-out
  when the task is quantitative. The equation *is* the constraint
  box.
- **No binary A/B framing** — check composability before presenting
  proposals as mutually-exclusive alternatives.
- **Schema vs. tooling** — missing tools are a developer signal, not
  a schema limitation. Don't conflate the two.
- **No 'Stage N' terminology in summaries** — use concept names, not
  process stage numbers, when writing summaries and public notes.
- **Shadow code vs. deferred** — verified items that are not yet live
  are shadow code, not "deferred to production".
- **Confer protocol** — all confers run under full CDSFL + FFAFP,
  with model routing and combinable dispatch.
- **Gemini version** — Gemini is 3.1 Pro, not 2.5 Pro.
- **CC2 dispatch route** — CC2 is `claude_cli` (Max plan), never
  OpenRouter.
- **MIDCA reassessment** — "6/8 with 2 partial" is obsolete.
  Substrate agnosticism reframes Requirement 3; cross-experiment
  memory reframes Requirement 8. There are 8 extension domains
  beyond MIDCA.

## Shorthand (Metacognitive Commands) Deltas

The canonical MC reference is `docs/REPRODUCING.md` §
Metacognitive Commands. These entries flag project-specific deltas
that the memory records:

- `f` — Find, Follow, Analyse (with available tools), Fix, P-pass
  (5-step intra-model reasoning cycle).
- `sy` — use all available STEM tools (SymPy, Wolfram, SciPy, NumPy,
  z3, uncertainties, mpmath) in analysis.
- `ext` — external research (shorter alias for `re`).
- `cc2`, `cx`, `ge`, `cgpt`, `ds` — confer routing. Current panel per
  the project `.claude/CLAUDE.md` (rotated 2026-05-10): `cc2` Claude
  Opus 4.7 via CLI piped mode on the Max subscription; `cx` Codex
  GPT-5.5 via OpenRouter; `ge` Gemini 3.1 Pro Preview via OpenRouter
  (moved off the direct Google route on 2026-05-10); `cgpt` ChatGPT
  GPT-5.5 via OpenRouter; `ds` DeepSeek V4 Pro via the DeepSeek direct
  API.
- `ag` — use sub-agents to parallelise independent tasks.
- `rg` — regain full context on a named topic: re-read anchoring
  memory files, canonical docs, and experimental notes before
  producing new output. Name the resources consulted.
- `sq` — sequential: strictly one tool call at a time, no parallel
  batches. Avoids stressing upstream API servers during long
  autonomous runs. Sub-agents inherit the same constraint.
- `cy` — continue the work AND apply live-experiment monitoring
  discipline (standing directive 2026-05-18): while any experiment or
  process runs, monitor at roughly 60-second cadence; on anything off,
  pause it, analyse with all available tools, fix, then resume; keep a
  terminal tailing the running experiment's current output.
- `pr` — panel review (2026-06-03): dispatch the full model panel on a
  completed analysis or design question, run WITHOUT compelled
  convergence so each model returns an independent verdict and its
  strongest falsification, and preserve disagreement as information
  rather than smoothing it to consensus.

Commands are combinable, e.g. `cx ge cc2` = confer with all three
routes; `ag` parallelises dispatch.

## Session Handoffs (archival)

Historical handoff entries (2026-03-19, 2026-03-20, 2026-03-23)
exist in the private memory for continuity across session resumes.
Their substance has since been absorbed into the canonical docs; they
are retained privately but not mirrored here, because their content is
already in `resources/ONBOARDING.md` history or `resources/RECOVERY.md`
pending-work notes.

## What is NOT in this mirror

Entries that were excluded from this mirror — cross-project notes,
personal accessibility and working-style feedback, and founder
personal-context entries — are itemised in
[MEMORY_EXCLUSIONS.md](MEMORY_EXCLUSIONS.md) along with the filter
criteria. The exclusion log exists so that the public record is
honest about the shape of what is withheld, not only what is shown.
