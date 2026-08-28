# Panel review: the convergence gate's rho veto, and the merge path

You are one of three reviewers (CC1, CC2, Fable). CC1 curates and does not vote.
Your working directory is a disposable copy of the repository. Read it, run
tests in it, run the code. **Tools decide, not votes** — run the command, then
make the claim. Where you cannot check something, say so plainly rather than
reasoning around it.

Three questions. Q1 and Q2 are measured claims to falsify or confirm. Q3 is a
design question where disagreement is preserved as information.

---

## Q1. Is `rho` structurally hostile to convergence, and what should replace the veto?

**The measured claim, made by CC1 on 2026-08-28. Try to refute it.**

`_compute_rho` in `bench/reference_runner_v2.py` returns `novelty/raw`. A round
with zero raw output contributes `0.0` to the rolling average
(`reference_runner_v2.py:2078`). The churn flag is
`rho_avg < rho_threshold AND round >= rho_earliest_round` (defaults 0.25, 12).

In `_check_gamma_alt_convergence`, `if rho_churn:` at **line 4979** is an
**early return that fires BEFORE the zero-critical streak is evaluated** at 4988.

CC1's measurements, which you should reproduce or break:

| scenario (round 12) | rho_avg | churn |
|---|---|---|
| honest total silence | 0.000 | True |
| exhausted, 2 duplicates a round | 0.000 | True |
| exhausted, 5 duplicates a round | 0.000 | True |
| winding down, 1 novel of 8 | 0.125 | True |
| winding down, 2 novel of 8 | 0.250 | False |
| recycling at volume | 0.000 | True |

The algebraic consequence CC1 draws: avoiding churn requires
`novelty >= raw/4` **every round, indefinitely**. A 5-model panel where each
model emits one finding per round has `raw >= 5` and therefore needs **>= 2
novel findings every round, forever**. But novelty falling to zero *is*
convergence. So the flag is anti-correlated with the outcome it certifies.

**Empirical check CC1 ran:** no archived run has ever tripped churn. The lowest
rolling average in the archive is exp43 at **0.287**, against a threshold of
0.25 — a margin of 0.037. CC1's explanation is a protective population
mismatch: rho is computed on ALL findings while the streak is CRITICAL-only, so
minor novelty keeps rho alive. The exposure is therefore a **clean document**,
where both dry up together.

**Ask yourself:**
- Reproduce the table. Does it hold on this tree?
- Is the anti-correlation argument sound, or is there a mechanism CC1 missed
  that prevents it?
- **The founder's position**, which you should treat as the design intent:
  rho should be *"a contributing measure when deciding if a problem space has
  been usefully exhausted"*. It is currently a **veto**. Is converting it from
  veto to contributor the right repair, and what would that look like
  concretely in `_check_gamma_alt_convergence`?
- The founder also objects that a zero-output round is not a real condition for
  an LLM — that every historical zero was broken machinery or a parse failure.
  Does that objection weaken the finding, given the blocked cases above have raw
  of 2, 5 and 8?

## Q2. The vacuous-curve guard appears unreachable when churn fires.

The guard for the clean-document case sits at **line 5002**, added 2026-07-29
after being found pre-launch on the zero-plant control. The churn early return
is at **4979**. CC1 claims the guard is therefore unreachable in exactly the
scenario it was written for.

Verify or refute by reading the control flow. If CC1 is right, what is the
minimal correct repair — reorder, or make the churn return conditional on the
vacuous check?

Note: exp53, the zero-plant control the guard was built for, ran twice and ended
at 3 and 4 rounds. Churn cannot fire before round 12, so the guard has never
been exercised against the condition that would disable it.

## Q3. Merge: wiring or building?

`reference_runner_v2.py:2183` — when arbitration votes MERGE, the runner does
**not** merge. It records `merge_blocked_reason` ("a model vote is not authority
to delete a finding from the gate"), logs MERGE WITHHELD, and returns
KEEP_DISTINCT. That closure implements the founder's no-voting ruling of
2026-08-19 and is correct.

But `reference_runner_v2.py:1193` already specifies the evidence a merge
requires, and it is **not** a vote: *"adjudicate_by_repair verdict SAME in BOTH
directions"*. `scripts/adjudicate_by_repair.py` exists, has run, and produced
**23 SAME-both-directions verdicts** in
`experimental_notes/data/adjudication_by_repair.json`.

CC1's conclusion: merge needs **wiring**, not building — the vote path was
closed and the tool path was specified but never connected.

**Ask yourself:**
- Is that right? Read both sites and the adjudicator.
- What breaks if MERGED is written on a repair verdict? Note that MERGED is in
  `_NON_NOVEL_TERMINAL_STATUSES`, so a merged finding leaves gamma, the novelty
  count, and `open_crit_high_count`. A **wrong** merge silently deletes a
  finding from the convergence evidence.
- The founder's question, which is the real one: *"aren't there cases where a
  degree of intelligence and judgement are still required? For a system like
  this to be considered an intelligent calculator a degree of intelligence and
  judgement is still required, since without this all you might have is a plain
  old dumb calculator."* Where, precisely, should judgement sit in the merge
  path without reintroducing voting? Disagreement here is preserved.

---

## Output format

For each question: **VERDICT** (CONFIRMED / REFUTED / PARTIAL, with what you
ran), **EVIDENCE** (commands and their output), **RECOMMENDATION** (concrete,
naming files and lines). Then a final section: **WHAT I COULD NOT CHECK**.

Do not pad. The founder is dyslexic and reads every word.
