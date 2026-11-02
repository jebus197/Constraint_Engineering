"""The pre-flight REFUSES an unregistered seat, and it no longer accuses correct code.

HIS RULING, 2026-11-01, verbatim: *"If a model a researcher wishes to add fails
registration, then that is a failure of both the intent to make adding a model
trivial and of the mechanics I asked you to build to make this the case. So it
should cause the pre-flight checks to fail and the issue should be raised loudly
for the researcher/HIL to investigate and to fix. But fixing a failing
registration should also preferably be made as trivial for a HIL to fix as
possible. So clear indications should be offered in the pre-flight check for any
such failures."*

WHY THIS COULD NOT SIMPLY BE SWITCHED FROM REPORT TO REFUSE. The check's own
docstring argued that refusing would get the screen switched off, because a run
with an unregistered stand-in would always be blocked. THAT ARGUMENT RESTED ON
THE CHECK'S OWN FALSE POSITIVE. It read

    base = getattr(rc, "base_model_label", lambda s: s)

and `base_model_label` is defined in `bench/reference_runner_v3.py`, NOT in
`runner_core`, so the getattr ALWAYS took its identity default and no `-SIM`
suffix was ever stripped. All 6 simulated seats were therefore reported absent
from all 4 tables. A silent default, inside the check whose whole purpose is to
find silent defaults.

MEASURED 2026-11-02 WITH THE RESOLVER WIRED: the real 5-seat roster is present in
all 4 tables, the 5-seat simulated roster is too, and the unregistered `Kimi` is
correctly absent from all 4. So refusing costs nothing a researcher has not
caused, and the docstring's objection dissolves.

AND REMOVING THE FALSE POSITIVE EXPOSED A TRUE ONE. `Fable` is present in
`MODEL_SPECS` and absent from `INITIAL_FINGERPRINTS`, `COMPOSER_MODEL_MAP`,
`PHENOTYPE_TRANSFORMS` and `MODEL_COHERENCE_BUDGETS`, while the other 5 vendors
are in all 5 -- and `Fable-SIM` has RUN that way. That was already tracked as
live ticket `5c099c217f11` from 2026-10-29; this pass corroborates it
independently and names why it stayed invisible.
"""
from __future__ import annotations

import importlib
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
POST = REPO / "scripts" / "preflight_health_check_2026-10-06.py"
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

REAL = ["CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini"]
SIM = [f"{m}-SIM" for m in REAL]
UNREGISTERED = "Kimi"


@pytest.fixture(scope="module")
def post():
    spec = importlib.util.spec_from_file_location("_post_under_test", POST)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _verdict(post, seats):
    status, headline, notes = post.check_every_seat_is_fully_registered(seats)
    return status, headline, notes


class TestTheResolverIsWiredAndNotDefaulted:

    def test_the_identity_fallback_is_gone(self, post):
        """EXECUTED, NOT GREPPED. A first version of this test asserted the old
        string was absent from the source -- and FAILED, because the comment
        documenting the defect quotes it. A source-text assertion cannot tell
        live code from a comment about live code, which is the rule
        `execute-do-not-grep` exists for, and it caught me inside the very test
        written to enforce the lesson.

        So the property is checked by BEHAVIOUR: under the identity fallback a
        simulated roster is refused, and under a real resolver it passes. The
        2 are distinguished by running them."""
        under_resolver = _verdict(post, SIM)[0]
        assert under_resolver == post.PASS, (
            "a simulated roster is refused, which is what the identity "
            "fallback caused")
        # and prove the 2 forms differ, so this is not vacuous
        rc = importlib.import_module("runner_core")
        identity_absent = sum(
            1 for seat in SIM
            for tbl in (rc.MODEL_SPECS, getattr(rc, "INITIAL_FINGERPRINTS", {}))
            if seat not in tbl)                      # raw label, as identity would
        resolved_absent = sum(
            1 for seat in SIM
            for tbl in (rc.MODEL_SPECS, getattr(rc, "INITIAL_FINGERPRINTS", {}))
            if rc._spec_key(seat) not in tbl)
        assert identity_absent > 0 and resolved_absent == 0, (
            f"the 2 resolutions no longer differ on this roster "
            f"(identity misses {identity_absent}, resolver misses "
            f"{resolved_absent}), so this test cannot discriminate them")

    def test_a_missing_resolver_FAILS_rather_than_comparing_raw_labels(self, post, monkeypatch):
        rc = importlib.import_module("runner_core")
        monkeypatch.delattr(rc, "_spec_key", raising=True)
        status, headline, _ = _verdict(post, REAL)
        assert status == post.FAIL, (
            "with the resolver gone the check must refuse, not silently compare "
            "raw labels")
        assert "_spec_key" in headline

    def test_the_resolver_strips_the_simulation_suffix(self):
        rc = importlib.import_module("runner_core")
        assert rc._spec_key("CC2-SIM") == "CC2"
        assert rc._spec_key("CC2") == "CC2"
        assert rc._spec_key(UNREGISTERED) == UNREGISTERED


class TestHisRulingIsInEffect:

    def test_a_complete_real_roster_passes(self, post):
        status, headline, notes = _verdict(post, REAL)
        assert status == post.PASS, (status, headline, notes)

    def test_a_complete_simulated_roster_passes(self, post):
        """The case the old docstring feared. It passes, so refusing is free."""
        status, headline, notes = _verdict(post, SIM)
        assert status == post.PASS, (
            f"a simulated roster is refused, which is what the old design "
            f"warned would get this screen switched off: {headline}")

    def test_an_unregistered_seat_is_REFUSED(self, post):
        status, headline, notes = _verdict(post, ["CC2", UNREGISTERED])
        assert status == post.FAIL, (
            f"an unregistered seat no longer fails the pre-flight, which is "
            f"what he ruled on 2026-11-01: {headline}")

    def test_the_refusal_tells_the_operator_how_to_fix_it(self, post):
        """*"clear indications should be offered in the pre-flight check"*."""
        _, headline, notes = _verdict(post, ["CC2", UNREGISTERED])
        assert "TO FIX" in headline, headline
        assert "COMPOSER_MODEL_MAP" in headline, (
            "the remediation does not name the composer map, so a researcher "
            "adding a new vendor is not told about the second vocabulary")
        assert any(UNREGISTERED in n and "absent from" in n for n in notes), (
            "the offending seat is not named in the notes")

    def test_the_refusal_names_every_missing_table_not_just_a_count(self, post):
        """Pin a set, not a count."""
        _, _, notes = _verdict(post, [UNREGISTERED])
        line = next(n for n in notes if UNREGISTERED in n)
        for table in ("MODEL_SPECS", "INITIAL_FINGERPRINTS",
                      "PHENOTYPE_TRANSFORMS", "MODEL_COHERENCE_BUDGETS"):
            assert table in line, f"{table} is not named in {line!r}"

    def test_no_seats_declared_still_fails(self, post):
        status, headline, _ = _verdict(post, [])
        assert status == post.FAIL and "no seats" in headline.lower()


class TestTheTruePositiveItExposed:
    """REWRITTEN 2026-11-02, AND THE PREVIOUS FORM WAS RIGHT TO FAIL.

    This class used to assert `Fable-SIM` FAILS registration. That was true when
    it was written and it stopped being true the moment the gap was closed, so
    the test began accusing correct code -- the shape recorded in
    `feedback_a_guard_can_accuse_correct_code_2026-10-28`, where 9 of 36 failures
    in the 2026-10-28 baseline were guards pinning a defect rather than a
    property, and fixing the subject to satisfy them would have made it worse.

    ITS OWN DOCSTRING SAID WHAT TO DO, and it is followed rather than ignored:
    "If this ever passes, ticket 5c099c217f11 is fixed -- verify and close it
    rather than deleting this test", on the condition that the calibration
    values be "MEASURED, not invented".

    THAT CONDITION IS NOT MET AND IS NOT CLAIMED TO BE. The 4 added entries are
    INHERITED from CC2/opus_4_6 with their provenance recorded in the source,
    on the same grounds and by the same convention as `MODEL_SPECS['Fable']`,
    which has carried "inherited from CC2 2026-08-30; not measured" since August.
    So the REGISTRATION half of ticket 5c099c217f11 is discharged and the
    MEASUREMENT half is not, and `test_fables_values_declare_that_they_are_inherited`
    below is what stops the inherited values from later passing as measured.

    What is guarded now is the PROPERTY -- that an unregistered seat is refused --
    tested against a name that is genuinely absent, so it cannot go stale when
    the next vendor is added.
    """

    def test_an_unregistered_seat_is_still_refused(self, post):
        """The property the old test guarded, pinned to a name that is absent.

        `Kimi` is in none of the 5 per-model tables. If it is ever added, this
        test must be re-pointed at another absent name rather than deleted --
        the refusal is the capability, and it must never go unexercised.
        """
        status, _, notes = _verdict(post, ["Kimi-SIM"])
        assert status == post.FAIL, (
            "an unregistered seat must FAIL the preflight. His ruling of "
            "2026-11-01: it 'should cause the pre-flight checks to fail and "
            "the issue should be raised loudly'.")
        line = next(n for n in notes if "Kimi" in n)
        assert "table" in line.lower(), line

    def test_the_refusal_names_what_to_add_and_where(self, post):
        """His ruling has a second half: the fix must be made trivial for a HIL.

        Verbatim, 2026-11-01: "fixing a failing registration should also
        preferably be made as trivial for a HIL to fix as possible. So clear
        indications should be offered in the pre-flight check for any such
        failures." A refusal that does not say which table and which key is
        loud but unactionable.
        """
        # THE GUIDANCE IS IN THE DETAIL, NOT THE PER-SEAT NOTES. A first version
        # joined only `notes` and failed -- correctly, because it was reading
        # the wrong half of the check's output. The per-seat notes name WHICH
        # tables; the detail names HOW to fix them. His ruling asks for both.
        _status, detail, notes = _verdict(post, ["Kimi-SIM"])
        blob = " ".join([str(detail)] + list(notes))
        assert "TO FIX" in blob, "the refusal must say how to fix it"
        assert "COMPOSER_MODEL_MAP" in blob, (
            "it must name the resolver, because 1 missing entry there produces "
            "3 reported absences and a reader who adds 3 rows does the wrong work")

    def test_all_six_vendors_including_fable_are_now_complete(self, post):
        for m in list(REAL) + ["Fable"]:
            status, _, _ = _verdict(post, [m])
            assert status == post.PASS, f"{m} is under-registered"

    def test_fables_values_declare_that_they_are_inherited(self):
        """An inherited value must never pass as a measured one.

        This is the guard that keeps ticket 5c099c217f11 honestly half-open.
        `MODEL_SPECS['Fable']` carries an explicit `_provenance`; the 3 entries
        added on 2026-11-02 record theirs in source comments at their own table.
        If someone later calibrates Fable for real, these assertions are what
        tell them which values were standing in.
        """
        import pathlib as _p
        from bench import runner_core as _rc
        root = _p.Path(__file__).resolve().parents[2]
        spec = _rc.MODEL_SPECS.get("Fable") or {}
        assert "not measured" in str(spec.get("_provenance", "")).lower(), (
            "MODEL_SPECS['Fable'] must keep saying its values are unmeasured")
        comp = (root / "bench" / "cdsfl_registry" / "composer.py").read_text()
        core = (root / "bench" / "runner_core.py").read_text()
        assert "NOT MEASURED" in comp, (
            "composer.py must record that Fable's phenotype is inherited")
        assert "NOT MEASURED" in core, (
            "runner_core.py must record that Fable's fingerprint is inherited")
