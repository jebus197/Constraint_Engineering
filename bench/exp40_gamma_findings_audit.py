#!/usr/bin/env python3
"""Exp 40 findings audit + production-faithful gamma recompute.

Two questions the founder posed:
  Q1. Recompute gamma through the runner's OWN post-reconciliation
      novelty definition (not an offline finding-list extraction) so the
      [8,4,0,3,1,1,1]-vs-zero-critical-tail contradiction is resolved
      and the dual-series numbers are trustworthy.
  Q2. Audit what is actually being found across Exp 40 runs: how
      valuable are the findings, and is there STILL meaningful residual
      churn in the series gamma is fed (despite the post-reconciliation
      strip)?

Production-true inputs: the registry, the runner's post-reconciliation
novelty rule (open_since_round==r AND status NOT in the non-novel
terminal set), the runner's actual _estimate_gamma, the runner's
sev>=0.7 critical convention. The ONLY estimate is the residual
near-duplicate rate among canonicals (offline difflib ratio; the
production _finding_similarity lives in the immune pipeline and would
give the definitive figure — this is a directional proxy, labelled).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from bench.reference_runner_v3 import _estimate_gamma  # noqa: E402

# Runner's post-reconciliation non-novel terminal set (verbatim from
# reference_runner_v3.py ~4909) — what is stripped before gamma sees it.
_NON_NOVEL_TERMINAL = {"MERGED", "DUPLICATE", "UNCONFIRMED", "REFUTED"}
CRIT = 0.7  # runner's hardcoded critical-severity convention (NOT a
            # documented schema boundary — see appendix sev thresholds
            # 0.0/0.3/0.5; flagged, applied as the runner applies it)

RUNS = {
    "plan-F (slice, apply-back ON, converged R6)":
        "bench/logs/exp40_slice_admissibility_20260516T223952Z/"
        "exp40_slice_admissibility_report.json",
    "Exp40 R0-R28 (full file, the long non-converged arc)":
        "bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json",
}


def per_round_novelty(entries, max_round):
    """Runner-faithful: per round r, canonical entries whose
    open_since_round==r and post-reconciliation status is genuinely
    novel. Split all vs critical (sev>=0.7)."""
    alln = [0] * (max_round + 1)
    crit = [0] * (max_round + 1)
    for e in entries:
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in _NON_NOVEL_TERMINAL:
            continue
        alln[r] += 1
        if (e.get("severity") or 0) >= CRIT:
            crit[r] += 1
    return alln, crit


def residual_neardup_rate(descs, thr=0.82):
    """Offline directional proxy: fraction of canonical descriptions
    that are >= thr difflib-similar to an earlier canonical (i.e.
    near-duplicates that survived production reconciliation and are
    still counted as distinct novelty feeding gamma)."""
    seen = []
    dup = 0
    for d in descs:
        d = (d or "")[:600]
        if any(SequenceMatcher(None, d, s).ratio() >= thr for s in seen):
            dup += 1
        else:
            seen.append(d)
    return dup, len(descs)


for label, rel in RUNS.items():
    p = REPO / rel
    if not p.exists():
        print(f"\n### {label}\n  report missing: {rel}")
        continue
    rep = json.loads(p.read_text())
    e = rep["registry"]["entries"]
    vals = list(e.values()) if isinstance(e, dict) else e
    total_findings = rep.get("total_findings", "n/a")
    max_round = max((x.get("open_since_round") or 0) for x in vals)

    alln, crit = per_round_novelty(vals, max_round)
    g_all = _estimate_gamma(alln)
    g_crit = _estimate_gamma(crit)

    statuses = Counter(x.get("status", "?") for x in vals)
    sev = [x.get("severity") or 0 for x in vals]
    n = len(vals)
    sev_crit = sum(1 for s in sev if s >= CRIT)
    sev_mid = sum(1 for s in sev if 0.3 <= s < CRIT)
    sev_low = sum(1 for s in sev if s < 0.3)
    verified = sum(1 for x in vals if x.get("verified"))
    hasfix = sum(1 for x in vals if x.get("proposed_fix"))
    # value proxy: a finding is "substantive" if sev>=0.5 AND (verified
    # OR has a proposed fix) — i.e. a real, actionable defect.
    substantive = sum(1 for x in vals
                      if (x.get("severity") or 0) >= 0.5
                      and (x.get("verified") or x.get("proposed_fix")))
    # gamma-relevant canonicals (the post-reconciliation novel set that
    # actually feeds gamma) — residual near-dup among THOSE:
    g_rel = [x for x in vals if x.get("status") not in _NON_NOVEL_TERMINAL]
    dup, tot = residual_neardup_rate([x.get("description") for x in g_rel])
    n_stripped = sum(statuses[s] for s in _NON_NOVEL_TERMINAL if s in statuses)

    print(f"\n{'='*70}\n### {label}\n{'='*70}")
    print(f"raw findings={total_findings}  canonical={n}  "
          f"rounds=0..{max_round}  "
          f"non-novel-terminal stripped from gamma={n_stripped}")
    print(f"status: {dict(statuses)}")
    print(f"severity: critical(>=0.7)={sev_crit}  mid[0.3,0.7)={sev_mid}  "
          f"low(<0.3)={sev_low}")
    print(f"value: verified={verified}  has_fix={hasfix}  "
          f"substantive(sev>=0.5 & (verified|fix))={substantive}/{n} "
          f"= {substantive/n:.0%}")
    print(f"per-round novel ALL : {alln}")
    print(f"per-round novel CRIT: {crit}")
    print(f"production-faithful gamma  all-novelty = {g_all:.4f}")
    print(f"production-faithful gamma  critical    = {g_crit:.4f}")
    print(f"reported gamma_history tail            = "
          f"{[round(x,4) for x in rep.get('gamma_history', [])][-7:]}")
    print(f"RESIDUAL near-dup among gamma-relevant canonicals "
          f"(offline difflib>=0.82 proxy): {dup}/{tot} = "
          f"{(dup/tot if tot else 0):.0%}  "
          f"[production _finding_similarity would give the definitive #]")
