#!/usr/bin/env python3
"""The last full-suite measurement, recorded so `sv` can CITE it instead of re-running.

FOUNDER, 2026-09-20: *"sv normally takes minutes? Hopefully we aren't looking at
hours?"* It was looking at 23 minutes, because the SESSION STATE block quotes a
suite figure and I re-ran the whole suite to make that figure fresh. Nothing
required that. The A23 guard requires a suite figure to NAME A PRODUCER a reader
can re-run; it does not require the run to have happened during this `sv`.

So the full run writes a record here, and `sv` cites it: commit, date, counts,
exit code, wall clock, whether the tree was clean, and the exact command. The
figure then travels with its producer by construction rather than by my
remembering to paste one, which is `measured-rate-travels-with-its-script`
applied to the 1 number a post-compaction reader trusts most.

  record   -- parse a finished pytest log and write the record
  cite     -- print the sentence `sv` puts in the state block
  check    -- exit 3 if the record is older than HEAD (for launchers)

Writes only `resources/suite_record.json`, and only under `record`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RECORD = REPO / "resources" / "suite_record.json"
COMMAND = "python3 -m pytest bench/tests/ -q --netguard-strict"
SUMMARY = re.compile(r"(?:(\d+) failed[, ]+)?(\d[\d,]*) passed"
                     r"(?:[, ]+(\d+) skipped)?(?:[, ]+(\d+) xfailed)?"
                     r".*?in ([\d.]+)s")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()


def parse(log_text: str) -> dict:
    """Counts from a pytest tail. Returns {} when the log has no summary line."""
    m = None
    for line in log_text.splitlines():
        hit = SUMMARY.search(line)
        if hit:
            m = hit
    if not m:
        return {}
    failed, passed, skipped, xfailed, secs = m.groups()
    return {"passed": int(passed.replace(",", "")), "failed": int(failed or 0),
            "skipped": int(skipped or 0), "xfailed": int(xfailed or 0),
            "seconds": float(secs)}


def record(log: pathlib.Path, exit_code: int | None, clean: bool | None) -> dict:
    counts = parse(log.read_text(encoding="utf-8", errors="replace"))
    if not counts:
        raise SystemExit(f"no pytest summary line in {log}: nothing to record")
    if exit_code is None:
        m = re.search(r"PYTEST_EXIT=(\d+)", log.read_text(encoding="utf-8", errors="replace"))
        exit_code = int(m.group(1)) if m else (1 if counts["failed"] else 0)
    if clean is None:
        clean = not _git("status", "--short")
    out = {"command": COMMAND, "commit": _git("rev-parse", "--short", "HEAD"),
           "when": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "exit_code": exit_code, "tree_clean_at_record_time": clean, **counts}
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def cite() -> str:
    """The sentence `sv` writes. It NAMES THE COMMAND, which is what the guard wants."""
    if not RECORD.is_file():
        return ("No full-suite record exists yet. Run "
                f"`{COMMAND}` and record it with "
                "`python3 scripts/suite_record.py record --log <file>`.")
    r = json.loads(RECORD.read_text(encoding="utf-8"))
    state = "GREEN" if r["exit_code"] == 0 else f"{r['failed']} FAILED"
    tree = "" if r.get("tree_clean_at_record_time", True) else \
        " The tree was NOT clean when this was measured, so the figure belongs to the run and not cleanly to the commit."
    return (f"**The last full-suite measurement, {state}, at `{r['commit']}` on "
            f"{r['when'][:10]}: {r['passed']:,} passed, {r['failed']} failed, "
            f"{r['skipped']} skipped, {r['xfailed']} xfailed, {r['seconds']:.2f} s, "
            f"pytest exit code {r['exit_code']}**, from `{r['command']}`. Cited, not "
            f"re-run: `sv` does not re-measure an unchanged tree.{tree}")


def stale() -> tuple:
    """(is_stale, why). A record older than HEAD describes a tree that has moved."""
    if not RECORD.is_file():
        return True, "no full-suite record exists"
    r = json.loads(RECORD.read_text(encoding="utf-8"))
    head = _git("rev-parse", "--short", "HEAD")
    if r["commit"] == head:
        return False, f"recorded at HEAD ({head})"
    behind = _git("rev-list", "--count", f"{r['commit']}..HEAD")
    return True, (f"recorded at {r['commit']}, HEAD is {head}"
                  + (f", {behind} commit(s) later" if behind else ""))


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=("record", "cite", "check"))
    ap.add_argument("--log", type=pathlib.Path, help="a finished pytest output file")
    ap.add_argument("--exit-code", type=int)
    ap.add_argument("--clean", action="store_true", help="assert the tree was clean")
    a = ap.parse_args(argv)
    if a.action == "record":
        if not a.log:
            raise SystemExit("record needs --log <pytest output file>")
        out = record(a.log, a.exit_code, True if a.clean else None)
        print(json.dumps(out, indent=2))
        return 0
    if a.action == "cite":
        print(cite())
        return 0
    is_stale, why = stale()
    print(("STALE: " if is_stale else "CURRENT: ") + why)
    return 3 if is_stale else 0


if __name__ == "__main__":
    sys.exit(main())
