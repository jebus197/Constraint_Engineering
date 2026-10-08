"""No test may disable a money guard for the tests that run after it.

FOUND 2026-10-08, by a batch run rather than by reading. Two fixtures written that
day did `os.environ.setdefault("PANEL_BRIEF_UNCHECKED", "1")` to get the panel
dispatcher imported. `setdefault` never restores, so the variable survived into
every later test in the same process -- and that variable makes the dispatcher SKIP
brief validation.

WHAT IT DISABLED. `test_panel_brief_format_2026-09-09.py::
test_the_dispatcher_REFUSES_a_bad_brief_before_paying_a_seat` exists to stop money
being spent on a defective brief. It PASSED in isolation and FAILED in the batch,
which is the signature of leaked state and is invisible to anyone running a single
file. A third instance, at module level in
`test_a_retry_never_erases_the_attempt_it_replaces_2026-10-06.py`, predated that day
and had the same effect.

AND THE FLAG WAS NEVER NEEDED. A22 moved the brief binding out of import time, so
the dispatcher imports cleanly with the variable absent -- verified by importing it
in an environment with the name unset. A leftover flag that disables a money guard
to solve a problem that no longer exists is exactly what the additive standard's
symmetric half is for.

THIS FILE IS STRUCTURAL, NOT A REMINDER. It scans the test suite for the pattern,
so the next person to reach for the flag is refused by a test rather than by a
memory. The permitted forms are `monkeypatch.setenv` (restored automatically) and
passing it to a SUBPROCESS's own environment, which cannot leak into this process.
"""
from __future__ import annotations

import re
from pathlib import Path

TESTS = Path(__file__).resolve().parent

#: Variables that switch OFF a control protecting spend or containment.
MONEY_GUARD_OVERRIDES = (
    "PANEL_BRIEF_UNCHECKED",   # skips brief validation before a paid dispatch
    "PANEL_SKIP_ALIVENESS",    # skips the pre-dispatch liveness probe
    "PANEL_SKIP_TOPOLOGY",     # skips the star-topology and joint-debt checks
)

#: Forms that cannot leak: pytest restores the first, and the second sets the
#: variable only inside a child process's own environment.
SAFE = (
    re.compile(r"monkeypatch\s*\.\s*(setenv|delenv)"),
    re.compile(r"env_extra\s*=|env\s*=\s*\{|\benv\[|subprocess|check_output|Popen"),
)

LEAKY = re.compile(
    r"os\.environ\s*\.\s*setdefault\s*\(|os\.environ\s*\[\s*['\"]"
    r"|os\.putenv\s*\(|os\.environ\s*\.\s*update\s*\(")


def _offending_lines(text: str, var: str):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if var not in line:
            continue
        stripped = line.strip()
        if stripped.startswith("#"):
            continue                      # a comment naming it is documentation
        if not LEAKY.search(line):
            continue
        if any(p.search(line) for p in SAFE):
            continue
        out.append((i, stripped))
    return out


class TestNoFileLeaksAnOverride:
    def test_no_test_sets_a_money_guard_override_without_restoring(self):
        bad = {}
        for p in sorted(TESTS.glob("test_*.py")):
            if p.name == Path(__file__).name:
                continue
            try:
                t = p.read_text(errors="ignore")
            except OSError:
                continue
            for var in MONEY_GUARD_OVERRIDES:
                hits = _offending_lines(t, var)
                if hits:
                    bad.setdefault(p.name, []).extend(
                        [f"{var} at line {n}: {s}" for n, s in hits])
        assert not bad, (
            "these test files set a money-guard override in a way that does NOT "
            f"restore, so it leaks into every later test in the process: {bad}. "
            "Use monkeypatch.setenv, or pass it to a subprocess's own environment. "
            "The dispatcher imports fine without PANEL_BRIEF_UNCHECKED since A22.")


class TestTheDetectorActuallyDetects:
    """A scanner that matches nothing would pass the test above vacuously, which
    is the failure shape this project has paid for repeatedly."""

    def test_it_catches_the_exact_pattern_that_was_removed(self, tmp_path):
        f = tmp_path / "test_leaky_example.py"
        f.write_text('import os\nos.environ.setdefault("PANEL_BRIEF_UNCHECKED", "1")\n')
        assert _offending_lines(f.read_text(), "PANEL_BRIEF_UNCHECKED")

    def test_it_catches_direct_assignment_too(self, tmp_path):
        t = 'import os\nos.environ["PANEL_SKIP_TOPOLOGY"] = "1"\n'
        assert _offending_lines(t, "PANEL_SKIP_TOPOLOGY")

    def test_it_permits_monkeypatch(self):
        t = '    monkeypatch.setenv("PANEL_BRIEF_UNCHECKED", "1")\n'
        assert not _offending_lines(t, "PANEL_BRIEF_UNCHECKED")

    def test_it_permits_a_subprocess_environment(self):
        t = '    run_dispatcher(env_extra={"PANEL_BRIEF_UNCHECKED": "1"})\n'
        assert not _offending_lines(t, "PANEL_BRIEF_UNCHECKED")

    def test_it_permits_a_comment_naming_the_variable(self):
        t = '    # PANEL_BRIEF_UNCHECKED was removed; os.environ.setdefault leaked it\n'
        assert not _offending_lines(t, "PANEL_BRIEF_UNCHECKED")

    def test_the_override_list_is_not_empty(self):
        assert len(MONEY_GUARD_OVERRIDES) >= 3, MONEY_GUARD_OVERRIDES
