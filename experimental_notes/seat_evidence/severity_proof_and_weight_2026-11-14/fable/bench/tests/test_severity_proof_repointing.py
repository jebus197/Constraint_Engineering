# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_proof_and_weight_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4d212530677159f845fa969dfc6b8b3fd205b681e1e0c689f2c6f0ac24c2a94f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""R1 (panel 2026-11-14): `severity_is_proven` repointed at the gated number.

The defect: the release doors test `severity < CRITICAL_SEVERITY_THRESHOLD and
severity_is_proven(e)`, but the proof reproduces R_k without reading `severity`
(r = -0.5538 over 652 archived PASS/WARN entries, producer
scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py). The repair is
DEFAULT OFF and awaits the founder's ruling; these tests execute both states so
the flag is wired to a caller and exercised, per the additive standard.
"""
import pytest

from bench import reference_runner_v3 as rr3


@pytest.fixture(autouse=True)
def _restore_mirror():
    before = dict(rr3._PROOF_ABOUT_GATED_NUMBER)
    yield
    rr3._PROOF_ABOUT_GATED_NUMBER.clear()
    rr3._PROOF_ABOUT_GATED_NUMBER.update(before)


GAMING = {"severity": 0.45,
          "severity_proof": {"status": "PASS",
                             "model_rk": 0.95, "recomputed_rk": 0.95}}
HONEST = {"severity": 0.66,
          "severity_proof": {"status": "WARN",
                             "model_rk": 0.65, "recomputed_rk": 0.63}}
NO_RK = {"severity": 0.45, "severity_proof": {"status": "PASS"}}
SKIP = {"severity": 0.45, "severity_proof": {"status": "SKIP"}}


def test_default_off_is_byte_identical_behaviour():
    """The pre-2026-11-14 predicate: status alone decides. The joint round's
    gaming entry (sev 0.45 released on a proven R_k of 0.95) still passes,
    which is the defect, preserved deliberately until the founder rules."""
    assert rr3._PROOF_ABOUT_GATED_NUMBER["on"] is False
    assert rr3.severity_is_proven(GAMING) is True
    assert rr3.severity_is_proven(HONEST) is True
    assert rr3.severity_is_proven(NO_RK) is True
    assert rr3.severity_is_proven(SKIP) is False


def test_repointed_requires_the_proof_to_be_about_the_gated_number():
    rr3._PROOF_ABOUT_GATED_NUMBER["on"] = True
    # |0.45 - 0.95| = 0.5 > 0.05: the proof is of a different number.
    assert rr3.severity_is_proven(GAMING) is False
    # |0.66 - 0.63| = 0.03 <= 0.05: the proven number IS the gated number.
    assert rr3.severity_is_proven(HONEST) is True
    # A proof carrying no reproducible number cannot be about the gated one.
    assert rr3.severity_is_proven(NO_RK) is False
    assert rr3.severity_is_proven(SKIP) is False


def test_repointing_is_a_subset_never_a_loosening():
    """For any entry, repointed-proven implies currently-proven."""
    rr3._PROOF_ABOUT_GATED_NUMBER["on"] = True
    entries = [GAMING, HONEST, NO_RK, SKIP,
               {"severity": None, "severity_proof": {"status": "PASS",
                                                     "recomputed_rk": 0.2}},
               {}]
    repointed = [rr3.severity_is_proven(e) for e in entries]
    rr3._PROOF_ABOUT_GATED_NUMBER["on"] = False
    current = [rr3.severity_is_proven(e) for e in entries]
    for rep, cur in zip(repointed, current):
        assert not rep or cur


def test_wire_module_mirrors_carries_the_config_flag():
    class _Cfg:
        severity_spec_enabled = False
        severity_proof_about_gated_number = True
    out = rr3.wire_module_mirrors(_Cfg())
    assert out["severity_proof_about_gated_number"] is True
    assert rr3._PROOF_ABOUT_GATED_NUMBER["on"] is True
    class _CfgOff:
        pass
    out = rr3.wire_module_mirrors(_CfgOff())
    assert out["severity_proof_about_gated_number"] is False
    assert rr3._PROOF_ABOUT_GATED_NUMBER["on"] is False


def test_runnerconfig_carries_the_field_default_off():
    import dataclasses
    fields = {f.name: f for f in dataclasses.fields(rr3.RunnerConfig)}
    assert "severity_proof_about_gated_number" in fields
    assert fields["severity_proof_about_gated_number"].default is False
