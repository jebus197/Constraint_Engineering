#!/usr/bin/env python3
"""Does the B196 exempt-span guard fail when the repair is reverted?

A guard that passes on broken code guards nothing. This harness reverts the
repair 5 distinct ways and requires `bench/tests/
test_an_exempt_span_covers_only_quotation_2026-11-14.py` to go RED each time.

★ MUTATION 1 IS THE ACTUAL HISTORICAL DEFECT, not an invented one: the span
opened before the outstanding-work loop and closed after it, so the exemption
meant for each headline covered the authored `what` and `why` too. It is
reproduced here exactly, because a harness whose mutations are all invented
cannot show the guard would have caught what happened.

★ EVERY MUTATION IS VERIFIED TO HAVE CHANGED THE FILE. An edit whose anchor has
moved leaves the subject intact, the guard passes, and the harness would report
that as a MISS -- a false alarm about the guard when the fault is the probe.

★ THE SUBJECT IS RESTORED FROM BYTES CAPTURED BEFORE THE FIRST MUTATION, never
with `git checkout --`, which in this project once ate the file under test, and
the restore is verified by comparing bytes because a restore is a mutation too.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "morning_report_build_2026-10-12.py"
GUARD = (REPO / "bench" / "tests"
         / "test_an_exempt_span_covers_only_quotation_2026-11-14.py")

PER_ITER = """    for o in outstanding:
        _s = len(L)                  # task-list headlines, as the markers carry them
        A(_spoken(o.get("title") or o["ident"]) + ".")
        _ex.append((_s, len(L)))     # the headline ONLY, never the prose below it
        A("")"""

#: (label, old, new). Each must change the file.
MUTATIONS = [
    ("THE HISTORICAL DEFECT: span opens before the loop, closes after it",
     PER_ITER,
     """    _s = len(L)
    for o in outstanding:
        A(_spoken(o.get("title") or o["ident"]) + ".")
        A("")"""),
    ("the span is closed after the whole loop as well",
     '    A(f"SECTION 4. EXPLANATIONS OWED, {len(owed)} OF THEM")',
     '    _ex.append((0, len(L)))\n    A(f"SECTION 4. EXPLANATIONS OWED, {len(owed)} OF THEM")'),
    ("the headline span is widened by 1 further emission",
     PER_ITER,
     """    for o in outstanding:
        _s = len(L)                  # task-list headlines, as the markers carry them
        A(_spoken(o.get("title") or o["ident"]) + ".")
        A("")
        A(_spoken(o.get("why", "")))
        _ex.append((_s, len(L)))"""),
    ("no span is recorded at all",
     PER_ITER,
     """    for o in outstanding:
        _s = len(L)                  # task-list headlines, as the markers carry them
        A(_spoken(o.get("title") or o["ident"]) + ".")
        A("")"""),
    ("every span is recorded empty",
     "        _ex.append((_s, len(L)))     # the headline ONLY, never the prose below it",
     "        _ex.append((_s, _s))"),
]


def _run_guard() -> bool:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
        cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main(argv=None) -> int:
    original = SUBJECT.read_bytes()
    text = original.decode("utf-8")

    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation. Fix that first; a "
              "harness cannot tell a mutation from a pre-existing failure.")
        return 2

    red = misses = probe_failures = 0
    try:
        for label, old, new in MUTATIONS:
            if old not in text:
                probe_failures += 1
                print(f"  [PROBE FAILED] {label}: anchor absent, nothing mutated. "
                      f"The probe is stale, not the guard.")
                continue
            SUBJECT.write_text(text.replace(old, new, 1), encoding="utf-8")
            if SUBJECT.read_bytes() == original:
                probe_failures += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged after the edit.")
                SUBJECT.write_bytes(original)
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}: guard stayed GREEN with the repair reverted.")
            else:
                red += 1
                print(f"  [RED]   {label}")
            SUBJECT.write_bytes(original)
    finally:
        SUBJECT.write_bytes(original)

    restored = SUBJECT.read_bytes() == original
    print(f"\n  subject restored byte-for-byte: {restored}")
    n = len(MUTATIONS)
    print(f"  {red} of {n} mutations turned the guard RED; "
          f"{misses} MISS; {probe_failures} probe failure(s)")
    if not restored:
        print("  RESTORE FAILED — the subject is not what it was.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probe_failures == 0) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
