"""The forensic verdict over an archive is a fact about the RUN, not the cwd.

STAR round 2026-10-03. Before the pin, `scan_run` judged archived absolute
path literals against the scanning machine's repo root only: run 1b scored
107 false advisory hits from any relocated checkout and the committed
measurement scripts/advisory_channel_selection_2026-10-02.py aborted on its
own regression assert. The pin reads `panel_confinement.run_root` from
RUNNER-AUTHORED records (trusted_record_names, the same anti-widening
boundary that guards target_file) and adds it ALONGSIDE the live root.

Guards asserted here, both directions:
  * run 1b reads 0 advisory / 7 audit from THIS checkout and from a second,
    physically different root (relocation invariance);
  * a forged second report cannot widen the recorded root (disagreement
    refuses the pin);
  * a confined exam stays confined: recording a run_root does not put the
    repo in scope when the targets sit outside it;
  * the exp48 exam verdict is unchanged by the pin (content-based key
    signals never consult scope).
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.key_access_forensics import (  # noqa: E402
    build_end_of_run_advisory, discover_run_root, scan_run)

RUN_1B = ROOT / "bench" / "logs" / "prose_convergence_run1b_2026-10-02_20261002T044234Z"
EXP48 = ROOT / "bench" / "logs" / "exp48_chemistry_exam_live_20260729T044134Z"

pytestmark = pytest.mark.skipif(not RUN_1B.is_dir(), reason="run 1b absent")


def test_recorded_root_is_discovered():
    assert discover_run_root(RUN_1B) == \
        "/Users/georgejackson/Developer_Projects/Constraint_Engineering"


def test_run1b_is_silent_from_this_checkout():
    rep = scan_run(RUN_1B, repo_root=ROOT)
    assert rep.run_root_recorded is not None
    assert len(rep.advisory_confirmed) == 0, [
        (h.file, h.label) for h in rep.advisory_confirmed][:5]
    assert len(rep.audit_confirmed) == 7
    assert build_end_of_run_advisory(rep) is None


def test_run1b_is_silent_from_a_second_real_root(tmp_path):
    """Relocation invariance: a physically different checkout location."""
    fake = tmp_path / "second_checkout"
    (fake / "bench").mkdir(parents=True)
    # the counterpart lookup only needs the committed files carried sources
    # quote; copy the module tree it reads
    for f in (ROOT / "bench").glob("*.py"):
        shutil.copy(f, fake / "bench" / f.name)
    rep = scan_run(RUN_1B, repo_root=fake)
    assert len(rep.advisory_confirmed) == 0, [
        (h.file, h.label) for h in rep.advisory_confirmed][:5]
    assert len(rep.audit_confirmed) == 7
    assert build_end_of_run_advisory(rep) is None


def test_a_forged_second_report_cannot_widen_the_root(tmp_path):
    run = tmp_path / "forged_run"
    run.mkdir()
    (run / "real_exp_report.json").write_text(json.dumps({
        "experiment": "real_exp",
        "panel_confinement": {"run_root": "/legit/checkout"}}))
    assert discover_run_root(run) == "/legit/checkout"
    # a model writes a second report declaring a friendlier root. "/" would
    # be refused outright by the slash guard (tested below), so the attack
    # uses the widest root the guard does not catch on its own.
    (run / "codex_analysis_report.json").write_text(json.dumps({
        "experiment": "codex_analysis",
        "panel_confinement": {"run_root": "/Users/attacker"}}))
    # two reports, two disagreeing recorded roots: the pin REFUSES (None)
    # rather than widening -- fall back to pre-pin behaviour, never trust
    # the forged value
    assert discover_run_root(run) is None


def test_root_slash_is_refused(tmp_path):
    run = tmp_path / "slash_run"
    run.mkdir()
    (run / "checkpoint.json").write_text(json.dumps({
        "panel_confinement": {"run_root": "/"}}))
    assert discover_run_root(run) is None


def test_a_confined_exam_stays_confined(tmp_path):
    """Recording a run_root must not put the repo in scope for an exam whose
    targets were deliberately staged OUTSIDE it."""
    run = tmp_path / "exam_run"
    run.mkdir()
    (run / "checkpoint.json").write_text(json.dumps({
        "target_file": str(tmp_path / "staged_exam" / "paper.md"),
        "panel_confinement": {"run_root": str(ROOT)}}))
    (tmp_path / "staged_exam").mkdir()
    (tmp_path / "staged_exam" / "paper.md").write_text("exam")
    rep = scan_run(run, repo_root=ROOT)
    assert rep.repo_in_scope is False


def test_exp48_exam_verdict_unchanged():
    if not EXP48.is_dir():
        pytest.skip("exp48 archive absent")
    rep = scan_run(EXP48, repo_root=ROOT)
    assert rep.repo_in_scope is False
    # C0012's answer-key read is content-based, never allowlist-gated
    assert any("key" in h.label.lower() for h in rep.confirmed), \
        "exp48 lost its key-access detection"


def test_an_absolute_target_under_the_recorded_root_is_a_code_review(tmp_path):
    """THE GATE THAT NOTHING ELSE REACHES (added in the MERGE round
    2026-10-03, because the delivered fix widened `confined` and no test
    executed the widening -- an addition nothing reaches is this project's
    top defect class).

    `resolve_target_dirs` already rescues a RELATIVE target record by
    resolving it against the live root, which is why run 1b reads in-scope
    from any checkout. It cannot rescue an ABSOLUTE target record written
    under the PRODUCING machine's repository root: on a relocated scan that
    directory is under neither the live root nor any staged directory, so the
    live-root-only confinement test calls a code review a confined EXAM,
    takes the repository off the allowlist, and reproduces the same
    false-positive storm the pin exists to stop.

    ANTI-VACUITY is the first assertion: the target must NOT be under the
    live root, or the recorded-root disjunct is not what is being measured.
    """
    live = tmp_path / "relocated_checkout"
    (live / "bench").mkdir(parents=True)
    recorded = tmp_path / "Users" / "originaluser" / "Repo"
    (recorded / "bench").mkdir(parents=True)
    run = tmp_path / "run"
    run.mkdir()
    (run / "runner_state.json").write_text(json.dumps({
        "target_file": str(recorded / "bench" / "widget.py"),
        "panel_confinement": {"run_root": str(recorded)}}))
    (run / "r0_seat.json").write_text(json.dumps({
        "falsifier": "open('%s/scripts/helper.py')" % recorded}))

    rep = scan_run(run, repo_root=live)
    assert rep.target_dirs == [str(recorded / "bench")]
    assert not any(d.startswith(str(live)) for d in rep.target_dirs), (
        "ANTI-VACUITY: the target resolved under the LIVE root, so the "
        "recorded-root disjunct is not the thing on test")
    assert rep.run_root_recorded == str(recorded)
    assert rep.repo_in_scope is True, (
        "a code review whose target_file was recorded as an absolute path "
        "was classified as a confined exam after relocation")
    assert not [h for h in rep.confirmed if h.label.startswith("out-of-scope")], (
        [(h.file, h.label) for h in rep.confirmed])

    # MUTATION CONTROL. Neutralise the recorded root and the same archive
    # must flip to confined -- otherwise this test would pass with the
    # widening deleted, which is the guard-that-cannot-fail shape mutation
    # testing caught in a seat's own fixture on 2026-10-02.
    import bench.key_access_forensics as _kf
    _orig = _kf.discover_run_root
    _kf.discover_run_root = lambda _d: None
    try:
        mutated = _kf.scan_run(run, repo_root=live)
    finally:
        _kf.discover_run_root = _orig
    assert mutated.repo_in_scope is False, (
        "the widened confinement test is not load-bearing here")


def test_an_exam_staged_outside_the_recorded_root_stays_confined(tmp_path):
    """THE OTHER DIRECTION, and the reason the widening is safe. Same shape
    as the test above except the target is staged OUTSIDE the recorded root,
    which is how every exam run is staged -- it must still come out
    confined, and a read of the recorded root must still be CONFIRMED."""
    live = tmp_path / "relocated_checkout"
    (live / "bench").mkdir(parents=True)
    recorded = tmp_path / "Users" / "originaluser" / "Repo"
    (recorded / "bench").mkdir(parents=True)
    staged = tmp_path / "Users" / "originaluser" / "review_targets"
    staged.mkdir(parents=True)
    run = tmp_path / "run"
    run.mkdir()
    (run / "runner_state.json").write_text(json.dumps({
        "target_file": str(staged / "paper.md"),
        "panel_confinement": {"run_root": str(recorded)}}))
    (run / "r0_seat.json").write_text(json.dumps({
        "falsifier": "open('/Users/originaluser/Repo/configs/exam_prereg.json')"}))

    rep = scan_run(run, repo_root=live)
    assert rep.run_root_recorded == str(recorded)
    assert rep.repo_in_scope is False
    assert any(h.label.startswith("out-of-scope") for h in rep.confirmed), (
        "a confined exam read the repository that holds the exam design and "
        "the widened confinement test let it through")
