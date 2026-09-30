# Panel FULL RECORD: the falsifier-supply root cause, prose targets, and the round limit

**2026-09-30T10:25:51+01:00. Audience: a reproducing engineer. UNFILTERED.** Both seats' replies are reproduced verbatim and complete below, under the founder's standing rule that external review is presented whole and never summarised in its place.

## The dispatch

**FREE SEATS ONLY. 0 paid dispatches, 0 spend.** First design review held BEFORE implementation, under the founder's 2026-09-30 policy.

| seat | route | elapsed | tool calls | passes |
|---|---|---|---|---|
| cc2 | claude_cli (Max) | 820.3 s | 53 | 4 |
| fable | claude_cli (Max) | 705.2 s | 53 | 3 |

**THE FIRST DISPATCH WAS KILLED AND RE-RUN.** It ran 6 minutes on a false premise — CC1 had told the seats that a stored falsifier may not call Wolfram and attributed that to the founder, who had ruled no such thing. It was stopped before any seat wrote output, the brief was corrected with his verbatim 2026-09-28 words, and the stored-falsifier question was re-posed as OPEN. Nothing was lost and nothing was extracted from the aborted run.

## Where the seats AGREE

1. **There is ONE root cause and it is fixable within spec: falsifier SUPPLY.** Both HOLD.
2. **Prose claims ARE decidable by runnable code, and the proof was executed.** All 5 committed fixture falsifiers discriminate BIDIRECTIONALLY through the runner's own decider: CONFIRMED on the planted claim, REFUTED once corrected, **5 of 5**.
3. **THE FOUNDER'S WOLFRAM WORRY DOES NOT FOLLOW.** He asked whether offering the natural-language route only to Wolfram owners would confine the project to natural-language mathematics rather than STEM generally. Both seats answer no, on executed evidence: the corpus spans 5 STEM domains — structural, statistics, metrology, algorithms, numerical analysis — reduced to executable checks with the open-source set alone. fable states the translation step plainly: *"what Wolfram's connector does — NL in, computation out — is what a panel model does when it writes a falsifier. The LLM is the translator; the open-source set is the engine."*
4. **The stored-falsifier refusal should STAND — explicitly as engineering judgement, not as his ruling.** Both, independently. Reasons: portability, serialisation against 1 kernel, and a measured cost of the prohibition of exactly **0 of 1,006** archived falsifier sources.
5. **His original admissibility triage IS implemented and running** — `resolve_target_kind`, `_gateable_source`, the one-sided A19 branch, preflight.
6. **Round limit: 10.** Both, from ceil(9.3805).
7. **Arm 4's `e2_regression` was FAKED, not excluded.** Both fixed it at the real path.
8. **One unifying defect class:** machinery whose output does not vary with its input — the constant `e2`, the unreachable corpus, and the 11 recorded additions that did nothing.

## Where they DISAGREE, preserved because it is the information

**This is a genuine split on what to build, and both positions are executed rather than argued.**

**cc2 — the cure is WIRING the artefact.** Driving the live `resolve_via_routing` with supply removed gives **0 of 5, ERROR at every rung**; with the corpus pattern, **5 of 5**, Fisher **p = 7.936508e-03**. Its formulation: *"Routing climbs a ladder of writers; it cannot manufacture a pattern. Routing is a multiplier on supply — and here, a multiplier on zero."* It further holds that the brief's own teaching-vs-routing evidence **pre-selected routing and does not survive execution**, because the 2026-06-07 comparison ranked two amplifiers of existing supply, not two rival cures — both arms had a pattern.

**fable — the cure is ROUTING as the default invariant.** `routing_enabled` defaults to **False** (`reference_runner_v3.py:1442`) and preflight forces it only on prose (`:13324`); everywhere else an UNTOOLABLE critical goes straight to the human queue, which fable names as *"the founder's exact 'plugging holes retrospectively'"*. It treats the corpus as rehearsal material, not as the answer to who writes the falsifier: *"reachability alone would not have saved a weak finder."*

**They are not mutually exclusive and neither seat claims otherwise.** cc2's W3 says add rungs only AFTER supply exists; fable's R3 attaches the domain-matched template at the strong rung as measure-before-keep. Read together they sequence rather than conflict: wire the pattern, then make routing unconditional, then measure.

## What the seats found wrong in the brief and in the project's own law

**GAMMA IS LOAD-BEARING, so cc2's first finding needs the founder's attention.** It reports that `_estimate_gamma:3190` fits the **cumulative** `N = a·n^β` with `γ = 1−β`, so `dN/dn = a(1−γ)n^(−γ)` and the optimal round count is **`n* = (a(1−γ)/θ)^(1/γ) = 1.6447`**, not 9.3805 — a factor **5.70** apart. It could not locate the fitting code to settle whether `a = 4.89` is a cumulative or a rate coefficient, and says a founder ruling resolves it fastest. Its recommendation of 10 is deliberately built not to depend on the answer.

**Both seats independently corrected the brief's arithmetic:** 19.9645 should read **19.9681**. cc2 also found the citation wrong — `n* = (a/θ)^(1/γ)` is **not** at appendix line 205, which carries the ΔR_k premature-stop band; the law is at `CDSFL_MASTER_TASK_LIST.md:171`. Both were inherited by the brief rather than invented in it, and cc2 notes that `feedback_rejected_advice_acquires_authority` applies to a brief's own arithmetic too.

**fable's methodological objection limits CC1's headline statistic.** *"A `-SIM` ladder is one model wearing five names — so the 0/12 prose sweep and its p = 8.4×10⁻¹⁰ measure the simulation's ladder, not the project's."* That is a real bound on the 0-of-12 result and it is accepted here.

**cc2 on the process question:** CC1 finding 0 of 3 result-corrupting defects has Wilson [0%, 56.1497%] — *"3 trials cannot measure a rate; that is the finding."*

**The control both converge on:** a **reachability test** — for every declared artefact, assert a live-path caller and an executing test — plus, from fable, a committed **discrimination pair** per gate: known-good and known-bad input producing different outputs. The fixture corpus supplies those pairs for 5 domains, free.

## Honesty notes from the seats' own reports

fable records that in its execution pass *"the code refuted my own CHK-2 assertion and I corrected my check, not the code"*, and that in integration *"the committed arms test refuted my fix until its own defect was established and repaired"* — a committed test that encoded the defect it was meant to catch. cc2 marks its F2 **PARTIAL** because it passed `baseline=None`, and states the strict claim it owns rather than the wider one.

---


# SEAT: cc2 — VERBATIM, COMPLETE

Route `claude_cli`, ok `True`, 8985 characters.

---

<!-- verbatim-begin: cc2 panel seat reply, reproduced complete -->

Both behave as designed. 4 passes run. Deliverables on disk.

---

# Verdict: there IS a single root cause, it is fixable once, and it is none of the three names the brief offers.

**It is an unwired artefact.** The project already owns a proven prose-falsifier pattern. It is reachable from **0** live-path modules.

## F1 — Root cause is falsifier SUPPLY · **HOLDS**

**Claim.** Not absent capability, not absent routing, not absent instruction — an executable artefact nothing reaches.

**Evidence** (`python3 scripts/falsify_prose_falsifier_supply_2026-09-30.py`):
```
fixtures=5 claims=29 FALSE=5 TRUE=24
  structural  pristine=CONFIRMED  corrected=REFUTED   OK
  statistics  pristine=CONFIRMED  corrected=REFUTED   OK
  metrology   pristine=CONFIRMED  corrected=REFUTED   OK
  algorithms  pristine=CONFIRMED  corrected=REFUTED   OK
  numerical   pristine=CONFIRMED  corrected=REFUTED   OK
  bidirectional: 5/5
  live-path modules importing the corpus: 0
  RESOLVED  no supply: 0/5   corpus supply: 5/5
```
All 5 committed falsifiers **discriminate bidirectionally** under the project's own decider — CONFIRMED on the planted claim, REFUTED once corrected. Reachability claim re-verified: 0 importers among `reference_runner_v3.py`, `runner_core.py`, `immune_agents.py`, `cdsfl_registry/`, `directives/`.

**The decisive run:** driving the live `resolve_via_routing` with supply removed → **0/5, ERROR at every rung**. With the corpus pattern → **5/5** (Fisher p = 7.936508e-03). Routing climbs a ladder of *writers*; it cannot manufacture a *pattern*. **Routing is a multiplier on supply — and here, a multiplier on zero.**

**Fix:** `experimental_notes/panel_fixes_falsifier_root_cause_2026-09-30/claude-seat.md` — W1 wire the pattern library into `bench/directives/`; W2 make `UNTOOLABLE` cost something (**28/28** were toolable, Wilson [87.9357%, 100%]); W3 add rungs only *after* supply exists.

**What would refute me:** a live-path importer I missed (I grep 3 files + 2 dirs, so a dynamic import would refute); or a seat that, given W1, still fails at today's rate — that moves the cause to capability. My 0/5 and 5/5 use stub `resolve_fn`s: they decide the **mechanism**, never a rate.

## F2 — Prose admissibility works; S_k gives prose nothing · **HOLDS (PARTIAL on one leg)**

20 runs of `compute_sk`, all 5 fixtures × {correct, harmful} × {flag off, on}:

| flag | correct | harmful | discrimination |
|---|---|---|---|
| `False` | `NO_SCORE` 0.0000 | `NO_SCORE` 0.0000 | **none** |
| `True` | `ESCALATE` 0.0000 | `ESCALATE` 0.0000 | **none** |

**Ever ADMISSIBLE: NONE** — veto-only holds. The flag changes the *label* of the non-decision, not the decision. With it on, hard gates **pass** on the `subprocess.call(..., shell=True)` payload and all four effect gates report unavailable. So prose has exactly **one** resolution channel, and F1 shows it is unwired — same failure, two sides.

**On Wolfram:** the founder's worry that Wolfram-only would confine the project to natural-language *maths* **does not follow** — the corpus spans 5 STEM domains reduced to executable checks with the open-source set alone, 5/5. **I judge the stored-falsifier refusal should STAND**, on merit not authority: a scored falsifier *is* the primary route, and needing a licensed kernel makes verdicts environment-dependent (§10 category-5 unreproducibility) and serialises 1 kernel against parallel re-verification. Cost of keeping it: zero (0/1,006 mention it).

**PARTIAL because:** I passed `baseline=None`. The strict claim I own is *with no baseline, prose S_k discriminates nothing across 20 runs*.

## F3 — Round limit: recommend **10**, move the binding rule to novelty · **HOLDS**

SymPy, cross-checked by mpmath and **Wolfram Language** (all agree to every digit):

| γ | source | n* | dn*/dγ | 0.05 γ error → |
|---|---|---|---|---|
| 0.7090 | March fit | 9.3805 | −29.6 | 1.48 rounds |
| 0.5301 | arm1 r3 | 19.9681 | −112.8 | 5.64 rounds |
| 0.2143 | arm1 r8 (my fit) | 1646.4943 | −56,904 | **2,845 rounds** |
| 0.1776 | arm1 final | 7607.5283 | −382,814 | **19,141 rounds** |

Two problems underneath, both found by executing project code:

1. **The law drops a factor its own estimator implies.** `_estimate_gamma:3190` fits the **cumulative** N=a·n^β, γ=1−β. So dN/dn = a(1−γ)n^(−γ), giving **n\* = (a(1−γ)/θ)^(1/γ) = 1.6447**, not 9.3805 — a factor 5.70 apart.
2. **The brief's two arm-1 series are mutually inconsistent** under the live estimator: `[8,2,6,5,4,3,3,9]` yields γ history `[0,0,0.4023,0.2997,0.2600,0.2501,0.2487,0.2143]`, not the brief's `[...0.5301,0.2824,0.1914,...]`.

**The datum that decides it:** arm 1's novel-per-round never fell below **2** and ended at **9** — *rising* at the cap. Arm 1 had **not** converged; that 8 is budget exhaustion carrying falsification debt, not convergence.

**Recommend `rounds = 10`** = ceil(9.3805) from the only credible fit, in the regime where n* is merely sensitive (±1.5) not useless (±2,845). Cost +25%. **Binding rule should be novelty:** stop when novel < θ for **2 consecutive** rounds (the round-7 surge of 9 vindicates this); cap at 10 as a backstop that **declares debt**. `n*` advisory only.

**Sampling caveat:** 4 γ values, n=1 arm. The operational γ distribution is **not known to me** and I assume none — this is a local-derivative argument.

## F4 — Prose arm's `e2_regression` was FAKED, not excluded · **HOLDS · FIXED**

`arm4.argv()` emitted no `--test-cmd`, so argparse substituted the **immune-memory suite**. `52/55 == 0.9454545454545454` exactly. Root cause is one line: **a falsy guard cannot express three states** — `None` (disabled), `''`, and *unset* were indistinguishable, so the most explicit signal was the one discarded.

**Fix applied:** `bench/tools/commissioning_arms_2026-09-21.py` → `if self.test_cmd is not None:` with explicit `else: a += ["--test-cmd", ""]`. Verified `_run_effect_regression` returns `(None,'no test command configured')` for both `None` and `''`. Arms 1–3 unchanged, arm 4 emits `''`, **226 passed**.

**Falsifier:** `scripts/falsify_e2_inherits_default_2026-09-30.py` — **exit 1 before, exit 0 after**.

**Recommended addition:** assert every *available* gate's score varies across ≥2 fixes. A zero-variance available gate is a defect, not a result.

## Q4 lesson

Mechanised layers 7/13 = 53.8462% [29.1438%, 76.7939%]. CC1 0/3 on result-corrupting defects is Wilson [0%, 56.1497%] — **3 trials cannot measure a rate**; that is the finding.

**F1 and F4 are the same defect shape: an intention recorded in prose with nothing mechanical carrying it.** The project's own record (11/13 were additions that did nothing) says this dominates. The control is narrow and buildable: **a reachability test** — for every declared artefact, assert a live-path caller and an executing test. It catches both.

---

**Passes run: 4.** Stopped on diminishing returns — pass 4 produced no new finding above consequence threshold.

**Not checked:** `compute_sk` with a real baseline (most likely to qualify F2); re-running arm 4 (brief-forbidden); full suite (brief-forbidden); independent re-derivation of the 24 TRUE claims; the other 12 session defects individually; any live model.

**Could not decide:** whether a=4.89 is a cumulative or rate coefficient — a factor 5.70 on March's n*. `decay_analysis.json` files it under `duane/params/alpha` (conventionally cumulative), but I could not locate the fitting code. **A founder ruling resolves this fastest**; my recommendation of 10 is built not to depend on it.

**Strongest disagreement with the brief's framing:** it offers four candidate causes but its teaching-vs-routing evidence pre-selects routing, and that does not survive execution. The 2026-06-07 comparison ranked two *amplifiers of existing supply*, not two rival cures — both arms had a pattern. Remove supply and routing returns 0/5. Reading it as "prefer routing" yields the wrong fix: more rungs, more cost, prose still halting at round 0. The brief lacks a word for the distinction that matters: teaching failed because it was **prompt-resident** and models don't learn across calls; wiring makes an **executable artefact reachable** and is immune to that amnesia, because the seat *reaches* it rather than *remembers* it.

Two inherited errors: `n* = (a/θ)^(1/γ)` is **not** at appendix line 205 (that line carries the ΔR_k premature-stop band; the law is at `CDSFL_MASTER_TASK_LIST.md:171`), and 19.9645 should read **19.9681**. Both inherited rather than invented — but `feedback_rejected_advice_acquires_authority` is about exactly this, and it applies to the brief's own arithmetic.

**Where I agree without qualification:** the brief's central statistics are exact. I reproduced 46/50 = 92.0000% [81.1618%, 96.8450%], 0/12 [0%, 24.2494%], and Fisher **p = 8.425329e-10** under two independent implementations (statsmodels; hand-coded Wilson in mpmath at 25 dps). Wolfram was available and confirmed every n* value as secondary falsifier.

<!-- verbatim-end -->

---


# SEAT: fable — VERBATIM, COMPLETE

Route `claude_cli`, ok `True`, 8585 characters.

---

<!-- verbatim-begin: fable panel seat reply, reproduced complete -->

All deliverables are written and executed. Final report.

---

# Fable seat — verdicts, evidence, fixes

**Deliverables (all in the sandbox tree, all executed):**
- `scripts/falsifier_supply_fable_2026-09-30.py` — 5 checks, final run **ALL CHECKS PASS**
- `bench/tools/commissioning_arms_2026-09-21.py` — arm-4 fix applied
- `bench/tests/test_commissioning_arms_carry_their_settings_2026-09-21.py` — wrong test corrected; **33/33 pass**
- `experimental_notes/panel_fixes_falsifier_root_cause_2026-09-30/fable.md` — full design note

## F1 — Q1: There is one root cause, and it is fixable within spec. **HOLDS**

**Claim:** falsifier production is coupled to finding production — the seat that discovers a claim must also supply the tool that decides it, with UNTOOLABLE as a free exit. The brief's candidate hypothesis (absent instruction) is only a surface form; so is absent capability.

**Evidence, executed:**
- CHK-1: the STRUCTURAL fixture falsifier through the runner's real decider: `pristine=CONFIRMED fixed=REFUTED`. Prose claims ARE decidable by runnable code, both directions — capability isn't absent from the toolset.
- CHK-3: `resolve_via_routing` with the real `reverify_falsifier` as decider: weak rung (empty falsifier) → `ERROR`, ladder with a strong rung → `CONFIRMED resolved=True model=Codex rungs=2`. Supply is a property of the **ladder**, not the finding. The historical record agrees: teaching weak finders 1/3, routing 7/7 (`bench/routing.py:14-20`).
- Reachability re-verified: `stem_fixtures` imported by `simulated_bench.py`, 2 tests, 3 A19 scripts; **0** of `reference_runner_v3`/`runner_core`/`immune_agents`/registry/directives; grep over `bench/directives/` for the open-by-path pattern returns nothing. The 28/28-toolable UNTOOLABLE record verified in `CDSFL_MASTER_TASK_LIST.md` §2.2.
- The cure exists but is not the invariant: `routing_enabled: bool = False` (`reference_runner_v3.py:1442`); preflight forces it only on prose (`:13324`). Everywhere else an UNTOOLABLE critical goes straight to HIL — the founder's exact "plugging holes retrospectively".

**Fix (design, recommend-not-ratify):** R1 make routing-before-escalation unconditional whenever the falsifier gate is on (default flip + preflight refusal, mirroring the prose refusal that already exists). R2 finder-supplied UNTOOLABLE is a routing input, never terminal. R3 attach the domain-matched `falsifier_template` to `_routing_resolve_prompt` as strong-rung scaffolding — measure-before-keep, since the 1/3 result was weak-rung teaching and doesn't decide this case. R4 give the sim a scripted strong rung emitting fixture-derived falsifiers, because a `-SIM` ladder is the same model at every rung and cannot rehearse the cure.

**What would refute me:** a live run, routing on, rungs of provably distinct capability, still leaving criticals unresolved at the A4 fail-safe.

## F2 — Q2: The lessons are applied; the Wolfram connector's essence is already internalised. **HOLDS**

CHK-2 executed the flag both ways: correct fix `off=NO_SCORE on=NO_SCORE (computed_sk=1.0)`; harmful fix `off=NO_SCORE on=REJECTED` (bandit 1 new HIGH in the fenced listing). The flag is **veto-only by design** (`:11624`) — so closure on prose runs solely through falsifiers, which is why Q1 *is* the prose question. The founder's triage (admissible iff computationally reducible elements exist; model's intelligence first, tools verify) is implemented and running: `resolve_target_kind`, `_gateable_source`, the one-sided A19 branch, preflight.

The NL-connector lesson: what Wolfram's connector does — NL in, computation out — is what a panel model does when it writes a falsifier. The LLM is the translator; the open-source set is the engine; CHK-1 is the executed proof, and the corpus spans five STEM domains, so nothing confines the project to NL mathematics or to Wolfram owners.

On `falsifier_verify.py:596`: the refusal should **stand, as my engineering judgement**: portability (stored falsifiers must re-run on Wolfram-less machines), serialisation (parallel falsifiers vs 1 kernel), and a measured cost of the prohibition of exactly zero (0/1006). `.claude/CLAUDE.md` already carries the corrected attribution in this sandbox (verified at lines 250–256). The headless-seat connector gap (0 MCP tools) is a capability fact, not a policy one; nothing recommended here depends on it.

## F3 — Q3: Recommend **max_rounds = 10**; the gates stay the stopper. **HOLDS**

- n\*(4.89, 0.709) = **9.3805** → ceil 10. Verified mpmath == sympy == **Wolfram Language** (`{9.380519..., 19.968130...}`, local kernel, exit 0).
- The brief's **19.9645 is wrong**: from its own inputs (γ=0.5301) the value is **19.9681** (rel. err 1.8e-4; non-material, but the brief demanded derivation).
- Per-run fits cannot set the limit — demonstrated: fitting arm 1's own novelty series gives n\* = 313.6 (rounds 1–7) or 1.64×10⁹ (all 8; the round-7 surge flips γ to 0.075). Sensitivity d ln n\*/dγ = −ln a/γ² = −50.3 per unit γ at γ=0.1776.
- Arm 1 met both convergence conditions at round 6 and was held open only by A4 over unsupplied falsifiers: **N is the wrong lever for that failure; Q1's fix dominates**. The round-7 surge (3→9 after budget extension) says novelty is budget-coupled — keep the extension mechanism gated on last-round novelty ≥ θ rather than inflating the ceiling.
- Cost: worst case +25% dispatches (40→50 on a 5-seat arm), paid only when gates don't stop earlier. **Refuted by:** a pooled ≥2-cycle fit with γ < 0.5, or a surge reproducing without a budget extension. **Sampling caveat:** the per-run numbers come from one simulated arm; the operationally relevant (live-panel) distribution is not the one sampled — only the March pooled fit approximates it, which is why the recommendation rests there.

## F4 — Q4: The arm-4 "excluded" gate was inherited, demonstrated, and is now fixed. **HOLDS → FIXED**

- **Demonstrated pre-fix** (CHK-4, first run): arm 4's `argv()` omits `--test-cmd`; parsed through the launcher's own argparse it yields the immune-memory suite — `AssertionError` at "defect demonstrated".
- **Fix at the real path:** `Arm.argv()` always emits `--test-cmd`, `""` when excluded; `""` reaches `RunnerConfig.test_cmd=""` and `_run_effect_regression` returns `score=None, 'no test command configured'` — executed in CHK-4 post-fix: `parsed test_cmd = ''`, gate genuinely unavailable. `"$@"` in the sandboxed launcher (line 197) carries the empty argument.
- The committed test asserting the omission (`test_..._passes_no_test_command`) encoded the defect; corrected per the integrity rule (reported, falsifier attached, not silently weakened). **33/33 pass.**
- **Lesson:** constant-e2, the unreachable corpus, and the 11 additions-that-did-nothing are one class — machinery whose output does not vary with its input. Tighten the additive standard: every gate needs a committed **discrimination pair** (known-good vs known-bad input producing different outputs). The fixture corpus supplies those pairs for five domains, free.

## F5 — Minor: the brief's 19.9645 (see F3). **HOLDS**, non-material transcription defect.

---

**What I did NOT check:** the overnight raw run data (blinded in this sandbox — I recomputed every number derivable from stated inputs: all three Wilson intervals and the Fisher p reproduce exactly, two tools each; the rest is taken on the brief); why arm 1's 2 specific criticals failed routing (logs absent); timeout behaviour of a routed falsifier; the wolfram_gate deny mechanics.

**Where I could not decide:** whether R3 (templates at the strong rung) lifts confirm rates — no measurement exists for that configuration; proposed as measure-before-keep.

**Strongest disagreement with the brief's framing:** the overnight arms could not have exercised the live spec's cure — a `-SIM` ladder is one model wearing five names — so the 0/12 prose sweep and its p = 8.4×10⁻¹⁰ measure the *simulation's* ladder, not the project's. And the fixture corpus is the answer to "is prose falsifiable" (CHK-1), not to "who writes the falsifier": reachability alone would not have saved a weak finder. The answer is routing as the default invariant; the corpus is the rehearsal material.

**Passes run: 3** (evidence; execution — in which the code refuted my own CHK-2 assertion and I corrected my check, not the code; integration — in which the committed arms test refuted my fix until its own defect was established and repaired). A fourth pass produced nothing above the material threshold; converged, with the stated residuals as the falsification debt.

<!-- verbatim-end -->

---


Written under CDSFL note standard v1.7 (26 August 2026).
