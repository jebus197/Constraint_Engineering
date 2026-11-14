#!/usr/bin/env python3
"""Does the decision-delivery guard fail when any of the 4 gates is reverted?

Entry B175 was invisible to the founder through 4 independent gates. This
harness reverts each and requires
`bench/tests/test_a_decision_reaches_the_file_he_reads_2026-11-14.py` to go RED.

★ 2 SUBJECTS, 1 CODE AND 1 DATA FILE, and both restore from bytes captured
before the first mutation -- never with `git checkout --`, which in this project
once ate the file under test. The restore is verified by SHA-256.

★ THE DATA MUTATIONS MATTER MOST. 3 of the 4 gates were not code at all: a
suppression flag, a title convention and a stale record. A harness that only
mutated code would leave 3 of 4 gates unverified.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DECIDE = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
GUARD = (REPO / "bench" / "tests"
         / "test_a_decision_reaches_the_file_he_reads_2026-11-14.py")


def _run_guard() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


# ---- code mutations: (label, old, new) against DECIDE
CODE_MUTATIONS = [
    ("G1 the bare possessive form is not recognised",
     "            if not _BARE_POSSESSIVE_ASK.search(sent):\n                continue",
     "            if True:\n                continue"),
    ("G1b the decision-noun requirement is dropped, so any 'is his' counts",
     'r"\\b(?:redesign|decision|choice|call|change|move|cut|level|mapping|question|"\n'
     '    r"ruling|trade|verdict|promotion|wording)\\s+(?:is|are|remains)\\s+(?:his|yours)\\b",',
     'r"(?:is|are|remains)\\s+(?:his|yours)\\b",'),
    ("G1c the other-entry exclusion is removed, re-admitting the false positive",
     "            if _others:\n                continue",
     "            if False:\n                continue"),
]


def _mutate_detail(kind: str, data: dict) -> dict:
    """Return a COPY of the authored detail with one gate reverted."""
    d = json.loads(json.dumps(data))
    if kind == "G2 the suppression flag comes back with its self-contradicting text":
        d["task:B175"]["no_ruling_needed"] = (
            "The 2 writes are mine to fix and the seam is already prepared. "
            "Only the 17-minute redesign is his, because it changes what a test asserts.")
    elif kind == "G3 a title stops starting with its own entry code":
        t = d["task:B175"]["title"]
        d["task:B175"]["title"] = t.split(" - ", 1)[1] if " - " in t else "the clean suite"
    elif kind == "G4 a closed entry keeps its authored detail":
        d["task:B183"] = {"title": "B183 - a closed entry that kept its detail",
                          "what": "x", "why": "y", "evidence_line": "z",
                          "options": ["a", "b"], "recommendation_standards": "s",
                          "no_ruling_needed": True}
    else:
        raise AssertionError(kind)
    return d


DATA_MUTATIONS = [
    "G2 the suppression flag comes back with its self-contradicting text",
    "G3 a title stops starting with its own entry code",
    "G4 a closed entry keeps its authored detail",
]


def main() -> int:
    code0 = DECIDE.read_bytes()
    data0 = DETAIL.read_bytes()
    shas = {DECIDE: hashlib.sha256(code0).hexdigest(),
            DETAIL: hashlib.sha256(data0).hexdigest()}
    code_text = code0.decode("utf-8")
    data_obj = json.loads(data0.decode("utf-8"))

    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation.")
        return 2

    red = misses = probe = 0
    total = len(CODE_MUTATIONS) + len(DATA_MUTATIONS)
    try:
        for label, old, new in CODE_MUTATIONS:
            if old not in code_text:
                probe += 1
                print(f"  [PROBE FAILED] {label}: anchor absent.")
                continue
            DECIDE.write_text(code_text.replace(old, new, 1), encoding="utf-8")
            if DECIDE.read_bytes() == code0:
                probe += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged.")
                DECIDE.write_bytes(code0)
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}")
            else:
                red += 1
                print(f"  [RED]   {label}")
            DECIDE.write_bytes(code0)

        for label in DATA_MUTATIONS:
            DETAIL.write_text(
                json.dumps(_mutate_detail(label, data_obj), indent=2,
                           sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8")
            if DETAIL.read_bytes() == data0:
                probe += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged.")
                DETAIL.write_bytes(data0)
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}")
            else:
                red += 1
                print(f"  [RED]   {label}")
            DETAIL.write_bytes(data0)
    finally:
        DECIDE.write_bytes(code0)
        DETAIL.write_bytes(data0)

    ok = all(hashlib.sha256(p.read_bytes()).hexdigest() == s for p, s in shas.items())
    print(f"\n  both subjects restored, SHA-256 verified: {ok}")
    print(f"  {red} of {total} mutations turned the guard RED; "
          f"{misses} MISS; {probe} probe failure(s)")
    if not ok:
        print("  RESTORE FAILED.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probe == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
