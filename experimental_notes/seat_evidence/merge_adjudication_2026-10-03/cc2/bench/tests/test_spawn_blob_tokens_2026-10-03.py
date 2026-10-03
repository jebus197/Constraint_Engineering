# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'merge_adjudication_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 08e97ab4c5aa85de11a465792f62ddf90539283d64da98bbcfe3ae33e7710af7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The spawn hook tests every path the command line carries (STAR 2026-10-03).

Under shell=True the audit-hook blob IS the command line, so the whole-blob
checks (`_resolve(text)` / `_looks_home_rooted(text)`) could not see a path
embedded after a command word. Demonstrated in this tree before the fix:

    subprocess.run('cat ' + os.environ['HOME'] + '/<file>', shell=True)
      -> spawn ALLOWED (falsifier verdict CONFIRMED on 'the spawn was allowed')
    subprocess.run(['cat', same_path])
      -> INTEGRITY_VIOLATION

First reported by cc2 (blind round 2, 2026-10-02); independently reproduced
and fixed here with a per-token pass in the observer source. These guards pin
both directions: the embedded path is refused, and honest spawn shapes carry
zero false refusals.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.falsifier_verify import reverify_falsifier  # noqa: E402

GATE_REFUSAL = "INTEGRITY_VIOLATION"


def _run(code: str) -> str:
    return reverify_falsifier(code, repo_root=str(ROOT))


def test_env_rooted_path_in_a_shell_blob_is_refused():
    code = (
        "import os, subprocess\n"
        "p = os.path.join(os.environ.get('HOME', '/tmp'),"
        " 'nonexistent_probe_key_d4.json')\n"
        "r = subprocess.run('cat ' + p, shell=True, capture_output=True)\n"
        "raise AssertionError('FALSIFIED: the spawn was allowed')\n"
    )
    assert _run(code) == GATE_REFUSAL


def test_the_list_form_standard_is_unchanged():
    code = (
        "import os, subprocess\n"
        "p = os.path.join(os.environ.get('HOME', '/tmp'),"
        " 'nonexistent_probe_key_d4.json')\n"
        "r = subprocess.run(['cat', p], capture_output=True)\n"
        "raise AssertionError('FALSIFIED: the spawn was allowed')\n"
    )
    assert _run(code) == GATE_REFUSAL


@pytest.mark.parametrize("code", [
    "import subprocess; r=subprocess.run('echo ok', shell=True,"
    " capture_output=True); assert r.returncode==0",
    "import subprocess; r=subprocess.run('ls /tmp', shell=True,"
    " capture_output=True); assert r.returncode==0",
    "import subprocess; r=subprocess.run('echo a | wc -l', shell=True,"
    " capture_output=True); assert r.returncode==0",
    "import subprocess,sys; r=subprocess.run([sys.executable,'-c','print(1)'],"
    "capture_output=True); assert r.returncode==0",
])
def test_honest_spawn_shapes_are_not_refused(code):
    # Clean execution reads REFUTED (no defect demonstrated); the property
    # pinned here is the ABSENCE of a gate refusal.
    assert _run(code) != GATE_REFUSAL
