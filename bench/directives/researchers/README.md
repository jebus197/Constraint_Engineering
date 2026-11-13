# Layer 3 — the researcher's own encoding

The directives README declares 3 layers. The runner composes layers 1 and 2
automatically; layer 3 is described there as "what the expert brings", and
until 2026-11-13 it had **never existed as a file**. This directory is that
layer.

## Why 3 files and not 1

A researcher encoding holds 3 things that change at radically different rates:

| file | what it holds | how often it changes |
|---|---|---|
| `standards.toml` | which domain encodings apply, and any standards cited directly | ~0.976 revisions/year, measured across the 4 standards feeds |
| `preferences.toml` | how this researcher prefers to work | rarely, and only when they say so |
| `confirmations.toml` | when each standard was last checked against upstream | every session start — ~1370/year at a measured 3.75 starts/day |

Putting them in one file makes a content hash useless as a tamper signal: it
would change 1370.66 times a year of which 0.98 are real, a precision of
**0.00071220**. Split, the standards file changes only when a standard does, so
the precision is **1.0** — a **1404.0952x** improvement on a named property.
That is why the split is the design and not a matter of taste.

## Why TOML

Not security — a `.txt` and a `.toml` sit in the same directory with the same
permissions. **Machine-checkability.** The 51 domain encodings have 5 different
header shapes and only 22 carry a full header, so a checker must handle 5 cases
and silently misses fields in the rest. A schema makes "this encoding has no
confirmation date" an error instead of something a regular expression shrugs at.

## Pointing, not restating

A researcher encoding **names** the domain encodings that apply to it rather
than copying their content. Pointing stays current automatically; restating goes
stale the moment a domain file changes. If a preference cannot be expressed
without restating a domain constraint, that is a finding about the domain
encoding, not a reason to copy it.

## Private and public

Two instances are expected: a local one carrying whatever the researcher wants,
and a repository one with health, neurotype and identifying detail removed. The
repository instance is the worked example others copy. **The researcher reads
the repository version before it is committed** — that judgement is theirs, not
the harness's.
