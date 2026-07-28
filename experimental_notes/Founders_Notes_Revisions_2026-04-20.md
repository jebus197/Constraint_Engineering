# Founders Notes Revisions — 20 April 2026

## Scope

On 20 April 2026 a further set of revisions was made to `docs/FOUNDERS_NOTES.md`, the long-form reflective record in which design decisions, their motivations, and the reasoning that led to them are preserved in the founder's own voice. The 20 April revisions did not add new material at the end of the document. They corrected four existing entries that had drifted in small but material ways from what the canonical record shows actually happened during April 2026, and they removed two entries that belonged on other project surfaces.

---

## Revision 1 — Cell-Type Architecture Timing

The entry previously titled *Cell Type Architecture*, dated 9 April 2026, was renamed and rewritten.

The canonical project record shows that the named immune cell types — Dendritic, Cytotoxic T, Natural Killer, Regulatory T, Helper T, B-Cell, Macrophage, and Ouroboros — first appeared in the project record between 2 and 4 April 2026. What happened on 9 April 2026 was different: it was the point at which the composition law

    S_k = A · E
    A   = Π g_j          (product of gate values)
    E   = Σ w_m · e_m    (weighted evidence aggregate)

was made mathematically explicit. The cells already existed; the rule for combining their outputs was what became explicit on 9 April.

**New title:** *The Composition Law Becomes Explicit (9 April 2026)*.

**Rationale.** The earlier framing conflated the introduction of a vocabulary with the introduction of a formalism. Those are two separate design moments, and the project's record keeps them separate elsewhere.

---

## Revision 2 — New Entry: Mathematics as Primary Reasoning

A new dated entry, *The Equation Becomes the Constraint Box (9 April 2026)*, was inserted between *Mathematical Model Under Audit (7–8 April)* and *The Composition Law Becomes Explicit (9 April)*.

**Motivation.** A genuine change of character occurred on 9 April that was not captured in any existing entry. Up to that point the mathematical framework was a support layer under a predominantly verbal reasoning process. From 9 April onwards it became the primary reasoning surface. Models participating in the framework were required to compute their own updates of the recursive state equation `R_k(i)`, to produce `q = η · d · p` at each step, and to use the sign and magnitude of `ΔR_k` as their stopping heuristic. The equation stopped being a notation for results already obtained; it became the working medium in which reasoning was carried out.

That shift deserves its own dated entry, and the revision now places one.

---

## Revision 3 — Ouroboros Paragraph Deepened

The paragraph on the Ouroboros cell was expanded rather than rewritten.

**Earlier text:** stated the name had been chosen without exploring the reason.

**Revised text:** sets out the specific failure mode the cell is built to catch — the production of findings that are strongly argued by one of the panel models but that, on external check, reproduce work already in the published literature. The serpent consuming its own tail is the visual analogue of that failure mode: a self-contained circle that appears to make progress because it moves, but is in fact consuming its own starting point. The Ouroboros cell is the framework's structural defence against that shape of error.

**Voice profile preserved:** biology-metaphor register, em-dashes, short verdict closers, British spelling. No new claims about cell performance.

---

## Revision 4 — Stage 6 Entry Fully Rewritten

The entry dated 14 April 2026 covering the Stage 6 literature-calibrated extension was fully rewritten.

**New title:** *On Novelty as a Moving Target (14 April 2026)*.

**What the earlier version captured.** The Hossenfelder concern. Sabine Hossenfelder's February 2026 observation that AI systems were producing confident solutions to Erdős problems already solved in the published literature had been the proximate trigger for the Stage 6 extension. The framework needed a way to check novelty against the external record, not only against its own internal record. Stage 6 added the second novelty dimension `c_ext` to give it one.

**What the earlier version missed.** The opposite concern, equally real and which must be held alongside the first. The temptation, once the rediscovery failure mode is named, is to constrain the models so tightly against the external record that they stop doing the thing language models are actually useful for — synthesising across a wide spread of published sources and producing framings that no single source had alone. Over-constrained novelty checking would push the framework back toward a retrieval-plus-rephrasing regime. That would be a regression against the project's own design intent.

**What the revised entry does.** Holds both concerns together. Describes the Hossenfelder failure mode, describes the synthesis-preservation failure mode, and describes the design decision — the two-dimensional novelty score that measures both internal re-injection quality and external originality, and that treats synthesis as a distinct, valued category rather than as a near-duplicate of retrieval.

**Rationale.** Novelty in this framework is not a single axis. It is a balance between two pulls, and the Founders Notes entry now says so.

---

## Removals

Two entries were removed from the document.

1. *README, the `rg` Command, and the Public Surface (18–19 April 2026)* — described ephemeral session work around the v3 draft of the README and the introduction of the `rg` metacognitive command. That work belongs in `resources/RECOVERY.md` and persistent memory. Founders Notes should contain design reflection, not session logs.

2. *A short meta entry summarising the 19 April sweep itself* — removed for the same reason. Founders Notes entries describe design decisions, not sweeps that record them.

---

## What Was Not Changed

- The Closing Reflection — including the floppy-disk / 386 analogy about conditions under which a methodology has to be written down explicitly in order to be passed on — was retained untouched.
- The voice profile of the document (em-dashes, British spelling, short verdict closers, biology-metaphor register) was retained.
- The chronological ordering of entries from the start of the project through to the present was retained.

---

## Effect

The Founders Notes are now an accurate reflective record of what was decided during April 2026, and why, consistent with the mathematical appendix, the white paper, and the experimental record.

---

*Companion TTS file: `~/Desktop/CDSFL_tts/Founders_Notes_Revisions_2026-04-20.txt`. Context: 20 April 2026 five-batch documentation consolidation sweep — Batch A. Related mirrors: `README_Promotion_2026-04-20.md` (Batch B), `Regulatory_Compliance_Framework_2026-04-20.md` (Batch D).*
