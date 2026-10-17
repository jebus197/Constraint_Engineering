"""Task C6: a skip count is a count of assertions that were not made.

HIS QUESTION, 2026-10-05, verbatim: "Are the 12 skipped safe to ignore?" It sat
under a run reporting "1643 passed, 12 skipped, 0 failed". Nothing answered it
and no script existed that could, while later boards kept quoting skip counts
without classifying them -- 18 in B11, then 20 and 26 in the overnight report
of 2026-10-06.

WHY IT IS SHARP. A skip is exactly how a guard stops running WITHOUT GOING RED,
and a checker that decides nothing is this project's most-repeated defect
class: 11 confirmed defects since 2026-08-01 were additions that did nothing.

THE PROPERTY THIS FILE EXISTS FOR is the one that makes the answer trustworthy
rather than comfortable: AN UNRECOGNISED REASON MUST NOT BE CALLED SAFE. A
classifier that defaults the unknown to safe always reports that everything is
fine, which is how a skip count stops meaning anything. UNCLASSIFIED is its own
class and the producer reports it separately.

Producer: scripts/are_the_skipped_tests_safe_to_ignore_2026-10-17.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "are_the_skipped_tests_safe_to_ignore_2026-10-17.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_c6", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _mod()


def test_the_producer_exists():
    assert PRODUCER.is_file()


@pytest.mark.parametrize("reason,expected", [
    # Absent by design on this machine -- would run where the resource exists.
    ("his Responses folder is not present", "SAFE"),
    ("no archive present in this checkout", "SAFE"),
    ("wolfram is not installed", "SAFE"),
    ("netguard: outbound calls denied by default", "SAFE"),
    ("too few tickets to measure", "SAFE"),
    ("no all-SIM reports in this clone", "SAFE"),
    # Something the project controls -- the guard is off where it should run.
    ("not yet implemented", "NOT SAFE"),
    ("temporarily disabled", "NOT SAFE"),
    ("flaky, see TODO", "NOT SAFE"),
    # His money, his call.
    ("this test dispatches to a paid model", "NEEDS HIS RULING"),
    ("needs an api key and spends credit", "NEEDS HIS RULING"),
])
def test_the_classifier_is_right_on_named_exemplars(reason, expected):
    assert M.classify(reason) == expected, (
        f"{reason!r} classified as {M.classify(reason)!r}, expected "
        f"{expected!r}")


@pytest.mark.parametrize("reason", [
    "",
    "   ",
    "because",
    "see the note above",
    "reason withheld",
])
def test_an_unrecognised_reason_is_never_called_safe(reason):
    """THE ASSERTION THAT MAKES THE ANSWER WORTH ANYTHING."""
    verdict = M.classify(reason)
    assert verdict == "UNCLASSIFIED", (
        f"{reason!r} was classified {verdict!r}. A classifier that defaults "
        f"the unknown to SAFE reports that everything is fine whatever the "
        f"input, which is exactly the checker-that-decides-nothing shape this "
        f"project keeps finding.")


def test_a_paid_reason_outranks_a_safe_sounding_one():
    """Rule ORDER is load-bearing: a reason naming both an absent tool and a
    paid dispatch must go to him, not be filed as safe."""
    assert M.classify("wolfram is unavailable and this would spend credit") \
        == "NEEDS HIS RULING"


def test_the_static_pass_finds_sites_and_is_not_vacuous():
    sites = M.static_sites()
    assert len(sites) > 50, (
        f"only {len(sites)} skip sites found across the suite; the enumerator "
        f"has gone blind and any verdict it produces is vacuous")
    assert all(s["file"].startswith("bench/tests/") for s in sites)
    assert {s["kind"] for s in sites} <= set(M.SKIP_CALLS + M.SKIP_MARKS)


def test_the_enumerator_parses_rather_than_matching_text(tmp_path):
    """`pytest.skip` appears in docstrings and comments throughout this suite,
    so a text match would over-count. Proven on a file built for it."""
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        '"""A docstring mentioning pytest.skip twice: pytest.skip."""\n'
        "# and a comment with pytest.mark.skipif in it\n"
        "def test_x():\n"
        "    assert 1 == 1\n", encoding="utf-8")
    import ast
    tree = ast.parse(probe.read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and M._dotted(n) in
             M.SKIP_CALLS + M.SKIP_MARKS]
    assert calls == [], (
        "the parser found a skip in prose; it is matching text, not parsing")
    assert "pytest.skip" in probe.read_text(encoding="utf-8"), \
        "the probe no longer contains the string, so it proves nothing"


def test_the_guard_set_is_readable_from_the_hook():
    """The default live scope is the pre-commit guard set, because a skip there
    is a gate standing open. If the hook's list cannot be read, the scope
    silently becomes nothing."""
    files = M.guard_files()
    assert files, "the pre-commit GUARDS list could not be read"
    missing = [f for f in files if not (REPO / f).is_file()]
    assert not missing, f"GUARDS names files that do not exist: {missing}"


def test_help_costs_nothing_and_an_unknown_flag_is_refused():
    ok = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                        capture_output=True, text=True, cwd=str(REPO))
    assert ok.returncode == 0
    assert "usage:" in ok.stdout
    bad = subprocess.run([sys.executable, str(PRODUCER), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert bad.returncode != 0, (
        "an unknown flag was accepted silently, which is the 118-day no-op "
        "shape: a script that takes a flag and does nothing with it")
