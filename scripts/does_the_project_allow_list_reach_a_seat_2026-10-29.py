#!/usr/bin/env python3
r"""Does the project's `.claude/settings.json` allow-list actually reach a CLI seat?

HIS ANNOTATION, 2026-10-29, verbatim: *"This is part of the Claude login process,
which as stated previously has already been done. The login process asks you to
trust the workspace or not. I accepted the prompt to authorise it. You can test it
to see."*

WHAT WAS CLAIMED AND WHY IT NEEDED TESTING. `Decisions_Awaiting_You_2026-10-29`
decision 2 said the project is not marked trusted, so "the command line tool
ignores the 20 permission entries the project settings declare", and that "seats
therefore run in a degraded state". That is 2 claims, and only the FIRST was ever
measured -- by reading a flag. The second was inferred from it. Reading a flag is
FIND, not ANALYSE: the deciding layer is whether a dispatched seat can use a tool
the project file allows.

WHAT THE FLAG ACTUALLY SAYS, measured 2026-10-29 from ~/.claude.json:
  /Users/georgejackson/Developer_Projects                    hasTrustDialogAccepted = True
  /Users/georgejackson/Developer_Projects/Constraint_Engineering  hasTrustDialogAccepted = False
So he is right that he accepted a trust prompt, and the earlier note was reading a
DIFFERENT key from the one his acceptance wrote. Both statements were true of
different directories, which is precisely why a flag is not the predicate.

THE DESIGN, with its control, because a control is what proves discrimination.
  TREATMENT: `claude -p` launched with cwd inside the repository, default
             permission mode, NO --allowedTools. The repository's
             .claude/settings.json allows `Bash`.
  CONTROL:   the identical invocation from a scratch directory carrying NO
             .claude/settings.json at all.
If BOTH succeed, the project file is NOT what permits the tool and the treatment
cannot support a claim about it. If the treatment succeeds and the control does
not, the project allow-list is in force. If NEITHER succeeds, the allow-list is
not reaching the seat and the original claim stands on its second half too.

A SEAT IS NOT ASKED TO DO WORK HERE. The prompt is 1 echo, so this costs the
subscription a few hundred tokens and nothing else; `a --help must never cost
money` is respected because --help never reaches the dispatch.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOKEN = "TRUST_PROBE_OK_7f3a"
PROMPT = (
    f"Use the Bash tool to run exactly: echo {TOKEN}\n"
    "Then reply with only the command's output and nothing else."
)
TIMEOUT_S = 180


def trust_flags() -> dict[str, object]:
    """Report hasTrustDialogAccepted for the repo and each ancestor that has an entry."""
    path = Path.home() / ".claude.json"
    if not path.exists():
        return {"error": f"{path} absent"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {"error": f"unreadable: {exc}"}
    projects = data.get("projects", {})
    out: dict[str, object] = {}
    candidates = [REPO] + list(REPO.parents)
    for cand in candidates:
        key = str(cand)
        if key in projects:
            out[key] = projects[key].get("hasTrustDialogAccepted", "<absent>")
    return out


def allow_entries() -> list[str]:
    path = REPO / ".claude" / "settings.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("permissions", {}).get("allow", []))


_KEEP_ON_SCRUB = {
    "PATH", "HOME", "SHELL", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "TERM",
}


def scrubbed_env() -> tuple[dict[str, str], list[str]]:
    """Every CLAUDE_*/ANTHROPIC_* variable removed, so an inherited grant cannot explain a pass."""
    env = {
        k: v
        for k, v in os.environ.items()
        if k in _KEEP_ON_SCRUB or not re.match(r"^(CLAUDE|ANTHROPIC)", k)
    }
    removed = sorted(k for k in os.environ if k not in env)
    return env, removed


def run_seat(cwd: Path, scrub: bool = False) -> dict[str, object]:
    exe = shutil.which("claude")
    if exe is None:
        return {"ran": False, "reason": "claude not on PATH"}
    if scrub:
        env, removed = scrubbed_env()
    else:
        env, removed = dict(os.environ), []
    try:
        proc = subprocess.run(
            [exe, "-p", PROMPT],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return {"ran": False, "reason": f"timed out after {TIMEOUT_S}s"}
    out = (proc.stdout or "") + (proc.stderr or "")
    return {
        "ran": True,
        "returncode": proc.returncode,
        "token_present": TOKEN in out,
        "chars": len(out),
        "env_removed": len(removed),
        "tail": out.strip()[-400:],
    }


def classify(treatment: dict[str, object], control: dict[str, object]) -> str:
    t = bool(treatment.get("token_present"))
    c = bool(control.get("token_present"))
    if not treatment.get("ran") or not control.get("ran"):
        return "UNMEASURED: a condition did not run; see its reason"
    if t and c:
        return (
            "NOT DISCRIMINATING: the tool ran with and without the project file, "
            "so the project allow-list is not what permits it and no claim about "
            "the allow-list may rest on this"
        )
    if t and not c:
        return "ALLOW-LIST IN FORCE: the project file is what permitted the tool"
    if (not t) and c:
        return "INVERTED: the project file appears to RESTRICT rather than permit"
    return (
        "ALLOW-LIST NOT REACHING THE SEAT: neither condition could use the tool, "
        "so the degraded-state half of the original claim survives"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--no-dispatch",
        action="store_true",
        help="report the flags and the allow-list without launching any seat",
    )
    args = ap.parse_args()

    flags = trust_flags()
    allows = allow_entries()
    report: dict[str, object] = {
        "trust_flags": flags,
        "allow_entry_count": len(allows),
        "allow_entries": allows,
    }

    if not args.no_dispatch:
        with tempfile.TemporaryDirectory(prefix="trust_control_") as tmp:
            control_dir = Path(tmp)
            report["treatment"] = run_seat(REPO)
            report["control"] = run_seat(control_dir)
            report["control_scrubbed_env"] = run_seat(control_dir, scrub=True)
            report["verdict"] = classify(report["treatment"], report["control"])  # type: ignore[arg-type]

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("== does the project allow-list reach a CLI seat? ==")
    print("   trust flags recorded in ~/.claude.json:")
    if "error" in flags:
        print(f"     {flags['error']}")
    else:
        for k, v in flags.items():
            print(f"     {v!r:>8}  {k}")
    print(f"   project allow entries: {len(allows)}")
    if "verdict" in report:
        for name in ("treatment", "control", "control_scrubbed_env"):
            r = report[name]
            assert isinstance(r, dict)
            if r.get("ran"):
                print(
                    f"   {name:<22} returncode={r['returncode']} "
                    f"token_present={r['token_present']} chars={r['chars']} "
                    f"env_removed={r['env_removed']}"
                )
            else:
                print(f"   {name:<22} DID NOT RUN: {r['reason']}")
        print(f"   VERDICT: {report['verdict']}")
    else:
        print("   no seat dispatched (--no-dispatch)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
