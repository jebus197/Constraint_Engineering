# PANEL ROUND ON BATCH 12: THE WIDENED PREDICATE AND THE BOUND THAT WAS NOT EVIDENCE

Record written 2026-11-23T18:43:46+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHY THIS ROUND EXISTED AND WHAT IT COST TO HOLD THE RULE

The commit board for batch 12 was 70 seconds into its run when the gate
reported 0 panel rounds since the previous commit. The board was killed rather
than the line ignored, because the preceding round had measured that 7 of 10
commits landed with no panel round and that the gate's line had been walked
past every time. Killing a board costs about 1 minute at that point; ignoring
the line costs the rule.

The easy argument was available and was not taken. Much of batch 12 adopts
proposals the previous round made, each tested first, so it could be argued no
new round was owed. It was owed, because the batch also contained work of mine
that no panel had seen, and 1 item of that work LOOSENED a predicate that a
board guard depends on, which is the shape most likely to be wrong in a way
nothing notices.

THE FIRST FINDING: THE WIDENING LET A SCRIPT WRITE

A seat found that the widened predicate asked its 2 conditions SEPARATELY of
the same collection of syntax nodes, with nothing requiring them to be the same
expression. A script whose path insertion takes a CONSTANT path, with a
file-derived name sitting beside it for an unrelated reason, was therefore
credited as safe.

This was reproduced before it was accepted. A constructed script of that shape
was placed in a temporary directory and run with the help flag: the predicate
reported it safe and the script WROTE A FILE. The condition is now joined, so
the file-derived value must be an argument of the path insertion itself, which
is the only reading under which the insertion says anything about where the
script lives. 2 further tests pin the exact shape, and the harness
adopted in the same batch, which runs a check with the defect present and then
absent, confirms they discriminate: the new
test fails with the separated form present and passes without it, with the
target restored byte for byte.

THE SECOND FINDING: A CONFIDENCE BOUND THAT WAS NOT EVIDENCE

A seat refused the framing of a measurement I had reported, and it was right to.
I had reported 0 full replacements in 14 observed pairs with a Wilson upper
bound of 0.215311, and offered it as corroborating the position of 1 of the 2 seats.

At 0 events the Wilson upper bound is exactly the squared critical value divided
by the sum of the sample size and that squared value. SymPy simplifies the
difference against the full Wilson expression to exactly 0 and the derivative
with respect to sample size to a strictly negative quantity, and statsmodels
agrees numerically at sample sizes of 9, 14, 69 and 200 to machine precision.
Since the sample size was the POLL COUNT, which was 14, the bound was set by
the polling interval, which is a free parameter, and not by the world.

Demonstrated rather than argued: the same unchanging process polled over 20
seconds yields 69 pairs and an upper bound of 0.052737 at an interval of 0.25
seconds, against 9 pairs and 0.299145 at an interval of 2.0 seconds. That is a
factor of 5.7 on identical evidence. The denominator also admitted pairs in
which the event was impossible, since a full replacement requires both
observations to be non-empty.

The repair, whose own falsifier was run before adoption, counts OPPORTUNITIES
instead: pairs in which the matched set actually changed with both sides
non-empty, which are the only occasions on which the event could have occurred.
With 0 opportunities the probe now prints no bound at all. Driven, an unchanging
set yields 0 opportunities at 15 polls and still 0 at 149 polls, so the
denominator is invariant to the polling rate, while a genuine replacement is
still counted.

The corrected reading corroborates NEITHER seat, because a non-occurrence in 0
opportunities is not an observation.

WHAT WAS DONE WITH THE FINDINGS

Both repairs were adopted after being reproduced and tested, and the figure I
had reported was withdrawn with its reason recorded rather than quietly
corrected. The withdrawal is the more important half: an interval whose width
was mine to choose had been presented as evidence, and more sampling would have
narrowed it while adding nothing, manufacturing confidence from an unchanging
process. That is the opposite of what a confidence interval is for.

A third proposal from the round remains untested: that the panel-coverage
line's defect was that its verdict went unrecorded rather than that it only
reported, so a ledgered advisory line might be the simpler sufficient fix. The
seat flagged its own preference for refusal as a judgement rather than a
measurement, and that flag is accepted.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — batch 12, 2026-11-23

**WHY THIS ROUND EXISTS, AND IT IS THE RULE BEING FOLLOWED RATHER THAN QUOTED.**
The preceding round measured that 7 of 10 commits had landed with no panel
round, and the commit gate's panel line was walked past every time. This batch
was 70 seconds into its board when that line reported 0 rounds since HEAD. The
board was KILLED rather than the line ignored again.

<!-- figure: help writers at HEAD | scripts/help_writers_rate_2026-09-17.py | 6 of 837 write and ignore --help = 0.7168% -->

**A NOTE ON THAT DECLARED FIGURE, BECAUSE THE VALIDATOR REFUSED MY FIRST
ATTEMPT AT IT AND WAS RIGHT TO.** I first declared **0 of 837**, which is the
working tree's figure, against a validator that runs the producer BARE — and
bare it measures HEAD. The declaration was a claim about bytes that are not
committed. The honest statement is 2 figures with their revisions named:
**6 of 837 at HEAD**, re-executable and declared above, and **0 of 839 on the
working tree**, obtainable only as
`python3 scripts/help_writers_rate_2026-09-17.py :worktree` and therefore NOT
declared here. The difference of 2 in the population is the 2 producers this
batch adds. And the producer imports its predicate from the WORKING TREE at all
times, so even its HEAD figure is HEAD's scripts judged by this batch's new
predicate — which is worth knowing before Q1 is answered.

**THE EASY ANSWER IS AVAILABLE AND IS NOT TAKEN.** Much of this batch adopts
proposals the previous round made, each tested first, so it could be argued no
new round is owed. **It is owed, because the batch also contains work of mine
that no panel has seen** — and 1 item of that work LOOSENS a predicate a board
guard depends on, which is the shape most likely to be wrong in a way nothing
notices.


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `scripts/help_writers_rate_2026-09-17.py` | `14a12b88f67113dc` | 5648 | 2026-09-17T17:33:09+00:00 |
| `bench/tests/test_help_never_acts_2026-09-11.py` | `c129c66e1abadfea` | 24670 | 2026-11-23T16:46:09+00:00 |
| `scripts/the_restore_mutations_2026-11-22.py` | `60d690634390362e` | 5592 | 2026-11-22T05:56:49+00:00 |
| `scripts/the_majority_separation_mutations_2026-11-22.py` | `dfcf68298596492f` | 5811 | 2026-11-22T15:46:15+00:00 |
| `scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py` | `2a7e4586a2e0ba06` | 6768 | 2026-11-23T16:32:28+00:00 |
| `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py` | `d4c07b7eb005aa88` | 8770 | 2026-11-23T16:50:05+00:00 |

## WHAT IS IN THE BATCH

Entry B212, the help-flag repair that regressed, is CLOSED at 0 of 839 on the working tree under
both invocations. Entry B215's seat disagreement was measured rather than
adjudicated. 2 of the previous round's proposals were adopted after testing. A
defect in the pre-board deriver was found while using it and fixed.

## USE THE HARNESS — answer by RUNNING things

Every seat must reach its answer by executing something and report the exact
command and output. `gamma` and the two-sided gate bear on Q2 as the
diminishing-returns measures: an upper bound that cannot exclude a rate of
0.215311 is weak evidence, and the question is whether it is weak enough to
withhold a conclusion. The severity model bears on Q1: say what severity a
wrong widening carries, and say so explicitly if no concrete failure can be
named, because an unnameable failure is not a finding.

---

## Q1. I WIDENED AN ACCEPTING PREDICATE THAT A BOARD GUARD DEPENDS ON. IS IT RIGHT?

`bench/tests/test_help_never_acts_2026-09-11.py:answers_help` decides whether a
script answers `--help` under `python3 -m`. It is a STATIC predicate, and
`scripts/help_writers_rate_2026-09-17.py` imports it, so there is 1
implementation and no second opinion anywhere.

**IT ACCUSED 2 CORRECT SCRIPTS.** It searched for the `sys.path` insert ONLY
among statements inside the same `try` and before the import, and required the
literal `__file__` among them. `the_restore_mutations_2026-11-22.py` and
`the_majority_separation_mutations_2026-11-22.py` place the insert among the
try's PRECEDING SIBLINGS and reach `__file__` through a module-level `REPO`.
Driven in a throwaway clone, with a tree-hash instrument validated on an
untouched tree first because its initial form was order-dependent, both exit 0
and change 0 Python bytes under direct invocation, under `-m` from `scripts/`,
and under `-m` from the repository root.

**MY WIDENING CREDITS 2 THINGS: a preceding-sibling insert, and a module-level
name whose own assignment contains `__file__`.** The second is the one I distrust
in my own work: it is a 1-step dataflow approximation, and a name assigned from
`__file__` somewhere else in the module may have nothing to do with the path
being inserted.

**P-PASS DONE, BOTH DIRECTIONS:** 5 discrimination tests, 15 passed. A
swallowing `try` with no insert is still unreachable under `-m` and still
reachable directly; an insert inside the try still counts; a script with no
handler is refused; **an insert built from a CONSTANT path is refused.**

**THE QUESTION.** Is the file-derived-name rule too permissive, and if so give a
constructed source it wrongly credits. Is a static predicate the right
instrument here at all, when an executing one costs about 18 s over 837 scripts
and would need no approximation? Name the concrete failure your answer permits.

## Q2. IS 0 OF 14 WITH AN UPPER BOUND OF 0.215311 EVIDENCE, OR NOT?

The previous round's 2 seats disagreed on entry B209's repair. Driven, both
their scorers reproduce and the disagreement is narrower than it looked: cc2's
S3 and fable's R1 are THE SAME scenario — the overlap key failing when the
matched process set is fully replaced between 2 consecutive polls. They agree on
the fact and differ on its WEIGHT.

<!-- figure: full replacement rate | scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py | FULL REPLACEMENTS (both non-empty, no overlap): 0 -->

`scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py` polls the gate's
own `_RUNNER_PATTERNS`, read out of the hook rather than typed, while a real
pytest run is live. Across 25 polls of a 106 s run and 14 pairs of a second run:
**0 full replacements, every pair identical, pid-set size 1 throughout.** Wilson
[0.000000, 0.215311] on 2 routes agreeing to 2.78e-17.

**THE INTERVAL FIGURES IN THIS SECTION ARE NOT DECLARED, FOR THE SAME REASON AS ABOVE.** The probe reports an interval only when something matches its patterns, so run bare — which is how the validator runs it — it correctly prints UNINFORMATIVE and no interval at all. The declared figure above is the part that re-executes; 0.215311, 0.000000 and the 2.78e-17 agreement come from runs taken while a real pytest was live, reproducible as `python3 scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py --seconds 30` with a suite running beside it. Treat them accordingly.

**I HAVE REPORTED THIS AS CORROBORATING fable AND AS CUTTING AGAINST B209's OWN
PREMISE**, which states the key churns because a board replaces its pytest child
per guard file. A single stable pid is not what that predicts.

**THE QUESTION.** Does an upper bound of 0.215311 support either conclusion? A
reading I can see and cannot refute is that 14 pairs of a short run say nothing
about a 34-minute board with other matched processes alive, so BOTH claims
should be withheld. Say which, and say what sample would settle it.

## Q3. WAS MY TESTING OF YOUR OWN PROPOSALS SUFFICIENT BEFORE I ADOPTED THEM?

2 proposals were adopted. **The fixer change**: its diagnosis was confirmed
first — all 6 declined files use `from pathlib import Path` — then in a clone
report named 6, `--apply` fixed 6, the rate fell to 0 of 837, all 6 compile and
answer `--help` writing 0 bytes, and a repaired harness RAN TO COMPLETION at 7
of 7 mutations RED with SHA-256 verified restore. **The differential falsifier
rule**: validated against known answers both ways, DISCRIMINATES on the real
guard at 3 failed against 21 passed, VACUOUS on an unrelated guard at exit 1,
target restored byte-for-byte in both arms.

**THE QUESTION.** What did that testing NOT cover? For the fixer, I ran 1 of the
6 repaired harnesses to completion and checked the other 5 only for compilation
and `--help`. Is that sufficient, or is the 1-of-6 sample the weak point?

## Q4. THE ONE PROPOSAL STILL UNTESTED, AND WHAT WOULD MEASURE IT

cc2's answer to the panel-line question reframed it from refuse-against-report
to AUDITABILITY: a reporting line that appended its own verdict to a ledger
would have made all 7 lapses visible on the first commit at no cost, so
unrecorded report was the defect rather than report itself. It flagged its own
preference for refusal as a judgement rather than a measurement, and that flag
is accepted.

**THE QUESTION.** What measurement decides between a ledgered advisory line and
a refusal? State a predicate a hook can evaluate and an outcome that would
distinguish them, not a preference. Note that this batch is itself 1 data point:
the line reported, and the board was killed rather than the line ignored.

---

## PRODUCE A FIX, AND TEST IT

A finding without a fix is incomplete. **A fix without a runnable falsifier the
seat has EXECUTED is a hypothesis, not a fix.** Report the exact command and the
output verbatim.

**Deliver your fix as a file,** written INTO the sandbox repository tree at its
real path. A fix described in prose is not delivered, and a fix written to
scratch space is destroyed at teardown.

**THE DIFFERENTIAL RULE NOW APPLIES TO YOUR OWN FALSIFIERS, and the tool is in
the tree:** `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py` runs a
falsifier with a defect present and absent and refuses a verdict when the 2
arms agree. Use it on any falsifier you write here, or say why it does not fit.

**Where more than 1 repair is in play, composability is a CLAIM THAT REQUIRES A
MEASUREMENT** — the founder's definition of 2026-10-02: compose only on a
demonstrated advantage over each fix alone, and prefer the single fix where it
performs as well. Reporting that 2 repairs merely do not interfere is the weak
form his definition excludes.

## WHAT WOULD REFUTE YOU

State what evidence would overturn your own answer. A verdict with no stated
refutation condition is an opinion and will be recorded as one. Where a question
is not decidable on the available evidence, say so and say what would decide it.

## OUTPUT SHAPE

For each of Q1 to Q4: `question`, `verdict` in 1 sentence, `reasoning` naming
the instrument you ran, `commands_run` verbatim, `fix` as a repository-relative
path or NONE, `falsifier` with the result of EXECUTING it,
`what_would_refute_me`, and `disagreement` — your strongest disagreement with
this brief's framing, including with any figure in it. Mandatory and it may not
be empty.

**Do not converge.** Disagreement is preserved as information. Anything proposed
here will be TESTED before adoption.

## TERMINATION

Stop when a further pass produces no new above-threshold findings, and state how
many passes you ran. A finding is above threshold if missing it could cause a
real-world failure, an unsafe condition, or a wrong decision by the founder.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 37 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_b12_20261123T170728Z) -->

Five passes run. Both fixes are in the tree, both falsifiers DISCRIMINATE, and the targeted suite is unchanged at `3 failed, 12 passed` (the 3 failures are the absent `.git` in the staged sandbox, identical before and after my edits).

---

## Q1. The widened accepting predicate

**question** Is the file-derived-name rule too permissive, and is a static predicate the right instrument?

**verdict** The widening is wrong, but **not for the reason you distrust** — the defect is that `inserts` and `uses_file` are asked *separately* of the same bag of nodes and nothing requires them to be the same expression; I have a constructed source that is credited and, run as `python3 -m x --help`, **writes a file**.

**reasoning** Instrument: the real `answers_help` imported from `bench/tests/test_help_never_acts_2026-09-11.py` (digest `c129c66e1abadfea`, as dispatched), plus direct execution of a constructed script under `-m`. Lines 225–232 of the dispatched file compute `inserts` (is there *any* `sys.path.insert` before the import) and `uses_file` (is there *any* file-derived name before the import) over the same node list, then accept on `inserts and uses_file`. The insert's **arguments are never inspected**. So a constant-path insert with a file-derived name beside it for an unrelated reason is credited.

Your own discrimination case `test_a_file_derived_name_is_required_not_just_any_insert` does not catch this, and its docstring claims more than it tests: it builds its constant-path variant by *replacing* the `__file__` assignment, so `__file__` vanishes from the whole module and `uses_file` is False for a reason the realistic shape does not share. Scrub-the-module is a weaker property than insert-must-carry-the-path.

Two constructed sources, both credited by the dispatched predicate:

```
B derived-name rule only     WRITES=True  dash-m credited=True
C bare __file__ sibling      WRITES=True  dash-m credited=True
```

`C` uses **no derived name at all** — just a bare `__file__` among the preceding siblings. So the half of the widening you trust (preceding siblings) is independently sufficient to break the predicate, and the half you distrust (file-derived names) is not required. **Your self-distrust is aimed at the wrong half.**

The concrete failure, executed rather than argued:

```
--- DIRECT invocation with --help ---
usage: (help answered, nothing written)
exit=0  wrote=NO

--- python3 -m scripts.constant_insert_demo --help ---
exit=0
wrote=ORDINARY_WORK_RAN.txt
this script just wrote a file
```

**Severity.** The help-ratchet domain declares no consequence scale of its own, so per the ordinal-severity rules it **inherits the application domain's** — the panel-record corpus, whose scale this guard's own comment names ("54,480 bytes of a record the founder's own directive requires preserved verbatim"). On that inherited ordering the defect is at the critical level under §10 category 3, **verification-integrity corruption**: a defect in the measurement machinery. I will not supply a number, and I note precisely what is *not* claimed — **0 scripts in the real tree are currently affected** (measured below), so the realised loss today is zero. The defect is in the guard's future accepting behaviour, not yet in the tree.

**Is static the right instrument?** Yes, keep it static. An executing predicate costs ~18 s and needs no approximation, but it must *run 837 untrusted scripts with `--help`* to decide whether they write — the exact action the guard exists to prevent, on the exact population most likely to do it. That trades an approximation for a 19-way-door execution surface, and your own record says the flag "was never the only way in." The approximation is repairable; the execution risk is not. Repair the join.

**fix** `bench/tests/test_help_never_acts_2026-09-11.py` (post-fix sha256 `d5c314c415abd8eb366a92`) — the file-derived value must be an **argument of the insert**. 13 lines, replacing two independent `any()` calls with one that walks `call.args`. No feature removed; the residual (`str(REPO / "vendor")` is file-derived but not the script's own directory) is unchanged and now stated in the code.

**falsifier** `scripts/the_insert_must_carry_the_file_2026-11-23.py` — imports the real predicate, asserts 3 constant-path shapes REFUSED and 4 genuine shapes CREDITED including both scripts the widening was written for. Executed:

```
  must REFUSE  constant insert, derived name beside it    -> False
  must REFUSE  constant insert, bare __file__ beside it   -> False
  must REFUSE  constant insert inside the try             -> False
  must CREDIT  preceding-sibling insert via a file-derived name -> True
  must CREDIT  insert inside the try, built from __file__ -> True
  must CREDIT  the_restore_mutations_2026-11-22.py        -> True
  must CREDIT  the_majority_separation_mutations_2026-11-22.py -> True
  must CREDIT  assemble_panel_record.py                   -> True
exit=0
```

Driven through your differential rule against the pre-fix bytes:

```
  DEFECT PRESENT  exit=1  FALSIFIED-token=True  -> FAIL
                  |   CREDITED a constant-path insert: constant insert, derived name beside it
  DEFECT ABSENT   exit=0  FALSIFIED-token=False -> PASS
  target restored byte-for-byte : True
  DISCRIMINATES
```

Regression over the real population — **0 verdict flips on all 840 scripts** (recursive; `840 = your worktree 839 + my 1 new script`, which reconciles your figure exactly), and 0 dash-m offenders after the fix. The join is a pure tightening that touches no real script.

**what_would_refute_me** A real tracked script that legitimately answers `--help` under `-m` while its insert's *arguments* contain no `__file__` and no file-derived name — e.g. one that mutates `sys.path` through a helper function call, `sys.path[0:0] = [...]`, or `site.addsitedir`. My fix would wrongly accuse it. I measured 0 such scripts in 840 today; one appearing tomorrow refutes the fix, and the repair is to credit those forms explicitly rather than to un-join the conjunction.

**disagreement** Two with your framing. First, as above: you nominate the file-derived-name rule as the suspect and it is not the culprit — case `C` breaks the predicate with no derived name. Second, **your declared figure "6 of 837 at HEAD" is not re-executable by any seat in this dispatch.** The sandbox has no `.git`, so the producer refuses:

```
REFUSING: git cannot list scripts/ at HEAD: fatal: not a git repository
```

That refusal is correct behaviour — `tracked_scripts()` deliberately refuses rather than reporting 0 offenders from an empty list, which is good design. But it means your note about declaring HEAD's figure rather than the working tree's solved a validator problem while leaving the figure unverifiable *here*. I substituted a recursive glob and said so.

---

## Q2. 0 of 14, upper bound 0.215311

**question** Is that bound evidence for either conclusion?

**verdict** **Neither** — and the bound is not "weak evidence", it is **not evidence at all**: it is a function of `--interval`, a free parameter, computed over a denominator that includes trials in which the event was impossible.

**reasoning** Two instruments. SymPy, symbolically: at k=0 the Wilson upper bound simplifies to exactly `z²/(n+z²)`, verified `upper - z²/(n+z²) == 0`. Confirmed on an independent kernel — Wolfram Language (local Wolfram Engine, via `wolframscript`, exit 0, no `Name::tag`, no `$Failed`) returned `0.2153108027376358`, `0.0036109316748686583`, and `0.` for the simplification difference. That form is strictly decreasing in `n`, and `n` is the **poll count**:

```
  pairs=   14  Wilson 95% upper = 0.215311   <- your 14 pairs
  pairs=   53  upper = 0.067582   <- the SAME 106 s run at 2.0 s
  pairs= 1060  upper = 0.003611   <- the SAME 106 s run at 0.1 s
```

Identical evidence — one unchanging pid — yields any bound you like. This is not hypothetical. I ran your probe against a live pytest for **20 seconds at 1.0 s spacing**:

```
  pid-set sizes seen                            : [2]
  consecutive pairs considered                  : 19
  FULL REPLACEMENTS (both non-empty, no overlap): 0
  Wilson 95%            : [0.000000, 0.168179]   (mpmath closed form agrees to 2.78e-17)
```

**A fifth of the observation time produced a tighter bound than yours.** An interval that narrows as you look less is measuring the observer, not the world. (Your `2.78e-17` two-route agreement reproduced exactly; that part of the instrument is sound. Note also pid-set size was **2**, not 1 — so "size 1 throughout" is not an invariant of the setup.)

Second defect, falsified directly on `classify`:

```
  alternating matched/empty -- event IMPOSSIBLE in every pair -> (0, 0, 15, 15)
  alternating case: 0 of 15 pairs, Wilson 95% upper = 0.203883
```

A full replacement requires both sides non-empty *by definition*, so those 15 pairs could not have contained the event — and they produce a bound **tighter than the one you declared**. The denominator is not a risk set.

So: withhold both claims, which is the reading you said you could see and could not refute. I confirm it and strengthen the ground. But one asymmetry survives — the probe does cut against B209's *premise*, because that premise predicts churn and 0 observed changes is inconsistent with churn *during a single pytest invocation*. That is weak and it is not the same as supporting either seat.

**What would settle it.** The identified denominator is **observed set-change events**, not polls, and it must be collected where churn is possible: a real 34-minute board that spawns a pytest child per guard file, not one invocation. With 0 events observed you need `n ≥ z²(1−ε)/ε` change events: **35** for ε=0.10, **73** for ε=0.05, **381** for ε=0.01. There are 971 files in `bench/tests/`, so if a board really replaces its child per guard file, one board supplies hundreds of change events and ε=0.01 is reachable in a single board — which is exactly why observing one board is the measurement, and 14 polls of a pytest never will be.

**fix** `scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py` (post-fix sha256 `31d53477cc6b7068cc5b6d`). `classify` now also returns `opportunities` — pairs where the set actually changed with both sides non-empty. With 0 opportunities the script prints **UNIDENTIFIED** and reports no bound, showing the poll-pair figure explicitly as a diagnostic of the polling rate. **Every previously printed count is still printed**; only the claim attached to them is corrected. I also split out a branch that would otherwise have printed "Nothing matched the gate's patterns" when processes *had* matched — found in my own fix on pass 5, and it now says the honest thing: corroborates neither seat.

**falsifier** `scripts/the_replacement_denominator_must_be_opportunities_2026-11-23.py`. Executed:

```
  A/C unchanging set, 15 polls        -> classify = (0, 14, 0, 14, 0)
  C   same set, 10x the polls         -> classify = (0, 149, 0, 149, 0)
  B   alternating matched/empty       -> classify = (0, 0, 15, 15, 0)
  D   a genuine full replacement      -> classify = (1, 0, 0, 1, 1)
  E   z^2/(n+z^2) at n=14             -> 0.215311 (expected 0.215311)
exit=0
```

Poll-pairs go **14 → 149** under 10× polling while opportunities stay **0**: the invariance is the whole point. Case D is the anti-vacuity arm — the fix cannot pass by reporting 0 for everything. Differential: `DEFECT PRESENT exit=1 FALSIFIED-token=True -> FAIL`, `DEFECT ABSENT exit=0 -> PASS`, `restored byte-for-byte: True`, **DISCRIMINATES**.

**what_would_refute_me** One observed full replacement on a real board promotes the scenario from unrealised to demonstrated and makes cc2's weight the right one. Separately, if the board genuinely runs one long-lived pytest rather than a child per guard file, then B209's premise is simply false and the whole disagreement dissolves — which would make my "re-measure the premise" the wrong recommendation and "withdraw B209" the right one.

**disagreement** I reject "an upper bound that cannot exclude a rate of 0.215311 is weak evidence." It is not on the evidence axis at all. Calling it weak invites the repair "take more samples", which here makes the bound *tighter without adding information* — the worst possible outcome, because it manufactures false confidence from the same unchanging pid. I also disagree with your framing that the probe "polls the gate's own `_RUNNER_PATTERNS`, read out of the hook rather than typed" as a sufficiency argument: reading the matcher from the hook guarantees you measure the right *population*, and says nothing about whether the *denominator* is a risk set. It was not.

---

## Q3. Was the testing of the adopted proposals sufficient?

**question** What did the testing not cover; is 1-of-6 the weak point?

**verdict** **Yes, 1-of-6 is the weak point** — "0 failures in 1 trial" bounds the per-harness failure rate at ≤0.793, consistent with up to 4.76 of the 6 being broken — but the binomial framing understates the fix's *real* strength and misplaces the risk.

**reasoning** Same closed form, `z²/(n+z²)`:

```
  0 failures in 1 trial -> Wilson 95% upper = 0.793451
  i.e. consistent with up to 4.76 of the 6 repaired harnesses being broken.
  0 failures in 6 trials -> upper = 0.390334  (up to 2.34 of 6)
```

So as an independent-trials argument, running 1 of 6 is near-vacuous. But the 6 are **not independent trials**: you confirmed first that all 6 share one diagnosis (`from pathlib import Path`) and applied one fix. For a common-cause defect with a common-cause fix, one completion run is far more informative than `n=1` implies — it exercises the shared mechanism end-to-end. The residual risk is not "do 5 independent things work" but "does the shared fix interact with per-harness differences", and *that* risk is invisible to both compilation and `--help`.

Concretely, what compilation and `--help` do **not** cover, and why it matters here: `--help` exits inside the guard, before the restore path is ever entered; compilation proves the import parses. The fix was to an *import*, and the thing that import feeds is the mutate-and-restore cycle. Your 1 completion run verified restore by SHA-256 at 7 of 7 mutations RED — that is the right observable, and it is the one the other 5 have no evidence for. Note your own third recorded vacuity case was precisely a *restore* observable reading wrong. The gap is therefore in the highest-risk place, and 5 completion runs are cheap against the claim they support. Run them.

**fix** NONE. This is an assessment of your testing, not a defect in an artefact; inventing a file here would be an addition nothing reaches. The action is to execute the other 5 harnesses to completion with SHA-256 restore verification — the instrument already exists and is already proven on 1 of 6.

**falsifier** Not applicable, and I will say why rather than force one: the proposition is "5 harnesses are untested", which is a fact about what was *run*, not about code state. A differential falsifier needs a defect to toggle, and there is no defect here to toggle — your `--defect-file` arm would be byte-identical to the target and the tool would correctly refuse as vacuous. The arithmetic above is the evidence, and it is re-executable.

**what_would_refute_me** All 5 remaining harnesses running to completion with verified restore. That converts my finding to no-change-needed and moves the bound to 0.390334 — still not tight, but the right 6 of 6.

**disagreement** Your question offers 1-of-6 as the candidate weak point and it is, but you framed it as a *sampling* shortfall. It is really a **coverage** shortfall: the 5 unrun harnesses are not under-sampled, they are untested on the only observable that matters, while being fully tested on two that cannot fail informatively. `--help` exiting cleanly is close to guaranteed once the guard parses, so reporting it for 5 of 6 adds confidence that was never at risk — the same shape as Q2's tightening bound.

---

## Q4. Ledgered advisory line versus refusal

**question** What measurement decides between them?

**verdict** Decidable, and the predicate is cheap — but **this batch is not a data point for it**, and 1 commit could not settle it even if it were.

**reasoning** The hook-evaluable predicate: on every commit, append `{commit_sha, rounds_since_head, honoured: bool}` where `honoured` is true iff `rounds_since_head > 0` *or* the commit was abandoned. That is a mechanical record, needs no judgement, and yields `lapse_rate = lapses / commits`. The decision rule is a comparison of two measured quantities, not a preference: **refusal dominates iff `lapse_rate × cost(unreviewed commit) > block_rate × cost(false block)`**, where `block_rate` is the fraction of commits where the line fires and a round genuinely was not owed. Both terms come out of the same ledger.

The distinguishing outcome is sharp. Advisory-plus-ledger and refusal differ **only** in the cases where the line fires: so ledger a stretch of commits and read the `honoured` column. If `lapse_rate → 0` once the column exists — i.e. being *visible* is what fixed it — advisory suffices and refusal is strictly more surface for no gain. If lapses persist at a visible rate, observation is not sufficient and refusal is the measured answer. cc2's point that "unrecorded report was the defect rather than report itself" is testable exactly here, and that is the right reframing.

What settles it quantitatively:

```
  0 lapses in 1 commit -> Wilson 95% upper on the lapse rate = 0.793451
  prior round measured 7 of 10 lapses = 0.700, which is INSIDE [0, 0.793].
  commits needed, 0 lapses, to push the upper bound below:
    e=0.30  -> 9 commits        e=0.10  -> 35 commits
```

So ~9 ledgered commits distinguish "fixed" from "still lapsing at the prior rate", and ~35 give a usefully tight bound.

**fix** NONE. A ledger is a real addition, but writing one here would be an addition nothing reaches — it needs to be wired into the commit hook and executed by a test, and I have neither the hook's dispatch path measured nor a round's worth of commits to validate it against. Per the additive standard I decline to ship an unreached entry point; this project has done that 11 times. The measurement above is what Q4 asked for.

**what_would_refute_me** A cost asymmetry large enough to swamp the rates — if one unreviewed commit can void an experiment's headline result the way Exp 48's falsifier did, then `cost(unreviewed commit)` is so far above `cost(false block)` that refusal wins at *any* non-zero lapse rate and the ledger measurement is moot. That is a question about the cost terms, and I have not measured them; if the founder can name one voided experiment per unreviewed commit, refuse and stop measuring.

**disagreement** Strongest disagreement in this brief: **"this batch is itself 1 data point" is wrong, and it is wrong in the direction that favours the line.** The line reported and the board was killed — but it was killed by *a human reading the line and choosing to act*, after the preceding round had just measured 7 of 10 lapses and made that lapse salient. That is a data point about human attention under fresh scrutiny, not about the reporting line's efficacy. The advisory condition it would need to test is "the line reports and nobody is primed to care", which is the condition under which all 7 lapses happened and is exactly the condition this batch does not instantiate. Counting it as evidence for advisory is the Hawthorne case, and it is the same error as Q2: a measurement taken in a regime where the failure could not occur.

---

## Termination

**5 passes.** Pass 1 read the predicate and located the unjoined conjunction. Pass 2 executed the counterexample, fixed it, drove the differential. Pass 3 ran the population diff, found my own glob was top-level-only, and redid it recursively over 840 — which is also what reconciled your 839. Pass 4 found the `classify` denominator defect and derived the polling-rate artefact. Pass 5 re-read my own probe fix and found the `else` branch printing "Nothing matched" when processes had matched; fixed. A sixth pass over both fixed files produced no new above-threshold findings.

**Two above-threshold findings, both with delivered fixes and DISCRIMINATING falsifiers:**

| | file | category |
|---|---|---|
| the dash-m proxy never required the insert to carry the file-derived path | `bench/tests/test_help_never_acts_2026-09-11.py` | §10.3 verification-integrity corruption |
| the full-replacement denominator is poll count, not a risk set | `scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py` | §10.3 verification-integrity corruption |

**No composability claim is made.** The two fixes touch unrelated artefacts and there is no measurement showing a composed repair beats either alone, so per the founder's 2026-10-02 definition each stands as the single fix. Reporting that they do not interfere would be the weak form his definition excludes, and I am not reporting it.

**Q1's widening was right to be made and wrong as implemented** — it correctly stopped accusing two correct scripts, and the brief's instinct to distrust it was correct while its diagnosis of *which half* to distrust was not. The judgement you asked me to be explicit about: the wrong widening carries a severity at the critical level on the inherited application scale, but has caused **zero** realised loss in the current tree, and I would not have found it by reading — case `C` only became visible once the arguments of the insert were examined separately from the names beside it.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 24 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_b12_20261123T170728Z) -->

All verification complete. The same 3 pre-existing failures are the sandbox's missing `.git` (the population guard refusing loudly, as designed — identical before and after my change); 13 passed, up from 12 — the +1 is my regression test. Report follows.

---

# SEAT REPORT — batch 12, 2026-11-23

**Sandbox caveat, stated once:** this sandbox stages no `.git`, so `tracked_scripts()` refuses (3 test failures, identical before and after my change — the fail-loud path working) and the brief's git-based populations (837 at HEAD / 839 worktree) are not reproducible here; my population figure is **825 by `scripts/*.py` glob**. Artefact digests at my read matched the dispatch stamps.

---

## Q1 — the widened predicate

**verdict:** The widening is **wrong as shipped** — the file-derived-name rule is a broken dataflow link, and I constructed and dynamically confirmed a source it wrongly credits; the static instrument itself is right, and I have delivered and differential-checked the tightening.

**reasoning:** `_help_calls_unreachable_under_dash_m` (lines 225–233 at dispatch) computes `inserts` and `uses_file` as **two independent `any()` scans over `before`**. Nothing requires the file-derived name to appear in the insert's argument. Constructed counterexample: a `sys.path.insert(0, '/somewhere/else')` (constant — the exact shape `test_a_file_derived_name_is_required_not_just_any_insert` exists to refuse) is credited whenever any *unrelated* preceding statement mentions `__file__` or a derived name — here `print('running from', HERE)`. Both variants (`HERE` decoy, bare `__file__` decoy) return `True` from `answers_help(…, under_dash_m=True)`. Dynamically driven under `python3 -m pkg.attack --help`: **exit 0, usage never printed, ordinary work ran and wrote a file.** The concrete failure the defect permits, named per the brief: a tracked writer of this shape passes the ratchet, and its `--help` under `-m` performs its write — the same class as the 54,480-byte record destruction of 2026-09-11, severity on this project's own scale **material** (§10 categories 1 and 4). Note the P-Pass's 5th discrimination test did not catch this because its constant-insert case *removed* the derived-name assignment entirely, so `derived` was empty — it tested the conjunction's second leg, never the broken coupling between the legs.

On the instrument question: **static is right as the per-run ratchet.** An executing predicate *runs the defect it detects* — my dynamic run wrote a file; over 837 scripts, every broken guard performs its ordinary work, and the docstring records that 15 of 17 runners once billed a live dispatch on an unrecognised argument. "18 s and no approximation" is only true in a throwaway clone, which is per-run machinery and spend-risk the static proxy avoids. The existing division — static ratchet plus one-shot executing validation in a clone — is the simplest sufficient arrangement; the fix is to repair the proxy, not replace the instrument.

**commands_run** (abridged to verdict lines; full outputs above):
```
python3 -m pytest bench/tests/test_help_never_acts_2026-09-11.py -q
  → 3 failed (git-less sandbox, fail-loud), 12 passed   [pre-fix baseline]
python3 - <<EOF  # static attack
  → ATTACK credited under -m rule: True / ATTACK2 credited: True
python3 -m pkg.attack --help   # dynamic, _cli_help beside script, constant insert
  → exit=0, FILE WRITTEN: ordinary work ran under --help
python3 -m pytest …::TestTheDashMProxyDiscriminates … -q   [post-fix]
  → 8 passed
python3 - <<EOF  # population diff, defect vs fixed, 825 scripts
  → verdict changes defect->fixed: 0; offenders 0 both ways
```

**fix:** `bench/tests/test_help_never_acts_2026-09-11.py` — replaced the two independent scans with a single `file_derived_insert` scan requiring `__file__`/a derived name **inside the insert call's arguments**, plus regression test `TestTheDashMProxyDiscriminates::test_a_decoy_derived_name_beside_a_constant_insert_is_refused` (wired: executed by the suite, 13 passed post-fix). Fixed artefact sha256 `9d9945d77cec0e8a…`. 0 verdict changes over all 825 staged scripts — the tightening touches only the decoy class, so the 2 wrongly-accused scripts stay accepted.

**falsifier:** executed via `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py --target bench/tests/test_help_never_acts_2026-09-11.py --defect-file /tmp/defect_copy_test_help.py -- python3 /tmp/q1_falsifier.py` →
```
DEFECT PRESENT  exit=1  FALSIFIED-token=True  -> FAIL
DEFECT ABSENT   exit=0  FALSIFIED-token=False -> PASS
target restored byte-for-byte : True
DISCRIMINATES
```
(The in-tree regression test could not serve as the differential falsifier — swapped to the defect copy it fails by *absence*, the tool's own vacuity case 2 — so the falsifier imports `answers_help` from the target and runs in both arms.)

**what_would_refute_me:** a driven run showing a script of the decoy shape *does* answer `--help` under `-m` (it cannot, unless `_cli_help` is importable from the constant path — in which case construct it with a path that provably isn't); or a tracked script whose verdict my tightening flips from accepted to accused while it dynamically answers `--help` under `-m` (my 0-of-825 diff says none exists today, but the HEAD/worktree git populations contain up to 14 scripts this sandbox does not stage).

**disagreement:** The brief frames the residual risk as "a name assigned from `__file__` somewhere else in the module may have nothing to do with the path being inserted." That is the *smaller* half of the defect. The larger half, which the brief does not name, is that the name needed not be in the insert **at all** — the two conditions were never conjoined on the same node. Also: the brief's "P-PASS DONE, BOTH DIRECTIONS: 5 discrimination tests, 15 passed" overstates coverage — the constant-insert test deleted the derived assignment rather than decoupling it, so the pass exercised the predicate's legs but never their coupling, and the P-Pass was green over a live material defect.

---

## Q2 — 0 of 14, upper bound 0.215311

**verdict:** The figure is arithmetically correct but bears on **neither** claim — this is a wrong-population problem, not a weak-sample problem, so both the corroboration of fable and the cut against B209's premise should be withheld.

**reasoning:** Derived, two routes plus Wolfram: Wilson upper at k=0 is z²/(n+z²) = 3.84146/17.84146 = **0.215311** (statsmodels and mpmath closed form agree to 2.78e-17; Wolfram Language, local Wolfram Engine: 0.21531080273763578). So the interval is sound. But the probe polled beside a **single plain pytest invocation** — pid-set size 1 throughout. B209's premise is churn **between pytest children across guard files during a ~34-minute board**. A stable pid within one invocation is what *both* hypotheses predict for this regime; the probe's own docstring says so ("a short run is not a commit board"). Even n → ∞ in this regime decides nothing about the board regime. Therefore: (a) "corroborates fable" — withhold; fable's claim concerns the board. (b) "cuts against B209's premise" — withhold, and this one is actively wrong as stated: a single pid during one pytest run is fully consistent with per-guard-file replacement during a board, because no guard-file boundary with a child swap was spanned. **The sample that settles it:** run `does_the_matched_set_ever_fully_replace_2026-11-23.py` for the full duration of a real commit board (~34 min at 2 s intervals ≈ 1020 polls spanning every guard-file boundary). Derived thresholds: 0 full replacements in **≥ 73** pairs bounds the rate below 0.05; in **≥ 381** pairs below 0.01; a board-length run exceeds both. One observed full replacement promotes the scenario to demonstrated and the question of weight is over.

**commands_run:**
```
python3 - <<EOF (statsmodels + mpmath)
  → [0.000000, 0.215311]; closed form agrees to 2.78e-17
  → exclude 0.05 needs n>=73; exclude 0.01 needs n>=381
wolframscript -code 'z = Quantile[NormalDistribution[], 0.975]; N[z^2/(14 + z^2), 10]'
  → 0.21531080273763578   [Wolfram Language attribution]
```

**fix:** NONE — the deliverable is the decision procedure above; the measuring instrument already exists in-tree and needs only to be run against a real board, which this sandbox cannot host.

**falsifier:** the arithmetic was differentially self-checking (two independent routes agreeing to 2.78e-17, third route Wolfram); the regime-mismatch argument is logical, not executable here, and I say so rather than fake a run.

**what_would_refute_me:** a board-length probe trace showing poll pairs that *did* span pytest-child replacements (e.g. pid-set sizes > 1 or non-identical pairs) — that would convert the 0-count into genuine evidence against realisability and my "wrong population" claim collapses; conversely a trace showing the board runs one pytest for all guard files refutes B209's premise directly and my withholding of (b) was too cautious.

**disagreement:** The brief reports the probe "AS CORROBORATING fable AND AS CUTTING AGAINST B209's OWN PREMISE." Both reports exceed the data, and the second is the worse overreach: absence of churn in a regime with no churn opportunity is not evidence about churn. The script's own printed interpretation (lines 128–137) makes the same overclaim and should be softened to name the regime.

---

## Q3 — was the adoption testing sufficient?

**verdict:** Sufficient for the help-flag property (measured on all 6) and the differential rule (validated both ways); **insufficient for the run-to-completion property, and the weak point is not the 1-of-6 sample but the extrapolation of a per-file behavioural claim from it.**

**reasoning:** "Compiles and answers `--help` writing 0 bytes" and "runs to completion with all mutations RED and SHA-256-verified restore" are different predicates, and this repository's own record proves the gap: `a_falsifier_must_disagree_with_itself_2026-11-23.py` lines 20–23 record a mutation harness in this very session that compiled, was invoked — and exited at `REFUSED: the guard is RED before any mutation`, a startup refusal that compile + `--help` cannot see, caused by a file the author was not looking at. The repair touches exactly the header region (imports/guard) where a path or ordering slip produces that failure mode. The 5 unexecuted harnesses therefore carry an evidenced, nameable risk: silent inability to run, discovered only when next needed. Cost to close: 5 clone runs, bounded and known. Alternatively, state the adopted claim honestly as "1 of 6 verified to completion" and close the other 5 on first scheduled use. What the differential-rule testing did NOT cover: its two validations (discriminates on real guard, vacuous on unrelated guard) exercise verdicts 0 and 1 but not the **inverted-sense arm** (defect-present PASS / defect-absent FAIL, lines 154–156) — no known-answer test ever drove it.

**commands_run:** the record cited was read in-tree (`Read scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py`); the 6 repaired harnesses are not identifiable in this sandbox (fixer report not staged — `grep` for the fixer and declined-file list returned no report), so I could not run the missing 5 here and say so rather than simulate it.

**fix:** NONE deliverable here — the fix is an action: run the remaining 5 repaired harnesses to completion in a throwaway clone before the run-to-completion claim is recorded for 6.

**falsifier:** for the future action, the in-tree differential tool itself is the falsifier (each harness run with one mutation un-reverted must go RED); not executable in this sandbox absent the 6 filenames.

**what_would_refute_me:** the fixer's report naming the 6 files plus 5 clean completion runs — that would show the extrapolation happened to be safe (it would not show it was *justified*, which is the finding); or evidence that the repair transform provably cannot alter pre-mutation startup (e.g. it only inserts statements inside the `__main__` guard after all preconditions), which would reduce the residual risk below material.

**disagreement:** The brief asks "is the 1-of-6 sample the weak point?" — framing it as a sample-size question invites the answer "run more." The defect is categorical, not statistical: run-to-completion was *claimed for the batch* while *measured for one member*. 6 of 6 at one property and 1 of 6 at another were reported in a single breath, and the brief's own sentence structure ("a repaired harness RAN TO COMPLETION") elides the quantifier.

---

## Q4 — ledgered advisory line vs refusal

**verdict:** The deciding measurement exists and is cheap: ledger the existing advisory line's verdict-and-outcome per significant commit, and escalate to refusal on the first recorded lapse; **0 lapses in 9 ledgered significant commits is the stopping rule that vindicates the advisory**, because its Wilson interval then excludes the measured baseline regime.

**reasoning:** The predicate a hook can evaluate is already implemented — `hooks/pre-commit` asks `was_this_batch_reviewed_2026-11-22.py` (`panel_rounds_since_HEAD == 0`, with `what_is_a_significant_batch_2026-11-23.py` scoping significance). The missing piece is one append per commit: `(commit_id, rounds_since_prev, significant?, proceeded?)`. Define a **lapse** = line reported 0 rounds on a significant commit ∧ commit proceeded ∧ no round completed before the next commit. Derived decision rule, all intervals computed above: baseline (unledgered advisory) is **7/10 lapses, Wilson [0.397, 0.892]**. A ledgered-advisory run of **0 lapses in 9** gives Wilson [0, 0.299] — **disjoint from the baseline interval**, so the ledgered advisory demonstrably dominates the unledgered one on the named property (lapse rate) and refusal's cost (blocked legitimate commits, also visible in the same ledger) is unjustified under the simplest-sufficient standard. **Any lapse ≥ 1 in the window → adopt refusal**, the escalation the hook's own comment pre-commits to. This batch's data point (reported → board killed) is 0/1, Wilson [0, 0.794] — consistent with everything, decides nothing, and I verified that rather than assuming it.

**commands_run:**
```
python3 - <<EOF (statsmodels)
  → baseline 7/10: [0.3968, 0.8922]; candidate 0/9: [0.0000, 0.2991]; disjoint: True
  → this batch 0/1: [0.0000, 0.7935] (uninformative)
```

**fix:** NONE delivered — deliberately. The ledger append belongs in `hooks/pre-commit`, which cannot execute in this git-less sandbox, so an implementation here would be an addition no test can reach — the exact 11-times-measured defect class the additive standard names. The specification above is complete enough to implement and test where a `.git` exists.

**falsifier:** for the eventual implementation: commit twice in a throwaway clone with 0 panel rounds; the ledger must gain 2 lapse rows (defect-absent arm: commit after a recorded round → 0 lapse rows). Not executable here; stated per the one-shot rule.

**what_would_refute_me:** evidence that the 7/10 baseline commits were predominantly *insignificant* batches (the baseline would then overstate the lapse rate the ledger must beat, and the 0-in-9 threshold would be miscalibrated — recompute against the significant-only baseline); or a founder ruling that any single lapse of this class is intolerable regardless of rate, which collapses the measurement into immediate refusal.

**disagreement:** The brief offers this batch as "1 data point: the line reported, and the board was killed." As computed, 0/1 carries an upper bound of 0.794 — it is consistent with a regime that lapses four times in five. Citing it as support for the auditability framing is the same shape of overclaim as Q2's: a count too small to exclude anything, narrated as if it leaned somewhere.

---

## TERMINATION

**3 passes run.** Pass 1: read artefacts, reproduce baseline, construct and dynamically confirm the Q1 counterexample. Pass 2: fix, regression test, differential vacuity check, 825-script verdict diff, Q2/Q4 derivations with second and third routes. Pass 3: full-file re-run (13 passed, same 3 sandbox-only failures as baseline), re-read of the patched region, Q3 gap check against the in-tree record — **no new above-threshold findings**. Converged under §10: the one material defect found (Q1 decoupled conjunction, categories 1/4) is fixed, tested, and differential-verified; every residual finding is below threshold or handed over with its deciding measurement named.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_b12_20261123T170728Z/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
