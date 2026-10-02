<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_root_cause_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b4007b9239e608cf3c889effdaeb53e50be60e92fd014f69ba862a54bc8975a7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Falsifier-supply root cause — fable seat, design review 2026-09-30

Every claim below was decided by execution. The executed falsifier for this
note is `scripts/falsifier_supply_fable_2026-09-30.py` (5 checks, ALL PASS at
time of writing; CHK-4 ran RED against the pre-fix tree and GREEN after the
fix, both runs recorded in the panel reply). Wolfram Language (local kernel,
via wolframscript) was run once as the secondary falsifier on the n* values
and agreed with mpmath/sympy to 10 digits.

## Q1 — The root cause, named, and the fix within spec

**Claim (stated so it can be wrong):** the recurring "no runnable falsifier"
failure has one root cause: **falsifier production is coupled to finding
production**. The seat that discovers a claim is also expected to supply the
tool that decides it, with UNTOOLABLE available as a zero-cost exit. Every
recorded surface form reduces to this coupling:

1. Weak finders cannot write falsifiers (Exp-42: weak source models 0/7 on
   the hardest residuals; overnight: prose arm queued 4 of 8 criticals with
   no falsifier at round 0).
2. UNTOOLABLE is accepted from the finder as if it were a property of the
   CLAIM, when 28 of 28 archived UNTOOLABLEs were properties of the FINDER
   (verified against `experimental_notes/CDSFL_MASTER_TASK_LIST.md` §2.2).
3. The directive text that states the obligation does not reach the seats:
   C0040 (severity 0.88, CONFIRMED, PARKED) shows 5 of 5 models receive a
   2,503-char reduced rendering from which "Runnable Falsifiers for Critical
   Findings" is absent.

**It is NOT absent instruction alone** — teaching weak models measured 1/3
against routing's 7/7 (bench/routing.py:14-20). **It is NOT absent
capability** — capability exists and is measured at the higher rungs. **It is
NOT absent machinery** — CHK-3 executed `resolve_via_routing` with the real
decider (`reverify_falsifier`) and showed a strong rung resolving what a
weak rung could not, CONFIRMED at rung 2. The spec already contains the cure
and the measurement that it works. What is missing is that the cure is not
the DEFAULT INVARIANT:

* `RunnerConfig.routing_enabled` defaults **False**
  (reference_runner_v3.py:1442). Preflight forces it only on prose targets
  (:13324). On every other run, an UNTOOLABLE critical goes straight to HIL
  and a human plugs the hole retrospectively — the founder's exact
  inefficiency.
* The one committed, executable proof that a prose claim is decidable by
  runnable code — the STEM fixture corpus — is reachable from 0 live-path
  modules (verified: imported by simulated_bench, 2 tests, 3 A19 scripts;
  by none of reference_runner_v3 / runner_core / immune_agents / registry /
  directives), and no seat-facing directive names the open-by-path pattern
  (grep over bench/directives/ returned nothing).

**Recommendation (design, not applied):**
R1. Make "an unresolved critical is always routed before it is escalated"
    the invariant: `routing_enabled` defaults True whenever
    `falsifier_gate_enabled` is True. One-line default change + preflight
    consistency check. Falsifier: a config with gate on / routing off must
    be refused at preflight the way prose already is.
R2. Treat finder-supplied UNTOOLABLE as a routing INPUT, never a terminal
    verdict (it already is when routing is on; R1 makes that unconditional).
R3. Attach the domain-matched `falsifier_template` from the fixture corpus
    to `_routing_resolve_prompt` as a worked example for the ROUTED rung.
    This is not the refuted "teach the weak finder": the 1/3 measurement was
    weak-rung teaching; this hands a strong writer a starting shape. Honest
    prediction: marginal gain, near-zero cost; measure before keeping
    (additive standard: it must be executed by a test or it is one of the
    11 additions that did nothing).
R4. The overnight evidence itself is partially a simulation artefact: every
    rung of a -SIM ladder is the same stand-in model, so the ladder that
    cures the supply hole is unrehearsable in simulation
    (bench/routing.py:86-91 records ladder order was already unrehearsed).
    Give the sim a scripted strong rung that emits fixture-derived
    falsifiers, so the ladder path is exercised mechanically.

**What would refute me:** a live (non-sim) run with routing enabled, rungs
provably distinct in capability, that still leaves criticals without a
resolved falsifier at the A4 fail-safe — that would show the coupling is not
the root cause and something in the reverify/decider path is. Also: a
measurement showing routed strong rungs fail specifically on prose targets
at a rate comparable to weak finders.

## Q2 — Prose targets; the natural-language-but-computable case

Executed evidence (CHK-1, CHK-2):
* CHK-1: the STRUCTURAL fixture falsifier, decided by the runner's real
  decider, returns CONFIRMED on the pristine document and REFUTED after the
  correct fix. A claim stated wholly in prose was decided by sympy+pint,
  both directions. The founder's "innate intelligence first, tools to
  verify" is not aspiration — it is committed, running code.
* CHK-2: `compute_sk` with `sk_score_prose_listings` off/on. The flag is
  ONE-SIDED by design (reference_runner_v3.py:11624): it convicts a harmful
  fix (REJECTED on a planted bandit HIGH inside a fenced listing) and never
  admits a clean one (NO_SCORE, computed_sk carried for the human). So even
  with A19 on, **closure on prose runs solely through falsifiers** — which
  is why the supply question above IS the prose question.

**The Wolfram connector lesson is already internalised.** What the connector
does — translate natural language into a computation — is exactly what a
panel model does when it writes a falsifier: the LLM is the translator, the
open-source set is the engine. Nothing confines this to natural-language
mathematics: the corpus spans structural, statistics, metrology, algorithms
and numerical analysis, and CHK-1 executed one end of that span. Offering
the connector to users who have Wolfram is an optional secondary channel
under the founder's actual 2026-09-28 ruling (never compelled, secondary
when present), not a capability the project lacks without it.

**The stored-falsifier Wolfram refusal (falsifier_verify.py:596) should
STAND, as an engineering judgement and in my name, not the founder's:**
(a) a stored falsifier must re-run on a machine with no Wolfram — the
refusal is what makes the falsifier corpus portable; (b) falsifiers run in
parallel against 1 licensed serial kernel — admitting Wolfram makes verdicts
timing-dependent; (c) measured cost of the prohibition: 0 of 1,006 archived
falsifier sources mention Wolfram, i.e. zero. A rule with zero cost, two
technical benefits, and one archived incident class (a fake-binary reach was
caught by it) is kept. `.claude/CLAUDE.md` already carries the corrected
attribution as of 2026-09-30 — verified in this sandbox.
**What would refute me:** a claim class demonstrated undecidable by the
open-source set but decidable by Wolfram, appearing in a real target; then
the refusal has a nonzero cost and the trade re-opens.

## Q3 — The round limit: recommend max_rounds = 10, gates remain the stopper

Derivation, all values cross-checked mpmath == sympy == Wolfram:
* March pooled fit (a=4.89, γ=0.709, θ=1): n* = 9.3805 → **ceil = 10**.
* Arm 1's best per-run γ=0.5301 gives n* = **19.9681** (the brief's 19.9645
  does not reproduce from its own inputs; rel. err 1.8e-4 — transcription
  defect, non-material).
* Per-run fits are unusable for setting the limit, and this is demonstrated,
  not judged: fitting arm 1's own novel-per-round [8,2,6,5,4,3,3,9] gives
  n* = 313.6 on rounds 1–7 and n* = 1.64e9 on all 8 (the round-7 surge
  destroys the fit). Sensitivity d ln n*/dγ = −ln(a)/γ²: −5.65 per unit γ
  at 0.5301, −50.3 at 0.1776. The exponent amplifies fit noise beyond use.
* The overnight record shows the limit is the WRONG LEVER for convergence
  failures: arm 1 satisfied both convergence conditions at round 6 and was
  held open only by the A4 fail-safe over unresolved falsifiers. More rounds
  without falsifier supply buy nothing; Q1's fix dominates the choice of N.
* The round-7 surge (novel 3→9 after a budget extension) says novelty is
  budget-coupled, not round-coupled: keep the existing extension mechanism,
  gated on measured last-round novelty ≥ θ, rather than inflating the flat
  ceiling.

**Cost:** worst case +25% dispatches over rounds=8 (5-seat arm: 40→50), paid
only when gates fail to stop earlier. **What would make 10 wrong:** a pooled
fit over ≥2 full cycles with γ materially below 0.5 (pushes n* past 20), or
evidence the round-7 surge reproduces without a budget extension.
**Sampling caveat:** every fitted number here comes from ONE simulated arm's
trajectory; the operationally relevant distribution (live panels, real
seats) is not the one sampled, and the March fit is the only pooled estimate
available. That is why the recommendation leans on the pooled fit and treats
the per-run fits as an instability demonstration only.

## Q4 — This session's defect record; the unfixed defect, now fixed

**The arm-4 e2 inheritance is real, was demonstrated, and is repaired in
this sandbox:**
* Demonstrated (pre-fix): CHK-4 executed arm 4's `argv()` through the
  launcher's own argparse defaults; the omitted `--test-cmd` parsed to the
  immune-memory suite — "excluded" arrived as "inherited and blind".
* Fix: `bench/tools/commissioning_arms_2026-09-21.py::Arm.argv` now always
  emits `--test-cmd`, empty string for an excluded gate; `""` reaches
  `RunnerConfig.test_cmd=""` and `_run_effect_regression` records e2
  unavailable (executed in CHK-4: `score is None`). The sandboxed launcher
  forwards `"$@"` verbatim, so the empty argument survives the bash hop.
* The committed test asserting the defective mechanism
  (`test_the_prose_arm_targets_prose_and_passes_no_test_command`) was
  corrected — reported here as a finding per the falsifier-integrity rule,
  not silently: its docstring stated the right property and its assertion
  enforced the wrong mechanism. 33/33 tests pass post-fix.

**The lesson to carry forward, and it unifies the session:** the constant-e2
gate, the unreachable fixture corpus, and 11 of the 13 confirmed defects
since 2026-08-01 are one class — **machinery that exists but whose output
does not vary with its input** (or that no input reaches). The additive
standard's "executed by a test" clause should be tightened to "executed by a
test that shows the output DIFFERING between a known-good and a known-bad
input". The fixture corpus supplies exactly those pairs, for free, for five
domains. A gate without a discrimination pair is presumed decorative.

## What I did NOT check
* The overnight run data itself (gamma histories, the 46/50 sweep, the
  0.9454... constant): `bench/logs` is blinded in this sandbox except the
  brief; I verified every number that could be recomputed from stated inputs
  (all Wilson intervals, Fisher p, n*) and took the rest on the brief.
* Why arm 1's 2 criticals specifically failed routing overnight (logs
  absent); my R4 sim-artefact explanation is inference from routing.py's
  own -SIM note, not measurement.
* `resolve_via_routing` under a rung that returns a falsifier which times
  out; and the `wolfram_gate` deny-list mechanics.

## Where I could not decide
Whether R3 (templates at the routed rung) will measurably lift confirm
rates: the only teaching measurement on record is weak-rung (1/3), which
neither supports nor refutes strong-rung scaffolding. It is proposed as
measure-before-keep.

## Strongest disagreement with the brief's framing
The brief frames the overnight arms as evidence that the falsifier hole is
open TODAY. But the sim ladder is the same stand-in model at every rung, so
the overnight arms could not have exercised the one mechanism the live spec
provides for closing it. The 0/12 prose sweep is evidence about the
SIMULATION'S ladder, not the project's — and the brief's own Fisher exact
(8.4e-10) therefore overstates what the live system would do. Second, the
brief says the fixture corpus "may already be the answer"; executed, it is
the answer to "is prose falsifiable" (CHK-1) but NOT to "who writes the
falsifier" — reachability would not have saved a weak finder (1/3 measured).
The answer is routing by default; the corpus is the rehearsal material.

— fable seat, 3 falsification passes run (evidence pass; execution pass in
which my own CHK-2 assertion was refuted by the code's designed one-sided
semantics and corrected; integration pass in which the committed arms test
refuted my fix until the test's own defect was established and repaired).
