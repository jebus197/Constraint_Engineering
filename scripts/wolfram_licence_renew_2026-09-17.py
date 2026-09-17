#!/usr/bin/env python3
"""Keep the local Wolfram Engine licence alive without anyone being asked to act.

FOUNDER, 2026-09-17: *"You can automate the Wolfram renewal via a small local
script, or maybe an Apple automation. It doesn't require a username/password.
Make sure it still loads on system reboot whatever you do."*

THE PROJECT RECORD SAID THE OPPOSITE, AND THE RECORD WAS WRONG. `.claude/CLAUDE.md`
records the 2026-09-15 activation as done by hand, and `scripts/cdsfl_onboard.py`
told the reader that activation "needs your Wolfram ID and password, so it cannot
be automated from here". Measured on 2026-09-17 21:26 BST, with the licence file
backed up first: `wolframscript -activate` with stdin closed returned exit 0 and
"Wolfram Engine activated", rewrote `~/Library/WolframEngine/Licensing/mathpass`,
and prompted for nothing. It authenticates through the cloud credential already
stored at `~/Library/WolframEngine/ApplicationData/CloudObject/Authentication/`
with the authentication path set in `WolframScript.conf`.

WHAT THE SAME MEASUREMENT ALSO SHOWED, AND WHY THIS RUNS DAILY RATHER THAN ONCE.
Activating while the licence is still valid does NOT move the date: before and
after that run, `$LicenseExpirationDate` read `DateObject[{2026, 10, 8}, Day]`.
The renewal takes effect at or after expiry -- which is how the 2026-09-15
activation worked, 4 days after the 2026-09-11 lapse. So this runs on a
schedule, attempts activation only inside the window around expiry, and keeps
attempting until the date moves. The worst case is a gap of hours, self-healed,
instead of a lapse nobody notices.

WHAT IT WILL NOT DO. It never types a credential: `-activate` is run with stdin
closed, so a build that ever DID prompt would fail the run rather than wait, and
that failure is logged and exits non-zero. It skips while another Wolfram kernel
is running, because the free Engine is single-kernel and 3 concurrent calls
measured on 2026-08-02 gave 1 result and 2 disconnections. It redacts anything
e-mail-shaped out of the output it logs.

Read-only unless `--run` is given. `--help` does nothing at all.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO / "scripts"))

DEFAULT_LOG = pathlib.Path.home() / "Library" / "Logs" / "cdsfl_wolfram_renew.log"
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+")
ACTIVATED = re.compile(r"\bactivated\b", re.I)


def _helpers():
    import wolfram_standard as W
    import importlib.util
    spec = importlib.util.spec_from_file_location("onb_renew", REPO / "scripts" / "cdsfl_onboard.py")
    onb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(onb)
    return W, onb


def read_expiry(runner=subprocess.run) -> tuple[str | None, str]:
    """(expiry as YYYY-MM-DD or None, why). Uses the Wolfram standard's own rules."""
    W, _ = _helpers()
    r = W.run_local("$LicenseExpirationDate", timeout=180, runner=runner)
    if not r["evidence"]:
        return None, f"the kernel did not answer: {r['reason']}"
    got = W.parse_licence_expiry(r["stdout"])
    return got, ("read from the kernel" if got else f"unparsable answer: {r['stdout'].strip()[:80]!r}")


def kernels_running(runner=subprocess.run) -> list[str]:
    """Wolfram kernels already running, from onboarding's own check (1 definition)."""
    _, onb = _helpers()
    saved = onb.subprocess.run
    try:
        onb.subprocess.run = runner
        return onb.stale_kernels()
    finally:
        onb.subprocess.run = saved


def activate(runner=subprocess.run, timeout: int = 300) -> tuple[bool, str]:
    """Run `wolframscript -activate` with stdin CLOSED, so a prompt fails rather than waits."""
    import shutil
    script = shutil.which("wolframscript")
    if not script:
        return False, "wolframscript is not installed"
    try:
        r = runner([script, "-activate"], stdin=subprocess.DEVNULL, capture_output=True,
                   text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"no answer in {timeout}s, which means it asked for input"
    out = EMAIL.sub("<redacted>", ((r.stdout or "") + (r.stderr or "")).strip())
    return (r.returncode == 0 and bool(ACTIVATED.search(out))), out[:300] or f"exit {r.returncode}, no output"


def log(path: pathlib.Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{dt.datetime.now().astimezone().isoformat(timespec='seconds')} {message}\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Renew the local Wolfram Engine licence when it is due. "
                                             "Reads only, unless --run is given.")
    ap.add_argument("--run", action="store_true", help="actually activate when it is due")
    ap.add_argument("--days", type=int, default=1,
                    help="attempt activation when the licence expires within this many days (default 1)")
    ap.add_argument("--force", action="store_true", help="attempt activation whatever the date says")
    ap.add_argument("--log", type=pathlib.Path, default=DEFAULT_LOG)
    a = ap.parse_args(argv)

    expiry, why = read_expiry()
    today = dt.date.today()
    left = (dt.date.fromisoformat(expiry) - today).days if expiry else None
    state = f"expiry {expiry or 'UNKNOWN'} ({why}), {left if left is not None else '?'} day(s) left"
    due = a.force or expiry is None or (left is not None and left <= a.days)

    if not a.run:
        print(f"{state}; {'DUE' if due else 'not due'}. Read-only: pass --run to act.")
        return 0

    busy = kernels_running()
    if busy and not a.force:
        log(a.log, f"SKIP {state}; {len(busy)} Wolfram kernel(s) running, will retry on the next run")
        print(f"{state}; skipped, {len(busy)} kernel(s) running")
        return 0
    if not due:
        log(a.log, f"OK {state}; nothing to do")
        print(f"{state}; nothing to do")
        return 0

    ok, detail = activate()
    after, _ = read_expiry()
    moved = bool(after and expiry and after > expiry)
    log(a.log, f"{'RENEWED' if ok else 'FAILED'} {state} -> {after or 'UNKNOWN'}"
               f"{' (date moved)' if moved else ' (date unchanged; will retry)'} :: {detail}")
    print(f"{'renewed' if ok else 'FAILED'}: {state} -> {after or 'UNKNOWN'}; {detail}")
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
