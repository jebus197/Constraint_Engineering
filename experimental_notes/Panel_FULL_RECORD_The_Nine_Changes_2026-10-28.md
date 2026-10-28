# The free panel refused tonight's severity promotion and found 2 defects in my own producer

Record written 2026-10-28T23:25:55+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED AND WHY. The 9 changes made on 2026-10-28 before any simulated run, on the founder's standing requirement that fixes go past a free panel first. Both seats are free (Max subscription); 0 paid seats were dispatched. The brief carried CHANGE 1 (the required quiet run reverted from 7 to 3), CHANGE 2 (the gamma arm's threshold raised from 0.30 to 0.41), CHANGE 3 (the ticket store's subject tier respecting kind), CHANGE 4 (the harvester's chat half, which had never worked), CHANGE 5 (the run configuration proposed for tonight, with --severity-spec), CHANGE 6 (the founder's own proposal on the nested test suite), CHANGE 7 (the adaptive quiet-run rule, pre-registered before being fitted), CHANGE 8 (the 0.7 severity proxy re-measured and a directive corrected) and CHANGE 9 (the completion barrier, instrumented and measured).

THE DECISION THE ROUND CHANGED. --severity-spec is NOT being passed in tonight's simulated run. Both seats reached that conclusion independently and by different arguments. cc2 established that effective_severity decides at exactly one site and that on the in-play domain V is at most 0.5, so the product of an asserted severity and V cannot reach the 0.7 cut, with z3 returning unsat for the negation and a local Wolfram Engine Maximize returning one half in agreement. The consequence is that the severity half of the release conjunction is constant-true and the A4 fail-safe collapses to severity_is_proven alone, releasing a proven asserted-1.0 unresolved critical from the one guard whose own comment says its censoring runs toward convergence. fable reached the same operational conclusion from the runner's own staging comment, which states that running the specification together with the quiet-run and gamma changes would make none of them attributable. Both seats also refuted the brief's stated risk: the settled novelty series reads raw asserted severity, so the critical series, gamma_critical and the K-round window are byte-identical with the flag on or off, which cc2 measured as identical sequences both ways. Dropping the flag additionally answers the attribution objection, because the run then varies only CHANGE 1 and CHANGE 2 against the 2 runs already completed.

WHAT WAS DONE WITH THE FINDINGS AGAINST CC1's OWN WORK. 2 defects were found in the CHANGE 8 producer and both are fixed. It shared one random generator across its power figures, so each figure depended on the order the others were computed in and on the trials count: the live run printed 0.1490 where the prose said 0.1460, and 0.9185 where it said 0.9207. Each figure now has its own seeded generator and the verdict block reads the computed values instead of restating them. Reproduced twice at the default trials, the figures are power against the strong effect 0.144250, power at n equals 63 of 0.916500, and power at the minimum detectable slope 0.798250. 33 citations were corrected across both copies of the additive-standard directive, both delivered notes, the recovery record and the brief itself. A third defect surfaced from running the producers rather than from either seat: the trials and json flags were unreachable in all 3 new producers, because the help helper defaults to refusing any argument before the caller's own parser runs, which made both flags unwired additions invisible to the guards. All 3 producers now pass the documented escape.

WHAT REMAINS OUTSTANDING FROM THIS ROUND. fable found the CHANGE 7 figures unpinned, 0.9345 against 0.9058 on re-run, which is accepted and not yet fixed. fable also raised an interaction neither CC1 nor cc2 had seen: every future labelled close used to fit the adaptive threshold will come from runs already filtered by the 0.41 gamma arm, so the threshold would be fitted to that arm's residual premature population rather than the population the discrimination figure was measured on. That is accepted outright and its remedy is the subject of the joint round. The 2 genuine verdict splits, CHANGE 3 and CHANGE 2, are carried into the joint half with CC1's own position stated as the thing to attack.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Review these fixes BEFORE they are tested in a simulated run

You are a seat on an independent review panel. The founder's standing practice
is to put proposed fixes past a free panel BEFORE spending a run on them, so
that effort is not wasted on changes that will not work. Your job is to find
what is WRONG, not to confirm what is right. There is no compelled convergence:
give your own verdict and your strongest falsification. Disagreement is kept as
information, not smoothed away.

You have no session context. Everything needed is below. Where you need to check
the code, read it in the repository at the paths named.

## Why a panel rather than more reasoning in one context

HYPOTHESIS UNDER TEST: that the 6 changes below are sound enough to spend a
simulated run on, and that the run as configured will actually exercise them.

WHAT WOULD FALSIFY IT: any one of the changes being unreachable by the run's
configuration, contradicting a measured property the project already holds, or
resting on a number with no producing script.

WHY ONE CONTEXT CANNOT ANSWER IT: the changes were made by the same context that
measured them, and 2 of its own hypotheses were already refuted by its own
instruments tonight. An independent reading is the only check on a reviewer's
blind spot about its own work.

## The project's standards you should hold these to

- `additive-standard`: never disable a feature. Removal only where a COMMITTED
  MEASUREMENT shows the replacement dominates on a named property. Symmetrically,
  an addition nothing reaches is not additive either: every new flag, gate or
  entry point must be wired to a caller and executed by a test.
- `execute-do-not-grep`: a test asserting on the SOURCE TEXT of a module proves
  only that the module describes itself consistently. Where both forms are live
  code, the test must CALL them and compare outputs.
- `measured-rate-travels-with-its-script`: a rate, proportion or count may be
  cited only if the script that produced it is committed alongside it.
- Every proportion carries a confidence interval. Every computational claim is
  cross-verified with at least 2 tools.
- Gamma is load-bearing and may not be demoted. The convergence gate is
  TWO-SIDED: `gamma_critical >= gamma_alt_threshold` AND K consecutive rounds
  with no new critical finding. Both sides must hold.

## CHANGE 1 — the required quiet run reverted from 7 to 3

`bench/reference_runner_v3.py`, `REQUIRED_QUIET_RUN = 3`.

Founder ruling, 2026-10-27: revert to 3.

Evidence behind it: across 63 archived reports covering 409 rounds, a run of 7
consecutive rounds with no new critical finding occurs 0 times; the longest
observed is 6. So the 7 setting was unreachable. The decision-relevant quantity
is P(findings remained | the gate fires), measured at 8 of 30 = 0.266667.

36 configuration files pin the old value and every one belongs to an experiment
with an archived run, so no live configuration changed.

QUESTION FOR YOU: is 3 defensible, or does reverting re-open the false-quiet
problem that motivated 7? What would you measure to tell?

## CHANGE 2 — the gamma arm's threshold raised from 0.30 to 0.41

`bench/reference_runner_v3.py`, `gamma_alt_threshold: float = 0.41`.

The defect: the lowest gamma value across all 8 premature closes in the archive
is 0.3173, which sits ABOVE the old 0.30 threshold. So the arm could never block
a premature close. Measured: it blocked 0 of 8 premature closes and 2 of 22
sound ones, Fisher exact p = 1.000000. Its only effect was to block correct
closes.

At 0.41: premature blocked rises to 4 of 8 (0.5, 95% CI [0.2152, 0.7848]) while
sound blocked stays at 2 of 22 (0.0909). One-sided Fisher exact p =
0.0293545535, cross-verified between scipy and Wolfram Language to 10 decimal
places. 0.41 was chosen because it DOMINATES rather than trades. A second
candidate, 0.4585 (Youden-optimal), catches 6 of 8 but costs 7 of 22 sound
closes; the founder ruled to keep 0.41.

QUESTION FOR YOU: is 0.41 fitted to 8 positive cases? The project has retired a
tuned constant before. Is dominance on 8 cases enough, and what would change
your mind?

## CHANGE 3 — the ticket store's subject tier now respects `kind`

`bench/ticket_store.py`, in `propose()`. It was:

    blocked = self.settled_on_subject(sub)

and is now:

    blocked = [b for b in self.settled_on_subject(sub) if b.kind == kind]

Context: `propose()` refuses to CREATE a ticket when any subject of the proposal
appears on any SETTLED ticket and the caller named no `task_ref` or `anchor`.
The 4 ticket kinds are `fr` (feature request), `pf` (proposed fix), `qs`
(question) and `wr` (work remaining). The founder ruled on 2026-10-19 that a
question and a proposed fix are different items whose resolutions travel in
opposite directions, which is why the ticket id hash digests the kind.

Measured on the live store: of 1,340 blocked (kind, subject) pairs, 994 are
blocked ONLY by a ticket of another kind, 0.741791 Wilson [0.717690, 0.764509].

<!-- figure: cross-kind blocked share | scripts/the_subject_blocklist_grows_with_every_close_2026-10-28.py | 0.741791 -->

THE ABSOLUTE COUNTS IN THAT FIGURE MOVE AND THE RATE DOES NOT. The store grew by
2 tickets between the first measurement and this brief, taking the pairs from
1,224 to 1,236 and the cross-kind count from 909 to 918 while the share moved
from 0.742647 to 0.741791. Quote the rate, not the counts. This was caught by the
dispatcher's own figure check before you saw it, which is the instrument working.

Two earlier repairs of this same defect were tried and REFUSED, and you should
know both because they bound what is acceptable:
  1. Requiring the word-overlap layer to corroborate a subject match. Refuted as
     circular: the subject tier exists to catch rewordings the word layer
     misses, so demanding its agreement destroys its value. The store fell from
     4 of 4 to 1 of 4 on the known rediscovery cases.
  2. A partial-vocabulary-overlap threshold. The 3 true rediscoveries score
     0.1429 to 0.2500 and the 2 genuinely-new items 0.0000 to 0.1111, so any
     threshold in that gap is a margin of 0.0318 fitted to 5 data points.
     Refused as a tuned constant pretending to be a finding.

The kind check adds no constant. Both anti-vacuity deduplication guards are
same-kind cases and still pass. The one guard whose expectation changed has a
docstring calling the old behaviour "THE DEFECT".

QUESTION FOR YOU: does kind-awareness weaken deduplication in a case the suite
does not cover? Name the case.

## CHANGE 4 — the harvester's chat half, which had never worked

`scripts/harvest_tickets_2026-10-17.py`, `from_chat()`.

Three faults, found in sequence:

(a) NO ANCHOR. `from_responses()` builds an anchor for every annotation;
`from_chat()` built none. An anchor is the explicit identity that lets
`propose()` escape the subject tier. So every chat-sourced item arrived with no
identity. This was the ROOT CAUSE of the over-matching. All 5 questions raised
by hand on 2026-10-27 carry neither a task reference nor an anchor, and 4 had to
be re-raised with invented subjects.

(b) A PREFILTER NARROWER THAN THE DECISION. The fast prefilter was
`r'"(fr|pf)[:\]]'` against each raw transcript line. It requires a leading
double quote, so a marker anywhere inside a message is invisible; and it omits
`qs` and `wr`, 2 of the 4 kinds, so a question marker in chat could never be
harvested at all. The function returned 0 rows for every window back to
2026-08-01.

Using the real marker regex as the prefilter was ALSO wrong: the decision runs
on DECODED text, a prefilter on the RAW JSON line, and the marker regex requires
the token to be followed by `:`, `]`, `)`, ` - ` or end-of-string, where the raw
line has JSON's closing quote. A message ending "... here pf" matches decoded
and fails raw. The prefilter is now `\b(fr|pf|qs|wr)\b`, argued to be a PROVABLE
SUPERSET of the decision: the decision can only fire if a kind token appears
literally in the decoded text, JSON never escapes ASCII letters, and the
decision's own left and right contexts each imply a word boundary.

(c) FIXING (b) ALONE MADE IT REACHABLE AND USELESS. Of the first 31 rows
returned, 0 were proposals: 24 were this session's own Stop-gate output quoted
back into the transcript, 3 were compaction summaries, and 4 only CITED an
existing ticket id, because the marker regex accepts `pf:` which is also the
form of every reference. Citation, harness-echo and code-span filters were
added.

AND THE HONEST RESULT: with all filters, decoding all 1,185 candidate lines
across 249,664 transcript lines, the number of messages whose text actually
RAISES a marker is 0. So the defect was real and cost 0 lost proposals. An
earlier draft of this work quoted a 0.92 discard rate as though proposals had
gone missing; that compared 2 raw-line predicates with each other and has been
withdrawn.

QUESTIONS FOR YOU:
  - Is the superset argument for `\b(fr|pf|qs|wr)\b` actually sound? Try to find
    a decoded text the decision accepts and the prefilter rejects.
  - The chat half was justified on the grounds that some founder questions exist
    ONLY in chat. Those questions carry no marker, so no marker-gated reader can
    reach them. Is a marker-gated chat harvester worth keeping at all, and if
    not, what predicate would work without flooding a 2,858-ticket store?

## CHANGE 5 — the run configuration proposed for tonight

`bench/tools/run_simulated_experiment.py`, with `--severity-spec`.

`--severity-spec` promotes the appendix section 7.7 severity specification from
SHADOW (recorded, gating nothing) to DECIDING. Section 7.7 states

    Sev(f) = W(class) . confidence . V(verification)
    W(HARD)=1.0, W(SOFT)=0.5; V(True)=1.0, V(None)=0.5, V(False)=0.0

with the key property that a disproved finding scores ZERO regardless of
confidence. Two of the three inputs were never collected: across 3,298 archived
entries `confidence` appears on 0 of them and no field carries a HARD/SOFT
class. The runner instead reads the model's own asserted `severity`.

The shadow reader applies V — the harness's OWN falsifier verdict — which is the
step the founder described on 2026-10-12 when he said a model must provide a
proof and the rest of the machinery must then check it with tools, and that this
is the opposite of a vote.

Measured across the archive: the share at or above the 0.7 critical cut falls
from 41.6313% (Wilson [39.9596%, 43.3225%]) to 16.3129% ([15.0912%, 17.6130%]),
with 835 of 3,298 entries crossing downward, 25.3184% Wilson [23.8636%,
26.8306%]. The appendix's key property is violated on 35 of 40 disproved
findings, 87.5000% Wilson [73.8879%, 94.5405%].

The founder ruled on 2026-10-28: implement it and measure it in the next
simulated run.

QUESTIONS FOR YOU:
  - A 25-point reclassification is replay-invalidating. Is it safe to let the
    spec DECIDE in the same run that first measures it, or must the run record
    it in shadow and promote only afterwards? The shadow telemetry is recorded
    unconditionally, so one run yields both readings — does that settle it?
  - With the spec deciding, far fewer findings are critical. The convergence gate
    requires K rounds with no new CRITICAL finding. Does `--severity-spec`
    therefore make convergence EASIER and mask the very false-quiet problem
    changes 1 and 2 address? This is the interaction we most need you to check.

## CHANGE 6 — the founder's own proposal on the nested test suite

Task entry B37: the suite contains 3 tests that run the suite inside themselves,
and on his 8 GiB machine that DEADLOCKS rather than merely running slowly. A
further 3 test files guarding the discipline checker are not collected by the
commit check, which is why 4 of them sat broken without anyone seeing; the
commit check reported 1,439 tests passing on 3 separate occasions while those 4
were failing. Adding them was attempted and deliberately reverted, because
enlarging the collected list enlarges the nested run.

His proposal, 2026-10-28, verbatim: "Can this test not be run sequentially,
similar to your sq MC command? Why risk choking up my 8GB machine and making it
unusable, or risk the tests failing to complete, when the tests can be run
sequentially, to the same effect?"

His machine: 8 logical cores, 8 GiB RAM. A pytest process tree on this
repository peaks at 364.7 MiB against roughly 1.9 GiB of live headroom. The
derived safe budget is 2 heavy and 6 light processes.

QUESTION FOR YOU: is serialising the nested run sufficient, or does a nested
pytest deadlock for a reason serialisation does not address — for example a
shared lock, a captured file descriptor, or a plugin that assumes one session
per process? Name the mechanism you would check first.

## CHANGE 7 — the adaptive quiet-run rule, PRE-REGISTERED BEFORE IT IS FITTED

This item SUBSUMES the blind round `the_quiet_run_is_not_the_lever_2026-10-25`,
which asked what the quiet-run count should be and whether an adaptive measure
could replace it. That round's joint half was never run; this round carries it.

THE QUESTION. The required quiet run is a fixed constant, K = 3. The founder's
objection is that it is arbitrary: "I remain uncomfortable however that it is
also an arbitrary number, and so far we have yet to decide if there is a
genuinely better way?" The candidate replacement is a rule that reads something
recorded at the moment of closing and decides whether to require more quiet
rounds.

WHAT WAS MEASURED, 2026-10-27. The question asked was: does ANY signal recorded
at the firing point separate a premature close from a sound one? 12 signals were
tested over the archive, with the first firing per run rather than overlapping
windows, and discrimination reported as area under the ROC curve with a
Hanley-McNeil interval.

Three signals discriminate:
  - `findings_count`, the count of findings so far: AUC 0.9345, 95% CI [0.7978,
    1.0000], p = 0.002163.
  - `registry_total`: AUC 0.8542, p = 0.009477.
  - a residual average, strongly in the inverse direction but on only 3 cases.

The direction is counter-intuitive and is the interesting part: a close is MORE
likely to be premature when the run has already found a great deal. Richness
predicts remainder. Local quiet predicts nothing, which is also why the gamma arm
was weak.

The signals proposed by an external speculative brief are BLIND: its
finding-silence signal scores 0.3097 with an interval spanning 0.5, its
residual-stability signal 0.2576 likewise, and its panel-disagreement signal is
not recorded at the firing point at all.

THE BINDING CONSTRAINT IS 8 LABELLED POSITIVES, NOT METHOD. Fitting a threshold
on 8 premature closes is exactly how K = 3 and K = 7 came about. So the
pre-registration below freezes the PROCEDURE and refuses to name a threshold now.

THE PRE-REGISTRATION, which you are asked to attack before it is frozen:

  1. SIGNAL: `findings_count` at the firing point. Primary and single. No
     composite, no weighting, because a composite fitted on 8 cases is 2 tuned
     constants instead of 1.
  2. DIRECTION, fixed in advance: higher `findings_count` means MORE quiet rounds
     required. A rule that fits the opposite direction is refused as overfitting
     even if it scores better.
  3. FORM: K_effective = 3 + 1 if findings_count >= T, else 3. One extra round,
     one threshold. The floor stays at the founder's ruled 3 so the rule can only
     ADD caution, never remove it.
  4. T IS NOT NAMED NOW. It is fitted only when at least 30 labelled closes exist,
     against the 8 available today. Every future run yields exactly 1 labelled
     close, so this is a countdown rather than an argument.
  5. DECISION MEASURE, and it is the same dominance standard the gamma arm was
     held to: the adaptive rule is ADOPTED only if, on 30 or more labelled closes
     under leave-one-out, it blocks strictly MORE premature closes than fixed
     K = 3 while blocking NO MORE sound closes, with Fisher exact p < 0.05 on the
     premature-blocking difference. If it blocks more premature closes at the cost
     of even one additional sound close, it is REJECTED and K = 3 stands.
  6. WHAT WOULD KILL IT: if `findings_count`'s AUC lower bound falls below 0.5
     once 30 labels exist, the signal is noise and the whole line is abandoned.

QUESTIONS FOR YOU:
  - Is `findings_count` confounded? The obvious objection is that premature runs
    simply have more rounds remaining and therefore more findings. Say how you
    would separate richness from run length, and whether the archive can.
  - Does the floor-at-3 form make the rule untestable in the direction that
    matters? If the true fault is closing too LATE on some runs, a rule that can
    only add rounds cannot ever detect it.
  - Is 30 the right count, or is it another arbitrary number replacing the first
     one? Name what should set it.
  - Is a single-signal rule with one threshold genuinely simpler than K = 3, or
     is it K = 3 plus 2 new constants wearing an adaptive label?

## How to work, and where a fix must land

RUN things; do not describe them. Execute the tests named above, execute the
producers named above, and read the source at the paths given. The tool output is
the evidence.

Where you propose a repair, DELIVER YOUR FIX AS A FILE: write it INTO the sandbox
repository tree at its real path, the same path the live file occupies. A fix left
in prose, or written into scratch space, is destroyed at teardown and does not
count as delivered. Alongside it, write a runnable falsifier and TEST YOUR FIX by
executing that falsifier; quote its actual output, not your expectation of it.

Use the project's own mathematical instruments where they bear on the question.
Gamma is the decay curve and is load-bearing: changes 1 and 2 are both about the
two-sided gate, so say what gamma_critical and the quiet-run count should tell
you about whether 0.41 and 3 can hold together. Severity is the quantity change 5
redefines. Every proportion you state carries a Wilson interval.

TERMINATION: stop when further reading produces no new above-threshold finding —
diminishing returns, which is this project's own criterion. Do not pad. One round
is expected; a finding is above threshold only if missing it could cause a real
failure.

## Output

Return these FIELDS, each named, for each change 1 to 7:

- VERDICT: one of SOUND, SOUND WITH CONDITIONS, UNSOUND.
- FALSIFICATION: your single strongest attempt to refute the change, naming the
  exact thing you ran or read, with its output.
- WHAT WOULD REFUTE ME: the evidence that would overturn your own verdict. State
  it even when your verdict is SOUND.
- COLLATERAL: anything the change breaks that this brief does not mention.
- FIX: where you judge the change unsound, the repair, delivered as a file at its
  real path in the sandbox repository tree, with the falsifier you executed.

Then, once, across all 7:

- DISAGREEMENT: name every point on which you expect the other seat, or the
  orchestrating model that wrote these changes, to disagree with you, and say
  which of you the evidence favours. This is a required field. Do not reconcile
  and do not defer: a round that converges by deference is not evidence, and
  preserved disagreement is the useful output.
- WASTED EFFORT: which single change is most likely to make tonight's simulated
  run wasted effort, and why.
- INTERACTIONS: any interaction between changes that reviewing each alone would
  miss. Change 5 against changes 1 and 2 is the one suspected here — whether
  letting the section 7.7 severity specification decide makes convergence easier
  and so masks the false-quiet problem changes 1 and 2 exist to fix. Say if you
  find others.
- UNREPRODUCIBLE: anything cited above as measured that you believe cannot be
  reproduced from the committed producers.
## CHANGE 8 — the 0.7 severity proxy, re-measured, and a DIRECTIVE CORRECTED

ADDED AFTER THIS BRIEF'S FIRST VALIDATION, on the founder's instruction of
2026-10-28: "Then do the measurement first." It is the newest item here and the
only one that corrects a standing project directive, so attack it hardest.

THE CLAIM BEING WITHDRAWN. `.claude/CLAUDE.md` and the global copy both say the
founder's catch of a rubric-replacement proposal rested on "a rubric it had
already measured as agreeing no better than chance (kappa = -0.0227, Fisher
p = 0.78)". Both figures reproduce EXACTLY: kappa = -0.022688, Fisher
p = 0.778818, odds ratio 0.900790, over the 259 judgeable items of
`experimental_notes/adversarial_records/rubric_adherence_audit_0C8_2026-09-02.json`.
The 2x2 is [[114, 67], [51, 27]].

WHY THE FIGURES CANNOT CARRY THAT SENTENCE. The audited corpus holds severities
in [0.65, 0.74] ONLY, standard deviation 0.026915, against the archive's full
[0.0, 1.0] and 0.224319 over 3,237 registry entries in 62 runs. The band is
0.132839 of all archive severities. Consequences, measured rather than asserted:

  - the analytic standard error 4.801159 matches the real fit's 4.862883 to
    1.3%, so the power model is validated on the data and not on an idealisation;
  - power against a strong relationship -- P(CRITICAL) running 0.10 at severity 0
    to 0.90 at severity 1, slope 2 ln 9 = 4.394449 -- is 0.144250;
  - that strong hypothesis PREDICTS an in-band odds ratio of 1.256464 -- the
    EXACT expected marginal figure, from the 0.051992 of severity separation the
    0.7 cut achieves inside the band; the first-order exp(beta . delta-mean) step
    gives 1.256682, a relative error of 0.0174%, so nothing rests on the
    approximation. The measured interval [0.516836, 1.569980] contains it,
    alongside 1.0;
  - and 0.792050 of 20,000 simulated draws under that same hypothesis produce a
    point estimate INSIDE the measured interval, median 1.260417. The observation
    is not merely compatible with the strong hypothesis, it is the MODAL outcome
    under it.

So the corpus cannot separate "no relationship" from "a strong relationship".
The pair is UNINFORMATIVE about the rubric, not negative about it.

WHAT WAS RULED OUT FIRST. Dichotomisation is not the cause: continuous severity
predicts the rubric verdict no better inside the band (logistic slope -4.199407,
p = 0.387828; Mann-Whitney p = 0.308546), and the mean severity of NON_CRITICAL
items, 0.695426, is marginally HIGHER than CRITICAL's 0.692424.

THE FALSIFICATION IT SURVIVED. If range restriction were a blanket excuse it
would also make the rubric's readers look unreliable in the band, collapsing this
into "the labels are noise". It does not: the 2 blind readers agree with EACH
OTHER at kappa 0.836883 on the 93 items both judged (raw 0.924731, Fisher
p = 6.230872e-17) while agreeing with the proxy at +0.016913 and +0.157562,
neither significant. Restriction bites the continuous predictor, not the binary
construct both readers judge.

SAMPLE SIZE IS NOT THE PROBLEM. Drawing the same 259 severities from the full
archive instead raises power against the strong relationship from 0.144250 to
1.0000 and drops the minimum detectable slope from 13.450854 to 1.7380.

A TENSION I AM RAISING MYSELF RATHER THAN WAITING FOR YOU TO FIND IT. The audit's
method line records severity "withheld and redacted from 80 of 286 texts", and NO
per-item redaction flag is stored, so up to 206 of 259 verdicts may have been
formed with the number in view. Contamination inflates agreement TOWARD positive.
Observed agreement is already at or below zero, so the uncontaminated in-band
agreement can only be worse. That STRENGTHENS the in-band null and leaves the
out-of-band question untouched -- but say so if you think it cuts differently.

AND THE STRONGEST OBJECTION DOES NOT SURVIVE THE ARCHIVE, which is why it is
answered here rather than only asked of you. Of 3,237 registry entries, 2,807 --
0.867161, Clopper-Pearson [0.854982, 0.878672] -- were classified at a severity
the audit never examined: 1,119 above 0.74 and 1,688 below 0.65. And 1,119 of
the 1,408 CRITICAL calls the gate has ever made, 0.794744, sit ABOVE the band.
Those are its CONFIDENT calls, where a disagreement is more consequential than
one at the cut, because nothing about a severity of 0.9 invites a second look.
Attack that if you can; it is the load-bearing step now, not the power argument.

WHAT IS OWED THE FOUNDER AS A RESULT: 63 full-range adjudications against the 5
clauses of `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`.
Simulated power 0.916500; about 48 reaches 0.80. The closed form says 35 and is
OPTIMISTIC, simulating 0.6472, so it must not be quoted. No model can supply the
labels: peer-model CONFIRM votes are forbidden as evidence here.

RUN THIS, do not reason about it:
  python3 scripts/the_severity_proxy_was_never_tested_2026-10-28.py
  python3 -m pytest bench/tests/test_the_severity_proxy_was_never_tested_2026-10-28.py -q

QUESTIONS FOR YOU:
  - Is the "strong relationship" a straw man? The slope 2 ln 9 was chosen as a
    round, legible effect, not derived from anything. Name the effect size that
    is actually at stake for the convergence gate, and say whether the band could
    detect THAT one.
  - THE STRONGEST OBJECTION, and I want it pressed: the gate only ever acts AT
    the cut, so in-band agreement may be the only agreement that matters
    operationally. If that is right, the original sentence was adequate for every
    decision it was used in and this correction is pedantry. Decide which, and
    say what measurement would settle it.
  - Does the power argument survive a non-monotone relationship? Everything above
    assumes P(CRITICAL) is monotone in severity. If the rubric's 5 clauses are
    orthogonal to magnitude, no sample size helps and the costed ask is wasted.
  - Archive severities mass at 0.5 (633 of 3,237), 0.8 (192) and 0.7 (174). Does
    simulating a continuous predictor on that lumpy a distribution overstate what
    a full-range sample would really achieve?
  - Is correcting a directive on the strength of a POWER argument legitimate at
    all, given no new labels were gathered? State the standard a withdrawal
    should meet, and whether this meets it.

HOW THIS BEARS ON CHANGE 5, WHICH IS THE INTERACTION TO CHECK. Change 5 promotes
the section-7.7 severity specification to DECIDING while leaving the cut at 0.7.
`scripts/the_severity_cut_collapses_the_formula_2026-10-13.py` already derived
that at a 0.7 cut the specification is the identity

    Sev(f) >= 0.7   IS   HARD  AND  CONFIRMED  AND  confidence >= 0.7

with z3 returning unsat on the negation. So the run is about to let a threshold
decide whose agreement with the project's own consequence definition has never
been measured where severity varies. That is not a reason to hold the run: the
specification's key property, a disproved finding scoring 0, is worth having on
its own and is violated on 35 of 40 disproved findings today, 87.5000% Wilson
[73.8879%, 94.5405%]. It is a reason the 2 items must be read together.

AND IT MAKES THE EXISTING AUDIT LESS REPRESENTATIVE, NOT MORE. Change 5's own
figures move 835 of 3,298 entries from above the cut to below it, 25.3184% Wilson
[23.8636%, 26.8306%]. The population sitting near 0.7 after the promotion is
therefore not the population the 2026-09-02 audit sampled, so the 259 band
verdicts speak even less to the convergence gate as it will behave once the
specification decides than they do to the gate as it behaves today. Say
whether that strengthens the case for the 63 full-range adjudications or whether
it argues for re-auditing the band after the promotion instead.
## CHANGE 9 — what a round pays to make every seat land, instrumented and measured

A COMPLETION BARRIER, as the term is used here, is the point at which a round
cannot proceed until every seat has landed. The staggered start is its opposite
number: one controls when seats begin, the other what the round pays for them
to all finish.

ADDED AFTER THIS BRIEF'S FIRST VALIDATION. HIS RULING, 2026-10-28, verbatim:
*"Verdict. Do it and study it in the upcoming simulated run."*

HIS QUESTION, `qs:157b6ddc201f`, asked 3 times before it was registered: does a
collaborative star round need a COMPLETION barrier, not just a staggered start?
The stagger's own derivation reduces to `s <= d1` under SymPy with z3 returning
unsat on the negation -- a condition entirely about STARTS. Nothing in the record
measured what a round spends waiting for its last seat to land.

WHAT WAS BUILT. `dispatch` now stamps `t_start_epoch` and `t_end_epoch` on every
seat record, on the failure path as well as the success path, because a seat that
times out is precisely the one that sets the barrier. `completion_barrier` in
`bench/star_topology_2026-10-06.py` derives the figures from those stamps, and
the round writes `completion_barrier.json` and prints a per-seat line. No
signature changed and `run_seat_group` is untouched: once the stamps exist the
barrier is derivable from the records the round already returns.

AND IT DID NOT HAVE TO WAIT FOR THE RUN. A seat's reply file is written at the
END of `dispatch`, so its mtime approximates that seat's completion and
`elapsed_s` recovers the start. 88 archived panel rounds answer his question
today:

  - a round wastes a median 0.144892 of its available seat-time at the barrier,
    bootstrap 95% CI [0.105753, 0.181047] over 20,000 resamples;
  - the median round loses 255.9 s; the archive loses 14.11 hours in all;
  - 13 of 88 rounds wasted more than 0.30, a share of 0.147727; the worst is
    0.729400.

So the answer to his question is YES, the cost is real and the stagger cannot
touch it.

WHETHER IT WORSENS WITH SEAT COUNT IS SUGGESTIVE AND NOT ESTABLISHED, and we
want that pressed. On rounds where every seat succeeded: 0.384744 at 4 or more
seats (n = 6, CI [0.186245, 0.535009]) against 0.131478 at 2 seats (n = 74,
CI [0.093287, 0.170485]). The intervals are disjoint; Mann-Whitney gives
p = 0.005483 and a permutation test on the median difference p = 0.000100; but
Brunner-Munzel, which does not assume equal spread, gives p = 0.104133. The
spreads differ markedly and the larger group is 6 rounds.

2 CORRECTIONS THIS MEASUREMENT MADE AGAINST ITS OWN FIRST READING, reported
because both came out of this instrument before being caught by it:

  1. THE FIRST PASS FOUND THE OPPOSITE. 4-or-more-seat rounds appeared to waste
     almost nothing, median 0.000014 against 0.128978, at p = 2.814701e-04. It
     was an artefact of treating any JSON carrying `model` and `elapsed_s` as a
     panel seat: experiment directories hold per-round finding files, one
     "round" was credited with 144 seats, and 34 of 60 supposed 4-seat rounds had
     ZERO seats succeed. A seat is now identified by the `route` field, which only
     `dispatch` writes, plus rejection of `r<digit>_` prefixed files. The seat
     counts then read 78 rounds of 2, 4 of 5 and 6 of 7.
  2. THE MTIME RECONSTRUCTION IS NOT VALID EVERYWHERE and the first pass did not
     bound it, giving a mean idle of 80,028.9 s and a start spread of 129,292.6 s,
     both impossible. The bound now applied is a necessary condition, not a tuned
     tolerance: a round's wall clock cannot exceed the sum of its seat durations
     plus at most 20 s of stagger per seat. 4 of 92 rounds are excluded, 0.043478,
     and they are counted rather than dropped in silence.

AN INDEPENDENT CORROBORATION FELL OUT AND WAS NOT SOUGHT. The median saving
against strict serialisation reads 0.436250 by this method against the 0.396900
committed by `scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py`,
which derived it from seat durations alone. 2 instruments, different inputs,
differing by 0.039350.

RUN THESE, do not reason about them:
  python3 scripts/what_a_round_waits_on_its_slowest_seat_2026-10-28.py
  python3 -m pytest bench/tests/test_the_completion_barrier_is_measured_2026-10-28.py -q

QUESTIONS FOR YOU:
  - Is the mtime reconstruction sound at all? It assumes a reply file is never
    rewritten after its round. `_preserve_prior_attempt` renames prior attempts
    rather than overwriting, which is the behaviour the assumption needs, but say
    whether any other path touches those files, and whether the
    wall-cannot-exceed-serial bound excludes the rounds it should or merely the
    rounds that were easy to spot.
  - A barrier is not obviously a FAULT. In a collaborative round every seat is
    supposed to see every other seat's reply, so waiting for the slowest seat is star-topology collaboration working as
designed rather than failing.
    State the condition under which barrier idle time is a cost worth paying and
    the condition under which it is waste, and say which the 0.144892 is.
  - If it IS waste, what is the fix that does not break collaboration? Partial
    barriers, a deadline that truncates the slowest seat, and starting the next
    round from whoever has landed all change what the round means. Name the one
    you would defend and what it would cost.
  - The 4-or-more-seat group is 6 rounds and 3 tests disagree. Say whether the
    direction should be acted on now or held until the instrumented runs supply
    more, and name the n at which you would act.
  - Does recording absolute epoch timestamps on every seat record leak anything
    or change any existing figure? `elapsed_s` is retained unchanged, but say if
    any consumer computes durations differently now that both ends exist.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 78 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel fix_review_panel_2026-10-28) -->

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

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 72 recorded tool call(s).

<!-- verbatim-begin: fable (panel fix_review_panel_2026-10-28) -->

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

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/fix_review_panel_2026-10-28/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
