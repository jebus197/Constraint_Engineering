#!/usr/bin/env python3
"""FALSIFIER: the R_k validator's extractor mis-reads the compact single-line
CORROBORATION style and manufactures FAILs against correct seat arithmetic.

Imports the REAL bench/reference_runner_v3.py and feeds it the REAL round-0
prose recorded in bench/logs/commissioning_arm1_panel_20260921T215405Z.

Demonstrated defect (pre-fix):
  CC2-SIM  s0: seat states R_old=0.50, q=0.727, S_k=0.92, nu_eff=0.038,
               R_k=0.266 -- arithmetic exact (SymPy: 0.26628). The extractor
               reads sk=0.237 (the seat's R_BASE result) and p=0.727 (the
               seat's q), recomputes 0.46759, grades FAIL.
  Gemini   s0: seat's R_k=0.303 is exact; extractor reads nu_eff=0.303 (the
               seat's R_K) and p=0.03 (the seat's nu_b), recomputes 0.65138.
  DeepSeek s0: seat states R_k=0.3590; extractor reads model_rk=0.141 -- the
               seat's DELTA-R -- because '.**' blocks the sentence clip.

Fails (AssertionError / prints FALSIFIED) iff the defect is present.
Exits 0 iff the extractor reproduces the seats' true values within the
validator's own WARN tolerance (0.05).

Run:  python3 bench/tests/test_rk_extractor_compact_prose_falsifier.py
"""
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REC = REPO / "bench" / "logs" / "commissioning_arm1_panel_20260921T215405Z"

spec = importlib.util.spec_from_file_location(
    "reference_runner_v3", REPO / "bench" / "reference_runner_v3.py")
rr = importlib.util.module_from_spec(spec)
sys.modules["reference_runner_v3"] = rr
spec.loader.exec_module(rr)


def section0(name):
    rec = json.load(open(next(REC.glob("r0_%s_*.json" % name))))
    return rr._extract_corroboration_sections(rec["response"])[0]


def true_rk(R_old, q, sk, nu):
    R_det = R_old * (1 - q) / (1 - q * R_old)
    R_base = sk * R_det + (1 - sk) * R_old
    return R_base * (1 - nu) + nu


failures = []

# (seat, params read by a human from the seat's own prose, seat's stated R_k)
CASES = [
    ("cc2-sim",      (0.50, 0.727, 0.92, 0.038),  0.266),
    ("gemini-sim",   (0.50, 0.650, 0.93, 0.0368), 0.303),
    ("deepseek-sim", (0.50, 0.578, 0.90, 0.0614), 0.3590),
]

for seat, params, stated in CASES:
    truth = true_rk(*params)
    assert abs(truth - stated) < 0.011, \
        "%s: test premise wrong -- seat arithmetic not clean" % seat
    status, model_rk, recomputed = rr._validate_rk_computation(section0(seat))
    if model_rk is None or abs(model_rk - stated) > 0.011:
        failures.append(
            "%s: extractor read model_rk=%s, seat stated %s" % (seat, model_rk, stated))
    if recomputed is None or abs(recomputed - truth) > 0.05:
        failures.append(
            "%s: extractor recomputed %s, true value from the seat's own "
            "stated parameters is %.4f (graded %s)" % (seat, recomputed, truth, status))

if failures:
    print("FALSIFIED")
    for f in failures:
        print("  " + f)
    raise AssertionError(
        "R_k extractor mis-reads compact prose: " + "; ".join(failures))

print("clean: extractor reproduces all 3 seats' stated parameters and values")
