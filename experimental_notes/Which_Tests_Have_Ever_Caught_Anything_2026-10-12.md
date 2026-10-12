# Which tests have ever caught anything — 2026-10-12 14:15 BST

The founder asked, after noting the real risk that tests come to test other tests:
*"there may be a question of if all these tests are necessary to begin with?"* He
approved this measurement and asked for it **before** anything is trimmed.

Producer: `scripts/which_tests_have_ever_caught_anything_2026-10-12.py`.

## What it cannot tell you, first

A guard whose whole value is that nothing ever happened appears in **no** commit
message. So a test with no record here is **UNKNOWN, not useless**, and this is not a
deletion list. Reading it as one would infer a property from the absence of a text
match — the error this session made 6 times, including twice inside this very
measurement.

## The result

Over **1,702** commits on all refs and **571** live test files:

| | files | share | 95% interval |
|---|---|---|---|
| demonstrably CAUGHT something | 75 | 0.1313 | Wilson [0.1061, 0.1615], CP [0.1047, 0.1618] |
| named, never in a defect commit | 95 | 0.1664 | Wilson [0.1381, 0.1991] |
| never named in any commit | 401 | 0.7023 | Wilson [0.6635, 0.7383], CP [0.6629, 0.7395] |

A test is credited as CAUGHT only when a commit names it, that commit's message carries
defect language, **and** it is not the file's own creation commit — so being named once
on the day you were written earns nothing.

Cross-verified by a second, independent instrument: per-file fixed-string search instead
of one regex sweep. It agrees **exactly** at 401, and 40 of 40 agree on a random sample.

Most-credited files, which are the mundane ones: the immune-memory consumption guard (5),
the memory-ledger repair guard (4), the operational-scripts guard (4), the `--help` guard
(4). Three of those caught **this session's own work**.

## A figure withdrawn

The first run reported **527 of 571, 0.9229**, never named. That was wrong. The pattern
was `test_[A-Za-z0-9_]+\.py`, which excludes the hyphen — and this project names test
files with dates, so **every dated test file was invisible to it**. The figure was an
artefact of the instrument, withdrawn before use, and it inflated the true value by 22
percentage points.

## What it licenses

Not a trim. It establishes a **floor** on the suite's value and rules out the cheap
answer. The honest trim target is the intersection of **slow** and **no record of ever
firing**; this supplies only the second half. The suite costs 3,468.81 s — 57 min 48 s —
so the first half is a per-file timing run, which has not been done.

---

*Written under CDSFL note standard v1.7.*
