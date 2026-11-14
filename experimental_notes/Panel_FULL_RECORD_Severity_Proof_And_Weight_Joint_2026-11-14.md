# Joint round: the proof door has 3 populations, and the credence coordinate still carries the weight

Record written 2026-11-14T05:22:06+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

The JOINT half of the severity round. Each seat was shown the other's actual words and told to resolve the disagreements by measurement, to say whether agreement SURVIVES seeing the other's reasoning, and to answer the brief's own self-falsification. A concurring answer carries no information in this project, because there are no votes in CDSFL.

WHAT IT RESOLVED. The 2 blind headline figures for the proof repointing answered DIFFERENT DOORS. `severity_is_proven` has 3 live call sites which do not share a population: the A4 release door and the reasoned withdrawal are each conjoined with a severity below the cut, while the calibration-demotion site requires a severity at or above it. Re-derived independently rather than taken from either seat: of 652 archived entries carrying a PASS or WARN proof, the release and withdrawal doors lose 422 of 519 and the demotion door loses 133 of 133, and 555 equals 422 plus 133 exactly with 0 critical keepers. Those 2 per-site figures are what the founder should be given, not the aggregate.

AND IT REFUTED A SENTENCE IN THE BRIEF. The brief offered as its strongest self-falsification that a 3rd consequence weight and the ordered pair are exclusive because magnitude moves into the pair's first coordinate. The conclusion is right and the reason is false: an ordered pair is compared LEXICOGRAPHICALLY and the second coordinate still contains the weight, so a tie in the first hands the decision to it. Both blind seats had inherited the false reason from the brief. The refutation was re-derived here on SymPy in exact rationals and on z3, which returns satisfiable for the existence of such an ordering flip with an explicit witness and unsatisfiable for its negation, and a producer and guard were committed for it.

BOTH BLIND DELIVERIES WERE ALSO DEFECTIVE, which is the argument for running a joint half rather than stopping at 2 agreeing blind answers. 1 seat's runner failed a stamped guard its own selected suites did not include; the 2nd seat's delivery accepted a boolean as the proof figure, because a bool is a subclass of int in Python, so the door returned True at a severity of 0.97 with the repoint enabled. Neither repair is adopted. Entry B143 records the outcome.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

*4 nested verbatim marker(s) in this brief were made inert by the record generator, so this region stays well formed. Only the HTML-comment delimiter changed; no word of the brief or of any quoted reply was altered.*


# PANEL BRIEF — JOINT ROUND on `severity_proof_and_weight_2026-11-14`

This is the JOINT half of the blind round `severity_proof_and_weight_2026-11-14`. In the blind half each of the 2 seats answered WITHOUT seeing the others. Both replies are reproduced BELOW IN FULL, verbatim. Read the other seat's actual words before you answer.

**Disagreement is INFORMATION and is preserved. There is no compelled convergence: do NOT move toward the other seat to be agreeable. Change your position only where its EVIDENCE moves you, and say which evidence did. Where you still disagree, say so and say what would settle it.**


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `bench/reference_runner_v3.py` | `9f689c6505d36c49` | 1280002 | 2026-11-13T21:28:38+00:00 |
| `bench/evidence.py` | `731ff271983e30fc` | 49981 | 2026-09-10T03:16:37+00:00 |
| `bench/tests/test_verified_true_ledger.py` | `85cda836deccd6be` | 26904 | 2026-09-01T12:24:12+00:00 |
| `bench/audit_closing_window.py` | `c2bf7ad7601ca997` | 13647 | 2026-09-01T12:24:12+00:00 |
| `bench/convergence_location.py` | `ea76b2852c07ee8d` | 65644 | 2026-09-01T12:24:12+00:00 |
| `docs/MATHEMATICAL_APPENDIX.md` | `b86878ca26ff337d` | 206307 | 2026-11-13T23:56:20+00:00 |
| `scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py` | `6378b3becdc1768b` | 5602 | 2026-10-12T20:05:19+00:00 |
| `bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py` | `e7038f5a74807066` | 10556 | 2026-10-15T03:49:47+00:00 |

## THE PROJECT, ITS AIMS, AND ITS SPECIFICATIONS — read before answering

CDSFL is a falsification harness. Its aim is the democratisation of science for every kind of intelligence, so a mechanism that only works on code, or only on this machine, is a mechanism that misses the point. The 3 formal standards below are exacting and are not loose English.

1. **ADDITIVE** — work adds to reliability, functionality, accuracy, robustness and the project's stated aims. A feature is never disabled or removed; removal only where a COMMITTED MEASUREMENT shows the replacement dominates on a NAMED property. Symmetrically, an addition nothing reaches is not additive either: every new flag, gate or entry point must be wired to a caller and executed by a test.
2. **SIMPLEST SUFFICIENT** — the smallest change addressing the ROOT CAUSE and the downstream consequences traced before the fix.
3. **COMPOSABILITY** — the founder, verbatim, 2026-10-02: "Composability doesn't mean composing two solutions just because they can be composed. It means this principle should be applied where two composed solutions demonstrably provide a better, more robust and/or more efficient solution than either fix in isolation. Where a single fix out performs a composed one, that fix should continue to be preferred. In all cases any fix should also take the first two conditions fully into consideration also." So a composed fix needs a MEASUREMENT showing it dominates either part alone. "They do not conflict" is the weak sense his wording excludes.

Work under `a` (analyse dispassionately), `f` (FFAFP: Find, Follow, Analyse with tools, Fix, P-pass) and `sy` (use the STEM tools; every computational claim cross-verified by 2 independent tools; every proportion carries a confidence interval). The tool output IS the evidence. **Findings are confirmed programmatically or by the founder — there is no model voting.**

## REQUIRED SECTION 1 — The question

**The blind half asked what should happen to the 2 parts of the old severity formulation that the per-domain ordinal reformulation did NOT change: `severity_is_proven` in `bench/reference_runner_v3.py`, which licenses a release door on a proof of a different quantity, and the 2-level consequence weight `W` in `compute_sev_f`, which can express exactly 2 severities. You each answered without seeing the other. Both replies landed.**

**NOW RESOLVE 3 THINGS.**

**J1. Where you DISAGREE on any of the 3 candidate repairs — R1 repointing the proof, R2 adding a 3rd consequence weight strictly inside `(1/2, 1)`, R3 retiring the product in favour of the ordered pair `( c_d(f) , credence(f) )` — settle it BY MEASUREMENT, or state precisely which measurement would settle it and why neither of you ran it.**

**J2. Where you AGREE, say whether the agreement SURVIVES seeing the other's reasoning. 2 seats reaching 1 answer by 1 flawed route is not corroboration, and a canonical rule of this project is that there are no votes in CDSFL. "I concur" carries no information and will be recorded as a non-answer.**

**J3. THE SELF-FALSIFICATION THE BLIND BRIEF OFFERED AND NEITHER OF YOU MAY SKIP. R2 and R3 may be mutually EXCLUSIVE rather than composable: if consequence magnitude is now carried by the domain's own ordinal scale under R3, then adding a 3rd weight to a product that has already been renamed a credence repairs a quantity with no job left. Say whether that is right. If it is, recommending both is incoherent and the brief's own framing of R2 as a smaller R3 is wrong.**

**AND 1 FACT NEITHER OF YOU HAD.** The frozen cut is spelled 4 times OUTSIDE its canonical constant and 3 of those 4 are pinned by nothing, read by importing the modules rather than by searching text: `bench/evidence.py::LEDGER_CRITICAL_SEVERITY` (pinned by `bench/tests/test_verified_true_ledger.py`), `bench/audit_closing_window.py::CRITICAL_SEVERITY_THRESHOLD` (unpinned), and the `critical_threshold` defaults of `hierarchical_novelty_series` and `novelty_rule_divergence` in `bench/convergence_location.py` (both unpinned). All 4 are 0.7 today. Say what a per-domain cut does to those 4, and whether that changes any verdict you gave blind.

## REQUIRED SECTION 2 — Use the harness

Read and RUN the code. Do not reason from the brief alone. Do not invoke pytest across the whole tree: the heavy-process budget on this machine is 1, and a full board is already cached. Targeted test files are fine.

## REQUIRED SECTION 3 — Produce a fix, and test it

Where you find a defect, deliver the fix and the executed evidence that it works, including what you tried that did NOT work. **WRITE YOUR FIX INTO THE SANDBOX REPOSITORY TREE AT ITS REAL PATH.** A fix left in prose, or written to scratch space, is destroyed when the sandbox is torn down and has not been delivered. Supply a runnable falsifier, EXECUTE it, and quote its output.

## REQUIRED SECTION 4 — What would refute you

State, for each position you hold, the observation that would overturn it. A position with no falsifier is not a finding.

## REQUIRED SECTION 5 — Output shape

`verdict`, `composability`, `reasoning`, `falsifier`, `falsifier_result`, `strongest_disagreement`, `aims_check`. In `strongest_disagreement` name the specific claim of the OTHER SEAT you reject, and why, with evidence.

## REQUIRED SECTION 6 — Termination

Stop when a pass produces no new above-threshold finding. State how many passes you ran.

---

# THE BLIND HALF — all 2 replies, verbatim and in full

## SEAT `cc2` — its blind reply, verbatim

[verbatim-begin -->

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

[verbatim-end]

## SEAT `fable` — its blind reply, verbatim

[verbatim-begin -->

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

[verbatim-end]


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 38 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel severity_proof_and_weight_2026-11-14_joint) -->

Converged. 141 targeted tests pass; exactly one dispatched artefact changed (the appendix, intentionally). Here is my verdict.

## `verdict`

| repair | my verdict | what moved me |
|---|---|---|
| **R1** repoint `severity_is_proven` | **HOLD FOR THE FOUNDER.** I did **not** rebuild it — see below. | Both seats built it independently with matching semantics and a correct tighten-only derivation. I verified the polarity at all three call sites myself: predicate-True admits more at each, so a conjunctive strengthening cannot loosen. Agreement survives. |
| **R2** a 3rd weight in `(1/2, 1)` | **REJECT** — and on a ground **neither seat gave**, because both their stated reasons are defective. | Executed below. |
| **R3** the ordered pair | **RECOMMEND the direction; R3 as recorded is INCOMPLETE.** New finding J-A. | The `credence` coordinate still carries a consequence weight. |

**I did not rebuild R1.** Two seats delivered it; a third copy in a third sandbox is an addition nothing reaches, which is the failure mode this project has shipped 11 times. Saying so is my answer, not an omission.

## `reasoning`

### J1 — the R1 population: measured, and **neither** seat's derivation is complete

`severity_is_proven` has three live call sites and they **do not share a population**:

- **Site A** (A4 release door, 4442) and **Site B** (reasoned withdrawal, 9735): each conjoined with `severity < 0.7`. An entry at or above the cut never held their exemption.
- **Site C** (calibration demotion, 10936): **not** so conjoined. `_is_demotion_eligible` *requires* `severity >= CRITICAL_SEVERITY_THRESHOLD` (line 10662). Site C acts on **exactly the 133 entries `fable` excluded**.

```
  fable's population (sites A and B: severity < 0.7):
    entries holding the exemption today : 519
    entries LOSING it when repointed    : 422/519 = 81.31%  Wilson [77.73%, 84.43%]
  the population both headline figures mishandle (site C: severity >= 0.7):
    entries at or above the cut : 133
    of those, demotion-ELIGIBLE (live _is_demotion_eligible): 0
```

**Resolution: `fable`'s number is right and its derivation is incomplete.** Site C's eligible population in the archive is **0 of 133**, so the omission is numerically inert *today* — `_is_demotion_eligible` also requires `latent` and a CONFIRMED falsifier, which no archived entry carries. It stops being inert the moment `severity_calibration_enabled` runs on a registry with `latent` populated. **Report 422/519 to the founder, with that condition attached.** `cc2`'s 555/652 answers a different question — how many proven-statuses flip — which is the right population for the monotonicity argument and the wrong one for the door.

*Caveat I owe my own measurement:* Site A reads `effective_severity(e)`, sites B and C read raw `e["severity"]`. My partition used raw. With `_SEVERITY_SPEC["on"]` False (the default) `effective_severity` returns the asserted float unchanged, so the partition is exact today and would need redoing with that flag on. `cc2` flagged this divergence as below threshold; it is below threshold for the verdict and *not* below threshold for the measurement, which is why I state it.

### J3 — the self-falsification: **right conclusion, wrong reason, and both seats inherited the wrong reason**

R2 and R3 **are** mutually exclusive. But the brief's reason — and `fable`'s restatement of it, "a 3rd weight ... decides nothing the pair gate reads" — is **false by execution**. A pair is compared **lexicographically**. When `c_d` ties, the comparison falls through to `credence`, which contains `W`:

```
    both findings share c_d = 'High'  -> FIRST coordinate TIES
    2 weights: A(MEDIUM->HARD default)=0.900  B(HARD)=0.800  -> A > B
    3 weights: A(MEDIUM)=0.720         B(HARD)=0.800  -> A < B
    ordering changed by adding a 3rd weight: True
```

`cc2`'s reason fails differently. Its φ-invariance `sat` is a test of the **product gate**, which R3 retires. φ re-labels the *consequence* scale; `credence` is a dimensionless belief in `[0,1]`, so the φ test does not reach R2-*alongside*-R3. `cc2`'s argument is sound against R2-*instead-of*-R3 and silent on the composition it was being asked about.

**The correct reason (finding J-A).** §7.7.1 defines `credence(f)` as "today's §7.7 product under its own name" — `W(class) · confidence · Ver`. **`W` is keyed on constraint class, the core directives' §1 *consequence* partition.** So the coordinate named `credence` is not a function of the evidence alone, and the pair double-counts consequence — the exact defect §7.7.1 names ("a product of a consequence and a belief is neither") surviving *inside its own repair*:

```
  evidential-invariance test -- same evidence, different class:
    conf=0.9  CONFIRMED   HARD=0.900  SOFT=0.450   <-- credence depends on CONSEQUENCE
    ... cells where identical evidence gave different credence: 6/6
  z3: today W*conf*Ver, identical evidence different credence?  sat   (defect)
  z3: repaired conf*Ver                                      ?  unsat (invariant)
  z3: pair (c_d, credence) lex: SOFT outranks HARD?  unsat (order tracks c_d)
```
Wolfram Language (local Wolfram Engine, exit 0, no `Name::tag`) independently returned `False` for the same existential — no SOFT finding outranks a HARD one under the lex pair.

So: **`W` is not jobless, it is misplaced.** R2 refines a term R3 should **delete**. Exclusive — yes. The brief's framing of R2 as "a smaller R3" is wrong, and the brief is right by accident.

### The fact neither seat had: what a per-domain cut does to the frozen spellings

**There are six, not four** — `cc2` is right, the brief is wrong. Read by `inspect.signature`, `convergence_location` carries `critical_threshold=0.7` on **four** functions (`combined_novelty_series`, `hierarchical_novelty_series`, `location_only_series`, `novelty_rule_divergence`). A parameter default is invisible to a text search for an assignment.

**`cc2` is right that a per-domain cut makes them wrong, not merely duplicated** — and in three independent ways, not one. All four declared levels are **strings** (`'High'`, `'Category 2'`, `'Grade 3'`, `'7'`); the manifest's own notes record CTCAE landing at 3.8 and FMEA at 7.3, *between levels, not expressible as a rank*; and GHS runs **inverted** (Category 1 is most severe), so `>=` points the wrong way there. `cc2`'s `TypeError: '>=' not supported between instances of 'float' and 'str'` reproduces.

**`fable` is wrong here, on count and mechanism.** Measured: **5** domains declare `severity_scale = "none"`, not 6. The sixth is `cross_domain`, which declares `"composed"` and by the manifest's own rule carries two-or-more scales and inherits **no single application level**.

**Does this change a verdict?** No — it strengthens all three. Pinning remains correct (drift protection), but it makes the six *consistently* wrong. The real repair is at the comparison site, which must take an ordering and a level, not a float.

### J2 — where we agree, does it survive

- **R1 HOLD: survives on its own merits.** I re-derived the polarity at all three sites independently. Not a concurrence.
- **R2 REJECT: the verdict survives, both routes to it do not.** Recorded above.
- **F4 ("operative"): the disagreement is verbal, not factual.** `fable`'s citation (`composer.py:2140`) is the real call site; `cc2`'s 888 is inside the function body. Both measured the same thing, and the code settles the word — `_severity_declaration`'s own docstring reads *"★ AND IT DOES NOT TOUCH WHAT THE GATE ADMITS."* `cc2` is right that "operative" overstates it; `fable` concedes "no gate consumes it". No factual disagreement to resolve.

## `composability`

- **R2 + R3: no composition.** R2's only live effect under R3 is through the credence tie-break — the coordinate R3 should strip of `W`. Composing adds precision to a doomed term. Fails the founder's rule and the additive standard.
- **R1 + R3: independent, not composed.** I do not accept `fable`'s dominance claim as a *measurement*. "R3 alone leaves F1" is true of a change that currently decides nothing — R3 is wired to no gate. Two repairs at disjoint sites fixing disjoint defects is the weak "they don't conflict" sense the founder's wording excludes. Ship R1 on its ruling; rule R3 separately.
- **My delivery claims no composition.**

## `falsifier` / `falsifier_result`

Delivered at real paths:
- `scripts/the_credence_coordinate_still_carries_consequence_2026-11-14.py` (producer, M-A/M-B/M-C)
- `bench/tests/test_the_credence_coordinate_still_carries_consequence_2026-11-14.py` (7 guards)
- `docs/MATHEMATICAL_APPENDIX.md` §7.7.1.a (the committed measurement; sole changed dispatch artefact, `b86878ca…` → `a3b89eb1…`)

```
$ python3 -m pytest bench/tests/test_the_credence_coordinate_still_carries_consequence_2026-11-14.py -q
7 passed in 0.63s
$ python3 -m pytest <test_the_severity_spec_decides_when_promoted, test_verified_true_ledger> -q
52 passed in 2.30s
$ python3 -m pytest <5 appendix-reading suites> -q
82 passed in 5.16s
```

**What did not work, stated openly — two defects in my own probe, both caught on my falsification pass:**
1. First version called `hierarchical_novelty_series([], max_round=1, critical_threshold="High")` and caught `TypeError: missing 1 required positional argument: 'symbols'` — a **signature** error. It demonstrates nothing about the comparison. Had I reported it, I would have confirmed `cc2`'s claim with the wrong error.
2. Second version supplied `round_opened`; `_gate_population` keeps on `open_since_round`, so the entry was filtered and the comparison **never ran**. The probe printed `'High' accepted — no type error`, a clean pass proving nothing. The guard now asserts the entry survives `_gate_population` *before* the probe, so it cannot pass vacuously again.
3. The z3 lex-pair line originally **printed a verdict I had not computed** ("unsat by construction"). Replaced with a solved query over ranks `rA < rB`.

## `strongest_disagreement`

**Against `fable`:** *"under R3 the consequence verdict `c_d ≽_d θ_d` contains no `W` term, so a 3rd weight changes **zero** consequence verdicts"* — and its gloss, *"decides nothing the pair gate reads."* The first clause is true; the second does not follow and is **refuted by execution**: on a `c_d` tie the lexicographic comparison falls through to `credence`, which contains `W`, and the third weight flips the ordering (0.900 ≻ 0.800 becomes 0.720 ≺ 0.800). Pinned by `test_a_third_weight_changes_a_lexicographic_pair_ordering`. Secondary: *"the 6 `severity_scale = "none"` domains"* — measured, **5**; the sixth declares `"composed"` and inherits no application level.

**Against `cc2`:** *"Composition is therefore **strictly worse than R3 alone** on the named property (invariance under strictly increasing re-labelling): the composite inherits the product's `sat`."* Under R3 the product **is not the gate** — the lex pair is, and it is `unsat` (z3 and Wolfram agree). The composite does not inherit a `sat` from a gate R3 retired. `cc2`'s `sat` is a correct result about R2-instead-of-R3 and is being applied to a configuration it does not reach. The REJECT verdict stands; this route to it does not.

## `aims_check`

Additive — one producer, one guard file, one appendix amendment; nothing removed, nothing disabled; every guard reached by pytest and executed. Simplest sufficient — finding J-A's *fix* (removing `W` from `credence`) is a live-computation change and therefore the founder's ruling; I delivered the measurement that a ruling needs and stopped. No key, manifest, or answer file was read; the producer reads `bench/logs`, the live modules, and the domain manifest only.

## `passes_run`

**Five.** (1) digest verification, call-site mapping — found the three-population split. (2) archive measurement — found site C's eligible population is empty, which rescues `fable`'s number while refuting its derivation. (3) appendix read — found J-A, the consequence weight inside `credence`. (4) falsifying my own work — found the signature-`TypeError`, the vacuous-pass, and the uncomputed z3 verdict; all three repaired. (5) regression across 141 targeted tests, confirming the appendix edit broke nothing. Pass 5 produced no new above-threshold finding, so I stopped.

## What would refute me

1. **J-A falls** if `compute_sev_f("HARD", c, v) == compute_sev_f("SOFT", c, v)` for all `(c, v)` — i.e. `W` is not in the credence coordinate. Run the guard.
2. **My J3 reason falls** if the pair is specified as compared on `c_d` *only*, with no tie-break — then `credence` is never read and `W` really is jobless. §7.7.1 does not say this; a founder ruling that it does would overturn me.
3. **My J1 correction falls** if any archived registry contains a demotion-eligible entry at or above the cut — site C's population would stop being empty and `fable`'s 422/519 would stop being the right number to quote. Measured 0/133 today.
4. **My "six spellings" claim falls** if `inspect.signature` is the wrong reader — e.g. a decorator rewrites the defaults at import. Pinned by the enumerating test, which would then show a DRIFT.
5. **My refusal to call R1+R3 a composition falls** on a measurement showing the composed state dominates either alone on a named property — which requires R3 to be wired to a gate first. It is not.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 37 recorded tool call(s).

<!-- verbatim-begin: fable (panel severity_proof_and_weight_2026-11-14_joint) -->

All verification complete. Final pass produced no new above-threshold finding — terminating. Here is my joint-round answer as seat `fable`.

---

## verdict

| item | joint verdict | decided by |
|---|---|---|
| **R1** repoint `severity_is_proven` | **HOLD FOR THE FOUNDER** — built, wired, default OFF, **now merged into this tree as one implementation (cc2's), not two** | Both blind builds were the same semantic; execution found one measured difference (below) that selects cc2's |
| **R2** 3rd weight in (½, 1) | **REJECT** — unchanged, and now corroborated by my own independent z3 encoding, cc2's encoding, and Wolfram | 3-weight product order-flip `sat`; agrees across 3 independent tools |
| **R3** ordered pair | **RECOMMEND** — unchanged | lex pair `unsat` under order-preserving re-label (my re-derivation + cc2's + Wolfram `True` for the flip's existence on the product side) |
| **cc2's blind delivery as shipped** | **DEFECTIVE, repaired in the merge** | Its runner fails the stamped `test_the_severity_spec_decides_when_promoted_2026-10-15.py::test_the_config_actually_moves_the_mirror` (exact-match line 217) — executed, 1 failed. cc2's "122 passed" was true of the suites it selected; the stamped file was not among them |
| **my blind delivery's R1 implementation** | **DEFECTIVE, superseded in the merge** | It accepts `recomputed_rk=True` (`bool ⊂ int`) as the figure 1.0 — executed: `severity_is_proven` returns **True** at sev 0.97 with repoint ON. cc2's returns **False**. A malformed proof figure must not license |

## J1 — disagreements, settled by measurement

**Population (555/652 vs 422/519): both were right about different doors, and neither of us reported it per-site.** `severity_is_proven` has 3 live sites. The A4 door (~4442) and reasoned withdrawal (~9735) consult the proof only when `sev < 0.7` — my 519 is their population. But `_is_demotion_eligible`'s first clause is `severity >= CRITICAL_SEVERITY_THRESHOLD` (line 10662), so the calibration-demotion site (~10936) consults the proof on exactly the **133 criticals I excluded**. Measured (producer now in tree): release/withdrawal doors lose 422/519 = 81.31% Wilson [77.73%, 84.43%]; demotion door loses **133/133 = 100.00%** Wilson [97.19%, 100.00%] — under the repoint, no archived critical's proof agrees with its own severity, so proof-licensed demotion stops entirely. 555 = 422 + 133 exactly; all 97 keepers are sub-critical. My blind correction of cc2's headline was itself incomplete: I called the 133 "never exempted", which is true of the release doors and false of the demotion door. The founder-facing figures are the two per-site numbers.

**Which R1 implementation:** settled by execution, above. cc2's also compares against `effective_severity(e)` where mine read raw `severity` — identical while `_SEVERITY_SPEC` is off (the default and only tested state); the divergence under both-flags-ON is recorded, not repaired, matching cc2's own scoped note, and my blind point stands that the tolerance form is interim: the terminal door under R3 is consequence-side (`c_d ≺_d θ_d` against the manifest), which no one built this round.

**Spelling count:** cc2's **six** confirmed by import — 4 `critical_threshold` defaults in `convergence_location` (`combined_novelty_series`, `hierarchical_novelty_series`, `location_only_series`, `novelty_rule_divergence`), plus `evidence.LEDGER_CRITICAL_SEVERITY` and `audit_closing_window.CRITICAL_SEVERITY_THRESHOLD`. The brief's "four" undercounts. My blind test claimed to enumerate "every" default via `inspect.signature` and it genuinely does — but my prose repeated the brief's framing of 3 unpinned spellings where there were 5.

## J2 — agreements, re-examined against the other seat's route

- **R2 REJECT survives, and the routes are genuinely independent.** cc2's route: z3 shows the cut stays a class-rescaled test on model-asserted confidence (unsat for the negation at 4 values of w3). My route: the product gate stays breakable under order-preserving re-labelling with 3 weights (`sat`). These are *different defects* — one epistemic (belief still decides), one measurement-theoretic (ordering not invariant) — each independently fatal. I re-derived the sat/unsat pair in my own z3 encoding this round (2-weight flip `sat`, witness b=4, a=1, cA=¾, cB=¼; 3-weight `sat`; lex pair `unsat`) and Wolfram computed `True` for the flip's existence (local Wolfram Engine, exit 0). This is corroboration by independent instruments, not a vote.
- **R1 HOLD survives.** Both routes used the same subset/conjunction derivation — so on its own that *would* be one route twice. What makes it survive J2 is the direction evidence: cc2's exhaustive 224-point grid (0 loosen) and my archive sweep (0 loosen) are independent executions of the monotonicity claim.
- **F4 wording:** cc2 was right that "operative" overstates it. Verified in the merged tree: `grep critical_level|severity_scale` over the five gate-bearing modules → **zero hits**. The level reaches the prompt; no gate reads it. I confirm cc2's correction of my word choice; the substance (delivered-to-prompt, consumed-by-nothing) we never disagreed on.

## J3 — the self-falsification

**Confirmed, and with cc2's stronger reason adopted.** R2 and R3 are **exclusive, not composable**, and the brief's framing of R2 as "a smaller R3" is wrong twice over: (1) my blind redundancy argument — under R3 consequence is carried by `c_d`, so a 3rd weight decides nothing the pair gate reads — holds; (2) cc2's inadmissibility argument is stronger because it holds *even if* one disputes that the ordinal scale has taken the job: the 3-weight product is `sat` under order-preserving re-labelling on the project's own live criterion. A composition inherits that `sat` and is strictly worse than R3 alone on the named property. Recommending both would be incoherent; neither of us did, and the joint round confirms it with three tools.

## The fact neither of us had — the 4 (actually 6) spellings under a per-domain cut

The count is six, measured above. What a per-domain cut does to them: **both blind accounts are partial and compose into one true statement, each half carried by its own measurement.** My half: the constants are not *wrong* today — 0.7 is the pre-registered numeric proxy (`bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`, FROZEN, verified present this round) that the `severity_scale = "none"` domains inherit as the application level; the defect pinning repairs is drift between spellings. cc2's half: the moment a domain's own ordinal level reaches these call sites, every float comparison is **type-incompatible, not merely stale** — reproduced this round with a gate-surviving entry: `hierarchical_novelty_series(..., critical_threshold="High")` → `TypeError: '>=' not supported between instances of 'float' and 'str'`. One addition from my repro: with an entry that `_gate_population` drops, the same call returns `[0, 0, 0]` **silently** — so the failure mode is a crash only when a critical reaches the comparison, and a silently empty series otherwise, which is the worse half. **Verdict change: none** — R1/R2/R3 verdicts stand; the pinning fix is confirmed necessary-but-interim, and the comparison-site-takes-a-domain-and-an-ordering build stays named, out of scope, and now twice evidenced.

## composability

- **R2 ⊕ R3: refused** — composite inherits the product's `sat`; measured, not judged.
- **R1 ⊕ R3: composes on measurement** (unchanged from blind): each alone fails the other's executed falsifier.
- **The two blind R1 builds: NOT composed.** Two flags for one semantic is an addition nothing needs; one implementation merged, selected by the executed bool-guard difference. My `test_severity_proof_repointing.py` and flag names were **not** carried into the tree — superseded, per the committed measurement above, by cc2's implementation plus cc2's guard tests.

## reasoning

Dispatch digests verified (all 8 match). Harvests inspected and both seats' runners diffed against dispatch. Decisive executions: (1) stamped mirror test fails on cc2's runner (1 failed, 13 passed) — so the merge must carry the test extension my blind round wrote, re-keyed to cc2's mirror name; (2) bool-guard difference executed both ways (`True` vs `False` on the same malformed entry) — selects cc2's implementation; (3) per-site populations measured, reconciling both blind figures exactly; (4) six spellings by import; (5) z3 re-derived independently; (6) Wolfram second falsifier computed (attribution: Wolfram Language, local Wolfram Engine); (7) TypeError reproduced with a gate-surviving entry, plus the silent-zeros variant.

**Delivered into the tree** (final digests): `bench/reference_runner_v3.py` ← cc2's R1 build (`8be3942ecc116b6b`); `bench/tests/test_severity_is_ordinal_guards_2026-11-14.py` (8 tests, includes the 6-spelling pin); `scripts/the_proof_must_be_about_the_gated_number_2026-11-14.py`; `docs/MATHEMATICAL_APPENDIX.md` §7.7 measurement block (`2b6611d8c4c7d3e1`); `bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py` line 217 extended to assert both mirrors (`9c63513c581ef896`) — no assertion loosened, skipped or deleted; **new** `scripts/the_door_populations_are_site_scoped_2026-11-14.py` (the joint round's own producer). **What did not work:** my first TypeError repro returned `[0,0,0]` because the entry lacked `open_since_round`/status and `_gate_population` dropped it before the comparison — kept, because the silent path is itself evidence; `timeout` is absent on this host's shell, so the Wolfram call ran unbounded (it returned in seconds).

## falsifier / falsifier_result

```
$ python3 -m pytest bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py -q   # vs cc2's raw delivery
FAILED ...::test_the_config_actually_moves_the_mirror        1 failed, 13 passed

fable impl, repointed ON, rk=True (bool), sev=0.97 -> True     # my blind defect
cc2  impl, repointed ON, rk=True (bool), sev=0.97 -> False    # selects cc2's

2-weight product order-flip: sat [b = 4, a = 1, cA = 3/4, cB = 1/4]
3-weight product order-flip: sat
lex pair verdict-change under order-preserving re-label: unsat
wolframscript: Reduce[Exists[...]] -> True   (Wolfram Language, local Engine, exit 0)

$ python3 scripts/the_door_populations_are_site_scoped_2026-11-14.py
  ALL entries: n=652 lose 555 (85.12%) Wilson [82.19%, 87.65%]
  sev < threshold (A4 + withdrawal): n=519 lose 422 (81.31%) Wilson [77.73%, 84.43%]
  sev >= threshold (demotion door):  n=133 lose 133 (100.00%) Wilson [97.19%, 100.00%]
  reconciliation: 555 = 422 + 133; 0 critical keepers
  merged guard: rk=True (bool) at sev 0.97 -> severity_is_proven = False

TypeError confirmed: '>=' not supported between instances of 'float' and 'str'
(and silently [0, 0, 0] when the entry does not survive _gate_population)

$ python3 -m pytest <7 targeted suites incl. the stamped file> -q
119 passed in 3.19s
```

## strongest_disagreement

**cc2's claim: "All nine dispatch digests verified unchanged before editing … 122 regression tests pass", presented as a clean delivery.** I reject the *completeness* of that regression claim, with executed evidence: cc2's delivered runner fails `bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py` — a file **stamped in cc2's own dispatch table** — at the exact-equality assertion on `wire_module_mirrors`' return (line 217; 1 failed on execution against its harvested runner). cc2 changed that function's return shape and did not run the stamped test that pins it. The defect class is the one this project's record names: a completion claim whose selected evidence set excludes the test that falsifies it. It was repairable in one edit and is repaired in the merge; the implementation itself is the better of the two, which is why it was adopted anyway. Secondary, smaller: cc2's `assert len(spellings) == 6` is an exact-count change-detector that will fail on any future *correct* seventh spelling — loud but noisy; acceptable today, noted for the record.

## aims_check

Additive: nothing removed — `severity_is_proven`'s current behaviour is byte-identical with the flag OFF (asserted by an executed test), §7.7 retained as credence, every new entry point (flag, mirror, predicate) wired through `wire_module_mirrors` and executed by tests. Simplest sufficient: one R1 implementation, not two; one spelling-pin test, not two; the stamped-test extension strengthens, never loosens. Democratisation aim: the TypeError/silent-zeros evidence is recorded precisely because the current gate only works on the 0–1 proxy — the named next build (comparison site takes a domain and an ordering) is what makes the harness work beyond code, and it is named, not smuggled in. No scoring key, manifest, or prior-round ground truth was read; all verdicts computed, none asserted.

## passes_run

**4.** (1) Digest verification, code reading of the 3 call sites + `_is_demotion_eligible`. (2) Joint measurements: per-site populations, 6 spellings by import. (3) Adversarial verification of both blind deliveries: stamped-test failure (cc2), bool gap (mine), independent z3 re-derivation, Wolfram second falsifier, TypeError repro. (4) Merge, 119-test regression, and final checks (F4 grep: zero gate reads; pre-registration file verified present) — pass 4 confirmed prior claims and produced **no new above-threshold finding**, so I stop here.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/severity_proof_and_weight_2026-11-14_joint/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
