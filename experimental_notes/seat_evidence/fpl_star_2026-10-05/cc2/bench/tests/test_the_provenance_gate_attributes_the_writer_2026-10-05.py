# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fpl_star_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2f050b3c53a53586e132565d7b8114fadfa602cde4dd7c87df6710167a117350
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The provenance gate credited the falsifier to the model that did NOT write it.

WHY THIS EXISTS. `scripts/competence_provenance.py` is the check
`bench/routing.py`'s star-marked founder warning names as the thing that must run
before `DEFAULT_FALSIFIER_STRENGTH` is ever re-derived, and
`experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`
proposes promoting it from an advisory script to a GATE on pool entry. Two defects
were found by execution in the 2026-10-05 panel review, and a gate carrying either
would admit the pool it exists to exclude.

**Defect 1 -- wrong attribution (this seat).** `analyse` keyed per-model on
`source_model`, the model that REPORTED the finding. When routing resolves a
critical, the attached falsifier was written by a ladder RUNG, and the runner records
that rung on the entry as `resolved_by_routing`. Measured over this repository's
archive: **1370 of 16500 registry entries carry `resolved_by_routing`**, so 8.3% of
all entries had their falsifier's provenance credited to the model that failed to
write a working one. The error runs in the direction that matters -- a strong rung's
successful resolutions were credited to the weak source model, flattering exactly the
models the ladder demotes. The runner already had the correct precedence in
`_corrected_copy_owner`; the gate did not use it.

**Defect 2 -- per-model aggregation (the fable seat, reproduced here).** The UNSAFE
rule read `reads == 0` over ALL of a model's entries, including REFUTED and ERRORed
ones. So 2 detached CONFIRMED entries plus 1 reading REFUTED entry gave `reads == 1`
and the pool passed.

**WHAT THESE TESTS DO NOT CLAIM.** `falsifier_style` is a regex over text, and
`test_the_gate_still_cannot_tell_reading_from_the_word_read` below pins that it is
still fooled by a decoy and by a comment. These repairs make the ACCOUNTING correct.
They do not make the CLASSIFIER behavioural, and a gate built on this script inherits
that hole. That is recorded as a limitation, not repaired here, because repairing it
requires execution-derived provenance and that is a different piece of work.
"""
import importlib.util
import json
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "competence_provenance", REPO / "scripts" / "competence_provenance.py")
PROV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PROV)

READER = 'import pathlib\nassert pathlib.Path("t.md").read_text()\n'
DETACHED = 'f_s = 200\nassert f_s > 100, "FALSIFIED"\n'


def _report(entries: dict) -> pathlib.Path:
    d = pathlib.Path(tempfile.mkdtemp()) / "x_report.json"
    d.write_text(json.dumps({"registry": {"entries": entries}}))
    return d


class TestTheWriterIsCredited:
    def test_a_routed_falsifier_is_credited_to_the_rung_not_the_source(self):
        per = PROV.analyse(_report({
            "C0001": {"source_model": "DeepSeek", "resolved_by_routing": "Codex",
                      "falsifier_code": READER, "falsifier_verdict": "CONFIRMED"},
        }))
        assert "Codex" in per, (
            f"the routing rung that wrote the falsifier is absent from the "
            f"attribution: {dict(per)}")
        assert "DeepSeek" not in per, (
            "the source model that FAILED to write a working falsifier is still "
            "being credited with the rung's confirmation")
        assert per["Codex"]["confirmed"] == 1

    def test_an_unrouted_falsifier_is_still_credited_to_its_source(self):
        """ADDITIVE: the ordinary path must be unchanged."""
        per = PROV.analyse(_report({
            "C0002": {"source_model": "Gemini", "falsifier_code": READER,
                      "falsifier_verdict": "CONFIRMED"},
        }))
        assert list(per) == ["Gemini"], dict(per)

    def test_the_precedence_matches_the_runner_s_own_rule(self):
        """The runner's `_corrected_copy_owner` is the agreed rule for the same question; this must agree with
        it rather than invent a second one. Compared by CALLING both."""
        import bench.reference_runner_v3 as R
        for entry in (
            {"source_model": "DeepSeek", "resolved_by_routing": "Codex"},
            {"source_model": "DeepSeek"},
            {"source_model": "DeepSeek", "resolved_by_routing": None},
            {"resolved_by_routing": "CC2"},
        ):
            assert PROV.falsifier_owner(entry) == R._corrected_copy_owner(entry), entry

    def test_the_archive_population_this_was_measured_on_is_real(self):
        """ANTI-VACUITY. If no archived entry carries `resolved_by_routing`, the
        1370-of-16500 figure above is stale and defect 1 affected nothing."""
        tot = routed = 0
        for p in REPO.rglob("*_report.json"):
            if ".pytest_cache" in str(p):
                continue
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            for e in ((d.get("registry") or {}).get("entries") or {}).values():
                if not isinstance(e, dict):
                    continue
                tot += 1
                routed += bool(e.get("resolved_by_routing"))
        assert tot >= 1000, f"only {tot} archived entries read; population not scanned"
        assert routed > 0, (
            f"0 of {tot} archived entries carry resolved_by_routing, so the "
            f"misattribution this test guards affected nothing and the docstring's "
            f"figure is stale")


class TestTheGateAsksPerConfirmation:
    def test_a_reading_refuted_entry_does_not_whitewash_detached_confirmations(self):
        per = PROV.analyse(_report({
            "C1": {"source_model": "Gemini", "falsifier_code": DETACHED,
                   "falsifier_verdict": "CONFIRMED"},
            "C2": {"source_model": "Gemini", "falsifier_code": DETACHED,
                   "falsifier_verdict": "CONFIRMED"},
            "C3": {"source_model": "Gemini", "falsifier_code": READER,
                   "falsifier_verdict": "REFUTED"},
        }))
        s = per["Gemini"]
        assert s["reads"] == 1 and s["confirmed"] == 2, dict(s)
        assert s["confirmed_reads"] == 0, (
            "a confirmation is being counted as resting on a reading falsifier when "
            "the reading falsifier belonged to a REFUTED entry")
        assert s["confirmed"] > 0 and s["confirmed_reads"] == 0, (
            "this is the pool the gate must refuse; the old per-model rule admitted "
            "it because reads == 1")

    def test_a_genuinely_reading_confirmation_is_still_safe(self):
        """ADDITIVE in the other direction: the gate must not start refusing clean
        pools, or it stops being usable as a gate at all."""
        per = PROV.analyse(_report({
            "C1": {"source_model": "Codex", "falsifier_code": READER,
                   "falsifier_verdict": "CONFIRMED"},
        }))
        s = per["Codex"]
        assert not (s["confirmed"] > 0 and s["confirmed_reads"] == 0)

    def test_the_whitewash_pool_exits_two_end_to_end(self, capsys, monkeypatch):
        """EXECUTED through `main`, not through the counters, so the exit code a
        caller would gate on is the thing measured."""
        rep = _report({
            "C1": {"source_model": "Gemini", "falsifier_code": DETACHED,
                   "falsifier_verdict": "CONFIRMED"},
            "C2": {"source_model": "Gemini", "falsifier_code": READER,
                   "falsifier_verdict": "REFUTED"},
        })
        monkeypatch.setattr(PROV.sys, "argv", ["x", str(rep)])
        rc = PROV.main()
        out = capsys.readouterr().out
        assert rc == 2, f"a detached-confirmation pool exited {rc}, so a gate would admit it"
        assert "UNSAFE TO RANK ON" in out


class TestTheKnownRemainingHole:
    """Pinned so a future reader does not mistake the repairs above for a fix to
    the classifier. If these two ever start passing, the classifier has become
    behavioural and the proposal's gating argument must be rewritten."""

    @pytest.mark.parametrize("code,why", [
        ('assert 1 == 2, "FALSIFIED"\nopen("/dev/null")\n',
         "a decoy open of a file that is not the target"),
        ('# we would open(the target) but the number is recalled\nassert 1 == 2\n',
         "the word open( inside a COMMENT"),
        ('"""this falsifier does not read_text anything"""\nassert 1 == 2\n',
         "a docstring mentioning read_text"),
    ])
    def test_the_gate_still_cannot_tell_reading_from_the_word_read(self, code, why):
        assert PROV.falsifier_style(code) == "reads", (
            f"{why} is no longer classified as reading. That is an IMPROVEMENT, but "
            f"the limitation recorded in this file's docstring and in the script's "
            f"own header is now stale and both must be rewritten.")
