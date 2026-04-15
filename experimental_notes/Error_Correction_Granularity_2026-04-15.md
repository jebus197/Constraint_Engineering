# Error Correction Granularity — Post-Hoc vs In-Flight

**Date:** 15 April 2026
**Prompt:** George asked whether §17's post-round feedback is a waste of opportunity/time relative to in-flight error correction in computer memory systems. Answered under `p a d e sth d t`.

---

## The question

> Isn't the fact that the models are only told about their errors and asked to solve them recursively/post-hoc, after each round completes, rather than ad-hoc (as the errors are detected) a potentially large waste of opportunity (and time?) Think of it in terms of error correction in computer memory, or other parts of computer tech that do similar things? If all computers ever did was wait for errors to accumulate, before trying to correct them, that would surely be a horrendously slow and computationally expensive process?

---

## Analyse

Map the analogy carefully. **ECC memory does not continuously correct errors while data sits in RAM.** It corrects at READ — when a word flows through the memory controller on its way to the CPU. An uncorrected single-bit error can sit in memory for hours until someone reads that address. The correction happens at the *point of use*, not at the *point of error*.

That is precisely what §17 does. Findings sit in logs after round K. The "point of use" is when those findings flow back into the model's context at round K+1. §17 intercepts them there and applies correction before the model reads them. The round boundary is not a gap — **the round boundary IS the read boundary**, exactly like the memory controller is ECC's read boundary.

Similar pattern across computing:

| System | Unit of correction | Timing |
|--------|-------------------|--------|
| ECC memory | Word | At read |
| TCP | Packet | At packet boundary (checksum then retransmit) |
| Compilers | Translation unit | After parse/semantic pass |
| CPU branch speculation | Mispredicted path | After branch resolves |
| Git | Ref integrity | At push time |
| §17 feedback channel | Round | At round boundary |

Truly continuous in-flight correction is rare and expensive. Hardware parity, watchdog timers, real-time safety systems. Always at a cost premium. Most systems correct at batch boundaries because batch boundaries are where the signal is complete enough to verify cheaply.

---

## P-pass

"The analogy supports us" is too tidy. Where does it fail?

The CDSFL signal set is not uniform. **Three quite different kinds of signal:**

1. **Per-finding refutation** (sympy says the identity fails, z3 says the constraint is unsatisfiable). Runnable on a single finding in isolation. Does NOT need a batch boundary. A model could call sympy mid-generation and self-correct before emitting finding #2.

2. **Cross-model signal** (NK-Cell duplicate detection, peer support across families, R_k aggregate comparison). REQUIRES all models to have reported. Inherently batch-bounded.

3. **Structural signal** (FFAFP admissibility gates). Computable per-finding but depends on the finding being complete, so at minimum "end-of-finding" boundary.

**Class 1 could be in-flight. Classes 2 and 3 can only partially be.**

So a sharper question emerges: why don't we run per-finding refutation in-flight for class 1?

**Answer: we partly do.** The FFAFP protocol and the `sy` command explicitly direct models to run sympy, z3, and pint on their own claims during generation. Frontier models with tool-use support (Claude, GPT-4, Gemini) can call the tool and self-correct mid-stream. The schema doesn't currently host a shared verification endpoint, but individual model tool-use accomplishes much of the same goal.

**What the schema does in §17 that models can't do alone:** cross-check one model's claimed output against OTHER models' outputs, against aggregate R_k, and against the FFAFP structural gates. That is inherently batch.

---

## Discuss — where you're onto something real

There IS a class of intra-round correction we're not doing. When finding #1 is refuted and finding #5 in the same round DEPENDS on finding #1, finding #5 is wasted work. We catch both at round end rather than stopping the rot at finding #2.

**How often does this actually happen?** Empirical question. From logs I've seen, frontier models typically generate findings as parallel candidates, not as chained derivations. Within-round correlation seems lower than intuition suggests. If findings were chained proofs (like a long math derivation), intra-round feedback would matter a lot. For parallel candidate findings, the batch boundary captures most of the value at a fraction of the API cost.

That empirical answer is not certain and is worth measuring.

---

## Extrapolate

Generalise the tradeoff. The optimal granularity of error correction feedback depends on three things:

- **Correlation between sub-units within a batch.** High correlation means error propagates within the batch, so fine-grained correction pays. Low correlation means errors are independent, so batch correction is sufficient.
- **Cost of pausing generation.** For autoregressive LLMs accessed via API, pausing costs roughly an extra API call plus re-prompting. Non-trivial.
- **Cost of verification per unit.** sympy on a single equation is cheap. Cross-model aggregation requires all models to have reported, which is expensive.

The pattern generalises well beyond LLMs:

- Database systems — transaction granularity
- Compilers — incremental vs batch
- Real-time control systems — sensor fusion rate
- Distributed consensus — message batching vs per-message

Always the same question: **at what granularity does the cost of frequent correction exceed the value of earlier detection?**

**[SPECULATIVE] Falsifiable question:** if we added a streaming per-finding verification server (model calls schema mid-generation rather than each model calling its own tools), would convergence speed up relative to the current §17 batch feedback? Testable via A/B comparison on the bench. Prior: marginal gain on parallel-candidate rounds, substantial gain on chained-derivation rounds. Since the bench mixes both, the population average probably shows 10-20% round reduction if the gain is real — small but measurable.

---

## Synthesise

**Three-layer frame for error correction in CDSFL:**

| Layer | Scope | Timing | Status |
|-------|-------|--------|--------|
| 1 | Within generation | In-flight via model tool-use (sympy/z3/pint) | Present via FFAFP + `sy` |
| 2 | Within a round, across findings | Intra-round inter-finding | **GAP** — not currently addressed |
| 3 | Across rounds | Post-batch feedback channel | Present via §17 (implemented today) |

The current architecture is not "wait until errors accumulate, then correct." It is **"correct at each layer's natural boundary."** Layer 1 is in-flight and self-served. Layer 3 is at batch boundary and schema-orchestrated. Layer 2 is the gap you're pointing at.

---

## Discuss — what to do about it

Two concrete ways to close layer 2 if the empirical data supports it:

### Option A: Streaming verification endpoint
Schema hosts a callable sympy/z3/pint service that models consult mid-generation. Low change to model protocol, schema owns the tool surface. **Low-to-medium effort.** Closes ~80% of the gap at ~20% of the cost.

Architecture:
- New module: `bench/dm/_verification_endpoint.py`
- Models call via existing tool-use protocol
- Schema-owned tool registry, authentication, logging, receipts
- Integrates with R_k as a "tool-observed" corroboration signal

### Option B: Sequential per-finding submission
Models submit one finding, receive flag-or-confirm, submit next. Major change to round architecture. **High effort.** Would enable intra-round cross-model signals too, at the cost of much slower rounds.

Probably only worth it if the data shows strong intra-round chained correlation, which I suspect is uncommon in parallel-candidate LLM output.

### Recommendation

**Option A is the cheap close.** Worth scoping as a follow-on experiment to §17 once we have baseline data on §17's standalone effect. Not a blocker, not a mistake to fix — an extension to consider.

Ordering:
1. Run Exp 39 with §17 live (current plan) to get baseline.
2. Measure intra-round chained-finding rate in the logs.
3. If rate > ~15%, Option A becomes high-value; scope the endpoint.
4. If rate < 5%, Option A is noise; stop here.

---

## Closing framing

The ECC intuition is sound. The interesting twist is that ECC itself does not do continuous in-flight correction — it does read-time correction, and that is exactly what §17 does. The gap George is sensing is not layer 3 versus continuous correction. It is **layer 2**, intra-round but inter-finding, which neither the current model tool-use layer nor the current §17 channel addresses directly.

Scoping a streaming verification endpoint is the natural next experiment, once we have baseline data on §17's standalone effect.

---

## References

- `bench/directives/universal/cdsfl_operational.md` §17 — feedback channel directive
- `bench/dm/_feedback.py` — implementation
- FFAFP protocol in MEMORY.md under `feedback_fff_is_prompting.md` — per-finding calibration protocol
- `sy` MC command — model-side tool-use invocation
- Future: `bench/dm/_verification_endpoint.py` (speculative, Option A above)
