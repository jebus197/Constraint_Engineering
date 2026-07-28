"""DECISIVE replay test (T2): feed Exp 42's RAW per-round model findings through the
dormant dm ConvergenceDetector + DiminishingReturnsDetector and ask whether our own
already-built machinery recognises convergence where the inline path failed.

Honest-input contract: we feed `rounds[r].findings` (the actual model output each round,
including all re-finds) — NOT the pre-deduplicated registry — so the detectors' own
content-clustering is what is under test. abstraction_index is unavailable in the log and
proxied at 0.5 (affects DRD yield/mu only, not ConvergenceDetector kappa).

Run: python3 bench/replay_exp42_convergence.py
"""
from __future__ import annotations
import json, os, sys
sys.path.insert(0, ".")
from bench.dm._types import Finding, DynamicManagementConfig
from bench.dm._convergence import ConvergenceDetector
from bench.dm._diminishing_returns import DiminishingReturnsDetector

RUN = "bench/logs/exp42_composer_takeupslack_20260607T154745Z"
REPORT = os.path.join(RUN, "exp42_composer_takeupslack_report.json")
CRIT = 0.7


def load_rounds():
    j = json.load(open(REPORT))
    rounds = []
    for r in j["rounds"]:
        fs = []
        for k, f in enumerate(r["findings"]):
            fs.append(Finding(
                finding_id=f"{f['model_id']}_r{r['round']}_{k}",
                model_id=f["model_id"], round_idx=r["round"],
                flaw_class=f["flaw_class"], severity=f["severity"],
                abstraction_index=0.5, description=f["description"],
                falsifier_code=""))
        rounds.append((r["round"], fs, len(r["models_responded"])))
    return j, rounds


def main():
    j, rounds = load_rounds()
    cfg = DynamicManagementConfig()
    cd = ConvergenceDetector(cfg)
    drd = DiminishingReturnsDetector(cfg)
    cumulative = []

    print(f"tau_kappa={cfg.tau_kappa} eta_veto={cfg.eta_veto} min_rounds={cfg.min_rounds_for_convergence} "
          f"tau_sim_embed={cfg.tau_sim_embed} tau_novelty={cfg.tau_novelty} "
          f"tau_novelty_stop={cfg.tau_novelty_stop} tau_vocab={cfg.tau_vocab_growth}")
    hdr = (f'{"rd":>2} {"raw":>3} {"#cls":>4} {"#novel":>6} {"novHi":>5} '
           f'{"k_set":>6} {"k_rate":>6} {"kappa":>6} {"veto":>4} {"CONV":>4} '
           f'{"gamma_d":>7} | {"nov_rt":>6} {"vocSat":>6} {"sMu":>6} {"STOP":>4}')
    print(hdr); print("-" * len(hdr))

    cd_conv_round = None
    drd_stop_round = None
    for rd, fs, nmodels in rounds:
        cd.add_round_findings(rd, fs, duration=1.0, adoption_delta=0.0)
        new = fs
        cumulative = cumulative + new
        drd.add_round_from_findings(rd, cumulative, new, cost=float(nmodels))

        ncls = len(cd.get_round_classes(rd))
        novel = cd._novel_classes(rd)
        nnovel = len(novel)
        nov_hi = sum(1 for ec in novel if ec.aggregated_severity >= cfg.eta_veto)
        k_set = cd.kappa_set(rd); k_rate = cd.kappa_rate(rd); kap = cd.kappa(rd)
        veto = cd._veto(rd); conv = cd.converged(rd)
        gam = cd.estimate_gamma(rd)
        nov_rt = drd.novelty_rate(rd); voc = drd.vocab_saturated(rd)
        smu = drd.smoothed_marginal_value(rd); stop = drd.stop(rd)

        if conv and cd_conv_round is None:
            cd_conv_round = rd
        if stop and drd_stop_round is None:
            drd_stop_round = rd

        print(f'{rd:>2} {len(fs):>3} {ncls:>4} {nnovel:>6} {nov_hi:>5} '
              f'{k_set:>6.3f} {k_rate:>6.3f} {kap:>6.3f} {str(veto):>4} {str(conv):>4} '
              f'{gam:>7.3f} | {nov_rt:>6.3f} {str(voc):>6} {smu:>6.2f} {str(stop):>4}')

    print()
    print(f"ConvergenceDetector.converged() first True at round: {cd_conv_round}")
    print(f"DiminishingReturnsDetector.stop()  first True at round: {drd_stop_round}")
    print(f"Inline runner path: converged=None (never, across 16 rounds)")
    # Distinct critical defects were all first found by round 3 (signature trace);
    # ground-truth convergence is ~R3-5. Report verdict.
    print()
    print("GROUND TRUTH: all 4 distinct late critical defects first appeared by round 3;")
    print("zero genuine late critical discovery. A correct detector should converge ~R4-7.")


if __name__ == "__main__":
    main()
