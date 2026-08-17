# Description Truncation: Three Fixes, and Why the Alarm Was Wrong

2026-08-17, 01:30 BST. Technical version. A plain-English companion and a TTS
file accompany this note.

## Summary

Three defects in how finding descriptions were stored and read are fixed. The
alarming claim that started this — that truncation had caused experiments to
converge early — is **refuted**. It was an artefact of comparing damaged text
against differently-damaged text.

- **[FIXED]** The parser substituted schema headers for claims on 15.1% of
  finding blocks. 312 blocks recovered, zero regressions.
- **[FIXED]** 531 archived descriptions repaired from raw model responses, with
  every join verified. No archived report was modified.
- **[FIXED]** Location extraction counted cited premises as accused locations.
- **[REFUTED]** No experiment converged early because of truncation. Two
  converged *later* than they would have on correct text — the safe direction.

## 1. What was actually wrong

### The 200-character fallback was substitution, not truncation

`runner_core.parse_findings` ended with
`description = desc_match.group(1).strip() if desc_match else block[:200]`.
When the DESCRIPTION/FIND regex failed, the stored description became the first
200 characters of the raw block — which is `FINDING_ID: F006\nSEVERITY: 0.80\n
FIND: <first ~130 chars>`. Not a clipped claim. A schema header where the claim
should be.

Three independent causes, each verified by derivation and by replay:

1. **The `|$` branch was unreachable.** `block = block.strip()` runs before the
   match, and the lookahead spelled `\n\s*$` — a newline, then whitespace, then
   end. `strip()` has already removed every trailing newline, so no such position
   can exist. The author's intent, "or the description runs to the end of the
   block", never executed once.
2. **The separator class was `[:=\-]`.** CC2 writes `FIND.` and `FIND —`.
3. **Markdown heading style has no separator at all.** Gemini and Codex emit
   `## FIND` on its own line.

### The 500-character registry cap reaches live code

`FindingRegistry.register` stores `finding.description[:500]`. I reported this as
storage-only on 2026-08-16. **That was wrong.** The same dict is read each round
by `_location_keyed_critical_series` (the convergence count), by
`_verification_step` at `[:500]` — where CC2 casts CONFIRM/REFUTE/DUPLICATE/
ESCALATE verdicts from round 6 — and by the routing ladder, which asks for
`[:1200]` and can never receive more than 500.

### Location extraction cannot tell an accusation from a citation

`finding_locations` is a word-boundary scan over the whole description. Exp 49's
C0037 accuses claim EN-16 of using the wrong factor convention, then lists four
premises — EN-01, EN-03, EN-17, EN-20 — to derive the correct value. All five
were flagged as locations the finding had accused.

## 2. The three fixes

### Fix A — the parser regex

**BUILT** in `bench/runner_core.py`, **TESTED** by replay over every archived
block, **COMMITTED**.

Line-anchored, separator widened, `\Z` replacing the dead `$`, and two labels
added to the terminator set — `FALSIFIER` and `TARGET_FILE` — because without
them `\Z` runs the description straight through the falsifier's Python.

Measured over the 5592 archived blocks the parser accepts, after applying its own
`_structurally_valid_fid` and code-leak guards:

| | current | fixed |
|---|---|---|
| blocks matched | 4748 (84.9%) | 5060 (90.5%) |
| recovered | — | **312** |
| regressions | — | **0** |
| descriptions containing falsifier source | 190 | 44 |

Of the 4748 that match both ways, 4734 are byte-identical. Nine gain text — two
of them from a previously **empty** capture, 0 → 966 and 0 → 3989 characters. Five
shrink, and all five are corrections: two where the un-anchored pattern had begun
matching inside a fenced code sample and swallowed 5439 characters of Python,
three where it had swallowed a FALSIFIER section.

**Two wider candidates were rejected on measurement.** Terminating at any
following ALL-CAPS label recovered the same 312 but **shortened 870** descriptions
that parse correctly today — `EVIDENCE:` and `IMPACT:` are part of the claim in
this corpus. Terminating at a code fence shortened 834. I nearly shipped the first
of these: my regression metric counted match/no-match and was blind to text loss,
which is precisely the failure class this project exists to catch.

### Fix B — the backfill

**BUILT** as `scripts/backfill_descriptions.py`.

531 descriptions repaired. Every join is verified against the stored text before
being trusted: either the stored value is an exact prefix of the recovered text
(the 500 cap), or it is exactly the `block[:200]` the old fallback would have cut.
471 joins that satisfied neither check were left alone. Nothing ambiguous was
repaired.

**The archived reports are not modified.** Repairs are written to
`bench/logs/<run>/descriptions_backfill.json` and every consumer opts in. Rewriting
the archive in place would destroy the "before" state and leave no way to tell a
repaired figure from an original one.

An earlier draft of this script keyed one candidate per `(model, finding_id)`.
Models re-file the same `F001` round after round, so it silently joined round 0's
block to a round 3 entry — 23 of exp47's repairs were quietly wrong, and the join
succeeded and the text looked plausible. The content check caught it. That is the
argument for having the check rather than trusting the key.

### Fix C — premise exclusion

**BUILT** in `bench/convergence_location.py`, **TESTED** at 19 passing in
`bench/tests/test_premise_exclusion.py`.

Symbols appearing only under a `Premises:` header no longer flag a location.

**The header set is deliberately narrow, and the scope was set by measurement.**
Of 2187 archived descriptions only 122 (5.6%) carry any supporting-material
header, and `EVIDENCE:` is 78 of them. Reading those, `EVIDENCE:` does not
introduce cited antecedents — it introduces substantiation of the same defect at
the same place. Stripping it would delete real signal. `premise(s)` is 35
findings, and those are the citation case.

## 3. The alarm, and why it was wrong

On 2026-08-16 I reported that exp46 and exp49 had converged early because of
truncation, and that exp49's convergence "would not have been reached". **Both
claims are refuted.**

The error was comparing truncated text against *premise-contaminated* full text.
C0037's truncation was cutting the premise list off the end, so extraction
produced the right answer — {EN-16} — for the wrong reason. Repairing the
truncation alone made extraction **worse**: {EN-01, EN-03, EN-16, EN-17, EN-20}.
The two defects were masking each other, which is why neither was visible alone.

Count-side gate close round, K=3 consecutive zero-new-critical rounds:

| run | archived | backfill only | backfill + premise fix |
|---|---|---|---|
| exp44 | 10 | 8 | **8** — truncation delayed it |
| exp45 | 3 | 3 | 3 |
| exp46 | 5 | 5 | **5** |
| exp47 | 11 | 5 | **7** — truncation delayed it |
| exp48 | never | never | never |
| exp49 | 6 | never | **6** |

**No run converged early.** The two that move were *delayed* by truncation, which
is the conservative direction: a finding whose locations are clipped is counted as
not novel by itself, but it also withholds those locations from the accumulator,
so later findings become more likely to count as new.

This vindicates the adversarial sweep's conclusion over my own. Its refuter
reached the same verdict by a stricter method and I initially disputed it on a
coverage gap that turned out not to matter.

## 4. Re-derived measurements

The similarity function's operating characteristic, recomputed on repaired text:

| | as archived | repaired |
|---|---|---|
| criticals | 165 | 165 |
| tier-2 coverage | 161 | 160 |
| tier-3 coverage | 94 | **110** |
| same-location pairs | 438 | **460** |
| labelled same / different | 28 / 290 | 31 / 296 |
| truncated criticals | 81 (49%) | **23 (14%)** |
| AUC | 0.986 | 0.976 |

**What survives the repair** — these hold on both versions:

- P(merge given genuinely different) at the live 0.20 threshold: 14.9% vs 14.5%
- **Zero false splits** on either version
- Against location keying alone, which merges every same-location pair: false
  merges 296 → 47, an **84% reduction**
- Tier 3 changes the decision on **3 of 327 pairs and is wrong on all 3**

**What dies.** The 2026-08-16 note recorded a pooled association between
truncation and wrong merges at Fisher p = 2.07 x 10^-5, odds ratio 10.5, flagged
at the time as NOT ESTABLISHED because it reversed under stratification. On
repaired text it measures **p = 0.272**. The stratification was right; the pooled
figure was an artefact. It is recorded rather than deleted, because a claim
correctly hedged and then correctly withdrawn is worth more as a record than as a
silence.

## 5. What this cost, honestly

Nothing that required a re-run. No experiment is invalidated. What needed doing
was a re-measurement, and it is done.

The genuine finding underneath all of it is smaller than the alarm and more
useful: **two defects can mask each other so completely that fixing one alone
makes the measurement worse.** The premise defect was invisible for as long as
truncation was cutting premise lists off the end. Anyone repairing the truncation
without also finding the premise defect would have concluded, with good evidence,
that their repair had broken the convergence gate.

## 6. What remains

| Item | Status |
|---|---|
| The 120 (now 133) unadjudicated pairs | **PENDING YOUR RULING** — machine labels cannot settle an operating point |
| 471 unverifiable backfill joins | Left alone by design; recoverable only by hand |
| 44 descriptions still containing falsifier source | Narrower than the 190 before; not yet zero |
| 532 blocks the parser still cannot read | Mostly code-leak junk, not findings |
| Registry `[:500]` cap | Still 500; the routing ladder still asks for 1200 |

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
