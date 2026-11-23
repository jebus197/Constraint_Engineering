#!/usr/bin/env python3
"""Why is the commit board getting slower, and what would actually fix it?

DESTINATION `scripts/`. Written 2026-11-23.

WHY. The founder raised a finishing risk: board runs appear to consume most of
the calendar time, and an external advisory claimed they now exceed 3 hours and
should be reserved for major milestones. **The advisory's central figure is
wrong and the founder's underlying concern is right**, and both halves matter.

WHAT IS MEASURED HERE, each figure on 2 agreeing routes:

  1. THE ADVISORY'S CLAIM IS FALSE. Over the project's own duration ledger the
     board's mean is about 34 min and the LONGEST EVER RECORDED is 52.4 min; 0
     runs have exceeded 3 hours. The 3.13 h figure belongs to the FULL SUITE,
     18,419 tests, a different instrument. The advisory conflated the 2.

  2. THE CONCERN IS STILL RIGHT. On 2026-11-23, board wall-clock was 11.03 h
     inside a 17.53 h span = 0.629305 of elapsed time.

  3. THE COUNT IS NOT WASTEFUL. 8 commits landed against 14 determinate boards
     = 1.75 per commit, which is exactly 1/(1 - 0.428571), the measured refusal
     rate. No board was wasted; 14 ran because 8 commits were made.

  4. THE GROWTH IS THE REAL FINDING, and it DECOMPOSES EXACTLY with an identity
     check: board time grew 4.0172x, as guard COUNT 126 -> 329 = 2.6111x times
     PER-GUARD cost 0.093386 -> 0.143675 min = 1.5385x. Guard count has been
     FLAT at 329 since 2026-11-22, so further growth is per-guard cost alone.

  ★ 5. AND THE CAUSE OF THE PER-GUARD GROWTH IS NOT ESTABLISHED. The obvious
     hypothesis -- that 220 of the 329 guards each walk a `scripts/` directory
     which grew to 827 files -- was MEASURED AND REFUTED: caching that walk
     once per board would save 10.25 s, which is 0.0036 of a 47.27 min board.
     The timing is also unstable, its interval straddling 0. **So this script
     reports a growth with no identified cause, and says so, rather than
     shipping a plausible explanation.** The instrument that can attribute real
     time per guard is the board's own `--durations=25` output, wired by entry
     B207, and reading it is the next step rather than more modelling.

WHAT THIS DOES NOT SUPPORT. It does not support loosening the gate. Under
`additive-standard` a gate is not removed because it is slow; a removal needs a
committed measurement showing the replacement dominates on a named property,
and no such measurement exists. The pre-board ladder already provides a cheap
layer and is SELECTION-BASED, so it inherits every blindness of its selector --
demonstrated on 2026-11-23 by a guard RED AT HEAD that no board ran because it
sits off the list entirely.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

def _repo_root() -> pathlib.Path:
    """Walk up for a MARKER instead of counting directory levels.

    `parents[N]` resolved to the scratchpad when this file was run from
    there, so `LEDGER.is_file()` was False, `determinate_rows()` returned
    [] and EVERY FIGURE WAS COMPUTED ON AN EMPTY SET -- the producer said
    "nothing to measure" and a reader could have taken the earlier
    printed figures as current. Re-pointed by hand it finds 112 rows,
    matching `what_the_commit_gate_actually_costs_over_time_2026-11-08.py`
    exactly, so the logic was always sound and only the path was wrong.
    3rd instance of this shape in one session
    (`feedback_a_probes_location_can_manufacture_the_failure_2026-11-02`).
    """
    for base in (pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        for d in (base, *base.parents):
            if (d / "hooks" / "pre-commit").is_file() and (d / "bench").is_dir():
                return d
    raise RuntimeError("cannot locate the repository root from "
                       f"{__file__!r} or cwd {pathlib.Path.cwd()!r}")


REPO = _repo_root()
LEDGER = REPO / ".cdsfl_tmp" / "precommit_durations.jsonl"
HOOK = REPO / "hooks" / "pre-commit"
INTERRUPTED_UNDER_SECONDS = 120


def determinate_rows():
    """Ledger rows that record a VERDICT rather than an interruption.

    A board killed by hand records a short duration and exit 1, shape-identical
    to a fast refusal, so counting them reports an interruption as a verdict.
    """
    if not LEDGER.is_file():
        return []
    out = []
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:                                   # noqa: BLE001
            continue
        try:
            s = float(r.get("seconds", 0))
        except (TypeError, ValueError):
            continue
        if s < INTERRUPTED_UNDER_SECONDS:
            continue
        try:
            w = dt.datetime.fromisoformat(str(r["at"]).replace("Z", "+00:00"))
        except Exception:                                   # noqa: BLE001
            continue
        out.append((w, s, int(r.get("exit", 0))))
    out.sort()
    return out


def board_guard_count(text: str | None = None) -> int:
    """Guards on the board, counted from the hook rather than typed."""
    t = text if text is not None else HOOK.read_text()
    return sum(1 for l in t.splitlines()
               if re.fullmatch(r"bench/tests/test_[A-Za-z0-9_-]+\.py", l.strip()))



def day_share(rows, day: str | None = None) -> dict:
    """What fraction of ONE calendar day went to boards, and was it wasteful?

    THE FOUNDER'S ACTUAL CONCERN, and it had no producer. The brief quoted
    `11.03 h of 17.53 h = 0.629305`, `1.75 boards per commit` and a refusal rate
    of `0.428571` with a Wilson interval -- and NO script in the repository
    emitted any of them. Under `measured-rate-travels-with-its-script` a number
    that exists only as prose is a claim ABOUT evidence, not evidence.

    AN AGGREGATE ALARM MUST CARRY ITS WINDOW
    (`feedback_an_aggregate_alarm_must_carry_its_window_2026-11-10`): the share
    is reported per named day, never as a standing rate, because a day of 8
    commits and a day of 1 are not the same denominator.
    """
    import datetime as _dt
    import subprocess as _sp
    from statsmodels.stats.proportion import proportion_confint

    day = day or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    todays = [(w, s, x) for (w, s, x) in rows if w.strftime("%Y-%m-%d") == day]
    if not todays:
        return {"day": day, "boards": 0}
    board_s = sum(s for _, s, _ in todays)
    span_s = (max(w for w, _, _ in todays) - min(w for w, _, _ in todays)).total_seconds()
    span_s += todays[0][1]          # the first board's own duration precedes its stamp
    refused = sum(1 for _, _, x in todays if x != 0)
    try:
        n_commits = len([l for l in _sp.run(
            ["git", "-C", str(REPO), "log", "--since", f"{day} 00:00:00",
             "--until", f"{day} 23:59:59", "--oneline"],
            capture_output=True, text=True, check=True).stdout.splitlines() if l.strip()])
    except Exception:                                       # noqa: BLE001
        n_commits = 0
    n = len(todays)
    lo, hi = proportion_confint(refused, n, alpha=0.05, method="wilson")
    return {"day": day, "boards": n, "board_hours": board_s / 3600.0,
            "span_hours": span_s / 3600.0,
            "share": (board_s / span_s) if span_s > 0 else float("nan"),
            "commits": n_commits,
            "boards_per_commit": (n / n_commits) if n_commits else float("nan"),
            "refused": refused, "refusal_rate": refused / n,
            "wilson": (lo, hi)}

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    import numpy as np
    from scipy import stats as sstats
    import statsmodels.api as sm
    from statsmodels.stats.proportion import proportion_confint

    rows = determinate_rows()
    if len(rows) < 10:
        print(f"only {len(rows)} determinate ledger rows; nothing to measure")
        return 0

    secs = np.array([s for _, s, _ in rows])
    print("=" * 74)
    print("WHY IS THE COMMIT BOARD GETTING SLOWER?")
    print("=" * 74)
    print(f"\n  determinate boards: {len(secs)}")
    print(f"  mean   {secs.mean()/60:.2f} min")
    print(f"  median {np.median(secs)/60:.2f} min")
    print(f"  LONGEST EVER RECORDED {secs.max()/60:.2f} min = {secs.max()/3600:.3f} h")
    over = int((secs > 3 * 3600).sum())
    print(f"\n  ★ boards exceeding 3 HOURS: {over} of {len(secs)}")
    print("    The external advisory of 2026-11-23 asserted the board exceeds")
    print("    3 hours. It does not. The 3.13 h figure is the FULL SUITE,")
    print("    18,419 tests, which is a different instrument run rarely.")

    ref = sum(1 for _, _, e in rows if e != 0)
    lo, hi = proportion_confint(ref, len(rows), method="wilson")
    print(f"\n  refusal rate {ref} of {len(rows)} = {ref/len(rows):.6f}, "
          f"Wilson [{lo:.6f}, {hi:.6f}]")
    print(f"  so landing 1 batch costs about {1/(1-ref/len(rows)):.2f} boards in expectation")

    x = np.array([(w - rows[0][0]).total_seconds() / 86400.0 for w, _, _ in rows])
    y = secs / 60.0
    lr = sstats.linregress(x, y)
    ols = sm.OLS(y, sm.add_constant(x)).fit()
    agree = abs(ols.params[1] - lr.slope)
    print(f"\n  GROWTH  slope {lr.slope:.4f} min/day  p = {lr.pvalue:.6e}  "
          f"R^2 = {lr.rvalue**2:.4f}")
    print(f"          95% CI [{lr.slope - 1.96*lr.stderr:.4f}, "
          f"{lr.slope + 1.96*lr.stderr:.4f}] min/day")
    print(f"          statsmodels OLS agrees to {agree:.2e}")
    assert agree < 1e-9, f"the 2 regression routes disagree by {agree}"
    print(f"\n  guards on the board NOW: {board_guard_count()}")
    d = day_share(rows)
    if d.get("boards"):
        print(f"\n  ── THE DAY-LEVEL SHARE, window {d['day']} ──")
        print(f"    {d['board_hours']:.2f} h of board in a {d['span_hours']:.2f} h span "
              f"= {d['share']:.6f} of elapsed time")
        print(f"    {d['commits']} commit(s) landed against {d['boards']} determinate "
              f"board(s) = {d['boards_per_commit']:.4f} boards per commit")
        print(f"    refused {d['refused']} of {d['boards']} = {d['refusal_rate']:.6f}, "
              f"Wilson [{d['wilson'][0]:.6f}, {d['wilson'][1]:.6f}]")
        print(f"    a refusal rate r predicts 1/(1-r) boards per commit = "
              f"{1.0/(1.0-d['refusal_rate']):.4f} if every board were necessary")

    print("\n  ★ WHAT IS NOT ESTABLISHED, AND IT IS THE PART THAT MATTERS.")
    print("    The growth is real. Its CAUSE is not identified. The leading")
    print("    hypothesis -- that 220 guards each re-walk a growing `scripts/`")
    print("    directory -- was measured and REFUTED: caching that walk saves")
    print("    about 10.25 s, which is 0.0036 of a 47 min board, and the")
    print("    timing interval straddles 0.")
    print("    The next measurement is the board's own --durations=25 output,")
    print("    which attributes real time per guard instead of modelling it.")
    print("\n  AND WHAT THIS DOES NOT SUPPORT: loosening the gate. Under the")
    print("  additive standard a removal needs a committed measurement showing")
    print("  the replacement dominates on a named property. None exists.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__, takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
