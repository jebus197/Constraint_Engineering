# README Promotion — 20 April 2026

## What This Document Covers

On 20 April 2026 the v3 draft of the public README for the Constraint-Driven Synthesis and Falsification (CDSFL) project was promoted to become the canonical `README.md` at the repository root. The v2 drafts, retained at the repository root for side-by-side comparison during the review period, were deleted as part of the promotion. This note documents the changes applied to the v3 draft before promotion, the state of the footer after promotion, the new material added, and what was retained unchanged.

---

## Starting Point

The v3 draft had been built on 18 April 2026 on the foundation of the founder's April 2026 blog post, not on the v2 nine-section plan shape. On 19 April 2026 it had been taken through a thirteen-point correction sweep covering: Exp 39 / Exp 40 runner references removed from the public surface, first-mention explanation of the Ouroboros cell, expanded five-model panel framing in the Abstract, explicit tool-deterministic constraint box, introduction of `R_k(i)` as the models' own reasoning methodology from Exp 37 onwards, and plain inline definitions of several terms.

What the v3 draft did not yet have, at the point where this session picked it up, was the additional 20 April material the sweep was building toward, plus the first-person oversights that had slipped through the 19 April correction round.

---

## First-Person Corrections

The README is a public document — third-person or descriptive voice throughout. Eight remaining first-person instances were corrected at lines 13, 15, 17, 19, 53, 75, 94, and 96 of the draft. One additional instance on line 13 (`which I call the P-Pass` → `called the P-Pass`) was caught during the correction round and fixed in the same pass. The document now reads in a consistent descriptive voice.

**Retained first-person (intentional):** lines 11 and 35 preserve the idiomatic "for me" in contexts where the founder is making a personal statement about the origin of the project. The directive for this session was to fix first-person oversights, not to strip the document of personal anchoring where that anchoring is load-bearing.

---

## Synthesis-Preservation Paragraph Added to §6.6

Immediately after the paragraph explaining the Hossenfelder concern in §6.6, a new paragraph was inserted stating the opposite concern:

> The temptation, once the rediscovery failure mode is named, is to constrain the models so tightly against the external record that they stop doing the thing language models are actually useful for — synthesising across a wide spread of sources and producing framings that no single source had alone.

The added text makes clear that the framework measures synthesis separately and treats it as a valued category rather than as a near-duplicate of retrieval.

**Rationale.** This closes a genuine gap in the v3 draft, which had named only one of the two concerns that together motivate the Stage 6 design.

---

## Expert-Encoding Essence-Capture Framing Strengthened in §8

The earlier text stated only that encodings capture field-specific method. The strengthened text now names the ten-section canonical template directly, treats the final section as load-bearing, and enumerates the nine essence-capture categories:

1. failure-mode priors
2. diagnostic heuristics
3. regime boundaries
4. tool-chain realism
5. standard gotchas
6. disagreement maps
7. evidence grading
8. tacit sequencing
9. escalation triggers

The intent: a qualified domain expert reading an encoding authored by a peer recognises it as an honest portrait of how work is actually done in that field, not as a compliance skeleton. The framing was converged on through confer review with external models in April 2026 — that fact is now noted in the text.

---

## Regulatory-Compliance Paragraph Added to §8

A new short paragraph at the end of §8 notes that several of the primitives named in the section happen to line up with the technical controls commonly required by modern AI and data-governance frameworks:

- EU AI Act
- GDPR
- NIST AI RMF
- ISO/IEC 42001

The paragraph is careful to note that:

- The alignment is genuine but partial.
- The framework provides technical primitives commonly required by these regimes; it does not by itself constitute a conformity package.
- Full compliance depends on supplementary controls that sit around the framework, not inside it.
- A detailed mapping and honest gap statement live in `docs/COMPLIANCE_FRAMEWORK.md` (created in Batch D of this session).
- The document is not legal advice.

---

## Further Reading Updated

One new entry added to Further Reading:

- [docs/COMPLIANCE_FRAMEWORK.md](docs/COMPLIANCE_FRAMEWORK.md) — mapping of CDSFL primitives to EU AI Act, GDPR, NIST AI RMF, and ISO/IEC 42001, with honest gap statements and supplementary-artefact templates.

---

## Footer Updated

**Before:**

> *CDSFL. 19 April 2026. Fundamentalist open source under the MIT License. A running system, a maintained test suite, and a mathematical appendix under iterative extension. Contributions, criticism, and competing schemas are welcomed under the same falsification discipline the framework applies to itself.*

**After:**

> *CDSFL. 20 April 2026. Fundamentalist open source under the MIT License. Forty experiments on the record; 1250 bench tests passing; a mathematical appendix under iterative extension at 1991 lines. Contributions, criticism, and competing schemas are welcomed under the same falsification discipline the framework applies to itself.*

The concrete scale of the project at this point in time is now visible from the footer.

---

## Promotion

The corrected and extended v3 draft was copied over `README.md` at the repository root. The v2 drafts at the repository root — `.docx`, `.html`, `.md` files dated 18 April 2026 — were deleted. The v3 draft file itself was also deleted, since it had been promoted to `README.md`. The repository root now contains a single `README.md` file.

**Files deleted:**

- `README_v2_draft_2026-04-18.docx`
- `README_v2_draft_2026-04-18.html`
- `README_v2_draft_2026-04-18.md`
- `README_v3_draft_2026-04-18.md`

---

## What Was Not Changed

- The thirteen corrections applied on 19 April 2026 were preserved.
- The voice of the document, the section structure, the mathematical notation, the diagrams, and the file pointers remain as they were.
- The Further Reading section's existing entries (other than the new COMPLIANCE_FRAMEWORK entry) were preserved unchanged.

---

## Effect

A sequence that started on 18 April 2026 with the first v3 draft, continued on 19 April 2026 with the thirteen-point correction sweep, closed on 20 April 2026 with eight first-person corrections, two content additions (synthesis preservation and regulatory-compliance framing), a strengthened essence-capture framing in §8, an updated Further Reading entry, and a bumped footer. v2 drafts retired. Repository root clean. The document a new reader will pick up first now reflects the state of the project as of 20 April 2026.

---

*Companion TTS file: `~/Desktop/CDSFL_tts/README_Promotion_2026-04-20.txt`. Context: 20 April 2026 five-batch documentation consolidation sweep — Batch B. Related mirrors: `Founders_Notes_Revisions_2026-04-20.md` (Batch A), `Regulatory_Compliance_Framework_2026-04-20.md` (Batch D).*
