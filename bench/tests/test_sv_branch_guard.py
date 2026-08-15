"""`sv` must say so out loud when it is committing anywhere but main.

WHY THIS EXISTS. The founder ruled weeks ago that main would be the working
branch. A milestone merge to main was made on 28 July 2026; work then continued
on exp39-experimental from 19:11 that same evening, for a further 107 commits
over 18 days. For that fortnight the public repository presented a project 16
days stale while the real work sat on a branch no external reader would open.

Nothing was lost — verified exhaustively on 15 August, 7,628 historical paths
checked — but the drift was invisible while it happened, and that is the defect.
The cause was mechanical: `_commit_and_push` pushes to whatever branch is checked
out and had no concept of main, so the ruling survived exactly as long as someone
remembered it. Same shape as the note standard decaying between v1.2 and v1.4.

The guard WARNS and never aborts, because a deliberate experimental branch is
legitimate. What is not legitimate is arriving on one without noticing.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

SV = REPO / "scripts" / "cdsfl_sv.py"


def _source() -> str:
    return SV.read_text(encoding="utf-8")


def test_the_guard_exists_at_all():
    """Pins the guard's presence, so removing it cannot pass unnoticed."""
    src = _source()
    assert "NOT ON main" in src, (
        "the branch-drift guard is gone from cdsfl_sv.py — main went 16 days "
        "stale the last time nothing checked")


def test_the_guard_reads_the_actual_branch_rather_than_assuming():
    """It must ask git, not infer from a config value or a default."""
    src = _source()
    window = src[src.index("NOT ON main") - 2000:src.index("NOT ON main") + 400]
    assert "rev-parse" in window and "abbrev-ref" in window, (
        "the guard must determine the branch from git, not from an assumption")


def test_the_guard_warns_and_does_not_abort():
    """A deliberate experimental branch is legitimate; blocking it is wrong.

    The failure this guards is *unnoticed* drift, so the correct behaviour is to
    be impossible to miss, not to refuse.
    """
    src = _source()
    start = src.index("NOT ON main")
    window = src[start - 2500:start + 800]
    for forbidden in ("sys.exit", "raise SystemExit", "return False"):
        assert forbidden not in window, (
            f"the guard appears to abort via {forbidden!r}; it must only warn")


def test_the_guard_cannot_itself_break_a_save():
    """A guard that crashes the save is worse than the drift it prevents."""
    src = _source()
    start = src.index("NOT ON main")
    window = src[start - 2500:start + 900]
    assert "except" in window, (
        "the branch lookup must be wrapped — a git failure must not stop a save")


def test_it_names_the_remedy_not_just_the_problem():
    """A warning a reader cannot act on is noise."""
    src = _source()
    start = src.index("NOT ON main")
    assert "git checkout main" in src[start:start + 900], (
        "the warning must tell the reader how to correct the drift")


@pytest.mark.parametrize("branch,should_warn", [
    ("main", False),
    ("exp39-experimental", True),
    ("some-feature", True),
])
def test_the_condition_is_exactly_not_main(branch, should_warn):
    """The comparison is against main specifically, not a pattern or prefix.

    Pinned because a looser test — 'does the branch contain experimental' —
    would have let `some-feature` drift silently, which is the same failure
    wearing different clothes.
    """
    src = _source()
    m = re.search(r'_branch\s*!=\s*"main"', src)
    assert m, "the guard must compare the branch against main by equality"
    assert (branch != "main") is should_warn
