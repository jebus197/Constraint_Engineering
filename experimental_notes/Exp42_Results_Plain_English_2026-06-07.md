# Experiment 42 Results, and the Human Review Question (Plain English)

**2026-06-07 01:34 BST**

## What Experiment 42 was, and what it produced

Experiment 42 was a full review of the composer module — the part of the system that assembles the directive text each model receives. It ran the complete twelve rounds with the falsifier mechanism switched on, the mechanism repaired over the preceding work so that every model now produces findings the runner can independently test.

The headline numbers are good. Across the twelve rounds the runner **confirmed 42 findings** by re-running real tests that import the actual composer code, **refuted one**, and **closed 41** as resolved. There were **no empty responses, no false confirmations, and no crashes**. A spot check confirmed the confirmed findings genuinely import the real module and re-confirm on demand — real, tool-decided results, not fabricated ones. The core principle holds end to end: tools decide, the runner adjudicates, nothing is taken on a model's word.

**The run did not converge.** It used all twelve rounds without reaching the clean-convergence bar, because **15 critical findings could not be tool-confirmed**, and the safety rule that blocks convergence while any unverified critical remains correctly kept it open.

## The question this raises

Are those 15 escalations to the human queue genuine — work that actually needs a human — or could the panel have resolved them itself? If the panel is sending the human work it could have finished, the workload is inflated for the wrong reasons.

## What the audit found

Fifteen independent agents each checked one un-confirmed critical, skeptically, against the **real** composer source.

- **13 of 15 are real defects.** The panel genuinely found subtle bugs (hard directives silently rewritten or pruned; a routine that classifies any block with an upper-case constraint word as hard; a density calculation that can only increase so it over-prunes; the universal directive silently shortened). **Only 1 of 15 was a false alarm.**
- **But all 15 reached the human queue avoidably:**
  - **8 of 15** — the model found the real bug but wrote a **broken test** (a non-existent import, a path that only works from one directory, a truncated line, a test that crashes instead of exiting cleanly). The runner correctly refused a broken test, so the real bug fell through.
  - **7 of 15** — no test written at all.
  - **9 of 15** — **over-rated severity**: real but latent, needing a trigger that never occurs in any of the 13 real directive files.

## Are these legitimate human-review events?

The defined categories were recovered from the project's own rules. The human is needed for: fixes touching **safety or core functionality** (fixes are never auto-applied; the human signs off each); genuine **disagreements** the panel cannot settle; genuinely **uncertain** findings; **contested** findings; **reopened** findings on new evidence. The standing principle: keep the human's workload **minimal**, and present **one clear recommendation**, not a menu.

**Judged against those categories, the 15 are not legitimate escalations.** None is a safety call, a core-functionality decision, or a real panel disagreement. They are real bugs the panel should have resolved itself but couldn't, because its test code was broken or its severity inflated. **This is a new issue to address, not the human queue working as intended.**

## The reassuring part, and the honest caveat

Encouraging in two ways: the panel **finds real bugs** (13 beyond the 42 confirmed), and the inflation is **mechanical and fixable**, not evidence the work needs a person.

Two fixes follow directly: **harden the test harness** so the common mechanical failures (paths, imports, exit behaviour) just work, and add a **test-repair step** that feeds the runner's error back so the model fixes its own broken test (the pattern already built for the weakest model). Plus a **severity-calibration nudge** so latent bugs aren't rated critical. With these, most of the 15 would resolve to confirmed-or-rejected by the panel, and the human queue would shrink to genuine fix sign-offs.

**Honest caveat:** in this run, *every* un-confirmed critical was avoidable. But the audit looked for, and did not find here, a different category — a real defect that genuinely cannot be reduced to a deterministic test (a timing or concurrency bug). For other targets that could appear, and those *would* be legitimate events where minimal human workload isn't achievable. So the minimal-human ideal is reachable on this target, with that exception held open for code where it isn't.

## Where this leaves the project

The runner is robust and the falsifier mechanism is proven on a full run. Experiment 42 surfaced a **quality layer above the mechanism**: how good the test code the models write is, how fairly they rate severity, and whether a real-but-latent defect should block convergence at all. Those are deliberate decisions to make before the next experiments — exactly the review of the experiment series you wanted.

---
*Written under CDSFL note standard v1.2 (14 May 2026). Technical version: `Exp42_Results_2026-06-07.md`. TTS: `~/Desktop/CDSFL_tts/Exp42_Results_and_HIL_Question_2026-06-07.txt`.*
