# Resources — Project Onboarding and Recovery

Everything needed to pick up this project from scratch — whether you are
a new AI model instance, a human developer, or a reviewer attempting to
reproduce or refute the results.

## Contents

- **[ONBOARDING.md](ONBOARDING.md)** — Start here. Full project context,
  current state, architecture overview, and how to get productive immediately.
- **[RECOVERY.md](RECOVERY.md)** — How to rebuild full working context from
  the repository alone after a session loss, compaction event, or fresh start.
- **[SHORTCUTS.md](SHORTCUTS.md)** — Metacognitive command and shorthand
  reference. Short tokens (e.g. `p`, `sv`, `qc`, `rg`, `sq`) that direct
  model behaviour; combinable.
- **[MEMORY.md](MEMORY.md)** — Public mirror of CC1's (Claude Code,
  instance 1) persistent auto-memory, filtered to project-scoped entries.
  Makes visible what context the assisting agent carries across sessions.
- **[MEMORY_EXCLUSIONS.md](MEMORY_EXCLUSIONS.md)** — Companion to
  MEMORY.md. Names the entries withheld and the criteria that withheld
  them, so the public record is honest about the shape of what is not
  mirrored.
- **[OPENBRAIN_FINDING.md](OPENBRAIN_FINDING.md)** — Explains why the
  OpenBrain cross-agent memory store is not mirrored here (cross-project
  scope, privacy boundary) and what is available in its place.
- **[configs/](configs/)** — Abstract domain-expert encoding templates
  (ANON variants). Pair with the populated examples under
  `bench/exp39_configs/` and the concrete template
  `examples/structural_building.txt.example`.

## For Reviewers

Everything needed to reproduce the bench test results is in this repository.
The methodology, the task corpus, the evaluation pipeline, the domain expert
configurations, and the Constraint Editor policy engine are all here. If you
get different results, that is data. If you get the same results, that is
replication. Either outcome advances the work.

## For Contributors

Read ONBOARDING.md first. Then read the [Founder's Notes](../docs/FOUNDERS_NOTES.md)
for design intent and open questions. The [PAPER.md](../PAPER.md) is the
canonical technical statement. The bench test code is in `bench/`.

