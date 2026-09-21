"""A resume pointer must be TRUE about git, or must say it is history.

WHAT THIS GUARDS, AND WHY THE SISTER TEST CANNOT.

`test_a_stale_source_says_so_2026-09-21.py` asks whether a canonical source is
OLD AND SILENT: file age from git, 14-day threshold, banner required past it.
That is the right question for an abandoned document and the wrong question for
a resume pointer, because a resume pointer goes wrong by being FALSE, not by
being old -- and a false one can be hours old.

THE INSTANCE. During an `rs` restore at 2026-09-21 22:14 BST,
`experimental_notes/CDSFL_Agent_Operational_Plan.md` -- by its own header the
"First resource to read after any compaction or long break" -- carried:

    ★ RESUME POINTER (2026-09-20 03:54 BST). SUPERSEDES EVERY POINTER BELOW.
    HEAD `d17ab01`, main, working tree CLEAN,
    **11 ahead of `origin/main` -- NOT PUSHED**

Every git fact in it was false: HEAD was `2b56916`, 23 commits later, and
`origin/main` was identical to HEAD, so nothing was unpushed. The file had been
committed 2 days earlier, so the age-based guard owed it nothing and said
nothing. The failure mode is not hypothetical for this file: it is the same file
that told a restoring session on 2026-09-09 that the answer-key sealing was
still waiting for the founder, 2 days after he had driven home to do it himself.

The test executes the claim rather than reading the text around it, which is
`execute-do-not-grep`: the document is internally consistent either way, so only
resolving its commit against the repository can show the document and the
repository disagree.

A pointer that LABELS itself historical is not judged. That exemption is not a
loophole -- `test_the_disclaimer_exemption_cannot_launder_a_live_pointer` below
holds it shut by requiring the label to sit with the claim, and the producer's
own first version over-reported precisely because the exemption was missing.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "resume_pointer_truth_2026-09-21.py"


def _module():
    spec = importlib.util.spec_from_file_location("resume_pointer_truth", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()


def test_the_producer_exists_and_imports():
    """A checker nobody can run is the shape this whole family exists to stop."""
    assert SCRIPT.is_file(), f"the resume-pointer checker is gone: {SCRIPT}"
    _module()


def test_no_canonical_source_asserts_a_false_git_fact():
    """The live guard. Green means every current pointer still resolves."""
    m = _module()
    head = _git("rev-parse", "HEAD")
    ahead = int(_git("rev-list", "--count", "origin/main..HEAD") or 0)

    liars = []
    for rel in m.SOURCES:
        row = m.check(rel, head, ahead)
        if row["verdict"] == "FALSE":
            liars.append(f"{rel}:\n      " + "\n      ".join(row["failures"]))

    assert not liars, (
        "these recovery documents assert git facts that are no longer true, and a "
        "restoring session reads them as current state:\n    " + "\n    ".join(liars)
    )


def test_the_check_can_actually_fail(tmp_path, monkeypatch):
    """A guard that cannot go red is not a guard.

    Reverting the repair must reproduce the failure, so the stale pointer text is
    reconstructed verbatim and fed through the real `check`.
    """
    m = _module()
    doc = tmp_path / "tracker.md"
    doc.write_text(
        "**★ RESUME POINTER (2026-09-20 03:54 BST). SUPERSEDES EVERY POINTER BELOW.** "
        "HEAD `d17ab01`, main, working tree CLEAN, "
        "**11 ahead of `origin/main` — NOT PUSHED**.\n"
    )
    monkeypatch.setattr(m, "REPO", tmp_path, raising=True)
    # `check` resolves SHAs through the real repository, so point BOTH git
    # helpers back there while the fixture document is read from tmp_path.
    #
    # `git_rc` must be redirected too. When it was not, `merge-base` ran against
    # tmp_path, which is not a git checkout, and its error exit was read as
    # "not an ancestor" -- so this test PASSED while asserting a failure count
    # it was reaching for the wrong reason. A test that is green by accident is
    # the thing this whole file exists to prevent.
    monkeypatch.setattr(m, "git", lambda *a: _git(*a), raising=True)
    monkeypatch.setattr(m, "git_rc", lambda *a: subprocess.run(
        ["git", *a], cwd=REPO, capture_output=True).returncode, raising=True)

    row = m.check("tracker.md", _git("rev-parse", "HEAD"), 0)
    assert row["verdict"] == "FALSE", row
    # 2, NOT 3. `d17ab01` is a real ancestor of HEAD, so naming it is a stale
    # pointer rather than a false claim and is reported as a note. The 2 claims
    # that were FALSE ABOUT THE PRESENT -- "NOT PUSHED" and "11 ahead" -- are
    # what the guard convicts on, and they are the 2 that caused the harm.
    assert len(row["failures"]) == 2, (
        "the stale pointer made 2 claims about the present and both were false: "
        "it said work was NOT PUSHED and 11 commits ahead, when nothing was "
        f"unpushed. The check found {len(row['failures'])}: {row['failures']}"
    )
    assert any("NOT PUSHED" in f for f in row["failures"]), row["failures"]
    assert any("ahead" in f for f in row["failures"]), row["failures"]
    assert any("ancestor, so not charged" in n for n in row["notes"]), row["notes"]


def test_the_disclaimer_exemption_cannot_launder_a_live_pointer(tmp_path, monkeypatch):
    """The label must sit WITH the claim, not merely somewhere in the file.

    Without this, any document containing the word "HISTORICAL" anywhere would
    excuse every false pointer in it.
    """
    m = _module()
    doc = tmp_path / "tracker.md"
    doc.write_text(
        "**★ RESUME POINTER.** HEAD `d17ab01`, **11 ahead of `origin/main`**.\n"
        + "\n" * 40
        + "Some much later block, clearly marked HISTORICAL, about other commits.\n"
    )
    monkeypatch.setattr(m, "REPO", tmp_path, raising=True)
    monkeypatch.setattr(m, "git", lambda *a: _git(*a), raising=True)

    row = m.check("tracker.md", _git("rev-parse", "HEAD"), 0)
    assert row["verdict"] == "FALSE", (
        "a HISTORICAL label far below a live pointer excused it; the exemption "
        f"must be local to the claim. Got: {row}"
    )


def test_a_correctly_labelled_historical_pointer_is_not_charged(tmp_path, monkeypatch):
    """The other direction: recording history must stay cost-free.

    `RECOVERY.md` and `CURRENT_STATE.md` both name older commits and both label
    them. The producer's first version charged both, which would have pressured
    a future session to delete accurate history to get the suite green.
    """
    m = _module()
    doc = tmp_path / "recovery.md"
    doc.write_text(
        "**SESSION STATE [HISTORICAL — this block describes commit `d17ab01` and "
        "is NOT current state].** HEAD `d17ab01`, **11 ahead of `origin/main`**.\n"
    )
    monkeypatch.setattr(m, "REPO", tmp_path, raising=True)
    monkeypatch.setattr(m, "git", lambda *a: _git(*a), raising=True)

    row = m.check("recovery.md", _git("rev-parse", "HEAD"), 0)
    assert row["verdict"] == "DISCLAIMED", (
        "a pointer that explicitly says it is historical was charged as false; "
        f"recording history must not cost anything. Got: {row}"
    )
    assert not row["failures"]


def test_the_tracker_is_in_scope():
    """The file the defect was found in must be the file the guard watches."""
    m = _module()
    assert "experimental_notes/CDSFL_Agent_Operational_Plan.md" in m.SOURCES, (
        "the operational tracker is the first document a restoring session reads "
        "and is where this defect was found; it cannot drop out of the checked set"
    )


def test_the_wilson_interval_is_cross_verified_not_asserted():
    """The producer's 2 CI routes must actually agree, and must be able to disagree."""
    m = _module()
    lo, hi = m.wilson_two_ways(1, 1)
    assert 0.0 < lo < 1.0 and hi == pytest.approx(1.0, abs=1e-12), (lo, hi)
    # A known value, so the pair is checked against arithmetic and not only itself.
    lo2, hi2 = m.wilson_two_ways(5, 10)
    assert lo2 == pytest.approx(0.2365, abs=5e-4), lo2
    assert hi2 == pytest.approx(0.7635, abs=5e-4), hi2


def test_a_pointer_naming_a_commit_from_another_history_is_charged(tmp_path, monkeypatch):
    """A fabricated or rewritten-history hash is a real defect, not staleness."""
    m = _module()
    doc = tmp_path / "tracker.md"
    doc.write_text("**★ RESUME POINTER.** HEAD `0123456789abcdef0123456789abcdef01234567`.\n")
    monkeypatch.setattr(m, "REPO", tmp_path, raising=True)
    monkeypatch.setattr(m, "git", lambda *a: _git(*a), raising=True)
    row = m.check("tracker.md", _git("rev-parse", "HEAD"), 0)
    assert row["verdict"] == "FALSE", row
    assert any("not a commit in this repository" in f for f in row["failures"]), row


def test_a_git_failure_is_reported_as_unchecked_not_as_refuted(tmp_path, monkeypatch):
    """`merge-base --is-ancestor` exits 1 for "no" and other codes for errors.

    Collapsing them made the guard state confidently that a commit was "on
    another branch or from a rewritten history" when git had merely failed to
    read the repository. An unchecked claim must say it is unchecked.
    """
    m = _module()
    doc = tmp_path / "tracker.md"
    head = _git("rev-parse", "HEAD")
    parent = _git("rev-parse", "HEAD~1")
    doc.write_text(f"**★ RESUME POINTER.** HEAD `{parent[:7]}`.\n")
    monkeypatch.setattr(m, "REPO", tmp_path, raising=True)
    monkeypatch.setattr(m, "git", lambda *a: _git(*a), raising=True)
    monkeypatch.setattr(m, "git_rc", lambda *a: 128, raising=True)   # git errored
    row = m.check("tracker.md", head, 0)
    assert row["verdict"] == "FALSE", row
    assert any("UNCHECKED" in f for f in row["failures"]), row["failures"]
    assert not any("another branch" in f for f in row["failures"]), (
        "a git error was reported as a refutation", row["failures"])
