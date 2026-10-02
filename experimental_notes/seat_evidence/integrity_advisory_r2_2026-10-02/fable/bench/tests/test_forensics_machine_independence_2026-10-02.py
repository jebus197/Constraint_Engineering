# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'integrity_advisory_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 056593bc95c8d2862029f4f431151e0850fbb7266c553481a67f3ea532a6b456
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Panel round 2 (2026-10-02), seat fable: D-1 / D-2 / D-5.

D-1. Exp 48's correct total is 12, not 10. The 2 extra hits (C0017) are a
confined exam falsifier reading the repository by absolute path. The 10 seen on
the canonical checkout was a FALSE NEGATIVE: `_in_scope`'s truncation shortcut
(`a.startswith(target)`) scored any ANCESTOR of an allowlist entry as in scope,
and on the canonical checkout the run directory sits inside the repository, so
the repo-root literal was an ancestor of the run_dir allowlist entry. The
repo_root PARAMETER was never the mechanism: all three pins give 12.

D-2. A forensic verdict must not depend on the scanning checkout. `scan_run`
now takes the run's own repo from a runner-authored record (`repo_root` in
completion_signal.json, written at finalize since 2026-10-02) or an explicit
argument, and REFUSES rather than guessing from `__file__`.

D-5. The C0015 oracle edit (round 1) IS an amendment to a committed acceptance
oracle. What protects C0012's half from the same reasoning later is pinned
here: C0012 is refused by ACCESS rules, not vocabulary, so no
vocabulary-precision argument can ever extend to it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bench.key_access_forensics import (
    RepoRootUnresolved,
    _in_scope,
    resolve_run_repo_root,
    scan_run,
)

REPO = Path(__file__).resolve().parents[2]
EXP48 = REPO / "bench/logs/exp48_chemistry_exam_live_20260729T044134Z"
RUN1B = REPO / "bench/logs/prose_convergence_run1b_2026-10-02_20261002T044234Z"
CANONICAL = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")


# ── D-1 ──────────────────────────────────────────────────────────────────────

def test_exp48_total_is_12_under_both_repo_root_pins():
    for rr in (REPO, CANONICAL):
        rep = scan_run(EXP48, repo_root=rr)
        by = {}
        for h in rep.confirmed:
            by[h.finding] = by.get(h.finding, 0) + 1
        assert by == {"C0012": 10, "C0017": 2}, (rr, by)
        assert rep.repo_in_scope is False  # confined exam, either pin


def test_truncation_shortcut_no_longer_scores_ancestors_in_scope():
    run_on_canonical = str(EXP48).replace(str(REPO), str(CANONICAL))
    allow = [run_on_canonical, "/Users/georgejackson/CDSFL_review_targets"]
    # The C0017 literal: the repo root, an ANCESTOR of the run dir. Pre-fix this
    # was True on the canonical checkout, which is where the 10 came from.
    assert not _in_scope(str(CANONICAL), allow)
    # $HOME was an ancestor of every target dir, so `ls /Users/georgejackson`
    # scored in scope on EVERY machine. Closed by the same line.
    assert not _in_scope("/Users/georgejackson", allow)
    # A genuine display truncation (cut MID-COMPONENT) keeps its shortcut.
    assert _in_scope("/Users/georgejackson/CDSFL_rev", allow)
    # And an elided path keeps its documented carve-out.
    assert _in_scope("~/.../target.md", allow)


# ── D-2 ──────────────────────────────────────────────────────────────────────

def test_scan_refuses_rather_than_guessing_the_repo_root():
    with pytest.raises(RepoRootUnresolved):
        scan_run(EXP48)  # archived run: no runner-authored repo_root record


def test_runner_authored_record_is_honoured(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    (run / "completion_signal.json").write_text(
        json.dumps({"status": "CONVERGED", "repo_root": str(tmp_path / "repo")}))
    assert resolve_run_repo_root(run) == tmp_path / "repo"
    rep = scan_run(run)  # resolves from the record: no refusal, no guess
    assert rep.files_scanned == 1


def test_relative_declared_target_resolves_against_the_runs_repo():
    # run 1b declares `bench` (relative). Resolved against the run's own repo
    # it is UNDER the repo root, so the run is a code review, not a confined
    # exam -- the misclassification that produced 114/108 is gone.
    rep = scan_run(RUN1B, repo_root=CANONICAL)
    assert rep.repo_in_scope is True
    assert str(CANONICAL / "bench") in rep.target_dirs
    # Residual, carried not hidden: the harvested detector copy quoting its own
    # fixtures. Every remaining hit is in that one carried source file.
    assert {h.file for h in rep.confirmed} <= {
        "panel_worktree_harvest/files/bench/falsifier_verify.py"}


def test_verdict_no_longer_depends_on_the_scanning_machine_for_exp48():
    a = scan_run(EXP48, repo_root=REPO)
    b = scan_run(EXP48, repo_root=CANONICAL)
    key = lambda rep: sorted((h.file, h.finding, h.label) for h in rep.confirmed)
    assert key(a) == key(b)


# ── D-5 ──────────────────────────────────────────────────────────────────────

_ACCESS_REASONS = {
    "an answer-key file path",
    "a key-internal field subscripted (implies a loaded key object)",
    "a key-internal field fetched via .get()",
    "a claims->truth lookup (the answer-key schema)",
}


def test_c0012_refusal_is_access_not_vocabulary():
    """The criterion, pinned, not the list: C0012 fires ACCESS rules. The C0015
    amendment's whole justification was 'fires 0 access rules, 1 vocabulary
    rule'; that reasoning can never extend to a falsifier that opens the key,
    subscripts its fields, and walks claims->truth -- and this test is the
    committed statement of that boundary."""
    from bench.falsifier_verify import scan_falsifier_source
    report = json.loads(
        (EXP48 / "exp48_chemistry_exam_live_report.json").read_text())
    code = report["registry"]["entries"]["C0012"]["falsifier_code"]
    reasons = {r for r, _ in scan_falsifier_source(code)}
    access = reasons & _ACCESS_REASONS
    assert len(access) >= 3, reasons   # path + subscript + claims->truth
