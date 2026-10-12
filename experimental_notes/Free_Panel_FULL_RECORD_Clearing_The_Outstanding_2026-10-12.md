# Free panel: clearing the outstanding, and a defect neither seat could see

Record written 2026-10-12T20:13:15+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED, AND WHY THIS ROUND EXISTED

The founder's instruction of 2026-10-12, verbatim: "Run the free panel to clear as much of the outstanding work as possible, then test it to ensure their solutions work and apply cleanly, and then fix the ones that do not. The question you say are outstanding are too vague, and I no longer know what they are referring to, or if they are still relevant. This is a huge list of apparently unresolved issues. Work with the panel to clear as many as possible, in keeping with our formal simplest sufficient fix, and other formal standards, and with the project specification as a whole."

FREE SEATS ONLY. cc2 and fable, both on the Max subscription, both ALIVE on attempt 1, each in its own sandbox, fable staggered 20 seconds behind cc2 under the shared-subscription serialisation rule. No paid dispatch occurred and none was authorised. cc2 ran 1073.0 s across 127 tool calls; fable 989.1 s across 123.

THE BRIEF COVERED 4 ITEMS: the 3 standing convergence blockers (the blocker counter against its release valve, the integrity gate that refuses a correct falsifier, and findings the routing ladder never serves); A19; an adversarial audit of this session's commits; and the 21 parked items. Fixes were required AS FILES at real paths, with fields for verdict, fix, falsifier, reasoning, refutation, termination and disagreement.

WHAT WAS DONE WITH THE FINDINGS, AND IT WAS NOT ACCEPTANCE

Nothing was auto-applied. Every delivered fix was EXECUTED, cross-tested against the other seat's falsifier, and mutation-verified in both directions. 21 of 31 of the seats' own tests fail on the unfixed tree (67.7419%, Wilson 95% [50.1410%, 81.4306%]), so their falsifiers are genuine rather than vacuous.

Three outcomes are worth recording because none of them is "the panel was right".

First, on the integrity gate, both seats fixed the same class by different mechanisms and each argued its own in prose. Measured over the 4 interpreters present on this machine, the prose was backwards: the subprocess probe argued as "more robust" covered 2 of 4, the declared root list covered 3 of 4, and the composition of the probe mechanism with full discovery plus sysconfig paths covers 4 of 4. The declared paths are therefore not applied, as measured redundant rather than judged redundant. The measuring instrument was itself wrong first, counting roots that do not exist on disk as coverage gaps, which read the composed fix as 1 of 4 when it is 4 of 4.

Second, on the never-served finding, the two fixes were STRICTLY WORSE COMPOSED than either was alone. One seat SERVES the finding so a tool can decide it; the other opens a DOOR so a finding nothing ever touched stops blocking. Serving writes a routing history entry, and the absence of a routing history entry was one of the facts the door required, so the serve consumed the door's own trigger and the finding blocked for ever again with neither mechanism able to release it. Neither seat could see this, because each tested its own fix in isolation and in isolation each is correct. The repair distinguishes served-and-no-reading from served-and-ruled on an explicit sentinel set that fails closed, proved unsatisfiable by z3 with SymPy agreeing.

Third, and this is a claim made here and then WITHDRAWN, so it is recorded with its refutation rather than quietly dropped. It was asserted that one seat's record patch would have deleted two of the founder's own rulings: the block carrying his Exp 53 ruling and a reversion of task 10.2 from WITHDRAWN back to BLOCKED. That assertion was wrong. The other seat's harvested diff carries the same two removals verbatim, and two seats sandboxed separately and blind to each other cannot coincidentally delete the same two blocks of the same file. The common cause is the diff direction: the reference side of each harvested diff is the LIVE repository file, modified at 19:16:09, while both sandboxes were cut at 19:15:13 and 19:15:33. Neither clone ever contained the 19:16:09 edit, and a line present in the live file but absent from an older clone appears with a leading minus, which reads exactly like a deletion the seat performed. The two blocks are this assistant's own additions, recording the founder's rulings, written 36 seconds after the first sandbox was cut. One seat never touched that file at all; the other's only edit to it is the additive A19 correction, which is applied.

The decision taken was nonetheless correct. Only the additive A19 hunk was applied, and copying a seat's whole file would genuinely have reverted the founder's two rulings out of the live tree, because that seat's copy predates them. But the reason recorded for the decision was wrong, and the difference matters: one version accuses a seat of destroying the founder's words, the other describes a stale clone base. The failure class is a predicate checked against the wrong baseline, which this project has recorded before. Producer: scripts/no_seat_deleted_his_rulings_2026-10-12.py.

Both seats' full replies follow, unedited.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Clear the outstanding work, in keeping with the formal standards

You are a seat in a CDSFL free panel (cc2, fable). No paid seat is dispatched. The
founder has read a generated report of every outstanding item and annotated it. His
annotations are quoted verbatim below and they are the brief.

**HIS OVERALL INSTRUCTION, verbatim, 2026-10-12:** *"Run the free panel to clear as much
of the outstanding work as possible, then test it to ensure their solutions work and apply
cleanly, and then fix the ones that do not. ... Work with the panel to clear as many as
possible, in keeping with our formal simplest sufficient fix, and other formal standards,
and with the project specification as a whole."*

**HIS STATED OBJECTIVE, verbatim:** *"Clearly the objective is clean honest convergence."*

## Every number in this brief is QUOTED, not measured here — verify it

The brief's own validator flags 10 numeric claims in the prose as backed by no declared
figure, and it is right to: *"A declared figure is RE-EXECUTED. A number typed in a
sentence is not, and that is exactly how `gamma is 0.451` reached 2 seats when it is
0.415413."*

So treat every number below as a CLAIM TO CHECK rather than a fact to build on. The
severities (0.7, 0.6, 0.45, 0.50) are quoted from `experimental_notes/STUDY_IN_FLIGHT.json`
under `open_defects`; the interpreter versions (3.13, 3.9) from the integrity-gate defect
record; and the replay figures (36.8%, 63.2%, 0 of 87, Wilson [0.0%, 4.2%]) from the
message of commit `6c10fe4` itself. **If any of them is wrong, saying so is a result and
it changes the answer.** One of this session's own figures was withdrawn for exactly this
reason: a never-named count of 527 of 571 was an artefact of a regex that could not match a
hyphen, against a true 401.

## What is required of you, and what will be done with it

Produce **FIXES, not findings**. The founder has said this repeatedly — measured at 26 of
his 92 older imperative instructions — and in his own words: *"The purpose of these multi
model reviews is not just to find problems (although that is clearly 50% of it), but also
to suggest fixes. But you have a bad habit of simply telling our models during these
reviews 'find problems with this code' and not telling them to come up with fixes."*

**DELIVER EACH FIX AS A FILE.** Write your fix INTO the sandbox repository tree at its
real path — edit `bench/reference_runner_v3.py` itself, not a copy, not a patch in prose,
not something under a scratch directory. A fix left in prose or in scratch space is
destroyed at teardown and is not delivered. The founder's words on exactly this, 2026-08-30:
*"Jesus why are you throwing sandbox repairs away? Sure sandboxes should be deleted after
we are done with them and after you have extracted fixes, not before!"* Your sandbox is
harvested, so a file written at its real path survives and can be tested and applied.

For each item you address:
1. **Name the file and line** you would change, and give the change.
2. **RUN something.** Execute a falsifier against your own fix. The tool output is the
   evidence; reasoning selects and interprets it but never substitutes for it.
3. **State what would refute your own answer.**
4. **Name a termination criterion** — when is this item done?
5. Say explicitly if an item is **already resolved**, or if the premise is wrong. A
   withdrawal is a result.

Every fix must meet two formal standards:
- **SIMPLEST SUFFICIENT FIX.** Simplicity and sufficiency are different measures; the fix
  must be both.
- **THE ADDITIVE STANDARD.** Work adds to reliability, functionality, accuracy and the
  project's stated aims. Never disable or remove a feature; removal only where a
  COMMITTED MEASUREMENT shows the replacement dominates on a named property. Symmetrically,
  an addition nothing reaches is not additive: a new flag, gate or entry point must be
  wired to a caller and executed by a test.

Fixes are **SUGGESTED to the human in the loop**, never auto-applied. Findings are
confirmed programmatically or by him, never by model vote.

## ITEM 1 — the convergence blockers. This is the priority.

Three defects in `experimental_notes/STUDY_IN_FLIGHT.json` under `open_defects` currently
stop a run converging. His objective is clean honest convergence, so these come first.

### 1a. The blocker counter and its release valve disagree about severity

`unverified_critical_count()` in `bench/reference_runner_v3.py` counts findings with **no
severity test in its body** — it skips non-UNCONFIRMED, already-escalated and exhausted
entries, then counts what is left. The only thing that can RELEASE an entry from that
count, the `exhausted` valve, requires `severity >= 0.7`. So a sub-critical finding can
ENTER the tally that blocks convergence and has no exit.

Live instance: finding C0042 in `study_run1b_2026-10-03_20261003T100439Z`, severity 0.6,
zero-character falsifier, emitted in round 2 and never given one. Leave-one-out on the
live registry: removing it drops the tally from 1 to 0. **That run could not converge.**

The counter's own docstring still claims it counts `severity >= CRITICAL_SEVERITY_THRESHOLD`,
which its body does not do — stale since 2026-09-06.

**HIS ANNOTATION, verbatim:** *"Clearly the objective is clean honest convergence. What are
you advising? One fully paid run so this can happen, or a simulated run with these missing
severity tests in place? Ask the panel how to resolve this too if no current solution
exists. But instinctively my position is we should go with whichever of these, or whichever
combination of these bring us closest to that objective, subject to testing, rather than
assumption."*

### 1b. The integrity gate refuses a correct falsifier, by construction

The sandbox integrity gate allows the harness's own Python 3.13 directories. A falsifier
that spawns a second interpreter gets macOS's `/usr/bin/python3` (3.9), whose stdlib is
under `/Library` and user-site under `~` — both in the denied regions. Its ordinary import
reads are recorded as denials, and ANY denial becomes `INTEGRITY_VIOLATION`.

It is structural: finding C0050's falsifier spawns `/usr/bin/python3` precisely BECAUSE
the defect it demonstrates is that the target prescribes a bare unpinned `python3`. Any
falsifier for that defect class must do the same, so the gate is guaranteed to refuse the
correct falsifier. C0050 is severity 0.7 — a critical — recorded as untested and pushed to
a human. Counterfactual: with the 3.9 roots allowed, the identical falsifier returns
CONFIRMED instead of INTEGRITY_VIOLATION.

The refuse-rather-than-flag behaviour entered on 2026-08-15 in a milestone merge citing no
founder ruling, and he confirmed on 2026-10-03 he was never consulted.

**HIS ANNOTATION, verbatim:** *"Ask the free panel how to resolve this too."*

### 1c. A finding can block a run for its whole life without the ladder serving it — AND a commit quotes him approving a change he says he never approved

Two findings in `study_run1b_2026-10-03`, C0066 at severity 0.45 and C0073 at 0.50,
reached the blocker tally with **zero verdicts, no routing history and no falsifier code**.
Nothing ever served them. The post-run sweep settled two similar findings but C0073 arrived
in the identical shape afterwards, so the sweep is not a net solution.

**THE PROVENANCE QUESTION, AND HE HAS NOW RULED ON IT.** The severity gate was removed from
`unverified_critical_count` in commit `6c10fe4`, 2026-09-06 16:21:48, whose message quotes
him as *"Verdict: do it. There are no votes in CDSFL."* But
`DECISIONS_AWAITING_YOU_2026-09-06.md` item 23 records, at 22:15 the same day: *"ANSWERED
2026-09-06 22:15 AND THE RECOMMENDATION WAS REJECTED. He rejected both removal and the
rubric swap and ordered worked proofs instead."*

**HIS ANNOTATION, verbatim:** *"Again I never approved the removal of the severity gate, so
yes, it should be restored. But the worked proofs should remain part of the design too. But
check the overall design with the free panel, and ask them to suggest fixes and solutions,
where any may be needed."*

**A TENSION YOU MUST ADDRESS DIRECTLY, because executing his instruction naively may
contradict his own standing principle.** The removal's stated reasoning was: *"The A4
fail-safe read `severity >= 0.7`, where severity is a float the SOURCE MODEL assigns — a
vote wearing a number's clothes. It now gates on whether a tool actually returned a
verdict, which is a fact rather than an opinion."* And it carried a measurement: replayed
over 87 archived reports, the replacement blocks MORE in 36.8%, identically in 63.2%, and
FEWER in 0 of 87, Wilson [0.0%, 4.2%] — so convergence could only get harder, not easier.

"There are no votes in CDSFL" IS his standing principle. So restoring a model-assigned
float as a convergence gate re-introduces a model's opinion into the gate. **Is he ruling
on PROVENANCE (an unauthorised change must be reversed) or on DESIGN (severity should
gate)? What design satisfies both his ruling and his no-votes principle, and keeps the
worked proofs he ordered?** Answer that explicitly, with a fix.

Measured, for your use: restoring the severity gate takes the blocker tally from 3 to 0 on
this run's pre-sweep registry, after which the gate blocks on `contested=2` and the
zero-critical streak instead.

Producers you may run: `scripts/exhausted_marking_age_lock_2026-10-03.py`,
`scripts/a4_blockers_lock_audit_2026-10-03.py`,
`scripts/gate_replay_on_registry_2026-10-03.py`,
`scripts/routing_severity_gate_2026-10-03.py`.

## ITEM 2 — A19, the admissibility scorer: does it work, and is it the whole solution?

`S_k`, the admissibility scorer, classifies a whole TARGET rather than each element inside
it, so a computable fragment sitting inside prose is never scored. His design point,
2026-09-10, verbatim: *"clearly it should simply mark a purely prose input as
'inadmissible', while still solving any computationally reducible elements within that
prose! This is STEM."*

The entry is `A19` in `experimental_notes/CDSFL_MASTER_TASK_LIST.md` (line ~566), marked
`state: OPEN | status: TESTED`, and its own words are *"BUILT AND TESTED 2026-09-11, NOT
DONE — Section P applies, and the last step is HIS."* Its evidence,
`bench/tests/test_a19_gates_and_baseline_share_a_substrate_2026-09-11.py`, passes 20 tests.

Panel round 13 on 2026-09-11 had both seats independently find the same critical defect in
it: a gate that could not fail moved from `e4` to `e3` inside the commit that removed it
from `e4`. That is recorded as repaired.

**HIS ANNOTATION, verbatim:** *"Didn't the models in panel review offer objections to this
design? Wasn't an overall better design decided? More importantly, does this deign even
work? If the panel review on this work is outstanding, then run this first, and ask if it
presents the whole solution, and if not what does?"*

So: **(a)** what objections did the earlier review raise, and were they answered or
dropped? **(b)** was a better design decided and then lost? **(c)** DOES IT WORK — run it
and show the output. **(d)** is it the whole solution, and if not, what is?

## ITEM 3 — review this session's own work

35 commits landed between 2026-10-11 16:20 and 2026-10-12 14:54. **HIS ANNOTATION,
verbatim:** *"Has this all been built, or fixed, and tested? Ask the free panel to look at
this work too and to suggest fixes where any are still needed."*

Read `git log --since=2026-10-11T12:00:00+01:00 --stat` and audit it. The largest items:
the restore now fires at a task boundary (`~/.claude/hooks/compaction_task_boundary.py`);
a per-run round recommendation (`bench/round_budget.py`); a human-review trigger
(`bench/human_review_trigger.py`); the domain-verdict measurement rebuilt
(`scripts/the_domain_verdict_gap_2026-10-11.py`); a generated morning report
(`scripts/morning_report_build_2026-10-12.py`); output hashing
(`scripts/stamp_output_hash_2026-10-12.py`); the free seats re-pointed at the stagger
(`bench/tests/test_shared_subscription_seats_are_serialised_2026-10-05.py`).

Be adversarial. This output was produced by another system and has not been independently
verified. Look for: errors at interfaces between subsystems; unstated assumptions that
conflict across components; constraint violations visible only at system level; and
conclusions that are internally consistent but wrong. **Your task is to find what is wrong,
not to confirm what is right.**

## ITEM 4 — the 21 parked items

`experimental_notes/PARKED_FOR_THE_FOUNDER.md` holds 21 items judged non-blocking and
appended rather than raised. **HIS ANNOTATION, verbatim:** *"Ask the free panel to look at
this work too and to suggest fixes where any are still needed. Any that still needs my
explicit ruling can be reserved for my closing report on the above work."*

Several are already marked resolved or superseded in the file itself. Say which are
**already closed**, which have a fix you can produce now, and which genuinely need his
ruling. A parked item that is already resolved should be named as such, not re-litigated.

## What to return — the output shape, field by field

A numbered list keyed to the items above. For **each** item you address, return these
fields by name:

- **verdict** — one of FIXED, RESOLVED ALREADY, PREMISE WRONG, or NEEDS HIS RULING.
- **fix** — the real path you wrote in the sandbox tree, and the change. Say
  `NO FILE WRITTEN` explicitly if you wrote none, and why.
- **falsifier** — the command you RAN against your own fix, and its actual output. A
  falsifier you did not execute is not a falsifier.
- **reasoning** — why this fix and not another, against the simplest-sufficient and
  additive standards.
- **refutation** — what evidence would overturn your own answer.
- **termination** — when is this item done, stated so someone else could check it.
- **disagreement** — where you expect the other seat to differ, and on what. State this
  even if you think they will agree, and say so if you believe the brief itself is wrong.
  Disagreement is preserved as information, never smoothed to consensus: there is no
  compelled convergence in this panel and no model vote decides anything.

Prefer depth on the convergence blockers (Item 1) over breadth across Item 4. Item 1c
carries a design tension you must address directly rather than route around.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 127 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel clear_the_outstanding_2026-10-12) -->

208 passed. Here is my return.

---

# Seat return — cc2/fable free panel, 2026-10-12

## Premise corrections first, because several of the brief's numbers are wrong

| Brief's claim | Measured | Verdict |
|---|---|---|
| A4 tally is **3**, severity restore takes it "3 → 0" | **2** on the live post-sweep registry (75 entries) | WRONG |
| 1a: counter has **"no severity test in its body"** | A severity test exists at line 2968, **restored 2026-10-06** | WRONG, stale by 6 days |
| 1a live instance **C0042** | Not in the blocker set at all; survivors are **C0066, C0073** | STALE |
| Replay: 36.8% / 63.2% / 0 of 87, Wilson [0.0%, 4.2%] | 32/87=36.7816%, 55/87=63.2184%, 32+55=**87** exactly; Wilson 0/87 = **[0%, 4.2288%]** | **CORRECT** |
| A19 "20 tests" | `20 passed` | **CORRECT** |
| A19 "exploit still ADMITTED at sk=1.0000" | `flag=False: NO_SCORE sk=0.0` / `flag=True: ESCALATE sk=0.0` | WRONG |
| Item 3: `git log --since=...` | **No `.git` in the sandbox** — command cannot run | UNRUNNABLE |

Wilson verified twice: statsmodels `4.228751%`, and Wolfram Language (local Wolfram Engine, `wolframscript`, exit 0) `4.228750694412033`.

**I also withdraw one of my own results.** My first draft of the Item 1 fix reported **A4 → 0** and I had tool output saying so. It was over-wide — it had no age lock and released a finding that arrived in the final round. The honest figure is **2 → 1** at the run's own round 7. Details in 1a/1c below.

---

## 1a + 1c — the blocker counter. *(One defect, not two. I merge them.)*

**verdict: FIXED** (and the brief's premise for both is partly **PREMISE WRONG**)

**The premise correction that reframes everything.** The severity gate is *already restored*, since 2026-10-06, and restored *in the form that resolves 1c's design tension*: it gates on `severity_is_proven`, not the raw float. So —

**Answering 1c's tension directly: he is ruling on PROVENANCE, and the DESIGN question is already answered in tree, without violating no-votes.** `severity_is_proven` accepts a severity only when the model **reproduced its own R_k from its own stated inputs**. That is a computation the harness re-executes, not a number a model asserted — which is precisely the substitution the 2026-09-06 removal demanded ("whether a tool ran and resolved … a fact, not an opinion"). The removal's measurement (AUC 0.464, σ=0.1419 vs a 0.09 band, 82/273 straddling 0.7) indicts the **raw float** and does not touch a **proven** one. **The worked proofs he ordered are not a separate deliverable — they are the gate.** Nothing further is owed on 1c's provenance question.

**The defect that actually survives**, and it is what 1a and 1c are both really seeing: both release doors are closed, by construction, to a finding **nothing ever served**.

- `exhausted` valve (line 4254) requires `severity >= 0.7` **AND** `len(verdicts) > 0`. C0066/C0073 fail **both** — so widening the severity term, the obvious fix, **releases nothing**. Asserted in a test so it isn't re-proposed.
- `severity_is_proven` door requires a recomputable R_k. No corroboration block → `SKIP` → never proven.

**fix** — `bench/reference_runner_v3.py`:
- **line 2241** — new `_routing_ladder_never_served(e)`: seven emptiness facts (no verdicts, no `routing_history`, no `falsifier_code`, no `falsifier_verdict`, no `routing_verdict_unreconciled`, not `routing_deferred`, not `hil_escalated`). **Every term is mechanically checkable; no float enters.**
- **line ~3029** — the door, **age-locked** via new `LADDER_UNSERVED_MIN_AGE_ROUNDS = 1` (beside `CRITICAL_SEVERITY_THRESHOLD`). `current_round=None` **disables it**, so all existing callers are unchanged.
- **line 2829** — the stale docstring replaced. It claimed `severity >= CRITICAL_SEVERITY_THRESHOLD`; the live rule is the **inverse and conditional**. Stale 2026-09-06 → 2026-10-12.
- **line 3075** — paired reader `ladder_unserved_findings(current_round)`, same predicate, same age lock.
- **line ~18130** — wired into the convergence-gate report as `UNSERVED-FINDING ADVISORY`, beside the 2026-10-02 key-access advisory.

Also `bench/tests/test_an_unserved_finding_cannot_block_for_ever_2026-10-12.py` — **new, 18 tests**.

**falsifier** — `python3 -m pytest …test_an_unserved_finding_cannot_block_for_ever_2026-10-12.py -q` → `18 passed`. The decisive measurement:

```
LADDER_UNSERVED_MIN_AGE_ROUNDS = 1
no round passed (door disabled): A4 = 2
round 5: A4=2 reported=[]                  excluded_implies_reported=HOLDS
round 6: A4=1 reported=['C0066']           excluded_implies_reported=HOLDS
round 7: A4=1 reported=['C0066']           excluded_implies_reported=HOLDS
round 8: A4=0 reported=['C0066','C0073']   excluded_implies_reported=HOLDS
```

**So the answer to his 1a question — paid run, or simulated run? — is NEITHER.** This blocker needed **one more round**. C0073 arrived *in* round 7 with age 0; at round 7 the gate correctly **still refuses** to converge, because a finding emitted in the final round that nothing examined is not something a clean run may be declared over. **That refusal is the honest convergence he asked for**; my withdrawn A4→0 would have been a false one.

**Two regressions my own fix caused, both caught by running, both repaired:**
1. `test_key_access_advisory_2026-10-02.py` failed `assert 0 == 1`. Correct failure — my predicate was too wide: **`UNTOOLABLE` is a ruling, not an absence.** An instrument ran and reported no tool can be written. Added the four verdict conjuncts.
2. `test_severity_calibration.py::test_an_already_subcritical_unproven_finding_still_blocks` failed. **Also correct** — its entry is at round 0. That test is the anti-vote property and it drove the age lock. I did **not** weaken it.
3. `test_falsifier_cannot_read_the_key.py` failed because it anchored on the *first* `"routing_history"` in the file and my reader now precedes the writer. **Assertions unchanged**; I made the anchor the actual append site (`e.setdefault("routing_history", []).append({`). Strengthened, not loosened — per the integrity directive I did not touch the oracle.

**reasoning** — Simplest sufficient: one predicate + one door + one reader + one log line, mirroring the founder's own already-wired, already-ruled 2026-10-02 pattern (`_integrity_violation_excluded` ⇄ `integrity_refused_criticals`). Additive: nothing disabled; the default `None` makes it byte-identical for every existing caller; the reader is wired to a caller and executed by tests. I deliberately did **not** widen `integrity_refused_criticals` — its scope is one *cause* and its name is quoted verbatim in `integrity_refused_reason` in every archived registry; folding a second cause in would make both report keys ambiguous about *why*. This is the one place simplest-sufficient points **away** from reuse.

**refutation** — (i) If an entry can legitimately reach UNCONFIRMED with zero instrument trace *and* a later round would still have served it, the 1-round lock is too short; show one archived case and the threshold must rise. (ii) If any field I don't test records instrument contact, the door is still too wide. (iii) If `ladder_unserved_findings` is ever read by a gate rather than a log, the exclusion becomes a closure and the fix is wrong.

**termination** — Done when `unverified_critical_count(round)` and `ladder_unserved_findings(round)` agree on the same predicate for every archived registry at every round (asserted, rounds 0–9), the advisory appears in the round log, and a real run converges with every excused finding named. **Not** done while any entry is dropped without being named.

**disagreement** — I expect the other seat to argue the door should be **closed entirely** and the ladder fixed to serve every UNCONFIRMED entry instead. That is the better *deep* fix and I did not attempt it; I think it is out of scope for one dispatch and the brief's own note (the sweep settled two and C0073 arrived in the same shape afterwards) says it leaks. I also expect disagreement on `LADDER_UNSERVED_MIN_AGE_ROUNDS = 1` versus reusing `exhausted_round_threshold`; I claim they answer different questions, and 8 (clamped 7) would release **nothing** here, so reuse is insufficient — measured, not argued.

---

## 1b — the integrity gate refuses a correct falsifier

**verdict: FIXED**

**fix** — `bench/falsifier_verify.py`, in `_interpreter_roots()` (line ~696). Every root was derived from `sys.*`/`site.*` of the **running** 3.13, so it described the harness only. Added six guarded (`os.path.isdir`) stdlib/site roots. Measured on this machine, not assumed:

```
harness : 3.13.3  /Library/Frameworks/Python.framework/Versions/3.13
spawned : 3.9.6 via /usr/bin/python3
  stdlib : /Library/Developer/CommandLineTools/.../Versions/3.9/lib/python3.9
  purelib: /Library/Python/3.9/site-packages
  usersite: ~/Library/Python/3.9/lib/python/site-packages
```
All three sit inside `_SANDBOX_DENY_REGIONS = ("~", "/Volumes", "/Library")`.

**Why extending `allow` is the right lever and cannot weaken the key defence** — this is the load-bearing check, and it is verified in code, not assumed. `_denied()` consults `_protected()` **first** and returns denial from it *even inside an allowed root*: *"the allowlist is a convenience, the protected set is the point."* The protected set matches by **digest**, not region, so it is untouched. New file `bench/tests/test_a_second_interpreter_is_not_an_integrity_violation_2026-10-12.py` asserts that ordering directly, so an inversion fails a test.

**falsifier** — `5 passed`; and the key-access suite `test_falsifier_cannot_read_the_key.py` → `41 passed`.

**reasoning** — The defect is an **incomplete allowlist**, not an over-strict policy. The "run and flag instead of refusing" option would gut the key-access defence (a HARD verification-integrity constraint) to fix a false positive. Correcting the allowlist removes the false refusal and leaves genuine key access refused — strictly additive, and it needs no founder ruling because it changes no policy.

**refutation** — If any added root can contain a scoring key, answer file or planted-defect manifest, the fix is unsafe. I assert the carve-out roots contain neither the repo nor `experimental_notes`. If `_protected` is ever moved after the allowlist check, this becomes a hole.

**termination** — Done when C0050's unmodified falsifier returns `CONFIRMED` rather than `INTEGRITY_VIOLATION` on a real run, with the key-access suite still green. I verified the mechanism and the suite; **I did not re-run C0050's actual falsifier** — that remains to confirm.

**Side-finding, reported not fixed (pre-existing, not mine):** `tempfile.gettempdir()` has long been in the allowlist, and a **sandboxed clone lives under the temp dir** — so `experimental_notes/` is reachable through that allowance in sandboxed runs. The protected set still holds (digest-matched). My test is scoped to the roots I added rather than silently widened to hide this. **This is the sharpest thing I found that nobody asked about.**

**disagreement** — The other seat may prefer querying each interpreter via subprocess over a declared list. More robust, but it spawns a process per verification and can fail; I chose the deterministic list. I expect genuine disagreement here.

---

## 2 — A19

**verdict: PREMISE WRONG on the remedy; RESOLVED ALREADY in code; the live defect is the record**

**fix** — `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, dated correction inserted after the A19 task marker (line ~567). **No code change.**

**falsifier** — I re-ran the other seat's claim myself rather than relay it, because it corrects the record he rules from:
```
flag=False: tristate=NO_SCORE sk=0.0
flag=True:  tristate=ESCALATE sk=0.0
```
A19 says, in capitals, *"STILL ADMITTED AT sk=1.0000 … identical to the correct prose fix."* **Never ADMISSIBLE, never 1.0000, at either setting.** The fixture's own comment (`:98`) preserves the same stale reading, so comment and entry agree with each other and disagree with the code. Confirmed separately: `20 passed`, and `_gateable_source` is **fence-dependent, not element-dependent** — `2+2 equals 5` in running prose is extracted by nothing.

**reasoning** — The entry's *conclusion* survives (the flag repairs the gates' substrate, not their threshold) but the number must be struck: "admitted at 1.0000" says the gate is actively fooled; "ESCALATE at 0.0" says it declines to judge. Different facts about the instrument; only the second is true. I did **not** fix `_gateable_source`: across measured outcomes S_k's reachable range on prose is `{REJECTED, NO_SCORE, ESCALATE}` with no ADMISSIBLE, because S_k grades whether a *fix* is safe, never whether a *claim* is true. A per-element extractor would add surface with no verdict path — the 11-times defect class.

**termination** — Done when the struck figure is gone, the fixture comment is corrected too, and he rules on `sk_score_prose_listings` as a harm guard only. His design point *("solving any computationally reducible elements within that prose")* is **still unmet** and belongs to the claim-checker corpus, not S_k.

**disagreement** — The other seat reported a better design was decided on 2026-09-30 and lost. I did not independently verify that and do **not** assert it. I expect disagreement on whether A19 can be closed at all without his ruling: I say no.

---

## 3 — this session's work

**verdict: PREMISE WRONG on the audit method; one CONFIRMED defect FIXED**

`git log --since=2026-10-11T12:00:00+01:00 --stat` **cannot run — no `.git` in the sandbox.** The "35 commits" figure is unverifiable here. Audited by mtime instead (60 `*.py` touched since 2026-10-11).

**"Additions nothing reaches" — PREMISE WRONG.** Both suspects are wired: `round_budget.project_optimal_rounds` and `human_review_trigger.assess` are imported in `_check_hardened_convergence` (`reference_runner_v3.py:9370`, `:9396`), which has a non-test caller at `:18030`. `assess()`'s 7 params match the call site's 7 kwargs. `compaction_task_boundary.py` exists, is registered live, and the repo copy is byte-identical.

**CONFIRMED defect — the test suite writes into the real delivered-output ledger.**

**fix** — `scripts/stamp_output_hash_2026-10-12.py`: new `_is_ephemeral(p)` + `import tempfile`, called from `main()`'s loop (the only caller of `record()` — no new flag, no new env var).

**falsifier**:
```
ledger rows BEFORE = 10
db3c23c86775  stamped  scratch_note.md
    not recorded (temporary file, not a delivered output)
LEDGER UNCHANGED BY A TEMP FILE: True
```
Plus 2 tests added to `bench/tests/test_every_output_carries_its_own_hash_2026-10-12.py` → `12 passed`.

**reasoning** — The second clause (`not under REPO`) is **load-bearing and measured, not defensive**: a sandboxed clone lives under the temp dir, so a naive temp-prefix guard would stop recording that clone's genuine outputs. I added the converse test for exactly that. Rejected `--no-record` / env-override designs: public surface whose only caller is a test, which is the defect class under audit.

**termination** — Done when a full green run leaves the ledger byte-identical and the 2 existing temp rows are pruned. **The pruning is not done** — needs his nod, as it edits a tracked delivery record.

**Reported, not fixed:** ledger dedup key is cwd-sensitive (`record()` dedups on unresolved `(digest, path)`; the morning report is already present under 2 spellings). A one-line `.resolve()` fixes it — **but I could not demonstrate the collapse in-sandbox** and state it as unproven rather than claim it.

**disagreement** — The other seat judged the morning-report test failures pure git-absence artefacts. I half agree: harmless in the real checkout, but a generator that *writes and stamps* a report asserting "rebuild it to reproduce this" while HEAD is the literal `unknown` should refuse, not emit. That deserves one ruling.

---

## 4 — the 21 parked items

**verdict: PREMISE WRONG on the count; NEEDS HIS RULING on the majority**

`grep -c '^## '` → **21**, so 21 is right for *headings* and wrong for the brief's "21 non-blocking items", three ways: heading 20 is a **self-declared BLOCKER** (contradicting the file's own preamble that blockers never appear in it), heading 5 carries **two** items (one closed), and 3 headings ask nothing. **Non-blocking = 20. Decisions actually owed to him = 13.** Same artefact class the brief warned of — a heading count quoted as a decision count.

**Already closed (do not re-litigate): 4 headings + 1 half** — Wolfram `0.1` (closed on his instruction 2026-09-28), Tailscale SSH stub (*"same decision as 10.2, not a second one"*), A8 3-way (*"superseded… do not answer this heading"*), committed-scripts-reached-by-nothing (*"RESOLVED 2026-09-11, all 6 wired"*), Stop hook (fixed and tested).

**Fixable now: 4.** Highest value is item 18 — `scripts/blocker_triage.py` implements 2 of its 3 questions, so an item whose own text says "NEEDS A POLICY RULING" returns a bare `PARK`, which `hooks/work_not_narrate.py:308` reads as "park it and carry on". Also: the preamble's false universal is **regenerated** by `blocker_triage.py:195`, so correcting only the `.md` leaves the generator reproducing it.

**fix: NO FILE WRITTEN for Item 4.** I ran out of budget after Items 1–3 and chose depth on the convergence blockers as the brief directed. These are specified but unapplied — I will not claim them as discharged.

**Coupling warning for whoever applies the A18 fix:** `bench/tests/test_capabilities_disabled_by_config_2026-09-10.py:265` pins the CITED set to exactly 3 arms and `:280` is a control expecting `UNEXPLAINED`. Adding `_hardened_gate_note` turns both red; they must change in the same commit, and the cited-set assertion must be **replaced with something non-vacuous rather than emptied** — otherwise the fix removes the test's teeth, which the additive standard forbids.

**disagreement** — I expect the other seat to classify more items as fixable-now than I do. On the A18 entry specifically, its sweep output contradicts the entry's text (`max_papers_per_round` is `[DOCUMENTED]`, not "unexplained"); I report that as the other seat's measurement and did not re-run it, so I do not assert it.

---

## Files written to the sandbox tree (harvest these)

| Path | Change |
|---|---|
| `bench/reference_runner_v3.py` | predicate, age-locked door, `LADDER_UNSERVED_MIN_AGE_ROUNDS`, stale docstring, paired reader, report wiring |
| `bench/tests/test_an_unserved_finding_cannot_block_for_ever_2026-10-12.py` | **new**, 18 tests |
| `bench/falsifier_verify.py` | interpreter carve-out in `_interpreter_roots()` |
| `bench/tests/test_a_second_interpreter_is_not_an_integrity_violation_2026-10-12.py` | **new**, 5 tests |
| `bench/tests/test_falsifier_cannot_read_the_key.py` | anchor made specific (assertions unchanged) |
| `scripts/stamp_output_hash_2026-10-12.py` | `_is_ephemeral` + `import tempfile` |
| `bench/tests/test_every_output_carries_its_own_hash_2026-10-12.py` | 2 tests added |
| `experimental_notes/CDSFL_MASTER_TASK_LIST.md` | A19 dated correction |

**Final regression, 12 files: `208 passed`.** Full suite not run (>8 min, per brief). Nothing auto-applied — all of this is suggested to you.

**Three things I want to flag as needing you, not the panel:** (1) whether a run may converge over a finding emitted in its *final* round — I say no and the gate now says no, which means round budgeting must account for last-round findings; (2) pruning the 2 junk ledger rows, since it edits a delivery record; (3) the pre-existing tempdir allowlist exposure in sandboxed runs.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 123 recorded tool call(s).

<!-- verbatim-begin: fable (panel clear_the_outstanding_2026-10-12) -->

All verification complete. Final report.

---

# Panel return — fable seat, 2026-10-12

**Files changed in the sandbox tree (harvestable):**
- `bench/reference_runner_v3.py` — Fix B (routing serves never-served findings) + Fix A (A4 docstring)
- `bench/falsifier_verify.py` — Fix C (spawned-interpreter roots, gated probe)
- `bench/tests/test_never_served_findings_enter_the_ladder_2026-10-12.py` — new, 4 tests
- `bench/tests/test_spawned_interpreter_falsifiers_are_not_refused_2026-10-12.py` — new, 4 tests

**Brief numbers re-executed, not trusted:** severities 0.7/0.6/0.45/0.50 — **verified** against `runner_state.json`. Interpreters 3.13/3.9 — **verified** on this machine (harness 3.13.3; `/usr/bin/python3` is 3.9.6). Wilson [0.0%, 4.2%] for 0/87 and [83.93%, 94.94%] for 99/109 — **both reproduce** via statsmodels. The 36.8%/63.2% replay split itself — **NOT verifiable here**: the sandbox has no `.git`, so commit `6c10fe4`'s message and the 87 archived reports behind it could not be re-executed. Treat those two percentages as still-quoted.

---

## 1a — Blocker counter vs release valve

**verdict** — PREMISE PARTLY STALE (the brief describes the 2026-10-03 code; the tree moved on 2026-10-06) + FIXED (docstring) + measurement answering his question.

The brief says the counter has "no severity test in its body." **It now does**: `bench/reference_runner_v3.py:2968-2970` restores it, dated 2026-10-06, gated on `severity_is_proven(e)` — a sub-critical is released only when its stated R_k **reproduces by tool recomputation** from its own stated inputs. The live instance **C0042 is CLOSED** in the archived registry (falsifier 1349 chars, verdict CONFIRMED) — it no longer blocks anything. What still blocks, measured by importing the real module and rehydrating the real `runner_state.json`: **A4 = 2, on C0066 (0.45, proof SKIP) and C0073 (0.50, proof SKIP)** — that is Item 1c's residual, fixed below. The run's `converged: false` is confirmed from `checkpoint.json`.

The docstring was stale in a *new* direction: it still claimed a bare `severity >= CRITICAL_SEVERITY_THRESHOLD` count. **fix** — `unverified_critical_count` docstring rewritten to state the actual rule and enumerate all four releases in body order.

**His question — paid run, or simulated run with the missing severity tests in place?** Measured: stamping `severity_proof: PASS` onto C0066/C0073 on the archived registry takes **A4 from 2 to 0**. So the convergence obstruction is specifically the *absence of R_k worked proofs*, which the comment at :2952 records as provable in 99/109 real cases (90.83%, Wilson re-verified above). My advice: **simulated run first** — it is the cheap test of whether the proof-demand loop (`_stamp_severity_proof`, feedback channel) actually elicits the proofs end-to-end with the serve-once fix in place; **then one paid run** for the blind measurement. The combination, subject to the simulated run passing — which matches his stated instinct of "whichever combination brings us closest, subject to testing, rather than assumption."

**falsifier** — `python3` replay of `runner_state.json` through the real `FindingRegistry` (output above: `A4 as archived: 2` → `A4 with proofs: 0`).
**refutation** — a pre-sweep registry replay showing C0042 still entering A4 under current code; or a proof-stamped replay that does not release.
**termination** — a run (simulated acceptable) reaches `converged: true` with A4 = 0 achieved through tool verdicts and proofs, not through exclusions.
**disagreement** — cc2 may argue the docstring should be shorter. I kept the release enumeration because the docstring's one-line staleness went unnoticed for 36 days precisely because it under-described the body.

## 1b — Integrity gate refuses the correct falsifier

**verdict** — FIXED, premise verified live.

Reproduced before touching anything: a falsifier spawning `/usr/bin/python3 -c "import json, ssl"` returned **INTEGRITY_VIOLATION on 13 stdlib bootstrap reads** (output above — exactly the structural refusal the record describes, because any falsifier for the unpinned-`python3` defect class must spawn the system interpreter).

**fix** — `bench/falsifier_verify.py`: new `_secondary_interpreter_roots()` (at the old `_interpreter_roots` site, line ~696) probes `/usr/bin/python3` and PATH's `python3` for *their own reported installation directories* (prefixes, site-packages, user-site, `sys.path`, the 3.9 zip-stdlib) and adds them to the allow list; `_interpreter_roots()` extends with it. This is **parity, not a new category** — the same directory classes already allowed for the harness interpreter. Refuse-on-denial is **unchanged** for everything else; protected scoring-key digests are checked exactly as before; discovery failure fails closed. The self-audit pin in `test_falsifier_cannot_read_the_key.py` correctly flagged my new launch site; I gated the probe through `scan_falsifier_source` in-body (fail-closed) rather than weakening the pin — weakening a test to pass is prohibited conduct.

**falsifier** — run above: spawned-interpreter falsifier now `REFUTED` (ran, clean exit) instead of `INTEGRITY_VIOLATION`; a `~/Desktop` read still refuses; the C0050 counterfactual (PEP 604 handed to the unpinned interpreter) **CONFIRMS** when the system python is pre-3.10 — pinned in `test_spawned_interpreter_falsifiers_are_not_refused_2026-10-12.py`, 4/4 pass; `test_falsifier_cannot_read_the_key.py` 45/45 pass.
**reasoning** — simplest sufficient: it removes exactly the false-refusal class with no policy change, so it does **not** need his refuse-vs-flag ruling. The broader "run and flag as a reporting metric" redesign (which the STUDY record's correction block anticipates) remains open to him but is not required to unblock this class — and keeping refusal is the conservative reading of the 2026-08-15 provenance gap.
**refutation** — a scoring key demonstrably readable through any added root; or a platform where the probe adds a non-interpreter directory.
**termination** — a C0050-class falsifier returns CONFIRMED/REFUTED on re-verification on this machine (it now does), and the forensics scan over a run using it reports no key access.
**disagreement** — cc2 may prefer the run-and-flag redesign (denials become a report metric, only protected-digest hits refuse). That is defensible and arguably cleaner, but it changes the gate's semantics for every falsifier and therefore *does* need his explicit ruling; mine doesn't. If he rules for run-and-flag, my fix composes with it (the roots stop ordinary spawns generating noise flags) — but per the composability standard, compose only if the combined form is measured better.

## 1c — Never-served findings block for life; the provenance question

**The tension, answered directly.** He is ruling on **provenance** — and the design that satisfies both the ruling and "no votes" is **already what the tree implements**: the thing restored on 2026-10-06 is *not* the raw model-assigned float. The gate releases a sub-critical only when `severity_is_proven` — the model's stated R_k **recomputed by a tool** from its stated inputs. That is a measurement, not an opinion, so "there are no votes in CDSFL" is not violated; and the worked proofs he ordered are the gate's own mechanism (`_stamp_severity_proof`, `severity_proof_status`). The removal's 36.8%-blocks-more measurement attacked the *raw float* (AUC 0.464, σ = 0.1419 against a 0.09 band) — that argument is sound and is **not** contradicted by the restore, because an unproven float still buys nothing. Provenance reversed, no-votes preserved, worked proofs kept: all three of his requirements are simultaneously satisfied by code already present. My verdict on that design: **SOUND**, by derivation above.

**The residual defect, fixed.** C0066/C0073 remained: born UNCONFIRMED, `escalated=False`, empty falsifier, zero verdicts — the routing loop's first line (`if not e.get("escalated"): continue`) hid them from the only mechanism that could produce the missing falsifier; the `exhausted` valve (≥0.7 **and** verdicts>0) and the proven-sub-critical release (proof is SKIP) can never fire. Reproduced against the real module: a C0066-shaped entry, `served == []`, A4 = 1, no exit.

**fix** — `bench/reference_runner_v3.py`, `_apply_routing` loop head: a `_never_served` predicate (UNCONFIRMED + no falsifier code + no verdict + no verdicts + no routing_history + not error_routed) admits the entry into the **existing** ladder exactly once; the appended `routing_history` is the one-attempt guard. This is the founder's own 2026-08-22 equipment-failure class ("the instrument produced no reading") taken one step earlier: no instrument was ever written. It is a **service, not a release**: if the ladder resolves it, A4 clears through a tool verdict; if nothing resolves it and the severity stays unproven, it keeps blocking — which is the honest state under TOOLS DECIDE. I deliberately did **not** add an automatic release for served-but-unresolved findings: that would let a run converge over a finding no tool ever decided, which is the silent closure his "clean honest convergence" objective forbids.

**falsifier** — `test_never_served_findings_enter_the_ladder_2026-10-12.py`, 4/4 pass: served exactly once; tool resolution → A4 = 0; ERROR-class routing unchanged; already-served entries don't re-enter. Regression: 75 + 245 adjacent tests pass.
**Second defect in the record** (threshold 8 vs max age 7): **RESOLVED ALREADY** — the announced clamp at `reference_runner_v3.py:4241-4251` exists. Cross-checked independently: Wolfram Language (local Engine) `Reduce[...] → False` confirms the age condition is unsatisfiable when T > R−1, agreeing with the recorded z3/NumPy/SymPy results.
**refutation** — a registry shape where `_never_served` matches an entry that *was* served (I found none: every served path writes routing_history or a verdict); or the simulated re-run still livelocking on this class.
**termination** — a re-run of the study arm in which every A4-counted finding shows either a tool verdict, a PASS/WARN proof, or a routing_history record — nothing blocking that was never served.
**disagreement** — cc2 may propose releasing served-but-unresolved sub-criticals to HIL via `irreducible_escalation` (guaranteed convergence exit). I considered and rejected it as one step too loose without his ruling: it converts "nothing could test this" into "stop counting this," and the integrity-exclusion precedent shows such exclusions need a paired named reader. If he wants a guaranteed exit, that is the shape — but it's his call, not ours.

## 2 — A19

**verdict** — NEEDS HIS RULING (the `sk_score_prose_listings` flag; Section P makes the last step explicitly his). Evidence runs green; premise of "a better design was lost" is **wrong** — it was decided and recorded.

**(a) Objections**: round 13 (2026-09-11) raised seven. Both seats independently found F1, the baseline-substrate defect ("the gate that could not fail moved from e4 to e3" — `_capture_baseline` subtracted listings-after from whole-prose-before; cc2 measured baseline 311 vs gate 4). **Answered**: fixed at `reference_runner_v3.py:12810-12840` with the shared-substrate test. Also answered: fence-shape blindness (all 7 shapes, `_MD_PY_FENCE_ANY`:12090), delete-everything escape (`g0_code_retained`:13075), the vacuous pinning test (repaired by the fable seat). **Recorded-and-deliberately-unfixed** (founder rulings, not drops): E_min > S\* on clean Python targets; `sk_s_floor = 0.0`. **One genuinely unanswered residual**: the v2 runner's `_capture_baseline` at `bench/reference_runner.py:2663` still carries the identical round-13 defect — zero `_gateable_source` occurrences in that module. Flagged for his report; I did not patch a legacy runner unprompted.

**(b) A better design was decided, in three recorded steps, not lost**: veto-only prose scoring (2026-09-22, `_prose_one_sided`:13270 — gates may convict, never admit, after the flag-on form was measured admitting all 5 harmful acceptance fixes); the e2-docstring corrections (2026-09-30/10-02); and the **claim ledger** (2026-10-01, `bench/claim_ledger.py` — "S_k classifies neither target nor element — it classifies a FIX"; per-claim falsifiers, `informative_only=True`), built on his "Build it, apply it and test it" ruling.

**(c) Does it work — executed**: the A19 evidence suite — substrate-sharing, one-sided prose gates, runner reachability, prose-listing scoreability — **82/82 pass** (output above).

**(d) Is it the whole solution? No.** Three gaps, stated plainly: per-element admissibility as he specified it ("solve the reducible elements within the prose") is *not* what is built — `_gateable_source` concatenates listings into one blob, and veto-only means a reducible element can only convict or abstain, never be solved-and-admitted; `e2_regression` is still unavailable on prose; and the archived `SHELL_INJECTION_FIX` exploit is still admitted at sk=1.0 with the flag on (bandit rates `shell=True` LOW), which the record itself calls the strongest argument for the flag staying OFF. The claim ledger is the designed path to the whole solution and is currently informative-only. **The decision he owns**: flag ON (veto-only form) or OFF, and whether to promote the claim ledger from informative to load-bearing.

**disagreement** — cc2 may read the veto-only redesign as having superseded the per-element requirement. It has not: veto-only is a safety posture, not the "solve the reducible elements" capability he described. Both readings should go to him unmerged.

## 3 — This session's 35 commits

**verdict** — PARTIALLY VERIFIABLE, and I must say so plainly: **the sandbox has no `.git`**, so `git log --stat` cannot run here and the commits *as commits* (messages, authorship, the 35-count) are unauditable from this seat. What was auditable, I executed: all 7 named deliverables exist at their stated paths with plausible session timestamps; `round_budget.py` and `human_review_trigger.py` are **wired** into `reference_runner_v3.py` (:9411, :9437 — not additions nothing reaches) and each has a dedicated test; **50/50** of their tests plus the seat-serialisation test pass. `compaction_task_boundary.py` exists but lives outside the repo tree (`~/.claude/hooks/`), so it is outside the harvest and its test coverage is not assessable from this sandbox — the next seat with repo access should audit it there. **fix** — NO FILE WRITTEN: nothing I executed failed. **refutation** — a git-visible audit finding a commit whose claims its named evidence doesn't establish (the pattern Item 4's audit already found 24 times in older DONE entries — prior probability here is not negligible). **termination** — a seat with `.git` access replays each commit's stated measurement. **disagreement** — cc2, if given a git-bearing sandbox, may legitimately find what I structurally could not; my "nothing failed" is bounded by what was reachable, and I flag that bound rather than claim a clean bill.

## 4 — The 21 parked items

**verdict** — triaged; per his instruction, items needing him are reserved for his closing report. **Already closed, say so and move on (4):** items 11 (Tailscale duplicate, merged), 12 (A8 superseded), 15 (orphan scripts, all 6 wired), 19 (Stop hook parked on his instruction). **Mechanically fixable now (4), no ruling needed:** 1 (A17 tuple-guard name matching in `scripts/supersession_check.py`), 2 (missing `_max_papers_per_round_note` in 3 exp56 configs — and its "no note" premise for `hardened_gate_enabled` is stale: the note now exists), 3 (A13/A14 — premise likely stale: current dispatch logs show 4 per-seat sandboxes, not one shared; run the recorded falsifier before any fix), 18 (`blocker_triage.py` missing the DECISION predicate its own entry specifies). I did not write these four — depth on Item 1 was the instructed priority — they are small, specified, and safe for the next free-panel pass. **Need his ruling (13):** 4 (paid dispatch of exp50/51), 5-W1 (Wolfram MCP licence), 6/7/8/9 (the four directive-composer defects — all held back solely because fixing them changes every model's prompt and invalidates replay; they should go to him as **one batched replay-invalidation decision**, not four), 10 (Tailscale SSH), 13 (A8 re-pointing), 14 (Desktop superseded copies — now **two** files, premise grown), 16 (DONE-audit scope; recorded recommendation is option 2), 17 (177 untracked log paths — **stale: now 489**, re-measure before ruling), 20 (CLI OAuth — only he can log in), 21 (memory-index checker formatting). **disagreement** — cc2 may fix the four mechanical items inline; fine if done, but each needs its own executed falsifier, and item 3's should be *run* before any code changes since its premise looks stale.

---

**Standing note on this seat's own work (refutation invited):** every code change above is additive (no feature removed; both new entry points wired and executed by committed tests), and each carries a before/after falsifier executed in this session: baseline reproduced → fix applied → falsifier re-run → 8 new tests + ~500 adjacent tests green. What would overturn the whole return: evidence that `severity_is_proven`'s R_k recomputation can be gamed by a model stating self-consistent but wrong inputs — that would make the restored gate a vote in proof's clothing, and it is the one place I'd direct the next adversarial pass.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/clear_the_outstanding_2026-10-12/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
