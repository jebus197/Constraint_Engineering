# Blind Panel on the Adaptive Distributed-Compute Spec: 6 Defects, 2 of Them Mine, 4 of Them Not

**2026-09-29, 14:24 BST.** Audience: a reproducing engineer. Plain-English companion at `~/Desktop/CDSFL_tts/Panel_Blind_Adaptive_Spec_2026-09-29.txt`.

**Run:** `bench/logs/adaptive_spec_blind_2026-09-29/`. Free seats only (`FREE_SEATS = {cc2, fable}`), `PANEL_ONLY` empty, **£0 spent**. `fable`: 24 tool calls, 649.7s, 12,714 chars. `cc2`: 32 tool calls, 887.5s, 14,343 chars, **4 passes**, terminating when pass 5 produced nothing above threshold.

**Containment held.** Per-seat sandboxes, no `.git`; each seat created exactly the files the brief named and nothing else (fable 2, cc2 3). Nothing touched the canonical tree.

---

## 1. Design of the round, and an honest limit on its blindness

The brief was written to the locked template (`bench/directives/universal/panel_brief_template.md`) after the validator **refused** the first draft for lacking a named instrument, a fix requirement, a delivery path and a termination criterion.

**Anti-anchor check, measured:** the words `conditional`, `expectation`, `nu_eff`, `inversion`, `understate` and `7.96` occur **0 times** in the brief. It named `sigma`, `nu` and `S_k` as instruments and told the seats to *call* `compute_rk` and the spec's §6.1 form and compare outputs — generic `execute-do-not-grep` practice, not a hint.

**The blindness was not total, and fable said so unprompted:** *"canonical commit `ea43d3f` (today) contains the founder's own assessment of this spec. I used the canonical git history for dates only and did not read that assessment."* A seat with repository access can see that an assessment exists. Recorded rather than glossed.

---

## 2. What the panel found that CC1 did not

CC1's prior assessment carried **2** findings. The panel returned **6**, independently reproducing both of CC1's and adding four.

| # | Finding | fable | cc2 | CC1 |
|---|---|:-:|:-:|:-:|
| F1 | §6.1's free `ν̂` cannot reproduce `compute_rk`'s `σ`-coupled `nu_eff` | ✓ | ✓ | ✓ |
| F2 | "zero credit" for a gate-failed candidate is **negative** credit | ✓ | ✓ | — |
| F3 | the routing estimator ranks on the conditional blend, not the expectation | ✓ | ✓ | ✓ |
| F4 | §6.5's additive objective double-counts, and the bias is **two-signed** | — | ✓ | — |
| F5 | §6.4's exploration term is 0 at `N_u=0`; the score is unit-dependent | ✓(a) | ✓(a,b) | — |
| F6 | `n=3` detects only enormous effects; 2 of 4 promotion gates unevaluable | ✓ | ✓ | — |

**F2, verified by CC1 against the shipped functions:** `compute_rk(0.5, 0.3, sk=0.0)` → `0.6200`, credit **−0.1200**; `apply_sk_to_rk(0.5, SK_NO_SCORE)` → `0.5000`, credit **exactly 0**. The spec's §6.1 treats a gate-failed candidate as zero credit, so a scheduler would **under-penalise configurations whose fixes fail gates and over-dispatch them**. cc2 sharpens it: the spec never links `σ̂` to `S_k`, so a candidate whose gate product will be 0 can carry `σ̂ = 0.9` and win the dispatch — *"the hard qualification boundary has no formal expression in the score."*

**F4, cc2 alone, verified by CC1 on two engines.** Summing per-configuration gains on the same unit is wrong because the update composes multiplicatively in the odds: SymPy gives `T(T(R,q₁),q₂) − T(R, q_eff) = 0` exactly. The additive gap is **two-signed** — at `R = 1/2` it overstates, at `R = 9/10` it understates. z3: **unsat** that any `R ≤ 1/2` fails to overstate; **sat** that it understates somewhere. The sign boundary `R* = (1−√(1−q_eff))/q_eff` has limits **1/2 → 1**, so **`RK0_PI_BASE = 0.5` sits exactly at its floor.** A two-signed bias is worse than a one-signed one: it cannot be treated as a conservative bound. **cc2 refuted its own first version of this mid-run** — it claimed the sum always overstates, Wolfram returned `False`, and it repaired the claim by deriving the boundary.

---

## 3. Three measurements of one quantity, and why the disagreement is the finding

All three analyses measured how often the spec's estimator ranks two candidates the wrong way, and got three different answers:

| source | rate | interval | sampling |
|---|---:|---|---|
| CC1 | 7.9567% | [7.7428%, 8.1759%] | uniform on `(R,q,σ,ν)` |
| fable | 3.09% | [2.86%, 3.34%] | uniform on `(R,q,σ)²` |
| cc2 | 2.3654% | [2.2513%, 2.4851%] | grid `q,σ ∈ {0.05..0.95}`, `R = 0.5` |

**Every one of the three stated, unprompted, that the number is a property of its own prior and that the operational distribution is unknown.** cc2: *"Whether F3's 2.37% is 0% or 40% in practice is undecided, and I decline to let my flat prior stand in for it. F3's existence is derived; its rate is not."*

**The convergence is on the caveat, not the number.** Three independent samplings spanning a factor of 3.4 is direct evidence that this rate is not a stable quantity and must not be quoted as one. The existence of the defect is algebraic and certain. How often it bites in practice cannot be computed from the current archive at all: it would need the joint distribution of `(R, q, σ, ν)` across live runs, and **no archived run records those 4 together**.

---

## 4. The most valuable thing the round produced, and it contradicts CC1's framing

cc2's stated disagreement with the brief:

> *"The brief directs me to check whether §6.1's transcription matches `compute_rk` — and it does not, which is F1. But that framing understates the problem by treating the canonical model as a fixed target. `git log` shows the appendix changed **7 times in the 15 days after the spec was written**, twice on the exact quantity §6.1 transcribes. So F3 is not a transcription error at all: the spec transcribed correctly and the canon moved."*

**CC1 framed the spec as stale. cc2 reframes it as a missing mechanism**, which generalises: *"a layer that declares it 'CONSUMES the canonical mathematics without redefining it' has silently taken on the canon's revision rate as a dependency, and neither document names the mechanism that would catch it."*

Its proposed remedy is one line in §6.1 — **pin the consumed appendix by commit hash and execute the transcription against `compute_rk` in CI, so the next appendix revision breaks a test instead of quietly invalidating a scheduler.** cc2: *"I would rather the founder buy that line than any of my other five fixes."*

**This applies beyond the spec.** Anything in or around this repository that consumes the canonical model by reference has the same unguarded dependency.

---

## 5. What the seats recorded as SOUND

Required by the brief, because a round returning only complaints has been obliging rather than sceptical. cc2 recorded six, including: §6.2's arithmetic exact in rationals; §6.3's refusal to manufacture a scalar correlation correction, matching the appendix's own Ising branch; §6.6 honestly hedged; §10's ruling on `_load_balancer.py` correct and consistent with the additive standard; and **§12 as the best part of the document**, its rule 2 conceding the scheduler in advance if the flat panel is not beaten at matched budget. cc2 also **implemented three of the compiler's five obligations to confirm they are buildable** — Kahn's algorithm separates a DAG from a cycle, dangling dependencies are set membership, interface ownership is an arity check — concluding it is *"a specification for three fifths and a wish for two fifths — a scoping problem, not a fatal one."*

---

## 6. Deliverables, executed

Both seats delivered fixes as files at real paths and both falsifiers were re-executed by CC1 from the harvest:

- `sandbox_harvest/fable/attempt-1/files/scripts/panel_adaptive_spec_falsifiers_2026-09-29.py` → **ALL DEMONSTRATIONS REPRODUCED (exit 0)**
- `sandbox_harvest/cc2/attempt-1/files/scripts/adaptive_spec_falsifiers_2026-09-29.py` → defects present in checks 1,2,3,4,5,6,8,9; **check 7 is a control and correctly held sound**
- fable's 6 fixes: `sandbox_harvest/fable/attempt-1/files/experimental_notes/panel_fixes_adaptive_spec_2026-09-29/fable.md`
- cc2's 6 fixes, 447 lines: `.../cc2/attempt-1/files/experimental_notes/panel_fixes_adaptive_spec_2026-09-29/opus-blind-seat.md`
- cc2 also proposed an **additive** entry to `docs/MATHEMATICAL_APPENDIX.md:270` — extending the existing A-vs-M correction from reading *one* cycle to *ranking several*, with an explicit statement of what it does not license (it is **not** an argument for feeding `M` to the convergence gate).

**Nothing has been applied.** Under `feedback_fixes_hil_only` fixes are suggested to the founder, never auto-applied.

---

## 7. Disposition — where both seats landed

Both independently reached the same placement, and it matches CC1's:

- **fable:** *"Phase B (substrate) only, and it does not earn a paid experiment until §6.1 and §6.4 are repaired."*
- **cc2:** *"sound enough for the runway, at Phase B ... It earns a paid experiment — Phase D, not Phase E."*

Neither correction sits on the simulated shakedown's execution path: the transitive import closure of the launch path reaches 60 modules and **0** references to either component.

**For the founder:** whether to adopt cc2's one-line CI pin (§4), which is the cheapest and most generalisable of the eleven fixes offered; and whether the six spec fixes are applied before or after the shakedown.
