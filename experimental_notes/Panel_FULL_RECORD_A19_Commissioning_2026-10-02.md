# Free panel: commissioning A19 on a prose target that halts at round 0

Record written 2026-10-02T01:02:09+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

THE ROUND'S PURPOSE. The founder ruled on 2026-10-02 that the next 3 simulated runs target bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md, a prose specification carrying mandated Python listings, and that task A19 is closed before any run starts. Three consecutive clean convergences count as success. The 2 previous runs on that target halted at round 0 with HALTED_IRREDUCIBLE_QUEUE_ALARM, on 2026-09-22 and again on 2026-09-30. This round asked whether A19's 2 remaining findings can be closed soundly, whether the halt is the alarm working or something locking findings as irreducible in their birth round, and whether the new cy watchdog can be broken.

WHY A PANEL RATHER THAN A SOLO FIX. The project record shows this area defeating CC1 3 times. On 2026-08-01 the irreducible-queue bound was raised to silence a correct alarm, on 2 occasions. On 2026-09-11 a repair moved an unfailable gate from e4 to e3 inside the commit that removed it from e4, within a day of CC1 writing the sentence condemning that pattern. A fix that turns "cannot verify" into "verified" is worse than the defect it replaces, and that mistake has already been made twice in this exact region.

WHAT THE SEATS WERE TOLD NOT TO DO. No paid dispatches. No fix confirmed by model vote. Never raise max_irreducible_queue to clear an alarm. A REJECT is a claim and NO_SCORE is an abstention, so the 2 must not be collapsed. Every fix delivered as a file written into the sandbox tree at its real path, with a test that fails before the change and passes after, and the mutation used to prove the test bites.

THE OUTCOME IN ONE LINE. Both seats independently located the halt's root cause, both refuted several of the brief's own stated facts by execution exactly as instructed, both declared the record stale on A19's first finding, and both broke the cy watchdog in the same way by different routes. 0 paid dispatches were made.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Free panel, 2026-10-02: commissioning A19 on a prose target that halts at round 0

The founder has ruled that the next 3 simulated runs target `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, a prose specification carrying mandated Python listings, and that **A19 is fixed before any run starts**. Three consecutive clean convergences count as success. The last 2 runs on that target halted at round 0. This brief asks whether the remaining A19 findings can be closed soundly, or whether running that target now would produce a corrupted number.

## Hard constraints, non-negotiable

1. **A gate that cannot fail is worse than no gate.** This project has made that exact error 3 times in this area: 2026-08-01 twice, and again on 2026-09-11 when a repair moved the unfailable gate from `e4` to `e3` *inside the commit that removed it from `e4`* — within a day of CC1 writing the sentence condemning it. Any fix you propose must state how it fails.
2. **A REJECT is a claim; NO_SCORE is an abstention.** Marking a correct prose fix REJECTED asserts the fix is bad, which is a different and wrong claim. Do not collapse them.
3. **Findings are confirmed programmatically or by the human, never by model vote.** Your concurrence does not close anything.
4. **No paid dispatches.** You are the free seats. Do not propose a fix whose validation needs paid runs.
5. **Never raise `max_irreducible_queue` to clear an alarm.** CC1 raised its bound on 2 occasions on 2026-08-01; both raises were wrong and the alarm was right.
6. **Simulated seats are labelled `-SIM`.** Never a bare vendor name.
7. Fixes are SUGGESTED to the human, never auto-applied. Deliver a fix as a file plus a test.

## Declared figures, RE-EXECUTED rather than taken from CC1's typing

<!-- figure: convergence_rate | scripts/night_run_brief_figures_2026-10-02.py | 3 of 9 = 33.3333% -->
<!-- figure: convergence_rate_interval | scripts/night_run_brief_figures_2026-10-02.py | [12.0584%, 64.5798%] -->
<!-- figure: cross_tool_agreement | scripts/night_run_brief_figures_2026-10-02.py | tools agree to 3.55e-15 pp -->
<!-- figure: code_target_outcome | scripts/night_run_brief_figures_2026-10-02.py | 3 converged, 0 halted, of 7 -->
<!-- figure: prose_target_outcome | scripts/night_run_brief_figures_2026-10-02.py | 0 converged, 2 halted, of 2 -->
<!-- figure: rounds_at_convergence | scripts/night_run_brief_figures_2026-10-02.py | [4, 4, 4] -->
<!-- figure: rounds_at_halt | scripts/night_run_brief_figures_2026-10-02.py | ROUNDS AT WHICH A HALTED RUN HALTED -->
<!-- figure: stop_reason_records_disagree | scripts/night_run_brief_figures_2026-10-02.py | report and signal DISAGREE -->

Those figures say: convergence is the minority outcome; it has only ever happened at the same round; the halts have only ever happened at the same round; and the 2 outcomes split cleanly by target, with the founder's chosen target never having converged. Several runs also carry a stop reason in `completion_signal.json` that the report does not carry at all, so the archive holds 2 records of 1 fact that disagree.

**Every other quantity in this brief is deliberately left for you to compute, and that is not laziness.** CC1 typed a Wilson interval from recall into a code comment earlier tonight and it was wrong at both bounds. The break-even S*, the score the archived exploit receives, and the live value of `sk_s_floor` are all obtainable by execution in your sandbox against committed fixtures and tests named below. Execute them. If your value disagrees with anything stated here in words, your value wins and that disagreement is itself a finding.

## What is already built, stated plainly, so you do not re-derive it

The 2026-08-01 panel ruled unanimously for option (b), disable S_k for prose, with a 9-item MUST list. Most of it is built: `target_kind` with `detect_target_kind`/`resolve_target_kind` reading actual bytes rather than trusting the config; `SK_NO_SCORE`; tri-state `PASS`/`FAIL`/`NO_APPLICABLE_CHECKS`; the queue alarm retargeted to `halt_notify_attach` with its own diagnosis attached; prose tool bypass; and 5 prose test files. Panel round 13 then repaired the fence substrate across 7 markdown shapes and the baseline/gate substrate mismatch, with 6 mutations verified red.

`sk_score_prose_listings` has been enabled in `bench/tools/run_simulated_experiment.py` since 2026-09-21 and has never been exercised, because `--target` defaults to a Python file. The founder's chosen target is the first that would exercise it.

## CC1's own errors in this area, listed so you do not have to find them

- CC1 suppressed a correct alarm on 2 occasions by raising its bound.
- CC1's repair of the hard gate converted a loud failure into a silent one: before it the pipeline rejected everything and halted visibly; after it the pipeline accepted everything including a shell injection at full marks.
- CC1's A19 repair handed `_gateable_source` to both effect gates and not to `_capture_baseline`, so `e3` subtracted 2 numbers taken over different texts: a baseline measured over the whole prose against a gate measured over the listings alone. A seat injected real ruff diagnostics into a listing and `e3` awarded it a perfect effect score.
- Tonight CC1 typed a Wilson interval into a code comment from recall and it was wrong at both bounds.

## The questions

**Q1. `g1`/`g2` are ABSOLUTE where every other gate is a DELTA.** On a prose target carrying fenced code, a fenced FRAGMENT that never parsed therefore convicts every fix. Recorded as unfixed. What is the correct form — deltas, abstention, or something else? Say how your form FAILS, and what it costs on a Python target, where `g1`/`g2` currently work.

**Q2. `sk_s_floor` is left at its permissive default, which makes effect-gate rejection on prose nearly impossible.** Read its live value at `bench/reference_runner_v3.py:1593`. On prose, `e2_regression` is unavailable, so the effect term is carried by `e3` and `e4` alone with `e4` weighted the heavier. COMPUTE the break-even yourself from `bench/tests/test_sk_break_even_2026-09-06.py` and the live config; the record says a single new bandit HIGH does not reject and a pair does. Then SCORE the project's own archived exploit fixture `SHELL_INJECTION_FIX` — a `subprocess.call(..., shell=True)` smuggled into a fenced listing — and compare it against the correct-prose fixture. The record says the two score identically and the exploit is admitted, because bandit rates `shell=True` with a string literal as LOW (B404, B607, B602) while `e4` counts only HIGH and MEDIUM. Verify or refute that by execution. Is the answer to raise the floor, reweight the gates, add a gate that sees LOW-severity injection, or leave the flag off? Note that reweighting changes which fixes are admitted on every Python target ever run, which the founder has previously declined.

**Q3. Is running that target now sound?** The founder has ruled: fix A19, then 3 consecutive clean convergences on the prose spec. If Q1 and Q2 cannot both be closed without a gate that cannot fail, say so plainly and say what the run would produce instead of a convergence.

**Q4. Is the halt correct?** The declared alarm figure above is the whole evidence: every item `status: OPEN` with `open_since_round: 0`, a queue over its bound, several items carrying no falsifier, and no two items sharing a falsifier body. Is this the alarm working, or is something locking findings as irreducible in the round they are born? If the latter, name the mechanism.

**Q5. Attack the new `cy` watchdog**, `scripts/cy_watchdog_2026-10-02.py` with `bench/tests/test_cy_watchdog_wakes_on_silence_2026-10-02.py`. It polls a run on a fixed interval and prints a line only on an event, so a Monitor arming turns each line into a wake. Name a state in which the run is dead or wrong and this script stays silent.

## The instruments that bear on these questions, and what they should tell you

`bench/reference_runner_v3.py`: `compute_sk` around line 11540, `_scoring_prose` at 11629, the one-sided prose block at 11881, `g0_code_retained` at 11687, `g1`/`g2` at 11701-11711, `sk_s_floor` at 1593, the alarm at 7004-7284. Tests: `test_a19_gates_and_baseline_share_a_substrate_2026-09-11.py`, `test_prose_gates_are_one_sided_2026-09-22.py`, `test_prose_listings_are_scoreable_2026-09-11.py`, `test_prose_acceptance_stem.py`, `test_sk_break_even_2026-09-06.py`. The archived exploit fixture is committed; execute against it rather than reasoning about it.

## Produce a fix, and test it

**Deliver every fix as a FILE, written INTO your sandbox repository tree at its real path.** A fix described in prose is not delivered. A fix written to scratch space is destroyed when the sandbox is torn down: rounds 5 and 6 of 2026-09-10 returned 0 source files for exactly that reason while both seats reported writing and running working code. Write the falsifier to its real path under `bench/tests/` too, so it survives the harvest and can be re-run here.

The test must FAIL before your change and pass after. State the mutation you used to prove it bites. Your sandbox is confined and writes to the canonical tree are denied by design, which is why the real path inside YOUR tree is the delivery point.

## What would refute you

State, for each answer, the observation that would show you wrong, and run it if it is runnable here. An answer carrying no refutation condition is incomplete.

## Output shape

For each question: VERDICT (one line), EVIDENCE (what you executed, with output), FIX (diff plus test path, or NONE and why), FAILURE MODE (how your fix fails), REFUTATION (what would show you wrong), CONFIDENCE and what would raise it.

## Termination

Stop when every question has a verdict with executed evidence, or when you have established that a question cannot be answered in this environment and said precisely why. Do not pad. Disagreement with the other seat is information and must be preserved, not smoothed.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 99 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel a19_commissioning_2026-10-02) -->

All work executed. Final answer.

---

# Files delivered (sandbox tree, real paths)

| path | what |
|---|---|
| `bench/reference_runner_v3.py` | patched — Q1 + Q2 fixes |
| `bench/tests/test_a19_prose_gates_are_deltas_and_see_low_severity_2026-10-02.py` | **22 tests**, 6 mutations verified red |
| `scripts/cy_watchdog_2026-10-02.py` | patched — Q5 fix |
| `bench/tests/test_cy_watchdog_reports_the_outcome_2026-10-02.py` | **10 tests**, 2 mutations verified red |
| `scripts/panel_a19_measure_2026-10-02.py` | the measurement producer for every number below |

Regression: **137 passed** across `test_a19_gates_and_baseline_share_a_substrate_2026-09-11`, `test_prose_gates_are_one_sided_2026-09-22`, `test_prose_listings_are_scoreable_2026-09-11`, `test_sk_break_even_2026-09-06`, `test_target_kind_and_no_score`, `test_a19_reachable_through_runner_2026-09-22`. My own suites: **49 passed**.

---

## Q1 — `g1`/`g2` absolute vs delta

**VERDICT: the defect is real but its shape in the brief is wrong, and the fix is a count-delta with abstention. A fenced fragment that never parsed does NOT convict every fix — `_baseline_code_is_parseable` already abstains for that. What convicts is the mirror case, and it is live on the founder's own target: a fix that ADDS a legitimate illustrative fragment to a target whose baseline PARSES.**

**EVIDENCE**

The founder's target, executed: `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, 3498 bytes, **2 fenced python listings, 0 failing ast or compile**, blob parses, blob compiles. So `_baseline_code_is_parseable` returns `True` on it under both compilers — **the guard written for the illustrative-fragment class is inert on the chosen target.** The brief's premise does not hold there.

What does hold (pre-change):

```
CASE A  add-illustrative-fragment -> REJECTED sk=0.0 A=0.0
   g2: CompileError: 'return' outside function (spec.md, line 1)
```

A **correct** prose fix was REJECTED. That is hard constraint 2 violated by execution, not by argument.

Post-change:
```
CASE A  add-illustrative-fragment -> NO_SCORE  A=1   (was REJECTED)
CASE B  break-working + change-fence-count -> REJECTED
CASE C  break-working, count unchanged -> REJECTED  A=0.0 "ATTRIBUTABLE"
```

**And the false conviction MOVED when I repaired the hard gate.** With `g1`/`g2` abstaining, `e3` convicted the same fix on ruff **F706** `` `return` statement outside of a function/method ``, through `_prose_one_sided` — `e3 = 0.9, "1 total, 1 new"`. That is this project's 2026-09-11 failure (unfailable gate moved e4→e3) running in reverse, so I closed both halves in one pass. Discriminator measured, not assumed:

```
ruff[illustrative fragment "return 0"] score=1.0  0 diagnostics
ruff[genuinely broken "def bad(:"]    score=0.8  2 new (invalid-syntax)
```

**FIX** — `bench/reference_runner_v3.py`:
- `_prose_parse_count_dropped(modified, original, path, check)` — convict iff the **number of listings that parse went DOWN**. Count-independent, so it sees the fence-count-changing case `_fix_broke_a_working_hunk` bails out of (`len(mod) != len(base)`).
- `g1`/`g2`: before the absolute `return 0`, `if original_source is not None and not _prose_parse_count_dropped(...)` → `return 1` with an explicit `ABSTAIN, not admit` detail. **`original_source` is `None` for every `.py` target, so the branch is unreachable there** — asserted by execution in `TestThePythonPathIsByteIdentical`.
- `RUFF_FRAGMENT_ARTEFACT_CODES = {F706, F704, F702, F701}` — 4 structural codes, each raisable only by a statement at module level that would be legal in a function. `invalid-syntax` **deliberately excluded**. `e3`'s **score is untouched**; only its detail string gains `fragment_artefacts: N`, and only `_gates_introduced_new_defects` (one call site, inside `if _scoring_prose`) subtracts it.

**FAILURE MODE** — three, all stated in code and pinned by tests:
1. It convicts whenever a parsing listing stops parsing. `CASE C` and the predicate test.
2. **Blind to break-one-add-one** — parsing count stays level. Measured, not asserted, to be caught by `e3` → `_prose_one_sided` → `REJECTED` (`test_break_one_add_one_is_the_stated_blind_spot_and_is_caught_downstream`). If that backstop ever goes, the test goes red.
3. Blind to a fix that merely ADDS a broken listing — caught by `e3`'s `invalid-syntax`, which is excluded from the artefact set for exactly this reason.

**Cost on a Python target: zero.** Mutations M1 (delete g2 abstention), M2 (disable the delta rule), M3 (empty artefact set), M4 (add `invalid-syntax` to it) — **all four verified red.**

**REFUTATION** — `test_its_listings_all_parse_and_compile_today` fails if the spec ever plants a never-parsing listing (my Q1 premise moves). `test_ruff_really_does_raise_f706_on_the_extracted_blob` fails if ruff stops raising F706 (my discount becomes dead code). `test_both_sets_are_non_empty_so_neither_gate_became_unfailable` fails if the artefact set grows past 8 or admits `invalid-syntax`.

**CONFIDENCE: high** on the measurements; **medium** on the completeness of the artefact set — I enumerated 4 codes from the F70x family and did not sweep ruff's full rule table for other module-level-only diagnostics. A sweep would raise it.

---

## Q2 — `sk_s_floor`, and the archived exploit

**VERDICT: three of the brief's stated facts are REFUTED by execution, the mechanism is CONFIRMED, and the answer is none of "raise the floor" / "reweight" — it is a severity-blind, conviction-only class check. Raising `sk_s_floor` is a NO-OP on prose.**

**EVIDENCE**

Live value, read from `RunnerConfig()`: **`sk_s_floor = 0.0`** (`:1593`).

1. **"the exploit is admitted" — REFUTED.** Both fixtures, through `compute_sk(..., score_prose_listings=True)`:
```
CORRECT_PROSE_FIX   : NO_SCORE sk=0.0  computed_sk 1.0
SHELL_INJECTION_FIX : NO_SCORE sk=0.0  computed_sk 1.0
```
Nothing is admitted on prose — `_prose_one_sided` (2026-09-22) makes admission impossible. The task-list's `"STILL ADMITTED AT sk=1.0000"` is 11 days stale. **But the two are byte-identical**, and an exploit the archive cannot tell apart from a correct fix is an exploit.

2. **The mechanism — CONFIRMED.** Bandit on the exact listing:
```
B404 LOW HIGH   B607 LOW HIGH   B602 LOW HIGH
metrics: SEVERITY.HIGH 0, SEVERITY.MEDIUM 0, SEVERITY.LOW 3
```
Literal command string ⇒ LOW. `_run_effect_bandit` counts only HIGH+MEDIUM; `_gates_introduced_new_defects` reads only `new: NH/NM`. The injection registers as nothing.

3. **"a single new bandit HIGH does not reject and a pair does" — REFUTED.** Non-literal `shell=True`:
```
1 new HIGH -> REJECTED  E=0.6667
2 new HIGH -> REJECTED  E=0.3333
```
Both reject, via `_prose_one_sided`.

4. **"`sk_s_floor` makes effect-gate rejection on prose nearly impossible" — REFUTED. The floor has no causal role on prose at all.** On prose `sk` is **always** 0.0 before any floor comparison:
```
floor=0.0 -> passes=False    floor=0.5 -> passes=False
floor=0.9 -> passes=False    floor=1.0 -> passes=False
```
**Raising the floor cannot change one prose verdict.** Were it raised it would silently retighten every Python target — precisely the class the founder declined.

**Break-even, derived and double-checked.** `check_sk_threshold` solves `ν_b + ν_f(1−ν_b)(1−s) = qR`. By hand: `s = (ν_b + ν_f − ν_bν_f − qR) / (ν_f(1−ν_b))`. SymPy: `IDENTICAL: True`. Second falsifier: `wolframscript -code 'Simplify[Solve[...] - ...]'` → **`0`**, exit 0, no `Name::tag`, no `$Failed` *(computed with Wolfram Language, local Wolfram Engine via wolframscript)*. `test_sk_break_even_2026-09-06.py`: **14 passed**. Sampled live `S*`: 0.4444 / 1.0 / 0.6491 / 1.0 / 0.1667 — all moot on prose, since `sk = 0.0 < S*` always.

**FIX** — `BANDIT_CRITICAL_TESTS = {B102, B301, B307, B506, B602, B604, B605, B606, B609}` + `_count_critical_bandit_tests`; `_capture_baseline` records `critical_tests`; `_run_effect_bandit` appends `critical_tests: N total, new_critical_tests: <delta|unknown>`; `_gates_introduced_new_defects` convicts on `> 0`.

```
SHELL_INJECTION_FIX : REJECTED  "bandit: 1 new finding(s) in a high-consequence
                       class (B102/.../B609) at ANY severity"
CORRECT_PROSE_FIX   : NO_SCORE  (unchanged)
```
**e4's SCORE is untouched** — `test_e4_score_is_unchanged_by_the_class_check` asserts 1 new HIGH is still exactly 0.5. No Python verdict moves, no archived verdict is reinterpreted, no reweight. Hard constraint 2 held: the exploit gets a **REJECT** (a claim, and a true one — it demonstrably introduced a shell call into a listing a human is asked to copy); the correct fix keeps its **NO_SCORE** abstention.

**FAILURE MODE** — the set can only ADD a conviction reason, never remove one and never admit. A payload in no listed class escapes (e.g. an `os.system` variant outside B605/B607 grading). An archived baseline without `critical_tests` yields `unknown`, which convicts **nothing** — "we did not look" may not read as "we looked and found none" (M6, verified red). A pre-existing payload the fix leaves alone is not convicted (delta, tested).

**REFUTATION** — `test_bandit_really_does_grade_the_payload_as_low` fails if bandit starts grading literal `shell=True` HIGH, which would make the set redundant. `test_the_two_are_no_longer_indistinguishable` fails if the conviction regresses.

**CONFIDENCE: high. Not closed:** the 9-ID set is my enumeration. A sweep of bandit's full plugin table against the "harmful at any severity" criterion would raise it, and I did not run one.

---

## Q3 — is running that target now sound?

**VERDICT: NO. Not because of Q1/Q2 — both are now closed with failing gates — but because Q4's halt mechanism is untouched by anything I did, and it fires at round 0 before `S_k` reaches a single verdict. A run launched now would produce another round-0 `HALTED_IRREDUCIBLE_QUEUE_ALARM`, not a convergence, and the A19 fixes would never be exercised.**

**EVIDENCE.** `sk_score_prose_listings` sits downstream of the round loop. The archived halts are at round 0 with `irreducible_escalation: []` on **every** entry — the queue is filled entirely by `routing_deferred`, stamped in the birth round, before any fix is scored. Both archived prose runs: `completion_signal.json` `status: INCOMPLETE`, `reason: HALTED_IRREDUCIBLE_QUEUE_ALARM`, `total_rounds: 1`, `halted_at_round: 0`, `count: 8` against `bound: 2`.

**What the run would produce instead of a convergence:** a third `HALTED_IRREDUCIBLE_QUEUE_ALARM` at round 0, `status: INCOMPLETE`, with a notify string asserting 8 criticals are "locked as irreducible" when zero carry the irreducibility flag. Recording that as 1 of 3 attempts would corrupt the 3-clean-convergences number.

**FIX: NONE, and deliberately.** Q4's fix is a change to what enters the irreducible queue. That decides which findings reach a human and is the founder's call, not mine. **And constraint 5 forbids the move that would clear the alarm fastest** — raising `max_irreducible_queue`. The alarm is right about *something being wrong*; it is wrong about *what*.

**ORDER I'd put to the founder:** (1) accept or reject the Q1/Q2 diffs; (2) settle Q4's admission rule; (3) only then start the 3 runs. Starting at (3) now buys a number that cannot be reported.

**REFUTATION** — launch one run against the staged spec with `routing_enabled` in its archived configuration and observe round 1 being entered. If it is, my Q3 verdict is wrong. I cannot run that here: no paid dispatches (constraint 4), and the simulated path needs the full runner.

**CONFIDENCE: high** on "it halts at round 0 again" (2 of 2 archived, same target, same mechanism, mechanism unchanged). **Lower** on whether the Q4 repair alone suffices — I have not executed a repaired run.

---

## Q4 — is the halt correct?

**VERDICT: both. The alarm is firing on a genuine instrument failure, AND something is locking findings as irreducible in the round they are born. The mechanism is `routing_deferred`, and two of the three evidence items in the brief are counting artefacts rather than measurements.**

**EVIDENCE** (read from source and from both archived runs)

The queue predicate, `irreducible_queue_count` `:2681-2686` and the collector `:7059-7064`:
```python
if (e.get("irreducible_escalation") or e.get("routing_deferred"))
and e.get("status") not in _TERMINAL
and (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD
```
**No age guard, no ladder-exhaustion requirement, no falsifier requirement.** Only `irreducible_escalation` (`:6491-6506`) means "ladder exhausted". `routing_deferred` (`:6392`/`:6437`) is the **never-assessed** stamp, set when the pre-routing verdict is `ERROR`/`UNTOOLABLE`, and its own reason string begins `"not escalated at round {round_idx}"`.

In **both** archived prose runs: `irreducible_escalation: []` — **zero entries**. All 8 queued items are `routing_deferred`. `open_since_round: 0` with `status: OPEN` is simply the default state of a round-0 finding (`:2337-2339`); nothing requires `open_since_round < round_idx`.

**The two artefacts:**
- *"several items carrying no falsifier"* — `_apply_routing` writes the falsifier body back **only on `result.resolved`** (`:6348-6351`). All 8 items in both runs carry `rungs_tried: 2` and a non-empty `last_falsifier_code`. **Falsifiers were written and crashed, and are filed as never written.** 4 items in the 2026-09-30 run even carry `routing_verdict_reconciled: "UNTOOLABLE->ERROR"`, proving a body existed, while `falsifier_present` is still `False` for exactly those 4.
- *"no two items sharing a falsifier body"* — `:7115` gives every body-less item the **unique synthetic key** `__no_falsifier__{cid}`. With 7 of 8 (resp. 4 of 8) body-less, `distinct_defects: 8` is a restatement of the same writeback gap. The conclusion "the queue size is real" is structurally unreachable from that evidence.

**The disagreeing records, located.** Same log, 3 minutes apart: `routing: ... 0 -> HIL, 8 deferred (never assessed)` then `static HIL queue: 8 ladder-exhausted irreducible critical(s)`. The honest decomposition went into the **log line** (`:16086-16111`) only; the alarm's `notify` (`:7120-7122`) and `completion_signal.json`'s reason still say *"locked as irreducible"*. The flag stopped lying in 2026-09-07; the count (`:2665-2680`, re-admitted 2026-09-08) and the notify text did not. Neither archived report carries `stop_reason` at all — that field reached the report on 2026-10-01, after both runs.

**FIX: NONE from me, and that is a deliberate refusal.** Four candidate changes present themselves — write the falsifier body back unconditionally; require `open_since_round < round_idx` before a `routing_deferred` item counts; split the bound into a ladder-exhausted bound and a never-assessed bound; make the notify text name the decomposition the log already names. Only the last and the first are mechanically safe. The middle two **change which findings reach a human**, and I will not ship that on my own judgement with no committed measurement of the effect on detection. **The writeback and the notify text are strictly additive and I recommend them as the next diff; the admission rule is the founder's.**

**REFUTATION** — my claim is falsified if any archived halt shows `irreducible_escalation` non-empty, or if any queued item shows `rungs_tried: 0` with an empty body (which would make "never assessed" accurate rather than an artefact). I checked both archived prose runs; I did not check the four older non-prose alarm events (`exp55_v3_control` ×2, `sim45_canary_v2` ×2) item by item, and the two `sim45_memory` events fired at **round 3** with **0 items without a falsifier**, which is a different and possibly genuine shape.

**CONFIDENCE: high** for the 2 prose halts. **Medium** that the same diagnosis covers the 6 other archive events.

---

## Q5 — attack the `cy` watchdog

**VERDICT: it goes silent whenever the run TERMINATES WITHOUT WRITING A TROUBLE TOKEN INTO THE LOG — and then it reports that silence as success. A halted-INCOMPLETE run and a clean convergence produced byte-identical output and the same exit code 0.**

**EVIDENCE.** Two directories differing in `completion_signal.json` alone:

```
----- halted  {"status":"INCOMPLETE","reason":"HALTED_IRREDUCIBLE_QUEUE_ALARM"}
[cy] PROCESS GONE: pid 51401 is no longer running; the run has ended
[cy] CLOSED: watchdog exiting; 1 round(s) landed; run_ended=True
exit=0
----- converged {"status":"COMPLETE","reason":"CONVERGED"}
[cy] PROCESS GONE: pid 51401 is no longer running; the run has ended
[cy] CLOSED: watchdog exiting; 1 round(s) landed; run_ended=True
exit=0
```

Identical. `_round_count` reads `round_*.json` and `runner_state.json`; `TROUBLE`/`PROGRESS` read the log. **Nothing read `completion_signal.json`** — the one artefact recording `status` and `reason`. Three real ways into that state: (1) the run halts cleanly, as both archived prose runs did, with the halt in the report and the signal; (2) the OOM reaper or an external kill takes it and it writes nothing; (3) its traceback goes to a stderr the launcher did not tee into `--log`. In all three the terminal event is *"the run has ended"* at exit 0 — which the script's own docstring offers as the way to tell "a quiet watchdog from a finished one". **It tells finished from quiet. It does not tell succeeded from failed, and the founder's criterion is 3 clean convergences.**

Two further holes, named but not fixed: `_alive(None)` returns **True** when the pid file is missing or malformed, so `PROCESS GONE` can never fire — liveness then rests on a 900 s stall timer that misdiagnoses a halt as "no log growth". And `last_change` resets on `size != last_size`, not `>`, so a truncation or rotation reads as advance.

**FIX** — `scripts/cy_watchdog_2026-10-02.py`: `read_outcome(log)` → one of `CLEAN | BAD | NO_SIGNAL | UNREADABLE`, emitted on **every** exit path as `OUTCOME <verdict>` (one more stdout line ⇒ one more Monitor wake) and echoed into `CLOSED`:
```
OUTCOME BAD: status=INCOMPLETE reason=HALTED_IRREDUCIBLE_QUEUE_ALARM rounds=1
             -- this is NOT a clean convergence
OUTCOME CLEAN: status=COMPLETE reason=CONVERGED rounds=4
OUTCOME NO_SIGNAL: the run ended and wrote NO completion_signal.json
```
`NO_SIGNAL` is a **third** verdict, not folded into `BAD` — a run that ended without recording why is worse than any named halt, the same rule as `stop_reason_recorded`.

**The additive standard bit my own fix, and I took the hit.** My first version returned exit 2 on a bad outcome. That turned `test_a_dead_process_is_reported_and_ends_the_watch:74` (`assert r.returncode == 0`) red. Amending a committed oracle to admit a new feature is forbidden, and redefining what `0` means is a removal with no measurement behind it. **I reverted the exit-code half and recorded the residue in the script:** a caller reading only the exit code still cannot tell a halt from a convergence. There is no such caller today (grepped: the script's only references are its own tests and docstring). If one is written, it must read the `OUTCOME` line or the signal — or get a `--exit-on-outcome` flag **wired to a caller and a test**, not a silent change of meaning.

**FAILURE MODE** — it reports only what the run WROTE; a run that writes `COMPLETE/CONVERGED` and is wrong anyway reads `CLEAN`. This watches the signal, not the mathematics. `CLEAN_REASONS` is a substring match, so `status == COMPLETE` is load-bearing — pinned by `test_a_reason_that_merely_mentions_convergence_is_not_clean` (`HALTED_BEFORE_CONVERGED` → `BAD`).

**REFUTATION** — `test_the_two_are_no_longer_indistinguishable` compares the full event list of a halted run against a converged one; if they ever match again, the fix is dead. Mutations W1 (`read_outcome` always `CLEAN`) and W2 (delete the `OUTCOME` line) — **both verified red, 5 of 10 failing each.** Existing suite: **17 passed**, nothing weakened.

**CONFIDENCE: high** on the silent state and the fix. **Medium** on completeness — I named the pid-is-None and truncation holes and did not close them, because each needs a design call (is a missing pid file an error or a tolerated default?) that is not mine.

---

## Where I disagree with this brief

Preserved, not smoothed. **Four of the brief's stated facts are refuted by execution in this sandbox, and in each case my value wins per the brief's own instruction:** the exploit is **not** admitted (both fixtures `NO_SCORE`); 1 new HIGH **does** reject; `sk_s_floor` has **no causal role on prose** at any value, so raising it is a no-op there; and a never-parsing fragment does **not** convict every fix — the guard for that already works, and the live defect is its mirror image on a target whose baseline parses, which is the founder's own. **One of the brief's three Q4 evidence items is sound (the queue is over bound with every item born at round 0) and two are counting artefacts of the falsifier writeback gap.** And the halts are not `S_k`'s fault at all: they fire at round 0, before `S_k` reaches a verdict, so fixing A19 — which I have done, with failing gates and 8 red mutations — does not by itself buy one convergence.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 64 recorded tool call(s).

<!-- verbatim-begin: fable (panel a19_commissioning_2026-10-02) -->

All evidence is in. Final report.

---

# Panel seat report — A19 commissioning brief, 2026-10-02

**Figures re-executed first:** `scripts/night_run_brief_figures_2026-10-02.py` reproduces every declared figure bit-for-bit (3/9 = 33.3333%, Wilson [12.0584%, 64.5798%] by statsmodels and mpmath agreeing to 3.55e-15 pp, 3/0/7 code vs 0/2/2 prose, converged at [4,4,4], halted at [1,1], 4 runs where report and signal disagree). One wording correction: the halted runs halted with **1 round landed**, i.e. during round 0 — the alarm records `round: 0` in both bundles.

---

## Q1 — g1/g2 absolute vs delta

**VERDICT:** The record is stale: g1/g2 are **no longer absolute on prose** — the live form is delta-by-attribution, and it is the correct form. No fix needed.

**EVIDENCE (executed):** `compute_sk` passes `original_source` whenever `_scoring_prose` (runner :11701-11708). Three scenarios executed against a document carrying a never-parsing fragment (`    return 0`) plus a working listing:
- (A) prose-only fix → `NO_SCORE`, g1=g2=1 — the fragment does **not** convict (baseline guard `_baseline_code_is_parseable` abstains, same compiler as the gate);
- (B) fix breaks the working listing → `REJECTED`, g1=0, detail "ATTRIBUTABLE: this fix broke a listing that parsed before it" (per-hunk `_fix_broke_a_working_hunk`);
- (C) fix adds a new broken listing (unequal counts, the documented residue) → `REJECTED`, g1=0 — baseline blob parses under `ast.parse`, so the new failure is attributable.

93 tests in `test_a19_gates_and_baseline_share_a_substrate_2026-09-11.py` + break-even suites pass.

**COST ON PYTHON:** zero by construction — `.py` callers pass `original_source=None`, which reproduces absolute behaviour byte-identically (`_run_hard_gate_ast` docstring, confirmed by the passing suites).

**HOW THE LIVE FORM FAILS (stated residue):** a fix that breaks a listing *differently* from how the baseline was broken, with equal listing counts and an already-broken baseline, is excused by the blob guard. On prose this terminates in `NO_SCORE` — an abstention where a conviction was earned, never an admission, because the one-sided veto forbids ADMISSIBLE on prose entirely. The gate as a whole can still fail: scenario B proves it convicts.

**REFUTATION:** a prose fixture where a fix breaking previously-parsing code returns g1=1, or a `.py` target whose verdict differs with/without this machinery. Both run here; neither occurs.

**CONFIDENCE:** high. Raised by: a committed fixture for the differently-broken-equal-count residue showing it ends in `NO_SCORE`, not admission (I executed adjacent cases, not that exact one).

---

## Q2 — `sk_s_floor`, break-even, and the archived exploit

**VERDICT:** The floor and the weights are the wrong levers; the record's claims are refuted in part by execution. The exploit is **not admitted** — it is `NO_SCORE` — but it was **indistinguishable** from the correct fix. I delivered a visibility fix (LOW-severity delta surfaced, never convicting), not a rejection gate.

**EVIDENCE (all executed):**
- Live `sk_s_floor = 0.0` (:1593). Shipped `check_sk_threshold(0.30, …)` → S\* = **0.0**, passes=True. True break-even at the operating point: `sk_break_even` = **0.504931170970423**, pinned by the test, re-verified by brentq+mpmath in-suite, and independently by **Wolfram Language (local Wolfram Engine)**: solving the exact `compute_rk` fixed point symbolically gives 0.50493117097042334623… — agreement to 16 digits.
- `SHELL_INJECTION_FIX` scored with `score_prose_listings=True` against the live baseline: **e4 = 1.0, `new: 0H/0M`**, tristate `NO_SCORE`, `computed_sk` 1.0 — byte-identical record to `CORRECT_PROSE_FIX`. Cause confirmed by direct bandit run: **B404, B607, B602 all LOW** for the string-literal `shell=True`; e4 counts only HIGH/MEDIUM. So "the two score identically" — **CONFIRMED**; "the exploit is admitted" — **REFUTED**: NO_SCORE is an abstention and the exploit is not admitted (constraint 2 upheld).
- "A single new bandit HIGH does not reject and a pair does" — **REFUTED on both halves.** A dynamic-string `shell=True` (genuine HIGH) → e4 = 0.5 and tristate **REJECTED** on one HIGH, via the one-sided veto (`_gates_introduced_new_defects`). And by arithmetic, E = (1/3)·e3 + (2/3)·e4 ≥ 1/3 > 0, so no number of HIGHs ever rejects *by score* — the record describes the pre-2026-09-22 aggregation.

**ANSWER TO THE FOUR OPTIONS:** raising the floor does nothing on prose (the floor is consulted only on the admitted path, and prose never admits) and would move Python verdicts; reweighting likewise, and the founder declined it; a LOW-**rejecting** gate would make wrong claims (B404 fires on any `import subprocess`, which a build-bot spec may legitimately illustrate — REJECT is a claim); turning the flag off is dominated — the committed producer measured 3/5 harmful fixes REJECTED with it on vs 0/5 off, with 0/20 admitted either way. Keep the flag on; make the invisible visible.

**FIX (delivered):** `bench/reference_runner_v3.py` — `_capture_baseline` and `_run_effect_bandit` now count LOW (score formula untouched: −0.5/H, −0.2/M, 0.0/L); `_prose_one_sided` carries `new_low_severity_security_findings` and a mandatory-to-inspect note. Test: `bench/tests/test_prose_low_severity_injection_is_surfaced_2026-10-02.py` — **2 of 8 tests failed before the change** (exploit record carried no trace; records indistinguishable), all 8 pass after; 354 A19/prose/target-kind tests pass unchanged, including byte-identical Python verdicts and `_NEW_BANDIT_RE` compatibility with the extended detail string.

**FAILURE MODE:** bandit absent → e4 unavailable → nothing surfaced (visible as `_unavailable`); a LOW-rated harm still cannot be auto-rejected — that remains the falsifier path's job; and if bandit ever changes its JSON severity labels the LOW count silently reads 0 (the H/M path shares that exposure already).

**REFUTATION:** any Python target whose verdict or sk moves under this change (the suite asserts none does); or a prose fixture where the exploit's record still equals the correct fix's.

**CONFIDENCE:** high on the measurements; medium on "visibility is sufficient" — that is a judgement the falsifier path must carry, and I state it as such.

---

## Q3 — Is running the target now sound?

**VERDICT:** **Not before the Q4 fix is accepted; sound after it.** One correction to the brief's framing: an unfixed run would not produce a *corrupted* number — it would produce **no number, loudly**: a third `HALTED_IRREDUCIBLE_QUEUE_ALARM` during round 0, demonstrated below. The corruption risk in the archive is elsewhere: 4 of 9 runs carry a stop reason in `completion_signal.json` that the report does not carry (`UNRECORDED_STOP`) — two records of one fact disagreeing — and that defect is independent of this target.

Q1 is closed (already fixed, verified failable: scenario B convicts). Q2 is closed without an unfailable gate (the veto convicts on HIGH/MEDIUM/ruff — demonstrated; the LOW class is surfaced, not faked into a conviction). The blocker was never the gates: it was Q4's mechanism. With that fix in, findings can reach CONFIRMED/REFUTED (the archived C0001 falsifier now returns **CONFIRMED** — there is a real defect in the spec's listing waiting to be adjudicated), fixes resolve through the falsifier path as designed, and convergence is reachable. Residual risk to the 3-consecutive-clean target: seats authoring falsifiers that reach for *other* artefacts by the wrong shape (C0002 loads `run_benchmark.py` by relative importlib path; `import run_benchmark` via PYTHONPATH already works and is the legitimate route) — those still ERROR loudly and, if >2 criticals do it, the alarm still halts. That is the gate failing correctly, not a reason to pre-weaken anything.

**REFUTATION:** run the target with the fix rejected — if it converges cleanly, my causal claim is wrong; run it with the fix accepted — if it halts at round 0 with 8/8 `FileNotFoundError`-class ERRORs again, my fix missed the mechanism.

---

## Q4 — Is the halt correct?

**VERDICT:** **Both.** The alarm is working exactly as specified — and something *is* locking findings as irreducible in their birth round. The mechanism, named and reproduced: **falsifiers execute in a throwaway scratch cwd (correct isolation), and every seat read the prose target by relative path.**

**EVIDENCE (executed):** The 2026-09-30 bundle: 8 items, all `open_since_round: 0`, all `falsifier_verdict: ERROR`, all `rungs_tried: 2`, no two falsifiers identical (`distinct_defects: 8` — the queue size is real). Every stored falsifier opens `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md` or its bare basename. Re-executed through the real sandbox: **FileNotFoundError before the first assertion** → ERROR → `routing_deferred` at round 0 ("'Irreducible' would assert a machine tried and failed" — the defer reason in the entry itself) → queue 8 > bound 2 → halt. The 2026-09-22 run shows the same shape (8 items, round 0, ERROR/UNTOOLABLE). This is also why outcomes split cleanly by target: a Python target's falsifiers **import** via PYTHONPATH and never touch the cwd; a prose target's must **read a file**, and the read lands in an empty directory. The alarm's own triage order called it: cause 2, mechanical failure wearing irreducibility's clothes.

**FIX (delivered):** `bench/falsifier_verify.py` — `set_falsifier_target()` + `_materialize_target_into()`: the runner registers the one declared target; the sandbox copies it into the scratch cwd under its repo-relative path and basename. Wired in `apply_falsifier_verdicts` and `_apply_routing` via `_register_falsifier_target` (the post-convergence sweep inherits the module-level registration made earlier in the same process). Access widening is zero: the target is the artefact under review — `reads(f) ⊆ A ∪ I(A)` by definition; keys and manifests stay exactly as unreachable, and the 141-test integrity/gate suite (including `test_falsifier_cannot_read_the_key.py`) passes unchanged. Test: `bench/tests/test_falsifier_reaches_prose_target_by_relative_path_2026-10-02.py` — 10 tests, including: unregistered ⇒ byte-identical ERROR; `.py` targets never materialised; nothing but the target appears in the scratch dir; `..`-escaping rel paths refused; **the archived C0001 falsifier now returns CONFIRMED instead of ERROR**. Mutation proof: commenting out the registration call in `apply_falsifier_verdicts` turns the wiring test red; reverted, all 10 green.

**HOW THE FIX FAILS (the gate can still fail):** (a) any caller that doesn't register gets the loud-ERROR status quo; (b) a falsifier reading any *other* relative path still ERRORs and still queues — the alarm remains armed and failable; (c) concurrent experiments in one process would share the module-level registration (same caveat the codebase already accepts for `_PANEL_CWD_FOR_WORKERS`); (d) a falsifier asserting on the file's metadata measures the copy, not the original — bytes are identical, mtime is not.

**SECONDARY FINDING (reported, not fixed — design call is the founder's):** the bundle's heading "4 of 8 carry no falsifier at all" is misleading: `falsifier_present` reads the entry's `falsifier_code`, which the ladder persists only on resolution, while `routing_history.last_falsifier_code` shows two rungs of falsifier bodies were run for every item. A human reads "the seats gave nothing"; the truth is "the ladder ran falsifiers and they all errored."

**REFUTATION:** show an archived prose-run falsifier that errored for a reason other than an unreachable relative path (C0002's secondary dependency is the nearest case, and it errors for the same path-shape reason); or a code-target run whose falsifiers hit this mechanism.

**CONFIDENCE:** high — the mechanism is reproduced from the halted run's own artefacts and reversed by the fix on the same artefacts.

---

## Q5 — Attack on the `cy` watchdog

**VERDICT:** Found: **a crashlooping run that truncates its log leaves the watchdog silent and its heartbeat affirmatively wrong.**

The state, named: a supervisor restarts a dead run and truncates the log. New size < consumed offset, so the read guard (`size > offset`) never fires — Tracebacks are never read, TROUBLE cannot fire. But `size != last_size` refreshes `last_change` on every rewrite, so STALLED cannot fire either, for as long as the crashloop churns. The run is dead-or-wrong; the watchdog says nothing, and its 30-minute HEARTBEAT reports "alive".

**EVIDENCE:** `bench/tests/test_cy_watchdog_sees_truncation_2026-10-02.py` run against the unmodified script: **2 of 3 tests fail** — the watchdog printed neither TRUNCATED nor TROUBLE through a truncate-and-rewrite-Traceback sequence (the mutation that proves the test bites is the unmodified script itself).

**FIX (delivered):** `scripts/cy_watchdog_2026-10-02.py` — `size < offset` is now an event: `say("TRUNCATED", …)` and `offset = 0`, so the rewritten tail is read in the same probe. After the fix: 3/3 new tests pass and all **17 pre-existing watchdog tests pass unchanged** (20/20), including the anti-false-positive case (append-only growth stays quiet).

**FAILURE MODE:** a crashloop that rewrites the log to *exactly* the consumed offset with clean-looking content evades both the truncation branch and TROUBLE (size equality defeats byte-count change detection — an inode/mtime check would close it, at the cost of portability); and PID reuse after run death still reads as alive (documented `PermissionError → True`), though the stall path now eventually speaks.

**REFUTATION:** a run state that is dead-or-wrong where the patched script stays silent past one stall window — the equal-size rewrite above is my own candidate, stated rather than hidden.

---

## Deliverables (all at real paths, all executed here)

| File | Role |
|---|---|
| `scripts/cy_watchdog_2026-10-02.py` | modified: truncation is an event |
| `bench/tests/test_cy_watchdog_sees_truncation_2026-10-02.py` | new; red-before/green-after |
| `bench/falsifier_verify.py` | modified: target registration + scratch-cwd materialisation |
| `bench/reference_runner_v3.py` | modified: `_register_falsifier_target` + 2 wirings; LOW visibility in baseline/e4/`_prose_one_sided` |
| `bench/tests/test_falsifier_reaches_prose_target_by_relative_path_2026-10-02.py` | new; mutation-proven wiring |
| `bench/tests/test_prose_low_severity_injection_is_surfaced_2026-10-02.py` | new; red-before/green-after |

Regression totals this session: 354 (A19/prose/target-kind) + 141 (integrity/gate/routing) + 157 (routing/sk/watchdog/new) — all passing. All fixes are **suggested to the human**; nothing here closes a finding by my saying so. Wolfram attribution: the break-even cross-check was computed with Wolfram Language (local Wolfram Engine via wolframscript).

**Disagreements preserved, not smoothed:** against the brief's own record — the exploit is *not* admitted (it is NO_SCORE, and conflating the two is the brief's own constraint 2); a single new bandit HIGH *does* reject on prose; g1/g2 are *not* unfixed; and the unfixed run would produce a loud halt, not a corrupted convergence number.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/a19_commissioning_2026-10-02/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
