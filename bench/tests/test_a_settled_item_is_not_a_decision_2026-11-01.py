"""What reaches his decision list, and what may not.

HIS CHALLENGE, 2026-11-01: *"The first seemed like a suspiciously high number,
as you have a habit of repeating issues to me to rule on that I have already
ruled on, or that have already been settled."*  And his instruction: *"On the
closed status tickets. Please fix it so issues that are genuinely closed don't
keep being represented."*

4 SUPPRESSION AND INFLATION FAULTS WERE FOUND IN ONE PASS, and 3 of them
pointed in OPPOSITE directions, which is why fixing any one alone made the
report worse:

  1. INFLATION. 4 entries that each declare in their own text that they await a
     5th entry's decision were presented as 4 separate decisions. The 2 filters
     the generator carried are both keyed on ONE entry's state and neither can
     see a decision graph.
  2. INFLATION. The register's CLOSED status was read by nothing. CLOSED is
     tool-only and requires a verification, so it is the only authoritative
     record of settlement, and the generator consulted PROSE instead.
  3. SUPPRESSION, the worse direction. A ruling date removed an item for good.
     The role-layer entry carries a ruling of 2026-10-17 and 4 questions raised
     on 2026-10-30, 2026-10-31 and 2026-11-01; all 4 were silenced. 3 places
     suppressed on a ruling date and 1 of them was DATA.
  4. OVER-CORRECTION. Replacing that with "does it still ask" took the list from
     3 to 12 and put back the zero-plant control, which he deferred himself. The
     ruling filter exists for a reason: measured 2026-10-17, 11 of 45 ruled
     entries still carried an asking sentence their ruling had answered.

SO THE PREDICATE IS DATE-AWARE AND STATE-AWARE, and this file holds every arm of
it by EXECUTION. The last test is the important one: 2 independently written
instruments must agree on the decision set, which is the only check that cannot
be satisfied by one of them being wrong in a convenient direction.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def gen():
    return _load(REPO / "scripts" / "morning_report_build_2026-10-12.py", "mrb_t")


@pytest.fixture(scope="module")
def prod():
    return _load(REPO / "scripts"
                 / "how_many_decisions_actually_need_him_2026-11-01.py", "hmd_t")


@pytest.fixture(scope="module")
def decided(gen):
    """The decision set the generator would actually render."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = gen.main(["x"])
    assert rc == 0, buf.getvalue()[-800:]
    out = buf.getvalue()
    import re
    return [m.group(1) for m in re.finditer(r"^### \d+\.\s+(\S+)", out, re.M)]


class TestInflationIsGone:
    def test_a_dependant_is_not_presented_as_a_decision(self, decided, prod):
        """LIVE CASE: 4 entries declare they await the scope decision."""
        rows = prod.classify()
        dependants = [r["ident"] for r in rows if r["kind"] == "DEPENDENT"]
        assert dependants, (
            "no entry currently declares a dependency, so this test is "
            "vacuous — do not let it pass on an absence")
        leaked = [d for d in dependants if d in decided]
        assert not leaked, (
            f"{leaked} wait on another entry's decision by their own text and "
            f"are still presented as decisions of their own")

    def test_a_settled_register_entry_with_no_live_ask_is_dropped(self, gen):
        """FORWARD GUARD, DRIVEN BY A CONSTRUCTED CASE because no live entry is
        in this state today: closing an entry properly also closes its tickets,
        so the filter fires on 0 of 16 live items. A guard whose only evidence
        is live data that does not exercise it is indistinguishable from a
        guard that does nothing."""
        settled, why = gen.settled_in_the_register("B64")
        assert settled and "CLOSED" in why, why
        assert not gen.still_asks("B64")
        # and the other direction, so it is not merely refusing everything
        open_settled, _ = gen.settled_in_the_register("B61")
        assert not open_settled

    def test_the_register_filter_IS_WIRED_not_merely_defined(self, gen, monkeypatch):
        """THE WIRING, WHICH NO LIVE MUTATION CAN REACH. `settled_in_the_register`
        fires on 0 of 16 live items, so unwiring it from `main()` changes no
        output and every other test here still passes. A fix nobody can observe
        failing is indistinguishable from no fix — the addition-reaching-nothing
        defect confirmed 11 times in this project. So both halves of the
        predicate are forced for ONE live decision and the entry must leave the
        list.

        THE ORIGINALS ARE CAPTURED BEFORE PATCHING. The first version of this
        test read `gen.still_asks` inside its own replacement and recursed to the
        stack limit, which is a test that fails for a reason having nothing to do
        with its subject.
        """
        import contextlib
        import io
        import re as _re
        orig_settled = gen.settled_in_the_register
        orig_asks = gen.still_asks
        monkeypatch.setattr(gen, "settled_in_the_register",
                            lambda i: (True, "forced for this test")
                            if i == "B60" else orig_settled(i))
        monkeypatch.setattr(gen, "still_asks",
                            lambda i: False if i == "B60" else orig_asks(i))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gen.main(["x"])
        rendered = [m.group(1) for m in
                    _re.finditer(r"^### \d+\.\s+(\S+)", buf.getvalue(), _re.M)]
        assert "B60" not in rendered, (
            "forcing the register to call B60 settled did not remove it, so the "
            "filter is defined and not wired")

    def test_an_entry_with_no_ticket_is_kept(self, gen):
        """FAILS OPEN. A filter that hides an item when its input is missing is
        the false-zero shape this project has met repeatedly."""
        settled, why = gen.settled_in_the_register("THERE-IS-NO-SUCH-ENTRY")
        assert not settled and "no ticket" in why


class TestSuppressionIsGone:
    def test_a_ruling_older_than_its_questions_does_not_silence_them(self, gen, decided):
        """LIVE CASE: the role-layer entry, ruled 2026-10-17, asking since."""
        assert gen.asks_newer_than_the_ruling("B21", "2026-10-17")
        assert "B21" in decided, (
            "the role-layer entry carries 4 questions raised after its ruling "
            "and has left the decision list again")

    def test_a_ruling_with_nothing_newer_still_silences(self, gen):
        """THE OTHER DIRECTION, without which the fix above would reintroduce
        the inflation: a ruling dated after everything in the entry settles it."""
        assert not gen.asks_newer_than_the_ruling("B21", "2099-01-01")

    def test_an_entry_he_deferred_is_never_a_decision(self, decided, prod):
        """LIVE CASE: the zero-plant control, deferred on his own ruling with
        the words that it is to stop surfacing."""
        rows = prod.classify()
        deferred = [r["ident"] for r in rows if r["state"] == "DEFERRED"]
        assert deferred, "no deferred entry exists, so this test is vacuous"
        leaked = [d for d in deferred if d in decided]
        assert not leaked, f"{leaked} were deferred by him and are back on the list"


class TestTheTwoInstrumentsAgree:
    def test_the_generator_and_the_producer_name_the_same_decisions(self, decided, prod):
        """THE CHECK THAT MATTERS. These 2 were written separately, read
        different inputs — the generator reads authored detail and markers, the
        producer reads each entry's own text — and reach the decision set by
        different routes. Agreement is evidence; disagreement is a defect in one
        of them, and on 2026-11-01 it was 4 against 3 because an entry's
        authored detail said it was his while the entry itself asked nothing.
        """
        owed = sorted(r["ident"] for r in prod.classify() if r["kind"] == "OWED")
        assert sorted(decided) == owed, (
            f"the generator renders {sorted(decided)} and the producer derives "
            f"{owed}. One of them is wrong; a count would have hidden a swap.")
