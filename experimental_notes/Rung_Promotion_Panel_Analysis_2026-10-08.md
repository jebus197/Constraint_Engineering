# Earned rungs and opaque identifiers: what the panel actually settled, and the one thing it did not

2026-10-08 11:12 BST

## Summary: the design survives, 3 disagreements are preserved, and a re-run was asked for twice and never dispatched

The 3rd panel round of this arc put the founder's rung-promotion design and his opaque-identifier proposal to 2 free seats, blind, 0 paid. Both returned **sound with repairs** on all 3 pillars — earned rungs, opaque identifiers, measured difficulty. This note is the analysis he asked for under `d` and did not receive at the time; the delay is itself recorded below, because an instructed item that lapses is a defect of the same standing as a stale document.

The round's most useful output is not the agreement. It is **3 disagreements that were preserved rather than resolved**, and a correction to the brief's own framing that one seat made which inverts the criticism the brief was built on.

## What both seats agreed on, independently

**The missing third seat state is a circuit breaker.** Both named it without coordination, as closed, open and half-open, and both found the term is already this project's own vocabulary: `experimental_notes/CDSFL_UX_Vision_Sketch_2026-03-28.md` specifies a "Circuit Breaker Display" and already offers the option to proceed without the failed model. The distinction from permanent benching is made structurally rather than by documentation — one seat's module cannot construct an open state without a re-probe deadline, and caps the backoff, so an unbounded re-probe interval, which is benching under another name, is inexpressible.

**A degraded run should converge, but never silently.** Both raise the quiet-round requirement as the roster shrinks rather than leaving it fixed. One derives a required run of 3, 4, 4, 5, 6 and 9 rounds as the roster falls from 6 seats to 1; the other conserves seat-rounds. Both label the outcome, and both hold that a round with 0 live seats must not converge, because that is no evidence at all. Both confirmed a full roster behaves exactly as it does today.

**Keep the hand-written ordering tuple as the cold-start tie-break.** Both refuted replacing it, and the reason is arithmetic rather than preference: on the first run every seat's lower confidence bound is exactly 0.0, so the derived key is a total tie and carries no ordering. One measured it — 12 shuffled inputs produced 12 distinct orders without the tuple and 1 with it.

**Holding an expensive model in reserve needs no classifier.** It is emergent from the key: an expensive seat has a large cost term, so the ordering places it late by construction and it is reached only on findings where every seat with more confirmations per unit cost already failed. One measured it dispatched on 3.61% of findings; the other computed a reach probability of 0.0287 in its worked example. Both noted the corollary — when the rest of the roster measures near-useless the key promotes the expensive seat instead of wasting the researcher's wait, which is the requirement working rather than a fault.

**Adding a model is one edit.** Both verified that `rank_falsifier_writers` already appends unranked models after the ranked ones, so the tuple is a priority prefix and not an allowlist. One ran the ranker on a roster containing an invented model name and got it back ordered last rather than dropped.

## The 3 disagreements, preserved as information

**1. Is a single scalar cost sufficient?** One seat says no, and constructed an instance whose budget-constrained optimum is optimal for no latency weight across 4001 tested values, concluding that a hard-capped resource such as a subscription limit needs a constraint rather than a weight. The other says yes, and proved with z3 that the exchange rule survives any fixed non-negative linear combination of money and waiting, adding that a vector introduces a dimension a one-scalar-per-seat sort key cannot consume.

Both results are correct because they answer different questions. The first is about FEASIBILITY, where no weight can express that a seat has become unavailable. The second is about ORDER, where any linear cost preserves optimality. The synthesis is a scalar for the order and a separate constraint for the cap, which is the shape Astra's section 6.5 already uses, where a missing tool or authority is a hard exclusion rather than a low rank. **Neither seat is overruled here; the composition is the finding.**

**2. Which way is recorded depth censored?** One seat finds `rungs_tried` RIGHT-censored by the cap: a finding of true depth 4 reports 2 under a cap of 2, indistinguishable from one genuinely resolved at rung 2. The other finds it LEFT-censored by strongest-first ordering: every finding the top model can handle reports 1, so the label discriminates only above the strongest rung's ceiling — 1 of 7 findings in the Exp 42 set — and weakest-first recovers the full ranking at 10 extra dispatches per 5 findings.

**Both mechanisms are real and they compose into something neither seat stated.** Difficulty cannot be measured without BOTH removing the cap and varying the order. And that re-creates the original try-order tension in a new place: strongest-first resolves efficiently while weakest-first measures difficulty, so the schema cannot optimise both from one ordering any more than it could optimise coverage and spend from one key.

**3. What is the promotion sample?** 3 derivations give 3 answers — 19 attempts per rung with 11 successes, 19 with 14 at a floor of 0.50, and 12 with 8 at an implied floor near 0.39. Each verifies minimality under its own stated error budget, so **the difference is the target specification, not the arithmetic**, and the targets are the founder's to set. All 3 assume independent attempts, and this project's measured intra-round correlation inflates 19 independent-equivalent attempts to about 30 actual ones, so every figure is a floor.

## The correction that inverts the brief's own criticism

The brief's quantitative case against promote-on-one-success — that it keeps a genuinely capable model out 40.951% of the time — **holds only under an absorbing reading the founder never stated.** One seat identified this directly: his phrase "stay on the same simpler problem resolution rung" naturally means the model keeps receiving that rung's work, and under that reading every model with any non-zero success rate reaches the top eventually, with expected attempts R divided by p. So the rule's defect is the opposite of the one alleged — it excludes nothing.

Both framings are wrong for the same reason, and the founder's own answer resolves it. Capability sets the RATE of climb, not whether a climb is possible: 5.56 expected attempts at a 0.90 per-rung success rate against 50.00 at 0.10, a 9-fold difference. Under a bounded horizon that rate IS the selection, with no absorbing rule, no exclusion and no threshold: at 10 attempts per rung a 0.90 model reaches the top 0.9998 of the time and a 0.10 model 0.0016, a factor of 625. That is his football pyramid exactly — nothing bars a Conference side from the Premier League, and almost none arrive.

## What the identifier proposal fixes, and the one place it needs amending

His proposal fixes a live fault rather than a preference. **There is currently no unique stable identifier for a model in this project.** `model_id` carries a vendor version in 9 of its 12 occurrences, so it is not stable across a release, and it SPLITS: 4 models are carried under 2 strings each, so a string-keyed capability record divides one model's evidence in two. One seat corrected the brief's stated mechanism here — the brief said "collides", which came from matching the suffix and so catching the secondary field as well; separated properly there is no collision, and the real defect is the opposite. **The conclusion stands and the stated reason did not.**

**Both seats reject RANDOM assignment in favour of a digest over the output-affecting configuration**, which contradicts his wording while serving his intent. One measured the cost: 2 instances of 1 configuration under split records need 21 rounds to separate 0.8 from 0.4 where pooling needs 11, so random keys double the cold-start price for no benefit. A random identifier cannot recognise the same configuration twice; one derived from provider, model version, temperature, top-p, max tokens, system prompt, tool set and quantisation can. Random tokens survive only as an instance identifier for dispatch bookkeeping.

**And a new vendor release takes a new identifier at 0 attempts**, by construction, because the version is part of the key. The cost is the cold-start price paid again; what is lost is nothing, because the old record stays valid for the old configuration and is retired rather than destroyed. Inheriting instead would route hard findings on a stale high bound — a bounded cost against an unbounded consequence.

## The answer to his cold-start question that is better than the author's

He asked how a model starting with zero credit can ever climb. One seat gave the reason the brief missed: **a new model placed at the back of the order sees only findings every stronger model has already failed** — a maximally hard, biased sample — so its free measurements are near-pure failures and cannot demonstrate capability. Rungs exist to hand it EASY attempts, and per-rung stratification stops back-of-order failures poisoning its easy-rung record. That is a better answer than rotation alone, which the author had offered.

## The instructed item that lapsed

He asked twice for this round to be **re-run with his fresh framing** — the clarification that promotion needs several tries on different problems, the football analogy with its finite and bounded divisions, the derived sample, the author's withdrawals, and the seats' own corrections. It was never dispatched. It was displaced by the gamma repair he also authorised, and the displacement was not flagged at the time, which is the failure rather than the delay.

**Whether it is still worth running is a real question and the answer is partly.** Three of the items in that framing have since been settled by other means: the promotion-sample question was independently derived by both seats under a different brief, the absorbing-versus-retry reading was resolved by the rate-and-horizon measurement above, and the identifier question was answered by both seats converging on a derived key. **What no seat has seen** is the finite-divisions insight and its consequence: that the tier count is bounded and small, that the cost of climbing is therefore bounded between 52 and 182 attempts across 2 to 14 tiers, and that the cost curve is NOT monotone — 7 tiers cost 91 attempts where 5 cost 95, and 10 cost the same as 8 — so the tier count must be scanned rather than reasoned to. His own four-division instinct lands on a local optimum at 68 attempts.

That is a narrow, well-posed question rather than a re-run of the whole brief, and it is the form the re-run should take if he wants it.

## What this leaves for his ruling

The promotion-gate targets, which fix the sample size and are his to set. How many tiers the ladder should have, which is bounded, non-monotone and must be scanned. Whether the convergence gate should READ the live roster or merely record it — recording lets a researcher detect a short-roster convergence afterwards, while reading it prevents one, and both seats proposed the second where his framing was the first. And whether the narrow re-run above is worth dispatching.

Written under CDSFL note standard v1.7 (26 August 2026).
