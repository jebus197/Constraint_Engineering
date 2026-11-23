# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_joint_b12_boardpolicy_20261123T201748Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 59c9ce37fc0598b4d2a52ed15026802e1515b878121ca6b38177373b7cd139f4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The board's `--durations` table was produced and deleted 1 line later.

DESTINATION `scripts/`. Written 2026-11-23. FALSIFIER for the retention block
in `hooks/pre-commit` marked `>>> CDSFL durations retention`.

WHAT IS CLAIMED, AND IT IS A CLAIM ABOUT 2 LINES OF ONE FILE. B207 exported
`PYTEST_ADDOPTS="--durations=25"` immediately above the board's pytest call,
and its own comment states the purpose: "feed the durations reader, which
parsed a table no caller emitted." The reader exists --
`scripts/which_tests_outlive_the_global_timeout_2026-10-18.py --durations LOG`,
whose `read_durations` matches pytest's `  12.34s call  path::test` rows. The
table is written ONLY into `$_CDSFL_BOARD_LOG`, and `rm -f "$_CDSFL_BOARD_LOG"`
removed that file at the end of every board. So the reader had NO INPUT on any
run after B207 landed, and the per-guard attribution that
`scripts/why_is_the_board_getting_slower_2026-11-23.py` names as "the next
measurement" was generated and destroyed once per board.

HOW IT IS CHECKED, END TO END RATHER THAN BY READING. The retention block is
EXTRACTED FROM THE REAL HOOK between its 2 markers and EXECUTED by `sh` in a
throwaway directory, against a synthetic board log carrying a real pytest
durations table. Whatever that block writes is then handed to the REAL
`read_durations`, imported from the real reader file. The check passes only if
a row the pytest table contained comes back out of the reader. A block that is
present but greps the wrong shape therefore FAILS -- which is the point, since
the defect being closed is precisely an output nothing could consume.

ORDER IS PART OF THE CLAIM. Retention after `rm -f` would read a file that no
longer exists, so the marker's position relative to the removal is asserted
too.

IT WRITES NOTHING INTO THE REPOSITORY. The extracted block is run with its cwd
set to a `TemporaryDirectory`, and the block's own output path is relative, so
`.cdsfl_tmp/board_durations/` is created there and discarded.

VERDICT PROTOCOL. Prints `FALSIFIED` and exits 1 when the defect is present
(no retention, retention after the removal, or a table that does not survive
the round trip). Exits 0 when the defect is absent.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import subprocess
import sys
import tempfile

START = ">>> CDSFL durations retention"
END = "<<< CDSFL durations retention"

#: A board log as pytest -q --durations=25 actually emits it. The 4 phase rows
#: are the payload; everything else is here so a block that greps too loosely
#: is caught rather than flattered.
SYNTHETIC_BOARD_LOG = """\
........................................................................ [  1%]
F....................................................................... [  2%]
=========================== short test summary info ============================
FAILED bench/tests/test_example_2026-01-01.py::TestThing::test_a_thing
============================= slowest 25 durations =============================
38.21s call     bench/tests/test_help_is_answered_2026-09-11.py::test_every_script_answers
12.13s call     bench/tests/test_does_filtering_the_stale_constant_repair_two_2026-10-30.py::test_two
 4.52s setup    bench/tests/test_panel_records_are_preserved_2026-09-11.py::test_records
 0.31s teardown bench/tests/test_a_refusal_records_why_2026-11-09.py::test_why
1 failed, 5129 passed, 27 skipped in 2615.21s (0:43:35)
"""

#: Rows the reader MUST return, keyed the way `read_durations` keys them.
EXPECT = {
    "bench/tests/test_help_is_answered_2026-09-11.py::test_every_script_answers": 38.21,
    "bench/tests/test_panel_records_are_preserved_2026-09-11.py::test_records": 4.52,
}


def _repo_root() -> pathlib.Path:
    """Walk up for a MARKER rather than counting directory levels.

    Counting `parents[N]` is how the figures in this batch's own brief came to
    be computed on an empty set, recorded in
    `why_is_the_board_getting_slower_2026-11-23.py`. cwd is tried as well
    because this file is run from a scratch copy when it is driven through
    `a_falsifier_must_disagree_with_itself_2026-11-23.py`.
    """
    for base in (pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        for d in (base, *base.parents):
            if (d / "hooks" / "pre-commit").is_file() and (d / "bench").is_dir():
                return d
    raise RuntimeError("cannot locate the repository root")


REPO = _repo_root()
HOOK = REPO / "hooks" / "pre-commit"
READER = REPO / "scripts" / "which_tests_outlive_the_global_timeout_2026-10-18.py"


def real_read_durations():
    """Import `read_durations` FROM THE REAL READER, never a retyped copy.

    A model-authored reimplementation would prove nothing about whether the
    retained file is consumable by the caller B207 named.
    """
    spec = importlib.util.spec_from_file_location("_cdsfl_durations_reader", READER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_durations


def retention_block(text: str) -> str | None:
    """The block between the markers, or None when the hook has no retention."""
    i = text.find(START)
    j = text.find(END)
    if i < 0 or j < 0 or j <= i:
        return None
    return text[text.index("\n", i) + 1:text.rindex("\n", i, j) + 1]


def removal_comes_after(text: str) -> bool:
    """`rm -f "$_CDSFL_BOARD_LOG"` must follow the retention, not precede it."""
    j = text.find(END)
    rm = text.find('rm -f "$_CDSFL_BOARD_LOG"')
    return j >= 0 and rm > j


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hook", default=str(HOOK),
                    help="the hook to test; defaults to the repository's own")
    a = ap.parse_args(argv)

    hook_text = pathlib.Path(a.hook).read_text(encoding="utf-8", errors="replace")

    block = retention_block(hook_text)
    if block is None:
        print("FALSIFIED: hooks/pre-commit carries NO durations retention; the "
              "board log is removed with the --durations table still in it, so "
              "the reader B207 was wired to feed has no input.")
        raise AssertionError("no durations retention block in the hook")

    if not removal_comes_after(hook_text):
        print("FALSIFIED: the retention block does not precede "
              'rm -f "$_CDSFL_BOARD_LOG"; it would read a removed file.')
        raise AssertionError("retention is not above the removal")

    read_durations = real_read_durations()

    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        log = d / "board.log"
        log.write_text(SYNTHETIC_BOARD_LOG)
        script = d / "retain.sh"
        script.write_text(
            "set -u\n"
            '_CDSFL_BOARD_LOG="' + str(log) + '"\n'
            "CODE=1\n"
            'GUARDS="bench/tests/test_a_2026-01-01.py\n'
            'bench/tests/test_b_2026-01-01.py"\n'
            + block
        )
        r = subprocess.run(["sh", str(script)], cwd=td,
                           capture_output=True, text=True, timeout=60)
        produced = [p for p in sorted(d.rglob("*.log")) if p != log]
        if r.returncode != 0:
            print("FALSIFIED: the retention block exited "
                  f"{r.returncode}\n{r.stderr[:800]}")
            raise AssertionError("the retention block failed to run")
        if not produced:
            print("FALSIFIED: the retention block ran and wrote no file, so "
                  "nothing was retained.")
            raise AssertionError("retention wrote nothing")

        got = {}
        for p in produced:
            got.update(read_durations(p))

        print(f"  retained files             : {[p.name for p in produced]}")
        print(f"  rows the REAL reader parsed: {len(got)}")
        missing = {k: v for k, v in EXPECT.items() if k not in got}
        if missing:
            print("FALSIFIED: the retained file is not consumable by "
                  f"read_durations; missing {sorted(missing)}")
            raise AssertionError("round trip lost the durations table")
        for k, v in EXPECT.items():
            phases = got[k]
            if abs(sum(phases.values()) - v) > 1e-9:
                print(f"FALSIFIED: {k} came back as {phases}, expected {v}s")
                raise AssertionError("a retained duration was corrupted")
        header = [l for p in produced
                  for l in p.read_text().splitlines() if l.startswith("# board ")]
        if not header or "guards=" not in header[0]:
            print("FALSIFIED: the retained file carries no board stamp, so a "
                  "reader cannot say which run or which guard count it is.")
            raise AssertionError("no board stamp retained")
        print(f"  board stamp                : {header[0]}")

    print("  the durations table survives the hook's own retention and is "
          "parsed by the reader B207 named. Defect ABSENT.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__, takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
