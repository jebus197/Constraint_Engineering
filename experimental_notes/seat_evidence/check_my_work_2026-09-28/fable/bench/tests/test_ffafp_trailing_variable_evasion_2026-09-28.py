# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 87ac382a7f1c171a645b2e58dab7568abde3894ca2a05665e470b995164ec5ec
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A variable AT OR AFTER the extension must not hide a write.

PANEL SEAT (fable), 2026-09-28, reviewing the unreviewed 2026-09-24 classifier
changes. The literal-prefix clause closed `bench/targets/exp$n.py` (variable in
the BASENAME, literal extension) but required the extension itself to be
literal. Appending a variable AFTER the extension put the `$` INSIDE what
`os.path.splitext` returns -- `.py$nope` -- so the clause declined and the path
fell to "unresolved", which every consumer excludes from the mutation set.

THE PREMISE THAT MADE "unresolved" SAFE IS FALSE FOR UNSET VARIABLES. The
2026-09-24 comment reasoned that a residual variable "does not persist into the
write's own shell, so the write it names did not land on any path". An UNSET
shell variable expands to the EMPTY STRING: executed on 2026-09-28,
`echo INJECTED > victim.py$NOPE_VAR` creates `victim.py`. So
`> bench/panel_sandbox.py$NOPE` was a REAL code write that the audit could not
see. The fix classifies the LITERAL PREFIX when it sits under a literal
directory: exact for the unset case, over-counting at worst otherwise, which is
the safe direction for a mutation guard.

Every case here is EXECUTED against the real module; the shell-semantics claim
is EXECUTED against a real shell.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _mod():
    spec = importlib.util.spec_from_file_location(
        "ffafp_audit_tve", ROOT / "hooks" / "ffafp_audit.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ffafp_audit_tve"] = m
    spec.loader.exec_module(m)
    return m


def test_an_unset_variable_expands_empty_so_the_write_lands_on_the_prefix(tmp_path):
    """The shell fact the whole finding rests on, executed rather than asserted."""
    r = subprocess.run(
        ["bash", "-c", "echo INJECTED > victim.py$NOPE_VAR_2026_09_28"],
        cwd=tmp_path, capture_output=True)
    assert r.returncode == 0
    assert (tmp_path / "victim.py").is_file(), "unset var did not expand empty?"


def test_a_variable_after_the_extension_no_longer_hides_a_code_write():
    fa = _mod()
    assert fa.classify_write("bench/panel_sandbox.py$NOPE_VAR", "") == "code"
    assert fa.classify_write("bench/panel_sandbox.py${NOPE_VAR}", "") == "code"


def test_an_extensionless_target_with_a_trailing_variable_is_counted():
    fa = _mod()
    # hooks/pre-commit is a real, extensionless, executable file in this repo.
    assert fa.classify_write("hooks/pre-commit$NOPE_VAR", "") == "other"


def test_the_prior_behaviour_is_unchanged_where_it_was_right():
    fa = _mod()
    assert fa.classify_write("bench/targets/exp$n.py", "") == "code"
    assert fa.classify_write("bench/logs/run_$STAMP/BRIEF.md", "") == "doc"
    assert fa.classify_write("$SP/gate_in.json", "") == "unresolved"
    assert fa.classify_write("/tmp/out_$N.log", "") == "transient"
    # A bare relative name with no literal directory stays undecidable.
    assert fa.classify_write("x.py$Z", "") == "unresolved"


def test_resolution_from_the_command_still_wins_over_the_prefix_rule():
    """`classify_write` resolves first; the prefix rule is the residual path."""
    fa = _mod()
    got = fa.classify_write("$SP/gate_in.json", "SP=/tmp/scratch; echo x > $SP/gate_in.json")
    assert got == "transient", got
