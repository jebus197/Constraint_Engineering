# Everything awaiting your verdict, consolidated

2026-10-30, 10:05 GMT (Europe/London). Branch `sim/shakedown-2026-09-29`, HEAD `8a05a1e3`.

Technical companion to the spoken version, `All_Verdicts_Consolidated_2026-10-30.txt`. It carries the file paths, line numbers, commit hashes, producer scripts and test counts that the spoken form omits under Rule 6. The spoken version is the one to listen to; this one is for checking a figure.

**This file replaces 5 spoken files** written from 17:42 on 2026-10-29 to 05:23 on 2026-10-30. Where they disagree with this one, this one is current. Section 6 names what is superseded.

## 1. Your 4 open questions

Every question recorded in the register and still OPEN. 54 recorded in total, 48 CLOSED, 1 DEPRECATED, 1 DUPLICATE. Source: `python3 scripts/register.py --kind qs --limit 0 --json`.

| id | reference | question |
|---|---|---|
| `fd5e6e379930` | B39 | Is severity a confidence within a range, and should merged assessments be combined at all? |
| `8755c675e3a9` | — | Should the 16 findings closed with a non-curing fix be reopened? |
| `4af75486305a` | — | What false-alarm proportion for demotion? 0.05 recommended |
| `b4fc0c6c0278` | — | Run both baseline arms after the 3rd convergence rather than before it? |

The 16-findings figure: 16 of 69 entries in the first commissioning arm of 2026-09-21, **0.231884**, Wilson 95% [0.148079, 0.343968]. The 3 categories (cured 25, not cured 16, instrument could not look 28) sum to 69 exactly, asserted rather than assumed.

The baseline-arm figure: the design names a run of 2026-10-03 as the fixed side. The branch has moved **341 commits** since, 51 touching the runner and 10 the composer.

## 2. The 6 open task entries

Markers in `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, verified against `scripts/task_list_markers.py --summary` (186 entries: 6 open, 167 done, 4 deferred, 9 withdrawn).

| entry | marker line | what it needs |
|---|---|---|
| B21 | 1098 | 3 panel questions; brief at `bench/logs/the_role_layer_b21_2026-10-30/BRIEF.md` |
| B22 | 1113 | a free-seat panel dispatched |
| C1 | 1130 | one scalar: `CLAIM_CHANNEL_WEIGHT`, `bench/claim_ledger.py:195`, currently `0.0` |
| B41 | 1345 | your go-ahead |
| B50 | 1369 | a ruling on the corrected price list |
| R1 | 1404 | authorisation, and it costs money |

### B50, the only genuinely new ruling

Verified against the live tree today, all claims holding:

- live store `bench/state/immune_memory.json`: `experiment_count: 1`, `experiment_ids: ['free_run3_no_spec_20261028T235529Z']`
- archive `bench/state/immune_memory_archive/immune_memory_20261017T095236Z.why.json`: `state_when_archived.experiment_count: 6`, reason recorded as your 2026-10-16 ruling verbatim
- `ImmuneMemory.load` at `bench/reference_runner_v3.py:21620`, `record_experiment` at `:21630` — load precedes record, so the path accumulates and a count of 1 is correct

**Option 2 priced, which it was not before.** Producer: `scripts/what_does_option_two_actually_cost_2026-10-30.py`.

| constraint | observed | runs needed | 95% range |
|---|---|---|---|
| `totals[1] >= 50` | 4 in 1 run | 12.5 | [4.9, 45.9] |
| `totals[5] >= 50` | 9 in 1 run | 5.6 | [2.9, 12.1] |
| flaw class 8 must appear | 1 experiment of 6 | **17** | — |

Binding: **about 17 live runs**. Exact Poisson limits from `scipy.stats.chi2.ppf` cross-checked against an mpmath inversion of the regularised incomplete gamma, asserted equal to 1e-6; the geometric figure checked against a 40,000-draw NumPy simulation. The first cross-check was wrong by a factor of about 8 because it inverted the 0.975 tail instead of 0.025; the producer now asserts agreement rather than printing it.

**2 further findings in B50's own evidence.** The reset wrote 2 archive files 61 seconds apart, `immune_memory_20261017T095135Z` and `...095236Z`, with identical sha256 `fc5779de…` and identical `experiment_count: 6`, so `restore_with` has 2 equivalent forms. And `experiment_count` is 6 while `experiment_ids` retains 3, so a rare class's per-run probability is not single-valued: 17 runs against 1 denominator, 8 against the other.

## 3. The decision with a number attached

`scripts/precommit_gate_cost_2026-09-10.py` `repository_reach()`: the gate's `GUARDS` list names **73** test files; `bench/tests/` holds **727**; **654 unreached**, share **0.8996**. A census of every test file, so no interval.

Cost of adding the newest 6 guards: **75 tests in 18.88 s** against a gate measured at **1,588 tests in 326.65 s** today, so roughly **6%** per commit. A ratio of 2 timings, so no interval.

## 4. Not yours to decide

**The 30 panel-labelled tickets are stale recording, not a backlog.** Read by your words rather than the label: 19 unconditional, 6 conditional, 5 not panel requests. Of the 11 whose subject traces to a task entry, 10 have every referenced entry closed — **0.909091**, [0.622642, 0.983768], exact test p = 0.005859; the exception is C1. **94 panel records exist against those 30 requests**, exceeding requests in every month (14 against 5 in August, 47 against 20 in September, 30 against 11 in October). The owed work is matching records to requests, which is reading, and it is mine.

Open-ticket totals, from the listing rather than `--summary`, which **ignores `--kind` and returns the same global figure for every kind** — a defect worth fixing:

| kind | total | OPEN |
|---|---|---|
| `qs` | 54 | 4 |
| `fr` | 118 | 5 |
| `pf` | 2,685 | 23 |
| `wr` | 59 | 36 |
| all | 2,916 | 68 (0.023320, Wilson [0.018437, 0.029457]) |

**The identity collapse is live, by execution not by reading.** `tid_of("pf", <text A>, task_ref="B50")` and `tid_of("pf", <text B>, task_ref="B50")` both return `2835f264ae18`. `bench/ticket_store.py:280` states the design: where a reference exists it is the whole identity and the text is excluded. The fix changes the identity scheme, so it needs you.

**Paid-dispatch gate**, re-measured today by `scripts/which_paid_routes_pass_his_gate_2026-10-29.py`: 1 of 155 modules consults the ledger, **0.006452**, Wilson [0.001140, 0.035636], exact beta [0.000163, 0.035420]; of 34 live entry points, 10 can issue an outbound request and 0 consult it.

## 5. The full board

`python3 -m pytest bench/tests/ -q -p no:randomly` on a frozen tree at `80f4dfcd`, 2 nodes deselected:

**7 failed, 13,625 passed, 20 skipped, 2 deselected, 25 warnings in 5634.07 s (1:33:54).**

6 of the 7 are B50's, in `bench/tests/test_immune_memory_evaluation.py`. The 7th was `bench/tests/test_operational_scripts.py::TestTruncatedListsStateTheirRemainder::test_no_script_prints_a_capped_listing_in_silence`, reporting `scripts/rebuild_morning_report_markdown_2026-10-30.py:196` as printing `diff[:40]` with no statement of the remainder. Fixed in `8a05a1e3`; the cap is now `_DIFF_LINES_SHOWN` and the generator's guard gained a test pinning the arithmetic, 2 of 3 mutations red (the third moves the constant, which the guard reads, so both sides move together by design).

The board also reports: **task 6.7 is marked DONE and names the failing immune-memory file**, a completion claim with no support. It resolves when B50 does.

**The prediction of 7 to 9 was correct, and was twice reported as failed.** Both reports were wrong. The cause was an instrument counting `F` and `E` characters in the progress stream while the output file also held the banner line naming the prediction, whose own letters were counted. Projections of 17.86 [13, 23] and 12.25 [11, 15] were both built on that contaminated count.

**The 2 deselected nodes**, named rather than counted:

- `test_vault_guard_timeout_has_headroom_2026-09-29.py::TestTheCapAndTheCostHaveNotDriftedApart::test_the_cap_leaves_real_margin_over_the_measured_cost`
- `…::test_the_old_cap_would_now_fail_this_check`

Only those 2 request `measured_idle_seconds`; the file's other 5 nodes ran. That fixture carries `subprocess.run(..., timeout=900)` with an authored message instructing the reader not to raise `VAULT_STATUS_TIMEOUT_S`. z3 returns **unsat** for that message being reachable under `pytest.ini`'s `timeout = 300`; SymPy agrees reachability needs the fixture's own timeout below **150 s**, since it loops twice. **A diagnostic written for this exact condition cannot fire.** Needs your ruling: raising the global cap and lowering the fixture's timeout are different decisions.

Related, found in the same run and not repaired: `bench/tests/test_precommit_guard_2026-09-09.py:170` hardcodes `timeout=180` and carries no `@pytest.mark.timeout`, while line 362 carries `@pytest.mark.timeout(1200)` with `_COMMIT_TIMEOUT = 900`. Its `git commit` child ran **293 s**. It was designed to be fast by removing `python3` from `PATH`, so the isolation it asserts is not biting.

## 6. Superseded — skip it

| the earlier files say | current |
|---|---|
| 12 entries open | 6 |
| B47 needs your ruling | closed on your 2026-10-29 ruling, 4 of 4 conditions verified by execution |
| C1 needs an architecture ruling | ruled and shipped; only the weight remains |
| B50 is 2-and-4 | 1-and-5, and the mechanical half is a trade |
| 30 panel requests outstanding | stale recording; 94 records against 30 requests |
| claim-channel wiring is 1 line at 2 sites | both sites are pure arithmetic with no ledger access; threading it is a design change |

## 7. Built this morning, needing nothing from you

Commit `8a05a1e3`, 11 files, 506 insertions, gate green at 1,588 tests.

`scripts/blocker_triage.py` `blocks_progress` opened with `lines = lines[:end_of_entries(lines)]`. The sentinel `# SUPPLEMENTARY LIST` sits at index **865**; **72 of 186** entries begin after it, all carrying real markers, including all 6 OPEN. z3 returns **unsat** for an entry at or beyond the cut being scanned.

Repair: `next_section_start(lines, after)` searches from the entry's own start, preserving the 2026-09-17 property exactly; `body_bounds` is the single definition of an entry's extent and **all 6 call sites now use it** — the idiom `else tlm.end_of_entries(lines)` returns 0 hits across the tree.

Unmasked defect: the term extractor's kebab branch matches any hyphenated word, and **1,028 of 2,686** distinct terms across the 186 bodies are hyphenated English — **0.382725**, Wilson [0.364524, 0.401262], Clopper-Pearson [0.364294, 0.401413]. Restricting it to CLI flags took 6 of 6 reported-as-blocking back to 3.

**Rejected on measurement**, recorded so it is not proposed again: requiring the term and the dependency phrase on the same line moved nothing — 6 of 6 before the restriction, 3 of 3 after — because this project writes 1 paragraph per line at about 1,100 characters.

Guard: `bench/tests/test_the_triage_can_see_the_whole_list_2026-10-30.py`, **20 tests, 5 of 5 mutations red**. 136 tests across the 11 dependent files pass.

Side effect: before the repair the final entry had a body of **0 characters** in 5 instruments, because the boundary lies before it begins. Its true body is **5,967 characters**.

## 8. The one recommendation

Rule on B50 and the identity collapse. Both are small, both unblock mechanical work, and the identity collapse is corrupting the register while it waits. Everything else here can sit.

Written under CDSFL note standard v1.8.
