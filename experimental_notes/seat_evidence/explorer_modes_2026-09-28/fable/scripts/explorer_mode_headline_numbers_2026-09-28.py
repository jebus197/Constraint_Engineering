# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'explorer_modes_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: f4e7385c7d27bf69c922d75cd3f0ef819e7f6329857b18eb12d759d1346052d8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Producer for EVERY measured figure quoted in explorer/index.html's mode comments.

The page quotes 3 headline measurements: the mode-disagreement rate, the
first-pass E[dR]/dR span, and the absence of gain re-clears (the premise of the
last-clearing stop rule). Before 2026-09-28 the first two shipped as prose with
no committed producer, and the disagreement figure was promptly misquoted
downstream ("1268 of 3249" became "1268 of 14440" in a panel brief) -- exactly
the corruption an unreproducible number invites. This script is the committed
producer: it EXECUTES the page's own simulate() and stopPass() in node (never a
re-implementation) over the same 14440-point slider grid committed in
scripts/explorer_stopping_rule_is_superseded_2026-09-28.py:

    pi, p in {0.05, 0.10, ..., 0.95}   (19 x 19)
    sigma in {0.1, ..., 1.0}           (10)
    nu    in {0, 0.02, 0.05, 0.1}      (4)      => 14440 combinations

and prints, with a Wilson 95% interval:
  1. how often the 2 modes, each at ITS OWN default theta (0.02 / 0.005), name a
     different stopping pass -- the comparison a reader experiences when toggling;
  2. the first-pass E[dR]/dR span over the grid (both positive);
  3. the number of gain-sequence re-clears (a sub-theta trough later re-cleared)
     with pert=0, for both gates -- expected 0: the recursion is deterministic
     and unimodal between perturbations, so the last-clearing rule cannot be
     dragged to the end of the chart by an accidental late clearing.

Requires node. Exit code 1 if any printed figure drifts from the values the page
quotes (so CI catches page/producer divergence).
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "explorer" / "index.html"

_PROBE = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];
const N = 60, PERT_STEP = 22;
eval(js.match(/function simulate\(o\)\{[\s\S]*?\n\}/)[0]);
eval(js.match(/function stopPass\(steps, theta, gate\)\{[\s\S]*?\n\}/)[0]);
const lin=(a,b,s)=>{const o=[];for(let v=a;v<=b+1e-9;v+=s)o.push(+v.toFixed(4));return o;};
let total=0, differ=0, rmin=Infinity, rmax=0, reclears=0;
for(const pi of lin(.05,.95,.05)) for(const p of lin(.05,.95,.05))
for(const sigma of lin(.1,1,.1)) for(const nu of [0,.02,.05,.1]){
  const sim=simulate({pi,p,eta:1,sigma,nu,pert:0}); total++;
  const sp=stopPass(sim.steps,0.02,s=>s.eDR), sr=stopPass(sim.steps,0.005,s=>s.dR);
  if(sp!==sr)differ++;
  const s0=sim.steps[0];
  if(s0.dR>1e-12&&s0.eDR>0){const r=s0.eDR/s0.dR; if(r<rmin)rmin=r; if(r>rmax)rmax=r;}
  for(const gate of [s=>s.dR, s=>s.eDR]){
    const g=sim.steps.map(gate);
    for(let i=1;i<g.length-1;i++){
      if(g[i]<g[i-1]-1e-15){
        for(let j=i+1;j<g.length;j++) if(g[j]>g[i]+1e-12){ reclears++; j=g.length; }
        break;
      }
    }
  }
}
console.log(JSON.stringify({total,differ,rmin,rmax,reclears}));
"""

# What the page's comments quote. If you change the page, change these together.
EXPECTED = {"total": 14440, "differ": 9824, "rmin": "1.0026", "rmax": "1956.10",
            "reclears": 0}


def wilson(k: int, n: int, z: float = 1.959963985) -> tuple[float, float]:
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return 100 * (c - hw), 100 * (c + hw)


def main() -> int:
    node = shutil.which("node")
    if not node:
        print("node is required (the page's own JS must be executed, not re-derived)")
        return 1
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(_PROBE)
        probe = f.name
    try:
        r = subprocess.run([node, probe, str(PAGE)], capture_output=True,
                           text=True, timeout=300)
    finally:
        Path(probe).unlink(missing_ok=True)
    if r.returncode != 0:
        print("probe failed:", r.stderr[:400])
        return 1
    got = json.loads(r.stdout)
    lo, hi = wilson(got["differ"], got["total"])
    print(f"grid points                          {got['total']}")
    print(f"modes name a different stop          {got['differ']} = "
          f"{100*got['differ']/got['total']:.4f}%  Wilson 95% [{lo:.4f}%, {hi:.4f}%]")
    print(f"first-pass E[dR]/dR span             {got['rmin']:.4f} to {got['rmax']:.2f}")
    print(f"gain-sequence re-clears (pert=0)     {got['reclears']}")
    ok = (got["total"] == EXPECTED["total"] and got["differ"] == EXPECTED["differ"]
          and f"{got['rmin']:.4f}" == EXPECTED["rmin"]
          and f"{got['rmax']:.2f}" == EXPECTED["rmax"]
          and got["reclears"] == EXPECTED["reclears"])
    print("MATCHES THE PAGE'S QUOTED FIGURES" if ok
          else "DRIFT: page comments quote different figures -- update them together")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
