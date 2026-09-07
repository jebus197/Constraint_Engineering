"""The review panel had never run under the CDSFL schema.

MEASURED 2026-09-07. Of the 37 dispatchers that call `call_claude_cli`, **0**
called the registry composer and this one carried a 3,015-character hand-written
system prompt. Meanwhile 28 of them load
`bench/directives/universal/cdsfl_core_formal.md` -- the formal schema itself,
28,183 characters covering constraint classification and precedence, the P-pass
loop, the proportionality gate, the corroboration model, extended P-pass as a
DAG, the survival predicate, epistemic marking, and Sufficiency Assessment and
Convergence Declaration.

A CORRECTION WORTH KEEPING. CC1 first reported "8 of 37 compose the schema,
Wilson [11.4%, 37.2%]" and told the founder so. That was a SUBSTRING match on
"cdsfl_registry"; those files reference it to load a TARGET MODULE, not to
compose directives. The true figure is 0 of 37, Wilson [0.0%, 9.4%]. The lesson
is the project's own: a substring is not a capability, and the fix was to run
the measurement that distinguishes them. See [[feedback_check_the_whole_set]].

WHAT THIS GUARDS, IN BOTH DIRECTIONS. The schema must be present, AND the four
panel-specific rules must survive alongside it. None of them appears in the
formal document (checked: 0 occurrences each), and the one-shot notice is what
stopped a seat returning a holding note instead of a verdict. Dropping any of
them to make room for the schema would be exactly the subtractive change the
additive standard forbids.

EXECUTED, NOT GREPPED. The module is imported and its real `SYSTEM` value
inspected. Asserting on the source text would only prove the file describes
itself consistently -- `execute-do-not-grep`.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DISPATCHER = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
SCHEMA_DOC = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"


def _load_system(tmp_path) -> str:
    """Import the dispatcher and return its real SYSTEM string.

    The module exits at import unless argv names a log directory holding a
    BRIEF.md, so one is staged. `main()` is never called, so nothing dispatches.
    """
    logs = REPO / "bench" / "logs" / "_schema_test_probe"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "BRIEF.md").write_text("# probe\n", encoding="utf-8")
    old_argv = sys.argv[:]
    sys.argv = ["confer_maths_panel", "_schema_test_probe"]
    try:
        spec = importlib.util.spec_from_file_location("_cmp_probe", DISPATCHER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.SYSTEM
    finally:
        sys.argv = old_argv
        (logs / "BRIEF.md").unlink(missing_ok=True)
        logs.rmdir()


@pytest.mark.skipif(not SCHEMA_DOC.is_file(), reason="schema document absent")
def test_the_panel_system_prompt_carries_the_formal_schema(tmp_path):
    system = _load_system(tmp_path)
    assert "CDSFL Core Directives" in system, (
        "the panel is not running under the formal schema. It was hand-written "
        "prose until 2026-09-07; do not let it revert."
    )
    # a section that exists only in the formal document
    assert "Convergence Declaration" in system, (
        "the schema present is not the formal core document, or it has been "
        "truncated: section 10 is missing."
    )
    assert len(system) > 25_000, f"SYSTEM is only {len(system)} chars; the schema alone is 28k"


@pytest.mark.skipif(not SCHEMA_DOC.is_file(), reason="schema document absent")
def test_the_panel_specific_rules_survive_alongside_the_schema(tmp_path):
    """Additive, not substitutive. Each of these is absent from the schema doc."""
    system = _load_system(tmp_path)
    doc = SCHEMA_DOC.read_text(encoding="utf-8")
    required = {
        "NO COMPELLED CONVERGENCE": "seats must return independent verdicts",
        "NEVER disable or remove a feature": "the additive standard reaches every seat",
        "ONE-SHOT DISPATCH": "a seat that waits for a later turn returns a holding note",
        "TOOLS DECIDE, NOT VOTES": "findings are confirmed by tools, never by agreement",
    }
    missing = [k for k in required if k not in system]
    assert not missing, (
        f"panel-specific rules lost when the schema was added: {missing}. "
        f"Each exists for a reason: " + "; ".join(f"{k} -- {v}" for k, v in required.items())
    )
    # and confirm they genuinely are NOT in the schema doc, so this is additive
    for k in required:
        assert k not in doc, (
            f"{k!r} now appears in the schema document too; this test's premise "
            f"has changed and the duplication should be reviewed."
        )
