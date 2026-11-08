"""The commit gate now has a cost HISTORY, not 1 overwritten number. B81.

HIS RULING, 2026-11-08: *"Add the guard, but make sure it contains a check for
why the commit is failing and so that it gives the reason for the failure, if
not already done. stm"*

WHAT WAS ALREADY DONE, reported because his own words invite it: the hook
already extracts the failing tests and prints them, so a refusal from a red
guard already says which guard. What was NOT in place is a refusal from the
LIMIT -- because there was no limit to refuse from.

THE DEFECT. The hook recorded its duration by OVERWRITING a single scratch
number, so the gate had no cost history at all. Every statement about what it
costs came from 1 number describing the last run, and the limit stated in the
hook's own header -- 11 minutes, so 660 seconds -- had nothing to be checked
against. Measured from this session's own boards: 652, 683 and 698 seconds, so
the gate sits ON that line rather than inside it.

THE OUTCOME IS RECORDED BESIDE THE DURATION, and that is the half worth having.
A refusal leaves NO trace in the repository -- which is why this session's own
refusal count had to be reported as session-observed rather than derived. From
the first ledger row onward it is derivable.

WHAT IS DELIBERATELY NOT BUILT: the refusal. B81's guard fails when the gate
exceeds its stated limit, and the gate is AT that limit today, so a refusing
guard would block every commit until the guard set is split into a commit-time
tier and a periodic one. That split and its bound are **B103**, which is his,
and which the decisions file records as 1 decision wearing 2 numbers.

THE APPEND MUST NEVER COST A COMMIT. An unwritable spool is worth a lost line
of history and not a refused commit, so every command in the block is
redirected. That is asserted here rather than hoped for, and the printf is
EXECUTED in a subshell to prove it emits parseable JSON -- a format error would
otherwise sit in the hook until the first time anyone read the ledger.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks/pre-commit"
PRODUCER = (REPO / "scripts"
            / "what_the_commit_gate_actually_costs_over_time_2026-11-08.py")


@pytest.fixture(scope="module")
def prod():
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    spec = importlib.util.spec_from_file_location("_gatecost", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_hook_appends_to_a_ledger():
    src = HOOK.read_text(encoding="utf-8")
    live = [l for l in src.splitlines()
            if "precommit_durations.jsonl" in l.split("#", 1)[0]]
    assert live, (
        "hooks/pre-commit does not append to a durations ledger on a live "
        "line, so the gate still has no cost history")
    assert any(">>" in l for l in live), (
        "the ledger is written with a single `>` somewhere, which OVERWRITES "
        "and recreates the exact defect B81 names")


def test_the_single_scratch_number_is_kept():
    """NOTHING IS REMOVED. scripts/cdsfl_sv.py:620 reads this exact path."""
    src = HOOK.read_text(encoding="utf-8")
    assert "precommit_seconds" in src, (
        "the scratch duration file is gone, and cdsfl_sv.py derives its own "
        "timeout from it")
    sv = (REPO / "scripts/cdsfl_sv.py").read_text(encoding="utf-8")
    assert ".cdsfl_tmp/precommit_seconds" in sv, (
        "cdsfl_sv.py no longer names that path; if it moved, the hook's write "
        "needs to move with it")


def test_the_append_records_the_outcome_too():
    """A refusal leaves no other trace in the repository."""
    src = HOOK.read_text(encoding="utf-8")
    i = src.index("precommit_durations.jsonl")
    window = src[max(0, i - 900):i]
    assert '"exit"' in window, (
        "the ledger line carries no exit code, so the refusal rate stays "
        "session-observed and underivable")
    assert '"seconds"' in window and '"head"' in window, window[-300:]


def test_the_append_cannot_fail_a_commit():
    """An unwritable spool is worth a lost line, not a refused commit."""
    src = HOOK.read_text(encoding="utf-8")
    i = src.index(">> .cdsfl_tmp/precommit_durations.jsonl")
    tail = src[i:i + 120]
    assert "2>/dev/null" in tail, (
        f"the append is not redirected, so a write failure could surface as a "
        f"hook error and refuse a commit: {tail!r}")


def test_the_printf_emits_parseable_json():
    """EXECUTED in a subshell, not read. A format error would otherwise sit
    in the hook until the first time anyone read the ledger."""
    src = HOOK.read_text(encoding="utf-8")
    m = re.search(r"printf '(\{[^']*\})\\n'", src)
    assert m, "could not find the ledger printf format string in the hook"
    fmt = m.group(1)
    r = subprocess.run(
        ["sh", "-c", f"printf '{fmt}\\n' 2026-01-01T00:00:00Z 123 0 abc1234"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    row = json.loads(r.stdout.strip())
    assert row == {"at": "2026-01-01T00:00:00Z", "seconds": 123,
                   "exit": 0, "head": "abc1234"}, row


def test_the_producer_runs_with_no_ledger_and_says_so(prod):
    """The honest first-run state, rather than a distribution from 1 number."""
    r = subprocess.run(["python3", str(PRODUCER)], capture_output=True,
                       text=True, timeout=120, cwd=str(REPO))
    assert r.returncode == 0, r.stderr[-600:]
    assert "660" in r.stdout, "the stated limit is not reported"


def test_malformed_rows_are_skipped_not_fatal(prod, tmp_path):
    """A corrupt line must cost its own row and nothing else."""
    p = tmp_path / "led.jsonl"
    p.write_text('{"at":"x","seconds":100,"exit":0,"head":"a"}\n'
                 'not json at all\n'
                 '{"seconds":"not an int"}\n'
                 '\n'
                 '{"at":"y","seconds":700,"exit":1,"head":"b"}\n')
    got = prod.rows(p)
    assert len(got) == 2, got
    assert [g["seconds"] for g in got] == [100, 700]


def test_the_producer_reads_a_real_row(prod, tmp_path):
    """ANTI-VACUITY. `rows` returning [] for everything would pass the test
    above, because 2 != 0 is the only thing it checks there."""
    p = tmp_path / "one.jsonl"
    p.write_text('{"at":"z","seconds":661,"exit":0,"head":"c"}\n')
    got = prod.rows(p)
    assert len(got) == 1 and got[0]["seconds"] == 661, got
    assert prod.STATED_LIMIT_SECONDS == 660, (
        "the stated limit moved; the hook's header says 11 minutes")
