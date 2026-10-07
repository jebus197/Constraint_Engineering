#!/usr/bin/env python3
"""A confirmation must be credited to the model that WROTE the falsifier.

THE DEFECT, found by the cc2 seat in the joint round of 2026-10-05 and verified here
by execution. `scripts/competence_provenance.py` keyed its per-model tally on
`source_model` — the model that REPORTED the finding. When the routing ladder resolves
a critical, the falsifier is written by a RUNG further up the ladder and recorded in
`resolved_by_routing`; the filing model is precisely the one that FAILED to produce a
working test.

MEASURED over `bench/logs/*/runner_state.json` by
`scripts/the_provenance_gate_credits_the_filer_2026-10-06.py`: of 3158 archived
entries, 210 carry `resolved_by_routing`, and **210 of 210 name a different model from
`source_model` — 6.6498% of all entries, Wilson [5.8324%, 7.5725%]**, statsmodels and
a scipy closed form agreeing. The commonest pairs are ChatGPT-SIM filed / Codex-SIM
resolved (25), CC2-SIM / Codex-SIM (18) and DeepSeek-SIM / Codex-SIM (17).

(The cc2 seat reported 1370 of 16500, 8.3%. Same direction, wider population — it
scanned report files as well. The figure cited here is the one with a producer
committed beside it, per `measured-rate-travels-with-its-script`.)

WHY THE DIRECTION IS WHAT MAKES IT SERIOUS. This script decides whether a model's
record is SAFE TO RANK ON, and the founder has ruled that the capability ladder must
become a measured statistic rather than a frozen list of vendor names. Crediting a
strong rung's successful work to the weak filer flatters exactly the models the ladder
exists to demote — an error in the one direction that cannot self-correct, because the
flattered model then gets routed MORE work and the bias compounds.
"""
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location(
        "competence_provenance", REPO / "scripts" / "competence_provenance.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PROV = _load()


def _entry(source, resolved_by=None, verdict="CONFIRMED", code="open('t.md').read()"):
    e = {"source_model": source, "falsifier_verdict": verdict, "falsifier_code": code}
    if resolved_by:
        e["resolved_by_routing"] = resolved_by
    return e


@pytest.fixture
def report(tmp_path):
    def _write(entries):
        p = tmp_path / "r.json"
        p.write_text(json.dumps(
            {"registry": {"entries": {f"C{i:04d}": e for i, e in enumerate(entries)}}}),
            encoding="utf-8")
        return p
    return _write


class TestTheAuthorIsCredited:
    def test_a_routed_confirmation_credits_the_rung_not_the_filer(self, report):
        p = report([_entry("DeepSeek-SIM", resolved_by="Codex-SIM")])
        per = PROV.analyse(p)
        assert per.get("Codex-SIM", {}).get("confirmed") == 1, (
            "the rung that WROTE the falsifier was not credited")
        assert per.get("DeepSeek-SIM", {}).get("confirmed", 0) == 0, (
            "the filing model was credited with a confirmation it did not produce — "
            "this flatters exactly the models the ladder should demote")

    def test_an_unrouted_confirmation_still_credits_the_filer(self, report):
        """Additive: nothing changes for a finding routing never touched."""
        p = report([_entry("Gemini-SIM")])
        per = PROV.analyse(p)
        assert per.get("Gemini-SIM", {}).get("confirmed") == 1

    def test_the_routed_share_is_reported(self, report):
        """A reader must be able to see how much of a record is its own work."""
        p = report([
            _entry("DeepSeek-SIM", resolved_by="Codex-SIM"),
            _entry("Codex-SIM"),
        ])
        per = PROV.analyse(p)
        assert per["Codex-SIM"]["n"] == 2
        assert per["Codex-SIM"]["via_routing"] == 1

    def test_the_precedence_matches_the_runners_own_resolver_keys(self):
        """The in-round and sweep resolvers must win over the filer too."""
        assert PROV.falsifier_author(
            {"source_model": "A", "resolved_in_round": "B"}) == "B"
        assert PROV.falsifier_author(
            {"source_model": "A", "resolved_by_sweep": "C"}) == "C"
        assert PROV.falsifier_author({"source_model": "A"}) == "A"
        assert PROV.falsifier_author({}) == "?"


class TestTheUnsafeVerdictStillFires:
    def test_a_detached_only_record_is_still_unsafe(self, report):
        """The gate's purpose must survive the attribution change: a model whose
        confirmations rest on falsifiers that never read the target is UNSAFE."""
        p = report([_entry("X-SIM", code="assert 1 == 1  # reads nothing")])
        per = PROV.analyse(p)
        s = per["X-SIM"]
        assert s["confirmed"] > 0 and s["reads"] == 0, (
            "the detached-confirmation condition no longer reproduces, so the "
            "UNSAFE verdict this script exists for cannot fire")


class TestTheProbeIsNotVacuous:
    def test_the_old_behaviour_would_fail_these(self, report):
        """ANTI-VACUITY. Keyed on `source_model`, the first assertion above would
        credit DeepSeek-SIM. If that is no longer true the fixture has drifted."""
        e = _entry("DeepSeek-SIM", resolved_by="Codex-SIM")
        assert e["source_model"] != e["resolved_by_routing"], (
            "the fixture no longer models a routed resolution")
        assert PROV.falsifier_author(e) != e["source_model"]

    def test_the_archive_population_is_real(self):
        """The defect must affect something. 0 routed entries would make it moot."""
        import glob
        routed = 0
        for f in glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json")):
            try:
                d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            ents = ((d.get("registry") or {}).get("entries") or {})
            routed += sum(1 for e in ents.values() if e.get("resolved_by_routing"))
        assert routed > 0, (
            "0 archived entries carry resolved_by_routing, so the mis-attribution "
            "affects nothing and this guard is measuring a hypothetical")


class TestTheFilersFailureIsInItsOwnDenominator:
    """AN EMPTY RECORD MUST NOT READ AS A PERFECT ONE.

    The 2026-10-06 repair fixed the NUMERATOR: a routed confirmation is credited to
    the model that wrote the falsifier, not to the one that filed the finding. It
    left the other half open, which the cc2 seat identified and the founder ruled on
    ("Verdict. Fix it."): the filer received NOTHING on a routed entry -- not the
    confirmation, and not the failed attempt either. A model that files criticals it
    never resolves therefore accumulated no denominator at all.

    Routing fires only on a critical its source did not resolve, so a routed entry
    IS a recorded failed attempt by the filer. Counting it is not a penalty; it is
    the attempt that happened.

    Measured over the archive by `scripts/the_filers_failure_was_missing_2026-10-07.py`:
    2 of 11 models change rank, 18.1818%, Wilson [5.1368%, 47.6981%], and the
    simulated models' confirm rates fall by roughly 0.2 to 0.3 absolute once their
    failures are counted.
    """

    def test_the_filer_gets_an_attempt_it_did_not_confirm(self, report):
        p = report([_entry("Filer-SIM", resolved_by="Resolver-SIM")])
        per = PROV.analyse(p)
        assert per["Resolver-SIM"]["confirmed"] == 1
        assert per["Filer-SIM"]["n"] == 1, (
            "the filing model carries no attempt for a finding it failed to "
            "resolve, so an empty record reads as a perfect one")
        assert per["Filer-SIM"]["confirmed"] == 0, (
            "the filer was credited with a confirmation it did not produce")

    def test_a_filer_that_never_resolves_has_a_real_denominator(self, report):
        """The shape that made the omission matter: file many, resolve none."""
        p = report([_entry("Filer-SIM", resolved_by="Resolver-SIM")
                    for _ in range(5)])
        per = PROV.analyse(p)
        assert per["Filer-SIM"]["n"] == 5 and per["Filer-SIM"]["confirmed"] == 0
        rate = per["Filer-SIM"]["confirmed"] / per["Filer-SIM"]["n"]
        assert rate == 0.0, f"a model that resolved nothing scores {rate}"

    def test_an_unrouted_entry_is_counted_once_not_twice(self):
        """ANTI-DOUBLE-COUNT. When the author IS the filer there is one attempt,
        and crediting it twice would invent a denominator."""
        import json as _json
        import pathlib as _pl
        import tempfile as _tf
        with _tf.TemporaryDirectory() as td:
            p = _pl.Path(td) / "r.json"
            p.write_text(_json.dumps({"registry": {"entries": {
                "C1": {"source_model": "Solo-SIM",
                       "falsifier_verdict": "CONFIRMED",
                       "falsifier_code": "open('t').read()"}}}}), encoding="utf-8")
            per = PROV.analyse(p)
            assert per["Solo-SIM"]["n"] == 1, (
                f"an unrouted entry counted {per['Solo-SIM']['n']} attempts")

    def test_the_producer_runs_and_answers_help_for_nothing(self):
        import subprocess
        import sys as _sys
        s = REPO / "scripts" / "the_filers_failure_was_missing_2026-10-07.py"
        assert s.is_file(), "the producing script is not committed beside the figure"
        r = subprocess.run([_sys.executable, str(s), "--help"], cwd=str(REPO),
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0 and "usage:" in r.stdout
