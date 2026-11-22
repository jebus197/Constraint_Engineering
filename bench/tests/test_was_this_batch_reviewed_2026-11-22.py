"""The panel-round detector must answer in BOTH directions, and never refuse.

HIS INSTRUCTION it serves, 2026-11-21: every meaningful batch of work goes to a
free panel before its fixes are adopted. The detector reports, at commit time,
whether that happened for the batch being committed.

WHY BOTH DIRECTIONS ARE TESTED EXPLICITLY. A detector that always answers "no"
passes every test written against a repository with no recent round, and this
project has recorded that exact failure: the passing input cannot test a
defence. So each property is asserted once on an input that should match and
once on an input that should not.

WHY THE FAIL-OPEN PROPERTY IS A TEST AND NOT A COMMENT. The script runs inside
the pre-commit pre-flight. A non-zero exit or an exception there would turn an
advisory line into a commit refusal costing about 27 minutes of his machine --
the opposite of what it is for.
"""
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "was_this_batch_reviewed_2026-11-22.py"
PRECOMMIT = REPO / "hooks" / "pre-commit"


def _mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("wtbr_guard", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["wtbr_guard"] = m
    spec.loader.exec_module(m)
    return m


def _round(root, name, *, barrier=True, seats=(), broken=(), junk=()):
    d = root / name
    d.mkdir(parents=True)
    if barrier:
        (d / "completion_barrier.json").write_text(json.dumps({"n_seats": len(seats)}))
    for s in seats:
        (d / f"{s}.json").write_text(json.dumps({"ok": True, "response": "a verdict"}))
    for s in broken:
        (d / f"{s}.json").write_text(json.dumps({"ok": False, "response": ""}))
    for j in junk:
        (d / f"{j}.json").write_text(json.dumps({"anything": 1}))
    return d


# --------------------------------------------------------------- seats_in

def test_a_seat_reply_counts(tmp_path):
    d = _round(tmp_path, "r", seats=("cc2", "fable"))
    ok, bad = _mod().seats_in(d)
    assert sorted(ok) == ["cc2", "fable"] and bad == []


def test_harness_bookkeeping_is_not_a_seat_reply(tmp_path):
    """topology.json and friends are the harness's own files, not a review."""
    d = _round(tmp_path, "r", junk=("topology", "sandbox_manifest",
                                    "canonical_attribution", "completion_barrier"))
    ok, bad = _mod().seats_in(d)
    assert ok == [] and bad == [], (ok, bad)


def test_a_failed_seat_is_not_a_review(tmp_path):
    d = _round(tmp_path, "r", broken=("cc2",))
    ok, bad = _mod().seats_in(d)
    assert ok == [] and bad == ["cc2"]


def test_an_empty_response_is_not_a_review(tmp_path):
    """ok=True with nothing said is the fail-safe-recorded-as-fact error."""
    d = tmp_path / "r"
    d.mkdir()
    (d / "cc2.json").write_text(json.dumps({"ok": True, "response": "   "}))
    ok, bad = _mod().seats_in(d)
    assert ok == [] and bad == ["cc2"]


def test_unreadable_seat_json_is_counted_as_failed_not_ok(tmp_path):
    d = tmp_path / "r"
    d.mkdir()
    (d / "cc2.json").write_text("{not json")
    ok, bad = _mod().seats_in(d)
    assert ok == [] and bad == ["cc2"]


# ------------------------------------------------------------ rounds_since

def test_a_round_without_the_barrier_is_incomplete(tmp_path, monkeypatch):
    """Completion is read from the marker, never inferred from seat files."""
    m = _mod()
    monkeypatch.setattr(m, "LOGS", tmp_path)
    _round(tmp_path, "unfinished", barrier=False, seats=("cc2",))
    assert m.rounds_since(None) == []


def test_a_complete_round_is_found(tmp_path, monkeypatch):
    m = _mod()
    monkeypatch.setattr(m, "LOGS", tmp_path)
    _round(tmp_path, "done", seats=("cc2",))
    got = m.rounds_since(None)
    assert [r["dir"] for r in got] == ["done"] and got[0]["ok"] == ["cc2"]


def test_rounds_before_the_cutoff_are_excluded(tmp_path, monkeypatch):
    """The window is what makes it answer about THIS batch rather than ever."""
    m = _mod()
    monkeypatch.setattr(m, "LOGS", tmp_path)
    old = _round(tmp_path, "old", seats=("cc2",))
    import os
    os.utime(old / "completion_barrier.json", (1_000_000, 1_000_000))
    new = _round(tmp_path, "new", seats=("fable",))
    os.utime(new / "completion_barrier.json", (2_000_000, 2_000_000))
    assert [r["dir"] for r in m.rounds_since(1_500_000)] == ["new"]
    assert sorted(r["dir"] for r in m.rounds_since(500_000)) == ["new", "old"]


def test_newest_round_is_reported_first(tmp_path, monkeypatch):
    m = _mod()
    monkeypatch.setattr(m, "LOGS", tmp_path)
    import os
    a = _round(tmp_path, "a", seats=("cc2",))
    b = _round(tmp_path, "b", seats=("cc2",))
    os.utime(a / "completion_barrier.json", (1_000_000, 1_000_000))
    os.utime(b / "completion_barrier.json", (2_000_000, 2_000_000))
    assert [r["dir"] for r in m.rounds_since(None)][0] == "b"


# ------------------------------------------------------------------ the CLI

def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=REPO, capture_output=True, text=True, timeout=120)


def test_quiet_prints_exactly_one_line_and_exits_zero():
    p = _run("--quiet")
    assert p.returncode == 0, p.stderr
    assert len([l for l in p.stdout.splitlines() if l.strip()]) == 1, p.stdout


def test_quiet_says_zero_when_there_is_nothing_in_the_window():
    """A window ending before this repository existed must find 0."""
    p = _run("--quiet", "--since", "2099-01-01T00:00:00")
    assert p.returncode == 0
    assert "0 panel rounds" in p.stdout


def test_quiet_reports_rounds_that_do_exist():
    """The matching direction, so the test cannot pass by always saying no."""
    p = _run("--quiet", "--since", "2020-01-01T00:00:00")
    assert p.returncode == 0, p.stderr
    assert "reviewed round" in p.stdout, p.stdout


def test_a_bad_since_value_exits_nonzero_but_only_outside_the_hook():
    """Argument errors are loud; the hook never passes --since."""
    p = _run("--quiet", "--since", "not-a-date")
    assert p.returncode == 2


def test_the_full_report_runs_and_exits_zero():
    p = _run()
    assert p.returncode == 0, p.stderr
    assert "Measuring panel rounds completed since" in p.stdout


# ------------------------------------------------------------- it is wired

def test_the_precommit_preflight_calls_it():
    """additive-standard: an addition nothing reaches is not additive."""
    t = PRECOMMIT.read_text()
    assert "was_this_batch_reviewed_2026-11-22.py" in t, (
        "the detector exists but no caller runs it")


def test_the_preflight_call_falls_open():
    """A report that can refuse a commit is not a report."""
    t = PRECOMMIT.read_text()
    #: ★ ANCHOR ON THE INVOCATION, NOT THE BARE FILENAME — this test failed on
    #: the 2026-11-22 board for exactly that reason. The GUARDS list contains
    #: `bench/tests/test_was_this_batch_reviewed_2026-11-22.py`, whose name
    #: CONTAINS this script's name, and it sits about 250 lines EARLIER in the
    #: file. `str.index` found that, and the 400 characters after it are other
    #: guard paths. A substring is not a call.
    call = "python3 scripts/was_this_batch_reviewed_2026-11-22.py"
    assert call in t, "the pre-flight no longer invokes the detector"
    i = t.index(call)
    window = t[i:i + 300]
    assert "|| true" in window, "the pre-flight call must not be able to fail the commit"


def test_the_preflight_block_is_valid_shell():
    p = subprocess.run(["bash", "-n", str(PRECOMMIT)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
