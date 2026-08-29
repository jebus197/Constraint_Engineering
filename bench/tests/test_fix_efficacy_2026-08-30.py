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


def test_the_probe_leaves_no_overlay_behind(repo, tmp_path):
    import tempfile
    before = {p.name for p in pathlib.Path(tempfile.gettempdir()).glob("cdsfl_disc_*")}
    probe({"falsifier_code": _falsifier(repo),
           "proposed_fix": _fix("VALUE = -1", "VALUE = 10")},
          TARGET_REL, repo_root=repo)
    after = {p.name for p in pathlib.Path(tempfile.gettempdir()).glob("cdsfl_disc_*")}
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
