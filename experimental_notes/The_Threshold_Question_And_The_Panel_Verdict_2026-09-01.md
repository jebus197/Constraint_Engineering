# The threshold question, the panel verdict, and what a fair test requires

**2026-09-01, 10:30 BST.**

## The question asked

> *"'Non-arbitrary' in the sense that I may not fully have comprehended and may have waved through during a period of lapsed attention... may still not be the same thing as being fully derived from the available data. Is that still a valid question to ask?"*

**Yes. It is valid, it is important, and the record shows it was raised at the time and never resolved.**

## What the record shows

`CRITICAL_DEFINITION_PREREG_2026-05-18.md` exists *because* the number was arbitrary before it — in its own words, "0.7 was an undocumented code convention (F6)", "indefensible to a hostile reviewer", "the single largest cooking vector". It fixed the definition **by consequence** in five clauses, declaring "the rubric governs, the number encodes it".

**But it cites the two confers as "both unanimous on this point" — and "this point" is its own antecedent: that an undocumented gate is indefensible. Not that 0.7 is right.**

On the number itself, the 2026-05-17 confer **split**, and the disagreement is preserved:

> *"The purely numerical `severity >= 0.7` cut is **arbitrary** and acts as a fragile heuristic proxy. It is currently functioning because it roughly correlates with the boundary between finite structural errors and infinite stylistic refinement."*

> *"SEVERITY CUT: **Sound, not arbitrary.** The 0.7 threshold corresponds to the CDSFL severity schema's High/Critical boundary."*

So the shape of the concern is right, though not its target. What was waved through was the **documentation fix**, which is sound. Underneath it, "is 0.7 the correct number" was raised, contradicted, and left open — for three and a half months.

## What the data says, now it has been looked at

Across **6,865** real archived findings:

| measurement | value | 95% CI |
|---|---|---|
| findings sitting **exactly on 0.70** | 401 = **5.84%** | [5.31%, 6.42%] |
| severities quantised to a 0.05 step | 4,948 = **72.1%** | [71.0%, 73.1%] |
| reclassified by moving 0.70 → 0.72 | 456 = **6.6%** | — |

- **No natural break at 0.70.** scipy KDE minima: 0.12 / 0.37 / 0.62. numpy histogram valleys: 0.67 and **0.71**, either side. The boundary sits on a local *peak*.
- **Severity is ordinal, not continuous** — ~20 rungs. A two-decimal threshold assumes precision the raters never supply.

**Honest position: the number is procedurally defensible and empirically unexamined.**

## And yet it must not be moved

The pre-registration names moving the number after seeing results as the single largest cooking vector — and this distribution evidence was gathered while investigating a result that displeased us. The ruling to keep 0.7 stands.

**The valid question is not whether 0.7 is right in the abstract, but whether it faithfully encodes the rubric it stands for.** That is testable, never tested, and requires no change to the threshold: *do findings ≥0.7 satisfy at least one of the five consequence clauses, and do findings just below fail all five?*

## The panel verdict on the instrument I built

**Refuted, correctly.** I validated the profile at `max_round=6`; exp45 ran **4 rounds**, converging at 3. γ is horizon-dependent and zero-padding inflates it monotonically:

```
[7,4,0,1]        -> 0.6213   <- exp45's real series, matching its recorded value
[7,4,0,1,0]      -> 0.6739
[7,4,0,1,0,0]    -> 0.7149
[7,4,0,1,0,0,0]  -> 0.7468   <- the figure I published
```

At the true horizon the instrument fires at **no** threshold; at `max_round=4` it reports the verdict **is** threshold-sensitive. My claim that it "strengthens the exp45 result" was exactly inverted.

Two structural defects beyond that: `gate_would_fire` reimplements a simplified gate that **appears nowhere in the runner** (ignoring configured thresholds, contested, unresolved-critical, the vacuous branch, the sparsity fallback); and on exp45 it reads the **ID-keyed** series `[7,4,0,1]` while the run gated on the **location-keyed** series `[4,0,0,0]`.

**This is the fifth wrong-artefact measurement in this body of work** — after a regex proxy instead of the parser, the truncated archive instead of full replies, raw text instead of stripped, and a guard measured on one round instead of all. The pattern is consistent and it is mine.

## The "done to death" hypothesis

**Majority explanation, not the whole one — and my own correction was itself corrected.**

- Target grew **317 → 489 lines**, commit `043a0a8`, 2026-08-15. Exactly **one** commit changed it between the runs.
- I said 2 of 5 themes fixed. It is **4 of 6** — **9 of the 12 original critical rows**.
- I said the rehearsal's 2 criticals were the still-open themes. **Both are against code the August repair created.**

| mechanism | share of the 12→2 drop |
|---|---|
| target repaired | **~75%** |
| row→theme dedup | **0 — anti-explanatory** |
| severity under-rating | **~25%** |

**The residual has a clean control.** Two defects live in code **byte-identical** between the pre-repair revision and HEAD (verified by AST comparison). exp45 rated them **0.72 / 0.80**; the rehearsal re-found them, executed working reproductions, and rated them **0.45 / 0.45 / 0.45 / 0.40**. Same bytes, no priming, −0.27 to −0.35.

The sharpest instance: a simulated reviewer reproduced a July finding **exactly** — the same hash-collision construction — executed it, passed every admissibility gate, and rated it **0.45 against 0.72**. *"The instrument found the defect and proved it. It priced it wrong."*

## Why this looked like a crisis and was not

A ~0.12 mean rating shift converts **mechanically** into a ~7.8× critical-rate ratio, because the boundary sits on a 5.8% spike. **Counting criticals amplifies a modest calibration gap into a dramatic-looking one and invites the wrong diagnosis** — which is precisely what happened to me.

## What a fair test requires

1. **Calibration → the frozen pre-repair revision.** The only design giving a **paired** measurement, since exp45's archived ratings are ground truth on those exact bytes. Report the *offset*, not the level. Near-zero cost: the rehearsal already runs in a worktree.
2. **Discovery/recall → a seeded target**, seeded from harvested real defects, not invented ones.
3. **A never-reviewed module** only alongside a real panel run, else the number is uninterpretable.
4. **Not rotation** — it destroys the longitudinal axis and makes instrument drift indistinguishable from target difficulty.

Four requirements, none currently met: a paired anchor; blinding enforced by checkout; **reporting the severity distribution rather than the count over 0.70**; and pre-registering the comparison before the run.

## Is a simulated panel valid for anything severity-dependent?

**Not at levels. Possibly at deltas, once calibrated. Definitely for machinery.** Invalid for critical counts, gate firing, convergence verdicts, or any BR2 go/no-go. Valid now for parser, dedupe, registry transitions, merge guards, gate plumbing, discrimination-control wiring.

## The finding that deserves its own decision

**88.4%** of scored discrimination-control records in the archive come from **simulated** runs, Wilson [80.4%, 93.4%] (the reviewer's structured count was starker). The mechanism carrying the project's central claim — *tools decide, not votes* — is presently evidenced overwhelmingly by simulation. Not a defect; a statement about where the evidence sits, and an argument for prioritising a real run that reaches the control.

## One reviewer did not report

Fable returned **54 characters** against a median of 7,512 across 14 reviews — *"Suite still running — I'll finalize once it completes."* It used 575s of a 2,400s budget and there is **no turn limit**, so it was not cut off; it returned voluntarily, expecting a second turn a single-shot dispatch never gives.

**The brief caused it** — I told reviewers to run a 5–7 minute suite without stating the dispatch is one-shot. The harness detected the non-answer, recorded `ok=False`, and **kept the result anyway**: its retry fires only on a completely empty response. To be re-dispatched before acting on any of the above, because the one time these reviewers disagreed, the minority was right.
