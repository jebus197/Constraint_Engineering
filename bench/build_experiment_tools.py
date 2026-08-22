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
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAX_CHARS = 24_000

TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a UTF-8 text file from the repository. Returns the file "
                       "with 1-based line numbers so you can cite them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "repo-relative path"},
            "start": {"type": "integer", "description": "first line, 1-based (optional)"},
            "end": {"type": "integer", "description": "last line, inclusive (optional)"}},
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


def _safe(rel: str) -> Path:
    p = (REPO / (rel or "").lstrip("/")).resolve()
    if not str(p).startswith(str(REPO)):
        raise ValueError(f"path escapes the repository: {rel}")
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
            return _clip("\n".join(f"{i:>6}  {lines[i-1]}" for i in range(s, e + 1)))

        if name == "grep":
            target = str(_safe(args.get("path") or "."))
            n = int(args.get("max_results") or 60)
            r = subprocess.run(
                ["grep", "-rnE", "--", args["pattern"], target],
                capture_output=True, text=True, timeout=60)
            out = "\n".join(
                ln.replace(str(REPO) + "/", "") for ln in r.stdout.splitlines()[:n])
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
            r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True,
                               timeout=600)
            return _clip(((r.stdout or "") + (r.stderr or ""))[-6000:])

        if name == "run_python":
            r = subprocess.run(["python3", "-c", args["code"]], cwd=str(REPO),
                               capture_output=True, text=True, timeout=180)
            return _clip(((r.stdout or "") + (r.stderr or ""))[-6000:])

        return f"[unknown tool: {name}]"
    except subprocess.TimeoutExpired:
        return "[tool timed out]"
    except Exception as exc:                     # noqa: BLE001 — reported, not swallowed
        return f"[{type(exc).__name__}: {exc}]"
