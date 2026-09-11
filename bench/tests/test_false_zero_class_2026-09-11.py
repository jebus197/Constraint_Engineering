"""The 4 false zeros of 2026-09-11, pinned as a CLASS and as 4 individuals.

A SCANNER THAT RESOLVES 1 FORM OF A THING AND REPORTS A FALSE ZERO FOR THE OTHER
has now been confirmed 15 times in this session, 4 of them on 2026-09-11 and 3 of
those inside instruments built to detect it. Every one was fixed individually and
the record of individual fixes preventing the next one is 0 for 15.

So the class check is the gate here: `scripts/false_zero_probe_2026-09-11.py`
takes each real scanner, an input it answers YES about, and transformations that
change FORM and not CONTENT, and requires the answer not to move. The individual
tests below sit under it, each holding a specific measured failure.

EVERY ASSERTION HERE WAS SEEN RED FIRST, by mutating the thing it guards. The
project's own record is that a control written and never seen to fail is usually
vacuous -- one in this session asserted `returncode in (0, 4)`, which no outcome
could violate.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(rel):
    spec = importlib.util.spec_from_file_location(
        pathlib.Path(rel).stem.replace("-", "_"), REPO / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def probe():
    return _load("scripts/false_zero_probe_2026-09-11.py")


@pytest.fixture(scope="module")
def lint():
    return _load("scripts/note_vagueness_lint.py")


@pytest.fixture(scope="module")
def reach():
    return _load("scripts/scripts_are_reached_2026-09-11.py")


@pytest.fixture(scope="module")
def sync():
    return _load("scripts/sync_desktop_mirrors.py")


class TestTheClassCheck:
    def test_no_scanner_flips_under_a_form_change(self, probe):
        """THE GATE. A flip that is not declared in ACCEPTED is a false zero."""
        real = [f for f in probe.run() if f["kind"] != "ACCEPTED"]
        assert not real, "\n".join(
            f"{f['probe']} answered NO under form axis {f['axis']}: {f['why']}"
            for f in real)

    def test_the_probe_is_not_vacuous(self, probe):
        """RED-BY-CONSTRUCTION. Put the old roll-call matcher back and the probe
        must report it. Without this, a probe whose every axis was trivially
        satisfied would read exactly like a probe that works."""
        old = re.compile(r'["\'`]?(scripts/[\w./-]+\.py)["\'`]?,?')
        subject = lambda s: bool(old.fullmatch(s.strip()))  # noqa: E731
        flips = [axis for axis, t in probe.LIST_FORMS
                 if not subject(t("scripts/a_specimen_path_that_is_not_a_real_script.py"))]
        assert subject("scripts/a_specimen_path_that_is_not_a_real_script.py"), \
            "positive control broken: the old matcher rejects the bare form too"
        assert len(flips) >= 4, (
            f"the old matcher was expected to drop the markdown list forms and "
            f"dropped only {flips}; the probe's LIST_FORMS axis is not "
            f"exercising anything")

    def test_every_accepted_flip_carries_a_reason(self, probe):
        """ACCEPTED is a record, never a mute. A blank reason is a mute."""
        for key, why in probe.ACCEPTED.items():
            assert len(why) > 80, f"{key} is silenced without a reason"


class TestTheRollCallMatcher:
    """FALSE ZERO 4: documented list markers that were never implemented."""

    def test_every_markdown_list_form_is_a_roll_call_line(self, reach):
        for form in ("scripts/foo.py", '"scripts/foo.py",', "- scripts/foo.py",
                     "* scripts/foo.py", "+ scripts/foo.py", "1. scripts/foo.py",
                     "- `scripts/foo.py`"):
            assert reach._ROLL_CALL.fullmatch(form.strip()), form

    def test_a_real_reference_is_still_not_a_roll_call_line(self, reach):
        """The whole point of line-wise filtering: a line with other content on
        it is a REAL reference and must keep counting, or the fix that stopped
        the instrument reading everything as reached starts deleting callers."""
        for form in ('SCRIPT = REPO / "scripts/foo.py"',
                     "python3 scripts/foo.py --check",
                     "see scripts/foo.py for the derivation"):
            assert not reach._ROLL_CALL.fullmatch(form.strip()), form


class TestTheUnclosedRegion:
    """FIX 4 WAS INCOMPLETE, and this is the file that shows it.

    A count of begin and end markers is ORDER-BLIND. A stray `verbatim-end`
    followed by an unclosed `verbatim-begin` tallies 1 and 1, so the guard added
    this morning reported BALANCED -- while a region really was open and really
    did exempt every paragraph to the end of the file.
    """

    STRAY = ("Intro paragraph that is definitely long enough to be linted.\n\n"
             "<!-- verbatim-end -->\n\n"
             "Middle paragraph of ordinary prose long enough to reach five.\n\n"
             "<!-- verbatim-begin: fable -->\n\n"
             "The coverage rose and the rate improved and the score moved.\n")

    def test_the_tally_that_shipped_this_morning_says_balanced(self, lint):
        """THE DEFECT, stated as the arithmetic that hid it. Not a mutation of
        the module -- the tally is reproduced here precisely to show that the
        number it computes cannot answer the question that was asked of it."""
        opens = closes = 0
        for para in lint.paragraphs(self.STRAY):
            scan = lint._strip_quoted(para)
            opens += 1 if lint.VERBATIM_BEGIN.search(scan) else 0
            closes += 1 if lint.VERBATIM_END.search(scan) else 0
        assert opens == closes == 1, (opens, closes)
        assert lint.region_state(self.STRAY)["unclosed"], (
            "a region IS open, and the tally above reports balance; if this "
            "ever stops being true the fixture has stopped reproducing")

    def test_the_state_machine_reports_it(self, lint):
        st = lint.region_state(self.STRAY)
        assert st["unclosed"] and st["opened_at"] == 4 and st["stray_closes"] == 1

    def test_partition_counts_the_finding(self, lint, tmp_path):
        p = tmp_path / "stray.md"
        p.write_text(self.STRAY, encoding="utf-8")
        counted, _ = lint.partition(p)
        assert any("UNBALANCED" in c[1] for c in counted), counted

    def test_a_balanced_file_is_not_flagged(self, lint, tmp_path):
        """POSITIVE CONTROL. A guard that fires on everything gates nothing."""
        p = tmp_path / "ok.md"
        p.write_text("Opening paragraph long enough to be linted here now.\n\n"
                     "<!-- verbatim-begin: fable -->\n\n"
                     "A seat wrote that the coverage rose and rate improved.\n\n"
                     "<!-- verbatim-end -->\n\n"
                     "Own voice: the accuracy fell and the precision fell.\n",
                     encoding="utf-8")
        counted, exempted = lint.partition(p)
        assert not any("UNBALANCED" in c[1] for c in counted), counted
        assert exempted, "the exemption stopped working"

    def test_one_implementation_two_callers(self, lint):
        """`verbatim_paragraphs` must DELEGATE. 2 expressions of 1 rule is the
        shape that produced this defect and the 2 before it in this module."""
        text = self.STRAY
        assert lint.verbatim_paragraphs(text) == lint.region_state(text)["marked"]


class TestTheDesktopGuard:
    """FIX 1 LEFT 2 HOLES, and both are reachable without touching the real
    Desktop because the decision now takes its inputs as arguments."""

    REAL = pathlib.Path("/Users/founder/Desktop")
    TMP = [pathlib.Path("/private/var/folders/x/T")]

    def call(self, sync, **kw):
        """ADAPTED TO THE SIGNATURE THAT LANDED, not the seat's own.

        The seat built `refuse_reason_for(..., env, roots, recorded_source)` in
        its sandbox; the version that shipped takes `under_pytest` (a decided
        boolean rather than a whole environment) and `canonical` (the registered
        checkout). Every PROPERTY these tests check is preserved -- only the
        spelling of the call changed. `env={"PYTEST_CURRENT_TEST": ...}` becomes
        `under_pytest=True`, and `recorded_source` becomes `canonical`.
        """
        env = kw.pop("env", None)
        if env is not None:
            kw["under_pytest"] = bool(env.get("PYTEST_CURRENT_TEST"))
        if "recorded_source" in kw:
            kw["canonical"] = kw.pop("recorded_source")
        args = dict(desktop=self.REAL, passwd_desktop=self.REAL,
                    passwd_reliable=True,
                    repo=pathlib.Path("/Users/founder/code/cdsfl"),
                    under_pytest=False, roots=self.TMP,
                    canonical="/Users/founder/code/cdsfl")
        args.update(kw)
        return sync.refuse_reason_for(**args)

    def test_a_clone_outside_the_temp_root_is_refused(self, sync):
        """HOLE 1, MEASURED. With the temp root relocated and nothing else
        changed, the shipped `refuse_reason()` returned None while DESKTOP was
        the founder's real one -- it would have copied a clone's older files
        over the ones he reads. A clone on his own Desktop, in ~/repos, or on
        an external drive escapes a rule that only knows about /tmp."""
        r = self.call(sync, repo=pathlib.Path("/Users/founder/Desktop/cdsfl-clone"),
                      recorded_source="/Users/founder/code/cdsfl")
        assert r is not None and "registered to" in r, r

    def test_sudo_does_not_disable_the_guard(self, sync):
        """HOLE 2, and it is the WORSE direction: it FAILS OPEN. Under sudo the
        passwd entry becomes /var/root, so DESKTOP != passwd_desktop, which the
        shipped guard read as PROOF OF A DRILL and returned None on -- skipping
        every remaining rule. One sudo turned the whole guard off."""
        r = self.call(sync, passwd_desktop=pathlib.Path("/var/root/Desktop"),
                      passwd_reliable=False,
                      repo=pathlib.Path("/private/var/folders/x/T/clone"))
        # ANY correct refusal satisfies this test's claim, which is that sudo
        # does not turn the guard off. The shipped guard refuses this case on the
        # passwd rule before it reaches the scratch rule -- a different reason,
        # the same verdict. Asserting the exact sentence would pin the ORDER of
        # the rules, which is not the property under test.
        assert r is not None, "sudo turned the guard off"
        assert ("clone or a scratch fixture" in r) or ("passwd database" in r), r

    def test_a_container_with_no_passwd_entry_is_refused(self, sync):
        r = self.call(sync, passwd_reliable=False)
        assert r is not None and "passwd database" in r, r

    def test_a_drill_pointing_elsewhere_is_still_never_refused(self, sync):
        """THE SECOND FAILURE IS WORSE THAN THE FIRST. Refusing a drill would
        make this a disabled feature, and the existing mirror fixtures point
        DESKTOP at a temp directory on purpose."""
        assert self.call(sync, roots=sync.scratch_roots(),
                         desktop=pathlib.Path("/tmp/fixture/Desktop"),
                         repo=pathlib.Path("/private/var/folders/x/T/clone"),
                         env={"PYTEST_CURRENT_TEST": "x"}) is None

    def test_the_founders_own_checkout_still_refreshes(self, sync):
        """AND THE BLOCKING FAILURE IS THE ONE TO FEAR. His own commit, from
        his own checkout, must pass every rule."""
        assert self.call(sync, recorded_source="/Users/founder/code/cdsfl") is None
        assert self.call(sync, recorded_source=None) is None

    def test_a_suite_run_on_the_real_desktop_is_still_refused(self, sync):
        r = self.call(sync, env={"PYTEST_CURRENT_TEST": "x"})
        assert r is not None and "a test is running" in r, r

    def test_the_temp_roots_are_resolved(self, sync):
        """macOS /var -> /private/var. REPO is resolved at import; the roots
        must be resolved too or the containment silently never matches."""
        for r in sync.scratch_roots():
            assert r == r.resolve(), r

    def test_bytes_are_never_destroyed(self, sync, tmp_path):
        """THE RULE THAT IS WRONG IN NONE OF THE ABOVE CASES. Every other rule
        here is a rule about PATHS, and paths can be misidentified by sudo, a
        missing passwd entry, a network home or a clone nobody thought of. The
        2026-09-11 recovery was luck. This makes it design."""
        dst = tmp_path / "CDSFL_OUTCOMES_LOG.md"
        dst.write_text("the founder's 34,082 bytes", encoding="utf-8")
        kept = sync.preserve_before_overwrite(dst)
        dst.write_text("a clone's older 27,669 bytes", encoding="utf-8")
        assert kept is not None and kept.is_file()
        assert kept.read_text(encoding="utf-8") == "the founder's 34,082 bytes"

    def test_nothing_is_kept_when_there_is_nothing_to_lose(self, sync, tmp_path):
        assert sync.preserve_before_overwrite(tmp_path / "absent.md") is None
