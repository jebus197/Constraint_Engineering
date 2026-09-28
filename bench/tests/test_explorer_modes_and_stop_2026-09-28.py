"""The explorer answers 2 questions, and its stop rule must survive a rising gain.

FOUNDER'S RULING, 2026-09-28, verbatim: *"What does the researcher want? Do they
want to look at how an experiment behaved in retrospect, or do they want to check
how it would be likely to behave before running it? Surely that should be up to
them? AKA again a not directly binary choice?"*

Both panel seats treated this as binary and chose opposite sides -- 1 kept the
realised drop and fixed the stop rule, the other switched the gate to the
expectation. Neither built a mode. The ruling dissolves the disagreement: each
seat was right about its own question.

EVERY TEST HERE EXECUTES THE PAGE'S OWN JAVASCRIPT. `execute-do-not-grep` is
explicit that a test asserting on SOURCE TEXT proves only that a file describes
itself consistently. So `simulate()` is lifted verbatim out of the HTML and run in
node, and its outputs are compared against an independent mpmath derivation. A
drift between the page and the maths fails here rather than in front of a reader.

MEASURED, WITH ITS PROTOCOL ATTACHED. `scripts/explorer_mode_disagreement_2026-09-28.py`
executes THIS page over a committed 14,440-point grid with each mode at its own
shipped theta: the 2 modes name a DIFFERENT stopping pass in 8,634 of the 8,904
settings where both name one at all = 96.9677%, Wilson 95% [96.5907%, 97.3041%], and
prospective is the EARLIER one in 8,293 of those.

THE FIGURE THIS REPLACES WAS UNPRODUCIBLE. This docstring previously read "1268 of
3249 combinations = 39.0274%", which shipped with no committed producer and which no
panel seat could reproduce from any natural grid. It also stated, without the
qualifier that carries it, that "the prospective view never stops earlier than the
retrospective one". That ordering is a theorem about the 2 QUANTITIES AT A SHARED
theta -- E[dR] >= dR everywhere on the open cube -- and it does NOT transfer to this
page, which ships 0.02 against 0.005. The tool inverts it in the large majority of
comparable settings, as the figure above records. Corrected 2026-09-28; the
class-level docstrings below already carry the qualifier, and
`test_the_tool_does_NOT_inherit_that_ordering` asserts the non-transfer.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import mpmath as mp
import pytest

mp.mp.dps = 30
ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "explorer" / "index.html"

_PROBE = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];
const simSrc = js.match(/function simulate\(o\)\{[\s\S]*?\n\}/)[0];
// EXECUTE THE PAGE'S OWN STOP RULE. Re-implementing it here is what let a restored
// first-dip latch keep all 8 tests green on 2026-09-28.
const stopSrc = js.match(/function stopPass\(steps, theta, gain\)\{[\s\S]*?\n\}/);
if (!stopSrc) { console.error('FATAL: stopPass() not found in the page'); process.exit(2); }
const N = 60, PERT_STEP = 22;
eval(simSrc);
eval(stopSrc[0]);
const stopFor = (steps, theta, gate) => stopPass(steps, theta, gate);
// THE SHIPPED THETAS, READ FROM THE PAGE'S OWN MODE TABLE. Hardcoding them in the
// test is what let a mutation giving both modes the same theta pass 9/9 on
// 2026-09-28 -- the 4th time that day a test re-derived a value the page owns.
const THETA = {
  prospective:  parseFloat(js.match(/prospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+)/)[1]),
  retrospective: parseFloat(js.match(/retrospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+)/)[1]),
};
function firstDip(steps, theta, gate){
  let st = null;
  steps.forEach(s => { if (st===null && gate(s) < theta && s.i > 1) st = s.i; });
  return st;
}
const out = [{__theta: THETA}];
for (const c of JSON.parse(process.argv[3])){
  const sim = simulate(c);
  out.push({
    first: sim.steps[0],
    stop_prosp: stopFor(sim.steps, c.theta, s=>s.eDR),
    stop_retro: stopFor(sim.steps, c.theta, s=>s.dR),
    stop_olddip: firstDip(sim.steps, c.theta, s=>s.dR),
    max_after_olddip: (()=>{ const d = firstDip(sim.steps, c.theta, s=>s.dR);
      return d===null ? null : Math.max(...sim.steps.filter(s=>s.i>d).map(s=>s.dR)); })(),
  });
}
console.log(JSON.stringify(out));
"""


def _node():
    exe = shutil.which("node")
    if not exe:
        pytest.skip("node is not installed; the page's own JS cannot be executed here")
    return exe


def run_page(cases: list[dict]) -> tuple[dict, list[dict]]:
    exe = _node()
    probe = ROOT / "bench" / "tests" / "_explorer_probe.js"
    probe.write_text(_PROBE, encoding="utf-8")
    try:
        r = subprocess.run([exe, str(probe), str(PAGE), json.dumps(cases)],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, f"probe failed: {r.stderr[:400]}"
        rows = json.loads(r.stdout)
        return rows[0]["__theta"], rows[1:]
    finally:
        probe.unlink(missing_ok=True)


def reference(c: dict) -> dict:
    """Independent mpmath derivation. NOT a second transcription of the page:
    these are the appendix's forms, so agreement is a real cross-check."""
    R = mp.mpf(str(c["pi"])); q = mp.mpf(str(c["eta"])) * mp.mpf(str(c["p"]))
    s = mp.mpf(str(c["sigma"])); v = mp.mpf(str(c["nu"]))
    R_det = R * (1 - q) / (1 - q * R)
    R_base = s * R_det + (1 - s) * R
    R_new = R_base * (1 - v) + v
    return {
        "dR": R - R_new,
        "eDR": R * q * s * (1 - v) - v * (1 - R),
        "nuStar": s * R * q / (1 - q * R * (1 - s)),
        "nuStarExp": R * q * s / (R * q * s - R + 1),
    }


DEFAULTS = {"pi": 0.85, "p": 0.45, "eta": 1, "sigma": 0.9, "nu": 0.05,
            "theta": 0.005, "pert": 0}


class TestThePageComputesWhatTheAppendixSays:
    @pytest.mark.parametrize("case", [
        DEFAULTS,
        {**DEFAULTS, "pi": 0.99, "p": 0.3, "sigma": 1, "nu": 0},
        {**DEFAULTS, "pi": 0.4, "p": 0.8, "sigma": 0.5, "nu": 0.2},
    ])
    def test_all_four_quantities_match_mpmath(self, case):
        _, rows = run_page([case]); got = rows[0]["first"]
        want = reference(case)
        for k in ("dR", "eDR", "nuStar", "nuStarExp"):
            assert abs(mp.mpf(str(got[k])) - want[k]) < mp.mpf("1e-12"), (
                f"{k}: page {got[k]} vs mpmath {want[k]}"
            )


class TestTheStopRuleSurvivesARisingGain:
    """THE DEFECT THIS REPLACES, demonstrated rather than described."""

    def test_a_perturbation_exposes_the_old_first_dip_rule(self):
        case = {**DEFAULTS, "theta": 0.02, "pert": 0.4}
        _, _rows = run_page([case]); r = _rows[0]
        assert r["stop_olddip"] is not None
        assert r["stop_retro"] is not None
        assert r["stop_retro"] > r["stop_olddip"] + 5, (
            f"old rule stopped at {r['stop_olddip']}, corrected rule at "
            f"{r['stop_retro']} -- expected a wide gap on a perturbed run"
        )

    def test_gains_after_the_old_stop_still_cleared_theta(self):
        """The old announcement was wrong because work remained, not merely late."""
        case = {**DEFAULTS, "theta": 0.02, "pert": 0.4}
        _, _rows = run_page([case]); r = _rows[0]
        assert r["max_after_olddip"] >= case["theta"], (
            "no pass after the old stop cleared theta; the premise of this fix fails"
        )

    def test_a_monotone_run_is_unchanged_by_the_fix(self):
        """ANTI-VACUITY: where the gain never rises again, both rules must agree."""
        _, _rows = run_page([DEFAULTS]); r = _rows[0]
        assert r["stop_retro"] == r["stop_olddip"], (
            f"corrected {r['stop_retro']} vs old {r['stop_olddip']} on an "
            "unperturbed run -- the fix must not move a stop that was right"
        )


class TestTheTwoModesAreDistinctAndOrdered:
    def test_prospective_never_stops_before_retrospective_AT_EQUAL_THETA(self):
        """E[dR] >= dR everywhere (z3 unsat it can be below), so AT A SHARED theta
        the prospective view runs at least as long.

        THE QUALIFIER IS LOAD-BEARING AND WAS MISSING. This test passes ONE theta to
        both gates, so it is a statement about the 2 QUANTITIES. It is NOT a statement
        about the page, which ships different thetas per mode (0.02 vs 0.005). Executed
        over 4,653 settings at the shipped defaults, the prospective view stops
        strictly EARLIER in 4,152 = 89.2328%, Wilson 95% [88.3095%, 90.0912%]. A panel
        seat found this test reading as a guarantee about the tool on 2026-09-28; the
        companion below now measures the tool."""
        cases = [DEFAULTS,
                 {**DEFAULTS, "pi": 0.99, "p": 0.3, "sigma": 1, "nu": 0},
                 {**DEFAULTS, "pi": 0.6, "p": 0.2},
                 {**DEFAULTS, "theta": 0.02, "pert": 0.4}]
        _, _rows = run_page(cases)
        for c, r in zip(cases, _rows):
            if r["stop_prosp"] is None or r["stop_retro"] is None:
                continue
            assert r["stop_prosp"] >= r["stop_retro"], (
                f"{c}: prospective {r['stop_prosp']} < retrospective {r['stop_retro']}"
            )

    def test_the_modes_actually_differ_somewhere(self):
        """ANTI-VACUITY: identical modes would satisfy the ordering test trivially."""
        _, _rows = run_page([DEFAULTS]); r = _rows[0]
        assert r["stop_prosp"] != r["stop_retro"], (
            "the 2 modes named the same stop at the shipped defaults; if this is "
            "genuinely so, the mode switch is not earning its place"
        )

    def test_the_tool_does_NOT_inherit_that_ordering(self):
        """ANTI-OVERCLAIM. The page scales theta per mode, so the fixed-theta theorem
        does not transfer. This is asserted so no future reader mistakes the test
        above for a property of the shipped page."""
        cases, thetas = [], []
        for pi in (0.3, 0.6, 0.9):
            for pp in (0.2, 0.5, 0.8):
                cases.append({**DEFAULTS, "pi": pi, "p": pp})
        # 2 batched runs, not 2 per case: the probe is a subprocess.
        th, _ = run_page([DEFAULTS])
        _, prosp = run_page([{**c, "theta": th["prospective"]} for c in cases])
        _, retro = run_page([{**c, "theta": th["retrospective"]} for c in cases])
        if abs(th["prospective"] - th["retrospective"]) < 1e-12:
            pytest.skip("the page now ships 1 theta for both modes; the ordering "
                        "theorem then DOES transfer and this test does not apply")
        earlier = compared = 0
        for a, b in zip(prosp, retro):
            rp, rr = a["stop_prosp"], b["stop_retro"]
            if rp is None or rr is None:
                continue
            compared += 1
            if rp < rr:
                earlier += 1
        assert compared > 0, "no case produced a stop in both modes; nothing measured"
        assert earlier > 0, (
            f"over {compared} comparable settings the shipped per-mode thetas produced "
            "no case where prospective stops earlier; if that is genuinely so, the "
            "page comment's measured 89.2328% needs re-taking"
        )
