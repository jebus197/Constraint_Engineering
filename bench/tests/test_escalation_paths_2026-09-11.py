"""Task A7: every critical escalated to a human names the mechanism that did it.

THE ENTRY SAID 25 ACROSS 9 RUNS, WITH `exp53_control_zero_live` ACCOUNTING FOR
10. Neither reproduces, and establishing that took longer than the repair.

  No predicate returns 25. The closest -- severity >= CRITICAL_SEVERITY_THRESHOLD
  (0.7, READ from the runner, not typed) AND `hil_escalated` AND no
  `falsifier_code` -- returns 22, and reproduces the entry's OTHER family figure
  exactly (`exp55_v3_control` = 8), so it is almost certainly what was meant.

  exp53 CONTRIBUTES 0 AND CANNOT CONTRIBUTE ANY. Its 2 runs hold no
  `*_report.json` at all: findings live in `checkpoint.json` under
  `all_findings`, as a list of per-round LISTS, in a schema carrying
  `falsification_present` where the registry carries `falsifier_code`, with no
  escalation flag set anywhere. Run 1 holds exactly 10 criticals at >= 0.7 --
  which is where the entry's "10" came from. They are criticals. They are not
  escalations.

THE ENTRY EXPECTED A HOLE AND THERE IS NOT ONE. It assumed "a falsifier-gate path
let a critical escalate with no runnable check". All 22 are escalated by a NAMED,
deliberate mechanism that records its reason: 11 irreducible (the routing ladder
ran out), 8 merge deadlock, 3 stale contested challenge.

WHAT WAS ACTUALLY MISSING IS THE INSTRUMENT. `irreducible_queue_count` counts
only the first of those -- correctly, its docstring scopes it to the ladder
running out -- so an audit keying on that one flag reports 11 of 22 as
unaccounted, and "no falsifier" gets read as "no reason".

AND THE COVERAGE CHECK FOUND A SEVENTH PATH ON ITS FIRST EXECUTION, which no
census could have found because it has never fired on a critical without a
falsifier: `escalate_stale_contested` has TWO escalating branches and the
CONTESTED one was unrecognised. That is the value of comparing the table against
the runner instead of against the archive.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "escalation_paths_2026-09-11.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("esc", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["esc"] = m
    spec.loader.exec_module(m)
    return m


class TestTheThresholdIsReadNotTyped:
    def test_it_matches_the_runner(self, mod):
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert f"CRITICAL_SEVERITY_THRESHOLD = {mod.critical_threshold()}" in src


class TestEveryEscalationSiteLeavesAMarker:
    def test_no_site_is_unrecognisable(self, mod):
        gaps = mod.uncovered_escalation_sites()
        assert not gaps, (
            f"these runner sites escalate a finding to a human and leave nothing "
            f"the path table can recognise, so anything they produce is reported "
            f"ANONYMOUS: {gaps}")

    def test_the_check_can_fire(self, mod, tmp_path, monkeypatch):
        """POSITIVE CONTROL. A comparator that cannot report a gap is not one.

        This is the check that FOUND the seventh path; if it silently stopped
        working, the table would drift behind the runner unnoticed.
        """
        fake = tmp_path / "bench"
        fake.mkdir()
        (fake / "reference_runner_v3.py").write_text(
            "def f(entry):\n"
            "    entry[\"hil_escalated\"] = True\n"
            "    entry[\"hil_reason\"] = \"something new nobody named\"\n",
            encoding="utf-8")
        monkeypatch.setattr(mod, "REPO", tmp_path)
        gaps = mod.uncovered_escalation_sites()
        assert len(gaps) == 1, gaps

    def test_the_runner_really_has_several_sites(self, mod):
        """ANTI-VACUITY. If the runner escalated from 1 place, the coverage
        check would be trivial."""
        import re
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        n = len(re.findall(r'\["hil_escalated"\]\s*=\s*True', src))
        assert n >= 5, f"only {n} escalation site(s) found; the scan has broken"


class TestNoArchivedEscalationIsAnonymous:
    def test_every_one_names_its_path(self, mod):
        thr = mod.critical_threshold()
        rows = mod.escalated_without_a_falsifier(thr)
        assert rows, "no escalated criticals found at all; the scan has broken"
        anon = [(r[0], r[1], r[4]) for r in rows if not r[3]]
        assert not anon, (
            f"escalated to a human, no falsifier, and no recognised mechanism: "
            f"{anon}")

    def test_the_population_is_the_one_the_entry_meant(self, mod):
        """The predicate is pinned to the family figure it reproduces, so a
        later change to the predicate cannot quietly move the population."""
        rows = mod.escalated_without_a_falsifier(mod.critical_threshold())
        fams = {}
        for run, _c, _s, _n, _w in rows:
            fams[run.split("_2026")[0]] = fams.get(run.split("_2026")[0], 0) + 1
        assert fams.get("exp55_v3_control") == 8, (
            f"the predicate no longer reproduces the entry's one checkable "
            f"family figure, exp55_v3_control = 8: {fams}")

    def test_exp53_cannot_contribute(self):
        """The entry credits exp53 with 10. Its runs hold no report at all."""
        runs = sorted((ROOT / "bench" / "logs").glob("exp53_control_zero_live_*"))
        assert runs, "exp53 has vanished from the archive -- standing directive"
        for r in runs:
            assert not list(r.glob("*_report.json")), (
                f"{r.name} now has a report; the exp53 finding needs re-deriving")
            assert (r / "checkpoint.json").is_file()


class TestTheScriptRuns:
    def test_it_exits_zero_and_states_its_boundary(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-600:] + r.stderr[-400:]
        assert "DOES NOT REPRODUCE" in r.stdout
        assert "DISPOSITION IS THE FOUNDER'S" in r.stdout, (
            "the script no longer says the backlog decision is not its to make")
