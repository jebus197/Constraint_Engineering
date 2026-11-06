#!/usr/bin/env python3
"""GUARD for scripts/the_line_caps_were_never_his_2026-11-06.py.

The producer answers a question he asked directly: did he ever specify a
line cap for the notes and the spoken files? Its answer -- 0 of 1,678 --
was quoted to him, so it needs a guard that goes red if the producer stops
being able to find the evidence, or starts finding evidence that is not
there.

What is pinned, and why each one can actually fail:
  * ANTI-VACUITY. 0 of 0 is also "0". The corpus must be large, so a
    reader that silently returns nothing cannot pass as a negative result.
  * PROVENANCE. The numbers must be found in exactly 1 of the standards,
    and it must be v1, the archival one -- not the current v1.9. If a
    later standard gains a length rule, this goes red and the claim that
    the gate enforces an archival number must be restated.
  * THE LABEL. "Rule 10" must be defined in 0 standards. The generator
    cites that label; if it ever becomes real, this goes red.
  * THE INTERVAL CONTRACT. _iv must return 2 DISTINCT families, each by 2
    routes. A helper that computed Wilson twice would satisfy a
    disagreement check and still leave 1 family unverified -- that is the
    exact defect that caused 12 of the 17 failures on the 2026-11-04 board.
"""
from __future__ import annotations
import importlib.util, pathlib, re, subprocess, sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PROD = ROOT / "scripts" / "the_line_caps_were_never_his_2026-11-06.py"


def _load():
    spec = importlib.util.spec_from_file_location("linecaps_producer", PROD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def out():
    r = subprocess.run([sys.executable, str(PROD)], cwd=ROOT,
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


@pytest.fixture(scope="module")
def mod():
    return _load()


class TestTheProducerExists:
    def test_the_producer_is_on_disk(self):
        assert PROD.exists(), f"the figure has no producer: {PROD}"


class TestHisOwnWords:
    def test_he_never_stated_a_numeric_length_limit(self, out):
        m = re.search(r"his blocks stating a numeric length limit: (\d+) of (\d+)", out)
        assert m, out[-3000:]
        k, n = int(m.group(1)), int(m.group(2))
        assert k == 0, f"{k} of his blocks now state a numeric length limit; restate the claim"

    def test_the_corpus_is_not_empty(self, out):
        """0 of 0 is also 0. A silent reader must not read as a negative result."""
        m = re.search(r"his blocks stating a numeric length limit: (\d+) of (\d+)", out)
        n = int(m.group(2))
        assert n >= 1000, f"only {n} annotation blocks scanned; the negative result is vacuous"

    def test_his_over_narration_instruction_is_found(self, out):
        m = re.search(r"his blocks saying 'over narration': (\d+)", out)
        assert m and int(m.group(1)) >= 1, "his actual instruction is no longer locatable"


class TestProvenance:
    def test_the_numbers_live_in_exactly_one_standard_and_it_is_v1(self, out):
        m = re.search(r"files DEFINING a Rule 10 or the numbers: (\d+) \[(.*?)\]", out)
        assert m, out[-3000:]
        assert int(m.group(1)) == 1, f"expected 1 defining standard, found {m.group(1)}"
        assert "v1.md" in m.group(2), f"the defining standard moved: {m.group(2)}"

    def test_the_current_standard_carries_no_length_rule(self):
        cur = pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_note_standard_v1.9.md"
        assert cur.exists()
        t = cur.read_text(errors="replace")
        assert not re.search(r"\b(40\s*(?:to|-)\s*300|60\s*(?:to|-)\s*400)\b", t), \
            "v1.9 has gained a length rule; the 'archival number' claim must be restated"

    def test_the_rule_10_label_is_defined_nowhere(self, out):
        m = re.search(r"files even MENTIONING Rule 10:\s+(\d+)", out)
        assert m, out[-3000:]
        assert int(m.group(1)) == 0, \
            f"'Rule 10' now appears in {m.group(1)} standard(s); the generator's citation may be valid"

    def test_the_generator_still_cites_the_phantom_label(self):
        """If the generator is repaired, THIS test must be updated, not the claim."""
        gen = (ROOT / "scripts" / "morning_report_build_2026-10-12.py").read_text(errors="replace")
        assert re.search(r"Rule 10", gen), \
            "the generator no longer cites Rule 10 -- update this guard and the finding together"


class TestTheIntervalContract:
    def test_it_returns_two_families_and_a_magnitude(self, mod):
        (wl, wh), (cl, ch), dis = mod._iv(3, 26)
        assert 0.0 <= wl < wh <= 1.0
        assert 0.0 <= cl < ch <= 1.0
        assert isinstance(dis, float) and dis < 1e-6

    def test_the_two_families_are_genuinely_different(self, mod):
        """A helper computing Wilson TWICE would pass a disagreement check and
        leave Clopper-Pearson unverified. That was 12 of 17 board failures."""
        (wl, wh), (cl, ch), _ = mod._iv(3, 26)
        assert abs(wl - cl) > 1e-9 or abs(wh - ch) > 1e-9, \
            "the 2 interval families are identical; one of them is not being computed"

    def test_the_zero_and_full_edges_do_not_crash(self, mod):
        (wl, wh), (cl, ch), dis = mod._iv(0, 1678)
        assert wl == 0.0 and cl == 0.0 and wh < 0.01 and dis < 1e-6
        (wl2, wh2), (cl2, ch2), dis2 = mod._iv(26, 26)
        assert wh2 == 1.0 and ch2 == 1.0 and dis2 < 1e-6

    def test_an_empty_denominator_is_the_whole_interval(self, mod):
        (wl, wh), (cl, ch), dis = mod._iv(0, 0)
        assert (wl, wh) == (0.0, 1.0) and (cl, ch) == (0.0, 1.0)


class TestAttributionIsAFloorNotACount:
    def test_the_scan_reports_its_own_blind_spot_subjects(self, out):
        """The morning report says 'your cap of 300' and the scan's pattern
        misses it. The figure is a FLOOR and the guard records that."""
        m = re.search(r"attributed to him: (\d+) of (\d+)", out)
        assert m, out[-3000:]
        k = int(m.group(1))
        assert k >= 2, f"only {k} attributing artefacts found; the pattern has broken"
        rep = ROOT / "experimental_notes" / "Morning_Report_2026-11-06.md"
        if rep.exists():
            assert re.search(r"your cap", rep.read_text(errors="replace"), re.I), \
                "the report no longer says 'your cap' -- the floor claim needs restating"
