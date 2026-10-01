#!/usr/bin/env python3
"""The labelled set is real, and its limitation is held rather than forgotten.

WHAT IT MEASURES. `scripts/claim_classifier_labelled_set_2026-10-01.py` scores
"does this document contain at least 1 decidable claim?" against known labels:
10 positives (the 5 corpus fixtures, intact and fence-stripped) and 5 mood-prose
negatives. The status quo -- fence syntax, `_gateable_source` -- scores accuracy
10 of 15 with sensitivity 5 of 10, missing every prose variant.

THE PROPERTY THIS FILE EXISTS TO PROTECT is the LIMITATION, not the headline.
The anchor arm locates claims using anchors taken from the corpus's own claim
lists -- the answer key -- so its 15 of 15 is a lookup's score, not a
classifier's. If that caveat is ever dropped, the project would be holding a
100% accuracy figure for a classifier it never tested, which is the answer-key
class of error it has been bitten by before. So the caveat is asserted here, and
so is the fact that the arm collapses on a document the corpus does not
describe.

Run:  python3 -m pytest bench/tests/test_claim_classifier_labelled_set_2026-10-01.py -q
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench"), str(REPO / "bench/tests/fixtures/stem")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SCRIPT = REPO / "scripts" / "claim_classifier_labelled_set_2026-10-01.py"


@pytest.fixture(scope="module")
def mod():
    if not SCRIPT.is_file():
        pytest.fail(f"{SCRIPT.name} is missing")
    spec = importlib.util.spec_from_file_location("claim_clf", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["claim_clf"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rows(mod):
    return mod._documents()


class TestTheSetIsLabelledAndBalancedEnoughToMeanSomething:
    def test_it_has_both_positives_and_negatives(self, rows):
        pos = [r for r in rows if r[2]]
        neg = [r for r in rows if not r[2]]
        assert len(pos) >= 8 and len(neg) >= 4, (len(pos), len(neg))

    def test_every_document_is_substantial_enough_to_judge(self, rows):
        thin = [(n, len(t)) for n, t, _l, _o in rows if len(t) < 150]
        assert thin == [], f"documents too short to carry a claim: {thin}"

    def test_the_negatives_really_carry_no_computable_claim(self, mod):
        """A negative that contains a number would be a mislabel."""
        import re
        for name, text in mod.MOOD_CONTROLS.items():
            assert not re.search(r"\d+\.\d+|\d+\s*(?:%|per cent)", text), (
                f"{name} contains a figure, so its NEGATIVE label is unsafe")

    def test_the_prose_variants_really_lost_their_fences(self, rows):
        prose = [(n, t) for n, t, _l, _o in rows if n.endswith("_prose")]
        assert prose, "no fence-stripped variants were built"
        for name, text in prose:
            assert "```" not in text and "~~~" not in text, name


class TestTheStatusQuoIsMeasuredAndItsFailureIsNamed:
    def test_the_syntax_arm_misses_every_prose_positive(self, mod, rows):
        missed = [n for n, t, label, _o in rows
                  if label and not mod._syntax_arm(t, n)]
        assert missed, (
            "the syntax arm now finds every positive; if that is real, this "
            "whole measurement and the claim channel's justification need "
            "restating")
        assert all(n.endswith("_prose") for n in missed), (
            f"the syntax arm misses something other than the prose variants, "
            f"which is a different finding from the one recorded: {missed}")

    def test_the_syntax_arm_raises_no_false_positive_on_mood_prose(self, mod,
                                                                   rows):
        wrong = [n for n, t, label, _o in rows
                 if not label and mod._syntax_arm(t, n)]
        assert wrong == [], (
            f"fence syntax claimed a mood-prose document is addressable: "
            f"{wrong}")

    def test_the_scoring_adds_up(self, mod, rows):
        s = mod._score(rows, lambda n, t: mod._syntax_arm(t, n))
        assert s["tp"] + s["fn"] + s["fp"] + s["tn"] == len(rows) == s["n"]
        assert s["correct"] == s["tp"] + s["tn"]


class TestTheAnswerKeyCaveatIsHeldAndNotMerelyWritten:
    """THE POINT OF THIS FILE."""

    def test_the_anchor_arm_collapses_on_a_document_the_corpus_never_saw(self,
                                                                        mod):
        """So its score is a lookup's, by execution and not by assertion."""
        unseen = (
            "A NOTE THE CORPUS DOES NOT DESCRIBE. The measured throughput was "
            "48.2 requests per second against a stated budget of 50, so the "
            "service is 3.6 per cent under target and the stated headroom of "
            "12 per cent cannot be right."
        )
        assert mod._claim_arm(unseen) is False, (
            "the anchor arm found a claim in a document whose anchors it "
            "cannot possess, so it is doing something other than lookup and "
            "the caveat needs re-deriving")

    def test_the_script_states_the_caveat_in_its_own_output(self, mod, capsys):
        mod.main([])
        out = capsys.readouterr().out
        assert "ANSWER KEY" in out, (
            "the output no longer warns that arm B uses the answer key; a "
            "reader would take 100% as a classifier's accuracy")
        assert "not a classifier" in out

    def test_the_model_arm_set_withholds_its_labels(self, mod, tmp_path):
        mod.main(["--emit-model-set", str(tmp_path)])
        docs = sorted((tmp_path / "documents").glob("*.md"))
        assert len(docs) >= 12, len(docs)
        labels = json.loads(
            (tmp_path / "LABELS_WITHHELD.json").read_text(encoding="utf-8"))
        assert len(labels) == len(docs)
        for d in docs:
            body = d.read_text(encoding="utf-8")
            assert "has_decidable_claim" not in body, (
                f"{d.name} carries the label it is meant to be scored on")

    def test_the_emitted_documents_match_the_measured_set(self, mod, rows,
                                                          tmp_path):
        mod.main(["--emit-model-set", str(tmp_path)])
        emitted = {p.stem for p in (tmp_path / "documents").glob("*.md")}
        assert emitted == {n for n, _t, _l, _o in rows}
