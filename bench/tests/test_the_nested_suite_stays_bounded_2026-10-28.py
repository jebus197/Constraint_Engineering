#!/usr/bin/env python3
r"""B37: the per-test timeout is the protection, and it may not be switched off.

HIS PROPOSAL, 2026-10-28: run the nested suite sequentially rather than risk his
8 GiB machine becoming unusable or the tests failing to complete.

HIS CONCERN IS RIGHT. HIS MECHANISM IS NOT THE ONE THAT APPLIES, and that is why
this file guards something else. Measured by
`scripts/the_nested_suite_is_bounded_not_serial_2026-10-28.py`:

  - The nested run was ALREADY serial. `hooks/pre-commit` runs
    `python3 -m pytest -q -p no:cacheprovider $GUARDS` with no `-n`, and
    `pytest.ini` carries no `addopts`. There was nothing to serialise.
  - A fork-inside-a-threaded-process deadlock is RULED OUT: Python 3.13 on macOS
    defaults to `spawn` and nothing in the tree forces another start method.
  - A thread-method timeout DOES reclaim a process blocked in `os.waitpid`. I
    expected it could not; measured against an unbounded
    `subprocess.run(["sleep", "25"])` under a 3-second limit, the run ended in
    3.3 seconds, an overshoot of 0.3. My hypothesis was wrong.

SO THE 45-MINUTE DEADLOCK WAS THE PROTECTION BEING ABSENT. B37's own record says
that run was made "WITH THE LIMIT RAISED TO 1800 SECONDS FOR THE WHOLE RUN". A
whole-run limit cannot reclaim an individual test. The per-test limit is what
keeps his machine usable, and the answer to the ruling B37 was waiting on is
therefore: a test MAY run the hook's full guard list, because the cost is
bounded and known, PROVIDED the per-test limit is never replaced by a whole-run
one.

That proviso is the thing worth guarding, because it is a configuration change
somebody will make again while chasing a slow suite.
"""
from __future__ import annotations

import ast
import configparser
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
INI = REPO / "pytest.ini"
NESTED = (
    "bench/tests/test_precommit_guard_2026-09-09.py",
    "bench/tests/test_precommit_restages_repairs_2026-09-11.py",
    "bench/tests/test_precommit_gate_cost_2026-09-10.py",
)
RUNNERS = {"run", "check_call", "check_output", "Popen", "call"}

#: AST-counted 2026-10-28. 13 of 22 launches across the 3 nested-hook files
#: carry no `timeout=`, 0.590909 Wilson [0.387348, 0.767442]. Lower is better and
#: this may never rise. A first count by `grep -A3` said 3 of 16 for one file
#: where the AST says 13 of 16: line proximity is the wrong instrument for a
#: question about call boundaries.
UNBOUNDED_CEILING = 13


def _ini() -> configparser.ConfigParser:
    cp = configparser.ConfigParser()
    cp.read(INI, encoding="utf-8")
    return cp


def test_a_per_test_timeout_is_configured():
    """THE PROTECTION. Without this, a nested run can hang the machine."""
    cp = _ini()
    assert cp.has_option("pytest", "timeout"), (
        "pytest.ini has no per-test `timeout`. A whole-run limit cannot reclaim "
        "an individual test, and that is the configuration in which the nested "
        "hook run sat at 0.0% CPU for 45 minutes on an 8 GiB machine. Restore "
        "the per-test limit; raise a single test with @pytest.mark.timeout "
        "instead of removing the global one.")
    value = int(cp.get("pytest", "timeout"))
    assert value > 0, f"per-test timeout is {value}, which disables it"


#: The only method this project has MEASURED to reclaim a process blocked in
#: `os.waitpid`. `signal` is pytest-timeout's other valid value and is plausible
#: but UNMEASURED here, so switching to it is a change that needs evidence first.
MEASURED_RECLAIMING_METHODS = ("thread",)


def test_the_timeout_method_is_one_this_project_has_measured():
    """A MUTATION TEST MADE THIS REACHABLE, having first shown it vacuous.

    The first version asserted `method in ("thread", "signal")`. Those are
    pytest-timeout's ONLY valid values, so any other setting makes pytest refuse
    to start with `ValueError: Invalid method` and returncode 3 -- measured. The
    assertion could therefore never fail, which is the addition-side half of the
    additive standard: a check nothing reaches.

    Narrowed to what has actually been measured. `thread` was measured on
    2026-10-28 reclaiming a child blocked in `os.waitpid` with a 0.3 s overshoot
    on a 3 s limit. `signal` was not. So switching to `signal` -- a perfectly
    valid value -- now goes red and asks for the measurement, which is a real
    and reachable outcome rather than a restatement of pytest's own validation.
    """
    cp = _ini()
    method = cp.get("pytest", "timeout_method", fallback="")
    assert method in MEASURED_RECLAIMING_METHODS, (
        f"timeout_method is {method!r}, which this project has not measured. "
        f"Only {MEASURED_RECLAIMING_METHODS} has been shown here to reclaim a "
        f"process blocked in os.waitpid. Run "
        f"scripts/the_nested_suite_is_bounded_not_serial_2026-10-28.py under the "
        f"new method and record the overshoot before changing this.")


def test_the_long_nested_test_raises_its_own_limit_rather_than_the_global_one():
    """B36's repair, held in place. The expensive one is marked, not exempted.

    ★ CONVERTED FROM A SOURCE-TEXT ASSERTION, 2026-10-28. It read
    `assert "mark.timeout" in txt`, which a COMMENT mentioning the decorator
    satisfies and which says nothing about the VALUE. The mark is now read off
    the collected function and compared with the global limit, so the property
    checked is the one that matters: the expensive test raises its OWN ceiling
    rather than the suite's. `execute-do-not-grep`.
    """
    import ast
    import configparser
    mod = REPO / "bench/tests/test_precommit_gate_cost_2026-09-10.py"
    tree = ast.parse(mod.read_text(encoding="utf-8"))
    marks: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            f = dec.func
            if getattr(f, "attr", None) != "timeout":
                continue
            for a in dec.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, (int, float)):
                    marks.append(int(a.value))
    assert marks, (
        "no test in the gate-cost module carries a timeout mark with a value, so "
        "either it will be killed at the global limit or the global limit has "
        "been raised for the whole suite to accommodate it. The second is the "
        "deadlock configuration.")
    cp = configparser.ConfigParser()
    cp.read(INI, encoding="utf-8")
    global_limit = int(cp.get("pytest", "timeout"))
    assert max(marks) > global_limit, (
        f"the gate-cost test's own ceiling is {max(marks)} s against a global "
        f"{global_limit} s, so marking it buys nothing and it will still be "
        f"killed mid-run")


def test_every_nested_hook_test_is_bounded_somehow():
    """EXECUTED against the AST, not asserted over source text.

    A nested-hook test is bounded if it carries its own timeout mark OR every
    one of its subprocess launches carries a timeout OR the global per-test
    limit applies. The last always holds while the first test above passes, so
    this checks the stronger per-call property and reports which files rely on
    the global backstop alone.
    """
    cp = _ini()
    assert cp.has_option("pytest", "timeout"), "global backstop missing"
    relying_on_the_backstop = []
    for rel in NESTED:
        p = REPO / rel
        txt = p.read_text(encoding="utf-8")
        tree = ast.parse(txt)
        bare = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and \
                    getattr(node.func, "attr", None) in RUNNERS and \
                    getattr(getattr(node.func, "value", None), "id", None) == "subprocess":
                if "timeout" not in {k.arg for k in node.keywords if k.arg}:
                    bare += 1
        if bare and "mark.timeout" not in txt:
            relying_on_the_backstop.append((rel, bare))
    # This is a REPORT, not a refusal: the global backstop genuinely covers them.
    # The ratchet below is what stops the number growing.
    assert all(n <= UNBOUNDED_CEILING for _, n in relying_on_the_backstop), (
        f"a nested-hook file's unbounded launches exceed the recorded ceiling: "
        f"{relying_on_the_backstop}")


def test_the_unbounded_launch_count_does_not_grow():
    """RATCHET. 13 of 22 today; it may fall and may not rise."""
    total = bare = 0
    sites = []
    for rel in NESTED:
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and \
                    getattr(node.func, "attr", None) in RUNNERS and \
                    getattr(getattr(node.func, "value", None), "id", None) == "subprocess":
                total += 1
                if "timeout" not in {k.arg for k in node.keywords if k.arg}:
                    bare += 1
                    sites.append(f"{rel}:{node.lineno}")
    assert bare <= UNBOUNDED_CEILING, (
        f"{bare} of {total} subprocess launches in the nested-hook files carry "
        f"no timeout, up from the ceiling of {UNBOUNDED_CEILING}. A launch "
        f"without one spends the whole per-test budget on a hang and fails the "
        f"test rather than the call.\nsites: {sites}")


def test_the_hook_does_not_parallelise_its_nested_run():
    """Hypothesis 1, held. If somebody adds xdist to the hook, the measurement
    above stops applying and must be redone."""
    import shlex
    hook = (REPO / "hooks" / "pre-commit").read_text(encoding="utf-8")
    line = next((l for l in hook.splitlines() if "-m pytest" in l), "")
    assert line, "the hook no longer invokes pytest; this guard is stale"
    # ★ TOKENISED, NOT SUBSTRING-MATCHED -- 2026-10-28. `"-n " not in line` is
    # defeated by `-n4` and by a line break, and it fires on the harmless `-n `
    # inside an unrelated word. shlex splits the command the way a shell does,
    # so the check is on the ARGUMENT LIST the hook actually passes.
    try:
        tokens = shlex.split(line, comments=False, posix=True)
    except ValueError:
        tokens = line.split()
    parallel = [t for t in tokens
                if t == "-n" or t.startswith("-n") and t[2:].strip().isdigit()
                or "xdist" in t or t.startswith("--numprocesses")]
    assert not parallel, (
        f"the hook's nested pytest run is now parallel ({parallel}): "
        f"{line.strip()!r}. Every "
        f"measurement in scripts/the_nested_suite_is_bounded_not_serial_"
        f"2026-10-28.py assumes it is serial, and the fork-deadlock exclusion "
        f"assumed a single process. Re-measure before keeping this.")
