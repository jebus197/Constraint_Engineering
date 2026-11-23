# Panel Round, Batches 2 and 3, Joint Review of the Autonomy Work

Record written 2026-11-23T00:25:59+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. Batches 2 and 3 of the autonomy run, landed as commits
ca0320ba and 7dd07521. The brief put 5 questions to the 2 free seats: whether
the recording-only supervisor pass is the instance's to run or the founder's;
whether a timeout mark should be read from source or from the collected test;
an asymmetry by which the supervisor asks for LESS corroboration on the path
that acts; whether a hash-chain majority is a finding or an artefact of a
bigger denominator; and what the cy gate's anti-trap refusal budget should be
keyed to, which is entry B209.

WHY A PANEL AT ALL. The founder's standing instruction of 2026-11-21 is that
every batch goes to a free panel and that any fix the panel proposes is TESTED
before adoption, because a panel verdict is a hypothesis and not a fix. Both
seats ride the Max subscription, so the round cost nothing; PANEL_ONLY was left
unset so no paid seat was reachable.

WHAT THE SEATS DID. 2 of 2 responded. cc2 ran 953.1 seconds across 64 tool
calls and 3 passes; fable ran 1123.4 seconds across 38 tool calls. Round wall
clock was 1143.4 seconds with 190.3 seconds of idle, which is 0.0832 of
available seat time. Both verified the brief's declared artefact hashes before
answering. Seats proposed edits to 25 files inside their own sandbox copies;
those edits are preserved in seat_proposals.diff and were NOT applied.

THE DISAGREEMENT, PRESERVED RATHER THAN SMOOTHED. On the supervisor authority
question cc2 held that the recording-only row is the instance's to run but that
the stated reason was wrong, because it found the recorded verdict can itself be
false; fable held that the specific reservation of 2026-11-08 is not clearly
superseded by the general handover of 2026-11-21 and that the authority question
should be closed by a confirmation rather than by inference. Both positions are
recorded. On entry B209 cc2 rejected all 3 candidates in the brief and proposed
a set-overlap epoch, scoring it 6 of 6 against 4 of 6 for the brief's preferred
candidate; fable implemented the brief's candidate with an observation-based
reset.

WHAT WAS DONE WITH THE FINDINGS. The orchestrator reproduced cc2's scoring
table independently, then ran the test neither seat ran: driving FABLE'S OWN
implemented hook through cc2's disputed scenario, in which 1 activity ends and
another begins with no empty observation between them. The first activity
exhausts the budget at 61 and the second opens at 62, so a genuinely live run
is left unprotected. cc2's objection is therefore confirmed against the real
code and not only against a model of it. Driving cc2's hook through the same
scenario returns 1, and through the brief's own predicted mid-run-gap falsifier
returns a clean climb. The set-overlap repair is the better evidenced of the 2.

NEITHER REPAIR IS ADOPTED YET. The change alters when a gate refuses, and cc2
documented 2 residual failure modes of its own candidate in the code it wrote:
a process set replaced with no overlap at all, and genuinely separate
activities that happen to overlap. Adoption with tests for those 2 modes is
sequenced as the next batch.

2 CORRECTIONS THE PANEL MADE TO THE BRIEF ITSELF. cc2 established that the
commit board makes exactly 1 pytest invocation, so the brief's account of the
churn as a child replaced per guard file is wrong: the churn comes from nested pytest children instead. It further observed that the brief's own test
fixture encoded a constant parent with a moving member, contradicting the
brief's prose. Both seats independently found that the timeout-mark defect the
brief described was already repaired in the dispatched tree, so that question
was moot. cc2 also corrected its own scoring harness twice against its own
interest and left both corrections documented in the file, noting that the
uncorrected run had flattered its own candidate.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — batches 2 and 3, v4, 2026-11-22

Supersedes `panel_brief_batch2_v3_2026-11-22.md`, which was REFUSED by
`scripts/panel_brief_validate.py` on 5 required checks and was therefore never
dispatched. Its 4 questions are carried below unchanged in substance; what was
missing was the template's own required sections, not the questions. A 5th
question is added for batch 3.

**WHY 5 AND NOT 14.** Batches 2 and 3 hold 14 items between them. 9 are
mechanical and are reported, not asked about: register a source-text assertion
in a manifest, wire 2 scripts to a caller, close a ticket whose evidence
directory exists, update 2 stale figures, raise 3 entries. The v2 brief's own
principle governs -- a brief naming 22 repairs gets 22 shallow answers.


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `scripts/panel_brief_validate.py` | `ca73f33a69d386c0` | 57573 | 2026-11-13T03:04:45+00:00 |
| `bench/tests/test_the_nested_suite_stays_bounded_2026-10-28.py` | `18ada600845f1927` | 13061 | 2026-11-22T08:19:14+00:00 |
| `hooks/cy_monitor_gate.py` | `19ed3464616bb89d` | 21719 | 2026-11-22T16:45:44+00:00 |
| `bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py` | `c3efa4352214b0e1` | 12610 | 2026-11-22T22:36:45+00:00 |
| `scripts/the_cy_refusal_budget_never_binds_2026-11-22.py` | `3edb281010da0b97` | 7463 | 2026-11-22T18:53:44+00:00 |
| `scripts/is_the_hash_chain_majority_real_2026-11-22.py` | `3dfb3813e43ea0cc` | 7407 | 2026-11-22T15:47:05+00:00 |

## CONTEXT THE PANEL NEEDS

The founder handed the work up to the bounded orchestrator run to this instance
on 2026-11-21, reserving himself for 4 categories only: computationally
irreducible, safety, legal or ethical, and a fundamental change in how CDSFL
works as a whole. He instructed that every batch go to a free panel and that any
fix the panel proposes be TESTED before adoption. **A panel verdict is a
hypothesis, not a fix.**

Batch 2 landed as commit `ca0320ba`. Batch 3 is on the board as this brief is
written. Both are reviewed AFTER landing, as batch 1 was; what must precede
adoption is any fix the panel itself proposes.

## USE THE HARNESS — form the answer by RUNNING things, not by describing them

Every seat must reach its answer using whatever parts of the machinery currently
work, and must report what it ran. Naming the instruments that bear on these
questions:

- **The two-sided gate** bears directly on Q5. The gate requires BOTH a
  flattened decay curve (`gamma_critical >= 0.30`) AND K consecutive zero-new
  rounds. Q5 concerns a DIFFERENT counter -- the cy gate's refusal budget -- and
  the question worth running is whether the two-sided form is the right shape
  for it: a budget keyed to a quantity that can reset is the single-sided
  failure the two-sided gate exists to avoid.
- **`gamma`** bears on Q3 and Q5 as the project's own diminishing-returns
  measure: if a supervisor or a gate can be driven indefinitely without its
  state advancing, gamma over that loop is undefined rather than flat, and an
  undefined gamma is the signature of a counter that is not counting.
- **The severity model** bears on Q3: state what severity the asymmetry would
  carry if the concrete failure it permits can be named, and say explicitly if
  it cannot be named, because an unnameable failure is not a finding.
- **`rho`** bears on Q4, where the question is whether 2 proportions measured at
  different n are distinguishable at all.

A seat that returns prose about a fix without having run anything has not
answered.

---
## Q1. IS THE RECORDING-ONLY SUPERVISOR PASS MINE TO RUN, OR HIS?

**THE CALL I MADE.** The orchestrator's supervisor has a 3-valued setting. The
middle row -- `--hil-review` on, `--act` WITHHELD -- classifies what happened and
writes the verdict down, re-invoking nothing. I judged that mine to run, and the
acting row (`--act`) his.

**THE REASONING.** Against his 4 reserved categories the middle row scores 0 of
4: not computationally irreducible; spends no money (simulated seats, paid
dispatch refused at the transport layer); takes no actions; changes nothing about
how CDSFL works. Verified by execution: with `act=False`, `drive()` invokes the
launch exactly once, sets `acted` False, and breaks after 1 iteration whatever
the verdict.

**WHAT CUTS AGAINST IT.** A task-list sentence of 2026-11-08 says "This does NOT
say either switch should be flipped; that remains his." I treated his 2026-11-21
handover as superseding it in scope. That is a judgement about which instruction
governs, and I may have it wrong.

**WHAT WOULD SHOW I AM WRONG.** An argument that RECORDING a verdict is itself a
behaviour change, or that the 2026-11-08 sentence is specific enough to survive a
later general handover. Prediction P2 of the pre-registration fails the instant
any action is taken, so the mechanical half is already guarded; the question is
the judgement, not the mechanism.

---

## Q2. HOW SHOULD A CHECKER READ A TIMEOUT MARK -- FROM THE SOURCE OR FROM THE
##     COLLECTED TEST?

**THE DEFECT.** `test_the_nested_suite_stays_bounded_2026-10-28.py` asserts that
the gate-cost module carries a timeout mark with a value, and reports `assert []`.
The mark EXISTS: `@pytest.mark.timeout(BOARD_BUDGET_SECONDS + 60)`. Executed
against the real file: 0 marks with a literal value, 1 with a computed value, a
`BinOp`. The checker accepts only `ast.Constant`.

**THE IRONY THAT MATTERS.** That checker's own docstring says it was "CONVERTED
FROM A SOURCE-TEXT ASSERTION" to obey `execute-do-not-grep`, and claims "The mark
is now read off the collected function". It is not: it parses source and matches
literals.

**MY PROPOSAL.** Read the mark off the COLLECTED item --
`item.get_closest_marker("timeout").args[0]` -- so a computed bound arrives as
the number it evaluates to.

**THE ALTERNATIVE I REJECTED, AND WHY THE PANEL SHOULD TEST THAT REJECTION.**
Teaching the AST walk to accept a `BinOp` is smaller and fixes this instance.
I rejected it because the next form -- a name, a call, a conditional -- stays
equally invisible. **But my proposal requires collection**, which costs more than
a parse and may not be available where this check runs. If collection is not
reachable there, my preferred fix is unbuildable and the narrow one is right.

---

## Q3. THE SUPERVISOR ASKS FOR LESS CORROBORATION ON THE PATH THAT ACTS

**THE FINDING, derived by enumerating all 28 states of exit code and pulse.**
HOLD 22, DONE 4, RESUME 2. RESUME requires exit 42 AND a pulse naming a process
that has exited.

**THE ASYMMETRY.** At exit 0, a pulse that does NOT say `ended` gives HOLD -- "the
run exited cleanly but its watch never recorded it". At exit 42 the same missing
`ended` gives RESUME anyway; the flag is not consulted on that path.

**SO THE ONE PATH THAT TAKES AN ACTION ASKS FOR LESS CORROBORATION THAN THE PATH
THAT DOES NOTHING.**

**THE DEFENSIBLE READING** is that exit 42 is an explicit pause signal from the
run itself, so the watch adds little. **I did not repair it**, because changing
when the supervisor acts is the founder's category.

**THE QUESTION FOR THE PANEL:** is the defensible reading right, or is this a
real hole that should be closed before `--act` is ever considered? Name the
concrete failure the asymmetry would permit, or say there is none.

---

## Q4. IS "THE HASH CHAIN NOW COVERS A MAJORITY" A FINDING, OR AN ARTEFACT OF A
##     BIGGER DENOMINATOR?

**THE MEASUREMENT.** 160 valid of 266 = 0.601504, Wilson [0.541626, 0.658492],
Clopper-Pearson [0.539926, 0.660794], 2 routes agreeing to max abs diff 0.000e+00 (Wilson) and max abs diff
1.110e-16 (Clopper-Pearson).
The interval clears 0.5, so a guard pinning "indistinguishable from half" goes
red and A1 needs restating.

**THE PART I REFUSED TO CLAIM.** Against 2026-11-06's 125 of 231 = 0.541126:
Fisher exact p = 2.030093e-01, Yates chi-square p = 2.053340e-01. The 2
measurements are NOT distinguishable. So I wrote that coverage is above half and
explicitly NOT that it rose.

**THE QUESTION:** is that the right restatement? A reading I can see and reject
is that the correct statement is weaker still -- that nothing has been shown to
change at all, and the guard should be restated to pin the straddle at a larger
n rather than to assert a majority. **Say which, and why.**

---

---

## Q5. B209 -- WHAT SHOULD AN ANTI-TRAP REFUSAL BUDGET BE KEYED TO?

**THE DEFECT, OBSERVED AND DRIVEN.** `hooks/cy_monitor_gate.py` refuses a
session's attempt to go idle while a long run is in progress, and carries
`MAX_REFUSALS = 60` as an ANTI-TRAP safeguard: on exhaustion it prints that it
is allowing the stop so a session cannot be trapped. `spend()` zeroes the count
whenever its key changes, and `main()` builds that key as the session id plus
the sorted watched-run directories OR, when there are none, the live process
ids. A commit board replaces its pytest child per guard file, so for an
UNWATCHED run the key churns, the counter resets, and 60 is never reached.

Driven against the real hook with its state file redirected to a temporary path:
a steady directory key returns 1, 2, 3, 4, 5 across 5 polls; a churning pid key
returns 1 every time, and still stands at 1 after 120 refusals.

**SO THE SAFEGUARD IS INERT FOR PRECISELY THE RUNS THE GATE CANNOT READ**, which
is the only case in which a session could be trapped. A watched run has a stable
key and does not need the protection.

**I DELIBERATELY DID NOT REPAIR IT.** It changes WHEN a gate refuses, so it goes
to the panel first. The producer and the guard are committed; the fix is not.

**FIRST, A CORRECTION TO MY OWN FRAMING, MADE BEFORE DISPATCH.** I recorded
candidate (a) as measured defective because 2 concurrent runs would share a
budget and the first would exhaust it for the second. **That reason assumes the
budget is PER RUN, and the gate's own message says it exists so A SESSION cannot
be trapped.** On a session-level purpose, sharing is correct behaviour, not a
fault: if the session has been refused 60 times it must be allowed to stop, and
which of several overlapping runs caused them is irrelevant. So my recorded
objection was a category error about the REQUIREMENT, not a finding about the
code. (a) is still defective, for a different reason given below. I state this
rather than quietly repairing it because the brief you are reading is the
artefact that would otherwise have carried my error into your answer.

**THE 3 CONDITIONS A KEY MUST MEET.**
1. STABLE across repeated polls of the same ongoing activity, or the counter
   cannot climb. This is what the churning pid list breaks, and it is B209.
2. DISTINCT enough that a budget exhausted long ago does not silence the gate
   for ever afterwards. Note this is WEAKER than "distinct per run".
3. COMPUTABLE WITHOUT READING THE RUN, since the unwatched case is the only one
   that needs protecting.

**THE CANDIDATES, SCORED.**
(a) Session id alone. Meets 1 and 3; FAILS 2 -- it never resets, so the 61st
refusal of the whole session is permanently allowed and the gate stops working
for the rest of that session however long it lives.
(b) Long-lived process ancestors rather than churning children. Meets 1 and 3;
meets 2 only if the chosen ancestor is not shared by every run in the session.
If it resolves to the session's own shell it degenerates silently into (a).
(c) A CONTIGUOUS-ACTIVITY EPOCH -- a counter advancing only when the live-run
set goes empty and then non-empty again. Meets 1, 2 and 3, and needs only the
emptiness of the set, which the gate already computes to decide whether to
refuse at all. I found this by asking what the budget is FOR rather than which
keys were available, and it is untested.

**A 4TH OPTION IS WITHDRAWN RATHER THAN OFFERED**: session id plus a coarse
time bucket converts a TOTAL into a RATE, so refusals resume every bucket and
the session CAN be refused for ever -- self-defeating against the stated
purpose.

**THE QUESTION, AND THE LOAD-BEARING PART IS CONDITION 2.** Which key, or a
candidate I have not seen? Attack condition 2 specifically: is "distinct per
contiguous busy period" the right weakening of "distinct per run"? That
judgement is mine and nothing measures it. For (c), the falsifier I most expect
to bite is a live-run set that momentarily EMPTIES during a single run -- a gap
between a board's cheap checks and its pytest -- because (c) would then reset
mid-run and reintroduce B209 in a slower form. That is testable against the
real board's process history. State the concrete failure your choice permits.

**★ 3 THINGS FOUND BY EXECUTION AFTER THIS QUESTION WAS FIRST DRAFTED. They
change what a repair must do, so they are added rather than left for you to
rediscover.**

**(i) THE CHURN IS SIMULTANEOUSLY THE DEFECT AND THE SAFEGUARD'S ONLY RESET
PATH.** Driven against the real hook with `CDSFL_CY_STATE` redirected to a
temporary path: `spend("sess|K1")` x 61 reaches n = 61, then `spend("sess|K2")`
returns n = 1. So condition 2 HOLDS TODAY -- and it holds BY MEANS OF the key
changing, which is the behaviour that breaks condition 1. `spend`'s only reset
is `if st.get("key") != key`; nothing else in it ever lowers the count.
**THEREFORE A REPAIR MUST SUPPLY A NEW RESET PATH, NOT MERELY STABILISE THE
KEY.** Candidate (a) does 1 of those 2 jobs and destroys the other, which is a
sharper objection than the one stated above.

**(ii) MY OWN REGRESSION GUARD CANNOT JUDGE THESE CANDIDATES, AND ITS DOCSTRING
CLAIMS IT CAN.** `bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py`
says it asserts the property and not the mechanism, "so whichever of B209's 2
options is taken, this file judges it". Traced against the 3 conditions, ALL 5
of its tests assert condition 1. Conditions 2 and 3 are asserted by nothing.
Measured: under candidate (a) a constant key gives [1, 2, 3, 4, 5] over its
first 5 calls and [63, 64, 65] over its last 3 of 65, so BOTH strict `xfail`
cases turn green, the markers come off, and the file reports a successful
repair while the session is silenced permanently after the 61st refusal. **2
tests are owed and are drafted: one driving K1 past the budget then presenting
a new period (passes today, goes RED under (a)), and one for condition 3 that
CANNOT BE WRITTEN until `refusal_key()` is extracted from `main()` -- the key
is assembled inline at `hooks/cy_monitor_gate.py:415`, so there is nothing a
test can call. That extraction is part of the repair, not a tidy-up.**

**(iii) A SECOND CONSEQUENCE THE ENTRY DOES NOT RECORD: AN UNBOUNDED TOKEN
COST.** Every refused stop re-injects the same context, measured at 4249
characters or about 1062 tokens. The declared budget of 60 is what would CAP
that cost; with the counter resetting, the refusal count is governed by the
run's DURATION instead, so the cost has no upper bound. Observed during this
batch's board: 7 refusals printing [1, 1, 2, 3, 1, 1, 1], peak 3, where a
working counter reads 7. **This matters because the entry's severity note says
the trap is conditional on an IDLE session and that a busy session "never
notices". That is true of the trap and FALSE of the cost**, which is paid on
every refusal, so it lands in exactly the common case the entry dismisses.

**(iv) THE STATE IS A SINGLE SLOT**, `{"key": ..., "n": ...}`, so a PER-RUN
budget is impossible against this interface by construction. The interface
itself says the budget is session-level.

**AND A SECOND DEFECT FOUND WHILE WRITING THIS BRIEF, WHICH IS NOT RHETORICAL.**
This brief cannot DECLARE B209's figures for re-execution, because the
validator refuses a declared figure whose producer exits non-zero, and this
producer exits 1 BY DESIGN to signal that the defect is still live. So 2 of my
own mechanisms are in direct conflict: a producer that reports a live defect
through its exit code is uncitable in the one artefact that instructs the panel.
The B209 figures above are therefore stated in prose with their producer named
-- `scripts/the_cy_refusal_budget_never_binds_2026-11-22.py`, exit 1 on the live
defect, 0 once repaired, 2 if the watched arm turns out broken too -- and the
seat should re-run it rather than trust them. **Is the right repair to let the
validator accept a declared non-zero exit when the brief states the expected
code, or to make producers signal liveness in their OUTPUT rather than their
exit status? Name which, and what it would break.**

---

## PRODUCE A FIX, AND TEST IT

A finding without a fix is incomplete. **A fix without a runnable falsifier the
seat has EXECUTED is a hypothesis, not a fix.** Report the exact command run and
the output seen; do not paraphrase the output.

**Deliver your fix as a file.** Write it INTO the sandbox repository tree at its
real path. A fix described in prose is not delivered, and a fix written to
scratch space is destroyed when the sandbox is torn down: rounds 5 and 6 on
2026-09-10 returned 0 source files for exactly that reason while both seats
reported writing and running working code.

**Where more than 1 repair is in play -- which is the case in Q5 and in the
second defect under it -- composability is a CLAIM THAT REQUIRES A MEASUREMENT.**
The founder's definition of 2026-10-02: compose only on a DEMONSTRATED advantage
over each fix alone, where the demonstration is a measurement and not a
judgement, and prefer the single fix wherever it performs as well. Reporting
merely that 2 repairs do not interfere is the weak form his definition
explicitly excludes, and will not be accepted as an answer.

## WHAT WOULD REFUTE YOU

Before you conclude on any question, state what evidence would overturn your own
answer. A verdict with no stated refutation condition is an opinion, and will be
recorded as one. Where you believe a question is not decidable on the available
evidence, say so and say what measurement would decide it.

## OUTPUT SHAPE — what to return, field by field

Return these fields for each of Q1 to Q5, so replies can be compared without a
parser guessing:

1. `question` -- Q1 to Q5.
2. `verdict` -- your position, in 1 sentence.
3. `reasoning` -- the derivation, naming which instrument you ran.
4. `commands_run` -- the exact commands, and their output verbatim.
5. `fix` -- the repository-relative path of the file you wrote, or NONE.
6. `falsifier` -- the runnable check, and the result of EXECUTING it.
7. `what_would_refute_me` -- the evidence that would overturn your answer.
8. `disagreement` -- your strongest disagreement with this brief's own framing,
   including with any figure in it. This field is mandatory and may not be
   empty; if you agree with the framing entirely, say what the framing omits.

**Do not converge.** Disagreement between seats is information and is preserved
rather than smoothed to consensus. Anything proposed here will be TESTED before
adoption.

## TERMINATION

Stop when a further pass produces no new above-threshold findings -- diminishing
returns is this project's own criterion -- and state how many passes you ran. A
finding is above threshold if missing it could cause a real-world failure, an
unsafe condition, or a wrong decision by the founder. Do not generate findings
to fill the output.

<!-- figure: hash chain live share | scripts/is_the_hash_chain_majority_real_2026-11-22.py | 160 of 266 = 0.601504 -->
<!-- figure: hash chain Wilson | scripts/is_the_hash_chain_majority_real_2026-11-22.py | [0.541626, 0.658492] -->
<!-- figure: hash chain Clopper-Pearson | scripts/is_the_hash_chain_majority_real_2026-11-22.py | [0.539926, 0.660794] -->
<!-- figure: hash chain prior observation | scripts/is_the_hash_chain_majority_real_2026-11-22.py | 125 of 231 = 0.541126 -->
<!-- figure: hash chain Fisher | scripts/is_the_hash_chain_majority_real_2026-11-22.py | p = 2.030093e-01 -->
<!-- figure: hash chain Yates | scripts/is_the_hash_chain_majority_real_2026-11-22.py | p = 2.053340e-01 -->
<!-- figure: hash chain Wilson route agreement | scripts/is_the_hash_chain_majority_real_2026-11-22.py | max abs diff 0.000e+00 -->
<!-- figure: hash chain C-P route agreement | scripts/is_the_hash_chain_majority_real_2026-11-22.py | max abs diff 1.110e-16 -->


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 64 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_batches23_20261122T223441Z) -->

Three passes complete; all instruments green and falsified in both directions. Writing up.

---

# Seat reply — batches 2 & 3, v4

**Passes run: 3.** (1) read + re-execute both named producers; (2) build fixes and score candidates; (3) falsify each fix in *both* directions and check for regressions. Pass 3 produced two findings that changed pass-2 conclusions, so I did not stop at 2. A 4th pass produced no new above-threshold findings.

**Headline: two of this brief's five premises are stale against the artefacts it stamped.** Q2's defect does not exist in the dispatched file, and Q5(ii)'s "owed and drafted" tests are present. Both verified against the matching sha256.

---

## Q1 — recording-only supervisor pass

- **verdict** — The middle row is yours to run, but your stated reason is wrong: recording is *not* consequence-free, because I found the recorded verdict can be false. The row stays yours; the obligation is to fix the record, not withhold the row.
- **reasoning** — Your 0-of-4 scoring treats "writes a verdict down" as inert. I ran `classify()` over the state space and found it emits `RESUME` with the reason *"its process has exited, so a resume cannot collide with a live run"* on a pulse **4000 s stale** — a claim about a process never established to belong to that run. Under `--hil-review` with `--act` withheld, that false sentence is exactly what a human reads to decide whether to flip `--act`. So the middle row's output is load-bearing on the acting decision. That is an epistemic consequence, not an actuating one, which is why it remains yours — but it means the 2026-11-08 sentence was guarding something real, just not the thing it named.
- **commands_run** — `python3 -m pytest bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py -q` → `test_without_act_nothing_is_reinvoked` asserts `len(calls) == 1 and res["resumes_driven"] == 0`; it passes. Your mechanical half is guarded. Full table under Q3.
- **fix** — NONE for Q1 itself; the Q3 fix is what makes the recording-only row safe to run.
- **falsifier** — Executed: `A.drive(..., act=False, _runner=...)` records one launch, zero resumes. Confirms no action on the middle row.
- **what_would_refute_me** — A demonstration that no human reads the recorded reason before flipping `--act` (e.g. the decision is taken from `decision` alone and the reason string is never surfaced). Then recording really is inert and your 0-of-4 holds unmodified.
- **disagreement** — "Spends no money, takes no actions, changes nothing" is the wrong test for a *recording* mechanism. The question for a recorder is whether its record can be wrong in a direction that biases the next decision. It could, and I fixed that.

## Q2 — timeout mark from source or collected test

- **verdict** — The question is moot: the dispatched file already reads the mark off the imported object and **passes**. Neither your proposal nor the AST-widening you rejected is needed, and the collection-cost objection you raised against yourself dissolves.
- **reasoning** — `sha256sum` matches your stamp `18ada600845f1927` exactly, so this is the file you dispatched. Lines 125–162 import the module via `importlib`, walk `dir()` descending into classes, and read `_mk.args[0]` off `pytestmark`. There is no `ast.Constant` filter on this path. Critically, this is **import**, not pytest **collection** — which is the third option your framing missed, and it is why your "my proposal requires collection, which may not be available where this check runs" worry does not bite. `pytestmark` is set by the decorator at import time.
- **commands_run**
  ```
  $ python3 -m pytest "bench/tests/test_the_nested_suite_stays_bounded_2026-10-28.py::test_the_long_nested_test_raises_its_own_limit_rather_than_the_global_one" -p no:randomly -q
  .                                                                        [100%]
  1 passed in 0.22s
  ```
- **fix** — NONE. Writing one would be an addition nothing reaches.
- **falsifier** — The test is its own falsifier and it ran clean in 0.22 s. `assert marks` does not fire, so `marks` is non-empty — the opposite of the `assert []` you report.
- **what_would_refute_me** — A `CDSFL_*` env var or conftest that routes this check through a different code path in the real board, where the AST version still runs. I did not find one, but I did not exhaustively search conftest chains.
- **disagreement** — The brief asserts a *current* failing observation (`reports assert []`) against a file whose digest it also publishes, and the two contradict each other. The dispatch-stamp table is doing real work here: it let me prove the staleness rather than guess at it. Whatever produced `assert []` was an earlier revision; the brief's Q2 should be withdrawn, not answered.

## Q3 — supervisor asks less corroboration on the acting path

- **verdict** — Your defensible reading is right about `ended` and wrong about the pulse overall: `ended` may properly be ignored at exit 42, but the pulse's **freshness** may not be, and ignoring it is a real hole in the acting path. Concrete failure named below. Fixed.
- **reasoning** — I enumerated the table by executing `classify()`, not by reading it. Your asymmetry reproduces. But the larger finding is that `PULSE_STALE_SECONDS = 180` is declared at line 153 and **consulted by no decision** — `age` is computed into the evidence dict and nowhere else. That is precisely the additive-standard failure class (an addition nothing reaches; 11 confirmed instances since 2026-08-01), sitting on the one path that acts.
  **The concrete failure, as asked.** An abandoned `cy_pulse.json` from an earlier run names a pid that is now dead. `_pid_alive` returns `False`. The current run exits 42. `classify` returns `RESUME` on liveness evidence belonging to a *different run*, asserting a resume "cannot collide with a live run" — while this run's process may still be alive. Under `--act` that re-invokes the launch into a live run's log directory. The sibling module already defends this exact shape: `hooks/cy_monitor_gate.py` carries `MAX_PULSE_AGE_HOURS = 36` so "an abandoned pulse file from a crashed machine cannot refuse stops for ever". The actuator had no equivalent.
  **Severity.** My domain declares no scale of its own, so per the ordinal-severity rules I inherit the application scale: this is a wrong-result-plus-unreproducibility defect, conditional on `--act`, which is withheld. Below threshold today; above it the moment `--act` is considered — which is exactly the decision Q1 is about.
- **commands_run** — `python3 /tmp/q3_enum.py` (executes `classify` over 7 pulse shapes × 4 exit codes):
  ```
  pulse                    exit0     exit42    exit1     exit2
  fresh NOT-ended dead     HOLD      RESUME    HOLD      HOLD
  STALE NOT-ended dead     HOLD      RESUME    HOLD      HOLD     <-- 4000 s old
  tally: {'DONE': 4, 'HOLD': 20, 'RESUME': 4}
  ```
  After the fix: `tally: {'DONE': 4, 'HOLD': 22, 'RESUME': 2}`, with `STALE NOT-ended dead` → `HOLD` and `fresh NOT-ended dead` → `RESUME` preserved.
- **fix** — `bench/tools/cy_actuator_2026-11-03.py` (staleness wired to the RESUME branch) and `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py` (fixture corrected + 4 new tests). The change can only turn `RESUME` into `HOLD`, so it strictly *reduces* acting and cannot cause an action — which is why I was willing to touch it despite "when the supervisor acts" being your reserved category. It removes an action; it never adds one.
- **falsifier** — Executed both directions. Against the unfixed classifier the stale pulse yields `RESUME` (red); against the fixed one `HOLD`, while `test_a_fresh_pulse_still_permits_a_resume` proves the check has not disabled the mechanism. Full file: `32 passed`. All four affected files: `68 passed in 1.24s`, and per-file collection reconciles to 32+21+9+6 = 68, so nothing was dropped.
- **I must report a test I modified.** My fix turned 3 existing tests red. Cause: `_pulse()` hardcoded `written_at: 1e9` — epoch 2001, so every pulse it built was ~25 years old against `time.time()`. That models an impossible state and was harmless only because nothing read the field. I changed the helper's timestamp to `time.time()` and **touched no assertion**, then added `test_a_stale_pulse_does_not_permit_a_resume` so the state the helper used to produce is pinned rather than lost. I flag this explicitly because "3 tests went green after I edited a fixture" is indistinguishable from weakening a measurement unless the reason is on the record.
- **what_would_refute_me** — Evidence that a pulse's `written_at` can legitimately be far in the past for a currently-paused run (e.g. the watchdog stamps it once at launch, not per heartbeat). Then 180 s is the wrong bound and my fix would block legitimate resumes. I checked that `PULSE_STALE_SECONDS` is documented as "3x the watchdog's 60 s interval", which implies per-heartbeat stamping, but I did not execute the watchdog to confirm it rewrites the field.
- **disagreement** — The brief frames Q3 as "is the defensible reading right?", a binary on `ended`. That framing is what hid the finding: the question is not *whether* the pulse is consulted but *which of its fields* and *with what preconditions*. Enumerating decisions over exit-code × `ended` only, as the brief did, cannot surface a third field being read without validation.

## Q4 — is "the hash chain covers a majority" a finding?

- **verdict** — Your restatement is correct in both halves, but your *explanation* of it is wrong, and the weaker reading you invite me to consider is wrong too: the straddle is gone, and it is gone because of the **share**, not the denominator.
- **reasoning** — I re-derived on routes your producer does not use. "Above half" is decided by an **exact binomial test against p = 0.5: p = 1.116040e-03** — no interval needed, no normal approximation. "It rose" fails on three independent routes: Fisher 2.030093e-01, Yates 2.053340e-01, and a two-proportion z-test **1.746471e-01**, with the CI on the *difference* — which is the quantity "it rose" actually claims — at **[−0.026748, +0.147504]**, containing 0.
  **The decomposition that settles your precision-vs-coverage claim.** You wrote that what changed is the denominator, "a gain in PRECISION, not a demonstrated gain in COVERAGE". Counterfactuals:
  - old share (0.541126) at the **new** n = 266 → Wilson **[0.481309, 0.600221]** — still straddles 0.5.
  - new share (0.601504) at the **old** n = 231 → Wilson **[0.537434, 0.662701]** — already clears 0.5.

  So the bigger denominator alone would *not* have cleared 0.5, and the new share would have cleared it at the old n. The majority result is attributable to the share value. Your prose explanation is therefore unsupported even though your two headline conclusions are right.
  **On the weaker reading you offered:** restating the guard to "pin the straddle at a larger n" would be false. At n = 266, k = 160 the interval excludes 0.5 on both routes and the exact test rejects p = 0.5 at p ≈ 1.1e-3. There is no straddle left to pin.
- **commands_run** — `python3` with scipy/statsmodels (`binomtest`, `fisher_exact`, `chi2_contingency`, `proportions_ztest`, `proportion_confint`); outputs as quoted. `python3 scripts/is_the_hash_chain_majority_real_2026-11-22.py` → **exit 0**, reproducing every figure in your table including the route agreements `0.000e+00` and `1.110e-16`.
- **Second falsifier (Wolfram).** `wolframscript -code 'N[{2*CDF[BinomialDistribution[266,1/2],106], 1-CDF[BetaDistribution[160,107],1/2]},10]'` → `{0.001116040145, 0.9994419799}`. Computed with Wolfram Language (local Wolfram Engine, via wolframscript); exit 0, no `Name::tag`, no `$Failed`. Agrees with scipy's `1.116040e-03` to 10 significant figures, and the posterior `P(p > 0.5) = 0.99944` corroborates independently of the frequentist route.
- **fix** — NONE. The restatement is yours to land; A1 should read *"above half, attributable to the share and not the denominator; not shown to have risen."*
- **what_would_refute_me** — If the 266 observations are not independent Bernoulli trials — e.g. the same artefacts re-counted across both measurements, making the two samples nested rather than independent. Then Fisher/z are the wrong tests and the exact binomial's independence assumption fails. **This is my one genuinely undecided point:** I did not establish whether the 231 are a subset of the 266. If they are, "did it rise" needs a paired test (McNemar), not Fisher, and my p-values are inadmissible. That measurement would decide it and I could not run it from the dispatched artefacts.
- **disagreement** — Your producer pins the 2026-11-06 figure as "PINNED historical observation, not re-measurable" and then feeds it to Fisher's exact test, which assumes two independent samples. If the earlier set is nested in the later, the test is mis-specified — and the brief's own "not re-measurable" note is the hint that it might be.

## Q5 — B209: what should the refusal budget be keyed to?

- **verdict** — None of your candidates (a), (b), (c) is right; the key should be the **set-overlap epoch** — a counter advancing when the newly observed process set is *disjoint* from the last. It scores 6/6 where every candidate you listed scores 4/6, needs no clock and no extra `ps` call, and keeps `spend()`'s existing reset so nothing already passing changes. Your condition 2 weakening is right in spirit and wrong in mechanism: "distinct per contiguous busy period" is correct, but *emptiness* is the wrong detector of a period boundary.
- **reasoning** — I started from your finding (i), which is the sharpest thing in the brief: a repair must supply a reset path, not merely stabilise the key. I then measured what actually churns. **The board makes exactly one pytest invocation** (`hooks/pre-commit:1184`; `grep -c` → 1), so your framing "replaces its pytest child per guard file" is wrong about the mechanism. The churn comes from *nested* pytest children, which `_RUNNER_PATTERNS`' `"pytest.*bench/tests"` also matches. Your own fixture encodes this and contradicts your prose: `CHURNING = [["70507"], ["70507","76042"], ...]` — a **constant parent** plus a moving member, commented "1 long-lived process, and a child replaced per guard file".
  That changes the problem. The set is not replaced; it **overlaps**. So overlap distinguishes "same activity" from "new activity" directly, with no clock and no gap-observation. Your (c) infers the boundary from *emptiness*, which is why it breaks on the mid-run gap you predicted — and also on a case you did not name: **two runs with no empty observation between them** (a turn that sees A finish and launches B), where (c) never advances and B inherits an exhausted budget. That is your candidate (a)'s failure, reintroduced.
  **Scored by execution, not judged** — `scripts/which_cy_refusal_key_survives_2026-11-22.py`:
  ```
  candidate        S1    S2    S3    S4    S5    S6
  (a) session      PASS  PASS  FAIL  FAIL  FAIL  PASS   3/6
  (c) empty-epoch  PASS  PASS  PASS  FAIL  FAIL  PASS   4/6
  (f) overlap      PASS  PASS  PASS  PASS  PASS  PASS   6/6
  (a+e) idle       PASS  PASS  FAIL  FAIL  FAIL  PASS   3/6
  (c+e) composed   PASS  PASS  PASS  FAIL  FAIL  PASS   4/6
  CANDIDATES PASSING ALL 6 : ['(f) overlap']
  ```
  S4 is your predicted mid-run-gap falsifier; it bites (c) exactly as you expected (`after_gap=1`, i.e. a full reset) and does not bite (f). S5 is the unobserved-gap case I added.
  **I corrected this harness twice against my own interest and both corrections are in the file.** The first version *spent* a refusal on the empty observation, which the real gate never does (`main()` returns 0 before `spend()`); that artefact failed (c) on S3 spuriously. The second had a stale S4 oracle (`n == 7`) inherited from the first model; the correct expectation is 6. Before correction (f) scored 6/6 and after the first correction only 5/6 — so the uncorrected run flattered my own candidate, and I have left both corrections documented in the script rather than presenting only the final table.
- **composability, measured not judged** — Composed `(c+e)` scores **4/6**; the best single candidate scores **6/6**. A composed fix is therefore *not* warranted: the single fix strictly dominates, which is your own 2026-10-02 rule applied rather than asserted. I did not report "the two don't interfere" — the weak form you excluded.
- **commands_run / falsifier** — executed, not described:
  ```
  $ python3 scripts/which_cy_refusal_key_survives_2026-11-22.py          # table above, exit 0
  $ python3 -m pytest bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py -q
  .........                                                                [100%]
  9 passed in 0.40s
  $ CDSFL_CY_GATE_PATH=/tmp/unrepaired_cy_monitor_gate.py python3 -m pytest <same> -q
  3 failed, 6 passed in 0.28s
    FAILED ...::test_a_churning_pid_key_still_climbs
    FAILED ...::test_an_idle_session_cannot_be_refused_for_ever
    FAILED ...::test_the_key_does_not_vary_with_child_process_churn
  $ python3 scripts/the_cy_refusal_budget_never_binds_2026-11-22.py
    ARM 2 ... 5 polls -> [1, 2, 3, 4, 5]
    unwatched arm is inert   : False
    THE DEFECT IS REPAIRED: the unwatched arm now climbs too.
  ```
  End-to-end on the real hook: `live-run exit=2`, `(cy refusal 1 of 60 for this run)`, state `{"key": "smoke|['run_x']", "n": 1}` — watched behaviour unchanged, as designed.
- **fix** — four files, written into the sandbox tree at their real paths:
  - `hooks/cy_monitor_gate.py` — `refusal_key()` extracted from `main()`; overlap epoch for the unwatched branch; watched branch untouched; fails toward *refusing* on any state fault, matching this file's existing doctrine.
  - `bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py` — condition-3 class unskipped, both strict `xfail`s removed, cases re-pointed at the real pipeline.
  - `scripts/the_cy_refusal_budget_never_binds_2026-11-22.py` — drives the gate's own key builder.
  - `scripts/which_cy_refusal_key_survives_2026-11-22.py` — new; the scoring harness above.
- **★ A finding that supersedes your (ii), and it is worse than what you reported.** You wrote that the guard's conditions 2 and 3 are "asserted by nothing" and that 2 tests are "owed and drafted". Against the file you stamped (`c3efa4352214b0e1`), condition 2 **is** asserted by two passing tests and condition 3 **is** written as two tests, `@pytest.mark.skip`ped pending the `refusal_key()` extraction. So your (ii) is stale.
  The real defect is the opposite shape and I demonstrated it mechanically: **the guard cannot see a correct repair.** Its two strict-`xfail` cases called `spend("sess|" + str(pids))` — a key string built *by the test* — so they mandate that the fix live inside `spend()`, while B209's defect is in the key *construction* (as the guard's own text says: "repair the key in hooks/cy_monitor_gate.py"). With `refusal_key()` extracted and the pid fallback repaired, the file still reported **`5 passed, 2 skipped, 2 xfailed`, byte-identical to its pre-repair result**, and I confirmed via `_find_repo()` that it was reading my patched file. Both strict markers would have stayed red against a working gate, so they could never have come off and the guard would have blocked its own repair indefinitely. That is a verification-integrity defect in the measurement machinery — materiality category 3 — and it is strictly more serious than an unasserted condition, because an unasserted condition is silent whereas this one actively reports a working repair as broken.
- **On your producer's exit-code conflict** — repair the **producer**, not the validator. The conflict is a symptom: your producer could not have exited 0 after a correct repair, because it had the same hand-built-key flaw as the guard, so its documented contract ("0 once repaired") was unreachable by construction. Having fixed that, it now exits 0 on the repaired gate and the validator needs no change. Teaching the validator to accept declared non-zero exits would have broken the one property that makes a declared figure trustworthy — that its producer ran clean — and it would have done so to accommodate a bug in the producer. Residual: the producer still prints the hardcoded line `resets: the budget NEVER binds` next to data reading `[1,2,3,4,5]`. I did not fix that label; it should be made conditional, and I flag it rather than claim it done.
- **the concrete failure my choice permits, as asked** — If an activity's process set is replaced with **no overlap at all** (every matched process exits before any replacement appears), the epoch advances mid-activity and B209 returns in a slower form. This does not occur on the measured board, whose parent pytest persists for the whole test phase. Second: a reused pid could make two genuinely separate activities overlap and carry an exhausted budget across, requiring reuse inside `_RUNNER_PATTERNS` between two polls.
- **what_would_refute_me** — Process history from a real board showing the matched set going fully disjoint mid-run — i.e. the parent pytest pid changing while the run continues. That is the one observation that breaks (f), and it is exactly the measurement you said was available ("testable against the real board's process history"). I could not take it: `pgrep` against a live board was not available in this sandbox, so **my S2/S4/S5 process sets are modelled from your recorded fixture, not observed live.** If the real parent churns, (f) degrades to (c) and the ranking changes.
- **disagreement** — Your claim (iii) is the part I'd push back on hardest. You say the counter resetting leaves the token cost unbounded, "where a working counter reads 7" for the observed `[1,1,2,3,1,1,1]`. But the board runs once per commit attempt, and a *correct* session-level-per-activity budget **should** reset between separate board invocations — that is condition 2 doing its job. Under the repair the cost is bounded at 60 refusals **per contiguous activity**, not per session; the cross-activity total remains unbounded, and no key choice can bound it, because the interface is a single slot (your own (iv)). So "a working counter reads 7" conflates within-run climbing with across-run resetting. The within-run resets you measured (the `1`s following a `3`) are the genuine defect; the between-run resets are correct behaviour counted as a fault.

---

**Not asked, flagged once:** the 9 mechanical items were out of scope and I did not touch them.

**Where I'd spend the next pass:** confirming live board process history (the one measurement that could refute Q5), and whether the 231 are nested in the 266 (the one that could refute Q4). Both are undecidable from the dispatched artefacts and I have said so rather than guessed.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 38 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_batches23_20261122T223441Z) -->

All instruments green. Here is my panel reply.

---

# SEAT REPLY — batches 2 & 3, v4 brief

**Artefact stamps verified** at dispatch: all six sha256 digests match. No `git` in the sandbox, so "independence from my change" is argued from symbol-reference and failure-content, not a pre-edit baseline — stated where it matters.

Passes run: **3.** Pass 1 read + ran all five producers/tests. Pass 2 implemented and tested the Q5 fix. Pass 3 re-ran the whole instrument set and checked neighbours; no new above-threshold finding emerged, so I stopped.

---

## Q1 — Is the recording-only supervisor pass yours to run?

1. **question** — Q1.
2. **verdict** — The record-only arm is mechanically safe to run (0/4 reserved categories, guarded by prereg P2), but the specific 2026-11-08 reservation of "either switch… remains his" is **not clearly superseded** by the general 2026-11-21 handover, so under CDSFL §1 (ambiguous → HARD) the authority question should be closed by a one-line confirmation, not by inference — I **partially disagree** that the judgement is settled.
3. **reasoning** — Read `bench/tools/cy_actuator_2026-11-03.py`. With `act=False`, `drive()` runs the launch once (line 290), never sets `acted` (300-301), and breaks after one iteration (304). `--classify-only` launches nothing. So "record-only" = launch-as-usual + classify + append JSONL, **no resume**. I ran the prereg: P2 is *"0 resumes are driven. Every recorded action flag is false and the launch command is invoked exactly once."* That is the mechanical guard, and it fails the instant any action is taken — so the mechanism half is sound. The unsettled half is interpretive: the 2026-11-08 sentence is *specific* and the handover is *general*; the canon that a later general instruction does not silently override an earlier specific one is exactly why this is not mechanically decidable.
4. **commands_run** —
   `python3 -c "import json;d=json.load(open('experimental_notes/data/dry_run_arm_prereg_2026-11-22.json'));..."` →
   `P2 :: 0 resumes are driven. Every recorded action flag is false and the launch command is invoked exactly once.`
   `_authority` field: *"Run on CC1's own judgement under the founder's 2026-11-21 autonomy handover: 0 of his 4 reserved categories apply…"*
5. **fix** — NONE (judgement question; no code defect).
6. **falsifier** — Behavioural, not runnable: P2 is the runnable guard and it already binds. I did not execute the arm (that is the action in question).
7. **what_would_refute_me** — An explicit founder statement that the handover covers actuator *operation*; or evidence that `--hil-review` is not one of "the two switches" the 2026-11-08 sentence reserved (i.e. it reserved only `--act` and the mode-select). Either makes the record-only run unambiguously the instance's.
8. **disagreement** — The brief treats "the mechanical half is already guarded, so only the judgement is open" as if that lowers the stakes. It is the reverse: a guarded mechanism makes the *authority* question the whole question, and §1 says an ambiguous authority defaults HARD → ask. The brief frames asking as already-resolved-against; I'd keep it open.

---

## Q2 — Read the timeout mark from source or from the collected test?

1. **question** — Q2.
2. **verdict** — The defect the brief describes is **already fixed in the dispatched tree**; the file reads the mark off the imported module's `pytestmark`, resolving the `BinOp` to the number `6346`, and it does so **without** requiring pytest collection — which is strictly better than *both* options the brief weighed.
3. **reasoning** — The dispatched `test_the_nested_suite_stays_bounded_2026-10-28.py` (mtime 2026-11-22T08:19:14, digest matches) no longer uses the `ast.Constant` walk the brief quotes. Lines 140-166 import `test_precommit_gate_cost_2026-09-10.py`, descend into classes (handling the method-on-class case), and read `getattr(_fn, "pytestmark", [])`, accepting `isinstance(_v,(int,float))`. Because decorator arguments are evaluated at import, `BOARD_BUDGET_SECONDS + 60` arrives as `6346`. This sidesteps the brief's own stated worry — "my proposal requires collection… may not be available where this check runs" — because `pytestmark` is an attribute set by the decorator at import, needing only import, not collection.
4. **commands_run** —
   `python3 -m pytest bench/tests/test_the_nested_suite_stays_bounded_2026-10-28.py -q` → `6 passed in 0.21s`
   Mark enumeration off the imported function → `TestItRuns.test_the_script_exits_zero timeout (6346,) ['int']` (and `6346 > 300`, so non-vacuous: removing the mark empties `marks` → first assert; value ≤ 300 → second assert).
5. **fix** — NONE (already repaired in the dispatched artefact).
6. **falsifier** — The test itself: it passes, and I confirmed it reads `6346` (an int) and compares `6346 > global 300`. If the mark were absent or ≤ 300 it fails.
7. **what_would_refute_me** — A deployment where this checker runs in a context that cannot *import* the gate-cost module (not merely cannot collect) — then the import-based read also fails and the brief's narrow `BinOp`-in-AST fix would be the only buildable one. I saw no such context.
8. **disagreement** — The brief's framing is stale against its own dispatched file: it presents a defect (`assert []`, "accepts only `ast.Constant`") that the stamped artefact no longer contains. The brief also frames the choice as "collection (mine) vs AST-BinOp (narrow)"; the shipped answer is a **third** option — import-and-read-`pytestmark` — that dominates both, and the brief omits it.

---

## Q3 — The supervisor asks for less corroboration on the path that acts

1. **question** — Q3.
2. **verdict** — The asymmetry is **defensible and I cannot name a concrete unsafe failure it permits**, given assumption A3 (exit 42 ⟹ a valid checkpoint was saved); the safety-relevant corroboration (pid liveness / G2) *is* consulted on the acting path, and the `ended` flag attests to a weaker fact the exit code already establishes first-hand.
3. **reasoning** — I exercised `classify()` directly. RESUME at exit 42 requires a pulse **with a pid that is confirmed dead** (`_pid_alive` returns True for unknown/None/unreadable, so unknown → HOLD). The `ended` flag is not consulted there — but `ended` means "the watchdog saw the process end," whereas at exit 42 the actuator *witnessed the exit directly* via the code, and G2 confirms the process is gone. To name a failure I need exit 42 + confirmed-dead pid + resuming-is-wrong: that requires a run that emitted 42 **without** a valid checkpoint, which is a breach of A3 in the runner, and which reading `ended` would **not** catch (`ended` ≠ "checkpoint valid"). pid reuse errs toward HOLD (alive → HOLD). So no nameable failure under A3.
4. **commands_run** — `classify()` table:
   `exit0 pulse-not-ended : HOLD`
   `exit42 pulse-not-ended, pid dead: RESUME`
   `exit42 no pulse : HOLD`
   `exit42 pid alive : HOLD`
5. **fix** — NONE. Changing when the actuator acts is the founder's category, and `--act` is withheld (Q1). The only *real* strengthening would be to check the **checkpoint artefact's existence** before RESUME (closing the A3 gap) — not to consult `ended`; I flag that as the measurement direction, not a change I made.
6. **falsifier** — The `classify()` table above is the runnable check; it confirms RESUME is gated on confirmed-dead pid, not on `ended`.
7. **what_would_refute_me** — A demonstrated runner code path that reaches `sys.exit(42)` **without** writing a resumable checkpoint. That would make the asymmetry bite — and would also prove `ended` is the wrong guard (checkpoint-existence is), so it refutes the brief's framing too, not just my "no failure" verdict.
8. **disagreement** — The brief asks whether `ended` should be consulted at exit 42. That is the wrong corroborator. `ended` attests "watch saw the end"; the resumption risk is "checkpoint invalid," which `ended` never measures. If the asymmetry is ever closed, the correct guard is checkpoint-existence, not symmetry with the exit-0 `ended` check.

---

## Q4 — Is "the hash chain now covers a majority" a finding, or a bigger denominator?

1. **question** — Q4.
2. **verdict** — The honest restatement is the **weaker** one: the share is above half **and nothing has been shown to have changed**. "Above half" is a true statement about today's precision; it must not be phrased so a reader infers a rise, because the two measurements are statistically indistinguishable (Fisher p = 0.203).
3. **reasoning** — Ran the producer. 160/266 = 0.601504; Wilson [0.541626, 0.658492] and Clopper-Pearson [0.539926, 0.660794] both clear 0.5 (two routes each, max abs diff 0.000e+00 / 1.110e-16). Against 125/231 = 0.541126: Fisher p = 2.030093e-01, Yates p = 2.053340e-01 → not distinguishable at 0.05. So what moved is the **denominator** (266 vs 231), which narrowed the interval enough to clear 0.5 — a gain in *precision*, not *coverage*. A1 should therefore be restated to assert the straddle has closed at the larger n (interval lower bound > 0.5), **not** that coverage rose and **not** merely that the straddle persists — the straddle has demonstrably closed.
4. **commands_run** — `python3 scripts/is_the_hash_chain_majority_real_2026-11-22.py` → every figure in the brief reproduced exactly (listed above), `above half = True; shown to have risen = False`.
5. **fix** — NONE. A1's restatement is a one-line assertion edit the brief is soliciting a direction for, not a defect in a script I was handed; I recommend `lo > 0.5` (which the producer supports) with a comment that it asserts precision-at-n, not a rise.
6. **falsifier** — The producer is the check; it exits 0 and prints both answers. If a future store makes Fisher p < 0.05, "did it rise" flips to True and the restatement can strengthen.
7. **what_would_refute_me** — A paired/temporal test appropriate to the same underlying store (not two independent proportions) showing the change is significant; or evidence the 266 and 231 samples are not comparable populations (then even "above half vs prior" is the wrong comparison).
8. **disagreement** — I disagree with the brief's middle reading that "the guard should pin the straddle at a larger n." The straddle has **closed** at n=266 (both lower bounds > 0.5) — pinning a straddle that no longer exists would be as wrong as claiming a rise. The correct guard pins *precision-at-n* (lower bound clears 0.5) while explicitly disclaiming a coverage change. The brief offers "majority" vs "nothing changed at all" as the two options and buries the actually-correct third: *the interval cleared 0.5 (true) and that is a denominator effect (true), both stated, neither implying the other.*

---

## Q5 — What should the anti-trap refusal budget be keyed to? (B209)

1. **question** — Q5.
2. **verdict** — Candidate **(c)**, the contiguous-activity epoch, is correct and is the **simplest *sufficient*** fix: (a) and (b) are simpler but fail condition 2, which makes them insufficient, not smaller. I implemented (c) as an epoch that advances only on an **observed** empty live-set, extracted `refusal_key()`, and removed the churning pid list from the key. All three conditions now hold on the real key path, including the brief's named falsifier (a process-level gap with no observed idle does **not** reset mid-run).
3. **reasoning** — The root cause (brief finding i) is that the churn was *simultaneously* the defect (broke condition 1) and the *only* reset path (satisfied condition 2 by accident) — `spend`'s sole reset is `if st.get("key") != key`. So a correct fix must remove the churn **and supply a new reset**. Observation-based (c) is strictly better than a gap timer or the withdrawn time-bucket: those infer idleness from elapsed time and cannot distinguish "the run ended" from "the session was busy working," which is exactly the brief's expected falsifier for (c); driving the reset off a *hook-observed* empty set (`note_idle`, called on `main()`'s idle early-return) resets only on a real idle Stop, never on a sub-second process gap that fires no Stop. On the load-bearing judgement — is "distinct per contiguous busy period" the right weakening of "distinct per run"? **Yes, and necessarily**: condition 3 forbids reading the run, and "contiguous busy period" is the finest partition computable *without* reading it; per-run requires reading runs apart, which violates condition 3.
   Brief finding (ii) is confirmed and addressed: the existing guard and producer drove `spend()` with hand-built churning keys — the wrong layer, since `spend` is a pure counter that *should* reset on a genuinely different key. The churn-invariance belongs in `refusal_key()` (where `main()` builds the key), so I retargeted the guard and producer to `refusal_key`, which is the real path and a strictly stronger check, and extracted `refusal_key()` so condition 3 is now assertable (unskipped). Brief finding (iii), the unbounded token cost: fixed as a consequence — the counter now binds, so the 60-refusal cap on re-injected context is reachable for unwatched runs too.
   On the **second defect** (validator refuses a declared figure whose producer exits non-zero): confirmed at `scripts/panel_brief_validate.py:468-472`. The right repair is **producers signal liveness in OUTPUT, exit 0 whenever the measurement ran** — *not* relaxing the validator. Relaxing it ("accept non-zero when the brief states the expected code") trusts the brief's word about what an exit means, re-opening the "assert a verdict you did not compute" hole and making non-zero ambiguous between "failed to run" (the 6.2 defect the rule exists for) and "signalled liveness." A printed token (`b209_state = REPAIRED|LIVE`) that the figure value captures keeps the validator's invariant intact and makes the producer citable. I did **not** implement that general convention change (cross-cutting, many producers; simplest-sufficient says don't sweep it into a point fix) — and note the B209 fix **resolves this instance** anyway, since the producer now exits 0.
   **Composability:** the two repairs (gate epoch vs producer-liveness convention) are orthogonal — no demonstrated synergy, neither needs the other. Per the founder's 2026-10-02 definition I do **not** compose them; I deliver the measured fix (A) standalone and recommend (B) as a separate convention. Measured fact that (A) dominates for the immediate conflict: the producer re-ran at **exit 0** after (A) alone.
4. **commands_run** —
   - `python3 /tmp/falsify_b209_fix.py` (drives `refusal_key`→`spend`, the real path):
     `condition 1  churn via refusal_key -> [1, 2, 3, 4, 5]`
     `condition 1  reaches budget, unwatched -> 70`
     `condition 2  after observed idle, new period opens at -> 1`
     `condition 2  no idle observed, counter continues -> 2`
     `condition 3  key invariant to child churn -> 'sess|unwatched' 'sess|unwatched'`
     `ALL THREE CONDITIONS HOLD; B209 repaired on the real key path` — exit 0
   - `python3 scripts/the_cy_refusal_budget_never_binds_2026-11-22.py` → `THE DEFECT IS REPAIRED: the unwatched arm now climbs too` — exit **0** (was 1).
   - `python3 -m pytest bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py -q` → `9 passed` (was 5 passed, 2 skipped, 2 xfailed).
   - End-to-end real `main()` on a watched pulse: `rc=2 (cy refusal 1 of 60)`, `2 of 60`, `3 of 60` — counter climbs through the live hook.
5. **fix** — files written into the repository tree:
   - `hooks/cy_monitor_gate.py` — extracted `refusal_key()`, added `note_idle()` + `_load_state`/`_save_state`, epoch in `spend()`, rewired `main()` (uses `refusal_key`, calls `note_idle()` on the idle early-return).
   - `bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py` — retargeted to `refusal_key`, removed the two `xfail(strict=True)` markers (per the file's own standing instruction, defect fixed), added condition-2 (observed-idle reset + no-reset-without-idle) and unskipped condition-3 tests. No assertion weakened — strengthened to the real layer.
   - `scripts/the_cy_refusal_budget_never_binds_2026-11-22.py` — unwatched arm now drives `refusal_key` as `main()` does; exit flips to 0 on repair.
6. **falsifier** — `/tmp/falsify_b209_fix.py` (shown above), run via Bash before reporting: exits 0 with all three conditions holding and the brief's named mid-run-reset falsifier demonstrated negative (counter continues to 2). It imports the **real** hook, asserts the `CDSFL_CY_STATE` override is in force (touches nothing live), and raises/ prints `FALSIFIED` if any condition breaks.
7. **what_would_refute_me** — (i) A board that fires a genuine idle **Stop** between two back-to-back runs with no work in between would advance the epoch and give run B a fresh budget — if the founder's intent is that two such runs *share* one budget, (c) is too fine there (though still safe; it only ever grants *more* budget, never silences). (ii) If the hook is ever invoked by something other than a Stop event (so `note_idle` never fires despite real idleness), condition 2 degrades toward (a) — I'd want the real Stop-event cadence measured. (iii) If `refusal_key` is in practice *bypassed* by a caller building keys inline again, the fix is defeated at that caller — searchable regression.
8. **disagreement** — The brief's finding (i) says a repair "must supply a new reset path, not merely stabilise the key," and offers candidates (a)/(b)/(c) as if they were comparable choices. They are not: (a) and (b) are **disqualified**, not merely weaker — removing the churn without adding `note_idle` leaves zero reset paths, so they are insufficient by construction, and the brief's scoring ("meets 1 and 3; fails 2") understates that failure as a trade-off when it is a hard disqualification. Second, the brief frames the second defect as a binary ("relax the validator OR change producers"); the honest answer is that relaxing the validator is *inadmissible* (it re-opens a verified integrity hole), so it is not a real alternative — and the B209 fix moots the instance regardless.

---

### Standing-principle attestation
- **Additive / simplest-sufficient:** the gate fix adds exactly one reset path (`note_idle`) and one extraction (`refusal_key`); every new symbol is wired to `main()` and executed by the guard. I rejected (a)/(b) as insufficient and declined the cross-cutting validator/producer convention change as more surface than the point defect requires.
- **No compelled convergence:** disagreement fields are my own; I did not smooth to the brief.
- **Tools decided:** every verdict that could be executed was — the B209 fix is confirmed by an independent falsifier re-running the real module, not by my prose.
- **Not Wolfram-verified:** the Q4 statistics are open-source only (statsmodels/mpmath/scipy, two routes agreeing to ~1e-16). I did not invoke Wolfram as a second falsifier; the arithmetic is already double-routed, and the claim stands on the open-source tools alone.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_batches23_20261122T223441Z/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
