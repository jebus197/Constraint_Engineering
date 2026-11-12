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

    @staticmethod
    def _decisions_generator():
        import importlib.util                                  # noqa: PLC0415
        path = REPO / "scripts" / "build_decisions_file_2026-11-07.py"
        spec = importlib.util.spec_from_file_location("_bdf", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m, path

    def test_the_decisions_generator_does_not_define_its_own_copy(self):
        """One definition. A copy is a second thing to drift.

        ★ CONVERTED FROM SOURCE TEXT TO A PARSED TREE, 2026-11-12, entry B158.
        This asserted `"def _mark_my_paragraphs" not in src`, which is a
        description of the file's spelling. The syntax tree answers the question
        the test is actually asking, and catches what the literal cannot: a
        decorated definition, an `async def`, a method on a class, or any
        spacing other than the single space the literal assumed.
        """
        import ast                                             # noqa: PLC0415

        _m, path = self._decisions_generator()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        own = [n.lineno for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == "_mark_my_paragraphs"]
        assert not own, (
            f"the decisions generator defines its own copy of the marker at "
            f"line(s) {own}; it must call the single implementation it already "
            f"receives as `mrb`")

    def test_the_generator_USES_the_marker_it_receives(self):
        """★ THE POSITIVE HALF, AND IT IS THE STRONGER ONE. Not defining a copy
        is not the same as using the shared one -- a generator that defined
        nothing and called nothing would pass the test above. A fake `mrb` is
        passed whose marker appends a sentinel, and the sentinel must reach the
        rendered output."""
        m, _path = self._decisions_generator()
        sentinel = "SENTINEL_FROM_THE_SHARED_MARKER_2026_11_12"

        class _FakeMRB:
            #: `render` touches exactly 2 attributes of `mrb`, derived by syntax
            #: tree rather than guessed: `_spoken` and `_mark_my_paragraphs`.
            #: A thinner fake failed with an AttributeError on `_spoken`, which
            #: is the fake being wrong and not the subject.
            _spoken = staticmethod(lambda t: t)

            @staticmethod
            def _mark_my_paragraphs(lines, exempt_spans, headings):
                lines.append(sentinel)
                return 1

        out = m.render(_FakeMRB(), [], spoken=True)
        assert sentinel in out, (
            "the decisions generator did not use the marker it was handed, so "
            "his asterisk convention comes from somewhere this test cannot see")

    def test_a_missing_marker_REFUSES_loudly_rather_than_silently(self):
        """The branch's own promise is 'LOUD, not silent'. An absent marker must
        stop the file being written, not produce one without the convention."""
        m, _path = self._decisions_generator()

        class _MRBWithoutIt:
            _spoken = staticmethod(lambda t: t)   # present, so the refusal below
                                                  # can only be about the marker

        with pytest.raises(SystemExit) as e:
            m.render(_MRBWithoutIt(), [], spoken=True)
        assert "_mark_my_paragraphs" in str(e.value), str(e.value)

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


class TestNoProseParagraphGoesUnmarked:
    """★ THE DISCRIMINATING ASSERTION, ADDED AFTER A P-PASS SHOWED THE FIX
    WAS UNGUARDED.

    The class above asks whether the spoken decisions file carries marks AT
    ALL, and 4 marks satisfies that. But 4 was the number the DEFECT produced:
    `L = [head]` put the whole multi-line header block in 1 list element, so
    the per-line walk saw a single line and the title exemption swallowed the
    header, leaving 4 of my 6 header paragraphs unmarked. Reverting the split
    left every test in this file GREEN -- the fix was real and nothing would
    have caught its loss.

    So the property is not "some marks exist" but "NO paragraph of mine is
    unmarked", and every unmarked paragraph opener must therefore be
    classifiable as something the convention deliberately spares: the title,
    a heading, an all-caps label, a numbered item, a timestamp, or the
    foot-line. Anything else is my prose going unmarked.
    """

    #: What the convention deliberately does NOT mark, each with its reason.
    #: A line matching none of these and carrying no marker is a defect.
    @staticmethod
    def _spared(line: str, index: int, first_nonblank: int) -> bool:
        s = line.strip()
        if index == first_nonblank:
            return True                      # the document title
        if re.match(r"^DECISION \d+\.", s):
            return True                      # a recorded heading
        if re.match(r"^\d+\.", s):
            return True                      # a numbered list item
        if re.match(r"^\d+ \w+ \d{4}", s):
            return True                      # a date stamp
        if "Written under CDSFL note standard" in s:
            return True                      # the foot-line
        letters = [c for c in s if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            return True                      # an all-caps section label
        return False

    def test_every_prose_paragraph_in_the_spoken_file_is_marked(self):
        files = sorted((REPO / "experimental_notes").glob(
            "Decisions_Awaiting_You_*_GENERATED.txt"))
        if not files:
            pytest.skip("no generated spoken decisions file in this checkout")
        lines = files[-1].read_text(encoding="utf-8").splitlines()
        first_nb = next((i for i, l in enumerate(lines) if l.strip()), 0)
        openers, at_start = [], True
        for i, l in enumerate(lines):
            if not l.strip():
                at_start = True
                continue
            if at_start:
                openers.append((i, l))
            at_start = False
        assert len(openers) > 20, (
            f"only {len(openers)} paragraph openers found in "
            f"{files[-1].name}; this guard's own walk has drifted")
        unmarked = [(i, l.strip()[:70]) for i, l in openers
                    if not l.startswith("*")
                    and not self._spared(l, i, first_nb)]
        assert unmarked == [], (
            f"{len(unmarked)} prose paragraph(s) in {files[-1].name} carry no "
            f"marker, so his convention reaches some of my prose and not the "
            f"rest. This is the state `L = [head]` produced -- the header "
            f"block in 1 list element, invisible to the per-line walk -- and "
            f"the file still carried 4 marks, which a 'does it carry any "
            f"marks' check passes: {unmarked}")

    def test_the_header_is_a_list_of_lines_not_one_block(self):
        """The mechanism, pinned directly, because the end-to-end test above
        can only see the consequence."""
        #: ★ READ THE PARSED ASSIGNMENT, NOT THE SOURCE TEXT. The first
        #: version asserted `'L = [head]' not in src` and FAILED immediately,
        #: because this file's own explanatory comment quotes that string --
        #: a scar reading as a wound, which is the shape this project records
        #: against a detector that spelled out its own pattern.
        import ast
        src = (REPO / "scripts" / "build_decisions_file_2026-11-07.py").read_text(
            encoding="utf-8")
        assigns = []
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "L" for t in node.targets):
                assigns.append(node.value)
        assert assigns, "no assignment to `L` found; the renderer moved"
        single_block = [a for a in assigns
                        if isinstance(a, ast.List) and len(a.elts) == 1
                        and isinstance(a.elts[0], ast.Name)
                        and a.elts[0].id == "head"]
        assert single_block == [], (
            "the header is back in a single list element, so the paragraph "
            "walk cannot see inside it and the title exemption swallows every "
            "paragraph in it")
        split = [a for a in assigns
                 if isinstance(a, ast.Call)
                 and isinstance(a.func, ast.Attribute)
                 and a.func.attr == "split"]
        assert split, (
            "the header is no longer split into lines; the marker's per-line "
            "walk needs 1 line per element")
