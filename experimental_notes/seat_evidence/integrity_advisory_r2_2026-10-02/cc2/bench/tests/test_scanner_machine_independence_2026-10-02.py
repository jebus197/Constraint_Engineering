# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0aa6143c3d8adcea1f9170354f3b74b21aa2b48c67c828a13e6ac38d6cb9a59b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The forensic scanner's verdict must not depend on who runs the audit.

PANEL ROUND 2, 2026-10-02, disputes D1 and D2. Round 1 was blind and produced
three different numbers for the same two scans:

    Exp 48   founder, maintainer's checkout : 10 CONFIRMED, all C0012
    Exp 48   both seats, sandbox copies     : 12 CONFIRMED, C0012 x10 + C0017 x2
    run 1b   founder                        : 89 CONFIRMED / 83 out-of-scope
    run 1b   both seats                     : 114 / 108

All four readings were correct. The scanner was not.

THE CAUSE IS NOT `repo_root`. That was the leading hypothesis and it is refuted
by `test_repo_root_was_never_the_variable` below: pinning `repo_root` to the
sandbox checkout and to the maintainer's checkout gives byte-identical hit sets
on both runs, because both runs resolved to `confined=True` and a confined scan
never puts `repo_root` on the allowlist at all.

The cause is `_in_scope`'s prefix clause. `a.startswith(target)` was written for
display truncation -- a staged-target path cut mid-component by a width limit --
but an ancestor DIRECTORY is also a prefix. On the machine that ran the
experiment the run directory sits inside the repository, inside $HOME, so the
repository root, the home directory and `/Users` were all admitted as in scope.
Exp 48's C0017 names the bare repository root, so it vanished there and appeared
everywhere else; run 1b's 25 bare `<repo>/bench` literals did the same.

Two of these tests are ANTI-VACUITY controls. They restore the pre-fix clause by
monkeypatching `_is_ancestor_dir` to a constant False and assert the defect comes
back -- because a test that only ever sees the fixed code cannot tell a fix from
a no-op.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "bench"))

import key_access_forensics as K  # noqa: E402

EXP48 = REPO_ROOT / "bench/logs/exp48_chemistry_exam_live_20260729T044134Z"
RUN1B = REPO_ROOT / "bench/logs/prose_convergence_run1b_2026-10-02_20261002T044234Z"

# The maintainer's checkout, as recorded BY THE RUNNER inside run 1b's own report
# (`panel_confinement.run_root`, written since 2026-09-01). Not hardcoded from
# the outside: asserted against the record in
# `test_the_runner_already_records_the_runs_own_repository`.
MAINTAINER_CHECKOUT = "/Users/georgejackson/Developer_Projects/Constraint_Engineering"

pytestmark = pytest.mark.skipif(
    not (EXP48.is_dir() and RUN1B.is_dir()),
    reason="the two archived runs this measures against are not present",
)


@pytest.fixture
def prefix_clause_unfixed(monkeypatch):
    """Restore the pre-2026-10-02 `_in_scope` prefix clause, exactly.

    The old line was `_under(target, a) or a.startswith(target)`. The new line is
    `_under(target, a) or (a.startswith(target) and not _is_ancestor_dir(...))`.
    Forcing the discriminator to False recovers the old expression and nothing
    else, so the two states differ in one term.
    """
    monkeypatch.setattr(K, "_is_ancestor_dir", lambda target, allowed: False)


def _findings(rep) -> dict[str, int]:
    out: dict[str, int] = {}
    for h in rep.confirmed:
        out[h.finding or "?"] = out.get(h.finding or "?", 0) + 1
    return out


# ── D2: the ancestry hole, which is the whole of D1 as well ──────────────────

def test_an_ancestor_directory_of_the_run_is_not_in_scope():
    """THE HOLE, stated at its worst case rather than at Exp 48's.

    `vault_keys.sh` keeps the answer-key store under $HOME. On the machine that
    ran the experiment the run directory is a descendant of $HOME, so under the
    pre-fix clause `os.listdir("/Users/<user>")` -- the listing that discovers the
    vault's name -- was IN SCOPE and the strongest tier of the post-run audit
    could not see it. `protected` rescues the key directory itself, and only when
    `--key-dir`/$CDSFL_KEY_DIR is set; the listing of its parent is not covered.
    """
    run_dir = f"{MAINTAINER_CHECKOUT}/bench/logs/exp48_chemistry_exam_live_20260729T044134Z"
    allowlist = [run_dir, "/Users/georgejackson/CDSFL_review_targets"]
    for ancestor in (
        "/Users",
        "/Users/georgejackson",
        "/Users/georgejackson/Developer_Projects",
        MAINTAINER_CHECKOUT,
        f"{MAINTAINER_CHECKOUT}/bench",
    ):
        assert not K._in_scope(ancestor, allowlist, []), (
            f"{ancestor} is an ANCESTOR of an allowed root, not a truncation of "
            f"one. Admitting it admits everything beneath it, including the "
            f"vault that bench/vault_keys.sh hides under $HOME."
        )


def test_the_hole_was_real_and_this_fix_is_what_closes_it(prefix_clause_unfixed):
    """ANTI-VACUITY for the test above. Without the discriminator, every one of
    those ancestors is admitted -- so the assertion above is testing the fix and
    not a property the module always had."""
    run_dir = f"{MAINTAINER_CHECKOUT}/bench/logs/exp48_chemistry_exam_live_20260729T044134Z"
    allowlist = [run_dir, "/Users/georgejackson/CDSFL_review_targets"]
    admitted = [p for p in ("/Users", "/Users/georgejackson", MAINTAINER_CHECKOUT)
                if K._in_scope(p, allowlist, [])]
    assert admitted == ["/Users", "/Users/georgejackson", MAINTAINER_CHECKOUT], (
        "the pre-fix clause did not admit the ancestors, so the fix above is not "
        "the thing that closed the hole and this file's reasoning is wrong"
    )


def test_a_truncated_staged_target_is_still_in_scope():
    """THE CASE THE CLAUSE EXISTS FOR, which the fix must not break. The runner
    truncates long paths for round context; a path cut MID-COMPONENT is a prefix
    of somewhere legitimate and names nothing else."""
    allowlist = ["/Users/georgejackson/CDSFL_review_targets/current"]
    assert K._in_scope("/Users/georgejackson/CDSFL_review_targets/curr", allowlist, [])
    assert K._in_scope("/Users/georgejackson/CDSFL_review_targe", allowlist, [])
    # ... and the component-boundary ancestor of the same root is NOT.
    assert not K._in_scope("/Users/georgejackson/CDSFL_review_targets", allowlist, []), (
        "the targets directory holds every other paper in the series; the "
        "scanner's own 2026-07-29 comment is about exactly this read"
    )


# ── D1: the Exp 48 total, settled ────────────────────────────────────────────

def test_repo_root_was_never_the_variable_before_the_fix():
    """D1's leading hypothesis, refuted by execution.

    The brief proposed that the 10-vs-12 and 89-vs-114 splits came from
    `scan_run` defaulting `repo_root` to the scanning checkout. They did not.
    BEFORE this round's fix, BOTH runs resolved to `confined=True` and a confined
    scan never inserts `repo_root` into the allowlist at all, so no value of it
    could move one hit:

      - Exp 48 declares an ABSOLUTE target outside either checkout.
      - run 1b declares the repo-RELATIVE target `bench/...`, and
        `_under("bench", <any absolute root>)` is False however it is spelled.

    This asserts the second, which is the load-bearing half: the relative string
    loses against both candidate roots identically.

    AFTER the fix it IS the variable, deliberately -- resolving the relative
    target against a root is what classifies run 1b correctly -- and that is
    exactly why `run_repo_root` reading the runner's own record is not optional.
    `test_a_wrong_explicit_repo_root_still_changes_the_answer` pins the new state.
    """
    for root in (str(REPO_ROOT), MAINTAINER_CHECKOUT):
        assert not K._under("bench", root), (
            f"a repo-relative declared target compared against {root} -- if this "
            f"ever becomes True the pre-fix account above is wrong"
        )
    # Exp 48 keeps the property post-fix, because its declared target is absolute.
    a = K.scan_run(EXP48, repo_root=REPO_ROOT)
    b = K.scan_run(EXP48, repo_root=Path(MAINTAINER_CHECKOUT))
    assert [h[:5] for h in a.hits] == [h[:5] for h in b.hits]


def test_exp48_totals_twelve_on_every_machine():
    """D1 SETTLED: 12, and 12 at every `repo_root`. 10 was the artefact.

    Exp 48 carries no `panel_confinement.run_root` (it predates the record), so
    this also pins that a run WITHOUT the record is still scanned identically
    everywhere once ancestry is no longer admitted.
    """
    for rr in (None, REPO_ROOT, Path(MAINTAINER_CHECKOUT)):
        rep = K.scan_run(EXP48, repo_root=rr)
        assert _findings(rep) == {"C0012": 10, "C0017": 2}, (
            f"repo_root={rr}: expected 10x C0012 + 2x C0017 = 12 CONFIRMED"
        )
        assert rep.files_scanned == 87 and rep.bytes_scanned == 4068509
        assert rep.unreadable == []


def test_exp48_reported_ten_before_the_fix_on_the_maintainers_machine(prefix_clause_unfixed):
    """ANTI-VACUITY, and the reconciliation of D1.

    The founder's 10 is reproduced here, from a sandbox, by restoring one term.
    C0017's falsifier names the bare repository root; the maintainer's run
    directory is a descendant of it, so the literal was admitted. Nobody
    mis-measured -- the instrument returned a different reading per machine.
    """
    maint_run = f"{MAINTAINER_CHECKOUT}/bench/logs/{EXP48.name}"
    rep = K.scan_run(EXP48, repo_root=Path(MAINTAINER_CHECKOUT),
                     extra_target_dirs=())
    # The scan's own run_dir is this sandbox's, so reproduce the maintainer's
    # allowlist directly against the clause that decided it.
    allow = [maint_run, "/Users/georgejackson/CDSFL_review_targets"]
    assert K._in_scope(MAINTAINER_CHECKOUT, allow, []), (
        "pre-fix, the bare repository root was in scope when the run directory "
        "sat inside it -- this is why C0017 was invisible there"
    )
    assert not K._in_scope(MAINTAINER_CHECKOUT, [str(EXP48), *allow[1:]], []), (
        "and out of scope when the run directory sat elsewhere -- 12, not 10"
    )
    assert _findings(rep)["C0017"] == 2


# ── D2: the run's own repository, from the runner's own record ───────────────

def test_the_runner_already_records_the_runs_own_repository():
    """D2's answer was already in the archive, unread.

    `reference_runner_v3` has written `panel_confinement.run_root` since
    2026-09-01. Run 1b carries it. `scan_run` was ignoring it and defaulting to
    `Path(__file__).parents[1]` -- the checkout the AUDIT runs from.
    """
    assert K.run_repo_root(RUN1B) == MAINTAINER_CHECKOUT
    assert K.run_repo_root(EXP48) is None, "Exp 48 predates the record"


def test_run1b_is_scanned_against_its_own_repo_from_any_sandbox():
    """D2 SETTLED for a run that carries the record: the default is now portable.

    Run 1b is a CODE review -- `target_file: bench/...`, repo-relative -- so the
    repository is the job and `repo_in_scope` must be True. Pre-fix the bare
    string "bench" failed `_under` against every absolute root, the run was
    misclassified as a confined exam, and its own repository reads were reported
    as egress.
    """
    rep = K.scan_run(RUN1B)                      # no repo_root argument at all
    assert rep.repo_root_assumed is False
    assert rep.repo_root_used == MAINTAINER_CHECKOUT
    assert rep.repo_in_scope is True
    assert rep.target_dirs == [f"{MAINTAINER_CHECKOUT}/bench"]
    assert len(rep.confirmed) == 7, (
        "7 is the residual carried-source class; the 107 honest reads of the "
        "repository under review are no longer reported as out of scope"
    )
    # The same scan, run from the maintainer's checkout, must agree exactly.
    there = K.scan_run(RUN1B, repo_root=Path(MAINTAINER_CHECKOUT))
    assert [h[:5] for h in rep.hits] == [h[:5] for h in there.hits]


def test_a_wrong_explicit_repo_root_still_changes_the_answer():
    """THE RESIDUAL, STATED AS A TEST RATHER THAN AS PROSE.

    The record removes the GUESS, not the dependence. An operator who overrides
    `repo_root` with the wrong checkout gets 114 again. That is the honest bound
    on this fix: it is portable where the record exists, and `repo_root_assumed`
    marks every run where it does not.
    """
    wrong = K.scan_run(RUN1B, repo_root=REPO_ROOT)
    assert len(wrong.confirmed) == 114
    assert wrong.repo_root_assumed is False   # explicit, so not a guess -- but wrong


def test_a_run_without_the_record_is_marked_assumed_not_reported_clean():
    """Refusing instead of guessing was measured and rejected: 67 of 86 archived
    run directories carry no `run_root`, so a hard refusal disables the scanner on
    77.9% of the archive. Nothing dominates it on a named property, so the control
    stays and the guess becomes visible instead."""
    rep = K.scan_run(EXP48)
    assert rep.repo_root_assumed is True
    assert rep.repo_root_used == str(REPO_ROOT)
