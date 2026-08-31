"""Simulated and real records must be separated by CONSTRUCTION, not convention.

Three mechanisms, closed 2026-08-31, each pinned here:

  1. THE SOURCE. Every run resolved one path, bench/logs/immune_pipeline.log
     (immune_agents.py:3393), so the simulated panel appended straight into the
     archival record -- 363 lines across two runs on 2026-08-30. The isolation
     hook CDSFL_SHADOW_LOG_DIR existed since 2026-07-31, added when pytest was
     found dirtying the same archive; the simulated runner never set it.

  2. THE FINITE PAST. Those 363 lines are already written, and the archive is
     append-only and never edited. A sidecar declares which ranges are
     simulated, bidirectionally: a bare vendor name INSIDE a window still
     fails, and a SIM-marked line OUTSIDE every window fails too.

  3. THE FALSE POSITIVE. The stopgap that preceded the sidecar exempted
     everything before 2026-08-30 and guarded everything after. Measured: all
     363 post-boundary lines came from the two simulated runs and no real run
     had written since, so the boundary separated nothing -- it held only
     because the sim runs happened to be the sole recent writers. One real run
     appending turned the guard red and demanded a genuine ChatGPT finding be
     relabelled ChatGPT-SIM. That case is the first test below.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import test_sim_naming_and_integrity_directive as G

TOKENS = ("CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT", "Fable")
REPO = Path(__file__).resolve().parents[2]
SIM_RUNNER = REPO / "bench" / "tools" / "run_simulated_experiment.py"


def _mixed_log(tmp_path, lines, windows):
    log = tmp_path / "immune_pipeline.log"
    log.write_text("".join(lines), encoding="utf-8")
    side = tmp_path / ("immune_pipeline.log" + G.PROVENANCE_SIDECAR_SUFFIX)
    side.write_text(json.dumps({
        "artefact": "bench/logs/immune_pipeline.log",
        "simulated_windows": [{"lines": list(w)} for w in windows],
    }) + "\n", encoding="utf-8")
    return log


class TestTheSidecarIsBidirectional:

    def test_a_real_run_appending_does_not_redden_the_guard(self, tmp_path):
        """THE REGRESSION. This is what the era boundary got wrong."""
        log = _mixed_log(tmp_path, [
            "2026-08-30T16:35:29 INFO agent: CC2-SIM_F001 ok\n",
            "2026-09-02T09:14:03 INFO finding_id: ChatGPT_F002 routed\n",
        ], [(1, 1)])
        hits = G.scan_artefact(log, "bench/logs/immune_pipeline.log",
                               log.read_bytes(), TOKENS)
        assert hits == [], (
            "a REAL run appending a real vendor name outside every declared "
            "window was reported as a provenance violation: "
            + "; ".join(h.render().replace("\n", " ") for h in hits))

    def test_a_bare_vendor_name_inside_a_window_still_fails(self, tmp_path):
        log = _mixed_log(tmp_path, [
            "2026-08-31T00:00:00 INFO dispatch model: Codex done\n"], [(1, 1)])
        hits = G.scan_artefact(log, "bench/logs/immune_pipeline.log",
                               log.read_bytes(), TOKENS)
        assert any(h.token == "Codex" for h in hits), (
            "a simulated line carrying a bare vendor name passed INSIDE a "
            "declared window; the sidecar has disarmed the guard")

    def test_a_sim_line_outside_every_window_still_fails(self, tmp_path):
        """New contamination must not be licensed by an old sidecar."""
        log = _mixed_log(tmp_path, [
            "2026-09-01T00:00:00 INFO lock: Fable-SIM_F009 NEW\n"], [(99, 99)])
        hits = G.scan_artefact(log, "bench/logs/immune_pipeline.log",
                               log.read_bytes(), TOKENS)
        assert hits, "new contamination was licensed by an old sidecar"
        assert hits[0].location == "outside declared provenance window"

    def test_the_regex_catches_the_shape_this_log_actually_uses(self, tmp_path):
        """`-SIM\\b` misses `Fable-SIM_F009`: M and _ are both word chars."""
        assert re.search(r"[A-Za-z0-9]-SIM(?![A-Za-z])", "Fable-SIM_F009")
        assert not re.search(r"-SIM\b", "Fable-SIM_F009")

    def test_an_unreadable_sidecar_declares_nothing(self, tmp_path):
        log = tmp_path / "immune_pipeline.log"
        log.write_text("2026-04-11T06:27:01 INFO agent: ChatGPT_F005\n",
                       encoding="utf-8")
        (tmp_path / ("immune_pipeline.log" + G.PROVENANCE_SIDECAR_SUFFIX)
         ).write_text("{ not json\n", encoding="utf-8")
        assert G._provenance_windows(log) is None, (
            "a corrupt sidecar must declare nothing, so the file falls back to "
            "the full scan and the guard goes loud rather than quiet")


class TestTheShippedSidecarMatchesTheShippedLog:

    def _live(self):
        log = G.LOGS_DIR / "immune_pipeline.log"
        side = log.with_name(log.name + G.PROVENANCE_SIDECAR_SUFFIX)
        if not (log.is_file() and side.is_file()):
            pytest.skip("archival log or sidecar absent")
        return log, side

    def test_every_sim_marked_line_falls_inside_a_declared_window(self):
        log, _ = self._live()
        windows = G._provenance_windows(log)
        assert windows, "sidecar present but declares no windows"
        rx = re.compile(r"[A-Za-z0-9]-SIM(?![A-Za-z])")
        stray = [i for i, line in
                 enumerate(log.read_text(errors="replace").splitlines(), 1)
                 if rx.search(line)
                 and not any(lo <= i <= hi for lo, hi in windows)]
        assert not stray, f"SIM-marked lines outside every window: {stray[:10]}"

    def test_the_windows_lie_inside_the_file(self):
        log, _ = self._live()
        n = len(log.read_text(errors="replace").splitlines())
        for lo, hi in G._provenance_windows(log):
            assert 1 <= lo <= hi <= n, f"window ({lo},{hi}) outside 1..{n}"

    def test_the_live_archive_is_green(self):
        log, _ = self._live()
        hits = G.scan_artefact(log, "bench/logs/immune_pipeline.log",
                               log.read_bytes(), G.load_vendor_tokens())
        assert hits == [], "\n".join(h.render() for h in hits[:10])


class TestTheSimulatedRunnerIsolatesItsOwnLog:
    """Part 1: the windows above can only stay closed if this holds."""

    def test_the_runner_sets_the_isolation_hook(self):
        src = SIM_RUNNER.read_text(encoding="utf-8")
        assert 'os.environ["CDSFL_SHADOW_LOG_DIR"]' in src, (
            "the simulated runner no longer isolates its immune log; it will "
            "append to the archival record and the sidecar windows will grow")

    def test_it_verifies_the_hook_took_effect_rather_than_assuming(self):
        src = SIM_RUNNER.read_text(encoding="utf-8")
        assert "immune.pipeline" in src and "baseFilename" in src, (
            "the runner sets the variable but never reads back where the "
            "handler points. immune_agents resolves it at IMPORT time, so a "
            "lazy import promoted to module level makes this a silent no-op")
        assert "Refusing to start" in src, (
            "the isolation check must abort the run, not warn")

    def test_the_hook_really_redirects_the_handler(self, tmp_path):
        """Not a source grep: run it and see where the bytes would go."""
        code = ("import sys, logging; sys.path.insert(0, %r);"
                "import immune_agents;"
                "print([h.baseFilename for h in "
                "logging.getLogger('immune.pipeline').handlers])"
                % str(REPO / "bench"))
        out = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path),
                 "CDSFL_SHADOW_LOG_DIR": str(tmp_path)})
        assert str(tmp_path) in out.stdout, (
            f"CDSFL_SHADOW_LOG_DIR did not redirect the immune log.\n"
            f"stdout={out.stdout!r}\nstderr={out.stderr[-400:]!r}")

    def test_the_archive_is_where_it_goes_without_the_hook(self, tmp_path):
        """The counterfactual: without isolation it lands in the archive."""
        code = ("import sys, logging; sys.path.insert(0, %r);"
                "import immune_agents;"
                "print([h.baseFilename for h in "
                "logging.getLogger('immune.pipeline').handlers])"
                % str(REPO / "bench"))
        out = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)})
        assert "bench/logs/immune_pipeline.log" in out.stdout, (
            "the default target moved; the isolation hook may now be guarding "
            f"the wrong path. stdout={out.stdout!r}")


class TestThePatchExemptionIsNotAnEscapeHatch:

    def test_a_simulated_artefact_renamed_to_patch_still_fails_by_path(self, tmp_path):
        f = tmp_path / "Codex.patch"
        f.write_text("agent: Codex\n", encoding="utf-8")
        assert G.scan_artefact(f, "bench/logs/sim_run/Codex.patch",
                               f.read_bytes(), TOKENS), (
            "a bare vendor name in the FILENAME survived the patch exemption")

    def test_only_patch_and_diff_are_exempt(self):
        assert G._REVIEWER_PATCH_SUFFIXES == {".patch", ".diff"}


class TestTheSidecarSurvivesAFreshClone:
    """A declaration git does not carry is a declaration only this machine has."""

    def test_the_sidecar_is_not_gitignored(self):
        log = G.LOGS_DIR / "immune_pipeline.log"
        side = log.with_name(log.name + G.PROVENANCE_SIDECAR_SUFFIX)
        if not side.is_file():
            pytest.skip("no sidecar present")
        out = subprocess.run(["git", "status", "--porcelain", "--ignored",
                              str(side)], cwd=REPO, capture_output=True,
                             text=True)
        assert not out.stdout.startswith("!!"), (
            "the provenance sidecar is gitignored. bench/logs/** ignores the "
            "directory while the archival log itself is tracked, so a fresh "
            "clone would have the log without its provenance declaration: "
            "_provenance_windows returns None, the whole file is scanned, and "
            "the guard re-reports 335 violations of which 99.4% are real runs.")

    def test_the_archive_it_describes_is_tracked(self):
        log = G.LOGS_DIR / "immune_pipeline.log"
        if not log.is_file():
            pytest.skip("no archive present")
        out = subprocess.run(["git", "ls-files", "--error-unmatch", str(log)],
                             cwd=REPO, capture_output=True, text=True)
        assert out.returncode == 0, (
            "the archival immune log is no longer tracked, so the sidecar "
            "describes a file that does not travel with the repository")
