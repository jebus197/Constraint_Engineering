"""The two record-only instruments added 2026-08-23, and what they must refuse to say.

Both exist because of an observation the project could not otherwise act on:

  * The harness-defect ledger answers Fable's Q3 dissent -- "demonstrably closer to
    iron-clad" needs a defects-per-run curve, and nothing tracked one.
  * The competence-provenance check answers the FOUNDER's observation, which neither
    external reviewer raised: measured competence is wired into `bench/routing.py`,
    so a contaminated confirm rate re-orders which model resolves the hardest
    findings. It is not a reporting statistic.

Both are RECORD ONLY. Nothing reads either to make a decision, and these tests pin
that as much as they pin the arithmetic.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / f"scripts/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RATE = _load("harness_defect_rate")
PROV = _load("competence_provenance")


class TestTheDefectRateRefusesToOverclaim:
    def test_gamma_is_none_below_three_points(self):
        assert RATE.duane_gamma([3]) is None
        assert RATE.duane_gamma([3, 7]) is None, (
            "two points fit any line exactly; a slope there is arithmetic, not evidence")

    def test_gamma_is_computed_at_three(self):
        assert RATE.duane_gamma([5, 8, 9]) is not None

    def test_a_saturating_series_gives_positive_gamma(self):
        """Discovery slowing -> gamma > 0, the same sign convention as the runner."""
        assert RATE.duane_gamma([10, 14, 16, 17, 17]) > 0

    def test_a_constant_rate_gives_gamma_near_zero(self):
        g = RATE.duane_gamma([5, 10, 15, 20, 25])
        assert abs(g) < 0.05, f"a flat discovery rate must not read as convergence: {g}"

    def test_the_ledger_on_disk_is_valid_and_declares_its_own_limits(self):
        d = json.loads((REPO / "experimental_notes/data/harness_defect_ledger.json").read_text())
        assert d["entries"], "ledger is empty"
        for e in d["entries"]:
            assert "reconstructed" in e, f"{e['occasion']} does not declare its provenance"
            for x in e["defects"]:
                assert {"id", "what", "author", "finder"} <= set(x), x.get("id")
        ids = [x["id"] for e in d["entries"] for x in e["defects"]]
        assert len(ids) == len(set(ids)), "duplicate defect ids"


class TestAConfirmRateIsNotACompetenceMeasure:
    def test_detached_falsifiers_are_recognised(self):
        assert PROV.falsifier_style("f_s = 200\nassert f_s > 100\n") == "detached"

    @pytest.mark.parametrize("code", [
        'open("t.md").read()',
        'pathlib.Path("t.md").read_text()',
        'import linecache; linecache.getlines("t.md")',
    ])
    def test_readers_are_recognised_including_linecache(self, code):
        assert PROV.falsifier_style(code) == "reads", (
            "linecache reads a file with none of the usual words; CC2 used exactly this "
            "as a counterexample to a source-scanning detachment test")

    def test_absent_falsifier_is_its_own_category(self):
        assert PROV.falsifier_style("") == "none"
        assert PROV.falsifier_style(None) == "none"

    def test_exp55_is_flagged_unsafe_to_rank_on(self, capsys, monkeypatch):
        rep = sorted(REPO.glob("bench/logs/exp55_v3_control_*/*_report.json"))
        if not rep:
            pytest.skip("no exp55 report in this checkout")
        monkeypatch.setattr(PROV.sys, "argv", ["x", str(rep[-1])])
        rc = PROV.main()
        out = capsys.readouterr().out
        assert rc == 2, "a run whose only confirmations are detached must exit non-zero"
        assert "UNSAFE TO RANK ON" in out

    def test_the_routing_order_carries_the_warning(self):
        """The guard is a comment; a comment that gets deleted is the failure mode."""
        src = (REPO / "bench/routing.py").read_text()
        assert "DO NOT RE-DERIVE THIS ORDER" in src
        assert "competence_provenance.py" in src, (
            "the warning must name the check that enforces it, or it is only a wish")

    def test_nothing_imports_either_script_into_the_runner(self):
        """RECORD ONLY. If this fails, one of them has become load-bearing."""
        runner = (REPO / "bench/reference_runner_v3.py").read_text()
        for name in ("harness_defect_rate", "competence_provenance"):
            assert name not in runner, f"{name} is record-only and must not drive the runner"
