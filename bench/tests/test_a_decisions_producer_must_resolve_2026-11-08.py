"""A decision that cites a producer must cite at least 1 that RESOLVES.

WHAT THIS CATCHES, WITH A LIVE REPRODUCTION RATHER THAN A SYNTHETIC ONE.
Entry B102's authored detail carried, as its ENTIRE evidence line, `Producer:
scripts/his_words_arrive_where_nothing_looks_2026-11-03.py` -- a file that has
never existed in this repository, which `git log --all` confirms by returning 0
commits for the path. So its measured figure, 206 of his 1,421 distinct
messages, reached the founder's morning deliverable with no reproducible route.
That is `measured-rate-travels-with-its-script` violated inside the document
the rule exists to protect, and it survived from 2026-11-03 to 2026-11-08
because NOTHING checked it: of the guards that read the decisions data, the
only one touching a field named `evidence_line` reads an unrelated tuple of
line numbers on the seeded-defect catalogue.

The entry's own TASK-LIST evidence field named both correct artefacts the whole
time, so the 2 surfaces disagreed and the task list held the sound citation.

WHY THE PREDICATE IS `AT LEAST ONE` AND NOT `ALL`, which is a deliberate
choice and not laxity. A repair should NAME the phantom producer so the record
shows what was wrong -- B102's own corrected evidence line does exactly that.
Under an ALL rule, writing that history down would itself fail the guard, so
the guard would punish the honest repair. This is the same ANY-versus-ALL
question raised for the task list's `evidence:` field as `qs:65a5b902ff02`, and
here the answer is settled by a concrete requirement rather than a preference.

WHY IT IS CONDITIONAL on a path being cited at all: 22 of 48 authored items
cite no producer, and whether they should is a SEPARATE question. A guard that
conflated the 2 would fire 22 times on its first run and be switched off.

EVERY ASSERTION CALLS THE PRODUCER'S OWN FUNCTION. None restates the rule in
its own words. The function lives in the generator, not here, because 2 callers
need it -- `--check` and this file -- and a duplicated copy is precisely how
`LINE_REF` came to disagree with its guard earlier the same day.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
GEN = REPO / "scripts" / "morning_report_build_2026-10-12.py"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"


@pytest.fixture(scope="module")
def G():
    spec = importlib.util.spec_from_file_location("_mrb_guard", GEN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_mrb_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheFunctionExistsAndIsCalled:
    def test_the_generator_exposes_the_predicate(self, G):
        assert hasattr(G, "decisions_citing_no_resolvable_producer"), (
            "the predicate must live in the generator so `--check` and this "
            "guard cannot drift apart")
        assert callable(G.decisions_citing_no_resolvable_producer)

    def test_the_live_data_satisfies_it(self, G):
        import json
        detail = json.loads(DETAIL.read_text(encoding="utf-8"))
        bad = G.decisions_citing_no_resolvable_producer(detail, root=REPO)
        assert bad == [], (
            "a decision cites producers and NOT ONE of them resolves, so its "
            "figures reach him with no reproducible route:\n  "
            + "\n  ".join(bad))


class TestItCatchesWhatItExistsFor:
    def test_an_item_whose_every_citation_is_absent_is_caught(self, G):
        synth = {"task:X": {"evidence_line":
                            "Producer: `scripts/absent_a_2026-01-01.py` and "
                            "`scripts/absent_b_2026-01-01.py`."}}
        bad = G.decisions_citing_no_resolvable_producer(synth, root=REPO)
        assert len(bad) == 1 and "task:X" in bad[0], bad

    def test_the_b102_shape_is_caught(self, G):
        """The exact string that was live until 2026-11-08."""
        synth = {"task:B102": {"evidence_line":
                               "Producer: scripts/"
                               "his_words_arrive_where_nothing_looks_2026-11-03.py"}}
        bad = G.decisions_citing_no_resolvable_producer(synth, root=REPO)
        assert len(bad) == 1, "the live defect's own shape is not caught"


class TestItDoesNotAccuseCorrectRecords:
    def test_an_item_citing_no_producer_is_exempt(self, G):
        synth = {"task:Y": {"evidence_line": "Producer: none recorded."}}
        assert G.decisions_citing_no_resolvable_producer(synth, root=REPO) == []

    def test_a_deliberate_historical_citation_is_exempt(self, G):
        """A repair must be able to NAME the phantom it replaced."""
        synth = {"task:Z": {"evidence_line":
                            "Producer: `scripts/his_messages.py`, which named "
                            "`scripts/absent_2026-01-01.py` until today."}}
        assert G.decisions_citing_no_resolvable_producer(synth, root=REPO) == [], (
            "naming the absent file as history must not fail the guard, or the "
            "guard punishes the honest repair")

    def test_an_empty_detail_set_is_not_a_finding(self, G):
        assert G.decisions_citing_no_resolvable_producer({}, root=REPO) == []

    def test_underscore_keys_are_skipped(self, G):
        synth = {"_archived": {"evidence_line":
                               "Producer: `scripts/absent_2026-01-01.py`."}}
        assert G.decisions_citing_no_resolvable_producer(synth, root=REPO) == []
