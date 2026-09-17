#!/usr/bin/env python3
"""The Wolfram standard in `.claude/CLAUDE.md`, as code rather than prose.

FOUNDER, 2026-09-17, approving Question 11: *"Any application of Wolfram in any
test, panel review, simulated, or real experiment ... should use the updated
Wolfram standard fully. Ensure this is wired in all cases appropriately."*

Until then the standard existed only as prose. A read-only audit that day found
no file in bench/, scripts/ or hooks/ putting any of it into effect: a seat's
shell had `wolframscript` on PATH, the falsifier sandbox let model-written code
start it (a fake binary of that name was reached), the test suite's network
guard did not list it, and onboarding classed kernel contention as a missing
kernel after 1 call.

WHAT THIS MODULE HOLDS, each part executed by
`bench/tests/test_wolfram_standard_2026-09-17.py`:

  * `classify` -- a failed call is NOT EVIDENCE. The prose rule asks for an
    `Out[` line, which the hosted connector prints and local `wolframscript
    -code` never does, so read literally it rejects every good local result.
    The rule is therefore per route: the connector needs `Out[`; the local
    kernel needs exit 0, output, and none of the failure shapes below.
  * `attribution` -- the attribution Wolfram's terms require wherever a result
    reaches a document.
  * `run_local` -- 1 retry, and only after a result that is not evidence,
    because a transient failure is not a statement about the mathematics.
  * `licence_warning` -- the Engine licence did not auto-renew on 2026-09-11;
    it was activated by hand on 2026-09-15, expires 2026-10-08, and now renews
    itself under a LaunchAgent (`scripts/wolfram_licence_renew_2026-09-17.py`).
  * The POLICY layer, `serial` or `deny`, selected by `CDSFL_WOLFRAM_POLICY`:
    `claude_cli_args` for `claude -p` seats, `gated_path` to put the policy's
    `wolframscript` first on a seat's PATH, `panel_clause` for what a seat is
    told, and `KERNEL_RE` for the falsifier sandbox's spawn check.

THE DEFAULT IS NOW `serial`, ON THE FOUNDER'S RULING OF 2026-09-17, AND THE
RULING REVERSED THE DEFAULT THIS FILE SHIPPED WITH 6 HOURS EARLIER. Verbatim:
*"So fully enable it. But we don't depend just on Wolfram ... Wolfram, although
it should always be used wherever possible, should remain the
secondary/verification source (a second falsifier), where our other relevant
tools should also aways be used and should remain primary in all cases.
Basically the idea is that anyone running the project, should not be required to
install Wolfram to do so"*, and *"Agents are not exempt from using tools. That is
the whole point of this project. Every model and every agent should use tools
wherever possible, including Wolfram ... The only exception is when a tool may be
literally physically unavailable to a model/agent, in which case it should also
fall back exclusively to the Open Source tools it does have access to."*

SO THE 3 PROPERTIES THE ENABLED ROUTE HAS TO CARRY, none of which "remove the
deny gate" would have given:

  1. **Serialised.** The free Engine is effectively single-kernel: 3 concurrent
     `wolframscript` calls measured on 2026-08-02 gave 1 result and 2
     "Connection closed by WolframKernel". Seats run concurrently by design, so
     an unqueued route hands 2 of every 3 seats a failure that looks like a
     mathematical answer. The `serial` gate takes an exclusive lock on 1 file,
     machine-wide, so calls queue instead of colliding.
  2. **Never a dependency.** A missing or busy kernel is not a blocker: the gate
     says so in the seat's own words and the seat carries on with SymPy, z3,
     mpmath, SciPy, statsmodels and NumPy, which stay PRIMARY in every case.
  3. **Loud about failure.** The gate classifies every call it passes through
     and appends the attribution on evidence, or `NOT EVIDENCE` and the reason
     when the call verified nothing, so a failed call cannot be quoted as a
     result. The child's exit code is passed through untouched -- annotated, not
     overridden, because a local kernel exits 0 on `1/0`.

`deny` is retained, not deleted, and is what the test suite runs under: a suite
must not start the licensed kernel, and the project must go on passing on a
machine that has never had Wolfram installed. Select it with
`CDSFL_WOLFRAM_POLICY=deny`.

WHAT NEITHER POLICY CAN DO, said rather than implied. A seat that names the
binary by absolute path steps past both the CLI rule, which matches a command
prefix, and the PATH gate; under `serial` that means an UNQUEUED call rather
than a denied one. The falsifier sandbox's check matches the absolute path too,
but a `claude -p` seat's own Bash tool has no such observer. The layer makes
Wolfram use deliberate and orderly; it does not make it impossible.
"""
from __future__ import annotations

import contextlib as _contextlib
import datetime as _dt
import fcntl as _fcntl
import os
import re
import subprocess
import time as _time
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE_ROOT = HERE / "tools" / "wolfram_gate"
DENY_GATE = GATE_ROOT / "deny"
SERIAL_GATE = GATE_ROOT / "serial"

#: The policies, and the default the founder ruled for on 2026-09-17.
POLICIES = ("serial", "deny")
DEFAULT_POLICY = "serial"
POLICY_ENV = "CDSFL_WOLFRAM_POLICY"

#: The lock every queued call takes. A FIXED ABSOLUTE PATH ON PURPOSE: a seat's
#: HOME and TMPDIR are both rewritten in places (the falsifier sandbox scrubs
#: both), and 2 processes holding locks on 2 different files are not serialised
#: at all. Overridable with `CDSFL_WOLFRAM_LOCK` for tests.
LOCK_PATH = "/tmp/cdsfl_wolfram_kernel.lock"  # noqa: S108 - machine-wide by design
LOCK_ENV = "CDSFL_WOLFRAM_LOCK"
LOCK_WAIT_ENV = "CDSFL_WOLFRAM_LOCK_WAIT"
DEFAULT_LOCK_WAIT = 600.0

#: Where every gated call is recorded, so the route can be measured rather than
#: assumed. Overridable with `CDSFL_WOLFRAM_LOG`.
CALL_LOG_ENV = "CDSFL_WOLFRAM_LOG"
DEFAULT_CALL_LOG = Path.home() / "Library" / "Logs" / "cdsfl_wolfram_calls.log"

#: Exit code when the queue never came free. 75 is EX_TEMPFAIL: try again later.
BUSY_EXIT = 75

#: `$LicenseExpirationDate` as read on 2026-09-15, after the manual activation.
RECORDED_LICENCE_EXPIRY = "2026-10-08"

#: How the hosted connector reports a failure while calling it a success.
FAILURE_PREFIXES = ("[HTTP Error", "[Timeout after", "[Error]")

#: What the local kernel prints when it did not compute, whatever its exit code.
LOCAL_FAILURES = ("not activated", "license-related problem", "licence-related problem",
                  "connection closed by wolframkernel", "could not be determined",
                  "unable to locate", "unable to connect", "kernel not found")

#: A Wolfram message, such as `Syntax::sntxf` or `Power::infy`.
MESSAGE_LINE = re.compile(r"^\s*[A-Za-z$][\w$]*::\w+", re.M)

DENY_MESSAGE = ("[Error] Wolfram is excluded from automated runs (licence constraint, "
                ".claude/CLAUDE.md). NOT EVIDENCE: the claim stays UNVERIFIED.")

#: Why the falsifier sandbox goes on refusing the kernel under EITHER policy,
#: and it is the founder's own rule rather than a preference of this file's.
#:
#: A falsifier is not a model and not an agent; it is a SCORED ARTEFACT, stored
#: and re-run by whoever reproduces the experiment. The founder's ruling of
#: 2026-09-17 says "anyone running the project, should not be required to
#: install Wolfram to do so" -- a falsifier that calls the kernel is exactly
#: that requirement, written into the archive. The model that WROTE it is free
#: to use Wolfram while reasoning, through its own Bash tool and the serial
#: gate; what it hands back has to stand on the open-source tools alone.
#: The second reason is mechanical: falsifiers run in parallel, and 3 concurrent
#: calls measured on 2026-08-02 gave 1 result and 2 disconnections.
SANDBOX_REFUSAL = ("[Error] a falsifier may not start the Wolfram kernel: it is a stored artefact "
                   "that anyone must be able to re-run without Wolfram installed (founder, "
                   "2026-09-17), and falsifiers run in parallel against 1 licensed kernel. Use "
                   "SymPy, z3, mpmath, SciPy, statsmodels or NumPy inside the falsifier; use "
                   "Wolfram in your own reasoning to check the result. NOT EVIDENCE: the claim "
                   "stays UNVERIFIED.")

#: The licensed kernel named in a spawn argument: a bare command, a path ending
#: in it, or the application bundle.
KERNEL_RE = re.compile(
    r"(?:^|[\s/;&|'\"(`])(?:wolframscript|WolframKernel|wolfram)(?=$|[\s;&|'\")`])"
    r"|Wolfram Engine\.app|WolframScript\.app")

#: The failure shapes, written once and quoted by every clause below, so the
#: words a seat is given cannot drift from the rule `classify` applies.
_NOT_EVIDENCE_SENTENCE = (
    "A Wolfram result is evidence only if it computed. It verified NOTHING, and the claim stays "
    "UNVERIFIED, when its text begins " + ", ".join(FAILURE_PREFIXES) + "; when it came from the "
    "hosted connector with no Out[ line; or when it came from the local kernel and exited non-zero, "
    "printed a message of the form Name::tag, or returned $Failed or $Aborted. A local kernel exits "
    "0 on `1/0`, so the exit code alone is not enough. Any Wolfram-derived value you quote carries "
    "an attribution to Wolfram Language or Wolfram|Alpha, as Wolfram's terms require.")

#: What every seat and every dispatched agent is told under `serial`, by
#: construction, in the dispatcher's SYSTEM prompt.
SERIAL_CLAUSE = (
    "TOOLS, AND WOLFRAM AMONG THEM (founder, standing, 2026-09-17). You are not exempt from using "
    "tools: use them wherever they can decide a claim. SymPy, z3, mpmath, SciPy, statsmodels, NumPy "
    "and the rest of the open-source set are PRIMARY and are used in every case. Wolfram is the "
    "SECOND falsifier: where it can check a result you have already obtained, use it as well, via "
    "`wolframscript -code '...'` in Bash. It is never the only source for a claim and never a "
    "dependency. Calls are queued against 1 licensed kernel, so yours may wait, and a call that "
    "cannot run -- Wolfram absent, kernel busy, licence lapsed -- is NOT a blocker: say so in your "
    "reply and carry on with the open-source tools, which is the whole answer on any machine where "
    "Wolfram is not installed. Run 1 Wolfram call at a time and never in the background. "
    + _NOT_EVIDENCE_SENTENCE)

#: What a seat is told under `deny`, which the test suite runs under.
DENY_CLAUSE = (
    "WOLFRAM (founder, standing, 2026-09-17). Do not run `wolframscript`, `WolframKernel` or any "
    "Wolfram service in this dispatch: Wolfram's published terms bar its use inside automated AI "
    "pipelines, and the local Engine is licensed for a single kernel. Cross-check with SymPy, "
    "mpmath, SciPy, statsmodels or z3 instead. A Wolfram result that reaches you from anywhere else "
    "is subject to the same rule. " + _NOT_EVIDENCE_SENTENCE)

#: The default clause, for a reader who wants the words without a policy in hand.
PANEL_CLAUSE = SERIAL_CLAUSE

#: Deny rules for a `claude -p` seat. `--strict-mcp-config` with no
#: `--mcp-config` also removes the hosted Wolfram connector.
CLAUDE_CLI_DENY_ARGS = ("--disallowedTools", "Bash(wolframscript *)", "Bash(WolframKernel *)",
                        "--strict-mcp-config")

#: Under `serial` the seat keeps a deterministic MCP surface but Bash is free to
#: reach the gate; there is no `--disallowedTools` rule for Wolfram.
CLAUDE_CLI_SERIAL_ARGS = ("--strict-mcp-config",)


def policy(env: "dict[str, str] | None" = None) -> str:
    """The policy in force: `CDSFL_WOLFRAM_POLICY`, else the founder's default."""
    got = (env if env is not None else os.environ).get(POLICY_ENV, "").strip().lower()
    if not got:
        return DEFAULT_POLICY
    if got not in POLICIES:
        raise ValueError(f"{POLICY_ENV} must be one of {POLICIES}, not {got!r}")
    return got


def gate_dir(pol: str | None = None) -> Path:
    """The gate directory a seat's PATH is given under `pol`."""
    return SERIAL_GATE if (pol or policy()) == "serial" else DENY_GATE


def claude_cli_args(pol: str | None = None) -> tuple[str, ...]:
    """The `claude -p` arguments that carry the policy to a seat."""
    return CLAUDE_CLI_SERIAL_ARGS if (pol or policy()) == "serial" else CLAUDE_CLI_DENY_ARGS


def panel_clause(pol: str | None = None) -> str:
    """What a seat or a dispatched agent is told about tools under `pol`."""
    return SERIAL_CLAUSE if (pol or policy()) == "serial" else DENY_CLAUSE


def classify(route: str, text: str, returncode: int | None = None) -> tuple[bool, str]:
    """(is_evidence, reason) for 1 Wolfram result. A failed call verified nothing."""
    body = (text or "").strip()
    if not body:
        return False, "no output"
    if body.startswith(FAILURE_PREFIXES):
        return False, f"failure reported as a result: {body[:40]!r}"
    if route == "connector":
        if "Out[" not in body:
            return False, "no Out[ line"
        return True, "an Out[ line"
    if route != "local":
        raise ValueError(f"route must be 'local' or 'connector', not {route!r}")
    if returncode not in (0, None):
        return False, f"exit {returncode}"
    low = body.lower()
    hit = next((f for f in LOCAL_FAILURES if f in low), None)
    if hit:
        return False, f"kernel failure: {hit!r}"
    m = MESSAGE_LINE.search(body)
    if m:
        return False, f"Wolfram message {m.group(0).strip()!r}"
    if body.splitlines()[-1].strip() in ("$Failed", "$Aborted"):
        return False, body.splitlines()[-1].strip()
    if returncode is None:
        return False, "exit code unknown"
    return True, "exit 0 with output and no failure shape"


def attribution(route: str) -> str:
    if route == "local":
        return "Computed with Wolfram Language (local Wolfram Engine, via wolframscript)."
    if route == "connector":
        return "Computed with Wolfram Language or Wolfram|Alpha, via the hosted Wolfram connector."
    raise ValueError(route)


def real_tool(name: str = "wolframscript", path_env: str | None = None) -> str | None:
    """The installed binary called `name`, never a gate in this repository.

    Skipping the gate directories is what stops the gate calling itself: it is
    first on the PATH it inherits, by construction.
    """
    root = os.path.realpath(str(GATE_ROOT))
    for d in (os.environ.get("PATH", "") if path_env is None else path_env).split(os.pathsep):
        if d and not os.path.realpath(d).startswith(root):
            cand = os.path.join(d, name)
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                return cand
    return None


def real_wolframscript(path_env: str | None = None) -> str | None:
    """The installed `wolframscript`, never a gate in this repository."""
    return real_tool("wolframscript", path_env)


def lock_path(env: "dict[str, str] | None" = None) -> str:
    return (env if env is not None else os.environ).get(LOCK_ENV) or LOCK_PATH


@_contextlib.contextmanager
def kernel_lock(wait: float | None = None, env: "dict[str, str] | None" = None):
    """Hold the machine-wide kernel lock, or yield False when the wait ran out.

    Serialisation is the whole reason the enabled route is safe: 3 concurrent
    calls measured on 2026-08-02 gave 1 result and 2 disconnections. A caller
    that cannot get the lock must NOT fall through and call the kernel anyway --
    it reports a busy queue, which is not a blocker, and uses the open-source
    tools instead.
    """
    src = env if env is not None else os.environ
    if wait is None:
        try:
            wait = float(src.get(LOCK_WAIT_ENV, "") or DEFAULT_LOCK_WAIT)
        except ValueError:
            wait = DEFAULT_LOCK_WAIT
    path = lock_path(src)
    fh = None
    try:
        fh = open(path, "a+")  # noqa: SIM115 - held for the duration of the call
    except OSError:
        yield False          # a lock we cannot take is not a licence to collide
        return
    deadline = _time.monotonic() + max(0.0, wait)
    got = False
    try:
        while True:
            try:
                _fcntl.flock(fh.fileno(), _fcntl.LOCK_EX | _fcntl.LOCK_NB)
                got = True
                break
            except OSError:
                if _time.monotonic() >= deadline:
                    break
                _time.sleep(0.05)
        yield got
    finally:
        if got:
            with _contextlib.suppress(OSError):
                _fcntl.flock(fh.fileno(), _fcntl.LOCK_UN)
        with _contextlib.suppress(OSError):
            fh.close()


def log_call(record: str, env: "dict[str, str] | None" = None) -> None:
    """Record 1 gated call. Logging never fails a call: it is measurement."""
    src = env if env is not None else os.environ
    path = Path(src.get(CALL_LOG_ENV) or DEFAULT_CALL_LOG)
    with _contextlib.suppress(OSError):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{_dt.datetime.now().astimezone().isoformat(timespec='seconds')} {record}\n")


def run_local(code: str, timeout: int = 120, runner=subprocess.run,
              script: str | None = None, serialise: bool = True,
              lock_wait: float | None = None) -> dict:
    """Evaluate `code` on the local kernel, retrying once after a non-evidence result.

    Queued against the machine-wide kernel lock by default, for the reason in
    :func:`kernel_lock`. `serialise=False` is for a caller that already holds it.
    """
    script = script or real_wolframscript()
    if not script:
        return {"evidence": False, "reason": "wolframscript is not installed", "attempts": 0,
                "stdout": "", "stderr": "", "returncode": None, "attribution": None}
    if serialise:
        with kernel_lock(wait=lock_wait) as got:
            if not got:
                return {"evidence": False, "attempts": 0, "stdout": "", "stderr": "",
                        "returncode": None, "attribution": None,
                        "reason": "another Wolfram call held the single-kernel queue; "
                                  "not a blocker, use the open-source tools"}
            return run_local(code, timeout=timeout, runner=runner, script=script, serialise=False)
    last: dict = {}
    for attempt in (1, 2):
        try:
            r = runner([script, "-code", code], capture_output=True, text=True,
                       timeout=timeout, stdin=subprocess.DEVNULL)
            out, err, rc = r.stdout or "", r.stderr or "", r.returncode
        except subprocess.TimeoutExpired:
            out, err, rc = "", f"[Timeout after {timeout}s]", None
        ok, why = classify("local", (out + "\n" + err).strip(), rc if rc is not None else 124)
        last = {"evidence": ok, "reason": why, "attempts": attempt, "stdout": out,
                "stderr": err, "returncode": rc, "attribution": attribution("local") if ok else None}
        if ok:
            break
    return last


def parse_licence_expiry(text: str) -> str | None:
    """`DateObject[{2026, 10, 8}, Day]` -> `2026-10-08`."""
    m = re.search(r"DateObject\[\{\s*(\d{4}),\s*(\d{1,2}),\s*(\d{1,2})", text or "")
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None


def licence_warning(expiry: str = RECORDED_LICENCE_EXPIRY, today: _dt.date | None = None,
                    horizon_days: int = 14) -> str | None:
    """A warning when the Engine licence has lapsed or lapses within `horizon_days`."""
    today = today or _dt.date.today()
    left = (_dt.date.fromisoformat(expiry) - today).days
    if left < 0:
        return f"the Wolfram Engine licence EXPIRED on {expiry}; run `wolframscript -activate`"
    if left <= horizon_days:
        return (f"the Wolfram Engine licence expires on {expiry}, in {left} day(s), and did not "
                f"auto-renew last time; renew it by hand with `wolframscript -activate`")
    return None


def gated_path(env: dict[str, str], pol: str | None = None) -> dict[str, str]:
    """`env` with the policy's gate first on PATH, and the other gate removed."""
    out = dict(env)
    chosen = str(gate_dir(pol or policy(env)))
    others = {str(DENY_GATE), str(SERIAL_GATE)}
    rest = [d for d in out.get("PATH", "").split(os.pathsep) if d and d not in others]
    out["PATH"] = os.pathsep.join([chosen, *rest])
    return out


def run_gated(args: list[str], tool: str = "wolframscript", runner=subprocess.run,
              env: "dict[str, str] | None" = None, seat: str | None = None) -> int:
    """Run the real `tool` under the single-kernel queue, and say what it was worth.

    This is the body of the `serial` gate that sits first on a seat's PATH. It
    passes the child's arguments and exit code through untouched -- annotating,
    never overriding, because a local kernel exits 0 on `1/0` -- and appends the
    attribution when the call computed, or `NOT EVIDENCE` and the reason when it
    did not, so a failed call cannot be quoted as a result.
    """
    import sys
    src = env if env is not None else os.environ
    seat = seat or src.get("CDSFL_SEAT") or src.get("CDSFL_AGENT") or "unknown"
    real = real_tool(tool, src.get("PATH", ""))
    if not real:
        msg = (f"[Error] {tool} is not installed on this machine. NOT EVIDENCE, and NOT a blocker: "
               "Wolfram is the second falsifier here, never a dependency. Use SymPy, z3, mpmath, "
               "SciPy, statsmodels or NumPy, which are primary in every case, and say in your reply "
               "that Wolfram was unavailable.")
        print(msg, file=sys.stderr)
        log_call(f"{seat}\tABSENT\t{tool}", src)
        return 127
    waited = _time.monotonic()
    with kernel_lock(env=src) as got:
        queued = _time.monotonic() - waited
        if not got:
            msg = ("[Error] the single Wolfram kernel stayed busy; this call was never made. NOT "
                   "EVIDENCE, and NOT a blocker: use the open-source tools, which are primary, and "
                   "say in your reply that the Wolfram queue was busy.")
            print(msg, file=sys.stderr)
            log_call(f"{seat}\tBUSY\t{queued:.1f}s waited", src)
            return BUSY_EXIT
        started = _time.monotonic()
        try:
            r = runner([real, *args], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            out, err, rc = r.stdout or "", r.stderr or "", r.returncode
        except OSError as exc:                       # the binary exists but would not start
            out, err, rc = "", f"[Error] {exc}", 126
        took = _time.monotonic() - started
    if out:
        print(out, end="")
    if err:
        print(err, end="", file=sys.stderr)
    ok, why = classify("local", (out + "\n" + err).strip(), rc)
    print(attribution("local") if ok else f"[NOT EVIDENCE] {why}: this call verified nothing, so "
          "the claim stays UNVERIFIED. Not a blocker: the open-source tools are primary.",
          file=sys.stderr)
    log_call(f"{seat}\t{'EVIDENCE' if ok else 'NOT_EVIDENCE'}\t{why}\t"
             f"queued {queued:.1f}s\tran {took:.1f}s\texit {rc}", src)
    return rc


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys
    raw = list(sys.argv[1:] if argv is None else argv)
    # `serial` is handled BEFORE argparse, because everything after it belongs to
    # the kernel: `wolframscript -code '...'` must reach the child verbatim, and
    # an argument parser would claim `-code` as its own.
    if raw and raw[0] == "serial":
        tool, rest = "wolframscript", raw[1:]
        if len(rest) >= 2 and rest[0] == "--tool":
            tool, rest = rest[1], rest[2:]
        if rest and rest[0] == "--":
            rest = rest[1:]
        return run_gated(rest, tool=tool)
    ap = argparse.ArgumentParser(description="The Wolfram standard. `deny` is what the deny gate "
                                             "runs; `serial` is what the serial gate runs.")
    ap.add_argument("command", choices=("deny", "serial", "licence", "policy"))
    args, _ = ap.parse_known_args(raw)
    if args.command == "deny":
        print(DENY_MESSAGE)
        return 3
    if args.command == "policy":
        print(policy())
        return 0
    print(licence_warning() or f"licence recorded as valid until {RECORDED_LICENCE_EXPIRY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
