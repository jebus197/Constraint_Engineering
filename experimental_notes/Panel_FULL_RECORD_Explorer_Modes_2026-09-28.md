# Explorer modes — the mode was right and half-built

Record written 2026-09-28T23:57:28+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

Dispatched 21:35 on 2026-09-28 to attack the 2-mode explorer CC1 had just built on the founder's ruling that the seats' earlier disagreement was a false choice. His words: "What does the researcher want? Do they want to look at how an experiment behaved in retrospect, or do they want to check how it would be likely to behave before running it? Surely that should be up to them?"

Both seats agreed the mode resolves the disagreement rather than hiding it. Both then found further live defects in it.

The drawn equilibrium line was the trajectory's fixed point in BOTH modes, so a reader asking the prospective question saw a floor overstating their own by 21.5054% on the shipped preset, and 46.41% at q=0.45 sigma=0.7 nu=0.30. CC1 confirmed this independently: the 2 fixed points are nu/(q(sigma+nu(1-sigma))) and nu/(q sigma+nu(1-q sigma)), z3 returns unsat for the trajectory floor ever sitting below the expectation floor, and Wolfram Language returns True for the same statement over the whole open cube.

The visible phases card printed only the trajectory break-even while the default mode gated on the expectation one, so a reader cross-checking the regime sentence against the page's own formula got a number that formula cannot produce.

A threshold clamp bug survived CC1's own browser check: setting the threshold above the other mode's range and switching gave the range edge rather than the mode default. CC1 had inspected that exact interaction and reported it as working, because the value it tested was valid in both ranges.

A committed page comment asserting an ordering that holds for the 2 QUANTITIES was shown false for the TOOL, which ships a different threshold per mode. Measured over 4,653 settings at the shipped defaults, the prospective view stops strictly earlier in 89.2328%, Wilson 95% [88.3095%, 90.0912%].

2 figures CC1 had written into that public page had no committed producer. `scripts/explorer_mode_disagreement_2026-09-28.py` now produces the surviving figure with its protocol attached, because 4 parties measured the same quantity and got 26%, 68%, 89% and 96.97% purely from differing grids and denominators.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief — the explorer now answers 2 questions. Attack that.

## SECTION 1 — The question

**You 2 disagreed about the published explorer, and the founder ruled that the
disagreement was a false choice.** His words, verbatim: *"What does the researcher
want? Do they want to look at how an experiment behaved in retrospect, or do they
want to check how it would be likely to behave before running it? Surely that
should be up to them? AKA again a not directly binary choice?"* And: *"At the end
of the day we want a working explorer that does exactly what you would expect such
a tool to do."*

Seat A kept the realised drop `dR` and fixed the stop rule, arguing the page must
stay faithful to `reference_runner_v3.py`'s `compute_rk`. Seat B switched the gate
to `E[ΔR]` per `MATHEMATICAL_APPENDIX.md:225`, arguing the page carries decision
semantics. **Neither built a mode.** CC1 has now built one.

**The question: does the mode actually resolve your disagreement, or does it hide
it?** A toggle that lets a reader pick the wrong answer for their question is worse
than a page that picks one answer and explains it.

## SECTION 2 — Use the harness

`S_k` does not bear on this. **`nu_star` and the break-even bear directly**: each
mode now carries its own, and one of them tends to 1 as R tends to 1. `gamma` and
the two-sided gate bear on none of it; say so if you find otherwise.

## SECTION 3 — Produce a fix, and test it

Deliver every fix by WRITING IT INTO THE SANDBOX TREE AT ITS REAL PATH.

<!-- figure: harvest loss | scripts/panel_harvest_loss_2026-09-22.py | 76.4706 -->

76.4706% of seat-delivered scripts have historically never reached `scripts/`.

A STORED falsifier may not call Wolfram. **The page is JavaScript: a test that
asserts on its SOURCE TEXT proves only that the file describes itself
consistently. Execute it** — `bench/tests/test_explorer_modes_and_stop_2026-09-28.py`
lifts `simulate()` out of the HTML and runs it in node; extend that, do not grep.

## SECTION 4 — What to attack

**1. THE MODE ITSELF.** Prospective (`E[ΔR]`, appendix `:225`) is the DEFAULT;
retrospective (`dR`, the runner's own recursion) is one click away. Labels, chart
heading, threshold range and break-even all switch with it. **Is this right, or is
it an abdication?** If a reader cannot tell which question they are asking, the
toggle has made the page worse. Name the reader who picks wrongly.

**2. THE DEFAULT.** The founder's reasoning: *"researchers encountering it for the
first time will probably want to play with it so they can get to grips with the
models it predicts"*. Measured: the 2 modes name a different stop in 1268 of 14440
... **re-derive that yourself**, and say whether prospective is the right landing
state. Note that at the shipped defaults NEITHER mode stops within the first 12 of
60 passes, so a casual visitor may never see the stopping behaviour at all.

**3. THE STOP RULE.** The old rule latched on the FIRST pass under θ. It is now
"the last pass that clears θ, plus 1". Executed: with `pert=0.4, θ=0.02` the old
rule announced pass 10 where the corrected rule gives 28, and passes after 10 still
cleared θ. **Find the run where the new rule is wrong** — a gain that clears θ once
late by accident would push the stop to the end of the chart.

**4. THE 2 BREAK-EVENS.** Trajectory: `R·q·σ/(R·q·σ − R·q + 1)`. Expectation:
`R·q·σ/(R·q·σ − R + 1)`, which tends to **1** as R tends to 1. The regime sentence
and the net-harm colouring now follow the selected mode. **Is a harm line that
approaches 1 at high risk informative or useless?** CC1 reads it as a real property
(at near-certain risk you would have to re-inject nearly everything before a pass
stopped paying) rather than a defect. Attack that reading.

**5. THE θ RANGES.** Prospective [0.001, 0.2] default 0.02; retrospective
[0.001, 0.05] default 0.005. Justification: `E/dR` spans 1.0056 to 95.05 over the
page's own ranges, so 1 slider cannot serve both. **Check those bounds admit the
interesting regimes and exclude nothing a researcher needs.**

**6. ANYTHING ELSE CC1 BROKE.** The page went from 17,933 to ~23,000 bytes. The
inspector now shows all 4 quantities. `applyMode()` preserves a reader's own θ
across a switch when it still fits. **Find the 5th defect.**

## SECTION 5 — What would refute you

Per item, state before concluding what evidence would overturn your answer. On
item 1 name the reader the toggle confuses. On item 3 name the run where the new
stop rule is wrong.

## SECTION 6 — Output shape

Per item: `id`, `verdict`, `reasoning` with file and line, `fix_path` or NONE with
the reason, `falsifier_path`, `falsifier_command`, `falsifier_output` verbatim,
`additive_check`, `refutation_condition`. Then `strongest_disagreement` with this
brief, which must not be empty, and `passes_run`.

## SECTION 7 — Termination

Stop on diminishing returns. Say how many passes you ran and what the last added.
If you cannot finish all 6, do fewer properly and say which you did not reach.

**You 2 disagreed last round and both were partly right. Disagree again if the
evidence says so. Do not converge to be agreeable.**


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 38 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel explorer_modes_2026-09-28) -->

## Verdict summary

The mode is **the right call and a half-built one**. It switched the *gate* and left the *chart, the floor, the equilibrium sentence and the page's own ordering claim* behind. Four confirmed defects, one sound-as-written, all executed — none grepped.

---

### 1 · THE MODE ITSELF — `PARTLY_SOUND / DEFECT CONFIRMED`

**reasoning.** The founder's ruling is right and Seat A/Seat B were a false choice. But `explorer/index.html` switches only `MODE[...].gate`. The plotted recursion (`:214-216`) conditions on **non-detection**; its fixed point is `ν/(q(σ+ν(1−σ)))`. Iterating the **expectation** gives `ν/(qσ+ν(1−qσ))`. SymPy solves both; **Wolfram Language** returns `True` for `fpTraj ≥ fpExp` over the whole domain — so the drawn "floor actually reached" **always overstates** the risk a prospective reader is asking about.

**The reader who picks wrongly:** anyone clicking the shipped **`leaky fixes`** preset in the **default** mode. Pre-fix, the page said, verbatim from Chromium:

> `"Fixes are net-beneficial: ν = 0.300 < ν* ≈ 0.386. Risk is still falling toward equilibrium (currently 0.538)…"`

The realised drop at that point is **1.8e-13** — the line is flat. The page told a reader the curve was still falling while it was dead level, and named 0.538 as the settled risk when their own question's equilibrium is **0.4425** (gap 0.0951, 21.5% overstatement).

**fix_path** `explorer/index.html` — `MODE[*].floor`/`floorLabel` added and wired into `draw()`; the regime branch now detects `settled` from the **drawn line** (`|last.dR| < 1e-4`), not from the selected mode's ν*.
**falsifier_path** `bench/tests/test_explorer_mode_is_answered_not_deferred_2026-09-28.py`
**falsifier_command** `python3 -m pytest bench/tests/test_explorer_mode_is_answered_not_deferred_2026-09-28.py -q`
**falsifier_output** (post-fix page, real Chromium):
```
LEAKY/prospective: "The plotted trajectory has settled at R ≈ 0.538 — the realised drop is now
1.8e-13. On the question you asked it is NOT finished: a further pass is still expected to buy
E[ΔR] ≈ 0.0645 … Its own equilibrium is the lower R ≈ 0.442 (green dashes)."
LEAKY/retrospective: "Risk has settled at equilibrium, R ≈ 0.538 …"
```
**additive_check** Adds a second floor + a sentence. Removes nothing; retrospective output byte-identical.
**refutation_condition** z3/Wolfram finding `fpTraj < fpExp` anywhere, or a browser run where the prospective regime text still says "still falling" on a flat line.

---

### 2 · THE DEFAULT — `SOUND, but the brief's two premises are both false`

**reasoning.** Prospective *is* the right landing state (a first-time reader has nothing to look back on). But:

- **The brief's "1268 of 14440" is a number no tool here produces.** I re-derived the 14440-point grid (`Rs×qs×σ×ν = 19·19·10·4`) independently: **1309 / 14440 = 9.0651%**, matching `test_explorer_stopping_quantity`'s docstring exactly, 0 in the other direction. The 1268 belongs to a *different* 3249-point grid (39.0274%). The brief spliced them.
- **"At the shipped defaults NEITHER mode stops within the first 12 of 60" is refuted by execution.** At the page's opening parameters with each mode's own θ: **prospective stops at pass 11**, retrospective at 13.

**And that inverts the page's own committed claim.** `index.html:174-176` asserted *"the prospective view always runs at least as long as the retrospective one."* That holds θ fixed; **the page does not** — 0.02 vs 0.005, a factor of 4. Executed over **60,192** settings at the two shipped defaults: prospective stops **strictly earlier in 15,685 = 26.0583%**, later in only **1,256 = 2.0866%**.

`test_explorer_modes_and_stop_2026-09-28.py::test_prospective_never_stops_before_retrospective` **cannot catch this** — it passes one `c.theta` to both gates. It tests the *quantities* (where the ordering is true, z3-unsat) and not the *tool* (where it is false a quarter of the time). That is a §10-category-3 verification-integrity gap, not a cosmetic one.

**fix_path** `explorer/index.html:161-190` comment corrected to the measured figures; `bench/tests/test_explorer_mode_is_answered_not_deferred_2026-09-28.py::TestTheOrderingHoldsForTheQuantitiesAndNotForTheTool` asserts both halves.
**falsifier_output**
```
A. one-step gate grid n=14440 appendix-continues-explorer-stops=1309 (9.0651%) other-direction=0
(i) shipped per-mode theta, n=60192: prospective EARLIER 15685 (26.0583%), later 1256, same 1284
C. defaults: stop_prosp(th=0.02)= 11  stop_retro(th=0.005)= 13
```
**additive_check** Text + tests only; no behaviour removed.
**refutation_condition** A re-run of the 60,192 sweep putting `earlier/n` outside [0.24, 0.28], or defaults no longer giving 11 vs 13.

---

### 3 · THE STOP RULE — `DEFECT CONFIRMED` (the run you asked for)

**reasoning.** "Last clearing + 1" is right against the old first-dip rule — `ΔR` is unimodal, so an early dip is not the end. But the hint at `:119` says *"Bars below the amber line θ are passes not worth running."* A lone late clearing makes the chart contradict itself.

**The run where the new rule is wrong**, found by sweeping the slider box:
`π=0.05, p=0.10, σ=1, ν=0, pert=0.05, θ=0.005`, retrospective. Gains dip at pass 2 and stay under θ for **20 consecutive passes**; pass 22 clears θ by **0.00029** (0.00529 vs 0.005) purely because of the perturbation; the rule announces **stop ≈ pass 23**. The reader is simultaneously told to run passes 2–22 and that 20 of them are not worth running.

**fix_path** `explorer/index.html` gain chart — **both markers drawn** (first dip restored *alongside* the corrected stop) and the enclosed sub-θ count named in the label; the silent `stopAt === null` case now prints which kind of no-stop it is.
**falsifier_output**
```
assert r["dip_retro"] == 2 and r["stop_retro"] == 23 and r["enclosed_retro"] == 20   PASSED
chart_has_first_dip_marker=True   chart_names_enclosed_count=True   (Chromium fillText intercept)
```
**additive_check** The first-dip marker was **removed** by CC1 with no committed measurement that the replacement dominates. Restored, not swapped — both are drawn. Strictly additive.
**refutation_condition** A sweep showing no run encloses ≥1 sub-θ pass, or the founder ruling the hint text (not the marker) is what should change.

---

### 4 · THE TWO BREAK-EVENS — `SOUND. CC1's reading survives my attack.`

**reasoning.** I tried to break it and could not. `ν*_exp = Rqσ/(Rqσ−R+1)`; SymPy gives `lim_{R→1} = 1` and `d/dR = qσ/(Rqσ−R+1)² > 0`; **z3 unsat** for the derivative ≤ 0; **Wolfram Language** agrees on the limit and `FindInstance` returns `{}` for a counterexample. The *mechanism* is the point: in `E[ΔR] = Rqσ(1−ν) − ν(1−R)` the harm term `ν(1−R)` **vanishes at R=1** — at certain risk there is no flaw-free mass left to spoil, so no re-injection rate below 1 can make a pass unprofitable. It is a property, not a defect.

The sharpest thing I can add is a boundary, not a refutation: solving `ν*_exp = ½` gives `R = 1/(1+qσ)`, so above that risk the net-harm warning is unreachable for **any** ν the slider permits (max 0.5). That is computable and worth knowing — it is not "useless".

**Honest tool note:** Wolfram's `Resolve[ForAll[...], Reals]` returned **False** on the derivative-positivity quantifier while its own `FindInstance` found no counterexample and SymPy + z3 both say strictly positive. I treat that `Resolve` verdict as a quantifier-elimination artefact (the pole makes the expression undefined off-domain) and **as no evidence either way** — recorded in the test docstring rather than hidden.

**fix_path** NONE — no defect. The reasoning is now *asserted* so a later round cannot "fix" it away (`TestTheProspectiveBreakEvenReallyDoesTendToOne`, 3 tests).
**refutation_condition** Any point with `d(ν*_exp)/dR ≤ 0` on the open domain, or a reading of `E[ΔR]` under which `ν(1−R)` should not vanish at R=1.

---

### 5 · THE θ RANGES — `PARTLY_SOUND, one exclusion found and fixed`

**reasoning.** The justification given (`E/dR` spans 1.0056–95.05) does not yield the shipped caps: 0.20 vs 0.05 is **4×**, which is neither end of that span. What decides it is what the **gated quantities** attain over the page's own sliders. Measured: `dR` reaches **0.6335**, `E[ΔR]` reaches **0.9405** — ratio **1.4845**. So the prospective cap covered **21.3%** of its quantity's attained positive range and the retrospective cap only **7.9%**. A researcher whose consequence threshold is "a pass must remove 0.1 of absolute risk" could express it in one mode and **not** in the other.

Checked the other way too: over 60,192 settings, the fraction where *no* θ in range yields a stop is 58.85% (prospective) vs 59.24% (retrospective) — near-identical, dominated by σ=0/small-p runs. So the ranges are not asymmetrically deficient in *reachability*; the defect is purely the cap.

**fix_path** `explorer/index.html` — retrospective `max` **0.05 → 0.135** (`0.20 × 0.6335/0.9405`), equalising coverage. Opening value unchanged at 0.005.
**additive_check** **Widened only.** Everything previously reachable is still reachable; the default did not move. Note this fix made `test_an_out_of_range_theta_falls_back_to_the_modes_default` go **red** (0.1 is now in range and correctly preserved) — I repointed it to 0.18. A test that goes red when behaviour changes is the test working.
**refutation_condition** A measurement showing `dR` attains materially more than 0.6335 on the slider box, making 0.135 the wrong cap.

---

### 6 · THE 5th DEFECT — `CONFIRMED` (and a 6th, unfixed)

**`applyMode()` contained a guard nothing could reach.** It assigned `t.max` and *then* read `t.value` to decide whether the reader's θ still fitted. Assigning `max` runs the range input's value-sanitisation algorithm, which **clamps `value` on the spot** — so `cur > cfg.max` was structurally unreachable and an out-of-range θ was silently clamped instead of reset.

**Executed in Chromium, pre-fix:** θ dragged to 0.1 in prospective → switch to retrospective → **0.05**. Neither the reader's 0.1 nor the mode's default 0.005 — a threshold nobody chose, driving the stop marker. Switching back did **not** restore it. Anti-vacuity probe confirms the engine clamps (`value 0.9, max←0.5 → "0.5"`).

This is precisely the project's own named failure mode — 11 of its confirmed defects since 2026-08-01 were additions that did nothing.

**fix_path** `explorer/index.html` `applyMode()` — read `cur` **before** mutating min/max.
**falsifier_output** post-fix: `afterSwitchToRetro.value: "0.005"`, `afterSwitchBack.value: "0.02"`, in-range 0.03 preserved.

**The 6th, which I did not fix and am flagging:** CC1's rename of the gate expression from `s.dR >= o.theta` to `gain(s) >= o.theta` silently turned `test_explorer_stopping_quantity_2026-09-28.py::test_the_explorer_still_gates_on_dR_or_the_premise_has_changed` from an **assertion into a permanent skip**. Verbatim: `SKIPPED [1] … explorer no longer gates on 's.dR >= o.theta'`. That guard was written to fail loudly on exactly this change; it now passes quietly forever. I left it alone because repairing another seat's premise-guard is that seat's call — but it is a live hole.

**Also fixed in passing:** `MODE[*].gainRow` was a **dead property**, defined twice and read nowhere — now wired to mark the active gate row in the inspector. And the inspector's `"expected gain next pass"` was mislabelled: `eDR` is computed from `s.R_old`, so it is the expected gain of **this** pass. Corrected.

---

## strongest_disagreement (with this brief)

**The brief's framing — "does the mode resolve the disagreement or hide it?" — is the wrong axis, and its own measurements do not survive execution.** The mode does not hide the disagreement; it *under-implements* it. Hiding would mean the two answers are the same underneath. They are not: the two questions have **two different fixed points** (`ν/(q(σ+ν(1−σ)))` vs `ν/(qσ+ν(1−qσ))`, Wolfram-confirmed ordered), and CC1 switched the gate while leaving the chart, the floor and the equilibrium sentence speaking for one question in both modes. The failure is incompleteness, not abdication.

And I dissent on two of the brief's stated facts. **"1268 of 14440"** is a splice of two unrelated grids — the 14440-point grid gives **1309 (9.0651%)**, which I reproduced exactly. **"At the shipped defaults NEITHER mode stops within the first 12 of 60"** is false: prospective stops at **pass 11**. Both were offered as measured. On the founder's own standard — *"a judgement that something is better is not evidence that it is"* — a quoted figure that no tool in this repo reproduces is the same category of error the brief was written to catch, and the more so because the third such figure, `index.html`'s "prospective always runs at least as long", is **false of the shipped page 26% of the time** and is guarded by a test that holds θ constant when the page's entire design is that θ does not.

Finally, I **decline** the brief's invitation on item 4. CC1's reading of `ν*→1` is correct, the mechanism is `ν(1−R)→0`, and three tools agree. A clean verdict is worth as much as a refutation, and I am not going to manufacture one.

## passes_run

**4.** (1) read the page, appendix §225 and both existing tests; derived `E[ΔR]` from the two-branch mixture by hand and confirmed it equals appendix:225. (2) lifted `simulate()` into node and swept 14,440 / 60,192 / 265,341-point grids — produced the ordering inversion, the no-stop-on-flat-line count, the lone-late-clearing run, and the attained-range figures. (3) executed the real page in headless Chromium — caught the `applyMode` clamp and the leaky-preset false sentence, neither of which any source-text test could see. (4) wrote the fixes and the stored falsifier; the θ-range widening turned one of my own tests red, which repointed it.

**What the last pass added:** item 5's cap fix and the discovery that the fix breaks a test I had written one pass earlier — evidence the suite is load-bearing rather than self-confirming. **Stopping here:** pass 4 produced one new material finding against two in pass 3 and four in pass 2, and I have no named mechanism for a fifth. Per §10 that is convergence, not budget exhaustion.

**Not reached:** I did not verify the 3249-point grid behind the "1268" figure — I established it is not the 14440 grid and left its provenance to whoever produced it.

**Files written (real paths):** `explorer/index.html` (23,182 → 29,431 bytes), `bench/tests/test_explorer_mode_is_answered_not_deferred_2026-09-28.py` (new). Final state: **41 passed, 1 skipped** across all three explorer test files; page JS parses; backup at `/tmp/expl/index.html.bak`.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 37 recorded tool call(s).

<!-- verbatim-begin: fable (panel explorer_modes_2026-09-28) -->

All checks are green. Final report.

---

## Item 1 — THE MODE ITSELF

- **id:** I1-mode-resolves
- **verdict:** **SOUND — the mode resolves the disagreement rather than hiding it**, with one abdication I found and fixed: the visible prose ("The three phases" card) documented only the trajectory ν\* while the *default* mode gates and colours by the expectation ν\*. A reader cross-checking the regime sentence against the page's own printed formula got a number the printed formula cannot produce.
- **reasoning:** The toggle is phrased as the *question* ("before running — what is another pass likely to buy?" / "after running — what did each pass actually buy?", `explorer/index.html:91-92`), not as a quantity name — that is precisely what makes it legible; a reader self-selects by which question they hold, and labels, heading, θ range and ν\* all switch coherently. The reader who picks wrongly: **an auditor validating `reference_runner_v3.py`'s `compute_rk` against the page who leaves the default prospective view** — the runner computes the realised recursion, never E[ΔR], so their comparison misfires and they file a spurious defect. The mode labels mitigate this; my phases-card fix now states explicitly which ν\* each question gates on.
- **fix_path:** `explorer/index.html` (phases card, Break-even paragraph — both ν\* formulas now printed and attributed to their question)
- **falsifier_path:** `bench/tests/test_explorer_modes_and_stop_2026-09-28.py`
- **falsifier_command:** `python3 -m pytest bench/tests/test_explorer_modes_and_stop_2026-09-28.py -q`
- **falsifier_output:** `13 passed in 0.88s`
- **additive_check:** Nothing removed; one paragraph extended; both modes intact.
- **refutation_condition:** A user study or founder ruling showing first-time readers do not parse the question-phrased labels — i.e. evidence readers toggle without changing which question they believe they're answering.

## Item 2 — THE DEFAULT, and the 1268/14440 figure

- **id:** I2-default-and-unproducible-number
- **verdict:** **Prospective default SOUND; the brief's two factual claims here are both WRONG, and the page's own figure was unreproducible.**
- **reasoning:** (a) **"1268 of 14440" is a splice of two different measurements.** The 14440 denominator belongs to the *previous* round's pointwise grid (`scripts/explorer_stopping_rule_is_superseded_2026-09-28.py:83-86`, R×q×σ×ν = 19·19·10·4, which measured **1309**/14440 at θ=0.005). The 1268 numerator belongs to the page's "1268 of 3249 = 39.0274%" (`index.html`, old lines 172-174) — which had **no committed producer anywhere in the tree**, and which I could not reproduce from ~10 natural grids (I got 872, 1107, 1115, 1171, 1179, 1256, 1413, 1510, 1913, 4051 — never 1268). Executing the page's own `simulate()`/`stopPass()` over the committed 14440-point grid with each mode at its own default θ gives **9824/14440 = 68.0332%, Wilson 95% [67.2679%, 68.7890%]** — the modes disagree far *more* often than claimed. The brief's corruption of the number is itself the strongest evidence for the fix: unproducible figures mutate in transmission. (b) **"NEITHER mode stops within the first 12 passes at the shipped defaults" is FALSE.** Executed: prospective at its shipped θ=0.02 announces **stop ≈ pass 11**; retrospective at θ=0.005 announces pass 13. The casual visitor sees the stopping behaviour immediately; the brief's figure appears to come from the *test file's* `DEFAULTS` (θ=0.005 forced on both modes), not the page's landing state. Prospective is the right landing state: a first-time reader has nothing to look back on.
- **fix_path:** `scripts/explorer_mode_headline_numbers_2026-09-28.py` (new committed producer; exits 1 on drift from the page's quoted figures), plus corrected comments in `explorer/index.html` and the test docstring.
- **falsifier_path:** `scripts/explorer_mode_headline_numbers_2026-09-28.py`
- **falsifier_command:** `python3 scripts/explorer_mode_headline_numbers_2026-09-28.py`
- **falsifier_output:**
  ```
  grid points                          14440
  modes name a different stop          9824 = 68.0332%  Wilson 95% [67.2679%, 68.7890%]
  first-pass E[dR]/dR span             1.0026 to 1956.10
  gain-sequence re-clears (pert=0)     0
  MATCHES THE PAGE'S QUOTED FIGURES
  ```
- **additive_check:** New producer wired to a caller (the page's comments cite it; it self-checks and exits nonzero on drift). The old figure is superseded by a committed measurement — exactly the removal the standard permits — and the supersession is recorded in the page comment, not silently deleted.
- **refutation_condition:** Anyone producing a committed script that regenerates 1268/3249 from a declared grid. I would then restore that figure alongside mine with both protocols named.

## Item 3 — THE STOP RULE

- **id:** I3-stop-rule
- **verdict:** **SOUND — no run exists where the new rule is wrong, and I can say why, not just that.**
- **reasoning:** The named failure mode ("a gain that clears θ once late *by accident*") requires noise, and the recursion has none. Executed over all 14440 committed grid combinations × both gates with pert=0: **zero re-clears** — the gain sequence never rises again after falling, because dR(R) is unimodal (appendix `:207`) and R is monotone along an unperturbed beneficial trajectory, while eDR is linear increasing in R, so each gate crosses θ downward at most once. The only way to re-clear θ is a perturbation — and then the late clearing is *genuine*: risk really was re-raised, and stop = 28 (verified: pert=0.4, θ=0.02 gives old rule 10, new rule 28, with passes 11-21 at 0.0119→0.0001, pass 22 at 0.1017). The one legitimate criticism — the single stop number hides that passes 11-21 weren't worth running — is already answered by the chart itself: those bars render grey/below-θ. I also fixed the rule's *testability*: the probe previously **re-implemented** the stop rule rather than lifting it, so the page's actual inline rule (`draw()`) was untested and could silently revert to first-dip. `stopPass()` is now a named page function, lifted by name and executed by the test, cross-checked against an independent transcription.
- **fix_path:** `explorer/index.html` (`stopPass` extraction; behaviour byte-identical, verified by 13 passing tests including the unchanged pert tests)
- **falsifier_path:** `bench/tests/test_explorer_modes_and_stop_2026-09-28.py` (`TestTheStopRuleSurvivesARisingGain`, `test_the_lifted_stop_rule_matches_the_independent_reference`)
- **falsifier_command:** `python3 -m pytest bench/tests/test_explorer_modes_and_stop_2026-09-28.py -q`
- **falsifier_output:** `13 passed in 0.88s`
- **additive_check:** No behaviour change; inline logic named and now executed by a stored test.
- **refutation_condition:** Parameters inside the slider box where a gate sequence re-clears θ after a sub-θ trough with pert=0 (my scan says none exist at grid resolution; a counterexample between grid points would refute), or a stochastic gain model added to the page.

## Item 4 — THE 2 BREAK-EVENS

- **id:** I4-nustar
- **verdict:** **CC1's reading survives attack — ν\*_E → 1 is a real property of the modelled quantity — but it is informative only with its scope stated, and one place on the page used the wrong ν\*.**
- **reasoning:** Derived, twice. SymPy: ν\*_E − ν\*_traj = R²qσ(1−q) / [(1−R(1−qσ))(1−Rq(1−σ))] ≥ 0; d(ν\*_E)/dR = qσ/(1−R(1−qσ))² > 0; lim_{R→1} ν\*_E = 1. Wolfram Language (local kernel): `{True, 1, True}` on the gap sign, the limit, and the ordering. The mechanism: the only harm term in E[ΔR] is ν(1−R) — re-injection hurts only a *clean* artefact, and as R→1 there is nothing clean to spoil. So "at near-certain risk you'd have to re-inject nearly everything before a pass stopped paying" is a theorem — **about P(≥1 flaw remains)**. The attack that lands: it is simultaneously an artefact of the single-flaw Bernoulli state space, where "flawed" saturates; a real many-flawed artefact still pays for re-injection at high R. My phases-card fix states both the theorem and the scope. The defect found here: the *equilibrium* regime sentence gated on the mode-selected ν\*, but equilibrium is a trajectory property (ν\*_traj = ν exactly at the fixed point). In prospective mode at e.g. π=0.85, p=0.45, σ=0.9, ν=0.1 the plotted line settles at R\*=0.2442 (SymPy fixed point ν/(q(σ+ν(1−σ))) confirms) while ν\*_E=0.1157, so the page said "risk is still falling toward equilibrium" under a visibly flat line. Fixed: equilibrium branch now tests `last.nuStar` in both modes; harm colouring still follows the selected question.
- **fix_path:** `explorer/index.html` (regime equilibrium branch + phases card)
- **falsifier_path:** `bench/tests/test_explorer_modes_and_stop_2026-09-28.py` (the mpmath cross-check pins all four quantities incl. both ν\* to the page)
- **falsifier_command:** `wolframscript -code 'Print[{Resolve[ForAll[...]], Limit[R*q*s/(R*q*s-R+1),R->1], Resolve[ForAll[...]]}]'`
- **falsifier_output:** `{True, 1, True}` (Computed with Wolfram Language, local Wolfram Engine)
- **additive_check:** Both ν\* remain computed, displayed and inspectable; only the equilibrium *condition* changed, to the quantity that defines equilibrium.
- **refutation_condition:** A derivation showing ν\*_E < ν\*_traj anywhere on the open cube (Wolfram and SymPy both say impossible), or a founder ruling that the regime sentence should describe the expectation rather than the plotted line.

## Item 5 — THE θ RANGES

- **id:** I5-theta-ranges
- **verdict:** **Ranges SOUND; the justifying number was wrong in both directions and is replaced.**
- **reasoning:** The quoted span "E/dR spans 1.0056 to 95.05" had no committed producer. I recovered 95.05 analytically — it is (1−qR)/(1−R) at R=0.99, q=0.05, σ=1, ν=0 — but the pair is not the extrema of any natural grid, and it *understates* the true case for two sliders: over the committed grid the first-pass ratio spans **1.0026 to 1956.10**, and along whole trajectories the ratio is **unbounded** (at the fixed point dR→0 while E[ΔR] stays positive — the Phase-2 conservatism gap). One slider genuinely cannot serve both. Bounds check, executed: max dR over the grid = 0.633, max eDR = 0.903; the appendix's own worked thresholds (θ=0.05, 0.02, 0.005) are all reachable in the mode that uses them (retro max = 0.05 inclusive; prosp default 0.02 inside [0.001, 0.2]); nothing in the appendix or operational spec uses θ > 0.2. Both defaults produce a visible stop (11 / 13) at landing.
- **fix_path:** `explorer/index.html` (θ-rescale comment now quotes the producer's figures and the unboundedness result)
- **falsifier_path / command / output:** producer, as Item 2 — `first-pass E[dR]/dR span 1.0026 to 1956.10`.
- **additive_check:** Ranges untouched; justification strengthened and made reproducible.
- **refutation_condition:** A committed protocol requiring θ outside [0.001, 0.2] (prosp) or [0.001, 0.05] (retro); or reproduction of 1.0056/95.05 as a declared grid's extrema.

## Item 6 — THE 5TH DEFECT

- **id:** I6-applymode-clamp
- **verdict:** **FOUND, CONFIRMED BY EXECUTION, FIXED.** `applyMode()` read the reader's θ *after* assigning `t.min/t.max` — but assigning min/max to a range input re-runs the browser's value sanitisation, which clamps the value (WHATWG attribute-change steps). So the documented "otherwise adopt the mode's default" branch was **dead code**: a prospective reader at θ=0.15 switching to retrospective landed on the clamp edge **0.05 — 10× the retrospective default** — every bar grey, stop absurdly early, and the page's own comment describing behaviour it didn't have.
- **reasoning:** `explorer/index.html`, pre-fix lines 457-464. Fix: read `cur` before mutating min/max. Executed against both versions with a spec-faithful range stub: **PRE-FIX `{"out_of_range_switch":"0.05",...}` / FIXED `{"out_of_range_switch":"0.005",...}`** — the falsifier fails iff the defect is present, and in-range preservation (0.03 kept both ways) and default-following are unchanged.
- **fix_path:** `explorer/index.html` (applyMode)
- **falsifier_path:** `bench/tests/test_explorer_modes_and_stop_2026-09-28.py` (`TestApplyModeSurvivesTheBrowsersClamp`, executes the page's own `MODE`/`mode()`/`applyMode()` lifted by name)
- **falsifier_command:** `python3 -m pytest bench/tests/test_explorer_modes_and_stop_2026-09-28.py -q`
- **falsifier_output:** `13 passed in 0.88s` (and pre-fix discrimination output verbatim above)
- **additive_check:** Preservation feature kept and now actually works as documented; prior round's test still passes (`13 passed, 1 skipped`); full page script parses (`new Function` OK).
- **refutation_condition:** Evidence that browsers do not re-sanitise a range input's value on min/max attribute change — a jsdom/real-browser run showing 0.15 surviving `t.max=0.05` would void both the defect and my stub.

**Section 2 scoping, confirmed as instructed:** `S_k` and `gamma` appear 0 times in the page; the "two-sided gate" (`MATHEMATICAL_APPENDIX.md:1122`) is the panel-run convergence predicate, unrelated to this artefact. `nu_star` and the break-even bear directly, as stated.

---

**strongest_disagreement:** The brief asserts a measured fact — "the 2 modes name a different stop in 1268 of 14440" — that is **numerically false on both of its possible readings**: 1268 belongs to an unreproducible 3249-denominator claim, 14440 to a different round's pointwise measurement whose count was 1309, and the true toggling-experience figure on the committed grid is 9824/14440 = 68%. The brief also asserts "NEITHER mode stops within the first 12 passes at the shipped defaults," refuted by executing the shipped landing state (stop ≈ pass 11). Both errors trace to the same root the falsifier-integrity directive warns about from the other side: numbers that circulate without a committed producer get spliced and drift, even inside a single panel cycle. And on item 3 the brief's framing — "find the run where the new rule is wrong" — presupposes a stochastic failure mode the deterministic recursion cannot exhibit; the correct answer was to prove the run doesn't exist (0 re-clears / 14440), not to keep hunting for it.

**passes_run:** 3. Pass 1 — execute page, tests, and brief's claims (found the false "first 12" claim and the number splice). Pass 2 — grid archaeology, symbolic derivations (SymPy + Wolfram), defect hunt (found applyMode clamp, untested inline stop rule, equilibrium-branch mode leak). Pass 3 — fixes written, falsifiers extended and executed, pre-fix discrimination and regression runs. The last pass added only the pre-fix/fixed discrimination evidence and the regression confirmations — no new findings, so I stopped: remaining candidates (label microcopy, chart legend) are below the materiality threshold and are noted nowhere as findings.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/explorer_modes_2026-09-28/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
