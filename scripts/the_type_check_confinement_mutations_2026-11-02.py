#!/usr/bin/env python3
"""Does confining the type-check task's comparisons to the files it opened WORK?

WHY THIS EXISTS. On 2026-11-02 `scripts/type_check_task_2026-11-01.py` reported
296 improvements under `--paths scripts/suite_record.py` and 0 on a full run.
All 296 were files the narrowed run never opened: an unchecked file returns 0
findings, and 0 against a non-zero baseline read as a complete improvement. The
`--update` half was worse -- it REPLACED the whole baseline, so a narrowed update
would have deleted every unchecked file's entry.

The repair confines every comparison to the files the run actually opened and
makes `--update` MERGE. A repair not tried against its own failure mode is a
hypothesis, so this harness checks 3 properties by execution:

  M1  A narrowed run stays SILENT about a file it did not open, even when that
      file's baseline says it should look improved.
  M2  A FULL run still REPORTS that same file as improved, so the repair confined
      the comparison rather than deleting it. Without M2, M1 could be satisfied
      by a task that reports nothing at all.
  M3  A narrowed `--update` KEEPS the entries for files it did not check.

IT RESTORES WHAT IT FOUND. The ledger is copied byte-for-byte before anything is
touched and written back in a `finally`, with the restoration verified by hash
before the harness exits.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TASK = REPO / "scripts" / "type_check_task_2026-11-01.py"
LEDGER = REPO / "experimental_notes" / "data" / "type_check_baseline.json"
ONE = "scripts/suite_record.py"


def _run(*args: str) -> str:
    return subprocess.run([sys.executable, "-I", str(TASK), *args],
                          capture_output=True, text=True,
                          cwd=str(REPO)).stdout


def _digest(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if not LEDGER.is_file():
        print("  no ledger at "
              f"{LEDGER.relative_to(REPO)}; run the task with --update first")
        return 1
    original = LEDGER.read_bytes()
    before = _digest(LEDGER)
    results: list[tuple[str, bool, str]] = []

    try:
        led = json.loads(original.decode())
        files = led.get("files") or {}
        # pick a VICTIM that the narrowed run will not open
        victim = next((f for f in sorted(files) if f != ONE), None)
        if victim is None:
            print("  the ledger holds fewer than 2 files; nothing to confine")
            return 1
        # raise its baseline so a naive comparison would call it improved
        led["files"][victim] = int(files[victim]) + 50
        LEDGER.write_text(json.dumps(led, indent=2) + "\n", encoding="utf-8")

        narrow = _run("--paths", ONE)
        full = _run()
        results.append((
            f"M1 a narrowed run stays silent about {victim}",
            victim not in narrow,
            "silent" if victim not in narrow else "NAMED IT -- not confined"))
        results.append((
            f"M2 a FULL run still reports {victim} as improved",
            victim in full and "IMPROVED" in full,
            "reported" if victim in full else "MISSING -- the comparison was "
            "deleted rather than confined"))

        # M3: a narrowed --update must keep the entries it did not check
        keys_before = set(json.loads(LEDGER.read_text())["files"])
        _run("--paths", ONE, "--update")
        keys_after = set(json.loads(LEDGER.read_text())["files"])
        lost = keys_before - keys_after
        results.append((
            "M3 a narrowed --update keeps unchecked entries",
            not lost,
            "kept all" if not lost else f"DROPPED {len(lost)} entr(ies)"))
    finally:
        LEDGER.write_bytes(original)
        after = _digest(LEDGER)
        restored = after == before

    print("=" * 74)
    print("DOES THE CONFINEMENT REPAIR DISCRIMINATE?")
    print("=" * 74)
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {detail}")
    print()
    print(f"  ledger restored byte-for-byte: {restored}")
    print(f"    sha256 before {before[:16]}  after {after[:16]}")
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"  {passed} of {len(results)} propert(ies) hold")
    return 0 if passed == len(results) and restored else 1


if __name__ == "__main__":
    raise SystemExit(main())
