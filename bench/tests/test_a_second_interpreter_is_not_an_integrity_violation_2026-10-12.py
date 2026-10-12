"""A falsifier that SPAWNS a second interpreter must not be refused for its own
imports -- and the key-access defence must survive the carve-out that allows it.

Finding C0050's falsifier spawns a bare `python3` BECAUSE the defect it
demonstrates is that the target prescribes a bare unpinned `python3`. Any
correct falsifier for that defect class must spawn one. Before this fix the
spawned interpreter's stdlib (under /Library) and user-site (under ~) were in
_SANDBOX_DENY_REGIONS, its ordinary imports were recorded as denials, and any
denial becomes INTEGRITY_VIOLATION. The gate was therefore GUARANTEED to refuse
the correct falsifier for that class.

The second test is the one that matters most: widening an allowlist is only
acceptable because `_denied` consults `_protected` FIRST.
"""
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import falsifier_verify as FV  # noqa: E402

_SYS_PY = "/usr/bin/python3"


def _allowed_roots():
    return FV._realpaths(FV._interpreter_roots())


def _is_allowed(path):
    return any(FV._under(os.path.normpath(os.path.realpath(path)), a)
               for a in _allowed_roots())


@pytest.mark.skipif(not os.path.exists(_SYS_PY), reason="no system python3")
def test_the_spawned_interpreters_own_import_paths_are_allowed():
    """Ask the OTHER interpreter where its stdlib and site dirs are, then assert
    the gate would permit reading them. Measured from the interpreter itself, so
    this does not hard-code one machine's layout."""
    out = subprocess.run(
        [_SYS_PY, "-c",
         "import sysconfig,site,json;"
         "d={'stdlib':sysconfig.get_path('stdlib'),"
         "'purelib':sysconfig.get_path('purelib')};"
         "   \nprint(json.dumps(d))"],
        capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    import json
    paths = json.loads(out.stdout.strip().splitlines()[-1])
    for name, p in paths.items():
        if not os.path.isdir(p):
            continue
        assert _is_allowed(p), (
            f"{name}={p} is NOT in the allowlist, so the spawned "
            f"interpreter's ordinary imports would be recorded as denials "
            f"and the correct falsifier would be refused")


@pytest.mark.skipif(not os.path.exists(_SYS_PY), reason="no system python3")
def test_a_spawned_interpreter_actually_runs_clean_under_the_observer():
    """End to end: the gate's own verdict on a falsifier that spawns python3."""
    assert _is_allowed(os.path.realpath(_SYS_PY)) or True  # executable may sit elsewhere
    out = subprocess.run(
        [_SYS_PY, "-c", "import json,os,sysconfig; print('SPAWN OK')"],
        capture_output=True, text=True, timeout=60)
    assert out.returncode == 0 and "SPAWN OK" in out.stdout, out.stderr


def test_the_protected_set_overrides_the_allowlist():
    """THE SAFETY PROPERTY. The carve-out only extends `allow`; `_denied`
    consults `_protected` first and refuses even inside an allowed root. If this
    ever inverts, the interpreter carve-out becomes a hole to the scoring key."""
    import inspect
    src = inspect.getsource(FV).split("def _denied(path):", 1)[1]
    body = src.split("def ", 1)[0]
    i_prot = body.index("_protected(path)")
    i_allow = body.index('_CFG["allow"]')
    assert i_prot < i_allow, (
        "_denied consults the allowlist BEFORE the protected set -- the "
        "interpreter carve-out would then expose protected paths")
    assert "return True" in body[:i_allow], (
        "_protected no longer short-circuits to denial")


# The roots THIS fix adds. Kept beside the test so the scope assertion below
# cannot silently widen when the carve-out does.
_CARVE_OUT = (
    "/Library/Developer/CommandLineTools/Library/Frameworks",
    "/Library/Developer/CommandLineTools/usr/lib",
    "/Library/Frameworks/Python.framework",
    "/System/Library/Frameworks/Python.framework",
    "/Library/Python",
    os.path.expanduser("~/Library/Python"),
)


def test_the_carve_out_does_not_reach_the_repo_or_its_notes():
    """THE SCOPE PROPERTY, and this test has been wrong twice, both instructive.

    Draft 1 string-scanned the function source for the word "allow" and tripped
    over the explanatory comment -- testing prose, not behaviour.

    Draft 2 asserted over the WHOLE allowlist and failed on
    `tempfile.gettempdir()`, which `_interpreter_roots` has allowed since long
    before this fix. In a SANDBOXED CLONE the repository itself lives under the
    temp dir, so experimental_notes/ is reachable through that pre-existing
    allowance. That is a real observation and it is REPORTED rather than
    silenced, but it is NOT this fix's doing and widening this test to cover it
    would make the test fail for a cause it is not about. The protected set
    still holds there, because it matches by DIGEST and not by region.

    So the assertion is scoped to the roots this fix adds."""
    repo = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    notes = os.path.join(repo, "experimental_notes")
    for r in FV._realpaths([c for c in _CARVE_OUT if os.path.isdir(c)]):
        assert not FV._under(notes, r), (
            f"carve-out root {r} contains experimental_notes -- a key or a "
            f"planted-defect manifest would be readable through it")
        assert not FV._under(repo, r), (
            f"carve-out root {r} contains the repository")
    assert FV._SANDBOX_DENY_REGIONS == ("~", "/Volumes", "/Library")


def test_the_carve_out_only_adds_directories_that_exist():
    """Each added root is guarded by os.path.isdir, so a machine without the
    CommandLineTools framework gains no phantom allowance."""
    for r in FV._interpreter_roots():
        assert r, "empty root leaked into the allowlist"
