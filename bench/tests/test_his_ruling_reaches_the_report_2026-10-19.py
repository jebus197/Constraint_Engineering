"""His ruling must reach the ROUTING predicate, not only the output record.

THE DEFECT, 2026-10-19. `morning_report_build_2026-10-12.decisions()` routed an
item out of the decision list on `d.get("ruled")`, where `d` is the AUTHORED
DETAIL. A task entry's ruling does not arrive there: it arrives on `it`, from
the marker's `ruled:` field. The merge `{**it, **d}` then carried the date into
the OUTPUT, so anything reading the merged record saw the ruling while the
routing predicate did not. A producer and a consumer that disagree, each
individually correct -- the shape `execute-do-not-grep` names.

THE COST WAS HIS. He ruled on B31 on 2026-10-18, "Your fix is approved"
(Responses/Review_Stop_And_Declared_Modes_2026-10-18.txt, read with
scripts/read_founder_responses_2026-10-11.py), and the generated report of
2026-10-19 put it to him again. His reply: "Then if I already ruled. Why are
you presenting it as a decision required from me again? Again your fix is
approved. Do it." 6 of the 7 live decisions in that report were in this state.

THESE TESTS CALL `decisions()` AND COMPARE OUTPUTS. None asserts on source text.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GEN = ROOT / "scripts" / "morning_report_build_2026-10-12.py"


def _gen():
    spec = importlib.util.spec_from_file_location("_mrb", GEN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_mrb"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def g():
    return _gen()


# ── 1. the marker's ruled date must route the item out ──────────────────────

def test_a_marker_ruling_routes_a_task_item_out_of_decisions(g, monkeypatch):
    """The exact defect: ruling on `it`, nothing on `d`."""
    item = {"key": "task:ZZ1", "headline": "a constructed entry", "ruled": "2026-10-19"}
    monkeypatch.setattr(g, "DETAIL", _detail_with({"task:ZZ1": {"what": "x"}}))
    attached, _missing, _orphan = g.decisions([item])
    assert len(attached) == 1
    assert attached[0].get("no_ruling_needed") == "2026-10-19", (
        "a marker's `ruled:` date did not route the item out of the decision "
        "list; this is the 2026-10-19 defect returning")


def test_without_a_ruling_anywhere_it_stays_a_decision(g, monkeypatch):
    """ANTI-VACUITY. If everything routed out, the test above could not fail."""
    item = {"key": "task:ZZ2", "headline": "a constructed entry", "ruled": None}
    monkeypatch.setattr(g, "DETAIL", _detail_with({"task:ZZ2": {"what": "x"}}))
    attached, _m, _o = g.decisions([item])
    assert not attached[0].get("no_ruling_needed"), (
        "an item with no ruling on either side was routed out anyway")


def test_the_authored_detail_still_routes_on_its_own(g, monkeypatch):
    """The original path must keep working: a ruling in the detail alone."""
    item = {"key": "task:ZZ3", "headline": "a constructed entry"}
    monkeypatch.setattr(
        g, "DETAIL", _detail_with({"task:ZZ3": {"what": "x", "ruled": "2026-10-18"}}))
    attached, _m, _o = g.decisions([item])
    assert attached[0].get("no_ruling_needed") == "2026-10-18"


def test_struck_permanently_still_routes_out(g, monkeypatch):
    item = {"key": "task:ZZ4", "headline": "a constructed entry"}
    monkeypatch.setattr(
        g, "DETAIL",
        _detail_with({"task:ZZ4": {"what": "x", "struck_permanently": True}}))
    attached, _m, _o = g.decisions([item])
    assert attached[0].get("no_ruling_needed") == "struck permanently"


# ── 2. MUTATION 2's gap: a falsy detail value must not clobber the marker ───

def test_a_null_ruled_in_the_detail_cannot_erase_a_marker_date(g, monkeypatch):
    """`{**it, **d}` lets `d` overwrite `it`. If the detail ever carries
    `"ruled": null` the merged record would claim no ruling while
    `no_ruling_needed` said otherwise. Measured 2026-10-19: 0 of 29 authored
    entries do this today, so the guard protects a reachable future state
    rather than a present one -- and without this test the explicit
    `"ruled": ruled` in the output is an addition nothing reaches."""
    item = {"key": "task:ZZ5", "headline": "a constructed entry", "ruled": "2026-10-19"}
    monkeypatch.setattr(
        g, "DETAIL", _detail_with({"task:ZZ5": {"what": "x", "ruled": None}}))
    attached, _m, _o = g.decisions([item])
    rec = attached[0]
    assert rec.get("no_ruling_needed") == "2026-10-19"
    assert rec.get("ruled") == "2026-10-19", (
        "the authored detail's null erased the marker's ruling date from the "
        "merged record, leaving no_ruling_needed set and ruled empty")


# ── 3. his duplicate complaint, mechanised ──────────────────────────────────

_FIG = re.compile(r"\d[\d,]*\.?\d*%?")


def _figures(s: str) -> set[str]:
    return set(_FIG.findall(s or ""))


def test_no_two_live_decisions_restate_the_same_measurement(g):
    """HIS COMPLAINT, 2026-10-19, verbatim: "I literally just answered this
    above! And I ruled previously!" -- written against DECISION 7 of a report
    whose DECISION 5 asked the same question.

    Measured that day: `task:B34` and `study:serialisation_cures_matched_
    failures` shared 9 figures at Jaccard 0.6000 -- the whole measurement,
    1 of 68 rounds, 1.4706%, interval 0.2601% to 7.8710%, 47 rounds for 50%
    power and 109 for 80%. Agreed by hand, by scipy and by mpmath.

    The threshold is 0.55 rather than 0.50 because a pair sharing only the
    token "1" scored 0.5000 on that day's data (B31 against B33) and is not a
    duplicate. A single common digit must not read as a restatement."""
    items = g.task_items() + g.study_items()
    decs, _m, _o = g.decisions(items)
    live = [d for d in decs if not d.get("no_ruling_needed")]
    sets = {d["key"]: _figures(d.get("evidence_line")) for d in live}
    dupes = []
    keys = sorted(sets)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = sets[a], sets[b]
            if not (A | B):
                continue
            j = len(A & B) / len(A | B)
            if j >= 0.55:
                dupes.append((round(j, 4), a, b, sorted(A & B)))
    assert not dupes, (
        f"{len(dupes)} pair(s) of LIVE decisions restate the same measurement "
        f"to him in one report: {dupes}\nHe reads this as being asked the same "
        f"question twice. Merge the entries or rule one of them.")


def test_the_duplicate_population_is_not_empty(g):
    """ANTI-VACUITY. With 0 or 1 live decisions the test above asserts nothing,
    and it would pass loudest the day the generator stopped emitting any."""
    items = g.task_items() + g.study_items()
    decs, _m, _o = g.decisions(items)
    assert len(decs) >= 2, (
        "fewer than 2 decisions exist, so the duplicate test is vacuous")


def test_the_overlap_measure_separates_a_real_duplicate_from_a_shared_digit(g):
    """The discriminator itself, exercised on the 2 constructed cases from
    2026-10-19 rather than trusted. Without this, a threshold that flagged
    everything or nothing would still pass the test above."""
    real_a = _figures("1 of 68 rounds, 1.4706%, interval 0.2601% to 7.8710%. "
                      "47 rounds for 50% power, 109 for 80%.")
    real_b = _figures("The rate to reproduce is 1 of 68 rounds, 1.4706%, "
                      "interval 0.2601% to 7.8710%; 47 rounds for 50% power "
                      "and 109 for 80%, which is 18.8 to 105.4 hours.")
    j_real = len(real_a & real_b) / len(real_a | real_b)
    assert j_real >= 0.55, f"the real duplicate scored only {j_real:.4f}"

    shy_a = _figures("4 of 4 reports withhold exactly 1 non-secret field.")
    shy_b = _figures("1 read of the switch in the entire runner.")
    j_shy = len(shy_a & shy_b) / len(shy_a | shy_b)
    assert j_shy < 0.55, (
        f"a pair sharing only a common digit scored {j_shy:.4f} and would be "
        f"reported to him as a duplicate")


# ── helper ──────────────────────────────────────────────────────────────────

def _detail_with(mapping: dict) -> pathlib.Path:
    import json
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8")
    json.dump(mapping, fh)
    fh.close()
    return pathlib.Path(fh.name)
