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


# ---------------------------------------------------------------------------
# THE RESURGENCE DIAGNOSTIC — added 2026-09-10 after panel round 4 (CC2, F3).
#
# The finding: side (a) of the gate passed on a series that RISES for 8
# consecutive passes, because gamma is fitted to the CUMULATIVE curve and a large
# leading round makes that fit sublinear whatever the tail does. Reproduced here
# against the project's own estimator, and cross-checked at measurement time
# against an independent numpy polyfit and a scipy linregress, all 3 agreeing to
# 1e-9.
#
# GAMMA IS NOT DEMOTED AND NO THRESHOLD MOVES. The tests below pin that gamma
# still correctly REFUSES constant, linear and exponential discovery, which is
# what makes it load-bearing. What is added is a printed warning, so a passing
# gamma is never handed to a reader beside a rising tail with no cue that the two
# disagree.
# ---------------------------------------------------------------------------

def test_gamma_passes_on_a_strictly_rising_tail():
    """The finding itself. If this ever fails, the confound is gone — say so."""
    rising = [11, 1, 2, 3, 4, 5, 6, 7, 8]
    g, gside, cside, verdict = C.gate(rising)
    assert gside is True, (
        f"gamma no longer passes on a rising tail (gamma={g:.6f}); the F3 "
        f"confound may have been removed and this test should be rewritten "
        f"deliberately, not deleted")
    assert cside is False and verdict == "KEEP GOING", (
        "the count side must still refuse it — that is what saves the gate")


def test_gamma_still_refuses_the_series_it_should():
    """What makes gamma load-bearing rather than decorative."""
    for series, why in (([2] * 9, "constant discovery"),
                        (list(range(1, 10)), "linear growth"),
                        ([2 ** i for i in range(9)], "doubling")):
        g, gside, _, _ = C.gate(series)
        # NOT `g == 0.0`. The least-squares fit leaves floating-point residue:
        # constant discovery returns 1.5543122344752192e-15, which prints as
        # "0.000000" under `:.6f`. The first version of this test asserted exact
        # equality after I had read the FORMATTED value and believed it, which is
        # reading the display instead of the number. What the gate actually needs
        # is that gamma sits below the threshold.
        assert abs(g) < 1e-9, (
            f"gamma must be indistinguishable from 0 for {why}; it returned {g!r}")
        assert not gside, (
            f"side (a) must refuse {why}; it returned {g!r}")


def test_the_resurgence_warning_fires_on_a_rising_tail(capsys, monkeypatch, tmp_path):
    _run_with_series(monkeypatch, tmp_path, [11, 1, 2, 3, 4, 5, 6, 7, 8])
    out = capsys.readouterr().out
    assert "RESURGENCE" in out, (
        "a rising tail must be announced beside the passing gamma")
    assert "UNINFORMATIVE" in out and "carrying this gate" in out


def test_the_resurgence_warning_is_silent_on_a_falling_tail(capsys, monkeypatch, tmp_path):
    """The negative control: a warning that always fires says nothing."""
    _run_with_series(monkeypatch, tmp_path, [11, 9, 8, 7, 3, 2, 1, 1, 0])
    out = capsys.readouterr().out
    assert "RESURGENCE" not in out, (
        "the diagnostic fired on a falling tail, so it is not reading the series")


def test_the_live_series_triggers_it(capsys, monkeypatch, tmp_path):
    """The recorded cycle is exactly the case the finding is about."""
    import json
    counts = [p["findings"] for p in json.loads(C.SERIES.read_text())["passes"]]
    _run_with_series(monkeypatch, tmp_path, counts)
    out = capsys.readouterr().out
    if sum(counts[-3:]) > sum(counts[-6:-3]):
        assert "RESURGENCE" in out, (
            "the recorded series is in resurgence and the diagnostic stayed quiet")
    else:
        assert "RESURGENCE" not in out


def test_the_gloss_no_longer_claims_the_tail_has_flattened():
    """Rule 20/21: the document must not assert what the statistic cannot.

    This is the ONE source-text assertion in this file and it is deliberate: the
    defect was a sentence, not a behaviour. Every other test here executes.
    """
    src = C.__doc__ or ""
    # SECTION SCOPED, and the first version was not. It forbade the phrase
    # anywhere in the docstring, and the docstring QUOTES the old wording while
    # explaining why it was wrong — so the check could not tell a phrase being
    # used from a phrase being cited. A document-wide search is the wrong
    # instrument for a question about one line, which is the same correction the
    # panel-brief validator needed on 2026-09-09.
    gate_lines = [ln for ln in src.splitlines() if ln.strip().startswith("(a) gamma")]
    assert gate_lines, "the gate definition block is gone from the docstring"
    assert not any("decay curve has flattened" in ln for ln in gate_lines), (
        "side (a)'s gloss overstates the statistic — gamma passes on a rising tail")
    assert any("CUMULATIVE" in ln for ln in gate_lines), gate_lines
    assert "NOT a claim" in src


def _run_with_series(monkeypatch, tmp_path, counts):
    """Drive `main()` against a temporary series file, never the committed one."""
    import json
    f = tmp_path / "series.json"
    f.write_text(json.dumps({
        "cycle": "fixture",
        "passes": [{"label": f"p{i}", "findings": n} for i, n in enumerate(counts, 1)],
    }))
    monkeypatch.setattr(C, "SERIES", f)
    monkeypatch.setattr(C.sys, "argv", ["ffafp_cycle_gamma"])
    assert C.main() == 0
