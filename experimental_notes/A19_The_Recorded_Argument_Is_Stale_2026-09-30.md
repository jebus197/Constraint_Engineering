# A19: the recorded decisive argument is stale, and the defect found beside it had its consequence backwards

**2026-09-30 12:20 BST. Branch `sim/shakedown-2026-09-29` at `9a1b7e9`. Audience: a reproducing engineer.** The plain-English companion is `A19_The_Recorded_Argument_Is_Stale_Plain_English_2026-09-30.md`; the spoken version is `~/Desktop/CDSFL_tts/A19_The_Recorded_Argument_Is_Stale_2026-09-30.txt`.

Every figure below was computed twice with independent tools. Producers: `scripts/a19_break_even_assumes_e2_absent_2026-09-30.py` (committed, exit 0, asserts on the rational enclosure, the E floor, the z3 non-vacuity control and the verdict flip) and the 5 sandboxed review agents whose full returns are in `.../subagents/workflows/wf_5e47f1a5-38d/journal.jsonl`.

---

## 1. The finding with a live decision consequence

`experimental_notes/CDSFL_MASTER_TASK_LIST.md:568`, dated 2026-09-11, carries the paragraph the founder would read in order to rule on A19. It states, capitalised in the original, that **"WITH THE FLAG ON, THIS PROJECT'S OWN ARCHIVED EXPLOIT IS STILL ADMITTED AT sk=1.0000"**, and concludes: *"That is the strongest argument for leaving it off."* Its companion sentence states that **"1 new HIGH is not enough to reject; 2 are."**

**Both are now false against current code.** Run against the same committed fixture `tk.SHELL_INJECTION_FIX`, `compute_sk` returns `NO_SCORE` at `sk = 0.0`, not `ADMISSIBLE` at 1.0.

**The cause is a repair made 11 days after the measurement.** `_prose_one_sided`, added 2026-09-22, sits at `bench/reference_runner_v3.py:12237`:

```python
if _scoring_prose and tristate == SK_ADMISSIBLE:
    introduced = _gates_introduced_new_defects(details)
    if introduced:
        return SkResult(sk=0.0, A=A, E=round(E, 4), tristate=SK_REJECTED, ...)
    details["_prose_one_sided"] = {"outcome": SK_NO_SCORE, "computed_sk": round(sk, 4), ...}
```

`_gates_introduced_new_defects` (`:11102`) reads only the `e3_ruff` and `e4_bandit` **`new:`** fields. Called directly with the gates' own detail strings:

| injected | `introduced` | prose outcome |
|---|---|---|
| clean (`0 new` ruff, `new: 0H/0M`) | `[]` | `NO_SCORE` |
| 1 new bandit HIGH | `['bandit: 1 new HIGH, 0 new MEDIUM']` | `REJECTED` |
| 2 new bandit HIGH | `['bandit: 2 new HIGH, 0 new MEDIUM']` | `REJECTED` |
| 20 new bandit HIGH | `['bandit: 20 new HIGH, 0 new MEDIUM']` | `REJECTED` |
| 1 new ruff diagnostic alone | `['ruff: 1 new diagnostic(s)']` | `REJECTED` |

End-to-end on the real prose target, 1/2/5/20 new HIGHs all returned `REJECTED`: **4 of 4, Wilson [51.0109%, 100.0000%]**. **So the prose path yields only `REJECTED` or `NO_SCORE`, never `ADMISSIBLE`.**

**The A19 entry is the artefact that needs correcting before the ruling, not the code.**

---

## 2. The defect found beside it, and the conclusion that was wrong

### Confirmed, by execution

`compute_sk`'s docstring (`:11335`) gives as the third of 3 reasons for the prose short-circuit that `e2_regression` is *"permanently unavailable: prose targets live outside the repository and no prose config sets `test_cmd`"*, and `:11390` asserts *"The third reason stands."*

**False on both halves for the run that tested it.**

- `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md` is **inside** the repository. The only kind-independent suppressor is containment: copied outside `REPO_ROOT`, e2 returns `{"score": null, "detail": "source not under REPO_ROOT"}`.
- A `test_cmd` **is** set. `Arm.argv()` guards `--test-cmd` with a truthiness test, so `test_cmd=None` emits no flag, and `build_parser()` substitutes its default. Executed:

```
arm4  argv()  : ['--target', 'bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md', ..., '--rounds', '8', ...]
  '--test-cmd' present in argv : False
  parsed args.test_cmd         : 'python3 -m pytest bench/tests/test_immune_memory_consumption.py
                                  bench/tests/test_immune_memory_evaluation.py -q'
  SUBSTITUTION OCCURRED        : True
arm1/arm2/arm3 : '--test-cmd' present True, SUBSTITUTION OCCURRED False
```

`compute_sk` never gates e2 on target kind; it appends `("e2_regression", score, 2.0)` whenever a score returns. Weights recovered **from the returned E** over 12 live `compute_sk` calls: sympy `solve` on 3 and on 4 equations both give `{a2: 2/5, a3: 1/5, a4: 2/5}`, ratio **2 : 1 : 2**; numpy `lstsq` gives `[0.4 0.2 0.4]`, rank 3, max residual 4.44e-16; mpmath at 50 dps max deviation 4.44e-17. **12 of 12 exact matches, Wilson [75.7506%, 100.0000%].**

**The gate cannot see its target.** A prose target with real bytes and with destroyed bytes both return `0.9454545454545454`; `bench/dm/_memory.py` real returns `0.9454545454545454` and gutted returns `None`. The constant is 52/55 = `"52/55 passed (sandbox)"`, and it is an artefact: `_run_effect_regression` copies `REPO_ROOT` with `secret_ignore(..., 'logs')`, so `bench/logs` is absent from the sandbox and 3 tests fail for that reason alone.

**`e1_efficacy`, not `e2_regression`, is the gate actually unavailable on this path.** Executed: `_unavailable = ['e1_efficacy']` on every arm4 fix, detail *"fix efficacy not measured: no probe result on this entry"*.

### Refuted: the conclusion drawn from it

The claim was *"no number of new bandit HIGH findings can ever cause rejection on a prose target with clean ruff."*

**Arithmetic exact, conclusion false.** All of it reproduces: e2 = 52/55, E floor = 159/275 = 0.5781818181818181, `S* = sqrt(23161)/38 - 7/2 = 0.50493117097042334623290819418709903839714462053309` (SymPy 50 dps and mpmath 60 dps agreeing to 4.5634e-51), margin 0.0732506472113948355852736239947 (agreeing to 1.9143e-32), and z3 returning `unsat` for "any (new HIGHs, new MEDIUMs) ≥ 0 gives E < S*" with a `sat` non-vacuity control and a `sat` contrast on the 2-gate mean.

**It describes the Python path.** On prose, E gates nothing: the veto intercepts first. Executed, the veto is invariant across **7 e2 values and 4 e1 values**, and deleting the `e2` or `e1` key changes its output not at all while deleting `e3` or `e4` changes it immediately. 3 different `test_cmd`s on the same prose fix give 1 tristate and identical R_k (0.5 → 0.5 clean; 0.5 → 0.62 with 1 new HIGH).

**The sign of the risk was also reversed:** the search was for a contaminated gate letting harm through, when the contaminated gate on prose cannot admit anything.

An intermediate claim, since withdrawn, held that `s_star` no longer decides. That was an over-correction. What is retired is the value the **shipped** `check_sk_threshold` *returns* (0.0 at the operating point, admitting everything — the gate whose records are "s_star zero in 4499 of 4499"). The live decision at `:12977` is `check_sk_threshold_corrected`, whose effective threshold is `max(sk_break_even(...), s_floor)`, and `sk_break_even` returns exactly A19's value. 4 routes agree to 2.005e-16 that `compute_rk(R,q,sk) <= R` is equivalent to `sk >= S*` at `q=0.5, R=0.5, nu_b=0.05, nu_f=0.20`: mpmath `findroot` 0.5049311709704231457357, scipy `brentq` 0.50493117097042339303, the closed form 0.5049311709704233462329, `sk_break_even()` 0.5049311709704235. **That equivalence is real but governs the Python path only.**

---

## 3. What the corrupted gate actually costs: a human-facing residue

**No machine verdict moves.** No archived prose-target fix was ever `ADMISSIBLE`: **0 of 8 deduplicated records, Wilson [0.0000%, 32.4408%], Clopper-Pearson [0.0000%, 36.9417%]** (statsmodels `beta` and `scipy.stats.beta.ppf` agreeing to 5.55e-17).

**The residue is the advisory number.** `_prose_one_sided` deliberately preserves `computed_sk` *"so a human reviewer could see what the gates would have said"*. Executed, it reads **1.0** with the target's own suite and **0.9782** with the argparse default. The archive holds **2** prose `NO_SCORE` records carrying `computed_sk = 0.9782` — a near-perfect advisory score built entirely from `bench/dm/_memory.py`'s suite run against a markdown specification.

**The guard that should have caught the substitution asserts on the producer only.** `bench/tests/test_commissioning_arms_carry_their_settings_2026-09-21.py:96-106` asserts `arm4.test_cmd is None` and never parses the argv with the real consumer — in a file whose own docstring cites `execute-do-not-grep`.

---

## 4. The heavier finding, on the path where E does decide

On a Python target with a real passing suite, a fix measured **not** to cure its own falsifier scores `E = sk = 5/7 = 0.7142857142857143`, is recorded `ADMISSIBLE`, and moves R_k from 0.5 to **0.495688**. SymPy, `fractions.Fraction` and mpmath agree the value is exactly 5/7 (max spread 1.586e-17), and since `inf` over e1 of E is 5/7 > 0 while `tristate = ADMISSIBLE if sk > 0`, **no finite weight lets e1 veto**. Archive: **73 raw records, ADMISSIBLE 73 of 73, Wilson [95.0008%, 100.0000%]** (11 deduplicated).

**Reproduction, not discovery** — the A19 entry already records it, and records why it was not fixed: reweighting *"changes which fixes are admitted on every Python target ever run."*

**The asymmetry, raised as a question.** The aggregation defect `_prose_one_sided` was built to fix — a hard negative dissolved into a weighted mean, with `ADMISSIBLE if sk > 0` carrying no threshold — is the same one that keeps `e1_efficacy` from vetoing on Python. One path got a one-sided veto; the other did not, for a recorded and real reason.

---

## 5. Three counting errors, one shape, one morning

All 3 are *a copy counted as an original*, and they occurred in 3 separate mechanisms on 2026-09-30.

1. **`.gitignore` inversion.** `bench/logs/**` plus `!bench/logs/**/*report*.json` and `!bench/logs/**/runner_state.json`: the `**` negations match at any depth, un-ignoring harvest **copies** while leaving unique seat scripts invisible. `git add -A` staged 20 byte-identical duplicates (`cmp`, 20 of 20) and left out 88 files including 3 seat-written falsifiers. Archive-wide: **220 of 220 seat `.py` ignored; 41 of 220 = 18.6364% unpreserved, Wilson [14.0451%, 24.3041%]**, 11 of 20 rounds affected. Producer `scripts/seat_evidence_is_gitignored_2026-09-30.py`.
2. **The archive gate counter.** `route_1_structured` counted harvest copies as archive records: on-disk 5086 → 5972, all **886** surplus from 136 byte-identical JSONs, **14.8359%** inflation. The guard's docstring instructed restating the figure, which would have published it. Fixed at the corpus definition; guarded by `bench/tests/test_a_sandbox_copy_is_not_an_archive_record_2026-09-30.py`, 14 executing cases, verified by reverting (20 passed → 13 failed).
3. **This note's own first scan.** Directory-level attribution took the first path component as the run, so `falsifier_root_cause_2026-09-30/sandbox_harvest/{cc2,fable}/attempt-1/files/bench/logs/<run>/` copies counted as independent. Path-aware resolution collapses **1066 raw hits to 17**: 11 legitimate on `bench/dm/_memory.py`, 6 contaminated on the prose target, **0** on `bench/cdsfl_registry/engine.py`. The reported "50 of 50" is **84 of 84, Wilson [95.6268%, 100.0000%]**; "593 of the other 643" double-counted, since 593 + 50 = 643. A second trap compounds it: `TARGET_KIND_PYTHON` is the string `"python_module"`, not `"python"` (`:1736`), and reading it as non-Python moved 133 Python records into the prose column. The reviewing agent hit both traps itself and recorded a retraction of its own `engine.py` claim under `failure-later-refutation-protocol`.

---

## 6. Not claimed

- `e2_regression` is **not** inert everywhere: it varies within a run in **17 of 41 runs, Wilson [27.7565%, 56.6329%]**, by 2 discriminators agreeing in 41 of 41.
- Nothing here shows turning `sk_score_prose_listings` **on** is safe. It shows the specific recorded argument against it has expired.
- The archive serialises each e2 score at 2 precisions (float in the report and `runner_state.json`; a 6-decimal string in `experiment_chain.json` sealed bodies), so any count must state its unit. Non-harvest numeric split: 4022 float, 617 string.
- **No clean full-suite figure exists for this HEAD.** A run begun 11:11 was invalidated by mid-run edits at 11:28:36 and 11:31:47 to documents ≥12 test files read, and was stopped at 48%. The only measured claim is the commit gate's 501 fast guards, green.

---

## 7. Open, and the founder's

1. **Turn `sk_score_prose_listings` on, or leave it off.** The recorded argument against has expired. Current behaviour: any new defect in a fenced listing → `REJECTED`; none → `NO_SCORE`; `ADMISSIBLE` unreachable. Whether that is wanted is design, not measurement.
2. **The false docstring sentence, and the argparse default.** Should `test_cmd=None` mean *no gate* rather than *substituted default*? The substitution is what made a gate grade a document it cannot read.
3. **Should `e1_efficacy` be allowed to veto on Python targets**, accepting that every past Python verdict shifts?
4. **Should `computed_sk` be suppressed when the gate behind it did not read the target?** It presently reads 0.9782 on a document nothing examined.

**Also pending and not in this note:** `rounds = 10` (both seats recommend it); whether `a = 4.89` is cumulative or a rate coefficient, which moves `n*` by a factor 5.70; and which cure to build first for the falsifier-supply gap.
