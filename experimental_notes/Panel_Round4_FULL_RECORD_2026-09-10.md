# Panel Round 4 — FULL RECORD, unfiltered

2026-09-10, dispatched 03:30:25 BST, both seats returned by 03:40:15 BST. Record written 2026-09-10T03:54:48+01:00.

## What was reviewed and why

Section P of the master task list makes a panel review a precondition on closing any entry: *"No entry may move to DONE until its fix has been through a panel review meeting every clause below."* Round 3 covered the DONE-evidence guard and the note-lint commit guard. Three further pieces of work landed afterwards — the restore-order repair at `fc479bb`, the task 6.7 repair at `03254e8`, and the 9 corrected figures at `efbaf8a` — and none had been reviewed. Round 4 is that review.

## Seats and cost

2 seats, `cc2` (Claude Opus 4.7 via CLI piped mode) and `fable`, both on the Max subscription. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`. The dispatcher was `bench/confer_maths_panel_2026-09-05.py`, the only 1 of 39 that carries the 28,183-character formal schema in its system prompt. The brief passed all 7 checks of `scripts/panel_brief_validate.py` before dispatch.

## Seat: cc2

Model `cc2`, route `claude_cli`, 48 recorded tool calls, 590.2 s, 20,960 characters returned.

### Verbatim response

<!-- verbatim-begin: a panel seat's reply, reproduced unaltered -->

# PANEL VERDICT — round 4

## `verdict`

**PARTIAL.** Repair 1 (restore order) and Repair 2 (6.7 assessment) hold under execution and under mutation. **Repair 3 (the 9 corrected figures) does not** — it reproduced its own subject: one of the corrected figures is the corrected numerator over the *superseded* denominator, which is verbatim the defect the same paragraph flags two sentences earlier. A second artefact in the batch, the watchdog script, was repaired without any test reaching it and remains blind to the regression it exists to detect.

`passes_run`: **5** (pass 5 produced no new above-threshold finding).

---

## `gate_reading` — **KEEP GOING**, and the gamma side should be read as carrying *no information here*

Executed:

```
$ python3 scripts/ffafp_cycle_gamma_2026-09-10.py
  series                 : [11, 4, 2, 3, 6, 2, 3, 2, 9]
  gamma (Duane slope)    : 0.415413
  (a) gamma >= 0.3       : PASS
  (b) 3 zero-finding passes: FAIL   (last 3: [3, 2, 9])
  TWO-SIDED GATE         : KEEP GOING
```

**Import verified, not asserted.** `ffafp_cycle_gamma_2026-09-10.py:42` is `from bench.reference_runner_v3 import _estimate_gamma`. There is no re-implementation. The gate constants (0.30, K=3) sit in the script, not the runner, but the estimator itself is shared. Confirmed sound.

**Derivation, independent of the tool.** cum = [11,15,17,20,26,28,31,33,42]; OLS of log(cum) on log(i+1) gives β = 0.5845866710519128, γ = 1 − β = **0.415413**. Exact agreement to the runner's value. Its band label is `Moderate depletion — consistent with PoC convergence`.

**The brief asked the right question and the answer is worse than it guessed.** γ is fitted to the *cumulative* series, so a large opening round mechanically guarantees a sublinear log-log fit no matter what the tail does. I ran the real estimator over a series that rises **monotonically for eight consecutive passes**:

```
STRICTLY ACCELERATING    [11, 1, 2, 3, 4, 5, 6, 7, 8]
   gamma = 0.324155  gamma-side = PASS   band = Moderate depletion — consistent with PoC convergence
   last-3 sum = 21, previous-3 sum = 12  -> RESURGENCE
```

γ passes on accelerating discovery. So `ffafp_cycle_gamma_2026-09-10.py:21`'s gloss — *"(a) gamma >= 0.30  the decay curve has flattened"* — is not supported by the statistic. On the live series, γ = 0.4154 versus 0.4606 had pass 9 returned zero: the resurgence moved γ by 0.045 and could not have moved it below threshold from where it started.

γ is not useless — `[2]*9` → 0.000, `[1..9]` → 0.000, `[1,2,4,…,256]` → 0.000, all correctly failing. It is *confounded by a large leading round*. Here pass 1 = 11 of 42 cumulative findings, and it is doing the work.

**Conclusion: the count side is carrying the entire gate.** Read it that way and the verdict is right for the right reason. Read γ as corroborating evidence and it is a false second opinion — the same shape as the stale document Repair 1 exists to prevent.

---

## `findings`

### F1 — CRITICAL. The 2.1 correction reproduced the defect it was correcting.

- **File/line:** `experimental_notes/CDSFL_MASTER_TASK_LIST.md:188`
- **Wrong:** the corrected paragraph reads *"Missed is **1,068** … 16.99% is arithmetically faithful to the wrong numerator. Of those, **1,052** carry a description between label and fence, 97.32%, Wilson [96.17%, 98.13%]"*. `1052/1081 = 97.3173%`, Wilson [96.17%, 98.13%] — an exact match to the **superseded** denominator 1,081. Against the entry's own corrected denominator 1,068 the value is `98.5019%`, Wilson [97.58%, 99.08%]. The scope word is `"Of those"`, so 1,068 is unambiguously the intended denominator. Task 2.1 is marked `state: DONE | status: ENABLED`.
- **Fix:** line 188, old → new:
  - old: `carry a description between label and fence, 97.32%, Wilson [96.17%, 98.13%], not 1,066.`
  - new: `carry a description between label and fence, 98.50%, Wilson [97.58%, 99.08%], Clopper-Pearson [97.58%, 99.14%], not 1,066 of 1,081.`
- **Executed falsifier:** `/tmp/fals/fals_A_entry21_ratio.py` (reads the real task list; no key, no manifest).

```
$ python3 /tmp/fals/fals_A_entry21_ratio.py
entry's CORRECTED missed denominator : 1068
entry's SUPERSEDED denominator       : 1081
described-subset numerator           : 1052
entry QUOTES                         : 97.32%  Wilson [96.17%, 98.13%]
1052/1068 (corrected)              : 98.5019%  Wilson [97.58%, 99.08%]
1052/1081 (superseded)             : 97.3173%  Wilson [96.17%, 98.13%]
FALSIFIED
AssertionError: entry 2.1 line 188 quotes 97.32% Wilson [96.17%, 98.13%] = 1052/1081, the
SUPERSEDED denominator. ... The 2026-09-10 correction reproduced the defect it was correcting.
EXIT=1
```

- **Negative control (fails *iff* the defect is present):** same falsifier against a copy patched only in that ratio and interval →
```
$ python3 /tmp/fals/fals_A_neg.py
entry QUOTES : 98.5%  Wilson [97.58%, 99.08%]
clean: the quoted percentage matches the corrected denominator
EXIT=0
```

### F2 — HIGH. The instrument behind 6.2 hardcodes the operator it claims to read, and no test reaches it.

- **File/line:** `scripts/watchdog_vs_retry_budget_2026-09-09.py:84` (`cap = mult_cap if form.startswith("pre-") else max(mult_cap, budget)`)
- **Wrong:** `multipliers()` reads the two *multipliers* from `reference_runner_v3.py:8404` by regex, but the **combining operator** (`max`) at `reference_runner_v3.py:8406` is typed into the script. If the runner regressed to `min`, the script — the artefact task 6.2 cites for its figures — still prints `fits` for every seat and `truncated: 0 of 5`. I verified this live, mutating the sandbox runner (restored, byte-identical to canonical, confirmed by `diff -q`):

```
$ # reference_runner_v3.py:8406  max(...) -> min(...)   MUTATION APPLIED at line 8406
$ python3 scripts/watchdog_vs_retry_budget_2026-09-09.py
  Gemini    timeout= 300  retries=5  budget= 1500s  watchdog= 1500s  fits
truncated: 0 of 5
```
Gemini is truncated 1500 s → 900 s and the instrument reports `fits`. (The *runner* regression is caught — the suite went `5 failed, 1 passed` — because `test_watchdog_respects_retry_budget_2026-09-09.py:51-53` pins the whole three-line expression. The script is the unguarded half.)

- **Second half, the additive-standard breach:** `grep -rn watchdog_vs_retry_budget bench/` returns exactly one hit — a **docstring mention** at `test_watchdog_respects_retry_budget_2026-09-09.py:14`. No test imports or executes the script. It silently exited 1 for a full day for precisely this reason, and the 2026-09-10 repair added the two-form acceptance without adding anything that reaches it. **Trap 2 of the brief:** the third-form refusal at `:67-68` does exist and is correct — but nothing executes it, so its status is *unmeasured*, not *verified*.
- **Fix (two lines, one test):**
  1. `scripts/…:59-62`, extend the post-form regex to capture the operator and return it:
     - old: `r"_mult = (\d+) if base_model_label\(mc\.label\) == \"CC2\" else (\d+)", src)`
     - new: `r"_mult = (\d+) if base_model_label\(mc\.label\) == \"CC2\" else (\d+)\n\s*_retry_budget = [^\n]+\n\s*wall_limit = (max|min)\(mc\.timeout \* _mult, _retry_budget\)", src)` — return `post.group(3)` as `op`.
  2. line 84: `cap = mult_cap if form.startswith("pre-") else (max if op == "max" else min)(mult_cap, budget)`.
  3. New `bench/tests/test_watchdog_script_tracks_the_runner_2026-09-10.py` with three cases: post-form → 0 of 5; regressed `min` form → Gemini TRUNCATED; **absent form → `SystemExit`** (which closes trap 2 by execution).
- **Executed falsifier:** `/tmp/fals/fals_B_watchdog_operator.py` — imports the real script module, redirects only `W.RUNNER` at a synthetic regressed source (the artefact is not mutated on disk):

```
$ python3 /tmp/fals/fals_B_watchdog_operator.py
script names the form as     : post-2026-09-09 (max of multiplier and retry budget)
  Gemini    budget= 1500s  script says watchdog= 1500s (fits     )  runner ACTUALLY caps at   900s (TRUNCATED)
FALSIFIED
AssertionError: the script reports 'fits' for Gemini while the runner it claims to read truncates
it from 1500s to 900s. The `max` at watchdog_vs_retry_budget_2026-09-09.py:84 is typed into the
script, not read from reference_runner_v3.py:8406 ...
EXIT=1
```

### F3 — HIGH. The gamma side's stated meaning is not what the statistic measures.

- **File/line:** `scripts/ffafp_cycle_gamma_2026-09-10.py:21`; the same gloss reaches operators through `reference_runner_v3.py:2637` (`(0.30, 0.45, "Moderate depletion — consistent with PoC convergence")`).
- **Wrong:** demonstrated above — γ = 0.3242 ≥ 0.30 on eight consecutive passes of *rising* discovery. The report prints γ and its verdict and says nothing about tail direction, so a reader given `γ = 0.415, PASS` alongside `pass 9 = 9` has no cue that the second number contradicts the first's usual reading.
- **Fix — additive, three lines, nothing removed.** After line 118, in `main()`:
```python
    if len(counts) >= 6:
        tail, prev = sum(counts[-3:]), sum(counts[-6:-3])
        if tail > prev:
            print(f"  !! RESURGENCE: last 3 passes found {tail} vs {prev} in the 3 before.")
            print(f"     gamma is fitted to the CUMULATIVE series and is dominated by pass 1")
            print(f"     ({counts[0]} of {sum(counts)}); it does not fall on a rising tail. Read")
            print(f"     side (a) as uninformative here — side (b) is carrying this gate.")
```
  and amend line 21 to `(a) gamma >= 0.30   the CUMULATIVE curve is sublinear — NOT a claim about the tail`. Pin it with a test asserting `[11,1,2,3,4,5,6,7,8]` prints `RESURGENCE` while passing side (a).
- **Executed falsifier:** `/tmp/fals/fals_C_gamma_accelerating.py`, output quoted in `gate_reading` above; `EXIT=1`, `FALSIFIED`.

### F4 — MEDIUM. 6.5's correction left the broken-state clause it names standing.

- **File/line:** `experimental_notes/CDSFL_MASTER_TASK_LIST.md:310`
- **Wrong:** the entry says *"The entry described a repaired state in the present tense of the broken one"* — and then, in the very next sentence, un-prefixed and in the present tense: *"the 1 file written by `bench/detached_launch.sh:11` is consumed only by a read-only printer."* That is false at HEAD: `bench/tail_until_done.sh:74` (`PIDFILE="${ARG2:-${LOG%.log}.pid}"`) consumes it to tie the monitor's lifetime to the run — which the same sentence group asserts two clauses earlier. The correction repaired two clauses of three.
- **Fix:** line 310, old `... the present tense of the broken one. the 1 file written by` → new `... the present tense of the broken one. BEFORE THE FIX, the 1 file written by`, and `is consumed only by` → `was consumed only by`.
- **Falsifier:** the same shape as F1 — assert that every present-tense clause after the `AS AT 2026-09-09, BEFORE THE FIX` marker is either past-tensed or carries the marker. I did not automate this one; the evidence is the two file reads quoted above and it is a text-level correction, so I report it as **PLAUSIBLE-verified-by-read**, not CONFIRMED-by-tool. Weigh it accordingly.

### F5 — MEDIUM. 6.2 attaches the pre-fix figure to the post-fix script.

- **File/line:** `experimental_notes/CDSFL_MASTER_TASK_LIST.md:301`
- **Wrong:** *"the script now reads BOTH the pre- and post-fix forms and names which it found, 20.0%, Wilson [3.6%, 62.4%]"*. Run today the script reports `truncated: 0 of 5`, `Wilson [0.0%, 43.4%]`. 20.0% / [3.6%, 62.4%] is `1/5`, the **pre-fix** rate — correct earlier in the same paragraph, misattached here to "the script now". Both figures appear in one paragraph with the reader left to sort them.
- **Fix:** line 301, old `names which it found, 20.0%, Wilson [3.6%, 62.4%], Clopper-Pearson [0.5%, 71.6%]` → new `names which it found. Against the PRE-fix form it reports 1 of 5, 20.0%, Wilson [3.6%, 62.4%], Clopper-Pearson [0.5%, 71.6%]; against HEAD it reports 0 of 5, Wilson [0.0%, 43.4%], Clopper-Pearson [0.0%, 52.2%]`.
- **Evidence:** the live script run above, plus `statsmodels` cross-check: `0/5` → Wilson [0.00%, 43.45%], CP [0.00%, 52.18%]; `1/5` → Wilson [3.62%, 62.45%], CP [0.51%, 71.64%]. Both quoted intervals are arithmetically correct; only the attribution is wrong.

### F6 — MEDIUM, and it is about *this review's* harness, not the artefacts.

The staged sandbox degraded **during** the review. Measured:

- 03:32 — `python3 scripts/ffafp_cycle_gamma_2026-09-10.py` ran to completion and printed the gate.
- 03:33 — `pytest` over the three named test files: `95 passed in 1.30s`.
- 03:36 — the same gamma command dies at `reference_runner_v3.py:169` with `ModuleNotFoundError: No module named 'dynamic_management'`; `bench/*.py` holds 8 files against canonical's 167; `bench/live_dispatch_policy.py` is gone and `pytest` now fails at import in `bench/tests/conftest.py`.
- `stat` on `bench/` shows mtime `Sep 10 03:36:07`, inside this session. I made exactly two writes, both `cp`-restored and both verified byte-identical to canonical (`diff -q` → identical). I cannot attribute the removals and do not claim to.

Consequence under §10 category 5: **my γ figure and my 95-passed figure are not reproducible from that directory now.** They were taken from the complete tree while it was complete and I have quoted them verbatim. Falsifier C was re-pointed read-only at the canonical tree to stay runnable. A seat dispatched later than mine will report the gate as unreadable and would be right to.

---

## Trap verdicts, as the brief posed them

**Trap 1 — the coincident-order fixture: CLOSED, demonstrated.** Mutation applied to `cdsfl_recover.py:225` (`existing.sort(...)` → `pass  # MUTATED`), verified single-occurrence before applying, and the line is on the executed path (`first_read_lines` is called by every fixture):

```
$ python3 -m pytest bench/tests/test_first_read_prefers_the_fresher_source_2026-09-10.py -q
FAILED ...::test_the_sort_is_load_bearing_when_declaration_order_disagrees
E       AssertionError: the freshest file was not put first when the declaration order
        disagreed with modification time — the sort is not doing anything
E       assert 1032 < 437
1 failed, 8 passed in 0.20s      # (restored; canonical verified identical)
```
The fixture genuinely inverts declaration order against mtime. **One residual, below threshold:** `targets` includes `Path.home()/"Desktop"/…`, which is outside `tmp_path`, so the "hermetic" fixtures read a live file on the founder's machine. It cannot currently break the assertions (the tmp files are stamped `now`), but it is a real-tree dependency inside a tmp fixture and worth a `monkeypatch` of `Path.home` when someone is next in the file.

**Trap 2 — the third, absent form: PARTIALLY OPEN.** The refusal exists and is correct (`:67-68`); nothing reaches it. See F2.

**Trap 3 — 6.5's docstring: CLOSED.** The file holds 11 tests; 9 execute the script, and the corrected paragraph says *"MOST TESTS HERE RUN THE SCRIPT"* and then names both exceptions by name (`test_the_script_exists_and_is_executable`, `test_the_launcher_names_the_monitor`) and defends the second. That is accurate against the file. Declared **SOUND**.

## Repairs 1 and 2, on the record

**Repair 1 holds.** Ordering is real (mutation red), staleness labelling is real (`20.0 DAYS older`, `10.0 DAYS older` asserted against built spreads), the disagreement rule is present verbatim, missing files are named rather than swallowed, and both new FIRST READ entries are asserted present. 9 tests, all collected, all executing `first_read_lines`.

**Repair 2 holds and is the cleanest work in the batch.** `test_the_seat_guard_names_a_member_that_does_not_exist` executes `m.has_evidence(0)` under `pytest.raises(AttributeError)` rather than asserting the absence; the premise test pins the fire at call 5; `test_it_does_not_fire_before_the_threshold_is_crossed` is a genuine discrimination control (a detector that fired immediately would prove nothing); and the two claims the original entry collapsed — *would not have fired on real data* versus *cannot fire* — are held apart by two tests that must both stand. This is what an executed verdict looks like.

## `rho` and `nu` — agreed, not implicated, and here is the check rather than the opinion

`grep -rn cdsfl_recover bench/*.py bench/dm/*.py` returns zero hits: nothing in the measurement path imports the restore script. `first_read_lines` is pure — it stats and formats, and returns a list of strings that `main()` prints. ρ and ν are computed in `reference_runner_v3.py` (`_compute_rho:2664`, `nu_eff:10211`) from per-round novelty counts produced by the panel, which never traverse the restore. **No path exists.** The nearest thing to one is second-order and outside the accounting: FIRST READ order changes what an *assistant* believes, which could change what it dispatches — but that is not novelty or overlap accounting, and treating it as one would be exactly the false-coupling this project keeps finding.

---

## `refutation_condition`

**What would overturn my PARTIAL.** F1 falls if `"Of those"` at line 188 is shown to scope to 1,081 rather than 1,068 — but the sentence introduces 1,068 as the corrected value one clause earlier, and 1,066/1,081 is the figure being *replaced*, so I hold it. F2 falls if a test is found that executes `scripts/watchdog_vs_retry_budget_2026-09-09.py`; my grep covered `bench/` and found only a docstring. F3 falls if the project's stated reading of the gamma side is narrower than the docstring says — if it means only "the cumulative curve is sublinear", my objection reduces to a wording fix, which is precisely the fix I proposed.

**If you accept these repairs as sound, the class they still let through** is the one F1 *is*: **a correction that fixes the numerator and leaves a derived quantity keyed to the old denominator.** Nothing in this batch cross-checks a percentage against the two integers printed beside it. Repair 3 employed 4 agents on 4 entries and 9 figures and still shipped one. The cheapest closure is a lint pass over the task list that re-derives every `k/n` and every Wilson interval from the integers in the same sentence and fails on disagreement — under a hundred lines, mechanical, and it would have caught F1, F5 and the original 2.1 defect. **It is worth its cost**, because it converts this project's most frequent defect class from an agent-hours problem into a commit-hook problem.

**What would make me say STOP rather than KEEP GOING.** Three consecutive zero-finding passes, with the resurgence line of F3 shipped and printing nothing. Not γ ≥ 0.30 — I have shown that number cannot fall on a rising tail. Concretely: passes 10, 11 and 12 at zero, where each pass reviewed a *newly named* mechanism rather than re-reading the same artefacts. Absent that, the Objective directive's Guard 2 is satisfied right now by a named mechanism: **corrections that re-key derived figures to superseded denominators**, unexamined until this pass and confirmed present on the first look.

---

## `strongest_disagreement` with this brief

**Section 2 states "`gamma` is 0.451". It is 0.415413.** Measured by the brief's own named instrument and re-derived by hand OLS to twelve significant figures. This is not a rounding quibble: `GAMMA_BANDS` at `reference_runner_v3.py:2636` puts 0.45 on the boundary, so 0.451 reads as `Strong depletion — confirms state-based closure` while the true value reads as `Moderate depletion`. The brief handed the panel a figure that upgrades the convergence evidence by one band, in a brief whose subject is nine figures that were wrong, and asked us to judge whether the process producing figures is sound. It is a digit transposition of 0.415. It is **not** in the repository — `grep` for `0.451` across the task list, the series JSON and the cycle script returns nothing — so the artefacts are clean and the brief is not.

Second, and more substantive: the brief frames the gate question as *"is a Duane slope over a rising tail being read correctly."* That framing concedes too much to γ. The finding is not that γ is being misread — it is that **γ over a cumulative series with a large opening round cannot be read at all in this direction**, which I demonstrated with a monotonically accelerating series that passes. Asking whether the number is being read correctly invites a better reading. There isn't one. The right response is to stop offering that side as corroboration and let the count side stand alone, which is what the two-sided gate was built to do and what its own founder ruling of 2026-06-10 already says.

Third: the brief asserts *"`rho` and `nu` — probably not implicated. Say so if you agree."* I do agree, and I ran the check — but a brief that supplies the expected answer to a question it is asking a panel to decide independently is doing to this panel what the stale tracker did to the assistant on 2026-09-09. **A brief written before the panel ran cannot record what the panel found.**

<!-- verbatim-end -->

---

## Seat: fable

Model `fable`, route `claude_cli`, 35 recorded tool calls, 353.6 s, 8,457 characters returned.

### Verbatim response

<!-- verbatim-begin: a panel seat's reply, reproduced unaltered -->

All machinery has been executed. Both passes complete — writing the verdict.

---

# Panel Seat Report — Round 4

## verdict
**PARTIAL.** Repairs 1 (restore order), 2 (seat-guard assessment) and 3's process (re-measurement, watchdog script revival) hold under execution and mutation. But the corrected 2.1 entry **still contains one figure computed against the stale denominator it was correcting** — the exact defect class this repair round existed to eliminate — so repair 3 is not fully delivered.

## reasoning (all from tool output I saw)

- **Repair 1 (restore order):** `first_read_lines` offers the task list and outcomes log, sorts by mtime newest-first, labels staleness. 9/9 tests pass. Mutation 1 (sort → `pass`, applied and verified) → **1 failed, 8 passed**: only `test_the_sort_is_load_bearing_when_declaration_order_disagrees` catches it, exactly as its docstring claims. Mutation 2 (staleness labels removed) → **3 failed, 6 passed**. Trap 1 is genuinely closed: the load-bearing fixture inverts declaration order against mtime order, so coincidence can no longer save a removed sort.
- **Repair 2 (6.7):** both verdicts execute. `ImmuneMemory` has no `has_evidence` (AttributeError raised, pinned), and the all-zero series fires the detector at call 5. 4+1 tests pass, including the no-production-caller sentinel. The entry's distinction ("would not have fired" ≠ "cannot fire") is correct and tested.
- **Repair 3 (figures):** the watchdog script now runs, exits 0, reports 0/5 truncated post-fix, Wilson [0.0%, 43.4%], statsmodels/scipy agreeing to 1e-9 — matching entry 6.2. Trap 2: I redirected `RUNNER` to a fabricated file containing a third expression form; `multipliers()` raised `SystemExit("...neither the pre- nor post-2026-09-09 form was found")` — **it still refuses**. Trap 3: 6.5's corrected docstring now says "MOST tests here run the script" and names both exceptions (mode check line 68, source-read line 209); verified against the file — accurate. M1's 15/48 = 31.25%, Wilson [19.95%, 45.33%] — my independent derivation agrees with the entry to the quoted precision.
- **Round-3 regression:** the `__doc__`-based guard is real. My first mutation attempt **failed to apply** (the docstring sentence wraps across lines; only the assert literal matched my needle — the exact SURVIVED-that-isn't trap the brief warns of). Corrected mutation, verified to land in the executed `__doc__` path → **1 failed, 80 passed**. The self-read defect is dead.
- **Import verification:** `ffafp_cycle_gamma` imports `_estimate_gamma` from `bench/reference_runner_v3` (line 42); my independent least-squares fit of log(cum) vs log(i) gives **0.41541332894808614**, matching the script's printed 0.415413 exactly — same math, no drift.

## findings

**F1 — CONFIRMED, HIGH (false figure standing as corrected in the canonical list).**
`experimental_notes/CDSFL_MASTER_TASK_LIST.md:188` (entry 2.1). The corrected sentence reads "**1,052** carry a description between label and fence, **97.32%, Wilson [96.17%, 98.13%]**". But 1052/1068 = **98.50%**, Wilson **[97.58%, 99.08%]**. 1052/**1081** — the stale missed-count the same sentence just retired — is 97.317%, Wilson [96.17%, 98.13%]: both the point estimate and the interval fingerprint the stale denominator exactly. The repair that fixed 9 wrong figures left a 10th of the identical class in the correcting sentence itself.
*Fix:* line 188, old: `97.32%, Wilson [96.17%, 98.13%]` → new: `98.50%, Wilson [97.58%, 99.08%]`.
*Falsifier executed:* Wilson script above; output: `desc/1068 CORRECT denom: 98.50% [97.58%, 99.08%]` / `desc/1081 STALE denom: 97.32% [96.17%, 98.13%]`.

**F2 — CONFIRMED, LOW (test hermeticity).**
`scripts/cdsfl_recover.py:195` hardcodes `Path.home()/"Desktop"/...`, so every tmp_path fixture in the freshness suite silently includes the **live machine's** Desktop file (it exists here: mtime Sep 9 23:39). No false-PASS path exists (declaration order defeats a removed sort regardless), but a Desktop mirror with a future mtime would flake the `"10.0 DAYS older"`/`"20.0 DAYS older"` assertions, and `out.index("CDSFL_Agent_Operational_Plan.md")` can bind to the mirror's identical basename. *Fix:* hoist the Desktop path to a module constant `DESKTOP_MIRROR`; fixtures monkeypatch it under `tmp_path`. Worth its ~5-line cost.

**F3 — advisory, below threshold.** `watchdog_vs_retry_budget:37` slices the orchestrator source from `label="CC2"` to the next `def `; a seat defined outside that window vanishes silently. A `assert len(out) == 5` (or a printed expected-count) would make omission loud.

## falsifier / falsifier_result
Primary: the Wilson two-denominator fingerprint (F1) — output above. Plus 3 applied-and-verified mutations (1 red / 3 red / 1 red), the third-form refusal (SystemExit raised), and the independent Duane fit (agreement to 1e-9). All commands and outputs shown in the transcript.

## gate_reading
**KEEP GOING** — and the script reads its own gate correctly (`(a) PASS, (b) FAIL → KEEP GOING`). Two corrections to the brief, though: (1) **gamma is 0.415413, not 0.451** — 0.451 ≈ the 8-pass prefix value (0.4537); the brief quotes a pre-pass-9 stale figure. (2) The gamma side's meaning is weaker than "the curve has flattened": pass 9 contributed 21% of all cumulative findings (9/42) and came from a **new discovery modality** (figure re-measurement agents, not run in passes 2–8). A Duane fit assumes a stationary process; each fresh modality re-inflates discovery, so gamma over the mixed series overstates depletion. The count side is the real protection — but a 3-zero streak from an exhausted modality does not test unexhausted ones. Cheap hardening: record the modality with each `--record`, and print a caveat when the latest pass exceeds the maximum of the preceding 3 (true here: 9 > max(6,2,3,2)).

## refutation_condition
My PARTIAL would flip to CONFIRMED if 1052/1068 were shown to be the wrong pairing — i.e. a committed measurement showing the description-bearing subset was counted against a 1081-sized population for a stated reason the entry records. It would flip to REFUTED if any of my three red mutations could be shown not to have applied to an executed path (I verified landing for all three, including redoing one that hadn't). The soundness I do grant would still let through: per-item mutation gaps the DONE guard itself disclaims (evidence files need not concern their task), any stale figure whose producing script agrees with it (the scripts pin reproduction, not truth of inputs — the 6363 denominator is admitted unstable), and convergence declared off a modality-exhausted zero streak. I would accept CONVERGED only after 3 zero passes of which ≥1 uses a modality not previously run, with gamma ≥ 0.30 recomputed at that point.

## strongest_disagreement
**The brief commits the defect it is prosecuting.** It states gamma = 0.451 as the live value; the machinery prints 0.415413, and 0.451 is the stale 8-pass figure. A panel brief reviewing "9 figures that were wrong" fed its reviewers a 10th unbacked figure — as did entry 2.1 (my F1). Also minor: the brief says "4 agents re-measured"; entry 2.1 says 5. The lesson generalizes: figures quoted in briefs and correction sentences are exactly as unbacked as the ones they replace unless re-executed at quote time — corrections need the same `measured-rate-travels-with-its-script` discipline as originals. Second disagreement: the brief frames "is the Duane slope read correctly" as potentially "the most important finding available"; it is not — the two-sided gate already neutralizes the misreading (verdict KEEP GOING either way). The stationarity critique is real but changes no decision today.

## rho / nu
Not implicated, confirmed by inspection: restore ordering shapes operator context only; novelty/overlap accounting operates over panel findings inside the runner, and no artefact in this batch writes to any state the runner's η/ν computation reads. I found no path.

## passes_run
**2.** Pass 1: executed all scripts and suites, 3 verified mutations, third-form refusal, independent gamma and 3 Wilson derivations, traps 1–3 → F1, F2, F3. Pass 2: re-examined the drift test's `hasattr` fallback (fails loud, not falsely passes), the ordering test's lexical ISO sort (sound), and the watchdog `seats()` slicing (already F3) → no new above-threshold findings. Terminated per §6: a further pass has no named mechanism left to search.

<!-- verbatim-end -->

---

## The brief the seats were given

<!-- verbatim-begin: the brief as dispatched; see BRIEF_CORRECTION_SIDECAR.md -->

# PANEL BRIEF — round 4: the restore-order fix, the seat-guard repair, and 9 figures that were wrong

## SECTION 1 — The question

**Three repairs landed after round 3 finished, so none of them has been reviewed. Do they hold, and is the process that produced them itself sound?**

Round 3 reviewed the DONE-evidence guard and the note-lint commit guard. Both seats returned PARTIAL with 6 findings between them; the worst was a guard that read its own source file and so satisfied itself from its own literal. Those 6 were repaired at commit `8f88650`. Then 3 further pieces of work landed, at `fc479bb`, `03254e8` and `efbaf8a`, and section P of `experimental_notes/CDSFL_MASTER_TASK_LIST.md` forbids any of them moving to DONE until a panel review has met every clause. This is that review.

**Repair 1 — the restore reads the older document first, and it cost the founder a drive home.** `scripts/cdsfl_recover.py` names an operational tracker as FIRST READ. On 2026-09-09 at 23:00 it fed the assistant a stale line saying the answer-key sealing still awaited the founder. He had already driven home from his hotel and done it himself on 2026-09-07 at 22:03, and the assistant repeated the stale line back to him. The correct record sat in the master task list, written 8 hours earlier. FIRST READ now offers `CDSFL_MASTER_TASK_LIST.md` and `CDSFL_OUTCOMES_LOG.md`, orders every entry by modification time newest-first, and labels how far behind the newest each one is. Its stated rule: the fresher one wins unless it says otherwise, and a stale document is not a second opinion.

**Repair 2 — an assessment declined a question that was answerable.** Task 6.7 recorded a seat's guard proposal as undecidable. `ImmuneMemory` has no `has_evidence` attribute, so the guard raises on its first call, and the premise is executable rather than a matter of opinion. Both verdicts are now executed rather than asserted.

**Repair 3 — 4 agents re-measured the figures in 4 entries and 9 of the figures were wrong.** Task 2.1 said 5,282 captured when its own next sentence said 5,295; missed was 1,068 not 1,081; the rate 16.78% not 16.99%; the description-bearing subset 1,052 not 1,066. Entry M1 said 15 of 29, 51.7%, where the denominator 29 came from the very narrow pattern that entry exists to complain about — the true count at both revisions is 48, so 15 of 48, 31.25%. Entry 6.5 described a repaired state in the broken state's present tense. **And `scripts/watchdog_vs_retry_budget_2026-09-09.py` had not run since the day it was written**: the 6.2 repair replaced the expression its regex matched, in the same commit that added the script, so it exited 1 and produced nothing while the entry went on citing figures it was supposed to be producing.

Artefacts under review, by path:

- `scripts/cdsfl_recover.py` — FIRST READ ordering and the staleness labels
- `bench/tests/test_first_read_prefers_the_fresher_source_2026-09-10.py` — 9 tests, 5 mutations
- `scripts/watchdog_vs_retry_budget_2026-09-09.py` — now accepts both expression forms
- `bench/tests/test_drift_seat_guard_assessment_2026-09-10.py` — the 6.7 repair
- `experimental_notes/CDSFL_MASTER_TASK_LIST.md` — entries 2.1, 6.2, 6.5, M1, V5, 6.7
- `scripts/ffafp_cycle_gamma_2026-09-10.py` — the stop criterion this whole programme runs under
- `bench/tests/test_done_markers_carry_evidence_2026-09-10.py` and `hooks/pre-commit` — round 3's repairs, for regression

## SECTION 2 — Use the harness

**Form your answer by RUNNING the machinery. A reply that reasons about these files without having executed them has not answered.**

Instruments that bear on this, and what each is expected to say:

- **`scripts/ffafp_cycle_gamma_2026-09-10.py`** — execute it. It applies this project's own two-sided gate: `gamma` at or above 0.30 AND 3 consecutive zero-discovery passes. The series is `[11, 4, 2, 3, 6, 2, 3, 2, 9]` and `gamma` is 0.451, so the `gamma` side passes and the count side does not. **Pass 9 found more than passes 6, 7 and 8 combined.** Ask whether a Duane slope computed over a series that rises at its tail is being read correctly, or whether the rise means the discovery process changed rather than that it is converging. If the gate is being read wrongly, that is the most important finding available in this brief.
- **`_estimate_gamma` in `bench/reference_runner_v3.py`** — the cycle script imports it rather than re-implementing it. Verify that. A stop criterion that re-implements its own gate can drift from the gate the runs use.
- **Wilson intervals** — every proportion in the corrected entries carries one, cross-checked by 2 tools. Re-derive at least 1 of them independently and say whether it agrees. 15 of 48 is quoted as 31.25%, Wilson [19.9%, 45.3%].
- **`severity` and `S_k`** — the additive standard holds that an addition nothing reaches is not additive. Each repair above is an addition. Ask, for each, whether anything reaches it: is the test collected, and does it go red when the property is violated?
- **`rho` and `nu`** — probably not implicated. Say so if you agree; if you can show a path by which restore ORDER affects novelty or overlap accounting, that is a finding the assistant missed.

## SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. A fix without a runnable falsifier that you have EXECUTED is a hypothesis, not a fix.

**Report the exact command you ran and the exact output.** Where you propose a change, give file, line, old text, new text. Where you claim a test is weak, DEMONSTRATE it: mutate the source, assert the mutation APPLIED and that it lands on a line the fixture actually executes, run the test, report whether it went red. A mutation that applies to the file but not to the executed path reads as SURVIVED and is not one — that has happened twice in this programme.

**The specific traps in this batch, each of which has already caught the assistant once:**

1. The freshness test's declared order and its true modification-time order COINCIDED in the live tree, so the suite could not tell a sorted list from an unsorted one until a fixture was rebuilt. Check whether that hole is really closed or merely moved.
2. The watchdog script now accepts 2 expression forms. A script that accepts anything cannot fail. Check that it still refuses a third, absent form.
3. 6.5's docstring claimed every test in the file runs the script and none reads its source, while 1 test checks a file mode and another reads a shell script as text. Check the corrected wording against what the file does.

**Work in the sandbox copy you are given. Do not modify the canonical tree.**

## SECTION 4 — What would refute you

State, before concluding, what evidence would overturn your own answer.

Specifically: if you judge these repairs sound, name the class of defect they would still let through. If you judge them unsound, name the cheapest addition that closes your objection and say whether it is worth its cost. If you believe the cycle should stop rather than continue, say what the gate would have to show for you to change your mind.

## SECTION 5 — Output shape

- `verdict` — CONFIRMED / REFUTED / PARTIAL on whether the 3 repairs hold
- `reasoning` — grounded in tool output you actually saw
- `findings` — each with file, line, severity, what is wrong, the fix, and the executed falsifier with its command and output
- `falsifier` and `falsifier_result` — the code you ran and what it returned
- `gate_reading` — your independent reading of the two-sided gate on the series above: CONVERGED or KEEP GOING, and why
- `refutation_condition` — Section 4's answer
- `strongest_disagreement` — your strongest disagreement with THIS BRIEF's framing. Disagreement is preserved as information; do not converge toward the brief.
- `passes_run` — how many

## SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could let a false completion claim stand, break a live run, or feed the founder a stale fact as a current one. Diminishing returns is this project's own criterion and it applies to you too. Do not generate findings for their own sake and do not police style.


<!-- verbatim-end -->



## Where the raw record lives

**Added 2026-09-11.** This note was written by hand before a builder existed and never named the directory it came from — so a coverage check over the notes reported it as having no record at all, which is the shape of false zero this project keeps meeting. It is named here.

`bench/logs/panel_round4_2026-09-10/` holds the brief, both seat replies, both tool logs, `BRIEF_CORRECTION_SIDECAR.md` and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/panel_records_2026-09-10/panel_round4_2026-09-10/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.

Written under CDSFL note standard v1.7 (26 August 2026).
