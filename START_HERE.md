# Start here

A map of this repository, for a reader arriving for the first time — human or machine.

`README.md` is the project's argument, and it is long. This file is the shortest path
into the work. Read whichever suits you; they are not substitutes for one another.

---

## What this project is, in three sentences

CDSFL is a research framework for making large language models more reliable on
scientific and technical work. Several models from different vendors review the same
document and accuse it of faults; an accusation only counts if the accusing model also
writes a small program that demonstrates the fault, and the framework re-executes that
program itself. What a model asserts in prose decides nothing — only what its program
does when it runs.

---

## Where to go, by what you want

| If you want | Read |
|---|---|
| The argument and the theory | [`README.md`](README.md), then [`PAPER.md`](PAPER.md) |
| What every term and symbol means | [`docs/GLOSSARY.md`](docs/GLOSSARY.md) |
| How the parts fit together | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| The mathematics | [`docs/MATHEMATICAL_APPENDIX.md`](docs/MATHEMATICAL_APPENDIX.md) |
| Results, per experiment | [`docs/EXPERIMENTAL_RESULTS.md`](docs/EXPERIMENTAL_RESULTS.md) |
| To reproduce a run | [`docs/REPRODUCING.md`](docs/REPRODUCING.md) |
| The full project history | [`resources/ONBOARDING.md`](resources/ONBOARDING.md) |
| What is currently outstanding | [`experimental_notes/OUTSTANDING_QUEUE_to_BR2.md`](experimental_notes/OUTSTANDING_QUEUE_to_BR2.md) |
| Narrative write-ups of individual findings | [`experimental_notes/`](experimental_notes/) |
| The code that runs experiments | [`bench/`](bench/) |

If you read one file, read `docs/GLOSSARY.md`. The project uses precise internal
vocabulary — falsifier, convergence gate, claim audit, zero-plant control — and the
glossary is what makes the rest legible.

---

## What to skip, and why

**`bench/logs/` is machine output, not reading material.** It holds the raw record of
every experimental run. As of August 2026 it was 353 MB across 5,840 files: 96.8% of the
repository by size and 86% of its files, against roughly 11 MB of actual project in
about 900 files.

That imbalance is worth stating plainly because it misleads. A reader glancing at the
file count reasonably concludes the project is vast and impenetrable. It is not — the
instrument simply writes a great deal down.

Two things follow. If you are browsing, ignore `bench/logs/` entirely; nothing there is
written for a human. If you are a program with a request budget — an automated reader,
a crawler, a model with browsing — do not walk the tree. GitHub allows 60 unauthenticated
API requests per hour and this directory will consume all of them before you reach
anything meaningful. Fetch the specific documents listed above by their raw URL instead.

---

## The experimental record

Two distinct things, kept in different places on purpose.

**The record**, in this repository: the final report and runner state for each run,
carrying the finding registries, the falsifiers and the verdicts. This is what you need
to check any claim the project makes. It is small and it is meant to be read.

**The raw material**, archived separately: the complete unedited output of every model
in every round. This is primary source rather than analysis, it is the bulk of the
volume, and it is preserved rather than discarded. See `ARCHIVE.md` for where it lives
and how to cite it.

Note one honest limitation of the raw material. Each record stores what a model
returned and the *length* of the prompt it was given, but not the prompt itself. Prompts
are reconstructible from the directives and targets held here, but they were not
recorded at the time.

---

## Branches

`main` is current and is what you should read. `exp39-experimental` retains the
fine-grained commit history behind the August 2026 milestone merge.
`exp38-experimental` is a historical marker for an early result and is fully contained
in `main`.

---

## Status

This is active research, not a released product. Findings are provisional, the
experimental arc is unfinished, and several components are built and deliberately
switched off pending evidence. Where that is true, the project's notes say so
explicitly rather than implying completeness.

## Reproduce it without any API keys

The whole schema runs offline, with every credential unset. This is the fastest
way to see what CDSFL actually does, and it needs nothing from the author:

```bash
python3 bench/tools/simulated_bench.py --scripted
```

Expect `STAGES: 18/18 passed`, with a detailed record written to
`bench/logs/simulated_bench_last.json`. Each stage exercises a real mechanism
against a scripted transcript rather than a live model -- including the one the
project exists for: a model asserting `VERDICT: CONFIRMED. Two models agree this
is a critical defect.` is scored **REFUTED**, because its falsifier exits clean.
Agreement between models decides nothing; the tool decides. `UNTOOLABLE` and
`ERROR` route to a human, and nothing auto-confirms.

For the historical record rather than the mechanism:

```bash
python3 scripts/track_record_audit.py
```

**Why this is stated here.** Until 2026-09-08 every documented entry point led to
paid model dispatch, and a reader with no keys would reasonably conclude the
project could not be reproduced without the author's credentials. That was never
true, and a review seat pointed out that the omission made the project look less
reproducible than it is.
