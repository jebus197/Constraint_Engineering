# The experimental archive

Where the raw experimental material lives, and how to cite it.

**Status as of 2026-08-16: UPLOADED AS A DRAFT, NOT PUBLISHED.**

The archive is on Zenodo as deposition **21959922**, 84.4 MB compressed from roughly
340 MB, 6,725 files, checksum recorded on upload. It is a draft: it has no DOI, it is
not publicly visible, and it can still be replaced or deleted.

**Publishing is deliberately left to the repository owner**, because publication mints
a permanent DOI and cannot be undone. Review the draft at
`zenodo.org/deposit/21959922`, check the metadata reads correctly, then press Publish.

Nothing has been removed from this repository and nothing will be until the archive is
published and its DOI recorded below.

---

## Why the material is split

Two different things get produced by every experimental run, and they serve different
readers.

**The record** — the final report and `runner_state.json` for each run. These carry the
finding registries, the falsifiers each model wrote, and the verdict the framework
reached on each one. This is what anyone checking a claim needs. Measured August 2026:
13.4 MB across 76 files. It stays in this repository, because evidence that requires a
second download is evidence most readers will not look at.

**The raw material** — the complete unedited output of every model in every round,
plus checkpoints, shadow traces and debug logs. Measured August 2026: roughly 340 MB
across 5,760 files. This is primary source rather than analysis. It is preserved, not
discarded, but it does not belong in a working repository.

The reason is measurable rather than aesthetic. Before the split, `bench/logs` was
96.8% of this repository by size and 86% of its files, against roughly 11 MB of actual
project. Two consequences followed. A human browsing saw a file count that suggested an
impenetrable codebase and reasonably declined to read it. An automated reader — a
crawler, or a model asked to summarise the project — exhausted its 60 unauthenticated
GitHub API requests per hour inside the log directory and reported that it could not
access the repository at all.

Neither reader was being served by keeping everything in one place.

---

## What the archive will contain

| Category | Size | Files |
|---|---|---|
| Raw per-model responses | 236.5 MB | 4,074 |
| Other run artefacts | 44.8 MB | 1,257 |
| Checkpoints (resumable working state) | 32.2 MB | 52 |
| Append-only debug logs | 21.9 MB | 143 |
| Shadow traces (diagnostic) | 4.2 MB | 238 |

Organised by run directory, preserving the existing structure, so a path cited in any
project note resolves inside the archive unchanged.

**One limitation, stated because it affects reproducibility.** Each per-model record
stores the model's response and the *length* of the prompt it received, but not the
prompt text. Prompts are reconstructible from the directives, targets and configuration
held in this repository, but they were not recorded at the time. Anyone attempting an
exact replay should know this before starting.

---

## Where it will live

**Zenodo**, the open research archive operated by CERN. It is free, it has no
institutional affiliation requirement, and it issues a DOI — a permanent citable
identifier of the same kind a journal article carries. The link does not rot, and the
project's paper can cite the dataset the way it cites any other source.

Alternatives considered: the Open Science Framework, Figshare, and Dryad are all
equivalent for this purpose. Zenodo is the usual default for software-adjacent research
and integrates directly with GitHub. A second GitHub repository was also considered and
rejected: it solves the file-count problem but provides no permanent identifier, so the
paper would have nothing stable to cite.

---

## Remaining steps

Steps 1 to 3 are done. The rest need the repository owner.

1. ~~Build the archive~~ — done. 84.4 MB compressed, 6,725 files, excluding the
   per-run reports and `runner_state.json`, which stay in this repository as the record.
2. ~~Create the Zenodo deposition~~ — done, id 21959922, metadata from `.zenodo.json`.
3. ~~Upload~~ — done, checksum verified on receipt.
4. **Review and publish.** Open `zenodo.org/deposit/21959922`, check the description,
   creator and licence, then press Publish. This mints the DOI and is irreversible,
   which is why it is not automated.
5. **Record the DOI** in the citation section below.
6. **Only then untrack the archived material.** The `.gitignore` rules already prevent
   new accumulation; this step removes the existing 353 MB from the working tree. It
   is what finally fixes the file-count problem that made the repository unreadable to
   automated readers.

Step 6 is deliberately last. Nothing leaves this repository before its replacement is
published and citable.

---

## Citing it

Once published, this section will carry the DOI and a formatted citation. Until then
there is nothing to cite, and this file says so rather than implying otherwise.
