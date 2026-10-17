#!/usr/bin/env python3
"""Can adding a COMMENT change a latent-control verdict? Measured, not argued.

WHY THIS EXISTS. `scripts/latent_control_audit.py` decides whether an unseen
report key is SILENT_BUT_RAN ("the surrounding code demonstrably ran") or
AMBIGUOUS ("we cannot tell") by looking for an unconditional, archive-witnessed
sibling write WITHIN 40 LINES. Proximity in LINES is a proxy for "the same block
of executed code", and a comment occupies lines without executing anything. So
the proxy can be broken by prose.

This was not hypothesised. On 2026-10-17, wiring the evidence predicate into the
human-review stop (entry B27) inserted explanatory comments above
`result["hil_status"]` and flipped its verdict from SILENT_BUT_RAN to AMBIGUOUS
while the executed behaviour of that write was unchanged. The repair that restored
it was to FACTOR OUT code into helpers and SHORTEN a comment -- that is, to edit
prose until an instrument agreed -- which is the wrong direction of causation.

THE SAME DEFECT CLASS WAS FIXED EARLIER THE SAME DAY in a different instrument: a
guard whose verdict depended on a 1,100-character comment slice was converted to
read the abstract syntax tree instead, which is strictly stronger because it sees
the structure the interpreter runs rather than the text around it.

This script sweeps the gap and reports where the verdict flips, so the fragility
is a measured line number rather than a claim. It modifies nothing: it works on a
COPY in a temporary directory and leaves the repository untouched.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KEY = "hil_status"
WITNESS = 'result["registry"] = registry.to_dict()'
TARGET = f'result["{KEY}"] = "paused_for_review"'


def _audit_module():
    """Import the audit once. Its RUNNER constant is what we repoint."""
    spec = importlib.util.spec_from_file_location(
        "lca_probe", REPO / "scripts" / "latent_control_audit.py")
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod


def _verdict_for(mod, source_path: Path, key: str) -> tuple[str, object, list]:
    """Audit with RUNNER repointed at `source_path`.

    IT DOES NOT COPY THE REPOSITORY. An earlier draft of this script copied the
    whole tree once per padding step; the logs directory alone is about 776 MB and
    the founder's machine has 8 GiB, so 5 copies would have been a resource fault
    committed in the course of measuring a different one. The audit reads the
    runner through a single module constant, so repointing that constant is both
    cheaper and a more faithful isolation: nothing else about the tree changes.
    """
    original = mod.RUNNER
    try:
        mod.RUNNER = source_path
        with contextlib.redirect_stdout(io.StringIO()):
            res = mod.audit()
    finally:
        mod.RUNNER = original
    for row in res["rows"]:
        if row["key"] == key:
            return row["verdict"], row["sibling"], row["lines"]
    return "KEY ABSENT", None, []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-padding", type=int, default=6,
                    help="how many comment lines to try inserting")
    args = ap.parse_args()

    runner_rel = Path("bench") / "reference_runner_v3.py"
    source = (REPO / runner_rel).read_text(errors="ignore")
    lines = source.splitlines()

    def line_of(needle: str) -> int:
        for i, ln in enumerate(lines, start=1):
            if needle in ln:
                return i
        return -1

    w, tg = line_of(WITNESS), line_of(TARGET)
    if w < 0 or tg < 0:
        print("the witness or the target write was not found -- the shape has moved, "
              "so this measurement cannot be made and is NOT reported as a pass")
        return 2
    print(f"witness `result[\"registry\"]` at line {w}")
    print(f"target  `result[\"{KEY}\"]`     at line {tg}")
    print(f"gap in lines: {tg - w}   (the audit's sibling window is 40)")
    print()

    mod = _audit_module()
    results = []
    with tempfile.TemporaryDirectory() as td:
        for pad in range(0, int(args.max_padding) + 1):
            padded = (lines[:tg - 1]
                      + ["            # padding" for _ in range(pad)]
                      + lines[tg - 1:])
            probe = Path(td) / f"runner_pad{pad}.py"
            probe.write_text("\n".join(padded) + "\n")
            verdict, sibling, _at = _verdict_for(mod, probe, KEY)
            results.append((pad, tg - w + pad, verdict, sibling))
            print(f"  +{pad} comment line(s)  gap {tg - w + pad:3}  -> {verdict:15} "
                  f"sibling={sibling}")

    print()
    flips = [r for r in results if r[2] != results[0][2]]
    if flips:
        first = flips[0]
        print(f"★ THE VERDICT FLIPS at +{first[0]} comment line(s), gap {first[1]}: "
              f"{results[0][2]} -> {first[2]}.")
        print("  No executed behaviour changed. Comment lines are not code, and a")
        print("  classification that moves when prose is added is measuring the wrong")
        print("  thing. The repair is the one applied to the other instrument the same")
        print("  day: decide from the syntax tree, not from line proximity.")
    else:
        print("the verdict did NOT flip within the padding tried, so this particular")
        print("fragility is not demonstrated at this distance -- which is not the same")
        print("as the proxy being sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
