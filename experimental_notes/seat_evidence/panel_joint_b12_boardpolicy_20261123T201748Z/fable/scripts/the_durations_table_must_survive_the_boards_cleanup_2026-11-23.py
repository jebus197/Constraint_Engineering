# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'panel_joint_b12_boardpolicy_20261123T201748Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1b13cce2052b2cf62f0f96c82c244edf85d185e28feab62c7ac7905e8b5418a8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The board's per-guard attribution must outlive the board's own cleanup.

DESTINATION `scripts/`. Written 2026-11-23, panel round `panel_b12_20261123T170728Z`.

WHY. B207 wired `--durations=25` into the board, answering an earlier finding
that a durations reader parsed a table no caller emitted. But the table is
written to `$_CDSFL_BOARD_LOG`, which `hooks/pre-commit` deletes with `rm -f`
right after capturing `$OUT`, and no grep over `$OUT` reads the durations
section. Measured 2026-11-23: 0 persisted durations tables exist anywhere in
`.cdsfl_tmp/` (the 6 retained board logs all predate B207). So the instrument
that attributes the board's measured growth -- 5.4980 min/day at a CONSTANT
guard count of 331, per
`scripts/the_growth_is_per_guard_not_more_guards_2026-11-23.py` -- ran on
every board and retained nothing.

WHAT THIS CHECKS, in 2 parts, and why the parts differ in kind:

  1. EXECUTED: `hooks/board_durations_persist.sh` is run byte-for-byte in a
     real /bin/sh against a rigged board log carrying a known durations table.
     The stamped block must land in `.cdsfl_tmp/board_durations.log`, twice
     for 2 boards, and a log with NO table must append nothing. The helper is
     a sourced file precisely so this part needs no retyping -- a retyped
     snippet would prove nothing about the hook's actual bytes.
  2. POSITIONAL, and named as such: the hook itself cannot execute without a
     `.git`, so its side is checked on its text -- the call line must exist
     and must sit ABOVE the `rm -f` that deletes its input. This is the same
     anchoring compromise the hook's own B207 comment records for its 4
     pinned-literal guards.

Exit 0 and no FALSIFIED token when both hold; exit 1 with FALSIFIED otherwise,
so `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py` can drive it
differentially against a hook copy with the call removed.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

def _repo_root() -> pathlib.Path:
    """Marker walk, never directory counting -- the counted form computed every
    figure of an earlier brief on an empty set
    (`why_is_the_board_getting_slower_2026-11-23.py` records the incident)."""
    for base in (pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        for d in (base, *base.parents):
            if (d / "hooks" / "pre-commit").is_file() and (d / "bench").is_dir():
                return d
    raise RuntimeError("cannot locate the repository root")


REPO = _repo_root()
HELPER = REPO / "hooks" / "board_durations_persist.sh"
HOOK = REPO / "hooks" / "pre-commit"

TABLE = """.....                                                                    [100%]
============================= slowest 25 durations =============================
9.88s call     bench/tests/test_slowest_guard.py::test_a
1.02s call     bench/tests/test_quick_guard.py::test_b
5 passed in 12.34s
"""


def fail(msg: str) -> int:
    print(f"FALSIFIED: {msg}")
    return 1


def main() -> int:
    # ── part 1: EXECUTE the real helper in /bin/sh ──────────────────────────
    if not HELPER.is_file():
        return fail(f"{HELPER.name} does not exist; nothing persists the table")
    with tempfile.TemporaryDirectory() as td:
        sand = pathlib.Path(td)
        log = sand / "cdsfl_board_fake.log"
        log.write_text(TABLE, encoding="utf-8")
        out = sand / ".cdsfl_tmp" / "board_durations.log"

        def call(exit_code: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                ["/bin/sh", "-c",
                 f'. "{HELPER}" && cd "{sand}" && '
                 f'_cdsfl_persist_durations "{log}" {exit_code}'],
                capture_output=True, text=True)

        r = call("0")
        if r.returncode != 0:
            return fail(f"helper exited {r.returncode}: {r.stderr}")
        if not out.is_file():
            return fail("no board_durations.log was written")
        text = out.read_text(encoding="utf-8")
        for needle in ("slowest 25 durations",
                       "9.88s call     bench/tests/test_slowest_guard.py::test_a",
                       "exit=0", "5 passed in 12.34s"):
            if needle not in text:
                return fail(f"persisted block lacks {needle!r}")
        if ".....  " in text.split("slowest")[0] and "[100%]" in text.split("slowest")[0]:
            return fail("progress noise above the table was persisted")
        r = call("1")
        text = out.read_text(encoding="utf-8")
        if text.count("slowest 25 durations") != 2 or "exit=1" not in text:
            return fail("a 2nd board did not append a 2nd stamped block")
        # a log with no table appends NOTHING -- absence is not an error
        log.write_text("no table here\n1 passed in 0.10s\n", encoding="utf-8")
        before = text
        r = call("0")
        if r.returncode != 0:
            return fail("helper must exit 0 on a table-less log (fail-open telemetry)")
        if out.read_text(encoding="utf-8") != before:
            return fail("a table-less log appended a block")

    # ── part 2: the hook calls it, ABOVE the rm that deletes its input ──────
    hook = HOOK.read_text(encoding="utf-8")
    call_line = '_cdsfl_persist_durations "$_CDSFL_BOARD_LOG" "$CODE"'
    rm_line = 'rm -f "$_CDSFL_BOARD_LOG"'
    if call_line not in hook:
        return fail("hooks/pre-commit never calls _cdsfl_persist_durations; "
                    "the rm still destroys the only copy of the table")
    if rm_line not in hook:
        return fail("the rm anchor moved; re-verify the ordering by hand")
    if hook.index(call_line) > hook.index(rm_line):
        return fail("the persistence call sits BELOW the rm; it reads a deleted file")

    print("OK: helper persists the table (executed, 3 arms) and the hook "
          "calls it above the rm (positional).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
