#!/usr/bin/env python3
"""What would it cost to ENFORCE the R_k proof the directive already demands?

THE SITUATION THIS MEASURES. Every model is told, in the round prompt itself:
"Findings missing any section will be rejected." One of those sections is
CORROBORATION, where the model must "compute R_k(i) numerically ... show your
working: R_old, eta, d, p, q, R_det, S_k, nu_b, nu_f, nu_eff, final R_k".

The runner already CHECKS that working. `validate_round_rk()` re-derives R_k from
the model's own stated parameters and grades the result PASS / WARN / FAIL / SKIP.
Its own docstring then says: "Advisory only -- logs WARN/FAIL but never rejects
findings." At reference_runner_v3.py:11699 the result is used to build one log
line and is then discarded. Every finding registers regardless.

So the sentence in the prompt is false, and severity is a model's unchecked
assertion -- which is what the founder identified: a severity that cannot be
recomputed is a vote, and CDSFL has no votes.

WHAT THIS SCRIPT DOES. It runs the SHIPPED validator over every archived model
response, so the rate is a property of the real corpus and the real code, not of
a reimplementation. It reports what fraction of findings would survive each
candidate enforcement rule, with confidence intervals, so the rule is chosen
against evidence instead of taste.

Usage: python3 scripts/measure_rk_proof_compliance.py
"""
from __future__ import annotations

import glob
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))

from reference_runner_v3 import (  # noqa: E402
    _extract_corroboration_sections,
    _validate_rk_computation,
)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval. Correct at k=0 and k=n, where the normal
    approximation is not."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    files = sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "round*_*.json")))
    status = Counter()
    per_model = {}
    deltas = []
    files_with_responses = 0

    for fp in files:
        try:
            doc = json.loads(Path(fp).read_text())
        except Exception:
            continue
        responses = doc.get("model_responses") or {}
        if not isinstance(responses, dict) or not responses:
            continue
        if doc.get("model_responses_truncated"):
            # A truncated response can lose its CORROBORATION tail, which would
            # score SKIP for a reason that is ours, not the model's.
            continue
        files_with_responses += 1
        for model, text in responses.items():
            if not isinstance(text, str):
                continue
            for sec in _extract_corroboration_sections(text):
                st, model_rk, recomputed = _validate_rk_computation(sec)
                status[st] += 1
                d = per_model.setdefault(model, Counter())
                d[st] += 1
                if model_rk is not None and recomputed is not None:
                    deltas.append(abs(model_rk - recomputed))

    n = sum(status.values())
    print("R_k PROOF COMPLIANCE IN THE ARCHIVE")
    print("=" * 74)
    print(f"  round files scanned      : {len(files)}")
    print(f"  files carrying responses : {files_with_responses}")
    print(f"  CORROBORATION sections   : {n}")
    if n == 0:
        print("\n  NO SECTIONS FOUND -- nothing to measure. Enforcement rate unknown.")
        return 1
    print()
    for st in ("PASS", "WARN", "FAIL", "SKIP"):
        k = status.get(st, 0)
        lo, hi = wilson(k, n)
        print(f"  {st:5s} {k:6d} of {n:6d}  {100*k/n:6.2f}%   "
              f"Wilson [{100*lo:.2f}%, {100*hi:.2f}%]")

    print("\nWHAT EACH CANDIDATE RULE WOULD REJECT")
    print("-" * 74)
    rules = {
        "strict  (only PASS survives)": ("WARN", "FAIL", "SKIP"),
        "moderate(PASS+WARN survive)": ("FAIL", "SKIP"),
        "lenient (reject only FAIL)": ("FAIL",),
        "arithmetic-only (FAIL, but SKIP routed back)": ("FAIL",),
    }
    for name, killed in rules.items():
        k = sum(status.get(s, 0) for s in killed)
        lo, hi = wilson(k, n)
        print(f"  {name:46s} rejects {k:6d}  {100*k/n:6.2f}%  "
              f"[{100*lo:.2f}%, {100*hi:.2f}%]")

    if deltas:
        import statistics
        deltas.sort()
        print(f"\n  |model R_k - recomputed R_k| over {len(deltas)} comparable sections:")
        print(f"    median {statistics.median(deltas):.4f}   "
              f"p90 {deltas[int(0.9*(len(deltas)-1))]:.4f}   max {max(deltas):.4f}")

    print("\nPER MODEL")
    print("-" * 74)
    for model in sorted(per_model, key=lambda m: -sum(per_model[m].values())):
        c = per_model[model]
        tot = sum(c.values())
        if tot < 20:
            continue
        graded = c["PASS"] + c["WARN"] + c["FAIL"]
        lo, hi = wilson(graded, tot)
        print(f"  {model:26s} n={tot:5d}  PASS={c['PASS']:5d} WARN={c['WARN']:4d} "
              f"FAIL={c['FAIL']:4d} SKIP={c['SKIP']:5d}   "
              f"gradeable {100*graded/tot:5.1f}% [{100*lo:.1f}%, {100*hi:.1f}%]")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    raise SystemExit(main())
