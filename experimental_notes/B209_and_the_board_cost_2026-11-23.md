# The anti-trap budget, and what 7 refused boards actually cost

*The anti-trap budget is a cap on refusals after which the gate must let go.*

**Date:** 2026-11-23
**Entries:** B209 (the `cy` gate's anti-trap refusal budget is inert), plus 2 new
findings on commit-board cost raised against an external advisory.

2 pieces of work are recorded here. The first repairs a safety mechanism in the
session stop gate that had never been able to fire. The second measures what the
commit board genuinely costs, in answer to an external advisory and to a concern
raised by the founder.

---

## Part 1 — the refusal budget that could not be reached

*The refusal budget is that same cap, counted against 1 key.*

CDSFL runs a `Stop` hook, `hooks/cy_monitor_gate.py`, that refuses to end a
session while an experiment is still live. So that it cannot trap a session for
ever, it carries an **anti-trap budget** of `MAX_REFUSALS = 60`, after which it
allows the stop regardless. Entry B209 recorded that this budget was unreachable
for precisely the runs the gate cannot read directly.

### The cause, in 2 lines

`hooks/cy_monitor_gate.py:415`:

```python
key = str(payload.get("session_id") or "") + "|" + \
    str(sorted(r["dir"] for r in live + unwatched) or pids)
```

With no watched run directory, `sorted([])` is falsy and the key embeds `pids`.
The board's real shape is **1 stable parent process with sub-second child
processes**, so the key changed on nearly every poll, `spend()` reset the counter
to 1 each time, and 60 was never approached.

### Candidates scored at the deciding layer

Scoring drove `main()`'s exit code (`2` = refuse, `0` = allow) rather than
testing `spend()` in isolation, because `main()` is the only layer whose verdict
reaches the session. The 5 scenarios are derived from the observed shape, not
invented; L2 is the measured live shape.

| candidate | L1 stable pid | L2 live shape | L3 live + idle | L4 new session | L5 full replacement |
|---|---|---|---|---|---|
| `HEAD`, unrepaired | 61 | **trapped** | **trapped** | **trapped** | **trapped** |
| composed (panel seat) | 61 | 61 | 181 | 61, refuses again | 181 |
| per-key (orchestrator) | 61 | 61 | 61 | 61, **never refuses again** | 61 |

The gate, as it stood before this repair, is trapped on **4 of 5** scenarios, Wilson 95%
[0.375535, 0.963776], Clopper-Pearson [0.283582, 0.994949]. The single scenario
it escapes is a stable lone process, which is not the shape the board has.

The orchestrator's own candidate passes 5 of 6 admissibility criteria and fails
the sixth: after releasing once it never refuses again, disabling the gate
permanently. It was **refuted twice, by 2 instruments at different layers**.

All 5 release indices predicted from the constants of the gate now adopted match the
executed values, cross-verified on 3 arithmetic routes (SymPy, `Fraction`,
NumPy).

### Composition was measured, not assumed

Under `composability-requires-a-measurement` a composed fix may be recommended
only with a measurement showing it dominates either part alone on a named
property. **Named property, fixed before any score existed: events until escape
on L2.**

| form | admissible | events to escape L2 |
|---|---|---|
| neither part (`HEAD`) | no, 2 of 6 | never |
| epoch/key repair alone | no, 4 of 6 | 61 |
| per-session ceiling alone | **yes, 6 of 6** | 181 |
| composed | **yes, 6 of 6** | **61** |

The ceiling alone is already sufficient. The composed form earns its place only
by escaping the live shape in 61 events rather than 181, ratio **2.967213**
(SymPy `181/61`, mpmath agreeing to 0.0).

Blast radius is contained: of 13 functions shared with `HEAD`, **11 are
behaviourally identical** once comments and docstrings are ignored; only `main`
and `spend` changed; **0 functions are lost**.

### The existing guard structurally cannot see this repair

`bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py` drives `spend()`
with key strings it constructs itself:

```python
got = [gate.spend("sess|" + str(p)) for p in CHURNING]
```

B209's defect was never in `spend()`; it was in the key handed to it. The repair
works by making the key **not** churn, so a test that supplies a churning key
manufactures the precondition the repair removes. Its recorded release condition
— *"an XPASS means the key was repaired and this marker must come off"* — is
therefore unreachable by a key-side repair, and `2 xfailed` must not be read as
"B209 is open".

**Nothing is removed.** Those 2 cases still hold a real property of `spend()`.
B209's verdict is recorded instead by a new guard at the deciding layer,
`bench/tests/test_the_cy_gate_releases_on_the_live_shape_2026-11-23.py`, which
separates all 4 candidates: composed 8 of 8, ceiling-only 7, the rejected
per-key fix 7, the gate as it stood before the repair 3. Its non-vacuity is proven rather than
asserted: it reads from git the gate as it stood before the repair and requires it to fail.

---

## Part 2 — what the board costs, measured

An external advisory argued the board now exceeds 3 hours, that running it
before every commit is not standard practice, and that it should be reserved for
major milestones.

### The central claim is false

Over 112 determinate runs: **mean 34.19 min, median 34.12, longest ever recorded
52.38, and 0 of 112 exceeding 3 hours.** The 3.13 h figure belongs to the full
suite of 18,419 tests, a different instrument run rarely. The advisory treats
the 2 as 1.

Producer: `scripts/why_is_the_board_getting_slower_2026-11-23.py`.

### The growth is real, and is the advisory's one strong point

Slope **1.6439 min/day**, `p = 1.410031e-21`, `R^2 = 0.5644`, 95% CI
[1.3740, 1.9137] min/day, on 2 agreeing routes (scipy `linregress` and
statsmodels OLS, matching to 1.33e-15). `R^2 = 0.5644` explains a little over
half the variance, so the growth is established and no dated projection is a
forecast. The cause is **not** identified: the leading hypothesis was measured
and refuted, the available saving being about 10.25 s, or 0.0036 of a 47 min
board, on an interval straddling 0.

### The sharpest finding is in neither document

**5 of 7 refusals on 2026-11-23 were avoidable with no reduction in gate
strength: 3.9875 h of the 5.5606 h spent on refusals.** Proportion 0.714286,
Wilson [0.358934, 0.917781], Clopper-Pearson [0.290421, 0.963307].

| cause | count | cost | remedy |
|---|---|---|---|
| ladder already selects the guard | 3 of 7 | 2.4006 h | make the hook **run** the ladder |
| 2 concurrent boards, each detecting the other | 2 of 7 | 1.5869 h | existing test seam + never run 2 boards |
| state guard the diff does not name | 2 of 7 | 1.5731 h | widen the selection rule |

The diff-derived pre-board ladder selects 47 guards, and **3 of the 5 distinct
guards that refused already sit in that selection.** They refused anyway because
the commit hook only *verifies* a stage-0 snapshot; nothing compels the ladder to
run. An existing, measured, useful mechanism that no caller reaches is exactly
the condition `additive-standard` names as a non-addition.

The concurrency pair is exact: boards at 05:15:12–06:02:59 and 05:16:27–06:03:53
overlapped by 46.5 min and **both refused naming the same guard**,
`test_the_parked_file_regenerates_without_losing_him_2026-10-17.py`. That guard
calls `blocker_triage.park()`, which refuses while a board runs (B155,
deliberate). The detector excludes its own process chain, so a lone board passes;
2 concurrent boards each detect the other. `park()` is the only function that
raises, and of the 3 guards calling it, 2 already use the `CDSFL_BT_BOARD` seam —
the 2 that test the interlock. Exactly 1 was unprotected, and it is the one that
failed.

All 5 distinct guards are green now and together run in **155.41 s = 2.5902
min**, against refusing boards of mean **2859.71 s = 47.66 min**, 95% t-interval
[45.82, 49.50] min.

**Window note:** 6 refusals among boards *starting* on 2026-11-23 and 7 among
boards *ending* on it, 1 having begun on 2026-11-22. Both are correct for their
window.

---

## A defect found in the measuring instrument itself

The brief's first version carried figures from a producer that resolved its
repository root by counting directory levels (`parents[1]`). Run from a scratch
directory the ledger was unreachable, `determinate_rows()` returned `[]`, and
**every figure in that draft was computed on an empty set.** Re-pointed it finds
112 rows, matching an independently written producer exactly, so the logic was
always sound and only the path was wrong. This is the **3rd instance of the same
location-dependent shape in a single session**, and the fix in all 3 is a marker
walk rather than a level count.

A second correction concerns an argument the orchestrator had made itself. The
draft claimed boards-per-commit was *"exactly what the measured refusal rate
predicts"*, concluding no board was wasted. That is an **identity, not
evidence**: with `r = refused/n` and `boards_per_commit = n/commits`,
`1/(1-r) = n/(n-refused)`, equal whenever `commits = n - refused`, which always
holds because every passing board yields 1 commit. SymPy returns a difference of
exactly `0`. The claim establishes nothing and is withdrawn.

---

## What the panel round added, and what testing it found

The blind round on this batch had already returned when this work began, and its
2 replies had not been read. Both seats independently found the same defect in a
predicate repaired earlier the same day, and both demonstrated it by **execution**
rather than argument, constructing a script that answers `--help` by writing a
file.

That repair was already in `fa687fda`. **The regression test seat `fable` named
was not.** The fix had landed with nothing holding the case that motivated it, so
a revert would have gone unnoticed. `test_a_decoy_derived_name_beside_a_constant_insert_is_refused`
is now added; it refuses the decoy while still crediting the unmodified fixture,
and goes red when the join is reverted, with the file restored byte-identical.

### The dispatcher refused twice and was right twice

| refusal | cause | remedy |
|---|---|---|
| joint-round debt | a blind round from 17:07 had never been followed by its joint half | run the joint round, discharging the debt |
| brief does not quote the parent | the gate samples spans at 0.25, 0.5 and 0.75 of each reply; the brief carried only the openings | embed both replies in full |

**Both of the orchestrator's own pre-checks reported a pass.** The first compared
text after stripping a `> ` prefix the gate does not strip; the second sampled
uniformly where the gate samples the interior. The remedy in both cases was to
call the gate's own `quotes_other_rounds` rather than a re-implementation, which
then reported `round_kind: joint`. A pre-flight must judge the gate's own
population — a shape already in this project's record.


## What happens next

The gate repair, the new deciding-layer guard, the corrected producer and the
test seam are prepared and apply as **1 atomic change** once the running board
lands; the apply-script refuses while a board is live, and verifies every anchor
before writing any byte.

The proposal to make the commit hook run the pre-board ladder itself, rather
than merely verify a snapshot, goes to panel review first, because it changes
when the gate runs. The 2 narrower fixes weaken nothing and were taken directly.

**No part of this recommends loosening the commit gate.** Under
`additive-standard` a removal requires a committed measurement showing the
replacement dominates on a named property, and no such measurement exists.

---

*Written under CDSFL note standard v1.9.*
