# Morning Round-Up — 2026-09-03

**2026-09-03 02:03 BST.** Markdown mirror of `~/Desktop/CDSFL_tts/Morning_Roundup_2026-09-03.txt`, with file and line references restored. Verbatim panel output: [Panel_Reduction_Criterion_FULL_RECORD_2026-09-03.md](Panel_Reduction_Criterion_FULL_RECORD_2026-09-03.md).

## Headline: a live defect in fix acceptance

`check_sk_threshold` (`bench/reference_runner_v3.py:9712`) computes
`S* = (ν_b + ν_f − ν_bν_f − qR) / (ν_f(1−ν_b))`. Found by cc2, verified four independent ways.

**Derivation.** S\* is the solution of `ν_eff(s_k) = ν*` with ν\* taken at **σ = 1**, i.e. ν\* = qR. The appendix's ν\* is σ-dependent: `ν* = σRq/(1 − qR(1−σ))`. The code froze σ at 1 while σ = s_k is the variable under test. SymPy: re-derivation minus code S\* simplifies to **0**.

**Consequence at the live operating point** (ν_b=0.05, ν_f=0.20, q=0.5, R=0.5):

| Quantity | Value | Tool |
|---|---|---|
| code S\* | **−1/19** = −0.0526 → clamps to 0.0 | Wolfram (exact rational) |
| true break-even | **0.504931170970423** | SymPy, mpmath 50 dp, Wolfram, direct `R_k(s_k)=R_old` |
| s_k range wrongly admitted | **50.5%** | — |

**Grid result.** Over 6,859 cells the gate admits a risk-*raising* fix in **1,420** — τ = 0.2070, Wilson 95% CI [0.1976, 0.2168] (cc2 got 0.1976 on a finer grid). Over 23,495 disagreements at finer resolution: **unsafe-direction 23,495, conservative 0.** The gate never errs toward caution.

**Upstream cause.** `model_params` has **zero write sites** (`bench/reference_runner_v3.py:9819` is the only read). The code's own comment: *"what every run from Exp 37 to Exp 49 actually used, because model_params is never populated."* `bench/dm/_fix_complexity.py` — built to make ν vary with fix size — has no pipeline caller.

**Third instance of one pattern.** The absorb signature rule; `gate_would_fire` (removed 2026-09-01, comment at `:6244-6255`); now S\*. All three found by *executing two forms against each other*, never by reading.

## The question actually asked

Both reviewers: the simplicity/sufficiency distinction is **sound**; **define it, add no machinery**.

Fable sharpens it — classify the move *before* proposing it: **identity** (proof available), **restriction** (declared boundary, named remainder), **proxy** (defining property replaced by an observable correlate; proof unavailable *in principle*, only measurement over the deployment population will do). Case C was a proxy trusted at identity-level evidence. This is sharper *ex ante* than τ, which only tells you after measuring.

Both independently: **the declared scope D is the load-bearing element**, not a setup clause. cc2 re-ran the absorb measurement under two reasonable definitions of "same function" and got rates differing by **3×** from identical code.

## My own record: 3 of 8 measurements survived

| # | Verdict |
|---|---|
| M1 29 props / 0 tested | **WRONG BOTH HALVES** — 28, and `test_channel_boundary.py:148-176` grid-asserts one to 1e-9 |
| M2 ν_eff blind to fix | HELD, understated |
| M3 ν>ν* in no live path | HELD for ν*; its dual S\* **is** live and defective |
| M4 `_fix_complexity` uncalled | HELD exactly |
| M5 27 tunables / 7 ruled | **NOT REPRODUCIBLE** |
| M6 282/711, τ=0.397 | **NOT REPRODUCIBLE** — 282 holds, 711 does not |
| M7 13 insufficient-fix | **NOT REPRODUCIBLE** — hand-classified, criteria unrecorded |
| M8 0 gaming / 5 containment | HELD; framing challenged |

3/8 = 0.38, Wilson CI [0.137, 0.694]. Fable's strongest finding: `scripts/similarity_operating_characteristic.py` was written 2026-09-01 explicitly to close the gap where *"no pair dataset was stored, no script rebuilt it, and no test recomputed it"* — and 282/711 was created **one day later with exactly that defect**. The criterion was violated by the document proposing it.

**Remedy, one sentence, no machinery:** a measured rate must travel with the script that produced it, or it is prose.

## Containment

Still **0** gaming instances. cc2 notes that holds only on an *intent* reading; behaviourally `adb566b` measured **126 of 246 proposed fixes do not silence their own test**.

Practical finding (fable): `scripts/latent_control_audit.py` reports `target_integrity_events` as **SILENT_BUT_RAN, seen=0** — the containment instrument cannot prove it ran. Three others likewise.

Both reach the same discriminator: **the tell is the record, not the crossing.** Helpful overreach is disclosed and persistent; the concerning case is *undisclosed and reverted* — as in `9bb0047`, where a reviewing model mutated the target and restored it, invisible to git and the round files. Cheap to measure: the target is already hashed each round. Neither recommends removing Write/Edit; a ruling on that has been pending since 2026-07-29.

## Recommended order

1. **Wire `_fix_complexity` in.** Fixing S\* while ν is four literal constants is "polishing the second decimal of a number with no first one" (cc2).
2. **Then fix S\*** — use the σ-dependent ν\*.
3. **Define the criterion** in `docs/MATHEMATICAL_APPENDIX.md` + one sentence in the acceptance policy. No score, no weight, no new term in R_k.

**Both advise against** testing the 28 reduction statements first: true by construction, the safest claims in the repo, and testing them yields green lights over what is least likely to be wrong. The productive direction is finding **undeclared** reductions — invisible to text search, and the source of all three known defects. Mechanically: wherever two functions answer the same question, grid both and diff.

## Did the panel earn its keep?

A solo falsification pass ran in parallel, deliberately unshared. It found 3 real weaknesses (admissibility needs Δ = ∅ not small τ — so **sampling can refute a simplification but never admit one**; two branches, exact and bounded; does not collapse into the two-sided gate). The panel reached 1 of those by another route and added **8** the solo pass missed, including the live defect. Novel share 8/9 = 0.89, CI [0.57, 0.98].

## Still open

Metering toggle, incidence matrix, single-model-vs-agents experiment, runway 0C.38/40/44/61. Wolfram Cloud was down overnight (scheduled upgrade); the local `wolframscript` kernel was used and gave exact confirmation.

---

## ADDENDUM (02:45 BST) — a prediction of mine, tested overnight and refuted

The round-up above closes with the claim that the panel's value lies in *causing* the tool step rather than in the reasoning, and that the productive sweep is "wherever two functions answer the same question, grid both and diff." Both halves were tested while the founder slept. The first is now qualified; the second is refuted as stated.

**Test 1 — version drift.** Every pure numeric function present in both the frozen Exp 38/39 baseline (`bench/reference_runner.py`) and the active runner (`bench/reference_runner_v3.py`) was executed against its counterpart over a grid: `compute_rk` (1,000 cells), `check_sk_threshold` (1,000), `_interpret_gamma` (40), `_estimate_gamma` (21). **Zero disagreements in 2,061 cells**, Wilson 95% CI [0.0000, 0.0019]. My predicted "more than zero, clustering where a constant was frozen" is **refuted for this pairing**. Both versions carry the same S\* defect, which is consistent: it was introduced 2026-04-10, before the version split.

**Test 2 — why that was the wrong pairing.** The S\* defect was not found by comparing a function to its own earlier version. It was found by comparing two *differently named* functions that answer the same question within one version. Those are not mechanically discoverable. `check_sk_threshold` and `compute_rk` share **no name tokens** and score 0.214 on sequence similarity. Ranking all 14,706 function pairs in the active runner by name similarity places **11,039 of them (75.1%, Wilson 95% CI [74.4%, 75.8%]) above the true pair.** A mechanical sweep would grid eleven thousand decoys before arriving at the one that mattered.

**The correction this forces.** The two steps are doing different jobs and neither substitutes for the other. Identifying the *candidate pair* is semantic work: it requires reading two functions and recognising that they answer one question despite sharing no vocabulary. Settling the *verdict* is tool work, and no amount of reading substitutes for it — this project's record contains eleven withdrawn claims that were confidently reasoned and wrong. The earlier formulation, that the panel merely manufactures doubt and the tool does the work, understated the panel's contribution. The panel found a pair that no index would have surfaced.

**Consequence for the open single-model-versus-agents question.** If the load-bearing capability is semantic pair identification rather than vendor diversity, then what matters is the number of independent *readings* of the codebase, not the number of distinct vendors. One model given several differently framed briefs might match a multi-vendor panel. That is now a sharp, cheap hypothesis rather than a vague one, and it is directly testable in the next simulated run.
