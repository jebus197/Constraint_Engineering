"""Panel review of task A23, 2026-09-17: the guard it shipped was RED at HEAD.

A23 is marked DONE and names
`bench/tests/test_recovery_session_state_is_current_2026-09-11.py` as its
evidence. Two defects were found by running it, not by reading it, and this file
pins both repairs and their boundaries.

1. UNSATISFIABLE BY HONEST PROSE. `TestASuiteFigureNamesItsProducer` recognised
   a producer only in the form `scripts/<name>.py`. The full suite has no such
   producer: what produces "7,493 passed" is a pytest invocation. So the newest
   SESSION STATE block -- which reported the suite green at `a2999f1` -- was an
   offender, and the only routes to green were to cite a script that did not
   produce the number, or to stop reporting the suite. The predicate now also
   accepts a COMPLETE pytest command, and `resources/RECOVERY.md` names one.
   `scripts/suite_figure_producers_2026-09-17.py` is the measurement behind
   that: the command form is the one the record already uses.

2. A FABRICATED FAILURE OUTSIDE A CHECKOUT.
   `test_it_names_a_commit_reachable_from_head` read `returncode == 0` from
   `git merge-base --is-ancestor`, collapsing exit 1 (not an ancestor) and exit
   128 (no repository) into "not reachable". In any `.git`-less copy (a
   `git archive` export, a ZIP), and in every panel sandbox --
   `panel_sandbox.build()` deletes `.git` -- it therefore asserted "the block
   describes a tree that is not this one" on no evidence. A `git clone` keeps
   `.git` and was never affected.
   Same defect panel round 12 found in `overstated_entries_2026-09-11.py`.

THE WIDENING IS NOT A LOOSENING AND THE SKIP IS NOT A HOLE. Both negative
controls below exist to say so: a bare mention of the word "pytest" is still not
a producer, and a bogus sha INSIDE a real checkout still fails.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GUARD = REPO / "bench" / "tests" / "test_recovery_session_state_is_current_2026-09-11.py"


def _guard():
    """Import the module under review. EXECUTE, DO NOT GREP: every assertion
    here calls its real predicates rather than restating its patterns."""
    spec = importlib.util.spec_from_file_location("a23_guard_under_review", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTheProducerPredicateIsWiderAndStillSharp:
    def test_a_complete_pytest_command_is_a_producer(self):
        g = _guard()
        assert g._NAMES_A_PRODUCER.search(
            "Suite 7,493 passed, `python3 -m pytest bench/tests -q "
            "--netguard-strict`, exit 0.")

    def test_a_scripts_py_is_still_a_producer(self):
        """NO REMOVAL. The form the guard already accepted must keep working."""
        g = _guard()
        assert g._NAMES_A_PRODUCER.search(
            "11 of 11, measured with scripts/overstated_entries_2026-09-11.py.")

    def test_a_bare_mention_of_pytest_is_not_a_producer(self):
        """THE BOUNDARY. If this ever passes, the widening has become a hole:
        any paragraph saying the word would satisfy a rule about re-running."""
        g = _guard()
        for vague in ("Suite 7,493 passed under pytest.",
                      "pytest reports 7,493 passed.",
                      "We ran python3 -m pytest and it passed."):
            assert not g._NAMES_A_PRODUCER.search(vague), vague

    def test_the_newest_block_satisfies_the_rule_by_calling_the_rule(self):
        """The regression pin for defect 1, run against the live file."""
        g = _guard()
        block = g._newest_block_text()
        offenders = [p for p in re.split(r"\n\s*\n", block)
                     if g._SUITE_FIGURE.search(p)
                     and not g._NAMES_A_PRODUCER.search(p)]
        assert not offenders, offenders[:2]

    def test_the_pin_is_not_vacuous(self):
        """ANTI-VACUITY: the block must actually carry a suite figure, or the
        test above passes on nothing -- the failure mode this project has
        found 16 times in one session."""
        g = _guard()
        assert len(g._SUITE_FIGURE.findall(g._newest_block_text())) >= 2


class TestTheReachabilityProbeSaysWhenItCannotAnswer:
    def test_it_skips_where_there_is_no_repository(self, tmp_path, monkeypatch):
        """Defect 2. Before the repair this raised AssertionError here."""
        g = _guard()
        monkeypatch.setattr(g, "ROOT", tmp_path)
        with pytest.raises(pytest.skip.Exception):
            g.TestTheNewestBlockIsCurrent().test_it_names_a_commit_reachable_from_head()

    def test_a_bogus_sha_inside_a_real_checkout_still_fails(self, tmp_path,
                                                            monkeypatch):
        """THE SKIP IS SCOPED. A sha that does not exist also exits 128; inside
        a checkout that is a real defect and must not be skipped away."""
        if not subprocess.run(["git", "--version"],
                              capture_output=True).returncode == 0:
            pytest.skip("no git binary")
        repo = tmp_path / "checkout"
        repo.mkdir()
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
               "PATH": "/usr/bin:/bin:/usr/local/bin"}
        for cmd in (["git", "init", "-q"],
                    ["git", "commit", "-q", "--allow-empty", "-m", "x"]):
            r = subprocess.run(cmd, cwd=repo, capture_output=True, env=env)
            if r.returncode != 0:
                pytest.skip(f"cannot build a scratch checkout: {r.stderr[:80]!r}")
        g = _guard()
        monkeypatch.setattr(g, "ROOT", repo)
        monkeypatch.setattr(g, "_newest_block",
                            lambda: ("2026-09-17", "names `deadbeefdeadbeef`"))
        # A SKIP MUST FAIL THIS TEST, NOT PASS THROUGH IT. Repaired at intake,
        # 2026-09-17. The first version wrapped the call in
        # `pytest.raises(AssertionError)` alone; `pytest.skip.Exception` is a
        # BaseException, so a skip loosened to key on exit 128 escaped the
        # `raises` block and this test reported SKIPPED with the suite at exit
        # 0 -- measured by keying the skip on `returncode == 128`: "14 passed,
        # 1 skipped", exit 0. The control could not fire in the one direction
        # it exists for.
        try:
            g.TestTheNewestBlockIsCurrent().test_it_names_a_commit_reachable_from_head()
        except pytest.skip.Exception as skipped:
            pytest.fail("a sha that does not exist INSIDE a real checkout was "
                        f"skipped rather than failed: {skipped}")
        except AssertionError:
            return
        pytest.fail("a sha that does not exist inside a real checkout PASSED "
                    "the reachability check")


class TestTheMeasurementBehindTheWideningTravels:
    def test_the_survey_script_runs_and_reports_both_forms(self):
        """`measured-rate-travels-with-its-script`: the count that justified
        widening the predicate must be reproducible by running its script."""
        script = REPO / "scripts" / "suite_figure_producers_2026-09-17.py"
        assert script.is_file(), script
        r = subprocess.run(["python3", str(script), "--json"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-400:]
        import json
        s = json.loads(r.stdout)
        assert s["paragraphs_with_a_suite_figure"] >= 10
        assert s["backed_by_a_pytest_command"] >= 1
        assert (s["backed_by_either"]
                == s["paragraphs_with_a_suite_figure"] - s["backed_by_neither"])
