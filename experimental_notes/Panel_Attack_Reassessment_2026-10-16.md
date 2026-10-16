# The attack broke 3 of my claims, I broke 2 of its findings, and neither fix is ready

Written 2026-10-16 18:35 BST. HEAD `f22cd671`, branch `sim/shakedown-2026-09-29`, working tree clean. Nothing in this note has been applied.

## What was run

4 independent adversarial checks against my composability verdict, 2 at a time, because the founder's machine holds only 1 heavy process at a time against 1,240 mebibytes of live headroom. All 4 returned **PARTIALLY_BROKEN**. None returned BROKEN and none returned HELD. 814,914 subagent tokens, 182 tool uses, 28.9 minutes, no model dispatched, no file in the repository written.

Every finding below that lands on my own work I re-measured myself before accepting it, and 2 of the agents' figures did not survive that.

## The 3 claims of mine that broke

**Claim (c) was false as worded.** I wrote "nothing that resolved before resolves differently". Re-measured on my own fixture: of 48 forms, 24 resolved at HEAD and **18 of those 24 now resolve differently** — 75.0000%, Wilson [55.1006%, 88.0006%]. They resolve differently because they were resolving to the WRONG finding, which is the repair working. But the sentence as written denies the mechanism the patch exists to provide, and Fable's own comment carries the same unqualified sentence. The defensible pair, which survives: **0 of 24 become unresolved** (Wilson [0.0000%, 13.7976%]) and **0 of 48 resolve to an entry the evidence never names** (Wilson [0.0000%, 7.4100%]).

**Claim (e) was false as worded.** I said the widening lets a seat NAME another seat's finding but not ACT on it, because an owner check follows the resolution. The owner check is not a gate that stops — it is a branch that WRITES. At `bench/reference_runner_v3.py:6664-6675`, inside `if owner and str(model_id) != owner:`, it writes `entry["corrected_copy_rejected"]` onto the other seat's entry, and `build_summary` takes no `model_id`, so that text reaches every seat's next prompt. I verified the write myself. The safety conclusion largely holds for a reason I had not given: the same state change was ALREADY reachable cross-model through the canonical id, so the widening adds trigger spellings rather than a new authorisation class.

**Claim (b)'s reasoning was unsound, and its conclusion is wrong too.** "Different functions, therefore no interaction" is not an argument. Measured: Fable's merge-source fix changes **both numbers my A4 LIMBO line prints** — the counts move in 4 of 16 writer-by-owner forms (25.0000%, Wilson [10.1821%, 49.4983%]) and the limbo MEMBER SET moves in 13 of 16 (81.2500%, Wilson [56.9911%, 93.4084%]). The direction favours adopting it: at HEAD the limbo list names a finding that was never touched and omits the one that was.

And a 4th, at the file level: **Fable's delivered runner is a whole-file replacement built on commit 47c51b1b, the tree as it stood before the A4 limbo additions landed at 17:07.** It contains 0 occurrences of `_routing_would_admit`, `blockers_routing_cannot_serve` and `A4 LIMBO`, against 2, 3 and 1 at HEAD. My "applies cleanly" was true of a patch I extracted by hand; taking the artefact as delivered would delete all 3 additions.

## The defect in my own published figure

**`94 of 212` does not reproduce against the real reader, and the cause is mine.** My producer `scripts/a_blocker_the_ladder_will_not_serve_2026-10-16.py` carries a hand-written MIRROR of `unverified_critical_count`'s release conditions rather than calling it. Executed side by side over all 74 archived states:

| | my mirror | the real method |
|---|---|---|
| blockers | **212** | **197** |
| unservable | 94 | 94 |
| runs affected | 18 | 18 |

The mirror is wider by **15** entries across 5 runs, because it implements 3 of the counter's skips and omits `_integrity_violation_excluded` and the proven-sub-critical severity release. The numerator of 94 and the run count of 18 are right; the denominator of 212 is wrong. The corrected figure is **94 of 197 = 47.7157%**, Wilson [40.8515%, 54.6673%], Clopper-Pearson [40.5684%, 54.9329%], against the published 44.3396%.

This is the exact failure this project has recorded before as `execute-do-not-grep` and "verify the deciding layer": I mirrored a deciding function instead of calling it, and the mirror drifted. My own producer's docstring even says the predicate "mirrors the counter's own skips". The wrong figure is live in 5 places: that producer, the `blockers_routing_cannot_serve` docstring, the test file's docstring, task entry B14, and the end-of-day note.

## The 2 agent findings that did not survive my check

**Cross-seat merge nomination does NOT need a ruling on the grounds given.** 1 agent argued it opens a new authorisation class and that "the codebase already states the opposite principle". The record says otherwise. `lookup_alias_any`'s own docstring states that a cross-model duplicate is **"the ONLY case co-discovery exists for"**, and `add_verdict(canonical_id, model_id, verdict, ...)` has never carried an owner check for ANY verdict type. The agent conflated the corrected-copy rule, where only the owner may supply the discriminating passage, with the verdict rule, where any seat may rule on any finding because that is the blackboard design. What is genuinely new is narrower: a MERGE SOURCE can now be a foreign composed id, which is precisely the gap `lookup_alias_any` was written to close.

**The `93 of 197 over 28 runs` figure is wrong.** The 197 is right and is the correction above. The 93 and the 28 are not: the real readers give 94 and 18, reproduced exactly.

## What the attack found that is new, verified, and not mine

**Fable's composer would turn a test that is already committed RED.** `bench/tests/test_the_composer_fallback_flag_is_consumed_2026-10-16.py:156` asserts `"No detection penalty is applied" in m`. HEAD's composer emits that phrase; Fable's emits "No penalty is applied" and contains 0 occurrences of the asserted phrase. So the 2 seats' replacement sentences are mutually exclusive and 1 of them is pinned by a shipped assertion. This is the hard half of the composer collision, and I had found only the rejected patch hunk.

**The premise both composer guards rest on is leaky.** `compose(task_domain='no_such_domain_xyz')` returns a non-None result after silently dropping an entire directive layer, so the dispatch records `composer_fallback: False` beside a density computed from a degraded composition. The marker therefore does not partition records into trustworthy and untrustworthy, which is the only job either guard gives it.

**CC2's skip does not produce "no answer".** Because `thresholds.setdefault` runs over `MODEL_COHERENCE_BUDGETS` at `composer.py:1638-1640`, a skipped model silently falls back to the source literal, and nothing in the output marks that data was discarded. Measured: 6 all-fallback records for `opus_4_6` give 0.02 under HEAD, which is exactly the literal.

**`docs/GLOSSARY.md` still states the retracted claim, and also describes the retired pruner as active.** Lines 103 to 112 read that the composer "prunes SOFT content to get under it" and that "a coherence penalty, written in the model as kappa(m,g) < 1, applies to effective detection". Pruning has been retired by default since the 2026-10-13 ruling, and the penalty sentence is the one both seats just retracted from the code. Neither bundle touches the glossary, and it is the operator-facing definition.

**My own kappa comment is false by count.** HEAD's composer comment says "every `kappa` in the live tree is `kappa_set`". Enumerated: `kappa_stuck` 62, `kappa_rate` 40, `kappa_history` 25, `kappa_adopt` 19, `kappa_window` 6, `kappa_converged` 2. All are convergence or pathology keys rather than detection penalties, so the operative half survives, but the sentence as written is wrong. And kappa(m,g) as a coherence penalty IS live in the tree, at `bench/gemini_math_audit.py:72,77,116`, inside a prompt payload: "kappa(m,g) = coherence penalty (new — conflicting directives degrade quality)". My own panel FULL RECORD states this correctly; both code comments drop it.

**Fable's fix is partial, and its own new test is vacuous.** A single `.`, `-` or `_` between 2 identifiers defeats the token scan and silently restores the mis-attribution. Its token pattern is compiled inline on every call and the scan is quadratic in evidence length, slope 1.9659 by 2 tools. And `test_fallback_records_do_not_pollute_a_calibration_from_real_densities` passes on commit 47c51b1b, where neither seat's guard exists yet, so it cannot detect the absence of either guard.

**Its safety justification does not apply on its own path.** Fable's comment relies on `lookup_alias_any` refusing ambiguity. That refusal cannot fire for a prefixed token, because composed ids embed the seat label and are all-distinct by construction. So every foreign composed id named in a MERGE line resolves and is acted on, and nothing refuses.

## Reachability, measured twice

The misfire is not a fixture artefact. Scanning every archived `alias_map`: **442** composed finding ids are misread by the digits regex, confirmed by 2 independent implementations, with the seat breakdown CC2 251 and CC2-SIM 188. On `CC2-SIM_F004` the pattern matches `C2` at offset 1, inside the seat label, so the function returns None and the specification converts an unresolved merge source into a CONFIRM on the target.

The proportion depends on which denominator is used: 442 of 3,098 composed locals is 14.2673%, Wilson [13.0799%, 15.5431%]; 442 of the agent's narrower 2,445 is 18.0777%. **This is the third time today a figure's numerator agreed while its denominator was the disputed part**, after the 64-versus-81-versus-98 identifier count and the 5,946-versus-30,442 dispatch-entry count. The predicate has to be named every time.

## Where this leaves the position

Stages 1 to 3 carry 19 items with 6 done, 31.5789%, Wilson [15.3644%, 53.9896%]. Stage 1 has 1.6 and 1.7 outstanding, Stage 2 is 3 of 3 outstanding and needs 1 live run, Stage 3 is 6 built-but-unrun plus 3.7 not built. The task list is 111 entries with 11 open and 1 blocked.

**Stage 1 item 1.2 is marked DONE and is incompletely closed.** Its text is "`_resolve_merge_source` cannot resolve the syntax the runner itself teaches, so MERGE silently recasts to CONFIRM", which is Fable's finding verbatim. Within its own stated scope, the owner's own composed id, it still fails for 2 of 8 seat labels, 25.0000%, Wilson [7.1479%, 59.0725%], and only for `CC2` and `CC2-SIM` because that label contains `C2`. Fable's fix takes it to 0 of 8. The original in-code comment enumerates `F001` and `Codex_F001`, so the implementer verified with Codex and never with CC2.

**The runway has no repository copy.** It exists only as `~/Desktop/CDSFL_RUNWAY.md`, unversioned, which is the single-point-of-failure argument already accepted for the operational tracker. 6 Stage 3 rows still read "blocked on the held-out-status ruling", stale against commit `102444cc` from 14:46 today.

## The optimal way forward

Ordered by dependency, cheapest first, nothing applied.

**1. Correct my own figure before anything else is built on it.** The 212 becomes 197 in 5 places, and the producer must CALL `unverified_critical_count` rather than mirror it. This is a correction, not a decision, and it is owed under `measured-rate-travels-with-its-script`.

**2. Keep CC2's composer fix. This is now settled by evidence rather than preference.** Its md5 is identical to HEAD, Fable's would turn a committed assertion red, and the only shape where the 2 guards differ cannot be produced by any live producer: 0 of 8,363 archived entries carry both fields, Wilson [0.0000%, 0.0459%]. Record the measured difference so a second producer cannot reintroduce it silently.

**3. Fix the 3 things both seats missed, which are independent of either patch.** The glossary's 2 stale sentences, the kappa comment that is false by count, and the fact that a skipped model silently inherits the source literal with no mark that data was discarded.

**4. Adopt Fable's runner fix, with 4 repairs first, as a hand-applied patch and never as the delivered file.** Correct the interval to Wilson [48.3628%, 74.7847%]; qualify the "nothing resolves differently" sentence to the pair that survives; hoist the token pattern to module scope; and either gate the refusal write in `_ingest_corrected_copies` on the offering seat holding its own alias, or add the distinct "cross-model id, confirm you mean this finding" line so the mis-cite is caught rather than silenced.

**5. Then Stage 1 item 1.7, the replay, which costs nothing and is the stage's exit test.** And re-open 1.2, because it is marked DONE on an incomplete repair.

## Smaller corrections that go with them, so nothing is left without an action

**6. Correct the reasoning behind claim (b) in the record, not only its conclusion.** The conclusion is now known wrong and the reason given was never an argument. The next patch to either side will otherwise be assessed against the same unsound test — that code in different functions cannot interact. It shares the entry dict, so it can.

**7. When the blocker figure is corrected, record that the checker's replacement was also wrong.** It gave 93 over 28 runs against the real readers' 94 over 18. Neither figure should be quoted again without its producer.

**8. Decide what to do about the leaky success marker, because it undermines BOTH composer repairs rather than either.** `compose(task_domain='no_such_domain_xyz')` returns non-None after dropping a whole directive layer, so the record carries `composer_fallback: False` beside a degraded density. Recommendation: record the dropped-layer COUNT in the dispatch record and have both guards read that, not the boolean. A flag that says nothing about degradation cannot do the job either guard gives it.

**9. Handle Fable's known hole rather than inheriting it silently.** A single `.`, `-` or `_` between 2 identifiers defeats the token scan and restores the mis-attribution. That seat already pinned the residual it did not build for; keep that pin and add the separator case to it.

**10. Re-derive Fable's new test or drop it.** `test_fallback_records_do_not_pollute_a_calibration_from_real_densities` passes on `47c51b1b`, where neither guard exists, so it cannot detect the absence of the thing it guards. Its other changed assertion IS discriminating and should be kept.

**11. Correct Fable's own safety comment.** It justifies the widening by `lookup_alias_any` refusing ambiguity, and that refusal cannot fire for a prefixed token, because composed ids embed the seat label and are all-distinct by construction. The widening may still be right; the stated reason is not.

**12. Put the runway into the repository.** It exists only as `~/Desktop/CDSFL_RUNWAY.md`, unversioned — the same single point of failure already fixed for the operational tracker by keeping the canonical copy in `experimental_notes/` with a Desktop mirror. Refresh the 6 stale Stage 3 rows at the same time.

**13. A habit, not a repair: make the predicate part of every reported figure.** Three times today a numerator agreed across 2 independent measurements while the denominator was disputed — the identifier count (64 / 81 / 98), the dispatch-entry count (5,946 / 30,442), and the blocker count (212 / 197). `scripts/how_many_identifiers_carry_a_bare_vendor_name_2026-10-16.py` already prints its whole predicate lattice for this reason; the blocker and dispatch-entry producers should do the same.

Written under CDSFL note standard v1.7, 26 August 2026.
