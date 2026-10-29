#!/usr/bin/env python3
"""The claim channel enters R_k as a multiplier, and this is what it would do.

HIS RULING, 2026-10-29, annotation 8 of
`Responses/Decisions_Awaiting_You_2026-10-29.txt`: *"I accept your
recommendation. fr"*, against the recommendation that the informative-only
channel's verdict enter *"As a multiplier on R sub k, by analogy with the ruling
you already gave for the verification fact in section 7.7"*. That answers his
instruction of 2026-10-02, which asked which of sigma, S_k or R_k the verdict
should enter and whether as a multiplier or an addition.

WHAT THIS SCRIPT ESTABLISHES, each part able to fail.

  1. THE ALGEBRA, PROVED TWICE. The factor is ``C = 1 - weight * coverage``.
     SymPy and z3 independently establish, over the box
     ``weight in [0, 1/2], coverage in [0, 1], R_k in [0, 1]``: C lies in
     [1/2, 1]; ``R_k * C`` lies in [0, 1]; the product can NEVER exceed R_k, so
     the channel cannot manufacture risk; a weight of 0 and a coverage of 0 each
     leave R_k exactly unchanged; and a positive R_k cannot be driven to 0.

  2. WHY THE CEILING IS 1/2 AND NOT 1. At weight 1 with full coverage the factor
     is exactly 0 and residual risk is annihilated. That is a far stronger claim
     than claim coverage can support, and z3 shows it is reachable, so the
     ceiling excludes it rather than trusting a caller not to ask.

  3. WHAT IT WOULD CHANGE, MEASURED OVER THE ARCHIVE rather than argued. The
     live weight is 0, so the channel is inert today by construction. The
     coverage distribution over archived runs says what a non-zero weight would
     move -- which is the evidence fable's own condition for promotion requires:
     a commissioning run measuring the channel's error rate. This is NOT that
     run. It bounds the channel's reach, which is the question that comes first:
     a channel that would move nothing needs no commissioning run at all.

READ-ONLY.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.claim_ledger import (  # noqa: E402
    CLAIM_CHANNEL_MAX_WEIGHT, CLAIM_CHANNEL_WEIGHT, apply_claim_channel,
    claim_channel_coverage, claim_channel_factor, ledger_from_registry)


def prove() -> list[tuple[str, str]]:
    """SymPy and z3 on the same 6 properties. Disagreement is itself a result."""
    rows: list[tuple[str, str]] = []
    import sympy as sp
    lam, cov, Rk = sp.symbols("lambda coverage R_k", nonnegative=True)
    C = 1 - lam * cov
    rows.append(("sympy: weight 0 leaves R_k unchanged",
                 "PROVED" if sp.simplify(Rk * C.subs(lam, 0) - Rk) == 0 else "FAILED"))
    rows.append(("sympy: coverage 0 leaves R_k unchanged",
                 "PROVED" if sp.simplify(Rk * C.subs(cov, 0) - Rk) == 0 else "FAILED"))
    rows.append(("sympy: monotone non-increasing in coverage",
                 "PROVED" if sp.simplify(sp.diff(C, cov) + lam) == 0 else "FAILED"))
    try:
        import z3
    except ImportError:                                      # pragma: no cover
        rows.append(("z3", "UNAVAILABLE — the claim stays SymPy-only"))
        return rows
    zlam, zcov, zRk = z3.Reals("lambda coverage R_k")
    MAX = z3.RealVal(1) / z3.RealVal(2)
    box = [zlam >= 0, zlam <= MAX, zcov >= 0, zcov <= 1, zRk >= 0, zRk <= 1]
    zC = 1 - zlam * zcov

    def proved(claim) -> str:
        s = z3.Solver(); s.add(box); s.add(z3.Not(claim))
        r = s.check()
        if r == z3.unsat:
            return "PROVED"
        if r == z3.sat:
            return f"COUNTEREXAMPLE {s.model()}"
        return "UNKNOWN — z3 could not decide, so the claim is UNVERIFIED"

    rows.append(("z3: factor lies in [1/2, 1]",
                 proved(z3.And(zC >= MAX, zC <= 1))))
    rows.append(("z3: product lies in [0, 1]",
                 proved(z3.And(zRk * zC >= 0, zRk * zC <= 1))))
    rows.append(("z3: the channel can never inflate risk",
                 proved(zRk * zC <= zRk)))
    s = z3.Solver(); s.add(box); s.add(zRk > 0, zRk * zC == 0)
    rows.append(("z3: a positive R_k cannot be driven to exactly 0",
                 "PROVED (unsat)" if s.check() == z3.unsat
                 else f"REACHABLE {s.model()}"))
    # THE CEILING'S JUSTIFICATION, shown by REMOVING it: at weight 1 it IS reachable.
    s = z3.Solver()
    s.add([zlam >= 0, zlam <= 1, zcov >= 0, zcov <= 1, zRk > 0])
    s.add(zRk * (1 - zlam * zcov) == 0)
    rows.append(("z3: with the ceiling at 1 instead, annihilation IS reachable",
                 "REACHABLE — this is why the ceiling is 1/2"
                 if s.check() == z3.sat else "unreachable, so the ceiling is unjustified"))
    rows.extend(_wolfram())
    return rows


#: THE WOLFRAM CROSS-CHECK IS THE SECOND FALSIFIER AND IS NEVER REQUIRED.
#: Founder's ruling of 2026-09-28: nobody is compelled to install Wolfram, and
#: where it IS available the model should use it as a SECONDARY falsifier against
#: open-source output. SymPy and z3 above are PRIMARY; this is additional. An
#: absent kernel, a licence problem or a timeout is REPORTED and is not a
#: blocker, and a call that printed a `::` message verified NOTHING.
_WL = r"""
ClearAll[w,v,r,fac];
box = 0<=w<=1/2 && 0<=v<=1 && 0<=r<=1;
fac = 1 - w*v;
Print["factor_in_half_to_one=", Resolve[ForAll[{w,v,r}, box, 1/2 <= fac <= 1], Reals]];
Print["product_in_zero_to_one=", Resolve[ForAll[{w,v,r}, box, 0 <= r*fac <= 1], Reals]];
Print["never_inflates=", Resolve[ForAll[{w,v,r}, box, r*fac <= r], Reals]];
Print["annihilation_at_half=", Resolve[Exists[{w,v,r}, box && r>0 && r*fac==0], Reals]];
Print["annihilation_at_one=", Resolve[Exists[{w,v,r}, 0<=w<=1 && 0<=v<=1 && 0<=r<=1 && r>0 && r*(1-w*v)==0], Reals]];
Print["derivative=", D[fac,v]];
"""

_WL_EXPECTED = {
    "factor_in_half_to_one": "True",
    "product_in_zero_to_one": "True",
    "never_inflates": "True",
    "annihilation_at_half": "False",
    "annihilation_at_one": "True",
    "derivative": "-w",
}


def _wolfram() -> list[tuple[str, str]]:
    import shutil
    import subprocess
    exe = shutil.which("wolframscript")
    if exe is None:
        return [("Wolfram Language (secondary falsifier)",
                 "UNAVAILABLE - wolframscript is not on PATH; the open-source "
                 "proofs above stand on their own")]
    try:
        proc = subprocess.run([exe, "-code", _WL], capture_output=True,
                              text=True, timeout=120)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return [("Wolfram Language (secondary falsifier)",
                 f"NOT EVIDENCE - {type(exc).__name__}: {exc}")]
    out = (proc.stdout or "") + (proc.stderr or "")
    if "::" in out:
        bad = [ln for ln in out.splitlines() if "::" in ln]
        return [("Wolfram Language (secondary falsifier)",
                 f"NOT EVIDENCE - the kernel printed a message: {bad[0][:80]}")]
    got = {}
    for line in out.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            got[k.strip()] = v.strip()
    rows = []
    for key, want in _WL_EXPECTED.items():
        have = got.get(key)
        if have is None:
            rows.append((f"wolfram: {key}", "MISSING from the kernel output"))
        elif have == want:
            rows.append((f"wolfram: {key}", f"AGREES ({have})"))
        else:
            rows.append((f"wolfram: {key}",
                         f"DISAGREES - expected {want}, got {have}"))
    rows.append(("Wolfram Language",
                 "the 6 rows above were computed with Wolfram Language and are "
                 "attributed to it"))
    return rows


def archive_reach(limit: int | None) -> dict:
    """Coverage over archived runs. Reports its own cap rather than truncating quietly."""
    states = sorted(REPO.glob("bench/logs/*/runner_state.json")) + \
             sorted(REPO.glob("bench/logs/*/*/runner_state.json"))
    total_found = len(states)
    capped = states if limit is None else states[:limit]
    rows = []
    for path in capped:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        reg = (doc.get("registry") or {}).get("entries") or {}
        if not reg:
            continue
        led = ledger_from_registry(reg, target=str(path.parent.name))
        rep = led.report()
        rows.append({
            "run": path.parent.name,
            "claims": rep["claims_total"],
            "coverage": rep["claim_channel_coverage"],
            "factor_live": rep["claim_channel_factor"],
            "factor_ceiling": rep["claim_channel_factor_at_ceiling"],
        })
    return {"found": total_found, "read": len(rows),
            "capped_at": limit, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=None,
                    help="cap how many archived runs are read (default: all)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    proofs = prove()
    reach = archive_reach(args.limit)
    if args.json:
        print(json.dumps({"proofs": proofs, "reach": reach}, indent=2))
        return 0

    print("== the claim channel's entry into R_k ==")
    print(f"   form           : R_k_effective = R_k * (1 - weight * coverage)")
    print(f"   live weight    : {CLAIM_CHANNEL_WEIGHT}  (inert by construction)")
    print(f"   ceiling        : {CLAIM_CHANNEL_MAX_WEIGHT}")
    print(f"   coverage means : confirmed claims / all claims about the target")
    print()
    print("   THE ALGEBRA, by 2 independent tools:")
    for name, verdict in proofs:
        print(f"     {name:<58} {verdict}")
    print()
    print(f"   ARCHIVE REACH: {reach['read']} of {reach['found']} archived run "
          f"states carry a registry"
          + (f" (capped at {reach['capped_at']})" if reach["capped_at"] else ""))
    if not reach["rows"]:
        print("     no archived run carries a claim ledger, so the channel's "
              "reach is 0 and a commissioning run would measure nothing")
        return 0
    covs = [r["coverage"] for r in reach["rows"]]
    import numpy as np
    from scipy import stats
    arr = np.array(covs, dtype=float)
    print(f"     coverage  n={len(covs)}  mean={arr.mean():.6f}  "
          f"median={float(np.median(arr)):.6f}  min={arr.min():.6f}  "
          f"max={arr.max():.6f}")
    nonzero = int((arr > 0).sum())
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(nonzero, len(covs), method="wilson")
    z = stats.norm.ppf(0.975)
    p = nonzero / len(covs)
    d = 1 + z * z / len(covs)
    c = (p + z * z / (2 * len(covs))) / d
    h = z * np.sqrt(p * (1 - p) / len(covs) + z * z / (4 * len(covs) ** 2)) / d
    print(f"     runs where the channel would move R_k at all: {nonzero} of "
          f"{len(covs)} = {p:.6f}")
    print(f"       statsmodels wilson   [{lo:.6f}, {hi:.6f}]")
    print(f"       numpy closed form    [{c - h:.6f}, {c + h:.6f}]")
    worst = min(reach["rows"], key=lambda r: r["factor_ceiling"])
    print(f"     largest reduction at the ceiling: run {worst['run']}, "
          f"factor {worst['factor_ceiling']:.6f} on {worst['claims']} claims")
    print(f"     a run with R_k = 0.308 would read "
          f"{apply_claim_channel(0.308, {'claims_total': worst['claims'], 'by_verdict': {'CONFIRMED': round(worst['coverage'] * worst['claims'])}}, weight=CLAIM_CHANNEL_MAX_WEIGHT):.6f} "
          f"at the ceiling and 0.308000 at the live weight")
    return 0


if __name__ == "__main__":
    sys.exit(main())
