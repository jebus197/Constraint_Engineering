"""Astra's branch table and the A-versus-M distinction, EXECUTED rather than read.

THE FOUNDER'S QUESTION, 2026-09-29, and his verdict. On the distinction between the
conditional update the chart plots and the unconditional expectation that should decide
whether to run a pass, he asked: *"OK, but does this mean our explorer, or our docs also
need work to reflect this? Even if it is just stated? Is stating it enough?"* and then
ruled *"Yes update the explorer as you suggest."* Separately, on the branch table:
*"Verdict: Yes do it."*

WHAT IS UNDER TEST, AND WHY IT IS EXECUTED. The page now carries two quantities that a
reader can confuse, and the confusion is decision-changing in one direction only:

    A = sigma*R_det + (1-sigma)*R     the model's CONDITIONAL update -- what is plotted
    M = R*(1 - q*sigma)               the UNCONDITIONAL expectation -- what decides

A >= M everywhere, so judging a pass by A alone understates its worth. The card states
that, shows both, and shows the quotient identity A = M / P(no detection) -- which is
EXACT AT sigma = 1 AND FALSE ELSEWHERE.

That last clause is why this file executes the renderer instead of asserting on its
source text. On 2026-09-28 a mode-switch clamp defect in this same page survived a
browser inspection because the probe used theta = 0.01, a value valid in BOTH ranges;
the bug lived only at the range edge. A probe that exercises sigma = 1 alone would
repeat that exactly: the identity branch is correct there and wrong everywhere else.
So the cases below straddle sigma = 1 deliberately.

CROSS-CHECK, not a second transcription. The reference values come from mpmath in the
appendix's own forms. The branch-expectation identity was proved independently by SymPy
and by Wolfram Language on 2026-09-29: `Resolve[ForAll[...], A - M >= 0]` returned True
and `Reduce[... && A - M < 0]` returned False (computed with Wolfram Language), while
SymPy reduced the same differences to an exact 0.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from mpmath import mp

mp.dps = 40

ROOT = Path(__file__).resolve().parent.parent.parent
PAGE = ROOT / "explorer" / "index.html"

_PROBE = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];
const simSrc = js.match(/function simulate\(o\)\{[\s\S]*?\n\}/)[0];
// EXECUTE THE PAGE'S OWN RENDERER. Re-implementing the identity branch here is exactly
// the failure this file exists to prevent.
const renSrc = js.match(/function renderBranches\(s, q, sigma\)\{[\s\S]*?\n\}/);
if (!renSrc) { console.error('FATAL: renderBranches() not found in the page'); process.exit(2); }
const N = 60, PERT_STEP = 22;
eval(simSrc);
let CAPTURED = '';
let HOST_PRESENT = true;
// The guard added 2026-09-29 means renderBranches returns early when the host is
// missing. A probe whose $ NEVER returns null cannot tell a working renderer from
// one that silently does nothing, so this probe models BOTH states.
const $ = (id) => (id === 'branchBody' && !HOST_PRESENT) ? null
                : ({ set innerHTML(v){ if (id === 'branchBody') CAPTURED = v; } });
eval(renSrc[0]);
const out = [];
for (const c of JSON.parse(process.argv[3])){
  const sim = simulate(c);
  const s = sim.steps[0];
  CAPTURED = '';
  HOST_PRESENT = true;
  renderBranches(s, sim.q, c.sigma);
  const withHost = CAPTURED;
  // Same call with the host absent: must write nothing and must not throw.
  CAPTURED = '<<untouched>>';
  HOST_PRESENT = false;
  let threw = null;
  try { renderBranches(s, sim.q, c.sigma); } catch (e) { threw = e.message; }
  const withoutHost = CAPTURED;
  HOST_PRESENT = true;
  out.push({first: s, q: sim.q, html: withHost,
            absent_html: withoutHost, absent_threw: threw});
}
console.log(JSON.stringify(out));
"""


def _node() -> str:
    exe = shutil.which("node")
    if not exe:
        pytest.skip("node is not installed; the page's own JS cannot be executed here")
    return exe


def run_page(cases: list[dict]) -> list[dict]:
    exe = _node()
    probe = ROOT / "bench" / "tests" / "_explorer_branch_probe.js"
    probe.write_text(_PROBE, encoding="utf-8")
    try:
        r = subprocess.run([exe, str(probe), str(PAGE), json.dumps(cases)],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, f"probe failed: {r.stderr[:500]}"
        return json.loads(r.stdout)
    finally:
        probe.unlink(missing_ok=True)


#: sigma STRADDLES 1 deliberately -- the quotient identity is exact only at sigma = 1.
CASES = [
    {"pi": .85, "p": .60, "eta": 1.0, "sigma": 1.00, "nu": .05, "pert": 0},   # identity exact
    {"pi": .85, "p": .60, "eta": 1.0, "sigma": .90, "nu": .05, "pert": 0},   # identity false
    {"pi": .50, "p": .80, "eta": 1.0, "sigma": 1.00, "nu": .00, "pert": 0},   # appendix example
    {"pi": .30, "p": .60, "eta": 1.0, "sigma": 0.00, "nu": .10, "pert": 0},   # sigma = 0 edge
    {"pi": .99, "p": .30, "eta": 1.0, "sigma": .50, "nu": .02, "pert": 0},   # near certainty
    # THE EXTERNAL REVIEWER'S COUNTEREXAMPLE, 2026-09-29: R=1/2, q=4/5, sigma=1/2.
    # It is the case that refutes calling A "the conditional risk" in general.
    {"pi": .50, "p": .80, "eta": 1.0, "sigma": .50, "nu": .00, "pert": 0},
]


def reference(c: dict) -> dict:
    """The appendix's forms in mpmath. NOT a transcription of the page."""
    R = mp.mpf(str(c["pi"])); q = mp.mpf(str(c["eta"])) * mp.mpf(str(c["p"]))
    s = mp.mpf(str(c["sigma"]))
    R_det = R * (1 - q) / (1 - q * R)
    return {"R_det": R_det,
            "A": s * R_det + (1 - s) * R,
            "M": R * (1 - q * s),
            "pDet": q * R, "pNo": 1 - q * R, "rDet": 1 - s,
            "gap_closed": R * R * q * s * (1 - q) / (1 - q * R)}


@pytest.fixture(scope="module")
def rows():
    return run_page(CASES)


class TestTheQuantitiesThePageComputes:
    def test_the_page_agrees_with_an_independent_mpmath_derivation(self, rows):
        for c, row in zip(CASES, rows):
            ref, got = reference(c), row["first"]
            for k in ("pDet", "pNo", "rDet"):
                assert abs(mp.mpf(got[k]) - ref[k]) < mp.mpf("1e-12"), (c, k)
            assert abs(mp.mpf(got["M_uncond"]) - ref["M"]) < mp.mpf("1e-12"), c
            assert abs(mp.mpf(got["R_base"]) - ref["A"]) < mp.mpf("1e-12"), c

    def test_the_branch_expectation_IS_M_for_every_sigma(self, rows):
        """qR(1-s) + (1-qR)*R_det == R(1-qs). Proved by SymPy and Wolfram; checked here."""
        for c, row in zip(CASES, rows):
            s = row["first"]
            across = (mp.mpf(s["pDet"]) * mp.mpf(s["rDet"])
                      + mp.mpf(s["pNo"]) * mp.mpf(s["R_det"]))
            assert abs(across - mp.mpf(s["M_uncond"])) < mp.mpf("1e-12"), (
                f"the table's own rows do not average to M at sigma={c['sigma']}")

    def test_the_probabilities_are_a_partition(self, rows):
        for row in rows:
            s = row["first"]
            assert abs(mp.mpf(s["pDet"]) + mp.mpf(s["pNo"]) - 1) < mp.mpf("1e-12")

    def test_A_is_never_below_M_and_the_gap_matches_its_closed_form(self, rows):
        for c, row in zip(CASES, rows):
            ref, s = reference(c), row["first"]
            gap = mp.mpf(s["R_base"]) - mp.mpf(s["M_uncond"])
            assert gap >= -mp.mpf("1e-15"), f"A < M at {c}, which Wolfram says is unreachable"
            assert abs(gap - ref["gap_closed"]) < mp.mpf("1e-12"), c

    def test_the_gap_is_strictly_positive_where_it_should_be(self, rows):
        """A guard that cannot distinguish cases is not a guard: sigma=0 must give 0."""
        by_sigma = {c["sigma"]: mp.mpf(r["first"]["R_base"]) - mp.mpf(r["first"]["M_uncond"])
                    for c, r in zip(CASES, rows)}
        assert by_sigma[0.0] == 0, "at sigma = 0 nothing is repaired, so A and M must coincide"
        assert by_sigma[1.0] > mp.mpf("1e-6"), "at sigma = 1 the gap must be real, not rounding"


class TestTheRenderedCardTellsTheTruthAboutTheIdentity:
    """The clause that is true at sigma = 1 and false elsewhere."""

    def test_at_sigma_1_the_card_asserts_the_exact_quotient(self, rows):
        for c, row in zip(CASES, rows):
            if c["sigma"] != 1.0:
                continue
            html = row["html"]
            assert "A = M ÷ P(no detection)" in html, c
            assert "ident live" in html
            assert "not</em> A" not in html

    def test_away_from_sigma_1_the_card_DENIES_the_quotient(self, rows):
        for c, row in zip(CASES, rows):
            if c["sigma"] == 1.0:
                continue
            html = row["html"]
            assert "not</em> A" in html, (
                f"at sigma={c['sigma']} the card must say the quotient is NOT A; it did not")
            assert "ident live" not in html, c

    def test_the_quotient_it_prints_at_sigma_1_really_is_A(self, rows):
        """Printing the identity is worthless if the printed number is not A."""
        import re
        for c, row in zip(CASES, rows):
            if c["sigma"] != 1.0:
                continue
            nums = re.findall(r"([0-9]+\.[0-9]{4}) ÷ ([0-9]+\.[0-9]{4}) = ([0-9]+\.[0-9]{4})",
                              row["html"])
            assert nums, f"no printed quotient found for {c}"
            M_s, pNo_s, quot_s = nums[0]
            assert abs(float(M_s) / float(pNo_s) - float(quot_s)) < 5e-4, nums
            assert abs(float(quot_s) - row["first"]["R_base"]) < 5e-4, (
                "the card prints a quotient that is not the plotted A")

    def test_both_branch_rows_and_the_expectation_row_are_present(self, rows):
        for row in rows:
            html = row["html"]
            assert "detected (a flaw was there, and was found)" in html
            assert "not detected" in html
            assert "M = R(1−qσ)" in html
            assert "A − M" in html

    def test_the_card_names_the_direction_of_the_error(self, rows):
        """The whole point: A reads worse, so A alone understates the pass."""
        assert "A always reads worse than M" in rows[0]["html"]


class TestTheGuardDoesNotMaskAMissingCard:
    """Added 2026-09-29 after an unguarded write took down 18 unrelated tests.

    The guard is correct -- the card is cosmetic and the charts are not -- but a
    guard that returns early can hide the card's absence. Two things must hold
    together: the renderer must survive a missing host, AND the shipped markup must
    actually contain the host, so the early return can never be the live behaviour.
    """

    def test_the_renderer_survives_a_missing_host_without_writing(self, rows):
        for row in rows:
            assert row["absent_threw"] is None, (
                f"renderBranches threw with no host: {row['absent_threw']}")
            assert row["absent_html"] == "<<untouched>>", (
                "renderBranches wrote somewhere despite the host being absent")

    def test_the_shipped_markup_really_contains_the_host(self):
        html = PAGE.read_text(encoding="utf-8")
        assert 'id="branchBody"' in html, (
            "the guard would silently disable the branch card: no host in the markup")
        assert 'id="branchCard"' in html

    def test_the_clear_path_in_draw_is_guarded_too(self):
        """Both write sites, not just the one this file exercises directly."""
        html = PAGE.read_text(encoding="utf-8")
        js = html.split("<script>")[1].split("</script>")[0]
        assert "$('branchBody').innerHTML" not in js, (
            "an UNGUARDED branchBody write is back in the page; it kills draw() "
            "entirely under any probe that does not stub that id")


class TestTheReviewersCounterexample:
    """R=1/2, q=4/5, sigma=1/2 -- where A is none of the other three quantities.

    Raised 2026-09-29 by an external assessment against the claim that A is the
    negative-branch conditional risk. It is not, except at sigma=1. This class pins
    the exact rational values so the page cannot drift back to the stronger reading.
    """

    @staticmethod
    def _case(rows):
        for c, r in zip(CASES, rows):
            if (c["pi"], c["p"], c["eta"], c["sigma"]) == (.50, .80, 1.0, .50):
                return r
        raise AssertionError("the counterexample case is missing from CASES")

    def test_all_four_quantities_are_distinct(self, rows):
        r = self._case(rows)["first"]
        Bm, M, A = mp.mpf(r["R_det"]), mp.mpf(r["M_uncond"]), mp.mpf(r["R_base"])
        quot = M / mp.mpf(r["pNo"])
        want = {"B-": mp.mpf(1)/6, "M": mp.mpf(3)/10, "A": mp.mpf(1)/3, "quot": mp.mpf(1)/2}
        got = {"B-": Bm, "M": M, "A": A, "quot": quot}
        for k in want:
            assert abs(got[k] - want[k]) < mp.mpf("1e-12"), (k, got[k], want[k])
        vals = sorted(float(v) for v in got.values())
        for x, y in zip(vals, vals[1:]):
            assert y - x > 1e-9, f"two of the four coincide: {got}"

    def test_A_is_not_the_conditional_risk_here(self, rows):
        r = self._case(rows)["first"]
        assert abs(mp.mpf(r["R_base"]) - mp.mpf(r["R_det"])) > mp.mpf("0.15"), (
            "A and B_- coincide at sigma=1/2, which would make the correction wrong")

    def test_the_page_DENIES_the_quotient_at_this_point(self, rows):
        assert "not</em> A" in self._case(rows)["html"]

    def test_the_page_no_longer_calls_A_a_conditional(self):
        js = PAGE.read_text(encoding="utf-8").split("<script>")[1].split("</script>")[0]
        assert "model\u2019s conditional update" not in js
        assert "conditional update" not in js, (
            "the page still describes A as a conditional update; it is a retained blend")
