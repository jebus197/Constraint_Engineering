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

def _roster_size() -> int:
    """How many seats the orchestrator ACTUALLY defines, asked of it directly.

    WAS A TYPED 5 UNTIL 2026-09-20, and it went stale the day Fable joined,
    taking 5 tests with it. The constant existed to make an omission loud: this
    script slices the seat block from `label="CC2"` to the next `def `, so a
    seat defined outside that window vanishes and every proportion below gets a
    smaller denominator in silence.

    A TYPED NUMBER CANNOT DO THAT JOB, because it goes stale for 2 different
    reasons and the message cannot tell them apart: the parser missed a seat, or
    the roster legitimately grew. Importing the roster distinguishes them --
    a mismatch now means the PARSER is short, which is the thing worth shouting
    about, and a roster change is absorbed without a false alarm.

    Falls back to the historical 5 if the orchestrator cannot be imported, and
    says so, because a failed lookup is not a measurement.
    """
    try:
        sys.path.insert(0, str(REPO))
        from bench.experiment_11_orchestrator import load_default_config
        return len(load_default_config().models)
    except Exception as exc:                                   # noqa: BLE001
        print(f"  !! could not read the live roster ({type(exc).__name__}: "
              f"{exc}); falling back to the historical 5, which may be stale",
              file=sys.stderr)
        return 5


EXPECTED_SEATS = _roster_size()

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
    # LOUD ON OMISSION (2026-09-10, panel round 4, fable F3). The block is sliced
    # from `label="CC2"` to the next `def `, so a seat defined outside that window
    # simply vanishes and every proportion silently gets a smaller denominator.
    # EXPECTED_SEATS is now read from the orchestrator itself, so a mismatch is
    # a fact about THIS SCRIPT'S REACH rather than about the configuration --
    # which is what the alarm was always meant to say.
    if len(out) != EXPECTED_SEATS:
        print(f"  !! this script found {len(out)} seat(s), not {EXPECTED_SEATS}: "
              f"{[o[0] for o in out]}\n     the slice window in seats() no longer "
              f"covers the whole panel; every proportion below is over a partial "
              f"denominator.", file=sys.stderr)
    return out


def multipliers():
    """Read the watchdog multipliers from the runner rather than typing them."""
    src = RUNNER.read_text()
    # THE FIX BROKE THE SCRIPT THAT MEASURES IT, which is
    # `measured-rate-travels-with-its-script` failing in the most circular way
    # available. This pattern matched the PRE-FIX expression
    # `wall_limit = (mc.timeout * 5 if ... else mc.timeout * 3)`. The 6.2 repair
    # replaced it with a `_mult` / `_retry_budget` / `max(...)` form on
    # 2026-09-09, so from that commit onward the script exited 1 with "the
    # watchdog expression has moved" and produced no figures at all — while the
    # task-list entry went on citing figures it was supposed to be producing.
    # Found 2026-09-10 by 2 independent agents measuring the entry's claims.
    #
    # BOTH FORMS ARE ACCEPTED so the script also runs against any archived
    # revision, and it says which form it found rather than silently assuming.
    # THE COMBINING OPERATOR IS READ, NOT TYPED (2026-09-10, panel round 4, CC2 F2).
    # The 2 multipliers were read from the runner and the `max` that combines them
    # with the retry budget was typed into this script. A seat mutated the runner's
    # `max` to `min` and this instrument still reported "fits" for every seat and
    # "truncated: 0 of 5" -- reporting no truncation while the runner truncated
    # Gemini from 1500 s to 900 s. An instrument that hardcodes half of the
    # expression it claims to read cannot detect that expression regressing.
    post = re.search(
        r"_mult = (\d+) if base_model_label\(mc\.label\) == \"CC2\" else (\d+)\n"
        r"\s*_retry_budget = [^\n]+\n"
        r"\s*wall_limit = (max|min)\(mc\.timeout \* _mult, _retry_budget\)", src)
    if post:
        return (int(post.group(1)), int(post.group(2)),
                f"post-2026-09-09 ({post.group(3)} of multiplier and retry budget)",
                post.group(3))
    pre = re.search(r"wall_limit = \(mc\.timeout \* (\d+) if base_model_label\("
                    r"mc\.label\) == \"CC2\"\s*\n\s*else mc\.timeout \* (\d+)\)", src)
    if pre:
        # The pre-fix form has no combining operator at all: the cap IS the
        # multiplier product. `None` says so rather than inventing one.
        return int(pre.group(1)), int(pre.group(2)), "pre-2026-09-09 (multiplier only)", None
    raise SystemExit("the watchdog expression at reference_runner_v3.py has moved, "
                     "and neither the pre- nor post-2026-09-09 form was found")


def main():
    cc2_mult, other_mult, form, op = multipliers()
    print(f"watchdog multipliers, read from the runner: CC2 x{cc2_mult}, "
          f"every other seat x{other_mult}")
    print(f"expression form found: {form}\n")
    rows, truncated = [], 0
    for label, timeout, retries in seats():
        mult = cc2_mult if label == "CC2" else other_mult
        budget = timeout * retries
        # POST-FIX the runner takes max(multiplier cap, retry budget), so the
        # cap can no longer sit below the budget. Modelling only the multiplier
        # would report a truncation the shipped code no longer performs.
        mult_cap = timeout * mult
        # The operator comes from the runner. If the runner regresses to `min`,
        # this instrument reports the truncation instead of hiding it.
        cap = mult_cap if op is None else (max if op == "max" else min)(mult_cap, budget)
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
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
