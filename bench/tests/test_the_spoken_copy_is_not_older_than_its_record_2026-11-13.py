"""The spoken morning report must not be older than the record it reports.

ENTRY B167. A document frozen at 04:09 had 3 of its 4 machine-checkable counts
wrong 8 h 55 m later -- 0.750000, Wilson [0.300642, 0.954413], producer
`how_stale_is_a_narrated_report_2026-11-13.py`. The entry proposed making the
standing spoken deliverable a generated surface, on the reasoning that prose
goes stale and derivation does not.

★ THE MEASUREMENT REFUTED THAT REASONING AND THIS GUARD ENCODES WHAT SURVIVED.
Both documents compared carried the SAME machine-written headline; the older one
was simply OLDER. So the mechanism is not prose against derivation, it is FROZEN
against RE-RENDERED. A generated report left sitting decays exactly as fast. The
property that actually matters is therefore CURRENCY AT DELIVERY, and that is
what is asserted here.

★ IT SKIPS RATHER THAN FAILS WHEN THE SPOKEN COPY IS ABSENT. The file lives on
the founder's Desktop, outside the repository, so a clone has none. A guard that
failed in a clone would be asserting something about the machine rather than
about the project, and `test_fresh_clone_suite_2026-09-10.py` exists precisely
because this suite must pass in a clone.

★ AND IT COMPARES AGAINST THE SOURCES THE GENERATOR ITSELF NAMES, read from its
own module rather than listed again here, so the 2 cannot drift apart.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
GEN = REPO / "scripts" / "morning_report_build_2026-10-12.py"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("mrb_currency", GEN)
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb_currency"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def _sources(m) -> list[pathlib.Path]:
    """The generator's OWN source paths, taken from its module constants."""
    names = ("TASKLIST", "DETAIL", "PARKED", "STUDY")
    out = []
    for n in names:
        p = getattr(m, n, None)
        if isinstance(p, pathlib.Path) and p.is_file():
            out.append(p)
    return out


def _content_changed_at(p: pathlib.Path) -> float:
    """When this file's CONTENT last changed, not when it was last written.

    ★ WHY THIS IS NOT `st_mtime`, found on 2026-11-14. The full suite rewrote
    `morning_report_decisions.json` mid-run at 11:55:24 with content IDENTICAL
    to HEAD -- `git status --porcelain` reports the path clean -- and this guard
    then named 11:55:24 as the moment the record moved. It had not moved. The
    verdict happened to be right for the wrong reason: the spoken copy WAS stale,
    by 5 minutes against a real content change at 08:20:15, and the reason
    printed sent a reader chasing a write that changed nothing. A right decision
    recorded with a false reason is a defect in its own right in this project.

    DIRTY -> mtime, because an uncommitted edit has no commit to date it by.
    CLEAN and tracked -> the commit date of the last commit touching the path.
    UNTRACKED, or no git at all -> mtime, which is the behaviour this replaces,
    so the fallback can only be as good as before and never worse.
    """
    mtime = p.stat().st_mtime
    try:
        rel = p.relative_to(REPO)
    except ValueError:
        return mtime                       # outside the repo; git knows nothing
    def git(*a):
        return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                              text=True, timeout=30)
    try:
        if git("status", "--porcelain", "--", str(rel)).stdout.strip():
            return mtime                   # uncommitted edit: mtime is the truth
        out = git("log", "-1", "--format=%ct", "--", str(rel)).stdout.strip()
        return float(out) if out else mtime
    except Exception:
        return mtime                       # no git, or git refused: degrade


def _spoken() -> pathlib.Path | None:
    d = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
    if not d.is_dir():
        return None
    cands = sorted(d.glob("Morning_Report_*_GENERATED.txt"))
    return cands[-1] if cands else None


class TestTheGeneratorStillNamesItsSources:
    def test_at_least_three_sources_resolve(self, mod):
        """NON-VACUOUS: if the constants are renamed this guard must not pass empty."""
        srcs = _sources(mod)
        assert len(srcs) >= 3, (
            f"only {len(srcs)} of the generator's source constants resolved to a "
            f"file; the currency check below would be comparing against almost "
            f"nothing. Found: {[p.name for p in srcs]}")


class TestTheSpokenCopyIsCurrent:
    def test_it_is_not_older_than_the_record_it_reports(self, mod):
        spoken = _spoken()
        if spoken is None:
            pytest.skip("no spoken copy on this machine; it lives outside the repo")
        srcs = _sources(mod)
        assert srcs, "no generator sources resolved"
        newest = max(srcs, key=_content_changed_at)
        if spoken.stat().st_mtime >= _content_changed_at(newest):
            return
        import datetime as dt
        def when(p):
            t = _content_changed_at(p) if p in srcs else p.stat().st_mtime
            return dt.datetime.fromtimestamp(t).isoformat(timespec="seconds")
        pytest.fail(
            f"the spoken copy is OLDER than the record it reports, so it is "
            f"describing a state that has moved.\n"
            f"  spoken : {spoken.name} at {when(spoken)}\n"
            f"  newest : {newest.name} at {when(newest)}\n"
            f"  Regenerate with: python3 scripts/morning_report_build_2026-10-12.py --write\n"
            f"  Measured 2026-11-13: a document frozen 8 h 55 m had 3 of its 4 "
            f"machine-checkable counts wrong.")


class TestTheContentTimeHelperBehavesBothWays:
    """Commissioning, driven on REAL files rather than on a described one.

    A touch cannot be simulated honestly by patching `stat`, because the thing
    under test is the DISAGREEMENT between mtime and git -- so these cases create
    the disagreement for real inside a throwaway repository.
    """

    def _repo(self, tmp_path):
        def git(*a):
            return subprocess.run(["git", *a], cwd=tmp_path, capture_output=True,
                                  text=True, timeout=30)
        git("init", "-q")
        git("config", "user.email", "t@t")
        git("config", "user.name", "t")
        f = tmp_path / "rec.json"
        f.write_text('{"a": 1}\n', encoding="utf-8")
        git("add", "rec.json")
        git("commit", "-q", "-m", "seed")
        return git, f

    def test_a_touch_that_changes_nothing_does_not_move_the_content_time(
            self, tmp_path, monkeypatch):
        git, f = self._repo(tmp_path)
        monkeypatch.setattr(sys.modules[__name__], "REPO", tmp_path)
        before = _content_changed_at(f)
        os.utime(f, (f.stat().st_atime + 10_000, f.stat().st_mtime + 10_000))
        assert f.stat().st_mtime > before + 1_000, "the touch did not take"
        after = _content_changed_at(f)
        assert after == before, (
            "a rewrite with identical content moved the content time, which is "
            "exactly the 2026-11-14 misattribution this helper removes")

    def test_a_real_edit_does_move_it(self, tmp_path, monkeypatch):
        git, f = self._repo(tmp_path)
        monkeypatch.setattr(sys.modules[__name__], "REPO", tmp_path)
        before = _content_changed_at(f)
        f.write_text('{"a": 2}\n', encoding="utf-8")
        os.utime(f, (f.stat().st_atime + 10_000, f.stat().st_mtime + 10_000))
        after = _content_changed_at(f)
        assert after > before, (
            "an uncommitted content change did not move the content time, so a "
            "genuinely stale spoken copy would pass")

    def test_an_untracked_file_falls_back_to_its_mtime(self, tmp_path, monkeypatch):
        git, _ = self._repo(tmp_path)
        monkeypatch.setattr(sys.modules[__name__], "REPO", tmp_path)
        u = tmp_path / "untracked.json"
        u.write_text("{}\n", encoding="utf-8")
        assert _content_changed_at(u) == u.stat().st_mtime
