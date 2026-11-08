# The gates refused 3 times and were right every time

8 November 2026, 09:14 GMT

## Summary

3 entries advanced in the window after the morning report was delivered. **B20**'s enablement question is settled by execution: the 2 switches it names are the complete set, and the middle setting records a decision while taking 0 actions. **B122** closed, state `DONE`, status `COMMITTED`, `ruled: 2026-11-06`. **B135**'s recommended fix was measured and reaches 0 of the 13 cases it was written for. A guard was built for the `queue-operation` branch of `scripts/harvest_tickets_2026-10-17.py`, live code that no test in the suite reached.

The more transferable result concerns the project's own gates. 3 refused work in this window, all 3 correctly, and 0 of the 3 problems were noticed before the gate stopped them. That matches `scripts/what_caught_my_errors_2026-10-29.py`, which measured 0 of 7 noticed unaided, exact binomial p = 0.0078.

## B20: the 2 switches are the whole set, and they are independent

Producer: `scripts/are_the_two_switches_the_whole_set_2026-11-08.py`, 5 cases, exit 0.

The entry pinned a **count** of 2 gates. `feedback_pin_a_set_not_a_count_2026-10-16` records checking 2 instruments when there were 3, so the count was attacked rather than accepted. The attack failed, confirming the entry.

Driving `drive()` in `bench/tools/cy_actuator_2026-11-03.py` through its own `_runner` seam with both switches on gives 3 invocations, `resumes_driven = 2`, `acted = [True, True, False]`, and `--resume` appended on invocations 2 and 3. 3 further conditions exist and none is a switch:

| condition | why it is not a switch |
|---|---|
| the pulse must name a pid that has exited | `cy_pulse.json` is written by `scripts/cy_watchdog_2026-10-02.py` during a run |
| `launch` must be given | a required positional argument |
| `resumes < max_resumes` | `--max-resumes` defaults to **3**, read out of argparse by AST rather than assumed |

**What was not known**: the switches are independent, so the setting is 3-valued.

| setting | decisions recorded | actions |
|---|---|---|
| both off | 0 | 0 |
| `--hil-review` on, `--act` off | `RESUME` with all 9 evidence fields | **0** |
| both on | `RESUME` | up to `--max-resumes` |

The middle row is a dry-run arm. `classify()` reaches `RESUME` and `record()` writes it to `actuator_decisions.jsonl` with `exit_code`, `pid`, `pid_alive`, `pid_known`, `pulse_present`, `pulse_age_s`, `pulse_ended`, `rounds` and `events`, re-invoking nothing. Across 352 archived run directories, 0 ever set `hil_review`: Wilson 95% [0.000000, 0.010795] on statsmodels against an mpmath closed form agreeing to 7.0e-18, Clopper-Pearson [0.000000, 0.010425] on scipy against the k=0 closed form `1 - 0.025^(1/352)` agreeing to 3.5e-18, exact binomial p = 2.180075e-106. Re-measured by the instrument that produced it, `scripts/the_unattended_loop_has_never_been_reachable_2026-11-04.py`; the superseded reading was 351 runs with Wilson upper 0.010826.

**The first measurement reported the opposite.** An empty temporary directory meant no pulse named a process, so `classify()` correctly returned `HOLD` on an UNKNOWN rather than a known exit — which reads as a third gate. See `feedback_a_probes_location_can_manufacture_the_failure_2026-11-02`. The no-pulse case is retained in the producer as a labelled negative control.

**2 stale figures in the entry were repaired.** The run count moved 351 → 352. And 2 line citations written into the entry's *prose* had drifted by +33 from commit `623d157b`: 21297 now holds a comment about a stall and 21361 a comment about topic exhaustion, while the gates sit at 21330 and 21394. The fix names the `CITATIONS` keys `A2.gate.round` and `A2.gate.phase` instead of writing the new numbers into a sentence no guard reads, because that is how the first pair drifted.

## B135: the recommended fix reaches 0 of its 13 targets

Option 1 of the entry says to execute the helper and compare its 2 routes, pointing at `TestEveryHelperIsExecutedNotJustRead` in `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`, which discovers a producer by `def _iv` in its source and calls `_iv(k, n)` for 2 intervals and a cross-check magnitude.

Measured against the authoritative 13, reproduced with the producer's own `LOOSE` gate rather than a hand-rolled predicate: **0 of 13 define `_iv`**, Wilson 95% [0.000000, 0.228095] on statsmodels against an mpmath closed form agreeing to 9.5e-17, Clopper-Pearson [0.000000, 0.247053] on scipy against `1 - 0.025^(1/13)` agreeing to 6.5e-17. The 13 compute Wilson inline with a locally spelled sample size.

So option 1 carries an unnamed prerequisite: propagate the canonical `_iv` into 13 producers that are already committed and already cited as evidence by other entries. The cheap alternative is option 2 again — `LOOSE` already matches 13 of 13 **by construction**, since `hidden` is defined as strict-miss ∧ LOOSE-hit — and that is the treadmill which already broke this entry's own producer. **Neither was taken.**

The denominator moved 154 → 165 with the numerator held at 13, so the share fell 0.084416 → 0.078788 without a producer being repaired. Read the count.

## B102: a repair recovering 206 of his messages had no test reaching it

`scripts/harvest_tickets_2026-10-17.py:440-446` handles `type == "queue-operation"` with `operation == "enqueue"` and takes `d["content"]`, the top-level key the harness uses for a message typed mid-turn, setting `role = "user"` by construction.

Measured 2026-11-08: `queue-operation` appears **0** times and `enqueue` **0** times in `bench/tests/test_ticket_harvest_2026-10-17.py`, and the only guard in the suite mentioning either is `test_his_words_are_read_from_both_records_2026-11-03.py`, which guards the union reader `scripts/his_messages.py` rather than the harvester. A live branch recovering 206 of 1,421 distinct messages was an addition nothing executed — the symmetric half of `additive-standard`.

New guard: `bench/tests/test_a_queued_marker_is_harvested_2026-11-08.py`, 7 tests, pytest exit 0 in 0.22 s. It calls the real `from_chat` with `TRANSCRIPTS` monkeypatched to a fixture, so no production code changed to make it testable.

- Asserts `source == "chat:user"` and `ruled == ts[:10]`, the property B102 names: an empty `ruled` is indistinguishable downstream from a message never ruled on.
- Anti-vacuity on the fixture itself, because `MARKER` requires the token at end-of-string; a fixture reading `pf the detector ...` would pass every assertion while testing nothing.
- Negative control: `operation: "remove"` must yield 0 rows.
- 3 of 3 mutations red — killing the branch, setting `role = "?"`, accepting any operation. Subject restored from saved bytes and verified byte-identical by sha256, not by `git checkout`, per `feedback_a_harness_must_restore_what_it_found_2026-11-01`.

**A claim of mine is withdrawn**: that 4 other producers needed migrating to the union reader. `scripts/founder_decision_ledger.py` and `scripts/triage_open_founder_decisions.py` read `journal.jsonl`; `scripts/pass_b_his_rulings_2026-10-11.py` reads the memory directory; `scripts/depth_and_breadth_are_measurable_2026-10-25.py` reads only `tool_use` blocks. The only blind in-scope consumer is `hooks/ffafp_audit.py`, hardlinked at inode 755421521 with link count 2, and it is **not** called defective: a mid-turn message does not start a turn, so excluding it is defensible for turn segmentation.

## The 3 refusals

1. **`task_list_markers.set_marker`** refused B122 as `DONE`: `scripts/the_line_caps_were_never_his_2026-11-06.py` sits outside `bench/tests`, so nothing in the suite runs it. Evidence reduced to the 2 guard files, both asserting on the entry's own claims.
2. **`scripts/morning_report_build_2026-10-12.py --check`**, exit 3: *AUTHORED DETAIL for an item no longer live: task:B122*. Closing B122 made its decision record stale. Whether the closure changed the 29 had been checked — it does not, the builder never rendered B122 — but whether it invalidated the record behind them had not. See `feedback_a_ruling_on_one_surface_breaks_the_other_readers_2026-11-06`. Moved to `_archived_authored_detail` with a `_moved_log` entry, per that archive's own rule: POINT, NEVER PRUNE. Top level 50 → 49 keys; check then passes at 47 derived items.
3. **The per-file lint check** in `hooks/pre-commit`, which blocks any commit that raises a note's finding count: `CDSFL_MASTER_TASK_LIST.md` went 24 → 25 findings, the addition being `UNNAMED SUBJECT`, raised against a sentence of mine that referred to a figure by a bare demonstrative inside the very amendment arguing that subjects must be named.

**The diagnosis of refusal 3 was wrong twice first.** A comparison linting HEAD's copy from `/tmp` without `--as` reported **337** findings against 24, because `scripts/note_vagueness_lint.py` scopes rules by logical path and a `/tmp` path fires every Rule 27 exemption the task list is scoped out of — `feedback_compare_lint_counts_like_with_like_2026-10-15`. A second counted `para` lines with `grep -c` instead of reading the summary, over-reporting both sides by 1. Like with like, `--as` the same logical path: HEAD 24, corrected copy 24.

## 4 wrong comparisons in 1 area

| what was fed | what the predicate decides on | result |
|---|---|---|
| entry titles | full entry text | `PARK` for 36 of 36, `decision_required` empty |
| full entry bodies (to 101,163 chars) | a single obstacle | cross-matches on `KW_ONLY`, `task_list_markers`, `ticket_id`; a ticket raised on a false premise, now `INVALID` |
| strict-miss alone | strict-miss ∧ `LOOSE`-hit | 128 instead of 13 |
| preserved copies | the harvest original | 7 of 7 "mismatches" |

The 4th is the clearest: `scripts/seat_evidence_is_gitignored_2026-09-30.py:190` states plainly that *a preserved copy is NOT byte-identical to the harvest original — provenance is prepended at rescue time, with the original's sha256 recorded inside it*. Checked against the originals, **7 of 7 match exactly**, so the provenance chain is sound and there was never an integrity problem.

Each returned a confident, reproducible number. 3 of the 4 were caught only because the number disagreed with something already known. The cheap check in every case: read the code that **writes** a figure before comparing against it.

## Outstanding

2 things await the founder: the 29 decisions, and whether to push 573 local commits. Nothing has been pushed.

The 29 are an unanswered backlog, not a fresh set — 0 of 29 carry a ruling that still settles them, and 29 of 29 were already put to him in a dated file; 3 carry a ruling on a different question and 26 carry none. Producer: `scripts/are_the_twenty_nine_new_or_repeats_2026-11-07.py`, exit 0. Both decision surfaces agree on all 29 by a z3 bijection and a SymPy `FiniteSet` equality.

B20 is the first of the 29. `scripts/blocker_triage.py`, given the obstacle rather than the entry, returns `BLOCK` plus `HIS DECISION` and instructs that it be carried to him as a decision rather than worked.

Written under CDSFL note standard v1.9 (1 November 2026).
