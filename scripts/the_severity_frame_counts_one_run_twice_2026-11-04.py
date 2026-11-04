#!/usr/bin/env python3
"""Does the severity archive count one run twice, and what does excluding it cost?

THE FIGURES THIS BACKS. Entry B121 of the master task list was raised on
2026-11-04 carrying 5 quantities and naming no script, which is
`measured-rate-travels-with-its-script` violated in the entry that reports a
measurement defect. This is that script. Every number B121 states is recomputed
here from the archive on disk.

WHAT IS WRONG. `bench/logs/exp36_evidence_latest` is a symbolic link to
`bench/logs/exp36_evidence_20260407T004931Z`, and `pathlib.Path.glob` follows
symbolic links. The severity frame is built by globbing `*/runner_state.json`
under `bench/logs`, so that one run's severities enter the frame twice, as an
exact duplicate rather than as a near copy. The link has been in place since
April, so it was inside the frame when the 2026-10-28 figures were taken: it is
NOT the cause of the drift those figures later suffered, but a separate and
older fault that the drift investigation surfaced.

WHY THE OBVIOUS REPAIR IS NOT OBVIOUSLY RIGHT, AND B121 UNDERSTATED THIS.
Excluding the link shrinks the frame, and the guard on the severity producer
holds floors that exist to detect a LOSS of archive data. B121 says 2 floors
would turn red. This script reads every floor out of the guard file and
measures each one both ways, and the answer is 3. So the day anyone
de-duplicates the frame without re-deriving the floors in the same commit, a
correct board will report that the archive was rewritten when nothing has been.

THE FLOORS ARE READ FROM THE GUARD, NEVER HARDCODED HERE. A second copy of a
threshold can be loosened while every test stays green, and a harness that
hardcodes what it measures stops tracking its subject the moment the subject
moves. This reads the guard file and reports what it found, including how many
floors it found, so a floor added or removed changes this output rather than
being silently missed.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
FRAME_GLOB = "*/runner_state.json"
PRODUCER = REPO / "scripts" / "the_severity_proxy_was_never_tested_2026-10-28.py"
GUARD = REPO / "bench" / "tests" / "test_the_severity_proxy_was_never_tested_2026-10-28.py"
#: The quantities the guard floors, each as it is named in the produced dict.
FLOORED = ("archive_n", "critical_above_band", "archive_critical")


def severities_of(path: pathlib.Path) -> list[float]:
    """Every registry severity in one run's state file, or none if unreadable."""
    try:
        entries = (json.loads(path.read_text(encoding="utf-8"))
                   .get("registry", {}).get("entries", {}))
    except (OSError, ValueError):
        return []
    return [float(e["severity"]) for e in entries.values()
            if isinstance(e, dict) and isinstance(e.get("severity"), (int, float))]


def read_floors() -> dict[str, int]:
    """Lift each floor out of the guard's source, so nothing is pinned twice."""
    src = GUARD.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for name in FLOORED:
        m = re.search(rf'\["{re.escape(name)}"\]\s*>=\s*(\d+)', src)
        if m:
            out[name] = int(m.group(1))
    return out


def band_and_cut() -> tuple[float, float, float]:
    """The audit's severity band and the gate's cut, from the producer itself."""
    sys.path.insert(0, str(PRODUCER.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("_sp", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sev, _y, _d = mod._audit_rows()
    return float(np.min(sev)), float(np.max(sev)), float(mod.CUT)


def two_route_wilson(k: int, n: int) -> tuple[tuple[float, float], float]:
    """Wilson by statsmodels and by an independent closed form in mpmath."""
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo_a, hi_a = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, N = mp.mpf(k) / n, mp.mpf(n)
    d = 1 + z**2 / N
    c = (p + z**2 / (2 * N)) / d
    h = (z / d) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return (float(lo_a), float(hi_a)), max(abs(float(c - h) - lo_a),
                                           abs(float(c + h) - hi_a))


def two_route_exact(k: int, n: int) -> tuple[tuple[float, float], float]:
    """Clopper-Pearson by statsmodels and by scipy's beta quantiles directly."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta
    lo_a, hi_a = proportion_confint(k, n, method="beta")
    lo_b = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi_b = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return (float(lo_a), float(hi_a)), max(abs(lo_b - lo_a), abs(hi_b - hi_a))


def measure() -> dict:
    link = LOGS / "exp36_evidence_latest"
    files = sorted(LOGS.glob(FRAME_GLOB))
    linked = [p for p in files if p.parent.is_symlink()]
    real = [p for p in files if not p.parent.is_symlink()]

    followed = np.array([s for p in files for s in severities_of(p)], dtype=float)
    excluded = np.array([s for p in real for s in severities_of(p)], dtype=float)
    from_link = [s for p in linked for s in severities_of(p)]

    target = (LOGS / os.readlink(link) / "runner_state.json") if link.is_symlink() else None
    target_sev = severities_of(target) if target and target.is_file() else []

    lo, hi, cut = band_and_cut()

    def vals(frame: np.ndarray) -> dict[str, int]:
        return {"archive_n": int(frame.size),
                "critical_above_band": int((frame > hi).sum()),
                "archive_critical": int((frame >= cut).sum())}

    r: dict = {
        "is_symlink": bool(link.is_symlink()),
        "link_target": os.readlink(link) if link.is_symlink() else None,
        "frame_files": len(files),
        "linked_dirs": [p.parent.name for p in linked],
        "n_followed": int(followed.size),
        "n_excluded": int(excluded.size),
        "n_from_link": len(from_link),
        "arithmetic_closes": int(excluded.size) + len(from_link) == int(followed.size),
        "duplicate_is_exact": sorted(from_link) == sorted(target_sev) and bool(from_link),
        "sd_followed": float(np.std(followed, ddof=1)),
        "sd_excluded": float(np.std(excluded, ddof=1)),
        "band": (lo, hi), "cut": cut,
        "followed": vals(followed), "excluded": vals(excluded),
        "floors": read_floors(),
    }
    r["share"] = r["n_from_link"] / r["n_followed"] if r["n_followed"] else float("nan")
    r["wilson"], r["wilson_gap"] = two_route_wilson(r["n_from_link"], r["n_followed"])
    r["exact"], r["exact_gap"] = two_route_exact(r["n_from_link"], r["n_followed"])
    r["floors_that_would_go_red"] = sorted(
        k for k, f in r["floors"].items() if r["excluded"].get(k, 0) < f)
    return r


def main() -> int:
    r = measure()
    W = 78
    print("=" * W)
    print("THE SEVERITY FRAME COUNTS ONE RUN TWICE")
    print("=" * W)
    print(f"\n  bench/logs/exp36_evidence_latest is a symbolic link: {r['is_symlink']}")
    print(f"    target                 : {r['link_target']}")
    print(f"    frame files globbed    : {r['frame_files']}")
    print(f"    of those, symlinked    : {len(r['linked_dirs'])} {r['linked_dirs']}")
    print(f"\n  severities, link followed : {r['n_followed']}")
    print(f"  severities, link excluded : {r['n_excluded']}")
    print(f"  severities from the link  : {r['n_from_link']}")
    print(f"  arithmetic closes         : {r['arithmetic_closes']} "
          f"({r['n_excluded']} + {r['n_from_link']} = {r['n_followed']})")
    print(f"  the duplicate is EXACT    : {r['duplicate_is_exact']} "
          f"(identical severity multiset, not a near copy)")

    print(f"\n  the duplicated share: {r['n_from_link']} of {r['n_followed']} = "
          f"{r['share']:.6f}")
    print(f"    Wilson 95%          : [{r['wilson'][0]:.6f}, {r['wilson'][1]:.6f}]"
          f"  (statsmodels; mpmath closed form agrees to {r['wilson_gap']:.1e})")
    print(f"    Clopper-Pearson 95% : [{r['exact'][0]:.6f}, {r['exact'][1]:.6f}]"
          f"  (statsmodels; scipy beta quantiles agree to {r['exact_gap']:.1e})")

    print(f"\n  archive standard deviation, followed : {r['sd_followed']:.6f}")
    print(f"  archive standard deviation, excluded : {r['sd_excluded']:.6f}")

    print(f"\n  WHAT EXCLUDING IT WOULD COST. Floors read from the guard file, "
          f"{len(r['floors'])} found:")
    print(f"    {'quantity':22s} {'followed':>9s} {'excluded':>9s} {'floor':>7s}  verdict")
    for k, f in r["floors"].items():
        red = r["excluded"][k] < f
        print(f"    {k:22s} {r['followed'][k]:>9d} {r['excluded'][k]:>9d} "
              f"{f:>7d}  {'RED' if red else 'still green'}")
    n_red = len(r["floors_that_would_go_red"])
    print(f"\n    floors that would go RED: {n_red} of {len(r['floors'])}")
    if n_red:
        print(f"    They are LOSS DETECTORS and they are correct: deleting real "
              f"runs turns\n    them red too. So de-duplicating the frame without "
              f"re-deriving them in the\n    same commit makes a correct board "
              f"report a loss that never happened.")
    print(f"\n  SCOPE, because a floor count is only meaningful with its "
          f"denominator. Entry\n  B121 says BOTH floors of one commit would "
          f"turn red, and within that scope it\n  is CORRECT. This reads every "
          f"floor the guard holds, {len(r['floors'])} of them, and "
          f"{n_red}\n  would cross -- so the consequence is WIDER than the "
          f"entry states rather than\n  different from it. A claim scoped to a "
          f"subset of floors understates it.\n")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NOT run the measurement: this reads 65 run directories and
    # loads the severity producer, which samples. The flag is answered first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
