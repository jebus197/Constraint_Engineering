# The two reviewers disagree about canaries, and both are right about different things

**Preserved rather than resolved by preference, per the founder's `pr` rule. CC1's own reading follows, and
it is a position, not a summary.**

## fable — the distinction is real and the instrument already measures the right axis

> *"The founder's correction invalidates the module's stated purpose, not its instrument… Exhausted-but-reading:
> organic space empty, capacity intact → a fresh seeded defect gets killed. Churning: recycling rather than
> reading → the fresh defect is missed. Both states show flattened gamma, K zero-critical rounds, low rho.
> Only an externally-known fresh defect distinguishes them."*

Recommends **keep**, with a named exit: run one probe in Bench Run 2 and measure sensitivity; retire then,
with data, if it does not separate the states.

## cc2 — the module has no channel through which churn could arrive

Proved it rather than argued it. **Verified independently by CC1:**

```
occurrences in bench/canary_seeding.py:  rho 0   gamma 0   churn 0   round 0
```

`catches()` takes a flat list of findings with **no round index**; `detection_rate()` returns one p̂ per
model over the whole run. There is no temporal dimension anywhere in the module.

CC2 built two synthetic panels and pushed both through the module. **CC1 reproduced this exactly:**

| panel | distinct outputs | caught | p̂ |
|---|---|---|---|
| exhausted (2 distinct findings, kills both early) | 2 | K1, K2 | 1.0 |
| churning (1 finding repeated, kills both late by recycling) | 1 | K1, K2 | 1.0 |

**Module output identical: `True`.**

## CC1's position

**They are not contradicting each other. They are answering different questions, and both answers stand.**

CC2 is right, demonstrably, that **the module as written cannot measure the distinction**. Nothing in it
knows what round anything happened in, so no amount of interpretation recovers churn from its output.

fable is right about the **principle**: a freshly seeded defect probes detection *capacity*, and capacity is
the axis on which an exhausted panel and a churning one genuinely differ.

The gap between them is exactly what fable's own protocol closes, and neither reviewer connects the two,
because each wrote independently. **The temporal dimension is supplied by WHEN the probe runs, not by the
module.** fable's design is a single out-of-band probe at the moment the two-sided gate first holds, against
a history-free copy, with the probe round excluded from gamma, rho and the registry. Under that protocol the
module needs no round index — there is only one round, and its position in time is the measurement.

So CC2's demonstration is not an argument for retirement. It is an argument that **the module must never be
fed a whole run's findings**, which is precisely the usage fable's protocol forbids.

## The question neither can answer, and both flag

**Does a churning panel actually miss a fresh canary?** CC2's construction assumes it kills them "late by
recycling"; fable lists sensitivity as unmeasured and names it as the falsifier of its own recommendation.

Neither can settle it without a live run. **That is the experiment, and it is one probe in BR2.**

## One thing the disagreement produced that neither reviewer claimed

CC2's second finding — that the overlay symlinked `.git` — had the side effect that
`canary_seeding._in_a_git_worktree` saw that symlink and made `seed()` **refuse the overlay**: the only
place in-flight seeding could ever have been legitimate. Fixed the same night. So the protocol fable
proposes was, until tonight, mechanically impossible to run.
