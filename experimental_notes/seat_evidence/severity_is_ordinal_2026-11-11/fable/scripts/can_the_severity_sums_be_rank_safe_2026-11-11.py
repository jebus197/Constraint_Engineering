# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_is_ordinal_2026-11-11', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a46f692819078ba81f3e8fe797d3d41baf454758fe79a5ae6ec62c15560b6c4d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Can kappa_set's severity SUMS become an order statistic without changing the gate?

THE QUESTION (severity_is_ordinal round, 2026-11-11, brief section 8). The brief's
P2 holds severity ORDINAL, on which a sum or mean of magnitudes is inadmissible
(Stevens 1946). The two magnitude sums in the live convergence machinery are
`bench/dm/_convergence.py` `_weighted_novel_severity` (the `sum(...)` over novel
classes) and `kappa_set` (the `sum(...)` over cumulative classes). The brief asks
whether those sums can be replaced by an order statistic WITHOUT changing what
`ConvergenceDetector.converged(r)` decides on any archived registry — and rules
that an answer asserting it can, without running it, has not answered.

THE MEASUREMENT. Every archived report under `bench/logs/` whose `rounds[*].findings`
carry (model_id, flaw_class, severity, description) is replayed through the stock
`ConvergenceDetector` and through three variants that differ ONLY in the per-class
weight entering kappa_set's numerator and denominator:

  stock     weight = aggregated_severity           (magnitude — the live code)
  count     weight = 1                             (order-free count; invariant)
  rank      weight = mid-rank of the class severity within the cumulative
            classes of that round, scaled to (0, 1]  (a function of ORDER only,
            so invariant under every strictly increasing relabelling)
  material  weight = 1 if aggregated_severity >= 0.7 else 0  (count above the
            frozen critical cut; invariant when the cut is re-frozen per scale
            as a LEVEL, which is how a rank-safe cut must be carried)

Suppression weights w(f) (similarity-derived, not severity-derived) are applied
identically in all four, so the comparison isolates the severity weighting.
The severity VETO (any novel class >= eta_veto) is already an order statistic and
is identical in all four. gamma_hat (`estimate_gamma`) reads class COUNTS, never
severity, and is bitwise untouched — gamma is load-bearing and is NOT demoted here.

Output: per variant, over every (report, round) pair, how many `converged(r)`
decisions differ from stock, and how many reports change their FIRST convergence
round. A variant with 0 differences is a committed measurement that the sum can
be replaced by that order statistic with the gate's archived behaviour preserved.

Usage: python3 scripts/can_the_severity_sums_be_rank_safe_2026-11-11.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from bench.dm._types import Finding, DynamicManagementConfig          # noqa: E402
from bench.dm._convergence import ConvergenceDetector                 # noqa: E402

CRIT = 0.7  # CRITICAL_SEVERITY_THRESHOLD, bench/reference_runner_v3.py


class WeightedDetector(ConvergenceDetector):
    """ConvergenceDetector whose kappa_set weight per class is pluggable.

    weight_mode: "stock" | "count" | "rank" | "material".
    Everything else — clustering, suppression, veto, kappa_rate, kappa_adopt,
    estimate_gamma, converged — is inherited unchanged.
    """

    def __init__(self, config, weight_mode: str):
        super().__init__(config)
        self.weight_mode = weight_mode

    def _class_weight(self, ec, cumulative):
        if self.weight_mode == "stock":
            return ec.aggregated_severity
        if self.weight_mode == "count":
            return 1.0
        if self.weight_mode == "material":
            return 1.0 if ec.aggregated_severity >= CRIT else 0.0
        if self.weight_mode == "rank":
            sevs = sorted(c.aggregated_severity for c in cumulative)
            n = len(sevs)
            if n == 0:
                return 1.0
            below = sum(1 for s in sevs if s < ec.aggregated_severity)
            equal = sum(1 for s in sevs if s == ec.aggregated_severity)
            return (below + (equal + 1) / 2.0) / n  # mid-rank in (0, 1]
        raise ValueError(self.weight_mode)

    # Override the two magnitude sums and nothing else.
    def kappa_set(self, round_idx: int) -> float:
        novel = self._novel_classes(round_idx)
        cumulative = self.get_cumulative_classes(round_idx)
        prior_findings = []
        if round_idx > 0:
            for ec in self.get_cumulative_classes(round_idx - 1):
                prior_findings.extend(ec.members)
        num = 0.0
        for ec in novel:
            if prior_findings:
                w = max(self._suppression_weight(m, prior_findings)
                        for m in ec.members) if ec.members else 1.0
            else:
                w = 1.0
            num += w * self._class_weight(ec, cumulative)
        den = sum(self._class_weight(ec, cumulative) for ec in cumulative)
        den += self.config.epsilon_conv
        return 1.0 - (num / den)


def load_rounds(report_path: str):
    with open(report_path, encoding="utf-8") as fh:
        j = json.load(fh)
    rounds = []
    for r in j.get("rounds", []):
        fs = []
        for k, f in enumerate(r.get("findings", [])):
            try:
                fs.append(Finding(
                    finding_id="%s_r%s_%d" % (f.get("model_id", "m"), r.get("round", 0), k),
                    model_id=str(f.get("model_id", "m")),
                    round_idx=int(r.get("round", 0)),
                    flaw_class=int(f.get("flaw_class", 0)),
                    severity=float(f.get("severity", 0.0)),
                    abstraction_index=0.5,
                    description=str(f.get("description", ""))[:400],
                ))
            except (TypeError, ValueError):
                return None
        rounds.append((int(r.get("round", 0)), fs))
    return rounds if rounds else None


def replay(rounds, mode: str):
    cfg = DynamicManagementConfig()
    cd = WeightedDetector(cfg, mode) if mode != "stock" else ConvergenceDetector(cfg)
    decisions = []
    for rd, fs in rounds:
        cd.add_round_findings(rd, fs, duration=1.0, adoption_delta=0.0)
        decisions.append(bool(cd.converged(rd)))
    return decisions


def main() -> None:
    reports = []
    for fp in sorted(glob.glob(os.path.join(REPO, "bench", "logs", "*", "*.json"))):
        if os.path.getsize(fp) > 50_000_000:
            continue
        try:
            with open(fp, encoding="utf-8") as fh:
                j = json.load(fh)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        rs = j.get("rounds") if isinstance(j, dict) else None
        if (isinstance(rs, list) and rs and isinstance(rs[0], dict)
                and rs[0].get("findings")
                and isinstance(rs[0]["findings"][0], dict)
                and "severity" in rs[0]["findings"][0]
                and "flaw_class" in rs[0]["findings"][0]):
            reports.append(fp)

    print("replayable archived reports: %d" % len(reports))
    skipped = 0
    stats = {m: {"diff_rounds": 0, "diff_reports": set(), "first_shift": 0}
             for m in ("count", "rank", "material")}
    total_rounds = 0

    for fp in reports:
        rounds = load_rounds(fp)
        if rounds is None:
            skipped += 1
            continue
        stock = replay(rounds, "stock")
        total_rounds += len(stock)
        first_stock = stock.index(True) if True in stock else None
        for mode in ("count", "rank", "material"):
            var = replay(rounds, mode)
            diffs = [i for i, (a, b) in enumerate(zip(stock, var)) if a != b]
            if diffs:
                stats[mode]["diff_rounds"] += len(diffs)
                stats[mode]["diff_reports"].add(os.path.basename(os.path.dirname(fp)))
            first_var = var.index(True) if True in var else None
            if first_var != first_stock:
                stats[mode]["first_shift"] += 1

    print("reports skipped (malformed findings): %d" % skipped)
    print("(report, round) decision pairs compared per variant: %d" % total_rounds)
    for mode in ("count", "rank", "material"):
        s = stats[mode]
        print("\nvariant %r:" % mode)
        print("  converged() decisions differing from stock : %d" % s["diff_rounds"])
        print("  reports with any differing decision        : %d" % len(s["diff_reports"]))
        for name in sorted(s["diff_reports"]):
            print("    %s" % name)
        print("  reports whose FIRST convergence round moved: %d" % s["first_shift"])

    # NON-VACUITY DIAGNOSTIC (the section 3.7 lesson: an instrument that cannot
    # flip is not a measurement). Report how often the gate fired and how often
    # kappa_set was the binding minimum, so a zero-difference verdict is shown
    # to have been exposed to real decision boundaries.
    conv_true = ks_bind = ks_near = veto_n = 0
    for fp in reports:
        rounds = load_rounds(fp)
        if rounds is None:
            continue
        cfg = DynamicManagementConfig()
        cd = ConvergenceDetector(cfg)
        for rd, fs in rounds:
            cd.add_round_findings(rd, fs, duration=1.0, adoption_delta=0.0)
            ks = cd.kappa_set(rd)
            kr = max(0.0, cd.kappa_rate(rd))
            ka = cd.kappa_adopt(rd)
            if cd.converged(rd):
                conv_true += 1
            if cd._veto(rd):
                veto_n += 1
            if ks == min(ks, kr, ka):
                ks_bind += 1
            if abs(ks - cfg.tau_kappa) <= 0.05:
                ks_near += 1
    print("\nnon-vacuity: converged()==True in %d rounds; veto fired in %d; "
          "kappa_set binding min in %d; kappa_set within 0.05 of tau_kappa in %d"
          % (conv_true, veto_n, ks_bind, ks_near))

    clean = [m for m in ("count", "rank", "material")
             if stats[m]["diff_rounds"] == 0 and stats[m]["first_shift"] == 0]
    if clean:
        print("\nVERDICT: variants %s reproduce every archived converged() "
              "decision. The kappa_set severity sums CAN be replaced by an order "
              "statistic with archived gate behaviour preserved (for these variants)." % clean)
    else:
        print("\nVERDICT: no tested order statistic reproduces every archived "
              "decision. Replacing the sums CHANGES the gate on the archive; any "
              "ordinal repair of kappa_set is a semantic change needing a run-level "
              "decision, not a drop-in substitution.")


if __name__ == "__main__":
    main()
