"""A model seat must not inherit the launching Claude Code session's identity.

WHY THIS EXISTS, AND IT IS THE REASON A SIMULATED RUN BEHAVES DIFFERENTLY DEPENDING
ON WHERE IT WAS LAUNCHED FROM.

`seat_environment` stripped SECRET-named variables only. Measured 2026-09-29 inside
a Claude Code desktop session: 29 parent markers were present and **28 reached every
seat**. The one that did not was `CLAUDE_CODE_MESSAGING_TOKEN`, removed only because
it happens to match `/TOKEN/`. What a seat was therefore handed is incoherent BY
CONSTRUCTION:

    CLAUDE_CODE_SESSION_ID, CLAUDE_CODE_CHILD_SESSION   "you are a child session"
    CLAUDE_CODE_SDK_HAS_HOST_AUTH_REFRESH=1             "your HOST refreshes your auth"
    CLAUDE_CODE_MESSAGING_SOCKET                        "...over this socket"
    CLAUDE_CODE_MESSAGING_TOKEN                         stripped -- so it cannot
    ANTHROPIC_BASE_URL=https://api.anthropic.com        and route to the METERED API

A seat is told to get its auth from a host it has been denied the token to reach,
while pointed at the metered endpoint instead of the subscription the founder pays
for. The founder saw "unable to authenticate" alerts naming nothing.

WHY IT ONLY BITES LONG RUNS, which is why this went unnoticed. A dispatch that
finishes before a token refresh is due never exercises the broken path: measured
2026-09-29, 5 concurrent PING dispatches succeeded 5 of 5 both with and without
these markers. The simulated shakedown's seats run about 725 s (observed mean,
n=7, numpy and statistics agreeing exactly) and every one of them crosses that
boundary. Every previously successful simulated run was launched from a terminal,
where none of these variables exist.

THE RULE THIS RESTORES. `seat_environment`'s own docstring already says a seat
authenticates "to the Max plan through the keychain" and that ANTHROPIC_API_KEY
"must never reach it". That intent covered the key and not the route or the
identity. This extends it to both. A seat is an independent process and must
authenticate independently.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from bench.experiment_11_orchestrator import (  # noqa: E402
    seat_environment, _PARENT_SESSION_NAME, _SECRET_NAME,
)

#: Every marker observed in a real Claude Code desktop session, 2026-09-29.
#: Listed explicitly rather than derived, so the test still means something on a
#: machine where the launching process is a plain terminal and none of them exist.
OBSERVED_PARENT_MARKERS = (
    "CLAUDECODE",
    "CLAUDE_AGENT_SDK_VERSION",
    "CLAUDE_CODE_ACCOUNT_UUID",
    "CLAUDE_CODE_CHILD_SESSION",
    "CLAUDE_CODE_DESKTOP_APP_VERSION",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_CODE_EXECPATH",
    "CLAUDE_CODE_HOST_SESSION_ID",
    "CLAUDE_CODE_MESSAGING_SOCKET",
    "CLAUDE_CODE_MESSAGING_TOKEN",
    "CLAUDE_CODE_OAUTH_SCOPES",
    "CLAUDE_CODE_ORGANIZATION_UUID",
    "CLAUDE_CODE_SDK_HAS_HOST_AUTH_REFRESH",
    "CLAUDE_CODE_SESSION_ATTENDED",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_EFFORT",
    "CLAUDE_PID",
    "CLAUDE_PREVIEW_CLASSIFIER_FLOOR",
    "ANTHROPIC_BASE_URL",
    "MCP_CONNECTION_NONBLOCKING",
    "MCP_SERVER_CONNECTION_BATCH_SIZE",
)

#: A seat genuinely needs these. Stripping them would break the dispatch outright,
#: which is the failure mode opposite to the one above and just as real.
MUST_SURVIVE = ("PATH", "HOME", "TMPDIR", "USER", "LANG", "SHELL")


@pytest.fixture
def synthetic_parent():
    """A parent environment carrying every observed marker, built not sampled.

    The bug is only VISIBLE when the launcher is a Claude Code session. Building
    the environment here means this test fails on the defect wherever it runs,
    rather than passing vacuously on a terminal-launched machine.
    """
    base = {m: "x" for m in OBSERVED_PARENT_MARKERS}
    base.update({"PATH": "/usr/bin:/bin", "HOME": "/tmp/h", "TMPDIR": "/tmp",
                 "USER": "u", "LANG": "en_GB.UTF-8", "SHELL": "/bin/zsh",
                 "ANTHROPIC_API_KEY": "sk-should-never-survive",
                 "HARMLESS_PROJECT_VAR": "keep-me"})
    return base


class TestTheParentSessionDoesNotReachASeat:

    def test_no_observed_marker_survives(self, synthetic_parent):
        env = seat_environment(synthetic_parent, seat="cc2")
        leaked = [m for m in OBSERVED_PARENT_MARKERS if m in env]
        assert leaked == [], (
            f"{len(leaked)} parent-session marker(s) reach the seat: {leaked}. "
            "A seat inheriting its launcher's session identity is told to refresh "
            "auth from a host it cannot reach.")

    def test_the_three_that_make_it_incoherent_are_gone(self, synthetic_parent):
        """Named individually because together they are the actual defect."""
        env = seat_environment(synthetic_parent, seat="cc2")
        for k in ("CLAUDE_CODE_SDK_HAS_HOST_AUTH_REFRESH",
                  "CLAUDE_CODE_MESSAGING_SOCKET",
                  "CLAUDE_CODE_SESSION_ID"):
            assert k not in env, k

    def test_the_seat_is_not_pointed_at_the_metered_api(self, synthetic_parent):
        """The founder pays for a subscription; a seat must use it, not the API."""
        env = seat_environment(synthetic_parent, seat="cc2")
        assert "ANTHROPIC_BASE_URL" not in env
        assert "ANTHROPIC_API_KEY" not in env

    def test_the_parents_mcp_configuration_does_not_follow(self, synthetic_parent):
        env = seat_environment(synthetic_parent, seat="cc2")
        assert [k for k in env if k.startswith("MCP_")] == []


class TestItStripsNothingASeatNeeds:
    """The opposite failure: an over-broad strip breaks every dispatch."""

    def test_the_essentials_survive(self, synthetic_parent):
        env = seat_environment(synthetic_parent, seat="cc2")
        for k in MUST_SURVIVE:
            assert k in env, f"{k} was stripped; a seat cannot run without it"

    def test_unrelated_variables_survive(self, synthetic_parent):
        env = seat_environment(synthetic_parent, seat="cc2")
        assert env.get("HARMLESS_PROJECT_VAR") == "keep-me"

    def test_the_seat_label_is_still_set(self, synthetic_parent):
        env = seat_environment(synthetic_parent, seat="cc2")
        assert env.get("CDSFL_SEAT") == "cc2"

    def test_keep_still_overrides_for_routes_that_need_a_key(self, synthetic_parent):
        """Codex falls back to OPENAI_API_KEY; `keep` must still win."""
        synthetic_parent["OPENAI_API_KEY"] = "sk-codex"
        env = seat_environment(synthetic_parent, keep=("OPENAI_API_KEY",), seat="codex")
        assert env.get("OPENAI_API_KEY") == "sk-codex"
        assert "ANTHROPIC_API_KEY" not in env


class TestThePatternIsNeitherVacuousNorGreedy:

    def test_it_matches_what_it_must(self):
        for k in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_PID",
                  "ANTHROPIC_BASE_URL", "MCP_CONNECTION_NONBLOCKING"):
            assert _PARENT_SESSION_NAME.match(k), k

    def test_it_does_not_match_what_it_must_not(self):
        for k in ("PATH", "HOME", "CDSFL_SEAT", "CDSFL_WOLFRAM_POLICY",
                  "OPENAI_API_KEY", "MY_CLAUDE_NOTES", "ANTHROPIC_MODEL_NOTES"):
            assert not _PARENT_SESSION_NAME.match(k), k

    def test_the_secret_rule_still_stands_on_its_own(self):
        """The new pattern must not have quietly replaced the old guarantee."""
        assert _SECRET_NAME.search("ANTHROPIC_API_KEY")
        assert _SECRET_NAME.search("GITHUB_TOKEN")
        assert not _PARENT_SESSION_NAME.match("GITHUB_TOKEN")


class TestTheLiveEnvironmentIsClean:
    """Executed against the REAL launching process, whatever it is."""

    def test_no_marker_from_this_process_reaches_a_seat(self):
        env = seat_environment(seat="cc2")
        leaked = [k for k in os.environ
                  if _PARENT_SESSION_NAME.match(k) and k in env]
        assert leaked == [], leaked
