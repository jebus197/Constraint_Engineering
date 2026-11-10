#!/usr/bin/env python3
"""B81 half 2: `sv`'s commit timeout killed `git` and left the BOARD running.

WHAT THIS MEASURES, and it is measured by EXECUTION rather than by reading the
`subprocess` documentation, because this project's record is that a predicate
read is a predicate assumed.

THE OBSERVED FAILURE. On 2026-11-10 at 06:42 and again at 06:46, `sv --commit
--push` died with `subprocess.TimeoutExpired` at 300 s while `hooks/pre-commit`
was running a 1,791 s pytest board. The timeout killed `git commit`. It did NOT
kill the hook or the board, which were reparented to pid 1 and kept running --
burning a core they could never produce a commit with, and then competing with
the retry for this machine's 8 cores. The founder's machine is a FIXED RESOURCE
of 8 cores and 8 GiB by his ruling of 2026-10-11, so a timeout that abandons
its own work still running is a leak against that resource. This half of B81
needs no ruling from him to be a defect; the LIMIT half does and is untouched.

THE 3 CONFIGURATIONS, and the middle one is the point. A parent that spawns a
long-lived grandchild and then waits -- the exact shape of
`sv -> git commit -> hooks/pre-commit -> pytest` -- is run under a 1 s timeout:

  A  what the code did: `proc.kill()` on the direct child only
  B  `start_new_session=True` but STILL only `proc.kill()`
  C  `start_new_session=True` plus `os.killpg` on the group  (the fix)

B IS THE DISCRIMINATION CONTROL. Without it the measurement cannot tell a fix
from a coincidence: a verdict that took the same value for the session alone
and for the session plus the group kill would carry 0 bits about which half is
load-bearing. B leaks, so the session alone is NOT the fix, and the group kill
is what does the work.

THE ROOT CAUSE, MEASURED FROM THE LIVE LEDGER AS WELL. The leak is why the
abandoned board kept running; it is not why the timeout fired at 300 s in the
first place. `hooks/pre-commit` writes `.cdsfl_tmp/precommit_seconds` from its
EXIT trap on EVERY run, so an EARLY REFUSAL overwrites the number with the cost
of refusing. `sv` then computed `max(300, 4 x that)`. Section 2 below reads the
ledger this repository actually holds and counts, over every position in it,
how often the last-row rule would have licensed a timeout SHORTER than a board
already recorded in the same window.

★ AND A PROPERTY THIS SCRIPT FIRST STATED TOO STRONGLY, CORRECTED HERE. The
first version said a refusal is SHORTER than a board by construction. That is
FALSE: the live ledger holds refusals at 1,672 s and 1,675 s, which are
LONGER than clean boards at 1,649 s, because the desktop-mirror check refuses
AFTER the board has run. The property the maximum actually needs is the weaker
and true one -- an EARLY refusal can only be SMALLER than a board and so can
never raise the maximum, while a LATE refusal costs a board plus a check and is
exactly what `sv` must wait for. Either way the maximum is right and no
duration threshold or exit code has to be interpreted.

Run: python3 scripts/the_commit_timeout_left_the_board_running_2026-11-10.py
Exit 0 when A and B leak and C does not -- that is the finding. Exit 1 when the
pattern does not hold, because a probe that cannot discriminate has measured
nothing and must say so rather than report a number.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import signal
import subprocess
import tempfile
import time

#: How long the grandchild is told to live. Long enough that survival is
#: unambiguous, short enough that an escaped process cannot outlive a session.
GRANDCHILD_SECONDS = 120
#: The timeout the parent is run under.
PARENT_TIMEOUT_SECONDS = 1
#: Settling time before survival is tested, so a dying process is not read as
#: a living one.
SETTLE_SECONDS = 0.6


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:              # exists, not ours to signal
        return True
    return True


def _reap(pid: int | None, pgid: int | None) -> None:
    """Leave nothing behind, whatever the outcome of the measurement."""
    if pgid is not None and pgid != os.getpgid(0):
        try:
            os.killpg(pgid, signal.SIGKILL)
        except OSError:
            pass
    if pid is not None:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def one_run(workdir: pathlib.Path, new_session: bool, kill_group: bool) -> bool:
    """Run the parent under a timeout. Return True if the grandchild SURVIVED."""
    mark = workdir / "grandchild.pid"
    parent = workdir / "parent.sh"
    parent.write_text(
        "#!/bin/sh\n"
        f"sh -c 'echo $$ > {mark}; sleep {GRANDCHILD_SECONDS}' &\n"
        "wait\n"
    )
    parent.chmod(0o755)
    mark.unlink(missing_ok=True)

    kw = {"start_new_session": True} if new_session else {}
    proc = subprocess.Popen(
        [str(parent)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw
    )
    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        pgid = None

    gpid = None
    for _ in range(200):
        if mark.exists() and mark.read_text().strip():
            gpid = int(mark.read_text().strip())
            break
        time.sleep(0.05)
    if gpid is None:
        _reap(None, pgid if new_session else None)
        raise SystemExit("the probe's grandchild never announced itself")

    try:
        proc.communicate(timeout=PARENT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        if kill_group and pgid is not None and pgid != os.getpgid(0):
            os.killpg(pgid, signal.SIGKILL)
        else:
            proc.kill()
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pass

    time.sleep(SETTLE_SECONDS)
    survived = _alive(gpid)
    _reap(gpid, pgid if new_session else None)
    return survived


def _repo_root() -> pathlib.Path | None:
    start = pathlib.Path(__file__).resolve().parent
    for cand in (start, *start.parents):
        if (cand / "bench" / "domain_immune.py").is_file():
            return cand
    return None


def _interval_line(k: int, n: int) -> str:
    """k of n with 2 independent interval routes. NOT named `_iv`.

    `_iv(k, n)` is a RESERVED contract in this project -- 50 scripts implement
    it returning ((wilson_lo, wilson_hi), (cp_lo, cp_hi), cross_check) and a
    committed guard calls every one of them. A local formatter under that name
    breaks the contract, which happened 3 times on 2026-11-10, so this one is
    deliberately named otherwise.
    """
    import numpy as np
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint
    sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    cp = proportion_confint(k, n, alpha=0.05, method="beta")
    z = st.norm.ppf(0.975)
    pr = k / n
    den = 1 + z * z / n
    cen = (pr + z * z / (2 * n)) / den
    hw = z * np.sqrt(pr * (1 - pr) / n + z * z / (4 * n * n)) / den
    return (f"{k} of {n} = {pr:.6f}  Wilson [{sm[0]:.6f}, {sm[1]:.6f}] "
            f"vs written-out [{max(0.0, cen - hw):.6f}, "
            f"{min(1.0, cen + hw):.6f}]  Clopper-Pearson "
            f"[{(cp[0] or 0.0):.6f}, {cp[1]:.6f}]")


def _report_the_sizing_defect() -> None:
    """Count, over the whole ledger, how often the last-row rule under-sized.

    Reports a STATE and never fails: the ledger is scratch under `.cdsfl_tmp`,
    so a clone that has made no commit has nothing to read, and that is a state
    rather than a fault. THE BOUND IS STATED because it matters -- these
    figures are reproducible only on a machine that holds this ledger, which is
    the same limitation B81 already records against its own earlier series.
    """
    print()
    print("-" * 76)
    print("  2. WHY THE TIMEOUT FIRED AT ALL: AN EARLY REFUSAL OVERWROTE THE")
    print("     RECORDED DURATION  (counted over this repository's own ledger)")
    print("-" * 76)
    root = _repo_root()
    if root is None:
        print("  no repository located; nothing to read")
        return
    led = root / ".cdsfl_tmp" / "precommit_durations.jsonl"
    if not led.is_file():
        print("  no ledger under .cdsfl_tmp — a clone that has made no commit")
        print("  has nothing to read, which is a state and not a fault")
        return

    rows: list[tuple[str, int, int, str]] = []
    for line in led.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            rows.append((str(d.get("at", "?")), int(d.get("seconds", 0)),
                         int(d.get("exit", 0)), str(d.get("why", ""))))
        except (ValueError, TypeError, AttributeError):
            continue
    if len(rows) < 2:
        print(f"  the ledger holds {len(rows)} parseable row(s); too few to count")
        return

    floor, headroom, win = 300, 4, 10
    under = []
    for i in range(1, len(rows)):
        window = rows[max(0, i - win + 1):i + 1]
        win_max = max(r[1] for r in window)
        last_rule = max(floor, headroom * rows[i][1])
        if last_rule < win_max:
            under.append((rows[i], win_max, last_rule))

    n = len(rows) - 1
    print(f"  parseable ledger rows : {len(rows)}")
    print(f"  positions examined    : {n}  (every row but the first)")
    print()
    print("  POSITIONS WHERE THE LAST-ROW RULE LICENSED A TIMEOUT SHORTER THAN")
    print("  A BOARD ALREADY IN THE SAME WINDOW:")
    print(f"    {_interval_line(len(under), n)}")
    for (at, secs, _rc, why), win_max, last_rule in under:
        print(f"    {at}  recorded {secs:5d} s"
              f"{('  [' + why + ']') if why else ''}")
        print(f"      -> last-row timeout {last_rule:5d} s against a "
              f"{win_max} s board in the same window "
              f"(short by a factor of {win_max / last_rule:.4f})")
    if not under:
        print("    none in the CURRENT ledger. That is a state, not a")
        print("    refutation: the window in force when this ran holds no early")
        print("    refusal, and a window with none cannot exhibit the defect.")
    print()
    print("  THE BOUND: this ledger is scratch under .cdsfl_tmp and is not")
    print("  tracked, so the count above is reproducible only on a machine that")
    print("  holds it. The GUARD does not depend on it --")
    print("  bench/tests/test_a_timeout_reaps_the_board_it_abandons_2026-11-10.py")
    print("  builds the 2026-11-10 state as a fixture and asserts both rules")
    print("  against it, so the regression is caught in any clone.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="b81_timeout_probe_") as td:
        work = pathlib.Path(td)
        rows = [
            ("A  the code as it was: proc.kill() only      ",
             one_run(work, new_session=False, kill_group=False)),
            ("B  new session, still only proc.kill()       ",
             one_run(work, new_session=True, kill_group=False)),
            ("C  new session + killpg on the group  (FIX)  ",
             one_run(work, new_session=True, kill_group=True)),
        ]

    print("=" * 76)
    print("B81 HALF 2: A TIMEOUT THAT LEFT ITS OWN BOARD RUNNING")
    print("=" * 76)
    for label, survived in rows:
        verdict = "LEAKED" if survived else "reaped"
        print(f"  {label}  grandchild {verdict}")

    leaks_a, leaks_b, leaks_c = (r[1] for r in rows)
    ok = leaks_a and leaks_b and not leaks_c
    _report_the_sizing_defect()
    print()
    if ok:
        print("  A and B LEAK, C does not.")
        print("  So `start_new_session=True` ALONE is not the fix -- that is")
        print("  what B establishes -- and the group kill is the load-bearing")
        print("  half. Both are therefore adopted together in")
        print("  `scripts/cdsfl_sv.py:_git` / `_reap_process_group`.")
    else:
        print("  *** THE PATTERN DID NOT HOLD. This probe has discriminated")
        print("  nothing and no claim may be drawn from it. ***")
    print("=" * 76)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
