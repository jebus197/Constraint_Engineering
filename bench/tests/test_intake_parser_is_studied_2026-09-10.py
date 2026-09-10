"""Task 9.3: the intake parser can now be studied by a run.

HIS RULING: "Study the parser behaviour in the next simulated run and report."

IT COULD NOT BE STUDIED. `extract_falsifiers` returned blocks and kept no record
of what it passed over. A recovery rate needs a denominator and there was none,
so every figure in task 2.1 -- 26 of 69 across a run, 1 of 9 in the round that
halted -- had to be reconstructed by hand from archived text.

THE FAIR DENOMINATOR IS THE WHOLE POINT, and reporting the raw one alone would
overstate the drop by a factor of 3. Measured over 119 archived replies carrying
a FALSIFIER label:

  * over RAW labels    : 132 of 411 = 32.1168%, Wilson [27.7862%, 36.7786%]
  * over FENCED labels : 132 of 140 = 94.2857%, Wilson [89.1297%, 97.0764%]

271 of those labels have no fence within 3 lines -- `FALSIFIER: none`, or the
word quoted in prose -- and nothing could be recovered from them. The parser
recovers 94.2857% of the labels that actually carry a block, which is a very
different picture from "the parser drops findings", and it is the honest one.
Both rates are reported so neither can be quoted alone.

6 of the 132 were recovered ONLY by the tolerant companion added on 2026-09-09.
That is the 2.1 widening's measured effect size on this sample, and it exists
because the companion was UNIONED with the strict pattern rather than replacing
it -- a replacement was tried first and measured WORSE, 4,867 against 5,295.

IT DECIDES NOTHING. No gate reads it, no status turns on it, no prompt changes.
"""
from __future__ import annotations

import ast
import glob
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

from runner_core import falsifier_intake_telemetry as telem  # noqa: E402
import reference_runner_v3 as rr  # noqa: E402

RUNNER = ROOT / "bench" / "reference_runner_v3.py"


class TestTheTelemetryMeasuresTheRightThing:
    def test_a_label_with_a_block_is_recovered(self):
        t = telem("FALSIFIER:\n```python\nassert False\n```\n")
        assert t["labels_seen"] == 1
        assert t["labels_with_a_fence_within_3_lines"] == 1
        assert t["blocks_recovered"] == 1
        assert t["recovery_rate_over_fenced_labels"] == 1.0

    def test_a_bare_label_counts_as_seen_and_not_as_fenced(self):
        """THE DISTINCTION THE FAIR DENOMINATOR RESTS ON."""
        t = telem("FALSIFIER: none, there is nothing to demonstrate here.")
        assert t["labels_seen"] == 1
        assert t["labels_with_a_fence_within_3_lines"] == 0
        assert t["blocks_recovered"] == 0
        assert t["recovery_rate_over_fenced_labels"] is None, (
            "a rate over an empty denominator must be None, not 0.0 -- 0.0 "
            "reads as total failure where nothing was recoverable")

    def test_both_rates_are_reported(self):
        t = telem("FALSIFIER: none\n\nFALSIFIER:\n```py\nx=1\n```\n")
        assert t["recovery_rate_over_raw_labels"] == pytest.approx(0.5)
        assert t["recovery_rate_over_fenced_labels"] == pytest.approx(1.0)
        assert t["recovery_rate_over_raw_labels"] < t["recovery_rate_over_fenced_labels"]

    def test_it_never_executes_anything(self):
        """PURE TEXT. A telemetry function that ran model code would be a hole."""
        t = telem("FALSIFIER:\n```python\nraise SystemExit('boom')\n```\n")
        assert t["blocks_recovered"] == 1


class TestTheArchiveGivesTheStatedFigures:
    def test_the_fenced_rate_is_high_and_the_raw_rate_is_not(self):
        # NEWEST FIRST, AND STOP WHEN THE SAMPLE IS BIG ENOUGH. Two earlier
        # versions were wrong in opposite directions. Taking the first 600 in
        # SORTED order found 0 fenced labels, because sorting puts the earliest
        # experiments first and those predate the FALSIFIER convention entirely
        # -- it sampled a period in which the thing being measured did not
        # exist. Scanning all 6,727 replies then took minutes, and a test that
        # slow is a test people skip.
        files = sorted(glob.glob(str(ROOT / "bench" / "logs" / "exp*" / "r*_*.json")),
                       reverse=True)
        if not files:
            pytest.skip("no archived replies in this clone")
        L = F = R = 0
        for f in files:
            try:
                r = json.loads(pathlib.Path(f).read_text()).get("response", "")
            except (ValueError, OSError):
                continue
            if "FALSIFIER:" not in r:
                continue
            t = telem(r)
            L += t["labels_seen"]
            F += t["labels_with_a_fence_within_3_lines"]
            R += t["blocks_recovered"]
            if F >= 120:          # enough for a tight interval; stop reading
                break
        assert F > 50, f"only {F} fenced labels; the sample is too thin"
        from statsmodels.stats.proportion import proportion_confint
        lo_f, hi_f = proportion_confint(min(R, F), F, method="wilson")
        lo_r, hi_r = proportion_confint(min(R, L), L, method="wilson")
        assert lo_f > 0.85, (
            f"recovery over fenced labels fell to [{lo_f:.4%}, {hi_f:.4%}]; the "
            f"2.1 widening may have regressed")
        assert hi_r < lo_f, (
            "the raw and fenced rates no longer differ, so the caveat that the "
            "raw rate overstates the drop needs rechecking")


class TestItIsWiredAndResetPerRun:
    def test_the_telemetry_has_a_call_site(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        called = {n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert "_note_intake" in called, (
            "the telemetry is imported and never called -- the additive "
            "standard's unwired half")

    def test_every_parse_site_is_covered(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert src.count("parse_findings(") <= src.count("_note_intake("), (
            "a reply is parsed at a site that does not record telemetry, so the "
            "denominator would be short")

    def test_the_tally_is_cleared_per_run(self):
        """A module tally never cleared reports run 2 as run 1 plus run 2."""
        src = RUNNER.read_text(encoding="utf-8")
        assert "_INTAKE_TALLY.clear()" in src, (
            "the tally survives between runs in one process, which is the defect "
            "the target-hash check already suffered on 2026-09-01")

    def test_a_broken_reply_does_not_raise(self):
        rr._INTAKE_TALLY.clear()
        rr._note_intake(None)
        rr._note_intake("")
        assert "telemetry_errors" not in rr._INTAKE_TALLY

    def test_it_accumulates(self):
        rr._INTAKE_TALLY.clear()
        rr._note_intake("FALSIFIER:\n```py\nx=1\n```\n")
        rr._note_intake("FALSIFIER: none")
        assert rr._INTAKE_TALLY["replies_examined"] == 2
        assert rr._INTAKE_TALLY["labels_seen"] == 2
        assert rr._INTAKE_TALLY["labels_with_a_fence_within_3_lines"] == 1
        assert rr._INTAKE_TALLY["blocks_recovered"] == 1
