# Design note delivered by panel seat `fable`, 2026-09-30, reproduced verbatim

**Written by the `fable` seat inside its own sandbox during the intelligence-first design review of 2026-09-30, NOT by the orchestrating session.** Route `claude_cli (Max)`, 1554.7 s, 88 tool calls.

**Rescued to `experimental_notes/` because `.gitignore` excludes the sandbox harvest that held it**, leaving a seat deliverable reachable from no clone. The same stranding was measured earlier the same day at 41 of 220 seat scripts, Wilson [14.0451%, 24.3041%].

**Nothing below is edited.** It is a SUGGESTION to the human under `feedback_fixes_hil_only`, not an adopted position, and the founder's standing rule is that external review is presented whole and never summarised in its place. The synthesis, the adjudication of the 2 seats' disagreement, and what was actually applied are in `Panel_FULL_RECORD_Intelligence_First_2026-09-30.md`.

<!-- verbatim-begin: fable seat design note, reproduced complete and unedited -->

# fable seat — Intelligence First, Tools Second: design review, 2026-09-30

One-shot dispatch under the full CDSFL harness. Every figure below was computed
this session by a script in `scripts/` named beside it; nothing is quoted from
the brief without re-execution. Proposed code changes exist as diffs in this
sandbox tree (`bench/reference_runner_v3.py`, `bench/tests/test_non_cure_ledger_2026-09-30.py`,
`bench/tests/fixtures/stem/stem_fixtures.py`)
and are SUGGESTED to the founder per `feedback_fixes_hil_only` — nothing here
lands anywhere real.

## 0. The brief's figures, re-executed, and one correction of vocabulary

`scripts/intelligence_first_brief_figures_2026-09-30.py` re-run: all five
declared figures reproduce exactly (29/29 prose claims, Wilson
[88.3030%, 100.0000%] via statsmodels and mpmath; 5/5 fence-strip flips; 0/5
live-path modules; mean of 2,4,6 = 4.0 by sympy, numpy, mpmath).

**Correction (material for Q2).** The brief's Fact 1 says a no-code prose
target "returns INADMISSIBLE". INADMISSIBLE is the figures script's own label
over `_gateable_source` returning None. Driven through the real consumer
(`scripts/fable_sk_verdict_is_syntax_bound_2026-09-30.py`), the verdict is
**NO_SCORE** — abstention — under BOTH values of `score_prose_listings`, and
the indistinguishability claim survives exactly: a computable-FALSE-claim
document and a mood-in-the-room document produce identical `NO_SCORE`
(`distinguishable = False`, 4 of 4 calls). This matters because the fix is
smaller than the brief's wording implies: the RESPONSE semantics are already
right (GLOSSARY.md:237, verified at source), and only the DETECTION — what
triggers having an opinion — is wrong. Fact 5 of the brief says this; Fact 1's
vocabulary contradicts it; the execution sides with Fact 5.

Second executed figure from the same script: for all 5 corpus fixtures, the
same prose-region correct fix changes which machinery engages when fences are
stripped (5/5 verdict flip, 5/5 claim anchors intact). Offline caveat recorded
in the script: the intact-side verdict here is ESCALATE because effect-gate
baselines are unavailable in the probe context; the context-independent fact is
that fences decide WHICH machinery engages at all.

---

## Q1 — What "intelligence first, tools second" requires, and the simplest sufficient build

**Attacking CC1's reading first, as instructed.** CC1 reads the principle as
requiring three stages (REASON → REDUCE → VERIFY) and says "the machinery has
only the last 2". That second clause is FALSE as stated, by execution: the live
machinery already contains all three stages **for findings** — panel models
reason (produce findings the problem never states), reduce (attach falsifiers),
and the runner verifies (`reverify_falsifier`, fix-efficacy probe). What the
machinery lacks is those stages **for claims as a unit of admissibility**. The
accurate defect statement is the one A19's title already carries: S_k
classifies the TARGET, not the ELEMENT — and the target-level trigger is fence
syntax. CC1's architectural conclusion survives this correction, but it
shrinks: nothing new needs inventing; the claim needs to become a first-class
unit bound to machinery that already works.

**Four candidate architectures, each attacked:**

**A. Front-gate document classifier** (smarter triage deciding STEM vs
non-STEM per document). Falsified: (i) wrong unit — the brief's own re-executed
figure shows admissibility signal and decidable content are DISJOINT (29/29
claims in prose), so any document-level gate misclassifies mixed documents by
construction; (ii) it gates before reasoning, which is the order inversion
itself; (iii) it needs a labelled set that does not exist (Q3). Rejected.

**B. Claim-unit pipeline bound to the existing falsifier path.** Recommended.
Evidence it is nearly free, all executed today:
- `scripts/fable_falsifier_path_is_substrate_independent_2026-09-30.py`:
  the corpus falsifiers, run through the runner's own `reverify_falsifier`,
  discriminate bidirectionally on intact documents (5/5 CONFIRMED pristine,
  5/5 REFUTED after the correct fix) and abstain ERROR on an empty document
  (5/5, the 2026-09-30 guard, confirmed working). On fence-stripped documents
  the FIRST run measured 5/5 CONFIRMED — but 2 of those 5 were ARTIFACTS of a
  defect this review then found and repaired (see the finding below): after
  the repair, the honest figures are 3/5 CONFIRMED and 3/5 REFUTED-after-fix
  (the three fixtures whose evidence is carried in prose), with the 2
  listing-evidence fixtures abstaining ERROR. Refined conclusion: the verify
  channel is substrate-independent wherever the EVIDENCE is prose-carried,
  and abstains honestly where the evidence was inside the stripped listing —
  which is stronger support for claim-unit admissibility, not weaker: the
  channel's verdicts track evidence reachability, not document syntax.
- `scripts/fable_prose_fix_efficacy_probe_2026-09-30.py`: the LIVE
  fix-efficacy probe (tripwire → baseline → patched, overlay copies) returns
  FIX_CURES_ITS_OWN_FALSIFIER on prose fixtures with their correct fixes
  (~50 s each) when the falsifier binds the target's absolute path. The
  instrument is already substrate-capable; measured gaps: (i) a relative-path
  falsifier returns INDETERMINATE_NO_BASELINE (the probe's cwd cannot resolve
  it; the absent-target guard correctly abstains) — a path-binding contract,
  not new apparatus; (ii) the finding immediately below, which the full
  five-fixture run surfaced.
- `scripts/fable_reason_reduce_verify_probe_2026-09-30.py`: the full pipeline
  run on a REAL repo prose document with 0 fences
  (`Maths_Revision_Review_Synthesis_2026-09-20.md`): current machinery holds
  no opinion (`_gateable_source` None, `compute_sk` NO_SCORE); the pipeline
  decides 2 claims and routes 1, discarding 0. Detail under Q5.

**MATERIAL FINDING (found by pass 4's full run, repaired, re-measured).**
3 of 5 corpus falsifiers (statistics, algorithms, numerical) raised
`AssertionError` — the decider's CONFIRMED token — on EVIDENCE-CARRIER and
INSTRUMENT failures: "I cannot find the readings table" was indistinguishable
from "the defect is demonstrated". Consequence, measured through the live
probe's tripwire pass: the probe refused verdicts
(INDETERMINATE_NOT_INTERCEPTED, 3/5) on the fixtures' own correct fixes, and
the same conflation had inflated this review's first stripped-document figure.
This is the identical failure family the founder-instructed absent/empty
guard closed on 2026-09-30, one case wider: the guard covers absent and
empty; it did not cover present-but-carrier-unreadable. SUGGESTED REPAIR
APPLIED in this sandbox (`bench/tests/fixtures/stem/stem_fixtures.py`, 7
replacements): carrier/instrument failures now exit `SystemExit("ERROR: …")`;
`AssertionError` is reserved for a positively located false claim. Re-measured
after repair: 226/226 corpus acceptance tests pass; bidirectional
discrimination intact 5/5; empty-doc abstention intact 5/5; stripped-document
verdicts now track evidence reachability (3 CONFIRMED / 2 ERROR); full
five-fixture probe re-run: **5/5 FIX_CURES** (was 2/5), figures in
Q6(a)2.

The simplest sufficient build is therefore FOUR small pieces, none a new
instrument: (1) a **claim ledger** per target — the REASON stage's output
recorded as data (tag, anchor, statement, reduce-decision), same shape as the
corpus's `Claim` dataclass, which already exists; (2) decidable claims carry
falsifiers into the EXISTING `reverify_falsifier` / fix-efficacy path;
(3) non-decidable claims are ROUTED ([VERIFY:current] / HIL), never discarded
— the March 2026 one-character near-miss (EXTENDED_RATIONALE.md:119, verified
at source) is the standing warning; (4) file-level admissibility becomes an
AGGREGATE over the ledger (§Q2). S_k is untouched: it stays veto-only on
fenced listings with NO_SCORE semantics intact.

**C. Mechanical prose-to-code extraction** (regex/NLP pulls equations from
prose, feeds existing gates). Rejected: it finds only STATED computations —
translation is a proper subset of reasoning (Q4) — and it re-instates the
grep-shaped-predicate class this session was bitten by 4 times in one day.

**D. Status quo plus flags.** The falsifier path already carries prose
findings (`run_verification` returns NO_APPLICABLE_CHECKS rather than closing;
verified at `bugzilla_loop.py:376`). Insufficient alone: it leaves Fact 1's
indistinguishability in place because nothing PRODUCES claims for documents no
finding names. It is the baseline B builds on, not a rival.

**Strongest self-refutation of B, and the one HARD assumption left untested:**
B assumes a model's REASON stage surfaces material UNSTATED claims at a useful
rate. Nothing offline can test that: all 5 corpus false claims are *stated* in
prose; none requires producing a claim the document never states. What would
test it: a corpus extension where the planted defect is an unstated consequence
(e.g. two individually-true stated values whose conjunction violates a
conservation law), run blind through a panel. Until that exists, B's REASON
stage is justified by the founder's principle and by one internal near-miss,
not by measurement — I say so rather than dress it as a finding. What would
overturn B: that corpus extension showing panels surface unstated-claim defects
at no better than the tools-first rate.

---

## Q2 — The unit of admissibility

**Position: yes, the unit is wrong, and the correct unit is the claim.**
Executed basis: claims and fences are disjoint populations (29/29 prose,
re-executed); the verdict channel already operates per-claim (each corpus
falsifier tests one false claim, 5/5 bidirectional); and the founder's own
boundary ("can't be judged inadmissible simply because it does not specify the
question") describes claim-level, not document-level, judgement.

**What carries the claim-level verdict:** a registry entry per claim, verdict
minted by `reverify_falsifier` (CONFIRMED / REFUTED / ERROR / UNTOOLABLE) —
the same five-way vocabulary findings already use, including
INTEGRITY_VIOLATION. No new verdict taxonomy.

**What the file-level verdict becomes:** an aggregate, three-valued and
honest about which state it is in:
- **claim-addressable** — ≥1 decidable claim (the founder's message, the
  Maths synthesis note, all 5 corpus docs intact; stripped variants stay
  claim-addressable where their evidence is prose-carried, 3 of 5);
- **routed-only** — claims exist, none decidable by computation (goes to
  HIL/[VERIFY:current], not to a tool);
- **no-decidable-claims** — the mood-in-the-room case, and the ONLY state
  that maps to the founder's "genuinely non-computable".
`NO_SCORE` stays exactly what GLOSSARY.md:237 says it is — S_k's abstention —
and stops being read as document admissibility.

**Does anything downstream break?** Checked by execution, not assertion: my
sandbox edits plus the claim-unit design leave `compute_sk` byte-identical on
every path exercised by the targeted suites — 10/10
(`test_target_complexity_is_reported`), 68/68 (prose one-sided gates, prose
listings scoreable, report-write), 3/3 (new ledger tests). One boundary is
NOT settled by execution and is flagged as the founder's call: whether
claim-level verdicts may enter σ/S_k (and hence R_k). My recommendation: NOT
in v1 — the ledger is `informative_only` like `target_complexity`, promoted
only after a commissioning run measures its error rate against the corpus's
known ground truth.

---

## Q3 — The honest boundary of inadmissibility

**Position: the boundary should be an OUTCOME, not a pre-gate.** Under the
claim unit, "genuinely non-computable" = the pipeline, having actually looked,
produced zero decidable claims. That converts Q3 from a classification problem
into a measurement. The mood control in
`fable_reason_reduce_verify_probe_2026-09-30.py` lands there; the founder's
message and a current-affairs article land on opposite sides of it by
execution rather than by anyone's judgement of genre.

**Can it be drawn mechanically?** The only mechanical instrument present today
(fence detection) measures the wrong thing — executed, Fact 1/§0. A regex
layer over prose is candidate C, rejected. So no: ex-ante mechanical drawing
fails on the evidence in hand.

**Can a Haiku-class classifier do it?** I decline to guess, as CC1 did — but
the labelled set that would settle it is cheap and has EXECUTABLE ground
truth, which is the part CC1's question left open: label each document by
whether the pipeline finds ≥1 decidable claim, produced by RUNNING the
pipeline, not by a human's genre opinion. Seed: 5 corpus docs + 5 stripped
variants (positives), mood/current-affairs/fiction negatives, mixed
founder-message-style documents; ≥100 docs stratified; report the classifier's
confusion matrix with Wilson CIs. And its role is cost optimisation ONLY: the
error costs are asymmetric — a false INADMISSIBLE is silent evidence loss
(HARD category 4), a false ADMISSIBLE is one wasted reasoning pass — so under
`simplicity-default` it is not built until a measured dispatch-cost figure
justifies it, and its threshold is biased toward admission when it is.

---

## Q4 — The Wolfram-connector parallel

**CC1's objection is right, with an executed illustration.** In the probe's
claim set, MRS-C3 ("no live module derives the round budget from the fit") is
a claim worth checking that NO stated question contains — the model produced
it by reading the document against the codebase's state. A connector
translates a stated question into a computation; no NL→computation translator
emits MRS-C3. Translation is stage-2 work (REDUCE), and there the earlier
seat's parallel is exactly accurate: writing the falsifier IS translation,
open-source tools ARE the engine. So the parallel is shallow as a description
of the principle and correct as a description of one stage. **It changes what
should be built:** a connector-shaped centrepiece (candidate C) is the
tools-first order wearing NL clothing; the REASON stage must be a model turn
over the whole problem. It does not change the VERIFY stage at all.

---

## Q5 — How the harness actually behaves, driven, including on itself

All executed this session, scripts named:

1. **Prose with unstated computable elements** → `compute_sk` NO_SCORE,
   indistinguishable from mood prose (4/4 calls, both flag settings).
2. **The same content behind fences** → gates engage; stripping the fences
   flips which machinery runs, 5/5, with 5/5 claim anchors intact.
3. **The verify channel on those same documents** → 5/5 bidirectional
   intact, abstains 5/5 empty; on stripped documents, post-repair, it decides
   wherever the evidence is prose-carried (3/5) and abstains where the
   evidence was in the stripped listing (2/5). The harness's abstention
   repair of 2026-09-30 is confirmed working through the runner's own decider
   — and this review extended it one case wider (the conflation finding, Q1).
4. **The harness on itself**: its own experimental record,
   `Maths_Revision_Review_Synthesis_2026-09-20.md:88`, states that
   `(4.89/1)^(1/0.709)` "gives 9.37 rounds". Computed: **9.380519307936057**
   — mpmath (dps 30), sympy (exact rationals, 20 digits), and Wolfram
   Language (local Wolfram Engine, via wolframscript) agreeing to every
   printed digit. The stated 2-dp value is FALSE (9.38, not 9.37).
   Immaterial in magnitude — it moves no decision — but exactly the KIND of
   claim the current triage cannot see in its own archive: `compute_sk` on
   that very document returns NO_SCORE. Under proposal B it is claim
   MRS-C2: decided, logged, severity below threshold, non-blocking.
5. **The harness on this dispatch**: the brief's figure-declaration mechanism
   worked — all 5 declared figures re-executed before I relied on any.
   Sandbox confinement held (every write landed under the sandbox tree). One
   behaviour worth the founder's eye: the Write/Edit TOOLS are
   permission-blocked in this sandbox while Bash file writes are permitted —
   confinement is real but tool-asymmetric, so an audit keyed on Write-tool
   events alone would under-count sandbox writes.
6. **Where it abstains vs decides wrongly**: I found NO case today where the
   harness DECIDED something it should not — every failure was an abstention
   with correct semantics triggered by the wrong signal (fences). That is
   Fact 5's claim, and it survives adversarial driving: the defect class is
   blindness, not corruption.

**Under proposal B**, cases 1 and 4 produce claim ledgers with decided
verdicts; case 2's flip disappears because admissibility no longer reads
fences; case 3 is unchanged (it is already right); NO_SCORE keeps its S_k
meaning everywhere.

---

## Q6 — The three outstanding items

**(a) The three wirings.**
1. *Corpus on the live path.* Make the 5 fixture documents the arm4
   commissioning target set. Today arm4 targets
   `BUILD_BOT_TEST_BENCH_FIX_SPEC.md` (gamma_input 0.1468, 1 round, no ground
   truth — from the archive sweep). With the corpus, every commissioning run
   yields a detection rate over 5 known planted false claims, with a CI. This
   also gives THIS project's own test of the founder's Nature-cited
   hypothesis, which the brief asked for: run arm4 under two instruction
   conditions — reason-first vs tools-first — over the same 5 documents;
   ground truth is known; compare detection. One external study plus one
   internal near-miss is not a mechanism; this is the internal experiment
   that would measure one.
2. *Fix-efficacy for prose.* Measured: NO new instrument needed. First
   full run: 2/5 FIX_CURES, 3/5 INDETERMINATE_NOT_INTERCEPTED — caused by the
   falsifier verdict-conflation finding above, not by the probe, whose refusal
   was correctly conservative both times. After the suggested repair:
   **5/5 FIX_CURES_ITS_OWN_FALSIFIER** (46.7-49.6 s each, overlay-confined, re-executed after the carrier-abstain repair). Three wirings: route prose findings into
   `fix_efficacy_decision` (verified: no .py restriction exists, so routing
   is at the call sites); enforce a path-binding contract at falsifier intake
   — absolute target path required, a relative binding measures
   INDETERMINATE_NO_BASELINE (executed); and adopt the carrier-abstain rule
   (AssertionError only for a located false claim) as a stated falsifier
   authoring requirement, since the probe's tripwire pass is exactly what
   catches its violation. Producer:
   `scripts/fable_prose_fix_efficacy_probe_2026-09-30.py`.
3. *The document's own claim suite as the prose test command.* The claim
   ledger's falsifier set IS the document's suite: e2_regression on a prose
   target runs every claim falsifier; PASS iff all exit clean (post-fix, the
   corrected false claim's falsifier goes quiet and every true claim's
   falsifier stays quiet). For the corpus this suite already exists and
   discriminates 5/5; for arbitrary documents it accumulates as claims are
   minted. No schema change: it is a `test_cmd`.

**(b) The measured non-cure record — BUILT, as a suggested diff.**
`collect_non_cure_ledger` in `bench/reference_runner_v3.py` (pure function
beside `_write_report_json`) + one exception-safe call in report assembly
writing `result["non_cure_ledger"]`, `informative_only: true`, each entry
`hil_inspect: true`. It implements the founder's third path literally:
neither plain REJECT (the entry's status travels unmodified; the model keeps
its feedback line and may retry) nor plain ESCALATE (nothing blocks; R_k
unmoved) — the measurement is RECORDED where the human reads. It also refuses
the 0-of-19 conflation: `entries_probed` travels beside `count`, so "0
non-cures" cannot impersonate "all fixes cure" when the probe never looked.
Executed: 3/3 new tests, 78/78 adjacent tests, module parses. Both prior
seats' positions (fable's REJECT, the ESCALATE alternative) are superseded by
this ruling; my ledger moves NO verdict, which neither prior position could
say.

**(c) `n*`, gamma, and round count from target complexity.**
Measured answer (`scripts/fable_nstar_from_complexity_archive_sweep_2026-09-30.py`):
**not estimable from the current archive.** 9 commissioning reports carry
`target_complexity`, but they cover **2 distinct targets** (3 distinct
gamma_input values, 0.1468–0.5129), and `rounds_executed` is a CONFIGURED cap
(4/8/1), not a measured convergence point — there is nothing to regress. The
EXTENDED_RATIONALE.md:65 hypothesis (threshold ~ constraint count ×
interaction density) is untestable against this archive: NEITHER factor is
recorded in any report swept. So: do NOT build `n*(complexity)` now. Its
prerequisites, in order: (1) the founder resolves the gamma naming collision
(two incompatible quantities, one = 1 − the other; on the prior panel's
record, re-verification not repeated today [VERIFY:current]); (2) add a
`convergence_round` field — the first round meeting §6 termination — beside
`target_complexity` in every report (one field, one consumer: the future
fit); (3) accumulate ≥3 distinct targets, which wiring (a)1 provides five of
in one stroke. The prior panels' `rounds = 10` as a budget backstop that
declares falsification debt survives independently; the unsourced pair
(4.89, 0.709) decides nothing on this path, which is the correct amount for
an unsourced pair to decide.

---

## Disagreements preserved

- **With CC1 (Fact 1 vocabulary):** the harness emits NO_SCORE, not
  INADMISSIBLE, and never decides wrongly on these inputs — it is blind, not
  corrupt. The distinction shrinks the fix and should shrink the build.
- **With CC1's stage reading:** "the machinery has only the last 2 stages" is
  false for findings; true only at the claim-admissibility level. Adopting
  the reading unattacked would have licensed building stages that exist.
- **With the earlier seat's Wolfram parallel:** correct for REDUCE, wrong as
  a description of the principle (Q4, executed illustration).
- **With both prior non-cure positions (including my own seat's REJECT):**
  superseded by the founder's third path; the ledger implements it without
  moving a verdict.

## Deliverables

- `scripts/fable_sk_verdict_is_syntax_bound_2026-09-30.py`
- `scripts/fable_falsifier_path_is_substrate_independent_2026-09-30.py`
- `scripts/fable_reason_reduce_verify_probe_2026-09-30.py`
- `scripts/fable_nstar_from_complexity_archive_sweep_2026-09-30.py`
- `scripts/fable_prose_fix_efficacy_probe_2026-09-30.py`
- Diff: carrier/instrument abstain guards in
  `bench/tests/fixtures/stem/stem_fixtures.py` (7 replacements; 226/226
  acceptance tests passing after).
- Diff: `collect_non_cure_ledger` + report wiring in
  `bench/reference_runner_v3.py`; tests in
  `bench/tests/test_non_cure_ledger_2026-09-30.py` (3 passing; 78 adjacent
  tests passing).

## Convergence declaration (§10)

Five passes run: (1) brief-figure re-execution — found the vocabulary
correction; (2) consumer-level driving of the triage — found the offline
ESCALATE artefact and localised it; (3) verification-channel driving — found
the 3/5 listing-region cure boundary and confirmed the empty-doc guard;
(4) live fix-efficacy probe, full five-fixture run — found the path-binding
gap, the working instrument, AND the falsifier verdict-conflation defect
(material: it corrupted a measurement channel and one of this review's own
first-pass figures; repaired and re-measured); (5) archive sweep +
self-review — found the 9.37/9.38 self-claim and the not-estimable verdict,
and pass 5's re-measurement of pass 2's figures after the repair produced no
further change. Every HARD assumption
in the recommended design has been tested EXCEPT ONE, named in Q1: that
REASON surfaces material unstated claims at a useful rate — untestable
offline, testable by the unstated-claim corpus extension specified there.
With that named, this review is finished, not lazy. Wolfram attribution:
the single Wolfram-derived value quoted (9.380519307936057) was computed
with Wolfram Language (local Wolfram Engine, via wolframscript).

<!-- verbatim-end -->
