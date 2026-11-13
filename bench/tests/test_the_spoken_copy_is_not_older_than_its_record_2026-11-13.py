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
import pathlib
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
        newest = max(srcs, key=lambda p: p.stat().st_mtime)
        if spoken.stat().st_mtime >= newest.stat().st_mtime:
            return
        import datetime as dt
        def when(p):
            return dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")
        pytest.fail(
            f"the spoken copy is OLDER than the record it reports, so it is "
            f"describing a state that has moved.\n"
            f"  spoken : {spoken.name} at {when(spoken)}\n"
            f"  newest : {newest.name} at {when(newest)}\n"
            f"  Regenerate with: python3 scripts/morning_report_build_2026-10-12.py --write\n"
            f"  Measured 2026-11-13: a document frozen 8 h 55 m had 3 of its 4 "
            f"machine-checkable counts wrong.")
