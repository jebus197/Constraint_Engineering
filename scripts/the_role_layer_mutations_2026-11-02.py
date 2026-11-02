#!/usr/bin/env python3
"""Can `test_the_role_layer_cannot_collide_2026-11-02.py` actually go RED?

WHY. B21's role layer is an ADDITION, and `additive-standard`'s symmetric form
says an addition nothing reaches is not additive. A guard that passes under every
mutation reaches nothing. 11 confirmed defects in this project were additions
that did nothing; this script is what keeps this one off that list.

WHAT IT MUTATES. 6 reversions, each undoing exactly 1 property the guard claims:
    1  a role file sets a key `domains/mathematics.toml` also sets
       -> disjointness must fail (THE ENFORCEMENT this file exists for)
    2  a role file writes a SECOND top-level table
       -> the `role`-namespace-only test must fail
    3  the role layer is cut out of load_effective_policy
       -> "passing a role changes the policy" must fail
    4  an unknown role falls through silently instead of raising
       -> the loud-failure test must fail (his 2026-11-01 ruling)
    5  `roles/worker.toml` is created
       -> the "his functional vocabulary is still his" test must fail
    6  a role file invents a policy key under [role]
       -> the content-is-his test must fail

RESTORE DISCIPLINE. Every mutation records the EXACT BYTES it found and writes
them back, never `git checkout --`. On 2026-11-01 a `git checkout --` restore ate
the subject of the measurement along with the mutation, because the subject was
itself uncommitted. Files created by a mutation are removed; files edited are
restored byte-for-byte and the restore is VERIFIED by hash.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = REPO / "bench" / "tests" / "test_the_role_layer_cannot_collide_2026-11-02.py"
REG = REPO / "bench" / "cdsfl_registry"
ROLES = REG / "roles"
REGISTRY_PY = REG / "registry.py"


def _run_guard() -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
                        "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=REPO)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _digest(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Mutation:
    """Edit or create, run the guard, restore the exact bytes found."""

    def __init__(self, name, path, *, edit=None, create=None):
        self.name, self.path, self.edit, self.create = name, path, edit, create
        self.before: bytes | None = None
        self.before_hash: str | None = None
        self.existed = False

    def __enter__(self):
        self.existed = self.path.exists()
        if self.existed:
            self.before = self.path.read_bytes()
            self.before_hash = hashlib.sha256(self.before).hexdigest()
            self.path.write_text(self.edit(self.path.read_text()), encoding="utf-8")
        else:
            self.path.write_text(self.create, encoding="utf-8")
        return self

    def __exit__(self, *exc):
        if self.existed:
            self.path.write_bytes(self.before)
            assert _digest(self.path) == self.before_hash, (
                f"RESTORE FAILED for {self.path}: bytes differ from what was found")
        else:
            self.path.unlink()
            assert not self.path.exists(), f"RESTORE FAILED: {self.path} still present"
        return False


MUTATIONS = [
    Mutation("1 role file collides with a domain key",
             ROLES / "collator.toml",
             edit=lambda t: t + '\n[tools]\nmandatory = ["sympy"]\n'),
    Mutation("2 role file writes a second top-level table",
             ROLES / "participant.toml",
             edit=lambda t: t + '\n[extra]\nwhatever = 1\n'),
    Mutation("3 role layer cut out of load_effective_policy",
             REGISTRY_PY,
             edit=lambda t: t.replace("    if role:\n", "    if False and role:\n", 1)),
    Mutation("4 unknown role falls through silently",
             REGISTRY_PY,
             edit=lambda t: t.replace(
                 "            raise FileNotFoundError(\n"
                 "                f\"Role config not found: {role_path}\\n\"\n"
                 "                f\"Available roles: {available}\"\n"
                 "            )",
                 "            pass  # MUTATION: silent", 1)),
    Mutation("5 his functional vocabulary decided for him",
             ROLES / "worker.toml",
             create='[role]\nname = "worker"\naxis = "structural"\n'),
    Mutation("6 role file invents a policy key",
             ROLES / "player_manager.toml",
             edit=lambda t: t.replace('axis = "structural"',
                                      'axis = "structural"\nmin_rounds = 4', 1)),
]


def main() -> int:
    print("=" * 78)
    print("CAN THE ROLE-LAYER GUARD GO RED?")
    print("=" * 78)
    code, out = _run_guard()
    print(f"\nBASELINE (unmutated): exit {code}")
    print("    " + [ln for ln in out.splitlines() if "passed" in ln or "failed" in ln][-1])
    if code != 0:
        print("    ★ baseline is NOT green, so no mutation result means anything")
        return 2

    red = 0
    for m in MUTATIONS:
        pre = _digest(m.path) if m.path.exists() else None
        with m:
            c, o = _run_guard()
        post = _digest(m.path) if m.path.exists() else None
        assert pre == post, f"★ {m.name}: file not restored to found bytes"
        verdict = "RED (good)" if c != 0 else "★ STILL GREEN -- VACUOUS"
        tail = [ln for ln in o.splitlines() if "passed" in ln or "failed" in ln or "error" in ln.lower()]
        print(f"\n  {m.name}")
        print(f"      exit {c}  {verdict}")
        if tail:
            print(f"      {tail[-1].strip()}")
        red += (c != 0)

    print("\n" + "-" * 78)
    print(f"RESULT: {red} of {len(MUTATIONS)} mutations turn the guard RED")
    code2, out2 = _run_guard()
    print(f"POST-RESTORE baseline: exit {code2}  "
          f"{[ln for ln in out2.splitlines() if 'passed' in ln or 'failed' in ln][-1].strip()}")
    if code2 != 0:
        print("    ★ THE RESTORE DID NOT RESTORE. Investigate before trusting anything above.")
        return 2
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
