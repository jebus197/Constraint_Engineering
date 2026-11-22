#!/usr/bin/env python3
"""CAN THE BOARD'S TEST PHASE STREAM WITHOUT THE GATE LOSING ITS VERDICT?

Producer for entry B202, the board's 27-minute test phase that cannot stream.
His ruling, 2026-11-21: stream the test phase.

THE DEFECT. `hooks/pre-commit` runs its guards as `OUT=$(python3 -m pytest ...)`.
A command substitution captures every byte, so nothing is observable until the
phase ends -- about 42 minutes on the last 3 boards. The `sv` side was already
fixed on 2026-11-17 under entry B195 and streams line by line, so the captured
variable is the ONLY remaining link in the chain.

THE TRAP. The obvious repair is `| tee`, and it SILENTLY DISABLES THE GATE: a
POSIX shell reports the exit status of the LAST element of a pipeline, which is
`tee`, and `tee` succeeds whatever pytest did. A red board would be recorded as
passing. `${PIPESTATUS[0]}` is bash-only and 0-indexed while zsh spells it
`${pipestatus[1]}` and 1-indexes it, so the portable-looking fix is also
shell-dependent -- this project has already lost an exit code to exactly that
difference, on 2026-10-02 and again on 2026-11-21.

WHAT THIS MEASURES, on real subprocesses in a real `/bin/sh`:
  1. exit-code fidelity of 3 candidate forms against trees rigged to pass,
     to fail, and to fail with output on stderr only;
  2. whether each form produces output BEFORE the child exits (the thing he
     asked for), timed;
  3. that the captured text is byte-identical to the unstreamed capture, so
     every downstream grep in the hook keeps working.

Exit 0 only if exactly one candidate is correct on all 3 counts. Writes only
inside a temporary directory.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

#: Each candidate is a /bin/sh program with CHILD substituted in. It must leave
#: the child's status in CODE and the child's full output in OUT.
CANDIDATES: dict[str, str] = {
    "capture (current)": '''
OUT=$(CHILD 2>&1)
CODE=$?
''',
    "tee (the obvious fix)": '''
OUT=$(CHILD 2>&1 | tee /dev/stderr)
CODE=$?
''',
    "logfile + background tail": '''
_LOG="$WORK/board.log"
: > "$_LOG"
tail -n +1 -f "$_LOG" >&2 &
_TAIL=$!
CHILD >> "$_LOG" 2>&1
CODE=$?
kill "$_TAIL" 2>/dev/null
wait "$_TAIL" 2>/dev/null
OUT=$(cat "$_LOG")
rm -f "$_LOG"
''',
}

#: (name, python program, expected exit code)
CHILDREN: list[tuple[str, str, int]] = [
    ("passes", "import sys,time\n"
               "for i in range(3):\n"
               "    print('tick %d' % i, flush=True); time.sleep(0.4)\n"
               "print('3 passed'); sys.exit(0)\n", 0),
    ("fails", "import sys,time\n"
              "for i in range(3):\n"
              "    print('tick %d' % i, flush=True); time.sleep(0.4)\n"
              "print('FAILED test_x'); sys.exit(1)\n", 1),
    ("fails on stderr only", "import sys,time\n"
                             "for i in range(3):\n"
                             "    print('err %d' % i, file=sys.stderr, flush=True)\n"
                             "    time.sleep(0.4)\n"
                             "sys.exit(2)\n", 2),
]


def run(form: str, child_src: str, work: pathlib.Path) -> tuple[int, str, float]:
    """Run one candidate and report (CODE it recorded, OUT it captured, time to
    first streamed byte relative to child exit; negative means it streamed early)."""
    child = work / "child.py"
    child.write_text(child_src, encoding="utf-8")
    prog = ("WORK=" + str(work) + "\n"
            + form.replace("CHILD", f"{sys.executable} -u {child}")
            + '\nprintf "CODE=%s\\n" "$CODE" > "$WORK/code"\n'
              'printf "%s" "$OUT" > "$WORK/out"\n')
    script = work / "form.sh"
    script.write_text(prog, encoding="utf-8")
    first_byte = [None]
    t0 = time.monotonic()
    proc = subprocess.Popen(["/bin/sh", str(script)], cwd=work,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    seen = []
    assert proc.stdout is not None
    for line in proc.stdout:
        if first_byte[0] is None:
            first_byte[0] = time.monotonic() - t0
        seen.append(line)
    proc.wait()
    total = time.monotonic() - t0
    code = int((work / "code").read_text().strip().split("=")[1])
    out = (work / "out").read_text(encoding="utf-8")
    lead = (total - first_byte[0]) if first_byte[0] is not None else -1.0
    return code, out, lead


def main(argv=None) -> int:
    #: `--help` is answered with a usage line and does no work, per
    #: `bench/tests/test_help_is_answered_2026-09-11.py`. This script spawns
    #: real subprocesses, so a `--help` that ran the measurement would cost
    #: seconds of his machine for a flag that asks a question about itself.
    argparse.ArgumentParser(
        description=__doc__.splitlines()[0]).parse_args(argv)
    print("=" * 74)
    print("EXIT-CODE FIDELITY AND STREAMING, DRIVEN AGAINST REAL /bin/sh")
    print("=" * 74)
    results: dict[str, dict[str, bool]] = {}
    baselines: dict[str, str] = {}

    for cname, csrc, cexp in CHILDREN:
        work = pathlib.Path(tempfile.mkdtemp(prefix="b202_base_"))
        try:
            _c, baseline_out, _l = run(CANDIDATES["capture (current)"], csrc, work)
            baselines[cname] = baseline_out
        finally:
            shutil.rmtree(work, ignore_errors=True)

    for fname, form in CANDIDATES.items():
        print(f"\n--- {fname} ---")
        rec = {"codes": True, "streams": True, "text": True}
        for cname, csrc, cexp in CHILDREN:
            work = pathlib.Path(tempfile.mkdtemp(prefix="b202_"))
            try:
                code, out, lead = run(form, csrc, work)
            finally:
                shutil.rmtree(work, ignore_errors=True)
            code_ok = code == cexp
            #: "streamed early" means output was observed at least 0.3 s before
            #: the form finished -- the child sleeps 0.4 s between writes, so a
            #: form that only reveals output at the end cannot clear this.
            stream_ok = lead >= 0.3
            text_ok = out == baselines[cname]
            rec["codes"] &= code_ok
            rec["streams"] &= stream_ok
            rec["text"] &= text_ok
            print(f"  child {cname:22s} exit {code} (want {cexp}) "
                  f"{'OK ' if code_ok else 'BAD'}   "
                  f"streamed {lead:5.2f}s early {'OK ' if stream_ok else 'NO '}  "
                  f"text {'identical' if text_ok else 'DIFFERS'}")
        results[fname] = rec
        print(f"  => exit codes {'KEPT' if rec['codes'] else 'LOST'}; "
              f"streams {'YES' if rec['streams'] else 'NO'}; "
              f"captured text {'identical' if rec['text'] else 'DIFFERENT'}")

    print("\n" + "=" * 74)
    print("VERDICT")
    print("=" * 74)
    good = [n for n, r in results.items() if all(r.values())]
    for n, r in results.items():
        verdict = "CORRECT" if all(r.values()) else "REJECTED"
        why = []
        if not r["codes"]:
            why.append("loses the exit code -> the gate becomes a rubber stamp")
        if not r["streams"]:
            why.append("nothing observable until the phase ends")
        if not r["text"]:
            why.append("captured text differs -> the hook's greps change meaning")
        print(f"  {verdict:8s}  {n}" + (f"  ({'; '.join(why)})" if why else ""))
    if len(good) != 1:
        print(f"\n!! expected exactly 1 correct candidate, got {len(good)}: {good}")
        return 1
    print(f"\n  The only form that satisfies all 3: {good[0]}")
    print("  It is what `hooks/pre-commit` now uses for its guard phase.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
