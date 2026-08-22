# resources/MEMORY_EXCLUSIONS.md — What Was Withheld From the Public Mirror

Companion document to [MEMORY.md](MEMORY.md). The public mirror of
CC1's (Claude Code, instance 1) persistent memory filters out entries
that would expose personal context, cross-project material, or
operating procedure scoped to a specific collaborator. This file lists
what was filtered and the criterion that filtered it, so the public
record is honest about the shape of what is withheld, not only what is
shown.

## Accounting (counted 2026-08-08 07:40 BST)

The source index lives privately at
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`.
Every figure below was counted from that directory on the date in this
heading, not carried forward from a previous version of this file.
The directory holds **103 files**, of which one is `MEMORY.md` itself
(the index), leaving **102 individual memory files**. They partition as:

| bucket | count |
|---|---|
| Mirrored (in summarised form) in `MEMORY.md` | 55 |
| Named as excluded, with a reason, below | 15 |
| Session handoffs, declared in `MEMORY.md` as retained privately and deliberately not mirrored | 3 |
| **Unclassified — neither mirrored nor previously declared** | **39** |
| total | 112 |

> **[Correction 2026-08-22.]** Mirrored 51 -> 55, total 108 -> 112 for
> `cdsfl_session_2026-08-18_to_22.md`, `cdsfl_bugzilla_design_2026-08-21.md`,
> `feedback_check_the_whole_set.md` and `cdsfl_session_2026-08-22_track_record.md`.
> All four carry an index line in `MEMORY.md`, so all four land in the mirrored
> bucket. **FIFTH consecutive correction in the same direction.** The fix recorded
> on 2026-08-17 — move the ledger bump into the `sv` path so it stops depending on
> the author remembering — was never implemented. The check keeps working and the
> remedy keeps not being built. That is the defect, not the count.

> **[Correction 2026-08-18.]** Mirrored 50 -> 51, total 107 -> 108 for
> `cdsfl_runway_2026-08-18.md`, the runway tracker.

> **[Correction 2026-08-17.]** Mirrored 49 → 50 and total 106 → 107 for
> `cdsfl_session_2026-08-17.md`. Fourth consecutive correction in the same direction —
> the ledger update belongs in the `sv` path, not the author's memory.

> **[Correction 2026-08-16.]** Mirrored 48 → 49 and total 105 → 106.
> `cdsfl_session_2026-08-16.md` was written this session and carries an index line in
> `MEMORY.md`, so it lands in the mirrored bucket. The accounting check went red on the
> mismatch again, which is again the check working rather than drifting. Noting the
> pattern rather than only the instance: this ledger has now been corrected on 2026-08-08,
> 2026-08-13 and 2026-08-16, always in the same direction — a memory file is written and
> the ledger is not updated in the same action. The check catches it every time, so
> nothing is lost, but the repetition says the ledger update belongs in the `sv` path
> rather than in the author's memory.

> **[Correction 2026-08-13.]** Mirrored 45 → 48 and total 102 → 105. Three memory files
> were written on 12–13 August and each carries an index line in `MEMORY.md`, so all three
> land in the mirrored bucket: `cdsfl_session_2026-08-12.md`,
> `cdsfl_note_standard_v1.3.md` and `cdsfl_note_standard_v1.4.md`. The accounting check in
> `bench/tests/test_recovery_memory_doc_repairs.py` went red on the mismatch, which is the
> check working: memory files were added without the ledger being updated, and it said so
> rather than drifting. Same failure the `sv` completeness check caught the day before.

**[Recount 2026-08-08.]** `feedback_help_must_never_cost_money.md` was added on
2026-08-07 — the rule that a `--help` must never bill the reader. Mirrored, so 44
becomes 45 and the total 101 becomes 102. This is the SECOND time this check has
gone red for the same reason: a memory written, correctly, by an agent that then
did not recount the ledger. The check is doing its job; the habit is the defect.

**[Recount 2026-08-06.]** One file was added since the previous count:
`cdsfl_session_2026-08-05.md`, the record of the recovery-resource audit. It
is mirrored in `MEMORY.md`, so it joins the first bucket — 43 becomes 44 and
the total 100 becomes 101. This recount exists because the accounting test
went RED the moment the file landed, which is the behaviour that document and
test were built for: a memory added without being classified stops the buckets
summing, and the document whose whole purpose is honesty about what is withheld
does not get to drift silently.

The 39 unclassified files are listed in their own section near the end of
this document. By this document's own Verification rule they are omission
faults, and they are named here rather than left silent. **No exclusion
reason has been assigned to any of them** — assigning one is a founder
decision, not a documentation decision.

The counts this file previously carried — "65 individual memory files",
"11 are excluded below, 2 are cross-project" — were wrong on both halves.
The directory had grown to 100 files, and the section below names 15
entries (13 of them non-cross-project), not 11 plus 2.

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

Fifteen entries, counted from the four subsections below on 2026-08-05:
2 cross-project, 4 personal/accessibility, 2 founder-personal, 7
operational-feedback.

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

## Unclassified — awaiting review

**These 39 files exist in the private memory directory and are neither
mirrored in `MEMORY.md` nor excluded under any criterion above.** Under
the Verification rule at the foot of this document, each is an omission
fault. They are named rather than left silent; none has been assigned an
exclusion reason, because none of the four criteria above demonstrably
applies to them and inventing a reason would defeat the purpose of this
document. Each needs a publication ruling: mirror it, or exclude it under
a stated criterion.

Listed alphabetically, exactly as they appear on disk (counted
2026-08-05 18:00 BST):

- `cdsfl_note_standard_v1.1.md`
- `cdsfl_note_standard_v1.2.md`
- `cdsfl_note_standard_v1.md`
- `cdsfl_session_2026-06-07.md`
- `cdsfl_session_2026-06-08.md`
- `cdsfl_session_2026-06-10.md`
- `cdsfl_session_2026-07-02.md`
- `cdsfl_session_2026-07-12.md`
- `cdsfl_session_2026-07-19.md`
- `cdsfl_session_2026-07-22.md`
- `cdsfl_session_2026-07-27.md`
- `cdsfl_session_2026-07-28.md`
- `cdsfl_session_2026-08-01.md`
- `feedback_15_experiments.md`
- `feedback_1e10_catch.md`
- `feedback_ask_for_founder_held_evidence.md`
- `feedback_bcell_not_tool.md`
- `feedback_communication_density.md`
- `feedback_compelled_convergence.md`
- `feedback_complete_task_lists.md`
- `feedback_fault_severity_convention.md`
- `feedback_fix_all_scope_split.md`
- `feedback_launcher_config_drop.md`
- `feedback_no_fake_model_labels.md`
- `feedback_no_mechanical_tts.md`
- `feedback_no_session_deferral.md`
- `feedback_notes_paired_output.md`
- `feedback_object_of_study.md`
- `feedback_read_the_clock.md`
- `feedback_runner_v1_v2.md`
- `feedback_shadow_promotion_now.md`
- `feedback_simplest_sufficient.md`
- `founder_hil_is_by_design.md`
- `mc_commands_nonoptional.md`
- `multi_tool_crossverify.md`
- `project_exp29_plan.md`
- `project_outreach_plan.md`
- `project_run12_gemini_customtools.md`
- `project_three_layer_schema.md`

## Verification

This exclusion log can be re-derived by comparing entries in
`MEMORY.md` with the source index at
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`.
If an entry is in the source index but neither in `MEMORY.md` nor in
this exclusion log, that is an omission bug — please report it.

The check is mechanical and is pinned by a test:
`bench/tests/test_recovery_memory_doc_repairs.py` counts the files on
disk, reads the buckets out of this document, and fails loudly if the
four buckets do not partition the directory exactly — if a file is in no
bucket, in two buckets, or if the totals stated above stop matching the
count. A silently drifting accounting is the failure this document exists
to prevent, so the test asserts the arithmetic rather than trusting the
prose.
