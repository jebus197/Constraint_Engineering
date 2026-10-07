# The combined rule meets 5 of 7 requirements by construction, and the 2 it misses are repairable without changing it

2026-10-07 22:30 BST

## Summary: how the combined rule dissolves the tension, in 3 steps

The founder asked directly: *"how does this combined approach solve the tension exactly?"* It does so in 3 steps, each verified rather than argued.

**Step 1. Removing the cap deletes one of the two questions.** With no limit on ladder depth, every seat is eventually reached, so the probability that nobody resolves a finding, `prod(1 - p_i)`, is taken over the whole roster. It becomes a CONSTANT: 1 distinct value across all 120 permutations of 5 seats, confirmed symbolically in SymPy with 0 mismatches and in exact rational arithmetic. The question "which seats do we try" ceases to have content, because the answer is always "all of them, eventually".

**Step 2. What remains is ordering alone, and ordering has a provably optimal rule.** Expected cost to the first CONFIRMED verdict is `sum_j c_j prod_{i<j}(1 - p_i)`, and seat `i` belongs before seat `j` exactly when `p_i * c_j >= p_j * c_i`. z3 returns `unsat` on a counterexample search in BOTH directions, so the condition is necessary as well as sufficient; brute force over 400 random instances attains the global optimum 400 times of 400, Wilson [99.0488%, 100.0000%].

**Step 3. That rule is a sort key over measured numbers, so it inherits the properties the founder asked for.** It is not a list to maintain. It is a comparison, and a comparison does not care whether it is handed 1 seat or 500.

So the tension existed because a single frozen tuple was doing 2 incompatible jobs. Removing the cap retires the first job; the key settles the second.

## The 7 requirements, measured one at a time

His requirements, in his own framing: *"the number of models used may eventually be entirely arbitrary. It could be 5, or 6, or 70, or 500, or 1."* *"Free, cheap, model name, setting an arbitrary limit on how far the ladder can climb ... are not meaningful considerations. The only thing that impacts capability in the schema, should be capability."* *"A ladder is bidirectional ... if a weaker model gets better at doing a job ... it should be able to climb."* And the guard: *"what we need to guard against is simply counting when a model is successful as an 'improvement in capability'."*

| | Requirement | Verdict | Evidence |
|---|---|---|---|
| R1 | Roster size arbitrary | **MET** | total order produced at 1, 6, 70 and 500 seats; monotone in the key at every size |
| R2 | No cap on depth | **MET** | `max_rungs=0` already means exhaust, and reaches all 6 rungs by execution |
| R3 | Capability, never name | **MET** | the key reads 2 measured numbers; no label appears in it |
| R4 | Never hand a seat work it cannot do | **MET, conditionally** | holds only because exhaustion makes coverage constant; under a cap it fails |
| R5 | Bidirectional | **MET** | a weak seat climbs and a strong seat falls at 6, 70 and 500 seats, with no tuple edited |
| R6 | A success is not a capability gain | **NOT MET** | a point estimate promotes 1-of-1 over 60-of-70 |
| R7 | Computed efficiently; the researcher waits | **NOT MET** | cost is money alone, and the researcher pays in time |

R1, R2, R3 and R5 are satisfied by the shape of the rule rather than by anything added to it, which is the strongest form of satisfaction available. The 2 failures are real and neither requires abandoning the rule.

## R7, and why it is the founder's Riemann objection surviving in a different currency

A hard finding, 4 cheap weak seats at a 2% resolve-rate and 1 dear strong seat at 80%, the weak seats costing 1 and the strong seat 100. Ordering by money puts the strong seat LAST. The answer still arrives, because exhaustion guarantees it, but:

| Ordering | Expected dispatches | Expected spend |
|---|---|---|
| by money (`p/c` descending) | **4.80** | 96.12 |
| by capability (`p` descending) | **1.78** | 100.78 |

That is **2.70 times the dispatches** — 2.70 times the researcher's wait — to save **4.85%** of the money. The trade-off is genuine and not an artefact: the dispatch-optimal order and the spend-optimal order are different permutations, confirmed by exhaustive search over all 120.

So his objection to handing a hard problem to a weak model was never only about failing to get an answer. Under exhaustion the answer arrives regardless. What is squandered is the one resource his own framing names explicitly — *"problem in (by the researcher, who then waits)"*.

**The repair needs no new rule, only an honest cost.** Price each dispatch in the researcher's waiting as well as in money, and the same key reorders itself. Sweeping the weight on waiting from 0 upward, the key crosses over to capability-first at a weight of just **2**: at 0 the order is the 4 weak seats then the strong one; at 2 and above the strong seat leads. One key serves both ends of the spectrum, and the exchange argument survives the change of currency — z3 returns `unsat` in both directions with cost defined as money plus a weighted latency term.

This is precisely the shape of Astra's section 6.4, which scores value over cost-plus-latency-plus-human-burden rather than over money. The founder's no-cap ruling and that scoring are therefore complementary rather than competing: his ruling removes the selection question, and the multi-currency cost makes the surviving ordering question answer the right objective.

## R6, and why it belongs to the estimator rather than the ordering

His guard is arithmetic, not philosophical. A seat with 1 success from 1 attempt has a point estimate of 1.0000, which outranks a seat sitting at 60 of 70 on 0.8571. Ordering on point estimates therefore promotes a single lucky success to the head of the ladder, which is exactly what he said to guard against.

A lower confidence bound refuses:

| Seat | Point estimate | Wilson lower bound | Jeffreys lower bound |
|---|---|---|---|
| 60 of 70 | 0.8571 | **0.7566** | 0.7614 |
| 1 of 1 | **1.0000** | 0.2065 | 0.1467 |

The closed-form Wilson bound agrees with statsmodels to within 1 part in 10^12, and a Beta posterior agrees on the direction. A newcomer needs **12 consecutive successes** before its lower bound can pass a seat at 60 of 70. That is the guard he asked for, expressed as a number rather than a policy.

It also solves a problem that would otherwise need a separate rule: **a seat with no measurements at all has a lower bound of 0.0000 and sorts last, then climbs on evidence.** No placement decision is required for a new seat, and none was taken when Fable was added.

## What the live roster actually is, which corrects the earlier note

The founder's correction was right and the earlier note understated it. The panel dispatcher's roster carries **7** seats, not 5 and not 6: `cx`, `cgpt`, `ge`, `ds`, `cc2`, `fable` and `kimi`. Kimi K3 is already wired, against `api.moonshot.ai`, with a measured quirk recorded in the orchestrator that it refuses any temperature but 1.

**There are 2 independent rosters and they disagree.** The falsifier ladder in `bench/routing.py` was a hardcoded tuple of 5 display names; the panel roster is separate code using short keys. The 47 experiment configuration files declare only the 5 display names — 46 CC2, 46 Codex, 46 ChatGPT, 45 Gemini, 45 DeepSeek and 0 Fable. A hardcoded name tuple cannot satisfy R1 at any roster size, which makes it the deeper defect; adding a name to it treats a symptom.

## Status of each artefact

- `bench/allocation_by_measured_capability_2026-10-07.py` — COMMITTED. Produces every figure above; `--help` runs no checks and costs nothing.
- `scripts/cdsfl_utils.py` — COMMITTED and ENABLED. A git call that cannot run now reports what a failed call reports, and an unreadable working tree is never reported clean. Guard: `bench/tests/test_git_state_degrades_offline_2026-10-07.py`, 14 tests.
- `bench/routing.py` — COMMITTED and ENABLED. Fable is the 6th rung, placed last because its lower confidence bound is 0.0000 on 0 attempts. Verified by execution that a capped run still dispatches exactly Codex then CC2, so no existing dispatch was displaced.
- Deriving the ladder from measured capability instead of a tuple — PROPOSED. Nothing is wired.
- Pricing the researcher's wait into the cost — PROPOSED. Nothing is wired.
- Using a lower confidence bound as the key — PROPOSED. Nothing is wired.

## Is there a better way

On the evidence gathered here, no — with 2 qualifications, and both are repairs to the inputs rather than to the rule.

The rule itself is optimal for the objective it is given: the exchange argument is necessary and sufficient, and it is the unique ordering rule with that property, so there is no third candidate to compare. What can be wrong is the objective. Giving it money alone produces the dispatch-count failure measured above; giving it money plus the researcher's wait does not. Giving it point estimates violates the founder's own guard; giving it lower confidence bounds does not.

The one structural extension worth naming is that cost is properly a VECTOR — money, waiting, and human attention — collapsed by weights the researcher sets per task, because a researcher chasing a deadline and a researcher chasing a budget are not optimising the same thing. That is Astra's formulation, and this analysis finds it correct in shape where it was earlier reported only as relocating the problem.

What remains genuinely open is unchanged: an estimate of resolve-rate conditioned on the particular finding. Under a cap that gap was load-bearing, because the wrong 2 seats lose the answer outright. Under exhaustion it is only an efficiency term, because the answer arrives either way and conditioning merely shortens the wait. **Removing the cap therefore downgrades the blocker from fatal to optimising**, which is the most consequential single effect of the founder's ruling and was not stated plainly before now.

Written under CDSFL note standard v1.7 (26 August 2026).
