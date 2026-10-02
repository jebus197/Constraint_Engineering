<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'green_board_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e8114459a6cd05e34c680bc2e554b0c90709e3cb62343814a7774e4b46469e60
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Figure drift — panel round 11, brief dated 2026-09-11

`BRIEF.md` IN THIS DIRECTORY IS UNEDITED AND MUST STAY THAT WAY. It is the record
of what 2 seats were actually given on 2026-09-11, and a figure inside it is
evidence about the dispatch, not a live readout.

One of its 2 declared figures no longer reproduces:

| | |
|---|---|
| declared in BRIEF.md, 2026-09-11 | `real-rejection rate : 2/640 = 0.3125%` |
| printed by the same script, 2026-09-29 | `real-rejection rate : 2/716 = 0.2793%` |

**THE NUMERATOR DID NOT MOVE.** Both figures count the same 2 real rejections —
`exp48_chemistry_exam_live_20260729T044134Z` findings `C0012` and `C0015`. What
moved is the denominator: the corpus of distinct archived falsifier sources grew
from 640 to 716 as runs landed. The brief was correct when it was sent, and the
rate it quoted is the rate as of its own date.

`scripts/panel_brief_validate.py` re-executes the record below and requires the
named script to print it TODAY, so this file cannot make a refusal go away by
assertion. See `FIGURE_SUPERSEDED` in that module for what the mechanism
deliberately cannot see.

<!-- figure-superseded: 2026-09-29 | archived falsifier rejections that are NOT location artefacts | scripts/archived_falsifier_rejections_2026-09-10.py | real-rejection rate : 2/716 = 0.2793% -->
