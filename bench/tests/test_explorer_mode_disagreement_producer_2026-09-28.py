"""The producer behind the figure quoted in the PUBLIC explorer page.

WHY IT IS GUARDED. `explorer/index.html` quotes 96.9677% in its comments and names
`scripts/explorer_mode_disagreement_2026-09-28.py` as the producer. Twice on
2026-09-28 a figure reached that same public page with NO producer at all -- first
`1268 of 3249`, which a panel seat could not reproduce from ~10 grids, then
`89.2328%`, computed in an uncommitted heredoc. A producer that silently reports
the wrong thing is worse than no producer, because it launders a bad number.

WHAT IS ASSERTED. Not the RATE -- that moves with the page's shipped thetas, and
pinning it would make this a tripwire on an intended change. What must hold is that
the producer EXECUTES THE PAGE and REFUSES rather than guesses:
  - it reads the thetas from the page's MODE table, not from its own constants;
  - it aborts if `stopPass()` is gone, instead of re-implementing it;
  - it reports its denominator convention, because 4 parties measured this quantity
    on 2026-09-28 and got 26%, 68%, 89% and 96.97% purely from protocol differences.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "explorer_mode_disagreement_2026-09-28.py"
PAGE = ROOT / "explorer" / "index.html"


def _run(page: Path = PAGE, timeout: int = 300):
    if not shutil.which("node"):
        pytest.skip("node is not installed; the page's own JS cannot be executed")
    return subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                          capture_output=True, text=True, timeout=timeout)


class TestItExecutesThePageRatherThanItsOwnCopy:
    def test_it_reports_the_thetas_it_read_from_the_page(self):
        r = _run()
        assert r.returncode == 0, r.stderr[:300]
        page = PAGE.read_text(encoding="utf-8")
        tp = float(re.search(r"prospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+)", page).group(1))
        tr = float(re.search(r"retrospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+)", page).group(1))
        assert f"prospective {tp}" in r.stdout, r.stdout
        assert f"retrospective {tr}" in r.stdout, r.stdout

    def test_it_states_its_denominator_convention(self):
        """4 parties, 4 numbers, all from protocol. The protocol must be printed."""
        r = _run()
        assert "both modes named a stop" in r.stdout
        assert "theta protocol" in r.stdout
        assert "grid" in r.stdout

    def test_every_proportion_carries_a_confidence_interval(self):
        r = _run()
        assert "Wilson 95%" in r.stdout
        assert "Clopper-Pearson 95%" in r.stdout

    def test_it_refuses_when_the_page_loses_stopPass(self, tmp_path, monkeypatch):
        """ABORT, DO NOT RE-IMPLEMENT. The single most repeated defect of the day
        was a probe quietly substituting its own copy of the page's logic."""
        broken = PAGE.read_text(encoding="utf-8").replace(
            "function stopPass(steps, theta, gain){", "function stopPassRENAMED(steps, theta, gain){")
        backup = PAGE.read_text(encoding="utf-8")
        PAGE.write_text(broken, encoding="utf-8")
        try:
            r = _run()
            assert r.returncode != 0, (
                "the producer completed with stopPass() absent from the page -- it is "
                "using its own copy of the stop rule somewhere"
            )
            assert "stopPass" in (r.stderr + r.stdout)
        finally:
            PAGE.write_text(backup, encoding="utf-8")

    def test_the_page_actually_cites_this_producer(self):
        """A producer nothing points at is an unwired addition."""
        page = PAGE.read_text(encoding="utf-8")
        assert SCRIPT.name in page, (
            f"{SCRIPT.name} is not named in the page whose figure it produces"
        )
