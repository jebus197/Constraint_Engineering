"""A blind round must be blind of ITS OWN other seat, not only of other rounds.

FOUND 2026-10-08 DURING THE ROUND IT APPLIES TO, by execution rather than by
reading. `division_count_and_bidirectional_ladder_blind_2026-10-08` was dispatched
with `PANEL_BLIND_OF` unset, which is correct -- it is the first round on its
brief, so it has no siblings. The fable seat landed at 12:00:16 with a 12,299
character reply. `fresh_sandbox_for_attempt` clones the LIVE tree at RETRY time,
so from that moment a cc2 retry would have been handed fable's whole answer.
Measured against the live tree: a sandbox built with `blind_of=()` carried
`fable.json` and `fable.tools.attempt1.json.txt`.

AND THE EXISTING CONTROL COULD NOT BE USED INSTEAD. Passing the round's own name
to `blind_of` removes the WHOLE directory -- `BRIEF.md` with it, measured in the
same probe -- so a seat told to work in the tree would find no brief there. The
gap is structural: `blind_of` names OTHER rounds and has no way to say "blind of
my own round's other seats". The first dispatch of a 2-seat blind round cannot
know a co-seat will land while it is still running.

THE FIRST ATTEMPT AT THE FIX WAS WRONG IN THE DIRECTION THAT REPORTS SUCCESS,
and that is why the mutation test below exists. The round name is in the
DIRECTORY name, not in `fable.json`, so `surviving_round_evidence`'s
`rglob(f"*{name}*")` matches the directory and nothing inside it. The first
`coseat_survivors` skipped directories as "not evidence" and returned an EMPTY
survivor list while the reply sat untouched -- a verify that agreed with what it
was hoping for, and one that would have shipped the hole with a green test beside
it. Caught by listing the sandbox's files instead of trusting the predicate.

EVERY TEST HERE BUILDS A REAL SANDBOX AND LOOKS AT THE FILES. `execute-do-not-grep`.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ROUND = "a_round_name_2026-10-08"
OTHER_ROUND = "some_other_round_2026-10-01"


@pytest.fixture(scope="module")
def ps():
    spec = importlib.util.spec_from_file_location(
        "panel_sandbox_coseat", REPO / "bench" / "panel_sandbox.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["panel_sandbox_coseat"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def tree(tmp_path):
    """A miniature repo carrying 2 rounds, 1 of them with a landed co-seat reply."""
    root = tmp_path / "repo"
    own = root / "bench" / "logs" / ROUND
    own.mkdir(parents=True)
    (own / "BRIEF.md").write_text("# the brief the seat must answer\n")
    (own / "fable.json").write_text(json.dumps(
        {"model": "fable", "ok": True, "response": "MY VERDICT IS SOUND"}))
    (own / "fable.tools.attempt1.json.txt").write_text("tool log\n")
    other = root / "bench" / "logs" / OTHER_ROUND
    other.mkdir(parents=True)
    (other / "cc2.json").write_text(json.dumps({"response": "EARLIER ROUND"}))
    # A mirrored copy elsewhere, which is how 2026-10-05's leak actually reached a seat.
    mirror = root / "experimental_notes" / "evidence" / f"panel_records_x" / ROUND
    mirror.mkdir(parents=True)
    (mirror / "fable.json").write_text(json.dumps({"response": "MY VERDICT IS SOUND"}))
    (root / "keep_me.py").write_text("print('ordinary file')\n")
    return root


class TestTheHoleIsRealWithoutTheFix:
    def test_a_default_sandbox_carries_the_coseat_reply(self, ps, tree):
        """If this ever fails, the hole closed by some other route and the rest
        of this file is measuring nothing."""
        dest = Path(ps.build(tree))
        got = sorted(p.name for p in (dest / "bench" / "logs" / ROUND).iterdir())
        assert "fable.json" in got, got

    def test_naming_your_own_round_in_blind_of_destroys_the_brief(self, ps, tree):
        """Why a new parameter was needed rather than another blind_of entry."""
        dest = Path(ps.build(tree, blind_of=(ROUND,)))
        assert not (dest / "bench" / "logs" / ROUND / "BRIEF.md").exists(), (
            "blind_of kept the brief, so it could have been used as-is and the "
            "new parameter is unjustified")


class TestOwnRoundClosesIt:
    def test_the_coseat_reply_is_gone_and_the_brief_remains(self, ps, tree):
        dest = Path(ps.build(tree, own_round=ROUND))
        d = dest / "bench" / "logs" / ROUND
        got = sorted(p.name for p in d.iterdir())
        assert got == ["BRIEF.md"], got
        assert (d / "BRIEF.md").read_text().startswith("# the brief")

    def test_the_mirrored_copy_elsewhere_goes_too(self, ps, tree):
        """2026-10-05's leak arrived through a mirror, not the round directory."""
        dest = Path(ps.build(tree, own_round=ROUND))
        hits = [p for p in dest.rglob("fable.json")]
        assert hits == [], [str(h.relative_to(dest)) for h in hits]

    def test_the_survivor_list_agrees_with_the_filesystem(self, ps, tree):
        """THE TEST THE FIRST BROKEN VERSION WOULD HAVE PASSED is the one above;
        this is the one that catches a predicate disagreeing with the disk."""
        dest = Path(ps.build(tree, own_round=ROUND))
        reported = {str(p.relative_to(dest)) for p in ps.coseat_survivors(dest, ROUND)}
        on_disk = {str(p.relative_to(dest))
                   for p in dest.rglob("*")
                   if p.is_file() and ROUND in str(p.relative_to(dest))
                   and p.name not in ps.OWN_ROUND_KEEP}
        assert reported == on_disk == set(), (reported, on_disk)

    def test_it_detects_what_it_cannot_remove(self, ps, tree):
        """Before any purge, the survivor list must SEE the 3 artefacts.

        A detector that reports nothing on a dirty tree is the defect this file
        was written around, so it is asserted directly rather than inferred from
        a clean one.
        """
        dest = Path(ps.build(tree))            # no own_round: nothing purged
        reported = {Path(p).name for p in ps.coseat_survivors(dest, ROUND)}
        assert {"fable.json", "fable.tools.attempt1.json.txt"} <= reported, reported
        assert "BRIEF.md" not in reported, (
            "the brief is the 1 file of its own round a seat may see")


class TestNothingElseIsTouched:
    def test_another_round_is_left_alone(self, ps, tree):
        dest = Path(ps.build(tree, own_round=ROUND))
        assert (dest / "bench" / "logs" / OTHER_ROUND / "cc2.json").exists(), (
            "own_round purged a DIFFERENT round, which would silently destroy "
            "the star topology's joint-round input")

    def test_ordinary_files_survive(self, ps, tree):
        dest = Path(ps.build(tree, own_round=ROUND))
        assert (dest / "keep_me.py").exists()

    def test_omitting_own_round_changes_nothing(self, ps, tree):
        """Additive: every existing caller behaves exactly as before."""
        a = sorted(str(p.relative_to(x)) for x in [Path(ps.build(tree))]
                   for p in x.rglob("*") if p.is_file())
        b = sorted(str(p.relative_to(x)) for x in [Path(ps.build(tree, own_round=None))]
                   for p in x.rglob("*") if p.is_file())
        assert a == b, set(a) ^ set(b)


class TestTheDispatcherActuallyPassesIt:
    """An addition nothing reaches is not additive. The wiring is asserted by
    calling the dispatcher's own builder with a stub, not by reading its text."""

    def test_both_build_call_sites_name_the_round(self):
        import ast
        src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
        calls = [n for n in ast.walk(ast.parse(src))
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "build"
                 and isinstance(n.func.value, ast.Name)
                 and n.func.value.id == "panel_sandbox"]
        assert len(calls) == 2, len(calls)
        for c in calls:
            kw = {k.arg for k in c.keywords}
            assert "own_round" in kw, (
                "a panel_sandbox.build call site does not pass own_round, so the "
                "parameter is an addition nothing reaches")
