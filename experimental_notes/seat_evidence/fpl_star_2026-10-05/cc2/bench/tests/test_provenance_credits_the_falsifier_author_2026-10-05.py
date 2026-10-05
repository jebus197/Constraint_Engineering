# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fpl_star_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 19c5957f7195e82b3c2a1fece08fb82ef07dd86a5ee6be2138f03740062d4500
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A confirm rate must be credited to the model that WROTE the falsifier.

WHAT WAS WRONG (panel review 2026-10-05, claude seat; measured by
`scripts/the_provenance_gate_credits_the_wrong_model_2026-10-05.py`).

`scripts/competence_provenance.py` is the check `bench/routing.py`'s star-marked
founder observation names as the thing that must run before the ladder's order is
ever re-derived, and the proposal
`experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`
would promote it from a record to a GATE. It keyed every falsifier on the entry's
`source_model`.

But `reference_runner_v3`'s routing block, in its ``elif result.resolved:`` arm,
REPLACES `falsifier_code` with the resolving rung's falsifier and stamps
`resolved_by_routing` with that rung's label, leaving `source_model` naming the
weak model whose own falsifier failed. So every routed CONFIRMED was credited to
the model that FAILED.

MEASURED OVER THE ARCHIVE, 72 reports: 248 of 3036 registry entries, 8.169%, ALL
of them confirmations -- the entire error in the numerator. Effect on the thing
that matters, the induced ordering of the 5 real vendors by confirm rate:

    frozen DEFAULT_FALSIFIER_STRENGTH : Codex, CC2, ChatGPT, Gemini, DeepSeek
    keyed on source_model (the bug)   : Gemini, Codex, ChatGPT, DeepSeek, CC2
                                        Kendall tau vs frozen = 0.0000
    keyed on the falsifier's author   : Codex, Gemini, CC2, ChatGPT, DeepSeek
                                        Kendall tau vs frozen = +0.6000

Under the bug the instrument has ZERO rank correlation with the Exp-42
measurement it would displace, and it puts CC2 -- rung 2 of the validated ladder
-- LAST, below DeepSeek. The attribution defect alone is large enough to invert
the ladder; it is not second-order behind the selection effect.

Every assertion below CALLS the module. None reads source text.
"""
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "competence_provenance", REPO / "scripts" / "competence_provenance.py")
PROV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PROV)


class TestTheAuthorIsTheResolver:
    def test_a_routed_entry_is_credited_to_the_rung_that_resolved_it(self):
        e = {"source_model": "DeepSeek", "resolved_by_routing": "Codex",
             "falsifier_verdict": "CONFIRMED", "falsifier_code": "open('x')"}
        assert PROV.falsifier_author(e) == "Codex", (
            "a routed confirmation is still credited to the model whose own "
            "falsifier failed")

    def test_an_unrouted_entry_keeps_its_source_model(self):
        """The historical attribution must be preserved everywhere routing did not
        fire, or the fix silently rewrites 91.8% of the archive."""
        e = {"source_model": "DeepSeek", "falsifier_verdict": "CONFIRMED"}
        assert PROV.falsifier_author(e) == "DeepSeek"

    def test_an_empty_routing_stamp_does_not_shadow_the_source(self):
        for stamp in (None, "", 0):
            e = {"source_model": "CC2", "resolved_by_routing": stamp}
            assert PROV.falsifier_author(e) == "CC2", stamp

    def test_neither_field_present_is_not_an_exception(self):
        assert PROV.falsifier_author({}) == "?"


class TestItIsWiredIntoTheRateItself:
    """An addition nothing reaches is not additive: `analyse` must USE it."""

    def test_analyse_moves_the_confirmation_to_the_resolver(self, tmp_path):
        import json
        rep = tmp_path / "x_report.json"
        rep.write_text(json.dumps({"registry": {"entries": {
            # DeepSeek found it, Codex's falsifier confirmed it.
            "C0001": {"source_model": "DeepSeek", "resolved_by_routing": "Codex",
                      "falsifier_verdict": "CONFIRMED",
                      "falsifier_code": "open('t').read()"},
            # DeepSeek's own, unrouted, not confirmed.
            "C0002": {"source_model": "DeepSeek", "falsifier_verdict": "REFUTED",
                      "falsifier_code": "open('t').read()"},
        }}}))
        per = PROV.analyse(rep)
        assert per["Codex"]["confirmed"] == 1, (
            "the resolver got no credit for the falsifier it wrote")
        assert per["DeepSeek"]["confirmed"] == 0, (
            "the model whose falsifier failed is still credited with the "
            "confirmation")
        assert per["DeepSeek"]["n"] == 1 and per["Codex"]["n"] == 1, (
            "the denominator must follow the numerator, or the rate is a ratio "
            "of two different populations")

    def test_the_reattribution_is_reported_not_silent(self, tmp_path):
        """A reader comparing this output against an earlier run must be able to
        see why a number moved."""
        import json
        rep = tmp_path / "y_report.json"
        rep.write_text(json.dumps({"registry": {"entries": {
            "C0001": {"source_model": "DeepSeek", "resolved_by_routing": "Codex",
                      "falsifier_verdict": "CONFIRMED", "falsifier_code": "open('t')"},
        }}}))
        per = PROV.analyse(rep)
        assert per["Codex"]["routed_in"] == 1


class TestTheProbeIsNotVacuous:
    def test_the_old_keying_would_fail_the_first_assertion(self):
        """ANTI-VACUITY. If `falsifier_author` were reverted to `source_model`,
        the test above must be the thing that catches it."""
        e = {"source_model": "DeepSeek", "resolved_by_routing": "Codex"}
        assert (e.get("source_model") or "?") == "DeepSeek", (
            "the defect this guard was written against no longer reproduces as "
            "described, so the guard may be passing for the wrong reason")

    def test_the_archive_still_contains_the_population_this_was_measured_on(self):
        """If no archived entry carries `resolved_by_routing`, the 8.169% figure in
        this file's docstring is unreproducible and the docstring is stale."""
        import json
        reps = sorted(REPO.glob("bench/logs/*/*_report.json"))
        if not reps:
            pytest.skip("no archived reports in this checkout")
        routed = 0
        for p in reps:
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            for e in ((d.get("registry") or {}).get("entries") or {}).values():
                if isinstance(e, dict) and e.get("resolved_by_routing"):
                    routed += 1
        assert routed > 0, (
            "no archived entry carries `resolved_by_routing`, so this guard "
            "describes a population that no longer exists")
