# The severity panel has reported

11 November 2026, 19:31 GMT. Round `severity_is_ordinal_2026-11-11`, blind, 2 free seats (`cc2`, `fable`), 0 paid. 2 of 2 responded: cc2 38,458 chars over 1,361 s, fable over 1,026 s. Dispatched only after the joint round `tonights_build_review_b22_b88_b105_2026-11-10_joint` cleared the outstanding topology debt.

## Verdict matrix

| | Position | cc2 | fable |
|---|---|---|---|
| P1 | definition stands (`cdsfl_core_formal.md`) | AGREE | AGREE |
| P2 | severity is ORDINAL | AGREE **+1 repair** | AGREE **+2 corrections** |
| P3 | domain-supplied scales | AGREE | AGREE **+2 defects** |
| P4 | model asserts existence + order only | **REFUTE AS STATED** | AGREE |
| P5 | consequence is a property of the application | AGREE | AGREE |
| P6 | §7.7 is a *good* credence formula | AGREE | **REFUTE** |
| P7 | `ΔV = Σ V(f)` → order statistic | AGREE on maths, **REFUTE urgency** | AGREE, measured |
| P8 | several scales per domain | AGREE | AGREE |
| P9 | scale selection is routing | AGREE | AGREE |
| P10 | `v_bar` is mean severity, 4 ways | **REFUTE — premise wrong** | **REFUTE AS STATED** |

7 of 10 carry both seats. The 2 genuine inter-seat disagreements are P4 and P6. P10 is refuted by both, independently.

## The most consequential finding: an order does not determine a cut

cc2's P4 refutation: *"Existence + order is not enough to support a gate. The model must assert existence + order + a distinguished level."*

Measured by that seat: `count ≥ cut` commutes with **0 of 6** relabellings when the cut is **transported** by the same monotone map, and breaks on **5 of 6** when the cut is **held fixed**. `CRITICAL_SEVERITY_THRESHOLD = 0.7` holds it fixed.

This is the single item most deserving a ruling: it says the model needs one thing more than the brief claimed, and the seats split on it.

## Both seats refuted P10, and they are right — my report to the founder was wrong

I told the founder on 2026-11-11 that `v_bar` is the mean severity of findings, computed 4 ways. Verified directly against the tree:

| site | what `v_bar` means |
|---|---|
| [run_exp19_fff.py:327](../bench/run_exp19_fff.py) | *"v_bar (mean severity): average severity of genuine findings"*; `:339` computes `sum(f.severity)/len(findings)` |
| [dm/_manager.py:644](../bench/dm/_manager.py) | *"v_bar: proportion of findings with verified=True"*; `:645` names mean severity as the **separate** axis `A`; `:719` computes `verified/len`, `:722` computes the severity mean into `obs_a` |
| [dm/_types.py:331](../bench/dm/_types.py) | `v_bar: float  # Mean verification quality` |

**So it is not 4 formulas for 1 quantity. It is 2 different quantities in 1 slot of 1 type**, depending on which runner filled it — `run_exp19_fff.py` imports `CapabilityFingerprint` ([:54](../bench/run_exp19_fff.py)) and writes mean severity where the type documents verification quality. That is a type-level confusion, strictly worse than the naming clash I reported.

## The median is not admissible, and the brief's instrument could not have seen it

Found independently by both seats, each verifying on SymPy **and** Wolfram Language (local Engine, exit 0).

`statistics.median` averages the 2 middle order statistics at even n, and averaging is the forbidden operation. cc2's counterexample on levels `{1,2,3,4}` under `φ(t)=t²`: `φ(median) = 25/4`, `median(φ) = 13/2`. fable's on `{1/4, 3/4}`: `median(φ(x)) = 5/16 ≠ φ(median(x)) = 1/4`.

**Why §3.7's sweep reported it invariant:** its sample ranks `{5,4,2,2,1,1}` sort to `[1,1,2,2,4,5]` — the 2 middle values are **tied at 2**, so the interpolation returned 2 either way and averaging was never exercised. A *selected* order statistic (lower/upper middle) fails 0 of 6. The brief's §3.7 caveat invited exactly this and it arrived.

## Other findings

- **Pure mathematics has no recognised consequence scale.** Both seats, independently, pointing at §5's own table: every other row names an external standard (FMEA, CTCAE, CVSS, INES); the mathematics row names *"result-validity 1–5"*, which exists nowhere outside the brief. cc2 proposes `{void, valid}`; fable proposes an order-only judgement against `cdsfl_core_formal.md` §10's 5 material-defect categories plus a human flag. Neither invents a numbering.
- **At least 3 magnitude-arithmetic sites beyond the census's 4**: `bench/dm/_feedback.py:187` (`score += 0.1 * severity`, live via `reference_runner_v3.py:393`), `bench/immune_agents.py:4146`/`:4149` (affine map of severity into confidence), `bench/dm/_convergence.py:276` (distinct from the cited `:267`).
- **`ΔV` urgency downgraded**: cc2 measured the live analogue `kappa_set` as the binding term of its `min` in **3 of 18** archived registries and flipped under **0 of 72** relabelling cases. Safe and low-yield, not load-bearing.
- **A brief figure was unverifiable in session.** fable reported the 25-of-29 claim-pattern routing rate as having no committed producer. Correct, and it is my fault: the measurement was run inline rather than committed as a script, which `measured-rate-travels-with-its-script` forbids.

## What this means for the ruling

The founder's position survives on substance. Severity is real, ordinal, domain-numbered, and the model sits above any particular measure. Nothing in either verdict supports a reading of severity as fairy dust.

What is added before he rules: **a gate needs a distinguished critical level as well as an ordering**, and the domain must supply both. The 2 seats split on it.

## Still unruled

- **B77** (convergence gate roster-blindness): wire both code paths, not only the legacy one (`HARDENED_GATE_DEFAULT = True`, [reference_runner_v3.py:1622](../bench/reference_runner_v3.py)); and which correlation — within-run recommended, differing from pooled at 2 of 6 roster sizes (9 vs 11 at 1 live seat).
- **Fold-back residue scoping**: a replace side carrying an unexamined payload beside a true computable rider still admits. Escalate the residue, or accept and record the risk.
- **Task-list provenance**: no entry records who raised it, so "how many are the founder's own" cannot be measured. By inspection 5 of 12 (B104, B140, B141, B142, B22).
- **Termination alarm struck** on his instruction of 2026-11-11, after B107 (`state: DONE`, `ruled: 2026-11-08`, *"I accept your recommendation"* on accepting the ratio) was re-raised to him regardless. Re-scoped from the interval's upper bound to the point estimate — a condition he has **not** ruled on — and verified still to fire at and above R = 1 rather than switched off.

Written under CDSFL note standard v1.9 (1 November 2026).
