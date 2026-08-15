"""Pins for the 2026-08-05 repairs to scripts/cdsfl_qc.py and cdsfl_seal_logs.py.

Every defect repaired here had the same shape: a failure that rendered as a
confident success, or as silence. So every test below asserts that a FAILURE
IS REPORTED, not merely that the happy path still works.

  Q1  cdsfl_seal_logs._verify_dir did `ok = chain.verify_chain()` — a tuple,
      always truthy — so the tamper detector could never report tampering. It
      also never re-read the sealed files, and the records are written in
      `hash_only` mode, so a rewritten log verified OK against an untouched
      seal.
  Q2  cdsfl_qc died with an unhandled OSError from check_file_references and
      printed no findings at all for 105 days.
  Q3  check_test_consistency matched a phrasing RECOVERY.md does not use, so
      it silently returned nothing, and it compared a pass count against a
      collected count.
  Q4  check_staleness never compared its two dates.
  Q5  --fix-timestamps was advertised in the usage text and not implemented.

All tests are offline: no subprocess, no network. `git_state`, `test_count`,
`measure_suite` and `subprocess.run` are faked where the code under test would
otherwise shell out.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"


def _load(name: str):
    """Import a scripts/*.py module by path (scripts/ is not a package)."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


qc = _load("cdsfl_qc")
seal = _load("cdsfl_seal_logs")


# ---------------------------------------------------------------------------
# Q1 — the tamper detector must be able to report tampering
# ---------------------------------------------------------------------------


def _sealed_fixture(tmp_path: Path, monkeypatch) -> Path:
    """Build logs/chat with two files and seal it. Returns the sealed dir."""
    logs = tmp_path / "logs"
    chat = logs / "chat"
    chat.mkdir(parents=True)
    (chat / "session.md").write_text("honest log content\n", encoding="utf-8")
    (chat / "record.json").write_text('{"round": 1, "verdict": "CONFIRMED"}',
                                      encoding="utf-8")
    monkeypatch.setattr(seal, "LOGS_ROOT", logs)
    assert seal._seal_dir(chat, dry_run=False, force=False) is not None
    assert (chat / seal.SEAL_FILENAME).exists()
    return chat


def _verify_main(monkeypatch) -> int:
    """Run the script's --verify entry point in-process; return its exit code."""
    monkeypatch.setattr(sys, "argv", ["cdsfl_seal_logs.py", "--verify"])
    return seal.main()


class TestQ1SealTamperDetection:

    def test_verify_chain_returns_a_truthy_tuple_even_when_it_says_false(
        self, tmp_path, monkeypatch
    ):
        """The exact defect: the verdict is the tuple's first element, and the
        tuple itself is always truthy. `bool(verdict)` discards the answer."""
        from bench.verification_chain import VerificationChain

        chat = _sealed_fixture(tmp_path, monkeypatch)
        seal_path = chat / seal.SEAL_FILENAME
        data = json.loads(seal_path.read_text())
        data["records"][0]["sealed_body"]["recorded_by"] = "attacker"
        seal_path.write_text(json.dumps(data, indent=2))

        verdict = VerificationChain.load_json(str(seal_path)).verify_chain()
        assert isinstance(verdict, tuple)
        assert verdict[0] is False
        assert bool(verdict) is True, "a non-empty tuple is always truthy"

        # The repaired verifier must follow verdict[0], not bool(verdict).
        assert seal._verify_dir(chat) is False

    def test_clean_seal_verifies_and_exits_zero(self, tmp_path, monkeypatch, capsys):
        _sealed_fixture(tmp_path, monkeypatch)
        code = _verify_main(monkeypatch)
        out = capsys.readouterr()
        assert code == 0
        assert "OK" in out.out
        assert "TAMPERED" not in (out.out + out.err)

    def test_sealed_chain_tamper_is_reported_and_exit_code_is_nonzero(
        self, tmp_path, monkeypatch, capsys
    ):
        chat = _sealed_fixture(tmp_path, monkeypatch)
        seal_path = chat / seal.SEAL_FILENAME
        data = json.loads(seal_path.read_text())
        data["records"][0]["sealed_body"]["recorded_by"] = "attacker"
        seal_path.write_text(json.dumps(data, indent=2))

        code = _verify_main(monkeypatch)
        combined = capsys.readouterr()
        both = combined.out + combined.err
        assert code != 0
        assert "TAMPERED" in both
        # The diagnostic half of the tuple must survive into the output, so
        # cdsfl_qc's bad_lines filter can carry it into the qc report.
        assert "entry_hash mismatch" in both

    def test_source_file_content_tamper_is_reported(
        self, tmp_path, monkeypatch, capsys
    ):
        """hash_only records mean verify_chain() alone cannot see this: the
        seal is untouched and self-consistent. Only re-reading the file does."""
        chat = _sealed_fixture(tmp_path, monkeypatch)
        (chat / "session.md").write_text("FORGED log content\n", encoding="utf-8")

        code = _verify_main(monkeypatch)
        both = "".join(capsys.readouterr())
        assert code != 0
        assert "TAMPERED" in both
        assert "session.md" in both
        assert "content hash mismatch" in both

    def test_json_source_file_content_tamper_is_reported(
        self, tmp_path, monkeypatch, capsys
    ):
        chat = _sealed_fixture(tmp_path, monkeypatch)
        (chat / "record.json").write_text('{"round": 1, "verdict": "REFUTED"}',
                                          encoding="utf-8")
        code = _verify_main(monkeypatch)
        both = "".join(capsys.readouterr())
        assert code != 0
        assert "TAMPERED" in both
        assert "record.json" in both

    def test_deleted_sealed_file_is_reported(self, tmp_path, monkeypatch, capsys):
        chat = _sealed_fixture(tmp_path, monkeypatch)
        (chat / "session.md").unlink()
        code = _verify_main(monkeypatch)
        both = "".join(capsys.readouterr())
        assert code != 0
        assert "TAMPERED" in both
        assert "missing from disk" in both

    def test_emptied_seal_is_reported(self, tmp_path, monkeypatch, capsys):
        """A seal with its records removed is internally self-consistent —
        verify_chain() calls it 'empty, nothing to verify'. It covers nothing."""
        chat = _sealed_fixture(tmp_path, monkeypatch)
        (chat / seal.SEAL_FILENAME).write_text(
            json.dumps({"schema_version": "1.0", "records": [], "epochs": []}),
            encoding="utf-8",
        )
        code = _verify_main(monkeypatch)
        both = "".join(capsys.readouterr())
        assert code != 0
        assert "TAMPERED" in both
        assert "0 records" in both

    def test_unsealed_directory_is_reported(self, tmp_path, monkeypatch, capsys):
        logs = tmp_path / "logs"
        chat = logs / "chat"
        chat.mkdir(parents=True)
        (chat / "session.md").write_text("unsealed\n", encoding="utf-8")
        monkeypatch.setattr(seal, "LOGS_ROOT", logs)
        code = _verify_main(monkeypatch)
        both = "".join(capsys.readouterr())
        assert code != 0
        assert "UNSEALED" in both

    def test_tamper_diagnostic_reaches_qcs_bad_lines_filter(
        self, tmp_path, monkeypatch, capsys
    ):
        """The two files' contract: cdsfl_qc greps the verifier's output for
        'TAMPERED' / 'UNSEALED' / 'ERROR'. A verdict with no message in the
        output would reach qc as 'seal verification failed' and name nothing."""
        chat = _sealed_fixture(tmp_path, monkeypatch)
        (chat / "session.md").write_text("FORGED log content\n", encoding="utf-8")
        assert seal._verify_dir(chat) is False
        real = capsys.readouterr()

        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "cdsfl_seal_logs.py").write_text("", encoding="utf-8")
        monkeypatch.setattr(
            subprocess, "run",
            lambda *a, **kw: subprocess.CompletedProcess(a, 1, real.out, real.err),
        )
        findings = qc.check_log_seals(tmp_path)
        assert findings[0]["category"] == "STALE"
        assert "TAMPERED" in findings[0]["detail"]
        assert "content hash mismatch" in findings[0]["detail"]
        assert findings[0]["detail"] != "seal verification failed"

    def test_new_file_added_after_sealing_is_not_a_false_positive(
        self, tmp_path, monkeypatch
    ):
        """Directories are sealed once and new logs land in them during normal
        operation. Flagging an addition would manufacture permanent human work."""
        chat = _sealed_fixture(tmp_path, monkeypatch)
        (chat / "later.md").write_text("a log written after sealing\n",
                                       encoding="utf-8")
        assert seal._verify_dir(chat) is True


# ---------------------------------------------------------------------------
# Q2 — one broken check must not take down the whole report
# ---------------------------------------------------------------------------


class TestQ2CheckCrashGuard:

    def test_run_check_turns_a_crash_into_a_loud_finding(self, tmp_path):
        def exploding(_root):
            raise OSError(63, "File name too long", "/some/absurdly/long/path")

        findings = qc.run_check("exploding", exploding, tmp_path)
        assert len(findings) == 1
        assert findings[0]["category"] == "CHECK_FAILED"
        assert "OSError" in findings[0]["detail"]
        assert "File name too long" in findings[0]["detail"]

    def test_run_check_does_not_swallow_a_healthy_result(self, tmp_path):
        def healthy(_root):
            return [{"category": "OK", "file": "x", "detail": "fine"}]

        assert qc.run_check("healthy", healthy, tmp_path) == [
            {"category": "OK", "file": "x", "detail": "fine"}
        ]

    def test_later_checks_still_run_after_an_earlier_one_crashes(self, tmp_path):
        def exploding(_root):
            raise RuntimeError("boom")

        def healthy(_root):
            return [{"category": "OK", "file": "y", "detail": "still ran"}]

        collected = []
        for name, fn in (("a", exploding), ("b", healthy), ("c", healthy)):
            collected.extend(qc.run_check(name, fn, tmp_path))
        assert [f["category"] for f in collected] == ["CHECK_FAILED", "OK", "OK"]

    def test_check_failed_is_counted_as_an_issue_not_hidden(self):
        source = (SCRIPTS / "cdsfl_qc.py").read_text(encoding="utf-8")
        assert "CHECK_FAILED" in source
        assert "issues = failed +" in source, (
            "a crashed check must be counted in the issue total, "
            "not reported as a clean run"
        )

    def test_one_unscannable_document_does_not_abort_the_reference_check(
        self, tmp_path, monkeypatch
    ):
        docs = tmp_path / "resources"
        docs.mkdir()
        (docs / "bad.md").write_text("see `a/b`\n", encoding="utf-8")
        (docs / "good.md").write_text("see `c/d`\n", encoding="utf-8")

        def fake_refs(md_path):
            if md_path.name == "bad.md":
                raise OSError(63, "File name too long", "/x")
            return [{"file": str(md_path), "line": 1, "reference": "c/d"}]

        monkeypatch.setattr(qc, "check_file_references", fake_refs)
        findings = qc.check_broken_references(tmp_path)

        cats = {f["category"] for f in findings}
        assert "CHECK_FAILED" in cats, "the unscannable file must be reported"
        assert "BROKEN_REF" in cats, "the other file must still be scanned"
        failed = [f for f in findings if f["category"] == "CHECK_FAILED"]
        assert failed[0]["file"].endswith("bad.md")

    def test_long_prose_reference_no_longer_crashes_the_run(self, tmp_path):
        """The real 105-day crash, reproduced.

        A backticked prose fragment containing a '/' is treated as a path.
        Its first component lands directly inside the document's own existing
        directory, exceeds NAME_MAX, and Path.exists() raises OSError 63 —
        which killed the process before any finding was printed. Verified to
        raise against the pre-repair code.
        """
        docs = tmp_path / "resources"
        docs.mkdir()
        prose = "alpha beta gamma delta epsilon " * 13 + "text."
        assert len(prose) > 255, "the component must exceed NAME_MAX to reproduce"
        (docs / "long.md").write_text(f"`{prose}/notes`\n", encoding="utf-8")

        findings = qc.check_broken_references(tmp_path)  # must not raise
        assert isinstance(findings, list)
        for f in findings:
            assert f["category"] in {"BROKEN_REF", "CHECK_FAILED"}


# ---------------------------------------------------------------------------
# Q3 — collected vs collected, passed vs passed, and never silence
# ---------------------------------------------------------------------------


def _recovery(tmp_path: Path, body: str) -> Path:
    res = tmp_path / "resources"
    res.mkdir(exist_ok=True)
    (res / "RECOVERY.md").write_text(body, encoding="utf-8")
    return tmp_path


def _fake_counts(monkeypatch, *, collected, passed, skipped=0, failed=0, error=0):
    monkeypatch.setattr(qc, "test_count", lambda: collected)
    monkeypatch.setattr(
        qc, "measure_suite",
        lambda _root: {"passed": passed, "skipped": skipped,
                       "failed": failed, "error": error},
    )


class TestQ3TestCountConsistency:

    CURRENT = (
        "# RECOVERY\n"
        "Last updated: 5 August 2026 14:08 BST\n"
        "    python3 -m pytest bench/tests/ -q --netguard-strict\n"
        "    -> 2099 passed, 3 skipped, 0 failed in 123 s (2102 collected).\n"
    )

    def test_matches_the_phrasing_the_document_actually_uses(
        self, tmp_path, monkeypatch
    ):
        """The old regex was `(\\d+)\\s+tests?\\s+pass`, which matches neither
        '2099 passed' nor '2102 collected' — so the check said nothing."""
        root = _recovery(tmp_path, self.CURRENT)
        _fake_counts(monkeypatch, collected=2102, passed=2099)
        findings = qc.check_test_consistency(root)
        details = " | ".join(f["detail"] for f in findings)
        assert "2102 collected" in details
        assert "2099 passed" in details
        assert not [f for f in findings if f["category"] == "STALE"]

    def test_passed_is_never_compared_against_collected(self, tmp_path, monkeypatch):
        """2102 collected and 2099 passed are different numbers. With both
        matching reality, neither may be reported stale against the other."""
        root = _recovery(tmp_path, self.CURRENT)
        _fake_counts(monkeypatch, collected=2102, passed=2099, skipped=3)
        findings = qc.check_test_consistency(root)
        assert [f["category"] for f in findings if f["file"].endswith("RECOVERY.md")] \
            == ["OK", "OK"]

    def test_stale_collected_count_is_flagged(self, tmp_path, monkeypatch):
        root = _recovery(tmp_path, self.CURRENT)
        _fake_counts(monkeypatch, collected=2556, passed=2099)
        stale = [f for f in qc.check_test_consistency(root)
                 if f["category"] == "STALE"]
        assert len(stale) == 1
        assert "2102 collected, actual collected is 2556" in stale[0]["detail"]

    def test_stale_passed_count_is_flagged(self, tmp_path, monkeypatch):
        root = _recovery(tmp_path, self.CURRENT)
        _fake_counts(monkeypatch, collected=2102, passed=2549)
        stale = [f for f in qc.check_test_consistency(root)
                 if f["category"] == "STALE"]
        assert len(stale) == 1
        assert "2099 passed, actual passed is 2549" in stale[0]["detail"]

    def test_legacy_phrasing_still_recognised(self, tmp_path, monkeypatch):
        root = _recovery(
            tmp_path,
            "# RECOVERY\n1121 tests pass and 1255 tests collected.\n",
        )
        _fake_counts(monkeypatch, collected=1255, passed=1121)
        cats = [f["category"] for f in qc.check_test_consistency(root)
                if f["file"].endswith("RECOVERY.md")]
        assert cats == ["OK", "OK"]

    def test_no_candidate_at_all_emits_a_warning_not_silence(
        self, tmp_path, monkeypatch
    ):
        """A future phrasing change must surface as an issue, not as nothing.

        Asserts the INTENT rather than the exact opening words. The wording was
        changed on 2026-08-12 and this test broke on the prose while the
        behaviour it guards was untouched — which is the wrong thing for a test
        to be sensitive to. What must hold is that the check says out loud that
        it cannot see, so silence is never mistaken for all-clear.
        """
        root = _recovery(tmp_path, "# RECOVERY\nThe suite is entirely green.\n")
        _fake_counts(monkeypatch, collected=2556, passed=2549)
        findings = qc.check_test_consistency(root)
        warns = [f for f in findings if f["category"] == "WARN"]
        assert warns, "a blind check must announce that it is blind"
        assert "blind" in warns[0]["detail"].lower()
        assert "No test-count claim" in warns[0]["detail"]

    def test_a_green_suite_reports_itself_rather_than_staying_silent(
        self, tmp_path, monkeypatch
    ):
        """Silence must never be how a passing suite is communicated.

        Added 2026-08-12. A red suite warned; a green one emitted nothing, so the
        report could not distinguish "the suite passed" from "the suite was never
        measured". That is the failure this script's own staleness check warns
        about in its docstring, and the same shape as a detector that cannot
        report the thing it detects.

        The count also matters on its own: RECOVERY.md deliberately no longer
        carries a bare pass-count, so the number should come from a measurement
        taken on the run rather than from prose that can rot.
        """
        root = _recovery(tmp_path, self.CURRENT)
        _fake_counts(monkeypatch, collected=2556, passed=2549)
        findings = qc.check_test_consistency(root)

        suite = [f for f in findings if f["file"] == "bench/tests/"]
        assert suite, "a green suite produced no finding at all — silence again"
        assert suite[0]["category"] == "OK"
        assert "2549" in suite[0]["detail"], (
            "the OK must carry the measured count, or it is an assurance with "
            "no evidence attached")
        assert "netguard-strict" in suite[0]["detail"], (
            "name the command, so the claim can be reproduced rather than trusted")

    def test_a_red_suite_still_warns(self, tmp_path, monkeypatch):
        """The other side of the branch, so the OK cannot swallow a failure."""
        root = _recovery(tmp_path, self.CURRENT)
        monkeypatch.setattr(qc, "test_count", lambda: 2556)
        monkeypatch.setattr(qc, "measure_suite", lambda root: {
            "passed": 2540, "skipped": 7, "failed": 9, "error": 0})
        findings = qc.check_test_consistency(root)
        suite = [f for f in findings if f["file"] == "bench/tests/"]
        assert suite and suite[0]["category"] == "WARN"
        assert "RED" in suite[0]["detail"]

    def test_a_deliberately_retired_claim_is_not_reported_as_blindness(
        self, tmp_path, monkeypatch
    ):
        """RECOVERY.md carries no bare pass-count ON PURPOSE.

        Added 2026-08-12. The document retracted its earlier counts and replaced
        them with a policy — a claim "must carry a date, a commit, and the
        command" — because bare counts were the defect. Demanding one back would
        push it into the failure it corrected, so a deliberate absence must read
        as OK while a genuine disappearance still reads as WARN. The test above
        pins the other side of that line.
        """
        root = _recovery(tmp_path, (
            "# RECOVERY\n"
            "Every pass-count in the dated session entries below is retracted.\n"
            "Any future claim must carry a date, a commit, and the command.\n"))
        _fake_counts(monkeypatch, collected=2556, passed=2549)
        findings = qc.check_test_consistency(root)
        assert not [f for f in findings if f["category"] == "WARN"], (
            "a documented, deliberate absence is not a blind check")
        oks = [f for f in findings if f["category"] == "OK"]
        assert any("deliberate" in f["detail"].lower() for f in oks), (
            "the OK must say WHY it is fine, or the next reader cannot tell "
            "this apart from the check having been quietly switched off")

    def test_unmeasurable_suite_emits_a_warning(self, tmp_path, monkeypatch):
        root = _recovery(tmp_path, self.CURRENT)
        monkeypatch.setattr(qc, "test_count", lambda: 2102)
        monkeypatch.setattr(qc, "measure_suite", lambda _root: None)
        findings = qc.check_test_consistency(root)
        assert any("Could not measure pass count" in f["detail"]
                   and f["category"] == "WARN" for f in findings)
        # and it must not invent a passed comparison out of nothing
        assert not [f for f in findings if "actual passed" in f["detail"]]

    def test_red_suite_is_reported(self, tmp_path, monkeypatch):
        root = _recovery(tmp_path, self.CURRENT)
        _fake_counts(monkeypatch, collected=2102, passed=2090, failed=9, error=1)
        findings = qc.check_test_consistency(root)
        assert any("Suite is RED" in f["detail"] and f["category"] == "WARN"
                   for f in findings)

    def test_measure_suite_parses_a_real_pytest_summary(self, tmp_path, monkeypatch):
        summary = (
            "bench/tests/test_x.py ....\n"
            "=========== 2549 passed, 7 skipped in 301.44s (0:05:01) ===========\n"
        )
        monkeypatch.setattr(
            subprocess, "run",
            lambda *a, **kw: subprocess.CompletedProcess(a, 0, summary, ""),
        )
        assert qc.measure_suite(tmp_path) == {
            "passed": 2549, "skipped": 7, "failed": 0, "error": 0,
        }

    def test_measure_suite_returns_none_when_the_suite_cannot_run(
        self, tmp_path, monkeypatch
    ):
        def boom(*a, **kw):
            raise OSError("no interpreter")

        monkeypatch.setattr(subprocess, "run", boom)
        assert qc.measure_suite(tmp_path) is None


# ---------------------------------------------------------------------------
# Q4 — the two dates must actually be compared
# ---------------------------------------------------------------------------


def _timestamped_docs(tmp_path: Path, stamp: str) -> Path:
    res = tmp_path / "resources"
    res.mkdir(exist_ok=True)
    for name in ("ONBOARDING.md", "RECOVERY.md"):
        (res / name).write_text(f"# {name}\n\nLast updated: {stamp}\n",
                                encoding="utf-8")
    return tmp_path


class TestQ4Staleness:

    def test_threshold_is_a_named_constant(self):
        assert isinstance(qc.STALENESS_THRESHOLD_DAYS, int)
        assert qc.STALENESS_THRESHOLD_DAYS > 0

    def test_parse_doc_timestamp(self):
        dt = qc.parse_doc_timestamp("5 August 2026 14:08 BST")
        assert (dt.year, dt.month, dt.day, dt.hour, dt.minute) == (2026, 8, 5, 14, 8)
        assert qc.parse_doc_timestamp("not a date") is None

    def test_parse_git_date(self):
        dt = qc.parse_git_date("2026-08-05 14:08:23 +0100")
        assert (dt.year, dt.month, dt.day, dt.hour) == (2026, 8, 5, 14)
        assert qc.parse_git_date("") is None

    def test_stale_document_is_flagged_with_the_threshold_stated(
        self, tmp_path, monkeypatch
    ):
        root = _timestamped_docs(tmp_path, "22 April 2026 09:00 BST")
        monkeypatch.setattr(
            qc, "git_state", lambda: {"last_date": "2026-08-05 14:08:23 +0100"})
        findings = qc.check_staleness(root)
        stale = [f for f in findings if f["category"] == "STALE"]
        assert len(stale) == 2
        assert "trails last commit" in stale[0]["detail"]
        assert f"threshold {qc.STALENESS_THRESHOLD_DAYS} days" in stale[0]["detail"]

    def test_current_document_is_not_flagged(self, tmp_path, monkeypatch):
        root = _timestamped_docs(tmp_path, "5 August 2026 14:08 BST")
        monkeypatch.setattr(
            qc, "git_state", lambda: {"last_date": "2026-08-05 14:08:23 +0100"})
        findings = qc.check_staleness(root)
        assert not [f for f in findings if f["category"] == "STALE"]
        assert all(f["category"] == "OK" for f in findings)

    def test_document_newer_than_the_last_commit_is_not_stale(
        self, tmp_path, monkeypatch
    ):
        root = _timestamped_docs(tmp_path, "5 August 2026 14:08 BST")
        monkeypatch.setattr(
            qc, "git_state", lambda: {"last_date": "2026-06-01 09:00:00 +0100"})
        assert not [f for f in qc.check_staleness(root)
                    if f["category"] == "STALE"]

    def test_missing_stamp_warns_rather_than_saying_nothing(
        self, tmp_path, monkeypatch
    ):
        res = tmp_path / "resources"
        res.mkdir()
        for name in ("ONBOARDING.md", "RECOVERY.md"):
            (res / name).write_text("# no stamp here\n", encoding="utf-8")
        monkeypatch.setattr(
            qc, "git_state", lambda: {"last_date": "2026-08-05 14:08:23 +0100"})
        findings = qc.check_staleness(tmp_path)
        assert len(findings) == 2
        assert all(f["category"] == "WARN" for f in findings)

    def test_unparseable_stamp_warns(self, tmp_path, monkeypatch):
        root = _timestamped_docs(tmp_path, "sometime last spring")
        monkeypatch.setattr(
            qc, "git_state", lambda: {"last_date": "2026-08-05 14:08:23 +0100"})
        findings = qc.check_staleness(root)
        assert all(f["category"] == "WARN" for f in findings)
        assert "staleness not checked" in findings[0]["detail"]

    def test_missing_file_still_reported(self, tmp_path, monkeypatch):
        (tmp_path / "resources").mkdir()
        monkeypatch.setattr(
            qc, "git_state", lambda: {"last_date": "2026-08-05 14:08:23 +0100"})
        findings = qc.check_staleness(tmp_path)
        assert all(f["category"] == "MISSING" for f in findings)


# ---------------------------------------------------------------------------
# Q5 — no advertised capability that does nothing
# ---------------------------------------------------------------------------


class TestQ5FixTimestampsFlag:

    def test_flag_is_no_longer_advertised(self):
        assert "--fix-timestamps" not in (qc.__doc__ or "")
        assert "--fix-timestamps" not in (SCRIPTS / "cdsfl_qc.py").read_text(
            encoding="utf-8")

    def test_flag_is_rejected_loudly_rather_than_silently_ignored(
        self, monkeypatch, capsys
    ):
        monkeypatch.setattr(sys, "argv", ["cdsfl_qc.py", "--fix-timestamps"])
        with pytest.raises(SystemExit) as exc:
            qc.main()
        assert exc.value.code != 0
        assert "unrecognized arguments" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Y1 / Y2 — an unscannable document is a named warning, and the reference
#           filter's suppression is printed rather than assumed
# ---------------------------------------------------------------------------


class TestY1UnreadableDocumentIsNamed:

    def test_unreadable_document_is_a_named_warning_not_silence(self, tmp_path):
        """A document that got no scan must not read as a clean document."""
        docs = tmp_path / "resources"
        docs.mkdir()
        (docs / "unreadable.md").mkdir()          # a directory named *.md
        (docs / "fine.md").write_text("`bench/definitely_gone.py`\n",
                                      encoding="utf-8")

        findings = qc.check_broken_references(tmp_path)

        warns = [f for f in findings if f["category"] == "WARN"]
        assert len(warns) == 1
        assert warns[0]["file"].endswith("unreadable.md")
        assert "NOT scanned" in warns[0]["detail"]
        # and the other document was still scanned
        assert any(f["category"] == "BROKEN_REF" for f in findings)


class TestY2SuppressionIsReported:

    def test_audit_entries_never_leak_into_the_findings_list(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "n.md").write_text("`bench/definitely_gone.py`\n", encoding="utf-8")

        findings = qc.check_broken_references(tmp_path)

        assert {f["category"] for f in findings} == {"BROKEN_REF"}
        assert all("Line " in f["detail"] for f in findings)

    def test_tally_reaches_the_caller_and_names_each_rule(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "n.md").write_text(
            "`/tmp/scratch.json`\n`bench/definitely_gone.py`\n", encoding="utf-8")

        audit: dict = {}
        findings = qc.check_broken_references(tmp_path, audit=audit)

        assert audit["candidates"] == 2
        assert sum(audit["suppressed"].values()) == 1
        assert len([f for f in findings if f["category"] == "BROKEN_REF"]) == 1

    def test_the_tally_is_actually_printed(self, capsys):
        qc.print_reference_audit(
            {"candidates": 100, "suppressed": {"some rule": 90}}, reported=10)

        out = capsys.readouterr().out
        assert "100 candidates examined, 90 suppressed, 10 reported broken" in out
        assert "some rule" in out

    def test_zero_suppression_says_so_rather_than_printing_nothing(self, capsys):
        qc.print_reference_audit({"candidates": 3, "suppressed": {}}, reported=3)

        assert "no candidate was suppressed" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Y3 — "Exp 48" is an experiment number too
# ---------------------------------------------------------------------------


class TestY3ExperimentRegexIsCaseInsensitive:

    def _onboarding(self, tmp_path, text):
        res = tmp_path / "resources"
        res.mkdir(exist_ok=True)
        (res / "ONBOARDING.md").write_text(text, encoding="utf-8")
        return tmp_path

    def test_the_uppercase_only_regex_did_produce_a_false_positive(self):
        """Pin the defect itself, so the repair cannot be undone unnoticed."""
        import re as _re
        text = "EXP 42 landed.\nExp 48 ran.\nExp 54 is planned.\n"
        assert max(int(m.group(1))
                   for m in _re.finditer(r"EXP\s+(\d+)", text)) == 42
        assert max(int(m.group(1))
                   for m in _re.finditer(r"EXP\s+(\d+)", text, _re.IGNORECASE)) == 54

    def test_mixed_case_numbers_are_seen_so_no_stale_finding(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(qc, "latest_experiment", lambda: {"number": 49})
        root = self._onboarding(
            tmp_path, "EXP 42 landed.\nExp 48 ran.\nExp 54 is planned.\n")

        assert qc.check_experiment_consistency(root) == []

    def test_a_genuinely_stale_document_is_still_reported(
        self, tmp_path, monkeypatch
    ):
        """The repair must not blind the check — only stop it lying."""
        monkeypatch.setattr(qc, "latest_experiment", lambda: {"number": 49})
        root = self._onboarding(tmp_path, "Exp 40 was the last write-up.\n")

        findings = qc.check_experiment_consistency(root)

        assert len(findings) == 1
        assert findings[0]["category"] == "STALE"
        assert "40" in findings[0]["detail"] and "49" in findings[0]["detail"]


# ---------------------------------------------------------------------------
# Y4 — a run in which checks crashed is not a successful run
# ---------------------------------------------------------------------------


class TestY4ExitCode:

    def _stub_all_checks(self, monkeypatch, tmp_path, *, crash: bool):
        monkeypatch.setattr(sys, "argv", ["cdsfl_qc.py"])
        monkeypatch.setattr(qc, "repo_root", lambda: tmp_path)
        monkeypatch.setattr(qc, "timestamp_iso", lambda: "2026-08-05T00:00:00+01:00")

        def ok(_root):
            return [{"category": "OK", "file": "x", "detail": "ran"}]

        for name in ("check_staleness", "check_test_consistency",
                     "check_experiment_consistency", "check_glossary",
                     "check_onboard_script", "check_log_seals"):
            monkeypatch.setattr(qc, name, ok)

        if crash:
            def boom(_root, **_kw):
                raise RuntimeError("check exploded")
            monkeypatch.setattr(qc, "check_broken_references", boom)
        else:
            monkeypatch.setattr(qc, "check_broken_references", lambda _r, **_k: [])

    def test_a_clean_run_exits_zero(self, tmp_path, monkeypatch, capsys):
        self._stub_all_checks(monkeypatch, tmp_path, crash=False)

        assert qc.main() == 0
        assert "0 checks crashed" in capsys.readouterr().out

    def test_a_crashed_check_exits_non_zero(self, tmp_path, monkeypatch, capsys):
        self._stub_all_checks(monkeypatch, tmp_path, crash=True)

        code = qc.main()

        out = capsys.readouterr().out
        assert code != 0, (
            "exiting 0 while reporting '1 checks crashed' tells any wrapper "
            "that a partially-failed run succeeded"
        )
        assert "1 checks crashed" in out
        assert "INCOMPLETE" in out

    def test_the_entrypoint_actually_propagates_the_code_to_the_shell(self):
        """A return value main() never passes to sys.exit is not a contract."""
        source = (SCRIPTS / "cdsfl_qc.py").read_text(encoding="utf-8")
        assert "sys.exit(main())" in source

    def test_findings_alone_do_not_gate(self, tmp_path, monkeypatch):
        """Stale docs and broken refs are reported, not enforced — exit 0."""
        self._stub_all_checks(monkeypatch, tmp_path, crash=False)
        monkeypatch.setattr(
            qc, "check_staleness",
            lambda _r: [{"category": "STALE", "file": "d", "detail": "old"}])

        assert qc.main() == 0
