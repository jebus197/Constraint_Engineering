# The severity proof licenses a door on a different number, and the consequence weight has 2 values

Record written 2026-11-14T05:17:14+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

This round put to the 2 free seats what should happen to the 2 parts of the old severity formulation that the per-domain ordinal reformulation did NOT change: `severity_is_proven` in `bench/reference_runner_v3.py`, which licenses a release door on a proof of a different quantity, and the 2-level consequence weight `W` in `compute_sev_f`, which can express exactly 2 severities.

It exists because the founder asked for it in the outstanding-work document of 2026-11-12, and his instruction was CONDITIONAL: run a fresh round if the questions were not asked last time. That condition was measured before anything was dispatched rather than assumed in either direction. All 3 of the issues he named did reach the brief of the 2026-11-11 round, and 3 of the 4 repairs that round put in play are live in the tree. The 4th, the repointing of the proof door, is not, and the 2-level weight had been handed to that round as an established FACT in its brief and never put to it as a QUESTION. That gap is what this round closes.

WHAT WAS DONE WITH THE FINDINGS. Both seats REJECT a 3rd consequence weight, on 2 independent and separately fatal grounds, and both HOLD the proof repointing for the founder because it changes what a release door admits. Nothing from either seat is adopted into the live runner, under the standing rule that a panel's fixes go to the human and are never auto-applied; the repairs sit in the harvested sandboxes. The brief's own self-falsification, that the 3rd weight and the ordered pair are mutually exclusive, came back CONFIRMED in conclusion and REFUTED in reason, and that refutation was re-derived independently on SymPy and z3 before being recorded. The brief also undercounted the frozen cut's spellings at 4 against a true 6, found by the `fable` seat and verified by enumerating every function carrying that parameter. Entry B143 records the outcome.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# BRIEF — the severity proof licenses a door on a different number, and the consequence weight has 2 values


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `experimental_notes/Panel_FULL_RECORD_Severity_Is_Ordinal_2026-11-11.md` | `097f8e02cefbf5f2` | 89373 | 2026-11-11T22:48:11+00:00 |
| `bench/directives/universal/cdsfl_core_formal.md` | `9da304edb6c80a60` | 31909 | 2026-11-12T03:58:04+00:00 |
| `bench/cdsfl_registry/domain_manifest.toml` | `501a257dbe67e8a5` | 25184 | 2026-11-12T03:47:08+00:00 |
| `docs/MATHEMATICAL_APPENDIX.md` | `b86878ca26ff337d` | 206307 | 2026-11-13T23:56:20+00:00 |
| `bench/reference_runner_v3.py` | `9f689c6505d36c49` | 1280002 | 2026-11-13T21:28:38+00:00 |
| `bench/evidence.py` | `731ff271983e30fc` | 49981 | 2026-09-10T03:16:37+00:00 |
| `bench/audit_closing_window.py` | `c2bf7ad7601ca997` | 13647 | 2026-09-01T12:24:12+00:00 |
| `bench/convergence_location.py` | `ea76b2852c07ee8d` | 65644 | 2026-09-01T12:24:12+00:00 |
| `scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` | `6378b3becdc1768b` | 5602 | 2026-10-12T20:05:19+00:00 |
| `bench/tests/test_verified_true_ledger.py` | `85cda836deccd6be` | 26904 | 2026-09-01T12:24:12+00:00 |
| `bench/cdsfl_registry/composer.py` | `eb836387286a87a3` | 117190 | 2026-11-13T21:27:13+00:00 |

## REQUIRED SECTION 1 — The question

**The single question: now that severity has been reformulated as a per-domain ordinal quantity, what should happen to the 2 parts of the old formulation that were NOT changed — `severity_is_proven`, which licenses a release door on a proof of a different quantity, and the 2-level consequence weight `W`, which can express exactly 2 severities?**

Each part needs its own verdict. They may or may not compose; section 3 states the standard under which a composed answer is admissible.

**WHY THIS ROUND EXISTS, AND IT IS NOT BECAUSE THE QUESTIONS WERE NEVER ASKED.** The founder asked, 2026-11-12: *"We identified that the maths model sits at a higher level of abstention, that the 0.7 cut was effectively meaningless and that the real measure of severity is entirely domain dependent. Why weren't these issues resolved the last panel review? If you didn't ask them, you should run another fresh free panel review to resolve these questions."* (His *abstention* is *abstraction*.)

That condition was MEASURED before this brief was written rather than assumed. All 3 of the issues he names reached the brief of the round of 2026-11-11 recorded in `experimental_notes/Panel_FULL_RECORD_Severity_Is_Ordinal_2026-11-11.md`: the abstraction question as its Q6, the frozen cut as its Q4, and domain-dependence as the whole subject of the round. So the honest answer to him is that they WERE asked, and 3 of the 4 repairs that round put in play are now live in the tree:

1. The ordinal reformulation of the convergence term IS applied — `bench/directives/universal/cdsfl_core_formal.md` line 418 onward now carries the per-domain ordering, the per-domain critical level, and a convergence term that SELECTS a maximum rather than summing.
2. The per-domain scale table IS applied — `bench/cdsfl_registry/domain_manifest.toml` now declares a named external scale and a named critical level per domain, with a source URL.
3. The credence finding IS recorded — `docs/MATHEMATICAL_APPENDIX.md` around line 1473 states that the old product is a credence formula wearing a consequence name, and writes the ordered-pair form.
4. **The repointing of `severity_is_proven` is NOT applied.** `bench/reference_runner_v3.py` line 10784 still returns `severity_proof_status(entry) in _RK_PROOF_ACCEPTED`, so a reproduction of the recursion depth `R_k` is still accepted as evidence for a severity claim.

**AND ONE THING WAS PUT TO THAT ROUND AS A FACT BUT NEVER AS A QUESTION.** Its brief carried measurement 3.5 — z3 asked for 4 distinct severities from `W` in `{0.5, 1.0}` returns **unsat**, with 2 it returns **sat**, so the formula expresses exactly as many severities as `W` has values. That was handed to the seats as established. No question asked them whether a 3rd weight should be added, and none of them was asked to rule on it. That is the gap this round closes.

### The artefacts under review, by path

- `bench/reference_runner_v3.py` — `severity_is_proven` at line 10784, `severity_proof_status`, `compute_sev_f`, and `CRITICAL_SEVERITY_THRESHOLD` at line 10484.
- `docs/MATHEMATICAL_APPENDIX.md` — section 7.7 at line 1253, its credence annotation at line 1473, and section 7.7.1 at line 1397.
- `bench/directives/universal/cdsfl_core_formal.md` — the reformulated guard at line 418 onward.
- `bench/cdsfl_registry/domain_manifest.toml` — the per-domain scales and critical levels.
- `bench/evidence.py` — `LEDGER_CRITICAL_SEVERITY` at line 798.
- `bench/audit_closing_window.py` — `CRITICAL_SEVERITY_THRESHOLD` at line 102.
- `bench/convergence_location.py` — the `critical_threshold` defaults at lines 1040 and 1085.
- `scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` — the producer of the polarity figure below.

### The measured facts this round starts from

**F1. The proof moves AGAINST the number it licenses.** Over 652 archived entries carrying a PASS or WARN severity proof, the proof statistic and the severity it licenses correlate at Pearson **r = -0.5538**, p = 1.152e-53, 95 per cent confidence interval [-0.6048, -0.4982], scipy and numpy agreeing to 1.11e-16, Spearman rho = -0.4716. At the proof mechanism's own tolerance of 0.05, **555 of 652, 85.12 per cent**, would stop being released. Re-run the producer; do not take the figure from this brief.

**F2. The consequence weight has 2 values and therefore ranks 2 consequences.** `compute_sev_f` multiplies a consequence weight `W` in `{0.5, 1.0}` by a belief term. z3 returns **unsat** for any assignment yielding 4 distinct severities and **sat** for 2. SymPy gives `sup(W . B) = 1/2` over the SOFT branch, so no cut above 0.5 can ever be reached on that branch, and at `W = 1` the test `Sev >= c` reduces identically to `B >= c`. Consequence magnitude therefore enters the gate through exactly 1 binary variable.

**F3. The cut is spelled 4 times outside its canonical constant, and 3 of those 4 are unpinned.** Read by importing the modules and by `inspect.signature`, not by searching text: `bench/evidence.py::LEDGER_CRITICAL_SEVERITY` is 0.7 and IS pinned against the runner by `bench/tests/test_verified_true_ledger.py`; `bench/audit_closing_window.py::CRITICAL_SEVERITY_THRESHOLD` is 0.7 and is pinned by nothing; and `bench/convergence_location.py` carries 0.7 as the default of the `critical_threshold` parameter of `hierarchical_novelty_series` and of `novelty_rule_divergence`, also pinned by nothing. All 4 agree today. Nothing makes them agree tomorrow.

**F4. The per-domain scale now REACHES a seat's prompt, which it did not on 2026-11-12.** `bench/cdsfl_registry/composer.py` made 0 calls to any severity API until 2026-11-13, so no domain's scale or critical level was delivered to any seat's directive. It now appends a severity declaration after the phenotype transform. This changes the question's stakes: a per-domain critical level is now operative rather than merely recorded.

<!-- figure: polarity_n | scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py | archived entries with a PASS/WARN R_k proof: 652 -->
<!-- figure: polarity_r | scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py | r = -0.5538 -->
<!-- figure: polarity_stop | scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py | 555 of 652 (85.12%) -->

## REQUIRED SECTION 2 — Use the harness

Form the answer by RUNNING the machinery, not by writing about it. A seat that returns prose about a fix without having executed anything has not answered.

**The instruments that bear on this question, and what each is expected to say.**

- **`severity`** is the subject. Call `compute_sev_f` directly from `bench/reference_runner_v3.py` on constructed inputs and report the outputs. It is expected to show F2 at the level of actual return values rather than symbolically.
- **The two-sided gate** is what the proof door feeds. Establish, by running it, whether repointing `severity_is_proven` LOOSENS or TIGHTENS what the gate admits, and by how much over the archive. A change of unknown direction is not a fix.
- **`gamma`** and the critical-finding series: `bench/convergence_location.py` takes the cut as a parameter at lines 1040 and 1085. Run the novelty series at 0.7 and at a per-domain level, and report whether the series changes. If it does not, say so, because an unpinned duplicate that changes nothing is a different defect from one that changes a verdict.
- **`S_k`** and the convergence location: the reformulated convergence term in `cdsfl_core_formal.md` SELECTS a maximum. Execute `bench/convergence_location.py` and say whether the live code does what the directive now asserts.
- **z3 and SymPy** for F2, and **scipy or numpy** for F1. Re-derive both; the figures above are declared so they can be refuted.

Use `python3 scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` as the starting point for F1 and say whether its figure reproduces.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. **A fix without a runnable falsifier that the seat has EXECUTED is a hypothesis, not a fix.** Report the exact command run and the output seen, pasted rather than summarised.

**WHERE THE FIX MUST BE DELIVERED.** Write it INTO the sandbox repository tree at its real path, as a file — an edited `bench/reference_runner_v3.py`, an edited `docs/MATHEMATICAL_APPENDIX.md`, a new guard under `bench/tests/`, or a new producer under `scripts/`. A fix described in prose is not delivered, and a fix written to scratch space is destroyed when the sandbox is torn down. Rounds 5 and 6 on 2026-09-10 returned 0 source files for exactly that reason while both seats reported writing and running working code.

**THE 3 CANDIDATE REPAIRS, each of which must get its own verdict.**

- **R1. Repoint `severity_is_proven`** so that the proof it demands is a proof of the quantity the gate reads, rather than of `R_k`. Name what evidence would then be required, and measure what happens to the archive: how many of the 652 entries still release.
- **R2. Add a 3rd consequence weight** strictly inside `(1/2, 1)` to the old product, which is the only change that makes any cut above 0.5 a magnitude test on the existing formulation.
- **R3. Retire the product in favour of the ordered pair** `severity_d(f) = ( c_d(f) , credence(f) )` already written at `docs/MATHEMATICAL_APPENDIX.md` line 1479, and let the domain's own ordinal scale carry consequence magnitude with no weight at all.

**THE STRONGEST AVAILABLE FALSIFICATION OF THIS BRIEF'S OWN FRAMING, STATED SO A SEAT DOES NOT HAVE TO FIND IT.** R2 and R3 may be mutually exclusive rather than composable: if consequence magnitude is now carried by the domain's ordinal scale under R3, then adding a 3rd weight to a product that has already been renamed a credence is repairing a quantity that no longer has the job. Say whether that is right. If it is, R2 is not a smaller version of R3 but a competing design, and recommending both would be incoherent.

**ON COMPOSABILITY, as the founder defines it.** Compose 2 repairs ONLY on a DEMONSTRATED advantage over each alone, where the demonstration is a MEASUREMENT and not a judgement, and prefer the single repair wherever it performs as well on the named property. Reporting that the repairs do not conflict is the weak non-interference form his definition excludes by name, and will be recorded as not having answered.

**AND THE ADDITIVE STANDARD BINDS BOTH DIRECTIONS.** R3 removes a formula. A removal is admissible only with a committed measurement showing the replacement dominates on a NAMED property. Name the property and take the measurement, or do not recommend the removal.

**A HARD CONSTRAINT ON ANY ANSWER.** R1 changes what a release door admits and R2 changes the mathematical model. Both are the founder's to rule, not the panel's to apply. Deliver the fix as a file so it is reviewable, and state plainly in the verdict that it awaits his ruling. Do not describe either as settled.

## REQUIRED SECTION 4 — What would refute you

Before concluding, state what evidence would overturn the answer. A verdict with no stated refutation condition is an opinion, not a finding. Be concrete: name the file, the command, and the result that would change the verdict.

## REQUIRED SECTION 5 — Output shape

Return these fields, named, so replies can be compared without a parser guessing.

- `verdict` — a table with 1 row per candidate repair R1, R2, R3: RECOMMEND, REJECT, or HOLD FOR THE FOUNDER, with 1 sentence of reason.
- `r1_measurement` — what repointing the proof does to the 652 archived entries, as a count and a proportion with an interval.
- `r2_vs_r3` — whether a 3rd weight and the ordered pair are composable, exclusive, or independent, with the MEASUREMENT that decides it.
- `f3_duplicates` — what should happen to the 3 unpinned spellings of the cut, and whether a per-domain cut makes a module-level constant wrong rather than merely duplicated.
- `falsifier` and `falsifier_result` — the runnable falsifier and its pasted executed output.
- `reasoning` — the derivation, premises first.
- `disagreement` — the strongest disagreement with this brief's own framing, including with the self-falsification offered in section 3. A concurring answer carries no information here, because there are no votes in this project.
- `plain_english` — 1 paragraph a non-mathematician can act on. The founder is not a mathematician and has asked twice for this question in plain English.
- `passes_run` — how many passes were run and what the last one added.

## REQUIRED SECTION 6 — Termination

Stop at diminishing returns: when a further pass produces no new above-threshold finding, where above-threshold means missing it could cause a real-world failure, an invalid release, or a wrong number reaching the founder. State how many passes were run. Do not pad with findings below that threshold.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 53 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel severity_proof_and_weight_2026-11-14) -->

All delivered, 8/8 new guards and 122 regression tests pass.

---

## `verdict`

| repair | verdict | reason |
|---|---|---|
| **R1** — repoint `severity_is_proven` at the gated number | **HOLD FOR THE FOUNDER** (built, wired, measured, default OFF) | Direction is now known and is monotone *tightening* — 555 of 652 archived entries stop releasing, 0 loosen — but it changes what a release door admits, which is his ruling. |
| **R2** — add a 3rd consequence weight in (1/2, 1) | **REJECT** | z3 shows it leaves the cut a test on model-asserted `confidence` (unsat for all four `w3` tried) and leaves the product's finding-ordering breakable by a strictly increasing re-label (**sat**). It repairs the arity of `W` without repairing the inadmissibility. |
| **R3** — ordered pair `(c_d(f), credence(f))` | **HOLD FOR THE FOUNDER** (recommended on the measurement) | Lexicographic comparison of the pair is **unsat** on the same invariance test — admissible. It is a model change, so his to rule; the appendix now records the measurement that selects it. |

## `r1_measurement`

Flag OFF: **652/652** proven. Flag ON: **97/652 = 14.88%**, Wilson [12.35%, 17.81%] still release. **555/652 = 85.12%**, Wilson [82.19%, 87.65%] stop releasing. Direction, which the count alone does not give: **555 tighten, 0 loosen**. Monotone because the repoint is conjunctive and all three live call sites admit *more* when the predicate is True (`reference_runner_v3.py` ~4442 A4 door, ~9735 reasoned withdrawal, ~10936 calibration demotion), so a strictly smaller proven set strictly shrinks what is released. F1 reproduced exactly from the brief's own producer: n=652, r=−0.5538, p=1.152e-53, CI [−0.6048, −0.4982].

## `r2_vs_r3`

**EXCLUSIVE, and the brief's own self-falsification is CONFIRMED** — with a stronger reason than the brief gives. The brief argues R2 is redundant because consequence has moved to the ordinal scale. The measurement says something worse: R2 is *inadmissible*, not merely redundant.

The deciding measurement, not a judgement: re-label the consequence classes by any strictly increasing map preserving their ordering. z3 — R2's product `W·c·Ver`: order-flipping re-label **exists (sat)**, witness `a=1, b=4, cA=3/4, cB=1/4` (A=SOFT/credence 0.75 scores 0.375 > 0.25=B=HARD/credence 0.25; after re-label A=0.75 < 1.0=B). R3's pair compared lexicographically: **unsat** — invariant. Independently confirmed on Wolfram Language (local Wolfram Engine, exit 0, no `Name::tag`): `Reduce[Exists[{a,b,x,y}, 0<a && a<b && 0<=x<=1 && 0<=y<=1 && (1/2)x > y && a x < b y], {}, Reals]` → `True`.

Composition is therefore **strictly worse than R3 alone** on the named property (invariance under strictly increasing re-labelling): the composite inherits the product's `sat`. That is a measured dominance, not the weak "they don't conflict" form.

**The additive standard on R3's removal.** R3 does not remove the formula — §7.7 is retained under its true name, `credence`. Named property on which the replacement dominates: invariance (unsat vs sat). Committed in `docs/MATHEMATICAL_APPENDIX.md` §7.7 and executed by `test_the_product_ordering_is_not_determined_by_the_consequence_ordering`.

## `f3_duplicates`

**The brief undercounts: there are six spellings outside the canonical constant, not four.** `convergence_location.py` carries `critical_threshold=0.7` on **four** functions — `combined_novelty_series`, `hierarchical_novelty_series`, `location_only_series`, `novelty_rule_divergence` — not two. Parameter defaults are invisible to a text search for an assignment, which is how two of them went uncounted. All six now pinned against the runner by `test_every_duplicate_spelling_of_the_critical_cut_matches_the_runner`.

**They are not inert.** Same archive (`exp37_evidence_20260409T050932Z`, 222 entries, 143 criticals), novelty-series sum by threshold: 0.5→89, 0.6→62, 0.7→54, 0.8→36, 0.9→12. A drift in any unpinned copy changes the measured series.

**And yes — a per-domain cut makes a module-level float constant *wrong*, not merely duplicated, and worse than wrong: type-incompatible.** The manifest's critical levels are ordinal *strings*: `'High'` (CVSS v4.0), `'7'` (AIAG-VDA FMEA — a string), `'Category 2'` (GHS), `'Grade 3'` (CTCAE v5.0). Executed: `hierarchical_novelty_series(..., critical_threshold="High")` → `TypeError: '>=' not supported between instances of 'float' and 'str'`. Pinning the six makes them *consistently* wrong; it buys drift protection today and nothing more. The real repair is that the comparison site must take a domain and an ordering, not a float — out of scope for this round and not smuggled in.

## `falsifier`

`bench/tests/test_severity_is_ordinal_guards_2026-11-14.py` (8 tests, imports the real `bench.reference_runner_v3`) and `scripts/the_proof_must_be_about_the_gated_number_2026-11-14.py`.

## `falsifier_result`

```
$ python3 -m pytest bench/tests/test_severity_is_ordinal_guards_2026-11-14.py -q
........                                                                 [100%]
8 passed in 0.76s

$ python3 scripts/the_proof_must_be_about_the_gated_number_2026-11-14.py
  proven with the door as it stands : 652/652
  proven with the proof repointed   : 97/652
  still releasing: 97/652 = 14.88%  Wilson [12.35%, 17.81%]
  STOP releasing : 555/652 = 85.12%  Wilson [82.19%, 87.65%]
    entries moved PROVEN -> UNPROVEN (gate TIGHTENS): 555
    entries moved UNPROVEN -> PROVEN (gate LOOSENS) : 0
    MONOTONE TIGHTENING over the whole archive: 0 entries loosen.
    w3=51/100: negation of 'cut == V=1 AND class-rescaled confidence test' -> unsat
    w3=3/4:    ... -> unsat      w3=9/10: ... -> unsat      w3=99/100: ... -> unsat
    R2 (product W*c*Ver): order-flipping re-label exists? sat
      witness: {b=4, a=1, cA=3/4, cB=1/4}
    R3 (ordered pair, lexicographic): verdict-changing re-label? unsat

$ python3 -m pytest <6 targeted severity/convergence/composer suites> -q
122 passed in 2.56s
```

**Delivered into the tree** (not scratch): patched `bench/reference_runner_v3.py` (`severity_proof_is_about_gated`, `_SEVERITY_PROOF_MATCHES_GATED`, `RunnerConfig.severity_proof_must_match_gated`, wired through `wire_module_mirrors`); new `bench/tests/test_severity_is_ordinal_guards_2026-11-14.py`; new `scripts/the_proof_must_be_about_the_gated_number_2026-11-14.py`; appended measurement block to `docs/MATHEMATICAL_APPENDIX.md` §7.7. All nine dispatch digests verified unchanged before editing.

## `reasoning`

Premises first. (1) `compute_sev_f` executed directly: `SEV_F_W = {HARD: 1.0, SOFT: 0.5}`, and of the six (class, verdict) cells exactly one — `(HARD, CONFIRMED)` — has a supremum reaching 0.7; inside it `Sev == confidence` exactly. So consequence enters the gate through one binary variable and places no constraint on the magnitude tested. (2) z3: three distinct weights from `{0.5, 1.0}` is unsat. (3) Adding `w3` leaves the cut equivalent to a class-rescaled confidence test (unsat for the negation, all four `w3`) — belief still does all magnitude work. (4) The directive at `cdsfl_core_formal.md:418+` now asserts severity is ordinal; a product's induced ordering is not a function of the consequence ordering (sat), a lex pair's is (unsat). (3)+(4) ⇒ R2 rejected, R3 selected, composition dominated. (5) `severity_is_proven` appears at three live sites, all in the admit-more polarity, so a conjunctive strengthening is monotone tightening — verified exhaustively over a 224-point grid and over all 652 archived entries.

Scoped note, below the material threshold and not offered as a finding: the A4 door reads `effective_severity(e)` while the other two sites read the raw `e["severity"]`. Identical today because `_SEVERITY_SPEC` defaults OFF; with both flags ON they would diverge. Recording it rather than repairing it, because repairing an untested flag combination is more surface than the problem requires.

## `disagreement`

Three, with the brief, not with other seats.

**1. F4 is false as stated.** The brief says the per-domain scale "now REACHES a seat's prompt… a per-domain critical level is now operative rather than merely recorded." The first half is true; the second is not. Measured: every reader of `severity_scale`/`critical_level` is the loader, `composer.py:888` (prose into the prompt), or a CLI printout. `grep critical_level|severity_scale` over `reference_runner_v3.py`, `convergence_location.py`, `evidence.py`, `dm/_convergence.py`, `audit_closing_window.py` returns **zero hits**. The composer's own docstring concedes it (`composer.py:879-883`). The level is rendered for a model to read and is read by no gate. "Operative" overstates it, and overstating it is how a prose-only control gets counted as enforcement.

**2. The brief's self-falsification is right for the wrong reason, and the right reason is stronger.** It frames R2 as repairing a quantity that no longer has the job — a redundancy argument. The measurement says R2 is *inadmissible on the project's own live criterion*, which holds even if one disputes whether the ordinal scale has taken the job over. I reject R2 on the sat, not on the redundancy.

**3. The brief's framing of "repoint" oversells what R1 can be.** R_k (residual risk) and `Sev(f)` (consequence × credence) are different quantities *by construction*; demanding they agree to 0.05 is not a proof of severity and I have not called it one. What it does is refuse to honour a demonstrated computation of a different number as evidence for this one. The honest repair is a harness-computed severity (§7.8 Approach B), and this round did not build it. A seat that reported R1 as "the proof now proves severity" would be reporting something the code does not do.

## `plain_english`

Two separate things were left half-fixed. **First**, a release door asks a model to show its working — but it checks the working on a *different number* from the one it then lets through. Over 652 archived cases the two numbers move in *opposite* directions. I built the fix (the door now checks the working against the number it actually releases) and measured it: it would stop 85% of past releases, and it can only ever be stricter — it can never wave something through that is currently blocked. It is switched **off** and waiting for your ruling, because tightening a release door is your call, not the panel's. **Second**, the old severity formula has a "how bad is it" dial with exactly two settings. The obvious fix is to add a third setting. I tested that and it **does not work**: with three settings the gate is still decided by the model's own confidence, just with a different pass mark per setting — and worse, the formula multiplies "how bad" by "how sure", which means if you ever renumber your severity labels (even keeping them in the same order), findings swap places. Two tools agree on this, and they disagree with the third-setting idea, not with each other. The repair you already have written down — reporting badness and confidence as a *pair* instead of multiplying them — survives that test. So: **do not add a third weight; the pair is the fix, and the two are alternatives, not partners.** Separately, the number `0.7` is written out in six places, not four; I have pinned them so they cannot drift apart. But be aware they are all going to be wrong eventually, because your domain manifest says severity levels are things like "High" and "Grade 3", and you cannot compare those to 0.7 at all — I ran it and it crashes.

## `passes_run`

**Five.** (1) digest verification of all nine artefacts and reproduction of F1. (2) direct execution of `compute_sev_f`, the z3 collapse, the ordinal-invariance test, Wolfram cross-check. (3) the six spellings read by import, and the per-domain wiring mapped — this pass produced the prose-only finding that refutes F4. (4) build, wire, archive measurement, guard test, 122-test regression. (5) novelty-series sensitivity across five thresholds (54→36→12 from 0.7→0.8→0.9, so the duplicates are not inert) and the `TypeError` demonstrating the domain level is an ordinal string the gate cannot accept — this pass is what turns F3 from "duplicated" into "type-incompatible". A sixth pass would have produced only the scoped `effective_severity`-vs-raw-float note, which is below the threshold, so I stopped.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 32 recorded tool call(s).

<!-- verbatim-begin: fable (panel severity_proof_and_weight_2026-11-14) -->

All affected tests pass (184 across the severity/mirror/threshold set). The sandbox is not a git repo; the fixes live at their real paths in the tree. One final falsification pass on my own edits found and repaired the one change-detector the extension legitimately broke (stated openly below). Terminating at diminishing returns.

---

# SEAT VERDICT — the door and the weight, after the ordinal repair

## verdict

| repair | verdict | reason |
|---|---|---|
| **R1** repoint `severity_is_proven` | **HOLD FOR THE FOUNDER** — built, default OFF, in tree | The defect is real and reproduced (r = −0.5538; the door releases a 0.45 on a proven 0.95). But the repointing strips the exemption from 422 of 519 archived escapees (81.31%), reversing most of his 2026-10-06 proven-sub-critical convergence repair. Direction is provably tighten-only (the repointed predicate is a conjunction, hence a subset). That trade is his to rule. |
| **R2** add a 3rd weight in (½, 1) | **REJECT** | z3: the product gate `W·B ≥ c` with a fixed real cut is **breakable by an order-preserving re-labelling with 3 weights exactly as with 2** (`sat` both times). R2 enlarges the inadmissible formula; it does not repair the proven defect. And under R3 the consequence verdict `c_d ≽_d θ_d` contains no `W` term, so a 3rd weight changes **zero** consequence verdicts. |
| **R3** retire the product for the ordered pair | **RECOMMEND the already-recorded form; no further removal needed** | §7.7.1 (appendix line ~1473) already states the pair and explicitly keeps §7.7 as the **credence** definition — so R3 correctly executed removes a *role*, not a formula, and the additive standard's removal clause is satisfied by measurement: pair gate `unsat` (admissible), product gate `sat` (breakable), named property = invariance under order-preserving re-parameterisation. The remaining work is the runner-side wiring (the gate still reads the 0–1 proxy), which is a build, not a ruling. |

## r1_measurement

Over the archive (re-derived, not quoted): 652 entries carry a PASS/WARN proof; **519 of them escape the blocking door today** (sev < 0.7 ∧ proven). Requiring the proof to be about the gated number at the proof's own WARN tolerance (|severity − recomputed R_k| ≤ 0.05): **97/519 = 18.69%, Wilson [15.57%, 22.27%] keep the exemption; 422/519 = 81.31%, Wilson [77.73%, 84.43%] lose it.** The brief's 555/652 (85.12%) is correct arithmetic on the wrong population: 133 of the 652 have sev ≥ 0.7 and never held the exemption, so the door-relevant figure is 81.31% of 519. Evidence required under R1 as built: PASS/WARN **and** a recomputed number that *is* the gated number within 0.05; a proof carrying no reproducible number no longer counts.

## r2_vs_r3

**Mutually exclusive competing designs, and R3 dominates.** The deciding measurements (producer in tree, output pasted below): (a) product gate breakability under order-preserving φ: `sat` with W ∈ {0.5, 1.0} **and** `sat` with W ∈ {0.5, 0.8, 1.0} — R2 leaves the proven defect intact; (b) pair gate with transported θ_d: `unsat` — admissible; (c) under R3, `W` lives in the credence coordinate and the consequence verdict reads no `W`, so a 3rd weight decides nothing the pair gate reads. The brief's self-falsification is **right**: consequence magnitude is carried by `c_d` under R3, so R2 repairs a quantity that no longer has the job. Composing them would add a dead value to a renamed belief formula — fails the founder's composability rule (no measurable advantage over R3 alone) and the additive standard (an addition nothing reaches).

**R1 + R3, by contrast, do compose on measurement:** R1 alone leaves F2 (product gate still `sat`); R3 alone leaves F1 (the door still accepts an R_k proof — the live module returned `severity_is_proven = True` for sev 0.45 / proven R_k 0.95). Each single repair fails the other's executed falsifier; the composed state passes both. That is the demonstrated-advantage form of composition, not coexistence.

## f3_duplicates

The duplicates are **live, not inert**: on `exp40_gate_20260514T020550Z` (296 entries, 28 rounds), `hierarchical_novelty_series` totals **30 / 26 / 20** novel criticals at cuts 0.65 / 0.70 / 0.75 — a drifted default changes the gamma-side series and therefore verdicts. Fix delivered: `bench/tests/test_critical_cut_single_spelling.py` pins `audit_closing_window.CRITICAL_SEVERITY_THRESHOLD` and **every** `critical_threshold` default in `convergence_location` (by import and `inspect.signature`, enumerating functions so future spellings are caught) against the runner's constant. `evidence.py` was already pinned. A per-domain θ_d does **not** make the module constant wrong: it is the APPLICATION level that the 6 `severity_scale = "none"` domains inherit, and the 2026-05-18 pre-registration forbids moving the numeric. What it forbids — and what the test now fails loud on — is drift between spellings. The genuine residual, named not fixed: a domain that declares its own scale (e.g. AIAG-VDA FMEA) has **no path into the runner's gate**, which reads only the 0–1 proxy; the composer now delivers θ_d to prompts (F4 confirmed, call site composer.py:2140) but no gate consumes it.

## falsifier / falsifier_result

Producer (in tree): `scripts/severity_door_and_weight_after_the_ordinal_repair_2026-11-14.py`. Executed output, pasted:

```
M-A  weight expressivity (z3):
  W in (0.5, 1.0):  2 distinct severities -> sat   3 distinct -> unsat
  W in (0.5, 0.8, 1.0): 3 distinct severities -> sat   4 distinct -> unsat
  SymPy: sup over the SOFT branch of W*B (B<=1, Ver<=1) = 1/2 ... at W=1, (Sev >= c) == (B >= c) identically: True

M-B  invariance under order-preserving re-labelling (z3):
  product gate, W in (0.5, 1.0):      breakable -> sat   (sat = defect present)
  product gate, W in (0.5, 0.8, 1.0): breakable -> sat   (sat = R2 does NOT repair it)
  pair gate c_d >= theta_d, theta transported: breakable -> unsat   (unsat = admissible)

M-C  the door (R1), measured on the door's own population:
  archived entries with a PASS/WARN proof:             652
  of those, escaping the blocking door (sev < 0.7):   519
  still escaping when the proof must be ABOUT the gated number (|sev - R_k| <= 0.05): 97/519 = 18.69%  Wilson [15.57%, 22.27%]
  entries LOSING the exemption: 422/519 = 81.31% -- the door TIGHTENS, and only tightens
```

Second falsifier, Wolfram Language (local Wolfram Engine via wolframscript, attribution per terms): `{-2*a*b, False, 1/2}` — the sum fails φ-admissibility by exactly −2ab, the SOFT branch can never reach 0.7 (`Reduce` → `False`), and its supremum is ½. Agrees with SymPy and z3.

F1 reproduction: `python3 scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` → `r = -0.5538, p = 1.152e-53, CI [-0.6048, -0.4982], 555 of 652 (85.12%)` — the brief's figures reproduce exactly. Live-module check: `severity_is_proven({"severity": 0.45, "severity_proof": {"status": "PASS", "recomputed_rk": 0.95}})` → `True` on the dispatched runner.

Tests delivered and run: `bench/tests/test_severity_proof_repointing.py` (5 tests: default-off byte-identical, repointed semantics, subset proof over constructed entries, mirror wiring, config field default) and `bench/tests/test_critical_cut_single_spelling.py` (3 tests). Full affected set: **184 passed, 0 failed** (`pytest bench/tests/test_the_severity_spec_*.py test_severity_proof*.py test_the_door*.py test_an_unserved*.py test_a_ruled*.py test_verified_true_ledger.py test_critical_cut_single_spelling.py test_panel_found_severity_defects*.py test_severity_calibration.py test_the_severity_predictions*.py -q`).

## Files changed/added in the tree

- `bench/reference_runner_v3.py` — 3 anchored edits: `RunnerConfig.severity_proof_about_gated_number: bool = False`; `_PROOF_ABOUT_GATED_NUMBER = {"on": False, "tol": 0.05}` module mirror + repointed branch in `severity_is_proven` (byte-identical behaviour while off); mirror wired in `wire_module_mirrors`. **Awaits the founder's ruling to enable.**
- `bench/tests/test_severity_proof_repointing.py` — new, 5 tests.
- `bench/tests/test_critical_cut_single_spelling.py` — new, 3 tests.
- `scripts/severity_door_and_weight_after_the_ordinal_repair_2026-11-14.py` — new producer.
- `bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py` — **one assertion extended, stated openly**: it exact-matched `wire_module_mirrors`' return dict, whose documented contract is "the values it set"; the extension now asserts *both* mirrors, which is strictly stronger. No assertion was loosened, skipped, or deleted.

## reasoning

Premises: (P1) the release doors (runner lines ~4442 and ~9734) test `severity < CRITICAL_SEVERITY_THRESHOLD ∧ severity_is_proven`; (P2) `severity_is_proven` reads only the proof *status*, and the proof recomputes R_k without reading `severity` — verified by executing the live function on a constructed entry; (P3) the two quantities anticorrelate over the archive (r = −0.5538). From P1–P3: the proof is a side-condition on a different number, so the door's epistemic warrant is void — F1 confirmed. For F2: executed `compute_sev_f` gives SOFT-branch sup = 0.5 and `Sev ≥ c ⇔ B ≥ c` at W = 1; z3 gives exactly |W| distinct severities — consequence enters as one bit. The 2026-11-12 ordinal proof supplies the admissibility criterion (survival of strictly increasing φ); applying it to each candidate: R2 `sat` (fails), R3 `unsat` (passes), R1 is orthogonal to φ (it fixes provenance, not scale) and is subset-monotone, hence safe to build and gate behind the founder's ruling.

## disagreement

Three points against the brief's framing. **(1) The headline figure is measured on the wrong population.** 555/652 (85.12%) counts 133 entries with sev ≥ 0.7 that the door never exempted; the door-relevant figure is 422/519 (81.31%). Materially the same conclusion, but the number that should reach the founder is 81.31%. **(2) "How many of the 652 still release" presupposes the tolerance form of R1 is the end state. It is not.** Demanding |severity − R_k| ≤ 0.05 forces numeric coincidence between two quantities the appendix now says are *different in kind* (consequence-pair vs residual risk). The tolerance form is the correct *interim* door on today's schema — it is what I built — but the terminal door under R3 is consequence-side: `c_d ≺_d θ_d` checked against the manifest, plus harness-computed credence (`compute_sev_f` / §7.8 S_v), with no coincidence requirement. The brief's R1, taken as final, would fossilise a category error at 0.05 tolerance. **(3) The brief's §2 asks whether the live code "does what the directive now asserts" and the answer is no, in one specific place:** nothing in `convergence_location.py` or the two-sided gate computes the directive's `Δ_d(K) = max` term — the gate counts criticals above a *fixed* 0.7, which the directive's own admissibility table marks inadmissible unless the level is read as the application scale's transported level. That reading is coherent today only because every archived severity is on the single 0–1 proxy; the moment a domain's own scale carries a consequence into the registry, the gate has no admissible comparison to make. That is the next build, and it belongs in the record now.

## plain_english

Two leftovers from the old severity design were examined. First, the "proof door": a finding can stop blocking release if its severity is "proven" — but the thing being proven is a different number from the severity being released, and across 652 archived cases the two actually move in opposite directions. I built the repair — the proof must now be about the released number itself — but left it switched OFF, because turning it on would make releases much stricter (about 4 in 5 currently-exempt findings would lose the exemption), and reversing your earlier convergence repair is your call, not the panel's. Second, the old severity formula can only say "serious" or "half-serious" — two levels. Adding a third level was proposed, but the maths shows that patches a formula whose job has already moved: under the new design the *domain's own scale* (CVSS for software, CTCAE for clinical, etc.) carries how bad a finding is, and the old formula survives only as a measure of how much we *believe* the finding. So: reject the third weight, keep the pair design already written in the appendix, and I also added a test that stops the 0.7 critical cut's four separate copies from silently drifting apart — I measured that a drifted copy really does change verdicts.

## passes_run

**4 passes.** Pass 1: stamp verification, F1 reproduction, code reading. Pass 2: live `compute_sev_f` grid, z3/SymPy/Wolfram derivations, archive door measurement — added the population correction (519 vs 652). Pass 3: novelty-series sensitivity run, fixes written, 8 new tests passing. Pass 4 (falsifying my own fix): swept every test touching `severity_is_proven`/`wire_module_mirrors`/the threshold — found one exact-equality change-detector my extension legitimately broke, strengthened it, re-ran the full affected set (184 passed), and confirmed the default-off path is behaviour-identical. Pass 4 added no new above-threshold finding beyond that repair → converged, declared per §10 with the evidence above: hard assumptions (door semantics, weight expressivity, cut-sensitivity, wiring) each tested by execution; residual findings (the gate's missing per-domain path) named and below this round's threshold because no domain scale yet reaches the registry.

**What would refute me:** (1) re-running `scripts/severity_door_and_weight_after_the_ordinal_repair_2026-11-14.py` and getting `unsat` for the 3-weight product breakability — R2 would then repair the defect and my REJECT falls; (2) a z3 model showing the pair gate `sat` under transported θ_d — R3's admissibility falls; (3) `pytest bench/tests/test_severity_proof_repointing.py` failing on `test_default_off_is_byte_identical_behaviour` — my claim that the tree is behaviour-unchanged pending the founder's ruling falls; (4) an archived registry where the repointed door *loosens* (any entry proven under the new predicate but not the old) — impossible by the subset derivation, so finding one would void my direction claim and the derivation both.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/severity_proof_and_weight_2026-11-14/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
