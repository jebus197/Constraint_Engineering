#!/usr/bin/env python3
"""Task 6.2: does the seat watchdog truncate the configured retry budget?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE TWO NUMBERS ARE SET IN DIFFERENT FILES AND NEVER COMPARED.
`bench/experiment_11_orchestrator.py` gives each seat a `timeout` and a
`max_retries`, so the worst-case time a seat may legitimately consume is
timeout * max_retries -- every attempt running to its full timeout.
`bench/reference_runner_v3.py:8336` independently caps the wall clock at
`timeout * 5` for CC2 and `timeout * 3` for everyone else. Where the cap is
below the budget, the watchdog kills a seat that was still inside the retry
allowance it was configured with, and the run records a timeout rather than a
misconfiguration.

The task list states this truncates the budget "for 4 of 5 seats". This script
exists to check that figure rather than repeat it.
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ORCH = REPO / "bench" / "experiment_11_orchestrator.py"
RUNNER = REPO / "bench" / "reference_runner_v3.py"

SEAT_RE = re.compile(
    r'label="(?P<label>[A-Za-z0-9_-]+)".*?'
    r'timeout=(?P<timeout>\d+).*?'
    r'max_retries=(?P<retries>\d+)',
    re.DOTALL)


def seats():
    src = ORCH.read_text()
    start = src.index("label=\"CC2\"")
    block = src[start - 200: src.index("def ", start)]
    out = []
    for m in SEAT_RE.finditer(block):
        out.append((m.group("label"), int(m.group("timeout")), int(m.group("retries"))))
    return out


def multipliers():
    """Read the watchdog multipliers from the runner rather than typing them."""
    src = RUNNER.read_text()
    m = re.search(r"wall_limit = \(mc\.timeout \* (\d+) if base_model_label\("
                  r"mc\.label\) == \"CC2\"\s*\n\s*else mc\.timeout \* (\d+)\)", src)
    if not m:
        raise SystemExit("the watchdog expression at reference_runner_v3.py has moved")
    return int(m.group(1)), int(m.group(2))


def main():
    cc2_mult, other_mult = multipliers()
    print(f"watchdog multipliers, read from the runner: CC2 x{cc2_mult}, "
          f"every other seat x{other_mult}\n")
    rows, truncated = [], 0
    for label, timeout, retries in seats():
        mult = cc2_mult if label == "CC2" else other_mult
        budget = timeout * retries
        cap = timeout * mult
        is_trunc = cap < budget
        truncated += is_trunc
        rows.append((label, timeout, retries, budget, cap, is_trunc))
        print(f"  {label:9s} timeout={timeout:4d}  retries={retries}  "
              f"budget={budget:5d}s  watchdog={cap:5d}s  "
              f"{'TRUNCATED by ' + str(budget - cap) + 's' if is_trunc else 'fits'}")

    n = len(rows)
    print(f"\ntruncated: {truncated} of {n}")
    if not n:
        return

    # TWO TOOLS, as the project requires for any computational claim.
    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(truncated, n, method="wilson")
    lo_c, hi_c = proportion_confint(truncated, n, method="beta")
    print(f"proportion          : {truncated / n:.4f}")
    print(f"Wilson 95%          : [{lo_w*100:.1f}%, {hi_w*100:.1f}%]  (statsmodels)")
    print(f"Clopper-Pearson 95% : [{lo_c*100:.1f}%, {hi_c*100:.1f}%]  (statsmodels/beta)")

    from scipy.stats import beta as sbeta
    lo_s = 0.0 if truncated == 0 else sbeta.ppf(0.025, truncated, n - truncated + 1)
    hi_s = 1.0 if truncated == n else sbeta.ppf(0.975, truncated + 1, n - truncated)
    print(f"Clopper-Pearson 95% : [{lo_s*100:.1f}%, {hi_s*100:.1f}%]  (scipy, cross-check)")
    print(f"the two tools agree to 1e-9: "
          f"{abs(lo_s - lo_c) < 1e-9 and abs(hi_s - hi_c) < 1e-9}")

    # The exact-equality cases matter: a cap EQUAL to the budget is not
    # truncation, but it leaves 0 seconds of slack for dispatch overhead.
    tight = [r[0] for r in rows if r[4] == r[3]]
    print(f"\nseats where the cap EQUALS the budget exactly (0 slack): {tight or 'none'}")


if __name__ == "__main__":
    sys.exit(main())
