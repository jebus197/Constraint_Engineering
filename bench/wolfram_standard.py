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
    it was activated by hand on 2026-09-15 and expires 2026-10-08.
  * The DENY layer for automated runs, which Wolfram's published terms put out
    of bounds: `CLAUDE_CLI_DENY_ARGS` for `claude -p` seats, `gated_path` to put
    a refusing `wolframscript` first on a seat's PATH, and `KERNEL_RE` for the
    falsifier sandbox's spawn check.

WHAT THE DENY LAYER CANNOT DO, said rather than implied. A seat that names the
binary by absolute path steps past both the CLI rule, which matches a command
prefix, and the PATH gate. The falsifier sandbox's check matches the absolute
path too, but a `claude -p` seat's own Bash tool has no such observer. The
layer makes Wolfram use deliberate rather than accidental; it does not make it
impossible.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
DENY_GATE = HERE / "tools" / "wolfram_gate" / "deny"

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

#: The licensed kernel named in a spawn argument: a bare command, a path ending
#: in it, or the application bundle.
KERNEL_RE = re.compile(
    r"(?:^|[\s/;&|'\"(`])(?:wolframscript|WolframKernel|wolfram)(?=$|[\s;&|'\")`])"
    r"|Wolfram Engine\.app|WolframScript\.app")

#: What every panel seat is told, by construction, in the dispatcher's SYSTEM
#: prompt. Built from the constants above so the words cannot drift from the
#: rule the code applies. DENY is the default in force until the founder rules
#: on Wolfram in panel reviews (action list 2026-09-17, item 12(d)).
PANEL_CLAUSE = (
    "WOLFRAM (founder, standing, 2026-09-17). Do not run `wolframscript`, `WolframKernel` or any "
    "Wolfram service in this dispatch: Wolfram's published terms bar its use inside automated AI "
    "pipelines, and the local Engine is licensed for a single kernel. Cross-check with SymPy, "
    "mpmath, SciPy, statsmodels or z3 instead. A Wolfram result that reaches you from anywhere else "
    "is evidence only if it computed. It verified NOTHING, and the claim stays UNVERIFIED, when its "
    "text begins " + ", ".join(FAILURE_PREFIXES) + "; when it came from the hosted connector with "
    "no Out[ line; or when it came from the local kernel and exited non-zero, printed a message of "
    "the form Name::tag, or returned $Failed or $Aborted. A local kernel exits 0 on `1/0`, so the "
    "exit code alone is not enough. Any Wolfram-derived value you quote carries an attribution to "
    "Wolfram Language or Wolfram|Alpha, as Wolfram's terms require.")

#: Deny rules for a `claude -p` seat. `--strict-mcp-config` with no
#: `--mcp-config` also removes the hosted Wolfram connector.
CLAUDE_CLI_DENY_ARGS = ("--disallowedTools", "Bash(wolframscript *)", "Bash(WolframKernel *)",
                        "--strict-mcp-config")


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


def real_wolframscript(path_env: str | None = None) -> str | None:
    """The installed binary, never a gate in this repository."""
    gate_root = str(HERE / "tools" / "wolfram_gate")
    for d in (os.environ.get("PATH", "") if path_env is None else path_env).split(os.pathsep):
        if d and not os.path.realpath(d).startswith(os.path.realpath(gate_root)):
            cand = os.path.join(d, "wolframscript")
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                return cand
    return None


def run_local(code: str, timeout: int = 120, runner=subprocess.run,
              script: str | None = None) -> dict:
    """Evaluate `code` on the local kernel, retrying once after a non-evidence result."""
    script = script or real_wolframscript()
    if not script:
        return {"evidence": False, "reason": "wolframscript is not installed", "attempts": 0,
                "stdout": "", "stderr": "", "returncode": None, "attribution": None}
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


def gated_path(env: dict[str, str]) -> dict[str, str]:
    """`env` with the refusing gate first on PATH."""
    out = dict(env)
    rest = [d for d in out.get("PATH", "").split(os.pathsep) if d and d != str(DENY_GATE)]
    out["PATH"] = os.pathsep.join([str(DENY_GATE), *rest])
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="The Wolfram standard. `deny` is what an automated "
                                             "run's `wolframscript` gate runs.")
    ap.add_argument("command", choices=("deny", "licence"))
    args, _ = ap.parse_known_args(argv)
    if args.command == "deny":
        print(DENY_MESSAGE)
        return 3
    print(licence_warning() or f"licence recorded as valid until {RECORDED_LICENCE_EXPIRY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
