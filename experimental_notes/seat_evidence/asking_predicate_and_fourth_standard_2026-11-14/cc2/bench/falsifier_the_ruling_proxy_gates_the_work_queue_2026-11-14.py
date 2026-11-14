# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5fb9726d853041e67b0e4e6d2807814b736da4c3ae11e26a627313e5f07dc614
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for the CRITICAL finding of 2026-11-14.

CLAIM UNDER TEST (brief fact F5): "A is noisy in the SAFE direction: it
over-reports what he owes, and he can see and dismiss a wrong entry but cannot
see an absent one."

THE DEFECT CLAIMED: F5 is true of the `[tasks]` BANNER and FALSE of a second
consumer. `classify_text`'s `kind` is also read by
`hooks/work_not_narrate._first_movable`, which SKIPS an entry when
kind == "OWED". On that surface an over-report does not add a visible item -- it
REMOVES an entry from the session's own work queue, invisibly. So "over-reporting
is safe" is not a property of the predicate; it is a property of a predicate
paired with a consumer, and this proxy has 2 consumers that read it with
opposite sign.

HOW IT IS DEMONSTRATED, through the REAL modules and the REAL hook:
  1. import the real classifier and the real `work_not_narrate`;
  2. record the entry the real `_first_movable` names under the live predicate A;
  3. relax predicate A to False on the undecidable entries -- the change B or C
     would make -- by patching the classifier FILE on disk, because
     `_first_movable` reloads it from disk by path and cannot be monkeypatched
     in memory;
  4. call the real `_first_movable` again.
If the named entry CHANGES, the proxy gates the work queue and the defect is
real. If it does not change, the proxy cannot reach that surface and the claim
is refuted.

FAILS IFF THE DEFECT IS PRESENT: prints FALSIFIED and raises AssertionError when
the named entry moves; exits cleanly when it does not.

The patched file is restored and the restoration is verified by sha256 before
the verdict is printed, so a crash cannot leave the tree altered.
"""
import hashlib
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve()
REPO = pathlib.Path.cwd()
CLF = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


original = CLF.read_bytes()
digest_before = hashlib.sha256(original).hexdigest()
print(f"target: {CLF}")
print(f"sha256 before: {digest_before[:16]}")

wnn = load("_wnn_f", REPO / "hooks" / "work_not_narrate.py")
wnn.TASKS = LIST
wnn.MARKERS = REPO / "scripts"
sys.path.insert(0, str(REPO / "scripts"))
import task_list_markers as tlm                                  # noqa: E402

opens = [e for e in tlm.parse_entries(LIST) if (e.state or "").upper() == "OPEN"]
clf = load("_clf_f", CLF)
bodies = clf.bodies()
undecidable = [e.ident for e in opens
               if clf.classify_text(e.state, e.ruled,
                                    bodies.get(e.ident, ""))["residue_undecidable"]]
print(f"OPEN entries: {len(opens)}")
print(f"entries the 3 predicates cannot decide: {undecidable}")

named_A = wnn._first_movable(opens)
print(f"entry the REAL Stop gate names under live predicate A: {named_A!r}")

named_relaxed = None
try:
    # Relax A to B's verdict: a later date must be IN the asking sentence.
    src = original.decode()
    old = "    return bool(ruled) and any(d > ruled for d in _DATED_IN_BODY.findall(body))"
    assert src.count(old) == 1, "falsifier could not find residue_A's body"
    new = ("    if not ruled:\n"
           "        return False\n"
           "    return any(any(d > ruled for d in _DATED_IN_BODY.findall(s))\n"
           "               for s in live_asks)")
    CLF.write_text(src.replace(old, new, 1))
    named_relaxed = wnn._first_movable(opens)
finally:
    CLF.write_bytes(original)
    digest_after = hashlib.sha256(CLF.read_bytes()).hexdigest()
    assert digest_after == digest_before, "RESTORATION FAILED -- tree is altered"
    print(f"sha256 after restore: {digest_after[:16]}  RESTORED OK")

print(f"entry the REAL Stop gate names with A relaxed to B: {named_relaxed!r}")

if named_relaxed != named_A:
    print()
    print("FALSIFIED")
    print(f"  The proxy GATES THE WORK QUEUE. Changing only the ruling-residue")
    print(f"  predicate moved the entry the Stop gate names from {named_A!r} to")
    print(f"  {named_relaxed!r}. The {len(undecidable)} entries A marks OWED are")
    print(f"  excluded from naming by hooks/work_not_narrate.py:805, and that")
    print(f"  exclusion is INVISIBLE to the founder -- the opposite direction")
    print(f"  from the banner, where F5's reasoning holds. F5 is therefore true")
    print(f"  of one surface and false of another.")
    raise AssertionError(
        f"over-reporting is NOT uniformly safe: the named work entry moved "
        f"{named_A!r} -> {named_relaxed!r} on a change to the proxy alone")

print()
print("not demonstrated: the named entry did not move, so on this corpus the")
print("proxy does not reach the work-queue surface and F5's claim survives.")
