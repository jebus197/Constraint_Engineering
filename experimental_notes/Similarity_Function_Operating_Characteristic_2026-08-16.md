# The Similarity Function: Operating Characteristic, and Two Defects It Exposed

2026-08-16, 23:42 BST. Technical version. A plain-English companion and a TTS
file accompany this note.

> **[Correction 2026-08-17.]** Two claims below were superseded within 24 hours by
> `Description_Truncation_Three_Fixes_2026-08-17.md`. They are left standing rather
> than edited, because a note that quietly rewrites its own refuted claims is worth
> less as a record than one that carries them.
>
> 1. **Section 4's truncation-harm association is WITHDRAWN.** The pooled odds ratio
>    of 10.5 at Fisher p = 2.07 x 10^-5 was flagged here as NOT ESTABLISHED because it
>    reversed under stratification by run. That hedge was right: on repaired text the
>    same measurement gives **p = 0.272**. The pooled figure was an artefact of the
>    degraded text it was computed on.
> 2. **Section 4's framing of the two caps is INCOMPLETE, and section 2's operating
>    points were computed on damaged input.** The `[:500]` registry cap is not
>    storage-only — it is read by the location-keyed convergence count and by the CC2
>    verification pass. Re-derived on repaired text the figures move: pairs 438 → 460,
>    tier-3 coverage 94 → 110, AUC 0.986 → 0.976. What does NOT move is every
>    load-bearing conclusion: P(merge | genuinely different) 14.5% → 14.9%, zero false
>    splits, an 84% reduction against location keying alone, and tier 3 wrong on all
>    three of the decisions it changes.
>
> The anchorless-wildcard fix in section 3 stands, and its root cause is now known: the
> anchorless `(0.6, '')` existed because the parser had substituted a schema header for
> C0063's claim, cutting off the word `double-penalty`. With the parser repaired the
> same finding parses to 175 characters and yields `(0.6, 'double')`.

## Summary

The similarity function's justifying measurement was rebuilt from the archive and
reproduces exactly. Building the operating characteristic it had never had then
exposed two defects in the rule it was measuring, one of which is fixed and
tested, and one of which needs a ruling.

- **[FIXED]** `quantities_agree` treated a MISSING anchor as a wildcard, so an
  anchorless number matched any number of equal value. This was tier 3's entire
  operative error on the archive: 3 merges, 0 correct. Fixed, 13 new tests,
  suite green.
- **[NEEDS YOUR RULING]** 63% of all archived finding descriptions are stored
  truncated at a round-number cap, and 1284 of them end mid-word. The similarity
  function reads the truncated form. Fixing this changes parsing for every future
  run, mid-arc.
- **[NEEDS YOUR RULING]** The 120 pairs the recorded measurement dropped are
  extracted and waiting. Nothing here is authoritative until they are adjudicated.

## 1. What was built

`scripts/similarity_operating_characteristic.py`. **BUILT**, **TESTED** at 10
passing in `bench/tests/test_operating_characteristic.py`, not yet committed at
time of writing.

It rebuilds the 438-pair dataset from the six archived reports, reproduces the
labels offline with the sentence-embedding backend, and computes the things a
p-value cannot tell you.

### Why it was needed

The measurement justifying the similarity function — 438 same-location critical
pairs, medians 0.559 against 0.000, Mann-Whitney p = 1.9 x 10^-25 — existed
**only as prose comments** in `bench/convergence_location.py`. No stored dataset,
no script, no test. The claim and its evidence lived in different places, so the
claim could outlive the evidence with nothing reporting a problem.

That gap is now closed. Every recorded figure reproduces from the archive:

| Figure | Rebuilt | Recorded |
|---|---|---|
| criticals | 165 | 165 |
| tier-2 coverage | 161 | 161 |
| tier-3 coverage | 94 | 94 |
| same-location pairs | 438 | 438 |
| labelled same defect | 28 | 28 |
| labelled different defect | 290 | 290 |

One subtlety cost real time and is now pinned by a test. The 438 figure uses
**every** critical in the registry, not `_gate_population`, which filters
terminal-non-novel entries and was added on 2026-08-12 — after the figure was
recorded. Rebuilding through the gate population gives 423 pairs, not 438. Anyone
re-deriving this will reach for the gate population, get 423, and wrongly conclude
the recorded number was an error.

## 2. What the operating characteristic shows

### Discrimination is genuinely strong

AUC 0.9864, 95% confidence interval [0.9569, 1.0000].

The interval resamples **findings**, not pairs. The 438 pairs come from 139
findings, so one finding appears in many pairs and their errors are correlated.
Resampling pairs directly would treat correlated observations as independent and
give an interval far too narrow — the standard way pairwise evaluations overstate
their own precision.

### The operating point, which nobody had measured

At the live threshold of 0.20, P(merge | genuinely different) = 14.48%.

| Threshold | False merges | Rate | Recall |
|---|---|---|---|
| 0.15 | 48/290 | 16.55% | 100.00% |
| **0.20 (live)** | **42/290** | **14.48%** | **100.00%** |
| 0.30 | 12/290 | 4.14% | 92.86% |
| 0.40 | 4/290 | 1.38% | 82.14% |

### And the reading that looks alarming until you check the comparator

Of the 73 pairs the rule merges, 45 are labelled different defects. Merge
precision is 38.4%.

That sounds like a broken rule. **It is not**, and reporting it without the
comparator would be as misleading as omitting it. Tiers 2 and 3 act only *within*
an already-flagged location, so the baseline — location keying alone — merges
every one of these pairs unconditionally. Its false-merge count is 290 of 290.

| | Merges | False merges |
|---|---|---|
| Location keying alone | 318 | 290 (100% of different-defect pairs) |
| Plus the similarity function | 73 | 45 (84% fewer) |
| False splits introduced | — | **0** |

The rule cuts false merges by 84% and has never split a same-defect pair on this
archive. Precision is low because the base rate is skewed — only 8.8% of these
pairs are the same defect — not because the discriminator is weak.

### The three-way rule you approved

| Split ≤ | Merge ≥ | Merge (wrong) | Refer to human | Split (wrong) |
|---|---|---|---|---|
| 0.05 | 0.40 | 27 (4, 14.8%) | 72 (22.6%) | 219 (0, 0.0%) |
| 0.10 | 0.50 | 24 (3, 12.5%) | 70 (22.0%) | 224 (0, 0.0%) |

A referral rate around 22% buys a false-merge rate of 12–15% on the automatic
merges, against 14.5% for the current all-or-nothing rule at 0.20. **The gain is
smaller than it looks** and this is not yet a recommendation, because these
numbers are scored against embedding labels.

## 3. [FIXED] The anchorless wildcard

**OBSERVED.** `quantities_agree` read:

```python
if a1 and a2 and a1 != a2:
    return _distinctive(v1)
return True
```

When *either* anchor was empty the guard was skipped and it returned `True`. An
anchorless quantity matched any quantity of equal value.

### Why no existing test saw it

Tier 3's recorded justification is its **answer distribution**: Fisher exact
p = 1.4 x 10^-7, and it never once called a same-defect pair DIFFERENT. Both true.
Neither measures the quantity that matters.

Routed through `identity_decision`, tier 3 **changed the outcome on 3 of 318
labelled pairs, and all 3 were wrong**:

| Pair | Label | Embedding |
|---|---|---|
| exp47 C0020/C0063 | DIFFERENT | 0.479 |
| exp47 C0041/C0063 | DIFFERENT | 0.526 |
| exp47 C0057/C0063 | DIFFERENT | 0.570 |

All three involve C0063, whose sole computed outcome is `(0.6, '')` — an
anchorless 0.6 wildcard-matching the penalty-tier 0.6 in every neighbour.

A statistic about a mechanism's opinions is not a statistic about its effects.
This project had been reading one as the other, and 36 green tests did not
distinguish them.

### Why the obvious fix is wrong

`_distinctive(0.6)` is `True`, because 0.6 is not an integer. A distinctiveness
fallback passes it straight through. In this codebase 0.6 is a penalty-tier
**configuration constant** recurring across findings about the same module —
exactly the coincidental agreement the anchor exists to prevent. Distinctiveness
answers "could this value identify a computation?", not "does this value identify
*this* computation?", and only the second question is being asked.

### The fix, and its measured cost

A missing anchor now blocks agreement. **BUILT** in `bench/convergence_location.py`,
**TESTED** at 13 passing in `bench/tests/test_anchorless_outcome_guard.py`. Live
in every run — it is the comparison itself and is not flag-gated.

Cost: **none.**

| | Before | After |
|---|---|---|
| Same-defect pairs: SAME / DIFFERENT / UNKNOWN | 19 / 0 / 9 | 19 / 0 / 9 |
| Different-defect: SAME / DIFFERENT / UNKNOWN | 14 / 30 / 246 | 10 / 34 / 246 |
| Fisher exact | p = 1.4 x 10^-7 | p = 3.3 x 10^-9 |
| Tier-3 operative errors | 3 | **0** |

Both p-values were cross-verified three ways — scipy, a hand-rolled
hypergeometric sum, and an exact SymPy rational — agreeing to four significant
figures.

### Downstream consequence, traced before the fix was accepted

The fix changes exp47's novelty series at round 11 from 0 to 1: C0063 is now
counted rather than merged away. Five of the six runs are byte-identical.

**No convergence conclusion moves.** exp47's tail already ended in a non-zero, so
the two-sided gate's K=3 zero-run test was False both before and after.

Three tests required updating, each with the rationale recorded in place.
C0063's status as a true second defect or a re-find is marked **PENDING** in a
named `pending` set rather than folded into `true_defects`, because folding it in
would record an assistant's guess as an adjudication.

## 4. [NEEDS YOUR RULING] Descriptions are truncated at scale

**OBSERVED.** Across every archived report, 2187 finding descriptions:

- **714 are exactly 200 characters** — `runner_core.py:814`, the parser's fallback
  `block[:200]` when the DESCRIPTION/FIND field does not match
- **661 are exactly 500 characters** — the registry write in
  `reference_runner_v2.py:1059`
- **1284 end mid-word**

Roughly 63% of the archive's findings are stored truncated, and the similarity
function reads the truncated form. In the similarity dataset specifically, 81 of
165 criticals (49%) are truncated.

C0063 is the illustration: it ends `"...escape the 0.60 do"`. The anchor that
would have disambiguated that 0.60 was removed by a length cap before the rule
ever saw the finding. The wildcard was the proximate cause of the bad merges; the
truncation is why there was nothing to match against.

### What is and is not established

**Pooled**, a merged pair involving truncated text is far more likely to be a
wrong merge: odds ratio 10.5, Fisher p = 2.07 x 10^-5.

**Stratified by run, the association reverses on the two exam targets.**

| Run | wrong+trunc | right+trunc | wrong+full | right+full |
|---|---|---|---|---|
| exp44 | 4 | 2 | 2 | 3 |
| exp45 | 11 | 1 | 0 | 0 |
| exp46 | 4 | 0 | 0 | 0 |
| exp47 | 16 | 0 | 4 | 1 |
| exp48 | 0 | 2 | 3 | 14 |
| exp49 | 0 | 2 | 1 | 3 |

That is a Simpson's-paradox signature. The pooled odds ratio is partly carried by
which runs happen to have both high truncation and high error. **The causal claim
is NOT established**, and reporting only the pooled figure would be the same
error this exercise was built to correct.

What does survive stratification:

- Truncation shrinks the stem signature — median 4 tokens against 5,
  Mann-Whitney p = 0.0104
- **15 of 318 labelled pairs sit exactly on the 0.20 threshold**, because a
  Jaccard over small token sets is coarse: 1 shared token out of 3 and 3 gives
  exactly 0.200

### The ruling needed

Fixing `block[:200]` to keep the whole block is a small change with a large blast
radius: it alters parsing for every future run, mid-arc, and would make Exp 50
onward non-comparable with Exp 40–49 on any signature-derived measure. Options
are (a) leave it and record the limitation, (b) fix it at the Exp 54 boundary,
(c) fix it now and re-derive the affected measurements. This is a decision about
experimental continuity, not a code question.

## 5. [NEEDS YOUR RULING] The 120 dropped pairs

The recorded measurement labels a pair the same defect at embedding ≥ 0.90 and
different at ≤ 0.70, and **silently drops the 120 pairs in between**.
438 − 28 − 290 = 120. No version of the recorded comment says so.

Those 120 are 27.4% of the data, and they are not a random 27%: they are
precisely the pairs where the question is hard. Excluding them makes any
separation look cleaner than it is. This is the single largest weakness in the
evidence base for the rule.

`experimental_notes/data/similarity_adjudication_pack.json` now holds all 120, unanswered,
sorted by embedding score descending, each with both finding texts, the shared
location, and the two tiers' scores.

**They are deliberately not pre-answered.** Labelling them here would reproduce
exactly the defect the exercise exists to remove — a machine grading a machine,
with the grader's errors invisible because nothing independent checks them. Every
operating point in section 2 carries that caveat until the pack comes back.

## 6. What this changes about method

The governing lesson is narrow and worth stating precisely.

**An answer distribution is not an operating characteristic.** Tier 3 was
justified by a Fisher exact p-value describing what it says. What it *does* — the
pairs where its answer changes a decision — was never measured, and when measured
came out 0 for 3. The p-value was not wrong. It was answering a different
question from the one being relied on.

This is the same shape as the governing failure mode already on record: every
failure renders as a confident success. A tier that abstains on 80% of pairs and
is right about the rest can carry an impressive statistic while contributing
nothing but errors, and nothing in the statistic reveals it.

## 7. Status of every claim in this note

| Claim | Status |
|---|---|
| Operating characteristic script | BUILT, TESTED (10), uncommitted at writing |
| Anchor fix | BUILT, TESTED (13), live, not flag-gated |
| Recorded figures reproduce | VERIFIED, pinned by test |
| Fisher p-values | VERIFIED three ways |
| Truncation at scale | OBSERVED, 2187 descriptions measured |
| Truncation causes merge errors | **NOT ESTABLISHED** — reverses under stratification |
| Operating points | PROVISIONAL — embedding labels, not human |
| C0063 a true second defect | **PENDING ADJUDICATION** |

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
