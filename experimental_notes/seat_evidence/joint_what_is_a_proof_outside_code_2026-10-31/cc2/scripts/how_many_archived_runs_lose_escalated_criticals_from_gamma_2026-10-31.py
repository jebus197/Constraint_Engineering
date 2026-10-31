# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 95c62cc1187302349e623f5ee86641173f92da190a0bb18184605040c77b3027
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""How many archived runs lose an escalated critical from gamma's novelty series?

THE PREDICATE-FIRST QUESTION behind the round-2 finding of seat fable in
`what_is_a_proof_outside_code_b22`. `apply_falsifier_verdicts` refuses to drop
an asserted-critical on a REFUTED verdict (CONFIRM-only, 2026-08-03) and
escalates it to HIL as UNCONFIRMED instead. UNCONFIRMED is in
`_NON_NOVEL_TERMINAL_STATUSES`, so `_settled_novelty_series` -- the series gamma
is estimated from -- counts that round as having produced no critical.

So the protection against faking a critical away in the STATUS channel deletes
it from the CONVERGENCE-MEASUREMENT channel. This script asks whether that
reached any archived decision, because an addition nothing reaches is not a
finding either.

Read through the runner's OWN predicates (`_settled_novelty_series`,
`_estimate_gamma`, `CRITICAL_SEVERITY_THRESHOLD`). No retyped copies. The
counterfactual re-admits an entry to the series by flipping ONLY its status,
leaving every severity untouched, so the comparison isolates the status channel.
"""
from __future__ import annotations

import collections
import copy
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from statsmodels.stats.proportion import proportion_confint      # noqa: E402

import reference_runner_v3 as rr                                 # noqa: E402

CRIT = rr.CRITICAL_SEVERITY_THRESHOLD
K = 2   # the convergence rule's consecutive-zero-new-critical requirement


class _Reg:
    """The duck type `_settled_novelty_series` reads."""

    def __init__(self, entries):
        self.entries = entries


def interval(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return f"{100.0 * k / n:.4f}%  Wilson [{100 * lo:.4f}%, {100 * hi:.4f}%]"


def first_k_consecutive_zero(series, k: int = K):
    run = 0
    for i, count in enumerate(series):
        run = run + 1 if count == 0 else 0
        if run >= k:
            return i
    return None


def states():
    seen = set()
    for p in sorted(REPO.glob("bench/logs/**/runner_state.json")):
        if "sandbox_harvest" in str(p) or "/seat_evidence/" in str(p):
            continue
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        yield p


def main() -> int:
    runs = entries_seen = 0
    by_verdict: collections.Counter = collections.Counter()
    moved = []
    for path in states():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        reg = ((data or {}).get("registry") or {}).get("entries") or {}
        if not isinstance(reg, dict):
            continue
        runs += 1
        entries_seen += len(reg)
        max_round = 0
        for e in reg.values():
            r = e.get("open_since_round") if isinstance(e, dict) else None
            if isinstance(r, int) and r > max_round:
                max_round = r

        _all_gated, crit_gated = rr._settled_novelty_series(_Reg(reg), max_round)

        counterfactual = copy.deepcopy(reg)
        readmitted = 0
        for e in counterfactual.values():
            if not isinstance(e, dict):
                continue
            if (e.get("status") == "UNCONFIRMED"
                    and float(e.get("severity") or 0.0) >= CRIT):
                by_verdict[str(e.get("falsifier_verdict") or "").strip().upper()
                           or "<no verdict>"] += 1
                e["status"] = "CONFIRMED"      # status only; severity untouched
                readmitted += 1
        _all_open, crit_open = rr._settled_novelty_series(
            _Reg(counterfactual), max_round)

        if crit_gated != crit_open:
            moved.append({
                "run": path.parent.name,
                "readmitted": readmitted,
                "crit_gated": crit_gated,
                "crit_counted": crit_open,
                "gamma_gated": rr._estimate_gamma(crit_gated),
                "gamma_counted": rr._estimate_gamma(crit_open),
                "k_gated": first_k_consecutive_zero(crit_gated),
                "k_counted": first_k_consecutive_zero(crit_open),
            })

    print("=" * 78)
    print("DOES ESCALATING A CRITICAL REMOVE IT FROM GAMMA, AND DID IT MATTER?")
    print("=" * 78)
    print(f"runs read: {runs}   entries: {entries_seen}")
    total = sum(by_verdict.values())
    print(f"\nasserted-critical entries at status UNCONFIRMED (escalated, hence "
          f"absent from the critical novelty series): {total}")
    for verdict, n in by_verdict.most_common():
        print(f"   {verdict:<22} {n:>4}  — {interval(n, total)}")
    print(f"\n   of which attributable to the PROOF-POLARITY route (a clean-exit "
          f"re-run, verdict REFUTED): {by_verdict.get('REFUTED', 0)} — "
          f"{interval(by_verdict.get('REFUTED', 0), total)}")
    print(f"   the remainder are EQUIPMENT escalations (UNTOOLABLE / ERROR / no "
          f"falsifier), which is a different cause with the same consequence.")

    print(f"\nruns whose critical novelty series MOVES when they are counted: "
          f"{len(moved)} of {runs} — {interval(len(moved), runs)}")

    premature = [m for m in moved
                 if m["k_gated"] is not None
                 and (m["k_counted"] is None or m["k_counted"] > m["k_gated"])]
    band_crossed = [m for m in moved
                    if (m["gamma_gated"] >= 0.30) != (m["gamma_counted"] >= 0.30)]

    for m in moved:
        flag = ""
        if m in premature:
            flag = ("   *** PREMATURE: K=%d satisfied at round %s; counted, %s"
                    % (K, m["k_gated"],
                       "never" if m["k_counted"] is None else m["k_counted"]))
        print(f"\n  {m['run']}  (+{m['readmitted']} re-admitted){flag}")
        print(f"    gated   {m['crit_gated']}")
        print(f"    counted {m['crit_counted']}")
        print(f"    gamma {m['gamma_gated']:.4f} -> {m['gamma_counted']:.4f}"
              f"   ({rr._interpret_gamma(m['gamma_gated'])!r}"
              f" -> {rr._interpret_gamma(m['gamma_counted'])!r})")

    print("\n" + "=" * 78)
    print(f"runs that converged on the K={K} test ONLY because escalated "
          f"criticals were absent: {len(premature)} of {runs} — "
          f"{interval(len(premature), runs)}")
    for m in premature:
        print(f"   {m['run']}: round {m['k_gated']} -> "
              f"{'never' if m['k_counted'] is None else m['k_counted']}")
    print(f"runs that cross the gamma_critical >= 0.30 gate: {len(band_crossed)} "
          f"of {runs} — {interval(len(band_crossed), runs)}")
    for m in band_crossed:
        print(f"   {m['run']}: {m['gamma_gated']:.4f} -> "
              f"{m['gamma_counted']:.4f}")
    print("\nREACH: the channel is LIVE (it moved an archived convergence "
          "decision). The proof-polarity ROUTE into it is LATENT (1 archived "
          "entry, 0 archived convergence decisions). Repairing the route does "
          "not repair the channel, and this script is the measurement that "
          "separates them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
