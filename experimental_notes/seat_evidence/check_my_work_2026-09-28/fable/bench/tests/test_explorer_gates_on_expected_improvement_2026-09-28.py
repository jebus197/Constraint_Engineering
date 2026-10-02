# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c1fc0468693208b3f33024aaa233e855368d9814d94185532de2ee2050222023
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The revised explorer must gate stopping on the appendix's expected improvement.

Companion to `test_explorer_stopping_quantity_2026-09-28.py`, whose premise test
SKIPS once the page stops gating on dR. This file asserts the page's NEW state,
so the revision cannot silently regress: the gate is `s.eDR >= o.theta`, and the
eDR formula transcribed from the JavaScript is symbolically identical to
`MATHEMATICAL_APPENDIX.md:225`, E[ΔR] = R·q·σ·(1−ν) − ν·(1−R).

`nuStar` is deliberately UNCHANGED: it is exactly the appendix's own §ν*
(MATHEMATICAL_APPENDIX.md:280, σRq/(1−qR(1−σ))), which this seat derived to be
the precise break-even of the plotted trajectory's per-cycle change (dR = 0 ⟺
ν = ν*). Whether §ν* itself should be superseded by the expectation break-even
σRq/(σRq − R + 1) is an APPENDIX-level decision for the founder, and the page
must not run ahead of the committed model.
"""
from __future__ import annotations

import re
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
EXPLORER = ROOT / "explorer" / "index.html"

R, q, sigma, nu = sp.symbols("R q sigma nu", positive=True)


def test_the_gate_is_on_eDR_not_dR():
    text = EXPLORER.read_text(encoding="utf-8")
    assert re.search(r"s\.eDR\s*>=\s*o\.theta", text), "the stop gate is not on eDR"
    assert not re.search(r"s\.dR\s*>=\s*o\.theta", text), (
        "the retired dR gate is back; MATHEMATICAL_APPENDIX.md:217 retired it"
    )


def test_the_js_eDR_formula_matches_the_appendix():
    text = EXPLORER.read_text(encoding="utf-8")
    m = re.search(r"const eDR = ([^;]+);", text)
    assert m, "eDR is not computed in simulate()"
    js = m.group(1)
    expr = sp.sympify(
        js.replace("R_old", "R").replace("o.sigma", "sigma").replace("o.nu", "nu"),
        locals={"R": R, "q": q, "sigma": sigma, "nu": nu})
    appendix = R * q * sigma * (1 - nu) - nu * (1 - R)
    assert sp.simplify(expr - appendix) == 0, f"JS computes {expr}, appendix says {appendix}"


def test_the_trajectory_and_nustar_are_untouched():
    """The recursion (the appendix's own Stage 5 spec) and the appendix's own
    break-even stay as committed -- the fix is to the stop layer only."""
    text = EXPLORER.read_text(encoding="utf-8")
    assert "R*(1-q)/(1-q*R)" in text
    assert "o.sigma*R_old*q/(1 - q*R_old*(1-o.sigma))" in text
