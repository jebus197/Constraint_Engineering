# Risk dynamics explorer — technical note (Read more target)

**Status:** Outline for the orchestrator / docs author. Full equations live in the Mathematical Appendix (Stage 5); this note should introduce them in researcher-facing order, then link or embed the formal recursion.

## Purpose of this page

The in-app meta-tooltip stays short and multi-domain. This page is for readers who want:

1. Precise meaning of detection, resolution, and re-injection
2. Parameter definitions tied to the Stage-5 model
3. What Retrospective vs Predictive compute from
4. Limits and non-claims
5. Pointers into `docs/MATHEMATICAL_APPENDIX.md` (and the live `explorer/` implementation)

## Suggested sections (implement in docs)

1. **The enquiry loop** — test → change → re-test as a general STEM pattern  
2. **Three phases** — detection; resolution (fix efficacy); re-injection (side-effects of change)  
3. **What R represents** — remaining risk that something material is still wrong (conservative bound language as in the appendix, not over-claim as calibrated probability unless the project later supports that)  
4. **Parameters** — π, p, η, σ, ν, θ, optional perturbation; each with plain sentence + formal role  
5. **Regimes** — healthy, ideal, leaky, futile (match explorer presets)  
6. **Retrospective Mode** — bound experiment, recorded passes, select different experiment  
7. **Predictive Mode** — parameters only; no last-run coupling  
8. **What does not follow** — does not clear claims; does not replace domain evidence; does not forecast live outcomes  
9. **Formal development** — link to Mathematical Appendix Stage 5 / R_k(i) with the project’s current verified statements  

## Orchestrator rule

Do not duplicate conflicting maths between this note and the appendix. Appendix wins on formal content; this note wins on teaching order and familiar-ground framing.
