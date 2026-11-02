#!/usr/bin/env python3
"""Revert each of the 2 directive repairs and confirm the NEW guard goes red.

★ THE POINT OF THIS SCRIPT IS A COMPARISON, not just a count. The 2 pre-existing
test files are falsifiers written on 2026-09-10 to demonstrate the ORIGINAL
defects, and they stay GREEN under every reversion below -- which is why both
repairs sat unguarded and neither entry could be marked done. Each mutation is
therefore run against BOTH suites, and the old one going green while the new one
goes red is the evidence that the new file adds coverage rather than duplicating it.
"""
from __future__ import annotations
import pathlib, subprocess, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
MOD = REPO / "bench" / "cdsfl_registry" / "composer.py"
T = REPO / "bench" / "tests"
NEW = T / "test_the_two_directive_repairs_hold_2026-11-02.py"
OLD = [T / "test_falsifier_C0037_containment_dedup_2026-09-10.py",
       T / "test_falsifier_C0036_C0054_conflict_topics_2026-09-10.py"]

MUTATIONS = [
    ("C0037: the survivor goes back to whichever arrived FIRST",
     '''            if _semantically_duplicate(line, existing):
                if len(_normalise_tokens(line)) > len(_normalise_tokens(existing)):
                    deduped[i] = line
                matched = True''',
     '''            if _semantically_duplicate(line, existing):
                matched = True'''),
    ("C0037: the survivor becomes the SHORTER member",
     '''                if len(_normalise_tokens(line)) > len(_normalise_tokens(existing)):''',
     '''                if len(_normalise_tokens(line)) < len(_normalise_tokens(existing)):'''),
    ("C0036: the arbitration record never reaches the manifest",
     '''"conflict_arbitration"''', '''"conflict_arbitration_DISABLED"'''),
    ("C0001: the coherence pruner comes back on by default",
     '''coherence_pruning: bool = False''', '''coherence_pruning: bool = True'''),
]


def run(paths) -> bool:
    p = subprocess.run([sys.executable, "-m", "pytest", *[str(x) for x in paths],
                        "-q", "--no-header"], capture_output=True, text=True,
                       timeout=300, cwd=str(REPO))
    return p.returncode == 0


def main() -> int:
    answer_help(__doc__, __file__)
    original = MOD.read_text()
    print("=" * 78)
    print("THE 2 DIRECTIVE REPAIRS: MUTATION TEST, NEW GUARD vs OLD FALSIFIERS")
    print("=" * 78)
    if not run([NEW]):
        print("  THE NEW SUITE IS ALREADY RED. Nothing concluded. Stopping.")
        return 2
    print(f"  baseline: new suite GREEN, old falsifiers "
          f"{'GREEN' if run(OLD) else 'RED'}\n")
    red = applied = old_green = 0
    try:
        for label, old, new in MUTATIONS:
            if original.count(old) < 1:
                print(f"  [SKIP  ] {label}")
                print(f"           anchor absent -- NOT APPLIED, nothing tested")
                continue
            applied += 1
            MOD.write_text(original.replace(old, new, 1))
            new_ok, old_ok = run([NEW]), run(OLD)
            if new_ok:
                print(f"  [GREEN ] {label}\n           *** THE NEW GUARD DID NOT "
                      f"NOTICE. ***")
            else:
                red += 1
                tag = "and the OLD falsifiers stayed GREEN" if old_ok else \
                      "(the old falsifiers also caught it)"
                old_green += 1 if old_ok else 0
                print(f"  [RED   ] {label}")
                print(f"           {tag}")
            MOD.write_text(original)
    finally:
        MOD.write_text(original)
    print(f"\n  {red} of {applied} applied mutation(s) turned the NEW suite RED")
    print(f"  of those, {old_green} were MISSED ENTIRELY by the 2 pre-existing")
    print(f"  falsifiers, which is the coverage this file adds.")
    print(f"  composer.py restored to its original text: "
          f"{MOD.read_text() == original}")
    return 0 if (red == applied and applied) else 1


if __name__ == "__main__":
    sys.exit(main())
