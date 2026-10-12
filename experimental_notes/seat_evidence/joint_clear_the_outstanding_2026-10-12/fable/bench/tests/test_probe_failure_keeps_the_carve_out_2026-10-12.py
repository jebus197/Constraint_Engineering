# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cda17c147811232a3fe5bb4b259b004d4d7276deff89af36fd7899cd86ec20f7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A probe that does not answer must not cost the interpreter carve-out.

JOINT ROUND J2, 2026-10-12. The probe-based carve-out failed CLOSED: a
candidate interpreter that did not answer within 10s contributed no roots, and
the per-process cache made one loaded moment permanent -- measured by
scripts/probe_failure_regresses_the_gate_2026-10-12.py, every probe timing out
left 0 roots for the life of the process, returning the gate to refusing every
spawned-interpreter falsifier (the C0050 false-refusal class). The repair is a
DECLARED fallback per failed candidate: roots derived from the candidate's
path without executing it, existence-filtered, consulted only on probe
failure. The probe stays primary and normal operation is byte-identical.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import bench.falsifier_verify as fv  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_cache():
    saved = fv._SECONDARY_ROOTS_CACHE
    fv._SECONDARY_ROOTS_CACHE = None
    yield
    fv._SECONDARY_ROOTS_CACHE = saved


def _timeout(*a, **k):
    raise subprocess.TimeoutExpired(cmd=a[0], timeout=k.get("timeout", 10))


def test_total_probe_failure_still_contributes_roots(monkeypatch):
    monkeypatch.setattr(subprocess, "run", _timeout)
    roots = fv._secondary_interpreter_roots()
    assert roots, (
        "every probe timed out and the carve-out vanished; the gate is back "
        "to refusing correct falsifiers for the life of the process")
    assert all(os.path.isdir(r) for r in roots), (
        "a declared root that does not exist can never be read, so declaring "
        "it is dead weight -- the fallback must existence-filter")


def test_the_fallback_never_declares_a_bare_system_prefix(monkeypatch):
    """dirname(dirname(/usr/bin/python3)) is /usr; the first draft of the
    fallback allowed it wholesale. A bare /usr or / in the allow set is a
    widening nobody sanctioned."""
    monkeypatch.setattr(subprocess, "run", _timeout)
    roots = fv._secondary_interpreter_roots()
    assert not any(r in ("/", "/usr", "/usr/local", "/opt") for r in roots)


@pytest.mark.skipif(
    not os.path.isdir("/Library/Developer/CommandLineTools/Library/Frameworks/"
                      "Python3.framework/Versions"),
    reason="no CommandLineTools python on this machine")
def test_the_system_shim_gets_its_declared_tree_without_execution():
    declared = fv._declared_secondary_roots("/usr/bin/python3")
    assert any("Python3.framework/Versions" in r and "/lib/python3." in r
               for r in declared), (
        "the /usr/bin/python3 shim's stdlib lives under CommandLineTools and "
        "is not derivable from the shim path; the declared patterns must "
        "cover it or C0050-class falsifiers are refused whenever the probe "
        "fails")


def test_bootstrap_class_coverage_degrades_but_does_not_vanish(monkeypatch):
    """Every import-bootstrap-class tree the live probe reports stays allowed
    in at least one REALPATH spelling under total probe failure. The observer
    realpaths both the read target and the allow set, so spelling collapse is
    the correct comparison."""
    normal = set(fv._secondary_interpreter_roots())
    fv._SECONDARY_ROOTS_CACHE = None
    monkeypatch.setattr(subprocess, "run", _timeout)
    degraded = {os.path.realpath(r) for r in fv._secondary_interpreter_roots()}
    gaps = [r for r in normal
            if ("/lib/python3" in r or r.rstrip("/").endswith(
                ("site-packages", "lib-dynload")))
            and os.path.realpath(r) not in degraded]
    assert gaps == [], f"bootstrap-class trees lost under probe failure: {gaps}"


def test_a_working_probe_is_byte_identical_no_fallback_consulted(monkeypatch):
    """Additive standard, both halves: the fallback is wired AND unreached
    when the mechanism it backs up is healthy."""
    calls = []
    real = fv._declared_secondary_roots

    def spy(cand):
        calls.append(cand)
        return real(cand)

    monkeypatch.setattr(fv, "_declared_secondary_roots", spy)
    fv._secondary_interpreter_roots()
    assert calls == [], (
        f"the declared fallback was consulted although every probe answered: "
        f"{calls}")
