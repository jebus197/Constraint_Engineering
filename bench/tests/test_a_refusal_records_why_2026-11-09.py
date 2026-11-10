"""A refused commit must record WHY, not only that it was refused.

HIS RULING, 2026-11-08, verbatim: "I accept your recommendation, but with the
caveat above that we must be able to know why a commit was refused, so it can
be repaired. (And in order specifically that you can repair it as needed. stm"

WHAT WAS TRUE BEFORE. The gate's ledger recorded `at`, `seconds`, `exit` and
`head`. A refusal in that history was a fact with no reason attached, so the
only way to learn WHY a past commit was refused was to have been watching when
it happened. Entry B128 is itself an instance: 12 files landed under a message
describing 2 of them because a refusal's cause was not carried forward.

THE REPAIR. Each of the 8 refusal points names itself in `CDSFL_REFUSAL` and
the exit handler writes it as `why`. It can never cost a commit: an unnamed
refusal records the empty string.

THESE TESTS EXECUTE THE HOOK. The ledger test RUNS the gate in a throwaway
repository and reads the line it wrote, because a hook that describes itself
consistently and writes nothing is the failure `execute-do-not-grep` names.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "pre-commit"


@pytest.fixture(scope="module")
def src() -> str:
    return HOOK.read_text(encoding="utf-8")


class TestEveryRefusalPointNamesItself:
    def test_the_variable_is_declared(self, src):
        assert re.search(r'^CDSFL_REFUSAL=""', src, re.M), (
            "CDSFL_REFUSAL is not declared, so an unset variable would be "
            "written into the ledger")

    def test_the_ledger_carries_the_field(self, src):
        assert '"why":"%s"' in src, "the ledger line no longer carries `why`"
        assert "${CDSFL_REFUSAL:-}" in src, (
            "the ledger does not read CDSFL_REFUSAL, or reads it unguarded")

    def test_every_refusal_point_sets_a_reason(self, src):
        """A refusal point that names nothing records an empty cause."""
        lines = src.splitlines()
        unnamed = []
        for i, line in enumerate(lines):
            if line.strip() != "exit 1":
                continue
            window = "\n".join(lines[max(0, i - 3):i])
            if "CDSFL_REFUSAL=" not in window:
                unnamed.append(i + 1)
        assert not unnamed, (
            f"these refusal points do not name themselves, so a commit refused "
            f"there records no cause: lines {unnamed}")

    def test_the_reasons_are_distinct(self, src):
        names = re.findall(r'CDSFL_REFUSAL="([^"]+)"', src)
        assert names, "no refusal names at all"
        dupes = {n for n in names if names.count(n) > 1}
        assert not dupes, (
            f"these causes are used at more than 1 refusal point, so the "
            f"ledger cannot tell them apart: {sorted(dupes)}")

    def test_there_are_at_least_eight(self, src):
        names = re.findall(r'CDSFL_REFUSAL="([^"]+)"', src)
        assert len(names) >= 8, (
            f"only {len(names)} refusal point(s) name themselves; the gate has "
            f"8 that can refuse")


class TestTheLedgerActuallyRecordsIt:
    """Run the real hook in a throwaway repository and read what it wrote."""

    def test_a_refusal_writes_its_cause(self, tmp_path):
        work = tmp_path / "repo"
        work.mkdir()
        subprocess.run(["git", "init", "-q", "."], cwd=work, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=work, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=work, check=True)
        (work / "hooks").mkdir()
        shutil.copy(HOOK, work / "hooks" / "pre-commit")
        os.chmod(work / "hooks" / "pre-commit", 0o755)
        (work / "a.txt").write_text("x")
        subprocess.run(["git", "add", "a.txt"], cwd=work, check=True)

        env = dict(os.environ, CDSFL_HOOK_T0=str(int(__import__("time").time())))
        r = subprocess.run(["sh", "hooks/pre-commit"], cwd=work, env=env,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode != 0, (
            "the gate did not refuse in a repository with no guard files, so "
            "this test cannot observe a refusal")

        ledger = work / ".cdsfl_tmp" / "precommit_durations.jsonl"
        assert ledger.is_file(), "the refusal wrote no ledger line at all"
        rows = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
        assert rows, "the ledger is empty"
        last = rows[-1]
        assert last.get("exit") != 0, last
        assert last.get("why"), (
            f"the refusal recorded no cause, so it cannot be repaired from the "
            f"history: {last}")
        assert re.fullmatch(r"[a-z0-9-]+", last["why"]), last["why"]

    def test_the_recorded_cause_matches_what_was_printed(self, tmp_path):
        """The cause in the ledger must be the refusal that actually fired."""
        work = tmp_path / "repo2"
        work.mkdir()
        subprocess.run(["git", "init", "-q", "."], cwd=work, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=work, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=work, check=True)
        (work / "hooks").mkdir()
        shutil.copy(HOOK, work / "hooks" / "pre-commit")
        os.chmod(work / "hooks" / "pre-commit", 0o755)
        (work / "a.txt").write_text("x")
        subprocess.run(["git", "add", "a.txt"], cwd=work, check=True)
        env = dict(os.environ, CDSFL_HOOK_T0=str(int(__import__("time").time())))
        r = subprocess.run(["sh", "hooks/pre-commit"], cwd=work, env=env,
                           capture_output=True, text=True, timeout=300)
        ledger = work / ".cdsfl_tmp" / "precommit_durations.jsonl"
        why = json.loads(ledger.read_text().splitlines()[-1])["why"]
        # the printed refusal and the recorded cause must agree on the subject
        blob = (r.stdout + r.stderr).lower()
        token = why.split("-")[0]
        assert token in blob, (
            f"the ledger recorded {why!r} but the printed refusal does not "
            f"mention {token!r}:\n{blob[:400]}")
