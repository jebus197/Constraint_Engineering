#!/usr/bin/env python3
"""Mutate the mid-turn predicate and require its guard to go RED each time.

THE SUBJECT IS A LIVE HOOK THAT SHARES AN INODE with `~/.claude/hooks/`, so a
mutation here changes the gate THIS SESSION runs. Every mutation is reverted
immediately after its board, and both the per-mutation revert and the final
restore are verified by sha256 -- a failed restore would leave the session's own
Stop gate broken, which is a worse outcome than any finding this harness could
produce.

ANCHORS ARE DERIVED FROM THE SUBJECT: each mutation asserts its substring occurs
EXACTLY ONCE and reports an ANCHOR MISS otherwise, so a refactor makes this
harness complain rather than silently mutate nothing and report green.

THE EXPECTATION IS NOT PER-TEST. The harness never names the test that should
fail; it requires red and REPORTS what failed.

Run: python3 scripts/the_mid_turn_predicate_mutations_2026-11-10.py
Exit 0 only when every mutation turns the guard red.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys


def _find_root() -> pathlib.Path:
    start = pathlib.Path(__file__).resolve().parent
    for cand in (start, *start.parents):
        if (cand / "bench" / "domain_immune.py").is_file():
            return cand
    raise SystemExit("cannot locate the repository")


ROOT = _find_root()
SUBJECT = ROOT / "hooks" / "work_not_narrate.py"
GUARD = ROOT / "bench" / "tests" / (
    "test_a_mid_turn_message_is_still_his_2026-11-10.py")

MUTATIONS = [
    ("M1  require type == 'user' again (the original defect)",
     '    if t == MIDTURN_ENTRY_TYPE:',
     '    if t == MIDTURN_ENTRY_TYPE and False:'),
    ("M2  accept ANY blob, marker unchecked",
     '        if MIDTURN_MARKER not in txt:\n            return None',
     '        if False:\n            return None'),
    ("M3  read every content block, tool_result included",
     '            if isinstance(x, dict) and x.get("type") == "text")',
     '            if isinstance(x, dict))'),
    ("M4  stop stripping the harness epilogue",
     '        after = after.split(MIDTURN_EPILOGUE, 1)[0]',
     '        after = after'),
    ("M5  prefilter narrows back to user lines only",
     "    if ('\"type\":\"user\"' not in line and '\"type\": \"user\"' not in line\n"
     "            and MIDTURN_MARKER not in line):\n        return False",
     "    if '\"type\":\"user\"' not in line and '\"type\": \"user\"' not in line:\n"
     "        return False"),
    # ★ M6's ANCHOR WAS NOT UNIQUE on the first attempt: the same line test
    # appears in `_turn_key` AND in `turn_signals`, so the harness reported an
    # ANCHOR MISS rather than mutating the wrong one silently -- which is the
    # behaviour a derived anchor is for. It is now anchored on the comment that
    # belongs to `_turn_key` alone.
    ("M6  the turn key stops seeing a mid-turn entry",
     "        #: ★ MID-TURN ENTRIES INCLUDED, 2026-11-10. The refusal BUDGET is keyed",
     "        continue\n        #: ★ MID-TURN ENTRIES INCLUDED, 2026-11-10. The refusal BUDGET is keyed"),
    ("M7  drop the system-reminder test from the mid-turn path",
     '        if not after or "<system-reminder>" in after:',
     '        if not after and False:'),
]


def run_guard() -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    return r.returncode, r.stdout + r.stderr


def failing(out: str) -> list[str]:
    return sorted({m for m in re.findall(r"^(?:FAILED|ERROR) (\S+)", out, re.M)})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)

    original = SUBJECT.read_text()
    sha = hashlib.sha256(original.encode()).hexdigest()
    print("=" * 78)
    print("MID-TURN PREDICATE MUTATION BOARD")
    print(f"  subject: {SUBJECT}  (shares an inode with the LIVE hook)")
    print("=" * 78)
    rc, out = run_guard()
    print(f"  baseline (unmutated)                                 exit={rc}  "
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
                print(f"  {label:52s}  ANCHOR MISS ({n} occurrences)")
                continue
            SUBJECT.write_text(original.replace(find, repl, 1))
            rc, out = run_guard()
            if rc == 0:
                print(f"  {label:52s}  exit=0  *** STILL GREEN ***")
            else:
                red += 1
                names = ", ".join(t.split("::")[-1] for t in failing(out)) \
                    or "collection error"
                print(f"  {label:52s}  exit={rc}  RED")
                print(f"       detected by: {names}")
            # revert IMMEDIATELY: this is the gate the session is running
            SUBJECT.write_text(original)
            assert hashlib.sha256(
                SUBJECT.read_text().encode()).hexdigest() == sha, \
                "per-mutation revert failed; the live gate is not as found"
    finally:
        SUBJECT.write_text(original)
        back = hashlib.sha256(SUBJECT.read_text().encode()).hexdigest()
        assert back == sha, "RESTORE FAILED -- the live Stop gate is damaged"
        print(f"\n  restored, sha256 {back[:16]} matches what was found")

    print(f"\n  {red} of {len(MUTATIONS)} mutations turn the guard RED")
    print("=" * 78)
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
