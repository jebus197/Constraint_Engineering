# Repair-loop panel — 2026-08-30

**The first brief in this project to ask reviewers for FIXES, not only findings.** The founder
identified on 2026-08-29 that all three previous dispatches asked only for problems; an audit
confirmed it — zero of three requested a repair.

Two questions: canaries re-pointed at churn rather than silence (the founder's own correction, that
an LLM going silent is not a signal that exists), and whether the fix-efficacy repair is the right one.

---

## fable — 15,371 chars, 1728 s

# Review report — canaries repointed at churn; the repair loop's real gap found and closed

**2026-08-30T01:29:09+01:00. Everything below marked MEASURED was executed in this worktree. Test totals: 4,349 passed pre-existing suite; 272 passed across every suite I touched, run serially; my changes add 13 new tests, all passing.**

---

## QUESTION 1 — Canaries and churn

### 1a. Is the distinction real and measurable? Yes — and the module's core already measures the right thing.

The founder's correction invalidates the module's stated *purpose*, not its *instrument*. `seed()`, `catches()` and `detection_rate()` measure detection capacity via the falsifier counterfactual — and detection capacity is exactly what separates the two states that produce identical gate evidence:

- **Exhausted-but-reading:** organic space empty, capacity intact → a fresh seeded defect gets killed, because there is now something new to find.
- **Churning:** recycling rather than reading → the fresh defect is missed.

Both states show flattened gamma, K zero-critical rounds, low rho. Only an externally-known fresh defect distinguishes them. That is mutation testing used exactly as designed; nothing in the scoring machinery assumed silence — only the docstring and the missing interpretation layer did.

**Two honest limits, both OPEN:** (1) sensitivity is unmeasured — a skimming panel might still catch a salient diff, so whether p_hat actually separates the states on real models needs one live probe experiment; (2) the probe costs one full panel round per run. I could not measure either without dispatching the paid panel, which is not mine to spend.

**One HARD constraint the previous brief missed** (classified HARD — it is the founder's frozen-article methodology): canaries must **never** be seeded into the live article or mid-run. That changes what gamma and rho measure and destroys round comparability. The probe must run **out of band, once, when the two-sided gate first holds**, against a history-free copy — which `seed()` already enforces by refusing tracked trees.

### 1b. What changed — MEASURED, code in the worktree, tests green

`bench/canary_seeding.py`, three changes:

1. **Docstring premise rewritten** (lines 1–28). The "panel went quiet" framing is replaced by the churn question, citing the founder's correction. Stale docs are defects; this one was the module's charter.
2. **New contributory layer** — `churn_probe_contribution(p_hat_by_model, threshold=0.5)` at the end of the module. Three string signals, deliberately not booleans: `DETECTION_INTACT` (all models ≥ threshold — corroborates the gate), `DETECTION_DEGRADED` (any model below — convergence **stands**, flag travels to HIL), `PROBE_NOT_RUN` (absent measurement ≠ degraded, the ERROR/REFUTED distinction again). Per-model, not pooled — one dead reviewer must not hide inside a healthy mean.
3. **Probe protocol documented** in the docstring: seed an off-tree copy at provisional convergence, score kills via `catches()` with a falsifier-counterfactual verifier, exclude the probe round from gamma/rho/registry, append the reason line beside the rho line in the verdict.

**How it combines with rho and the gate:** the returned record has no pass/fail field, no `failures` key, nothing a gate can block on — structurally incapable of vetoing. It is one sentence for the convergence reason string, the same shape as `churn_signal` in `_evaluate_gate_conditions` (`reference_runner_v2.py:4690`) after commit `aff3ab7`. Gate + rho-churn + `DETECTION_INTACT` = the strongest convergence statement this system can make: quiescent, AND proven still capable. Gate + `DETECTION_DEGRADED` = converged, flagged for a human. `bench/tests/test_canary_churn_repoint_2026-08-30.py` (7 tests) pins all of this, including a test asserting no record ever carries a blockable field. I did **not** wire the reason-string into `_evaluate_gate_conditions` — until the probe round exists, it would print `PROBE_NOT_RUN` on every verdict. Wire it with the probe, not before.

**Confidence: high** the mechanism is correctly repointed and correctly contributory. **Falsified by:** a live probe where a panel later shown to be churning (rho low, then fresh criticals found by a replacement panel) still kills ≥ threshold canaries — that would show the probe lacks sensitivity, and then 1c's answer flips.

### 1c. Retire it? No — but with a named exit condition.

rho measures novelty of *output*; the canary measures capacity of *detection*. They are different axes, and the canary is the only external ground-truth instrument this project has for the second. The real cost is not code — it is the exp48 lesson the module itself records: **seeding created the motive** for the one excluded run. The probe design keeps the catalogue off-machine and the probe round out of the registry, but the surface exists. My recommendation: keep, wire the probe round, and measure sensitivity in one Bench Run 2 experiment. If sensitivity is poor there, retire it then, with data — not now, without.

---

## QUESTION 2 — The repair loop

### 2a. Attack on CC1's proposal — three hits, one of them large

**Hit 1 — the mechanism named as precedent does not do what the brief says.** `scripts/adjudicate_by_repair.py` does **not** use a scratch copy. `_direction` (line 217) writes the patched text **to the live target** and restores in `finally`. In flight that trips the runner's target-integrity hash every round, and a kill between write and restore corrupts the frozen article permanently. So "adjudicate_by_repair already does exactly this" is false in the detail that matters most.

**Hit 2 — a plain scratch copy is invisible to most falsifiers.** `bench/fix_efficacy.py` records the measurement: 57 of 70 exp44 falsifiers reach their target by **import**, which resolves to the original module, not the copy — every probe would report "ineffective", wrongly, in the confident direction. (Archive claim, read not re-derived — but my own test empirically shows the correct alternative working on an import-based falsifier.) The correct scratch mechanism already exists: the discrimination overlay (`_build_discrimination_overlay`, `reference_runner_v2.py:2804`) — a symlink-mirrored throwaway repo root differing in one file, with a tripwire that *measures* interception instead of trusting it.

**Hit 3 — the largest: the counterfactual already runs in flight, and it misattributes its own result.** Since 2026-08-22, `_derive_corrected_copy_from_fix` (`reference_runner_v2.py:3360`) feeds the discrimination control a copy built from the finding's **own proposed fix**, on the assumption — written into the code — that "a finding's own proposed fix corrects THIS claim by construction." Commit `adb566b` measured that assumption false: **126 of 246 archived fixes do not silence their own falsifier**. When the fix is the broken half, the control sees "still fires", stamps `NO_DISCRIMINATION`, marks the falsifier a **MECHANICAL FAULT**, escalates, and (with `discrimination_control_blocks`) un-confirms a demonstrated finding.

**MEASURED, not asserted:** `bench/tests/test_fix_ineffective_attribution_2026-08-30.py` builds a falsifier proven discriminating (goes quiet on a true correction — `DISC_PASSED`) plus a fix that applies cleanly and changes only a comment. Pre-repair, the live path logged: `★ MECHANICAL FAULT C0001: falsifier fires on a CORRECTED copy — NOT closed, escalated to human` — three false statements about a sound instrument attached to a real defect. So the brief's premise "`FIX_INEFFECTIVE` is invisible live" is wrong for post-08-22 runs: it is **visible and mislabeled as an instrument fault**, which is worse.

**The remaining attack questions, answered with evidence:**
- *Cost per round:* zero new sandbox executions — the control already runs and caches on (falsifier, copy, target) hashes; my change is attribution. Worst case per fresh probe is ~5 sandbox runs ≤ 30 s each, the cost the 2026-08-22 wiring already carries. The close guard *saves* bugzilla's 4 tool runs on unproven fixes.
- *Fix touching a non-target file:* `_fix_block_targets` (line 3345) filters blocks to the reviewed target; no matching block → derivation declines, reason recorded, no probe. Covered by existing decline tests.
- *Conflicting fixes in one round:* probes are per-finding, sequential, each spliced from the pristine target onto its own overlay. No shared state; conflicts cannot interact — and independent measurement against the frozen article is the correct semantics.
- *Static-article violation:* none. The overlay never writes the tracked tree; the integrity hash never sees a change.

### 2b. The proposal did not survive as written — here is what I built instead (MEASURED, all tests green)

Five edits to `bench/reference_runner_v2.py`, one supersession in tests:

1. **`DISC_FIX_UNPROVEN = "FIX_DOES_NOT_SILENCE"`** — new outcome beside `DISC_FAILED` (~line 2777), with the measured justification in the comment.
2. **Attribution in `run_discrimination_control`**: `corrected_verdict == CONFIRMED` on a copy whose `corrected_copy_source == "proposed_fix"` → `DISC_FIX_UNPROVEN` with the honest disjunction ("either the fix is incomplete or the falsifier does not test what the finding claims — a fix-derived copy cannot separate the two"). The ask path — a model-authored corrected passage — keeps full `DISC_FAILED` instrument-fault semantics, pinned by a test.
3. **New branch in `_apply_discrimination_control`**: sets `fix_unproven`, logs — **no** un-confirm, **no** mechanical-fault stamp, **no** escalation. Contributory, the rho ruling's shape.
4. **Verified-hold at the falsifier gate** (~line 3900): the claim resolves CONFIRMED, but `verified` stays False on `DISC_FIX_UNPROVEN` — because `_update_finding_statuses` transitions CONFIRMED+verified → CLOSED with the evidence string "verified fix", and no fix was verified. **This is the closed loop:** a stronger fix next round changes `corrected_sha`, the cache misses, the control re-runs, `DISC_PASSED` reopens the verified path.
5. **Feedback line in `_rejection_lines`** (~line 8894), delivered by the channel that already runs: *"YOUR FIX DOES NOT CURE YOUR OWN FALSIFIER: applying it to a copy of the target and re-running your test leaves the test still demonstrating the defect. Either the fix is incomplete or the test does not test what the finding claims. The finding stays CONFIRMED and will NOT close on this fix. Send a stronger fix, or a falsifier that goes quiet when the claim is fixed, with a CORRECTED_COPY so the control can tell the two apart."* The CORRECTED_COPY request is load-bearing — an ask-path copy is what resolves the disjunction.
6. **Close guard `_fix_unproven_blocks_close`** on the bugzilla condition (~line 2600): lint evidence cannot close a fix the counterfactual has measured not to cure.

**Three things needing founder ratification, stated plainly:** (a) this supersedes the 2026-08-22 "corrects by construction" assumption — three tests in `test_corrected_copy_from_proposed_fix.py` were updated to the new semantics with the supersession named in their docstrings; (b) the residual ambiguity now fails the other way: broken-instrument-plus-good-fix reads as unproven fix rather than being routed for falsifier replacement — I judge that safer (the old direction un-confirmed demonstrated criticals and minted false faults at a ~50% measured base rate; the new direction withholds closure and asks for the copy that decides), but it is a direction choice, not a theorem; (c) `bench/fix_efficacy.py` — built earlier today, which CC1's own note does not mention — is the standalone instrument for this same question and was left unwired pending exactly this ruling. My wiring and that module coexist without conflict; if ratified, the natural consolidation is for the fix-derived branch to delegate to `fix_efficacy.probe`.

**Confidence: high** for correctness of the wiring (272 targeted tests serial-green, full suite green minus pre-existing failures below). **Falsified by:** an archived finding where the falsifier was independently shown non-discriminating (e.g. the access-not-dependence class), its fix independently shown effective, and my branch keeps the false claim CONFIRMED without ever obtaining an ask-path copy — that case would prove the un-routed residual bites in practice.

### 2c. Final-round falsifier errors — measured, and mostly not worth a new mechanism

MEASURED across all 30 archived reports: unresolved ERROR/UNTOOLABLE findings at run end are **0–2 on every healthy recent run** (exp44: 0, exp45: 0, exp46: 0, exp47: 2, exp48: 0, exp49: 0). The large counts are exp42 (15 — the parse-era run) and the two exp55 round-0 halts (8 each) caused by the relative-path defect already fixed on 2026-08-23; a final-round repair would have fixed none of them. Additionally, the routing ladder (`_apply_routing`, line 4222) already routes ERROR/UNTOOLABLE falsifiers to stronger writers **within the same round, including the final one** — though note `routing_enabled` defaults False and was unset in the exp44–47 configs, so it did not run there.

**Recommendation: do not build a repair epilogue now.** The measured population is ≤2 per healthy run, those findings fail toward the human (correct direction), and extending `_inround_reask` would break its single-purpose contract ("reformat, no new analysis"). The cheap correct move if Bench Run 2 shows a higher residue: enable `routing_enabled`, which is the final-round repair mechanism that already exists. If an author-repair pass is ever wanted, bound it as: fires only on non-converged termination, one pass ever, only falsifier-rewrites for named finding ids accepted, all other content logged and discarded — that shape cannot extend a run indefinitely. Deferral here is scope-honest, not evasion: the evidence says the mechanism would idle.

---

## What I could not check, and why

- **Canary probe sensitivity on real models** — requires paid panel dispatch; not mine to spend. This is the single biggest OPEN item in Q1.
- **57/70 import-based falsifiers, 954/1503 derivable fixes, 126/246 ineffective** — archive measurements from today's commits, read not re-derived; their test suites pass in this worktree, and my own end-to-end test independently exercises the overlay redirection they rely on.
- **Three pre-existing test failures on the pristine tree**, none mine: the Desktop-mirror drift guard, the run-ledger-vs-logs check, and the key-guard archive sweep — all environment/archive-state assertions that this disposable worktree cannot satisfy. Verify on the canonical checkout.
- **One flaky interaction I caused and diagnosed:** running two full suites concurrently makes `test_the_probe_leaves_no_overlay_behind` see the other process's temp-dir overlays. Serial runs are clean. Not a product defect.

**Where I disagree with the brief:** the counterfactual probe was not missing from the live loop — it has been running since 2026-08-22 with its result mislabeled as an instrument fault, and the brief's own note (corrected once already) still frames the gap as absence rather than misattribution. The run that proves it is `test_fix_ineffective_attribution_2026-08-30.py`, whose pre-repair log line reads `★ MECHANICAL FAULT` against a falsifier the same file proves sound.

---

## cc2 — DID NOT RETURN

Hit the 2400 s dispatch timeout and was still retrying when this record was written.

---

## Brief

```
# Closing the repair loop — and adapting canaries to what is actually detectable

**READ THIS FIRST — this brief asks for FIXES, not just findings.**

The three dispatches before this one asked you to find problems, refute claims and return verdicts. None
asked for a repair. The founder identified that on 2026-08-29 and was right: *"The purpose of these multi
model reviews is not just to find problems (although that is clearly 50% of it), but also to suggest fixes.
But you have a bad habit of simply telling our models during these reviews 'find problems with this code'
and not telling them to come up with fixes."*

So for **every** finding below, return: the finding, **a concrete fix** (file, function, the actual change),
and **your confidence in that fix** with what would falsify it. A finding without a proposed repair is half
an answer here.

Two independent questions. Answer both.

---

## QUESTION 1 — Canaries must detect churn, not silence

The founder has corrected the premise the previous canary brief was built on, and the correction is
load-bearing:

> *"you cannot look for a signal of 'silence' from an LLM. That is impossible. If things are done this way,
> then the risk is you will end up looking for a signal you can never detect... The only condition (ever) in
> the entire history of this project where a model, a round, or an experiment has produced no output has been
> the result of broken machinery, a misconfigured experiment, or one of the parsing issues we have
> encountered. The purpose of rho and our other machinery is to detect when models have stopped producing
> new useful and/or novel output and may have entered the territory of 'churn', which in itself should be a
> contributing measure when deciding if a problem space has been usefully exhausted."*

The previous brief framed canary seeding as distinguishing *"the panel went quiet because the document is
clean"* from *"the panel went quiet because the panel stopped looking"*. **Both halves of that are the wrong
signal.** An LLM does not go quiet. It keeps producing. The real failure mode is **churn** — continued
volume with no new content.

`bench/canary_seeding.py` (built 2026-08-28, 42 tests, read it in full) is therefore currently pointed at a
condition that does not occur.

**1a.** Can the mechanism be re-pointed at churn? Concretely: a panel that is genuinely exhausted should
still **kill a freshly seeded canary**, because detection capacity is intact even when there is nothing left
to find. A panel that is churning should **miss it**, because it is recycling rather than reading. Is that
distinction real, and is it measurable with what this module already does?

**1b.** If yes — what exactly changes in `canary_seeding.py`? Give the code. Note that `rho` was changed
TODAY (commit `aff3ab7`) from a convergence **veto** to a **contributory** signal, per founder ruling. How
should a canary result combine with rho and with the two-sided gate? It must **contribute**, never veto —
that is a standing ruling, not a preference.

**1c.** If the answer is that canary seeding cannot be adapted and should be retired as an idea, say so
plainly and say why. The founder asked directly: *"Is it useful or not? Can it be fixed? Should it be? Or
should it be retired as an idea?"* A clean "retire it" is a perfectly acceptable answer and costs nothing to
give.

---

## QUESTION 2 — The repair loop closes for broken falsifiers but not for ineffective fixes

Read `experimental_notes/Why_The_Machinery_Was_Not_Clearing_The_Pile_2026-08-30.md` first — it is short and
carries the evidence for everything below.

Established, and not in dispute:

* The feedback channel is **built and enabled by default**. It already tells a model *"FALSIFIER ERROR: your
  test did not run to a verdict... Re-write it so it runs."*
* A fix is **never applied and its own falsifier re-run in flight**, because the test article is frozen by
  founder-directed methodology (`bench/launch_exp41.py:6`, `apply_fixes_back_enabled=false`).
* Consequently `FIX_INEFFECTIVE` — a fix that does not cure the defect it claims to cure — is invisible
  live. **16 of the 48 undecided similarity pairs are exactly this.**

**2a.** CC1's proposal: run the counterfactual on a **scratch copy** — apply the fix, re-run that finding's
own falsifier, discard the copy — leaving the frozen article byte-identical, and emit one more feedback line.
`scripts/adjudicate_by_repair.py` already does exactly this post-hoc with a `try/finally` restore. **Attack
this proposal.** Does it violate the static-article methodology in some way CC1 has not seen? What does it
cost per round? What happens when a fix touches a file that is not the target? When two findings propose
conflicting fixes in the same round?

**2b.** If the proposal survives, **write it** — the function, where it hooks in, what the feedback line
says, and the test that would commission it. If it does not survive, give the alternative that does.

**2c.** A second gap: `_inround_reask` fires on **one** condition, unparseable output, and its prompt says
*"Do not add new analysis; reformat what you already produced."* Everything else waits for the next round —
so a finding whose falsifier errors in the **final** round never gets a repair opportunity. Is that worth
closing, and if so how, without letting a run extend itself indefinitely to chase repairs?

---

## Rules

- Run things. Every verdict must be something you executed, not something you read.
- You are in a throwaway git worktree. Nothing you write escapes. Do not push.
- **Disagreement is information.** Do not converge toward the other reviewer or toward CC1. Where you think
  CC1 is wrong, say so and show the run that proves it — that has been the most valuable output of every
  dispatch so far.
- Report what you could not check, and why. That section is not optional.
- The founder is not a developer and reads these. Name files and functions precisely; do not assume context.

```