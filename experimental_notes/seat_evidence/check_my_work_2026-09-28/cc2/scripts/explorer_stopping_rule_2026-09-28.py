# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 77d3b83765c94debffcb109efabdab00eeb97ce9f7e221b05cda6072db29f7ad
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does the PUBLISHED explorer's stop annotation contradict its own bars?

`explorer/index.html` is served at
`jebus197.github.io/Constraint_Engineering/explorer/`. Its lower chart plots the
per-pass gain `dR = R_old - R_new` of the Stage 5 three-phase recursion, draws a
dashed line at the slider `theta`, and prints `stop ~ pass N`.

THE DEFECT THIS FALSIFIES. The old code latched `stopAt` on the FIRST pass whose
bar fell under theta and never revised it. But `dR` is NOT monotone in `R`. SymPy
gives, for the recursion in the page,

    dR(R) = R - ( (sigma*R*(1-q)/(1-q*R) + (1-sigma)*R) * (1-nu) + nu )

and at nu = 0 that is exactly  sigma * q*R*(1-R)/(1-q*R)  -- sigma times the
quantity `docs/MATHEMATICAL_APPENDIX.md:217` qualified on 2026-09-21. Its maximum
in R sits at R* = (1 - sqrt(1-q))/q, INDEPENDENT of sigma, so the page inherits the
appendix's premature-stop band whole. Above that peak the relation inverts: as risk
falls toward R*, the per-pass gain RISES. A first crossing at high R therefore means
"not yet past the peak", not "exhausted" -- and the page's own default preset opens
at pi = 0.85, above R* across most of the p range.

WHY THIS NEEDS NO APPEAL TO THE APPENDIX. It checks a property the page owes
itself: if the page says "stop at pass N", no bar after pass N may stand above the
theta line the page drew. Internal consistency, decided by executing the page's OWN
code. The separate disagreement about which stopping QUANTITY is correct -- this
seat holds that the appendix's `R*q*sigma*(1-nu) - nu*(1-R)` is the improvement of a
DIFFERENT recursion and must NOT be pasted over `dR` -- is deliberately kept out of
it, so the verdict does not depend on winning that argument.

IT READS THE REAL FILE. `simulate()` and the stop-computation block are extracted
verbatim from `explorer/index.html` and executed under node. Nothing is retyped: a
model-authored copy of the recursion would prove nothing about the published page.
Canvas calls are stubbed, because the arithmetic under test touches no canvas.

NO WOLFRAM. Anyone reproducing this project must not need it installed.

Exit 0 = consistent. `FALSIFIED` + AssertionError = the page contradicts itself.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
#: Optional argv override so CI can point at a built/staged copy, and so the
#: DISCRIMINATION check below can be run against a deliberately reverted page.
#: A falsifier that has never been shown to FAIL on the defect it names is a
#: hypothesis; `scripts/explorer_stopping_rule_2026-09-28.py <reverted.html>`
#: is how that was demonstrated.
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "explorer" / "index.html"

#: The page's own slider ranges, read off its `<input type=range>` elements. The
#: sweep stays inside what a visitor can actually select; a defect reachable only
#: outside the sliders would not be a defect of the published page.
SWEEP = {
    "pi":    [x / 100 for x in range(5, 100, 5)],
    "p":     [x / 100 for x in range(5, 96, 5)],
    "sigma": [0.0, 0.25, 0.5, 0.75, 0.9, 1.0],
    "nu":    [0.0, 0.05, 0.1, 0.2, 0.3, 0.5],
    "theta": [0.001, 0.005, 0.01, 0.02, 0.05],
    "pert":  [0.0, 0.3],
}


def _extract(src: str):
    """(simulate source, stop-computation source), both verbatim from the page.

    The stop block runs from the first `let firstCross`/`let stopAt` declaration to
    the `line(ctx2, ...)` call that draws the theta rule. Lines touching the drawing
    context are dropped -- the only part that cannot run headless, and it computes
    nothing the stop depends on. BOTH the pre- and post-fix shapes of the block
    survive this treatment, which is what lets one falsifier discriminate between
    them rather than merely failing to parse the old one.
    """
    m = re.search(r"function simulate\(o\)\{.*?\n\}", src, re.S)
    if not m:
        raise SystemExit("simulate() not found in explorer/index.html -- the page "
                         "changed shape; fix this extractor, not the result")
    start = re.search(r"^\s*let (?:firstCross|stopAt) = null;", src, re.M)
    end = re.search(r"^\s*line\(ctx2,", src, re.M)
    if not start or not end or end.start() < start.start():
        raise SystemExit("the stop-computation block was not located in "
                         "explorer/index.html -- fix this extractor, not the result")
    block = "\n".join(ln for ln in src[start.start():end.start()].splitlines()
                      if "ctx2" not in ln)
    return m.group(0), block


HARNESS = r"""
%(simulate)s
// Canvas stubs. The stop arithmetic touches none of these; they exist so the
// page's own lines execute UNALTERED rather than being rewritten to fit the test.
const c2 = {width: 900, height: 260};
const M = {l:52, r:16, t:14, b:30};
const X = () => 0, Y = () => 0;
// The grid is fed on STDIN: 129,960 cases overflow argv (Errno 7).
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = [];
for (const o of cases){
  const sim = simulate(o);
  const dmax = 1;
  %(block)s
  const cut = (typeof stopAt === 'undefined' || stopAt === null) ? 1e9 : stopAt;
  const after = sim.steps.filter(s => s.i > cut).map(s => s.dR);
  out.push({o, stopAt: (typeof stopAt === 'undefined') ? null : stopAt,
            worstAfter: after.length ? Math.max.apply(null, after) : null});
}
process.stdout.write(JSON.stringify(out));
"""


def main() -> int:
    if not shutil.which("node"):
        print("node is not installed; this falsifier could not run and has "
              "therefore VERIFIED NOTHING.", file=sys.stderr)
        return 4

    src = PAGE.read_text(encoding="utf-8")
    simulate, block = _extract(src)
    n_match = re.search(r"\bN\s*=\s*(\d+)", src)
    pert_match = re.search(r"PERT_STEP\s*=\s*(\d+)", src)
    prelude = (f"const N = {n_match.group(1) if n_match else 40};\n"
               f"const PERT_STEP = {pert_match.group(1) if pert_match else 22};\n")

    cases = [{"pi": pi, "p": p, "eta": 1, "sigma": sg, "nu": nu,
              "theta": th, "pert": pe}
             for pi in SWEEP["pi"] for p in SWEEP["p"] for sg in SWEEP["sigma"]
             for nu in SWEEP["nu"] for th in SWEEP["theta"] for pe in SWEEP["pert"]]

    js = prelude + HARNESS % {"simulate": simulate, "block": block}
    r = subprocess.run(["node", "-e", js], input=json.dumps(cases),
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[:2000], file=sys.stderr)
        raise SystemExit("the extracted page code did not run; that is an "
                         "EXTRACTOR failure, not a demonstration of the defect")
    rows = json.loads(r.stdout)

    bad = [x for x in rows
           if x["stopAt"] is not None and x["worstAfter"] is not None
           and x["worstAfter"] >= x["o"]["theta"]]
    announced = sum(1 for x in rows if x["stopAt"] is not None)

    print(f"slider-reachable grid points swept      : {len(rows)}")
    print(f"points where the page announces a stop  : {announced}")
    print(f"points where a LATER bar clears theta   : {len(bad)} "
          f"= {100.0*len(bad)/len(rows):.4f}%")
    q = 0.45
    print(f"peak of dR at q={q} (default preset)   : R* = (1-sqrt(1-q))/q = "
          f"{(1-math.sqrt(1-q))/q:.6f}  -- independent of sigma, SymPy-derived")

    if bad:
        worst = max(bad, key=lambda x: x["worstAfter"] / max(x["o"]["theta"], 1e-12))
        print("FALSIFIED")
        print(f"  worst case: {worst['o']}")
        print(f"    announced stop = pass {worst['stopAt']}, yet a later pass "
              f"reaches dR = {worst['worstAfter']:.6f} >= theta "
              f"= {worst['o']['theta']}")
        raise AssertionError(
            f"explorer/index.html contradicts its own chart at {len(bad)} of "
            f"{len(rows)} slider-reachable points: it prints 'stop ~ pass N' "
            f"while drawing a later bar above the theta line it drew")

    print()
    print("CONSISTENT: wherever the page announces a stop, no later bar on the "
          "same chart stands above theta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
