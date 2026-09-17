#!/usr/bin/env python3
"""The 97% removal rate must keep reproducing, or the record loses its producer.

`Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md` is where the 4-month suppression
defect was found, and it stated the rate 6 times while naming no script. A
producer now exists. This guard executes it, so the record's figures cannot
quietly stop reproducing -- which is the exact failure the producer was written
to end.

IT RUNS THE SCRIPT. Asserting on the script's source text would confirm only
that the script describes itself consistently.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "scripts" / "immune_removal_rate_exp46_2026-09-17.py"
RECORD = ROOT / "experimental_notes" / "Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md"


@pytest.fixture(scope="module")
def out():
    r = subprocess.run([sys.executable, str(PRODUCER)], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-800:] + r.stderr[-600:]
    return r.stdout


class TestTheRecordsFiguresReproduce:
    def test_the_population_is_the_one_the_record_names(self, out):
        assert "archived findings: 27" in out
        assert "pairs: 351" in out

    def test_every_declared_figure_matches(self, out):
        lines = [l for l in out.splitlines() if "declared" in l]
        assert len(lines) == 15, f"expected the record's 15 figures, saw {len(lines)}"
        differs = [l.strip() for l in lines if "DIFFERS" in l]
        assert not differs, f"the record's figures no longer reproduce: {differs}"

    def test_no_cosine_is_negative(self, out):
        """The whole defect: half the output scale was reserved for a region the
        data never visits. If a negative ever appears, the premise has changed."""
        assert "negative: 0" in out


class TestItReportsRatherThanHides:
    def test_the_comment_s_figures_reproduce_on_the_set_they_measured(self, out):
        """TURNED AROUND 2026-09-17, AND THE OLD FORM ENCODED A FALSE FINDING.

        This asserted "UNREPRODUCED": that the comment's 15.8% matched nothing.
        Rates had been computed over all 351 pairs and over the 79 sharing a class,
        never over the other 272. A test that pins a negative finding pins
        whatever search was run, including the one that was missed.
        """
        assert "SET differ272 n=272 retired 97.4 (265 of 272) clamped 15.8 (43 of 272)" in out
        assert "SET all351 n=351 retired 98.0 (344 of 351) clamped 21.4 (75 of 351)" in out
        assert "UNREPRODUCED" not in out

    def test_the_subset_is_m10s_by_medians_not_only_rates(self, out):
        """The class partition leaves only the 272, but 20 pair counts up to 351
        admit both 97.4% and 15.8%, so the set is taken from M10's label "(n=272)";
        its medians are checked as corroboration."""
        assert "pair counts up to 351 admitting both 97.4% and 15.8%: 20" in out
        assert "a count out of 351 that rounds to 15.8%: none exists" in out
        assert "M10's subset figures: REPRODUCED" in out
        assert "MISMATCH" not in out

    def test_every_figure_in_the_comment_is_tied_to_its_set(self, out):
        """The consumer checked against the producer: the comment's 4 clamping
        percentages and the 2 retired rates beside them, each tied to its set, and
        the original mislabel forbidden.

        SCOPE, STATED BECAUSE IT WAS OVERSTATED ONCE. The first version asked only
        whether each percentage appeared somewhere in the output, and passed with
        the 2 sets' labels swapped. This one fails on that swap, on a changed
        figure, and on the original "Same 351 pairs" sentence being put back. It
        does NOT check the comment's non-percentage figures (0.150, 0.460, 0.541,
        79 of 79); those are checked, from the record's side, by the declared
        figures above.
        """
        import re
        src = (ROOT / "bench" / "dm" / "_similarity.py").read_text(encoding="utf-8")
        block = src[src.index("# Map to [0, 1]. CLAMPED"):src.index("cos01 = max(0.0, cos_sim)")]
        assert "Same 351 pairs" not in block, "the original mislabel is back"
        n_label = re.search(r"\(n=(\d+)\)", block)
        assert n_label and n_label.group(1) == "272", "the comment's (n=...) no longer names the 272"
        flat = " ".join(ln.strip().lstrip("#").strip() for ln in block.splitlines())
        sets = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(
            r"SET (\w+) n=\d+ retired (\d+\.\d) \(\d+ of \d+\) clamped (\d+\.\d)", out)}
        claims = {
            "all351": re.search(r"(\d+\.\d)% -> (\d+\.\d)% flagged on all 351 pairs", flat),
            "differ272": re.search(r"(\d+\.\d)% -> (\d+\.\d)% on the 272 with no class match", flat),
        }
        for name, m in claims.items():
            assert m, f"the comment no longer states the {name} figures in a form this test reads"
            assert (m.group(1), m.group(2)) == sets[name], (
                f"the comment says {name} went {m.group(1)}% -> {m.group(2)}%; "
                f"the producer measures {sets[name][0]}% -> {sets[name][1]}%")
        r272 = re.search(r"the 272 pairs with no class match\): (\d+\.\d)% flagged", flat)
        r351 = re.search(r"\((\d+\.\d)% of all 351\)", flat)
        assert r272 and r272.group(1) == sets["differ272"][0]
        assert r351 and r351.group(1) == sets["all351"][0]
        stated = set(re.findall(r"(\d+\.\d)%", flat))
        known = {*sets["all351"], *sets["differ272"], "97.1"}
        assert stated <= known, f"the comment states {stated - known}, tied to no measured set"

    def test_the_two_scenarios_are_distinguished(self, out):
        """0.520 and 0.541 are both correct, for different sets. Collapsing them
        into a contradiction was an error made while writing this producer."""
        assert "HYPOTHETICAL" in out and "ACTUAL" in out


class TestTheRecordPointsAtIt:
    def test_the_record_names_the_producer(self):
        assert PRODUCER.name in RECORD.read_text(encoding="utf-8"), (
            "the record no longer names its producer, so a reader meeting the "
            "97% figure has no way to check it")

    def test_the_transcript_itself_was_not_rewritten(self):
        t = RECORD.read_text(encoding="utf-8")
        assert "Nothing above this line has been altered" in t
        assert t.index("Addendum, 2026-09-17") > t.index("Q6. THE 97%"), (
            "the addendum must sit after the transcript, not inside it")
