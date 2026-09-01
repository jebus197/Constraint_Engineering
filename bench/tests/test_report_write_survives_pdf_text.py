"""A completed run must never fail to record itself because of one bad character.

Discovered 2026-07-31 while wiring the literature-retrieval cell's brief into the
panel prompt. Text extracted from a PDF can contain a LONE SURROGATE — the
unpaired half of a codepoint that survived extraction on its own. U+D835 is the
one that turned up: the high half of the mathematical-alphanumeric block, so it
appears in precisely the papers the retrieval cell fetches.

Python stores such a string without complaint and refuses to encode it. The run
report is written with `ensure_ascii=False` and a strict UTF-8 encode, so the
write raises UnicodeEncodeError AFTER the experiment has converged: every round
paid for, every finding demonstrated, and no report on disk.

THREE writes shared the exposure, not one — the final report and both HIL partial
reports. The checkpoint writes escaped only because they left `ensure_ascii` at
its default, which is luck rather than design.

The contract pinned here: the ordinary path is byte-identical to a plain strict
write (so no existing report changes by a byte), the pathological path still
produces a valid report, and the substitution is recorded IN the report — a
silently scrubbed record reads exactly like a clean one, which is worse than a
crash.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.reference_runner_v3 import _write_report_json  # noqa: E402

# The exact character that broke the run: high surrogate, no low half following.
LONE = "\ud835"


class TestTheOrdinaryPathIsUnchanged:
    def test_a_clean_report_is_byte_identical_to_a_strict_write(self, tmp_path):
        payload = {
            "experiment": "exp99", "gamma": 0.6213,
            "greek": "γ_critical rose to 0.62", "emdash": "a — b",
            "nested": {"findings": [{"id": "C0031", "sev": 0.75}]},
        }
        via_helper = tmp_path / "helper.json"
        _write_report_json(via_helper, payload)

        expected = json.dumps(payload, indent=2, ensure_ascii=False,
                              default=str).encode("utf-8")
        assert via_helper.read_bytes() == expected, (
            "the helper must not change a single byte of any report that was "
            "writable before it existed")

    def test_no_sanitisation_key_is_added_when_nothing_was_sanitised(self, tmp_path):
        p = tmp_path / "clean.json"
        _write_report_json(p, {"experiment": "exp99"})
        assert "_text_sanitised" not in json.loads(p.read_text(encoding="utf-8"))


class TestThePathologicalPath:
    def test_a_lone_surrogate_would_kill_a_strict_write(self):
        """The premise. If this ever stops raising, the guard is obsolete."""
        with pytest.raises(UnicodeEncodeError):
            f"brief: {LONE}analysis".encode("utf-8")

    def test_the_report_is_still_written(self, tmp_path):
        p = tmp_path / "report.json"
        _write_report_json(p, {"experiment": "exp99", "converged_at": 6,
                               "ouroboros_brief": f"The paper defines {LONE}(x) as..."})
        assert p.exists() and p.stat().st_size > 0

    def test_the_written_report_is_valid_utf8_and_valid_json(self, tmp_path):
        p = tmp_path / "report.json"
        _write_report_json(p, {"brief": f"{LONE}{LONE} two of them"})
        loaded = json.loads(p.read_bytes().decode("utf-8"))  # both must succeed
        assert "�� two of them" == loaded["brief"]

    def test_every_other_value_survives_intact(self, tmp_path):
        """Degrading one string must not disturb the numbers the run exists for."""
        p = tmp_path / "report.json"
        _write_report_json(p, {
            "converged_at": 6, "gamma_critical": 0.6213,
            "registry": {"C0031": {"severity": 0.75, "verdict": "CONFIRMED"}},
            "brief": f"bad {LONE} char",
        })
        out = json.loads(p.read_text(encoding="utf-8"))
        assert out["converged_at"] == 6
        assert out["gamma_critical"] == pytest.approx(0.6213)
        assert out["registry"]["C0031"] == {"severity": 0.75, "verdict": "CONFIRMED"}

    def test_the_substitution_is_recorded_in_the_report_itself(self, tmp_path):
        p = tmp_path / "report.json"
        _write_report_json(p, {"brief": f"{LONE}a{LONE}b{LONE}"})
        note = json.loads(p.read_text(encoding="utf-8"))["_text_sanitised"]
        assert note["unpaired_surrogates_replaced"] == 3, (
            "the count must be the truth about this report, not a flag")
        assert "U+FFFD" in note["note"]

    def test_it_survives_a_surrogate_buried_deep_in_the_structure(self, tmp_path):
        """The brief does not sit at the top level of a real report."""
        p = tmp_path / "report.json"
        _write_report_json(p, {"rounds": [{"findings": [
            {"id": "C1", "ouroboros": {"papers": [{"brief": f"x{LONE}y"}]}}]}]})
        out = json.loads(p.read_text(encoding="utf-8"))
        assert out["rounds"][0]["findings"][0]["ouroboros"]["papers"][0]["brief"] == "x�y"
        assert out["_text_sanitised"]["unpaired_surrogates_replaced"] == 1


class TestAllThreeReportWritesUseTheGuard:
    """The final report was the one that crashed; the other two are the same code.

    Pinned by source inspection because reaching either HIL pause in a test means
    running a full experiment. A raw `write_text(json.dumps(result, ...))` for a
    report is the shape of the defect, and it must not reappear.
    """

    def test_no_report_write_bypasses_the_guard(self):
        src = (_root / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        lines = src.splitlines()
        offenders = []
        for i, line in enumerate(lines):
            if "write_text(" not in line:
                continue
            window = "\n".join(lines[i:i + 4])
            if "ensure_ascii=False" in window and "report" in window.lower():
                offenders.append(f"line {i + 1}: {line.strip()}")
        assert not offenders, (
            "a report write is encoding non-ASCII strictly again — route it "
            "through _write_report_json:\n  " + "\n  ".join(offenders))
