# The try-order question has two objectives, and no single key optimises both

2026-10-07 14:45 BST

## Summary: the tension was never dissolved because it is two questions wearing one name

Three successive proposals for ordering the falsifier ladder each dissolved half of a tension and left the other half standing. The founder observed this directly on 2026-10-07: *"This leaves the tension in place? My solution, your solution and Astra's did not dissolve it?"* The observation is correct, and the cause is structural rather than a failure of analysis by any panel seat. Under a cap on the number of ladder rungs, the ladder makes two decisions that carry two different objectives, and those objectives have different optima. A single sort key cannot be the optimum of both.

The two objectives are stated precisely below, each verified by at least two independent tools.

## The two objectives, and why they cannot be merged

**COVERAGE.** The probability that no seat resolves a finding is `P(unresolved) = prod(1 - p_i)` over the seats actually tried, where `p_i` is the probability that seat `i` produces a CONFIRMED falsifier. This quantity is **order-invariant**: it is a property of the SET of seats tried and nothing else.

Verification, 2 tools. SymPy expanded the product over all 120 permutations of 5 symbolic probabilities and found 0 mismatches against the reference expansion. Exact rational arithmetic over a concrete instance returned 1 distinct value across all 120 permutations.

**SPEND.** The expected cost to the first CONFIRMED verdict, or to exhaustion, is `E[cost] = sum_j c_j prod_{i<j}(1 - p_i)`, where `c_i` is the cost of dispatching seat `i`. This quantity is **order-dependent**, and it is minimised by placing seat `i` before seat `j` whenever `p_i * c_j >= p_j * c_i` — the cross-multiplied form of `p/c` descending, which is well defined when a seat costs nothing.

Verification, 3 tools. z3 searched for a counterexample over the reals under `0 < p < 1` and `c >= 0` and returned `unsat`; the converse search also returned `unsat`, so the condition is necessary as well as sufficient. Brute force over 400 randomly generated instances with between 3 and 5 seats compared the key's order against the global optimum found by exhaustive permutation, in exact `Fraction` arithmetic: the key attained the optimum 400 times of 400, Wilson 95% interval [99.0488%, 100.0000%].

Because coverage depends only on the set and spend depends only on the order, "which seats are tried" and "in what sequence they are tried" are different questions. Every proposal so far has answered the second.

## Worked example with real values, under the live cap

Three seats, shaped like this project's own roster: two free seats of middling and poor strength, and one dear seat that is the only one with a real chance on a hard finding.

| Seat | `p` | `c` |
|---|---|---|
| weak, free | 0.05 | 0 |
| middling, free | 0.10 | 0 |
| strong, paid | 0.80 | 100 |

With the cap at 2, there are 3 possible pairs. The coverage-optimal pair is {middling, strong}, leaving the finding unresolved with probability 0.18. The spend-optimal pair is {weak, middling}, leaving it unresolved with probability 0.855 — a factor of 4.75 worse. The two objectives select different sets, which is the whole claim in one instance.

**A second worked case shows the ordering objective going vacuous.** If every candidate seat is free, `E[cost]` is identically 0 for every order. Measured across all 6 permutations of 3 free seats: 1 distinct value. So among free seats cheapest-first is not merely the wrong rule; it carries no information at all, and only the set matters.

## What is live in the repository, measured rather than assumed

OBSERVED on the tree at commit `20ec400a`:

- `routing_max_rungs` has a dataclass default of **2**, and **0 of 47** experiment configuration files pin it, Wilson [0.0000%, 7.5558%]. The cap governs every routed run.
- `routing_enabled` has a dataclass default of **False**. The literal key appears in 5 configuration files, but `reference_runner_v3` maps the legacy alias `take_up_slack_enabled` onto it, so routing is **effectively on in 23 of 47** files.
- `DEFAULT_FALSIFIER_STRENGTH` is **5 rungs**: Codex, CC2, ChatGPT, Gemini, DeepSeek. With a cap of 2, **3 seats are never asked at all**, and the order selects 1 of the 10 possible pairs.
- The order can matter — meaning at least 2 ladder rungs appear on the configuration's declared roster — in **22 of 23** routed configurations, Wilson [79.0088%, 99.2283%].
- Exactly **1 rung is free**, CC2. The seat `fable` is free and does not appear on the ladder at all. This is recorded as a fact requiring a ruling, not asserted as a defect.

The ladder is intersected with each configuration's declared `models` roster: a rung absent from the roster returns an empty reply and the ladder advances. The configuration file is therefore the authorisation surface for paid dispatch on this path, and no unauthorised-spend defect exists in it.

## Two measurement defects in the producing script, both failing toward the comfortable answer

OBSERVED, and both corrected before any figure above was reported:

**The configuration search pointed at a directory that has never existed.** The first draft globbed `bench/configs` and reported "0 config files", which is indistinguishable in a report from "no configuration pins the cap". The real files are in `bench/expNN_configs/`. The correct denominator is 47; the figure quoted to the founder earlier the same day was 49.

**The free-seat declaration was read from a sandbox harvest copy.** Discovery walked every Python file under `bench` with last-match-wins and resolved `FREE_SEATS` to a harvested copy under `bench/logs/`, which records what a panel seat was given rather than what runs now. Live code declares it at `bench/confer_maths_panel_2026-09-05.py:411`.

Both are instances of the standing lesson that an instrument is the weak point: check the predicate before the result. Both are now held by executing guards.

**A third defect was caught by an existing guard, minutes after the note block was written.** The new SESSION STATE paragraph in the recovery document cited "35 passed, 0 failed" without naming the command that produces it, and `test_recovery_session_state_is_current_2026-09-11.py` refused the save on the ground that a suite figure whose producer is absent "can go false without anything noticing". That is the rule requiring a measured figure to travel with its script, enforced mechanically on prose.

## What this implies for the ordering rule, as a proposal awaiting a ruling

PROPOSED, not built. The decomposition suggests two rules rather than one, attached to the two decisions:

1. **Membership of the tried set** is decided by the probability that nobody resolves the finding. Minimising `prod(1 - p_i)` over sets of size K means taking the K seats with the highest resolve probability. Order is irrelevant here, so no sequencing argument belongs in this step.
2. **Sequence within that set** is decided by expected cost, settled by the cross-multiplied comparator `p_i * c_j >= p_j * c_i`. Where every member is free the comparator ties and the step is a no-op.

Under this split, the founder's instruction to escalate from the cheapest upward and his objection to sending a hard problem to a weak model are both correct, about different variables, and they do not conflict. The conflict existed because one knob — a single ordering tuple — was doing both jobs.

**The blocker is a measurement, not a design choice.** Both rules require `p` conditioned on the finding. What the archive supports is `p` marginal over all findings, which cannot distinguish a hard problem from a trivial one. A conditioned estimate does not exist in the repository, and without it the selection step chooses the same two seats for a research-grade problem as for a typographical error. That is the precise point at which all three earlier proposals, and this one, still stop.

## Status of each artefact

- `bench/why_one_ordering_cannot_serve_both_objectives_2026-10-07.py` — COMMITTED at `20ec400a`. Produces every figure above. `--help` runs no checks and costs nothing.
- `bench/tests/test_two_objectives_cannot_share_one_key_2026-10-07.py` — COMMITTED, 12 tests, all passing. Every test CALLS the producing functions rather than asserting on their text. Two are mutations: one asserts that a probability-only key is not spend-optimal, the other that a cost-only key is not coverage-optimal. A guard that passed against the wrong comparator would establish nothing.
- The two-rule split — PROPOSED. Nothing is wired, and nothing should be until the conditioning question is answered.

## Correction from the P-pass: the founder's own ruling dissolves the selection half

The falsification attempt against the decomposition was to ask whether an ERRORED rung frees its slot for a later seat. If it did, the realised set would depend on which seats errored rather than on the order, and coverage would stop being order-invariant. OBSERVED by execution: it does not. `route` applies the budget as a slice, `list(rungs)[:_budget]`, so an errored rung is already inside the slice and its `continue` buys no replacement. With the cap at 2 and rung 1 erroring, the seats dispatched are still exactly the first 2. The decomposition survives.

**The same lines carry a ruling that changes the conclusion.** `bench/routing.py` quotes the founder verbatim, 2026-10-06: *"I don't think there should be a cap at all. If it's a measured statistic, along with capability fingerprinting then the problem should run until it is either resolved, or the ladder is exhausted. (No more models to try.)"* And `max_rungs=0` is already wired to mean exhaust: executed against the live ladder, it dispatches all 5 rungs rather than 2.

Under exhaustion the tried set is the whole ladder. `prod(1 - p_i)` is then a **constant**, verified over all 120 permutations as 1 distinct value, so the selection question disappears and only expected spend remains — which is exactly the problem the cross-multiplied comparator solves optimally. **So the tension is dissolved by the founder's ruling, and the cap of 2 is what keeps it alive.** The conditioned estimate of `p` is required only if the cap stays.

What remains OBSERVED and unresolved is that the ruling is not in force: `routing_max_rungs` still defaults to 2 and 0 of 47 configuration files set it to 0. That is a wiring gap, not a design question. Guards: 5 further tests in `bench/tests/test_two_objectives_cannot_share_one_key_2026-10-07.py`, 17 in total, all calling `route` with stub seats and no spend.

Written under CDSFL note standard v1.7 (26 August 2026).
