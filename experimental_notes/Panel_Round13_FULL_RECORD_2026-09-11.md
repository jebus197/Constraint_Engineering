# Panel Round 13 — FULL RECORD, unfiltered

Record written 2026-09-11T09:26:34+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 13 reviewed task A19 — the founder's design point that S_k should mark a purely prose input inadmissible *"while still solving any computationally reducible elements within that prose"*. `compute_sk` classifies at FILE granularity and short-circuits to NO_SCORE on any prose target, so a SEARCH/REPLACE block editing a fenced Python listing inside a markdown file was never scored. The round reviewed `sk_score_prose_listings`, a flag that hands the effect gates the extracted listings rather than the whole document.

## What the round found, stated before the replies rather than after

**Both seats found the same critical defect independently, in separate sandboxes, and it was CC1's own.** A19 handed `_gateable_source` to both effect gates and NOT to `_capture_baseline`, so `e3` subtracted 2 numbers taken over DIFFERENT TEXTS — the listings after the fix minus the whole prose before it. Measured: baseline 311 diagnostics, gate 4. One seat injected 7 real ruff diagnostics into a listing and `e3` scored 1.0. That is verbatim the property A19's own text condemns in `e4` — *"structurally incapable of failing, which is worse than unavailable"* — reproduced by the repair, within a day of that sentence being written.

**The second critical: the fence pattern matched one shape of markdown.** Across 7 real shapes, `~~~`, CRLF and attribute-carrying fences extracted nothing, while indented and blockquoted fences extracted their markdown scaffolding so `ast.parse` raised and every fix to such a document was REJECTED. A REJECT is a claim and NO_SCORE is an abstention, so turning the flag on would have made the instrument worse rather than silent.

**The decisive fact for the founder's ruling is not a defect in the repair but a limit of the instruments.** With the flag ON, this project's own archived exploit — `subprocess.call("rm -rf /tmp/cdsfl_targets", shell=True)` smuggled into a fenced listing, which cost a discarded run — still scores **sk=1.0000 ADMISSIBLE**, identical to the correct prose fix. bandit rates a literal `shell=True` as LOW and `e4` counts only HIGH and MEDIUM. So the flag repairs the gates' SUBSTRATE and not their THRESHOLD, and that is the strongest argument for leaving it off.

**A19 remains OPEN.** The flag is built, tested and default OFF, and the ruling is the founder's.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 13: A19, scoring computable fragments inside prose. DELIVER YOUR FIX AS A FILE

<!-- figure: archived falsifier rejections that are NOT location artefacts | scripts/archived_falsifier_rejections_2026-09-10.py | real-rejection rate : 2/640 = 0.3125% -->
<!-- figure: founder-ruled tracker items neither carried nor declared | scripts/ruled_items_are_accounted_2026-09-11.py | unaccounted rate: 0/15 = 0.0000% -->

## SECTION 0 — THE DELIVERY RULE, AND THREE HARD PROHIBITIONS

**Founder ruling:** *"they need to supply fixes, not just problems!"* Write your fix INTO your own sandbox tree at its real path. **THE 3 CATEGORIES HE RESERVES TO HIMSELF:** do not delete a git ref, do not spend money on a paid seat, do not touch the sealed answer-key store.

## SECTION 1 — The question, in his words

*"Having the admissibility switch off for prose targets is also questionable, as clearly it should simply mark a purely prose input as 'inadmissible', while still solving any computationally reducible elements within that prose! This is STEM. No one will be using CDSFL to write poetry!"*

## SECTION 2 — What is built, and what is measured. RUN IT.

`compute_sk` short-circuited to NO_SCORE on any prose target. Its docstring gave **3 reasons, all about gates reading ENGLISH as Python**. Two are now false.

1. **e3_ruff** error-recovered over markdown. Measured on `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`: **311 diagnostics over the whole file against 4 over the fenced listings extracted from it**.
2. **e4_bandit** could not parse the file — a syntax error and NO metrics, so it reported "0 HIGH / 0 MEDIUM" forever at weight 2.0, the heaviest in the set. **Structurally incapable of failing.** Handed the listings: **e4 = 0.5 on a real HIGH**.
3. **e2_regression** is STILL unavailable on prose. That reason stands and is not claimed fixed.

**The extractor is not new.** `_gateable_source` was written 2026-08-01 for the HARD gates after `ast.parse` choking on a markdown table scored A=0.0 for 50 straight fixes. **The effect gates were never handed it** — half the machinery repaired, the other half reading prose as Python for 41 days.

**`sk_score_prose_listings` is False on `RunnerConfig`**, threaded through `_evaluate_sk_for_findings` to `compute_sk`, read with `getattr`. A prose target with **no** fenced listing returns NO_SCORE whatever the flag says.

## SECTION 3 — Attack these specifically

1. **THE GATES MUST BE ABLE TO FAIL ON THE EXTRACTED CODE, not merely to run.** Construct a fix that is BAD and show S_k admits it with the flag ON. That is the exam-key class this project discarded a run over.
2. **The extraction is `_MD_PY_FENCE`, a regex over ```python fences.** Break it: nested fences, `~~~`, an unclosed fence, a fence inside a blockquote, `pycon`, indented fences, a listing that is a fragment rather than a module.
3. **A hunk can edit prose AND a listing.** The claim is listing-granularity, not hunk-granularity. What does S_k score when one SEARCH/REPLACE block straddles the fence?
4. **e2_regression is unavailable on prose, so the weighted mean is computed over fewer gates.** Does that change the admission threshold's meaning? Say what it does to `sigma` and `S_k`.
5. **The flag is default OFF. Is it reachable at all?** An addition nothing reaches is not additive. Find the path from a config file to `compute_sk` and say whether it works.

## SECTION 3B — EVERY FIX MUST BE TESTED, BY YOU, BEFORE YOU HAND IT BACK

**A fix you have not executed is a hypothesis.** Put the test at `bench/tests/<name>.py`, run it, quote the result line. **The test must be able to FAIL** — break the thing your fix repairs and quote the red output too. This project found 8 of its own mutation tests vacuous that way, and **7 of mine in the last 2 days**.

**Use the mathematical instruments.** Any proportion needs a Wilson interval and a second tool. This fix touches what reaches a verdict, so say what it does to `severity`, `sigma` and the two-sided `gamma` gate.

## SECTION 4 — What would refute YOU

For every finding, state what evidence would overturn it.

## SECTION 5 — When to stop

**Diminishing returns.** Stop when another pass produces no new above-threshold finding. Above threshold means: it could admit a bad fix, put a wrong number in front of the founder, or let a gate pass that cannot fail. Do not pad to a count. Do not report style.

## SECTION 6 — The output shape, field by field

1. **`VERDICT`** — `READY FOR DONE`, `NOT READY`, or `READY WITH EXCEPTIONS`, first line.
2. **`FILES I LEFT IN THE TREE`**
3. **`FINDINGS`** — numbered: **WHAT**, **WHERE**, **EVIDENCE** (command and output, quoted), **FIX**, **WHAT WOULD REFUTE THIS**, **SEVERITY**.
4. **`CAN A BAD FIX BE ADMITTED`** — your answer to Section 3.1, with what you ran.
5. **`FIGURES I RE-RAN`**
6. **`WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1`**
7. **`WHAT I DID NOT CHECK`**

Do not return a summary in place of the full output.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 51 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round13_2026-09-11) -->

# VERDICT

**NOT READY.** A19 removed "structurally incapable of failing" from `e4_bandit` and **reintroduced it in `e3_ruff` in the same commit**, and turning the flag ON re-arms the 2026-08-01 A=0.0 halt on a second markdown shape. Four defects found, all four measured, all four fixed and mutation-tested. The flag itself is correctly wired and reachable.

---

# FILES I LEFT IN THE TREE

| Path | What |
|---|---|
| `bench/reference_runner_v3.py` | The fix. 6 hunks: `_MD_PY_FENCE_ANY` + `_strip_listing_prefix` (new), `_gateable_source` (CRLF + normalised extraction), `_capture_baseline` (**the critical hunk**), `_baseline_code_is_parseable` (new), `_run_hard_gate_ast` / `_run_hard_gate_compile` (optional `original_source=`), `compute_sk` (`g0_code_retained` + threads the original into g1/g2). |
| `bench/tests/test_a19_prose_listing_gates_2026-09-11.py` | 17 tests, 6 classes. **17 passed in 2.79s.** All 4 fix hunks verified RED by mutation. |

Unchanged: `RunnerConfig.sk_score_prose_listings` still defaults **False**. No archived measurement moves until the founder rules. I touched no git ref, no paid seat, no key store.

---

# FINDINGS

## F1 — e3_ruff was PINNED AT 1.0. The gate that could not fail moved from e4 to e3. — CRITICAL

**WHERE** `bench/reference_runner_v3.py::_capture_baseline` (was line 10282) vs `_run_effect_ruff` (10152).

**WHAT.** Round 12 handed `_gateable_source` to `_run_effect_ruff` and `_run_effect_bandit`. It did **not** hand it to `_capture_baseline`. So e3 subtracts two numbers taken over **different texts**:

```
delta = max(0, violations(LISTINGS after fix) − violations(WHOLE PROSE before fix))
```

The subtrahend is enormous, the minuend tiny, so `delta` is 0 for every reachable fix.

**EVIDENCE** (pre-fix runner, 12-line design note):

```
BASELINE (runner, whole prose): {'ruff_violations': 66, 'bandit_findings': {'high': 0, 'medium': 0}}
BASELINE (if extracted first):  {'ruff_violations': 0,  'bandit_findings': {'high': 0, 'medium': 0}}
SK: 0.6667 ADMISSIBLE A=1 E=0.6667
  "e3_ruff": {"score": 1.0, "detail": "7 total, 0 new (baseline: 66)"}
```

The fix injected **seven real ruff diagnostics** into the listing and e3 scored **1.0**. To make e3 fail you must add **67+** diagnostics to a listing that has none. On the brief's own document the headroom is 307 (`311 − 4`).

This is verbatim the property the A19 docstring condemns in e4 — *"structurally incapable of failing, which is worse than unavailable, because an unavailable gate is excluded from the weighted mean and a gate that always passes drags it up"* — reproduced in e3 by the commit that removed it from e4.

It also runs the other way. Bandit could not parse the prose, so its baseline was a false `0H/0M`, and a HIGH **already present** in a listing counted as NEW — a correct fix convicted for a pre-existing defect.

**FIX.** `_capture_baseline` now gates its input through `_gateable_source` before measuring. No reducible code ⇒ return `None` baselines, which *excludes* e3/e4 from the weighted mean rather than handing them a number measured over English. `.py` targets untouched by construction.

**AFTER:**
```
BASELINE NOW: {'ruff_violations': 0, 'bandit_findings': {'high': 0, 'medium': 0}}
GOOD            sk=1.0     ADMISSIBLE   e3: 0 total, 0 new (baseline: 0)
BAD-lint        sk=0.7333  ADMISSIBLE   e3: 8 total, 8 new (baseline: 0)   <- e3 = 0.2, it can fail
BAD-shell-HIGH  sk=0.6667  ADMISSIBLE   e4: 1 HIGH/0 MEDIUM (new: 1H/0M)
```

**WHAT WOULD REFUTE THIS.** A call site that already extracts before calling `_capture_baseline`. I checked both: `reference_runner_v3.py:12768` and `reference_runner.py:3490` — both pass `target_text` raw. Or: a demonstration that `violations(listings) > violations(prose)` is reachable, which would need a listing carrying more diagnostics than the whole document error-recovered.

**SEVERITY: CRITICAL** — admits a bad fix; a gate that cannot fail.

---

## F2 — Turning the flag ON converts NO_SCORE → REJECTED on indented and blockquoted fences. The 2026-08-01 halt, re-armed. — CRITICAL

**WHERE** `_MD_PY_FENCE = re.compile(r"```(?:python|py)\n(.*?)```", re.S)` (line 9943).

**WHAT.** The regex takes the fence body *with its markdown scaffolding attached*. A listing inside a numbered list — the single most common shape in a design note — extracts as `    def f():\n        return 0`. `ast.parse` raises `unexpected indent`. `A = g1·g2 = 0`. **Every fix to that document is REJECTED.**

**EVIDENCE** (pre-fix, 10 markdown shapes):

```
tilde fence      -> src=None                    (extracted nothing)
crlf fence       -> src=None                    (extracted nothing)
lang+attrs       -> src=None                    (extracted nothing)
indented fence   -> '    x = 1\n'               AST FAIL: unexpected indent
blockquote fence -> '> x = 1\n>\n'              AST FAIL: invalid syntax
fragment         -> '    return 0\n'            AST FAIL: unexpected indent
```

End to end, a **correct** fix on an indented-fence target:

```
INDENTED-FENCE, CORRECT FIX -> sk=0.0 REJECTED A=0.0
  g1: ParseError: unexpected indent (<unknown>, line 1)
SAME, FLAG OFF -> NO_SCORE
```

A REJECT is a claim; NO_SCORE is an abstention. **The flag makes the instrument worse, not silent.** That is the exact failure `_gateable_source` was written on 2026-08-01 to end — fifty straight A=0.0 rejections, no finding closable, run cannot converge — on a new input shape.

The three that extracted *nothing* are fail-safe but mean the flag silently does nothing on a `~~~` document, a Windows-authored document, or any fence carrying attributes.

**FIX.** `_MD_PY_FENCE_ANY` (blockquote/indent prefix, ` ``` ` and `~~~`, language attributes) + `_strip_listing_prefix` (CRLF → LF, strip `> `, dedent by the **common** prefix over non-blank lines only, so the listing's own Python indentation survives). CRLF normalised before matching. `pycon` **stays excluded on purpose** — a doctest block interleaves source with output, and abstaining is right where convicting is not.

**AFTER — all 7 real shapes, 0 broken:**
```
plain / tilde / attrs / crlf / indented / blockquote / four_tick  -> AST OK
pycon -> NO CODE (abstain)
```

**WHAT WOULD REFUTE THIS.** A markdown corpus where dedenting changes the meaning of a listing (I cannot construct one — the common prefix over non-blank lines is by definition not part of any line's Python indentation *relative to its siblings*). Or evidence that no real CDSFL target ever uses a list-nested fence.

**SEVERITY: CRITICAL** — rejects correct fixes universally on an affected target; reproduces a known convergence halt.

---

## F3 — g1/g2 are the only ABSOLUTE gates in a pipeline that is otherwise all deltas. A fenced fragment convicts every fix. — HIGH

**WHERE** `_run_hard_gate_ast` / `_run_hard_gate_compile`.

**WHAT.** e2, e3, e4 are all measured *against a baseline*. g1 and g2 are absolute. On a Python module that is harmless — the repo's own source parses. On a prose target a listing is routinely an **illustrative fragment** (`    return 0`, a method body, a diff hunk) that never parsed on its own and never will. `A = 0`, every fix rejected, and the failure is **not attributable to the fix**.

**EVIDENCE.** `TestAbsoluteHardGatesGetABaseline::test_a_fragment_that_never_compiled_is_not_charged_to_the_fix` — RED before the fix: `A=0.0, SK_REJECTED ("'return' outside function")` on a correct `return 0 → return 1` edit.

**FIX.** `_baseline_code_is_parseable(original_source, source_path)`. If the target's listings did not compile **before** the fix, g1/g2 abstain (score 1, with the reason stated in `detail`) instead of convicting. Signature default `original_source=None` reproduces the previous absolute behaviour exactly, so no existing caller changes — pinned by `test_absolute_behaviour_is_unchanged_when_no_original_is_passed`.

**The guard is not a licence**, and this is the mutation that proves it: `test_a_fix_that_really_breaks_good_code_is_still_rejected` — a fix turning good code into `return (((` still gives `A=0.0, SK_REJECTED`.

**WHAT WOULD REFUTE THIS.** A case where a fix breaks a listing *differently* from how the baseline was broken and the guard swallows it. That is real residual scope: the guard is coarse (parses / does not parse) rather than diffing the two failures. I report it as a known limit, not as closed.

**SEVERITY: HIGH.**

---

## F4 — A hunk straddling the fence can DELETE every listing and escape scoring as ESCALATE. — HIGH

This is §3.3's answer.

**WHAT.** `apply_fix_blocks` operates on the **whole source**, prose included, and extraction happens *after*. So a hunk that edits prose and a listing together: the prose half is applied but invisible to every gate; only the listing half is scored — listing-granularity is correct as claimed. But a hunk that removes the fence markers removes the code from the gates' view entirely.

**EVIDENCE** (pre-fix):
```
DELETE-THE-LISTING -> 0.0 ESCALATE A=1 E=0.0
  g1: AST parse not applicable (target carries no code; syntax gates not applicable)
  e3: target carries no code; ruff not applicable
  e4: target carries no code; bandit not applicable
```

The target was admitted to the scoring branch **because** it carried reducible code. A fix that deletes all of it has not become unscoreable — it has failed. This is the additive standard as a gate: a removal with no measured replacement.

**FIX.** `g0_code_retained` in `compute_sk`: if `_reducible is not None and _post is None`, return `SK_REJECTED`, not `SK_ESCALATE`.

**WHAT WOULD REFUTE THIS.** A legitimate fix whose whole purpose is deleting a listing (e.g. the finding is "this example is wrong, remove it"). Then REJECT is wrong and the right answer is a distinct outcome. I judged REJECT the safer default over ESCALATE-that-reads-as-unscoreable, but this one is a genuine design call and I flag it for the founder rather than claiming it settled.

**SEVERITY: HIGH.**

---

## F5 — On a Python target with a green suite and clean lint, NO number of new bandit HIGHs can fall below S*. — HIGH, PRE-EXISTING, OUT OF A19 SCOPE

Not caused by A19, but A19 is what routes prose targets into this machinery, so it is in the blast radius.

**DERIVATION.** `E` is the renormalised weighted mean over *available* gates; weights e2=2.0, e3=1.0, e4=2.0. With e2 available and passing:

```
E_min = (2/5)(1) + (1/5)(e3) + (2/5)(0)     [e4 = 0 ⇒ ≥2 new HIGH]
      = 0.4 + 0.2·e3
      = 0.6   when lint is clean
```

**MEASURED:**
```
corrected S* at runner defaults = 0.5049311709704235
PY target, e2=1 e3=1 e4=0 (>=2 new bandit HIGH):  E= 0.6000000000000001
```

`0.600 > 0.5049` ⇒ **ADMITTED**. Unbounded new bandit HIGHs are admissible on a Python target whose tests pass and whose lint is clean. The only way a Python fix falls below S* is to break the suite or be lint-filthy. Pinned as a *documented* behaviour in `test_a_python_fix_with_green_tests_can_never_fall_below_s_star`, not silently.

**WHAT WOULD REFUTE THIS.** A real config with `sk_s_floor > 0.6`, or per-finding `model_params` that push `s_star` above 0.6. I checked: `sk_s_floor` defaults 0.0 and `model_params` is, per the runner's own comment at line ~11290, *"never populated"* — so `nu_b=0.05, nu_f=0.20, q=0.5, R=0.5` are the operating point.

**SEVERITY: HIGH**, deliberately **not fixed**: reweighting the effect gates changes which fixes are admitted on every Python target ever run. That is a founder ruling, not an assistant's.

---

# CAN A BAD FIX BE ADMITTED

**Yes. I constructed one and ran it.** This is the answer to §3.1, and the answer survives my own fix.

```
BAD-shell-HIGH   sk=0.6667  ADMISSIBLE  passes_S*=True
                 e4: 1 HIGH/0 MEDIUM (baseline: 0H/0M, new: 1H/0M)
```

The fix injects `subprocess.call(cmd, shell=True)` — arbitrary shell execution, bandit HIGH — into a fenced listing, and it is **ADMITTED and clears the corrected break-even**.

**The derivation, not a vote.** On a prose target `e2_regression` is unavailable, so `W = 1.0 + 2.0 = 3`:

```
E = (1/3)·e3 + (2/3)·e4
e4 = max(0, 1 − 0.5·H_new − 0.2·M_new)
S*_corrected = 0.50493   (nu_b=0.05, nu_f=0.20, q=0.5, R=0.5, s_floor=0)

Admission ⇔ 1/3 + (2/3)·e4 ≥ 0.50493 ⇔ e4 ≥ 0.25740
                                     ⇔ 0.5·H + 0.2·M ≤ 0.74260

H=1, M=0 → e4=0.5 → sk=0.6667 → ADMITTED   ← the shell-injection fix
H=1, M=1 → e4=0.3 → sk=0.5333 → ADMITTED
H=1, M=2 → e4=0.1 → sk=0.4000 → rejected
H=2, M=0 → e4=0.0 → sk=0.3333 → rejected
```

**One new bandit HIGH is not enough to reject.** Two are.

**What my fix did and did not change here.** Pre-fix, the *only* thing separating good from bad was e4, because e3 was pinned — and pre-round-12 the ranking was *inverted* (`sk=1.0000` for the `rm -rf` fix against `0.6667` for a correct one, per the runner's own docstring). Post-fix the ordering is correct and e3 is live (`BAD-lint` 1.0 → 0.7333). **But both still clear the threshold.** The discrimination is ordinal, not decisive.

**And the A19 docstring's own headline number is the tell:** it cites `0.6667` as the score of *a correct prose fix*. Post-A19 the shell-injection fix scores exactly `0.6667`. The malicious fix now scores what the docstring uses as its example of an acceptable one. That coincidence is worth the founder's attention.

---

# FIGURES I RE-RAN

| Figure | Claimed | I measured | Verdict |
|---|---|---|---|
| e3 over `BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, whole vs extracted | 311 / 4 | **311 / 4** | **Exact.** |
| e4 on an injected HIGH | `e4 = 0.5` | **0.5** (`1 HIGH/0 MEDIUM`) | **Exact.** |
| e2 still unavailable on prose | stands | `"no test command configured"` | **Stands, correctly not claimed fixed.** |
| Flag reachable config → `compute_sk` (§3.5) | — | `RunnerConfig.from_dict` → **True**; `launcher_core.build_runner_config_from_dict` → **True** | **Reachable on both ingestion boundaries.** Not an addition nothing reaches. No shipped config sets it, so no measurement moves until he rules. |

**The one figure the brief does not state, and should:** the runner's baseline on that same document was **311**, not 4. Post-fix it is **4**. That is 307 diagnostics of free headroom a fix could previously consume.

**Proportions, with the second tool as required** (`scipy.stats.beta` Clopper–Pearson alongside Wilson):

```
fence shapes BROKEN, before fix   5/7=0.7143  Wilson95 [0.3589,0.9178]  CP [0.2904,0.9633]
fence shapes BROKEN, after fix    0/7=0.0000  Wilson95 [0.0000,0.3543]  CP [0.0000,0.4096]
mutants killed by the new test    4/4=1.0000  Wilson95 [0.5101,1.0000]  CP [0.3976,1.0000]
```

**I will not over-read these.** n=7 and n=4 give intervals too wide to support any claim beyond "the shapes I tested". The 7 shapes were chosen adversarially, not sampled — these are a census of a hand-picked set, and the interval is decoration on it. The load-bearing evidence is the per-shape table, not the proportion.

**Effect on `severity` / `sigma` / `gamma`:** `sigma ≡ s_k`, so F1 raised `sigma` by pinning e3 at 1.0 — every prose fix was scored as more correct than it was, which *lowers* `R_k` too fast through `compute_rk`. Findings closed on inflated `sigma` leave `R_k` understating residual risk. `severity` is untouched (S_k scores fixes, not findings). `gamma` is untouched directly, but F2 reaches it: A=0 rejections leave findings OPEN, they stay novel-eligible, and the novelty series that feeds `_estimate_gamma` never decays — the 2026-08-01 non-convergence signature.

---

# MUTATION EVIDENCE (§3B: the test must be able to FAIL)

Each fix hunk reversed one at a time against the real module, test re-run, module restored:

```
MUTANT APPLIED: M1_baseline_ungated        -> 3 failed, 14 passed
MUTANT APPLIED: M2_narrow_fence            -> 1 failed, 16 passed
MUTANT APPLIED: M3_absolute_hard_gates     -> 1 failed, 16 passed
MUTANT APPLIED: M4_allow_code_deletion     -> 1 failed, 16 passed
=== RESTORED ===                              17 passed in 2.87s
```

**M2 killing only 1 test is itself a result, and I looked rather than assumed.** With the narrow fence restored, `test_a_correct_fix_on_an_indented_fence_is_not_rejected` still passes — because the F3 guard catches it: the original listing does not parse either, so g1/g2 abstain. Defence in depth, confirmed by accident and then deliberately.

**Two of my own tests were wrong on first run and I fixed the tests, not the assertions.** `2 failed, 15 passed` initially: (a) `_capture_baseline(listing, source_path=TARGET)` re-gated already-extracted Python under a `.md` path and found no fence — extraction is not idempotent w.r.t. path; the runner calls it once on the raw target, so this is a test artefact, now documented in the test. (b) An assertion whose premise was simply false (`x = (` inside a closed fence *is* a syntax error, so 0 was right). Both are in the file's history of this turn, stated rather than buried.

**Regression, 11 files touching `_capture_baseline` / the effect gates / `_gateable_source` / `compute_sk` / `resolve_target_kind`:**
```
449 passed, 1 warning in 25.27s
```
Blast radius on Python targets is nil by construction and pinned by `TestPythonTargetsAreUntouched`: `_gateable_source` returns Python unchanged, so `_capture_baseline` on a `.py` target is byte-identical to before. Pure prose with no listing still returns **NO_SCORE** with the flag ON — the founder's own distinction, preserved.

---

# WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

I did not read the other seats' round-13 output; this is my independent verdict.

I disagree with the **round-12 tracker entry**, on the record at `experimental_notes/CDSFL_MASTER_TASK_LIST.md:493`, on three points:

1. **"Two of the short-circuit's 3 stated reasons ... are repaired."** One and a half. e4 is genuinely repaired — I confirmed `e4 = 0.5` on a real HIGH. **e3 is not.** It was moved from "reads prose as Python" to "compares listings against prose", which is the same disease with a better cover story: pre-fix, `7 total, 0 new (baseline: 66)` scored **1.0**. The entry's own standard — *"structurally incapable of failing, which is worse than unavailable"* — condemns the state it shipped.

2. **"10 tests, 4 mutations verified red."** I believe the count; the mutations did not cover the *baseline* path, which is why F1 survived them. A mutation suite that cannot reach the defect is the project's own vacuous-test failure mode — 8 found that way historically, 7 in the last two days per the brief. This is the 16th.

3. **"A Python target is untouched by construction — so no existing measurement can move."** True for round 12 and true for my fix. But it is stated as though it bounded the risk, and it does not: the uncovered surface was never Python targets, it was the *prose baseline*, which round 12 did not touch and therefore did not test.

I **agree** with the entry, against any instinct to find more fault, on: default-OFF is right; pure prose returning NO_SCORE is right and is his distinction, not a hedge; `e2_regression` is honestly not claimed fixed; and reading the flag with `getattr` so an older config cannot break the call is the correct defensive choice.

---

# WHAT I DID NOT CHECK

- **The full suite.** Brief forbade it (8+ min). 449 tests over the 11 files touching this machinery. A failure in an untouched file is possible; I have no evidence either way.
- **`bench/reference_runner.py`** carries its own `_capture_baseline` at line 2663 with, as far as I can see from the call at 3490, **the identical defect**. I did not fix it — I do not know whether that runner is live or archived, and fixing a dead path is the "addition nothing reaches" failure in reverse. **Flagged for the founder: if v2 is live, F1 is open there.**
- **The F3 guard's coarseness.** It asks "did it parse before", not "did it fail the *same way*". A fix that breaks a listing differently from how it was already broken is swallowed. Stated as residual, not closed.
- **Whether any real exam target uses `~~~`, CRLF, or list-nested fences.** I fixed the extractor against seven constructed shapes; I did not survey the corpus. If none of them occur in practice, F2's severity drops to the NO_SCORE-silently cases only — though the fix costs nothing either way.
- **`gamma` end to end.** I derived the path from A=0 rejections → findings stay OPEN → novelty series does not decay. I did not run a multi-round experiment to measure it. Marked **[SPECULATIVE]** on the magnitude; the mechanism is `_estimate_gamma`'s dependence on the novelty counts and is not speculative.
- **`pycon` extraction.** Deliberately left excluded. That is a decision, not an omission, but it means doctest-style STEM documents get NO_SCORE rather than a score.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 56 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round13_2026-09-11) -->

**VERDICT: READY WITH EXCEPTIONS** — the A19 flag is sound in intent, reachable from both config ingestion paths, and correctly preserves the founder's "purely prose → NO_SCORE" distinction; but as dispatched it contained one critical hole (fixed in my tree, red/green tested) and one vacuous pinning test (repaired). Exceptions are two founder-call items: markdown-dialect fragilities I report but do not fix, and the `sk_s_floor=0.0` policy that makes effect-gate rejection on prose nearly impossible.

## FILES I LEFT IN THE TREE

- `bench/reference_runner_v3.py` — 2 edits: `_capture_baseline` now routes through `_gateable_source` (the fix); `_MD_PY_FENCE` tolerates info strings and CRLF (with `pycon` still excluded).
- `bench/tests/test_sk_baseline_gates_same_substrate_2026-09-11.py` — NEW, 8 tests, all green; 4 fail against the unfixed runner.
- `bench/tests/test_prose_listings_are_scoreable_2026-09-11.py` — repaired the vacuous fixture and strengthened the flag-on assertion.
- `scratch_seat/demo_bad_fix_admitted.py` — the Section 3.1 attack, runnable; `scratch_seat/reference_runner_v3.py.ORIG` — pre-fix snapshot for diffing.

## FINDINGS

**F1 — The S_k baseline is captured over the WHOLE document while the repaired gates score the extracted listings, so with the flag ON, e3 was structurally incapable of failing — the exact defect class A19 claimed to repair, moved one function upstream.**
- **WHERE**: `_capture_baseline` (was line 10282), called by `run_experiment` at line 12768 with raw `target_text`; vs `_run_effect_ruff`/`_run_effect_bandit`, which now extract.
- **EVIDENCE** (unfixed runner, `python3 scratch_seat/demo_bad_fix_admitted.py`):
  ```
  BASELINE over whole document: {'ruff_violations': 311, 'bandit_findings': {'high': 0, 'medium': 0}}
  tristate: ADMISSIBLE sk: 1.0 A: 1 E: 1.0
    e3_ruff -> {'score': 1.0, 'detail': '10 total, 0 new (baseline: 311)'}
  ```
  That is a **perfect score for a fix replacing a working listing line with five undefined names and an unused `pickle` import**. Derivation: e3 = max(0, 1 − max(0, T − 311)·0.1) < 1 requires T ≥ 312 total diagnostics *over the listings* — a fix must add ≥308 new defects before the gate loses its first 0.1. Confirmed mechanically: 310 undefined names in one listing → `e3=1.0 (310 total, 0 new (baseline: 311))`. Sweep: 20/20 escalating bad fixes scored e3=1.0; Wilson 95% [0.8389, 1.0000] by closed form AND statsmodels (agree to 4 dp). Mirror defect on bandit: whole-document baseline is unparseable → 0H/0M, so a pre-existing listing HIGH is billed as NEW to any innocent fix.
- **FIX**: `_capture_baseline` extracts via `_gateable_source` first; nothing gateable → both baselines stay `None` (gates say "baseline unavailable" → ESCALATE, never a fabricated 0/0). Identity on `.py` by construction.
- **TESTED**: red run against ORIG: `4 failed, 1 passed` (only the .py blast-radius test passes, as it should — quoted above); green: `5 passed`. Post-fix: bad fix sk=0.8 (`10 total, 6 new (baseline: 4)`), evil `shell=True` fix sk=0.6333 (e4: `new: 1H/0M`), good fix sk=1.0 — ranking restored. Blast radius: 320 tests across the sk/target-kind/hard-gate/immune-memory/ouroboros suites pass.
- **WHAT WOULD REFUTE THIS**: a call path that captures the baseline over the listings that I missed (there is exactly one call site, line 12768, and it passes raw text); or evidence that prose runs never reach e3 with the flag ON (they do — demonstrated end-to-end through `compute_sk`).
- **SEVERITY**: CRITICAL — admits a bad fix at an unimprovable score; the inflated sk then enters `compute_rk_with_eta_channel` as the fix-efficacy term.

**F2 — The shipped A19 pinning test is vacuous: its fixture uses 7-angle git-conflict markers, which `parse_search_replace_blocks` parses to ZERO blocks, so the flag-on test asserted on the parse-error path and no gate ever ran.**
- **WHERE**: `bench/tests/test_prose_listings_are_scoreable_2026-09-11.py`, `FIX` constant + `test_a_listing_bearing_target_is_scored`.
- **EVIDENCE**: `parse_search_replace_blocks("<<<<<<< SEARCH\n...=======\n...>>>>>>> REPLACE")` → `[]`; `compute_sk(FIX, …, score_prose_listings=True)` → `ESCALATE {'error': 'no SEARCH/REPLACE blocks found'}` — which satisfies `tristate != "NO_SCORE"` without a single gate running. The runner's own prompt (line 12823) specifies `<<<< SEARCH file_path`. This is the 8-vacuous-mutation-tests class the brief warns about.
- **FIX**: 4-angle fixture + assertions `blocks_parsed > 0`, `tristate == "ADMISSIBLE"`, and e3/e4 scores non-None with a real baseline. File now `10 passed`.
- **WHAT WOULD REFUTE THIS**: the parser accepting 7-angle markers somewhere I didn't find — I tested the exact shipped string and it returns `[]`.
- **SEVERITY**: HIGH — the sole test pinning A19's headline claim proved a parse error, not scoring.

**F3 — Fence extraction silently misses CRLF documents and info-string fences; blockquoted/indented fences extract garbage.**
- **WHERE**: `_MD_PY_FENCE`, line 9943.
- **EVIDENCE** (probe against unfixed code): `crlf -> NOT EXTRACTED`, `info_string -> NOT EXTRACTED`, `tilde -> NOT EXTRACTED` (feature silently defeated → NO_SCORE); `blockquote -> SYNTAX ERROR (A=0)`, `indented -> unexpected indent (A=0)`, `fragment -> (A=0)` — every fix on such a target REJECTED, the 2026-08-01 fifty-rejection class resurrected behind the flag. `pycon` correctly excluded. `unclosed_spill` fails closed (A=0). A genuinely-unclosed FINAL fence's payload (`os.system(...)`) escapes all gates while earlier listings keep the target scoreable.
- **FIX**: CRLF + info-string tolerance applied and tested (3 new tests; `pycon` exclusion pinned). `~~~` fences, blockquote/indent stripping, and unclosed-final-fence handling **reported, not fixed** — supporting a markdown dialect properly wants a real fence scanner, and that scope is the founder's call. Note the unclosed-fence escape is power-equivalent to writing in prose, which the gates never scan by design — but the gates' silence may be read as "scanned"; worth a sentence in the run report when listings are gated.
- **WHAT WOULD REFUTE THIS**: measurement that real CDSFL prose targets never carry CRLF/info-string/quoted fences. The measured spec file uses plain LF fences, so the *current* corpus is unaffected; the defect fires on the next Windows-authored document.
- **SEVERITY**: MEDIUM (conservative failure directions, but wrong verdicts of both kinds: NO_SCORE for scoreable targets, REJECTED for unassessed fixes).

**F4 — With `sk_s_floor=0.0` (every shipped sk-enabled config) the two-gate prose mean can barely reject anything. Derived, not asserted.** E_prose = (1·e3 + 2·e4)/3. With bandit clean, E ≥ 2/3 even at e3=0. The corrected threshold at the defaults every finding actually receives (nu_b=0.05, nu_f=0.20, q=0.5, R=0.5) is S* = 0.5049 (computed via `check_sk_threshold_corrected`; the shipped checker returns 0.0). Hence: **ruff alone can never reject on prose** (0.667 > 0.505); one new bandit HIGH still passes (E=0.667); rejection requires ≥2 new HIGHs (E=0.333) or 1 HIGH + ≥7 new ruff violations (E=0.433). Against 5-gate Python weighting {2,1,2}/5, dropping e2 renormalizes to {1,2}/3 — a HIGH costs 0.333 of E on prose vs 0.2 on Python, so per-gate failures weigh *more*, but the absent regression gate removes the only correctness evidence: **S_k on prose is a lint/security non-regression instrument, not a correctness instrument; correctness stays with the falsifier path.** Recommendation (founder's call, not mine to set): prose-scoring runs should carry a non-zero `sk_s_floor`, and the run report should say which gates contributed. SEVERITY: MEDIUM, policy.

**Effect on the instruments** (Section 3B): `severity` — untouched; sk does not enter severity. `sigma`/S_k — sk is the efficacy term in `compute_rk_with_eta_channel`; pre-fix, garbage fixes carried σ=1.0 and drove R_k down on fabricated evidence; post-fix they carry 0.8/0.633. `gamma` — the two-sided gate reads critical density; a finding falsely resolved by an sk=1.0 garbage fix leaves the open-critical count it feeds, so the pre-fix hole was a path to convergence on a corrupted registry. My fix narrows that path; it does not change the gamma thresholds themselves.

## CAN A BAD FIX BE ADMITTED

**As dispatched: YES, at sk=1.0000 ADMISSIBLE, and it also passes the corrected threshold (0.5049 at defaults).** Ran: `compute_sk` with the runner's real baseline (311) on `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, flag ON, fix = five undefined names + unused import → `e3: 10 total, 0 new (baseline: 311)`, sk=1.0. **After my fix: the same fix scores 0.8 and a `shell=True` injection 0.6333** — the gates fail and rank correctly — but both remain tristate-ADMISSIBLE and threshold-passing at `s_floor=0.0` (see F4). Tools decided all of the above; every number quoted is from an executed run.

## FIGURES I RE-RAN

- `scripts/archived_falsifier_rejections_2026-09-10.py`: **2/640 = 0.3125%**, Wilson 95% [0.0857%, 1.1322%] (statsmodels), Clopper–Pearson cross-check agrees to 1.7e-18. Matches the brief.
- `scripts/ruled_items_are_accounted_2026-09-11.py`: **0/15 = 0.0000% unaccounted**. Matches the brief.
- The 311-vs-4 measurement: re-derived live — whole-document baseline 311, listing-substrate baseline 4.

## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

With the A19 author's dispatch note: (1) "The gates must be able to fail — e4 = 0.5 on a real HIGH" was measured with a **hand-supplied** baseline, not the baseline `run_experiment` actually captures; with the real baseline, e3 could not fail at all (F1). The e4=0.5 claim itself replicates. (2) The claim that the flag is "wired" was pinned by a test that never exercised the wiring past the parser (F2). (3) The claim "half the machinery repaired, the other half never handed the extractor" was itself incomplete — the *baseline*, a third piece of the same machinery, was never handed it either. I have no other seat's output to dispute.

## WHAT I DID NOT CHECK

The full test suite (per dispatch rule; 566 targeted tests run instead). `_run_effect_regression` on a prose target with a configured `test_cmd` (writes markdown into a repo sandbox — untested path, currently unreachable since no prose config sets `test_cmd`). `detect_target_kind` edge: a PYTHON-kind target at a non-`.py` path would send hard gates through fence extraction — not audited. `bench/tests/test_rejection_reasons_reach_the_panel.py` also uses 7-angle markers — possibly intentionally, not audited. Whether any archived report replays differently: none should — no completed run ever had the flag ON, the `.py` substrate is byte-identical, and the only flag-OFF delta is the baseline log line at 12769 now printing listing-based numbers on prose targets.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round13_2026-09-11/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
