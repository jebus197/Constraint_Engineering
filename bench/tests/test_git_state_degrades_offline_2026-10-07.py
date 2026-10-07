"""Recovery must survive the network being down, because that is when it is needed.

RAISED BY THE FOUNDER, 2026-10-07: *"You should have your notes too to account
for network instability."* Acting on that turned up the reason it matters:
`scripts/cdsfl_recover.py` -- the `rs` restore -- CRASHED when the network was
unreachable, and so did `cdsfl_sv.py` and `cdsfl_qc.py`. All 3 call `git_state()`,
which fetched unconditionally.

MEASURED 2026-10-07 by substituting each failure mode into the live function:

    fetch exits NON-ZERO (fast offline refusal) -> SURVIVED
    fetch raises TimeoutExpired (flaky link)     -> CRASHED
    fetch raises OSError (interface down)        -> CRASHED

`_run_git_rc` returns `(returncode, stdout)`, so the return-code path was already
tolerated; the RAISED forms were not caught anywhere. 11 of the 25 failures on
the 2026-10-07 full board were this single cause, 44.0000% of them, Wilson
[26.6656%, 62.9327%]; the same 10 tests pass with the link up, which is what
establishes the cause as network-conditional rather than a code regression.

AND THE DEFECT THE FIX ITSELF NEARLY INTRODUCED, which is why these cases exist.
`git status --porcelain` prints NOTHING for a clean tree, so an empty stdout from
a FAILED call is byte-identical to success on a clean tree. Degrading a raised
error to "no output" therefore made "I cannot see the tree" render as "the tree
is clean" -- a failure that does not look like a failure. The return code is the
only thing separating the two, so it is read rather than inferred, and an
unreadable tree is reported as NOT clean under `p-pass-ambiguity-default`.

Every test CALLS `git_state` with `subprocess.run` substituted. Nothing here
reaches the network and nothing asserts on source text.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def U():
    spec = importlib.util.spec_from_file_location(
        "cdsfl_utils_offline", REPO / "scripts" / "cdsfl_utils.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_utils_offline"] = m
    spec.loader.exec_module(m)
    return m


def _only(monkeypatch, which: str, *, rc=None, raises=None):
    """Make ONE git subcommand fail, leaving the rest genuinely working."""
    real = subprocess.run

    def fake(cmd, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) > 1 and cmd[1] == which:
            if raises is not None:
                raise raises
            return subprocess.CompletedProcess(cmd, rc, "", "fatal")
        return real(cmd, **kw)

    monkeypatch.setattr(subprocess, "run", fake)


class TestAFetchThatCannotRunNoLongerCrashes:
    @pytest.mark.parametrize("exc", [
        subprocess.TimeoutExpired(["git", "fetch"], 30),
        OSError("Network is unreachable"),
        FileNotFoundError("git"),
    ])
    def test_each_raised_form_degrades(self, U, monkeypatch, exc):
        _only(monkeypatch, "fetch", raises=exc)
        st = U.git_state()                      # must not raise
        assert isinstance(st["remote_sync"], str) and st["remote_sync"]

    def test_a_non_zero_fetch_still_degrades_as_it_always_did(self, U, monkeypatch):
        _only(monkeypatch, "fetch", rc=128)
        assert U.git_state()["remote_sync"]

    def test_the_helper_reports_a_failure_as_a_non_zero_code(self, U, monkeypatch):
        real = subprocess.run

        def fake(cmd, **kw):
            raise OSError("down")

        monkeypatch.setattr(subprocess, "run", fake)
        rc, out = U._run_git_rc("status", "--porcelain")
        assert rc != 0, "a call that could not run must not report success"
        assert out == ""


class TestAnUnreadableTreeIsNeverReportedClean:
    """The defect the fix nearly introduced. These are the load-bearing cases."""

    @pytest.mark.parametrize("kw", [
        {"rc": 128},
        {"raises": OSError("down")},
        {"raises": subprocess.TimeoutExpired(["git", "status"], 30)},
    ])
    def test_a_failed_status_does_not_claim_a_clean_tree(self, U, monkeypatch, kw):
        _only(monkeypatch, "status", **kw)
        st = U.git_state()
        assert st["clean"] is not True, (
            "an empty `git status --porcelain` from a FAILED call is identical to "
            "success on a clean tree; reporting it as clean is a failure that "
            "does not look like a failure")
        assert st["status_known"] is False
        assert any("UNKNOWN" in line for line in st["uncommitted"]), st["uncommitted"]

    def test_a_real_read_still_reports_truthfully(self, U):
        st = U.git_state()
        assert st["status_known"] is True
        assert isinstance(st["clean"], bool)
        assert st["clean"] == (len(st["uncommitted"]) == 0)

    def test_every_git_subcommand_dead_still_returns_usable_state(self, U, monkeypatch):
        monkeypatch.setattr(
            subprocess, "run",
            lambda *a, **k: (_ for _ in ()).throw(OSError("no git at all")))
        st = U.git_state()
        assert st["clean"] is not True
        assert st["status_known"] is False
        assert st["last_hash"] == "unknown"


class TestTheThreeCallersAreCovered:
    """FOLLOW, executed: the fault was shared by 3 scripts, not 1."""

    @pytest.mark.parametrize("script,line_owner", [
        ("cdsfl_recover.py", "rs"),
        ("cdsfl_sv.py", "sv"),
        ("cdsfl_qc.py", "qc"),
    ])
    def test_each_caller_imports_the_repaired_helper(self, script, line_owner):
        src = (REPO / "scripts" / script).read_text()
        assert "git_state" in src, (
            f"{script} ({line_owner}) no longer calls git_state; this guard's "
            "blast-radius claim is stale and must be re-measured")

    def test_the_unconditional_fetch_is_still_the_only_network_call(self, U):
        src = (REPO / "scripts" / "cdsfl_utils.py").read_text()
        assert src.count('_run_git("fetch"') + src.count("_run_git('fetch'") == 1, (
            "a second network call appeared; OFFLINE_RECOVERY.md names this file "
            "and must be re-checked")
