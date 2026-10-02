# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_commissioning_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9f319fb5f0e32736c7df180d26ef0a3544c62ae355799be3455b6ba68201e8f7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Executed measurement for the 2026-10-02 free-panel A19 brief.

Scores the committed exploit fixture and the correct-prose fixture through
compute_sk with sk_score_prose_listings=True, reads the live sk_s_floor, and
computes the break-even S* from the live config.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

from bench.reference_runner_v3 import (  # noqa: E402
    RunnerConfig, check_sk_threshold, compute_sk, _capture_baseline,
)
import bench.tests.test_target_kind_and_no_score as tk  # noqa: E402

TARGET = "SW-21-REF-04.md"
base = _capture_baseline(tk.PROSE_TARGET, TARGET)
print("BASELINE:", json.dumps(base, default=str)[:400])
print()

for name, fix in (("CORRECT_PROSE_FIX", tk.CORRECT_PROSE_FIX),
                  ("SHELL_INJECTION_FIX", tk.SHELL_INJECTION_FIX)):
    r = compute_sk(fix, tk.PROSE_TARGET, TARGET, baseline=base,
                   score_prose_listings=True)
    print(f"=== {name}: tristate={r.tristate} sk={r.sk} A={r.A} E={r.E}")
    for k, v in r.gate_details.items():
        print(f"    {k}: {json.dumps(v, default=str)[:300]}")
    print()

cfg = RunnerConfig()
print("LIVE sk_s_floor =", cfg.sk_s_floor)
print("LIVE max_irreducible_queue =", cfg.max_irreducible_queue)
