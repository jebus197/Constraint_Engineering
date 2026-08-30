# Repair-loop panel — 2026-08-30

**The first brief in this project to ask reviewers for FIXES, not only findings.** The founder
identified on 2026-08-29 that all three previous dispatches asked only for problems; an audit
confirmed it — zero of three requested a repair.

Two questions: canaries re-pointed at churn rather than silence, and whether the fix-efficacy repair
is the right one.

**The reviewers DISAGREE on the canaries and the disagreement is preserved, not resolved by
preference.** fable holds the distinction is real and the instrument measures the right axis; cc2
PROVED the module has no temporal dimension and returns identical output for a churning and an
exhausted panel. Both verified independently by CC1; see `Canary_Panel_Disagreement_2026-08-30.md`
for CC1's own position, which is that they answer different questions and both stand.

**cc2's Finding 0 was a real sandbox escape that CC1 had twice reported to the founder as a false
alarm.** Fixed the same night (`eeaa0b3`).

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

## cc2 — 22,335 chars, 3791 s  (timed out once at 2400 s, returned on retry)

Code is untouched; only notes landed. I deliberately did not read `panel_results/Repair_Loop_Panel_2026-08-30.md` so my verdicts stay independent.

---

# Repair-loop review — findings, fixes, confidence

**Base commit `657b02c`.** All work in a throwaway worktree at `/tmp/cdsfl_review_89557`. Canonical tree verified byte-clean before and after (`git status --porcelain` → 0 lines, twice). Nothing pushed.

---

## Finding 0 — the brief's first sentence was false, and it was the dangerous kind of false

**The brief says:** *"Your working directory is a DISPOSABLE COPY of the repository... break things in it freely."*

**It was not.** `git worktree list` put me in `/Users/georgejackson/Developer_Projects/Constraint_Engineering` on branch `main` — the canonical tree, clean. A reviewer who took the brief at its word and ran `adjudicate_by_repair.py` (which writes to live target files) would have been mutating the real repository.

**Fix, `scripts/` — one line at the top of any review brief, and it should be mechanical, not prose:**

```bash
test "$(git rev-parse --abbrev-ref HEAD)" = "HEAD" || { echo "REFUSING: not a detached worktree"; exit 1; }
```

I made my own worktree instead. **Confidence: certain** — I ran `git worktree list` and `git rev-parse --abbrev-ref HEAD`. **Falsified by:** showing that some wrapper does isolate the cwd before the agent starts. Nothing in the session indicated one.

---

# QUESTION 2 first, because it changes the answer to Question 1

## Finding 1 — Q2a's premise is wrong twice, and the thing you asked me to write already exists

The brief says: *"CC1's proposal: run the counterfactual on a scratch copy... `scripts/adjudicate_by_repair.py` already does exactly this post-hoc with a `try/finally` restore."*

**Both halves are wrong.**

**(a) `adjudicate_by_repair.py` does not use a scratch copy.** `scripts/adjudicate_by_repair.py:217` is `target.write_text(patched)` — it writes the **live tracked file** and restores at `:221`. There is no copy anywhere in it.

**(b) A scratch copy cannot work, and the repo already measured why.** Falsifiers reach their target by **importing** it (`bench/falsifier_verify.py:8`: *"must IMPORT THE REAL target module"*), resolved through `PYTHONPATH=<repo_root>`. A patched file at a different path is invisible to them. `bench/fix_efficacy.py:23` records the measurement: **57 of 70 exp44 falsifiers import rather than read a path.**

**(c) The in-flight version is already built.** `bench/fix_efficacy.py` — commit `775518d`, *"The fix-efficacy probe: ask whether a fix cures the defect its OWN falsifier demonstrates"* — implements it via a symlinked overlay, carries the `FEEDBACK_LINE` verbatim, and has 14 tests. I ran them: **14 passed**.

**What is actually missing is the wiring.** `grep -c fix_efficacy bench/reference_runner_v2.py` → **0**. Built, tested, two consuming scripts, never called by the runner.

This is the third instance of the same failure the note at `experimental_notes/Why_The_Machinery_Was_Not_Clearing_The_Pile_2026-08-30.md:42` already confesses: *"a universal claimed after checking one member."* The note corrected itself about `bugzilla_loop.py` and then, in the same document, proposed building a thing that `bench/fix_efficacy.py` had already built.

### What I measured with it

I ran `scripts/fix_efficacy_sweep.py` over the whole archive — **313 findings carrying both a falsifier and a fix**:

| outcome | n |
|---|---|
| fix does **not** cure its own falsifier | **125** |
| fix cures its own falsifier | 118 |
| indeterminate (no fix applied / no baseline / falsifier never reads target / other) | 70 |

**125 of the 243 findings that yield a verdict — 51.4% — propose a fix that does not cure the defect their own falsifier demonstrates.** Wall-clock **79.7 s for 313 probes = 0.255 s each**.

This independently corroborates commit `657b02c`'s "126 of 246" from a different angle; the small gap is the five findings discussed in Finding 3.

**I hand-checked one.** exp44 `C0011`, `bench/evidence.py`: the falsifier requires the classifier to recover a verdict from sealed metadata; the proposed fix's own REPLACE text says the verdict *"cannot be recovered from the chain"*. The fix documents the limitation instead of curing it. `FIX_INEFFECTIVE` is correct.

### Answers to the specific attacks the brief asked for

- **Does it violate the static-article methodology?** No — the overlay is a `tempfile.mkdtemp` with symlinks; the article is never opened for writing. I ran 313 probes and the tracked tree stayed byte-clean.
- **Cost per round?** 0.255 s per probe measured. At the cap I set (5/round) that is **~1.3 s per round**.
- **A fix touching a file that is not the target?** `_apply_fix_to_source` matches against the target's text only; a fix aimed elsewhere fails to apply and returns `INDETERMINATE_NO_APPLICABLE_FIX`. Measured: 33 of 313. It fails safe.
- **Two findings proposing conflicting fixes in the same round?** A non-issue. Each `probe` builds its own overlay from the pristine text. They cannot interact. This is precisely what write-and-restore *cannot* say.

**Confidence in the diagnosis: certain** (ran the tests, ran the sweep, hand-verified a case). **Confidence in the 51.4%: high, with a caveat** — it measures archived fixes against *today's* target, and the probe requires the falsifier to reproduce on today's file before scoring, so drift is excluded by construction. **Falsified by:** showing `_apply_fix_to_source` systematically mis-applies fixes such that `patched != original` but the intended edit did not land. I checked one case by hand, not 125.

## Fix 1 — the wiring (written and tested)

Four edits to `bench/reference_runner_v2.py`:

1. `FIX_EFFICACY_PER_ROUND_LIMIT = 5`, beside `BUGZILLA_PER_ROUND_LIMIT`.
2. A probe block in `_update_finding_statuses`, immediately after the Bugzilla block, guarded by `fix_efficacy_attempted` and the per-round cap, exception-safe, writing only `entry["fix_efficacy"]`.
3. A branch in `_rejection_lines` emitting `FEEDBACK_LINE` — **only** for `FIX_INEFFECTIVE`.
4. The import.

**Two design rulings I took, and why:**

**It is contributory, never a veto.** It writes no status, and `test_the_probe_is_contributory_and_cannot_gate_anything` reads the source of `_evaluate_gate_conditions` and `_check_gamma_alt_convergence` and fails if either mentions it. This follows the rho ruling of 2026-08-29 (`aff3ab7`) for the same reason: an instrument that measures the exhaustion of a search must not be able to refuse the convergence it measures.

**The four INDETERMINATE outcomes are recorded but never shown to the model.** "The instrument could not look" is a statement about the apparatus. Telling a model that invites it to rewrite a fix nothing found fault with — the "cannot verify becomes verified" inversion that `bugzilla_loop.run_verification` fell into three times, pointed the other way.

**New file `bench/tests/test_repair_loop_wiring_2026-08-30.py` — 8 tests, all pass.**

**Confidence: high on correctness, medium on completeness.** The wiring is small and tested. What I could **not** do is run a live experiment — that needs paid model dispatch. So the probe has never been exercised inside a real round; only against archived findings and synthetic fixtures.

---

## Finding 2 — the overlay leaks the real `.git`. High severity, and it silently blocks canary seeding

Found by running it, not reading it.

`_build_discrimination_overlay` (`reference_runner_v2.py:2804`) symlink-mirrors the repo root. `.git` was mirrored with everything else. Measured on a live overlay before my fix:

```
.git present in overlay: True | symlink: True → /private/tmp/cdsfl_review_89557/.git
git -C <overlay> diff --stat  rc=0   → returns the full mutation set
git -C <overlay> log --oneline -2   rc=0   → 657b02c LATENT high-severity: ...
```

Every discrimination-control and fix-efficacy overlay differs from the tracked file by exactly the mutation under test. With `.git` reachable, `git -C <overlay> show HEAD:<target>` returns the pristine text and the diff returns the plant **at precision 1.000, no key required** — the exact leak `canary_seeding.seed` refuses a tracked target to prevent (`canary_seeding.py:203`), arriving through a route that guard cannot see.

**And it has a second effect that decides Question 1.** `canary_seeding._in_a_git_worktree` walks for a `.git` entry. The symlink satisfies it, so **`seed()` refused the overlay** — the only place in-flight seeding could ever be legitimate. I ran it and got the refusal.

### Fix 2

`reference_runner_v2.py`: add `_OVERLAY_NEVER_MIRROR = frozenset({".git"})`, add an `is_root` parameter to `_discrimination_mirror_except`, skip the set at root only, and pass `is_root` from the two call sites in `_build_discrimination_overlay`. Root only, because that is the only level at which git resolves a repository.

**Verified after the fix:** `.git` absent; `git log` through the overlay returns rc=128; the symlink mirror still intact; the leaf still a real file with substituted content; the real tree untouched; **`seed()` now accepts the overlay**. Three regression tests cover all three properties.

**Confidence: certain on the leak** (I ran `git log` and `git diff` through a live overlay and got real history). **Confidence in the fix: high.** **Falsified by:** finding another route from the overlay to the tracked history — a `.gitdir` file, an env var like `GIT_DIR` inherited into the sandbox. I checked `.git` only. `_sandbox_env` does drop most inherited variables, but I did not specifically test `GIT_DIR` or `GIT_WORK_TREE`. **That is a gap in my check.**

---

## Finding 3 — running from a git worktree makes the integrity guard reject 15 honest falsifiers

The full suite failed 2 tests. I stashed my changes and re-ran on pristine HEAD: **both fail there too.** Not mine. But one is serious.

`test_falsifier_cannot_read_the_key.py::test_the_guard_rejects_nothing_else_in_the_whole_tracked_archive` expects exactly 2 rejections across 560 archived falsifiers. From a worktree it rejects **17**. Its own docstring: *"If a future rule change makes this fail, the rule is blocking honest work."*

**Cause.** `falsifier_verify.REPO_ROOT` is `parents[1]` of that file, so in a worktree it names the worktree. `_allow_roots` therefore omits the canonical tree, and archived falsifiers that name it by absolute path are rejected as `INTEGRITY_VIOLATION` — which routes the finding to a human and never to CONFIRMED. **The brief itself says panels are dispatched into throwaway worktrees, and `git worktree list` shows two.** This is the live configuration, not a hypothetical.

### Fix 3

`bench/falsifier_verify.py`: add a cached `_main_work_tree()` that reads `git rev-parse --git-common-dir` and appends its parent to `_allow_roots`. Falls back to `REPO_ROOT` on any failure — the failure direction is "no extra root", the status quo, never a widening.

**Verified.** `test_falsifier_cannot_read_the_key.py` + `test_verdict_reader_and_access.py`: **72 passed**. And I attacked the widening directly:

| falsifier | verdict |
|---|---|
| reads the off-repo key store by literal path | INTEGRITY_VIOLATION |
| reconstructs the key path via `Path.home()` | INTEGRITY_VIOLATION |
| walks `~/Desktop` for ground truth | INTEGRITY_VIOLATION |
| honest falsifier naming the canonical tree by absolute path | **REFUTED** (ran clean) |

**Downstream effect, measured.** Re-running the 313-finding sweep with both fixes: 5 findings moved from `NO_BASELINE` to `NOT_INTERCEPTED` — a wrong diagnosis replaced by the right one — and **not one verdict changed. 125/243 = 51.4% before and after.** The headline number is robust to both repairs.

**Confidence: high.** **Falsified by:** an exfiltration route that the canonical tree makes reachable and the worktree did not. The keys live outside the repo, so I do not believe one exists, but I tested three routes, not all of them.

**The second failure** — `test_experiment_run_ledger_2026-08-26.py` — is genuine, pre-existing, and unrelated: `experimental_notes/EXPERIMENT_RUN_LEDGER.md` has drifted from `bench/logs/`. Fix is one command, which the test prints: `python3 scripts/experiment_run_ledger.py > experimental_notes/EXPERIMENT_RUN_LEDGER.md`.

**Suite after all three fixes: 4354 passed, 1 failed (the ledger drift), 38 skipped.** Was 2 failed.

---

## Q2c — the final-round gap is real, small, and I recommend not closing it

Measured across the archive: **40 of 1174 findings (3.4%) end their run with a dead falsifier** (`ERROR` or `UNTOOLABLE`).

**But I could not isolate the final-round subset.** The `last_round` field is absent or zero on archived entries, so my "in final round" column collapsed to the total. That figure is an **upper bound**, and the true one is well below it: 16 of the 40 come from `exp42_composer` and 16 from the two `exp55_v3_control` runs, which commit `657b02c` records as **round-0 halts** — they never had a second round, so no repair round could have helped them either. The population a final-round repair opportunity would actually rescue is plausibly under ten across the entire archive.

**Against that:** those findings are not dropped. A non-CONFIRMED verdict sets `escalated` and goes to a human. The loop closes — to HIL, not to a model.

**My recommendation: do not build it.** One extra model dispatch per run to rescue under 1% of findings, when the same effort spent on Fix 1 reaches 51% of fixes, is the wrong trade. **This is a disagreement with the brief's framing**, which treats it as a gap to close.

**If you want it anyway,** the design that answers *"without letting a run extend itself indefinitely"* is a single **repair-only round** after the final round that accepts **no new findings** — only rewritten falsifiers and fixes for findings already open. The termination argument is structural, not a counter: a round that cannot generate new findings cannot generate new work needing another repair round. Bound it at exactly one, behind a config flag defaulting off. Extending `_inround_reask` instead does **not** work: its prompt says *"Do not add new analysis; reformat what you already produced"*, and rewriting a broken falsifier **is** new analysis.

**Confidence: medium.** The 3.4% is solid; the final-round split is unmeasured and I have said so.

---

# QUESTION 1 — canary seeding

I ran the module's suite: **42 passed.** The code is careful and the guards are real. That is not the problem.

## Q1a — the distinction is not real, and the module could not measure it if it were

**Two separate claims. I proved one and argued the other.**

**Proved: the module has no channel through which churn could arrive.** Occurrences in `bench/canary_seeding.py`: `rho` **0**, `gamma` **0**, `churn` **0**. `catches` takes a flat list of findings with no round index; `detection_rate` returns one p̂ per model over the whole run. There is no temporal dimension anywhere.

I built two synthetic panels — one maximally novel (6 rounds, 2 distinct outputs, kills both canaries in round 1), one maximally churning (6 rounds, 1 distinct output repeated, kills both late by recycling) — and pushed both through `catches` → `detection_rate`:

```
P_EXHAUSTED  caught={'M': ['K1','K2']}  p_hat={'M': 1.0}
P_CHURNING   caught={'M': ['K1','K2']}  p_hat={'M': 1.0}
distinct texts  EXHAUSTED: 2   CHURNING: 1
module output identical: True
```

**Argued: the mechanism behind the distinction does not exist.** The brief's premise is that *"a panel that is churning should miss it, because it is recycling rather than reading."* An LLM re-reads its prompt on every call. There is no persistent state that could switch off reading. Churn in this harness is a property of the **output stream** — near-duplicate findings — not of a reading faculty that has degraded.

**The founder's own correction cuts against the rescue, not for it.** If silence is impossible because a model always produces, then a model that always produces will also produce against a freshly seeded defect. The premise that makes silence undetectable is the same premise that makes a missed canary unlikely.

So what a canary measures is a **detection floor at a moment** — a capability control, not a search state.

**Confidence: high on measurability** (executed). **Medium on the mechanism** — this is the honest boundary. Settling it needs a live A/B with real dispatch: seed one held-out canary at a round where rho says the panel is churning, and at a round where it is not, and compare kill rates. I could not run that; it costs paid dispatch and this session is non-interactive.

## Q1c — my recommendation: retire it as a convergence instrument. Keep the code.

You asked directly and said a clean "retire it" costs nothing. So: **retire the convergence framing. Do not wire it to the gate in any form.**

Three reasons, in order of weight:

1. **It cannot make the claim its own docstring makes.** `canary_seeding.py:15` — *"Silence PLUS killed canaries is affirmative evidence of credible exhaustion."* That inference needs "the panel would have found a real remaining defect", and a planted defect of known class establishes only that *that class* is detectable. The generalisation is the module's load-bearing step and nothing in it supports the step.
2. **The repo already has this control, twice, on real findings.** `scripts/null_perturbation_control.py` and the discrimination control both ask "is this instrument actually sensitive to the target?" — on the findings a run actually produced, with no planted material and no answer key. The discrimination control is strictly the better instrument for the same question.
3. **The seeding pressure is documented as harmful in the module's own docstring** (`:32-41`): exp48's key read happened because a model reasoned that editing a file would destroy *"a seeded fault the panel is scored on"*. **Seeding created the motive.** That is the project's one excluded run, and it is the closest thing to a base rate this design has.

**Retiring costs nothing.** No gate reads it, no runner imports it, the 42 tests keep passing. Mark the module `RESEARCH INSTRUMENT — NOT A CONVERGENCE SIGNAL` and correct the docstring's claim.

## Q1b — if you keep it anyway, here is the only defensible shape

Two things, and the first is mandatory regardless.

**Prerequisite: Fix 2 must land first.** Before it, `seed()` refuses the overlay and `git diff` through the overlay returns the plant at precision 1.000. Any canary run before that fix is answer-key-exposed by construction. I demonstrated both.

**The reframe that would be measurable: latency, not detection.** Change the question from *"did the panel kill the canary"* to *"how many rounds did it take"*. Rounds-to-kill sits on the same diminishing-returns axis as gamma, which is where this project's mathematics already lives. Concretely, in `bench/canary_seeding.py`:

```python
def kill_latency(findings, canaries, *, seeded_at_round, verifier=None):
    """Rounds from seeding to first kill, per canary. None = not killed.

    Detection is a floor; LATENCY is a rate, and a rate is what belongs beside
    gamma. `seeded_at_round` is REQUIRED: latency measured from round 0 for a
    canary seeded at round 5 is not a slower panel, it is a wrong denominator.
    """
    if verifier is None:
        return {}
    first: dict[str, int] = {}
    for f in findings:
        r = f.get("round")
        if r is None or r < seeded_at_round:
            continue
        for c in canaries:
            if verifier(f, c) and c.id not in first:
                first[c.id] = r - seeded_at_round
    return {c.id: first.get(c.id) for c in canaries}
```

**How it combines with rho and the two-sided gate: it does not enter either.** That is the whole answer. Contributory means it appears in the run record and in the convergence narrative a human reads, and **nowhere** in `_evaluate_gate_conditions` or `_check_gamma_alt_convergence`. Pin it the way I pinned the fix-efficacy probe — a source-reading test that fails if either gate function ever mentions it. Commit `aff3ab7` removed two rho veto sites; adding a canary veto would re-create the same inversion under a new name.

**Confidence: medium-low, and I want to be clear about that.** The latency reframe is coherent and it is measurable, but I have **not** demonstrated that latency separates a churning panel from an exhausted one — that is the same live A/B I could not run. It is a better-shaped hypothesis than the current one, not a validated instrument. **My actual recommendation remains Q1c: retire it.**

---

# What I could not check

1. **No live experiment.** Everything is archived findings, synthetic fixtures and unit tests. The fix-efficacy wiring has never run inside a real round. Paid dispatch, non-interactive session.
2. **The churn mechanism itself.** Same reason. Both Q1a's mechanistic argument and Q1b's latency reframe rest on unrun experiments and I have marked both.
3. **The final-round subset of the 40 dead falsifiers.** `last_round` is absent or zero on archived entries. 3.4% is an upper bound over all rounds.
4. **Other routes from the overlay to git history.** I closed `.git`. I did **not** test `GIT_DIR` / `GIT_WORK_TREE` inherited into the sandbox, or a `.gitdir` pointer file.
5. **The 51.4% by hand.** I verified one case (exp44 C0011) manually. The other 124 rest on the probe's own guards.
6. **The other reviewer's report.** `experimental_notes/panel_results/Repair_Loop_Panel_2026-08-30.md` landed on main mid-session. I did not read it, deliberately, so nothing here is contaminated by it. Where we agree, that is independent corroboration; where we differ, both readings stand.

---

# Diff

```
 bench/falsifier_verify.py    |  43 +++++++++++++++++++
 bench/reference_runner_v2.py | 104 ++++++++++++++++++++++++++++++++++++++++++--
 bench/tests/test_repair_loop_wiring_2026-08-30.py  | new, 8 tests
```

Suite: **4354 passed, 1 failed** (pre-existing ledger drift, proven to fail on pristine HEAD), 38 skipped. Was 2 failed at base.

**The single most useful thing in this report:** `bench/fix_efficacy.py` already answers Question 2. It needed four small edits to be called, and 51.4% of the fixes in your archive fail the test it applies.

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