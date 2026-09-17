"""The overclaim census must DERIVE its round-2 half, not carry it as a constant.

WHAT HAPPENED, 2026-09-17. The census read
`ROUND2_UPHELD = ("3.3", "9.2", "9.3", "9.4", "L2", "P7")` -- 6 ids transcribed
by eye from the round-2 adjudication and never compared against it. That file
marks SEVEN entries non-SUPPORTED; `7.3`, verdict PARTIAL, was dropped in
transcription. The census reported 30 where its own committed evidence says 31,
and the brief that quoted it carried the short figure to a panel.

The cc2 seat in panel round 16 found it. It was confirmed here independently
before being accepted, because a seat's claim is not evidence either.

WHY THESE TESTS MUTATE THE EVIDENCE. Asserting that the source text contains no
tuple would only prove the module describes itself consistently -- exactly the
`execute-do-not-grep` failure the audited entries are being closed for. A
derivation is proved by changing what it derives FROM and requiring the output
to follow.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "done_audit_overclaim_rate_2026-09-17.py"


@pytest.fixture()
def census():
    spec = importlib.util.spec_from_file_location("census", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["census"] = m
    spec.loader.exec_module(m)
    return m


def test_seven_three_is_in_the_round_two_set(census):
    """The id the typed tuple dropped."""
    assert "7.3" in census.round2_upheld(), census.round2_upheld()


def test_the_round_two_set_matches_the_adjudication(census):
    """Every non-SUPPORTED verdict, and nothing else."""
    raw = json.loads(census.ROUND2.read_text(encoding="utf-8"))
    rows = []

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "verdict" in o:
                rows.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(raw)
    expected = {str(r["id"]).strip() for r in rows
                if str(r.get("verdict", "")).strip().upper() not in ("SUPPORTED", "")}
    assert census.round2_upheld() == expected
    assert len(expected) == 7, sorted(expected)


def test_flipping_a_verdict_changes_the_count(census, tmp_path, monkeypatch):
    """THE DERIVATION TEST. Mark 7.3 SUPPORTED and the census must drop to 30.

    A hand-typed constant would not move. This is the control that the old
    implementation could not pass.
    """
    before, _ = census.overclaiming()
    raw = json.loads(census.ROUND2.read_text(encoding="utf-8"))
    blob = json.dumps(raw).replace('{"id": "7.3", "verdict": "PARTIAL"',
                                   '{"id": "7.3", "verdict": "SUPPORTED"')
    edited = tmp_path / "round2.json"
    edited.write_text(blob, encoding="utf-8")
    monkeypatch.setattr(census, "ROUND2", edited)
    after, _ = census.overclaiming()
    assert "7.3" in before, sorted(before)
    assert "7.3" not in after, "the census did not follow its evidence"
    assert len(after) == len(before) - 1


def test_a_phantom_id_in_round_two_cannot_inflate_the_count(census, tmp_path, monkeypatch):
    """The intersection must be SYMMETRIC.

    It used to apply to round 1 only, and round 1 genuinely carried 5 ids that
    are not entries at all -- so the same hazard was live on the other half.
    """
    raw = json.loads(census.ROUND2.read_text(encoding="utf-8"))
    raw.append({"id": "ZZ99", "verdict": "PARTIAL"})
    edited = tmp_path / "round2.json"
    edited.write_text(json.dumps(raw), encoding="utf-8")
    monkeypatch.setattr(census, "ROUND2", edited)
    ids, real = census.overclaiming()
    assert "ZZ99" in census.round2_upheld(), "the fixture did not take"
    assert "ZZ99" not in ids, "a phantom id reached the reported count"
    assert ids <= real


def test_every_reported_id_is_a_real_done_entry(census):
    ids, real = census.overclaiming()
    assert ids <= real
    assert len(ids) == 31, sorted(ids)
