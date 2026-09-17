#!/usr/bin/env python3
"""Do the runner's fix gates need the dispatcher's secrets? Measured, not assumed.

Action list item 4, 2026-09-17. `_apply_back_gate` and `_run_effect_regression`
in `bench/reference_runner_v3.py` run an experiment's `test_cmd` over a sandbox
copy holding MODEL-PROPOSED source, with the parent's full environment, API keys
included. Before they are given `seat_environment()` instead, this runs the same
pytest selections twice, once with the `.env` secrets present and once with the
environment a seat now gets, and compares the passed, failed, skipped and error
counts. The change is justified only if every pair agrees.

The selections are every distinct non-empty `test_cmd` configured in a tracked
experiment config except the whole-suite one, which takes hours and is
represented instead by every test file that names a secret-named variable, the
only tests whose outcome could depend on one.

Secret VALUES are loaded into the child environment and never printed; only
names and counts are. Nothing is written. Runs only with --run.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))

COUNT = re.compile(r"(\d+) (passed|failed|skipped|error|errors|xfailed|xpassed)")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def configured_commands() -> list[str]:
    cmds = set()
    for rel in _git("ls-files", "bench/*.json", "bench/**/*.json").split():
        if rel.startswith("bench/logs/"):
            continue
        try:
            data = json.loads((REPO / rel).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        cmd = data.get("test_cmd") if isinstance(data, dict) else None
        if isinstance(cmd, str) and cmd.strip():
            cmds.add(cmd.strip())
    return sorted(cmds)


def secret_reading_tests() -> list[str]:
    from experiment_11_orchestrator import _SECRET_NAME
    out = []
    for rel in _git("ls-files", "bench/tests/*.py").split():
        if not Path(rel).name.startswith("test_"):
            continue   # conftest.py applies to every selection anyway; fixtures are not tests
        src = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        names = set(re.findall(r"['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]", src))
        if any(_SECRET_NAME.search(n) for n in names) and re.search(r"environ|getenv|setenv|delenv", src):
            out.append(rel)
    return out


def dotenv() -> dict[str, str]:
    env = {}
    path = REPO / ".env"
    if path.is_file():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.removeprefix("export ").partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def counts(argv: list[str], env: dict[str, str]) -> dict[str, int]:
    r = subprocess.run(argv + ["-p", "no:cacheprovider"], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=3600)
    last = [line for line in r.stdout.splitlines() if COUNT.search(line)]
    found = {k.rstrip("s") if k == "errors" else k: int(n) for n, k in COUNT.findall(last[-1])} if last else {}
    found["exit"] = r.returncode
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare fix-gate test outcomes with and without the "
                                             "dispatcher's secrets. Read-only; runs pytest twice per selection.")
    ap.add_argument("--run", action="store_true", help="actually run the selections")
    args = ap.parse_args()
    if not args.run:
        print("Not run. Pass --run to execute each selection twice.")
        return 0
    from experiment_11_orchestrator import seat_environment
    with_secrets = {**os.environ, **dotenv()}
    without = seat_environment(with_secrets)
    held = sorted(k for k in set(with_secrets) - set(without))
    print(f"secret-named variables present in the 'with' run: {len(held)} ({', '.join(held)})")
    selections = [shlex.split(c) for c in configured_commands() if c.split()[-3:] != ["bench/tests/", "-q", "--tb=line"]]
    tests = secret_reading_tests()
    selections.append([sys.executable, "-m", "pytest", *tests, "-q", "--tb=line"])
    print(f"test files naming a secret-named variable: {len(tests)}")
    agree = 0
    for argv in selections:
        argv = [sys.executable if a in ("python3", "python") else a for a in argv]
        a, b = counts(argv, with_secrets), counts(argv, without)
        same = a == b
        agree += same
        label = " ".join(x for x in argv[3:] if not x.startswith("-"))[:90]
        print(f"{'AGREE   ' if same else 'DISAGREE'} {label}\n  with secrets: {a}\n  without:      {b}")
    print(f"selections agreeing: {agree} of {len(selections)}")
    return 0 if agree == len(selections) else 1


if __name__ == "__main__":
    raise SystemExit(main())
