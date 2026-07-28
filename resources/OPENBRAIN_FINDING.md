# resources/OPENBRAIN_FINDING.md — Why OpenBrain Records Are Not Mirrored

Companion document to [MEMORY.md](MEMORY.md) and
[MEMORY_EXCLUSIONS.md](MEMORY_EXCLUSIONS.md). Explains why OpenBrain
records are deliberately not mirrored into this repository, and what
is available in their place.

## What OpenBrain Is

OpenBrain is a separate project at
`/Users/georgejackson/Developer_Projects/OpenBrain/` that provides a
cross-agent, cross-project persistent memory store. The founder
operates it as shared infrastructure across multiple research efforts,
not as a CDSFL-specific store.

CC1 (this repo's assisting agent) uses OpenBrain to:

- persist session summaries and decisions that should survive context
  compaction;
- exchange messages and status notes with other agents (referred to
  internally as CW, CX, CGPT, DS, etc., corresponding to different
  model routes or agent roles);
- surface pending and blocked tasks across sessions.

OpenBrain is queried at session start via
`python3 -m open_brain.cli session-context --agent cc` and at key
milestones via other CLI subcommands. Its record schema is internal to
the OpenBrain project.

## Why Records Are Not Mirrored Here

Inspection of a representative `session-context` output shows that the
store contains:

1. **Cross-project material.** Entries from other projects the
   founder is working on (e.g. Project Genesis, Genesis Story, CW's
   UX work) appear alongside CDSFL entries in the same query result.
   These are not CDSFL material and cannot be cleanly separated
   without a per-project filter that does not currently exist on the
   public side.
2. **Agent-to-agent messages.** Pending-task, blocked-task, and
   decision entries from other agents (CW, CX) are directed at their
   respective workflows. They are working notes between tools, not
   records of CDSFL experimental method.
3. **Live working state.** Session summaries describe the founder's
   current working focus, which by design is mutable day to day. A
   snapshot frozen into this repo would be stale within hours.
4. **Privacy boundary.** OpenBrain holds free-form prose that has not
   been through the same privacy review as committed documentation.
   Treating it as public-ready by default would violate the standing
   privacy rule.

Mirroring OpenBrain records into this repo would therefore (a) leak
other-project material, (b) stale quickly, and (c) sidestep the
privacy boundary that applies to committed docs.

## What Is Available Instead

The substantive CDSFL content that would otherwise be sought in
OpenBrain records is available — in curated and sanitised form — in
the following files within this repo:

- `resources/ONBOARDING.md` — full project history and context.
- `resources/RECOVERY.md` — pending work, recent decisions, recovery
  protocol.
- `resources/MEMORY.md` — this mirror's public index of project-
  scoped CC1 memory.
- `experimental_notes/*` — third-party-readable experimental records.
- `docs/CURRENT_STATE.md` — machine-generated state snapshot produced
  by `scripts/cdsfl_sv.py`.

These files are updated at each `sv` milestone and are the
project-scoped alternative to raw OpenBrain queries for anyone outside
the founder's direct working environment.

## If a Future Need Arises

If a specific OpenBrain entry needs to become public (for example,
a decision record worth citing), the path is:

1. Extract the entry.
2. Review for cross-project leakage and personal-context leakage.
3. Sanitise and place into `resources/RECOVERY.md` (if decision-like)
   or `experimental_notes/` (if results-like).
4. Link from `MEMORY.md` if it is something CC1 will continue to
   reference across sessions.

No mass export or automated mirror is planned. Mirroring is handled
by deliberate human review per entry, not by bulk sync, because the
store's cross-project scope precludes safe bulk sync.
