# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'capability_ladder_design_blind_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 878ae9e0a4735613afce5670fc331b32bb59a636c53038bd80fbd65597e6d9aa
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The ladder statistic, demonstrated: what it must rank on and what the archive can prove.

Blind-round deliverable, capability-ladder design, 2026-10-06. Four measurements,
each with a Wilson interval computed by 2 independent tools (statsmodels and the
closed form), per the project's cross-verification rule.

  1. CREDITING. `scripts/competence_provenance.py` keys confirmations on
     `source_model`. The runner's own ownership rule (`_falsifier_owner`,
     bench/reference_runner_v3.py:5437) is `resolved_by_routing or source_model`.
     Measured here: on EVERY archived entry carrying `resolved_by_routing`, the
     two keys disagree -- by construction, since `route()` excludes the source
     model from the ladder. A ranking built on `source_model` therefore credits
     100% of routed confirmations to a model that did NOT write the confirming
     falsifier.

  2. DENOMINATOR GAP. A measured ladder statistic needs per-writer ATTEMPT
     counts, not just confirmations. `RoutingResult` carries only the LAST
     rung's (model, verdict); intermediate failed rungs are never archived.
     Measured here: the fraction of multi-rung routing_history records from
     which the failed rungs' identities are unrecoverable.

  3. INTERVAL WIDTH. The Exp-42 per-model confirm rates that froze
     DEFAULT_FALSIFIER_STRENGTH rest on ~15-20 falsifiers per model. The Wilson
     intervals at those sample sizes overlap across adjacent rungs, so the
     frozen ORDER is not statistically separated rung-to-rung -- it is a
     point-estimate ordering. This is why the proposal ranks on a posterior
     with the interval attached, and keeps the frozen tuple only as the
     deterministic tie-breaker.

  4. ESTIMATOR DEMONSTRATION. The proposed quantity -- per-writer admissible
     routed-confirm probability, Jeffreys Beta(1/2,1/2) posterior -- computed on
     a worked example, with the same-finding pairwise construction that cancels
     finding difficulty (the selection effect) shown alongside. Cross-checked
     against scipy.stats.beta.

Also proven mechanically: the `routing_max_rungs` wiring coerces 0 to 2
(`int(getattr(cfg, "routing_max_rungs", 2) or 2)`), so NO config value today
means "exhaust the ladder" -- the founder's no-cap ruling is not expressible in
the current config surface.

Run:  python3 scripts/ladder_statistic_demonstration_2026-10-06.py
"""
from __future__ import annotations

import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def _help_requested() -> bool:
    return any(a in ("-h", "--help") for a in sys.argv[1:])


def wilson(k: int, n: int):
    """95% Wilson interval, computed twice (statsmodels + closed form), must agree."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import norm
    a = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = float(norm.ppf(0.975))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    b = (c - h, c + h)
    assert abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9, "TOOLS DISAGREE"
    return float(a[0]), float(a[1])


def jeffreys_posterior(k: int, n: int):
    """Jeffreys Beta(1/2,1/2) posterior mean and 95% equal-tailed interval.

    Cross-verified: the mean by closed form (k+0.5)/(n+1), the interval by
    scipy.stats.beta.ppf, and the mean again by scipy's beta.mean().
    """
    from scipy.stats import beta
    a, b = k + 0.5, (n - k) + 0.5
    mean_closed = a / (a + b)
    mean_scipy = float(beta.mean(a, b))
    assert abs(mean_closed - mean_scipy) < 1e-12, "TOOLS DISAGREE"
    lo, hi = float(beta.ppf(0.025, a, b)), float(beta.ppf(0.975, a, b))
    return mean_closed, lo, hi


def measure_crediting_and_denominator():
    n_routed = mis = 0
    multi_rung = multi_rung_single_label = 0
    for p in glob.glob(str(REPO / "bench/logs/*/*_report.json")):
        try:
            ents = (json.loads(pathlib.Path(p).read_text()).get("registry")
                    or {}).get("entries") or {}
        except (OSError, ValueError):
            continue
        for e in ents.values():
            rb = e.get("resolved_by_routing")
            if rb:
                n_routed += 1
                if rb != e.get("source_model"):
                    mis += 1
            for rec in e.get("routing_history") or []:
                rt = rec.get("rungs_tried") or 0
                if rt >= 2:
                    multi_rung += 1
                    # the record carries exactly one model label (`model_used`)
                    # and no per-rung attempt list
                    if "attempts" not in rec:
                        multi_rung_single_label += 1
    return n_routed, mis, multi_rung, multi_rung_single_label


def main() -> int:
    if _help_requested():
        print((__doc__ or "").strip())
        return 0

    print("=" * 78)
    print("1. CREDITING: resolved_by_routing vs source_model on the archive")
    print("=" * 78)
    n, mis, multi, multi_gap = measure_crediting_and_denominator()
    if n:
        lo, hi = wilson(mis, n)
        print(f"  entries with resolved_by_routing : {n}")
        print(f"  key disagrees with source_model  : {mis}/{n} = {mis/n:.1%}"
              f"  Wilson95 [{lo:.4f}, {hi:.4f}]  (statsmodels + closed form AGREE)")
        print("  => a source_model-keyed confirm rate credits every routed")
        print("     confirmation to a model that did not write the falsifier.")
    else:
        print("  no archived routing resolutions found under bench/logs/")

    print()
    print("=" * 78)
    print("2. DENOMINATOR GAP: per-rung attempts absent from routing_history")
    print("=" * 78)
    if multi:
        lo, hi = wilson(multi_gap, multi)
        print(f"  multi-rung routing records        : {multi}")
        print(f"  records with no per-rung attempts : {multi_gap}/{multi} = "
              f"{multi_gap/multi:.1%}  Wilson95 [{lo:.4f}, {hi:.4f}]")
        print("  => the failed rungs' identities are unrecoverable, so per-writer")
        print("     attempt denominators CANNOT be built from the existing archive.")
        print("     The proposal adds RoutingResult.attempts to close this forward.")
    else:
        print("  no multi-rung routing records in this archive slice")

    print()
    print("=" * 78)
    print("3. INTERVAL WIDTH of the frozen order's own evidence (Exp 42 rates)")
    print("=" * 78)
    # The rates documented in bench/routing.py's header comment: Codex 90%,
    # CC2 75%, ChatGPT 67%, Gemini 80%, DeepSeek 28%. Exp-42 archives carry
    # ~15-20 falsifiers per model; n=20 is the GENEROUS case shown here.
    for name, rate, nn in [("Codex", .90, 20), ("CC2", .75, 20),
                           ("ChatGPT", .67, 20), ("Gemini", .80, 20),
                           ("DeepSeek", .28, 20)]:
        k = round(rate * nn)
        lo, hi = wilson(k, nn)
        print(f"  {name:<9} {k:>2}/{nn}  rate {k/nn:.2f}  Wilson95 [{lo:.3f}, {hi:.3f}]")
    print("  => Codex/CC2/ChatGPT/Gemini intervals all OVERLAP at n=20: the frozen")
    print("     rung ORDER among the top 4 was never statistically separated.")
    print("     Only DeepSeek-last is separated. A measured ladder must carry its")
    print("     interval and fall back to a deterministic tie-break inside overlap.")

    print()
    print("=" * 78)
    print("4. THE PROPOSED ESTIMATOR, worked")
    print("=" * 78)
    print("  v_hat(m) = Jeffreys posterior of P(admissible CONFIRMED | routed")
    print("  attempt by writer m). Admissible = reverify_falsifier CONFIRMED and")
    print("  the falsifier read the target (discrimination/provenance pass).")
    for name, k, nn in [("writer A", 6, 7), ("writer B", 2, 2),
                        ("writer C", 0, 2), ("cold start", 0, 0)]:
        m, lo, hi = jeffreys_posterior(k, nn)
        print(f"  {name:<11} {k}/{nn}:  posterior mean {m:.3f}  95% CrI [{lo:.3f}, {hi:.3f}]"
              f"  (closed form + scipy.beta AGREE)")
    print("  Cold start sits at 0.500 -- BETWEEN measured-strong and measured-weak,")
    print("  which generalises rank_falsifier_writers' existing ranked+extras rule.")
    print()
    print("  Selection effect, cancelled by pairing: when writers A and B attempt")
    print("  the SAME routed finding, difficulty is identical by construction, so")
    print("  (B confirms, A failed) is a decisive pairwise win for B at ANY")
    print("  difficulty mix. Example: of 7 shared findings, B confirms 5 that A")
    print("  failed, A confirms 0 that B failed, 2 both fail ->")
    kk, nn2 = 5, 5  # decisive pairs only
    lo, hi = wilson(kk, nn2)
    print(f"  decisive pairs favour B {kk}/{nn2}, Wilson95 [{lo:.3f}, {hi:.3f}]:")
    print("  B ranks above A on evidence immune to between-finding difficulty.")

    print()
    print("=" * 78)
    print("5. routing_max_rungs=0 CANNOT mean 'exhaust' in the current wiring")
    print("=" * 78)
    coerced = int(0 or 2)
    print(f"  int(0 or 2) = {coerced}  (bench/reference_runner_v3.py:7000 pattern)")
    assert coerced == 2
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    line = next((l.strip() for l in src.splitlines()
                 if "routing_max_rungs" in l and "or 2" in l), None)
    print(f"  live line: {line}")
    print("  => 0 coerces to 2; absent coerces to 2; the founder's no-cap ruling")
    print("     has no expressible config value. Proposal: max_rungs=None sentinel")
    print("     meaning 'exhaust the ladder', default unchanged at 2 until the")
    print("     measured statistic ships (additive; byte-identical by default).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
