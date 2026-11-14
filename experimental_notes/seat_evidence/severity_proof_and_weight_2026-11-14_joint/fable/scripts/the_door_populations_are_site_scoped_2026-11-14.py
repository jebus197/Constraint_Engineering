# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_proof_and_weight_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2d1dd845c63136f0a196a32c2da5d7c18269da33dac89ea98a8fd5b12f676afc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The R1 headline figure is SITE-SCOPED, and both blind seats' numbers were
right about different doors.

JOINT ROUND `severity_proof_and_weight_2026-11-14`. The blind half produced two
figures for "how many archived entries stop releasing when the proof must be
about the gated number at tolerance 0.05":

  cc2   : 555/652 = 85.12%  -- every archived PASS/WARN entry
  fable : 422/519 = 81.31%  -- only entries with severity < 0.7

`severity_is_proven` has THREE live call sites and they read DIFFERENT
populations:

  * the A4 convergence door (reference_runner_v3.py ~4442) and the
    reasoned-withdrawal retirement (~9735) consult the proof ONLY when
    severity < CRITICAL_SEVERITY_THRESHOLD -- fable's 519 is their population;
  * the severity-calibration demotion (~10936) consults it only on entries
    `_is_demotion_eligible` admits, whose FIRST clause is
    severity >= CRITICAL_SEVERITY_THRESHOLD -- the 133 criticals cc2's count
    includes and fable's excludes are EXACTLY that door's population.

So neither single figure is "the" effect of the repoint. This script reports
the effect PER DOOR. Measured at dispatch: release/withdrawal doors lose
422/519 (81.31%); the demotion door loses 133/133 (100.00%, Wilson
[97.19%, 100.00%]) -- under the repoint, NO archived critical's proof agrees
with its own severity, so proof-licensed demotion would stop entirely until a
proof about the gated number exists. 555 = 422 + 133 exactly, which is why the
two blind figures reconcile: every entry that keeps the exemption (97) is
sub-critical.

Usage: python3 scripts/the_door_populations_are_site_scoped_2026-11-14.py
"""
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
PROVEN = {"PASS", "WARN"}
TOL = 0.05


def pairs():
    out = []
    for fp in (REPO / "bench" / "logs").glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                  # noqa: BLE001
            continue
        for e in ((d or {}).get("registry") or {}).get("entries", {}).values():
            if not isinstance(e, dict):
                continue
            p = e.get("severity_proof")
            if not isinstance(p, dict):
                continue
            if str(p.get("status") or "").strip().upper() not in PROVEN:
                continue
            sev = e.get("severity")
            rk = p.get("recomputed_rk", p.get("model_rk"))
            if isinstance(sev, (int, float)) and isinstance(rk, (int, float)):
                out.append((float(sev), float(rk)))
    return out


def main() -> int:
    answer_help(__doc__, __file__)
    from statsmodels.stats.proportion import proportion_confint
    from bench.reference_runner_v3 import CRITICAL_SEVERITY_THRESHOLD as T

    data = pairs()
    if len(data) < 10:
        print(f"only {len(data)} proven entries found; the measurement is void.")
        return 3

    def rep(name, pop):
        n = len(pop)
        keep = sum(1 for s, r in pop if abs(s - r) <= TOL)
        lose = n - keep
        lo, hi = proportion_confint(lose, n, alpha=0.05, method="wilson")
        print(f"  {name}\n    n={n}  keep exemption: {keep} ({keep/n:.2%})  "
              f"lose: {lose} ({lose/n:.2%})  Wilson [{lo:.2%}, {hi:.2%}]")
        return n, keep, lose

    sub = [(s, r) for s, r in data if s < T]
    crit = [(s, r) for s, r in data if s >= T]
    print(f"archived PASS/WARN entries: {len(data)}  "
          f"(threshold read from the runner: {T})")
    n_all, k_all, l_all = rep("ALL entries (the blind 555/652 population)", data)
    n_sub, k_sub, l_sub = rep(
        "severity < threshold -- A4 door (~4442) + reasoned withdrawal (~9735)",
        sub)
    n_cr, k_cr, l_cr = rep(
        "severity >= threshold -- calibration demotion door (~10936, "
        "via _is_demotion_eligible clause 1)", crit)
    assert l_all == l_sub + l_cr and k_all == k_sub + k_cr
    print(f"\n  reconciliation: {l_all} = {l_sub} + {l_cr}; every keeper is "
          f"sub-critical ({k_cr} critical keepers).")

    # The guard that decided the merge: a malformed proof figure must not
    # license. Python's bool is an int, so an isinstance((int, float)) check
    # ADMITS `recomputed_rk=True` as 1.0; the merged implementation rejects it.
    from bench import reference_runner_v3 as rr
    was = rr._SEVERITY_PROOF_MATCHES_GATED["on"]
    try:
        rr._SEVERITY_PROOF_MATCHES_GATED["on"] = True
        e = {"severity": 0.97,
             "severity_proof": {"status": "PASS", "recomputed_rk": True}}
        got = rr.severity_is_proven(e)
        print(f"\n  merged guard: PASS proof with recomputed_rk=True (bool) at "
              f"severity 0.97 -> severity_is_proven = {got} "
              f"(must be False: a malformed figure is not agreement)")
        assert got is False
    finally:
        rr._SEVERITY_PROOF_MATCHES_GATED["on"] = was
    return 0


if __name__ == "__main__":
    sys.exit(main())
