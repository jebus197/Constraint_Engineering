# Morning report, 2026-10-12 — the night of 11 October

**Window** 22:18–23:25 BST. **Branch** `sim/shakedown-2026-09-29`, HEAD `9ebf843b`.
**Audience: a reproducing engineer.** Plain-English companion:
`~/Desktop/CDSFL_tts/Morning_Report_2026-10-12.txt`.

## 1. Recovery is now mechanical — his ruling of 2026-10-11

*"You compacted, detected it after the compaction completed, and ran rs without my intervention
at all. If you could do this after every compaction event (again perhaps mechanically?) …"*

**Detection already existed; execution did not.** `compaction_watch.py` has detected compaction
structurally since 2026-09-08 (`"isCompactSummary": true`, byte-offset scan, acknowledgement
only a real restore clears). It *notified*. On 2026-10-11 a compaction landed, the notice fired,
the restore ran — and the session still spent most of a day recovering. He asked for a mechanism
and had a reminder.

`_auto_restore()` now runs `scripts/cdsfl_recover.py --record-restore` and injects its FIRST READ
block into context. **Once per compaction**, not per turn: the script writes `last_recovery`,
`_recovery_ran_after` reads it, the alarm self-acknowledges.

**It cannot fell the session.** Every failure path returns a string: missing script, timeout,
non-zero exit, unexpected exception. Verified — malformed stdin exits 0 silently; absent script
returns `DID NOT RUN … owed manually`; no-compaction transcript stays silent.

## 2. Saving refuses rather than runs — deliberately asymmetric

Restore is read-only → safe to execute unasked. `sv` **writes, commits and pushes** → a Stop
gate that refuses, in the shape of `ffafp_stop_gate.py`.

**Threshold derived, not shipped** — his own objection to a constant of 10 for the round cap,
applied here pre-emptively. Over 600 commits: **42 saves, median gap 2, p75 = 10.8, p90 = 22.9,
worst 267**. A fixed 3 would fire on **19 of 42 = 0.4524**, Wilson [0.3122, 0.6005] — noise, not
signal. The gate recomputes p75 at run time, clamped to `[FLOOR=4, CEILING=40]`.

Refuses **at most once per HEAD**. A gate that refuses forever gets switched off.

**Guard:** `bench/tests/test_recovery_and_saving_are_mechanical_2026-10-11.py` (12).
**Mutation:** neutering `_auto_restore` kills 3; restoring returns 12.

## 3. Item 13 — stranded work recovered, 2.49 GiB reclaimed

4 commits on `r3-parser-envelope` existing nowhere else: a self-locating field envelope, a
438-line producer, an 833-line guard (**78 passed**).

His caution applied **before** merging: absent from the sim branch, no equivalent exists, no
record of rejection. **18 conflicts, 22 hunks, all citation line-numbers** — verified by
normalising `.py:<n>` → `.py:N`. Resolved **hunk-by-hunk, not `--ours`**, which would have
discarded cleanly-auto-merged branch content in those same files. One carried a rename
(`<<<<<<< HEAD:path`) that the first pass missed.

**More than the 4 commits was in there:** a complete rubric-vs-proofs measurement (producer,
guard, adversarial record, notes) and 10 A19 probe scripts, all uncommitted. Each committed on
its own branch → object store. **All 5 branch refs intact** — deleting one is reserved to him in
person, and freeing disk does not require it.

## 4. Item 11 — 3 of 4 had landed; "0 of 4" withdrawn

`scripts/the_four_panel_lessons_2026-10-11.py`. **LANDED 3 of 4 = 0.7500**, Wilson
[0.3006, 0.9544].

| # | Lesson | Verdict |
|---|---|---|
| 1 | substance test on every reply | **NOT LANDED** — `accept_reply_or_work` called by 3 confer harnesses, **0 runners**; `runner_core.dispatch_to_model` returns `(text, elapsed)` unchecked |
| 2 | retry must not erase the attempt | LANDED, **better than the panel's** — dispatcher *accumulates* across attempts with `per_attempt` detail (fixed 2026-09-07: 7 calls then 2 logged as 2) |
| 3 | state detected, not declared | LANDED **in a different form** — `detect_target_kind` reads path and bytes; the panel's round-kind form has no runner analogue |
| 4 | one definition, not restated | LANDED — `verdict_is_substantive` is a free function whose docstring records the consolidation |

**Why "0 of 4" was wrong, twice:** patterns used `\|` (BRE) under `grep -E` → searched for a
literal pipe; then searched `reference_runner_v3.py` for the *panel's* symbol names rather than
the behaviour, in the wrong module.

**Lesson 1 is deliberately not rushed.** Wiring a substance test into
`runner_core.dispatch_to_model` changes what the live runner accepts as an answer, which is
convergence-affecting. Point identified; build it fresh.

## 5. Three faults in this night's own producer, caught by its own P-pass

A rigid regex reported a **line-wrapped** docstring absent minutes after it was read; the note
then **contradicted its computed verdict**; and the producer counted **itself** as an importer
of the symbols it audits — the same self-pollution as the inventory producer that morning. All
repaired; a check now asserts 0 note/verdict contradictions.

## 6. Open

Wire the substance test (point identified) · apply the 0.05 false-alarm proportion · the
per-run computed round recommendation · the human-review trigger · verify all 87 older
instructions · rebuild the domain-verdict measurement last.

---

# Later the same night, 23:00–23:15 BST — lesson 1 wired, item 3 pinned

**His correction, and it was right:** saying a change *"affects whether runs converge"* is not
saying it breaks convergence, and caution must not stand in for a measurement.

## The substance test, measured then wired

Across **2,582 archived runner replies** the predicate rejects **26 = 0.0101**, Wilson
[0.0069, 0.0147], exact [0.0066, 0.0147]. **20 of the 26 are EMPTY.** The remaining 6 are 2, 7,
191, 191 and 603 chars. **Exactly 1** would be rejected while carrying a finding — 191 chars,
1 finding, the holding-note case the test exists for. No panel needed; the archive answered it.

| Site | Applied? | Why |
|---|---|---|
| `_dispatch_single_model_inner` (primary seat) | **yes** | the reply he means |
| …its secondary fallback | **yes** | answers the same question |
| `run_preflight` | **no** | accepts `len(text.strip()) > 5` as proof of life; an 800-char floor fails every preflight |
| `_arb_dispatch` (:16152) | **no** | closure invoked indirectly; the 1 of 14 sites not inside `try/except` |

It **raises** rather than returning a sentinel because `dispatch_to_model` already raises on a
timeout and on a process exiting without a result. A hollow reply is the same class of event.

**Finding along the way:** `_report_dispatch_failure` is imported at
`reference_runner_v3.py:244` and **called nowhere** — an unwired import in the active runner,
and the reason no live reporting path existed to route a rejection into.

**P-pass:** 7 passed; disabling the check kills 2; the default path asserted byte-identical.
**501 passed** in the gate, so the behaviour change breaks nothing.

## Item 3 — `FALSE_ALARM_PROPORTION = 0.05`

*"Then yes. Do it that way. 0.05 is acceptable within this f[r]amework."* Pinned in the
division producer with his other 2 rulings; **0 live references** to relegation machinery in
the runner or routing. The *reasoning* is recorded beside the value and a test asserts it:
0.05 is right **because** ruling 4 fixes rankings at experiment start, moving demotion to
between experiments. If ruling 4 changes, this is revisited, not inherited.

## Why building stopped at 23:15

**The same predicate fault twice within an hour** — a contiguous search for a sentence that
wraps across 2 lines, first on the lesson-4 docstring, then on his quoted ruling. A repeating
error class inside an hour is what `feedback_long_session_degradation` names, so items 9, 12
and 14 were left rather than pushed through.

## All 4 remaining items complete

Work resumed after 23:15. 3 of the 4 items surfaced a defect in previously proposed or
delivered work, and in 2 cases the defect was in a proposal CC1 had made itself.

### Item 14 — the review of the older instructions

**92, not 87.** The earlier figure came from a narrower regex. Producer:
`scripts/his_older_instructions_triage_2026-10-11.py`.

A first extraction re-implemented the annotation predicate inline instead of calling
`read_founder_responses_2026-10-11.annotations()`, and admitted **2 markdown headings from a
saved Google Search page** as his words — the "one code path" lesson repeated within the hour
of learning it. The extraction now runs through the single definition and asserts no `.md`
heading can contribute.

**26 of 92, 0.2826, Wilson [0.2008, 0.3819], refer the fix to the model panel** — and his
wording escalates across the month, which is what a repeatedly-ignored instruction looks
like. 2026-08-29: *"The purpose of these multi model reviews is not just to find problems
(although that is clearly 50% of it), but also to suggest fixes."* 2026-08-31: *"Did you ask
the models? Or did you (again) just ask them to find problems"*. 2026-09-21: *"clearly you
keep missing things."* Beside that: 39 bare standing orders, 13 he deferred himself, 11
awaiting an explanation before he rules.

Spot-checked by execution, not reading: his 2026-08-31 order to strip personal and disability
directives is done and guarded (`test_live_spawns_do_not_inherit_operator_config_2026-08-31.py`,
9 green; `sim_dispatch_shim.py` carries his verbatim words at `--setting-sources ""`); his
2026-09-17 order to set the stalled valve to 6 is in all 3 `bench/exp56_configs/*.json` and
the value reaches `RunnerConfig` (confirmed by constructing the dataclass from the file, and
every ignored key is an `_`-prefixed annotation block); the Stop-hook repair is green at 21.

**The largest-looking open item is correctly parked.** His 2026-09-21 ruling that a
non-curing fix route back to the models is wired as `record` not `veto` on the measured 126 of
246; the 2026-10-03 attempt at the stronger form broke 2 committed oracles and armed a
deferred ruling. See [[cdsfl_withholding_verified_is_blocking_2026-10-03]].

### The board of guards dated on his instruction days: 4 failed, 1142 passed, 1 skipped, 237.09 s

105 files. Nobody had run that set.

**Failure 1 was CC1's, from the same evening, and would have muted the next simulated run.**
`require_substance` was added to `runner_core.dispatch_to_model` and not to
`bench/tools/sim_dispatch_shim.py`. That guard exists because on 2026-08-30 a mismatched shim
raised inside a bare `except` and read as a model returning nothing: **falsifier_code 0 of 19
against 23 of 39, Fisher p = 6.0e-06**. 2 live call sites pass `require_substance=True`. The
shim now carries and ENFORCES it (the module's own contract: *"THE ERROR CONTRACT IS PART OF
THE SEAM"*), executed in all 3 states.

**Failures 2–4 were instrument failures; the runner was sound.** `46617574` (2026-10-07) split
`_dispatch_single_model` into a 12-line wrapper over a 77-line `_inner`. AST at 3 revisions:
at `46617574^` 78 lines holding `_ASK_CORRECTED_COPY`; after, `_inner` holds that marker, the
"NO ask" announcement and the `dispatch_to_model` call, the wrapper none. **4th
`execute-do-not-grep` occurrence.** Repaired by `bench/tests/_delegation.py`, which follows and
CONCATENATES, so a marker deleted from both still fails and a rename fails loudly; 12-test
ratchet proves it can fail.

### Item 9 — the round recommendation, and CC1's own 2026-09-20 wiring was wrong

`bench/round_budget.py`: n* = (a/θ)^(1/γ) fitted per run; `round_budget_theta` is a config
field, named distinctly because `theta` was already bound to `gamma_alt_threshold`.

**Two γ estimators had one name.** The gate fits the CUMULATIVE series (`1 - slope`); the
formula needs the PER-ROUND intensity exponent. On exact counts at γ = 0.709 the intensity fit
recovers 0.709000 at every n; the cumulative returns **0.3525 (n=4), 0.4129 (n=10), 0.5121
(n=50), 0.6100 (n=500)** — the log-linear form drops the `-1` in
`N(n) = a(n^(1-γ) - 1)/(1-γ)`. Biased low by 0.30–0.36 at the 3–21 rounds actually run.

The proposal never said where `a` comes from (`_estimate_gamma` discards its intercept), so 3
wirings were available and **all 3 overestimate** against the correct 9.3695 on [5,3,2,2]:
**22.3759 (2.3882×)**, **71.5436 (7.6358×)**, **75.9566 (8.1068×)**.

**γ is not demoted and not touched.** `_estimate_gamma` and the 0.30/0.45 thresholds are a
matched pair on that estimator's scale. A guard asserts `round_budget.py` consults no gate
threshold and never calls `_estimate_gamma`; both γ appear side by side in one telemetry
record. Advisory: the gate's verdict is identical at θ = 0.1, 1.0, 100.0. `a = exp(α)·β` is
SymPy-verified; python/numpy/mpmath agree to 3.55e-15.

### Item 12 — the human-review trigger, refuted before it was built

`bench/human_review_trigger.py`. The elegant design (fire when n* > rounds remaining) was
tested against the archive FIRST: over 17 archived reports n* spans **151.64 to
1.79969828506e20 rounds**, firing on 16 of 17 including **4 of the 5 that converged**. The 5th
escaped only on a too-short series. Cause: convergence is the two-sided gate on CRITICAL
findings, not total yield below θ.

Signal A is DEDUCTIVE — with fewer than K rounds left, criterion (C) cannot be met by a
flawless run. **0 of 5 false alarms, Wilson [0.0000, 0.4345]; 12 of 12 on capped runs.** The
honest claim is 0 observed in 5. Signals B and C are statistical, so 2 are required. 0 of 17
reports carry a convergence field, so the label is DERIVED and marked as such. Producer:
`scripts/the_review_trigger_false_alarm_rate_2026-10-11.py`.

**A clean run is never flagged** — the fatal case, since 3 consecutive clean convergences is
the programme of study's success criterion. It inherits `_gamma_is_estimable` from his
2026-10-08 ruling, so γ's 0.0 SENTINEL is never read as "no decay". It halts nothing.

### Item 5 — the domain-verdict gap, and an error inside the correction

His ruling: *"If there is valid work to do, then you should do it."* Producer:
`scripts/the_domain_verdict_gap_2026-10-11.py`.

| domain | findings | settled rate | Wilson 95% |
|---|---|---|---|
| statistics | 1198 decided | 0.8656 | [0.8451, 0.8838] |
| software | 1313 decided | 0.7372 | [0.7128, 0.7603] |
| engineering | 62 decided | 0.6774 | [0.5537, 0.7805] |
| cs_software | 63 decided | 0.4286 | [0.3140, 0.5514] |
| chemistry | 37 decided | 1.0000 | [0.9059, 1.0000] |

Pooled 0.7897 (2111 of 2673); largest share 0.4912; shares sum to 1.000000. **`domain` is
RUN-level** — no finding record carries one. Excluded: 2099 records whose `status` is a test
outcome, 2774 duplicates across state file and report.

Withdrawn figures confirmed impossible exactly: implied share **9914312/14289591 = 0.693814**,
required rate **10592550459/1030160000 = 10.282432 > 1** (SymPy exact rationals, mpmath 30 dps).

**And the withdrawal was itself miscalculated** — the note gave 0.6142 and 14.6356, off by
0.0796 and 4.3532. The conclusion holds, so the withdrawal stands, but both wrong figures stay
recorded in the script. It now recomputes the refutation every run and exits 3 if any rate,
share or partition cannot be true — answering *"Ae you even checking if these numbers make any
practical sense before writing them"* mechanically. See
[[feedback_a_correction_needs_checking_too_2026-10-11]].

### A stale citation between 2 correct safety mechanisms

`experimental_notes/EXPERIMENT_RUN_LEDGER.md` cites a line in `reference_runner_v3.py` that had
drifted **238 lines**. Located at 3 revisions: correct at `40c4a154`, **already 174 stale at
this evening's starting HEAD**, 238 by the end — so the guard was red beforehand and 64 of the
drift is CC1's.

Neither repairer could fix it, both correctly. `citation_content_guard_2026-09-10.py` only
re-points a citation preceded by a backticked `def`/`class` whose AST span it reads; this points
at a COMMENT (it repaired 29 others the same evening). And `experiment_run_ledger.py` refuses to
rewrite on a checkout holding fewer artefacts than the ledger declares (44/31 against 56/31),
because that would delete rows existing elsewhere — the removal half of the additive standard.

**A row-protection refusal was blocking a citation repair, the 2 being bundled.** Now separable:
the refusal still fires, the derived citation is repaired anyway. Mutation-verified — set to
99999 it repairs to 18535 with all 55 table rows byte-identical; a correct citation leaves the
file untouched.

## A direct answer on saving from Word

**Yes, and no change of habit is required.** The reader handles both the RTF and the plain text
Word produces, including Mac OS Roman line endings and curly quotes. All 18 annotated files read
with **0 characters lost**, and `--verify` exits 3 if any annotated file cannot be read — the
silent failure was the actual defect.

## Open

1. **Item 8 — recovered and compared earlier this evening; the BUILD remains.** Not among the
   4, and the morning report's first draft wrongly called it "not started". The record of
   21:50 has it: the better way is **incremental stream-json parsing**, which beats a
   completion marker because a seat that has DIED never prints the marker either, and the
   clock cannot separate working from churning (**20.455 s vs 20.816 s per call**, measured).
   A live tool-call count separates all 3 states. Same work as the lapsed stream-json trigger
   — **1 build, not 2**. It touches `dispatch_to_model` and its ~20 callers.
2. **11 of the 92 await an explanation before he rules.** Answers owed, not work owed.
3. **The 26-of-92 panel referral** is the clearest actionable pattern in the review: a free
   `cc2` + `fable` panel briefed with proposed fixes rather than problems.

Board: 501 fast guards green; 338 across every γ and convergence guard; 204 across every guard
touching the simulation shim. Commits `a1014a47`, `8288b40b`, `6a2e87f0`, `45ba58b4`, `a4a5a4a6`.

---

*Written under CDSFL note standard v1.7.*
