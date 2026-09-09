# Closing report, 2026-09-09

**2026-09-09T22:57:43+01:00 (Europe/London).** Companion to `~/Desktop/CDSFL_tts/Closing_Report_2026-09-09.txt`, which carries the same account for listening and omits the locators below.

**The two documents are separate resources for different readers**, per the founder's ruling of 2026-09-09 recorded in `memory/cdsfl_two_document_audiences.md`: the experimental notes serve a technical reader reproducing the work exactly; the TTS version serves a technical but non-coding reader. Neither is a simplification of the other.

**The full record is elsewhere and is not duplicated here.** `experimental_notes/CDSFL_OUTCOMES_LOG.md` holds every outcome and the reversibility census; `experimental_notes/ISSUES_LOG_2026-09-09.md` holds all 35 issues as they were found; `experimental_notes/CDSFL_MASTER_TASK_LIST.md` holds the per-item detail. This file is the index across them.

---

## State at close

| Measure | Value |
|---|---|
| Full suite | 5721 passed, 4 skipped, 1 xfailed, 0 failed, exit 0 |
| Task list | 60 entries: 19 done, 38 open, 1 blocked, 2 withdrawn |
| Commits | `0c0f450`, `41d52fe`, `2ef96a1`, `b593500`, `dd297ec`, all pushed |
| Paid dispatch | **none**, verified before the panel by resolving the seat list with `PANEL_ONLY=cc2,fable` and printing it: 0 paid seats |
| Issues logged | 35 (I1 to I35) |

---

## The panel finding, with locators

**`bench/reference_runner_v3.py`, the `exhausted` valve.** Added 2026-09-07 so an unresolvable critical "cannot block for ever". 2 functions read the flag — `FindingRegistry.open_crit_high_count` and `FindingRegistry.unverified_critical_count` — and between them examine 6 statuses. `_update_finding_statuses` set it for 4 and did `e.pop("exhausted", None)` for the rest, including **UNCONFIRMED**, the only status the A4 counter examines, and **REOPENED**, which the other reader examines.

Its only test was `bench/tests/test_panel_five_fixes_2026-09-07.py:78`, asserting the string `e.get("exhausted")` appears in the counter's body. It passed against dead code for 2 days.

Fixed by deriving `EXHAUSTED_VALVE_STATUSES` from the readers rather than listing statuses. cc2 found the UNCONFIRMED half in panel review; the REOPENED half was found on verification. 12 executing tests in `bench/tests/test_exhausted_valve_reaches_its_readers_2026-09-09.py`, 5 mutations, all caught.

**Why it became load-bearing.** The empty-ladder repair earlier the same day makes `routing_deferred` terminal for every escalated critical in the 1-seat arm, and `routing_deferred` is deliberately not A4-excluded. Executed: an UNCONFIRMED deferred critical gives `unverified_critical_count` = 2 against `irreducible_queue_count` = 2 and `max_irreducible_queue` = 2 — at the bound, not over it. The arm can neither converge nor halt.

---

## Completed items, by task number

| # | What | Evidence |
|---|---|---|
| 3.1a | Roster confinement, routing and sweep ON in all 3 arms | `scripts/roster_disjointness_2026-09-09.py`: 0 of 60 archived runs disjoint, Wilson [0.0%, 6.0%] |
| 3.2 | DeepSeek compensator's 3 silent failures made loud | `scripts/deepseek_falsifier_supply_2026-09-09.py`: 103 of 468, 22.01%, vs 325 of 1925, Fisher p = 0.0106, OR 1.389 [1.083, 1.782] |
| 4.1 | Escalation rule names MISCONFIGURATION, first, at all 5 sites | 8 tests calling `build_irreducible_queue_alarm` and asserting on its returned string |
| 4.2 | The simplicity note's wrong line removed | `memory/feedback_simplest_sufficient.md` |
| 6.1–6.5, 6.7 | Stop reasons, watchdog, logs dir, shared path predicate, monitor lifetime, drift assessment | `scripts/watchdog_vs_retry_budget_2026-09-09.py`, `scripts/archive_root_agreement_2026-09-09.py` |
| 7.1 (bounded) | 207 of 283 spelled numbers converted, 73.14%, Wilson [67.7%, 78.0%] | `scripts/spelled_number_repair_2026-09-09.py` |
| 7.2 | Note linter reached by the commit path | 5th guard in `hooks/pre-commit`, a ratchet |
| 7.3, 8.1 | Two-document distinction recorded; `rs` no longer hunts absent files | `git log --all`: 0 commits touching either path |
| L2 | Quote exemption survives a sentence boundary | `scripts/quote_exemption_effect_2026-09-09.py`: 8 removed, 0 added |

---

## Decisions with the founder

**CORRECTED.** An earlier version of this section was headed "The 6 decisions that need the founder" and read as a complete account. Those 6 are the ones **arising from this session**. Others were already standing, and the `rs` restore at 23:00 on 2026-09-09 surfaced them.

### The 6 that arose today

| Issue | Decision |
|---|---|
| **I23** | `exhausted_round_threshold` defaults to 8 while every arm sets `max_rounds: 8`, so `age >= 8` is unsatisfiable. cc2 proposes 6. Frozen pre-registration files. |
| **I16** | C0050: all 6 seats withdrew it as a claim about the review process. Falsifiable, but not against the object the harness offers. Two opposite pieces of work follow. |
| **I18** | `stash@{0}` holds a `# MUTANT M9` removing `cid in _handled` at `bench/reference_runner_v3.py:5898`. Guard verified intact; the stash still exists. |
| **I31** | `update_drift` has no production caller. Largest CUSUM excursion 0.5595 against a threshold of 2.0, 27.98%. Wire it or retire it. |
| **I28** | Task 6.6 needs root for `fs_usage`. Candidate-recording is achievable and must not be called attribution. |
| **7.1 TTS half** | 622 spelled-number sites across 138 of 486 Desktop TTS files. Unversioned, so not revertible. |

---

### Already standing before this session

| Source | Decision |
|---|---|
| RECOVERY.md, 2026-09-08 16:10 | The **absolute-path ruling** for seat confinement. Seats hold the absolute repo path by the 2026-08-23 ruling, so a cwd cannot confine a Bash-bearing seat; `_absolute_target` already takes a `repo_root`. |
| RECOVERY.md, 2026-09-08 16:10 | **Falsifier supply** — the Exp 45 halt cause, 5 of 14 criticals with no runnable check. Moved on both halves this session (task 2.1's union, task 3.2's measurement) but not closed. |
| RECOVERY.md, 2026-09-08 16:10 | ~~One run, two directories~~ — **CLOSED by task 6.3 on 2026-09-09.** |
| RECOVERY.md, 2026-09-06 04:05 | Promoting the corrected **S\* threshold** from shadow to live. Ruled for the simulated run; not for general use. |
| RECOVERY.md, 2026-09-06 04:05 | **Where reach belongs** — the fable/cc2 panel split, unresolved. |
| RECOVERY.md, 2026-09-06 04:05 | The **references section**, deferred to discussion by the founder. |

### A correction the restore itself caused

The `rs` protocol names `experimental_notes/CDSFL_Agent_Operational_Plan.md` as FIRST READ. That tracker still listed the **answer-key sealing** as HELD awaiting the founder. It was not: he executed it himself on **2026-09-07 at 22:03, 53 files into 1 archive, 0 plaintext keys left**, having driven home from his hotel to do it. The assistant read the stale line during the restore and repeated it in the resume pointer committed as `8f411e2`.

**The correct record already existed.** `CDSFL_MASTER_TASK_LIST.md`, written 2026-09-09 14:15, states he executed it *and* states the tracker was stale on it. **So the restore reads the older document first and with the greater authority** — a defect in the protocol, not only in the reading. Verified before striking it: `find` over `$HOME` to depth 4 and over the repository returns **0** files matching `*answer_key*.json`.

## What is not established

The panel's canonical-tree alarm cannot distinguish an assistant edit from a seat escape (**I27**); it fired on 14 files, all of them this session's own concurrent work, and confinement did hold — 0 canonical-path references in either seat's tool log. The dispatcher's DEFAULT is 3 paid seats, with only an environment variable preventing it (**I20**). And 3 of this session's own measurements used a broken instrument before being corrected (**I35**) — in each case the defect was in the ruler, not the code under study.

Written under CDSFL note standard v1.7 (26 August 2026).
