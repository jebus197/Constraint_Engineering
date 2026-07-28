# resources/MEMORY_EXCLUSIONS.md — What Was Withheld From the Public Mirror

Companion document to [MEMORY.md](MEMORY.md). The public mirror of
CC1's (Claude Code, instance 1) persistent memory filters out entries
that would expose personal context, cross-project material, or
operating procedure scoped to a specific collaborator. This file lists
what was filtered and the criterion that filtered it, so the public
record is honest about the shape of what is withheld, not only what is
shown.

The source index lives privately at
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`
and contains 65 individual memory files. Of those, 11 are excluded
below, 2 are cross-project, and the remainder are mirrored (in
summarised form) in `MEMORY.md`.

## Filter Criteria

An entry is EXCLUDED from the public mirror if any of the following
hold:

1. **Cross-project scope.** The entry is about a different project
   (e.g. Metis, Project Genesis) that happens to share CC1's memory
   store. These do not belong in the CDSFL public record.
2. **Personal or accessibility context.** The entry documents the
   founder's working style, accessibility needs, health context, or
   a specific tool used to compensate for those (e.g. TTS output for
   dyslexia-related reading accommodation). These are not appropriate
   for public project docs.
3. **Founder-personal ideology or political motivation.** The
   founder's personal political or philosophical framing is private
   context for CC1 only, and the explicit standing rule is that only
   technical citations enter public docs.
4. **Operational feedback directed at CC behaviour.** Rules that
   instruct CC how to address or interact with the founder (e.g.
   "no self-flagellation", "apply drafted edits without stalling").
   These are internal working-style guidance, not methodology.

## Excluded Entries

### Cross-project scope

- **`project_metis.md`** — Metis (agent harness) project notes;
  pre-implementation, blocked on CDSFL prerequisites. Not part of
  the CDSFL repo.
- **`feedback_metis_sv_local.md`** — sv routing for Metis is
  local-only until that project acquires a git remote. Metis-scoped.

### Personal or accessibility context

- **`feedback_accessibility_recovery.md`** — use TTS files for
  context recovery. Describes a personal accommodation for
  dyslexia-related text consumption.
- **`feedback_tts_format.md`** — TTS plain-text format conventions
  for Firefox Read Aloud (reference file, zero-markdown rules,
  section-break conventions). The format exists because of the
  founder's accessibility requirements.
- **`feedback_tts_dissemination.md`** — third-party-readable voice
  conventions for TTS and experimental notes. Same accessibility
  context.
- **`feedback_no_jargon_tts.md`** — avoid software jargon in TTS and
  notes; use plain English. Same accessibility context.

### Founder-personal context

- **`founder_privacy_boundary.md`** — the source-of-truth rule that
  founder personal ideology is private context for CC only; only
  technical citations go in public docs.
- **`founder_scientific_method.md`** — the founder's Popperian
  framing and novel-input heuristic. Partially reflected
  (methodologically) in public docs; the personal-framing entry
  itself is kept private.

### Operational feedback directed at CC behaviour

- **`feedback_self_flagellation.md`** — errors get analytical
  responses, not apologies. Instruction about CC's response style,
  not project methodology.
- **`feedback_apply_drafted_edits.md`** — once edits are drafted,
  apply them; don't stall with "should I proceed?". Instruction
  about CC's execution discipline, not project methodology.
- **`feedback_factual_synthesis.md`** — deliver evidence-grounded
  analysis; don't amplify founder framings into theses. Instruction
  about CC's analytical discipline.
- **`feedback_hil_fatigue.md`** — the system must converge to ONE
  recommendation, not present a buffet. Partially methodology, but
  phrased as an instruction about how CC should present output to
  the founder. The methodology element (single convergent
  recommendation, not multiple-choice) is captured as a design
  principle elsewhere.
- **`feedback_long_session_degradation.md`** — 18+ hour sessions
  cause term conflation; fresh starts safer than contaminated
  continuations. Operational rule for CC session management.
- **`feedback_quote_convention.md`** — single-vs-double quote
  convention for paraphrase vs. verbatim citation. An interaction
  convention between CC and the founder.
- **`feedback_naming_conventions.md`** — no unagreed acronyms, and
  use "the founder" rather than the personal name in public docs.
  The *public-doc* half is in force throughout this repo (it's the
  reason "the founder" appears instead of a name in the paper and
  project docs); the private half is about interaction style.

## Entries That Required Judgment

A few entries sat on the line between methodology and personal
operating procedure. They are recorded here for transparency:

- **`feedback_tts_format.md` / `feedback_tts_dissemination.md`** —
  the underlying principle (public-facing docs should be
  third-party-ready, not AI-addressing-user) is a project
  documentation standard. The full entries, however, bake in TTS
  accessibility context that is personal. Decision: exclude the
  entries; the universal principle is already implicit in how
  `resources/ONBOARDING.md`, `experimental_notes/*`, and the public
  README are written.
- **`feedback_hil_fatigue.md`** — the underlying principle (system
  converges to one recommendation) is architectural. The entry
  itself is phrased as an instruction to CC about founder
  interaction. Decision: exclude the entry; the architectural
  principle is in `docs/ARCHITECTURE.md`.
- **`feedback_naming_conventions.md`** — the "the founder" naming
  convention is applied visibly across the public docs; the
  convention itself is personal. Decision: exclude the entry; the
  effect is observable in the prose.

## Verification

This exclusion log can be re-derived by comparing entries in
`MEMORY.md` with the source index at
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`.
If an entry is in the source index but neither in `MEMORY.md` nor in
this exclusion log, that is an omission bug — please report it.
