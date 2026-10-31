#!/usr/bin/env python3
"""A brief RETIRED on his ruling is not a backlog item.

WHY THIS DISTINCTION EXISTS AND WHY IT IS NARROW. On 2026-10-30 he pushed back
on being told the panel backlog was stale recording rather than undone work:
*"There are several panel requests outstanding on your master task list as I
recall. Not all of them are likely to be stale. They have simply not yet been
done as far as I can tell?"* He was right, and the artefact census that proved
it -- a brief directory with no seat reply means the review never ran -- is
load-bearing and is NOT weakened here.

What it could not express is a brief he has RETIRED. On 2026-10-30 he rejected
the framing of the B22 briefs and supplied a better one, so 3 written-and-never-
dispatched briefs became superseded rather than owed. Nothing on disk
distinguished the 2, so the census kept reporting them as a backlog -- which is
the over-reporting he named in the same reply.

THE MARKER IS A FILE, NOT A FLAG IN A SCRIPT. `RETIRED.md` sits beside the
brief, states his ruling verbatim, and names the superseding round. Nothing is
deleted, so the decision stays auditable, and a reader of the directory learns
it from the directory rather than from a report about it.

THE RISK THIS GUARDS, and it is the obvious one: a marker that excuses a brief
from the census is a way to make a backlog disappear by writing files. So these
tests require a retirement to NAME its successor and to name his ruling, and
they require the census to keep counting an unmarked brief as unrun.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

LOGS = REPO / "bench" / "logs"
CENSUS = REPO / "scripts" / "which_panel_briefs_were_never_run_2026-10-30.py"
ORDER = REPO / "scripts" / "the_outstanding_work_in_his_order_2026-10-30.py"


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def retired_dirs() -> list[pathlib.Path]:
    return sorted(p.parent for p in LOGS.glob("*/RETIRED.md"))


class TestARetirementMustJustifyItself:
    def test_there_is_at_least_one_and_the_fixture_is_not_empty(self):
        assert retired_dirs(), (
            "no retirement markers exist, so every test below is vacuous")

    @pytest.mark.parametrize("d", retired_dirs(), ids=lambda p: p.name)
    def test_it_names_the_superseding_round(self, d):
        text = (d / "RETIRED.md").read_text()
        assert "SUPERSEDED BY" in text.upper(), (
            f"{d.name} is retired but names no successor, so the question it "
            "asked may simply have been dropped")
        # the named successor must exist and must itself carry a brief
        import re
        named = re.findall(r"bench/logs/([A-Za-z0-9_\-]+)", text)
        assert named, f"{d.name} names no successor path"
        assert any((LOGS / n / "BRIEF.md").is_file() for n in named), (
            f"{d.name} names {named} as its successor and none of them carries "
            "a BRIEF.md, so the question has no live home")

    @pytest.mark.parametrize("d", retired_dirs(), ids=lambda p: p.name)
    def test_it_quotes_his_ruling(self, d):
        text = (d / "RETIRED.md").read_text()
        assert "HIS RULING" in text.upper(), (
            f"{d.name} is retired without naming the ruling that retired it; "
            "only he may retire a question he asked")

    @pytest.mark.parametrize("d", retired_dirs(), ids=lambda p: p.name)
    def test_the_brief_itself_is_still_there(self, d):
        assert (d / "BRIEF.md").is_file(), (
            f"{d.name} was retired by DELETING its brief; retirement preserves "
            "the archive, it does not empty it")


class TestTheCensusHonoursItWithoutBeingWeakened:
    """★ THESE CALL `classify`, THEY DO NOT RESTATE IT. The first version of
    this class recomputed the partition from the census's primitives, and
    mutating the census's own branch left it GREEN twice -- a reimplementation
    agrees with itself. The classification was extracted from `main` for
    exactly this reason, so there is 1 spelling and a test can reach it."""

    def test_a_retired_brief_is_not_counted_as_unrun(self):
        c = _load(CENSUS, "census_retired")
        unrun, ran, retired = c.classify(c.brief_dirs())
        assert retired, "no retired brief is also reply-less, so this is vacuous"
        names = {r["name"] for r in unrun}
        for r in retired:
            assert r["name"] not in names, (
                f"{r['name']} is retired and is still counted as unrun")

    def test_an_UNMARKED_reply_less_brief_is_still_counted(self):
        """The property he was right about must survive. If every reply-less
        brief could be excused, the census would stop being able to tell him
        that a review had simply not been done."""
        c = _load(CENSUS, "census_retired2")
        unrun, ran, retired = c.classify(c.brief_dirs())
        assert unrun, (
            "0 reply-less briefs are counted as unrun; either the backlog is "
            "genuinely empty, which should be stated, or the marker is now "
            "excusing everything")
        for r in unrun:
            assert not r["retired"], (
                f"{r['name']} is in the unrun set AND marked retired, so the "
                "partition is not a partition")

    def test_the_partition_is_total_and_disjoint(self):
        c = _load(CENSUS, "census_retired4")
        dirs = c.brief_dirs()
        unrun, ran, retired = c.classify(dirs)
        names = [r["name"] for r in unrun + ran + retired]
        assert len(names) == len(dirs), (
            f"{len(names)} classified against {len(dirs)} directories")
        assert len(set(names)) == len(names), "a directory is in 2 buckets"

    def test_the_2_instruments_agree_on_the_retired_set(self):
        """The census and the order producer must not drift, which is the
        defect that made them disagree 7 against 8 on 2026-10-30."""
        c = _load(CENSUS, "census_retired3")
        o = _load(ORDER, "order_retired")
        _, _, retired = c.classify(c.brief_dirs())
        c_retired = {r["name"] for r in retired}
        o_retired = {b["dir"] for b in o.briefs()
                     if not b["ran"] and b.get("retired")}
        assert c_retired == o_retired, (
            f"the census sees {sorted(c_retired)} and the order producer sees "
            f"{sorted(o_retired)}; 2 instruments answering 1 question is the "
            "defect, not the disagreement")
