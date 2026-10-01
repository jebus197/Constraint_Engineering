"""The session's `grep` hides most matching files, and the measurement can lie.

FOUND 2026-09-28. `grep` in this session is a SHELL FUNCTION from Claude Code's
own shell snapshot, wrapping ugrep with `--ignore-files`. It honours `.gitignore`,
and `.gitignore` ignores `bench/logs/**` (353 MB, 5,840 files), so it skips the
project's entire evidence archive SILENTLY. Measured across 8 patterns: 3743 of
5245 matching files are never shown, 71.3632%, Wilson 95% [70.1245%, 72.5706%].

WHY IT IS LOAD-BEARING. A search that cannot see the archive reports "0
occurrences" for a term occurring thousands of times, and "0 occurrences" is
exactly the shape this project treats as a finding.

WHAT THIS FILE GUARDS IS THE MEASUREMENT'S HONESTY, NOT THE RATE. The rate moves
with the repository and pinning it would make this test a tripwire on ordinary
growth. What must not move is the script's refusal to report a reassuring 0%, and
that guard exists because THE FIRST ATTEMPT AT THIS MEASUREMENT DID EXACTLY THAT:
it ran through `zsh -ic`, a shell that never sources the snapshot, compared
/usr/bin/grep with itself, and returned 0 of 541 missed. A lie in the reassuring
direction is the worst kind here, because nothing prompts a second look.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "shell_grep_blind_spot_2026-09-28.py"


@pytest.fixture(scope="module")
def mod():
    assert SCRIPT.is_file(), f"missing {SCRIPT}"
    spec = importlib.util.spec_from_file_location("grep_blind_spot", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["grep_blind_spot"] = m
    spec.loader.exec_module(m)
    return m


def _backend_state() -> str:
    """Can the grep wrapper reach the backend it shells out to? "reachable" or not.

    THE THIRD PRECONDITION, AND THE ONE THAT ACTUALLY BIT. Measured 2026-10-01.
    The wrapper is NOT self-contained. Its own body reads:

        local _cc_bin="${CLAUDE_CODE_EXECPATH:-}"
        [[ -x $_cc_bin ]] || _cc_bin=$HOME/.local/bin/claude
        if [[ ! -x $_cc_bin ]]; then command grep "$@"; return; fi

    So `grep` resolving to a shell function is NOT sufficient for the divergence
    to exist: the backend it execs as `ugrep` must be executable, or the wrapper
    SILENTLY becomes plain grep and the 2 counts are identical by construction.

    WHY THIS TEST FLIPPED ON 2 CONSECUTIVE DAYS, AND IT WAS NEVER SUITE CONTEXT.
    `CLAUDE_CODE_EXECPATH` is exported into the agent's environment and is NOT
    set in the operator's login shell, where `$HOME/.local/bin/claude` does not
    exist either. Measured in both: agent shell, the variable set and executable,
    911 against 1159; login shell, UNSET with the fallback absent, 1159 against
    1159 and `assert 1159 < 1159`. Every targeted re-run was launched by the
    agent and passed; both full-suite runs were launched from the terminal and
    failed. The variable is WHICH SHELL STARTED PYTEST.

    Reproduced directly rather than inferred: pointing CLAUDE_CODE_EXECPATH at a
    missing path turns 911 against 1159 into 1159 against 1159, which is the
    suite's exact failure. The wrapper hides 248 of 1159 files when it works,
    21.3978%, Wilson [19.1332%, 23.8513%] on statsmodels and mpmath agreeing to
    2.8e-17.

    A WRONG HYPOTHESIS WAS TRIED FIRST AND IS RECORDED SO IT IS NOT RETRIED. It
    gated on whether any git-ignored file carried the pattern, reasoning that the
    suite creates and deletes ignored files for 55 minutes. That gate measured
    910 ignored matches, so it never fired, the test failed again, and the
    failure message refuted the hypothesis outright: 1159 against 1159 WITH 910
    ignored matches present is a wrapper doing nothing, not a population with
    nothing to hide.
    """
    try:
        r = subprocess.run(
            ["zsh", "-c",
             'b="${CLAUDE_CODE_EXECPATH:-}"; [[ -x $b ]] || b="$HOME/.local/bin/claude"; '
             '[[ -x $b ]] && echo reachable || echo unreachable'],
            capture_output=True, text=True, timeout=60)
        return r.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _wrapper_state() -> str:
    """How `grep` resolves in the newest shell snapshot: independent of any count.

    Returns "function" when a wrapper is defined, "binary" when it resolves to a
    file, "no-snapshot" when there is nothing to source. Kept separate from
    `counts()` so wrapper presence is never inferred from the inequality under
    test -- which is exactly the circularity that made the strict divergence test
    report a clean environment as a failure on 2026-09-29.
    """
    try:
        r = subprocess.run(
            ["zsh", "-c", "ls -t ~/.claude/shell-snapshots/ 2>/dev/null | head -1"],
            capture_output=True, text=True, timeout=60)
        if not r.stdout.strip():
            return "no-snapshot"
        r = subprocess.run(
            ["zsh", "-c", "source ~/.claude/shell-snapshots/"
             "$(ls -t ~/.claude/shell-snapshots/ | head -1) 2>/dev/null; type grep"],
            capture_output=True, text=True, timeout=60)
    except Exception:                                         # noqa: BLE001
        return "no-snapshot"
    return "function" if "shell function" in r.stdout else "binary"


class TestTheVacuityGuard:
    """A measurement whose control and treatment are the same thing measures
    nothing, and must say so instead of printing a small number."""

    def test_equality_on_every_pattern_is_vacuous(self, mod):
        assert mod.is_vacuous([("a", 5, 5), ("b", 9, 9), ("c", 0, 0)]) is True

    def test_one_genuine_difference_is_not_vacuous(self, mod):
        assert mod.is_vacuous([("a", 5, 9), ("b", 9, 9)]) is False

    def test_all_probes_failing_is_vacuous_not_clean(self, mod):
        """A failed probe is not a measurement of 0 difference."""
        assert mod.is_vacuous([("a", -1, -1), ("b", -1, -1)]) is True

    def test_no_matches_anywhere_is_vacuous(self, mod):
        """If nothing matched, the patterns are wrong and nothing was measured."""
        assert mod.is_vacuous([("a", 0, 0)]) is True


class TestTheDivergenceIsReal:
    """EXECUTED against the real shell, not asserted from the docstring.

    Uses 1 cheap pattern rather than the script's 8, so the suite does not pay for
    a full sweep. The claim under test is only that the 2 greps DISAGREE, which is
    what makes the blind spot real rather than theoretical.
    """

    def test_the_wrapper_can_only_subtract_never_add(self, mod):
        """THE UNCONDITIONAL INVARIANT, and it is the one worth having.

        The wrapper filters; it cannot conjure matches. So `seen <= real` holds in
        EVERY environment, wrapper or not, and its violation would invalidate
        every figure in this file's header. This runs with no skip, which is what
        the strict form below cannot do.
        """
        seen, real = mod.counts("gamma_critical")
        if seen < 0 or real == 0:
            pytest.skip("probe could not run in this environment")
        assert seen <= real, (
            f"session grep found MORE files ({seen}) than /usr/bin/grep ({real}). "
            "The wrapper filters, so it cannot add matches: either the comparison "
            "is not measuring the 2 things it names, or /usr/bin/grep is being "
            "given a narrower root. Every rate in this file's header is void "
            "until this is explained.")

    def test_the_session_grep_sees_fewer_files_than_usr_bin_grep(self, mod):
        """THE STRICT FORM, now gated on an INDEPENDENT wrapper probe.

        REWRITTEN 2026-09-29, by both seats of the free between-rounds panel and
        confirmed here. It asserted the divergence UNCONDITIONALLY and so inferred
        wrapper presence FROM THE INEQUALITY IT WAS ASSERTING. Measured on
        2026-09-29 under Claude Code 2.1.284: 403 and 403, identical -- and the
        test reported a clean environment as a failure. `counts()` sources whichever
        snapshot is NEWEST, which need not be the one this session loaded and need
        not define `grep` at all, so absence of a wrapper is an ordinary state and
        not a fault.

        THIS IS THE SAME SHAPE `TestAgeControl` WAS REWRITTEN FOR on the day it was
        written, its docstring recording that it "failed *because the age control
        worked*". A test asserting a transient cannot tell a fixed world from a
        broken one.

        DETECTION IS NOT LOST, and that is the point of splitting the assertion in
        two. The invariant above runs unconditionally; the script's own honesty
        guard (it exits 3 and prints VACUOUS rather than a reassuring 0%) is tested
        unconditionally in `TestTheScriptRefusesRatherThanReassures`; and the
        wrapper probe below is independent of the counts. What is skipped is only
        the claim that cannot be true when there is no wrapper to measure.
        """
        if _wrapper_state() != "function":
            pytest.skip(
                f"grep resolves to {_wrapper_state()!r} in the newest snapshot, "
                "so there is no wrapper to diverge from; the blind spot cannot "
                "exist here and its absence is not a defect")
        seen, real = mod.counts("gamma_critical")
        if seen < 0 or real == 0:
            pytest.skip("probe could not run in this environment")
        assert real > 0
        # THE BACKEND MUST BE REACHABLE, PROBED RATHER THAN INFERRED. See
        # `_backend_state`: a wrapper that cannot exec its backend falls back to
        # plain grep, so the counts agree by construction and the blind spot
        # cannot exist here.
        backend = _backend_state()
        if backend != "reachable":
            pytest.skip(
                f"the grep wrapper's ignore-aware backend is {backend!r} in "
                "this environment -- CLAUDE_CODE_EXECPATH unset and the "
                "fallback path absent -- so the wrapper degrades to plain grep "
                "and there is no divergence to measure. Its absence is not a "
                "defect, and it depends on WHICH SHELL started pytest")
        assert seen < real, (
            f"the wrapper's backend is reachable, so it must filter. "
            f"a grep WRAPPER is loaded yet session grep found {seen} files and "
            f"/usr/bin/grep found {real}. Either the wrapper has stopped honouring "
            "ignore files -- measured as its behaviour under Claude Code 2.1.284, "
            "in which case this file's 71.3632% is stale and must be re-taken -- "
            "or `counts()` is no longer reaching the wrapper it thinks it is.")

    def test_the_wrapper_is_a_shell_function_not_a_binary(self):
        """The mechanism, checked directly: `grep` must not resolve to a file."""
        r = subprocess.run(
            ["zsh", "-c", "source ~/.claude/shell-snapshots/"
             "$(ls -t ~/.claude/shell-snapshots/ | head -1) 2>/dev/null; type grep"],
            capture_output=True, text=True)
        if "shell function" not in r.stdout:
            pytest.skip(f"no grep wrapper in this environment: {r.stdout.strip()[:80]}")
        assert "shell function" in r.stdout

    def test_usr_bin_grep_exists_so_the_remedy_is_available(self):
        assert Path("/usr/bin/grep").is_file(), (
            "the stated remedy (/usr/bin/grep) does not exist on this machine"
        )


class TestTheScriptRefusesRatherThanReassures:
    def test_main_returns_3_when_the_measurement_is_vacuous(self, mod, monkeypatch, capsys):
        """The whole point: exit non-zero, and say so on stderr."""
        monkeypatch.setattr(mod, "PATTERNS", ["zzz_pattern"])
        monkeypatch.setattr(mod, "counts", lambda p: (7, 7))
        rc = mod.main()
        err = capsys.readouterr().err
        assert rc == 3, f"expected refusal, got {rc}"
        assert "VACUOUS" in err
        assert "measured nothing" in err

    def test_main_reports_a_rate_when_the_measurement_is_real(self, mod, monkeypatch, capsys):
        """ANTI-VACUITY FOR THIS FILE. A guard that refuses everything is not a
        guard, so the honest path must still produce its number."""
        monkeypatch.setattr(mod, "PATTERNS", ["zzz_pattern"])
        monkeypatch.setattr(mod, "counts", lambda p: (25, 100))
        rc = mod.main()
        out = capsys.readouterr().out
        assert rc == 0
        assert "75.0000%" in out, out
        assert "Wilson" in out
