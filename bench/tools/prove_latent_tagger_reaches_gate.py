"""End-to-end proof that a latent tag reaches the convergence verdict.

A tag written to a registry entry proves nothing. What has to be shown is the
whole chain, at the point where it matters: tag -> eligibility -> demotion ->
the settled critical-novelty series -> gamma -> the two-sided gate's verdict.
Every function below is imported from the runner; none is reimplemented.

Run: python3 bench/tools/prove_latent_tagger_reaches_gate.py
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bench.latent_tagger import tag_registry  # noqa: E402
from bench.reference_runner_v2 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD,
    FindingRegistry,
    RunnerConfig,
    _apply_severity_calibration,
    _check_gamma_alt_convergence,
    _estimate_gamma,
    _is_demotion_eligible,
    _settled_novelty_series,
)


def build_registry() -> FindingRegistry:
    """Three demonstrated criticals, arranged so the gate verdict turns on the
    demotion and nothing else.

    C2 is latent, uncategorised, and opens in the FINAL round — so while it
    stands at critical severity it holds the zero-critical streak open and
    convergence is refused. Demoting it closes the streak and the run converges.

    C1 declares itself reachable and must never be demoted. C3 is latent too,
    but it is a data-loss finding: the never-demote interlock must refuse it,
    which is why it stays at 0.95 in every arm.
    """
    reg = FindingRegistry()
    reg.entries = {
        "C1": {
            "canonical_id": "C1", "severity": 0.85, "open_since_round": 2,
            "status": "CONFIRMED", "falsifier_verdict": "CONFIRMED",
            "description": "REACHABILITY: reachable from the default ingestion "
                           "path. verify() returns a stale verdict.",
            "proposed_fix": "",
        },
        "C2": {
            "canonical_id": "C2", "severity": 0.90, "open_since_round": 5,
            "status": "CONFIRMED", "falsifier_verdict": "CONFIRMED",
            "description": "REACHABILITY: no in-repo caller reaches this "
                           "overload. Off-by-one in the unused helper.",
            "proposed_fix": "",
        },
        "C3": {
            "canonical_id": "C3", "severity": 0.95, "open_since_round": 2,
            "status": "CONFIRMED", "falsifier_verdict": "CONFIRMED",
            "description": "REACHABILITY: no in-repo caller reaches it today, "
                           "but it corrupts the evidence chain when it runs.",
            "proposed_fix": "",
        },
    }
    return reg


def gate(reg: FindingRegistry, cfg: RunnerConfig, max_round: int):
    all_s, crit_s = _settled_novelty_series(reg, max_round)
    gamma_crit = _estimate_gamma(crit_s, min_rounds=cfg.min_rounds_for_gamma)
    ok, why = _check_gamma_alt_convergence(
        max_round, _estimate_gamma(all_s, cfg.min_rounds_for_gamma), crit_s, cfg,
        unresolved_critical=reg.unverified_critical_count(),
        contested=reg.contested_count(max_round, subcritical_exclusion=False),
        rho_churn=False, irreducible_queue=reg.irreducible_queue_count(),
        gamma_critical=gamma_crit, total_findings=len(reg.entries),
    )
    return crit_s, gamma_crit, ok, why


def run(label: str, *, tagger: bool, calibration: bool) -> None:
    reg = build_registry()
    cfg = RunnerConfig(experiment_name="proof", models=["CC2"])
    cfg.latent_tagger_enabled = tagger
    cfg.severity_calibration_enabled = calibration
    cfg.gamma_alt_earliest_round = 3
    cfg.gamma_alt_consecutive_zero_crit = 3
    max_round = 5

    print("=" * 76)
    print(f"{label}   (latent_tagger={tagger}, severity_calibration={calibration})")
    print("=" * 76)

    n_tagged = tag_registry(reg) if tagger else 0
    print(f"\n  1. TAG      {n_tagged} entr{'y' if n_tagged == 1 else 'ies'} "
          f"tagged latent")
    for cid, e in reg.entries.items():
        print(f"       {cid}  latent={str(e.get('latent')):5s} "
              f"category={e.get('finding_category', '') or '-':18s} "
              f"src={e.get('latent_source', '-')}")

    print("\n  2. ELIGIBLE (real _is_demotion_eligible)")
    for cid, e in reg.entries.items():
        print(f"       {cid}  {_is_demotion_eligible(e)}")

    n = _apply_severity_calibration(reg, cfg, max_round)
    print(f"\n  3. DEMOTE   {n} demoted by the real calibration sweep")
    for cid, e in reg.entries.items():
        if e.get("severity_calibrated"):
            print(f"       {cid}  {e['severity_original']} -> {e['severity']}  "
                  f"(retained, reason recorded)")
        else:
            print(f"       {cid}  {e['severity']} unchanged")

    crit_s, gamma_crit, ok, why = gate(reg, cfg, max_round)
    n_crit = sum(1 for e in reg.entries.values()
                 if e["severity"] >= CRITICAL_SEVERITY_THRESHOLD)
    print(f"\n  4. SERIES   critical-novelty series the gate reads: {crit_s}")
    print(f"              entries still >= {CRITICAL_SEVERITY_THRESHOLD}: {n_crit}")
    print(f"\n  5. GAMMA    gamma_critical = {gamma_crit:.3f}")
    print(f"\n  6. VERDICT  converged={ok}")
    print(f"              {why}\n")


if __name__ == "__main__":
    print("\nPROOF: does a latent tag change the convergence verdict?\n")
    run("A — both gated OFF (the shipped default)",
        tagger=False, calibration=False)
    run("B — tagger ON, calibration OFF (observational only)",
        tagger=True, calibration=False)
    run("C — both ON (the mechanism live)",
        tagger=True, calibration=True)
    print("=" * 76)
    print("""READ THIS BEFORE CONCLUDING ANYTHING

The registry above is CONSTRUCTED. Its three findings carry an explicit
REACHABILITY field, which is what the tagger is built to read. That is the
point of the demonstration: it proves the wiring is live end to end — a tag
becomes an eligibility, an eligibility becomes a demotion, a demotion leaves
the critical series, and the series changes gamma and the gate's verdict.

It proves NOTHING about whether real panels emit that field. They do not.
Across the 293 archival findings of Exp 44-49, zero carry a reachability
field and one carries an explicit prose latency claim. Run
bench/validate_latent_tagger.py for that measurement.""")
    print("=" * 76)
