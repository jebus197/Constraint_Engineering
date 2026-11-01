#!/usr/bin/env python3
"""The type checker as its OWN TASK, with a per-file ratchet, on his ruling.

HIS RULING, 2026-11-01, verbatim: *"Enable it as its own task, as you suggest."*
The recommendation he accepted: enable the type checker as a task of its own,
fix what it surfaces in batches, and keep it OUT of the commit check until it is
clear.

★ THE ORIGINAL JUSTIFICATION WAS REFUTED BEFORE THIS WAS BUILT, and the task
survives on a different premise. B68 claimed that because `bench` is a namespace
package the checker cannot resolve a bare project import, so
`--ignore-missing-imports` turns a project symbol into `Any` and nothing behind
it is checked. **Refuted by execution:** a probe importing `TicketStore` from
`bench.ticket_store` and calling a method that does not exist is checked WITH
the flag and the call IS caught. The flag suppresses THIRD-PARTY stub errors --
`scipy.stats`, `statsmodels.stats.multitest`, both `[import-untyped]` -- which
is what it is for. The 2 quoted figures were OUTPUT LINES counted as findings:
the flagless run on `bench/routing.py` prints 7 lines, and 7 minus the summary
line is the "6" that was reported against a true error count of 3.

SO THE PREMISE IS THE PLAIN ONE: the checker has never been run over this
project as a task, and it finds real errors when it is.

HOW THIS AVOIDS THE EXCLUSION HIDING ANYTHING. Running WITHOUT the flag and
classifying by error code gives both numbers from ONE pass: codes
`import-untyped` and `import-not-found` are environment facts about third-party
stubs and are reported SEPARATELY, and every other code is a finding about this
project's code and is what the ratchet counts. Nothing is dropped silently,
which is this project's excluded-implies-reported discipline.

THE RATCHET IS PER FILE, NOT A TOTAL. A total lets a new error in one file hide
behind a fix in another. A file may only improve; a file with no baseline and
any finding is reported as unbaselined and fails, so a new file cannot arrive
dirty without someone deciding to baseline it.

NOT IN THE COMMIT CHECK, by his ruling, and a guard asserts that rather than
trusting it: `bench/tests/test_the_type_check_task_is_its_own_task_2026-11-01.py`.

Usage:
    python3 scripts/type_check_task_2026-11-01.py            # check, exit 1 on a rise
    python3 scripts/type_check_task_2026-11-01.py --update    # rebaseline
    python3 scripts/type_check_task_2026-11-01.py --worst 20  # where to start fixing
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LEDGER = REPO / "experimental_notes" / "data" / "type_check_baseline.json"
#: The 2 codes that are facts about the ENVIRONMENT rather than about this
#: project's code. Reported separately; never counted by the ratchet.
THIRD_PARTY_CODES = ("import-untyped", "import-not-found")
#: `path:line: error: message  [code]`
_ERROR = re.compile(r"^(?P<path>[^:]+):(?P<line>\d+):(?:\d+:)?\s*error:\s*"
                    r"(?P<msg>.*?)(?:\s+\[(?P<code>[a-z-]+)\])?\s*$")
TARGETS = ("bench", "scripts")


def _sources() -> list[str]:
    out: list[str] = []
    for t in TARGETS:
        out += [str(p.relative_to(REPO)) for p in sorted((REPO / t).glob("*.py"))]
    return out


def run_checker(paths: list[str]) -> tuple[dict, dict, str]:
    """(project findings per file, third-party per file, raw output).

    Run WITHOUT `--ignore-missing-imports` so the third-party cases are visible
    and can be reported rather than silently suppressed.
    """
    # ★ `--explicit-package-bases` AND `MYPYPATH` ARE LOAD-BEARING, NOT TIDINESS.
    # Without them mypy ABORTS at the second file with "Source file found twice
    # under different module names: build_acceptance and bench.build_acceptance",
    # because the repository root is also on the search path and `bench` has no
    # marker file, so every file is reachable under 2 module names. Measured: the
    # flagless run over `bench/*.py` exits 2 having reported 8 errors, 7 of them
    # third-party stubs, and never reaches the remaining 150-odd files. THIS is
    # the real consequence of the namespace package -- the checker does not run
    # at all -- and it is not what B68 originally claimed, which was that project
    # symbols silently become `Any`. With these 2 settings the same 3-file probe
    # reports 0 "found twice" and surfaces real findings, including a `None`
    # returned where a `frozenset` is declared.
    cmd = [sys.executable, "-m", "mypy", "--explicit-package-bases",
           "--no-error-summary",
           "--cache-dir", str(REPO / ".mypy_cache"), *paths]
    env = {**os.environ, "MYPYPATH": str(REPO)}
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, env=env)
    proj: dict[str, int] = collections.Counter()
    third: dict[str, int] = collections.Counter()
    for line in (r.stdout or "").splitlines():
        m = _ERROR.match(line.strip())
        if not m:
            continue
        where = m.group("path")
        if (m.group("code") or "") in THIRD_PARTY_CODES:
            third[where] += 1
        else:
            proj[where] += 1
    return dict(proj), dict(third), r.stdout or ""


def load_ledger() -> dict:
    if not LEDGER.is_file():
        return {"_what_this_is": [
            "PER-FILE baseline for the type-check task (B68, his ruling 2026-11-01).",
            "A file may only improve. A file absent here with any finding is",
            "unbaselined and fails, so a new file cannot arrive dirty unnoticed.",
            "Third-party stub errors are NOT counted here; they are reported",
            "separately by the task, because they are facts about the",
            "environment rather than about this project's code.",
        ], "files": {}}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--update", action="store_true",
                    help="write the current counts as the new baseline")
    ap.add_argument("--worst", type=int, default=0,
                    help="list the N files with the most findings")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="check only these files (default: bench/ and scripts/)")
    args = ap.parse_args(argv[1:])

    paths = args.paths or _sources()
    proj, third, _raw = run_checker(paths)
    led = load_ledger()
    base = led.get("files") or {}

    total_p = sum(proj.values())
    total_t = sum(third.values())
    print("=" * 74)
    print("TYPE CHECK TASK — per-file ratchet, outside the commit check")
    print("=" * 74)
    print(f"\nfiles checked              : {len(paths)}")
    print(f"findings about THIS project: {total_p} across {len(proj)} file(s)")
    print(f"third-party stub errors    : {total_t} across {len(third)} file(s)"
          f"  (reported, never ratcheted)")

    if args.worst:
        print(f"\nWHERE TO START, worst {args.worst} by finding count:")
        for f, n in sorted(proj.items(), key=lambda kv: -kv[1])[:args.worst]:
            print(f"    {n:4}  {f}   (baseline {base.get(f, 'none')})")

    if args.update:
        led["files"] = dict(sorted(proj.items()))
        LEDGER.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\nBASELINE WRITTEN: {len(proj)} file(s), {total_p} finding(s).")
        return 0

    risen = {f: (n, base.get(f)) for f, n in proj.items()
             if f in base and n > int(base[f])}
    unbaselined = {f: n for f, n in proj.items() if f not in base}
    improved = {f: (proj.get(f, 0), int(n)) for f, n in base.items()
                if proj.get(f, 0) < int(n)}

    if improved:
        print(f"\nIMPROVED, {len(improved)} file(s) — run --update to lock it in:")
        shown = sorted(improved.items())[:12]
        for f, (now, was) in shown:
            print(f"    {was:4} -> {now:<4} {f}")
        # A list cut to N under a heading that reads as complete is a silent
        # falsehood, so the remainder is stated rather than left to inference.
        if len(improved) > len(shown):
            print(f"    + {len(improved) - len(shown)} more improved file(s) "
                  f"not shown; all of them are in the ledger after --update")
    for f, (now, was) in sorted(risen.items()):
        print(f"\n★ RISEN: {f} was {was}, now {now}")
    for f, n in sorted(unbaselined.items()):
        print(f"\n★ UNBASELINED with {n} finding(s): {f}")
        print("    baseline it deliberately with --update, or fix it")
    if risen or unbaselined:
        print(f"\nREFUSED: {len(risen)} risen, {len(unbaselined)} unbaselined.")
        return 1
    print(f"\nOK — no file is worse than its baseline.")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    # `takes_no_arguments=False` because this script HAS a parser: the helper
    # answers --help before argparse sees anything, and otherwise stands aside.
    answer_help(__doc__, __file__, takes_no_arguments=False)
    sys.exit(main(sys.argv))
