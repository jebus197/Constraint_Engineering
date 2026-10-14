<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 492dc53487d92db1a4e1f84953a74fa8dc707592b91319d99be1132b3b70138a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Specification — feeding no-falsifier findings back for resolution
**Written 2026-10-14, joint round J3. SUGGESTED, not applied.**

## What the measurement established, and what it did not

His claim — that these findings are not computationally irreducible, that a
model cannot simply say nothing, and that the project has existing mechanics to
feed them back — **holds**, with one asymmetry that must be stated because it
bounds the spec below.

| figure | k/n | % | Wilson 95% |
|---|---|---|---|
| no falsifier / UNTOOLABLE (brief's figure, reproduced exactly) | 1938/3298 | 58.7629% | [57.0736%, 60.4318%] |
| same, harvested-sandbox copies excluded | 1886/2994 | 62.9927% | [61.2476%, 64.7044%] |
| **demonstrably irreducible — a reason in the record says so** | **18/1938** | **0.9288%** | **[0.5883%, 1.4634%]** |
| widest conceivable irreducible bound (any reason-bearing entry) | 126/1938 | 6.5015% | [5.4876%, 7.6876%] |
| **never attempted — nothing in the record but the claim** | **1365/1938** | **70.4334%** | **[68.3629%, 72.4231%]** |
| target a `.py` file | 1751/1938 | 90.3509% | [88.9554%, 91.5867%] |
| called UNTOOLABLE or ERROR by the machinery, later decided by a falsifier | 36/3298 | 1.0916% | [0.7895%, 1.5074%] |

Producers: `scripts/how_many_untoolable_were_never_attempted_2026-10-14.py`,
`scripts/the_archive_denominator_triple_counts_harvest_copies_2026-10-14.py`.
Every proportion carries a Wilson interval from statsmodels and a hand-derived
Wilson in mpmath at 50 dp; worst disagreement 1.11e-16.

**The asymmetry.** The archive cannot show that a tool was tried and failed for
the remainder, because **no field records an attempt**: `untoolable_reason`,
`irreducible_reason`, `falsifier_attempts` and `execution_log` are **0 of
3,298**. So "never attempted" is strictly "nothing in the record", and the 18
is a floor on irreducibility, not an estimate of it. The ratio of
never-attempted to demonstrably-irreducible is 75.8 : 1, and 36 findings the
machinery itself called UNTOOLABLE or ERROR were later decided by a falsifier.
That is enough to confirm his claim and not enough to put a number on true
irreducibility. **The first thing to build is therefore the record, not the
loop** — otherwise the same question is unanswerable again next quarter.

## The mechanism, in four parts, against real call sites

The channel already exists. `bench/dm/_feedback.py` builds per-finding records
(`FindingFeedback`, `build_feedback_records`, `build_feedback_sections`) and
prepends them to round K+1's prompt, imperative not advisory, capped at
`top_k=10` per model and ranked by schema-disagreement magnitude. Nothing new
is needed to carry the message. What is missing is a record kind for "this
finding has no falsifier", and a place to put the answer.

**Part 1 — the attempt record (build this first; it is the root cause).**
On the registry entry, one field written by the falsifier path, never by a
model: `falsifier_attempt` = `{round, outcome, detail}` with `outcome` in
`{NOT_ATTEMPTED, SUPPLIED, BROKEN_IMPORT, TIMEOUT, NO_TOOL_APPLIES}`. Written
where `falsifier_verdict` is already written, so the two cannot drift. Default
absent means NOT_ATTEMPTED, so every archived entry reads correctly without
migration. Acceptance: the J3 question becomes answerable from the field alone.

**Part 2 — the feedback record kind.** A fifth `FindingFeedback` kind beside
REJECTED / FFAFP-FAIL / DUPLICATE / R_k-discrepancy: **NO_FALSIFIER**, raised
for any entry whose `falsifier_code` is absent or blank after strip. Rank it
below REJECTED and above DUPLICATE — a refuted claim is more urgent than an
unproven one. It inherits the existing `top_k` cap, so the prompt cannot blow
up; the overflow is already summarised in aggregate by
`build_feedback_sections`.

**Part 3 — what the model is required to return, and the honest exit.** The
record asks for one of exactly two things, and this is the part that makes the
loop terminate rather than spin: either **a runnable falsifier** per the core
directive's own requirements (imports the real target, fails iff the defect is
present, run via `execute_python` before reporting), **or** a named
`NO_TOOL_APPLIES` justification identifying which part of the claim is not
computable and why. The second is a legitimate answer — the directive's own
words are that an honest UNTOOLABLE is a correct outcome — and it is what
populates `falsifier_attempt.outcome`, turning the 70.43% from silence into
data. A model that returns neither has not answered; the record repeats next
round, which is the existing channel's behaviour and needs no new code.

**Part 4 — what must NOT be built.** No convergence authority moves. The
feedback record gates nothing, blocks nothing and admits nothing: the harness
arbitrates, exactly as today. A finding with a `NO_TOOL_APPLIES` justification
is still routed to human review, not auto-confirmed, because the runner's
re-execution of a falsifier is the only thing that confirms anything. Any
version of this in which a model's justification closes a finding is out of
scope and should be refused.

## Why this and not something larger

Parts 2–4 are prompt and ranking work inside a module that already does exactly
this for four other record kinds. Part 1 is one dict on an entry, written at a
site that already writes a sibling field. The alternative — a new routing rung,
a new queue class, or a new bound — adds parameters to machinery whose current
bound is already compared against a count these findings never enter (measured
0 on the only run cited for it, 2026-10-13). **This project has shipped 11
confirmed defects that were additions nothing reached.** The record field is
the one piece that is certainly reached, because the J3 question cannot be
asked again without it.

## Not built here, and why

The prompt text a model receives is the founder's, and J4 of this round
measured that the directive sections mandating runnable falsifiers and
falsifier integrity do not currently reach any seat through the directive files
at all. **Specifying a feedback record that asks for a falsifier, while the
section defining what a falsifier must be is not delivered, would be asking for
compliance with an unread rule.** The delivery question is therefore a
precondition of Part 3, not a parallel task. That ordering is the one
substantive thing this spec asserts beyond the measurement.
