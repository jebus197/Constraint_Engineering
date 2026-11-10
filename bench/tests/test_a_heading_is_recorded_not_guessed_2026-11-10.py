"""A HEADING IS RECORDED WHERE IT IS EMITTED, NEVER INFERRED FROM ITS SHAPE.

B105, his ruling of 2026-11-08: *"change this so that your messages open with
an asterisk *like this but do not close with one"*. `_mark_my_paragraphs` in
`scripts/morning_report_build_2026-10-12.py` implements it.

WHAT WENT WRONG ON THE FIRST BUILD, and it is the reason this file exists.
The function decided "this line is a heading, leave it alone" with an all-caps
test over the line's letters. A numbered decision heading reads
`DECISION 1. B13, admitting a model is not trivial`, whose headline is prose,
so it failed that test and all 17 were marked. 3 consequences, 2 of them
invisible to the function itself:

  1. 17 spoken instances of the word "asterisk" landed on the lines that give
     the report its structure. His ruling governs PARAGRAPHS, not headings.
  2. The FOOT-LINE was marked. The note standard requires exactly
     `Written under CDSFL note standard <version>.` as the final content, and
     a missing or altered foot-line flags a note that violates the standard.
  3. A sibling guard, `test_his_copy_is_the_index_2026-11-08.py`, went red,
     because its pattern for a numbered decision heading no longer matched.

B105'S OWN FINDING WAS THAT A SHAPE HEURISTIC MISREADING HEADINGS WAS 1 OF THE
3 MEASURED CAUSES OF HIS LOST RESPONSES, so guessing at a heading here would
repeat the error that entry diagnosed. `render_tts` knows which lines it emits
as headings; it now records their indices as it emits them, exactly as `_ex`
already records quoted spans. 1 record, no second opinion.

AND THE MECHANISM WAS REACHED BY NO TEST AT ALL until this file. The symmetric
form of `additive-standard` says an addition nothing reaches is not additive,
so the build of 2026-11-10 02:50 was itself in breach until now.
"""
import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
MRB = REPO / "scripts" / "morning_report_build_2026-10-12.py"

#: The 3 labels that open MY prose paragraphs in the spoken report. Used as the
#: ANTI-VACUITY probe: a repair that marked nothing at all would satisfy every
#: "is not marked" assertion in this file and fail these.
MY_PARAGRAPH_LABELS = ("What it is.", "Why it needs a decision.", "The evidence.")


@pytest.fixture(scope="module")
def mrb():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_mrb_headings", MRB)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_mrb_headings"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rendered(mrb):
    try:
        items = mrb.task_items()
        decs = mrb.decisions(items)[0]
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"the decision queue is not collectable here: {exc}")
    if len(decs) < 2:
        pytest.skip(f"only {len(decs)} decision(s); not exercisable")
    full = mrb.render_tts(decs, [], [], [], [], None, (), detail=True)
    return decs, full


class TestTheRecordedHeadingsAreNotMarked:
    def test_every_numbered_decision_heading_is_bare(self, rendered):
        decs, full = rendered
        bare = re.findall(r"^DECISION \d+\.", full, re.M)
        marked = re.findall(r"^\*DECISION \d+\.", full, re.M)
        assert len(bare) == len(decs), (
            f"{len(bare)} bare decision headings for {len(decs)} decisions")
        assert marked == [], f"{len(marked)} decision heading(s) carry a marker"

    def test_the_options_subheading_is_bare(self, rendered):
        _decs, full = rendered
        lines = full.splitlines()
        assert "*The options." not in lines, "a sub-heading carries a marker"
        #: NOT VACUOUS: the bare form must actually be present, or this passes
        #: on a render that stopped emitting the sub-heading altogether.
        assert "The options." in lines, "the sub-heading is absent entirely"

    def test_the_foot_line_is_exact_and_final(self, rendered, mrb):
        _decs, full = rendered
        expect = f"Written under CDSFL note standard {mrb.CURRENT_NOTE_STANDARD}."
        last = full.rstrip().splitlines()[-1]
        assert last == expect, (
            f"the foot-line must be the final content, exactly. Got {last!r}")

    def test_no_marker_is_a_bullet(self, rendered):
        """THE DISTINCTION THAT KEEPS THIS CLEAR OF THE TTS RULE.
        `test_markdown_in_a_tts_file_2026-11-04.py` forbids a line opening with
        an asterisk AND A SPACE, which Read Aloud speaks as a bullet. His
        amendment is an asterisk with NO space, so the 2 rules do not collide --
        but only while the marker is written tight against the text."""
        _decs, full = rendered
        bullets = [l for l in full.splitlines() if l.startswith("* ")]
        assert bullets == [], f"{len(bullets)} line(s) read as a bullet: {bullets[:3]}"


class TestTheMarkerStillDoesItsJob:
    """ANTI-VACUITY. Every assertion above is of the form "X is NOT marked", so
    all of them pass on a function that marks nothing. These fail on it."""

    @pytest.mark.parametrize("label", MY_PARAGRAPH_LABELS)
    def test_my_prose_paragraphs_are_marked(self, rendered, label):
        decs, full = rendered
        n = sum(1 for l in full.splitlines() if l.startswith("*" + label))
        assert n == len(decs), (
            f"{n} of {len(decs)} '{label}' paragraphs carry the marker")

    def test_the_opening_prose_is_marked(self, rendered):
        _decs, full = rendered
        first = next(l for l in full.splitlines() if l.startswith("*"))
        assert first.startswith("*This report is generated"), (
            f"the first marked line is not the opening prose: {first[:60]!r}")


class TestTheRecordIsLoadBearing:
    """SENSITIVITY. Without these, the heading fix could be inert -- the
    headings might be unmarked for some unrelated reason and the recorded
    index doing nothing. These call the function BOTH ways on the same lines
    and require the record to change the outcome."""

    #: ★ THE PROBE CARRIES A TITLE LINE, AND THE FIRST VERSION DID NOT.
    #: Without it the heading sat at index 0 and was spared by the DOCUMENT
    #: TITLE exemption -- `_first_nonblank` -- rather than by the heading
    #: record, so the unrecorded walk ALSO left it bare and this class could
    #: not distinguish the 2 mechanisms. The probe's position manufactured
    #: the result. Index 2 is the heading, index 4 the paragraph.
    HEAD_I, PARA_I = 2, 4

    @classmethod
    def _case(cls):
        #: A mixed-case numbered heading, then a blank, then a paragraph. This
        #: is the exact shape the all-caps test cannot classify.
        return ["MORNING REPORT, 10 November 2026",
                "",
                "DECISION 1. B13, admitting a model is not trivial",
                "",
                "What it is. Putting a model that does not exist through it."]

    def test_without_the_record_the_heading_is_marked(self, mrb):
        lines = self._case()
        mrb._mark_my_paragraphs(lines, [], ())
        assert lines[self.HEAD_I].startswith("*"), (
            "the all-caps test already exempts this heading, so the recorded "
            "index is inert and this file's subject does not exist")

    def test_with_the_record_the_heading_is_spared(self, mrb):
        lines = self._case()
        mrb._mark_my_paragraphs(lines, [], (self.HEAD_I,))
        assert not lines[self.HEAD_I].startswith("*"), "the recorded index was ignored"

    def test_the_record_spares_only_what_it_names(self, mrb):
        """The record must not be a blanket off-switch."""
        lines = self._case()
        marked = mrb._mark_my_paragraphs(lines, [], (self.HEAD_I,))
        assert lines[self.PARA_I].startswith("*"), "the paragraph was spared too"
        assert marked == 1, f"marked {marked}, expected 1"

    def test_render_tts_actually_populates_the_record(self, rendered):
        """WIRED TO A CALLER. If `render_tts` passed an empty record, every
        assertion in the first class would fail -- but it would fail for a
        reason a reader could mistake for a shape problem. This pins the wiring
        itself by requiring the live render to differ from the unrecorded walk
        on the same lines."""
        decs, full = rendered
        lines = full.splitlines()
        heads = [i for i, l in enumerate(lines) if re.match(r"^DECISION \d+\.", l)]
        assert len(heads) == len(decs)
        probe = [l.lstrip("*") for l in lines]
        import importlib
        m = sys.modules["_mrb_headings"]
        m._mark_my_paragraphs(probe, [], ())
        assert any(probe[i].startswith("*") for i in heads), (
            "with no record the same lines are still spared, so render_tts "
            "passing a populated record cannot be what fixed them")


class TestEverySpokenGeneratorAppliesTheConvention:
    """★ HIS RULING GOVERNS "THE GENERATED TTS FILES", PLURAL, AND THE BUILD
    COVERED 1 OF 2 GENERATORS UNTIL 2026-11-10.

    `_mark_my_paragraphs` was wired into `render_tts` in the morning-report
    generator and into nothing else. `scripts/build_decisions_file_2026-11-07.py`
    writes 3 further spoken artefacts -- the repository `.txt`, its markdown
    twin and the Desktop copy -- and applied no marker at all, so 0 of that
    file's paragraphs carried the convention.

    I NEARLY CLOSED B105 ON THAT STATE. The entry's own words said the
    remaining build was done, the guard was green, and the first verification
    I ran reported 0 marked paragraphs in the generated decisions file -- a
    build present in 1 place and absent in another, which is the shape this
    project records against a widened pattern fixed in 1 reader and left
    narrow in its sibling. The entry stayed OPEN and the second generator was
    wired instead.

    THE MARKER IS IMPORTED, NEVER COPIED. A second definition of his
    convention would be a second thing to drift; this project has measured
    what copies cost. The decisions generator calls the morning-report
    module's function, and refuses LOUDLY if it is ever renamed away.
    """

    @staticmethod
    def _generators():
        return (REPO / "scripts" / "morning_report_build_2026-10-12.py",
                REPO / "scripts" / "build_decisions_file_2026-11-07.py")

    def test_both_generators_reach_the_one_marker(self):
        hits = [p for p in self._generators()
                if "_mark_my_paragraphs" in p.read_text(encoding="utf-8")]
        assert len(hits) == 2, (
            f"{len(hits)} of 2 spoken generators reference the marker: "
            f"{[p.name for p in hits]}. His ruling governs the generated TTS "
            f"files, plural.")

    def test_the_decisions_generator_does_not_define_its_own_copy(self):
        """One definition. A copy is a second thing to drift."""
        src = (REPO / "scripts" / "build_decisions_file_2026-11-07.py").read_text(
            encoding="utf-8")
        assert "def _mark_my_paragraphs" not in src, (
            "the decisions generator defines its own copy of the marker; it "
            "must call the single implementation it already receives as `mrb`")

    def test_the_spoken_decisions_file_carries_the_convention(self):
        """END TO END on the artefact he actually listens to."""
        files = sorted((REPO / "experimental_notes").glob(
            "Decisions_Awaiting_You_*_GENERATED.txt"))
        if not files:
            pytest.skip("no generated spoken decisions file in this checkout")
        lines = files[-1].read_text(encoding="utf-8").splitlines()
        marked = [l for l in lines if l.startswith("*")]
        assert marked, (
            f"{files[-1].name} carries 0 marked paragraphs, so his asterisk "
            f"convention reaches the morning report and not this file")
        closes = [l for l in marked
                  if l.rstrip().endswith("*") and len(l.strip()) > 1]
        assert closes == [], (
            f"{len(closes)} paragraph(s) also CLOSE with an asterisk. His "
            f"amendment of 2026-11-08 is open-only: Read Aloud speaks every "
            f"asterisk, so 2 per paragraph is twice the noise of 1.")
        assert [l for l in lines if l.startswith("* ")] == [], (
            "a line reads as a bullet, which Read Aloud speaks as 'asterisk'")
        heads = [l for l in lines if re.match(r"^\*?DECISION \d+\.", l)]
        assert [l for l in heads if l.startswith("*")] == [], (
            "a decision heading carries the marker; his ruling governs "
            "paragraphs, not headings")
        foot = [l for l in lines if "Written under CDSFL note standard" in l]
        assert foot, "the foot-line is missing"
        assert not foot[0].startswith("*"), (
            "the foot-line carries the marker; the note standard requires "
            "that exact line as the final content")
