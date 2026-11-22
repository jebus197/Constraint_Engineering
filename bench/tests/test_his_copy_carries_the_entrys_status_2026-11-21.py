#!/usr/bin/env python3
"""HIS COPY SAID WHAT A DECISION ASKS AND NEVER WHAT THE ENTRY'S RECORD SAYS.

★ WHY THIS EXISTS, AND WHY THE OBVIOUS READING OF THE DEFECT IS WRONG.
On 2026-11-21 his Desktop copy of the decisions file was 8,482 bytes against the
repository copy's 95,259 at the SAME FILENAME, and carried 0 of the 4 premise
reversals a blind free panel had found on 2026-11-17. The obvious conclusion is
that his copy is truncated and should be restored to full length.

THAT WOULD UNDO HIS OWN RULING. The index-only Desktop copy is the 2026-11-11
repair to his 2026-11-08 complaint that the full file, at over 22,000 words, is
an almost impossible workload, and `test_his_copy_is_not_cut_to_fit_2026-11-11.py`
pins it. Regenerating his copy at full length re-creates exactly what he
objected to.

SO THE DEFECT IS NOT LENGTH. It is that an index line carried the QUESTION and
not the entry's STATE, so an entry already built and running read identically to
one awaiting a fresh ruling. Measured 2026-11-21 from the task list's own
markers: 34 of 49 open entries are BUILT-or-better and 10 of his 21 are, which is
0.476190, Wilson [0.283440, 0.676305]; 3 of the panel's 4 falsified-premise
entries are among them. A ruling given without that fact answers a question that
no longer exists.

THE FIX IS ABOUT 40 CHARACTERS ON A FLAGGED LINE and nothing is cut. Both
surfaces are rendered from ONE composed flag, because this loop emits a spoken
and a markdown line and a flag written into one of them only would make the 2
surfaces promise different things.

Mutations: `scripts/the_status_flag_mutations_2026-11-21.py`.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GEN = ROOT / "scripts" / "build_decisions_file_2026-11-07.py"


def _mod():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("bdf_status", GEN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def m():
    return _mod()


@pytest.fixture(scope="module")
def rendered(m):
    mrb, rows = m.collect()
    return {
        "rows": rows,
        "his": m.render(mrb, rows, spoken=True, detail=False),
        "spoken_full": m.render(mrb, rows, spoken=True, detail=True),
        "md": m.render(mrb, rows, spoken=False, detail=True),
        "states": m.entry_states(),
    }


class TestThePremiseIsAlive:
    def test_entries_exist_that_are_open_and_already_built(self, rendered):
        """If this ever reaches 0 the flag is inert and this guard says so."""
        st = rendered["states"]
        built = [k for k, (s, t) in st.items()
                 if s == "OPEN" and t in ("BUILT", "TESTED", "COMMITTED", "ENABLED")]
        assert built, "no OPEN entry is BUILT-or-better; the flag cannot fire"

    def test_his_copy_is_still_the_index_and_not_the_full_render(self, rendered):
        """His 2026-11-08 workload ruling must not be undone by this repair."""
        assert len(rendered["his"]) < len(rendered["spoken_full"]) / 4


class TestTheCopyHeReadsIsTheOneMainChooses:
    """★ THE GAP THE MUTATION HARNESS FOUND, AND IT WAS A REAL ONE.

    Reverting `main`'s Desktop render from the index to the full document left
    every other test here GREEN, because they all call `render` directly with
    `detail=False` and so never exercise the choice `main` actually makes about
    which render reaches his Desktop. The property was asserted on the function
    and not on the call that produces his file — a guarded mechanism no caller
    reaches, which this project has recorded before.

    This test drives `main` in its DRY-RUN form, which writes nothing, and
    records what `render` was asked for.
    """

    def test_main_asks_for_the_index_for_his_desktop_copy(self, m, monkeypatch, capsys):
        calls: list[dict] = []
        real = m.render

        def spy(mrb, rows, spoken, detail=True):
            calls.append({"spoken": spoken, "detail": detail})
            return real(mrb, rows, spoken, detail)

        monkeypatch.setattr(m, "render", spy)
        rc = m.main([])                      # no --write: a dry run
        capsys.readouterr()
        assert rc == 0, rc
        #: 3 renders: the repository markdown, the repository spoken copy, and
        #: HIS copy. Exactly 1 of them must be the index.
        assert len(calls) == 3, calls
        index_calls = [c for c in calls if c["detail"] is False]
        assert len(index_calls) == 1, (
            f"expected exactly 1 index render for his Desktop copy, got "
            f"{len(index_calls)}: {calls}")
        assert index_calls[0]["spoken"] is True, (
            "his copy is the SPOKEN index; a markdown index would reach no one")
        #: and the 2 repository copies keep every section
        full = [c for c in calls if c["detail"] is not False]
        assert len(full) == 2 and {c["spoken"] for c in full} == {True, False}

    def test_the_dry_run_reports_his_copy_as_a_small_fraction(self, m, capsys):
        rc = m.main([])
        out = capsys.readouterr().out
        assert rc == 0
        assert "his copy" in out
        frac = float(out.split("of the full spoken render")[0].rsplit("(", 1)[1])
        assert 0.0 < frac < 0.25, (
            f"his copy is {frac:.4f} of the full render; his 2026-11-08 "
            f"workload ruling is being undone")


class TestTheFlagIsDerived:
    def test_a_dead_premise_is_flagged_from_the_rows_own_text(self, m):
        flag = m.status_flag(
            "X1", {"what": "THE PREMISE OF THIS ENTRY NO LONGER HOLDS, found by a panel"}, {})
        assert "premise already falsified" in flag
        assert "ratify or close" in flag

    def test_built_or_better_is_flagged_from_the_task_lists_markers(self, m):
        for status in ("BUILT", "TESTED", "COMMITTED", "ENABLED"):
            flag = m.status_flag("X2", {}, {"X2": ("OPEN", status)})
            assert status.lower() in flag, status
            assert "ratify or close" in flag

    def test_a_merely_proposed_entry_is_NOT_flagged(self, m):
        assert m.status_flag("X3", {}, {"X3": ("OPEN", "PROPOSED")}) == ""

    def test_a_closed_entry_is_NOT_flagged(self, m):
        assert m.status_flag("X4", {}, {"X4": ("DONE", "COMMITTED")}) == ""

    def test_an_unknown_ident_is_NOT_flagged(self, m):
        assert m.status_flag("ZZ99", {}, {}) == ""

    def test_the_dead_premise_wins_over_the_status(self, m):
        """A falsified premise is the stronger fact and must be the one said."""
        flag = m.status_flag(
            "X5", {"what": "THE PREMISE OF THIS ENTRY NO LONGER HOLDS"},
            {"X5": ("OPEN", "BUILT")})
        assert "premise already falsified" in flag

    def test_the_states_come_from_the_canonical_parser(self, m):
        """Never re-derive a population a helper already defines."""
        st = m.entry_states()
        assert len(st) > 100, len(st)
        #: Imported by NAME, not loaded from a path under a fresh module name.
        #: A second `module_from_spec` of this file is not registered in
        #: `sys.modules`, and `dataclasses` resolves `InitVar` through
        #: `sys.modules[cls.__module__]`, so the unregistered copy raises
        #: AttributeError on a None module -- a failure in the probe and not in
        #: the subject.
        sys.path.insert(0, str(ROOT / "scripts"))
        import task_list_markers
        assert len(st) == len(task_list_markers.parse_entries())

    def test_an_unreadable_task_list_costs_a_flag_and_not_the_file(self, m, tmp_path):
        assert m.entry_states(tmp_path) == {}


#: ★ THE PREMISE THESE 3 LIVE ASSERTIONS REST ON, MADE EXPLICIT — 2026-11-22.
#:
#: WHAT WENT WRONG. 3 assertions in this class required at least 1 flag to fire
#: on the LIVE render (`got == expected > 0`, `0 < added`, and the phrase being
#: present). On 2026-11-22 all 3 failed with `0 flagged lines, 0 warranted`,
#: and 0 IS THE CORRECT ANSWER: the 8 rendered decisions were B94, B143, B154,
#: B160, B170, B186, B190 and B197, every one PROPOSED, while the 8 entries that
#: are OPEN and BUILT-or-better -- B165, B172, B173, B178, B179, B188, B189,
#: B192 -- are not decisions he owes a ruling on at all. The 2 sets are
#: DISJOINT, so no flag can fire and none should.
#:
#: WHY THE PREMISE TEST DID NOT CATCH IT. `test_entries_exist_that_are_open_and
#: _already_built` searches EVERY task-list entry, while these 3 assertions
#: range over DECISION ROWS. 2 different populations, and they diverged — the
#: premise test passed while everything downstream of it failed.
#:
#: WHY THIS IS NOT A WEAKENING. The mechanism is pinned by 6 CONSTRUCTED cases
#: in `TestTheFlagItself` -- dead premise flagged, built-or-better flagged,
#: merely-proposed NOT flagged, closed NOT flagged, unknown ident NOT flagged,
#: dead premise winning over status -- none of which depends on live data. The
#: equality assertions (`got == expected`, and the markdown surface agreeing)
#: keep their full force at 0, which is exactly how the markdown sibling has
#: always been written. What is removed is an assumption that some owed
#: decision is ALWAYS already built, which is not invariant and became false
#: through ordinary progress.
def _warranted(m, rendered) -> int:
    """How many DECISION ROWS -- not task-list entries -- warrant a flag."""
    return sum(1 for r in rendered["rows"]
               if m.status_flag(r["ident"], r, rendered["states"]))


class TestBothSurfacesCarryIt:
    def test_his_copy_carries_the_flag_in_plain_words(self, m, rendered):
        if _warranted(m, rendered) == 0:
            import pytest
            pytest.skip("0 decision rows warrant a flag, so none can appear; "
                        "the mechanism is pinned by TestTheFlagItself's 6 "
                        "constructed cases, which do not depend on live data")
        assert "ratify or close rather than rule" in rendered["his"]

    def test_his_copy_flags_every_entry_whose_record_warrants_it(self, m, rendered):
        expected = sum(
            1 for r in rendered["rows"]
            if m.status_flag(r["ident"], r, rendered["states"]))
        got = rendered["his"].count("ratify or close rather than rule")
        #: EQUALITY KEEPS ITS FULL FORCE AT 0 -- a renderer that emitted a flag
        #: nothing warranted, or dropped one that was, still fails here. The
        #: `> 0` that used to ride on this line asserted that some owed decision
        #: is always already built, which is a claim about the WORK and not
        #: about the renderer. Its markdown sibling below has never carried it.
        assert got == expected, f"{got} flagged lines, {expected} warranted"

    def test_the_markdown_surface_carries_the_same_count(self, m, rendered):
        expected = sum(
            1 for r in rendered["rows"]
            if m.status_flag(r["ident"], r, rendered["states"]))
        got = rendered["md"].upper().count("RATIFY OR CLOSE RATHER THAN RULE")
        assert got == expected, (
            f"the 2 surfaces disagree: markdown {got}, warranted {expected}")

    #: ★ CONSTRUCTED, BECAUSE THE LIVE RENDER CANNOT EXERCISE THESE — 2026-11-22.
    #:
    #: `scripts/the_status_flag_mutations_2026-11-21.py` reported 5 of 8 red and
    #: named the 2 it could NOT catch: *"the markdown surface loses the flag, so
    #: the 2 surfaces disagree"* and *"the spoken surface gains markdown
    #: decoration"*. Both go undetected whenever 0 flags fire, which is the live
    #: state from 2026-11-22: `got == expected` is `0 == 0` however the renderer
    #: behaves, and the decoration check loops over flag lines that do not
    #: exist. The vacuity PREDATES the conditional-premise repair made the same
    #: day -- but that repair stopped 3 sibling assertions failing, so a green
    #: suite would have hidden it. A fix that makes siblings pass vacuously is a
    #: fault this project already records.
    #:
    #: These 2 force a flag by planting the STATE, so they bite at any live
    #: count. `render` reads `entry_states(REPO)` itself at its line 841, which
    #: is why the module attribute is patched rather than an argument passed.
    def _forced(self, m, monkeypatch):
        """(his, md, ident) with exactly 1 row forced to warrant a flag."""
        mrb, rows = m.collect()
        assert rows, "no decision rows to force a flag on"
        ident = rows[0]["ident"]
        monkeypatch.setattr(m, "entry_states",
                            lambda *a, **k: {ident: ("OPEN", "BUILT")})
        return (m.render(mrb, rows, spoken=True, detail=False),
                m.render(mrb, rows, spoken=False, detail=True), ident)

    def test_both_surfaces_carry_a_forced_flag(self, m, monkeypatch):
        """Catches a markdown surface that drops the flag the spoken one keeps."""
        his, md, _ident = self._forced(m, monkeypatch)
        his_n = his.count("ratify or close rather than rule")
        md_n = md.upper().count("RATIFY OR CLOSE RATHER THAN RULE")
        assert his_n == 1, f"his copy carried {his_n} forced flag(s), expected 1"
        assert md_n == 1, f"the markdown surface carried {md_n}, expected 1"

    def test_a_forced_flag_line_carries_no_markdown(self, m, monkeypatch):
        """Catches decoration added to the spoken flag, which TTS reads aloud."""
        his, _md, _ident = self._forced(m, monkeypatch)
        lines = [l for l in his.splitlines()
                 if "ratify or close rather than rule" in l]
        assert len(lines) == 1, f"{len(lines)} forced flag line(s), expected 1"
        for ch in "*`[]|#":
            assert ch not in lines[0], f"{ch!r} in a spoken flag line: {lines[0][:70]!r}"

    def test_his_copy_stays_free_of_markdown_decoration(self, rendered):
        """The spoken flag must carry no brackets, asterisks or backticks."""
        for line in rendered["his"].splitlines():
            if "ratify or close rather than rule" not in line:
                continue
            for ch in "*`[]|#":
                assert ch not in line, f"{ch!r} in a spoken flag line: {line[:70]!r}"

    def test_the_flag_costs_little_and_cuts_nothing(self, m, rendered):
        """Bounded, against the 368 characters the uncapped index was measured to add."""
        mrb, rows = m.collect()
        states = rendered["states"]
        flagged = [m.status_flag(r["ident"], r, states) for r in rows]
        added = sum(len(f) + 2 for f in flagged if f)
        if added == 0:
            import pytest
            pytest.skip("0 decision rows warrant a flag, so the flag adds "
                        "nothing; the UPPER bound is what this test exists "
                        "for and it cannot be exceeded at 0")
        assert added < 2_000, added
        #: nothing is removed: every decision still appears in his copy
        for r in rows:
            assert r["ident"] in rendered["his"], r["ident"]
