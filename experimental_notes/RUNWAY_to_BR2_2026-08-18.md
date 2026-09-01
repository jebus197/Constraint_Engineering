# THE RUNWAY — where we are, what is left, what each step costs

> **★ STATUS 2026-08-24 00:30 BST. CORRECTED — THE ARTICLES ARE NOT LOST.**
> An earlier line here said the Stage 3 targets were "not on this machine". That was a
> SEARCH FAILURE, not a data loss, and it is withdrawn. The configs point at STAGING
> names (`PX-12-REF-05.md`, `BX-14-REF-04.md`, `SW-14-REF-01.md`); in the repository the
> same articles are `exp50_physics.md`, `exp51_biology.md` and `exp52_factorial.md`. All
> three recover from local history at `ddd74bde^` and reproduce the target MANIFEST's
> published hashes exactly; all five answer keys are at `eecdb0f^`.
>
> **What actually blocks Stage 3 is a ruling, not a build.** The articles and their keys
> were committed to a branch that was public on GitHub for a period. That branch is now
> gone from the remote (`git ls-remote origin` returns only `main`, and neither commit is
> an ancestor of it), so the live route is shut — but anyone who cloned during that window
> holds them. Whether Exp 50/51/52 may still be reported as blind exams is a scientific
> judgement about that window. The target MANIFEST asked for that ruling on 2026-08-08 and
> has not received it.
>
> **The 23 August work did NOT advance this runway** and should not be counted as though
> it did. It repaired defect H08, reachable only from `55_v3_control.json`, a config
> written the previous day; zero arc configs use the relative path form that triggers it.
> It also repaired three defects in the mechanical acceptance gate. Real work, none of it
> on this list.
>
> **The nearest item that can actually be done is 1.7** — replay exp44-49 through the
> repaired accounting. Zero dispatch, no missing files, and it is Stage 1's exit test.

> **★★★ THE HOLD IS LIFTED. ALL NINE WERE RULED ON 2026-08-22 AT 16:49 BST, COMMIT `d713379`.**
> **Do not act on the hold below — it is answered, and the table under it records the
> recommendations put TO the founder, not the rulings that came back.** The rulings are
> appended at the foot of `experimental_notes/Decisions_Inventory_2026-08-22.md` under
> *FOUNDER RULINGS, 22 August 2026*, and three of the nine changed shape there:
> **#1** use the mechanism that already exists (retry → stronger model → HIL), **#3**
> re-routed so tool-undecidable pairs enter the normal guarded HIL queue and the 30-pair
> sitting is WITHDRAWN, **#6** SHELVE the load balancer rather than retire it, and **#7**
> reverses the recommendation below — the survived-falsification ledger is to be WIRED,
> not withdrawn.
>
> **The work this block gates was then done the same day.** The instrument inventory it
> names as the next thing to build landed at 17:41 BST in `239d5c8`
> (`scripts/instrument_inventory.py`, `experimental_notes/Instrument_Inventory_2026-08-22.md`,
> 34 instruments). Spot-checked in code 2026-08-24: ruling 1 is live —
> a discrimination failure now writes `NON_DISCRIMINATING` / `verified=False` /
> `escalated=True` and demotes CONFIRMED to UNCONFIRMED at `reference_runner_v3.py` § `entry["falsifier_verdict"] = "NON_DISCRIMINATING"`,
> which is what carries it into `_apply_routing`'s existing `escalated=True, not CONFIRMED`
> trigger; ruling 6 is marked SHELVED in `docs/ARCHITECTURE.md`,
> `bench/dynamic_management.py` and the inventory; ruling 7's ledger is wired at
> `reference_runner_v3.py` § `def attach_survival_ledger`, called with `ledger=survival_ledger`.
>
> **Line numbers in this tracker were replaced by anchor text on 2026-09-01.** Four citations were checked against the runner and all four were wrong: the `NON_DISCRIMINATING` write by 534 lines, the keying limitation by 1,897, the ledger wiring and the `discrimination_control_ask` default by more again. The 2026-09-01 rename rewrote the *filename* in these citations from v2 to v3 while carrying the old line numbers over verbatim, which made stale pointers look freshly checked. An anchor survives edits above it; a number does not. See 0C.19 and 0C.19a.
>
> **Why this marker exists.** The block below was written at 03:47 on 22 August and the
> rulings arrived that afternoon. This file was edited twice on 24 August (`46024a1`,
> `79abe37`) and the block was not touched, so it went on declaring the project frozen
> pending answers that already existed — while a SEPARATE list of nine new decisions
> accumulated in the 24 August handover, which cites these rulings nowhere. Two decision
> surfaces, neither pointing at the other. Marked superseded 2026-08-24 03:31 BST.

**★★★ EVERYTHING IS ON HOLD PENDING NINE FOUNDER DECISIONS, 2026-08-22 03:47 BST.**
**The list is `experimental_notes/Decisions_Inventory_2026-08-22.md` (+ Desktop TTS).**
**SUPERSEDED — see the block immediately above. Retained as the record of what was ASKED.**
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
has never run once in the project's life (`reference_runner_v3.py` § `discrimination_control_ask: bool = False`). Everything else on this page is downstream of the
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

**VERIFIED TONIGHT AND UNCHANGED: no code path in `reference_runner_v3.py`,
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

| 1.8 | **NEW, OBSERVED 2026-08-18. FIGURE CORRECTED 2026-08-23.** churn detector cannot fire on most of the arc. `rho_earliest_round=12`. The original row said "of exp44-49 only exp44 (13 rounds) reaches R12"; **re-measured 2026-08-23 that is exp44 (13) AND exp47 (14), so 2 of 6, and 5 of 11 across exp42-49.** The row was written before exp47's missing rounds were reconstructed on 2026-08-20, so it was stale rather than wrong. At the derived floor of 2 x window = 6, **9 of 11** runs would qualify | exp45=4, exp46=6, exp47=9, exp48=6, exp49=7 rounds | **SHADOW 2026-08-20** — derived floor 2x window = 6 computed and logged, NOT gating. Would have refused convergence in exp46 and exp48, so promotion needs clean data from the exp46 re-run |
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
| 3.1 | exp50 physics exam | `bench/exp50_configs/50_physics_exam_live.json` | **BUILT, NOT RUN.** Article recovers from `ddd74bde^` as `exp50_physics.md` (29,378 bytes, hash matches the MANIFEST). Staging name in the config is `PX-12-REF-05.md`. Blocked on the held-out-status ruling, not on the file |
| 3.2 | exp51 biology exam | `bench/exp51_configs/51_biology_exam_live.json` | **BUILT, NOT RUN.** Recovers as `exp51_biology.md` (27,931 bytes, hash matches). Blocked on the same ruling as 3.1 |
| 3.3 | exp52 factorial cell A | `bench/exp52_configs/52_factorial_cell_A.json` | **BUILT, NOT RUN.** Recovers as `exp52_factorial.md` (23,740 bytes, EXACT hash match — the manifest's 'fully exposed' row). Blocked on the same ruling as 3.1 |
| 3.4 | exp52 factorial cell B | `..._cell_B.json` | **BUILT, NOT RUN.** Recovers as `exp52_factorial.md` (23,740 bytes, EXACT hash match — the manifest's 'fully exposed' row). Blocked on the same ruling as 3.1 |
| 3.5 | exp52 factorial cell C | `..._cell_C.json` | **BUILT, NOT RUN.** Recovers as `exp52_factorial.md` (23,740 bytes, EXACT hash match — the manifest's 'fully exposed' row). Blocked on the same ruling as 3.1 |
| 3.6 | exp52 factorial cell D | `..._cell_D.json` | **BUILT, NOT RUN.** Recovers as `exp52_factorial.md` (23,740 bytes, EXACT hash match — the manifest's 'fully exposed' row). Blocked on the same ruling as 3.1 |
| 3.7 | exp54 capstone / integration | no config yet | NOT BUILT |

---

## STAGE 4 — PROPOSED, NOT BUILT

| # | Item | Origin | STATUS |
|---|---|---|---|
| 4.1 | Clean control target, generated by script so correctness is a property of the generator | founder ruling, `Path_To_BR2_And_Open_Decisions_2026-08-13.md` | **RUN TWICE 2026-08-23 as Exp 55.** Both halted at round 0 on the irreducible-queue alarm, 1152 s and 1178 s. Cause was the falsifier gate running every falsifier in an empty working directory (defect H08), reachable only because this config used a REPO-RELATIVE target path — the one form neither the gate nor `_retarget_falsifier` supports, and the only prose config of eleven that did. Fixed `0c93e2b` by the founder's absolute-path ruling. **A third run has not been attempted.** |
| 4.2 | exp53 re-run on the new clean target | same | PROPOSED |
| 4.3 | Load-balancer shakedown: panel judges whether a component should EXIST, then builds it | founder proposal, Decision 8. Brief must carry the "nine judges, two effective votes" finding so the panel starts from the constraint | PROPOSED, CAPPED |
| 4.4 | `exp49_dedup` | **DEFERRED by unanimous panel advice** — premature until Stage 1 and 2 land | DEFERRED |

---

## STAGE 4B — THE BR2 BRIDGE. **Immediately before BR2. Recorded 2026-08-27 00:04 BST.**

**Placed here on the founder's ruling of 2026-08-26: after the arc and the open decisions, immediately before BR2.**

**BR2 IS the external target source, and it was specified on 8 April 2026** — 27 frontier STEM tasks across 8 domains. A discussion on 26 August briefly reasoned about external targets as though they needed inventing; that was wrong and BR2 is the answer to it.

### The tasks are NOT the gap. They exist.

**MEASURED 2026-08-26.** All **27** encodings are present in `bench/tasks_frontier/`, `ft-001.json` … `ft-027.json`, median **5,096 bytes**. Domain spread: mathematics 7, software 6, cross-domain 5, chemistry 3, hardware 2, structural 2, industrial 1, physics 1. Every one carries `id`, `domain`, `title`, `prompt`, `ground_truth_notes`; **26 of 27** also carry `verification_method`, `why_frontier_hard` and **`expected_single_pass_accuracy`** — a pre-registered prediction written months before any run, which is exactly what a hostile reviewer looks for. **One of the 27 uses a different schema** (`hard_constraints` / `soft_constraints` / `status` instead) and needs reconciling.

### INCONSISTENCY 1 — the tasks are wired to a runner generation we replaced.

```
reference_runner_v3.py   last commit 2026-08-26   references tasks_frontier   0 times
run_benchmark.py         last commit 2026-04-13   consumes them
run_phase2.py            last commit 2026-03-19   consumes them
run_experiment.py        last commit 2026-03-18   consumes them
run_round_robin.py       last commit 2026-08-15   consumes them
```

**BR2 as currently wired would run on machinery predating the two-sided gamma gate (10 June), the falsifier-gate hardening, location-keyed convergence, the v3 patches (23 August), and every fix of 16–26 August.** The entire Exp 40–55 arc hardened a runner BR2 would not use. **This is the work, and it was on no stage, in no queue, and had never been named.**

### INCONSISTENCY 2 — [OPEN] prompt and ground truth share a file, in all 27.

`prompt` and `ground_truth_notes` sit in the same JSON object in **every** task. That is the structure that removed exp48 and exp49 from every headline figure and burned exp55's target three days before it ran.

**Labelled [OPEN], not [MEASURED]:** it has NOT been shown that any loader stages ground truth into a model prompt. What is shown is that the structure permits it, in all 27, and this project has been bitten by that exact structure three times. **Splitting the keys needs nothing from the rewiring and can be done at any time, for free.** **DONE 2026-08-27 (item 4B.1)** — 14,528 characters across all 27 moved to `CDSFL_experiment_keys/br2_keys/`.

**★ FOUNDER RULING 2026-08-27 on the fact that they were already public since 2026-03-18 (162 days): NON-ISSUE.** BR2 has never run, so the exposure never reached a run; the repository has never been cloned; and splitting before the first run is precisely the lesson exp48, exp49 and exp55 taught. CC1's alarm was disproportionate and is withdrawn. An answer key matters only if it can reach a run.

### The work, in order

| # | Item | Cost | Note |
|---|---|---|---|
| 4B.1 | **Split `ground_truth_notes` out of all 27** into the outside key store | zero, offline | Do NOW — needs nothing from 4B.2 |
| 4B.2 | Reconcile the one off-schema task to the 26-task schema | zero | |
| 4B.3 | Wire `reference_runner_v3` to the frontier schema | zero dispatch | Decide how `verification_method` maps onto the falsifier gate |
| 4B.4 | **C5 — dry-run all 27 for tool availability, graceful degradation, answer leakage** | zero dispatch | In the 8 April plan, never done |
| 4B.5 | Live burn-in on **ONE** BR2 task | 1 BR2 task | Validates 4B.3. Does NOT consume internal runway |
| 4B.6 | **Audit the 27 targets for prose/markdown documents that print fenced code listings** | zero, offline | Founder ruling 2026-08-30. A falsifier about such a document must quote the listing, so its own source carries three backticks. The extractor was repaired that day and now survives 7 reply shapes plus both self-fenced fixtures — but the RE-ASK path uses the same transport, so if any of the 27 is that shape it wants one live check, not just a unit test |
| 4B.7 | ~~Gemini has no tool path~~ **CLOSED 2026-08-31** | done | Google function-calling implemented on the `google` route (Gemini's FAILOVER route and the one `decomposed_dispatch` uses; its PRIMARY route was openrouter, which already had tools -- an earlier report of "Gemini has no tools" mapped it to the wrong function and is corrected). Verified with ONE PAID CALL, not by inspection: asked for the Wilson interval of 126/246, it returned 0.4500, 0.5740 to 4dp in 6.4s, obtainable only by running statsmodels. |
| 4B.8 | **Vault the seeded pairs for the cell build-out exams** | zero, offline | Founder, 2026-08-31: *"The seeded pairs from the upcoming cell build out exams on the runway have not yet been vaulted as far as I know. But this is not a blocker to the simulated run. It is easily fixable after this run."* CORRECTION TO A CLAIM MADE THE SAME NIGHT: `vault_keys.sh status` reported "VAULTED" and that was read here as the whole key-material question being closed. It is not. That command scans `$CDSFL_STORE` and `$CDSFL_LEGACY_STORES` and reports on "any known or scanned location" (vault_keys.sh:114-124) — seeded pairs created for exams not yet in those stores are outside its scan set entirely, so a clean status says nothing about them. Do after the current simulated run. |

### Runway calculus after 4B

Internal shots remain **three**: exp50 physics, exp51 biology, exp52 factorial — and exp52 is a 2×2, so it spends 4–5 runs as ONE experiment. exp53 needs a re-run; exp55's target is spent. Stage 2 already books exp50. **4B costs roughly one BR2 task, not internal runway.**

### ★ THE INFINITE-LOOP QUESTION, and a stopping rule instead of an argument

The founder's concern, 2026-08-26: BR2 becomes a shakeout test in its own right, generating its own defects and fixes, and the project never terminates.

**MEASURED — machinery commits to `bench/` between consecutive live runs:**

```
exp43  10    exp46  4    exp49  0    exp55  32   <- v3 runner, FIRST run
exp44   1    exp47  7    exp53  0    now    26
exp45   4    exp48  0
```

**The decay was real and then broke, and the break has a cause: a new instrument generation resets the defect curve.** Caveat, stated: commits-between-runs is a proxy confounded by cadence — exp48 and exp49 ran 100 minutes apart, so their zeros mean "no time to fix", not "nothing to fix". The **32-commit spike after a new runner generation** is the clean signal.

**Consequence for BR2: 4B.3 creates a new instrument generation. Running BR2 immediately after it means running at the PEAK of a fresh defect curve** — the trap precisely located.

**The escape is not more hardening. It is refusing to let BR2 absorb the shakeout.** The free simulated experiment (founder decision 7) plus the 4B.5 burn-in are the shock absorber, and both are cheap.

**STOPPING RULE, pre-registered here rather than argued later:** after 4B, run the cheap probes. **If the fix curve flattens across two consecutive probes, the generation is stable enough to spend BR2 on. If it does not flatten, that is the answer — bought for the price of a simulated run rather than 27 real ones.** This is the project's own diminishing-returns criterion applied to the project.

---

## STAGE 5 — THE REVIEWER REPRODUCTION PACK. **The final item. After BR2.**

**Recorded 2026-08-24 20:54 BST on founder instruction, so it is not lost. Status: DEFERRED BY DECISION.**

**Founder ruling (2026-08-24 20:54):** defer. *"You can't build a test suite for something that is yet to be built."*
Sharpened in discussion, and this is the operative reason: the pack would technically work today,
because it reproduces measurements that are already complete. What defeats it is that **the set of
headline numbers is still moving** — the discrimination result is days old, Stage 1's exit test has
only just landed, exp50/51/52 have not run, and BR2 supersedes much of it. Assembling now creates a
SECOND ESTATE pinned to a snapshot that is about to change, which is the drift failure this project
hit twice on 2026-08-24 (a RUNWAY hold left standing after it was lifted, and `MEMORY.md` line 31
carrying a figure the file it pointed at had never held).

**Trigger:** after BR2, and not before handover item 9 clears — nothing publishes while the branch
cannot push.

### 5.1 — What it is, and what it is NOT

Three different things get called a test suite and they cost wildly different amounts. Naming them
apart is the point of this row.

| | what it is | state |
|---|---|---|
| (a) software suite | proves the harness code does what it says | **EXISTS** — `bench/tests/`, 3840 passing. Wrong audience: it tests the instrument, not the theory |
| **(b) reproduction pack** | lets a reviewer re-derive the project's published numbers, offline, free | **THIS ROW.** Largely exists already and is invisible |
| (c) theory-testing kit | lets a reviewer apply CDSFL to their own artefact | **OUT OF SCOPE, deferred past BR2 with no date.** Needs keys and paid dispatch, and — the real objection — a strange result from it would be uninterpretable: neither party could tell a refutation of CDSFL from an unvalidated instrument. That confusion has already happened once, when a mis-specified zero-plant control read as a substantive false-positive result |

### 5.2 — The asset that already exists and is signposted NOWHERE

**This is the part that must not be lost.** Eight scripts regenerate headline numbers at zero cost.
Verified 2026-08-24 by reading each: **zero network references, zero dispatch references, zero key
references**; five read only the local archive. Meanwhile the only signposted route for an outsider
is `docs/REPRODUCING.md`, which is organised around *Prerequisites → Running an Experiment → Cost
Estimates* and carries 16 references to API keys and paid dispatch. **The cheap path exists and the
expensive one is the only one documented.**

| script | reproduces |
|---|---|
| `scripts/replay_accounting.py` | Stage 1's exit test — 8 of 8 archived series reproduce exactly |
| `scripts/discrimination_control_archive.py` | the 132-of-263 discrimination result |
| `scripts/track_record_audit.py` | 85.3% of terminal verdicts carry a tool verdict; 97.4% of closures |
| `scripts/instrument_inventory.py` | 34 instruments, and the detector that scored itself wrong |
| `scripts/null_perturbation_control.py` | 397 findings, 360 fired, 0 moved on an irrelevant change |
| `scripts/harness_defect_rate.py` | the harness-defect rate curve |
| `scripts/competence_provenance.py` | the routing-ladder provenance guard |
| `scripts/note_vagueness_lint.py` | the note-standard vagueness check |

### 5.3 — Design constraints agreed 2026-08-24, before anything is built

1. **The explorer is the FRONT DOOR, not the backbone.** Zero install, zero cost, works without
   Python, gives a reviewer something to hold in thirty seconds. But it demonstrates one stage's
   internal dynamics at d = 1 and says in its own words that it is not evidence. A pack centred on it
   leads with the least evidential artefact in the project. **The eight scripts are the spine,**
   because they regenerate measurements and measurements are what a reviewer came to attack.
2. **Runnable things plus one short index. Links, never copies.** A folder that accumulates copies of
   explanatory documents becomes a second documentation estate that drifts from the first. One copy
   of every explanation, always.
3. **Point at the instruments, not at their outputs.** A list of scripts stays true when the numbers
   move; a list of numbers rots. Same lesson as the `MEMORY.md` index line.
4. **Two README links, different jobs:** one near the top of the 540-line README (the anti-wading
   fix — adding *more* to that README cannot itself be the fix), and one in context at the end of §6
   after the mathematical core, before §7. §11 is the natural home for the reproduction link, since
   that is where a sceptical reader goes.

### 5.4 — The smallest useful version, if it is ever wanted early

Twenty lines in `docs/REPRODUCING.md` listing the eight scripts, one line each, naming what each
reproduces and **not quoting any value**. Creates no new estate and does not rot. Offered and
deferred 2026-08-24 20:54; recorded here rather than lost.

---

## STAGE 6 — OUTREACH. **Also after BR2. Recorded 2026-08-24 21:57 BST.**

**Status: DEFERRED BY DECISION, same slot as Stage 5.** Founder policy, recorded in persistent
memory and honoured since: outreach begins only once Genesis, OpenBrain and CDSFL are near
complete, because *"starting outreach before finishing would be a distraction and risk never
completing the work."* First emails were planned for **2026-03-17**; that date passed and the hold
was kept deliberately. It is discipline, not slippage.

### 6.1 — What already exists, and what it is NOT

| document | date | what it actually covers |
|---|---|---|
| `~/Developer_Projects/Outreach.docx` | 2026-03-21 | **The substantial one.** ~48,500 characters. Verified-contact dossier: Hinton, Bengio, Russell, the IASR network, each with role, fit rationale, interests, and published contact addresses |
| `~/Developer_Projects/outreach_plan.md` | 2026-02-07 | **Candela / Guardian, NOT CDSFL** — Mini-BERT, on-chain anchoring, Sepolia. Predates this repo by five weeks |
| `~/Developer_Projects/Gemini Candela Outreach.docx` | 2026-02-07 | Candela again |
| `Project_Genesis/cw_handoff/OUTREACH_STRATEGY.md` | 2026-03-07 | Genesis |

**Do not treat the February files as a CDSFL plan.** Two of the four are for a different project.

### 6.2 — The agent's role, and the line it does not cross

Founder question, 2026-08-24 21:57: whether an autonomous agent can handle most of the initial outreach. The
concern behind it is **volume**, and the volume concern is well founded — a tailored approach to
each name in the dossier is more drafting than one person completes by hand.

**Agreed split: the agent researches, drafts, tracks and prepares. The founder reads and sends.
Every time.**

Three reasons, and the first is the one that would be raised publicly:

1. **The medium would refute the message.** The pitch is a methodology for keeping AI work honest
   and human-supervised. Delivered autonomously to Stuart Russell, who works on bounded oversight,
   it contradicts its own thesis in the act of announcing it.
2. **This project's own architecture forbids it.** CDSFL keeps the human in the loop for decisions
   that carry consequences. Autonomous sending is the project violating its own principle.
3. **These contacts are one-shot and non-renewable.** A failed experiment re-runs; a first email to
   Hinton does not. In a small field the impression does not reset.

Separately and independently: an assistant cannot send on the founder's behalf without explicit
per-message permission, so a fully autonomous sender is not available regardless of the argument.

### 6.3 — What the agent SHOULD do. This is the volume answer.

1. **Freshness pass.** The dossier is five months old; affiliations move. Re-verify every contact
   and role before anything sends. Unglamorous, high-value, exactly what an agent is for.
2. **Per-target preparation, never templating.** Read each person's recent output, identify the
   specific overlap, draft the one paragraph proving they were actually read. Ten tailored openings
   is agent-days and human-minutes; ten templated ones are worthless.
3. **A tracker that is generated, not maintained** — who, when, what was said, what came back. This
   file's own history is the argument: three separate stale-document defects on 2026-08-24 alone.
4. **Materials**, pointing at the Stage 5 reviewer pack rather than at the 540-line README.

### 6.4 — Reorder the ladder. Do not open with Hinton.

Persistent memory already names the **Stanford/Harvard POPPER team** as priority contact: nearest
methodological neighbour, complementary statistical approach (e-values against this project's
Bayesian R_k), most likely to engage on substance, and a survivable place to learn what lands.
Work up from there. Building the ladder is agent work; deciding it is the founder's.

---

## STAGE 7 — DOCUMENTATION CANNOT CLOSE BEFORE PoC FINAL. **Recorded 2026-08-24 23:22 BST.**

**Founder position, 2026-08-24 23:22:** the README and many project documents are *not complete and cannot be*
until final proof-of-concept status is reached. There will almost certainly be more to say. This row
exists so that "the README is finished" is never inferred from the fact that nobody has edited it.

### 7.1 — ★ THE COUPLING INTRODUCED ON 2026-08-24, WHICH WILL ROT IF NOTHING WATCHES IT

**README section 11 and the opening block are now the same content at two depths.** On 2026-08-24 a
short block was added at README line 11, above section 1, stating what the project supports strongly
and what it names as open. It is a faithful condensation of **section 11**, which sits at line 473.

**If section 11 changes and the opening block does not, the front page states a superseded
conclusion in the most prominent position in the project.** That is not a hypothetical failure mode;
it is the same shape as all three defects found on 2026-08-24 — a RUNWAY hold that outlived its
rulings by two days, a `MEMORY.md` line pointing at a figure its target never held, and a Desktop
mirror 127 lines stale. Every one of them was a copy or a derivation that nothing checked.

**BR2 will change section 11.** Its "remains open" list explicitly includes whether the strongest
emergence claims survive larger and harder datasets, which is what BR2 tests. So this coupling is
guaranteed to be exercised, not merely at risk.

**NOT BUILT:** a check that the opening block and section 11 have not diverged. Recorded as not
built rather than claimed.

**Provenance, recorded because this project counts these.** The coupling was introduced by CC1 on
2026-08-24 *while repairing a different instance of the same class* — the front page was reordered
to surface the project's limitations earlier, and the reordering created a second copy of them.
`scripts/harness_defect_rate.py` already records that all eleven harness defects to date were
authored by CC1; this is a twelfth of the same lineage, disclosed at the moment of creation rather
than found later.

### 7.2 — What else must be revisited when the PoC closes

| item | why it will need changing |
|---|---|
| README §11 and the opening block | BR2 answers part of the open list. Both, in lockstep |
| The discrimination control result | 132 of 263 is the most concrete self-found limitation the project has and it postdates §11, so it appears in neither. Deliberately left out on 2026-08-24 rather than smuggled into the front page |
| Test and experiment counts throughout | every figure carries a date and a commit and ages the moment either moves |
| The explorer's own README | its calibration proposal becomes either done or refuted once the archive fit is attempted |
| `START_HERE.md` | the three-minute map describes a project whose arc stops at experiment 49 |

### 7.3 — Recommendations accumulated 2026-08-24, all post-BR2 unless marked

1. **Do not announce before BR2.** Topics and a homepage URL are catalogue hygiene, reversible, and
   were applied on 2026-08-24. An *announcement* — a post, a mailing list, a link from anywhere with
   traffic — is one-shot. Someone arriving now meets an arc that stops at 49 and nine open rulings;
   after BR2 they meet the same project with its central question answered.
2. **Zenodo over social.** A citable archived deposit with a DOI reaches people who cite rather than
   people who scroll, and it is the right register for this work. Partly set up already — the token
   rotation is decision nine on the founder's desk.
3. **Put the closed-form floor into the Mathematical Appendix.** The appendix states only the bound
   `lim R ≥ ν` at line 232 and gives no closed form. Solving the Stage 5 recursion for its fixed
   point yields `R* = ν / (q(σ + ν(1−σ)))`, which is `ν/q` at σ = 1, so detection quality MULTIPLIES
   the floor and the bound is tight only at q = 1. Verified 2026-08-24 by SymPy plus 40-decimal-place
   iteration agreeing to twelve decimals, valid inside the convergent regime. **This is a small new
   result and it currently lives only in a note and a tool.**
   **And a second, added 2026-08-25 00:14: the crossing is a TRANSCRITICAL bifurcation.** `R = 1` is a fixed point
   for all parameter values (verified symbolically), so nothing annihilates; the interior fixed point
   crosses it exactly where ν crosses ν\* evaluated at `R = 1`, and the two exchange stability. Measured
   at σ=1, ν=0.05: at q=0.20 the interior point sits at 0.25 and attracts while |f′(1)|=1.188 repels; at
   q=0.03 the interior point has left [0,1] and |f′(1)|=0.979 attracts; at the crossing the multiplier at
   `R = 1` is exactly 1.000. An earlier description of this as a saddle-node collision was WRONG and is
   withdrawn — a fold destroys both fixed points, and these persist. The six anomalies in the 600-point
   sweep all sat within ~1e-3 of this boundary, which is expected near a transcritical crossing and was
   at first mistaken for measurement error. **The appendix classifies the crossing nowhere.**
4. **The three checks that are available and NOT BUILT**, each recorded as not built: that the note
   standard version named in the project instructions matches the version named in memory (these
   drifted two versions and four months); that each document's declared Desktop mirror matches its
   canonical copy (the runway's was 127 lines stale); and deriving the memory ledger inside `sv`
   instead of typing it (seven consecutive manual bumps, two in one session).
5. **An archive scheme for the TTS folder.** Roughly four hundred files going back to March sit in
   one directory the founder reads from. Offered 2026-08-24 and not taken up; recorded so it is not
   lost.

### 7.4 — Editorial principles for the final pass, established 2026-08-24 23:35 BST

Recorded because they were argued out in discussion and would otherwise survive only in a transcript.

1. **Length is not the problem; ordering is.** The two have opposite remedies — "too long" says cut,
   "badly ordered" says re-sequence and keep everything. The README is 12,047 words, which is a long
   journal article and defensible for the content. **Do not cut it.**
2. **The audience triages; it is not short of attention.** Frontier researchers read enormous
   quantities of difficult material under inbound volume that forces rationing. A document gets about
   sixty seconds to establish it deserves an hour. This is the actionable diagnosis; "attention spans
   have collapsed" is not, because it leads to writing it anyway rather than to earning the hour.
3. **Lead with the limitations.** To this audience a project that states plainly what it has NOT
   established is doing something almost nobody does, so the open list buys more trust in thirty
   seconds than forty minutes of argument can. Applied on 2026-08-24; keep it applied.
4. **Open with the concrete and earn the abstraction.** *Origin of Species* is 150,000 words and its
   first chapter is pigeon breeding. Darwin opened with the most checkable thing he had and earned
   the theory rather than leading with it.
5. **State the convention, never the stance.** Never write that the project is careful or does not
   over-claim; that is an unfalsifiable assertion about oneself of exactly the shape this project
   exists to catch. Labelling is governed by note standard v1.6 Rule 26, used sparingly — peppering
   reads as irrational doubt rather than as care.
6. **Describing the explorer publicly.** Two analogies, each covering half. The Sinclair Executive
   for the FORM — an existing capability made portable rather than a new capability added, which is
   what it did to Stage 5. An engineering design chart drawn *before its correlation was calibrated*
   for the EPISTEMIC STATUS — the mathematics is right, the chart is usable, and the experimental
   programme that would say whether it describes anything real is the one still to run. Neither
   analogy alone is honest. Full argument in *Assessment of the Stage 5 Explorer*, 2026-08-24.
7. **A note on where the new result came from.** The closed-form floor at 7.3 item 3 was found by
   *using* the explorer rather than by reading the appendix. That is the strongest available argument
   for the tool earning a place in the documentation, and it is worth stating when the tool is
   described.

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
| FW.2 | **Structural keying of claims** — key a finding on the structure of the claim it challenges rather than on its location in the document | Addresses a limitation the code documents at `reference_runner_v3.py` § `KNOWN LIMITATION, unchanged: location-only keying`: location-only keying "cannot see a SECOND distinct defect in an already-flagged function". Needs enforced structured output first | NOT BUILT |
| FW.3 | **Fingerprinting (MinHash/SimHash/LSH) scoped to the ouroboros literature cell** | Right tool, wrong component. At 27-82 findings a run, exact comparison is milliseconds; LSH earns its place at N in the thousands, which is the literature cell. Proposed twice and killed once by measurement at finding level — the scoping is the correction, not the rejection | NOT BUILT |
| FW.4 | **The discussion-board layer** | Founder ruling 2026-08-20: a UX build, expensive, unnecessary to prove the theory. Explicitly still WANTED, just not now. Work done in the meantime should aim to make it trivial to add | DEFERRED BY DECISION |
| FW.5 | **Wire counterfactual repair to the merge site** | The tool exists and costs 0.287 s/pair with no metered charge. It is not connected because `_update_finding_statuses` receives no path to the document under review — but `target_path` IS in scope in the calling function at `:8132`, so this is one argument, not an architecture change. **Until it lands, NO code path writes MERGED at all** | NOT BUILT — highest priority of these |

---

## STAGE 0C — INSTRUMENT COMMISSIONING. **Recorded 2026-09-01 12:15 BST. Zero dispatch except where noted.**

The 31 Aug – 1 Sep simulated-rehearsal arc commissioned the rehearsal harness and, in doing so, found defects in the **shared** runner. Of 12 code fixes in the arc, **8 touch `reference_runner_v3.py` / `runner_core.py`** — the runner real experiments use — and only 2 are simulation-only. The simulation is not a fork: `RUNNER_VERSION = "v3.2"` lives in the one runner file, and the sim launcher imports it. The harness patches one function (the dispatch primitive) and wraps the real runner.

### What was found and closed

| # | Finding | Status |
|---|---|---|
| 0C.1 | **A model could delete a finding by repeating itself.** `auto_resolve_contested` counts verdict ROWS, not distinct models; `add_verdict` never deduped. One model, one reply, three CHALLENGE lines auto-refuted a severity-0.9 finding. **Pre-existing at HEAD**, verified from git. | Closed by per-reply dedupe + five-label whitelist. **+651 verdicts recovered, 9.7%** of all verdicts, Wilson [9.00%, 10.42%] |
| 0C.2 | **The parser dropped panel findings.** Four of six agents' replies parsed to zero. Two faults coincided: no arm accepted a markdown-heading finding, and the fallback was suppressed by two guards that were each correct about their own case. | Closed. Rehearsal round 0: 4 → 17 findings, 2 → 6 of 6 agents |
| 0C.3 | **The heading pattern also matches a Python comment**, minting spurious severity-0.5 findings from pasted transcripts — **12 across real June 2026 replies** | Closed by a per-heading content test |
| 0C.4 | **Panel agents write to the canonical repo during runs**, including the experiment's own target. Not simulation-specific: 30 archived runs targeted repo code under the same inheritance | Closed for simulated runs by sandboxing; **OPEN for real runs** — see 0C.9 |
| 0C.5 | **Simulated replies were counted as real archive.** 9 of 11 simulated run directories carry no `runner_state.json` (81.8%, Wilson [52.3%, 94.9%]), so they were misfiled as pre-v3 real history | Closed at record level via the `-SIM` marker |
| 0C.6 | **The pre-registered threshold profile (F6) was never built.** `CRITICAL_DEFINITION_PREREG_2026-05-18.md` requires γ at 0.5/0.6/0.7/0.8 and a rubric-disagreement count. **0 of 50 archived real reports carried one** | Built at `48d6254`; **defective, see 0C.10** |
| 0C.7 | **The verdict tally counted verdict ROWS across rounds.** One model challenging the same finding in three consecutive rounds refuted it alone — a self-consensus path in a project that does not confirm or delete findings by vote at all | Closed 2026-09-01: counts distinct models. Archive exposure **1 of 66** findings carrying ≥3 CHALLENGE rows was REFUTED/CONTESTED with <3 distinct challengers (1.5%, Wilson [0.3%, 8.1%]). An earlier **22.7% was an over-statement** — it counted by row regardless of eligibility for auto-resolution |
| 0C.10 | The threshold profile as shipped was defective — `gate_would_fire` reimplemented a gate appearing nowhere in the runner | Closed at `c58b03e`. The reimplementation is gone; the profile now reports `inputs_vary_with_threshold` and `gamma_range_across_thresholds` and asserts nothing about firing |
| 0C.11 | **Sandbox blinding was defeated by construction** — the worktree carried `bench/logs/**`, so exp45's 12 criticals **with severities** were readable inside the frozen tree | Closed at `c58b03e` by pathspec staging (founder ruling 2026-09-01); `bench/logs/`, `bench/results/` and `experimental_notes/` are excluded from the sparse checkout |
| 0C.12 | **WITHDRAWN as a standing ruling, 2026-09-01.** It said a simulated run is permanently barred from severity, threshold and **convergence** claims. It never had the standing it was given: it arrived as a two-model panel convergence, THIS TABLE recorded it as *"needs a standing ruling"*, and it was then written into commit `bb8d54b` **as** a STANDING RULING without reaching HIL — a model vote promoted to a rule, in a project whose founding principle forbids exactly that | **Founder ruling 2026-09-01:** *"remove that clause that prevents you from reporting when that is the case. It seems to serve no purpose other than to confuse you and me."* The blocking clause is gone. What survives, correctly scoped: simulated severity **magnitudes** are uncalibrated and do not transfer. Readiness reporting from a simulated run is now explicitly PERMITTED in the report itself |
| 0C.16 | **The panel harness accepted a non-verdict** — a reviewer returned 54 characters against a median reply of 7,512 and the harness recorded `ok=False` and kept it | Closed 2026-09-01. **Worse than recorded here:** the retry fired on *neither* an empty reply (`CircuitBreakerTripped` is re-raised immediately) nor a short one (`return text`, untested). Now an `accept=` predicate inside the retry loop; default `None` leaves every existing caller unchanged |
| 0C.17 | **Runner name and version disagreed** — `reference_runner_v3.py` carrying `RUNNER_VERSION = "v3.2"` | Closed 2026-09-01 at `ce08914`: renamed to `bench/reference_runner_v3.py`, 191 files rewritten. The filename now carries the major version and the constant the minor. `experimental_notes/` deliberately **not** rewritten — those notes describe the file as it was named when written |

### What is OPEN and needs work

| # | Item | Evidence | Priority |
|---|---|---|---|
| **0C.8** | **Rubric-adherence audit of the boundary.** Never done. Sample ~200 findings in [0.65, 0.75), score against the five consequence clauses **blind to the numeric**, report concordance. The only legitimate way to test 0.7 without moving it | 401 findings (5.84%, Wilson [5.31%, 6.42%]) sit exactly on 0.70; 72.1% [71.0%, 73.1%] are quantised to a 0.05 step, so severity is ordinal | **HIGH** — 1–2 days, no live run |
| **0C.9** | **Real runs still inherit the repo.** The sandbox closed this for simulated runs only. **Detection half closed 2026-09-01**; the confinement half is a behavioural change to live experiments and is held for panel review | `set_panel_cwd(cfg.panel_cwd or None)` leaves panel cwd unset for code runs, deliberately. The mid-run mutation guard is now exercised (see 0C.20) but remains **detective only** — it cannot prevent the write, and whether to remove model write access is a founder ruling | **HIGH** |
| **0C.13** | **Panel independence is unverified.** One reviewer measured the simulated panel's between-model variance as **zero after noise correction** (observed 0.000139 < sampling noise 0.000910) against a real-panel 0.0255 — "five seats, one voice". If true it threatens what a "panel" result means, beyond severity | Unverified by me | **HIGH** |
| **0C.14** | **The discrimination-control evidence base is overwhelmingly simulated.** 84 of 95 scored records (88.4%, Wilson [80.4%, 93.4%]) come from simulated runs. A reviewer's structured count was starker, and reported 50.2% DISCRIMINATES against a pre-registered ≥95% bar — **I could not verify this: the file cited does not exist, only the script that generates it** | Verified for the 88.4%; the 50.2% is UNVERIFIED | **HIGH** — argues for routing the control through a real run |
| 0C.15 | **Canary seeding: BUILT, TESTED, AND NOW USED.** `bench/canary_seeding.py` had 42 passing tests and had never been wired into a run, because no catalogue existed for it to read | Closed 2026-09-01. A catalogue of 5 real defects in `bench/dm/_memory.py` across 2 generators now lives outside the repo, seeding is wired into the sandboxed harness after the history is severed (the ordering matters — `seed()` refuses a target inside a git work tree), and the run of 2026-09-01 used it. **The row's own note that it carries no severity field still stands**: it measures recall, not calibration |
| **0C.18** | **The exp39-experimental bundle is a single point of failure.** 676 commits; the only copy system-wide is `~/Desktop/CDSFL_archive/exp39-experimental-2026-08-17.bundle.enc` (86.8 MB), unversioned, on a Desktop | Verified by system-wide search | **MEDIUM** |
| **0C.19a** | **The 0C.19 sweep ran, and its result is that the sweep cannot detect 0C.19.** 974 typed `file.py:NNNN` citations exist in tracked non-log files. **Zero** name a missing file (the 10 apparent hits are all test fixtures: `bench/real.py:42`, `bench/x.py:41`) and **zero** point past the end of the file they name. But line 11002 sits comfortably inside a 12,128-line file, so the ledger's own 1,068-line error would pass this check | The only mechanical detector for the class is anchoring: match the citation to the text it refers to and derive the number, which is what was done for the ledger. **A typed line number is unverifiable by construction** | **MEDIUM** — the exposure is 974 citations, none of them checkable as written |
| **0C.19** | **A document that verifies against its own generator verifies nothing.** `EXPERIMENT_RUN_LEDGER.md` opens "DERIVED. Every figure below is read from the artefacts, never typed", and cited line 11002 of `reference_runner_v2.py` — the file's name at the time; written out of `path:line` form deliberately, so that it reads as the historical measurement it is and no checker mistakes it for a live pointer — for a comment that a text search located 1,068 lines further down. Both numbers are stated here as **historical measurements taken at commit `ce08914^`**, not as pointers: neither is valid against the current file, and that is the point of the finding. Its test compared the ledger against the generator's own hard-coded copy of the same wrong number, so two copies of a typo agreed perfectly | Fixed for this citation: generator and test both derive the line from the runner source, and the generator raises rather than guessing if the anchor comment is rewritten. **The class is open** — no sweep has been done for other assertions that compare a derived document against its generator rather than against the source | **HIGH** — cheap to sweep, and it silently voids a "DERIVED" claim |
| **0C.20** | **Silent guards, and how to tell them from dead ones.** The mid-run target mutation guard was recorded here on 2026-09-01 as never having fired. **That was wrong, and CC2 refuted it in panel review the same day.** The claim rested on 0 of 83 run directories carrying `target_integrity_events` — the violation-gated key. The unconditional sibling `target_hashes` is written one line below it: **9 run directories carry it across 38 hashed rounds.** The guard has executed 38 times and been correctly silent every time | CC2's triage rule, adopted: (1) unconditional write with 0 occurrences means unreachable as configured; (2) violation-gated write plus an unconditional sibling present in ≥1 run means reachable and correctly silent; (3) violation-gated write with no sibling and 0 occurrences is genuinely ambiguous. **Only category 3 is actionable, and the fix is to give every guard an unconditional "I ran" counter beside its alarm** — which converts all future ambiguity to category 1 or 2 for free. The cross-run false alarm found and fixed on 2026-09-01 was therefore reachable, which makes that fix more load-bearing, not less | **HIGH** — the most expensive error in the review was a working control recorded as dead |
| **0C.21** | **New tests can look green without ever running.** Three regression files written this session landed in a root `tests/` directory the suite does not collect. They passed when invoked directly and would have contributed nothing to the suite count | Moved to `bench/tests/` before commit. **The class is open** — nothing checks that every test file in the tree is reachable by the suite's collection roots | **MEDIUM** — one collection-coverage test closes it |

| 0C.22 | **Seats are not models — and the figure I published was wrong.** The tally counted distinct seat LABELS while `Codex` and `ChatGPT` declare one model | Published: 21/103 = 20.4%. **That denominator double-counted**: each run's registry appears in both its report and its `runner_state.json`, and one run directory is a symlink to another. Re-measured on the deduplicated corpus (47 registry-bearing directories, symlinks resolved — I said 46 and dropped `logs_quarantine`, which contributes 0/0; of those, 44 are distinct runs and 39 are real, since two pairs are byte-identical duplicates): **11/47 = 23.4%, Wilson [13.6%, 37.2%], Clopper-Pearson [12.3%, 38.0%]**. Identity is now keyed on **(model_id, api)**, not model_id alone — see 0C.29 | **CLOSED 2026-09-01** |
| **0C.23** | **A length floor rejects a terse conclusion.** The 0C.16 predicate rejected anything under 800 characters, which would retry a reviewer who genuinely had nothing to add — spending dispatches re-asking an answered question | CC2's concrete example, `[NO_NOVEL_FINDINGS]`, is **not a token in this codebase** (no such literal in `bench/`), so that exact reply could never have been rejected. The class is real: a short reply is now accepted when it carries an explicit verdict marker or is a bracketed all-caps token, and rejected otherwise. The 54-character holding note is still rejected | **CLOSED 2026-09-01** |
| **0C.24** | **The only tested cost control has never written a byte, and the current runner has none.** `bench/cost_ledger.py` is imported by exactly one file — its own test. Its `totals()` schema (`dispatches`, `metered_dispatches`, `unmetered_dispatches`) appears in **zero** archived artefacts; all four archived `cost_ledger.json` files carry the schema of two untested shadow copies in `run_phase2.py` and `run_round_robin.py`. `UNMETERED_ROUTES`, which exempts the flat-rate Max `claude_cli` route from the cap, exists only in the module and its test | Found by CC2. **Its severity framing needs correcting:** the shadows last wrote in **March 2026**, and `reference_runner_v3.py` has **zero** cost or cap references, with **zero** cost artefacts from any exp40+ run. So this is not "real spend tracked by untested code" — on the path actually in use, spend is tracked by **nothing**. Whether the current runner should meter at all is a founder scope call, not a fix | **NEEDS YOUR RULING** |
| **0C.25a** | **The latent-control audit is BUILT.** `scripts/latent_control_audit.py`, 12 seconds, offline, stdlib only. It reads report keys from the runner by AST, counts them across 82 archived reports, and classifies by CC2's triage rule. It independently reproduced the `target_integrity_events` refutation — **SILENT_BUT_RAN, witness `target_hashes`** — without being told, which is the error it exists to prevent. Age control quarantined the 3 keys committed that day as TOO_NEW rather than reporting the session's own work as dead | Standing findings: **2 UNREACHABLE** (`hierarchical_crit_series_error`, `stalled`), **5 AMBIGUOUS** — of which `burst_phases` and `hil_paused_at_phase` corroborate CC2's report, and `reason`, `tier`, `terminate` are known false positives from matching any local named `result`. The tool over-reports by design; that limitation is stated in its own docstring | **CLOSED 2026-09-01** — the remaining 0C.25 gates still need measuring |
| 0C.25 | **The nine gates, NAMED.** The count was recorded from a reviewer without naming its members — the exact vagueness this project has a standing rule against, and the founder called it | Re-measured against all 43 configs: of 23 boolean `RunnerConfig` fields, **9 are set true by no config**: `discrimination_control_ask`, `discrimination_control_blocks`, `hierarchical_novelty_convergence`, `hil_review`, `immune_memory_consume_rk0`, `latent_tagger_enabled`, `resume`, `severity_calibration_enabled`, `stall_gamma_termination_enabled`. **The reviewer's headline is REFUTED by execution**: a config setting all nine reaches the runner with 8 of 9 true on the launcher path and 9 of 9 via `--config`; only `resume` is unreachable, because the launcher overwrites it from `args.resume`. `burst_phases`, which the reviewer named, is not a config field at all | **HIGH** — remove or wire, but the count is no longer vague |

| **0C.26** | **Uncommitted runner work, standing register.** A live worktree at `/private/tmp/cdsfl_review_89557` (HEAD `657b02c`) holds **143 insertions / 4 deletions across 2 files** that exist in no commit: 100 insertions in the runner and 43 in `falsifier_verify.py`. `/private/tmp` clears on reboot, and it is the only copy | **Assessed 2026-09-01 and both halves are SUPERSEDED.** The runner half is the reviewer's own draft of the fix-efficacy wiring; the adopted `fix_efficacy_decision()` implements the same feature, and the proof is that all 8 of the reviewer's own commissioning tests now pass against it in the suite. The `falsifier_verify.py` half adds `_main_work_tree()` for the worktree `INTEGRITY_VIOLATION` problem, which the founder ruled on differently the same day — Option B, `CDSFL_CANONICAL_REPO`, live at `_allow_roots`. Adopting it would give the same widening a second route | **NEEDS YOUR RULING** — recommendation: discard and prune. Not pruned here; it is the only copy and deleting it is yours to call |

| **0C.27** | **0C.11 WAS NOT CLOSED. The blinding was defeated a second time, by history.** Pathspec staging removes the archive from the WORKING TREE; a linked worktree's `.git` points at the main object store, so the whole archive stayed readable by `git show`. Measured from inside a sandbox that had just printed *"blinded: 0 files"*: exp45's report yields **39 entries, 39 severities, 12 critical at ≥0.7, exact values 0.82 / 0.80 / 0.80 / 0.80 / 0.80 / 0.78 …** — the reference outcome this simulation is compared against, one command from agents that carry Bash | The file-counting guard could never see it: it counts files in a tree they were deliberately removed from. **Every simulated run to date was measured through this, including the round-4 convergence of 2026-09-01.** Closed: the run now happens in a plain copy, `--exclude=.git`, worktree removed before dispatch, and the script **aborts** if `git rev-parse` still answers inside the run directory. Also unblocks canary seeding, whose `seed()` refuses a git work tree for the same reason | **CLOSED 2026-09-01** — the prior 0C.11 closure was premature |
| 0C.28 | **REFUTED by the run it predicted.** It asserted a simulated run *cannot* converge non-vacuously "by construction", because the critical arm needs severity ≥ 0.70 and simulated severity clusters near 0.46 | The canary run of 2026-09-01 converged at round 3, `CRITICAL_QUIESCENCE_CONVERGED (two-sided gate): gamma_critical=1.000 >= 0.3`, with **zero** occurrences of VACUOUS and **12 of 22 findings at severity ≥ 0.70** (54.5%, Wilson [34.7%, 73.1%]). The prediction failed because it held the target constant: seed genuinely severe defects and the panel rates them severely. **Vacuity was a property of a clean target, not of simulation** | **CLOSED 2026-09-01** |

| **0C.29** | **The Codex/ChatGPT contrast was real, and it lapsed silently.** The founder recalled the two seats once being differentiated and asked when that stopped. It was **route-based**, not prompt injection: Codex ran via `codex exec`, carrying OpenAI's own hidden agent prompt, while ChatGPT ran bare via OpenRouter with CDSFL as the system message — same weights, two instruction conditions, a designed contrast in `bench/EXECUTION_PLAN_EXPERIMENT_11.md` § Diversity Axes | **Lapsed 2026-04-02, commit `556e0af`** (*"Run 6: switched from codex_exec to openrouter"*), for sound reliability reasons, and the difference went unrecorded. Measured either side: pre-lapse 78 paired rounds, 356 vs 479 findings, **sign test p = 0.00515**; post-lapse 205 paired rounds, 270 vs 251, **p = 0.378**. Today the two configs differ in **1 field of 12** (the label) and the composed directive text is byte-identical. The prompt-injection remedy the founder remembered is in the record too — approved and **never built** (`OUTSTANDING_QUEUE_to_BR2.md:279-281`) | **NEEDS YOUR RULING** — restore the contrast, or accept four architectures and say so |
| **0C.30** | **Canary detection, MEASURED.** Previously reported as unmeasurable post-hoc; that was wrong. The seeded text reconstructs byte-exactly from the catalogue (its sha256 matches the report's `target_hashes` for all four rounds), and 20 of 22 findings carry executable falsifier code (90.9%, Wilson [72.2%, 97.5%]) | Replaying all 20 falsifiers against seeded and clean text under the module's own kill criterion: **14 of 20 meet it** (70.0%, Wilson [48.1%, 85.5%]); **3 of 5 canaries killed**, and **all 3 held-out canaries killed (3/3)** — the split `detection_rate` reports `p_hat` on. Per seat on held-out: CC2 3/3, ChatGPT 3/3, DeepSeek 3/3, Codex 2/3, Gemini 2/3, **Fable 0/3** (binomial p = 0.0214 against the pooled 72.2%, but **does not survive correction for six seats**, 0.05/6 = 0.0083; n = 3 per seat) | **CLOSED 2026-09-01** — the two misses are tracked as 0C.31 |
| 0C.31 | **Two seeded defects missed by all six seats — ANSWERED, and it was mine.** Four independent angles agree: MIXED, weighted heavily to the catalogue author | **The decisive measurement:** seed each plant alone and run this project's own 135-test memory suite. MEM-01 → 4 failed, MEM-02 → 3 failed, MEM-03 → 12 failed. **MEM-04 → 135 passed, 0 failed. MEM-05 → 135 passed, 0 failed.** Our own instruments cannot tell the two missed plants from clean code, so a blind reviewer cannot fairly be expected to. Compounding it: MEM-04 sat in `compute_source_hash`, which the target's own header (line 29) declares *"UNUSED. Nothing calls compute_source_hash"* — three seats cited exactly that to exclude the site, and **zero of 22 findings targeted it**; and the seeding **deleted the file's only token of evidence for the invariant it broke**, since the `sorted()` call WAS that evidence. The detection the catalogue did measure was docstring-vs-code differencing: 17 of 22 descriptions quote the adjacent docstring (77.3%, Wilson [56.6%, 89.9%]). **Not unavoidable** — killing falsifiers were written for both and verified through `reverify_falsifier`. **Residual model component, real but small:** `sorted(` appears 0 times in all 24 replies, two seats rewrote the seeded line verbatim, and one examined `provenance_complete`'s `>=` by name and cleared it in prose without writing the two-line falsifier | **CLOSED 2026-09-01** — catalogue v2 rebuilt to five written fairness criteria |

| **0C.32** | **The withdrawal of 0C.12 stopped at the payload.** BOTH panel reviewers found it independently, and CC2 named the shape: *"the same shape as the `target_hashes` sibling — the checked artefact was cleaned, the unchecked sibling was not."* Three channels went on asserting the withdrawn bar while the suite stayed green: the function's own docstring (*"PERMANENTLY barred"*, plus a **false** *"founder-adopted"*), a runtime `_log` line emitted on **every** simulated run citing 0C.12 *as a standing ruling*, and the test module's docstring. **The console barred what the report permitted** | Closed 2026-09-01. All three corrected, the false provenance is now named and disowned rather than repeated, and `TestTheWithdrawalReachedTheSIBLINGS` guards all three channels — because a guard that inspects only the returned dict is how this happened | **CLOSED** |
| **0C.33** | **My seat-identity statistics are WITHDRAWN — they never reproduced.** I published *"pre-lapse 78 paired rounds, sign test p = 0.00515; post-lapse 205 paired rounds, p = 0.378"* | **Neither reviewer could reproduce any of the six numbers**, and no script computing them exists anywhere in the repo — they appear only as prose. The analysis was also wrong in kind: rounds within a run share target, prompt lineage and accumulated findings, so they are not independent trials. **Run-level: sign test p = 0.6875, Wilcoxon p = 0.156, paired t p = 0.588.** It was pseudo-replication. And *"205 post-lapse rounds"* is the **entire archive including pre-lapse runs** — the whole dataset mislabelled. A confound makes it unattributable regardless: pre-lapse the Codex seat was dispatched **decomposed** far more often, so the route change altered dispatch mechanics and output length, not only the instruction condition. **What survives is enough**: the mechanism is documented, the route change is in the diff, and the two seats are byte-identical today. The design conclusion needs no p-value | **CLOSED** — struck from code, tests and this table |
| **0C.34** | **The latent-control audit's simulated-run filter was a dead conditional** — `if <cond>: pass` — so it excluded nothing and simulated reports counted as archive. Found by fable | The consequence was **circular**: the three keys the tool reported as SEEN were seen *only* because the canary rehearsal's own report sits in `bench/logs`, and it sits there **twice** via a duplicated run directory. A tool built to find *"controls nobody has seen fire"* was accepting the runner's own rehearsal, double-counted, as evidence they had fired. Fixed; the witness set drops 82 → 73 reports and those three keys correctly revert to TOO_NEW | **CLOSED** |
| **0C.35** | **Commissioning the comparison is not commissioning its input.** Mutating `min(stamps)` → `max(stamps)` in the audit's dating function survived the entire suite while flipping 3 of 50 verdicts — including `target_hashes`, the witness key from the original refutation, quarantined by a corrupted date with nothing going red. Cause: every test read `first_committed` out of the tool's **own** output and re-applied the comparison to it | Closed 2026-09-01 by pinning `registry`'s first-commit epoch from git, independently of the tool. Both reviewers' surviving mutants now die. **CC2's residual stands open**: nothing constrains behaviour *at* the boundary — `>` vs `>=` vs `> newest + 1` are still indistinguishable to this suite | **MOSTLY CLOSED** — boundary case open |
| **0C.36** | **A seat that fails over to its secondary is still counted as its primary architecture.** CC2 proposed the converse — that a mid-run `api` change splits one seat into two voices — and that is **REFUTED**: `model_identity` is built once per run keyed by `label`, and `dataclasses.replace` keeps `mc.label`, so the seat resolves to one identity throughout. Fable's residual is the real one | Two seats failing over to a shared backup would count as two distinct models while **one architecture voted twice** — the 0C.22 error re-entering through the failover door. `route_used` is already recorded per reply, so the fix is in-band. Also minor: identity values are not case-normalised, so `OpenRouter` vs `openrouter` in two configs would over-separate | **OPEN** |
| **0C.37** | **Over half the raw findings are absorbed by aliasing, and one correct catch died that way.** Measured on the canary run: 23 of 45 raw findings absorbed into 22 canonical entries (51.1%, Wilson [37.0%, 65.0%]). Dedupe is the point of aliasing, so the rate alone is not the finding | The finding is that fable traced **the one parsed `compute_source_hash` catch to a registry alias collision** — so even a correct detection had a live path to oblivion, independent of whether the reviewer saw the plant. Needs a content comparison on the absorb path, not an ID match | **OPEN — HIGH** |

| **0C.38** | **The irreducibles were REAL, and the alarm fired on a transient.** The v2 canary run HALTED at round 0: *"3 criticals are locked as irreducible, over the bound of 2 … 3 of 3 carry no falsifier at all"* | **All three were correct catches of seeded defects.** C0001 (sev 0.95) and C0013 (0.88) both quote `if exp_id in self._experiment_ids and allow_reingest:` — the MEM2-REINGEST plant; C0014 (0.75) is MEM2-PIMEM. All three carried `falsifier_verdict: UNTOOLABLE` **at the moment the alarm evaluated**, and all three finish the run **CLOSED / CONFIRMED with falsifier code present**. The residual-clearing sweep tooled them. So this is neither "genuine irreducibles" nor "broken machinery": **the alarm evaluates before the falsifier path has finished tooling, and a bound of 2 is reached by findings that are minutes from being toolable.** Its own text forbids the obvious fix — *"Do NOT raise max_irreducible_queue to clear this — that is how the same alarm was suppressed twice on 2026-08-01 while it was right"* — so the fix is to evaluate after tooling, or to exclude transiently-UNTOOLABLE items, and it is a gate-adjacent change that must go to the panel first | **OPEN — HIGH**, and do NOT raise the bound |
| **0C.39** | **Catalogue v2 measured detection rather than docstring-diffing, and the panel passed.** Under v1 the killed plants all sat beside a docstring stating the invariant they broke; v2 removed that crutch | **4 of 5 plants NAMED** (80.0%, Wilson [37.6%, 96.4%]): both easy controls, the medium guard inversion (MEM2-REINGEST, 4 separate entries), and — the result that matters — **MEM2-CUSUM, a hard plant with no adjacent formula**, where the negative CUSUM arm is clamped from below so downward drift becomes permanently undetectable. Only MEM2-RESET, the incomplete state reset requiring round-trip reasoning, went unnamed. Final registry: 16 entries, **16/16 carrying falsifier code** (100%, Wilson [80.6%, 100%]), all CLOSED/CONFIRMED | **CLOSED** — naming is not killing; a formal kill score needs the counterfactual replay |


### The calibration design, and why it is a scope question rather than a resource one

The claim that calibration needs ~44 distinct model architectures is **a methodological error, and it was mine** — the power calculation used the finding-level standard deviation (0.218) as the noise term for a model-level effect. The comparison is inherently **paired**: the same defects rated by both panels. Pairing removes "how bad is this defect", which is most of that variance.

Measured on the one paired target available (exp45 vs sim45, per-seat means, statsmodels + scipy):

| paired targets | paired obs | 95% CI on the offset | power |
|---|---|---|---|
| 1 (today) | 5 | [0.022, 0.290] | 0.68 |
| **2** | 10 | [0.079, 0.233] | **0.98** |
| 3 | 15 | [0.096, 0.216] | 0.999 |

**Two paired targets take the offset from borderline to decisive.** exp50, exp51, exp52 and exp54 remain unrun; running each as a pair (real and simulated on the same target) yields the calibration **as a by-product of the runway**, requiring no additional models and no separate campaign.

Caveat that survives regardless: calibration buys **deltas**, never **levels** (0C.12).

### Additions to FUTURE WORK

| # | Item | Why it is future work |
|---|---|---|
| FW.6 | **Harvested historical revisions as a recall target.** One reviewer argues these *dominate* seeded targets: a seeded target measures the intersection of real defect-space with the author's imagination, whereas the 676-commit branch carries defects that actually occurred, with ground truth already attached — archived findings plus their executed falsifiers | The other reviewer favours seeding; unresolved, and the branch must be secured first (0C.18) |
| FW.7 | **Severity is a vote, not a tool.** A reviewer's observation, and the sharpest of the arc: the convergence gate depends on a model-assigned float in a framework whose founding principle is that votes do not decide. The real/sim gap is a symptom; the model-priced float gating convergence is the condition | Structural. Not actionable without a design decision on what would replace it |

