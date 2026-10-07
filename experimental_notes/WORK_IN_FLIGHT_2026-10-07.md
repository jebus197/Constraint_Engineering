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
| 12 | Panel lessons applicable to the runners | Decide them, put in the morning report | OPEN |

## Questions he asked that the morning report must answer

1. Why would gamma become a recorded statistic, when it is foundational? Is the ladder order inverted, and is that the real fault?
2. What is the outstanding question, in plain English, and has he already answered it?
3. Are the joint-round seat verdicts in, and was it Fable that was outstanding? **Answer: yes, both are in. Fable returned 2220 words on its second dispatch.**

## Outstanding measurement, carried forward

**`hil_review` is the one switch whose ON path has never executed.** It is live in the ACTIVE runner — a configuration field, a command-line flag that sets it, and 2 branches that pause a run for human review — and no test turns it on. The CLI wiring is now executed by a guard; the gate itself needs a real round, because a structural claim about a branch is not evidence that the branch runs. Everything else among the 6 is read by live code, gates a real branch, and has a test that enables it: dormant by choice rather than by neglect.

## Recovery

Everything committed and pushed per item. `git log --oneline` on the branch is the record of what landed. This table is updated in the same commit as the work it describes.
