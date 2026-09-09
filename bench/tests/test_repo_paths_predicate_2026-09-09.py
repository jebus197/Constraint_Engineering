"""One predicate decides what is archived run output, and it is delimited.

Task 6.4. Founder ruling, verbatim: *"So the sweep (and its original context,
which I shouldn't need to repeat), should be run again if you do this? If so,
do it."*

FIVE CHECKERS DECIDED THIS QUESTION SEPARATELY AND DISAGREED. Measured by
`scripts/archive_root_agreement_2026-09-09.py`: **1 of 10 pairs agreed exactly**,
Wilson [1.8%, 40.4%], Clopper-Pearson [0.3%, 44.5%]. Only 1 of 5 excluded
`bench/results/`; **0 of 5 excluded `bench/logs_quarantine/`**, which exists on
disk and holds quarantined run output; and 1 of 5 tested a bare SUBSTRING rather
than a path prefix. The same file could be production source to one checker and
archive to the next.

THE REASON FOR COMPONENT COMPARISON IS IN THIS REPOSITORY. `bench/logs_quarantine`
starts with the string `bench/logs`, so `startswith("bench/logs")` matches it by
accident while `startswith("bench/logs/")` misses it entirely. Neither is a
decision anyone made. Comparing PATH COMPONENTS removes the choice.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.repo_paths import (  # noqa: E402
    ARCHIVE_ROOTS, is_archived_run_output, is_production_source,
    line_mentions_archive_path,
)


@pytest.mark.parametrize("path,expected", [
    ("bench/logs/run/x.json", True),
    ("bench/logs", True),
    ("bench/logs_quarantine/sim45/x.py", True),
    ("bench/results/report.json", True),
    ("bench/reference_runner_v3.py", False),
    ("scripts/cdsfl_qc.py", False),
    ("docs/GLOSSARY.md", False),
])
def test_classification(path, expected):
    assert is_archived_run_output(path) is expected
    assert is_production_source(path) is (not expected)


@pytest.mark.parametrize("path", [
    "bench/logsomething/x.py",
    "bench/logs_other/x.py",
    "bench/resultsomething/y.json",
])
def test_a_sibling_that_merely_shares_a_prefix_is_not_archive(path):
    """THE WHOLE REASON FOR COMPONENT COMPARISON.

    `"bench/logsomething".startswith("bench/logs")` is True and means nothing.
    If this test fails, the predicate has gone back to string prefixes and the
    5 checkers' disagreement will grow back."""
    assert is_archived_run_output(path) is False


def test_separator_and_dot_prefix_forms_agree():
    for form in ("bench/logs/x", "./bench/logs/x", "bench\\logs\\x"):
        assert is_archived_run_output(form) is True, form


def test_logs_quarantine_is_matched_by_being_named_not_by_prefix():
    """It is a DIFFERENT root, and it is covered because it is declared."""
    assert "bench/logs_quarantine" in ARCHIVE_ROOTS
    assert is_archived_run_output("bench/logs_quarantine/x") is True
    assert is_archived_run_output("bench/logs_quarantine/x",
                                  roots=("bench/logs",)) is False, (
        "it must not be caught by sharing a prefix with bench/logs")


def test_the_declared_roots_exist_or_are_deliberate():
    """A root naming a directory that never existed is an unwired addition."""
    missing = [r for r in ARCHIVE_ROOTS if not (REPO / r).exists()]
    assert not missing, (
        f"{missing} are declared archive roots but are not on disk; either the "
        f"directory was removed or the root was a guess")


# --- the text-scanning companion --------------------------------------------

@pytest.mark.parametrize("line,expected", [
    ('        fp = REPO / "bench/logs/run" / name', True),
    ('    q = base / "bench/logs_quarantine/sim" / f', True),
    ('    out = REPO / "bench/results/x.json"', True),
    ('    # a comment mentioning bench/logs/ as read-only', True),
    ('    x = REPO / "bench/reference_runner_v3.py"', False),
    ('    y = tmp_path / "scratch"', False),
    ('    z = "bench/logsomething/x.py"', False),
])
def test_line_scanning(line, expected):
    assert line_mentions_archive_path(line) is expected


def test_the_line_scanner_is_not_the_path_predicate():
    """WHY BOTH EXIST, pinned as a test rather than left to a comment.

    The first attempt at task 6.4 wired a text-scanning checker to the PATH
    predicate by stripping the line's quotes and passing the whole line. Every
    line then failed the check, every offender was skipped, and the test went
    green while detecting nothing."""
    line = '        fp = REPO / "bench/logs/run" / name'
    assert is_archived_run_output(line.strip().strip('"\'')) is False, (
        "a whole source line is not a path; if this ever returns True the two "
        "predicates have been conflated and the text scan is vacuous")
    assert line_mentions_archive_path(line) is True
