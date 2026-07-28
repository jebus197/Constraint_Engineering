# Session Summary — 16 April 2026

**Date:** 16 April 2026, 01:00–02:30 BST
**Branch:** `exp39-experimental`

---

## Part 1 — Documentation refresh

The project had accumulated approximately ninety files over the preceding week that were written as notes addressed directly to the founder. Three problems were fixed across all of them:

1. **Voice normalisation** — direct address removed; descriptive third-person or passive throughout.
2. **Inline glosses** — domain-specific terms introduced with a one-clause explanation on first use.
3. **AI-model pronoun correction** — gendered pronouns for AI models corrected to *it* or the model's name.

47 files committed to the repository, 49 TTS mirrors updated on the desktop. Three new writing standards added to the global configuration: `tts-plain-english`, `tts-third-party-voice`, `public-gender-neutral-ai`.

---

## Part 2 — §18 divergence directive: round-2 implementation

Five frontier AI models (Gemini 3.1 Pro, Codex GPT-5.4, CC2 Opus 4.6, ChatGPT GPT-5.4, DeepSeek R1-0528) reviewed the §18 divergence directive in two rounds. Round 1 identified three divergences. Round 2 converged unanimously (5/5) on all three plus a structural channel-assignment question.

### Single recommendation (implemented)

The divergence quality modulator belongs on the internal-novelty channel (η_int), not on the validity channel (R_k). Four tiers: 1.00 (compliant), 0.85 (soft failure), 0.70 (hard failure), 0.60 (severe — near-copy or all-isomorphic). Three new requirements: mandatory contrast statement on every alternative, sibling alt-vs-alt mandatory rejection gate, and near-copy 0.98 threshold for the severe tier.

### Verification

| Metric | Result |
|--------|--------|
| Divergence tests | 75/75 pass |
| Full suite | 935/935 pass |
| SymPy/z3 cross-check | 41/41 pass |
| ruff + mypy | Clean |
| Round-3 5-panel review | 3/5 immediate convergence, 2/5 raised one prose fix (corrected), effective 5/5 |

### Residual debt (documented, not blocking)

- Recidivism detection needs cross-round state from the reference runner
- End-to-end channel-assignment verification at the integration call site
- `divergence_config_from_dict(None)` returns `enabled=False` — intentional

---

## Founder feedback — HIL fatigue (standing correction)

The founder raised a concern about presenting multiple candidate solutions to the human decision-maker instead of one definitive recommendation. This is now a standing correction. The CDSFL system must converge to a single recommendation with visible reasoning and present that. The human's role is to approve or reject, not to choose from a shortlist. Alternatives are generated during the internal exploration phase (correct — Popper's bold conjectures). The output to the human must be one answer, not a buffet. This applies to all model confer dispatch, all reporting, and all future confer scripts.
