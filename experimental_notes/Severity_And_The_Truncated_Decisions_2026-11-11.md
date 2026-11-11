# Severity, the truncated decisions, and a recommendation that was backwards

11 November 2026, 17:25 GMT. Repository at commit `92ae4a1a`, branch `sim/shakedown-2026-09-29`.

## Summary

This note closes 3 things: it restores the 3 recommendations that reached the founder cut off mid-sentence and explains why; it answers 3 questions he raised about severity, about `v_bar`, and about the dimensional check; and it withdraws a recommendation made earlier the same day which the evidence shows was stated backwards.

The headline is the withdrawal. Entry B136, on the dimensional check reporting homogeneity as correctness, carried a recommendation to move that check to `secondary_only` so it could corroborate but never refuse. Measurement shows the opposite: the check is sound exactly when it refuses and carries 0 information when it confirms. The recommendation would have kept the worthless half and discarded the sound one.

## 1. The truncation

3 of 10 recommendations in `Decisions_Awaiting_You_2026-11-11_GENERATED.txt` reached the founder cut mid-sentence: 0.300000, Wilson 95% [0.107791, 0.603222], statsmodels and a SymPy symbolic solve agreeing to 2.776e-17.

The proximate cause is `_gist` at [build_decisions_file_2026-11-07.py:106](../scripts/build_decisions_file_2026-11-07.py), a hard 150-character limit on each index line. `git log -S` dates it to `e796a010`, 2026-11-07, unchanged since.

**The first measurement was the wrong one, and that matters more than its result.** It asked whether truncation had become more frequent. It had not: 6 of 56 index lines on 2026-11-07 and 2026-11-08 against 5 of 27 since, Fisher exact p = 0.325711, odds ratio 1.893939, scipy cross-checked against an independent arbitrary-precision hypergeometric sum in mpmath agreeing to 5.551e-17. On that evidence the founder's report would have looked mistaken. It was not.

**The real change is in his copy, not in the index.**

| copy | bytes | words | detail sections |
|---|---|---|---|
| his, 2026-11-08 | 132,241 | 22,902 | 30 |
| his, 2026-11-11 | 5,962 | 1,026 | 0 |
| repository, 2026-11-11 | 49,616 | — | 11 |

His copy fell to 0.044800 of its former word count and lost every full argument. The split is deliberate and is recorded at [build_decisions_file_2026-11-07.py:890](../scripts/build_decisions_file_2026-11-07.py) as `tts_index = render(mrb, rows, spoken=True, detail=False)`, written to the Desktop path, with the comment `★ THE COPY HE ACTUALLY READS IS THE INDEX, on his complaint of 2026-11-08.`

**So this is a composition defect.** A 150-character index cap is harmless when the full argument follows below; an index-only copy is harmless when nothing is cut. Together they yield a recommendation that stops mid-sentence with no recourse.

**The artefact contradicts itself.** The 2026-11-11 file states, verbatim: *"Written at the raised cap, on your ruling of the 6th of November that you never specified a cap. Nothing here is cut to fit a length."* It then cuts 3 recommendations to fit 150 characters. The founder's position — that he asked for a presentation change (issue, why it matters, recommendation) and not a numerical limit — is corroborated by the generator's own header text.

**Repair:** make the cap conditional on `detail`. Restoring all 3 lines costs 143 characters against a 5,962-byte file. Not applied: `d` was in force.

## 2. The 3 recommendations, restored

**Decision 6, B125 — joint brief quoting files that have moved** (190 chars, 41 lost):
> Have the joint brief quote the state of every file it references, as at the blind half's dispatch, composed with a refusal when a referenced file has moved since.

The founder accepted the quoting half on 2026-11-11. The refusal half is what was cut. Note his composability standard binds: the composed form needs a measurement showing it dominates either half alone.

**Decision 8, B141 — the commit gate checking its own declared cost** (245 chars, 98 lost — the worst of the 3):
> SPLIT IT: put the FILE-COUNT assertion on the gate, because that number only moves when someone deliberately edits the guard list, and leave the COLLECTED-COUNT assertion in the full suite where entry closures belong.

**Decision 10, B143 — the severity proof and a third consequence weight** (153 chars, 4 lost):
> REPOINT THE PROOF AND ADD A THIRD WEIGHT, taken in that order and with the collection done first by me without troubling you.

## 3. The dimensional check is one-sided, and B136's recommendation is withdrawn

`_verify_dimensional_analysis` at [immune_agents.py:1633](../bench/immune_agents.py), called directly:

```
1 km = 2000 m    -> CONFIRMED  conf 0.85     FALSE
1 km = 1000 m    -> CONFIRMED  conf 0.85     true
5 kg = 99 g      -> CONFIRMED  conf 0.85     FALSE
3 m + 2 s = 5 m  -> REJECTED   conf 0.85
```

Verified on 3 tools:

- **pint** — all 4 claims are dimensionally homogeneous; only 2 are numerically true. Homogeneity and truth are independent, so CONFIRMED carries no information about correctness.
- **z3** — the dimension constraints for `3 m + 2 s` return `unsat`. No assignment of magnitudes makes an inhomogeneous sum well-formed, so a refusal is a proof.
- **SymPy** — used for the exact-rational interval arithmetic below.

**Therefore B136's recommendation is withdrawn.** `secondary_only` would preserve corroboration (uninformative) and remove refusal (sound). The defect is that the check emits `CONFIRMED` at confidence 0.85 on claims whose truth it never examined, and downstream code reads that as correctness.

## 4. What to do on a detected dimensional error

Exhaustive enumeration of 3-term equations over 4 units: of **60** inhomogeneous cases, **24** admit more than 1 equally minimal repair — 0.400000, Wilson 95% [0.285695, 0.526339], statsmodels and SymPy agreeing to 0.000e+00. Where all 3 terms differ there are 3 equally minimal repairs; where 2 of 3 agree the repair is unique.

An earlier example suggested uniqueness; it was the easy case, and the founder's intuition that the repair is underdetermined is correct in 0.400000 of cases. A further limit is not statistical: even a unique minimal repair does not recover intent, since `3 m + 2 m = 5 m` is a valid repair of `3 m + 2 s = 5 m` and the author may have meant a rate calculation.

**Automatic correction is refused on 2 independent grounds:** underdetermination at 0.400000, and the standing rule that fixes go to the human in the loop and are never auto-applied.

**Recommended route (single fix, not composed):** feed the detected error back to the harness models for a proposed repair, then re-run the dimensional tool against that proposal. This is not a model vote — the model supplies a candidate, the tool decides, which is the project's confirm-programmatically rule honoured. Escalation to the human in the loop is the terminal branch, taken where the re-check still refuses or where the minimal repair is non-unique. A terminal branch is not a composed fix and does not trip the composability measurement requirement.

Non-uniqueness is cheaply detectable by the modal-unit count, so exactly those cases route to a human and the rest are tool-decided — minimal human intervention without driving it to 0.

## 5. `v_bar`, and what the panel settles

`v_bar` is severity: the mean severity of genuine findings, [run_exp19_fff.py:339](../bench/run_exp19_fff.py). The panel settles the principle; the residue is a consistency defect needing no ruling.

The principle: a mean assumes the gaps between severity levels are meaningful. If severity is ordinal, they are not, and the mean is inadmissible.

The residue: 4 sites compute this one name by 4 different formulas —

| site | formula |
|---|---|
| [run_exp19_fff.py:339](../bench/run_exp19_fff.py) | plain mean over all findings |
| [run_exp12_live_wire.py:508](../bench/run_exp12_live_wire.py) | 50/50 blend of 2 fingerprints |
| [dm/_manager.py:743](../bench/dm/_manager.py) | mean over recent rounds |
| [dm/_manager.py:751](../bench/dm/_manager.py) | exponentially weighted moving average |

4 programs, 1 name, 4 numbers. That is a defect whatever the panel rules.

## 6. What the brief still needs

The founder extended his own framing: if the model sits above any particular measure and each domain carries its own consequence scales, then there may be **several** measures per domain, and the harness's **domain classification of the target** is what selects which applies.

Checked against `bench/logs/severity_is_ordinal_2026-11-11/BRIEF.md`: `v_bar` appears **0** times, and no section states that scale selection follows from domain classification. The brief's §1 does carry his framing verbatim and survived the compaction intact.

**3 additions owed before dispatch:** (1) the admissible-scale set per domain is not fixed at 1; (2) scale selection is driven by the harness's domain classification, making it a routing question and not only a definitional one; (3) `v_bar` is a live in-code instance of the inadmissible operation, so the panel has an example and not only a principle.

## 7. State

**Ready to build:** B22 (what a fix means outside code — widen claim patterns, runway note on specialist-cell generality), B77 (convergence gate seat count — adopt the exact version), B84 (difficulty estimator — record the class of missing reference points, build nothing), B88 (fold-back gate suite visibility — launcher refuses a substituted default), and the founder's ruling that **both** claim prose and proposed fix are the admissible basis, which unblocks the Fable exploit repair.

**Restored above, now answerable:** B125 refusal half, B141 in full, B143 in full.

**No verdict recorded:** B142 (interface roles onto harness roles) — 9 annotations on a 10-item file; apparently passed over.

**Withdrawn:** B136, replaced by §3 and §4 above.

## Producers

All figures produced by execution on 2026-11-11, none quoted from memory. Truncation and word counts: `build_decisions_file_2026-11-07.py` called directly via `collect()`, not parsed. Dimensional verdicts: `immune_agents._verify_dimensional_analysis` on 4 claims. One-sidedness: pint and z3. Repair ambiguity: exhaustive over 3-term equations on 4 units. Every proportion carries a 95% interval on 2 independent routes; maximum inter-route disagreement observed 5.551e-17.

Written under CDSFL note standard v1.9 (1 November 2026).
