#!/usr/bin/env python3
"""The generated report and the spoken file must name the SAME decisions.

THE DEFECT THIS GUARDS, 2026-11-01. The generated report derived
{B21, B60, B61, B63}; the spoken file he was handed carried
{B21, B60, B61, B71}. Both said 4, so a count check passes and the sets differ:
1 real decision reached him and another did not. Nothing compared the 2
surfaces, which is the `execute-do-not-grep` shape -- 2 declarations of 1 fact
with no comparator.

AND THE SUPPRESSION THAT CAUSED HALF OF IT. B71 carries a ruling date of
2026-11-01 for the design he settled and was BLOCKED the same day on a
different question. The date comparison cannot separate 2 events on 1 day, so
the ruling was read as settling both. `ruling_is_spent` is the 1 predicate that
now decides this, in place of the same rule written out at 2 call sites.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
CHECK = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"
BUILD = REPO / "scripts" / "morning_report_build_2026-10-12.py"


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def surfaces():
    return _load(CHECK, "surfaces_guard")


@pytest.fixture(scope="module")
def mrb():
    return _load(BUILD, "mrb_guard")


class TestTheSurfacesAgree:
    def test_the_checker_passes_on_the_committed_state(self):
        r = subprocess.run([sys.executable, str(CHECK)], capture_output=True,
                           text=True, cwd=REPO)
        assert r.returncode == 0, (
            "the generated report and the spoken file name different decisions:\n"
            + r.stdout[-2000:])
        assert "AGREE on all" in r.stdout

    def test_every_live_decision_carries_a_join(self, surfaces):
        """A decision with no `spoken_heading` can never be checked."""
        missing = [i for i, h in surfaces.derived() if not h]
        assert not missing, (
            f"no spoken_heading, so unverifiable against the spoken file: {missing}")

    def test_help_is_answered_for_free(self):
        r = subprocess.run([sys.executable, str(CHECK), "--help"],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0
        assert "DO THE 2 DECISION SURFACES AGREE?" not in r.stdout


class TestTheCheckerIsNotVacuous:
    """★ A CHECKER THAT CANNOT FAIL IS THE TRAP THIS PROJECT MET THE SAME DAY,
    when a rule written to stop vacuous decision reporting passed the first file
    it judged by finding 0 items. Each case below drives `main()` with a
    constructed disagreement and requires a non-zero exit."""

    def test_a_derived_decision_absent_from_the_spoken_file_is_caught(
            self, surfaces, monkeypatch, capsys):
        monkeypatch.setattr(surfaces, "derived",
                            lambda: [("B1", "ALPHA"), ("B2", "BETA")])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"), [(1, "ALPHA")]))
        assert surfaces.main() != 0
        assert "DERIVED BUT NOT SPOKEN: BETA" in capsys.readouterr().out

    def test_a_spoken_decision_absent_from_the_record_is_caught(
            self, surfaces, monkeypatch, capsys):
        monkeypatch.setattr(surfaces, "derived", lambda: [("B1", "ALPHA")])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"),
                                     [(1, "ALPHA"), (2, "GAMMA")]))
        assert surfaces.main() != 0
        assert "SPOKEN BUT NOT DERIVED: GAMMA" in capsys.readouterr().out

    def test_a_missing_join_is_caught(self, surfaces, monkeypatch, capsys):
        monkeypatch.setattr(surfaces, "derived", lambda: [("B1", None)])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"), []))
        assert surfaces.main() != 0
        assert "NO JOIN FOR B1" in capsys.readouterr().out

    def test_equal_sets_pass(self, surfaces, monkeypatch):
        monkeypatch.setattr(surfaces, "derived", lambda: [("B1", "ALPHA")])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"), [(1, "ALPHA")]))
        assert surfaces.main() == 0

    def test_the_heading_pattern_reads_both_spellings(self, surfaces):
        """The spoken file writes a bare heading; the markdown writes `### `."""
        found = surfaces._HEADING.findall(
            "DECISION 1. ONE\n### DECISION 2. TWO\nnot a heading\n")
        assert [n for n, _ in found] == ["1", "2"]
        assert [h for _, h in found] == ["ONE", "TWO"]


class TestARulingIsSpentWhenTheEntryStillAsks:
    def test_no_ruling_is_never_spent(self, mrb):
        assert mrb.ruling_is_spent("B71", None, "BLOCKED") is False

    def test_blocked_and_still_asking_is_spent(self, mrb, monkeypatch):
        """B71's own case, now driven SYNTHETICALLY rather than off live state.

        ★ CORRECTED 2026-11-09. This asserted on B71 itself, and B71 was closed
        DONE on 2026-11-08 once his permission arrived and the work was built.
        `ruling_is_spent` consults `still_asks`, which reads the LIVE entry, so
        the test went red the moment its subject was repaired -- a guard that
        needs a live defect, which this project has already recorded as a
        defect of its own. There is now NO blocked entry in the list at all, so
        no substitute ident would help either.

        The BRANCH is what matters and it is exercised directly: a ruled entry
        that is BLOCKED and still asking is spent, whatever the tree happens to
        hold today.
        """
        monkeypatch.setattr(mrb, "still_asks", lambda _i: True)
        monkeypatch.setattr(mrb, "asks_newer_than_the_ruling",
                            lambda _i, _r: False)
        assert mrb.ruling_is_spent("SYNTH", "2026-11-01", "BLOCKED") is True

    def test_not_blocked_is_not_spent_by_that_branch(self, mrb, monkeypatch):
        """ANTI-VACUITY for the monkeypatch. If the patched `still_asks` alone
        made it spent, the BLOCKED discriminator would be doing nothing."""
        monkeypatch.setattr(mrb, "still_asks", lambda _i: True)
        monkeypatch.setattr(mrb, "asks_newer_than_the_ruling",
                            lambda _i, _r: False)
        assert mrb.ruling_is_spent("SYNTH", "2026-11-01", "OPEN") is False

    def test_the_state_is_what_discriminates(self, mrb):
        """A bare still-asks test took the list from 4 to 12 earlier the same
        night, because a ruled entry keeps the sentence that was answered. Only
        BLOCKED entries are rescued by this branch."""
        assert mrb.ruling_is_spent("B71", "2026-11-01", "OPEN") is False
        assert mrb.ruling_is_spent("B71", "2026-11-01", "DONE") is False

    def test_a_blocked_asking_entry_reaches_the_decision_list(self, mrb):
        """THE PROPERTY, not one entry's name.

        ★ CORRECTED 2026-11-09. This named B71 and asserted it was derived.
        B71 closed DONE on 2026-11-08, so the assertion failed for the best
        possible reason -- the entry it guarded had been repaired. The property
        it was protecting is general: an entry that is BLOCKED and still asking
        must appear in the decision list and must not be routed to the work
        section, where he would never be asked the permission it waits on.

        It holds VACUOUSLY when the list carries no such entry, and the live
        count is printed rather than asserted, so a reader can tell the
        difference between "none exist" and "the check stopped looking". The
        branch itself is proven synthetically in
        `TestARulingIsSpentWhenTheEntryStillAsks`.
        """
        items = mrb.task_items() + mrb.study_items()
        decs, missing, orphan = mrb.decisions(items)
        assert not missing and not orphan, (missing, orphan)
        blocked_asking = [
            d for d in decs
            if (d.get("state") or "").upper() == "BLOCKED"
            and mrb.still_asks(str(d["key"]).split(":")[-1])]
        print(f"blocked-and-asking entries in the decision list: "
              f"{len(blocked_asking)}")
        for d in blocked_asking:
            assert not d.get("no_ruling_needed"), (
                f"{d['key']} is BLOCKED and still asking, yet it is routed to "
                f"the work section, so he is never asked the permission it "
                f"waits on")

    def test_the_asking_pattern_reads_a_permission(self, mrb):
        """The pattern had only ruling words, so a permission went unseen."""
        probe = _load(REPO / "scripts"
                      / "how_many_decisions_actually_need_him_2026-11-01.py",
                      "probe_guard")
        for phrase in ("CANNOT BE INSTALLED WITHOUT HIS PERMISSION",
                       "His confirmation of that reading is owed.",
                       "this needs your permission"):
            assert probe.ASKS.search(phrase), phrase
        for phrase in ("the file permission bits were widened",
                       "chmod changed the permissions on his home directory"):
            assert not probe.ASKS.search(phrase), f"false positive: {phrase}"


class TestTheInverseDirectionAlsoHolds:
    """Authored detail with a heading must correspond to a decision the generator renders.

    THE DIRECTION THIS FILE ALREADY COVERED, and it is the loud one:
    `test_every_live_decision_carries_a_join` requires every live decision to
    carry a `spoken_heading`, so he is never asked about something the record
    does not track.

    THE DIRECTION IT DID NOT, found 2026-11-02 by auditing the queue rather than
    by a failure: authored detail that carries a heading while the generator
    renders nothing for it. 10 authored entries carried a heading, the generator
    derived 9, and the 1 difference was C0001 -- so the record said "this is a
    decision to put to him" while the generator said it was not, and he saw
    NEITHER. That direction produces SILENCE rather than a wrong question, which
    is why it survived a guard written to catch divergence, and silent
    under-reporting is the harder failure to see.

    WHY A PINNED SET AND NOT A TOLERANCE. The pin names each identifier allowed
    to carry authored detail without being rendered, with its reason, so a NEW
    one FAILS rather than being absorbed. The project's rule is to pin a set and
    not a count: 2 surfaces once both reported 4 and meant different 4s.
    """

    #: Authored entries that may carry a heading while the generator renders
    #: nothing, each because its SUBSTANCE is settled and only its STATE is open.
    #: C0001 -- his 2026-11-01 scope decision recorded it RECORDED-AND-NOT-
    #: REPAIRED and its subject `_prune_for_coherence` is already retired from
    #: the default path on his ruling of 2026-10-13, so what remains is 1 word on
    #: whether this list should say OPEN or DEFERRED. Raising it as a decision
    #: would ask him to decide again what he has already decided.
    #: B122 -- he RULED it on 2026-11-06 ("I never specified a cap"), so its
    #: substance is settled and only its state is open: it moves to DONE and
    #: COMMITTED when the commit carrying the repair lands. Rendering it as a
    #: decision would ask him to rule again what he has already ruled, which is
    #: the complaint he has now made 5 times. `test_the_pin_is_not_stale`
    #: removes it from here automatically if it is ever rendered again.
    #: ★ 4 ADDED 2026-11-09, EACH FOR THE SAME REASON IN HIS OWN WORDS.
    #: B107, B123 and B128 -- he annotated all 3 on 2026-11-08 with "I accept
    #: your recommendation", and in each case the recommendation was that NO
    #: ACTION is owed. So the substance is settled and only the state is open:
    #: B123 and B128 carry NO evidence path, so `set_marker` correctly refuses
    #: to mark them DONE, and there is no test to name because there is no work.
    #: Rendering them as decisions would ask him to accept again what he has
    #: already accepted, which is the complaint he has now made 5 times.
    #: B20 -- DEFERRED on his ruling of 2026-11-09, verbatim: "As for the
    #: orchestrator experiment, we will run this once everything is cleared."
    #: Its build is complete at 4 of 4 components and the simulated-and-
    #: resumable seam landed 2026-11-08, so what waits is the RUN and it waits
    #: on the queue rather than on him.
    #:
    #: WHY THEY ARE PINNED AND NOT ARCHIVED, which was tried first and was
    #: wrong: removing their authored detail made the report builder REFUSE
    #: with "NO AUTHORED DETAIL for a live item" for all 4, because an entry
    #: the task list still carries as live needs its detail to be reportable at
    #: all. Pinning says the same thing without breaking the builder, and
    #: `test_the_pin_is_not_stale` removes any of them automatically the moment
    #: it is rendered again.
    RENDERED_NOWHERE_BY_DESIGN: tuple[str, ...] = (
        "C0001", "B122", "B107", "B123", "B128", "B20")

    @staticmethod
    def _authored() -> set[str]:
        import json
        p = (REPO / "experimental_notes" / "data" / "morning_report_decisions.json")
        d = json.loads(p.read_text(encoding="utf-8"))
        return {k[5:] for k, v in d.items()
                if k.startswith("task:") and isinstance(v, dict)
                and v.get("spoken_heading")}

    def test_every_authored_heading_is_rendered_or_pinned(self, surfaces):
        rendered = {ident for ident, _ in surfaces.derived()}
        unrendered = sorted(self._authored() - rendered)
        new = [u for u in unrendered if u not in self.RENDERED_NOWHERE_BY_DESIGN]
        assert not new, (
            f"{len(new)} authored decision(s) carry a spoken_heading and are "
            f"rendered nowhere, so the record says he should be asked and he "
            f"never is: {new}. Give the entry an ask the generator reads, or "
            f"remove its authored detail, or pin it WITH ITS REASON.")

    def test_the_pin_is_not_stale(self, surfaces):
        """A pinned identifier that is now rendered must leave the pin.

        Without this the pin accumulates slack by the width of every entry since
        fixed -- the shape the unreached ratchet's own source records, where an
        exemption duplicating a citation loosened the bound silently.
        """
        rendered = {ident for ident, _ in surfaces.derived()}
        stale = [u for u in self.RENDERED_NOWHERE_BY_DESIGN if u in rendered]
        assert not stale, (
            f"{stale} are pinned as rendered nowhere and are now rendered; "
            f"remove them from the pin rather than leaving slack in it")

    def test_the_check_is_not_vacuous(self, surfaces):
        """ANTI-VACUITY. Without this, an empty authored set or an empty
        rendered set would satisfy both tests above on nothing."""
        authored = self._authored()
        rendered = {ident for ident, _ in surfaces.derived()}
        assert len(authored) >= 5, (
            f"only {len(authored)} authored heading(s); the tests above would "
            f"pass on almost nothing")
        assert len(rendered) >= 5, (
            f"only {len(rendered)} rendered decision(s); same problem")
        assert authored & rendered, (
            "the 2 sets are disjoint, which means the identifiers are not "
            "comparable and the comparison above is meaningless")
