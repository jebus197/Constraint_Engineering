# Resources — Project Onboarding and Recovery

Everything needed to pick up this project from scratch — whether you are
a new AI model instance, a human developer, or a reviewer attempting to
reproduce or refute the results.

## Contents

- **[ONBOARDING.md](ONBOARDING.md)** — Start here. Full project context,
  current state, architecture overview, and how to get productive immediately.
- **[RECOVERY.md](RECOVERY.md)** — How to rebuild full working context from
  the repository alone after a session loss, compaction event, or fresh start.

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

## For the Founder

After compaction or fresh session: point your new model instance at
ONBOARDING.md. It contains everything needed to resume work without
the 30-minute recovery dance.
