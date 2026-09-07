"""A seat reached the operator's real ~/.claude/settings.json and nothing fired.

2026-09-07, 15:04:45. A review seat running inside the panel sandbox wrote to
the operator's REAL settings file. `panel_sandbox.canonical_was_touched` did not
fire, and could not have: it digests the repository's tracked files, and $HOME
is not one of them. The write itself was additive and harmless -- it appended a
hook entry -- but that is luck rather than containment, and the next one need
not be.

These are not ordinary files. `settings.json` names HOOKS, which are commands
run on every turn of every session; `hooks/*.py` is their code; `CLAUDE.md` is
the directive set handed to every model. A seat editing them changes the
behaviour of sessions that have nothing to do with the panel.

The response is DETECTION, not prevention, for a reason recorded in
`panel_sandbox`: rewriting HOME to confine the seat would break OAuth exactly as
`--bare` did on 2026-07-29, when a confinement flag switched off the credential
store it depended on. Reachable pointer, detected use -- the position this
project takes everywhere else.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import panel_sandbox  # noqa: E402


def _home(tmp_path):
    h = tmp_path / "home"
    (h / ".claude" / "hooks").mkdir(parents=True)
    (h / ".claude" / "settings.json").write_text('{"hooks": {}}')
    (h / ".claude" / "CLAUDE.md").write_text("directives")
    (h / ".claude" / "hooks" / "a_hook.py").write_text("print(1)")
    return h


def test_an_unchanged_control_plane_reports_nothing(tmp_path):
    h = _home(tmp_path)
    before = panel_sandbox.control_plane_fingerprint(h)
    assert panel_sandbox.control_plane_was_touched(before, h) == {}


def test_a_modified_settings_file_is_caught(tmp_path):
    h = _home(tmp_path)
    before = panel_sandbox.control_plane_fingerprint(h)
    (h / ".claude" / "settings.json").write_text('{"hooks": {"evil": 1}}')
    touched = panel_sandbox.control_plane_was_touched(before, h)
    assert touched.get(".claude/settings.json") == "modified", touched


def test_an_APPENDED_hook_is_caught(tmp_path):
    """The exact shape of the real event: additive, benign-looking, unnoticed."""
    h = _home(tmp_path)
    before = panel_sandbox.control_plane_fingerprint(h)
    p = h / ".claude" / "settings.json"
    p.write_text(p.read_text().replace('"hooks": {}',
                                       '"hooks": {"UserPromptSubmit": ["x.py"]}'))
    assert panel_sandbox.control_plane_was_touched(before, h) == {
        ".claude/settings.json": "modified"
    }


def test_a_NEW_hook_script_is_caught(tmp_path):
    """A created file was invisible to the repo-side check until it learned to
    report CREATED. The same hole must not exist here."""
    h = _home(tmp_path)
    before = panel_sandbox.control_plane_fingerprint(h)
    (h / ".claude" / "hooks" / "planted.py").write_text("import os")
    touched = panel_sandbox.control_plane_was_touched(before, h)
    assert touched.get(".claude/hooks/planted.py") == "CREATED", touched


def test_a_DELETED_hook_is_caught(tmp_path):
    h = _home(tmp_path)
    before = panel_sandbox.control_plane_fingerprint(h)
    (h / ".claude" / "hooks" / "a_hook.py").unlink()
    touched = panel_sandbox.control_plane_was_touched(before, h)
    assert touched.get(".claude/hooks/a_hook.py") == "deleted", touched


def test_a_file_absent_at_both_ends_is_not_reported(tmp_path):
    """settings.local.json does not exist here. Absent-then-absent is not an
    event, and reporting it would make the alarm useless by crying every run."""
    h = _home(tmp_path)
    before = panel_sandbox.control_plane_fingerprint(h)
    assert before[".claude/settings.local.json"] == "ABSENT"
    assert panel_sandbox.control_plane_was_touched(before, h) == {}


def test_a_file_CREATED_where_one_was_absent_is_caught(tmp_path):
    h = _home(tmp_path)
    before = panel_sandbox.control_plane_fingerprint(h)
    (h / ".claude" / "settings.local.json").write_text("{}")
    touched = panel_sandbox.control_plane_was_touched(before, h)
    assert touched.get(".claude/settings.local.json") == "CREATED", touched
