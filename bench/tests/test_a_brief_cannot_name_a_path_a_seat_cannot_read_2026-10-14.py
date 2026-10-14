"""A brief that names a path a seat cannot read is refused before dispatch.

MEASURED 2026-10-14 ON CC1'S OWN BRIEF. The joint brief for
`his_rulings_2026-10-13` told both seats to read
`bench/logs/his_rulings_2026-10-13/cc2/` and `fable/`. Neither directory exists:
the replies are `cc2.json` and `fable.json`. A seat following the brief would have
found nothing, improvised, and nothing in the harness would have reported it. The
round was killed for an unrelated reason and this was found by accident.

THE CHECK IS SECTION SCOPED and these tests hold that boundary, because the
obvious whole-document version would refuse every brief that correctly tells a
seat to CREATE a file -- which is the normal output instruction.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def V():
    spec = importlib.util.spec_from_file_location(
        "_pbv_paths", REPO / "scripts" / "panel_brief_validate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_pbv_paths"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_a_missing_path_in_the_artefacts_section_is_reported(V):
    text = ("## THE ARTEFACTS UNDER REVIEW, BY PATH\n\n"
            "- `bench/logs/does_not_exist_anywhere_2026-01-01/cc2/` — the reply.\n")
    found = V.named_paths_that_do_not_exist(text)
    assert any("does_not_exist_anywhere" in c for c, _ in found), found


def test_the_exact_path_from_the_2026_10_14_brief_is_reported(V):
    """The real defect, not a paraphrase of it."""
    text = ("## THE ARTEFACTS UNDER REVIEW, BY PATH\n\n"
            "- `bench/logs/his_rulings_2026-10-13/cc2/` and "
            "`bench/logs/his_rulings_2026-10-13/fable/` — the blind replies.\n")
    found = V.named_paths_that_do_not_exist(text)
    assert len(found) == 2, found


def test_an_elided_path_is_reported(V):
    text = ("## THE ARTEFACTS UNDER REVIEW, BY PATH\n\n"
            "- `experimental_notes/seat_evidence/r/cc2/` and `.../fable/` — both.\n")
    found = V.named_paths_that_do_not_exist(text)
    assert any(c.startswith("...") for c, _ in found), found


def test_a_path_that_exists_is_not_reported(V):
    text = ("## THE ARTEFACTS UNDER REVIEW, BY PATH\n\n"
            "- `bench/reference_runner_v3.py` — the runner.\n"
            "- `scripts/panel_brief_validate.py` — this validator.\n")
    assert V.named_paths_that_do_not_exist(text) == []


def test_a_file_the_seat_is_told_to_CREATE_is_not_reported(V):
    """THE BOUNDARY. A whole-document check would refuse this, and it is correct.

    Every brief ends by telling the seat to write its fix somewhere that does not
    exist yet. If this check reached that instruction it would refuse every brief
    in the project.
    """
    text = ("## THE ARTEFACTS UNDER REVIEW, BY PATH\n\n"
            "- `bench/reference_runner_v3.py` — the runner.\n\n"
            "## OUTPUT — WHAT TO RETURN\n\n"
            "Write your fix to `sandbox/my_new_fix_2026-10-14.py` and say so.\n")
    assert V.named_paths_that_do_not_exist(text) == []


def test_no_artefacts_section_means_no_finding(V):
    """The check must not fire on a brief shaped differently; other checks cover
    the missing section itself."""
    assert V.named_paths_that_do_not_exist("## SOMETHING ELSE\n\n`a/b/c.py`\n") == []


def test_validate_surfaces_it_as_a_refusal(V):
    """EXECUTED THROUGH THE REAL ENTRY POINT, not the helper alone, because the
    dispatcher calls `validate` and nothing else."""
    text = ("## THE ARTEFACTS UNDER REVIEW, BY PATH\n\n"
            "- `bench/logs/nope_2026-01-01/cc2/` — a reply.\n")
    assert any("cannot read" in p for p in V.validate(text))


def test_the_live_briefs_are_checked_by_this_rule(V):
    """The directive-set brief must be clean; a regression here is a real one."""
    f = REPO / "bench" / "logs" / "the_directive_set_and_capability_2026-10-14" / "BRIEF.md"
    if not f.is_file():
        pytest.skip("that brief is not in this tree")
    assert V.named_paths_that_do_not_exist(f.read_text(encoding="utf-8")) == []
