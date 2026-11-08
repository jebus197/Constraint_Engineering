"""Quoted material is exempt in the spoken copy, without markup in the file.

HIS RULING, B96 / decision 15 of 2026-11-08: wrap genuinely quoted material in
the spoken renderer too, so commit subjects, task-list headlines and his own
words are exempt in BOTH copies rather than only the written one. Then, when the
straightforward reading was shown to break another of his rules, he ruled again:
use the version that honours both.

WHY THE STRAIGHTFORWARD READING COULD NOT BE BUILT. The written exemption is
carried by literal `verbatim-begin` / `verbatim-end` HTML comments which the
lint finds by searching the file TEXT, so exempting a span that way requires the
marker to be IN the file. Measured 2026-11-08: 0 of the delivered spoken files
carried them, and the note standard forbids markup in a spoken file in its own
words -- anything that would be spoken as a noise or skipped awkwardly must not
be there. That rule is his accessibility accommodation, not tidiness. Building
option 1 as worded would have served consistency by damaging what the spoken
copy is for.

THE VERSION BUILT. The generator already lints both copies immediately after
writing them, so it already knows where its quoted spans are. `render_tts`
records them by LINE INDEX and converts to character offsets with the same join
it returns, and `note_vagueness_lint.partition` maps those offsets to paragraph
numbers through `PARAGRAPH_BREAK` -- the module's ONLY splitter, so the exempt
set cannot be numbered by one rule and applied to findings numbered by another,
which is the measured drift of 2026-09-11.

A BUG OF MINE IS WORTH RECORDING HERE. The conversion block first landed inside
`render_md`, because I selected the LAST matching return line and then replaced
the FIRST occurrence of that identical text. `render_md` would have raised
NameError on `exempt_out`. The 2 renderers are now asserted apart below.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def mods():
    sys.path.insert(0, str(REPO / "scripts"))
    out = {}
    for key, name in (("mrb", "morning_report_build_2026-10-12.py"),
                      ("nvl", "note_vagueness_lint.py")):
        spec = importlib.util.spec_from_file_location(f"_{key}_b96",
                                                      REPO / "scripts" / name)
        m = importlib.util.module_from_spec(spec)
        sys.modules[f"_{key}_b96"] = m
        spec.loader.exec_module(m)
        out[key] = m
    return out


#: Quoted material carrying a spelled number in each of the 3 regions the
#: markdown wraps. A spelled number is used because Rule 27 is BLOCKING, so the
#: exemption is observable through `blocking` rather than only through `lint`.
DONE = [("abc1234", "2026-11-08", "twenty-nine things were committed today")]
OUTSTANDING = [{"ident": "B1", "title": "thirty headlines as the markers carry them"}]
OWED = [{"date": "2026-11-08", "text": "He asked about forty of them."}]


def _render(mods, **kw):
    decs = mods["mrb"].decisions(mods["mrb"].task_items())[0]
    spans: list = []
    txt = mods["mrb"].render_tts(decs, OUTSTANDING, DONE, OWED, [], None, (),
                                 detail=False, exempt_out=spans, **kw)
    return txt, spans


def _write(txt: str) -> pathlib.Path:
    f = pathlib.Path(tempfile.mkdtemp()) / "Morning_Report_2026-11-08.txt"
    f.write_text(txt, encoding="utf-8")
    return f


class TestTheExemptionIsCarriedOutOfBand:
    def test_the_fixture_really_carries_blocking_findings(self, mods):
        """ANTI-VACUITY. If the quoted fixtures stop carrying a blocking
        finding, every assertion below passes while testing nothing."""
        txt, _ = _render(mods)
        assert len(mods["nvl"].blocking(_write(txt))) >= 3

    def test_the_spans_exempt_them(self, mods):
        txt, spans = _render(mods)
        f = _write(txt)
        before = mods["nvl"].blocking(f)
        after = mods["nvl"].blocking(f, spans)
        assert len(after) < len(before), (
            f"{len(before)} findings before and {len(after)} after; the "
            f"out-of-band spans exempt nothing")

    def test_the_spoken_file_carries_no_markup(self, mods):
        """THE WHOLE POINT. His TTS standard forbids it, and he listens to this."""
        txt, _ = _render(mods)
        assert "verbatim-begin" not in txt
        assert "<!--" not in txt

    def test_every_span_lies_inside_the_text_it_describes(self, mods):
        txt, spans = _render(mods)
        assert spans, "no spans recorded, so the exemption reaches nothing"
        for a, b in spans:
            assert 0 <= a < b <= len(txt), f"span ({a}, {b}) is outside the text"

    def test_each_span_covers_its_quoted_material(self, mods):
        """NOT a blanket exemption: each span must contain the quoted text it
        is for, and the report's own prose must stay outside every span."""
        txt, spans = _render(mods)
        covered = "".join(txt[a:b] for a, b in spans)
        for needle in ("twenty-nine things", "thirty headlines", "forty of them"):
            assert needle in covered, f"{needle!r} is not inside any span"
        assert "MORNING REPORT" not in covered, (
            "the report's own heading is inside an exempt span, which would buy "
            "amnesty for its own prose")

    def test_an_empty_region_records_no_span(self, mods):
        """A span of 0 length would exempt a paragraph boundary and nothing else,
        so empty regions must record nothing rather than an empty range."""
        decs = mods["mrb"].decisions(mods["mrb"].task_items())[0]
        spans: list = []
        mods["mrb"].render_tts(decs, [], [], [], [], None, (),
                               detail=False, exempt_out=spans)
        assert spans == []


class TestTheTwoRenderersStayApart:
    def test_render_md_does_not_take_the_out_of_band_argument(self):
        """THE BUG THIS CATCHES HAPPENED. The conversion block first landed in
        `render_md`, which would have raised NameError on `exempt_out`."""
        import ast
        src = (REPO / "scripts/morning_report_build_2026-10-12.py").read_text(
            encoding="utf-8")
        tree = ast.parse(src)
        md = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == "render_md")
        tts = next(n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name == "render_tts")
        assert "exempt_out" not in ast.unparse(md)
        assert "exempt_out" in ast.unparse(tts)

    def test_render_md_still_renders(self, mods):
        decs = mods["mrb"].decisions(mods["mrb"].task_items())[0]
        assert len(mods["mrb"].render_md(decs, [], [], [], [], None, ())) > 1000


class TestTheLintHelpersAreSound:
    def test_paragraph_offsets_cover_the_text_without_overlap(self, mods):
        text = "One.\n\nTwo two.\n\n  \n\nThree.\n"
        bounds = mods["nvl"].paragraph_offsets(text)
        assert bounds and bounds[0][0] == 0
        for (a, b), (c, _d) in zip(bounds, bounds[1:]):
            assert a <= b <= c, f"offsets overlap or run backwards: {bounds}"

    def test_offsets_use_the_modules_only_splitter(self, mods):
        """PINNED. 2 paragraph numberings drifting apart is the measured defect
        of 2026-09-11; these offsets must come from the same expression.

        ★ THE FIXTURE IS THE BLANK LINE CARRYING ONE SPACE, and the first
        version of this test used an ordinary blank line instead -- on which a
        literal 2-newline split and the module's whitespace-tolerant expression
        AGREE, so the mutation harness found this test GREEN against a splitter
        swap and the assertion proved nothing. The module's own comment names
        this exact case: a blank line carrying one space is a paragraph break to
        the regular expression and not to the literal.
        """
        text = "One.\n \nTwo two.\n\nThree.\n"
        assert len(mods["nvl"].paragraphs(text)) == 3, (
            "the fixture no longer distinguishes the 2 splitters, so this "
            "assertion is vacuous")
        assert len(mods["nvl"].paragraph_offsets(text)) == \
            len(mods["nvl"].paragraphs(text))

    def test_no_spans_changes_nothing(self, mods):
        """NEGATIVE CONTROL: the new argument must be inert when absent."""
        txt, _ = _render(mods)
        f = _write(txt)
        assert len(mods["nvl"].blocking(f)) == len(mods["nvl"].blocking(f, None))
        assert len(mods["nvl"].blocking(f)) == len(mods["nvl"].blocking(f, []))
