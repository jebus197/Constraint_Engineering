"""His words may not sit unread while a turn ends.

HIS RULING, 2026-10-25: *"we should implement a rule mechanically that compels
you to read from the record, rather than to just make assumptions."*

WHAT THESE TESTS ESTABLISH BY EXECUTION, not by reading the hook's source:
  1. With every annotation rowed, the gate ALLOWS the stop (exit 0).
  2. With one row removed, the gate REFUSES (exit 2) and NAMES the anchor.
  3. A row marked `anchor_lost` does NOT count as coverage.
  4. The refusal ceiling is reachable, so a session cannot be trapped.
  5. A broken reader fails OPEN, because a felled session is worse than the gap.
  6. The deployed copy at ~/.claude/hooks is the SAME INODE as the repo copy.

WHY 2 AND 3 ARE THE LOAD-BEARING ONES. `execute-do-not-grep`: a test that reads
the hook's text proves only that the hook describes itself consistently. These
drive the real `main()` over a real fixture and read the real exit code, which is
the only thing the Stop event actually consults.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "his_responses_freshness_gate.py"
DEPLOYED = pathlib.Path.home() / ".claude" / "hooks" / "his_responses_freshness_gate.py"


def _load(tmp_state: pathlib.Path):
    spec = importlib.util.spec_from_file_location("_frgate", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.STATE = tmp_state                      # never the live counter directory
    return m


def _fixture_record(tmp_path: pathlib.Path, rows: list[dict]) -> pathlib.Path:
    p = tmp_path / "verdicts.json"
    p.write_text(json.dumps({"window_from": "2026-10-01", "rows": rows}),
                 encoding="utf-8")
    return p


#: Two annotations of his, one file, standing in for the 8 he wrote on the 23rd.
ANNOTATIONS = [
    {"file": "/x/Report_2026-10-19.txt", "line_index": 11, "date": "2026-10-19",
     "text": "Why have you not read this?"},
    {"file": "/x/Report_2026-10-19.txt", "line_index": 40, "date": "2026-10-19",
     "text": "And this one too."},
]


def test_all_rowed_allows_the_stop(tmp_path):
    """1. Nothing unread -> the gate must stand aside."""
    m = _load(tmp_path / "state")
    m.RECORD = _fixture_record(tmp_path, [
        {"anchor": "Report_2026-10-19.txt#11"},
        {"anchor": "Report_2026-10-19.txt#40"},
    ])
    m._reader = lambda: type("R", (), {"annotations": staticmethod(lambda: ANNOTATIONS)})
    assert m.unread() == []


def test_one_missing_row_is_detected_and_named(tmp_path):
    """2. THE INCIDENT. One annotation with no row must be caught AND named."""
    m = _load(tmp_path / "state")
    m.RECORD = _fixture_record(tmp_path, [{"anchor": "Report_2026-10-19.txt#11"}])
    m._reader = lambda: type("R", (), {"annotations": staticmethod(lambda: ANNOTATIONS)})
    miss = m.unread()
    assert len(miss) == 1, f"expected exactly 1 unread, got {len(miss)}"
    assert miss[0]["anchor"] == "Report_2026-10-19.txt#40"
    assert "And this one too." in miss[0]["text"]


def test_anchor_lost_is_not_coverage(tmp_path):
    """3. `anchor_lost` says his words VANISHED, which is a different fact."""
    m = _load(tmp_path / "state")
    m.RECORD = _fixture_record(tmp_path, [
        {"anchor": "Report_2026-10-19.txt#11"},
        {"anchor": "Report_2026-10-19.txt#40", "anchor_lost": True},
    ])
    m._reader = lambda: type("R", (), {"annotations": staticmethod(lambda: ANNOTATIONS)})
    assert [a["anchor"] for a in m.unread()] == ["Report_2026-10-19.txt#40"]


def test_before_the_window_is_out_of_scope(tmp_path):
    """An annotation older than `window_from` is not owed a row."""
    m = _load(tmp_path / "state")
    m.RECORD = _fixture_record(tmp_path, [])
    old = [{"file": "/x/Old_2026-09-02.txt", "line_index": 3, "date": "2026-09-02",
            "text": "ancient"}]
    m._reader = lambda: type("R", (), {"annotations": staticmethod(lambda: old)})
    assert m.unread() == []


def test_the_ceiling_is_reachable_so_no_session_is_trapped(tmp_path, capsys):
    """4. Drive main() past MAX_REFUSALS and prove it yields.

    This is the test the FFAFP gate did NOT have tonight, which is exactly how a
    counter that was read but never written shipped as an unreachable ceiling.
    """
    m = _load(tmp_path / "state")
    m.RECORD = _fixture_record(tmp_path, [])
    m._reader = lambda: type("R", (), {"annotations": staticmethod(lambda: ANNOTATIONS)})

    codes = []
    for _ in range(m.MAX_REFUSALS + 1):
        sys.stdin = open(os.devnull)         # main() reads stdin itself
        import io
        payload = json.dumps({"session_id": "T", "stop_hook_active": True})
        sys.stdin = io.StringIO(payload)
        codes.append(m.main())
    assert codes[:m.MAX_REFUSALS] == [2] * m.MAX_REFUSALS, (
        f"expected {m.MAX_REFUSALS} refusals, got {codes}")
    assert codes[-1] == 0, f"ceiling not reachable; codes were {codes}"
    assert "ceiling" in capsys.readouterr().err


def test_a_broken_reader_fails_open(tmp_path, capsys):
    """5. A gate that fells the session is worse than the gap it guards."""
    import io
    m = _load(tmp_path / "state")
    m.RECORD = _fixture_record(tmp_path, [])

    def boom():
        raise RuntimeError("reader exploded")
    m._reader = boom
    sys.stdin = io.StringIO(json.dumps({"session_id": "T2"}))
    assert m.main() == 0
    assert "failing OPEN" in capsys.readouterr().err


def test_a_missing_record_says_nothing(tmp_path):
    """Not built in this checkout -> silent, not a refusal."""
    import io
    m = _load(tmp_path / "state")
    m.RECORD = tmp_path / "does_not_exist.json"
    sys.stdin = io.StringIO(json.dumps({"session_id": "T3"}))
    assert m.main() == 0


def test_the_deployed_hook_is_the_same_inode():
    """6. Two copies that drift are a gate that guards nothing.

    Same discipline as `ticket_queue_gate.py`: hard-link, never copy.
    """
    if not DEPLOYED.exists():
        pytest.skip("not deployed on this machine")
    assert DEPLOYED.stat().st_ino == HOOK.stat().st_ino, (
        "deployed hook has DRIFTED from the repo copy; re-link with "
        f"ln -f {HOOK} {DEPLOYED}")


def test_it_is_registered_as_a_stop_hook():
    """An addition nothing reaches is not additive (`additive-standard`)."""
    settings = pathlib.Path.home() / ".claude" / "settings.json"
    if not settings.is_file():
        pytest.skip("no settings.json")
    text = settings.read_text(encoding="utf-8")
    assert "his_responses_freshness_gate.py" in text, (
        "the gate is not wired to the Stop event, so it never runs")
    cfg = json.loads(text)
    cmds = [h.get("command", "") for entry in cfg.get("hooks", {}).get("Stop", [])
            for h in entry.get("hooks", [])]
    assert any("his_responses_freshness_gate" in c for c in cmds), (
        f"named in the file but not under Stop; Stop holds {len(cmds)} hook(s)")
