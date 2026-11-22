#!/usr/bin/env python3
"""A share above half and a share that ROSE are 2 claims, and 1 does not imply the other.

GUARDS: `scripts/is_the_hash_chain_majority_real_2026-11-22.py`.

WHY IT EXISTS. On 2026-11-22 assertion A1 of
`bench/tests/test_open_brain_assessment_2026-09-10.py` was restated from
`lo < 0.5 < hi` to `lo > 0.5`, and the comment justifying that restatement
carried a Clopper-Pearson interval, a Fisher exact p-value and a Yates
chi-square p-value that **no committed script produced**. The figures reproduce
EXACTLY. That is the point rather than a mitigation: under
`measured-rate-travels-with-its-script` a correct figure with no producer is
still a figure nobody can check, so the producer was written and this guard
holds it.

★ THE PROPERTY UNDER TEST IS THE SEPARATION, NOT THE ARITHMETIC. The failure
mode this file exists to prevent is reporting a narrower interval as a rise. The
denominator grew from 231 to 266, which bought PRECISION; the share itself is
not distinguishable between the 2 measurements at the conventional level. A
producer that printed only "above half" would invite every reader to supply
"and therefore rising" for themselves, which is the shape
[[feedback_a_figure_can_answer_a_different_question]] records.

★ EVERY CASE HERE DRIVES THE MODULE'S OWN FUNCTIONS ON KNOWN INPUTS rather than
asserting on its source text, because a source-text assertion proves only that
the module describes itself consistently (`execute-do-not-grep`). The live
counts are read through a SEAM so no case depends on the Open Brain store, whose
contents change.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "bench" / "tests").is_dir() and (cand / "scripts").is_dir():
            return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()
SUBJECT = REPO / "scripts" / "is_the_hash_chain_majority_real_2026-11-22.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("hash_majority", SUBJECT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["hash_majority"] = m
    spec.loader.exec_module(m)
    return m


class TestBothIntervalsAgreeAcrossRoutes:
    """2 routes per interval, and the agreement is ASSERTED rather than hoped for."""

    def test_wilson_routes_agree(self, mod):
        (lo1, hi1), (lo2, hi2), diff = mod.wilson_two_routes(160, 266)
        assert diff < 1e-9, (
            f"the 2 Wilson routes disagree by {diff:.3e}; a cross-check that "
            f"does not agree is a finding, not a formality")
        assert lo1 == pytest.approx(0.541626, abs=1e-6)
        assert hi1 == pytest.approx(0.658492, abs=1e-6)

    def test_clopper_pearson_routes_agree(self, mod):
        (lo1, hi1), (lo2, hi2), diff = mod.clopper_two_routes(160, 266)
        assert diff < 1e-9, f"the 2 Clopper-Pearson routes disagree by {diff:.3e}"
        assert lo1 == pytest.approx(0.539926, abs=1e-6)
        assert hi1 == pytest.approx(0.660794, abs=1e-6)

    def test_the_exact_route_is_not_the_beta_route_in_disguise(self, mod):
        """ANTI-VACUITY: 2 routes that are 1 function called twice prove nothing.

        The project has already been caught by this -- `statsmodels` and `scipy`
        both resolved to 1 verifier, so the canonical 2-tool pair for a
        statistical claim was a single function called twice. The exact route
        here inverts binomial tails and must therefore disagree with the beta
        quantile SOMEWHERE in the parameter space, even if not at n = 266.
        """
        seen_any_difference = False
        for v, t in [(1, 3), (2, 5), (1, 7), (3, 4)]:
            (_l1, _h1), (_l2, _h2), d = mod.clopper_two_routes(v, t)
            if d > 0:
                seen_any_difference = True
        assert seen_any_difference, (
            "the 2 Clopper-Pearson routes agreed to the bit on every small case "
            "tried, which is what a single function called twice would do. If "
            "this ever fails, check that `clopper_two_routes` really computes 2 "
            "independent routes and has not been collapsed into one")


class TestTheSeparationOfTheTwoQuestions:
    """THE POINT OF THE FILE."""

    def test_above_half_does_not_imply_risen(self, mod, capsys, monkeypatch):
        monkeypatch.setattr(mod, "live_counts", lambda: (160, 266))
        assert mod.main() == 0
        out = capsys.readouterr().out
        assert "above half = True" in out
        assert "shown to have risen = False" in out, (
            "the live figures are above half AND not shown to have risen; a "
            "report carrying only the first invites the reader to infer the "
            "second")
        assert "not a demonstrated gain in COVERAGE" in out

    def test_a_genuinely_risen_share_is_reported_as_risen(self, mod, capsys, monkeypatch):
        """ANTI-VACUITY the other way: the 'did it rise' branch must be REACHABLE.

        A test that only ever sees False cannot tell a working comparison from a
        constant. 260 of 266 against the pinned 125 of 231 is a real rise.
        """
        monkeypatch.setattr(mod, "live_counts", lambda: (260, 266))
        assert mod.main() == 0
        out = capsys.readouterr().out
        assert "shown to have risen = True" in out
        assert "MAY NOT BE SAID" not in out, (
            "the withholding paragraph printed on a share that genuinely rose")

    def test_a_minority_is_reported_as_a_minority(self, mod, capsys, monkeypatch):
        """And the 'above half' branch must be reachable in BOTH directions."""
        monkeypatch.setattr(mod, "live_counts", lambda: (40, 266))
        assert mod.main() == 0
        out = capsys.readouterr().out
        assert "above half = False" in out


class TestItRefusesRatherThanGuessing:
    def test_an_unparseable_producer_refuses(self, mod, monkeypatch):
        """A missing count must REFUSE, never default to a number.

        `scripts/the_failing_set_is_recorded_not_guessed` records the same
        property for a different instrument: an absent measurement leaves the
        tally EMPTY rather than inventing one.
        """
        class _R:
            stdout = "nothing resembling a count here\n"

        monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _R())
        with pytest.raises(SystemExit) as e:
            mod.live_counts()
        assert "REFUSED" in str(e.value)

    def test_the_prior_pin_is_declared_as_a_pin(self, mod):
        """The earlier pair is typed because that store state is gone.

        It is asserted here so a future edit cannot silently re-point it at a
        live reading, which would make the comparison compare today with today.
        """
        assert (mod.PRIOR_VALID, mod.PRIOR_TOTAL) == (125, 231)
        assert mod.PRIOR_DATE == "2026-11-06"
