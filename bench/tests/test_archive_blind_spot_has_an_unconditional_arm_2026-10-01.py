"""The archive blind spot must be guarded where the FOUNDER runs it too.

FREE PANEL, 2026-10-01, Q5. `test_shell_grep_blind_spot_2026-09-28.py` skips
unless the session `grep` wrapper can exec its backend, which happens only where
`CLAUDE_CODE_EXECPATH` is set -- an agent's environment, not a login shell. The
skip is right for the wrapper proposition and wrong as the whole guard, because
the project-level fact it protects needs no wrapper: the evidence archive sits
behind a `.gitignore` rule, so every ignore-aware search is blind to it.

This arm asserts that fact from the filesystem alone: no git binary, no shell,
no `grep`, no environment variable in the decision. The RATE stays with the
wrapper test, where it belongs -- it moves with the repository. The EXISTENCE of
the blind spot moves with nothing.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "scripts"
          / "archive_is_invisible_to_ignore_aware_search_2026-10-01.py")


def _mod():
    assert SCRIPT.is_file(), f"missing {SCRIPT}"
    spec = importlib.util.spec_from_file_location("archive_blind_arm",
                                                  str(SCRIPT))
    m = importlib.util.module_from_spec(spec)
    sys.modules["archive_blind_arm"] = m
    spec.loader.exec_module(m)
    return m


def test_the_archive_is_behind_an_ignore_rule():
    m = _mod()
    hits = m.rules_matching_archive()
    n = m.archive_file_count()
    if n < m.MIN_FILES:
        import pytest
        pytest.skip(f"only {n} archived files in this clone")
    assert hits, (
        f"{n} files under {m.ARCHIVE_REL}/ and no .gitignore rule covers them; "
        f"either the ignore rule was dropped (good -- retire this guard and the "
        f"wrapper test's premise) or the archive moved")


def test_the_decision_does_not_read_the_environment():
    """The whole point of this arm. It must not consult the agent's env.

    EXECUTED, NOT GREPPED: the two deciding functions are called with the
    agent-only variable REMOVED from the environment, and must return the same
    answer. A source-text check here would assert only that the module
    describes itself consistently.
    """
    m = _mod()
    before = (sorted(m.rules_matching_archive()), m.archive_file_count())
    saved = os.environ.pop("CLAUDE_CODE_EXECPATH", None)
    try:
        after = (sorted(m.rules_matching_archive()), m.archive_file_count())
    finally:
        if saved is not None:
            os.environ["CLAUDE_CODE_EXECPATH"] = saved
    assert before == after, (
        "the unconditional arm changed its answer when CLAUDE_CODE_EXECPATH "
        "was removed, so it is measuring the environment after all")


def test_the_arm_runs_clean_and_is_wired():
    """An addition nothing reaches is not additive: this is the caller."""
    assert _mod().main() == 0
