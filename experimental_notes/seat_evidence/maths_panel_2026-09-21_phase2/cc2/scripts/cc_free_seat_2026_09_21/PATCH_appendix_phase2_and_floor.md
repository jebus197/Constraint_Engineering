<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'maths_panel_2026-09-21_phase2', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 18bd4a5975dac7cea97836a775350be6812582cbd67d0a331aa8e99e48f66ed3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# PATCH — docs/MATHEMATICAL_APPENDIX.md

Two corrections. Both are to text that already exists. Neither adds a parameter,
a gate, a flag or an entry point. Practitioner parameter count before: η, σ, ν, d, p.
After: **identical**. No equation changes.

The equations are RIGHT. What is wrong is the JUSTIFICATION attached to Phase 2,
and it is wrong in a way that has already cost something measurable: it caused a
panel seat to propose replacing a correct equation with one that violates
conservation of expected evidence at one endpoint and asserts zero residual risk
at the other.

---

## Correction 1 — line 229, Phase 2's justification

REPLACE:

> When σ = 1, the full detection benefit is captured. When σ = 0, risk stays at
> R_old — the fix failed and the pre-detection risk level applies.

WITH:

> When σ = 1, the full detection benefit is captured.
>
> **When σ = 0, risk returns to R_old. This is not the observation being
> discarded — it is the observation being accounted on both branches.** A cycle
> has two, and Phase 1 names only one of them. With P(detect | flaw) = q and no
> false positives:
>
> - **no detection**, probability 1 − q·R_old, posterior R_det = R_old(1−q)/(1−q·R_old), no fix attempted;
> - **detection**, probability q·R_old, posterior 1 (no false positives), fix resolves with probability σ, leaving 1 − σ.
>
> The mixture is `(1 − q·R_old)·R_det + q·R_old·(1 − σ) = R_old·(1 − q·σ)`, which
> at σ = 0 is **exactly R_old**. This is the tower property: an observation nobody
> successfully acts on cannot move expected risk. A rule returning the σ = 0
> posterior R_det instead would keep the favourable branch and drop the
> unfavourable one, manufacturing a free risk decrease of
> `q·R_old(1−R_old)/(1−q·R_old)` per cycle from an unrepaired finding.
>
> **Where this form is approximate.** Phase 2 interpolates between a quantity
> conditional on non-detection (σ = 1) and a marginal expectation (σ = 0), so it
> is not the exact mixture except at σ = 0. It exceeds it by
> `σ·q·R_old²(1−q)/(1−q·R_old) ≥ 0` — the composite **never understates risk**.
> That direction is deliberate and is why the form is retained.

## Correction 2 — line 247, the substrate-ceiling floor

REPLACE: `> lim_{n→∞} R_{n,k} ≥ ν_k`

WITH:

> lim_{n→∞} R_{n,k} ≥ ν_k, and at σ = 1 the attracting limit is **exactly ν_k / q**.
>
> The cycle map has fixed points {1, ν/q}. For ν < q the interior point ν/q
> attracts and 1 repels; for ν > q, ν/q leaves the interval and **R = 1 —
> certain failure — is the only fixed point in [0,1]**. At ν = q the two
> coincide, f'(1) = 1, and the approach to 1 is O(1/n) rather than geometric,
> so a run at the critical rate looks like slow convergence, not divergence.
> The stated floor ν_k is loose by a factor 1/q: at q = 0.2, ν = 0.05 the true
> floor is 0.25, five times the stated value.
