# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: da673350979e52ed2459bd7c6d8e45c30e45909e1d585ed3ee7c3e01d4701f60
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: does the CRITICAL PARTITION count a disproved finding as a
critical discovery?

Imports the REAL readers from `bench.reference_runner_v3` and calls them. No
function under test is retyped. The defect is DEMONSTRATED (AssertionError, and
the literal token FALSIFIED printed) exactly when a finding whose falsifier the
harness re-ran and did NOT demonstrate still lands in the critical series that
feeds `_check_gamma_alt_convergence`; the script exits cleanly when it does not.

Bidirectional by construction: check [D] monkeypatches `spec_critical_severity`
back to the raw `severity` read the readers performed before 2026-11-04 and
requires the defect to REAPPEAR. A falsifier that cannot fail is not a
falsifier.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import bench.reference_runner_v3 as rr  # noqa: E402
from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD, FindingRegistry, RunnerConfig,
    _check_gamma_alt_convergence, _corroborated_novelty_series,
    _estimate_gamma, _settled_novelty_series,
)

PROBLEMS: list[str] = []
READERS = (("_settled_novelty_series", _settled_novelty_series),
           ("_corroborated_novelty_series", _corroborated_novelty_series))


def _reg(**over) -> FindingRegistry:
    e = {"canonical_id": "C0001", "source_model": "SEAT", "source_aliases": [],
         "severity": 0.9, "description": "probe", "proposed_fix": "",
         "status": "OPEN", "open_since_round": 0,
         "last_status_change_round": 0, "verdicts": [], "verified": False,
         "escalated": False, "flaw_class": 1}
    e.update(over)
    reg = FindingRegistry()
    reg.entries = {"C0001": e}
    return reg


def _check(label: str, cond: bool, detail: str) -> None:
    print(f"  {label:<62}{'OK' if cond else 'FALSIFIED'}")
    if not cond:
        PROBLEMS.append(f"{label}: {detail}")


print("[A] KEY PROPERTY: a disproved finding is not a critical discovery")
for name, fn in READERS:
    reg = _reg(falsifier_verdict="REFUTED")
    all_s, crit_s = fn(reg, 0)
    _check(f"{name}: REFUTED 0.9 -> crit_s",
           crit_s == [0] and all_s == [1],
           f"all_s={all_s} crit_s={crit_s} (want all_s=[1], crit_s=[0]) -- a "
           "finding the harness disproved is counted as a critical discovery")

print("[B] V(None) must NOT de-escalate (the A4 fail-safe stays armed)")
for name, fn in READERS:
    reg = _reg()                                  # no falsifier_verdict at all
    all_s, crit_s = fn(reg, 0)
    _check(f"{name}: unresolved 0.9 -> crit_s", crit_s == [1],
           f"crit_s={crit_s} -- an UNRESOLVED critical was silently halved "
           "below the cut, which is the manufactured-convergence direction")

print("[C] a tool-CONFIRMED status outranks a stale REFUTED verdict field")
for name, fn in READERS:
    reg = _reg(falsifier_verdict="REFUTED", status="CONFIRMED")
    _all, crit_s = fn(reg, 0)
    _check(f"{name}: REFUTED verdict + CONFIRMED status", crit_s == [1],
           f"crit_s={crit_s} -- a tool-CONFIRMED critical was dropped on a "
           "stale verdict field")

print("[D] the check can FAIL: restore the pre-2026-11-04 raw read")
_saved = rr.spec_critical_severity
rr.spec_critical_severity = lambda e: float(e.get("severity") or 0.0)
try:
    reappeared = []
    for name, fn in READERS:
        reg = _reg(falsifier_verdict="REFUTED")
        _all, crit_s = fn(reg, 0)
        reappeared.append(crit_s == [1])
        print(f"  {name:<40} raw read -> crit_s={crit_s}")
    _check("defect reappears under the raw read", all(reappeared),
           "the falsifier cannot distinguish the defect from its absence")
finally:
    rr.spec_critical_severity = _saved

print("[E] no archived convergence verdict is restated by the repair")
cfg = RunnerConfig()
seen, moved, n = set(), [], 0
for p in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h in seen:
        continue
    seen.add(h)
    try:
        d = json.loads(p.read_text())
    except Exception:                             # noqa: BLE001
        continue
    ents = (d.get("registry") or {}).get("entries") or {}
    if not ents:
        continue
    n += 1
    verdicts = []
    for hook in (lambda e: float(e.get("severity") or 0.0), _saved):
        rr.spec_critical_severity = hook
        try:
            reg = FindingRegistry()
            reg.entries = copy.deepcopy(ents)
            rounds = [e.get("open_since_round") for e in reg.entries.values()
                      if isinstance(e, dict)
                      and isinstance(e.get("open_since_round"), int)]
            mr = max(rounds) if rounds else 0
            all_s, crit_s = _settled_novelty_series(reg, mr)
            verdicts.append(_check_gamma_alt_convergence(
                mr, _estimate_gamma(all_s, cfg.min_rounds_for_gamma),
                list(crit_s), cfg,
                unresolved_critical=int(reg.unverified_critical_count(mr)),
                contested=int(reg.contested_count(mr)), rho_churn=False,
                irreducible_queue=int(reg.irreducible_queue_count()),
                gamma_critical=_estimate_gamma(crit_s, cfg.min_rounds_for_gamma),
                total_findings=len(reg.entries))[0])
        finally:
            rr.spec_critical_severity = _saved
    if verdicts[0] != verdicts[1]:
        moved.append((p.parent.name, verdicts))
print(f"  replayed {n} distinct archived registries")
_check("archived gate verdicts changed by the repair", not moved, str(moved))

print()
if PROBLEMS:
    print("FALSIFIED")
    raise AssertionError("defect present: " + "; ".join(PROBLEMS))
print(f"defect NOT demonstrated: the critical partition enforces the section "
      f"7.7 key property at the {CRITICAL_SEVERITY_THRESHOLD} cut on both "
      f"readers, V(None) still blocks, a tool-CONFIRMED status outranks a "
      f"stale verdict, the check is capable of failing, and 0 of {n} archived "
      f"verdicts move.")
