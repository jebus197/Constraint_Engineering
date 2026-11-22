#!/usr/bin/env python3
"""Does `test_no_entry_hides_a_ruling_of_his` still bite after its floor is removed?

WRITTEN BEFORE THE PATCH IS APPLIED, 2026-11-22, because no mutation harness in
`scripts/` names `test_a_prior_ruling_is_acknowledged_2026-11-03.py` and a
relaxation with no harness behind it is a hypothesis.

WHAT IS BEING CHANGED AND WHY. The live check carries 2 anti-vacuity devices.
The 1st is `assert len(det) >= 5`, a FLOOR on how many entries carry a ruling of
his. The 2nd is a set of CONSTRUCTED cases in the same file -- one of which its
own author labelled *"THE ANTI-VACUITY CASE. Without this, a live 0 proves
nothing."* On 2026-11-22 the live count fell to 3, because 4 entries were closed
and 2 of them carried his words. The PROPERTY held: 0 entries hide a ruling.
Only the floor failed.

THE 3 THINGS THIS SCRIPT ESTABLISHES, and the 1st is the one that matters:

  1. WITH a population above the floor and 1 entry unacknowledged, the check
     FAILS. If it does not, the relaxation is vacuous and must be REVERTED.
  2. WITH the live population of 3 and nothing hidden, the check SKIPS rather
     than silently passing -- a silent pass is the vacuity this exists to avoid.
  3. The constructed cases in the same file stay green.

EXIT 0 only when all 3 hold. Any other outcome means revert.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

def _find_repo() -> pathlib.Path:
    """Locate the repository, including from a scratch directory.

    ★ THE FIRST VERSION SEEDED `REPO` WITH THE FILE ITSELF and only replaced it
    if an ancestor held `bench/tests`. Run from a scratch directory no ancestor
    does, so REPO stayed as the script PATH and the first write raised
    NotADirectoryError. A fallback to the known checkout is what makes a
    producer runnable from anywhere, which is the point of keeping it portable.
    """
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "bench" / "tests").is_dir():
            return cand
    fb = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
    if (fb / "bench" / "tests").is_dir():
        return fb
    raise SystemExit("cannot locate the repository: bench/tests not found")


REPO = _find_repo()
GUARD = "bench/tests/test_a_prior_ruling_is_acknowledged_2026-11-03.py"
NODE = f"{GUARD}::TestTheLiveState::test_no_entry_hides_a_ruling_of_his"

#: A conftest-free way to force a population: run pytest with a tiny plugin that
#: patches the module's `detail_rulings` before the test executes.
PLUGIN = '''
import pytest
@pytest.fixture(autouse=True)
def _force(monkeypatch, request):
    if "test_no_entry_hides_a_ruling_of_his" not in request.node.name:
        return
    import sys
    mod = None
    for m in list(sys.modules.values()):
        if getattr(m, "__file__", "") and "which_open_entries_already_have_his_ruling" in str(m.__file__):
            mod = m
            break
    if mod is None:
        pytest.skip("module under test not importable from here")
    monkeypatch.setattr(mod, "detail_rulings", lambda *a, **k: {
        "B01": {"acknowledged": True},  "B02": {"acknowledged": True},
        "B03": {"acknowledged": True},  "B04": {"acknowledged": True},
        "B05": {"acknowledged": True},  "B06": {"acknowledged": False},
    })
'''


def run(args, env_plugin=None):
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args]
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)


def main() -> int:
    ok = True

    print("1. WITH 6 entries and 1 unacknowledged, the check must FAIL")
    plug = REPO / "bench" / "tests" / "_force_hidden_ruling_plugin.py"
    plug.write_text(PLUGIN)
    try:
        r = run(["-p", "bench.tests._force_hidden_ruling_plugin", NODE])
        failed = r.returncode != 0 and "1 failed" in r.stdout
        print(f"   rc={r.returncode}  {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''}")
        print(f"   {'OK — it bites' if failed else 'VACUOUS — REVERT THE PATCH'}")
        ok &= failed
    finally:
        plug.unlink(missing_ok=True)

    print("\n2. WITH the live population, it must SKIP and not silently pass")
    r = run(["-rs", NODE])
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    skipped = "skipped" in tail
    print(f"   rc={r.returncode}  {tail}")
    print(f"   {'OK — skipped with a reason' if skipped else 'NOT SKIPPED — check why'}")
    ok &= skipped

    print("\n3. The constructed cases must stay green")
    r = run([GUARD])
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    green = r.returncode == 0
    print(f"   rc={r.returncode}  {tail}")
    ok &= green

    print(f"\n{'ALL 3 HOLD — the relaxation is sound.' if ok else 'FAILED — REVERT.'}")
    return 0 if ok else 1


if __name__ == "__main__":
    #: ANSWER `--help` WITHOUT DOING THE WORK. The guard EXECUTES any
    #: script whose behaviour it cannot establish structurally, so a
    #: producer without this runs its whole body merely by being asked
    #: what it does. That fault caused 3 of the 15 board failures on
    #: 2026-11-22.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
