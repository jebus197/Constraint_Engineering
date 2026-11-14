# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_proof_and_weight_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: fb0777ed878f1124d18e534cf854d1b182f5dd5dd0cea2031d8818a6737dc679
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""F3 (panel 2026-11-14): every spelling of the critical cut is pinned.

Measured 2026-11-14 on exp40_gate_20260514T020550Z (296 entries, 28 rounds):
`hierarchical_novelty_series` totals 30 / 26 / 20 criticals at cuts
0.65 / 0.70 / 0.75, so a drifting duplicate CHANGES the gamma-side series --
these are live inputs, not inert copies. `bench/evidence.py` was already pinned
by test_verified_true_ledger.py::test_critical_threshold_matches_the_runner;
this file pins the 3 spellings that were pinned by nothing, and does it by
IMPORT and `inspect.signature`, never by source text.

A per-domain critical level (domain_manifest.toml, composer severity
declaration) does not make these constants wrong: they are the APPLICATION
level that domains with `severity_scale = "none"` inherit, and the
pre-registration of 2026-05-18 forbids moving the numeric. What it forbids is
DRIFT between spellings, which is exactly what this test fails loud on.
"""
import inspect

import bench.audit_closing_window as acw
import bench.convergence_location as cl
from bench import reference_runner_v3 as rr3

CANON = rr3.CRITICAL_SEVERITY_THRESHOLD


def test_audit_closing_window_matches_the_runner():
    assert acw.CRITICAL_SEVERITY_THRESHOLD == CANON


def test_every_convergence_location_default_matches_the_runner():
    """Walk EVERY public function in the module: any parameter named
    `critical_threshold` with a numeric default must equal the runner's
    constant. Robust to new spellings being added later."""
    found = []
    for name, fn in inspect.getmembers(cl, inspect.isfunction):
        if fn.__module__ != cl.__name__:
            continue
        sig = inspect.signature(fn)
        p = sig.parameters.get("critical_threshold")
        if p is not None and isinstance(p.default, (int, float)):
            found.append((name, p.default))
    assert found, "no critical_threshold defaults found -- the module moved"
    for name, default in found:
        assert default == CANON, (
            f"{cl.__name__}.{name} defaults critical_threshold={default}, "
            f"runner canon is {CANON}: the series this feeds changes with the "
            f"cut (30/26/20 at 0.65/0.70/0.75 on exp40_gate), so this drift "
            f"changes verdicts.")


def test_the_known_spellings_are_among_those_pinned():
    sigs = {n: inspect.signature(getattr(cl, n))
            for n in ("hierarchical_novelty_series", "novelty_rule_divergence")}
    for n, sig in sigs.items():
        assert sig.parameters["critical_threshold"].default == CANON, n
