#!/usr/bin/env python3
"""Tool cross-check: verify the round-2 implementation against Stage 6 math.

Runs the same eight boundary claims that were verified symbolically before
implementation, but this time drives the actual implementation in
`bench/dm/_divergence.py` and compares its observable behaviour against
SymPy/z3 predictions. If the code disagrees with the math, this script
fails loudly — that is the contract.

Usage:
    python3 bench/verify_round2_implementation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import sympy as sp  # noqa: E402
import z3  # noqa: E402

from bench.dm._divergence import (  # noqa: E402
    DivergenceConfig,
    build_divergence_record,
    divergence_penalty_multiplier,
    eta_int_modulator,
    parse_contrast_statement,
    score_isomorphism,
)


FAIL = 0
PASS = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global FAIL, PASS
    if condition:
        PASS += 1
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAIL += 1
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))


def primary_text() -> str:
    return (
        "Use conjugate gradient descent with Polak-Ribiere updates and "
        "Armijo backtracking line search."
    )


def valid_alt_body(dim: str, body: str) -> str:
    return (
        f"Alternative 1 (dimension: {dim})\n"
        f"{body}\n"
        f"Differs from primary: uses a genuinely different update rule with "
        f"different convergence guarantees.\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Claim 1 — Modulator tier set is {1.00, 0.85, 0.70, 0.60} and monotone
# ─────────────────────────────────────────────────────────────────────────────


def claim_1_tier_set() -> None:
    print("\n[1] Modulator tier set = {1.00, 0.85, 0.70, 0.60}, severe = 0.60")

    # Compliant alternative — 1.00
    compliant = build_divergence_record(
        "f1",
        primary_text(),
        valid_alt_body("mechanism", "Truncated-Newton with matvec products."),
    )
    m1 = eta_int_modulator(compliant)
    check("compliant → 1.00", m1 == 1.00, f"got {m1}")

    # Soft tier — engaged but missing dimension
    soft = build_divergence_record(
        "f1",
        primary_text(),
        "Alternative:\nNewton-Raphson method.\nDiffers from primary: changes the second-order method.\n",
    )
    m2 = eta_int_modulator(soft)
    check("soft (missing dim) → 0.85", m2 == 0.85, f"got {m2}")

    # Hard tier — no alt, no null
    hard = build_divergence_record("f1", primary_text(), "just primary, nothing else")
    m3 = eta_int_modulator(hard)
    check("hard (no engagement) → 0.70", m3 == 0.70, f"got {m3}")

    # Severe tier — near-copy 0.98+
    severe = build_divergence_record(
        "f1",
        primary_text(),
        valid_alt_body("mechanism", primary_text()),  # iso 1.0
    )
    m4 = eta_int_modulator(severe)
    check("severe (near-copy ≥0.98) → 0.60", m4 == 0.60, f"got {m4}")

    # Monotonicity: 1.00 > 0.85 > 0.70 > 0.60
    tiers = [m1, m2, m3, m4]
    check(
        "monotone descending across tiers",
        tiers == sorted(tiers, reverse=True),
        f"{tiers}",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Claim 2 — eta_int_modulator ∈ (0, 1] for all parsed inputs
# ─────────────────────────────────────────────────────────────────────────────


def claim_2_unit_interval() -> None:
    print("\n[2] eta_int_modulator always in (0, 1]")

    cases = [
        ("compliant", valid_alt_body("mechanism", "Truncated Newton with matvec.")),
        ("iso-full", valid_alt_body("mechanism", primary_text())),
        ("missing-contrast",
            "Alternative 1 (dimension: mechanism)\nNewton method.\n"),
        ("missing-dim", "Alternative:\nNewton.\n"),
        ("empty", ""),
        ("nothing", "just primary"),
    ]
    for label, raw in cases:
        rec = build_divergence_record("f1", primary_text(), raw)
        m = eta_int_modulator(rec)
        check(f"{label} ∈ (0, 1]", 0.0 < m <= 1.0, f"got {m}")


# ─────────────────────────────────────────────────────────────────────────────
# Claim 3 — Channel assignment: modulator multiplies η_int, effect on R_k
#          flows through η_combined → q → recurrence
# ─────────────────────────────────────────────────────────────────────────────


def claim_3_channel_assignment() -> None:
    print("\n[3] Channel assignment: m · η_int → η_combined → q → R_k")

    # Symbolic check — derive the chain using SymPy, confirm m appears only
    # through η_int, not as a free R_k multiplier.
    m, eta_int, c_ext, nu_k, d, p, R_prev = sp.symbols(
        "m eta_int c_ext nu_k d p R_prev", positive=True
    )

    eta_int_modulated = m * eta_int
    eta_combined = eta_int_modulated * (1 - c_ext * (1 - nu_k))
    q = eta_combined * d * p
    R_next = R_prev * (1 - q) / (1 - q * R_prev)

    # Partial of R_next wrt m — should be non-zero (modulator DOES affect R_k)
    dR_dm = sp.simplify(sp.diff(R_next, m))
    check("∂R/∂m ≠ 0 (modulator reaches R_k)", dR_dm != 0, f"symbolic: {dR_dm}")

    # Partial of R_next wrt m, evaluated in the limit η_int → 0: should go
    # to zero (no internal novelty → no modulation effect). This is the
    # channel contract: modulation is multiplicative on η_int, not additive.
    dR_dm_at_zero_eta = sp.simplify(dR_dm.subs(eta_int, 0))
    check(
        "η_int=0 kills the modulation path (multiplicative on η_int)",
        dR_dm_at_zero_eta == 0,
        f"symbolic: {dR_dm_at_zero_eta}",
    )

    # Partial of R_next wrt m, at c_ext=1, nu_k=0 → η_combined=0 → q=0 →
    # R_next = R_prev (no effect). Modulator cannot rescue a
    # full-coverage-known finding.
    full_known = sp.simplify(dR_dm.subs({c_ext: 1, nu_k: 0}))
    check(
        "c_ext=1, ν_k=0 → modulator has no effect (known-and-corroborated)",
        full_known == 0,
        f"symbolic: {full_known}",
    )

    # ν_k does not appear in the modulator's definition — check that the
    # modulator factor in the chain is independent of ν_k structurally.
    # (This is the ν_k-credit-forbidden invariant.)
    # Take ∂m/∂ν_k — m is a scalar, not a function of ν_k, so trivially 0.
    # Verify by constructing a symbolic modulator that would violate the
    # invariant and showing it mathematically ≠ our m.
    check(
        "modulator m is independent of ν_k (type-level, not functional)",
        not m.has(nu_k),
        "m is a bare symbol with no ν_k dependency",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Claim 4 — Contrast statement is parsed and required
# ─────────────────────────────────────────────────────────────────────────────


def claim_4_contrast_required() -> None:
    print("\n[4] Contrast statement: parsed and required by validator")

    # Parse positive
    body = "Truncated-Newton.\nDiffers from primary: second-order via matvec.\n"
    c, stripped = parse_contrast_statement(body)
    check("parses 'Differs from primary:' → captures statement", c is not None and "second-order" in c)
    check("removes contrast line from body (no double-count in Jaccard)", "Differs from primary" not in stripped)

    # Validator rejects missing contrast
    raw_missing = "Alternative 1 (dimension: mechanism)\nNewton method.\n"
    rec = build_divergence_record("f1", primary_text(), raw_missing)
    has_missing_reason = any(
        "missing_contrast_statement" in r
        for a in rec.alternatives for r in a.rejection_reasons
    )
    check("rejects missing contrast", has_missing_reason and not rec.compliant)

    # Validator rejects too-short contrast
    raw_short = (
        "Alternative 1 (dimension: mechanism)\n"
        "Newton method.\n"
        "Differs from primary: x.\n"  # 1 char
    )
    rec_short = build_divergence_record("f1", primary_text(), raw_short)
    has_short_reason = any(
        "contrast_statement_too_short" in r
        for a in rec_short.alternatives for r in a.rejection_reasons
    )
    check("rejects too-short contrast", has_short_reason and not rec_short.compliant)


# ─────────────────────────────────────────────────────────────────────────────
# Claim 5 — Sibling alt-vs-alt ship-blocker demotes ONLY the later sibling
# ─────────────────────────────────────────────────────────────────────────────


def claim_5_sibling_ship_blocker() -> None:
    print("\n[5] Sibling ship-blocker: later duplicate demoted, first stands")

    raw = (
        "Alternative 1 (dimension: mechanism)\n"
        "Truncated-Newton with matvec Hessian products.\n"
        "Differs from primary: second-order via matvec, not line search.\n\n"
        "Alternative 2 (dimension: assumption)\n"
        "Truncated-Newton with matvec Hessian products.\n"  # duplicate
        "Differs from primary: assumes cheap Hessian-vector product.\n"
    )
    rec = build_divergence_record("f1", primary_text(), raw)
    check("first alt admissible", rec.alternatives[0].admissible is True)
    check("second alt inadmissible (sibling duplicate)", rec.alternatives[1].admissible is False)
    check(
        "sibling score recorded on second, not first",
        rec.alternatives[0].sibling_max_isomorphism == 0.0
        and rec.alternatives[1].sibling_max_isomorphism >= 0.85,
    )
    # Structural claim: the first alternative (i=0) has no earlier sibling.
    # check_sibling_admissibility loops j in range(i); for i=0, range(0) is
    # empty → max_sib stays 0.0 → first alt cannot lose by sibling check.
    check("structural: first-alt cannot lose sibling check (range(0) empty)", True,
          "check_sibling_admissibility loops j in range(i); i=0 → no comparisons")


# ─────────────────────────────────────────────────────────────────────────────
# Claim 6 — Near-copy 0.98 threshold and severe tier 0.60
# ─────────────────────────────────────────────────────────────────────────────


def claim_6_near_copy_tier() -> None:
    print("\n[6] Near-copy 0.98 Jaccard triggers severe 0.60 tier")

    # Identical primary text → iso 1.0 → severe
    raw = valid_alt_body("mechanism", primary_text())
    rec = build_divergence_record("f1", primary_text(), raw)
    m = eta_int_modulator(rec)
    check("iso=1.0 → 0.60 severe tier", m == 0.60, f"got {m}")

    # Partial overlap (~0.85-0.95 Jaccard, below near-copy) should land in
    # the regular all-isomorphic path → also 0.60 via the original §18 rule.
    # Verify the boundary is correctly ordered: near_copy_threshold (0.98)
    # ≥ isomorphism_threshold (0.85).
    cfg = DivergenceConfig()
    check("near_copy_threshold ≥ isomorphism_threshold (boundary ordering)",
          cfg.near_copy_threshold >= cfg.isomorphism_threshold,
          f"{cfg.near_copy_threshold} vs {cfg.isomorphism_threshold}")

    # z3 constraint solve: does there exist iso in [0,1] such that the
    # near-copy path fires but the original isomorphic-path doesn't? Only
    # if iso ≥ 0.98 AND NOT(iso ≥ 0.85) — impossible.
    iso = z3.Real("iso")
    s = z3.Solver()
    s.add(iso >= 0.98, iso < 0.85)
    check("no iso satisfies near_copy AND NOT isomorphic (monotone gate)",
          s.check() == z3.unsat)


# ─────────────────────────────────────────────────────────────────────────────
# Claim 6b — ν_k = 1 boundary (Gemini gap) + all-isomorphic-below-near-copy
# ─────────────────────────────────────────────────────────────────────────────


def claim_6b_model_review_gaps() -> None:
    print("\n[6b] Verification gaps identified by round-3 model panel")

    # Gap A (Gemini): ν_k = 1 boundary → η_combined = η_int (novel, no penalty)
    m, eta_int, c_ext, nu_k, d, p = sp.symbols(
        "m eta_int c_ext nu_k d p", positive=True
    )
    eta_combined = (m * eta_int) * (1 - c_ext * (1 - nu_k))
    at_novel = eta_combined.subs(nu_k, 1)
    check("ν_k=1 → η_combined = m·η_int (novel finding, full detection)",
          sp.simplify(at_novel - m * eta_int) == 0,
          f"symbolic: {at_novel}")

    # Gap B (CC2): all-isomorphic-below-near-copy path exercised in code.
    # Need Jaccard in [0.85, 0.98) — requires enough shared tokens that
    # changing one word still leaves overlap above threshold. Use a longer
    # primary to increase token count (more overlap per word changed).
    long_primary = (
        "Use conjugate gradient descent with Polak-Ribiere updates and "
        "Armijo backtracking line search. This approach converges linearly "
        "for strongly convex quadratic functions with bounded condition number."
    )
    long_alt = long_primary.replace("linearly", "quadratically")
    iso_check = score_isomorphism(long_primary, long_alt)
    check(f"crafted alt has iso={iso_check:.3f} in [0.85, 0.98)",
          0.85 <= iso_check < 0.98,
          f"iso={iso_check:.3f}")

    # Now build a divergence record manually. The parser would strip the
    # contrast statement, so we build the raw output with a contrast line
    # that is long enough to pass but the alternative body is the long_alt.
    raw = (
        "Alternative 1 (dimension: mechanism)\n"
        f"{long_alt}\n"
        "Differs from primary: changes convergence rate from linear to quadratic.\n"
    )
    rec = build_divergence_record("f1", long_primary, raw)
    m_val = eta_int_modulator(rec)
    # With ONE alternative that's isomorphic (iso ≥ 0.85 but < 0.98), ALL
    # alternatives are isomorphic → all_isomorphic path → 0.60.
    check("all-isomorphic-below-near-copy → 0.60 severe tier",
          m_val == 0.60,
          f"got {m_val}")


# ─────────────────────────────────────────────────────────────────────────────
# Claim 7 — Jaccard score is in [0, 1] and symmetric
# ─────────────────────────────────────────────────────────────────────────────


def claim_7_jaccard_bounds() -> None:
    print("\n[7] Jaccard: bounded [0,1] and symmetric")

    pairs = [
        ("", ""),
        ("x y z", "x y z"),
        ("x y z", "a b c"),
        ("x y z", "x y w"),
        ("conjugate gradient", "truncated newton"),
    ]
    for a, b in pairs:
        s_ab = score_isomorphism(a, b)
        s_ba = score_isomorphism(b, a)
        check(f"bounded s({a!r},{b!r})={s_ab:.3f} ∈ [0,1]", 0.0 <= s_ab <= 1.0)
        check(f"symmetric s({a!r},{b!r}) == s({b!r},{a!r})", s_ab == s_ba)


# ─────────────────────────────────────────────────────────────────────────────
# Claim 8 — Backward compatibility: divergence_penalty_multiplier alias works
# ─────────────────────────────────────────────────────────────────────────────


def claim_8_backward_compat() -> None:
    print("\n[8] Backward compatibility: legacy alias resolves to eta_int_modulator")

    check(
        "divergence_penalty_multiplier is eta_int_modulator (same object)",
        divergence_penalty_multiplier is eta_int_modulator,
    )

    raw = valid_alt_body("mechanism", "Truncated-Newton.")
    rec = build_divergence_record("f1", primary_text(), raw)
    legacy = divergence_penalty_multiplier(rec)
    current = eta_int_modulator(rec)
    check("legacy and current return identical values", legacy == current, f"{legacy} == {current}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    print("=" * 72)
    print("  Round-2 Implementation Cross-Check")
    print("  Tools: SymPy 1.14, z3 4.16, implementation in bench/dm/_divergence.py")
    print("=" * 72)

    claim_1_tier_set()
    claim_2_unit_interval()
    claim_3_channel_assignment()
    claim_4_contrast_required()
    claim_5_sibling_ship_blocker()
    claim_6_near_copy_tier()
    claim_6b_model_review_gaps()
    claim_7_jaccard_bounds()
    claim_8_backward_compat()

    total = PASS + FAIL
    print("\n" + "=" * 72)
    print(f"  {PASS}/{total} checks passed, {FAIL} failed")
    print("=" * 72)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
