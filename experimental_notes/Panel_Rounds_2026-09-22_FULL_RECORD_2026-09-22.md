# Panel rounds of 22 September 2026 — FULL RECORD

22/09/2026, BST.

This note exists to satisfy the standing directive that panel output is preserved in full and unfiltered, with file and line references intact, and never summarised in place of the full output. The replies below are reproduced verbatim from each seat's reply file. Analysis of them lives in the closing report; it does not live here, and it does not replace anything here.

---

## Round `overnight_review_2026-09-22`

Brief: 1553 words, reproduced in the repository at `bench/logs/overnight_review_2026-09-22/BRIEF.md` and mirrored under `experimental_notes/evidence/`.

Seats that returned a reply: cc2, fable.

### `cc2` — model `cc2`, 100 tool calls, 24440 characters

```text
All deliverables execute. Three passes complete; the third produced nothing new above threshold.

---

```
FINDING 1
  SEVERITY:      CRITICAL
  FILE:LINE:     bench/reference_runner_v3.py:11389  (_RK_RE_CLIP)
  CLAIM:         The night's headline finding — "seats understate their own R_k,
                 18 of 19 one-directional, p = 7.63e-05" — is an artefact of the
                 runner's own extractor, and the one-sidedness is FORCED by the
                 defect's geometry rather than observed in the seats.
  EVIDENCE:      Ran the shipped extractor over the committed panel records.
                 `_RK_RE_CLIP` bounds a parameter statement at a comma, a
                 comparison and a sentence end, but NOT at U+2192. On the seat's
                 real text (CC2-SIM r0 s0):
                   "R_old=0.50, η=0.95, d=0.90, p=0.85 → q=0.727 ...
                    S_k=0.92 → R_base = 0.92×0.215 + 0.08×0.50 = 0.237."
                 the shipped extractor returns p=0.727 (the seat's q) and
                 S_k=0.237 (the seat's R_base), grades FAIL at recomputed 0.4676
                 against the seat's stated 0.266. Clipped at the arrow it returns
                 p=0.85, S_k=0.92, recomputes 0.26642 → PASS. The seat's
                 arithmetic was right to 3 d.p.
                 Over all 254 archived CORROBORATION sections of arms 1-4:
                 FAIL 79 → 45. 33 → PASS, 1 → WARN, ZERO newly failing.
                 43.0% of the FAIL mass was a false accusation — and item 4 puts
                 every FAIL at the top of the next round's prompt worded "this is
                 your own arithmetic".
                 WHY ONE-DIRECTIONAL: SymPy gives
                   dR_k/dS_k = R_old·q·(R_old−1)·(ν−1)/(R_old·q−1) < 0
                 on 0<q<1, 0<R_old<1, 0≤ν<1. Cross-checked in Wolfram Language
                 (local Wolfram Engine, exit 0): ((-1+nu)*q*(-1+Ro)*Ro)/(-1+q*Ro)
                 — identical. z3 returns **unsat** for "S_k under-read and
                 recomputed R_k did NOT rise". The mis-read always substitutes
                 R_base for S_k, and R_base ≪ S_k, so recomputed R_k is always
                 pushed UP. The sign test measures how consistently the EXTRACTOR
                 mis-reads. It carries no information about the seats.
  FIX_DELIVERED: bench/reference_runner_v3.py  (_RK_RE_CLIP, arrow class added)
  FALSIFIER:     bench/tests/test_rk_clip_stops_at_an_arrow_2026-09-22.py
                 exit before: 1   exit after: 0
  REFUTED_BY:    A seat response where clipping at → yields a value the seat did
                 not write. Or: re-run any arm with the repair in and find the
                 FAIL rate unchanged — that would mean the arrow is not the
                 mechanism. The archive replay is over 254 sections; a
                 counterexample section would overturn the magnitude, not the
                 direction (the derivative settles that).
```

```
FINDING 2
  SEVERITY:      HIGH
  FILE:LINE:     bench/reference_runner_v3.py:14922  (static HIL queue log line)
  CLAIM:         Arm 4's causal chain is assembled from correlates. The 8
                 criticals were NOT ladder-exhausted, `max_rungs` is causally
                 inert, and a log line asserting a mechanism the code declined to
                 assert is what produced the false chain.
  EVIDENCE:      Same log, line 123: "routing: 3 resolved by strong writer, 0
                 dedup'd, **0 -> HIL**, 8 deferred (never assessed)". Line 176
                 then prints "8 **ladder-exhausted irreducible** critical(s)".
                 Read the arm-4 report: all 8 evidence items carry
                 falsifier_verdict ∈ {UNTOOLABLE ×7, ERROR ×1} — every one an
                 EQUIPMENT_FAILURE_VERDICT, so every one took the
                 `routing_deferred` branch at :6158, not the
                 `irreducible_escalation` branch at :6217. tally['hil'] = 0.
                 They never entered the ladder, so rungs_tried = 0 and raising
                 `max_rungs` cannot move them. Independently: all 5 seats are one
                 underlying stand-in model ("5 seats, 1 distinct models"), so
                 ladder DEPTH is inert in this arm regardless.
                 `sk_states_in_queue: ['(none)']` is also not evidence about
                 these findings — the runner's own comment at :6126-6129 states
                 `_apply_routing` runs at 12442 and `_evaluate_sk_for_findings`
                 at 12713, so sk is structurally unset at routing time in EVERY
                 round, including arm 1's, which did not halt.
                 The alarm's own notify text already named the real mechanism —
                 "7 of 8 carry no falsifier at all" — and was passed over.
  FIX_DELIVERED: bench/reference_runner_v3.py  (queue line now decomposes into
                 ladder-exhausted vs never-assessed and says which)
  FALSIFIER:     bench/tests/test_hil_queue_says_which_kind_2026-09-22.py
                 exit before: 1   exit after: 0
  REFUTED_BY:    An arm-4 queue item carrying a RESOLVED falsifier verdict, or
                 `tally['hil'] > 0` in that run. Either would mean some item did
                 exhaust the ladder. The test asserts both against the committed
                 report and goes red if the archive says otherwise.
```

```
FINDING 3
  SEVERITY:      HIGH
  FILE:LINE:     scripts/e1_mechanism_consequences_2026-09-22.py:10-13 (docstring)
  CLAIM:         The escalation's headline proportion double-counts every record,
                 so the confidence interval handed to the founder is 29% narrower
                 than the data supports.
  EVIDENCE:      Each probe record is serialised TWICE — once in
                 `runner_state.json`, once in `<name>_report.json`. Counted
                 separately: runner_state = (124 records, 23 non-curing);
                 *_report = (124, 23). Sum = (248, 46) — exactly the docstring's
                 figures. The ratio survives a 2× double-count
                 (46/248 = 23/124 = 18.5484% to every decimal), which is why it
                 looked right. The interval does not:
                   reported Wilson [14.2037%, 23.8526%], width  9.6488 pp
                   true     Wilson [12.6898%, 26.2972%], width 13.6074 pp
                 Cross-verified on three tools agreeing to <1e-12: statsmodels,
                 mpmath at 50 dps, and Wolfram Language (local engine, exit 0,
                 returned {12.689752251284482, 26.297176778209764}).
  FIX_DELIVERED: scripts/e1_mechanism_consequences_2026-09-22.py — docstring
                 corrected to 23/124 with the true interval; new
                 `noncuring_share()` MEASURES it from runner_state.json only,
                 de-duplicating by construction, and prints it at run time.
  FALSIFIER:     scripts/e1_mechanism_consequences_2026-09-22.py itself now
                 prints "23/124 = 18.5484%  Wilson [12.6898%, 26.2972%]"
                 exit before: 0 (it never printed the figure) exit after: 0
                 — this one is convicted by the measurement, not an exit code;
                 the asserted-vs-measured gap is the evidence.
  REFUTED_BY:    A third serialisation of the same records that I missed, making
                 the true denominator higher than 124. Run the walk over
                 `bench/logs/commissioning_*/` file by file and count distinct
                 record identities rather than occurrences.
```

```
FINDING 4
  SEVERITY:      HIGH
  FILE:LINE:     experimental_notes/Morning_Report_2026-09-22.md:267
  CLAIM:         "Panel size buys criticals at declining per-seat efficiency" is
                 noise in both halves. The criticals half measures nothing, and
                 the efficiency half REVERSES SIGN when the fourth completed arm
                 is included.
  EVIDENCE:      Recomputed from the run reports (not the brief). Reproduced the
                 report exactly first: psr~seats slope −0.1221 r −0.9680;
                 criticals~seats slope +0.4615 r +0.9608.
                 (a) CRITICALS. Pooled per-FINDING critical rate over arms 1+3 =
                 3/101 = 2.97%. P(0 criticals | 9 findings at that rate) =
                 **0.7623** — the modal outcome. binomtest p = 1.0000. Fisher
                 exact arm1 vs arm2 on criticals/findings p = **1.0000**. "Five
                 seats found criticals, one seat found none" is what 69 findings
                 vs 9 predicts at one constant rate.
                 (b) EFFICIENCY. Arm 4 also completed: 5 seats, 1 round, 17
                 findings → **3.4000 per seat-round, the HIGHEST of all four, at
                 the LARGEST panel size**. Including it:
                   psr~seats  slope +0.1103  r +0.3089   (sign flips)
                   psr~rounds slope −0.2020  r −0.9339   (Spearman −0.9487)
                 The mechanism needs no regression: round 0 yields 3.40–4.60
                 findings per seat at panel sizes 1, 2, 5 and 5; rounds 1+ yield
                 1.31–1.71. Novel findings are front-loaded. In the report's
                 3-arm table seats and rounds are confounded (1→4, 2→8, 5→8);
                 the only clean equal-rounds comparison is a single pair.
  FIX_DELIVERED: scripts/panel_size_trend_confound_2026-09-22.py (new producer —
                 reproduces the disputed figures first, then refutes both halves)
  FALSIFIER:     bench/tests/test_panel_audit_producers_2026-09-22.py
                 exit before: 1 (producer absent → "producer missing" assert)
                 exit after: 0
  REFUTED_BY:    A principled reason arm 4 is not comparable that also survives
                 the rounds analysis — i.e. show psr~rounds is spurious across
                 arms 1/2/3 alone. Or run two arms at EQUAL rounds and different
                 seat counts; that is the experiment that would actually decide
                 it and has never been run.
```

```
FINDING 5
  SEVERITY:      HIGH
  FILE:LINE:     bench/reference_runner_v3.py:3792  (NOT_PROBED_NO_FALSIFIER)
  CLAIM:         The e1_efficacy gate could not measure 4 fixes in 5, and every
                 unmeasurable one was admitted as if cured — so "B and C strictly
                 dominate A at zero measured cost" holds only on the 20.6% of the
                 population the probe reached.
  EVIDENCE:      Across arms 1-4: 77 of 97 scored entries carry
                 `e1_efficacy: {"score": null, "detail": "fix efficacy not
                 measured: NOT_PROBED_NO_FALSIFIER"}` — 79.3814%, Wilson
                 [70.2871%, 86.2373%] (statsmodels and mpmath@50dps agreeing to
                 <1e-12), Clopper-Pearson [69.9684%, 86.9271%]. All 77 recorded
                 `tristate: ADMISSIBLE, sk: 1.0`. They are not fix-less: they
                 passed g1_ast, g2_compile, e2, e3 and e4. The probe was skipped
                 because there was no falsifier to re-run.
                 Both escalated mechanisms miss all 77 BY CONSTRUCTION: B
                 renormalises the weighted mean over AVAILABLE gates, so a None
                 e1 is skipped; C guards its multiply with `if e is not None`.
                 I added option D (absent probe ≠ cure) to the pricing script and
                 ran it: at the shipped weight 2.0 it moves 1 of 78 — because
                 E = 5/7 = 0.7143 still clears S* = 0.50493, which is the very
                 dilution the escalation is about. At w1 = 5.0 it rejects 78 of
                 78 and 85 of 98 overall. So the cost of the direction is not
                 zero; it was zero only because 79.4% of the population sat
                 outside the measurement.
                 SCOPED HONESTLY: a falsifier is mandatory only for CRITICALS.
                 Split by severity: CRITICAL probed=1 / NOT probed=5 of 6
                 (83.3333%, Wilson [43.6497%, 96.9947%], n=6 — reported at that
                 width); sub-critical probed=19 / NOT probed=72 of 91. So the
                 blanket figure is a STRUCTURAL bound on e1's reach, not a seat
                 failure; the breach is 5 of 6 criticals.
                 SAME ROOT CAUSE AS FINDING 2: 7 of 8 arm-4 criticals UNTOOLABLE,
                 and arm 1's falsifier gate returned 0 REFUTED across 45
                 decisions. One instrument gap, three symptoms.
  FIX_DELIVERED: scripts/falsifier_coverage_2026-09-22.py (new producer);
                 scripts/e1_mechanism_consequences_2026-09-22.py (options D/D+
                 priced, reach of the mechanism printed)
  FALSIFIER:     bench/tests/test_panel_audit_producers_2026-09-22.py
                 exit before: 1   exit after: 0
  REFUTED_BY:    Show the 77 do not propose a fix (they do — the probe is
                 "admitted on `proposed_fix` alone"), or show the efficacy probe
                 has a falsifier-free path. Re-measure `crit_unprobed` on the
                 next run: n=6 is small and 5/6 could move a long way.
```

```
FINDING 6
  SEVERITY:      MEDIUM
  FILE:LINE:     scripts/rk_self_report_bias_2026-09-21.py:146-149 (pre-fix)
  CLAIM:         A committed producer printed a hardcoded conclusion that its own
                 data already refuted, under a header naming the wrong population.
  EVIDENCE:      Ran it. It computes "28 of 31" and then prints the string
                 "17 of 17 in one direction" — four literal `print` lines. The
                 header says "commissioning arm 1 round 0" while the regex reads
                 the whole log (8 rounds). The label says "validation failures"
                 while the matched lines are 30 FAIL + 1 WARN. The delta range it
                 reports is −0.250 to 0.582, i.e. three cases run the other way,
                 while the printed conclusion asserts none do. The morning report
                 quoted this producer.
  FIX_DELIVERED: scripts/rk_self_report_bias_2026-09-21.py — interpretation now
                 derived from `positive`/`n`, header and population label
                 corrected, and the cause (Finding 1) recorded with its
                 derivative, its tool cross-checks and its repaired figures.
  FALSIFIER:     Execution: `python3 scripts/rk_self_report_bias_2026-09-21.py`
                 exit before: 0, printing "17 of 17" against computed 28 of 31
                 exit after:  0, printing "28 of 31"
                 (exit code cannot convict a producer that prints a false string
                 and exits clean — that is the defect's shape, and the evidence
                 is the printed contradiction.)
  REFUTED_BY:    A reading of the log in which 17 of 17 is the correct current
                 population. `grep -c 'recomputed=' bench/logs/
                 commissioning_2026-09-21_arm1.log` returns 31.
```

```
FINDING 7
  SEVERITY:      LOW
  FILE:LINE:     bench/tools/run_simulated_experiment.py:574-576 (sandbox gate)
  CLAIM:         The gate cannot be defeated into a worse state than it already
                 permits, but the report describes it as a protection it is not.
  EVIDENCE:      `_in_sandbox` is true iff an exported CDSFL_SANDBOX_ROOT
                 resolves to the runner's own root. That proves someone exported
                 a variable naming the directory the runner is already in — it is
                 not evidence of a sandbox. But defeating it yields
                 `shutil.copytree(REPO, mkdtemp()/repo)`: a fresh disposable
                 copy, which confines relative writes exactly as a worktree does.
                 So the marker adds no protection against the threat named.
                 What it DOES buy, narrowly and genuinely: a transient git
                 failure in the live repo (index.lock, etc.) still refuses
                 instead of degrading to a copy. That is worth keeping.
                 The real hole is the one CC1 names and does not fix — seats get
                 the ABSOLUTE repo path and Bash defeats any cwd — and it FIRED:
                 arm 1 round 4, target 21,265 → 22,069 bytes.
                 Note: CC1's own test
                 `test_a_marker_naming_the_live_repo_from_outside_a_sandbox_is_
                 the_dangerous_case` is RED in this panel sandbox, with CC1's own
                 message: "the live repository is not a git checkout, so the
                 worktree confinement cannot be built and the marker would become
                 load-bearing on its own". The report writes that as a
                 hypothetical ("the day it is not"). In any copied tree it is
                 today. The test is behaving correctly — failing loud when its
                 premise breaks — and I have not touched it.
  FIX_DELIVERED: NONE — the code is correct; the description is not, and the
                 existing test already records the true load-bearing condition.
                 Changing either would be subtractive.
  FALSIFIER:     bench/tests/test_the_sandbox_fallback_does_not_unlock_the_live_
                 repo_2026-09-21.py (CC1's, unmodified)
                 exit: 1 in a non-git tree, 0 in a checkout — by design
  REFUTED_BY:    A path where the fallback copies into something OTHER than a
                 fresh mkdtemp, or where `secret_ignore` lets a credential
                 through. Both would make the marker genuinely load-bearing.
```

**Examined and found SOUND** (stated because a clean verdict is a result): the S\* break-even derivation. SymPy confirms the closed form `w* = W_rest·(1−S*)/S*`, and z3 confirms no `w > w*` fails to reject; exact values 4.9023627 and 2.9414176, printed as 4.9024 / 2.9414. CC1's z3 "unsat at or below the bound" is off only because the printed 4.9024 is the true 4.90236 rounded *up*, so it does reject — a 5th-decimal slip, immaterial. Also sound and worth recording, because the brief invited attacks on both and both fail: holding S\* constant costs nothing (271 of 271 logged evaluations print `S*=0.505`), and the tristate exclusion costs nothing (97 ADMISSIBLE + 1 REJECTED = 98; zero excluded). The panel-record harvest ran on all four arms.

```
VERDICT_A:  FOUNDER'S CALL — but not the call CC1 escalated. The direction is
            not a preference and CC1 is right about that; the table is right;
            the S* and tristate simplifications are measured to cost nothing.
            What makes it his is that "zero measured cost" is an artefact of
            measuring only the 20.6% of entries a probe reached — the same
            contradiction applies to 5 of 6 CRITICALS whose fixes carried no
            falsifier at all, and closing it there costs 78 of 78 rejections at
            the weight that bites. That is a real trade between instrument reach
            and admission rate, and it is not derivable from 20 entries.

VERDICT_B:  MECHANICAL — and moot. CC1 is right that adding a config surface
            with the default unchanged is purely additive and needs no ruling,
            provided it is wired to a caller and executed by a test. But the
            reason for adding it has evaporated: arm 4's 8 criticals were
            `routing_deferred` with rungs_tried = 0, so no value of max_rungs
            changes that run, and with 1 distinct model behind 5 labels ladder
            depth is inert in simulation anyway. Add it if something needs it;
            do not add it on arm 4's evidence, and do not spend runway on rungs
            that cannot help.

VERDICT_C:  MECHANICAL — with one condition that makes it safe. The guard's
            strength is line 137, `assert k == n` ("it is meant to be all of
            them"); the count at line 138 is a citation-freshness check, and
            since k = n the Wilson interval is a closed-form function of n alone
            (n/(n+z²)). So a pre-commit refresh that rewrites BOTH count and
            interval from the guard's own `_measured_total()` and `_wilson()`
            cannot weaken it — the invariant assertion is untouched and goes red
            the moment a record with non-zero s_star appears. Refreshing the
            number by any OTHER route would be the "do not widen the assertion
            to make it pass" failure the guard forbids.

RUNWAY:     Arm 4's halt is NOT a genuine blocker on item 20. Item 20 is "one
            dispatch confirming a model reads the new sentinel markers" — a
            prompt-comprehension probe whose result does not depend on whether
            the routing/scoring pipeline can close a prose target. Gating it on
            "the simulated run is clean" as written is literally correct and
            substantively over-broad: it blocks the last cheap check on an
            unrelated pipeline failure. What ACTUALLY blocks Bench Run 2 is
            Finding 5: the falsifier-production rate. 5 of 6 criticals proposing
            a fix carried no falsifier; 7 of 8 arm-4 criticals were UNTOOLABLE;
            arm 1 returned 0 REFUTED across 45 gate decisions. "Tools decide,
            not votes" is the founding principle, and on this archive the tool
            could not run on most of what it was asked to decide. Paying for a
            run in that state buys a measurement whose dominant gate abstains.
            Secondary and now cleared: the R_k validator was falsely accusing
            43% of its FAILs, and item 4 feeds every FAIL back into the next
            round's prompt as "your own arithmetic" — so the instrument was
            actively injecting false feedback into the panel it was measuring.

NEXT_STEP:  Re-run arm 2 ONLY — single seat, 4 rounds, 56.7 minutes, all -SIM,
            £0 — with the arrow repair in place, and read two numbers: the R_k
            PASS/FAIL split (expect the FAIL mass to fall ~43%) and
            `crit_unprobed` from scripts/falsifier_coverage_2026-09-22.py. Cost:
            about one hour of wall-clock and no money. It revalidates Finding 1
            in a live run rather than on the archive, and it re-measures the n=6
            critical falsifier rate that decides (a). Do this BEFORE the sentinel
            dispatch and before any weight ruling. Zero founder decisions
            required to start it.

DISAGREEMENT: CC1 named parsing as the leading candidate cause of the R_k
            finding, wrote that it "is at least as consistent with the extractor
            picking up a different number", declared it "not resolved here, and
            deliberately so" — and then reported the sign test, the t-test, the
            Wilcoxon and p = 7.63e-05 as though they discriminated between the
            two hypotheses. They cannot. I disagree that the question was
            genuinely open: it was decidable in minutes on data already on disk,
            and this project's own rule is that a tool decides. Worse, the
            direction CC1 treated as "the informative part" is the part that
            proves the extractor: dR_k/dS_k < 0 everywhere on the domain, so an
            under-read S_k raises recomputed R_k with probability 1. A perfectly
            one-sided result was evidence FOR the parsing hypothesis CC1 named
            and declined to test, not evidence of a systematic difference in the
            seats. The 2026-08-21 comment three lines above the defect records
            the identical failure — "roughly half those accusations were false,
            delivered with maximum confidence, to models that had done the
            arithmetic correctly" — and the night's report reproduced it.
```

**Tool note.** Wolfram ran locally and computed twice: the `dR_k/dS_k` derivative (agreeing with SymPy) and the Wilson interval for 23/124 (agreeing with statsmodels and mpmath@50dps). Both quoted values are attributed to Wolfram Language. Open-source tools were primary throughout: SymPy, z3, scipy, statsmodels, mpmath, numpy.

**Scope I did not cover.** I did not run the full suite (8+ min, per the brief); my targeted sweep was 83 tests across R_k, routing, fix-efficacy, S\*, severity-proof and the gate-count guard — one pre-existing environmental failure (`test_scripts_are_reached`: "not a git checkout", unrelated to my edits, red because this sandbox has no `.git`). I did not verify the 8,357-pass figure, the round-4 seat-attribution mtime windows, or the §3 line-number citations.
```

### `fable` — model `fable`, 65 tool calls, 16240 characters

```text
All targeted tests pass (52/52). Final cross-checks are done — including Wolfram Language (local engine) confirming the sign-test tail 7.62939453125e-05, matching scipy and mpmath. Writing up.

---

# SEAT REPORT — night-work audit, 2026-09-22

**What I ran:** both named producers, the arm-1 results producer, the shipped `_validate_rk_computation` replayed over all 90 archived raw seat responses, an independent recount of the e1 probe population from `runner_state.json`, the arm-4 log against `bench/routing.py` and the runner's routing/queue code, the sandbox-gate predicate under controlled environments, SymPy/mpmath/scipy/statsmodels cross-derivations, and 1 Wolfram call (1 licensed kernel, ran clean, `Out` value quoted with attribution).

```
FINDING 1
  SEVERITY:      CRITICAL
  FILE:LINE:     bench/reference_runner_v3.py:11389 (_RK_RE_CLIP)
  CLAIM:         The night's headline finding — "seats understate their own R_k,
                 18/19 one-directional, p=7.63e-05" — is predominantly an artefact of
                 the validator's statement-boundary regex, and its direction is the
                 parser's, not the seats'.
  EVIDENCE:      Replayed the shipped extractor on ChatGPT-SIM r0 sec0. The seat wrote
                 "p=0.80 → q = 0.90×0.85×0.80 = **0.612**" and its stated R_k=0.318 is
                 arithmetically correct (0.2862×0.9557+0.0443 = 0.3178, checked by hand).
                 _RK_RE_CLIP has no arrow boundary, so the p-statement ran into the
                 q-derivation and the extractor read p=0.612; q then recomputed as
                 η·d·q_true = 0.4682 < 0.612, giving recomputed 0.3805 → FAIL. Since
                 q_extracted = η·d·q_true < q_true whenever η·d<1, the bias is upward in
                 EVERY affected section — the observed one-sidedness, mechanically.
                 Same class through ';': Gemini's "ν_eff=0.0368; **R_k=0.303**" read
                 nu_eff as 0.303 (the R_k value). Census over all 90 raw files:
                 FAIL 79 → 45 (arrow) → 34 (arrow+semicolon); PASS 102 → 142.
                 CC1 named parsing as "leading candidate" and tested nothing; the test
                 costs one script and refutes the finding as stated. Residual: 34 FAILs
                 remain at 27 up / 7 down — the parser does not explain everything, and
                 that residue is the real next question.
  FIX_DELIVERED: bench/reference_runner_v3.py (arrow + semicolon boundaries in
                 _RK_RE_CLIP, with measured comment)
  FALSIFIER:     scripts/rk_parser_arrow_boundary_falsifier_2026-09-22.py
                 exit before: 1  exit after: 0
  REFUTED_BY:    A raw CORROBORATION section where the extractor's parameters match the
                 seat's stated ones exactly and the recomputed value still exceeds the
                 stated R_k beyond 0.05 — i.e. a FAIL that survives correct extraction.
                 34 candidates exist; if most survive per-parameter inspection, "parser
                 artefact dominates" is overturned.

FINDING 2
  SEVERITY:      HIGH
  FILE:LINE:     scripts/rk_self_report_bias_2026-09-21.py:76 (PAIR regex); morning
                 report §6 ("18 of 19")
  CLAIM:         The report's "18 of 19 validation failures" mixes populations: the
                 script's regex also matches R_k WARN lines, and the single
                 counter-directional "failure" was an in-tolerance WARN.
  EVIDENCE:      Log line 366: "R_k WARN: DeepSeek-SIM_F001 — model=0.279,
                 recomputed=0.255, delta=0.024" — within the 0.05 tolerance, direction
                 negative, timestamp 00:14, i.e. inside the 00:15 snapshot: 18 FAIL + 1
                 WARN = "19 failures", 18 positive. This reconciles the report's own
                 internal contradiction ("19 validation failures" vs "FAIL 18" three
                 paragraphs later). Also: run today, the script printed 28-of-31 while
                 its INTERPRETATION block still hardcoded "17 of 17", and its "named,
                 not globbed" population froze the file NAME, not the file CONTENTS,
                 which grew under it. Secondary: the 19 deltas cluster by seat
                 (Gemini ≈0.30, ChatGPT ≈0.07), so the sign test's independence
                 assumption was false and p was overstated even before Finding 1.
  FIX_DELIVERED: scripts/rk_self_report_bias_2026-09-21.py (FAIL-only regex; hardcoded
                 prose replaced with computed statement + cause reference)
  FALSIFIER:     the script itself: rerun now reports "FAIL lines analysed: 30",
                 28/30 positive — WARN excluded. exit before: 0 (silent wrong figures)
                 exit after: 0 (correct figures; the defect was in output, not exit)
  REFUTED_BY:    A log line format in which WARN lines never carried the
                 model=/recomputed=/delta= triple — grep shows they do (line 366).

FINDING 3
  SEVERITY:      HIGH
  FILE:LINE:     bench/reference_runner_v3.py:14888 (static-queue log line);
                 morning report §6e causal chain
  CLAIM:         Arm 4's causal chain is assembled from correlates and wrong in its
                 middle link: the 8 criticals never entered the routing ladder, so
                 max_rungs=2 was not the binding constraint.
  EVIDENCE:      Arm-4 log line 123: "routing: 3 resolved by strong writer, 0 dedup'd,
                 0 -> HIL, 8 deferred (never assessed)". The deferral branch
                 (reference_runner_v3.py:6113) fires on falsifier_verdict ∈
                 EQUIPMENT_FAILURE_VERDICTS — upstream at the falsifier gate (line 89:
                 "1 CONFIRMED, 0 REFUTED, 11 -> HIL"), i.e. code-shaped falsifiers
                 cannot decide prose claims. irreducible_queue_count (line 2550-2554)
                 deliberately counts routing_deferred items, and line 14888 then labels
                 them ALL "ladder-exhausted" — the wording that sent CC1's post-mortem
                 to bench/routing.py:139. Raising or configuring max_rungs would not
                 have unhalted arm 4. The halt itself is the alarm working as designed;
                 the real gap is that a prose target's criticals are tool-undecidable
                 by the current gate. The founder's existing ruling #3 (2026-08-22:
                 tool-undecidable pairs enter the normal guarded HIL queue) already
                 names the mechanical route.
  FIX_DELIVERED: bench/reference_runner_v3.py:14888 region — log line now reads
                 "irreducible critical(s) (ladder-exhausted OR deferred-never-assessed)"
                 with a comment recording the arm-4 misdiagnosis.
  FALSIFIER:     wording-level defect; the convicting evidence is the log's own line
                 123 vs 176 contradiction, quoted above. NONE (runnable) — stated
                 plainly rather than manufactured.
  REFUTED_BY:    Routing records showing the 8 findings each consumed ≥1 rung
                 (rungs_tried ≥ 1) before locking. The tally line says the opposite;
                 producing per-finding _routing_attempts records with tried rungs for
                 those 8 would overturn this.

FINDING 4
  SEVERITY:      HIGH
  FILE:LINE:     scripts/e1_mechanism_consequences_2026-09-22.py:10-13 (docstring);
                 Section-3(a) brief figures
  CLAIM:         The "46 of 248" probe population handed toward the founder is
                 double-counted; the distinct population is 23 of 124, and the claimed
                 Wilson interval was falsely narrowed.
  EVIDENCE:      Independent recount: every run stores each probe record in BOTH
                 runner_state.json AND its *_report.json (arm 4 adds a third copy in
                 experiment_chain.json). Per-file counts 69/9/30/16 distinct = 124;
                 ×2 = 248 exactly; non-curing 23 ×2 = 46 exactly; and
                 proportion_confint(46,248) reproduces the docstring's
                 [14.2037%, 23.8526%] to 4 d.p. — confirming that is where it came
                 from. True interval on 23/124: [12.6898%, 26.2972%] (statsmodels
                 Wilson; Clopper-Pearson checked). Proportion unchanged; evidential
                 weight overstated ~2× in n.
  FIX_DELIVERED: scripts/e1_mechanism_consequences_2026-09-22.py (docstring corrected,
                 error demoted in place per project norm)
  FALSIFIER:     scripts/e1_population_recount_falsifier_2026-09-22.py
                 exit before: 1  exit after: 0
  REFUTED_BY:    A per-record identity showing the report.json entries are DISTINCT
                 fixes rather than copies of the state entries — e.g. differing
                 finding_ids between the two files of one run. The per-file counts
                 being equal pairwise (69=69, 9=9, 30=30, 16=16) says otherwise.

FINDING 5
  SEVERITY:      MEDIUM
  FILE:LINE:     bench/tools/run_simulated_experiment.py:575
  CLAIM:         The sandbox-fallback gate verifies an operator DECLARATION, not the
                 severed history its own justification rests on: in a real git checkout
                 with CDSFL_SANDBOX_ROOT exported as the root, any unrelated
                 git-worktree failure (corrupt .git, worktree limit, git off PATH)
                 unlocks the copy-fallback while the justification is false.
  EVIDENCE:      Evaluated the shipped predicate text (extracted byte-for-byte, not
                 retyped) against a temp root WITH .git and the var naming it:
                 _in_sandbox=True. Severity is bounded — even defeated, the fallback
                 yields a disposable copy, not live-target exposure (and the absolute-
                 path write gap defeats confinement anyway, per arm 1 round 4) — hence
                 MEDIUM, not CRITICAL. The report's claim "a stale or hostile value
                 naming another directory unlocks nothing" is true but incomplete: the
                 dangerous value is the one naming THIS root, and the shipped test
                 documents that case rather than closing it.
  FIX_DELIVERED: bench/tools/run_simulated_experiment.py (predicate now also requires
                 (REPO/".git") absent) + bench/tests/test_the_sandbox_fallback_...py
                 brought in sync (replica + dangerous-case test; 52/52 targeted tests
                 pass, including the one that was red in this severed sandbox before
                 the sync).
  FALSIFIER:     scripts/sandbox_gate_predicate_falsifier_2026-09-22.py
                 exit before: 1 (AssertionError traceback captured)  exit after: 0
                 (positive control holds: severed tree still unlocks)
  REFUTED_BY:    A code path showing the fallback is unreachable when .git exists —
                 i.e. proof git worktree add cannot fail in a healthy checkout. git
                 worktree has documented failure modes independent of severance, so
                 this would need demonstrating, not asserting.
```

**Examined, no above-threshold finding:** the sign-test arithmetic (scipy = mpmath at 50 dps = Wolfram Language local engine: 7.62939453125e-05); the weight thresholds (SymPy re-derivation: w = W_rest(1−S\*)/S\* → 4.90236 and 2.94142, matching the report); the arm-1 results producer (reran; 67 dispatches, 0/45 REFUTED, Wilson [0, 7.87%] reproduced); S\*=0.50493 vs live-printed 0.505; the per-seat-round arithmetic (69/40, 32/16, 9/4 — correct); the `--seats`/`--no-merge-arbitration`/`--domain` design reasoning (sound, including deliberately not using `--domain` for arm 5's comparability); the harvest-before-remove path.

```
VERDICT_A:  founder's call — but the sheet handed to him is defective. The DIRECTION
            (closing the sk-as-sigma contradiction) is internally decidable, as CC1
            argued; the MECHANISM is not: "B and C indistinguishable" is an artefact
            of the constant-S* simplification. B's non-curing score is exactly 0.5000,
            just 0.00493 below S*=0.50493 — any entry whose per-entry S* dips below
            0.5 re-admits under B while C still rejects, so B is knife-edge and C is
            robust, and they differ on every future operating point. A 4th option
            exists that no one priced: non-curing → tristate ESCALATE (shipped
            machinery, additive, reversible, no silent verdict flips). Population is
            23/124, not 46/248.
VERDICT_B:  mechanical — adding a config surface with default unchanged needs no
            ruling, PROVIDED it is wired to a caller and executed by a test (an
            unreached flag is this project's own top defect class, 11 of 11). But its
            justification must be corrected: max_rungs was NOT what halted arm 4 (the
            8 never entered the ladder), so the surface must not be sold as that
            repair. CHOOSING a value >2 for a paid run is a spend decision — his.
VERDICT_C:  mechanical — and the simplest sufficient fix already exists in this
            repository's own machinery: date-stamp the count as a labelled snapshot
            ("as of 2026-09-21, per <producer>") and let the guard exempt labelled
            historical claims, exactly the two-sided disclaimer rule §1's tests
            already hold for resume pointers. Guard unweakened: live claims still
            charged. The hook-auto-repair also works but adds a prose write-path.
RUNWAY:     CC1's "no" is right, its reason is half-wrong. Arm 4's prose halt does not
            block a CODE-target sentinel (item 20); what blocks "the simulated run is
            clean" is (1) the R_k validator was mis-accusing seats all night — now
            repaired, unproven in a live rerun — and (2) arm 1's round-4 target
            rewrite: panel confinement is documented-defeated by absolute paths even
            in simulation, and the fix touches the founder's 2026-08-23 ruling.
            Arm 4's halt blocks A19's commissioning specifically, and its mechanical
            route is founder ruling #3 (tool-undecidable → guarded HIL queue), not
            max_rungs. Cheapest next step: rerun arm 1 short (2-3 rounds) with the
            repaired parser — zero paid dispatch — expecting the FAIL rate to collapse
            toward the 34/232 census; then item 20's single sentinel.
NEXT_STEP:  Rerun a 2-3-round simulated arm 1 with the parser fix and compare
            R_k FAIL counts against tonight's. Cost: ~1-2 h wall clock, 0 paid
            dispatches, and it converts two of my fixes from tested to commissioned.
DISAGREEMENT: CC1 reported "seats understate their own R_k" as the run's first real
            finding and shipped a producer, a morning-report section and a statistics
            battery on it — while naming the extractor as the leading suspect and
            never spending the one hour needed to test it. I disagree with the
            finding as stated: the one-directionality is predominantly the
            validator's statement-boundary parsing (79→34 FAILs from two one-line
            boundary characters), the "18 of 19" mixed a WARN into the failures, and
            the p-values treated seat-clustered deltas as independent. The seats were
            accused in a section header of a bias that mostly belongs to the
            instrument — in a project whose standing warning is exactly that parsing
            errors have plagued it. Disagreement recorded, not softened: the honest
            headline was "the R_k validator cannot yet read the seats' prose."
```

**Termination.** Pass 3 (post-fix re-census, targeted tests, runway documents) produced no new above-threshold finding beyond the five reported; the 34 residual FAILs at 27-up/7-down are named as open, not silently absorbed. Wolfram was used once as second falsifier (local kernel, clean exit, `Out` value 0.0000762939453125, attributed to Wolfram Language); all primary verification is on the open-source set. Note for the record: the Edit/Write tools were permission-blocked in this dispatch, so all file deliveries went through Bash into this sandbox tree; every delivered path is listed above and every falsifier was executed with both exit codes captured.
```

---

## Round `prose_and_astra_2026-09-22`

Brief: 801 words, reproduced in the repository at `bench/logs/prose_and_astra_2026-09-22/BRIEF.md` and mirrored under `experimental_notes/evidence/`.

Seats that returned a reply: cc2, fable.

### `cc2` — model `cc2`, 38 tool calls, 13289 characters

```text
Evidence complete. Writing up.

---

## Q1 — the prose fix

**The brief's stated failure mode does not occur on the live path.** `compute_sk` passes `original_source` whenever `_scoring_prose` is true (line ~10925), so `_baseline_code_is_parseable` always fires on the A19 path. Executed:

```
baseline  listing 1  def good(): return 1   (parses)
          listing 2  def bad(:   return 2   (does not)
fix       breaks listing 1 AS WELL
shipped → g1=1 "it ALSO failed before this fix", g2=1, A=1, ADMISSIBLE
```

The blob does **not** let listing 2 condemn listing 1. It lets listing 2 **absolve** listing 1. The concatenation contaminates the *abstention*, and the direction is **over-admission**, not over-rejection — a fix that broke working code was admitted. This is the residue `_baseline_code_is_parseable` names in its own docstring ("a fix that breaks a listing DIFFERENTLY from how the baseline was broken is swallowed") and leaves open.

I also tried to construct the over-rejection case and could not: `"\n\n".join` of individually-parsing top-level blocks parses (checked, including the `from __future__` ordering case). Over-rejection from concatenation alone is essentially unreachable; over-admission is reachable and demonstrated.

**So per-hunk is the right target — but per-hunk *attribution*, not per-hunk `A`.** `A` stays a scalar, so `compute_rk`'s single-`sk` contract is untouched.

## Q2 — the three questions

Derived independently, then confirmed by Wolfram (local kernel, exit 0, symbolic + 10-digit numeric agreement):

| quantity | form | @ R=.99, q=.3 |
|---|---|---|
| blend / conditional on non-detection | `qR(1−R)/(1−qR)` | 0.0042248 |
| exact marginal (tower) | `qR` | 0.297 |
| ratio | `(1−R)/(1−qR)` | 1/70.3 |

*(symbolic forms cross-checked with Wolfram Language, local Wolfram Engine via `wolframscript`)*

**Q2.3, on the 13 of 124: I re-measured it and the brief undercounts its own defect.** Denominator 124 confirmed. But CLOSED ∧ `verified=True` ∧ ADMISSIBLE ∧ non-curing is **18 = 14.5161%**, not 13. The `sk = 1.0` qualifier drops 6 more at sk ∈ {0.98, 0.7143, 0.7} — still admitted, still non-curing. The harm is a third larger than stated.

```
Q1_VERDICT:      per-hunk — but ATTRIBUTION only, and for the opposite reason the brief gives.
                 Executed: the blob does not let listing 2 CONDEMN listing 1 (the baseline guard
                 always fires on the A19 path); it lets listing 2 ABSOLVE listing 1. Measured
                 failure direction is OVER-ADMISSION: a fix that broke a listing which parsed
                 before was ADMITTED at A=1. I could not construct the over-rejection case at all.

Q1_DESIGN:       `_gateable_hunks` (same regex + dedent as `_gateable_source`, no join) +
                 `_fix_broke_a_working_hunk(modified, original, path, check)`, consulted by g1/g2
                 ONLY to convict. Index-paired; unequal listing counts return False and fall
                 through to the existing blob logic untouched. `check` is the caller's own
                 compiler (ast.parse vs compile differ on `return 0` — that mismatch has already
                 produced one wrong verdict here). ~40 lines, no new flag, no new entry point.

Q1_DOWNSTREAM:   Nothing. A hunk-wise `A` would be the wrong build: `compute_rk` takes one `sk`,
                 and a vector A has no defined reduction — min() rejects the whole fix on one bad
                 hunk (the brief's feared behaviour, now real), mean() invents a partial-credit
                 semantics S_k does not have, and either way `apply_sk_to_rk`'s NO_SCORE/score
                 distinction would need a third case. Attribution is per-hunk; `A` stays scalar;
                 `sk` stays scalar; compute_rk is byte-identical.

Q1_FIX:          bench/reference_runner_v3.py  (+_gateable_hunks, +_fix_broke_a_working_hunk,
                 3 call-site edits in _run_hard_gate_ast / _run_hard_gate_compile)

Q1_FALSIFIER:    bench/tests/test_hunkwise_attribution_2026-09-22.py
                 exit 1 BEFORE (AssertionError + FALSIFIED: "A=1 ... ADMITTED because listing 2
                 was already broken") / exit 0 AFTER.
                 Strictly-additive proven in the same file: abstention preserved where the fix
                 did not touch the broken listing; pre-existing conviction preserved; unpairable
                 fix not convicted; .py target unaffected.
                 Regression: 50 passed — test_hard_gates_non_python_target,
                 test_prose_listings_are_scoreable_2026-09-11,
                 test_a19_gates_and_baseline_share_a_substrate_2026-09-11,
                 test_fix_efficacy_wiring_2026-08-30, + the new file.

Q1_REFUTED_BY:   A real prose target whose two listings each parse alone but not concatenated —
                 that would make over-rejection reachable and per-hunk A (not just attribution)
                 the right build. Or a caller that passes original_source=None on the prose
                 scoring path, which would restore the brief's over-rejection story. Or an
                 archived run where index pairing convicts the wrong listing because a fix
                 reordered fences without changing their count — my guard does not catch that.

Q2_1: answered — they are TWO DIFFERENT CLAIMS, both recorded as wins, and the second is
      narrower than the first. Astra's claim is about §4 of the revised specification (does it
      contain both branches and the tower property). The 2026-09-21 panel's claim is about the
      APPENDIX's Phase 2 (is revert-to-prior at σ=0 a discard). The panel's own record settles
      it against conflation: F1 says Phase 2's σ=0 value is the tower property and CC1's revision
      discards the unfavourable branch — but F2, in the SAME round, says Phase 2 "interpolates
      between a quantity conditional on non-detection (σ=1) and a marginal expectation (σ=0) …
      not exact except at σ=0", verdict PARTIAL. So the appendix is exact at ONE POINT of the
      interpolation and approximate everywhere else. "Phase 2 is correct" is true only of σ=0.
      Astra's §4 claim is separately true and is not evidence for the appendix claim.

Q2_2: answered. The blend bounds the expected improvement CONDITIONAL ON THE NO-DETECTION
      BRANCH: R − R(1−q)/(1−qR) = qR(1−R)/(1−qR). Astra's 0.297 is the UNCONDITIONAL
      expectation qR, obtained by the tower property over both branches. Ratio (1−R)/(1−qR) =
      1/70.3 at her point. It does NOT justify the stopping rule. A stopping rule is evaluated
      BEFORE the observation, so the ex-ante quantity is qR; the blend conditions on an event
      that has not happened and has probability 1−qR = 0.703.
      THE DIRECTION IS THE POINT, AND IT REVERSES F2's "harmless". F2 proved appendix ≥ exact on
      the LEVEL — conservative for a gate firing on R ≥ threshold. But a higher level IS a
      smaller increment: the same inequality makes ΔR UNDERSTATED, and `scripts/
      appendix_corrections_2026-09-21.py` records that "the Hard Exit fires on `dR = 0`". So a
      ΔR-differencing caller exists, and for it the bias is ANTI-conservative. F2's refutation
      condition ("a caller that treats R_k as a calibrated probability") is the wrong one; the
      exposure is a caller that DIFFERENCES R_k, which F2 did not consider.
      The record already contains the closing half, in the same script, correction 3: ΔR is
      unimodal with peak R* = (1−√(1−q))/q, "PREMATURE-STOP BAND at the highest-risk states".
      Verified with SymPy: R* = 0.5445 at q = 0.3, so Astra's R = 0.99 sits inside that band.
      Her counter-example is an instance of a defect the project had already derived and had not
      connected to her question.

Q2_3: answered — and it answers MORE than circularity, in the WORSE direction. Circularity means
      the AFTER separation is uninformative. The 124-record measurement shows the incorporated
      signal is not merely uninformative but OPERATIONALLY INERT: a probe that fired
      FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER changed no verdict. My re-measurement: 18/124 =
      14.5161% (not 13/10.4839% — the brief's `sk = 1.0` qualifier drops 6 admitted non-curing
      fixes at sk ∈ {0.98, 0.7143, 0.7}; 12 sit at exactly 1.0). Mechanism confirmed by the
      repo's own producer run today: at w1 = 2.0 with other gates clean, E = 5/7 = 0.714286
      against break-even S* = 0.50493, so e1 = 0 cannot pull sk below the line — 0 of 7 probed
      non-curing fixes rejected. At w1 = 5.0 or as a hard gate, 7 of 7 rejected and 0 of 13
      curing fixes wrongly rejected, so one option dominates on a named property and needs no
      preference to choose.
      DIRECTION: it does not rescue the scorer from Astra's charge, it deepens it. She asked
      whether the AFTER separation shows independent performance. The answer is that it does not
      even show the wiring MATTERS — a p = 9.89e-27 separation coexists with zero verdict flips,
      because the weighted mean averages the signal away. Worse, the producer's own non-circular
      proxy runs the WRONG WAY: mean sk 0.983953 for later-extended fixes vs 0.956555 for never-
      extended (p = 0.000035), and it is underpowered (d = 0.5133 observed vs 0.4877 detectable).

ASTRA_STATUS:    All 3 closed, and the reason nobody "went back to them" is not that nobody did —
                 it is that the work did not land. `panel_adjudication_cc_seat_2026-09-21.py`
                 derives Astra's Q2.2 exactly (SymPy + z3 unsat + mpmath, header "A2 ASTRA CLAIM
                 2 — conservative bound != conservative stopping rule") and exists ONLY at
                 bench/logs/final_review_2026-09-21/sandbox_harvest/cc2/attempt-1/files/scripts/.
                 It is not in scripts/. An adjudication that ran, passed, and was never harvested
                 is an addition nothing reaches — the project's own dominant defect class (11 of
                 11 since 2026-08-01). Harvest it and Q2.1/Q2.2 have a committed producer.
                 The brief's criticism of scripts/scorer_separation_is_circular_2026-09-21.py is
                 correct — it globs bench/logs/*/runner_state.json and the arms are at
                 bench/logs/commissioning_*/ — but it is no longer load-bearing: today's
                 scripts/e1_mechanism_consequences_2026-09-22.py reads the arms and prices the
                 fix. One defect in it: its docstring quotes 46/248 = 18.5484% while the script
                 prints 7/20 = 35.0000%. Two figures, one script, different populations, no
                 statement of which — the measured-rate-travels-with-its-script rule broken
                 inside the script that invokes it.
                 NOTHING BLOCKS EXPERIMENTAL VALIDATION on the maths. What blocks a validation
                 of the REPAIRED SCORER is that the archive is underpowered by its own
                 calculation, so a new run is required — and that run should not launch at
                 w1 = 2.0, because the arms already show that setting flips no verdicts.

REFUTED_BY:      Q2.1 — a reading of revised §4 showing it asserts the appendix's σ-blend rather
                 than the two branches, collapsing the two claims into one.
                 Q2.2 — showing no shipped caller differences R_k (which would restore F2's
                 "harmless in direction"), or showing the Hard Exit's dR test runs on a
                 quantity other than compute_rk's output. Either kills my direction argument
                 while leaving the algebra intact.
                 Q2.3 — a per-entry recomputation of S* from that entry's own nu_b, nu_f, q, R
                 showing the 0.50493 constant misplaces the break-even, so that some of the 18
                 were in fact near the line; or evidence that those 18 were closed by the
                 falsifier path with S_k not load-bearing, making the admission harmless.

DISAGREEMENT:    With the brief itself, on Q1, and it is the sharpest thing I have. It asserts
                 "a syntax error in the second condemns the first" and I could not reproduce
                 that on the live path — the baseline guard abstains for the whole blob, so the
                 shipped behaviour is the exact opposite: the second listing EXONERATES the
                 first. Had per-hunk been built to the brief's rationale — loosening a gate
                 believed to over-reject — it would have widened an over-admission that is
                 already real and measured. Direction, not existence, was the load-bearing fact,
                 and the brief has it backwards.
                 Secondary, with F2 of 2026-09-21: "harmless in direction" is safe for a level
                 and unsafe for an increment, and the project's own Hard Exit reads the
                 increment. A conservative bound and a conservative stopping rule are not the
                 same property, and F2's stated refutation condition would never have caught it.
```

**Not verified:** nothing material was left unchecked. Wolfram ran locally and agreed symbolically and to 10 digits; every other figure I quote I either executed or took from a producer I ran.
```

### `fable` — model `fable`, 85 tool calls, 10164 characters

```text
All evidence in: 66 targeted gate/S_k tests pass against the patch. Final answer.

---

# Panel reply — Fable seat

**A note before the shape:** my first falsifier draft came back CLEAN — an indented `return 0` fragment *concatenates into valid Python* inside the preceding listing, so the blob defect didn't fire. That is itself evidence: blob gating's verdict depends on **adjacency accidents** between unrelated listings, a third pathology beyond the two the record names. The committed falsifier uses a fragment (`elif` arm) that genuinely breaks the blob.

```
Q1_VERDICT:      per-hunk. The record's named target is right, and the live defect is
                 WORSE than the brief's demo: since the 2026-09-11 baseline guard, the
                 dominant blob failure is inverted — an illustrative fragment ANYWHERE
                 in the document makes the baseline blob unparseable, so a fix that
                 breaks a listing that parsed perfectly at baseline is EXCUSED as
                 "also failed before this fix" and ADMITTED. Demonstrated live
                 (exit 1) before my patch. The brief's condemn-direction now only
                 bites in absolute mode; the excuse-direction bites in exactly the
                 guarded mode compute_sk uses. Both are blob-granularity
                 mis-attribution; per-hunk removes both, plus the adjacency
                 coupling above. On the founder's other half: the record's
                 refinement stands — purely prose is NO_SCORE, not REJECTED
                 (line 1809 is right: a reject is a claim; on pure prose the gates
                 observed nothing).
Q1_DESIGN:       per-hunk CLASSIFICATION, per-file VERDICT. One ~60-line shared
                 helper `_run_hard_gate_per_hunk` routed from g1 and g2 for non-.py
                 targets. A hunk is convicted only when it fails to parse AND is
                 attributable: not byte-identical to any baseline hunk (untouched
                 fragments excused), aligned same-index baseline hunk parsed
                 (fragment-edited-to-fragment excused), blob-baseline fallback when
                 hunk counts change (preserves old semantics in the unaligned case;
                 residue stated, not hidden). Absolute mode = per-hunk absolute,
                 verdict-identical to the old blob on every contract-test shape.
                 Nothing simpler is sufficient: any single-blob scheme keeps the
                 parse-adjacency coupling.
Q1_DOWNSTREAM:   a hunk-wise A never reaches compute_rk, by design. Per-hunk is where
                 ATTRIBUTION happens; A stays one scalar (the AND over attributable
                 hunk verdicts) and sk stays one number, because one fix resolves one
                 finding and R_k is per finding-class. A per-hunk sk vector would
                 need per-hunk finding attribution and per-hunk R_k, which nothing
                 upstream supports — do not build that half.
Q1_FIX:          bench/reference_runner_v3.py (helper `_run_hard_gate_per_hunk` +
                 routing in `_run_hard_gate_ast` and `_run_hard_gate_compile`;
                 `_gateable_source` untouched — ruff/bandit/g0/reducibility callers
                 unchanged)
Q1_FALSIFIER:    scripts/falsifier_per_hunk_hard_gates_2026-09-22.py
                 exit before = 1 (FALSIFIED: broken-good-listing admitted g1=g2=1)
                 exit after  = 0 (convicts the regression, excuses the fragment,
                 admits the prose-only edit). Non-regression: 66 gate/prose/sk
                 contract tests pass (test_hard_gates_non_python_target,
                 test_prose_listings_are_scoreable, test_a19_..., test_gate_writes_
                 no_files, compute_sk suite), 8306 deselected.
Q1_REFUTED_BY:   a committed measurement over a real design-note corpus showing the
                 per-index alignment excuse admits attributable breakage at material
                 rate (then drop the alignment excuse and accept fragment-edit false
                 convictions); or a demonstrated caller needing per-hunk A downstream.

Q2_1: ANSWERED — they are TWO different claims about TWO different artefacts, and
      both are genuine wins; the error is only in the headline's flattening.
      Astra's claim is about the REVISED SPEC: its §4 carries both observation
      branches explicitly (B+ and B−, with a false-positive rate f, spec lines
      122–128) and the tower CONTENT (E[B] = R, line ~159 — the term "tower" never
      appears; grep: zero hits). The panel's claim is about the APPENDIX: Phase 2 is
      exact at σ=0 (where it IS the tower property) and a never-understating bound
      for σ>0 (cc2's F2 verdict was PARTIAL — equation sound, documentation
      silent). Recording them as one claim would be wrong; recording them as two is
      right. The record's one-line headline (":11 The appendix is right") flattens
      the second into the first. I re-derived the tower identity with both branches
      and f: E[posterior] − R ≡ 0 (SymPy; Wolfram Language, local Wolfram Engine:
      FullSimplify → 0).
Q2_2: ANSWERED. The blend bounds RESIDUAL RISK, from above: R_base never understates
      the exact branch-averaged R_old(1−qσ) (z3 unsat, recorded; direction is the
      safe one for a risk register). It does NOT bound — in either direction — the
      quantity the stopping decision needs, because ΔR_k = qR(1−R)/(1−qR) is the
      change CONDITIONAL on the non-detection branch, while stopping is decided
      before the branch is known and needs E[improvement] = R·q·σ(1−ν) − ν(1−R).
      Verified by execution: at R=0.99, q=0.3 → ΔR = 0.00422475, exact = 0.297,
      factor 70.30 (SymPy and Wolfram Language agree, both computed). So no: a
      conservative bound on risk does not yield a conservative stopping rule — the
      greedy rule stops in the HIGHEST-risk band R ∈ [0.855, 1) at θ=0.05.
      RESIDUAL DEFECT, in scope because Astra asked about "the stopping rule
      actually used": the appendix now carries the full qualification (its lines
      207–231), but bench/directives/universal/cdsfl_operational.md §5 (lines
      205–219) — the text the models actually load — still states the greedy
      "continue while Σ w·ΔR > θ" rule UNQUALIFIED. The correction exists in the
      reference document and not in the operational one.
Q2_3: ANSWERED, in the negative, and the new data is worse than Astra's framing in a
      specific way: the incorporated outcome does not even reliably AFFECT the
      score. I re-scanned all 4 commissioning arms (124 probe records, confirmed;
      23 no-cure). Two distinct mechanisms:
      (1) THIRTEEN no-cure records are CLOSED, verified=True, ADMISSIBLE with
          e1_efficacy ABSENT from the gate mean — 12 at sk=1.0 and 1 at sk=0.98
          (the brief's "13 at sk=1.0" is off by that one record; the count 13 and
          rate 10.4839%, Wilson [6.2298%, 17.1128%], both reproduce). Mechanism
          found in code: the post-sweep reconciliation (~line 15636) probes fixes
          AFTER the verdict — by its own comment "it moves nothing that the gate
          reads" — and never re-runs S_k, so the outcome lands on the entry but
          never enters the score. Not averaging-away: NON-INCORPORATION.
      (2) EIGHT no-cure records where e1 IS wired at 0.0 score sk = 0.70–0.7143
          and are STILL ADMISSIBLE, because tristate = ADMISSIBLE iff sk > 0
          (line 11066) — there is no threshold, so e1 = 0 can never reject unless
          every other gate is also 0. This is the averaging-away the brief names.
      So: the scorer evaluation demonstrated neither independent performance
      (Astra's point, already conceded as circular) nor reliable incorporation
      (the new result). The circularity script's own conclusion — a non-circular
      test needs a held-out outcome and a NEW run — stands and is still unmet.
ASTRA_STATUS: All 3 are now closed as ADJUDICATIONS: Q1 yes-but-two-claims, Q2
      no-the-bound-is-on-the-wrong-quantity, Q3 no-and-worse. Two repair items
      block reading the validation, not running it: (a) cdsfl_operational.md §5
      still ships the unqualified greedy rule; (b) until the post-sweep probe
      outcome re-enters S_k (or those entries are marked unscored-on-efficacy) and
      an admission threshold exists, commissioning-arm results cannot be read as
      evidence about scorer performance — the 4 arms already ran with a scorer
      that admits demonstrated non-curing fixes at 0.71–1.0.
REFUTED_BY:  Q2.1/Q2.2 — a spec §4 or appendix text differing from the copies read,
      or a caller shown to treat R_k as a calibrated probability (then the
      conservative-bound defence of Phase 2 fails too). Q2.3 — a scan showing
      e1_efficacy present in the gate_details of the 13 (mine walked every
      runner_state.json in the 4 arm directories; a fifth arm or a different
      store would reopen it), or a committed threshold I failed to find that
      makes 0.7143 inadmissible.
DISAGREEMENT: with CC1/the brief's own diagnosis of the 13: "the incorporated
      signal is averaged away by the weighted mean" is FALSE for the 13 — for them
      the signal was never incorporated (post-verdict probe, no re-score). It is
      true only for the other 8. The distinction is material because the fixes
      differ: (1) needs a re-score after the post-sweep probe; (2) needs a
      threshold or hard-gate status for e1. One prose sentence conflating them
      would have produced one repair where two are required.
```

**Attribution:** the second-falsifier checks above were computed with Wolfram Language (local Wolfram Engine, via wolframscript); primary derivations SymPy/statsmodels, data claims by direct scan of the four commissioning `runner_state.json` files.

**Termination:** §6 criteria met — every hard assumption I relied on was executed, the last pass produced no new material finding, and the remaining observations (headline flattening at record :11; the 0.98-vs-1.0 discrepancy in the brief) are below threshold and noted above. Converged.
```

---

## Round `arm4_prose_anatomy_2026-09-22`

Brief: 1278 words, reproduced in the repository at `bench/logs/arm4_prose_anatomy_2026-09-22/BRIEF.md` and mirrored under `experimental_notes/evidence/`.

Seats that returned a reply: cx, ge.

### `cx` — model `cx`, 30 tool calls, 4422 characters

```text
- `verdict`: **PARTIAL**

- `reasoning`:
  1. **CC1 is materially wrong on at least one counted fact.**  
     CC1 says all 11 routing episodes were `rungs_tried=2` vs `rungs_available=5`.  
     My executed check over the same report found one counterexample: `C0014` had `rungs_tried=1`, `rungs_available=5`.  
     Evidence: my executed assertion failed with:
     ```
     AssertionError: [('C0001', 2, 5), ..., ('C0014', 1, 5), ('C0015', 2, 5)]
     ```
     So “all 11 are 2/5” is false.

  2. **UNTOOLABLE is assigned before any S_k scoring and for “no runnable falsifier”, not “nothing computational in prose”.**  
     In `bench/reference_runner_v3.py`:
     - `apply_falsifier_verdicts` sets `UNTOOLABLE` when `falsifier_code` is empty for critical findings (`5360`–`5365`).
     - S_k on prose returns `NO_SCORE` in `compute_sk` (`10862`–`10875`) and does not run scoring gates.
     - `apply_sk_to_rk` keeps risk unchanged on `NO_SCORE` (`11198`–`11203`).
     - `_evaluate_sk_for_findings` logs `NO_SCORE` and continues (`12207`–`12217`).
     In the arm4 report, `target_kind.kind=prose`, `sk_enabled_effective=false`, and entries had no `sk_result` in this run.  
     **Therefore, in this run, UNTOOLABLE vs REJECTED is not being decided by S_k.**

  3. **Ladder stopping is constant-governed, not gamma-governed.**
     - `bench/routing.py` hard-caps routing with `max_rungs: int = 2` in both `resolve_via_routing` (`139`) and `route` (`183`), and iterates `list(rungs)[:max_rungs]` (`158`).
     - In `bench/reference_runner_v3.py`, the `route(...)` call (`5975`–`5978`) does not pass any `max_rungs` override and does not pass gamma.  
     So rung stopping is from the routing cap, not gamma logic.

  4. **CC1’s truncation observation is supported.**  
     `routing_history.last_falsifier_code` is explicitly truncated to 600 chars (`reference_runner_v3.py:6003`), matching the 600-char pattern seen in the report.

  5. **Two-sided gate/severity model bearing.**  
     On this specific UNTOOLABLE-vs-REJECTED question, I found no evidence that two-sided gate logic determines that label. Severity still affects escalation pathways (critical/non-critical handling), but not the core UNTOOLABLE assignment trigger above.

- `falsifier_path`: **NONE (UNVERIFIED: tool limit hit before I could write a standalone file under `scripts/` or `bench/tests/`)**

- `falsifier_command`:  
  I executed an inline Python falsifier via the harness `execute_python` tool (not a saved file), checking:
  - routing default `max_rungs==2`,
  - runner does not pass gamma/max_rungs into `route(...)`,
  - CC1’s “all 11 are 2/5” claim.

- `falsifier_output`:
  ```
  Traceback (most recent call last):
    File "<string>", line 37, in <module>
      assert all(t==2 and a==5 for _,t,a in rows), rows
             ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  AssertionError: [('C0001', 2, 5), ('C0002', 2, 5), ('C0005', 2, 5), ('C0006', 2, 5), ('C0008', 2, 5), ('C0009', 2, 5), ('C0011', 2, 5), ('C0012', 2, 5), ('C0013', 2, 5), ('C0014', 1, 5), ('C0015', 2, 5)]
  ```

- `fix_path`: **NONE — UNVERIFIED (tool-call limit reached before I could commit a file edit/test in-repo).**  
  Proposed fix (not applied): correct `scripts/arm4_untoolable_anatomy_2026-09-22.py` to report the true rung distribution (e.g., histogram of `rungs_tried`) instead of implying all are 2/5.

- `refutation_condition`:  
  My conclusion would be overturned by either of:
  1. A code path in the same run where `UNTOOLABLE/REJECTED` is rewritten by S_k (with line-level evidence and execution trace), or
  2. A reproduction on the exact report showing all routing rows are truly `2/5` (i.e., disproving the observed `C0014: 1/5` row).

- `strongest_disagreement`:  
  Strongest disagreement with the brief framing: **“S_k is the instrument that decides this question” is wrong for this run.**  
  In this prose-target run, S_k is forced off (`sk_enabled_effective=false`) and compute path returns `NO_SCORE`; UNTOOLABLE comes from falsifier-gate/routing mechanics, not S_k adjudication. Treating S_k as decider here conflates “unscored fix quality” with “absence of runnable falsifier.”

- `passes_run`: **2**  
  - Pass 1: reproduce CC1 script/report facts and code-path read.  
  - Pass 2: targeted falsification of CC1’s strongest concrete claim; found `C0014` counterexample (`1/5`), no new higher-severity finding beyond that in final pass.
```

### `ge` — model `ge`, 16 tool calls, 2709 characters

```text
- `verdict`: PARTIAL

- `reasoning`: 
  1. **How UNTOOLABLE feeds `S_k`**: It does damage. Line 5424 of `bench/reference_runner_v3.py` explicitly groups it with refutations: `# an un-demonstrated critical (REFUTED, ERROR, or UNTOOLABLE) is`. Furthermore, line 1809 defines `NO_SCORE` as the mechanism for withholding from `S_k` when it has no opinion. Because `UNTOOLABLE` is treated as an un-demonstrated critical rather than `NO_SCORE`, it penalises the finding in the `S_k` score just as a `REFUTED` verdict does.
  2. **The ladder's stop**: The output of `arm4_untoolable_anatomy_2026-09-22.py` shows that all 6 `UNTOOLABLE` findings stopped at exactly `rungs_tried=2` out of `rungs_available=5`. Because I exhausted my tool calls before locating the exact ladder loop code, the mechanism governing this stop is UNVERIFIED. However, the uniform stop at exactly 2 across all 11 routing episodes strongly suggests a constant-governed cap rather than a dynamic diminishing-returns (gamma) stop.

- `falsifier_path`: NONE (Tool call limit reached before I could write the file).

- `falsifier_command`: NONE (Tool call limit reached).

- `falsifier_output`: NONE (Tool call limit reached).

- `fix_path`: NONE (Tool call limit reached before I could write the fix).

- `refutation_condition`: 
  1. My conclusion that `UNTOOLABLE` damages `S_k` would be overturned if the actual `S_k` scoring function (which I could not fully read) explicitly intercepts `EQUIPMENT_FAILURE_VERDICTS` (defined on line 1855) and converts them to `NO_SCORE` before the final calculation, despite the comment on line 5424 grouping them with `REFUTED`.
  2. My inference about the ladder stop would be overturned if the ladder loop actually evaluates a dynamic condition (like gamma) that coincidentally evaluated to true at exactly rung 2 for all 11 independent episodes.

- `strongest_disagreement`: The brief asks me to find what is wrong with CC1's reading. CC1 asserts that because `last_falsifier_code` existed, "UNTOOLABLE does not mean 'nothing to compute'". This is a logical leap. The existence of generated source code only proves that the *model attempted* to write a falsifier, not that the underlying prose target actually contained computationally accessible elements. A model can easily generate 600 characters of doomed regex, hallucinated assertions, or boilerplate imports against pure English text. The machinery giving up at rung 2 with truncated source is indeed a harness failure, but it does not prove the finding was genuinely toolable. CC1 conflates "the model wrote code" with "the target was computable".

- `passes_run`: 1 (Terminated due to tool call exhaustion; residual falsification debt remains).
```

---

## Provenance and cost

The rounds `overnight_review_2026-09-22` and `prose_and_astra_2026-09-22` were dispatched to the free seats only, `cc2` and `fable`, both on the Max subscription.

The round `arm4_prose_anatomy_2026-09-22` was dispatched at 11:41:59 BST WITHOUT the free-seat restriction, so it reached 5 paid seats. It was terminated at 11:44:38, about 2 minutes and 39 seconds in. `ge` and `cx` completed and their replies appear above; `cgpt`, `ds` and `kimi` were cut off before writing output and are partially billed. No cost field is recorded anywhere in the run, so the spend cannot be measured from the archive and no figure is offered for it. That round is NOT named in `bench/directives/universal/paid_dispatch_authorisations.json`, because the founder did not authorise it; the guard `TestNoPaidSeatWasDispatched` is red for that reason and is correct to be.

Written under CDSFL note standard v1.7 (26 August 2026).