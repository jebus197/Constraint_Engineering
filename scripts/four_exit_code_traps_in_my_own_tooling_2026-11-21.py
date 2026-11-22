#!/usr/bin/env python3
"""The 4 exit-code and observability traps that bit MY OWN instruments on
2026-11-21, each REPRODUCED rather than counted.

WHY THIS EXISTS. In the session of 2026-11-21 I told the founder that 4
separate exit-code or observability faults had occurred in my own tooling
rather than in the subject under test. That was a count quoted to him with no
committed script behind it, which is `measured-rate-travels-with-its-script`
broken inside the very analysis that names the rule. A count of occurrences in
my own prose would also be a weak instrument: the prose is the thing under
suspicion.

SO THIS DOES NOT COUNT ANYTHING. It REPRODUCES each trap against real
subprocesses and shows the correct form beside it. A demonstration is stronger
than a tally, because it can fail: if a trap stops reproducing, this script
says so, and the claim that it was real becomes checkable rather than
remembered.

THE 4, IN THE ORDER THEY BIT:

  1. `${pipestatus}` / `${PIPESTATUS}`. bash is 0-indexed and spells it
     `PIPESTATUS`; zsh is 1-indexed and spells it `pipestatus`. A script
     written for one silently reads the wrong element under the other. This
     project has lost an exit code to exactly this twice, on 2026-10-02 and
     again on 2026-11-21.

  2. `cmd | tail`. A POSIX shell reports the LAST pipeline element's status,
     so a RED pytest piped through `tail` reports 0. This is the same defect
     entry B202, the board's silent test phase, was raised for -- and it bit
     the tooling that was repairing B202.

  3. A redirected interpreter without `-u`. Python block-buffers stdout in
     8 KiB chunks when it is not a terminal, so a long run redirected to a
     file produces NOTHING observable until a buffer fills. A 208-file pytest
     run was watched for 12 minutes and showed 0 bytes for this reason.

  4. `cmd | head`. Identical to trap 2 in cause and different in disguise:
     `head` succeeds even when the producer failed, and it is reached for when
     trimming output rather than when streaming it.

WHAT WOULD REFUTE THE CLAIM THESE ARE REAL: any arm below whose trapped form
returns the child's own exit code. The script exits non-zero if that happens,
because then the trap is not a trap on this machine and the claim is wrong.

NOTE ON TRAP 1. The 2 shells are only compared where both exist. On a machine
with 1 of them the arm reports SKIPPED and is excluded from the verdict rather
than counted as a pass, because `a fail-safe must not be recorded as a fact`.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

#: The child's exit code every arm must preserve. 3 is chosen because it is
#: neither 0 nor 1, so a form that collapses every failure to 1 is caught too.
CHILD_CODE = 3


def _sh(shell: str, script: str, cwd: str) -> tuple[int, str]:
    r = subprocess.run([shell, "-c", script], cwd=cwd,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout or "").strip()


def trap_1_pipestatus(cwd: str) -> dict:
    """bash `PIPESTATUS[0]` against zsh `pipestatus[1]`: same text, different element."""
    out: dict = {"name": "1. PIPESTATUS indexing differs between bash and zsh"}
    bash, zsh = shutil.which("bash"), shutil.which("zsh")
    if not (bash and zsh):
        out["status"] = "SKIPPED"
        out["detail"] = "needs both bash and zsh; excluded from the verdict"
        return out
    # The BASH spelling, 0-indexed, run under BOTH shells.
    script = f"(exit {CHILD_CODE}) | cat; echo ${{PIPESTATUS[0]}}"
    rc_b, o_b = _sh(bash, script, cwd)
    rc_z, o_z = _sh(zsh, script, cwd)
    out["bash_reports"] = o_b
    out["zsh_reports"] = o_z
    out["status"] = "REPRODUCED" if o_b != o_z else "DID NOT REPRODUCE"
    out["detail"] = (
        f"the identical script prints {o_b!r} under bash and {o_z!r} under zsh; "
        f"the child exited {CHILD_CODE}")
    return out


def trap_2_tail(cwd: str) -> dict:
    """`cmd | tail` returns tail's status, not the producer's."""
    out: dict = {"name": "2. a pipe through tail discards the producer's exit code"}
    trapped = f"(exit {CHILD_CODE}) | tail -1; echo $?"
    correct = (f"_log=$(mktemp); (exit {CHILD_CODE}) >> \"$_log\" 2>&1; "
               f"_c=$?; tail -1 \"$_log\" >/dev/null; rm -f \"$_log\"; echo $_c")
    _, o_t = _sh("/bin/sh", trapped, cwd)
    _, o_c = _sh("/bin/sh", correct, cwd)
    out["trapped_reports"] = o_t
    out["correct_reports"] = o_c
    out["status"] = ("REPRODUCED" if o_t != str(CHILD_CODE)
                     and o_c == str(CHILD_CODE) else "DID NOT REPRODUCE")
    out["detail"] = (f"piped form reports {o_t!r}; redirect-then-read reports "
                     f"{o_c!r}; the child exited {CHILD_CODE}")
    return out


def trap_3_buffering(cwd: str) -> dict:
    """A redirected interpreter without `-u` shows nothing for a long time."""
    out: dict = {"name": "3. a redirected interpreter without -u is unobservable"}
    prog = (
        "import sys, time\n"
        "for i in range(400):\n"
        "    sys.stdout.write('.' * 40)\n"
        "    time.sleep(0.002)\n")
    src = pathlib.Path(cwd) / "emit.py"
    src.write_text(prog, encoding="utf-8")
    sizes = {}
    for label, flags in (("buffered", []), ("unbuffered", ["-u"])):
        log = pathlib.Path(cwd) / f"{label}.log"
        log.write_text("", encoding="utf-8")
        with log.open("ab") as fh:
            p = subprocess.Popen([sys.executable, *flags, str(src)],
                                 stdout=fh, stderr=subprocess.STDOUT, cwd=cwd)
            time.sleep(0.35)                 # look EARLY, while it is alive
            sizes[label] = log.stat().st_size
            alive_when_sampled = p.poll() is None
            p.wait(timeout=60)
        out[f"{label}_bytes_at_0.35s"] = sizes[label]
        out[f"{label}_still_running"] = alive_when_sampled
    out["status"] = ("REPRODUCED"
                     if sizes["buffered"] < sizes["unbuffered"]
                     else "DID NOT REPRODUCE")
    out["detail"] = (
        f"after 0.35 s the buffered run had written {sizes['buffered']} byte(s) "
        f"and the unbuffered run {sizes['unbuffered']}")
    return out


def trap_4_head(cwd: str) -> dict:
    """`cmd | head` returns head's status. Same cause as trap 2, different disguise."""
    out: dict = {"name": "4. a pipe through head discards the producer's exit code"}
    trapped = f"(exit {CHILD_CODE}) | head -1; echo $?"
    _, o = _sh("/bin/sh", trapped, cwd)
    out["trapped_reports"] = o
    out["status"] = "REPRODUCED" if o != str(CHILD_CODE) else "DID NOT REPRODUCE"
    out["detail"] = (f"piped form reports {o!r}; the child exited {CHILD_CODE}. "
                     f"This is the form that reported WOLFRAM_EXIT=0 for a "
                     f"`wolframscript` invocation that had not run.")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=("Reproduce the 4 exit-code and observability traps that bit "
                     "this project's own tooling on 2026-11-21."))
    ap.add_argument("--json", action="store_true",
                    help="emit the arms as JSON instead of prose")
    args = ap.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="cdsfl_traps_") as td:
        arms = [trap_1_pipestatus(td), trap_2_tail(td),
                trap_3_buffering(td), trap_4_head(td)]

    if args.json:
        import json
        print(json.dumps(arms, indent=2, default=str))
    else:
        print("THE 4 TRAPS, REPRODUCED AGAINST REAL SUBPROCESSES")
        print(f"(every arm's child exits {CHILD_CODE}, so a form that collapses "
              f"failures to 1 is caught too)\n")
        for a in arms:
            print(f"  [{a['status']:17s}] {a['name']}")
            print(f"      {a['detail']}")
        print()

    judged = [a for a in arms if a["status"] != "SKIPPED"]
    reproduced = [a for a in judged if a["status"] == "REPRODUCED"]
    skipped = [a for a in arms if a["status"] == "SKIPPED"]
    print(f"  {len(reproduced)} of {len(judged)} judged arm(s) reproduced"
          + (f"; {len(skipped)} skipped and EXCLUDED from the verdict"
             if skipped else ""))
    if len(reproduced) != len(judged):
        print("  -> an arm did NOT reproduce, so the claim that all 4 are real "
              "traps on this machine is WRONG and must be corrected.")
        return 1
    print("  -> every judged arm is a real trap on this machine. The correct "
          "forms are shown beside traps 2 and 3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
