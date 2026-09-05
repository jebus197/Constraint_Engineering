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
