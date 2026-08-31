"""The era split and the patch exemption must not disarm the guard.

Written 2026-08-31 as the falsification pass on the append-only-log fix in
test_sim_naming_and_integrity_directive.py. Both changes EXEMPT things, and an
exemption in a provenance guard is the dangerous direction: the failure that
matters is a simulated record passing as real. Each test below tries to get a
simulated violation past the guard.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import test_sim_naming_and_integrity_directive as G

TOKENS = ("CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT")


class TestTheEraSplitCannotExemptASimulatedLine:

    def test_a_bare_vendor_after_the_boundary_still_fails(self, tmp_path):
        log = tmp_path / "immune_pipeline.log"
        log.write_text(
            "2026-04-11T06:27:01 INFO classifier: ChatGPT_F005 ok\n"
            "2026-08-31T02:02:37 INFO agent: Codex_F004 locked\n",
            encoding="utf-8")
        era = G.simulation_era_lines(log.read_bytes())
        hits = G.scan_artefact(log, "bench/logs/immune_pipeline.log", era, TOKENS)
        assert any(h.token == "Codex" for h in hits), (
            "a bare vendor name written during the simulation era passed the "
            "guard; the era slice has disarmed it")

    def test_the_pre_era_line_is_the_one_exempted(self, tmp_path):
        log = tmp_path / "immune_pipeline.log"
        log.write_text(
            "2026-04-11T06:27:01 INFO agent: ChatGPT_F005 ok\n"
            "2026-08-31T02:02:37 INFO agent: Fable-SIM_F002 done\n",
            encoding="utf-8")
        era = G.simulation_era_lines(log.read_bytes()).decode()
        assert "2026-04-11" not in era
        assert "2026-08-31" in era

    def test_a_line_exactly_on_the_boundary_is_guarded_not_exempt(self, tmp_path):
        """Midnight of the boundary day is INSIDE the era: >=, never >."""
        log = tmp_path / "immune_pipeline.log"
        log.write_text("2026-08-30T00:00:00 INFO agent: Codex_F001 x\n"
                       "2026-08-30T00:00:01 INFO agent: CC2_F002 y\n",
                       encoding="utf-8")
        era = G.simulation_era_lines(log.read_bytes())
        assert era.decode().count("2026-08-30") == 2
        assert G.scan_artefact(log, "bench/logs/immune_pipeline.log", era, TOKENS)

    def test_a_file_that_is_not_a_timestamped_log_is_scanned_whole(self, tmp_path):
        """Returning None is what routes an ordinary artefact to the full scan."""
        f = tmp_path / "round_03.json"
        f.write_text('{"agent": "Codex", "simulated": true}\n', encoding="utf-8")
        assert G.simulation_era_lines(f.read_bytes()) is None

    def test_an_unstamped_continuation_inherits_the_line_above(self, tmp_path):
        """A traceback under an era line must not fall out of the era."""
        log = tmp_path / "immune_pipeline.log"
        log.write_text(
            "2026-08-31T02:02:37 INFO agent: begin\n"
            "    continuation naming Codex\n"
            "2026-08-31T02:02:38 INFO agent: end\n"
            "2026-08-31T02:02:39 INFO agent: end\n"
            "2026-08-31T02:02:40 INFO agent: end\n"
            "2026-08-31T02:02:41 INFO agent: end\n"
            "2026-08-31T02:02:42 INFO agent: end\n"
            "2026-08-31T02:02:43 INFO agent: end\n"
            "2026-08-31T02:02:44 INFO agent: end\n"
            "2026-08-31T02:02:45 INFO agent: end\n"
            "2026-08-31T02:02:46 INFO agent: end\n"
            "2026-08-31T02:02:47 INFO agent: end\n"
            "2026-08-31T02:02:48 INFO agent: end\n"
            "2026-08-31T02:02:49 INFO agent: end\n"
            "2026-08-31T02:02:50 INFO agent: end\n"
            "2026-08-31T02:02:51 INFO agent: end\n"
            "2026-08-31T02:02:52 INFO agent: end\n"
            "2026-08-31T02:02:53 INFO agent: end\n"
            "2026-08-31T02:02:54 INFO agent: end\n"
            "2026-08-31T02:02:55 INFO agent: end\n",
            encoding="utf-8")
        era = G.simulation_era_lines(log.read_bytes()).decode()
        assert "continuation naming Codex" in era


class TestThePatchExemptionIsNotAnEscapeHatch:

    def test_a_simulated_artefact_renamed_to_patch_still_fails_by_path(self, tmp_path):
        f = tmp_path / "Codex.patch"
        f.write_text("agent: Codex\n", encoding="utf-8")
        hits = G.scan_artefact(f, "bench/logs/sim_run/Codex.patch", f.read_bytes(),
                               TOKENS)
        assert hits, ("a bare vendor name in the FILENAME survived the patch "
                      "exemption; only the body is exempt")

    def test_only_patch_and_diff_are_exempt(self):
        assert G._REVIEWER_PATCH_SUFFIXES == {".patch", ".diff"}, (
            "the exemption widened; every added suffix is a new way for a "
            "simulated artefact to avoid the body scan")

    def test_a_json_artefact_is_still_body_scanned(self, tmp_path):
        f = tmp_path / "round.json"
        f.write_text('{"agent": "Codex"}\n', encoding="utf-8")
        assert G.scan_artefact(f, "bench/logs/sim/round.json", f.read_bytes(),
                               TOKENS)


class TestTheBoundaryIsAnchoredInEvidence:

    def test_the_boundary_predates_every_simulated_artefact(self):
        """No simulated artefact may exist before the era begins, or the split
        would exempt a genuinely simulated record."""
        import re
        earliest = None
        for f in G.LOGS_DIR.rglob("*"):
            if not f.is_file():
                continue
            rel = str(f.relative_to(G.LOGS_DIR))
            try:
                sim = G.name_marks_simulated(rel) or G.content_marks_simulated(
                    f.read_bytes())
            except OSError:
                continue
            if not sim:
                continue
            m = re.search(r"(\d{8})T(\d{6})Z", rel)
            if m:
                stamp = m.group(1) + m.group(2)
                if earliest is None or stamp < earliest:
                    earliest = stamp
        if earliest is None:
            pytest.skip("no timestamped simulated artefact present")
        assert earliest >= G.SIMULATION_ERA_BEGINS.strftime("%Y%m%d%H%M%S"), (
            f"a simulated artefact at {earliest} predates the era boundary "
            f"{G.SIMULATION_ERA_BEGINS}; every line it wrote is being exempted")
