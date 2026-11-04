"""Guard for B127: his blinkered-depth hypothesis, and the producer that tests it.

`reasoning-depth-before-breadth` marks one half of its failure analysis
`[SPECULATIVE]` and writes a decision rule so the test can fail: the hypothesis
holds if the second-context share's Wilson 95% lower bound exceeds 0.5000.
`scripts/is_depth_alone_blinkered_2026-11-04.py` measures it over the
2026-11-04 budget and reports 3 readings, because the observed partition has a
third category -- an INSTRUMENT firing -- that the binary rule has no slot for.

WHAT THIS GUARD HOLDS, and why each assertion is here rather than decorative:

  * the producer runs and answers --help without measuring, because the
    measurement streams the git log and the task list;
  * its PROVENANCE CHECK actually discriminates. Every attribution it reports
    is verified by locating the quoted words in the record, and a quote it
    cannot find is DOWNGRADED to DECLARED. A verifier that found everything
    would be indistinguishable from one that checked nothing, so this test
    plants an unfindable quote and requires the downgrade to happen;
  * the whitespace normalisation is held, because the first version of that
    check matched literally and reported 15 of 23 rows unfindable purely
    because commit messages are hard-wrapped;
  * the rule's verdict is reported for all 3 readings rather than 1.

It does NOT assert the hypothesis is false in general. The producer's own
verdict states the scope: 1 budget, n = 25, upper bounds reaching 0.475766.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = REPO / "scripts" / "is_depth_alone_blinkered_2026-11-04.py"


@pytest.fixture(scope="module")
def mod():
    if not PROD.is_file():
        pytest.fail(f"the producer is not at {PROD}")
    spec = importlib.util.spec_from_file_location("_blinkered", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_blinkered"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def run_out():
    r = subprocess.run([sys.executable, str(PROD)],
                       capture_output=True, text=True, cwd=str(REPO))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return r.stdout


class TestTheProducerRuns:
    def test_help_does_not_measure(self):
        """The measurement streams the git log; --help must not pay for it."""
        r = subprocess.run([sys.executable, str(PROD), "--help"],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, r.stderr[-800:]
        assert "usage:" in r.stdout.lower()
        assert "VERDICT" not in r.stdout, (
            "--help printed the verdict, so it ran the whole measurement")

    def test_all_three_readings_are_reported(self, run_out):
        labels = re.findall(r"^\s+([ABC])\. ", run_out, re.M)
        assert set(labels) == {"A", "B", "C"}, (
            f"expected 3 readings A, B and C; found {sorted(set(labels))}. "
            f"A binary rule mis-assigns the instrument category whichever way "
            f"it is read, which is why all 3 are reported.")

    def test_the_rule_is_evaluated_and_not_merely_described(self, run_out):
        verdicts = re.findall(r"HIS RULE: Wilson lower bound ([\d.]+) > 0\.5 \? (\w+)",
                              run_out)
        assert len(verdicts) == 3, f"expected 3 rule evaluations, got {verdicts}"
        for lower, met in verdicts:
            assert met == "False", (
                f"a reading reports the rule MET at lower bound {lower}; the "
                f"entry text and the verdict both say it is not met on this "
                f"budget, so one of them is now wrong")
            assert float(lower) < 0.5


class TestTheProvenanceCheckDiscriminates:
    """A verifier that finds everything is indistinguishable from none."""

    def test_whitespace_is_normalised(self, mod):
        """Held because matching literally reported 15 of 23 as unfindable."""
        assert mod._flat("  A  B\nC  ") == "a b c"
        assert mod._flat("answered --help\nby running") == "answered --help by running"

    def test_a_findable_quote_is_kept(self, mod):
        v = mod._verify_quotes()
        assert v["found"], "no attribution verified at all, so the check is inert"

    def test_an_unfindable_quote_is_downgraded(self, mod, monkeypatch):
        """PLANTED NEGATIVE. Without this the check could pass vacuously."""
        planted = list(mod.DEFECTS) + [
            ("a defect that never happened", mod.FIRST, "COMMITTED",
             "zzqq this string appears nowhere in the record zzqq"),
        ]
        monkeypatch.setattr(mod, "DEFECTS", planted)
        v = mod._verify_quotes()
        lost = [n for n, _ in v["lost"]]
        assert "a defect that never happened" in lost, (
            "a quote that appears nowhere was accepted as COMMITTED, so the "
            "provenance label is doing no work")

    def test_the_declared_share_is_reported_as_a_figure(self, run_out):
        assert "rows attributed by MY judgement" in run_out
        m = re.search(r"rows attributed by MY judgement[^\n]*\n\s+(\d+) of (\d+)",
                      run_out)
        assert m, "the self-classification exposure is not reported as a figure"
        k, n = int(m.group(1)), int(m.group(2))
        assert n >= 20, f"only {n} defects classified; the budget was larger"
        assert k < n, "every row is my judgement, so no row is auditable"


class TestThePartitionHasThreeParts:
    def test_three_buckets_exist_and_are_distinct(self, mod):
        assert len({mod.SECOND, mod.FIRST, mod.INSTRUMENT}) == 3

    def test_each_bucket_is_populated(self, mod):
        counts = {b: sum(1 for d in mod.DEFECTS if d[1] == b)
                  for b in (mod.SECOND, mod.FIRST, mod.INSTRUMENT)}
        for bucket, n in counts.items():
            assert n > 0, (
                f"{bucket} is empty, so the 3-part claim this entry rests on "
                f"is no longer supported by its own table")

    def test_the_instrument_bucket_is_why_three_readings_exist(self, mod, run_out):
        n_inst = sum(1 for d in mod.DEFECTS if d[1] == mod.INSTRUMENT)
        assert f"{n_inst} of " in run_out or str(n_inst) in run_out
        assert "which his binary" in run_out, (
            "the verdict no longer names the missing category, which is the "
            "finding this entry reports as more important than the share")
