"""Task 6.6, panel round 16: the attribution record, attached and dated by execution.

2 GAPS IN `test_target_rewrites_carry_an_author_2026-09-10.py`.

1. ATTACHMENT WAS A SUBSTRING. `test_the_record_is_attached_to_the_integrity_event`
   asserted `'"attribution": _attrib' in src`, inside a class whose docstring said
   "AST, not grep". With `_attrib = target_attribution(_tgt_p) and {}` substituted,
   the event carries `{}` and that file still gave 9 passed. This file selects the
   real `if _prev_h:` branch from `bench/reference_runner_v3.py` by AST, compiles
   it alone, executes it with 2 seat threads registered, and checks the event it
   appends. The same checks must fail on the `and {}` copy.

2. "A STALE REGISTRATION IS VISIBLE AS STALE" WAS FALSE. `seat_done` had no
   production caller and a registration had no completion marker, so after a
   5-seat pool and then a 2-seat pool had both shut down, `seats_in_flight()`
   returned 5 records with none marked finished (the 2-seat pool's threads had
   overwritten 2 of them by reused ident). Wiring `seat_done` in a `finally` would
   have emptied the record instead, because the integrity check runs after the
   round's pool has joined. The runner now records completion without deleting:
   `_records_seat_completion` sets `until` in a `finally` around the real
   `_dispatch_single_model`, registrations are keyed by (thread, label, since), and
   `could_have_written` excludes a seat whose window lies wholly before or after
   the file's mtime. This file drives the REAL dispatcher through 2 shrinking pools
   and requires every record to carry `until`; with `seat_finished` disabled it
   must fail.
"""
from __future__ import annotations

import ast
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

import reference_runner_v3 as rr  # noqa: E402

RUNNER = ROOT / "bench" / "reference_runner_v3.py"
TARGET = ROOT / "bench" / "dm" / "_memory.py"


@pytest.fixture(autouse=True)
def _clean_registry():
    with rr._SEATS_LOCK:
        rr._SEATS_IN_FLIGHT.clear()
    yield
    with rr._SEATS_LOCK:
        rr._SEATS_IN_FLIGHT.clear()


def integrity_branch(src: str) -> ast.If:
    """The `if _prev_h:` whose body takes the attribution record."""
    hits = [n for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.If) and ast.unparse(n.test) == "_prev_h"
            and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                    and c.func.id == "target_attribution" for c in ast.walk(n))]
    assert len(hits) == 1, f"expected 1 integrity branch, found {len(hits)}"
    return hits[0]


def check_attachment(src: str) -> None:
    """Execute the branch with 2 registered seats. Raises AssertionError."""
    node = integrity_branch(src)
    code = compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                   str(RUNNER), "exec")
    release = threading.Event()
    ready = threading.Barrier(3)

    def seat(label):
        rr.seat_in_flight(label)
        ready.wait(timeout=5)
        release.wait(timeout=5)

    threads = [threading.Thread(target=seat, args=(label,)) for label in ("CC2", "Gemini")]
    for t in threads:
        t.start()
    try:
        ready.wait(timeout=5)
        ns = {"_prev_h": "a" * 40, "_tgt_h": "b" * 40, "_tgt_p": TARGET,
              "result": {}, "round_idx": 3,
              "cfg": SimpleNamespace(test_article="bench/dm/_memory.py"),
              "_log": lambda *a, **k: None,
              "target_attribution": rr.target_attribution}
        exec(code, ns)
    finally:
        release.set()
        for t in threads:
            t.join(timeout=5)
    events = ns["result"].get("target_integrity_events")
    assert isinstance(events, list) and len(events) == 1, events
    ev = events[0]
    assert (ev["round"], ev["from"], ev["to"]) == (3, "a" * 40, "b" * 40), ev
    att = ev.get("attribution") or {}
    labels = sorted(s["label"] for s in att.get("seats_in_flight", []))
    assert labels == ["CC2", "Gemini"], f"the event names {labels}"
    f = att.get("file") or {}
    assert f.get("uid") == os.getuid() and str(f.get("mode", "")).startswith("0o") \
        and "mtime" in f, f


class TestTheRecordIsAttached:
    def test_the_real_branch_attaches_a_record_naming_the_seats(self):
        check_attachment(RUNNER.read_text(encoding="utf-8"))

    def test_a_discarded_record_fails_the_same_checks(self):
        src = RUNNER.read_text(encoding="utf-8")
        old = "_attrib = target_attribution(_tgt_p)\n"
        assert src.count(old) == 1
        with pytest.raises(AssertionError):
            check_attachment(src.replace(old, "_attrib = target_attribution(_tgt_p) and {}\n"))


def _slow_compose(*a, **k):
    """Keeps each real dispatch open long enough to have a measurable window."""
    time.sleep(0.05)
    raise ValueError("composer stubbed for the attribution test")


def _dispatch(label, tmp):
    mc = rr.ModelConfig(label=label, model_id="none", api="__no_such_route__",
                        role="player", system_prompt_path="")
    try:
        return rr._dispatch_single_model(mc, None, "p", "", "", 0, "pat", "dom", tmp)
    except Exception as exc:        # unroutable api: expected, and free
        return type(exc).__name__


def shrinking_pools(tmp_path):
    """5 real dispatches on a 5-thread pool, then 2 on a 2-thread pool, both joined."""
    first = ["SIM-A", "SIM-B", "SIM-C", "SIM-D", "SIM-E"]
    second = ["SIM-A", "SIM-B"]
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda label: _dispatch(label, tmp_path), first))
    time.sleep(0.05)
    boundary = time.time()
    time.sleep(0.05)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda label: _dispatch(label, tmp_path), second))
    return first, second, boundary


def check_completion(tmp_path) -> None:
    first, second, boundary = shrinking_pools(tmp_path)
    recs = rr.seats_in_flight()
    assert sorted(r["label"] for r in recs) == sorted(first + second), (
        f"expected 7 registrations, 1 per dispatch; got {[r['label'] for r in recs]}")
    for r in recs:
        assert r["finished"] is True and r["until"] is not None, (
            f"{r['label']} finished dispatching but its record does not say so: {r}")
        assert r["until"] >= r["since"]
    before = [r for r in recs if r["until"] < boundary]
    after = [r for r in recs if r["since"] > boundary]
    assert len(before) == 5 and len(after) == 2, (len(before), len(after))


class TestCompletionIsRecordedNotDeleted:
    def test_every_record_carries_until_after_2_shrinking_pools(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rr, "_compose_for_model", _slow_compose)
        check_completion(tmp_path)

    def test_without_seat_finished_the_same_checks_fail(self, tmp_path, monkeypatch):
        """Control: a dispatcher that never sets `until`."""
        monkeypatch.setattr(rr, "_compose_for_model", _slow_compose)
        monkeypatch.setattr(rr, "seat_finished", lambda label: None)
        with pytest.raises(AssertionError, match="does not say so"):
            check_completion(tmp_path)

    def test_the_window_excludes_seats_that_could_not_have_written(
            self, tmp_path, monkeypatch):
        monkeypatch.setattr(rr, "_compose_for_model", _slow_compose)
        first, second, boundary = shrinking_pools(tmp_path)
        recs = rr.seats_in_flight()
        late = [r for r in recs if r["since"] > boundary]
        assert len(late) == 2
        # A write between the 2 pools: every seat's window lies wholly before
        # or wholly after it.
        assert [r for r in recs if rr.could_have_written(r, boundary)] == []
        # A write while the 2 late seats were both still open.
        m = max(r["since"] for r in late) + 0.001
        assert m < min(r["until"] for r in late), "the 2 late windows do not overlap"
        assert sorted(r["label"] for r in recs if rr.could_have_written(r, m)) \
            == sorted(second)

    def test_target_attribution_carries_the_narrowed_candidates(
            self, tmp_path, monkeypatch):
        """The helper is wired: the record lists who could have written the file."""
        monkeypatch.setattr(rr, "_compose_for_model", _slow_compose)
        first, second, boundary = shrinking_pools(tmp_path)
        late = [r for r in rr.seats_in_flight() if r["since"] > boundary]
        m = round(max(r["since"] for r in late) + 0.001, 3)
        f = tmp_path / "rewritten.py"
        f.write_text("x = 1\n", encoding="utf-8")
        os.utime(f, (m, m))
        rec = rr.target_attribution(f)
        assert len(rec["seats_in_flight"]) == 7, "the superset must be kept whole"
        assert sorted(rec["seats_whose_window_contains_mtime"]) == sorted(second)
        f2 = tmp_path / "before.py"
        f2.write_text("x = 1\n", encoding="utf-8")
        os.utime(f2, (round(boundary, 3), round(boundary, 3)))
        assert rr.target_attribution(f2)["seats_whose_window_contains_mtime"] == []

    def test_an_open_registration_is_kept_for_a_later_mtime(self):
        rec = {"label": "CC2", "since": 100.0, "until": None}
        assert rr.could_have_written(rec, 150.0) is True
        assert rr.could_have_written(rec, 99.0) is False
        assert rr.could_have_written({"since": 100.0, "until": 120.0}, 121.0) is False
        assert rr.could_have_written({"since": 100.0, "until": 120.0}, 120.0) is True
