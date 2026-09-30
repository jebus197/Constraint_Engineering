# A19 as a STEM calculator: the flag is the wrong instrument, and the affirmative channel is already committed

Record written 2026-09-30T14:40:01+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## The dispatch

**FREE SEATS ONLY. 0 paid dispatches, 0 spend.** Second design review held BEFORE implementation under the founder's 2026-09-30 policy. The harness warned that 3 of its 5 default seats are paid; `PANEL_ONLY=cc2,fable` restricted it to the 2 claude_cli Max seats, because his standing rule forbids paid dispatch without express authorisation.

| seat | route | elapsed | tool calls | passes |
|---|---|---|---|---|
| cc2 | claude_cli (Max) | 1316.2 s | — | 5 |
| fable | claude_cli (Max) | 1598.3 s | 73 | 4 |

**The harness refused the first brief twice and the commit gate 3 times more, every reason substantive:** the brief did not require the fix to be DELIVERED as a file (rounds 5 and 6 of a prior arc returned 0 source files because seats wrote into scratch that teardown destroyed); it stated no termination criterion; the new figure producer ignored `--help` and ran the whole measurement; the round needed mirroring; and the memory ledger was stale. **7 figures were declared for RE-EXECUTION** rather than typed, after the validator named the incident that justifies it — a brief typed `gamma is 0.451` when the value is 0.415413, briefing 2 seats on the wrong number.

## Where the seats AGREE

1. **A19's flag is the WRONG INSTRUMENT for the founder's requirement.** cc2: *"It scores a fix; the calculator needs a verdict on a claim."* fable: *"the flag is a smoke detector being asked to certify the building."* Both answer his sub-questions the same way: sufficient for a meaningful test of the VETO today; **not** sufficient for the calculator.
2. **The affirmative channel already exists in the repository and is wired to nothing.** fable: *"committed, bidirectionally validated, and wired to nothing."* The live path reaches the corpus 0 times.
3. **What is needed is WIRING, not new science.** fable names 3 wirings — supply, e1-for-prose, and prose-e2 defined as the claim suite. cc2 concurs that the deciding machinery already exists at claim level, naming `reverify_falsifier` running a per-claim falsifier as the thing that returns a verdict.
4. **No finite weight can make `e1_efficacy` veto.** cc2 derives it: `E(e1=0) = 5/(w1+5) > 0` at every finite `w1`, and `tristate = ADMISSIBLE if sk > 0` has no threshold. So a GATE is the only instrument. Both built one.
5. **`a` IS a cumulative coefficient.** Q6 settled by calling the fitter, `bench/decay_analysis.py::fit_duane`, an `alpha·n^gamma` fit to `np.cumsum`.
6. **`(4.89, 0.709)` is UNSOURCED.** cc2: 0 of 421 committed curves reproduce the pair. fable: absent from all 379 archived fits swept — *"mixed provenance"*.
7. **`rounds = 10` survives only as an empirical BUDGET CAP, never as `ceil(n*)`**, and the recommendation is deliberately independent of the coefficient answer.
8. **The advisory number must be repaired by fixing its INPUTS and stating what it can say — never suppressed.** Both, matching the founder's ruling.
9. **Accuracy and meaning are different repairs.** cc2 measured the trap: with real baselines the advisory reads 1.0 on all 5 correct fixes AND 1.0 on both harmful fixes it scores, **0 of 5 separation**, while the decision beside it separates 3 of 5.

## Where they DISAGREE, preserved because it is the information

**The corrected `n*` value, and they are a factor of about 33 apart, each with 3-to-4-tool agreement.** cc2: `a` is cumulative but **1.6447 is also wrong** because it takes a continuous derivative of a discretely-indexed series; the discrete answer is **2.1879** (mpmath, SymPy, `scipy.brentq` and Wolfram Language agreeing to 12 digits). fable: the convention-consistent form is `(a·gamma/theta)^(1/(1-gamma))` = **71.6994** at `(4.89, 0.709)` and **147.4350** at the actual record (SymPy, mpmath and a local Wolfram Engine agreeing to every digit), and **1.6447 is refuted by the fit's own data** because the `alpha = 4.8969` series still yields 2 novel per round at round 5. **GAMMA IS LOAD-BEARING**, so this is the founder's to resolve.

**Q5 remedy for the copy-counted-as-original conflation.** cc2: **content-hash dedup, not a path predicate** — the conflation inflates its own Q3 number by **53.7313%** (309 to 201); path filtering and content dedup give an identical count, so hashing dominates on robustness-to-renaming at equal accuracy; a path predicate would need **259** edits and relocating harvest moves 182 MB. fable: **option (b), namespace separation** — a shared predicate cannot bind `.gitignore` or `co_filename`, and a guard test shares those blind spots, while separation removes the class for every consumer language at once.

**Q4 repair route.** cc2 took the one-line argparse-default repair (`--test-cmd` default to `None`) *because* the `argv()` repair also requires editing a committed test, and the tree already carries a contradiction between that test and a prior seat's script. fable took the three-state `test_cmd` repair in `Arm.argv()` with an explicit `--test-cmd ""`, and updated the committed test, recording the reasoning in its docstring.

**Whether a non-cure should REJECT or ESCALATE.** fable built REJECT and names the cost asymmetry that decides it — a wrong REJECT returns with feedback, a wrong ADMIT lowered risk 73 times — but states plainly that **ESCALATE is the softer alternative if the founder wants a human on every non-cure**. It calls this a ruling, not a computation.

## New findings neither review had, and 2 are serious

**A SANDBOX CONTAINMENT BREACH, found by fable in its own run.** Its regression run failed with tracebacks pointing at the REAL repository: the staging copy carried **988 `.pyc` files** whose `co_filename` names the real repo, so `Path(__file__)` in a cached test module resolves OUTSIDE the sandbox and can import real-repo modules into a panel measurement. Demonstrated by running `strings` on the `.pyc`, purging, and re-running. The immediate remedy is a one-liner — staging and harvest must exclude `__pycache__` and `*.pyc` — but the staging code is not in this tree, so it is a suggestion with evidence rather than a patch. **This bears directly on the founder's hard rule that no model should be able to reach the real repository.**

**THE COMMITTED FALSIFIER CORPUS HAS THE ARM-4 DEFECT ONE LEVEL DOWN, found by cc2.** It proposes a third control beside the existing two-way discrimination: a falsifier run against a document whose bytes are GONE must not return REFUTED. Executed over the 5 committed fixtures through the runner's own `reverify_falsifier`: pristine **5 of 5**, corrected **5 of 5**, and the new blank check **3 of 5** — `structural` and `metrology` return REFUTED on an empty document, caused by `if block is None: print("NOT FALSIFIED"); exit 0`. So 2 of the 5 falsifiers this project relies on as proof that prose is decidable cannot tell a claim from an absent document.

**THE FLIP IS NECESSARY BUT NOT SUFFICIENT, established by fable falsifying its own proposal.** The metrology HARMFUL fix also earns the falsifier flip — `pristine=CONFIRMED` to `harmful=REFUTED` — because it repairs the false claim while corrupting the evidence table. So admission must require the flip AND veto-clean AND the document's other claims' falsifiers green. Executed: flag ON gives 0 of 10 fixes ADMISSIBLE, Wilson [0.00%, 27.75%]; the correct-fix flip is 5 of 5, Wilson [56.55%, 100%].

**TWO INCOMPATIBLE QUANTITIES ARE BOTH NAMED `gamma`**, both seats independently. cc2 measured 0.8776 against 0.2143 on the same data; fable located the conventions — the runner's `_estimate_gamma` computes `1 - beta` while `decay_analysis` uses `gamma_d = beta`, giving 0.2654 against 0.2583 on one series. cc2 adds that **no live module emits `a`**, so the harness cannot evaluate `n*` at all.

**`(a/theta)^(1/gamma)` solves a rate law no fitter in this repository produces**, per fable, failing the fitted model's own stopping equation with a residual far from 0.

## What the seats found wrong in CC1's own work, accepted

**A HARDCODED LITERAL IN MY OWN FIGURES SCRIPT, caught by cc2:** *"the brief's '73 of 73' is a hardcoded literal in the figures script, not a live count; the live deduplicated count is 201."* That is precisely the defect the declared-figure mechanism exists to prevent, and this session shipped it. **3 measurements now exist and I cannot reconcile them** — 73, 201 and 309 — and a re-measurement here returned 0 records, so my accessor does not match the archive's shape either. The figure is **WITHDRAWN** rather than replaced, and the dispute is recorded as an open item.

**MY INVARIANCE CLAIM WAS CORRECT BUT INCOMPLETE, fable's named disagreement.** No verdict and no R_k moves, which both seats re-executed. **But** the contaminated `"52/55 passed (sandbox)"` also reaches the archived `gate_details` and the HIL evidence bundle, and costs roughly 1.7 GB of repository copy plus 55 unrelated tests of wall-clock per fix per round. So "decision-inert" understated the cost.

**A retraction of its own from cc2**, recorded under `failure-later-refutation-protocol`: it first reported 3 false rejections of correct fixes in Q2, then found the cause was its own fabricated zero ruff baseline, and rewrote the script to call `_capture_baseline`.

## Deliverables, in the sandbox trees

cc2: `experimental_notes/cc_a19_calculator_design_2026-09-30.md`, falsifiers `scripts/q1…q6_*_2026-09-30.py`, and code changes to `bench/reference_runner_v3.py` (e1 veto) and `bench/tools/run_simulated_experiment.py`. fable: `experimental_notes/fable_a19_calculator_design_2026-09-30.md`, `scripts/a19_affirmative_channel_2026-09-30.py` and `scripts/n_star_convention_settled_2026-09-30.py`, plus proposed `_e1_veto` and advisory-basis fields in the runner and a three-state `test_cmd` in the arms. **All SUGGESTED to the human, none applied to this tree.** cc2 reports 381 targeted tests green; fable reports 344 affected tests passing.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Free panel, design review BEFORE build: what makes a prose target answerable?

**Dispatched 2026-09-30 by CC1 on the founder's instruction.** Standing policy since 2026-09-30: *the panel reviews a design BEFORE it is built, not after.* Nothing here is built. Your job is to say what should be built and what evidence would show it works.

## Hard constraints, non-negotiable

- **You are in your own sandbox copy. Do NOT write to the real repository.** The founder's rule: *"none of the models... should ever be able to reach the real repo, let alone edit it!"*
- **Never touch `~/.config/cdsfl/scoring.env` or any answer-key store. Never print a secret value.**
- **`execute-do-not-grep`.** A claim asserting on the SOURCE TEXT of a module asserts only that the module describes itself consistently. Where a producer and a consumer both exist as live code, CALL them and compare outputs.
- **`measured-rate-travels-with-its-script`.** Every rate, proportion or count you report must come from code you ran, and you must show the command and its output. Any proportion needs a confidence interval.
- **Cross-verify every computational claim with at least 2 independent tools** (SymPy and mpmath, scipy and statsmodels, z3 and exact rationals). A Wolfram call that errored verified nothing.
- **`feedback_no_model_voting`.** Findings are confirmed programmatically or by the human, never by model agreement. Do not report consensus; report executed evidence.
- **`feedback_fixes_hil_only`.** Every fix you propose is SUGGESTED to the human. Do not present a proposal as decided.
- **No compelled convergence.** Disagreement between seats is information and is preserved. If you disagree with the other seat, say so and say why, with evidence.
- **`simplicity-default` and the additive standard, both directions.** The simplest sufficient design wins. An addition nothing reaches is not additive; a removal needs a committed measurement showing the replacement dominates on a named property.

## The founder's requirement, verbatim, and it governs every answer below

> *"CDSFL is, was and will remain envisaged to be a STEM calculator. Input computationally addressable/reducible question in, get definitive answer out. So whatever option we go with (or whatever the panel may already, or may yet advise), this is the logic we need to follow. The question is how do we do that, even with the kind of prose targets under discussion? Or is what we have done sufficient for a meaningful test already? Is there something else we need to do?"*

He also observed, of the 2 options he was offered on task A19, that **"by either of these options the result would produce nothing useful"** — and the measurements below say he is right about that.

## Declared figures. These are RE-EXECUTED when this brief is validated, not taken from CC1's typing.

`scripts/panel_brief_validate.py` runs the producer below and refuses this brief if any value fails to reproduce. That mechanism exists because a prior brief typed a gamma of 0.451 when the value is 0.415413, and 2 seats were briefed on the wrong number.

<!-- figure: e2_constant_on_prose | scripts/a19_calculator_brief_figures_2026-09-30.py | 0.9454545454545454 -->
<!-- figure: E_with_substituted_suite | scripts/a19_calculator_brief_figures_2026-09-30.py | 0.978182 -->
<!-- figure: E_floor_at_2_or_more_new_HIGHs | scripts/a19_calculator_brief_figures_2026-09-30.py | 159/275 -->
<!-- figure: S_star_break_even | scripts/a19_calculator_brief_figures_2026-09-30.py | 0.50493117097042334623290819418709903839714462053309 -->
<!-- figure: e1_uncured_fix_score | scripts/a19_calculator_brief_figures_2026-09-30.py | 0.7142857142857143 -->
<!-- figure: live_path_modules_reaching_the_prose_corpus | scripts/a19_calculator_brief_figures_2026-09-30.py | 0 of 5 -->
<!-- figure: new_HIGH_rejection_lower_bound | scripts/a19_calculator_brief_figures_2026-09-30.py | 51.0109 -->

## Measured facts, established 2026-09-30 by execution. Treat as data, and re-verify anything you intend to rely on.

1. **On a prose target with `sk_score_prose_listings` ON, `ADMISSIBLE` is UNREACHABLE.** `reference_runner_v3.py:11624`: `if _scoring_prose and tristate == SK_ADMISSIBLE:` — both arms return. Any new defect gives `REJECTED` with `sk = 0.0`; none gives `NO_SCORE`. Executed: 1 new bandit HIGH rejects; 1 new ruff diagnostic alone rejects; 1/2/5/20 new HIGHs all reject, 4 of 4, Wilson [51.0109%, 100.0000%]. So the instrument can refuse or abstain, and cannot affirm.
2. **The recorded justification for leaving the flag off is stale.** `CDSFL_MASTER_TASK_LIST.md:568`, dated 2026-09-11, states as its *"DECISIVE FACT FOR THE RULING"* that the archived exploit is *"STILL ADMITTED AT sk=1.0000"*, and that *"1 new HIGH is not enough to reject; 2 are"*. Against current code the same committed fixture `tk.SHELL_INJECTION_FIX` returns `NO_SCORE` at `sk = 0.0`, and 1 new HIGH rejects. The cause is `_prose_one_sided`, added 2026-09-22, 11 days after that measurement.
3. **`e2_regression` runs on prose and cannot see its target.** `Arm.argv()` guards `--test-cmd` with a truthiness test, so arm4's `test_cmd=None` emits no flag and argparse substitutes the immune-memory suite for `bench/dm/_memory.py`. The prose document with real bytes and with its bytes destroyed both return `0.9454545454545454`; a `.py` target gutted returns `None`. The 52/55 is an artefact: `_run_effect_regression` copies `REPO_ROOT` with `secret_ignore(..., 'logs')`, so 3 tests fail for the missing `bench/logs` alone. **No verdict moves** — the veto reads only the e3/e4 `new:` fields and is invariant across 7 e2 values.
4. **The advisory number is the only live residue.** `_prose_one_sided` preserves `computed_sk` *"so a human reviewer could see what the gates would have said"*. It reads **0.9782** with the substituted suite and **1.0** without it. Removing the false input moves it UPWARD. SymPy, `Fraction` and mpmath agree: `(2·52/55 + 1 + 2)/5 = 269/275 = 0.978182` against `(1 + 2)/3 = 1`.
5. **On the Python path, a fix that does not work is admitted.** A fix measured not to cure its own falsifier scores exactly `5/7 = 0.7142857142857143` (SymPy, `Fraction`, mpmath agreeing to 1.586e-17), is recorded `ADMISSIBLE`, and moves R_k from 0.5 to 0.495688. Since `inf` over e1 of E is 5/7 > 0 and `tristate = ADMISSIBLE if sk > 0`, **no finite weight lets `e1_efficacy` veto**. Archive: 73 of 73 `ADMISSIBLE`, Wilson [95.0008%, 100.0000%].
6. **The founder has cleared the objection that previously blocked fixing 5.** The recorded reason was that reweighting *"changes which fixes are admitted on every Python target ever run."* His ruling, 2026-09-30: *"'Every target ever run' is acceptable, since these experiments exist to uncover problems of this nature. Conversely 'every target that will ever be run in the future' is clearly also equally acceptable for the same reason, providing it plugs the hole and makes the instrument more accurate?"* Note the question mark: the clearance is conditional on evidence, not granted outright.
7. **A committed prose falsifier corpus exists and the live path does not reach it.** `bench/tests/fixtures/stem/` holds 5 ground-truth STEM documents, 29 tagged claims (24 true, 5 false) and a runnable `falsifier_template` each; all 5 discriminate bidirectionally through the runner's own `reverify_falsifier`. Importers: 2 test files, 5 measurement scripts, 1 simulation tool. **`reference_runner_v3.py`, `routing.py`, `falsifier_verify.py`, `immune_agents.py` and `runner_core.py` mention it 0 times each.**
8. **A recurring structural conflation.** Copies of archive artefacts are stored INSIDE the archive namespace, at paths differing only by depth (`<run>/sandbox_harvest/<seat>/attempt-N/files/bench/logs/<run>/`). 3 separate mechanisms were bitten by it on 2026-09-30: a `.gitignore` rule that versioned 20 byte-identical duplicates while excluding 88 unique seat scripts; an archive counter inflated 14.8359%; and CC1's own scan, where path-aware resolution collapsed 1066 raw hits to 17.

## Questions. Answer each separately. Where you cannot settle one by execution, say so and name what would settle it.

**Q1 — THE PRIMARY QUESTION. What mechanism yields a DEFINITIVE AFFIRMATIVE answer on a prose target?** The founder wants a calculator: reducible question in, definitive answer out. Fact 1 says the current instrument can only refuse or abstain. Generate 2 to 4 distinct candidate mechanisms independently, then falsify each. Then answer his 2 sub-questions directly: **is what already exists sufficient for a meaningful test?** and **what else, if anything, is needed?** Consider explicitly whether A19's flag is even the right instrument for this requirement, or whether it is a harm guard being asked to do a job it cannot do.

**Q2 — Make the advisory number accurate AND meaningful, without suppressing it.** His ruling: *"No we don't present false information. Nor do I like the sound of 'suppression'. It sounds like hiding? How about we instead try to fix it so that the HIL is provided only with fully accurate information instead? How about in other words we make this number accurate and meaningful? Is that possible?"* Note the trap in fact 4: removing the false input yields an honestly-derived 1.0, which is accurate in derivation and still uninformative, because the project's own recorded reasoning says a clean static sweep on prose carries no information. Distinguish accuracy from meaning and say what design delivers both.

**Q3 — Design the `e1_efficacy` veto on the Python path, and name its evidence.** Fact 6 clears the way conditionally. What exactly should be built, and what measurement would show it *plugs the hole and makes the instrument more accurate* rather than merely changing which fixes pass? A verdict count that changes is not evidence of improvement.

**Q4 — Should `test_cmd=None` mean NO GATE rather than a substituted default?** And the founder's specific question: **what is the consequence DURING A RUNNING EXPERIMENT** of each option? CC1 measures that no verdict and no R_k moves and only the advisory number shifts 0.9782 to 1.0 — verify or refute that, and consider whether any other consumer of the e2 record is affected.

**Q5 — Remedy for the structural conflation in fact 8.** Candidates to weigh, not endorse: a single shared "is this a copy" predicate every consumer must use; moving harvest out of the archive namespace entirely so no glob can reach it; a guard test refusing any new archive scan that does not use the shared predicate. Which is simplest sufficient, and what does each cost?

**Q6 — Settle `n* = (a/theta)^(1/gamma)`.** A prior round reported that `_estimate_gamma` fits the CUMULATIVE curve, making `n* = (a(1-gamma)/theta)^(1/gamma) = 1.6447` rather than 9.3805, a factor 5.70, but could not locate the fitting code to decide whether `a = 4.89` is cumulative or a rate coefficient. Find the fitting code and settle it by execution. **GAMMA IS LOAD-BEARING** — a standing founder directive. Also: both seats of a prior round recommended `rounds = 10`; say whether that survives your own analysis and whether it depends on the answer.

## Delivery. A design left in prose is destroyed at teardown and does not count.

**Write your answer INTO the sandbox repository tree at its real path, not into scratch space.** Rounds 5 and 6 of a prior arc returned 0 source files because both seats wrote into scratch that `panel_sandbox.teardown` deleted. Specifically:

- **The design itself** goes to `experimental_notes/<seat>_a19_calculator_design_2026-09-30.md` in your sandbox tree, as a real file at a real path.
- **Every falsifier you run** goes to `scripts/<descriptive_name>_2026-09-30.py` in your sandbox tree, committed-shaped and runnable from the repository root, so the figure it produces travels with the script that produced it.
- **Any proposed code change** is written as a fix INTO the module it belongs to, at its real path, so a reviewer can diff it. Do not paste a patch into your reply and leave the tree untouched.

A fix or a design that exists only in your reply text is not delivered. Your reply should point at the files, not substitute for them.

## When to stop

**Terminate on diminishing returns, which is this project's own criterion.** Concretely: stop when 2 consecutive falsification passes produce no new finding above the real-world-consequence threshold, or when every HARD assumption in your design has been tested and survives. Budget up to 5 passes. Do not pad: `p-pass-anti-nitpick` forbids generating findings for their own sake, and a design review that stops early with its HARD assumptions tested is finished, not lazy.

If you cannot reach that state on a question, say which HARD assumption remains untested and what would test it, rather than continuing past the point of return.

## Output format

For each question: your position, the executed evidence, and your strongest attempt to falsify your own answer. Name any disagreement with the other seat explicitly. If a question is not computationally reducible, say which part is not and why, rather than producing a qualitative opinion dressed as a finding.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 157 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel a19_calculator_design_2026-09-30) -->

All 7 declared figures reproduce unchanged after my edits; all 6 falsifiers exit 0.

## Delivered into the sandbox tree

- **Design:** `experimental_notes/cc_a19_calculator_design_2026-09-30.md`
- **Falsifiers:** `scripts/q1…q6_*_2026-09-30.py`, runnable from the repo root
- **Code changes, for diff:** `bench/reference_runner_v3.py` (e1 veto), `bench/tools/run_simulated_experiment.py` (`--test-cmd` default → `None`). Both SUGGESTED, not decided.

## The six answers

**Q1 — A19 is the wrong instrument.** It scores a *fix*; the calculator needs a verdict on a *claim*. The affirmative mechanism already exists at claim level. I propose adding a third control to the existing two-way discrimination: **B — a falsifier run against a document whose bytes are gone must not return REFUTED.** Executed over the 5 committed fixtures through the runner's own `reverify_falsifier`: P 5/5, N 5/5, **B 3/5**. Two committed falsifiers (`structural`, `metrology`) return REFUTED on an empty document — the arm-4 defect one level down, caused by `if block is None: print("NOT FALSIFIED"); exit 0`. B is reached and load-bearing. *Sufficient for a meaningful test today; not sufficient for the calculator* — the live path reaches the corpus 0 times.

**Q2 — accuracy and meaning need different repairs, and I measured the trap.** With baselines captured by the runner's own `_capture_baseline`: the advisory is **1.0 on all 5 correct fixes and 1.0 on both harmful fixes it scores — 0/5 separation**, while the decision beside it separates 3/5. Q4 buys accuracy and zero meaning. Design: fix the inputs, rename it to `static_harm_sweep: CLEAN`, and attach its measured discrimination. No suppression.

**Q3 — derived, not asserted: no finite weight can veto.** `E(e1=0) = 5/(w₁+5) > 0` at every finite w₁, and `tristate = ADMISSIBLE if sk > 0` has no threshold. So a gate is the only instrument. Efficacy: **201 of 201** archived measured-ineffective fixes admitted, Wilson [98.1247%, 100%]. Invariance: **0 of 6** other e1 classes move. 381 targeted tests green.

**Q4 — CC1's claim CONFIRMED on all three counts.** e2 returns 52/55 for the prose document with real bytes *and* with bytes destroyed. I took the one-line argparse-default repair rather than the `argv()` repair, because the latter also requires editing a committed test — and this tree already carries a contradiction between that test and a prior seat's script.

**Q5 — content-hash dedup, not a path predicate.** The conflation inflates Q3's own number by **53.7313%** (309 → 201). Path filtering and content dedup give the identical count, so hashing dominates on robustness-to-renaming at equal accuracy. The path predicate would need **259** edits; relocating harvest moves 182 MB.

**Q6 — settled by calling the fitter.** `a` is a **cumulative** coefficient. But `1.6447` is *also* wrong: it takes a continuous derivative of a discretely-indexed series; the discrete answer is **2.1879** (mpmath, SymPy, scipy.brentq, and Wolfram Language all agreeing to 12 digits). Three larger findings: **two incompatible quantities are both named `gamma`** (0.8776 vs 0.2143 on the same data); **no live module emits `a`**, so the harness cannot evaluate n\* at all; and `(4.89, 0.709)` is **unsourced** — 0 of 421 committed curves reproduce the pair. `rounds = 10` survives as an empirical budget, never as a derivation from n\*.

## Two corrections I owe

I initially reported 3 false rejections of correct fixes in Q2. That was **my own artefact** — I had fabricated a zero ruff baseline. Retracted; the script now calls `_capture_baseline`. And the brief's "73 of 73" is a hardcoded literal in the figures script, not a live count; the live deduplicated count is 201.

## Untested HARD assumptions, named rather than padded over

1. **Q3 invariance on the real archive** rather than 6 synthetic classes. Settled by replaying archived entries through the patched `compute_sk` — needs fix text and baselines the archive does not store.
2. **Q5 near-duplicates** differing by one byte would survive content dedup. Settled by a byte-diff of every harvested copy against its original.

Stopped on diminishing returns at pass 5: pass 4 produced only the Q2 retraction, pass 5 nothing new.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 73 recorded tool call(s).

<!-- verbatim-begin: fable (panel a19_calculator_design_2026-09-30) -->

All deliverables verified reproducible. Final answer.

---

# Verdict: the calculator's affirmative channel already exists in this repository — committed, bidirectionally validated, and wired to nothing. 4 passes run; passes 3–4 produced one new material finding (`.pyc` contamination) then none.

**Deliverables in the sandbox tree** (all executed, all reproducible):

| path | what |
|---|---|
| `experimental_notes/fable_a19_calculator_design_2026-09-30.md` | the design |
| `scripts/a19_affirmative_channel_2026-09-30.py` | Q1–Q4 falsifiers — ALL CHECKS PASS |
| `scripts/n_star_convention_settled_2026-09-30.py` | Q6 falsifiers — ALL CHECKS PASS |
| `bench/reference_runner_v3.py` | PROPOSED `_e1_veto` (Q3) + advisory-basis fields (Q2) |
| `bench/tools/commissioning_arms_2026-09-21.py` | PROPOSED three-state `test_cmd` (Q4) |
| 2 updated tests | old contracts replaced by strictly stronger ones, reasoning in docstrings |

All brief figures re-validated by re-execution before use. All proposals are SUGGESTED to the human.

## Q1 — PRIMARY. Wire the falsifier flip; the flag is a smoke detector being asked to certify the building.

4 mechanisms generated, each falsified. What survives: **per-claim falsifier coverage (M1) + the σ flip g(V_pre,V_post) for fixes (M2), composed** — because my own falsification of M2 **landed by execution**: the metrology *harmful* fix also earns the flip (`pristine=CONFIRMED → harmful=REFUTED` — it repairs the false claim while corrupting the evidence table). So the flip is necessary, never sufficient: **admit only on flip AND veto-clean AND the document's other claims' falsifiers green** — the claim suite is the honest prose `test_cmd`. Executed: flag ON, 0/10 fixes ADMISSIBLE, Wilson [0.00%, 27.75%] (refuse/abstain only, fact 1 confirmed on the corpus); correct-fix flip **5/5** through the runner's own `reverify_falsifier`, Wilson [56.55%, 100%]. **Sufficient for a meaningful test?** Of the veto, yes; of the calculator, no — no run today can produce one affirmative on prose. **Needed:** three wirings (supply, e1-for-prose, prose-e2 := claim suite), no new science. Deliberately NOT half-built here: an addition must arrive with caller and test.

## Q2 — Accuracy = true inputs; meaning = the reader knows what the number CAN say.

Applied: `computed_sk` now travels with `gates_consulted / gates_absent / affirmative_evidence:"none"` (executed, 4 checks PASS; record already reaches the HIL bundle at `:7019`, so it is not an unreached addition). The scalar is never suppressed; a 1.0 now reads as "veto silent, affirmative evidence none" — and becomes fully meaningful when Q1's wiring gives it an evidence-bearing input.

## Q3 — Built as proposed: measured non-cure ⇒ REJECTED, the mean's value still travels.

Executed: FIX_INEFFECTIVE → REJECTED sk=0.0, veto records the would-have-paid 3/5 (5/7 with e2; sympy=Fraction=mpmath); FIX_CURES byte-identical at 1.0; unmeasured still drops from the mean. **344 affected tests pass.** Evidence it improves accuracy rather than merely moving counts: (1) verdicts now agree with the tool measurement of the quantity sk is *defined* to be (before: Mann-Whitney p=0.746836 independence; 73/73 uncured admitted, Wilson [95.00%, 100%]); (2) zero collateral on cures by construction — archive replay over the 136 probe-carrying records is the named pre-ratification measurement; (3) an ineffective fix can no longer move R_k down. Self-falsification: a flaky falsifier wrongly rejects — cost asymmetry (wrong-REJECT returns with feedback; wrong-ADMIT lowered risk 73 times) decides for REJECT; ESCALATE is the softer alternative if the founder wants HIL on every non-cure.

## Q4 — Yes: NO GATE. And CC1's invariance claim is correct but incomplete — my named disagreement.

Verified: no verdict or R_k can move (prose branch forces sk=0.0 regardless of E; the veto reads only e3/e4 `new:` fields — both re-executed). **But** the contaminated "52/55 passed (sandbox)" also reaches the **archived `gate_details` (`:12916`) and the HIL evidence bundle (`:7019`)**, plus ~1.7 GB repo copy + 55 unrelated tests of wall-clock per fix per round. Fix applied: explicit `--test-cmd ""` → `(None, "no test command configured")`, recorded in `_unavailable`; arm1 untouched (executed).

## Q5 — Option (b), namespace separation — and this session added a fourth bite mark.

My own regression run failed with tracebacks pointing at the **real repository**: the staging copy carried **988 `.pyc` files** with real-repo `co_filename`, so `Path(__file__)` in cached test modules resolves outside the sandbox and can import real-repo modules into a panel measurement (executed: `strings` on the `.pyc`; purge; re-run). A shared predicate (a) cannot bind `.gitignore` or `co_filename`; a guard test (c) shares those blind spots; (b) removes the class for every consumer language at once. Immediate one-liner: staging/harvest must exclude `__pycache__`/`*.pyc` — the staging code is not in this tree, so that is a suggestion with evidence, not a patch.

## Q6 — Settled by execution: **both prior numbers are wrong; a IS a cumulative coefficient; rounds=10 survives only as a budget cap.**

The fitter is `bench/decay_analysis.py::fit_duane`: `alpha·n^gamma` fit to `np.cumsum` — fitted N(1)=α (CHK-2), reproduced to 4 dp from its own `rounds_data=[5,3,3,3,2]`. The project runs **two opposite γ conventions** (runner `_estimate_gamma` = 1−β vs decay γ_d=β; CHK-3: 0.2654 vs 0.2583 on the same series). `(a/θ)^(1/γ)`=9.3805 solves a rate law **no fitter in this repo produces** (fails the fitted model's own stopping equation, residual ≫0). The prior correction 1.6447 is **refuted by the fit's own data** — the α=4.8969 series still yields 2 novel/round at round 5. The convention-consistent value is `(aγ/θ)^(1/(1−γ))` = **71.6994** at (4.89, 0.709), **147.4350** at the actual record — SymPy, mpmath, and Wolfram Language (local Wolfram Engine) agreeing to every digit. And the pair (4.89, 0.709) exists in **no single archived fit** (379 swept): mixed provenance. So `rounds=10` cannot be `ceil(n*)` — it survives as what both prior seats' better half already said: novelty-based stop binding, cap as budget backstop that **declares falsification debt** (arm 1 ended *rising* at 9 novel). The recommendation is independent of the coefficient answer — which is why it survives that answer being "both numbers were wrong."

**Not settled by execution and named:** the Q3 archive replay (data in run archives; producer pattern exists), and whether the founder prefers ESCALATE over REJECT for non-cures — a ruling, not a computation.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/a19_calculator_design_2026-09-30/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
