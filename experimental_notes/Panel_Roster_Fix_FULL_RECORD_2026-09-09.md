# Panel — roster confinement fix, FULL RECORD, unfiltered

Record written 2026-09-11T09:42:34+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

This round reviewed task 3.1a — repairing the runner so routing and the post-convergence sweep respect `cfg.models`, after which the arms' disabled flags lift themselves. The founder had ruled *"these are the class of misconfigurations I observed as significant previously and they should be fixed"*, and the literal reading of that ruling would have flipped flags that were a documented mitigation for 2 live runner defects — destroying the experiment the arm exists to run and spending money doing it.

## What the round found

**CC2 CAUGHT A GUARD THAT COULD NOT GO RED.** The test written to prove the repair called the helper directly rather than the caller, so it did not fail when the wiring was reverted. That is the defect this project names as "a guard that cannot fail is not a guard", inside the guard for the repair.

**ONE FURTHER FINDING WAS REFUSED, and the refusal is measured.** The panel proposed filtering `_verification_step` for consistency. Against the 3 arm configs that removes CC2v from the contrast arm alone, converting a held-constant control into a confound in 1 of 3 arms. Refused, pinned at the call site and by `test_cc2v_is_held_constant_across_arms_2026-09-09.py`.

**THIS IS ONE OF THE 2 ROUNDS WHOSE SEAT REPLIES CARRY NO `strongest_disagreement` FIELD** — it was dispatched before that field was written into the brief. The misses are identified, not unexplained.

**A CAUTION THAT APPLIES TO THIS ROUND.** Until task A20 landed on 2026-09-11, all seats shared ONE writable sandbox and ran concurrently. Agreement between seats here is not evidence of independence.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Did today's roster-confinement repair actually close the leak, and did it break anything it was not meant to touch?

## The question

`_apply_routing` and `_post_convergence_sweep` in `bench/reference_runner_v3.py` both iterated `exp_config.models`, the full orchestrator roster, instead of the models the running arm declared in `cfg.models`. A new helper `_declared_models(exp_config, cfg)` now filters the roster, and both call sites use it. The founder has, on the strength of that repair, ruled routing and the post-convergence sweep ON in all 3 arms of `bench/exp56_configs/`.

**Your question: is that repair correct, complete, and safe enough to justify turning both mechanisms on?**

## What you are reviewing

- `bench/reference_runner_v3.py` — the new `_declared_models` helper and its 2 call sites.
- `bench/routing.py` — `rank_falsifier_writers`, which the helper feeds.
- `bench/tests/test_declared_models_roster_2026-09-09.py` — the new guards.
- `bench/tests/test_d9_d11_configs_valid_2026-09-05.py` — 3 pre-existing guards that were re-aimed rather than deleted.
- `bench/exp56_configs/*.json` — the 3 configs whose flags were flipped.

## Use the harness

RUN things. Do not describe them. Import the runner, call `_declared_models` with constructed rosters, drive `_post_convergence_sweep` with a stub in place of `dispatch_to_model` and count the seats reached. Report the command you ran and the output you saw.

Use the mathematical model as an instrument, not as background. Specifically:

- **Severity and S_k**: the ladder exists to resolve un-confirmed criticals. Does confining the roster change which findings can reach a resolving seat, and therefore change S_k's input distribution?
- **gamma**: routing resolutions feed the critical series. If confinement reduces the seats available, does gamma's decay shape change, and would a run that previously converged still converge?
- **rho**: the cross-architecture correlation is measured across seats. A 1-seat arm has no cross-architecture signal at all. State what rho can and cannot mean under confinement.

Measured, for your reference and to be checked rather than trusted: across 7 deduplicated simulated runs the ladder took 69 findings and absorbed 53 of them — 76.8%, Wilson [65.6%, 85.2%] — with 9 reaching the human. If the repair damages that, it is not worth having.

## Produce a fix, and test it

A finding without a fix is half an answer. A fix without a runnable falsifier that you have EXECUTED is a hypothesis. For every defect you raise, supply the falsifier, run it, and report its output.

## What would refute you

Before you conclude, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

Specific things worth attacking, since a reviewer told where to look is more useful than one told to look everywhere:

1. The `-SIM` suffix normalisation. In a simulated run the roster is `CC2-SIM` while a config may declare `CC2`. Is the normalisation correct in both directions, and is there a label shape that defeats it?
2. The empty case. If an arm declares seats the roster does not carry, `_declared_models` returns an empty list and logs. Is returning empty right, or should it refuse the run outright?
3. The re-aimed guards. Three pre-existing tests were changed because the defect they pinned is gone. Were they re-aimed honestly, or weakened to make a change pass?
4. Whether anything else in the runner still reads `exp_config.models` where it should read the declared subset. 2 sites were found. Are there more?

## Output

Return, as named fields:

- **verdict** — is the repair correct, complete and safe to enable? One of CONFIRMED, REFUTED, UNCERTAIN.
- **reasoning** — the derivation, not the conclusion.
- **falsifier** — the code you wrote, and the output you got when you ran it.
- **disagreement** — your strongest objection to this brief's own framing.
- **model_use** — where gamma, rho, S_k or severity bore on your answer, with values.

## Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. Diminishing returns is this project's own criterion, and a clean verdict backed by derivation is as useful as a finding.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 44 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_roster_fix_2026-09-09) -->

## verdict

**REFUTED** — the two repaired sites are correct and correctly guarded, but the repair is **incomplete**, and one consequence of enabling routing is unsafe. Turning routing and the sweep on is not yet justified for all three arms. Two material findings, both with executed falsifiers and verified fixes.

The parts that are sound, established by execution:

```
$ python3 -m pytest bench/tests/test_declared_models_roster_2026-09-09.py \
                    bench/tests/test_d9_d11_configs_valid_2026-09-05.py -q
81 passed, 1 warning in 0.61s
```

```
$ python3 /tmp/fx/f2.py     # drives both call sites in all 3 arms, stubbed dispatcher
=== d9_single_model_with_agents.json   declared=['CC2']
 _declared_models -> ['CC2']   ladder(exclude=CC2) = []
 routing seats reached: []      sweep seats reached: ['CC2','CC2']            undeclared: []
=== d9_multi_model_panel.json          declared=['CC2','Codex','Gemini','DeepSeek','ChatGPT']
 routing seats reached: ['Codex','ChatGPT']  sweep: all 5 × 2 rounds          undeclared: []
=== d11_seat_contrast_diversity_arm.json declared=['Codex','ChatGPT']
 routing seats reached: ['ChatGPT']          sweep: ['Codex','ChatGPT']×2     undeclared: []
```

**Mutation test (item 3 — were the guards weakened?).** I reverted both call sites to `exp_config.models`, ran the suite, restored:

```
mutant applied
FAILED test_declared_models_roster_2026-09-09.py::test_the_SWEEP_reaches_only_declared_seats
FAILED test_declared_models_roster_2026-09-09.py::test_apply_routing_builds_its_ladder_from_the_DECLARED_roster
FAILED test_d9_d11_configs_valid_2026-09-05.py::TestSubsetPanelLeaks::test_the_post_convergence_sweep_dispatches_to_undeclared_seats
3 failed, 78 passed
RESTORED → 81 passed
```

The re-aimed guards are **honest**. The inverted sweep assertion still asserts `reached` non-empty first, so it cannot pass vacuously, and it dies under the mutant. The preflight guard was *strengthened*, not weakened — it now builds its own routing-off fixture instead of borrowing a production value, and adds a converse check that the refusal discriminates. One caveat worth stating: `test_the_routing_ladder_reaches_only_seats_the_arm_declared` does **not** go red under the mutant, because it calls `_declared_models` directly — it has exactly the weakness its own docstring criticises in its predecessor. It is covered only because the new file's two wiring tests exist.

**Edge shapes (item 1).** `-SIM` normalisation is correct in both directions; whitespace stripped; case variants and double suffixes fail closed with a loud log. The one thing that defeats it is case (`'cc2'` → `[]`), which fails safe.

```
SIM roster, bare decl  roster=['CC2-SIM',...] decl=['CC2']     -> ['CC2-SIM']
REAL roster, SIM decl  roster=['CC2',...]     decl=['CC2-SIM'] -> ['CC2']
case variant 'cc2'                                             -> []   (+ ROSTER EMPTY log)
```

**Empty case (item 2).** Returning empty is right — refusing the run would be a new failure mode in a helper whose whole job is selection, and the log fires. But see finding C-B: empty is only safe if the *caller* knows why it is empty.

---

## findings

### C-A (material) — a third live leak site the repair missed

`_verification_step` (CC2v, A5) is handed `exp_config.models` at `reference_runner_v3.py:13052`, unconditionally, and selects a seat by base label. Arm C declares `['Codex','ChatGPT']` and gets **CC2** — a seat it never declared — at every round ≥ `verification_min_round` (6), with `max_rounds` 8. That silently makes Arm C a three-seat arm for its last two rounds and contaminates the D9/D11 comparison the arms exist to run.

I enumerated all 8 `dispatch_to_model` call sites. Answer to item 4: routing (5244, fixed), sweep (5769, fixed), the three inside `_dispatch_single_model` (fed from `eligible`, filtered by `cfg.models`), preflight (11378, filtered), merge arbitration (12020, full roster but off in all three arms and documented), and **9163 — `_verification_step`, full roster, ungated**. Exactly one unmitigated site remains.

```
$ python3 /tmp/fx/f1.py
arm declares : ['Codex', 'ChatGPT']
roster carries: ['CC2', 'Codex', 'ChatGPT', 'Gemini', 'DeepSeek']
verification_min_round = 6  max_rounds = 8
seats reached by CC2v: ['CC2']
FALSIFIED
AssertionError: CC2v dispatched to seats Arm C never declared: ['CC2']
```

**Fix** (one line at 13052, plus the comment block):

```diff
-        verification_stats = _verification_step(
-            registry, round_idx, full_code, exp_config.models, cfg)
+        verification_stats = _verification_step(
+            registry, round_idx, full_code,
+            _declared_models(exp_config, cfg), cfg)
```

This is a confinement, not a removal: Arm C loses CC2v *because it declared no CC2 seat*, and the existing `{"skipped": True, "reason": "CC2 config not found"}` already announces it. Verified that it does not become a blanket disable:

```
$ python3 /tmp/fx/f3.py
PRE  d11_seat_contrast... declared=['Codex','ChatGPT'] reached=['CC2'] undeclared=['CC2']
POST d11_seat_contrast... declared=['Codex','ChatGPT'] reached=[]      undeclared=[] skipped=True
POST d9_single...         declared=['CC2']             reached=['CC2']
POST d9_multi...          declared=[...5...]           reached=['CC2']
clean: leak closed, CC2v retained in every arm that declares CC2
```

### C-B (material) — an empty ladder is misclassified as a dead transport

Newly reachable *because* routing was just enabled. In Arm A the ladder is `rank_falsifier_writers(['CC2'], exclude=['CC2']) == []` — measured. `route()` returns `rungs_tried=0`, and the transport-dead guard at ~5364 `continue`s before the deferral stamp. The critical carries **neither** `routing_deferred` **nor** `irreducible_escalation`: it blocks convergence forever (`unverified_critical_count` counts UNCONFIRMED and skips only `irreducible_escalation`) while never entering `irreducible_queue_count` (which counts `irreducible_escalation OR routing_deferred`). The `HALTED_IRREDUCIBLE_QUEUE_ALARM` that Arm A's own pre-registration names as its reportable outcome **cannot fire**.

```
$ python3 /tmp/fx/f5.py
ARM A  declared=['CC2']  rungs_available=1 rungs_tried=0 verdict=UNTOOLABLE
       routing_deferred=None irreducible_escalation=None escalated=True
       irreducible_queue_count=0  unverified_critical_count=1
ARM C (transport DEAD)   rungs_available=2 rungs_tried=1
FALSIFIED
AssertionError: Arm A: empty ladder -> no deferral stamp, queue count 0,
unverified count 1. The pre-registered irreducible-queue halt cannot fire and
the critical blocks to the round cap instead.
```

Note `rungs_available=1` in the history record: a human reading the bundle sees "1 rung available, 0 tried" and reads a transport failure. The one available rung is the source model itself.

**Fix** — one branch, no new state. `resolve_via_routing` increments `tried` *before* calling `resolve_fn`, so `rungs_tried == 0` can only mean the ladder was empty:

```diff
         if e.pop("_error_route_pending", None):
             if len(_routing_attempts) > _n0:
                 e["error_routed"] = True
+            elif getattr(result, "rungs_tried", 0) == 0:
+                # EMPTY LADDER != DEAD TRANSPORT. Waiting for a later round
+                # cannot help: the ladder is empty by construction.
+                e["routing_deferred"] = True
+                _log(f"  routing {cid}: EMPTY LADDER ({len(models)} declared "
+                     f"seat(s), all excluded as the source) — deferred, "
+                     f"not transport-dead")
+                continue
             elif not result.resolved and result.verdict != "DUPLICATE":
                 continue
```

Discriminator proven exact, and consequence measured:

```
$ python3 /tmp/fx/f6.py
empty ladder  -> rungs_tried=0 verdict=UNTOOLABLE
rung present  -> rungs_tried=1 verdict=ERROR
discriminator EXACT: rungs_tried == 0 iff the ladder had no rungs

stamp=False queue=0 unverified=3 alarm=silent evidence_items=-
stamp=True  queue=3 unverified=3 alarm=FIRES  evidence_items=3
```

Additive on both counts: the stamp does **not** excuse the critical (unverified count stays 3, it keeps blocking), and it restores the alarm *with* its evidence bundle — the 2026-09-08 collector at line 6085 already reads `routing_deferred`.

### Below threshold, recorded not blocking

- `_declared_models`'s local `_base` duplicates `base_model_label`, defined in the **same module** at line 449. The docstring's justification ("routing.py must not import its own caller") is a non-sequitur here. Four copies now exist (runner_core:88, routing.py:97, rr:449, rr:5174). Identical today; a divergence risk, not a defect.
- `_routing_note` and `_sweep_note` in all three configs still read **"OFF IN ALL THREE ARMS"** beside `routing_enabled: true` and `post_convergence_sweep_rounds: 2`. The comment at 5364 likewise still asserts "routing_enabled is unset in all 14 forward configs — VERIFIED against the config files". Behaviour follows the flags, so this misleads a reader, not the runner.
- `_declared_models` normalises `-SIM`; the panel-eligibility rule at 8362/8442 matches labels exactly. Measured divergence: SIM roster + bare declaration gives `panel_eligible=[]` while `routing/sweep=['CC2-SIM']`. Not live — no exp56 arm is simulated, and an empty panel would be immediately visible.

---

## model_use

**S_k.** Vacuous here, and I will not manufacture an answer: `sk_enabled: false` in all three arms (measured). Confinement cannot change an input distribution that has no inputs. Generally the brief's premise holds — fewer resolving seats means fewer findings reach a rung that proposes a fix, so S_k's input set shrinks — but not in Exp 56.

**γ.** Ladder depth per arm, measured: A = 0 rungs, C = 1, B = 4 (capped at `max_rungs=2`). Taking §5's `C(n) = 1 − (1−q)ⁿ` with the archive's 53/69 = 0.768 measured on full-roster ladders at n = 2:

> (1−q)² = 0.232 → q = 0.518; Wilson [0.656, 0.852] → (1−q)² ∈ [0.148, 0.344] → **q ∈ [0.414, 0.615]**

Predicted absorption under confinement: **Arm B 0.768** [0.656, 0.852] (unchanged — it declares all 5), **Arm C 0.518** [0.414, 0.615], **Arm A exactly 0** — not an estimate, a measurement, the ladder is `[]`. Residual per un-confirmed critical therefore rises 0.232 → 0.482 → 1.000. With `max_irreducible_queue = 2`, Arm A halts at its third un-confirmed critical *once C-B is fixed*; today it silently runs to the round cap instead.

Does γ's decay shape change? No. γ_critical is computed on the location-keyed critical *arrival* series; routing converts escalated criticals to CONFIRMED but does not change arrival rate. Arm A's binding gate is criterion (3), "no unverified critical pending" — not γ. And the honest answer to "would a run that previously converged still converge": **the question has no archival referent.** The test file's own section 10 states no configuration has ever declared a panel subset. There is no prior confined run to regress, and equally no evidence that one converges. The 76.8% figure was measured on 4-rung ladders in deduplicated simulated runs; it does not transfer to a 0- or 1-rung arm, so "did the repair damage it" is the wrong test. It is unchanged for Arm B and inapplicable to A and C.

**ρ.** Estimable pairs = C(k,2): Arm A → **0 pairs, no estimator at all**. Any ρ Arm A reports is a default, not a measurement, and `rho_threshold: 0.25` over a rolling window of 3 cannot gate on it — it must not be read as evidence of independence. Arm C → 1 pair, and by the config's own `state_at_head_measured` those two seats share model_id, api, role and system_prompt_path, so what is measured is composed-phenotype divergence between two instances of the same weights, not cross-architecture correlation; reporting it as ρ is a category error. Only Arm B (10 pairs, 4 vendors) yields cross-architecture ρ. Note the direction: the repair **improves** ρ's validity — the leak would have injected 4 undeclared vendors into Arm A and could have manufactured a spurious cross-architecture ρ in a 1-seat arm.

**Severity.** `CRITICAL_SEVERITY_THRESHOLD = 0.7` gates the sub-critical ladder branch; both findings above sit at severity ≥ 0.7 in the arms' own terms — C-A because it changes an arm's seat count mid-experiment (verification-integrity, §10 cat. 3), C-B because it suppresses a pre-registered reportable outcome (§10 cat. 4).

---

## disagreement

The brief names the defect after two functions rather than after the invariant, and that framing is precisely what let C-A survive today's repair. The leak was never a property of `_apply_routing` and `_post_convergence_sweep`; it is a property of *every* consumer of `exp_config.models` that dispatches. Three call-site edits produce a fix that closes two of three live sites and a test suite that guards two of three — and the fourth site was missed because it is not called "routing". The durable fix is an invariant at the dispatcher: `dispatch_to_model` should refuse a `ModelConfig` whose label is not in the run's declared set, so that a new consumer added next month cannot reintroduce this. I did not implement that here because it is a larger change than the panel was convened for, but I would not call the leak closed until it exists.

Second: "2 sites were found. Are there more?" invites a bounded search. I answered it by enumerating dispatch sites rather than `.models` reads, which is the reason I found one. The brief's own question would have been answered "no" by a reviewer who grepped for the phrase in the diff.

## what would refute me

- **C-A**: show that `_verification_step` is unreachable in Arm C — that `run_experiment` returns before round 6, or that the arm's `max_rounds: 8` is capped below `verification_min_round: 6` by the extension/stall path in practice. My probe called `_verification_step` directly; I did not drive `run_experiment` to round 6. If the arm reliably terminates before round 6, C-A is latent rather than live — but still a defect, since `verification_min_round` is a config value.
- **C-B**: show a second writer of `routing_deferred` or `irreducible_escalation` on the path Arm A takes, which would mean the stamp arrives elsewhere and the alarm can still fire. I grepped all writers (5470 and 5529 only) and measured the entry post-call, but a later-round code path I did not execute could stamp it.
- **Both**: a founder ruling that Arm C is intended to receive CC2v verification despite not declaring CC2, or that Arm A is intended to run to the round cap rather than halt. Either would make the behaviour a design choice; both should then be written into the config as an explicit declared delta, the way merge arbitration was.
- **The clean verdict on the two repaired sites**: a config or launch path where `cfg.models` is populated after `_apply_routing` is first called, or where the roster is mutated mid-run. I assumed both lists are fixed at build time.

## termination

**4 passes.** Pass 1: read the helper, both call sites, `routing.py`, both test files; drove all 3 arms. Pass 2: enumerated `.models` reads, then all 8 dispatch sites → C-A; ran the mutation test on the guards. Pass 3: edge shapes, the empty case, the normalisation asymmetry → C-B. Pass 4: fix verification for both, and a re-check for further above-threshold findings — none. Pass 4 produced only the three sub-threshold notes above, which is the diminishing-returns signal; I stopped there rather than enumerate further.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 23 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_roster_fix_2026-09-09) -->

All passes complete. Final answer.

---

## verdict

**REFUTED** — on the conjunction asked. Decomposed: the repair is **correct at its two sites** and enabling routing + the sweep is safe on their own terms; but the repair is **incomplete as a roster-confinement guarantee**, and the founder's ruling rests on that guarantee. A third dispatch-bearing site of the identical class is live in the shipped configs: `_verification_step` (A5/CC2v) at line 13052 still receives `exp_config.models` unfiltered, and with `max_rounds=8 > verification_min_round=6` it **will fire in rounds 6–7 of every exp56 arm**, dispatching to CC2 in the d11 arm that declares `['Codex','ChatGPT']` — and its vote-based CONFIRM resolves registry entries.

## reasoning

**The helper is correct.** I exercised `_declared_models` against constructed rosters (output above): SIM-roster/bare-declaration → `['CC2-SIM']`; SIM/SIM → same; **real-roster/SIM-declaration → `['CC2']`** (the reverse direction, which the shipped test does not cover — it works); whitespace stripped; no-declaration → full roster; unknown/case-mismatched declaration → empty **with the loud log firing**. Two shapes defeat it, both below threshold today: a roster carrying `CC2` *and* `CC2-SIM` maps one declaration to two dispatchable seats, and a lowercase `-sim` suffix is not normalised — neither shape exists in any orchestrator roster.

**The two wired sites are correct.** Driven with a stub in place of `dispatch_to_model` across all 3 arms: the sweep reached exactly `{CC2}`, `{all 5}`, `{Codex, ChatGPT}` respectively — zero undeclared seats. `_apply_routing` builds its ladder from `_declared_models` (line 5202–5204) and hands it to `route()`. Arm B (declared == roster) is byte-identical to pre-repair behaviour, so nothing the archive measured on 5/6-seat runs is disturbed there.

**The exhaustive site sweep** (attack item 4): all `exp_config.models` reads classified — 772 (probe compose, filtered, no dispatch), 8362/8442/11373 (round loops + preflight, filtered by `cfg.models` — note: by **exact** match, an asymmetry with the helper's normalisation; consistency observation, below threshold since the config guard pins declared labels to the live roster), 11830 (identity map, no dispatch), 12028 (merge arbitration — dispatch-bearing, unfiltered, but flag off in all 3 arms and pinned by a test; a leak mitigated by a flippable flag is precisely how routing's leak survived until today), **13052 — the live one**. 7983 is the in-round re-ask on an already-filtered `mc`.

**The empty case** (attack item 2): returning empty is right *at this layer*. The typo case is caught pre-launch by `test_every_declared_seat_exists_in_the_orchestrator_roster`; refusing mid-run would kill a paid run over an epilogue mechanism; and the fail-soft path is loud. Routing with an empty roster yields UNTOOLABLE→HIL, which is the honest outcome.

**The re-aimed guards** (attack item 3) were re-aimed honestly — all 81 tests pass (`0.39s`). The ladder test now checks the caller's roster selection plus non-emptiness; the sweep test inverts its assertion while keeping the `assert reached` non-vacuity guard; the preflight test constructs its fixture and adds converse discrimination (strengthened). Two cosmetic notes: the sweep test's *name* now says the opposite of what it asserts, and the re-aimed ladder test calls `_declared_models` directly — the helper-not-wiring shape its sibling file's docstring condemns — but the new file's two wiring tests cover the gap.

**The fix** (repo is staged read-only, so supplied as a patch and executed in-memory):

```diff
-        verification_stats = _verification_step(
-            registry, round_idx, full_code, exp_config.models, cfg)
+        verification_stats = _verification_step(
+            registry, round_idx, full_code, _declared_models(exp_config, cfg), cfg)
```
and, same class, latent behind a flag:
```diff
-            "panel": list(exp_config.models),
+            "panel": _declared_models(exp_config, cfg),
```
Executed both sides: confined, the d11 arm skips A5 honestly (`"CC2 config not found"`, 0 dispatches, finding stays OPEN); arms declaring CC2 still get it (`reached=['CC2']`). `_verification_step` already normalises via `base_model_label`, so SIM rosters keep working. Add a wiring test in the 2026-09-09 file mirroring the sweep test's stub-and-count shape, plus the honest-skip converse.

## falsifier

Two scripts, both importing the real runner, both run (`python3 /tmp/falsifier_cc2v.py`, `python3 /tmp/falsifier_fix_and_edges.py`; full source in transcript). Decisive output:

```
declared: ['ChatGPT', 'Codex'] max_rounds: 8 verification_min_round: 6
roster: ['CC2', 'Codex', 'ChatGPT', 'Gemini', 'DeepSeek']
dispatched to: ['CC2']
FALSIFIED: _verification_step dispatched to undeclared seat(s): ['CC2']
and its CONFIRM resolves registry entries: CONFIRMED
```
and for the fix: `d11...: reached=[] undeclared=[] skipped_reason=CC2 config not found status=OPEN`. The sweep/helper/ladder falsifier passed every assertion (`ALL CHECKS DONE`).

## disagreement

The brief's rho framing is wrong for this runner. It calls rho "the cross-architecture correlation measured across seats." The runner's `_compute_rho` (line 2664) is **discovery efficiency** — novelty/raw per round, seat-count-agnostic, division guarded — not a seat-pair correlation. It cannot crash at 1 seat and carries no architecture signal to lose. Second, quieter objection: the brief says "2 sites were found" as settled fact and asks whether the repair is safe — but the ruling's premise ("only safe because the roster is filtered") was checkable against the whole dispatch surface before ruling, and wasn't; the enumeration stopped at the sites the old tests happened to name.

## model_use

- **S_k / severity**: confinement changes the ladder's input distribution exactly as measured: Arm A rungs = `[]` (every un-confirmed critical → HIL, absorption 0), Arm C = 1 rung of `max_rungs=2`, Arm B = `['Codex','CC2','ChatGPT','Gemini']` — unchanged. The 76.8% [65.6, 85.2] absorption figure is preserved where its topology is preserved (Arm B) and structurally reduced in A/C — that reduction **is the arm's premise**, not repair damage; the leaky alternative measured a 5-seat panel wearing a 1-seat costume. The CC2v leak was severity-material precisely because its CONFIRM enters the registry without a falsifier verdict, feeding S_k's input set from an undeclared seat.
- **gamma**: routing resolutions move findings between resolution states; they do not add to the new-finding series that gamma decays over, and `stall_gamma_terminate > 1.0` is pinned by test in all arms, so a previously-converging run still converges — the sweep runs strictly after the verdict by construction. Arm A's cost is a larger HIL queue, honestly reported.
- **rho**: valid as discovery efficiency in all arms; any diversity reading of it is void at 1 seat (self-novelty only) and condition-only in Arm C, whose two seats share `model_id` (pinned by `test_the_two_seats_share_weights`).

## What would refute me

(1) An upstream gate I missed that makes the `_verification_step` call unreachable in exp56 — I verified the call site is unconditional in the round loop and `min_round 6 < max_rounds 8`, but a launcher-level suppression would overturn finding 1. (2) A founder ruling that CC2v is a fixed cross-arm **instrument** (like `reverify_falsifier`), not a seat — then confinement should not apply and my fix is wrong; no config, design note, or docstring currently says so. (3) A committed measurement that exp56 arms terminate before round 6 in practice.

**Passes: 3** (read-and-classify; execute falsifiers; residual sweep — rho, remaining dispatch sites, guard re-run). A fourth pass produced nothing new above the material threshold.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_roster_fix_2026-09-09/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
