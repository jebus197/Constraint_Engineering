"""The verifier tools must work when the CALLER IS RUN AS A SCRIPT.

WHY THIS FILE EXISTS
--------------------
On 2026-09-05 a six-seat panel was dispatched under the founder's ruling that
"tool use is at the core of what CDSFL is". It reported cx=10 tool calls and
cgpt=7 tool calls, and looked tool-enabled. 16 of those 17 calls had in fact
returned

    {"error": "ModuleNotFoundError: No module named 'bench.immune_agents'"}

The single survivor was pytest_run, which shells out with cwd=REPO_ROOT and so
never performs the import.

THE DEFECT. ``openrouter_tools`` reaches the sympy/z3 verifiers as
``bench.immune_agents``. That name resolves only with the REPO ROOT on
sys.path. Python puts the SCRIPT'S OWN DIRECTORY on sys.path[0], so running
``python3 bench/confer_maths_panel_2026-09-05.py`` puts ``bench/`` there, and the
repo root is then on the path only by accident.

AND IT WAS WORSE THAN THAT, which is why the observed error named the submodule.
``bench`` has no ``__init__.py``; it is a namespace package. An empty stray tree
-- ``bench/bench/results/phase2``, 0 files, untracked, left by a
``mkdir -p bench/results/phase2`` run with cwd already inside ``bench/`` -- was
therefore enough to make ``bench`` resolve SUCCESSFULLY from a script, to the
empty ``bench/bench``. The package import worked and shadowed the real one; only
``bench.immune_agents`` failed. The strays were removed on 2026-09-05 (nothing
was lost: the real ``bench/results/phase2`` holds its 6 files), so ``bench`` now
resolves to one directory. Both spellings of the failure are guarded below,
because the difference between them is one accidental ``mkdir``.

WHY THE EXISTING SUITE DID NOT CATCH IT. ``test_openrouter_tools.py`` passes,
all 36 of it, because pytest inserts its rootdir on sys.path. The test and the
script therefore disagree about what is importable, and only the script is how
the panel actually runs. A test that imports the module the way pytest does can
never see this defect.

WHY THE FAILURE IS SILENT, WHICH IS THE EXPENSIVE PART. The model receives the
error string AS A TOOL RESULT. It does not crash, it does not retry; it reads
"ModuleNotFoundError" and reasons on unaided. Every downstream stage then treats
an unverified answer as a tool-verified one. This is the same shape as the
Wolfram rule already in .claude/CLAUDE.md -- a failed call is NOT a result --
and the same shape as the verdict reader that once matched NOT FALSIFIED as
FALSIFIED.

WHY THIS TEST SUBPROCESSES INSTEAD OF IMPORTING. Per ``execute-do-not-grep``:
asserting that openrouter_tools.py CONTAINS ``sys.path.append`` would pass
against both the fixed and the broken module, because the string is not the
behaviour. The only way to observe the defect is to reproduce the interpreter
state that produced it -- sys.path[0] == bench/ -- and call the dispatcher. So
each test here spawns a real script and reads a real verdict.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BENCH = REPO_ROOT / "bench"

# The signatures of the defect. BOTH forms must be caught, and pinning only the
# first is a trap this file already fell into once.
#
# Which one you get depends on whether a nested `bench/bench` directory happens
# to exist. With one present, `bench` resolves as a namespace package to the
# WRONG directory and only the submodule lookup fails ->
# "No module named 'bench.immune_agents'". With none present, the package itself
# is absent -> "No module named 'bench'".
#
# The original version of this file asserted on the first string alone. When the
# stray directory was removed minutes later, reverting the fix produced the
# SECOND string, and 7 of 10 assertions here passed against a module whose tools
# were completely broken. A test pinned to one spelling of a failure is not a
# test of the failure.
DEFECT_SIGNATURES = (
    "No module named 'bench.immune_agents'",
    "No module named 'bench'",
)


def _assert_no_import_defect(out: str, what: str) -> None:
    """Fail if the output carries ANY form of the import defect."""
    for sig in DEFECT_SIGNATURES:
        assert sig not in out, (
            f"{what} hit the 2026-09-05 silent tool failure ({sig!r}). "
            f"Every sympy/z3 call from a script-run caller is erroring, and the "
            f"model reads the error as a tool result and reasons on regardless.\n"
            f"{out}"
        )
    # Belt and braces: any ModuleNotFoundError at all means the verifier never ran.
    assert "ModuleNotFoundError" not in out, (
        f"{what} raised an unrecognised ModuleNotFoundError -- the verifier did "
        f"not execute, so any verdict downstream is unsupported.\n{out}"
    )


def _run_as_script(body: str, cwd: Path) -> str:
    """Execute ``body`` as a real script INSIDE bench/, returning its stdout.

    Writing the file into bench/ is what makes sys.path[0] == bench/, which is
    the condition under test. Running it from a temp directory elsewhere would
    not reproduce the defect.
    """
    script = BENCH / "_tmp_script_path_probe.py"
    script.write_text(textwrap.dedent(body), encoding="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )
    finally:
        script.unlink(missing_ok=True)
    assert proc.returncode == 0, (
        f"probe script failed rc={proc.returncode}\n"
        f"stdout={proc.stdout}\nstderr={proc.stderr}"
    )
    return proc.stdout


PROBE = """
    import json
    import openrouter_tools as T
    print(T.dispatch_tool_call({name!r}, json.dumps({args!r})))
"""


class TestSympyVerifyWorksFromTheScriptPath:
    """sympy_verify must return a VERDICT, not a ModuleNotFoundError."""

    def test_a_true_claim_is_confirmed(self):
        out = _run_as_script(
            PROBE.format(name="sympy_verify",
                         args={"claim": "Eq((1-p)**2, 1 - 2*p + p**2)"}),
            cwd=REPO_ROOT,
        )
        result = json.loads(out.strip().splitlines()[-1])
        assert "error" not in result, (
            f"tool errored instead of verifying: {result}. "
            f"If this names a missing module, the sys.path fix in "
            f"openrouter_tools.py has been reverted."
        )
        assert result["verdict"] == "CONFIRMED"

    def test_no_form_of_the_import_defect_is_present(self):
        """Named separately so a failure reads as the defect, not as noise."""
        out = _run_as_script(
            PROBE.format(name="sympy_verify",
                         args={"claim": "Eq(x + 0, x)"}),
            cwd=REPO_ROOT,
        )
        _assert_no_import_defect(out, "sympy_verify")

    def test_a_false_claim_is_still_rejected(self):
        """Discrimination: the tool must distinguish, not just return CONFIRMED.

        Without this, a stub that always answered CONFIRMED would satisfy the
        test above. This is the tautology trap the panel caught twice in the
        appendix tests on 2026-09-05.
        """
        out = _run_as_script(
            PROBE.format(name="sympy_verify",
                         args={"claim": "Eq((1-p)**2, 1 - p**2)"}),
            cwd=REPO_ROOT,
        )
        result = json.loads(out.strip().splitlines()[-1])
        assert "error" not in result, result
        assert result["verdict"] != "CONFIRMED", (
            f"a FALSE claim was not rejected: {result}. The verifier is not "
            f"discriminating, so a CONFIRMED elsewhere carries no information."
        )


class TestZ3VerifyWorksFromTheScriptPath:
    """z3_verify imports through the same ``bench.`` name and broke identically."""

    def test_z3_returns_a_verdict_not_an_import_error(self):
        out = _run_as_script(
            PROBE.format(name="z3_verify",
                         args={"claim": "for all x: x > 0 implies x + 1 > 1"}),
            cwd=REPO_ROOT,
        )
        _assert_no_import_defect(out, "z3_verify")
        result = json.loads(out.strip().splitlines()[-1])
        assert "error" not in result, result
        assert "verdict" in result


class TestTheConditionUnderTestIsRealNotSimulated:
    """Guard the guard: prove the probe really does run with sys.path[0]==bench/.

    If a future refactor moved the probe out of bench/, every test above would
    still pass while testing nothing -- the exact vacuity that let the original
    defect through 36 green tests.
    """

    def test_the_probe_runs_with_bench_as_sys_path_zero(self):
        out = _run_as_script(
            "import sys; print(sys.path[0])",
            cwd=REPO_ROOT,
        )
        assert out.strip() == str(BENCH), (
            f"probe ran with sys.path[0]={out.strip()!r}, not {str(BENCH)!r}. "
            f"The script-path condition is NOT being reproduced, so the tests "
            f"in this file are vacuous."
        )

    def test_bench_immune_agents_is_genuinely_unimportable_by_default(self):
        """The premise of the whole file: without the fix, the verifiers are gone.

        Asserted by running a probe that does NOT import openrouter_tools, so
        nothing has had a chance to repair sys.path.

        THE PRECONDITION IS ABOUT THE SUBMODULE, NOT THE PACKAGE, and getting
        that wrong is what made the original diagnosis incomplete. On 2026-09-05
        an empty stray directory tree -- bench/bench/results/phase2, 0 files,
        untracked, left behind by a `mkdir -p bench/results/phase2` run with cwd
        already inside bench/ -- made `bench` resolve PERFECTLY WELL from a
        script, as an implicit namespace package pointing at the empty
        bench/bench. Only the submodule lookup failed, which is why the observed
        error was `No module named 'bench.immune_agents'` and never
        `No module named 'bench'`. Asserting on the package would have passed
        while the tools were broken. The strays were removed the same day, but
        the assertion must not depend on their absence: any future nested
        directory would silently restore the shadow.
        """
        out = _run_as_script(
            """
            import importlib.util
            try:
                found = importlib.util.find_spec('bench.immune_agents') is not None
            except ModuleNotFoundError:
                found = False
            print(found)
            """,
            cwd=REPO_ROOT,
        )
        assert out.strip() == "False", (
            "`bench.immune_agents` is importable from a script WITHOUT "
            "openrouter_tools repairing sys.path, so this file no longer tests "
            "what it claims. Something else now puts the repo root on the path "
            "-- find it, because the fix in openrouter_tools.py may have become "
            "dead code and would then be removed by a future tidy-up, silently "
            "restoring the defect."
        )


class TestEverySeatFacingToolSurvivesTheScriptPath:
    """All 5 advertised tools, because the panel advertised all 5."""

    @pytest.mark.parametrize(
        "name,args",
        [
            ("sympy_verify", {"claim": "Eq(x*1, x)"}),
            ("z3_verify", {"claim": "for all x: x > 0 implies x >= 0"}),
            ("ruff_check", {"file_path": "bench/openrouter_tools.py"}),
            ("mypy_check", {"file_path": "bench/openrouter_tools.py"}),
        ],
    )
    def test_tool_does_not_return_an_import_error(self, name, args):
        out = _run_as_script(PROBE.format(name=name, args=args), cwd=REPO_ROOT)
        _assert_no_import_defect(out, name)
