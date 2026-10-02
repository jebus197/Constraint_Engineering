<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8304977ce074ca82fed66f6a5b8b7480d19190da3542bb1bcd14423ac6a015a8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# CC seat — design review BEFORE build: what makes a prose target answerable?

**Dispatched 2026-09-30. Nothing here is decided; every fix is SUGGESTED to the
human per `feedback_fixes_hil_only`. Two code changes have been written into the
sandbox tree so a reviewer can diff them; both are reversible one-liners plus
comment.**

Every number below comes from a script in `scripts/` that runs from the
repository root. Where a script's name is given, that script produced the
number and nothing was retyped.

| script | produces |
|---|---|
| `scripts/q1_claim_ledger_three_way_discrimination_2026-09-30.py` | Q1 |
| `scripts/q2_advisory_accuracy_vs_meaning_2026-09-30.py` | Q2 |
| `scripts/q3_e1_efficacy_veto_2026-09-30.py` | Q3 |
| `scripts/q4_test_cmd_none_no_gate_2026-09-30.py` | Q4 |
| `scripts/q5_archive_copy_conflation_inflates_q3_2026-09-30.py` | Q5 |
| `scripts/q6_nstar_alpha_is_cumulative_2026-09-30.py` | Q6 |

**Code written into the tree, for diff:**

1. `bench/reference_runner_v3.py` — the `e1_efficacy` veto (Q3), placed
   immediately after `tristate = SK_ADMISSIBLE if sk > 0 else SK_REJECTED`.
2. `bench/tools/run_simulated_experiment.py` — `--test-cmd` default changed
   from the immune-memory suite to `None` (Q4).

All 7 declared brief figures were re-executed and reproduce exactly.

---

## Q1 — THE PRIMARY QUESTION. What yields a DEFINITIVE AFFIRMATIVE on prose?

### Position

**A19 is the wrong instrument and no repair to it can answer this.** A19 scores
a *fix*. The founder's calculator wants a verdict on a *claim*. Those are
different objects, and an instrument measuring one cannot emit the other. A19 is
a **harm guard** being asked to do a job it is not pointed at.

The affirmative mechanism **already exists in this repository**, at the claim
level, and is reachable today. What is missing is one control and a caller.

### Four candidates, generated independently, then falsified

**M1 — Make `ADMISSIBLE` reachable on prose (repair A19).**
*Falsified.* `ADMISSIBLE` on prose would mean "no new ruff/bandit diagnostic in
the fenced listings". Measured on the committed ground truth
(`q2_...py`): the advisory that summarises exactly those gates takes the value
**1.0 on all 5 fixes a reviewer should accept and 1.0 on both harmful fixes it
scores — 0 of 5 separation**. A verdict from a measurement with zero
discriminative power is not an affirmative; it is a constant. The project's own
recorded reasoning already says this, and the measurement agrees with it.

**M2 — Panel agreement / consensus.**
*Falsified on arrival* by `feedback_no_model_voting` and by the founding
principle. Not admissible, and I record it only because it is the tempting
answer.

**M3 — Differential recomputation with two independent solvers.**
*Survives, but it is not a mechanism — it is an engine.* It needs a carrier that
says which value to recompute and what counts as agreement. That carrier is M4.

**M4 — THE CLAIM LEDGER, with three-way discrimination. RECOMMENDED.**

A prose target is **answerable** iff each of its claims is *computationally
addressable*: reducible to a value recomputable from the document's own declared
inputs. For each such claim the instrument holds a falsifier `F`, and may emit a
verdict **only** when all three controls pass, each one a run of the runner's own
decider `falsifier_verify.reverify_falsifier`:

```
P  POSITIVE   F(D_defective) == CONFIRMED    F can demonstrate the defect.
N  NEGATIVE   F(D_corrected) == REFUTED      F goes quiet once the claim is true.
B  BLIND      F(D_destroyed) != REFUTED      F actually READS its target.

AFFIRMED(C)   iff P and N and B, and F(D_actual) == REFUTED
REFUTED(C)    iff P and N and B, and F(D_actual) == CONFIRMED
UNTOOLABLE(C) otherwise — and report WHICH control failed, never a verdict.
```

**B is the addition.** P and N together are the existing discrimination control
(`run_discrimination_control`). Without B, a `REFUTED` on the actual document is
indistinguishable from a falsifier that never opened it.

### Executed evidence, and it found something

`scripts/q1_claim_ledger_three_way_discrimination_2026-09-30.py`, over the 5
committed fixtures, through `reverify_falsifier`:

```
fixture      claim    P(defect)   N(fixed)    B(no bytes)    P N B
structural   SM-08    CONFIRMED   REFUTED     REFUTED        Y Y n
statistics   ST-05    CONFIRMED   REFUTED     CONFIRMED      Y Y Y
metrology    CM-06    CONFIRMED   REFUTED     REFUTED        Y Y n
algorithms   AL-03    CONFIRMED   REFUTED     CONFIRMED      Y Y Y
numerical    NA-05    CONFIRMED   REFUTED     CONFIRMED      Y Y Y

P 5/5   N 5/5   B 3/5   all three 3/5
Wilson 95% on all-three [23.0724%, 88.2379%]  (mpmath and statsmodels agree)
```

**2 of the 5 committed falsifiers return `REFUTED` against a document whose
bytes are gone.** Root cause, read from the two failing templates:

```python
if block is None:
    print("NOT FALSIFIED: SM-08 is absent from the document")
    raise SystemExit(0)
```

That conflates *claim corrected* with *document unreadable*. It is **the arm-4
defect one level down** — the same shape as `e2_regression` returning 52/55 for
a prose document with its bytes destroyed. The README's recorded claim that all
5 "discriminate bidirectionally" is true and insufficient: bidirectional is two
directions, and there are three.

The design claim I tested is **not** "the corpus is a calculator" — it is "B is
not redundant with P and N", because an addition nothing reaches is not
additive. B rejects 2 of the 5 falsifiers that P+N accept. It is reached and it
is load-bearing.

### Is what already exists sufficient for a meaningful test?

**Yes for a meaningful test, no for the calculator.** Concretely:

- **Sufficient:** the corpus (5 documents, 29 tagged claims, 24 true / 5 false),
  the falsifier templates, `reverify_falsifier`, and the prose routing prompt
  that already tells a model to open the document by path. A meaningful test can
  be run *this afternoon* on what is committed. That is not nothing and it
  should be said plainly.
- **Not sufficient:** the live path reaches none of it —
  `reference_runner_v3.py`, `routing.py`, `falsifier_verify.py`,
  `immune_agents.py` and `runner_core.py` mention the corpus **0 times each**
  (re-executed, brief figure 7). And 2 of 5 falsifiers fail control B.

### What else is needed — the minimum, in order

1. **Add control B to the existing discrimination control.** One extra
   `reverify_falsifier` call against an emptied copy, per falsifier. Cost: one
   subprocess per claim. This is the single highest-value item and it is small.
2. **Repair the 2 failing templates** so an absent claim block is `ERROR`, not
   `NOT FALSIFIED`. Suggested, not performed — it edits a fixture, and under
   `falsifier-integrity` rule 2 a measurement is not repaired quietly.
3. **Wire one caller.** The corpus needs a live-path consumer or it is an
   addition nothing reaches. The join point is a new effect gate registered
   alongside `e4_bandit`, or a replacement for the NO_SCORE arm's outcome.

### Strongest attempt to falsify my own answer

*"B will reject honest falsifiers that legitimately exit clean when a claim is
absent."* — It will, and that is the point: an absent claim is not a true claim.
But this does make B a **behaviour change to existing fixtures**, not a pure
addition, and the founder should rule on it. *"3 of 5 is a small denominator."*
— It is; the Wilson interval [23.07%, 88.24%] is honest about that, and I make
no rate claim from it. The claim I make is existential — B catches two real
cases — and an existential claim does not need a tight interval.

---

## Q2 — Make the advisory accurate AND meaningful, without suppressing it

### Position

**Accuracy and meaning are different properties needing different repairs, and
the founder's trap is real: the Q4 repair delivers accuracy and buys no meaning
at all.** I measured it rather than asserting it.

- **ACCURATE** = every input measures the thing it names. `0.978182` fails:
  its `e2` input scores the immune-memory suite, not the prose target. Removing
  the false input yields an honestly derived `1.0`.
- **MEANINGFUL** = the number MOVES when the thing it summarises moves.

### Executed evidence

`scripts/q2_advisory_accuracy_vs_meaning_2026-09-30.py`, baselines captured with
the runner's own `_capture_baseline` (my first run fabricated a zero baseline and
manufactured 3 false rejections — **retracted**, and the corrected script uses
the real function):

```
fixture      correct_fix       harmful_fix
structural   1.0 NO_SCORE      None REJECTED
statistics   1.0 NO_SCORE      None REJECTED
metrology    1.0 NO_SCORE      1.0  NO_SCORE
algorithms   1.0 NO_SCORE      1.0  NO_SCORE
numerical    1.0 NO_SCORE      None REJECTED

advisory on the 5 fixes a reviewer SHOULD accept : [1.0, 1.0, 1.0, 1.0, 1.0]
advisory on the 5 fixes a reviewer MUST reject   : [1.0, 1.0]
fixtures where correct scores STRICTLY ABOVE harmful : 0 of 5
the DECISION (tristate) separates on                 : 3 of 5
```

**The advisory scalar has zero discriminative power (0/5). The decision it sits
beside has 3/5.** The 2 it misses are exactly the 2 the fixture module declares
to be semantic harms with no payload — the metrology harm edits the measured
input so the document becomes self-consistent; the algorithms harm improves the
metric under review while destroying correctness. No static sweep can see
either, by construction.

### The design that delivers both

Not suppression. Not a bigger number. **Report the number with its measured
discrimination attached.** Three parts:

1. **Fix the inputs** (Q4). `computed_sk` becomes honestly derived.
2. **Rename it to what it is.** Not "sk would have been 1.0" — which invites the
   reading that the fix scored full marks — but
   `static_harm_sweep: CLEAN (0 new ruff, 0 new bandit)`. Same information, no
   false implicature. This costs one string.
3. **Attach the separation.** Ship the Q2 measurement as a committed test, and
   have the advisory carry its own last-measured discrimination:
   `static_harm_sweep: CLEAN — separates 3/5 known harm classes; blind to
   semantic harm`. A number that states what it cannot see is meaningful even
   when its value is constant, because the *reader* can now act on it.

Meaning at the level the founder wants comes from a **different measurement**,
and it is Q1's claim ledger, which demonstrably separates (P and N, 5/5).

### Strongest attempt to falsify

*"Attaching a discrimination figure is itself an addition nothing reaches."* —
Fair, and it is why part 3 is specified as a committed test first and a display
string second: the test is reached by CI, the string by the HIL. If the founder
takes only one part, take part 2 — it is one string and it removes a false
implicature at zero cost.

---

## Q3 — The `e1_efficacy` veto, and its evidence

### Position

`e1_efficacy` must be a **gate**, not a weighted term. Written into
`bench/reference_runner_v3.py` for diff.

### Derivation, not assertion — no finite weight can do this job

With `e1 = 0` and the other gates clean, SymPy gives

```
E(e1=0) = (2*s2 + s3 + 2*s4) / (w1 + 5)        with e2=e3=e4=1:  E = 5/(w1+5)

w1 = 2       E = 5/7      = 0.7142857143   > 0  -> ADMISSIBLE
w1 = 10      E = 1/3      = 0.3333333333   > 0  -> ADMISSIBLE
w1 = 100     E = 1/21     = 0.0476190476   > 0  -> ADMISSIBLE
w1 = 10^6    E = 1/200001 = 0.0000050000   > 0  -> ADMISSIBLE
lim(w1->oo) E = 0
```

`tristate = SK_ADMISSIBLE if sk > 0` has **no threshold**. `E > 0` at every
finite `w1`, so **no reweighting ever rejects**. The veto cannot be bought with
weight; it has to be a gate. (5/7 cross-checked on SymPy, `Fraction` and mpmath,
agreeing to 1e-30.)

### The two measurements the founder's condition requires

His clearance was conditional: it must *plug the hole and make the instrument
more accurate*, not merely change which fixes pass. So:

**(1) EFFICACY — the targeted class.** The named property is the
**false-admission rate on fixes MEASURED not to cure their own falsifier**. This
requires no judgement: `FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER` is a probe verdict
produced by re-running the falsifier after the fix. Admitting such a fix is a
false positive by the instrument's own definition.

Archive measurement, deduplicated against the copy conflation (Q5):

```
fixes measured not to cure their own falsifier, ADMITTED anyway: 201 of 201
Wilson 95% [98.1247%, 100.0000%]   (hand Wilson and statsmodels agree)
```

(The brief's figure of 73 is a hardcoded literal in the figures script, not a
live count. The live count is 201 after deduplication and 309 before — see Q5.)

After the change, live `compute_sk` on `bench/dm/_convergence.py`:
`e1 = FIX_INEFFECTIVE -> REJECTED, sk = 0.0`, with the arithmetic preserved in
`_e1_veto.computed_sk`. **Nothing is hidden**; the HIL still sees what the
weighted mean said.

**(2) INVARIANCE — everything else. This is the load-bearing half.** Six other
e1 classes, live calls:

```
FIX_CURES_ITS_OWN_FALSIFIER        ADMISSIBLE  sk=1.0  veto_fired=False
NOT_PROBED_NO_FALSIFIER            ADMISSIBLE  sk=1.0  veto_fired=False
None                               ADMISSIBLE  sk=1.0  veto_fired=False
INDETERMINATE_NO_BASELINE          ADMISSIBLE  sk=1.0  veto_fired=False
INDETERMINATE_OTHER                ADMISSIBLE  sk=1.0  veto_fired=False
INDETERMINATE_NOT_INTERCEPTED      ADMISSIBLE  sk=1.0  veto_fired=False
```

**0 of 6.** The veto fires only on the explicit measured-ineffective verdict.
`None` — not measured — is untouched, because an unmeasured fix is not a failed
fix and conflating them would be the silent-evidence-loss failure the file
already records against `e2`.

Targeted tests after the change, all green: `test_prose_acceptance_stem.py`
(226 passed), and 155 passed across `test_prose_gates_are_one_sided`,
`test_target_kind_and_no_score`, `test_immune_memory_consumption` (the AST guard
on the `sk_result` reader set), `test_e2_unavailability_is_recorded`,
`test_commissioning_arms_carry_their_settings`.

### The one thing the founder must rule on

**On a prose target the e1 veto now runs BEFORE the prose one-sided veto**, so a
prose fix with a genuinely measured `FIX_INEFFECTIVE` moves `NO_SCORE ->
REJECTED`. I judge that correct — it is a decided rejection on *measured
evidence*, not a static sweep, which is precisely the distinction the prose
NO_SCORE arm was built to protect. But it **is** a prose-path behaviour change
and it is not covered by the founder's 2026-09-30 clearance, which was about
Python targets. If he wants it scoped to Python, add
`and not _scoring_prose` to the condition. One clause.

### Strongest attempt to falsify

*"Invariance on 6 synthetic classes is not invariance on the archive."* — True,
and it is the gap. The synthetic sweep proves the branch condition is narrow; it
does not prove no archived Python entry changes. **What would settle it:** a
replay of the archived entries through the patched `compute_sk` with their
recorded gate inputs, asserting bit-identity on every non-`FIX_INEFFECTIVE`
entry. I did not run it — the archived entries store the *result* of
`compute_sk`, not all its inputs, so a faithful replay needs the fix text and
baseline reconstructed. **This is the one HARD assumption in my Q3 design that
remains untested**, and I name it rather than continue past the point of return.

---

## Q4 — Should `test_cmd=None` mean NO GATE?

### Position

**Yes.** `None` means the caller declined to supply a test command, and no layer
below should invent one. Written into `bench/tools/run_simulated_experiment.py`.

### Which repair, and why this one

Two were available:

- **(a) `Arm.argv()`: `if self.test_cmd is not None`, with an explicit empty
  else.** Rejected. It also requires changing a committed test —
  `bench/tests/test_commissioning_arms_carry_their_settings_2026-09-21.py`
  asserts `--test-cmd` is *absent* from `arm4.argv()` — and under
  `falsifier-integrity` rule 2 a measurement is not repaired quietly. Note this
  tree already carries the conflict: `scripts/falsifier_supply_fable_2026-09-30.py`
  asserts `got.test_cmd == ""`, which the committed test contradicts. **The two
  cannot both be satisfied**, and that disagreement belongs to the human.
- **(b) argparse default `None`.** Taken. One line, no test change, and it fixes
  the defect at the layer that invented the value. `_run_effect_regression`
  already returns `(None, "no test command configured")` on a falsy `test_cmd`,
  so `e2` becomes *unavailable* and is excluded from `E`'s renormalised mean
  rather than faked. `simplicity-default`.

End to end through the real parser, after the change:

```
parse_args(arm4.argv()).test_cmd = None       arm4 declines -> NO GATE
parse_args(arm1.argv()).test_cmd = 'python3 -m pytest bench/tests/...'   gate ON
```

### CC1's claim: verified

```
prose with REAL bytes      -> e2 = 0.9454545454545454  (52/55 passed)
prose with bytes DESTROYED -> e2 = 0.9454545454545454  (identical: BLIND)
distinct veto outputs over 7 e2 values : 1
apply_sk_to_rk(0.5, NO_SCORE) -> 0.5     delta = 0.0
E with substituted suite = 269/275 = 0.978182   ->   E without = 1.0
```

**All three counts CONFIRMED.** No verdict moves, `R_k` does not move, and the
advisory moves **upward** when the false input is removed.

### What CC1's claim does not cover, and I add

- `scripts/estimate_nu_from_archive_2026-09-21.py` reads `e2_regression.score`
  from archived entries to emit a ν lower bound. It filters on `ADMISSIBLE`,
  which prose never is, so it is unaffected **today** — and affected the moment
  prose becomes scoreable. Name it now.
- `scripts/a19_break_even_assumes_e2_absent_2026-09-30.py` counts occurrences of
  the 52/55 constant. Its count changes by construction.
- `scripts/scorer_discrimination_2026-09-20.py` carries its **own** hardcoded
  `WEIGHTS["e2_regression"] = 2.0`. A second copy of the weight, pinned to the
  runner's literal by no test. A latent divergence, independent of this change.
- The e2 record **is** persisted into `runner_state.json`, the checkpoint and
  `sk_pipeline`. The AST guard in `test_immune_memory_consumption.py` bounds the
  `sk_result` reader set to 4 functions, none of which reads the e2 score by
  name — so a resumed round cannot read it into a decision. That guard is the
  reason this change is safe, and it should be said.

### Strongest attempt to falsify

*"Changing an argparse default silently changes behaviour for every caller that
relied on it."* — It does, and that is the real cost. Measured: arms 1–3 pass
`ENGINE_TESTS` explicitly, so only arm 4 and any ad-hoc invocation without
`--test-cmd` are affected. An ad-hoc caller now gets `e2` unavailable instead of
a suite it did not ask for, which is the correct outcome — but it is a change
and it is not free.

---

## Q5 — Remedy for the structural conflation

### Position

**Content-hash deduplication at the point of measurement, plus a guard test.**
Not a path predicate, and not relocating the harvest.

### Executed evidence — a FOURTH mechanism bitten, and it is Q3's number

`scripts/q5_archive_copy_conflation_inflates_q3_2026-09-30.py`:

```
e1-bearing archive entries under bench/logs : 1692

raw (every path, every entry)      measured-ineffective = 309  ADMISSIBLE = 309
path-filtered (shared predicate)   measured-ineffective = 201  ADMISSIBLE = 201
content-deduplicated (sha + id)    measured-ineffective = 201  ADMISSIBLE = 201
both                               measured-ineffective = 201  ADMISSIBLE = 201

INFLATION raw vs deduplicated: 309 vs 201 = 53.7313%
```

**53.73% inflation on the exact count Q3 turns on.** The brief lists 3 mechanisms
bitten; this is a fourth, and it was about to become a fifth in my own answer.

### Weighing the three candidates

| candidate | cost, measured | verdict |
|---|---|---|
| shared `is_archive_copy` predicate | **259** archive-scanning call sites carry no copy filter today; each needs editing, and the predicate hardcodes the string `sandbox_harvest`, so a rename silently un-fixes all 259 | **reject** — 259 edits, and fragile |
| move harvest out of the archive namespace | **24** directories, **182,014,739 bytes**; every committed path into those trees breaks at once | **reject** — largest blast radius, and it fixes only the last instance |
| guard test refusing an unguarded scan | one AST test | **keep** — the only candidate that prevents the *next* instance |

**The measurement that decides it:** path filtering and content deduplication
give the **identical** count, 201. The copies are byte-identical. So content
hashing is *sufficient*, needs no naming convention, survives any rename of
`sandbox_harvest`, and cannot over-count. It dominates the path predicate on a
named property — robustness to renaming — at equal accuracy. That is the
committed measurement the additive standard asks for before preferring one to
the other.

**Recommended, in order:** (1) a 12-line `bench/archive_scan.py` exposing
`dedup_entries(iterable)` keyed on `(file_sha256, finding_id)`; (2) a guard test
asserting any *new* script that globs `bench/logs/**.json` imports it. Do **not**
retrofit all 259 — that is a large edit for measurements mostly already
published. Fix forward.

### Strongest attempt to falsify

*"Content hashing collapses two genuinely distinct runs that produced identical
files."* — It can, and in that case they are identical measurements and
collapsing them is correct, not lossy. The failure mode is the reverse: a copy
that differs by one byte survives dedup. **That is untested here** and is the
one HARD assumption in Q5 I have not settled; what would settle it is a byte-diff
of every harvested copy against its original, which I did not run.

---

## Q6 — Settle `n* = (a/theta)^(1/gamma)`

### Position

**`a` is a CUMULATIVE coefficient — settled by execution. But the prior round's
correction to `(a(1-gamma)/theta)^(1/gamma) = 1.6447` is ALSO wrong, and the
whole quantity is moot in the harness.** Four separate results.

### S1 — the fitting code, found and called

`bench/decay_analysis.py:fit_duane`, the only committed Duane fitter. Called, not
read:

```
fit_duane([5,5,5,5,5,5,5,5])     -> alpha = 5.0, gamma = 1.0, sse = 0.0
```

A constant **rate** of 5/round has cumulative `5n`. The fitter returns
`alpha = 5, gamma = 1`, so it fits `N(n) = alpha * n^gamma` to the **cumulative**
series (`np.cumsum`). `alpha` is a cumulative coefficient. The module's own
intensity comment confirms it: `lambda(n) = alpha*gamma*n^(gamma-1)`, so
`lambda(1) = alpha*gamma != alpha`.

### S2 — TWO INCOMPATIBLE QUANTITIES ARE BOTH NAMED `gamma`

On arm 1's own novel-per-round series `[8, 2, 6, 5, 4, 3, 3, 9]`:

```
decay_analysis.fit_duane   gamma = 0.877600   (== beta, the growth exponent)
run_exp35._estimate_gamma  gamma = 0.214289   (== 1 - beta, clamped at 0)
disagreement                     = 0.663311
```

`GAMMA IS LOAD-BEARING` is a standing directive, and the repository holds two
different load-bearing quantities under one name. Feeding one into a law written
for the other moves `n*` by orders of magnitude. **I rate this the most
consequential finding in Q6.**

### S3 — the live path cannot evaluate `n*` at all

`_estimate_gamma` returns a bare `float` and never forms the regression
intercept. `reference_runner_v3.py` imports only `compute_d_score` from
`decay_analysis`, which discards `alpha`. `routing.py`, `falsifier_verify.py`
and `runner_core.py` mention it 0 times. **No live module emits `a`.** The
`CDSFL_MASTER_TASK_LIST.md:171` claim that "the fit already runs every round via
`_estimate_gamma`" is false for this purpose: that function cannot supply `a`.

### S4 — `n*` under three readings, at `a = 4.89, gamma = 0.709, theta = 1`

```
(A) a is a RATE coefficient      n* = (a/theta)^(1/gamma)          =  9.380519307936
(B) a cumulative, CONTINUOUS     n* = (a(1-gamma)/theta)^(1/gamma) =  1.644680681197
(C) a cumulative, DISCRETE       a(n^b - (n-1)^b) = theta          =  2.187873457283
```

mpmath, SymPy and `scipy.optimize.brentq` agree to 12 significant figures on all
three. **Cross-checked on Wolfram Language** (local Wolfram Engine via
`wolframscript`, exit 0, no `Name::tag`, no `$Failed`), which returned
`{9.380519307936057, 1.6446806811974513, 2.1878734572826417}` — agreeing to 12
digits. *(Values computed with Wolfram Language.)*

**The discriminator.** For the fitted cumulative `N(n) = alpha*n^beta`,
`N(1) = alpha*1^beta = alpha` for **every** beta. So `alpha` **is** the round-1
finding count, and the law's own gloss — "the round-1 finding rate divided by the
threshold" — is satisfied by `alpha` itself. The prior round's correction
multiplies by `(1-gamma)` because it takes the **continuous** derivative
`dN/dn` of a series indexed by a **discrete** round number. Rounds are discrete.
Reading (C) is the honest stopping rule and it gives **2.19**.

Reading (A) is self-inconsistent on its own terms: it implies
`N(1) = a/(1-gamma) = 16.80` findings in round 1, not 4.89.

### S5 — the constants are UNSOURCED

421 committed per-round curves with ≥3 rounds and >0 findings were fitted with
`fit_duane`. Mean round-1 count **3.501188**, max 16. **44** fits land within 0.5
of `alpha = 4.89`. **0** land within 0.5 of 4.89 *and* within 0.05 of
`gamma = 0.709`. The pair `(4.89, 0.709)` is **not reproducible from any
committed artefact in this tree**. It survives only as prose in
`experimental_notes`.

### S6 — does `rounds = 10` survive?

```
   gamma       (A) rate    (B) cont.   (C) discrete
  0.7090         9.3805       1.6447       2.1879
  0.5301        19.9681       4.8039       5.3172
  0.2824        275.9913     85.2244      85.7250
  0.1914       3993.9691   1316.2695    1316.7695
  0.1776       7607.5283   2529.9264    2530.4264
```

Across **arm 1's own gamma history**, under a single reading, `n*` ranges from
9.38 to 7607.53. Across readings at a single gamma it moves by a factor 5.70.

**`n*` is not a stable number.** `rounds = 10` survives — but **only as an
empirical budget, never as a derivation from `n*`**. Both prior seats reached 10
and both, per the record, built it "not to depend on the answer". That was the
right instinct and my analysis strengthens it: the answer they declined to depend
on is a quantity with no settled value, computed from constants with no
provenance, by a formula the harness cannot evaluate. **I agree with `rounds =
10`, and I disagree with any justification for it that cites `n*`.**

### What would make me wrong

Producing the March 2026 artefact in which `(4.89, 0.709)` was fitted, and
showing which of the two `gamma` conventions it used. If it used
`decay_analysis`'s convention, then `0.709` is beta, the convergence gamma is
0.291, and every `n*` above is computed with the wrong exponent. **That artefact
is not in this tree.** Recovering it is the single action that would settle Q6
completely; without it, S1–S3 stand on execution and S4–S6 are conditional on
constants nobody can source.

---

## Disagreement with the other seat

I have not seen the other seat's reply and will not shape mine toward it. Where
we differ the disagreement is preserved as information. Two places I expect it:

1. **Q6.** If the other seat endorses the prior round's `1.6447`, I disagree:
   that is the continuous derivative of a discretely-indexed series, and the
   discrete answer is 2.19. Both are moot next to S2 and S3.
2. **Q1.** If the other seat proposes repairing A19 to reach `ADMISSIBLE` on
   prose, I disagree, and the measurement is `q2_...py`: 0 of 5 separation.

## Where I stopped, and why

Two consecutive passes produced no new finding above the real-world-consequence
threshold. Pass 4 produced the Q2 baseline retraction (my own artefact, corrected
in the script). Pass 5 produced nothing new. Every HARD assumption in the design
has been tested except two, both named above and neither padded over:

1. **Q3 invariance on the real archive**, not on 6 synthetic classes. Settled by
   replaying archived entries through the patched `compute_sk`; needs fix text
   and baselines the archive does not store.
2. **Q5 near-duplicate copies** differing by one byte would survive content
   dedup. Settled by a byte-diff of every harvested copy against its original.
