#!/usr/bin/env python3
"""The fast citation index must answer exactly what `git grep` answers.

WHY IT EXISTS. `cited_where` shelled out to `git grep` once per path, 1.42s
against 8,705 tracked files, and every caller loops it over the whole untracked
set. `test_cited_evidence_classification_2026-09-11.py` took 611s, of which 608s
was 4 such loops. The set had just grown 58 -> 95 because the A8 reversal
untracked 37 `bench/logs` files, so the cost rose with the ruling rather than
with any code change.

An index now answers those paths in 1 pass, 2.0s, and that file runs in 7s.

THE RISK THE SPEED CREATES, which is the whole reason for this file: a fast path
that disagrees with the slow one is worse than the slow one, because the figures
it feeds -- entry A8's population, the note-cited census -- are load-bearing and
a divergence would be invisible. So this CALLS BOTH and compares. Asserting on
the index's source text would prove only that it describes itself consistently.

2 REJECTED ALTERNATIVES ARE RECORDED IN THE PRODUCER, measured not reasoned:
a single `git grep` carrying 95 patterns (127.8s, because cost scales per
pattern too) and a single pass with a 95-branch alternation regex (>660s,
catastrophic backtracking). The winner uses 1 simple regex after a plain
substring reject.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "orphan_figures_2026-09-10.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("orphan_idx", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["orphan_idx"] = mod
    spec.loader.exec_module(mod)
    return mod


def _git_grep(path: str) -> list[str]:
    """The slow answer, as a WHOLE TOKEN rather than a bare substring.

    CORRECTED 2026-09-21. This ran `git grep -l -- <path>`, a substring search,
    and compared it against an index built by EXTRACTING whole
    `bench/logs/[\w./-]+` tokens. Those two agree on every path except one that
    is a PREFIX of another, and they must disagree there by construction: the
    substring search reports every file containing the longer path as well.

    It surfaced on
    `.../sim45_canary_v2_20260901T214242Z_report.j` -- note the `.j`, a path
    TRUNCATED at a column boundary, which genuinely appears that way in 3
    tracked files dated 2026-09-01 and 2026-09-17. `git grep` matched it inside
    every mention of the real `...report.json`; the index, correctly, listed
    only the files where the truncated token actually appears.

    THE INDEX WAS RIGHT AND THE ORACLE WAS WRONG. Claiming a citation of
    `report.j` because `report.json` is present is a false citation, so the
    comparison is now made on the same terms the index uses: the path must not
    be followed by another path character.

    THIS WAS PRE-EXISTING AND WAS EXPOSED, NOT CAUSED, BY A CHANGE ELSEWHERE.
    The test samples every 19th path, so mirroring 11 panel-record files on
    2026-09-21 shifted the sample onto this one. It would have fired on any
    change that moved the list.
    """
    r = subprocess.run(
        ["git", "grep", "-lP", "--", re.escape(path) + r"(?![\w./-])"],
        cwd=ROOT, capture_output=True, text=True)
    return sorted(f for f in r.stdout.split() if f)


class TestTheFastPathAgreesWithTheSlowOne:
    def test_a_sample_of_live_paths_matches_git_exactly(self, m):
        _cited, untracked = m.untracked_cited_paths()
        assert untracked, "no untracked cited paths at all; this compares nothing"
        # Every 19th path, so the sample spans the list rather than its head.
        sample = sorted(untracked)[::19][:6]
        assert len(sample) >= 3, f"sample too small to mean anything: {sample}"
        for p in sample:
            assert m.cited_where(p) == _git_grep(p), (
                f"the index and `git grep` disagree about {p}. The index feeds "
                f"entry A8's population; a divergence here is a wrong figure, "
                f"not a slow one.")

    def test_the_comparison_is_not_vacuous(self, m):
        """If every sampled path were uncited, both sides would agree on empty
        lists and this file would pass while checking nothing."""
        _cited, untracked = m.untracked_cited_paths()
        sample = sorted(untracked)[::19][:6]
        assert any(m.cited_where(p) for p in sample), (
            f"every sampled path is uncited, so the agreement above is between "
            f"2 empty lists: {sample}")

    def test_a_non_indexable_path_still_falls_back_to_git(self, m):
        """The extractor captures `bench/logs/` + `[\\w./-]+`. Anything else was
        never an index key, and answering it from the index would report a false
        UNCITED rather than an answer."""
        p = "scripts/blocker_triage.py"
        assert m._INDEXABLE.fullmatch(p) is None
        assert m.cited_where(p) == _git_grep(p)
        assert m.cited_where(p), "this path is cited somewhere; an empty answer is wrong"


class TestItCoversTheWholeCheckout:
    def test_the_index_reads_more_than_the_extractor_s_5_directories(self, m):
        """The extractor scans 5 directories. The index reads every tracked file,
        which closes a gap of 77 tracked `.md` files outside them -- any one of
        which could turn a CODE ONLY into a NOTE."""
        m.build_citation_index()
        scanned = {f for files in m._CITATION_INDEX.values() for f in files}
        dirs = ("experimental_notes/", "resources/", "scripts/", "bench/tests/", "docs/")
        outside = [f for f in scanned if not f.startswith(dirs)]
        assert outside, (
            "no citation was found outside the extractor's 5 directories, so "
            "reading the whole checkout is currently indistinguishable from "
            "reading those 5 -- check this still holds before trusting it")


class TestItStaysFast:
    def test_classifying_the_whole_set_is_not_back_to_minutes(self, m):
        """A RATCHET, NOT A BENCHMARK. Wall clock is a property of this machine
        under this load, so the bound is deliberately loose: the measured figure
        is 2.5s and the regression it guards against is 135.4s.
        """
        m._WHERE_CACHE.clear()
        m._CITATION_INDEX = None
        t0 = time.perf_counter()
        _cited, untracked = m.untracked_cited_paths()
        for p in untracked:
            m.classify_citation(p)
        el = time.perf_counter() - t0
        assert el < 60, (
            f"classifying {len(untracked)} paths took {el:.1f}s. It was 135.4s "
            f"with a `git grep` per path and 2.5s with the index; this looks "
            f"like the per-path form is back.")
