# Three questions: is this fix defensible, do the night's findings hold, and how do we run a FAIR test?

You are reviewing work committed at `48d6254` (see `git show HEAD`). Answer all
three sections. **Run the code; do not reason from the brief.** Where the brief
is wrong, say so — two earlier rounds found premises of mine false, and both
times that was the most valuable part of the review.

## Section 1 — the fix: sane and defensible?

`CRITICAL_DEFINITION_PREREG_2026-05-18.md` (F6) mandates two things that were
**never built**: γ reported at 0.5/0.6/0.7/0.8 "so a reviewer sees the full
threshold profile, not a single chosen point", and per run "the count of findings
where rubric and numeric disagreed, and the verdict's sensitivity to that
disagreement". Measured: neither in the code; **0 of 50 archived real reports**
carries a profile.

Built: `gamma_threshold_profile()` and `boundary_band_census()` in
`reference_runner_v2.py`, both diagnostic, neither touching the gate.
`_settled_novelty_series` gained an optional `severity_threshold` defaulting to
the pre-registered proxy so every existing caller is byte-identical.

**The threshold is NOT moved** — the pre-registration calls that "the single
largest cooking vector" and the founder's ruling is "keep 0.7".

**Questions.** Is the parameterisation genuinely behaviour-preserving for every
existing caller? Is `boundary_band_census` defensible as a *proxy*, given the
rubric is consequence-based and cannot be evaluated mechanically — or does
shipping a proxy under a pre-registration clause that asks for rubric
adjudication risk being mistaken for the real thing? Is `PREREG_BOUNDARY_BAND
= 0.10` justifiable, or arbitrary in the same way 0.7 once was? **Does this fix
enhance the schema or quietly weaken it?**

## Section 2 — do the night's findings hold?

Verify or refute each, with evidence:

1. **A model could delete a finding by repeating itself.** `add_verdict` appends
   unconditionally; `auto_resolve_contested` counts verdict ROWS, not distinct
   models. Reproduced: one model, one reply, three CHALLENGE lines → severity-0.9
   finding auto-refuted. Confirmed pre-existing at real HEAD. Repaired by
   per-reply dedupe, **but the repair is per-reply**: a model challenging across
   three ROUNDS still auto-refutes. Is that residual acceptable, and is the right
   repair in the tally rather than the parser?
2. **No natural break at 0.70.** 6,865 archived findings; scipy KDE minima at
   0.12/0.37/0.62; numpy histogram valleys at 0.67 and 0.71; **401 findings
   (5.8%) sit exactly on 0.70**; moving to 0.72 reclassifies 456 (6.6%).
3. **The simulated panel rates 0.132 severity points lower than the real panel on
   the SAME defect** (source_hash/load integrity, open in both runs): real n=22
   mean 0.609, sim n=28 mean 0.477, Mann-Whitney p=0.0006, Welch p=0.0012.
4. **Of 11 falsifiers the discrimination control tested, only 4 discriminate**
   (36.4%, Wilson [15.2%, 64.6%]).

## Section 3 — the founder's hypothesis, and how to run a FAIR test

The founder asks whether the simulated runs find few criticals because **the
target has been "done to death"** — reviewed 3–4 times in days — rather than
because the stand-ins under-rate.

The evidence I have: the target grew **317 → 489 lines** (commit `043a0a8`,
2026-08-15, "Exp 47-49, the control-run findings, and the instrument repairs").
exp45's 12 critical ROWS collapse to **5 distinct themes** (2.4× duplication
across models). **2 of the 5 are fixed** (`decay_rate` validation, negative-count
rejection); 3 remain. The rehearsal found **2 criticals against 3 still-open
themes**, and found all three themes — rating them 0.65, 0.52, 0.50, i.e. just
under the line.

**Questions — this is the section that matters most.**

- Does the founder's hypothesis hold? Quantify how much of the 12→2 drop is
  explained by (a) the target being repaired, (b) row-vs-theme deduplication, and
  (c) genuine severity under-rating. My split may be wrong.
- **A rehearsal against a target its own panel has already repaired cannot be a
  fair test of finding-discovery.** What target *should* a simulated run use?
  Options I can see, none obviously right: a frozen historical revision of
  `_memory.py` as exp45 saw it; a module never reviewed; a deliberately seeded
  target; or rotating targets per run. What are the trade-offs, and what would
  make the result comparable to a live run rather than merely internally
  consistent?
- Given the 0.132 rating shift, is a simulated panel a valid instrument for
  anything **severity-dependent** at all, or only for machinery validation?

Return per item: `VERIFIED` / `REFUTED` / `UNSUPPORTED`, the evidence, and what
you would do instead. Section 3 needs a recommendation, not just a critique.
