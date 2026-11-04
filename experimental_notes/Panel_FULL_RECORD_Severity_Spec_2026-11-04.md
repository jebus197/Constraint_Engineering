# Panel record — the severity specification, 2026-11-04

**The 2 seat replies are kept UNFILTERED and byte-exact in `Panel_FULL_RECORD_Severity_Spec_2026-11-04_seat_replies.txt`**, beside this file. The standing rule is that external review output is presented complete and is never summarised in place of the original. They are in plain text rather than here because they are a transcript and not a note of this project's own: the note standard governs what this project writes, and editing a seat's words to satisfy a prose rule would destroy the reply being recorded. Byte-identity to `cc2.json` and `fable.json` is asserted at write time, 11,407 and 8,345 characters.

**This file carries only what is mine: the dispatch facts, what each seat claimed, and what was independently checked before anything was believed.**

## Dispatch

| | |
|---|---|
| brief | `bench/logs/severity_spec_is_uncomputable_2026-11-04/BRIEF.md`, 8,967 characters |
| brief checks | `scripts/panel_brief_validate.py` all 8 required sections; `scripts/note_vagueness_lint.py` 0 findings |
| seats | `cc2` (opus, claude_cli) and `fable` (fable, claude_cli) |
| paid seats | **0**. No spend. |
| topology | blind round, star, stagger 20 s, `blind_of=none`, `joint_of=none` |
| aliveness | both ALIVE on attempt 1 of 3 |
| `cc2` | 11,407 chars, 782.0 s, 4 passes |
| `fable` | 8,345 chars, 696.2 s, 5 passes |
| completion barrier | round wall 782.0 s, total idle 65.8 s (0.0421 of available seat-time), saving against serial 0.4710 |
| seat-proposed edits | 15 files, **untested and NOT applied**, in `seat_proposals.diff` |
| harvested | 3 seat-written files from `cc2`, 2 from `fable`, under `experimental_notes/seat_evidence/severity_spec_is_uncomputable_2026-11-04/` |

**Nothing from either seat is applied to this tree.** `fixes-to-HIL-only` means a seat's proposal reaches the founder before it reaches the runner.

## Both seats returned the same verdict and disagreed about why

`NOT_AS_SPECIFIED` from both: the §7.7 product cannot be formed, because `confidence` is not collected on any archived entry and the HARD/SOFT class has no field.

**Then they diverge, and the divergence is the information.** No convergence was compelled, so it is preserved rather than smoothed.

## What was verified before anything was adopted

A seat's finding is a claim about evidence, not evidence. Each checkable claim was re-derived here first.

| seat claim | how it was checked | outcome |
|---|---|---|
| the §7.7 key-property rate triple-counts 5 findings; `42 = 32 + 2*5`, `37 = 27 + 2*5` | recounted both ways through the producer's own `registry.entries` schema, content-hash deduplicating | **CONFIRMED to the integer** |
| `_sk_admits` does not exist in `bench/reference_runner_v3.py` | `grep -c 'def _sk_admits'` | **CONFIRMED, 0 definitions** |
| 10 of 77 `runner_state.json` files are sandbox copies | `find bench/logs -name runner_state.json -path '*sandbox_harvest*'` | **CONFIRMED: 10 of 77, 67 distinct by content hash** |
| `cc2`'s correction of the denominator to 3,691 | the deduplicated count | **REFUTED: 3,170. `cc2`'s figure is inflated by the same mechanism the brief's was.** |

### The figure defect, reproduced here

```
with the sandbox copies : 37 of 42 = 0.880952, Wilson [0.749996, 0.948062]
deduplicated            : 27 of 32 = 0.843750, Wilson [0.682459, 0.931356]
```

`scripts/severity_was_never_computed_from_the_model_2026-10-12.py` globbed `bench/logs/**/runner_state.json`, which matches 77 files; 10 sit under `sandbox_harvest/`, the directory a PANEL RUN writes to preserve what its seats produced. The 5 REFUTED findings of `commissioning_arm1_panel_20260929T214647Z` each entered the tally 3 times.

**A panel's own evidence-preservation step corrupted the measurement a later panel was convened to examine.** Repaired: the producer deduplicates by content hash and PRINTS the skip, because 84.3750% means nothing to a reader who cannot see that its denominator is 32 and not 42. `docs/MATHEMATICAL_APPENDIX.md` §7.10 is corrected, and the earlier `35 of 40 / 87.5000%` recorded there carries the same defect and is superseded rather than stale.

## Where the seats contradict each other

### 1. Whether dropping `confidence` is safe — opposite signs

| seat | substitution | partition moves | gate flips | direction |
|---|---|---|---|---|
| `cc2` | `asserted · V` | 29 of 78 runs | **11 of 78**, 14.1026%, Wilson [8.0610%, 23.5140%] | **every one False→True**, manufacturing convergence |
| `fable` | `compute_sev_f(class, confidence, verdict)` | 588 entries | **12 of 46** verdict-bearing runs | **every one True→False**, preventing convergence |

They substituted **different definitions**, which explains the sign and is itself the result: *"drop `confidence`"* is not 1 option but 2, with opposite failure modes. The brief listed that direction first and neutrally; `cc2` calls it *the one that breaks the harness* and its own most consequential result.

`cc2` derives why the sign is what it is: severity lies in [0,1] and the critical cut is 0.7, so `sev/2 >= 0.7` requires `sev >= 1.4`. SymPy returns `7/5`; Wolfram `Reduce` returns `False`. `V(None) = 0.5` therefore makes **every** unresolved finding sub-critical — precisely the population the A4 fail-safe exists to block on.

### 2. Whether the directive and the appendix actually conflict — the hinge of B87

`cc2` reads `cdsfl_operational.md:773` as forbidding confidence only as a **rebuttal to a tool verdict**: it sits under *Action precedence, item 1, REFUTED by tool*, and §7.7 **implements** that by setting confidence's weight to 0 exactly where a tool refuted. On that reading the 2 documents agree and B87's central claim dissolves.

`fable` holds the conflict is real, citing **§15 `d_tool`** — quantities come from tool execution, *not from self-assessed confidence* — as an independent prohibition.

**They cite different clauses.** Whether §15's `d_tool` independently forbids `confidence` as a severity input is a factual question about 1 document and it is the hinge of entry B87. It is recorded for the founder's ruling rather than decided here.

## Findings neither B87 nor the brief contained

- **A second partition reader.** `_corroborated_novelty_series` at `bench/reference_runner_v3.py:10912`, with an identical raw-severity read. `cc2` found it only because its patch refused to apply on a unique match.
- **`compute_sev_f` and `stamp_sev_f` already exist**, wired into the round loop at line 20523, tested, default-off, with reader-side support for both missing factors. So *add the HARD/SOFT field* needs a **writer**, not a build from scratch.
- **`effective_severity` and `RunnerConfig.severity_spec_enabled`** were built 2026-10-15, so *§7.7 gates nothing* overstates: the promotion reaches **1 of the 2** severity consumers that decide convergence.
- **The key property may not be unconditionally desirable at the gate that blocks convergence.** Exp 42 measured 2 of 3 REFUTED criticals as falsely REFUTED, so full §7.7 compliance there would have released real defects. `fable` places it at the scoring layer only.
- **`cc2` declined to compose, citing the founder's rule.** Its restricted annihilator-only form (`V=0` implies 0, other values untouched) flips **0 of 78**, Wilson [0.0000%, 4.6938%], and dominates the full product on a named property: manufactured convergences, **0 against 11**. Since the single fix performs strictly better alone, it added no second guard.

## What the seats say would refute them

`cc2` names its own weakest joint: its fix treats `REFUTED` as permanent annihilation, and it did **not** measure REFUTED-to-CONFIRMED transitions on a single canonical identifier. If that count exceeds 0, the fix must read the latest verdict rather than any verdict. It also states that all 78 replays hold `unresolved_critical = 0` and `contested = 0`, so a live run with either above 0 could flip where the replay does not.

`fable` reports no residual debt on its own claims and terminated converged at pass 5.

## What this changes in the record

1. `docs/MATHEMATICAL_APPENDIX.md` §7.10 — figure corrected to 27 of 32, 84.3750%, with the provenance of the error.
2. `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` — deduplicates by content hash and reports the skip.
3. Entry B87's central claim is **contested by `cc2` and defended by `fable`**, and needs the founder's reading of §15 `d_tool`.
4. The brief's own artefact list named a function that does not exist, which is a defect in my brief and is recorded as such.

---

Written under CDSFL note standard v1.9 (1 November 2026).
