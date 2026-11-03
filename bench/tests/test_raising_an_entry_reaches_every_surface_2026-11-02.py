"""The raise-an-entry checker must refuse when a surface is genuinely unreached.

WHY THIS FILE EXISTS. `scripts/raise_an_entry_2026-11-02.py` was written because
8 of 13 completed commit attempts on 2026-11-02 were refused, 0.615385, Wilson
95% [0.355229, 0.822903], and 3 of those were the same fault: an entry on the
task list whose other surfaces were not reached. A CHECKER I HAVE NOT TRIED TO
BREAK IS A HYPOTHESIS, and this one exists because I trusted my own completeness
3 times in a night and was wrong each time.

WHAT IS ASSERTED BY EXECUTION RATHER THAN BY READING. The checker's own 6 rows,
run against the live record; a nonexistent entry refused at row 1; and the
tool's inertness, because a checker that writes is a second author of his
decision aid.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / "scripts" / "raise_an_entry_2026-11-02.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_rae", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_rae"] = m
    try:
        spec.loader.exec_module(m)
    finally:
        pass
    return m


class TestItChecksTheSurfacesItClaimsTo:
    def test_it_returns_one_row_per_surface_THE_DOCSTRING_NAMES(self, mod):
        """Derive the expected SET from the tool's own docstring, not a literal.

        ★ THIS REPLACED `assert len(rows) == 6` ON 2026-11-02, AND THE LITERAL
        WENT STALE WITHIN HOURS. Surface 7 was added after this tool passed an
        entry the commit gate then refused twice, because checks 4 and 5 read
        the generator and the spoken file while a 3rd decision instrument reads
        each entry's OWN TEXT. A count assertion cannot say WHICH surface is
        missing and goes stale the moment one is added, which is the fault
        `feedback_pin_a_set_not_a_count_2026-10-16` records 5 times.

        Deriving the set from the docstring means the description and the code
        CANNOT disagree: adding a surface to one without the other turns this
        red in either direction.
        """
        declared = {int(m) for m in
                    re.findall(r"^  (\d+)\. ", mod.__doc__ or "", re.M)}
        assert declared, "the docstring no longer enumerates its surfaces"
        returned = {int(name.split(".", 1)[0]) for name, _o, _d
                    in mod.check("B87")}
        assert declared == returned, (
            f"the docstring names surfaces {sorted(declared)} and check() "
            f"returned {sorted(returned)}; a checker and its own description "
            f"must not disagree. Missing: {sorted(declared - returned)}; "
            f"unexpected: {sorted(returned - declared)}")
        assert declared == set(range(1, len(declared) + 1)), (
            f"the surface numbering has a gap or a duplicate: "
            f"{sorted(declared)}")

    def test_each_row_names_its_surface_and_carries_a_detail(self, mod):
        for name, ok, detail in mod.check("B87"):
            assert name and name[0].isdigit(), f"unnumbered surface: {name!r}"
            assert isinstance(ok, bool), f"{name}: verdict is not a boolean"
            assert detail, f"{name}: a verdict with no detail cannot be acted on"

    def test_a_nonexistent_entry_is_refused_at_the_first_surface(self, mod):
        rows = mod.check("ZZ404")
        assert rows[0][1] is False, "an absent entry must fail the marker check"
        assert len(rows) == 1, (
            "after the marker fails there is nothing to check, so the remaining "
            "surfaces must not be reported as passing on nothing")

    def test_the_live_entry_reaches_every_surface(self, mod):
        """ANTI-VACUITY. Without this, a checker that failed everything would
        satisfy the refusal test above."""
        rows = mod.check("B87")
        bad = [n for n, ok, _ in rows if not ok]
        assert not bad, (
            f"B87 was raised across every surface on 2026-11-02 and the checker "
            f"reports {bad} unreached; either the record regressed or the "
            f"checker is wrong, and both matter")


class TestItIsInert:
    def test_it_writes_nothing(self):
        """A checker that writes becomes a second author of his decision aid."""
        before = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                capture_output=True, text=True).stdout
        subprocess.run([sys.executable, str(TOOL), "--entry", "B87"],
                       cwd=ROOT, capture_output=True, text=True)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                               capture_output=True, text=True).stdout
        assert before == after, "running the checker changed the working tree"

    def test_help_is_answered_and_costs_nothing(self):
        r = subprocess.run([sys.executable, str(TOOL), "--help"],
                           cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0
        assert "usage:" in r.stdout, "a flag a caller passes must be ANSWERED"

    def test_an_unknown_flag_is_refused_loudly(self):
        r = subprocess.run([sys.executable, str(TOOL), "--entry", "B87",
                            "--bogus"], cwd=ROOT, capture_output=True, text=True)
        assert r.returncode != 0
        assert "bogus" in (r.stderr + r.stdout), (
            "a refusal must NAME the flag it refused, or the caller cannot act")


class TestItAgreesWithTheGateRatherThanWithItself:
    """Surfaces 4 and 5 call the gate's own instruments as subprocesses, so the
    checker cannot drift from what actually refuses a commit. This pins that."""

    #: Every instrument a surface must CALL rather than reimplement. Named as a
    #: SET, because the test this replaces was called
    #: `test_surface_4_and_5_are_subprocess_calls_...` and its own NAME carried
    #: a count that went stale the moment surface 7 was added -- the 4th time in
    #: one session that a count stood where a set belonged
    #: (`feedback_pin_a_set_not_a_count_2026-10-16`).
    INSTRUMENTS = (
        "morning_report_build_2026-10-12.py",                    # surface 4
        "do_the_two_decision_surfaces_agree_2026-11-01.py",      # surfaces 5, 7
        "how_many_decisions_actually_need_him_2026-11-01.py",    # surface 7
    )

    def test_every_surface_calls_its_instrument_rather_than_copying_its_rules(self):
        src = TOOL.read_text()
        missing = [i for i in self.INSTRUMENTS if i not in src]
        assert not missing, (
            f"these surfaces must CALL the real instruments rather than "
            f"reimplement their rules; a copied rule drifts and a called one "
            f"cannot. Not referenced: {missing}")
        assert "subprocess.run" in src or "spec_from_file_location" in src, (
            "no instrument is actually invoked; naming one in a comment is not "
            "calling it")

    def test_the_ticket_identity_is_derived_and_not_typed(self):
        src = TOOL.read_text()
        assert "tid_of(" in src and "from_task_list()" in src, (
            "the ticket identity must come from the harvester's derived row; a "
            "hand-built identity lands off-identity, recorded 2026-10-28")
