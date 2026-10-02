# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 176f6e2c030cfedcf2fc00b3fc52bb31ab25830f6f06c12a862d59d29c717a04
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The published explorer must stop on E[dR], not on the retired conditional dR.

PANEL SEAT (fable), 2026-09-28, checking CC1's item 1. The appendix retired
"continue while dR > theta" on 2026-09-21: dR is the change CONDITIONAL on the
non-detection branch, while the decision precedes the branch. The published
explorer still coloured a pass green on `s.dR >= o.theta` (the trajectory's own
decrement, which at sigma=1, nu=0 IS the conditional quantity) and printed
"stop ~ pass N" from it. DERIVED and verified on SymPy and Wolfram Language:

    E[dR] - dR_explorer = (1-nu)*sigma*q*R^2*(1-q)/(1-q*R) >= 0  everywhere,

so the defect was STRICTLY one-directional -- the explorer could only ever stop
EARLY, by a factor of 70.3 at R=0.99, q=0.3. The fix bases the stop decision and
chart-2 bars on E[dR] = R*q*sigma*(1-nu) - nu*(1-R) (appendix general form) and
KEEPS dR for what it is legitimately for: the trajectory chart, the nu* break-even
and the dR<0 hard exit (appendix section 1.1), none of which this changes.

If node is present the explorer's OWN JavaScript is executed; the Python
reimplementation runs everywhere.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "explorer" / "index.html"


def _sim_py(pi, p, eta, sigma, nu, N=40):
    q = eta * p
    R = pi
    steps = []
    for i in range(1, N + 1):
        R_old = R
        R_det = R * (1 - q) / (1 - q * R) if q < 1 else 0.0
        R_base = sigma * R_det + (1 - sigma) * R_old
        R_new = R_base * (1 - nu) + nu
        E = R_old * q * sigma * (1 - nu) - nu * (1 - R_old)
        steps.append({"dR": R_old - R_new, "E": E, "R_old": R_old})
        R = R_new
    return steps


def test_the_decision_reads_E_not_dR():
    src = HTML.read_text(encoding="utf-8")
    assert "const good = s.E >= o.theta" in src, "stop decision must read E"
    assert "const good = s.dR >= o.theta" not in src, "retired dR rule still live"
    assert "stopping threshold on E[ΔR]" in src, "slider still labelled for dR"


def test_dR_keeps_its_legitimate_roles():
    """The fix must not remove what dR is FOR: trajectory, nu*, hard exit."""
    src = HTML.read_text(encoding="utf-8")
    assert "dR: R_old - R_new" in src                       # trajectory decrement
    assert "s.dR < 0" in src                                # net-harm hard exit
    assert "nuStar" in src                                  # break-even nu*


def test_expected_gain_dominates_the_conditional_everywhere():
    """E - dR = (1-nu)*sigma*q*R^2*(1-q)/(1-q*R) >= 0: no reverse disagreement."""
    for pi in (0.2, 0.5, 0.85, 0.99):
        for p in (0.1, 0.3, 0.6, 0.9):
            for sigma in (0.1, 0.5, 1.0):
                for nu in (0.0, 0.05, 0.3):
                    for s in _sim_py(pi, p, 1.0, sigma, nu, N=10):
                        R, q = s["R_old"], p
                        closed = (1-nu)*sigma*q*R*R*(1-q)/(1-q*R)
                        assert s["E"] - s["dR"] >= -1e-12
                        assert abs((s["E"] - s["dR"]) - closed) < 1e-9


def test_the_worked_point_now_continues():
    """R=0.99, q=0.3, sigma=1, nu=0, theta=0.005: dR says grey, E says green."""
    s = _sim_py(0.99, 0.3, 1.0, 1.0, 0.0, N=1)[0]
    assert s["dR"] < 0.005, "the premature-stop point must still exhibit low dR"
    assert s["E"] >= 0.005, "E must continue at the high-risk point"
    assert abs(s["E"] / s["dR"] - 70.3) < 0.05


def test_the_explorers_own_javascript_agrees_with_the_python_model():
    """Execute the ACTUAL simulate() from index.html under node, if present."""
    node = shutil.which("node")
    if node is None:
        import pytest
        pytest.skip("node not installed; the Python reimplementation stands")
    src = HTML.read_text(encoding="utf-8")
    m = re.search(r"(function simulate\(o\)\{.*?\n\})", src, re.S)
    assert m, "simulate() not found in explorer/index.html"
    js = ("const N = 40; const PERT_STEP = 22;\n" + m.group(1) +
          "\nconst s = simulate({pi:0.99, p:0.3, eta:1, sigma:1, nu:0, pert:0});"
          "\nconsole.log(JSON.stringify([s.steps[0].dR, s.steps[0].E]));")
    r = subprocess.run([node, "-e", js], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    import json
    dR, E = json.loads(r.stdout.strip())
    assert abs(dR - 0.004224751067) < 1e-9
    assert abs(E - 0.297) < 1e-12


def test_the_operational_directive_scopes_the_Rq_corner():
    """PANEL SEAT (fable), 2026-09-28. The appendix scoped R*q as the sigma=1,
    nu=0 corner on 2026-09-21, but cdsfl_operational.md section 5 -- the document
    models actually use -- still taught E[dR] = R*q as THE stopping rule with no
    scoping. The two standing documents disagreed on the stopping quantity."""
    doc = (ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md")
    text = doc.read_text(encoding="utf-8")
    assert "R · q · σ · (1 − ν) − ν · (1 − R)" in text, (
        "the general expected-improvement form is missing from the operational "
        "stopping rule")
    assert "σ = 1, ν = 0 corner" in text
