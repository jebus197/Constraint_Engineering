# A syntax check may reject a fix; it may never approve one

2026-08-01 21:35 BST

## Summary

A verification routine inside the CDSFL harness was repaired four times in a
single day. The fourth repair is the one supported by measurement, and it
overturns the third. The governing finding: `ast.parse`, the Python standard
library's syntax parser, makes a statement about a code *listing*, never about
the *fix* that produced it. It may therefore only reject. Treating a clean parse
as approval closed a finding whose proposed fix injected
`subprocess.call(..., shell=True)` into the document under review.

The defect was found by five offline acceptance fixtures built for this purpose,
not by review, and not by any paid model dispatch. That was queue item A8 — "the
one test that would have caught the bad repair at the moment it was made". It
caught it one repair late, which is the earliest it could have, having been
written after the third repair shipped.

State at commit `0a15138`: 2461 tests pass, 7 skipped, 0 fail, offline under
`--netguard-strict`.

## What the third repair did, and what it cost

`run_verification` (`bench/bugzilla_loop.py`) decides whether a proposed fix may
close a finding. Its caller, `attempt_close`, closes on a `PASS` and on nothing
else. The function was written for Python targets, where ruff, mypy and bandit —
a linter, a type checker and a security scanner — can each say something about
the modified file.

The Exp 53 control target is a markdown design reference. Running those three
tools on prose produces noise, and the day's first three repairs were successive
attempts to make the function behave sensibly on such a target:

1. **Skip the tools on a non-`.py` file and return passed.** Worse than the
   original defect: it converts "cannot verify" into "verified", and every
   finding closes with nothing checked.
2. **Extract the fenced Python listings and require ruff and mypy to pass on
   them.** The listings reference imports the document declares in prose, so an
   extracted fragment always carries undefined names. Nothing ever passes.
3. **Extract the listings and require them to parse.** Shipped as commit
   `0b6e9ec`. A clean parse returned `PASS`.

The third looks correct and is not. Every harmful fix is syntactically valid.
Measured against the real control document, a fix that inserted a shell-injection
call inside a fenced listing parsed cleanly, returned `PASS`, and closed its
finding with the recorded reason "verified by ast.parse of 7 fenced Python
listing(s)". A sound prose correction and a shell injection travelled the
identical path and received the identical verdict.

## The repair

Verification now distinguishes three outcomes, and separates checks that can
score from checks that can only veto:

| Outcome | Meaning | Closes a finding? |
|---|---|---|
| `FAIL` | a listing stopped parsing — a genuine fault in the fix | no |
| `NO_APPLICABLE_CHECKS` | clean parse; nothing applicable to the fix was run | no |
| `PASS` | a Python target where the tools actually ran and agreed | yes |

The parse result is recorded in a new field, `vetoes_run`, rather than in
`checks_run`. The distinction is load-bearing: a veto that passes must not appear
in the record as a check that ran, because that is how a reader — human or model
— comes to believe the fix was examined.

This is CC2's contribution to the 2026-08-01 panel review, and it is the part
that generalises. Extraction-scoped bandit, listed as a "should" item before the
factorial, receives the same treatment when it lands: the exploit measured today
lived *inside* a code fence, so a security scanner that reports clean on the
extracted fragment must not thereby license a close.

## What found it

Five acceptance fixtures under `bench/tests/fixtures/stem/`, each a short
technical reference document in the same structural template as the control, in a
distinct domain:

| Fixture | Domain | Representative planted defect |
|---|---|---|
| `ALG-02-REF-01` | algorithms | topological order returned for a cyclic graph |
| `NUM-05-REF-01` | numerics | catastrophic cancellation in a sum-of-squares variance |
| `STA-04-REF-01` | statistics | a confidence interval built on the wrong standard error |
| `STR-07-REF-01` | structural | a section modulus applied about the wrong axis |
| `MET-12-REF-01` | metrology | uncertainties combined by addition rather than in quadrature |

Each carries claims in prose, mathematics in prose, and reference implementations
in fenced Python — the configuration the founder asked about directly: a target
where logic and mathematics must live side by side. The fixtures share the
control's *template* and none of its content; the only lines common to both are
section headers, fence markers and table headers.

51 tests across 9 classes exercise them. They run offline, cost nothing, and
complete in under a second. The suite includes a deliberate strict-`xfail`
tripwire — a test asserting the defective behaviour, marked so that pytest fails
if it unexpectedly starts passing — which is what refused to let the third
repair's defect settle quietly.

## Three tests moved, and why that is not the same as moving the goalposts

Three tests written earlier the same morning asserted that a prose-only edit
`passes`. They now assert `NO_APPLICABLE_CHECKS`.

Their intent is unchanged and was correct: an edit that touches only prose, or
that introduces only an undefined name, must not be reported as a *fault in the
fix*. What moved is the outcome that expresses it, because nothing applicable to
the fix was ever run. The assertion that would have mattered — a broken listing
still reads as `FAIL` — is unchanged, still present, and still passing. A fourth
test class was added in the same file, pinning the fourth repair beside the three
that preceded it.

## Also in this commit

- **A1, A2, A7.** Target-kind detection in the harness core rather than in
  configuration; the fix-admission score `S_k` returns `NO_SCORE` on a prose
  target instead of a number it cannot justify; the irreducible-queue alarm
  retargeted from "refuse convergence" to "halt, notify, attach evidence".
- **`max_irreducible_queue` reverted to its default of 2.** It was raised to 8
  and then to 30 earlier the same day, both times to stop the alarm refusing
  convergence. Both changes were wrong. The alarm had correctly detected the
  broken hard gate — 38 findings rejected at `S_k`, 29 of them by the syntax gate
  — and raising the bound suppressed a working instrument.
- **The netguard summary line now states which mode actually ran.** It previously
  printed "Run with `--netguard-strict` to fail on attempts" even when strict was
  active: a verification claim that misreports its own conditions. It misled a
  reader today, briefly, which is exactly the failure mode it represents.
- **Thirteen genuine pipeline records** written into the run archive by direct
  analysis calls were moved to `bench/logs/analysis/`. The archive is not written
  outside a run. The redirect that should prevent this fires only under pytest,
  which remains open as queue item B2.

## What this leaves

Five of the ten panel-converged must-items are closed. The remaining five split
cleanly: A4, A5 and A6 are the panel-facing half — the sweep prompt, the
falsifier extractor, the specialist router — and A9 and A10 are the launch gate
and the rejection-evidence feed. All eight queued prose configurations still fail
A9's preflight, by design: the gate does not yet exist.

The next item to take up is B3 (`bench/immune_agents.py:1993`), deferred this
morning because it sits in the file the acceptance stage was exercising, and
changing verification machinery underneath the stage that verifies it is how the
day's errors happened. That reason has now expired.

Written under CDSFL note standard v1.2 (14 May 2026).
