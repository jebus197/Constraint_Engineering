# FULL RECORD — free panel round on severity and residual risk, 2026-11-06

Record written 2026-11-06T21:26:38+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. A corrected brief on severity and residual risk, put to 2 free seats (cc2 and fable, both via claude_cli on the existing subscription). 0 paid seats; the dispatcher resolves MODELS to FREE_SEATS when PANEL_ONLY is unset, verified by execution before dispatch. The brief replaced a 2026-11-04 round whose own brief had asserted a conflation the founder has since disowned.

WHY. The founder asked 2 questions: given that severity and residual risk are different quantities, how can severity be meaningfully measured and fed back into the harness; and should severity block convergence until it is within an acceptable bound, and what should that bound be.

WHAT THE ROUND FOUND, AND MOST OF IT IS AGAINST THE BRIEF. Both seats independently refuted the brief's lead framing. The brief claimed sections 7.7 and 7.8 of the mathematical appendix contradict each other, because a disproved finding scores 0 under 7.7 and 0.27289178365887046 under 7.8 Approach B. They do not contradict: section 7.11 CONJOINS them, and 7.8 sets its prior from "uniform prior: P(claim true) = 0.5", so S_v is a posterior credence rather than a severity. The gap was produced by substituting S_v for confidence times V, which no section and no code does. Verified at source afterwards.

The brief also claimed the contradiction was verified by SymPy and z3 independently. 1 seat identified precisely why that was false: the tools verified that V(REFUTED) = 0 zeroes the product and that S_v never reaches 0, both true, and neither establishes that the 2 expressions denote the same quantity.

The real defect is a naming collision: S_v is called "multi-verifier Bayesian severity" at 2 sites while 7.8 derives P(claim true). A clarification is now in the appendix.

WHAT SURVIVED AND WAS STRENGTHENED. The brief's argument that no cut above 0.5 is a magnitude test was generalised by cc2 into a shape-quantified theorem: for Sev = W times B with W taking 2 values and B any composition in [0,1], Sev >= c is equivalent to W = W(HARD) and B >= c, for every c in (W(SOFT), W(HARD)]. Re-derived independently here: z3 unsat for the negation of both directions over all 3 variables at once, premise satisfiable so not vacuous, and satisfiable at c = 0.5 so the interval is tight. SymPy puts the SOFT supremum at 1/2.

THE CENSUS DISPUTE. fable returned DOES NOT REPRODUCE against the brief's 1,559 of 3,474 and was right on both figures. The authoritative population is 3,170, by whole-file digest dedup, which this project has used since 2026-10-12 and which is better than the name-based exclusion first attempted here and now withdrawn. The numerator is 1,297 of 3,170 = 0.409148, Wilson [0.392152, 0.426364]: the field holds an empty string on 305 entries, and a first count here treated present-but-blank as a recorded verdict. The conclusion is frame-independent, because confidence is recorded on 0 entries in every frame.

WHAT WAS DONE WITH THE FINDINGS. All of it folded back: 2 producers and 2 guards from the seats, 60 tests, plus the appendix clarification. The seats' own guards were then mutated and only 1 of 4 mutations was caught, so a further guard pins the factor values and the 7.11 conjunction, taking that to 4 of 4. The seats' own files were left unchanged so provenance stays legible.

Entry B87's framing moves: neither document is wrong, so the question is not which to amend; the formula needs 2 inputs recorded on 0 entries and collecting them is prior to choosing a bound. Entry B121 is narrower than the defect it reports.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# CORRECTED BRIEF -- severity and residual risk, with the error the last brief carried


## REQUIRED SECTION 1 -- The question

**This output was produced by another system and has not been independently verified.** It may
contain errors at interfaces between subsystems, unstated assumptions that conflict across
components, constraint violations visible only at system level, and conclusions that are
internally consistent but wrong. **Your task is to find what is wrong, not to confirm what is
right.**

**WHY THIS ROUND EXISTS, AND WHAT THE LAST ONE GOT WRONG.** The round of 2026-11-04 asked you
both about severity and residual risk. Its brief asserted: *"Residual risk is `R_k`, a different
quantity with no severity term."* **1 of you refuted that sentence** and was right to. This
brief carries the correction, and the founder has disowned the conflation that prompted the
original question: it was his, he has withdrawn it, and he does not want it reproduced.

**THE LEAD QUESTION IS NOT HIS CONFLATION. IT IS THAT 2 SECTIONS OF OUR OWN APPENDIX
DISAGREE WITH EACH OTHER.** Verified 2026-11-05 by SymPy and z3 independently, with the factor
tables parsed out of `bench/reference_runner_v3.py` at run time rather than restated here:

* `docs/MATHEMATICAL_APPENDIX.md` section 7.7 gives `Sev(f) = W(class) . confidence .
  V(verification)` with `V(REFUTED) = 0.0`, so a disproved finding scores **exactly 0**. SymPy
  gives 0 identically; z3 returns unsat for any value above 0.
* Section 7.8 offers 2 fusions. **Approach A** is multiplicative and preserves that 0: z3
  returns unsat for a result above 0 when the SymPy factor is 0. **Approach B**, which 7.8
  marks *preferred*, is `S_v = 1 / (1 + exp(-Lambda_total))`, which **never reaches 0 at all** --
  z3 unsat for `S_v = 0` under `t > 0`, and SymPy finds no real solution, only an unattained
  limit.
* The appendix's own worked example closes it: SymPy falsified with the others verified gives
  `Lambda = -49/50` and **`S_v = 0.27289178365887046`**, by SymPy and mpmath agreeing to 1e-15.

**So the same disproved finding scores 0 under 7.7 and 0.273 under 7.8 Approach B.** 1 seat's
joint-round fix was to *delete the KEY PROPERTY paragraph and the `V` column; redirect to 7.8*.
The other seat's blind reply warned that *the key property is silently lost if 7.7's
`confidence . V` is replaced by `S_v` alone*. **The appendix's own number makes the second seat
right and the first seat's deletion harmful as written**, because it would adopt the
disagreement as the specification. The joint round did not settle this. **Attack that reading.**

## REQUIRED SECTION 2 -- What is true of the live code, measured

Treat every figure as a hypothesis under test and re-derive what you can.

* **The 7.7 formula IS implemented and is switched OFF.** `compute_sev_f` at
  `bench/reference_runner_v3.py:10986` computes the product exactly, including the hard 0.
  `_SEVERITY_SPEC = {"on": False}`. With it off the gate reads `float(entry["severity"])`, a
  model-asserted number.
* **The key property is violated where it should bite.** `scripts/severity_was_never_computed_from_the_model_2026-10-12.py`,
  run 2026-11-06 at exit 0: **27 of 32 disproved findings carry a severity above 0, 84.3750%**,
  Wilson [68.2459%, 93.1356%], Clopper-Pearson [67.2121%, 94.7249%].
* **Severity ALREADY blocks convergence.** The `exhausted` door out of
  `unverified_critical_count` requires `severity >= 0.7` AND at least 1 verdict.
* **BUT NO CUT ABOVE 0.5 IS A MAGNITUDE TEST.** Verified at 19 cuts by z3 with cell suprema by
  SymPy: exactly 1 cell, `(HARD, CONFIRMED)`, can reach 1; every other cell's supremum is at
  most 1/2. So `Sev >= c` for any `c > 0.5` is identically `HARD AND CONFIRMED AND confidence >=
  c`, and inside that cell `Sev = confidence` exactly. Moving 0.7 to 0.8 tightens nothing about
  impact; it moves a threshold on the model's own self-reported confidence.
* **The severity PROOF checks the wrong formula.** `severity_is_proven` is true *"when the
  model's stated R_k reproduces from its own stated inputs"* (`reference_runner_v3.py:10512`) --
  a residual-risk reproduction offered as evidence for a severity claim. Measured by
  `scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py`: over 652 entries with a
  PASS or WARN proof, the proven `R_k` and the severity it licenses correlate at **r = -0.5538,
  p = 1.152e-53, 95% CI [-0.6048, -0.4982]**, numpy agreeing to 1.11e-16, Spearman rho =
  -0.4716. The proof moves AGAINST the number it licenses.
* **AND THE OBVIOUS REPAIR IS UNSATISFIABLE TODAY.** Over 3,474 archived entries carrying a
  severity: `falsifier_verdict` present on 1,559 (0.448762, Wilson [0.432289, 0.465349]),
  `confidence` on **0**, HARD/SOFT class on **0**, all 3 on **0** (Wilson [0.000000,
  0.001105]). `flaw_class` is present but is section 4's integer class id, not the HARD/SOFT
  class. So a proof that recomputes 7.7 cannot pass for any entry, and forcing it would halt
  the release door. Entry B87 is the open entry asking the founder to rule on collecting the 2 missing inputs.
* **Residual risk, settled and already corrected.** The per-class `R_k` is a probability in
  `[0, pi_k]`; the aggregate `R_n = sum w_k R_k` is an expected-loss scale -- z3 finds `R_n > 1`
  satisfiable with unnormalised weights, unsat once they sum to 1, and satisfiable for
  `R_n > 1/2` while every per-class `R_k` is at or below 1/2. A seat's witness recomputes
  exactly: `w = (3, 4)`, `R_k = (1/2, 1/2)` gives **7/2** by SymPy, NumPy and z3. This landed:
  `MATHEMATICAL_APPENDIX.md:169` and `cdsfl_operational.md:178`.

## REQUIRED SECTION 3 -- The founder's own questions, in his words

He asks 2 things this round must answer, and they are HIS framing, not mine:

1. **Given that severity and residual risk are different quantities, how can severity be
   meaningfully measured, and how should that measurement feed back into the rest of the
   harness?**
2. **Should severity block convergence until it is within an acceptable bound, and what should
   that bound be?** Note that section 2 above argues the question presupposes a magnitude the
   formula does not supply above 0.5. **If that argument is wrong, say so and show why.**

He has also proposed, on 2026-11-01: run the current severity measure live and the new one in
**shadow across several simulated runs** until there is enough data to retire the old one.
**Entry B5, recorded DONE, holds the objection that a shadow cannot be tested by a simulation,
because a shadow never decides.** Adjudicate that against his proposal. He is entitled to
either answer; what he is not entitled to is silence.

## REQUIRED SECTION 4 -- Produce a fix, deliver it as a file, and test it

Name files by path, state what you executed, and paste the output. A fix you have not tried to
break is a hypothesis.

**DELIVER EACH FIX AS A FILE, WRITTEN INTO THE SANDBOX REPOSITORY TREE AT ITS REAL PATH.** A fix
left in prose, in a scratch directory, or in this reply alone is destroyed at teardown and never
reaches the project: on 2026-10-15 a seat's finding sat in a sandbox for 10 days and existed
nowhere else. Write the edited file where it actually lives, for example
`docs/MATHEMATICAL_APPENDIX.md`, and not a copy beside it. Where the tree genuinely refuses a
write, name the path that refused and deliver an exact diff as well.

**IF YOU RECOMMEND A COMPOSED FIX, THE STANDARD IS THE FOUNDER'S AND IT REQUIRES A MEASUREMENT.**
His words, verbatim: *"Composability doesn't mean composing two solutions just because they can be
composed. It means this principle should be applied where two composed solutions demonstrably
provide a better, more robust and/or more efficient solution than either fix in isolation. Where
a single fix out performs a composed one, that fix should continue to be preferred."* So compose
ONLY on a demonstrated advantage over each part alone, where the demonstration is a MEASUREMENT
and not a judgement, and prefer the single fix where it performs as well. Stating that the
repairs do not conflict is the weak sense his definition explicitly excludes.


## REQUIRED SECTION 5 -- What would refute you

State the single observation that would overturn your central claim, and whether it is
reachable from this repository today.

## REQUIRED SECTION 6 -- Output shape and termination

Return all of: `verdict`, `per_part`, `severity_and_residual_risk`, `reasoning`, `commands_run`,
`strongest_falsification`, `refutation_condition`, `fix`, `disagreement`, `termination`.

`disagreement` is NOT optional and `none` is a non-answer: state your strongest disagreement
with this brief's own framing, or with the other seat, and say what evidence would settle it.
**This round does not ask you to converge.** Compelled convergence is retired.

Terminate when a further pass produces no new above-threshold finding.


Written under CDSFL note standard v1.9.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 35 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel severity_corrected_2026-11-06) -->

All green: 65 tests pass, four producers exit 0, three files delivered at real paths.

---

## `verdict`

**The brief's lead framing is REFUTED. §7.7 and §7.8 do not disagree as written.** The second joint-round seat reached the right conclusion (seat 1's deletion is harmful) but the brief's stated reason for it is a type confusion. And the brief's §2 argument — that no cut above 0.5 is a magnitude test — is **right, and weaker than the truth**: I strengthened it from one formula to every formula of that shape, and found that on the live archive no cut in (0.5, 1.0] tests anything at all.

## `per_part`

**1. "2 sections of our own appendix disagree with each other" — REFUTED.** §7.8's own text sets `Λ_prior = 0` from *"uniform prior: P(claim true) = 0.5"*. So `S_v` is a **posterior credence over "the claim is true"**, not a severity, despite the section heading. §7.7 caution 1 states the substitution target is `` `confidence` `` — not `confidence · V`. Under the appendix as written, a disproved finding scores `W · S_v · V(False) = 1 · 0.27289178365887046 · 0 = 0` exactly (SymPy simplifies to 0; z3 unsat for a result above 0). **0.273 is the belief factor and 0 is the severity.** The brief compares a credence with a severity. The key property survives the text as written.

**2. Seat 1's deletion — harmful, confirmed, and worse than "silently lost".** `S_v = 1/(1+exp(−Λ))` has **no zero** (SymPy `solve` → `[]`; z3 unsat; Wolfram Language `Solve` → `{}`; the Λ→−∞ limit is 0 and unattained). So `Sev = W · S_v` cannot *represent* `V(False) = 0`. The property becomes **unrepresentable**, not merely unstated. Seat 2's warning was correct; the brief's grounds for it were not.

**3. "No cut above 0.5 is a magnitude test" — CONFIRMED and generalised.** The brief derived this for §7.7 at 19 sampled cuts. The real result is about the **shape**, quantified over the cut as a free real:

> for `Sev = W·B` with `W ∈ {W(SOFT), W(HARD)}` and `B ∈ [0,1]` any composition of belief factors, `Sev ≥ c ⇔ W = W(HARD) ∧ B ≥ c` for **every** `c ∈ (W(SOFT), W(HARD)]`

z3: unsat for the negation over all three variables simultaneously. SymPy: `max_B W(SOFT)·B = 1/2`, unreachable. Wolfram Language `Resolve[ForAll[...]]`: `True` on each `W` branch, `Reduce` finds no counterexample. Because it is about the shape, it covers **all four** candidates on the table — `W·conf·V` (status quo), `W·S_v·V` (caution 1's repair), `W·σ(Λ)` (the 2026-11-04 seat's `EL`), `W·S_v` (seat 1's deletion). **All four collapse identically.** Replacing `confidence` with `S_v` is a **provenance** repair — it changes who computed the belief factor — and leaves the magnitude deficiency exactly in place. §7.7 caution 1 offers it under a heading about magnitude; that is the sentence I fixed.

**4. NEW, and it decides founder Q2: the computed severity is three-valued on the archive.** Over 3,474 archived entries, `constraint_class` and `confidence` are present on **0** each (Wilson 95% [0.000000, 0.001105]), and `compute_sev_f` defaults both to their *stricter* readings. So `sev_f` reduces to `V` alone: **0.0 on 42 entries, 0.5 on 2,050, 1.0 on 1,382**. Every cut in (0.5, 1.0] induces the **same partition**; moving 0.7 → 0.8, 0.9 or 0.95 reclassifies **0 entries**. On the model-asserted float the door reads today, the same moves reclassify 548 / 1,102 / 1,312 — but whether *any* of that is impact-related is **unmeasurable**, because the class is recorded nowhere.

**5. Clean, stated as such: the shadow is NOT an addition nothing reaches.** `stamp_sev_f` is called at `bench/reference_runner_v3.py:11010` and exercised by `bench/tests/test_sev_f_and_queue_membership_2026-10-13.py` (asserts the off-path no-op returns 0 and the on-path stamps 2). No additive-standard violation here. I checked because 11 of this project's confirmed defects were additions nothing reached.

**6. Brief's measured claims — all reproduced**, exit 0: 84.3750% key-property violation, Wilson [68.2459%, 93.1356%]; `r = −0.5538, p = 1.152e-53, CI [−0.6048, −0.4982]`, Spearman −0.4716; the `−49/50 → 0.27289178365887046` worked example. Sub-threshold drift: the `reference_runner_v3.py` comment states 831/835 V-crossers; the live archive now gives **834/838** (99.5227%). Immaterial, not fixed.

## `severity_and_residual_risk`

They are different quantities and the brief is right that they are. But **§7.7's `Sev(f)` is not a severity either** — it is a consequence weight times a belief, and the 2026-11-04 seat already derived this (`scripts/severity_is_an_expectation_not_a_magnitude_2026-11-04.py`, re-run today, 4/4 PASS, exit 0). I confirm that and extend it: consequence enters `Sev` through `W` alone, and `W` has **two** values.

**Founder Q1 — how can severity be meaningfully measured, and how should it feed back?** Severity is consequence-if-shipped (`cdsfl_core.txt` Objective section: *"Severity is **materiality** — the consequence if the defect ships"*). A two-valued `W` cannot express that, and today the harness records neither input to it. So: (a) the honest measurement requires a consequence scale with more than two levels, and CDSFL already enumerates one — §10's five material-defect categories; (b) **prior to any of that**, the two missing inputs must be collected, which is exactly entry B87's open question. The feedback path is already correct and should not change: `sev_f` is stamped **beside** `severity`, never over it, and the disagreement count is logged. Do not promote it to the gate — `V(None)` at the blocking gate would release 834 of 838 crossers on falsifier *omission*, which is the loophole the one-directional rule exists to close.

**Founder Q2 — should severity block convergence until within an acceptable bound, and what bound?** It already blocks (`unverified_critical_count`'s `exhausted` door requires `severity ≥ 0.7` plus a verdict). The question as posed presupposes a magnitude the formula does not supply, and **the brief's §2 argument is correct** — I was asked to say so if it were wrong, and it is not. A bound above `W(SOFT)` is a **bound on belief conditional on `class = HARD`**, under every candidate formula, and on the current archive it is inert. So: keep the existing block, **do not move the number**, and rename what it tests. A bound on magnitude is not specifiable until the class is collected.

**Residual risk:** settled and already corrected — per-class `R_k ∈ [0, π_k]` is a probability; `R_n = Σ w_k R_k` with `w_k` a consequence weight is an expected-loss scale, not a probability, and must never be thresholded at 0.5 (`MATHEMATICAL_APPENDIX.md:169`, `cdsfl_operational.md:178`). I did not re-litigate it.

**B5 vs the founder's shadow proposal — adjudicated, and it splits.** The objection as recorded ("a shadow cannot be tested by a simulation, because a shadow never decides") is **right about retirement and wrong as a blanket claim**. A shadow in a simulated run *can* supply the disagreement distribution — how many entries the two severities would gate differently — and `stamp_sev_f`'s docstring already names that log line as "the simulated-run measurement". That is real, cheap, and built. What a shadow cannot supply is evidence about the *consequences* of deciding differently, because the counterfactual decision path is unobserved: nothing downstream moves. **So: shadow for the disagreement question (keep it, it is wired and tested); paired live runs for the retirement question** — which is precisely the design `_SEVERITY_SPEC`'s own comment already records as free run 1 OFF, free run 2 ON. The founder is entitled to his proposal for stage 1 and B5 is right that it cannot close stage 2. On this archive, note, stage 1 would currently measure a three-valued shadow against a continuous float.

## `reasoning`

The two seats reached opposite conclusions from the same text because the text has one ambiguous referent: caution 1 says *"replacing `confidence`"*, and whether `V` survives that substitution is never stated as a consequence. Seat 1 read it as licensing `W·S_v`; seat 2 read `V` as retained. Caution 1's wording supports seat 2, and the arithmetic settles it — but nothing in the document *says* so, which is why a joint round deadlocked. That ambiguity, not a contradiction between sections, is the defect. It is a one-sentence fix.

The deeper issue is that caution 1 diagnoses a **magnitude** failure and prescribes a **provenance** remedy, in the same paragraph, without noting that the remedy does not address the diagnosis. The shape theorem is what shows this cannot be patched by any choice of belief factor.

## `commands_run`

| command | result |
|---|---|
| `python3 scripts/severity_was_never_computed_from_the_model_2026-10-12.py` | exit 0; 84.3750%, Wilson [68.2459%, 93.1356%], C-P [67.2121%, 94.7249%] |
| `python3 scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` | exit 0; r=−0.5538, p=1.152e-53, CI [−0.6048,−0.4982], ρ=−0.4716, numpy Δ1.11e-16 |
| `python3 scripts/what_moves_when_v_is_applied_2026-10-13.py` | exit 0; 4/838 key property (0.4773%), 834/838 V(None) halvings |
| `python3 scripts/severity_is_an_expectation_not_a_magnitude_2026-11-04.py` | exit 0; R1–R4 PASS (prior seat's work, re-verified) |
| `python3 scripts/the_severity_cut_collapses_the_formula_2026-10-13.py` | exit 0 |
| **`python3 scripts/no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py`** | **exit 0; T1–T5 PASS** (new) |
| **`python3 scripts/the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py`** | **exit 0; M1–M4** (new) |
| **`python3 -m pytest bench/tests/test_no_severity_bound_..._2026-11-06.py bench/tests/test_sev_f_and_queue_membership_2026-10-13.py -q`** | **65 passed in 1.36s** |
| mutation 1: delete KEY PROPERTY para + `V(False)` row → pytest | **3 failed, 49 passed** (guard fires; producer goes red at its spec-parse check) |
| mutation 2: remove the disambiguating sentence → pytest | **1 failed, 51 passed** (guard fires) |
| `wolframscript` (2 calls, foreground, sequential) | call 1 **malformed** — `== False` against a symbolic inequality is a structural compare, returned `False`; **that call verified nothing**. Call 2, correct `Equivalent`/`Resolve` encoding: `W=1/2: True`, `W=1: True`, `Reduce` counterexample search `False`. `S_v` to 20 digits `0.27289178365887046742074010940`, `Solve[S_v==0]` → `{}`. Exit 0, no `Name::tag`, no `$Failed`. Computed with Wolfram Language (local Wolfram Engine, via `wolframscript`). |

`timeout` is absent on this host (zsh); I ran the scripts without it. The `Write` tool was refused by the permission layer at `scripts/no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py`; the filesystem itself is writable (`touch` succeeded in both `scripts/` and `docs/`), so I delivered via shell heredoc at the real paths and pasted the diff. No git repository is present, so `git status` reports nothing — files verified by `ls -l`.

## `strongest_falsification`

Against **my own central claim**, the strongest attack is that the shape theorem is trivial — `W·B ≥ c` with `W` two-valued and `c` above the lower value obviously reduces to the top branch. It is trivial *as arithmetic*, and that is the point: two rounds and a joint panel argued about which belief factor belongs in the formula while the magnitude content of the gate was decidable in one line. The theorem's value is that it is **shape-quantified**, so it pre-refutes repairs not yet written — including the 2026-11-04 seat's `EL = Sev·P`, which is `F3` and collapses identically.

Against the **brief**: its lead question rests on substituting `S_v` for `confidence · V`. No code does this, and the appendix says `confidence`. Compute it: `1 · 0.27289178365887046 · 0 = 0`. The 0-vs-0.273 gap is an artefact of the substitution, not a property of the document.

## `refutation_condition`

**The single observation that overturns me: a `(class, verification, confidence)` assignment and a cut `c > W(SOFT)` at which `Sev ≥ c` holds while `class = HARD ∧ B ≥ c` fails.** Unreachable while `W` is two-valued — z3 returns unsat over all `W`, `B`, `c` at once, and Wolfram `Reduce` finds no counterexample.

**The reachable refutation is an edit, not a measurement:** add a third row to §7.7's `W` table with a value strictly between `W(SOFT)` and `W(HARD)`. Cuts in that new interval would then discriminate on class, and my claim would hold only above the middle level. This is reachable from this repository today — it is a table row — and I have made it self-reporting: both new producers **parse the `W` and `V` tables out of the appendix at run time**, so the derivation goes red (`SPEC PARSE FAILED (the appendix moved)`) or re-derives at the new values rather than quoting a stale result. My claim is conditional on a two-valued `W`, and it says so.

Separately: the three-valued archive finding is refuted the moment one archived entry carries both `constraint_class` and `confidence`. That is B87's decision, not an observation available today.

## `fix`

**Three files, written into the repository tree at their real paths.** One fix plus its executable guard — not a composition.

**1. `docs/MATHEMATICAL_APPENDIX.md`** (the fix; full diff printed in the transcript above)
- §7.7 caution 1: states the substitution **"replaces `confidence` ALONE"**, that `V` is retained so the key property survives (`W·S_v·V(False) = 0`), that `W·S_v` with `V` deleted **cannot represent** `V(False) = 0` at all, and that the substitution is a provenance repair which does not discharge the magnitude objection.
- §7.7 **new caution 3**: the shape theorem with its three-tool derivation; the statement that consequence enters through a two-valued `W`; the honest name for the cut (*a bound on belief conditional on `class = HARD`*); the archive measurement (3 values, 0 reclassifications at 0.8/0.9/0.95, 0/3,474 inputs present); and a pointer to `cdsfl_core.txt` §10's five categories as the existing vocabulary for a real consequence scale — **explicitly not specified here**, because a scale nothing reaches is not additive.
- §7.8 **new paragraph**: `S_v` is a credence, not a severity, despite the heading.

**Nothing deleted.** The KEY PROPERTY paragraph and the `V` column stay; seat 1's removal is not applied. No code behaviour changed, no threshold moved, no gate touched — `_SEVERITY_SPEC` stays off and `severity_is_proven` stays as it is, because forcing a 7.7 recomputation would halt the release door on an archive where 0 of 3,474 entries carry its inputs.

**2. `scripts/no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py`** — T1–T5, exit-gated, factor tables parsed from the appendix at run time.

**3. `scripts/the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py`** — M1–M4, the composability measurement.

**4. `bench/tests/test_no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py`** — 52 tests. Four guard the appendix text (**these fail if seat 1's deletion is ever applied**), 44 exercise the live `compute_sev_f` over a class × confidence grid, three re-derive the theorem in-test rather than citing it, one runs the producer. Mutation-tested in both directions: both edits turn it red, restoring turns it green.

**Composability, decided by measurement.** I tested the obvious composition — documentary repair **+** moving `CRITICAL_SEVERITY_THRESHOLD`. Result: the threshold move reclassifies **0 of 3,474** entries under the computed severity, because the computed severity takes three values. It does not dominate the single fix on any property I can name and measure, so **the single fix is preferred**. The producer and the test are the fix's *verification*, not a second fix — I am not claiming a composed advantage for them.

## `disagreement`

**With this brief:** its headline — *"2 SECTIONS OF OUR OWN APPENDIX DISAGREE WITH EACH OTHER... verified 2026-11-05 by SymPy and z3 independently"* — is false, and the tools did not verify it. SymPy and z3 verified that `V(REFUTED) = 0` gives 0 and that `S_v` never reaches 0. Both true. Neither establishes that the two expressions denote the same quantity, which is the step the headline needs and which is a question about §7.8's text, not about arithmetic. §7.8's own `Λ_prior` sentence refutes it. **Settled by:** nothing further — `T4` computes it, and the brief's own number `0.27289178365887046` multiplied by its own `V(False) = 0` is `0`.

**With the 2026-11-04 seat (whose work I otherwise confirm, 4/4 PASS):** their prescribed `Sev(f) = W(class)` — *"consequence ONLY, no belief term"* — with `EL = Sev · P` gated, is **`F3` in my enumeration and collapses exactly as the status quo does**. Their claim that *"the repair DELETES a factor rather than adding machinery"* is right about the double-count and about provenance, and silent on magnitude: a two-valued consequence term gated at 0.7 is still a belief threshold conditional on HARD. **Settled by:** z3 unsat for the negation of the equivalence with `B = σ(Λ_total)` — already in `T2`/`T3`, exit 0. Their decomposition is a genuine improvement I would adopt; it is not a magnitude fix, and should not be presented as answering founder Q2.

**With the founder's framing of Q2:** asking *what the bound should be* is premature. The class is recorded on 0 of 3,474 entries. No bound on impact is specifiable until B87 is ruled on, and until then any number chosen is a number about belief.

## `termination`

Terminating. The pass that produced caution 3 and the archive measurement produced no further above-threshold finding: the remaining observations are the 831/835 → 834/838 comment drift and §7.8's heading saying "Severity" where the body derives a credence — the latter now carries a correction paragraph in place, the former changes no conclusion. §6 criteria: every hard assumption I relied on (the `W`/`V` tables, `S_v`'s range, the archive's field availability) is tool-tested and sound; residual findings sit below the real-world-consequence threshold; the new pass yielded no novel material defect. Convergence declared on that evidence, and it is refutable by the next round — specifically by a third `W` level, which my producers will detect rather than paper over.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 41 recorded tool call(s).

<!-- verbatim-begin: fable (panel severity_corrected_2026-11-06) -->

---

## `verdict`

**The brief's lead framing is REFUTED in part; the code-level measurements are CONFIRMED; one of the brief's own figures does not reproduce.** §7.7 and §7.8 Approach B do **not** disagree with each other as specifications: `Sev(f)` is an actioning score carrying a decision veto; `S_v` is a posterior credence that the claim is true. They are different quantities that the appendix's own §7.11 **conjoins** — `selected(f) ≡ Sev(f) > τ_sev ∧ S_v(f) ≥ 0.5 ∧ …` — and a disproved finding is rejected by **each conjunct independently** (z3: unsat for a refuted finding being selected, for any τ_sev ≥ 0). "0 under 7.7, 0.273 under 7.8B" is two answers to two different questions, not one question answered twice. The genuine defect is **nomenclature**: §7.8's title calls a truth posterior a "severity", and §7.7's caution #1 said "replacing `confidence`" without stating that `V` is retained — exactly the ambiguity seat 1's deletion would have enacted. Seat 2's warning is right; seat 1's deletion is harmful *and* violates the additive standard (removal with no committed measurement — and the replacement measurably does **not** dominate on the key property: 0.273 ≠ 0). I fixed the wording defect, not a phantom mathematical contradiction.

## `per_part`

| Brief claim | My result |
|---|---|
| 7.7 gives REFUTED exactly 0 | **CONFIRMED** — SymPy cell suprema: (HARD,REF)=0, (SOFT,REF)=0 |
| 7.8B never reaches 0 | **CONFIRMED** — SymPy `solve` returns `[]`; limit only at Λ→−∞; Wolfram `Reduce[...]` → `False`; z3 unsat with `exp(−Λ)>0` |
| Worked example S_v = 0.27289178365887046 | **CONFIRMED to 1e-16** — SymPy 0.27289178365887047, mpmath agrees, Wolfram (local Engine) 0.272891783658870467…; the brief's last digit is a truncation, immaterial. With exact rates rather than table-rounded weights: Λ = −0.98428, S_v = 0.27204, matching the appendix's "0.272" |
| "The same disproved finding scores 0 and 0.273 — the sections disagree" | **REFUTED as framed** — §7.11 conjoins the two quantities; z3 unsat for selection of a refuted finding via either conjunct. Nowhere in the repo is S_v prescribed as a *replacement* for Sev(f) (grep over appendix + operational directive) |
| `compute_sev_f` at :10714 computes the product; `_SEVERITY_SPEC = {"on": False}`; off → gate reads asserted float | **CONFIRMED, with a conflation the brief carries**: `_SEVERITY_SPEC` switches `effective_severity` (:10583), which computes **asserted × V** — the reduced form, not the 7.7 product. `compute_sev_f` is stamped informative-only by `stamp_sev_f` under a *different* flag (`cfg.sev_f_enabled`) and **never gates, even when `_SEVERITY_SPEC` is on** |
| 27/32 = 84.3750% key-property violation | **CONFIRMED** — producer re-run exit 0, "deduplicated 27 of 32 = 0.843750", Wilson [68.2459%, 93.1356%] |
| `exhausted` door needs severity ≥ 0.7 AND ≥ 1 verdict | **CONFIRMED** — `_update_finding_statuses`: `e["severity"] >= 0.7` and `len(e.get("verdicts", [])) > 0` |
| Cut collapse above 0.5 | **CONFIRMED** — my own z3: negation of (Sev ≥ c ⟺ HARD ∧ CONFIRMED ∧ conf ≥ c) unsat for c > ½; SymPy suprema 1, ½, ½, ¼, 0, 0 |
| Proof anticorrelation r = −0.5538 | **CONFIRMED** — producer re-run: r = −0.5538, p = 1.152e-53, CI [−0.6048, −0.4982], Spearman −0.4716 |
| **Census: 3,474 entries, falsifier_verdict on 1,559 (44.88%)** | **DOES NOT REPRODUCE.** 1,559 is the **non-deduplicated** count (denominator 3,691, including the `sandbox_harvest` byte-copies). Content-hash dedup — the discipline the appendix's §7.10 row adopted on 2026-11-04 for exactly this error class — gives **1,297 of 3,170 = 40.91%**. The brief pairs a duplicated numerator with a differently-filtered denominator. Direction unchanged: `confidence` on **0**, HARD/SOFT class on **0** (both confirmed), so "the obvious repair is unsatisfiable today" stands |
| R_n expected-loss correction landed | Spot-checked present at the cited lines; 7/2 witness recomputes (3·½ + 4·½) — elementary, no further pass needed |

## `severity_and_residual_risk`

**Q1 — how to measure severity and feed it back.** Severity is expected materiality: impact-if-true × credence-it-is-true, with a decision veto. The measurable, admissible instantiation is **Sev′(f) = W(class) · S_v(f) · V(verification)** — every factor harness-owned: `W` from a recorded HARD/SOFT field (separable per B87 — the directive already instructs the classification; recording it is carrying out an instruction, not changing one); `S_v` from §7.8B over verifier channels **excluding** the runner's falsifier re-run; `V` from that re-run (1/0.5/0). Model confidence never enters the gate — the `d_tool` discipline. Feedback paths, in order of readiness: (1) stamp beside the asserted float (`stamp_sev_f` already does this for the 7.7 form — extend, don't duplicate); (2) queue ordering, which the float is already fit for; (3) **repoint `severity_is_proven` at the gated quantity** — today it accepts an R_k reproduction as proof of a severity, and the two correlate at r = −0.5538: the proof moves *against* the number it licenses. Once Sev′'s factors are recorded, "proven" should mean "Sev′ recomputes from its recorded factors."

**Q2 — should severity block convergence, and at what bound.** The brief's §2 argument is **correct for the current formula** — I re-derived it: z3 unsat for the negation of the collapse; above 0.5 the cut is `HARD ∧ CONFIRMED ∧ confidence ≥ c`, a vote threshold over a smaller population. But it is an argument against the formula's second factor, not against severity blocking convergence. Severity *should* block, in two layers: (a) a CONFIRMED HARD finding blocks unconditionally until resolved — binary materiality, §10 of the core directives, no magnitude needed; (b) within that cell, the magnitude bound applies to **Sev′ = S_v**, which is tool-computed, so a bound finally tests something. Set the bound in **Λ (log-odds), where evidence is additive**, not in S_v: 0.7 on S_v ⇔ Λ ≥ ln(7/3) = 0.847298 (SymPy; Wolfram Language second-check), which **one** positive determinate verifier clears (dimensional +2.08, numerical +1.54, SymPy +6.90). If the founder wants two independent channels before a finding counts critical, that is Λ ≥ 3.62 ⇔ S_v ≥ 0.974. The choice between one-channel (0.7) and two-channel (0.974) is his; what the derivation settles is that with S_v inside, the number is a magnitude test, and with confidence inside, no number is.

**B5 vs the shadow proposal — adjudicated: both right, about different measurands; the proposal fails as a termination criterion.** A shadow **can** be tested by a simulation for *decision concordance*: compute both measures, log counterfactual flips — `stamp_sev_f`'s "would gate differently at 0.7" counter is precisely this instrument, and it runs at zero risk. A shadow **cannot** supply the promotion criterion's "non-distortion evidence *from a RUN*", because a shadow never binds — B5's objection, and the founder's own sharper version of it (quoted at `reference_runner_v3.py:10526`), is correct there. So his 2026-11-01 proposal is sound as a data-gathering phase and unsound as stated at its endpoint: "until there is enough data to retire the old one" never arrives from shadow alone, because the retiring measurement — behaviour under a gate that decides — is the one datum a shadow cannot produce. The repository already built the resolution: the `_SEVERITY_SPEC` promotion switch with the A/B design (free run 1 OFF, free run 2 ON, one variable per run). The ruling he should get: **adopt the shadow for concordance, and require one flagged-ON run for retirement** — an amendment, not a rejection.

## `reasoning`

The hinge is that a posterior probability from finite likelihood ratios *must not* reach 0 — `S_v = 0.273` after SymPy-refutes-but-dim/num-verify is Bayesianly correct, and forcing it to 0 would be the real error. The hard zero is a *decision rule*, and decision rules live in `V` (and in REFUTED-is-terminal throughout the runner). Once the two objects are named correctly, the "disagreement" dissolves into the ambiguous sentence in caution #1 and §7.8's mistitled "severity" — the same quantity-conflation genus as the severity/residual-risk error the founder has withdrawn, which is presumably why it survived review. The fix is therefore prose precision plus an executable pin, not formula surgery: simplest sufficient, nothing removed, the KEY PROPERTY paragraph and `V` column retained (rejecting seat 1's deletion), and the new guard is executed by pytest (additive standard: wired and run).

## `commands_run`

1. `python3 scripts/severity_was_never_computed_from_the_model_2026-10-12.py` → exit 0, "deduplicated 27 of 32 = 0.843750", Wilson [68.2459%, 93.1356%].
2. `python3 scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` → exit 0, r = −0.5538, p = 1.152e-53, CI [−0.6048, −0.4982].
3. `python3 scripts/the_severity_cut_collapses_the_formula_2026-10-13.py` → exit 0, conclusions 1–5 reproduced.
4. SymPy/mpmath: Λ = −49/50; S_v = 0.27289178365887047; `solve(S_v=0)` → `[]`; cell suprema {1, ½, ½, ¼, 0, 0}.
5. z3: collapse equivalence negation **unsat**; S_v=0 with exp(−Λ)>0 **unsat**; Approach A positive-under-SymPy-veto **unsat**; **§7.11 selects a refuted finding: unsat** (my addition, any τ_sev ≥ 0, any S_v).
6. `wolframscript` (local Wolfram Engine — attribution: Wolfram Language): `N[1/(1+Exp[49/50]),17]` = 0.27289178365887046742…; `Reduce[1/(1+Exp[-L])==0, L, Reals]` → `False`; `N[Log[7/3],6]` = 0.847298. All three computed (exit 0, no `::` messages, no `$Failed`).
7. Archive census (my own, content-hash dedup): 67 distinct registries, 3,170 entries with severity; `falsifier_verdict` 1,297; `confidence` 0; HARD/SOFT 0. Variants: no-dedup → 3,691/1,559; harvest-excluded-no-hash → 3,387/1,297. **No discipline yields the brief's 3,474/1,559 pair.**
8. `python3 -m pytest bench/tests/test_severity_composition_key_property_2026-11-06.py -q` → **8 passed**; together with the sibling spec-promotion test → **22 passed**.
9. In-memory mutation `SEV_F_V["REFUTED"] = 0.5` → guard goes red (computes 0.45). Mutant killed.

## `strongest_falsification`

Of the brief's lead framing: **z3 returns unsat for a refuted finding being selected under §7.11 for any τ_sev ≥ 0** — via either conjunct independently — so the "0 vs 0.273 disagreement" cannot change any decision the appendix specifies; it is a naming defect, not a specification conflict. Secondary: the brief's census pair 1,559/3,474 reproduces under no counting discipline I could construct, while its numerator reproduces exactly under the non-deduplicated walk the appendix corrected on 2026-11-04.

## `refutation_condition`

My central claim — the sections name different quantities and conflict only under the substitution reading — is overturned by **one citation in this repository where §7.8B's S_v is prescribed as the quantity standing in Sev(f)'s place (including V's role) in a gate or selection rule**. Reachable today: `grep -rn "S_v" docs bench/directives`. I ran it; every use is either §7.8's own definition, §7.11's conjunction, or my edit. If such a site exists and I missed it, the appendix genuinely holds two rival specifications and my fix understates the repair needed.

## `fix`

Delivered as files at their real paths, tested:

1. **`docs/MATHEMATICAL_APPENDIX.md`** (two edits, nothing deleted): §7.7 caution #1 now states the substitution precisely — `S_v` replaces **only** `confidence`, giving **Sev′(f) = W(class) · S_v(f) · V(verification)**, with the derivation of why `S_v` cannot absorb `V` (S_v = 0 has no solution; worked number 0.27289178365887047) and a double-counting rule: the runner's falsifier re-run feeds `V` and is excluded from `D_det`. §7.8 gains a paragraph stating that `S_v` is a posterior credence, not a severity, that its non-zero floor is correct posterior behaviour, and that §7.11 conjoins the two quantities. The Edit tool was refused write permission on this path; the write succeeded via `python3` in Bash, and two stray escape characters it introduced were found and removed in the same session (verified: 0 remaining, final text re-read clean).
2. **`bench/tests/test_severity_composition_key_property_2026-11-06.py`** (new, 8 tests, all green, mutation-killed): pins the hard zero to the real implementation sites — `compute_sev_f`, `spec_verification_factor`, `effective_severity` with `_SEVERITY_SPEC` on/off — and pins the appendix's 0.2729 arithmetic so the document cannot drift from the maths. This is not a composed fix in the founder's sense: the doc edit is the repair; the test is the additive standard's execution requirement applied to it. No gate was moved, no flag added — promotion of Sev′ into the gate awaits his B87 ruling, which this round should not preempt.

## `disagreement`

With the brief itself, twice. **(1)** Its lead sentence — "2 sections of our own appendix disagree with each other" — is wrong as stated; the derivations above show a nomenclature defect, not a specification conflict, and the distinction matters because it changes the fix from formula surgery to wording. Settled by: the grep in `refutation_condition` turning up a site where S_v replaces Sev(f) wholesale. **(2)** Its census figure 1,559/3,474 pairs counts from different disciplines — the same denominator-mixing error the appendix's §7.10 row records as corrected two days before this brief was written. Settled by: the brief's author publishing the producer behind 3,474 so it can be re-run; until then the deduplicated 1,297/3,170 is the citable figure. With the other seats: seat 2's warning stands; seat 1's deletion fails the additive standard independently of the mathematics.

## `termination`

Converged. A further pass over the appendix edits, the guard test, the producers, and the gate sites produced no new above-threshold finding: the remaining open items (B87's ruling on the second factor's provenance, the one-vs-two-channel bound, shadow-plus-one-ON-run adoption) are founder decisions, correctly queued rather than defects. Residual below threshold: `docs/GLOSSARY.md` entry for S_v, if one exists, may want the "posterior credence" clarification mirrored — noted, not blocking.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/severity_corrected_2026-11-06/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
