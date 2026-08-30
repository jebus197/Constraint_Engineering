"""Commissioned tests for the fix-efficacy probe.

The probe answers one question the live loop has never asked: does a finding's
proposed fix cure the defect that finding's OWN falsifier demonstrates?

Every guard is fed both a case it must pass and a case it must refuse. The two
INDETERMINATE guards matter most: they are the two ways a SOUND fix could be
falsely condemned, and both are checked before any verdict can be produced.
"""
import pathlib
import shutil
import sys
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

from bench.fix_efficacy import (            # noqa: E402
    FIX_CURES, FIX_INEFFECTIVE, NOT_INTERCEPTED, NO_BASELINE, NO_FIX,
    FixEfficacyResult, probe,
)

TARGET_REL = "bench/toy_target.py"
CLEAN = 'VALUE = 10\n\n\ndef get():\n    return VALUE\n'
BUGGY = 'VALUE = -1\n\n\ndef get():\n    return VALUE\n'


@pytest.fixture
def repo(tmp_path):
    """A throwaway repo root holding one target under bench/."""
    (tmp_path / "bench").mkdir()
    (tmp_path / TARGET_REL).write_text(BUGGY, encoding="utf-8")
    return tmp_path


def _falsifier(repo_root: pathlib.Path) -> str:
    """Reads the target by ABSOLUTE path, so _retarget_falsifier redirects it."""
    return textwrap.dedent(f'''
        import pathlib
        src = pathlib.Path(r"{repo_root / TARGET_REL}").read_text()
        if "VALUE = -1" in src:
            raise AssertionError("FALSIFIED: VALUE is negative")
    ''').strip()


def _fix(old: str, new: str) -> str:
    return f"```\n<<<<<<< SEARCH\n{old}\n=======\n{new}\n>>>>>>> REPLACE\n```"


# --------------------------------------------------------------------------- #
# The two verdicts                                                             #
# --------------------------------------------------------------------------- #
def test_a_fix_that_cures_its_own_falsifier(repo):
    r = probe({"falsifier_code": _falsifier(repo),
               "proposed_fix": _fix("VALUE = -1", "VALUE = 10")},
              TARGET_REL, repo_root=repo)
    assert r.outcome == FIX_CURES, r.detail
    assert r.is_a_verdict


def test_a_fix_that_does_not_cure_its_own_falsifier(repo):
    """The known-BAD half. A fix that applies cleanly and changes nothing that
    matters is the FIX_INEFFECTIVE condition -- 16 of the 48 undecided pairs."""
    r = probe({"falsifier_code": _falsifier(repo),
               "proposed_fix": _fix("def get():", "def get():  # tidied")},
              TARGET_REL, repo_root=repo)
    assert r.outcome == FIX_INEFFECTIVE, r.detail
    assert r.is_a_verdict


# --------------------------------------------------------------------------- #
# The two ways a SOUND fix could be falsely condemned                          #
# --------------------------------------------------------------------------- #
def test_a_falsifier_that_never_reads_the_target_yields_no_verdict(repo):
    """Measured on exp44: 57 of 70 falsifiers reach their target by IMPORT.
    One that reads neither by import nor by path would otherwise have every fix
    condemned, and condemned confidently."""
    r = probe({"falsifier_code": 'raise AssertionError("FALSIFIED: I read nothing")',
               "proposed_fix": _fix("VALUE = -1", "VALUE = 10")},
              TARGET_REL, repo_root=repo)
    assert r.outcome == NOT_INTERCEPTED, r.detail
    assert not r.is_a_verdict, "an unintercepted falsifier produced a verdict"


def test_a_falsifier_that_does_not_reproduce_yields_no_verdict(repo):
    """If the falsifier is already quiet on the UNMODIFIED target it never
    demonstrated the defect, so there is nothing for a fix to cure and the probe
    must not credit the fix with curing it."""
    (repo / TARGET_REL).write_text(CLEAN, encoding="utf-8")
    r = probe({"falsifier_code": _falsifier(repo),
               "proposed_fix": _fix("VALUE = 10", "VALUE = 11")},
              TARGET_REL, repo_root=repo)
    assert r.outcome == NO_BASELINE, r.detail
    assert not r.is_a_verdict


def test_a_fix_that_does_not_apply_yields_no_verdict(repo):
    r = probe({"falsifier_code": _falsifier(repo),
               "proposed_fix": _fix("TEXT THAT IS NOT IN THE FILE", "x")},
              TARGET_REL, repo_root=repo)
    assert r.outcome == NO_FIX, r.detail
    assert not r.is_a_verdict


def test_no_falsifier_yields_no_verdict(repo):
    r = probe({"falsifier_code": "", "proposed_fix": _fix("VALUE = -1", "VALUE = 10")},
              TARGET_REL, repo_root=repo)
    assert not r.is_a_verdict


# --------------------------------------------------------------------------- #
# The property the frozen-article methodology depends on                       #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("fix_text,label", [
    ("VALUE = 10", "an effective fix"),
    ("def get():  # tidied", "an ineffective fix"),
])
def test_the_real_target_is_never_modified(repo, fix_text, label):
    """The whole reason this uses an overlay rather than adjudicate_by_repair's
    write-and-restore: the runner hashes the target every round, and a kill
    between write and restore corrupts the article under review."""
    before = (repo / TARGET_REL).read_bytes()
    old = "VALUE = -1" if fix_text == "VALUE = 10" else "def get():"
    probe({"falsifier_code": _falsifier(repo), "proposed_fix": _fix(old, fix_text)},
          TARGET_REL, repo_root=repo)
    assert (repo / TARGET_REL).read_bytes() == before, (
        f"{label} left the target modified; the frozen-article guarantee is broken")


def test_the_probe_leaves_no_overlay_behind(repo, tmp_path, monkeypatch):
    """Scoped to a temp root this test OWNS.

    THE DEFECT, 2026-08-30. This globbed the SHARED system temp directory, so it
    asserted that no process anywhere on the machine had created a
    `cdsfl_disc_*` directory during the call. It passed alone and failed in the
    full suite -- `overlay directories leaked: ['cdsfl_disc_lzcubcn1']` -- while
    a review panel was concurrently running pytest in its own sandboxes against
    the same temp root. A guard that cannot tell "the probe leaked" from
    "another process on this Mac made a directory" is a false-positive
    generator, and this project runs panels alongside suites routinely.

    `reference_runner_v2._discrimination_overlay` builds the overlay with
    `tempfile.mkdtemp(prefix="cdsfl_disc_")` (line 3094), which honours
    `tempfile.tempdir`. Pointing that at the test's own tmp_path confines the
    measurement to directories THIS call created, which is the property the test
    was always trying to assert.
    """
    import tempfile
    own_root = tmp_path / "tmproot"
    own_root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(own_root))
    before = {p.name for p in own_root.glob("cdsfl_disc_*")}
    probe({"falsifier_code": _falsifier(repo),
           "proposed_fix": _fix("VALUE = -1", "VALUE = 10")},
          TARGET_REL, repo_root=repo)
    after = {p.name for p in own_root.glob("cdsfl_disc_*")}
    assert after <= before, f"overlay directories leaked: {sorted(after - before)}"


# --------------------------------------------------------------------------- #
# The outcome vocabulary must not collapse                                     #
# --------------------------------------------------------------------------- #
def test_only_the_two_real_outcomes_count_as_verdicts():
    """"The fix did not cure it" and "the instrument could not look" must never
    be the same value. That collapse is the defect this project keeps relearning."""
    for o in (FIX_CURES, FIX_INEFFECTIVE):
        assert FixEfficacyResult(o).is_a_verdict
    for o in (NOT_INTERCEPTED, NO_BASELINE, NO_FIX, "INDETERMINATE_OTHER"):
        assert not FixEfficacyResult(o).is_a_verdict


# --------------------------------------------------------------------------- #
# Pair adjudication -- the tool verdict the MERGED status requires             #
# --------------------------------------------------------------------------- #
from bench.fix_efficacy import (           # noqa: E402
    PAIR_DIFFERENT, PAIR_INCONCLUSIVE, PAIR_SAME, probe_pair,
)

TWO_BUGS = 'A = -1\nB = -2\n\n\ndef get():\n    return A, B\n'


@pytest.fixture
def repo2(tmp_path):
    (tmp_path / "bench").mkdir()
    (tmp_path / TARGET_REL).write_text(TWO_BUGS, encoding="utf-8")
    return tmp_path


def _f(repo_root, token):
    return textwrap.dedent(f'''
        import pathlib
        src = pathlib.Path(r"{repo_root / TARGET_REL}").read_text()
        if "{token}" in src:
            raise AssertionError("FALSIFIED: {token} present")
    ''').strip()


def test_two_findings_of_the_SAME_defect(repo2):
    """One fix removes both symptoms, in both directions -> SAME."""
    both = _fix("A = -1\nB = -2", "A = 1\nB = 2")
    a = {"falsifier_code": _f(repo2, "A = -1"), "proposed_fix": both}
    b = {"falsifier_code": _f(repo2, "B = -2"), "proposed_fix": both}
    r = probe_pair(a, b, TARGET_REL, repo_root=repo2)
    assert r.outcome == PAIR_SAME, r.detail


def test_two_findings_of_DIFFERENT_defects(repo2):
    """Each fix cures only its own symptom -> DIFFERENT, both directions."""
    a = {"falsifier_code": _f(repo2, "A = -1"), "proposed_fix": _fix("A = -1", "A = 1")}
    b = {"falsifier_code": _f(repo2, "B = -2"), "proposed_fix": _fix("B = -2", "B = 2")}
    r = probe_pair(a, b, TARGET_REL, repo_root=repo2)
    assert r.outcome == PAIR_DIFFERENT, r.detail


def test_an_ineffective_fix_yields_no_pair_verdict(repo2):
    """The 2026-08-28 defect, which must not be reintroduced here: SAME used to be
    the FALL-THROUGH in adjudicate_by_repair, so anything that was not a positive
    confirmation PRODUCED a SAME verdict rather than merely contaminating one."""
    a = {"falsifier_code": _f(repo2, "A = -1"),
         "proposed_fix": _fix("def get():", "def get():  # tidied")}
    b = {"falsifier_code": _f(repo2, "B = -2"), "proposed_fix": _fix("B = -2", "B = 2")}
    r = probe_pair(a, b, TARGET_REL, repo_root=repo2)
    assert r.outcome == PAIR_INCONCLUSIVE, r.detail
    assert not r.is_a_verdict


def test_a_pair_adjudication_never_touches_the_target(repo2):
    before = (repo2 / TARGET_REL).read_bytes()
    both = _fix("A = -1\nB = -2", "A = 1\nB = 2")
    probe_pair({"falsifier_code": _f(repo2, "A = -1"), "proposed_fix": both},
               {"falsifier_code": _f(repo2, "B = -2"), "proposed_fix": both},
               TARGET_REL, repo_root=repo2)
    assert (repo2 / TARGET_REL).read_bytes() == before, (
        "the reviewed article changed; this is the exact property that makes the "
        "overlay usable in flight and write-and-restore not")
