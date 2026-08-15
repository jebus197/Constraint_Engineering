"""Regression pins for the four `scripts/cdsfl_utils.py` repairs (2026-08-05).

Each defect below rendered a failure as a confident success, which is the
governing pattern of the recovery-resource audit:

  U1  latest_experiment() returned None whenever the HIGHEST-numbered
      experiment had written no report (exp53, the halted zero-plant control),
      so `rs` and `sv` printed "(No experiment logs found)" with 37 reports on
      disk.
  U2  git_state() compared every branch against a hardcoded origin/main, and
      _run_git discarded return codes — so a FAILED rev-list produced empty
      stdout, parsed as 0, and rendered as "up to date".
  U3  source_env() partitioned `export KEY=value` on "=" without stripping the
      prefix, naming the variable "export KEY", so cdsfl_onboard reported all
      six API keys MISSING while all six were present.
  U4  read_section() returned "" both for an unreadable file and for an absent
      start marker, so a dead marker was indistinguishable from an empty
      section.

Offline by construction: the git tests replace `_run_git_rc` (the single
subprocess call site) with a fake, so no `git fetch` is attempted. The one
test that does spawn git runs a local, network-free ref lookup.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cdsfl_utils  # noqa: E402
from cdsfl_utils import (  # noqa: E402
    SectionText,
    _run_git_rc,
    git_state,
    latest_experiment,
    read_section,
    source_env,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _write_report(logs_dir: Path, dirname: str, payload: dict) -> Path:
    d = logs_dir / dirname
    d.mkdir(parents=True)
    (d / f"{dirname}_report.json").write_text(json.dumps(payload))
    return d


def _fake_repo(monkeypatch, tmp_path: Path) -> Path:
    """Point cdsfl_utils at a throwaway repo root and return bench/logs."""
    logs = tmp_path / "bench" / "logs"
    logs.mkdir(parents=True)
    monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)
    return logs


# ─────────────────────────────────────────────────────────────────────────────
# U1 — latest_experiment() falls back past a report-less top experiment
# ─────────────────────────────────────────────────────────────────────────────

class TestU1LatestExperimentFallback:

    def test_falls_back_when_highest_number_has_no_report(
        self, tmp_path, monkeypatch, capsys
    ):
        """THE DEFECT: exp53 (halted control, no report) hid exp49."""
        logs = _fake_repo(monkeypatch, tmp_path)
        (logs / "exp53_control_zero_live_20260801T005649Z").mkdir()  # no report
        _write_report(
            logs, "exp49_engineering_exam_live",
            {"experiment": "exp49_engineering_exam_live", "total_rounds": 7},
        )

        exp = latest_experiment()

        assert exp is not None, "report-less exp53 must not hide exp49"
        assert exp["number"] == 49
        assert exp["name"] == "exp49_engineering_exam_live"

    def test_skip_is_carried_in_the_returned_data(self, tmp_path, monkeypatch):
        """The caller must be able to say WHY 53 is not being shown."""
        logs = _fake_repo(monkeypatch, tmp_path)
        (logs / "exp53_control_zero_live").mkdir()
        (logs / "exp51_no_report").mkdir()
        _write_report(logs, "exp49_engineering_exam_live", {"experiment": "exp49"})

        exp = latest_experiment()

        assert exp["skipped_higher"] == [53, 51]

    def test_skip_is_announced_on_stderr(self, tmp_path, monkeypatch, capsys):
        logs = _fake_repo(monkeypatch, tmp_path)
        (logs / "exp53_control_zero_live").mkdir()
        _write_report(logs, "exp49_engineering", {"experiment": "exp49"})

        latest_experiment()

        err = capsys.readouterr().err
        assert "exp53" in err
        assert "no parseable" in err

    def test_no_skip_reported_when_top_experiment_has_a_report(
        self, tmp_path, monkeypatch, capsys
    ):
        logs = _fake_repo(monkeypatch, tmp_path)
        _write_report(logs, "exp53_control_zero_live", {"experiment": "exp53"})
        _write_report(logs, "exp49_engineering", {"experiment": "exp49"})

        exp = latest_experiment()

        assert exp["number"] == 53
        assert exp["skipped_higher"] == []
        assert "exp53" not in capsys.readouterr().err

    def test_mtime_ordering_preserved_within_one_number(self, tmp_path, monkeypatch):
        """Two runs of the same experiment: the newest still wins."""
        logs = _fake_repo(monkeypatch, tmp_path)
        older = _write_report(logs, "exp42_composer_older", {"experiment": "older"})
        newer = _write_report(logs, "exp42_composer_newer", {"experiment": "newer"})
        os.utime(older, (1_600_000_000, 1_600_000_000))
        os.utime(newer, (1_700_000_000, 1_700_000_000))

        assert latest_experiment()["name"] == "newer"

    def test_unparseable_report_is_skipped_like_a_missing_one(
        self, tmp_path, monkeypatch
    ):
        logs = _fake_repo(monkeypatch, tmp_path)
        bad = logs / "exp53_control_zero_live"
        bad.mkdir()
        (bad / "exp53_report.json").write_text("{ this is not json")
        _write_report(logs, "exp49_engineering", {"experiment": "exp49"})

        exp = latest_experiment()

        assert exp["number"] == 49
        assert exp["skipped_higher"] == [53]

    def test_returns_none_when_nothing_is_parseable(self, tmp_path, monkeypatch):
        logs = _fake_repo(monkeypatch, tmp_path)
        (logs / "exp53_control_zero_live").mkdir()

        assert latest_experiment() is None

    def test_real_repo_reports_an_experiment(self):
        """The founder-visible symptom: `rs` said "(No experiment logs found)"."""
        logs = REPO_ROOT / "bench" / "logs"
        if not list(logs.glob("exp*/exp*_report.json")):
            pytest.skip("no experiment reports on disk in this checkout")

        exp = latest_experiment()

        assert exp is not None
        assert exp["number"] > 0


# ─────────────────────────────────────────────────────────────────────────────
# U2 — git_state() compares against the branch's own upstream, and a failed
#      rev-list is reported as unknown, never as "up to date"
# ─────────────────────────────────────────────────────────────────────────────

def _git_fake(upstream: tuple[int, str], revlist: tuple[int, str]):
    """Stand in for _run_git_rc. _run_git delegates to it, so this replaces
    EVERY git subprocess in git_state — including the fetch."""
    def fake(*args: str, cwd=None) -> tuple[int, str]:
        if args[0] == "rev-parse":
            return upstream
        if args[0] == "rev-list":
            return revlist
        if args[0] == "branch":
            return (0, "exp39-experimental")
        if args[0] == "log":
            return (0, "abc1234 a commit message")
        return (0, "")
    return fake


class TestU2GitState:

    def test_compares_against_this_branchs_own_upstream(self, monkeypatch):
        """THE DEFECT: exp39-experimental was compared to origin/main and
        reported "diverged (ahead 98, behind 1)" while level with upstream."""
        monkeypatch.setattr(
            cdsfl_utils, "_run_git_rc",
            _git_fake((0, "origin/exp39-experimental"), (0, "0\t0")),
        )

        sync = git_state()["remote_sync"]

        assert sync == "up to date with origin/exp39-experimental"
        assert "origin/main" not in sync

    def test_failed_rev_list_is_unknown_not_up_to_date(self, monkeypatch):
        """A false ALL-CLEAR is worse than a false alarm."""
        monkeypatch.setattr(
            cdsfl_utils, "_run_git_rc",
            _git_fake((0, "origin/exp39-experimental"), (128, "")),
        )

        sync = git_state()["remote_sync"]

        assert sync.startswith("unknown")
        assert "up to date" not in sync
        assert "origin/exp39-experimental" in sync

    def test_garbled_rev_list_output_is_unknown(self, monkeypatch):
        monkeypatch.setattr(
            cdsfl_utils, "_run_git_rc",
            _git_fake((0, "origin/exp39-experimental"), (0, "not-a-count")),
        )

        assert git_state()["remote_sync"].startswith("unknown")

    def test_no_upstream_falls_back_to_origin_main_and_names_it(self, monkeypatch):
        monkeypatch.setattr(
            cdsfl_utils, "_run_git_rc",
            _git_fake((128, ""), (0, "0\t0")),
        )

        sync = git_state()["remote_sync"]

        assert "origin/main" in sync
        assert "no upstream configured" in sync

    def test_ahead_behind_and_diverged_name_the_ref(self, monkeypatch):
        ref = "origin/exp39-experimental"
        cases = {
            (0, "0\t3"): f"ahead of {ref} by 3",
            (0, "2\t0"): f"behind {ref} by 2",
            (0, "1\t4"): f"diverged from {ref} (ahead 4, behind 1)",
        }
        for revlist, expected in cases.items():
            monkeypatch.setattr(
                cdsfl_utils, "_run_git_rc", _git_fake((0, ref), revlist)
            )
            assert git_state()["remote_sync"] == expected

    def test_run_git_rc_reports_a_nonzero_return_code(self, tmp_path):
        """The plumbing itself: a failing git command must not look like ""."""
        rc, out = _run_git_rc(
            "rev-list", "--count", "cdsfl-no-such-ref-2026", cwd=tmp_path
        )

        assert rc != 0
        assert out == ""


# ─────────────────────────────────────────────────────────────────────────────
# U3 — source_env() strips the `export ` prefix
# ─────────────────────────────────────────────────────────────────────────────

class TestU3SourceEnv:
    """No real key material is read or written here: these tests point
    cdsfl_utils at a throwaway repo root with a synthetic .env, and every
    assertion is on variable NAMES and synthetic placeholder values."""

    def _isolated_env(self, monkeypatch) -> dict:
        fake_env: dict[str, str] = {}
        monkeypatch.setattr(os, "environ", fake_env)
        return fake_env

    def test_export_prefixed_keys_resolve_under_their_real_names(
        self, tmp_path, monkeypatch
    ):
        """THE DEFECT: the variable was named "export OPENROUTER_API_KEY", so
        cdsfl_onboard reported all six keys MISSING while all six were set."""
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)
        (tmp_path / ".env").write_text(
            "# a comment\n"
            "export CDSFL_TEST_ALPHA=placeholder-not-a-key\n"
            "CDSFL_TEST_BETA=placeholder-not-a-key\n"
        )
        env = self._isolated_env(monkeypatch)

        source_env()

        assert env.get("CDSFL_TEST_ALPHA") == "placeholder-not-a-key"
        assert env.get("CDSFL_TEST_BETA") == "placeholder-not-a-key"

    def test_no_variable_is_named_with_the_export_prefix(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)
        (tmp_path / ".env").write_text(
            "export CDSFL_TEST_ALPHA=placeholder-not-a-key\n"
        )
        env = self._isolated_env(monkeypatch)

        source_env()

        assert [n for n in env if n.startswith("export ")] == []

    def test_matches_runner_core_on_the_same_line(self, tmp_path, monkeypatch):
        """bench/runner_core.py is the reference implementation of this parse."""
        line = "export CDSFL_TEST_GAMMA=placeholder-not-a-key"
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)
        (tmp_path / ".env").write_text(line + "\n")
        env = self._isolated_env(monkeypatch)

        source_env()

        # runner_core: strip "export ", partition on "=", strip both halves.
        stripped = line[7:]
        key, _, val = stripped.partition("=")
        assert env.get(key.strip()) == val.strip()


# ─────────────────────────────────────────────────────────────────────────────
# U4 — read_section() distinguishes an unreadable file from a dead marker
# ─────────────────────────────────────────────────────────────────────────────

class TestU4ReadSection:

    def test_present_marker_reads_the_section(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("intro\n## Current State\nbody line\n## Next\ntail\n")

        out = read_section(f, "## Current State", "\n## ")

        assert out == "body line"
        assert out.status == "ok"

    def test_missing_marker_and_unreadable_file_are_distinguishable(self, tmp_path):
        """THE DEFECT: both returned a bare "", so a dead marker in
        resources/RECOVERY.md went unnoticed for 113 days."""
        f = tmp_path / "doc.md"
        f.write_text("intro only\n")

        missing = read_section(f, "NEXT STEPS:")
        unreadable = read_section(tmp_path / "absent.md", "NEXT STEPS:")

        assert missing == "" and unreadable == ""
        assert missing.status == "marker-missing"
        assert unreadable.status == "unreadable"
        assert missing.status != unreadable.status

    def test_missing_marker_is_loud_and_names_file_and_marker(
        self, tmp_path, capsys
    ):
        f = tmp_path / "RECOVERY.md"
        f.write_text("**IMMEDIATE NEXT STEPS (consult HIL before proceeding):**\n")

        read_section(f, "NEXT STEPS:", "\nARCHITECTURAL GAPS")

        err = capsys.readouterr().err
        assert "NEXT STEPS:" in err
        assert "RECOVERY.md" in err
        assert "MARKER NOT FOUND" in err

    def test_unreadable_file_is_loud(self, tmp_path, capsys):
        read_section(tmp_path / "absent.md", "## Current State")

        err = capsys.readouterr().err
        assert "absent.md" in err
        assert "CANNOT READ" in err

    def test_result_is_still_a_plain_string_for_existing_callers(self, tmp_path):
        """Callers do `if section:`, `.splitlines()`, `.find()`, slicing."""
        f = tmp_path / "doc.md"
        f.write_text("## S\nalpha\nbeta\n")

        out = read_section(f, "## S")
        empty = read_section(f, "## MISSING")

        assert isinstance(out, str) and isinstance(out, SectionText)
        assert bool(out) is True
        assert bool(empty) is False
        assert out.splitlines() == ["alpha", "beta"]
        assert out.find("beta") == 6
        assert out[:5] == "alpha"

    def test_end_marker_absent_reads_to_end_of_file(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("## S\nalpha\nbeta\n")

        assert read_section(f, "## S", "\n## ") == "alpha\nbeta"


# ─────────────────────────────────────────────────────────────────────────────
# Y1 / Y2 — the reference checker (2026-08-05)
#
#   Y1  check_file_references called Path.exists() on backtick spans pulled
#       from prose. An unbalanced backtick yields a several-hundred-character
#       "path"; its first component exceeds NAME_MAX (255) and exists() raises
#       OSError 63 instead of returning False, so two documents got NO
#       reference scan at all. The cause is fixed with a length guard placed
#       BEFORE the exists() call. An unreadable document is no longer silent.
#
#   Y2  183 BROKEN_REF findings of which ~10 were real. A report that buries
#       10 real defects under 173 false ones is functionally the crash it
#       replaced. The checker now understands `path:line`, `path:line-range`,
#       `path::symbol`, the registry prefix, and the forms that are not repo
#       paths at all — and it REPORTS every suppression, per rule, so an
#       over-broad rule added later is visible rather than invisible.
#
# The governing risk of Y2 is that a filter hides a real defect. The test that
# matters most below is test_dead_references_survive_every_filter.
# ─────────────────────────────────────────────────────────────────────────────


def _ref_repo(monkeypatch, tmp_path: Path) -> Path:
    """A throwaway repo with one real module and one real registry file."""
    (tmp_path / "bench").mkdir()
    (tmp_path / "bench" / "real.py").write_text("x = 1\n", encoding="utf-8")
    registry = tmp_path / "bench" / "cdsfl_registry" / "domains" / "immune"
    registry.mkdir(parents=True)
    (registry / "biology.toml").write_text("k = 'v'\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)
    return tmp_path


def _scan(root: Path, body: str):
    """Write body to docs/note.md, scan it, return (broken, audit)."""
    doc = root / "docs" / "note.md"
    doc.write_text(body, encoding="utf-8")
    entries = cdsfl_utils.check_file_references(doc)
    audit: dict = {}
    cdsfl_utils.merge_reference_audit(entries, audit)
    broken = [e for e in entries if cdsfl_utils.AUDIT_KEY not in e]
    return broken, audit


class TestY1LengthGuard:

    def test_an_overlong_component_really_does_raise_without_the_guard(
        self, tmp_path
    ):
        """The guard is load-bearing, not decorative — prove the crash exists.

        This is the exact call the checker used to make. If this ever stops
        raising, the guard's justification has changed and the rest of this
        class needs re-reading.
        """
        component = "alpha beta gamma delta epsilon " * 13
        assert len(component) > cdsfl_utils.MAX_REFERENCE_LEN
        with pytest.raises(OSError):
            (tmp_path / component / "notes").exists()

    def test_overlong_span_is_suppressed_and_the_scan_completes(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        prose = "alpha beta gamma delta epsilon " * 13
        assert len(prose) > cdsfl_utils.MAX_REFERENCE_LEN

        broken, audit = _scan(root, f"`{prose}/notes`\n`bench/gone.py`\n")

        assert audit["suppressed"][cdsfl_utils.SUPPRESS_OVERLENGTH] == 1
        # The rest of the document was still scanned — that is the whole point.
        assert [b["reference"] for b in broken] == ["bench/gone.py"]

    def test_unreadable_document_reports_scan_failed_never_zero_broken(
        self, tmp_path, monkeypatch, capsys
    ):
        _ref_repo(monkeypatch, tmp_path)
        absent = tmp_path / "docs" / "not_there.md"

        entries = cdsfl_utils.check_file_references(absent)

        failures = [e for e in entries if e.get("scan_failed")]
        assert len(failures) == 1, (
            "an unreadable document must announce itself; returning [] would "
            "read as 'this file has no broken references'"
        )
        assert "not_there.md" in failures[0]["file"]
        assert "CANNOT READ" in capsys.readouterr().err


class TestY2ReferenceFilter:

    def test_dead_references_survive_every_filter(self, tmp_path, monkeypatch):
        """The suppression rules must not swallow a genuinely dead path.

        Every line below names a file that does NOT exist, dressed in each
        form the new normalisations understand. All five must still be
        reported. If a future rule is written too broadly, this fails.
        """
        root = _ref_repo(monkeypatch, tmp_path)
        broken, _ = _scan(root, "\n".join([
            "`bench/gone.py`",
            "`bench/gone.py:42`",
            "`bench/gone.py:10-20`",
            "`bench/gone.py::Klass`",
            "`domains/immune/absent.toml`",
        ]) + "\n")

        assert [b["reference"] for b in broken] == [
            "bench/gone.py",
            "bench/gone.py:42",
            "bench/gone.py:10-20",
            "bench/gone.py::Klass",
            "domains/immune/absent.toml",
        ]

    def test_line_and_range_suffixes_resolve_when_the_file_exists(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        broken, audit = _scan(
            root, "`bench/real.py:42`\n`bench/real.py:10-20`\n")

        assert broken == []
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_LINE] == 2

    def test_symbol_suffix_resolves_when_the_file_exists(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        broken, audit = _scan(
            root, "`bench/real.py::Klass`\n`bench/real.py::Klass::test_it`\n")

        assert broken == []
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_SYMBOL] == 2

    def test_suppression_label_admits_what_is_not_checked(self):
        """The label must not claim a property the checker never verified."""
        assert "NOT checked" in cdsfl_utils.SUPPRESS_SYMBOL
        assert "NOT checked" in cdsfl_utils.SUPPRESS_LINE
        assert "NOT checked" in cdsfl_utils.SUPPRESS_MEMORY

    def test_registry_prefix_resolves(self, tmp_path, monkeypatch):
        root = _ref_repo(monkeypatch, tmp_path)
        broken, audit = _scan(root, "`domains/immune/biology.toml`\n")

        assert broken == []
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_REGISTRY] == 1

    def test_out_of_repo_and_template_forms_are_skipped_by_named_rule(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        broken, audit = _scan(root, "\n".join([
            "`/tmp/exp40_scratch.json`",
            "`~/Desktop/CDSFL_tts/note.txt`",
            "`memory/ce_state.md`",
            "`experimental_notes/<Name>_<DATE>.md`",
        ]) + "\n")

        assert broken == []
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_TMP] == 1
        assert (audit["suppressed"].get(cdsfl_utils.SUPPRESS_HOME, 0)
                + audit["suppressed"].get(cdsfl_utils.SUPPRESS_HOME_ABSENT, 0)) == 1
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_MEMORY] == 1
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_TEMPLATE] == 1

    def test_prose_span_and_command_line_are_skipped_by_named_rule(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        broken, audit = _scan(root, "\n".join([
            "text ` see docs/whatever.md and ` more text",
            "`bench/real.py --resume`",
        ]) + "\n")

        assert broken == []
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_PROSE] == 1
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_COMMAND] == 1

    def test_a_leading_space_is_the_only_thing_the_prose_rule_keys_on(
        self, tmp_path, monkeypatch
    ):
        """Narrowness check: the same span without the space is still checked."""
        root = _ref_repo(monkeypatch, tmp_path)
        broken, _ = _scan(root, "`docs/whatever.md`\n")
        assert [b["reference"] for b in broken] == ["docs/whatever.md"]

    def test_audit_entry_is_always_present_and_counts_candidates(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        doc = root / "docs" / "note.md"
        doc.write_text("`bench/real.py`\n`bench/gone.py`\n`/tmp/x.json`\n",
                       encoding="utf-8")

        entries = cdsfl_utils.check_file_references(doc)
        audits = [e for e in entries if cdsfl_utils.AUDIT_KEY in e]

        assert len(audits) == 1
        assert audits[0][cdsfl_utils.AUDIT_KEY]["candidates"] == 3

    def test_audit_survives_a_document_with_nothing_to_report(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        broken, audit = _scan(root, "no references here at all\n")

        assert broken == []
        assert audit == {"candidates": 0, "suppressed": {}}


class TestY2HomePathSuppressionStaysInformative:
    """The ~ rule is the only suppression that can drop a real absence.

    Suppressing both cases under one label would hide, invisibly, the only
    home-path candidates that carry information. The tally must separate them.
    """

    def test_a_resolving_and_an_absent_home_path_are_counted_apart(
        self, tmp_path, monkeypatch
    ):
        root = _ref_repo(monkeypatch, tmp_path)
        home = tmp_path / "home"
        (home / "Desktop").mkdir(parents=True)
        (home / "Desktop" / "there.txt").write_text("x\n", encoding="utf-8")
        monkeypatch.setenv("HOME", str(home))

        broken, audit = _scan(
            root, "`~/Desktop/there.txt`\n`~/Desktop/gone.txt`\n")

        assert broken == [], "a ~ path is never reported as a repo-broken ref"
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_HOME] == 1
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_HOME_ABSENT] == 1

    def test_the_absent_label_admits_the_file_may_be_dead(self):
        assert "DOES NOT resolve" in cdsfl_utils.SUPPRESS_HOME_ABSENT
        assert "may be dead" in cdsfl_utils.SUPPRESS_HOME_ABSENT
