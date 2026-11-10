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
    #: ★ THE LEDGER GAINED `why` ON 2026-11-09, on his ruling attached to
    #: B128: "we must be able to know why a commit was refused, so it can be
    #: repaired." Each of the 8 refusal points now names itself and the exit
    #: handler writes that name here, so the row carries 5 fields rather than
    #: 4. A clean exit records the empty string, which is the case driven
    #: below, and a refusal records its cause -- asserted end to end by
    #: bench/tests/test_a_refusal_records_why_2026-11-09.py, which RUNS the
    #: real hook in a throwaway repository rather than reading it.
    r = subprocess.run(
        ["sh", "-c", f"printf '{fmt}\\n' 2026-01-01T00:00:00Z 123 0 abc1234 ''"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    row = json.loads(r.stdout.strip())
    assert row == {"at": "2026-01-01T00:00:00Z", "seconds": 123,
                   "exit": 0, "head": "abc1234", "why": ""}, row
    #: AND A REFUSAL'S CAUSE SURVIVES THE SAME FORMAT STRING.
    r2 = subprocess.run(
        ["sh", "-c",
         f"printf '{fmt}\\n' 2026-01-01T00:00:00Z 9 1 abc1234 guard-file-missing"],
        capture_output=True, text=True, timeout=30)
    assert r2.returncode == 0, r2.stderr
    assert json.loads(r2.stdout.strip())["why"] == "guard-file-missing"


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

def test_an_interrupted_board_is_not_counted_as_a_refusal(prod):
    """A KILLED BOARD IS NOT A FAST REFUSAL, and the ledger cannot tell.

    Found hours after the ledger itself: the 4th row ever written was a board
    interrupted by hand and it recorded `{"seconds":12,"exit":1}` --
    shape-identical to a gate that refused quickly, because the hook sees only
    the exit code of a pytest whose process was killed, which is 1, the same
    code a genuine test failure gives.

    IT CHANGED THE FIGURES MATERIALLY, which is why this is guarded rather than
    noted: counting that row put "over the stated limit" at 4 of 5 instead of
    4 of 4, and the standard deviation at 314.9 seconds instead of 37.9 -- a
    factor of 8.3 on a number that describes how predictable the gate is.
    """
    assert hasattr(prod, "split_rows"), (
        "the producer no longer separates interrupted runs, so an "
        "interruption would be reported as a verdict about the gate's cost")
    rows = [{"seconds": 700, "exit": 0}, {"seconds": 12, "exit": 1},
            {"seconds": 680, "exit": 1}, {"seconds": 119, "exit": 1}]
    done, short = prod.split_rows(rows)
    assert [r["seconds"] for r in done] == [700, 680], done
    assert [r["seconds"] for r in short] == [12, 119], short


def test_the_threshold_is_below_any_real_board(prod):
    """ANTI-VACUITY in the dangerous direction.

    A threshold set too high would silently discard REAL runs and flatter the
    gate. The gate's cheap phase alone runs for minutes, so 120 s cannot
    exclude a completed board -- and every completed row in the live ledger
    must survive the split.
    """
    assert prod.INTERRUPTED_UNDER_SECONDS <= 120, (
        f"the cutoff is {prod.INTERRUPTED_UNDER_SECONDS} s, high enough to "
        f"discard a real board and report the gate as cheaper than it is")
    live = prod.rows()
    if not live:
        pytest.skip("no ledger rows on this machine yet")
    done, _short = prod.split_rows(live)
    for r in done:
        assert r["seconds"] >= prod.INTERRUPTED_UNDER_SECONDS
    # every row at or above the cutoff is kept: nothing real is dropped
    assert len(done) == sum(
        1 for r in live if r["seconds"] >= prod.INTERRUPTED_UNDER_SECONDS)


def test_a_ledger_of_only_interrupted_rows_claims_nothing(prod, tmp_path):
    """The honest degenerate case, rather than a distribution from noise."""
    p = tmp_path / "all_short.jsonl"
    p.write_text('{"at":"a","seconds":3,"exit":1,"head":"x"}\n'
                 '{"at":"b","seconds":9,"exit":1,"head":"y"}\n')
    rows = prod.rows(p)
    done, short = prod.split_rows(rows)
    assert done == [] and len(short) == 2, (done, short)
