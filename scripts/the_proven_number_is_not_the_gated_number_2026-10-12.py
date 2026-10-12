#!/usr/bin/env python3
"""Is the R_k the severity gate PROVES related to the severity it RELEASES?

THE CLAIM THIS SETTLES, and it reverses what was reported to the founder on
2026-10-12 at 20:30. Both free seats of the blind round concluded, independently
and therefore by replication, that his provenance ruling and his "there are no
votes in CDSFL" principle are BOTH already satisfied in the tree, because the
restored severity test gates on `severity_is_proven` -- a TOOL RECOMPUTATION of
the model's stated R_k -- rather than on the raw model-stated float. That
consolidation was reported to him as probably settling the tension.

THE JOINT ROUND REFUTED IT, both seats refuting their own blind-round answer,
each with an executed attack. Two findings, and the second is the decisive one:

  LEVEL 1  the recomputation checks ARITHMETIC SELF-CONSISTENCY ONLY. Invented
           inputs that happen to be mutually consistent return PASS; nothing
           cross-checks any input against a harness-held fact. Reproduced here
           by scripts/severity_proof_gaming_2026-10-12.py: PASS on fabricated
           inputs, and a proof computing R_k = 0.95 releases a 0.45 float.

  LEVEL 2  THE PROVEN QUANTITY AND THE GATED QUANTITY ARE DIFFERENT NUMBERS.
           The release condition is `severity < 0.7 AND severity_is_proven(e)`.
           `severity_is_proven` reads only the proof STATUS, and the proof
           recomputes R_k from R_k's own stated inputs WITHOUT EVER READING
           `severity`. So the number that moves the gate is the raw
           model-stated severity float -- precisely the number the 2026-09-06
           measurement condemned -- and the proof is a side-condition on a
           different quantity.

WHAT THIS SCRIPT MEASURES. Over every archived entry carrying a PASS/WARN R_k
proof, the relation between the PROVEN R_k and the GATED severity. If the proof
corroborated the float even weakly, the two would correlate positively. The
measurement is the test of whether "the proofs are the gate's mechanism" is true
of the quantity the gate actually releases.

Usage: python3 scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py
"""
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
PROVEN = {"PASS", "WARN"}


def pairs():
    """(severity, proven R_k) for every archived entry with a passing proof."""
    out = []
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        for e in ((d or {}).get("registry") or {}).get("entries", {}).values():
            if not isinstance(e, dict):
                continue
            proof = e.get("severity_proof")
            if not isinstance(proof, dict):
                continue
            status = str(proof.get("status") or "").strip().upper()
            if status not in PROVEN:
                continue
            sev = e.get("severity")
            rk = proof.get("recomputed_rk", proof.get("model_rk"))
            if isinstance(sev, (int, float)) and isinstance(rk, (int, float)):
                out.append((float(sev), float(rk)))
    return out


def main() -> int:
    answer_help(__doc__, __file__)
    data = pairs()
    n = len(data)
    if n < 10:
        print(f"only {n} proven entries found; the measurement is void.")
        return 3
    import numpy as np
    from scipy import stats

    sev = np.array([a for a, _ in data])
    rk = np.array([b for _, b in data])
    print(f"archived entries with a PASS/WARN R_k proof: {n}")

    r, p = stats.pearsonr(sev, rk)
    r_np = float(np.corrcoef(sev, rk)[0, 1])
    rho, p_s = stats.spearmanr(sev, rk)
    # Fisher z interval, computed directly and cross-checked against scipy's own.
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(n - 3)
    lo, hi = np.tanh(z - 1.959963985 * se), np.tanh(z + 1.959963985 * se)
    print(f"  Pearson  r = {r:.4f}   p = {p:.4g}   95% CI [{lo:.4f}, {hi:.4f}]")
    print(f"             numpy corrcoef agrees: {r_np:.4f}  "
          f"(delta {abs(r - r_np):.2e})")
    print(f"  Spearman rho = {rho:.4f}   p = {p_s:.4g}")
    print(f"  r^2 = {r*r:.4f}  -> the proven R_k explains "
          f"{r*r:.2%} of severity variance, "
          f"{'NEGATIVELY' if r < 0 else 'positively'}")

    gap = np.abs(sev - rk)
    from statsmodels.stats.proportion import proportion_confint
    print(f"\n  mean |severity - proven R_k| = {gap.mean():.4f}   "
          f"median = {np.median(gap):.4f}")
    for tol in (0.01, 0.05, 0.10):
        k = int((gap <= tol).sum())
        clo, chi = proportion_confint(k, n, alpha=0.05, method="wilson")
        print(f"  |severity - R_k| <= {tol:.2f}: {k:4d}/{n}  {k/n:7.2%}  "
              f"Wilson [{clo:.2%}, {chi:.2%}]")
    k05 = int((gap <= 0.05).sum())
    print(f"\n  If release required the proof to be ABOUT the released number "
          f"at the proof's own 0.05 tolerance,\n  {n - k05} of {n} "
          f"({(n-k05)/n:.2%}) currently-proven entries would stop being "
          f"released.")
    if r < 0:
        print("\nVERDICT: the proof does not corroborate the float it licenses. "
              "It moves AGAINST it.")
    else:
        print("\nVERDICT: positively related; the consolidation may survive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
