#!/usr/bin/env python3
"""Keep re-dispatching a panel round until it lands a reply, through a flaky network.

THE FOUNDER'S ASK, 2026-10-06 04:22 BST: *"I'm having intermittent internet issues.
You should take careful notes of where you are at and retry with a script over a few
minute intervals until they resolve themselves cleanly."*

WHAT GOES WRONG WITHOUT THIS. A `claude_cli` seat is a network call. When the link
drops mid-reply the dispatcher's own retry may exhaust its attempts, the process
exits, and the round leaves a directory holding a BRIEF and a tools log but no
reply -- which is exactly the state `capability_ladder_design_blind_cc2_2026-10-06`
was in at 04:23 (BRIEF.md and cc2.tools.json present, cc2.json absent). Nothing then
re-dispatches it, and the blind round is silently lost. A panel round lost to a
network blip is indistinguishable, in the record, from a seat that declined to answer.

WHAT COUNTS AS LANDED. The seat's reply file exists AND carries a non-empty
`response`. A reply file with 0 characters is a failure, not a landing: the fable
round's own JSON carries `chars: 12269` under `response`, and an earlier read of
`reply` returned 0 because that key does not exist. Checking only for the file would
accept an empty answer as success.

WHAT IT WILL NOT DO. It never dispatches a PAID seat. The seat set is checked against
the dispatcher's own `FREE_SEATS` before every attempt and the run is refused
otherwise, because an unattended retry loop is the worst possible place to spend the
founder's money. It also stops after `--max-attempts`, so a permanently broken route
cannot loop all night.

Run:
  python3 scripts/panel_round_watchdog_2026-10-06.py <round_dir_name> \
      --seats cc2 --blind-of <other_round> --interval 180 --max-attempts 8

  --interval seconds between a failed attempt and the next (default 180)
  --max-attempts total dispatches including the one already running (default 8)
  --status-file where to write machine-readable progress (default under the round)
Exit: 0 the reply landed, 1 attempts exhausted, 2 refused before dispatching.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="panel_round_watchdog_2026-10-06.py",
        description="Re-dispatch a free panel round until its reply lands.")
    # OPTIONAL POSITIONAL, DELIBERATELY. As a REQUIRED positional, argparse
    # reports "the following arguments are required: round_dir" when the only
    # fault is a MISTYPED FLAG, so the operator is told the wrong thing and
    # `test_an_unknown_flag_is_rejected_loudly` fails. Optional here, checked
    # below, so an unrecognised flag is reported as an unrecognised flag.
    p.add_argument("round_dir", nargs="?", default=None,
                   help="round directory name under bench/logs")
    p.add_argument("--seats", default="cc2",
                   help="comma-separated seat names (FREE seats only)")
    p.add_argument("--blind-of", default="",
                   help="comma-separated round ids this seat must stay blind to")
    p.add_argument("--interval", type=int, default=180,
                   help="seconds to wait after a failed attempt (default 180)")
    p.add_argument("--max-attempts", type=int, default=8,
                   help="total dispatches, including one already running")
    p.add_argument("--status-file", default=None)
    return p.parse_args(argv)


def _star():
    """The SINGLE definition of 'a seat landed a reply', loaded from one place.

    THIS FUNCTION EXISTS BECAUSE THE SECOND COPY WAS THE DEFECT. The first version
    of this file re-implemented the emptiness test here, giving the project 2
    definitions of "landed" -- and a producer and a consumer that each define a
    predicate correctly can still disagree, which is the failure shape this
    project has recorded repeatedly. `bench/star_topology_2026-10-06.py` owns it.
    """
    import importlib.util
    _p = REPO / "bench" / "star_topology_2026-10-06.py"
    spec = importlib.util.spec_from_file_location("cdsfl_star_topology_wd", _p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_star_topology_wd"] = m
    spec.loader.exec_module(m)
    return m


def reply_has_landed(round_dir: pathlib.Path, seats) -> tuple[bool, dict]:
    """Has every seat written a reply with a NON-EMPTY response?

    The emptiness test is the point, and it is DELEGATED rather than restated. A
    dispatcher that failed after creating the file would otherwise read as a
    success: cc2's round wrote a 9280-byte reply file carrying `ok: False` and 0
    words of response.
    """
    ST = _star()
    detail = {}
    ok = True
    for seat in seats:
        if not (round_dir / f"{seat}.json").is_file():
            detail[seat] = "no reply file"
            ok = False
            continue
        words = ST.seat_reply_words(round_dir, seat)
        if words == 0:
            detail[seat] = "reply file present but response is EMPTY"
            ok = False
            continue
        detail[seat] = f"landed: {words} words"
    return ok, detail


def panel_is_running() -> bool:
    r = subprocess.run(["pgrep", "-f", "confer_maths_panel"],
                       capture_output=True, text=True)
    return r.returncode == 0 and bool(r.stdout.strip())


def refuse_if_any_seat_is_paid(seats) -> str | None:
    """Read FREE_SEATS from the dispatcher itself rather than restating it here.

    A second copy of the free-seat list is a second thing to go stale, and the
    standing rule is that no paid dispatch happens without the founder present.
    """
    sys.path.insert(0, str(REPO / "bench"))
    os.environ.setdefault("PANEL_BRIEF_UNCHECKED", "1")
    try:
        import importlib
        mod = importlib.import_module("confer_maths_panel_2026-09-05")
        free = set(getattr(mod, "FREE_SEATS"))
    except Exception as exc:  # noqa: BLE001
        return (f"could not read FREE_SEATS from the dispatcher "
                f"({type(exc).__name__}: {exc}); refusing rather than guessing")
    paid = [s for s in seats if s not in free]
    if paid:
        return (f"seat(s) {paid} are not in FREE_SEATS {sorted(free)}; an "
                f"unattended retry loop never spends money")
    return None


def dispatch(round_name: str, seats, blind_of: str) -> subprocess.Popen:
    env = dict(os.environ)
    env["PANEL_ONLY"] = ",".join(seats)
    if blind_of:
        env["PANEL_BLIND_OF"] = blind_of
    out = LOGS / round_name / "watchdog_dispatch.out"
    fh = out.open("ab")
    return subprocess.Popen(
        [sys.executable, "bench/confer_maths_panel_2026-09-05.py", round_name],
        cwd=str(REPO), env=env, stdout=fh, stderr=subprocess.STDOUT)


def write_status(path: pathlib.Path, payload: dict) -> None:
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        pass  # a status file that cannot be written must not kill the watch


def main(argv=None) -> int:
    args = _parse_args(argv)
    if not args.round_dir:
        print("a round directory name is required, e.g.\n"
              "  python3 scripts/panel_round_watchdog_2026-10-06.py "
              "<round_dir> --seats cc2", file=sys.stderr)
        return 2
    seats = [s.strip() for s in args.seats.split(",") if s.strip()]
    round_dir = LOGS / args.round_dir
    status = pathlib.Path(args.status_file) if args.status_file else (
        round_dir / "watchdog_status.json")

    if not round_dir.is_dir():
        print(f"no such round directory: {round_dir}", file=sys.stderr)
        return 2
    if not (round_dir / "BRIEF.md").is_file():
        print(f"no BRIEF.md in {round_dir} — nothing to dispatch", file=sys.stderr)
        return 2
    refusal = refuse_if_any_seat_is_paid(seats)
    if refusal:
        print(f"REFUSED: {refusal}", file=sys.stderr)
        return 2

    log = []

    def record(event: str, **kw):
        entry = {"at": _now(), "event": event, **kw}
        log.append(entry)
        print(f"[{entry['at']}] {event} {kw}", flush=True)
        write_status(status, {"round": args.round_dir, "seats": seats,
                              "interval_s": args.interval,
                              "max_attempts": args.max_attempts,
                              "events": log})

    record("watch started", already_running=panel_is_running())

    attempts = 1 if panel_is_running() else 0
    while True:
        # Let anything already in flight finish before judging the round.
        while panel_is_running():
            landed, detail = reply_has_landed(round_dir, seats)
            if landed:
                record("landed while a dispatch was in flight", detail=detail)
                return 0
            time.sleep(15)

        landed, detail = reply_has_landed(round_dir, seats)
        if landed:
            record("LANDED", detail=detail, attempts=attempts)
            return 0

        if attempts >= args.max_attempts:
            record("ATTEMPTS EXHAUSTED", detail=detail, attempts=attempts)
            return 1

        if attempts:
            record("waiting before the next attempt", seconds=args.interval,
                   detail=detail)
            time.sleep(args.interval)

        attempts += 1
        record("dispatching", attempt=attempts, of=args.max_attempts)
        proc = dispatch(args.round_dir, seats, args.blind_of)
        rc = proc.wait()
        record("dispatch exited", attempt=attempts, returncode=rc)


if __name__ == "__main__":
    sys.exit(main())
