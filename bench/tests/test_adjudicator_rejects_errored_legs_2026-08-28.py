"""An ERRORed falsifier leg must never PRODUCE a verdict.

Commissioned, not merely tested: every case feeds `_direction` legs whose right
answer is known, including the known-BAD ones that used to fall through to SAME.
A test that only fed sound legs would have passed against the defective code.

The defect: SAME was the fall-through, so `self=REFUTED other=ERROR` returned
SAME -- reading an equipment failure as evidence that two findings are one
defect. Because MERGED is terminal with no REOPENED exit, wiring the merge path
to that would have deleted findings unrecoverably on the strength of a crash.
"""
import importlib.util, pathlib, sys
import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "_adj", REPO / "scripts" / "adjudicate_by_repair.py")
adj = importlib.util.module_from_spec(_spec)
sys.modules["_adj"] = adj
_spec.loader.exec_module(adj)


def _direction_with(monkeypatch, tmp_path, v_self, v_other):
    """Drive _direction with the two leg values, stubbing out the machinery."""
    target = tmp_path / "t.py"
    target.write_text("ORIG\n", encoding="utf-8")
    monkeypatch.setattr(adj, "_apply_fix_to_source", lambda orig, fix: "PATCHED\n")
    calls = iter((v_self, v_other))
    monkeypatch.setattr(adj, "_verdict", lambda code, state, **kw: next(calls))
    return adj._direction({"proposed_fix": "f", "falsifier_code": "a"},
                          {"falsifier_code": "b"}, target, "ORIG\n", "k")[0]


# --- known-GOOD legs: the verdicts these support must still be returned -------
@pytest.mark.parametrize("v_self,v_other,expected", [
    ("REFUTED",   "REFUTED",   "SAME"),
    ("REFUTED",   "CONFIRMED", "DIFFERENT"),
    ("CONFIRMED", "REFUTED",   "FIX_INEFFECTIVE"),
    ("CONFIRMED", "CONFIRMED", "FIX_INEFFECTIVE"),
    ("CONFIRMED", "ERROR",     "FIX_INEFFECTIVE"),   # holds whatever `other` did
])
def test_sound_legs_still_give_their_verdict(monkeypatch, tmp_path, v_self, v_other, expected):
    assert _direction_with(monkeypatch, tmp_path, v_self, v_other) == expected


# --- known-BAD legs: every one of these used to return a verdict -------------
@pytest.mark.parametrize("v_self,v_other,was", [
    ("ERROR",   "ERROR",       "SAME"),
    ("ERROR",   "REFUTED",     "SAME"),
    ("REFUTED", "ERROR",       "SAME"),
    ("ERROR",   "CONFIRMED",   "DIFFERENT"),
    ("ERROR",   "NO_FALSIFIER", "SAME"),
])
def test_errored_legs_cannot_produce_a_verdict(monkeypatch, tmp_path, v_self, v_other, was):
    got = _direction_with(monkeypatch, tmp_path, v_self, v_other)
    assert got == "INCONCLUSIVE_EQUIPMENT", (
        f"self={v_self} other={v_other} returned {got}; the defective code "
        f"returned {was}, reading an equipment failure as a finding about the pair")


def test_the_archived_run_still_carries_the_defective_verdicts():
    """The recorded data predates the fix, so it must still show the damage.

    If this ever fails, the adjudicator has been re-run and the corrected counts
    in RECOVERY.md are stale -- which is the exact staleness class this file's
    sibling audit exists to catch.
    """
    import json, re, collections
    rows = json.loads((REPO / "experimental_notes" / "data"
                       / "adjudication_by_repair.json").read_text())["rows"]
    bad = collections.Counter()
    for r in rows:
        parts = (r.get("detail") or "").split("|")
        for i, d in enumerate((r.get("forward"), r.get("reverse"))):
            if i >= len(parts):
                continue
            m = re.search(r"self=(\S+)\s+other=(\S+)", parts[i])
            if not m:
                continue
            s, o = m.group(1), m.group(2)
            if d == "SAME" and not (s == "REFUTED" and o == "REFUTED"):
                bad["SAME"] += 1
            if d == "DIFFERENT" and not (s == "REFUTED" and o == "CONFIRMED"):
                bad["DIFFERENT"] += 1
    assert bad["SAME"] == 29 and bad["DIFFERENT"] == 11, (
        f"archived unsound directions moved: {dict(bad)} (expected 29 SAME, 11 DIFFERENT)")
