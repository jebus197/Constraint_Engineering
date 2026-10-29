# Decisions awaiting the founder, 29 October 2026

Prepared 10:51 GMT at `d3d7fb9a` on `sim/shakedown-2026-09-29`, pushed. **12 items need his answer**, grouped by the kind of answer each requires. A closing section separates what is owed by the assistant, so the 2 are not confused.

Every proportion carries a 95% interval computed twice by independent methods that agree to the printed digits (`statsmodels` Wilson against a NumPy closed form), with exact Clopper–Pearson given alongside where the denominator is small. The headline was checked a third time in **Wolfram Language**, returning `{0.09972945195171447, 0.12260366537401539}` against `[0.099729, 0.122604]` — reported with attribution to Wolfram Language, with the open-source tools remaining primary. **That figure moved while this document was being written**, because the register grew by 5 tickets as the session's own bookkeeping landed; the check caught it before he read it rather than after.

**1 blocker has cleared and is not carried forward.** `experimental_notes/Overnight_Work_Blocked_On_Login_2026-10-28.md` reported all overnight work blocked on an expired CLI login. `claude auth status` now returns `loggedIn: true`, `authMethod: claude.ai`, so the free seats and the simulated run are reachable.

## A. Things only he can do

### 1. Authorise the restart of Exp 53, the zero-plant control — entry R1

Ruled twice, 2026-08-07 and 2026-09-06, carried 33 days. It is a paid run.

2 reasons were recorded. **Money stands.** **The dependency named in the entry is stale:** A1–A8 and A10 are `DONE`, A9 is `WITHDRAWN`, so the A1 to A10 engineering work the entry says it waits on is finished. `scripts/blocker_triage.py` classifies it `BLOCK` + `NEEDS PERMISSION — IRREVERSIBLE`.

**Recommendation: authorise.** The gate is clear, it is the cheapest outstanding run, and 33 days is the longest carry on the list.

### 2. The workspace trust flag

`~/.claude.json` carries `hasTrustDialogAccepted: false` for this project, so the CLI ignores the **20** permission entries in `.claude/settings.json`. Seats run degraded even with the login restored. Untouched deliberately: it is a security setting and his.

**Recommendation:** accept the dialogue once interactively, rather than have the flag written for him.

### 3. Whether a paid API key may substitute for a free seat

Declined as a workaround when the seats were unreachable. It would move free seats onto paid credit; extra usage is disabled with 0.00 GBP spent against a 150.00 GBP monthly limit.

**Recommendation: decline as a standing substitute.** The free route works again, and a standing fallback removes the pressure to repair it next time. A per-occasion authorisation is the narrower form if he wants it.

## B. Rulings on proposals

### 4. B47 — base the memory check on the last save that finished cleanly (Option 1 of B29)

`scripts/cdsfl_sv.py`'s `memory-updated` check measures the memory directory against the **previous save**. Sound for a session's first save; wrong for a follow-up, whose predecessor is the save whose memory it is asking to see again.

He asked on 2026-10-19 whether Options 3 and 1 compose. They do and neither is redundant: Option 3 (built) pre-checks the cause of **7 of 14** follow-up saves in history; the other 7 have a cause a staleness pre-check cannot see.

**It cost time 4 times in the session just ended.** The fourth refused a commit carrying 1 line of bookkeeping, because the memory entry written minutes earlier timed `0.0 hours BEFORE the previous sv commit`. Satisfying it would have meant writing a second memory entry not owed — gaming the check — so that record is deliberately uncommitted. **This document's own markdown mirror is blocked by the same check, for the fifth time.**

**Recommendation: build Option 1.** Have the save record whether its own postconditions passed; have the memory check move its baseline to the last save that finished cleanly. Replaces an inference with a committed fact, no weaker for a first save.

> 7 of 14 preventable by Option 3, 7 not: 0.500000 each, Wilson [0.267992, 0.732008]. Redundancy needs 0 in the not-prevented column; its lower bound is 0.2680. Producer: `scripts/do_options_three_and_one_compose_2026-10-29.py`

### 5. B49 — the ceiling on tickets carrying no identity

`bench/tests/test_an_identity_is_derived_not_remembered_2026-10-28.py` ratchets at **317**; it stands at **320**, from 3 tickets raised via `propose` rather than `propose_from_chat`, which derives an anchor. The guard is correct and the 3 are the assistant's.

**The count cannot be reduced, measured against a scratch copy:** 320 → 321 on raising 1, → **322** on `migrate_identity` (history is preserved by a tombstone that is itself identityless), and still 322 after a correct re-raise. **287 of 320 are such tombstones**, 0.896875, Wilson [0.858711, 0.925623].

**Refuted, so not offered:** enforcing identity at creation breaks **60 call sites across 11 test files** whose purpose is the fallback tiers; narrowing to ignore tombstones fails because tombstone statuses are in `TERMINAL` and `settled_on_subject` treats a terminal ticket sharing a subject as grounds not to raise.

**Recommendation: re-baseline to 320** with B49 as the record, plus an `fr` for a method that sets a missing identity so the next breach is reversible. **Fourth option, found by accident while repairing the entry:** let `tid_of` admit more than 1 ticket per `(kind, task_ref)`. 2 distinct defects sharing a `task_ref` currently collapse and the second silently overwrites the first — the defect `tid_of`'s own docstring says the reference was added to fix, recurring at the level above.

> 320 of 2,892: 0.110650, Wilson [0.099729, 0.122604], exact [0.099442, 0.122652]. Producer: `scripts/the_identity_ratchet_cannot_be_walked_back_2026-10-29.py`

### 6. B50 — what 4 immune-memory assertions should do after the reset he ordered

6 assertions in `bench/tests/test_immune_memory_evaluation.py` fail every run; the live memory holds 1 experiment where they describe 3 to 5.

**The product is right.** `bench/state/immune_memory_archive/immune_memory_20261017T095236Z.why.json` records the reason verbatim: *"his ruling of 2026-10-16: reset immune memory for the upcoming live experiments, since simulation can only tell us so much about how this facility will function in real live/paid experiments"*, with `experiment_count: 6`, the prior ids, and a `restore_with` command. `reference_runner_v3.py:21602` loads before `record_experiment` at `:21612`, so a count of 1 is correct accumulation onto a deliberately emptied store.

**Why now and not then.** `reset_record()`'s condition is *"0 records on disk AND an archive exists"*, with the stated intent that it re-arms as soon as a run writes. `free_run3_no_spec_20261028T235529Z` wrote the first post-reset records at 00:57 on 2026-10-29, so the skip correctly lapsed against a population that can never return. The design is sound; its content is stale.

**2 of the 6 are a stale constant** — `_RECORDING_RUNS` names exp47/48/49, dated 2026-07-28/29, about 3 months before the reset; filtering repairs both. **The other 4 assert facts measured on destroyed data** and no filter repairs them.

**Recommendation: widen the skip** from "0 records plus an archive" to "the live memory no longer contains the runs this claim was measured on" — keeps the anti-exemption intent because it re-arms once comparable runs exist. Alternatives: re-measure all 4 as the memory refills, or restore the archived priors, which would pass at once and undo his reset (listed for completeness, not recommended).

> 2 of 6 mechanically fixable: 0.333333, Wilson [0.096771, 0.700007], exact [0.043272, 0.777222] — wide because n = 6, quoted rather than hidden. Producer: `scripts/the_reset_rearmed_six_stale_pins_2026-10-29.py`

### 7. B48 — how the Feedback section of the memory index should be relieved

The loader truncates on **either** 25,000 characters (`PRe`) **or** 200 lines (`fie`), both read from the installed binary. `entries_left` reported the character answer alone: **34 entries of runway where the binding line budget allowed 11**, and **1** before `_check_memory_index_size` refuses. Fixed — the figure now takes whichever binds, and same-date `Project State` entries merge onto one line: **189 → 174 lines**, refuse headroom **1 → 16**, all **187** pointers intact.

**116 of 149 entry-lines, 77.8523%, are permanently beyond the trim**, the largest block being `Feedback` at **78** lines, which ages by design never. Growth is ~1 line per lesson. Unlike `Project State` it carries no date to group on, so automatic compaction would merge by position — the mechanical-transformation failure the record names.

**Recommendation: group Feedback under the bold sub-headings the index already carries**, joined by the ` · ` separator it already applies elsewhere. Lossless and immediate. Alternatives: raise the loader's limits if reachable (uncertain — both numbers come from the binary), or accept a periodic curation pass now the reported figure is honest.

> Producer: `scripts/the_line_budget_is_the_binding_one_2026-10-29.py`. Guard: `bench/tests/test_the_reported_runway_respects_both_budgets_2026-10-29.py`, 21 tests, 6 of 7 mutations red.

## C. Questions needing his judgement

Recorded as `qs` because each resolves to an answer, not a build.

| | ticket | question | recommendation |
|---|---|---|---|
| 1 | `qs:cea0bd553f52` (C1) | Into which appendix term — σ, S_k or R_k — should an informative-only channel's verdict enter, and as a multiplier? | **As a multiplier on R_k**, by analogy with his §7.7 verification-fact ruling, keeping 1 rule rather than 2 to tell apart. Held loosely: it is his model. |
| 2 | `qs:fd5e6e379930` (B39) | Is severity inherently a confidence within a range? | **None offered, deliberately.** He has said no archive can settle it: the question is what severity *means*. The measurement follows once the meaning is fixed. |
| 3 | `qs:3684bacc44bd` (B46) | The residual of the duplicate taxonomy. | **Apply his 2026-10-16 definition from here and leave existing pairs as history.** Both halves are now enforced with a `DUPLICATE_REPAIR_FLOOR` of 0.95; re-adjudicating would rewrite settled records. |
| 4 | `qs:9bc696a93ed1` | The task list's `state: DEFERRED` marker and the register's `deferred` field are independent and today disagree in **both** directions. | **Make the register authoritative and derive the marker from it.** The register already refuses a terminal status without a verification, so it is the stricter of the two. A build once he rules, because it changes which artefact is authoritative. |

## D. Labour only he can supply

### 8. The 63 full-range adjudications

The severity proxy was measured over severities spanning a window only 0.09 wide, so the pair (κ = −0.022688, Fisher p = 0.778818) is **uninformative about the proxy, not negative about it**. Settling it needs 63 adjudications drawn from the full range against the 5 clauses of `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`.

No model can supply those labels: peer-model CONFIRM votes are forbidden as evidence here and no other ground truth exists.

**Recommendation: batch them.** Simulated power is 0.916500 at 63 and ~0.80 at 48, so a first batch of 48 settles it at the conventional threshold with 15 as margin. **The closed form's 35 must not be quoted** — simulating it gives 0.6472, so it is optimistic.

> Producer: `scripts/the_severity_proxy_was_never_tested_2026-10-28.py`; guard `bench/tests/test_the_severity_proxy_was_never_tested_2026-10-28.py`, 31 assertions, 4 reversions red across 10.

## Closing — owed by the assistant, needing no decision

- **9 explanations** he asked for before ruling, oldest 2026-08-30, newest 2026-09-28. Answers owed, not work owed. Listed in §4 of `Morning_Report_2026-10-29_GENERATED`.
- **`fr:27ed80d7028e`** — his own proposal that CLI and model logins be checked before any substantial work, with a loud alert otherwise. Already his instruction, so a build owed; the expired login of the 28th is the case that proves it.
- **B20's bounded orchestrator** (`fr:1124302cec27`) — his design specified, nothing built.
- **The free panel on B21 and B22** — possible again now the login is restored, to run alongside whatever he decides rather than ahead of it.

---

Written under CDSFL note standard v1.8.
