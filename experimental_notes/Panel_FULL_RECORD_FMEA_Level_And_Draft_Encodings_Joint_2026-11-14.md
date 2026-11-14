# Joint round: the level stays at 7, and a declared clinical scale had been superseded for 16 months

Record written 2026-11-14T05:20:25+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

The JOINT half of the encoding round. Each seat saw the other's actual words, including the arithmetic error in the brief, and was asked to resolve the disagreement by measurement rather than by concession.

WHAT IT RESOLVED. The failure-mode critical level stays at 7. Agreement survived both seats seeing the other's reasoning, and the reasons are independent of each other: the published standard's own 2 landmark bands put 7 at loss of primary function and 9 at a safety or regulatory consequence, so a move to 9 would place the case where the artefact does not work outside the critical class; 4 of the project's own 5 material categories would fall below the cut; and engineering would become the only declared scale gating at its standard's maximal band. The founder's 4th candidate standard, real-world applicability with a human-consequence caveat, points the same way, because a repair that does not work has a consequence for the person who has to deal with it.

WHAT THE BRIEF GOT WRONG, AND BOTH SEATS CAUGHT IT. The joint brief asked each seat to justify the 5 encodings it classified differently from the other. 5 is the absolute difference of the 2 counts, 16 and 11, and the symmetric difference of 2 sets is not the difference of their sizes. The real disagreement spans 11 encodings. Both seats named the error independently, which is the clearest evidence in the round that the joint half is not ceremonial.

THE DECISION THAT DID NOT CONVERGE IS RECORDED AS NOT CONVERGED. 11 encodings against 16 is a gap of 5 in the conservative direction, and nothing was promoted on either count. The 2 criteria differ in kind rather than in strictness: 1 seat requires a second independent verification route, the other requires only that the declared figures reproduce. That difference is information and is preserved rather than averaged.

AND A DEFECT NEITHER THE BRIEF NOR THE PROJECT HAD NOTICED. The clinical severity scale declared in the domain manifest had been superseded roughly 16 months before a note in the same file asserted it was confirmed current. Verified against the primary 312-page publication and corrected, together with a stale printing citation on the failure-mode handbook. Entries B154 and B185 record the outcomes.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

*4 nested verbatim marker(s) in this brief were made inert by the record generator, so this region stays well formed. Only the HTML-comment delimiter changed; no word of the brief or of any quoted reply was altered.*


# PANEL BRIEF — JOINT ROUND on `fmea_level_and_draft_encodings_2026-11-14`

This is the JOINT half of the blind round `fmea_level_and_draft_encodings_2026-11-14`. In the blind half each of the 2 seats answered WITHOUT seeing the others. Both replies are reproduced BELOW IN FULL, verbatim. Read the other seat's actual words before you answer.

**Disagreement is INFORMATION and is preserved. There is no compelled convergence: do NOT move toward the other seat to be agreeable. Change your position only where its EVIDENCE moves you, and say which evidence did. Where you still disagree, say so and say what would settle it.**


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `bench/cdsfl_registry/composer.py` | `eb836387286a87a3` | 117190 | 2026-11-13T21:27:13+00:00 |
| `bench/reference_runner_v3.py` | `9f689c6505d36c49` | 1280002 | 2026-11-13T21:28:38+00:00 |
| `bench/cdsfl_registry/registry.py` | `8d37e067ebdc0757` | 19691 | 2026-11-09T05:09:06+00:00 |
| `bench/cdsfl_registry/domain_vocabulary.py` | `f27c7b6cb0a63f56` | 21926 | 2026-11-12T21:03:50+00:00 |
| `bench/convergence_location.py` | `ea76b2852c07ee8d` | 65644 | 2026-09-01T12:24:12+00:00 |
| `bench/tests/test_the_domain_severity_reaches_the_prompt_2026-11-13.py` | `c8e3b4f0a7069046` | 5112 | 2026-11-13T21:28:00+00:00 |
| `bench/tests/test_the_cut_is_a_domain_property_2026-11-11.py` | `87cd7b882b5adb06` | 10118 | 2026-11-12T03:45:47+00:00 |
| `bench/tests/test_the_consequence_domain_is_resolved_2026-11-12.py` | `234bf2710b6f7c54` | 12970 | 2026-11-12T21:03:40+00:00 |
| `bench/directives/universal/cdsfl_core_formal.md` | `9da304edb6c80a60` | 31909 | 2026-11-12T03:58:04+00:00 |
| `bench/directives/physics/physics_general.txt` | `1891ab2a94cdc379` | 7571 | 2026-11-12T01:41:31+00:00 |
| `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md` | `14a5b7fa2949b134` | 3739 | 2026-07-28T12:27:32+00:00 |
| `bench/cdsfl_registry/domain_manifest.toml` | `d71c5d47ef9e3e67` | 26575 | 2026-11-14T02:45:27+00:00 |
| `bench/directives/statistics/statistics_inference.txt` | `ead4e211ef3660d6` | 6946 | 2026-11-12T01:44:46+00:00 |

## THE PROJECT, ITS AIMS, AND ITS SPECIFICATIONS — read before answering

CDSFL is a falsification harness. Its aim is the democratisation of science for every kind of intelligence, so a mechanism that only works on code, or only on this machine, is a mechanism that misses the point. The 3 formal standards below are exacting and are not loose English.

1. **ADDITIVE** — work adds to reliability, functionality, accuracy, robustness and the project's stated aims. A feature is never disabled or removed; removal only where a COMMITTED MEASUREMENT shows the replacement dominates on a NAMED property. Symmetrically, an addition nothing reaches is not additive either: every new flag, gate or entry point must be wired to a caller and executed by a test.
2. **SIMPLEST SUFFICIENT** — the smallest change addressing the ROOT CAUSE and the downstream consequences traced before the fix.
3. **COMPOSABILITY** — the founder, verbatim, 2026-10-02: "Composability doesn't mean composing two solutions just because they can be composed. It means this principle should be applied where two composed solutions demonstrably provide a better, more robust and/or more efficient solution than either fix in isolation. Where a single fix out performs a composed one, that fix should continue to be preferred. In all cases any fix should also take the first two conditions fully into consideration also." So a composed fix needs a MEASUREMENT showing it dominates either part alone. "They do not conflict" is the weak sense his wording excludes.

Work under `a` (analyse dispassionately), `f` (FFAFP: Find, Follow, Analyse with tools, Fix, P-pass) and `sy` (use the STEM tools; every computational claim cross-verified by 2 independent tools; every proportion carries a confidence interval). The tool output IS the evidence. **Findings are confirmed programmatically or by the founder — there is no model voting.**

## REQUIRED SECTION 1 — The question

**The blind half asked 2 things: where the engineering domain's FMEA critical level should sit when the published standard names 2 landmark bands, and which of the 22 DRAFT encodings may move to CROSS_VERIFIED. You each answered without seeing the other. Both replies landed.**

**YOU AGREED ON Q1 AND DISAGREED ON Q2, AND THE DISAGREEMENT IS A NUMBER: 11 against 16.**

**J1. Q2, SETTLED BY ADJUDICATION AND NOT BY SPLITTING THE DIFFERENCE.** One of you recommends 11 of 22 move to CROSS_VERIFIED, the other 16 of 22. Go encoding by encoding over the 5 you classify differently and say, for each, which verdict is right and on what evidence. A midpoint is not an answer. Where you cannot settle one, name the single check that would.

**J2. Q1, RE-EXAMINED RATHER THAN CONFIRMED.** You both recommend RETAINING 7 and both derived a decision procedure. Say whether your agreement SURVIVES seeing the other's procedure — 2 seats reaching 1 answer by 1 flawed route is not corroboration, and there are no votes in CDSFL. In particular: one procedure keys the cut to the consuming project's own material-defect categories, the other to whether a band's published definition ENTAILS the project's pre-registered materiality definition. State whether those are the same rule in different words or 2 rules that can disagree, and construct a standard on which they WOULD disagree.

**J3. THE CTCAE FINDING IS CONFIRMED AND IT CHANGES THE GROUND UNDER Q2.** The `fable` seat found that CTCAE v5.0 is superseded. That has now been verified against the PRIMARY document, not taken from the reply: **CTCAE v6.0 (MedDRA 28.0), published 2025-07-22**, 312 pages, with implementation for trials planned 2026-01-01. The grade ladder is UNCHANGED — v6.0 defines Grade 3 verbatim as *"Severe or medically significant but not immediately life-threatening; hospitalization or prolongation of hospitalization indicated; disabling; limiting self-care ADL"* — so only the version NAME was stale and `critical_level = "Grade 3"` stands. The manifest has been corrected to v6.0 with the primary citation. **NOW ANSWER THIS: the manifest's previous note said CTCAE was "CONFIRMED 2026-11-12 against the NCI source rather than recalled", and that confirmation was WRONG BY ABOUT 16 MONTHS. How many of the OTHER declared scales carry a confirmation of the same kind, and what is the chance each is also stale? Check them against primary sources and report per scale. A confirmation is only as current as the day it was made and nothing re-checks it.**

**AND 1 FACT NEITHER OF YOU HAD, WHICH BEARS DIRECTLY ON Q2.** `encoding_tier` is consumed by **0 decisions anywhere in the tree**. Verified by AST over `bench/cdsfl_registry/composer.py`, `bench/reference_runner_v3.py`, `bench/cdsfl_registry/registry.py` and `bench/cdsfl_registry/domain_vocabulary.py`: 0 references in the first 3, and the 4 in `domain_vocabulary.py` are a VALIDATION that the field is one of the 4 declared tiers plus a `print` in that module's own `main()`. So a promotion from DRAFT to CROSS_VERIFIED changes a validated string and a printed line and nothing else. Say what that does to your Q2 recommendation, and whether the adjudication should be RECORDED somewhere a consumer will read before any tier is written.

## REQUIRED SECTION 2 — Use the harness

Read and RUN the code. Do not reason from the brief alone. Do not invoke pytest across the whole tree: the heavy-process budget on this machine is 1, and a full board is already cached. Targeted test files are fine.

## REQUIRED SECTION 3 — Produce a fix, and test it

Where you find a defect, deliver the fix and the executed evidence that it works, including what you tried that did NOT work. **WRITE YOUR FIX INTO THE SANDBOX REPOSITORY TREE AT ITS REAL PATH.** A fix left in prose, or written to scratch space, is destroyed when the sandbox is torn down and has not been delivered. Supply a runnable falsifier, EXECUTE it, and quote its output.

## REQUIRED SECTION 4 — What would refute you

State, for each position you hold, the observation that would overturn it. A position with no falsifier is not a finding.

## REQUIRED SECTION 5 — Output shape

`verdict`, `composability`, `reasoning`, `falsifier`, `falsifier_result`, `strongest_disagreement`, `aims_check`. In `strongest_disagreement` name the specific claim of the OTHER SEAT you reject, and why, with evidence.

## REQUIRED SECTION 6 — Termination

Stop when a pass produces no new above-threshold finding. State how many passes you ran.

---

# THE BLIND HALF — all 2 replies, verbatim and in full

## SEAT `cc2` — its blind reply, verbatim

[verbatim-begin -->

Manifest, runner and composer digests are unchanged from dispatch — I touched none of them.

---

## `verdict`

| Q | verdict | reason |
|---|---|---|
| **Q1** | **RECOMMEND RETAIN 7** — the mechanism is applicable and delivered; the level itself needs no ruling because retaining changes nothing. **HOLD FOR THE FOUNDER** on any move to 9. | A cut at 9 would demote 4 of the project's own 5 §10 material categories below critical, and would make engineering the only declared scale whose critical level is the maximal band. |
| **Q2** | **RECOMMEND CROSS_VERIFIED for 11 of 22; the other 11 stay DRAFT.** Tier promotions **not applied** to the manifest. | The tier gates nothing at dispatch (`encoding_tier`: 0 occurrences in composer and runner), so writing promotions now would be an addition nothing reaches. |

## `q1_procedure`

Given a standard naming landmarks B₁ ≺ … ≺ Bₘ:

1. **Enumerate every landmark the standard labels**; record all of them in `severity_levels`. Do not collapse two into one.
2. **Reject Bₘ as a candidate cut** unless the standard says only the top band carries consequence. At the maximum, `c_d(f) ≽_d θ_d` is equivalent to `c_d(f) = max` — an identity test, not an ordinal threshold.
3. **Map the *consuming project's* own material-defect categories onto the bands. The cut is the lowest band at least one material category reaches.** This is the operative step: it makes the cut a property of the consumer's materiality definition, not of the standard's vocabulary.
4. **Check the rank from the top against the project's other declared scales.** Outside the observed range is not disqualifying but must be justified in the note.
5. **Where 3 and 4 disagree, resolve toward the tighter cut** and record the disagreement — ambiguity is HARD by §1.
6. **Record which landmark was not chosen, and why.** Both landmarks keep reaching a seat on the `LEVELS:` line regardless.

Applied here step 3 yields **7** and step 4 agrees. Run against the other three declared scales the procedure reproduces CVSS → High (7.0) and CTCAE → Grade 3, i.e. every existing declaration. That is the evidence it generalises.

**Step 3 is the decisive ground and it is argued, not measured** — written out in full in the script's M6 so it can be disputed. §10 names five material categories; only *hard-constraint violation*, and only its law/safety sub-case, reaches FMEA's 9-10 SAFETY OR REGULATORY band. Wrong result, verification-integrity corruption, silent evidence loss and unreproducibility all sit in 7-8 HIGH.

**The third option — declare both landmarks — is REJECTED on measurement.** `severity()` returns exactly one `critical_level` key; `_severity_declaration` emits exactly one `CRITICAL LEVEL:` line; two product modules reference `critical_level`. Nothing can consume a second cut. And it is unnecessary: **both landmarks already reach the seat**, on the delivered `LEVELS:` line. A second field would add a second *cut*, not a second *landmark*.

## `q1_consequence` (measured)

- `CRITICAL_SEVERITY_THRESHOLD = 0.7` (**float**); `critical_level = '7'` (**str**, a rank on an external ordinal scale). Mutating the manifest 7→9 on a copy: declaration text changed `True`, runner threshold **unchanged at 0.7**. Two distinct quantities.
- `convergence_location.py`: `critical_level` **0** occurrences, `severity_scale` **0**. All three novelty series take a float `critical_threshold` (default 0.7) and have **no `domain` parameter**. The named level does not enter convergence.
- What a move changes is **one line in a seat's composed directive**. Q1 is a reporting question, and that bounds its consequence.
- Rank from top of each declared critical level: software (CVSS v4.0/High) **2**, chemistry (GHS Rev. 11/Category 2) **2**, biology (CTCAE v5.0/Grade 3) **3**, engineering@7 **2**. Engineering@9 → **1**, outside the observed range [2,3] and the only maximal-band cut.

## `q2_table` — 22 of 22 examined

Tool-checkable = reduces to a determinate computation, a closed named vocabulary, or a stated numeric bound. Edition column is **post-repair**.

| domain / file | cited standard | current? | HARD tool-checkable | verdict | evidence |
|---|---|---|---|---|---|
| biology_genetics | CTCAE v5.0 (2017) | yes | 4/7 | **CROSS_VERIFIED** | confirmed current 2026-11-12 |
| biology_natural_world | CTCAE v5.0, 2017-11-27 | yes | 3/7 | DRAFT | below majority tool-checkable |
| biology_zoology | CTCAE v5.0 (human half only) | partial | 1/7 | DRAFT | animal-welfare scale `[VERIFY:current]`, none confirmed |
| chemistry_general | GHS Rev. 10 primary; Rev. 11 secondary | **no** | 7/8 | DRAFT | Rev. 11 currency is secondary-sourced |
| cross_general | none (founder's rule) | n/a | 2/6 | DRAFT | cites no external standard |
| is_data_management | FAIR 2016; ISO 11179 | **no** | 6/7 | DRAFT | ISO unversioned, `[VERIFY:current]` |
| is_general | CVSS v4.0; ISO 11179 | mixed | 7/7 | DRAFT | ISO citation `[VERIFY:current]` |
| is_knowledge_representation | ISO 11179; Dublin Core | **no** | 6/7 | DRAFT | both unversioned |
| is_retrieval | ASA 2016 | yes | 5/7 | **CROSS_VERIFIED** | dated doc, no edition exists; scale honestly none |
| logistics_warehousing | "None confirmed primary" | n/a | 6/6 | DRAFT | `[VERIFY:current]`, honest absence |
| mathematics_applied | FMEA 2019 handbook; CTCAE v5.0; SI 9th ed | yes | 5/7 | **CROSS_VERIFIED** | editions added this round |
| mathematics_numerical | IEEE 754-2019; ISO/IEC 60559:2020 | yes | 7/7 | **CROSS_VERIFIED** | figures verified against the running implementation |
| mathematics_proof | none, with stated reason | n/a | 5/8 | **CROSS_VERIFIED** | honest none + majority checkable |
| physics_classical | FMEA 2019 handbook; SI 9th ed 2019 | yes | 6/7 | **CROSS_VERIFIED** | edition added this round |
| physics_general | SI 9th ed 2019; INES unversioned | partial | 6/6 | **CROSS_VERIFIED** | INES is an inheritance example, not the declared scale — see residual |
| physics_quantum | SI 9th ed 2019 | yes | 5/7 | **CROSS_VERIFIED** | ħ exact by definition |
| physics_thermodynamics | GHS Rev. 11; SI 9th ed | **no** | 6/6 | DRAFT | inherits chemistry's Rev. 11 currency defect |
| software_general | CVSS v4.0, FIRST, Nov 2023, Table 22 | yes | 8/8 | **CROSS_VERIFIED** | strongest of the 22 |
| statistics_experimental_design | CONSORT/PRISMA unversioned | **no** | 4/7 | DRAFT | "cited without a version", `[VERIFY:current]` |
| statistics_general | ISO 3534; Stevens | **no** | 6/6 | DRAFT | ISO no edition |
| statistics_inference | ASA 2016, "not formally superseded" | yes | 4/7 | **CROSS_VERIFIED** | supersession reasoned, not assumed |
| statistics_time_series | ASA 2016 | yes | 6/7 | **CROSS_VERIFIED** | |

11/22 = 50.0000%, Wilson [30.7221%, 69.2779%]. Tool-checkable overall 115/152 = 75.6579%, Wilson [68.2581%, 81.7928%].

## `q2_coverage`

**22 of 22 examined. None left.** The 29 encodings without a `SEVERITY SCALE:` line were not adjudicated — they are out of Q2's scope (22 of 51 carry one = 43.1373%, Wilson [30.5012%, 56.7347%]).

## `tier_mechanism`

**The tier gates nothing at dispatch.**

```
composer.py              'encoding_tier'=0  'CROSS_VERIFIED'=0  'DRAFT'=0
reference_runner_v3.py   'encoding_tier'=0  'CROSS_VERIFIED'=0  'DRAFT'=1
with EVERY tier flipped DRAFT -> CROSS_VERIFIED on a copy:
    composed declaration byte-identical= True
```

It is validated for membership in `tiers` by `domain_vocabulary.load()` (fails closed) and printed by that module's CLI. Nothing else reads it. So I did **not** write the promotions into the manifest — that would be an addition nothing reaches, the failure class this project has shipped 11 times since 2026-08-01.

## `falsifier`

Three files, all in the repository tree:

- `scripts/where_does_a_critical_level_land_2026-11-14.py` — M1–M6. Points the vocabulary reader at a **copy** under tmp; never writes the artefact.
- `bench/tests/test_the_severity_declaration_is_complete_2026-11-14.py` — the fix, 6 tests, two of which exist only to prove the guards are not vacuous.
- `experimental_notes/Panel_Severity_Critical_Level_And_Draft_Adjudication_2026-11-14.md` — the record.

## `falsifier_result`

```
$ python3 -m pytest bench/tests/test_the_severity_declaration_is_complete_2026-11-14.py -q
......                                                                   [100%]
6 passed in 0.41s

$ python3 -m pytest bench/tests/test_the_domain_severity_reaches_the_prompt_2026-11-13.py \
    bench/tests/test_the_cut_is_a_domain_property_2026-11-11.py \
    bench/tests/test_the_consequence_domain_is_resolved_2026-11-12.py -q
......................................                                   [100%]
38 passed in 4.67s
```

The guard fires on the as-dispatched text and is silent after repair:

```
OFFENDERS IN THE AS-DISPATCHED TEXT OF THOSE 7 FILES: 11
   chemistry_general.txt                      cites GHS with no edition in its declaration block
   mathematics_applied.txt                    cites CTCAE / FMEA with no edition
   physics_classical.txt                      cites FMEA with no edition
   physics_thermodynamics.txt                 cites GHS with no edition
   software_general.txt                       cites CTCAE / FMEA with no edition
   statistics_experimental_design.txt         cites CTCAE / FMEA with no edition
   statistics_inference.txt                   cites CTCAE / FMEA with no edition

OFFENDERS AFTER THE REPAIR, SAME 7 FILES            : 0
OFFENDERS ACROSS ALL 22 ENCODINGS, AFTER THE REPAIR : 0
```

Admissibility of the rank statistic, **z3**:

```
claim 1  'an order-preserving relabel moves the rank' : unsat    (rank is INVARIANT = admissible)
claim 2  'a fixed-real cut can be broken by a relabel': sat      (INADMISSIBLE)
         witness relabel: [11/4, 3, 13/4, 7/2, 15/4] -> count above 4 becomes 0, was 2
```

**Wolfram second falsifier** (computed on the local Wolfram Engine via `wolframscript`, exit 0, `Out` value returned):

```
$ wolframscript -code 'Module[{bands={1,2,3,4,5},phi},phi=Function[x,x^3+x];
    {Ordering[bands]===Ordering[phi/@bands], Length[Select[bands,#>=4&]],
     Length[Select[phi/@bands,#>=4&]]}]'
{True, 2, 4}
```

Attribution: computed with **Wolfram Language** (local Wolfram Engine). φ(x) = x³+x preserves `Ordering` (`True`) while the count clearing a **fixed** cut of 4 moves from 2 to 4 — independently reproducing §Objective's own proof that comparison to a fixed real is inadmissible, and that rank selection is.

## `reasoning`

Premises first.

1. `cdsfl_core_formal.md` tells every seat the critical level "arrives in your directive. Do not invent either." Since 2026-11-13 that is true: `_severity_declaration` delivers it.
2. The delivered level and the gate float are separate quantities — proved by mutation on a copy (level 7→9, threshold stayed 0.7), by type (`str` rank vs `float` on [0,1]), and by absence (`convergence_location.py` holds 0 references to either `critical_level` or `severity_scale`). Therefore Q1 governs **what a seat is told**, not what the gate admits.
3. Severity is ordinal, so any claim about the cut must survive re-labelling by a strictly increasing φ. Rank-from-top is a selected order statistic and survives — z3 `unsat`, Wolfram concurring on the contrapositive. Comparison to a fixed real does not — z3 `sat` with a witness.
4. On that admissible statistic, 7 places engineering at rank 2 from the top, matching CVSS and GHS exactly and sitting one band tighter than CTCAE. 9 places it at rank 1, where the up-set collapses to a single element and the predicate degenerates to equality with the maximum.
5. Mapping §10's five material categories onto the bands, four of five sit in 7-8 HIGH. A cut at 9 would make four-fifths of this project's own definition of material non-critical.
6. Therefore retain 7. Since retaining loosens nothing, no ruling is required to retain; a move to 9 loosens and is his.
7. For Q2, the manifest's own rule caps a standards-based encoding at CROSS_VERIFIED. Applying (a) current versioned citation or honest declared absence, (b) majority tool-checkable HARD constraints, (c) no `[VERIFY:current]` on a load-bearing citation, gives 11/11.
8. While measuring (a) I found the suppression asymmetry: `_severity_declaration` yields to any encoding carrying its own `SEVERITY SCALE:` line on the ground that it is "better-sourced", and on version-carrying that ground was false for 11 citations in 7 files. Repaired; guarded.

**Composability, under the founder's definition — the two repairs do NOT compose, and that is a measurement, not a judgement.** R1 (edition tokens + guard) and R2 (the maximal-band guard mechanising Q1) act on disjoint properties. Measured: R2's verdict is **invariant** to R1 — ranks `[2,2,2,3]`, 0 degenerate, before and after the encoding edits, because R1 touched no manifest entry (digest `501a257d…` unchanged). R1's offender count is **invariant** to R2 — 11→0 either way, because R2 touched no encoding. Neither improves the other's named property, so each is preferred **alone** on its own property and no composed fix is proposed. They are co-located in one test file for a reader's convenience, not composed: each test is independently deletable, and the module docstring names the single test to delete if the founder rules for 9.

## `disagreement`

**F5 is right in effect and wrong in mechanism, and the mechanism is what matters.** F5 says 9 "LOOSENS what the gate admits". Measured, the named level **never reaches the gate** — threshold unmoved under mutation, 0 references in the convergence module. So 9 cannot loosen the gate directly. It loosens *indirectly*: a seat told "critical at 9" assigns lower severities to loss-of-function defects, and those self-reported floats are what meet 0.7. **The loosening therefore passes through the model's own self-report, where no instrument records it.** The gate's shadow-severity diagnostic compares a *claimed* float to a *computed* float; nothing compares either to the FMEA rank the seat was told to use. So F5 understates the problem by locating it in the gate: a level change is a silent, unmeasured perturbation of seat behaviour, which is a worse property than a visible gate change, not a better one.

**Second disagreement, with the brief's own §2 expectation.** It anticipates that domains delivering silence are "a seat with no lawful move". Measured, that is not the current state: all six `scale = "none"` domains deliver an explicit instruction — `SCALE: none` plus a reason plus "the consequence scale is INHERITED from the application… name it". That is a lawful move. The unlawful case is narrower and different: a seat told to inherit **FMEA severity, critical at 7** with no edition, which is what I found and repaired.

**Third, against my own Q1 answer.** Step 3 of the procedure is an argued mapping of §10's categories onto FMEA bands. Nothing executed it. If that mapping is wrong — specifically if "wrong result" in a safety-bearing engineering artefact should map to 9-10 rather than 7-8 — then step 3 yields 9 and only the weaker arguments 2 and 4 survive. I have given the mapping in full rather than concealing that weakness.

## `plain_english`

Two separate things were being confused. The *engineering severity level* (the number 7) is a sentence printed into a reviewer's instructions; the *gate* (0.7) is a piece of arithmetic the software does. I proved by experiment that changing the first does not touch the second, so this question is about what reviewers are told, not about what the software lets through — which limits how much is at stake. On the substance: the standard labels 7-8 "high" and 9-10 "safety or regulatory", and the project should keep **7**, because four of the five kinds of defect this project itself calls serious (a wrong answer, broken measurement machinery, lost evidence, unreproducible results) are "high" and not "safety or regulatory" — so moving to 9 would quietly stop treating most of them as serious. Declaring both numbers was considered and rejected: nothing in the software can use two, and both band labels already reach reviewers anyway. Separately, I found and fixed a real problem: seven instruction files named a safety standard without saying which edition — "FMEA", "CTCAE", "GHS" with no year or revision — which is exactly the mistake this project corrected last week when it found it was citing a superseded version of CVSS. Eleven such citations are now complete, and a test now fails if anyone reintroduces one. Half the draft files are ready to be marked checked-against-standards; the other half are not, each for a named reason. Nothing was promoted, because that label currently controls nothing.

## `passes_run`

**Seven.** P1 digest verification (all 6 matched). P2 severity dump for all 10 domains + consumer greps. P3 the M1–M6 measurement script. P4 file-scope correction of M6 — which caught **two false positives of my own**, where `2019` matched the SI Brochure year rather than an FMEA edition; scope narrowed to the declaration block. P5 the guard test, which **failed twice on my own bugs** (`relative_to` on a tmp path; a docstring mention counted as a code reference — now checked by AST, with the incident recorded in the test's comment). P6 reconstruction of the as-dispatched text to prove the guard fires (11→0), plus z3 and Wolfram on admissibility, plus 38 regression tests. P7 searched for a conversion from a named ordinal rank to the gate's float: **0 definitions** across the runner, composer and vocabulary.

**The last pass added the only thing I am leaving open**, and it is recorded in the panel note rather than claimed: a seat is told to report a rank on a 1-10 scale, the gate reads a float on [0,1], and no code defines the conversion. I state it as a measured absence, not a confirmed defect, because no falsifier I ran demonstrates a wrong outcome from it. It is the strongest candidate for the next round. Also named rather than repaired: `physics_general.txt` cites **INES** with no revision, and because INES is not manifest-declared there is no edition anywhere in the project to supply — inventing one would be the magic wand this project refuses.

Terminating here: pass 7 produced no further above-threshold finding.

[verbatim-end]

## SEAT `fable` — its blind reply, verbatim

[verbatim-begin -->

All machinery executed. Final report.

---

## `verdict`

| Q | Verdict | Reason |
|---|---|---|
| **Q1** | **RECOMMEND 7 — retain; the proposed move to 9 is REJECTED on evidence; final say is HOLD FOR THE FOUNDER** since the recommendation touches what a gate-adjacent declaration admits. | 7 is the lowest published landmark whose band definition (S7 degradation / S8 loss of primary function) entails the project's pre-registered materiality rubric; 9 would exclude "the artefact does not work" from critical, and would make engineering the only domain gating on the catastrophic band when CVSS, CTCAE and GHS all chose the lower qualifying landmark. |
| **Q2** | **RECOMMEND: 16 of 22 move DRAFT → CROSS_VERIFIED; 6 stay DRAFT** (adjudicated per-encoding below, edits delivered as files, guard test added). | Each mover has primary-confirmed current citations and/or load-bearing claims re-executed by tool today; each stay has a named defect — including one **material finding: CTCAE v5.0 is superseded by v6.0**, refuting the manifest's 2026-11-12 "confirmed current" claim. |

## `q1_procedure`

**When a declared standard names ≥2 landmark bands, set the critical level to the LOWEST landmark whose published band definition entails the project's own pre-registered materiality definition** (`CRITICAL_DEFINITION_PREREG_2026-05-18.md` / §10's five categories: wrong result, hard-constraint violation, verification-integrity corruption, silent evidence loss, unreproducibility). Concretely: (1) write each landmark's defining criteria beside the five categories; (2) a band qualifies iff a defect meeting its definition is material under at least one category; (3) take the lowest qualifying band — choosing a higher one excludes material defects from critical, which is §10 category-4 silent evidence loss by construction; (4) if the band criteria cannot be read (standard unreachable), fall back to `p-pass-ambiguity-default` → HARD → the tighter cut, flagged `[VERIFY:current]`; (5) the rejected landmark stays in the delivered LEVELS line so the seat sees both.

**Applied to AIAG-VDA:** four independent secondary sources agree S7 = degradation of primary function, S8 = loss of primary function, S9 = regulatory noncompliance, S10 = safety hazard. Loss/degradation of the artefact's primary function **is** §10 category 1 (wrong result in the specified function) — so band 7-8 qualifies and is the lowest. **Yields 7.** The procedure applies to the next standard unchanged, and it is already the project's de facto rule — a consistency fact the brief did not surface: CVSS chose High (7.0) over Critical (9.0), CTCAE chose Grade 3 (severe) over Grade 4 (life-threatening), GHS chose Category 2 over Category 1. All four existing declarations sit on the lower qualifying landmark. Moving FMEA alone to 9 would be the project's only departure from its own pattern, on its only secondary-sourced scale.

**The third option (declare both landmarks):** evaluated and **already shipped in its simplest sufficient form**. The executed declaration above delivers `9-10 safety or regulatory` verbatim in the LEVELS line — both landmarks reach the seat today. A second machine-readable field (`safety_level = "9"`) has **zero consumers**: nothing in the repo reads even `critical_level` outside `composer._severity_declaration` (measured: 0 occurrences in the runner, 0 in convergence). It would be an addition nothing reaches — rejected under the additive standard until a consumer exists. The guard test now asserts both landmarks continue to reach the seat, which wires the existing two-landmark delivery to a test.

## `q1_consequence` (measured)

- `reference_runner_v3.py`: **0** occurrences of `critical_level`, **0** of `domain_vocabulary`; `CRITICAL_SEVERITY_THRESHOLD = 0.7` is a frozen float on the 0–1 proxy scale. `convergence_location.py`: likewise **0/0**; its `severity_threshold: float = 0.7` is a bare float. Both verified by AST import-walk and source count, pasted above.
- Therefore the two-sided gate and the gamma critical series are **mechanically independent** of the domain's named level: a 7→9 move changes **only the sentence delivered into the seat's prompt**. Convergence verdicts do not change by any code path.
- What it *does* change: a seat told "critical at 9" stops reporting S7/S8 findings (loss/degradation of primary function) as critical in FMEA coordinates; the model-asserted 0–1 severities that the gate *does* consume are downstream of that framing, so there is an **indirect, unmeasured gate exposure through model behaviour** — which is exactly why the recommendation holds for the founder rather than being applied.

## `q2_table`

| # | Encoding | Cited standard | Current? | HARD tool-checkable? | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 1 | software_general | CVSS v4.0, Table 22 (FIRST) | **Yes** (reconfirmed 2026-11-14) | Yes (ast, pytest, crosshair/z3, mypy, dis) | **CROSS_VERIFIED** | Primary spec read directly; 0.7×10=7.0 lands exactly on the High boundary, recomputed |
| 2 | chemistry_general | UN GHS Rev. 11 | **Yes — flag discharged**: UNECE published Rev. 11 on 2025-09-12 (primary) | Yes (rdkit, pint, scipy; element-balance by execution) | **CROSS_VERIFIED** | Rev-11 amendments don't touch acute-toxicity categories; inversion claim (Cat 1 most severe) correct |
| 3 | biology_genetics | CTCAE v5.0 "confirmed current" | **No — REFUTED**: v6.0 published 2025-07-10, errata 2026-01-20 | Yes (Biopython, scipy.stats) | **DRAFT** | Superseded version citation; Grade 3 landmark retained in v6.0, so the *level* survives |
| 4 | biology_natural_world | CTCAE v5.0 | **No** (same) | Partially (scoped inheritance) | **DRAFT** | Same supersession; scoping (ecology inherits application) is sound |
| 5 | biology_zoology | CTCAE v5.0 + unnamed welfare regimes | **No** (same) + own unresolved flag | Partially | **DRAFT** | Two unresolved currency gaps |
| 6 | cross_general | Founder's composition rule (internal); pint/SymPy | n/a — no external standard | Yes — **re-executed**: 3.540000 cm exact, m+s and K+V refused, CTCAE 3+CVSS 7.0=10.0 limitation reproduced | **CROSS_VERIFIED** | Judgement call flagged: all load-bearing claims tool-verified; nothing external exists to cite |
| 7 | info_science_general | FAIR 2016; ISO/IEC 11179 | **Yes — flag discharged**: ISO/IEC 11179-1:2023 Ed. 4 (2023-01-16, IEC webstore) | Yes (round-trip, validation) | **CROSS_VERIFIED** | Severity 'none' consistent with manifest |
| 8 | info_science_data_management | FAIR 2016; ISO/IEC 11179-1:2023 | **Yes** (same discharge) | Yes (hash/restore by execution) | **CROSS_VERIFIED** | |
| 9 | info_science_knowledge_rep | ISO/IEC 11179-1:2023; Dublin Core | **Yes** (same) | Yes | **CROSS_VERIFIED** | |
| 10 | info_science_retrieval | "Standard IR evaluation practice" — **unnamed**; ASA 2016 | ASA yes; primary basis unnamed | Yes | **DRAFT** | An unnamed source cannot be cross-verified; recommend naming the evaluation literature |
| 11 | logistics_warehousing | None confirmed primary (its own admission) | n/a | Yes (pint, reconciliation) | **DRAFT** | Its honesty is correct and the tier correctly reflects it |
| 12 | mathematics_applied | SI Brochure 9th ed. (BIPM 2019) | Yes (edition in force) | Yes (pint, SymPy, scipy) | **CROSS_VERIFIED** | Inheritance targets (FMEA 7, CTCAE Grade 3) match manifest |
| 13 | mathematics_numerical | IEEE 754-2019 / ISO/IEC 60559:2020 | Yes | Yes — **re-executed**: 53 bits, −1022..+1023, ties-to-even; 53·log₁₀2 = 15.954590 by Python **and Wolfram Language (local kernel)** | **CROSS_VERIFIED** | My first re-check used 52·log₁₀2 and "refuted" the figure wrongly — the claim survived its falsifier |
| 14 | mathematics_proof | None — "no standards body governs proof" | n/a | Yes (SymPy, z3) | **DRAFT** | CROSS_VERIFIED would certify a verification event that cannot exist; its route up is VALIDATED (HIL) directly |
| 15 | physics_general | SI Brochure 9th ed. | Yes | Yes — **re-executed**: 5 defining constants exact float equality, uncertainty 0.0 | **CROSS_VERIFIED** | |
| 16 | physics_classical | SI Brochure | Yes | Yes | **CROSS_VERIFIED** | FMEA-7 inheritance matches manifest |
| 17 | physics_quantum | SI Brochure; h exact | Yes — h = 6.62607015e-34 re-executed exact | Yes | **CROSS_VERIFIED** | |
| 18 | physics_thermodynamics | SI Brochure; k exact | Yes — k = 1.380649e-23 re-executed exact | Yes | **CROSS_VERIFIED** | GHS Cat-2 inheritance matches manifest |
| 19 | statistics_experimental_design | ASA 2016; CONSORT/PRISMA | **Yes — flag discharged**: CONSORT 2025 (2025-04-14, five journals), PRISMA 2020 | Yes (simulation, scipy.stats) | **CROSS_VERIFIED** | |
| 20 | statistics_general | Stevens (1946); ISO 3534 | Stevens yes (stable literature, matches the 2026-11-11 z3-verified admissibility results); ISO 3534 edition unconfirmed, marked not load-bearing | Yes | **CROSS_VERIFIED** | Judgement call flagged |
| 21 | statistics_inference | ASA 2016 (operative); ISO 3534 (vocabulary) | ASA yes, unsuperseded; ISO 3534 flagged not load-bearing | Yes | **CROSS_VERIFIED** | Judgement call flagged |
| 22 | statistics_time_series | ASA 2016 | Yes | Yes (statsmodels) | **CROSS_VERIFIED** | |

## `q2_coverage`

**22 of 22 examined; 0 left.** Counts re-measured from disk: 52 `.txt`, 1 universal, 51 domain encodings; exactly 22 carry both `SEVERITY SCALE:` and `TIER: DRAFT` (list pasted above), all dated 2026-11-12. 22/51 = 0.431373, Wilson [0.305012, 0.567347] — **confirmed independently by Wolfram Language (local kernel): {0.305012, 0.567347}**. Adjudication: 16/22 moved (0.727273, Wilson [0.518483, 0.868492]), 6/22 stay (Wilson [0.131508, 0.481517]). Three movers are explicitly flagged judgement calls (rows 6, 20, 21); if the founder's reviewers reject the "not load-bearing" carve-out or the internal-rule reading, those three revert and the split becomes 13/9.

## `tier_mechanism`

**The tier gates nothing at dispatch.** Established by: `grep -rn 'encoding_tier' --include='*.py' bench scripts` → hits only in `domain_vocabulary.py` (parse-time validation that the value is on the ladder, lines 76–81, and a CLI print, line 471); `grep -n 'TIER'` over `composer.py`, `reference_runner_v3.py`, `scripts/` → **0 consumers of the file-level `TIER:` line**. DRAFT was a label with no mechanism — under the additive standard, an addition nothing reaches. The delivered fix makes `bench/tests/test_severity_tier_guards.py` the TIER line's **first consumer** (legality, flag-consistency, supersession rules), so Q2's adjudication now changes something a test executes.

## `falsifier` and `falsifier_result`

Delivered files: **16 encoding edits** (tier + evidence), **3 biology corrections**, **1 manifest note correction** (`domain_manifest.toml` biology `critical_level_note` — the refuted claim is preserved verbatim inside the correction, per project practice), and **`bench/tests/test_severity_tier_guards.py`** (7 tests: tier legality; no unresolved `[VERIFY:current]` above DRAFT; superseded-CTCAE-v5.0-cannot-leave-DRAFT; the Q1 tripwire asserting `CRITICAL LEVEL: 7` + both landmarks reach the seat; no scale-bearing domain delivers silence; gate/convergence independence incl. `CRITICAL_SEVERITY_THRESHOLD == 0.7`; and a mutation test proving every guard goes red — including red on `CRITICAL LEVEL: 9`). The engineering manifest entry is **untouched**: no level was written as settled.

Executed, output pasted above in-session:
```
python3 -m pytest bench/tests/test_severity_tier_guards.py ... -q
43 passed in 0.61s        (7 new + 36 existing severity/dispatch tests)
```
The guard also demonstrated it can fail on real data: its first run went red on `statistics_inference.txt` (excusal regex not spanning a line break) — fixed, re-run green. Final sweep: `_severity_declaration("engineering","")` still delivers `CRITICAL LEVEL: 7` with both landmark bands; own-scale suppression intact (`FALSIFIER CLEAN` pasted above).

## `reasoning`

Premises, each executed or primary-sourced: (P1) the critical level reaches only prompt text — 0 `critical_level`/`domain_vocabulary` references in runner and convergence, by AST and count; (P2) the frozen 0.7 is not expressible as a rank on FMEA — recomputed: 1+0.7·9 = 7.3, between levels (F4 confirmed; also 7.0 CVSS exact, 3.8 CTCAE, 4.9 INES); (P3) FMEA band semantics from four concordant secondary sources: S7/S8 functional, S9/S10 safety-regulatory; (P4) the project's critical definition is consequence-based and pre-registered (§10 / F6 prereg). From P3+P4: band 7-8 already meets materiality (loss of function = wrong result), so the lowest qualifying landmark is 7; from P1: the choice is reporting vocabulary, bounded in consequence; from the cross-scale pattern (CVSS High, CTCAE Grade 3, GHS Cat 2): 7 preserves the project's uniform rule. For Q2: per-encoding citation currency was resolved by proactive verification (§9) rather than left flagged — which surfaced the CTCAE v6.0 supersession the 2026-11-12 pass missed.

## `disagreement`

Three points against the brief's framing. **(1) F5 overstates mechanically:** "moving to 9 loosens what is admitted" is true of reporting vocabulary only — by execution, `critical_level` admits nothing into any gate; the two-sided gate and gamma are independent floats. The founder-ruling constraint still binds (via indirect model-behaviour exposure), but the brief presents a gate change where measurement shows a prompt-text change. **(2) "7 is conservative, therefore tighter" conflates admission count with calibration:** labelling S7 degraded-function findings critical is not cost-free — on a safety-certified artefact, "critical" in FMEA coordinates brushes against a band with regulatory meaning; the (value, scale-name) discipline is what actually prevents miscommunication, not the cut's direction. My recommendation of 7 rests on the materiality-entailment procedure and cross-scale consistency, **not** on the conservatism default F5 leans on. **(3) The brief's F3 said "3 of the 4 declared scales were corrected... CTCAE v5.0 was confirmed already correct" — that confirmation was wrong:** v6.0 had been published four months before the 2026-11-12 check. The falsification loop caught the project's own verification pass, which is the system working, but F3 should not be cited as clean again.

## `plain_english`

The engineering severity scale has two natural cut points: 7 ("the thing stops working properly") and 9 ("safety or the law is implicated"). The project should keep 7, because its own definition of a critical finding is "a defect that makes the result wrong" — and a product that stops working is exactly that, even when nobody is endangered. Every other scale the project uses already follows this same rule, so 7 keeps the system consistent; only the founder can decide otherwise, and nothing was changed pending his word. Separately, of the 22 draft domain write-ups, 16 checked out against current published standards (several re-verified by running the maths and the tools today) and were promoted one rung; 6 stay draft for named reasons — the biggest being that the clinical severity scale the biology write-ups cite was quietly superseded last year, which this review caught and corrected. A new automated test now watches all of this so none of it can drift silently.

## `passes_run`

**3 passes.** Pass 1: read artefacts, execute the severity/tier/gate machinery, establish independence and the counts. Pass 2: proactive verification of every citation (6 web checks against primary publishers; Wolfram as second falsifier on two computed figures) — added the CTCAE v6.0 refutation, the GHS Rev 11 / ISO 11179-1:2023 / CONSORT 2025 discharges, and corrected my own wrong refutation of the 15.954590 figure. Pass 3: deliver and falsify the fixes — added nothing new above threshold beyond the guard-regex defect its own first run exposed. Terminated at diminishing returns: the remaining open items (ISO 3534 edition, the AIAG-VDA primary handbook, the CTCAE v6.0 document itself) are flagged in the files, not silently dropped.

**What would refute me (Q1):** a reading of the primary AIAG-VDA handbook showing the 7-8 band's definitions do **not** entail functional loss/degradation — e.g. if S7/S8 criteria were written as inconvenience/appearance classes — would collapse the materiality entailment and move the recommendation to 9; so would a founder-level ruling that CDSFL "critical" should mean only safety/regulatory consequence, which would also require re-cutting CVSS to 9.0 and CTCAE to Grade 4 for consistency. **(Q2):** `sha256sum` any adjudicated file against the dispatch stamps — my verdicts hold against the staged state; a primary UNECE/NCI/ISO document contradicting a discharge (command: open the cited publisher page; result: different edition or date) reverts that row to DRAFT, and `python3 -m pytest bench/tests/test_severity_tier_guards.py -q` failing after such a reversion is the designed loud signal.

Sources: [FMEA ranking tables (AIAG-VDA 2019)](https://qhubio.com/fmea-ranking-tables), [AIAG VDA FMEA tables](https://fmearatings.com/aiag-vda-fmea-tables), [Severity in FMEA (AIAG-VDA)](https://quasist.com/fmea/severity-in-fmea/), [Design FMEA severity table](https://sripadhmam.com/wp-content/uploads/2021/08/Design-FMEA-SOD-tables.pdf), [UNECE GHS Rev. 11 (2025)](https://unece.org/transport/dangerous-goods/ghs-rev11-2025), [NCI CTEP CTC page](https://ctep.cancer.gov/protocoldevelopment/electronic_applications/ctc.htm), [PharmaSUG 2026 on CTCAE v6.0](https://pharmasug.org/proceedings/2026/DS/PharmaSUG-2026-DS-131.pdf), [CTCAE v6.0 lookup](https://www.weguide.health/tools/ctcae-lookup), [CONSORT 2025 statement (PLOS Medicine)](https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1004587), [CONSORT 2025 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/40228833/), [CVSS v4.0 specification (FIRST)](https://www.first.org/cvss/specification-document), [ISO/IEC 11179-1:2023 (IEC webstore)](https://webstore.iec.ch/en/publication/81976). Wolfram-derived values (15.9545898; Wilson {0.305012, 0.567347}) computed with Wolfram Language (local Wolfram Engine, via wolframscript).

[verbatim-end]


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 43 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel fmea_level_and_draft_encodings_2026-11-14_joint) -->

All green; 0 stale citations remain. Five passes run, terminating.

---

## `verdict`

| Q | verdict |
|---|---|
| **Q1** | **RETAIN 7.** I concur with both seats on the answer and **reject both decision procedures as general rules** — z3 shows they are two different rules, and each breaks on a different one of the project's own four declared scales. Any move to 9 remains the founder's. |
| **Q2** | **10 of 22 EARN CROSS_VERIFIED — but my set differs from both seats, and I recommend WRITING NONE.** `encoding_tier` is consumed by 0 decisions, so a promotion is not a repair. The adjudication is recorded at the write site instead. |
| **J3** | **The SI Brochure carries the same stale confirmation as CTCAE, and it undercuts 4 encodings BOTH seats promoted.** |

**First: the brief's premise is arithmetically wrong.** It asks me to adjudicate "the 5 you classify differently." 5 is `|16 − 11|`, the *net*. The symmetric difference is **11** — `cc2` alone promotes 3, `fable` alone promotes 8, and only 8 are promoted by both. Confirmed in Python and by Wolfram Language (local kernel, exit 0): `{3+8, Abs[16-11]} = {11, 5}`. I adjudicate all 11.

## `J1` — the 11 disputed encodings, adjudicated

The governing text is the manifest's own tier definition: *"A machine-generated encoding of **published formal standards** reaches CROSS_VERIFIED."*

| # | encoding | cc2 | fable | **my verdict** | decisive evidence |
|---|---|---|---|---|---|
| 1 | biology_genetics | CV | DRAFT | **DRAFT** — fable | cc2's cited evidence *was* the false confirmation: line 8 read `CTCAE v5.0 (2017), confirmed current 2026-11-12`, wrong by ~16 months |
| 2 | information_science_retrieval | CV | DRAFT | **DRAFT** — fable | primary basis is `Standard information-retrieval evaluation practice` — unnamed. An unnamed practice is not a published formal standard |
| 3 | mathematics_proof | CV | DRAFT | **DRAFT** — fable | declares "No standards body governs proof": the tier antecedent fails. Whether a second route to CROSS_VERIFIED exists is ambiguous → §1 HARD → tighter |
| 4 | chemistry_general | DRAFT | CV | **DRAFT** — cc2 | `[VERIFY:current] -- the Rev. 11 citation is secondary` **could not be discharged from here**: unece.org returned HTTP 403 on both URLs. 5 secondary sources concur on `ST/SG/AC.10/30/Rev.11`, 2025-09-12 |
| 5 | cross_general | DRAFT | CV | **DRAFT** — cc2 | cites no external standard (founder's internal rule); antecedent fails |
| 6 | information_science_general | DRAFT | CV | **CROSS_VERIFIED** — fable | **fable's evidence moved me.** I primary-confirmed `ISO/IEC 11179-1:2023, Edition 4.0, 2023-01-16` on the IEC webstore (pub 81976). Flag now discharged in the text |
| 7 | information_science_data_management | DRAFT | CV | **CROSS_VERIFIED** — fable | same primary discharge |
| 8 | information_science_knowledge_representation | DRAFT | CV | **DRAFT** — cc2 | ISO half discharged, but **Dublin Core is still unversioned and I did not check DCMI**. Half a discharge is not a discharge |
| 9 | physics_thermodynamics | DRAFT | CV | **DRAFT** — cc2's reason survives, plus one neither seat had | inherits chemistry's open GHS flag; *and* cited the superseded 2019 SI printing |
| 10 | statistics_experimental_design | DRAFT | CV | **DRAFT** — unsettled | text still says the edition "could not be confirmed". I did not reproduce fable's CONSORT 2025 discharge. **Settling check:** fetch the PLOS Medicine CONSORT 2025 statement, then edit the SOURCES line — promotion before the text edit is self-contradicting |
| 11 | statistics_general | DRAFT | CV | **DRAFT** — cc2 | `ISO 3534 for vocabulary`, unversioned **with no flag** — an undisclosed gap is worse than a disclosed one |

**Score: `fable` right on 3, `cc2` right on 6, 1 unsettled, 1 (#6/#7) where fable was right and I executed the discharge.** Neither seat's number survives.

**`cc2` is internally inconsistent here.** It added edition tokens to 7 files (its R1 repair) and then left chemistry_general, physics_thermodynamics and statistics_experimental_design at DRAFT on the ground *"cites X with no edition"* — the ground its own repair had just discharged.

## `J2` — Q1: the agreement survives, the procedures do not

**They are two rules, not one, and z3 proves it.** Formalising each seat's qualifying predicate over bands `B` against the project's materiality set `M`:

- `cc2` step 3 — *"the lowest band at least one material category reaches"* → `B ∩ M ≠ ∅` (**existential overlap**)
- `fable` — *"the lowest landmark whose definition entails materiality"* → `B ⊆ M` (**entailment**)

`B ⊆ M` implies `B ∩ M ≠ ∅`, so the predicates are ordered, not equivalent. Executed:

```
CLAIM 1  'the 2 predicates can pick DIFFERENT cuts' : sat    <-- 2 RULES, NOT 1
  witness: band0 (a=F,b=F) band1 (a=T,b=F) band2 (a=T,b=T) band3 (a=T,b=T)
  cc2 -> band 1,  fable -> band 2        DISAGREEMENT = 1 band
CLAIM 2  'fable cut can sit BELOW cc2 cut'          : unsat   <-- strict ordering
```

**The standard on which they disagree** is the z3 witness made concrete: any standard with a *partially material* band below a wholly material one. E.g. band 1 = "degraded output in a non-primary function" (some instances material, some not) under band 2 = "wrong output in the primary function" (all material). `cc2` cuts at 1, `fable` at 2.

**And the agreement at 7 is reached by two routes that each fail on the project's own scales:**
- `cc2` claims its procedure *"reproduces CVSS → High (7.0) ... That is the evidence it generalises."* It does not. The existential predicate has **no lower bound** — §10 category 1 (wrong result) plainly reaches CVSS **Medium 4.0–6.9**, so the rule yields Medium, not High, unless an unstated constraint stops it. cc2 concedes step 3 is "argued, not measured"; the argument is doing the work the rule claims to do.
- `fable`'s predicate needs bands carrying **published criteria text** to entail with. CVSS v4.0 Table 22 bands are **numeric score ranges only**. The predicate has nothing to evaluate. Inapplicable, not wrong.

Both yield 7 on FMEA because FMEA *does* carry criteria text (S7 degradation / S8 loss of primary function) and §10's categories map into it cleanly. **So: the answer corroborates; the procedures do not.** That is the honest reading and it is what "no votes in CDSFL" demands.

## `J3` — the staleness audit, per scale, against primary sources

| scale | dated claim in the repo | my primary re-check (2026-11-14) | verdict |
|---|---|---|---|
| **CVSS v4.0** | `Confirmed 2026-11-12` (unflagged — the only other confirmation of CTCAE's kind) | first.org: v4.0 current, **no successor** | **STANDS** |
| **SI Brochure 9th ed.** | `(BIPM, 2019)` in **5 encodings** | bipm.org primary: *"9th edition (2019) Complete brochure (updated in 2026)"*; **version 4.01, published 2026-06-04**, endorsed by the **28th CGPM, 13–15 Oct 2026**. v3.02 (2025) revised the dalton | **STALE — repaired** |
| **ISO/IEC 11179** | unversioned + `[VERIFY:current]` ×3 | IEC webstore pub 81976: **11179-1:2023, Ed. 4.0, 2023-01-16** | **DISCHARGED — repaired** |
| **GHS Rev. 11** | `[VERIFY:current]`, self-declared secondary | unece.org **HTTP 403**, two URLs | **OPEN** |
| **AIAG-VDA FMEA** | `[VERIFY:current]`, secondary only | no 2nd edition found; 1st ed. 2019 + Jun 2020 errata | **secondary only — Q1's own basis** |
| **CTCAE** | corrected to v6.0 today | manifest's primary cite; encodings were **not** corrected | **see below** |

**Answer to "how many others carry a confirmation of the same kind": exactly one — CVSS — and it survives.** Chemistry and engineering both self-flag `[VERIFY:current]`, which is a different and honest epistemic state. **But the audit found a worse case the manifest's own scales don't cover: the SI Brochure, cited in 5 encodings with no flag at all, was 5 months stale — and 4 of those 5 sit in encodings BOTH seats recommended for promotion** (mathematics_applied, physics_general, physics_classical, physics_quantum). The agreed set was not clean either.

**What `encoding_tier` consuming 0 decisions does to my Q2 recommendation:** I verified the brief's claim myself by AST rather than accepting it — 4 references, all in `domain_vocabulary.py` (membership validation + a `print` in its `main()`); 0 in composer, runner, registry, convergence. So **writing a promotion would be an addition nothing reaches** — this project's most-shipped defect class (11 since 2026-08-01). I wrote **no tier**. And yes, the adjudication **must** be recorded where a tier is written: I put it in the `domain_manifest.toml` tier block, which `domain_vocabulary.load()` is the sole consumer of and which anyone writing a tier must open.

## The material finding — a correction that reached nobody

`composer.py:888` returns `""` whenever the encoding carries its own `^SEVERITY SCALE:` line, on the stated ground that the encoding is *"the narrower, better-sourced statement."* For biology that ground was **false**: the manifest was corrected to v6.0 today; the three encodings still said v5.0. The worse-sourced statement wins, so the founder's correction reached no seat. §10 category 4.

## `falsifier` / `falsifier_result`

**F1 — does the correction reach a seat?** (imports the real `composer` and `domain_vocabulary`; no key, no fixture)

```
BEFORE: MANIFEST biology scale: CTCAE v6.0 grade
        manifest declaration delivered alongside encoding: ''
        CTCAE versions the SEAT actually sees: ['CTCAE v5.0']
        FALSIFIED
        AssertionError: biology seat receives CTCAE v5.0 only; the manifest's
        primary-verified v6.0 correction is suppressed by composer.py:888
AFTER:  CTCAE versions the SEAT actually sees: ['CTCAE v5.0', 'CTCAE v6.0']
        manifest version present in seat text: True          exit=0
```
(v5.0 survives after the fix only inside the `CORRECTED` note — the record is preserved, the declaration is v6.0.)

**F2 — the guard, red on dispatched text and green after:**
```
A) as-dispatched:  AssertionError: biology_genetics.txt ... names CTCAE v5.0
                   while domain_manifest.toml declares CTCAE v6.0 ... the
                   correction reaches nobody        1 failed, 6 passed
B) after repair:   7 passed in 0.26s
```

**F3 — z3 on the two procedures:** `sat` / `unsat` as quoted in J2.

**Regression + cross-verification:**
```
45 passed in 4.83s   (new guard + the 3 named suites)
manifest STILL PARSES; tiers: ['DRAFT','CROSS_VERIFIED','VALIDATED','OPERATIONAL']
Wilson 10/22  Wolfram {0.26920294180813314, 0.6534020467926505}
              statsmodels [0.2692029418081, 0.6534020467927]   agree to 13 dp
```
Wolfram-derived values computed with **Wolfram Language** (local Wolfram Engine via `wolframscript`, exit 0, `Out` value returned).

**What did NOT work:** (1) `git` is absent from this sandbox (exit 128), so my first attempt to demonstrate the guard against the as-dispatched text via `git checkout` failed; I reverted the declaration manually instead. (2) `timeout` is absent on this host — the first Wolfram call died `exit=127` before reaching the kernel. (3) My ISO-11179 edit to `information_science_data_management.txt` silently no-matched on a line-break difference; I caught it only because I printed the edit log, and had to re-read the raw bytes. (4) The **UNECE primary is unreachable from here (403, twice)** — I could not reproduce `fable`'s "primary" GHS discharge and say so rather than inherit it.

## `fix` — delivered at real paths

13 citation repairs across 11 files, plus the guard and the record:

- `bench/directives/biology/{biology_genetics,biology_natural_world,biology_zoology}.txt` — CTCAE v5.0 → **v6.0 (MedDRA 28.0), published 2025-07-22**, Grade 3 quoted verbatim; the false confirmation preserved *as* a correction, not deleted
- `bench/directives/{mathematics/mathematics_applied,physics/physics_general,physics/physics_classical,physics/physics_quantum,physics/physics_thermodynamics}.txt` — SI Brochure 2019 printing → **version 4.01, 2026-06-04**
- `bench/directives/information_science/{general,data_management,knowledge_representation}.txt` — ISO 11179 → **ISO/IEC 11179-1:2023 Ed. 4.0**; Dublin Core's flag deliberately **kept** in knowledge_representation
- `bench/tests/test_the_manifest_correction_reaches_the_seat_2026-11-14.py` — 7 tests, incl. a non-vacuity test and a mutation test
- `bench/cdsfl_registry/domain_manifest.toml` — the tier-block record (comment only; manifest re-parsed and validated after)
- `scripts/two_cut_procedures_are_not_one_rule_2026-11-14.py`, `experimental_notes/Panel_Joint_FMEA_Level_And_Tier_Adjudication_2026-11-14.md`

**I did not change the suppression rule.** Preferring a better-sourced encoding is defensible; altering what the composer admits is the founder's ruling, not a repair. The root cause is that the version string lives in two independently editable places with nothing comparing them.

## `composability`

**The data repair and the guard DO compose, and that is a measurement.** Executed both ways: the guard **alone** (without the citation fixes) is **red** — it blocks but leaves the artefact wrong and no seat served; the citation fix **alone** is green but leaves the invariant unenforced, so the next manifest correction drifts exactly as this one did. Neither half alone yields a correct-*and*-enforced state; the pair does. That is a demonstrated advantage over each part in isolation, not "they don't conflict."

Against `cc2`'s own composability claim: it reported R1 and R2 as *not* composing, measured by invariance. I accept that measurement for *its* two repairs — different property pairs, different answer.

## `strongest_disagreement`

**I reject `cc2`'s claim that its procedure *"reproduces CVSS → High (7.0) and CTCAE → Grade 3, i.e. every existing declaration. That is the evidence it generalises."*** z3 characterises its predicate as existential overlap, which has no lower bound; §10 category 1 reaches CVSS Medium; and CVSS Table 22 carries no criteria text for a category to "reach," so the mapping is unstated judgement — which cc2 itself concedes ("argued, not measured"). The generalisation claim is the one part of cc2's answer with no execution behind it, and it is the part load-bearing for Q1.

**And I reject `fable`'s row 2**, that chemistry_general's GHS flag is *"discharged: UNECE published Rev. 11 on 2025-09-12 (primary)."* I could not reach any UNECE primary page (HTTP 403, two URLs). Five independent secondary sources concur, so fable's *conclusion* is probably right — but the flag it claims to discharge says specifically *"the Rev. 11 citation is secondary,"* and secondary corroboration cannot discharge a secondary-sourcing flag. **Single settling check:** fetch `unece.org/.../ghs-rev-11` from a host not 403'd and read the document symbol.

**`fable` moved me on three rows** (biology_genetics, information_science_retrieval, mathematics_proof — and its ISO 11179 lead, which I then confirmed at primary). **`cc2` moved me on none**, but its DRAFT reasons were right six times.

## `falsifier` — what would refute each position

- **Q1 = 7** → the primary AIAG-VDA handbook showing S7/S8 are inconvenience/appearance classes, not functional loss. Then §10 category 1 no longer reaches 7-8 and the cut is 9. Also refuted by a founder ruling that CDSFL "critical" means safety/regulatory only — which would force CVSS to 9.0 and CTCAE to Grade 4 for consistency.
- **"two rules, not one"** → exhibiting a formal standard in which every band is either wholly material or wholly immaterial. Then overlap and entailment coincide and the z3 witness is unreachable in practice.
- **"SI citation was stale"** → a BIPM page showing v4.01 is a reprint with no normative change *and* that v3.02 did not revise the dalton. The physics content is unaffected either way; only the citation is at issue.
- **"the correction reached nobody"** → any code path delivering the manifest's `severity_scale` to a biology seat alongside the encoding. F1 found none; a reference I missed refutes it.
- **"write no tier"** → one consumer anywhere reading `encoding_tier` for a decision. My AST found 4 references, all non-deciding; a dynamic read (`getattr`, dict lookup by computed key) would evade it and refute me.
- **10 of 22** → Wilson [0.269, 0.653] at 22 trials is wide enough that this number is a recommendation, not a measurement. Any row's citation contradicted at primary moves it.

## `aims_check`

**Additive** — 13 stale citations corrected, 0 features disabled, 0 removed. The guard is wired to pytest and demonstrated red on real data twice, so it is not an addition nothing reaches. The false confirmations are preserved *inside* their corrections rather than deleted. **Simplest sufficient** — I fixed the data and compared the two copies of the version string; I did **not** touch the suppression rule, add a `safety_level` field, or write a tier, all of which would be more surface than the problem requires. **Democratisation** — the defect was in prose a reviewer reads, in biology and physics, not in code; the mechanism that found it was a primary-source re-check, which works on any artefact and any machine.

**Residual, named not buried:** GHS Rev. 11 primary unreachable from this sandbox; Dublin Core unversioned; IEEE 754-2019, ASA 2016, CONSORT and ISO 3534 not primary-re-checked this round. And the standing one — **nothing in this repository re-checks a recorded confirmation.** That is what made CTCAE wrong by 16 months and the SI Brochure wrong by 5 months, and no test can fix it.

**Passes run: 5.** P1 digests (9/9 matched) + manifest dump. P2 AST on `encoding_tier` + set difference, which caught the brief's own arithmetic. P3 primary-source sweep, which found the SI staleness. P4 the composer falsifier → CONFIRMED, then repairs + guard (caught my own silent no-match edit). P5 z3 + Wolfram/statsmodels cross-check + the record; re-ran 45 tests. Pass 5 produced no new above-threshold finding. Terminating.

**Sources:** [BIPM SI Brochure](https://www.bipm.org/en/publications/si-brochure) · [BIPM v4.01 announcement](https://www.bipm.org/en/-/2026-06-04-updated-si-brochure-clarifies-the-status-of-non-SI-units) · [FIRST CVSS](https://www.first.org/cvss/) · [ISO/IEC 11179-1:2023, IEC webstore](https://webstore.iec.ch/en/publication/81976) · [UNECE GHS Rev. 11](https://unece.org/transport/dangerous-goods/ghs-rev11-2025) (403 from sandbox) · [AIAG-VDA FMEA severity tables](https://fmearatings.com/aiag-vda-fmea-tables)

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 89 recorded tool call(s).

<!-- verbatim-begin: fable (panel fmea_level_and_draft_encodings_2026-11-14_joint) -->

All green. Final sweep (pass 7) produced no new above-threshold finding. Terminating and reporting.

---

# JOINT VERDICT — seat 3, round `fmea_level_and_draft_encodings_2026-11-14`

## `verdict`

| Q | verdict |
|---|---|
| **J1 (Q2)** | **Neither 11 nor 16. Adjudicated: 17 of 22 CV-eligible, 5 stay DRAFT** (0.772727, Wilson [0.565600, 0.898770]; interval cross-verified by Wolfram Language, local Wolfram Engine: {0.565600, 0.898770}). Per-row adjudication below — **fable wins 10 of the 11 contested rows on verdict, cc2 wins 1 on remedy discipline**, and one row (biology_genetics) flips from fable's DRAFT to eligible because I repaired its only named defect this round. **Tier lines held for the founder, with the full evidence record delivered where he will read it.** |
| **J2 (Q1)** | **RETAIN 7 — agreement SURVIVES, and not as corroboration-by-vote.** The two procedures are **2 rules that can disagree**, demonstrated by execution on a constructed standard (cut at class 1 vs class 3 of 4). They coincide on AIAG-VDA because FMEA's bands partition by consequence-of-function — the same coordinates as §10. Two valid routes coinciding on this standard is evidence; it would not be on a standard with intensionally-defined bands. |
| **J3** | Of the 3 other declared scales: **CVSS v4.0 NOT stale** (primary re-checked: current, spec doc v1.2, metrics unchanged since 2023-11); **GHS Rev. 11 confirmed against the UNECE primary** (ST/SG/AC.10/30/Rev.11, published 2025-09-12; flag discharged); **FMEA STALE at printing level** — current is **1st Edition, 2nd Printing, August 2022**, the manifest cited "1st edition 2019 (errata June 2020)" — same shape as CTCAE/CVSS, corrected this round. Stale-in-some-respect rate across the 4 declared scales: 2/4 = 0.500000, Wilson [0.150039, 0.849961]; among citations that *claimed* a confirmation: 1/2, Wilson [0.094531, 0.905469]. Small n — the mechanism matters more than the rate, and the mechanism is now partly closed (below). |
| **The "0 consumers" fact** | **Materially incomplete, and I measured the correction.** The AST claim is true of the manifest field `encoding_tier` and **false of the file-level `TIER:` line**: `composer.compose(domain, model).rendered_text` delivers the default encoding's `TIER: DRAFT` line **verbatim** for 8 of 9 routable domains. The consumer the AST sweep cannot see is the **seat model**. A tier flip is a prompt change to every seat — the same class as the Q1 critical level, which both blind seats held for the founder. So: yes, the adjudication must be recorded before any tier is written, and it now is. |

## J1 — the 11 contested rows (the brief's "5" is wrong: 16−11=5 is the *net*; the symmetric difference is **11**, recounted programmatically)

**cc2-only CV (3):**
- **biology_genetics — fable right at dispatch.** cc2's evidence was "confirmed current 2026-11-12" — it accepted the exact confirmation J3 proves false, the failure the whole round is about. Repaired this round (v5.0→v6.0 against the NCI primary, Grade 3 wording unchanged); **now CV-eligible**, which is why my total is 17, not 16.
- **is_retrieval — fable right, DRAFT.** `SOURCES: Standard information-retrieval evaluation practice` is an **unnamed basis**; nothing exists to cross-verify against. cc2's stated ground ("dated doc, no edition exists") describes the ASA citation and misses the unnamed primary. Settling check: name the evaluation literature in the file; then it moves.
- **mathematics_proof — fable right, DRAFT.** CROSS_VERIFIED marks a verification **event**. cc2's "5/8 tool-checkable" is check*ability*; no 2-source verification of this encoding's content was executed by anyone, and no standard exists to verify against. Its route up is VALIDATED (HIL) directly. This also disciplines fable's own cross_general call: the distinguisher is that cross_general **has** an executed verification event (pint + SymPy agreeing to 0.000e+00, re-executed) and mathematics_proof has none.

**fable-only CV (8):** chemistry_general (GHS Rev. 11 **confirmed against the UNECE primary by me today**, flag discharged in file and manifest), is_general / is_data_management / is_knowledge_representation (ISO/IEC 11179-1:2023 **Edition 4, 2023-01-16, confirmed current**; DCMI Metadata Terms 2020-01-20 / ISO 15836-1:2017, -2:2019; flags discharged in-file), physics_thermodynamics (own sources primary and exact; the GHS inheritance correctly names scale+level while the **version lives in the manifest** — duplicating it would be 2 tables that drift; dependency chain traced to the discharged chemistry citation per the §3 boundary-tracing amendment), statistics_experimental_design (CONSORT 2025, 2025-04-15, + PRISMA 2020 confirmed, discharged), cross_general (CV-eligible, flagged to the founder as the weakest promotion), and **statistics_general — fable right in verdict, wrong in remedy**: the "not load-bearing" carve-out left ISO 3534 unversioned, which is the CVSS-v3.1 failure shape; I **pinned** it instead — ISO 3534-1:2006 Ed 2, corrected 2007-09, reviewed and confirmed 2021, and **ISO marks it for revision as of 2026-06-24**, which is recorded in-file because this citation ages. That one row is cc2's discipline (versions in files) applied to fable's verdict.

The deep difference between 11 and 16 was never 5 encodings — it was **two defensible readings of the question**: cc2 adjudicated the *staged files* (and was right that un-delivered discharges don't count); fable adjudicated *its edited files* (and its edits died with its sandbox). The adjudication: deliver the edits in the real tree — done — then count.

## J2 — same rule or two rules?

**Two rules.** cc2 maps the project's material categories to the band their **consequence magnitude** sits in; fable asks whether a band's **published definition entails** materiality. Executed construction (`scripts/the_two_q1_procedures_can_disagree_2026-11-14.py`): a tolerance-class standard whose lowest class is defined as *"any deviation beyond nominal tolerance, however small."* Any such deviation **is** a hard-constraint violation (§10 category 2), so fable's entailment rule cuts at **class 1 of 4**; the categories' representative consequences sit at class 3, so cc2's magnitude mapping cuts at **class 3 of 4**. Output: `DIVERGENCE DEMONSTRATED: same standard, same materiality definition, different cuts.` They coincide on AIAG-VDA because S7 (degradation of primary function) / S8 (loss of primary function) are **consequence partitions** — the two coordinates are the same there. So RETAIN 7 stands on three independent grounds (admissible rank-from-top = 2, matching CVSS/GHS; §10 entailment via S7/S8 = wrong result; cross-scale lower-qualifying-landmark pattern), and the divergence case is pre-resolved: intensionally-defined bands → ambiguity is HARD per §1 → tighter cut → hold for the founder. fable's rule unguarded is the dangerous one of the two — it drags the cut to any definitionally-broad low band.

## `composability`

The two seats' repairs (cc2: edition tokens in files; fable: primary discharges + tier moves) were built in separate sandboxes and **neither survived into this tree** — so composition here was not optional coexistence but necessity: fable's discharges without cc2's in-file version discipline reproduce the CVSS-v3.1 shape (statistics_general proves it); cc2's discipline without fable's primary checks leaves 7 flags undischarged forever. The measurement that the composed result dominates either alone: the guard test fails on cc2-only state (v5.0 live in 3 files — executed red) and fable's own adjudication loses biology_genetics without the in-file repair (16 vs 17). Each half alone leaves a named defect the other closes; that is the founder's strong sense of composability, demonstrated red/green rather than judged.

## `reasoning` (compressed)

(1) The tier is prompt-delivered — measured by execution, wired to a test; therefore Q2 is not a no-op bookkeeping question and promotions carry the Q1 class of consequence. (2) CROSS_VERIFIED marks a verification event; 17 encodings now have one (primary citation reads 2026-11-14 + tool re-executions on record), 5 do not. (3) Q1's two procedures coincide on consequence-partitioned standards and split on intensional ones — executed, not argued. (4) A confirmation is a dated event: 2 of 4 declared-scale citations were stale in some respect within ~16 months and ~40 months respectively of their source events; the repair is dates-and-cadence in the citations plus a mechanical re-check of the one failure shape that has recurred, not a speculative scheduler.

## `falsifier` / `falsifier_result`

Delivered at real paths, executed, quoted:
- `bench/tests/test_the_tier_line_reaches_the_seat_2026-11-14.py` — 4 guards. **Red first**: `AssertionError: directives still citing superseded CTCAE v5.0 … ['biology_genetics.txt', 'biology_natural_world.txt', 'biology_zoology.txt']` → after repair: `4 passed in 0.25s`. Includes a mutation check proving a v5.0 `SEVERITY SCALE:` line offends even beside a correction note, and a quoted refuted claim does not. **What did not work and was fixed**: my first guard flagged the refuted claims preserved verbatim inside corrections — project practice requires preserving them, so the predicate was sharpened from "mentions v5.0" to "cites v5.0 live," with the as-dispatched red state retained under the new predicate.
- `scripts/the_two_q1_procedures_can_disagree_2026-11-14.py` — `fable's entailment rule -> cut at class 1 of 4; cc2's magnitude mapping -> cut at class 3 of 4; DIVERGENCE DEMONSTRATED`.
- Regressions: `38 passed in 5.45s` (the 3 stamped severity test files), plus `10 passed in 0.47s` final. Manifest re-parses through `domain_vocabulary.load()` (fail-closed) in those runs; its new digest is `9beaec577c8a02c5`.
- 9 file repairs + 2 manifest corrections, itemised in `experimental_notes/Panel_Joint_FMEA_Level_And_Tier_Adjudication_2026-11-14.md`.

## `strongest_disagreement`

**Against cc2**: its claim that writing promotions "would be an addition nothing reaches" rests on a measurement of the wrong surface — cc2 flipped the **manifest** tiers on a copy and observed byte-identical composition, but Q2's object is the **file-level** `TIER:` line, which I measured reaching `rendered_text` verbatim in 8 of 9 domains. The conclusion (hold the tiers) survives; the mechanism was wrong, and a wrong mechanism with a right conclusion is the thing cc2 itself accused F5 of. Also rejected: its biology_genetics CV, grounded on the precise stale confirmation this round refutes.
**Against fable**: its 16 counts edits that existed only in its own sandbox as if delivered — in the staged tree its number was unearned until someone re-delivered the discharges; and its statistics_general "not load-bearing" carve-out recreates the unversioned-citation failure shape it had itself just caught in CTCAE.
**Against the brief**: "the 5 you classify differently" is false — the symmetric difference is **11 rows** (3+8), recounted programmatically; and the "0 consumers" framing is incomplete as above.

## `aims_check`

Additive: no feature removed or disabled; every new guard is wired to a caller and executed (red→green shown); the one named-but-unbuilt item (scheduled re-verification) is recorded as a gap rather than built unreached. Simplest sufficient: root cause is dated-confirmation staleness; the fix is corrected citations carrying dates and cadence plus one mechanical re-check of the recurred shape — no scheduler, no new fields, no tier flips without the founder. Democratisation: every repair lands in prompt-delivered text, the surface every kind of seat reads.

## What would refute me

- **Q1/7**: the primary AIAG-VDA handbook showing S7/S8 defined as appearance/annoyance classes rather than function degradation/loss — collapses the entailment and moves the cut to 9; or a founder ruling that CDSFL-critical means safety/regulatory only (which then also requires CVSS→9.0 and CTCAE→Grade 4 for consistency).
- **Two-rules claim**: a proof that for every standard satisfying both seats' stated preconditions the two procedures select the same band — my construction is a counterexample, so the refutation must show my constructed standard violates a precondition one seat actually stated.
- **17/22**: any primary publisher page contradicting a discharge (UNECE, ISO/IEC, CONSORT journals, NCI, FIRST) reverts that row to DRAFT; `sha256sum` against the stamps distinguishes my repairs from the dispatch state.
- **Tier-delivery fact**: run the delivered test; if `compose().rendered_text` ever lacks the default encoding's TIER line for ≥8 domains, test 1 fails and my reframing of Q2's consequence falls with it.
- **FMEA printing staleness**: AIAG's own catalogue (FMEAAV-1) showing no August 2022 2nd printing would void that correction; the severity bands themselves remain `[VERIFY:current]` — I did not claim them primary-confirmed.

## Termination

**7 passes**: (1) digest/tree-state verification; (2) tier-ladder semantics + the prompt-delivery measurement; (3) contested-row file reads + programmatic recount (11, not 5); (4) primary-source checks, 8 standards; (5) repairs with red→green guard + 48 targeted tests; (6) J2 divergence falsifier + Wilson/Wolfram cross-verification; (7) final sweep — residuals named, not silently dropped: ASA 2016 accepted on both seats' concordant reasoning without my own primary re-read; INES in `physics_general` remains unversioned with no in-project edition to supply (inventing one is the magic wand); CTCAE v6.0 primary accepted from the orchestrator's stamped verification. Pass 7 produced no new above-threshold finding. Stop.

Sources: [UNECE GHS Rev. 11](https://unece.org/transport/dangerous-goods/ghs-rev11-2025) ([primary PDF](https://unece.org/sites/default/files/2025-09/GHS%20Rev11e.pdf)), [ISO/IEC 11179-1:2023](https://www.iso.org/standard/78914.html), [ISO 3534-1:2006](https://www.iso.org/standard/40145.html), [CONSORT 2025 (PLOS Medicine)](https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1004587), [CONSORT 2025 (Lancet)](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(25)00672-5/fulltext), [DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/), [ISO 15836-2 publication note](https://www.dublincore.org/news/2020/01-16-dcmi-metadata-terms-revised/), [CVSS v4.0 specification (FIRST)](https://www.first.org/cvss/v4-0/cvss-v40-specification.pdf), [IEEE 754 (IEEE SA)](https://standards.ieee.org/ieee/754/11684/), [SI Brochure 9th ed (BIPM)](https://www.bipm.org/en/si-brochure-9), [28th CGPM](https://www.bipm.org/en/committees/cg/cgpm/meetings), [AIAG FMEAAV-1](https://www.aiag.org/training-and-resources/manuals/details/FMEAAV-1), [AIAG errata note](https://blog.aiag.org/translated-aiag-vda-fmea-handbook-errata-sheets-now-available), [2nd printing (Centrum FMEA)](https://fmea.com.pl/second-print-of-the-aiag-vda-fmea-ed-1-manual/?lang=en). Wilson interval {0.565600, 0.898770} cross-computed with Wolfram Language (local Wolfram Engine, via wolframscript).

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/fmea_level_and_draft_encodings_2026-11-14_joint/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
