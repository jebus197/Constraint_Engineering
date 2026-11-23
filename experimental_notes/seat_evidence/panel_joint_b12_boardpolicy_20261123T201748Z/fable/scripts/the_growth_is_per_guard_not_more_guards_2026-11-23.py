# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'panel_joint_b12_boardpolicy_20261123T201748Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 988552e9554bad5ef60011e86db66943fd38161b1ec72563ff03ddbd22a7adfd
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The board's current growth is per-guard cost, measured at a CONSTANT guard count.

DESTINATION `scripts/`. Written 2026-11-23, panel round `panel_b12_20261123T170728Z`.

WHY. `scripts/why_is_the_board_getting_slower_2026-11-23.py` established the
growth (1.6606 min/day over 113 boards) and decomposed it historically into
guard-count growth times per-guard growth -- but that decomposition cannot say
what is growing NOW, because both factors moved over the full window. The
ledger itself supplies the controlled experiment: since 2026-11-22T20:13Z the
hook has recorded a `guards` field, and it has been CONSTANT at 331 across
every determinate board since. Any duration growth inside that window is
per-guard cost by construction -- hypothesis (a), "more guards on the list",
is held at zero by the data rather than argued away.

WHAT IT REPORTS, each figure on 2 agreeing routes where 2 exist:

  1. The within-window slope (scipy linregress and statsmodels OLS, asserted
     to agree), with its CI and p, plus Spearman as a rank-route caveat --
     printed even when it disagrees, because at n~19 a parametric slope can
     outrun a rank test and the honest state is both numbers.
  2. The attribution coverage: how many determinate boards since B207 have a
     persisted `--durations` table in `.cdsfl_tmp/board_durations.log`. At
     the time of writing the answer was 0 of 19 -- the hook EMITTED the table
     on every board and deleted it (`rm -f "$_CDSFL_BOARD_LOG"`), which is why
     `hooks/board_durations_persist.sh` now exists. This figure rising from 0
     is how the repair proves it is wired; it staying 0 is how a silent
     telemetry failure surfaces without ever blocking a commit.

WHAT IT DOES NOT CLAIM. It does not name the per-guard cause. The candidate
consistent with growth at fixed guard count -- archive-parametrised guards
whose case count scales with notes and scripts added per batch -- is exactly
what the persisted durations tables will decide, guard by guard, and guessing
ahead of that data is the error this round's Q2 exists to stop.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

def _repo_root() -> pathlib.Path:
    """Marker walk, never `parents[N]` -- the counted form once computed every
    figure of a brief on an empty set (see
    `why_is_the_board_getting_slower_2026-11-23.py`, which records it)."""
    for base in (pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        for d in (base, *base.parents):
            if (d / "hooks" / "pre-commit").is_file() and (d / "bench").is_dir():
                return d
    raise RuntimeError("cannot locate the repository root")


REPO = _repo_root()
LEDGER = REPO / ".cdsfl_tmp" / "precommit_durations.jsonl"
DUR = REPO / ".cdsfl_tmp" / "board_durations.log"
INTERRUPTED_UNDER_SECONDS = 120   # same cut as the slower-board producer


def guarded_rows():
    """Determinate rows carrying the hook's own `guards` field."""
    if not LEDGER.is_file():
        return []
    out = []
    for line in LEDGER.read_text().splitlines():
        try:
            r = json.loads(line)
        except Exception:                                   # noqa: BLE001
            continue
        if "guards" not in r:
            continue
        try:
            s = float(r.get("seconds", 0))
            w = dt.datetime.fromisoformat(str(r["at"]).replace("Z", "+00:00"))
        except Exception:                                   # noqa: BLE001
            continue
        if s >= INTERRUPTED_UNDER_SECONDS:
            out.append((w, s, int(r["guards"])))
    out.sort()
    return out


def modal_guard_window(rows):
    """The rows at the MOST COMMON guard count -- the constant-count window."""
    from collections import Counter
    if not rows:
        return 0, []
    g, _ = Counter(g for _, _, g in rows).most_common(1)[0]
    return g, [(w, s) for w, s, gg in rows if gg == g]


def persisted_tables() -> int:
    if not DUR.is_file():
        return 0
    return len(re.findall(r"slowest \d+ durations", DUR.read_text(errors="replace")))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    import numpy as np
    from scipy import stats as sstats
    import statsmodels.api as sm

    rows = guarded_rows()
    g, win = modal_guard_window(rows)
    if len(win) < 8:
        print(f"only {len(win)} determinate boards at the modal guard count "
              f"({g}); nothing to regress yet")
        return 0

    x = np.array([(w - win[0][0]).total_seconds() / 86400.0 for w, _ in win])
    y = np.array([s / 60.0 for _, s in win])
    lr = sstats.linregress(x, y)
    ols = sm.OLS(y, sm.add_constant(x)).fit()
    agree = abs(ols.params[1] - lr.slope)
    assert agree < 1e-8, f"the 2 regression routes disagree by {agree}"
    rho, p2 = sstats.spearmanr(x, y)

    if not a.quiet:
        print("=" * 74)
        print("THE GROWTH AT A CONSTANT GUARD COUNT")
        print("=" * 74)
    print(f"  window: {len(win)} determinate boards, guard count CONSTANT at {g}, "
          f"spanning {x[-1]:.3f} days")
    print(f"  slope {lr.slope:.4f} min/day  p = {lr.pvalue:.4e}  "
          f"R^2 = {lr.rvalue**2:.4f}")
    print(f"  95% CI [{lr.slope - 1.96*lr.stderr:.4f}, "
          f"{lr.slope + 1.96*lr.stderr:.4f}] min/day   "
          f"(OLS agrees to {agree:.2e})")
    print(f"  rank route: Spearman rho = {rho:.4f}, p = {p2:.4e}"
          + ("  <- marginal; say so rather than hide it" if p2 > 0.05 else ""))
    print(f"  guard count change inside the window: 0 by construction, so this")
    print(f"  slope is hypothesis (b) -- existing guards getting slower -- with")
    print(f"  hypothesis (a), more guards, held at zero by the data.")
    n_tab = persisted_tables()
    print(f"\n  attribution coverage: {n_tab} persisted durations table(s) for "
          f"{len(win)} determinate boards in the window")
    if n_tab == 0:
        print("  0 is the honest pre-repair state: the board EMITS --durations=25")
        print("  (B207) and deleted the log that carried it. The persistence step")
        print("  (hooks/board_durations_persist.sh) accrues from the next board;")
        print("  if this stays 0 after boards run, the telemetry is broken and")
        print("  THAT is the finding, surfaced here instead of blocking commits.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__, takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
