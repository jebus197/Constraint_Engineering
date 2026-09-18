# The list for after the mathematical model revision

2026-09-17, 22:22 BST, Europe/London. Opened on the founder's instruction: "we will need to build another action list for things to do after the mathematical model revisions."

## What this list is for

Every item here is held for 1 reason: it depends on how the revised mathematical model settles, so doing it now would build against a moving target. Nothing here blocks the revision itself. Items are added as they are ruled; each names who ruled it and what the dependency is.

## The list

1. [ ] **R10, R11 and A19 go to the panel, or close, once the revision is reviewed.** Founder, 2026-09-17: "We will do exactly that after these issues are addressed." R11 answers ruling 4.3 with `gamma_input`; R10 is the reading behind the references selection; A19 is the per-fragment admissibility design point.

2. [ ] **The drift detector is enabled properly, or retired. ON THE RUNWAY TOO, at Stage 4 row 4.5, on the founder's ruling of 2026-09-18 01:30 BST:** *"The drift detector should be put on the action list (and on the runway) for after the maths model review."* Founder, 2026-09-17: "if what it's supposed to do is useful and it isn't doing it, we should probably enable it, once the work on the revised mathematical model is complete." What it is supposed to do: memory holds, per flaw class, how often findings of that class proved real, and the detector accumulates how far this run's confirmation rate drifts from that prediction, warning when the total gets large. What stops it: `ImmuneMemory.save` writes no CUSUM state, so every run starts from 0 and gets exactly 1 update, while z3 and Wolfram's `Reduce` both find 3 same-direction updates are needed to cross 2.0. Enabling it means persisting that state between runs, which changes how memory behaves, and its threshold of 2.0 has never met live data. The report-only call stays meanwhile: it decides nothing and cannot fire.

3. [ ] **Experiment 56's arm-declaration exposure.** Founder, 2026-09-17: "Agreed. But we will need to build another action list for things to do after the mathematical model revisions. This should be one of them." It is held as an expected failure because its fix edits a frozen pre-registration.

4. [ ] **V9 — OPENED 2026-09-18 01:30 BST on the founder's approval, "V9: Approved."** For each DONE entry, undo its fix in a scratch tree, run the test its marker names, and require that test to fail; a test that stays green against its own reverted fix is decorative evidence. Explained in chat on 2026-09-17; approved 2026-09-18 and now entry V9 of the master task list, state OPEN, status PROPOSED. It is scheduled here rather than now because the entries it audits are the ones the revision may reopen.

5. [ ] **The panel's architecture count, once the seat question is settled.** The Codex and ChatGPT seats are byte-identical `ModelConfig`s apart from the label, so the panel has 4 architectures and reports 5. The founder's goal is epistemic diversity; the options are a genuinely distinct Codex route (`codex_exec`), separate OpenRouter models, or the approved-but-unbuilt injection of a published Codex system prompt into 1 seat. Measurement of what OpenRouter currently offers precedes his ruling.

Written under CDSFL note standard v1.7 (26 August 2026).
