# The Wolfram Rule Was Inverted In Prose, The Drift Detector Cannot Fire, And The Explorer Now Separates A From M

**2026-09-29, 10:31 BST.** Audience: a reproducing engineer. The plain-English companion for a non-coding reader is `~/Desktop/CDSFL_tts/Wolfram_Correction_And_Drift_Detector_2026-09-29.txt`.

---

## 1. The Wolfram denial rule never existed, and the code always knew it

The founder's correction, verbatim: *"There is no 'denial rule' for Wolfram. That is clearly an invention by you in what probably seemed like a 'safe default'. But it is actually opposite to what I recently said. What I actually said is that where seats can use Wolfram (in its recently revised 'best of both' configuration preferably), then they should use it (as their secondary cross verification falsifier), where they cannot, then they should default to equivalent Open Source tools."*

**Six facts, obtained by executing the module rather than reading its docstrings** (`execute-do-not-grep`; a module that describes itself consistently proves nothing about what it does):

| what was checked | result |
|---|---|
| `wolfram_standard.DEFAULT_POLICY` | `serial` |
| `wolfram_standard.policy()` live | `serial` |
| `wolfram_standard.claude_cli_args()` | `('--strict-mcp-config',)` — **no** `--disallowedTools` |
| `wolfram_standard.gate_dir().name` | `serial` |
| `seat_environment(seat="cc2")["PATH"][0]` | the serial gate directory |
| `CDSFL_WOLFRAM_POLICY=deny` anywhere in the repo | **0 occurrences** outside the variable's own definition |

`bench/wolfram_standard.py:95` carries the comment *"the default the founder ruled for on 2026-09-17"*. `PANEL_CLAUSE` resolves to `SERIAL_CLAUSE`, which opens *"TOOLS, AND WOLFRAM AMONG THEM (founder, standing, 2026-09-17). You are not exempt from using tools."* The real binary is installed at `/usr/local/bin/wolframscript`; the gate carries its shim. **Wolfram has been enabled for every command-line seat since the ruling and still is.**

### 1.1 The provenance is worse than "a panel said so"

The denial began as **CC1's own recommendation**, in `experimental_notes/Awaiting_Your_Decision_2026-09-17.md` item (d): *"Recommendation: keep it denied until Wolfram answers A5."* The founder answered *"So fully enable it"* and the code changed within hours. **The prose did not.** Item (e) of the same file recommended treating dispatched agents as automated; that was overruled in the same breath — *"Agents are not exempt from using tools. That is the whole point of this project."*

On 2026-09-21 a panel seat independently restated denial (`Panel_FULL_RECORD_Final_Review_2026-09-21.md:1070`), recorded as *"denial stands. Unanimous"* — giving a rejected recommendation the appearance of external confirmation. It then propagated to `Programme_of_Study_Full_Scope_2026-09-21.md:71,86`, `Morning_Report_2026-09-22.md:328`, `Morning_Report_2026-09-29.md:101`, and finally `CDSFL_Agent_Operational_Plan.md:11,26`, where it acquired the founder's name: *"that rule has been in force since he set it."*

**Two standing rules exist for this and neither fired.** `feedback_no_model_voting` (a panel opinion cannot become a rule) and `feedback_check_the_record_before_declaring_a_gap` (the refutation was in the record throughout). A rejected recommendation that survives in prose and then acquires the founder's name is unfalsifiable by anyone who trusts the document, and would have been *implemented* by anyone making the code match the docs.

### 1.2 What was changed

Seven documents carry dated corrections placed **beside** the original wording, not replacing it, because a statement that was true when written and was overtaken by a ruling should show both states: `CDSFL_Agent_Operational_Plan.md` (full retraction block), both copies of `Programme_of_Study_Full_Scope_2026-09-21.md`, `Morning_Report_2026-09-22.md`, `Morning_Report_2026-09-29.md`, `Programme_Of_Study_2026-09-17.md` §10, `Awaiting_Your_Decision_2026-09-17.md` items (d) and (e). **Panel transcripts and `evidence/` JSON were left untouched** — rewriting a transcript destroys the record it exists to preserve (task 7.1's ruling).

`bench/tests/test_wolfram_is_enabled_not_denied_2026-09-29.py`, 11 tests in two halves. The first **calls** the policy layer. The second scans every live `.md` under `experimental_notes/` and `docs/` and fails on a denial sentence with no retraction within its paragraph, exempting transcripts by path. Mutation-tested: flipping `DEFAULT_POLICY` to `deny` fails 5; appending one denial sentence to the tracker fails 1; baseline green.

### 1.3 The one real gap is capability, not policy — and it needs no ruling

**Measured 2026-09-29:** a headless `claude -p` seat reports **0** MCP tools matching `olfram`, **with or without** `--strict-mcp-config`. The flag is therefore *not* what removes the connector; it was never in the headless CLI's server list. The flag is load-bearing for confinement (*"none of the models... should ever be able to reach the real repo"*) and stays.

The founder's *"best of both"* is his own two-environment directive: the cloud connector for semantic queries, real-time lookup and **verifying mathematical correctness**; the local Engine for execution. CC1 has both and used both this session. **CLI seats have the local Engine only. API seats (`cx`, `ge`, `cgpt`, `ds`) receive JSON tool specs and no shell, so his fallback clause governs them — they use SymPy and z3 and already comply.**

**No question is put to the founder.** An earlier draft offered building the API seats a `wolfram_verify` tool. It is withdrawn unasked, under his ruling of 2026-09-28: *"Both matters should be considered closed. You have gone on about Wolfram licencing for weeks."*

---

## 2. The drift detector cannot fire, and "3 consecutive rounds" was CC1's error

The founder asked whether it *"will fire after 3 consecutive rounds in any given experiment."* **No.** The figure came from a z3 proof about **3 same-direction UPDATES** and was restated as **rounds**, a different unit.

`bench/dm/_memory.py:335-341` accumulates a two-sided sum against `drift_threshold = 2.0`. **Three independent reasons it cannot fire, and removing any one is insufficient:**

1. **Arithmetic.** `residual = observed_rate - pi_mem(flaw_class)` is a difference of two probabilities, so `|residual| <= 1`. The guard fires on `cusum_pos > threshold`, **strictly**, so 2 updates of exactly 1.0 *reach* 2.0 without firing: **exceeding** it needs `floor(2.0/1.0) + 1 = 3` same-direction updates, each at the theoretical maximum. z3 confirms 1–2 cannot cross and 3 can; the local Wolfram Engine confirmed the same independently (`Reduce` → `False` for 2, `True` for 3).
2. **Supply.** Production makes **1 update per flaw class per run**, not per round.
3. **Memory.** `save()` (`_memory.py:379`) writes `records` but **not `self._drift`** — 0 references. Every reload restarts at 0, so updates cannot accumulate across runs. **Maximum reachable per run = 1.0 < 2.0.**

Replayed over 48 archived production cases it fired **0** times, largest excursion **0.950032**. It is unreachable anyway: `immune_memory_enabled=False` in all three `bench/exp56_configs/*.json` arms.

### 2.1 The obvious repair would invert it into a false-alarm generator

`update_drift` **omits the slack term a CUSUM is defined by**. A one-sided CUSUM is `S+ = max(0, S+ + (x - mu0 - k))`; with `k = 0` the statistic is a random walk reflected at 0 — a non-negative submartingale — which climbs under a perfect null and crosses any fixed threshold in finite time.

**Measured, `scripts/i31_slackless_cusum_2026-09-29.py`, 4000 trials per cell, residual noise 0.15, null with zero drift:**

| steps | no slack | Wilson | slack k=0.05 | Wilson |
|---:|---:|---|---:|---|
| 10 | 0.0000% | [0.0000%, 0.0959%] | 0.0000% | [0.0000%, 0.0959%] |
| 50 | 16.2500% | [15.1392%, 17.4255%] | 0.0750% | [0.0255%, 0.2203%] |
| 200 | 92.9750% | [92.1411%, 93.7265%] | 0.5000% | [0.3239%, 0.7711%] |
| 1000 | 100.0000% | [99.9041%, 100.0000%] | 2.9500% | [2.4691%, 3.5212%] |

Wilson intervals computed twice — direct formula and `statsmodels.proportion_confint` — agreeing to **1.110e-16**. Crossing follows the diffusive law: median first crossing 195, 93 and 37 steps at noise 0.10, 0.15, 0.25 against unscaled `(2.0/σ)²` of 400, 177.8, 64, giving near-constant ratios 0.487, 0.523, 0.578. The analytic `E[max] ≈ σ√(2n/π)` crosses 2.0 between n=200 and n=1000, consistent with a simulated median of 93.

**Persistence alone is the wrong repair.** Effectiveness needs three things together: persistence, a slack term, and a threshold derived from the observed excursion distribution rather than chosen — the present 2.0 exceeds the largest recorded excursion by more than a factor of 2.

**Open for the founder, unchanged since 2026-09-17 (item 12b):** retire the detector with an explicit entry, or keep the reporting-only call and rebuild it properly alongside whichever study enables immune memory. The measurement above is now committed either way, so the naive repair is pre-refuted.

---

## 3. The explorer and the appendix now separate A from M

Approved: *"Yes update the explorer as you suggest"* and, on Astra's branch table, *"Verdict: Yes do it."* They turned out to be one addition.

- **A** = `σ·R_det + (1−σ)·R`, `R_det = R(1−q)/(1−qR)` — a **σ-weighted blend**, exactly linear in σ (`A = R + σ(B₋ − R)`). What `explorer/index.html` has always plotted. **It equals the true risk-given-no-detection only at σ = 1** — see §4.
- **M** = `R(1−qσ)` — the risk **expected before the branch is known**. What should decide whether to run the pass.

| outcome | probability | risk afterwards |
|---|---|---|
| detected | `qR` | `1−σ` |
| not detected | `1−qR` | `R(1−q)/(1−qR)` |
| **expectation** | **1** | **`M = R(1−qσ)`** |

`qR(1−σ) + (1−qR)·R_det ≡ R(1−qσ)` for every σ. At **σ = 1 only**, `A = M ÷ P(no detection)`. Elsewhere that quotient is false and the card says so. What holds everywhere is `A − M = R²qσ(1−q)/(1−qR) ≥ 0`. **The direction is one-way: A never reads better than M, so judging a pass by A alone understates its worth.** Worked example `R=1/2, q=4/5, σ=1`: `A=1/6`, `M=1/10`, `P=3/5`, `(1/10)÷(3/5)=1/6`.

**Two engines.** SymPy reduced all three differences to an exact 0. As the secondary cross-verification falsifier, Wolfram Language returned `{0, 0, 0, True, False, {1/6, 1/10, 3/5, 1/6}}` — `Resolve[ForAll[...], A−M≥0]` → `True`, `Reduce` on the strict negation → `False`. *Computed with Wolfram Language.*

Added to `docs/MATHEMATICAL_APPENDIX.md`, which already carried the equivalent correction for **improvements** but not for the **risk levels**. Held by `bench/tests/test_explorer_branch_table_2026-09-29.py`, 10 tests, which executes the page's own `renderBranches` rather than re-deriving it, with cases straddling σ=1 because the identity clause is true there and false elsewhere — a probe testing only σ=1 would confirm a renderer wrong everywhere else, which is precisely the 2026-09-28 clamp-bug failure mode. Five mutations introduced; all five caught.

---

## 4. An external assessment, 2026-09-29, and both of its corrections were right

`Responses/CDSFL_Panel_Advice_and_Shakedown_Readiness_2026-09-29.md`, reviewing commit `9c39332`, recommended proceeding with the simulated shakedown and raised two concrete corrections. **Both were verified and both held.**

### 4.1 Correction 1 — the perfect-repair identity does not establish the partial-repair reading

The claim under review: `scripts/branch_form_semantics_2026-09-29.py` proved `A = M/P(negative)` **at σ=1** and then described `A` as the negative-branch conditional *generally*. **That extension is not justified, and the same wording had propagated into `docs/MATHEMATICAL_APPENDIX.md` and `explorer/index.html`.**

The reviewer's counterexample, `R = 1/2, q = 4/5, σ = 1/2`, checked value by value on SymPy and independently on Wolfram Language — **every figure quoted was exact**:

| quantity | value |
|---|---:|
| P(positive) = qR | 2/5 |
| P(negative) | 3/5 |
| risk given a negative result, `B₋` | 1/6 |
| risk after a positive result and repair, `1−σ` | 1/2 |
| expected risk `M` | 3/10 |
| the retained blend `A` | 1/3 |
| `M ÷ P(negative)` | 1/2 |

**`A` is none of the other three.** `Reduce[A == B₋ && 0<R<1 && 0<q<1 && 0<σ≤1, σ]` returns `σ == 1`, and the same for the quotient identity — so both are endpoint results, not general ones. *Computed with Wolfram Language*; SymPy's `solve` agrees, returning `[1]`.

**What survives untouched:** the branch average `qR(1−σ) + (1−qR)B₋ ≡ M` for every σ, and `A − M = R²qσ(1−q)/(1−qR) ≥ 0` (`Resolve[ForAll[...]]` → `True`). The correction is to the *label*, not the algebra.

**Closed.** The script now executes the counterexample as check 6 and asserts the four values are distinct; the appendix carries the table above with an explicit "what `A` is not"; the explorer no longer says "conditional update" anywhere; and `bench/tests/test_explorer_branch_table_2026-09-29.py` carries the reviewer's case with the exact rationals pinned.

### 4.2 Correction 2 — experiment age must not change when files are copied

`scripts/latent_control_audit.py:266` set the age baseline from `fp.stat().st_mtime`. **Reproduced against the real functions:** touching one report with **0 bytes changed and an identical sha256** moved the baseline **58.0 days** and flipped the `TOO_NEW` verdict for a control first committed 2026-09-01 from **True to False**.

**Closed by the reviewer's own minimal closure.** `_provenance_time()` now reads a run's recorded date from its own path, and **filesystem mtime is not a fallback** — a fallback would restore the defect precisely for the undated files a copy would silently re-date. A report with no recorded date contributes nothing to the baseline and is listed in `reports_without_provenance`; `audit()` now declares `age_source` (`recorded_provenance` / `override` / `UNKNOWN`) and `age_conclusions_available`.

**Coverage, measured:** 221 of 287 run directories carry a parseable date (**77.0035%**, Wilson [71.7975%, 81.4962%]); of the **77 admitted reports, 75 did** (**97.4026%**, Wilson [91.0154%, 99.2848%]) before a shape-constrained bare-`YYYYMMDD` pattern was added, and **0 lack provenance now**. The pattern rejects `99999999` and month-13 dates.

**The mirror had to move with it, and its going red was it working.** `test_latent_control_audit_2026-09-01.py` carries `_newest_archive_mtime()`, a deliberate hand-written mirror of `_archive()` whose stated purpose is to catch the audit drifting from the rule it claims to apply. It went red the moment the audit was corrected. It now reads recorded dates too — **via `datetime.strptime`, not a copy of the audit's regexes**, because two independent readings that agree are evidence while one reading imported twice is a tautology. Across the live archive the two agree on **7206 of 7206 files, 100.0000%**, Wilson [99.9467%, 100.0000%], statsmodels and a direct closed form agreeing to 1.11e-16.

Held by `bench/tests/test_archive_age_is_provenance_not_mtime_2026-09-29.py`, 15 tests. Mutations: forcing `_provenance_time` to `None` fails 6; restoring the mtime baseline fails 1.

### 4.3 What the assessment did not change

Its readiness judgment stands and nothing here contradicts it: neither correction is a launch prerequisite, and the inspected simulated launch path calls neither the archive audit nor the branch-semantics script. Correction 2 was a limitation on *historical-evidence conclusions*, which is why it was closed rather than deferred — an age verdict that depends on when files were last copied cannot be cited as commissioning evidence.


---

## What remains

1. **One ruling**, open since 2026-09-17: retire the drift detector or keep it reporting-only and rebuild later. §2.1 carries the evidence for both.
2. **Nothing on Wolfram.** Every seat class complies; closed by the founder's 2026-09-28 ruling and recorded here only so a later session does not reopen it.
3. The simulated shakedown run remains the next action and remains unblocked.
