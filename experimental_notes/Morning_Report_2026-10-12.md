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

*Written under CDSFL note standard v1.7.*
