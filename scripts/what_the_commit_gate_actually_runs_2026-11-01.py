#!/usr/bin/env python3
"""What fraction of this project's tests does the commit gate actually run?

WHY IT EXISTS. The gate's figure was reported as "the full suite is green" on
2026-11-01. It is not the full suite: `hooks/pre-commit` runs a GUARDS list, and
that list is a deliberately cheap slice. Nothing in the project measured the
slice, so the phrase went unchallenged twice in one session. This script is the
measurement, so the share travels with a producer rather than as prose.

WHAT IT DOES NOT CLAIM. A share of tests is NOT a share of risk. The guards are
chosen because they are the cheap ones that catch the recurring faults, so a
1-in-6 share may well cover most of what breaks; this script cannot say, and
does not try. It answers exactly one question -- how much of the suite the gate
executes -- and the interval it prints is about that and nothing else.

HOW THE 2 COUNTS ARE OBTAINED, both by EXECUTION rather than by reading.
`GUARDS` is parsed out of the hook, then each path is checked to exist, so a
stale entry is reported rather than inflating the numerator. The denominators
come from globbing `bench/tests/test_*.py` and from pytest's own collection, so
the case-level figure is pytest's count and not an estimate.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "pre-commit"
_GUARDS_BLOCK = re.compile(r'^GUARDS="(.*?)"', re.S | re.M)
_TEST_PATH = re.compile(r"bench/tests/test_[\w./-]+\.py")
_COLLECTED = re.compile(r"(\d[\d,]*)\s+tests? collected")


def interval(k: int, n: int) -> str:
    """Wilson and Clopper-Pearson, each in 2 independent implementations."""
    import mpmath as mp
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    sm = proportion_confint(k, n, method="wilson")
    cp = proportion_confint(k, n, method="beta")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054")
    K, N = mp.mpf(k), mp.mpf(n)
    ph = K / N
    d = 1 + z**2 / N
    c = (ph + z**2 / (2 * N)) / d
    h = z * mp.sqrt(ph * (1 - ph) / N + z**2 / (4 * N**2)) / d
    lo2 = float(stats.beta.ppf(0.025, k, n - k + 1))
    hi2 = float(stats.beta.ppf(0.975, k + 1, n - k))
    return (f"{k} of {n} = {k/n:.6f}\n"
            f"      Wilson  statsmodels [{sm[0]:.6f}, {sm[1]:.6f}] "
            f"mpmath [{float(c-h):.6f}, {float(c+h):.6f}] "
            f"agree to {max(abs(sm[0]-float(c-h)), abs(sm[1]-float(c+h))):.1e}\n"
            f"      Clopper statsmodels [{cp[0]:.6f}, {cp[1]:.6f}] "
            f"scipy  [{lo2:.6f}, {hi2:.6f}] "
            f"agree to {max(abs(cp[0]-lo2), abs(cp[1]-hi2)):.1e}")


def guard_files() -> tuple[list[str], list[str]]:
    """(guard paths that exist, guard paths that do not)."""
    m = _GUARDS_BLOCK.search(HOOK.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("could not find the GUARDS list in hooks/pre-commit")
    paths = sorted(set(_TEST_PATH.findall(m.group(1))))
    live = [p for p in paths if (REPO / p).is_file()]
    dead = [p for p in paths if not (REPO / p).is_file()]
    return live, dead


def collected(paths: list[str] | None) -> int:
    cmd = [sys.executable, "-m", "pytest", "-q", "--collect-only",
           "-p", "no:cacheprovider"]
    cmd += paths if paths else ["bench/tests"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    hits = _COLLECTED.findall(r.stdout or "")
    if not hits:
        raise SystemExit("pytest printed no collection count:\n"
                         + (r.stdout or r.stderr)[-1500:])
    return int(hits[-1].replace(",", ""))


def main() -> int:
    live, dead = guard_files()
    all_files = sorted(p.relative_to(REPO).as_posix()
                       for p in (REPO / "bench" / "tests").glob("test_*.py"))
    print("=" * 74)
    print("WHAT THE COMMIT GATE ACTUALLY RUNS")
    print("=" * 74)
    if dead:
        print(f"\n★ {len(dead)} GUARDS entry/entries name a file that does not exist,")
        print("  so the hook's own list is stale:")
        for p in dead:
            print(f"    {p}")
    print(f"\n  by FILE : {interval(len(live), len(all_files))}")
    gate_cases = collected(live)
    all_cases = collected(None)
    print(f"\n  by CASE : {interval(gate_cases, all_cases)}")
    print("\n  A SHARE OF TESTS IS NOT A SHARE OF RISK: the guards are chosen")
    print("  because they are cheap and catch the recurring faults. This says")
    print("  how much of the suite runs, and nothing about what it covers.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
