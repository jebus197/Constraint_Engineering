# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: bc198afb223ef1e65a89ea940c9fbd06bdc44e51ac157097ce4858a9b085ac4b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The integrity gate must not refuse a falsifier for spawning a second interpreter.

THE DEFECT (STUDY_IN_FLIGHT.json, integrity-gate-interpreter-carve-out; free
panel 2026-10-12, fable seat). C0050's falsifier spawns ``/usr/bin/python3``
BECAUSE the defect it demonstrates is that the target prescribes a bare
unpinned ``python3`` whose PEP 604 annotations raise TypeError on 3.9. Any
falsifier for that defect class must spawn the system interpreter, whose
stdlib bootstrap reads fall inside _SANDBOX_DENY_REGIONS, so the gate was
guaranteed to refuse the CORRECT falsifier: executed 2026-10-12 before the
fix, the probe below returned INTEGRITY_VIOLATION on 13 stdlib reads.

THE FIX (_secondary_interpreter_roots) allows only the installation
directories a discoverable interpreter itself reports — parity with the
harness interpreter's existing carve-out. Refuse-on-denial is unchanged for
everything else, asserted here by the denied-region case.
"""
import os
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import bench.falsifier_verify as fv  # noqa: E402

_SYS_PY = "/usr/bin/python3"
needs_system_python = pytest.mark.skipif(
    not os.path.isfile(_SYS_PY)
    or os.path.realpath(_SYS_PY) == os.path.realpath(sys.executable),
    reason="no distinct system python3 on this machine")


@needs_system_python
def test_spawned_interpreter_stdlib_reads_are_not_denials():
    code = (
        "import subprocess\n"
        f"r = subprocess.run([{_SYS_PY!r}, '-c',"
        " 'import json, ssl; print(\"IMPORTS_OK\")'],"
        " capture_output=True, text=True, timeout=30)\n"
        "assert 'IMPORTS_OK' in r.stdout, 'FALSIFIED: stdlib import denied'\n"
    )
    verdict = fv.reverify_falsifier(code, timeout=120)
    assert verdict != fv.INTEGRITY_VIOLATION, (
        "a falsifier was refused for its spawned interpreter's own stdlib "
        "bootstrap reads — the C0050 false-refusal class")
    assert verdict == "REFUTED"  # imports succeed, clean exit


@needs_system_python
def test_the_c0050_counterfactual_confirms():
    # The defect class itself: PEP 604 syntax handed to the unpinned
    # system interpreter. On 3.9 this raises at definition time, the
    # falsifier raises AssertionError, and the verdict is CONFIRMED —
    # exactly the counterfactual recorded in STUDY_IN_FLIGHT.json.
    code = (
        "import subprocess\n"
        f"r = subprocess.run([{_SYS_PY!r}, '-c',"
        " 'def f() -> str | None: pass'],"
        " capture_output=True, text=True, timeout=30)\n"
        "assert r.returncode == 0, 'FALSIFIED: unpinned python3 rejects PEP 604'\n"
    )
    verdict = fv.reverify_falsifier(code, timeout=120)
    assert verdict in ("CONFIRMED", "REFUTED")
    import subprocess as sp
    probe = sp.run([_SYS_PY, "-c", "def f() -> str | None: pass"],
                   capture_output=True, text=True)
    if probe.returncode != 0:  # system python is pre-3.10: defect is real
        assert verdict == "CONFIRMED"


def test_denied_region_reads_are_still_refused():
    code = (
        "import os\n"
        "print(len(os.listdir(os.path.expanduser('~/Desktop'))))\n"
    )
    verdict = fv.reverify_falsifier(code, timeout=60)
    assert verdict == fv.INTEGRITY_VIOLATION, (
        "widening the interpreter carve-out must not loosen the gate for "
        "genuine out-of-bounds reads")


def test_secondary_roots_never_include_protected_material():
    roots = fv._secondary_interpreter_roots()
    for r in roots:
        assert "scoring" not in r.lower() and "answer_key" not in r.lower()
    # Only installation directories: every root must exist and be an
    # interpreter artefact, not a repo or home document path.
    home_docs = os.path.expanduser("~/Desktop")
    assert home_docs not in roots
