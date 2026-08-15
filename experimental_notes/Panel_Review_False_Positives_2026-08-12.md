# Panel review: telling a false positive from a true finding, deterministically

2026-08-12, 01:59–02:11 BST. Five models, one dispatch, approximately £3.

Full unedited responses: `bench/logs/pr_false_positives_2026-08-12/` (one JSON per
model, 81,397 characters total). Structured per-model extraction with verbatim
quotes: `experimental_notes/Panel_False_Positives_2026-08-12_full_extraction.json`
(153 KB). This note synthesises; it does not replace either.

Run under `pr` semantics — no compelled convergence. Each model gave an independent
verdict and its strongest falsification of the others. Disagreement is preserved
below as information rather than smoothed toward consensus.

Panel: CC2 (Claude Opus 4.7, 16,089 chars, 219 s), Codex (GPT-5.5, 21,404, 109 s),
ChatGPT (GPT-5.5, 20,118, 140 s), Gemini (3.1 Pro Preview, 7,537, 45 s), DeepSeek
(V4 Pro, 16,249, 174 s).

## The prompt carried a premise that was refuted after dispatch

The panel was told the control document's claims were "intended to be true, so that
any critical finding against it is false by construction". That premise was refuted
by direct measurement the same night — see the companion note on the zero-plant
control. The document contains real, unplanted defects and the confirmed findings
against it are true positives.

This is recorded rather than hidden because it produced the review's most useful
result: **four of the five models rejected the premise unprompted**, and the one that
accepted it produced the weakest answer. That is an unusually clean natural experiment
in why convergence should not be compelled.

## Where all five agreed

**The falsifier's computed outcome should be emitted structurally and compared by the
runner, not inferred from prose.** Every model proposed this independently. Gemini
specifies a `verdict.json` carrying `{"expected": X, "actual": Y}`; Codex a normalised
tuple of `(claim_id, claimed_value, observed_value, unit, operator, tolerance)`;
ChatGPT `{claimed, computed, operator, units}`; DeepSeek numeric extraction from
stdout compared against the claim; CC2 folds it into an "outcome algebra" covering
dedup, contradiction and independent recomputation.

This is the founder's own second criterion, raised repeatedly since early August and
not yet built. Five frontier models given the problem cold reached for it first.

**Failure-phase classification replaces the keyword verdict reader.** All five. The
failure must be classified by *where* it occurred — import, setup, or the declared
check — rather than by whether the author used a particular word in an assertion
message. Codex and ChatGPT both specify stack-frame origin; Gemini specifies exception
typing; DeepSeek exit code plus traceback origin; CC2 derives it as a consequence of
its mutation table.

**The false-positive rate has never been measured.** CC2, ChatGPT and DeepSeek state
this explicitly. ChatGPT: the criticals are "candidate critical accusations before
adjudication", not measured false positives.

**The existing control should be replaced by a corpus with a mechanical oracle.** All
five. Every claim derived by a script from stated inputs, so truth is a property of
the generator rather than an authorial assertion.

## The decisive refutation, and it lands on CC1's own recommendation

CC1 had recommended blocking closure when a falsifier never opened the target it
accuses. CC2 refutes it:

> "A gate whose satisfaction condition is *access* rather than *dependence* is one
> line away from being defeated, and it fails green."

Adding `open(TARGET).read()` and discarding the contents satisfies the gate. Coverage
then reports 100%, discriminating power is zero, and the metric moves in the direction
that looks like success. CC2 names it as the same shape as the Exp-48 forensic scan
that reported CLEAN because it globbed the wrong pattern.

The recommendation is withdrawn. The check remains useful as a **coverage floor** —
computable on 100% of falsifiers against the discrimination control's 20% — but it
must not close anything on its own.

CC2 also names three classes of legitimate falsifier the check would wrongly refuse:
one reading a warm bytecode cache rather than the source; one running work in a
subprocess invisible to parent-process instrumentation; and one recomputing from
premises quoted in the finding itself.

## The replacement: differential mutation sensitivity

CC2's headline instrument, and the reason it matters is one sentence:

> "The discrimination control is degenerate because it needs a *corrected* copy,
> which needs the answer. It does not. It needs a *perturbed* copy, which needs
> nothing."

The runner — explicitly never a model — mutates the accused span in a scratch copy,
separately mutates an unrelated control span, re-runs the falsifier against each, and
reads a four-row table:

| Accused span | Control span | Reading |
|---|---|---|
| verdict changes | unchanged | depends on the accused content — CONFIRM-eligible |
| unchanged | — | verdict independent of the accusation — block |
| changes | changes | global or undiscriminating — block |
| unchanged, still failing | unchanged | environment-level failure — block |

The fourth row deterministically replaces the keyword classifier: a setup failure is
*invariant to the target*, and invariance is measurable without reading anyone's
assertion message. All three phrasings that defeated the keyword check land in the
same row.

The instrument is itself falsifiable, which is the property that makes it admissible:
seed it with a known-good falsifier against a known-planted defect (must show
sensitivity) and with `assert False` (must show invariance). If those two do not
separate, the instrument is broken and says so.

Codex and ChatGPT independently propose the same shape — Codex as "irrelevant-mutation
control", ChatGPT as "unrelated-span perturbation" — and both name dynamic taint
tracking from the accused bytes to the failing branch as the principled endpoint.

## Two findings CC1 had not reached

**Run A is a free true-positive arm.** CC2 observed that the seven claims repaired on
1 August were real defects present at Run A's dispatch, so Run A's criticals can be
scored against them mechanically. This was measured immediately and confirmed: Run A's
seven criticals map almost exactly onto the seven repaired claims. See the companion
note.

**The convergence gate reads the wrong numerator.** `gamma_critical` and the
K-consecutive-zero counter are computed over *rated* criticals rather than
*adjudicated* ones. CC2's framing: "the interesting failure here is not the
false-positive rate, it is that the system's stop rule is driven by a quantity nobody
has adjudicated."

This is not an argument against gamma, which remains load-bearing and is not in
question. It is a question about what feeds it, and it is worth a decision.

## Preserved disagreement

**Gemini** accepts the Q5 steelman entirely and places every fault on the runner:
"Precision is the exclusive responsibility of the mechanical runner." It also
contradicts itself — Q3 says the control's correctness is "an authorial assumption,
not a mechanical guarantee", while Q4 says "the number of CONFIRMED findings is your
exact False Positive count". Both cannot hold. Shortest response in the panel by a
factor of two and the least engaged.

**Codex** did not spot the false premise, and it cost the answer: it wrote off the
discrimination control on the strength of it ("for clean documents the corrected copy
degenerates"), which is false against the measured document. Its structured verdict
protocol is nonetheless the panel's most implementable single proposal.

**DeepSeek** falsified the zero-plant control convincingly, then prescribed a
replacement scored by "if a finding points to a planted defect it is a true positive,
otherwise it is a false positive" — reproducing the exact un-tampered-equals-correct
fallacy it had just demolished.

**ChatGPT**'s one worked falsifier has inverted polarity: given the contract that a
falsifier fails if and only if the defect is real, its example passes when the defect
is real. A panel model got the core contract backwards in the course of explaining it.

## CC1's position

The mutation-sensitivity instrument should be built, and it should be built before the
capstone rather than after. It is the only proposal on the table that resolves the
degeneracy without requiring an answer key, it honours the determinism constraint
completely, and it subsumes the keyword-classifier repair rather than sitting beside
it.

The open-the-target check should still be built, but demoted to telemetry with an
explicit note that it is defeatable and must never gate closure alone. Recording a
weak instrument as weak is worth more than discarding it, because its coverage is
100% where everything else is partial.

The structured outcome artifact should be built first of the three, because it is the
cheapest, it has unanimous support, it is the founder's own long-standing proposal,
and every other mechanism becomes easier once falsifiers emit their numbers instead of
narrating them.

## Method note

The panel was dispatched with measurements rather than conclusions, and explicitly
invited to attack them. It did. The single most valuable output was not any proposed
mechanism but the independent rejection, by four models, of a premise the prompt
asserted as given.

Written under CDSFL note standard v1.2 (14 May 2026).
