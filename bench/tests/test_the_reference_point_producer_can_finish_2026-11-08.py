"""B84's producer crashed mid-run, and its figures were correct anyway.

FOUND BY RUNNING IT, which is the only way it could have been found. On
2026-11-08, working B84, `scripts/the_archive_records_outcomes_not_reference_
points_2026-11-02.py` raised `NameError: name 'np' is not defined` at the
closed-form table near its end. `np.log` is the SECOND of its 2 cross-check
routes and numpy was never imported, so the module died on the first row it
reached.

EVERYTHING AFTER THAT POINT WAS UNREACHABLE, and that is the consequential
half. The `--sizing` block is what computes the floor multiplier
`2240/481 = 4.656965`, and entry B84 quotes that figure to the founder. No
invocation of this script could produce it.

THE FIGURES WERE CORRECT, AND SAYING SO IS NOT A SOFTENING. Checked on 3
independent routes on 2026-11-08 -- SymPy exact arithmetic, mpmath at 40
digits and numpy -- the ratio is exactly `2240/481` and the pass counts are
14.4830 at q=0.3, 2.0202 at q=0.9 and 25.1235 at q=0.2, matching the prose to
4 decimal places. So this is `measured-rate-travels-with-its-script` broken in
the direction that is easiest to miss: a number that is RIGHT and that nothing
can produce. A reader who re-ran the script to check would have got a stack
trace, concluded the figure was unsupported, and been wrong about that too.

AND 3 OF THOSE FIGURES WERE LITERALS IN A PRINT STATEMENT sitting immediately
after the loop that computes them. They are now derived from that loop, so they
cannot drift from it.

NOTHING CAUGHT IT BECAUSE NOTHING RAN IT. The producer is 1 of the 229 dated
producers in the admitted-debt set, and 0 tests named it. This file is why the
debt is now 1 smaller rather than re-admitted -- which is the whole point of
pinning a SET rather than a total: a name leaves the set only when something
reaches it.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "scripts"
            / "the_archive_records_outcomes_not_reference_points_2026-11-02.py")


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PRODUCER), *args],
                          capture_output=True, text=True, timeout=600,
                          cwd=str(REPO))


@pytest.fixture(scope="module")
def plain():
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    return _run()


@pytest.fixture(scope="module")
def sized():
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    return _run("--sizing")


def test_it_runs_to_completion(plain):
    """It did not, and that is why this file exists."""
    assert plain.returncode == 0, (
        f"exited {plain.returncode}\nstderr tail:\n{plain.stderr[-900:]}")
    assert "NameError" not in plain.stderr
    assert "Traceback" not in plain.stderr


def test_the_closed_form_table_is_reached(plain):
    """The section the crash cut off. Its first row is where np.log died."""
    assert "n* to 0.01 from R=1" in plain.stdout, (
        "the closed-form table is missing, so the run is still stopping short")
    assert "TOOLS DISAGREE" not in plain.stdout, (
        "the mpmath and numpy routes disagree on a pass count")


def test_the_derived_pass_counts_are_in_the_output(plain):
    """The 3 figures that were literals. Now derived, so they must still match.

    Verified independently on 2026-11-08 by SymPy, mpmath and numpy: 14.4830 at
    q=0.3, 2.0202 at q=0.9, 25.1235 at q=0.2.
    """
    for figure in ("14.4830", "2.0202", "25.1235"):
        assert figure in plain.stdout, (
            f"{figure} is absent from the output. It is now derived from the "
            f"loop rather than typed, so either the maths moved or the "
            f"derivation broke -- and the figure must not simply be re-typed.")


def test_the_sizing_block_is_reachable_at_all(sized):
    """IT WAS NOT. This is the half that mattered: B84 quotes 2240/481."""
    assert sized.returncode == 0, (
        f"--sizing exited {sized.returncode}\n{sized.stderr[-900:]}")
    assert "SIZING ONLY" in sized.stdout, "the --sizing block never ran"
    assert "2240/481" in sized.stdout, (
        "the floor multiplier entry B84 quotes to the founder is not in the "
        "output, so the figure is again unproducible")
    assert "4.656965" in sized.stdout


def test_help_costs_nothing(plain):
    """His standing rule: a --help must never cost money or minutes."""
    r = _run("--help")
    assert r.returncode == 0
    assert "usage:" in (r.stdout + r.stderr).lower()


def test_both_cross_check_routes_are_actually_used(plain):
    """ANTI-VACUITY. Importing numpy and not calling it would pass every test
    above, because the crash would be gone and the table would print. The
    module must still CALL both routes, which is what the cross-check is.
    """
    src = PRODUCER.read_text(encoding="utf-8")
    assert "import numpy as np" in src, "numpy is not imported"
    live = [l for l in src.splitlines()
            if "np.log" in l and not l.lstrip().startswith("#")]
    assert live, (
        "numpy is imported and never called, so the second cross-check route "
        "is gone and a single-route figure would read as corroborated")
    assert any("mp.log" in l for l in src.splitlines()), (
        "the mpmath route is gone, so there is nothing to cross-check against")
