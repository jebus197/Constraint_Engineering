# WHAT THIS PANEL IS FOR

CDSFL runs multi-model falsification experiments against STEM documents. A run ends when
a convergence gate says discovery has flattened. The founder's goal is Bench Run 2 (BR2),
the full-scale evaluation. Before BR2 can run, the harness must be able to record what an
experiment would show.

Three days of audit produced a set of repairs, a set of findings, and a set of retracted
claims. The founder cannot adjudicate the technical content and has asked you to.

# HOW TO READ THIS BRIEF

Everything below is either:

  [SOURCE]    raw code or raw measurement, in the appended PRIMARY SOURCE packs.
              This is evidence. Check it.
  [CLAIM-A]   a claim CC1 made and later replaced.
  [CLAIM-B]   the claim CC1 replaced it with.
  [CLAIM]     a claim CC1 made that has not been revised.

CLAIM-A and CLAIM-B are presented WITH EQUAL STANDING. This brief deliberately does not
tell you which one CC1 currently holds. Decide from the source pack.

# THE DISPUTED PAIR

[CLAIM-A] "The convergence gate's gamma input counted a population that included
findings later found to be duplicates. Item 1.1 repairs this. Measured: 236 of 287
MERGED entries (82%) were merged in a LATER round than they opened in, so the
pre-existing in-round correction reached only 18% of merges. All 8 archived runs shift
under the repair and 7 of 8 shift gamma upward."

[CLAIM-B] "The gate never reads the repaired variable. It calls _settled_novelty_series
directly, which rebuilds from the finding registry on every call and therefore already
excluded MERGED/DUPLICATE/UNCONFIRMED/REFUTED in EVERY round. Item 1.1 is real but it
repairs rho and the endocrine module, not the gate. The '7 of 8 shift upward' figure was
computed on the all-findings series, which the gate does not read."

Source pack sections A, B, C, D, E, F and measurement table M1 bear on this.

# THE OTHER CLAIMS ON THE TABLE

[CLAIM] Experiment 46 converged with gamma_critical = 0.3357 against a threshold of
0.30 -- a margin of 0.036, the narrowest in the arc. (See M1.)

[CLAIM] The churn detector cannot fire on most of the current arc: rho_earliest_round
is 12, and of experiments 44-49 only exp44 (13 rounds) reaches round 12. (See M2, G.)

[CLAIM] exp47's archived report is incomplete: it records converged_at 13 and
total_rounds 14, but its per-round list and gamma_critical_history both begin at round 5.
Raw per-round response files for all 14 rounds are present on disk. (See M3.)

[CLAIM] No convergence verdict has changed as a result of any repair this week. (See M4.)

[CLAIM] MERGED is a delete-with-pointer, not a fold. When a finding is marked MERGED the
runner records an alias to the canonical entry and stops counting the old one. Nothing
propagates: not severity, not tool verdicts, not supporting evidence, not the fact that a
second model found the same defect independently. Models are told in their round prompt
that MERGED means "folded into" the canonical entry. (See M5.)

# THE QUESTIONS

Answer each. Number them. Where a question has a decision consequence, state the
consequence you would accept if you are wrong.

**Q1. ADJUDICATE THE DISPUTED PAIR.** From the source pack, not from the prose: does the
convergence gate read a series that was already post-deduplication in every round? If
CLAIM-B is right, does item 1.1 remain worth having, and is anything else in CC1's Stage 1
built on the same misattribution? If CLAIM-A is right, say what in the source pack shows
it and what CLAIM-B has misread.

**Q2. THE FOUNDER HAS RULED ON MERGED SEMANTICS. FALSIFY THE RULING.**
This is no longer an open design question. The founder's ruling, in their own framing:

  "Then it is clearly a dupe. But dupes don't invalidate a finding or cause it to get
  thrown away. If you look at the real structure of Mozilla Bugzilla, usually the first
  finding is either marked as confirmed, resolved, dupe or rejected. But the record of
  all dupes etc. continues to survive... the important part we should not neglect is
  when an issue is marked as 'resolved'. Usually that is the result of a human volunteer
  or a Bugzilla engineer, looking at the issue and issuing the 'simplest sufficient fix',
  which has been a core guiding principle of this project since its inception... dupes
  (and potentially dupe fixes) are still recorded, presumably in the event that the fix
  adopted might need to be revisited... providing it can be demonstrated as effective,
  it can stand as a positive step, or one of the notches on the dial towards convergence.
  So what should we do? We do it the way Bugzilla does it. But we adapt this model not
  just for software, but for STEM research as a whole."

Verified against primary sources (M8, M9) and external research since that ruling:
  * CDSFL ALREADY preserves the duplicate record. registry.resolve() writes status +
    merged_into to the duplicate and the entry survives. 287 of 287 carry pointers.
    This half of the Bugzilla model is already implemented correctly.
  * CDSFL does NOT do the other half. Bugzilla adds the duplicate reporter to the
    ORIGINAL's CC list, maintains a dupe count over direct AND indirect duplicates, and
    surfaces "Most Frequently Reported Bugs" so that report frequency informs priority.
    CDSFL writes NOTHING to the target. No dupe count exists anywhere in the codebase.
  * The runner's own round prompt already opens with "State machine (Bugzilla paradigm)".
  * "Simplest sufficient solution" IS in the directives every panel model receives
    (cdsfl_core_formal.md:359 and two others). It is NOT in the mathematical appendix --
    no parsimony term is formalised anywhere in the model.

Your task is NOT to agree. Falsify it:
  (a) Is the Bugzilla analogy sound when carried from software defects to STEM research
      claims? Name where it BREAKS. A software bug is a defect in an artefact under the
      maintainer's control; a STEM claim may be wrong about the world. Does "duplicate"
      even mean the same thing? Does "resolved by simplest sufficient fix" survive the
      translation, or does it import a repair-centric assumption that does not hold?
  (b) CC1's position is that recording and surfacing a dupe count is an ACCOUNTING change
      (computable retroactively from stored pointers, replay-validatable, zero dispatch)
      while letting the count move severity or reach the convergence gate is BEHAVIOURAL
      (needs a live run). Is that split real, or does merely surfacing a count change
      behaviour through some path CC1 has not traced?
  (c) M9 shows only 13 merge pointers across six experiments and a maximum corroboration
      count of 3. Is a dupe count worth building against a signal that thin? What would
      have to be true for it to become informative?
  (d) Should "simplest sufficient fix" be FORMALISED in the mathematical model as a
      parsimony term, or does it belong only in the directives? Argue either way.

**Q3. THE TWO NEW FINDINGS.** Are the churn-detector claim and the exp47 report-truncation
claim real, given M2, M3 and G? Rank their severity against the repairs already made. Is
either a blocker for BR2, or neither?

**Q4. THE MINIMUM REPAIR SET BEFORE BR2.** Given everything above, what is the smallest
set of repairs that must land before BR2 is worth spending money on? Name what you would
CUT from the current plan as well as what you would add. The current plan is Stage 1
(accounting repairs, zero dispatch) then Stage 2 (one behavioural repair to the immune
pipeline's duplicate auto-reject, needs one live run) then Stage 3 (experiments 50, 51,
52 four-cell factorial, 54 capstone).

**Q5. THE PROCESS QUESTION.** Six of fifteen commits in three days were CC1 correcting its
own claims. CC1's own diagnosis is that each was a claim quantified over a set ("the gate
reads X", "deleting is lossless") asserted after checking one member of that set, and that
each was refutable by one cheap command not run. Is that diagnosis sufficient? What
concrete, mechanical process change would you impose? Consider specifically whether panel
review helps with this failure mode or is structurally unable to -- a panel briefed with a
description inherits the description's errors.

**Q6. THE IMMUNE PIPELINE IS REMOVING 97% OF EVERYTHING. HOW SHOULD IT BE FIXED?**
The founder has named this alarming and asked the panel to address it directly.
MEASURED (M6), from the pipeline's own append-only log, unit-test runs excluded:

    2026-04   1351 removed / 1400 handled   96.5%
    2026-05    801 / 813                    98.5%
    2026-06    439 / 450                    97.6%
    2026-07    451 / 469                    96.2%
    TOTAL     3042 / 3132                   97.1%

Sustained for four months. Dated to a regression on 12 April 2026, commit
"Phase 2: Embedding similarity shared backend".

CC1 HYPOTHESISED that duplicates were being destroyed before reaching the registry,
and then REFUTED IT against source (M7): registration is at :8899, the pipeline runs
at :9092, and the pipeline never writes to the registry at all. Its only live effect
is that NK-cell duplicate verdicts are rendered into the NEXT round's prompt.

So the mechanism appears to be SUPPRESSION, not deletion: models are told their finding
duplicates an existing one, and stop re-reporting it. That would explain why only 13
merge pointers exist across six experiments (M9) -- corroboration never forms because
re-reporting is discouraged before it can.

  (a) Is that mechanism right? Check M7 and say what CC1 has still missed.
  (b) A separate measurement this week found NO similarity threshold separates the hard
      cases: against 85 tool-decided labels, embedding AUC 0.608, Jaccard 0.586,
      stem-signature 0.433 (BELOW CHANCE). So "retune the threshold" is not available.
      Given that, what SHOULD the duplicate discriminator do? Options include: route
      the decision to a tool rather than a similarity score; stop auto-rejecting and
      let corroboration accumulate; flag without suppressing; something else.
  (c) What is the SMALLEST change that restores useful throughput without inventing new
      machinery? Occam's razor is a project directive -- apply it to your own proposal.

**Q7. ANYTHING NOT COVERED.** The founder explicitly asked what has been missed. If you
see a defect, a confound, or a risk that none of Q1-Q6 names, raise it here. If you see
nothing, say so plainly rather than inventing something.

# WHAT THE FOUNDER NEEDS FROM THIS PANEL

Verbatim: "we need to clear the path forward for the remainder of the project... I've
said many times a system that can only find more problems than it fixes is of limited
value to anyone. But what is the point of having all this 'intelligence' if we can't
use it?"

This is NOT a request for compelled convergence. Disagree with each other and with CC1
freely; disagreement is preserved as information and no synthesis step will erase it.

It IS a requirement that each of you COMMIT TO A RECOMMENDATION. A verdict that only
enumerates further problems, without naming what to do next and in what order, does not
meet the brief. Where you are uncertain, name the cheapest measurement that would
resolve the uncertainty rather than deferring the decision.

The founder is funding this personally from borrowed money. Weight your recommendations
by cost. Zero-dispatch work that can be validated by replaying the existing archive is
close to free; a live experiment run is not.

# CC1's OWN POSITION, for you to attack

CC1 is a participant here, not the convenor. Its current position, so you can target it:

  1. CLAIM-B is correct and CLAIM-A is not. The gate reads a settled series.
  2. Item 1.1 remains worth keeping, but as a rho/endocrine repair, correctly labelled.
  3. The founder's Bugzilla ruling is right, and the missing half is aggregation onto
     the target, not preservation of the duplicate.
  4. Q6's suppression mechanism is the real blocker, ahead of everything in Stage 1.
  5. Stage 2 should be reordered AHEAD of the remaining Stage 1 items, because a dupe
     count built now would measure a signal the pipeline is currently suppressing.

CC1's error rate this week is material and is stated so you discount it appropriately:
six of fifteen commits in three days were corrections of its own prior claims, and one
hypothesis was refuted within this very brief (Q6). Do not defer to positions 1-5.

---
Brief assembled 2026-08-18 12:5x BST at HEAD f4df176. Primary-source packs generated
at assembly time from bench/reference_runner_v2.py and the archived run reports.
