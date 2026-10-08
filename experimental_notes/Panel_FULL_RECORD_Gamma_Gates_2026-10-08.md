# Gamma gates wherever a curve exists: the free panel on the committed fix

Record written 2026-10-08T05:15:53+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. A change already COMMITTED to the active runner, at ad2ae579 and 8f014a59 on sim/shakedown-2026-09-29, not a proposal: gamma now gates in every case where a decay curve exists, and where no curve exists the 2 guards from the sibling gate apply, one of which refuses.

WHY. The founder's standing directive is that gamma is load-bearing and must never be demoted. A seat found _check_hardened_convergence making gamma "reported-not-gated" whenever the cumulative critical pool fell below 8, so the gate described throughout the project as two-sided went one-sided in precisely the endgame, and the surviving half is the half a shrinking roster attacks. He ruled: gamma remains active in all cases. A first attempt gated gamma wherever estimable and labelled the rest "unestimable", which he rejected as the demotion renamed -- correctly, because in that branch gamma still did not gate.

HOW THE ROUND RAN. 2 free seats, 0 paid, blind round, dispatched 04:32. cc2 answered with 14,244 characters, 2,110 words and 64 tool calls in 1427.2 s; fable with 11,575 characters, 1,668 words and 49 tool calls in 833.6 s. Both on the first attempt. All 52 committed guards passed unmodified under both seats.

THE VERDICTS. cc2: sound in its central claim, unsound as shipped, needs repairs not reversion. fable: sound with repairs. They converged independently on the same 2 critical defects.

F1, BOTH SEATS, CRITICAL. The fix imported the sibling gate's 2 vacuity guards and left behind the 2 blocks that stand in front of them -- the A4 unverified-critical fail-safe and the contested block -- so the 2 gates returned opposite verdicts on identical registries. The direction is unsafe: UNCONFIRMED is an unresolved status that the novelty filter strips from the settled series, so an unverified critical drives `cum_crit` down and pushes the run INTO the vacuous branch. cc2 demonstrated 6 untested critical claims converging where the sibling refused with "A4 BLOCK", and measured that A4 alone would not close the gap, so both blocks are needed. fable traced the dependency chain to the boundary and found no intervening recheck once convergence is promoted, and measured archive exposure at 0 of 69 runs -- a forward hazard rather than a retroactive miscount.

F2, BOTH SEATS, CRITICAL. The full branch's leave-one-round-out loop gated on the 0.0 sentinel. Dropping the only non-zero round of a single-burst series leaves an all-zero subseries, the estimator returns its sentinel, and a maximal-depletion run -- gamma 1.0000, window met -- is permanently refused at any horizon. That contradicts the fix's own stated principle in the branch directly beside the one it repaired. fable measured archive exposure at 6 of 69 runs with that shape, naming exp38_ouroboros, exp39_0_gate, exp42_composer and 2 sim45_canary runs.

F3, fable, LOW. When `cum_crit` is positive but gamma is unestimable, the refusal text asserted a slope that is a sentinel. The verdict cannot flip, but the record claimed a measurement it does not have.

F4, fable, LOW. 2 stale docstrings: one described the mode name of the REJECTED first version, which appears nowhere in the code, and one still stated the removed "reported-not-gated" contract. Its phrasing is kept because it names a failure this project has recorded twice before: a stale guarantee in a docstring is how a rejected position acquires authority here.

VERIFIED CLEAN BY BOTH SEATS. The hand-maintained mirror between the estimability predicate and the estimator: cc2 found 0 failures over 1,195,703 series and fable over 21,845 exhaustive series. Both derived that the one condition the predicate omits, the degenerate denominator, needs on the order of a million rounds to bite, against a maximum of 21. The constant-rate lookalike never reaches the vacuous path. Telemetry persistence is wired.

WHAT WAS DONE WITH THE FINDINGS. All 4 are fixed in the canonical tree rather than left as proposals, because the founder's instruction was to fix and then consult. F2 was repaired before fable's reply landed, from cc2's falsifier. F1 is derived IN-GATE rather than passed as parameters, which is fable's correction of its own first repair after its falsifier caught that a caller can omit a defaulted parameter and reopen the hole. F3 names the sentinel in the refusal text. F4 retracts both stale docstrings. 133 tests pass across 9 affected guard files.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Gamma now gates in every case where a curve exists: review the fix and try to break it

## What you are reviewing

A change already COMMITTED to the active runner, at `8f014a59` and `ad2ae579` on `sim/shakedown-2026-09-29`. Not a proposal. If it is wrong it is wrong in live code, and the founder will act on what you find.

- `bench/reference_runner_v3.py` — `_check_hardened_convergence` and the new `_gamma_is_estimable`
- `bench/tests/test_gamma_gates_wherever_it_exists_2026-10-08.py` — 21 guards
- `bench/tests/test_hardened_gate.py` — 2 pre-existing guards updated, 1 added
- `bench/tests/test_vacuous_gamma_curve.py` — the sibling path this fix imports from

Run all of them. Execute `_check_hardened_convergence` directly; do not read it and conclude.

## Why the change was made

The founder's standing directive is that gamma is load-bearing and must never be demoted. The fable seat found `_check_hardened_convergence` making gamma "reported-not-gated" whenever the cumulative critical pool falls below `gamma_crit_min_cumulative`, which defaults to 8 and is set by only 4 of the 47 experiment configs. So the gate described throughout the project as two-sided went ONE-SIDED in precisely the endgame regime, and the surviving half — the zero-novel-critical window — is the half a shrinking roster attacks.

His ruling: *"Gamma should remain active in all cases. Fix it."*

The first attempt gated gamma wherever it was estimable and labelled the remaining case "unestimable". **He rejected that**: *"if gamma remains unestimable, how can gamma ever hit the 0.30 mark that has traditionally been set for it? Isn't this gamma demotion by another name?"* He was right. In that branch gamma still did not gate, and renaming a state is not fixing a behaviour.

## What the change now does

**`_estimate_gamma` returns 0.0 for 4 distinct reasons and only 1 is a slope of 0.0** — too few rounds, an all-zero series, fewer than 2 usable log points, a degenerate denominator. `_gamma_is_estimable` separates the sentinel from a slope by mirroring the estimator's own conditions. Measured: `[1,0,0,0,0]` gives 1.0000, `[5,0,0,0,0]` gives 1.0000, `[2,1,0,0,0]` gives 0.7597, `[1,2,3,4,5]` gives 0.0000 and `[0,0,0,0,0]` gives 0.0000. A flat cumulative curve is maximal diminishing returns, so flat-at-zero receiving the FLOOR is the wrong answer rather than an unknowable one.

**Where a curve exists, gamma gates.** Including in the sparse branch where it previously did not. Reachability was measured rather than assumed, because a change that bites nowhere is an unwired addition: an exhaustive sweep over short sparse series with the window met found `[1,3,0,0,0]` at gamma 0.1783 and `[1,4,0,0,0]` at 0.0461. Both converged before and are refused now.

**Where no curve exists, the proven two-guard vacuity from the sibling gate applies, imported rather than re-invented.** `test_vacuous_gamma_curve.py` states the principle: gamma is not demoted, its estimator's DOMAIN is narrowed. The 2 guards are that cumulative critical over the WHOLE history must be zero, so a constant-rate series stays blocked; and that the panel must have produced findings of SOME severity, so a clean target is distinguishable from a dead panel. The second guard REFUSES convergence.

**The gate's mode is now persisted to the round record.** It previously reached `_log` and nothing else: a scan of every report under `bench/logs` for a record carrying `mode` returned 0, so no archived run says which mode closed it and the ruling would have been unauditable even once implemented.

Every path, executed:

| critical series | findings | outcome | mode |
|---|---|---|---|
| `[0,0,0,0]` | 18 | CONVERGED | `vacuous_curve_converged` |
| `[0,0,0,0]` | 0 | **REFUSED** | `vacuous_curve_refused_dead_panel` |
| `[0,0]` | 18 | REFUSED | `vacuous_curve_window_unmet` |
| `[1,3,0,0,0]` | 12 | REFUSED | `sparsity_gamma_gated` |
| `[5,0,0,0]` | 12 | CONVERGED | `sparsity_gamma_gated` |
| `[2,2,2,2,2,2]` | 30 | REFUSED | never reaches the vacuous path |

## What you must try to break

1. **Find a path where gamma is excused without a guard.** That is the whole claim. If one exists the fix fails on its own terms.
2. **Find a case where a dead panel still converges**, or where a clean target is refused. The 2 guards are supposed to separate them; show they do not.
3. **The mirror between `_gamma_is_estimable` and `_estimate_gamma` is hand-maintained.** Find an input where they disagree — where the predicate says estimable and the estimator returns its sentinel, or the reverse. A test executes both on 10 shared inputs; widen it.
4. **Is "flat cumulative curve means fully decayed" actually right?** The fix does NOT set gamma to its ceiling for an all-zero series; it routes that case to guarded vacuity instead. Say whether setting the ceiling would be better or worse, and what it would break.
5. **The constant-rate series is the dangerous lookalike.** `[2,2,2,2,2,2]` drives the estimator to the same 0.0 as a clean run for the opposite reason. Prove the first guard excludes every such case, or find one it admits.
6. **This change TIGHTENS convergence**, so a run that previously closed may now continue. Quantify the cost against the archive: how many completed runs would have been refused, and at what round?
7. **Does the fix interact with the roster hazard?** The one-sided endgame was found because a shrinking roster attacks the window. With gamma now gating in the sparse branch, is the roster hazard reduced, unchanged, or moved?

## Required: fixes, not only findings

For every problem you raise, propose a repair, write and EXECUTE a falsifier, and deliver each fix as a file at its real path in your sandbox tree. A fix you have not run is a hypothesis. Where a parameter is involved, derive it and show the derivation.

## Output

- VERDICT on the committed change: sound, sound with repairs, or unsound and should be reverted.
- FINDINGS, each with file and line, each marked OBSERVED with the command that shows it or HYPOTHESISED with what would settle it.
- FIXES, one per finding, delivered as files, each with its executed falsifier output.
- YOUR STRONGEST DISAGREEMENT with this brief's framing. Briefs in this series have been wrong about a correlation, a rate, a sensitivity span, a collision mechanism and the direction of a censoring, each caught by a seat rather than the author. Assume this one is wrong somewhere.
- WHAT WOULD REFUTE YOUR OWN POSITION, as a measurement someone else could run.
- CONFIDENCE, with the evidence that sets it.

## Termination

Stop when every numbered item above has a fix with an executed falsifier or an explicit statement that it cannot be answered and why. Stop early if 2 consecutive passes produce no new finding above the threshold of real-world consequence.
<!-- figure: flat_after_something_is_the_ceiling | bench/gamma_sentinel_versus_slope_2026-10-08.py | 1.0000 -->
<!-- figure: partially_flat_curve | bench/gamma_sentinel_versus_slope_2026-10-08.py | 0.7597 -->
<!-- figure: sparse_window_met_gamma_low | bench/gamma_sentinel_versus_slope_2026-10-08.py | 0.1783 -->
<!-- figure: sparse_window_met_gamma_lower | bench/gamma_sentinel_versus_slope_2026-10-08.py | 0.0461 -->


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 64 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel gamma_gates_everywhere_2026-10-08) -->

## VERDICT

**Sound in its central claim, unsound as shipped — needs repairs, not reversion.** The founder's ruling is correctly implemented: gamma does gate wherever a curve exists, the vacuity narrowing is guarded, and the dead-panel guard really refuses. I executed the gate rather than reading it, and the brief's own table reproduces. But the fix states *"there is no case left in which gamma is excused without a guard"*, and that is true only inside the settled-series abstraction. Outside it, **the fix imported the sibling gate's 2 vacuity guards and left behind the 2 blocks that stand in front of them**, so the two gates return opposite verdicts on identical registries — in the unsafe direction.

All 52 committed guards pass unmodified (`116 passed` with my 9 added).

---

## FINDINGS

### F1 — The vacuous-curve path converges over unverified criticals that the gate it copied from blocks. **OBSERVED**
`bench/reference_runner_v3.py:9285-9298` (guard), `:9282` (guard 2 input), `:17670` (call site)

`_check_gamma_alt_convergence` reaches its vacuous-curve case only after the A4 fail-safe (`:8181`) and the contested block (`:8219`) pass. `_check_hardened_convergence` receives the same registry and consults neither — the call site passes it only `(round_idx, registry, cfg)` while the sibling is handed `unresolved_critical`, `contested`, `irreducible_queue` explicitly (`:17689-17696`).

The direction is what makes it material. `UNCONFIRMED` is an *unresolved* status (`:3140`) that `_NON_NOVEL_TERMINAL_STATUSES` strips from the settled series. An unverified critical therefore does not merely fail to block — it **drives `cum_crit` down and pushes the run into this branch**. The censoring runs toward convergence.

```
$ python3 /tmp/fx/fals_A4.py     # real FindingRegistry, real _settled_novelty_series
settled critical series : [0, 0, 0, 0, 0, 0]
cum_critical            : 0          <- guard 1 satisfied
A4 unverified criticals : 6          <- six untested critical claims
hardened gate converged : True   mode: vacuous_curve_converged
sibling gate converged  : False  "A4 BLOCK: 6 unverified critical-severity candidate(s)"
FALSIFIED                                                             exit 1
```

Not confined to the new code: 9 CONFIRMED criticals in round 0 + 3 UNCONFIRMED pending puts `cum_crit=9`, i.e. `mode="full"`, with the same gap.

Both blocks are needed, and that is a **measurement, not a judgement** (founder, 2026-10-02):

```
$ python3 /tmp/fx/compose_measure.py
crit_s: [0,0,0,0,0,0] cum: 0 | A4: 0 | contested: 4
hardened : True  mode: vacuous_curve_converged
sibling  : False "critical-quiescence blocked: contested=4"
A4-ONLY fix would close this divergence?  NO
```
Neither block subsumes the other, so the composed fix is justified on a demonstrated advantage over A4 alone.

### F2 — `_gamma_is_estimable` was added and then applied in 1 of the 4 places the estimator meets a threshold. **OBSERVED**
`bench/reference_runner_v3.py:3637-9341` and `:9346-9350`

The `sustained` and leave-one-round-out loops call `_estimate_gamma` on **shorter** sub-series and compare the result to theta raw. Shorter is where the sentinel is *most* likely, not least. By the fix's own standard — "gating on a sentinel is not gating on gamma" (`:9248`) — that is the same defect one branch over, running in the opposite direction.

```
$ python3 /tmp/fx/fals_loo_sentinel.py
series: [9,0,0,0,0,0]  cum_crit: 9 (FULL branch)
gamma_crit: 1.0 >= theta: True | sustained: True | zero_crit_ok: True
loo_min: 0.0  loo_ok: False  ->  verdict: False
   drop-one -> [0,0,0,0,0]: gamma=0.0  estimable=False  <-- SENTINEL, not a slope
sibling gate on identical data: True
FALSIFIED                                                             exit 1
```
A run that found every critical in round 0 and nothing in 5 clean rounds since — maximal diminishing returns — is refused, and burns its budget to `max_rounds=21`. That is the false negative the vacuous-curve guard exists to prevent.

### F3 — The 2 guards are measured in different coordinate systems. **OBSERVED, not patched**
`bench/reference_runner_v3.py:9282`

Guard 1 reads `sum(crit_s)` (settled-novelty space); guard 2 reads `len(registry.entries)` (raw-entry space). A registry whose every entry the gate's own novelty filter discards satisfies guard 2:

```
$ python3 /tmp/fx/item7.py
18xDUPLICATE : sum(all_s)=0 len(entries)=18 -> converged=True mode=vacuous_curve_converged
18xMERGED    : sum(all_s)=0 len(entries)=18 -> converged=True
18xREFUTED   : sum(all_s)=0 len(entries)=18 -> converged=True
```
`sum(all_s)` is already a local in the same function, so the repair is one token. **I did not apply it.** Archive incidence is zero — 0 of 134 archived registries have `sum(all_s)==0` with entries present — and the consistent repair must land in the sibling's call site (`:17696`) too, which is the 43/47 production path. Simplest sufficient says report it; don't ship an elaboration nothing reaches.

### Non-findings I tried hard to make into findings, and could not

- **Item 3, the hand-maintained mirror: SOUND.** 0 predicate failures over 1,195,703 series (lengths 0–12). The one estimator condition the predicate omits is `abs(denom) < 1e-12`. Derived: usable log points are a contiguous suffix, so the minimising case at `usable==2` is indices `{n-2, n-1}`, giving `denom = ln(n/(n-1))² ~ n⁻²`. Degeneracy needs **n ≈ 1.0000005×10⁶ rounds**; `max_rounds = 21` gives `2.38×10⁻³`, nine orders clear. SymPy and Wolfram Language (local Wolfram Engine, via `wolframscript`, exit 0, `Out` values printed) agree to 7 figures. The omission is unreachable, so the mirror is exact in the reachable domain. The 9,957 "estimable yet exactly 0.0" cases are β>1 clamps — genuine slopes, correctly refused.
- **Item 5, guard 1 vs the constant-rate lookalike: SOUND, by construction.** The branch requires `cum_crit == 0`; a constant-rate series with rate c≥1 has `cum_crit = c·n ≥ 1`. 0 of 70 constant-rate series (7 rates × 10 lengths) reach a vacuous path or converge. Census over 20,480 driven gate calls: the *only* converging mode with `gamma_crit_gated False` is `vacuous_curve_converged`, and every instance has `cum_crit == 0` and `findings > 0`.
- **A re-indexing hypothesis I raised and then refuted myself.** The LOO loop does not leave a round out — it *relabels the time axis* of every retained round (`crit_s[:i] + crit_s[i+1:]`). I predicted this artefactually blocks real runs. Measured against a time-preserving fit on the archive's one near-miss round: **0 of 8 candidate series flip toward passing**; the time-preserving LOO is *tighter* (0.0000 vs 0.0711). My hypothesis was wrong in the direction I guessed.

### Item 4 — would the ceiling be better? **Worse, and measurably so**

For `[k,0,0,…]` the cumulative curve is flat and β=0, so γ=1 is a *fitted* result. For an all-zero series the fit has **zero points** — γ is undefined, not 0 and not 1. Setting the ceiling makes the series estimable and ≥ θ, which routes the run *out* of the guarded branch and bypasses guard 2 entirely:

```
$ python3 /tmp/fx/item4b.py
DEAD PANEL (0 findings of any severity)
   as committed (guarded vacuity): converged=False mode=vacuous_curve_refused_dead_panel
   with gamma=ceiling           : converged=True  mode=sparsity_gamma_gated
```
The ceiling re-opens the exact hole the fix closes. Guarded vacuity is the right answer.

### Item 7 — the roster hazard is **moved and narrowed, not removed**

The window-only regime shrank from all of `cum_crit < 8` to `cum_crit == 0`, so gamma now gates in the band the brief measured. The residual is that guard 2's threshold is **one finding**:

```
findings= 0 -> converged=False mode=vacuous_curve_refused_dead_panel
findings= 1 -> converged=True  mode=vacuous_curve_converged
```
A roster shrunk to a single seat returning one low-severity finding clears it. The hazard did not reduce; it concentrated into the one branch where the window is still the only series-derived condition.

---

## FIXES

Delivered at their real paths in my sandbox tree (`bench/reference_runner_v3.py` is denied write in the canonical repo; this panel's staged copy is the sandbox):

| file | change |
|---|---|
| `bench/reference_runner_v3.py` | **Fix 1** (F1): review-clean preconditions read off the registry the function already holds, placed before the branch split so one block covers `full`, `sparsity_gamma_gated` and `vacuous_curve_*`. Duck-typed with `review_clean_source` on the round record, so the 52 stub-driven guards keep passing and no reader mistakes "never asked" for "asked and clean". No new crash surface: `contested_count` is already called every round via `_check_stall_convergence` (`:9484`). **Fix 2** (F2): `sustained`/LOO skip *unestimable* sub-series instead of counting their sentinel as fragility, with `loo_estimable_n` / `sustain_estimable_n` recorded so a silent robustness arm reads as silence, not satisfaction. |
| `bench/tests/test_hardened_gate_review_clean_2026-10-08.py` | 9 guards, all driving the **real** `FindingRegistry` through the **real** `_settled_novelty_series` — the committed guards monkeypatch the series and pass a stub with only `.entries`, which cannot express a registry where a critical exists but is invisible to the series. Includes the composability measurement and `test_an_estimable_fragile_sub_series_still_refuses`, which proves fix 2 is a domain restriction and not a relaxation. |

```
$ python3 -m pytest <9 gamma/gate/A4 files> -q
116 passed in 1.15s

fals_A4                exit 0 (defect NOT demonstrated -> repaired)
fals_loo_sentinel      exit 0 (defect NOT demonstrated -> repaired)
compose_measure        exit 0 (defect NOT demonstrated -> repaired)
```

---

## STRONGEST DISAGREEMENT WITH THE BRIEF

**Item 6 asks the wrong question and its premise is false. The answer is zero, and the reason matters more than the number.**

The brief says "this change TIGHTENS convergence, so a run that previously closed may now continue" and asks for the archive cost. Measured:

- 0 of 8,239 JSON artefacts under `bench/logs` carry `hardened_gate_enabled: true`; **4 of 47 configs enable this gate at all**, and none of them is a live exam arm (48 chemistry, 49 engineering, 50 physics, 51 biology, 53 control all run `false`, i.e. the sibling path this fix does not touch).
- Exactly **5 archived runs** ever executed `_check_hardened_convergence`, and exactly **1 round in the whole archive ever converged through it**: `exp40_unitB`, R3, `cum_critical=4 < 8`, `γ_crit=1.000 reported-not-gated`.
- Under the new code that round becomes `sparsity_gamma_gated` with γ=1.000 ≥ 0.30 and **still converges, at the same round R3**.

So **0 of 1 archived hardened-gate convergences would be refused**. The reachability sweep the brief cites — `[1,3,0,0,0]` → 0.1783, `[1,4,0,0,0]` → 0.0461 — establishes that the band exists in an abstract space of short series. It does not establish archive incidence, and the archive incidence is 0/1, because the one real convergence sat at the ceiling, not in the band. The brief presents a sweep over synthetic series as if it discharged the additive standard's reachability requirement. It does not. By that standard this fix is wired to a caller and executed by tests, but **it has not been shown to bite on any run anyone has made** — and it was the brief, not the fix, that claimed otherwise.

Second, smaller: the brief says `_estimate_gamma` "returns 0.0 for 4 distinct reasons". It returns 0.0 for **five** — the fifth is `max(0.0, …)` clamping β>1, which is a genuine slope and accounts for 9,957 of my 21,845 enumerated cases. That fifth one is why my own re-indexing hypothesis died and why fix 2's archive incidence is 0: all four reconstructable archived `loo_min=0.0` values are clamps, not sentinels (`[5,1,3,0]`, `[5,1,3,0,2]`, `[7,1,2,0]`, `[7,2,3,3]`, each uniquely pinned by its logged γ). Miscounting the sentinel sources is how you reach for the wrong half of the arm.

---

## WHAT WOULD REFUTE MY POSITION

1. **F1 dies** if a reader shows that in a real run under `hardened_gate_enabled`, `unverified_critical_count()` cannot exceed 0 at the moment the gate is called — e.g. the finalize sweep resolves every UNCONFIRMED critical earlier in the round loop. Measurement: instrument `:17633` and `:17670` in one live `41_convergence` run and log `(round_idx, unverified_critical_count(), mode)` per round. A run where `unverified_critical > 0` and `mode` is a converging mode confirms me; 0 such rounds across the 4 hardened configs' full round budgets makes F1 a theoretical hole, still worth the block but not material.
2. **F2 dies on incidence** if, across those same instrumented runs, `loo_estimable_n == len(crit_s)` in every round — i.e. an unestimable sub-series never arises in practice. My demonstration uses `[9,0,0,0,0,0]`; if real critical series never concentrate in one round, the fix is correct and unreached.
3. **My item-6 claim dies** if a run archive exists outside `bench/logs` where `hardened_gate_enabled` was true. I scanned `bench/logs` only; a differently-rooted archive would change the 0/1 denominator and could change my verdict on reachability.

---

## CONFIDENCE

**High on F1 and F2 as defects** (both CONFIRMED by falsifiers that import the real module, drive the real registry, and go from exit 1 to exit 0 across the patch; F1's divergence is shown against the sibling gate on byte-identical registries). **High on the three non-findings** (mirror: 1,195,703 series, 0 failures, plus a closed-form bound cross-checked by SymPy and Wolfram Language; guard 1: exclusion by construction plus 20,480 driven gate calls; ceiling: executed counterfactual). **High on item 6's numbers** (config scan is exhaustive over 47 files; archive scan is exhaustive over 8,239 artefacts; the one converging round is quoted from its log line).

**Medium on F1's and F2's real-run incidence** — that is precisely what measurement 1 and 2 above would settle, and I could not settle it from the archive because the hardened gate has 5 runs and no A4 log line among them. **Low confidence, stated as such, that F3 deserves shipping at all**: 0 of 134 archived registries reach it.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 49 recorded tool call(s).

<!-- verbatim-begin: fable (panel gamma_gates_everywhere_2026-10-08) -->

All items are now answered with executed evidence. Final report.

---

# VERDICT: SOUND WITH REPAIRS

The committed change does what it claims — gamma gates wherever estimable, the constant-rate lookalike is excluded, the mirror cannot drift on any reachable input, telemetry is persisted — and it tightens, never loosens, closure. But it imported the sibling gate's two vacuity guards **without the preconditions that guard them** (A4, contested), and it left the gate's own LOO loop gating on the very sentinel the fix was built to name. Both defects confirmed by executed falsifiers. Neither warrants revert; both have running repairs.

# FINDINGS

**F1 — CRITICAL (verification-integrity): the hardened gate's vacuous-curve path converges past the A4 fail-safe.** `bench/reference_runner_v3.py:9281–9298` (gate), `:17669–17670` (caller). An UNCONFIRMED critical-severity candidate is excluded from the settled series by `_NON_NOVEL_TERMINAL_STATUSES` (line 8695), so the critical series reads all-zero and `vacuous_curve_converged` fires while a critical the system gave up on is pending — the exact scenario `unverified_critical_count`'s docstring forbids ("would vanish from the count and let the streak accrue"). The sibling gate reaches its vacuous branch only *behind* its A4 block (8181) and contested block (8219); the import took the guards and left their preconditions. I traced the dependency chain to the boundary: `_unresolved_crit` is computed at 17633 and passed **only** to the sibling (17689); once `gamma_alt_converged` promotes `converged` (17713–17715) the run closes at 18190–18205 with no intervening recheck. Contested has the same bypass. **OBSERVED:** `python3 /tmp/cdsfl_seat/falsifier_a4_bypass.py` → `converged=True mode=vacuous_curve_converged unresolved_critical=1` → AssertionError. Archive exposure: 0 of 69 archived runs (scan executed) — a forward hazard, not a retroactive miscount. Partly pre-existing (the old sparse branch converged on the window alone), but the commit's explicit claim of sibling parity makes the missing preconditions a defect of this change.

**F2 — CRITICAL (wrong result, opposite direction): the full branch's LOO loop gates on the 0.0 sentinel.** `bench/reference_runner_v3.py:9345–9350`. Dropping the only non-zero round of a single-burst series leaves an all-zero LOO subseries; `_estimate_gamma` returns its sentinel; `loo_min=0.0` fails `θ−tol` forever. A maximal-depletion run — γ_crit = 1.0000, window met — is **permanently refused**: `[8,0,…,0]` never converges at any horizon. This contradicts the commit's own principle ("gating on a sentinel is not gating on gamma") in the branch directly beside the one it fixed; `_gamma_is_estimable` existed and was not applied here. **OBSERVED:** `python3 /tmp/cdsfl_seat/falsifier_loo_sentinel.py` → refused at z=4,8,16,32 with `loo_min=0.0` → AssertionError. Archive exposure: **6 of 69 runs** have this shape (`exp38_ouroboros [19]`, `exp39_0_gate [12]`, `[11,0,0,0]`, `exp42_composer [14]`, two `sim45_canary` `[12,0,0,0]`/`[13]`).

**F3 — LOW (audit accuracy): sparse branch renders the sentinel as a measured slope.** `:9330`. When `cum_crit>0` but gamma is unestimable (criticals only in the final round), the refusal reason says "γ_crit=0.000 < θ and gamma GATES here". The outcome is always refusal (sentinel 0.0 can never pass θ, proven by the fuzz), so this cannot flip a verdict — but the record asserts a slope that is a sentinel. **OBSERVED:** `_gate([0,0,0,0,1])` on the committed tree.

**F4 — LOW (doc drift, two sites).** `bench/tests/test_gamma_gates_wherever_it_exists_2026-10-08.py:21` describes mode `sparsity_gamma_unestimable`, which belongs to the **rejected first version** and appears nowhere in the code (`grep -rn sparsity_gamma_unestimable` → docstring only). `bench/tests/test_hardened_gate.py:12–14` still states the removed contract "γ reported-not-gated". A stale guarantee in a docstring is how a rejected position acquires authority here.

**F5 — items verified clean (no defect):** mirror exact over 21,845 exhaustive series (disagreements: 0); degenerate denominator needs ~1.05M rounds (for 2 points denom = (log(n+1)−log n)² ≈ n⁻²; < 1e-12 requires n > 10⁶ — unreachable); constant-rate `[c…c]`, c∈1..5, L∈3..12: 0 vacuous-path entries, 0 convergences (window excludes any positive tail; guard 1 excludes the rest); telemetry persistence wired at 17681→17945.

# FIXES (sandbox tree `/tmp/cdsfl_seat/fixtree`, diff at `/tmp/cdsfl_seat/fix_reference_runner_v3.diff`, 87 lines)

- **F1:** `_check_hardened_convergence` now derives `unresolved_critical` and `contested` **in-gate** from the registry/cfg it already holds and refuses (`a4_blocked` / `contested_blocked`) before any convergence path. My first repair passed them as default-0 parameters; my own falsifier caught that a caller can omit them — the hole re-opened. Derivation in-gate is the simplest form no caller can forget; stub registries without the readers fall back to prior behaviour.
- **F2:** LOO subseries are skipped when `¬_gamma_is_estimable(loo)` — an unestimable subseries carries no curve and cannot testify — with skips counted in `telem["loo_unestimable_skipped"]`. LOO is narrowed, not disabled: `[3,1,4,0,0,0]` (own γ=0.3828, estimable LOO dip 0.0461) is still refused, tested.
- **F3:** sentinel refusals name themselves ("0.0 is the SENTINEL, not a slope"). **F4:** both docstrings corrected.
- **Executed falsifier outputs:** both falsifiers exit 1 on the committed tree (defect demonstrated), exit 0 on the patched tree (`a4_blocked`; `converged=True loo_min=1.0` for all `[8,0,…,0]`). Regression tests added (sibling-precondition class, LOO-sentinel class, sparse-sentinel naming): **60 pass** in the three named files, plus **97 pass** across the eight adjacent convergence test files. Composition note: F1 and F2 touch disjoint paths; each was validated alone by its own falsifier before running together — this is two independent fixes, not a composition claiming joint advantage.

# ANSWERS TO THE NUMBERED ITEMS

1. **Gamma excused without a guard:** yes — F1. The guards exist but their sibling preconditions were not imported, so the vacuity is reachable while an unverified critical is pending.
2. **Dead panel converging:** a panel dead from round 0 is refused (tested); a *fully* dead later round terminates the run via `_safety_check` → `all_models_failed` (16389–16393), so it cannot fill the window. The residual is a **mostly-dead** panel (one ≥50-char responder), which no findings-count guard can detect — see item 7. A clean target is not refused: `vacuous_curve_converged` verified over a working panel.
3. **Mirror drift:** none, on 21,845 exhaustive series; the unmirrored fourth condition (degenerate denominator) is mathematically unreachable below ~10⁶ rounds. But the mirror was **not applied** where the sentinel still leaks — the LOO loop (F2). The drift risk was in usage, not in the predicate.
4. **Ceiling for flat-at-zero would be worse.** γ=1.0 for an all-zero series fabricates a measurement from no data: it would flow into `GAMMA_BANDS` as "Strong depletion — confirms state-based closure" for a possibly-dead panel, erase the dead-panel refusal (vacuity would ride the ordinary γ≥θ path with no second guard), and poison archived telemetry with a number downstream readers can't distinguish from a fit. Guarded vacuity, which keeps γ undefined and lets one guard refuse, is the right committed choice.
5. **Constant-rate exclusion: proven.** Executed sweep, 0 violations. Structurally: convergence requires the last W entries zero, so no constant-positive series meets the window in any branch; and cum>0 excludes it from the vacuous path besides.
6. **Cost against the archive: zero.** Replayed all 69 archived registries through old-vs-new sparse rules: 0 runs change their first-closure round. Every archived sparse run that met the window had estimable γ ≥ θ (flat tails push γ up). The newly-refused band (`[1,3,0,0,0]`-like) has never occurred in a real run — the tightening is free retroactively, and its bite is so far synthetic-only.
7. **Roster hazard: reduced marginally, not removed — measured.** A quiet tail is exactly what pushes γ *up*: `[1,3,0,0,0]` is refused at γ=0.1783, but one more quiet round gives `[1,3,0,0,0,0]` γ=0.3076 ≥ 0.30 → converges. Across heads `[1,3]`, `[1,4]`, `[2,5]`, `[1,2,1]`: the γ gate delays closure by **1–2 rounds** over the old window-only rule. Extending sustain+LOO to the sparse branch buys ~1 round each. The hazard is *moved*, not closed: no function of `crit_s` alone can distinguish "roster collapsed to one weak seat" from "error space exhausted" — both produce the same flat tail. The discriminator the gate would need is per-round liveness/effort (responder count), which it does not read. I did not implement that: it is a design decision (new input wiring) for the founder, not a mechanical repair — flagged, not fetched.

# STRONGEST DISAGREEMENT WITH THE BRIEF'S FRAMING

The headline — "Gamma now gates in every case where a curve exists" — is false in the branch the fix itself added, in **both** directions. Where the critical curve doesn't exist but the **all-severity curve does** (`vacuous_curve_converged` requires findings of some severity, i.e. `all_s` has a curve), that existing curve never gates: a panel producing a constant stream of new HIGH-severity findings every round — zero depletion anywhere — closes as vacuous-converged, γ_all carried as a diagnostic only. That is panel-ruled design (2026-05-23), not a defect I can confirm, but the brief's slogan overclaims it. And in the other direction, F2 shows a case where the curve exists at γ=1.0 and a *sentinel* gates instead of gamma — the committed change shipped the exact confusion it was written to end, one loop below the line it fixed. The brief also presents the 1-round-delay sparse refusals as closing the endgame hole; measured, the shrinking-roster attack still succeeds 1–2 rounds later.

# WHAT WOULD REFUTE MY POSITION

- **F1:** run the real runner (`hardened_gate_enabled`, any config) with a registry containing one UNCONFIRMED severity≥0.7 entry and ≥1 benign finding into the window regime; if the run does **not** close `vacuous_curve_converged` (some blocker I missed between 17713 and 18205 fires), F1's severity drops to gate-local. My demonstration is gate-level plus a traced caller chain, not a full integration run.
- **F2:** show that `gamma_crit_min_cumulative`-respecting configs cannot produce a single-burst settled series in live runs — the 6 archived counterexamples say otherwise, but all 6 predate the hardened gate being enabled; if none of the 6 ran with `hardened_gate_enabled`, the archive exposure is 0 realized (the defect remains, forward-looking).
- **Item 6:** rerun my replay with each run's actual config overrides (I used defaults W=3, θ=0.30, min_cum=8; 4 of 47 configs set min_cum) — a nonzero diff under a real override would refute "zero retroactive cost".

# CONFIDENCE

**High** on F1 and F2 (falsifier fails on committed, exits clean on patched, both directions executed; F2 additionally has 6 archive instances of the exposed shape). **High** on the clean items (exhaustive execution: 21,845-series fuzz, constant-rate sweep, 69-run archive replay). **Medium** on the exact size of the retroactive-cost claim (config defaults assumed, stated above). Wolfram Language (local Wolfram Engine) independently confirmed γ([1,3,0,0,0]) = 0.178345, matching the runner and numpy; it was the second falsifier, not the source.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/gamma_gates_everywhere_2026-10-08/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
