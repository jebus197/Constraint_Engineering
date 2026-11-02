"""A mypy run that checked nothing must not be reported as clean.

WHAT WAS WRONG. `bench/openrouter_tools._run_mypy` passes
`--ignore-missing-imports`, which does not merely silence a warning: it
substitutes `Any` for a module mypy cannot find, and every attribute of `Any`
type-checks trivially. So a file importing an absent module -- a typo, a deleted
module, an uninstalled dependency -- exited 0 and was handed to a panel seat as
`status: "ok"`. A clean verdict on a file nothing was checked in.

THIS IS THE STANDING WOLFRAM RULE IN A DIFFERENT TOOL. The project already holds
that a call which verified nothing must never be recorded as confirming anything,
and that a failure which does not look like a failure is the most expensive defect
this harness can carry, because every downstream stage treats it as evidence.

★ TWO CLAIMS WERE WITHDRAWN IN THE COURSE OF FIXING THIS, AND BOTH WITHDRAWALS ARE
PINNED HERE SO THEY CANNOT QUIETLY RETURN.

  1. ENTRY B21 claimed `mypy_check` "returns `status: \"ok\"` for files it could
     not type". It does not: `_run_mypy` maps a non-zero returncode to "errors",
     so an import FAILURE is loud. `test_a_file_mypy_cannot_parse_is_reported_as_errors`.

  2. I THEN CLAIMED the "ok" was vacuous because bare-name project imports do not
     resolve. That was an artefact of my probe living in a TEMPORARY DIRECTORY.
     Because the tree has no `bench/__init__.py`, mypy treats each bench file as a
     top-level module and puts `bench/` on its own search path, so a sibling
     bare-name import RESOLVES.
     `test_a_bare_name_sibling_import_resolves_from_inside_bench`.

So the defect is narrow and real, and the fix is correspondingly narrow: an
unfindable import, not the tree's mypy configuration, whose installation remains a
decision recorded as the founder's in B21.

Producer: `scripts/does_mypy_check_anything_2026-11-02.py`.
"""
from __future__ import annotations

import pathlib
import sys
import uuid

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.openrouter_tools import (                            # noqa: E402
    _mypy_imports_were_unresolved, _run_mypy)


@pytest.fixture
def probe_in_bench():
    """Write a throwaway module inside bench/ and always remove it.

    It has to live in `bench/` rather than a temp directory, because the probe's
    LOCATION is what decides whether sibling imports resolve -- the mistake this
    file's docstring records. The name is unique per call so a crashed run cannot
    leave a file that collides with the next one.
    """
    made: list[pathlib.Path] = []

    def _write(body: str) -> str:
        p = REPO / "bench" / f"_tmp_mypy_guard_{uuid.uuid4().hex[:10]}.py"
        p.write_text(body)
        made.append(p)
        return f"bench/{p.name}"

    try:
        yield _write
    finally:
        for p in made:
            p.unlink(missing_ok=True)


class TestTheRepair:
    """An unfindable import must not come back as clean."""

    def test_an_absent_import_is_not_reported_as_ok(self, probe_in_bench):
        rel = probe_in_bench(
            "import a_module_that_truly_does_not_exist_xyz\n"
            "x = a_module_that_truly_does_not_exist_xyz.anything\n"
            "y: int = x\n")
        r = _run_mypy(rel)
        assert r["returncode"] == 0, (
            "mypy no longer exits 0 on an absent import under these flags; the "
            "premise of this guard has changed rather than the code being wrong")
        assert r["status"] == "ok_but_nothing_was_checked", (
            f"got {r['status']!r}; a file whose import mypy could not find was "
            f"checked against Any and must not be reported as clean")
        assert r["unresolved_imports"] >= 1
        assert "could not be FOUND" in r["caveat"]

    def test_a_genuinely_clean_file_is_still_ok(self, probe_in_bench):
        """The control. Without it, a blanket downgrade would pass the test above.

        This is the property that keeps the change ADDITIVE: no existing clean
        verdict is lost, only a verdict that was never earned.
        """
        rel = probe_in_bench(
            "import json\n"
            "\n"
            "def n() -> int:\n"
            "    return len(json.dumps({}))\n")
        r = _run_mypy(rel)
        assert r["status"] == "ok", (
            f"got {r['status']!r}; a stdlib-only file with no type errors must "
            f"still be reported as clean, or the repair is a blanket downgrade")
        assert "caveat" not in r

    def test_a_real_type_error_is_still_errors(self, probe_in_bench):
        """The other control: the loud path is untouched."""
        rel = probe_in_bench("x: int = 'not an int'\n")
        r = _run_mypy(rel)
        assert r["status"] == "errors"
        assert r["returncode"] != 0


class TestTheTwoWithdrawnClaims:
    """Pinned so neither overstatement can return unnoticed."""

    def test_a_file_mypy_cannot_parse_is_reported_as_errors(self, probe_in_bench):
        """B21's claim, refuted. A non-zero returncode is reported loudly."""
        rel = probe_in_bench("def broken(  :\n")        # a syntax error
        r = _run_mypy(rel)
        assert r["status"] == "errors", (
            "B21 claims this surfaces as 'ok'; it does not, and that claim is "
            "withdrawn in the entry")

    def test_a_bare_name_sibling_import_resolves_from_inside_bench(self, probe_in_bench):
        """My own claim, refuted, with the planted error that settles it.

        `season_strength_order` really is in `bench/routing.py` and really does
        take a required argument, so calling it with one positional argument is
        an error mypy MUST report if the import resolved.
        """
        rel = probe_in_bench(
            "from routing import season_strength_order\n"
            "\n"
            "def go() -> int:\n"
            "    x: int = season_strength_order(12345)\n"
            "    return x\n")
        r = _run_mypy(rel)
        assert r["status"] == "errors", (
            f"got {r['status']!r}; if the sibling import did NOT resolve this "
            f"would be a silent 'ok', and the withdrawn claim would stand")
        assert "season_strength_order" in r["output"], (
            "the planted call-arg error is not reported, so bare-name sibling "
            "imports are not resolving after all")

    def test_there_is_still_no_bench_init_which_is_why_they_resolve(self):
        """The mechanism behind the withdrawal, asserted rather than assumed.

        If a `bench/__init__.py` is ever added, bench files become a package,
        bare-name sibling imports STOP resolving, and the withdrawn claim becomes
        true. This test is the tripwire for that, and it must be read as a
        prompt to re-measure rather than as a prohibition.
        """
        assert not (REPO / "bench" / "__init__.py").is_file(), (
            "bench/ is now a package. Bare-name sibling imports may no longer "
            "resolve, so re-run scripts/does_mypy_check_anything_2026-11-02.py "
            "and revisit the withdrawal recorded in entry B21.")


class TestTheDetector:
    """The predicate itself, with a control, because a detector that always says
    yes would satisfy every test above."""

    def test_it_detects_an_absent_module(self, tmp_path):
        p = tmp_path / "m.py"
        p.write_text("import definitely_absent_module_abc\n"
                     "x = definitely_absent_module_abc.y\n")
        unresolved, n = _mypy_imports_were_unresolved(p)
        assert unresolved is True and n >= 1

    def test_it_stays_quiet_on_a_stdlib_only_file(self, tmp_path):
        p = tmp_path / "c.py"
        p.write_text("import json\nx: str = json.dumps({})\n")
        assert _mypy_imports_were_unresolved(p) == (False, 0)
