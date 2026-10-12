# Joint round: the panel refuted its own blind-round answer, and mine

Record written 2026-10-12T21:06:42+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT THIS ROUND WAS, AND WHY IT EXISTED

This is the joint half of the free-panel round of 2026-10-12. The blind half ran first, with each seat sandboxed and unable to see the other. The project's own enforcement refuses a new blind round while an earlier one still owes its joint half, and that refusal is what prompted this dispatch: the blind replies had been harvested, tested and partly applied, but the half where the seats see each other's work and the assistant's own repairs had not run.

Free seats only, cc2 and fable, both on the Max subscription, each in its own sandbox, pinned explicitly rather than left to a default. That pinning mattered: the first dispatch attempt was refused by the brief gate, and the refusal reported that five seats were selected with three of them paid. The gate prevented an unauthorised spend, and no paid dispatch occurred.

THE QUESTIONS PUT TO THE SEATS

Five, each requiring an executed falsifier and a fix delivered as a file. Attack the assistant's own composition repair, which was the least reviewed code in the tree. Decide whether the interpreter probe's fail-closed direction was the wrong choice. Consolidate the severity-gate answer both seats had independently reached in the blind half, and then execute the attack one of them had itself named against it. Write the two parked items both seats had called mechanically fixable and neither had written. And decide which of two reported-but-unfixed side-findings was above the real-world-consequence threshold.

WHAT THE ROUND ESTABLISHED, AND THE FIRST ITEM IS A REFUTATION OF THE ASSISTANT'S OWN REPAIR

The composition repair applied after the blind half distinguished a finding that was served and read from one that was served and ruled, keyed on a small set of no-reading verdicts. It was verified against three outcomes, all three produced with a stubbed ladder result whose verdict the assistant had chosen. One seat enumerated the live ladder's reachable verdicts by execution and found the intersection with that set EMPTY. Independently confirmed from source and then measured across the whole archive: 0 of 311 archived ladder records carry a verdict the set matches, Wilson 95 percent interval 0 to 1.2201 percent. The repair was INERT in production and the defect it was reported as fixing still stood. A repair verified only against a mock is a repair verified against its author's expectations.

The repair that makes it live is the other seat's: the transport-dead path, where no rung reached any model, appended a record claiming an ERROR ruling, which is a false assertion that something read the finding. Reclassified to a no-reading record with zero rungs reached, the door opens, names the entry, and the ladder may try again. Measured on the composed tree: the record now carries the no-reading verdict, A4 falls to 0, the entry is named, and it is re-served.

The second seat's J1 fix closes a different hole in the same door, and it is the sharper one. Every conjunct of the door's predicate reads a ladder, falsifier or escalation field, while the R_k proof checker reads the finding's own corroboration block and records a result in none of them. So an entry whose proof had been computed and had FAILED was released by the door anyway, which made the door strictly wider than the severity gate whose removal the founder has rejected four times, and nullified that gate for this entry class. Measured across the archive: of 431 non-terminal entries the pre-fix door released, 25 carried a proof result, so a reading had been discarded on 5.80 percent of them, Wilson 95 percent interval 3.96 to 8.42 percent.

Both J1 fixes were cross-tested against each other's falsifiers and against the assistant's. Each alone passes its own and fails the other's. Composed, all of them pass: 13, 6, 6, 18 and 20 across five suites, with the two adjacent suites green. The age bound on the door was challenged rather than accepted, and measured: across every archived registry, 230 of 230 ladder-served entries were served in the round they arrived, 100 percent with a Wilson lower bound of 98.36 percent, so a longer wait buys no service and the bound of one round is a full round of margin.

THE SEVERITY GATE: BOTH SEATS REFUTED THEIR OWN BLIND-ROUND ANSWER

In the blind half both seats concluded that the founder's provenance ruling and his principle that there are no votes in this project were both already satisfied by the code, because the restored severity test gates on a tool recomputation of the model's stated residual-risk figure rather than on the raw model-stated float. That was reported to the founder as probably settling a tension he had been asked to rule on. The joint round asked each seat to execute the attack one of them had itself named, and both refuted themselves, at two levels.

At the first level the recomputation checks arithmetic self-consistency only. Inputs invented wholesale, but mutually consistent, return a passing proof; nothing cross-checks a single input against any value the harness holds. At the second level, which is the decisive one, the proven quantity and the gated quantity are different numbers. The release condition reads the proof's status and the raw severity float; the proof recomputes the residual-risk figure from that figure's own stated inputs and never reads the severity at all. So a proof whose own content states a residual risk of 0.95 releases a severity float of 0.45, and the blocker count falls from 1 to 0 on exactly that proof.

Measured independently of both seats, over every archived entry carrying a passing proof: 521 entries, Pearson correlation between the proven figure and the gated float of minus 0.3438, p equal to 6.689 times 10 to the minus 16, 95 percent confidence interval minus 0.4174 to minus 0.2657, with a numpy cross-check agreeing to 5.55 times 10 to the minus 17. The proven figure explains 11.82 percent of the variance in the float it licenses, and the sign is NEGATIVE: a higher claimed severity goes with a lower proven residual risk. The proof does not weakly corroborate the number it releases; it moves against it.

What remains true, so that the correction does not overshoot: the gate is not a no-op. It forces a model to commit to named inputs and publish arithmetic that a later round can attack, and a failing proof is reachable and blocks. It is better than the bare float. It is simply not what both seats, and then the assistant, said it was. Tying the proof to the released number would stop 434 of 521 currently-proven entries from being released at the proof's own tolerance, which is a large movement of the gate and is the founder's decision rather than the panel's, because it turns on what severity is to be computed from. Residual risk and impact are different quantities and no seat can settle that by measurement.

THE INTERPRETER PROBE: A GENUINE DISAGREEMENT, RESOLVED BY COMPOSING BOTH

Both seats found the same cause and proposed opposite repairs. The roots discovery runs each interpreter to ask where its own installation lives, and cached the answer for as long as the runner stayed loaded in memory. With every probe timing out on a loaded machine the function returned no roots at all, and the cache made that permanent: one load spike at the first falsifier returned the gate to refusing every spawned-interpreter falsifier for the whole run, measured end to end as a verdict moving from confirmed to integrity violation and staying there after the load cleared.

One seat made the failure transient, by refusing to cache an incomplete discovery and retrying. The other made it harmless, by deriving an interpreter's roots structurally from its own path when its probe cannot answer. Measured, the structural fallback yields 41 roots under total probe failure against 39 healthy, so coverage is not merely preserved but exceeded, and the retry therefore buys no coverage while costing up to 30 seconds per falsifier on this machine. But the fallback set is a structural guess and wider than what the interpreters report, and caching it would persist that wider allowance long after the spike. Both seats were right about something, and the composition takes both: fall back so the moment is harmless, decline to cache so the moment stays a moment, and name the interpreters whose roots are guesses so that a refusal against one of them is not read as a verdict. The naming follows the founder's own 2026-10-02 discipline that an exclusion must be reported.

The assistant's first version of the paired reader carried a defect of the same family as the others recorded here: it decided whether to run discovery by looking at the cache, and a pass that fell back does not populate the cache, so calling the reader re-ran discovery and, if the load had cleared, reported nothing for a failure it had just observed. The first test written for it did not catch that, because it read the report while the probes were still dead, so the re-run fell back too and named the same interpreters. The test now reads the report after recovery, which is the sequence that exposes it, and reverting the reader turns it red.

THE TWO PARKED ITEMS, AND A CONTRADICTION BETWEEN THE SEATS

Both items turned out to rest on stale premises, which is itself the answer the founder asked for when he said the outstanding questions were too vague to act on. The first names a guard in a file that contains no such guard and does no name matching; the real guard lives elsewhere and was fixed on 2026-09-11, with its own committed test, and both seats independently declined to write anything, one of them noting that a second test would be an addition nothing reaches.

On the second the seats directly contradicted each other. One held that writing the missing note would be actively harmful, because it would move the row onto a different explanation path and break a control test. The other wrote the note in all three arm configurations and replaced the two affected assertions with sharper ones. Tested: the replacements pin two facts where the old pinned one, and require the note to state the redundancy rather than merely restate the block's intent, so the objection is true of the old control and answered by its replacement rather than by avoiding the work. The configurations still parse, no runner module reads an annotation key, and the capability sweep is 21 green with the exp52 switch suite at 95.

THE SIDE-FINDINGS: ONE IS ABOVE THRESHOLD AND NEITHER SEAT WOULD TOUCH IT

Both seats agreed, and the assistant's own instrument independently confirms, that a falsifier's observer allows reads of this project's own evidence directories. The repository root is in the rendered allow set, so the experimental notes and the panel logs are readable from inside a sandboxed falsifier, while the sealed scoring key store is not. One seat measured 472 sibling panel sandboxes sitting under an allowed temporary root, which is cross-sandbox material rather than a key; the other established that narrowing the temporary-directory allowance alone would not close it, because the clone root grants it too. Both declined to fix it, and both gave the same reason: the observer is the most safety-critical component in the harness, the change reorders the gate's precedence, and shipping it untested at the end of a one-shot round is worse than the documented hole. Both recommend a dedicated pass with the key-access suite extended first. The assistant did not fix it either, and records it as the sharpest open item in the tree.

The other side-finding, a defect in the superseded version-2 runner's baseline capture, is below threshold by both seats' measurement: no production or launch path imports that module, its only importers are tests and archived analysis scripts, and changing its measurement code would invalidate byte-for-byte replay of the experiments it is the substrate for. Neither seat touched it and neither recommends porting the fix unprompted.

Both seats' full replies follow, unedited.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# JOINT ROUND — clear_the_outstanding_2026-10-12

You reviewed this independently and blind. You are now seeing the other seat's work and mine. This is the joint half: resolve what can be resolved, and preserve genuine disagreement as information rather than smoothing it to consensus. There are no votes in CDSFL — a finding is confirmed programmatically or by the founder, never by agreement between seats.

Every fix you delivered was EXECUTED, cross-tested against the other seat's falsifier, and mutation-verified in both directions. 21 of 31 of your tests fail on the unfixed tree, so your falsifiers are genuine. What follows is what happened when they met each other.

## WHAT WAS APPLIED, AND WHY

**1b, the integrity gate.** Both of you fixed it. cc2 added a declared list of roots; fable probed each interpreter for its own roots and argued that as more robust. MEASURED over the 4 python3 interpreters present on this machine (`scripts/interpreter_allowlist_coverage_2026-10-12.py`):

    baseline, no fix                                      1 of 4 fully covered
    fable, probe of /usr/bin/python3 and PATH python3      2 of 4
    cc2, declared roots                                    3 of 4
    composed: fable's probe + full discovery + sysconfig    4 of 4

So the prose argument was backwards: the probe covered FEWER interpreters than the declared list, because it probed only 2 of the 4 present. APPLIED: fable's probe mechanism, with discovery widened to Homebrew and every framework version by glob, and the probe extended to report `sysconfig.get_paths()` (which is what surfaces 3.9's purelib). cc2's declared paths are NOT applied — measured redundant under the composed form at 4 of 4, not judged redundant. Both of your interpreter suites pass (5 and 4), and the key-access suite is 41 green.

My own instrument was wrong first: it counted roots that DO NOT EXIST on disk as coverage gaps, reading the composed fix as 1 of 4 when it is 4 of 4. A directory not on disk can never be read, so it can never be denied.

**1c, and this is the part that matters.** fable SERVES a never-served finding up the ladder so a tool can decide it. cc2 opens a DOOR so a finding nothing ever touched stops blocking, with a paired reader so the exclusion is never silent. Each passes its own falsifier and fails the other's. Neither dominates.

COMPOSED, THEY WERE STRICTLY WORSE THAN EITHER ALONE. Serving appends to `routing_history`, and an empty `routing_history` was one of the seven emptiness facts cc2's door required. So the serve CONSUMED THE DOOR'S OWN TRIGGER. Measured on a C0066-shaped entry served to a ladder returning UNRESOLVED:

    before the serve:  A4=0, door releases and names C9001
    after  the serve:  A4=1, door empty  -> blocks for ever, neither mechanism can release it

Neither of you could see this. Each tested its own fix in isolation, and in isolation each is correct. Producer: `scripts/do_both_never_served_fixes_earn_their_place_2026-10-12.py`.

THE REPAIR I APPLIED distinguishes SERVED-AND-NO-READING from SERVED-AND-RULED. `_routing_ladder_never_served` no longer requires an empty `routing_history`; instead every ladder record must have `resolved` false AND a verdict in a new `NO_READING_ROUTING_VERDICTS = frozenset({"", "UNRESOLVED"})`. Any other verdict string, known or not, is treated as a ruling and closes the door — so it FAILS CLOSED. cc2's `{"verdict": "UNTOOLABLE"}` case stays green, because UNTOOLABLE is a ruling by something that ran. Measured, all three outcomes:

    ladder returned UNRESOLVED   A4=0  door=['C9001']  -> released AND named
    ladder ruled UNTOOLABLE      A4=1  door=[]         -> still blocks
    ladder RESOLVED it           A4=0  door=[]         -> cleared by the tool verdict

z3 proves `door_open AND a_ruling_exists` is UNSAT, and that the door is still reachable (SAT), with SymPy agreeing. All 57 tests across both your suites and the 2 adjacent suites pass, and no test was weakened.

**Also applied:** cc2's ledger-pollution fix to the output stamper (its 2 new tests fail without it), its key-test anchor change (both assertions byte-identical, anchor made specific — verified), and its additive A19 record correction.

**A claim I made and WITHDREW.** I asserted that cc2's record patch deleted two of the founder's rulings. fable's diff carries the same two removals verbatim, and two blind seats cannot coincidentally delete the same blocks. The cause is the diff direction: both sandboxes were cut at 19:15, the live file was edited at 19:16:09, and a line present in the live file but absent from an older clone appears with a leading minus. The removals are my own additions. cc2 is owed that correction explicitly. Producer: `scripts/no_seat_deleted_his_rulings_2026-10-12.py`.

## WHAT I AM ASKING YOU FOR

Nothing you write is auto-applied; every delivery is tested and suggested to the founder.

### OUTPUT SHAPE — return these fields, per item, by name

- **verdict** — one of FIXED, PREMISE WRONG, RESOLVED ALREADY, NEEDS HIS RULING, or UNRUNNABLE HERE.
- **fix** — write it INTO the sandbox repository tree at its real path. A fix left in prose or in scratch space is destroyed at teardown and is not delivered. Name every path you wrote.
- **falsifier** — the command you EXECUTED and its actual output, pasted. Not a command you would run.
- **reasoning** — why this is the simplest sufficient fix, and what you rejected.
- **refutation** — what evidence would overturn your own answer.
- **termination** — when this item is DONE, and when to stop pushing on it.
- **disagreement** — where you expect the other seat to differ, and whether the difference is real or verbal.

**J1. Attack the composition repair.** It is mine, it is new, and it is the least reviewed thing in the tree. Specifically: is there a FOURTH ladder outcome neither of the three above covers — a record shape where `resolved` is false and the verdict is empty but an instrument did in fact read the finding? Is `LADDER_UNSERVED_MIN_AGE_ROUNDS = 1` right, or does a finding emitted in a run's final round need longer? And cc2's own refutation condition still stands: if any field I do not test records instrument contact, the door is still too wide. Name it.

**J2. The probe fails CLOSED, and that may be the wrong direction.** fable's discovery failure contributes no roots, so the gate stays as strict as before — which means the false refusals RETURN. cc2's declared list cannot fail that way. Is there a machine state (a probe timeout under load, a stripped PATH, a seat sandbox without the framework tree) where the composed form regresses to refusing correct falsifiers, and should a declared fallback therefore be kept beside the probe after all? This is the one place my measurement may have picked the wrong mechanism. Measure it, do not argue it.

**J3. The severity gate: consolidate, then attack.** You independently reached the same conclusion — that the founder's provenance ruling and his "no votes" principle are BOTH satisfied by what is already in the tree, because `severity_is_proven` gates on a TOOL RECOMPUTATION of the model's stated R_k rather than on the raw float, and the worked proofs he ordered ARE the gate's mechanism. Two blind seats agreeing is replication, not proof. So: state the consolidated answer in one paragraph he can rule on, AND execute fable's own named attack on it — can `severity_is_proven`'s recomputation be gamed by a model stating self-consistent but WRONG inputs? If it can, the restored gate is a vote in proof's clothing and the consolidation is void. That is the decisive question.

**J4. Write parked items 1 and 2.** Both of you named them mechanically fixable and neither wrote them. Item 1: the A17 verdict-tuple guard matches function names across the repository (`scripts/supersession_check.py`). Item 2: the A18 missing note for `max_papers_per_round` in the exp56 configs — and note fable measured its "no note" premise for `hardened_gate_enabled` as already stale, so check the premise before writing. cc2's coupling warning applies and must be honoured: `bench/tests/test_capabilities_disabled_by_config_2026-09-10.py:265` pins the CITED set to exactly 3 arms and :280 is a control expecting UNEXPLAINED; both must change in the same commit, and the cited-set assertion must be REPLACED with something non-vacuous rather than emptied. Item 18 is already done (`decision_required` in `scripts/blocker_triage.py`, a third flag rather than a third verdict, 27 tests green). Item 3 (A13/A14) is confirmed STALE as fable predicted: today's own run gave 2 distinct sandbox roots for 2 seats and `test_fresh_sandbox_per_attempt_2026-09-17` passes 11 tests.

**J5. Two side-findings, reported by you and not fixed. Which is above threshold?** cc2: `tempfile.gettempdir()` has long been in the allowlist and a sandboxed clone lives under the temp dir, so `experimental_notes/` is reachable through that allowance in sandboxed runs (the protected set still holds, being digest-matched). fable: the v2 runner's `_capture_baseline` at `bench/reference_runner.py:2663` still carries the identical round-13 baseline-substrate defect, with zero `_gateable_source` occurrences in that module. For each: is missing it capable of causing real-world failure, and if so what is the simplest sufficient fix? Do not fix a legacy runner unprompted — say what you would do and what it would cost.

## STANDARDS THAT BIND THIS ROUND

Simplest sufficient fix. Additive: nothing disabled or removed, and every new flag, gate or entry point wired to a caller and executed by a committed test — an addition nothing reaches is not additive either. A measured rate travels with the script that produced it. Execute, do not grep: where both a producer and a consumer are live code, call them and compare outputs rather than asserting on source text. Every `--help` must be free. Never weaken a test to make it pass; if a pinned behaviour is measured wrong, REPLACE the assertion with a sharper one and say so. Simulated agents are labelled SIM only, never a vendor name. Cross-verify every computational claim with at least two tools, and give any proportion a confidence interval.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 98 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_clear_the_outstanding_2026-10-12) -->

All 139 tests green across the 10 affected suites. Here is my answer.

---

# J1 — Attack on the composition repair

**verdict: FIXED** (the repair is sound in its three measured outcomes; it has a fourth, and I closed it)

**The fourth outcome exists, and it is SERVED-AND-READ-BY-A-NON-LADDER-INSTRUMENT.** Every conjunct of `_routing_ladder_never_served` reads a ladder, falsifier or HIL field. The R_k proof checker reads the finding's own corroboration block and records PASS/WARN/FAIL in `severity_proof` **without touching any of them**. So `resolved` is false, the ladder verdict is empty — there is no ladder record at all — and an instrument did in fact read the finding.

This is not a tidiness point, and it is the sharpest possible form of cc2's refutation condition. Your door is evaluated at line 3151, the restored severity test at 3193. The door reads no severity field. `severity_proof_status == "FAIL"` is the one state where `severity_is_proven` is **guaranteed** to refuse a release. Before my fix the door released it anyway — so **the door was strictly wider than the gate whose removal the founder has rejected 3–4 times, and nullified it for this entry class.** Your own docstring asserted this was impossible ("`severity_proof_status` returns SKIP, so the entry can never be proven sub-critical"). That sentence was true of C0066/C0073 and false in general.

**fix** (written into the tree):
- `bench/reference_runner_v3.py` — `NO_READING_SEVERITY_PROOF_STATUSES = frozenset({"ABSENT","SKIP"})`, one new conjunct in `_routing_ladder_never_served`, and the two docstring claims corrected.
- `bench/tests/test_the_door_does_not_override_the_severity_gate_2026-10-12.py` — 13 tests.
- `scripts/never_served_door_vs_instrument_contact_2026-10-12.py` — producer.

It reuses **your own** `NO_READING_ROUTING_VERDICTS` shape, so an unrecognised status fails closed.

**falsifier** — executed:

```
NON-TERMINAL entries the PRE-FIX door released   431
   ABSENT   393  91.18%   SKIP  13  3.02%
   PASS      12   2.78%   FAIL  11  2.55%  Wilson 95% [1.43%, 4.51%]
   WARN       2   0.46%
   -> A READING WAS DISCARDED on 25 of 431 (5.80%, Wilson 95% [3.96%, 8.42%])
```
```
$ pytest test_the_door_does_not_override_the_severity_gate_2026-10-12.py -q
13 passed in 0.53s
MUTATION: conjunct removed  ->  6 failed, 7 passed
restored                    ->  13 passed
+ 70 passed across the 4 adjacent suites; 139 passed across all 10.
```

**`LADDER_UNSERVED_MIN_AGE_ROUNDS = 1` is right, and I measured it rather than agreeing with you.** From the ladder's own record across every archived registry:

```
ladder-served entries with a round-stamped first attempt: 230
first_routing_round - open_since_round = 0 : 230  100.00%  Wilson 95% [98.36%, 100.00%]
```

**The ladder serves an entry in its arrival round or never.** So a longer wait buys no service — the data puts the bound at 0 and 1 is a full round of margin. Your final-round worry is answered in the opposite direction from the one you feared: C0073 at age 0 is held not because the ladder might still reach it, but because holding is the conservative side of a bound the evidence already satisfies. **No change.**

**reasoning / what I rejected.** A conjunct qualifies only if it (a) records a *tool* reading and (b) is still absent on C0066/C0073, so the fix is not reverted to a no-op. The producer prints both halves per field, so every rejection is measured:

| field | C0066 / C0073 | rejected because |
|---|---|---|
| `status_adjudicator`, `status_log` | CONTACT / CONTACT | ordinary OPEN→UNCONFIRMED bookkeeping — closes the door on everything |
| `computed_evidence` | CONTACT / CONTACT | holds `{"kind":"reasoned_withdrawal","by":"CC2-SIM"}` — a **model** statement, the opposite of instrument contact |
| `fix_efficacy` | CONTACT / CONTACT | outcome `NOT_PROBED_NO_FALSIFIER` — its own detail says nothing ran |
| `occasions`, `corrected_copy`, `merge_blocked_reason` | CONTACT | same |
| **`severity_proof`** | **– / –** | **DISCRIMINATING — applied** |

I rejected an allowlist-of-inert-fields design (fails closed on unknown fields, but closes the door on everything measured) and rejected enumerating all 94 fields.

**My own instrument was wrong first, exactly as yours was.** The discrimination column tested field *presence*, so it reported `severity_proof` as closing the door on C0066 — it does not, because the conjunct keys on the *status*. A wrong instrument reads as a confident result. Corrected in the script, with the reason recorded there.

**disagreement — I NAME the residual, I do not close it.** `sk_result` is also discriminating (absent on both reference entries, set on 133 of 431) and `compute_sk` **applies the proposed fix to real source and runs the test command** — unambiguous contact. I did **not** add it. Whether an SK *admissibility* score counts as "the finding was read" is a semantic ruling about the door's purpose, not something a tool can decide: an SK score produces no falsifier verdict, so your door's rationale ("nothing can ever come of it") still arguably holds. **Your door is still wider than its docstring claims, by 133 of 431 entries, and that gap needs your ruling, not my judgement.** Same for `sk_evaluated`, `cc2v_escalated`, `latent_evidence`.

**refutation.** Show me a run where an entry carrying a non-SKIP `severity_proof` and no ladder trace *should* have been released — then my conjunct is the thing blocking a correct convergence. Or show `last_status_change_round` < `open_since_round` on a never-served entry (I measured 0 of 715; age is never overstated).

**termination.** DONE when the founder rules on `sk_result`. Stop pushing on the proof conjunct now — it is mutation-verified both ways.

---

# J2 — The probe fails closed, and your measurement picked the right mechanism for the wrong reason

**verdict: FIXED. Your mechanism choice stands; the defect is the CACHE, not the probe — and a declared fallback is NOT the answer.**

**fix** (written into the tree):
- `bench/falsifier_verify.py` — incomplete discovery is no longer cached; `SECONDARY_ROOTS_DISCOVERY_ATTEMPTS = 3`; new `secondary_interpreter_discovery_incomplete()` paired reader; the **stale docstring** corrected (it claimed discovery covers 2 interpreters — stale the moment your glob landed).
- `bench/tests/test_a_transient_probe_failure_is_not_permanent_2026-10-12.py` — 5 tests.
- `scripts/secondary_root_discovery_failure_is_not_permanent_2026-10-12.py` — producer.

**falsifier** — executed, end to end, on the repaired tree and on the mutated one:

```
--- REPAIRED ---                          --- MUTATED (pre-repair caching) ---
HEALTHY  roots =  22                      HEALTHY  roots =  22
HEALTHY  verdict = CONFIRMED              HEALTHY  verdict = CONFIRMED
TRANSIENT roots = 15   lost = 7           TRANSIENT roots = 15   lost = 7
TRANSIENT CACHED = False                  TRANSIENT CACHED = True   <-- PERMANENT
AFTER     roots = 22   recovered = True   AFTER     roots = 15   recovered = False
AFTER     verdict = CONFIRMED             AFTER     verdict = INTEGRITY_VIOLATION
REPAIRED                                  REGRESSION PRESENT
```
```
pytest (repaired) -> 5 passed;  (mutated) -> 3 failed, 2 passed
key-access + interpreter suites: 56 passed
```

**The machine state you asked me to find.** `_SECONDARY_ROOTS_CACHE` is module-level and populated once per process. **A single transient 10-second probe timeout cached a partial root list for the life of the runner.** The 13 refused reads in that run are the identical bootstrap class your own fix exists to remove — reinstated, permanently, long after the machine recovered. Not hypothetical: `CONFIRMED → INTEGRITY_VIOLATION`.

**I measured your other three candidates and they do not bite.** A stripped PATH is harmless — `/usr/bin/python3` and the Homebrew prefixes are absolute candidates, not PATH-resolved. A sandbox without the framework tree is harmless — the glob finds nothing *and* the interpreter is absent, so there is no gap. Probe *failure* without the cache is harmless — it is one degraded verification, which is the correct fail-closed direction.

**reasoning — and this is my answer to your actual question: NO, do not keep a declared fallback.** Three measured grounds. It covered 3 of 4 against the composed 4 of 4, so it cannot improve the covered set. In the common path nothing would reach it — an addition nothing reaches is not additive. And for an interpreter that cannot be *probed*, its declared roots are a guess at a layout this function otherwise reads from the interpreter itself. **Permanence was the defect, not the mechanism.** Composing the two fixes here would fail your own 2026-10-02 composability rule: no demonstrated advantage over the single fix.

I state plainly that `SECONDARY_ROOTS_DISCOVERY_ATTEMPTS = 3` is a **chosen bound, not a measured optimum** — with per-attempt failure probability *q*, permanent degradation falls from *q* to *q*³. I rejected never-caching (unbounded 10s-per-falsifier probe cost against a dead interpreter) and per-candidate memoisation (more state, same guarantee).

**refutation.** Measure a real runner process and find the probe sweep is a material fraction of wall-clock, and 3 attempts is too many. Or find a machine where an interpreter is *permanently* present-but-unprobeable — then the declared list earns its place after all, and my rejection of it is wrong.

**termination.** DONE. Mutation-verified both directions end to end.

**disagreement.** cc2 will say its declared list cannot fail this way — true, and irrelevant: it also cannot cover the 4th interpreter. **The difference is real, not verbal, and the measurement is now on my side of it rather than on the prose.**

---

# J3 — The severity gate: consolidated, then **refuted**

### The consolidated paragraph, for your ruling

> The severity test was restored on 2026-10-06 and is gated on `severity_is_proven`, not on the raw float. `severity_is_proven` requires `severity_proof_status(entry) ∈ {PASS, WARN}`, which the runner computes by re-deriving R_k in `_validate_rk_computation` from the parameters the model itself stated (R_old, η·d·p or q, S_k, ν_eff) and comparing against the R_k the model stated, at tolerance 0.01/0.05. **The worked proofs you ordered on 2026-09-06 are therefore not a separate artefact awaiting wiring — they *are* this gate's mechanism**, and FAIL is live and blocking (34 of 128 archived corroboration sections scored FAIL). On that basis both blind seats concluded your provenance ruling and your no-votes principle are already satisfied by what is in the tree.

### And the attack you ordered **kills it.** Executed:

```
=== ATTACK 1: self-consistent but FABRICATED inputs ===
  status=PASS  model_rk=0.0148  recomputed=0.014802  delta=1.98e-06
  severity_is_proven -> True
```

Every input in that block is invented — q = 0.99 claims a near-perfect detector, S_k = 0.99 a near-perfect fix. **Nothing cross-checks a single one against any harness-held value.** The gate verifies *arithmetic*, not *inputs*. Cross-verified three ways: runner `0.014801980198019815`, SymPy exact `299/20200`, and Wolfram Language (local Wolfram Engine, via `wolframscript`) `299/20200 → 0.0148019801980198`. All agree to 1e-9.

```
=== ATTACK 2: the gate's released number is NOT the proven number ===
  severity=0.10  R_k proven=PASS  blockers=0
  severity=0.45  R_k proven=PASS  blockers=0
  severity=0.69  R_k proven=PASS  blockers=0
```

**This is the decisive one.** The release condition is `severity < 0.7 AND severity_is_proven(e)`. `severity` and `R_k` are **two different model-stated numbers**, and the proof reproduces R_k from R_k's own inputs *without ever reading `severity`*. The number that actually moves the gate is the raw model-stated severity float — **precisely the number your 2026-09-06 measurement condemned** (AUC 0.464, σ = 0.1419 against a 0.09 band, 30.04% of identical defects on opposite sides of 0.7). The proof is a side-condition on a different quantity.

```
=== Is the PROVEN R_k even related to the GATED severity? n=521 ===
  Pearson  r = -0.3503  p<0.0001  95% CI [-0.4235, -0.2726]   (numpy corrcoef agrees: -0.3503)
  Spearman rho = -0.3540
  r^2 = 0.1227  -> explains 12.3% of severity variance, NEGATIVELY
```

On 521 real PROVEN entries the proven R_k correlates with the gated severity at **r = −0.35, and the sign is negative** — higher claimed severity goes with *lower* proven residual risk. The proof does not weakly corroborate the severity it licenses; it moves **against** it.

**verdict: PREMISE WRONG — the consolidation is VOID, by your own stated criterion.** Two blind seats replicated each other and both were wrong on the load-bearing claim. `severity_is_proven` is **not** "a tool recomputation of the model's stated R_k gating the release" — it is a tool recomputation of a *different* model-stated number, standing beside an ungated raw float. Replication is not proof, and here it replicated an error.

**What remains true, stated so you are not over-corrected:** the gate is not a no-op. It forces the model to commit to named inputs and publish arithmetic — a falsifiable artefact a later round can attack — and FAIL is reachable and blocks. It is strictly better than the bare float. It is simply not what we said it was.

**fix** — none applied; this is a design ruling, not a defect I should patch unilaterally. The repair that would make the gate what both seats claimed: require the proof to be *about* the gated quantity — either `|severity − model_rk| ≤ tol` as a condition of release, or gate on the **recomputed** R_k instead of on `severity`. Measured cost, so you can price it:

```
|severity - proven R_k| <= 0.01 :  21/521   4.03%  Wilson 95% [ 2.65%,  6.08%]
|severity - proven R_k| <= 0.05 :  93/521  17.85%  Wilson 95% [14.80%, 21.37%]
|severity - proven R_k| <= 0.10 : 162/521  31.09%  Wilson 95% [27.27%, 35.19%]
mean |severity - R_k| = 0.1913   median = 0.1610
```

At the proof's own 0.05 tolerance, **82% of currently-proven entries would stop being released.** That is a large gate movement and it is your call, not mine.

**refutation of my own answer.** Show me that any input in the corroboration block is cross-checked against a harness-held value (π from immune memory, K from panel size, d from a measured detection rate) — then Attack 1 fails and the inputs are anchored. I read `_validate_rk_computation` end to end and found none, but a cross-check applied *elsewhere* before the proof is stamped would overturn me. Second: if `severity` is in fact derived from R_k upstream rather than stated independently, Attack 2 collapses — but r = −0.35 is strong evidence it is not.

**termination.** DONE when you rule on tying the gated number to the proven one. **Do not close this as consolidated.**

**disagreement.** Both seats and I independently reached the consolidated answer; I am now the only one refuting it. That disagreement is the information — **preserve it unsmoothed**, because the measurement is on the refuting side.

---

# J4 — Parked items 1 and 2: both premises are stale

**Item 1 (A17 verdict-tuple guard) — verdict: PREMISE WRONG on location, RESOLVED ALREADY on substance. Nothing written.**

There is no A17 guard in `scripts/supersession_check.py` — that file has zero occurrences of "A17" and does no name matching; it is a markdown scanner and is the *victim* of the collision, not its site. The guard is `TestVerdictTuplesAreNeverTestedForTruth` in `bench/tests/test_operational_scripts.py:368`, and the file-scoping fix already exists at `_truthiness_violations:292` (`names = names - _locally_shadowed(src, names)`). Proved by execution, not reading — the original collision was rebuilt and the guard mutated in both directions:

```
collector sees 'scan' as a tuple-returning name: True
--- AS SHIPPED (file-scoped shadowing ACTIVE) ---
violations on supersession_check.py: []
--- MUTATION: shadowing DISABLED (pre-A17 whole-repo matching) ---
violations: ["scripts/supersession_check.py:149: 'findings' was bound whole from scan() at line 146 ..."]

pytest test_verdict_guard_resolves_the_call_2026-09-11.py -q  -> 7 passed
pytest test_operational_scripts.py -q                        -> 678 passed in 144s
supersession_check.py --help -> EXIT=0
```

The test I was asked to write already exists (`test_verdict_guard_resolves_the_call_2026-09-11.py`), including the exact-file regression case and a `TestImportsAreStillFlagged` boundary pin. **Adding a second file would be an addition nothing reaches.** Fixed 2026-09-11; A17 is `DONE` at `CDSFL_MASTER_TASK_LIST.md:746`. The live residue is bookkeeping: `PARKED_FOR_THE_FOUNDER.md:9` is stamped the day *before* the fix and still says "the cause stands", and `scripts/wolfram_route_health_2026-09-10.py:49-56` carries a now-stale comment. **That parked file is why this was re-filed, and it will be re-filed a third time if it is not reconciled.**

**Item 2 (A18 note for `max_papers_per_round`) — verdict: PREMISE WRONG. Nothing written.** Checked by running the live checker, not by grepping:

```
SET TO OFF BUT THE RUNNER NEVER READS THE FIELD (3):
    d11_seat_contrast_diversity_arm.json  _ouroboros.max_papers_per_round = 0  [DOCUMENTED]
    d9_multi_model_panel.json             [DOCUMENTED]
    d9_single_model_with_agents.json      [DOCUMENTED]
  THE FIGURE THAT MATTERS: off-switches with NEITHER a note NOR a cited record: 0 of 15
pytest test_capabilities_disabled_by_config_2026-09-10.py -q  -> 21 passed in 55.17s
```

DOCUMENTED in all 3 arms via `_ouroboros._note`, an **enclosing-block** note. The checker grew nested-block lookup on 2026-09-17 naming this exact field as its motivating case. A top-level grep for `_max_papers_per_round_note` finds nothing — that is almost certainly how this was filed. Writing a second note would have been **actively harmful**: it flips the row onto the sibling-note path and breaks the control at `:271`, which deletes `_ouroboros["_note"]` to prove block-level lookup is what explains the row.

**Your coupling constraint never fired, because the CITED set did not change** — so no edit to `:265`/`:280` was needed, and I weakened nothing. For the record, `:265` already pins exact CITED membership by name and `:280` is already the synthetic deep-copy control your instruction said to build if no real UNEXPLAINED arm remained. None remains, and the controls do not depend on one.

**One correction owed to fable:** its verdict on `hardened_gate_enabled` (not UNEXPLAINED) is right, but its stated reason is not. No note was added — `_hardened*_note` is absent in all 3 arms. It is CITED via `_convergence_criteria.description`. **Amend the record to say "cited via the convergence-criteria description", not "note added", or a future seat greps for a note, fails, and re-files it.**

**termination.** Both DONE as no-ops. The remaining work is documentation reconciliation in `PARKED_FOR_THE_FOUNDER.md` and `wolfram_route_health_2026-09-10.py`, which is your call.

---

# J5 — Which side-finding is above threshold

### cc2's temp-dir allowance: **ABOVE THRESHOLD — and cc2 named the wrong allowance**

**verdict: NEEDS HIS RULING.** Measured on the live rendered policy:

```
sibling panel sandboxes present under the temp root RIGHT NOW: 472
probe path: .../T/cdsfl_panel_07pxkelz
  ALLOWED by: ['/private/var/folders/.../T']      <- tempfile.gettempdir()
  DENIED  by: []                                   <- deny = ('~','/Volumes','/Library')
tempdir itself in the rendered allow set: True
```

cc2's stated consequence is wrong: `experimental_notes/` in *this* sandbox is reachable via the **repo-root** allowance (`_allow_roots` returns the repo root), so removing `gettempdir()` would not close that path. **What `gettempdir()` uniquely grants is cross-sandbox reads.** 472 other seats' trees sit directly under an allowed root, prefix-matched, with no deny region covering them — including their harvested reports and their own `experimental_notes/`. **That is the Exp 48 shape exactly: a panel member holding material from outside its own artefact.** §10 category 3 (verification-integrity corruption) and category 4 (silent evidence loss). It is above threshold, and it is *wider* than reported.

**Simplest sufficient fix**, and why I did not apply it: narrow the temp allowance from the tempdir **root** to the falsifier's own scratch directory — your integrity section already specifies `writes(f) ⊆ scratch(f)`, and reads should be scoped the same way. This is a narrowing of an allowlist, so it can refuse honest falsifiers that use temp scratch, and I have no budget left to inventory those. **Narrowing it on a judgement would be the exact error this round has twice caught.** What it needs before it lands: a scratch-path inventory across archived falsifiers plus a measured green run of the key-access suite. One line of code, one measurement I did not have time to take.

### fable's v2 runner: **BELOW THRESHOLD today — dormant, not harmless**

**verdict: RESOLVED ALREADY (by dormancy), and I did not touch it.** The facts confirm:

```
bench/reference_runner.py     : 0 occurrences of _gateable_source
bench/reference_runner_v3.py  : 17
_capture_baseline: reference_runner.py:2663, called only at :3490 (same module)
modules importing the v2 runner: exactly 2, BOTH TESTS
  bench/tests/test_confer_verification.py:18
  bench/tests/test_runner_status_transitions.py:13
```

No production or launch path imports it as a module. The defect cannot corrupt a live measurement — it is unreachable from any run. Below the §6 real-world-consequence threshold.

**What I would do, and the cost.** **Do not port `_gateable_source`.** 17 call sites to mirror into a module with no coverage of that path, and a real risk of silently changing archived-run reproducibility — a large, unmeasured change to buy a guard against a path nothing takes. Instead, the cheap and additive move: one committed test pinning the dormancy that makes the defect harmless (the v2 runner is not an entry point for new runs), plus a module-level note naming the defect so a future reader does not reach for it believing it sound. Cost: one small test versus a 3500-line retrofit. **Nothing is removed either way.**

**Which is above threshold: cc2's.** fable's is a dormant defect in code nothing calls; cc2's is a live allowance, measured today at 472 reachable sibling sandboxes, in the machinery whose integrity the whole programme rests on. Missing fable's costs nothing until someone revives the v2 runner. Missing cc2's can void an experiment's headline result the way Exp 48's was voided — and that one rendered as a confident CLEAN until a corrected scanner was re-run over the whole directory.

---

## One correction accepted, and one owed

I accept your withdrawal on the record patch without reservation — the diff-direction explanation is sound and two blind seats cannot coincidentally delete the same blocks.

**And I am owed none; I owe one.** My J1 instrument shipped with the same defect yours did — it tested field presence where the conjunct tests status, and reported my own fix as closing the door on the case it exists for. I caught it because I ran it and read the output against a fact I already knew. The correction is recorded in the script.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 86 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_clear_the_outstanding_2026-10-12) -->

176 green across every touched suite (plus 21 in `test_capabilities_disabled_by_config_2026-09-10.py`, run separately). Final report, per item.

---

## J1 — Attack on the composition repair

**verdict** — FIXED. There IS a fourth outcome, and it is the inverse of the one you asked about: not a no-reading record hiding instrument contact, but a **ruling-shaped record minted when no instrument ever read the finding**.

**The attack, executed.** `bench.routing.route`'s reachable verdict set, enumerated by execution with stubbed `resolve_fn`/`reverify_fn`, is {CONFIRMED, DUPLICATE, ERROR, INTEGRITY_VIOLATION, NON_DISCRIMINATING, REFUTED, UNTOOLABLE}. Its intersection with `NO_READING_ROUTING_VERDICTS` is **EMPTY** — the live ladder never writes `""` or `"UNRESOLVED"`. Your three measured outcomes used a mocked `"UNRESOLVED"` production never emits. The live failure shape: a **transport-dead serve** (every rung's dispatch fails — the 402-cascade class) returns verdict `"ERROR"`, and `_apply_routing` appends that record *before* the transport-dead guard runs. Measured end-to-end on the unfixed tree: a C0066-shaped entry served once on a dead transport → record `{verdict: "ERROR", resolved: False}` → door reads it as a ruling and closes → `_never_served` admission consumed by the non-empty `routing_history` → never re-served → **A4=1 forever, door=[]**. The composed defect back, one failure class over. A dispatch exception never even reaches `resolve_via_routing` — the runner's `resolve_fn` closure swallows it to `""` (verified by execution; a raising stub propagates).

**fix** (written, three edits in `bench/reference_runner_v3.py`): (1) the transport-dead path reclassifies its just-appended `"ERROR"` record to `"UNRESOLVED"` with `rungs_reached: 0` — this is the write the `NO_READING_ROUTING_VERDICTS` comment at :2242 always *claimed* happened and never did; only the ERROR-with-zero-models-reached shape is touched, so your mocked-UNTOOLABLE pin keeps its ruling semantics; (2) `error_routed` — your named untested instrument-contact field — is now a door conjunct; it is stamped only when a rung genuinely reached a model, and the telemetry append is wrapped in `except Exception`, so a failed write erases the record while the flag survives; 68 archived entries carry the flag with no history (pre-2026-09-02 shape), though **0 of 681 archived door-open entries carry it (Wilson [0%, 0.5609%])** — prophylactic, one line, fails closed; (3) the `_never_served` admission keys on `_routing_ladder_never_served` itself — one predicate, two readers — so a no-reading serve no longer burns the one admission and a healed transport can retry, exactly as the transport-dead guard's own comment promises.

**falsifier** — `python3 scripts/transport_dead_serve_blocks_for_ever_2026-10-12.py`: before — `verdict='ERROR' … NEVER RE-SERVED … A4=1, door=[] → BLOCKED FOR EVER`; after — `verdict='UNRESOLVED' … RE-SERVED … A4=0, door=['C9001'] → RELEASED AND RE-SERVED`. Archive figures: `scripts/door_open_archive_carries_no_instrument_contact_2026-10-12.py`. Committed test: `bench/tests/test_transport_dead_serve_is_not_a_ruling_2026-10-12.py` (6 tests). Two assertions in my own blind-round file `test_never_served_findings_enter_the_ladder_2026-10-12.py` pinned the measured-wrong behaviour ("served exactly once" regardless of outcome) and were **REPLACED with sharper ones** — retried iff no reading, once iff ruled — and I say so there and here. 176 green across all adjacent suites; no other test weakened.

**On `LADDER_UNSERVED_MIN_AGE_ROUNDS = 1`:** right. `_apply_routing` runs at :17379, the gate reads `unverified_critical_count(round_idx)` at :18309 — the ladder has its turn before the gate reads, within every round. A final-round finding has age 0 < 1 and **blocks** — fail-closed, honest non-convergence; the remedy is a round, not a wider gate. Lengthening the lock only delays naming without adding verification. The age keys on `last_status_change_round`, which can only reset the clock *later* — conservative direction.

**refutation** — a live path that writes a routing_history record with verdict `"ERROR"` where a model *was* reached while `error_routed` fails to stamp (I found none: the stamp and the record share the `_reached_someone` fact); or an archived registry whose door-open entries carry an instrument-contact field I did not scan for (I scanned `error_routed` and `escalated`; `routing_corrected`, `resolved_by_routing` and `merge_candidate_of` all co-occur with fields already tested).

**termination** — done when the founder accepts or rejects the reclassification semantics; stop pushing after that — the remaining risk is enumerated and measured at 0 in the archive.

**disagreement** — cc2 may argue reclassifying ERROR→UNRESOLVED weakens the fail-closed sentinel. Verbal, I think: the rewrite keys on the one fact (`rungs_reached == 0`) that makes "ERROR" a false assertion of contact, and every decider-returned verdict requires code, which requires a reached model.

## J2 — The probe's fail-closed direction

**verdict** — FIXED, and your suspicion was right with a sharper cause: **the cache makes one bad moment permanent**. Measured on the unfixed tree: normal probe 22 roots; every probe timing out (loaded machine) **0 roots**; after the load clears, same process, **still 0** — poisoned for process life. One 10-second spike at the first falsifier of a run returned the gate to refusing every spawned-interpreter falsifier for the whole run. Stripped PATH: no regression (22 roots — the static candidates and globs cover it).

**fix** — `bench/falsifier_verify.py`: `_declared_secondary_roots(cand)`, consulted **only** when a candidate's probe fails — roots derived from the candidate's path without executing it (structural `lib/python3.*` trees from both the shim-level and realpathed prefixes; the declared CommandLineTools/`/Library/Python` globs for the `/usr/bin/python3` shim, whose prefix resolves uselessly to `/usr`), existence-filtered. So cc2's declared mechanism is kept after all — as the probe's fallback, not its replacement. My own first draft had two defects the measurement caught: it missed the shim's 3.9 tree *and* added bare `/usr` to the allow set — an unsanctioned widening, now pinned against by test. Under total probe failure every import-bootstrap-class tree stays allowed in at least one realpath spelling (the observer realpaths both sides, `_resolve` :558 / `_realpaths` :943); when probes answer, behaviour is byte-identical — the fallback is provably unreached (spy test).

**falsifier** — `python3 scripts/probe_failure_regresses_the_gate_2026-10-12.py` → `-> COVERED`; your `scripts/interpreter_allowlist_coverage_2026-10-12.py` still reads **4 of 4**; committed test `bench/tests/test_probe_failure_keeps_the_carve_out_2026-10-12.py` (5 tests); key-access suite 41 green, both interpreter suites green.

**reasoning** — composability satisfied by measurement, not judgement: probe alone fails the loaded-machine state (0 roots, measured); declared alone covered 3 of 4 (your measurement); composed covers 4 of 4 normally and degrades to declared coverage instead of to refusal. Rejected: per-candidate cache retry (adds up to N×10s per falsifier on a loaded box — the cache poisoning becomes a latency tax) and touching the `scan_falsifier_source` fail-closed branch (a deliberate tripwire for scanner corruption; his to change).

**refutation** — a machine where an interpreter's bootstrap reads live outside every declared/structural pattern *and* the probe fails; or evidence the observer compares unresolved paths somewhere I missed.

**termination** — done; stop unless a run logs a spawned-interpreter refusal with the fallback present.

**disagreement** — none expected; this adopts cc2's mechanism in the slot where mine was measured weaker.

## J3 — The severity gate: consolidation, then the attack that voids half of it

**Consolidated paragraph for his ruling:** The restored severity test is gated on `severity_is_proven`, which accepts only a PASS/WARN from `_validate_rk_computation` — a tool recomputation of the model's stated R_k from the model's stated inputs — and the enforcement is one-directional: an unproven float still blocks at its claimed value and can never demote, clear or close. This satisfies the provenance ruling's letter ("requiring the models to provide worked proofs") and is not a raw vote: the float alone buys nothing. **But the executed attack lands at two levels, and the second is the one that matters.** Level 1: the recomputation checks arithmetic self-consistency only — invented inputs (R_old=0.30, q=0.648, R_k=0.1312) PASS; nothing cross-checks any input against a registry fact or tool measurement (recomputation cross-checked by SymPy and by Wolfram Language, local Wolfram Engine: 0.13108242303872889…). Level 2: **the proven quantity is never compared with the gated quantity** — `severity_is_proven` reads only the status, so a proof whose own content is R_k = 0.95 releases a 0.45 severity float; measured, A4 goes 1→0 on exactly that proof. So the gate demonstrates *use of the mathematical model*; it does not demonstrate that the inputs are true, nor that the released float is related to the arithmetic shown. What gaming buys is bounded by the one-directional design — only sub-criticals (a float the model already controls) are releasable — so the gate does real work against honest noise and is gameable by an adversarial seat.

**verdict** — the consolidation is PREMISE WRONG in its strong form ("the worked proofs ARE the gate's mechanism" — they are the gate's *ritual*; the mechanism never touches the float). NEEDS HIS RULING on the repair: tying the proof to the float requires deciding what severity is *computed from* (R_k is residual risk; severity is impact — different quantities), and that is semantics only he can set. I deliberately wrote no unilateral coupling.

**falsifier** — `python3 scripts/severity_proof_gaming_2026-10-12.py`, output pasted in the transcript above (PASS / PASS / `True` / `A4 gamed 0, honest 1`).

**refutation** — a code path I missed that compares `recomputed_rk` (or `model_rk`) with `entry["severity"]`; I found none — the proof dict's `delta` is model-vs-recomputed R_k only.

**termination** — done at his ruling; do not iterate on coupling proposals before it.

**disagreement** — cc2 (and my own blind-round self) held the consolidation whole. The Level-2 measurement is new information, not a verbal difference: two blind seats replicated an answer neither had executed.

## J4 — Parked items 1 and 2

**Item 1 (A17), verdict — RESOLVED ALREADY.** The parked entry is stale: fixed 2026-09-11 by `_locally_shadowed()` (Python's scoping rule, not a heuristic), task-list state DONE at line 565, committed evidence `bench/tests/test_verdict_guard_resolves_the_call_2026-09-11.py` — executed now, 7/7, and the live guard class 24/24 with no false positive over the real scripts. The declared residual (imported names matched by name, not resolved to module) is the guard's documented boundary with its own anti-weakening test; "fixing" it would un-flag the defect the guard was built for (`cdsfl_seal_logs.py` binding an imported verdict). Nothing written; nothing to write.

**Item 2 (A18), verdict — FIXED, premise checked first and found half-stale.** Measured by running the sweep: `max_papers_per_round` was already `[DOCUMENTED]` via the block-level `_ouroboros._note` — but no note anywhere stated the *redundancy* (the key is read by no runner module; `api_access = []` is the load-bearing switch). Written: `_max_papers_per_round_note` beside the key in all 3 arm configs (`bench/exp56_configs/d9_multi_model_panel.json`, `d9_single_model_with_agents.json`, `d11_seat_contrast_diversity_arm.json`) — an annotation key nothing executes, so the frozen pre-registration behaviour is byte-identical; the sweep still prints 15 off-switches, 12 read, 0 unexplained. The coupling warning as transmitted **did not bind**: the :265 CITED-set assertion and the :280 citation control both passed unchanged (they pin `hardened_gate_enabled`, untouched). The two tests that *did* fail were the `why`-equals-block-note pin and the delete-block-note control; both REPLACED with sharper, non-vacuous versions (sibling note alone keeps DOCUMENTED; only deleting both notes yields UNEXPLAINED; the note must name the redundancy) — 21/21 green. `hardened_gate_enabled` remains CITED-with-no-reason in 3 arms; the reason belongs to his 2026-06-10 ruling and inventing one would be me coining content — left for him.

## J5 — The two side-findings

**cc2's tempdir finding — ABOVE THRESHOLD (category 3, verification-integrity), and wider than reported.** Measured with the observer's own precedence (`_denied`: protected → allow → deny): reading this exam's own prior-round FULL RECORD from a sandboxed falsifier is **ALLOWED, SILENTLY** — allowed reads emit nothing, so post-run forensics sees nothing unless vocabulary leaks. And it is allowed through **two** roots, not one: `tempfile.gettempdir()` *and* the clone root itself sits in the allow set, so narrowing the tempdir allowance alone would not close it. This is K-class material (prior-round reports of the same exam) reachable without touching a digest-protected key — the Exp 48 class with no key involved. Simplest sufficient fix, specified but **not written**: a second always-denied tier in `_denied`, checked where `_protected` already is (before the allow test), holding the staged clone's `experimental_notes/` and `bench/logs/` — precedence-respecting, inert for honest scratch writes. I did not edit the observer template: it is the single most safety-critical component, the change reorders gate semantics, and shipping it untested in the last hour of a one-shot round is worse than the documented hole. It needs a dedicated pass with the 41-test suite extended first. Recommend: next free panel, as its own item.

**My v2 `_capture_baseline` finding — BELOW THRESHOLD for current operations.** The forward path imports v3 only (`bench/launcher_core.py:133,359`); v2's importers are archived experiment launchers and analysis scripts. The defect corrupts the baseline substrate only in a v2 *run*, and none is scheduled. What I would do if one ever is: port the v3 round-13 `_gateable_source` substrate fix (a few lines mirroring v3 plus one test); the real cost is not the lines but archival comparability — v2 is the replay substrate for exp38–44, and changing its measurement code invalidates byte-for-byte replay, which is why I did not fix a legacy runner unprompted and will not.

---

**Paths written:** `bench/reference_runner_v3.py` (3 edits), `bench/falsifier_verify.py` (fallback + helper), `bench/exp56_configs/{d9_multi_model_panel,d9_single_model_with_agents,d11_seat_contrast_diversity_arm}.json`, `bench/tests/test_transport_dead_serve_is_not_a_ruling_2026-10-12.py` (new), `bench/tests/test_probe_failure_keeps_the_carve_out_2026-10-12.py` (new), `bench/tests/test_never_served_findings_enter_the_ladder_2026-10-12.py` (2 assertions replaced sharper), `bench/tests/test_capabilities_disabled_by_config_2026-09-10.py` (2 assertions replaced sharper), and 4 producer scripts `scripts/{transport_dead_serve_blocks_for_ever,probe_failure_regresses_the_gate,severity_proof_gaming,door_open_archive_carries_no_instrument_contact}_2026-10-12.py`, every `--help` free. 197 tests green across every touched surface; no test weakened — four assertions replaced with sharper ones, each saying so in place. One Wolfram call made, attributed; everything else decided by the open-source tools.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_clear_the_outstanding_2026-10-12/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
