# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9154ecb5798e429dcec39746d077ec4b12cd89b2f5d95194f7beef9f2ca8870e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The key-access ADVISORY must be silent on a LOCATION ARTEFACT, and loud on a read.

THE DEFECT THIS PINS, measured 2026-10-02 before the repair. The merged
advisory/audit split in `bench/key_access_forensics.py` was accepted on the
evidence of `scripts/advisory_channel_selection_2026-10-02.py`, whose published
figure is "run 1b 0 advisory / 7 audit". Re-executed from a checkout at a
different absolute path, that producer DIED on its own
`assert not fires`, reporting 107 advisory / 7 audit. Every one of the 107
literals begins `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`
-- the root the run was RECORDED on. The reads were in scope when they happened;
only the root string moved.

So the merge left a false positive 15x larger than the one it was built to kill
(107 against 7), in the one direction that matters: the advisory fired on a run
in which no key was read, which is precisely the founder ruling it implements
("If no key was accessed, say nothing").

THE REPAIR, and it is the merge's OWN ruling applied once more: the test decides
the CHANNEL, never whether the hit survives. A foreign-checkout artefact goes to
AUDIT; nothing is dropped. The predicate is NOT a third implementation -- it is
`bench.repo_paths.names_this_checkout`, promoted verbatim out of
`scripts/archived_falsifier_rejections_2026-09-10.py` so both consumers of the
identical question share one rule.

THE CANNOT-FAIL GUARD IS THE POINT OF THIS FILE. A reclassification rule that
silences everything would pass "run 1b is quiet" and be worse than no rule at
all -- this project has shipped that twice (`check_sk_threshold` hardwired to
`return True` passed 321 tests; A19's `e4_bandit` reported 0 HIGH forever).
`TestTheGuardCannotBeBlanket` therefore stubs the predicate to always-True --
the maximally permissive form of this fix -- and requires a real key read to
fire ANYWAY. If that test can be made to pass with the detector disabled, the
detector is decoration.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench import key_access_forensics as KAF  # noqa: E402

RUN_1B = (REPO / "bench" / "logs"
          / "prose_convergence_run1b_2026-10-02_20261002T044234Z")
ALIEN_ROOT = "/Users/georgejackson/Developer_Projects/Constraint_Engineering"


def _scan(run: pathlib.Path):
    return KAF.scan_run(run, repo_root=REPO)


def _plant(body: str) -> pathlib.Path:
    """A run directory holding one carried source file containing `body`."""
    td = pathlib.Path(tempfile.mkdtemp())
    dest = td / "fake_run" / "panel_worktree_harvest" / "files" / "bench"
    dest.mkdir(parents=True)
    (dest / "falsifier_verify.py").write_text(
        (REPO / "bench" / "falsifier_verify.py").read_text() + "\n" + body,
        encoding="utf-8")
    return td / "fake_run"


# ── the defect itself ────────────────────────────────────────────────────────

@pytest.mark.skipif(not RUN_1B.is_dir(), reason="run 1b not in this tree")
class TestRun1bIsQuiet:
    def test_the_advisory_does_not_fire_on_run_1b(self):
        rep = _scan(RUN_1B)
        assert KAF.build_end_of_run_advisory(rep) is None, (
            "the advisory fired on a run in which no key was read; "
            f"{len(rep.advisory_confirmed)} advisory hit(s), first = "
            f"{rep.advisory_confirmed[0] if rep.advisory_confirmed else None}")

    def test_every_foreign_checkout_hit_is_retained_on_the_audit_channel(self):
        rep = _scan(RUN_1B)
        assert len(rep.advisory_confirmed) + len(rep.audit_confirmed) \
            == len(rep.confirmed), "a CONFIRMED hit left the record entirely"
        assert len(rep.audit_confirmed) == 114, (
            "the artefact count moved; the archive or the predicate changed")

    def test_the_artefacts_really_do_name_the_recording_checkout(self):
        rep = _scan(RUN_1B)
        foreign = [h for h in rep.audit_confirmed if h.foreign_checkout]
        assert len(foreign) == 107
        assert all(ALIEN_ROOT in h.snippet or "/Constraint_Engineering" in h.snippet
                   for h in foreign)


# ── the cannot-fail guard ────────────────────────────────────────────────────

class TestTheGuardCannotBeBlanket:
    """With the predicate stubbed to its most permissive possible form, a real
    key read must STILL fire. This is the test that would have caught
    `check_sk_threshold: return True`."""

    def test_a_planted_key_read_fires_even_with_the_predicate_always_true(
            self, monkeypatch):
        monkeypatch.setattr(KAF, "names_this_checkout", lambda *a, **k: True)
        run = _plant("k = json.load(open('/Users/x/exp99_answer_key.json'))\n")
        rep = _scan(run)
        adv = KAF.build_end_of_run_advisory(rep)
        assert adv is not None, (
            "THE GUARD IS A BLANKET SILENCER: with names_this_checkout stubbed "
            "to always-True a planted answer-key read did not fire. The "
            "reclassification must be reachable ONLY through the out-of-scope "
            "branch, never through the key-material patterns.")
        assert adv["advisory_hit_count"] >= 1

    def test_a_key_read_under_the_FOREIGN_root_still_fires(self):
        """The sharpest form: the bypass recipe is to park the key read behind
        the recording machine's own root, so the artefact rule absorbs it."""
        run = _plant(
            f"k = json.load(open('{ALIEN_ROOT}/bench/exp99_answer_key.json'))\n")
        rep = _scan(run)
        assert KAF.build_end_of_run_advisory(rep) is not None, (
            "a key read hidden behind the recording checkout's root was "
            "absorbed by the location-artefact rule")

    def test_the_predicate_fails_closed_on_paths_this_tree_does_not_hold(self):
        from bench.repo_paths import names_this_checkout as n
        assert n(f"{ALIEN_ROOT}/bench", REPO) is True
        for alien in ("/Users/x/exp99_answer_key.json", "/etc/passwd",
                      "/Users/x/Constraint_Engineering/no/such/file.py"):
            assert n(alien, REPO) is False, f"absorbed {alien}"


# ── the merge's original property is not regressed ───────────────────────────

class TestTheMergeStillDominates:
    def test_a_faithful_self_copy_is_silent_and_a_plant_is_loud(self):
        quiet = _scan(_plant(""))
        assert KAF.build_end_of_run_advisory(quiet) is None
        assert len(quiet.audit_confirmed) > 0, "evidence was dropped, not moved"

        loud = _scan(_plant(
            "k = json.load(open('/Users/x/exp99_answer_key.json'))\n"))
        assert KAF.build_end_of_run_advisory(loud) is not None
        assert len(loud.advisory_confirmed) + len(loud.audit_confirmed) \
            == len(loud.confirmed)


class TestTheRuleIsNotDuplicated:
    def test_the_archived_rejections_script_delegates_to_the_shared_predicate(self):
        src = (REPO / "scripts"
               / "archived_falsifier_rejections_2026-09-10.py").read_text()
        assert "from bench.repo_paths import names_this_checkout" in src, (
            "the script carries its own copy of the rule again")
