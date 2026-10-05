# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 34de671ad9f42c6c17e89963467c1f105975c8220914142f4c3a95d7632e3c7c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The provenance gate failed in both directions, and both were measured.

`scripts/competence_provenance.py` is the check `bench/routing.py`'s star-marked
founder warning names: run it before re-deriving `DEFAULT_FALSIFIER_STRENGTH`,
because the ladder's order is not a report -- it decides which model is asked to
resolve the hardest findings.
`experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`
goes further and makes it a GATE ON POOL ENTRY. A gate is held to a higher
standard than an advisory script, and under that standard it had two defects.

DEFECT 1 -- THE CLASSIFIER WAS A SUBSTRING MATCH, so it answered the wrong
question in the direction that inverts the ladder. `import
bench.cdsfl_registry.engine` -- the form the CDSFL core directive REQUIRES of a
code falsifier, and the form `bench/routing.py`'s own comment relies on
("a code falsifier reaches its target by `import`, which PYTHONPATH carries
regardless of working directory") -- contains none of the five tokens the regex
looked for, so it scored DETACHED. Measured over `bench/logs/`: 644 of 1034
archived CONFIRMED falsifiers scored detached and do reach the target. In the
other direction a falsifier that restated the document from memory scored READS
on the strength of `# could open(it) but I remember the numbers` in a comment.

DEFECT 2 -- THE GATE WAS PER MODEL, NOT PER CONFIRMATION. It asked
`confirmed > 0 and reads == 0`, so ONE genuine reader anywhere in the run
licensed a numerator built entirely from detached confirmations. The synthetic
registry below is the demonstration: 2 detached CONFIRMED plus 1 reading REFUTED
exited 0 and ranked that model first at 67%.

EVERY CHECK HERE EXECUTES THE CLASSIFIER OR THE GATE. Nothing asserts on the
text of a source file; that class is capped by
`bench/tests/test_source_text_and_neighbour_audit_2026-09-11.py` and four guards
of it broke on correct changes in a single day.
Producer for the figures: `scripts/provenance_gate_misreads_the_mandated_form_2026-10-05.py`.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "competence_provenance.py"
TARGET = "bench/cdsfl_registry/engine.py"


@pytest.fixture(scope="module")
def prov():
    spec = importlib.util.spec_from_file_location("competence_provenance_probe", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _entry(cid, model, code, verdict):
    return {"canonical_id": cid, "source_model": model,
            "falsifier_code": code, "falsifier_verdict": verdict}


def _report(tmp_path, entries, target=TARGET):
    d = tmp_path / "run"
    d.mkdir(exist_ok=True)
    p = d / "probe_report.json"
    p.write_text(json.dumps({"target_file": target,
                             "registry": {"entries": {e["canonical_id"]: e
                                                      for e in entries}}}),
                 encoding="utf-8")
    return p


class TestTheClassifierReadsTheParsedModule:
    def test_the_mandated_import_of_the_target_counts_as_reading_it(self, prov):
        """The case that matters most: the core directive's REQUIRED form."""
        code = ("from bench.cdsfl_registry.engine import PolicyEngine\n"
                "assert PolicyEngine().validate(), 'FALSIFIED'\n")
        assert prov.falsifier_style(code, TARGET) == "reads"

    def test_a_dotted_import_of_the_target_module_counts(self, prov):
        code = ("import bench.cdsfl_registry.engine as E\n"
                "assert E.PolicyEngine, 'FALSIFIED'\n")
        assert prov.falsifier_style(code, TARGET) == "reads"

    def test_a_token_in_a_comment_is_not_evidence_of_reading(self, prov):
        code = ("# we could open(the file) but the numbers are in the document\n"
                "assert 175 == 21, 'FALSIFIED'\n")
        assert prov.falsifier_style(code, TARGET) == "detached"

    def test_a_token_in_a_string_literal_is_not_evidence_either(self, prov):
        code = "note = 'did not open('\nassert 175 == 21, 'FALSIFIED'\n"
        assert prov.falsifier_style(code, TARGET) == "detached"

    def test_reading_some_other_file_is_its_own_category(self, prov):
        """Not `reads`, because the run's target was never named; and not
        `detached`, because it did consult a file. Conflating the two is how a
        falsifier that opens /dev/null scored as a reader."""
        code = "open('/dev/null').close()\nassert 175 == 21, 'FALSIFIED'\n"
        assert prov.falsifier_style(code, TARGET) == "elsewhere"

    def test_linecache_is_still_recognised(self, prov):
        """CC2's counterexample to a word-matching detachment test, preserved:
        linecache reads a file with none of the usual words."""
        code = f"import linecache\nlinecache.getlines({TARGET!r})\n"
        assert prov.falsifier_style(code, TARGET) == "reads"

    def test_a_subprocess_handed_the_target_counts(self, prov):
        code = (f"import subprocess\n"
                f"r = subprocess.run(['ruff', 'check', {TARGET!r}])\n"
                f"assert r.returncode == 0, 'FALSIFIED'\n")
        assert prov.falsifier_style(code, TARGET) == "reads"

    def test_absent_and_unparsable_are_distinct_from_detached(self, prov):
        assert prov.falsifier_style("", TARGET) == "none"
        assert prov.falsifier_style(None, TARGET) == "none"
        assert prov.falsifier_style("this is prose, not python {", TARGET) == "unparsable"

    def test_the_classifier_is_not_constant(self, prov):
        """ANTI-VACUITY. A classifier stuck on one answer would satisfy whichever
        half of the cases above happened to expect it."""
        genuine = f"assert 'x' in open({TARGET!r}).read(), 'FALSIFIED'\n"
        memory = "fs, fmax = 400, 180\nassert fs > fmax, 'FALSIFIED'\n"
        assert prov.falsifier_style(genuine, TARGET) == "reads"
        assert prov.falsifier_style(memory, TARGET) == "detached"

    def test_with_no_target_the_question_is_not_silently_invented(self, prov):
        """A report that records no target cannot be asked whether the TARGET was
        read. The answer must fall back to 'did it read anything', not to a
        guess, or every archived run without `target_file` becomes unsafe."""
        code = "open('/dev/null').close()\n"
        assert prov.falsifier_style(code, "") == "reads"
        assert prov.falsifier_style(code, TARGET) == "elsewhere"


class TestTheGateCountsPerConfirmation:
    def test_one_genuine_reader_does_not_license_detached_confirmations(
            self, prov, tmp_path, monkeypatch, capsys):
        """THE REGRESSION TEST FOR DEFECT 2, as the defect was demonstrated:
        2 detached CONFIRMED and 1 reading REFUTED. Under the old predicate
        (`reads == 0`) this exited 0 and ranked the model first at 67%."""
        rep = _report(tmp_path, [
            _entry("C0001", "Gemini", "assert 175 == 21, 'FALSIFIED'", "CONFIRMED"),
            _entry("C0002", "Gemini", "assert 3 == 4, 'FALSIFIED'", "CONFIRMED"),
            _entry("C0003", "Gemini",
                   f"assert 'x' in open({TARGET!r}).read()", "REFUTED"),
        ])
        monkeypatch.setattr(prov.sys, "argv", ["x", str(rep)])
        rc = prov.main()
        out = capsys.readouterr().out
        assert rc == 2, out
        assert "UNSAFE TO RANK ON" in out
        assert "2 of 2" in out, (
            "the gate does not say HOW MANY confirmations are contaminated, so a "
            "reader cannot tell a wholly detached rate from a mostly clean one")

    def test_a_wholly_clean_run_is_rankable(self, prov, tmp_path, monkeypatch, capsys):
        """ANTI-VACUITY AND POSITIVE CONTROL. A gate that refused everything
        would pass the test above and make the script useless."""
        rep = _report(tmp_path, [
            _entry("C0001", "Codex",
                   "from bench.cdsfl_registry.engine import PolicyEngine\n"
                   "assert PolicyEngine, 'FALSIFIED'", "CONFIRMED"),
            _entry("C0002", "Codex",
                   f"assert 'x' in open({TARGET!r}).read()", "CONFIRMED"),
        ])
        monkeypatch.setattr(prov.sys, "argv", ["x", str(rep)])
        rc = prov.main()
        out = capsys.readouterr().out
        assert rc == 0, out
        # the closing RULE paragraph names the phrase unconditionally, so look
        # for the per-model VERDICT form, which carries the count.
        assert "UNSAFE TO RANK ON \u2014" not in out, out

    def test_a_model_with_no_confirmations_is_not_called_unsafe(
            self, prov, tmp_path, monkeypatch, capsys):
        """A model that supplied only ERRORing readers has a SUPPLY problem, not
        a provenance one. Calling it unsafe would blame DeepSeek for the gate's
        own empty-working-directory defect."""
        rep = _report(tmp_path, [
            _entry("C0001", "DeepSeek",
                   f"assert 'x' in open({TARGET!r}).read()", "ERROR"),
            _entry("C0002", "DeepSeek",
                   f"assert 'y' in open({TARGET!r}).read()", "ERROR"),
        ])
        monkeypatch.setattr(prov.sys, "argv", ["x", str(rep)])
        rc = prov.main()
        out = capsys.readouterr().out
        assert rc == 0, out
        assert "no confirmations to rank on" in out

    def test_the_naive_and_clean_rates_are_both_reported(
            self, prov, tmp_path, monkeypatch, capsys):
        """The gap between them IS the contamination. Reporting only one of them
        is how a contaminated rate travels as a number."""
        rep = _report(tmp_path, [
            _entry("C0001", "Gemini", "assert 175 == 21, 'FALSIFIED'", "CONFIRMED"),
            _entry("C0002", "Gemini",
                   f"assert 'x' in open({TARGET!r}).read()", "CONFIRMED"),
        ])
        monkeypatch.setattr(prov.sys, "argv", ["x", str(rep)])
        rc = prov.main()
        out = capsys.readouterr().out
        per = prov.analyse(rep)["Gemini"]
        assert per["confirmed"] == 2 and per["clean_confirmed"] == 1
        assert "100%" in out and "50%" in out, out
        # A PARTLY contaminated rate is still unrankable: half the numerator
        # rests on a falsifier that never read the target.
        assert rc == 2, out
        assert "1 of 2" in out, out


class TestTheHistoricalMeasurementStillReproduces:
    """A repair to an instrument that silently moves the figure it already
    published is not a repair. Exp 55 is the measurement `bench/routing.py`
    cites, and it must survive the classifier change unchanged."""

    def test_exp55_gemini_is_still_two_of_two_detached(self, prov):
        reps = sorted(REPO.glob("bench/logs/exp55_v3_control_*/*_report.json"))
        if not reps:
            pytest.skip("no exp55 report in this checkout")
        per = prov.analyse(reps[0])
        g = per["Gemini"]
        assert g["confirmed"] == 2, dict(g)
        assert g["clean_confirmed"] == 0, dict(g)
        assert g["detached"] == 2, dict(g)

    def test_exp55_deepseek_still_supplied_genuine_readers(self, prov):
        reps = sorted(REPO.glob("bench/logs/exp55_v3_control_*/*_report.json"))
        if not reps:
            pytest.skip("no exp55 report in this checkout")
        per = prov.analyse(reps[0])
        d = per["DeepSeek"]
        assert d["confirmed"] == 0 and d["reads"] == 2, dict(d)
