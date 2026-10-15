"""Section 7.7's severity specification DECIDES when promoted, and is recorded otherwise.

FOUNDER'S OBJECTION, 2026-10-14, which is why this exists: *"I note you stating
that several recently built/recently enabled features will be run in shadow in
the simulated run, but why run them in shadow in a simulated run, when the
purpose of a simulated run is to test how they will behave in a real experiment
and to fix any deficiencies/issues you encounter so that we don't run into those
same issues in a paid run, and risk pointlessly burning money we don't have?"*

HE IS RIGHT, AND THE CIRCLE IS SHARPER THAN HE PUT IT. `severity_spec_shadow`'s
own promotion criterion asks for non-distortion evidence *from a RUN*. A shadow
never decides, so a run can never supply that evidence. The shadow would have
stayed a shadow for ever and a PAID run would have been its first live test.
Promotion therefore needed a BUILD, not a setting.

MEASURED BEFORE IT WAS BUILT, over 2,994 archived entries across 59 runs
(`scripts/would_the_severity_promotion_reach_anything_2026-10-15.py`):

  * `severity_is_proven` holds for 295 of 2,994 — 9.8530%, Wilson [8.8364%,
    10.9726%], Clopper-Pearson [8.8084%, 10.9768%]. The A4 door's conjunctive
    proof half DOES open, so the promotion is not blocked by it.
  * The A4 population is 196 of 2,994 — 6.5464%, Wilson [5.7149%, 7.4893%].
  * Of those, 85 are asserted-critical and specification-sub-critical —
    43.3673%, Wilson [36.6227%, 50.3670%].
  * Of those 85, 7 are also proven and would therefore be RELEASED — 8.2353%,
    Wilson [4.0464%, 16.0360%].
  * 195 of the 196 A4 entries carry V=0.5 — 99.4898%, Wilson [97.1671%,
    99.9099%] — because A4 is by definition the entries whose falsifier has not
    resolved. That is where the whole effect lives.

AND THE FIRST VERSION OF THAT PRODUCER RETURNED 0 ENTRIES ACROSS 59 RUNS,
because it read `finding_registry` where the archive key is `registry.entries`.
An empty answer from a guessed predicate is an instrument result, not a
measurement. Recorded because it is the same shape as 8 of 10 errors measured on
2026-10-11.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

import reference_runner_v3 as rr  # noqa: E402

CRIT = rr.CRITICAL_SEVERITY_THRESHOLD


@pytest.fixture(autouse=True)
def _restore_flag():
    """The mirror is module state. Save and restore, never `setdefault` — an
    env/state leak that never restores is how the `PANEL_BRIEF_UNCHECKED` guard
    was silently disabled by 3 fixtures (2026-10-08)."""
    saved = dict(rr._SEVERITY_SPEC)
    try:
        yield
    finally:
        rr._SEVERITY_SPEC.clear()
        rr._SEVERITY_SPEC.update(saved)


def _entry(severity, verdict=None, proof=None, status="UNCONFIRMED",
           falsifier_code=""):
    """THE PROOF KEY IS `severity_proof["status"]`, NOT A FLAT FIELD, and the
    first version of this fixture wrote `rk_proof_status`. `severity_is_proven`
    then returned False for every entry and 2 tests failed against correct code
    -- a FIXTURE defect masquerading as a code defect. Read from
    `severity_proof_status` rather than guessed the second time."""
    e = {"severity": severity, "status": status,
         "falsifier_code": falsifier_code}
    if verdict is not None:
        e["falsifier_verdict"] = verdict
    if proof is not None:
        e["severity_proof"] = {"status": proof}
    return e


class TestTheVerificationFactor:
    def test_the_three_values_are_the_appendix_s(self):
        assert rr.spec_verification_factor(_entry(0.8, "CONFIRMED")) == 1.0
        assert rr.spec_verification_factor(_entry(0.8, "REFUTED")) == 0.0
        assert rr.spec_verification_factor(_entry(0.8)) == 0.5
        assert rr.spec_verification_factor(_entry(0.8, "ESCALATE")) == 0.5

    def test_the_key_property_annihilates_rather_than_reduces(self):
        """A disproved finding scores ZERO regardless of confidence. That is the
        property that makes the formula the opposite of a vote."""
        rr._SEVERITY_SPEC["on"] = True
        for asserted in (0.1, 0.5, 0.7, 0.99, 1.0):
            assert rr.effective_severity(_entry(asserted, "REFUTED")) == 0.0

    def test_the_verdict_read_is_case_and_space_insensitive(self):
        assert rr.spec_verification_factor(_entry(0.8, "  confirmed ")) == 1.0
        assert rr.spec_verification_factor(_entry(0.8, "Refuted")) == 0.0


class TestTheDefaultPathIsUnchanged:
    def test_off_returns_the_asserted_float(self):
        rr._SEVERITY_SPEC["on"] = False
        for asserted, verdict in ((0.8, None), (0.8, "CONFIRMED"),
                                  (0.8, "REFUTED"), (0.0, None), (1.0, "X")):
            assert rr.effective_severity(_entry(asserted, verdict)) == asserted

    def test_a_missing_or_malformed_severity_is_zero_either_way(self):
        for on in (False, True):
            rr._SEVERITY_SPEC["on"] = on
            assert rr.effective_severity({"status": "UNCONFIRMED"}) == 0.0
            assert rr.effective_severity({"severity": None}) == 0.0

    def test_the_config_default_keeps_it_recorded_only(self):
        assert rr.RunnerConfig().severity_spec_enabled is False, (
            "the specification now decides by default, which would make free "
            "run 1 measure 2 changes at once")
        assert rr.RunnerConfig(severity_spec_enabled=True
                               ).severity_spec_enabled is True, (
            "the promotion cannot be switched on, so it is an addition nothing "
            "reaches")


class TestItReachesTheA4Door:
    """EXECUTED against the real registry, not asserted about the source."""

    def _registry(self, entries):
        reg = rr.FindingRegistry()
        reg.entries = dict(entries)
        return reg

    def test_the_promotion_releases_a_proven_specification_subcritical(self):
        """0.8 asserted, no verdict so V=0.5, giving 0.4 — sub-critical — and a
        PASSING R_k proof, so the conjunctive door opens."""
        entries = {"C1": _entry(0.8, proof="PASS")}
        reg = self._registry(entries)
        rr._SEVERITY_SPEC["on"] = False
        before = reg.unverified_critical_count()
        rr._SEVERITY_SPEC["on"] = True
        after = reg.unverified_critical_count()
        assert before == 1, before
        assert after == 0, (
            "the specification does not reach the A4 door, so the promotion is "
            "an addition nothing reaches")

    def test_an_unproven_entry_is_still_not_released(self):
        """THE PROOF REQUIREMENT IS NOT WEAKENED. This is the discipline the
        founder restored on 2026-10-06 and the promotion must not erode it."""
        reg = self._registry({"C1": _entry(0.8)})
        for on in (False, True):
            rr._SEVERITY_SPEC["on"] = on
            assert reg.unverified_critical_count() == 1, on

    def test_an_already_subcritical_proven_entry_is_unaffected(self):
        reg = self._registry({"C1": _entry(0.3, proof="PASS")})
        for on in (False, True):
            rr._SEVERITY_SPEC["on"] = on
            assert reg.unverified_critical_count() == 0, on

    def test_a_confirmed_verdict_keeps_its_full_severity(self):
        """V=1.0, so a CONFIRMED entry is NOT released by the specification. It
        leaves the count only by the resolved-verdict route, as before."""
        rr._SEVERITY_SPEC["on"] = True
        assert rr.effective_severity(
            _entry(0.8, "CONFIRMED", proof="PASS")) == 0.8


class TestTheShadowIsRetained:
    def test_the_shadow_reader_still_exists_and_still_gates_nothing(self):
        reg = rr.FindingRegistry()
        reg.entries = {
            "C1": _entry(0.8),
            "C2": _entry(0.9, "REFUTED"),
            "C3": _entry(0.75, "CONFIRMED"),
        }
        shadow = reg.severity_spec_shadow()
        assert shadow["critical_asserted"] == 3, shadow
        assert shadow["V_none"] == 1 and shadow["V_false"] == 1
        assert shadow["V_true"] == 1
        assert "C2" in shadow["key_property_violations"]
        assert "C1" in shadow["crossed_downward"]
        # It must agree with the accessor on every entry, or the record and the
        # decision would describe different quantities.
        rr._SEVERITY_SPEC["on"] = True
        for cid, e in reg.entries.items():
            expected = float(e["severity"]) * rr.spec_verification_factor(e)
            assert rr.effective_severity(e) == expected, cid


class TestTheMirrorIsWiredFromTheConfig:
    def test_the_launcher_exposes_the_flag_and_help_costs_nothing(self):
        """A `--help` must never cost money (15 of 17 runners once billed a live
        dispatch on an unrecognised argument)."""
        import subprocess
        out = subprocess.run(
            [sys.executable, str(ROOT / "bench" / "tools" / "run_simulated_experiment.py"),
             "--help"],
            capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-800:]
        assert "--severity-spec" in out.stdout

    def test_the_config_actually_moves_the_mirror(self):
        """★ CONVERTED FROM A SOURCE-TEXT ASSERTION, 2026-10-15. It used to read
        `reference_runner_v3.py` and assert a line was present, which says only
        that the module describes itself consistently. The census guard caught it
        at 99 against a ceiling of 98 and named the remedy: convert, do not raise.

        `wire_module_mirrors` was extracted for exactly this, so the wiring can
        be EXECUTED with a config and the mirror observed to move -- costing
        nothing, because no round is dispatched."""
        for flag in (True, False, True):
            got = rr.wire_module_mirrors(rr.RunnerConfig(severity_spec_enabled=flag))
            assert rr._SEVERITY_SPEC["on"] is flag, (
                f"config said severity_spec_enabled={flag} and the mirror reads "
                f"{rr._SEVERITY_SPEC['on']}; the launcher flag would be recorded "
                f"and ignored")
            assert got == {"severity_spec": flag}, got

    def test_a_config_missing_the_field_entirely_is_safe(self):
        """A bare object with no such attribute must leave the mirror OFF rather
        than raise, because `getattr(..., False)` is the contract."""
        class Bare:
            pass
        rr._SEVERITY_SPEC["on"] = True
        rr.wire_module_mirrors(Bare())
        assert rr._SEVERITY_SPEC["on"] is False
