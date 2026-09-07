"""The MC-command hook: obligations arrive in context, mechanically, every time.

WHY A HOOK AND NOT ANOTHER MEMORY NOTE. `mc_commands_nonoptional.md` has said
since 20 April 2026 that MC commands are directives to be executed in full, and
instructed that the rule be marked in every memory and recovery resource. It was
marked, in six places, and recalled correctly whenever asked.

It still failed. Measured from the session transcript on 2026-08-30: `sy` issued
5 times; ONE genuine STEM-tool invocation across 223 tool calls on the night of
2026-08-29/30 (0.45%); the 21 April two-tool cross-verification rule satisfied
ZERO times. A headline given to the founder was falsified the next morning by one
statsmodels call that should have been made at the time.

The failure is not recall. An MC reads as a MODE ("be rigorous") rather than a
required ARTEFACT ("emit a tool call"), and under load the mode is satisfied in
prose while the artefact never appears. This project's own rule covers the case:
falsification must be STRUCTURALLY ENFORCED, not hoped for
(`feedback_falsification_gate.md`). The hook is the structural version.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "mc_commands.py"


def _load():
    spec = importlib.util.spec_from_file_location("_mc_hook", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _fires(msg: str):
    r = subprocess.run([sys.executable, str(HOOK)],
                       input=json.dumps({"prompt": msg}), capture_output=True, text=True)
    return r.stdout.strip(), r.returncode


def test_the_hook_is_versioned_in_the_repo():
    assert HOOK.is_file(), "the hook exists only as a dotfile and is not recoverable"


@pytest.mark.parametrize("msg", [
    "why?\n\nrg, a, f. sy, d, t",                 # the founder's actual message, typo included
    "did it go well?\n\na, d",
    "check\n\nrg, sq, a, sy, sth, p, d, t, e",    # 9 -- the documented example is 8
    "rg, a, sy\n\nthen tell me\nabout x\nand y\nand z",
    "ok\n\nrg a d please",
    "check\n\nRG, A, D",
    "fine\n\ny",
])
def test_it_fires_on_real_command_forms(msg):
    out, rc = _fires(msg)
    assert out, f"missed a real MC directive: {msg!r}"
    assert rc == 0


@pytest.mark.parametrize("msg", [
    "Good morning. Is the work complete?",
    "I saw a dentist and a doctor",
    "Explain option a",
    "run:\n```\nls -la\n```",
    "Please do a full review of the divergence code",
    "So the answer is that we need to test it and then decide",
])
def test_it_does_not_report_COMMANDS_on_ordinary_prose(msg):
    """Superseded in scope 2026-08-30. The hook now ALWAYS emits the standing
    f/sy pair, so "no output" is no longer the right assertion. What must still
    hold is that ordinary prose is not misread as an issued command list."""
    out, rc = _fires(msg)
    assert "MC command(s) ALSO issued" not in out, (
        f"ordinary prose was parsed as a command list: {msg!r}")
    assert rc == 0


def test_sy_demands_an_actual_tool_call_not_a_mood():
    out, _ = _fires("check\n\nsy")
    assert "REQUIRES an actual STEM-tool invocation" in out
    assert "Prose reasoning does NOT satisfy it" in out
    assert "TWO tools" in out, "the 21 Apr cross-verification rule is not surfaced"
    assert "confidence interval" in out, "the interval requirement is not surfaced"


def test_f_surfaces_all_five_ffafp_steps():
    out, _ = _fires("check\n\nf")
    for step in ("FIND", "FOLLOW", "ANALYSE", "FIX", "P-PASS"):
        assert step in out, f"FFAFP step {step} missing from the obligation"


def test_every_issued_command_gets_an_obligation_line():
    """Six issued commands, plus the two standing ones that fire unconditionally.

    `f` and `sy` appear in both sets, and the obligation text is identical, so the
    bullet count is 6 issued + 2 standing = 8 with two duplicated lines. Asserting
    on the SET of obligations rather than a raw count keeps this honest."""
    out, _ = _fires("check\n\nrg, a, f, sy, d, t")
    bullets = [ln.strip()[2:].split(" — ")[0].strip()
               for ln in out.splitlines() if ln.strip().startswith("• ")]
    for cmd in ("RG", "A", "F", "SY", "D", "T"):
        assert cmd in bullets, f"command {cmd} produced no obligation line:\n{out}"
    assert bullets.count("F") == 2 and bullets.count("SY") == 2, (
        "the standing pair should appear in addition to the issued ones")


def test_the_hook_never_blocks_a_prompt():
    """A hook that blocks is far worse than a missed directive."""
    for msg in ("", "rg, a, d", "\x00\x01 garbage", "x" * 20000):
        _, rc = _fires(msg)
        assert rc == 0
    r = subprocess.run([sys.executable, str(HOOK)], input="not json at all",
                       capture_output=True, text=True)
    assert r.returncode == 0


def test_t_is_defined_as_the_artefact_pair():
    """CC1 did not know what `t` meant until 2026-08-30, having been issued it 5
    times. It is the TTS + markdown notes pair."""
    out, _ = _fires("check\n\nt")
    assert "TTS" in out and "experimental_notes" in out


# --------------------------------------------------------------------------- #
# The standing pair — unconditional, per the founder's hard constraint         #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("msg", [
    "Good morning. Is it all done?",
    "I saw a dentist and a doctor",
    "",
    "Please review the divergence code",
])
def test_f_and_sy_fire_on_every_turn_even_with_no_commands(msg):
    """Founder 2026-08-30, verbatim: "you should use 'f' on all your work
    exclusively, and 'sy' on all work that can be computationally checked and
    determined! This is a hard constraint and should never be bypassed!"

    So they are NOT conditional on the letters being typed."""
    out, rc = _fires(msg)
    assert "STANDING HARD CONSTRAINT" in out, f"the standing pair did not fire on {msg!r}"
    assert "FFAFP" in out and "STEM-tool invocation" in out
    assert rc == 0


def test_issued_commands_still_arrive_alongside_the_standing_pair():
    out, _ = _fires("check\n\nrg, a, d")
    assert "STANDING HARD CONSTRAINT" in out
    assert "3 MC command(s) ALSO issued" in out
    assert "rg, a, d" in out


class TestRetiredDuplicatesStayRetired:
    """`ext`, `rc` and `rr` were removed 2026-09-07 as duplicates.

    Founder: *"Some MC commands are dupes. re and rs are fine. Remove the dupes."*
    Each pair had one command doing the work and one widening the surface that has
    to stay synchronised across 5 locations:

      * `ext` -- the project table itself called it a "shorter alias for `re`".
        0 uses measured across the visible transcripts, Wilson [0.00%, 5.35%].
      * `rc` -- the global shorthand called it "equivalent to `rs`".
      * `rr` -- not a plain duplicate but a contradiction: the global line declared
        it superseded by `rs` while 3 separate rules still described it as live,
        and THIS HOOK never recognised it, so typing it produced no obligation.

    The hook is the only one of the 5 locations with runtime effect, and it was
    absent from the sync rule until the same day -- so the rule covered the 4
    places that DESCRIBE the commands and not the one that ACTS on them.
    """

    @pytest.mark.parametrize("cmd", ["ext", "rc", "rr"])
    def test_a_retired_command_is_not_recognised(self, cmd):
        out, rc = _fires(f"do the thing\n\n{cmd}")
        assert rc == 0
        issued = out.split("ALSO issued:")[-1] if "ALSO issued:" in out else ""
        assert cmd not in issued, f"{cmd!r} is recognised again"

    @pytest.mark.parametrize("cmd", ["re", "rs", "t", "a", "d", "sy", "f", "qc"])
    def test_the_survivors_still_fire(self, cmd):
        """Without this the test above passes trivially on a hook that recognises
        nothing at all."""
        out, rc = _fires(f"do the thing\n\n{cmd}")
        assert rc == 0
        assert "ALSO issued:" in out or "STANDING HARD CONSTRAINT" in out, (
            f"{cmd!r} produced no obligation line at all")

    def test_no_documented_location_still_advertises_a_retired_command(self):
        """A command removed from the parser but left in a table is worse than
        leaving it alone: the founder reads it as available and it silently does
        nothing."""
        import pathlib
        repo = pathlib.Path(__file__).resolve().parents[2]
        home = pathlib.Path.home()
        locations = {
            ".claude/CLAUDE.md": repo / ".claude/CLAUDE.md",
            "docs/REPRODUCING.md": repo / "docs/REPRODUCING.md",
            "~/.claude/CLAUDE.md": home / ".claude/CLAUDE.md",
        }
        offenders = []
        for name, path in locations.items():
            if not path.exists():
                continue
            text = path.read_text()
            for cmd in ("ext", "rc", "rr"):
                for marker in (f"| `{cmd}` |", f"`{cmd}`/", f"{cmd} = ",
                               f"explicit `{cmd}` command"):
                    if marker in text:
                        offenders.append(f"{name}: {marker!r}")
        assert not offenders, (
            "retired commands are still advertised: " + ", ".join(offenders))


def test_the_repo_copy_and_the_live_hook_are_the_same_file():
    """THE GAP THAT LET A DUPLICATE-REMOVAL DIVERGE, 2026-09-07.

    There are TWO copies of this hook: `hooks/mc_commands.py` in the repository,
    which the tests above run, and `~/.claude/hooks/mc_commands.py`, which Claude
    Code actually executes on every prompt. They were byte-identical, nothing
    compared them, and editing only the live one left the repository advertising
    commands the parser had stopped recognising -- with a green suite, because the
    suite runs the repo copy.

    The failure is silent in the dangerous direction: the tests pass against a file
    that is not the one doing the work.
    """
    import pathlib
    live = pathlib.Path.home() / ".claude" / "hooks" / "mc_commands.py"
    if not live.exists():
        pytest.skip("no live hook installed on this machine")
    assert HOOK.read_text() == live.read_text(), (
        f"{HOOK} and {live} have diverged. The tests run the repo copy; Claude "
        f"Code runs the live one. Whichever was edited, copy it to the other.")
