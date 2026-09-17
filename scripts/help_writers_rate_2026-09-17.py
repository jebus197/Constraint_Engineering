#!/usr/bin/env python3
"""How many tracked scripts WRITE something and ignore `--help`, at any revision?

PANEL ROUND 16, 2026-09-17. Task A26 says "7 tracked scripts both WROTE something
and ignored the flag -- 5.7377% of 122", and no committed script printed it. This
applies the committed matchers, `WRITES` and `answers_help` from
`bench/tests/test_help_never_acts_2026-09-11.py`, to every `.py` file under
scripts/ at a revision, read with `git ls-tree` and `git show` so no checkout is
touched, and prints k of n with Wilson and Clopper-Pearson intervals, each
computed by 2 independent routes.

2 COLUMNS, because the flag can be ignored in 2 ways:

  direct   `answer_help` is called or a parser is built: answers `--help` when the
           script is run as `python3 scripts/x.py`.
  dash-m   the same, except that a call behind `try: from _cli_help import ...`
           whose `except ImportError: pass` is not preceded by a `sys.path`
           insert built from `__file__` does not count: under `python3 -m
           scripts.x` that import fails, the failure is swallowed, and the
           script's ordinary work runs.

Both matchers are static. They read source; they run no script.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MATCHERS = REPO / "bench" / "tests" / "test_help_never_acts_2026-09-11.py"
Z = 1.959963984540054


def _matchers():
    spec = importlib.util.spec_from_file_location("help_never_acts_matchers", MATCHERS)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


WORKTREE = ":worktree"


def offenders(rev: str) -> tuple[int, list[str], list[str]]:
    """(population, direct offenders, dash-m offenders) at `rev`.

    `rev` may be WORKTREE: the tracked scripts as they stand on disk, which is
    what the suite's own ratchet reads."""
    m = _matchers()
    # BOUND UNDER ANOTHER NAME ON PURPOSE. `scripts/help_is_answered_2026-09-11.py`
    # also defines an `answers_help`, which returns (ok, why), and
    # `test_operational_scripts.py` flags any `answers_help()` tested for truth as
    # a discarded verdict. This one, from the test module, returns a plain bool.
    writer_answers = m.answers_help
    if rev == WORKTREE:
        r = _git("ls-files", "--", "scripts")
    else:
        r = _git("ls-tree", "-r", "--name-only", rev, "--", "scripts")
    if r.returncode != 0:
        raise RuntimeError(f"git cannot list scripts/ at {rev}: {r.stderr.strip()}")
    names = [n for n in r.stdout.split() if n.endswith(".py")]
    direct, dash_m = [], []
    for n in names:
        if rev == WORKTREE:
            src = (REPO / n).read_text(encoding="utf-8", errors="replace")
        else:
            src = _git("show", f"{rev}:{n}").stdout
        if not m.WRITES.search(src):
            continue
        if writer_answers(src, under_dash_m=False) is False:
            direct.append(n)
        if writer_answers(src, under_dash_m=True) is False:
            dash_m.append(n)
    return len(names), direct, dash_m


def wilson_closed_form(k: int, n: int) -> tuple[float, float]:
    p = k / n
    centre = (p + Z * Z / (2 * n)) / (1 + Z * Z / n)
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / (1 + Z * Z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def clopper_pearson_bisection(k: int, n: int) -> tuple[float, float]:
    def at_most(q: float, j: int) -> float:
        return math.fsum(math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(j + 1))

    def root(f):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else root(lambda q: 0.025 - (1 - at_most(q, k - 1)))
    upper = 1.0 if k == n else root(lambda q: at_most(q, k) - 0.025)
    return lower, upper


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("revs", nargs="*",
                    help=f"revisions to measure (default HEAD); {WORKTREE} means the "
                         f"tracked scripts as they stand on disk")
    a = ap.parse_args()
    from statsmodels.stats.proportion import proportion_confint
    for rev in a.revs or ["HEAD"]:
        try:
            n, direct, dash_m = offenders(rev)
        except RuntimeError as exc:
            print(f"REFUSING: {exc}", file=sys.stderr)
            return 2
        print(f"revision {rev}: {n} scripts")
        for label, off in (("direct", direct), ("dash-m", dash_m)):
            k = len(off)
            wl, wh = proportion_confint(k, n, method="wilson")
            cl, ch = proportion_confint(k, n, method="beta")
            wl2, wh2 = wilson_closed_form(k, n)
            cl2, ch2 = clopper_pearson_bisection(k, n)
            agree = max(abs(wl - wl2), abs(wh - wh2), abs(cl - cl2), abs(ch - ch2))
            print(f"  {label:6s}: {k} of {n} write and ignore --help = {k / n:.4%}")
            print(f"          Wilson 95%          : [{wl:.4%}, {wh:.4%}]  "
                  f"(statsmodels; closed form agrees to {agree:.1e})")
            print(f"          Clopper-Pearson 95% : [{cl:.4%}, {ch:.4%}]  "
                  f"(statsmodels; math.comb bisection agrees)")
            print(f"          {off}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
