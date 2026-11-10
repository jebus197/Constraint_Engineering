#!/usr/bin/env python3
"""Mutate the 7 repaired defects in the owed derivation; require RED each time.

4 of the 7 were found by a free panel on 2026-11-10 -- both seats independently
-- and 3 were introduced by the repair itself and found by running it. Each
mutation below restores exactly 1 of them, so a reversion cannot pass unnoticed.

ANCHORS ARE DERIVED FROM THE SUBJECT: each asserts its substring occurs EXACTLY
ONCE and reports an ANCHOR MISS otherwise. THE EXPECTATION IS NOT PER-TEST: the
harness requires red and REPORTS which tests detected it.

RESTORES WHAT IT FOUND, verified by sha256.

Run: python3 scripts/the_owed_derivation_mutations_2026-11-10.py
Exit 0 only when every mutation turns the guard red.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys


def _root() -> pathlib.Path:
    start = pathlib.Path(__file__).resolve().parent
    for cand in (start, *start.parents):
        if (cand / "bench" / "domain_immune.py").is_file():
            return cand
    raise SystemExit("cannot locate the repository")


ROOT = _root()
SUBJECT = ROOT / "scripts" / "build_decisions_file_2026-11-07.py"
GUARD = ROOT / "bench" / "tests" / (
    "test_a_response_is_not_a_ruling_2026-11-09.py")

MUTATIONS = [
    ("D1  stop at every bold span, heading or not",
     "        if (star or inner.rstrip().endswith(\":\")",
     "        if (True or inner.rstrip().endswith(\":\")"),
    ("D2  discard the heading's own clause again",
     "    inside = head_raw if continues else \"\"",
     "    inside = \"\""),
    ("D3  restore the 30-character minimum",
     "    hits = list(_OWED_MARKER_RE.finditer(flat))",
     "    hits = [h for h in _OWED_MARKER_RE.finditer(flat)\n"
     "            if len(flat[h.end():]) > 30 and False]"),
    ("D4  coerce the copula onto a clause again",
     "    lead = \"What is still owed:\" if clausal else \"What is still owed is\"",
     "    lead = \"What is still owed is\""),
    ("D4b never skip a value that already opens \"What is\"",
     "    if owed[:12].lower().startswith(\"what is\"):",
     "    if False:"),
    ("M1  split on any full stop, decimals included",
     "    for part in re.findall(r\".*?(?<!\\d)[.!?](?!\\d)(?!\\.)|.+$\", text):",
     "    for part in re.findall(r\"[^.!?]*[.!?]|[^.!?]+$\", text):"),
    ("M2  ellipsise a trailing fragment after a whole sentence",
     "    whole = [x for x in out if x.rstrip().endswith((\".\", \"!\", \"?\"))]\n"
     "    if whole:\n        return \" \".join(whole).strip()",
     "    whole = []\n    if whole:\n        return \" \".join(whole).strip()"),
    ("M3  shout the kept heading",
     "    if continues:\n        joined = _sentence_case(joined)",
     "    if continues:\n        joined = joined"),
]


def board() -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, timeout=900, cwd=str(ROOT))
    return r.returncode, r.stdout + r.stderr


def failing(out: str) -> list[str]:
    return sorted({m.split("::")[-1].split("[")[0]
                   for m in re.findall(r"^FAILED (\S+)", out, re.M)})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)
    original = SUBJECT.read_text()
    sha = hashlib.sha256(original.encode()).hexdigest()

    print("=" * 78)
    print("THE OWED DERIVATION: 7 DEFECTS, 8 MUTATIONS")
    print("=" * 78)
    rc, out = board()
    print(f"  baseline (unmutated)                            exit={rc}  "
          f"{'GREEN' if rc == 0 else 'RED'}")
    if rc != 0:
        print("  *** not green to begin with; nothing below means anything ***")
        print(out[-2500:])
        return 1

    red = 0
    try:
        for label, find, repl in MUTATIONS:
            n = original.count(find)
            if n != 1:
                print(f"  {label:48s}  ANCHOR MISS ({n})")
                continue
            SUBJECT.write_text(original.replace(find, repl, 1))
            rc, out = board()
            if rc == 0:
                print(f"  {label:48s}  exit=0  *** STILL GREEN ***")
            else:
                red += 1
                names = ", ".join(failing(out)) or "collection error"
                print(f"  {label:48s}  RED")
                print(f"       detected by: {names}")
            SUBJECT.write_text(original)
    finally:
        SUBJECT.write_text(original)
        back = hashlib.sha256(SUBJECT.read_text().encode()).hexdigest()
        assert back == sha, "RESTORE FAILED -- the subject is not what I found"
        print(f"\n  restored, sha256 {back[:16]} matches what was found")

    print(f"\n  {red} of {len(MUTATIONS)} mutations turn the guard RED")
    print("=" * 78)
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
