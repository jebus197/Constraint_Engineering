#!/usr/bin/env python3
"""The removed fence pattern stays removed only while its survivor dominates it.

WHAT HAPPENED. `reference_runner_v3` carried 2 markdown-fence patterns:
`_MD_PY_FENCE_ANY`, live with 2 call sites, and `_MD_PY_FENCE`, the original
narrow form with ZERO callers. The cc2 seat reported the orphan in the free
panel of 2026-09-30 and it was recorded as reported-rather-than-deleted; the
founder asked why that was not a fix. It was removed on 2026-10-01 under the
additive standard's removal clause, which requires a committed measurement
showing the replacement dominates on a named property.

THE PROPERTY IS RECOGNITION over realistic markdown shapes, and this file holds
it by EXECUTION rather than by citing the commit that claimed it. The removed
pattern survives as a literal in
`scripts/md_fence_orphan_dominance_2026-10-01.py`, so the comparison is
re-derived on every suite run and a regression in the live pattern fails here
rather than being discovered by a lost extraction.

WHY A TEST AND NOT JUST THE SCRIPT. A measurement taken once and remembered is
the shape `measured-rate-travels-with-its-script` exists to prevent. If someone
narrows `_MD_PY_FENCE_ANY` later, the removal's justification silently stops
being true, and nothing would say so.

Run:  python3 -m pytest bench/tests/test_md_fence_orphan_is_dominated_2026-10-01.py -q
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PRODUCER = REPO / "scripts" / "md_fence_orphan_dominance_2026-10-01.py"


@pytest.fixture(scope="module")
def producer():
    if not PRODUCER.is_file():
        pytest.fail(
            f"{PRODUCER.name} is missing. It is the committed measurement that "
            f"licenses the removal of _MD_PY_FENCE; without it the removal has "
            f"no justification on record.")
    spec = importlib.util.spec_from_file_location("md_fence_dom", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["md_fence_dom"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def live():
    from reference_runner_v3 import _MD_PY_FENCE_ANY
    return _MD_PY_FENCE_ANY


class TestTheOrphanIsGoneFromTheLiveModule:
    def test_the_live_module_no_longer_defines_it(self):
        import reference_runner_v3 as R
        assert not hasattr(R, "_MD_PY_FENCE"), (
            "the orphan is defined again. An extractor with no callers is an "
            "addition nothing reaches, which the additive standard counts as a "
            "defect in its own right.")

    def test_the_live_pattern_is_still_there_and_still_called(self):
        import reference_runner_v3 as R
        assert hasattr(R, "_MD_PY_FENCE_ANY")
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(
            encoding="utf-8")
        calls = src.count("_MD_PY_FENCE_ANY.finditer")
        assert calls >= 2, (
            f"the surviving pattern has {calls} call sites; it was kept BECAUSE "
            f"it is the one in use")


class TestTheDominanceStillHolds:
    def test_no_shape_is_recognised_only_by_the_removed_pattern(self, producer,
                                                                live):
        """THE REMOVAL CONDITION. 0 orphan-only shapes, or the removal is unsafe."""
        r = producer.compare(live)
        assert r["orphan_only"] == [], (
            "the live pattern no longer recognises every shape the removed one "
            "did, so the removal's justification has lapsed. Either restore the "
            f"pattern or widen the survivor. Lost shapes: {r['orphan_only'][:10]}")

    def test_the_dominance_is_proper_not_merely_equal(self, producer, live):
        """"Better" means strictly better, not a like-for-like swap."""
        r = producer.compare(live)
        assert r["live_only"] > 0, (
            "the survivor recognises nothing extra, so it is not BETTER on the "
            "named property -- it is only the one that happened to have callers")

    def test_the_corpus_is_big_enough_to_mean_something(self, producer):
        """ANTI-VACUITY. 0 orphan-only over 3 shapes would prove nothing."""
        assert len(producer.shapes()) >= 500, len(producer.shapes())

    def test_the_orphan_actually_recognised_something(self, producer, live):
        """ANTI-VACUITY, THE OTHER DIRECTION. A pattern that matched NOTHING
        would make the dominance trivially true and the test worthless."""
        r = producer.compare(live)
        assert r["both"] > 0, (
            "the removed pattern matches none of the corpus, so '0 orphan-only' "
            "is arithmetic rather than evidence")

    def test_the_producer_agrees_with_itself_when_run(self, producer, live):
        """The script's headline numbers are the ones this test measures."""
        r = producer.compare(live)
        assert r["both"] + len(r["orphan_only"]) == 14, r
        assert r["both"] + r["live_only"] == 224, r
        assert r["n"] == 560, r
