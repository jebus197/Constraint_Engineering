# CORRECTED BRIEF -- severity and residual risk, with the error the last brief carried

> ## ★ THIS BRIEF'S OWN LEAD CLAIM WAS REFUTED BY THE ROUND IT DISPATCHED. BANNER ADDED 2026-11-07.
>
> **Read this before reading anything below.** The brief's lead question, stated in
> SECTION 1 and closed at the sentence beginning *"So the same disproved finding scores 0
> under 7.7 and 0.273 under 7.8 Approach B"*, asserts that 2 sections of
> `docs/MATHEMATICAL_APPENDIX.md` contradict each other. **They do not.** Both free seats,
> cc2 and fable, reached that conclusion independently and from their own reading of the
> appendix, and it was then checked directly against the appendix text.
>
> **§7.11 of the same appendix requires BOTH quantities at once**: a finding is selected
> only if its severity exceeds one threshold AND `S_v` is at least 0.5. They are 2 measures
> used together, not 2 competing definitions of 1 measure. §7.8 states its own prior as the
> probability that a claim is TRUE before verification, so `S_v` is a credence about truth,
> not a measure of consequence. The 0 against 0.273 gap was produced by substituting 1 for
> the other, which neither the appendix nor the code does anywhere.
>
> **The claim of tool verification was the more serious error.** The brief says the
> contradiction was verified by 2 independent mathematical tools. Both tool results are
> TRUE -- the 3-factor product is 0 when its verification factor is 0, and `S_v` never
> reaches 0 -- and neither establishes that the 2 expressions name the same quantity, which
> is the step the headline needed and is a question about what §7.8 says rather than a
> question of arithmetic. 2 true answers were attached to a conclusion neither supported.
>
> **The underlying cause is a naming collision, now documented in the appendix.** `S_v` is
> called multi-verifier Bayesian SEVERITY in the selection section and in the glossary while
> §7.8 derives a probability of truth. A clarification now stands in
> `docs/MATHEMATICAL_APPENDIX.md` under the heading beginning *"`S_v` is a credence, not a
> severity"*, pinned by
> `bench/tests/test_the_severity_factor_values_are_pinned_2026-11-06.py`. It is named by its
> heading rather than by a line number, because a line number drifts and a heading does not.
>
> **What survived, and was made stronger:** the argument that no severity threshold above
> 0.5 tests how bad a finding is, because the only factor carrying consequence has 2 values.
> 1 seat generalised it from this formula to every formula of the same shape, with the
> threshold left free rather than tested at chosen values.
>
> **The census figures below are also superseded**: the archive total of 3,474 counts each
> seat's private copy of the repository as a further run. The authoritative total is 3,170 by
> whole-file digest de-duplication, and 1,297 of those carry a falsification verdict, because
> the verdict field is an EMPTY STRING on 305 findings. The conclusion is unaffected in every
> frame, since the factor the formula needs is recorded on 0 findings in all of them.
> Producers for those 4 figures, so they travel with the code that makes them:
> `scripts/severity_was_never_computed_from_the_model_2026-10-12.py` for the digest
> de-duplication, and `scripts/the_severity_census_has_three_frames_2026-11-06.py` for the 4
> frames side by side. They are NOT in this brief's declared-figures block and cannot be:
> that block was written before the round, and these are figures the round produced. The
> validator's figure-coverage warning rose from 24 to 25 for exactly that reason, which is
> the brief-artefact integrity question already open as entry B125.
>
> **The original text is left standing below, unedited, because it is the record of what the
> seats were actually asked.** Full record:
> `experimental_notes/Free_Panel_Severity_Corrected_2026-11-06.md`.


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
  `bench/reference_runner_v3.py:10878` computes the product exactly, including the hard 0.
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
