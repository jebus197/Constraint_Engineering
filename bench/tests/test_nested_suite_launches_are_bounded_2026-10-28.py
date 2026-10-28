# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fix_review_panel_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2471501fd68a8356e72f1b9e89c696f90bd200878b33dbe8ff8cca1d2c2742b3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Every subprocess launch in the nested precommit tests carries a timeout.

Panel falsifier, 2026-10-28 (B37). The committed producer
`scripts/the_nested_suite_is_bounded_not_serial_2026-10-28.py` refuted the
serialisation hypothesis (both runs are already serial) and counted 13 of 22
launches with no timeout in test_precommit_restages_repairs_2026-09-11.py.
An unbounded child that wedges presents as the deadlock B37 reports: the
per-test timeout (method=thread) then kills the outer pytest process while
the inner pytest/git tree runs on as an orphan, keeping an 8 GiB machine
choked. A hang must FAIL, not hang -- the property the sibling file
test_precommit_guard_2026-09-09.py states for its own _COMMIT_TIMEOUT.
"""
import ast
from pathlib import Path

FILES = [
    "test_precommit_guard_2026-09-09.py",
    "test_precommit_gate_cost_2026-09-10.py",
    "test_precommit_restages_repairs_2026-09-11.py",
]

def _unbounded(path: Path) -> list:
    tree = ast.parse(path.read_text())
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("run", "check_output", "check_call", "call")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and not any(k.arg == "timeout" for k in node.keywords)):
            out.append(node.lineno)
    return out

def test_every_subprocess_launch_in_the_nested_tests_is_bounded():
    here = Path(__file__).resolve().parent
    offenders = {f: _unbounded(here / f) for f in FILES}
    offenders = {f: ls for f, ls in offenders.items() if ls}
    assert not offenders, (
        "unbounded subprocess launches in nested precommit tests "
        f"(a wedged child reads as B37's deadlock): {offenders}")
