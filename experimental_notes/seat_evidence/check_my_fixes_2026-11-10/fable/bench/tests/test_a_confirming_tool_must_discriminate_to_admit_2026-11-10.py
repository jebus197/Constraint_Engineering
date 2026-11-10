# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'check_my_fixes_2026-11-10', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ee9d5732df36f440c9e88299ce4da9f8a848054c5cb9404a34718193b005fce4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A CONFIRMED verdict admits a prose fix only if it could have come out the other way.

THE DEFECT, DEMONSTRATED BY EXECUTION ON 2026-11-10 (free-seat round). Three
B-Cell verifiers carry a CONFIRMED path whose value does not depend on the
claim's truth:

  * `_verify_astronomical` returns CONFIRMED 0.9 for BOTH "the speed of light
    is 299792458 m/s" AND the km/s variant, wrong by a factor of 1000 -- its
    constant branch extracts the numeral and never reads the unit.
  * `_verify_dimensional` (tool `dimensional_analysis`) returns CONFIRMED 0.85
    for BOTH "1 km = 1000 m" AND "1 km = 1001 m" -- it tests dimensional
    homogeneity, not numeric correctness.
  * `_verify_biological_sequence` returns CONFIRMED 0.85 from its
    pure-validity fallback for ANY claim containing a valid sequence,
    including a claim it never evaluated. Its reverse-complement branch DOES
    discriminate, which is why the exclusion is at the ADMIT PATH and not in
    the verifier: at admit time the branch that fired cannot be told apart
    from the verdict alone.

Driven through `_apply_back_gate` with `domain="physics"`, the unit-blind
confirmation gave `ok=True` for the km/s claim -- the gate would fold back a
claim wrong by 1000x. `bench/domain_immune.CANNOT_ADMIT_ALONE` now bars these
three from being the basis of an admission, and the manifest's
`secondary_only` field (his ruling of 2026-09-28: Wolfram "should never be
considered the primary falsifier route") is honoured on the same path.

THIS FILE IS THE COMMITTED MEASUREMENT behind that set, per the standing rule
that a measured rate may be cited only if the script producing it is committed
alongside it. The discrimination probes are re-run here, so the set cannot
outlive its evidence: if a listed tool learns to discriminate, the matching
probe test FAILS and the entry must be removed.

ADDITIVE in both directions: the sympy-backed admissions pinned by
`test_the_verification_set_comes_from_the_topic_2026-11-10.py` still admit
(re-asserted below), and the only admissions removed are ones demonstrated
here to be truth-blind.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(scope="module")
def ia():
    import immune_agents
    return immune_agents


@pytest.fixture(scope="module")
def di():
    import bench.domain_immune as domain_immune
    return domain_immune


@pytest.fixture(scope="module")
def manifest(ia):
    return ia._load_tool_manifest()


class _FindingView:
    def __init__(self, description: str) -> None:
        self.description = description


TRUE_C = "the speed of light is 299792458 m/s"
FALSE_C = "the speed of light is 299792458 km/s"


class TestTheProbesThatJustifyTheSet:
    """Each exclusion rests on a re-runnable demonstration, not a citation."""

    def test_astronomical_confirms_the_1000x_wrong_variant(self, ia, manifest):
        fn = getattr(ia, manifest["astronomical"]["verifier"])
        vt, vf = fn(TRUE_C), fn(FALSE_C)
        assert vt.verdict == "CONFIRMED", vt
        assert vf.verdict == "CONFIRMED", (
            "astronomical now discriminates on units; remove it from "
            "CANNOT_ADMIT_ALONE and retire this probe")

    def test_dimensional_analysis_confirms_a_false_equality(self, ia, manifest):
        fn = getattr(ia, manifest["dimensional_analysis"]["verifier"])
        vt, vf = fn("1 km = 1000 m"), fn("1 km = 1001 m")
        assert vt.verdict == "CONFIRMED", vt
        assert vf.verdict == "CONFIRMED", (
            "dimensional_analysis now checks values; remove it from "
            "CANNOT_ADMIT_ALONE and retire this probe")

    def test_biological_sequence_confirms_a_claim_it_never_evaluated(
            self, ia, manifest):
        fn = getattr(ia, manifest["biological_sequence"]["verifier"])
        v = fn("the sequence 'ATGC' proves the defendant was present")
        assert v.verdict == "CONFIRMED", (
            "the pure-validity fallback no longer confirms blindly; remove "
            "biological_sequence from CANNOT_ADMIT_ALONE and retire this probe")

    def test_biological_sequence_RC_branch_DOES_discriminate(self, ia, manifest):
        """Why the exclusion is at the admit path, not in the verifier."""
        fn = getattr(ia, manifest["biological_sequence"]["verifier"])
        t = fn("the reverse complement of 'ACGT' is 'ACGT'")
        f = fn("the reverse complement of 'ACGT' is 'AAAA'")
        assert t.verdict == "CONFIRMED", t
        assert f.verdict == "REJECTED", f


class TestTheAdmitPath:
    def test_the_false_physics_claim_no_longer_admits(self, di):
        dv = di.domain_verification_set("physics", _FindingView(FALSE_C))
        assert dv["admits"] is False, dv
        # astronomical's confirmation is RECORDED, never silently dropped
        assert any(n == "astronomical" and v == "CONFIRMED"
                   for n, v, _ in dv["verdicts"]), dv["verdicts"]
        assert "for_but_cannot_admit=" in dv["detail"], dv["detail"]
        assert "astronomical" in dv["detail"], dv["detail"]

    def test_the_true_physics_claim_also_does_not_admit_on_a_blind_tool(self, di):
        """Symmetry: the m/s claim's ONLY confirmation is the same blind
        branch, so it cannot admit either -- a confirmation that cannot
        distinguish this claim from its false variant is not evidence."""
        dv = di.domain_verification_set("physics", _FindingView(TRUE_C))
        assert dv["admits"] is False, dv

    def test_a_sympy_backed_admission_still_admits(self, di):
        """The additive direction: nothing evidence-backed was removed."""
        dv = di.domain_verification_set(
            "mathematics", _FindingView("Eq(x**2 - 1, (x-1)*(x+1))"))
        assert dv["admits"] is True, dv

    def test_a_secondary_only_tool_cannot_be_the_sole_admitter(
            self, di, manifest, monkeypatch):
        """His ruling of 2026-09-28, honoured where admission is decided.
        Wolfram is not called live (1 licensed kernel); the manifest flag is
        exercised with a stubbed verdict, which is the property under test:
        the FLAG bars admission, whatever the tool said."""
        assert manifest["wolfram"].get("secondary_only") is True
        import bench.domain_immune as dimod

        class _V:
            verdict = "CONFIRMED"
            confidence = 0.9

        cfg = dimod.DomainConfig(
            domain="physics",
            claim_patterns={"mathematical": [r".*"]},
            verification_tools={"mathematical": ["wolfram"]},
        )
        monkeypatch.setattr(dimod, "load_domain_config", lambda d: cfg)
        import immune_agents as ia_mod
        monkeypatch.setattr(
            ia_mod, ia_mod._load_tool_manifest()["wolfram"]["verifier"],
            lambda claim: _V(), raising=True)
        dv = dimod.domain_verification_set("physics", _FindingView("any claim"))
        assert dv["admits"] is False, dv
        assert "wolfram" in dv["detail"], dv["detail"]


class TestTheSetMatchesItsEvidence:
    def test_every_member_has_a_probe_in_this_file(self, di):
        """The set and the demonstrations cannot drift apart silently."""
        src = pathlib.Path(__file__).read_text(encoding="utf-8")
        for tool in di.CANNOT_ADMIT_ALONE:
            assert f'"{tool}"' in src or f"'{tool}'" in src, (
                f"{tool} is excluded from admission with no committed "
                "demonstration in this file")
