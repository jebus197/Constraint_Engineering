"""No LIVE claude-CLI spawn may inherit the operator's own instructions.

FOUNDER RULING 2026-08-31: "remove personal directives like this and any
disability directives from the directive set fed to the models... do it."

A `claude -p` subagent loads ~/.claude/CLAUDE.md AND the project .claude/CLAUDE.md
before it sees its brief, and `--system-prompt` does NOT displace them -- verified
by execution. Measured on the simulated panel, which uses the same CLI: 66,533 of
93,442 briefing characters, 71.2%, was inherited config -- 2.5x more than the
CDSFL directive the panellist is meant to apply.

The consequence was not theoretical. Two panellists declined to review at all,
citing the operator's personal working-hours directive; a third objected using a
naming rule superseded 23 days earlier. And `call_claude_cli` is how CC2 and
Fable reach a PAID experiment, so a paid panellist has been reading the
operator's private instructions in every real run to date.

SCOPE, stated rather than implied: this pins the LIVE dispatch paths. Four
standalone scripts (two exp39 confer one-offs, two smoke tests) are imported by
nothing and are deliberately not covered -- adding them would be churn, and their
absence here is a recorded boundary, not an oversight.
"""
import pathlib
import sys

import pytest

BENCH = pathlib.Path(__file__).resolve().parents[1]

#: Every module that can spawn the CLI on a live experiment or panel path.
LIVE_SPAWN_SITES = {
    "experiment_11_orchestrator.py": "call_claude_cli — CC2 and Fable in PAID runs",
    "cc2_manager.py": "reached from ouroboros_cell",
    "tools/sim_dispatch_shim.py": "the simulation seam",
    "tools/sim_panel_agents.py": "simulated panellists",
}


@pytest.mark.parametrize("rel", sorted(LIVE_SPAWN_SITES), ids=sorted(LIVE_SPAWN_SITES))
def test_live_spawn_suppresses_inherited_config(rel):
    src = (BENCH / rel).read_text(encoding="utf-8")
    assert "--setting-sources" in src, (
        f"{rel} spawns the claude CLI without --setting-sources, so the "
        f"panellist inherits the operator's personal directives. "
        f"({LIVE_SPAWN_SITES[rel]})"
    )


@pytest.mark.parametrize("rel", sorted(LIVE_SPAWN_SITES), ids=sorted(LIVE_SPAWN_SITES))
def test_no_live_spawn_uses_bare(rel):
    """`--bare` also suppresses config, but forces API-key auth and would break
    subscription dispatch. Both reviewers rejected it for that reason."""
    src = (BENCH / rel).read_text(encoding="utf-8")
    assert '"--bare"' not in src and "'--bare'" not in src


def test_the_paid_path_is_covered():
    """The single most important one: the route CC2 and Fable take in a real run."""
    src = (BENCH / "experiment_11_orchestrator.py").read_text(encoding="utf-8")
    i = src.index("def call_claude_cli")
    j = src.index("\ndef ", i + 10)
    assert "--setting-sources" in src[i:j], (
        "call_claude_cli no longer suppresses inherited config — a PAID "
        "panellist would read the operator's private instructions again"
    )
