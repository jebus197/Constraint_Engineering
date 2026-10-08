# Both seats say sound with repairs, and the sharpest finding is that the convergence gate goes one-sided exactly where the hazard lives

2026-10-08 00:46 BST

## Summary: the verdicts, and the one finding that outranks the brief's own subject

Both free seats returned **sound with repairs** on the derived-capability routing design, and both delivered fixes as files with executed falsifiers rather than findings alone. 0 paid dispatches. cc2 answered with 14,564 characters, 2,178 words and 70 tool calls over 3421.4 s across 2 attempts; fable with 8,142 characters, 1,104 words and 62 tool calls in 955.0 s on its first attempt.

**The most consequential finding came from fable and is not about rosters at all.** `bench/reference_runner_v3.py:9207-9215` carries a sparsity fallback: when cumulative criticals fall below `gamma_crit_min_cumulative`, which is 8, `gamma` becomes reported-not-gated and closure rests on the zero-new-critical window **alone**. So the gate advertised as two-sided is **one-sided in precisely the endgame regime**, and the surviving half is the half a shrinking roster attacks. This is a code path that demotes gamma automatically whenever criticals are sparse, which is the standing directive's own prohibition arriving by the back door rather than by proposal. It requires the founder's ruling.

**The second most consequential came from cc2 and is a number nobody had.** At the archive-measured parameters the gate's **absolute** false-quiet rate at FULL roster is 0.1159 — an 11.59% chance that 3 consecutive quiet rounds arise without the problem space being exhausted, with every seat present. The brief framed the hazard entirely as a ratio between roster sizes and never stated the absolute 0.1159, which is the larger number and which **no roster-aware repair addresses**. Lowering it needs a higher global K or more seats.

## Where the seats converged independently

**The third state the design needs is a circuit breaker**, named by both seats without coordination, as `CLOSED / OPEN / HALF_OPEN`. Both also found that this is the project's own existing vocabulary rather than a coinage: `experimental_notes/CDSFL_UX_Vision_Sketch_2026-03-28.md` already specifies a "Circuit Breaker Display" and already offers "proceed without the failed model". The distinction from benching is made structurally rather than by documentation — cc2's module raises on any non-closed state lacking a re-probe deadline and caps backoff, so an unbounded re-probe interval, which is benching under another name, cannot be constructed.

**A degraded run should converge, but never silently.** Both seats reached this, and both raise the quiet-window requirement rather than leaving it fixed: cc2 derives `K(n) = ceil(K0 · log Q(n0) / log Q(n))`, giving K of 3, 4, 4, 5, 6 and 9 as the roster falls from 6 to 1 and holding the false-quiet probability at or below its full-roster value at every size; fable conserves seat-rounds with `ceil(n0·K0/n_live)`. Both label the outcome — `CONVERGED_DEGRADED_ROSTER` and a `_DEGRADED_ROSTER` verdict suffix — and both hold that a round with 0 live seats must not converge, because that is no evidence at all. Crucially both verified that a full roster behaves exactly as today, so a healthy run pays nothing.

**Keep `DEFAULT_FALSIFIER_STRENGTH`, as the cold-start tie-break.** Both seats refuted the proposal to replace the hand-written tuple with the derived key. The reason is arithmetic: on the first run every seat's lower confidence bound is exactly 0.0, so the derived key is a total tie and carries no ordering at all. cc2 measured it — 12 shuffled inputs produced 12 distinct orders without the tuple and 1 with it. The tuple is the only ordering information that exists at that moment, and it is itself a committed measurement from Exp 42.

**Kimi K3 needs no human classifier and no new mechanism.** Both seats found "hardest" to be an emergent property of the derived key rather than a judgement: an expensive seat has a large cost term, so the key places it late by construction, and it is reached only on findings where every seat with a better measured ratio has already failed. cc2 measured it dispatched on 3.61% of findings; fable computed a reach probability of 0.0287 in its worked example. Both note the corollary: when the rest of the roster measures near-useless, the key promotes the expensive seat instead of wasting the researcher's wait, which is the requirement working rather than a defect.

**Adding a model is one edit.** Both verified that `rank_falsifier_writers` already appends unranked models after the ranked ones, so the tuple is a priority prefix and not an allowlist: cc2 ran `rank_falsifier_writers(['Codex', 'BrandNewModel', 'DeepSeek'])` and got `['Codex', 'DeepSeek', 'BrandNewModel']`. A new model therefore needs only its entry in a configuration's `models` list; no ladder edit and no estimator edit. Both also turn the two-roster mismatch from a log line into a refusal, and both make removal a policy act requiring a recorded reason, explicitly forbidden as a response to a seat not answering — that is the breaker's job.

## The one genuine disagreement, and why both seats are right

**Is a single scalar cost sufficient, or must cost be a vector?**

cc2 says a scalar is not sufficient in general, and measured rather than argued it: it constructed an instance where the budget-constrained optimum is not optimal for **any** latency weight across 4001 tested values, concluding that a hard-capped resource such as the Max subscription needs a constraint rather than a weight.

fable says a single scalar suffices, and proved the ordering claim: z3 confirms the exchange rule survives any fixed non-negative linear combination of money and latency, and a vector adds a dimension that a one-scalar-per-seat sort key cannot consume.

**Both results are correct because they answer different questions.** fable's result is about the ORDERING: given a cost, the key is optimal, and any linear cost preserves that. cc2's result is about FEASIBILITY: a hard cap is not an ordering problem at all, because no weight can express "this seat is unavailable once the subscription is exhausted". The synthesis is therefore a scalar for the order and a separate constraint for the cap, which is exactly the shape of Astra's section 6.5 — a missing tool or authority is a hard feasibility exclusion rather than a low rank. The disagreement is preserved here as information, not resolved by preference.

## Where the seats contradicted the brief, and the brief was wrong

The brief's headline hazard figure rested on two parameters and **both were wrong**.

- **q.** The brief assumed a per-seat-per-round new-critical rate of 0.3. cc2 measured 0.233740, Wilson [0.215572, 0.252945], and rejected the assumption with an exact binomial test at **p = 5.6e-11**. fable measured 0.1994 over a wider population. The archive refutes the assumption on any reading.
- **The correlation.** The brief said it had never been measured and asked the seats how it could be. cc2 found the measurement already committed and runnable, which was fair: it was made after the brief was dispatched and the brief was deliberately not rewritten a second time, so the brief was stale rather than mistaken about the world. The consequence stands either way — there was nothing for a seat to propose.
- **The span.** The brief said the magnitude moves by a factor of 7.7915 across a plausible range. fable identified the error precisely: 7.7915 spans a correlation of 0 to 0.8, while the brief presented exact values only over 0.1 to 0.5, where the correct collapse is **6.053**.

**Corrected, the operative figure is near 1.4 rather than 8.49986**, and cc2 puts the 6-seat-to-2-seat overstatement at **29.1 times** (72.247616 against 2.4796).

**The load-bearing step survived, as the brief predicted it would.** Both seats confirm that recording the live roster is necessary at any correlation, because z3 returns unsat on separating 0 new criticals from a healthy panel from 0 from a depleted one — they are the same integer — and unsat on a round being both intact and degraded once the roster is recorded. Necessity follows from indistinguishability, and the magnitude sets only urgency.

## The correlation now has three estimates, and they do not agree

| Source | Population | Estimate |
|---|---|---|
| cc2 | 64 reports, 395 rounds, 1968 seat-rounds | ICC 0.405989, bootstrap [0.332313, 0.476821] |
| fable | 75 reports, 516 rounds | ICC(1) 0.4903, pairwise 0.5095; live-only 0.4581 / 0.4821 |
| CC1, within-experiment | 40 reports, pair-weighted | **0.236014**, against 0.405989 pooled |

All three agree the correlation is substantial and that q is not 0.3. They disagree on magnitude by a factor of about 2, and the reason is identified: pooling across reports conflates "some rounds go quiet" with "some experiments are quieter", which inflates the estimate by a measured 1.7202, and including simulated runs inflates it again because the shim is far more correlated than live seats at 0.681094 against 0.275298.

**This closes cc2's own first refutation.** cc2 named pooling contamination as the measurement that would undermine its K(n), and said that if the per-stratum correlation fell below about 0.1 its correction would under-correct. The within-experiment figure is 0.236014, which is above that threshold, so its K(n) is not badly under-corrected on this evidence.

**And it carries a consequence for simulation that nobody set out to find.** A simulated arm sits where the hazard nearly vanishes, with a 6-to-4 factor of 1.1280 against 1.7766 for a real run. A simulated arm therefore cannot rehearse this class of defect, and simulation will under-report it by construction.

## The timeout lesson, and it transfers to the runners

Tonight's round cost 30 minutes of a free seat for nothing. cc2's attempt 1 was killed at the 1800 s cap; its successful attempt 2 took **1594.6 s**, which is 88.6% of the cap that killed the first. A cap of 2426 s, the measured 95th percentile of observed seat work, would have covered that work with 33.2% headroom.

OBSERVED in the active runner, and the lesson applies there unchanged:

- `dispatch_to_model` in `bench/runner_core.py` sets the wall clock to `model_config.timeout * 2`. Both CLI seats are defined at 900 s, so the runner's effective cap is **1800 s — the identical number**.
- **Both CLI seats carry `max_retries=1`.** There is no second attempt in the runner. Tonight's answer arrived only on attempt 2, so the same work in a runner would have produced nothing at all.
- The measured 95th percentile of 2426 s and 99th of 3418 s both **exceed** the runner's 1800 s cap, so a measurable share of seat work fails outright there with no retry.
- API seats sit at 300 s doubled to **600 s**, which is below the 955 s fable took tonight. Whether API seats are fast enough for that cap is unmeasured, and should not be assumed.

**On whether partial output should be harvested, the founder's position is the correct one and it narrows the fix.** A full reply is always preferable, and extending the cap is the repair; a truncated reply is not a valid verdict, and the dispatcher already refuses one through `stalled_mid_stream`. The only legitimate use of a killed process's partial output is the RECORD — tonight 1800 s of work left 0 characters and no trace of what the seat had been doing, which is the retraceability requirement failing. It is a diagnostic, not a fallback answer, and not a second fix.

**The retry stays.** Tonight vindicates it: cc2 succeeded on attempt 2, and without a retry the round would have returned nothing.

## Status of each artefact

Both seats delivered files into their own sandbox trees with executed falsifiers; the harvest is preserved at `bench/logs/dynamic_roster_and_derived_ladder_2026-10-07/sandbox_harvest` (3,364,173 bytes) and mirrored to `experimental_notes/evidence/panel_records_2026-10-07/`, 123 of 123 rounds mirrored. 3 sandbox copies are kept rather than reaped.

- cc2's roster-aware quiescence — **WIRED into the live runner** by the seat, at 3 sites, with `live_by_round=None` reproducing today's behaviour exactly; 119 routing and gate tests plus 435 convergence tests pass. Its circuit breaker, capability ledger and roster registry are **DELIVERED BUT UNWIRED**, which the seat states plainly: wiring the breaker changes what every live experiment does on a dead seat, and that is the founder's ruling.
- fable's 6 fixes — **DELIVERED with falsifiers passing**, including edits flipping the no-cap default and updating 3 superseded 2026-09-24 assertions to the ruling; targeted suites 7 of 7 and 86 of 86 pass.
- Nothing from either seat is merged into the canonical tree. Both are proposals with evidence.

## What neither seat settled, and what the founder must rule on

1. **The endgame one-sidedness** at `reference_runner_v3.py:9207-9215`. A code path that makes gamma reported-not-gated is an automatic demotion, and the standing directive forbids demoting gamma. Neither seat proposed changing it; both only named it.
2. **The absolute 0.1159 full-roster false-quiet rate.** No roster-aware fix touches it. Raising the global K or adding seats are the only levers identified, and both cost the researcher.
3. **Flipping the cap default to exhaust**, which changes what 23 routing-enabled configs dispatch.
4. **The degraded-convergence policy** — converge, declared, on a raised window — which both seats recommend and neither can authorise.
5. **Whether the runner's caps and retry budget are reset from the measured distribution**, which is the lesson tonight paid 30 minutes to learn.

Written under CDSFL note standard v1.7 (26 August 2026).
