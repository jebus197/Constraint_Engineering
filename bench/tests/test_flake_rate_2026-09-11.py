"""The audit that counted a flake had the defect it was counting.

I38's issues-log row said "1 failure in 4 full-size runs". The re-count grepped
`^FAILED` across the archived suite logs and returned **0** -- those lines are
indented by 2 spaces, because the logs were piped through `sed 's/^/  /'` when
they were written, so the anchor could not match and 2 real failures read as
none. A scanner that resolves one form of a thing and reports a false zero for
the other is this session's recurring defect, and this instance sat inside the
instrument built to count that defect.

The corrected figure is **2 of 6 full-size runs, 33.3333%, Wilson [9.6771%,
70.0007%], Clopper-Pearson [4.3272%, 77.7222%]**, and both failures were clones:
2 of 5 against 0 of 1 working-tree run, Fisher exact p = 1.0000, which describes
the runs rather than establishing a cause.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "flake_rate_2026-09-11.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("flake_rate", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheAnchorDefect:
    def test_an_indented_failure_line_is_matched(self, mod):
        """THE DEFECT ITSELF. This is how every archived log is written."""
        assert mod._failed_the_test(f"  FAILED {mod.TEST}\n")

    def test_a_bare_failure_line_is_matched(self, mod):
        """POSITIVE CONTROL: the unanchored pattern must not have become so
        loose that it stopped matching pytest's own output format."""
        assert mod._failed_the_test(f"FAILED {mod.TEST}\n")

    def test_a_passing_log_is_not_matched(self, mod):
        """ANTI-VACUITY. A matcher that returned True always would pass both
        tests above and make every run a failure."""
        assert not mod._failed_the_test("7104 passed, 2 failed in 1987.09s\n")
        assert not mod._failed_the_test(f"  {mod.TEST} PASSED\n")


class TestTheCensusIsTheEvidence:
    def test_the_census_is_committed(self):
        assert mod_census().exists(), (
            "the census is not committed, so the figure in the issues log lives "
            "only as prose -- which is what `measured-rate-travels-with-its-script` "
            "forbids")
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch",
             str(mod_census().relative_to(REPO))],
            cwd=REPO, capture_output=True, text=True)
        assert tracked.returncode == 0, "the census exists but is not tracked"

    def test_it_reproduces_the_figure_quoted_in_the_issues_log(self, mod):
        """PARSED FROM THE NOTE, NOT PINNED IN THE TEST.

        This asserted `(k, n) == (2, 6)` with 4 hard-coded interval bounds, and
        went red the moment a 7th and 8th run were censused -- over a corpus that
        grows by design. Pinning an absolute figure over a growing corpus is the
        staleness trap this project named in entry 6.1 and then walked into here.

        The DURABLE invariant is that the producer and the note agree. Reading
        the figure out of the note and recomputing it enforces exactly that, and
        cannot go stale: if either moves without the other, this fails.
        """
        rows = json.loads(mod_census().read_text(encoding="utf-8"))
        r = mod.rate(rows)
        note = (REPO / "experimental_notes" / "ISSUES_LOG_2026-09-09.md").read_text(
            encoding="utf-8")
        m = re.search(r"\*\*(\d+) failures? in (\d+) full-size runs, "
                      r"([\d.]+)%, Wilson \[([\d.]+)%, ([\d.]+)%\]", note)
        assert m, "the issues log no longer states the figure in the expected form"
        k, n = int(m.group(1)), int(m.group(2))
        assert (r["k"], r["n"]) == (k, n), (
            f"the producer says {r['k']} of {r['n']} and the issues log says "
            f"{k} of {n}; one of them has drifted")
        assert abs(100 * r["k"] / r["n"] - float(m.group(3))) < 5e-5
        assert abs(100 * r["wilson"][0] - float(m.group(4))) < 5e-5
        assert abs(100 * r["wilson"][1] - float(m.group(5))) < 5e-5

    def test_the_census_is_not_trivially_small(self, mod):
        """ANTI-VACUITY for the test above: parsing agreement between an empty
        census and an empty claim would pass while measuring nothing."""
        rows = json.loads(mod_census().read_text(encoding="utf-8"))
        assert len(rows) >= 6, f"only {len(rows)} full-size runs censused"

    def test_both_wilson_tools_agree(self, mod):
        """The 2-tool rule, executed rather than asserted."""
        rows = json.loads(mod_census().read_text(encoding="utf-8"))
        r = mod.rate(rows)
        for a, b in zip(r["wilson"], r["wilson_mpmath"]):
            assert abs(a - b) < 1e-9, (a, b)

    def test_a_subset_run_is_not_counted(self, mod, tmp_path):
        """A partial run is not evidence about a test that only ever failed in a
        whole-suite run, and the scratch directory is full of them."""
        (tmp_path / "subset.log").write_text(f"  FAILED {mod.TEST}\n"
                                             "1 failed, 500 passed in 60s\n")
        assert mod.census_from_logs(tmp_path) == []

    def test_a_full_size_run_is_counted(self, mod, tmp_path):
        """POSITIVE CONTROL for the threshold."""
        (tmp_path / "clone_big.log").write_text(f"  FAILED {mod.TEST}\n"
                                                "1 failed, 7000 passed in 1800s\n")
        rows = mod.census_from_logs(tmp_path)
        assert len(rows) == 1 and rows[0]["i38_failed"] is True
        assert rows[0]["environment"] == "clone"


class TestItRefusesRatherThanFabricates:
    def test_the_refusal_branch_is_reachable(self, mod, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(mod, "CENSUS", tmp_path / "absent.json")
        monkeypatch.setattr(sys, "argv", ["flake_rate_2026-09-11.py"])
        assert mod.main() == 4
        assert "REFUSED" in capsys.readouterr().err

    def test_an_unknown_flag_is_refused(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--nope"], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode != 0
        assert "unrecognized arguments" in r.stderr


def mod_census() -> Path:
    return REPO / "experimental_notes" / "evidence" / "suite_runs_2026-09-11.json"
