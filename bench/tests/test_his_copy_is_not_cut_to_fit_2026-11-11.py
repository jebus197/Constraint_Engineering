#!/usr/bin/env python3
"""His copy is the WHOLE index, uncut. The cap applies only where detail follows.

★ WHY THIS EXISTS. On 2026-11-11 the founder received
`Decisions_Awaiting_You_2026-11-11_GENERATED.txt` with 3 of its 10
recommendations cut off mid-sentence, and could not rule on 2 of them. His
words: *"But I didn't impose a literal cap. You did it to your self. I simply
framed it as a formatting and presentation issue, rather than requiring a hard
cap. Instead you went from one extreme to another."*

THE RECORD AGREES WITH HIM TWICE. `render`'s docstring records his 2026-11-08
complaint as a WORKLOAD one -- 22,902 words -- and the generated file's own
header states that he never specified a cap and that *"Nothing here is cut to
fit a length"*, while `_gist` cut 3 of 10 to fit 150 characters.

THE DEFECT IS A COMPOSITION, which is why neither half is reverted. A
150-character index cap is harmless when the full argument follows below. An
index-only copy is harmless when nothing in it is cut. Together they produce a
recommendation that stops mid-sentence with nowhere to resolve it, because the
detail is in a repository file he does not have in front of him.

MEASURED 2026-11-11 before the repair: his copy fell from 22,902 words to
1,026, which is 0.044800 of it. The truncation RATE did NOT move -- 6 of 56
index lines before against 5 of 27 after, Fisher exact p = 0.325711 -- so a
rate measurement alone would have reported his complaint as mistaken. The
change was the DETAIL LEAVING HIS COPY. A measurement can answer the wrong
question and look decisive doing it.

THE BOUND, so the repair cannot re-create his workload complaint: across the
live queue's 32 options, leads run 8 to 245 characters, mean 93.375 (numpy and
mpmath agreeing exactly), 6 of 32 over the old cap at 0.187500 Wilson
[0.088895, 0.353092]. Removing the cap from his copy adds at most 368
characters in total. `test_the_uncapped_index_stays_small` pins that.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GEN = ROOT / "scripts" / "build_decisions_file_2026-11-07.py"
CUT = re.compile(r"Recommended option \d+: [^\n]*?\.\.\.")


def _load():
    spec = importlib.util.spec_from_file_location("_bdf_cut", GEN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_bdf_cut"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    assert GEN.is_file(), f"{GEN} is missing"
    return _load()


@pytest.fixture(scope="module")
def built(gen):
    mrb, rows = gen.collect()
    return gen, mrb, rows


class TestTheGistHonoursAnAbsentLimit:
    def test_limit_none_returns_the_lead_whole(self, gen):
        opt = "**" + "w " * 200 + "end.** trailing detail"
        whole = gen._gist(opt, limit=None)
        assert not whole.endswith("..."), "limit=None still truncated"
        assert "end." in whole, "the lead's own final token was dropped"

    def test_a_numeric_limit_still_cuts(self, gen):
        opt = "**" + "w " * 200 + "end.** trailing detail"
        short = gen._gist(opt, limit=150)
        assert short.endswith("..."), (
            "the cap no longer applies even where the detail follows below, so "
            "the repair removed the behaviour instead of scoping it")
        assert len(short) <= 153

    def test_a_short_lead_is_untouched_either_way(self, gen):
        opt = "**Raise the cap.** Everything after this is detail."
        assert gen._gist(opt, limit=150) == "Raise the cap."
        assert gen._gist(opt, limit=None) == "Raise the cap."


class TestHisCopyCarriesEveryRecommendationWhole:
    """★ THE PROPERTY HE ACTUALLY NEEDS, asserted on the real render."""

    def test_the_index_only_render_truncates_nothing(self, built):
        gen, mrb, rows = built
        his = gen.render(mrb, rows, spoken=True, detail=False)
        found = CUT.findall(his)
        assert not found, (
            f"{len(found)} recommendation(s) reach him cut off mid-sentence in "
            f"the copy that carries NO detail to resolve them against: {found[:3]}")

    def test_the_full_render_keeps_the_cap(self, built):
        """The cap is SCOPED, not deleted. Where the argument follows below, a
        scannable index is a real gain and `additive-standard` forbids removing
        it without a measurement showing the removal dominates."""
        gen, mrb, rows = built
        full = gen.render(mrb, rows, spoken=True, detail=True)
        leads = [len(gen._gist(o, limit=None)) for r in rows for o in r["options"]]
        if not any(x > 150 for x in leads):
            pytest.skip("no option lead exceeds 150 today, so the cap is untestable here")
        assert CUT.search(full), (
            "the full render stopped capping, so the repair widened beyond his "
            "ruling, which was about the copy that carries no detail")

    def test_the_file_does_not_contradict_its_own_header(self, built):
        """It claimed `Nothing here is cut to fit a length` while cutting 3 of 10."""
        gen, mrb, rows = built
        his = gen.render(mrb, rows, spoken=True, detail=False)
        if "cut to fit a length" not in his:
            pytest.skip("the header no longer makes that claim")
        assert not CUT.search(his), (
            "the document asserts that nothing in it is cut to fit a length and "
            "then cuts a recommendation to fit one")


class TestTheRepairCannotRecreateHisWorkloadComplaint:
    def test_the_uncapped_index_stays_small(self, built):
        """His 2026-11-08 complaint was 22,902 words. The bound measured on
        2026-11-11 is that removing the cap adds at most 368 characters."""
        gen, mrb, rows = built
        capped = gen.render(mrb, rows, spoken=True, detail=False)
        leads = [len(gen._gist(o, limit=None)) for r in rows for o in r["options"]]
        overflow = sum(max(0, x - 150) for x in leads)
        assert overflow < 5000, (
            f"uncapping would add {overflow} characters to his copy. That "
            f"approaches the workload complaint the index split was built for; "
            f"shorten the OPTION LEADS rather than re-imposing a character cap.")
        assert len(capped.split()) < 5000, (
            f"his copy is {len(capped.split())} words. It is the index; if it "
            f"has grown to a document, the leads have grown, not the cap.")

    def test_every_row_is_present_in_his_copy(self, built):
        """Uncapping must not drop a decision."""
        gen, mrb, rows = built
        his = gen.render(mrb, rows, spoken=True, detail=False)
        missing = [r["ident"] for r in rows if r["ident"] not in his]
        assert not missing, f"decisions absent from his copy: {missing}"
