# Documentation Refresh — Third-Party Voice, Plain-English Accessibility, and AI Gender-Neutrality

**Date:** 16 April 2026, 01:07 BST
**Commit:** `0651974` on `exp39-experimental`
**Scope:** 45 experimental-notes markdown files + 49 TTS (text-to-speech) plain-text mirrors

---

## Why the refresh happened

The CDSFL (Constraint-Driven Synthesis and Falsification, a Popperian multi-vendor large-language-model falsification framework) project had accumulated approximately ninety experimental-note and TTS files in the preceding seven days (9–15 April 2026). These files were originally written as notes addressed directly to the project founder and worked well as session artefacts, but did not read as standalone documents for third-party consumers. A single consistent voice and a plain-English standard that preserves technical rigour were required.

Three specific problems drove the refresh:

1. **Voice.** Files spoke to the founder directly, using *you*, *your*, *we*, *I*.
2. **Accessibility.** Technical terms appeared without first-use glosses, on the implicit assumption of session context.
3. **AI-model pronouns.** Several files referred to Gemini using feminine pronouns (*she*, *her*). This is a training-data artefact (users select Gemini's default female TTS voice) that had propagated into the written record. Model branding and product voice selections do not constitute gender.

---

## What changed

### Global CLAUDE configuration (`~/.claude/CLAUDE.md`)

Three new directives added, expanding the existing `tts-output-protocol`:

- **`tts-plain-english`** — Both `.txt` and `.md` outputs must be clear plain English, accessible to an outside reader who lacks session context, but not dumbed down. Technical rigour preserved: every file path, commit hash, LOC count, test count, percentage, equation, and numerical value remains verbatim. Domain-specific terms are introduced inline with a one-clause gloss on first use (e.g. "kappa_set, the set-level convergence metric, reached 0.461"). A competent outside reader — a mathematician or scientist in an adjacent field — should follow the document end-to-end without a glossary.

- **`tts-third-party-voice`** — No direct address to the user (no *you*, *your*), no conversational narration (*as discussed*, *here's what I did*), no first-person plural implying a shared session (*we decided*). Decisions are reported as decisions. Human collaborators retain their own names and pronouns when referenced.

- **`public-gender-neutral-ai`** — AI models take the pronoun *it* or the model's name. Applies to Gemini, Claude, CC1, CC2, Codex, ChatGPT, DeepSeek, and future models. Model branding, default voice selections, and anthropomorphic nicknames do not constitute gender. Human co-authors, scientists, philosophers, and named examples (Alice/Bob in cryptography) retain their own pronouns.

### Repository sweep (CE repo `experimental_notes/` + `resources/`)

Six parallel reformatting agents, one per date (9, 10+11, 12, 13, 14, 15 April), processed:

- **45 markdown notes** in `experimental_notes/`
- **49 TTS plain-text files** in `~/Desktop/CDSFL_tts/`
- **2 state files** (`resources/ONBOARDING.md`, `resources/RECOVERY.md`) with Gemini pronoun corrections applied directly

Each file received:

1. **Voice normalisation** — direct address removed; descriptive third-person or passive throughout.
2. **Inline glosses** on first use of domain-specific terms: CDSFL, FFAFP (Find, Follow, Analyse, Fix, P-pass), R_k(i) (iterative residual-risk self-assessment), η_int (internal novelty), ν_k (literature novelty), w(f) (continuous suppression weight), kappa_set (set-level convergence metric), Stage 6, §17 (Feedback Channel), §18 (Divergence Directive), S_k (severity/stringency tristate gate), Jaccard (token-overlap similarity), HIL (human-in-the-loop), AIS (Artificial Immune Systems), and others.
3. **AI-model pronoun correction** — Gemini, CC2, and any other AI model referenced with gendered pronouns corrected to *it* or the model name.

Markdown structure preserved in `.md` files. TTS `.txt` files stripped of any residual hash symbols, asterisks, pipes, em-dashes, en-dashes, or Unicode bullets that would read as noise under TTS.

---

## Scope and method

| Metric | Value |
|---|---|
| Total repo files committed | 47 |
| Desktop TTS mirrors updated | 49 |
| Commit hash | `0651974` |
| Branch | `exp39-experimental` |
| Insertions / deletions | 366 / 336 |
| Technical content changes | zero (equations, paths, hashes, counts all verbatim) |

Verification: three independent post-edit grep passes.

- Zero AI-model gendered pronouns remain in either the repository or `~/Desktop/CDSFL_tts/`.
- Zero first- or second-person direct address remains in any reformatted TTS file.
- Inline glosses present on first use in each document.

---

## What generalises

The third-party-voice and plain-English standards now apply to every future TTS file and experimental note in CDSFL and in any other project using the same convention. A competent outside reader — a mathematician, a scientist in an adjacent field, a careful journalist — must be able to follow a document end-to-end without a glossary.

The AI-gender-neutrality rule extends beyond Gemini. It applies uniformly across Claude, the two Claude Code instances CC1 and CC2, Codex, ChatGPT, DeepSeek, and any future model. Model branding and default voice selections are product decisions, not attributes of the model.

---

## What did not change

No substantive framework change. No equations touched. No experimental design shifts. No revision to the three founder decisions pending before Experiment 40 (channel reassignment, contrast-statement requirement, experimental-design Option B or Option C). The refresh was a documentation operation, not a substantive one.

---

## Forward implications

Forthcoming TTS files and experimental notes are produced to the new standard from the outset. Files older than seven days remain in their original voice. Extending the sweep to the full archive is a straightforward batch operation if requested.
