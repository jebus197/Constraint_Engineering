# Overnight work is blocked on one login

28 October 2026, 02:55 GMT (2026-10-28T02:55:27+00:00). Branch `sim/shakedown-2026-09-29`, commit `2f3388f6`, pushed, working tree clean at the time of writing.

## The one action that is needed

The `claude` CLI is logged out. `claude auth status` returns `loggedIn: false`, `authMethod: none`, and a direct call prints `Failed to authenticate: OAuth session expired and could not be refreshed`. The remedy is `claude login`, which is interactive and only the founder can run.

Registered as `pf:3adecb80188f`.

## Why one command matters more than it looks

Every free panel seat dispatches through `claude -p` (`bench/confer_maths_panel_2026-09-05.py`, seats `cc2` and `fable`, both Max subscription), and every seat in a simulated run dispatches through `claude -p --model` (`bench/tools/sim_dispatch_shim.py`). The same expired session therefore blocks 3 things at once:

1. The panel review of tonight's fixes, which the founder asked for before any run.
2. The simulated run itself, which was to be the overnight work.
3. A backlog larger than either: of **36 open `wr` items in the register, 30 are marked PANEL REQUESTED** — 0.833333, Wilson [0.681092, 0.921296]. Every one is a review the founder asked for and every one needs a free seat.

Reproducible with:

```
python3 scripts/register.py --kind wr --status OPEN --limit 0
```

## A second, smaller item in the same place

`hasTrustDialogAccepted` is `false` for this workspace in `~/.claude.json`, so the CLI ignores 19 `permissions.allow` entries from `.claude/settings.json`. Seats would run degraded even once the login is restored. Fix: open Claude Code interactively here once and accept the trust dialog, or set that key to `true` under this project. **Not touched** — it is a security setting and belongs to the founder.

An API key was deliberately not used as a substitute: that moves free seats onto paid credit, and extra usage is disabled with 0.00 GBP spent, so it needs explicit authorisation.

## The aliveness test earned its keep on its first real occasion

The founder accepted the 20-second stagger on 2026-10-28 and observed that it is a mitigation intended to be paired with the model aliveness test. That pairing was tested for real within the hour. The dispatcher probed both free seats, received nothing across 3 attempts each, and refused the whole round. Without it, a 19,888-character brief would have gone to 2 dead routes.

`qs:6b0997d1f6b9` (the stagger value) is now CLOSED with his words as verification. His completion-barrier question is registered separately as `qs:157b6ddc201f`.

## What was completed, independent of the login

`pf:b705bdbab3a9` — the ticket-store defect he asked to be fixed — is CLOSED, with an honest limit recorded in the resolution.

**The root cause was not what had been reported to him earlier.** The reported cause was subject-tier over-matching on shared symbols. The actual cause: `from_chat()` in `scripts/harvest_tickets_2026-10-17.py` passed no `anchor`, where `from_responses()` always has. An anchor is the explicit identity `_distinct()` uses to escape the subject tier, so every chat-sourced item arrived with nothing to distinguish it. All 5 questions raised by hand on 2026-10-27 carry neither `task_ref` nor `anchor`; 4 had to be re-raised.

**And the chat half had never worked at all.** It returned 0 rows for every window back to 2026-08-01. Its prefilter was `r'"(fr|pf)[:\]]'`: it required the marker immediately after a double quote, which only happens at the start of a JSON string value, and it knew only 2 of the 4 `KINDS`. `qs` and `wr` could never be harvested from chat, and `qs` is the kind he instructed on 2026-10-19.

### Two hypotheses of mine, refuted by my own instruments

| Hypothesis | Measured result |
|---|---|
| The suppression rate rises as the store grows | **Flat and high**: blocked share 0.8370 at 250 tickets, 0.9310 at 750, 0.8644 at 2,857. The blocked *set* cannot shrink (z3 `unsat`), but the blocked *share* is not the blocked set. |
| Over-matching comes from overloaded identifiers acting as stopwords | **No subject is common**: max document frequency 9 of 2,857, **median 1**, with 210 of 354 subjects naming exactly 1 ticket. The existing selectivity rule in `scripts/blocker_triage.py` would have caught nothing. |

Producers: `scripts/the_subject_blocklist_grows_with_every_close_2026-10-28.py`, `scripts/the_chat_half_was_blind_2026-10-28.py`.

### A third correction, against a flattering headline

An earlier draft quoted a 0.92 discard rate as though proposals had been lost. That compared 2 raw-line predicates with each other. Decoding all 1,185 candidate lines across 249,664 transcript lines, the messages whose text actually **raises** a marker number **0**. The defect was real and its cost was 0 lost proposals; those are 2 separate facts.

### Fixing the prefilter alone made it reachable and useless at once

Of the first 31 rows returned: 24 were this session's own Stop-gate output quoted back, 3 compaction summaries, 4 citations of existing ticket ids (`MARKER` accepts `pf:`, the form of every reference). A register that files its own prodding as new work is circular. `CITATION`, `HARNESS_ECHO` and `CODE_SPAN` filters added; the last was found by the P-pass, when the single surviving row was my own message containing the literal `` `[qs:...]` ``.

### His question on the combined word-search and issue-ID method

**Implemented and live.** `fr:11b8625abc85` (CLOSED) is the inverted word index; `TicketStore.candidates()` consults all 4 tiers — exact hashed id (`tid_of`), reworded content hash (`nid_of`), subject, word overlap (`similar_by_words`). Executed to confirm the index builds and answers.

**Not the remedy here**, and that was already established: requiring the word layer to corroborate a subject match was tried against this exact defect and refused as circular, dropping the store from 4-of-4 to 1-of-4 on known rediscoveries.

## B37, answered on evidence

His proposal: *"Can this test not be run sequentially, similar to your sq MC command? Why risk choking up my 8GB machine and making it unusable, or risk the tests failing to complete, when the tests can be run sequentially, to the same effect?"*

His concern is right; serialising is not the repair that applies.

| Hypothesis | Verdict |
|---|---|
| The nested run is parallel and needs serialising | **Refuted.** `hooks/pre-commit:357` runs `python3 -m pytest -q -p no:cacheprovider $GUARDS` — no `-n`, no xdist; `pytest.ini` has no `addopts`. Both runs were already serial. |
| A fork inside a threaded process deadlocks on an inherited lock | **Refuted.** Python 3.13 on macOS defaults to `spawn`; nothing in the tree calls `set_start_method`. |
| A thread-method timeout cannot reclaim a process blocked in `os.waitpid` (**mine**) | **Refuted by execution.** Against an unbounded `subprocess.run(["sleep","25"])` under a 3 s limit, the run ended in **3.3 s**, overshoot 0.3 s. |
| The per-test limit had been replaced by a whole-run limit | **Supported.** B37's own record says that run used 1800 s *for the whole run*. A whole-run limit cannot reclaim an individual test. |

**The answer to the ruling B37 was waiting on:** a test may run the hook's full guard list, because the cost is bounded and known, **provided the per-test limit is never replaced by a whole-run one.** Now guarded by `bench/tests/test_the_nested_suite_stays_bounded_2026-10-28.py` (6 tests, 3 of 3 mutations red).

**Residual risk, real but not the cause:** 13 of 22 subprocess launches across the 3 nested-hook files carry no `timeout=` — 0.590909, Wilson [0.387348, 0.767442] — all 13 in `bench/tests/test_precommit_restages_repairs_2026-09-11.py`. Ratcheted. A first count by `grep -A3` said 3 of 16 where the AST says 13 of 16: line proximity is the wrong instrument for a question about call boundaries.

**The guard found one of its own assertions vacuous.** Its first version asserted `timeout_method in ("thread","signal")` — pytest-timeout's only valid values, so any other setting makes pytest exit 3 with `ValueError: Invalid method` before the test runs. Narrowed to `("thread",)`, the one method measured here, so switching to the valid-but-unmeasured `signal` now goes red and asks for the measurement.

## Seven questions closed using his own words

The register held 10 OPEN `qs`; 7 already carried his ruling of 2026-10-28. Reporting those back would repeat a failure he has named — *"Then if I already ruled. Why are you presenting it as a decision required from me again?"* Each is closed with the exact annotation line as verification, read with `scripts/read_founder_responses_2026-10-11.py`.

Closed: `qs:3cef02fdd3bb`, `qs:0c69884fa97f`, `qs:db9fb60889f5`, `qs:507deab063d2`, `qs:01e5959468cf`, `qs:49c2c0ed167e`, `qs:a66794e63539`, plus `qs:92f807974742` and `qs:6b0997d1f6b9`.

## What is actually awaiting him — 3 questions

1. **`qs:c2e25a1e79c1`** — re-measure the 0.7 severity cut against its pre-registered rubric. His ruling made this conditional on the convergence question closing. It has not closed; it is now a countdown needing 30 labelled closes against the 8 that exist, so the trigger has not fired. Cheap and queued.
2. **`qs:bb639f25d8ef`** — is a marker-gated chat reader worth keeping? It is now correct rather than blind, but cannot capture the item it was justified by, because that item carries no marker. Harvesting everything would flood a 2,858-ticket store.
3. **`qs:157b6ddc201f`** — his own star-topology question. The stagger's measured bounds govern **starts**; his question is about **completions**. Recommendation: instrument it in the next run by recording per-seat start and completion times, which costs only logging.

## What did not happen

The panel review did not run and the simulated run did not start. Neither was skipped by choice. The brief is written and validated against all 8 required checks: `bench/logs/fix_review_panel_2026-10-28/BRIEF.md`, 7 changes, including the adaptive quiet-run rule as a **pre-registration** for the panel to attack before it is frozen, with a decision rule stated so it can fail.

Writing it cleared a real debt: the blind round `the_quiet_run_is_not_the_lever_2026-10-25` never received its joint half, and the dispatcher refused a new blind round until it was resolved. Recorded SUPERSEDED by tonight's round in `bench/directives/universal/joint_round_debt.json`, with the reason stated, because change 7 carries the same question forward with his rulings applied.

The brief's own figure check caught a stale number before any seat saw it: the cross-kind share had moved from 0.742647 to 0.742718, because the store grew by the 2 tickets raised this session.

## Tests and commits

- Pre-commit board at `2f3388f6`: **1,442 passed, 0 failed**.
- 177 pass across the 13 ticket-related files, 24 written tonight, **6 of 6 mutations red**.
- Nested-suite guard: 6 tests, **3 of 3 mutations red**.
- Verdict rows recorded for all 11 of his annotations of 2026-10-28; the freshness Stop gate reports 0 unread.

Written under CDSFL note standard v1.8 (17 October 2026).
