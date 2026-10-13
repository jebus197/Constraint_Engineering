# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0df86520899d4ab306be7cef5254885d2b7a6070c1956222d2709ea19c803593
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Which verdict class drives the 835 downward crossers when V is applied?

CONTEXT. Item 1 of the 2026-10-13 free-panel brief measured that applying only
the V factor of docs/MATHEMATICAL_APPENDIX.md section 7.7 to the archived
severities moves the share at or above the 0.7 cut from 41.6313% to 16.3129%,
with 835 of 3,298 entries crossing downward. The brief asks whether that
movement is evidence the formula is right or evidence the cut was calibrated
against the uncomputed float.

THE QUESTION THIS SCRIPT DECIDES IS SHARPER: of the downward crossers, how many
cross because V(False) = 0 (the appendix's KEY PROPERTY -- a disproved finding
scores zero) and how many cross because V(None) = 0.5 (a finding nothing ever
verified is HALVED)? The distinction is load-bearing for the gate design:

  * A crosser with falsifier_verdict REFUTED crosses because a TOOL disproved
    it. Zeroing it can never loosen the gate against a real defect -- the tool
    already ruled, and status REFUTED is terminal in the halt machinery anyway
    (bench/reference_runner_v3.py, _irreducible_queue_split's _TERMINAL set).
  * A crosser with NO verdict crosses only because V(None) = 0.5 HALVED an
    unverified claim. If V(None) were applied to the BLOCKING gate, a model
    could drop its own critical below the 0.7 cut by never attaching a
    falsifier -- rewarding exactly the omission the falsifier gate polices.
    Same loophole shape as the one the 2026-09-06 one-directional rule closed
    for missing R_k proofs (bench/reference_runner_v3.py, "THE ENFORCEMENT IS
    ONE-DIRECTIONAL").

Usage: python3 scripts/what_moves_when_v_is_applied_2026-10-13.py
"""
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

CUT = 0.7
#: V per the appendix: CONFIRMED is V(True), REFUTED is V(False), anything
#: else -- absent, UNTOOLABLE, ERROR, NON_DISCRIMINATING -- is V(None) = 0.5.
V = {"CONFIRMED": 1.0, "REFUTED": 0.0}

KEY_PROPERTY = "REFUTED (V=0, the key property)"
HALVED = "no/indeterminate verdict (V=0.5 halving)"


def entries():
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if isinstance(e, dict):
                yield cid, e


def _both_cis(k: int, n: int):
    """Wilson (statsmodels) and Clopper-Pearson (scipy) -- 2 independent tools."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo2 = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi2 = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return (lo, hi), (lo2, hi2)


def main() -> int:
    answer_help(__doc__, __file__)
    n = before = after = 0
    crossers = collections.Counter()
    for _cid, e in entries():
        sev = e.get("severity")
        if not isinstance(sev, (int, float)):
            continue
        n += 1
        verdict = str(e.get("falsifier_verdict") or "").strip().upper()
        sev_v = float(sev) * V.get(verdict, 0.5)
        if float(sev) >= CUT:
            before += 1
            if sev_v < CUT:
                crossers[KEY_PROPERTY if verdict == "REFUTED" else HALVED] += 1
        if sev_v >= CUT:
            after += 1
    if not n:
        print("no archived entries carry a numeric severity; measurement void.")
        return 3
    total_cross = sum(crossers.values())
    print(f"archived entries with numeric severity : {n}")
    print(f"at/above {CUT} before V                 : {before} ({before/n:.4%})")
    print(f"at/above {CUT} after  V                 : {after} ({after/n:.4%})")
    print(f"downward crossers                      : {total_cross}")
    for label, c in crossers.most_common():
        (wl, wh), (cl, ch) = _both_cis(c, total_cross)
        print(f"  {label:<44}{c:>5}  ({c/total_cross:.4%} of crossers)")
        print(f"    Wilson 95% [{wl:.4%}, {wh:.4%}]  "
              f"Clopper-Pearson 95% [{cl:.4%}, {ch:.4%}]")
    refuted_cross = crossers.get(KEY_PROPERTY, 0)
    print()
    print(f"VERDICT: {refuted_cross} of {total_cross} crossers are the key property;")
    print(f"the other {total_cross - refuted_cross} cross only because V(None)=0.5")
    print(f"halves an UNVERIFIED claim. Applying V(None) at the BLOCKING gate")
    print(f"would release those {total_cross - refuted_cross} without any tool")
    print(f"having ruled -- the falsifier-omission loophole. V(False)=0 is safe")
    print(f"to gate; V(None) belongs to scoring/reporting only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
