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
        assert mrb.ruling_is_spent("B71", "2026-11-01", "BLOCKED") is True, (
            "B71 was ruled and BLOCKED on 1 day on different questions")
        assert mrb.asks_newer_than_the_ruling("B21", "2026-10-17") is True
        assert mrb.asks_newer_than_the_ruling("B21", "2099-01-01") is False, (
            "the other direction: a ruling later than everything still settles it")

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
        assert n == 29, (
            f"the queue is {n}; it was 29 on 2026-11-07 and 36 under the "
            f"rejected fail-open design. If this moved for a real reason, "
            f"re-run the producer and update this pin WITH its reason.")


class TestTheProducerAnswersHisQuestion:
    def test_the_producer_exits_zero_and_its_gate_holds(self):
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0, r.stdout[-3000:]
        out = r.stdout
        assert "NOT NEW:     29 of 29" in out, out[-2000:]
        assert "NOT REPEATS: 0 of 29" in out, out[-2000:]
        assert "B20: REPEAT -> LIVE-AGAIN" in out, (
            "the correction of yesterday's figure must be reproduced, not asserted")

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
        assert "'REPEAT': 7" in r.stdout, (
            "the corrected partition is 7 repeats of 41, not the 10 it reported "
            "under the prefixed key")
