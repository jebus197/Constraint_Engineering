# PANEL BRIEF TEMPLATE — the required form of every CDSFL panel brief

**Locked 2026-09-09 on the founder's ruling, verbatim:** *"In all cases and with all fixes always check them with Fable and CC2 in full CDSFL panel review format (so not just some simple open ended prompt), they must use whatever aspects of the harness are currently working, including our mathematical model and all relevant mechanics in the formation of their answers/fixes, as should you. this format should then be saved as the standard for all future 6 full paid model reviews also."*

**This is the standard for every panel review, free-seat and full paid 6-model alike.** It is validated by `scripts/panel_brief_validate.py`, which `bench/confer_maths_panel_2026-09-05.py` runs before dispatching. A brief that fails validation is refused rather than sent, because a paid dispatch on a defective brief costs money and returns nothing usable.

**Why a template at all, measured.** Across the 49 briefs archived before this date: **0 required a seat to use the mathematical model as an instrument, 8 required a fix, and 2 required the fix to be tested.** They were hand-written markdown read straight off disk with no template, no schema, no validation and no test. The founder's diagnosis — that they were closer to open-ended prompts than to a format — is confirmed by that measurement.

**What this template does NOT contain.** The formal schema, the no-compelled-convergence rule, the additive standard and the one-shot notice all reach every seat through the dispatcher's SYSTEM string by construction, and are tested by `bench/tests/test_panel_runs_under_the_schema_2026-09-07.py`. Repeating them here would be duplication with no comparator. This template governs the USER half only, which is the half that did not exist.

---

## REQUIRED SECTION 1 — The question

State the single question the panel is being asked. One sentence, then as much context as it genuinely needs. Name the artefact under review by path.

## REQUIRED SECTION 2 — Use the harness

State explicitly that the seat must form its answer USING whatever parts of the machinery currently work, not by describing them. Name the specific instruments that bear on this question. At least one of `gamma`, `rho`, `S_k`, `sigma`, `nu`, the two-sided gate, or the severity model must be named, with what it is expected to say about the question.

A seat that returns prose about a fix without having run anything has not answered.

## REQUIRED SECTION 3 — Produce a fix, and test it

State that a finding without a fix is incomplete, and a fix without a runnable falsifier that has been EXECUTED is a hypothesis. Require the seat to report the command it ran and the output it saw.

## REQUIRED SECTION 4 — What would refute you

Require each seat to state, before it concludes, what evidence would overturn its own answer. A verdict with no stated refutation condition is an opinion.

## REQUIRED SECTION 5 — Output shape

State exactly what the seat must return, field by field, so that replies can be compared without a parser guessing. At minimum: verdict, reasoning, the falsifier and its executed result, the strongest disagreement with the brief's own framing.

## REQUIRED SECTION 6 — Termination

State when to stop. Diminishing returns is the project's own criterion: stop when a further pass produces no new above-threshold findings, and say how many passes were run.

---

Written under CDSFL note standard v1.7 (26 August 2026).
