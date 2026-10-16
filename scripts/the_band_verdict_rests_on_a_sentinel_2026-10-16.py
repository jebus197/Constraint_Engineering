#!/usr/bin/env python3
"""How often does the boundary-band verdict rest on a sentinel rather than a slope?

HIS RULING, 2026-10-16, on the 7 smaller defects including this one: *"Fix it
all."*

THE DEFECT. `_estimate_gamma` returns 0.0 for FOUR distinct reasons and only one
of them is a slope of 0.0 -- too few rounds, no novelty at all, fewer than 2
usable log points, and a degenerate denominator are the other three, as its own
mirror `_gamma_is_estimable` documents. The boundary-band sensitivity block
compared the two band edges for equality:

    verdict_robust_to_band = (_lo is not None and _hi is not None and _lo == _hi)

So two sentinels compared EQUAL, and the run was reported *robust to the whole
rubric disagreement* on the strength of a quantity that was never measured. The
disagreement in question is large: across 286 archived findings in that band the
numeric proxy and the five-clause rubric agree on 141 of 259 judgeable cases,
54.4%, while two blind readers agreed with each other on 86 of 93 (92.5%,
Cohen's kappa 0.837). A false "robust" therefore retires a real question.

IT FAILS IN BOTH DIRECTIONS, which is why the repair is a gate and not a sign
flip. Where both edges are sentinels the verdict reads TRUE and should read
"unreadable". Where one edge is real and the other a sentinel the verdict reads
FALSE -- a false alarm, claiming the verdict is fragile on the basis of a number
that does not exist.

`execute-do-not-grep`: this reads the ARCHIVE's own recorded blocks, and the
companion test calls the live reporter. Neither asserts on source text.

Free on `--help`: dispatches nothing, spends nothing, reads only local files.

Usage:
    python3 scripts/the_band_verdict_rests_on_a_sentinel_2026-10-16.py
    python3 scripts/the_band_verdict_rests_on_a_sentinel_2026-10-16.py --json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def _blocks() -> list[tuple[str, dict]]:
    found: list[tuple[str, dict]] = []
    for path in sorted(LOGS.rglob("*_report.json")):
        try:
            doc = json.loads(path.read_text(errors="replace"))
        except (OSError, ValueError):
            continue
        run = path.relative_to(LOGS).parts[0]

        def walk(obj):
            if isinstance(obj, dict):
                blk = obj.get("boundary_band_sensitivity")
                if isinstance(blk, dict):
                    found.append((run, blk))
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)

        walk(doc)
    return found


def _wilson(k: int, n: int) -> tuple[float, float]:
    from statsmodels.stats.proportion import proportion_confint
    return proportion_confint(k, n, alpha=0.05, method="wilson")


def _exact(k: int, n: int) -> tuple[float, float]:
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="beta")
    # Cross-verified against scipy's beta quantiles, per the 2-tool rule.
    from scipy.stats import beta as sbeta
    lo_s = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
    hi_s = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
    assert abs(lo - lo_s) < 1e-9 and abs(hi - hi_s) < 1e-9, (lo, lo_s, hi, hi_s)
    return lo, hi


def measure() -> dict:
    blocks = _blocks()
    n = len(blocks)
    both_sentinel = one_sentinel = readable = errored = 0
    gated = 0
    for _run, b in blocks:
        if "error" in b:
            errored += 1
            continue
        lo, hi = b.get("gamma_at_lower_edge"), b.get("gamma_at_upper_edge")
        # A block written by the REPAIRED reporter carries the estimability keys.
        if "band_is_readable" in b:
            gated += 1
        lo_sent = (lo == 0.0)
        hi_sent = (hi == 0.0)
        if lo is None or hi is None:
            one_sentinel += 1
        elif lo_sent and hi_sent:
            both_sentinel += 1
        elif lo_sent or hi_sent:
            one_sentinel += 1
        else:
            readable += 1
    false_robust = sum(
        1 for _r, b in blocks
        if b.get("gamma_at_lower_edge") == 0.0
        and b.get("gamma_at_upper_edge") == 0.0
        and b.get("verdict_robust_to_band") is True
    )
    return {
        "blocks": n,
        "errored": errored,
        "both_edges_sentinel": both_sentinel,
        "exactly_one_edge_sentinel": one_sentinel,
        "both_edges_real": readable,
        "false_robust_true_on_two_sentinels": false_robust,
        "blocks_written_by_the_gated_reporter": gated,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args()
    m = measure()
    if args.json:
        print(json.dumps(m, indent=2, sort_keys=True))
        return 0

    n = m["blocks"]
    print("THE BOUNDARY-BAND VERDICT, OVER THE ARCHIVE'S OWN RECORDED BLOCKS")
    if n == 0:
        print("  no report carries a boundary_band_sensitivity block.")
        return 1
    rows = [
        ("both edges are the 0.0 sentinel", m["both_edges_sentinel"]),
        ("exactly one edge is a sentinel or absent", m["exactly_one_edge_sentinel"]),
        ("both edges are real slopes", m["both_edges_real"]),
        ("the block records an error", m["errored"]),
        ("FALSE 'robust' asserted on two sentinels",
         m["false_robust_true_on_two_sentinels"]),
    ]
    print(f"  blocks found: {n}")
    for name, k in rows:
        lo_w, hi_w = _wilson(k, n)
        lo_e, hi_e = _exact(k, n)
        print(f"  {name:<44}{k:>4}/{n:<4}{100*k/n:>8.4f}%  "
              f"Wilson [{100*lo_w:6.4f}%,{100*hi_w:8.4f}%]  "
              f"CP [{100*lo_e:6.4f}%,{100*hi_e:8.4f}%]")
    meaningless = m["both_edges_sentinel"] + m["exactly_one_edge_sentinel"]
    lo_w, hi_w = _wilson(meaningless, n)
    print()
    print(f"  VERDICTS CARRYING NO INFORMATION: {meaningless} of {n} "
          f"({100*meaningless/n:.4f}%, Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%])")
    print(f"  blocks written by the GATED reporter: "
          f"{m['blocks_written_by_the_gated_reporter']} of {n}")
    print()
    if m["blocks_written_by_the_gated_reporter"] == n:
        print("  VERDICT: every archived block carries the estimability gate, so")
        print("  the defect is historical. Re-derive the figures above.")
        return 0
    print("  VERDICT: the archive is PRE-REPAIR, as expected -- nothing recorded")
    print("  is rewritten. The repair gates the verdict in runs from here on:")
    print("  `band_is_readable` is emitted, and `verdict_robust_to_band` is null")
    print("  where gamma is not estimable at an edge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
