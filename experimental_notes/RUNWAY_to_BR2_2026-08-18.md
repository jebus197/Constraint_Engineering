# THE RUNWAY — where we are, what is left, what each step costs

**★★★ EVERYTHING IS ON HOLD PENDING NINE FOUNDER DECISIONS, 2026-08-22 03:47 BST.**
**The list is `experimental_notes/Decisions_Inventory_2026-08-22.md` (+ Desktop TTS).**
**Nothing is built and nothing is run until it is answered. This supersedes every
ordering below, including the one written two hours earlier on this same page.**

The nine, with the recommendation carried here so a recovering agent does not have
to open the file to know what is pending:

| # | decision | recommendation | blocks |
|---|---|---|---|
| 1 | discrimination gate: **block / label / retry** | **retry then block** — a filter that only subtracts turns a quality problem into a volume problem; iteration is recorded as load-bearing | the fix experiment and every future run |
| 2 | does a finding reclassified **equipment error** stop counting? | **counts as UNRESOLVED** — otherwise a run looks more converged the more its instruments fail | any future run |
| 3 | the **133 similarity pairs**: 33 machine-settled both ways, **100 still need a human** | a **stratified sample of 30**, ~1 hour, not all 100 | any claim about dedup quality |
| 4 | the **critical-severity threshold, 0.7** | **keep it**, and cite the frozen pre-registration from the live queue, which does not mention it | nothing now; a future agent could move the float blind |
| 5 | **exp50/51**: redesign before running? | **redesign** — same TRUE/FALSE pairing that contaminated exp48/49 | exp50 and exp51 |
| 6 | the **load balancer** | **retire** — never ran outside its own tests, reports impossible allocations as successes, self-description false 4.5 months | nothing |
| 7 | the **survived-falsification ledger** — verified NOT read by the runner | **withdraw the claim it exists** | nothing; records accuracy |
| 8 | the **exp46 pre-registration** draft | **do not sign** — it predates the discrimination result it must account for | the exp46 re-run, already held |
| 9 | **`.env` quoting + Zenodo token rotation** | needs the founder's own hands; open 3 days | nothing technical |

**PROCEEDING ON ONE ASSUMPTION unless told otherwise:** the archive re-grade writes
SIDECARS and modifies no archived report, per the 2026-07-29 standing rule that a
fold-forward never alters a completed experiment's record.

**AFTER the nine are answered, the order is: (a) the INSTRUMENT INVENTORY — ~17
components emit a number or a verdict and nobody has ever listed them or recorded
which are commissioned; this is what converts an apparently endless defect stream
into a finite burndown — then (b) the fix experiment.**

---

**★★ THE DISCRIMINATION CONTROL HAS BEEN RUN, 2026-08-22 03:05 BST. THE RESULT IS
THE MOST IMPORTANT NUMBER THIS PROJECT HAS. READ THIS FIRST.**

**Of 263 archived confirmations that could be tested, 132 (50.2%) are backed by a
falsifier demonstrated to fire on the accused defect and go silent on its repair.
The other 131 still fire after their own accused defect is repaired, and 128 of
those have NEVER been observed to go quiet under any condition tested.**

The pre-registered rule, taken from CC2 before the measurement: ≥95% quiet →
H-BUILD without reservation; ≥10% still firing → materially toward H-VOID.
**50.2% FAILS THAT RULE, on the H-VOID side.** It is honoured, not renegotiated.

**THE CONFOUND WAS MEASURED, NOT ASSUMED.** "Still fires" could mean the fix was
bad rather than the falsifier blind. Each still-firing falsifier was re-run against
up to 8 OTHER findings' fixes for the same file, known-substantive because each had
silenced some other falsifier. **2 of 130 (1.5%) were sensitive — their own fix
failed. 128 (98.5%) never went quiet on anything.** The bad-fix explanation accounts
for 1.5%, not 50%.

**THE MIRROR CONTROL SAYS THE PASSING HALF PASSES CLEANLY.** Of the 132, **92
(69.7%) are specific** — quiet on their own fix, firing on all 8 others. Of the 40
that were not, **35 were silenced by only 1–2 of 8**, which is the signature of
DUPLICATE findings sharing a root cause (this project's own repair adjudicator uses
exactly that as its SAME criterion). Exactly **1** is genuinely fragile. **So the
fragile population is 1–5 of 132, not 40.**

**ROUTE B IS LARGELY UNINFORMATIVE — DO NOT QUOTE ITS 3.9%.** 346 of 360 fire on
every stored version, but **126 findings went quiet on their own fix while firing on
every version**: this runner suggests fixes to a human and does not commit them, so
most accused defects were never repaired in git and a correct falsifier is RIGHT to
fire on every version. Route A is load-bearing.

**WHAT THIS DOES NOT SHOW.** Not that the design is unsound. 50% is not 0% — 132
falsifiers do exactly what the design specifies, and a design that did not work
would return near 0%, not a clean split. The failure is located in the GATE, not the
concept: `reverify_falsifier("print('FALSIFIED')")` returns CONFIRMED, because
nothing ever required a falsifier to demonstrate dependence on its target. **And the
measurement IS the repair** — `scripts/discrimination_control_archive.py` is the
filter; run it in-loop and the 131 never reach CONFIRMED.

**THE QUEUE, RE-ORDERED BY THIS RESULT:**

| # | item | why |
|---|---|---|
| **1** | **Feed the in-runner control.** `run_discrimination_control` exists with 8 outcomes and 3 self-probes; it is presence-gated on a corrected copy no panel has ever been asked for. A finding's own proposed fix is already emitted, so the corrected copy is one apply away | until it lands, no future run can tell a demonstration from an assertion either |
| **2** | **Re-grade the archive.** Stamp all 263 scored findings with their discrimination outcome: 132 demonstrated, 131 asserted | this IS Codex's typed-provenance work, and the data now exists |
| **3** | **The 67 NO_APPLICABLE_FIX and 30 INDETERMINATE_ERROR** — a quarter of the population could not be scored at all | its own finding, unexamined |
| **4** | FW.5, wire counterfactual repair to the merge site | unchanged; still true that no code path writes MERGED |
| **5** | ERROR/UNTOOLABLE can write a terminal status (4 of 24, all escalated) | small, cheap |
| **6** | `null_perturbation_control.py` needs `--dry-run` | it overwrote its own committed result on 22 Aug |

**NO LIVE RUN UNTIL ITEM 1 LANDS.** Adding runs to an instrument that cannot
distinguish a demonstration from an assertion multiplies the problem measured here.
This supersedes every run ordering below.

Full account: `experimental_notes/Discrimination_Control_Result_2026-08-22.md`
(+ plain-English companion + Desktop TTS). Data:
`experimental_notes/data/discrimination_control_archive.json` and the two
`..._cross_probe_*.json`.

---

**★ THE ORDER CHANGED, 2026-08-22 01:40 BST. READ THIS BLOCK BEFORE THE TABLES BELOW.**

A five-model panel (`Panel_Track_Record_FULL_RECORD_2026-08-22.md`, 5 of 5
returned, no compelled convergence) was asked whether the project's track record
is sound. **Four of the five named the same next step, and it is not the one this
tracker had at the top.**

**THE NEW HEAD OF THE QUEUE: run the DISCRIMINATION CONTROL on the archive,
offline, at zero cost.** Repair the accused claim; the falsifier must go quiet.
It was believed to need a live run because the in-runner version is presence-gated
on a corrected copy no panel has ever been asked for. It does not. 367 of 437
modern CONFIRMED findings carry a machine-applyable SEARCH/REPLACE fix, and CC2's
second route needs no fix at all — re-run each archived falsifier against the
commit that later fixed the defect it accuses.

**PRE-REGISTERED DECISION RULE, taken from CC2 before the measurement:**
≥95% go quiet → the modern arc is H-BUILD without reservation.
≥10% still fire → it moves materially toward H-VOID.

**WHY IT JUMPED THE QUEUE.** CC2 executed the gate rather than reasoning about it:

    reverify_falsifier("assert False, 'FALSIFIED: trivially'")  ->  CONFIRMED
    reverify_falsifier("print('FALSIFIED')")                    ->  CONFIRMED

The gate measures that a falsifier FIRED, never that it fired BECAUSE of the
claim. **0 of 2,030 archived entries carry a discrimination record** — the control
has never run once in the project's life (`discrimination_control_ask = False`,
`reference_runner_v2.py:593`). Everything else on this page is downstream of the
answer, because a transition log that records which mechanism decided is worthless
if the mechanism does not discriminate.

**WHAT THE SAME AUDIT ESTABLISHED IN THE PROJECT'S FAVOUR.** The claim CC1 made on
21-22 August that "the founding principle is unauditable on its own record" is
**WITHDRAWN**. It is false from exp42 on and true only for exp34-41, where the
mechanism did not exist — `falsifier_verdict` entered the code 2026-06-03
(`4fba6cc`), and `falsifier_gate_enabled` is unset in all 8 exp40/41 configs and
True in all 17 configs from exp42 on. Modern arc: **85.3%** of terminal verdicts
carry a recorded tool verdict, **97.4%** of closures do, status tracks the tool
verdict at **99.8%**, and 8 of 8 archived series replay exactly.

**WHAT WAS ALSO WITHDRAWN, and it was CC1's own.** The sign test on M6 (25/25,
p = 2.98e-08, then 25/26, p = 4.02e-07) is **deleted**. `apply_falsifier_verdicts`
runs AFTER `_update_finding_statuses` and overwrites status unconditionally, so
"the tool prevails" is deterministic and the p-value was arithmetic on a foregone
conclusion. The table survives as a REGRESSION CHECK — the gate was on and nothing
bypassed it — which is worth having given six model-vote paths to MERGED were found
on 19 August. And the 26 disagreements decompose 18 / 6 / 2: **"the tool overrules
the panel on truth" rests on n = 2, not 26.**

**NEW EXCLUSION: exp48 and exp49 come out of headline claims.** Answer-key
contamination already in the errata; **both target documents are deleted from disk**
so 68 falsifiers can never be re-executed; and 100% of the archive's detached
falsifiers (9 by one heuristic, 15 by CC2's) live in those two runs.

**NEW SMALL DEFECTS.** (a) A falsifier verdict of ERROR or UNTOOLABLE can still
write a terminal status: 4 of 24, two of them REFUTED with `verified=False`. All
four carry `escalated=True`, so a human saw them; the status is still wrong.
(b) `scripts/null_perturbation_control.py` writes its output unconditionally — a
read-only reviewer overwrote the committed 397-row result with a 12-row one on
22 August. Disclosed, restored from git. It needs `--dry-run`.

**VERIFIED TONIGHT AND UNCHANGED: no code path in `reference_runner_v2.py`,
`immune_agents.py` or `bench/dm/` writes MERGED at all.** Any live run started today
produces zero merges. `target_path` is a local in `run_experiment` (`:8225`-`:8231`)
and the `_update_finding_statuses` call is at `:9122` in the same function, so
FW.5 is one argument. It is now SECOND, not first: MERGED is 13 modern entries,
CONFIRMED/CLOSED is 436, and the wiring falls out of the discrimination control's
machinery anyway.

Full account: `experimental_notes/Track_Record_Audit_2026-08-22.md`
(+ the plain-English companion + Desktop TTS). Reproduce with
`python3 scripts/track_record_audit.py`.

---

**Opened 2026-08-18 11:42 BST at HEAD `f53c276`. Last updated 2026-08-18 12:28 BST at HEAD `f4df176`.**
**This is a LIVING TRACKER. Update the STATUS column as each item lands.**
**Canonical copy: this file. Mirror: `~/Desktop/CDSFL_RUNWAY.md`.**

The order below is not mine. It is what all 5 panel models independently
recommended on 2026-08-18 with no compelled convergence, and the reason is
CC2's: *"the binding constraint is not experiments, it is that the harness
cannot currently record what an experiment would show. A dedicated dedup
experiment run now measures the instrument, not the question."*

---

## THE SPLIT THAT DECIDES COST

Verified 2026-08-18: the NEAR-DUPLICATE flag is rendered into the next round's
prompt (`bench/dm/_feedback.py:393`, `:472`). So repairs divide in two, and only
one half costs money.

**ACCOUNTING fixes** change only how findings are COUNTED. Offline replay against
the archive validates them — same findings, same rounds, same targets, different
accounting. A genuine controlled before/after. **Cost: zero.**

**BEHAVIOURAL fixes** change what models SEE, so replay is invalid: it would be
replaying responses the models would no longer have given. **Cost: at least one
live run.**

---

## STAGE 1 — ACCOUNTING REPAIRS + REPLAY. Zero dispatch.

| # | Item | Evidence | STATUS |
|---|---|---|---|
| 1.1 | ~~Gate-population mismatch~~ **CORRECTED 2026-08-18 12:28: this is a rho/endocrine repair, NOT a gate repair.** `novelty_counts` was corrected in its final position only; it feeds `_compute_rho` (:8935) and the endocrine module (:9060). The gamma gate reads `_settled_novelty_series` directly (:4385-4387), which was ALREADY post-dedup in every round | 82% of merges land in a later round and are never corrected. Refutation: the runner's own settled series reproduces archived `gamma_critical_history` exactly in 9 of 11 archived runs | DONE (re-scoped) |
| 1.2 | Alias-key normalisation: `_resolve_merge_source` cannot resolve the syntax the runner itself teaches, so MERGE silently recasts to CONFIRM | spec `cdsfl_topology_formal.md:126-127` mandates the recast; the repair target is the resolver | DONE |
| 1.3 | Merge target guards: no check that the target exists, is live, or is not self | exp37 has a finding merged into itself at severity 0.86 | DONE |
| 1.4 | Merge cycle guard | 21 of 86 merged entries in exp36 sit inside a cycle | DONE |
| 1.5 | Health-monitor carve-out: suppresses the alarm when all removals are duplicates, so a 100%-rejection round reports healthy | `bench/immune_agents.py:4711-4726` | DONE |
| 1.6 | MERGED semantics: it is a delete-with-pointer, not a fold. Either make it fold, or stop telling models it folds | alias map is a bijection in **all 28 registries**; no entry has ever gained a second alias | TODO |
| 1.7 | **REPLAY exp44-49** through the repaired accounting; report old vs new rho, gamma, novelty series | archive is intact; this is how everything this week was derived | TODO |

| 1.8 | **NEW, OBSERVED 2026-08-18:** churn detector cannot fire on most of the arc. `rho_earliest_round=12`; of exp44-49 only exp44 (13 rounds) reaches R12 | exp45=4, exp46=6, exp47=9, exp48=6, exp49=7 rounds | **SHADOW 2026-08-20** — derived floor 2x window = 6 computed and logged, NOT gating. Would have refused convergence in exp46 and exp48, so promotion needs clean data from the exp46 re-run |
| 1.9 | **NEW, OBSERVED 2026-08-18:** exp47's report records 9 rounds; its registry carries `open_since_round` up to 13 | any per-round exp47 comparison spans two different lengths. An apparent rho rise of +0.2153 was an artefact of this and is WITHDRAWN | **DONE 2026-08-20** — cause found (round 5 carries 15 model files: a resume), rounds 0-4 reconstructed with unrecoverable fields left NULL |

**Stage 1 exit test:** the replay reproduces each run's archived series exactly
under the OLD accounting, and reports a defensible delta under the new. If it
cannot reproduce the old, the replay harness is wrong and nothing downstream is
trustworthy.

---

## STAGE 2 — THE BEHAVIOURAL FIX. Needs one live run.

| # | Item | Note | STATUS |
|---|---|---|---|
| 2.1 | Remove/repair the immune duplicate auto-reject | Regression dated **12 April 2026**, commit "Phase 2: Embedding similarity shared backend". Pipeline passed ~944 findings in its first 6 weeks, then 0 from round 1 of every run since | TODO |
| 2.2 | Preserve tool verdicts through synthesis | one run recorded 19 CONFIRMED + 8 REJECTED tool verdicts, final verdicts 38 DUPLICATE / 1 CONFIRMED / 1 UNCERTAIN | TODO |
| 2.3 | Validate on ONE live run (exp50 physics) | replay cannot validate this — it changes the prompt | TODO |

**Do NOT set a new similarity threshold.** Measured 2026-08-18 against 85
tool-decided labels: embedding AUC 0.608, Jaccard 0.586, stem-signature 0.433
(below chance). No threshold separates on the hard cases; sweeping 0.50->0.72
flags all 85 pairs at 47% precision, which is the base rate.

---

## STAGE 3 — THE REMAINING ARC

| # | Run | Config | STATUS |
|---|---|---|---|
| 3.1 | exp50 physics exam | `bench/exp50_configs/50_physics_exam_live.json` | BUILT, NOT RUN |
| 3.2 | exp51 biology exam | `bench/exp51_configs/51_biology_exam_live.json` | BUILT, NOT RUN |
| 3.3 | exp52 factorial cell A | `bench/exp52_configs/52_factorial_cell_A.json` | BUILT, NOT RUN |
| 3.4 | exp52 factorial cell B | `..._cell_B.json` | BUILT, NOT RUN |
| 3.5 | exp52 factorial cell C | `..._cell_C.json` | BUILT, NOT RUN |
| 3.6 | exp52 factorial cell D | `..._cell_D.json` | BUILT, NOT RUN |
| 3.7 | exp54 capstone / integration | no config yet | NOT BUILT |

---

## STAGE 4 — PROPOSED, NOT BUILT

| # | Item | Origin | STATUS |
|---|---|---|---|
| 4.1 | Clean control target, generated by script so correctness is a property of the generator | founder ruling, `Path_To_BR2_And_Open_Decisions_2026-08-13.md` | **BUILT 2026-08-20** — `bench/cdsfl_registry/targets/control_two_distinct_defects.md` + ground-truth key. Settles the CC2/DeepSeek prose disagreement. NOT YET RUN |
| 4.2 | exp53 re-run on the new clean target | same | PROPOSED |
| 4.3 | Load-balancer shakedown: panel judges whether a component should EXIST, then builds it | founder proposal, Decision 8. Brief must carry the "nine judges, two effective votes" finding so the panel starts from the constraint | PROPOSED, CAPPED |
| 4.4 | `exp49_dedup` | **DEFERRED by unanimous panel advice** — premature until Stage 1 and 2 land | DEFERRED |

---

## HELD IN RESERVE

**Full live re-run of exp44-49 with fixes in place.** Founder decision
2026-08-18: hold unless the Stage 1 replay throws up something replay cannot
account for. It would give a same-target before/after, which is a stronger design
than testing only on new targets — but it is nice-to-have, not load-bearing, and
it is the single most expensive item on this page.

---

## THE OPEN SCIENTIFIC QUESTION, unresolved and NOT blocking

Three panel models independently objected that **counterfactual repair is not
ground truth**: one broad repair can cure two genuinely different defects,
especially in the dominant absence-of-validation class. So the 85 labels may
contain false SAME labels, and DS put the consequence exactly: *"the project has
replaced a text-similarity problem with a patch-equivalence problem."*

The control that would settle it: a target carrying two KNOWN distinct defects
that share a plausible common repair. Candidate for 4.1's generator.

Until then the defensible claim is the narrow one: **free-text similarity is not
a reliable final identity decider on the hard cases.** Not "sameness is
undecidable from text".

---

## WHAT IS ALREADY DONE (do not redo)

- Parser substituting schema headers for claims — FIXED, tested, committed
- Location extractor counting cited premises as accusations — FIXED, 19 tests
- Fix parser unable to read the fix emitter's own output — FIXED, 8 contract
  tests, verified to fail against the pre-fix code
- Registry description cap 500 -> 2000 — FIXED
- Anchorless-anchor wildcard in the outcome tier — FIXED, 13 tests
- 85 of 133 disputed pairs adjudicated by counterfactual repair, zero cost
- `exp39-experimental` archived to `~/Desktop/CDSFL_archive/`, encrypted by the
  founder, restore-tested. **Remote branch NOT deleted** — 17 answer-key blobs
  reachable from it, including exp50/51/52 which are unrun.

---

## STANDING CONSTRAINTS

- No paid dispatch without explicit approval.
- No remote branch deletion without explicit approval.
- The key vault stays sealed. Exam targets are staged only for the duration of a
  run and removed in a `finally`.
- Every claim in this file is either measured (with its measurement) or marked
  proposed. Nothing here is inferred and presented as fact.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).

---

## FUTURE WORK — RECORDED 2026-08-21, having been item 9 on the 19 August list and never done

Not deferred by decision; simply never written down. Named here so they are not lost.

| # | Item | Why it is future work | Status |
|---|---|---|---|
| FW.1 | **The missing epistemic state** — a finding that was RIGHT about a target that was WRONG. Today a finding is either fixed or refuted; there is no terminal value for "the model's objection held and the claim under review is the error", which in science is the most valuable outcome available | A status value plus a pointer to the overturned claim. Cheap. The founder has ruled the Bugzilla structural fixes back IN scope (2026-08-20), so this is not deferred by choice | NOT BUILT |
| FW.2 | **Structural keying of claims** — key a finding on the structure of the claim it challenges rather than on its location in the document | Addresses a limitation the code documents at `reference_runner_v2.py:4331`: location-only keying "cannot see a SECOND distinct defect in an already-flagged function". Needs enforced structured output first | NOT BUILT |
| FW.3 | **Fingerprinting (MinHash/SimHash/LSH) scoped to the ouroboros literature cell** | Right tool, wrong component. At 27-82 findings a run, exact comparison is milliseconds; LSH earns its place at N in the thousands, which is the literature cell. Proposed twice and killed once by measurement at finding level — the scoping is the correction, not the rejection | NOT BUILT |
| FW.4 | **The discussion-board layer** | Founder ruling 2026-08-20: a UX build, expensive, unnecessary to prove the theory. Explicitly still WANTED, just not now. Work done in the meantime should aim to make it trivial to add | DEFERRED BY DECISION |
| FW.5 | **Wire counterfactual repair to the merge site** | The tool exists and costs 0.287 s/pair with no metered charge. It is not connected because `_update_finding_statuses` receives no path to the document under review — but `target_path` IS in scope in the calling function at `:8132`, so this is one argument, not an architecture change. **Until it lands, NO code path writes MERGED at all** | NOT BUILT — highest priority of these |
