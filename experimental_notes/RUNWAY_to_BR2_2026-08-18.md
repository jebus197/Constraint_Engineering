# THE RUNWAY — where we are, what is left, what each step costs

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
