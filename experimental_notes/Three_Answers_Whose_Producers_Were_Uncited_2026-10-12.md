# Three answers whose producers nothing cited — 2026-10-12 15:00 BST

`scripts_are_reached_2026-09-11.py` reported 3 measurement scripts "reached by nothing":
no caller, no note citing them as a figure's producer, no document naming them as a
command. All 3 answer the founder's own direct questions, so the fix is to cite them
rather than to retire them. Each answer and its producer follows.

## How many attempts a ranking needs

His challenge, 2026-10-09: *"300 attempts for a single model to solve any given problem
is clearly vastly much too much!"* Producer:
`scripts/how_many_attempts_a_ranking_needs_2026-10-09.py`.

**A knockout bracket cannot support a ranking at all.** It yields n−1 matches and never a
cycle, so Ford's condition fails and the Bradley-Terry estimate is UNDEFINED: 4 players
give 3 matches, 8 give 7, 16 give 15, every one acyclic and none strongly connected. An
8-player round robin gives 28 matches and IS strongly connected. A knockout also removes
a participant on a single result, against the standing rule that no model is ever
permanently set aside.

## Can the registry be cleared or exported without destroying what was measured

His question, 2026-10-06, about what happens when a user clears or exports records once
the interface exists. Producer: `scripts/registry_is_the_evidence_base_2026-10-06.py`.

**An exported entry can be read back on its own.** Over 3,158 archived entries, each of
`canonical_id`, `status`, `severity`, `source_model`, `open_since_round` and
`description` is present in 3,158 of 3,158 — 100.0000%, Wilson [99.8785%, 100.0000%]. So
an export is self-describing and clearing the live registry does not destroy the
evidence, provided the export is kept.

## Which of the week's agreed changes are actually live

His challenge, 2026-10-11: *"in the past there have been periods where we have spent
significant effort discussing changes and improvements that were ultimately never
implemented."* Producer: `scripts/what_was_actually_implemented_2026-10-11.py`.

Over the 8 items it probes: **3 LAPSED (0.3750, Wilson [0.1368, 0.6943]), 2 LIVE
(0.2500), 2 MEASURED_NOT_ACTED (0.2500), 1 needing a CHECK (0.1250)**. The script states
its own boundary and it is repeated here: no fan-out rows were merged, so this covers
only those 8 and is **not** the project-wide rate.

---

*Written under CDSFL note standard v1.7.*
