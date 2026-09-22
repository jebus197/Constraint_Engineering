#!/usr/bin/env python3
"""The R_k extractor must stop a parameter statement at an ARROW.

WHAT THIS DEMONSTRATES. `_rk_statement` runs to end of line and
`_rk_stated_value` takes the LAST '=' value inside it. `_RK_RE_CLIP` bounds the
statement at a comma, a comparison or a sentence end -- but NOT at U+2192, which
is the delimiter the seats actually use. So on the real text a seat wrote in
commissioning arm 1 round 0:

    R_old=0.50, eta=0.95, d=0.90, p=0.85 -> q=0.727. ...
    S_k=0.92 -> R_base = 0.92x0.215 + 0.08x0.50 = 0.237.

the statement for `p` ran on through the arrow and returned 0.727, the model's
`q`; and the statement for `S_k` returned 0.237, the model's `R_base`. The
section was then graded FAIL at recomputed 0.4676 against the model's own stated
R_k of 0.266 -- an accusation of bad arithmetic against a seat whose arithmetic
was correct to 3 decimal places, delivered at the top of the next round's prompt
worded "this is your own arithmetic".

WHY IT IS ONE-DIRECTIONAL AND THEREFORE LOOKED LIKE A FINDING.

    d R_k / d S_k = R_old*q*(R_old - 1)*(nu - 1) / (R_old*q - 1)  <  0

on 0 < q < 1, 0 < R_old < 1, 0 <= nu < 1 -- derived in SymPy, cross-checked in
Wolfram Language, and z3 returns `unsat` for "S_k was under-read and recomputed
R_k did NOT rise". The mis-read always substitutes R_base for S_k, and R_base is
far below S_k, so recomputed R_k is always pushed UP. The 2026-09-21 report's
"18 of 19 one-directional, p = 7.63e-05" measures how consistently this
extractor mis-reads, not what the seats computed.

THE CHECK RUNS THE REAL EXTRACTOR ON THE REAL ARCHIVED TEXT. It imports
`bench/reference_runner_v3.py` and reads the committed panel record; it does not
retype the function or the prose. It SKIPS rather than passes if the archive is
absent, so a missing fixture can never be mistaken for a green result.

Run:  python3 -m pytest bench/tests/test_rk_clip_stops_at_an_arrow_2026-09-22.py -q
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
RECORD = (REPO / "bench" / "logs" / "commissioning_arm1_panel_20260921T215405Z"
          / "r0_cc2-sim_20260921T220447Z.json")


def _runner():
    spec = importlib.util.spec_from_file_location("_rr3_arrowtest", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# The exact line the seat wrote, kept here ONLY as the minimal synthetic case.
# The archive test below is the one that binds; this one localises the defect.
_REAL_LINE = (
    "R_old=0.50, η=0.95, d=0.90, p=0.85 → q=0.727. "
    "R_det = 0.50×0.273/(1−0.363) = 0.215. "
    "S_k=0.92 → R_base = 0.92×0.215 + 0.08×0.50 = 0.237. "
    "ν_b=0.03, ν_f=0.10 → ν_eff = 1−0.97×0.992 = 0.038. "
    "**R_k = 0.237×0.962 + 0.038 = 0.266.**"
)


def test_an_arrow_bounds_a_parameter_statement():
    """p must read 0.85 (what the seat wrote), not 0.727 (the seat's q)."""
    rr3 = _runner()
    p = rr3._rk_stated_value(rr3._RK_RE_P, _REAL_LINE)
    sk = rr3._rk_stated_value(rr3._RK_RE_SK, _REAL_LINE)
    assert p == 0.85, (
        f"p read as {p!r}; the seat wrote p=0.85 and 0.727 is its q. "
        "_RK_RE_CLIP does not stop at U+2192, so the p statement ran on "
        "through the arrow into the q statement."
    )
    assert sk == 0.92, (
        f"S_k read as {sk!r}; the seat wrote S_k=0.92 and 0.237 is its R_base. "
        "Same unclipped arrow."
    )


def test_the_real_archived_section_is_not_falsely_graded_FAIL():
    """The committed seat response must grade PASS, not FAIL.

    This is the load-bearing assertion: it runs the shipped validator over the
    shipped archive, so it cannot be satisfied by a fixture written to suit it.
    """
    if not RECORD.is_file():
        pytest.skip(f"archive absent: {RECORD}")
    rr3 = _runner()
    text = json.loads(RECORD.read_text(encoding="utf-8")).get("response") or ""
    assert text, "panel record carries no response text"
    sections = rr3._extract_corroboration_sections(text)
    assert sections, "no CORROBORATION section extracted"
    status, model_rk, recomputed = rr3._validate_rk_computation(sections[0])
    assert model_rk == 0.266, f"stated R_k read as {model_rk!r}, expected 0.266"
    assert status == "PASS", (
        f"graded {status} with recomputed={recomputed!r} against the seat's "
        f"stated {model_rk!r}. The seat's arithmetic is right to 3 d.p.; the "
        f"extractor read its q as p and its R_base as S_k."
    )


def test_the_clip_direction_is_the_one_the_derivative_predicts():
    """Under-reading S_k must raise recomputed R_k -- the artefact's signature.

    Guards the *reason* the defect masqueraded as a finding, so a future change
    that reintroduces a downward S_k mis-read is recognised as one-directional
    by construction rather than re-reported as a discovery about the seats.
    """
    R_old, q, nu = 0.50, 0.727, 0.038

    def recomputed(sk: float) -> float:
        R_det = R_old * (1.0 - q) / (1.0 - q * R_old)
        return (sk * R_det + (1.0 - sk) * R_old) * (1.0 - nu) + nu

    # d R_k / d S_k < 0 on this domain, so a lower S_k gives a HIGHER R_k.
    assert recomputed(0.237) > recomputed(0.92)
    assert all(recomputed(a) > recomputed(b)
               for a, b in zip([0.1, 0.3, 0.5, 0.7], [0.3, 0.5, 0.7, 0.9]))


def test_ascii_arrow_was_already_clipped_and_still_is():
    """`->` was clipped incidentally by the '>' in the class. Keep it clipped."""
    rr3 = _runner()
    assert rr3._rk_stated_value(rr3._RK_RE_P, "p=0.85 -> q=0.727") == 0.85


def test_a_comma_and_a_comparison_still_bound_a_statement():
    """The 2026-09-07 repairs this sits beside must not regress."""
    rr3 = _runner()
    assert rr3._rk_stated_value(
        rr3._RK_RE_R_OLD, "R_old=0.50, eta=0.90, d=0.80, nu_f=0.07") == 0.50
    assert rr3._rk_stated_value(
        rr3._RK_RE_SK, "S* check: S_k = 0.90 > S* = 0.08") == 0.90


def test_a_decimal_point_is_not_a_clip():
    """Sentence punctuation clips; a decimal point must not."""
    rr3 = _runner()
    assert rr3._rk_stated_value(rr3._RK_RE_P, "p = 0.444.") == 0.444
