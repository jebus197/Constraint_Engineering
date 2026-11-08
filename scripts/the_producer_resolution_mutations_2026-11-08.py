"""Reversal harness for the decisions-producer resolution guard.

A guard that has not been shown to go RED is a hypothesis about coverage. This
reverts the predicate 4 ways, each aimed at a DISTINCT assertion, and requires
the guard to fail every time. It restores what it FOUND, byte-exactly, because
a harness that restores a remembered copy rather than the bytes it read becomes
the mutation it was testing.

★ ON ITS FIRST RUN 1 OF THE 4 ANCHORS DID NOT MATCH, and the harness
reported SKIP rather than counting it. The anchor had been written from
memory as `for p in cited` while the installed predicate reads `for c in
cited`. That is the derive-your-anchors rule: an anchor restated rather than
read is a mutation that silently never happens, and a bare "3 of 4 caught"
would have read as a coverage gap in the GUARD instead of a typo in the
PROBE. The anchor is now derived from the live source by regex above.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GEN = REPO / "scripts" / "morning_report_build_2026-10-12.py"
GUARD = REPO / "bench" / "tests" / "test_a_decisions_producer_must_resolve_2026-11-08.py"

MUTATIONS = [
    ("the predicate decides nothing and always returns clean",
     "    out: list[str] = []\n    for key, v in detail.items():",
     "    out: list[str] = []\n    return out  # MUTANT\n    for key, v in detail.items():"),
    ("ALL must resolve instead of AT LEAST ONE, so naming history fails",
     "if not any((root / c).is_file() for c in cited):",
     "if not all((root / c).is_file() for c in cited):  # MUTANT"),
    ("archived keys are no longer skipped",
     'if key.startswith("_") or not isinstance(v, dict):',
     'if not isinstance(v, dict):  # MUTANT'),
    ("an item citing no producer is no longer exempt",
     "        if not cited:\n            continue",
     "        if False:  # MUTANT\n            continue"),
]


def main() -> int:
    # ★ `--help` MUST NOT DO THE WORK. Added 2026-11-08: 8 scripts of this
    # date wrote files while answering `--help`, which
    # `bench/tests/test_help_never_acts_2026-09-11.py` forbids and which
    # `feedback_help_must_never_cost_money` records as 15 of 17 runners
    # billing for a help request. A parser is used rather than
    # `_cli_help.answer_help` because an unrecognised argument then exits 2
    # instead of being ignored, and because it cannot be made unreachable
    # under `python3 -m`, which is how 5 of 9 earlier repairs failed.
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    original = GEN.read_bytes()
    print(f"saved {len(original)} bytes of {GEN.name}")
    reds = 0
    try:
        for label, old, new in MUTATIONS:
            text = original.decode("utf-8")
            if text.count(old) != 1:
                print(f"  SKIP  {label}: anchor occurs {text.count(old)}x, "
                      f"so this mutation is not derived from the live source")
                continue
            GEN.write_text(text.replace(old, new), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               cwd=str(REPO), capture_output=True, text=True)
            tail = [ln for ln in r.stdout.splitlines()
                    if "passed" in ln or "failed" in ln]
            verdict = "RED" if r.returncode != 0 else "GREEN -- NOT CAUGHT"
            reds += r.returncode != 0
            print(f"  {verdict:<18} {label}")
            print(f"                     {tail[-1] if tail else '(no summary)'}")
    finally:
        GEN.write_bytes(original)
        assert GEN.read_bytes() == original, "restore did not reproduce the bytes read"
        print(f"restored {GEN.name} byte-exactly")
    n = len([m for m in MUTATIONS])
    print(f"\n{reds} of {n} reversals caught")
    return 0 if reds == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
