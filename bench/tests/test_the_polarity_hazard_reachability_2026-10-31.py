"""Guard for `scripts/is_the_polarity_hazard_reachable_2026-10-31.py`.

EVERY assertion here CALLS the producer's own function. None restates a
decision. That is not a style preference: on 2026-10-31, 5 guards written
earlier the same day passed with their defect restored, and every one of them
failed the same way -- the test recomputed the decision instead of asking the
subject for it, so the subject's own text was never exercised.

The 3 defects pinned below were all live in the producer's first run and all 3
changed a reported figure:

  1. The live-reference grep counted THE PRODUCER'S OWN TEXT. The first run
     reported 5 live references to `verification_polarity`; all 5 were lines of
     the script doing the reporting. True count: 0.
  2. The entry predicate required "finding_id", which the RESOLVED registry
     entry does not carry -- it is keyed by `canonical_id`. The first run
     therefore collected 29,755 dicts of which every single one had status
     None, and printed the exposure census as 0 and 0. Those zeros were zeros
     of nothing.
  3. The regime boundary. The whole headline rests on splitting runs at the
     2026-08-30 ask-wire, so an off-by-one at the boundary moves entries
     between arms.
"""
import importlib.util
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROD = os.path.join(REPO, "scripts", "is_the_polarity_hazard_reachable_2026-10-31.py")


def _load():
    spec = importlib.util.spec_from_file_location("polarity_reach", PROD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["polarity_reach"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def prod():
    assert os.path.exists(PROD), f"producer missing: {PROD}"
    return _load()


class TestTheRegimeBoundary:
    """Defect 3. The split at the ask-wire decides which arm an entry joins."""

    def test_the_day_before_the_wire_is_pre(self, prod):
        assert prod.regime_of("someRun_20260829T235959Z") == "pre"

    def test_the_wire_day_itself_is_post(self, prod):
        # The wire landed ON 2026-08-30, so that day is the first post day.
        # An inclusive comparison here would move a whole day into `pre`.
        assert prod.regime_of("someRun_20260830T000000Z") == "post"

    def test_a_run_with_no_stamp_joins_neither_arm(self, prod):
        # 24 archived entries have no parsable stamp. They must be EXCLUDED
        # from both arms and counted, not silently defaulted into one.
        assert prod.regime_of("commissioning_arm1_panel") is None
        assert prod.regime_of("") is None
        assert prod.regime_of(None) is None

    def test_the_boundary_is_a_parameter_not_a_constant(self, prod):
        # Moving the wire must move the classification, or the split is a
        # hardcoded answer rather than a measurement.
        assert prod.regime_of("r_20260901T000000Z", wire="20260930") == "pre"
        assert prod.regime_of("r_20260901T000000Z", wire="20260801") == "post"


class TestTheEntryPredicate:
    """Defect 2. The resolved registry entry is keyed by canonical_id."""

    def test_a_canonical_id_entry_is_collected(self, prod):
        out = []
        prod.walk_entries({"canonical_id": "C0001", "status": "CONFIRMED"}, out)
        assert len(out) == 1, (
            "the resolved registry entry carries canonical_id and NO finding_id; "
            "requiring finding_id is what made 29,755 collected dicts all have "
            "status None")

    def test_a_falsifier_verdict_entry_is_collected(self, prod):
        out = []
        prod.walk_entries({"falsifier_verdict": "CONFIRMED"}, out)
        assert len(out) == 1

    def test_a_dict_that_is_not_an_entry_is_not_collected(self, prod):
        # Discriminating fixture: the predicate must REJECT as well as accept,
        # or it would collect every dict in the archive and the denominator
        # would be meaningless.
        out = []
        prod.walk_entries({"round": 3, "gamma": 0.5, "severity": 0.9}, out)
        assert out == []

    def test_entries_are_found_at_depth(self, prod):
        out = []
        prod.walk_entries(
            {"registry": {"entries": {"C0001": {"canonical_id": "C0001"},
                                      "C0002": {"canonical_id": "C0002"}}}}, out)
        assert len(out) == 2, "the registry sits 2 levels down in runner_state.json"


class TestTheProducerDoesNotMeasureItself:
    """Defect 1. An instrument that counts its own text measures nothing."""

    def test_the_producers_own_lines_are_excluded(self, prod):
        # The producer's source contains the literal "verification_polarity"
        # many times over -- in its docstring, its LIVE_NAMES tuple and its
        # census line. A grep that counts those reports a live reference that
        # does not exist.
        with open(PROD) as fh:
            own = fh.read()
        assert "verification_polarity" in own, (
            "fixture precondition: the producer must mention the term for this "
            "test to have teeth")
        # ★ THE ONLY LEGITIMATE LIVE REFERENCE, ADDED 2026-11-01. This asserted
        # ZERO live references, because the hazard was PROSPECTIVE: the field
        # was read by nothing, and any hit was the producer counting its own
        # text. On his ruling of 2026-11-01 the seat's proof verifier was fixed
        # and folded back, and it reads that field in order to HANDLE the
        # polarity correctly. So the hazard is now addressed rather than
        # prospective, and `bench/proof_verify.py` is the module that addresses
        # it -- the opposite of a hazard.
        #
        # THE TEST'S PURPOSE IS UNCHANGED: an instrument that counts its own
        # text measures nothing. Anything OTHER than the module that implements
        # the handling still fails here, so a future reader cannot quietly
        # reintroduce an unhandled reference.
        #: ★ A SECOND MODULE NOW HANDLES IT, ADDED 2026-11-10 ON HIS B22
        #: INSTRUCTION, and this is the extension the comment above
        #: anticipates rather than a weakening of the check.
        #: `_apply_back_gate` ROUTES on the field: an entry declaring proof
        #: polarity goes to `verify_proof` instead of to the falsifier probe,
        #: BEFORE that probe, because a proof lives in the same
        #: `falsifier_code` field and under falsifier polarity a correct proof
        #: exits cleanly, reads as REFUTED, and would score as a refutation
        #: for being right. Reading the field in order to route away from the
        #: inverting path is handling the hazard, not an instance of it.
        #:
        #: THE TEST'S FORCE IS UNCHANGED: any file OTHER than these 2 still
        #: fails, so an unhandled reference cannot be reintroduced quietly.
        #: Adding a module here is a deliberate act with a reason attached,
        #: which is the point of keeping the set explicit rather than widening
        #: it to a pattern.
        ADDRESSES_IT = ("bench/proof_verify.py",
                        "bench/reference_runner_v3.py")
        stray = [h for h in prod.live_hits("verification_polarity")
                 if not h.startswith(ADDRESSES_IT)]
        assert stray == [], (
            f"live references to verification_polarity must come only from "
            f"{ADDRESSES_IT}, which exist to handle the polarity. These do "
            f"not: {stray}")
        assert any(h.startswith(ADDRESSES_IT)
                   for h in prod.live_hits("verification_polarity")), (
            f"{ADDRESSES_IT} no longer reads verification_polarity, so either "
            f"the fold-back was reverted or the handling has been removed")

    def test_the_filter_still_finds_a_term_that_IS_live(self, prod):
        # Control. Without this, the test above is satisfied by a grep that
        # returns nothing at all, which would hide a broken search.
        hits = prod.live_hits("apply_falsifier_verdicts")
        assert hits, ("the filter must still find a term that really is live, "
                      "or the 0 above proves only that the search is broken")
        assert any("reference_runner_v3" in h for h in hits)
