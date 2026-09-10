"""The FFAFP stop criterion is the project's own two-sided gate, not a judgement.

Founder instruction 2026-09-10, verbatim: *"f everything (FFAFP in cyclic mode
until diminishing returns, as per our maths model, which you should refer to and
use)"*.

Until `scripts/ffafp_cycle_gamma_2026-09-10.py`, "diminishing returns" was
ASSERTED. The machinery to decide it has been live for months -- `_estimate_gamma`
and the two-sided gate -- and the standing directive in `.claude/CLAUDE.md` says
gamma is load-bearing and must not be demoted. An assistant declaring a cycle
converged from intuition was demoting it by omission.

THE GATE IS TWO-SIDED AND THESE TESTS EXIST TO KEEP IT THAT WAY. Founder ruling
2026-06-10: convergence needs gamma >= 0.30 AND K consecutive zero-discovery
rounds. Either alone is insufficient, and the failure mode of gamma alone is the
one the directive names -- a flattened curve read as an exhausted problem while
discovery continues. Scored on its own series tonight, the assistant's work gives
gamma 0.598 with findings still arriving: gamma side PASS, count side FAIL,
verdict KEEP GOING.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "cyc", REPO / "scripts" / "ffafp_cycle_gamma_2026-09-10.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

from bench.reference_runner_v3 import _estimate_gamma  # noqa: E402


def test_it_uses_the_projects_own_estimator_rather_than_a_copy():
    """A second copy of the decay maths would drift from the one gating runs."""
    src = (REPO / "scripts" / "ffafp_cycle_gamma_2026-09-10.py").read_text()
    assert "from bench.reference_runner_v3 import _estimate_gamma" in src
    assert "def _estimate_gamma" not in src, "the estimator has been re-implemented"


def test_its_thresholds_match_the_runners():
    """0.30 and K=3 are the runner's defaults, not numbers chosen here."""
    from bench.reference_runner_v3 import RunnerConfig
    cfg = RunnerConfig(test_article="x")
    assert C.GAMMA_THRESHOLD == cfg.gamma_alt_threshold, (
        f"the cycle gate uses {C.GAMMA_THRESHOLD} while the runner converges at "
        f"{cfg.gamma_alt_threshold}")
    assert C.K_ZERO == 3


@pytest.mark.parametrize("counts,expected", [
    ([3, 3, 3, 3, 3, 3], "KEEP GOING"),      # constant discovery, gamma 0
    ([8, 4, 2, 1, 1, 0], "KEEP GOING"),      # decaying but still finding
    ([8, 4, 2, 0, 0, 0], "CONVERGED"),       # both sides hold
    ([5, 0, 0, 0, 0, 0], "CONVERGED"),
    ([11, 4, 2], "KEEP GOING"),              # the assistant's own series tonight
])
def test_the_gate_verdicts(counts, expected):
    assert C.gate(counts)[3] == expected


def test_gamma_alone_never_converges():
    """THE DIRECTIVE'S OWN FAILURE MODE, pinned.

    A series can flatten hard while discovery continues. If a future edit drops
    the count side, this goes red rather than silently converging early."""
    counts = [50, 1, 1, 1, 1, 1]
    gamma, gside, cside, verdict = C.gate(counts)
    assert gside, f"the fixture must pass the gamma side to be meaningful (got {gamma})"
    assert not cside
    assert verdict == "KEEP GOING", (
        "a flattened curve with findings still arriving converged on gamma alone")


def test_the_count_side_alone_never_converges():
    """The other half of the same property.

    Three zero rounds after constant discovery still leaves gamma below the
    threshold, and the gate must refuse."""
    counts = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0]
    gamma, gside, cside, verdict = C.gate(counts)
    assert cside, "the fixture must pass the count side to be meaningful"
    assert not gside, f"the fixture must FAIL the gamma side (got {gamma})"
    assert verdict == "KEEP GOING"


def test_too_few_passes_cannot_converge():
    """`_estimate_gamma` returns 0.0 below min_rounds, so 2 clean passes are not
    a convergence. The insurance endpoint needs 3."""
    assert C.gate([0, 0])[3] == "KEEP GOING"


def test_the_series_file_exists_and_parses():
    """It survives compaction only if it is on disk and committed."""
    import json
    assert C.SERIES.is_file(), f"{C.SERIES} is missing"
    d = json.loads(C.SERIES.read_text())
    assert d.get("passes"), "the series records no passes"
    assert all(isinstance(p.get("findings"), int) for p in d["passes"])


def test_the_recorded_series_is_not_yet_converged():
    """THE HONEST STATE, asserted so it cannot quietly be claimed otherwise.

    If this fails because the cycle genuinely converged, replace it with an
    assertion of the new state and say which pass closed it. Do not delete it."""
    import json
    counts = [p["findings"] for p in json.loads(C.SERIES.read_text())["passes"]]
    assert C.gate(counts)[3] == "KEEP GOING", (
        "the recorded cycle now converges; update this test deliberately")
