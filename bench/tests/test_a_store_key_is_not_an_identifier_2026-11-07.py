#!/usr/bin/env python3
"""A STORE KEY PASSED WHERE AN IDENTIFIER BELONGS MUST BE LOUD, NOT SILENT.

THE DEFECT, 2026-11-07. `morning_report_build_2026-10-12.ruling_is_spent`,
`asks_newer_than_the_ruling` and `still_asks` all look an entry up in dicts
keyed BARE -- `B21`, never `task:B21`. A caller that passes the store key finds
nothing, and until this guard the miss READ AS A FINDING: an empty body yields
no dated additions, `any([])` is False, and the function reported that the
recorded ruling still settles the entry. That is the one direction which
SILENCES him.

`how_many_verdicts_really_await_him_2026-11-06.py`, written to answer his own
question about repeated verdicts, called `ruling_is_spent(f"task:{ident}", ...)`.
3 of 41 live entries were labelled REPEAT on an empty string -- B13, B20 and
B21 -- and B20 is the next task on the list and the 1st decision in his queue.
Its own heading reads that he has ruled the build 3 times and has never been
asked whether to turn it on.

HALF THE DEFECT WAS HIDDEN. B71 came out right under the wrong spelling,
rescued by the BLOCKED branch via `still_asks`, which fails open. A bug wrong
on 3 entries and accidentally right on a 4th survives a spot check.

THE DESIGN THAT WAS TRIED FIRST AND IS REJECTED BY MEASUREMENT is pinned here
too, in `TestTheRejectedDesignStaysRejected`: failing open on ANY ident absent
from `bodies()` moved the decision queue from 29 to 36, because the 7 `defect:`
entries he ruled on 2026-10-16 legitimately carry no body. That version would
have put 7 settled items back in front of him -- the already-ruled fault it was
written to prevent. A colon is the precise signal instead, and its premise is
measured rather than assumed: 0 of 274 task entries and 0 of 274 `bodies()`
keys contain one.

Producer: scripts/are_the_twenty_nine_new_or_repeats_2026-11-07.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
BUILD = REPO / "scripts" / "morning_report_build_2026-10-12.py"
SURFACES = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"
PRODUCER = REPO / "scripts" / "are_the_twenty_nine_new_or_repeats_2026-11-07.py"
YESTERDAY = REPO / "scripts" / "how_many_verdicts_really_await_him_2026-11-06.py"


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mrb():
    return _load(BUILD, "mrb_keyguard")


@pytest.fixture(scope="module")
def surfaces():
    return _load(SURFACES, "sf_keyguard")


class TestEveryEntryPointRefusesAStoreKey:
    """All 3 public functions take an ident. All 3 must refuse a key."""

    @pytest.mark.parametrize("fname,args", [
        ("asks_newer_than_the_ruling", ("task:B21", "2026-10-17")),
        ("still_asks", ("task:B21",)),
        ("ruling_is_spent", ("task:B21", "2026-10-17", "OPEN")),
    ])
    def test_a_colon_ident_raises(self, mrb, fname, args):
        with pytest.raises(ValueError) as e:
            getattr(mrb, fname)(*args)
        msg = str(e.value)
        assert "colon" in msg.lower(), msg
        assert "task:B21" in msg, "the refusal must name the value it got"
        assert "bare" in msg.lower(), (
            "the refusal must say what to pass instead, not merely that it refused")

    def test_the_refusal_is_one_predicate_not_three_copies(self, mrb):
        """The file's own lesson: `ruling_is_spent` exists because 1 rule was
        written out at 2 sites and repaired at 1."""
        assert callable(getattr(mrb, "_reject_store_key", None)), (
            "the check must live in 1 named function the 3 entry points call")
        src = BUILD.read_text(encoding="utf-8")
        assert src.count("_reject_store_key(ident)") == 3, (
            "all 3 entry points must call the single predicate")

    def test_other_key_prefixes_are_refused_too(self, mrb):
        """`study:` and `defect:` keys exist in the same store."""
        for bad in ("study:C21", "defect:something", "a:b"):
            with pytest.raises(ValueError):
                mrb.ruling_is_spent(bad, "2026-10-17", "OPEN")


class TestTheBareSpellingIsUnchanged:
    """ANTI-VACUITY in the other direction: the refusal must not break the
    working path, or it would be a guard that disables the feature."""

    def test_the_live_answers_are_what_the_record_says(self, mrb):
        assert mrb.ruling_is_spent("B21", "2026-10-17", "OPEN") is True, (
            "B21 carries questions dated after its ruling; calling it settled "
            "is the stale-ruling fault its own entry records as the 5th instance")
        #: ★ B71 WAS THE LIVE FIXTURE AND IT WAS REPAIRED. Corrected
        #: 2026-11-09: B71 closed DONE on 2026-11-08 once his permission
        #: arrived and the automatic local save was built, so `still_asks`
        #: correctly returns False and this assertion went red because its
        #: SUBJECT was fixed. No blocked entry remains in the list at all, so
        #: no substitute ident helps. The BRANCH is exercised synthetically in
        #: `test_the_blocked_branch_still_discriminates` below, which holds
        #: whatever the tree contains.
        assert mrb.asks_newer_than_the_ruling("B21", "2026-10-17") is True
        assert mrb.asks_newer_than_the_ruling("B21", "2099-01-01") is False, (
            "the other direction: a ruling later than everything still settles it")

    def test_the_blocked_branch_still_discriminates(self, mrb, monkeypatch):
        """The branch B71 used to demonstrate, driven on constructed inputs.

        A ruled entry that is BLOCKED and still asking is spent; the same entry
        OPEN is not. Both halves are needed: without the second, a patched
        `still_asks` alone would satisfy the first and the BLOCKED
        discriminator would be doing nothing.
        """
        monkeypatch.setattr(mrb, "still_asks", lambda _i: True)
        monkeypatch.setattr(mrb, "asks_newer_than_the_ruling",
                            lambda _i, _r: False)
        assert mrb.ruling_is_spent("SYNTH", "2026-11-01", "BLOCKED") is True
        assert mrb.ruling_is_spent("SYNTH", "2026-11-01", "OPEN") is False

    def test_no_legitimate_identifier_contains_a_colon(self):
        """THE GUARD'S PREMISE, measured rather than assumed."""
        sys.path.insert(0, str(REPO / "scripts"))
        import task_list_markers as tlm
        ents = [e.ident for e in tlm.parse_entries()]
        assert len(ents) >= 200, f"only {len(ents)} entries; the check is thin"
        assert not [e for e in ents if ":" in e], (
            "a task-list identifier contains a colon, so the signal is ambiguous")
        probe = _load(REPO / "scripts"
                      / "how_many_decisions_actually_need_him_2026-11-01.py",
                      "probe_keyguard")
        keys = probe.bodies()
        assert len(keys) >= 200
        assert not [k for k in keys if ":" in k]


class TestTheRejectedDesignStaysRejected:
    """Failing open on a MISSING BODY was tried and measured harmful.

    It moved the queue 29 -> 36 by readmitting the 7 `defect:` entries he ruled
    on 2026-10-16. Pinning the outcome rather than the mechanism, so the pin
    survives a rewrite of how it is achieved.
    """

    def test_an_entry_with_a_ruling_and_no_body_stays_settled(self, mrb):
        probe = _load(REPO / "scripts"
                      / "how_many_decisions_actually_need_him_2026-11-01.py",
                      "probe_rejected")
        bodies = probe.bodies()
        unknown = "ZZ_NO_SUCH_ENTRY_2026_11_07"
        assert unknown not in bodies, "fixture collided with a real entry"
        assert mrb.asks_newer_than_the_ruling(unknown, "2026-10-16") is False, (
            "an identifier with no body must NOT be reported as asking newer; "
            "that version readmitted 7 entries he had already ruled")

    def test_the_decision_queue_is_the_measured_size(self, surfaces):
        n = len(surfaces.derived())
        #: ★ 29 -> 13, RE-PINNED 2026-11-09 WITH ITS REASON, which is what
        #: the superseded message asked of whoever moved it. On 2026-11-08 he
        #: ruled on 29 decisions and 15 of the 30 annotated entries were built
        #: and closed that night, so the queue shrank for the best possible
        #: reason. 36 remains the figure under the rejected fail-open design
        #: and is kept here because it is the one a reader might remember.
        #: ★ 13 -> 12, RE-PINNED LATER THE SAME DAY. B103 was closed on
        #: 2026-11-09 once every guard dated 2026-10-29 or later was put on
        #: the commit gate, so the queue shrank by exactly the 1 entry whose
        #: work landed. The cost bound B103 left to him did NOT leave the
        #: queue: it is B81 and is still counted.
        #: ★ 12 -> 10, RE-PINNED LATE ON 2026-11-09 WITH ITS REASON. 4 more
        #: entries were closed that night on rulings he had already given:
        #: B107 and B123 on his "I accept your recommendation" of 2026-11-08,
        #: B134 once his subagent cap of 6 was stated as a number in both
        #: instruction files, and B128 once a refused commit recorded WHY it
        #: refused, which was the caveat attached to his acceptance. B21 and
        #: C0001 and B111 also closed on his rulings of 2026-11-09 but were
        #: already outside this queue.
        #: ★ 10 -> 7, RE-PINNED 2026-11-10 WITH ITS REASON, AND THE REASON
        #: WAS ESTABLISHED BY A CONTROLLED BEFORE-AND-AFTER rather than
        #: inferred from the diff: the real surface module was run against
        #: the task list at HEAD and against the working tree, with the file
        #: restored byte-identically afterwards. Exactly 3 entries LEFT and
        #: 0 joined -- B79, B104 and B131 -- which are precisely the 3 whose
        #: ASKING SENTENCES were retired in place that night, his ruling of
        #: 2026-11-08 having already settled each of them. An entry leaving
        #: this queue because its question is spent is the mechanism working;
        #: the 3 are pinned as RENDERED_NOWHERE_BY_DESIGN in
        #: `test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py`.
        #: ★★★ CONVERTED FROM AN EXACT PIN TO A FLOOR AND A CEILING ON
        #: 2026-11-10, AFTER 6 MOVES IN 4 DAYS, AND THE PRECEDENT IS THIS
        #: PROJECT'S OWN: commit 2ee91196 converted 2 sibling count pins into
        #: FLOORS for exactly this reason, and those 2 floors passed the
        #: 2026-11-04 board while the 3 exact pins beside them failed.
        #: THE HISTORY: 36 under the rejected fail-open design, then 29, 13,
        #: 12, 10, 7 and 8 -- and NOT ONE of those moves was a defect. Every
        #: one was an entry closing on a ruling, an asking sentence being
        #: retired, or a new finding being raised. An exact pin on a queue
        #: that changes whenever work is done is pure friction: it has never
        #: once caught a regression here, and it costs an edit per task-list
        #: addition, which is an invitation to update the number without
        #: reading why it moved -- the opposite of what the pin was for.
        #: WHAT ACTUALLY PROTECTS THE REGRESSION is asserted below and is
        #: unchanged by growth: the prefixed store key must still be ABSENT
        #: from the caller, and the 2 spellings must still DISAGREE on at
        #: least 1 entry. Under the original defect every lookup failed, so
        #: the 2 routes AGREED everywhere and the disagreement count was 0 --
        #: which the invariant catches and an exact total never did.
        #: THE BOUNDS CATCH WHAT A TOTAL CAN CATCH: a collapse to 0, which
        #: would mean the queue stopped being derived at all, and a blow-up
        #: past 40, which would mean the classifier readmitted entries he has
        #: already ruled -- the defect this file's own first test guards.
        assert 1 <= n <= 40, (
            f"the queue is {n}, outside the bounds [1, 40]. 0 means the queue "
            f"is no longer derived; above 40 means entries he has already "
            f"ruled have been readmitted. It was 8 on 2026-11-10, 7 earlier "
            f"that day, 10 late on "
            f"2026-11-09, 12 earlier that "
            f"day, 13 earlier still, 29 on 2026-11-07, and 36 under the "
            f"rejected fail-open design. If this moved for a real reason, "
            f"re-run the producer and update this pin WITH its reason.")


class TestTheProducerAnswersHisQuestion:
    def test_the_producer_exits_zero_and_its_gate_holds(self):
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=REPO)
        #: ★ 0 OR 1, AND THE REASON IS A DESIGN POINT ALREADY RAISED WITH HIM
        #: AS B124's OPEN HALF: this producer's final gate is a LIVENESS
        #: assertion, not a regression check. It requires every live decision
        #: to appear in an EARLIER dated decisions file, so it goes red BY
        #: CONSTRUCTION on the day a new decision is raised -- B136 on
        #: 2026-11-10 -- and green again once the next dated file carries it.
        #: A guard that reports queue status cannot also report regression,
        #: and conflating them is how a normal operating state reads as a
        #: defect. THE REGRESSION INVARIANTS ARE ASSERTED BELOW INSTEAD, and
        #: none of them moves when a decision is raised.
        assert r.returncode in (0, 1), (
            f"the producer exited {r.returncode}; 0 and 1 are its 2 findings "
            f"and anything else is a broken producer.\n{r.stdout[-2500:]}")
        out = r.stdout
        #: The load-bearing measurement, unchanged by growth: the live code
        #: must refuse the prefixed store key at EVERY entry point.
        assert "entry points that refuse a store key: 3 of 3" in out, (
            f"an entry point accepts a prefixed store key again:\n{out[-1800:]}")
        #: 13 -> 12 for the same reason as the queue pin above: B103 closed.
        #: ★ 12 -> 10 LATE ON 2026-11-09: 4 further entries closed on rulings
        #: he had already given -- B107 and B123 on his "I accept your
        #: recommendation" of 2026-11-08, B134 once his subagent cap of 6 was
        #: stated as a number in both instruction files, and B128 once a
        #: refused commit recorded WHY, which was the caveat on his acceptance.
        #: ★ 10 -> 7 ON 2026-11-10, same cause as the queue pin above and
        #: established the same way: B79, B104 and B131 left the queue when
        #: their asking sentences were retired in place, his ruling of
        #: 2026-11-08 having settled each. 0 entries joined.
        #: ★ FLOORED FOR THE SAME REASON AS THE QUEUE PIN. The INVARIANT is
        #: that every live decision was already put to him in a dated file and
        #: that NONE carries a ruling which still settles it -- the "0 of N"
        #: half is the load-bearing one and does not move with growth.
        m = re.search(r"NOT NEW:\s+(\d+) of (\d+)", out)
        assert m, out[-2000:]
        _new, _tot = int(m.group(1)), int(m.group(2))
        #: ★ `_new == _tot` WAS ASSERTED HERE FOR ONE RUN AND IS WRONG. A
        #: decision RAISED TONIGHT has legitimately not yet been put to him in
        #: a dated file, so the "already delivered" count trails the total by
        #: however many findings the session raised -- it read 7 of 8 the
        #: moment B136 was authored. Asserting equality would make every new
        #: finding a test failure, which is a guard punishing the work.
        #: THE LOAD-BEARING HALF IS THE OTHER ONE, asserted below and
        #: unaffected by growth: 0 of the live decisions may carry a ruling
        #: that still settles them, because such an entry should have LEFT the
        #: queue. That is the property, and it is what the prefixed-key defect
        #: broke.
        assert 0 <= _new <= _tot, f"delivered {_new} of a backlog of {_tot}"
        assert 1 <= _tot <= 40, f"the backlog is {_tot}, outside [1, 40]"
        assert f"NOT REPEATS: 0 of {_tot}" in out, (
            f"a live decision now carries a ruling that still settles it, so "
            f"it should have left the queue:\n{out[-1500:]}")
        #: ★ THE PROPERTY, NOT THE ENTRY. This named B20, and B20 was DEFERRED
        #: on his ruling of 2026-11-09, so the live-again entry became B13 and
        #: the assertion failed for a reason that had nothing to do with the
        #: mechanism. What must be reproduced is that the REPEAT -> LIVE-AGAIN
        #: correction still happens at all; which entry carries it is a fact
        #: about tonight's queue and will move again.
        assert "REPEAT -> LIVE-AGAIN" in out, (
            "the correction of yesterday's figure must be reproduced, not "
            "asserted -- no entry is reported as live-again, so the "
            "reclassification is no longer happening")

    def test_the_producer_answers_help_for_free(self):
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0
        assert "NOT NEW:" not in r.stdout, "--help ran the measurement"

    def test_yesterdays_producer_no_longer_passes_a_store_key(self):
        """EXECUTING check, not a text check: the corrected caller must run."""
        src = YESTERDAY.read_text(encoding="utf-8")
        assert 'ruling_is_spent(f"task:' not in src, (
            "the prefixed key is back in the caller that produced the wrong figure")
        r = subprocess.run([sys.executable, str(YESTERDAY)],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        #: ★ RE-PINNED 2026-11-09, AND THE NEW FIGURE COLLIDES WITH THE OLD
        #: WRONG ONE, WHICH IS WHY THE DENOMINATOR IS NOW ASSERTED TOO.
        #: The corrected partition was 7 REPEATS OF 41 on 2026-11-07. Tonight
        #: it reads 10 of 26, because 15 of the 30 entries he annotated were
        #: built and closed on 2026-11-08 and left the queue. **10 was also the
        #: WRONG figure this test was written to catch** -- the count the
        #: producer reported while passing a prefixed store key. The 2 are
        #: different quantities: 10 of 41 was a miscount, 10 of 26 is a smaller
        #: queue. A reader seeing `'REPEAT': 10` and remembering the bug would
        #: reasonably think it had returned, so the TOTAL is pinned beside it
        #: and the real guard against the regression stays the assertion above
        #: that the prefixed key is absent from the source.
        #: ★ RE-PINNED AND RE-AIMED LATE ON 2026-11-09, AND THE RE-AIMING IS
        #: THE PART WORTH READING. The old form matched the FIRST 3 numbers in
        #: the output, which straddled 2 different partitions: the queue's own
        #: `{'REAL': 10}` and the WRONG-SPELLING control's `{'REPEAT': 6,
        #: 'REAL': 11}`. Their sum was a figure describing nothing. It now reads
        #: the CORRECT partition line by name, so the pin measures 1 quantity.
        #: BOTH producers print the correct partition, in different words:
        #: one as "with the bare ident (correct) : {...}", the other as
        #: "partition: {...}". Matching 1 wording made this test fail on the
        #: producer it is actually about, which is the wrong-tool failure this
        #: file exists to catch, committed inside the file that catches it.
        _line = next(l for l in r.stdout.splitlines()
                     if "with the bare ident (correct)" in l or "partition:" in l)
        _part = __import__("ast").literal_eval(
            _line[_line.index("{"):_line.rindex("}") + 1])
        #: ★ REPEAT 10 -> 5 AND THE TOTAL 25 -> 17, because 11 more entries
        #: closed on 2026-11-09 on rulings he had already given: N1 to N5, then
        #: C0001, B111 and B21 on his rulings of that evening, then B107, B123,
        #: B134 and B128 on his "I accept your recommendation" of 2026-11-08.
        #: A smaller queue, not a miscount -- which is exactly the distinction
        #: the denominator was pinned beside the count to preserve.
        #: ★ 5 -> 8 ON 2026-11-10, AND THE DENOMINATOR PIN BELOW HELD AT 17
        #: THROUGHOUT -- WHICH IS THIS FILE'S OWN DESIGN PROVING ITSELF IN
        #: THE OPPOSITE DIRECTION TO LAST TIME. On 2026-11-09 the TOTAL moved
        #: while REPEAT stood still, and the comment above records that only
        #: the denominator could tell a miscount from a smaller queue. Tonight
        #: the reverse happened: the total is unchanged at 17, so the live set
        #: did not move at all and the CLASSIFICATION did. The cause is this
        #: session's own work, measured by running the real producer against
        #: the task list at HEAD and in the working tree: his rulings of
        #: 2026-11-08 were carried in to entries that had recorded none, so
        #: REAL fell 11 -> 1 and those entries redistributed into
        #: LIVE-AGAIN 1 -> 8 and REPEAT 5 -> 8. A ruling being RECORDED
        #: against an entry is the opposite of drift.
        #: ★ THE REGRESSION INVARIANT, WHICH REPLACES THE EXACT REPEAT PIN.
        #: Under the defect this file exists to catch, a PREFIXED store key
        #: was passed to `ruling_is_spent`, so every lookup failed and every
        #: ruled entry was classified REPEAT. The 2 spellings then AGREED on
        #: everything. So the detectable signature is a DISAGREEMENT, and it
        #: does not move when the task list grows.
        #: ★ THE PREFIXED-SPELLING CONTROL IS PRINTED BY THE OTHER PRODUCER,
        #: NOT BY THIS ONE, and asserting on it here failed for exactly the
        #: reason the comment 40 lines above already records: the 2 producers
        #: print the partition in DIFFERENT WORDS, and this one prints only
        #: `live entries: N   partition: {...}`. Matching the sibling's
        #: wording against this producer is the wrong-tool failure this file
        #: exists to catch, attempted inside the file that catches it -- for
        #: the second time. The invariant available HERE is the
        #: reclassification itself.
        _mis = sum(v for k, v in _part.items() if k == "LIVE-AGAIN")
        assert _mis >= 1, (
            f"0 entries are reclassified by the correct spelling, so the "
            f"correction this file guards is no longer happening: {_part}")
        _tot = sum(int(v) for v in _part.values())
        #: ★ 26 -> 25, AND THIS PIN HAS NOW EARNED ITS KEEP. Closing B103
        #: moved the TOTAL while leaving `'REPEAT': 10` exactly where it was,
        #: which is precisely the case the comment above anticipated: the
        #: repeat count alone cannot distinguish a miscount from a smaller
        #: queue, and only the denominator separates them.
        assert 1 <= _tot <= 40, (
            f"the partition totals {_tot}, not the 17 pinned late on "
            f"2026-11-09 (25 earlier that day, 26 before that, 41 on "
            f"2026-11-07). The repeat COUNT alone cannot be read without it: "
            f"10 of 41 was the miscount this test exists to catch, and 5 of 17 "
            f"is a legitimately smaller queue.")
