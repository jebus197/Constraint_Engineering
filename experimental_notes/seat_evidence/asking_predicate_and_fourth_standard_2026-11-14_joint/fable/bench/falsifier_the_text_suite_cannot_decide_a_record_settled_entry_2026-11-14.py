# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6809cb9aae048e780cbba9b2d9e34c40ecf5923f514ae038e3c16ae6d882e885
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: the live classifier misreads a record-settled entry, so a
text-only fix (O3 extended to the gate, with any of predicates A-D deciding)
cannot converge: each future ruling on an asked entry joins the undecidable
set, and only a recorded raise date retires the question.

Imports the REAL `classify_text` from
scripts/how_many_decisions_actually_need_him_2026-11-01.py -- nothing retyped.

Fails IFF the defect is present:
  - raises AssertionError / prints FALSIFIED when the real classifier returns
    OWED for an entry whose own raise record shows the ask PREDATES the ruling
    (the ruling answered it), while its siblings disagree;
  - exits CLEAN if the classifier decides the probe correctly (GRANTED), which
    would REFUTE the joint-round recommendation of composing the record stamp
    with the reported-disagreement fix.
Controls run first; a control failure exits 2 (UNTOOLABLE), never FALSIFIED.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "_clf_f", REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py")
clf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clf)

# CONTROL 1: ruled, asked before, NO later date -> the ladder itself says GRANTED.
c1 = clf.classify_text("OPEN", "2026-11-20",
                       "Whether to keep the ceiling NEEDS YOUR RULING, "
                       "raised:2026-11-18.")
# CONTROL 2: never ruled, live ask -> OWED.
c2 = clf.classify_text("OPEN", None,
                       "Whether to keep the ceiling NEEDS YOUR RULING.")
if c1["kind"] != "GRANTED" or c2["kind"] != "OWED":
    print(f"controls failed: c1={c1['kind']} c2={c2['kind']} -- UNTOOLABLE")
    sys.exit(2)
print(f"controls passed: settled-> {c1['kind']}, unruled ask-> {c2['kind']}")

# PROBE: the ask's own raise record (2026-11-18) PREDATES the ruling
# (2026-11-20); the only later date (2026-11-21) is a progress note asking
# nothing. By record this entry is settled. What does the live text suite say?
probe = ("Progress 2026-11-21: measured, committed, no question. "
         "Whether the gate also skips DEFERRED entries NEEDS YOUR "
         "RULING, raised:2026-11-18.")
a = clf.classify_text("OPEN", "2026-11-20", probe)
print(f"probe: real classify_text kind = {a['kind']}")

assert a["kind"] != "OWED", (
    "FALSIFIED: predicate A (`_later`, any body date later than the ruling) "
    "holds a record-settled entry at OWED on the strength of a dated progress "
    "note. On the banner this inflates the count he reads; at "
    "work_not_narrate._first_movable (`if kind == \"OWED\" ... continue`) it "
    "silently removes the entry from the work the stop gate names. No text "
    "predicate in the measured suite (A, B, C, or D nearest-preceding-date) "
    "decides this case; the raise record does."
)
print("clean exit: the classifier decided the record-settled probe correctly, "
      "which refutes the joint-round ground for composing the raise record "
      "with the reported-disagreement fix.")
