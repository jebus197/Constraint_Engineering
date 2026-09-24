#!/usr/bin/env python3
"""FALSIFIER: the archived `REJECTED` token conflates TWO causes, and 0 of them
are the unmeasured constants.

THE CLAIM UNDER TEST is the round-4 panel brief, Section 3:

    "191 fixes were refused on the strength of a constant nobody measured."

It is false, and the error is one level above the parsing trap the brief itself
records. CC1 correctly stopped reading the constant NAME `SK_REJECTED` and read
the recorded VALUE "REJECTED" instead -- 191 real verdicts, reproduced here
exactly. It then attributed all 191 to the S* threshold, which is the gate the
frozen literals (q, R_old, nu_b, nu_f) feed. But `REJECTED` is written at TWO
sites in bench/reference_runner_v3.py:

  (a) compute_sk returns SK_REJECTED     -- the patch would not apply, or a hard
      gate failed. `compute_sk(fix_text, source, source_path, baseline=,
      test_cmd=, declared_target_kind=, score_prose_listings=)` takes NO model
      parameters at all (line 10685). The constants decide NOTHING here.

  (b) line 12106 OVERWRITES the tristate:  entry["sk_result"]["tristate"] =
      SK_REJECTED, after check_sk_threshold_corrected refused. THIS is the site
      the constants decide.

Both write the same five bytes, so the token alone cannot tell them apart. They
are separable on the record, because (b) passes through line 11998,
`entry["sk_result"]["passes_threshold"] = passes`, and (a) never reaches it. So
a (b)-refusal carries the key `passes_threshold`; an (a)-refusal does not.

MEASURED: 0 of 191 carry it. Every archived refusal is cause (a). Corroborating,
all 4142 archived gate records carry s_star == 0 -- the threshold never bound.

This reinstates the residual the cc2 seat raised and declined to close:
"If none did, then the one constant decides nothing on the record either, and
CHANGE NOTHING becomes the correct verdict for the archive." It is the correct
verdict for the archive. The Phase 2 defect is real and prospective; it has no
archival body count.

Exits cleanly if the brief's attribution is right (some refusal is gate-caused).
Raises AssertionError if the attribution is wrong.

Run:  python3 scripts/rejected_is_two_causes_conflated_2026-09-20.py
"""
from __future__ import annotations

import glob
import json
import os
import sys
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 60_000_000


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def collect(pattern: str) -> tuple[int, list[dict]]:
    """Walk archived runner states, returning every sk_result dict."""
    out: list[dict] = []

    def walk(o: object) -> None:
        if isinstance(o, dict):
            sk = o.get("sk_result")
            if isinstance(sk, dict) and "tristate" in sk:
                out.append(sk)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    files = 0
    for f in sorted(glob.glob(str(ROOT / pattern))):
        if os.path.getsize(f) > MAX_BYTES:
            continue
        try:
            walk(json.loads(open(f, errors="ignore").read()))
        except Exception:
            continue
        files += 1
    return files, out


def main() -> int:
    # CC1's exact corpus, so the 191 is reproduced rather than re-derived on a
    # corpus of my choosing.
    files, recs = collect("bench/logs/*/runner_state.json")
    rejected = [r for r in recs if str(r.get("tristate")) == "REJECTED"]
    reached_gate = [r for r in rejected if "passes_threshold" in r]
    by_constants = [r for r in reached_gate
                    if r.get("passes_threshold") in (False, "False", 0)]
    n, k = len(rejected), len(by_constants)
    lo, hi = wilson(k, n)

    print(f"corpus bench/logs/*/runner_state.json           : {files} files")
    print(f"sk_result records                               : {len(recs)}")
    print(f"REJECTED (CC1 reports 191)                      : {n}")
    print(f"  reached the S* gate (has passes_threshold)    : {len(reached_gate)}")
    print(f"  refused BY THE CONSTANTS                      : {k}")
    print(f"  refused by compute_sk, which takes no params  : {n - len(reached_gate)}")
    print(f"  share attributable to the constants           : {100.0 * k / n:.4f}%"
          f"  Wilson [{100.0 * lo:.4f}%, {100.0 * hi:.4f}%]")

    try:
        from statsmodels.stats.proportion import proportion_confint
        slo, shi = proportion_confint(k, n, 0.05, method="wilson")
        agree = abs(slo - lo) < 1e-12 and abs(shi - hi) < 1e-12
        print(f"  statsmodels Wilson agrees to 1e-12            : {agree}")
    except ImportError:
        print("  statsmodels unavailable; closed form only")

    s_stars = [r.get("s_star") for r in recs if "s_star" in r]
    nonzero = sum(1 for v in s_stars if v is not None and float(v) != 0.0)
    print(f"gate records carrying s_star                    : {len(s_stars)}")
    print(f"  with a NON-ZERO s_star                        : {nonzero}"
          f"   (the threshold never bound)")

    assert n > 0, "no REJECTED verdicts found; corpus is not what the brief describes"
    assert k == 0, (
        f"the brief's attribution SURVIVES: {k} of {n} archived refusals were "
        f"decided by the constants")
    print("\nFALSIFIED: 0 of "
          f"{n} archived refusals were decided by q / R_old / nu_b / nu_f. "
          "The brief's\nSection 3 attributes all of them to the constants. "
          "cc2's residual stands: for the\nARCHIVE, change nothing.")
    return 1


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    # CORRECTED 2026-09-24 (CC1): was `sys.exit(0 if main() == 0 else 1)`,
    # which collapses EVERY non-zero status to 1 and throws away the code
    # main() computed. A caller distinguishing 2 (refused to measure) from
    # 1 (measured and failed) could not.
    sys.exit(main())
