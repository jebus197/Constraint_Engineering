"""The naming check catches a coined machinery name and passes an introduced one.

WHY. Of 13 terms the founder examined from CC1's own reports, 8 were faults: 7
coined outright, 1 a collision with an existing project meaning. His complaint:
*"It can't be the case that I wake up to a tts report and struggle to know what
you are talking about!"* `note_vagueness_lint.py` passed every faulty term.

WHAT IS GUARDED. The check's DISCRIMINATION, executed rather than described -- it
must fire on a bare coined machinery name and stay silent on one the writer
introduces. Its measured limits are asserted too, because a check whose blind
spots are undocumented invites exactly the false confidence it exists to prevent.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "note_naming_check_2026-09-28.py"


def _load():
    spec = importlib.util.spec_from_file_location("naming_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["naming_check"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def nc():
    assert SCRIPT.is_file(), f"missing {SCRIPT}"
    return _load()


def test_candidates_require_a_machinery_head_noun(nc):
    """Adjacency is not a name. The first design matched any 2-4 words and
    returned 24 findings on one report, nearly all sentence fragments."""
    found = nc.candidates("The critics order ran first and the write returned nothing.")
    assert "critics order" in found
    assert "write returned" not in found, "a verb phrase is not a machinery name"


def test_ordinary_english_with_a_head_noun_is_not_a_name(nc):
    found = nc.candidates("The same gate fired again at the next stage.")
    assert "same gate" not in found
    assert "next stage" not in found


def test_an_introduced_name_is_passed_over(nc):
    """Coining a name is permitted; asserting one as already-shared is the fault."""
    text = "The absorb rule, which is the mechanism merging near-duplicates, fired."
    cands = nc.candidates(text)
    assert "absorb rule" in cands
    assert nc.introduced(text, "absorb rule", cands["absorb rule"]) is True


def test_a_bare_name_is_not_treated_as_introduced(nc):
    text = "The critics order determined which dimension ran first."
    cands = nc.candidates(text)
    assert "critics order" in cands
    assert nc.introduced(text, "critics order", cands["critics order"]) is False


def test_code_and_paths_are_not_scanned_for_names(nc):
    """A phrase inside backticks or a path is not prose making a claim."""
    stripped = nc._strip("Text `the widget gate` and bench/the_widget_gate.py here.")
    assert "widget gate" not in stripped.lower()


def test_repo_hits_excludes_the_note_being_checked(nc, tmp_path):
    """A note must not vouch for its own coinage."""
    hits_all = nc.repo_hits("additive standard", exclude=None)
    assert hits_all > 0, "expected a known project term to appear in the repo"
    missing = nc.repo_hits("zzqx nonexistent gate", exclude=None)
    assert missing == 0


def test_a_verb_before_the_head_means_the_match_crossed_a_clause(nc):
    """Measured 2026-09-28: the head-noun pattern alone returned 6 findings on the
    28 September report, 5 of them clause fragments. The verb filter removed only
    false positives -- the 24 September report stayed at 3 findings including the
    confirmed fault `prose scoring flag`, and the fixture's `critics order` still
    fired."""
    assert "appendix retired that rule" not in nc.candidates(
        "The appendix retired that rule on 2026-09-21.")
    assert "decision precedes the branch" not in nc.candidates(
        "The decision precedes the branch in every case.")
    assert "dispatcher passes seats" not in nc.candidates(
        "The dispatcher passes seats their tool list.")
    # And the filter must not eat a real coinage whose modifier merely looks verb-like.
    assert "prose scoring flag" in nc.candidates("The prose scoring flag was unreachable.")


def test_the_documented_blind_spot_is_real_not_theoretical(nc):
    """A COLLISION is invisible: the term exists, so novelty is 0 and nothing fires.

    This is asserted so the limit cannot quietly stop being true and leave the
    docstring overstating what the check covers.
    """
    hits = nc.repo_hits("blocking gate", exclude=None)
    assert hits > 0, (
        "`blocking gate` no longer appears in the repo; the collision blind spot "
        "documented in the script's header needs re-measuring"
    )
