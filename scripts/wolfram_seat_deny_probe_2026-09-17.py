#!/usr/bin/env python3
"""Can a `claude -p` seat reach `wolframscript`, before and after the deny layer?

Question 11, 2026-09-17. The real kernel is never started. A FAKE `wolframscript`
that prints FAKE-WOLFRAMSCRIPT-REACHED is put first on the base PATH, so the
BEFORE call shows the probe can detect a seat reaching it, and the AFTER call
starts the seat as the launchers now do: `seat_environment()` plus
`WOLFRAM_DENY_ARGS`. The stream-json init event is read for any tool or MCP
server whose name contains "wolfram", so the connector is checked by the CLI's
own report rather than by asking the model.

2 `claude -p` calls on the Max subscription, so it runs only with --live.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
PROMPT = ("Use your Bash tool to run exactly this 1 command, then reply with its output only: "
          "wolframscript -code 1+1")


def _seat(env: dict, deny: tuple) -> dict:
    cmd = ["claude", "-p", PROMPT, "--model", "sonnet", "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--setting-sources", "", *deny, "--allowedTools", "Bash"]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=240,
                       stdin=subprocess.DEVNULL, cwd=tempfile.gettempdir())
    tools, servers, results = [], [], []
    for line in r.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            tools = ev.get("tools", [])
            servers = [s.get("name", "") for s in ev.get("mcp_servers", [])]
        for block in (ev.get("message", {}) or {}).get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                c = block.get("content")
                results.append(c if isinstance(c, str) else json.dumps(c))
    return {"exit": r.returncode, "wolfram_tools": [t for t in tools if "wolfram" in t.lower()],
            "wolfram_servers": [s for s in servers if "wolfram" in s.lower()],
            "reached_fake": any("FAKE-WOLFRAMSCRIPT-REACHED" in x for x in results),
            "gate_refused": any("Wolfram is excluded from automated runs" in x for x in results),
            "tool_results": [x[:160] for x in results]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe the Wolfram deny layer on a real claude -p seat "
                                             "(2 free Max-plan calls, fake wolframscript).")
    ap.add_argument("--live", action="store_true", help="actually make the 2 claude -p calls")
    args = ap.parse_args()
    if not args.live:
        print("Not run. Pass --live to make 2 claude -p calls on the Max subscription.")
        return 0
    sys.path.insert(0, str(REPO / "bench"))
    import experiment_11_orchestrator as orch
    with tempfile.TemporaryDirectory() as d:
        fake = pathlib.Path(d) / "wolframscript"
        fake.write_text("#!/bin/sh\necho FAKE-WOLFRAMSCRIPT-REACHED\n")
        fake.chmod(0o755)
        base = dict(os.environ, PATH=f"{d}{os.pathsep}{os.environ['PATH']}")
        before = _seat(base, ())
        after = _seat(orch.seat_environment(base), orch.WOLFRAM_DENY_ARGS)
    print("BEFORE (no deny layer):", json.dumps(before))
    print("AFTER  (deny layer):   ", json.dumps(after))
    ok = (before["reached_fake"] and not after["reached_fake"]
          and not after["wolfram_tools"] and not after["wolfram_servers"] and after["exit"] == 0)
    print("RESULT:", "the deny layer holds" if ok else "UNEXPECTED -- read the lines above")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
