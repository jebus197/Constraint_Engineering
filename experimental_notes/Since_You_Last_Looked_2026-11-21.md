# Since you last looked

*21 November 2026, 20:16 GMT*

> **Addressed to the founder in the second person**, which this project's note standard normally reserves for the decisions file. Written that way deliberately: he asked for a briefing, not a record. A third-party reader should treat it as correspondence rather than as a finding. Its spoken companion is `Since_You_Last_Looked_2026-11-21.txt`, re-rendered rather than copied.

## The short answer

**The number in front of you is 11, not 29.** Of the 21 decisions currently waiting, **10** ask you to ratify or close work the record already says is built, and **11** are live questions.

The split is not my judgement. It is `status_flag` in `scripts/build_decisions_file_2026-11-07.py`, reading each entry's own marker through `scripts/task_list_markers.py`. An entry whose prose claims completion but whose marker says `PROPOSED` is counted **live**.

| of the 21 waiting on you | n | share | Wilson 95% |
|---|---|---|---|
| ratify or close | 10 | 0.476190 | [0.283440, 0.676305] |
| genuinely live | 11 | 0.523810 | [0.323695, 0.716560] |

## What you actually did since the 29

Of the 29 put to you on 2026-11-08, accounted for exactly, 29 of 29:

| | n | share | Wilson 95% |
|---|---|---|---|
| closed on **your** dated ruling | **23** | 0.793103 | [0.616099, 0.901539] |
| closed with no ruling on record | 1 | 0.034483 | [0.006113, 0.171755] |
| still open | 5 | 0.172414 | [0.075979, 0.345484] |

**20 of those 23 rulings are dated 2026-11-08 itself.** The implementation was mine; the decisions were not.

Your own queue, from the files delivered to `~/Desktop/CDSFL_tts/` rather than from the task list (which has been edited since, and so cannot say what you saw then):

| date | decisions |
|---|---|
| 2026-11-07 | 29 |
| 2026-11-08 | 29 |
| 2026-11-09 | 10 |
| 2026-11-10 | 10 |
| **2026-11-11** | **7** |
| 2026-11-12 | 11 |
| 2026-11-13 | 16 |
| 2026-11-14 | 19 |
| 2026-11-17 | 21 |
| 2026-11-21 | 21 |

**You cleared it to 7.** The low point you described sat immediately before the steepest fall in the record, not during a plateau.

## Why it refilled, and whose doing that is

From the trough of 7 on 2026-11-11 the queue climbs at **+1.264423 decisions/day** — p = 0.045659, r² = 0.672484, 95% CI [+0.399666, +2.129180], with SciPy `linregress` and NumPy `polyfit` agreeing to 4.44e-16. Over the whole window the slope is −0.027778/day at p = 0.966908, which is indistinguishable from flat.

Over the same 13 days: **75 entries raised, 57 closed.** As daily rates, **5.769231 arriving** against **4.384615 closing**, exact Poisson intervals [4.537866, 7.231781] and [3.320865, 5.680778], each on 2 routes (SciPy `chi2.ppf` against mpmath `gammainc` inversion) agreeing to 0.00e+00.

**Those 2 intervals overlap**, so the gap is not established at 95%. The point estimate says arrivals outrun closures; the interval says do not call it proven. Both are stated rather than the flattering one alone.

Net change since the 29: **−8**. You are still ahead of where you started.

## When does this end

**On the whole backlog, over the last 13 days, it does not converge.** More arrives than closes. No end point may be quoted from this window, and I am not going to manufacture an end point the data does not support.

**On your own queue it is different**, and that is the one you experience. You took it 29 → 7 in 4 days. What happened since is that I raised decisions faster than you were asked to absorb them.

So the lever is mine: raise fewer items to you, route more as my own work, and mark the ratifications so they stop reading as questions. The third was built today and is why the figure is 11 rather than 21.

Producer for every figure in this section: `scripts/since_you_last_looked_2026-11-21.py`, which reads the task list's own markers and the delivered files. It is guarded by `bench/tests/test_todays_producers_run_2026-11-21.py`, which pins that it **reaches** a convergence verdict and never which verdict — a view that can only reassure is not a measurement.

## The 11 that need your ruling

Rule by naming the entry and the option number. Full arguments in `~/Desktop/CDSFL_tts/Decisions_Awaiting_You_2026-11-21_GENERATED.txt`.

1. **B94**, the 2 decisions left over from the verified-flag repair — whether `v_bar` counts a model's own claim, and what the 4 sibling runners do. *Recommended: keep both; you choose which the fingerprint reads.*
2. **B143**, the appendix severity formula that cannot be computed — repoint the proof, and add a third consequence weight? *Recommended: both, in that order.*
3. **B154**, the 2 decisions owed from the night's encoding work — engineering critical level 7 → 9, and when the 22 draft encodings go to the panel. *Recommended: leave at 7; send the 22 at your convenience.*
4. **B160**, the figure the turn hook prints to you — which test replaces the proxy, given 3 candidates disagree on every entry they touch. *Recommended: keep the test, report the disagreement beside the figure.*
5. **B170**, every commit for 43 days on a non-default branch — merge the 620+ commits to `main`, or make the shakedown branch the default? *Recommended: merge to `main`.*
6. **B180**, the gate enforcing your 60-second monitoring directive — widen it to see a full-suite run? It was silent through both of today's 3-hour measurements. *Recommended: widen it.*
7. **B182**, `local_resource_budget.py` stopping delegated work launching heavy verification — widen the hook now letting 126 of 150 real instructions through? Editing it needs your permission by design. *Recommended: widen the noun-phrase side.*
8. **B186**, your proposed 4th formal standard, real-world applicability — adopt it, and in what words? *Recommended: adopt it scoped exactly as you worded it.*
9. **B190**, a panel answering a question you had asked — is the disjunction the right aggregator, and authorise severity-record stamping? *Recommended: authorise stamping; treat the disjunction as provisional.*
10. **B197**, the task list's branching point estimate crossing 1 — does a point estimate crossing, rather than an interval crossing, change your 2026-11-08 ruling? *Recommended: direct a verified closing pass.*
11. **B204**, the census of guards missing from the commit gate that nothing enforces — may that gap be gated at all, when gating it decides every future board's length? *Recommended: report it in the pre-flight and refuse nothing.*

## The 10 that need ratifying or closing

**B77, B84, B125, B141, B142, B159, B171, B175, B185, B194.** Each was raised as a question; the record now says the work is built, tested or committed, or that the premise has been falsified. A single instruction covering all 10 is enough.

## The 1 that closed without you

**B103, the 54 guard files sitting outside the commit gate** against the gate's own written scope rule. It was 1 of your 29, is marked `DONE | COMMITTED`, and carries no `ruled` field — the only 1 of the 29 in that position.

The work is not in doubt: the scope rule predates the entry, so the repair closed a violation rather than making a choice, which is the likely reason no ruling was sought. **Whether it was yours to decide is in doubt, and only you can settle it.** Offered for ratification and deliberately *not* reopened — reopening an entry to collect a ruling it never needed would put work back in your queue to satisfy bookkeeping. Recorded as an amendment on the entry itself.

## What happened today

3 repairs, 1 batch, on your instruction to *"do both, and stream the test phase"*.

**B159, the memory index with no headroom.** Your account of the design was right and mine was wrong. The trim has been automatic since 2026-10-03; its **scope** was the defect — it reached 0.063955 of the index while `Feedback`, at 0.810667, is excluded by design. A standing ceiling now runs in the pre-flight: 24,486 → 22,938 characters, headroom 14 → 1,563.

**B202, the board's silent test phase.** A command substitution captured ~2,556 s of output. It now streams, about 1 line per 35.75 s. The obvious `tee` repair would have made the gate a rubber stamp: **0 of 3 exit codes kept**, including 0 on a tree rigged to exit 1.

**Your decision list** now carries each entry's own status. That is what turned 21 into 11.

**The first board refused all 3 and was right to** — 18 failed, 5,131 passed, 2663.27 s. **10 of the 18** were broken by my own hook change, because 5 instruments pinned the line I replaced and I had not traced them. A **19th** was invisible to the board, its file not being on the `GUARDS` list. All 19 repaired: **1,309 passed, 0 failed**.

**The board had run 0 of this batch's own 70 tests** — all 4 new guard files were off `GUARDS`. `scripts/b103s_rule_is_not_being_followed_2026-11-13.py` priced it at 4 of 245, Wilson [0.006367, 0.041219], all 4 dated today. Now added; cost measured first at 70 tests in 64.88 s, +2.44% of a board.

**2 raised, not fixed.** B204 is in your list. **B205** is mine: the Stop gate told me 6 times I had committed when HEAD never moved, because it matches the literal `git commit` anywhere in the turn and `hooks/pre-commit` contains that string as advice; it also called a `BUILT` entry unstarted. Neither false sentence reaches its decision, so it is a false self-report and not a defeatable gate. Both fixes specified, neither applied, on the B203 precedent.

## What I recommend next

Rule the 11, or as many as you will in one sitting. Give 1 instruction for the 10 ratifications. Say whether B103 is ratified.

**And 1 thing not on the list.** The measurement says the backlog does not converge because I raise faster than anything closes. If you want that ended rather than managed, the instruction that would do it is a **cap on how many decisions may be open to you at once**, with everything above the cap held as my work until the queue drops. Your call; I have not built it.

## What is still owed to you

The 11 rulings. The 10 ratifications. A decision on B103. An answer on whether you want a cap on your open queue.

---

Proportions carry 95% Wilson intervals on 2 independent routes agreeing to better than 1e-12 (statsmodels against a hand-rolled mpmath computation); daily rates carry exact Poisson intervals on 2 routes agreeing to 0.00e+00. 3 interval figures were additionally cross-checked in **Wolfram Language** and agreed on every bound. Board-cost figures come from `.cdsfl_tmp/precommit_durations.jsonl`, which is unversioned and gains a row per board, so they go stale immediately — re-run `scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py` rather than quoting them from here.

Written under CDSFL note standard v1.9 (1 November 2026).
