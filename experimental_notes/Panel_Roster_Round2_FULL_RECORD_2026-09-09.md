# Panel — roster confinement, round 2, FULL RECORD, unfiltered

Record written 2026-09-11T09:42:34+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

The second roster-confinement round, following the repair reviewed in `Panel_Roster_Fix_FULL_RECORD_2026-09-09.md`. Read that note first.

## What the round found

The repair to `_declared_models` got 3 things wrong and all 3 were caught the same day. The first version read the hardcoded `RunnerConfig.models` default as an arm's declaration and returned an EMPTY roster when nothing matched, which dispatched to nobody in silence and took 2 executing tests red — archive reach measured at **0 of 60 runs, Wilson [0.0%, 6.0%]** by `scripts/roster_disjointness_2026-09-09.py`. Enabling routing then made a previously unreachable path live, in which an empty ladder was misclassified as a dead transport so `HALTED_IRREDUCIBLE_QUEUE_ALARM` could not fire in the 1-seat arm.

**THIS IS THE OTHER OF THE 2 ROUNDS WHOSE SEAT REPLIES CARRY NO `strongest_disagreement` FIELD**, for the same reason: dispatched before that field was in the brief.

**A CAUTION THAT APPLIES TO THIS ROUND.** Until task A20 landed on 2026-09-11, all seats shared ONE writable sandbox and ran concurrently. Agreement between seats here is not evidence of independence.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 2 on the exp56 roster confinement, after the round-1 findings were applied

## SECTION 1 — The question

**Does the corrected roster-confinement work now do what it claims, and what did applying round 1's findings break that nobody has looked at?**

Round 1 of this panel reviewed `_declared_models` in `bench/reference_runner_v3.py` and returned 2 material findings plus 3 below threshold. All were verified independently before being applied, and 1 of the 2 material findings was REFUSED on measurement. The artefacts under review are:

- `bench/reference_runner_v3.py` — `_declared_models` (roster confinement), `_runner_config_models_default`, the empty-ladder branch inside `_apply_routing`, and the annotated `_verification_step` call site
- `bench/exp56_configs/*.json` — all 3 arm configs, whose `_routing_note`, `_sweep_note` and new `_verification_note` were rewritten
- `bench/tests/test_declared_models_roster_2026-09-09.py`
- `bench/tests/test_empty_ladder_is_not_a_dead_transport_2026-09-09.py`
- `bench/tests/test_cc2v_is_held_constant_across_arms_2026-09-09.py`
- `bench/tests/test_d9_d11_configs_valid_2026-09-05.py` — the re-aimed routing test CC2 criticised in round 1
- `scripts/roster_disjointness_2026-09-09.py`

**What round 1 found, and what happened to each finding.**

1. **C-A, `_verification_step` receives the roster unfiltered.** Observation CONFIRMED, prescription REFUSED. That function does not dispatch to the roster: it selects the single seat whose base label is CC2 as a verifier and skips if absent. Measured against the 3 real arm configs, filtering keeps CC2v in the 1-seat and 5-seat arms and removes it from the contrast arm alone, converting a control held constant across arms into a confound in 1 of 3. **Attack this refusal.**
2. **C-B, an empty routing ladder was misclassified as a dead transport.** CONFIRMED and fixed. In the 1-seat arm `rank_falsifier_writers(['CC2'], exclude=('CC2',))` returns 0 rungs, so the finding got neither `irreducible_escalation` nor `routing_deferred`, and `HALTED_IRREDUCIBLE_QUEUE_ALARM` could not fire in the arm whose pre-registration names that halt as its reportable outcome.
3. **CC2's criticism that the re-aimed guard test called the helper rather than the caller.** CONFIRMED by mutation and fixed.

**What the assistant broke and then repaired, which the panel did not find.** The first `_declared_models` read the hardcoded `RunnerConfig.models` default as an arm's declaration and returned EMPTY when nothing matched, dispatching to nobody in silence. It took `bench/tests/test_corrected_copy_wiring.py` red on 2 executing tests. Archive reach measured at 0 of 60 runs, Wilson [0.0%, 6.0%].

## SECTION 2 — Use the harness

**Form your answer by RUNNING the machinery, not by describing it.** A reply that reasons about these functions without having called them has not answered.

Instruments that bear directly on this question, and what each is expected to say:

- **`irreducible_queue_count` and `build_irreducible_queue_alarm`** — the load-bearing pair for finding 2. Drive them. The claim is that 3 deferred criticals against `max_irreducible_queue = 2` now produce an alarm object where before they produced `None`. Falsify it.
- **`gamma` and the two-sided gate (`_check_gamma_alt_convergence`)** — routing is now ON in all 3 arms where it was OFF. Routing absorbs findings. **Does enabling an absorber change what the decay curve reports, and can a run now converge on a flattened gamma that flattened because findings were routed away rather than because the problem space was exhausted?** This is the question the assistant has NOT asked and it is the reason gamma is named here.
- **`severity` and `CRITICAL_SEVERITY_THRESHOLD`** — the empty-ladder deferral is gated on severity. Check the boundary.
- **`rho`** — if routing changes the novelty profile of what survives to later rounds, rho moves. Say whether it does.

## SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. A fix without a runnable falsifier that has been EXECUTED is a hypothesis, not a fix.

**Report the exact command you ran and the exact output you saw.** Where you propose changing a line, give the file, the line, the old text and the new text. Where you claim a test is weak, DEMONSTRATE it: mutate the source, assert the mutation applied, run the test, and report whether it went red. A mutation that fails to apply is indistinguishable from one that was not caught.

**Work in a sandbox copy. Do not modify the canonical tree.**

## SECTION 4 — What would refute you

Before concluding, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

Specifically: if you attack the C-A refusal, state what measurement would show the refusal is right after all. If you defend it, state what would show it is wrong.

## SECTION 5 — Output shape

Return these fields:

- `verdict` — one of CONFIRMED / REFUTED / PARTIAL for the claim that the corrected work does what it claims
- `reasoning` — grounded in tool output you actually saw
- `findings` — each with: file, line, severity, what is wrong, the fix, and the executed falsifier with its command and output
- `falsifier` and `falsifier_result` — the code you ran and what it returned
- `refutation_condition` — Section 4's answer
- `strongest_disagreement` — your strongest disagreement with THIS BRIEF's own framing, including the framing of the C-A refusal. Disagreement is preserved as information; do not converge toward the brief.
- `passes_run` — how many

## SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could cause real-world failure in a paid experimental run. Do not generate findings for their own sake and do not police style.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 66 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_roster_round2_2026-09-09) -->

## verdict

**PARTIAL.**

The three round‑1 repairs do what they claim — I confirmed each by execution and each survives mutation. But applying them made `routing_deferred` the *terminal* state of every escalated critical in the 1‑seat arm, and the only thing bounding that state is an A4 release valve that has never executed in any run since it was added.

---

## reasoning (all from tool output)

**Sandbox:** `/private/var/folders/.../cdsfl_panel_k8zypybl/repo` (staged copy; canonical tree untouched).

### The round‑1 work, driven

**Finding 2 (empty ladder → alarm) — CONFIRMED.** `python3 /tmp/fpanel/e1.py`:

```
bound = 2
n=1 deferred: queue_count=1 alarm=None                evidence=0
n=2 deferred: queue_count=2 alarm=None                evidence=0
n=3 deferred: queue_count=3 alarm=IRREDUCIBLE_QUEUE   evidence=3
n=5 deferred: queue_count=5 alarm=IRREDUCIBLE_QUEUE   evidence=5
--- REGRESSION: pre-fix count (irreducible_escalation only) ---
 pre-fix count = 0 -> alarm would be None
 post-fix count = 3
```
The claim in the brief is exact: 3 deferred criticals against bound 2 produce an alarm object where the pre‑fix predicate produced `None`, and the collector now fills (3 evidence items, not the empty bundle of `sim45_memory_20260908T033012Z`).

**Severity boundary — correct.** `>=` is inclusive at exactly 0.7 and excludes `0.6999999999`; `severity=None` and a missing key both floor to 0.0 and drop out.

**End‑to‑end across all 3 arms** (`/tmp/fpanel/e2.py`, `e3.py`, dispatcher stubbed):

```
ArmA decl=[CC2] roster=5      -> _declared_models = ['CC2']       dispatched: []
ArmC decl=[Codex,ChatGPT]     -> _declared_models = ['Codex','ChatGPT']
ARM A: deferred=3 irreducible=0  queue=3  alarm=HALT (3>2)
```
Arm A dispatches to nobody and halts with a filled bundle — its pre‑registered outcome. Roster confinement holds.

**Gamma — SOUND, and the brief is out of date.** `/tmp/fpanel/e5.py`, four absorber conditions including the strongest (every finding resolved `CONFIRMED` by routing):

```
BEFORE routing:                     crit_series=[2,2,1,1] gamma=0.20815990525009165
AFTER ArmA empty ladder:            crit_series=[2,2,1,1] gamma=0.20815990525009165  delta=0.0
AFTER ArmC all UNTOOLABLE:          crit_series=[2,2,1,1] gamma=0.20815990525009165  delta=0.0
AFTER ArmC all REFUTED:             crit_series=[2,2,1,1] gamma=0.20815990525009165  delta=0.0
STRONGEST ABSORBER (all CONFIRMED): statuses=['CONFIRMED'] gamma identical=True
```
`_settled_novelty_series` keys on `open_since_round` and excludes only `{MERGED, DUPLICATE, UNCONFIRMED, REFUTED}`. Routing writes `CONFIRMED`, which is not in that set; the DUPLICATE path *withholds* the merge (NO VOTING, 2026‑08‑19) and leaves status alone. Routing cannot flatten gamma. The brief says "this is the question the assistant has NOT asked" — it has: `bench/tests/test_routing_cannot_flatten_gamma_2026-09-09.py`, 177 lines, executing, already in the tree.

**Rho — SOUND, by call order.** `_compute_rho` is called at line 12835; `_apply_routing` at 12884. Rho's inputs (`novelty_counts`, `raw_counts`) are appended at 12815/12817, before routing runs. The post‑routing `novel_this_round = _settled_all[round_idx]` at 13324 is a local reassignment *after* the append and feeds only `novel_critical_history[-1]`. Routing cannot move rho in‑round, and gamma invariance above shows it does not move the settled series that would move it next round.

### Mutation results (`bash /tmp/fpanel/mut.sh`) — every mutation verified applied

```
M1 rungs_tried == 0  -> == -1                       mutation applied (1 site)  3 failed, 4 passed   RED
M2 queue_count drops routing_deferred               mutation applied (1 site)  3 failed, 15 passed  RED
M3 alarm COLLECTOR drops routing_deferred           mutation applied (1 site)  3 failed, 15 passed  RED
M4 _declared_models: return kept -> return roster   mutation applied (1 site)  6 failed, 77 passed  RED
M5 my own fix reverted                              mutation applied (1 site)  3 failed, 2 passed   RED
M6 queue_count severity >= -> >                     mutation applied (1 site)  45 passed            GREEN ← gap
```

---

## findings

### F1 — the A4 `exhausted` release valve is unreachable. **ABOVE THRESHOLD.**

**File** `bench/reference_runner_v3.py`, **line 2957** (guard it feeds: line 2059).

**What is wrong.** `unverified_critical_count()` examines only `status == "UNCONFIRMED"` and skips entries carrying `exhausted`. `_update_finding_statuses` pre‑pass 1 evaluates the age rule for `("OPEN","CONTESTED","CORROBORATED","WITHHELD")` and does `e.pop("exhausted", None)` for everything else — including UNCONFIRMED. The valve added 2026‑09‑07 ("this cannot block for ever") has never executed. Its only test is a **source grep**: `test_panel_five_fixes_2026-09-07.py:78` asserts `'e.get("exhausted")' in body` — that the line *exists*. It passes against dead code.

**Why round 1 made it load‑bearing.** The empty‑ladder repair makes `routing_deferred` the terminal state of every escalated critical in Arm A (the ladder excludes the finding's own source model, so it is empty *every round forever*). `routing_deferred` is deliberately **not** excluded from the A4 blocker — the valve was its bound. Measured asymmetry:

```
routing_deferred      : unverified_critical_count=2  irreducible_queue_count=2
irreducible_escalation: unverified_critical_count=0  irreducible_queue_count=2
```
With 1–2 deferred criticals the queue is **below** `max_irreducible_queue=2`, so the halt alarm stays silent and A4 blocks the gamma‑alt path for the life of the run. Arm A burns all 8 rounds and exits `BUDGET_EXHAUSTED` — neither of its two pre‑registered outcomes, in a paid run. Arms B/C reach `irreducible_escalation`, which *is* A4‑excluded, so the three arms now have different stopping rules.

**Second, independent kill.** `exhausted_round_threshold` defaults to 8; every exp56 arm sets `max_rounds: 8`, so rounds run 0..7, max reachable age is 7, and `age >= 8` is unsatisfiable. The code fix alone is necessary but not sufficient.

**Executed falsifier** — `python3 /tmp/fpanel/FALSIFIER_F1.py` (imports the real module; no retyped copy):

```
  exhausted before=True A4=0
  exhausted after =None A4=1
FALSIFIED
AssertionError: unverified_critical_count's `if e.get('exhausted'): continue` (line 2059)
is UNREACHABLE. _update_finding_statuses pre-pass 1 evaluates the age rule only for
OPEN/CONTESTED/CORROBORATED/WITHHELD and pops `exhausted` from every other status --
including UNCONFIRMED, the ONLY status unverified_critical_count examines. The flag was
stripped by one ordinary round tick and the A4 blocker rose 0 -> 1.
```

**Fix (a), code.** `bench/reference_runner_v3.py:2957`

- old: `        if (e["status"] in ("OPEN", "CONTESTED", "CORROBORATED", "WITHHELD")`
- new: `        if (e["status"] in ("OPEN", "CONTESTED", "CORROBORATED", "WITHHELD",` / `                            "UNCONFIRMED")`

(plus a 10‑line comment recording the measurement). After the patch the same falsifier exits cleanly:
```
  exhausted before=True A4=0
  exhausted after =True A4=0
valve is reachable -- claim not demonstrated
```

**Fix (b), config.** All 3 files in `bench/exp56_configs/`, inserted after `"max_rounds": 8,`:
`"exhausted_round_threshold": 6,` + `_exhausted_note`. **6 is derived, not chosen:** it is the *latest* value still reachable more than once (ages 6 and 7 occur at rounds 6 and 7) — the smallest departure from the default that makes the valve exist. Nothing else is claimed for it. The arm‑identity assertion in `test_d9_d11_configs_valid_2026-09-05.py` still passes because the keys are identical across all three.

**New test** — `bench/tests/test_exhausted_valve_reaches_a4_2026-09-09.py`, 7 executing tests, replacing the source grep: flag survives a tick; runner derives it and A4 releases 1→0; does **not** release early; still requires review activity; and pins the config kill. Mutation M5 (revert the fix) takes it **red, 3 failed**.

**Blast radius, measured:** `546 passed` across A4, gamma‑alt, open‑crit‑high, panel‑five, all round‑1 artefacts, and `test_corrected_copy_wiring.py`.

### F2 — the A4 reason string names a severity filter that was deleted. **ABOVE THRESHOLD (lower rank).**

**File** `bench/reference_runner_v3.py`, **lines 6362‑6363** and **13460‑13461**.

Severity stopped gating `unverified_critical_count` on 2026‑09‑06 ("there are no votes in CDSFL"), but both the gamma‑alt reason string and the round‑loop log still say `critical-severity ... sev>=0.7`. Executed:

```
severity 0.2 UNCONFIRMED -> unverified_critical_count = 1
gamma-alt reason string -> A4 BLOCK: 1 unverified critical-severity candidate(s)
                           (status UNCONFIRMED, sev>=0.7) pending at round 5 ...
```
An operator adjudicating a blocked exp56 run is told a critical is pending when none is. This project's own record says a message that misdescribes itself gets the line moved instead of read — the alarm was suppressed twice that way while it was right.

**Fix** (2 sites): `critical-severity candidate(s) (status UNCONFIRMED, sev>=0.7)` → `UNCONFIRMED candidate(s) with no resolved falsifier`. Verified: `A4 BLOCK: 1 unverified UNCONFIRMED candidate(s) with no resolved falsifier pending at round 5 …`; `57 passed`.

### F3 — mutation gap on the queue's severity boundary. **BELOW THRESHOLD (closed anyway).**

M6 (`>=` → `>` in `irreducible_queue_count`) left **45 tests green**. The shipped code is correct, so this is coverage, not a live defect. Two boundary tests added; re‑running M6 now gives `1 failed, 6 passed`.

### Below threshold, stated not fixed

- **Arm B's declaration is byte‑identical to the hardcoded default**, so `_declared_models` reads it as "no declaration" and returns the roster unfiltered. Measured: `load_default_config()` → `['CC2','Codex','ChatGPT','Gemini','DeepSeek']`, the same set, so the leak is **0 today**. It goes live the day a sixth seat joins: `ArmB decl=DEFAULT-5 roster=6(+Fable) -> ['CC2','Codex','Gemini','DeepSeek','ChatGPT','Fable']`. Routing is capped at `max_rungs=2` and ranks unknown labels last, so routing would not reach it — but `_post_convergence_sweep` iterates *every* seat with no cap, 2 rounds, now enabled. The docstring names this as a KNOWN LIMIT; the mitigation is a warning, not confinement.
- `_error_route_pending` is written before `route()` and popped after; if `route()` raises it persists onto the entry and into the report.

---

## falsifier / falsifier_result

Code: `/tmp/fpanel/FALSIFIER_F1.py` (reproduced in substance above; imports `bench.reference_runner_v3` directly). Command: `python3 /tmp/fpanel/FALSIFIER_F1.py`. Result: **FALSIFIED** before the patch (`exhausted True→None`, A4 `0→1`, `AssertionError`); **clean exit** after. Six mutations run, all verified applied; five red, one green and now closed.

---

## refutation_condition

**F1 is overturned if** any of: (a) a path exists that reaches `unverified_critical_count` with `exhausted=True` on an UNCONFIRMED entry *without* `_update_finding_statuses` having run that round — show it and F1 dies; (b) exp56 Arm A's realistic queue is always ≥3, in which case the alarm halts first and the 1–2 band never occurs — an archive replay of Arm‑A‑shaped runs showing `P(queue ∈ {1,2}) ≈ 0` would demote F1 to below threshold; (c) `routing_deferred` is meant to be A4‑excluded like `irreducible_escalation`, making the valve the wrong mechanism entirely — then the fix is a one‑line exclusion, not this.

**On C‑A, I defend the refusal, and here is what would show me wrong.** The refusal is right on its measurement: filtering `_verification_step` removes CC2v from Arm C alone and converts a constant into a 1‑of‑3 confound. I would abandon that defence if someone measured that an *undeclared* CC2 dispatch in Arm C materially changes Arm C's findings — e.g. a paired run of Arm C with and without CC2v showing a difference in confirmed‑finding count outside noise. That would make CC2v a seat rather than infrastructure, and a seat must be declared. Absent that measurement, holding it constant is correct.

---

## strongest_disagreement

**With the brief's framing of the gamma question.** The brief says enabling routing raises a question "the assistant has NOT asked and it is the reason gamma is named here." It was asked, answered by execution, and pinned in a 177‑line test that was already in the tree when this brief was written. I re‑derived it independently under four absorber conditions and got gamma identical to 17 significant figures. Naming gamma sent the panel at the one door that was already bolted; the door standing open was three functions away, in a valve nobody had executed. **A brief that asserts what has not been looked at is doing the same thing the source grep at `test_panel_five_fixes_2026-09-07.py:78` does — asserting presence instead of measuring behaviour.** If the panel is to be steered, steer it with a measurement.

**With the framing of the C‑A refusal.** It is presented as a clean win — observation confirmed, prescription refused on measurement. It is *narrower* than that. `_declared_models` is described as "the seats a run is ALLOWED to dispatch to," and after the refusal that is false: in Arm C a CC2 seat is dispatched at rounds 6–7 that Arm C never declared. The refusal is correct and the confinement claim is overstated; both are true at once. The honest repair is not to filter but to **declare** — an explicit verifier key in all 3 arm configs, so the seat is on the record rather than reachable only because the roster was passed unfiltered. I did not implement that: `verification_min_round` is the only `verification_*` key that exists, the seat is selected by scanning the roster for base label `CC2`, and a new config key with no caller would be exactly the additive violation this brief warns about (11 confirmed defects of that class since 2026‑08‑01). It is a design proposal, and I have no falsifier for it, so I am not filing it as a finding.

**With "what did applying round 1's findings break."** Nothing was broken. What round 1 did was make a *pre‑existing* dead valve load‑bearing. That distinction matters for the ledger: F1 is not a regression from 2026‑09‑09, it is a 2026‑09‑07 addition that nothing reached, whose cost only became payable once the empty‑ladder repair started routing traffic into it.

---

## passes_run

**4.** Pass 4 produced F2 and F3 and no further above‑threshold finding; pass 5 over `_error_route_pending`, the sweep's `repo_root`, and the Arm‑B default‑equality case produced only below‑threshold items already listed. Terminating.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 55 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_roster_round2_2026-09-09) -->

# Round-2 verdict — exp56 roster confinement

## `verdict`: **CONFIRMED** (with 1 conditional finding and 1 sub-threshold finding)

The corrected work does what it claims. Every claim I could reach was driven through the real machinery and none was falsified. The one defect I found is in a **config**, not in the corrected code, and is conditional on a roster change before launch.

## `reasoning`

Grounded in execution, not description:

1. **Finding 2's fix (empty ladder → deferral → alarm) works end-to-end.** Ran the real `_apply_routing` with a stubbed dispatcher on a 1-seat arm with 3 escalated criticals: 0 dispatches, all 3 stamped `routing_deferred`, `irreducible_queue_count()==3`, `build_irreducible_queue_alarm` returns an alarm object with **evidence for all 3** (the sim45 empty-bundle regression stays closed: collector == counter, verified at the boundary too). At exactly the bound (2) the alarm is `None`. Premise executed: `rank_falsifier_writers(['CC2'], exclude=('CC2',)) == []`.
2. **Severity boundary:** sev = 0.7 exactly is counted by both counter and collector; 0.6999 by neither. Terminal `CONFIRMED` leaves the queue.
3. **The gamma question the brief says nobody asked — answered by execution: routing CANNOT flatten the gate.** Routing's only status write is `registry.resolve(cid, "CONFIRMED")`; `_NON_NOVEL_TERMINAL_STATUSES = {MERGED, DUPLICATE, UNCONFIRMED, REFUTED}` does **not** contain CONFIRMED/CLOSED, so an absorbed critical still counts at its **discovery** round in both the settled series (gamma side) and the location-keyed series (count side). Executed: 3 criticals discovered rounds 3–5 and instantly routed-CONFIRMED give `crit=[0,0,0,1,1,1]` and `_check_gamma_alt_convergence` **refuses** (`novel_crit_recent=[1,1,1]`) even at `gamma_critical=0.99`; the same 3 discovered at round 0 converge. Routing changes *resolution*, never *discovery attribution* — the decay curve measures the latter. Deferred entries keep status OPEN (visible to the series). Routing's DUPLICATE path withholds the merge (no-voting), so it removes nothing from the series either. The one path that *does* remove a critical from the series — CC2v REJECT → UNCONFIRMED — is not routing, and the A4 blocker counts it (executed: deferred UNCONFIRMED critical counted; only `irreducible_escalation` is excluded, the fail-safe direction).
4. **Ordering:** within the round loop, gamma-alt is assessed at ~13482 but the alarm builder at 13742 runs before every convergence action, sets `converged=False` and breaks — no `break`/`return` exists between them (grepped 13494–13742). The 6380 docstring's "never reaches this check with an over-bound queue" is imprecise (it is reached, same round) but behaviourally safe.
5. **rho:** mechanically unchanged by enabling routing. Its inputs are `novelty_counts`/`raw_counts`, appended from the panel review parse at lines 12826–12828 before `_apply_routing` touches the registry; routing writes flags/verdicts only. Second-order movement via next-round prompt context (confirmed list, feedback sections) is possible and is the panel mechanism working as designed, not an accounting artefact.
6. **Shipped tests:** 24/24 pass (three 2026-09-09 files), 74/74 pass (`test_d9_d11_configs_valid`), `scripts/roster_disjointness_2026-09-09.py` reproduces 0/60 disjoint, Wilson [0.0%, 6.0%], both libraries agreeing.
7. **Test strength demonstrated by mutation** (in a disposable copy, since removed): (M1) revert deferral branch to `if False:` → 3 tests red; (M2) `_roster = list(exp_config.models)` → wiring test red; (M3) drop `routing_deferred` from the counter → 2 tests red. All three mutations verified applied by grep before running.
8. **C-A refusal: I attacked it and it held.** Executed against the 3 real configs and a 5-seat roster: filtering leaves CC2v reachable in A (`['CC2']`) and B, removes it from C (`['Codex','ChatGPT']`) alone — a constant converted into a 1-of-3 confound. `_verification_step` (read at 9207–9329) genuinely does not dispatch to the roster; it selects the single CC2 seat and returns `{'skipped': True, 'reason': 'CC2 config not found'}` when absent (executed with an OPEN finding present, so the skip is the CC2 branch, not the empty-registry branch). The refusal is right. My sharpest counter — CC2v dispatches an *undeclared vendor* inside arm C, the same class as the merge-arbitration leak that config switched off — fails on the difference that matters: arbitration/routing/sweep vary panel work by arm; CC2v is identical harness in all 3 arms, its CONFIRM/REJECT never enters the primary metric (falsifier-gate CONFIRMED only, per the frozen pre-registration), and filtering it *creates* the asymmetry it purports to remove. Also frozen 2026-09-05 with CC2v in place; filtering now would be post-freeze tuning.

## `findings`

**Finding 1 — Arm B's declaration is byte-equal to the stale hardcoded default, so the 5-seat arm is classified as "no declaration made".** Conditional-material.
- **file/line:** `bench/exp56_configs/d9_multi_model_panel.json` line 12 (`"models"`), interacting with `bench/reference_runner_v3.py:5217` (`declared == list(_runner_config_models_default())`).
- **what is wrong:** Executed: `armB == default → True`. Today this is harmless (live orchestrator roster, executed via `load_experiment_config()`, is the same 5 labels — the filter would be a no-op either way). But if a 6th seat joins the orchestrator default before launch — the exact "before Fable joined" drift the project has hit, per its own record, 7 times — routing and the sweep in arm B silently widen to 6 seats (executed: `_declared_models` returns all 6) while the frozen pre-registration says "B = 5 seats, 4 vendors", and the main review dispatch stays at 5 (separate exact-match confinement at line 8470). PANEL MISMATCH (11614–11623) is log-only. The runner docstring names this KNOWN LIMIT; a known limit sitting on a frozen arm is still an exposure.
- **fix (config layer, zero behaviour change today):** in `d9_multi_model_panel.json`, reorder to `["CC2", "Codex", "Gemini", "ChatGPT", "DeepSeek"]` (same set; list-equality with the default breaks, so the declaration binds). Caveat: the file is frozen pre-registration — needs founder sign-off; the set and semantics are unchanged. Alternative not touching frozen files: a launch-guard test pinning `{m.label for m in load_experiment_config().models}` to the 5 declared labels.
- **executed falsifier:** applied the reorder in a disposable copy; `_declared_models` vs 6-seat roster (Fable added) returned only the 5 (`Fable` excluded); vs today's 5-seat roster, identical behaviour; then `pytest` over all 4 relevant test files: **98 passed**. Output above.

**Finding 2 — `_verification_note` false self-reference in 2 of 3 configs.** Below threshold (documentation).
- **file/line:** `d9_single_model_with_agents.json` line 101 and `d9_multi_model_panel.json` (`_verification_note`), byte-identical (executed: `A==B==C: True`) to the d11 file's, so arms A and B state that filtering would "remove it from **this contrast arm** alone" — false in those two files; filtering *keeps* CC2v there. No behaviour rides on the key.
- **fix:** old text `remove it from this contrast arm alone` → new text `remove it from the contrast arm (d11_seat_contrast_diversity_arm) alone` in all 3 files.

**Observation (below threshold):** main review dispatch confines by exact label (`mc.label in set(cfg.models)`, 8470–8472) with no `-SIM` normalisation and no fallback — divergent semantics from `_declared_models`. A sim rehearsal of an exp56 arm config (bare names vs `-SIM` roster) yields `eligible == []` and `ThreadPoolExecutor(max_workers=0)` raises `ValueError` — loud, not silent, hence below threshold; worth a line in the runner comment.

## `falsifier` / `falsifier_result`

Primary falsifier: the 19-check script shown in full in the transcript (`python3 - <<'PYEOF' …`), importing the real `bench.reference_runner_v3` and `bench.routing`. Result: **`ALL CHECKS PASSED - no claim falsified`** (19/19 PASS lines above). Supporting runs: the CC2-absent re-check (`{'skipped': True, 'reason': 'CC2 config not found'}`), 3 mutations (all caught red), the arm-B fix falsifier (Fable excluded, 98 tests green), and commands `python3 -m pytest … -q` / `python3 scripts/roster_disjointness_2026-09-09.py` with outputs as shown.

## `refutation_condition`

- **My CONFIRMED verdict falls** if anyone exhibits a registry state where a critical discovered inside the zero-streak window is absent from `location_keyed_novelty_series`/`_settled_novelty_series` *because of a status routing wrote* — i.e. a routing code path that writes MERGED/DUPLICATE/UNCONFIRMED/REFUTED onto an entry. I found none; one concrete example refutes me.
- **My defence of the C-A refusal falls** on a measurement showing CC2v's verdicts leak into the primary metric — e.g. an archived run where a finding's falsifier-gate CONFIRMED count changed because of a CC2v CONFIRM/REJECT rather than a runner falsifier re-run. It also falls if any exp56 arm config is shown to set a `verification_*` key (none does today).
- **My Finding 1 falls** if the orchestrator roster is contractually pinned to these 5 labels through exp56's launch by something stronger than the log-only PANEL MISMATCH — show me that pin and the finding drops to documentation.

## `strongest_disagreement`

The brief frames the gamma question as an open hazard ("can a run now converge on a flattened gamma that flattened because findings were routed away"). The framing presumes routing removes findings from the decay series. It does not, structurally: both series key on `open_since_round` and strip only four statuses, none of which routing writes. The genuine series-removal channel in this codebase is **CC2v REJECT → UNCONFIRMED** (`_verification_step`, line 9310) — a *model-prose* verdict resolving a finding out of the novelty series, guarded only by the A4 counter and the `exhausted` release valve at round 8. If the panel wants to worry about an absorber corrupting the decay curve, that is the mechanism to audit — and it sits inside the very step whose unfiltered roster the C-A refusal (correctly) protected. Second disagreement: the brief says the round-1 observation C-A was "CONFIRMED, prescription REFUSED" — on my measurement even the observation is only half-right, since `exp_config.models` at that call site is not "the roster unfiltered" in any operative sense; it is a one-seat lookup table.

## `passes_run`

**4.** Pass 1: read all artefacts + shipped tests + script (green). Pass 2: 19-check falsifier + 3 mutations (all claims held; all mutations caught). Pass 3: residual surface — found Finding 1 (fix built, falsified, regression-tested) and Finding 2. Pass 4: sufficiency check over the remaining instruments named in the brief (severity boundary, rho, ordering) — no new above-threshold findings. Terminated on a quiet pass with no specific unexamined mechanism left to name.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_roster_round2_2026-09-09/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
