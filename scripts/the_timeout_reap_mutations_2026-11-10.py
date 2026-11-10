#!/usr/bin/env python3
"""Mutate the B81 half-2 fix and require the guard to go RED each time.

ANCHORS ARE DERIVED FROM THE SUBJECT, never typed as an expectation: each
mutation names a substring, asserts it occurs EXACTLY ONCE in the live file,
and fails loudly if it does not -- so a refactor that moves the code makes this
harness complain rather than silently mutate nothing.

THE EXPECTATION IS NOT PER-TEST. The harness does not say which test should
fail; it requires the guard to go red and REPORTS which tests did. Naming the
test in advance is how a harness ends up agreeing with itself.

★ MUTATION 3 IS RUN IN AN ISOLATED PROCESS GROUP ON PURPOSE. Removing the
own-group refusal makes the code `killpg` the group its own runner is in, so
the mutant kills pytest. Run in-group it would kill THIS harness and the shell
around it. `start_new_session=True` confines that blast to the subprocess, and
the detection is the runner being killed -- which is itself the demonstration
of why the refusal exists.

RESTORES WHAT IT FOUND, not what it assumes: the original bytes are held in
memory and written back in a `finally`, verified by sha256.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

#: This harness lives in a scratchpad OUTSIDE the repository, so walking its
#: own parents cannot find the tree. The root is located from the working
#: directory instead, and the located path is PRINTED so a wrong tree cannot
#: be mutated silently.
def _find_root() -> pathlib.Path:
    start = pathlib.Path.cwd().resolve()
    for cand in (start, *start.parents):
        if (cand / "bench" / "domain_immune.py").is_file():
            return cand
    raise SystemExit("cannot locate the repository from the working directory")


ROOT = _find_root()

SUBJECT = ROOT / "scripts" / "cdsfl_sv.py"
GUARD = ROOT / "bench" / "tests" / (
    "test_a_timeout_reaps_the_board_it_abandons_2026-11-10.py")

MUTATIONS = [
    ("M1  drop start_new_session from _git",
     "        start_new_session=True,\n    )\n    try:\n        out, err = proc.communicate",
     "    )\n    try:\n        out, err = proc.communicate",
     False),
    ("M2  never signal the group at all",
     "    if pgid is not None and pgid != os.getpgid(0):",
     "    if False:",
     False),
    ("M3  drop the own-group refusal  (ISOLATED: kills its own runner)",
     "if pgid is not None and pgid != os.getpgid(0):",
     "if pgid is not None:",
     True),
    # M4 MUST PARSE. Its first form wrapped the print in a tuple, which is a
    # SyntaxError, so pytest exited 2 on COLLECTION and the stderr assertion
    # was never reached -- a mutation detected by the interpreter proves
    # nothing about the guard. Sending the record to stdout instead is
    # semantically valid and is exactly the mistake the test exists to catch.
    ("M4  send the reap record to stdout, not stderr",
     "            file=sys.stderr,",
     "            file=sys.stdout,",
     False),
    # M6 IS THE ONE THE MEASUREMENT ADDED. A SIGKILL-only reap looks simpler
    # and destroys the hook's own duration record, which `commit_timeout()`
    # is the sole consumer of -- turning 1 timeout into a permanent floor.
    ("M6  SIGKILL only, skipping the SIGTERM grace",
     "        for sig in (signal.SIGTERM, signal.SIGKILL):",
     "        for sig in (signal.SIGKILL,):",
     False),
    # M7-M9 cover the SIZING half, which is a second defect in the same
    # mechanism rather than a second fix for the same one: the leak is why an
    # abandoned board kept running, and the sizing is why the timeout fired at
    # 300 s at all. No composability claim is made or needed.
    ("M7  ignore the ledger, read the last run only",
     "    for line in rows[-COMMIT_TIMEOUT_LEDGER_ROWS:]:",
     "    for line in []:",
     False),
    ("M8  take the ledger MINIMUM instead of the maximum",
     "        ledger_max = max(ledger_max, secs)",
     "        ledger_max = min(ledger_max, secs) if ledger_max else secs",
     False),
    ("M9  drop the recent-window bound",
     "rows[-COMMIT_TIMEOUT_LEDGER_ROWS:]",
     "rows[:]",
     False),
    ("M5  raise the wrong exception type",
     'raise subprocess.TimeoutExpired(["git", *args], timeout) from None',
     'raise RuntimeError("git timed out") from None',
     False),
]


def run_guard(isolate: bool) -> tuple[int, str]:
    kw = {"start_new_session": True} if isolate else {}
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, timeout=600, cwd=str(ROOT), **kw,
    )
    return r.returncode, r.stdout + r.stderr


def failing_tests(out: str) -> list[str]:
    return sorted(set(re.findall(r"^(?:FAILED|ERROR) (\S+)", out, re.M)))


def main(argv: list[str] | None = None) -> int:
    # A `--help` MUST NEVER COST MINUTES -- his standing rule. Without argparse
    # the flag was ignored and the whole board ran, which is several minutes of
    # pytest for a usage string.
    import argparse
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)
    print(f"  repository: {ROOT}")
    original = SUBJECT.read_text()
    sha = hashlib.sha256(original.encode()).hexdigest()
    print("=" * 76)
    print("B81 HALF 2 MUTATION BOARD")
    print("=" * 76)

    rc, out = run_guard(False)
    print(f"  baseline (unmutated)                                  "
          f"exit={rc}  {'GREEN' if rc == 0 else 'RED'}")
    if rc != 0:
        print("  *** the guard is not green to begin with; nothing below "
              "means anything ***")
        print(out[-2500:])
        return 1

    red = 0
    try:
        for label, find, repl, isolate in MUTATIONS:
            n = original.count(find)
            if n != 1:
                print(f"  {label:54s}  ANCHOR MISSED ({n} occurrences)")
                continue
            SUBJECT.write_text(original.replace(find, repl, 1))
            rc, out = run_guard(isolate)
            got = failing_tests(out)
            if rc == 0:
                print(f"  {label:54s}  exit=0  *** STILL GREEN ***")
            else:
                red += 1
                how = (f"killed by signal {-rc}" if rc < 0
                       else f"exit={rc}")
                names = ", ".join(t.split("::")[-1] for t in got) or \
                    "runner died before reporting"
                print(f"  {label:54s}  {how}  RED")
                print(f"       detected by: {names}")
    finally:
        SUBJECT.write_text(original)
        back = hashlib.sha256(SUBJECT.read_text().encode()).hexdigest()
        assert back == sha, "RESTORE FAILED -- the subject is not what I found"
        print(f"\n  restored, sha256 {back[:16]} matches what was found")

    print(f"\n  {red} of {len(MUTATIONS)} mutations turn the guard RED")
    print("=" * 76)
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
