"""The discrimination control's outcome IS persisted on the finding. B83.

WHY THIS GUARD EXISTS, AND IT IS NOT THE GUARD B83 ASKED FOR. B83 recommended
writing the control's outcome onto the registry entry, and he accepted that
recommendation on 2026-11-08. The write was already there: `git log -S` puts
``entry["discrimination"] = rec`` in commit ce08914c of 2026-09-01, 2 months
before the entry. What the entry measured as empty was a field named
``discrimination_control``, which NOTHING HAS EVER WRITTEN -- so the miss was
reported as a finding.

That is the store-key-is-not-an-identifier failure, and it occurred 3 times in
1 day: twice in this session's ticket lookups, where ``task:B102`` returned 0
rows against a store keyed on ``B102``, and once in B83 itself, where it
produced an entry, a recommendation and a request for his ruling on work that
did not need doing.

SO THIS FILE GUARDS THE OTHER DIRECTION: that the field stays written, and that
the wrong name stays absent. The second assertion is the one that stops the
premise being re-raised, because a reader who greps for the entry's field name
will keep finding nothing.

WHAT IS DELIBERATELY NOT ASSERTED. That the control is working well. 22 of 30
entries carry an outcome and every one of the 22 reads
INDETERMINATE_NOT_INTERCEPTED, which is the entry's substantive worry and is
left open rather than quietly settled. Producer:
``scripts/b83s_premise_is_false_the_outcome_is_stored_2026-11-08.py``.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts/b83s_premise_is_false_the_outcome_is_stored_2026-11-08.py"
RUNNER = REPO / "bench/reference_runner_v3.py"


def _producer():
    spec = importlib.util.spec_from_file_location("_cdsfl_b83", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_runner_still_writes_the_field():
    """The write B83 asked for, asserted on the runner's own source.

    A behavioural test would need a full live run, which this file does not
    fabricate. The string is the assignment itself, so a rename breaks this
    test rather than silently removing the persistence.
    """
    src = RUNNER.read_text()
    assert 'entry["discrimination"] = rec' in src, (
        "the runner no longer writes the discrimination record onto the entry; "
        "B83's defect would now be real")


def test_nothing_writes_the_field_name_the_entry_looked_for():
    """The assertion that stops B83 being re-raised.

    If a writer ever starts using ``discrimination_control`` as well, 2 names
    would carry 1 quantity and a reader would get a different answer depending
    on which it asked for -- strictly worse than today.
    """
    hits = []
    for p in sorted((REPO / "bench").rglob("*.py")):
        if "/logs/" in str(p) or "/tests/" in str(p):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if '["discrimination_control"]' in txt or "'discrimination_control'" in txt:
            hits.append(str(p.relative_to(REPO)))
    assert not hits, (
        f"something now writes or reads a `discrimination_control` field: "
        f"{hits}. One quantity under 2 names answers differently depending on "
        f"which name is asked for.")


def test_the_stored_outcome_is_actually_there():
    """EXECUTED against the archived run the entry itself measured."""
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    mod = _producer()
    if not mod.RUN.is_dir():
        pytest.skip(f"{mod.RUN.name} is not in this checkout")
    n, carrying, claimed, tally = mod.survey()
    assert n >= 30, f"the run holds {n} entries; the frame has changed"
    assert carrying >= 22, (
        f"only {carrying} of {n} entries carry a discrimination outcome; it "
        f"was 22 of 30 when B83's premise was withdrawn")
    assert claimed == 0, (
        f"{claimed} entries now carry the field name B83 looked for")
    assert tally, "an outcome tally of nothing means the survey measured nothing"


def test_the_producer_cannot_pass_by_measuring_nothing():
    """ANTI-VACUITY. A survey of an empty registry would satisfy every bound
    above that is phrased as an absence, so the presence side is required too.
    """
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    mod = _producer()
    assert mod.entries(REPO / "bench/logs/a-run-that-does-not-exist") == {}, (
        "the producer returns entries for a path that does not exist")
    if mod.RUN.is_dir():
        assert mod.entries(), "the producer sees no entries in the named run"
