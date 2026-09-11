# Panel Round 8 — FULL RECORD, unfiltered

Record written 2026-09-11T09:40:55+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 8 reviewed the figures and instruments behind several closed entries, at a point where the list was closing entries quickly and the risk was a correct conclusion resting on a wrong number.

## What the round found, and 3 of the corrections landed on CC1's own work

**A MAXIMALLY-SELECTED STATISTIC REPORTED AS A SINGLE TEST (cc2).** Entry 0.2's change-point analysis searched 17 candidate dates and reported the minimising Fisher exact p as though one test had been run. Corrected by the union bound — Šidák correctly rejected, because the nested cuts share data and are not independent — giving **Bonferroni p = 3.738445e-13**, with a permutation test over 2000 shuffles at **p <= 4.9975e-04**, a resolution bound at 1/(B+1) since 0 shuffles reached the observed minimum. **The conclusion is unchanged; the number was overstated by exactly the factor 17.**

**"DEAD" OVERSTATED WHAT THE DATA SHOW (cc2).** The most recent attempt of ANY kind, 2026-09-09 09:07:25, SUCCEEDED. The entry had quoted the most recent FAILURE at 09:02:48. The defensible claim is *availability too low to depend on*, not *never works*.

**A CONTROL OF CC1'S THAT WAS A TAUTOLOGY (cc2, severity 0.6).** `test_reverting_the_fix_reproduces_the_defect_exactly` compared `prior.alternative_text` with `fixed.alternative_text` — the same `str` object — so the assertion was `score_isomorphism(s, s) == 1.0`, a property of `score_isomorphism` and of nothing else, and it survived destroying the function it guarded. In the file whose own docstring says *"A falsifier that cannot fail confirms nothing"*.

**THE MATERIALITY SEARCH WAS TOO NARROW TO FALSIFY ITS OWN NULL (fable, severity 0.3).** The 690-candidate space was single-field equality only, so *"escalated AND not resolved"* — the claim's most natural reading — was inexpressible. Extended to 1,679 definitions: the triple is still NONE, and the withdrawal survived.

**A CAUTION THAT APPLIES TO THIS ROUND.** Until task A20 landed on 2026-09-11, all seats shared ONE writable sandbox and ran concurrently. Agreement between seats here is not evidence of independence.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 8: attack tonight's task-list work, and DELIVER YOUR FIX AS A FILE

<!-- figure: nu grid points whose verdict moves | scripts/nu_carries_complexity_moves_the_gate_2026-09-10.py | 570 -->
<!-- figure: post-mechanism missing falsifiers | scripts/missing_falsifiers_2026-09-10.py | 28 raised after it -->
<!-- figure: archived runs that cannot be checked | scripts/target_mutation_blast_radius_2026-09-10.py | 35 of 39 -->

## SECTION 0 — READ THIS FIRST. THE DELIVERY RULE.

**Founder ruling, verbatim, 2026-09-10:** *"they need to supply fixes, not just problems!"* and *"its fine to find problems, but you must also provide (tool verified) fixes in all cases"*.

**A finding without a fix is not a deliverable. A fix described in prose is not delivered either.** Measured across rounds 5 and 6: the seats handed back **0 source files**. The cause is mechanical — `bench/panel_sandbox.py:teardown` destroys the sandbox and `changes()` preserves only files still **inside the sandbox repository tree**.

**Write your fix INTO the sandbox repository tree, at the path it would live at, and leave it there.** Not `/tmp`. Edit existing files in place. Put a new test at `bench/tests/<name>.py`. Anything outside the tree is destroyed. You may write freely; it is a copy and the canonical tree is fingerprinted before and after.

## SECTION 1 — What landed tonight. 7 task-list entries.

**1. The commit hook could refuse every remaining commit and carried its own cure out of reach.** The Desktop-mirror drift guard went red; the stage that REPAIRS mirror drift was stage 6 of the same hook, below the exit. Fixed by ordering: the refresh is now stage 0, still unable to refuse a commit. Underneath it, **3 hand-written mirror tables existed and all 3 disagreed** — 3 names in `scripts/sync_desktop_mirrors.py`, 2 pairs in `bench/tests/test_documentation_drift_guards_2026-08-25.py`, 3 names again in `scripts/cdsfl_recover.py`. Union 4, intersection 1. All 3 keyed on a bare filename and so could not express `RUNWAY_to_BR2_2026-08-18.md` → `~/Desktop/CDSFL_RUNWAY.md`. One table of pairs now, imported by all 3.

**2. R5a — the materiality population 11 / 6 / 2 is withdrawn.** `scripts/materiality_population_2026-09-10.py` enumerates every count the 3 archives can produce, 690 candidate definitions, and none reproduces the triple. Positive control: fed a triple that IS one measure (the archives' own escalated counts 0, 1, 6) the search must name `escalated == true`.

**3. R6 — blast radius.** 0 of 39 archived runs show a mutated target; **35 of 39 carry no instrument at all** and are reported as neither clean nor dirty. Question (b) is fully decidable and the answer is nothing needs reverting: all 3 observed rewrites of `bench/dm/_memory.py` appear in no commit on any ref.

**4. 4.3 / R11 — complexity reported, reaching no decision.** `result["target_complexity"]` in `bench/reference_runner_v3.py`. It goes to `gamma_input`, not nu, because **570 of 676** grid points in the reachable nu box give a different admission verdict. A near-miss: below `MIN_WINDOWS` the measuring function returns an ASSUMED beta of 0.5, and at the default window EVERY ordinary code target falls below it — `bench/dm/_memory.py` is 20,563 chars but only **1,485 tokens**, a 13.8:1 ratio against the module's assumed 4:1. The report would have carried `gamma_input` 0.5 in a field a reader takes as measured.

**5. 0.2 — the Wolfram route disabled, with the cut FITTED not chosen.** `change_point()` tries every candidate date and takes the split minimising Fisher exact p. A first version cut at the FIRST failure and got 2026-08-25, which is a 1-off blip with a success 19 seconds later.

**6. 2.2 — the missing-falsifier population was wrong by a factor of 29.** The naive sweep returns 817; the falsifier mechanism was built 2026-06-03, so **789 predate it**. Real population **28**. All 28 carry the verdict `UNTOOLABLE` and the first one examined was not: exp47 C0053 is a claim about 2 named functions in a module still in this repository.

## SECTION 2 — Attack these specifically

1. **The single mirror table.** I claim importing it into 3 consumers closes the gap. Does it? Is there a 4th consumer? Can a mirror be declared in a document and still escape both the guard and the refresher? `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py` claims to check both directions — break it.
2. **The R5a search.** 690 candidate definitions sounds exhaustive. Is it? Name a definition of "HIL residual" the search cannot express, and if you find one, ADD IT to `candidates()` and report what it yields.
3. **The `ASSUMED_DEFAULT` flag.** I key it on `n_windows >= MIN_WINDOWS`. I first keyed it on `r_squared > 0` and that was wrong — a perfectly saturated text has zero variance and returns `r_squared` 0.0 while gamma 1.0 is exactly right. Is the current key right? Construct a case where it lies.
4. **The fitted change point.** Minimising Fisher p over every candidate date is a multiple-comparisons procedure and I report the p-value as if it were a single test. That is a real statistical objection and I have not addressed it. **Address it, and deliver the corrected code.**
5. **The C0053 falsifier's control.** It reverts the fix by writing the pre-fix expression out in the test rather than monkeypatching the module. Is that a real revert, or does it test a copy of the logic instead of the logic?
6. **Anything in `bench/reference_runner_v3.py`'s new `target_complexity` block.** It runs inside the round loop on every run. Can it throw where I do not catch? Can it be slow on a large target?

## SECTION 3 — Use the harness

**Form your answer by RUNNING things.** Every script named above executes offline. Run them. If a figure in this brief does not reproduce, that IS the finding — say so and give the number you got.

Every claim you make must be executed or withdrawn. Every finding must arrive with a fix, in the tree, at its real path.

## SECTION 4 — What would refute YOU

State, for each finding you return, **what evidence would overturn it**. A finding that names no such evidence is an opinion, and this project does not act on opinions. If your fix rests on a measurement, name the measurement that would falsify it. If you cannot name one, say so and mark the finding as unfalsifiable rather than dropping it.

The same applies to disagreeing with me: if you think a claim in Section 1 is wrong, say what you ran and what it returned. "This looks wrong" is not a finding.

## SECTION 5 — When to stop

**Diminishing returns, which is this project's own criterion.** Stop when a further pass over the same material produces no new above-threshold finding. A finding is above threshold if missing it could cause a wrong number to reach the founder, a guard to pass something it should refuse, or a run to record a value it did not measure.

Do not pad to a count. 2 findings with working fixes beat 9 with none. Do not nitpick style, naming or comment density; every file here is deliberately over-commented and that is not a defect to report.

## SECTION 6 — The output shape, field by field

Return **Markdown**, in this order:

1. **`VERDICT`** — one of `SOUND`, `SOUND_WITH_CAVEATS`, `UNSOUND`, for tonight's work as a whole, in the first line.
2. **`FILES I LEFT IN THE TREE`** — a list of repo-relative paths you created or edited in the sandbox. If this list is empty, say `NONE` and explain why; an empty list with no explanation is a failed round.
3. **`FINDINGS`** — numbered. For each: **WHAT** (1 sentence), **WHERE** (`path:line`), **EVIDENCE** (the exact command you ran and its output, quoted), **FIX** (the path you wrote it to, and what it changes), **WHAT WOULD REFUTE THIS** (per Section 4), **SEVERITY** (0.0 to 1.0).
4. **`FIGURES I RE-RAN`** — each declared figure in this brief, the number you got, and whether it matched.
5. **`WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1`** — disagreement is preserved as information, never smoothed. If you agree with everything, say so explicitly; silent agreement is indistinguishable from not looking.
6. **`WHAT I DID NOT CHECK`** — the honest boundary of your pass.

Do not return a summary in place of the full output. The founder decides what matters, not the summariser.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 53 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round8_2026-09-10) -->

VERDICT: `SOUND_WITH_CAVEATS`

All three declared figures reproduced exactly. Tonight's substantive conclusions survive my pass — including the one I attacked hardest (the fitted change point), which survives correction by 12 orders of magnitude. Four defects found, all in the *measurement and verification machinery* rather than in the conclusions, all delivered as fixes in the tree.

## FILES I LEFT IN THE TREE

| Path | New/edited |
|---|---|
| `scripts/wolfram_route_health_2026-09-10.py` | edited — multiple-comparisons correction + current-state reporting |
| `bench/tests/test_change_point_multiple_comparisons_2026-09-10.py` | **new** — 6 tests |
| `bench/tests/test_falsifier_C0053_recidivism_2026-09-10.py` | edited — vacuous control replaced with a real revert |
| `bench/reference_runner_v3.py` | edited — `NO_TOKENS` third state in the `target_complexity` block |
| `bench/tests/test_target_complexity_no_tokens_2026-09-10.py` | **new** — 8 tests, lifts the real block by `ast` |
| `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py` | edited — false-red repair on the ordering test |

`43 passed, 1 skipped` across the four test files plus the drift guard (2 pre-existing failures unrelated to my edits — see §5).

---

## FINDINGS

### 1. The fitted change point reports `min_j p_j` over 17 tests as if it were one test — and it justifies a removal

**WHAT** `change_point()` searches every candidate cut and prints the minimising Fisher p as "Fisher exact p"; a minimum over m dependent tests is not a p-value, and this figure is what `.claude/CLAUDE.md` quotes to justify retiring the Wolfram route.

**WHERE** `scripts/wolfram_route_health_2026-09-10.py:217` (was: the bare `best["p"]` print in `main`)

**EVIDENCE**
```
$ python3 scripts/wolfram_route_health_2026-09-10.py
  fitted cut : 2026-09-04
  Fisher exact p = 2.199086e-14          # ← before my edit
```
The search space, counted:
```
$ python3 -c "...dated_attempts()..."
distinct dates: 18 ; candidate cuts tried (dates[1:]): 17
```
The inflation, measured on 400 null replicates (no change point, labels iid):
```
UNCORRECTED min-p rejects at 0.05 in 16.5%   <-- should be 5%
BONFERRONI       rejects at 0.05 in  1.8%
```
A 3.3× inflation of the stated error rate.

**DERIVATION** (union bound, no independence assumption — which is essential, since consecutive cuts share nearly all their data): Fisher's exact test is valid, so `P(p_j ≤ α) ≤ α` for each j. Then `P(min_j p_j ≤ α) = P(∪_j{p_j ≤ α}) ≤ Σ_j P(p_j ≤ α) ≤ mα`. Hence `p_adj := min(1, m·p_min)` satisfies `P(p_adj ≤ α) ≤ α`. Šidák's `1−(1−p)^m` is **invalid** here — it requires independence and would be anti-conservative on these nested splits. That is why the fix uses Bonferroni.

**FIX** `scripts/wolfram_route_health_2026-09-10.py` — extracted `_min_p_over_cuts()` so the observed and permuted statistics are *one function* (two implementations would calibrate the wrong quantity), then added `p_bonferroni` and a permutation test of the maximally-selected statistic. New output:
```
candidate cuts searched : 17  (this is a MAXIMALLY-SELECTED statistic, not a single test)
min Fisher exact p over those cuts = 2.199086e-14  <- NOT a p-value; do not quote alone
Bonferroni-corrected p  = 3.738445e-13  (= 17 x min p; valid under ARBITRARY dependence)
permutation p (B=2000) <= 4.9975e-04  [0 of 2000 shuffles reached the observed minimum]
```
**The conclusion is unchanged.** `3.74e-13` is still overwhelming. The number was wrong; the decision was right. Test: `bench/tests/test_change_point_multiple_comparisons_2026-09-10.py`.

**Sub-finding, same fix:** the log's **most recent attempt of any kind SUCCEEDED** — `2026-09-09 09:07:25`, `announcing WolframCloud: 3 tool(s)`. Entry 0.2 quotes the most recent *failure* (09:02:48) and concludes "dead". The last attach, five minutes later, worked. The script now prints this beside the retirement figure:
> *THE ROUTE'S LAST OBSERVED ATTACH SUCCEEDED. The post-cut rate is 'almost always fails', NOT 'never works'. A retirement argued from 'dead' is arguing something the data does not show; the defensible claim is availability too low to depend on.*

The additive standard permits removal only on a committed measurement showing dominance on a named property. Availability of 1/43 still dominates 0/43 in the sense that matters to that standard's wording — the retirement should be argued on the rate, not on "dead".

**WHAT WOULD REFUTE THIS** (a) A demonstration that the 17 splits are jointly independent, which would make Bonferroni the wrong correction and Šidák right — I derived they are not (they share data), but a formal argument that Fisher's conditional test at nested cuts is independent would overturn my choice of correction, though not the fact that a correction is needed. (b) A rerun of the null sweep showing the uncorrected minimum crossing 0.05 at ≈5% — that is exactly what `test_the_uncorrected_minimum_is_anticonservative` asserts against, and it would fire. (c) On the success: evidence that `announcing WolframCloud: 3 tool(s)` is emitted from cache rather than a live attach would kill the sub-finding entirely.

**SEVERITY 0.55**

---

### 2. The C0053 falsifier's "revert" control is a tautology — it passes with the fix destroyed

**WHAT** `test_reverting_the_fix_reproduces_the_defect_exactly` asserted `score_isomorphism(prior.alternative_text, fixed.alternative_text) == 1.0`, but both records are built by `_record(BODY, …)` so both attributes are the **same `str` object** — the assertion is `score_isomorphism(s, s) == 1.0`, a property of `score_isomorphism` and of nothing else.

**WHERE** `bench/tests/test_falsifier_C0053_recidivism_2026-09-10.py:151` (replacing the old control)

**EVIDENCE**
```
$ python3 - <<'EOF' ...
shipped control value: 1.0
  are the two args the SAME object? True
control passes with _recidivism_text destroyed: True
REAL revert -> gate rejection_reasons: ['recidivism_near_copy (jaccard_vs_prior_round_alt_0=1.000 >= 0.98)']
fix in place -> gate rejection_reasons: []
```
The control survives `_divergence._recidivism_text = lambda r: "TOTAL GARBAGE"`. It also short-circuits the mechanism: `parse_contrast_statement` never runs, so the **stripping step C0053 is entirely about** is never exercised by the control. To the founder's question 5 directly: **it is not a real revert. It tests a hand-constructed post-strip state, not the logic that produces it.**

This is the file whose own docstring says *"A falsifier that cannot fail confirms nothing"*, and it is a §10 category-3 defect (verification-integrity corruption) under CDSFL's own classification.

**FIX** `bench/tests/test_falsifier_C0053_recidivism_2026-09-10.py` — the control now rebinds the module-level `_divergence._recidivism_text` to the pre-fix expression (`_divergence.py:638-640` looks the name up on the module at call time, so the rebinding reaches the real call site) and demonstrates the defect **through `check_sibling_admissibility`**, the gate C0053 complains about. Undone in a `finally`, with a test asserting it was. Added a meta-control proving the new control responds to what `_recidivism_text` *does*, and a test pinning the old control's tautology so the account of why it was replaced is itself checkable. `9 passed`.

**WHAT WOULD REFUTE THIS** If `prior.alternative_text is fixed.alternative_text` ever evaluates False (different string objects with equal content), the old control would be comparing two objects and my "tautology" characterisation weakens to "trivially-true comparison" — `test_the_superseded_control_was_a_tautology` asserts the identity and would fail, forcing a re-read. If `check_sibling_admissibility` stops routing through the module-level `_recidivism_text` (e.g. it gets inlined or bound at import), my new control silently stops reverting anything — `test_the_control_would_notice_a_destroyed_fix` is the tripwire for that and would fail.

**SEVERITY 0.6**

---

### 3. `target_complexity` recorded `gamma_input: 1.0` beside prose asserting 0.5

**WHAT** The `ASSUMED_DEFAULT` flag is keyed correctly, but the two fields behind it describe only one of the two not-measured cases: when a target tokenises to nothing, `compute_gamma_input` returns early at `input_complexity.py:211` with `gamma=1.0` and never reaches the assumed-default branch at `:232`.

**WHERE** `bench/reference_runner_v3.py:13287` (the new `_no_tokens` line and the three fields below it)

**EVIDENCE** — the founder asked me to *construct a case where the flag lies*. Here it is:
```
$ python3 -c "compute_gamma_input('四七八九 五六 一二三'*500)"
CJK            tokens=0 n_windows=0 gamma=1.0 beta=0.0 r2=0.0
all stopwords  tokens=0 n_windows=0 gamma=1.0 beta=0.0 r2=0.0
short toks     tokens=0 n_windows=0 gamma=1.0 beta=0.0 r2=0.0
```
Running the **pre-patch block itself**, lifted from source by `ast`:
```
PRE-PATCH gamma_input : 1.0
PRE-PATCH fit         : ASSUMED_DEFAULT
PRE-PATCH reading     : ...gamma is the module's assumed default of 0.5...
```
`1.0` is the **extreme "maximally simple" end** of the scale, recorded for a target never measured, with prose beside it naming a different number. Reachable, not theoretical: `tokenize` keeps only `[a-zA-Z_][a-zA-Z0-9_]*` runs longer than 2 chars, so any CJK, RTL, minified or short-identifier target yields zero tokens.

**On the founder's actual question — is `n_windows >= MIN_WINDOWS` the right key? Yes, and I declare that sound.** Keying on `r_squared > 0` was correctly rejected (a saturated text legitimately returns `r_squared 0.0` with `gamma 1.0`). And with ≥3 windows `_fit_heaps` **cannot** reach its `(0,0,0)` sentinel: cumulative token counts strictly increase by construction, so `len(pairs) < 2` is unreachable and `denom` is a strictly positive variance of distinct logs. The key is right. Only the fields behind it were wrong.

**FIX** `bench/reference_runner_v3.py` — three states instead of two (`measured` / `NO_TOKENS` / `ASSUMED_DEFAULT`), and the `reading` now interpolates `round(_cx.gamma, 6)` rather than hardcoding `0.5`, so the prose cannot drift from the field again. Test: `bench/tests/test_target_complexity_no_tokens_2026-09-10.py` — which **lifts the real `if "target_complexity" not in result:` node out of `reference_runner_v3.py` with `ast` and executes it**, rather than retyping the logic. Retyping is exactly the defect in Finding 2, and I was not going to commit it in the same round I reported it. Non-vacuity proven above against the reconstructed pre-patch source: the shipped assertion `"0.5" not in reading` fails on it. `8 passed`.

**WHAT WOULD REFUTE THIS** If `input_complexity.compute_gamma_input` changes its empty-input return to `gamma=0.5`, the mismatch disappears and this finding is void — `test_and_the_module_then_returns_gamma_one_not_half` asserts the premise and would fail first, which is the design. If it can be shown the exam can never be dispatched against a zero-token target (a staging guard I did not find), severity drops toward 0 but the internal contradiction remains.

**SEVERITY 0.4**

---

### 4. The ordering test reported tonight's headline fix as BROKEN, for a reason that has nothing to do with ordering

**WHAT** `test_a_drifted_mirror_does_not_refuse_the_commit` asserts only `r.returncode == 0`, and cannot tell *which* refusal it observed; `hooks/pre-commit:40` refuses at "cannot find the repository root" before any mirror stage exists.

**WHERE** `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py:333`

**EVIDENCE**
```
$ python3 -m pytest bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py -q
E   AssertionError: a drifted Desktop mirror still refuses the commit:
E     pre-commit: cannot find the repository root. Refusing.
1 failed, 14 passed
```
That is a **false red on Section 1 item 1** — the guard built to confirm the ordering fix reported the ordering fix broken. This file's own comment, twelve lines above the assertion, says *"a test that turns unrelated guards red proves nothing about the ordering it claims to test"*; the earliest guard of all was the one it did not account for.

**FIX** `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py` — two additive repairs: (1) when the hook's own documented precondition is unmet, **skip with the reason named**, gated on the literal refusal string **and** on `.git` being genuinely absent so it cannot fire on a real checkout; (2) when the hook refuses for any other reason, the message now names **which stage** refused. Both verified:
```
# no .git:
SKIPPED [1] ...: the pre-commit hook refuses at hooks/pre-commit:40 before any
mirror stage runs, because this tree has no .git directory...
14 passed, 1 skipped

# with .git present — the skip is proven unreachable:
SKIPPED present with .git existing: False
E   AssertionError: the hook refused the commit. Stage 0 (the Desktop mirror
    refresh) did NOT run, so the refusal came from BEFORE the mirror refresh
```

**WHAT WOULD REFUTE THIS** If `hooks/pre-commit` gains a `.git`-independent root detection, the precondition is always satisfiable and the skip becomes dead code — which the additive standard forbids, and this finding should then be reverted rather than kept. If someone shows a path where a *genuinely drifted mirror* produces the literal string `"cannot find the repository root"`, my skip would hide a real failure and the fix is actively harmful; I searched `hooks/pre-commit` and found that string only at :40, above all mirror logic, but I did not exhaust the scripts it invokes.

**SEVERITY 0.35**

---

## FIGURES I RE-RAN

| Figure | Declared | I got | Match |
|---|---|---|---|
| nu grid points whose verdict moves | 570 | **570 of 676 (84.3%)**; 645/676 over `[0,1]²` | ✅ exact |
| post-mechanism missing falsifiers | 28 | **28** (789 predate 20260603; 817 naive) | ✅ exact |
| archived runs that cannot be checked | 35 of 39 | **35 of 39**; 0 mutated, 0 needing revert | ✅ exact |
| Wolfram pooled rate (0.2) | — | **43 of 64 = 67.19%**, cut `2026-09-04`, `1/21` → `42/43`, p `2.199086e-14`, OR 840 | ✅ reproduced, then corrected (Finding 1) |
| materiality population (R5a) | 690 defs, none reproduces 11/6/2 | reproduced; positive control names `escalated == true` | ✅ |
| `_memory.py` token ratio | 20,563 chars / 1,485 tokens ≈ 13.8:1 | reproduced; `gamma_input` **0.394127**, `fit: measured` | ✅ |

---

## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

**I do not disagree with any Section 1 conclusion.** Every figure I could run, ran and matched. The four defects above are in the machinery that produces and checks the figures, not in the figures.

**Two points of friction, stated rather than smoothed:**

1. **On "the route is dead" (0.2).** The most recent attempt in the log succeeded. The change-point analysis is sound and the availability argument is sound; the word "dead" is not what the data shows. I have made the script say so at the point of the recommendation. This does not change the retirement decision, but the additive standard is specific about what a removal must rest on, and it should rest on `1/43`, not on "dead".

2. **Another seat broadened my exception fix while I was working.** I narrowed `except (OSError, ValueError)` → `+ ArithmeticError`; a second round-8 seat broadened the same clause to `except Exception` with the stronger reasoning that anything unnamed falls through to the outer integrity handler and blinds the target-hash detective control before it records — *"35 of 39 archived runs already carry no target hash; this path must not create more."* **Their fix dominates mine on a named property (blast radius of an uncaught class) and I withdraw the `ArithmeticError` narrowing as superseded.** My `test_an_arithmetic_failure_is_caught_rather_than_killing_the_run` passes unchanged under their broader clause and now serves as the executed check on *their* fix — which is what an addition being reached looks like.

---

## WHAT I DID NOT CHECK

- **Section 2 item 2 (the R5a `candidates()` search).** I ran `scripts/materiality_population_2026-09-10.py` and reproduced its conclusion, but I did **not** audit the 690 definitions for expressiveness and I did **not** find a definition the search cannot express. I ran out of budget before opening `candidates()`. This is the one Section 2 item I am returning unanswered — flagged rather than dropped.
- **Section 2 item 1, the "4th consumer" question.** I confirmed three consumers import `sync.MIRRORS` (`test_documentation_drift_guards_2026-08-25.py:138-141`, `cdsfl_recover.DESKTOP_MIRRORS`, the sync script itself) and found no fourth in a repo-wide `--include=*.py,*.sh` sweep. I did **not** check whether a mirror can be *declared in a document* and escape both guard and refresher — the founder's sharper sub-question. Unanswered.
- **The 2 pre-existing failures in `test_documentation_drift_guards_2026-08-25.py`** (`CDSFL_MASTER_TASK_LIST.md` 150,312 vs 153,501 bytes; `CDSFL_Consolidated_Plan_2026-04-21.md`). These are the *sandbox copy* drifting against the founder's *live* Desktop and are not caused by my edits. I did not investigate whether they indicate real drift or sandbox staleness — I believe staleness, but I did not verify it, so I am not asserting it.
- **The remaining 27 missing falsifiers** from task 2.2. I verified the population is 28 and that C0053's is the one already written; I wrote none of the other 27.
- **Full test suite.** Per the dispatch rule, targeted runs only. My edits touch `bench/reference_runner_v3.py`, which many tests import; I did not run its full dependent set.
- **Whether `math.exp` in `_fit_heaps` can actually overflow in practice.** I argued the path is expressible (`:168` uses the unclamped `beta`) and tested that the handler catches it, but I did not construct a real target that triggers it, so I make no claim that it is reachable.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 81 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round8_2026-09-10) -->

All evidence is in. Final report.

---

# VERDICT: SOUND_WITH_CAVEATS

Tonight's seven entries are substantially sound — all three declared figures reproduce exactly, the R5a withdrawal survives a strictly stronger search, and the change-point objection was real but does not change the retirement conclusion. The caveats are load-bearing: entry 1's closure claim ("one table, imported by all 3, gap closed") is **refuted by a fifth declared, existing, currently-diverged Desktop mirror** that escaped both directions of the new test, and the 4.3 fix landed mid-round with its own paired guard broken.

Note on concurrency: another seat edited this same sandbox during my pass (runner, wolfram script, C0053 test). I verified their work by execution instead of duplicating it, repaired the guard their fix broke, and overrode one of their choices (stated in §5).

## FILES I LEFT IN THE TREE

1. `scripts/sync_desktop_mirrors.py` — added the 5th mirror pair with provenance comment
2. `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py` — expected set 4→5; declaration regex widened; docstrings updated
3. `scripts/materiality_population_2026-09-10.py` — negation + HIL-conjunction candidate families added to `candidates()`
4. `bench/reference_runner_v3.py` — complexity-block `except` broadened to `Exception` (over the other seat's `ArithmeticError`)
5. `bench/tests/test_target_complexity_is_reported_2026-09-10.py` — paired guard repaired to hold the three-state `fit` invariant

## FINDINGS

**F1 — A declared, existing, diverged Desktop mirror escapes the table and both directions of the new test.** *(severity 0.7)*
- **WHAT:** `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` → `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md` is declared three times in the notes (tracker item C3 says verbatim "Mirrored \`…\` → \`~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md\`"), the Desktop copy exists **now**, is **diverged now**, and `Document_Estate_Audit_2026-08-06.md:421` records the document as CORE/KEEP_AND_CONVERT — a live instruction ("brief any panel from there, never from this section"). It is in no table; nothing refreshes or guards it. This is the exact failure class entry 1 claims closed, recurring while the closure was being written.
- **WHERE:** `scripts/sync_desktop_mirrors.py:63` (table), `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py:131` (regex)
- **EVIDENCE:** `md5 -q` canonical/sandbox/Desktop → `b515c9dd… / b515c9dd… / 8ad4019e…` (real divergence, not a sandbox artefact; audit at :421 says the repo copy carries a 2026-08-05 `_suppression.py` correction the Desktop never received). The old regex against C3's phrasing: `current regex matches C3 declaration: False` — it required the Desktop path within 20 **non-backtick** chars of "mirror", and C3 puts the backticked repo path there first. My widened regex (`[Mm]irror[^\n]{0,120}?` + backticked path), enumerated over all notes before shipping, yields **exactly the 5 real mirrors, zero false positives**.
- **FIX:** files 1 and 2 above. `python3 scripts/sync_desktop_mirrors.py --check` now reports: `CDSFL_Consolidated_Plan_2026-04-21.md: diverged, canonical is +2,606 bytes`. The next commit's hook stage 0 repairs it; until then the drift guard is correctly red for this mirror on the founder's machine — that is the guard working, not a regression. 9/9 `TestTheSyncWorks` pass, 2/2 `TestTheRestoreCanSeeThem` pass.
- **WHAT WOULD REFUTE THIS:** evidence the founder ruled this mirror retired/archival (a dated ruling superseding the audit's KEEP_AND_CONVERT), or a demonstration that my widened regex matches a `~/Desktop/*.md` phrase in the notes that is not a real mirror declaration (re-run my enumeration; it currently yields exactly 5).

**F2 — The 4.3 fix landed with its paired guard broken.** *(severity 0.45)*
- **WHAT:** the other seat's (correct) three-state `fit` fix (`measured`/`NO_TOKENS`/`ASSUMED_DEFAULT`) changed the exact source line the guard test pins, turning `test_an_assumed_value_cannot_be_read_as_a_measurement` red — and the hook runs the guards, so a red guard refuses commits; the conftest also flagged tasks 4.3/R11 as "DONE entries whose evidence failed".
- **WHERE:** `bench/tests/test_target_complexity_is_reported_2026-09-10.py:90`
- **EVIDENCE:** `pytest … test_target_complexity_is_reported_2026-09-10.py` → `1 failed, 9 passed`; the failed assert is the two-state exact string. After my repair: `10 passed in 4.43s`.
- **FIX:** file 5 — asserts the three-state form and that `NO_TOKENS` is distinguished from `ASSUMED_DEFAULT` (the strengthened invariant, not a loosening).
- **WHAT WOULD REFUTE THIS:** showing the guard was green against the fixed runner before my edit (re-run the file at the pre-edit runner state; it was not).

**F3 — Zero-token targets recorded gamma_input 1.0 beside prose claiming 0.5** *(convergent; severity 0.35)* **and the informative block could still blind the integrity control** *(my residual)*.
- **WHAT:** I demonstrated independently (`compute_gamma_input` on a digits/short-token text → `tokens: 0, gamma 1.0, n_windows 0`) that the `ASSUMED_DEFAULT` reading hardcoded "0.5" beside a field holding 1.0 — the extreme "maximally simple" end, for a target never measured. The other seat found and fixed the same defect (NO_TOKENS state) while I was verifying; convergent finding, their fix verified. Residual: their `except (OSError, ValueError, ArithmeticError)` still lets `MemoryError`/`RecursionError`/`TypeError` fall to the outer handler at `reference_runner_v3.py:13360`, which returns **before** `target_hashes` is recorded — an informative statistic able to blind the detective control, in a project where 35/39 archived runs already carry no target hash.
- **WHERE:** `bench/reference_runner_v3.py:13335` (except clause)
- **EVIDENCE:** control-flow read of the block: complexity computation sits above `result.setdefault("target_integrity_events", [])` and hash recording, inside the same outer `try`. Perf half of attack 6 also executed: 41 ms on the 776KB runner itself, 0.46 s on a synthetic 7.8MB target, once per run — not slow.
- **FIX:** file 4 — `except Exception` with the error still recorded loudly in `result["target_complexity"]["error"]`.
- **WHAT WOULD REFUTE THIS:** a demonstration that no `Exception` subclass outside the three named can escape `read_text`/`tokenize`/`compute_gamma_input` on any byte sequence — I could not construct that proof, and the containment costs nothing.

**F4 — The R5a search could not express the claim's own most natural meaning; extended, the withdrawal survives and sharpens.** *(severity 0.3)*
- **WHAT:** the 690-candidate space is single-field-equality only — no negation, no conjunction. "HIL residual" most naturally means `escalated AND not resolved`, which was inexpressible; the null result was weaker than it read.
- **WHERE:** `scripts/materiality_population_2026-09-10.py:61` (`candidates()`)
- **EVIDENCE:** base run reproduced (187+204+299 = 690, NONE). After my extension: **1,679 definitions** (233+594+852), triple still **NONE**. Sharpener: `escalated == true AND status != "CLOSED"` yields **exactly 2 for exp47** (matching its claimed 2), **1 for exp48** (claimed 6), and is inexpressible for exp49 (no escalation fields in its archive). Even granting the claim its best reading, it matches 1 run of 3. Paired test `test_materiality_population_2026-09-10.py`: passes (23 passed with the wolfram tests).
- **FIX:** file 3.
- **WHAT WOULD REFUTE THIS:** a definition family still outside the space (e.g. three-way conjunctions, cross-run joins, or answer-key-dependent adjudication for the two exam runs) shown to yield 11/6/2 — the exam-run half of that is the brief's own "innocent reading" and remains open for exp48/49 only, never for exp47's code target.

**F5 — Verified, not duplicated: the change-point correction (attack 4) and the C0053 through-the-gate control (attack 5), both delivered by the other seat, are sound.**
- **EVIDENCE (change point):** ran `scripts/wolfram_route_health_2026-09-10.py` on the real logs: 17 candidate cuts; min Fisher p 2.199086e-14 now labelled "NOT a p-value; do not quote alone"; **Bonferroni 3.738445e-13** (union bound — valid under the arbitrary dependence these nested cuts have; Šidák correctly rejected as anti-conservative); **permutation p ≤ 4.9975e-04** (0 of 2000 shuffles, `<=` with (1+hits)/(1+B), correctly labelled a resolution bound). The uncorrected number was overstated by exactly the factor m=17; the retirement conclusion is unchanged. Derivation checked line-by-line: correct.
- **EVIDENCE (C0053):** the brief's question 5 answer is **yes — the original control tested a copy of the logic**: it re-evaluated `score_isomorphism(prior.alternative_text, fixed.alternative_text)` inline, exercising the comparison expression but never the gate at `_divergence.py:648`, so a gate whose rejection depended on anything beyond the score would have escaped it. The other seat's added control monkeypatches `_recidivism_text` and drives `check_sibling_admissibility` itself, with a `finally` restore and a destroyed-fix probe. Ran the file: **9 passed**.

## FIGURES I RE-RAN

| Declared | Got | Match |
|---|---|---|
| 570 of 676 nu grid points move the verdict | 570 of 676 (84.3%); [0,1]² box: 645 of 676 | ✓ |
| 28 missing falsifiers post-mechanism | 789 pre-date 2026-06-03, **28** after; all UNTOOLABLE; 27 remaining | ✓ |
| 35 of 39 runs cannot be checked | **35 of 39** no hash; 0 mutated; 0 rewrites reached any commit; nothing to revert | ✓ |

Also re-ran: the R5a base search (NONE, as claimed), the wolfram pooled rate (43 of 64, cut 2026-09-04, odds 840 — matches `.claude/CLAUDE.md`).

## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

- **With CC1 (entry 1):** "one table of pairs now, imported by all 3" was presented as closing the gap. It did not — F1 is the same failure class, live, found by widening the search the entry's own test used. The claim "the founder reads 4 files from his Desktop" is an undercount; it is at least 5.
- **With the other seat:** their `ArithmeticError` broadening of the complexity-block except is insufficient for the reason in F3; I overrode it to `Exception` in the shared tree. If they held a reason to enumerate classes narrowly, that reason is not in their comment, and the asymmetry is: a too-broad catch here costs a loudly-recorded error field; a too-narrow one costs a round of the integrity hash record.
- **Otherwise I agree with tonight's work explicitly, having executed it:** the R5a withdrawal (strengthened, F4), the R6 blast-radius answers (a) and (b), the fitted-vs-naive cut (the naive 2026-08-25 cut is genuinely a 1-off blip; the fitted 2026-09-04 cut survives correction), the `ASSUMED_DEFAULT` key on `n_windows` (right key — with ≥3 windows the `(0,0,0)` sentinel in `_fit_heaps` is unreachable because cumulative token counts strictly increase; the defect was in the fields beside the flag, not the flag), and the 2.2 population correction (789/28 reproduces).

## WHAT I DID NOT CHECK

- `TestTheOrderingActuallyHolds` (executes the full pre-commit hook, ~minutes) — my 5th mirror flows through the same stage-0 path the passing static assertions cover, but I did not run the hook end-to-end.
- The 27 remaining post-mechanism missing falsifiers (only C0053 has one).
- Whether a mirror could be declared **outside** `experimental_notes/` — I swept the repo's other `.md` trees and found only TTS/archive references (RECOVERY.md), which are archives, not mirrors; but the test still scans only `experimental_notes/`.
- A pytest anomaly I observed but did not root-cause: tracebacks for two test modules cited canonical-tree paths while running in the sandbox (likely module-name/`__pycache__` collision via conftest sys.path). It did not affect any verdict above — I confirmed every decisive comparison against explicit absolute paths — but someone should look, because a guard that silently reads the wrong tree is a measurement-integrity risk.
- Whether these sandbox fixes propagate to the canonical tree — that is the harness's fingerprint-diff, not something I can execute from here.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round8_2026-09-10/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
