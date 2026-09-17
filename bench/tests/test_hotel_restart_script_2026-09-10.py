"""Task 10.1: the script he can run from the hotel to get this session back.

HIS RULING, verbatim: "We will build a script I can place on my remote desktop
here in my hotel, which when I run it will restart you/the Claude desktop app and
if necessary/technically possible restart this specific session, so I can begin
working with it immediately."

WHY IT IS NEEDED. The desktop application force-restarts to apply a pending
update the moment the session goes IDLE. Measured twice: 2026-09-04 23:10:45
after 76 hours, and 2026-09-08 16:52:11 after 85 hours, with 48 consecutive
deferrals each logged in the app's own words as "Claude is working". It waits for
the first quiet moment, which is exactly when a remote user is least able to
notice, and the session does not reconnect by itself. Until now the only remedy
on record was to be physically at the machine.

"THIS SPECIFIC SESSION" IS ANSWERED, NOT APPROXIMATED. `claude --resume <id>`
restores this conversation by its own identifier, with `--continue` as the
fallback if the id has aged out.

NEVER RUN AGAINST A REAL HOST, DELIBERATELY. Running it for real restarts the
application, which would kill the session writing it. Since 2026-09-17 both the
dry run and the full restart-and-resume path are EXECUTED against a recording
`ssh` stub (`TestTheDryRunIsObservedOffline`), which proves what the script SENDS
and nothing about what the Mac does with it. The real restart-and-resume path
remains unexecuted end to end.

ONE DEFECT WAS FOUND BY RUNNING IT AND WOULD NOT HAVE BEEN FOUND BY READING IT.
`BatchMode=yes` is correct -- it stops the script hanging on a password prompt a
remote user cannot see -- but it also makes the FIRST connection to a host fail
outright rather than offering the usual "continue connecting?" question. On the
hotel machine, first run, it would simply have failed. It now detects that exact
case and prints the single command that fixes it.
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO_COPY = ROOT / "scripts" / "restart_claude_from_hotel.sh"
DESKTOP = pathlib.Path.home() / "Desktop" / "restart_claude_from_hotel.sh"


@pytest.fixture(scope="module")
def src():
    assert REPO_COPY.is_file(), "the versioned copy is missing"
    return REPO_COPY.read_text(encoding="utf-8")


class TestItIsSafeToRun:
    def test_it_parses(self):
        r = subprocess.run(["bash", "-n", str(REPO_COPY)], capture_output=True,
                           text=True)
        assert r.returncode == 0, r.stderr

    def test_it_deletes_nothing(self, src):
        """It runs on his machine over SSH. It must not be able to destroy."""
        for bad in ("rm -rf", "git push", "git branch -D", "git reset --hard",
                    "shutdown", "diskutil", "> /dev/"):
            assert bad not in src, f"the script contains {bad!r}"

    def test_an_unknown_flag_is_refused(self):
        r = subprocess.run([str(REPO_COPY), "--this-flag-does-not-exist"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode != 0, (
            "an unrecognised argument exits 0, which is the "
            "reads-as-success defect this project spent 118 days on")
        assert "unknown option" in r.stderr

    def test_help_needs_no_network(self):
        r = subprocess.run([str(REPO_COPY), "--help"], capture_output=True,
                           text=True, timeout=120)
        assert r.returncode == 0
        assert "--dry-run" in r.stdout


class TestItDoesWhatHeAsked:
    def test_it_restarts_the_application(self, src):
        # The former first disjunct entailed the second, so it could never decide.
        assert "quit app" in src
        assert "open -a Claude" in src

    def test_it_resumes_THIS_session_by_id(self, src):
        assert "--resume" in src, "it cannot restore a specific session"
        assert re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-", src), (
            "no session identifier is carried, so --resume has nothing to resume")
        assert "--continue" in src, (
            "no fallback: if the id has aged out he is left with nothing")

    def test_the_session_id_is_overridable(self, src):
        """A hardcoded id is useless the moment the session changes."""
        for var in ("CLAUDE_SESSION_ID", "CLAUDE_MAC_HOST", "CLAUDE_PROJECT_DIR"):
            assert var in src, f"{var} cannot be overridden"

    def test_it_reaches_the_mac_over_the_tailnet(self, src):
        # The former `or "CLAUDE_MAC_HOST" in src` is already asserted by the test
        # above, so it made this one pass whenever that one did.
        assert "tail8b628c.ts.net" in src


class TestItFailsHelpfully:
    def test_it_handles_the_first_connection_case(self, src):
        assert "host key verification failed" in src.lower(), (
            "the first run from a new machine would fail with no explanation")
        assert "exit 3" in src, "the first-run case shares an exit code with a "\
                                "real outage, so he cannot tell them apart"

    def test_every_failure_path_says_nothing_was_changed(self, src):
        assert src.count("NOTHING WAS CHANGED") >= 2, (
            "a failure that does not say whether it changed anything leaves him "
            "guessing from a hotel")

    def test_dry_run_and_check_exist(self, src):
        assert "--dry-run" in src and "--check" in src


class TestTheDryRunIsObservedOffline:
    """The dry run is executed to completion against a recording `ssh` stub.

    REPLACES `test_a_dry_run_changes_nothing_here` (2026-09-17, task 10.1
    correction). That test ran the script against the live tailnet and accepted
    exit 0, 1 or 3. Where the host did not resolve it exited 1 at the reachability
    probe, before the dry-run branch, and still passed; a copy with both `DRY`
    checks disarmed passed it too. On a machine that DID reach the host, that
    disarmed copy would have issued a real quit. The replacement dominates on
    that named property: it detects disarmed `DRY` checks in every environment,
    and it never touches a network.

    THE STUB. `ssh` and `tailscale` are shadowed first on PATH. `ssh` appends its
    argv to a log and answers the reachability probe with `ok`; it reaches no host.
    `CLAUDE_MAC_HOST` is set to a `.invalid` name as well, so even a bypassed stub
    fails at the probe, before anything is restarted.
    """

    SSH_STUB = (
        "#!/bin/bash\n"
        "printf '%s\\n' \"$*\" >> \"$SSH_STUB_LOG\"\n"
        "if [ \"${@: -1}\" = \"echo ok\" ]; then echo ok; fi\n"
        "exit 0\n")

    def _run(self, tmp_path, *args):
        bindir = tmp_path / "bin"
        bindir.mkdir(exist_ok=True)
        for name, body in (("ssh", self.SSH_STUB), ("tailscale", "#!/bin/bash\nexit 0\n")):
            p = bindir / name
            p.write_text(body, encoding="utf-8")
            p.chmod(0o755)
        log = tmp_path / "ssh_calls.log"
        env = dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}",
                   CLAUDE_MAC_HOST="nobody@stub.invalid", SSH_STUB_LOG=str(log))
        r = subprocess.run(["bash", str(REPO_COPY), *args], capture_output=True,
                           text=True, timeout=120, env=env)
        calls = log.read_text(encoding="utf-8").splitlines() if log.is_file() else []
        assert any("nobody@stub.invalid" in c and c.endswith("echo ok") for c in calls), (
            "the stub never saw the reachability probe, so this run did not go "
            f"through it: rc={r.returncode} stderr={r.stderr[-300:]}")
        return r, calls

    def test_a_dry_run_completes_and_sends_no_restart_or_resume(self, tmp_path):
        r, calls = self._run(tmp_path, "--dry-run")
        assert r.returncode == 0, (r.returncode, r.stdout[-400:], r.stderr[-300:])
        assert "DRY RUN COMPLETE" in r.stdout, r.stdout[-400:]
        for forbidden in ("osascript", "open -a Claude", "claude --resume"):
            sent = [c for c in calls if forbidden in c]
            assert not sent, f"a dry run sent {forbidden!r} over ssh: {sent}"

    def test_the_stub_does_observe_a_real_restart_attempt(self, tmp_path):
        """CONTROL. Without --dry-run the same stub must record both commands,
        or the test above would pass for a stub that sees nothing."""
        r, calls = self._run(tmp_path)
        assert any("osascript" in c and "open -a Claude" in c for c in calls), calls
        assert any("claude --resume" in c for c in calls), calls
        assert "DRY RUN COMPLETE" not in r.stdout


class TestTheDesktopCopyMatches:
    def test_it_is_byte_identical_where_present(self, src):
        if not DESKTOP.is_file():
            pytest.skip("no Desktop copy on this machine")
        assert DESKTOP.read_text(encoding="utf-8") == src, (
            "the copy he actually runs has drifted from the versioned one; the "
            "repository copy is canonical by founder ruling of 2026-08-06")


class TestEveryFailurePathSaysNothingWasChanged:
    """Entry 10.1 claimed a universal that one path did not satisfy.

    It read *"every failure path says NOTHING WAS CHANGED"*. The unknown-flag
    path (`exit 2`) did not say it -- found by the adversarial audit of the list's
    DONE entries on 2026-09-11, and confirmed by reading the script rather than
    taking the finding on trust.

    THE UNIVERSAL WAS MADE TRUE RATHER THAN NARROWED, because at that point
    nothing has run, so the reassurance is accurate and is the one a reader most
    needs after a typo on hotel wifi. It is deliberately NOT added after the
    restart step, where it would be false.
    """

    def test_every_nonzero_exit_is_preceded_by_the_reassurance(self):
        import re
        src = REPO_COPY.read_text(encoding="utf-8")
        lines = src.splitlines()
        missing = []
        for i, ln in enumerate(lines):
            m = re.search(r"\bexit ([1-9])\b", ln)
            if not m:
                continue
            # COMMENTS STRIPPED. The first version scanned the raw window, and
            # the explanatory COMMENT above `exit 2` contains the phrase -- so
            # deleting the real `echo` left this test green. A guard reading its
            # own documentation as evidence of the thing documented is the defect
            # this session found repeatedly; it survived a mutation here before
            # being caught.
            window = "\n".join(
                ln.split("#", 1)[0] for ln in lines[max(0, i - 8):i + 1])
            if "NOTHING WAS CHANGED" not in window:
                missing.append(f"line {i + 1}: exit {m.group(1)}")
        assert not missing, (
            f"these failure exits do not say NOTHING WAS CHANGED: {missing}. "
            f"Entry 10.1 states that as a universal, so either the path says it "
            f"or the entry stops claiming it.")

    def test_the_reassurance_is_not_claimed_after_the_restart(self):
        """ANTI-VACUITY, and the reason the universal is safe to state at all.
        After the restart step something MAY have changed, so the same string
        there would be a lie. A version that printed it everywhere would satisfy
        the test above and be worse than the defect it fixes."""
        src = REPO_COPY.read_text(encoding="utf-8")
        after = src.split("open -a Claude", 1)
        if len(after) > 1:
            assert "NOTHING WAS CHANGED" not in after[1], (
                "the script claims nothing was changed AFTER restarting the "
                "application, which is false")

    def test_a_bad_flag_actually_exits_two_and_says_it(self):
        """EXECUTED, not read. The path is safe to run: it exits before anything
        happens, which is the whole reason the message is true there."""
        import subprocess
        r = subprocess.run(["bash", str(REPO_COPY), "--not-a-flag"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 2, (r.returncode, r.stderr[-300:])
        assert "NOTHING WAS CHANGED" in r.stderr, r.stderr[-300:]
