# Where the failure-mode critical level sits, and whether 22 draft encodings may leave DRAFT

Record written 2026-11-14T05:22:06+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

This round put to the 2 free seats the 2 decisions owed to the founder from the encoding work of 2026-11-12: where the engineering domain's failure-mode critical level should sit when the published standard names 2 landmark bands, and which of the 22 DRAFT encodings may move to CROSS_VERIFIED.

It exists because he instructed it in the outstanding-work document: that this should also be put to the free panel for resolution, and that the result should be checked with dispassionate analysis, the 5-step reasoning cycle and the full STEM toolset before anything is applied.

WHAT CHANGED BETWEEN HIS INSTRUCTION AND THE DISPATCH, and it changes the stakes of the first question. On 2026-11-12 the critical level reached nothing: the composer made 0 calls to any severity API, so the manifest's declared scale and level were recorded and never delivered. That was repaired on 2026-11-13, so `CRITICAL LEVEL: 7` is now a sentence delivered into a working seat's directive rather than a line in a configuration file nobody reads. The first question is therefore operative rather than documentary.

WHAT WAS DONE WITH THE FINDINGS. Both seats recommend RETAINING the level at 7 and reject the move to 9, and the reasons are substantive rather than conservative: moving to 9 would exclude the case where the artefact does not work from the critical class, would demote 4 of the project's own 5 material categories below the cut, and would make engineering the only declared scale gating on its standard's maximal band. The 2nd question did not converge, 11 against 16, and 0 tier lines were written. 1 seat found a material defect neither the brief nor the project had noticed: the clinical scale declared in the manifest had been superseded about 16 months before a note there claimed it was confirmed current. That was verified against the primary 312-page document and corrected, along with a stale printing citation on the failure-mode handbook. Entry B154 records the outcome and entry B185 records the staleness mechanism.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# BRIEF — where the failure-mode critical level sits, and whether 22 draft encodings may leave DRAFT


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `bench/cdsfl_registry/composer.py` | `eb836387286a87a3` | 117190 | 2026-11-13T21:27:13+00:00 |
| `bench/cdsfl_registry/domain_manifest.toml` | `501a257dbe67e8a5` | 25184 | 2026-11-12T03:47:08+00:00 |
| `bench/directives/universal/cdsfl_core_formal.md` | `9da304edb6c80a60` | 31909 | 2026-11-12T03:58:04+00:00 |
| `bench/reference_runner_v3.py` | `9f689c6505d36c49` | 1280002 | 2026-11-13T21:28:38+00:00 |
| `experimental_notes/Panel_FULL_RECORD_Severity_Is_Ordinal_2026-11-11.md` | `097f8e02cefbf5f2` | 89373 | 2026-11-11T22:48:11+00:00 |
| `bench/convergence_location.py` | `ea76b2852c07ee8d` | 65644 | 2026-09-01T12:24:12+00:00 |

## REQUIRED SECTION 1 — The question

**2 questions, each needing its own verdict.**

**Q1. The engineering domain declares the AIAG-VDA FMEA severity scale and a critical level of 7. The published standard carries 2 landmarks, not 1: the 7-8 band is labelled HIGH, and the 9-10 band is SAFETY OR REGULATORY. Which of the 2 should the project's critical level be, and on what evidence?**

**Q2. 22 of the 51 domain encodings carry their own `SEVERITY SCALE:` line and are tagged DRAFT. Adjudicate them: which may move from DRAFT to CROSS_VERIFIED, and which may not?**

**WHY THESE 2 TRAVEL TOGETHER AND NOT SEPARATELY.** They share one cause — the encoding work of 2026-11-12 — and the founder has asked for the queue of decisions put to him to be kept small. Splitting them would put 2 items in his queue with identical context. His instruction, 2026-11-12: *"This should also be put to the free panel for resolution. Once run you should check with a, f, and sy before applying, as you should do with all panel suggested fixes."*

**WHAT CHANGED BETWEEN HIS INSTRUCTION AND THIS BRIEF, AND IT CHANGES THE STAKES OF Q1.** On 2026-11-12 the critical level reached nothing. `bench/cdsfl_registry/composer.py` made 0 calls to any severity API, so the manifest's `severity_scale` and `critical_level` were recorded and never delivered. That was repaired on 2026-11-13. Executed just now rather than asserted, `_severity_declaration("engineering", ...)` returns:

```
SEVERITY SCALE FOR THIS DOMAIN, from the project's domain manifest rather than from this encoding:
  SCALE: AIAG-VDA FMEA severity 1-10 (2019 handbook)
  LEVELS: 1 no effect; 2-3 very minor to minor; 4-6 moderate; 7-8 high; 9-10 safety or regulatory
  CRITICAL LEVEL: 7
  Report a consequence as a (value, scale-name) pair. Never average, sum or interpolate across scales.
```

So **`CRITICAL LEVEL: 7` is now a sentence delivered into a working seat's directive**, not a line in a configuration file nobody reads. Q1 is therefore operative rather than documentary, and getting it wrong now changes what a seat reports.

### The artefacts under review, by path

- `bench/cdsfl_registry/domain_manifest.toml` — the `[engineering]` block at line 288 onward: `severity_scale` at line 290, `severity_levels` at line 291, `critical_level` at line 292, `severity_scale_source` at line 293, `critical_level_note` at line 294, `encoding_tier` at line 295. The tier ladder is declared at line 132.
- `bench/cdsfl_registry/composer.py` — `_severity_declaration` and `_load_domain_directive`.
- `bench/directives/` — the 51 domain encodings in the 14 domain directories, and `bench/directives/universal/cdsfl_core_formal.md`, which tells every seat *"The ordering and the critical level are the DOMAIN's, and both arrive in your directive. Do not invent either."*
- `bench/reference_runner_v3.py` — `CRITICAL_SEVERITY_THRESHOLD` at line 10484, the live gate constant, which is a SEPARATE quantity from a domain's named critical level and must not be confused with it.

### The measured facts this round starts from

**F1. The counts, read from disk by execution rather than recalled.** 52 `.txt` files live under `bench/directives`, of which 1 is the universal layer, so **51 are domain encodings** across 14 domain directories: software 5; statistics, physics, mathematics, logistics, information_science, cross-domain and chemistry 4 each; structural, product-engineering, industrial, hardware, biomedical and biology 3 each. **22 of the 51 carry their own `SEVERITY SCALE:` line, and 22 carry DRAFT.** 10 manifest entries declare `encoding_tier`, and all 10 declare DRAFT.

**F2. The tier ladder has 4 rungs and the panel can move an encoding exactly 1.** `DRAFT`, `CROSS_VERIFIED`, `VALIDATED`, `OPERATIONAL`. The manifest states that an encoding written against published standards reaches CROSS_VERIFIED and NEVER VALIDATED, because no human has checked it. A verdict of VALIDATED or OPERATIONAL is therefore out of this panel's gift and must not be returned.

**F3. 3 of the 4 declared scales were corrected against their published standards on 2026-11-12**, which is what the research authorisation bought: CVSS v4.0 rather than v3.1; GHS Revision 11 with 5 acute-toxicity categories rather than 4; AIAG-VDA FMEA with both landmark bands named rather than 1. CTCAE v5.0 was confirmed already correct. The FMEA source is marked `[VERIFY:current]` in the manifest because the handbook is not open-access and only secondary sources were reachable — which is directly relevant to Q1 and is stated here rather than hidden.

**F4. The frozen cut is not expressible as a rank on this scale.** The round of 2026-11-11 recorded in `experimental_notes/Panel_FULL_RECORD_Severity_Is_Ordinal_2026-11-11.md` carried the project's frozen 0.7 linearly into the 4 validated scales. On CVSS it lands exactly on the High boundary at 7.0. On FMEA it lands at 7.3 — BETWEEN levels — and likewise between levels on the clinical and nuclear scales. So no reading of the frozen constant settles Q1 either way, and an argument from the constant is not available.

**F5. The direction of the change is known and it is the reason this is a question.** 7 is the CONSERVATIVE cut: it admits MORE findings as critical, which is the tighter gate. Moving to 9 LOOSENS what is admitted. Under the project's own rule, loosening a gate is the founder's ruling and not a repair to be taken from a reading of a standard. `p-pass-ambiguity-default` resolves an ambiguous constraint as HARD, which is why 7 was declared.

## REQUIRED SECTION 2 — Use the harness

Form the answer by RUNNING the machinery, not by writing about it. A seat that returns prose without having executed anything has not answered.

**The instruments that bear on these questions, and what each is expected to say.**

- **`severity`** is the subject of both questions. Call `bench.cdsfl_registry.composer._severity_declaration` for every domain in the manifest and paste what each seat would actually receive. It is expected to reveal which domains deliver a usable level and which deliver silence. A domain that delivers silence while `cdsfl_core_formal.md` forbids invention is a seat with no lawful move, and that is the defect class Q1 belongs to.
- **The two-sided gate** and **`CRITICAL_SEVERITY_THRESHOLD`**: establish by execution whether a domain's named critical level and the gate's float are 2 distinct quantities or 1. If a change to the first propagates to the second, Q1 is a gate change and is strictly the founder's. If it does not, say what the named level actually governs. Do not assume either.
- **`gamma`** and the critical-finding series in `bench/convergence_location.py`: run the series and say whether a domain's critical level enters it at all. If it does not, Q1 affects reporting and not convergence, and that bounds its consequence.
- **`nu`** and the routing of a task to a domain: an encoding at DRAFT is still composed and still delivered. Establish whether the tier is read by anything at dispatch time, or whether DRAFT is a label with no mechanism. An addition nothing reaches is not additive, and if the tier gates nothing then Q2's answer changes nothing until it does.
- **Wilson** intervals on any proportion returned. A bare count over 51 encodings without an interval is not a measurement.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. **A fix without a runnable falsifier that the seat has EXECUTED is a hypothesis, not a fix.** Report the exact command run and the output seen, pasted rather than summarised.

**WHERE THE FIX MUST BE DELIVERED.** Write it INTO the sandbox repository tree at its real path, as a file — an edited `bench/cdsfl_registry/domain_manifest.toml`, an edited encoding under `bench/directives/`, a new guard under `bench/tests/`, or a new producer under `scripts/`. A fix described in prose is not delivered, and a fix written to scratch space is destroyed when the sandbox is torn down. Rounds 5 and 6 on 2026-09-10 returned 0 source files for exactly that reason while both seats reported writing and running working code.

**ON Q1, THE FIX MUST BE A MECHANISM AND NOT A NUMBER.** A verdict of "9" or "7" on its own is a vote, and there are no votes in this project. What is wanted is the DECISION PROCEDURE: on what evidence should a project set a critical level when a standard names 2 landmark bands, and does that procedure yield 7 or 9 here? A procedure that cannot be applied to the next standard is not a fix.

**A THIRD OPTION IS AVAILABLE AND MUST BE EVALUATED RATHER THAN IGNORED:** declare BOTH landmarks — a HIGH level at 7 and a SAFETY OR REGULATORY level at 9 — and let the consumer say which it is gating on. State what that costs and whether anything in the harness can consume 2 levels today. If nothing can, say so, because then it is an addition nothing reaches.

**ON Q2, AN ADJUDICATION MUST BE PER-ENCODING AND MUST NAME ITS EVIDENCE.** A blanket verdict on all 22 is not an adjudication. For each encoding examined, name the external standard it cites, say whether that citation is current, and say whether its HARD constraints are checkable by a tool. Where fewer than 22 can be examined in the pass budget, examine as many as can be done properly and SAY HOW MANY WERE LEFT, with which ones. A silent cap reads as full coverage.

**ON COMPOSABILITY, as the founder defines it.** Compose 2 repairs ONLY on a DEMONSTRATED advantage over each alone, where the demonstration is a MEASUREMENT and not a judgement, and prefer the single repair wherever it performs as well on the named property. Reporting that the repairs do not conflict is the weak non-interference form his definition excludes by name, and will be recorded as not having answered.

**AND THE ADDITIVE STANDARD BINDS BOTH DIRECTIONS.** Declaring a second landmark is an ADDITION and must be wired to a consumer and reached by a test. Removing the conservative level is a REMOVAL and needs a committed measurement that the replacement dominates on a named property.

**A HARD CONSTRAINT ON ANY ANSWER.** Q1 may loosen a gate, which makes it the founder's ruling and not the panel's to apply. Deliver the analysis and the mechanism as files; state plainly in the verdict that the level change awaits his ruling. Do not write a changed level into the manifest as though it were settled.

## REQUIRED SECTION 4 — What would refute you

Before concluding, state what evidence would overturn the answer. A verdict with no stated refutation condition is an opinion, not a finding. Be concrete: name the file, the command, and the result that would change the verdict. For Q1, state what a reading of the primary AIAG-VDA handbook could say that would reverse the recommendation, since this brief has only secondary sources.

## REQUIRED SECTION 5 — Output shape

Return these fields, named, so replies can be compared without a parser guessing.

- `verdict` — 2 rows, Q1 and Q2, each RECOMMEND / REJECT / HOLD FOR THE FOUNDER with 1 sentence of reason.
- `q1_procedure` — the decision procedure for setting a critical level from a standard that names more than 1 landmark, stated so it applies to the next standard as well as this one.
- `q1_consequence` — measured: what a move from 7 to 9 would change, in what it admits and in what reaches a seat's prompt.
- `q2_table` — 1 row per encoding examined: domain, cited standard, citation current yes or no, HARD constraints tool-checkable yes or no, verdict DRAFT or CROSS_VERIFIED, evidence.
- `q2_coverage` — how many of the 22 were examined and which were not. A silent cap is a defect.
- `tier_mechanism` — whether the tier is read by anything at dispatch time, with the command that establishes it.
- `falsifier` and `falsifier_result` — the runnable falsifier and its pasted executed output.
- `reasoning` — the derivation, premises first.
- `disagreement` — the strongest disagreement with this brief's own framing, including with F5's claim that 9 loosens the gate. A concurring answer carries no information here, because there are no votes in this project.
- `plain_english` — 1 paragraph a non-specialist can act on.
- `passes_run` — how many passes were run and what the last one added.

## REQUIRED SECTION 6 — Termination

Stop at diminishing returns: when a further pass produces no new above-threshold finding, where above-threshold means missing it could cause a real-world failure, an unsafe condition, or a wrong level reaching a working seat. State how many passes were run. Do not pad with findings below that threshold.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 59 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel fmea_level_and_draft_encodings_2026-11-14) -->

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

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 41 recorded tool call(s).

<!-- verbatim-begin: fable (panel fmea_level_and_draft_encodings_2026-11-14) -->

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

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/fmea_level_and_draft_encodings_2026-11-14/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
