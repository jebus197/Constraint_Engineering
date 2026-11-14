#!/usr/bin/env python3
"""What the 2026-11-14 full suite found, set against the 2026-11-13 baseline.

The full suite ran 3:17:05 against commit `6304f771` and reported 32 failed,
17,760 passed, 40 skipped, 1 error. The previous full measurement, 2026-11-13 at
`846c4ffe`, reported 29 failed, 17,456 passed, 38 skipped, 1 error.

★ 29 -> 32 IS NOT 3 NEW FAILURES, AND READING IT THAT WAY IS THE ERROR THIS
SCRIPT EXISTS TO PREVENT. The 2 sets are compared by NODE ID, which gives 23
carried over, 7 that stopped failing and 10 that started. A net movement of 3
conceals 17 individual changes.

★ WHAT IT WILL NOT DO. It will not call a carried-over row PRE-EXISTING on the
strength of its name. `pytest -q` prints a bare `FAILED <nodeid>` with no
reason, so for most rows there is no reason text to compare, and a test can fail
at the same name for a new cause -- an error already made once in this project
and reversed when the content was re-measured. Rows are partitioned by identity
and the reason column is filled only where the log actually carries one.

★ BOARD VISIBILITY IS THE RESULT WORTH CARRYING. The pre-commit board is a
subset of the suite, so a failure outside it survives a green commit. This
script reports how many of the new failures sit in files the board names.

Reads 2 logs and the commit hook. Writes nothing. Runs no pytest.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "pre-commit"
#: A short-summary row. The node id is EVERYTHING after the verdict word, minus
#: an optional ` - <reason>` tail.
#:
#: ★ IT WAS `(\S+?)` UNTIL THIS SCRIPT WAS CROSS-CHECKED AGAINST A PLAIN LINE
#: COUNT, AND THAT FORM SILENTLY DROPPED A ROW FROM BOTH LOGS. A pytest node id
#: may carry SPACES inside a parametrize label --
#: `test_the_labelled_set[I23: exhausted_round_threshold defaults to 8 while
#: max_rounds is 8-True]` is a real one in this suite -- so `\S+?` could not
#: span it, the optional ` - ` tail could not absorb the remainder either, and
#: the whole line failed to match. The partition then read 22 carried over where
#: the truth was 23. An instrument that drops a row reports a smaller, tidier
#: number and gives no sign it has done so, which is why `parse_or_refuse`
#: below compares this against a line count and REFUSES on a mismatch.
ROW = re.compile(r"^(FAILED|ERROR)[ \t]+(.+?)[ \t]*$", re.M)
VERDICT_LINE = re.compile(r"^(?:FAILED|ERROR)[ \t]", re.M)


def split_reason(rest: str) -> tuple[str, str]:
    """Node id and reason. The separator is ` - `, AFTER any parametrize bracket.

    Searching from the start would cut a node id whose own label contains the
    separator; searching after the last `]` cannot.
    """
    start = rest.rfind("]") + 1
    i = rest.find(" - ", start)
    if i == -1:
        return rest.strip(), ""
    return rest[:i].strip(), rest[i + 3:].strip()
TAIL = re.compile(r"^\d[\d,]*\s+(?:failed|passed).*\bin [\d.]+s", re.M)


def rows(log_text: str) -> dict[str, dict]:
    """Node id -> {kind, reason}. Keyed by node id, because that is the identity."""
    out: dict[str, dict] = {}
    for m in ROW.finditer(log_text):
        nodeid, reason = split_reason(m.group(2))
        out[nodeid] = {"kind": m.group(1), "reason": reason}
    return out


def parse_or_refuse(log_text: str, label: str) -> dict[str, dict]:
    """Parse, then check the parse against a plain count of verdict LINES.

    2 forms of 1 count, compared -- the only way a dropped row shows itself.
    """
    parsed = rows(log_text)
    lines = len(VERDICT_LINE.findall(log_text))
    if len(parsed) != lines:
        raise SystemExit(
            f"REFUSED on {label}: {lines} verdict line(s) in the log but "
            f"{len(parsed)} parsed. A row was dropped or 2 rows collided on 1 "
            f"node id. Fix the parser; do not report the smaller number.")
    return parsed


def tail(log_text: str) -> str:
    lines = [ln.strip() for ln in log_text.splitlines() if TAIL.match(ln.strip())]
    return lines[-1] if lines else "(no summary line)"


def board_files() -> set[str]:
    """Test file names the pre-commit board names."""
    if not HOOK.is_file():
        return set()
    return set(re.findall(r"(test_[A-Za-z0-9_\-]+\.py)", HOOK.read_text(
        encoding="utf-8", errors="replace")))


def _wilson_two_ways(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo_s, hi_s = proportion_confint(k, n, alpha=0.05, method="wilson")
    mp.mp.dps = 40
    z = mp.sqrt(2) * mp.erfinv(mp.mpf("0.95"))
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo_m, hi_m = max(mp.mpf(0), (c - h) / d), min(mp.mpf(1), (c + h) / d)
    return (lo_s, hi_s), max(abs(float(lo_m) - lo_s), abs(float(hi_m) - hi_s))


def _cp_two_ways(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo_s, hi_s = proportion_confint(k, n, alpha=0.05, method="beta")
    mp.mp.dps = 40
    a = mp.mpf("0.025")

    def tail_at(p, lo_side):
        rng = range(k, n + 1) if lo_side else range(0, k + 1)
        return mp.fsum([mp.binomial(n, i) * p**i * (1 - p)**(n - i) for i in rng])

    def bisect(lo_side):
        lo, hi = mp.mpf(0), mp.mpf(1)
        for _ in range(240):
            mid = (lo + hi) / 2
            f_mid, f_lo = tail_at(mid, lo_side) - a, tail_at(lo, lo_side) - a
            if f_mid * f_lo <= 0:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    lo_e = mp.mpf(0) if k == 0 else bisect(True)
    hi_e = mp.mpf(1) if k == n else bisect(False)
    return (lo_s, hi_s), max(abs(float(lo_e) - lo_s), abs(float(hi_e) - hi_s))


def report(k: int, n: int, label: str) -> None:
    (wl, wh), wd = _wilson_two_ways(k, n)
    (cl, ch), cd = _cp_two_ways(k, n)
    print(f"    {label}: {k} of {n} = {k / n if n else 0.0:.6f}")
    print(f"        Wilson          [{wl:.6f}, {wh:.6f}]  (statsmodels; "
          f"hand-rolled mpmath agrees to {wd:.3e})")
    print(f"        Clopper-Pearson [{cl:.6f}, {ch:.6f}]  (beta quantile; "
          f"exact binomial tails agree to {cd:.3e})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--today", required=True, help="the 2026-11-14 pytest log")
    ap.add_argument("--baseline", required=True, help="the 2026-11-13 pytest log")
    a = ap.parse_args([] if argv is None else argv)

    t_txt = pathlib.Path(a.today).read_text(encoding="utf-8", errors="replace")
    b_txt = pathlib.Path(a.baseline).read_text(encoding="utf-8", errors="replace")
    today = parse_or_refuse(t_txt, "today")
    base = parse_or_refuse(b_txt, "the baseline")
    if not today or not base:
        print("  REFUSED: a log carries no FAILED/ERROR rows. A silent 0 here "
              "would read as a green suite.")
        return 2

    carried = sorted(set(today) & set(base))
    fixed = sorted(set(base) - set(today))
    new = sorted(set(today) - set(base))

    print(f"  today    : {tail(t_txt)}")
    print(f"             rows parsed: {len(today)}")
    print(f"  baseline : {tail(b_txt)}")
    print(f"             rows parsed: {len(base)}")
    print()
    print(f"  CARRIED OVER (same node id in both): {len(carried)}")
    print(f"  STOPPED FAILING                    : {len(fixed)}")
    print(f"  STARTED FAILING                    : {len(new)}")
    print(f"  arithmetic closes: {len(carried)} + {len(new)} = {len(today)} today, "
          f"{len(carried)} + {len(fixed)} = {len(base)} baseline -> "
          f"{len(carried) + len(new) == len(today) and len(carried) + len(fixed) == len(base)}")
    print()
    print("  STARTED FAILING, in full:")
    for n in new:
        print(f"    {today[n]['kind']:<6} {n}")
    print()
    print("  STOPPED FAILING, in full:")
    for n in fixed:
        print(f"    {base[n]['kind']:<6} {n}")
    print()

    bf = board_files()
    print(f"  pre-commit board names {len(bf)} distinct test files.")
    on_board = [n for n in new if n.split("::")[0].split("/")[-1] in bf]
    off_board = [n for n in new if n not in on_board]
    report(len(on_board), len(new),
           "new failures the board could have caught")
    for n in off_board:
        print(f"        INVISIBLE TO THE BOARD: {n.split('::')[0].split('/')[-1]}")
    print()
    with_reason = [n for n in today if today[n]["reason"]]
    print(f"  rows whose reason text the log carries: {len(with_reason)} of "
          f"{len(today)} -- `pytest -q` prints a bare FAILED row, so a carried-over")
    print("  row may NOT be called pre-existing from this log alone. Re-run it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
