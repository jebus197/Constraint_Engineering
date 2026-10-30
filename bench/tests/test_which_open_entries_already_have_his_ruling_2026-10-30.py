#!/usr/bin/env python3
"""2 of the 3 entries asking him to rule already carry his ruling, and the
detector that found them was blind on its first run.

THE FINDING. On 2026-10-30, `B47` read `state: OPEN`, `status: PROPOSED`, no
`ruled` date and closed with *"NEEDS HIS RULING."* He had ruled on 2026-10-29 in
words commit `b7cf1566` quotes verbatim -- *"Build and implement option 1. fr"*
-- and the work shipped in that same commit with 14 passing tests and a mechanism
that is live today. `C1` is the same shape from the same commit: *"I accept your
recommendation. fr"*, built as the claim channel entering R_k as a multiplier,
16 passing tests, while the entry's `ruled` field still reads 2026-10-02.

WHY IT MATTERS MORE THAN OTHER STALENESS. Every other kind wastes my time. This
kind queues a decision back to the founder that he has already made, so it wastes
HIS, and it is the `already ruled` failure this project's record names twice.

THE DETECTOR WAS BLIND ON ITS FIRST RUN AND REPORTED 0, WITH B47 SITTING IN THE
HISTORY, READ BY HAND MINUTES EARLIER. 2 predicate errors, both mine, in a
producer written to catch exactly this shape:

  1. It split `git log` output on NEWLINES while requiring the field separator on
     every line, so only the FIRST body line of each commit was examined and
     B47's quotation sits further down. Records are now terminated with `%x1e`.
  2. It passed `--grep=\\bB47\\b` with `-E`; `\\b` is a GNU extension git's POSIX
     ERE does not honour. The grep is now loose and the word boundary is applied
     in Python.

So the FIRST test below is a positive control on a known true positive. A count
assertion would have passed while the detector saw nothing.

AND THE FIRST DISCRIMINATOR FAILED TOO. Matching an MC marker ANYWHERE in a
quotation gave 4 of 19, 3 being the English article "a" matching the `a` command
mid-prose. Requiring the marker to TRAIL the quotation gives 1 of 19 and excludes
all 3. Both halves are pinned below, because a discriminator is only useful if it
discriminates in both directions.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

PRODUCER = (REPO / "scripts"
            / "which_open_entries_already_have_his_ruling_2026-10-30.py")

#: KNOWN TRUE POSITIVES, pinned as a SET with the commit and the exact words.
#: A count would read 2 whether or not it found these 2.
HIS_RULINGS = {
    "B47": ("b7cf1566", "Build and implement option 1. fr"),
    "C1": ("b7cf1566", "I accept your recommendation. fr"),
}

#: MY OWN PROSE, quoted back in my own commit messages. The "marker anywhere"
#: form classified all 3 as his because of the article "a".
NOT_HIS_VOICE = (
    "answering it once would retire a class",
    "on a STILL tree so the figure is a baseline",
    "a local-first general-purpose STEM calculator and experiment instrument",
    "needs no ruling",
    "monotonicity protects the HARD keys either way but the SOFT keys go to "
    "whichever layer merges last",
)


def _producer():
    assert PRODUCER.is_file(), f"producer absent: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("ruled_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _producer()


class TestTheDetectorIsNotBlind:
    """It reported 0 on its first run with a true positive in the history."""

    @pytest.mark.parametrize("ident", sorted(HIS_RULINGS))
    def test_it_finds_the_known_ruling(self, mod, ident):
        sha, words = HIS_RULINGS[ident]
        commits = mod._commits_naming(ident)
        assert commits, (
            f"0 commits name {ident}. The first version of this function split "
            f"git output on newlines and used `\\b` in a POSIX ERE, and reported "
            f"exactly this.")
        hit = [c for c in commits if c["sha"].startswith(sha[:7])]
        assert hit, (
            f"commit {sha} names {ident} in its message but the detector did "
            f"not return it; found {[c['sha'] for c in commits][:6]}")
        text = hit[0]["subject"] + "\n" + hit[0]["body"]
        assert words in text, (
            f"{sha} no longer carries his words {words!r} beside {ident}")

    @pytest.mark.parametrize("ident", sorted(HIS_RULINGS))
    def test_the_quotation_is_harvested_from_a_later_body_line(self, mod, ident):
        """THE EXACT BUG: the quotation is not on the first body line."""
        sha, words = HIS_RULINGS[ident]
        c = [x for x in mod._commits_naming(ident)
             if x["sha"].startswith(sha[:7])][0]
        body_lines = c["body"].split("\n")
        where = [i for i, L in enumerate(body_lines) if words in L]
        assert where, f"{words!r} is not in the body of {sha}"
        assert where[0] > 0, (
            "the quotation is on the FIRST body line, so this test no longer "
            "exercises the multi-line defect it was written for; find a case "
            "that does before weakening it")
        found = mod._quotes_beside(ident, c["subject"] + "\n" + c["body"])
        assert any(words in q or q in words for q in found), (
            f"the quote scanner did not return {words!r} from line "
            f"{where[0]} of the body; it returned {found[:4]}")


class TestTheVoiceDiscriminatorWorksBothWays:
    @pytest.mark.parametrize("ident", sorted(HIS_RULINGS))
    def test_his_verdict_reads_as_his(self, mod, ident):
        assert mod.is_his_voice(HIS_RULINGS[ident][1]) == "fr"

    @pytest.mark.parametrize("quote", NOT_HIS_VOICE)
    def test_my_own_prose_does_not(self, mod, quote):
        """NEGATIVE CONTROL. The 'marker anywhere' form called 3 of these his."""
        assert mod.is_his_voice(quote) is None, (
            f"{quote!r} reads as his verdict. If the marker set has gained a "
            f"common English word the discriminator stops discriminating -- "
            f"which is why `a` is deliberately excluded.")

    def test_the_article_a_is_not_in_the_marker_set(self, mod):
        """THE EXCLUSION AND ITS COST, both asserted.

        * THE FIRST VERSION OF THIS TEST ASSERTED NOTHING. It read
        `assert mod.is_his_voice("do it. a") == "a" if False else True`, which
        Python evaluates as `assert (... == "a") if False else True` -- always
        `True`, and unfailable. An assertion that cannot fail is the
        addition-nothing-reaches defect this project has confirmed 11 times, and
        it appeared in a file written to guard against exactly that.

        THE PROPERTY: `a` is excluded from the marker set, so a quotation whose
        only marker is `a` does NOT read as his voice. That is a deliberate
        trade -- a verdict of his reading only "a" would be missed -- and the
        cost is recorded here rather than hidden, because 3 of 4 hits from the
        unrestricted form were the English article.
        """
        assert mod.is_his_voice("this retires a class") is None, (
            "the article 'a' mid-prose reads as his verdict again")
        assert mod.is_his_voice("do it. a") is None, (
            "a quotation whose only trailing marker is `a` now reads as his "
            "voice. That re-admits the commonest word in English as a "
            "discriminator, which is what made 3 of 4 hits false.")
        assert mod.is_his_voice("do it. y") == "y", (
            "a single-letter marker that is NOT a common English word must "
            "still be recognised, or the exclusion has been over-applied")

    def test_a_trailing_marker_is_required_not_merely_present(self, mod):
        assert mod.is_his_voice("fr is the marker for a feature request") is None
        assert mod.is_his_voice("Build it. fr") == "fr"


class TestTheDecisionItself:
    """SYNTHETIC. The live tree's suspect list is EMPTY once the finding is
    acted on, so pinning it would make this guard fire on its own success.

    * THE FIRST VERSION OF THIS CLASS DID EXACTLY THAT. It asserted that B47
    and C1 are reported as suspects. Closing B47 and advancing C1's `ruled`
    field -- which is what the finding called for -- correctly emptied the list
    and turned the assertion red within the hour. The same defect is recorded
    in `test_admission_counts_announced_apart_from_silent_2026-10-18.py`:
    *"IT FIRED ON SUCCESS ... refused by a guard celebrating its own
    obsolescence."*

    So the DECISION is exercised on inputs no repair can erase, and the live
    scan is checked only for self-consistency.
    """

    def test_an_entry_with_no_ruled_date_and_his_voice_is_a_suspect(self, mod):
        assert mod.is_suspect(True, None, "2026-10-29") is True

    def test_an_entry_ruled_before_his_quoted_ruling_is_a_suspect(self, mod):
        """C1's exact shape: `ruled` read 2026-10-02, the ruling came later."""
        assert mod.is_suspect(True, "2026-10-02", "2026-10-29") is True

    def test_an_entry_ruled_on_or_after_the_commit_is_not(self, mod):
        """The repair must CLEAR the suspicion, or the detector never settles."""
        assert mod.is_suspect(True, "2026-10-29", "2026-10-29") is False
        assert mod.is_suspect(True, "2026-10-30", "2026-10-29") is False

    def test_an_entry_he_never_spoke_on_is_not_a_suspect(self, mod):
        """B50's shape: it asks, and no commit quotes him naming it."""
        assert mod.is_suspect(True, None, None) is False

    def test_an_entry_that_does_not_ask_is_not_a_suspect(self, mod):
        """Without this the detector would flag every entry he ever discussed."""
        assert mod.is_suspect(False, None, "2026-10-29") is False
        assert mod.is_suspect(False, "2026-10-02", "2026-10-29") is False


class TestTheLiveScanIsSelfConsistent:
    """No pinned identifiers here, so acting on a finding cannot fail it."""

    def test_every_reported_suspect_satisfies_the_decision(self, mod):
        a = mod.analyse()
        for r in a["rows"]:
            newest = (r["his_voice_commits"][0]["when"]
                      if r.get("his_voice_commits") else None)
            assert r["suspect_stale"] == mod.is_suspect(
                r["asks_for_a_ruling"], r["ruled_field"], newest), (
                f"{r['ident']} is classified {r['suspect_stale']} but the "
                f"decision function says otherwise on the same inputs; the "
                f"scan and the rule have drifted apart")

    def test_a_suspect_is_never_reported_without_his_voice(self, mod):
        a = mod.analyse()
        for ident in a["suspects"]:
            row = [r for r in a["rows"] if r["ident"] == ident][0]
            assert row["his_voice_commits"], (
                f"{ident} is a suspect with no commit quoting him, so the "
                f"detector is flagging entries merely discussed")
