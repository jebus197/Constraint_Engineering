# Design note delivered by panel seat `cc2`, 2026-09-30, reproduced verbatim

**Written by the `cc2` seat inside its own sandbox during the intelligence-first design review of 2026-09-30, NOT by the orchestrating session.** Route `claude_cli (Max)`, 953.3 s, 136 tool calls.

**Rescued to `experimental_notes/` because `.gitignore` excludes the sandbox harvest that held it**, leaving a seat deliverable reachable from no clone. The same stranding was measured earlier the same day at 41 of 220 seat scripts, Wilson [14.0451%, 24.3041%].

**Nothing below is edited.** It is a SUGGESTION to the human under `feedback_fixes_hil_only`, not an adopted position, and the founder's standing rule is that external review is presented whole and never summarised in its place. The synthesis, the adjudication of the 2 seats' disagreement, and what was actually applied are in `Panel_FULL_RECORD_Intelligence_First_2026-09-30.md`.

<!-- verbatim-begin: cc2 seat design note, reproduced complete and unedited -->

# Intelligence first, tools second — what it requires, and what the harness actually does

**Seat:** claude (free panel, design review before build)
**Dispatched:** 2026-09-30
**Scope:** design only. Two code changes were made and are named in §7; everything
else is a SUGGESTION for HIL per `feedback_fixes_hil_only`.

Every figure below travels with the script that produced it. All scripts run from
the repository root and write nothing outside a temporary directory.

| script | what it decides |
|---|---|
| `scripts/inadmissible_is_not_a_harness_verdict_2026-09-30.py` | the brief's Fact 1, split into 3 propositions |
| `scripts/two_fence_extractors_disagree_2026-09-30.py` | two live extractors, pre-fix |
| `scripts/fence_extractor_dominance_2026-09-30.py` | the removal clause, 360 shapes |
| `scripts/one_extractor_invariant_2026-09-30.py` | the post-fix regression guard |
| `scripts/harness_on_this_brief_2026-09-30.py` | Q5, the harness on real briefs |
| `scripts/target_complexity_is_a_constant_2026-09-30.py` | Q6(c), does γ_input vary |
| `scripts/sd_convention_makes_the_claim_undecided_2026-09-30.py` | Q4, translation ⊊ reasoning |

The 5 declared brief figures were re-executed and all 5 reproduce exactly
(`python3 scripts/intelligence_first_brief_figures_2026-09-30.py`): 29 of 29
claims in prose, Wilson [88.3030%, 100.0000%]; 5 of 5 documents flip; 0 of 5 live
modules reach the corpus; claimed_mean_is_false = 4.0.

---

## 0. The headline, before the questions

**I disagree with the brief's central framing, and the disagreement is
executed, not argued.** The brief's Fact 1 bundles three propositions with
different truth values. Separated and decided by calling the live code:

```
P1  `_gateable_source` returns None for both documents          TRUE
P2  that shared outcome is a harness verdict "INADMISSIBLE"     FALSE
P3  repairing the detector would let such a document be ADMISSIBLE  FALSE
```

Producer: `scripts/inadmissible_is_not_a_harness_verdict_2026-09-30.py`, exit 1
(FALSIFIED). Output:

```
P2  'INADMISSIBLE' is not a value the harness can emit
    live S_k tristate vocabulary = ['ADMISSIBLE', 'ESCALATE', 'NO_SCORE', 'REJECTED']
    'INADMISSIBLE' in vocabulary = False; as a module attribute = False
    computable-false  kind=prose  tristate=NO_SCORE
    mood-in-the-room  kind=prose  tristate=NO_SCORE
```

There is no verdict named INADMISSIBLE. The word is the producer script's own:
`intelligence_first_brief_figures_2026-09-30.py` prints
`'ADMISSIBLE' if red else 'INADMISSIBLE'`, a truthiness test on an extractor's
return value. The live verdict on both documents is `NO_SCORE`, which by
`docs/GLOSSARY.md:237` is "the statement that S_k has no opinion" — and on a
prose target with no fix offered, that is the **correct** answer.

`_gateable_source` is not a triage sitting before reasoning. It is an extractor
**inside `compute_sk`**, and `compute_sk` scores a **proposed fix**
(`fix_text`, `source`, `source_path`, …). It has never been asked whether a
document is worth reviewing, and it does not answer that question.

P3 is the load-bearing one. Sweeping document × A19 flag × fix:

```
doc=no fence  score_prose=False/True  -> NO_SCORE
doc=fenced    score_prose=True        -> ESCALATE
tristates observed = ['ESCALATE', 'NO_SCORE']       ADMISSIBLE never reached
```

Corroborated independently by the project's own producer
`scripts/a19_prose_gates_are_one_sided_2026-09-22.py`: over 5 real fixtures ×
{harmful, correct} × {flag off, on} = **20 evaluations, 0 ADMISSIBLE**, 3 of 5
harms actively REJECTED, every NO_SCORE holding R_k at 0.5000.

**So detector repair alone buys zero additional reachable states.** A design
that aims at the detector is aimed at a stage that does not gate the outcome.

**Where I was wrong.** My own P3 prose said the reachable set is bounded to
`{REJECTED, NO_SCORE}`, following the brief's Fact 4. The sweep returned
`ESCALATE`, from `reference_runner_v3.py:11427` ("no SEARCH/REPLACE blocks
found"). The brief's Fact 4 is correct *given a parseable fix*; both it and my
restatement are incomplete as written. Corrected here rather than quietly.

---

## 1. Q1 — What "intelligence first, tools second" requires

### 1.1 Attacking CC1's reading first, as instructed

CC1's reading: the principle implies REASON → REDUCE → VERIFY; the machinery has
only the last two; the triage sits *before* stage 1 and gates on syntax.

**The last clause is false.** Nothing in the harness gates a panel model's
reasoning. The evidence is this document: the target is a prose brief with
**0 fenced listings** (`harness_on_this_brief_2026-09-30.py`), and the seat
reasoned freely and produced 5 falsifiers, 3 of which found defects the brief
does not name. No gate was consulted before any of it. The "triage before stage
1" does not exist.

**The first clause survives, but relocated.** The REASON stage is not missing
and not gated — it is **unrecorded**. The harness has no unit smaller than a
file. 29 of 29 corpus claims live in prose and the harness has no object that
holds one. That is the real defect, and it is one level above A19's title:
A19 says "S_k classifies the TARGET, not the ELEMENT". Sharper: **S_k classifies
neither — it classifies a FIX.** Asking it about claim admissibility is a
category error, and the answer it gives (`NO_SCORE`) is correct precisely
because it declines to answer a question it was not asked.

### 1.2 Four candidate architectures, each falsified

**A1 — Claim ledger replaces document admissibility.** REASON emits claims;
REDUCE assigns decidability and writes a falsifier; VERIFY runs it; the file
verdict becomes an aggregate over claims.
*Falsified as stated:* it changes what `NO_SCORE` means on the S_k path, and
`NO_SCORE` is already correct (§0). Replacing a correct mechanism violates the
removal clause — there is no committed measurement that an aggregate dominates.

**A2 — Widen the triage to recognise prose-embedded computables.**
*Falsified by P3:* 0 additional reachable states. Also falsified by 1.1: the
thing it would unblock (reasoning) was never blocked.

**A3 — Build nothing structural; the falsifier path already is
REASON→REDUCE→VERIFY. Just do the 3 wirings and record non-cure.**
The `simplicity-default` favourite, and it is closest to right.
*Falsified, narrowly:* the falsifier path has no per-claim record either.
`reverify_falsifier` returns a bare `str` per *falsifier*
(`bench/falsifier_verify.py:1156`), and the finding catalogue's record fields
(`reference_runner_v3.py:3495-3525`) carry no claim identity. A document with 29
prose claims produces no per-claim verdicts, so "which of these 29 did we
decide?" is unanswerable from the archive. A3 leaves the measurement gap open.

**A4 — Claim ledger as a NEW, additive channel; S_k untouched.**
This is A1 restricted to the part A1 got right, with the part that violated the
removal clause dropped. S_k keeps scoring fixes and keeps returning `NO_SCORE`
on prose. A second channel takes a CLAIM as its unit.
*Attempted falsification:* the additive standard's other direction — "an
addition nothing reaches is not additive". This is the project's most-confirmed
defect class (11 of 11 confirmed defects since 2026-08-01 were additions that
did nothing), and a claim ledger is exactly the shape that fails that way. It
survives **only if** the ledger has a caller and a test from the first commit.
That is a HARD constraint on the build, not a nicety, and it is why §7 records
that I verified `_MD_PY_FENCE` has **zero callers** — the failure mode is live
in this very module today.

### 1.3 Recommendation

**Build A4, smallest form, wired on day one.**

```
ClaimRecord:
    id            stable, document-scoped
    span          (start, end) byte offsets into the target — the claim is a
                  SPAN, so "29 of 29 in prose" becomes representable
    text          the claim as stated
    assumptions   list[str]  — see Q4; this field is load-bearing
    decidability  DECIDABLE | UNDECIDABLE | UNDECIDED
    falsifier     source, or None
    verdict       CONFIRMED | REFUTED | UNTOOLABLE | ERROR | None
                  (the existing reverify_falsifier vocabulary, unchanged)
```

Three properties make it sufficient and no larger:

1. **It reuses the existing verdict vocabulary.** No new enum, no new
   adjudication rule, no change to `reverify_falsifier`.
2. **The file-level verdict becomes a summary, not a gate** — "29 claims, 11
   decidable, 8 confirmed, 3 refuted, 18 undecidable" — and nothing consumes it
   as a precondition.
3. **S_k is not touched.** Executed evidence that this is safe: the prose S_k
   range is `{NO_SCORE, ESCALATE, REJECTED}` with `ADMISSIBLE` unreachable, and
   the claim channel writes to none of those.

**What would overturn this.** If a per-claim ledger can be shown to duplicate
information the finding registry already carries — i.e. if findings are already
in 1:1 correspondence with claims on real runs — then A3 dominates and A4 is an
addition nothing needs. I did not measure that correspondence and it is the
strongest attack on my answer. The test: take an archived prose run, count
distinct claims in the target and distinct findings in the catalogue, and
measure the mapping. If it is 1:1, build A3.

---

## 2. Q2 — The unit of admissibility

**Position: yes, admissibility attaches to a CLAIM, not a document — but
"admissibility" is the wrong word for it and importing it will cause the next
defect.**

The document-level property the harness actually needs is not admissible /
inadmissible. It is a **distribution over claims**. The founder's own example
settles it: his message is prose-heavy and carries several decidable claims. A
single label cannot be right for a mixed document, and forcing one is how the
project got here.

- **What carries the claim-level verdict:** `ClaimRecord.verdict`, using the
  existing `reverify_falsifier` vocabulary (`CONFIRMED`, `REFUTED`,
  `UNTOOLABLE`, `ERROR`), plus `decidability` which is a *different axis*.
  A claim can be DECIDABLE and its falsifier ERROR.
- **What the file-level verdict becomes:** a count, reported and consumed by
  nothing. Not a gate. `docs/GLOSSARY.md:237`'s "NO_SCORE is not a third grade
  of admissibility" is exactly the right instinct applied one level down.
- **Does anything downstream break?** Executed check: no. S_k's prose behaviour
  is unchanged by construction (nothing writes to it), and
  `bench/tests/test_prose_acceptance_stem.py` (250 tests) passes against the
  tree as modified in §7.

**Strongest attack on my own answer.** A claim ledger imposes a claim-extraction
step, and claim extraction is itself a model judgement with no tool to check it.
If the extractor drops a claim, the ledger reports "11 of 11 decided" over a
document that had 29 — a confident success over a silent loss, which is the
failure shape the first forensic scan of Exp 48 had. **Mitigation that must be
built with it:** claims carry SPANS, so coverage is mechanically computable as
the fraction of the document's bytes inside some claim span, and that fraction
is reported beside every summary. Without span-coverage the ledger is not safe
to build.

---

## 3. Q3 — Where the honest boundary of inadmissibility lies

**Position: the boundary cannot be drawn from surface syntax, and I have
executed proof. Whether a small classifier can draw it, I do not know, and I
decline to guess — but I can specify exactly what would settle it.**

**Syntax is refuted as the boundary.** Two independent measurements:

- 29 of 29 corpus claims live in prose, 0 inside a code fence, Wilson
  [88.3030%, 100.0000%]. The fences and the claims are disjoint.
- Run on the real brief: `reducible = False`, `fenced listings = 0` — and the
  brief carries many decidable claims, several of which this note decides.
  Even the *widest* extractor in the tree (120 of 360 shapes after §7's
  widening) recognises none of them, because they are English.

**Is judgement therefore required?** For the *decidability* question, yes.
And there is a sharper reason than "prose is hard", which Q4 develops: the
specimen claim the brief itself uses is **not decidable as stated**. Executed
(`sd_convention_makes_the_claim_undecided_2026-09-30.py`):

```
population (ddof=0)  numpy 1.6329931619  mpmath 1.6329931619  sympy 2*sqrt(6)/3
sample     (ddof=1)  numpy 2.0000000000  mpmath 2.0000000000  sympy 2
claimed 2.0  ->  population says FALSE, sample says TRUE
```

Wolfram Language, run separately as the second falsifier:
`N[{Mean[{2,4,6}], StandardDeviation[{2,4,6}]}, 12]` → `{4., 2.}`. Wolfram's
`StandardDeviation` is the sample convention, so the tool most likely to be
consulted for a second opinion calls the claim **true**. (Computed with Wolfram
Language, local Wolfram Engine.)

So the classifier's target must not be "is this claim decidable". It must be
**"is this claim decidable once its assumptions are stated, and what are they"**
— a strictly harder label, and one the corpus does not currently carry.

**Can a Haiku-class classifier do it? No evidence either way, and I will not
guess.** What would establish it, precisely:

- **Positives:** the 29 tagged corpus claims. Already labelled, already located.
- **Negatives: they do not exist.** The corpus has 0 non-STEM documents. The
  founder names the classes he would accept — current affairs, short story,
  poetry, "anything generally of a non-STEM nature" — and a labelled set needs
  them at comparable count. **This is the blocking item**, and it is cheap:
  ~30 short non-STEM documents, claim-tagged by HIL.
- **The measurement:** per-claim agreement between classifier and HIL, reported
  as a proportion with a Wilson interval, stratified by class. With 29 + 30 the
  interval on a 90% agreement rate is roughly ±8 points — enough to reject a
  bad classifier, not enough to certify a good one. Certification needs a few
  hundred claims.
- **The trap to avoid:** measuring agreement on documents drawn only from this
  repository. Every STEM positive here was written by this project, so a
  classifier could learn house style rather than decidability.

**HARD assumption I could not test:** that per-claim decidability is a
well-posed label at all — that two competent humans agree on it. If inter-rater
agreement is low, no classifier can be validated and the whole Q3 programme is
ill-founded. Testing it needs two independent HIL passes over the same 59
claims and a Cohen's κ. I recommend that **before** any classifier work.

---

## 4. Q4 — Is the Wolfram-connector parallel deep or shallow?

**Position: CC1's objection is correct, and the distinction does change what
should be built.**

The earlier seat wrote that a connector's "NL in, computation out" is what a
panel model does when it writes a falsifier. CC1 objects that a connector
translates a *stated* question, whereas the founder describes the model *forming*
the claim worth computing — so translation is a proper subset of reasoning.

**Demonstrated rather than asserted, on the brief's own specimen.** Given the
stated question "what is the standard deviation of 2, 4, 6", Wolfram returns
`2.` — a correct, complete translation. It executed; it is evidence. What it
does not and cannot do is ask *which convention the document's author meant*.
That question is nowhere in the input. Yet it is the question that decides the
verdict: under one convention the document is defective, under the other it is
correct. A tools-first reviewer computes 1.633, compares to 2.0, and reports a
defect that may not exist. The brief itself does this — it reports the specimen
flatly false, citing `numpy.std`'s default.

That is the founder's principle demonstrated against the brief that argues for
it, using the brief's own example. **Translation is a proper subset of
reasoning, and the gap is exactly the unstated assumption.**

**What it changes in the build.** The REDUCE stage must emit **the assumptions a
falsifier depends on**, not only the falsifier. Hence `ClaimRecord.assumptions`,
and one rule with teeth:

> A falsifier whose verdict flips under any assumption listed on its claim must
> return **UNDECIDED**, not CONFIRMED. The assumption is then a finding in its
> own right — "this document does not state which standard deviation it means" —
> routed to HIL.

Without that rule the claim ledger inherits the defect: it would have recorded
`CONFIRMED` on the specimen and been wrong. Mechanically checkable: re-run the
falsifier under each listed assumption and compare verdicts. That is a tool
deciding, not a vote.

**What would overturn this.** If assumption-sensitivity turns out to be rare —
if over the 29 corpus claims fewer than, say, 2 flip under any plausible
convention — then the rule is machinery for a case that does not arise, and
`simplicity-default` says drop it. I measured 1 of 1 on the specimen and did
**not** sweep the corpus. That sweep is the test, and it is cheap.

---

## 5. Q5 — What the harness actually does, including on itself

### 5.1 On this brief

`scripts/harness_on_this_brief_2026-09-30.py`, over the real dispatched files:

```
=== this brief   bench/logs/intelligence_first_2026-09-30/BRIEF.md
    chars 13165   resolve_target_kind prose (suffix .md)
    reducible False (target carries no code; syntax gates not applicable)
    fenced listings 0
    S_k flag OFF NO_SCORE      S_k flag ON NO_SCORE
    gamma_input 0.170966  beta=0.829034  r2=0.995754  n_windows=7
=== corpus fixture NUM-05 (STEM, fenced)
    reducible True (3 fenced listings)
    S_k flag OFF NO_SCORE      S_k flag ON ESCALATE
    gamma_input 0.227373  r2=0.999668
```

**Where it abstains, correctly:** S_k returns `NO_SCORE` on every brief, both
flag settings. No fix was offered, so there is nothing to score. This is the
harness behaving well and it should not be "fixed".

**Where it decides something it should not:** nowhere on this path — which is
itself the finding. The brief's premise is that something over-decides. Executed,
nothing does. The gap is silence, not error: the harness has **no instrument at
all** for "which sentences here are decidable", because no live component takes a
claim as its unit.

**Where the correlation that hid this comes from:** on the fixture corpus,
"carries fenced Python" and "carries decidable claims" coincide, because the
fixtures were written to carry both. On a brief they come apart completely —
0 fences, many decidable claims. The admissibility signal and the decidable
content are disjoint, exactly as the brief says; my disagreement is only about
which component is at fault.

### 5.2 On itself — the harness adjudicating my own work

This is the part no static analysis substitutes for. **I made three errors in
this review. The harness's own rules caught all three, and no model vote was
involved.**

1. **`execute-do-not-grep` caught a wrong instrument.** My first fence
   comparison used `run_verification`'s *outcome* as the signal and reported the
   canonical ` ```python ` fence as a disagreement. Wrong: `NO_APPLICABLE_CHECKS`
   is returned **both** when nothing was found **and** when listings were found
   and parsed cleanly (`bugzilla_loop.py:496`), because a clean parse is a veto
   that passed, not a check that ran. Reading the code would not have caught it.
   Running it did. Recorded in the script's docstring so the next reader does not
   repeat it.
2. **The additive standard's removal clause caught a would-be regression.** I
   proposed deleting the duplicate extractor in favour of the runner's. The
   committed measurement said **no**: 2 shapes (`>  ```python`) were recognised
   by the duplicate and *not* by the survivor. Dominance failed, the removal was
   refused, and the fix had to be re-shaped as a *widening plus rewiring* with
   nothing removed. Had I trusted the judgement that the runner's regex was
   "obviously better", I would have silently dropped a capability.
3. **My own falsifier refuted my own reading.** I reported `gamma_input = 0.5`
   on every target and was about to call it a hard-coded default. It was: I had
   omitted the runner's window retry (`reference_runner_v3.py:15185-15196`).
   With the retry, γ_input takes **9 distinct values** across 9 targets,
   range 0.315, r² > 0.99. The wrong figure is recorded as wrong in the script.

**This is the strongest evidence in this note for the founder's position, and it
is evidence about the coupled design, not about either half.** In all three
cases the reasoning proposed something plausible and a tool refused it. In none
of them would the tool have had anything to chew on without the reasoning that
proposed the claim. Neither half would have produced the result alone — which is
the founder's "two sides of the same coin", measured rather than asserted.

### 5.3 What my proposal would change

Under A4, this note's own review would have produced a `ClaimRecord` per
proposition (P1, P2, P3, the dominance claim, the γ_input claim), each with its
falsifier and verdict, and the three errors above would appear as
**verdict transitions on identified claims** rather than as prose confessions a
reader must take on trust. That is the measurable benefit and it is the reason to
build it. It also means the claim ledger would have recorded my γ_input error as
a REFUTED claim rather than losing it.

### 5.4 On the external citation

I did not read the Nature article and make no claim about it. Two observations
that cost nothing: one external study plus one internal near-miss
(`docs/EXTENDED_RATIONALE.md:119`) is not a mechanism, and CC1 is right to say
so. **What in this archive could test the same hypothesis:** the project runs
commissioning arms with the falsifier gate on and off. An arm pair differing
*only* in whether the seat is instructed to reduce-to-tool first would measure
the effect directly on this project's own targets, with findings-per-round as the
outcome. That experiment does not exist and is buildable from
`bench/tools/commissioning_arms_2026-09-21.py`. I did not run it.

---

## 6. Q6 — The three outstanding items

### 6(a) The three wirings

**Corpus on the live path.** Already measured and pinned: 0 of 5 live modules
reach it, codified in
`bench/tests/test_declared_patterns_reach_the_live_path_2026-09-30.py` with a
ratchet. **Suggestion:** the claim ledger is the natural consumer — the corpus's
29 tagged claims and 5 discriminating falsifiers are exactly a
`ClaimRecord` fixture set. Wiring the corpus *to the ledger* makes it reachable
by a live component and gives the ledger a caller and a test from commit one,
which is the condition §1.2 put on A4. **One wiring closes two problems.**

**Fix-efficacy for prose.** The probe (`bench/fix_efficacy.py:132`) is already
substrate-agnostic — nothing in it tests `target_kind`. The blocker is
`compute_sk`'s prose short-circuit, and **the fix is not to lift it.** Lifting it
re-opens the harm the one-sided rule closed (3 of 5 harmful fixes REJECTED today;
lifting returns them to a weighted mean that admitted 5 of 5). **Suggestion:**
route `e1` into the claim channel instead. The claim ledger asks the right
question for prose — "did the fix make this claim's falsifier stop firing?" —
and that is exactly `FIX_CURES_ITS_OWN_FALSIFIER`, computed per claim rather than
per document. No gate changes.

**The document's own claim suite as the prose test command.** This falls out of
the ledger for free: `test_cmd` for a prose target becomes "run every
`ClaimRecord.falsifier` on this document". It is the first prose test command
that is substrate-appropriate rather than borrowed — and today argparse
substitutes an *unrelated* Python suite when no command is configured
(`reference_runner_v3.py` docstring, measured on
`commissioning_arm4_prose_20260930T064044Z`: the immune-memory suite runs against
a prose target and returns 0.9454545 whether the document has real bytes or is
gutted). That substitution should be **refused**, not improved.

### 6(b) A measured non-cure must reach the registry and HIL

**This ruling cannot be honoured today, and the reason is worse than a missing
status: the fact is not persisted at all.**

- There is no status for it. The vocabulary is `OPEN CORROBORATED CONFIRMED
  REFUTED CLOSED MERGED WITHHELD CONTESTED ESCALATED UNCONFIRMED REOPENED
  DUPLICATE` (`reference_runner_v3.py:1961-2087`). None means "measured, did not
  cure".
- The outcome string `FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER`
  (`bench/fix_efficacy.py:70`) exists, but it is **not among the catalogue record
  fields** (`reference_runner_v3.py:3495-3525`). It is stored as a side dict and
  surfaced only as a model-facing feedback line. **It does not travel into the
  registry export.** A HIL reviewer reading the exported catalogue cannot see
  that a fix was measured and failed.

**Suggestion, minimal and additive, in this order:**

1. Add `fix_efficacy` to the catalogue record fields. This alone makes the fact
   inspectable and is the smallest change that honours the ruling. **Do this
   first and separately** — it adds a field and changes no decision.
2. Only then consider a status. The founder's ruling is that a measured non-cure
   is neither plain REJECT nor plain ESCALATE, and the vocabulary comment already
   warns that `ESCALATED` is "the SOLE arbiter state — do not widen it". A
   non-terminal `FIX_INEFFECTIVE` that keeps the finding OPEN and flags it for
   HIL fits the ruling. **This is a founder call, not mine**, and it should not
   be made until (1) has produced a run's worth of data showing how often it
   fires.

**Do not** build the proposed `_e1_veto`. It does not exist in the live tree, and
turning a measured non-cure into an outright REJECT contradicts the ruling it is
meant to implement.

### 6(c) n*, the gamma collision, and complexity-based round counts

**There are three gamma conventions, not two, and the published pair is a
chimera.**

| name | where | quantity | on identical data |
|---|---|---|---|
| γ_input | `bench/input_complexity.py:241` | 1 − β, Heaps exponent over **text vocabulary** | — |
| γ_convergence | `reference_runner_v3.py:3190` | 1 − β over **cumulative novel findings**, clamped [0,1] | **0.2143** |
| Duane γ | `bench/decay_analysis.py:26` | β itself, growth exponent, same substrate as above | **0.8776** |

The last two share a substrate and use **opposite** conventions
(0.8776 vs 0.2143 on the series `[8,2,6,5,4,3,3,9]`; note 1 − 0.8776 ≈ 0.1224,
the clamp accounting for the residue).

**(4.89, 0.709) reproduces from no archived fit — 0 of 379 Duane fits in
`bench/results/round_robin_phase2/decay_analysis.json`.** Its α half is nearest
`ft-014/deepseek` α=4.8969, which carries γ=0.7417. Its γ half is nearest
`ft-006/deepseek` γ=0.7082, which carries α=4.1502. **The two halves come from
different records.** Independently reproduced by two prior seats over 421 and 379
curves. And the γ value 0.709 belongs to the Duane convention while the formula
`n* = (a/θ)^(1/γ)` is applied with the runner's inverse convention — which is the
collision, not merely a naming clash. No live module emits `a` at all
(`decay_analysis` computes it and discards it as an `alpha == 0` guard).

**Conclusion: n\* is not recoverable. Stop trying.** `rounds = 10` at
`bench/tools/commissioning_arms_2026-09-21.py:104` is an empirical cap with a
founder ruling behind it, and it is more honest than a derivation from a chimera.

**The founder's alternative is live and it varies.** `target_complexity` is
already recorded once per run (`reference_runner_v3.py:15234`) carrying
`gamma_input`, `beta`, `r_squared`, `n_windows`, `target_chars`, currently
`informative_only: True` and firewalled from every gate by a test. Measured
(`target_complexity_is_a_constant_2026-09-30.py`):

```
this brief              γ=0.170966   A19 brief      γ=0.206685
corpus NUM-05           γ=0.227373   GLOSSARY       γ=0.227645
corpus ALG-02           γ=0.259398   bugzilla_loop  γ=0.384571
PAPER                   γ=0.391083   EXTENDED_RAT.  γ=0.408181
reference_runner_v3.py  γ=0.485911
9 targets, 9 distinct values, range 0.314945, variance 0.01097842
(stdlib and numpy agree to 8 decimals), r² > 0.99 on every fit
```

Direction is sensible and matches the runner's own prose: low γ = complex and
novel (a fresh brief, 0.171), high γ = repetitive (a 900k-char module, 0.486).

**Two cautions before anyone wires it to a round count.**

1. **It is computed pre-run and it is cheap** — genuinely better than a
   post-hoc decay fit for the founder's stated purpose.
2. **The correlation with rounds-needed has never been measured.** Not once.
   `docs/EXTENDED_RATIONALE.md:65` hypothesises the threshold "may correlate with
   constraint count multiplied by constraint interaction density" and that has
   never been tested either. **A quantity that varies is not a quantity that
   predicts.** The naive small-target path also pins `n_windows = 7` by
   construction, so the fit is window-count-normalised in a way that has not been
   examined.

**The test, and it is the one thing I would build first on Q6(c):** take every
archived run with a recorded target and a recorded convergence round, compute
γ_input on each target with the runner's retry, and regress rounds-to-convergence
on γ_input. Report r² with a confidence interval. **Until that number exists,
γ_input must stay `informative_only: True`.** Its firewall test
(`bench/tests/test_target_complexity_is_reported_2026-09-10.py`) is currently the
only thing preventing an unvalidated statistic from becoming a gate, and it
should not be relaxed on the strength of the variation shown above. Variation was
the *precondition* for the hypothesis, not evidence for it.

---

## 7. Code changes made (two, both additive; everything else is a suggestion)

Found by execution while answering Q5, not by reading. **The harness carried two
independent fenced-Python extractors on its two live prose paths and they
disagreed.**

`scripts/two_fence_extractors_disagree_2026-09-30.py`, calling both on identical
bytes: **3 of 13 realistic fence shapes split them** — a tilde fence, a fence
carrying an info-string attribute, and a CRLF (Windows-authored) document — every
one in the direction *the runner sees code, close-the-loop does not*. On such a
document S_k's prose path engages while `run_verification` returns
`NO_APPLICABLE_CHECKS` carrying the message "carries no fenced Python listing",
which is **false of the document**. The weaker claim reached the log. A fourth
shape produced a **false FAIL**: a fence indented inside a list item extracted
still-indented, and the harness reported "the fix leaves 1 of 1 listing(s)
unparseable — unexpected indent" against a document whose Python is valid. A
false FAIL accuses the fix.

**Change 1 — `bench/reference_runner_v3.py:10581`, `_MD_PY_FENCE_ANY` widened**
from `(?:>[ \t]?)*` to `(?:>[ \t]*)*`. Strictly additive: `[ \t]*` accepts
everything `[ \t]?` accepted, so no shape that matched can stop matching.
Necessary because dominance **failed** before it (§5.2, error 2).
Regression-checked: extraction is **byte-identical on all 5 corpus documents and
all 1200 repository markdown files**.

**Change 2 — `bench/bugzilla_loop.py`, both narrow call sites rewired** to the
runner's `_gateable_hunks` (function-level import, matching the existing
local import of `attempt_close` at `reference_runner_v3.py:3861`, since the two
modules reference each other).

**Nothing was removed.** `_PY_FENCE` stays defined. The dominance measurement
(`fence_extractor_dominance_2026-09-30.py`, 360 shapes: subset **True**, proper
**True**, 120 vs 10) is recorded so a later removal is *evidenced* when a human
makes that call. It is not a licence taken here. My first draft of the code
comment claimed the removal was licensed; that was wrong and is corrected in the
comment itself.

**Verification:** `scripts/one_extractor_invariant_2026-09-30.py` drives both
live entry points over 14 shapes — **0 path splits, 0 false FAILs** — and should
become a permanent regression test. `python3 -m pytest
bench/tests/test_prose_acceptance_stem.py
bench/tests/test_falsifier_abstains_on_an_absent_target_2026-09-30.py -q` →
**250 passed**.

**Reported, not fixed: `_MD_PY_FENCE` (`reference_runner_v3.py:10559`) has zero
callers.** A third extractor, byte-identical to the narrow one, defined and never
reached — the project's most-confirmed defect class (11 of 11 since 2026-08-01),
live in the same module as the defect above. **Suggested to HIL**, not removed,
per `feedback_fixes_hil_only`.

---

## 8. Where I stopped, and what remains untested

Stopped under the project's own criterion: the last two passes produced no new
finding above the real-world-consequence threshold, and every HARD assumption in
the recommended design has been tested except the three named below. Passes used:
4 of 5.

**HARD assumptions still untested, with what would test each:**

1. **That a claim ledger is not already duplicated by the finding registry.**
   Test: on an archived prose run, count distinct claims in the target against
   distinct findings in the catalogue and measure the mapping. If 1:1, build A3
   and not A4. *This is the strongest attack on §1 and I did not run it.*
2. **That per-claim decidability is a well-posed label.** Test: two independent
   HIL passes over the same claims, Cohen's κ. If agreement is low, Q3's
   classifier programme is ill-founded regardless of model class.
3. **That γ_input predicts rounds-to-convergence.** Test: regress archived
   rounds-to-convergence on γ_input, report r² with an interval. Until then
   γ_input stays informative-only.

**Disagreements preserved.** I disagree with the brief's Fact 1 (§0, executed),
with its Fact 4 as written (incomplete — `ESCALATE` is a third exit), with its
implied remedy (§1.2 A2, refuted), and with its own specimen figure
`claimed_mean_is_false` (§4 — the mean half is false, the standard-deviation half
is convention-dependent and four tools including Wolfram say the document is
right under the sample convention). I agree with its Facts 2, 3, 5 and 6, and
with its diagnosis that the admissibility signal and the decidable content are
disjoint — while locating the fault in a different component. I have not seen the
other seat's return and so name no disagreement with it.

<!-- verbatim-end -->
