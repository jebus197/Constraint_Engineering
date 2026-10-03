#!/usr/bin/env python3
"""The discrimination control now reaches falsifiers with no corrected copy.

THE DEFECT, measured. `run_discrimination_control` can only compare a
falsifier's behaviour on the real target against a CORRECTED copy, and a
corrected copy has to be supplied. Measured over the archive: it left a record
on 44 of 567 falsifier-bearing entries, 7.7601%, Wilson [5.8313%, 10.2575%]. On
the other 523 it returned `NO_CONTROL` having decided nothing, and roughly 1 in
3 of the falsifiers it DID check turned out to be unable to fail -- so the
hazard on the unchecked 523 is not hypothetical.

WHAT BOTH PANEL SEATS REFUSED, and why this is not that. Both independently
refused a second standalone template under ADDITIVE: an unwired mechanism beside
a working one is this project's recorded 11-of-11 failure class. Both named the
same additive move instead -- synthesise the missing side so the guard that
already works reaches the whole population. That is what `invariance_probe` is.

ONE-SIDEDNESS IS THE WHOLE DESIGN. A corrected copy cannot be synthesised
without knowing the claim. A set of materially different targets can, and a
falsifier whose verdict never moves across them is not reading the target to
decide -- non-discrimination, whatever the claim was. The converse says nothing,
and the record says so in its own `limit` field.

IT RUNS AS A POST-RUN SWEEP, NOT INLINE, AND THAT IS A MEASURED DECISION. An
overlay build at the real repository root measures 14.034 s because
`panel_sandbox` recursively scans the clone for surviving secrets, so 2 overlays
per probed finding per round would add roughly 187 minutes to a run -- for a
statistic nothing in the convergence path reads. The first version of this
instrument WAS wired inline on a projection of 1.4 minutes taken from a probe
timed against a 1-file temporary directory: a 68x underestimate, and the same
"measure one member, assert the universal" shape this project has recorded 12
times. `scripts/invariance_sweep_2026-10-03.py` pays the cost once per distinct
falsifier, after the run, where it cannot perturb what it measures.

IT CANNOT COST A ROUND, which these tests assert by execution: the outcome it
reaches is in neither `DISC_INDETERMINATE` nor `DISC_FAILED`, so none of
`mechanical_fault`, `escalated` or `hil_escalated` is set by it.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    DISC_ABSENT, DISC_FAILED, DISC_INDETERMINATE, DISC_INVARIANT,
    _invariance_variants, invariance_probe, run_discrimination_control,
)

TARGET = "sample_target.py"


def _tree(tmp_path: pathlib.Path, body: str) -> pathlib.Path:
    (tmp_path / TARGET).write_text(body, encoding="utf-8")
    return tmp_path


CANNOT_FAIL = (
    "# this falsifier never reads its target\n"
    "raise AssertionError('FALSIFIED: the defect is present')\n"
)

READS_TARGET = (
    "import pathlib\n"
    "text = pathlib.Path('sample_target.py').read_text()\n"
    "assert 'BROKEN' not in text, 'FALSIFIED: the marker is present'\n"
)


class TestTheProbeItself:
    def test_the_variants_are_materially_different(self):
        v = dict(_invariance_variants("alpha\n"))
        assert v["emptied"] == ""
        assert v["duplicated"] == "alpha\nalpha\n"
        assert len(set(v.values())) == 2, (
            "two variants that are equal to each other cannot separate "
            "anything")

    def test_a_content_independent_falsifier_is_caught(self, tmp_path):
        """EXECUTED. The verdict is the same on every variant -> invariant."""
        root = _tree(tmp_path, "BROKEN marker here\n")
        rec = invariance_probe(CANNOT_FAIL, root, TARGET, "CONFIRMED",
                               kwargs={"timeout": 30})
        assert rec["ran"] is True, f"the probe did not run: {rec}"
        assert rec["invariant"] is True, (
            f"a falsifier that never reads its target was not caught: {rec}")

    def test_a_falsifier_that_reads_its_target_is_not_caught(self, tmp_path):
        """ANTI-FALSE-POSITIVE. This is the shape that must NOT be stamped."""
        root = _tree(tmp_path, "BROKEN marker here\n")
        rec = invariance_probe(READS_TARGET, root, TARGET, "CONFIRMED",
                               kwargs={"timeout": 30})
        assert rec["ran"] is True, f"the probe did not run: {rec}"
        assert rec["invariant"] is False, (
            "an honest falsifier was stamped as content-independent, which "
            f"would mint mechanical faults wholesale: {rec}")
        assert rec["variants"]["emptied"] == "REFUTED", (
            f"emptying the target did not quiet it: {rec['variants']}")

    def test_the_record_states_its_own_limit(self, tmp_path):
        root = _tree(tmp_path, "x\n")
        rec = invariance_probe(CANNOT_FAIL, root, TARGET, "CONFIRMED",
                               kwargs={"timeout": 30})
        assert "one-sided" in rec["limit"], (
            "the probe does not carry its own one-sidedness, so a reader could "
            "take variation as evidence of discrimination")

    def test_an_unreadable_target_is_reported_not_raised(self, tmp_path):
        rec = invariance_probe(CANNOT_FAIL, tmp_path, "absent.py", "CONFIRMED",
                               kwargs={"timeout": 30})
        assert rec["ran"] is False and rec["invariant"] is None, (
            f"a missing target produced a verdict it cannot support: {rec}")


class TestTheReachIsActuallyWidened:
    def test_an_entry_with_no_corrected_copy_now_gets_a_record(self, tmp_path):
        """EXECUTED through the real control, which used to return at once.

        This is the path `scripts/invariance_sweep_2026-10-03.py` drives after a
        run. `_apply_discrimination_control` still returns early on this
        population inside a round, deliberately and for the measured cost reason
        in the module docstring.
        """
        root = _tree(tmp_path, "BROKEN marker here\n")
        entry = {"falsifier_code": CANNOT_FAIL, "corrected_copy": ""}
        rec = run_discrimination_control(
            entry, repo_root=str(root), target_rel=TARGET, timeout=30)
        assert "invariance_probe" in rec, (
            "the widened path left no record at all, so reach is unchanged")
        assert rec["outcome"] == DISC_INVARIANT, (
            f"a content-independent falsifier was not named: {rec['outcome']}")
        assert "RECORDED ONLY" in rec["detail"], (
            "the detail does not say the finding is not acted on")

    def test_an_honest_falsifier_keeps_the_old_outcome(self, tmp_path):
        root = _tree(tmp_path, "BROKEN marker here\n")
        entry = {"falsifier_code": READS_TARGET, "corrected_copy": ""}
        rec = run_discrimination_control(
            entry, repo_root=str(root), target_rel=TARGET, timeout=30)
        assert rec["outcome"] == DISC_ABSENT, (
            f"the outcome changed for an honest falsifier: {rec['outcome']}")
        assert rec["invariance_probe"]["invariant"] is False


class TestItCannotCostARound:
    def test_the_new_outcome_escalates_nothing(self):
        """The property that makes widening safe on the very next run.

        `DISC_FAILED` sets mechanical_fault/escalated/hil_escalated, and every
        member of `DISC_INDETERMINATE` sets hil_escalated. Reach went from 44 to
        567; if the new outcome were in either set the HIL queue would grow by
        an unmeasured factor on first use, and an unusually high irreducible
        queue is the founder's own named signal of mechanical failure.
        """
        assert DISC_INVARIANT not in DISC_INDETERMINATE
        assert DISC_INVARIANT != DISC_FAILED
        assert DISC_INVARIANT != DISC_ABSENT, (
            "the new outcome is indistinguishable from the old one, so the "
            "measurement it exists to make cannot be made")

    def test_a_probe_that_explodes_is_recorded_not_raised(self, tmp_path,
                                                          monkeypatch):
        """A shadow instrument may never kill a round."""
        import bench.reference_runner_v3 as rr
        root = _tree(tmp_path, "x\n")

        def boom(*a, **k):
            raise RuntimeError("planted probe failure")

        monkeypatch.setattr(rr, "invariance_probe", boom)
        entry = {"falsifier_code": CANNOT_FAIL, "corrected_copy": ""}
        rec = rr.run_discrimination_control(
            entry, repo_root=str(root), target_rel=TARGET, timeout=30)
        assert rec["outcome"] == DISC_ABSENT
        assert rec["invariance_probe"]["ran"] is False
        assert "the probe itself failed" in rec["invariance_probe"]["detail"]


class TestTheSweepIsTheCaller:
    """The probe is reached by a SWEEP, and the sweep is executed here.

    Without this the probe would be a mechanism with no caller -- the project's
    recorded 11-of-11 failure class -- because the inline wiring was removed on
    a cost measurement. The sweep is run as a subprocess against a planted run
    directory, so what is tested is the script a human actually types.
    """

    def test_the_sweep_finds_a_cannot_fail_falsifier(self, tmp_path):
        import json
        import subprocess
        import sys as _sys

        run = tmp_path / "planted_run"
        run.mkdir()
        (run / "runner_state.json").write_text(json.dumps({
            "config": {"test_article": TARGET},
            "registry": {"entries": {
                "C0001": {"falsifier_code": CANNOT_FAIL, "corrected_copy": "",
                          "falsifier_verdict": "CONFIRMED"},
                "C0002": {"falsifier_code": READS_TARGET, "corrected_copy": "",
                          "falsifier_verdict": "CONFIRMED"},
                # a corrected copy means the REAL control can speak, so the
                # sweep must leave this one alone rather than double-report it
                "C0003": {"falsifier_code": READS_TARGET,
                          "corrected_copy": "fixed\n",
                          "falsifier_verdict": "CONFIRMED"},
            }}}), encoding="utf-8")

        (REPO / TARGET).write_text("BROKEN marker here\n", encoding="utf-8")
        out_json = tmp_path / "rec.json"
        try:
            p = subprocess.run(
                [_sys.executable,
                 str(REPO / "scripts" / "invariance_sweep_2026-10-03.py"),
                 "--run", str(run), "--target", TARGET,
                 "--timeout", "30", "--out", str(out_json)],
                capture_output=True, text=True, cwd=str(REPO), timeout=600)
        finally:
            (REPO / TARGET).unlink(missing_ok=True)

        assert p.returncode == 0, f"the sweep failed: {p.stderr[-800:]}"
        rec = json.loads(out_json.read_text())
        assert rec["distinct_falsifiers_without_a_corrected_copy"] == 2, (
            "the sweep did not exclude the entry the real control can speak "
            f"for: {rec['distinct_falsifiers_without_a_corrected_copy']}")
        inv = {tuple(r["cids"]): r["probe"].get("invariant") for r in rec["rows"]}
        assert inv[("C0001",)] is True, (
            f"the cannot-fail falsifier was not caught by the sweep: {inv}")
        assert inv[("C0002",)] is False, (
            f"an honest falsifier was flagged by the sweep: {inv}")
        assert "invariant=false demonstrates nothing" in rec["one_sided"]

    def test_a_limit_is_reported_rather_than_silent(self, tmp_path):
        """No silent caps: a bounded sweep must say what it did not probe."""
        import json
        import subprocess
        import sys as _sys

        run = tmp_path / "planted_run"
        run.mkdir()
        (run / "runner_state.json").write_text(json.dumps({
            "config": {"test_article": TARGET},
            "registry": {"entries": {
                f"C{i:04d}": {"falsifier_code": CANNOT_FAIL + f"# {i}\n",
                              "corrected_copy": "",
                              "falsifier_verdict": "CONFIRMED"}
                for i in range(1, 4)}}}), encoding="utf-8")
        (REPO / TARGET).write_text("BROKEN marker here\n", encoding="utf-8")
        out_json = tmp_path / "rec.json"
        try:
            p = subprocess.run(
                [_sys.executable,
                 str(REPO / "scripts" / "invariance_sweep_2026-10-03.py"),
                 "--run", str(run), "--target", TARGET, "--limit", "1",
                 "--timeout", "30", "--out", str(out_json)],
                capture_output=True, text=True, cwd=str(REPO), timeout=600)
        finally:
            (REPO / TARGET).unlink(missing_ok=True)
        assert p.returncode == 0, f"the sweep failed: {p.stderr[-800:]}"
        rec = json.loads(out_json.read_text())
        assert rec["probed"] == 1 and rec["skipped_by_limit"] == 2
        assert "SKIPPED BY --limit" in p.stdout, (
            "a bounded sweep said nothing about what it skipped, which reads "
            "as full coverage")
