"""Asking him to rule must never be read as him having ruled.

THE DEFECT, OBSERVED 2026-11-02. In
`scripts/which_entries_ask_for_a_ruling_he_has_given_2026-11-01.py`, `ASKS`
matches `NEEDS HIS RULING` and `GAVE` matches `HIS RULING` -- a SUBSTRING of it.
So the sentence asking him for a decision satisfied the pattern for him having
given one, and the producer reported entries as ALSO recording a ruling when the
only "ruling" in them was the request for one.

MEASURED BEFORE THE REPAIR: of 35 entries matching `ASKS`, 31 matched `GAVE`
somewhere and 6 matched it ONLY inside the asking phrase -- 6 of 31, 0.193548,
Wilson 95% [0.091870, 0.362803]. 3 of those 6 were entries genuinely awaiting
his decision, so the error ran in the direction that tells a reader he has ruled
where he has not. `feedback_already_ruled_and_misread_rates` records that
failure reaching him 4 times.

IT DOES NOT NEED THE LIVE DEFECT. Nothing here asserts on which real entries are
awaiting a ruling, because that set changes every time he rules and a guard
pinned to it would go stale and then be switched off. The property is stated over
synthetic text and over the 2 patterns themselves.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "scripts"
            / "which_entries_ask_for_a_ruling_he_has_given_2026-11-01.py")


@pytest.fixture(scope="module")
def mod():
    """Load the producer WITHOUT running it: it walks the whole task list."""
    ns = {"__name__": "_guard", "__file__": str(PRODUCER)}
    exec(compile(PRODUCER.read_text(), str(PRODUCER), "exec"), ns)
    return ns


class TestTheAskingPhraseIsNotAnAnswer:
    #: Every form `ASKS` is written to catch. None may count as a ruling.
    ASKING = [
        "NEEDS HIS RULING",
        "NEEDS YOUR RULING",
        "STILL NEEDS HIS GO-AHEAD",
        "NEEDS HIS AUTHORISATION",
        "NEEDS HIS VERDICT",
        "NEEDS HIS DECISION",
        "AWAITS HIS RULING",
        "AWAITS YOUR VERDICT",
    ]

    @pytest.mark.parametrize("phrase", ASKING)
    def test_an_asking_phrase_alone_records_no_ruling(self, mod, phrase):
        assert mod["ASKS"].search(phrase), (
            f"{phrase!r} must be recognised as asking, or this guard is "
            "testing nothing")
        assert mod["gave_outside_the_ask"](phrase) is None, (
            f"{phrase!r} was read as HIM HAVING RULED. The asking phrase "
            "contains the giving phrase, so the detector matched itself.")

    def test_the_raw_pattern_still_self_matches_so_the_masking_is_load_bearing(
            self, mod):
        """ANTI-VACUITY. If `GAVE` ever stops matching the asking phrase on its
        own, these tests would pass with the masking REMOVED, and the guard
        would be measuring nothing. This pins that the overlap is real."""
        assert mod["GAVE"].search("NEEDS HIS RULING"), (
            "the raw GAVE pattern no longer matches the asking phrase; the "
            "masking may now be dead code -- re-derive before deleting it")


class TestAGenuineRulingIsStillFound:
    @pytest.mark.parametrize("text", [
        'He ruled on 2026-10-17 that the loud failure should be a raise.',
        'HIS INSTRUCTION, verbatim: "I accept your recommendation."',
        'DEFERRED ON HIS RULING OF 2026-10-30, and it is to stop surfacing.',
        'You ruled the ordering on 2026-11-01.',
    ])
    def test_a_ruling_with_no_ask_present(self, mod, text):
        assert mod["gave_outside_the_ask"](text) is not None, (
            f"a genuine ruling was missed: {text!r}")

    def test_a_ruling_in_the_same_entry_as_an_ask_is_still_found(self, mod):
        """The masking covers the matched asking phrase only, about 16
        characters, so a real ruling elsewhere in the entry survives."""
        text = ("NEEDS HIS RULING on the second factor. "
                "Separately, HIS INSTRUCTION of 2026-11-01 was to implement it.")
        g = mod["gave_outside_the_ask"](text)
        assert g is not None, "a real ruling beside an ask was masked away"
        assert "INSTRUCTION" in text[g.start():g.end() + 12], text[g.start():]

    def test_a_ruling_in_the_same_SENTENCE_as_an_ask_is_still_found(self, mod):
        text = "NEEDS HIS RULING, though he ruled the ordering already."
        assert mod["gave_outside_the_ask"](text) is not None


class TestItIsStatedOverTheOtherPatternRatherThanDuplicatingIt:
    def test_the_mask_comes_from_ASKS_itself(self, mod):
        """Masking is derived from `ASKS.finditer`, so the 2 patterns cannot
        drift apart. A hand-written exclusion list would need updating every
        time a new asking phrase is added."""
        src = PRODUCER.read_text()
        fn = src[src.index("def gave_outside_the_ask"):]
        fn = fn[:fn.index("\ndef ") if "\ndef " in fn else len(fn)]
        assert "ASKS.finditer" in fn, (
            "the mask must be built from ASKS's own matches, not from a "
            "separate literal list")

    def test_every_ask_match_is_masked_not_just_the_first(self, mod):
        """2 asks in one entry, and the second must be masked too."""
        text = "NEEDS HIS RULING here. And later, NEEDS HIS RULING there."
        assert mod["ASKS"].search(text)
        assert mod["gave_outside_the_ask"](text) is None, (
            "only the first asking phrase was masked")

class TestTheCALLERUsesTheMaskedPredicate:
    """★ ADDED AFTER THE MUTATION HARNESS FOUND THIS GAP, 2026-11-02.

    Every test above calls `gave_outside_the_ask` DIRECTLY, so reverting the
    CALLER in `main()` to the raw `GAVE.search(e.text)` left the whole suite
    GREEN while restoring the defect. That is the deciding-layer fault
    `feedback_verify_the_deciding_layer` records: the helper was exercised and
    the decision that uses it was not.

    THE PROPERTY IS STATED WITHOUT A LITERAL COUNT, so it cannot go stale as
    entries are added or he rules on them: whichever entries the producer
    reports as ALSO recording a ruling, the masked predicate must agree about
    every one of them. Under the raw pattern the producer lists entries whose
    only "ruling" is the phrase asking for one, and for those the predicate
    returns None -- so the sets diverge and this fails.
    """

    def test_every_entry_the_producer_calls_ruled_survives_the_mask(self, mod):
        import re as _re
        import subprocess as _sp
        import sys as _sys
        r = _sp.run([_sys.executable, str(PRODUCER)], capture_output=True,
                    text=True, cwd=str(REPO), timeout=600)
        out = r.stdout + r.stderr
        block = out.split("M1.")[-1].split("M2.")[0]
        # Each reported row opens with "  <IDENT>  state=..."
        idents = _re.findall(r"^\s{2}([A-Z]+\d+)\s+state=", block, _re.M)
        assert idents, (
            "the producer reported no entries under M1, so this test would "
            f"pass vacuously. Output head: {block[:300]!r}")
        bodies = _entry_bodies()
        disagreed = [i for i in idents
                     if mod["gave_outside_the_ask"](bodies.get(i, "")) is None]
        assert not disagreed, (
            f"the producer calls {disagreed} entries that ALSO record a ruling, "
            f"but the masked predicate finds no ruling outside their asking "
            f"phrase. The caller is not using the mask.")


def _entry_bodies() -> dict:
    """code -> its text, from the task list the producer itself reads."""
    import re as _re
    t = (REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md").read_text(
        errors="replace")
    out = {}
    for m in _re.finditer(r"^\*\*([A-Z]*[0-9]+)\.", t, _re.M):
        nxt = _re.compile(r"^\*\*[A-Z]*[0-9]+\.", _re.M).search(t, m.end())
        out[m.group(1)] = t[m.start():nxt.start() if nxt else len(t)]
    return out
