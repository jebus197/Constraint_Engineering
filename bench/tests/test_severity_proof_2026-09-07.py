"""Severity must be a calculation, not a vote. Founder ruling, 2026-09-06.

THE FOUNDER'S QUESTION, verbatim: "If a model can demonstrably be shown to be
using the mathematical model (and tools) to calculate severity, then is that
really a vote? ... The difference is I think in requiring the models to provide
worked proofs in all cases."

It is a better fix than the one it replaced. The earlier proposal swapped the
model's float for a consequence-class rubric lookup, but the rubric was measured
against the number and agrees no better than chance (kappa = -0.0227, Fisher
p = 0.78) -- a different oracle, not a better one. A worked proof instead makes
the number RECOMPUTABLE, which is what separates arithmetic from assertion.

THE CHECK ALREADY EXISTED AND DECIDED NOTHING. `validate_round_rk` re-derived R_k
from each model's stated parameters and graded it; its own docstring said
"Advisory only -- logs WARN/FAIL but never rejects findings", the result built one
log line and was discarded, and the round prompt meanwhile told every model
"Findings missing any section will be rejected."

AND THE CHECK ITSELF WAS MISREADING THE MODELS. Measured over the archive with
the shipped code: 34 of 128 CORROBORATION sections scored FAIL, and the 3 largest
discrepancies all recomputed to exactly 1.0 while the model's own arithmetic was
correct to 3 decimals. The parameter reader could not cross a newline, so a model
writing the working the directive ORDERS it to show --

    nu_eff = 1 - (1 - nu_b)*(1 - (1 - S_k)*nu_f)
           = 1 - 0.97*(1 - 0.05*0.07)
           = 0.03340

-- had its nu_eff read as the leading 1. That forces R_k = 1.0 and grades the
model FAIL for the runner's own reading. The check punished compliance.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import reference_runner_v3 as R  # noqa: E402
from bench.dm._rk_proof import build_proof_requests  # noqa: E402


# --------------------------------------------------------------------------
# 1. The reader: real shapes taken from real archived responses.
# --------------------------------------------------------------------------

ALIGNED_BLOCK = """R_old = 0.50
η     = 0.90
d     = 0.95
p     = 0.90
S_k   = 0.95
ν_b   = 0.03
ν_f   = 0.07

q = η·d·p
  = 0.90 × 0.95 × 0.90
  = 0.7695

R_det = R_old·(1 − q) / (1 − q·R_old)
      = 0.18732

R_base = S_k·R_det + (1 − S_k)·R_old
       = 0.20296

ν_eff = 1 − (1 − ν_b)·(1 − (1 − S_k)·ν_f)
      = 1 − 0.97·(1 − 0.05×0.07)
      = 1 − 0.97·0.9965
      = 0.03340

R_k = R_base·(1 − ν_eff) + ν_eff
    = 0.20296·0.96660 + 0.03340
    = 0.22957
"""

DENSE_ONE_LINE = (
    "R_old=0.50, η=0.80, d=0.70, p=0.70, S_k=0.80, ν_b=0.03, ν_f=0.10. "
    "q=η×d×p=0.80×0.70×0.70=0.392. "
    "R_det=0.50×(1-0.392)/(1-0.392×0.50)=0.304/0.804=0.378. "
    "R_base=0.80×0.378+(1-0.80)×0.50=0.402. "
    "ν_eff=1-(1-0.03)×(1-(1-0.80)×0.10)=1-0.97×0.98=0.049. "
    "R_k=0.402×(1-0.049)+0.049=0.432. "
    "S*=((0.03+0.10-0.03×0.10)-(0.392×0.50))/(0.10×(1-0.03))=-0.711, "
    "so S_k=0.80 is above break-even."
)

S_STAR_TRAP = """R_old=0.50, η=0.90, d=0.85, p=0.80, S_k=0.90, ν_b=0.04, ν_f=0.12
q = 0.90 × 0.85 × 0.80 = 0.612
R_det = 0.50 × (1 − 0.612) / (1 − 0.612 × 0.50) = 0.280
R_base = 0.90 × 0.280 + 0.10 × 0.50 = 0.302
ν_eff = 1 − (1 − 0.04) × (1 − (1 − 0.90) × 0.12) = 1 − 0.96 × 0.988 = 0.051
R_k = 0.302 × (1 − 0.051) + 0.051 = 0.338
S* check: S_k=0.90 > S* ≈ 0.08 → fix is above break-even. Accepted.
"""


def test_the_multi_line_working_the_directive_demands_now_reads_correctly():
    """The headline regression. Before the fix nu_eff read as 1, R_k recomputed
    to exactly 1.0, and a correct model was graded FAIL."""
    assert R._rk_stated_value(R._RK_RE_NU_EFF, ALIGNED_BLOCK) == pytest.approx(0.0334)
    status, model_rk, recomputed = R._validate_rk_computation(ALIGNED_BLOCK)
    assert recomputed != pytest.approx(1.0), "the exactly-1.0 signature is back"
    assert model_rk == pytest.approx(0.22957)
    assert status == "PASS", f"got {status}: model {model_rk}, recomputed {recomputed}"


def test_the_dense_single_line_form_reads_its_own_R_k_not_the_trailing_S_k():
    """The statement ran on past its answer into the next sentence, so R_k came
    back as 0.80 -- the model's S_k -- and nu_eff came back as nothing."""
    assert R._rk_stated_value(R._RK_RE_NU_EFF, DENSE_ONE_LINE) == pytest.approx(0.049)
    status, model_rk, recomputed = R._validate_rk_computation(DENSE_ONE_LINE)
    assert model_rk == pytest.approx(0.432), f"read {model_rk}, not the stated R_k"
    assert status in ("PASS", "WARN"), f"got {status}, recomputed {recomputed}"


def test_S_k_is_the_declared_parameter_not_the_threshold_it_is_compared_against():
    """'S* check: S_k=0.90 > S* = 0.08' made S_k read as 0.08 and turned 6
    correct sections into FAILs when the reader took the LAST occurrence."""
    assert R._rk_stated_value(R._RK_RE_SK, S_STAR_TRAP) == pytest.approx(0.90)
    status, model_rk, recomputed = R._validate_rk_computation(S_STAR_TRAP)
    assert status == "PASS", f"got {status}: model {model_rk}, recomputed {recomputed}"


def test_a_formula_with_no_evaluated_result_states_nothing():
    """Mining an operand out of an unevaluated expression is how the earlier
    reader produced accusations against arithmetic no model wrote."""
    assert R._rk_stated_value(
        R._RK_RE_NU_EFF, "nu_eff = 1 - (1-nu_b)*(1-(1-S_k)*nu_f)") is None


def test_a_comma_separated_list_reads_each_parameter_as_its_own():
    line = "R_old=0.50, η=0.90, d=0.80, p=0.70, S_k=0.95, nu_b=0.02, nu_f=0.05"
    assert R._rk_stated_value(R._RK_RE_R_OLD, line) == pytest.approx(0.50)
    assert R._rk_stated_value(R._RK_RE_SK, line) == pytest.approx(0.95)


def test_the_reader_is_load_bearing_and_this_suite_is_not_vacuous():
    """REVERT TEST. Restore the pre-fix single-line semantics and prove the
    aligned block goes back to recomputing exactly 1.0. Without this the tests
    above could pass against a reader that never changed."""
    m = R._RK_RE_NU_EFF.search(ALIGNED_BLOCK)          # the OLD extraction
    old_value = float(m.group(1))
    assert old_value == 1.0, "the pre-fix reader no longer reproduces its own bug"
    R_old, q, sk = 0.50, 0.7695, 0.95
    R_det = R_old * (1 - q) / (1 - q * R_old)
    R_base = sk * R_det + (1 - sk) * R_old
    old_recomputed = max(0.0, min(1.0, R_base * (1 - old_value) + old_value))
    assert old_recomputed == pytest.approx(1.0), (
        "the old reader's signature failure was recomputed == exactly 1.0")


# --------------------------------------------------------------------------
# 2. The enforcement: an unproven severity may never make the gate looser.
# --------------------------------------------------------------------------

def test_proof_status_reading():
    assert R.severity_is_proven({"severity_proof": {"status": "PASS"}}) is True
    assert R.severity_is_proven({"severity_proof": {"status": "WARN"}}) is True
    assert R.severity_is_proven({"severity_proof": {"status": "FAIL"}}) is False
    assert R.severity_is_proven({"severity_proof": {"status": "SKIP"}}) is False
    assert R.severity_is_proven({}) is False, "no proof is not a proof"
    assert R.severity_proof_status({}) == "ABSENT"


class _Reg:
    def __init__(self, entries): self.entries = entries


def _eligible_entry(proof_status):
    """Demotion-eligible by every existing criterion, differing only in proof."""
    e = {
        "severity": 0.85,
        "status": "OPEN",
        "falsifier_verdict": "CONFIRMED",
        "latent": True,
        "finding_category": "performance",
    }
    if proof_status is not None:
        e["severity_proof"] = {"status": proof_status}
    return e


class _Cfg:
    severity_calibration_enabled = True
    severity_calibration_floor = 0.69


def test_a_proven_severity_can_be_demoted():
    reg = _Reg({"C0001": _eligible_entry("PASS")})
    n = R._apply_severity_calibration(reg, _Cfg(), 3)
    assert n == 1
    assert reg.entries["C0001"]["severity"] < R.CRITICAL_SEVERITY_THRESHOLD


@pytest.mark.parametrize("proof", ["FAIL", "SKIP", None])
def test_an_unproven_severity_cannot_buy_a_demotion(proof):
    """Demotion is the one place the number makes the gate LOOSER: it lifts a
    blocking critical out of the count. An unrecomputable number must not do
    that, or a model could clear the gate by omitting its arithmetic."""
    reg = _Reg({"C0001": _eligible_entry(proof)})
    n = R._apply_severity_calibration(reg, _Cfg(), 3)
    assert n == 0, f"an entry with proof={proof} was demoted"
    assert reg.entries["C0001"]["severity"] == pytest.approx(0.85), "severity moved"
    assert reg.entries["C0001"]["severity"] >= R.CRITICAL_SEVERITY_THRESHOLD, (
        "the finding stopped counting as a blocking critical")


def test_the_guard_is_one_directional_and_never_clears_a_finding():
    """The enforcement must not delete findings: a defect reported without a
    proof may still be a real defect. It keeps its severity and its status."""
    reg = _Reg({"C0001": _eligible_entry("FAIL")})
    R._apply_severity_calibration(reg, _Cfg(), 3)
    assert "C0001" in reg.entries
    assert reg.entries["C0001"]["status"] == "OPEN"


# --------------------------------------------------------------------------
# 3. The route-back: the model is told, in its own numbers.
# --------------------------------------------------------------------------

def test_the_request_names_the_finding_and_both_numbers():
    out = build_proof_requests([("C0007", "FAIL", 0.23, 1.0)])
    assert "C0007" in out
    assert "0.2300" in out and "1.0000" in out
    assert "0.7700" in out, "the model should see the size of the discrepancy"
    assert "withdraw" in out.lower(), "withdrawal must be offered as legitimate"


def test_no_requests_produces_no_section():
    assert build_proof_requests([]) == ""


def test_the_request_is_capped_and_says_how_many_it_did_not_show():
    reqs = [(f"C{i:04d}", "SKIP", None, None) for i in range(25)]
    out = build_proof_requests(reqs, max_entries=5)
    assert "further finding(s) awaiting" in out


def test_both_dispatch_topologies_receive_the_section():
    """A wiring guard, deliberately structural: enforcement that is real on the
    relay path and cosmetic on the star path is the failure this project keeps
    finding. Two call sites must exist."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    assert src.count("build_rk_proof_requests(") == 2, (
        "the severity-proof section no longer reaches both dispatch paths")


def test_a_HIL_adjudicated_latency_demotes_even_without_a_model_proof():
    """The one carve-out, and it is required by the no-voting rule rather than an
    exception to it. Demotion eligibility needs entry["latent"], and the tagger
    records where that came from: "prose"/"explicit_field" mean the MODEL said
    so, which is the vote being policed; "external" means HIL ruled. Blocking a
    human ruling for want of a model's arithmetic would invert the rule."""
    e = _eligible_entry(None)
    e["latent_source"] = "external"
    reg = _Reg({"C0001": e})
    n = R._apply_severity_calibration(reg, _Cfg(), 3)
    assert n == 1, "a HIL-adjudicated latency was refused for want of a model proof"
    assert reg.entries["C0001"]["severity"] < R.CRITICAL_SEVERITY_THRESHOLD


@pytest.mark.parametrize("source", ["prose", "explicit_field", "", None])
def test_a_model_asserted_latency_still_needs_the_proof(source):
    e = _eligible_entry("FAIL")
    e["latent_source"] = source
    reg = _Reg({"C0001": e})
    assert R._apply_severity_calibration(reg, _Cfg(), 3) == 0
