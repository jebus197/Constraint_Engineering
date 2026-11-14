"""B196. The spoken report's exempt spans must cover QUOTATION and nothing else.

WHY THIS FILE EXISTS. `render_tts` records, out of band, which character ranges
of the spoken morning report are quoted material -- the written copy marks them
with `verbatim-begin` comments, and a file the founder LISTENS to may carry no
markup, so the spans travel separately. 2 consumers read them: the self-lint,
which exempts a finding inside a span, and `_mark_my_paragraphs`, which withholds
his asterisk from a paragraph it is told is his own words.

THE DEFECT, measured 2026-11-14 by running the lint twice, once with the
generator's spans and once without. The outstanding-work loop opened its span
BEFORE the loop and closed it AFTER, so the exemption meant for each entry's
headline also covered the "You ruled on this" sentence, the recorded status, and
both the authored `what` and `why` fields. **3 spans covered 52,584 of 57,898
characters = 0.908218 of the file**, span 2 alone running [2109, 48419) at 46,310
characters. The effects were 2, from 1 cause:

  * the self-lint reported `is clean` on a file carrying **39 blocking findings**
    -- 29 spelled numbers, 7 bare entry codes, 3 category nouns -- so the
    founder's ruling of 2026-09-04 making a spelled-number finding BLOCKING was
    unenforced on the surface he listens to; and
  * **189 of 205** paragraph openers carried no asterisk, because the marker was
    told 0.908218 of the document was his own words.

WHAT IS ASSERTED, and it is the property rather than a number. A FRACTION would
be a pin on a growing document, which this project has had to correct 3 times in
10 days. So the test asserts that no authored field -- a `what` or a `why` from
`data/morning_report_decisions.json` -- lands inside an exempt span, which is the
invariant the defect violated and which cannot go stale as the report grows. The
anti-vacuity cases are the other half: spans must EXIST and must actually exempt
the quoted headlines, or a generator that recorded nothing would pass.
"""
from __future__ import annotations

import importlib.util
import io
import contextlib
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

GEN = SCRIPTS / "morning_report_build_2026-10-12.py"
DETAIL = ROOT / "experimental_notes" / "data" / "morning_report_decisions.json"


@pytest.fixture(scope="module")
def rendered():
    """(text, spans), captured through the generator's OWN call path.

    `render_tts` is wrapped rather than called directly, because replicating
    `main()`'s argument plumbing would be a 2nd opinion about what the generator
    does -- and a probe that reimplements its subject tests the probe.
    `main([])` without `--write` computes everything and writes nothing.
    """
    spec = importlib.util.spec_from_file_location("_mrb_spans", GEN)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_mrb_spans"] = m
    spec.loader.exec_module(m)
    cap: dict = {}
    real = m.render_tts

    def wrap(*a, **kw):
        out = real(*a, **kw)
        cap["spans"] = list(kw.get("exempt_out") or [])
        cap["text"] = out
        return out

    m.render_tts = wrap
    with contextlib.redirect_stdout(io.StringIO()):
        m.main([])
    m.render_tts = real
    if "text" not in cap:
        pytest.skip("the generator did not reach render_tts on this checkout")
    return cap["text"], cap["spans"]


def _inside(spans, pos: int) -> bool:
    return any(a <= pos < b for a, b in spans)


class TestTheSpansExist:
    def test_there_are_spans_at_all(self, rendered):
        """ANTI-VACUITY. A generator recording 0 spans would satisfy every
        containment assertion below while exempting nothing."""
        _text, spans = rendered
        assert spans, (
            "render_tts recorded 0 exempt spans, so the quotation exemption "
            "reaches nothing and every assertion below is vacuous")
        assert all(b > a for a, b in spans), f"a span is empty or inverted: {spans}"

    def test_the_spans_actually_exempt_something(self, rendered):
        """ANTI-VACUITY, the other direction: spans covering 0 characters would
        pass the containment test trivially."""
        text, spans = rendered
        covered = sum(b - a for a, b in spans)
        assert covered > 0, "the spans cover 0 characters"
        assert covered < len(text), (
            "the spans cover the WHOLE document, which is the defect this file "
            "exists for in its most extreme form")


class TestAuthoredProseIsNeverExempt:
    @staticmethod
    def _authored_windows(m) -> list:
        """(label, probe) for each authored what/why, in its SPOKEN form.

        The spoken render passes authored text through `_spoken()`, so a raw
        probe from the JSON would not match and the test would pass by failing
        to find its own subject -- the false-zero shape this project has met
        repeatedly. The probe is taken AFTER that transform.
        """
        d = json.loads(DETAIL.read_text())
        out = []
        for key, rec in d.items():
            if not isinstance(rec, dict):
                continue
            for field in ("what", "why"):
                raw = rec.get(field)
                if not isinstance(raw, str) or len(raw) < 80:
                    continue
                spoken = " ".join(m._spoken(raw).split())
                if len(spoken) >= 60:
                    out.append((f"{key}.{field}", spoken[:60]))
        return out

    def test_no_authored_what_or_why_lands_inside_an_exempt_span(self, rendered):
        """THE INVARIANT THE DEFECT VIOLATED. An authored field is this
        project's own prose and Rule 27 binds it; a quotation exemption that
        covers it silences the rule on the surface he listens to.
        """
        text, spans = rendered
        m = sys.modules["_mrb_spans"]
        windows = self._authored_windows(m)
        assert len(windows) >= 10, (
            f"only {len(windows)} authored field(s) produced a probe; the "
            f"detail file or `_spoken` has changed shape and this test would "
            f"be asserting almost nothing")
        found = offenders = 0
        names = []
        for label, probe in windows:
            pos = text.find(probe)
            if pos < 0:
                continue                      # not rendered in the spoken copy
            found += 1
            if _inside(spans, pos):
                offenders += 1
                names.append(label)
        assert found >= 5, (
            f"only {found} of {len(windows)} authored probes were located in "
            f"the render, so this test is not reaching its subject")
        assert offenders == 0, (
            f"{offenders} authored field(s) sit INSIDE a quotation exemption, "
            f"so the note standard is unenforced on the spoken copy for them: "
            f"{names[:8]}")


class TestTheQuotedHeadlinesAreExempt:
    def test_a_headline_is_still_inside_a_span(self, rendered):
        """The repair must not have thrown the exemption away. A task-list
        headline is quoted as the markers carry it and must stay exempt.
        """
        text, spans = rendered
        d = json.loads(DETAIL.read_text())
        m = sys.modules["_mrb_spans"]
        titles = [" ".join(m._spoken(r["title"]).split())
                  for r in d.values()
                  if isinstance(r, dict) and isinstance(r.get("title"), str)
                  and len(r["title"]) > 25]
        hits = 0
        for ti in titles:
            pos = text.find(ti[:40])
            if pos >= 0 and _inside(spans, pos):
                hits += 1
        assert hits >= 1, (
            "no rendered headline sits inside an exempt span, so the repair "
            "removed the exemption rather than scoping it")
