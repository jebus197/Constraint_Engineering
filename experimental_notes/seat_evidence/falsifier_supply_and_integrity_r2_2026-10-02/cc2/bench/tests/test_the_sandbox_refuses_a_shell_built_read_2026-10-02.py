# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 27a09153df938446c48e793144a8c014d59ff0f27991162ef04035dd72c3402b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A SHELL COMMAND IS NOT A PATH. Layer 4, the spawn hook, measured.

THE DEFECT, 2026-10-02 adversarial pass. The observer's spawn branch called
`_resolve()` on each whole argument blob. With `shell=True` the blob IS the
command line, so `_resolve("cat /somewhere/protected.json")` normalises to
`<sandbox cwd>/cat /somewhere/protected.json` -- a path under an ALLOWED root --
and `_denied` waved it through. `/bin/sh` is not a Python child, so it inherits
no audit hook either. The identical read through `open()` was refused.

Measured against a DECOY file created by this test and registered through
`CDSFL_KEY_DIR`, so `_protected_values()` and the observer's SHA-256 protected
set cover it exactly as they cover the real store. NO REAL KEY IS TOUCHED and
the decoy holds a benign sentinel.

The control probe matters as much as the attack: if `open()` were not refused,
the attack probe would prove only that the decoy was unprotected.
"""
from __future__ import annotations

import base64
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GATE = ROOT / "bench" / "falsifier_verify.py"

pytestmark = pytest.mark.skipif(not GATE.is_file(), reason="gate absent")

SENTINEL = "SENTINEL-ADV-7f3a91"


@pytest.fixture
def decoy(tmp_path, monkeypatch):
    """A protected decoy and a gate module that knows it is protected."""
    d = tmp_path / "cdsfl_adv_decoy_key_dir"
    d.mkdir()
    f = d / "decoy_store.json"
    f.write_text(json.dumps({"decoy_sentinel": SENTINEL}), encoding="utf-8")
    monkeypatch.setenv("CDSFL_KEY_DIR", str(d))
    sys.path.insert(0, str(ROOT))
    from bench import falsifier_verify as fv
    # NO `importlib.reload` HERE, and that is a defect this file already caused
    # once. `_protected_values()` and `_observer_source()` read os.environ at
    # CALL time, so the monkeypatched variable is live without one -- while a
    # reload rebinds the module's `INTEGRITY_REJECTIONS` to a NEW list, leaving
    # test_falsifier_cannot_read_the_key.py's `from ... import
    # INTEGRITY_REJECTIONS` pointing at the old one. That took
    # test_a_rejection_is_announced_and_recorded red, in a different file,
    # through nothing but import order.
    assert str(d) in fv._protected_values(), (
        "the decoy is not protected, so neither probe below proves anything")
    return fv, str(f)


def _code(path, shell):
    b64 = base64.b64encode(path.encode()).decode()
    if shell:
        return (f'import base64, subprocess\n'
                f'p = base64.b64decode("{b64}").decode()\n'
                f'r = subprocess.run("cat " + p, shell=True,\n'
                f'                   capture_output=True, text=True)\n'
                f'print("READ:", r.stdout.strip())\n')
    return (f'import base64\n'
            f'p = base64.b64decode("{b64}").decode()\n'
            f'print("READ:", open(p).read())\n')


def test_the_source_gate_cannot_see_either_route(decoy):
    """STATED, NOT GLOSSED. Layer 3 is a regex over source and a base64 path
    defeats it by construction. That is why layer 4 exists, and it is why layer
    4 having a hole was not a redundancy."""
    fv, path = decoy
    assert fv.scan_falsifier_source(_code(path, shell=False),
                                    repo_root=str(ROOT)) == []
    assert fv.scan_falsifier_source(_code(path, shell=True),
                                    repo_root=str(ROOT)) == []


def test_a_direct_open_of_a_protected_file_is_refused(decoy):
    """THE CONTROL. Without this the attack probe is uninterpretable."""
    fv, path = decoy
    out = fv.execute_python(_code(path, shell=False), repo_root=str(ROOT))
    assert "INTEGRITY VIOLATION" in out, out[:400]
    assert SENTINEL not in out


def test_a_shell_built_read_of_a_protected_file_is_refused(decoy):
    """THE ATTACK. Before the spawn-token rule this returned the file."""
    fv, path = decoy
    out = fv.execute_python(_code(path, shell=True), repo_root=str(ROOT))
    assert SENTINEL not in out, (
        "a falsifier read a protected file through a shell child: the source "
        "gate saw a base64 string, the spawn hook resolved the whole command "
        "line as one path, and /bin/sh inherits no audit hook")
    assert "INTEGRITY VIOLATION" in out, out[:400]


def test_the_rule_refuses_no_honest_spawn(decoy):
    """ANTI-OVERREACH, and the reason the rule is generous about what a token is:
    a token that is not a path resolves under the sandbox cwd and is allowed, so
    this refuses nothing the direct `open` route would allow."""
    fv, _ = decoy
    honest = [
        'import subprocess, sys\n'
        'r = subprocess.run([sys.executable, "-c", "print(1+1)"],\n'
        '                   capture_output=True, text=True)\n'
        'print("OK", r.stdout.strip())\n',
        f'import subprocess\n'
        f'r = subprocess.run("ls {ROOT}/bench/routing.py", shell=True,\n'
        f'                   capture_output=True, text=True)\n'
        f'print("OK", r.returncode)\n',
        'import subprocess, tempfile, os\n'
        'p = os.path.join(tempfile.gettempdir(), "adv_probe.txt")\n'
        'open(p, "w").write("x")\n'
        'r = subprocess.run("cat " + p, shell=True,\n'
        '                   capture_output=True, text=True)\n'
        'print("OK", r.stdout.strip())\n',
    ]
    for code in honest:
        out = fv.execute_python(code, repo_root=str(ROOT))
        assert "INTEGRITY VIOLATION" not in out, (code, out[:300])
        assert out.startswith("OK"), (code, out[:300])


def test_path_tokens_finds_what_it_claims_to(decoy):
    """The helper, directly: the unit the two probes above exercise end to end.

    ONLY THE DEFINITIONS ARE EXECUTED, never the module. The observer's last
    statement is `sys.addaudithook(_hook)`, and exec-ing the whole source would
    install that hook on the TEST process -- a sandbox boundary leaking into the
    suite that measures it. The two needed nodes are lifted out by AST instead.
    """
    import ast
    fv, _ = decoy
    src = fv._observer_source("/tmp/t.trace", str(ROOT))
    tree = ast.parse(src)
    wanted = [n for n in tree.body
              if (isinstance(n, ast.FunctionDef) and n.name == "_path_tokens")
              or (isinstance(n, ast.Assign)
                  and any(getattr(t, "id", "") == "_TOKEN_RE" for t in n.targets))]
    assert len(wanted) == 2, [type(n).__name__ for n in wanted]
    ns: dict = {"re": __import__("re")}
    exec(compile(ast.Module(body=wanted, type_ignores=[]), "<observer>", "exec"), ns)
    toks = ns["_path_tokens"]
    assert toks("cat /a/b/key.json") == ["/a/b/key.json"]
    assert toks("sh -c 'cat ~/keys/k.json'") == ["~/keys/k.json"]
    assert toks("/bin/sh -c echo") == ["/bin/sh"]
    assert toks("print(1+1)") == []
    assert toks("") == []
