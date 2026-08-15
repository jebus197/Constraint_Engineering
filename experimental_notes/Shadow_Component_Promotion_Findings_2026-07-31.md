# Shadow-component promotion: findings before any component was enabled

2026-07-31, 18:13 BST.

## Summary

Four dormant components were built, wired and tested for promotion out of shadow
status. None was enabled. An adversarial pass over all four downgraded two that
the building agents had marked ready. Three of the four carried defects that
would have produced a corrupted or misleading result had they been enabled
without testing. Two further defects were found by following those outward, one
of which has been silently damaging the archive since 2026-05-15.

Total dispatch cost: nil. Every claim below was established against the 293
findings already recorded across the six completed runs
(`bench/logs/exp4[4-9]_*`), or by executing the production functions directly.

The most consequential finding is not one of the four components. It is that the
convergence counter promoted to gating in sixteen configs is running in a mode
its own docstring, its own calibration test, and the plan that introduced it all
state it must not be used in.

---

## 1. Location-keyed convergence is gating in a mode its authors excluded

### 1.1 The mechanism

`_location_keyed_critical_series` (`bench/reference_runner_v2.py:2492`) counts a
critical as novel iff it names at least one code location not previously
flagged:

```python
locs = finding_locations(e.get("description", "") or "", symbols)
key = set(locs) if locs else {"<generic>"}
if key - seen:
    series[r] += 1
seen |= key
```

A second, genuinely distinct defect in an already-flagged function yields
`key - seen == ∅` and contributes **zero** — not a duplicate, not a downgrade.
Zero.

The promotion to gating is at `bench/reference_runner_v2.py:7085-7087`:

```python
if _gates and round_idx < len(location_crit_history) and novel_critical_history:
    # PROMOTED: the location-keyed count is the convergence trigger.
    novel_critical_history[-1] = location_crit_history[round_idx]
```

### 1.2 The prohibition, in three places

The function's own docstring (`reference_runner_v2.py:2493-2502`):

> `SHADOW (telemetry-only, NEVER gates)` … `NOT trusted to gate: the exact round
> is keying-dependent and location-only misses a 2nd distinct defect in an
> already-flagged function — live promotion is gated on a semantic splitter +
> null/seeded calibration.`

A dedicated test exists whose sole purpose is to demonstrate the blindness —
`bench/tests/test_convergence_location_calibration.py:94`,
`test_known_limitation_second_defect_same_function_is_missed`, asserting
`new == 0` with the comment that live-gating promotion is conditional on adding
the semantic splitter.

The plan that introduced the method
(`experimental_notes/Convergence_Consolidation_Plan_2026-06-08.md:214-215`):

> `Live-GATING remains future work (semantic splitter for 2nd-defect-same-function
> + a live confirmation run), per the adversarial verdict.`

**The semantic splitter was never built.** `location_keyed_convergence: true`
appears in sixteen configs: Exp 42, 43, 44, 45, 46, 47, the chemistry and
engineering exams, physics, biology, all four factorial cells plus the combined
factorial config, and the zero-plant control.

### 1.3 It fired twice, at closing rounds, on CONFIRMED criticals

Replaying the production counting rule over the recorded registries reproduces
the recorded `[0,0,0]` tails exactly:

| Run | Finding | Sev | Verdict | Opened | Converged | Locations named | Unflagged |
|---|---|---|---|---|---|---|---|
| Exp 45 | `C0031` | 0.75 | CONFIRMED | r3 | r3 | `ImmuneMemory`, `__init__`, `record_experiment` | none |
| Exp 47 | `C0070` | 0.85 | CONFIRMED | r13 | r13 | `check_sibling_admissibility`, `parse_alternative_block` | none |

Gate series, Exp 45: `[4, 0, 0, 0]` — tail `[0,0,0]`.
Gate series, Exp 47: `[5,3,1,0,1,1,0,0,1,0,0,0,0,0]` — tail `[0,0,0]`.

`C0031`: `ImmuneMemory.__init__` does not validate `decay_rate`; a negative
`decay_rate` makes `math.exp(-self.decay_rate)` in `record_experiment` exceed
1.0.

`C0070`: `check_sibling_admissibility` strips contrast statements before checking
sibling and cross-round recidivism isomorphism, because
`parse_alternative_block` removes the contrast statement from `alternative_text`
— so the comparison compares the wrong text.

Both are CONFIRMED, both landed at the exact round the gate closed, both counted
as zero. No other completed run shows a confirmed critical opening at or after
its convergence round (Exp 44, 46, 48, 49: zero such findings).

### 1.4 Scope of the consequence

Nothing was lost. Both findings are demonstrated and recorded in their
registries. What is not true is the claim attached to those two convergences.
"Three consecutive rounds with zero new criticals" meant, in those runs, "zero
new criticals in previously unmentioned code locations" — a materially weaker
statement.

Only three of the six completed runs closed on this gate at all; the other three
closed on the state gate. Tightening this path alone changes nothing for half of
them.

### 1.5 The splitter is NOT a cheap composition — measured, and refuted

The obvious hypothesis was that the missing splitter is mostly already built:
`bench/dm/_similarity.py` provides `finding_similarity` (embedding backend,
sentence-transformers available on this machine) and `jaccard_similarity`
(lexical), with calibrated thresholds `tau_sim_embed ≈ 0.55` and
`tau_sim ≈ 0.33`. Composing location with similarity would then be a small
change: a critical is novel iff it names an unflagged location **or** it is
dissimilar to every prior critical at the locations it does name.

Tested against all six completed runs at zero cost. **The hypothesis is refuted
in both directions.**

*Embedding backend.* Against priors sharing a location, the two target findings
score:

| | max similarity vs prior at same location | verdict at τ=0.55 |
|---|---|---|
| Exp 45 `C0031` | 0.684 (`C0022`), 0.676, 0.639 | REPEAT — still missed |
| Exp 47 `C0070` | 0.781 (`C0053`), 0.769, 0.703 | REPEAT — still missed |

Both far above threshold. Embeddings of findings about the same function in the
same codebase are uniformly close — the backend captures *same topic*, not *same
defect*. This is the anisotropy the module's own docstring documents.

*Lexical Jaccard.* The same pairs score 0.081 and 0.152 — comfortably below
τ=0.33, so Jaccard **correctly calls both NEW**. But replayed across the archive
it destroys convergence in **all six runs**; every closing tail becomes non-zero:

| run | location-only tail | location + Jaccard tail |
|---|---|---|
| Exp 44 | `[0,0,0]` | `[1,1,0]` |
| Exp 45 | `[0,0,0]` | `[4,0,1]` |
| Exp 46 | `[0,0,0]` | `[2,1,0]` |
| Exp 47 | `[0,0,0]` | `[1,0,1]` |
| Exp 48 | `[0,0,0]` | `[0,1,0]` |
| Exp 49 | `[0,0,0]` | `[1,0,0]` |

Models reword re-finds enough that lexical overlap collapses for genuine repeats
too — which is precisely why location keying was introduced. Lowering τ to admit
0.081 would make it more permissive still, the wrong direction.

One comparator says everything is the same defect; the other says everything is
different. **Neither threshold sits anywhere useful.** The June plan was right to
call the splitter future work, and option 1 below is confirmed expensive rather
than cheap.

### 1.6 Options

1. **Build the semantic splitter.** The stated precondition. §1.5 establishes it
   is genuine new work, not a composition of existing parts — neither available
   comparator can serve.
2. **Revert to the settled ID-proxy series.** Would have refused two of the three
   γ-alt convergences (LOO margins 0.136–0.137 against 0.018 reconstruction
   uncertainty). Longer, dearer runs.
3. **Continue and declare.** Record in the results and any paper that convergence
   here means no new criticals at unflagged locations.
4. **Post-hoc audit — BUILT, zero cost.** The blindness only bites when a
   CONFIRMED, still-unresolved critical opens in the closing window. That is
   checkable exactly, after the fact, on every run. Implemented as
   `bench/audit_closing_window.py`; tests in
   `bench/tests/test_audit_closing_window.py` (13, falsifiable — removing the
   resolved-status filter turns 2 red).

   Over the whole archive it flags **2 of 36** runs: Exp 45 and Exp 47, exactly
   the known cases. Selectivity is load-bearing and was got wrong first: the
   initial draft flagged 7 of 36 by counting criticals that were demonstrated
   **and resolved** inside the window, which is the ladder working, not failing.
   The filter that distinguishes them is the whole value of the tool.

   It changes no gate and no verdict. It removes the silence.

Options 1 and 4 compose; so do 3 and 4. Given §1.5, the recommendation is **4 now,
plus 3 in the write-up**, with 1 scheduled only if the arc's budget allows.

**Founder ruling required on 1/2/3. Option 4 is already in place.**

### 1.7 A completed report does not record which rule closed the run

Found while building the audit. The run report stores `convergence_config` with
exactly four keys — `earliest_stop`, `consecutive_required`, `rho_threshold`,
`rho_rolling_window`. It does **not** record `location_keyed_convergence`, and it
does not record `gamma_alt_consecutive_zero_crit`.

`convergence_reason` names the path and quotes the tail, e.g.

> `CRITICAL_QUIESCENCE_CONVERGED (two-sided gate): gamma_critical=0.621 >= 0.3 …
> AND 3 consecutive zero-new-critical rounds (history tail=[0, 0, 0]) at round 3`

— but not which series produced that tail. Worse, the report writes the location
series under the key `location_crit_shadow_history`, still called *shadow*, in
runs where the config had promoted it to gating.

So determining which counting rule closed a completed run requires going back to
the launch config file. The report is not self-describing on the single most
important input to its own convergence decision, and its key name actively
misleads. The audit therefore infers the gate and marks the inference with a `?`
rather than asserting it.

Not fixed here: fixing it means changing the runner, which cannot retro-fill a
completed record. Recommended for the next runner change, before any further run.

---

## 2. ImmuneMemory consumption would have coupled the factorial

### 2.1 The defect

Consumption shipped gated on `immune_memory_enabled`, which is `true` in eleven
configs — verified directly, not from a report:

```
exp47_configs/47_divergence_locationkey_live.json   exp48_configs/48_chemistry_exam_live.json
exp49_configs/49_engineering_exam_live.json         exp50_configs/50_physics_exam_live.json
exp51_configs/51_biology_exam_live.json             exp52_configs/52_factorial_cell_A.json
exp52_configs/52_factorial_cell_B.json              exp52_configs/52_factorial_cell_C.json
exp52_configs/52_factorial_cell_D.json              exp52_configs/52_factorial_live.json
exp53_configs/53_control_zero_live.json
```

None was written with any intention of consuming a prior. Because
`ImmuneMemory` accumulates between runs, cell D's `R_k(0)` would depend on cells
A–C having already run. The 2×2 factorial's entire comparison rests on cell
independence. The zero-plant control would likewise inherit a prior shaped by
three earlier experiments — an uncontrolled variable inside the one instrument
built to have none.

Neither would have announced itself. Both runs complete and produce numbers.

### 2.2 The fix (applied)

`immune_memory_enabled` retains its meaning — **recording**. A new
`immune_memory_consume_rk0: bool = False` governs **consumption**
(`reference_runner_v2.py`, `RunnerConfig`). `_build_rk0_prior` now gates on the
new flag. Both config-ingestion paths carry it — `RunnerConfig.from_dict` and
the launcher whitelist at `bench/launcher_core.py:233`, the latter being the
failure class that has bitten five times.

Report emission now distinguishes the two states that previously read
identically: `rk0_consumed` (bool, the switch) beside `rk0_priors_used` (the
receipt). `consumed=True` with an empty receipt is the "wired but reaching
nothing" state; `consumed=False` is a deliberate abstention.

### 2.3 Verification

`bench/tests/test_immune_memory_consumption.py`, class
`TestRecordingAndConsumptionAreSeparateSwitches` — 7 tests. Falsified by
restoring the original gating in a scratch copy: **4 of 7 fail against the
defect, 7/7 pass after the fix.**

Two of those four were initially written to inspect the config field and passed
against the defect — the same blindness that let it through, since under the
defect the field reads `False` while the builder consumes anyway. Rewritten to
build each shipped config through the real launcher path and interrogate
`_build_rk0_prior` itself. A third was vacuous as first written
(`cfg.get(K) is True and K not in cfg` is unsatisfiable) and was replaced.

Nothing in the current queue consumes. Whether to enable it anywhere is a
founder decision; the prior work (2026-07-22) records it as useful at BR2 scale.

---

## 3. Literature retrieval: one character, three boundaries

Text extracted from PDFs can carry a **lone surrogate** — U+D800–U+DFFF, the
unpaired half of a UTF-16 pair. U+D835 is the common case: the high half of the
mathematical-alphanumeric block, so it occurs in exactly the papers the
retrieval cell fetches. Python stores it; UTF-8 refuses it.

Three boundaries measured, all three real:

| Boundary | Result | Cost |
|---|---|---|
| `subprocess` stdin (CC2, Codex) | `UnicodeEncodeError` | **kills the round mid-run** |
| log file write | `UnicodeEncodeError` | kills whatever logs it |
| run report (`ensure_ascii=False`, strict) | `UnicodeEncodeError` | run completes, no report |
| JSON request body | survives | only via `ensure_ascii=True` escaping |

The original diagnosis named only the report. The prompt path is worse and was
missed.

**Fixes applied.** Root: `bench/text_safety.py` — `scrub_surrogates` /
`scrub_deep`, scrubbing at ingest so one guard covers all exits. Clean text is
returned as the *same object*, so the common path allocates nothing.
Defence-in-depth: `_write_report_json` (`reference_runner_v2.py`, replacing three
raw writes — the final report and both HIL partials). Its ordinary path is
byte-identical to a strict write, asserted; substitution fires only on failure
and records itself in the report under `_text_sanitised`.

Tests: `bench/tests/test_text_safety.py` (20), `test_report_write_survives_pdf_text.py`
(9). Both assert the failure modes as facts about Python, so they go stale
loudly. The falsification that mattered: U+1D6FE (`𝛾`) is **one** codepoint in
Python, not a surrogate pair, so the guard cannot corrupt legitimate mathematical
symbols — asserted explicitly.

**Still open before enabling injection:** `_target_to_query` (10-keyword cap
severing multi-word terms; label prefix; code identifiers fed to academic
search). Under repair in a parallel workflow, with the librarian bake-off.

---

## 4. Severity calibration: works, does not earn promotion

Built its missing producer, then evaluated against all 293 recorded findings.
Its own verdict, upheld by the adversarial pass after reproducing the numbers:
**do not enable.** It does not improve severity honesty enough to justify the
distortion risk against the governing `pass_condition`.

This satisfies the standing instruction — use it only if it produces
demonstrably useful results. It does not. It stays off, tested, with the
reasoning recorded.

---

## 5. The test suite has been writing into the archive since 2026-05-15

`bench/immune_agents.py:3219` attaches a `FileHandler` to
`bench/logs/immune_pipeline.log` at **import** time. Every pytest run imports the
module, so every pytest run appends synthetic pipeline output — `TestModel_F001`,
toy targets, fixture findings — into the file holding real experiment history.

**332 such lines**, continuously from 2026-05-15T21:52:18 to 2026-07-31T17:15:40.
Nothing in the file marks any of it synthetic; separating fixture noise from run
history requires inspecting model names line by line.

`bench/logs/` is archival — never edited, corrections filed as sidecars. The test
suite has been violating that rule silently for two and a half months. Found by
`git status` showing the archive dirty after a test run that touched nothing.

**Fix applied.** Under pytest the shadow log is redirected to a scratch directory;
`CDSFL_SHADOW_LOG_DIR` overrides in both directions. Tests:
`bench/tests/test_archive_is_not_written_by_tests.py` (4), falsified by disabling
the redirect — 2 of 4 fail against the defect.

**The existing 332 lines are left in place.** They are interleaved with genuine
records, and rewriting an archive to tidy it is what the rule forbids.

**Founder note.** The uncommitted delta on that file is 1,597 lines: 25 from
2026-07-29 (the halted control run, legitimate), 102 from 2026-07-30, and 1,502
from today, the bulk of which is test noise predating the fix. Committing it
commits the noise permanently. Not committing leaves the working tree dirty.
Ruling needed; no action taken either way.

---

## Method note

Every defect here was found before anything ran. The pattern of the week held:
each component was correct in isolation and broke against something it had to
coexist with. Two of the four were self-reported ready and downgraded only when a
separate pass reproduced the work instead of reading the reports.

The ImmuneMemory coupling was invisible from inside the component. It was
findable only by asking which shipped configs already carried the flag — a
question about the system, not about the change.

An earlier circulation of the plain-English companion carried two errors in §1,
since corrected: prior-flag counts of "fourteen and eleven" that matched nothing,
and a description that split one finding into two. The substance was unaffected
and is now firmer, having been reproduced by executing the production counting
function over the recorded registries.

---

Written under CDSFL note standard v1.2 (14 May 2026).
