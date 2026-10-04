# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'panel_blocker_round1_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ab509739a8153d1d9a92fc2366ba5bd20db54b7f1ed4e126bf60afb42808670c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Arm-isolation measurement for the run-1b A4 blockers (C0066, C0073).

Builds 4 variants of bench/reference_runner_v3.py's pre-pass 1 by exact
textual substitution, rehydrates the ARCHIVED run-1b registry through the
real FindingRegistry for each, and sweeps _update_finding_statuses over
round_idx 8..40, reading unverified_critical_count() after every call.

Variants:
  ORIG   : shipped code (severity>=0.7 clause AND has_reviews=verdicts-only)
  A_ONLY : Position A's repair alone  (severity clause removed; verdicts-only)
  B_ONLY : Position B's channel alone (computed_evidence counts; severity kept)
  A_PLUS_B: both arms (the delivered fix)
"""
import json, sys, types
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "bench" / "reference_runner_v3.py").read_text()
STATE = json.load(open(ROOT / "bench/logs/study_run1b_2026-10-03_20261003T100439Z/runner_state.json"))

SEV = '''        if (e["status"] in EXHAUSTED_VALVE_STATUSES
                and e["severity"] >= 0.7):'''
SEV_WIDE = '''        if (e["status"] in EXHAUSTED_VALVE_STATUSES
                and (e["status"] == "UNCONFIRMED" or e["severity"] >= 0.7)):'''
REV = '''            has_reviews = len(e.get("verdicts", [])) > 0'''
REV_WIDE = '''            has_reviews = (len(e.get("verdicts", [])) > 0
                           or len(e.get("computed_evidence", []) or []) > 0)'''

def build(name, src):
    mod = types.ModuleType(f"rr_{name}")
    mod.__file__ = str(ROOT / "bench" / "reference_runner_v3.py")
    sys.modules[mod.__name__] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod

def sweep(mod, rounds=range(8, 41)):
    reg = mod.FindingRegistry.from_dict(json.loads(json.dumps(STATE["registry"])))
    cfg = SimpleNamespace(exhausted_round_threshold=8, max_contested_rounds=3,
                          merge_arbitration_enabled=False, models=[],
                          test_article="", test_cmd="", fix_efficacy_mode="off")
    a4_0 = reg.unverified_critical_count()
    series = {}
    for r in rounds:
        mod._update_finding_statuses(reg, r, cfg)
        series[r] = reg.unverified_critical_count()
    ex = {c: bool(reg.entries[c].get("exhausted")) for c in ("C0066", "C0073")}
    stat = {c: reg.entries[c]["status"] for c in ("C0066", "C0073")}
    return a4_0, series, ex, stat

variants = {
    "ORIG": SRC,
    "A_ONLY": SRC.replace(SEV, SEV.replace('\n                and e["severity"] >= 0.7', "").replace('(e["status"]', 'e["status"]').replace('STATUSES)', 'STATUSES')),
    "B_ONLY": SRC.replace(REV, REV_WIDE),
    "A_PLUS_B": SRC.replace(SEV, SEV_WIDE).replace(REV, REV_WIDE),
}
# sanity: every substitution must have landed
assert SEV in SRC and REV in SRC
assert variants["B_ONLY"] != SRC and variants["A_PLUS_B"] != SRC and variants["A_ONLY"] != SRC

for name, src in variants.items():
    a4_0, series, ex, stat = sweep(build(name, src))
    rel = [r for r, v in series.items() if v == 0]
    print(f"{name:9s} A4@start={a4_0} A4@r8={series[8]} A4@r13={series[13]} "
          f"A4@r15={series[15]} A4@r40={series[40]} first_zero_round={rel[0] if rel else None} "
          f"exhausted={ex} status={stat}")
