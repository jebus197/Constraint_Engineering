#!/usr/bin/env python3
"""Does the census guard actually go red when the repair is reverted?

6 REVERSIONS, each a single textual change to live code, each run against
`bench/tests/test_the_census_counts_only_his_writing_2026-11-04.py`. A guard
that stays green under all of them guards nothing.

MUTATION 2 IS THE ONE THAT MATTERS MOST. There are 2 ways to make the census
agree with the reader: narrow the ANNOTATION counts (correct) or narrow
READABILITY (a regression that blinds the gap detectors). Mutation 2 performs
the wrong one, and the guard must reject it even though the equality it was
written for would then HOLD.

The harness restores every file it touched from the bytes it FOUND, in a
`finally`, including on keyboard interrupt -- a harness that writes and does not
restore leaves no diff and is therefore invisible.

Usage: python3 scripts/the_census_mutations_2026-11-04.py
"""
import argparse
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
RECOVER = REPO / "scripts" / "cdsfl_recover.py"
GUARD = REPO / "bench" / "tests" / "test_the_census_counts_only_his_writing_2026-11-04.py"

MUTATIONS = [
    ("1. revert the gate: count every readable file's markers as his",
     READER,
     """        if not is_one_of_his_annotated_responses(p):
            try:
                size = p.stat().st_size
            except OSError:
                size = -1
            excluded_count += n
            excluded.append({"file": p.name, "annotations": n, "bytes": size,
                             "suffix": p.suffix.lower() or "(none)"})
            continue
""",
     ""),

    ("2. agree the WRONG way: narrow readability to the his-writing set",
     READER,
     '    files = [p for p in RESPONSES.glob("*") if is_a_response_file(p)]\n'
     "    annotated, blind, blind_count, total_count = 0, 0, 0, 0\n",
     '    files = [p for p in RESPONSES.glob("*")\n'
     "             if is_one_of_his_annotated_responses(p)]\n"
     "    annotated, blind, blind_count, total_count = 0, 0, 0, 0\n"),

    ("3. silence the residue: count it but name nothing",
     READER,
     '            excluded.append({"file": p.name, "annotations": n, "bytes": size,\n'
     '                             "suffix": p.suffix.lower() or "(none)"})\n',
     "            pass\n"),

    ("4. drop the residue from the accounting entirely",
     READER,
     "            excluded_count += n\n",
     "            excluded_count += 0\n"),

    ("5. remove the banner's residue clause",
     RECOVER,
     '    residue = (f" A further {extra} markers sit in readable files that are NOT his "\n'
     '               f"writing and are excluded here." if extra else "")\n',
     '    residue = ""\n'),

    ("6. make the banner quote the broad count again",
     RECOVER,
     '    extra = cov.get("annotations_excluded_as_not_his") or 0\n',
     '    extra = cov.get("annotations_excluded_as_not_his") or 0\n'
     '    n_ann = n_ann + extra\n'),
]


def run_guard() -> tuple:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                        "--no-header", "-x"],
                       capture_output=True, text=True, cwd=str(REPO))
    tail = [l for l in r.stdout.splitlines() if l.strip()][-1:] or [""]
    return r.returncode, tail[0][:88]


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()

    base_rc, base_line = run_guard()
    print(f"BASELINE (unmutated): rc={base_rc}  {base_line}")
    if base_rc != 0:
        print("  the guard is not green before mutation; nothing can be concluded.")
        return 2

    originals = {p: p.read_bytes() for p in {READER, RECOVER}}
    red = 0
    try:
        for name, target, old, new in MUTATIONS:
            src = target.read_text(encoding="utf-8")
            if old not in src:
                print(f"  SKIP  {name}\n        anchor absent; mutation not applied")
                continue
            target.write_text(src.replace(old, new, 1), encoding="utf-8")
            try:
                rc, line = run_guard()
            finally:
                target.write_bytes(originals[target])
            verdict = "RED (good)" if rc != 0 else "GREEN -- NOT CAUGHT"
            if rc != 0:
                red += 1
            print(f"  {verdict:<20}{name}")
            print(f"  {'':<20}{line}")
    finally:
        for p, b in originals.items():
            p.write_bytes(b)

    post_rc, post_line = run_guard()
    print(f"\nRESTORED: rc={post_rc}  {post_line}")
    print(f"{red} of {len(MUTATIONS)} reversions turned the guard red.")
    ok = red == len(MUTATIONS) and post_rc == 0
    print("VERDICT:", "every reversion is caught." if ok
          else "AT LEAST 1 REVERSION SURVIVES; the guard is incomplete.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
