# The discrimination control: run at last, both routes. Half the archive's confirmations are demonstrated. Half are not.

**22 August 2026, 02:10–03:05 BST. HEAD `a171529` plus working tree.**
**Offline, zero dispatch, zero metered cost. Nothing was written to the real tree.**
**Reproduce: `scripts/discrimination_control_archive.py`, then `scripts/discrimination_cross_probe.py`.**

---

## What was asked, and the rule fixed in advance

The null-perturbation control (21 August) asked: change something the finding does
**not** accuse — does the falsifier stay put? 0 of 360 moved. That closed one half.

This is the other half, and four of five panellists named it as the next step:
**repair the accused defect, and the falsifier must go quiet.** Before any number
existed, a decision rule was taken from CC2 and recorded:

> **≥95% go quiet → the modern arc is H-BUILD without reservation.
> ≥10% still fire → it moves materially toward H-VOID.**

That rule is honoured below rather than renegotiated.

## Scope and method

372 CONFIRMED falsifiers across exp42–exp47, the code targets. exp48/exp49 are
excluded: their target documents are deleted from disk, so their falsifiers cannot
be re-executed at all.

Every execution ran inside a throwaway symlink overlay built by the runner's own
`_build_discrimination_overlay`. **The real repository was never written to.** The
earlier tool that adjudicated by repair wrote to the target file and restored it in
a `finally`; this deliberately does not.

Four preconditions, and nothing is scored until all four pass:

1. **Tripwire.** Replace the target with a file that raises on import. A falsifier
   that still returns a normal verdict never read the target — 8 findings excluded.
2. **Baseline.** The falsifier must FIRE against a real stored version of the file
   it accuses, found by `git log --all` version search. Without one, "went quiet"
   would be vacuous — 4 excluded.
3. **Determinism.** Two runs on identical bytes must agree.
4. **Whole-fix application.** All SEARCH/REPLACE blocks must apply, not some. Cross-
   verified two ways: 262 of 263 scored fixes carry exactly one block by both the
   regex and a raw `<<<< SEARCH` count. One fix has two blocks and one was dropped.

## Route A — repair the accused defect

| outcome | n |
|---|---|
| **DISCRIMINATES** — went quiet on its own fix | **132** |
| **NO_DISCRIMINATION_OR_INEFFECTIVE_FIX** — still fired | **131** |
| NO_APPLICABLE_FIX — the SEARCH block matches no stored version | 67 |
| INDETERMINATE_ERROR | 30 |
| INDETERMINATE_NOT_INTERCEPTED | 8 |
| EXCLUDED_NO_BASELINE | 4 |

**Of 263 scored findings, 132 went quiet: 50.2%.**

**Against the pre-registered rule this fails, and it fails on the H-VOID side.**
The threshold was 95%. The result is 50.2%, and 49.8% still fire.

## Route B — does it ever respond to the file it accuses?

346 of 360 fire on **every** stored version of their target; 14 go quiet somewhere.

**Route B is largely uninformative here and should not be quoted as 3.9%.** The
internal check says why: **126 findings went quiet on their own fix (route A) yet
fire on every stored version (route B).** This runner suggests fixes to a human and
does not commit them, so most accused defects were never repaired in git and a
correct falsifier is *right* to fire on every version. Route A is load-bearing.

## The confound, named in advance and then measured

"Still fires after the fix" conflates **the falsifier does not discriminate** with
**the proposed fix did not work**. These are model-proposed fixes that in most cases
were never applied or reviewed. A perfect falsifier facing a bad fix is right to
keep firing.

So each of the 130 still-firing falsifiers was re-run against up to 8 *other*
findings' fixes for the same file — patches known to be substantive because each
was observed to silence some other falsifier.

| | n | % |
|---|---|---|
| **SENSITIVE** — quiet on some other substantive change, so its own fix is what failed | **2** | 1.5% |
| **NEVER QUIET ON ANY CHANGE TESTED** | **128** | 98.5% |

**The bad-fix explanation accounts for 1.5%, not 50%.**

**The counter-objection, and it is real:** firing on another finding's fix is
*expected* of a correct falsifier — fixing defect Y should not silence a test for
defect X. So the 98.5% is not itself proof of brokenness. The evidence against these
131 is that they fire on their **own** fix. What the cross-probe adds is narrower:
for 128 of them, no condition tested anywhere — their own repair, eight substantive
edits, an unrelated function rename, every stored version — has ever been observed
to change their answer.

## The mirror control: are the 132 that passed actually specific?

A falsifier that goes quiet on *any* patch is not discriminating, merely fragile,
and its route-A pass would be hollow. So the same probe was run on the 132 passers.

| | n | % |
|---|---|---|
| **SPECIFIC** — quiet on its own fix, fires on all 8 others | **92** | 69.7% |
| also quiet on other findings' fixes | 40 | 30.3% |

**And the 30.3% is mostly not fragility.** Of those 40, **35 were silenced by only
one or two of eight** donors — the signature of *duplicate findings sharing a root
cause*, which is precisely the criterion this project's own counterfactual-repair
adjudicator uses to label a pair SAME. Exactly **one** falsifier was silenced by 8
of 8, which is genuine fragility. Four sit between.

**So the fragile population is 1 to 5 of 132, not 40.** The passing half passes
cleanly.

---

## The result, stated without softening

**Of 263 archived confirmations that could be tested, 132 (50.2%) are backed by a
falsifier demonstrated to fire on the accused defect and go silent on its repair,
and essentially all of those are specific. The other 131 still fire after their own
accused defect is repaired, and 128 of those have never been observed to go quiet
under any condition tested.**

By the rule fixed before the measurement, this moves the modern arc **materially
toward H-VOID**. Half the archive's confirmations are demonstrated. Half are not,
and are now known not to be.

## What this does NOT show, and the distinction is the whole point

It does not show that the design is unsound or that the engine cannot work. Three
reasons, each a measurement rather than a consolation:

1. **50% is not 0%.** 132 falsifiers do exactly what the design specifies: fire on
   the defect, fall silent on its repair, keep firing through eight other
   substantive edits. **A design that did not work would return near 0%, not a clean
   split.** What a working instrument applied to a mixed population looks like is
   precisely a split.

2. **The failure is located, and it is in the gate, not the concept.** CC2
   demonstrated on 22 August that `reverify_falsifier("print('FALSIFIED')")` returns
   CONFIRMED. The gate has never required a falsifier to demonstrate dependence on
   its target. Nothing about the *idea* of runner-adjudicated falsification fails
   here; one missing check does.

3. **This measurement is the repair.** The script that produced these numbers is the
   filter. Run it in-loop — the runner's `run_discrimination_control` already
   implements it with eight outcomes and three self-probes, and has simply never been
   fed a corrected copy — and the 131 never reach CONFIRMED in the first place.
   Applied retroactively it re-grades the archive rather than discarding it.

## What follows

1. **Feed the in-runner control.** It is presence-gated on a corrected copy no panel
   has ever been asked for. Ask for one: a finding's own proposed fix is already
   emitted, so the corrected copy is one apply away. Until then no future run can
   distinguish a demonstration from an assertion either.
2. **Re-grade the archive.** Stamp each of the 263 scored findings with its
   discrimination outcome. The 132 become demonstrated confirmations; the 131 become
   asserted ones. This is the typed-provenance work Codex wanted, and the data for it
   now exists.
3. **Investigate the 67 NO_APPLICABLE_FIX and 30 INDETERMINATE_ERROR.** A quarter of
   the population could not be scored at all, and that is its own finding.
4. **Do not start a live run until the in-loop control lands.** Adding runs to an
   instrument that cannot tell a demonstration from an assertion multiplies the
   problem measured here.

## Sources

`experimental_notes/data/discrimination_control_archive.json` (372 rows),
`..._cross_probe_never_quiet.json` (130), `..._cross_probe_discriminating.json` (132);
`bench/reference_runner_v2.py` `_build_discrimination_overlay`, `_retarget_falsifier`,
`run_discrimination_control`, `DISC_*`; `bench/falsifier_verify.reverify_falsifier`;
`experimental_notes/Track_Record_Audit_2026-08-22.md`;
`experimental_notes/Panel_Track_Record_FULL_RECORD_2026-08-22.md`.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
