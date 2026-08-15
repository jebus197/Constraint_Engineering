# Does the veto repair endanger convergence, or flood the HIL queue?

2026-08-01 22:30 BST

Eleven-agent adversarial falsification, run offline at HEAD `4d10e53`. Five tracing
agents, two measuring agents driving the real functions with hand-written panel input,
three adversarial skeptics under distinct lenses, one synthesis. No live model dispatch;
no cost beyond local compute.

Presented **in full and unfiltered**, per standing directive. Raw agent output:
`HIL_Convergence_Falsification_RAW_2026-08-01.json` in this directory.

---

## Verdict: convergence

No — today's change does not put convergence beyond reach, and the reason is a guard, not a theory. But convergence IS currently out of reach on one class of target, and that has nothing to do with today's change.

Today's change (the tri-state repair) sits on exactly one of the routes a finding can take to a settled state, and it is the least-used one. A finding settles when the falsifier gate independently re-runs the model's own test and gets a CONFIRMED demonstration (bench/reference_runner_v2.py:1908-1911 sets verified=True), and the next pass turns CONFIRMED+verified into CLOSED (bench/reference_runner_v2.py:1822-1823). The close-the-loop block sits upstream behind `not entry.get("verified")` (bench/reference_runner_v2.py:1779) and is therefore never even reached for such a finding. In the two real prose runs that converged — Exp 48 chemistry, Exp 49 engineering — close-the-loop verified 0 of 37 and 0 of 38 findings. All 64 closures came from the falsifier gate. A path that produced zero closures cannot block convergence by being tightened.

I verified the CONFIRM-only critical rule myself at bench/reference_runner_v2.py:1893-1932, and confirmed that in every currently-configured experiment (falsifier_gate_enabled: true everywhere) the gate reaches a critical BEFORE the close-the-loop block's `status == CONFIRMED` precondition can hold. So today's change has zero effect on criticals in any configured run.

What IS blocking convergence, right now, on a prose target: bench/logs/exp53_control_zero_live_20260801T005649Z/checkpoint.json reads converged: False, completed_round: 3 against max_rounds: 16. It halted because 20 of 40 findings were locked "irreducible" against a bound of 2 (bench/reference_runner_v2.py:650). That halt predates today's repair by 12 hours and is caused by the routing prompt, not by verification. See ranked risk 1.

One genuine convergence risk that today's change EXPOSED (did not cause) — this is the finding I would not have expected, and it survived my own attempt to dismiss it. A sub-critical finding that has been adjudicated real, carries a proposed fix, but has no runnable falsifier now has NO in-run route to a settled state at HEAD: the falsifier gate skips it (bench/reference_runner_v2.py:1896-1906 — the no-falsifier branch acts only `if is_critical`), routing ignores it (bench/reference_runner_v2.py:2087 takes only escalated entries), and close-the-loop is one-shot and now declines. It therefore sits at CONFIRMED, and CONFIRMED is NOT challenge-immune: bench/reference_runner_v2.py:1763-1764 turns CONFIRMED plus one late CHALLENGE into CONTESTED, whereas CLOSED is immune (bench/reference_runner_v2.py:1645-1655 reads only REOPEN verdicts). CONTESTED does block both convergence gates. I recounted this population across 10 live archives myself: 38 entries end in exactly this state (exp43 3+7, exp44 8, exp45 7, exp46 4, exp48 1, exp53 2+6). The adversarial harness drove 5 such findings with one late challenge each and produced 11 consecutive blocked rounds against Exp 53's 16-round budget.

Two things stop me calling that BLOCKING. First, the counterfactual "convergence" it removed was false convergence — the third repair closed a Markdown-document finding by running Python linters against a Markdown file, and closed 5/5 harmful fixes including a remote fetch-and-exec. Second, relative to the version that actually ran every archive in bench/logs (12ad362, in force for Exp 43-53), HEAD changes nothing here — that version also failed to close prose fixes. The delta is only against the third repair, which never ran live.

GAMMA IS NOT IMPLICATED ANYWHERE IN THIS. Every mechanism above is string handling, prompt construction, or a status-transition guard. The gamma side of the two-sided gate reads the settled critical novelty series and is untouched by any verification outcome. Where a gate does block, it blocks on the `contested` term or the A4 unverified-critical term, both mechanical.

---

## Verdict: HIL load

Split answer, and the split is the whole point.

On prose documents that contain REAL, findable defects, HIL is already rare and the founder's design intent is being met: Exp 48 chemistry 1 escalation in 37 findings, Exp 49 engineering 0 in 38. That is 1 in 75 (1.3%), BETTER than the code-target aggregate of 10 in 218 (4.6% across Exp 44-47). The single Exp 48 escalation was severity 0.45 and was cleared by the post-convergence sweep, leaving a net HIL queue of zero. I recounted all of this from the runner_state.json files myself.

On prose documents that contain FENCED CODE LISTINGS, the HIL queue floods, and it is not close. Exp 53 control: 5 of 23 (21.7%) on the 29 July run and 20 of 40 (50.0%) on the 1 August run — 25 of 63 combined, 39.7%. Fourteen of those are critical-severity AND locked irreducible, against a tolerance of two. The run halted at round 3 of 16.

The mechanism is verified and it is mechanical, not philosophical. I read bench/reference_runner_v2.py:1945-1966 directly. The routing prompt — the ONLY absorber standing between the falsifier gate and the HIL queue — is code-only. Its system message says "read the real source (import inspect; from bench.cdsfl_registry import <mod>)". The finding dict handed to it carries id, description, source_model and severity, and nothing else. It never receives the target document's path or its text. So when a model is asked to write a falsifier for a defect in "Listing A" of a Markdown document, it is told to import a module that does not exist. Both rungs fail, and bench/reference_runner_v2.py:2144-2149 stamps irreducible_escalation=True with the reason "routing ladder exhausted (no model produced a runnable test)". That reason string is factually false: no model was ever given the target.

The discriminator is measured, not inferred. I ran it: routing resolved 16 of Exp 48's findings and 25 of Exp 49's — 41 successes on listing-free prose, with 0 findings mentioning a listing. On the two Exp 53 runs, routing resolved 0, with 23 and 14 findings mentioning a listing, and 25 irreducible escalations. 41 for 41 versus 0 for 25.

These are findings the machinery ought to settle itself, exactly as the founder says. The adversarial pass demonstrated it: a 14-line falsifier that opens SW-21-REF-04.md by path, extracts the TokenBucket listing and exercises allow(-10) returns CONFIRMED from the runner's own reverify_falsifier — for the very finding HEAD locked as irreducible with "no model produced a runnable test".

Today's tri-state repair contributes zero to this. I verified the complete list of escalation writers with grep: bench/reference_runner_v2.py:1305, 1327, 1658, 1710, 1742, 1902, 1929, 2144, 2145. Not one is inside the close-the-loop block (1776-1821). The non-close branch writes a log line and nothing else.

Scale caveat the founder needs: only one of the six remaining prose targets exists on disk (SW-21-REF-04.md, 7 fenced blocks). BX-14, DR-09, PR-14, PX-12 and SW-14 are named in the Exp 50/51/52 configs but have not been written yet. That is leverage, not just risk — see recommended actions.

---

## Verdict: the founder's premise

Limb (b) — "STEM topics are ultimately computable whether or not they are expressed in prose" — is CORRECT and demonstrated, not merely asserted. Five planted prose STEM defects (fourth-power section algebra, a Student-t critical value, an uncertainty combination, an asymptotic inference about a listing, binary64 catastrophic cancellation) were each settled by a runnable falsifier with no human involved, in one round, at HEAD. And the Exp 53 finding the instrument called irreducible is settled in under a second by a 14-line falsifier that knows the document's path.

But computability is NOT the binding constraint, and this is where the code does not yet deliver the premise. Two places:

First, the falsifier is never told where the document is. bench/reference_runner_v2.py:1945-1966. The finding is computable; the instrument withholds the input needed to compute it, then records the failure as irreducibility. Note the inconsistency: the post-convergence sweep prompt IS prose-aware at HEAD — it labels the target "a PROSE DOCUMENT, not Python source" and embeds the document verbatim (bench/reference_runner_v2.py:2196-2222). Routing was never given the same treatment. That asymmetry is the defect.

Second, when the computation SUCCEEDS and returns the answer "this claim is fine", the instrument throws the answer away if the finding is critical. bench/reference_runner_v2.py:1918-1932: the REFUTED branch is entered only `and not is_critical`. A correctly-refuted critical is escalated instead. The rule is deliberate and evidence-backed (Exp 42: 2 of 3 REFUTED criticals were wrong, 7 of 7 CONFIRMED were right), so I am not calling it a bug. But it means a false-positive critical is mathematically closed to programmatic resolution: the accepting alphabet for a critical is exactly {CONFIRMED}, and no input makes a true claim yield CONFIRMED.

Limb (a) — "miscategorised findings get cleared by the post-convergence sweep" — is TRUE for sub-criticals and FALSE for criticals, and the founder has been shown only the true half.

I scanned every sweep disposition in the entire archive myself. There are eight, ever. Severities: 0.66, 0.50, 0.50, 0.50, 0.50, 0.45, 0.35, 0.30. The maximum severity the sweep has ever touched is 0.66. The critical threshold is 0.70 (bench/reference_runner_v2.py:2839). The sweep has never cleared a critical and structurally cannot: I read both guards. The reasoned-withdrawal path at bench/reference_runner_v2.py:2400-2401 discards a WITHDRAW for any entry with `severity >= CRITICAL_SEVERITY_THRESHOLD` unread. The falsifier-reattachment path at bench/reference_runner_v2.py:2384-2385 accepts a REFUTED verdict only `< CRITICAL_SEVERITY_THRESHOLD` — so a correct refutation of a critical is not merely rejected, it is not even recorded. The function's own docstring at :2316-2317 states the contract: "Criticals can only be cleared by a CONFIRMED runnable demonstration — never by withdrawal."

And there is a worse structural point. The sweep runs only `if converged` (bench/reference_runner_v2.py:8389). Exp 53 halted with converged: False, so the sweep never ran at all. The cleaner the founder is relying on is switched off in precisely the runs where the residue is worst. It is also off by default (post_convergence_sweep_rounds: int = 0 at :603), though every live config from Exp 46 onward sets it to 2.

The escape hatch that would rescue this — severity calibration, the only mechanism that can lower a severity into the withdraw-eligible band — requires `falsifier_verdict == "CONFIRMED"` (bench/reference_runner_v2.py:2869-2871), the exact verdict a false-positive critical can never earn. It is also `severity_calibration_enabled: bool = False` (:583) and set in zero config files. I verified both.

Net: the single number that decides whether a miscategorised finding is cleared by the machinery or becomes permanent human work is the severity float, assigned once at intake by a model, never independently recomputed (the only assignment site in the runner is :2894, inside the disabled calibration path). A 0.69 is cleared; a 0.71 is permanent. The founder's premise (a) holds below 0.70 and fails above it.

---

## What the 51 tests did not show

The 51 tests did not measure either of the two things being asked about. This needs saying plainly because the commit message and the test count read as reassurance they do not carry.

Across all six test files there is not one reference to apply_falsifier_verdicts, _update_finding_statuses, unverified_critical_count, irreducible_queue_count, irreducible_escalation, hil_escalated, or gamma. The words "converg" and "escalat" appear only inside docstrings and once as an S_k tally field. No test calls _check_gamma_alt_convergence or _evaluate_gate_conditions. No test instantiates the state machine.

Most tellingly: zero tests assert that any finding, on any target, ever reaches CLOSED. The only two occurrences of `closed=True` in the entire set are a docstring and a `pytest.raises` negative-construction check. The suite proves the machinery declines to close things. It never proves anything can close.

The only two references to "HIL" anywhere in the 51 are substring checks on a failure message string (test_prose_acceptance_stem.py:940 and test_verification_non_python_target.py:135). They measure a LABEL, not a LOAD.

What the tests DO establish, and establish well: a harmful fix on a prose target is never scored and never closes (all 5 fixtures plus the real control document); S_k's NO_SCORE moves the risk score by exactly zero across 25 iterations, versus the 0.5 to 0.62 the naive formula would have produced; the falsifier verifier returns the right verdict on a source string; the sweep prompt delivers 100% of a document; and the Python code path still returns PASS and FAIL correctly. These are real, and they are worth having. They are no-false-close properties. They are not convergence or HIL measurements.

One thing in the suite deserves the founder's attention. The suite MEASURED a defect and then skipped the tests that would have costed it. Two of the five prose falsifiers carry their own fenced listing and are truncated in markdown transport, returning ERROR (test_prose_acceptance_stem.py:747, :773). ERROR on a critical is precisely the input that stamps escalated=True and trips the A4 convergence block. I re-ran the suite at HEAD: 171 passed, 4 skipped, and both skip reasons read "falsifier carries its own fence; see TestAFalsifierThatCarriesItsOwnFence" (lines 621 and 658). The two tests that would have shown the end-to-end HIL consequence of a 40% transport failure are the ones excused.

Finally, the module docstring at test_prose_acceptance_stem.py:40-58 is half stale: it describes a defect as open with a strict xfail that was repaired at 21:20 and removed. A reader of the header would believe a closed defect is open, and would also believe the "MEASURED STATUS" block is current. It is not.

---

## Ranked risks


### 1. [BLOCKING] The routing prompt is code-only and never receives the target document's path, so on a prose document containing fenced code listings the routing ladder — the only absorber between the falsifier gate and the HIL queue — cannot resolve anything. Every such finding is locked as 'irreducible' with a reason string that is factually false, the queue exceeds its bound of 2, and the run halts. This is the actual HIL flood and the actual convergence blocker, it predates today's repair by nearly two months, and it is untracked.

**Anchor.** bench/reference_runner_v2.py:1945-1966 (code-only system prompt and resolve prompt; the finding dict passed at :2131-2134 carries id/description/source_model/severity only) then bench/reference_runner_v2.py:2144-2149 (irreducible_escalation=True, hil_escalated=True, reason 'no model produced a runnable test') then bench/reference_runner_v2.py:650 (max_irreducible_queue=2) then halt. Measured by me: routing resolved 16/37 (exp48) and 25/38 (exp49) on listing-free prose with 0 findings mentioning a listing, versus 0 resolved and 25 irreducible across the two exp53 runs, whose documents drew 23 and 14 listing-referencing findings. bench/logs/exp53_control_zero_live_20260801T005649Z/checkpoint.json: converged False, completed_round 3 of 16. Contrast bench/reference_runner_v2.py:2196-2222, where the sweep prompt IS already prose-aware.

**Fix.** Pass the target path (and, for a listing-referencing claim, the listing text) into _routing_resolve_prompt, and branch _ROUTING_SYSTEM on the already-resolved target_kind exactly as _sweep_prompt branches at :2196-2222. Do the same for the panel falsifier directive _RUNNABLE_FALSIFIER_S2, which also tells every model every round to import the target module. Neither prompt has a single test in bench/tests/ — add one that asserts the target path appears in the prose-branch prompt.


### 2. [HIGH] The post-convergence sweep — the mechanism the founder is relying on to clear miscategorised findings — has never cleared a critical and structurally cannot. Combined with the CONFIRM-only critical rule and a disabled severity-calibration path, a false-positive critical is a permanent HIL resident by construction, and the instrument tolerates exactly two of them before refusing to converge.

**Anchor.** bench/reference_runner_v2.py:2400-2401 (WITHDRAW discarded unread if severity >= 0.7) and :2384-2385 (a REFUTED falsifier verdict is accepted only if severity < 0.7, so a correct refutation of a critical is not even recorded); function docstring at :2316-2317 states the contract. Escape hatch closed: :2869-2871 requires falsifier_verdict == 'CONFIRMED' to demote, and :583 severity_calibration_enabled = False with zero config files setting it. I scanned every sweep disposition in the archive: 8 total, severities 0.66/0.50/0.50/0.50/0.50/0.45/0.35/0.30 — maximum ever touched 0.66, threshold 0.70 (:2839). exp53 produced 14 critical AND irreducible entries against max_irreducible_queue=2 (:650).

**Fix.** Two options, and they compose. (i) Let the sweep record a REFUTED falsifier verdict on a critical even where it declines to act on it, so the human sees a computed answer rather than a blank. (ii) Add a narrow demotion path: a critical whose falsifier clean-exits against BOTH the document and a corrected copy may be demoted one severity band with the evidence attached, subject to founder ruling. Do not weaken CONFIRM-only itself — its Exp 42 evidence is sound.


### 3. [HIGH] The post-convergence sweep runs only when the run converged, so the cleaner is switched off in exactly the runs whose residual ledger is worst. exp53 halted and the sweep never ran at all.

**Anchor.** bench/reference_runner_v2.py:8389 `if converged and getattr(cfg, "post_convergence_sweep_rounds", 0):`. bench/logs/exp53_control_zero_live_20260801T005649Z/checkpoint.json: converged False. bench/exp53_configs/53_control_zero_live.json:85 sets post_convergence_sweep_rounds: 2 — it was configured and never executed.

**Fix.** Run the sweep on a halt and on a round-cap exit as well as on convergence, marking the result as a residual-clearing pass rather than a post-convergence one. It costs a bounded model dispatch and it is the difference between shipping a 20-item queue and shipping whatever survives adjudication.


### 4. [MEDIUM] Today's repair removed the only in-run route to a settled state for one population — sub-critical findings adjudicated as real, carrying a fix, with no runnable falsifier — and that population stays exposed to a single late CHALLENGE, which flips it to CONTESTED and blocks BOTH convergence gates. This is the one place today's change genuinely raises convergence risk, and it is a hole today's change exposed rather than created.

**Anchor.** No route out: bench/reference_runner_v2.py:1896-1906 (no-falsifier branch acts only `if is_critical`), :2087 (routing takes only escalated entries), :1779/:1783 (bugzilla_attempted sticky, one shot). Exposure: :1763-1764 (CONFIRMED plus unresolved challenge becomes CONTESTED) versus :1645-1655 (CLOSED reads only REOPEN, i.e. challenge-immune). I recounted the population across 10 live archives: 38 entries end in exactly this state (exp43 3+7, exp44 8, exp45 7, exp46 4, exp48 1, exp53 2+6). Adversarial harness: 5 such findings with one late challenge each produced 11 consecutive blocked rounds against exp53's max_rounds=16, plus 5 HIL escalations.

**Fix.** Give this population a route to terminal. Cheapest correct version: after N rounds at CONFIRMED with no new challenge, make the entry challenge-immune (mirror the CLOSED rule at :1645-1655), or add a dedicated pass that resolves an adjudicated, un-tool-checkable sub-critical to a distinct terminal status. Do NOT restore the clean-parse PASS — it closed 5/5 harmful fixes including a remote fetch-and-exec.


### 5. [MEDIUM] The panel prompt still tells every model, every round, that the runner applies a parseable fix, runs ruff + mypy + bandit + the test suite, and transitions the finding to CLOSED on a clean pass. At HEAD on a prose target none of that happens. The panel is being briefed on a state machine that no longer exists, and today's repair is what made the description false without the prompt being swept.

**Anchor.** bench/reference_runner_v2.py:1217-1221, verbatim: 'When a CONFIRMED finding carries a parseable proposed_fix in SEARCH/REPLACE format, the runner applies it to a sandbox copy of the target file and runs ruff + mypy + bandit + the experiment's test suite. On clean pass, the finding transitions to CLOSED and is removed from the active discovery pool.' Contrast bench/bugzilla_loop.py:649-659, where a clean parse now returns closed=False.

**Fix.** Branch that paragraph on target_kind — which the harness already resolves — so a prose run tells the panel the truth: fixes are not tool-verified on this target, and a finding settles on a CONFIRMED runnable falsifier. One edit, no behaviour change.


### 6. [MEDIUM] A syntactically valid but logically broken falsifier can produce a false CONFIRMED and close a finding against a claim that is TRUE, at critical severity, with no human involved. This is the mirror image of the risk CONFIRM-only was built to prevent, and CONFIRM-only does not guard it. Observed accidentally during the measurement pass, not sought.

**Anchor.** bench/falsifier_verify.py:197 and :201-202 treat any non-setup AssertionError as a genuine demonstration. A mis-indexed regex extraction in a mass-balance falsifier raised AssertionError, reverify_falsifier returned CONFIRMED, the gate set verified=True at bench/reference_runner_v2.py:1911, and the finding reached CLOSED against a true claim. The setup/precondition filter at :198-200 catches declared breakage but not a wrong computation.

**Fix.** Require a CONFIRMED falsifier to also clean-exit against a corrected copy of the document — the fixtures already supply corrected copies and all five fixture falsifiers pass that test. Cheap, and it closes the only demonstrated false-CLOSE route at HEAD.


### 7. [MEDIUM] Two of five prose falsifiers are truncated in markdown transport and return ERROR. ERROR on a critical sets escalated=True and feeds the A4 convergence block. The test suite measured the 40% rate and skipped the two tests that would have shown its consequence.

**Anchor.** bench/tests/test_prose_acceptance_stem.py:747 (self-fenced set == {'algorithms','numerical'}), :773 (verdict == 'ERROR'). Consequence unmeasured: bench/reference_runner_v2.py:1918-1932 (escalated=True, CONFIRMED demoted to UNCONFIRMED, tally['HIL'] incremented) then :2698-2704 A4 BLOCK. I re-ran the suite at HEAD: 171 passed, 4 skipped, both skips at :621 and :658 reading 'falsifier carries its own fence'.

**Fix.** Fix the transport (extract the OUTERMOST fence, or use the non-collidable sentinel the sweep prompt already uses at :2169), then un-skip the four tests. Until then the 40% figure is a fixture property, not a measurement of real panel output — count fence-carrying falsifiers in bench/logs/exp53_control_zero_live_*/r*_<model>_*.json to get the real rate.


### 8. [LOW] The falsifier gate does not clear the escalated flag when the routing ladder exhausts, so the same structurally-doomed two-rung dispatch repeats every subsequent round. On exp53 that is roughly 20 findings times 2 rungs times the remaining rounds — paid model calls that cannot succeed by construction.

**Anchor.** bench/reference_runner_v2.py:2144-2145 sets irreducible_escalation and hil_escalated but does not clear e['escalated']; only dedup (:2122) and routing success (:2129) clear it. The selection gate at :2087 therefore re-selects the entry every round.

**Fix.** Clear escalated, or set a routing_exhausted flag that the selection gate at :2087 skips, once a finding is locked irreducible. Pure cost saving; no behavioural change to the queue.


---

## Corrections to the record


- WRONG, and it matters most: bench/exp53_configs/53_control_zero_live.json:90 attributes the 1 August halt to the S_k hard gates — 'Those findings could never resolve, exhausted the routing ladder, and were locked irreducible' — and declares it fixed at commit 0b6e9ec. The first half is true (S_k did reject every fix by running ast.parse over Markdown). The causal chain is mechanically false. I grepped every escalation writer in the runner: bench/reference_runner_v2.py:1305, 1327, 1658, 1710, 1742, 1902, 1929, 2144, 2145. Not one is in the S_k pipeline (6213-6259). SK_REJECTED only increments a stats counter. Neither apply_falsifier_verdicts nor _apply_routing reads sk_result. All 20 exp53 escalations carry falsifier_verdict UNTOOLABLE (7) or ERROR (13), both written by the falsifier gate. The fix at 0b6e9ec cannot have touched the mechanism that produced the queue. If Exp 53 is re-run on the strength of that note, it will halt again.


- WRONG: the framing that today's repair is what put prose convergence at risk. The two prose runs that converged — Exp 48 at round 5, Exp 49 at round 6 — did so under bugzilla_loop.py at 12ad362, the WORST version the project has shipped, which ran ruff/mypy/bandit against a Markdown file. They reached 36/37 and 37/38 hard-terminal with a net HIL queue of zero. Close-the-loop verified 0 of 37 and 0 of 38. Relative to the version that actually produced every archive, HEAD changes nothing on prose. The only real delta is against the third repair, which never ran live.


- ALREADY CORRECTED, and worth the founder knowing it was corrected: experimental_notes/OUTSTANDING_QUEUE_to_BR2.md listed A4, A5 and A6 as TODO when all three had already landed in commit 0a15138 — the queue file was committed roughly 30 seconds after the fix commit. The document at HEAD (commit 4d10e53) now marks all three DONE and, to its credit, records that A5 was reported to the founder as 'the single largest open HIL-flood risk' before the code was checked. That claim was wrong. A5 is closed. The largest open HIL-flood risk is the routing prompt, which appears nowhere on that queue.


- OVERSTATED: the docstring at bench/reference_runner_v2.py:2004 says the extractor change is 'strictly widening' so that 'nothing the old rule admitted is newly rejected'. Measured over real archived panel output, 101 prose-target and 104 code-target blocks ARE newly rejected. The narrowing is correct — 100% of them fail ast.parse and are prompt text that merely contained the word 'import' — but the sentence as written is false and should say so.


- MISLEADING BY OMISSION: the commit message '51 tests, 9 classes' and the green suite do not evidence convergence reachability or HIL load. No test in the set touches a convergence gate, a status-transition function, or any HIL counter, and no test asserts that any finding ever reaches CLOSED. The fixtures' own README (bench/tests/fixtures/stem/README.md:302) states the boundary honestly — 'They do not exercise the panel, the routing ladder, S_k, gamma, or convergence' — but that disclaimer sits where nobody reading the commit will find it.


- STALE: the module docstring at bench/tests/test_prose_acceptance_stem.py:40-58 describes a defect as open under a strict xfail. It was repaired at 21:20 and the xfail removed; the suite reports zero xfails at HEAD. Its 'MEASURED STATUS' block is no longer current. The transport defect it also names IS still open.


- STALE: the panel prompt at bench/reference_runner_v2.py:1217-1221 tells every model that a parseable fix is applied, linted, tested and CLOSED on clean pass. Today's repair made that false on prose targets and the prompt was not swept.


---

## Recommended actions


- FIRST, before any further paid run on a prose target: make the routing prompt prose-aware. Pass the target path and, for a listing-referencing finding, the listing text, into _routing_resolve_prompt (bench/reference_runner_v2.py:1954-1966), and branch _ROUTING_SYSTEM on target_kind the way _sweep_prompt already branches at :2196-2222. Do the same for the panel falsifier directive _RUNNABLE_FALSIFIER_S2. This is the single change that converts 25 measured 'irreducible' escalations into programmatic resolutions, and it is the difference between Exp 53 halting at round 3 and finishing. Add a test asserting the target path reaches the prose-branch prompt — neither prompt currently has one.


- SECOND, and it costs nothing: the five remaining prose targets (BX-14, DR-09, PR-14, PX-12, SW-14) are named in the Exp 50/51/52 configs but do not exist on disk yet. Only SW-21-REF-04.md exists, and it has 7 fenced blocks. Until the routing prompt is fixed, author those documents with their STEM claims in prose, tables and equations rather than in fenced code listings. Exp 48 and Exp 49 are the proof this works: zero listing-referencing findings, 41 routing resolutions, 1 escalation in 75 findings. This is a choice available today, and it decouples the remaining arc from the routing defect.


- THIRD: correct bench/exp53_configs/53_control_zero_live.json:90 before anyone acts on it. Its diagnosis of the halt is mechanically wrong and will send a re-run into the same wall. Replace the S_k attribution with the routing-prompt mechanism and the verified escalation cross-tab (UNTOOLABLE 7, ERROR 13, from the falsifier gate at :1902 and :1929).


- FOURTH: run the post-convergence sweep on a halt and on a round-cap exit, not only on convergence (bench/reference_runner_v2.py:8389). It is configured at 2 rounds in exp53 and never executed. The cleaner being disabled in exactly the runs with the worst residue is the cheapest structural fix on this list.


- FIFTH, a founder ruling is needed, not an engineering decision: the sweep cannot clear a critical, and a false-positive critical is therefore permanent human work decided by a single un-recomputed severity float. The instrument tolerates two such residents before refusing to converge. Either accept that ceiling explicitly, or authorise one of: recording a REFUTED verdict on a critical even where the sweep declines to act on it, or a narrow demotion path for a critical whose falsifier clean-exits against both the document and a corrected copy. I recommend recording the verdict at minimum — a human adjudicating a permanent resident should see the computation the instrument already performed and discarded.


- SIXTH: fix the falsifier transport (extract the outermost fence, or reuse the non-collidable sentinel already at :2169), then un-skip the four tests at test_prose_acceptance_stem.py:621 and :658. And measure the real rate — the 40% figure is a property of five hand-written fixtures, not of panel output. Counting fence-carrying falsifiers in bench/logs/exp53_control_zero_live_*/r*_<model>_*.json settles it offline, for free.


- SEVENTH, before the next prose run: give the 38-entry stuck-CONFIRMED population a route to terminal — either challenge-immunity after N quiet rounds, mirroring the CLOSED rule at :1645-1655, or a dedicated resolution pass. And sweep the panel prompt at :1217-1221, which now describes machinery that no longer runs on prose.


- DO NOT restore the third repair's clean-parse PASS. Measured: it closed 5 of 5 correct fixes and 5 of 5 harmful ones, including a remote fetch-and-exec, an eval of an environment variable, and rm -rf with shell=True. The five correct-fix closures it gave up are closed anyway by the falsifier gate, one round later at most. The tri-state repair is a strictly good trade and nothing in this analysis argues otherwise.


- FINALLY, one honest boundary: no run has completed at HEAD. Every archive predates today's repairs, and the routing ladder and post-convergence sweep both dispatch live models and cannot be exercised offline. Everything above is anchored in code read at HEAD, offline harnesses driving the real functions, and archives from the pre-repair instrument. A single completed Exp 53 control run after the routing-prompt fix is what would settle the post-repair prose HIL rate, and until it exists no number in this report should be quoted as HEAD's steady-state behaviour.


---

Written under CDSFL note standard v1.2 (14 May 2026).
