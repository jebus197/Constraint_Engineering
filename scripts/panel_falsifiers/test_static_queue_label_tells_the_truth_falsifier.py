#!/usr/bin/env python3
"""FALSIFIER: the static-HIL-queue log line calls every queued critical
"ladder-exhausted", but the counter it prints (irreducible_queue_count)
deliberately includes `routing_deferred` items the ladder NEVER RAN FOR.

Real case: commissioning arm 4 (2026-09-22) — the alarm queue of 8 was
entirely routing_deferred (log: "0 -> HIL, 8 deferred (never assessed)";
report: 7 of 8 UNTOOLABLE with falsifier_present=false, 1 ERROR), yet the
log said "static HIL queue: 8 ladder-exhausted irreducible critical(s)",
and the morning report built its arm-4 causal chain (max_rungs=2 ->
exhausted -> never scored -> halt) on that label.

Imports the REAL bench/reference_runner_v3.py. Fails iff the registry
cannot state the split its own log line asserts — i.e. there is no
irreducible_queue_breakdown() distinguishing ladder-exhausted from
deferred-never-assessed, or it mis-counts an all-deferred queue.
"""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "reference_runner_v3", REPO / "bench" / "reference_runner_v3.py")
rr = importlib.util.module_from_spec(spec)
sys.modules["reference_runner_v3"] = rr
spec.loader.exec_module(rr)

reg = rr.FindingRegistry()
for i in range(8):  # arm 4's shape: all deferred, none escalated
    reg.entries[f"C{i:04d}"] = {
        "status": "OPEN", "severity": 0.85, "routing_deferred": True,
    }
reg.entries["C0100"] = {  # a genuinely ladder-exhausted one for contrast
    "status": "OPEN", "severity": 0.9, "irreducible_escalation": True,
}

if not hasattr(reg, "irreducible_queue_breakdown"):
    print("FALSIFIED")
    raise AssertionError(
        "FindingRegistry cannot distinguish ladder-exhausted from "
        "deferred-never-assessed; the 'N ladder-exhausted irreducible' log "
        "line asserts a split the instrument cannot state (arm 4: 8 deferred "
        "items logged as ladder-exhausted).")

exhausted, deferred = reg.irreducible_queue_breakdown()
assert (exhausted, deferred) == (1, 8), \
    f"breakdown wrong: got ({exhausted}, {deferred}), want (1, 8)"
assert reg.irreducible_queue_count() == 9, "total must stay unchanged"
print("clean: breakdown (1 ladder-exhausted, 8 deferred), total unchanged at 9")
