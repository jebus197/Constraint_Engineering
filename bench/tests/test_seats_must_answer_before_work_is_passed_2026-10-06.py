#!/usr/bin/env python3
"""A seat is asked to print Ready! before it is handed a brief.

THE FOUNDER'S ASK, 2026-10-06: *"perhaps we should build a simple 'aliveness test',
where the models get up to 3 attempts, by simply asking it to print 'Ready!'"*

MEASURED THE SAME NIGHT, which is the case for it. The cc2 seat was dispatched on a
1236-word brief at 03:41 and returned `ok: False` with a response of 0 words after
2423.7 seconds across 2 dispatcher attempts, because the network dropped mid-round.
The expense was not the failure; it was discovering the failure at the END of a
40-minute dispatch. The probe is 1 line of prompt and a 16-token ceiling.

THE 2 PROPERTIES THAT ARE EASY TO GET WRONG, and both are held here:

  * **"Non-empty" is not "alive".** A route returning an error string, a usage notice
    or a holding note is answering, but not answering THIS question. The project has
    already been bitten by a reply accepted on the sole condition of being non-empty
    (a 54-character holding note). `test_a_wrong_but_non_empty_reply_is_not_alive`.
  * **A dead seat REFUSES THE ROUND; it is never dropped.** `feedback_no_benching` is
    standing: models are never rested, skipped or benched. A probe that pruned the
    roster would be an automated benching mechanism.
    `test_the_refusal_does_not_reduce_the_roster`.

Every behavioural assertion CALLS the probe with an injected caller, so the guard runs
with no network and touches no credential. The 3 structural tests parse source, because
"does a caller exist, and does it run before the expensive step" is a structural claim
and the only kind source-reading can settle.
"""
import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PANEL = REPO / "bench" / "confer_maths_panel_2026-09-05.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "sa_under_test", REPO / "bench" / "seat_aliveness_2026-10-06.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["sa_under_test"] = m          # dataclasses need this registered
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def AL():
    return _load()


def _counter(replies):
    """A caller that returns each reply in turn, raising if asked once too often."""
    seq = list(replies)
    calls = {"n": 0}

    def _call():
        calls["n"] += 1
        if not seq:
            raise AssertionError("the probe called more times than attempts allow")
        v = seq.pop(0)
        if isinstance(v, Exception):
            raise v
        return v
    return _call, calls


class TestALiveSeatAnswers:
    def test_a_ready_reply_is_alive_on_the_first_attempt(self, AL):
        r = AL.probe_seat("s", lambda: "Ready!")
        assert r.alive is True and r.attempts_used == 1

    def test_the_token_is_matched_case_insensitively(self, AL):
        assert AL.probe_seat("s", lambda: "ready").alive is True
        assert AL.probe_seat("s", lambda: "READY!").alive is True

    def test_a_ready_inside_a_longer_reply_still_counts(self, AL):
        r = AL.probe_seat("s", lambda: "Sure thing. Ready!")
        assert r.alive is True

    def test_a_seat_recovering_on_the_third_attempt_is_alive(self, AL):
        """The founder's '3 attempts' exists for exactly the transient case."""
        call, counter = _counter(["", "", "Ready!"])
        r = AL.probe_seat("s", call, attempts=3)
        assert r.alive is True and r.attempts_used == 3
        assert counter["n"] == 3


class TestADeadSeatDoesNot:
    def test_an_empty_reply_is_not_alive(self, AL):
        r = AL.probe_seat("s", lambda: "", attempts=3)
        assert r.alive is False and r.attempts_used == 3

    def test_a_raising_route_is_not_alive_and_names_the_exception(self, AL):
        def boom():
            raise ConnectionError("network is down")
        r = AL.probe_seat("s", boom, attempts=2)
        assert r.alive is False
        assert any("ConnectionError" in x for x in r.replies), (
            f"the operator is not told why the route is dead: {r.replies}")

    def test_a_wrong_but_non_empty_reply_is_not_alive(self, AL):
        """THE KEY TEST. 'Non-empty' has already fooled this project once."""
        for bad in ("[HTTP Error 401]", "Usage limit reached.",
                    "Suite still running, will report back shortly."):
            r = AL.probe_seat("s", lambda b=bad: b, attempts=1)
            assert r.alive is False, (
                f"{bad!r} was accepted as an aliveness answer; the criterion has "
                f"collapsed back to 'the route returned something'")

    def test_attempts_are_bounded(self, AL):
        call, counter = _counter(["", "", "", ""])
        AL.probe_seat("s", call, attempts=3)
        assert counter["n"] == 3, (
            f"the probe made {counter['n']} calls for a 3-attempt budget")


class TestTheRefusal:
    def test_all_alive_is_no_refusal(self, AL):
        res = {"a": AL.probe_seat("a", lambda: "Ready!")}
        assert AL.refusal_for(res) is None

    def test_every_dead_seat_is_named(self, AL):
        res = {"a": AL.probe_seat("a", lambda: "Ready!"),
               "b": AL.probe_seat("b", lambda: "", attempts=1),
               "c": AL.probe_seat("c", lambda: "", attempts=1)}
        msg = AL.refusal_for(res)
        assert msg and "b" in msg and "c" in msg
        assert "2 of 3" in msg

    def test_the_refusal_does_not_reduce_the_roster(self, AL):
        """A probe that pruned the roster would be an automated benching
        mechanism, which `feedback_no_benching` forbids."""
        res = {"a": AL.probe_seat("a", lambda: "Ready!"),
               "b": AL.probe_seat("b", lambda: "", attempts=1)}
        msg = AL.refusal_for(res)
        assert "never benched" in msg or "NOT reduced" in msg
        assert len(res) == 2, "the probe mutated the roster it was handed"


class TestTheDispatcherRunsIt:
    def test_the_panel_calls_the_probe(self):
        tree = ast.parse(PANEL.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and (getattr(n.func, "id", None)
                      or getattr(n.func, "attr", None))
                 == "_refuse_if_a_seat_is_not_alive"]
        assert calls, (
            "confer_maths_panel never calls the aliveness probe, so it is a module "
            "nothing reaches")

    def test_the_probe_runs_BEFORE_the_sandboxes_are_built(self):
        """ORDERING IS THE WHOLE SAVING. Sandbox build is 6.53 s and 606 MB per
        seat. A probe placed after it saves none of that, and the point of the
        probe is to spend nothing before establishing the route works."""
        src = PANEL.read_text(encoding="utf-8")
        tree = ast.parse(src)
        probe_line = min(
            n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
            and (getattr(n.func, "id", None) or getattr(n.func, "attr", None))
            == "_refuse_if_a_seat_is_not_alive")
        build_lines = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
                       and getattr(n.func, "attr", None) == "build"
                       and getattr(getattr(n.func, "value", None), "id", "")
                       == "panel_sandbox"]
        in_main = [ln for ln in build_lines if ln > probe_line - 400]
        assert in_main, "no panel_sandbox.build call found to order against"
        assert probe_line < max(in_main), (
            f"the aliveness probe at line {probe_line} runs AFTER the sandbox "
            f"build at {max(in_main)}, so it saves none of the per-seat cost")

    def test_a_probe_that_cannot_load_refuses(self):
        """Same trap as the POST one level up: swallowing a load error and going on."""
        src = PANEL.read_text(encoding="utf-8")
        i = src.index("def _refuse_if_a_seat_is_not_alive")
        body = src[i:i + 2400]
        assert "could not be loaded" in body and "return 2" in body, (
            "a probe that fails to load does not refuse, so a broken probe passes")


class TestTheProbeIsCheap:
    def test_the_prompt_is_one_short_line(self, AL):
        assert "\n" not in AL.PROBE_PROMPT
        assert len(AL.PROBE_PROMPT) < 80, (
            f"the probe prompt is {len(AL.PROBE_PROMPT)} characters; its cheapness "
            f"is the reason it exists")

    def test_the_caller_builder_caps_output_tokens(self):
        src = PANEL.read_text(encoding="utf-8")
        i = src.index("def _probe_caller")
        body = src[i:i + 1400]
        assert "max_tokens=16" in body, (
            "the probe does not cap its output, so a confused seat could return a "
            "full essay to a 1-word question")
