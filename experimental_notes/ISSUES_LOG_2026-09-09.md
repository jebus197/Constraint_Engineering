# Issues log, 2026-09-09 work session

**Running log. Founder instruction 2026-09-09, verbatim: *"All issues that emerge should be put in a closing tts report. Nothing (unless potentially catastrophic) should detract from the above instructions to complete the entire outstanding work list."*** Entries are appended as found and are NOT acted on unless they are catastrophic or are themselves on the task list. The closing TTS report is built from this file.

Severity vocabulary: CATASTROPHIC (stop everything) / HIGH (schedule on the task list) / MEDIUM (note and move on) / LOW (record only).

| # | Severity | Issue | Evidence | Status |
|---|---|---|---|---|
| I1 | HIGH | 177 of 3803 cited `bench/logs/` paths are untracked, so a body of cited evidence exists on 1 machine only. 4.65%, Wilson [4.03%, 5.37%]. | `git ls-files` against `git grep` over the repository, 2026-09-09 | Own instance fixed at `3c6f143`; the remaining 177 need a founder policy ruling |
| I2 | MEDIUM | The 2-consecutive-clean-passes stop rule is unsafe when every pass uses the same vantage point. Pass 4 returned 0; pass 5, which cloned the repository, returned the most serious defect of the day. | FFAFP passes 1-5 on item 1.1 | Recorded; argues for varying the ANGLE, not just repeating passes |
| I3 | LOW | `note_vagueness_lint.py` loses its quote exemption on any quotation spanning more than 1 sentence, because it strips balanced pairs but checks per sentence. 3 of 560 findings, 0.54%, Wilson [0.18%, 1.56%]. | `scripts/lint_quote_exemption_defect_2026-09-09.py` | On the task list as L2 |
| I4 | MEDIUM | 3 of the 4 live Claude Code hooks were unversioned, existing only under `~/.claude/hooks/`. | FFAFP pass 1 FOLLOW, 2026-09-09 | Fixed: versioned in `hooks/` with a per-hook drift test |
| I6 | HIGH | **The suite does not pass in a fresh clone: 11 failed, 5487 passed, exit 1, against 0 failures in the working tree.** For a project whose stated purpose is reproducibility this is central, not cosmetic. 10 of the 11 are pre-existing; 1 was mine and is fixed. | `git clone` + full suite, 2026-09-09, HEAD `3c6f143` | Added to the task list; NOT allowed to derail the list per founder instruction |
| I7 | MEDIUM | The Rule 20 vocabulary cannot express an item closed by a founder ruling with no work product. Entry 1.3 (QWERTY, closed by ruling) reads state=DONE status=PROPOSED, which the cross-check correctly flags as contradictory. | `scripts/task_list_markers.py --check`, first run | Fixed by adding a WITHDRAWN state |
| I5 | LOW | 1 `.py` file already sits under `experimental_notes/`, inside the source-scanner surface. | `rglob` count during the pass-5 fix | Recorded, not investigated |

Written under CDSFL note standard v1.7 (26 August 2026).
