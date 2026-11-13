# Standards currency and model-version staleness — a 2-round free panel review

**Recorded 2026-11-13 · Constraint Engineering (CDSFL) · star topology, blind round then joint round · 2 seats, both on the Max subscription at 0 marginal cost**

## The question

The founder asked how an expert encoding keeps its externally-defined standards current, given that a severity scale such as GHS health hazard category or CTCAE grade is published by an outside body on its own revision schedule. His proposal: a classifier model performs an online check when an encoding is loaded and updates the encoding dynamically before loading it, as part of a boot-time health check, at a cadence of 1 month. He then reopened it in sharper form — how is the encoding kept current if it *cannot* be updated dynamically, and can it be after all?

A second question ran alongside: model names and version numbers in the harness go stale, so could a model name/version check be integrated with the existing seat aliveness check?

## Method and round statistics

| round | brief | seat | chars | tool calls | elapsed |
|---|---:|---|---:|---:|---:|
| blind | 14,619 chars, validator-clean (0 shape, 0 figure) | cc2 | 28,405 | 48 | 1,077.3 s |
| blind | — | fable | 16,074 | 32 | 1,014.8 s |
| joint | 59,796 chars, both blind replies verbatim | cc2 | 31,842 | 69 | 1,766.3 s |
| joint | — | fable | 17,915 | 56 | 1,738.2 s |

The joint round completed inside its 1,800 s ceiling with 8.1 s total idle across both seats. No paid seat was dispatched.

## What the panel refuted in the orchestrator's own work

3 claims fell in the blind round, each found by both seats independently, and each then **confirmed programmatically** rather than accepted on the seats' agreement — concurrence between 2 models is not a confirmation route in this project.

### 1. The exposure formula was a leading term, not the quantity

The orchestrator computed the fraction of runs executed under a superseded standard as `λ × E[window]`, which **sums** the stale windows of every revision in a check interval. Two revisions in one interval leave the standard stale *once*. The correct object is the union:

```
E[stale length] = ∫₀ᵀ (1 − e^{−λt}) dt   →   exact = 1 − (1 − e^{−λT})/(λT)
```

Overstatement of the first-order form: **1.37 %** at T=30, **8.38 %** at T=180, **17.32 %** at T=365.

### 2. The orchestrator's own cross-check had been rejecting its own formula

Re-run over 12 independent seeds, the Monte Carlo sits **−1.13σ and −0.90σ** from the exact law and **−3.33σ and −28.65σ** from the first-order one. A single seed under a typed relative tolerance of `0.12` concealed it — and 0.12 is wider than the form's own truncation error of 0.0838.

### 3. The failure-mode count was not a dominance measurement

Coverage of a composition is the union of the parts' coverage, so the composed figure can **never** come out lower than the better part: 2 checks covering 15 of 30 and 18 of 30 domain configs compose to at least 18 of 30, never 14. An instrument that cannot return the answer it was built to test is a rubric wearing a number. A 2nd seat broke it independently by re-partitioning the same coverage and reversing the ranking. What survives is strict set inclusion (partition-invariant) plus a genuine ratio-scale property: provenance alone leaves detection latency unbounded; a detect-only check bounds it at an expected `T/2`.

## The sharpest finding — concessions written as prose, not code

Both seats, independently, re-executed the corrections the joint brief reported and found 3 had not landed.

- The brief stated the cross-check tolerance *"is now derived from the simulation's own sampling error."* On the dispatched bytes it was not: `assert err < 0.12` still ran against the **first-order** form on a **single** seed, printing `agree on 4 of 4`. The derived tolerance lived in a docstring with no caller.
- `exposure_ceiling_cadence` had **no caller inside the producer** — an addition nothing reached, inside the producer written to correct that shape.
- The guard was **red on the dispatched tree**, so the mutation harness refused its baseline. The brief's "5 of 5 red" was **0 of 5** there.

> *In a project whose founding principle is that tools decide, a concession paragraph is not a correction — the re-run is.*

## The answer

**Pin, record, check out of band, mutate only through the human.** The encoding pins the standard `(name, version)`; every run records the pin; a scheduled out-of-band check compares pin to upstream and opens a ticket; only the human merges. The boot path reads a local pin and touches no network, so the "slow experiments down" concern dissolves and no progress indicator is needed in the startup sequence.

**The orchestrator's stated reason was wrong and 1 seat corrected it.** The claim was that the check's *position* does not appear in the exposure quantity. It does, through the effective cadence. Measured at the observed run rate (65 runs / 104 days): boot-time check → worst-case exposure **0.001094**; daily out-of-band check → **0.000684**. The conclusion survives on a stronger footing — a daily scheduled check **strictly dominates** a boot-time check at any run rate below 1 per day. A measurement, not an algebraic cancellation.

## Can anything be applied dynamically? Yes — but not as first drawn

The proposed boundary (auto-apply when the name or citation year changes while the ordinal scale and critical cut stay bit-identical) is **unsound**, and both seats showed why.

The check compares the encoding against *itself*; the claim needing verification is the encoding against the **external document**. `bench/cdsfl_registry/domain_vocabulary.py` records for chemistry that the numeric LD50/LC50 cutoffs *"were not retrieved and are deliberately not stated here."* The tuple binds **labels**; the definitions live only in the cited revision. A revision moving a toxicity boundary while keeping the label set leaves the tuple bit-identical — so the gate auto-applies it and silently rebinds `Category 2` to different substances.

**The citation year is not the non-semantic part. It is the only semantic pointer the encoding holds.**

The converse is in the record: the software domain's note states the CVSS v3.1 → v4.0 update was safe because *"first.org's own Table 22 was read directly for the bands. THE BANDS ARE UNCHANGED."* The project's 1 executed safe relabel was decided by reading source text.

**Sound repair — clause-digest pinning.** Extend the pin to `(name, version, sha256 of the clauses defining the levels and the cut)`. A version bump whose defining-clause digest is unchanged is then mechanically provably a pure relabel and may auto-apply. Everything else is held at mutation. The class is empty today; the digest makes it non-empty.

A 2nd seat reached the same verdict by execution: a relabel passing the proposed check changed **6 of 67** decisions and made every archived stamp compare unequal. It also found the 2 repairs **interfere** — provenance stamps the scale name; the relabel boundary licenses a machine to change it. The single repair is preferred: **provenance without the dynamic relabel.** Under the founder's composability standard this is a result running *against* composing, which is the case that standard exists to catch.

## Model identity

| finding | evidence |
|---|---|
| Fable 5.2 is real | upstream refusal names its own minimum client, **2.1.290** |
| the dispatch pins no version | seat table lifted by AST: `free_seats_pinning_a_version = 0` |
| a runner's label was already wrong | labels the seat `Fable 5.1`, which the path client (**2.1.220**) cannot serve |
| the newer client is already installed | desktop app bundles **2.1.309** and **2.1.317** |
| through 2.1.317 the gate does not refuse | `claude-fable-5-1` returns rc=0; `claude-fable-5-2` not refused, **timed out at 150 s — UNVERIFIED** |

`_find_claude_cli()` in `bench/experiment_11_orchestrator.py:32` holds 4 faults in 18 lines, 3 masked by the first:

1. `shutil.which` returns at line 36, so the bundle branch is unreachable.
2. The bundle glob is 1 directory level short — **0** matches where a corrected pattern matches **2**.
3. `sorted(..., reverse=True)` is lexicographic under a *newest version first* comment: 2.1.90 beats 2.1.317.
4. Duplicated in `bench/cc2_manager.py:96`; the 2 copies already differ by md5.

**The repair is a single one.** Read the identity from the **transport**, never from the model — asking a model its own name is a model vote on its identity. The streaming output format already in force on every free-seat call already carries `modelUsage` / `canonicalModel`, and the log sink records the alias requested while discarding the identifier served. Reading it costs no call, no network, no dispatch, and closes the time-of-check/time-of-use gap because the identifier arrives in the same bytes as the reply.

## The 6 disagreements, settled

| # | subject | resolution |
|---|---|---|
| D1 | deriving a size bound from the record | the bound **ratchets** — binds on growth ratio, never on size (admitted sizes reached 2.45e12 with 0 refusals). Seats differ on the repair and **both constraints hold**: the direction must be monotone non-increasing or typed; and the quantity must not be downstream of the bound |
| D2 | does the preferences question belong? | **No** — the founder's framing exempts preferences by name |
| D3 | size of the severity archive | **3,094** (de-duplicated run population). 809 counted a transport format; a 4th population of 10,549 live-checkpoint records was found in the joint round. Union: **0 of 14,452** carry any scale key, Wilson [0, 0.00026574] |
| D4 | the archive-epoch figure | refuted and confirmed by a 2nd route incl. Wolfram. Refined: 4 versions after 3 checks needs ≥1 revision in *each* interval, P = **4.574e-4** (~1 in 2,200). Caveat: GHS is exactly biennial (variance 0), so `E[N] = 1.277957` is model-free while the tail is not |
| D5 | identity from the transport | reproduces on this machine, naming `canonicalModel` and `provider` |
| D6 | time-of-check/time-of-use gap | real; cheapest closure costs 0 dispatches |

## What was repaired and proven

- Cross-check **anchored to the exact law** over 12 seeds at a tolerance in units of the simulation's own standard error: accepts the exact form at **−1.15σ**, rejects the first-order one at **−9.93σ** at the same cell, with a guard asserting the simulation must *prefer* the exact law. Figures reproduce a seat's independently to the digit.
- `exposure_ceiling_cadence` **wired**; exact ceilings reported beside the retained first-order ones for all 4 standards.
- The figure contract is now **three-way** — `CURRENT` / `SUPERSEDED` / `WITHDRAWN`. It immediately caught a 4th defect neither seat flagged: `share_version_bearing` had moved 0.253054 → 0.282700 silently. Getting the classification order wrong reproduced a separate defect inside the guard, because a retraction line quotes the figure it retracts.
- Guard holds **8 contracts**; mutation harness reports **11 of 11 red**, restore byte-verified, baseline green afterwards.
- A population defect recurred **4 times in one night**, each time detected by the figure moving: the measured population must exclude the instrument, the instrument's guard, and every directory of archived evidence. `experimental_notes/seat_evidence/` alone held **359** files from **63** earlier rounds, all inside the measured population.

## Awaiting a human decision

1. Adopt **clause-digest pinning** as the admissibility test in place of tuple comparison?
2. Confirm **provenance without the dynamic relabel**, since the 2 interfere?
3. Authorise stamping each severity record with `(scale_name, standard_version, critical_level)` — **269 sites across 139 files**, measured storage overhead **3.0 %** (208 bytes against a 6,924-byte mean entry)?
4. Shorten the persistent memory index or raise its limit — **91 characters** of headroom, **0 of 95** current pointers archivable by date?

**No proposed repair has been merged.** Both seats' delivered code is preserved as proposals under `experimental_notes/seat_evidence/standards_currency_2026-11-13/`, with the full diff at `bench/logs/standards_currency_2026-11-13/seat_proposals.diff`. A proposed repair goes to the human and is never auto-applied.

---

*Producer for every figure above: `scripts/standards_currency_and_model_staleness_2026-11-13.py`. Guard: `bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py`. Mutation harness: `scripts/the_standards_currency_mutations_2026-11-13.py`. Spoken companion: `~/Desktop/CDSFL_tts/Standards_Currency_Panel_2026-11-13.txt`.*

*Written under CDSFL note standard v1.9.*
