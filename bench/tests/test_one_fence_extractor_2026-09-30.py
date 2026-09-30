"""One fenced-Python extractor, and a carrier failure is not a verdict.

WHY THIS FILE EXISTS, and it is a gap in the seats' own delivery rather than in
their reasoning. The 2026-09-30 intelligence-first review produced 4 fixes. 1 of
them, fable's non-cure ledger, arrived with its own test. The other 3 arrived with
NO guard: reverting cc2's regex widening, reverting its de-duplication of the
second extractor, or removing fable's carrier-abstain guards each left the whole
adjacent suite green at 253 passed. cc2's reported "250 targeted tests pass" was
the EXISTING suite continuing to pass, not new coverage. By the project's own
additive standard a fix nothing executes can regress silently, so the 3 are
covered here together.

WHAT THE 3 FIXES WERE.

1. **TWO EXTRACTORS ANSWERED THE SAME QUESTION AND DRIFTED.**
   `bugzilla_loop._PY_FENCE` and `reference_runner_v3._gateable_source` both
   decide whether a document carries fenced Python. cc2 measured them splitting
   on 3 of 13 realistic shapes -- a tilde fence, a fence carrying an info-string
   attribute, and a CRLF-authored document -- every one in the direction "the
   runner sees code, bugzilla does not". On such a document S_k's prose path
   engages while `bugzilla_loop` logs "carries no fenced Python listing", which
   is FALSE of the document, and the weaker claim is the one that reached the log.

2. **THE WIDENING THAT LICENSED THE DE-DUPLICATION.** The runner's pattern
   allowed a blockquote marker plus AT MOST ONE space, so `>  ```python` -- a
   CommonMark blockquote containing an indented fence, which a real author writes
   -- was recognised by the narrow private regex and NOT by the runner. The
   removal clause requires the survivor to DOMINATE, and it did not until
   `[ \\t]?` became `[ \\t]*`. Verified below as STRICTLY ADDITIVE: over a
   48-shape product no shape that matched before stops matching.

3. **A CARRIER FAILURE IS NOT A VERDICT.** A fixture falsifier that cannot locate
   the evidence it recomputes from raised `AssertionError` -- which the decider
   reads as CONFIRMED -- so "I cannot read the evidence" was indistinguishable
   from "the defect is demonstrated". fable found this through `fix_efficacy`'s
   own probe, which then refused a verdict on the fixture's CORRECT fix. It is the
   same class as the absent/empty-target guard added earlier the same day,
   extended one level inward: `AssertionError` is reserved for a POSITIVELY
   located false claim.

`_PY_FENCE` IS STILL DEFINED AND THAT IS DELIBERATE. cc2 replaced both of its
call sites and left the definition, recording the dominance measurement so the
removal stays a human decision. This file does not require its absence.
"""
from __future__ import annotations

import itertools
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from reference_runner_v3 import _gateable_hunks, _gateable_source  # noqa: E402

#: Shapes a real author writes. The 3 cc2 measured as splitting the extractors
#: are here by name so a regression names itself.
SHAPES = {
    "plain backtick fence": "```python\nx = 1\n```\n",
    "tilde fence": "~~~python\nx = 1\n~~~\n",
    "info-string attribute": "```python {.numberLines}\nx = 1\n```\n",
    "CRLF authored": "```python\r\nx = 1\r\n```\r\n",
    "short lang tag py": "```py\nx = 1\n```\n",
    "indented inside a list item": "- item\n\n  ```python\n  x = 1\n  ```\n",
    "blockquoted, one space": "> ```python\n> x = 1\n> ```\n",
    "blockquoted, two spaces": ">  ```python\n>  x = 1\n>  ```\n",
}


class TestTheTwoExtractorsAgree:
    """Called against each other on identical bytes, never read as source."""

    def test_every_shape_gets_the_same_answer_from_both(self):
        split = []
        for label, doc in SHAPES.items():
            a, _ = _gateable_source(doc, "d.md")
            b = _gateable_hunks(doc, "d.md")
            if bool(a) != bool(b):
                split.append(f"{label}: _gateable_source={'code' if a else 'none'} "
                             f"_gateable_hunks={'code' if b else 'none'}")
        assert not split, (
            "the 2 fenced-Python extractors disagree on "
            f"{len(split)} of {len(SHAPES)} shapes: {split}. Whichever sees LESS "
            "will log 'carries no fenced Python listing' about a document that "
            "does, and the weaker claim is the one that reaches the record.")

    def test_bugzilla_no_longer_calls_the_narrow_regex(self):
        """The de-duplication itself, at the CALL SITES rather than the definition."""
        src = (REPO / "bench" / "bugzilla_loop.py").read_text(encoding="utf-8")
        live = [ln for ln in src.splitlines()
                if "_PY_FENCE.findall" in ln and not ln.lstrip().startswith("#")]
        assert not live, (
            f"{len(live)} live call(s) to the narrow private regex remain: {live}. "
            f"Both call sites must use _gateable_hunks, or the 2 extractors drift "
            f"apart again. The DEFINITION may stay -- only calls are replaced.")


class TestTheWideningIsStrictlyAdditive:
    """The property that licenses the de-duplication under the removal clause."""

    OLD = re.compile(
        r"^(?P<prefix>[ \t]*(?:>[ \t]?)*)(?P<f>```|~~~)[ \t]*(?:python|py)\b[^\n]*\n"
        r"(?P<body>.*?)\n(?P=prefix)(?P=f)[ \t]*$", re.S | re.M)
    NEW = re.compile(
        r"^(?P<prefix>[ \t]*(?:>[ \t]*)*)(?P<f>```|~~~)[ \t]*(?:python|py)\b[^\n]*\n"
        r"(?P<body>.*?)\n(?P=prefix)(?P=f)[ \t]*$", re.S | re.M)

    def _product(self):
        for pre, f, lang in itertools.product(
                ["", "  ", "\t", "> ", ">  ", ">>", "> > ", ">\t"],
                ["```", "~~~"],
                ["python", "py", "python {.numberLines}"]):
            yield f"{pre}{f}{lang}\nx = 1\n{pre}{f}"

    def test_no_shape_that_matched_before_stops_matching(self):
        shapes = list(self._product())
        lost = [s.splitlines()[0] for s in shapes
                if self.OLD.search(s) and not self.NEW.search(s)]
        assert not lost, (
            f"the widening LOST {len(lost)} shape(s): {lost[:5]}. It must accept a "
            f"superset, or extraction that worked before is silently gone.")

    def test_the_widening_actually_gained_something(self):
        """A widening that gains nothing is an addition that does nothing."""
        shapes = list(self._product())
        gained = [s.splitlines()[0] for s in shapes
                  if self.NEW.search(s) and not self.OLD.search(s)]
        assert gained, (
            "the widened pattern recognises nothing the narrow one did not, so it "
            "cannot be what licenses the de-duplication")

    def test_the_live_pattern_is_the_widened_one(self):
        """Ties the property above to the code actually in use."""
        for doc in (">  ```python\n>  x = 1\n>  ```\n",):
            got, _ = _gateable_source(doc, "d.md")
            assert got, (
                "a blockquote containing an indented fence is not recognised by "
                "the live extractor, so the widening is not in force")


class TestACarrierFailureAbstains:
    """A falsifier that cannot read its evidence must not claim the defect."""

    def test_an_unreadable_evidence_table_does_not_CONFIRM(self, tmp_path):
        sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))
        import stem_fixtures as S
        from bench.falsifier_verify import reverify_falsifier

        for fx in S.load_all():
            doc = tmp_path / fx.doc_name
            # A document with real prose but NONE of the evidence the falsifier
            # recomputes from: the carrier case, distinct from empty or absent.
            doc.write_text("# Title\n\nSome prose carrying no tables and no "
                           "listings whatsoever.\n" * 3, encoding="utf-8")
            r = reverify_falsifier(fx.falsifier(doc), repo_root=str(REPO))
            v = r if isinstance(r, str) else getattr(r, "verdict", repr(r))
            assert v != "CONFIRMED", (
                f"{fx.key}: a document containing none of the evidence returned "
                f"CONFIRMED. 'I cannot read the evidence' must not be "
                f"indistinguishable from 'the defect is demonstrated'.")
