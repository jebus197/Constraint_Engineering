#!/usr/bin/env python3
"""How often do the explorer's 2 modes name a DIFFERENT stopping pass?

WHY THIS SCRIPT EXISTS, and it is a defect report about its own author. The
figure `1268 of 3249 = 39.0274%` was written into `explorer/index.html`'s comments
-- a PUBLIC artefact -- computed in a throwaway shell heredoc that was never
committed. A panel seat then tried ~10 natural grids and could not reproduce 1268
from any of them (it obtained 872, 1107, 1115, 1171, 1179, 1256, 1413, 1510, 1913
and 4051). When that comment was corrected, the replacement figure `89.2328%` was
produced the SAME WAY and had the SAME defect.

`measured-rate-travels-with-its-script` is unambiguous: a number that exists only
as prose is not evidence, it is a claim about evidence. Three separate parties
measured this quantity and got 26%, 68% and 89% -- not because any of them erred,
but because each used a different grid and a different theta protocol, and none of
the grids travelled with its number. That is exactly the failure the rule names.

WHAT IS MEASURED HERE, stated so the number cannot mutate in transmission:
  grid       R and q over 19 values each (0.05..0.95 by 0.05), sigma over 10
             (0.1..1.0), nu over {0, 0.02, 0.05, 0.1} -- the 14440-point grid
             already committed in explorer_stopping_rule_is_superseded_2026-09-28.py
  theta      EACH MODE AT ITS OWN SHIPPED DEFAULT, read from the page's MODE table,
             because that is what a reader actually meets. A shared theta measures
             the quantities; the per-mode theta measures the tool.
  compared   only settings where BOTH modes name a stop inside N passes.

Both the grid and the theta protocol are printed with the result, so a reader can
tell this figure apart from one taken another way.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "explorer" / "index.html"

_PROBE = r"""
const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const N=60, PERT_STEP=22;
eval(js.match(/function simulate\(o\)\{[\s\S]*?\n\}/)[0]);
const sp=js.match(/function stopPass\(steps, theta, gain\)\{[\s\S]*?\n\}/);
if(!sp){console.error('stopPass() not found in the page');process.exit(2);}
eval(sp[0]);
const TP=parseFloat(js.match(/prospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+)/)[1]);
const TR=parseFloat(js.match(/retrospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+)/)[1]);
let diff=0, same=0, cmp=0, earlier=0, later=0;
const Rs=[],qs=[];
for(let i=1;i<=19;i++){Rs.push(i*0.05); qs.push(i*0.05);}
const sgs=[]; for(let i=1;i<=10;i++) sgs.push(i*0.1);
const nus=[0,0.02,0.05,0.1];
for(const R of Rs) for(const q of qs) for(const sg of sgs) for(const nu of nus){
  const sim=simulate({pi:R,p:q,eta:1,sigma:sg,nu,pert:0});
  const a=stopPass(sim.steps,TP,s=>s.eDR), b=stopPass(sim.steps,TR,s=>s.dR);
  if(a===null||b===null) continue;
  cmp++;
  if(a!==b){diff++; if(a<b) earlier++; else later++;} else same++;
}
console.log(JSON.stringify({theta_prospective:TP,theta_retrospective:TR,
  grid:Rs.length*qs.length*sgs.length*nus.length, compared:cmp,
  different:diff, same, earlier, later}));
"""


def main() -> int:
    node = shutil.which("node")
    if not node:
        print("node is not installed; the page's own JS cannot be executed", file=sys.stderr)
        return 2
    if not PAGE.is_file():
        print(f"missing {PAGE}", file=sys.stderr)
        return 2
    probe = ROOT / "scripts" / "_explorer_disagreement_probe.js"
    probe.write_text(_PROBE, encoding="utf-8")
    try:
        r = subprocess.run([node, str(probe), str(PAGE)],
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            print(f"probe failed: {r.stderr[:300]}", file=sys.stderr)
            return 2
        d = json.loads(r.stdout)
    finally:
        probe.unlink(missing_ok=True)

    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    mp.mp.dps = 40
    n, k = d["compared"], d["different"]
    w = proportion_confint(k, n, method="wilson")
    cp = proportion_confint(k, n, method="beta")
    z = mp.mpf('1.959963984540054')
    N_, K_ = mp.mpf(n), mp.mpf(k)
    ph = K_ / N_
    den = 1 + z**2 / N_
    c = (ph + z**2 / (2 * N_)) / den
    hw = z * mp.sqrt(ph * (1 - ph) / N_ + z**2 / (4 * N_**2)) / den

    print("EXPLORER MODE DISAGREEMENT -- how often the 2 modes name a different stop")
    print(f"  grid                   {d['grid']} points (R,q x19 each; sigma x10; nu in 0,.02,.05,.1)")
    print(f"  theta protocol         EACH MODE AT ITS OWN SHIPPED DEFAULT")
    print(f"                         prospective {d['theta_prospective']}, "
          f"retrospective {d['theta_retrospective']}  (read from the page)")
    print(f"  compared               {n} (both modes named a stop)")
    print(f"  DIFFERENT stop         {k} = {100.0*k/n:.4f}%")
    print(f"    Wilson 95%           [{100*w[0]:.4f}%, {100*w[1]:.4f}%]")
    print(f"    Clopper-Pearson 95%  [{100*cp[0]:.4f}%, {100*cp[1]:.4f}%]")
    print(f"    mpmath@40dps Wilson  [{mp.nstr(100*(c-hw),6)}%, {mp.nstr(100*(c+hw),6)}%]"
          f"   |agreement| {mp.nstr(abs((c-hw)-mp.mpf(str(w[0]))),3)}")
    print(f"  of those: prospective EARLIER {d['earlier']}, LATER {d['later']}")
    print()
    print("  A figure taken on another grid, or with a shared theta, is a DIFFERENT")
    print("  measurement and will not match. Quote this one only with its protocol.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
