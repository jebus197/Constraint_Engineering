# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'capability_ladder_design_blind_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 43fae42094063380b268afb9b4a4a91294307ba55db6ae1c8ff06cf723e9441a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Per-rung attempt recording + the max_rungs=None exhaustion sentinel.

WHY THIS FILE EXISTS (blind round, capability-ladder design, 2026-10-06).

1. DENOMINATOR. A measured ladder statistic needs per-writer attempt counts
   with tool verdicts. RoutingResult previously kept only the LAST rung's
   verdict; scripts/ladder_statistic_demonstration_2026-10-06.py measured 87
   of 87 archived multi-rung routing records with the failed rungs'
   identities unrecoverable. `RoutingResult.attempts` closes that forward;
   these tests are the additive-standard wiring proof that the field is
   populated and consumable.

2. EXHAUSTION. The founder ruled there should be no rung cap: the ladder
   runs until resolved or exhausted. The runner-side coercion
   ``int(getattr(cfg, "routing_max_rungs", 2) or 2)`` turns 0 into 2, so the
   sentinel must be None, and the DEFAULT must stay 2 so every archived path
   is byte-identical until a config opts in.

3. CREDIT. The resolving writer, not the reporter, owns the confirmation --
   asserted here against resolve_via_routing's own return, matching the
   repaired scripts/competence_provenance.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from routing import resolve_via_routing  # noqa: E402


def _resolver(good_model):
    return lambda model, f: "GOOD" if model == good_model else "BROKEN"


def _reverifier():
    return lambda code: "CONFIRMED" if code == "GOOD" else "ERROR"


def test_attempts_record_every_rung_with_its_verdict():
    r = resolve_via_routing({"id": "C1"}, ["CC2", "Codex", "ChatGPT"],
                            _resolver("ChatGPT"), _reverifier(), max_rungs=None)
    assert r.attempts == [("CC2", "ERROR"), ("Codex", "ERROR"),
                          ("ChatGPT", "CONFIRMED")]
    assert r.rungs_tried == 3 and len(r.attempts) == r.rungs_tried


def test_attempts_record_empty_falsifier_as_error():
    resolve = lambda model, f: ""  # noqa: E731 -- model produced nothing
    reverify = lambda code: "CONFIRMED"  # noqa: E731 -- must never be reached
    r = resolve_via_routing({"id": "C2"}, ["CC2"], resolve, reverify, max_rungs=None)
    assert r.attempts == [("CC2", "ERROR")] and not r.resolved


def test_max_rungs_none_exhausts_the_whole_ladder():
    calls = []
    resolve = lambda model, f: calls.append(model) or "BAD"  # noqa: E731
    reverify = lambda code: "ERROR"  # noqa: E731
    r = resolve_via_routing({"id": "C3"}, ["A", "B", "C", "D", "E"],
                            resolve, reverify, max_rungs=None)
    assert calls == ["A", "B", "C", "D", "E"]  # no cap: every rung tried once
    assert not r.resolved and r.rungs_tried == 5
    assert [a[0] for a in r.attempts] == calls  # bounded by the roster, recorded


def test_default_cap_is_unchanged_at_two():
    calls = []
    resolve = lambda model, f: calls.append(model) or "BAD"  # noqa: E731
    reverify = lambda code: "ERROR"  # noqa: E731
    resolve_via_routing({"id": "C4"}, ["A", "B", "C"], resolve, reverify)
    assert calls == ["A", "B"]  # byte-identical default behaviour


def test_confirmation_is_credited_to_the_writer_not_the_reporter():
    r = resolve_via_routing({"id": "C5", "source_model": "DeepSeek"},
                            ["CC2", "Codex"], _resolver("Codex"),
                            _reverifier(), max_rungs=None)
    assert r.resolved and r.model_used == "Codex"
    # the reporter appears nowhere in the attempts: it never wrote this falsifier
    assert all(m != "DeepSeek" for m, _ in r.attempts)


def test_runner_wiring_maps_null_and_zero_to_exhaustion_sentinel():
    """The config surface can now express the founder's no-cap ruling.

    Mirrors test_routing_max_rungs_is_reachable_2026-09-24.py's approach:
    assert on the live wiring expression, not a re-implementation. None and 0
    both map to the None sentinel (exhaust); 2 stays the inert default; any
    other int passes through.
    """
    for raw, expect in ((None, None), (0, None), (2, 2), (5, 5)):
        _rungs = None if raw in (None, 0) else int(raw)
        assert _rungs == expect
    src = (Path(__file__).resolve().parents[1] / "reference_runner_v3.py").read_text()
    assert '_rungs = None if _rungs_raw in (None, 0) else int(_rungs_raw)' in src
    assert 'int(getattr(cfg, "routing_max_rungs", 2) or 2)' not in src
