# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_blocker_round1_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 53b2d50b04514206e6bce75a5da27bc494d35c5eb3b36562a1a589cd53e0d415
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Producer for every figure quoted in the 2026-10-03 panel answer on A4.

Run:  python3 scripts/a4_handoff_figures_2026-10-03.py
"""
import copy, importlib.util, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
STATE = (REPO / "bench/logs/study_run1b_2026-10-03_20261003T100439Z"
         / "runner_state.json")
REPORT = (REPO / "bench/logs/study_run1b_2026-10-03_20261003T100439Z"
          / "study_run1b_2026-10-03_report.json")

spec = importlib.util.spec_from_file_location("rr3_fig", RUNNER)
rr3 = importlib.util.module_from_spec(spec); sys.modules["rr3_fig"] = rr3
spec.loader.exec_module(rr3)

RAW = json.load(STATE.open())["registry"]
REP = json.load(REPORT.open())
def reg(): return rr3.FindingRegistry.from_dict(copy.deepcopy(RAW))

print("=" * 78)
print("[1] THE ARCHIVED STATE, read through the real FindingRegistry")
r = reg()
print(f"    entries                        = {len(r.entries)}")
print(f"    A4 unverified_critical_count   = {r.unverified_critical_count()}  (WITH the fix)")
stripped = reg()
for e in stripped.entries.values(): e.pop("hil_has_computed_evidence", None)
print(f"    A4 with the door closed        = {stripped.unverified_critical_count()}  (= a4_before)")
print(f"    handed_to_human_ids()          = {r.handed_to_human_ids()}")
print(f"    irreducible_queue_count()      = {r.irreducible_queue_count()}")
print(f"    contested_count(8, excl=True)  = {r.contested_count(8, subcritical_exclusion=True)}")
print(f"    contested_count(8, excl=False) = {r.contested_count(8, subcritical_exclusion=False)}")
print(f"    open_crit_high_count()         = {r.open_crit_high_count()}")
print(f"    undemonstrated_subcritical_ids = {r.undemonstrated_subcritical_ids()}")
print(f"    integrity_refused_criticals    = {r.integrity_refused_criticals()}")
for cid in ("C0066", "C0073"):
    e = r.entries[cid]
    print(f"    {cid}: sev={e['severity']} verdicts={len(e['verdicts'])} "
          f"routing_history={'routing_history' in e} "
          f"falsifier_code={bool((e.get('falsifier_code') or '').strip())} "
          f"hil_stamp={e.get('hil_has_computed_evidence')} "
          f"kinds={sorted({c.get('kind') for c in e.get('computed_evidence') or []})}")

print("=" * 78)
print("[2] THE BRIEF'S gamma ATTRIBUTION, read out of the report")
print(f"    gamma_all_history      = {REP['gamma_all_history']}")
print(f"    gamma_critical_history = {REP['gamma_critical_history']}")
print(f"    -> gamma_all final      = {REP['gamma_all_history'][-1]}   <-- the brief's 0.4274")
print(f"    -> gamma_critical final = {REP['gamma_critical_history'][-1]}   <-- the ACTUAL gamma_critical")
print(f"    gamma_alt_threshold = {REP['convergence_config']['gamma_alt_threshold']}, "
      f"consecutive_zero_crit = {REP['convergence_config']['gamma_alt_consecutive_zero_crit']}")
print(f"    max_rounds = {REP['max_rounds']}, stop_reason = {REP.get('stop_reason')}")
dc = REP["_declared_config"]
print(f"    declared: falsifier_gate_enabled={dc['falsifier_gate_enabled']}, "
      f"exhausted_round_threshold={dc['exhausted_round_threshold']}, "
      f"max_irreducible_queue={dc['max_irreducible_queue']}")

print("=" * 78)
print("[3] POSITION A, EXECUTED ALONE (severity clause deleted from the valve)")
src = RUNNER.read_text()
old = ('        if (e["status"] in EXHAUSTED_VALVE_STATUSES\n'
       '                and e["severity"] >= 0.7):')
mut = REPO / "bench" / ".a4_position_a_probe.py"
mut.write_text(src.replace(old, '        if (e["status"] in EXHAUSTED_VALVE_STATUSES):'))
sp = importlib.util.spec_from_file_location("rr3_posA", mut)
mA = importlib.util.module_from_spec(sp); sys.modules["rr3_posA"] = mA
sp.loader.exec_module(mA); mut.unlink()
cfg = mA.RunnerConfig(falsifier_gate_enabled=True)
for rnd in (8, 9, 20, 100):
    rr = mA.FindingRegistry.from_dict(copy.deepcopy(RAW))
    for e in rr.entries.values(): e.pop("hil_has_computed_evidence", None)
    mA._update_finding_statuses(rr, rnd, cfg)
    print(f"    round={rnd:>3}: A4={rr.unverified_critical_count()}  "
          f"C0066.exhausted={rr.entries['C0066'].get('exhausted')}  "
          f"C0073.exhausted={rr.entries['C0073'].get('exhausted')}")

print("=" * 78)
print("[4] WHY NO PRE-EXISTING DOOR IS REACHABLE for a sub-critical, EXECUTED")
sub = {"status": "UNCONFIRMED", "severity": 0.5, "verdicts": [],
       "falsifier_code": "", "falsifier_verdict": ""}
print(f"    _irreducible_queue_split on one sub-critical UNCONFIRMED entry = "
      f"{rr3._irreducible_queue_split({'C9': dict(sub, irreducible_escalation=True)})}"
      f"   (both arms 0: the split skips severity < 0.7)")
print(f"    same entry at severity 0.9                                     = "
      f"{rr3._irreducible_queue_split({'C9': dict(sub, severity=0.9, irreducible_escalation=True)})}")
cfg2 = rr3.RunnerConfig(falsifier_gate_enabled=True)
for sev in (0.5, 0.69, 0.70, 0.9):
    rr = rr3.FindingRegistry()
    rr.entries["C9"] = dict(sub, canonical_id="C9", severity=sev,
                            last_status_change_round=0,
                            verdicts=[{"model": "M", "verdict": "CONFIRM",
                                       "round": 0, "evidence": ""}])
    rr3._update_finding_statuses(rr, 20, cfg2)
    print(f"    exhausted valve at severity {sev:<5}: exhausted="
          f"{rr.entries['C9'].get('exhausted')}  status={rr.entries['C9']['status']}")

print("=" * 78)
print("[5] THE GATE, with the run's own declared config")
hist7 = [1, 3, 0, 0, 1, 0, 1, 0, 0]       # run 1b round-7 tail [1, 0, 0]
hist8 = hist7 + [0]                        # one more round -> tail [0, 0, 0]
for label, rg, hist, rnd in (("a4_before (door closed), round 7", stripped, hist7, 7),
                             ("a4_after  (door open),   round 7", reg(), hist7, 7),
                             ("a4_before (door closed), round 8", stripped, hist8, 8),
                             ("a4_after  (door open),   round 8", reg(), hist8, 8)):
    conv, why = rr3._check_gamma_alt_convergence(
        round_idx=rnd, gamma=0.4274, novel_critical_history=hist, cfg=cfg2,
        unresolved_critical=rg.unverified_critical_count(),
        contested=rg.contested_count(rnd, subcritical_exclusion=True),
        rho_churn=False, irreducible_queue=rg.irreducible_queue_count(),
        gamma_critical=0.7323, total_findings=len(rg.entries))
    print(f"    {label}: A4={rg.unverified_critical_count()} converged={conv}")
    print(f"        {why}")
print("=" * 78)
