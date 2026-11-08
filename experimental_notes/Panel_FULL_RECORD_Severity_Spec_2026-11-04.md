# Panel FULL RECORD — the severity specification, round 1 (blind), 2026-11-04

Record written 2026-11-04T01:41:44+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

# Panel record — the severity specification, 2026-11-04

**The 2 seat replies are kept UNFILTERED and byte-exact inside this file**, in a verbatim region built by `scripts/make_panel_full_record_2026-09-11.py`. The standing rule is that external review output is presented complete and is never summarised in place of the original. They are in plain text rather than here because they are a transcript and not a note of this project's own: the note standard governs what this project writes, and editing a seat's words to satisfy a prose rule would destroy the reply being recorded. Byte-identity to `cc2.json` and `fable.json` is asserted at write time, 11,407 and 8,345 characters.

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

- **A second partition reader.** `_corroborated_novelty_series` at `bench/reference_runner_v3.py:10963`, with an identical raw-severity read. `cc2` found it only because its patch refused to apply on a unique match.
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

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — The severity specification asks for two factors this harness refuses to collect

## REQUIRED SECTION 1 — The question

**Can section 7.7's `Sev(f)` be computed in this harness as specified, and if not, what is the simplest sufficient replacement that preserves its one stated KEY PROPERTY?**

`docs/MATHEMATICAL_APPENDIX.md` section 7.7 specifies

> **Sev(f) = W(class) · confidence · V(verification)**

with the KEY PROPERTY that a disproved finding scores 0 whatever the model claimed. Three factors. Exactly one of them is collected.

**`V(verification)` IS collected.** It is the harness's own falsifier verdict, produced by `bench/falsifier_verify.py` and recorded per finding.

**The other 2 are absent, and for OPPOSITE reasons — that asymmetry is the whole question.**

1. **`confidence` is REFUSED BY POLICY, not missing by oversight.** `bench/directives/universal/cdsfl_operational_*` rules a model's self-reported confidence inadmissible as evidence. So the specification asks for a quantity the operational directive forbids. This is not a gap to be filled by collecting harder; it is a contradiction between 2 documents the harness treats as binding.
2. **The HARD/SOFT class is instructed on every finding and has nowhere to be recorded.** No field on a registry entry holds it. Measured: **0 of 3,298 archived entries carry either `confidence` or a HARD/SOFT class.**

**What runs today instead.** `bench/reference_runner_v3.py` reads a model-asserted severity float. `FindingRegistry.severity_spec_shadow` applies the section 7.7 product advisory-only and **gates nothing**. The KEY PROPERTY is violated on **37 of 42 disproved findings — 88.0952%, Wilson 95% [74.9996%, 94.8062%], Clopper-Pearson [74.3683%, 96.0194%]** (re-measured 2026-10-29).

<!-- figure: key property violation rate | scripts/severity_was_never_computed_from_the_model_2026-10-12.py | 88.0952 -->
<!-- figure: wilson lower | scripts/severity_was_never_computed_from_the_model_2026-10-12.py | 74.9996 -->
<!-- figure: wilson upper | scripts/severity_was_never_computed_from_the_model_2026-10-12.py | 94.8062 -->
<!-- figure: clopper lower | scripts/severity_was_never_computed_from_the_model_2026-10-12.py | 74.3683 -->
<!-- figure: clopper upper | scripts/severity_was_never_computed_from_the_model_2026-10-12.py | 96.0194 -->

**Artefacts under review, by path:**
- `docs/MATHEMATICAL_APPENDIX.md` section 7.7 and the Reduction Properties table
- `bench/reference_runner_v3.py` — the severity read and `_sk_admits`
- `bench/falsifier_verify.py` — the `V` factor's only producer
- `bench/directives/universal/` — the directive that refuses self-reported confidence
- `scripts/severity_was_never_computed_from_the_model_2026-10-12.py`
- `scripts/the_severity_cut_collapses_the_formula_2026-10-13.py`
- `/Users/georgejackson/Developer_Projects/Responses/Orchestrator_Note_Solution_Severity_Residual_Risk_2026-11-02.md`

**WHAT IS ALREADY SETTLED AND IS NOT THE QUESTION.** Whether severity and residual risk are the same quantity. They are not, and 3 independent sources agree: the appendix models residual risk as the recursive `R_k` and severity as the section 7.7 product, with no shared term; an outside model's note of 2026-11-02 states that severity labels a *finding* while residual risk labels the *state of the investigation*; and a scan of 5,026 files in this repository finds the 2 terms equated in code in exactly **1** place, a comment at `scripts/can_the_carry_latch_the_gate_at_one_2026-10-31.py:6`. **Do not spend a pass re-deriving that.** It is given as context so no seat mistakes the conflation for the open problem.

**A DISCLOSURE ABOUT THE EVIDENCE IN THIS BRIEF.** The 88.0952% figure, the 0-of-3,298 figure and the 1-of-5,026 figure were all produced by the same author as this brief. A seat that can show any of them is wrong, mis-scoped, or answering a different question has made a larger contribution than a seat that accepts them.

## REQUIRED SECTION 2 — Use the harness

Form your answer by RUNNING the named instruments below, not by describing them. Named instruments that bear on this question, each with what it is expected to say:

- **The severity model itself.** Call `FindingRegistry.severity_spec_shadow` on real archived entries under `bench/logs/`. Expected: it returns a value and nothing consumes it. Confirm or refute by finding its consumers in the gating path.
- **The two-sided convergence gate.** `_check_gamma_alt_convergence` in `bench/reference_runner_v3.py`. Expected: it reads `gamma_critical`, which depends on which findings are CRITICAL, which depends on the severity cut. Establish by execution whether a change to the severity definition changes a convergence verdict, or whether the cut collapses the formula to a threshold test (the second producer above claims it does).
- **`gamma` and `gamma_critical`.** Recompute both over at least 1 archived run and report whether the CRITICAL partition is stable under a severity definition that drops `confidence`.
- **`S_k` / `sigma`.** The scorer's sigma slot is the appendix's own home for a severity-like quantity. State whether `sk` can carry `Sev` or whether it measures something else.
- **`nu`.** Report whether novelty and severity are separable on the archive, or whether a severity change moves the novelty series too.

A seat that returns prose without having run anything has not answered. Report the archive paths you read and how many entries you read.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. A fix without a runnable falsifier that has been **EXECUTED** is a hypothesis.

Write your fix **INTO the sandbox repository tree at its real path, as a file.** A fix described in prose is not delivered. A fix written to scratch space is destroyed when the sandbox is torn down. Report the exact command you ran and the output you saw.

Candidate directions are listed so you can refute them, not so you can adopt any of them unexamined:
- drop `confidence` and renormalise the remaining 2 factors;
- replace `confidence` with a harness-measured proxy, and say which, and show it is not the model's own word wearing a new name;
- add the HARD/SOFT field and collect it, which is additive but needs a writer and a reader;
- declare section 7.7 advisory and gate on something else;
- amend the operational directive so `confidence` becomes admissible under stated conditions.

**COMPOSABILITY, AS THE FOUNDER DEFINES IT.** Where more than one repair is in play, compose ONLY on a DEMONSTRATED advantage over each fix alone, where the demonstration is a **MEASUREMENT** and not a judgement, and prefer the single fix wherever it performs as well. If you recommend a composed pair, name the property it dominates on and give the number. 2 repairs that merely sit side by side without interfering have not met this standard, and a reply resting on that reading has not answered the question.

**THE ADDITIVE STANDARD BINDS BOTH WAYS.** Do not remove a capability without a committed measurement showing the replacement dominates on a named property. Equally, do not add a flag, field or gate that no caller reaches and no test executes — in this repository, 11 confirmed defects were additions that did nothing, against 0 removals of something needed.

## REQUIRED SECTION 4 — What would refute you

Before you conclude, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

At minimum, state: what measurement over this archive would show your replacement severity is WORSE than the model-asserted float in use today, and on what named property.

## REQUIRED SECTION 5 — Output shape

Return exactly these fields, so replies can be compared without a parser guessing:

- `verdict` — can section 7.7 be computed as specified: YES / NO / NOT_AS_SPECIFIED, one line.
- `reasoning` — the derivation, with the instrument outputs it rests on.
- `fix` — the path(s) you wrote in the sandbox tree, and what each changes.
- `falsifier` — the command you ran, verbatim.
- `falsifier_result` — the output you saw, verbatim, including a failure.
- `key_property_preserved` — does a disproved finding still score 0 under your fix: YES / NO, with the executed check.
- `disagreement` — your strongest disagreement with this brief's own framing. This field is not optional and "none" is a non-answer: the brief was written by the same author as the evidence in it.
- `passes_run` — how many.

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could cause a wrong convergence verdict, a wrong fix admission, or a figure reported to the founder that cannot be reproduced.

Do not converge with the other seats. Disagreement is preserved as information here, not smoothed to consensus.

---

Written under CDSFL note standard v1.9.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 52 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel severity_spec_is_uncomputable_2026-11-04) -->

All green. Writing up.

---

## `verdict`

**NOT_AS_SPECIFIED.** `Sev(f) = W(class) · confidence · V(verification)` cannot be formed — `confidence` is collected on 0 of 3,691 archived entries and the HARD/SOFT class has no field. But the brief's diagnosis of *why that matters* is wrong: the one stated KEY PROPERTY never depended on `confidence`, and it is now enforced.

## `reasoning`

**The KEY PROPERTY is invariant to the two missing factors — derived, not argued.** Write `Sev = M · V`, `M = W·confidence ∈ [0,1]`. z3: `∃M∈[0,1], V=0, M·V≠0` → **unsat**. Wolfram Language (local Wolfram Engine, via wolframscript, exit 0): `Resolve[Exists[{m},0<=m<=1&&m*0!=0],Reals]` → `False`. So not collecting `confidence` was never what prevented the key property from holding. What prevented it was that the partition readers read the asserted float raw.

**Instruments run.** Archive: 78 `bench/logs/**/runner_state.json`, **3,691 entries** (the brief's 3,298 is stale; `confidence` count is still 0).

- `FindingRegistry.severity_spec_shadow` — returns on **78/78** runs; `V_true=1382 V_none=2267 V_false=42`. Consumers in the gating path: **none**. Sole consumer is `telem["severity_spec_shadow"]` at line 11389. Brief **CONFIRMED**.
- **Key-property violations: 37 of 42 = 88.0952%**, Wilson [74.9996%, 94.8062%], Clopper-Pearson [74.3683%, 96.0194%] — reproduces the brief's figure to the digit.
- `_check_gamma_alt_convergence` — `gamma_critical` **is** load-bearing (the docstring's "γ IS REPORTED, NEVER A TRIGGER" refers to plain `gamma`). I called the real function, never a copy; line ~11020 records that a prior reimplementation of this gate answered about a gate that does not exist.
- **`gamma`/`gamma_critical` recomputed over all 78 runs under `asserted · V`: partition moves on 29/78, `gamma_critical` on 20/78, and the real gate FLIPS on 11/78 — 14.1026%, Wilson [8.0610%, 23.5140%] — *all eleven False→True*, every one through the VACUOUS-CURVE branch.** The CRITICAL partition is **not** stable under a severity definition that drops `confidence`.
- **Why**, derived: severity ∈ [0,1], cut 0.7, so `sev/2 ≥ 0.7` needs `sev ≥ 1.4`. sympy `solve(sev/2−7/10)` → `7/5`; Wolfram `Reduce[sev/2>=7/10&&0<=sev<=1,sev,Reals]` → `False`. `V(None)=0.5` makes **every** unresolved finding sub-critical — exactly the population the A4 fail-safe exists to block on. The branch's own comment warns "a clean target and a broken severity classifier look alike from here"; the full product makes the runner the second and reads it as the first.
- `S_k`/`sigma` — **cannot carry `Sev`**. The runner states "S_k measures the quality of a FIX, not the truth of the claim", and `test_immune_memory_consumption.py:395` *pins the set of functions permitted to read `sk_result`* so S_k cannot influence routing. A test enforces the boundary.
- `nu` — **separable on the all-severity channel, not on the critical channel.** `all_s` moved on **0 of 78** runs under any severity redefinition (it increments before the severity test); `crit_s` moved on 29.
- Found by the patch refusing to apply: **a second partition reader**, `_corroborated_novelty_series` (line 10912), carrying an identical raw-severity read. The brief names neither.

**The fix.** The restricted form — annihilator only, `V=0 ⇒ 0`, other values untouched — flips **0 of 78**, Wilson [0.0000%, 4.6938%], Clopper-Pearson [0.0000%, 4.6192%]. It **dominates** the full product on a named property: manufactured convergences, **0 against 11**. Per the founder's composability rule I therefore did **not** compose: the single fix performs strictly better alone, so no vacuous-curve guard was added — that would have been an addition nothing reaches. No new flag: the form differs from `effective_severity` because the *guard* differs (the A4 door is conjunctive with `severity_is_proven`; the partition has no guard).

## `fix`

| Path | Change |
|---|---|
| `bench/reference_runner_v3.py` | New `spec_critical_severity()` with the derivation and measurement; both `_settled_novelty_series` and `_corroborated_novelty_series` rewired from the raw read to it. Unconditional — §7.7 states the key property with no configuration attached. `effective_severity`/`severity_spec_enabled` untouched. |
| `bench/tests/test_severity_key_property_critical_partition_2026-11-04.py` | 16 **executing** tests (0 source-text assertions, per that guard's own instruction), incl. an executed disproof that the full product manufactures a vacuous curve. |
| `scripts/does_the_severity_definition_reach_the_convergence_gate_2026-11-04.py` | The measurement instrument (full vs restricted, real gate). |
| `scripts/falsifier_key_property_in_the_critical_partition_2026-11-04.py` | The falsifier. |
| `docs/MATHEMATICAL_APPENDIX.md` | §7.7 caution 3 + the key-property-invariance derivation; §7.10 `Sev(f)` row corrected (it said "NOT implemented", which now understates and overstates in different directions). |

## `falsifier`

```
python3 scripts/falsifier_key_property_in_the_critical_partition_2026-11-04.py
python3 -m pytest bench/tests/test_severity_key_property_critical_partition_2026-11-04.py -q
```

## `falsifier_result`

```
[A] KEY PROPERTY: a disproved finding is not a critical discovery
  _settled_novelty_series: REFUTED 0.9 -> crit_s                 OK
  _corroborated_novelty_series: REFUTED 0.9 -> crit_s            OK
[B] V(None) must NOT de-escalate (A4 fail-safe must stay armed)
  _settled_novelty_series: UNRESOLVED 0.9 -> crit_s              OK
  _corroborated_novelty_series: UNRESOLVED 0.9 -> crit_s         OK
[C] No archived convergence verdict is restated
  replayed 78 archived registries
  archived gate verdicts changed by the repair                   OK
defect NOT demonstrated: ... 0 of 78 archived verdicts move.    EXIT=0
16 passed in 0.55s
```

Fails **iff** the defect is present — with `spec_critical_severity` monkeypatched back to the raw read: `FALSIFIED` on both readers, `AssertionError: defect present: _settled_novelty_series: REFUTED 0.9 -> crit_s [1]; _corroborated_novelty_series ... [1]`.

**Regression: 157 passed** across 11 related severity/gamma/novelty test files; **35 passed** on the appendix reduction-properties audit. **One pre-existing failure I did not cause and did not repair:** `test_source_text_and_neighbour_audit_2026-09-11.py::test_the_class_has_not_grown_silently`, 5 unpinned source-text assertions, all in `*_2026-11-02.py` files (other seats' work). Grepping the failure output for `2026-11-04` returns 0. This sandbox is not a git checkout, so I could not diff to prove pre-existence — I am reporting the inference, not a measurement.

## `key_property_preserved`

**YES.** Check [A] above, executed: `severity=0.9, falsifier_verdict=REFUTED` → `crit_s=[0]` on both readers, while `all_s=[1]` (a refuted finding is still a finding). `test_key_property_annihilates_whatever_was_asserted` sweeps asserted ∈ {0.0, 0.3, 0.7, 0.9, 1.0} → 0.0 for all.

## `disagreement`

**The brief's claim 1 is mis-scoped, and it is the load-bearing half of its framing.** `cdsfl_operational.md:773` does not rule self-reported confidence inadmissible as a severity input. It sits inside *"Action precedence → 1. REFUTED by tool"* and forbids confidence as a **rebuttal to a tool verdict**: "Assertions that 'my reasoning is sound' *without tool receipts* are inadmissible." §7.7 does not merely comply with that — it *implements* it, setting confidence's weight to exactly 0 in precisely the case the directive names (`V(False)=0` iff a tool refuted). Where no tool refuted, the directive is silent. **The two documents are in exact agreement.** The brief's "contradiction between 2 documents the harness treats as binding" does not exist, and the asymmetry it calls "the whole question" dissolves: both missing factors are absent for the same ordinary reason — nobody built a writer.

Three further disagreements. (a) **"§7.7 is NOT implemented / gates nothing" overstates**: `effective_severity` + `RunnerConfig.severity_spec_enabled` were built 2026-10-15 to make §7.7 decide, and the brief's artefact list omits both. The accurate statement is that the promotion is wired to **1 of the 2** severity consumers that decide convergence — executed: flag ON drives `effective_severity` 0.9→0.0 while the critical series stays `[1]`. (b) **The brief's candidate direction #1, "drop `confidence` and renormalise the remaining 2 factors", is the one that breaks the harness**, and it is listed first and neutrally — 11 of 78 runs converge that did not. The brief invited refutation of its candidates; this is the refutation, and it is the single most consequential result I have. (c) **3,298 is stale** (3,691 now) — though the 88.0952% headline reproduces exactly, because the REFUTED population is unchanged at 42. The brief's figure is right; its denominator is not.

Where the brief is simply correct, and I confirm it against my own measurement: the shadow gates nothing, the 88.0952% figure and both its intervals, and the 0-`confidence` finding.

## `passes_run`

**4.** P1 mapped the code paths (refuted "gates nothing"; found the raw read at 10794). P2 measured (88.0952% reproduced; 11-flip result; four derivations, each cross-checked on Wolfram). P3 implemented — and the patch refusing to apply on a unique match surfaced the second partition reader, an above-threshold finding that justified P4. P4 regression + bidirectional falsifier + appendix. P4 produced no new above-threshold finding, so I stop.

**Residual falsification debt, stated rather than hidden:** `W` and `confidence` remain uncollected, so the asserted float still stands in for `W·confidence` in both consumers. I did **not** add the HARD/SOFT field. It needs a writer, a reader and a collection-side default, and §7.7 caution 2 shows the default must be **SOFT** here (inverting `cdsfl_core.txt` §1) — too large to land on measurement I have not taken, and 11 of this project's confirmed defects were additions nothing reached.

## What would refute me

- **My restricted form is worse than the asserted float if** replaying the archive shows it removes a finding from the critical count that a *later* round re-confirmed — i.e. `falsifier_verdict=REFUTED` is not terminal. My fix treats REFUTED as permanent annihilation. Named property: **count of REFUTED→CONFIRMED transitions on one canonical id.** I did not measure it, and it is the weakest joint in this answer. If it is non-zero, the fix must read the *latest* verdict, not any verdict.
- **The whole approach falls if** `V(None)=0.5` is shown to be *intended* for the critical partition — e.g. a founder ruling that an unresolved critical should de-escalate rather than block. Then my 11-flip result is the specification working, not a defect, and the A4 fail-safe is what needs changing.
- **The 0-of-78 flip result is weaker than it reads.** All 78 replays hold `unresolved_critical=0` and `contested=0` so that severity is the only varying input. A live run with those non-zero could flip where my replay does not. Named property: **gate verdict flips under a replay that also varies `unresolved_critical`.**
- `spec_critical_severity` would be refuted as *simplest sufficient* if a single change at the `crit_s` comparison, with no new function, gave the same 0-flip result. I chose a named function because there are two readers; with one reader the inline form would win.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 50 recorded tool call(s).

<!-- verbatim-begin: fable (panel severity_spec_is_uncomputable_2026-11-04) -->

All instruments executed, fixes delivered and tested. Final report.

---

`verdict` — **NOT_AS_SPECIFIED.** The §7.7 product cannot be computed in this harness: `confidence` is inadmissible by binding directive, the HARD/SOFT class has no registry field, and only `V` is collected.

`reasoning` —

**The contradiction is real and one-sided as the brief says, with one correction.** `cdsfl_operational.md` §15 (d_tool: quantities come from tool execution, "not from self-assessed confidence") and feedback action-precedence item 1 ("Self-reported confidence is not accepted") forbid the `confidence` factor. My independent scan of every distinct archived registry (67 registries, 3,170 entries, content-hash deduplicated) confirms **0 entries carry `confidence` and 0 carry a constraint class** — the brief's 0-of-3,298 claim survives in direction and substance. Admitting confidence instead (candidate e) is refuted by derivation: z3 returns **unsat** for the negation of `Sev ≥ 0.7 ⟺ HARD ∧ CONFIRMED ∧ conf ≥ 0.7`, and inside the surviving cell `Sev = confidence` exactly — the gate would equal the model's self-assessment, a vote.

**Instruments run (archive paths: `bench/logs/**/runner_state.json`, 77 files read, 67 distinct registries, 3,170 entries):**

- **`severity_spec_shadow`** — executed on all 67 distinct registries via `FindingRegistry`. Deduped key-property violations: **27 of 32 REFUTED, 84.3750%**, not the brief's 37 of 42. Consumers: exactly one, `telem["severity_spec_shadow"]` at `reference_runner_v3.py:11389` — telemetry; **gates nothing** (confirmed: no gating-path read exists).
- **`_check_gamma_alt_convergence`** — executed per run with both severity definitions. The cut does **not** merely collapse to an inert threshold test: recomputing severity as `Sev_op = compute_sev_f(class, confidence, verdict)` (= `V` on all archived data) **moves the critical partition on 588 entries and flips the convergence verdict True→False in 12 of 46 verdict-bearing runs**. The static collapse claim (producer 2) is simultaneously true — z3-confirmed — but the collapsed conjunction selects a *different population* than the asserted float, so the gate verdict moves. Both halves hold.
- **`gamma` / `gamma_critical`** — recomputed over all 46 runs: `gamma_all` is byte-identical under both definitions (the severity cut does not enter the all-severity series); `gamma_critical` moves in nearly every run (e.g. leg3_final_shakedown 1.000→0.702). The CRITICAL partition is **not stable** under dropping confidence.
- **`S_k` / `sigma`** — cannot carry Sev(f). `compute_sk(fix_text, source, …)` scores a **proposed fix** (SEARCH/REPLACE application + hard gates), and §15 σ_measured defines σ = g(V_pre, V_post) from post-fix re-runs. Sev labels a *finding*; S_k measures a *fix*. Different object, different time.
- **`nu` / novelty** — separable at the per-finding layer (η is similarity-computed, reads no severity; `all_s`/`gamma_all` provably unchanged), **not** separable at the critical-novelty series, which is a severity-filtered count by construction (`_settled_novelty_series`).

**The brief's evidence, refuted on scope.** The producer's recursive glob counts sandbox_harvest **copies** of `runner_state.json`: 10 of 77 matched files are byte-identical copies, and the 5 REFUTED findings of `commissioning_arm1_panel_20260929T214647Z` (C0002/C0003/C0004/C0016/C0046) each entered the tally **three times**: 42 = 32 + 2×5, 37 = 27 + 2×5. Corrected: **27/32 = 84.3750%, Wilson [68.2459%, 93.1356%], Clopper-Pearson [67.2121%, 94.7249%]** (Wilson endpoints independently confirmed with Wolfram Language, local Wolfram Engine, verbatim `{0.84375, 0.682459…, 0.931356…}`). Direction unchanged; figure mis-scoped.

**The simplest sufficient replacement: `Sev_op(f) = W(class) · V(verification)` — drop confidence, do not proxy it.** §7.8's S_v with the harness's one verifier is a monotone relabel of V (0.9990/0.5/0.0099 at the SymPy-row rates) and S_v(falsified) = 0.0099 ≠ 0, so S_v **alone breaks the key property**; composing W·S_v·V preserves it but is a deterministic function of the same verdict V already reads — no demonstrated advantage, so the founder's composability rule selects the single fix. Critically, the harness **already computes Sev_op**: `compute_sev_f`/`stamp_sev_f` exist, are wired into the round loop (line 20523), tested, default-off — a fact the brief omits. And the key property must bind **scoring only, never the blocking gate**: CONFIRM-only for criticals stands on Exp 42's measurement that 2 of 3 REFUTED criticals were falsely REFUTED — §7.7-compliance at the gate would have released real defects, and my 12 measured True→False flips show promotion is replay-invalidating, hence the founder's call.

`fix` — three files, all in the sandbox tree:
1. `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` — `entries()` now deduplicates registries by content hash and **reports** the skip (10 copies). Figures become reproducible per distinct finding.
2. `docs/MATHEMATICAL_APPENDIX.md` — §7.7 computability note (4 points: uncomputable as specified; operational form `W·V` with the S_v refutation; key-property scope = scoring not gate, with the 588/12 measurement; figure scope correction) + §7.10 row correction.
3. `scripts/the_severity_definition_moves_the_convergence_verdict_2026-11-04.py` — persisted producer for the 588-flip / 12-verdict-flip measurement (reproduces from the tree).
4. `bench/tests/test_severity_operational_form_2026-11-04.py` — executes the key property exhaustively and the producer dedup on a synthetic duplicate tree.

`falsifier` —
```
python3 -m pytest bench/tests/test_severity_operational_form_2026-11-04.py -q
python3 scripts/severity_was_never_computed_from_the_model_2026-10-12.py
python3 scripts/the_severity_definition_moves_the_convergence_verdict_2026-11-04.py
python3 -m pytest bench/tests/test_the_severity_specification_shadow_2026-10-12.py bench/tests/test_sev_f_and_queue_membership_2026-10-13.py bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py bench/tests/test_appendix_reduction_properties_2026-09-05.py bench/tests/test_appendix_inverse_is_executed_2026-09-20.py bench/tests/test_sk_measures_fix_efficacy_2026-09-20.py -q
```

`falsifier_result` — verbatim tails: `3 passed in 0.61s`; producer: `[scope] skipped 10 duplicate registry copies … disproved (REFUTED) findings : 32 / NON-ZERO severity : 27 / violation rate : 84.3750% / Wilson [68.2459%, 93.1356%]`; movement producer: `critical-partition flips … 588 / convergence-verdict flips … 12` (12 runs listed, all True → False); regression suites: `34 passed in 1.51s` and `63 passed in 7.63s`. No failures.

`key_property_preserved` — **YES.** Executed: `compute_sev_f(cls, conf, "REFUTED") == 0.0` asserted over 7 class values × 8 confidence values × 3 verdict spellings (168 cases) — passed. Symbolically: SymPy, `W·c·0 = 0`.

`disagreement` — Four, strongest first. (1) **The brief's headline figure is mis-scoped**: 88.0952% triple-counts 5 findings via sandbox_harvest registry copies; the distinct-finding rate is 84.3750% [68.2459%, 93.1356%]. (2) **"Exactly one of them is collected" understates the tree**: `compute_sev_f`/`stamp_sev_f` already implement the §7.7 product as a wired, tested, default-off derived field with reader-side support for both missing factors — the candidate direction "add the HARD/SOFT field" needs only a writer, not the from-scratch build the brief implies. (3) **The KEY PROPERTY is not unconditionally desirable**: at the blocking gate it is refuted by the harness's own Exp 42 measurement (2/3 of REFUTED criticals falsely REFUTED); the 84% "violation" is a scoring-layer defect only, and full §7.7 gate-compliance would have released real defects. (4) Minor: the brief's artefact list names `_sk_admits` in `bench/reference_runner_v3.py`; no such function exists in the current file (prose references in one test and one script only).

`passes_run` — 5. Pass 5 (regression and consumer sweep: appendix-coupled tests, figure registry, telemetry consumers) produced no new above-threshold findings — terminated converged, no residual falsification debt on the claims above. Wolfram ran as second falsifier on one computed result (Wilson endpoints); all primary verification is SymPy/z3/statsmodels/scipy.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/severity_spec_is_uncomputable_2026-11-04/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
