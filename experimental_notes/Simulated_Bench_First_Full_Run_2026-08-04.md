# The pipeline runs end to end, on a panel it did not script

2026-08-04 03:53 BST

> **CORRECTION, 2026-08-05 14:05 BST — THE PANEL LABELS WERE MISLEADING.**
> The five agents in this run were **Claude subagents via the Agent tool**. They
> were originally labelled `Gemini`, `Codex`, `ChatGPT`, `CC2` and `DeepSeek` to
> mirror the real panel's composition, and the results were then reported using
> those names — "Gemini built the negative control", "Gemini's AL-02 finding".
> That reads as though the named frontier models participated. **They did not. No
> paid dispatch occurred in this run at all**, which was the entire point of it.
>
> The confusion is worse because the record contains a REAL panel review from the
> same 24 hours (`bench/logs/pr_semantic_distinctness_2026-08-04/`, five models via
> `dispatch_to_model`, ~£3) using the same five names. A reader could not tell them
> apart.
>
> Relabelled throughout to `SIM-A` … `SIM-E`. The findings, the falsifiers and every
> measured result are unchanged — only the attribution was wrong. Commit `154d8fc`
> carries the original wording and cannot be rewritten; this note supersedes it.


## What was untested until now

A week of repairs — the routing ladder's prompt, tri-state verification, S_k
NO_SCORE on prose, the panel briefing, the launch preflight, rejection reasons,
sweep-on-halt, ruling 3's computed evidence, the ouroboros query and reader, and a
shadow novelty rule. Two were proven end to end. The rest were unit-tested only,
and unit-green-while-the-live-path-disagrees is this project's signature failure.

An earlier harness was described as a simulated bench and was not one: it
registered findings and compared novelty rules, never calling the falsifier gate,
routing, verification, S_k, the rejection lines or either convergence gate. The
founder caught the gap.

## The run

Target `bench/tests/fixtures/stem/docs/ALG-02-REF-01.md` — 7 claims, ONE planted
defect (AL-03), two executable fenced listings, the document shape that halted the
zero-plant control. Ground truth exact, so the run scores itself.

Panel: five agents, blind. Forbidden from opening the fixture module or any answer
key. Each required to WRITE and RUN a falsifier before reporting it. No paid model
dispatch.

**12 of 12 stages passed.**

| stage | result |
|---|---|
| target kind | prose, detected from the file |
| A9 preflight | passes; REFUSES the same config with routing off |
| S_k | `NO_SCORE` — abstains rather than inventing a number |
| verification | `NO_APPLICABLE_CHECKS`, veto recorded, never PASS |
| panel briefing | prose branch: names the falsifier, promises no linters |
| falsifier gate | **7 CONFIRMED, 1 → HIL** |
| A10 | reasons rendered into the ROUND PROMPT, not just the entry |
| novelty | location `[1,0]`, hierarchical `[1,0]`, 0 blind-spot candidates |
| two-sided gate | evaluates and converges on a quiet series |
| **ground truth** | **planted defect DETECTED, 5 demonstrations, 0 false positives confirmed** |
| residue | 1 unsettled (ERROR), 1 escalated |
| honesty check | **1 finding the agent said RAN that the runner could not confirm** |

## What the panel produced

8 findings from 5 agents; 5 critical. **All five agents
independently found AL-03**, each with its own falsifier, and the runner
re-executed every one. Five separate demonstrations of one real defect.

The novelty series collapsing five findings to `[1, 0]` is the Exp 42 failure mode
— models relabelling one defect every round — handled correctly by both rules.
Zero blind-spot candidates, correctly: all five genuinely ARE the same defect.

## Two things the panel did that were not asked for

**One agent built the negative control for the false-CONFIRMED hole.** SIM-A ran
its falsifier against a corrected copy of the document (`seen = set()` rather than
a list) and recorded that it printed "not falsified" and exited 0. That is the
discrimination test for the open hole where a valid-but-wrong falsifier closes a
finding against a TRUE claim — performed spontaneously. It suggests the fix is
cheaper than feared: ASK THE PANEL for the control rather than building machinery
to synthesise a corrected copy.

**One agent corrected the assistant.** SIM-A's AL-02 finding identifies that
Python's `in` applies an identity check before equality — the exact point CC1 got
wrong earlier the same night, when a `nan` demonstration contradicted its own
label. Rated 0.30, correctly sub-critical.

## The honesty check, and why it matters

All eight agents claimed their falsifier RAN. The runner confirmed seven. C0003
returned ERROR — an asserted demonstration that is not one.

That gap is precisely what CONFIRM-only exists to police, and it appeared on the
first real pass. It is the standing argument against ever accepting "the model
says it verified this".

## Boundary

This is NOT an experiment and none of it belongs in the paper. A simulated panel's
findings differ in character from five frontier models under the full directive.
It tests MECHANICS: that each stage receives what it expects, acts correctly, and
hands on. That was the untested thing, and it now runs.

Raw evidence: `adversarial_records/simulated_panel_alg02_findings_2026-08-04.json`
and `adversarial_records/simulated_bench_stages_2026-08-04.json`.

Written under CDSFL note standard v1.2 (14 May 2026).
