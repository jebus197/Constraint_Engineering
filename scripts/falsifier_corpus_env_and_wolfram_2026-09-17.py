#!/usr/bin/env python3
"""What the archived falsifiers ask of their environment, and whether any calls Wolfram.

Question 11 and action list item 4, 2026-09-17. Before the falsifier sandbox
(`bench/falsifier_verify.py`) is changed to refuse the Wolfram kernel and to
drop secret-named variables from the child's environment, measure what those 2
changes would take away from falsifiers models have actually written.

Reads every `falsifier_code` string under `bench/logs` (untracked in most clones,
so it says so and exits 0 when the directory is absent). Distinct sources are
counted once. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))

ENV_READ = re.compile(r"os\.environ|os\.getenv|getenv\(|environ\[|environ\.get")


def _strings(node, key):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key and isinstance(v, str) and v.strip():
                yield v
            else:
                yield from _strings(v, key)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v, key)


def corpus() -> set[str]:
    out: set[str] = set()
    for f in (REPO / "bench" / "logs").rglob("*.json"):
        try:
            if f.stat().st_size > 50_000_000 or b"falsifier_code" not in f.read_bytes():
                continue
            out.update(_strings(json.loads(f.read_text(encoding="utf-8", errors="replace")), "falsifier_code"))
        except (OSError, ValueError):
            continue
    return out


def main() -> int:
    argparse.ArgumentParser(description="Measure the archived falsifiers' environment reads and "
                                        "Wolfram calls. Read-only.").parse_args()
    if not (REPO / "bench" / "logs").is_dir():
        print("bench/logs is absent in this clone; nothing to measure")
        return 0
    import wolfram_standard as W
    from experiment_11_orchestrator import _SECRET_NAME
    src = corpus()
    env_reads = [s for s in src if ENV_READ.search(s)]
    names = sorted({n for s in env_reads
                    for n in re.findall(r"environ(?:\.get)?[\[(]\s*['\"]([A-Za-z_][A-Za-z0-9_]*)", s)
                    + re.findall(r"getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)", s)})
    secret_names = [n for n in names if _SECRET_NAME.search(n)]
    wolfram = [s for s in src if W.KERNEL_RE.search(s) or "wolfram" in s.lower()]
    print(f"distinct archived falsifier sources: {len(src)}")
    print(f"sources that read the environment: {len(env_reads)}")
    print(f"variable names they read: {', '.join(names) or 'none'}")
    print(f"secret-named variables they read: {len(secret_names)}{': ' + ', '.join(secret_names) if secret_names else ''}")
    print(f"sources that mention Wolfram or name its kernel: {len(wolfram)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
