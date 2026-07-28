"""Unit tests for the routing (capability-aware falsifier routing) module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from routing import (  # noqa: E402
    rank_falsifier_writers,
    confirmed_duplicate,
    resolve_via_routing,
    route,
)


def test_rank_strongest_first_and_excludes_source():
    avail = ["DeepSeek", "Gemini", "CC2", "ChatGPT", "Codex"]
    ranked = rank_falsifier_writers(avail, exclude=("DeepSeek",))
    # strongest-first by the falsifier-strength order, DeepSeek (the failed source) dropped
    assert ranked == ["Codex", "CC2", "ChatGPT", "Gemini"]


def test_rank_appends_unknown_models_after_known_strong():
    ranked = rank_falsifier_writers(["MysteryModel", "CC2"])
    assert ranked == ["CC2", "MysteryModel"]


def test_confirmed_duplicate_found_above_threshold():
    f = {"id": "C0028", "target": "composer.py:1362"}
    confirmed = [{"id": "C0003", "target": "composer.py:1362"},
                 {"id": "C0099", "target": "engine.py:10"}]
    sim = lambda a, b: 0.95 if a["target"] == b["target"] else 0.1  # noqa: E731
    assert confirmed_duplicate(f, confirmed, sim, threshold=0.85) == "C0003"


def test_confirmed_duplicate_none_below_threshold():
    f = {"id": "C0040", "target": "x"}
    confirmed = [{"id": "C0003", "target": "y"}]
    sim = lambda a, b: 0.2  # noqa: E731
    assert confirmed_duplicate(f, confirmed, sim, threshold=0.85) is None


def test_ladder_confirms_on_first_strong_rung():
    finding = {"id": "C0028"}
    # first rung (CC2) writes a code that the decider CONFIRMS
    resolve = lambda model, f: "GOOD" if model == "CC2" else "BAD"  # noqa: E731
    reverify = lambda code: "CONFIRMED" if code == "GOOD" else "ERROR"  # noqa: E731
    r = resolve_via_routing(finding, ["CC2", "Codex"], resolve, reverify, max_rungs=2)
    assert r.resolved and r.verdict == "CONFIRMED" and r.model_used == "CC2" and r.rungs_tried == 1


def test_ladder_climbs_to_second_rung():
    finding = {"id": "C0063"}  # the string-embedding trap: rung 1 fails, rung 2 resolves
    resolve = lambda model, f: "GOOD" if model == "Codex" else "BROKEN"  # noqa: E731
    reverify = lambda code: "CONFIRMED" if code == "GOOD" else "ERROR"  # noqa: E731
    r = resolve_via_routing(finding, ["CC2", "Codex"], resolve, reverify, max_rungs=2)
    assert r.resolved and r.model_used == "Codex" and r.rungs_tried == 2


def test_ladder_exhausts_then_reports_unresolved_for_hil():
    finding = {"id": "Cxxxx"}  # genuinely hard: no rung confirms -> caller escalates to HIL
    resolve = lambda model, f: "BAD"  # noqa: E731
    reverify = lambda code: "REFUTED"  # noqa: E731
    r = resolve_via_routing(finding, ["CC2", "Codex"], resolve, reverify, max_rungs=2)
    assert not r.resolved and r.rungs_tried == 2 and r.verdict == "REFUTED"


def test_ladder_respects_max_rungs():
    finding = {"id": "C"}
    calls = []
    resolve = lambda model, f: calls.append(model) or "BAD"  # noqa: E731
    reverify = lambda code: "ERROR"  # noqa: E731
    resolve_via_routing(finding, ["CC2", "Codex", "ChatGPT"], resolve, reverify, max_rungs=2)
    assert calls == ["CC2", "Codex"]  # never tried the 3rd rung


def test_route_dedup_short_circuits_before_dispatch():
    finding = {"id": "C0028", "source_model": "DeepSeek", "target": "t"}
    confirmed = [{"id": "C0003", "target": "t"}]
    dispatched = []
    resolve = lambda model, f: dispatched.append(model) or "GOOD"  # noqa: E731
    reverify = lambda code: "CONFIRMED"  # noqa: E731
    sim = lambda a, b: 0.95  # noqa: E731
    r = route(finding, ["CC2", "DeepSeek"], confirmed, resolve, reverify, sim)
    assert r.verdict == "DUPLICATE" and r.duplicate_of == "C0003" and r.resolved
    assert dispatched == []  # no model was dispatched — dedup caught it first


def test_route_excludes_source_then_ladders():
    finding = {"id": "C0040", "source_model": "ChatGPT", "target": "t"}
    confirmed = [{"id": "C0003", "target": "other"}]
    used = []
    resolve = lambda model, f: used.append(model) or ("GOOD" if model == "CC2" else "BAD")  # noqa: E731
    reverify = lambda code: "CONFIRMED" if code == "GOOD" else "ERROR"  # noqa: E731
    sim = lambda a, b: 0.0  # noqa: E731
    r = route(finding, ["CC2", "Codex", "ChatGPT"], confirmed, resolve, reverify, sim)
    assert r.resolved and r.model_used == "CC2"
    assert "ChatGPT" not in used  # the failed source model is never re-asked
