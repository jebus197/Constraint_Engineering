#!/usr/bin/env python3
"""The gate's deciding series is not in the registry, so a verdict cannot be audited.

`_check_gamma_alt_convergence` decides convergence on `gamma_critical`, the
CRITICAL-ONLY decay curve, and the project's standing directive is that gamma is
load-bearing. But `runner_state.json` persists `gamma_history` -- the ALL-SEVERITY
curve -- and on study_run1b carries no `gamma_critical_history` at all. The
consequence was concrete: a replay script's `or` fallback substituted the
all-severity value (0.4274) under the label `gamma_critical` and it was reported as
the gate's input for hours, when the run's own log shows 0.732.

The founder's position is that the registry is the single source of truth for any
experiment a researcher may wish to run. That cannot hold while the deciding input
of the convergence gate lives only in a log line, so this measures how widespread
the omission is across the whole archive rather than asserting it from one run.

Runs that cannot be measured are counted and reported SEPARATELY rather than folded
into either arm: a directory with no state file is not a run that lacks the series.
"""
import glob
import json
import pathlib
import re
import sys

import numpy as np
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

# GUARDED BY `__main__`, and the reason is a real failure (2026-10-03).
# `bench/tests/test_operational_scripts.py::test_help_builds_and_lists_every_advertised_flag`
# import-probes every parser-less script in a subprocess started with
# `python3 -c ...`, where `sys.argv` is ['-c', '<this path>']. A module-level
# `answer_help` therefore sees the script's own path as an unrecognised argument
# and exits 2, so the script "no longer imports" as far as that guard is
# concerned. The project's convention is to call it from main() --
# scripts/a19_flag_admits_harmful_fixes_2026-09-22.py:81 does exactly that.
if __name__ == "__main__":
    answer_help(__doc__, __file__)

REPO = pathlib.Path(__file__).resolve().parents[1]
GAMMA_LOG = re.compile(r"gamma_critical:\s*([0-9.]+)")


def wilson(k, n):
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 30
    z = mp.mpf("1.959963984540054235309065817"); ph = mp.mpf(k) / n; nn = mp.mpf(n)
    c = (ph + z**2 / (2 * nn)) / (1 + z**2 / nn)
    hw = (z / (1 + z**2 / nn)) * mp.sqrt(ph * (1 - ph) / nn + z**2 / (4 * nn**2))
    assert abs(float(c - hw) - lo) < 1e-9 and abs(float(c + hw) - hi) < 1e-9, \
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}"
    return round(100 * lo, 4), round(100 * hi, 4)


has_crit = has_all = neither = 0
unreadable = 0
recoverable_from_log = 0
rows = []
dirs = sorted(p for p in (REPO / "bench" / "logs").iterdir() if p.is_dir())
for d in dirs:
    state = None
    for name in ("runner_state.json",):
        f = d / name
        if f.is_file():
            state = f
            break
    if state is None:
        for f in sorted(d.glob("*_report.json")):
            state = f
            break
    if state is None:
        continue                      # not a run we can measure; not an arm
    try:
        js = json.loads(state.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        unreadable += 1
        continue
    crit = bool(js.get("gamma_critical_history"))
    allg = bool(js.get("gamma_history"))
    has_crit += crit
    has_all += allg
    if not crit and not allg:
        neither += 1
    # could the real value be recovered from the log instead?
    rec = False
    log = d / "console.log"
    if not crit and log.is_file():
        try:
            rec = bool(GAMMA_LOG.search(log.read_text(errors="replace")))
        except Exception:
            rec = False
    recoverable_from_log += rec
    rows.append((d.name, crit, allg, rec))

n = len(rows)
print(f"run directories carrying a state or report file: {n}")
print(f"unreadable state files (counted separately): {unreadable}")
print()
k = n - has_crit
lo, hi = wilson(k, n)
print(f"MISSING gamma_critical_history (the gate's own series): {k}/{n} = "
      f"{100.0*k/n:.4f}%  Wilson [{lo}%, {hi}%]  (statsmodels == mpmath)")
lo2, hi2 = wilson(has_all, n)
print(f"carrying gamma_history (ALL-severity, not the gate's input): {has_all}/{n} "
      f"= {100.0*has_all/n:.4f}%  Wilson [{lo2}%, {hi2}%]")
print(f"carrying NEITHER series: {neither}")
print()
if k:
    lo3, hi3 = wilson(recoverable_from_log, k)
    print(f"of the {k} missing it, recoverable from the run log's "
          f"'gamma_critical:' line: {recoverable_from_log}/{k} = "
          f"{100.0*recoverable_from_log/k:.4f}%  Wilson [{lo3}%, {hi3}%]")
    print(f"  -> so {k - recoverable_from_log} run(s) have the gate's deciding "
          f"input in NO durable place at all.")
print()
arr = np.array([1 if c else 0 for _, c, _, _ in rows])
print(f"NumPy cross-check: sum(has_crit) = {int(arr.sum())}, "
      f"matches the counter {has_crit}")
assert int(arr.sum()) == has_crit, "numpy and the loop disagree"
print()
print("THE POINT, stated plainly: a reader given only the registry cannot check")
print("why a run converged or did not, because the series the gate reads is not")
print("there. A replay that falls back to gamma_history is not auditing the gate;")
print("it is auditing a different curve under the gate's name.")
