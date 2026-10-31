#!/usr/bin/env python3
"""Mutation harness for the `ds` vocabulary work of 2026-10-30.

A guard that passes proves nothing on its own; what it must do is FAIL when the
thing it guards is broken. This reverts each change made on 2026-10-30 in turn
and requires `bench/tests/test_the_ds_kind_is_confined_to_his_annotations_2026-10-30.py`
to go red for every one of them. The 10-of-10 figure quoted beside that work is
produced here rather than asserted, per `measured-rate-travels-with-its-script`.

★ IT FOUND 2 HOLLOW ASSERTIONS OF MY OWN, which is the reason to run it rather
than to trust the guard. On the first pass 8 of 10 mutations went red and 2
SURVIVED:

  M5, deleting the chat exclusion, survived because `MARKER` does not list `ds`,
  so `marked_kind` returns None whatever the exclusion does. The test was
  asserting MARKER's accidental silence, not the exclusion.

  M6, reverting the allow-list to its hand-written ("fr", "pf", "qs") tuple,
  survived because the test RESTATED the allow-list expression instead of
  calling `from_responses`. A reimplementation agrees with itself -- which is
  `execute-do-not-grep` broken by the test rather than by the product.

Both were replaced with tests that reach the real code path, and all 10 then
went red. The harness restores every file it touches, including on failure.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = ("bench/tests/"
         "test_the_ds_kind_is_confined_to_his_annotations_2026-10-30.py")

#: (name, file, the live text, what to revert it to). Each reverts exactly 1 of
#: the 2026-10-30 changes.
MUTATIONS = [
    ("M1 disc dropped from KINDS", "bench/ticket_store.py",
     'KINDS = ("fr", "pf", "qs", "wr", "disc", "dis", "ds")',
     'KINDS = ("fr", "pf", "qs", "wr", "dis", "ds")'),
    ("M1b legacy ds dropped, orphaning 93 rows", "bench/ticket_store.py",
     'KINDS = ("fr", "pf", "qs", "wr", "disc", "dis", "ds")',
     'KINDS = ("fr", "pf", "qs", "wr", "disc", "dis")'),
    ("M1c legacy dis dropped, orphaning 93 rows", "bench/ticket_store.py",
     'KINDS = ("fr", "pf", "qs", "wr", "disc", "dis", "ds")',
     'KINDS = ("fr", "pf", "qs", "wr", "disc", "ds")'),
    ("M1d the alias map emptied", "bench/ticket_store.py",
     'LEGACY_KIND_ALIASES = {"ds": "disc", "dis": "disc"}',
     'LEGACY_KIND_ALIASES = {}'),
    ("M1e the alias map CHAINS instead of pointing flat",
     "bench/ticket_store.py",
     'LEGACY_KIND_ALIASES = {"ds": "disc", "dis": "disc"}',
     'LEGACY_KIND_ALIASES = {"ds": "dis", "dis": "disc"}'),
    ("M11 legacy spellings no longer normalise",
     "scripts/read_founder_responses_2026-10-11.py",
     '    found = [_LEGACY_MARKERS.get(x, x) for x in found]', '    pass'),
    ("M11b the own-line reader cannot see `disc`",
     "scripts/read_founder_responses_2026-10-11.py",
     r'    r"^\s*(fr|pf|qs|wr|disc|dis|ds)(?:\s*,\s*(?:fr|pf|qs|wr|disc|dis|ds))*\s*$", re.I)',
     r'    r"^\s*(fr|pf|qs|wr|dis|ds)(?:\s*,\s*(?:fr|pf|qs|wr|dis|ds))*\s*$", re.I)'),
    ("M12 deferral visible only when OPEN", "bench/ticket_store.py",
     '        return [t for t in self._by_tid.values()\n'
     '                if t.status in LIVE and t.deferred and not t.blocker]',
     '        return [t for t in self.open_tickets()\n'
     '                if t.deferred and not t.blocker]'),
    ("M13 deferral reported whatever the status", "bench/ticket_store.py",
     '        return [t for t in self._by_tid.values()\n'
     '                if t.status in LIVE and t.deferred and not t.blocker]',
     '        return [t for t in self._by_tid.values()\n'
     '                if t.deferred and not t.blocker]'),
    ("M2 default back to pf", "scripts/harvest_tickets_2026-10-17.py",
     '    return "qs" if str(text).rstrip().endswith("?") else "disc"',
     '    return "pf"'),
    ("M3 question-mark half removed", "scripts/harvest_tickets_2026-10-17.py",
     '    return "qs" if str(text).rstrip().endswith("?") else "disc"',
     '    return "disc"'),
    ("M4 seat guard removed", "scripts/read_founder_responses_2026-10-11.py",
     '    if found == ["ds"] and _SEAT_BEFORE.search(body[:m.start(1)]):\n'
     '        return ""\n', ''),
    ("M5 chat exclusion removed", "scripts/harvest_tickets_2026-10-17.py",
     '    return None if k in CHAT_EXCLUDED_KINDS else k', '    return k'),
    ("M5b only the legacy spellings excluded, `disc` raisable from chat",
     "scripts/harvest_tickets_2026-10-17.py",
     'CHAT_EXCLUDED_KINDS = ("disc", "dis", "ds")   # `disc` live; 2 legacy spellings',
     'CHAT_EXCLUDED_KINDS = ("dis", "ds")'),
    ("M6 allow-list back to the hand tuple",
     "scripts/harvest_tickets_2026-10-17.py",
     '        _mk = _mk if _mk in KINDS else (marked_kind(txt) or "")',
     '        _mk = _mk if _mk in ("fr", "pf", "qs") else (marked_kind(txt) or "")'),
    ("M7 epoch lowered", "bench/ticket_store.py",
     'STORE_EPOCH = "2026-10-17"', 'STORE_EPOCH = "2026-10-01"'),
    ("M8 floor clamp removed", "scripts/harvest_tickets_2026-10-17.py",
     '    if a.since < STORE_EPOCH:', '    if False:'),
    ("M9 undeprecate status guard removed", "bench/ticket_store.py",
     '        if t.status != "DEPRECATED":', '        if False:'),
    ("M10 register --kind hand tuple", "scripts/register.py",
     '    p.add_argument("--kind", choices=KINDS,  # the vocabulary, never a copy',
     '    p.add_argument("--kind", choices=("fr", "pf", "qs", "wr"),'),
]


def main() -> int:
    red = skipped = 0
    for name, rel, live, reverted in MUTATIONS:
        path = REPO / rel
        original = path.read_text()
        if original.count(live) != 1:
            print(f"  {name}: PATTERN NOT UNIQUE ({original.count(live)}) "
                  "-- the live code has moved; this mutation is STALE")
            skipped += 1
            continue
        path.write_text(original.replace(live, reverted))
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", GUARD, "-q", "--no-header", "-x"],
                capture_output=True, text=True, cwd=str(REPO), timeout=600)
            tail = [l for l in r.stdout.splitlines()
                    if "passed" in l or "failed" in l or "error" in l]
            if r.returncode != 0:
                red += 1
                print(f"  {name}: RED :: {tail[-1] if tail else ''}")
            else:
                print(f"  {name}: GREEN -- MUTATION SURVIVED, the guard is "
                      f"hollow here :: {tail[-1] if tail else ''}")
        finally:
            path.write_text(original)
    live_count = len(MUTATIONS) - skipped
    print(f"\n{red} of {live_count} live mutations turned the guard red "
          f"({skipped} stale)")
    return 0 if red == live_count and live_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
