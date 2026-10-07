# Work in flight — founder's TTS responses of 2026-10-06

Opened 2026-10-07T11:51:36+01:00. **This file is the resume pointer for the current work order.** It is updated as each item closes, so an interrupted session can restart from it without re-reading the conversation. Branch `sim/shakedown-2026-09-29`; `main` untouched.

## The work order, verbatim in substance

His instruction: run `sv`, then work his `#` responses, then everything else still outstanding, then a morning report in the usual Desktop location carrying any decisions still needed. Do not stop while work remains that does not need his attention. Internet is unstable until about 10 October, so every step is committed as it lands rather than batched.

## His standing position, which governs several items at once

**Capability is MEASURED capability. A model's name records who did what and decides nothing else.** Stated twice in the responses and again afterwards. Several items below are the same ruling applied in different places.

## Items

| # | Item | His verdict | State |
|---|---|---|---|
| 1 | Gamma coupling / "recording only" | Challenged as gamma demotion | **ANALYSED** — nothing demoted; the evidence does not support a change either way |
| 2 | `--seat-models` default uniform | Turn it on. Simulated runs can carry real distinct Anthropic models | **DONE** — default is `ladder`; 4 probed models |
| 3 | Ladder must route back to the source model when no better rung exists | Turn it on and leave it on | **DONE** — self-rung, on by default, carries the prior verdict |
| 4 | Boot check outstanding repairs | Fix if not already done | **DONE** — POST green, 5 of 5 |
| 5 | Network-degradation lessons into the runners | Incorporate | **PARTLY DONE** — probe + serialisation in; mid-run degraded-route detection is a proposal for him |
| 6 | Free-seat contention | Fix if it can be fixed | **DONE** — runner serialises shared-credential routes |
| 7 | Remaining suite failures | Do the work | **DONE** — all 4 fixed at root cause |
| 8 | 6 switches enabled nowhere | Investigate and do the work | **DONE** — 0 retire, 5 retain, 1 scheduled (`hil_review`) |
| 9 | Provenance denominator | Fix it | **DONE** — filer's failure counted; 2 of 11 ranks move |
| 10 | ITC left unswitchable, reported when it fires | Agreed | ACCEPTED, no code owed |
| 11 | Minimum sample | "No work to do here? Fine if so" | CLOSED, no code owed |
| 12 | Panel lessons applicable to the runners | Decide them, put in the morning report | **DONE** — 2 applied, 4 offered for decision |

## ALL 12 ITEMS ARE CLOSED. The morning report is at `~/Desktop/CDSFL_tts/Morning_Report_2026-10-07.txt`.

## Questions he asked that the morning report must answer

1. Why would gamma become a recorded statistic, when it is foundational? Is the ladder order inverted, and is that the real fault?
2. What is the outstanding question, in plain English, and has he already answered it?
3. Are the joint-round seat verdicts in, and was it Fable that was outstanding? **Answer: yes, both are in. Fable returned 2220 words on its second dispatch.**

## Outstanding measurement, carried forward

**`hil_review` is the one switch whose ON path has never executed.** It is live in the ACTIVE runner — a configuration field, a command-line flag that sets it, and 2 branches that pause a run for human review — and no test turns it on. The CLI wiring is now executed by a guard; the gate itself needs a real round, because a structural claim about a branch is not evidence that the branch runs. Everything else among the 6 is read by live code, gates a real branch, and has a test that enables it: dormant by choice rather than by neglect.

## Afternoon of 2026-10-07, after the 12-item work order closed

| # | What he asked | State |
|---|---|---|
| 13 | Free panel review on resolving the ladder/allocation tension, pointing at Astra's spec | **DONE** — both seats landed first attempt, 0 paid; cc2 4857 words / 43 tool calls / 1007.2 s, fable 3066 words / 31 tool calls / 949.7 s. Commit `1a4b0c07`. |
| 14 | "Report back when both seats land" | **DONE** — reported, including that the panel overturned the brief's own evidence: `falsifier_style` misclassifies 740 of 1078 archived falsifiers, 68.6456%, Wilson [65.8141%, 71.3448%]. |
| 15 | "This leaves the tension in place?" | **DONE** — he was right. The ladder carries 2 objectives on 2 decisions; coverage is order-invariant, spend is order-only. Commit `20ec400a`, notes `f430f691`. |
| 16 | `sv` | **DONE** — green at `c264435e`, all 6 postconditions pass. Refused twice first: a memory index line over 150 characters, then a suite figure with no named producer. Both were real. |
| 17 | P-pass on the decomposition | **DONE** — it survives, and his own ruling of 2026-10-06 dissolves the half it names. Commit `8b3b31a8`. |
| 18 | "If I run `rs` now does this change anything?" | **DONE** — restore run, exit code 0; the owed OpenBrain session-context check also run, exit 0. |
| 19 | Notes to account for network instability, as a standing resource | **DONE** — `experimental_notes/OFFLINE_RECOVERY.md`, undated and revised in place. |

## Carried forward for his ruling

1. **`git_state()` crashes `rs`, `sv` and `qc` on an unreachable network.** `scripts/cdsfl_utils.py:80` fetches unconditionally; a non-zero return code is tolerated but `TimeoutExpired` and `OSError` are not caught. 11 of the 25 failures on the 2026-10-07 board are this single cause. Repair is PROPOSED, 1 point in 1 function, and not built.
2. **`routing_max_rungs` still defaults to 2 and 0 of 47 configs set it to 0**, so his 2026-10-06 ruling that there should be no cap is in force nowhere. Under exhaustion the selection question disappears and the ordering question is already solved, so this is a wiring gap rather than a design question. Changing it raises dispatch across 23 routed configs, which is spend he has not authorised.
3. **`fable` is free and is not on the falsifier ladder at all.** Exactly 1 of the 5 rungs is free.
4. The paired exhaustion-versus-cap run; `hil_review`'s unexecuted ON path; the 4 panel lessons for the runners; the `falsifier_style` repair conditioned on target type.

## Recovery

Everything committed and pushed per item. `git log --oneline` on the branch is the record of what landed. This table is updated in the same commit as the work it describes.
