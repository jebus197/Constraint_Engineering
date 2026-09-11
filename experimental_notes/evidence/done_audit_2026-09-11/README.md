# Adversarial audit of the 84 DONE entries, 2026-09-11

**What this is.** 52 independent agents read the master task list entry by entry and asked, of each one marked DONE, whether the evidence file it names actually establishes the claim the entry makes — not merely whether that file passes. Anything flagged was then handed to a second agent instructed to REFUTE the flag, with the burden of proof on the flag rather than on the entry.

`audit_findings.json` holds all 78 first-pass judgements in full. `verification_verdicts.json` holds all 42 adversarial verifications in full, including the 13 that refuted the flag. Neither is summarised; the prose below is in addition to them, never instead of them.

## The result, with two corrections to the audit itself

**24 of 71 real DONE entries — 33.8028%, Wilson [23.8850%, 45.3834%], Clopper-Pearson [22.9970%, 46.0073%] — carry at least one claim their named evidence does not establish.**

Two defects in the audit had to be corrected before that figure could be stated.

**The batch list named 7 ids that do not exist.** It was written by hand: `10.3`, `11.1`, `12.1`, `5.3`, `I1`, `I31`, `I38`. The auditors correctly reported NOT_FOUND and the verifiers correctly upheld that, so 5 of the 29 originally reported as unsupported were verdicts about nothing at all. The real count is 24.

**13 real DONE entries were never audited**: `2.3`, `3.2`, `3.3`, `7.3`, `9.2`, `9.3`, `9.4`, `L1`, `L2`, `P6`, `P7`, `R5a`, `Z1`. Coverage was 84.5238% of the 84, not 100%. A second run covers them; until it lands the figure above describes the 71 that were examined.

## What kind of gap, across the 24

An entry can carry more than one.

- **25 quote a figure no committed script produces** — the `measured-rate-travels-with-its-script` class.
- **25 name evidence that asserts on SOURCE TEXT where the claim is about behaviour** — the `execute-do-not-grep` class.
- **13 name evidence that tests something adjacent to the claim** rather than the claim.
- **9 state a claim broader than what was actually run.**

## The shape of a typical finding

Entry 1.2 is representative and worth reading in full in the JSON. Its catcher statistics reproduce exactly — the verifier ran the script and every figure matched, including two independent Wilson implementations agreeing to better than 1e-12. What does not reproduce is the entry's own load-bearing sentence, that a split "survives reclassifying every arguable entry in all 16 combinations" with a "worst case p of 0.598". No committed artefact produces either number. The script has no claim/code field at all, and a search across the whole tree finds no 16-combination enumeration and no 0.598.

So the entry is mostly supported, with one sub-claim that exists only as prose. That is the dominant pattern: **these are rarely entries that did nothing, and usually entries that claim slightly more than they established.**

## What this does not say

It does not say the work is undone. Every one of the 71 evidence files exists, and all of them pass — the full suite ran green in a fresh clone four times on 2026-09-11 with 7,247 passing and nothing failing. The gap is between what the tests establish and what the entries claim, which is a documentation-integrity problem rather than a broken-code problem.

Written under CDSFL note standard v1.7 (26 August 2026).
