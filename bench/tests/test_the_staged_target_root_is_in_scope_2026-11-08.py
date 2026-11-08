"""The staged target root is the mandated location, not an escape. B82.

HIS RULING, 2026-11-08: allow-list the staged target root in the scope check.

THE DEFECT. A falsifier is REQUIRED by the design to work inside
``~/CDSFL_review_targets`` -- the runner stages the file under review there
precisely so the panel cannot reach the repository. The forensic scope check
built its allowlist as ``[str(run_dir), *rep.target_dirs]`` and that root was in
neither, so a path literal naming the one directory a falsifier must use was
recorded at the CONFIRMED tier as "out-of-scope path opened or listed". It fired
100 times.

WHY THIS IS A GUARD AND NOT JUST AN EDIT. Widening an allowlist is exactly the
change that can silently blind a security check, so the direction that matters
is not the one the fix was made for. ``bench/vault_keys.sh`` deliberately hides
a key store inside an otherwise-boring subtree, and if the staged root were
tested before ``protected`` then a key placed under it would become invisible.
The module already states that ``protected`` is tested FIRST; this file ASSERTS
it by calling ``_in_scope`` rather than trusting the comment, because a comment
cannot follow the code when it moves.

ALL 3 DIRECTIONS ARE EXECUTED, not described:
  1. a path under the staged root is IN scope -- the false positive is gone;
  2. a path outside both the staged root and the repository is STILL refused --
     the check has not been turned off;
  3. a PROTECTED key location under the staged root is STILL refused -- the
     widening did not create a false negative.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.key_access_forensics import _in_scope          # noqa: E402
from bench.falsifier_verify import STAGED_TARGET_ROOT      # noqa: E402


def test_the_staged_root_is_a_real_absolute_path():
    """If this constant moved, every case below would pass vacuously."""
    assert STAGED_TARGET_ROOT, "STAGED_TARGET_ROOT is empty"
    assert str(STAGED_TARGET_ROOT).startswith("/"), (
        f"STAGED_TARGET_ROOT is not expanded: {STAGED_TARGET_ROOT!r}")
    assert "CDSFL_review_targets" in str(STAGED_TARGET_ROOT)


def test_a_path_under_the_staged_root_is_in_scope():
    """DIRECTION 1. The false positive the ruling was about."""
    allow = ["/tmp/run-0", str(STAGED_TARGET_ROOT)]
    under = f"{STAGED_TARGET_ROOT}/current/target.md"
    assert _in_scope(under, allow, protected=()), (
        f"{under} is the mandated falsifier location and was refused")


def test_the_staged_root_is_refused_when_it_is_not_allow_listed():
    """ANTI-VACUITY. If _in_scope returned True for everything, direction 1
    would pass while testing nothing. Same literal, allowlist WITHOUT the root.
    """
    under = f"{STAGED_TARGET_ROOT}/current/target.md"
    assert not _in_scope(under, ["/tmp/run-0"], protected=()), (
        "_in_scope accepted a path under a root that was NOT allow-listed, so "
        "it is not consulting the allowlist and every case here is vacuous")


def test_a_path_outside_everything_is_still_refused():
    """DIRECTION 2. The check has not been turned off."""
    allow = ["/tmp/run-0", str(STAGED_TARGET_ROOT)]
    for bad in ("/etc/passwd",
                "/Users/georgejackson/Developer_Projects/Constraint_Engineering"
                "/bench/falsifier_verify.py",
                "/var/root/.ssh/id_rsa"):
        assert not _in_scope(bad, allow, protected=()), (
            f"{bad} is outside both the staged root and the run directory and "
            f"was accepted")


def test_a_protected_key_under_the_staged_root_is_still_refused():
    """DIRECTION 3, and the one that would make this fix dangerous if it failed.

    A key store deliberately hidden inside an allowed subtree must still lose
    the test, because `protected` is checked before the allowlist. This is the
    false-negative direction, so it is asserted rather than assumed.
    """
    hidden = f"{STAGED_TARGET_ROOT}/current/.boring/keys"
    allow = ["/tmp/run-0", str(STAGED_TARGET_ROOT)]
    assert not _in_scope(hidden, allow, protected=[hidden]), (
        "a PROTECTED key location under the staged root was accepted; "
        "widening the allowlist has blinded the scanner")
    assert not _in_scope(f"{hidden}/openrouter.key", allow, protected=[hidden]), (
        "a key file inside a protected directory under the staged root was "
        "accepted")


def test_the_forensic_module_actually_adds_the_root():
    """EXECUTED against the module's own source structure, not its prose.

    The allowlist is built inside a long function, so the cheapest honest check
    that the edit is wired is that the module imports the constant and appends
    it. A behavioural end-to-end test needs a full recorded run directory,
    which this file deliberately does not fabricate.
    """
    import ast
    src = (REPO / "bench/key_access_forensics.py").read_text()
    tree = ast.parse(src)
    names = {n.asname or n.name
             for node in ast.walk(tree)
             if isinstance(node, ast.ImportFrom)
             for n in node.names}
    assert "_STAGED_ROOT" in names, (
        "bench/key_access_forensics.py does not import STAGED_TARGET_ROOT, so "
        "the allowlist cannot contain it")
    assert "allowlist.append(str(_STAGED_ROOT))" in src, (
        "the staged root is imported but never appended to the allowlist -- an "
        "addition nothing reaches")
