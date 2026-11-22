# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'batch1_autonomy_2026-11-22_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0a4975a08d4b4f5e1e493d2d386d9dc5b7acc54de8f6bc4bab37ec340e626e69
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Do the 2 seats' B205(c) repairs COMPOSE, or are they orthogonal single fixes?

THE QUESTION, AND WHY A JUDGEMENT WILL NOT DO. The joint round of 2026-11-22
applied repairs from both seats to the same defect report:

  cc2    `scripts/blocker_triage.py:_ps_can_answer()` -- the predicate returns
         '' when `ps` cannot answer, restoring its documented fail-toward-
         writing direction. A change to the SUBJECT.
  fable  the `no_board` fixture in `bench/tests/test_blocker_triage_2026-09-10.py`
         -- the parking classes set the `CDSFL_BT_BOARD=0` seam the hook already
         carried, so they stop passing or failing by accident of machine state.
         A change to the HARNESS.

The founder's standing rule, verbatim 2026-10-02: compose only on a DEMONSTRATED
advantage over each fix alone, and the demonstration is a measurement. So this
script measures a 2x2 -- each repair present or absent -- against 2 NAMED
properties, and reports which cell discharges which.

  P1  the parking guards pass regardless of what else is running on the machine
  P2  `a_commit_board_is_running` returns '' where `ps` cannot answer, as its
      own docstring promises, so the Stop gate in `hooks/work_not_narrate.py`
      does not stand down on a false positive

METHOD. Both repairs are REMOVABLE in a scratch copy without touching the tree:
cc2's by forcing `_ps_can_answer` to return True (which is what the pre-repair
code did -- it never asked), fable's by neutralising the fixture's `setenv`.
P1 is measured with a LIVE non-shell process that `pgrep` is stubbed to name,
which is the machine state the fixture exists to isolate from. P2 is measured
with `ps` stubbed to exit 1.

Reads nothing outside the artefacts under review.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import time

for _c in (pathlib.Path(__file__).resolve().parent,
           *pathlib.Path(__file__).resolve().parents):
    if (_c / "_cli_help.py").is_file():
        sys.path.insert(0, str(_c))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
TRIAGE = REPO / "scripts" / "blocker_triage.py"
PARKING_GUARD = REPO / "bench" / "tests" / "test_blocker_triage_2026-09-10.py"
PARKING_CLASSES = ("TestTheParkingFileIsRealAndAppendOnly", "TestParkingIsIdempotent")

PROBE = r'''
import os, sys, importlib.util
os.environ.pop("CDSFL_BT_BOARD", None)
spec = importlib.util.spec_from_file_location("bt", r"{subject}")
m = importlib.util.module_from_spec(spec); sys.modules["bt"] = m
spec.loader.exec_module(m)
if not {cc2}:
    m._ps_can_answer = lambda: True      # pre-repair: the gate did not exist
print(repr(m.a_commit_board_is_running()))
'''


#: * A FUNCTIONAL `ps` SUBSTITUTE, AND THE FIRST VERSION OF THIS SCRIPT NEEDED
#: ONE AND DID NOT HAVE IT. The `ps_works=True` stub was `exec /bin/ps "$@"`,
#: and `/bin/ps` is not executable under panel seat confinement, so every arm
#: fell into the ps-DENIED branch, P1 read HOLDS in all 4 cells, and the script
#: printed a conclusion it had not computed. Its own 4-cell table is what
#: exposed that: a cell with BOTH repairs absent cannot legitimately hold.
#: The same version also set `CDSFL_COMPOSE_DROP_PS_GATE`, which nothing read
#: -- an addition nothing reaches, which the additive standard forbids. It is
#: deleted rather than wired, because the substitute below makes it needless.
#:
#: WHAT THE SUBSTITUTE IS, DESCRIBED IN FULL RATHER THAN GIVEN A NAME. The
#: subject under measurement is the predicate's LOGIC, not `ps` itself, and the
#: predicate asks `ps` exactly 3 questions: `-o comm=` for `_ps_can_answer`
#: (can you answer at all), `-o ppid=` for the ancestry walk, and `-o comm=`
#: for the shell test. A 10-line Python script answers all 3, so the arm where
#: `ps` WORKS becomes constructible on a machine where `/bin/ps` is denied. It
#: reports the planted pid as `python3` -- a real non-shell -- and no parent,
#: so the walk terminates and the shell exclusion declines to exclude. That is
#: exactly the machine state P1 is about.
_FAKE_PS = '#!/usr/bin/env python3\nimport sys\na = sys.argv[1:]\nif "ppid=" in a:\n    print("")                 # no parent: the ancestry walk terminates\n    sys.exit(0)\nif "comm=" in a:\n    print("python3")          # a real non-shell, so it is not excluded\n    sys.exit(0)\nsys.exit(1)\n'


def _stubs(d: pathlib.Path, pid: str, ps_works: bool):
    pg = d / "pgrep"; pg.write_text(f"#!/bin/sh\necho {pid}\nexit 0\n"); pg.chmod(0o755)
    ps = d / "ps"
    ps.write_text(_FAKE_PS if ps_works else "#!/bin/sh\nexit 1\n")
    ps.chmod(0o755)


def p2_holds(cc2: bool) -> bool:
    """Does the predicate return '' with `ps` denied and `pgrep` answering?"""
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td); _stubs(d, "99999", ps_works=False)
        env = dict(os.environ); env["PATH"] = f"{d}:{env.get('PATH','')}"
        env.pop("CDSFL_BT_BOARD", None)
        o = subprocess.run([sys.executable, "-c", PROBE.format(subject=TRIAGE, cc2=cc2)],
                           cwd=REPO, capture_output=True, text=True, timeout=120, env=env)
        return o.returncode == 0 and o.stdout.strip() in ("''", '""')


def p1_holds(cc2: bool, fable: bool, board_pid: str) -> tuple[bool, str]:
    """Do the parking guards pass with a live non-shell process on the machine?

    `pgrep` is stubbed to name that process, which is exactly the sibling-run
    condition the fixture exists to isolate from.
    """
    src = PARKING_GUARD.read_text()
    if not fable:
        marker = 'monkeypatch.setenv("CDSFL_BT_BOARD", "0")'
        assert src.count(marker) == 1, "the fixture's setenv has moved"
        src = src.replace(marker, 'pass  # fable repair REMOVED for this arm')
    copy = PARKING_GUARD.parent / f"_scratch_compose_{int(cc2)}{int(fable)}.py"
    copy.write_text(src)
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td); _stubs(d, board_pid, ps_works=True)
        env = dict(os.environ); env["PATH"] = f"{d}:{env.get('PATH','')}"
        env.pop("CDSFL_BT_BOARD", None)
        #: cc2's repair is INERT when `ps` answers -- `_ps_can_answer()` returns
        #: True and the gate falls through -- so on this arm the cc2-present and
        #: cc2-absent cells are behaviourally identical BY CONSTRUCTION, and
        #: that identity is itself the finding, not a gap in the measurement.
        try:
            o = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                 "--no-header", "-o", "addopts=", str(copy),
                 "-k", " or ".join(PARKING_CLASSES)],
                cwd=REPO, capture_output=True, text=True, timeout=600, env=env)
        finally:
            copy.unlink(missing_ok=True)
    last = (o.stdout + o.stderr).strip().splitlines()[-1] if (o.stdout or o.stderr) else "?"
    return o.returncode == 0, last


def main() -> int:
    #: A REAL non-shell process, so the shell exclusion cannot dismiss it. A
    #: dead pid would be dismissed by `ps` and the arm would measure nothing.
    board = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    time.sleep(0.5)
    bp = str(board.pid)
    try:
        print(f"planted a live non-shell process at pid {bp}; pgrep stubbed to "
              f"name only it\n")
        print("P2 -- the predicate returns '' where `ps` cannot answer")
        rows2 = {}
        for cc2 in (False, True):
            rows2[cc2] = p2_holds(cc2)
            print(f"  cc2 repair {'PRESENT' if cc2 else 'ABSENT ':8}: "
                  f"P2 {'HOLDS' if rows2[cc2] else 'FAILS'}")
        print("  (fable's repair is HARNESS-ONLY and cannot affect P2 at all)\n")

        print("P1 -- the parking guards pass regardless of machine state")
        rows1 = {}
        for cc2 in (False, True):
            for fable in (False, True):
                ok, last = p1_holds(cc2, fable, bp)
                rows1[(cc2, fable)] = ok
                print(f"  cc2 {'Y' if cc2 else 'N'} / fable {'Y' if fable else 'N'}: "
                      f"P1 {'HOLDS' if ok else 'FAILS'}   [{last}]")
        print()

        bad = []
        # Each property must be discharged by exactly ONE of the two repairs.
        if not (rows2[True] and not rows2[False]):
            bad.append("P2 is not discharged by cc2's repair alone")
        if not rows1[(False, True)]:
            bad.append("P1 is not discharged by fable's repair alone")
        # The composed cell must not beat fable's cell alone on P1.
        if rows1[(True, True)] and not rows1[(False, True)]:
            bad.append("the composed form DOES dominate on P1 -- composition "
                       "would be warranted and this script's conclusion is wrong")
        #: * ANTI-VACUITY ON P1, THE CHECK THE FIRST VERSION LACKED. If a cell
        #: with fable's repair ABSENT still holds, the arm did not reproduce the
        #: condition P1 is about and the 4 cells say nothing at all.
        if rows1[(True, False)] or rows1[(False, False)]:
            bad.append("P1 holds with fable's repair ABSENT, so this arm did not "
                       "reproduce a detectable sibling run: the 4 cells are "
                       "VACUOUS and no conclusion may be drawn from them")
        if bad:
            for b in bad:
                print(f"FALSIFIED — {b}")
            return 1
        print("MEASURED CONCLUSION. P2 is discharged by cc2's repair alone and "
              "is untouched by fable's, which is harness-only. P1 is discharged "
              "by fable's repair alone; cc2's repair alone does NOT discharge it "
              f"(cell cc2 Y / fable N: P1 {'HOLDS' if rows1[(True, False)] else 'FAILS'}), "
              "because the seam is read BEFORE `_ps_can_answer` and a working "
              "`ps` leaves the sibling pid detected. No cell dominates either "
              "single fix on the other's property, so these are 2 ORTHOGONAL "
              "SINGLE FIXES and not a composition. Under the founder's rule the "
              "single fixes stand.")
        return 0
    finally:
        board.terminate()
        try:
            board.wait(timeout=5)
        except Exception:                                    # noqa: BLE001
            board.kill()


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
