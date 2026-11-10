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
        if not dependants:
            #: ★ THE LIVE SET EMPTIED ON 2026-11-09 AND THE BRANCH IS DRIVEN
            #: INSTEAD. The 4 entries that declared they await the shared scope
            #: decision were closed or settled that night, so the live scan has
            #: nothing to classify. Its own message forbids passing on that
            #: absence, so the DEPENDENT branch is exercised with a CONSTRUCTED
            #: case -- which is exactly how `classify_text`'s docstring says
            #: this branch must be driven, because on live data it has never
            #: decided anything: all 4 dependants also carried no asking
            #: sentence and so fell to MINE whether the branch existed or not.
            d = prod.classify_text(
                "OPEN", None,
                "This repair AWAITS THE SHARED SCOPE DECISION AT B61 and "
                "raises nothing of its own.")
            assert d["kind"] == "DEPENDENT", (
                f"the DEPENDENT branch no longer fires on a text that declares "
                f"a dependency; it returned {d['kind']!r}, so the detector has "
                f"stopped working rather than the live set merely emptying")
            assert d["parent"] == "B61", d
            #: and the other direction, so it is not answering DEPENDENT to all
            plain = prod.classify_text("OPEN", None, "An ordinary repair.")
            assert plain["kind"] != "DEPENDENT", plain
            return
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
        # and the other direction, so it is not merely refusing everything.
        #
        # ★ REPOINTED FROM B61 TO C0001, 2026-11-02, AND THE OLD CONTROL WAS
        # RIGHT TO FAIL. B61's ticket was CLOSED on 2026-11-02 when its entry
        # was closed, so B61 became settled in the register and stopped being a
        # control -- the same staleness shape as a ratchet holding a name that
        # is no longer unreached. C0001 is chosen because its single register
        # ticket is open AND its entry is deliberately left open pending the
        # founder's judgement on whether a finding whose code path is switched
        # off stays listed, so it is unlikely to settle as a side effect of
        # other work. If it ever does, repoint this at another entry with an
        # open ticket rather than deleting the assertion: without it the test
        # passes by refusing everything.
        # ★ AND REPOINTED AGAIN 2026-11-09, THIS TIME BY SEARCH RATHER THAN BY
        # NAME. C0001 was CLOSED that night on his ruling, so the control went
        # stale for the 3rd time -- B61, then C0001. A control that names its
        # subject will keep going stale every time that subject is settled,
        # which is the "pin a set, not a count" rule applied to a fixture. It
        # now takes whichever live entry currently has an open register ticket,
        # and says so loudly if none does.
        import sys as _s, pathlib as _p
        _s.path.insert(0, str(_p.Path(__file__).resolve().parents[2] / "scripts"))
        from task_list_markers import parse_entries as _pe2       # noqa: E402
        _subject = None
        for _e in _pe2():
            if _e.state in ("DONE", "WITHDRAWN"):
                continue
            _st, _ = gen.settled_in_the_register(_e.ident)
            if not _st:
                _subject = _e.ident
                break
        assert _subject, (
            "every live entry is now settled in the register, so this control "
            "cannot control: the assertion would pass by refusing everything. "
            "That state is worth seeing rather than skipping past.")
        open_settled, why_open = gen.settled_in_the_register(_subject)
        assert not open_settled, (
            f"{_subject} reports settled ({why_open}) immediately after being "
            f"selected as unsettled, so the predicate is not deterministic")

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
        """An entry whose questions POSTDATE its ruling must stay in the list.

        ★ THE SUBJECT IS FOUND, NOT NAMED, 2026-11-09. This test pinned B21 and
        the literal date 2026-10-17. On 2026-11-09 he ruled on B21 again --
        "build it and implement it, on steps through 1 to 5 in full" -- and that
        ruling POSTDATES all 4 of the questions the entry had accumulated:
        `asks_newer_than_the_ruling("B21", "2026-11-09")` is False where the
        same call against 2026-10-17 and 2026-11-08 is True. So B21 left the
        decision list for the RIGHT reason and this test failed for the wrong
        one, accusing a correct closure of being a suppression.

        IT IS NOT WEAKENED. The property is the same and it is now checked on
        whichever entry currently exhibits it, so a real suppression anywhere
        still fails here. IT CANNOT PASS ON AN ABSENCE: if no live entry has
        questions newer than its ruling, the test says so and fails, exactly as
        its sibling `test_a_dependant_is_not_presented_as_a_decision` does.
        """
        import sys as _sys, pathlib as _pl
        _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2] / "scripts"))
        from task_list_markers import parse_entries as _pe   # noqa: E402
        #: DEFERRED is excluded with DONE and WITHDRAWN, and the reason is his
        #: own act: a deferral is HIM parking the entry, so leaving the decision
        #: list is the intended effect rather than a suppression. The sibling
        #: test_an_entry_he_deferred_is_never_a_decision asserts that directly.
        #: Without this the first run of the rewritten test accused B13, which
        #: he deferred himself.
        bearers = [e.ident for e in _pe()
                   if e.state not in ("DONE", "WITHDRAWN", "DEFERRED") and e.ruled
                   and gen.asks_newer_than_the_ruling(e.ident, e.ruled)]
        if not bearers:
            #: ★ THE LIVE SET IS EMPTY AS OF 2026-11-09, AND THAT IS RECORDED
            #: RATHER THAN SILENTLY ACCEPTED. Every entry that carried a
            #: question postdating its own ruling was either closed that night
            #: or ruled on again: B21 on his "build it and implement it, on
            #: steps through 1 to 5 in full", and B13 is DEFERRED by him and so
            #: excluded above. An empty live set makes the scan above vacuous,
            #: so the DETECTOR is driven instead and must still discriminate.
            #: Without this branch the test would pass on an absence, which is
            #: exactly what its own message forbade.
            live = [e for e in _pe()
                    if e.state not in ("DONE", "WITHDRAWN", "DEFERRED")]
            assert live, "no live entry at all, so nothing can be checked"
            #: THE PROBE MUST BE ABLE TO ANSWER. `live[0]` was B22, which
            #: carries no DATED ask at all, so the detector correctly returned
            #: False for 1970 and the probe accused it of being broken. An
            #: entry is a usable probe only if something in it is dated.
            probe = next((e.ident for e in live
                          if gen.asks_newer_than_the_ruling(e.ident, "1970-01-01")),
                         None)
            assert probe, (
                "no live entry carries a DATED ask, so the detector cannot be "
                "driven at all. That is itself worth seeing: either every live "
                "entry has stopped asking anything, or the date parser has.")
            assert not gen.asks_newer_than_the_ruling(probe, "2099-01-01"), (
                f"the detector reports an ask in {probe} newer than 2099, so it "
                f"is answering True regardless of the date")
            #: ★ AND THE ROUTING PREDICATE ITSELF, because the branch above only
            #: proves the ASK DETECTOR works. Mutation-tested 2026-11-10: with
            #: only the 2 assertions above, forcing `ruling_is_spent` to return
            #: False for everything -- which routes every entry to
            #: `no_ruling_needed` and suppresses the whole decision list -- left
            #: this file GREEN. That is a guard weakened to go green, which is
            #: exactly what the FFAFP gate asks to be distinguished from a
            #: predicate defect. The empty live set removes the subject, not the
            #: obligation, so the predicate is driven directly instead.
            spent_when_old = gen.ruling_is_spent(probe, "1970-01-01", "OPEN")
            spent_when_new = gen.ruling_is_spent(probe, "2099-01-01", "OPEN")
            assert spent_when_old, (
                f"{probe} has asks newer than 1970 and `ruling_is_spent` says "
                f"the ruling still settles it, so every such entry would be "
                f"routed out of the decision list -- the suppression this test "
                f"exists to catch")
            assert not spent_when_new, (
                f"`ruling_is_spent` reports a 2099 ruling as spent for {probe}, "
                f"so it is answering the same way regardless of the date and "
                f"the inflation direction would return")
            return
        missing = [b for b in bearers if b not in decided]
        assert not missing, (
            f"these entries carry questions raised AFTER their own ruling and "
            f"have left the decision list, which is the suppression direction "
            f"the project names as the worse one: {missing}. This test was "
            f"pinned to B21 until 2026-11-09; it now finds its own subject.")

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

class TestTheCoarseSplitterHidesNoLiveAsk:
    """★ THE SENTENCE SCOPING IS COARSER THAN IT LOOKS, AND MEASURED SAFE.

    `_SENT` splits on sentence punctuation followed by WHITESPACE, so a heading
    ending `.**` does not split from the paragraph after it: measured over every
    entry, 152 of 5,802 blobs span a paragraph break and 222 span a marker
    comment. That matters because the free-panel test is scoped to the BLOB, and
    a free-panel mention anywhere in a blob suppresses every ask inside it --
    the dangerous direction this probe already failed in once, when a
    body-scoped test hid the role-layer question from him.

    MEASURED 2026-11-01: exactly 1 ask is affected, and it is B22's own sentence
    declaring an EARLIER ask stale, so suppressing it is correct and a finer
    split would put a stale question back on his queue. The splitter was
    therefore NOT changed, and `p-pass-anti-nitpick` applies. This pins that
    result: if a future entry puts a genuinely live ask in the same blob as a
    free-panel mention, it goes red and the scoping has to be revisited.
    """

    def test_no_live_ask_is_hidden_by_blob_scoping(self, prod):
        import re
        import task_list_markers as T
        bodies = prod.bodies()
        hidden = []
        for e in T.parse_entries():
            for blob in prod._SENT.split(bodies.get(e.ident, "")):
                if not (prod.ASKS.search(blob) and prod.FREE.search(blob)):
                    continue
                for part in re.split(r"(?<=[.!?])\s+|\.\*\*\s*|\n\s*\n", blob):
                    if not prod.ASKS.search(part) or prod.FREE.search(part):
                        continue
                    if prod.STALE.search(part):
                        continue          # the part declares an earlier ask stale
                    hidden.append((e.ident, " ".join(part.split())[:160]))
        assert not hidden, (
            "a LIVE ask is hidden because a free-panel mention shares its blob, "
            "so he is never asked it; tighten the scoping:\n"
            + "\n".join(f"  {i}: {t}" for i, t in hidden))

    def test_the_span_rates_behind_it_are_reproducible(self, prod):
        """The 2 rates are cited in the record, so they are recomputed here
        rather than trusted: a figure with no live producer is a claim."""
        import task_list_markers as T
        bodies = prod.bodies()
        total = para = marker = 0
        for e in T.parse_entries():
            for blob in prod._SENT.split(bodies.get(e.ident, "")):
                total += 1
                para += "\n\n" in blob
                marker += "<!--" in blob
        assert total > 1000, f"only {total} blobs; the corpus cannot be right"
        # Non-zero is the POINT: the scoping is genuinely coarse, which is what
        # the test above exists to bound. Asserting 0 would be asserting the
        # opposite of the measurement.
        assert 0 < para < total * 0.2, (para, total)
        assert 0 < marker < total * 0.2, (marker, total)
