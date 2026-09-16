"""A8: the era census must not count a log file citing its own siblings.

FOUNDER, 2026-09-16: the untracked cited logs might be explained by the
project's early prose era. Testing that needs a census, and the first version of
this census made the defect the A8 entry itself records: it matched every
`bench/logs/...` string in every TRACKED file, and 6,459 files under bench/logs
are tracked despite `.gitignore:41`. One archived transcript alone contributed
1,047 matches, so the result measured the extractor rather than the corpus.

These tests EXECUTE both forms and require them to differ, which is the only way
to catch a scanner that silently reverts to the wide population.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "orphan_citation_era_2026-09-17.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("era", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["era"] = m
    spec.loader.exec_module(m)
    return m


def _wide_population() -> int:
    """The WRONG form, run deliberately: sources not excluding bench/logs."""
    raw = subprocess.run(
        ["git", "grep", "-I", "-o", "-E", r"bench/logs/[A-Za-z0-9_][A-Za-z0-9_./-]*",
         "--", "."], cwd=REPO, capture_output=True, text=True).stdout
    return len({l.split(":", 1)[1].strip().rstrip(".,);`'\"")
                for l in raw.splitlines() if ":" in l})


def test_the_narrow_form_is_much_smaller_than_the_wide_one(mod):
    narrow = len(mod.cited_paths())
    wide = _wide_population()
    assert narrow < wide, "excluding bench/logs changed nothing; the exclusion is not applied"
    assert wide > 3 * narrow, (
        f"wide {wide} against narrow {narrow}: the wide form should sweep in "
        f"thousands of log-internal strings, so this comparison is not exercising "
        f"what it claims")


def test_no_source_under_bench_logs_contributes(mod):
    """The exclusion must hold at the pathspec, not by luck of the corpus."""
    raw = subprocess.run(
        ["git", "grep", "-I", "-l", "-E", r"bench/logs/[A-Za-z0-9_]",
         "--", ":(exclude)bench/logs", "."], cwd=REPO,
        capture_output=True, text=True).stdout
    assert raw.strip(), "no sources found at all; the census would be empty"
    assert not any(l.startswith("bench/logs/") for l in raw.splitlines())


def test_every_cited_path_is_classified(mod):
    cites = mod.cited_paths()
    assert cites, "no citations found"
    for path, kinds in cites.items():
        assert kinds <= {"NOTE", "TEST", "CODE"}, (path, kinds)
        assert kinds, path


def test_era_reads_both_directory_naming_styles(mod):
    assert mod.era("bench/logs/exp55_v3_control_20260823T153955Z/x.json") == "2026-08"
    assert mod.era("bench/logs/panel_round15_2026-09-11/cc2.json") == "2026-09"
    assert mod.era("bench/logs/launcher_transcripts/no_date_here.log") is None


def test_help_answers_without_measuring(mod):
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0
    assert "hypothesis" in r.stdout.lower()
