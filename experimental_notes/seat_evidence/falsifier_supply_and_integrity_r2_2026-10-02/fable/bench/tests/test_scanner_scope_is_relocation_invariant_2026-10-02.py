# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 30d576817a905967f07f12235117f051889035b2b0ed010cd15e9ae171ad2407
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""An archived run's scope verdict must not depend on which machine re-scans it.

FOUND 2026-10-02, BY EXECUTING THE COMMITTED MEASUREMENT. The brief for the
integrity merge declared "run 1b 0 advisory / 7 audit", and
`scripts/advisory_channel_selection_2026-10-02.py` asserts exactly that. Run
in a relocated checkout (a panel sandbox, CI, any machine that is not the
founder's), it CRASHES: 107 advisory / 7 audit, every one of the 107 an
`out-of-scope path opened` hit on a falsifier body in `checkpoint.json` that
opens `/Users/georgejackson/.../bench/...` -- the ORIGINAL machine's repo
root. On the original machine those literals sit under the current repo root
and are in scope; relocated, the same bytes are out of scope, so the advisory
fires on a clean archived run and the committed measurement does not
re-execute. A measurement that is true on exactly one machine is pinned, not
committed.

THE REPAIR, held here: when the repository is in scope (a code review --
`confined` is False), a path literal whose longest existing suffix resolves
under the CURRENT repo root is in scope: it names content the panel may read
anyway, spelled with another machine's prefix. The remap is OFF for a
confined exam run, protected key paths still lose first, and a literal whose
suffix exists nowhere under the repo stays CONFIRMED -- misclassification
still fails toward reporting.

EXECUTE, DO NOT GREP: every case runs scan_run on a synthetic run directory.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.key_access_forensics import scan_run  # noqa: E402

FOREIGN = "/Users/somebodyelse/Development/Constraint_Engineering"


def _mk_run(tmp_path: Path, target_file: str, log_line: str) -> Path:
    run = tmp_path / "fake_run"
    run.mkdir()
    (run / "runner_state.json").write_text(json.dumps(
        {"experiment": "t", "target_file": target_file,
         "registry": {"entries": {}}}))
    (run / "round1.log").write_text(log_line)
    return run


class TestRelocatedCodeReview:
    def test_foreign_prefix_repo_suffix_is_in_scope(self, tmp_path):
        """The run-1b shape: a falsifier body opening the ORIGINAL machine's
        copy of a file this repository contains. In a code review the panel
        may read that file; the foreign prefix is relocation, not egress."""
        run = _mk_run(
            tmp_path, "bench/x.md",
            f'code = open("{FOREIGN}/bench/falsifier_verify.py").read()\n')
        rep = scan_run(run, repo_root=ROOT)
        assert rep.repo_in_scope, "a relative target_file is a code review"
        hits = [h for h in rep.advisory_confirmed
                if h.label == "out-of-scope path opened or listed"]
        assert not hits, (
            "a relocated checkout fired the advisory on a path literal whose "
            f"suffix exists under the current repo root: {hits[:3]}")

    def test_foreign_path_with_no_repo_counterpart_stays_confirmed(
            self, tmp_path):
        """The remap must FAIL TOWARD REPORTING: a foreign literal whose
        suffix exists nowhere under this repository is still an egress."""
        run = _mk_run(
            tmp_path, "bench/x.md",
            'data = open("/Users/somebodyelse/secrets/notes_xyzzy_77.txt")\n')
        rep = scan_run(run, repo_root=ROOT)
        assert any(h.label == "out-of-scope path opened or listed"
                   for h in rep.advisory_confirmed), (
            "a foreign path with no counterpart in this repository was "
            "scored in scope -- the remap widened past relocation")

    def test_an_answer_key_literal_is_confirmed_regardless(self, tmp_path):
        """The key-path signal is content-based and must survive the remap."""
        run = _mk_run(
            tmp_path, "bench/x.md",
            'k = json.load(open("/Users/x/exp99_answer_key.json"))\n')
        rep = scan_run(run, repo_root=ROOT)
        assert any("answer-key" in h.label for h in rep.advisory_confirmed)


class TestConfinedExamUnchanged:
    def test_remap_is_off_for_a_confined_exam(self, tmp_path):
        """An exam run records an ABSOLUTE staged-target path outside the
        tree; the repository is out of scope there and a repo-suffix literal
        remains exactly the evidence the 2026-07-29 audit added confinement
        to catch."""
        staged = tmp_path / "staged_targets"
        staged.mkdir()
        run = _mk_run(
            tmp_path, str(staged / "exam.md"),
            f'code = open("{FOREIGN}/bench/falsifier_verify.py").read()\n')
        rep = scan_run(run, repo_root=ROOT)
        assert not rep.repo_in_scope
        assert any(h.label == "out-of-scope path opened or listed"
                   for h in rep.advisory_confirmed), (
            "a confined exam run let a repo-suffix literal through -- the "
            "relocation remap must not apply when the repo is out of scope")


class TestTheRealRun:
    def test_run_1b_is_advisory_silent_everywhere(self):
        """The committed measurement itself: 0 advisory / 7 audit, on ANY
        machine that holds this checkout, not only the one that ran it."""
        run = (ROOT / "bench" / "logs" /
               "prose_convergence_run1b_2026-10-02_20261002T044234Z")
        if not run.is_dir():
            import pytest
            pytest.skip("run 1b is not in this checkout")
        rep = scan_run(run, repo_root=ROOT)
        assert len(rep.advisory_confirmed) == 0, (
            f"{len(rep.advisory_confirmed)} advisory hit(s) on a run that "
            "read no key -- the scope verdict is machine-dependent")
        assert len(rep.audit_confirmed) == 7


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
