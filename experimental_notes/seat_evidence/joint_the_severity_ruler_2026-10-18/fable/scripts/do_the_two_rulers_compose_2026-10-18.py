# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_severity_ruler_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 919e4c38cbed3895b9ffe2754eaf0bcf9ee1ea530f0b887b46abc188ceec098d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Do the 2 de-coarsening fixes COMPOSE? Measured, not judged.

Joint round 2026-10-18. The two fixes under test, reconstructed from the blind
replies because the sandbox was torn down between rounds:

  * cc2's: replace the hard indicator 1[severity >= 0.7] inside the critical
    novelty count with its expectation under the measured instrument noise,
    w = Phi((sev - 0.7) / sigma), sigma = 0.1419 (docs/MATHEMATICAL_APPENDIX.md
    line 765, 273 duplicate pairs), with falsifier_verdict == REFUTED
    short-circuiting to 0.0. Quiescence: all tail expected-counts < 0.5.
  * fable's: replace the single asserted severity with the median over the
    direct codiscovery star (the entry plus every `from_canonical` named by a
    via=="codiscovery" occasion, self-reference refused), then apply the SAME
    hard indicator. Informative-only in the blind round.
  * the composition: Phi((star_median - 0.7) / (sigma * c_k)) where c_k is the
    sampling-SD constant of the median of k independent normal assessments --
    pooling shrinks the noise term, smoothing carries what remains.

Every series is produced through the production path where one exists:
`_settled_novelty_series` for both indicator rulers (hard and pooled), and
`_estimate_gamma` for every gamma. The soft rulers mirror the production
population filter; the mirror is verified value-for-value at sigma -> 0
against `_settled_novelty_series` on every catalogue.
"""
from __future__ import annotations

import json
import math
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

import numpy as np  # noqa: E402

import reference_runner_v3 as rr  # noqa: E402

SIGMA = 0.1419  # docs/MATHEMATICAL_APPENDIX.md line 765, bootstrap CI [0.1241, 0.1575]
THR = rr.CRITICAL_SEVERITY_THRESHOLD  # 0.7, pre-registered, frozen


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def median_sd_constants(max_k: int) -> dict:
    """c_k = SD(median of k std normals). k=1 exact 1.0; k=2 exact 1/sqrt(2)
    (median of 2 IS the mean of 2). k>=3 by seeded Monte Carlo, 4e6 draws."""
    out = {1: 1.0, 2: 1.0 / math.sqrt(2.0)}
    rng = np.random.default_rng(20261018)
    for k in range(3, max_k + 1):
        draws = rng.standard_normal((4_000_000, k))
        out[k] = float(np.median(draws, axis=1).std(ddof=0))
    return out


class _Reg:
    def __init__(self, entries):
        self.entries = entries


def star_members(cid: str, entries: dict) -> list:
    """Direct codiscovery star of cid: itself plus every distinct
    from_canonical named by a via=='codiscovery' occasion. Self-reference
    refused (the `from_canonical` fallback case)."""
    e = entries[cid]
    members = [cid]
    for occ in e.get("occasions") or []:
        if occ.get("via") != "codiscovery":
            continue
        fc = occ.get("from_canonical")
        if fc and fc != cid and fc in entries and fc not in members:
            members.append(fc)
    return members


def pooled_severity(cid: str, entries: dict):
    ms = star_members(cid, entries)
    sevs = [float(entries[m].get("severity") or 0.0) for m in ms]
    return statistics.median(sevs), len(ms)


def soft_series(entries: dict, max_round: int, sev_of, sigma_of):
    """Mirror of _settled_novelty_series' population filter with the indicator
    replaced by Phi; REFUTED falsifier verdict annihilates to 0.0."""
    s = [0.0] * (max_round + 1)
    for cid, e in entries.items():
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in rr._NON_NOVEL_TERMINAL_STATUSES:
            continue
        if str(e.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
            continue  # annihilation: a disproved finding is worth exactly 0
        s[r] += phi((sev_of(cid, e) - THR) / sigma_of(cid, e))
    return s


def indicator_series_check(entries: dict, max_round: int):
    """sigma -> 0 limit of the mirror must equal the production series."""
    s = [0] * (max_round + 1)
    for cid, e in entries.items():
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in rr._NON_NOVEL_TERMINAL_STATUSES:
            continue
        if (e.get("severity") or 0.0) >= THR:
            s[r] += 1
    return s


def discover_runs():
    runs = []
    for p in sorted((ROOT / "bench" / "logs").glob("*/runner_state.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        reg = d.get("registry") or {}
        entries = reg.get("entries") if isinstance(reg, dict) else None
        if not entries:
            continue
        nc = d.get("novelty_counts") or []
        max_round = max(
            len(nc) - 1,
            max((e.get("open_since_round") or 0) for e in entries.values()),
        )
        if max_round < 0:
            continue
        runs.append((p.parent.name, entries, max_round))
    return runs


def main():
    runs = discover_runs()
    max_k = 1
    for _, entries, _ in runs:
        for cid in entries:
            max_k = max(max_k, len(star_members(cid, entries)))
    CK = median_sd_constants(max_k)
    print(f"catalogues discovered: {len(runs)}; max star size: {max_k}")
    print("median-of-k SD constants:",
          {k: round(v, 4) for k, v in sorted(CK.items())})

    rows = []
    mirror_mismatch = 0
    for name, entries, max_round in runs:
        reg = _Reg(entries)
        _, hard = rr._settled_novelty_series(reg, max_round)
        if indicator_series_check(entries, max_round) != hard:
            mirror_mismatch += 1

        # fable's pooled ruler through the PRODUCTION counter
        pooled_entries = {
            cid: {**e, "severity": pooled_severity(cid, entries)[0]}
            for cid, e in entries.items()
        }
        _, pooled = rr._settled_novelty_series(_Reg(pooled_entries), max_round)

        # cc2's soft ruler
        soft = soft_series(entries, max_round,
                           lambda cid, e: float(e.get("severity") or 0.0),
                           lambda cid, e: SIGMA)
        # the composition
        comp = soft_series(
            entries, max_round,
            lambda cid, e: pooled_severity(cid, entries)[0],
            lambda cid, e: SIGMA * CK[pooled_severity(cid, entries)[1]])

        def tail(s):
            return s[-3:] if len(s) >= 3 else list(s)

        row = {
            "run": name,
            "rounds": max_round + 1,
            "k2_entries": sum(1 for cid in entries
                              if len(star_members(cid, entries)) >= 2),
            "hard": hard, "pooled": pooled,
            "soft": [round(x, 4) for x in soft],
            "comp": [round(x, 4) for x in comp],
            "g_hard": round(rr._estimate_gamma(hard), 4),
            "g_pooled": round(rr._estimate_gamma(pooled), 4),
            "g_soft": round(rr._estimate_gamma(soft), 4),
            "g_comp": round(rr._estimate_gamma(comp), 4),
            "q_hard": all(c == 0 for c in tail(hard)) and bool(tail(hard)),
            "q_pooled": all(c == 0 for c in tail(pooled)) and bool(tail(pooled)),
            "q_soft": all(w < 0.5 for w in tail(soft)) and bool(tail(soft)),
            "q_comp": all(w < 0.5 for w in tail(comp)) and bool(tail(comp)),
        }
        rows.append(row)

    print(f"mirror mismatches (sigma->0 vs production): {mirror_mismatch}")
    print()
    hdr = ("run", "k>=2", "q_hard", "q_pool", "q_soft", "q_comp",
           "g_hard", "g_pool", "g_soft", "g_comp")
    print(("{:<58}" + "{:>8}" * 9).format(*hdr))
    for r in rows:
        print(("{:<58}" + "{:>8}" * 9).format(
            r["run"][:57], r["k2_entries"],
            str(r["q_hard"]), str(r["q_pooled"]),
            str(r["q_soft"]), str(r["q_comp"]),
            r["g_hard"], r["g_pooled"], r["g_soft"], r["g_comp"]))

    flips_soft = [r["run"] for r in rows if r["q_soft"] != r["q_hard"]]
    flips_pooled = [r["run"] for r in rows if r["q_pooled"] != r["q_hard"]]
    flips_comp_vs_soft = [r["run"] for r in rows if r["q_comp"] != r["q_soft"]]
    g_pooled_moves = [r["run"] for r in rows if r["g_pooled"] != r["g_hard"]]
    g_comp_moves = [r["run"] for r in rows if r["g_comp"] != r["g_soft"]]
    oneway_soft = [r["run"] for r in rows if r["q_soft"] and not r["q_hard"]]
    oneway_comp = [r["run"] for r in rows if r["q_comp"] and not r["q_hard"]]

    print()
    print(f"quiescence: soft differs from hard on {len(flips_soft)}: {flips_soft}")
    print(f"quiescence: pooled differs from hard on {len(flips_pooled)}: {flips_pooled}")
    print(f"quiescence: COMPOSED differs from SOFT on {len(flips_comp_vs_soft)}: {flips_comp_vs_soft}")
    print(f"gamma: pooled differs from hard on {len(g_pooled_moves)}: {g_pooled_moves}")
    print(f"gamma: composed differs from soft on {len(g_comp_moves)}: {g_comp_moves}")
    print(f"ONE-WAY violations, soft permits where hard refuses: {oneway_soft}")
    print(f"ONE-WAY violations, composed permits where hard refuses: {oneway_comp}")

    crossers = []
    for name, entries, max_round in runs:
        for cid, e in entries.items():
            if e.get("status") in rr._NON_NOVEL_TERMINAL_STATUSES:
                continue
            if str(e.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
                continue
            med, k = pooled_severity(cid, entries)
            if k < 2:
                continue  # k=1: composed weight IS cc2's weight, identically
            sev = float(e.get("severity") or 0.0)
            w_soft = phi((sev - THR) / SIGMA)
            w_comp = phi((med - THR) / (SIGMA * CK[k]))
            if (w_soft >= 0.5) != (w_comp >= 0.5):
                crossers.append((name, cid, k, sev, med,
                                 round(w_soft, 4), round(w_comp, 4),
                                 str(e.get("falsifier_verdict") or "")))
    print(f"\nk>=2 entries where composed and soft disagree at the 0.5 line: {len(crossers)}")
    for c in crossers:
        print("  ", c)
    return rows


if __name__ == "__main__":
    main()
