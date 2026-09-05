# Morning Report — tool dispatch was silently broken, and fixing it exposed a second defect

**2026-09-05, 05:09 BST (Saturday)**

Companion plain-text version: `~/Desktop/CDSFL_tts/Morning_Report_2026-09-05.txt`.
Full verbatim panel output: `experimental_notes/Panel_Findings_Verbatim_2026-09-05.md` (75,204 bytes), regenerable with `scripts/dump_panel_findings_2026-09-05.py`.

---

## Summary

The six-seat panel was re-dispatched under the founder's ruling that tool use is core to CDSFL. The re-dispatch established that the *previous* tool-enabled panel was not tool-enabled: **16 of its 17 tool calls returned `ModuleNotFoundError` and the models read that error as a tool result and reasoned on**. Root cause found, fixed, and proved by an executing regression test. After the fix the same 2 seats made **49 tool calls with 0 failures**.

Repairing that defect immediately exposed a second one it had been masking. With working tools, `cx` went from 10 tool calls to 31, exhausted `MAX_TOOL_ITERATIONS`, and `call_openrouter_with_tools` returned `final_text=""` — a full paid seat produced nothing. Also fixed, also proved.

Neither defect is applied to the mathematical appendix. Per the founder's instruction, all appendix changes are held for review.

---

## Defect 1 — silent tool failure

`bench/openrouter_tools.py:211,226` reach the verifiers as `from bench.immune_agents import ...`. That name needs **REPO_ROOT** on `sys.path`. Python sets `sys.path[0]` to the *script's own directory*, so `python3 bench/confer_maths_panel_2026-09-05.py` put `bench/` there instead.

### Measurement (broken run, `bench/logs/panel_maths_tools_20260905T034234Z/broken_toolpath_run/`)

| Seat | Tool calls | Errored | Survived |
|---|---|---|---|
| `cx` | 10 | 9 | 1 (`pytest_run`) |
| `cgpt` | 7 | 7 | 0 |

`pytest_run` survived because it shells out with `cwd=REPO_ROOT` and never performs the import.

### The second half of the cause, found only because a guard test contradicted the first diagnosis

`bench/` has **no `__init__.py`** — it is a namespace package. An empty stray tree `bench/bench/results/phase2` (3 dirs, 0 files, untracked, referenced by nothing, left by a `mkdir -p bench/results/phase2` run with cwd already inside `bench/`) was therefore enough to make `bench` resolve *successfully* to the wrong directory. The package import worked and shadowed the real one; only the submodule failed. **That is why the error read `No module named 'bench.immune_agents'` and never `No module named 'bench'`** — a distinction missed on first reading.

### Fix

- `bench/openrouter_tools.py`: append `REPO_ROOT` to `sys.path` at module import (appended, not inserted at 0, so nothing can shadow an installed package). All 4 callers inherit it.
- Removed the 3 empty stray dirs. Nothing lost: `bench/results/phase2/` still holds its 6 files from March, and `bench/run_phase2.sh:22` uses `$SCRIPT_DIR/results/phase2`, which is correct.

### Proof — `bench/tests/test_tool_dispatch_survives_script_path_2026-09-05.py`

Per `execute-do-not-grep`, the test **subprocesses a real script from inside `bench/`** rather than asserting on source text; a source-text guard passes against both the fixed and broken module. 10 pass with the fix, **6 fail with it reverted**, 10 pass on restore.

**A correction to that test file, same error class as the defect it guards.** Its first version pinned the exact string `No module named 'bench.immune_agents'`. Once the stray dir was removed the failure changed spelling to `No module named 'bench'`, and **7 of 10 assertions passed against a completely broken module**. It now checks both forms plus any bare `ModuleNotFoundError`.

---

## Defect 2 — cap exhaustion discarded the answer

`call_openrouter_with_tools` used `for … else: stopped_reason = "max_iterations"` and returned `final_text=""`. The cap's purpose is to stop tool spam, which exhausting the loop already achieves; discarding the reasoning was a separate unintended loss.

**Fix.** On exhaustion, exactly 1 further round-trip with `tools` omitted, asking for the verdict from work already done. Cannot loop (no tools advertised ⇒ no `tool_calls` can return). The prompt instructs the model to mark incomplete checks `UNVERIFIED` rather than assert them, so being cut off cannot silently convert a half-finished check into a stated result. A failed harvest sets `max_iterations_harvest_failed:<Type>` rather than looking like a model with nothing to say.

**Proof — `bench/tests/test_tool_cap_harvests_the_answer_2026-09-05.py`.** The re-dispatch that demonstrated the defect did *not* re-demonstrate it (cx used 9 calls the second time, under the cap); a branch reached by luck is untested. A mocked model that always requests another tool forces the condition deterministically and for free. 6 pass, **4 fail on revert**. Full tool suite: **52 passing**.

---

## Panel outcome

5 seats responded. `cc2` and `fable` route through `call_claude_cli` (`experiment_11_orchestrator.py:964`, `--allowedTools Bash Read Grep Glob`) and were never affected — both used real shell tools, and **both independently caught that the brief promised them 5 tools their route does not have**.

`ds` produced 602 characters and no usable verdict: it emitted Anthropic `<invoke name="sympy_verify">` XML as plain text, guessing the parameter name `proposition` where the spec says `claim`. Its route nulls tools by a deliberate gate at `experiment_11_orchestrator.py:1406` (2026-06-06, DSML leakage). Defensible for an experiment run where the runner re-executes falsifiers; **not** defensible for a design review with no runner. Recorded as unverified, not counted.

### What the panel found in my own brief — 5 defects, all valid

1. **"30 tests"** — the file has **31**. Confirmed by 3 seats, each by executing it.
2. **Wrong ν\*** — the break-even is at `MATHEMATICAL_APPENDIX.md` §1.1/L224, not §7.1; the brief also conflated the Stage-5 per-fix ν with the §7.1 Duane point-process ν.
3. **False tool routing** — promised 5 tools to seats that had none, *and* told the shell-capable seats they could not read files, which contradicts it.
4. **"Every test asserts zero-residual AND non-zero for a wrong model"** — false; 4 named tests carry no discrimination.
5. **"Three orders past the bound"** — corrected by a seat to 2.3. On checking, **both are right for their own parameters and wrong as general claims**; at the values actually tested it is 3.81 orders. The real defect is that neither statement named its parameters.

---

## Appendix defects — including a correction to my own proposed fix

### L38 coupling bound

The refutation stands: `exp(x) > 0` everywhere, so weights are non-negative without any bound, and `Z` already guarantees `P(x) ∈ [0,1]` (the appendix says so at L34).

**My proposed replacement was also wrong**, and this is the most useful thing the panel produced. I derived the bound from the all-ones state (`Σψ ≤ −Σlog qᵢ`). `cc2` showed that is **not sufficient for n ≥ 3**. Verified here with **SymPy, mpmath and Wolfram**, all agreeing exactly:

> n=3, q=1/20, entire budget `−Σlog qᵢ = 3log20 = 8.9872` placed on ψ₀₁. The all-ones bound is satisfied *exactly*, yet state {0,1} carries unnormalised weight **19** (`= (1−q)/q`).

The correct condition is per-subset, one inequality per S ⊆ [n]:

```
∀S ⊆ [n]:  Σ_{i<j∈S} ψ_ij  ≤  −Σ_{i∈S} log qᵢ  −  Σ_{i∉S} log(1−qᵢ)
```

The all-ones state is **one of 2ⁿ constraints**, not the binding one.

**New finding, from neither seat.** The original error is a complement error (`1−qᵢ` where `qᵢ` belongs), and it is **not uniformly conservative**. `Solve[−Log[1−q] == −Log[q], q]` → **q = 1/2** (Wolfram; SymPy agrees). Below ½ the stated bound over-constrains; **above ½ it under-constrains**, admitting couplings it was meant to exclude. That upper half is the reportable one.

**Seats disagree on purpose.** `cc2` argued the real purpose is float overflow; refuted here — the overflow threshold is `Log[$MaxMachineNumber] = 709.783`, the stated bound at q=0.05,n=3 is **0.1539**. Not an overflow guard. `fable` is correct on this point.

### G_n reduction row

My claim that the row needs `n_H = 0` is **too strong** — 3 seats said so independently and they are right. The exact residual (`cgpt`, confirmed here with SymPy **and** Wolfram):

```
G − w·C_M  =  w · C_H · (1−ρ) · (1−C_M)
```

Zero set: **C_H = 0 ∨ C_M = 1 ∨ ρ = 1 ∨ w = 0** — 4 conditions. Wolfram's `Reduce` supplied the 4th (`w = 0`), which I had missed. `n_H = 0` is sufficient via `C_H = 0`, never necessary. **The better fix is to state the residual, not enumerate conditions.**

### NEW — the numerical illustration is spliced (L688–695)

Found by `cc2`, recomputed here from the appendix's own formulas with SymPy and Wolfram, agreeing to 6 figures. Parameters as stated: 3 machine passes (p_M=0.3, d_M=0.7), 2 human (E=0.85, M=0.9, α=0.4, d_H=0.9).

| Quantity | Appendix formula gives | Table prints |
|---|---|---|
| C_M | 0.506961 | 0.507 ✓ |
| **C_H** | **0.921095** | **0.698 ✗** |
| Combined ρ=0 | 0.9611 | 0.961 ✓ (uses C_H=0.921) |
| Combined ρ=0.3 | **0.8249** | 0.851 ✗ |
| Combined ρ=0.6 | **0.6886** | 0.748 ✗ |

And the rows are **shifted by one**: recomputing with the table's own C_H=0.698 gives 0.8511 at ρ=0 and 0.7479 at ρ=0.3 — exactly the values printed against ρ=0.3 and ρ=0.6.

---

## The central question — preserved disagreement

**Does the simplicity/sufficiency distinction require new mathematics?**

- `cx`, `cgpt`, `fable`: **No** new central mathematics; yes to process machinery (a reduction-discharge rule).
- `cc2`: **Yes, minimally** — one scalar.

`cc2`'s argument was *checked*, not counted (tools decide, not votes). Verified with SymPy, z3 and Wolfram:

- ν\* at σ=1 reduces exactly to `qR` — matches L224.
- ν\*'s free symbols are exactly `{R, q, σ}` — **no reach or scope term**.
- `∂R_new/∂ν = 1 − R_base`, and z3 finds **no counterexample** to its strict positivity on `[0,1)`.

So the model charges blast radius identically whether a change holds at 1 site or 1000. **The consequence is sharper than "it fails to encode the distinction": it encodes the negation**, asserting that simplicity and sufficiency always compete. `cc2`'s proposal is one division — `ν_eff = ν/|D|`, charge blast radius per site covered — which is not piecewise and collapses to the present model exactly at `|D| = 1`.

The **diagnosis** is tool-confirmed. Whether to **act** on it is a design decision and is held open.

All 4 responding seats agree process machinery is needed, and 2 proposed **composable** refinements: `cc2` — the rule governs *identities*, not *parameter estimates*; `fable` — split `UNDISCHARGED` into `UNDISCHARGED(no attempt)` and `SAMPLED(evidence, n, interval)`. Together these answer the objection that the rule would otherwise forbid the appendix's only empirical anchor.

---

## Open decisions (nothing applied)

1. L38 — strike the false justification; remove the bound or adopt the per-subset form (correct, but 2ⁿ inequalities).
2. G_n row — replace the condition with the residual expression.
3. L688–695 — recompute, or state the C_H actually used.
4. **Adopt `ν_eff = ν/|D|`?** The only item that would change the mathematics.
5. Adopt the discharge rule, and with which of the 2 compatible refinements.
6. Give `ds` a text-protocol fallback, or keep recording it as an unverified seat.

## Housekeeping

- The compaction hook built 2026-09-04 is working — it has correctly reported all night that a compaction occurred at 03:51 and no `rs` has been run since.
- **Wolfram licence expires 2026-09-11** (6 days).
- `main` is **81 commits** ahead of `origin/main`; tonight's work is uncommitted.

Written under CDSFL note standard v1.7 (26 August 2026).

---

# Part 2 — the agreed task list, worked

**Appended 2026-09-05 05:57 BST.** Part 1 covered the panel rerun. This covers the 01:25 ruling list, which was the larger job and was not started when Part 1 was written.

**A correction first.** Asked whether the panel was the only job, the honest answer was no — only the panel had been done. Worse, the RTF containing the list was *skimmed*: grepped for verdict keywords, then read as one `sed` slice. That missed 3 annotations, one of them a direct instruction (`line 13`, "Can you fix?"), on the very document whose closing line warns against skimming. What follows comes from reading all 64 lines.

## Item 8 — the 2 appendix defects — **APPLIED**

Ruling: *"If you have [asked the models], then simply do the fix."* 4 seats had reviewed across 2 rounds. Every finding re-verified locally with 2 or 3 tools before touching `docs/MATHEMATICAL_APPENDIX.md`.

| Defect | Correction | Verified by |
|---|---|---|
| L38 justification (non-negativity) | Struck — `exp(x) > 0` always; `Z` already bounds `P(x)` | SymPy, mpmath, Wolfram |
| **My own** replacement bound | Refuted — all-ones is insufficient for n ≥ 3 | 3 tools, all return **19** exactly |
| Complement error character | **NEW** — crosses over at exactly `q = 1/2`; above ½ it *under*-constrains | SymPy `solve`, Wolfram `Solve` |
| G_n reduction row | States exact residual `w·C_H·(1−ρ)·(1−C_M)` | SymPy + Wolfram `Reduce` (supplied `w=0`) |
| L688–695 illustration | Spliced + row-shifted; C_H 0.698 → 0.921095; 0.851→**0.825**, 0.748→**0.689** | `scripts/verify_appendix_numerical_illustration.py`, 6/6 rows |

Counterexample detail: n=3, q=1/20, entire all-ones budget `3·log20 = 8.9872` on ψ₁₂ satisfies that bound *with equality* while state {1,2} carries unnormalised weight `(1−q)/q = 19`.

Tests **31 → 35**: the refuted bound test replaced by 4 discriminating ones.

## Item 6 — D12 commissioning — **DONE, premise false**

"Reachable by no configuration" ceased to be true on 2026-07-29 / 07-31. Executing probe through `build_runner_config_from_dict`: **71 of 72** fields arrive intact (the exception, `resume`, is read from `args` by design). What was missing was end-to-end evidence — now `bench/tests/test_d12_commissioning_end_to_end_2026-09-05.py`, **20 tests**, each comparing ON against OFF.

Still enabled in **0** shipped configs, deliberately: switching either on changes convergence conditions.

## Item 2 — the discharge rule — **STATED**

`experimental_notes/The_Discharge_Rule_And_Its_Alternative_2026-09-05.md`. Both options written in adoptable form, with a worked example on 2 adjacent appendix lines.

## Item 1 — the fix-acceptance gate — **WITHDRAWN, premise refuted**

1. "0 of 3816" had **no committed script** — 1 day after the ruling requiring one. Third repeat. `scripts/measure_sk_threshold_gate_fire_rate.py` reproduces it: **0 of 3816**, Wilson [0.0000, 0.0010], cross-checked vs statsmodels. The "400 error-path lines" is **376**.
2. That script's first version counted the bare phrase `"(Valley of Bad Fixes)"` → 11 hits, **all** models discussing the concept in transcripts. Phrase-mentions as events, same class as the 1,577-mention miscount. Both patterns now anchored on the emitted line format.
3. **The shipped S\* formula is correct.** Re-derived from the runner's own `nu_eff`: SymPy gives `derived − shipped = 0`; z3 returns `unsat` searching for any point where the gate condition differs from `nu_eff ≤ nu*`.
4. **The real defect is the σ conflation** — ν\* is evaluated at σ=1 while σ *is* s_k. Correcting flips **3.215%** of decisions over 400,000 points with s_k ≥ 0.74, Wilson [3.161%, 3.270%], **every flip PASS → REJECT**. So "provably inert" is false.
5. `s_star` reads **0.0 in 3816 of 3816**. At shipped defaults it clamps to 0 for `qR ≥ 0.24` and to 1 for `qR ≤ 0.05` — the gate discriminates only inside `qR ∈ (0.05, 0.24)`.

**Applied** (additive, unambiguous): `reference_runner_v3.py` now records `gate_inputs` — `nu_b`, `nu_f`, `q`, `R_old`, `s_floor`, `effective_threshold`. Not 1 of 3816 records carried them, which is why the first explanation *inferred* `nu_f = 0` and was wrong.

**Composed action stays unapplied** — the attached condition was model review, and the panel record has 0 mentions of it.

## Item 7 — D13 rubric — **BOTH QUESTIONS ANSWERED**

`scripts/reproduce_rubric_human_queue_partition.py` reproduces the panel exactly: 286 items, 27 UNJUDGEABLE, 259 judgeable, 141 agree = **54.44%** Wilson [48.4%, 60.4%], 33 falsifier-era disagreements, **A=27 (81.8%) B=2 (6.1%) C=0 D=4 (12.1%)**, 87.9% decided programmatically.

**Q1, who adjudicates? Nobody.** A 4-way schema lookup, not a judgement. Only class D reaches a person, as a *decision* (commission a falsifier?), never a severity judgement.

**Q2, are the 4 irreducible? No — and worse.** Hypothesis that they were already tool-settled (status is tool-only; `CONFIRMED` ≡ "a falsifier fired") was **refuted twice**: the enforcement making tool-only statuses unfakeable landed **2026-08-23** (`b312b84`) and all 4 runs predate it; and **0 of 4 carry any `falsifier_code`**. Their status came from model verdicts — CC2 CONFIRM, DeepSeek CONFIRM, Codex/ChatGPT CONFIRM. **Confirmation by model vote, which the project forbids.**

**Wider:** **118 of 864** archived findings with a tool-only status have no falsifier code — **13.66%**, Wilson [11.53%, 16.11%] (CONFIRMED 65, CLOSED 28, REFUTED 13, MERGED 12; MERGED legitimately needs none → ~106 concerning). All pre-2026-08-23.

## Items 4, 5 and line 13

- **D9 + D11** — 3 configs in `bench/exp56_configs/` + design note, **69 tests** driving each through the launcher path. **Not launched** (paid dispatches).
- **D10** — `bench/seeded_defect_catalogue.py` built, under verification.
- **Line 13, "Can you fix?"** — `~/.claude/hooks/ffafp_audit.py`, **33 tests**. Reports missing FFAFP traces; does not block, because a heuristic block gets disabled and a false block is worse than a missed reminder. `settings.json` **not** edited — stanza reported.

## Held back

**D8 execution-based matcher** — builds, 20 tests, but **flaky: 2 of 5 consecutive runs fail**, Wilson [11.8%, 76.9%] on n=5. A flaky test reads as green, so it is not recorded as done.

## What was got wrong — 7 refuted claims

| Claim | Reality |
|---|---|
| "Repair is provably inert" | Flips 3.215% of decisions, all PASS→REJECT |
| "400 error-path lines" | 376 |
| "Route 2 shows 0 occurrences" | First script showed 11 — all phrase-mentions |
| CI "[9.7%, 70.0%]" | Wilson, unlabelled; Clopper-Pearson is [4.3%, 77.7%] |
| "3 orders past the bound" | Parameter-dependent; 3.81 at the values used |
| "ν_f = 0" | Inferred, not measured — wrong |
| "The 4 were tool-settled" | Refuted; confirmed by model vote |

Every one was caught by **running** something, not by reading.

## Outstanding decisions

1. Discharge rule, or its alternative.
2. Correct the gate's σ conflation, now that inertness is disproved.
3. Commission 4 falsifiers → human queue to 0.
4. What to do about the 118 archived findings with unbacked tool-only status.
5. Launch the D9/D11 comparison (paid).
6. Enable either D12 setting in a real config (changes experimental conditions).
7. Wire the FFAFP audit hook into `settings.json`.
8. The reach normalisation `ν_eff = ν/|D|` — the only item that changes the mathematics.

`main` is **84 commits** ahead of `origin/main`, unpushed.

Written under CDSFL note standard v1.7 (26 August 2026).

---

# Part 3 — the builds returned, and none is clean

**Appended 2026-09-05 07:05 BST.** The 4 parallel builds finished; each was then checked by a separate adversarial reviewer instructed to find what is wrong. **Not 1 of 4 came back clean.**

## D8 — the flakiness is gone, and Part 2's entry needs correcting

Part 2 recorded D8 as held back at 2 of 5 runs failing. The builder found and fixed the cause. Re-measured post-fix: **0 failures in 16 runs** (10 idle + 6 under deliberate load), Wilson [0.0%, 19.4%], Clopper-Pearson [0.0%, 20.6%].

**Caveat that cannot be removed:** the failing version was untracked and has been overwritten, so it cannot be re-run. The improvement is *consistent with* the fix but not separable from the fact that the failures were measured while 2 workflows loaded the machine.

**Headline reproduced independently** (`python3 -m bench.execution_based_matcher --compare exp44`):

| Metric | Value |
|---|---|
| pairs / execution-decided | 15 / 12 |
| disagreements with text matcher | 7 of 12 (58.3%, Wilson [32.0%, 80.7%]) |
| text merges what execution separates | **7 of 7** |
| text separates what execution merges | **0** |
| sign test on the direction | p = **0.0156** (scipy + hand-computed, identical) |
| agreement with the *independent* stored repair adjudicator | **12 of 15 = 80%**, Wilson [54.8%, 93.0%] |
| all 3 referee disagreements | rows whose stored detail carries an **ERROR leg** |

Survey across 4 archived code-target runs: 4,511 pairs, 643 text-duplicate, **rate 0.14254**.

### A repo-safety defect that is NOT D8's fault

D8's docstring claims *"the repository is never written to."* **False, and reproduced here independently before reporting.**

`_build_discrimination_overlay` builds a symlink tree — every file except the target is a symlink to the real file — and `profile()` hashes **only the target**. A falsifier writing to any sibling writes through the link into the real working tree, undetected. Demonstrated in a throwaway repo: sibling overwritten with `CLOBBERED BY FALSIFIER`, real file changed, **guard did not fire**.

**The builder is the runner's** (`reference_runner_v3.py:3442`), already used by the discrimination control at `:4187` and `:4228`. So this is a **pre-existing hole D8 inherits and would amplify** — 81 executions versus 1 at the gate. Both default-off. Project memory already records *panel agents edit the repo mid-run, caught twice*; this is the same shape one level down.

**Second defect:** the `except` path in `_run` (`:340`) has zero coverage. Replacing `HARNESS_ERROR:{type}` with `"REFUTED"` leaves **20/20 green** and converts an equipment failure into a false `SAME` — verbatim the failure the module's own comment names.

## Line 13, "Can you fix?" — the answer is **no**

Verbatim from the builder: *"THE PREMISE IS FALSE AND THE HONEST ANSWER IS 'NO, NOT AS STATED'. FFAFP cannot be enforced mechanically, and I should not have said it could."*

Find and Follow happen in reasoning; a hook sees the tool-call record and nothing else. It cannot tell a real test from a tautological one — **all 3 of this project's constant-42 tautology tests would satisfy such a detector.**

Built instead: a **one-sided trace detector**, `~/.claude/hooks/ffafp_audit.py`, named `ffafp_audit` not `ffafp_enforce`. Absence of a trace is evidence (a turn that edited Python and ran no test, assert or STEM tool did not P-pass); presence proves nothing. Docstring lists 5 false-negative and 4 false-positive modes.

**Reviewer verdict: PARTIALLY REFUTED.** 40 mutations, 33 killed, **7 survived**. 3 of 4 headline discrimination claims hold only for the P-pass limb; 1 of 3 verdict codes can be deleted with the suite green. **Not wired** — `settings.json` stanza described, not applied.

## D9/D11 and D10

- **D9/D11 — PARTIALLY VERIFIED.** One claimed discrimination **refuted by execution**; 6 defects confirmed. Useful correction: seat contrast was removed in `556e0af` on 2026-04-02 and **not cleanly** — a residual contrast survives. Design problem flagged: **seat count is confounded with vendor diversity**, and 3 arms cannot separate them; a 4th arm is needed.
- **D10 — VERIFIED**, but the claimed discrimination figure is overstated and 9 of 10 unkillable guards were undisclosed.

## A mistake made and corrected during this work

Testing D8 under deliberate load, 4 CPU-spinner processes were started and **not successfully stopped** — `jobs -p` does not capture them in a non-interactive shell. They ran **7 minutes at ~85% each** before being noticed and killed (PIDs 25633-25636). Same class the founder had to clean up manually once before. It also slowed the concurrent full-suite run.

Written under CDSFL note standard v1.7 (26 August 2026).

---

# Part 4 — the full suite, and 3 guards that were wrong

**Appended 2026-09-05 07:16 BST.** Suite run twice, before and after the fixes below.

**First run: `8 failed, 5144 passed`.** Every failure traced to work added tonight, so each was diagnosed rather than patched to green. **3 of the 4 guards were measuring the wrong thing.**

| Guard | Verdict | Why |
|---|---|---|
| `test_operational_scripts` exit-code check | **FALSE POSITIVE**, 2nd of its class | substring-matched 2 literal spellings |
| `test_launch_preflight_refuses` | **FALSE POSITIVE** — acting on it would void Exp 56 | hardcoded `TARGET_KIND_PROSE` |
| `claims_audit.merge_arbitration_default` | **WRONG SENSITIVITY** | 1 never-run config flips a claim about runs |
| `EXPERIMENT_RUN_LEDGER.md` | **NOT A DEFECT** | derived; regenerated |

## 1. Exit-code check — the same false positive, one spelling later

Matched exactly `sys.exit(main())` / `raise SystemExit(main())`. Its own comment records fixing this on **2026-08-16 by adding the second spelling** — the same instrument with a longer list.

**Measured by execution**, 4 probe scripts, shell exit codes read:

| Entrypoint | Exit | Verdict |
|---|---|---|
| `main(sys.argv)` (bare) | 0 | correctly a violation |
| `raise SystemExit(main())` | 3 | accepted |
| `raise SystemExit(main(sys.argv))` | 3 | **flagged, and it propagates** |
| `sys.exit(main(sys.argv[1:]))` | 3 | **flagged, and it propagates** |

Replaced with an `ast`-based check asking the structural question — is the `main()` call inside `sys.exit(...)` or `SystemExit(...)`? — which is spelling- and argument-independent. A new test pins the argument-passing forms and still rejects a bare call. A third spelling would have repeated the mistake a third time.

## 2. Preflight — acting on it would have voided the experiment

It passed `TARGET_KIND_PROSE` for every config. The absorber refusal is **gated on prose**, so the 3 Exp 56 arms (target: `bench/cdsfl_registry/engine.py`) were flagged for a refusal unreachable at launch.

The obvious repair — enable `routing_enabled` — **would have silently destroyed the comparison.** Routing is off in all 3 arms deliberately: with 1 seat in Arm A the ladder is built from the orchestrator's full 5-seat roster and pulls in exactly the 4 vendors that arm exists to do without (design note line 74; `rank_falsifier_writers(['CC2'], exclude=['CC2'])` returns 0 rungs, the full roster returns 4). Fixed by calling `resolve_target_kind` per config.

## 3. Merge arbitration — wrong sensitivity

Returned False only while **no** config disabled it (`on and not off`), so one never-executed config flips a claim about what **runs** used. The Exp 56 arms disable it deliberately to stop the arbitration context arming with the full roster inside the single-model arm; the explicit `false` is kept, not omitted, so the run cannot depend on a dataclass default. Now weighs `on > off`.

## 4. Ledger — regenerated

Derived from `bench/logs`; adding configs moved it. Regenerated → matches, **56 run directories**. Gap-set expectation `{50,51,52}` → `{50,51,52,56}`, since a planned experiment with configs and no runs is precisely "configured but never ran". Its real subject — exp54 has *neither*, and a config-only scan misses it — is untouched.

## Result

**`5153 passed, 0 failed`** under `--netguard-strict`; 45 outbound attempts across 19 tests, all denied. Arithmetic consistent: 5144 + 8 = 5152, +1 new guard test = 5153.

## Two more of my own mistakes

- **`git add -A` swept an agent's script into a commit unreviewed.** Reviewed after the fact and kept: `scripts/verify_rtf_annotation_attribution.py` answers the founder's 2026-09-04 question about whether a missing `#` jumbled annotation authorship — and answers it *without using `#`*, partitioning the RTF by Word `insrsid` revision ids. Measured: **72 founder-typed blocks, 0 unmarked, 0 `#` in CC1 text.**
- **Its interface was broken**: usage advertised `--falsify` while argv was hand-parsed, so `--help` showed nothing argparse-shaped and `--falsfy` was silently dropped rather than refused — the falsification pass would quietly not run while output still looked clean. Now argparse, `nargs="*"` so an unknown flag is reported before a missing filename.

Written under CDSFL note standard v1.7 (26 August 2026).
