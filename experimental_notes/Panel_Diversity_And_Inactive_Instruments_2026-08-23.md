# The panel has never once recorded two models finding the same thing — and four convergence deciders have never been tested

**23 August 2026. Every figure reproducible offline at zero cost from `bench/logs/*/*_report.json`
and `experimental_notes/data/instrument_inventory.json`.**

---

## Why this was measured

The founder asked what a six-model panel working **in turn** buys over one capable
model, and pointed out that the star topology and the machinery built over the
preceding months exist precisely to answer that. The build experiment of 22 August
used a serial ladder instead and therefore could not answer it.

The archive can, because v2's star dispatch puts every model on the same target in
the same round. So the question was put to the archive rather than argued.

---

## What the star actually does, verified in the code

`reference_runner_v2.py` at the star branch injects the mathematical model **into
every model's prompt, every round**:

> *"Per-round metrics injection — models use γ, ρ, registry state to calibrate
> effort (cdsfl_operational.md §8, §13)."*

ρ, ρ̄₃, γ and the registry counts (OPEN / CONFIRMED / CLOSED) are written into the
panel prompt. **The mathematical model is not bookkeeping in v2; it is a feedback
signal to the panel.** A serial ladder with no rounds has nothing to inject, no
registry state to summarise and no γ or ρ to calibrate against.

That capability is real and the 22 August harness discarded it.

---

## But co-discovery has never been recorded. Not once

`source_aliases` records every model that raised a finding before deduplication
collapsed them into one canonical entry. Across the modern arc (exp42–exp49):

| | |
|---|---|
| findings | **566** |
| total source aliases | **566** |
| aliases per finding | **1.00** |
| findings raised by two or more models | **0 (0.0%)** |

**Not one finding in the entire modern arc was ever recorded as raised
independently by more than one model.**

That is not evidence of remarkable diversity. It is the aliasing mechanism never
firing, and it is already a known open item: runway 1.6 records that *"the alias
map is a bijection in all 28 registries; no entry has ever gained a second alias"*.

**The consequence is the one that matters: the project cannot currently measure
whether its models find different things.** The field that would show it is
structurally empty, so the central claim for running a multi-model panel at all has
no measurement behind it in this project's own archive.

## Cross-examination, the weaker signal

Do models at least pass judgement on each other's findings, even if co-discovery is
unrecorded?

| distinct models judging a finding other than its source | findings | share |
|---|---|---|
| **0** | **410** | **72.4%** |
| 1 | 98 | 17.3% |
| 2 | 36 | 6.4% |
| 3 | 18 | 3.2% |
| 4 | 4 | 0.7% |

299 of 566 (52.8%) carry any verdict at all; **156 (27.6%) are judged by at least
one model other than the one that raised them.**

**Two readings, and the data cannot separate them.** Either the panel genuinely
cross-examines only 28% of the time, or the recording of it is as under-populated
as `source_aliases`. This note does not choose between them. It is the same shape
as the discrimination finding of 22 August: the mechanism may work, and the record
cannot show it.

---

## ρ: what it is, and what is actually wrong with it

**What it is.** ρ is discovery efficiency, or semantic novelty rate: of the raw
findings a round produced, what fraction were genuinely new rather than restatements
of something already in the registry. `_compute_rho` (`:1656`) returns the current
round's value, a rolling average over `rho_rolling_window = 3` rounds, and a boolean
**churn** verdict. A falling ρ means the panel is going round in circles.

Both ρ and its rolling average are **computed every round and shown to the panel**,
which is how models are meant to calibrate effort.

**What is wrong.** Only the *churn verdict* is gated, and it is gated on
`rho_earliest_round = 12`, a constant with, in the code's own words, *"no derivation
on record"*. The rolling window is 3, so a defensible floor would be two full
windows — 6.

Measured across the modern arc:

| threshold | runs long enough for the churn verdict to fire |
|---|---|
| the live `rho_earliest_round = 12` | **5 of 11** |
| the derived floor of 2 × window = 6 | **9 of 11** |

**A correction to the runway.** Runway item 1.8 states that of exp44–49 *"only
exp44 (13 rounds) reaches R12"*. Measured now: exp44 (13) **and exp47 (14)** both
reach it — 2 of 6, not 1 of 6 — and 5 of 11 across the whole arc. The runway's
figure was written on 18 August, before exp47's missing rounds were reconstructed on
20 August, so it is stale rather than wrong-in-principle. It should be corrected
where it stands.

**The distinction that must not be blurred:** ρ is live and feeds the panel. It is
the *churn detector built on top of it* that cannot fire in half the arc. Saying
"ρ does not work" would be false.

**The fix** is a founder ruling, not an engineering choice: either derive
`rho_earliest_round` and record the derivation, or adopt the 2 × window floor that
is already computed in shadow at `:1696` and has never gated anything. Promoting it
changes convergence behaviour, so it needs clean data from a live run first.

---

## The inventory sweep: what else is inactive, and what has never been tested

Of the 34 instruments enumerated on 22 August:

**Six cannot affect a live run today:**

| id | instrument | state |
|---|---|---|
| I16 | discrimination control | presence-gated — fed by nothing until T02 merges |
| I24 | fix complexity (ν) | shadow |
| I26 | load balancer | shelved by founder ruling |
| I27 | shadow stage-6 | shadow |
| I33 | survived-falsification ledger | **not wired** |
| I34 | null-perturbation control | offline script only |

**Seven have no commissioning evidence at all** — no test that feeds them a
known-good *and* a known-bad input and asserts they answer differently:

| id | instrument |
|---|---|
| **I02** | **the two-sided gamma gate** |
| **I04** | **state-convergence check** |
| **I07** | **stall convergence** |
| **I08** | **budget extension** |
| I14 | the falsifier gate (measured NOT commissioned, 22 August) |
| I26 | load balancer (shelved) |
| I33 | survived-falsification ledger (not wired) |

**The first four are convergence deciders.** They are what ends a run. **I02 is the
two-sided gamma gate, which the founder holds as a standing directive: GAMMA IS
LOAD-BEARING.** None of the four has ever been shown to answer differently on a
known-good and a known-bad input.

That is not a claim that they are wrong. It is a claim that nothing on the record
shows they are right — which is exactly the position the falsifier gate was in
before it was tested on 22 August and found to accept `print('FALSIFIED')` as a
confirmation.

---

## What T01 was, and why it matters that it failed

**T01: route discrimination failures up the escalation ladder.**

The ladder (`_apply_routing`, `:3279`) already routes a failed critical to
progressively stronger writers and escalates to a human only when the strongest
cannot resolve it. But it fires on `escalated=True AND not CONFIRMED`, and a
falsifier that **fails the discrimination control is CONFIRMED** — it fired. So such
a finding never reaches the ladder.

Three independent writers — Codex, CC2, Fable — produced patches that applied and
then failed to make their own tests pass. It escalated to HIL.

**The consequence for the next run:** merging the six composable patches wires the
discrimination control (T02) but leaves its failures unable to reach the ladder.
**That is a half-repair and must be stated as one.**

---

## What the next run has to be

The founder's framing is right: build the revised runner, merge the fixes, then run
**live** to gather the data that does not exist. Specifically it must produce:

1. **Whether wiring the discrimination control changes what a run yields** — the
   50% figure of 22 August was measured on an archive produced without it.
2. **Whether the panel co-discovers** — which requires the aliasing mechanism to
   record a second model. Until it does, no run can answer the founder's question
   about six models versus one.
3. **Whether the six patches hold live**, not merely statically composed.
4. **Whether T01 is hard or the brief was bad.**

Item 2 is the cheapest and it is about the existing runner rather than anything
built on 22 August. Until aliasing records a second model, every future run
reproduces the same silence.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
