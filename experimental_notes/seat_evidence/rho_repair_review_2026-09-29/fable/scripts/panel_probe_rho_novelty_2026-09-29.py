# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rho_repair_review_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c68f8b1c52f62d6a73e42fec0de4e0996a73ad3af5334386742fe68092929cfa
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Panel probe (seat: fable), 2026-09-29 between-rounds review.

Exercises _settled_novelty_series, _corroborated_novelty_series,
_corroborated_discounts, _compute_rho, _estimate_gamma and
_check_gamma_alt_convergence on constructed registries, across a range of
corroboration overlaps and on named edge cases. Read-only w.r.t. the repo;
registries are in memory only. Exit 0 always; findings print with EDGE-N tags.
"""
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO))

from reference_runner_v3 import (  # noqa: E402
    FindingRegistry,
    RunnerConfig,
    _settled_novelty_series,
    _corroborated_novelty_series,
    _corroborated_discounts,
    _compute_rho,
    _estimate_gamma,
    _check_gamma_alt_convergence,
)
from dynamic_management import Finding  # noqa: E402


def mk(fid, model, rnd, sev=0.5):
    return Finding(finding_id=fid, model_id=model, round_idx=rnd,
                   flaw_class=1, severity=sev, abstraction_index=0.5,
                   description="defect %s" % fid)


def sweep():
    print("== SWEEP: k re-sightings per round, k = 0..6 ==")
    cfg = RunnerConfig()
    for k in range(0, 7):
        reg = FindingRegistry()
        per_round_A = {}
        raw_counts = []
        for r in range(4):
            raw = 0
            ids = []
            for i in range(6):
                fid = "A_r%d_f%d" % (r, i)
                reg.register(mk(fid, "A", r), "A")
                ids.append(fid)
                raw += 1
            per_round_A[r] = ids
            if r >= 1:
                for i in range(k):
                    fid = "B_r%d_f%d" % (r, i)
                    reg.register(mk(fid, "B", r), "B")  # dup keeps its canonical
                    raw += 1
                    tgt = reg.lookup_alias("A", per_round_A[r - 1][i])
                    reg.record_codiscovery(tgt, "B", fid, 0.9, round_idx=r)
            raw_counts.append(raw)
        s_all, _ = _settled_novelty_series(reg, 3)
        c_all, _ = _corroborated_novelty_series(reg, 3)
        rho_s = _compute_rho(s_all, raw_counts, cfg)
        rho_c = _compute_rho(c_all, raw_counts, cfg)
        print(" k=%d: settled=%s corr=%s raw=%s rho_settled=(%.4f,%.4f) rho_corr=(%.4f,%.4f)"
              % (k, s_all, c_all, raw_counts, rho_s[0], rho_s[1], rho_c[0], rho_c[1]))


def edge_mutual_same_round():
    print("== EDGE-1: mutual same-round codiscovery (A<->B) ==")
    reg = FindingRegistry()
    c1 = reg.register(mk("fA", "A", 0), "A")
    c2 = reg.register(mk("fB", "B", 0), "B")
    reg.record_codiscovery(c1, "B", "fB", 0.9, round_idx=0)
    reg.record_codiscovery(c2, "A", "fA", 0.9, round_idx=0)
    d = _corroborated_discounts(reg)
    s_all, _ = _settled_novelty_series(reg, 0)
    c_all, _ = _corroborated_novelty_series(reg, 0)
    print(" discounts=%s settled=%s corroborated=%s" % (d, s_all, c_all))
    if c_all[0] == 0:
        print(" FINDING: one real defect, 2 registrations, corroborated count 0 "
              "(both discounted). Under-count when occasions are mutual.")
    else:
        print(" OK: exactly one survives.")


def edge_chain():
    print("== EDGE-2: chain C1(r0) <- C2(r1) <- C3(r2) ==")
    reg = FindingRegistry()
    c1 = reg.register(mk("f1", "A", 0), "A")
    c2 = reg.register(mk("f2", "B", 1), "B")
    c3 = reg.register(mk("f3", "C", 2), "C")
    reg.record_codiscovery(c1, "B", "f2", 0.9, round_idx=1)
    reg.record_codiscovery(c2, "C", "f3", 0.9, round_idx=2)
    d = _corroborated_discounts(reg)
    c_all, _ = _corroborated_novelty_series(reg, 2)
    print(" discounts=%s corroborated=%s" % (d, c_all))
    print(" OK" if c_all == [1, 0, 0] else " FINDING: chain does not collapse to 1")


def edge_kept_terminal():
    print("== EDGE-3: kept canonical is REFUTED, discounted one is OPEN ==")
    reg = FindingRegistry()
    c1 = reg.register(mk("f1", "A", 0, sev=0.9), "A")
    c2 = reg.register(mk("f2", "B", 1, sev=0.9), "B")
    reg.record_codiscovery(c1, "B", "f2", 0.9, round_idx=1)
    reg.entries[c1]["status"] = "REFUTED"
    d = _corroborated_discounts(reg)
    s_all, s_crit = _settled_novelty_series(reg, 1)
    c_all, c_crit = _corroborated_novelty_series(reg, 1)
    print(" discounts=%s settled=%s/%s corroborated=%s/%s" % (d, s_all, s_crit, c_all, c_crit))
    print(" C2 status=%s -- OPEN critical, corroborated series contributes %d criticals total"
          % (reg.entries[c2]["status"], sum(c_crit)))
    reg.entries[c1]["status"] = "UNCONFIRMED"
    c_all2, c_crit2 = _corroborated_novelty_series(reg, 1)
    print(" with C1=UNCONFIRMED: corroborated=%s/%s" % (c_all2, c_crit2))


def edge_idempotent_and_backfill():
    print("== EDGE-4: idempotency + resume backfill ==")
    reg = FindingRegistry()
    c1 = reg.register(mk("f1", "A", 0), "A")
    reg.register(mk("f2", "B", 1), "B")
    r1 = reg.record_codiscovery(c1, "B", "f2", 0.9, round_idx=1)
    r2 = reg.record_codiscovery(c1, "B", "f2", 0.9, round_idx=2)
    occ = [o for o in reg.entries[c1]["occasions"] if o.get("via") == "codiscovery"]
    print(" first=%s second=%s codiscovery occasions=%d (want 1)" % (r1, r2, len(occ)))
    reg2 = FindingRegistry()
    c1b = reg2.register(mk("g1", "A", 0), "A")
    reg2.register(mk("g2", "B", 1), "B")
    reg2.entries[c1b]["source_aliases"].append("B:g2")   # pre-2026-09-29 checkpoint
    rv = reg2.record_codiscovery(c1b, "B", "g2", 0.8, round_idx=1)
    occ2 = [o for o in reg2.entries[c1b]["occasions"] if o.get("via") == "codiscovery"]
    print(" backfill: return=%s (want False) occasions=%d (want 1) from_canonical=%s"
          % (rv, len(occ2), occ2[0]["from_canonical"] if occ2 else None))


def edge_self_reference():
    print("== EDGE-5: unresolved alias -> self-reference refused ==")
    reg = FindingRegistry()
    c1 = reg.register(mk("f1", "A", 0), "A")
    reg.record_codiscovery(c1, "B", "zz", 0.9, round_idx=1)
    d = _corroborated_discounts(reg)
    c_all, _ = _corroborated_novelty_series(reg, 1)
    tag = "OK: no self-discount" if (not d and c_all[0] == 1) else "FINDING"
    print(" discounts=%s corroborated=%s %s" % (d, c_all, tag))


def rho_stale_window():
    print("== EDGE-6: rho_avg window mixes stale and corroborated values ==")
    cfg = RunnerConfig()
    raw = [6, 6, 6]
    as_recorded = [6, 6, 3]      # rounds 0-1 keep the value known at the time
    fully_resettled = [6, 3, 3]  # what the final registry says
    r_rec = _compute_rho(as_recorded, raw, cfg)
    r_set = _compute_rho(fully_resettled, raw, cfg)
    print(" recorded=%s -> rho_avg=%.4f; resettled=%s -> rho_avg=%.4f; delta=%+.4f"
          % (as_recorded, r_rec[1], fully_resettled, r_set[1], r_rec[1] - r_set[1]))


def gate_probe():
    print("== GATE: can rho churn move _check_gamma_alt_convergence? ==")
    cfg = RunnerConfig()
    hist = [0] * 20
    ok_no_churn = _check_gamma_alt_convergence(
        19, 0.5, hist, cfg, unresolved_critical=0, contested=0,
        rho_churn=False, gamma_critical=0.6, total_findings=10)
    ok_churn = _check_gamma_alt_convergence(
        19, 0.5, hist, cfg, unresolved_critical=0, contested=0,
        rho_churn=True, gamma_critical=0.6, total_findings=10)
    print(" converged (no churn) = %s" % ok_no_churn[0])
    print(" converged (CHURN)    = %s" % ok_churn[0])
    print(" churn reason note    = %s" % ok_churn[1][:200])
    if ok_no_churn[0] == ok_churn[0]:
        print(" FINDING: churn does NOT change the gamma-alt verdict "
              "(docstring condition (d) is stale; founder ruling 2026-08-29).")


if __name__ == "__main__":
    sweep()
    edge_mutual_same_round()
    edge_chain()
    edge_kept_terminal()
    edge_idempotent_and_backfill()
    edge_self_reference()
    rho_stale_window()
    gate_probe()
    print("DONE")
