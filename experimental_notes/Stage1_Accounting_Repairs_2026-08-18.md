# Stage 1 Accounting Repairs — technical note, and a correction to the item-1.1 claim

**18 August 2026, 12:28 BST.** HEAD `f4df176`. Repairs at `dcbc91b` (items 1.1, 1.5)
and `e1aca4f` (items 1.2–1.4). Suite: **3573 passed, 14 skipped, 0 failed**
(`python3 -m pytest bench/tests/ -q --netguard-strict`, 2026-08-18 12:1x BST, HEAD `dcbc91b`).

Plain-English companion: `Stage1_Accounting_Repairs_Plain_English_2026-08-18.md`.
TTS companion: `~/Desktop/CDSFL_tts/Stage1_Accounting_Repairs_2026-08-18.txt`.

---

## 1. The correction, stated first

Item 1.1 is described in the runway tracker as *"Gate-population mismatch: gamma's
input counts a different population from the one the spec requires"*, and the
commit message for `dcbc91b` repeats the framing. **That description is wrong, and
the measurement below refutes it.** The γ gate's input was already
post-deduplication in every round.

The repair itself is correct and stays. It fixes `novelty_counts`, which feeds
**ρ and the endocrine module** — not the gate.

### 1.1 The two counters

| | `novelty_counts` | `_settled_novelty_series` |
|---|---|---|
| Kind | stored `List[int]`, appended per round | function; rebuilds from the registry on every call |
| Location | `bench/reference_runner_v2.py:8244`, appended `:8915` | `bench/reference_runner_v2.py:4347` |
| Sees current status? | only where explicitly rewritten | always — it reads `e.get("status")` each call |
| Excludes `_NON_NOVEL_TERMINAL_STATUSES`? | round `[-1]` only, pre-repair | **every round, always** |

`_NON_NOVEL_TERMINAL_STATUSES = {MERGED, DUPLICATE, UNCONFIRMED, REFUTED}`
(`bench/reference_runner_v2.py:4179`).

### 1.2 What the gate actually reads

`_check_gamma_alt_convergence` (`bench/reference_runner_v2.py:3856`) — the two-sided
gate — does this at `:4385–4387`:

```python
all_s, crit_s = _settled_novelty_series(registry, round_idx)
g_all  = _estimate_gamma(all_s)
g_crit = _estimate_gamma(crit_s)
```

It never references `novelty_counts`. Neither does the reported γ series:
`:9396–9397` also feed `_settled_all` / `_settled_crit`.

### 1.3 The measurement that settles it

Running the runner's own `_settled_novelty_series` against the archive and feeding
the result to the runner's own `_estimate_gamma`:

| run | settled critical series (the gate input) | γ_crit recomputed | γ_crit archived | match |
|---|---|---|---|---|
| exp43 | `[5,2,3,3,1,0,0,0,0,0,0,1,3,1]` | 0.5659 | 0.5659 | ✅ |
| exp44 | `[8,5,7,6,0,3,2,1,0,0,1,1,0]` | 0.4532 | 0.4532 | ✅ |
| exp45 | `[7,4,0,1]` | 0.6213 | 0.6213 | ✅ |
| exp46 | `[4,2,3,2,1,0]` | 0.3357 | 0.3357 | ✅ |
| exp48 | `[25,4,1,0,1,0]` | 0.8847 | 0.8847 | ✅ |
| exp49 | `[22,3,2,2,1,0,0]` | 0.8293 | 0.8293 | ✅ |
| exp42 (16r) | `[15,10,6,3,1,0,1,0,2,1,1,0,4,4,…]` | 0.6372 | 0.6372 | ✅ |
| exp42 (7r) | `[20,4,8,3,4,1,0]` | 0.6068 | 0.6068 | ✅ |
| exp42 (2r) | `[14,3]` | 0.0000 | 0.0000 | ✅ |

9 of 11 reproduce exactly. The 2 that do not (exp42 12-round, exp47) differ in the
`max_round` bound passed, not in the accounting — see §4.

**Conclusion: the gate input was already post-deduplication across the whole series.**
`cdsfl_topology_formal.md:210-215`'s MUST was already satisfied on the gate path.

---

## 2. The defect is real; only its blast radius was misstated

`novelty_counts[-1]` was rewritten post-reconciliation at `:9005–9013` — the current
round only. Measured on the archive: **236 of 287 (82%) MERGED entries carrying round
data were merged in a LATER round than they opened in**, so the single-position
correction reached 18% of merges.

The retroactive repair (`:9017–9046`) recomputes every position. Its consumers:

| Consumer | Site | Effect |
|---|---|---|
| ρ (`_compute_rho`) | `:8935`, defined `:1656` | rolling window of `novelty_counts[i]/raw_counts[i]` over `rho_rolling_window=3` |
| Endocrine module | `:9060`, `novelty_counts=novelty_counts` | per-round input |
| Checkpoint | `:9528` | persistence only |
| **γ gate** | — | **none. Does not read it.** |

### 2.1 ρ, measured

`rho_threshold=0.25`, `rho_rolling_window=3`, `rho_earliest_round=12`
(`bench/reference_runner_v2.py:478-479, 557`). Recomputed with the archived
`findings_count` as denominator and a fully post-deduplication numerator:

| run | ρ_avg archived | ρ_avg corrected | Δ |
|---|---|---|---|
| exp42 (12r) | 0.4266 | 0.2817 | −0.1449 |
| exp42 (2r) | 0.7273 | 0.5808 | −0.1465 |
| exp45 | 0.9246 | 0.6126 | −0.3120 |
| **exp46** | **0.3009** | **0.2176** | **−0.0833** |
| exp48 | 0.3056 | 0.1944 | −0.1112 |
| exp42 (7r), exp42 (16r), exp43, exp44, exp49 | — | unchanged | 0.0000 |

Direction is always down, as it must be: the correction only ever removes findings
from a round. **exp46 and exp48 cross below `rho_threshold=0.25` under the
correction.** Neither reaches `rho_earliest_round=12`, so no churn flag would have
fired either way — see §3.

---

## 3. NEW FINDING (OBSERVED): the churn detector cannot fire on most of the arc

`rho_earliest_round = 12` (`:557`). Rounds actually recorded:

| run | rounds | reaches R12? |
|---|---|---|
| exp44 | 13 | ✅ |
| exp45 | 4 | ❌ |
| exp46 | 6 | ❌ |
| exp47 | 9 (see §4) | ❌ |
| exp48 | 6 | ❌ |
| exp49 | 7 | ❌ |

**Only exp44 of experiments 44–49 reaches round 12.** For the other 5 the churn
indicator is structurally unable to fire regardless of ρ. OBSERVED in the archived
reports; not on the runway; proposed as a new Stage 1 item.

---

## 4. ANOMALY (OBSERVED): exp47's report and registry disagree on round count

`exp47_divergence_locationkey_live_20260728T230026Z`: the report's `rounds` list holds
**9** entries; registry entries carry `open_since_round` values up to **13**.

**Consequence, and a withdrawal.** A first pass of the ρ measurement showed exp47 as
the sole run where ρ *rose* (+0.2153). That is an artefact of comparing a 9-round
window against a 14-round registry. **The exp47 ρ rise is withdrawn — it is not a
measured effect.** The report/registry mismatch itself is real and goes to item 1.7.

---

## 5. exp46 — the flag raised in the session report is half withdrawn

| Claim | Verdict |
|---|---|
| exp46 converged at γ_crit 0.3357 vs threshold 0.30, margin 0.036 — narrowest in the arc | **STANDS** |
| exp46's γ moves 0.2910 → 0.3756 under the repair, so its verdict may be at risk | **REFUTED** |

exp46's critical series is `[4,2,3,2,1,0]` before *and* after the correction — every
entry was already settled. The 0.2910 → 0.3756 figures come from the **all-findings**
series, which the gate does not read. **No archived run changes its convergence
verdict under this repair.**

---

## 6. Item 1.5 — the starvation floor. Stands as reported.

`regulatory_t_v2` (`bench/immune_agents.py:4711-4726`) exempted the case where all
removals are duplicates. Sound reasoning — a high duplicate rate *is* depletion — but
with no floor, so total rejection also satisfied the exemption and reported healthy.

**OBSERVED:** every modern run records `rejection_rate` 1.0 from round 1; exp47 in
8 of 8 rounds. The monitor never fired.

**Status:** BUILT (`bench/immune_agents.py`), TESTED (8 in
`bench/tests/test_starvation_floor.py`, 4 verified to fail against pre-repair code),
COMMITTED (`dcbc91b`), ENABLED (not flag-gated).

First version was over-broad and intercepted genuine REJECTED removals; caught by
`test_rt_v2_bias_windowing.py::TestOtherChecksNotWindowed::test_combined_removal_rate_still_immediate`.
Narrowed to `elif rejected == 0 and total > 0 and removed >= total:`.

---

## 7. Runway consequences

- **Item 1.1 needs re-describing** in the runway tracker: it is a ρ/endocrine repair,
  not a gate repair. Its evidence column ("82% of merges land in a later round") is
  correct; its title is not.
- **Item 1.7** gains three questions: the ρ deltas above, the exp47 round mismatch,
  and the churn-earliest-round finding.
- **Item 1.6 (MERGED semantics)** is unaffected and remains the founder's decision.
  Alias map is a bijection in all 28 registries; no canonical entry has ever gained a
  second alias.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
