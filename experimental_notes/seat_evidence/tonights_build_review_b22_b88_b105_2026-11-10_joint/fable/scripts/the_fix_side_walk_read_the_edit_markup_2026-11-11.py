# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cd0e2cd289ff082000b3f4522e19c1b1656b4a051e65fd9c3bf9247ada4aaa41
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The fix-side walk read the edit MARKUP, not what the fix makes the document say.

JOINT ROUND `tonights_build_review_b22_b88_b105_2026-11-10`, seat fable,
2026-11-11. The 2026-11-11 closure of the unexamined-fix hole runs the topic's
tools over `finding.proposed_fix` RAW. On the live promote path
(`reference_runner_v3._apply_back_promote`) that field is ALWAYS search/replace
blocks -- `no_parseable_block` is refused before the gate is consulted -- so the
tools reduced the SEARCH half (text the fix REMOVES) and the delimiters.

Decided by execution against `_apply_back_gate`, the real gate:
  P1  THE CANONICAL CORRECTION REFUSED (inert on the shape B88 admits):
      SEARCH carries the FALSE formula, REPLACE the TRUE one. The tool
      reduces the false half -> REJECTED -> definitive_against -> refuse.
  P2  A DELETION OF A TRUE STATEMENT ADMITTED: the true claim sits only in
      the SEARCH half -- text the fix destroys -- and verifies.
Exit 1 printing FALSIFIED while either defect is present; exit 0 when clean.

DECLARED RESIDUE, NOT DECIDED HERE: a REPLACE side that carries an unexamined
payload plus a true computable rider still admits (demonstrated the same day).
That is structural to any text-scoped admission -- the predicate is an
existential over reducible fragments -- and WHICH residues escalate is a
scoping ruling for the founder, the same route the original exploit took.
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "bench"))
import bench.reference_runner_v3 as rr

TRUE_C = "the molecule 'CCO' has formula C2H6O"
FALSE_C = "the molecule 'CCO' has formula C3H8O"
bad = 0

sr_correct = ("<<<< SEARCH notes/thing.md\n" + FALSE_C + "\n====\n" + TRUE_C
              + "\n>>>> REPLACE")
ok, why = rr._apply_back_gate("repaired prose", "notes/thing.md", "",
    finding={"description": TRUE_C, "proposed_fix": sr_correct},
    domain="chemistry")
print(f"P1 canonical correction admits: {ok}  ({why[:120]})")
if not ok:
    bad += 1

sr_delete = ("<<<< SEARCH notes/thing.md\n" + TRUE_C + "\n====\n>>>> REPLACE")
ok2, why2 = rr._apply_back_gate("repaired prose", "notes/thing.md", "",
    finding={"description": TRUE_C, "proposed_fix": sr_delete},
    domain="chemistry")
print(f"P2 deletion-of-the-truth admits: {ok2}  ({why2[:120]})")
if ok2:
    bad += 1

if bad:
    print("FALSIFIED")
    sys.exit(1)
print("CLEAN")
