# State of Play — 2026-09-29

2026-09-29, 00:15 BST

## What needs a verdict

### Decision 1 — adopt the branch-weighted expectation in the canonical model?

Astra's Q1 is mathematically correct. The shipped recursion in `reference_runner_v3.py` (`compute_rk`, and the explorer verbatim) tracks the **non-detection branch**; Astra's `M(R) = R(1−qσ)` is the **branch-weighted expectation**. Both are sound arithmetic; they answer different questions.

| | at Astra's own worked example (R=1/2, q=4/5, σ=1) |
|---|---|
| shipped `A(R) = σ·B₋ + (1−σ)R` | **1/6** |
| Astra `M(R) = R(1−qσ)` | **1/10** |

1/6 is exactly Astra's *negative branch* value, so the two are not in conflict — one tracks a branch, the other the average. Difference verified identical on SymPy and Wolfram: `A − M = R²qσ(1−q)/(1−qR)`.

**The cost, measured not estimated.** `scripts/` blast-radius probe over the archive: **386 (R,q,σ) triples across 11 log files, 100% would move**, Wilson 95% [99.0146%, 100.0000%], Clopper-Pearson [99.0489%, 100.0000%]; median shift **0.0438**, largest **0.1918**. Always upward — z3 returns unsat for a negative shift and Wolfram returns `True` for `A ≥ M` over the whole open cube.

**So the question is not whether Astra is right.** It is whether to revalue the entire experimental record before Bench Run 2. That is bookkeeping judgement, and it is the founder's.

### Decision 2 — take the branch table from Astra's explorer candidate?

The candidate is **superseded as an implementation**: it examined `9f8a10a` (2026-09-27 23:35) and `explorer/index.html` has moved **+410/−36** since. Reviewing it now reviews a file that no longer exists.

But it has one feature the current page lacks: a **branch table** showing both detection outcomes with their probabilities, resulting risks, and the expected risk across both. Worth taking precisely because it makes Decision 1's distinction visible in one place.

### Decision 3 — the £10 paid panel was authorised and not spent

Reasoning recorded so it can be overruled:

- **Q3** resolved on the day it was asked; `scripts/scorer_separation_is_circular_2026-09-21.py` credits *"THE ASTRA REVIEW OF 2026-09-21"* by name.
- **Q2** correct, but independently reproduced and carried further on 2026-09-28.
- **Q1** is Decision 1 — settled on 3 tools, only a choice remains, and a panel cannot choose what a project measures.
- **Explorer half** would review a rewritten file.

## What Astra got right, and why nothing caught it sooner

Astra's brief of **21 September** states: R=0.99, q=0.3, exact expected gain **0.297**, old-blend gain **≈0.004225**, threshold 0.05. Those are the exact figures derived independently on **28 September**. SymPy confirms its difference expression is identical to the one derived a week later.

Its explorer notes also record that the previous page *"treated a small risk change as an instruction to stop"* — the latched-stop defect a seat found on 2026-09-28 and which was fixed the same evening.

**The finding worth more than either** concerns how external review reaches the project's own record. That brief was in the founder's hands on 21 September; a full working day was then spent re-deriving its central result. Nothing currently requires an external assessment to be read against live code and either adopted, refuted, or explicitly deferred.

**Remaining artefacts.** `adaptive_distributed_compute_design_spec.md` (4,993 words) is a careful scheduling/topology layer, explicitly *"not an empirical claim"* and explicitly barred from Experiment 56. The package verifies intact: **158 files, 153 source mappings**.

## What was done overnight

Four faults the panel found in CC1's own work, each confirmed by execution, each fixed with mutation evidence:

| # | Fault | Evidence |
|---|---|---|
| 1 | Paid-dispatch gate non-functional — wrong path, wrong schema | 7 of 7 authorised rounds refused; 11 tests green only via synthetic fixtures |
| 2 | Classifier evadable by traversal | `classify_write('/tmp/../repo/hooks/evil.py','')` → `transient` |
| 3 | Naming check reported 0.0000% when blind | `git grep` → −1 → every phrase dropped silently |
| 4 | 3 "appears nowhere" claims unsafe, 1 written that day | shell `grep` hides **71.3632%** of matching files, Wilson [70.1245%, 72.5706%] |

**Explorer rebuilt** on the founder's ruling that the seats' disagreement was a false choice. Question selector (prospective default), per-mode threshold, heading, break-even and explanation. Stop rule is now the last pass clearing θ — with `pert=0.4, θ=0.02` the old rule announced pass 10 where the answer is 28. Two unproducible figures removed from the public page.

**W1 closed** on his ruling; the "dead endpoint" claim rescoped in 4 documents — the 97.6744% measured the `npx mcp-remote` bridge's attach, never the host.

**arm4 dispatch recorded** on his express authority, honestly as authorised *in arrears*.

**His September notes** added to `docs/FOUNDERS_NOTES.md` (11 sections, 6,362 words, 733→1004 lines), placed before the April Closing Reflection. **Essay plan** listed as runway step **RL.1**, listed not expanded.

## One honest note on the night's own quality

**8 times** in one day, a check written to guard something turned out unable to fail if that thing broke. Every one was caught by mutation; none by reading. The pattern was identical each time: **a test re-deriving a value the code already owns instead of extracting it** — a probe reimplementing a rule, a test hardcoding two thresholds the page defines, a count of text appearing in both markup and the script that reads it.

8 occurrences in 1 day is the finding, not any single instance.

## Suite state

**Measured on the committed tree at `f60df73`, 2026-09-29 00:44, `pytest bench/tests/ -q --netguard-strict`: 8 failed, 8833 passed, 6 skipped, 1851.65 s.** Recorded by `scripts/suite_record.py`.

**The prediction was wrong and the correction matters.** CC1 stated before this run that 6 failures would remain and all 6 would be pre-existing. There were **8**, and **2 were CC1's own from that same evening** — `scripts/explorer_mode_disagreement_2026-09-28.py` WRITES a probe file and did not answer `--help`, so the flag performed a file write and a 14,440-point sweep. It was caught by `test_help_never_acts_2026-09-11.py`, which is the guard for exactly that defect, in the script written to measure a different blind spot. Measured at the time: 1 of 225 tracked scripts, 0.4444%, Wilson 95% [0.0785%, 2.4741%]. Fixed immediately after the run; 20 tests green.

**The 6 that remain are pre-existing and concern ARCHIVE CONTENT, not code.** Every failing identifier predates 2026-09-28: `exp33_endocrine_20260405`, `commissioning_arm1_20260921`, `commissioning_arm4_20260922`, `panel_round11_2026-09-11`; and the quarantine case compares a script committed **2026-09-01** against an archive last written **2026-08-27**. Stated precisely: that is **dated evidence of pre-existence, not a re-run at an earlier commit**, and the distinction is kept because it is the difference between knowing and assuming.

| file | what it concerns |
|---|---|
| `test_brief_figure_coverage_2026-09-11` | round 11's brief declares a figure its named producer does not print |
| `test_latent_control_audit_2026-09-01` | a quarantine verdict disagreeing with the archive's own dates |
| `test_latent_tagger_evaluation` | prose-source tagging over the commissioning rounds |
| `test_panel_conditions_are_met_2026-09-10` (×3) | P3 tool-call recording and P5 disagreement preservation, over archived replies |

**Named next step, not done tonight.** `main()` in `scripts/explorer_stopping_rule_is_superseded_2026-09-28.py` reads `sys.argv` when called with no argument, so a future test calling `main()` gets `SystemExit 2` from pytest's own flags. `main(argv=[])` is safe. Reproduced and recorded rather than fixed mid-suite.

Written under CDSFL note standard v1.7 (26 August 2026).
