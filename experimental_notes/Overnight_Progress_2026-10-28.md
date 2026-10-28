# Overnight progress, 2026-10-28

**Branch `sim/shakedown-2026-09-29`, commit `a6c50b9e`, pushed.** Written at 22:53 GMT, covering the work since the founder's instruction to stop narrating and work unsupervised.

## The suite

| | baseline, same day | after the fixes |
|---|---|---|
| failed | 36 | **4** |
| passed | 12,954 | **13,001** |
| skipped | 24 | 25 |
| seconds | 5123.39 (1:25:23) | **5319.78 (1:28:39)** |

Recorded from the log by `scripts/suite_record.py`, not typed. `bench/logs/**` is gitignored, so both logs are mirrored at `experimental_notes/evidence/suite_logs_2026-10-28/` with a README naming each.

## B37, answered by measurement

Resident memory sampled every 15 s across the whole Python process tree:

| quantity | value |
|---|---|
| peak total | **1082.5 MB** |
| share of the 8.00 GiB machine | **0.132141** |
| headroom at the peak | 7109.5 MB |
| median total | 153.1 MB |
| largest single process | 747.3 MB |
| peak concurrent processes | 9 (median 5) |

z3 returns `unsat` for "2 concurrent trees at this peak exceed 8 GiB" and `sat` for "they fit"; NumPy and mpmath agree on the share to 6 decimal places. **No deadlock.** Boundary stated: 247 samples cover 61.8 of the 88.7 minutes, because the sampler started after launch; spot readings over the first 27 minutes were 88–243 MB, below the sampled peak. Samples: `experimental_notes/evidence/suite_logs_2026-10-28/rss_during_suite_2026-10-28.csv`.

## The 4 remaining failures

1. **`test_python_floor`** — an f-string nesting the same quote character. Legal from 3.12 (PEP 701), a `SyntaxError` on the 3.11 floor, and a module that cannot *parse* stops the suite *collecting* there. **Mine**, from my own capped-listing fix hours earlier. Fixed and verified on both interpreters.
2. **`test_cited_evidence_is_recoverable`** — refused a citation no reader could reach. Fixing it exposed a resolver blind spot: the mirror search is `evidence/*/<parts[2]>/<name>`, which needs `parts[2]` to be a round *directory*, so a file directly in `bench/logs/` can never resolve. **Measured: 0 of 45 cited 3-part paths resolved against 74 of 335 deeper ones**, and **5 of the 21** paths in the test's own pin are 3-part (0.238095, Wilson [0.106280, 0.450912]) — pinned because the instrument could not see them. The fix is strictly additive and the deeper-path count is unchanged at 74 of 335.
3. **`test_task_list_burndown`** — a **measurement**, not a code defect: R = **0.835714**, 95% CI [0.6542, 1.0676], upper bound still touching 1. Tonight's 4 new entries move it the wrong way until they close.

## The 0.7 severity cut has never been tested where severity varies

`kappa = -0.022688`, Fisher `p = 0.778818` **reproduce exactly** — and cannot carry the sentence they were put under. The audited corpus holds severities in **[0.65, 0.74]** only, SD 0.026915 against the archive's 0.224319 over 3,237 entries spanning [0.0, 1.0].

- power against a strong full-range effect: **0.144250**
- that hypothesis predicts an exact in-band odds ratio of **1.256464**; the measured interval **[0.516836, 1.569980]** contains it, alongside 1.0
- **0.792050** of 20,000 draws under it land inside the same interval

**"Only the band matters" is false.** 2,807 of 3,237 entries (**0.867161**, Clopper-Pearson [0.854982, 0.878672]) were classified at a severity the audit never examined, and **1,119 of the 1,408 critical calls** the gate has ever made — **0.794744** — sit *above* the band, where a disagreement is more consequential, not less.

Both copies of `additive-standard` now carry the band qualifier. His catch of the rubric-replacement proposal is unaffected: a replacement acts at the cut, and at the cut the band did measure chance. **Owed to him: 63 full-range adjudications** (simulated power 0.916500). No model can supply the labels — peer-model CONFIRM votes are forbidden as evidence here. Producer: `scripts/the_severity_proxy_was_never_tested_2026-10-28.py`.

## The completion barrier, built and already measured

`dispatch` stamps `t_start_epoch` and `t_end_epoch` on **both** the success and the failure record — a seat that times out is precisely the one that sets the barrier. `completion_barrier` in `bench/star_topology_2026-10-06.py` derives the figures.

Answered retrospectively from 88 archived rounds, reconstructing completions from reply-file mtimes: a round wastes a median **0.144892** of its available seat-time, bootstrap 95% CI **[0.105753, 0.181047]**; the median round loses 255.9 s; the archive loses 14.11 hours; 13 of 88 wasted over 0.30. The 20-second stagger cannot touch it — a stagger governs *starts*, this is wholly *finishes*.

Seat-count worsening is **suggestive, not established**: 0.384744 at 4+ seats (n = 6) against 0.131478 at 2 seats (n = 74); intervals disjoint; Mann-Whitney `p = 0.005483` and permutation `p = 0.000100`, but Brunner-Munzel — which does not assume equal spread — `p = 0.104133`.

Two corrections against this instrument's own first reading are in the producer: a loose seat detector counted experiment finding files as seats, credited one round with **144 seats** and reported the effect *backwards*; and an unbounded mtime reconstruction gave an impossible mean idle of **80,028.9 s**.

## Why I kept stopping

`hooks/work_not_narrate.py` **decides correctly and fired on nothing.** Called on this session's own 488.4 MB transcript it refuses **8 of the newest 12** genuine founder turns (0.666667, Wilson [0.390622, 0.861880]); the 4 it allows are the 4 where he issued `d`; self-test 7 of 7.

Three independent disablements:

1. a 0-byte sentinel `~/.claude/hooks/.work_not_narrate_PARKED` dated 2026-09-11, on which `main()` returns 0 before reading the payload;
2. its `Stop` key renamed `_PARKED_Stop_2026-09-11` — and its own guard passes a parked entry **by design**, so nothing was red;
3. `hooks/ticket_queue_gate.py`, which *is* wired and no longer yields, standing down on a pause file carrying his 2026-10-24 *"do not resume the master task list until I tell you to do so"*.

All three cleared on his 2026-10-28 instruction; the pause **archived, not deleted**. **An earlier reading of mine is withdrawn**: it reconstructed the rule from `MIN_TOOL_CALLS` and `MIN_PROSE`, which `verdict` consults only to *word* its message — 0 of 12 against 8 when called, exact McNemar `p = 0.0078125`. Producer: `scripts/the_gate_was_disabled_three_ways_2026-10-28.py`.

## Where things stand

The master task list opens with T1–T4, so both Stop gates name T1 rather than an older entry.

- **T1 — land and commit the staged work.** Done, `b4e66b85`, closed with its verification. The pre-commit board refused 3 times across 6 classes and every refusal was a real defect of mine, including a truncation path that reserved a hardcoded 200 characters for a notice whose length grows with the item count.
- **T2 — free panel review, both halves.** Running. Both seats confirmed ALIVE, each confined to its own repository copy, stagger visible, joint debt 0.
- **T3 — simulated run** with `--severity-spec` and the barrier, under `cy`.
- **T4 — resume the list from R1** and retire the harvester's chat half on his ruling.

**Nothing currently requires his verdict.** The one item genuinely owed to him is the 63 severity adjudications, which only he can supply and which blocks nothing else.

Written under CDSFL note standard v1.8
