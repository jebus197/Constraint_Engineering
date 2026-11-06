#!/usr/bin/env python3
"""The census PRODUCER must run and agree with itself, not merely exist.

★ SPECIFIED BY A FREE PANEL SEAT, 2026-11-04, AND NEVER LANDED. The blind round
asked both seats what was wrong with the period's work. One found that
`scripts/the_census_counts_what_the_reader_excludes_2026-11-04.py` -- entry
B108's own named producer, whose entry claims "exit 0" -- EXITED 1 on the
committed tree, because the B108 fix inverted the producer's oracle while its
`step_2` still asserted the pre-fix identity. The other seat specified this file
as the repair's guard. Neither landed: the regression was fixed in commit
e6857344, and 5 of the round's 10 named deliverables never reached the tree, of
which this was one.

WHY THE EXISTING GUARD COULD NOT SEE IT. The committed guard tests the census
FUNCTION. The producer is a separate program that reads the function's output and
prints a verdict, and nothing executed it. A producer and a consumer that
disagree, each individually correct, is the shape `execute-do-not-grep` names --
and the project's own record says 4 defects have been found by executing two
forms against each other and none by reading.

SO THIS FILE EXECUTES IT. Exit code, verdict integrity, and an independently
re-derived identity, with a visible skip when the founder's Responses folder is
absent rather than a silent pass.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if not (REPO / "bench").is_dir():
    REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
#: THE TARGET IS OVERRIDABLE so a mutation harness can point this guard at a
#: MUTANT COPY and prove the guard discriminates, without editing the tree. The
#: default is the committed producer, so the override is a testability
#: affordance and not a way to weaken the guard in normal use.
PRODUCER = Path(os.environ.get("CENSUS_PRODUCER") or
                (REPO / "scripts" / "the_census_counts_what_the_reader_excludes_2026-11-04.py"))
RESPONSES = Path(os.path.expanduser("~/Developer_Projects/Responses"))


@pytest.fixture(scope="module")
def run():
    """Execute the producer once and hand its real exit code to every test."""
    if not PRODUCER.is_file():
        pytest.skip(f"producer absent: {PRODUCER}")
    if not RESPONSES.is_dir():
        #: A VISIBLE SKIP, NOT A SILENT PASS. The producer reads the founder's
        #: annotated responses; without them it cannot be judged, and a test
        #: that passes on a missing corpus is the vacuous-guard fault.
        pytest.skip(f"the Responses corpus is absent at {RESPONSES}")
    p = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                       capture_output=True, text=True, timeout=600)
    return p


class TestTheProducerExecutes:
    def test_it_exits_zero(self, run):
        assert run.returncode == 0, (
            "the producer named as B108's evidence exits non-zero. Its entry "
            f"claims exit 0.\nstdout tail:\n{run.stdout[-1500:]}\n"
            f"stderr tail:\n{run.stderr[-800:]}")

    def test_it_prints_a_verdict(self, run):
        assert "VERDICT:" in run.stdout, "no verdict line was printed at all"

    def test_the_verdict_is_asserted_XOR_withheld(self, run):
        """A verdict and a failed check must never be printed together.

        The defect this replaces was exactly that shape: the producer printed
        "All structural checks held: False" beside a verdict sentence, so a
        reader quoting the verdict carried a false claim.
        """
        held = re.search(r"ALL HELD:\s*(True|False)", run.stdout)
        assert held, "the structural-check summary line is missing"
        asserted = "the census is CORRECT" in run.stdout
        assert (held.group(1) == "True") == asserted, (
            "a verdict was asserted while a structural check failed, or "
            f"withheld while all held. ALL HELD={held.group(1)}, "
            f"verdict asserted={asserted}")

    def test_every_structural_check_is_named_and_true(self, run):
        line = next((l for l in run.stdout.splitlines()
                     if "structural checks:" in l), None)
        assert line, "the producer no longer names its structural checks"
        flags = re.findall(r"(\w+)\s+(True|False)", line)
        assert flags, f"no named checks parsed from: {line!r}"
        bad = [n for n, v in flags if v != "True"]
        assert not bad, f"structural checks failed: {bad}"


class TestTheIdentityHoldsByAnIndependentRoute:
    """Re-derive the corpus identity rather than trusting the printed line.

    The producer's own claim is that the census reports only HIS annotations and
    names the excluded markers separately. That is an arithmetic identity:
    his + excluded == the readability-wide total. It is recomputed here from the
    producer's own printed figures, by a route the producer does not use, so a
    drift in either side shows up as a mismatch.
    """

    def test_his_plus_excluded_reconstructs_the_broad_total(self, run):
        his = re.search(r"(\d[\d,]*)\s+annotations", run.stdout)
        broad = re.search(r"would report\s+(\d[\d,]*)", run.stdout)
        excl = re.search(r"names\s+(\d[\d,]*)\s+excluded", run.stdout)
        assert his and broad and excl, (
            "the 3 figures the identity needs are no longer all printed; "
            "the producer's output shape changed")
        h = int(his.group(1).replace(",", ""))
        b = int(broad.group(1).replace(",", ""))
        e = int(excl.group(1).replace(",", ""))
        assert h + e == b, (
            f"the identity fails: his {h} + excluded {e} = {h + e}, "
            f"but the broad count is {b}")

    def test_the_ratio_is_stated_and_consistent(self, run):
        m = re.search(r"factor of ([\d.]+) too high", run.stdout)
        his = re.search(r"(\d[\d,]*)\s+annotations", run.stdout)
        broad = re.search(r"would report\s+(\d[\d,]*)", run.stdout)
        if not m:
            pytest.skip("the producer no longer states the ratio")
        h = int(his.group(1).replace(",", ""))
        b = int(broad.group(1).replace(",", ""))
        assert abs(float(m.group(1)) - b / h) < 5e-4, (
            f"the stated factor {m.group(1)} does not match {b}/{h} = {b / h:.4f}")
