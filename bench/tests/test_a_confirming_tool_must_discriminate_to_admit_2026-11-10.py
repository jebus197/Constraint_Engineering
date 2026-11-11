"""AN ADMISSION NEEDS A VERDICT THAT COULD HAVE COME OUT THE OTHER WAY.

A verdict taking the SAME value on a claim and on a false variant of that
claim carries 0 bits about the claim. Admitting a fix on it is admission by
vocabulary, not by tool. `bench/domain_immune.py` therefore narrows which
favourable verdicts may admit ALONE, by 2 mechanisms:

  CANNOT_ADMIT_ALONE      -- tools measured truth-blind at the TOOL level
  BRANCH_GATED_ADMISSION  -- 1 tool measured truth-blind on SOME branches only

PROVENANCE, because it matters for how this file reads. The defect was first
narrowed by me to 2 tools on a measurement that found `biological_sequence`
DISCRIMINATING. A FREE PANEL SEAT REFUTED THAT and was right: the tool has 5
favourable branches, 4 comparing and 1 validity-only, and my probe had hit a
comparing one and generalised. The seat proposed excluding the tool outright.
That was then measured too, and REFUSED, because it scores worse on both named
properties than gating the tool at its branch -- and the same measurement
turned up a third truth-blind tool, `chemistry_structure`, which the seat had
explicitly judged safe because its own probes never drew a CONFIRMED from it.

Producer: `scripts/which_admissions_are_truth_blind_2026-11-10.py`.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import domain_immune as di                                    # noqa: E402

MARKER = "matches claim"


class _F:
    #: ★ `fix` DEFAULTS TO EMPTY, AND THAT DEFAULT IS DELIBERATE. From the
    #: founder's ruling of 2026-11-11 -- *"Keep both the claim prose, and the
    #: proposed fix."* -- an admission needs BOTH texts to verify, so a probe
    #: built with a description alone can no longer admit. The tempting
    #: shortcut was to default `fix` to the description, which would have made
    #: every probe admit and quietly turned each REFUSAL test in this file into
    #: a test that passes for the wrong reason. Admission probes therefore pass
    #: their fix EXPLICITLY, and anything that should be refused says nothing.
    def __init__(self, d, fix=""):
        self.description = d
        self.proposed_fix = fix


class TestTheTablesAreNotEmpty:
    """ANTI-VACUITY. Every behavioural assertion below passes on empty tables,
    because an empty table means "everything may admit", which is the state
    before the repair."""

    def test_the_tool_level_set_is_populated(self):
        assert di.CANNOT_ADMIT_ALONE, "the truth-blind tool set is empty"

    def test_the_branch_gate_is_populated(self):
        assert di.BRANCH_GATED_ADMISSION, "the branch gate is empty"

    def test_the_measured_members_are_present(self):
        """★ `chemistry_structure` MOVED FROM THE TOOL SET TO THE BRANCH GATE
        ON 2026-11-10, and this test failing is what a reader should see if it
        ever moves back. The tool has 3 favourable branches: molecular formula
        and molecular weight COMPARE a computed value against the claim, and
        only the SMILES-validity fallback is truth-blind. Barring it at the
        tool level destroyed a live, reachable, discriminating admission --
        `the molecule 'CCO' has formula C2H6O` routes to chemistry/mathematical
        and is confirmed by the formula branch. A free panel seat found it."""
        for t in ("dimensional_analysis", "astronomical"):
            assert t in di.CANNOT_ADMIT_ALONE, f"{t} is no longer barred"
        for t in ("biological_sequence", "chemistry_structure"):
            assert di.BRANCH_GATED_ADMISSION.get(t) == MARKER, (
                f"{t} must be gated at the BRANCH: it has both a truth-blind "
                f"favourable branch and comparing ones, so a tool-level bar "
                f"removes a capability that works")
        assert "chemistry_structure" not in di.CANNOT_ADMIT_ALONE, (
            "chemistry_structure is barred at the tool level again, which "
            "destroys the formula and molecular-weight admissions")

    def test_a_tool_with_no_comparing_branch_stays_at_the_tool_level(self):
        """The converse, so the correction cannot over-rotate.
        `dimensional_analysis` has 0 comparing branches -- it reports
        dimensional homogeneity and never checks a claimed value -- so a
        tool-level bar removes nothing there and a branch gate would be
        inert, admitting on a marker it can never emit."""
        assert "dimensional_analysis" not in di.BRANCH_GATED_ADMISSION
        assert di._may_admit_alone("dimensional_analysis", MARKER) is False


class TestThePredicate:
    def test_a_barred_tool_cannot_admit_whatever_its_evidence(self):
        for ev in ("", "anything at all", MARKER):
            assert di._may_admit_alone("dimensional_analysis", ev) is False, ev

    def test_the_branch_gated_tool_admits_only_on_a_comparing_branch(self):
        assert di._may_admit_alone(
            "biological_sequence",
            "biopython: BIO_VALID: RC(ATGC)=GCAT matches claim") is True
        assert di._may_admit_alone(
            "biological_sequence",
            "biopython: BIO_VALID: DNA sequence 'ATGC' (len=4, GC=50.0%)") is False

    def test_an_unlisted_tool_is_unaffected(self):
        """THE ADDITIVE DIRECTION. The repair must narrow admission for the
        measured tools and for nothing else; a blanket refusal would satisfy
        every "cannot admit" assertion above while removing the mechanism."""
        for t in ("sympy", "z3", "stoichiometric_balance", "statsmodels"):
            assert di._may_admit_alone(t, "") is True, t

    def test_the_chemistry_marker_behaves_like_the_biology_one(self):
        """Both gated tools share one anatomy, so they must share one rule."""
        assert di._may_admit_alone(
            "chemistry_structure",
            "rdkit: CHEM_VALID: SMILES=CCO formula=C2H6O matches claim") is True
        assert di._may_admit_alone(
            "chemistry_structure",
            "rdkit: CHEM_VALID: SMILES=CCO parsed (3 atoms, 0 rings)") is False

    def test_the_marker_is_tool_scoped_not_global(self):
        """A marker read off 1 verifier's source may only be applied to that
        verifier. Applied globally it barred `stoichiometric_balance`, which
        the producer measures as DISCRIMINATING, and cost the adopted option a
        point it should never have lost."""
        assert di._may_admit_alone("stoichiometric_balance", "no marker here") is True


class TestEndToEndThroughTheRealGate:
    def test_a_false_claim_confirmed_only_by_a_truth_blind_tool_is_refused(self):
        """★ THE TEST THAT ACTUALLY EXERCISES THE GATE, AND THE FIRST VERSION
        OF THIS CLASS DID NOT HAVE IT.

        Reverting the admit line to `bool(definitive_for)` -- the original
        defect, in full -- left all 12 tests of the first version GREEN. Every
        end-to-end probe it used was refused because some tool REJECTED the
        claim, so `not definitive_against` was False and the verdict never
        depended on the gate at all. A verification passing for the wrong
        reason is indistinguishable from one that works.

        This case has no rejection in it. `the molecule CCO is benzene` is
        FALSE -- CCO is ethanol -- and `chemistry_structure` CONFIRMS it
        anyway at 0.85, because it validates the SMILES string and not the
        claim. Nothing else in the chemistry set speaks against it. So under
        the defect the harness would fold a fix back on the strength of a
        verdict that carries 0 bits about the claim.
        """
        r = di.domain_verification_set("chemistry", _F("the molecule CCO is benzene"))
        vs = r.get("verdicts") or []
        fors = [n for n, v, _c in vs if v in ("CONFIRMED", "VERIFIED", "SUPPORTED")]
        agst = [n for n, v, _c in vs if v in ("REFUTED", "REJECTED", "CONTRADICTED")]
        #: The premise of the test, asserted so it cannot rot into a probe
        #: that passes because nothing confirmed or because something rejected.
        assert fors, "nothing confirmed, so the gate is not exercised"
        assert not agst, (
            f"{agst} rejected this claim, so a refusal here would not be the "
            f"gate's doing and this test would pass for the wrong reason")
        #: ★ THE PREMISE TESTS THE PREDICATE, NOT THE TABLE. It used to read
        #: `all(t in di.CANNOT_ADMIT_ALONE ...)`, which broke the moment
        #: `chemistry_structure` moved to the branch gate -- correctly, but
        #: the test then failed on its own premise rather than on the
        #: property. What matters is that no confirmer here MAY ADMIT ALONE,
        #: by whichever of the 2 mechanisms applies to it.
        ev_of = {n: (e or "") for n, _v, _c, e in
                 [(n, v, c, None) for n, v, c in vs]}
        for t in fors:
            assert not di._may_admit_alone(t, ev_of.get(t) or ""), (
                f"{t} may admit alone on this claim, so the probe no longer "
                f"isolates the gate")
        assert r["admits"] is False, r.get("detail")

    def test_the_rejection_path_still_fails_closed(self):
        """A panel seat demonstrated this live false admit in its own sandbox.
        It is refused HERE by a REJECTION from `astronomical`, not by the
        gate -- which is why it cannot stand in for the test above. Kept
        because fail-closed on a rejection is itself a property worth pinning."""
        r = di.domain_verification_set(
            "physics", _F("the speed of light is 299792.458 km/s"))
        assert r["admits"] is False, r.get("detail")

    def test_a_discriminating_tool_still_admits(self):
        """THE CAPABILITY THE ADOPTED OPTION EXISTS TO PRESERVE. If this fails,
        the repair has become the tool-level exclusion it was measured against."""
        r = di.domain_verification_set(
            #: ★ THE FIX TEXT IS THE BARE EQUATION, not "correct it to: ...".
            #: The prefix made `stoichiometric_balance` REJECT the fix -- its
            #: parser reads the whole string as the equation -- so the probe
            #: would have failed on the wording of its own fixture rather than
            #: on the property. A fix the tools must verify has to be a fix the
            #: tools can PARSE.
            "chemistry", _F("2 H2 + O2 -> 2 H2O", "2 H2 + O2 -> 2 H2O"))
        assert r["admits"] is True, r.get("detail")

    def test_a_reachable_comparing_branch_admits_end_to_end(self):
        """★ THE ADMISSION THE FIRST COMMITTED FIX WAS DESTROYING, pinned
        end-to-end rather than at the predicate. This claim routes to
        chemistry/mathematical, `chemistry_structure` is dispatched, and its
        FORMULA branch confirms it with the marker. Under the tool-level bar
        the gate returned `admits=False, for=-,
        for_but_cannot_admit=chemistry_structure` -- a true, reachable,
        discriminating admission refused. The false variant is asserted in the
        same test so this cannot rot into a probe that passes because the tool
        confirms everything."""
        r = di.domain_verification_set(
            "chemistry", _F("the molecule 'CCO' has formula C2H6O",
                            "correct it to: the molecule 'CCO' has formula C2H6O"))
        assert r["admits"] is True, (
            f"the live formula admission is refused again: {r.get('detail')}")
        bad = di.domain_verification_set(
            "chemistry", _F("the molecule 'CCO' has formula C3H8O",
                            "correct it to: the molecule 'CCO' has formula C3H8O"))
        assert bad["admits"] is False, (
            f"the FALSE formula variant admits, so the branch is not "
            f"discriminating and the marker is worthless: {bad.get('detail')}")

    def test_the_molecular_weight_branch_also_admits(self):
        """The tool's second comparing branch, so the pin is not 1-of-N --
        which is the error that produced the defect this file now guards."""
        r = di.domain_verification_set(
            "chemistry",
            _F("the molecule 'CCO' has molecular weight 46.07 g/mol",
               "correct it to: the molecule 'CCO' has molecular weight 46.07 g/mol"))
        assert r["admits"] is True, r.get("detail")

    def test_the_detail_names_the_muted_voice(self):
        """A refusal must say WHICH tools spoke in favour but could not admit,
        or the record cannot tell "nothing agreed" from "only blind tools
        agreed" -- the B88 false-reason harm in a new place."""
        r = di.domain_verification_set("physics", _F("1 km = 2000 m"))
        assert "for_but_cannot_admit=" in (r.get("detail") or ""), r.get("detail")


class TestTheHonestLimit:
    """The branch-gated tool is NOT reachable by real traffic today, and that
    is recorded here so a reader cannot mistake the gate for an exercised one.
    Same root cause as B22's `graph_property` finding."""

    def test_the_branch_gated_tool_is_currently_unreachable(self):
        cfgs = di.load_all_domain_configs()
        assigning = [(d, ct) for d, c in sorted(cfgs.items())
                     for ct, tl in (c.verification_tools or {}).items()
                     if "biological_sequence" in (tl or [])]
        assert assigning, "nothing assigns the tool, so the gate guards nothing"
        reached = 0
        for dom, _ct in assigning:
            cfg = cfgs[dom]
            kind, _ = di.domain_classify_claim(
                _F("the reverse complement of ATGC is GCAT"), cfg)
            if "biological_sequence" in (di.domain_b_cell_tools(kind, cfg) or []):
                reached += 1
        #: ★ RE-PINNED 2026-11-11 FROM 0 TO AT LEAST 1, on the founder's B22
        #: verdict to widen the claim patterns. The old pin recorded an HONEST
        #: LIMIT -- `biology.toml` named none of sequence, DNA, RNA, protein,
        #: nucleotide, complement, codon or GC content, so 0 of 10 archived
        #: sequence claims could reach `biological_sequence` and the branch gate
        #: guarded nothing. Adding that vocabulary makes the route live.
        #: RE-PINNED RATHER THAN DELETED, because the guard's job is unchanged:
        #: it still asserts that something assigns the tool and that the route
        #: is in the state the record says it is. Its own failure message asked
        #: for exactly this, and the end-to-end discrimination test below is the
        #: second half of what it asked for.
        assert reached >= 1, (
            f"{reached} route(s) reach biological_sequence; at least 1 was "
            f"pinned on 2026-11-11 after B22's widening. Going back to 0 means "
            f"the sequence vocabulary has been removed from biology.toml, which "
            f"re-breaks a capability the founder ruled in.")

    def test_the_comparing_branch_discriminates_end_to_end(self):
        """★ THE HALF THE OLD PIN COULD NOT TEST, now that a route exists.

        Reaching a tool is not the same as the tool deciding anything. This
        asserts the repaired route actually DISCRIMINATES: a true reverse
        complement admits and a false one does not. Without this, the widening
        could have routed claims to a tool that says yes to everything, which
        is precisely the truth-blind failure this whole file exists to catch.
        """
        _CLAIM = "the reverse complement of ATGC is GCAT"
        true_claim = di.domain_verification_set(
            "biology", _F(_CLAIM, f"correct it to: {_CLAIM}"))
        false_twin = di.domain_verification_set(
            "biology", _F("the reverse complement of ATGC is AAAA",
                          "correct it to: the reverse complement of ATGC is AAAA"))
        assert true_claim["admits"] is True, (
            "the repaired biology route no longer admits a TRUE sequence "
            "claim, so the widening gained reach and lost the capability")
        assert false_twin["admits"] is False, (
            "the repaired biology route admits a FALSE sequence claim. That "
            "is truth-blindness: the route was widened to a tool that cannot "
            "tell the claim from its false twin.")

    def test_cross_domain_declares_tools_it_can_never_dispatch(self):
        cfgs = di.load_all_domain_configs()
        cfg = cfgs["cross_domain"]
        assert not (cfg.compiled_claim_patterns() or {}), (
            "cross_domain now has claim_patterns, so its tools are reachable. "
            "Re-measure and re-pin.")
        tools = {t for tl in (cfg.verification_tools or {}).values() for t in (tl or [])}
        assert len(tools) == 11, (
            f"cross_domain declares {len(tools)} tools, pinned at 11 on "
            f"2026-11-10, every one unreachable because the domain has 0 "
            f"claim_patterns so every claim classifies 'uncategorised'.")
