# Parked for the founder — non-blocking items, newest last

**Opened 2026-09-10 on his instruction:** *"Why not just leave them all to discuss with me at the end of the completed task list, unless there is something that clearly warrants my immediate attention?"*

Every item here was classified by `scripts/blocker_triage.py` as NOT blocking. Nothing here is dropped; it is queued. Items that DO block are raised at once and never appear in this file.

---

## A17: the verdict-tuple guard matches function names across the repository

*Parked 2026-09-10T17:15:14+01:00.*

A new script defining scan() returning a tuple caused supersession_check.py:149 to be flagged for a truth test that is correct on a list. The guard matches tuple-returning function NAMES without resolving the call. Worked around by renaming; the cause stands. Fix is to resolve the call, which is execute-do-not-grep applied to an AST scan.

## A18: nine off-switches in the exp56 configs that no runner module reads

*Parked 2026-09-10T17:15:14+01:00.*

merge_arbitration_enabled, immune_memory_enabled and _ouroboros.max_papers_per_round, each off in all 3 arms, read by none of 210 runner modules. The additive standard's unwired half, in data rather than code. Not urgent: 0 of the 3 affects a live run, precisely because nothing reads them.

## A13/A14: the panel sandbox lost most of its bench tree mid-review and no seat could account for it

*Parked 2026-09-10T17:15:14+01:00.*

8 files against the canonical 167, reported by cc2 in round 4. Both seats share one sandbox, so a destructive action by the seat that finishes first lands under the seat still working. The falsifier is cheap: build a sandbox, count, run the suite inside it, count again.
