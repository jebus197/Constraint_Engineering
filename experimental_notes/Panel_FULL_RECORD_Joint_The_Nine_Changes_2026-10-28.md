# The joint round found a defect neither blind seat saw: any of an empty tail is False

Record written 2026-10-28T23:42:37+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED AND WHY. The joint half of the blind round on the 9 changes of 2026-10-28, carrying both blind replies verbatim. Both seats are free; 0 paid seats were dispatched. The round was asked to settle 2 verdict splits and 1 interaction, and CC1's own position was stated in the brief as the thing to attack. Both seats declared a stop on the project's diminishing-returns criterion.

THE FINDING NEITHER BLIND SEAT MADE, AND IT DECIDES BOTH SPLITS. The cc2 seat read the label-generating code rather than the closes and found that a premature label is computed as a disjunction over the rounds recorded AFTER a gate fire point. The disjunction of an empty sequence is false, so a fire point with no recorded round after it is labelled sound with zero evidence: it is unobserved, not sound. Measured over the archive, 10 of 30 fire points have an empty tail and 10 more have a tail of 1, all 20 labelled sound, and not one of the 8 premature labels comes from a tail shorter than 2. Tail length alone predicts the label with an area under the curve of 0.971591, interval 0.888203 to 1.0, Spearman rho 0.751455 at p = 1.70325e-06, which out-separates every signal the committed table scores including the one at 0.9058. In the seat's own words it is length scored against length. The repair is delivered: a tail count carried on every row, the empty-tail count printed unconditionally, and a minimum-tail flag whose default of 0 reproduces every published figure byte for byte. Verified after adoption: the default still gives 30 fire points, 8 premature and 22 sound, with the 2 discriminating signals at 0.9058 and 0.8693 unchanged.

AND A FIRST VERSION OF THAT ADOPTION WAS ITSELF AN UNWIRED ADDITION. The 2 new counts were computed and then dropped from both the printed output and the returned record, which is the half of the additive standard about additions nothing reaches, occurring inside the fix for a measurement defect. Both counts are now reported, under the exact key names used by bench/tests/test_a_sound_label_is_an_observation_not_an_empty_tail_2026-10-28.py, the test the cc2 seat delivered with the repair, so that it exercises the real interface rather than a parallel one.

SPLIT 1, THE SUBJECT TIER RESPECTING KIND, IS RESOLVED AGAINST BOTH BLIND VERDICTS AND AGAINST CC1's STATED POSITION. The 2 seats measured different populations and both measured correctly. The cc2 seat replayed anchorless existing items and found that a question-only narrowing of the filter recovers an identical set to the shipped general form, 4 of 31 each with an empty set difference, giving the narrowing strictly the smaller admission surface. The fable seat delivered an executed table over 3 documented case families and showed the shipped form is the unique variant correct on both cases with a live occurrence: a settled proposed fix against a new question, which is the founder's own ruling, and a settled proposed fix against a genuinely new feature request, which is a live incident of 2026-10-17 pinned by a committed test. The case the shipped form loses has 0 live occurrences and exists only as a constructed demonstration. The 2 cases are inseparable by kind alone, since they share an identical call shape and differ only in text, and text-similarity repairs were tried against this exact problem and refused twice as circular. CC1's resolution is to retain the shipped form, because reverting is a removal and the additive standard requires a committed measurement that the replacement dominates: parity on recovery is not dominance, and the narrowing loses a live case. The figure that originally justified the filter is withdrawn outright, because 0.740299 of its denominator is pairs for which no ticket of that kind exists, and the executed case table replaces it in the source comment.

SPLIT 2, THE GAMMA THRESHOLD, IS RESOLVED AS A LABEL RATHER THAN A SPLIT, AND CC1 CONCEDED THE WRONG HALF. Both blind verdicts were sound with conditions. The cc2 seat showed that the comparison between the old and new thresholds is NESTED on the same fire points and therefore PAIRED, so the independent 2 by 2 test cited in the brief is the wrong statistic for the decision taken. On the paired statistic, raising the threshold blocks 4 additional closes of which 4 are premature and 0 sound, leaves the sound-blocking count identical at 2 of 22, and gives an exact binomial p of 0.005057, with a local Wolfram Engine agreeing to the digits shown. So the word withdrawn should have been the swept test's p value, not the claim of dominance. The fable seat independently delivered the producer the figures had been missing, confirming a selection-corrected permutation p of 0.075846 over 20,000 shuffles and a leave-one-out optimal interval containing the chosen value in 8 of 8 folds. Both seats agree the value stands. The genuine third option is neither a new value nor a reversion: it is to instrument the series the gate actually compares against, where the archive currently supports no cut at all, and to amend a frozen reachability condition in writing rather than letting it be superseded silently.

THE LABEL-CENSORING INTERACTION RAN THE OPPOSITE WAY FROM THE DIRECTION THE BRIEF ACCEPTED. The fable seat raised it in the blind round and CC1 accepted it outright. The cc2 seat read the code and showed that the causal chain runs the other way: the arm blocks the close, so the run continues, so more rounds are recorded, so the tail grows and the disjunction becomes more likely to be true. The arm does not delete premature labels, it converts sound labels into premature ones. Both remedies CC1 offered were therefore wrong, one on the merits and one because it would propagate a backwards description. Both seats converged on the same answer: fix the label definition before the threshold is fitted, state that the labels are conditional on the arm being active, and run no rounds with the arm disabled. The cost is 0 runs.

AND ONE CHARGE CC1 MADE AGAINST ITSELF WAS FALSE. The brief conceded that a second set of figures was unpinned on the strength of a re-run disagreement. The cc2 seat ran the committed producer on the falsifiable-label subset and reproduced what the brief quoted to 4 decimal places. The concession is withdrawn. A concession accepted without checking is the same failure as a claim asserted without checking, and it happened in the same document that corrected 2 genuine instances of it.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — JOINT ROUND on fix_review_panel_2026-10-28

**THIS IS THE JOINT HALF OF A BLIND ROUND, AND IT IS OWED.** Both seats answered the same brief on the 9 changes without seeing each other. Their replies are carried below IN FULL and UNEDITED. The dispatcher refuses a new blind round until this is run, which is correct: a blind round whose joint half never happens leaves 2 answers and no resolution.

## REQUIRED SECTION 1 — The question

**You agreed on the facts and split on 2 verdicts. Which split is real, and which is a label?**

**WHERE YOU ALREADY CONVERGE, so do not spend the round on it.** On change 5 you reached the SAME operational conclusion by different routes and CC1 has acted on it: `--severity-spec` is NOT being passed tonight. cc2 proved that on the in-play domain V is at most 0.5, so `asserted . V <= 0.5 < 0.7` holds unconditionally (z3 `unsat`, and a local Wolfram `Maximize` returning 1/2), which collapses the A4 door to `severity_is_proven` alone and releases a proven asserted-1.0 unresolved critical. fable reached "not tonight" from the runner's own staging comment at lines 10378 to 10380. You BOTH also refuted the brief's stated risk: `_settled_novelty_series` at line 10659 reads RAW severity, so `crit_s`, `gamma_critical` and the K-round window are byte-identical with the flag on or off, which cc2 measured as `[0, 1, 1, 0]` both ways. **The brief was wrong and you were right. Dropping the flag also answers fable's attribution objection, because the run now varies only changes 1 and 2 against the 2 completed runs.**

**SPLIT 1, AND IT IS THE REAL ONE — CHANGE 3, the subject tier respecting `kind`.** cc2 returned **UNSOUND**: the shipped change recovers **1 item in 31, p = 0.5**, and the producer refutes its own headline because 0.741791 counts hypothetical `(kind, subject)` pairs rather than realised blocks. fable returned **SOUND WITH CONDITIONS** but held the RATIONALE false for `fr` against `pf`, with an EXECUTED demonstration that a cross-kind rediscovery now enters the store. You are measuring 2 different populations: cc2 measured RECOVERY on known rediscovery cases, fable measured ADMISSION of a new duplicate. Both can be true.

**SPLIT 2 — CHANGE 2, `gamma_alt_threshold` at 0.41.** fable says the cut is **FITTED** and that CC1's word "DOMINATES" is refuted by CC1's own instrument, whose AUC for gamma-at-fire is **0.3466 with an interval spanning 0.5**. cc2 returned SOUND WITH CONDITIONS and asked for a committed producer emitting the 4 figures. fable expects the writing seat to resist the word "fitted".

**AND ONE FINDING fable BELIEVES UNNOTICED, which CC1 had not seen: interaction 2 x 7, LABEL CENSORING.** Every future labelled close used to fit `T` will come from runs already filtered by the 0.41 arm, so `T` would be fitted to the gamma arm's RESIDUAL premature population rather than the population the AUC was measured on. cc2 did not raise it.

## REQUIRED SECTION 2 — CC1's position, which is the thing to attack

**On change 3, CC1 holds the filter should be RETAINED and its JUSTIFICATION WITHDRAWN.** The founder ruled on 2026-10-19 that a question and a proposed fix take distinct identities, in his own words: *"Questions should be given their own unique hashed ID in the registry, like the other categories ... so they can be tied directly to the problems they address and so that in future you can't lose them"*. That is a ruling about identity, not a hypothesis about effect size, so an effect size of 1 in 31 is not a reason to revert it. What IS refuted is the brief's claim that the filter repairs over-matching at scale, and CC1 withdraws that claim. **ATTACK THIS**: say whether implementing a ruling at a measured effect of 1 in 31 is additive or is an addition nothing reaches, and if the latter, what reaches it.

**On change 2, CC1 CONCEDES to fable on the statistics and keeps the value.** "Dominates" is withdrawn: the AUC interval spans 0.5 and the cut is fitted, with leave-one-out stability as partial cover only. 0.41 stands because 0.30 was measured strictly harmful, which makes this a choice between a fitted cut and a harmful one rather than between a fitted cut and a principled one. **ATTACK THIS**: name the third option, or say plainly that there is none.

**On the label-censoring interaction, CC1 accepts it without reservation and asks you to settle the remedy.** It must be named in the pre-registration BEFORE it freezes. The question is whether naming it is sufficient, or whether `T` must be fitted on an UNFILTERED labelled set, which would require running some rounds with the gamma arm disabled and so costs runs.

**AND A DEFECT OF CC1's OWN THAT fable FOUND AND CC1 HAS FIXED, stated because it bears on what you can trust in the brief.** The change 8 producer shared ONE random generator across its power figures, so the figures moved with call order: the live run printed 0.1490 where the prose said 0.1460, and 0.9185 where it said 0.9207. Each figure now has its own seeded generator and the verdict block READS the computed values instead of restating them. Reproduced twice at the default trials: power against the strong effect **0.144250**, n=63 power **0.916500**, power at the minimum detectable slope **0.798250**. 33 citations were corrected across the directive, the notes and this brief. **fable also found the change 7 figures unpinned (0.9345 against 0.9058 on re-run); CC1 accepts that and it is NOT yet fixed.**

## REQUIRED SECTION 3 — Use the harness

RUN things; do not describe them. Execute the producers and tests named in the replies below. The tool output IS the evidence.

## REQUIRED SECTION 4 — Produce a fix and test it

Write any fix INTO the sandbox tree at its real path and EXECUTE it. A finding without an executed fix is half an answer.

## REQUIRED SECTION 5 — What would refute you

State, before you conclude, what evidence would overturn your own position in this round.

## REQUIRED SECTION 6 — Output

Return: your verdict on each of the 2 splits, whether you now change your blind verdict and why, your answer on the label-censoring remedy, and your strongest disagreement with CC1's framing above.

## REQUIRED SECTION 6b — When to stop

STOP when the 2 splits are either resolved or shown to be unresolvable on the evidence available tonight, and say which. This is a BOUNDED round: it is the joint half of one blind round, not an open inquiry. Diminishing returns is this project's own criterion, so if a further pass would only restate a position already argued, stop and say so. Specifically: stop on change 3 once you have agreed whether a ruling implemented at a measured effect of 1 in 31 is additive; stop on change 2 once the third option is named or its absence is stated; stop on label censoring once the remedy is either "name it" or "fit T unfiltered, at a cost in runs". Do not open new changes; anything new goes in DISAGREEMENT as a pointer, not as a 10th item.

## REQUIRED SECTION 7 — The other seat's blind reply, in full

### cc2, blind, 35,395 characters, 78 tool calls, 977.1 s

I ran every producer and test named, plus my own falsifiers. Three files were delivered into the repository tree and executed. Wolfram was available and used once as a second falsifier.

---

## CHANGE 1 — `REQUIRED_QUIET_RUN` reverted to 3

**VERDICT: SOUND**

**FALSIFICATION.** I tried to show 3 re-opens false quiet. It does not, because quiet is not the signal. I ran `bench/can_any_signal_see_a_premature_close_2026-10-27.py`:

```
    novel_this_round            30    0.3097      [0.1067, 0.5126]   BLIND -- interval spans 0.5
    findings_count              29    0.9058      [0.7494, 1.0000]   DISCRIMINATES
```

Local quiet (`novel_this_round`) is blind at the firing point on the project's own instrument. Raising K from 3 to 7 therefore buys nothing on the discriminating axis; it only shortens the reachable run set, and 7 occurs 0 times in 409 rounds. 3 is defensible because it is the floor of a lever that was never the lever.

**WHAT I WOULD MEASURE.** Not P(premature | K). Hold K at 3 and measure P(findings remained | gate fires) *stratified by `findings_count` at the fire point*. If that conditional is flat in `findings_count`, change 7 dies too; the brief's AUC 0.9 says it will not be flat.

**WHAT WOULD REFUTE ME.** A recount showing the 8 premature closes at K=3 cluster in runs that *would* have survived to a 4th or 5th quiet round — i.e. that K=4 blocks ≥4 of 8 at no sound-close cost. The archive can answer this today and the brief does not report it.

**COLLATERAL.** The producer `scripts/the_subject_blocklist_grows_with_every_close_2026-10-28.py` prints, as one of its own false-suppression examples:

```
   qs:524186098488 'Does the 2026-10-08 ruling raising the quiet run to 7 still stand'
      blocked on `REQUIRED_QUIET_RUN` by pf:028f975075d0 [MERGED]
```

The ticket store suppressed the question that this change answers. That is evidence for change 3's existence, and against its sufficiency (see below).

---

## CHANGE 2 — `gamma_alt_threshold` 0.30 → 0.41

**VERDICT: SOUND WITH CONDITIONS**

**FALSIFICATION.** The source comment names `bench/can_any_signal_see_a_premature_close_2026-10-27.py` as the producer of "the MINIMUM gamma across all 8 premature closes is 0.3173", 0-of-8, 4-of-8 and Fisher p = 0.029355. I ran it. Its entire output is 15 lines and contains **none of those figures**. What it does contain is the discrimination of the two gamma series the threshold is applied to:

```
    gamma                       30    0.3466      [0.1337, 0.5595]   BLIND -- interval spans 0.5
    gamma_critical              21    0.4500      [0.0000, 1.0000]   BLIND -- interval spans 0.5
```

Two consequences. (a) **The gate reads `gamma_critical`** (`_check_hardened_convergence`: `g_crit = _estimate_gamma(crit_s)`), and `gamma_critical` is recorded at only 21 of 30 fire points with an AUC interval of [0.0000, 1.0000]. The arm's case is argued on `gamma`. (b) p = 0.029355 is the p-value of **one threshold selected by sweeping a continuum against 8 positives**, uncorrected for that search, on a signal whose own AUC interval contains chance. "Leave-one-out returns 0.4140 or 0.4585 in 8 of 8 folds" measures the stability of the *optimum*, not out-of-sample blocking.

**Why still SOUND WITH CONDITIONS and not UNSOUND:** 0.30 was measured strictly harmful — 0 of 8 premature, 2 of 22 sound, Fisher p = 1.000000. Replacing a harmful constant with one that is no worse on sound closes and better on premature ones satisfies the additive standard's dominance test. The conditions: (1) commit the script that produces 0.3173 / 4-of-8 / 0.029355, or correct the citation — at present the named producer does not produce them; (2) re-derive the figures on `gamma_critical`, the series the gate actually reads, and record that it is missing at 9 of 30 fire points; (3) record 0.41 as provisional with the same countdown change 7 pre-registers.

**WHAT WOULD REFUTE ME.** A committed producer emitting those four figures from `gamma_critical`, with a permutation null over the threshold sweep that keeps p < 0.05.

**COLLATERAL.** None found. `bench/tests/test_gamma_does_not_cover_the_quiet_arm_2026-10-08.py` passes, 13 tests.

**On "can 0.41 and 3 hold together":** yes, and the reason is structural rather than empirical. The gate is a conjunction, so raising one side and lowering the other is not a cancellation — each side must independently pass. `gamma_critical ≥ 0.41` is a statement about the *shape* of the cumulative critical arrival curve; K = 3 is a statement about its *tail*. They are computed from the same `crit_s`, which is a real coupling, but in opposite directions: a run that just achieved 3 quiet rounds has a flattening cumulative curve, so the two conditions correlate positively and the conjunction is weaker than their nominal product. That is an argument for *reporting* the joint block rate, not against the pair.

---

## CHANGE 3 — subject tier respects `kind`

**VERDICT: UNSOUND**

**FALSIFICATION — the producer refutes its own headline.** I ran `scripts/the_subject_blocklist_grows_with_every_close_2026-10-28.py`. The brief quotes its 0.741791 and not its replay:

```
== replay: the store's own items, re-proposed without an anchor ==
   AS SHIPPED  suppressed 5 of 31 = 0.161290  Wilson [0.070926, 0.326344]
   KIND-AWARE  suppressed 4 of 31 = 0.129032  Wilson [0.051343, 0.288524]
   items the kind check recovers: 1
   Fisher exact (shipped suppresses more): p = 5.000000e-01, odds ratio = 1.2981
```

**The change recovers 1 item in 31, p = 0.5.** 0.741791 counts hypothetical `(kind, subject)` pairs; it is not a measure of how often the filter changes a decision. And of the five false suppressions the same producer exhibits, **four are same-kind** (`fr` blocked by `fr`, `qs` blocked by `qs`) and are untouched by the filter. The change addresses 1 of the 5 defects its own producer displays.

**The case the suite does not cover, which the brief asked me to name.** Every known-rediscovery case in `test_ticket_store_2026-10-17.py` seeds and proposes with kind `pf` (`_seeded`, `CASES`), so the suite is blind to the cross-kind axis by construction. The founder's 2026-10-19 ruling is about `qs` against `pf` — "he answers mine, I answer his". The change generalises it to all six unordered pairs, including `fr`↔`pf` and `pf`↔`wr`, where resolutions do **not** travel in opposite directions: a feature request, a proposed fix and the work remaining on the same mechanism are one item seen from three sides. Delivered and executed:

```
bench/tests/test_the_kind_filter_reopens_the_cross_kind_rediscovery_2026-10-28.py
settled pf -> proposed pf : subject-settled
settled fr -> proposed pf : created
settled pf -> proposed wr : created
kinds used by the known-rediscovery seeding: ['pf']
4 passed in 0.17s
```

The second line is the 2026-10-17 routing-ladder rediscovery — the case the tier exists for — passing straight through. `from_chat` types a ticket from the marker its author wrote, not from its content, so his `fr` and the assistant's `pf` land on different kinds while naming the same subject.

**FIX.** I did not patch `ticket_store.py`, and that is deliberate. The measured effect of the shipped change is +1 of 31 at p = 0.5; the measured effect of the *narrow* form — restricting the exemption to `qs` against the three work kinds, which is exactly the founder's ruling and adds no constant — would by the same replay be ≤ +1 of 31. Neither clears the dominance bar the gamma arm was held to. The defensible action is to **revert the kind filter** and keep `propose_from_chat`'s anchor (change 4a), which already escapes the tier through the designed `_distinct` hatch and is the fix that actually recovers the items. Delivering a patch here would be the composed fix the founder's 2026-10-02 ruling forbids: two mechanisms where one demonstrably suffices.

**WHAT WOULD REFUTE ME.** A replay on the real store showing the kind filter recovers substantially more than 1 of 31 at p < 0.05 — e.g. run against the 994 cross-kind pairs rather than the 31-item sample — *together* with a cross-kind rediscovery corpus showing no genuine rediscovery is let through.

---

## CHANGE 4 — the harvester's chat half

**VERDICT: UNSOUND as committed. (a) and (c) are sound; the superset argument in (b) is false.**

**FALSIFICATION.** `MARKER` is compiled with `re.MULTILINE` and its left context is `(?<=^)|(?<=[\s(\[])`, so a **newline** is an accepted left neighbour. In the raw JSON line that newline is the two characters `\` and `n`, so the character immediately left of the token is the word character `n`, and `\b` fails. Executed on the real regexes:

```
newline before marker    MARKER=True  CANDIDATE_LINE(raw)=False  SUPERSET VIOLATED
tab before marker        MARKER=True  CANDIDATE_LINE(raw)=False  SUPERSET VIOLATED
carriage return          MARKER=True  CANDIDATE_LINE(raw)=False  SUPERSET VIOLATED
plain space (control)    MARKER=True  CANDIDATE_LINE(raw)=True   OK
FALSIFIED: 3 of 4 cases are accepted by the DECISION and rejected by the PREFILTER
```

The dropped shape is a marker at the start of a line inside a multi-line message — **how a marker on its own line is written**, which is the form the module docstring says it is for. The superset argument's third clause, "MARKER's own left and right contexts each imply a word boundary", is true of the decoded text and false of the raw line, which is the same class of error the brief credits itself with catching one step earlier.

**This invalidates the headline.** "With all filters … the number of messages whose text actually RAISES a marker is 0" was produced by a reader that provably cannot see a newline-prefixed marker. The 0 is not yet evidence that the chat half harvests nothing.

**FIX — delivered at its real path and executed.** `scripts/harvest_tickets_2026-10-17.py`:

```python
CANDIDATE_LINE = re.compile(r"(?:fr|pf|qs|wr)", re.IGNORECASE)
```

Drop the boundaries rather than enumerate the escapes. A bare substring is provably a superset: `MARKER` can only fire if the two letters are contiguous in the decoded text, and these transcripts' JSON never escapes an ASCII letter, so they are contiguous in the raw line. Any boundary assertion on the raw line is an assertion about the token's *neighbours*, and the neighbours are exactly what encoding changes. It costs decoding, the direction a prefilter is allowed to be wrong in, as the original docstring already conceded. Falsifier `bench/tests/test_the_chat_prefilter_is_not_a_superset_2026-10-28.py`:

```
old prefilter rejects 3 of 3 decided cases: ['newline', 'tab', 'return']
decided cases 128; prefilter misses 0
3 passed in 0.20s
```

The sweep covers 4 kinds × 8 left-neighbours × 4 marker punctuations.

**Is a marker-gated chat harvester worth keeping?** Yes, but re-run the (c) measurement first — the 0 is not established. On the second question: no marker-free predicate over 249,664 lines will do it without flooding a 2,879-ticket store, and I would not build one. The predicate that works is **`propose_from_chat` at the moment of raising**, which is change 4(a) and is already right: the anchor is derived, not remembered. Unmarked founder questions are reachable by a *human* marker applied retrospectively, not by a reader.

**WHAT WOULD REFUTE ME.** A demonstration that `from_chat` never sees a raw line containing an escaped newline — e.g. the transcript writer emits literal newlines inside JSON strings (which would be invalid JSON) or one message per physical line with no embedded breaks.

---

## CHANGE 5 — `--severity-spec` promoted to DECIDING

**VERDICT: UNSOUND**

**FALSIFICATION.** `effective_severity` is read at exactly one decision site, `FindingRegistry.blocking_entry_ids` (line 4263), where the rule is `effective_severity(e) < CRITICAL_SEVERITY_THRESHOLD and severity_is_proven(e) → release`. Every entry whose blocking decision is still **in play** there carries V ≤ 0.5: V = 1.0 requires `falsifier_verdict == "CONFIRMED"` and `_FALSIFIER_RESOLVED_VERDICTS == {"CONFIRMED"}`, so such an entry is released four lines later regardless. Severity is a [0, 1] score, so `asserted · V ≤ 0.5 < 0.7` **unconditionally**. The severity half of the conjunction is constant-true; the door collapses to `severity_is_proven(e)` alone.

Executed (`bench/tests/test_the_severity_spec_annihilates_the_a4_severity_door_2026-10-28.py`):

```
asserted 1.0, PROVEN, unresolved falsifier: spec OFF blocks=['C1']  spec ON blocks=[]
max effective_severity over the in-play domain = 0.5; CRITICAL_SEVERITY_THRESHOLD = 0.7
z3: exists an in-play entry with asserted*V >= 0.7 ?  unsat
archive: 76 states, 3630 entries, 246 UNCONFIRMED; proven 30; UNCONFIRMED+REFUTED 1, also proven 0
crit_s spec OFF = [0, 1, 1, 0]   spec ON = [0, 1, 1, 0]
5 passed
```

Second falsifier, Wolfram Language (local Wolfram Engine, via `wolframscript`):
`Maximize[{s*v, 0<=s<=1 && (v==1/2 || v==0)}, {s,v}]` → `{1/2, {s -> 1, v -> 1/2}}`. Maximum 1/2 < 7/10, agreeing with z3.

So a **proven, asserted-1.0, unresolved critical is released from the A4 fail-safe** — the one guard whose own code comment says the censoring "runs toward convergence".

**And the brief's own statement of the risk is wrong.** `_settled_novelty_series` (line 10659) reads `e.get("severity")` raw. `crit_s`, `gamma_critical`, `cum_crit` and the K-round window are untouched by the flag — fourth line of output above. "With the spec deciding, far fewer findings are critical. The convergence gate requires K rounds with no new CRITICAL finding" is false of the gate's critical series.

**FIX — attempted, measured, and WITHDRAWN; no patch shipped.** I wrote the obvious repair (leave the `V(None)=0.5` stand-in at identity, keep only the measured factors V=0 and V=1), it passed its own falsifier, and it broke two tests whose docstrings state the defect as the design. I then measured its reachability over 76 archived states and 3,630 entries: the population it would still release is **1 entry UNCONFIRMED+REFUTED, of which 0 are proven**. An addition nothing reaches, which the additive standard forbids as squarely as a vacuous gate. I reverted the source file (`test_the_severity_spec_decides_when_promoted_2026-10-15.py`: 14 passed) and shipped the falsifier with the killing measurement in it.

The real conclusion is stronger than either patch. With V the only collected factor, the specification's range on the in-play domain is [0, 0.5] and a cut of 0.7 has **no discriminating power at all**: the only two reachable behaviours are "release every proven entry" and "release nothing". `W(class)` and `confidence` are collected on 0 of 3,298 entries. Promotion requires either collecting them, or re-deriving the cut on the specification's own scale — which is precisely change 8's 63 full-range adjudications. **Do not pass `--severity-spec` tonight.**

**WHAT WOULD REFUTE ME.** A second decision site reading `effective_severity` that I missed (I grepped: 4263 and 21269, the latter telemetry only), or evidence that entries with `severity > 1.4` occur, which would make the comparison non-vacuous.

---

## CHANGE 6 — serialising the nested test suite

**VERDICT: SOUND WITH CONDITIONS — serialisation is necessary and not sufficient**

**FALSIFICATION / the mechanism I would check first.** Not a lock and not a file descriptor. `pytest.ini` sets `timeout = 300` and `timeout_method = thread`. I read the installed `pytest_timeout.timeout_timer`: *"Dump stack of threads and call os._exit()"* — confirmed, four `os._exit` sites in the module. The nested invocations use longer budgets than the outer backstop:

- `bench/tests/test_every_test_file_is_collected_2026-09-01.py:174` → `timeout=600`
- `bench/tests/test_cited_evidence_is_recoverable_2026-09-11.py:197` → `timeout=1800`

A 600 s or 1800 s inner budget nested inside a 300 s outer per-test backstop means **the outer timer always fires first**, and because the thread method calls `os._exit(1)` rather than raising, the parent dies without reaping the child. The nested pytest tree is orphaned and keeps its ~365 MiB. Under xdist (3.8.0 installed) with eight outer workers on 1.9 GiB of headroom, repeated orphaning is sufficient on its own to produce the symptom he describes — the machine becomes unusable and the run never completes — and **serialising the nested run does not touch it**.

Three conditions, all checkable before the run: (1) make every nested `subprocess.run` timeout strictly **less** than `pytest.ini`'s 300 s, or set a per-test `@pytest.mark.timeout` above the inner budget on exactly those tests; (2) wrap the nested call so the child is killed on the parent's exit path — `os._exit` skips `finally`, so this needs `start_new_session=True` plus a process-group kill from a watchdog, not a `try/finally`; (3) serialise the **outer** suite's nested tests against each other, not just the inner run — eight outer workers each running a serial inner suite is still eight concurrent suites.

**WHAT WOULD REFUTE ME.** A reproduction on his machine showing the inner budgets are never approached (every nested run finishing well under 300 s), in which case the orphaning path is never entered and memory pressure from concurrency is the whole story — and serialisation alone would then suffice.

**COLLATERAL.** The brief notes that adding the 3 uncollected discipline-checker files was "attempted and deliberately reverted, because enlarging the collected list enlarges the nested run". That reasoning disappears under fix (1): if the nested run is bounded and reaped, the three files can be collected, and 4 broken tests hiding behind a 1,439-passing report is a verification-integrity defect in its own right.

---

## CHANGE 7 — the pre-registered adaptive quiet-run rule

**VERDICT: SOUND WITH CONDITIONS — the procedure is right, the chosen signal is not the best one in its own producer's table**

**FALSIFICATION.** The brief's figures do not match the committed producer. Running `bench/can_any_signal_see_a_premature_close_2026-10-27.py`:

| | brief | producer |
|---|---|---|
| `findings_count` | AUC 0.9345, CI [0.7978, 1.0000] | AUC 0.9058, CI [0.7494, 1.0000], n=29 |
| `registry_total` | AUC 0.8542 | AUC 0.8693, CI [0.6999, 1.0000], n=30 |
| third signal | "a residual average … on only 3 cases" | `rho_avg` AUC 0.0455, CI [0.0000, 0.1309], **n=25** |

And the third row is the finding, not a nit. **`rho_avg` discriminates far better than `findings_count`**: |AUC − 0.5| = 0.4545 with a CI of width 0.1309 that excludes 0.5 by a margin of 0.369, against `findings_count`'s 0.4058 with a CI touching 1.0000. Pre-registration §1 names `findings_count` "primary and single" on the strength of a figure that is not the producer's, and dismisses `rho_avg` as resting on 3 cases when the producer says 25. **Fix §1 before freezing**, or justify in writing why the better-separating signal is rejected.

**Is `findings_count` confounded with run length?** Almost certainly, and the archive can separate them. Fire points carry `round_idx`; regress the premature label on `findings_count` **and** `round_idx` jointly, or use the rate `findings_count / round_idx`. If the rate discriminates and the count does not, it is richness; if the reverse, it is length. Do this before fitting T, because if it is length the rule reduces to "run longer runs longer", which is `max_rounds`, not an adaptive gate.

**Does floor-at-3 make it untestable in the direction that matters?** Yes, and that is a real limitation — a rule that can only add rounds cannot detect closing too late. But §5's decision measure does capture the cost: "blocks NO MORE sound closes" is exactly the late-closing penalty, measured. The asymmetry is a design choice with a stated cost, not a blind spot.

**Is 30 the right count?** No; it is arbitrary in the same way 3 and 7 were. What should set it: a power calculation for the Fisher test in §5 at the smallest adoption-worthy effect — e.g. +2 of 8 premature blocked at 0 additional sound blocks. Run that calculation and let it name n. Until it does, 30 is the third constant in a document whose whole argument is that constants must be earned.

**Is it simpler than K = 3?** No. It is K = 3 plus T plus the `+1` increment: two new constants, one of them fitted. The pre-registration's honesty about this is its best feature, but §4's "countdown rather than an argument" is correct only if the countdown is enforced — nothing in the repository blocks T being set at 8 labels.

**WHAT WOULD REFUTE ME.** A second producer, committed, emitting 0.9345 and the 3-case residual figure, and showing `rho_avg` is recorded at only 3 fire points under the "first firing per run" restriction the brief describes but the committed producer does not implement.

---

## CHANGE 8 — the 0.7 severity proxy re-measured, directive corrected

**VERDICT: SOUND WITH CONDITIONS**

**FALSIFICATION.** Both artefacts reproduce — `scripts/the_severity_proxy_was_never_tested_2026-10-28.py` runs clean, and `pytest bench/tests/test_the_severity_proxy_was_never_tested_2026-10-28.py` plus the barrier file gives `35 passed in 3.21s`. The argument's load-bearing step, §7b, holds: 2,807 of 3,237 entries (0.867161, CP [0.854982, 0.878672]) sit outside the audited band and 0.794744 of all CRITICAL calls sit above it. I could not break that.

What I did break is the **numbers the brief quotes**. The script is seeded (`np.random.default_rng(SEED)`), so these are not run-to-run noise:

```
   power against the strong effect (slope 4.394449): 0.1490      <- §4
   ... power against it is 0.1460                                <- VERDICT, same run
   full-range n =  63: simulated power 0.9185                    (brief says 0.9207)
   minimum detectable slope 13.450855                            (brief says 13.450854)
```

**The script emits two different values for the same quantity within a single run** — 0.1490 in section 4 and 0.1460 in the verdict. A directive is being withdrawn on the strength of a power figure the producer reports twice with two values. Condition: make the two call sites share one computation, re-run, and quote what it prints.

**Is "strong relationship" a straw man?** Partly. 2 ln 9 is a legible round number, not a derived one. The effect size actually at stake is whatever slope makes 0.7 the *right* cut — i.e. the slope at which P(CRITICAL) crosses 0.5 at severity 0.7. The band cannot detect that one either: its minimum detectable slope is 13.45, three times the "strong" 4.39. So the conclusion survives a better-chosen effect size, but the brief should state the decision-relevant slope rather than the legible one.

**The strongest objection — "only the band matters" — is answered, and the answer holds.** The gate acts at the cut only in the sense that the *comparison* happens there; the *classification* happens wherever the severity was assigned, and 0.794744 of CRITICAL calls were assigned above 0.74 where nothing invites a second look. Correction, not pedantry. What would settle it: adjudicate a stratified sample — say 20 above 0.74, 20 in band, 20 below 0.65 — and report per-stratum kappa. If the above-band stratum agrees well, the original sentence was adequate.

**Non-monotonicity.** If the 5 clauses are orthogonal to magnitude, no n helps and the costed ask is wasted. This is not hypothetical: the script already reports mean severity of NON_CRITICAL (0.695426) marginally *above* CRITICAL (0.692424). Condition: the 63-item adjudication must be designed to test monotonicity — rank correlation across the full range — and not only to estimate a slope.

**Lumpy distribution.** Yes, it overstates. 633 of 3,237 sit at exactly 0.5 and **174 sit at exactly 0.7, on the cut itself**, where the dichotomisation is a coin toss on rounding. Re-run the full-range power simulation by *resampling the empirical severities with their ties* rather than treating severity as continuous; expect the n = 63 power of 0.9185 to fall.

**Is a power-based withdrawal legitimate with no new labels?** Yes, and this meets the standard. The withdrawn claim is an *acceptance of a null* — "agrees no better than chance". Accepting H₀ is only licensed by adequate power against the alternative, and the power is 0.146. The standard a withdrawal should meet is exactly this: show the original claim's inferential form requires a quantity nobody computed, and compute it. It does, and they did. The conditions above are about arithmetic hygiene, not legitimacy.

**On change 5.** The 25-point reclassification argues for **both**, but the full-range adjudication first. Re-auditing the band after promotion measures a population that the promotion itself reshapes, which is the same circularity the shadow reader was criticised for.

---

## CHANGE 9 — the completion barrier

**VERDICT: SOUND**

**FALSIFICATION.** `scripts/what_a_round_waits_on_its_slowest_seat_2026-10-28.py` reproduces exactly: median idle 0.144892, CI [0.105753, 0.181047], seat counts `{2: 78, 5: 4, 7: 6}`, 4 of 92 rounds excluded. `pytest bench/tests/test_the_completion_barrier_is_measured_2026-10-28.py` passes. The mechanism is wired to a real caller — `bench/confer_maths_panel_2026-09-05.py:1903` calls `completion_barrier` and writes `completion_barrier.json` — and both `dispatch` return paths stamp the epochs (lines 1001 and 1034, the success and `except Exception` paths). It satisfies the additive standard: new code, reached by a caller, executed by a test.

**Is the mtime reconstruction sound?** Conditionally, and the bound is weaker than claimed. `wall ≤ Σ durations + 20 s × seats` excludes rounds where the *reconstruction* is broken only when the breakage inflates wall clock. A reply file touched *earlier* than its true completion — or a round whose seats all finished before a later unrelated write — produces an under-estimate that the bound cannot see, because under-estimates satisfy it trivially. The bound is one-sided. I found no second writer of reply files in `star_topology_2026-10-06.py`, which supports the assumption, but the one-sidedness means the 0.144892 is a **lower bound with an unbounded upper tail**, and should be reported as such. The prospective instrumentation removes the problem entirely, which is the right call.

**Is a barrier a fault?** Not inherently, and the brief is right to ask. Barrier idle is a **cost worth paying** when the round is genuinely collaborative — every seat's prompt for round *k+1* includes every seat's reply from round *k*, so the wait buys cross-seat information. It is **waste** when the barrier gates work that does not consume the slow seat's output: writing the round log, computing gamma, persisting the registry, or dispatching a seat whose prompt does not include the laggard. The 0.144892 is mostly the first, because the star topology's defining property is that every seat reads every other. So: a real cost, correctly measured, and *not* yet shown to be waste.

**If it is waste, which fix?** A **deadline that truncates the slowest seat**, and nothing else. Partial barriers and start-from-whoever-has-landed both change what a round *means* — they make a seat's input set depend on scheduling, which destroys the comparability of rounds across runs, and this project's entire archive rests on that comparability. A deadline keeps every seat's input set identical (all landed replies as of time T) and costs exactly one thing, stated plainly: the truncated seat contributes nothing that round, and the round log must say which seat and why.

**The 4-or-more-seat direction: hold.** Six rounds, and Brunner-Munzel at p = 0.104133 is the right test here precisely because the spreads differ markedly (the condition under which Mann-Whitney's equal-spread assumption fails). Two of three tests agreeing is not robustness when the disagreeing one is the appropriate one. **I would act at n = 20 rounds at ≥4 seats**, with Brunner-Munzel as the primary test — that is roughly the n at which it has 0.8 power against the observed 0.25 median gap given the observed spread, and it is reachable within a few instrumented runs.

**Do the epoch stamps leak or move anything?** `elapsed_s` is retained and no consumer recomputes from the endpoints — I grepped; `completion_barrier` is the only reader of the new fields. They are wall-clock epochs on a local machine, so they reveal when a run happened, which the directory timestamps already reveal.

---

## DISAGREEMENT

1. **Change 3.** I expect the orchestrating model to hold that 0.741791 justifies the change. It does not: the same producer's replay says 1 of 31, p = 0.5, and 4 of its 5 exhibited false suppressions are same-kind. **The evidence favours me**, and it is the orchestrator's own producer.
2. **Change 5.** I expect disagreement that the promotion is "reached" — the committed test `test_the_promotion_releases_a_proven_specification_subcritical` asserts it is. It *is* reached; my claim is that what it reaches is a tautology. z3 unsat and Wolfram's maximum of 1/2 settle it. **Evidence favours me.**
3. **Change 5, the interaction.** The brief predicts the masking runs through the critical count. It does not — `crit_s` is identical with the flag on. **Evidence favours me**, but the brief's *conclusion* (that change 5 eases convergence) is right for a reason it did not identify; see INTERACTIONS.
4. **Change 2.** I expect pushback that the missing producer is a citation slip, not a defect. Under `measured-rate-travels-with-its-script` it is the defect that standard exists to catch, and the AUC intervals say the signal is blind. **Evidence favours me on the citation; the orchestrator is right that 0.41 still beats 0.30**, which is why my verdict is conditional rather than UNSOUND.
5. **Change 7.** I expect the pre-registration to be defended as frozen. §1 picks the weaker of two discriminating signals on a figure the producer does not emit. **Evidence favours me**, and this is cheap to fix before freezing.
6. **Change 6.** I expect "serialisation is sufficient" because it is what he asked for. `os._exit` in `timeout_timer` plus inner timeouts of 600/1800 against an outer 300 says otherwise. **Evidence favours me**, though I grant I have not reproduced the deadlock on an 8 GiB machine.
7. **Change 9.** I expect the seat-count effect to be quoted as established. Brunner-Munzel at p = 0.104 on n = 6 is the correct test and it does not clear. **Evidence favours me**; the brief half-concedes this already.

---

## WASTED EFFORT

**Change 5.** It is the single change most likely to make tonight's run worthless, for two compounding reasons. First, it will not produce the evidence the promotion decision needs: the quantity the brief measures (835 of 3,298 crossing the cut) does not reach the convergence gate's critical series at all, so the run cannot observe the distortion it is being run to observe. Second, it contaminates everything else the run measures: releasing proven UNCONFIRMED entries from the A4 door makes this run's convergence behaviour non-comparable with all 62 archived runs, which is the baseline changes 1, 2 and 7 are all evaluated against. Run tonight **without** `--severity-spec`; the shadow telemetry is recorded unconditionally, so nothing is lost by waiting.

---

## INTERACTIONS

**Change 5 × changes 1 and 2 — real, but one layer upstream of where the brief looked.** `--severity-spec` does not shrink `crit_s`. It shrinks `blocking_entry_ids`, and `_check_hardened_convergence` evaluates the A4 block **before** it ever reaches the gamma and window tests:

```
if _unresolved_crit > 0:
    telem["mode"] = "a4_blocked"
    return False, ...
```

So the effect is not that the gate passes more easily — it is that **the gate is consulted at all, in runs where A4 would previously have refused**. Over the archive, 30 of 3,630 entries are proven UNCONFIRMED and would be released. Changes 1 and 2 only bind on runs that get past A4; change 5 increases that population. The false-quiet problem is not masked by a lower critical count, it is masked by an earlier door opening. Both effects point the same way, which is why the brief's instinct was right.

**Change 5 × change 8 — the same problem stated twice.** Change 8 establishes the 0.7 cut's agreement with the consequence rubric has never been measured where severity varies. Change 5 moves the quantity the cut is applied to — from asserted severity onto `asserted · V`, whose in-play range is [0, 0.5] — and leaves the cut at 0.7. You cannot promote 5 before 8's adjudications land, because 8 is what would tell you where the cut belongs on the new scale. Treat them as one item.

**Change 3 × change 4(a) — a composition with no demonstrated advantage.** Both reduce subject-tier over-blocking. The anchor in `propose_from_chat` already escapes the tier through `_distinct`, and the brief's own account of the 2026-10-27 incident says all 5 questions failed because the anchor was omitted, not because of kind. By the producer's replay the kind filter adds 1 recovered item at p = 0.5 on top of that. That is composing two fixes because they can be composed, which the founder's 2026-10-02 ruling forbids. Prefer the anchor alone.

**Change 1 × change 2 — no adverse interaction found.** The conjunction means each side must pass independently; lowering K and raising θ do not cancel. They correlate positively through the shared `crit_s`, which makes the conjunction weaker than nominal. Report the joint block rate rather than the two marginals.

---

## UNREPRODUCIBLE

1. **Change 2's entire case.** `bench/can_any_signal_see_a_premature_close_2026-10-27.py`, the producer named in `reference_runner_v3.py` for it, emits none of 0.3173, 0-of-8, 4-of-8, or Fisher p = 0.029355. Its whole output is the 15-line AUC table quoted above.
2. **Change 7's headline AUCs.** 0.9345 / [0.7978, 1.0000] and 0.8542 do not reproduce; the producer gives 0.9058 / [0.7494, 1.0000] and 0.8693. The "residual average on only 3 cases" does not reproduce either: `rho_avg` is n = 25.
3. **Change 8's power figures.** 0.1460 and 0.9207 do not reproduce; the seeded script gives 0.1490 (§4) / 0.1460 (verdict) — two values for one quantity in one run — and 0.9185. Minimum detectable slope 13.450854 against the script's 13.450855.
4. **Change 3's 1,340 / 994.** These do reproduce from the committed producer, but they are not the decision-relevant quantity, and the quantity that is — 1 recovered of 31 at p = 0.5 — is in the same output and is not cited.

---

**Files delivered into the repository tree, all executed:**

- `scripts/harvest_tickets_2026-10-17.py` — `CANDIDATE_LINE` repaired to a provable superset
- `bench/tests/test_the_chat_prefilter_is_not_a_superset_2026-10-28.py` — 3 passed
- `bench/tests/test_the_kind_filter_reopens_the_cross_kind_rediscovery_2026-10-28.py` — 4 passed
- `bench/tests/test_the_severity_spec_annihilates_the_a4_severity_door_2026-10-28.py` — 5 passed

`bench/reference_runner_v3.py` and `bench/ticket_store.py` are **unmodified**: in both cases I wrote a patch, measured it, and withdrew it because it failed the project's own additive standard. One pre-existing failure, unrelated to anything I touched, is in `bench/tests/test_ticket_harvest_2026-10-17.py::test_the_seeded_store_holds_three_integrity_properties` — settled ticket `97c0008fff1f` conceals open task `T1`.

### fable, blind, 29,671 characters, 72 tool calls, 1021.3 s

All evidence is in. Composing the verdict.

---

# PANEL VERDICT — seat report, 2026-10-28

## CHANGE 1 — REQUIRED_QUIET_RUN reverted 7 → 3

**VERDICT: SOUND WITH CONDITIONS.**

**FALSIFICATION:** I ran `scripts/quiet_run_brief_figures_2026-10-25.py` and `scripts/is_any_live_config_still_on_the_old_quiet_run_2026-10-18.py`. Output: `first_fire_k3 = 8 of 30 = 0.266667, Wilson [0.1418, 0.4445]` — matches the brief; `posterior_k7_denominator = 0` — K=7 fires zero times in 63 reports; "NO LIVE FORWARD-LOOKING CONFIG IS STILL ON THE OLD VALUE." My attempt to refute — that 3 re-opens false-quiet — half-lands: 3 carries a 26.7% false-quiet rate, but 7 is a gate **nothing reaches**, which the project's own additive standard names as not additive (`test_the_raised_quiet_run_removes_the_windows_rather_than_blocking_them` now pins exactly this: at 7 the archive holds 0 premature windows, so the arm was made unreachable, not safe). An unreachable gate is strictly worse than a reachable one with a measured error rate.

Is 3 defensible? Yes, **conditionally on change 2 holding**: of the 8 false-quiets at K=3, the 0.41 gamma arm blocks 4, so the residual is ~4/30 = 0.1333, Wilson [0.0533, 0.2966]. What I would measure: exactly what item 7 pre-registers — `findings_count` at the firing point on every future close, so the residual 4 become attributable rather than folklore.

**WHAT WOULD REFUTE ME:** a committed measurement showing quiet runs of length 7 occur in future instrumented runs (the 0-of-409 could be an artefact of runs ending at the gate, which truncates the quiet-run distribution — runs stop *because* they went quiet, so long quiet runs are censored by construction). Nobody has measured that censoring.

**COLLATERAL:** `gamma_alt_consecutive_zero_crit = REQUIRED_QUIET_RUN` (line 1664) — the revert silently changes the hardened gate's window W too (line 11201). That is one constant feeding two gates; the brief mentions only one.

---

## CHANGE 2 — gamma_alt_threshold 0.30 → 0.41

**VERDICT: SOUND WITH CONDITIONS.**

**FALSIFICATION:** I recomputed the statistics independently. scipy: one-sided Fisher on [[4,4],[2,20]] = **0.0293545535**, odds ratio 10.0; Wolfram Language (local kernel): `1 − CDF[HypergeometricDistribution[6, 8, 30], 3]` = **0.02935455349…** — agreement to 10 decimals, as claimed. Wilson 4/8 = [0.2152, 0.7848] ✓. The old threshold gives p = 1.000000 ✓. `pytest bench/tests/test_gamma_does_not_cover_the_quiet_arm_2026-10-08.py` — 13 passed, including the inverted assertions pinning 0.41.

My strongest refutation attempt, and it partly lands: I ran `bench/can_any_signal_see_a_premature_close_2026-10-27.py`. Its own table says **gamma at the firing point is BLIND: AUC 0.3466, 95% CI [0.1337, 0.5595] — the interval spans 0.5**. The continuous signal does not significantly discriminate premature from sound; the significant Fisher p appears only after dichotomising at a cut chosen on the same 30 cases. That is the signature of in-sample threshold selection. The LOO stability claim (0.4140/0.4585 in 8 of 8 folds, runner comment line 1650) mitigates but does not cure it — LOO on 8 positives tests stability of the argmax, not out-of-sample performance. Yes, 0.41 is fitted to 8 positive cases. What saves it: the failure cost is asymmetric. The gamma arm can only *block* convergence; its worst failure is wasted rounds, never a wrong close. A tuned constant whose failure mode is caution is a different risk class from one whose failure mode is a false pass.

**WHAT WOULD REFUTE ME:** the first ~10 instrumented closes showing sound-blocked rising above the 2/22 baseline (i.e. a sound close firing with γ ∈ [0.30, 0.41)); or the item-7 LOO protocol at 30 labels showing 0.41 blocks no more prematures than 0.30.

**COLLATERAL (unmentioned in the brief):** `scripts/recalibrate_gamma_threshold_reachability.py` output — exp46's live peak gamma is **0.3357**, inside [0.30, 0.41). At 0.41 a run like exp46 can **never** converge via the gamma arm at all; it exits only via max_rounds or HIL. Reachability at the new threshold drops from 10/13 to 9/13 live runs, and the pre-registered anti-cooking condition (b) was frozen at 0.30 on 2026-05-17 — the brief does not say the frozen reachability bar has been moved post hoc.

---

## CHANGE 3 — subject tier respects `kind`

**VERDICT: SOUND WITH CONDITIONS.**

**FALSIFICATION — the named case, executed, not hypothesised:** I ran a fresh `TicketStore`, settled a `pf` on subjects `(propose, subject_tier)`, then re-proposed **the same item, reworded, as `fr`**, with no anchor or task_ref. Output:

```
settled pf: created | SAME item re-raised as fr: created
same-kind reworded pf: subject-settled
```

A true rediscovery that crosses the fr/pf line now **enters the store**. The founder's 2026-10-19 rationale — "resolutions travel in opposite directions" — is true of qs vs pf, but **fr and pf resolutions travel the same direction**: both are discharged by implementing the mechanism. "Add X" (fr) and "fix by adding X" (pf) are routinely one item. The suite's anti-vacuity guards are same-kind only; this cross-kind case is uncovered.

**WHAT WOULD REFUTE ME:** a measurement over the live store showing the fr↔pf slice of the 994 cross-kind blocks is dominated by genuinely distinct items (the producer's false-suppression examples are qs↔pf and fr↔fr, so my case may be rare in practice). That measurement does not exist; it should, before the risk is accepted. I am NOT proposing a repair — both refused repairs show the cure space is treacherous, and the simplest sufficient response is to measure the fr↔pf share first.

**COLLATERAL:** 3 store-adjacent tests are failing in the shipped tree right now (confirmed pre-existing by reverting my change-4 patch and re-running): `test_the_seeded_store_holds_three_integrity_properties` fails with "settled tickets conceal open work: 97c0008fff1f hides ['T1']" — an over-merging failure in the live store, the very defect family this change addresses, and the brief does not mention the suite is red here. Also reproduced: the producer's replay shows the kind check recovers only **1** false suppression, Fisher p = 0.50 — the change's standalone benefit is directionally right but not demonstrated at significance; its justification is the 0.741791 cross-kind share, which counts blocks, not wrong blocks.

---

## CHANGE 4 — the harvester's chat half

**VERDICT: UNSOUND as argued (superset claim is false) — FIXED, fix delivered and tested. The repair's other parts (anchor, filters, honest 0-of-0) are sound.**

**FALSIFICATION:** The "provable superset" proof has a hole: JSON **does** escape the whitespace that MARKER's left context accepts — as `\n`, `\t`, `\uXXXX` — and those escapes end in a **word character** (`n`, `t`, a hex digit), which destroys the left `\b` on the raw line. Executed falsifier (imports the real module):

```
FALSIFIED: decision accepts, prefilter rejects raw line:
  kind='pf' text='plan for tonight:\npf: raise the gamma th'
  kind='qs' text='items follow\tqs: does the star round nee'
  kind='wr' text='list:\xa0wr: finish the adjudication of the'
AssertionError: CANDIDATE_LINE is NOT a superset of the decision
```

The exact blind spot of the OLD prefilter — markers mid-message after a newline — survives in the new one for every multi-line message, because `from_chat` normalises whitespace (line 331) before deciding, while the prefilter reads the raw line.

**FIX, delivered at the real paths and executed:**
- `scripts/harvest_tickets_2026-10-17.py` — `CANDIDATE_LINE` is now `r"(?:fr|pf|qs|wr)\b"` (left context unconstrained; the right `\b` is safe because every right context MARKER accepts maps to a non-word char or a backslash escape in raw), with the corrected proof in the comment.
- `bench/tests/test_candidate_line_is_a_superset_2026-10-28.py` — the falsifier as a committed test, plus a 500-case seeded randomised superset check. Output: `2 passed`. Falsifier re-run post-fix: `clean: prefilter admitted every decision-accepted case`.

**On keeping the chat half at all:** keep it. The producer (`the_chat_half_was_blind_2026-10-28.py`, re-run: 258,146 lines, 0 genuine raisers, truth table 12/12) shows it is correct-and-empty, costs ~30 s per harvest, and is the only channel by which the founder *can* raise a marker in chat. Do **not** add an unmarked-question predicate — any classifier of "is this chat turn a question worth a ticket" is a tuned constant pretending to be a finding, against a 2,858-ticket store; the right channel for markerless founder questions already exists and derives its anchor: `propose_from_chat`.

**WHAT WOULD REFUTE ME:** a transcript writer in this project that `\u`-escapes ASCII letters (then even my fix under-admits; I checked the stated assumption but not every writer).

---

## CHANGE 5 — `--severity-spec` promoted to DECIDING tonight

**VERDICT: SOUND WITH CONDITIONS — the implementation is narrower and safer than the brief implies, but tonight's run design contradicts the runner's own documented staging.**

**FALSIFICATION:** I read the implementation rather than the brief's description. Three facts the brief omits, all load-bearing:

1. `effective_severity` decides at **one site only** — the blocking-criticals predicate (line 4263) — and release there is **conjunctive**: `_sev < 0.7 AND severity_is_proven(e)`. An unproven halved severity buys nothing. The runner's own pre-build measurement: only **7 of 2,994** archived entries would actually be released.
2. **The 25-point reclassification does not reach the convergence arms changes 1–2 configure.** `_settled_novelty_series` (line 10659) reads **raw** `e["severity"]` — so the K-consecutive-zero-critical count and gamma_critical are byte-identical with the spec on or off. The feared masking of false-quiet via easier criticality is architecturally bounded to the blocking count.
3. REFUTED findings never blocked anyway (line 4268 blocks only *unresolved* falsifiers), so the key property's gate-level effect is through V=0.5 halving, not V=0.

On shadow-vs-decide: the registry retains asserted severities and `severity_spec_shadow` is recorded unconditionally (line 11254), so both **classifications** are recoverable from one run — but the counterfactual **trajectory** (which rounds would have run had the gate not fired earlier) is not. That is the true replay-invalidation residue, and it is small given fact 2.

**THE CONDITION:** the runner's own comment (lines 10378–10380): *"Free run 1 measures the directive repair with this OFF; free run 2 turns it ON. Running both changes at once would make neither attributable."* Tonight's run turns on the spec **and** reverts the quiet run **and** moves the gamma threshold. If convergence behaves differently, nothing is attributable to anything — the run's own code says so. Changes 1–2 are archive-derived and need no run to validate; change 5 is the one that needs the run. Either accept the attribution loss explicitly or stage it.

**WHAT WOULD REFUTE ME:** a call site I missed where `effective_severity` or `_SEVERITY_SPEC` feeds the novelty series or gamma. I grepped every call site (3: lines 4263, 10425 def, 21269 telemetry); refute me with a fourth.

**COLLATERAL:** none found beyond the attribution issue; the flag is wired (`run_simulated_experiment.py:341 → RunnerConfig:2008 → wire_module_mirrors`, executed by test per the `execute-do-not-grep` conversion note at line 10387).

---

## CHANGE 6 — serialising the nested test suite

**VERDICT: UNSOUND as proposed — serialisation is a no-op. Fix for the actual mechanism delivered.**

**FALSIFICATION:** I ran the committed producer `scripts/the_nested_suite_is_bounded_not_serial_2026-10-28.py`. Its output refutes the proposal's premise directly:

```
-- hypothesis 1: the nested run is parallel and needs serialising
   hook_pytest_invocation: OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1)
   hook_uses_xdist: False
   ini_has_addopts: False
   verdict: both runs are already serial
```

Both the outer and nested runs are **already sequential**. "Run it sequentially" cannot fix a deadlock in a system that is already sequential. The producer also rules out fork-lock inheritance (spawn is the default) and refutes its own author's thread-timeout hypothesis.

**The mechanism I would check first**, and the one the producer's residual-risk section names: **13 of 22 subprocess launches in `test_precommit_restages_repairs_2026-09-11.py` carried no timeout** (0.5909, Wilson [0.3873, 0.7674]). Each nested `git commit` runs the full ~334.5 s GUARDS board; a wedged child blocks forever; pytest-timeout's `thread` method then kills the **outer** pytest process while the inner pytest/git tree runs on as an orphan — orphan trees at ~365 MiB each accumulate on an 8 GiB machine and present exactly as "deadlocks rather than merely running slowly." Secondary mechanism to keep in view: adding the 3 precommit test files to the GUARDS board (the reverted attempt) creates hook↔test **mutual recursion** — commit → hook → board → precommit test → commit → … — which no serialisation bounds either; I confirmed the board (hooks/pre-commit:115) currently excludes them, so depth is 2 today.

**FIX, delivered and executed:**
- `bench/tests/test_precommit_restages_repairs_2026-09-11.py` — all 13 unbounded launches now carry `timeout=900` (the sibling file's own derived bound: 2.7× the measured 334.54 s board; "a hang still fails rather than hanging" is that file's stated B37 property). AST-verified: patched exactly the producer's 13 named lines; file re-parses; 42 tests collect.
- `bench/tests/test_nested_suite_launches_are_bounded_2026-10-28.py` — committed falsifier asserting zero unbounded launches across all 3 nested files. Output: `1 passed`. Producer re-run: `0 of 22 launches carry no timeout = 0.000000, Wilson [0.000000, 0.148655]`.

**WHAT WOULD REFUTE ME:** a reproduction on the 8 GiB machine showing the hang persists with every launch bounded — that would point to the one mechanism I could not test here (memory pressure alone: outer tree + inner board + git ≈ 1 GiB against 1.9 GiB headroom is tight if anything else is open, and swap-thrash is indistinguishable from deadlock to an operator).

---

## CHANGE 7 — the pre-registered adaptive quiet-run rule

**VERDICT: SOUND WITH CONDITIONS — the procedure-freezing is the right instinct, but the registration has two defects that must be repaired BEFORE freezing, and its headline figures do not reproduce from the committed producer.**

**FALSIFICATION:** I ran `bench/can_any_signal_see_a_premature_close_2026-10-27.py`. It emits `findings_count AUC 0.9058, 95% CI [0.7494, 1.0000], n=29` and `registry_total 0.8693` and `rho_avg n=25, AUC 0.0455`. The brief quotes **0.9345 [0.7978, 1.0000], p = 0.002163**, **0.8542**, and a residual average "on only 3 cases". None of the brief's three figures is what the committed producer prints today. The discriminating-signal conclusion survives (CI lower bound 0.7494 > 0.5), but under `measured-rate-travels-with-its-script`, a pre-registration quoting numbers its producer does not emit must be corrected before it is frozen.

Answers to the questions put:
- **Confound.** Partially — but mostly it is the mechanism, not a confound: findings-so-far estimates the run's defect density, and remainder is proportional to density. The genuine confound is firing-round: later fires accumulate more findings. The archive records round indices at fire, so it **can** separate them — fit `premature ~ findings_count + firing_round` logistic and report the partial effect. Do this before fitting T.
- **Floor-at-3 directionality.** Yes, the rule is structurally blind to closing-too-late. That is a deliberate asymmetry (late costs budget; early costs validity) but the registration should SAY it measures one direction only, or the eventual dominance test will be read as a full evaluation.
- **Is 30 right?** As written, the registration is **internally inconsistent**: "fitted only when at least 30 labelled closes exist, against the 8 available today" — but 30 labelled closes exist **today** (8 premature + 22 sound; the producer's own header: "30 fire points"). Either it means 30 labelled *premature* closes (~110 total at the 26.7% rate — a long countdown) or the trigger is already met and the countdown is fiction. What should set the number: the power of the pre-registered LOO Fisher dominance test, computed the way change 8 computed power — not a round count. Fix the sentence before freezing.
- **Simpler?** No. It is K=3 plus 2 constants (T and the +1) wearing an adaptive label — the registration should own that; its justification is the dominance test, not simplicity.

**WHAT WOULD REFUTE ME:** the producer being re-run against a pinned archive snapshot reproducing 0.9345 exactly — then the discrepancy is archive growth, not an instrument fault, and only the pin is missing.

**COLLATERAL / INTERACTION WITH CHANGE 2 (serious, unmentioned):** future labelled closes are collected from runs already filtered by the 0.41 arm. The premature closes 0.41 blocks **never become labels**. The training distribution for T is therefore censored by change 2, non-stationarily — the adaptive rule will be fitted on exactly the prematures the gamma arm missed. The registration must state the labels are post-0.41 and that T is being fitted to the gamma arm's residual, not to the original population.

---

## CHANGE 8 — the 0.7 proxy re-measured, directive corrected

**VERDICT: SOUND — the withdrawal is justified and the power argument is correctly constructed. Two instrument defects to repair, neither overturning the verdict.**

**FALSIFICATION:** I ran both named commands. `pytest … -q`: **23 passed**. The producer reproduces the whole chain: analytic SE 4.801159 vs fit 4.862883; in-band OR prediction 1.256464 inside [0.516836, 1.569980]; 0.7921 of 20,000 draws inside the measured interval; readers at kappa 0.836883; full-range n=63 power 0.92.

My strongest attempt to refute, pressed as instructed:
- **"Only the band matters."** I reject it, and not only on the producer's 0.7947-above-band figure. The gate's decisions are not confined to the cut: a 0.9-severity entry the rubric's five clauses would call non-material **blocks convergence wrongly** (it sits in the blocking count and the novelty series), and nothing about 0.9 invites a second look — a decision error invisible precisely because it is confident. The original sentence was adequate for the one decision it was used in (the replacement proposal acted at the cut); it was inadequate as the general claim CLAUDE.md made of it. The correction is not pedantry; the measurement that settles it is the 63 full-range adjudications **stratified above/below the band, reporting the decision-flip rate among the 1,119 above-band CRITICAL calls**.
- **Straw man?** No — in the direction used. The 2 ln 9 slope is a round benchmark, but the argument is a fortiori: power 0.146 against a LARGE effect bounds power against the realistic effect from above. The effect actually at stake for the gate is the decision-flip rate at and above 0.7, and no slope parametrisation is needed to say the band cannot measure what it never sampled.
- **Non-monotone.** The logistic power figures are conditional on monotonicity and should be quoted as such — but the 63-item ask survives non-monotonicity: full-range adjudication is exactly what *detects* a non-monotone relationship (AUC ≈ 0.5 with structure in the residuals), where more in-band sampling never could. The costed ask is not wasted under the objection; it is the test of it.
- **Lumpy distribution.** Handled correctly: the power simulation draws the archive's own severities (point masses included), not an idealised continuum. Verified in the producer's §4 (analytic SE validated against the real fit to 1.3%).
- **Withdrawal standard.** A directive asserting a measured negative is refuted by showing the measurement could not have detected the effect it claims to exclude. That requires no new labels — it is a claim about the instrument, decidable from the instrument's own data. Met. The contamination point (up to 206 of 259 verdicts possibly formed with the number in view) cuts the way the brief says: contamination inflates agreement upward, observed agreement is ≤ 0, so the clean in-band null is at least as strong.

**Two defects found:** (1) The producer's VERDICT section hardcodes "power against it is 0.1460" (line 447) while the live, **unseeded** simulation printed **0.1490** this run — a figure that moves on re-run cannot travel with its script; seed the RNG and make the verdict text read the computed value. (2) The brief says power 0.9207 at n=63; the producer printed 0.9185 this run — same unseeded cause.

**WHAT WOULD REFUTE ME:** the 63 adjudications coming back with full-range kappa ≈ 0 **and** high reader-reader agreement — that would mean the proxy is genuinely chance-level everywhere and the original directive was accidentally right; the correction's "uninformative, not negative" framing would then have been too generous to the proxy, not too harsh.

---

## CHANGE 9 — the completion barrier, instrumented and measured

**VERDICT: SOUND WITH CONDITIONS.**

**FALSIFICATION:** I ran both named commands: producer reproduces every headline figure exactly (median idle share 0.144892, CI [0.105753, 0.181047]; 255.9 s median; 14.11 h total; 13/88 over 0.30; seat counts {2:78, 5:4, 7:6}; corroboration delta 0.039350); `pytest …` — **12 passed**. I verified the mtime assumption's load-bearing premise in source: `_preserve_prior_attempt(_reply_path)` (confer_maths_panel line 1038) runs **before** the reply write (line 1040), so prior attempts are renamed, not overwritten. The wiring satisfies the additive standard: `dispatch` stamps both epochs on success (line 1001) and failure (line 1034) paths; `completion_barrier` is called at line 1903 and writes `completion_barrier.json`.

Answers:
- **mtime soundness.** Sound for the round's own writes; the wall-cannot-exceed-serial bound is a *necessary* condition only — it excludes impossible reconstructions, not plausible-but-wrong ones (any post-run tool that rewrites a reply file in place would inflate idle while staying inside the bound). This is acknowledged obliquely; it should be said plainly. The prospective instrumentation moots it, which is the right design.
- **Cost or design?** The barrier is the price of the collaboration contract *wherever a later round consumes the replies*. It is waste in exactly two places: the **final round** (nothing consumes the barrier) and the tail where the slowest seat's reply is a timeout record rather than content. The 0.144892 median is therefore an upper bound on waste, not a measurement of it; decompose it by round position before calling it a cost.
- **The fix I would defend:** none yet. Partial barriers and deadline truncation change what a collaborative round means; the committed instrumentation is the correct next step and the only one the additive standard currently licenses.
- **Act on the seat-count direction?** Hold. n=6, and the one test robust to unequal spread (Brunner–Munzel, p = 0.104) does not confirm. Act when Brunner–Munzel goes significant — at the observed effect size roughly n ≈ 15–20 instrumented 4+-seat rounds.
- **Epoch leakage/consumers:** `elapsed_s` retained; `completion_barrier` is the only new consumer of the epochs I could find (grep across bench/ and scripts/); no existing figure changes. Absolute epochs in a local research archive leak nothing beyond what file mtimes already did.

**WHAT WOULD REFUTE ME:** the first instrumented runs reporting idle shares far from the mtime estimate's CI — that would void the 88-round retrospective and the 14.11 h figure with it.

---

# CROSS-CUTTING FIELDS

## DISAGREEMENT

1. **Change 2, with the orchestrating model:** it presents 0.41 as "DOMINATES rather than trades." I say the producer's own AUC table shows gamma-at-fire is not significantly discriminative (0.3466, CI spans 0.5), so the dominance is an in-sample artefact of cut selection with LOO-stability as partial cover. The evidence favours me on the statistics (their own instrument printed it) and favours them on the decision (asymmetric failure cost makes the fitted cut acceptable anyway). I expect the writing seat to resist the word "fitted"; it should not — item 7's own text concedes the principle.
2. **Change 7's figures:** the writing seat will say archive growth explains 0.9345 → 0.9058. Possibly — but then the brief violated measured-rate-travels-with-its-script by quoting unpinned numbers, and the evidence (the producer's live output) favours me until a pinned snapshot reproduces 0.9345.
3. **Change 3:** the writing seat holds the founder's kind ruling fully general; I hold its rationale (opposite resolution directions) false for fr↔pf, with an executed demonstration that a cross-kind rediscovery now enters the store. Evidence favours me on the existence of the case; favours them on expected frequency (unmeasured by both of us — which is my point).
4. **Change 6:** the founder proposed serialisation; his own commissioned producer refutes the premise. Evidence favours the producer. I expect other seats to defer to the founder here; deference is not evidence.
5. **Change 5:** the brief's framing ("25-point reclassification is replay-invalidating") overstates — I say the implementation bounds the effect to one conjunctive site and the novelty/gamma arms are untouched (code at line 10659). Evidence favours me; I read the call sites.

## WASTED EFFORT

**Change 5** is the likeliest to waste the run — not because it is wrong, but because tonight's configuration runs it simultaneously with changes 1 and 2, and the runner's own comment (lines 10378–10380) states that running both at once "would make neither attributable." If the run converges differently from the archive's expectations, three explanations will be on the table and the run will decide among none of them. Second place: change 2's 0.41 making an exp46-like article unable to converge via the gamma arm at all, burning the run to max_rounds.

## INTERACTIONS

1. **5 × (1, 2) — the suspected one, resolved by code reading:** the severity spec does **not** make the quiet-count or gamma sides of the two-sided gate easier; `_settled_novelty_series` reads raw asserted severity. The masking channel is only the blocking count, conjunctive with `severity_is_proven`, measured at ~7 of 2,994 archived entries. The interaction is real, small, and bounded — but the **attribution** interaction (which change moved tonight's convergence behaviour?) is unbounded and is the one to worry about.
2. **2 × 7 — label censoring (new, I believe unnoticed):** every future labelled close used to fit T comes from runs already filtered by the 0.41 arm, so T will be fitted to the gamma arm's *residual* premature population, not the population the AUC was measured on. The pre-registration should name this before it freezes.
3. **4 × 3 — converging on the same defect:** anchors on every harvested item (4a) shrink the population exposed to the subject tier that change 3 modifies. Under the founder's composability standard, the composed benefit of (anchor fix + kind filter) over the anchor fix alone is **not yet demonstrated** — the replay measured the kind filter recovering 1 false suppression at Fisher p = 0.50. The kind filter's justification is currently a rate (0.7418) that counts blocks, not wrong blocks.
4. **1 × 2 — one constant, two gates:** `REQUIRED_QUIET_RUN` feeds both the quiet arm and the hardened gate's window W; the revert moved both. Anyone evaluating "did 3 reopen false-quiet" must hold 0.41 fixed, or the two reverts confound each other — which tonight's run, running both, does not do.

## UNREPRODUCIBLE

1. **Change 7's AUC figures as quoted** (0.9345 / [0.7978, 1.0000] / p 0.002163; 0.8542; "3 cases" for the residual signal): the committed producer emits 0.9058 / [0.7494, 1.0000] / no p-value / 0.8693 / n=25. Not reproducible as stated.
2. **Change 2's LOO claim** ("0.4140 or 0.4585 in 8 of 8 folds"): exists only as a comment in `reference_runner_v3.py` (line 1650); I found no committed script that emits it. The 4/8, 2/22, 0.3173 figures do have an executing producer (`claim_gamma_does_not_cut_the_joint_rate`, exercised by 13 passing tests), but the LOO fold table does not.
3. **Change 8's 0.1460 / 0.9207**: reproducible only to ±0.003 because the producer's simulation is unseeded while its verdict text is hardcoded — printed 0.1490 / 0.9185 on my run. Repair: seed the RNG, interpolate the computed value into the verdict.
4. Everything else I ran reproduced exactly: 8/30 and its Wilson interval, Fisher 0.0293545535 (scipy and Wolfram Language to 10 decimals, computed on the local Wolfram Engine), 0.741791 context, the completion-barrier figures to 6 decimals, and the chat-half 0-of-0.

**Files delivered into the repository tree:** `scripts/harvest_tickets_2026-10-17.py` (prefilter fix), `bench/tests/test_candidate_line_is_a_superset_2026-10-28.py` (falsifier, 2 passed), `bench/tests/test_precommit_restages_repairs_2026-09-11.py` (13 launches bounded at 900 s), `bench/tests/test_nested_suite_launches_are_bounded_2026-10-28.py` (falsifier, 1 passed; producer re-run confirms 0 of 22 unbounded).

That is my verdict on all nine. The run should proceed only after the Change 5 attribution decision is made explicitly and Change 7's registration text is corrected — everything else is condition-noting, not blocking.

## REQUIRED SECTION 8 — Standards

Hold these to the project's standards: `execute-do-not-grep`, `additive-standard` in BOTH directions, and `measured-rate-travels-with-its-script`. A figure without a committed producer is a claim about evidence, not evidence -- as 2 of CC1's own figures in the blind brief proved.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 45 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_the_nine_changes_2026-10-28) -->

All evidence is in. Both splits resolve, and they resolve on a defect neither seat found.

---

# JOINT ROUND — third seat, 2026-10-28

I did not sit the blind half, so I have no verdict to change. What follows is de novo, and it moved both splits.

---

## THE FINDING THAT DECIDES BOTH SPLITS: the `premature` label is the observation window

`fire_points` (`bench/can_any_signal_see_a_premature_close_2026-10-27.py:124`) labels a fire position with `premature = any(h > 0 for rounds AFTER it)`. **`any([])` is False.** A fire point with no recorded round after it is labelled SOUND — not observed clean, *not observed*. Executed against the archive:

```
tail  0:  10 fire pts   premature  0  sound 10     <- any([]) decided these
tail  1:  10 fire pts   premature  0  sound 10
tail  2:   2 fire pts   premature  2  sound  0
tail >=3:  8 fire pts   premature  6  sound  2

AUC of TAIL LENGTH ALONE as a predictor of the label:
   0.971591   CI [0.888203, 1.0]   n=8/22
Spearman(tail, premature) rho = 0.751455  p = 1.70325e-06
median tail | premature = 11   | sound = 1    MWU p = 2.88125e-05
```

Twenty of thirty labels — two thirds — are "sound" from runs that stopped at the fire point. Not one of the 8 premature labels comes from a tail shorter than 2. **Tail length out-separates every signal in the committed table, `findings_count` (0.9058) included.** Both seats asked "is `findings_count` confounded with run length?" and both proposed `premature ~ findings_count + round_idx`. That regression cannot fix this, because the *dependent variable* is a function of recorded length. It is length scored against length.

This is not fatal to change 7 — dropping the non-falsifiable labels **sharpens** `findings_count` (below). It is fatal to the denominator everything else is argued on.

---

## SPLIT 1 — CHANGE 3. REAL, AND IT DISSOLVES. Both seats measured correctly; neither measured the pair.

Nobody broke the 994 down by ordered kind pair. Executed on the live store (2,879 tickets):

```
realised (proposed <- blocker) suppressions, pre-change:
   fr <- fr : 2      qs <- qs : 2      qs <- pf : 1

the 0.741791 denominator:
   (subject,kind) pairs counted: 1340
   pairs where a ticket of that kind EXISTS on that subject: 348
   HYPOTHETICAL share of the denominator: 0.740299
```

**The only realised cross-kind suppression in 2,879 tickets is `qs` blocked by `pf` — the founder's exact pair, and no other.** cc2 is right that 0.741791 counts hypotheticals: 0.740299 of it is pairs for which no such ticket exists. fable is right that the general form admits an fr↔pf duplicate; I reproduced it (`settled pf -> re-raised as fr : created`). Both true, because they measured different populations — and the pair breakdown shows the two measurements are the same fact: the general form bought nothing outside `qs↔pf` and sold deduplication on five kind pairs to get it.

**VERDICT: the shipped general form is UNSOUND. The narrow form — the question/work split — is SOUND, and dominates by count, not by judgement.**

```
  pre      suppressed 5 of 31
  general  suppressed 4 of 31   recovers ['524186098488']
  narrow   suppressed 4 of 31   recovers ['524186098488']
  recovered by GENERAL but NOT by NARROW: []        <- set difference EMPTY
```

Identical recovery, strictly smaller admission surface. That is the committed measurement the removal standard demands.

**FIX, delivered at its real path and executed.** `bench/ticket_store.py:855`:

```python
blocked = [b for b in self.settled_on_subject(sub)
           if (b.kind == "qs") == (kind == "qs")]
```

A question is a distinct item from work on the same subject; work items of any kind still block each other. No constant added. Executed against the real module after the patch:

```
settled pf -> re-raised as fr : subject-settled   <- fable's hole, closed
settled pf -> raised as qs    : created           <- his 2026-10-19 ruling, intact
settled pf -> reworded pf     : subject-settled   <- anti-vacuity guard, intact
```

`bench/tests/test_the_subject_tier_splits_questions_from_work_2026-10-28.py` — **5 passed**, including a live-store replay that fails the moment a realised cross-kind suppression appears that is not `qs←pf`. Adjacent suites: **46 passed** (`test_ticket_store_2026-10-17`, `test_a_question_is_its_own_kind_2026-10-19`, `test_ticket_harvest_2026-10-17`, `test_the_ticket_gate_states_2026-10-24`, plus both new files).

**ON CC1's QUESTION — additive at 1-in-31, or an addition nothing reaches? Neither: 1-in-31 is the wrong denominator.** The ruling is about `qs` against work kinds. The realised population of that pair in the whole store is **1**, and the narrow form reaches **1 of 1** — 100% of the case he ruled on, not 3% of something else. That is additive. The *general* form is worse than non-additive: it is a **removal**, of deduplication across five kind pairs, justified by 0.741791 — a judgement dressed as a measurement, since 0.740299 of that figure is pairs that do not exist. Removal requires a committed measurement showing the replacement dominates. There was none. There is one now, and it points the other way.

cc2's proposed action — revert the kind filter entirely, keep only the anchor — I reject, and on cc2's own composability reasoning: the narrow predicate is not a second mechanism composed onto the anchor, it is *one line already present*, narrowed. Reverting it re-breaks his ruling at the only site where that ruling is realised.

---

## SPLIT 2 — CHANGE 2. THE THIRD OPTION EXISTS, AND IT IS NOT A THIRD THRESHOLD.

I supplied cc2's own refutation condition: a permutation null over the threshold sweep. 20,000 permutations, seeded:

```
tail>=0 (n=30): best sweep theta=0.414  uncorrected Fisher p=0.029355
   SWEEP-CORRECTED permutation p = 0.074246
tail>=1 (n=20): best sweep theta=0.414  uncorrected Fisher p=0.057792
   SWEEP-CORRECTED permutation p = 0.114144
```

**cc2's refutation condition is met in the negative: the permutation null does not keep p < 0.05.** And the uncorrected Fisher decays under label repair: 0.029355 → 0.057792 (tail≥1) → 0.777778 (tail≥2). fable is right that 0.029355 is the signature of in-sample cut selection; I have now quantified it.

**But the dichotomy CC1 accepted — "a fitted cut or a harmful one" — is false, and that is the third option.** `{γ < 0.30} ⊆ {γ < 0.41}`. The comparison is **nested on the same 30 fire points**, so it is paired, and Fisher's independent 2×2 is simply the wrong statistic for the decision taken. The paired statistic:

```
newly blocked by moving 0.30 -> 0.41: 4 closes, premature 4, sound 0
sound closes blocked:  2/22 at theta=0.30  ==  2/22 at theta=0.41   (IDENTICAL)
exact binomial, all newly blocked premature vs base rate 4/15:
   p = 0.005057      (tail>=1, base 0.4: p = 0.025600)
```

Second falsifier, Wolfram Language (local Wolfram Engine, via `wolframscript`): `1 - CDF[HypergeometricDistribution[6,8,30],3]` = `0.02935455349248452697` and `(4/15)^4` = `0.00505679012345679012`, agreeing with scipy to the digits shown.

Raising the cut costs **zero** additional sound closes on the archive and captures 4 prematures. That is dominance in the strict sense, it is a paired claim, and it does not depend on the swept Fisher p at all.

**VERDICT: SOUND. Keep 0.41. Withdraw the Fisher p, not the word "dominates".** CC1 conceded the wrong half. fable is right about the statistic and wrong about the decision; cc2's "0.41 still beats 0.30" is right and under-argued. The third option, stated plainly: **report the paired statistic and fix the label set — both free, neither a new constant.** There is no third *threshold*; there was never a need for one.

On fable's exp46 collateral (peak γ 0.3357, reachability 10/13 → 9/13): real, and it is a run-budget cost, not an evidence cost — see below.

---

## LABEL CENSORING — NEITHER REMEDY CC1 OFFERED. fable's mechanism is real and runs the OPPOSITE way.

I read the label-generating code rather than reasoning about closes. `fire_points` builds a row from the **quiet series alone** — line 135 tests only `recs[j][2] == 0`. Nothing in it consults gamma, the gate's verdict, or whether the run closed. The row exists for every run with a K-quiet window, blocked or not.

The gamma arm returns `False` (`reference_runner_v3.py:10025`) — it blocks the close; the run **continues**. More rounds are recorded. The tail **grows**. `any(h > 0)` becomes **more** likely.

> **The 0.41 arm does not delete premature labels. It converts sound labels into premature ones.** T fitted on post-0.41 data sees an *inflated* premature rate, not a residual one.

So:
- **"Fit T unfiltered" is wrong on the merits, not merely expensive.** T is deployed *alongside* the gamma arm. The estimand is P(premature | signals, arm active). The filtered population **is** the deployment population. Unfiltered fitting costs runs to estimate the wrong conditional.
- **"Name it" propagates an error**, because the direction named in the brief is backwards.
- **exp46 is not censored.** A run that never reaches 0.41 burns to max_rounds and therefore records a *long* tail after its fire point — it labels, and labels well. fable's reachability finding stands as a run-budget cost; it is not a label cost.

**THE REMEDY: fix the label definition before T is fitted. Cost: zero runs.** Delivered into `bench/can_any_signal_see_a_premature_close_2026-10-27.py` — `tail_rounds` carried on every row, the unobserved count printed **unconditionally**, and `--min-tail` to drop labels that could not have been refuted. Default 0, so every cited figure still comes out of the default invocation:

```
default:        fire points 30  (8 premature, 22 sound)
                of these, 10 were labelled SOUND over an EMPTY tail
--min-tail 1:   fire points 20  (8 premature, 12 sound)  -- 0 prematures lost
```

`bench/tests/test_a_sound_label_is_an_observation_not_an_empty_tail_2026-10-28.py` — **5 passed**, including one asserting the flag is reached and one asserting the default moves no published figure.

The pre-registration should name `--min-tail` as part of T's fitting protocol. That is the whole remedy.

---

## STRONGEST DISAGREEMENT WITH CC1's FRAMING — and it is a correction in CC1's favour

Section 8 says "2 of CC1's own figures in the blind brief proved" the measured-rate standard. **On change 7 that charge is false, and both seats got it wrong.** Run the committed producer on the falsifiable-label subset:

```
--min-tail 1:   findings_count  AUC 0.934524  CI [0.797777, 1.0]
                registry_total  AUC 0.854167
brief quoted:   findings_count  AUC 0.9345    CI [0.7978, 1.0000]
                registry_total  AUC 0.8542
```

Exact, to every digit quoted. cc2 listed these as UNREPRODUCIBLE #2; fable as UNREPRODUCIBLE #1 and demanded a pinned snapshot. Neither is needed: CC1 was analysing the labels that could be refuted, and the committed producer's **default** was the weaker analysis. That is still a `measured-rate-travels-with-its-script` defect, but it is the **inverse** of the one charged — the script was weaker than the figure, not the figure weaker than the script. The flag now makes the restriction speakable, so the figure travels. (The "residual average on only 3 cases" still does not reproduce: `rho_avg` is n=15 at `--min-tail 1`, n=25 at default. That one is a real citation error.)

The second-strongest disagreement: CC1's concession on change 2 gave up the correct half. "Dominates" is defensible; the Fisher p is not.

Not reproduced from any producer I could find, and I agree with fable: the leave-one-out fold table (`0.4140/0.4585`, 8 of 8) exists only as `reference_runner_v3.py:1650`. The 4/8, 2/22, 0.3173 and p = 0.029355 figures **do** reproduce — I re-derived all four directly from the archive — but `claim_gamma_does_not_cut_the_joint_rate` lives in `bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py`, not in the file the runner comment cites. cc2 overstated by concluding no producer exists; fable located it. Fix the citation.

---

## WHAT WOULD REFUTE ME

- **Split 1:** one realised cross-kind suppression in the live store that is not `qs←pf` — `test_the_split_recovers_exactly_what_the_general_form_recovers` goes red the moment one appears. Or a worked case where `fr` and `pf` resolutions genuinely travel in opposite directions.
- **Split 2:** evidence that 0.41 was pre-registered rather than swept, which would void the sweep correction; or a recount showing the sound-block sets at 0.30 and 0.41 differ, which would destroy the paired dominance.
- **The label finding:** evidence that the 10 empty-tail runs were confirmed clean by some channel outside the round log. Then their "sound" labels are earned, the 0.9716 is run-length truncation rather than unobservation, and `--min-tail` is discarding good data.

---

## STOP

**Both splits are resolved, not unresolvable.**

Split 1 resolved by the ordered-pair count: one realised cross-kind suppression in 2,879 tickets, and it is his pair. Narrow form shipped, tested, dominant. Split 2 resolved by the nested comparison: 0.41 keeps its value and loses its p-value. Label censoring resolved: direction inverted, remedy is a label repair at zero run cost, shipped and tested. A further pass would restate. Stopping.

**Files delivered into the tree, all executed:**
- `bench/ticket_store.py` — subject tier narrowed to the question/work split (46 adjacent tests green)
- `bench/tests/test_the_subject_tier_splits_questions_from_work_2026-10-28.py` — 5 passed
- `bench/can_any_signal_see_a_premature_close_2026-10-27.py` — `tail_rounds`, `--min-tail`, unconditional unobserved count; default reproduces every published figure
- `bench/tests/test_a_sound_label_is_an_observation_not_an_empty_tail_2026-10-28.py` — 5 passed

Opened nothing new. One pointer for DISAGREEMENT, not a tenth item: `cross_kind_share`'s docstring in `scripts/the_subject_blocklist_grows_with_every_close_2026-10-28.py` claims 0.741791 is "exactly what the kind check recovers". It is refuted by its own replay in the same run, and 0.740299 of its denominator is hypothetical. That docstring needs correcting wherever the figure was cited.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 35 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_the_nine_changes_2026-10-28) -->

Wolfram Language (local Wolfram Engine): 0.0293545535 — agrees with scipy to 10 digits. All evidence is in. Composing the joint verdict.

---

# JOINT VERDICT — fable seat, fix_review_panel_2026-10-28

## SECTION 1 — Which split is real, which is a label

**SPLIT 2 (change 2) was a LABEL.** Both blind verdicts were SOUND WITH CONDITIONS; the apparent split was two citation conditions and one word. Both are now discharged mechanically (below). **SPLIT 1 (change 3) was REAL** — UNSOUND-revert vs SOUND-retain is a genuine disposition conflict — and it is now **resolved by measurement, against the revert**.

## Split 1 — change 3: RETAIN THE SHIPPED FILTER. cc2's revert is refuted.

Delivered and executed: `bench/tests/test_the_kind_filter_three_variants_measured_2026-10-28.py` (**3 passed**), measuring kind-ignorant vs shipped vs a narrow qs-only exemption on the three documented case families, with the real `propose` tied to the simulated column:

| case | evidence | ignorant | shipped | narrow-qs |
|---|---|---|---|---|
| A: settled pf vs new qs (founder's ruling) | live: qs:524186098488 blocked by pf:028f975075d0 | ✗ | ✓ | ✓ |
| B: settled pf vs genuinely-new fr | live: namespace-paths incident 2026-10-17, pinned by `test_a_new_kind_is_not_absorbed_by_a_settled_one` | ✗ | ✓ | ✗ |
| C: settled pf vs same item reworded as fr | constructed (my blind demo); 0 live occurrences | ✓ | ✗ | ✓ |

**No variant dominates. Shipped is the unique variant right on both documented-live cases.** B and C are inseparable by kind alone — identical `(kind, subject)` call shape, differing only in text — and text-similarity repairs were already tried and refused twice (recorded in the module cc2 cites). So cc2's UNSOUND fails twice on the project's own standards: (i) its 1-in-31 replay measures recovery only and is blind to case B, which the committed suite pins to a live incident the anchor hatch demonstrably did not prevent (the caller omitted the anchor; 291/907 = 32% of tickets carry neither task_ref nor anchor); (ii) the revert is a REMOVAL, and the additive standard demands a committed measurement that kind-ignorant dominates — the executed table shows it loses A and B to win C.

**Answer to CC1's attack question:** implementing the ruling at 1-in-31 **is additive**. "Reached" is satisfied three ways: wired at `ticket_store.py:855`, executed by a committed test, and discharging two documented live incidents. 1-in-31 measures the wrong population (anchorless replay of existing items) and even there the filter is +1 recovery at zero added suppression. But CC1 under-defends its own position: the justification need not retreat to the ruling alone — the measured table above *is* a justification, and it is stronger than the withdrawn 0.741791. My remaining condition from the blind round (measure the fr↔pf share of the 994 for C-type admissions) stands as monitoring, not a blocker.

## Split 2 — change 2: 0.41 STANDS; "fitted" is now a measurement, not an accusation; and the third option exists in kind, not in value

Delivered and executed: `scripts/the_gamma_cut_figures_travel_with_this_script_2026-10-28.py`, importing fire-point extraction from the committed signal producer. Output:

- **Every contested figure reproduces**: min premature gamma **0.3173**; θ=0.30 blocks 0/8 premature, 2/22 sound, Fisher p = 1.000000; θ=0.41 blocks **4/8** premature, **2/22** sound, Fisher one-sided **p = 0.029355** (scipy; Wolfram Language local kernel: 0.0293545535, 10-digit agreement). cc2's condition (1) is discharged — the figures were true but uncommitted, the exact defect `measured-rate-travels-with-its-script` exists to catch. My own blind claim that `claim_gamma_does_not_cut_the_joint_rate` was their producer was **wrong** — I verified tonight it measures 23 premature *windows*, not the 8 gate-fire closes, emits none of the four figures, and its emitted block count (4 of 23) contradicts its own in-file comment (2 of 23). I withdraw that sub-claim.
- **The LOO comment is vindicated**: the optimal cut is the flat interval **(0.3927, 0.4140]**, containing 0.41, in **8 of 8** leave-one-out folds. "0.4140" was the interval's upper endpoint. It now has a producer.
- **"Fitted" is confirmed mechanically**: permutation null over the full threshold sweep (20,000 shuffles, seeded) gives **selection-corrected p = 0.0758**. The in-sample 0.0294 does not survive correction at 0.05. CC1's concession was correct and is now a number.
- **cc2's condition (2) re-derived on `gamma_critical`, the series the gate reads: NOTHING is derivable** — premature n = 1 at the fire points, and 8 of 20 recorded sound closes sit below 0.41.

**The third option, named:** there is **no third value** tonight — on that CC1 is right, and 0.41 (inside the LOO-stable optimal interval, perm p 0.076, failure mode caution-only) beats both 0.30 and arm-removal on everything measured. But the choice is not binary either. The third option is in kind: **instrument `gamma_critical` recording at every fire point and re-derive the cut on the gate's own operand at the pre-registered label count** — the entire 0.41-vs-0.30 case was argued on the `gamma` proxy series, and on the operand series the evidence is indeterminate for prematures and adverse-leaning for sound closes. Plus one non-optional repair: the frozen 2026-05-17 reachability condition (b) was set at 0.30 and exp46's live peak is 0.3357 (re-confirmed tonight: reachability 10/13 → 9/13) — the freeze must be amended explicitly, not moved silently.

## Label censoring (2 × 7) — the remedy, decided by data

**Name it AND fit T on the post-censoring labels, which is what accrues naturally. Do NOT run gamma-disabled rounds.** Measured tonight: the 0.41 arm censors exactly the **low-count** prematures (findings_count 4, 7, 7, 8); the survivors are 13, 13, 24 against sound closes at 1–10; on the residual population `findings_count` separates perfectly (AUC 1.0, n=3 — directional, not conclusive). The censoring is *complementary*, not adversarial: gamma catches the prematures findings_count would miss. Fitting T on an unfiltered labelled set would train it on prematures the deployed arm already removes — whose counts overlap the sound range — dragging T down into the sound distribution at a cost in sound closes. So unfiltered fitting is not merely expensive in runs; it targets the wrong population. Two obligations in the pre-registration text: (i) state that labels are post-0.41 and T is conditional on θ = 0.41, to be refitted if θ moves; (ii) re-verify `findings_count`'s discrimination on the residual population before fitting T, since tonight's n=3 preview cannot carry that weight alone.

## SECTION 5 — What would refute me

- **Change 3:** a replay over the full 994 cross-kind pairs showing C-type duplicate admissions occur live at a rate exceeding B-type false suppressions — then the table's tiebreak (documented occurrences) flips.
- **Change 2:** evidence that the recorded `gamma_critical` telemetry is not the gate's operand at fire (my 8/20 sound-block concern then evaporates); or future labels pushing the permutation-corrected p below 0.05 (then "fitted" ceases to be a reservation).
- **Censoring:** the next labelled prematures arriving with low findings_count despite surviving the gamma arm — breaking the complementarity measured on n=3.

## SECTION 6 — Verdicts, changes, disagreement

**Split 1: resolved — change 3 SOUND WITH CONDITIONS, filter retained; the revert is refuted by the executed three-variant table.** **Split 2: resolved — a label; change 2 SOUND WITH CONDITIONS, both citation conditions now discharged by a delivered producer.**

**Blind-verdict changes (fable):** I keep both verdict labels but correct two sub-claims. (1) Change 2: my blind assertion that the 4/8–2/22–0.3173 figures had an executing producer was wrong — verified tonight, and repaired by delivering one. (2) Change 3: my blind framing of the fr↔pf arm as pure unmeasured risk was incomplete — the committed namespace-paths test pins a live false suppression that same arm discharges; my "measure first" condition demotes from blocker to monitoring.

**Strongest disagreement with CC1's framing:** "a choice between a fitted cut and a harmful one" conducts the entire decision on the `gamma` proxy series. The gate compares against `gamma_critical`, where the archive supports **no cut at all** (premature n=1) and shows 8/20 recorded sound closes below 0.41. The fitted-vs-harmful binary is real but it is a binary *on the wrong series*; the operand-series instrumentation is the missing third option, and the silently-superseded 0.30 reachability freeze (exp46 peak 0.3357) must be amended in writing. Secondarily: on change 3 CC1 retreats further than the evidence requires — the ruling need not carry the retention alone; the measured case-family table carries it.

**Pointer, not a 10th item:** `bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py` emits `gamma_above_threshold_on = 19` of 23 (4 blocked) while its consuming test's comment states "blocks 2 of 23" — one of the two is stale; neither tonight's splits nor the run depend on it.

**Files delivered into the tree, all executed:** `scripts/the_gamma_cut_figures_travel_with_this_script_2026-10-28.py` (runs clean, writes `experimental_notes/data/gamma_cut_figures_2026-10-28.json`); `bench/tests/test_the_kind_filter_three_variants_measured_2026-10-28.py` (3 passed). Wolfram used once as second falsifier; it computed; value attributed to Wolfram Language.

## SECTION 6b — Stop

Both splits are **resolved on tonight's evidence**: change 3 by the executed dominance table (stop criterion met — the 1-in-31 question is answered: additive, reached, retained); change 2 by naming the third option (operand-series instrumentation + freeze amendment) while confirming no third *value* exists. The censoring remedy is decided: name it, fit on post-censoring labels, no disabled-arm runs. A further pass would restate positions already carried by executed artefacts. **Stopping here.**

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_the_nine_changes_2026-10-28/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
