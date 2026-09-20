"""Read-only repository tools for the metered panel routes.

WHY THIS FILE EXISTS. `bench/openrouter_tools.py` was built for Exp 40 and offers
sympy, z3, pytest, ruff and mypy -- but NO WAY TO READ A FILE. So even with the
tool loop switched on, Codex, Gemini, ChatGPT and DeepSeek could run a checker and
could not look at the source it was checking. CC2 and Fable reach files natively
through the Claude CLI; the other four never have, in this project's history.

Every tool here is READ-ONLY and confined to the repository. A model in this
experiment proposes a patch as text; it never writes to disk. Only
`bench/build_acceptance.py` applies anything, and only inside a throwaway
worktree.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAX_CHARS = 24_000

TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a UTF-8 text file from the repository. Returns the RAW "
                       "text, byte for byte, so anything you copy from it can be used "
                       "verbatim in a SEARCH block. Pass numbered=true only if you want "
                       "line numbers to cite a location -- numbered output must NEVER be "
                       "pasted into a SEARCH block.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "repo-relative path"},
            "start": {"type": "integer", "description": "first line, 1-based (optional)"},
            "end": {"type": "integer", "description": "last line, inclusive (optional)"},
            "numbered": {"type": "boolean", "description": "prefix line numbers (default false)"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "grep",
        "description": "Search the repository for a regular expression. Returns "
                       "path:line:text for each match.",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string"},
            "path": {"type": "string", "description": "repo-relative dir or file to search"},
            "max_results": {"type": "integer"}},
            "required": ["pattern"]}}},
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the entries of a repository directory.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_pytest",
        "description": "Run pytest on a repo-relative test path, offline. Returns the "
                       "tail of the output. Use it to see a test fail before you fix it.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "expression": {"type": "string", "description": "-k expression (optional)"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_python",
        "description": "Run a short read-only Python snippet from the repo root. Use it "
                       "to CHECK a claim rather than assert it. Do not write files.",
        "parameters": {"type": "object", "properties": {"code": {"type": "string"}},
                       "required": ["code"]}}},
]



#: A read-only execution profile. Reads anywhere, writes only to scratch.
_SANDBOX_PROFILE = """(version 1)
(allow default)
(deny file-write*)
(allow file-write* (subpath "/private/tmp") (subpath "/tmp") (subpath "/dev"))
"""

# THE PROFILE IS PASSED INLINE AND NEVER WRITTEN TO DISK (2026-09-20, second
# pass, after a panel agent found the first pass had opened an escape).
#
# The first version cached the profile at
# `pathlib.Path(tempfile.gettempdir()) / "cdsfl_tool_readonly.sb"` and passed it
# as `sandbox-exec -f <path>`, reusing it whenever the file existed WITHOUT
# verifying its contents. `tempfile.gettempdir()` returns `/tmp` whenever TMPDIR
# is unset, and the profile below GRANTS the confined child write access to
# `/tmp`. So a seat could overwrite the cached profile on one call and run
# completely unconfined on the next.
#
# MEASURED END TO END rather than argued: call 1 "REPO WRITE: DENIED
# PermissionError"; call 2 overwrites the cached profile with "(allow default)";
# call 3 "REPO WRITE: ALLOWED". Two tool calls take a seat from confined to
# unconfined. On this machine TMPDIR is set to a /var/folders path outside the
# allow-list, so it was not live HERE -- which is the point: the guard's
# integrity rested on an environment variable, and a guard that silently
# degrades to no guard is the exact defect this module's docstring says it
# exists to prevent.
#
# `sandbox-exec -p <profile-string>` takes the profile on the command line and
# needs no file at all. Measured identical on the property that matters: the
# inline form returns the same "DENIED PermissionError" on a repository write.
# Removing the write also restores the module's bright line -- no write appears
# in it anywhere -- which the source-text guard in
# bench/tests/test_build_experiment_tools.py checks as a second layer beside the
# executing guard in test_seat_tools_are_read_only_2026-09-20.py.


def _confined(argv: list):
    """Wrap `argv` so it CANNOT write to the repository. (cmd, refusal_note).

    WHY THIS EXISTS, MEASURED 2026-09-20. When the panel's paid seats were given
    `run_python`, the tool ran `python3 -c <code>` with `cwd=REPO` and no
    confinement whatever. A probe wrote a file into the repository root and into
    /tmp, and both succeeded. The tool's own description says "Run a short
    read-only Python snippet ... Do not write files", which is an INSTRUCTION
    AND NOT A GUARD -- and this project has twice recorded panel agents editing
    the repository mid-run.

    The paid seats reach the real tree, not a sandbox copy: `panel_sandbox`
    confines the CLI seats by working directory, and an HTTP seat has no working
    directory to confine. So before today the confinement rested entirely on
    those seats having no filesystem tool at all. Giving them one removed the
    only thing that was stopping them.

    IT FAILS CLOSED. If `sandbox-exec` is unavailable the call is REFUSED rather
    than run unconfined, because a guard that silently degrades to no guard is
    the defect it was written to prevent. That costs the tool on platforms
    without it, and the refusal says so plainly instead of pretending.
    """
    if not shutil.which("sandbox-exec"):
        return None, ("[REFUSED] execution is confined read-only via sandbox-exec, "
                      "which is not available on this platform. Running unconfined "
                      "would let a review seat modify the repository it is "
                      "reviewing, so the call is refused rather than downgraded.")
    return ["sandbox-exec", "-p", _SANDBOX_PROFILE, *argv], ""


def _root() -> Path:
    """The tree this seat's tools may see: its OWN sandbox, or the repo.

    WHY THIS EXISTS, AND IT IS THE PROJECT'S SIGNATURE FAILURE ONE LAYER DOWN
    (2026-09-20). The panel dispatcher builds a sandbox copy FOR EVERY SEAT --
    measured in round 4: 7 copies for 7 seats, including all 5 paid ones -- and
    sets the calling thread's working directory to it via `set_panel_cwd`.
    The CLI seats honour that, because their tools are a subprocess with a cwd.

    This module did not. `_safe()` resolved every path against the module-level
    `REPO` constant, so the HTTP seats' `read_file`, `grep`, `list_dir`,
    `run_python` and `run_pytest` all reached the LIVE repository while the
    seat's own private copy sat untouched. 5 of 7 sandboxes were built and
    never used.

    WHAT THAT COST, MEASURED. In round 4 the `ge` seat ran
    `grep -rn 10.4882 bench` and swept in 4.7945% of the `cx` seat's reply,
    Wilson [2.8772%, 7.8858%] -- because `bench/logs/<round>/` in the LIVE tree
    accumulates each seat's answer as it finishes. Seats that were supposed to
    be independent were reading each other mid-round. Read-only confinement
    could not prevent it: the defect was never about what they could WRITE.

    The dispatcher's own comment records the same shape one level up: "The cwd
    mechanism has existed since August ... and was never called ... describing
    the confinement half as unbuilt when in fact it was built and unwired".

    FAILS SAFE. When no panel cwd is set -- ordinary experiment runs, the test
    suite, direct use -- this returns `REPO` exactly as before, so every
    existing caller is unchanged. A panel cwd that is not a directory is
    refused by `set_panel_cwd` itself rather than silently ignored.
    """
    # BOTH IMPORT NAMES ARE CONSULTED, AND THAT IS NOT PEDANTRY (2026-09-20).
    #
    # The dispatcher puts `bench/` on sys.path and imports the orchestrator
    # bare; a caller that imports it as `bench.experiment_11_orchestrator` gets
    # a SECOND module object with its OWN thread-local, and a working directory
    # set through one is invisible to the other. Found by this module's own test
    # on the day it was written: `set_panel_cwd` was called, `_root()` returned
    # the live repository, and the seat would have been unconfined.
    #
    # A containment control must not depend on which spelling a caller happened
    # to use. Both are checked, and the first that carries a value wins.
    cwd = None
    import sys as _sys
    for _name in ("experiment_11_orchestrator", "bench.experiment_11_orchestrator"):
        mod = _sys.modules.get(_name)
        if mod is None:
            continue
        try:
            cwd = mod.get_panel_cwd()
        except Exception:  # noqa: BLE001 - not initialised
            cwd = None
        if cwd:
            break
    if not cwd:
        return REPO
    p = Path(cwd)
    return p if p.is_dir() else REPO


def _safe(rel: str) -> Path:
    root = _root()
    p = (root / (rel or "").lstrip("/")).resolve()
    if not str(p).startswith(str(root)):
        raise ValueError(
            # The wording names BOTH, because the confined tree is the
            # repository on an ordinary run and the seat's own sandbox copy
            # during a panel round. Saying only one of them would be wrong
            # half the time, and the existing guard in
            # bench/tests/test_build_experiment_tools.py checks this string.
            f"path escapes the repository or this seat's sandbox tree: {rel}")
    return p


def _clip(s: str) -> str:
    return s if len(s) <= MAX_CHARS else s[:MAX_CHARS] + f"\n[...truncated at {MAX_CHARS} chars]"


def execute(name: str, args: dict) -> str:
    """Dispatch one tool call. Never raises: an error is returned as text so the
    model can see what went wrong and try something else."""
    try:
        if name == "read_file":
            p = _safe(args["path"])
            if not p.is_file():
                return f"[not a file: {args['path']}]"
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            s = int(args.get("start") or 1)
            e = int(args.get("end") or len(lines))
            s, e = max(1, s), min(len(lines), e)
            sel = lines[s - 1:e]
            if args.get("numbered"):
                # OPT-IN ONLY. This was the DEFAULT until 2026-08-22 and it made a
                # verbatim SEARCH block impossible: Codex stripped the digits, kept the
                # two-space separator, and every line it returned carried +2 indentation.
                # The rejection rendered as a model failure and was a harness failure.
                return _clip("\n".join(f"{i:>6}  {ln}" for i, ln in enumerate(sel, s)))
            return _clip("\n".join(sel))

        if name == "grep":
            target = str(_safe(args.get("path") or "."))
            n = int(args.get("max_results") or 60)
            r = subprocess.run(
                ["grep", "-rnE", "--", args["pattern"], target],
                capture_output=True, text=True, timeout=60)
            out = "\n".join(
                ln.replace(str(_root()) + "/", "") for ln in r.stdout.splitlines()[:n])
            return _clip(out) or "[no matches]"

        if name == "list_dir":
            p = _safe(args["path"])
            if not p.is_dir():
                return f"[not a directory: {args['path']}]"
            return _clip("\n".join(sorted(
                c.name + ("/" if c.is_dir() else "") for c in p.iterdir())))

        if name == "run_pytest":
            cmd = ["python3", "-m", "pytest", args["path"], "-q", "--netguard-strict"]
            if args.get("expression"):
                cmd += ["-k", args["expression"]]
            r = subprocess.run(cmd, cwd=str(_root()), capture_output=True, text=True,
                               timeout=600)
            return _clip(((r.stdout or "") + (r.stderr or ""))[-6000:])

        if name == "run_python":
            cmd, note = _confined(["python3", "-c", args["code"]])
            if cmd is None:
                return note
            r = subprocess.run(cmd, cwd=str(_root()), capture_output=True,
                               text=True, timeout=180)
            return _clip(((r.stdout or "") + (r.stderr or ""))[-6000:])

        return f"[unknown tool: {name}]"
    except subprocess.TimeoutExpired:
        return "[tool timed out]"
    except Exception as exc:                     # noqa: BLE001 — reported, not swallowed
        return f"[{type(exc).__name__}: {exc}]"
