# Panel FULL RECORD — the severity specification, round 2 (joint), 2026-11-04

Record written 2026-11-04T01:41:44+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

# Panel record — severity specification, JOINT round, 2026-11-04

**Both replies are kept UNFILTERED and byte-exact in `Panel_FULL_RECORD_Severity_Joint_2026-11-04.md`**, verified identical to `cc2.json` and `fable.json` at write time: 23,552 and 13,767 characters. Round 1 is in `Panel_FULL_RECORD_Severity_Spec_2026-11-04.md`. This file carries only the synthesis and what was checked.

## Dispatch

| | |
|---|---|
| brief | `bench/logs/joint_severity_spec_is_uncomputable_2026-11-04/BRIEF.md`, 26,991 characters, carrying both round-1 replies in full |
| topology | JOINT round, `joint_of=['severity_spec_is_uncomputable_2026-11-04']`, stagger 20 s |
| seats | `cc2` 23,552 chars / 61 tool calls / 1067.6 s; `fable` 13,767 chars / 819.5 s |
| paid seats | **0**. No spend. |
| seat-proposed edits | 41 files, **untested and NOT applied** |
| why it ran | the dispatcher REFUSED a new blind round while this one owed a joint round. That refusal was correct and is what produced this result. |

## Both items resolved, and each seat withdrew a round-1 claim of its own

**That is the outcome worth reading.** No convergence was compelled; both seats moved on evidence and each names what moved it.

### ITEM 1 — the opposite-sign contradiction DISSOLVES, and my own synthesis of round 1 is superseded

Round 1 looked like a contradiction: `cc2` measured 11 of 78 gate flips all False→True, `fable` measured 12 of 46 all True→False. **I recorded that as "opposite failure modes depending on the substitution". That framing is now superseded.**

Measured on 1 archive (67 distinct registries, 3,170 entries) through the REAL `_settled_novelty_series` into the REAL `_check_gamma_alt_convergence`, with A4 inputs forced to 0 so severity is the only mover:

| substitution | flips / 67 | False→True (manufactured) | True→False (prevented) |
|---|---|---|---|
| `asserted · V` (`cc2`'s) | 11 | **11**, all vacuous-curve | 0 |
| `compute_sev_f(class, confidence, V)` (`fable`'s) | 23 | **11**, the same runs | **12** |
| `W(class) · V` (`fable`'s proposed fix) | 23 | 11 | 12 |
| restricted annihilator (`cc2`'s proposed fix) | **0** | 0 | 0 |

**`fable` withdrew its own direction claim.** Its "every one True→False" was an artefact of its run cut: the 11 manufactured flips all occur in runs carrying **0** entries with any `falsifier_verdict`, where every entry gets `V=0.5`, the critical series falls to 0 throughout and the vacuous-curve branch opens. Restricting to the 46 **verdict-bearing** runs excludes by construction exactly the population where the manufacturing happens.

**So "drop `confidence`" is not 2 options with opposite failure modes.** It is 2 options of which one has **both** failure modes and the other has one. `fable`'s 2 forms are also **a single function on this archive** — `compute_sev_f` and `W·V` differ on 0 of 3,170 entries, because class defaults to HARD and confidence defaults to 1.

**`cc2` withdrew something too:** it had not considered that a severity redefinition could RAISE severity. z3 gives the witness (`asserted=0, V=1`), and that non-monotonicity is the whole mechanism of the True→False half.

**The 2 seats' flip totals for `fable`'s substitution differ slightly — 23 against 26** — and both agree on the 11 False→True and on the restricted form flipping 0. That residual is not reconciled here and is recorded rather than smoothed.

### ITEM 2 — resolved AGAINST BOTH SEATS, and B87's letter-level conflict dissolves

`fable` quoted both clauses with line numbers and conceded by reading.

`bench/directives/universal/cdsfl_operational.md:600-606` (§15, `d_tool`) scopes its prohibition to **the detection probability `d` entering `q = η · d · p`**: *"must come from actual tool execution ... not from self-assessed confidence"*. The §15 preamble at line 578 scopes all 5 constraints to a finding or parameter update entering the `R_k` update. Lines 773-775 forbid self-reported confidence as a **rebuttal**: *"Assertions that 'my reasoning is sound' without tool receipts are inadmissible."*

**Those are the only 2 occurrences of `confidence` in the whole directive**, by grep. **Severity is not `d`, and `Sev(f)` is not a factor of `q`.** So §15 does not, by its letter, forbid `confidence` as an input to a harness-computed quantity in general.

**`cc2` also rejected its OWN round-1 position** that the 2 documents are *"in exact agreement"* — that overstated in the opposite direction. The clauses are independent prohibitions with different scopes; neither reaches severity.

**WHAT REMAINS FOR THE FOUNDER IS ONE PRECISELY NAMED CASE, and it is a judgement rather than a reading.** Model self-assessed confidence as an input to a harness-computed severity that reaches a convergence gate. §7.7 includes it. `d_tool`'s **rationale** — that a self-assessment must not source a convergence-deciding number — extends to it only by **analogy**, and an analogy is not a directive.

- **Reading R1**: silence means permitted; the documents agree. *This is what the text supports.*
- **Reading R2**: `d_tool` states a principle merely instanced at `d`. *A design judgement he may adopt; nothing in the text compels it.*

`fable`'s own words on its round-1 answer: it *"erred by presenting R2 as the text."*

## `cc2` discharged the debt it named itself, and the answer changed its fix

Round 1 it wrote that its fix treats `REFUTED` as permanent annihilation and that it had **not** measured REFUTED-to-CONFIRMED transitions, calling it the weakest joint in its answer. Measured 3 ways:

- **Archive**: `falsifier_verdict == "REFUTED"` on 32 of 3,170 entries; 63 `status_log` hops out of REFUTED, **all 63 REFUTED-to-REFUTED**. **REFUTED-to-CONFIRMED: 0.**
- **Code**: `record_in_round_falsifier_reattachments` and `_post_convergence_sweep` skip on `status` only, never on `falsifier_verdict`.
- **Executed**: calling the real reattachment on an entry stamped `falsifier_verdict="REFUTED", status="OPEN"` with a demonstrating falsifier returned `executed=1 cleared=1` and the verdict moved **REFUTED to CONFIRMED**.

So the count is 0 in the archive but the transition is **REACHABLE**, which is what its round-1 refutation condition said would force the fix to read the LATEST verdict rather than any verdict. A seat naming its own weakest joint, measuring it, and changing its fix on the result is the method working.

## A third gating reader, which neither round 1 nor the brief named

`fable` extended the repair to `_location_keyed_critical_series` at about line 11295, which **gates**. The count of raw-severity partition readers has gone 1 (my brief) to 2 (`cc2`, round 1) to **3**.

## What this changes

1. **Section 10.2 of `Consolidated_Report_Since_Yesterday_Morning_2026-11-04.md` is superseded** and corrected: the opposite-signs framing was mine and the joint round refutes it.
2. **Entry B87's letter-level conflict dissolves.** What survives is 1 named unlegislated case and 2 readings, for his ruling.
3. 3 raw-severity readers exist, not 1.
4. **Nothing is applied.** 41 proposed file edits sit untested in `seat_proposals.diff`, per `fixes-to-HIL-only`.

---

Written under CDSFL note standard v1.9 (1 November 2026).

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# JOINT PANEL BRIEF — the severity specification, round 2. YOU DISAGREE WITH EACH OTHER ON 2 THINGS.

**This is the JOINT half of `severity_spec_is_uncomputable_2026-11-04`.** That round was BLIND. Both seats answered, both refuted the brief, and both replies are reproduced IN FULL below so this round is exposure rather than a pointer at a file.

**NO COMPELLED CONVERGENCE.** A seat that reads the other and does not move has done its job, provided it names the specific claim it rejects. A seat that moves has also done its job, provided it names what moved it. Splitting the difference without engaging a claim is the one unacceptable answer.

## WHAT IS SETTLED. DO NOT SPEND THIS ROUND ON IT.

**1. The brief's headline figure was wrong and `fable` is right.** CC1 reproduced it independently before believing it. `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` globbed `bench/logs/**/runner_state.json`: 77 files, 10 under `sandbox_harvest/`, 67 distinct by content hash. `42 = 32 + 2*5` and `37 = 27 + 2*5`, exact to the integer. **The rate is 27 of 32 = 0.843750, Wilson [0.682459, 0.931356]**, not 37 of 42. The appendix is corrected and the producer now deduplicates and prints the skip. **`cc2`: your correction of the denominator to 3,691 is inflated by the SAME mechanism; the deduplicated count is 3,170.**

**2. `_sk_admits` does not exist.** `grep -c 'def _sk_admits'` returns 0. CC1 wrote that into the brief's artefact list and withdraws it.

**3. The shadow gates nothing.** Both of you confirmed it independently.

## WHAT THIS ROUND IS FOR: THE 2 ITEMS ON WHICH YOU CONTRADICT EACH OTHER

### ITEM 1 — dropping `confidence` flips the gate in OPPOSITE directions

`cc2`: substituting `asserted * V` moves the partition on 29 of 78 runs and flips the real gate on **11 of 78, every one False to True** — manufacturing convergences, all through the vacuous-curve branch. Derived: severity in [0,1] with a 0.7 cut means `sev/2 >= 0.7` needs `sev >= 1.4`; SymPy gives 7/5, Wolfram `Reduce` gives False. `V(None)=0.5` makes every unresolved finding sub-critical.

`fable`: substituting `compute_sev_f(class, confidence, verdict)` moves the partition on 588 entries and flips **12 of 46 verdict-bearing runs, every one True to False** — preventing convergences.

**The question for this round.** You substituted different definitions, so these may be 2 compatible results about 2 different changes rather than a contradiction. **Establish which, by execution, on the SAME archive and the SAME gate.** If both hold, then "drop `confidence`" is not 1 option but 2 with opposite failure modes, and that is the result the founder needs. If one is an artefact of its substitution, name which and why. The safety asymmetry matters: manufacturing a convergence releases defects, while preventing one only costs rounds.

### ITEM 2 — whether the directive and the appendix conflict at all

This is the hinge of open task entry B87.

`cc2`: `cdsfl_operational.md:773` forbids confidence only as a **rebuttal to a tool verdict**. It sits under *Action precedence, item 1, REFUTED by tool*, and reads *"Assertions that 'my reasoning is sound' without tool receipts are inadmissible."* Section 7.7 **implements** that by setting confidence's weight to 0 exactly where a tool refuted. On that reading the 2 documents agree and B87's central claim dissolves.

`fable`: the conflict is real, citing **section 15 `d_tool`** — quantities come from tool execution, *"not from self-assessed confidence"* — as an **independent** prohibition, separate from action precedence.

**The question for this round.** You cite different clauses of the same document. **Quote both clauses verbatim, with their line numbers, and state whether section 15's `d_tool` independently forbids `confidence` as an INPUT TO A HARNESS-COMPUTED QUANTITY, as distinct from forbidding it as a REBUTTAL.** This is a question about 1 document and it is answerable by reading it. If it is genuinely ambiguous, say so and name the ambiguity precisely, because the founder will rule on it and he needs the 2 readings stated cleanly rather than a verdict.

## REQUIRED SECTION 1 — The question

Resolve item 1 by measurement and item 2 by reading, or establish that either is irreducible. Name the artefact under review by path: `bench/reference_runner_v3.py`, `bench/directives/universal/cdsfl_operational.md`, `docs/MATHEMATICAL_APPENDIX.md` section 7.7 and section 15.

## REQUIRED SECTION 2 — Use the harness

Form your answer by RUNNING the machinery named here, not by describing it. For item 1 you must call the REAL `_check_gamma_alt_convergence` and recompute `gamma_critical` over the archive under BOTH substitutions, reporting how many runs flip under each and in which direction. `S_k`, `sigma` and `nu` are already settled between you and need no further work. A seat that returns prose without having run anything has not answered.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete; a fix without an EXECUTED falsifier is a hypothesis. Write it INTO the sandbox tree at its real path. Report the command and the output verbatim.

`cc2` proposed the restricted annihilator-only form and measured it flipping 0 of 78, and declined to compose on the founder's rule because the single fix dominates. `fable` proposed `W(class) * V(verification)`. **These 2 are not obviously the same fix.** State whether they are, and if not, which dominates on a NAMED property with a MEASUREMENT. Compose ONLY on a demonstrated advantage over each part alone, and prefer the single fix wherever it performs as well; 2 repairs that merely coexist have not met that standard.

**`cc2`, 1 specific debt you named yourself:** your fix treats `REFUTED` as permanent annihilation and you did not measure REFUTED-to-CONFIRMED transitions on a single canonical identifier. You called it the weakest joint in your answer. Measure it this round.

## REQUIRED SECTION 4 — What would refute you

State what evidence would overturn your own answer before you conclude.

## REQUIRED SECTION 5 — Output shape

Return exactly these fields, in this order:

- `verdict`
- `moved` — what moved you and what did not, naming the claim each way
- `flip_direction` — item 1 above resolved or irreducible, with the figures
- `clause_reading` — item 2 above: the 2 clauses quoted verbatim with line numbers, and your reading
- `fix` — the path(s) you wrote in the sandbox tree
- `falsifier` — the command, verbatim
- `falsifier_result` — the output, verbatim, including a failure
- `refuted_to_confirmed_count` — `cc2` only; `fable` states it is not yours
- `disagreement` — your strongest disagreement with this brief's own framing. Not optional, and "none" is a non-answer.
- `passes_run`

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings and say how many you ran. A finding is above threshold if missing it could cause a wrong convergence verdict, a wrong fix admission, or a figure reported to the founder that cannot be reproduced.

---

# ROUND 1, SEAT cc2, VERBATIM AND COMPLETE

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

---

# ROUND 1, SEAT fable, VERBATIM AND COMPLETE

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

---

Written under CDSFL note standard v1.9.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 61 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_severity_spec_is_uncomputable_2026-11-04) -->

All instruments executed. Final report.

---

`verdict` — **BOTH ROUND‑1 RESULTS HOLD; THEY ARE NOT A CONTRADICTION.** Item 1 is **resolved by measurement**: `cc2`'s 11 False→True and `fable`'s 12 True→False are two compatible results about two *different* functions, and `fable`'s substitution produces **both** signs. Item 2 is **resolved by reading, against both seats**: neither cited clause forbids `confidence` as an input to a harness‑computed quantity. The §7.7 product is still uncomputable as specified; the KEY PROPERTY is now enforced at the critical partition.

I answer as the shell‑bearing seat, `cc2`. The `refuted_to_confirmed_count` field is below either way, because I measured it.

---

`moved`

**Moved me.** (1) **`fable`'s denominator correction is right and my 3,691 was wrong by the same mechanism I was told it was.** 67 distinct registries, **3,170 entries**, `confidence` on **0**, `constraint_class` on **0** — reproduced in my own producer before adopting. (2) **`fable`'s claim that `compute_sev_f`/`stamp_sev_f` already implement the §7.7 product** — true, and my round‑1 artefact list under‑described the tree. (3) **`fable`'s W·V is non‑monotone and can ADD criticals** — I had not considered that a severity redefinition could *raise* severity; z3 gives a witness (`asserted=0, V=1`). That is the whole mechanism of the T→F direction and I missed it.

**Did not move me.** (1) **`fable`'s "every one True→False" is incomplete, not wrong.** The same substitution manufactures the same 11 convergences I found. The 11 runs it misses carry **0** entries with any `falsifier_verdict`; restricting to the **46** verdict‑bearing runs — `fable`'s exact denominator — excludes by construction every run where the manufacturing happens. (2) **I reject `fable`'s reading that §15 `d_tool` is an independent prohibition** (below). (3) **I reject my own round‑1 claim that the two documents are "in exact agreement."** That overstated in the opposite direction; see `clause_reading`.

---

`flip_direction` — **RESOLVED.** One archive (67 distinct, 3,170 entries), one gate, `RunnerConfig()` defaults, real `_settled_novelty_series` → real `_check_gamma_alt_convergence`. A4 inputs forced to 0 so severity is the only mover:

| substitution | flips / 67 | False→True (manufactured) | True→False (prevented) |
|---|---|---|---|
| `cc2`: `asserted * V` | 11 | **11**, all VACUOUS‑CURVE | 0 |
| `fable`: `compute_sev_f(class, confidence, V)` | 23 | **11** (same runs) | **12** |
| `fable` fix: `W(class) * V` | 23 | 11 | 12 |
| `cc2` round‑1 fix: annihilator only | **0** | 0 | 0 |
| **SHIPPED** `spec_critical_severity` | **0** [Wilson 0.0000%, 5.4226%] | 0 | 0 |

**`fable`'s two forms are one function here** — `compute_sev_f(class, confidence, V)` and `W·V` differ on **0 of 3,170** entries, because class defaults to HARD (W=1) and confidence defaults to 1. So `fable`'s *proposed* fix **is** the 23‑flip substitution.

**Both seats' numbers reproduce exactly**: 11 (mine) and 12 (`fable`'s), on the same run.

**Derived, not asserted.** `asserted·V` is monotone non‑increasing — z3 **unsat** for the negation over `asserted∈[0,1], V∈{0,½,1}` — so it can only *remove* criticals, and `asserted·½ ≥ 0.7` is unsatisfiable on [0,1] (SymPy boundary `7/5`; second falsifier: Wolfram Language, local Wolfram Engine, `Reduce[0<=a<=1 && a/2>=7/10,a,Reals]` → `False`, exit 0). Every unresolved finding therefore goes sub‑critical, the series goes to all‑zero, and the vacuous‑curve branch converges. `W·V` is **not** monotone (z3 **sat**, witness `asserted=0, V=1`), so it also *adds* criticals, destroys the zero tail and refuses convergence. Note the precision: monotonicity makes condition (a) only easier but `gamma_critical` is not monotone in the series, so T→F is not excluded *a priori* under `asserted·V` — it simply did not occur, 0 of 67.

**Two findings the brief did not ask for, both above threshold.**

1. **The A4 fail‑safe does not remove the manufactured direction.** Recomputing `unverified_critical_count` / `contested_count` / `irreducible_queue_count` under the *same* substituted severity (which they also read): `asserted·V` → **3** flips, all still F→T, all still VACUOUS; `W·V` → 11 (3 F→T + 8 T→F); shipped fix → 0. The fail‑safe shrinks the manufacturing 11→3; it does not close it, because the substitution shrinks the blocker counter too.
2. **The brief named the wrong gate, and the result survives anyway.** `HARDENED_GATE_DEFAULT = True`, so a default‑config live run takes `_check_hardened_convergence` and *bypasses* `_check_gamma_alt_convergence` entirely (`reference_runner_v3.py:20959`). I replayed the hardened gate as well — it calls the same `_settled_novelty_series` at line 11391: `asserted·V` → **4 flips, all F→T**; `W·V` → **12 flips (4 F→T + 8 T→F)**; shipped fix → **0 of 67**. The two‑sign result is not an artefact of a legacy gate.

---

`clause_reading` — **The conflict is real but NEITHER seat located it correctly. Both cited clauses are out of scope, in opposite directions.**

`bench/directives/universal/cdsfl_operational.md` **lines 773–775**, under `## 17. Feedback Channel` → *Action precedence* → *1. **REFUTED by tool***:

> `773:   Self-reported confidence is not accepted. Assertions that "my`
> `774:   reasoning is sound" without tool receipts are inadmissible under this`
> `775:   directive.`

Same file, **lines 600–606**, under `## 15. FFAFP Admissibility Constraint Set` (section begins line 563), gate **`d_tool`**:

> `600: **d_tool — detection probability grounded in tool output.**`
> `601: The detection probability d entering q = η · d · p must come from actual`
> `602: tool execution (static analysis, test runner, SymPy verification, AST`
> `603: parse), not from self-assessed confidence. A claim of d = 0.9 based on`
> `604: "I am certain" is not admissible. d = 0.9 derived from "9 of 10 relevant`
> `605: tests caught the flaw class" is admissible. Formally: d_i = f(T_i) where`
> `606: T_i is the result of executing a defined verification tool.`

**My reading: §15 `d_tool` does NOT independently forbid `confidence` as an input to a harness‑computed quantity.** It names exactly one quantity — `d`, the detection probability *entering `q = η · d · p`* — and its formal statement is scoped to that index: `d_i = f(T_i)`. `Sev(f)` is not `d` and does not enter `q`. The enclosing section is a per‑finding admissibility set over the R_k inputs (`S_min`, `G‑completeness`, `d_tool`, `σ_measured`, `q_retest`); §7.7 severity is not among them, and the string `Sev(` appears **0 times** in the whole document. So `fable`'s "independent prohibition" reads a *scoped* gate as a *general* one.

**And my own round‑1 position was also wrong.** Line 773 is scoped to *rebuttal of a tool verdict*, so §7.7 setting `V(False)=0` does **not** "implement" it — §7.7 lets `confidence` pass through at full weight wherever no tool refuted (`V=1` or `V=0.5`), and nothing at line 773 reaches that case. "Exact agreement" was the wrong word: the two documents do not agree, they **do not meet**.

**So B87's central claim as stated — a conflict between two clauses of these two documents — dissolves, but the defect it points at is real and sits elsewhere.** `confidence` as a severity input is forbidden by neither clause; it is forbidden by CDSFL's founding principle *tools decide, not votes*, which lives in the panel directive and `cdsfl_core.txt`, not in a numbered clause of `cdsfl_operational.md`. The appendix already says so itself at §7.7 caution 1 — *"A severity gate built this way is therefore **not** 'the opposite of a vote' — it is the same vote taken over a smaller population… Making it tool-decided requires replacing `confidence` with a harness-computed quantity"*. **This is NOT genuinely ambiguous and I am not asking the founder to break a tie.** The ruling he needs to give is narrower than B87 frames it: *does `d_tool` generalise from `d` to every harness‑computed quantity, or does severity need its own admissibility gate?* Written as it stands, it does not generalise.

---

`fix` — written into the sandbox tree at these real paths:

| path | change |
|---|---|
| `bench/reference_runner_v3.py` | **new `spec_critical_severity(entry)`** + both novelty readers rewired from the raw `(e.get("severity") or 0.0) >= _thr` read (the only 2 occurrences, lines 10794 and 10965) to it. Annihilator only. Unconditional — §7.7 states the key property with no configuration attached. `effective_severity` / `_SEVERITY_SPEC` / `compute_sev_f` untouched. |
| `bench/tests/test_the_critical_partition_enforces_the_key_property_2026-11-04.py` | 24 **executing** tests, 0 source‑text assertions. |
| `scripts/which_direction_does_dropping_confidence_flip_the_gate_2026-11-04.py` | the flip‑direction producer (5 severity maps × 2 A4 variants × real gate). |
| `scripts/is_a_refuted_falsifier_verdict_terminal_2026-11-04.py` | the REFUTED‑terminality producer. |
| `scripts/falsifier_the_critical_partition_counts_a_disproved_finding_2026-11-04.py` | the falsifier. |
| `bench/tests/test_the_severity_spec_annihilates_the_a4_severity_door_2026-10-28.py` | **one assertion corrected, not weakened and not deleted**: `assert sum(crit_on) == 2` → `== 1`, plus `assert crit_on == [0,0,1,0]`. That test's own claim (`crit_off == crit_on`, the series does not move with the *flag*) is untouched and still checked. The 2 pinned the defect: its `C1` is asserted 0.9 with `falsifier_verdict == "REFUTED"`. Reported here rather than silently repaired, and the correction carries its own falsifier (check [A]). |
| `docs/MATHEMATICAL_APPENDIX.md` | §7.7 cautions **3** (the two‑sign table + derivations + why each seat saw one sign) and **4** (what is implemented); §7.10 `Sev(f)` row corrected from "**NOT implemented**" — now false in one direction — to "**PARTIALLY implemented: the KEY PROPERTY only**". |

**Are the two seats' fixes the same? No, and the single fix dominates — measured, not judged.** `fable`'s `W·V` and my annihilator‑only form differ on every archived entry with an unresolved falsifier. Named property, **gate verdicts the repair moves on the archive**: `W·V` **23** (legacy gate) / **12** (live hardened gate), of which **11** / **4** are manufactured convergences; annihilator‑only **0** / **0**. `fable` confined the key property to scoring precisely to avoid that, which is the right instinct and the wrong lever: scoping it away from the gate leaves the gate counting disproved findings as critical discoveries, which is the defect. **Per the founder's composability rule I did not compose:** the single fix is strictly better alone, so no vacuous‑curve guard and no S_v proxy were added — either would be an addition nothing reaches.

**One measured refinement to my own round‑1 form.** The shipped function also returns the asserted value when `status == "CONFIRMED"`. Not precautionary: **1 of 3,170** archived entries (`arm1_harvest` C0048, asserted 0.8) carries `falsifier_verdict == "REFUTED"` while its status is CONFIRMED, and CONFIRMED status is tool‑only in this registry (a model‑requested CONFIRMED is substituted to CORROBORATED and recorded in `refused_transitions`). Without the carve‑out the two forms differ on exactly that entry, on the corroborated series in **1** run and on `gamma_critical` in **1** run; with it, `gamma_critical` moves on **0 of 67**. Equal on flips (0 vs 0), strictly better on *runs whose `gamma_critical` the repair perturbs* (0 vs 1), and the residual failure direction is the cheap one. One extra conjunct, one extra test, measured reach of 1 entry — not a composition of two fixes.

**Reach, stated honestly against the additive standard:** the change moves **32** archived entries' computed severity, the critical partition on **3 of 67** runs, and **0 of 67** archived gate verdicts on *both* gates — so the quantity is corrected without restating any archived verdict, which is the founder's 2026‑11‑01 constraint. It is reached by both gate modes (`_check_gamma_alt_convergence` and `_check_hardened_convergence` both call `_settled_novelty_series`) and executed by 24 tests.

---

`falsifier`

```
python3 scripts/which_direction_does_dropping_confidence_flip_the_gate_2026-11-04.py
python3 scripts/is_a_refuted_falsifier_verdict_terminal_2026-11-04.py
python3 scripts/falsifier_the_critical_partition_counts_a_disproved_finding_2026-11-04.py
python3 -m pytest -q -p no:randomly bench/tests/test_the_critical_partition_enforces_the_key_property_2026-11-04.py bench/tests/test_the_severity_spec_annihilates_the_a4_severity_door_2026-10-28.py bench/tests/test_gamma_alt_convergence.py bench/tests/test_vacuous_gamma_curve.py bench/tests/test_a4_verifier_failsafe.py
```

---

`falsifier_result` — verbatim.

```
[A] KEY PROPERTY: a disproved finding is not a critical discovery
  _settled_novelty_series: REFUTED 0.9 -> crit_s                OK
  _corroborated_novelty_series: REFUTED 0.9 -> crit_s           OK
[B] V(None) must NOT de-escalate (the A4 fail-safe stays armed)
  _settled_novelty_series: unresolved 0.9 -> crit_s             OK
  _corroborated_novelty_series: unresolved 0.9 -> crit_s        OK
[C] a tool-CONFIRMED status outranks a stale REFUTED verdict field
  _settled_novelty_series: REFUTED verdict + CONFIRMED status   OK
  _corroborated_novelty_series: REFUTED verdict + CONFIRMED statusOK
[D] the check can FAIL: restore the pre-2026-11-04 raw read
  _settled_novelty_series                  raw read -> crit_s=[1]
  _corroborated_novelty_series             raw read -> crit_s=[1]
  defect reappears under the raw read                           OK
[E] no archived convergence verdict is restated by the repair
  replayed 67 distinct archived registries
  archived gate verdicts changed by the repair                  OK

defect NOT demonstrated: the critical partition enforces the section 7.7 key property at the 0.7 cut on both readers, V(None) still blocks, a tool-CONFIRMED status outranks a stale verdict, the check is capable of failing, and 0 of 67 archived verdicts move.
FALSIFIER EXIT=0
85 passed in 1.61s
```

**Including a failure, as required.** The falsifier fails iff the defect is present — run with `rr.spec_critical_severity` pre‑patched to the raw read:

```
AssertionError: defect present: _settled_novelty_series: REFUTED 0.9 -> crit_s: all_s=[1] crit_s=[1] (want all_s=[1], crit_s=[0]) -- a finding the harness disproved is counted as a critical discovery; _corroborated_novelty_series: REFUTED 0.9 -> crit_s: all_s=[1] crit_s=[1] ...
[A] KEY PROPERTY: a disproved finding is not a critical discovery
  _settled_novelty_series: REFUTED 0.9 -> crit_s                FALSIFIED
  _corroborated_novelty_series: REFUTED 0.9 -> crit_s           FALSIFIED
FALSIFIED
EXIT=1
```

**And a failure I caused and repaired rather than hid:** `test_the_severity_spec_annihilates_the_a4_severity_door_2026-10-28.py::test_the_convergence_critical_series_is_untouched_by_the_flag` → `assert 1 == 2 / where 1 = sum([0, 0, 1, 0])`. Repaired as described above; 5 passed after.

**Regression: 146 passed** (gamma/novelty/vacuous/hardened/A4 set), **91 passed** (severity set), **279 passed** (every test file touching the two readers), **42 passed** (appendix). **One pre‑existing failure I did not cause and did not repair:** `test_source_text_and_neighbour_audit_2026-09-11.py::test_the_class_has_not_grown_silently` — 5 unpinned source‑text assertions, every one in a `*_2026-11-02.py` file (other seats' work); my files appear 0 times in its output, and my new test file contains no source‑text assertion. Not a git checkout, so I cannot diff to prove pre‑existence — that is an inference, not a measurement.

---

`refuted_to_confirmed_count` — **0 recorded in the archive; the transition is REACHABLE and I executed it.** Three ways:

- **Archive:** `falsifier_verdict == "REFUTED"` on **32** of 3,170 entries; **2** have non‑terminal status (re‑servable); **4** are asserted‑critical, **2** of those non‑terminal. `status_log` hops **from** REFUTED: **63**, and all 63 are `REFUTED → REFUTED` (idempotent re‑records). **`REFUTED → CONFIRMED`: 0.**
- **Code:** `record_in_round_falsifier_reattachments` and `_post_convergence_sweep` both skip on `status ∈ {MERGED, CLOSED, REFUTED, DUPLICATE}` and **never** on `falsifier_verdict`. So a REFUTED verdict on a live entry is re‑served.
- **Executed:** calling the **real** `record_in_round_falsifier_reattachments` on an entry pre‑stamped `falsifier_verdict="REFUTED"`, `status="OPEN"`, with a demonstrating falsifier → `executed=1 cleared=1`, verdict **REFUTED → CONFIRMED**. With `status="REFUTED"` → `skipped_terminal=1`, verdict unchanged.

**My round‑1 debt is discharged, and the answer changed the fix.** REFUTED is terminal only through `status`, never through `falsifier_verdict`, so a fix that **stamped** zero onto the entry would permanently delete a finding the harness later proves real. `spec_critical_severity` **recomputes from the current field on every read** and stamps nothing — pinned by `test_the_annihilation_is_recomputed_not_stamped` and `test_the_live_reattachment_path_moves_refuted_to_confirmed`, which executes the transition and shows the critical count return to `[1]`.

---

`disagreement` — strongest first.

1. **The brief mandated a measurement on a gate that a default‑config live run does not reach.** Section 2 requires "the REAL `_check_gamma_alt_convergence`". `HARDENED_GATE_DEFAULT = True`, and at line 20959 the hardened branch *bypasses legacy γ‑alt entirely* — its own comment says "Legacy γ-alt is bypassed entirely." Had I obeyed the brief and stopped, I would have handed the founder a figure about a gate his runs skip. The result happens to survive on the live gate because both read `_settled_novelty_series` (4 F→T, 8 T→F, 0 under the fix), but that is luck, not the brief's design. **A brief that names the artefact by path should name the gate by reachability.**
2. **"Establish which, by execution, on the SAME archive and the SAME gate" framed this as an either/or and it was never one.** The two substitutions are different functions with different monotonicity; the sign of the flip is a property of the function, derivable before any replay (z3 settles both in one call each). The brief's framing invited a tie‑break where the honest answer is a *union*, and the union is what matters: the dangerous direction is present under **both** candidate replacements, not just mine.
3. **The brief declared item 2 "answerable by reading it" and it is — but the answer is that both quoted clauses are off‑target.** By asking each seat to defend its own clause, the brief made a scope error on *both* sides look like a disagreement about *one* document. The real question is whether `d_tool` generalises beyond `d`, and no amount of re‑reading lines 773 or 600 decides it, because neither mentions severity.
4. **Pre‑declaring `S_k`, `sigma` and `nu` "settled between you and need no further work" is the brief exercising the authority it tells the seats not to exercise.** Two seats agreeing is model agreement, which this project's own founding principle says does not confirm anything. They are almost certainly fine — I re‑checked that `nu`'s all‑severity channel is untouched, 0 of 67 — but "both seats said so" is the exact warrant CDSFL rejects.

---

`passes_run` — **4.**

**P1** mapped the real path: both novelty readers, the two‑sided gate, the vacuous‑curve branch, and the write sites for `falsifier_verdict`. **P2** measured: the two‑sign table, the identity of `fable`'s two forms (0 of 3,170), the 46‑verdict‑bearing scope artefact, the four derivations (z3 ×3, SymPy, Wolfram second falsifier on one). **P3** implemented and found two above‑threshold items the implementation surfaced — the A4 variant does not close the manufactured direction, and the hardened gate is the live one. **P4** regression, the REFUTED‑terminality measurement, the corrected 2026‑10‑28 assertion, the appendix. P4 produced no new above‑threshold finding, so I stop.

**Residual falsification debt, stated rather than hidden.** (a) `W` and `confidence` are still uncollected, so the asserted float still stands in for `W·confidence` wherever the key property does not fire; the full §7.7 product remains uncomputable and I did not add the HARD/SOFT field — §7.7 caution 2 shows its default must be **SOFT**, inverting `cdsfl_core.txt` §1, and that needs a writer, a reader and a collection default I have not measured. (b) The *other* severity consumers — `blocking_entry_ids` / `unverified_critical_count`, `open_crit_high_count`, `contested_count` — still read the raw float; I deliberately left them, because `test_the_withdrawn_repair_would_have_been_unreachable` measures a V=0‑only repair as reaching **nothing** at the A4 door (`refuted_proven == 0`), and loosening a blocker count is the releasing direction. That withdrawal was correct for the door and does **not** transfer to the partition, where the same form reaches 32 entries and 3 runs. (c) All 67 replays are final‑state; a live run varying `unresolved_critical` mid‑run could flip where a replay does not.

---

## What would refute me

- **The flip resolution falls if** the two seats' round‑1 replays differed in a third way I did not control — a different `RunnerConfig` (`gamma_alt_threshold` 0.41 here), a different `max_round`, or a different `novel_critical_history` construction. Named property: **`fable`'s 12 T→F run names**. I reproduce 12 under forced‑A4 and 8 under live‑A4; if `fable`'s 12 are not the same 12 runs I list, the substitutions are not the only difference and the resolution is incomplete.
- **The clause reading falls if** a clause I did not find generalises `d_tool`. Named property: **any sentence in `cdsfl_operational.md` or `cdsfl_core.txt` binding self‑assessed confidence to a quantity other than `d`.** I grepped: `confidence` appears at exactly 2 lines, 603 and 773, and `Sev(` appears 0 times. A third site anywhere in the binding directive set refutes me.
- **The fix is worse than the raw read if** `status == "CONFIRMED"` is *not* reliably tool‑owned — if some path writes CONFIRMED status from model prose, the carve‑out admits a vote. I read the substitution record (`refused_transitions`: "CONFIRMED is TOOL-ONLY") but I did **not** enumerate every writer of `registry.resolve(cid, "CONFIRMED")`. Named property: **count of CONFIRMED status writes whose adjudicator is not `tool`.** This is the weakest joint in this answer.
- **The whole repair is wrong rather than right if** the founder rules that a REFUTED critical must keep blocking — the Exp 42 measurement `fable` cites (2 of 3 REFUTED criticals were themselves falsely REFUTED) is live evidence for that, and it is already the ruling at the *retirement* path (2026‑08‑03: a critical is never retired by a refutation). If that ruling extends to the *counting* path, then §7.7's key property must not bind the partition either, and the appendix — not the runner — is what needs changing.
- **0 of 67 is weaker than it reads.** It is a statement about an archive in which the repair changes 32 entries and no verdict. Wilson's upper bound is 5.42%: up to roughly 1 run in 18 could flip on a corpus this size and still be consistent with what I measured.

Written under CDSFL note standard v1.9. Wolfram ran once, as second falsifier on one already‑obtained result (`Reduce` → `False`), attributed to Wolfram Language, local Wolfram Engine; all primary verification is z3 / SymPy / statsmodels.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 49 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_severity_spec_is_uncomputable_2026-11-04) -->

All measurements complete, fixes in the tree, falsifiers executed, regression green. Final report.

---

## `verdict`

**Both of the brief's "contradictions" dissolve under measurement and reading — and one of my own round-1 claims falls with them.** Item 1: the two flip results are compatible facts about two different substitutions, reproduced side by side on the same 67 distinct registries through the real `_check_gamma_alt_convergence`; but my round-1 "every one True to False" was an artefact of my run cut — my substitution ALSO manufactures the same 11 convergences cc2's does, plus 15 blocked. Item 2: cc2 is right on the letter; my §15 citation broadened "the detection probability d" into "quantities", and that broadening was mine, not the document's. Artefacts reviewed: `bench/reference_runner_v3.py`, `bench/directives/universal/cdsfl_operational.md` (lines 600–606, 763–775), `docs/MATHEMATICAL_APPENDIX.md` §7.7/§7.10/§15-adjacent.

## `moved`

**Moved, with the evidence that moved me:**
1. **My directional claim on item 1.** Executed on the same archive and gate: `compute_sev_f`/`W·V` flips **26 of 67** — **11 False→True** (identical run list to cc2's eleven, all via the vacuous-curve branch) **plus 15 True→False**. My round-1 "12 of 46 verdict-bearing, all True→False" was true of the cut I took: the 11 manufactured flips all occur in runs carrying **no falsifier verdicts at all** (every entry gets V=0.5, the critical series zeroes, the vacuous branch opens), and "verdict-bearing" excluded exactly those runs. cc2's result stands whole; mine was half of a larger, worse result.
2. **My fix.** `W(class)·V` is **refuted by measurement** as the partition definition — it contains cc2's failure mode as a strict superset. I adopt the restricted annihilator.
3. **My §15 reading** (detail under `clause_reading`).

**Did not move:** the NOT_AS_SPECIFIED verdict on §7.7's computability; 0-of-3,170 `confidence` collection; the dedup correction (settled); the key property's scope — discovery counting, never blockers — which now rests on Exp 42's falsely-REFUTED measurement *embedded in the fix's design* rather than on my round-1 prose.

## `flip_direction`

**Resolved, not irreducible.** Producer: `scripts/both_severity_substitutions_one_archive_one_gate_2026-11-04.py` — 77 files, 67 distinct by content hash, 3,170 entries, real gate, real readers, severity varied only on deep copies. Protocol A = both seats' round-1 inputs (unresolved=0, contested=0); Protocol B = faithful, with `unverified_critical_count()`/`contested_count()` recomputed from the real `FindingRegistry` (both are status-only, hence severity-invariant — cc2's "live run could flip where my replay does not" worry is discharged *for these two inputs* by construction):

| definition | partition moves (entries) | A: flips | A: F→T / T→F | B: flips | B: F→T / T→F |
|---|---|---|---|---|---|
| `asserted·V` (cc2's substitution) | 818 | **11** | 11 / 0 (all vacuous) | 3 | 3 / 0 |
| `compute_sev_f` = `W·V` (mine; identical on archive, confidence divergence = 0) | 1,378 | **26** | 11 / 15 | 14 | 3 / 11 |
| restricted annihilator (cc2's fix) | **4** | **0** | 0 / 0 | **0** | 0 / 0 |

So "drop `confidence`" is not 2 options with opposite failure modes — it is 2 options of which **one has both failure modes and the other has one**. The founder's choice is not between them: the restricted form flips 0 of 67 (Wilson upper bound 5.4226%). Mechanism, derived (settled round 1, re-confirmed): severity ∈ [0,1] ⇒ `sev/2 ≥ 0.7` unsatisfiable; and the defaulted `W=1.0, c=1.0` promotes every CONFIRMED sub-critical to 1.0, which is the True→False half. 11/67 = 16.4179%, Wilson [9.4226%, 27.0553%] — statsmodels, endpoints confirmed with **Wolfram Language (local Wolfram Engine, via wolframscript)**: {0.164179, 0.0942261, 0.270553}.

## `clause_reading`

**`bench/directives/universal/cdsfl_operational.md:600–606** (§15, d_tool):

> **d_tool — detection probability grounded in tool output.**
> The detection probability d entering q = η · d · p must come from actual
> tool execution (static analysis, test runner, SymPy verification, AST
> parse), not from self-assessed confidence. A claim of d = 0.9 based on
> "I am certain" is not admissible. d = 0.9 derived from "9 of 10 relevant
> tests caught the flaw class" is admissible. Formally: d_i = f(T_i) where
> T_i is the result of executing a defined verification tool.

**Lines 763–775** (Action precedence, item 1, REFUTED by tool), the operative sentence at 773–775:

> Self-reported confidence is not accepted. Assertions that "my
> reasoning is sound" without tool receipts are inadmissible under this
> directive.

**My reading.** The two clauses ARE independent prohibitions — cc2's round-1 statement that the prohibition "sits under action precedence" is true of line 773 and not of line 600; §15 admissibility gates findings at entry, action precedence governs rebuttals in feedback. **But d_tool's letter is scoped to d**: "the detection probability d entering q = η · d · p", and the §15 preamble (line 578) scopes all five constraints to "a finding or parameter update" entering *the R_k update*. Severity is not d and Sev(f) is not a factor of q. These are the only 2 occurrences of "confidence" in the entire directive (grep, 2 hits, both quoted above). **So: §15 d_tool does NOT, by its letter, forbid `confidence` as an input to a harness-computed quantity in general; it forbids it as the source of d specifically, and line 773 forbids it as a rebuttal.** B87's letter-level conflict dissolves — cc2's conclusion, reached by cc2's reading, and I concede it by reading rather than split any difference. What remains for the founder is one precisely-nameable unlegislated case: *model self-assessed confidence as an input to a harness-computed severity that reaches a convergence gate*. §7.7 includes it; d_tool's **rationale** (a self-assessment must not source a convergence-deciding number) extends to it only by analogy, and an analogy is not a directive. Reading R1 (silence = permitted; documents agree) is what the text supports. Reading R2 (d_tool states a principle instanced at d) is a design judgement the founder may adopt — but nothing in the text compels it, and my round-1 answer erred by presenting R2 as the text.

## `fix`

cc2's restricted annihilator and my `W(class)·V` are **not the same fix**, and the annihilator **dominates on two named, measured properties**: manufactured convergences (0 vs 11) and archived-verdict invariance (0 vs 26 flips; partition moves 4 vs 1,378). No composition — composing W into the annihilator would import the promotion failure mode, and the single fix performs strictly better alone. Adopted and **extended to a third gating reader neither round-1 seat nor the brief named**: `_location_keyed_critical_series` (line ~11295), which GATES whenever `location_keyed_convergence` is set — 16 configs — and carried the identical raw read, plus a location-inoculation hazard (a refuted claim's location permanently suppressing later genuine criticals there). Blockers stay un-annihilated by design (Exp 42: 2 of 3 REFUTED criticals falsely refuted; annihilating a blocker releases).

- `bench/reference_runner_v3.py` — new `spec_critical_severity()` (identifier follows cc2's round-1 fix rather than coining a second name); `_settled_novelty_series`, `_corroborated_novelty_series`, `_location_keyed_critical_series` rewired to it.
- `bench/tests/test_spec_critical_severity_three_readers_2026-11-04.py` — 14 executing tests, incl. verdict-reversal self-healing, no-inoculation, no-promotion, and 67-registry replay invariance.
- `scripts/both_severity_substitutions_one_archive_one_gate_2026-11-04.py` — the item-1 instrument.
- `scripts/falsifier_disproved_findings_count_as_critical_discoveries_2026-11-04.py` — the falsifier.
- `bench/tests/test_the_severity_spec_annihilates_the_a4_severity_door_2026-10-28.py` — **one pre-existing test updated, reported not silent**: its secondary assertion `sum(crit_on) == 2` pinned the verdict-REFUTED 0.9 *as a critical discovery* — the key-property violation itself, pinned incidentally. Its actual property under test (flag-invariance of the series) passes unchanged; the pinned count now asserts the repaired semantics and additionally executes the un-annihilation case.
- `docs/MATHEMATICAL_APPENDIX.md` — §7.7 caution 3 (the three-way measurement, Wolfram-attributed endpoints); §7.10 Sev(f) row notes the key property — and only it — is now enforced in the gating path.

## `falsifier`

```
python3 scripts/both_severity_substitutions_one_archive_one_gate_2026-11-04.py
python3 scripts/falsifier_disproved_findings_count_as_critical_discoveries_2026-11-04.py
python3 -m pytest bench/tests/test_spec_critical_severity_three_readers_2026-11-04.py -q
```

## `falsifier_result`

```
[scope] 77 runner_state.json files, 67 distinct by content hash, 10 duplicate copies skipped
[conf]  entries where W*V != compute_sev_f (live confidence): 0
[pop]   verdict-REFUTED, status non-terminal, raw sev>=0.7 (the population any annihilator can move): 1
== cc2_full ==        protocol A: 11 gate flips (False->True 11, True->False 0, via vacuous branch 11)
== fable_WV ==        protocol A: 26 gate flips (False->True 11, True->False 15, via vacuous branch 15)
== cc2_restricted ==  protocol A: 0 gate flips   protocol B: 0 gate flips

defect NOT demonstrated: all three partition readers satisfy the key property and
do not de-escalate unresolved criticals. EXIT=0
14 passed in 0.90s
```

Fails iff the defect is present — executed with the raw read restored in-memory: `FALSIFIED` + `AssertionError: defect present: _settled_novelty_series: REFUTED 0.9 -> crit_s [0, 1, 0, 0]; _corroborated_novelty_series ...; _location_keyed_critical_series ...`. Regression: **491 passed** across the 23 test files pinning the three readers, both gates, the vacuous branch, A4, location keying, rho, severity calibration and the appendix properties.

## `refuted_to_confirmed_count`

Not mine per the brief — cc2 reports it. But adopting cc2's fix makes its weakest joint mine too, so I measured it rather than inherit it on trust: **0** `status_log` transitions out of REFUTED to any other state across 67 distinct registries (63 transitions carry from=REFUTED, every one REFUTED→REFUTED re-stamps); **2** entries archive-wide ever status-REFUTED now carry verdict CONFIRMED (`commissioning_arm1_panel_20260929T194414Z/C0036`, `free_run2…/C0016`), both in status-terminal entries the status filter excludes before severity is ever read. And the fix reads the **live** `falsifier_verdict` field, so annihilation self-heals on reversal — executed in `test_refuted_to_confirmed_reversal_restores_the_count`. cc2's "if non-zero, the fix must read the latest verdict": it reads the latest by construction.

## `disagreement`

The brief's safety-asymmetry sentence — "manufacturing a convergence releases defects, while preventing one only costs rounds" — frames item 1 as two options carrying one failure mode each, and invites the founder to weigh them against each other. **Measured, the weighing never arises: one option's failure set strictly contains the other's** (the same 11 manufactured convergences appear in both, on the identical run list). Secondary: both round-1 flip denominators the brief reproduces (11 of 78, 12 of 46) are run-selection artefacts — same-archive figures are 11/67 and 26/67, and the faithful protocol B drops them to 3 and 14, so the brief circulated protocol-dependent magnitudes as results; the directions survive, the numbers did not. And the brief's implied fix scope (two partition readers) was incomplete: `_location_keyed_critical_series` gates on 16 configs and carried the same raw read.

## `passes_run`

**4.** P1 mapped the gate, the three readers (finding the third), and the two directive clauses. P2 measured: both substitutions × two protocols on 67 registries, confidence divergence (0), the annihilator population (1 entry), REFUTED transitions. P3 implemented, falsified bidirectionally, regressed — surfacing one stale pinned assertion (above-threshold: it pinned the defect as expected behaviour), which justified P4. P4: appendix record, Wolfram second-falsifier on the Wilson endpoints, and a sweep of every remaining raw severity read (all are blockers, routing, alarms or telemetry — protective or non-gating, correctly untouched). P4 produced no new above-threshold finding. Converged; no residual falsification debt on the claims above, with one stated limit under refutation below.

## What would refute me

- **The 0-of-67 invariance claim** replays the settled-series gate; the 16 `location_keyed_convergence` runs gated live through the location series, whose archived counts are embedded in `novel_critical_history`. An end-to-end location-keyed replay showing a verdict move under the third-reader rewire would overturn "no archived verdict is restated." The touched population is 1 entry archive-wide, but that is an archive fact, not a theorem.
- **A verdict-level REFUTED→CONFIRMED record outside `runner_state.json`** (round logs) on a non-terminal entry would weaken the evidential base of the self-healing argument — though not its mechanism, which is executed.
- **A founder ruling that V(None)=0.5 is intended at the partition** would convert the 11 manufactured convergences from defect to specification, and the fix's refusal to de-escalate would then be the defect.
- **On item 2:** any future clause — or an existing one under vocabulary other than "confidence"/"self-assessed", which my 2-hit grep cannot exclude — generalising d_tool beyond d would restore my round-1 reading and make the §7.7 confidence factor a genuine directive violation.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_severity_spec_is_uncomputable_2026-11-04/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
