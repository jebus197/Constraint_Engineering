# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_is_ordinal_2026-11-11_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: deebfd9dca595b8563e3827a47f4f4d68d538fe973ddeff57ed355d35653316e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The credence half of section 7.7.1's pair must carry no consequence factor.

Joint round `severity_is_ordinal_2026-11-11_joint`, `fable` seat, 2026-11-12.

Section 7.7.1 defines `severity_d(f) = (c_d(f), credence(f))` to SEPARATE a
consequence from a belief.  As first written it defined the second component as
section 7.7's product `W(class) * confidence * Ver(verification)`, and section
7.7 caution 3 states that consequence magnitude enters `Sev` through `W` alone.
So the pair carried a consequence factor in both components and performed no
separation; caution 3's collapse travelled with the product into the new slot.

These tests are the regression guard.  The derivation lives in
`scripts/the_credence_half_still_carries_the_consequence_2026-11-12.py`, which
these tests EXECUTE rather than restate, so the two cannot drift.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"
PRODUCER = (REPO / "scripts"
            / "the_credence_half_still_carries_the_consequence_2026-11-12.py")


def _s771() -> str:
    t = APPENDIX.read_text(encoding="utf-8")
    i = t.index("### 7.7.1 The symbolic form")
    j = t.index("### 7.8 Multi-Verifier Severity")
    return t[i:j]


def test_the_producer_exists_and_exits_clean() -> None:
    """The derivation is executable, and a stale producer fails here."""
    assert PRODUCER.is_file(), f"producer missing: {PRODUCER}"
    r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"producer exited {r.returncode}\n{r.stdout}\n{r.stderr}"
    assert "FALSIFIED" not in r.stdout, r.stdout
    # the mutation test inside it must have fired, else the check is vacuous
    assert "the predicate DOES fire on the superseded sentence" in r.stdout
    for tok in ("z3 -> unsat", "solveset -> EmptySet"):
        assert tok in r.stdout, f"{tok!r} absent -- derivation did not run"


def _predicate():
    """Import the producer's OWN predicate rather than re-implementing it.

    A first version of this test re-implemented the check as a bare negative
    match on the superseded sentence, and it FAILED on the repaired file --
    because the amendment QUOTES the sentence it supersedes, which is this
    project's recording convention.  The producer's predicate is a conjunction
    (superseded phrasing present AND the repaired definition absent) and does
    not have that false positive.  Two copies of one predicate drift, which is
    the defect `bench/immune_agents.py` records for its own alias table, so
    there is one copy and this is a loader for it.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_cred_producer", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_credence_is_defined_without_a_consequence_factor() -> None:
    mod = _predicate()
    s = _s771()
    assert re.search(r"\*\*credence\(f\)\s*=\s*S_v\(f\)\s*·\s*Ver\(verification\)\*\*", s), (
        "section 7.7.1 no longer defines `credence(f) = S_v(f) · Ver(verification)`"
    )
    assert not mod.credence_half_carries_consequence(s), (
        "the superseded definition is live again: section 7.7's product contains "
        "W(class), which caution 3 names as the CONSEQUENCE term"
    )
    # the predicate must still be CAPABLE of firing, or this test is vacuous
    mutant = s.replace("**credence(f) = S_v(f) · Ver(verification)**", "")
    assert mod.credence_half_carries_consequence(mutant), (
        "the predicate no longer fires on the superseded form -- it has gone blind"
    )


def test_ver_is_retained_because_s_v_has_no_zero() -> None:
    """Deleting `Ver` makes the key property unrepresentable, not merely unstated."""
    import sympy as sp
    L = sp.symbols("L", real=True)
    assert sp.solveset(sp.Eq(1 / (1 + sp.exp(-L)), 0), L,
                       domain=sp.S.Reals) == sp.EmptySet
    s = _s771()
    assert "has no zero" in s.lower(), (
        "section 7.7.1 must state WHY `Ver` is retained alongside `S_v`"
    )


def test_w_is_relocated_and_not_removed() -> None:
    """The additive standard: `W` is the only ordering the 6 `none` domains have."""
    s = _s771()
    assert "NOT DELETED" in s and "constraint-class proxy" in s, (
        "section 7.7.1 must state that `W` survives as the declared fallback "
        "ordering where sigma_d = none and the application supplies no scale"
    )
