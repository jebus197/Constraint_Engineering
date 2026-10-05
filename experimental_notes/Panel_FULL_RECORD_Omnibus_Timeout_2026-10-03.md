# The omnibus brief that returned nothing: 2 seats, 2 attempts, 0 files

Record written 2026-10-04T02:56:58+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS ATTEMPTED, AND WHY THIS RECORD EXISTS EVEN THOUGH IT RETURNED NOTHING. This round asked 2 free seats to review 9 faults at once, adjudicate 2 competing root-cause positions, and answer a structural question about the project's parsing, each with a fix, a runnable falsifier, an executed result and a mutation check. Both seats hit the claude CLI's 1800-second cap on attempt 1 having written 0 files, retried, and were stopped during retry 2 rather than allowed to repeat an identical failure for another 30 minutes.

WHAT IT COST. 2 seats x 2 attempts x 1800 seconds, 0 response characters, and 2 full repository sandbox copies of roughly 2.4 GiB each. Nothing usable was produced. The dispatch was free in the sense of using no paid seat, but it consumed Max-plan subscription time on a night when the weekly allowance was already at 97%.

THE CAUSE WAS NOT BRIEF LENGTH, WHICH WAS MEASURED RATHER THAN ASSUMED. This brief was 2762 words. Across the 99 other archived briefs the median is 1067 words, and briefs of 7482, 9009 and 17901 words all returned 4 seat files. So length does not predict failure here. What differs is the VOLUME OF WORK REQUESTED: 9 faults each requiring a fix plus a falsifier plus an execution plus a mutation check is hours of work inside a 30-minute window.

WHAT REPLACED IT. A narrow brief covering the single most pressing question, 1224 words, dispatched as panel_blocker_round1_2026-10-03. Both seats completed in 903 and 935 seconds with 52 and 47 tool calls, and returned measured, executed answers including a refutation of the brief's own framing. The record of that round is Panel_Full_Record_Blocker_Round1_2026-10-03.md.

THE LESSON, STATED SO IT IS NOT RELEARNED. A panel brief is bounded by the work it asks for, not by the words it uses. Where a review has more than one question, dispatch it as more than one round. This failure is recorded rather than quietly deleted because an unrecorded null result invites the same brief to be written again.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief — the convergence blockers of study_run1b, and the parser class behind them

## What this asks of you

`study_run1b_2026-10-03` ran 8 rounds, produced 75 findings and did NOT converge. `gamma_critical`
finished at 0.4274 against the `gamma_alt_threshold` of 0.30, so the decay curve HAD flattened; the
two-sided gate was blocked on its other side. Replaying the live
`_check_gamma_alt_convergence` with 1 more zero-new-critical round returns
`CRITICAL_QUIESCENCE_CONVERGED`, so the run was 1 round short of the streak, not failing on
principle. Nothing below questions the mathematical model: the founder's standing directive is that
when convergence seems out of reach the cause is MECHANICAL, and every fault below is mechanical.

Your task is to review 9 faults and 1 built fix, decide which repairs are correct, and deliver the
ones you endorse as files. Disagreement between seats is kept as information; you are NOT being
asked to converge with the other seat.

## The standards that bind every answer

- **Simplest sufficient.** The smallest repair that addresses the root cause and its downstream
  consequences. Not the most thorough.
- **Additive, in BOTH directions.** Never disable or remove a mechanic. Removal only where a
  COMMITTED MEASUREMENT shows the replacement dominates on a named property — a judgement that
  something is better is not evidence that it is. Symmetrically, an addition nothing reaches is not
  additive either: every new flag, gate or branch must be wired to a caller and executed by a test.
- **Composability.** Before presenting 2 repairs as alternatives, check whether they compose.
  Compose ONLY where the composition demonstrably beats EACH arm alone; where a single arm performs
  as well, prefer the single arm.
- **No model voting.** A finding is confirmed programmatically or by the human, never by a model's
  say-so. A repair that makes a model's opinion decide anything is wrong by construction.

## Founder rulings that are NOT open for you to revisit

1. **Ruling 23, 2026-09-06 — severity is not a vote.** `unverified_critical_count`
   (`bench/reference_runner_v3.py:2747`) had its `severity >= CRITICAL_SEVERITY_THRESHOLD` gate
   removed because `severity` is a float the SOURCE MODEL assigns. Measured then: AUC 0.464 against
   0.5 for chance inside the deciding band, per-assignment sigma 0.1419 over 273 duplicate pairs
   scored by 2 models, against a band 0.09 wide, and 82 of 273 identical defects landing on
   opposite sides of 0.7. **Do not propose putting a model-assigned float back in charge of
   convergence.** NOTE FOR THE RECORD: the removal was committed at 16:21:48 and the founder's
   written answer at 22:15 the same day REJECTED both removal and the rubric swap, ordering worked
   proofs instead. The provenance is with the founder and is not yours to settle. Reason about the
   measurement, not the authority.
2. **Worked proofs are the agreed replacement.** `bench/dm/_rk_proof.py` asks each seat to re-emit a
   CORROBORATION block; `_validate_rk_computation` recomputes R_k and compares. PASS/WARN/FAIL/SKIP.
   A recomputation that survives is a FACT, not an opinion, so it satisfies the no-voting rule while
   keeping severity load-bearing.
3. **HIL intervention is the system working, not failing.** An UNCONFIRMED finding handed to the
   human is a designed terminal state. The target is minimal-HIL, never zero-HIL.
4. **The closing sweep must NEVER rescue a failed run.** `converged` is assigned only before the
   sweep, and the only post-sweep writes to the result dict come from `stop_reason_fields`, which
   returns just `stop_reason` and `stop_reason_recorded`. The founder's position, verbatim in
   substance: a sweep that could flip a verdict would make convergence unfalsifiable and would look
   like sweeping an inconvenient result under the carpet. **Keep it incapable of that.**

## Fault 1 — ALREADY FIXED. Review it adversarially.

`validate_round_rk` (`bench/reference_runner_v3.py`) paired CORROBORATION sections to findings BY
POSITION. Two failure modes, both measured on run 1b:

- The original `_extract_corroboration_sections` splits case-insensitively on the bare word, so it
  fires on the JSON key `corroboration_fit` and on prose like "independent corroboration".
  **Measured: 226 phantom sections on top of 109 real ones — 67.46% of everything it reported was
  not a corroboration block.** Round 7: the ChatGPT seat reported 27 where 3 are real; DeepSeek 29
  where 4 are real.
- A finding whose index exceeded the section count was stamped SKIP whatever it had written. C0073
  carried a block that `_validate_rk_computation` returns PASS on (`model_rk` 0.49, recomputed
  0.4851, delta 0.0049) and was stored SKIP with all 3 values None. Unproven, it was counted by the
  A4 blocker, and convergence was blocked by a proof the parser could always have passed.

**The fix as built:** a sibling `_extract_corroboration_sections_with_ids` that is line-anchored
(excluding `corroboration_fit`) and decoration-tolerant (seats write `**FINDING_ID:** F609`), plus
identity-first pairing in `validate_round_rk` with the OLD positional path retained as the fallback.
The original extractor is untouched, because the frozen v1 runner,
`scripts/measure_rk_proof_compliance.py`, 2 committed panel falsifiers and
`bench/tests/test_rk_clip_stops_at_an_arrow_2026-09-22.py` all read its shape.

**Measured after the fix:** identity pairing reaches 104 of 109 real sections, 95.41%, Wilson
[89.71%, 98.03%]. Safety invariant executed over all 48 archived responses: the sibling never
reports MORE sections than the original, 48 of 48, so it filters phantoms and cannot invent proofs.
Over real sections only the status census is PASS 82, WARN 17, FAIL 10, SKIP 0 — **99 of 109 prove,
90.83%, Wilson [83.93%, 94.94%]**, against the corrupted instrument's 35/4/4/32. Tests:
`bench/tests/test_rk_proof_pairing_by_identity_2026-10-03.py`, 8 tests including a mutation check
that fails if anyone reverts to positional. Regression: 4333 passed, 1 skipped, 0 failures
attributable to the change.

**Your job on fault 1:** try to REFUTE it. Run the tests. Find a response shape where the sibling
mis-attributes a section, or where the fallback silently hides a mis-pairing, or where the
line-anchored header pattern misses a real header a seat actually emits. State what would overturn
the 90.83% figure.

## Faults 2 to 9 — diagnose and fix

2. **The two readers contradict each other, 3 log lines apart.** On run 1b's registry
   `unverified_critical_count()` returns 3 while `undemonstrated_subcritical_ids()` returns the SAME
   3 entries described as "un-demonstrated sub-criticals, non-gating". One function gates the run on
   them; the other tells the operator they are harmless. `console.log:1496` and `:1499`.
3. **C0066's withdrawal was recorded and never applied.** Its `computed_evidence` holds
   `{'kind': 'reasoned_withdrawal', 'by': 'CC2-SIM', ...}` plus a concrete `proposed_fix`, and its
   status stayed UNCONFIRMED. A field written by one mechanism and read by none.
4. **C0073's merge has no path through.** `merge_blocked_reason` is "model-declared DUPLICATE
   action; no tool verdict" and `merge_candidate_of` is C0069, which is CLOSED, `verified` True,
   `falsifier_verdict` CONFIRMED. The no-voting rule correctly refuses a model's say-so — and
   nothing produces the tool verdict that would settle it. A programmatic claim-text comparison is
   exactly a tool's job.
5. **The `exhausted` valve's age lock is arithmetically unreachable.**
   `exhausted_round_threshold` defaults to 8 (`:1607`) while `round_idx` is 0-based, so the maximum
   attainable age in an 8-round run is 7. z3 returns `unsat`, a NumPy enumeration of all 36 legal
   pairs gives max age 7, and SymPy gives the general condition `T <= R - 1`. Producer:
   `scripts/exhausted_marking_age_lock_2026-10-03.py`.
6. **Severity proofs are unauditable from the registry.** 44 of 75 stored proofs cannot be
   re-derived from the entry's own stored description, because the description does not retain the
   CORROBORATION block. Checking any proof means going back to the raw seat files. The founder's
   position is that the registry is the single source of truth for any experiment a researcher may
   run, so this is a registry defect, not a convenience.
7. **`UNRECORDED_STOP`.** The round loop's natural exit (round cap reached) sets no stop reason, so
   the commonest non-convergent outcome reports as "the runner did not record why" and is
   indistinguishable in the archive from a genuinely unexplained stop. The loop has 8 `break`
   statements of which 2 set a reason, and the natural exit sets none.
8. **A 12-character guard refused a real correction.** `console.log:1508` — "corrected copy REFUSED
   C0072 from DeepSeek-SIM: the original passage is shorter than 12 characters, which is too short
   to locate reliably". A mechanic fired and a length threshold stopped it.
9. **`scripts/cdsfl_recover.py` cannot see these runs.** Its live-process check scans for
   `/reference_runner_v3|detached_launch|launch_exp/` while the study runs launch as
   `bench/tools/run_simulated_experiment.py`, so it reported "nothing running — this is a completed
   check, not a failed one" while PID 14585 was alive. A recovery instrument stating a false
   negative confidently.

## The disagreement you must adjudicate, NOT smooth

Two independent investigations reached DIFFERENT root causes for why 3 entries blocked run 1b. Both
are evidence-backed. Decide, with execution, which is right, or whether they compose.

**Position A — the valve's severity clause is the root cause.** `_update_finding_statuses:3933`
still gates release on `severity >= 0.7`, the very float the counter stopped gating on. Measured
across 65 archived runs: 22 carry at least 1 permanently-blocked entry, 33.85%, Wilson [23.53%,
45.96%], 150 such entries in total. Of 150 blocking entries, 107 are blocked by the severity clause
alone. Severity is immutable — 0 of 523 entries with a `severity_proof_history` show more than 1
distinct value — so `severity >= 0.7` fails at EVERY round for those 107, permanently. Prevalence
jumped from 22.00% to 73.33% at a fitted change point of 2026-09-08, which coincides with ruling 23.
Association with non-convergence: Fisher odds ratio 6.15, p = 4.99e-03, cross-verified by an mpmath
exact hypergeometric tail agreeing to 1.7e-18 and by a statsmodels Table2x2 Woolf CI [1.68, 22.56];
still significant after collapsing byte-identical run families (OR 5.31, p = 1.68e-02). **Stated
limit: within the post-ruling era alone, 13 decidable runs, OR 18 but p = 0.108 — underpowered.
Suggestive, not causal.** Proposed repair: remove the valve's severity clause. Additive — nothing
disabled, a release path widened.

**Position B — the missing verdict is the root cause, and a severity-free door already works.**
Pre-pass 2 of `_update_finding_statuses` (`:3943-3953`) reopens an UNCONFIRMED entry to OPEN when
`rounds_in_status >= 2` and any verdict arrived after the status change. It contains 0 occurrences
of "severity". **It FIRED in run 1b**: `console.log:948` — "REOPEN C0042: new evidence after
UNCONFIRMED" — on an entry at severity 0.6 with no falsifier, no `routing_history` and
`escalated` False, which is the same shape as the 3 blockers. It was freed by 1 verdict row. So the
discriminating variable between C0042 and C0066/C0067/C0072 is `verdicts == []`, not severity, and
the real question is why no model files a verdict on those 3. Position B holds that widening the
valve treats a symptom while an in-spec door already exists.

**Questions.** Which position survives execution? Do the repairs compose, and does the composition
demonstrably beat each arm alone — or does one arm suffice? If `verdicts == []` is the binding
constraint, what makes a finding never receive a verdict, and is that the fault to fix instead?

## The structural question — the parser class, after 10 months

The founder's question, and it is the most important item here: parser defects have recurred
throughout the project's life. Why, and can the class be closed for good?

Observed, this run alone: the phantom-section defect above; `**FINDING_ID:**` defeating an
undecorated pattern; a 12-character minimum refusing a real correction; a description truncation
that drops the block a parser needs; and historically a verdict reader that matched `NOT FALSIFIED`
as containing `FALSIFIED`.

**The hypothesis to test.** The project runs 2 parsing regimes side by side. Sentinel-delimited:
`<<<CDSFL_ORIGINAL>>>`, `<<<CDSFL_CORRECTED>>>`, `<<<CDSFL_END>>>` and nonce-protected
`<<<CDSFL_TARGET_BEGIN {nonce}>>>`, which are unambiguous by construction and which seats emit
reliably — measured, 45 of 48 responses carry such a marker, 93.75%, Wilson [83.16%, 97.85%], 330
markers in total. And bare-regex-over-prose, used for EVERY finding field — `FINDING_ID`,
`SEVERITY`, `CORROBORATION`, `FLAW_CLASS`, verdict words — which must guess whether a word is a
header, a JSON key, a prose mention, a decorated form or a negation. Every parser defect in the
record belongs to the second regime. The project solved this properly once, in one place, and never
generalised it.

**Your task.** Decide whether extending the sentinel envelope to the finding fields is the correct
permanent repair, and whether it can be made robust, accurate, flexible and genuinely useful in all
cases — including for a seat that does not comply, which must keep working. If you think the
envelope is the wrong answer, say what is right and why, with evidence. Then build it, or build the
smaller thing that closes the class.

## How to work

Run things. Do not describe what you would do. You are in a sandbox COPY of the repository; the live
repository is not reachable from your seat and must not be. Read
`bench/logs/study_run1b_2026-10-03_20261003T100439Z/runner_state.json` and `console.log` as your
evidence — they are the run's own record. Execute `bench/reference_runner_v3.py`'s functions
directly on that registry rather than reading the source and inferring behaviour: a test that
asserts on SOURCE TEXT shows only that a module describes itself consistently, and 4 defects in this
project have been found by executing 2 forms against each other where reading found none.

Every proportion you report carries a confidence interval, and every computed statistic is
cross-verified with a second tool (scipy with statsmodels, or NumPy with mpmath). A measured rate may
be cited only if the script that produced it is delivered beside it. Numbers in digits, never words.

**Deliver each fix as a file**, written into the sandbox repository tree at its real path — a fix
left in prose or in scratch space is destroyed at teardown and has not been delivered. Deliver a
runnable falsifier for each fix, EXECUTE it, and give its output. A fix you have not tried to break
is a hypothesis, not a fix. Include a mutation check: show that reverting your fix makes your own
test fail, so the test cannot pass vacuously.

**State what would refute you.** For each answer, name the evidence that would overturn it. An
answer with no refutation condition is not falsifiable and will be discounted.

## Output shape — return exactly these fields, per item

Reply as a list, one entry per fault you address, so replies can be compared without a parser
guessing. Wrap the machine-readable part of each entry between `<<<CDSFL_ANSWER_BEGIN>>>` and
`<<<CDSFL_ANSWER_END>>>`; prose outside those markers is read by a human and parsed by nothing.
Per entry, field by field:

- `fault` — the fault number from this brief (1 to 9), or `parser-class`, or `position-A-vs-B`.
- `verdict` — one of CONFIRMED, REFUTED, PARTIAL, UNVERIFIED, for the fault as this brief states it.
- `root_cause` — the mechanism, with file and line. Not a restatement of the symptom.
- `fix_path` — the real repository path you wrote your fix to, inside the sandbox tree.
- `fix_rationale` — why this is the SIMPLEST SUFFICIENT repair, and what it adds rather than removes.
- `composes_with` — the other fault numbers your fix interacts with, and whether the composition
  beats each arm alone or whether a single arm suffices. Say so explicitly if nothing composes.
- `falsifier_path` — the repository path of the runnable falsifier you wrote for your own fix.
- `falsifier_command` — the exact command you ran.
- `falsifier_output` — what it printed, verbatim, including the failure you saw before the fix.
- `mutation_check` — the result of reverting your fix and re-running your test: name which
  assertions failed. A test that still passes with the fix reverted proves nothing.
- `figures` — every number you quote, each with the repository path of the script that produced it.
  A number with no producing script is a claim about evidence, not evidence.
- `refutation_condition` — the specific evidence that would overturn your answer.
- `disagreement` — your strongest disagreement with this brief's own framing, including with its
  measurements. The brief is not authoritative and its figures are open to your challenge; say so
  plainly where you think it is wrong.

Then one final entry with `fault: termination`, stating how many passes you ran and what the last
pass found.

## Where this brief's own figures come from

Every figure quoted above is reproducible from a committed script, named here so you can re-run and
challenge it: `scripts/rk_pairing_reach_2026-10-03.py` (the 109 real sections, the 226 phantoms,
the 95.41% identity reach), `scripts/exhausted_marking_age_lock_2026-10-03.py` (the z3 `unsat`, max age
7, `T <= R - 1`), `scripts/gate_replay_on_registry_2026-10-03.py` (the gate inputs and verdict),
`scripts/a4_blockers_lock_audit_2026-10-03.py` (the per-blocker lock split),
`scripts/routing_severity_gate_2026-10-03.py` (the routing-versus-severity association). The
position-A prevalence figures come from a script delivered with that analysis; if you cannot
re-execute a figure, report it as UNVERIFIED rather than repeating it.

**Termination.** Stop when all hard assumptions have been tested and 2 consecutive passes produce no
new above-threshold findings — this project's own diminishing-returns criterion. A finding is above
threshold if missing it could cause a real-world failure, an unsafe condition or a wrong
convergence verdict. Do not nitpick, do not generate findings for their own sake, and do not police
style.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 37 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_convergence_blockers_2026-10-03) -->

(this seat returned no response text)

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 11 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_convergence_blockers_2026-10-03) -->

(this seat returned no response text)

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_convergence_blockers_2026-10-03/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
