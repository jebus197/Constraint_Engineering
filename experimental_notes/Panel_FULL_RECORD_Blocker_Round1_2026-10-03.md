# Panel round 1: which repair clears the A4 convergence blocker

Record written 2026-10-04T02:56:38+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. study_run1b_2026-10-03 ran 8 rounds, produced 75 findings and did not converge. Exactly 2 registry entries held the A4 blocker: C0066 at severity 0.45 and C0073 at 0.50, both UNCONFIRMED with verdicts == [], no routing_history and no falsifier_code, and both carrying computed_evidence with kinds ['reasoned_withdrawal']. Two independent analyses had reached DIFFERENT root causes, and the seats were asked to adjudicate by execution rather than to agree.

POSITION A, put to them: the exhausted valve still gates release on severity >= 0.7 while unverified_critical_count has had no severity test since founder ruling 23 of 2026-09-06. Measured over 65 archived runs, 22 carry at least 1 permanently blocked entry, 33.8462%, Wilson [23.5335%, 45.9616%]; 107 of 150 blocking entries are blocked by the severity clause alone; severity is immutable, 0 of 523 proof histories showing more than 1 distinct value.

POSITION B, put to them: pre-pass 2 of _update_finding_statuses reopens an UNCONFIRMED entry on any later verdict and contains 0 occurrences of "severity". It FIRED in this run, console.log line 948, REOPEN C0042, on an entry at severity 0.6 with the same shape. So the discriminating variable is verdicts == [], not severity.

WHAT THE SEATS FOUND. Both measured, independently and in separate sandboxes, that POSITION A ALONE IS A NO-OP: cc2 swept rounds 8, 9, 20 and 100, fable swept to round 40 across 4 textual variants, and the blocker count never moves, because the valve also requires len(verdicts) > 0 and both findings have none. cc2's phrasing: "an addition nothing reaches". cc2 additionally found that hil_has_computed_evidence occurs exactly once in the whole repository, at reference_runner_v3.py line 14231, as a WRITE, with zero reads anywhere.

THE DISAGREEMENT, PRESERVED RATHER THAN SMOOTHED. cc2 returned position B with composes false, proposing a _handed_to_human predicate plus a fifth door in the counter plus handed_to_human_ids so that exclusion implies reporting, mirroring the existing _integrity_violation_excluded pattern; measured A4 2 to 0 and the gate False to True at round 8, with 12 of its 14 tests failing when the fix is reverted, 85.7143%, Wilson [60.0586%, 95.9906%]. fable returned BOTH with composes true, proposing that the valve be severity-free for UNCONFIRMED only and that has_reviews count computed_evidence as well as verdicts; measured A4 reaching 1 at round 13 and 0 at round 15, and refusing on principle to let a repair change an archived verdict.

BOTH SEATS ALSO REFUTED THE BRIEF'S OWN FRAMING, unprompted: draining A4 to 0 and calling the real gate at round 7 still returns False on the COUNT side, novel_crit_recent [1, 0, 0] against gamma_alt_consecutive_zero_crit 3. The run's non-convergence was overdetermined. fable further corrected the brief's gamma figure: the gate receives gamma_critical 0.732, and 0.4274 is the all-severity series.

WHAT WAS DONE WITH THE FINDINGS. Neither repair was adopted. A third fact, established after both seats reported and by AST attribution, decides it: reasoned_withdrawal is written at exactly 1 site, line 7514, inside _post_convergence_sweep, which runs after converged is assigned. So the evidence BOTH repairs read does not exist until after the verdict that needs it, and neither would change a live run. The founder's own proposal was implemented instead: record_in_round_withdrawals now records the same evidence DURING the round, as a metric that blocks nothing, per his ruling of 2026-10-04. His words: "it should simply be a recorded metric, and should not block anything."

COST AND CONFINEMENT. 2 free seats, cc2 and fable on the Max subscription, 0 paid dispatches, verified before launch. Each seat worked in its own disposable copy; both copies were kept and are listed in sandbox_manifest.json. Seat-written evidence was harvested to experimental_notes/seat_evidence/panel_blocker_round1_2026-10-03, 2 files from cc2 and 3 from fable, which exist nowhere else a clone can reach. An earlier attempt at this review asked for 9 repairs at once and both seats hit the 1800-second dispatch cap having written 0 files; the narrow brief that replaced it was 1224 words and both seats finished in 903 and 935 seconds.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel round 1 — why 2 findings block convergence, and which repair is right

## The question

`study_run1b_2026-10-03` ran 8 rounds and did not converge. `gamma_critical` finished at 0.4274
against the 0.30 threshold, so the decay curve HAD flattened; the gate was blocked on its other
side by the A4 fail-safe. **Exactly 2 registry entries hold it: C0066 (severity 0.45) and C0073
(severity 0.50).** Both are UNCONFIRMED with `verdicts == []`, no `routing_history` and no
`falsifier_code`.

Two independent analyses reached DIFFERENT root causes. Decide which survives execution, whether
they compose, and deliver the repair. **You are not asked to agree with the other seat.**
Disagreement is kept as information.

Artefacts under review: `bench/reference_runner_v3.py`, and as evidence
`bench/logs/study_run1b_2026-10-03_20261003T100439Z/runner_state.json` and that directory's
`console.log`.

**Position A — the `exhausted` valve's severity clause.** `_update_finding_statuses` gates release
on `severity >= 0.7` (around line 3933). `unverified_critical_count` (around line 2747) has NO
severity test, by founder ruling 23 of 2026-09-06, because `severity` is a float the SOURCE MODEL
assigns: AUC 0.464 against 0.5 for chance in the deciding band, per-assignment sigma 0.1419 over
273 duplicate pairs, against a band 0.09 wide. So the counter stopped consulting the float and the
release path still consults it. Measured over 65 archived runs: 22 carry at least 1 permanently
blocked entry, 33.8462%, Wilson [23.5335%, 45.9616%]; 150 such entries in total, of which 107 are
blocked by the severity clause alone. Severity is immutable — 0 of 523 entries with a
`severity_proof_history` show more than 1 distinct value. Proposed repair: remove the valve's
severity clause. Additive, since nothing is disabled and a release path is widened.

**Position B — the missing verdict, and a severity-free door that already works.** Pre-pass 2 of
`_update_finding_statuses` (around lines 3943 to 3953) reopens an UNCONFIRMED entry to OPEN when
`rounds_in_status >= 2` and any verdict arrived after the status change. It contains 0 occurrences
of "severity". **It fired in this run**: `console.log` line 948 reads "REOPEN C0042: new evidence
after UNCONFIRMED", on an entry at severity 0.6 with no falsifier, no `routing_history` and
`escalated` False — the same shape as the 2 blockers. It was freed by 1 verdict row. So the
discriminating variable is `verdicts == []`, not severity, and the question becomes why no model
files a verdict on these 2. Position B holds that widening the valve treats a symptom.

**What each blocker actually carries, because it bears on the answer.** C0066's `computed_evidence`
holds `{'kind': 'reasoned_withdrawal', 'by': 'CC2-SIM', ...}` plus a concrete `proposed_fix`, and
its status stayed UNCONFIRMED — a withdrawal recorded by one mechanism and read by none. C0073's
`merge_blocked_reason` is "model-declared DUPLICATE action; no tool verdict" and its
`merge_candidate_of` is C0069, which is CLOSED, `verified` True, `falsifier_verdict` CONFIRMED —
the no-voting rule correctly refused a model's say-so that it is a duplicate, and nothing produces
the tool verdict that would settle it.

## Rulings that are NOT open to you

- **Severity is not a vote.** Do not propose putting a model-assigned float back in charge of
  convergence. Reason about the measurement, not about who ruled it.
- **Worked proofs are the agreed replacement.** `bench/dm/_rk_proof.py` plus
  `_validate_rk_computation` recompute R_k from stated parameters. A recomputation that survives is
  a fact, not an opinion.
- **An UNCONFIRMED finding handed to the human is a designed terminal state**, not a failure. The
  target is minimal-HIL, never zero-HIL.
- **The closing sweep must never rescue a failed run.** `converged` is assigned only before it, and
  a sweep that could flip a verdict would make convergence unfalsifiable.

## Use the harness

Form your answer by RUNNING things. Rehydrate that registry through the real `FindingRegistry` and
CALL `unverified_critical_count`, `contested_count`, `irreducible_queue_count` and
`_update_finding_statuses` on it. Call `_check_gamma_alt_convergence` to see what the gate does with
your repair in place. Do not read the source and infer behaviour: a test that asserts on SOURCE TEXT
shows only that a module describes itself consistently, and 4 defects in this project were found by
executing 2 forms against each other where reading found none.

Every proportion carries a confidence interval (Wilson), and every statistic is cross-verified with
a second tool — scipy with statsmodels, or NumPy with mpmath. A number with no producing script is
a claim about evidence, not evidence. Digits, never words.

## Produce a fix, test it, deliver it as a file

A finding without a fix is half an answer, and a fix without a runnable falsifier you have EXECUTED
is a hypothesis. Apply the standards: the SIMPLEST SUFFICIENT repair; ADDITIVE in both directions,
so never disable a mechanic and never add a branch nothing reaches; and COMPOSABILITY — compose A
and B only where the composition demonstrably beats EACH alone, and prefer the single arm where one
suffices.

**Write your fix INTO the sandbox repository tree at its real path**, as a file. A fix left in prose
or in scratch space is destroyed at teardown and has not been delivered. Report the command you ran
and the output you saw, including the failure you saw BEFORE the fix. Include a mutation check:
revert your fix, re-run your own test, and name which assertions fail. A test that still passes with
the fix reverted proves nothing.

**Scope discipline. This round is ONLY the question above.** A previous attempt at this review asked
for 9 faults at once and both seats hit the 1800-second dispatch cap having written 0 files. Answer
this one question completely rather than many partially.

## What would refute you

State, before you conclude, the specific evidence that would overturn your own answer. A verdict
with no refutation condition is an opinion and will be discounted.

## Output shape

Wrap the machine-readable part between `<<<CDSFL_ANSWER_BEGIN>>>` and `<<<CDSFL_ANSWER_END>>>`.
Prose outside those markers is read by a human and parsed by nothing. Fields:

- `position` — A, B, BOTH or NEITHER, for which root cause survives execution.
- `evidence_for_position` — what you RAN and what it printed.
- `composes` — true or false, with the measurement. If true, show the composition beating each arm
  alone; if false, name the single arm that suffices.
- `root_cause` — the mechanism, with file and line.
- `fix_path` — the real repository path you wrote your fix to.
- `fix_rationale` — why it is the simplest sufficient repair, and what it adds rather than removes.
- `falsifier_path`, `falsifier_command`, `falsifier_output` — the test, the command, the output.
- `mutation_check` — which assertions fail when the fix is reverted.
- `a4_before` and `a4_after` — `unverified_critical_count()` on that registry, before and after your
  repair, obtained by CALLING it.
- `gate_after` — what `_check_gamma_alt_convergence` returns with your repair in place, and whether
  the run would then converge. State plainly if it would not, and why.
- `figures` — every number you quote with the path of the script that produced it.
- `refutation_condition` — what would overturn you.
- `disagreement` — your strongest disagreement with this brief's framing, including with its
  measurements. The brief is not authoritative; challenge its figures where you think they are wrong.

## Termination

Stop when every hard assumption has been tested and a further pass produces no new above-threshold
finding — this project's own diminishing-returns criterion. A finding is above threshold if missing
it could cause a real-world failure, an unsafe condition or a wrong convergence verdict. Say how
many passes you ran. Do not nitpick and do not police style.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 47 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_blocker_round1_2026-10-03) -->

Four passes run. Three files delivered into the real tree.

**What execution decided.** Position A's repair is inert: with the `severity >= 0.7` clause deleted from the `exhausted` valve, A4 stays at **2** on study_run1b's own registry at rounds 8, 9, 20 and 100 alike — because the valve *also* requires `has_reviews = len(verdicts) > 0`, and both blockers have `verdicts == []`. The valve sets `exhausted = False`, not True. Position A is an addition nothing reaches — this project's #1 confirmed-defect class, 11 of 11 since 2026-08-01.

Position B's discriminating variable is right, and its *cause* is determinate rather than behavioural: all four of A4's pre-existing release doors are produced by machinery gated at `severity >= 0.7`. Executed, not read: `_irreducible_queue_split` returns `(0, 0)` for a sub-critical carrying `irreducible_escalation` and `(1, 0)` for the same entry at 0.9; the valve returns `exhausted=None` at 0.5 and 0.69, `True` at 0.70 and 0.9. Ruling 23 removed A4's *own* severity clause and gave the population it thereby added **no reachable door**.

**The fix is not a severity carve-out.** `_record_computed_evidence` writes `entry["hil_has_computed_evidence"] = True` at line 14231 — **1 write site, 0 read sites in the entire repository**. That is the machine's own record that an entry is a human decision (founder ruling 2026-08-03: "stays open, stays critical, stays a human decision"), and A4 was counting those entries as *pending machine verification*. I wired the reader, behind four conjuncts a broken instrument cannot satisfy, and paired it with a report line that fires in the real round-loop path.

**I disagree with the brief's central premise, and it is measured.** "Exactly 2 registry entries hold it" is false. With A4 at 0 the gate *still* refuses at round 7 — `novel_crit_recent=[1, 0, 0]`, two consecutive zero-critical rounds against `gamma_alt_consecutive_zero_crit = 3`. A4 was necessary, not sufficient; the run needed a 9th round it never had (`max_rounds = 8`). Also: `gamma_critical` finished at **0.7323**, not 0.4274. 0.4274 is `gamma_all`. The brief's *statistics*, by contrast, all reproduce exactly (22/65, 58/86, 82/273) across statsmodels, mpmath and Wolfram.

<<<CDSFL_ANSWER_BEGIN>>>
```yaml
position: B

evidence_for_position: |
  Producer: scripts/a4_handoff_figures_2026-10-03.py (written into the tree).
  All numbers below are return values of shipped functions on a registry
  rehydrated via the real FindingRegistry.from_dict.

  [1] POSITION A, EXECUTED ALONE (severity clause deleted from the exhausted
      valve in a mutant copy of the module, handoff stamp stripped so A is
      measured in isolation):
        round=  8: A4=2  C0066.exhausted=False  C0073.exhausted=False
        round=  9: A4=2  C0066.exhausted=False  C0073.exhausted=False
        round= 20: A4=2  C0066.exhausted=False  C0073.exhausted=False
        round=100: A4=2  C0066.exhausted=False  C0073.exhausted=False
      A4 NEVER MOVES. The valve's other precondition `has_reviews =
      len(verdicts) > 0` is False for both blockers, so the valve writes
      exhausted=False. Position A's repair is an addition nothing reaches.
      It also could not fire on age: exhausted_round_threshold=8 (declared
      config) against ages 7-5=2 and 7-7=0.

  [2] POSITION B's DISCRIMINATING VARIABLE, confirmed. Both blockers:
        C0066: sev=0.45 verdicts=0 routing_history=False falsifier_code=False
               hil_stamp=True kinds=['reasoned_withdrawal']
        C0073: sev=0.50 verdicts=0 routing_history=False falsifier_code=False
               hil_stamp=True kinds=['reasoned_withdrawal']
      Both pre-pass 2 (needs a verdict later than the status change) and the
      exhausted valve (needs len(verdicts)>0) are keyed on verdicts. Neither
      is reachable with verdicts == [].

  [3] WHY NO MODEL EVER FILES ONE -- B's open question, answered by execution
      rather than by behaviour. Every pre-existing A4 door sits behind
      severity >= 0.7:
        _irreducible_queue_split({sub-critical + irreducible_escalation}) = (0, 0)
        _irreducible_queue_split({same entry at severity 0.9})            = (1, 0)
        exhausted valve, one tick at round 20, verdicts present:
          severity 0.5  -> exhausted=None
          severity 0.69 -> exhausted=None
          severity 0.70 -> exhausted=True
          severity 0.9  -> exhausted=True
      Ruling 23 removed A4's own severity clause, so A4 counts a population
      for which no door is reachable. Permanent block by construction.

  [4] THE UNREAD STAMP. grep over the whole repository for
      `hil_has_computed_evidence`: 1 hit, reference_runner_v3.py:14231, a
      WRITE. Zero reads anywhere (bench/*.py, bench/dm/*.py included).

  [5] COUNTERS on the archived registry, before the fix:
        A4=2 | irreducible_queue=0 | contested(8,excl=True)=0
        contested(8,excl=False)=1 | open_crit_high=0
        undemonstrated_subcritical_ids=['C0066','C0073']
        integrity_refused_criticals=[]
      Note the already-shipped contradiction: the same two ids the runner logs
      as "residual queue (un-demonstrated sub-criticals, NON-GATING)" are
      exactly the two A4 gates on.

composes: false
composes_measurement: |
  Position A contributes nothing measurable in isolation (A4 = 2 at every
  round tested, items [1] above), so a composition A+B equals B on this state
  by construction -- there is no demonstrated advantage over B alone, which is
  what the founder's composability rule requires before composing. It fails
  the additive standard in the second direction too: A's widened branch would
  be a branch nothing reaches for this population. SINGLE ARM THAT SUFFICES:
  the B-side repair alone (the recorded-handoff door), measured A4 2 -> 0 and
  gate False -> True at round 8.
  Deliberately NOT composed in: the obvious one-liner `if severity <
  CRITICAL_SEVERITY_THRESHOLD and falsifier_verdict != "CONFIRMED": continue`,
  i.e. keying A4 on undemonstrated_subcritical_ids()' own predicate. It would
  also have drained A4 to 0 here, in 1 line and with the paired report already
  wired -- but it puts the model-assigned float back in charge of convergence,
  which is refused. Measured cost of that arm: sigma 0.1419 against a deciding
  band 0.09 (ratio 1.5767 -- noise exceeds the band by 57.67%), 82/273 =
  30.0366% of duplicate pairs straddling 0.7. A defect scored 0.68 by one
  model would be released and 0.72 by another would keep blocking.

root_cause: |
  bench/reference_runner_v3.py, FindingRegistry.unverified_critical_count
  (the A4 fail-safe, body lines ~2833-2945 after the fix; the door inserted at
  line 2931).

  MECHANISM. A4's contract is "candidates the system gave up on WITHOUT
  verification ... the convergence count path must not accrue while any of
  these are PENDING". Its four release doors are each produced only by
  machinery gated at severity >= CRITICAL_SEVERITY_THRESHOLD:
    (1) irreducible_escalation  -- _apply_routing, line 6763 skips sev < 0.7
    (2) exhausted               -- _update_finding_statuses pre-pass 1, line
                                   ~3932 requires sev >= 0.7 AND verdicts > 0
    (3) _integrity_violation_excluded -- needs a falsifier verdict, from the
                                   critical-only falsifier gate
    (4) falsifier_code + CONFIRMED    -- same critical-only gate
  Founder ruling 23 (2026-09-06) removed THIS counter's own severity clause.
  Correct on its own terms, and its safety argument held (it blocks a strict
  superset). What was not checked is that the newly-counted population can
  reach no door at all. So an UNCONFIRMED entry below 0.7 blocks A4 for the
  life of the run; the loop waits on an event no mechanism will ever produce
  and the run burns to max_rounds. study_run1b's own report records the
  symptom: stop_reason = "UNRECORDED_STOP (the round loop exited by a path
  that names no reason)".

  AND THE RECORD THAT WOULD HAVE SETTLED IT WAS UNREAD.
  _record_computed_evidence (line 14201) sets
  entry["hil_has_computed_evidence"] = True at line 14231 -- the machine's own
  stamp that this entry is a human decision, by the founder ruling of
  2026-08-03 ("the finding stays open, stays critical, stays a human
  decision"). That key had 1 writer and 0 readers in the entire repository.
  Both blockers carry it, with kind='reasoned_withdrawal'. A4 was counting as
  "pending machine verification" two entries the machine had already booked to
  a human. That is not a pending verification; it is the designed terminal
  state.

fix_path: bench/reference_runner_v3.py

fix_rationale: |
  THREE PIECES, the file's own established pattern for this exact requirement
  (one predicate, N readers, excluded-implies-reported -- as
  _integrity_violation_excluded / integrity_refused_criticals already do):
    1. `_handed_to_human(e)` module-level predicate + HANDOFF_EVIDENCE_KINDS,
       inserted immediately before _integrity_violation_excluded (line ~2163).
    2. A fifth door in unverified_critical_count: `if _handed_to_human(e):
       continue` (line 2931), plus FindingRegistry.handed_to_human_ids()
       keyed on the SAME predicate so the exclusion and the report cannot
       drift.
    3. One `_log` line in _evaluate_gate_conditions beside the existing
       residual-queue line. PROVEN REACHABLE: calling the real
       _evaluate_gate_conditions at round 14 printed
         HANDOFF: 2 finding(s) excused from the A4 blocker because the machine
         recorded them as a human decision and no instrument output is
         pending: C0066, C0073. The claims remain UNTESTED and HIL review is
         required (minimal-HIL, never zero-HIL).

  SIMPLEST SUFFICIENT. One skip in the counter that is wrong, keyed on a flag
  the machinery already writes. No new config key, no new state, no new halt
  path, no second counter, nothing rewired. The elaborate alternatives were
  measured and rejected: widening _irreducible_queue_split to carry
  sub-criticals cannot halt this run either (queue would be 2 against
  max_irreducible_queue = 2, and the alarm tests `>`), and a per-round
  A4-persistence alarm is new config + new state + new halt wiring for an
  outcome one skip already produces.

  ADDITIVE IN BOTH DIRECTIONS. Nothing is disabled: all four existing doors,
  ruling 23's severity-free counting, the valve, the integrity carve-out and
  the irreducible queue are untouched; 143 pre-existing tests over the A4,
  exhausted-valve, gamma-alt, severity-proof, key-access and
  post-convergence-settle paths pass unchanged. And the addition is reached:
  it fires on the real archived registry through the real counter and the real
  gate path, with a log line that executed.

  SEVERITY IS NEVER READ. Executed, not asserted on source: the predicate's
  verdict is invariant over all 101 severities in {0.00, 0.01, ..., 1.00}, and
  it is run against a dict subclass whose .get raises on the key "severity".
  The door releases a severity-0.95 entry of the same shape identically --
  stated in a test so no later reader mistakes it for a sub-critical carve-out.

  WHY IT CANNOT CAUSE A FALSE CONVERGENCE. Four conjuncts, each of which a
  broken instrument fails: the hil stamp (written only when a computation
  RETURNED an answer); a kind in {reasoned_withdrawal,
  critical_refuted_evidence_recorded} -- `discrimination_control:*` is
  excluded BY KIND precisely because NON_DISCRIMINATING means the instrument
  is broken, which is the 2026-09-09 hazard; verdicts == [] and no
  routing_history (anything in play is untouched); empty falsifier_code
  (anything with a test is untouched). A wholesale routing failure produces
  entries with EMPTY computed_evidence -- those keep blocking. Verified over
  400 randomised registries: A4_with_door <= A4_without_door in every trial,
  0 exceptions.

falsifier_path: bench/tests/test_a4_handoff_door_2026-10-03.py

falsifier_command: |
  python3 -m pytest bench/tests/test_a4_handoff_door_2026-10-03.py -q -p no:cacheprovider
  python3 scripts/a4_handoff_figures_2026-10-03.py

falsifier_output: |
  BEFORE THE FIX (the failure I saw first, from /tmp probe through the real
  FindingRegistry):
      entries: 75
      A4 unverified_critical_count   = 2
      irreducible_queue_count        = 0
      contested_count(8, excl=True)  = 0
      A4 BLOCKERS: [('C0066', 0.45, 0, True, ''), ('C0073', 0.5, 0, True, 'C0069')]
  and with Position A applied, still:
      round=  8: A4=2 ... round=100: A4=2   (exhausted=False on both)

  AFTER THE FIX:
      $ python3 -m pytest bench/tests/test_a4_handoff_door_2026-10-03.py -q
      ..............                                                   [100%]
      14 passed in 0.65s

  REGRESSION (targeted, not the full suite):
      $ python3 -m pytest bench/tests/falsifier_carveout_drains_a4_2026-10-03.py \
          bench/tests/test_a4_scope_guards_2026-10-03.py \
          bench/tests/test_an_unobserved_refusal_keeps_a4_blocking_2026-10-03.py \
          bench/tests/test_one_predicate_excludes_and_reports_2026-10-02.py -q
      28 passed in 0.61s
      $ python3 -m pytest bench/tests/test_exhausted_valve_can_fire_2026-09-17.py \
          bench/tests/test_exhausted_valve_reaches_its_readers_2026-09-09.py \
          bench/tests/test_gamma_alt_convergence.py \
          bench/tests/test_a4_verifier_failsafe.py \
          bench/tests/test_key_access_decoupled_from_convergence_2026-10-02.py \
          bench/tests/test_severity_proof_2026-09-07.py \
          bench/tests/test_panel_found_severity_defects_2026-09-07.py \
          bench/tests/test_post_convergence_settle.py \
          bench/tests/test_tool_loop_exhaustion.py -q
      143 passed in 5.05s

mutation_check: |
  Reverted all three pieces (predicate block, counter door + handed_to_human_ids,
  log line) by script; AST OK; `_handed_to_human` and `handed_to_human_ids`
  absent from the file. Re-ran my own test:
      12 failed, 2 passed in 0.68s
  FAILING assertions (12 of 14 = 85.7143%, Wilson [60.0586%, 95.9906%]):
    test_predicate_exists_and_is_severity_free            AttributeError
    test_door_drains_a4_on_the_real_run                   A4 == 0 -> got 2
    test_gate_after_the_door_round7_blocks_on_the_COUNT_side_not_a4
                                                          "A4" not in reason
    test_gate_after_the_door_converges_at_round8_and_a4_is_the_decider
                                                          conv_fixed is True
    test_door_stays_shut_for_every_dead_instrument_shape  x6 (AttributeError)
    test_door_is_severity_blind_for_a_critical_too        A4 == 0 -> got 2
    test_excluded_implies_reported_randomised             AttributeError
  PASSING ON REVERT, BY DESIGN -- and this is the point, not an omission:
    test_archived_blockers_are_the_two_named              (facts about the state)
    test_position_a_severity_clause_removal_does_not_move_a4
      Position A is inert with OR without my fix. A test of A's inertness that
      depended on my fix would not be a test of A.
  Fix restored; 14 passed.

a4_before: 2
a4_before_detail: |
  FindingRegistry.from_dict(runner_state.json["registry"]).unverified_critical_count()
  with the handoff stamp stripped (i.e. the shipped behaviour) = 2.
  Blocking set = ['C0066', 'C0073'], severities 0.45 and 0.50.

a4_after: 0
a4_after_detail: |
  Same call on the same registry with the fix in place = 0.
  handed_to_human_ids() = ['C0066', 'C0073'] -- excluded implies reported, and
  the HANDOFF log line fires in the real _evaluate_gate_conditions path.

gate_after: |
  _check_gamma_alt_convergence called with study_run1b's own declared config
  (falsifier_gate_enabled=True, gamma_alt_threshold=0.3,
  gamma_alt_consecutive_zero_crit=3, gamma_alt_earliest_round=3) and its own
  measured series:

  ROUND 7 (the run's last round; novel-critical tail [1, 0, 0] per console.log
  line 1500), WITH the fix, A4 = 0:
    converged = False
    "two-sided gate not met: novel_crit_recent=[1, 0, 0],
     gamma_critical=0.732 (convergence needs gamma_critical >= 0.3 AND 3
     consecutive zero-new-critical rounds)"

  SO THE RUN WOULD STILL NOT HAVE CONVERGED, AND I STATE THAT PLAINLY. A4 was
  necessary but NOT sufficient. The count side of the two-sided gate needs 3
  consecutive zero-new-critical rounds; at round 7 the tail was [1, 0, 0] --
  only 2. max_rounds = 8 (rounds 0..7), so the run had no 9th round in which
  to earn the third zero. The brief's "exactly 2 registry entries hold it" is
  therefore false: two entries held the A4 side, and the count side was also
  short by one round.

  ROUND 8 (one more round, tail [0, 0, 0]) -- where the fix is EXACTLY the
  decider:
    A4 = 2 (door closed): converged = False
      "A4 BLOCK: 2 unverified critical-severity candidate(s) ... pending at
       round 8 -- zero-critical streak does NOT accrue
       (novel_crit_recent=[0, 0, 0]). HIL review required."
    A4 = 0 (door open):   converged = True
      "CRITICAL_QUIESCENCE_CONVERGED (two-sided gate): gamma_critical=0.732
       >= 0.3 (decay curve flattened) AND 3 consecutive zero-new-critical
       rounds (history tail=[0, 0, 0]) at round 8 -- the two sides of the same
       diminishing-returns measure agree"

  NO-RESCUE RULING RESPECTED. The door reads computed_evidence, whose
  reasoned_withdrawal records are written by _post_convergence_sweep (line
  7513), which runs AFTER `converged` is assigned. So on a live run the fix
  cannot flip this run's verdict; it changes the verdict only from the NEXT
  round onward, which is where a convergence decision belongs. In-round
  reachability of the stamp is via _apply_discrimination_control (line 5863).
  Stated as a residual: for an entry of C0066/C0073's exact shape -- nothing
  ever routed, nothing ever tested -- no in-round writer of the stamp exists
  today, so the door helps such an entry only from the round after a sweep.
  That is a real limitation of this fix and I am not hiding it.

figures:
  - "A4 = 2; blockers ['C0066','C0073']; severities 0.45 / 0.50; verdicts 0 / 0; routing_history absent; falsifier_code empty; hil_has_computed_evidence True; kinds ['reasoned_withdrawal'] -- scripts/a4_handoff_figures_2026-10-03.py [1]"
  - "A4 after the fix = 0; handed_to_human_ids = ['C0066','C0073'] -- scripts/a4_handoff_figures_2026-10-03.py [1]"
  - "Position A alone: A4 = 2 at rounds 8, 9, 20, 100; exhausted=False on both blockers -- scripts/a4_handoff_figures_2026-10-03.py [3]"
  - "exhausted_round_threshold = 8; max_irreducible_queue = 2; falsifier_gate_enabled = True; max_rounds = 8 -- report _declared_config, scripts/a4_handoff_figures_2026-10-03.py [2]"
  - "_irreducible_queue_split = (0,0) at sev 0.5 and (1,0) at sev 0.9; exhausted valve None/None/True/True at sev 0.5/0.69/0.70/0.90 -- scripts/a4_handoff_figures_2026-10-03.py [4]"
  - "gamma_all_history [0.0,0.0,0.3338,0.3922,0.3875,0.3926,0.4102,0.4274]; gamma_critical_history [0.0,0.0,0.6423,0.682,0.6971,0.7018,0.716,0.7323] -- scripts/a4_handoff_figures_2026-10-03.py [2]"
  - "stop_reason = UNRECORDED_STOP -- scripts/a4_handoff_figures_2026-10-03.py [2]"
  - "gate: round 7 A4=0 -> False (count side); round 8 A4=2 -> False (A4 BLOCK), A4=0 -> True -- scripts/a4_handoff_figures_2026-10-03.py [5]"
  - "hil_has_computed_evidence: 1 write site (reference_runner_v3.py:14231), 0 read sites repo-wide -- grep over bench/reference_runner_v3.py bench/dm/*.py bench/*.py"
  - "severity-invariance of the predicate over 101 values in [0,1] -> {True}; .get('severity') trap not triggered -- bench/tests/test_a4_handoff_door_2026-10-03.py::test_predicate_exists_and_is_severity_free"
  - "400 randomised registries: excluded == reported in all 400; A4_with_door <= A4_without_door in all 400 -- bench/tests/test_a4_handoff_door_2026-10-03.py::test_excluded_implies_reported_randomised"
  - "6 dead-instrument mutants each return the entry to the count -- bench/tests/test_a4_handoff_door_2026-10-03.py::test_door_stays_shut_for_every_dead_instrument_shape"
  - "mutation check 12/14 = 85.7143%, Wilson [60.0586%, 95.9906%] -- /tmp/cdsflw/stats.py (statsmodels + mpmath, |diff| 1.11e-16) and wolframscript (60.058620503029644, 95.9906078728535); computed with Wolfram Language (local Wolfram Engine, via wolframscript)"
  - "brief's 22/65 = 33.8462%, Wilson [23.5335%, 45.9616%] REPRODUCES -- statsmodels, mpmath (|diff| 5.55e-17) and Wolfram Language (23.533503312096666, 45.96162308448794)"
  - "file's 58/86 = 67.4419%, Wilson [56.9779%, 76.4143%] REPRODUCES -- statsmodels, mpmath (|diff| 1.11e-16) and Wolfram Language (56.9778553659483, 76.41430054268858)"
  - "brief's 82/273 = 30.0366% REPRODUCES (brief says 30.04%); sigma 0.1419 / band 0.09 = 1.5767 -- /tmp/cdsflw/stats.py"

refutation_condition: |
  Any ONE of these overturns me:
  1. An in-round (pre-convergence) writer of computed_evidence with kind in
     HANDOFF_EVIDENCE_KINDS reached by an entry with verdicts == [], no
     routing_history and empty falsifier_code. I searched and found none
     (reasoned_withdrawal: _post_convergence_sweep only;
     critical_refuted_evidence_recorded: same function, and those entries
     carry falsifier_code). If one exists, my fix becomes capable of releasing
     an untested critical mid-run and the four conjuncts are not enough.
  2. A single run in the archive where an entry with verdicts == [], no
     routing_history, empty falsifier_code AND a reasoned_withdrawal record
     was LATER tool-CONFIRMED. That would make the handoff stamp a premature
     label and the door would be releasing live defects. I did not sweep all
     65 archived runs for this; it is the strongest open attack on my fix and
     I name it as unexecuted.
  3. Evidence that a verdict CAN reach a sub-critical UNCONFIRMED entry in the
     normal loop -- e.g. an escalation path that bypasses _apply_routing's
     line-6763 severity skip. That would restore Position A's premise, since
     `has_reviews` would become reachable and the valve's severity clause
     would then be the binding constraint. A4 going 2 -> 0 under Position A on
     ANY archived registry refutes my item [3].
  4. A run where `handed_to_human_ids()` is non-empty, the HANDOFF line is
     absent from console.log, and the run converged. That breaks
     excluded-implies-reported and makes my exclusion a silent one.
  5. A demonstration that routing_history is written for C0066/C0073 under a
     different config, which would make my "the ladder never ran" conjunct
     config-dependent rather than structural.

disagreement: |
  THE BRIEF'S CENTRAL CLAIM IS FALSE, AND MEASURED SO. "Exactly 2 registry
  entries hold it; the decay curve HAD flattened; the gate was blocked on its
  other side by the A4 fail-safe." Draining A4 to 0 and calling the real gate
  at round 7 with the run's own config returns converged=False on the COUNT
  side: novel_crit_recent=[1, 0, 0] against gamma_alt_consecutive_zero_crit=3.
  Two blockers held the A4 side AND the zero-critical streak was one round
  short. Had the A4 question been fixed in isolation, study_run1b would still
  have ended at the round cap and the fix would have been scored a failure for
  the wrong reason.

  THE BRIEF MISATTRIBUTES ITS OWN HEADLINE NUMBER. "gamma_critical finished at
  0.4274" -- no. gamma_all_history[-1] = 0.4274; gamma_critical_history[-1] =
  0.7323. The console prints both on adjacent lines and the brief took the
  wrong one. It does not change the verdict (both clear 0.30), but it is the
  same confusion the file itself already corrected once, in
  _irreducible_queue_split's comment: "That is FALSE. The second half of the
  gate is gamma_alt_consecutive_zero_crit ... not gamma_all." Twice in two
  days on the same two series argues for naming the series in the log line
  rather than relying on readers to keep them apart.

  POSITION B'S OWN EVIDENCE IS WRONG IN ITS PARTICULARS. "It fired in this
  run: console.log line 948 ... on an entry at severity 0.6 with NO FALSIFIER,
  no routing_history and escalated False -- the same shape as the 2 blockers."
  C0042 carries 1,180+ characters of falsifier_code and falsifier_verdict ==
  "CONFIRMED". It is not the same shape; it is the opposite shape, and that is
  precisely WHY it was freed. B's conclusion survives on better evidence than
  the evidence it was given.

  "A WITHDRAWAL RECORDED BY ONE MECHANISM AND READ BY NONE" IS HALF RIGHT, AND
  THE HALF IT GETS WRONG MATTERS. The non-retirement is deliberate and
  correct: line 7508 refuses to retire on model prose when severity is
  unproven ("an unproven severity cannot buy a demotion, a clearance or a
  closure"), and C0066's severity_proof.status is "SKIP". If the panel treats
  that refusal as the bug, the repair is to let a model's say-so retire a
  finding -- a vote. What IS unread is the stamp the refusal writes,
  hil_has_computed_evidence, and the right repair is to read it as "this is a
  human decision", never as "this claim is retired". My fix changes what the
  CONVERGENCE MACHINERY believes is pending; it changes nothing about the
  claim's status, severity or truth. Both entries remain UNCONFIRMED and both
  are still named in a report line every round.

  WHERE THE BRIEF IS RIGHT AND I CHECKED. All three of its statistics
  reproduce to the digit across three independent tools: 22/65 = 33.8462%
  Wilson [23.5335%, 45.9616%]; 58/86 = 67.4419% [56.9779%, 76.4143%];
  82/273 = 30.0366%. statsmodels and mpmath agree to 1.1e-16, and Wolfram
  Language (local Wolfram Engine) returns the same bounds to 10 significant
  figures. I found no arithmetic to dispute.

  LAST, AND IT IS A FINDING RATHER THAN A QUIBBLE: this run's stop_reason is
  "UNRECORDED_STOP (the round loop exited by a path that names no reason)".
  The loop spent 342 minutes and 8 rounds reaching a state it was already in
  at round 5, and exited through a path that records nothing about why. A4 has
  no persistence bound the way the irreducible queue has max_irreducible_queue,
  so a permanently-blocked A4 cannot halt with an evidence bundle -- it can
  only burn to the cap. I deliberately did NOT fix that here (scope
  discipline; it is new config + new state + new halt wiring), but it is the
  next above-threshold item and it is the reason this run cost what it cost.

passes_run: 4
termination: |
  Pass 1 located the artefacts and rehydrated the registry through the real
  FindingRegistry. Pass 2 executed Position A in isolation and refuted it.
  Pass 3 traced every A4 door to its severity gate by execution, found the
  unread handoff stamp, and rejected two more elaborate repairs on measurement.
  Pass 4 applied the fix, wrote and ran the falsifier, ran the mutation check,
  ran 171 related tests, measured the gate at rounds 7 and 8, and
  cross-verified every proportion with statsmodels, mpmath and Wolfram.
  Pass 4 produced no new above-threshold finding inside this question's scope;
  the one it produced outside scope (A4 has no persistence bound) is recorded
  under disagreement rather than acted on.
```
<<<CDSFL_ANSWER_END>>>

**Delivered files:** `bench/reference_runner_v3.py` (fix), `bench/tests/test_a4_handoff_door_2026-10-03.py` (14 tests, 12 fail on revert), `scripts/a4_handoff_figures_2026-10-03.py` (every quoted figure). Wolfram ran locally, exit 0, no `Name::tag`, and agreed with statsmodels and mpmath to 10 significant figures.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 52 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_blocker_round1_2026-10-03) -->

All evidence is in. Three tools (statsmodels, mpmath, Wolfram Language via local Wolfram Engine) agree on every interval; the arm-isolation, the fix, the falsifier, the mutation check, and the archive census all ran. Summary of what execution showed, then the machine-readable block.

**What execution decided.** Position A's site is real but its repair is a no-op: with the severity clause removed, the valve's `has_reviews` guard (`verdicts`-only) still refuses C0066/C0073, so A4 = 2 at every round through 40. Position B's discriminator (`verdicts == []`) is correct, but its framing ("why does no model file a verdict?") is half-wrong by the registry's own contents: models assessed these entries five times each — the WITHDRAW door recorded every assessment into `computed_evidence`, because the 2026-09-07 ruling rightly refuses to let an unproven severity buy a retirement. The activity exists; the valve reads the wrong channel. Neither arm alone releases anything; both together release both entries to the designed UNCONFIRMED/HIL hand-off without retiring, closing, or voting on anything. That is a composition demonstrably beating each arm alone, where each arm alone equals doing nothing.

<<<CDSFL_ANSWER_BEGIN>>>

**position**: BOTH — with a correction to each. A names a real asymmetry (counter severity-free since ruling 23; valve severity-gated) but A's repair alone is executable-no-op: `has_reviews` still blocks. B names the true discriminator (`verdicts == []`) but misdiagnoses it as a missing verdict; the panel's review activity exists, recorded by the WITHDRAW door into `computed_evidence`, a channel the valve never read. The repair is at A's site, on both guards, using B's evidence.

**evidence_for_position**: `scripts/a4_blocker_arm_isolation_2026-10-03.py` — four textual variants of the real module, each sweeping `_update_finding_statuses` over the rehydrated archived registry, rounds 8–40, reading `unverified_critical_count()` after every call. Printed:
```
ORIG      A4@start=2 ... A4@r40=2 first_zero_round=None exhausted={'C0066': False, 'C0073': False}
A_ONLY    A4@start=2 ... A4@r40=2 first_zero_round=None   (severity clause removed; verdicts-only reviews)
B_ONLY    A4@start=2 ... A4@r40=2 first_zero_round=None   (computed_evidence counted; severity clause kept)
A_PLUS_B  A4@start=2 A4@r13=1 A4@r15=0 first_zero_round=15 exhausted both True, status both UNCONFIRMED
```

**composes**: true, by that measurement: each arm alone leaves A4 = 2 at every round (identical to the shipped code); composed, A4 → 1 at round 13 (C0066, age 8 ≥ `exhausted_round_threshold` 8), → 0 at round 15 (C0073), with both statuses still UNCONFIRMED — the designed HIL terminal — and neighbours C0042/C0069 untouched at CLOSED. No single arm suffices, so the single-arm preference cannot apply.

**root_cause**: `bench/reference_runner_v3.py`, pre-pass 1 of `_update_finding_statuses` (shipped lines 3931–3941). Ruling 23 (2026-09-06) made `unverified_critical_count` severity-free, but every exit stayed narrower than the counter: the valve required `severity >= 0.7` AND `len(verdicts) > 0`; routing takes only `escalated` criticals (line 6761); pre-pass 2 needs a verdict row; the falsifier path needs code no model filed; and the WITHDRAW door (line ~7546) records sub-critical/unproven-severity assessments into `computed_evidence`, which nothing on the release side read. A sub-0.7 UNCONFIRMED entry with zero verdict rows therefore had no exit at ANY round — demonstrated by the r40 sweep — and run 1b burned to max_rounds on exactly two such entries.

**fix_path**: `bench/reference_runner_v3.py` (pre-pass 1 of `_update_finding_statuses`). Two changes: (1) valve scope matched to its readers per status — UNCONFIRMED entries valve severity-free, matching `unverified_critical_count`; all other valve statuses keep the 0.7 scope, matching `open_crit_high_count`, so no flag is written that no reader consults; (2) `has_reviews` counts recorded review activity in either channel: `verdicts` OR `computed_evidence` (whose only writers are `falsifier_refuted` — a tool ran — and `reasoned_withdrawal` — a dispatched model's recorded assessment).

**fix_rationale**: Simplest sufficient — it repairs the one existing mechanism built for exactly this ("cannot block for ever"), adds no new flag, counter, status, or entry point, and every line it touches is executed by the delivered test. Additive both ways: nothing is disabled (age guard kept, requires-review-activity guard kept — entries with no recorded activity in either channel still never exhaust, pinned by test), and the released entries are not retired — they stay UNCONFIRMED and go to the human with the withdrawal evidence on file, which is minimal-HIL, not zero-HIL, and not a vote: the severity float decides nothing, the withdrawals close nothing. The alternative (a new A4 skip keyed on `hil_has_computed_evidence` plus a paired reporter) would duplicate the valve's age/activity guards under a second name — more surface, same function.

**falsifier_path**: `bench/tests/test_exhausted_valve_matches_a4_scope_2026-10-03.py` — 9 tests: the archived before-state as fact; release at threshold age through the REAL registry and REAL pre-pass; both arm-insufficiency pins; three guard-preservation pins (age, no-activity, critical-OPEN path byte-identical); and the gate called before/after including an honesty pin that run 1b is NOT retro-rescued.

**falsifier_command**: `python3 -m pytest bench/tests/test_exhausted_valve_matches_a4_scope_2026-10-03.py -q`

**falsifier_output**: `9 passed in 0.38s` (post-fix). Before the fix the same behaviour was observed as the failure: ORIG sweep A4 = 2 at rounds 8–40, `first_zero_round=None`.

**mutation_check**: Executed — fix reverted by exact hunk swap, test re-run, fix restored byte-identical (sha256 verified): `4 failed, 5 passed`. Failing: `test_run1b_blockers_release_at_threshold_age` (A4 stays 2 at r13/r15), `test_subcritical_unconfirmed_with_recorded_withdrawal_exhausts`, `test_severity_arm_alone_is_insufficient` and `test_age_guard_kept` (shipped code never enters the valve for sub-critical UNCONFIRMED, so `exhausted` is popped — key absent, not False). Restored run: `9 passed`. Neighbour regression: 60 tests across the six A4/valve/predicate suites pass; 92 more across valve-reader, open-crit, gamma-alt, status-transition, EXTEND and transport-guard suites pass.

**a4_before**: 2 — obtained by calling `unverified_critical_count()` on `FindingRegistry.from_dict` of the archived `runner_state.json`.

**a4_after**: 2 at the archived final round (ages 2 and 0 against threshold 8 — the fix does not and must not flip an archived verdict); by calling `_update_finding_statuses` forward: 1 at round 13, 0 at round 15. Without the fix: 2 at every round tested through 40.

**gate_after**: Called. At round 7 as-run (A4=2): `(False, "A4 BLOCK: 2 ...")`. At round 7 with A4 counterfactually 0: `(False, "two-sided gate not met: novel_crit_recent=[1, 0, 0], gamma_critical=0.732 ...")` — **run 1b would still not converge**, plainly: its non-convergence was overdetermined — a novel critical landed at round 5 (inside the 3-round window), `max_rounds=8` with `extension_cap=8` (no headroom), and `exhausted_round_threshold=8` exceeds the rounds remaining after either blocker's birth. In a continuation, the gate returns `(True, "CRITICAL_QUIESCENCE_CONVERGED ...")` the first round where the zero tail and the released A4 coincide — round 15 under this config. The fix converts a permanent block into an age-bounded one; it rescues nothing retroactively.

**figures** (every one produced by a script run here):
- A4 before = 2; contested(8) = 1; irreducible_queue = 0, decomposition (0,0); open_crit_high = 0 — inline rehydration calls (first harness block).
- Arm isolation: ORIG/A_ONLY/B_ONLY A4=2 at r8–r40; A_PLUS_B A4: 2→1 (r13) →0 (r15) — `scripts/a4_blocker_arm_isolation_2026-10-03.py`.
- Archive census (`scripts/a4_blocked_entry_census_2026-10-03.py`, statsmodels ≡ mpmath to 1e-6, Wolfram Language local engine agreeing to shown digits): 59 archives readable (not 65); 22/59 = 37.2881% runs with ≥1 counted entry, Wilson [26.0840%, 50.0464%]; 175 counted entries (not 150); severity-clause-ALONE 57/175 = 32.5714% [26.0672%, 39.8244%]; BOTH guards 52/175 = 29.7143% [23.4381%, 36.8619%]; critical-zero-verdict 43/175 = 24.5714%; releasable by composed fix 99/175 = 56.5714% [49.1645%, 63.6961%]; the 76 with no recorded activity in either channel stay blocking, correctly.
- Brief's quoted intervals reproduce exactly: 22/65 → [23.5335%, 45.9616%]; 58/86 → [56.9779%, 76.4143%] (three tools).
- Gate figures: gamma_critical passed to the gate = 0.7323 (report `gamma_critical_history[-1]`); 0.4274 = all-severity `gamma_history[-1]` — gate call output and report read.

**refutation_condition**: Any of: (1) a run or test showing the shipped code releasing C0066/C0073 at some round — my permanence sweep only reached round 40; (2) a demonstration that single-arm A or B releases them under the run's real config — my variants are textual edits, and a mis-built variant would void the composition claim (I verified the A_ONLY substitution text, but an independent rebuild is the stronger check); (3) a reader of `exhausted` or `computed_evidence` I did not find whose behaviour the fix changes harmfully — my reader enumeration was grep-based; (4) evidence that `computed_evidence` rows can be minted without a real dispatch (which would make the activity guard spoofable and the evidence arm a vote in disguise); (5) a founder ruling that sub-critical UNCONFIRMED entries must hold A4 until a verdict row exists, in which case the correct repair is instead at the WITHDRAW door (write a verdict row alongside the evidence row) — same discriminator, different channel.

**disagreement**: Four, with measurements. (1) The brief's "gamma_critical finished at 0.4274" misattributes the series: the gate receives gamma_critical = 0.7323 (`gamma_critical_history[-1]`); 0.4274 is the all-severity gamma. The conclusion (flattened, ≥ 0.30) survives — more comfortably than stated. (2) Position A's "107 of 150 blocked by the severity clause alone" does not reproduce and is internally confounded: on the 59 archives present, only 57/175 are blocked by the severity clause *alone*; 52 need both guards, and 57+52 = 109 ≈ 107 strongly suggests A counted "severity < 0.7" as "severity clause alone", conflating a failing guard with a sole blocker — the exact conflation that made A's repair a no-op on this run. (3) The archive is 59 runs here, not 65, and 175 counted entries, not 150; A's 22 blocked runs matches but its denominator does not. (4) Position B's "the question becomes why no model files a verdict" is the wrong question: five models per entry filed assessments; the runner's own WITHDRAW door routed them into `computed_evidence` by ruling — the defect is a write channel with no reader, which is also this project's most-confirmed defect class (additions nothing reaches). The brief's claim that C0066's withdrawal was "recorded by one mechanism and read by none" is confirmed and understated: five withdrawals, read by none. A's "severity immutable, 0 of 523" I could not reproduce or refute in-sandbox and mark unverified rather than disputed.

<<<CDSFL_ANSWER_END>>>

**Termination.** Four falsification passes: (1) arm isolation over the real registry; (2) fix + 9-test falsifier + executed mutation check with byte-identical restore; (3) neighbour regression (60 + 92 targeted tests, all green); (4) archive census with triple-tool statistics, which also tested the brief's own figures. The final pass surfaced no new above-threshold finding — the residual items (76 archive entries with no recorded activity remain blocking; 8-round configs still cap before the age valve opens for late-born entries) are design-consistent behaviour, named here rather than silently absorbed. Wolfram ran (local Wolfram Engine, 1 call, attributed above) and agreed with statsmodels and mpmath on every interval. Done: the composed valve repair is delivered at `bench/reference_runner_v3.py`, falsified by `bench/tests/test_exhausted_valve_matches_a4_scope_2026-10-03.py`, with both producing scripts in `scripts/`.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_blocker_round1_2026-10-03/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
