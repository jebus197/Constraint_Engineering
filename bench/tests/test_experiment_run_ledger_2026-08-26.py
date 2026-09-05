"""The experiment run ledger is DERIVED from artefacts, and this proves it discriminates.

FOUNDER INSTRUCTION 2026-08-25: renumber the experiments by actual run order.

MEASURING FIRST REFUTED THE PREMISE. Sorted by start time, the experiment number
is already perfectly monotonic across all 44 non-empty run directories -- zero
violations. The only apparent violations are three EMPTY directories written on
2026-08-07 by aborted re-invocations of exp35 and exp36, which are not runs. A
renumber by run order would change nothing, and it would cost a great deal: the
run directory name and the report filename both embed the experiment number, so
renumbering means renaming 56 directories and severing every doc reference to
them.

Two real defects sit underneath the request, and the ledger surfaces both:

  HOLE 1  Four numbers in the exp29-exp55 span never ran. exp50/51/52 have
          configs and no directory; exp54 has no config either.
  HOLE 2  Status lives in completion_signal.json AND in the run report, and
          they disagree. 20 of 31 signals carry an EMPTY reason; in 7 of those
          the report names an outcome the signal has lost.

WHAT THIS FILE ASSERTS. Not that the script runs. That its answers CHANGE with
the input -- a monotonic sequence and a non-monotonic one must not produce the
same verdict, and a ledger that no longer matches bench/logs must fail.
"""
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/experiment_run_ledger.py"
LEDGER = REPO / "experimental_notes/EXPERIMENT_RUN_LEDGER.md"

sys.path.insert(0, str(REPO / "scripts"))
import experiment_run_ledger as erl  # noqa: E402


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=REPO, timeout=120)


class TestMonotonicityDiscriminates:
    """The load-bearing claim. If this cannot fail, it is not evidence."""

    def test_known_good_an_ordered_sequence_is_monotonic(self):
        data = {"runs": [
            {"exp": 29, "started": "20260404T193100Z", "aborted": False},
            {"exp": 30, "started": "20260404T235100Z", "aborted": False},
            {"exp": 42, "started": "20260602T230000Z", "aborted": False},
        ]}
        m = erl.monotonicity(data)
        assert m["monotonic"] is True and m["violations"] == []
        assert m["checked"] == 3

    def test_known_bad_an_out_of_order_run_is_caught(self):
        """KNOWN-BAD: exp30 running after exp42 must NOT read as ordered."""
        data = {"runs": [
            {"exp": 29, "started": "20260404T193100Z", "aborted": False},
            {"exp": 42, "started": "20260602T230000Z", "aborted": False},
            {"exp": 30, "started": "20260701T000000Z", "aborted": False},
        ]}
        m = erl.monotonicity(data)
        assert m["monotonic"] is False, "an out-of-order run reported as monotonic"
        assert m["violations"][0]["exp"] == 30 and m["violations"][0]["after"] == 42

    def test_aborted_empty_directories_are_excluded(self):
        """The three 2026-08-07 empty directories are aborted invocations, not
        runs. Counting them makes a correctly ordered project look disordered."""
        data = {"runs": [
            {"exp": 53, "started": "20260801T005600Z", "aborted": False},
            {"exp": 36, "started": "20260807T043201Z", "aborted": True},
            {"exp": 55, "started": "20260823T144624Z", "aborted": False},
        ]}
        assert erl.monotonicity(data)["monotonic"] is True
        data["runs"][1]["aborted"] = False
        assert erl.monotonicity(data)["monotonic"] is False, (
            "with the empty directory counted as a run it MUST report a violation; "
            "otherwise the exclusion is doing no work"
        )


class TestSignalReportDisagreement:
    def test_a_signal_saying_INCOMPLETE_over_a_named_outcome_is_flagged(self):
        data = {"runs": [{"exp": 55, "signal_status": "INCOMPLETE", "signal_reason": "",
                          "report_converged_at": None,
                          "report_reason": "HALTED_IRREDUCIBLE_QUEUE_ALARM", "aborted": False}]}
        assert len(erl.disagreements(data)) == 1, (
            "a run whose report names an outcome its signal lost was not flagged"
        )

    def test_agreement_is_not_flagged(self):
        """KNOWN-GOOD: a CONVERGED signal with a matching report is not a defect."""
        data = {"runs": [{"exp": 44, "signal_status": "CONVERGED", "signal_reason": "STATE_CONVERGED",
                          "report_converged_at": 12, "report_reason": "STATE_CONVERGED",
                          "aborted": False}]}
        assert erl.disagreements(data) == []

    def test_an_empty_signal_with_an_empty_report_is_not_flagged(self):
        """Nothing recorded anywhere is a different defect from two artefacts
        disagreeing, and conflating them inflates the count."""
        data = {"runs": [{"exp": 43, "signal_status": "INCOMPLETE", "signal_reason": "",
                          "report_converged_at": None, "report_reason": "", "aborted": False}]}
        assert erl.disagreements(data) == []


class TestAgainstTheRealArtefacts:
    def test_the_committed_ledger_matches_bench_logs(self):
        """Drift guard: the ledger is generated, so a hand edit or a new run
        must make this fail rather than sit unnoticed."""
        r = _run("--check")
        assert r.returncode == 0, (
            f"ledger no longer matches the artefacts:\n{r.stdout}\n{r.stderr}"
        )

    def test_the_real_tree_is_monotonic_and_says_so(self):
        r = _run("--json")
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout)
        assert d["monotonicity"]["monotonic"] is True, (
            f"run order is no longer monotonic: {d['monotonicity']['violations']}. "
            "If a new experiment ran out of order this is a real finding, not a "
            "test to relax."
        )
        assert d["monotonicity"]["checked"] >= 44

    def test_the_gap_set_includes_exp54_which_has_no_config(self):
        """exp54 has neither a config nor a run. A config-only scan misses it,
        which is how a sentence reading 'four numbers' came to sit above a list
        of three while this script was being written."""
        d = json.loads(_run("--json").stdout)
        assert 54 in d["gap_numbers"], "exp54 is absent from the gap set"
        assert 54 in d["gap_no_config"]
        # 56 joined the set on 2026-09-05 when the Exp 56 arms were written:
        # 3 configurations, no runs yet, which is exactly what "configured but
        # never ran" means. A planned experiment legitimately lands here, so the
        # assertion names the set rather than freezing a moment. What this test
        # is actually for is the line above it -- exp54 has NEITHER a config nor
        # a run and a config-only scan misses it -- and that part is unchanged.
        assert set(d["configured_never_ran"]) == {50, 51, 52, 56}

    def test_exp53_ran_and_is_not_dropped(self):
        """Standing directive: exp53 is the zero-plant control and MUST NOT be
        dropped. It must therefore appear as a run that happened."""
        d = json.loads(_run("--json").stdout)
        assert 53 in d["ran"], "exp53 has vanished from the run set"

    def test_the_ledger_names_the_disagreement_count(self):
        text = LEDGER.read_text(encoding="utf-8")
        assert "Hole 2" in text and "EMPTY reason" in text
        # DERIVED, not typed. The previous form asserted a literal line
        # number that was wrong by 1,068 lines and agreed with the generator's
        # identical typo, so the pair verified each other and never the source
        # (2026-09-01).
        sys.path.insert(0, str(REPO / "scripts"))
        from experiment_run_ledger import _gamma_alt_comment_line
        assert f"reference_runner_v3.py:{_gamma_alt_comment_line()}" in text, (
            "the ledger no longer cites where the runner's own source names "
            "this defect"
        )


def test_help_costs_nothing():
    r = _run("--help")
    assert r.returncode == 0 and "run ledger" in r.stdout.lower()


class TestTheDriftGuardCanActuallyFail:
    """FOUND BY FALSIFYING THIS FILE, 2026-08-26. Five deliberate breaks were
    introduced to check these tests can fail. Four were caught. The fifth --
    replacing the ledger comparison with `if True:` so --check always exits 0 --
    passed all twelve tests, because --check was only ever run against a ledger
    that already matched. A guard exercised only on the passing case is not a
    guard. These run it on the failing case.
    """

    def _check_against(self, monkeypatch, tmp_path, body):
        target = tmp_path / "LEDGER.md"
        if body is not None:
            target.write_text(body, encoding="utf-8")
        monkeypatch.setattr(erl, "LEDGER", target)
        monkeypatch.setattr(sys, "argv", ["experiment_run_ledger.py", "--check"])
        return erl.main()

    def test_known_good_an_identical_ledger_passes(self, monkeypatch, tmp_path):
        fresh = erl.render(erl.collect())
        assert self._check_against(monkeypatch, tmp_path, fresh) == 0

    def test_known_bad_a_single_altered_character_fails(self, monkeypatch, tmp_path):
        """A hand edit to a generated file must be caught, not absorbed."""
        drifted = erl.render(erl.collect()).replace("monotonic", "NOT monotonic", 1)
        assert self._check_against(monkeypatch, tmp_path, drifted) == 1, (
            "an edited ledger passed the drift check; the guard does nothing"
        )

    def test_known_bad_a_truncated_ledger_fails(self, monkeypatch, tmp_path):
        truncated = "\n".join(erl.render(erl.collect()).splitlines()[:10]) + "\n"
        assert self._check_against(monkeypatch, tmp_path, truncated) == 1

    def test_known_bad_a_missing_ledger_fails(self, monkeypatch, tmp_path):
        assert self._check_against(monkeypatch, tmp_path, None) == 1, (
            "a ledger that does not exist passed the check"
        )

    def test_the_three_answers_differ(self, monkeypatch, tmp_path):
        fresh = erl.render(erl.collect())
        good = self._check_against(monkeypatch, tmp_path, fresh)
        bad = self._check_against(monkeypatch, tmp_path, fresh.replace("|", "!", 1))
        gone = self._check_against(monkeypatch, tmp_path, None)
        assert (good, bad, gone) == (0, 1, 1), (
            f"drift check does not discriminate: {(good, bad, gone)}"
        )
