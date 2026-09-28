"""Each question has its own floor, and the regime sentence must describe the drawn line.

TWO PANEL SEATS, TWO FAULTS, ONE PUBLIC PAGE. `explorer/index.html` is served at
jebus197.github.io/Constraint_Engineering/explorer/, so a prospective reader is the
first person to meet these numbers.

  cc2   the page drew ONE floor -- the trajectory's fixed point -- in BOTH modes, so
        a reader asking the prospective question was shown the other question's
        equilibrium, always the higher of the two. And the "settled" sentence tested
        the SELECTED mode's nu*, which is the trajectory's equilibrium identity and
        means nothing for the expectation, so on the shipped "leaky fixes" preset the
        page said "risk is still falling ... currently 0.538" while the realised drop
        was 1.816770e-13 and 0.537634 was the equilibrium it had already reached.
  fable the visible "three phases" card printed only the trajectory nu* while the
        DEFAULT mode gates on the expectation nu*, so a reader cross-checking the
        regime sentence against the page's own printed formula got a number that
        formula cannot produce: the sentence says 0.386, the printed formula yields
        0.300.

EVERY TEST HERE EXECUTES THE PAGE. `execute-do-not-grep` is explicit that asserting on
source text proves only that a file describes itself consistently. Three consequences
shape this file:

  1. draw() is run for real behind a minimal DOM stub, so the assertions are about
     what a reader SEES -- the drawn floor label, its value, the rendered sentence --
     not about what the source says it draws.
  2. The stub implements the WHATWG value-sanitisation clamp for <input type=range>,
     because the applyMode() defect only exists in the presence of that clamp.
  3. The card's four printed formulas are EXTRACTED from the markup, mechanically
     transliterated, and EVALUATED against the page's own computed quantities. A test
     that retyped those formulas would prove only that the test agrees with itself,
     which is the defect that shipped five times on 2026-09-28.

NOTHING HERE HARDCODES A CONSTANT THE PAGE OWNS. Slider defaults, preset values, the
per-mode thetas and SETTLED_EPS are all read out of the page.

MEASURED WHEN THIS LANDED, producer `_grid_all_branches` below, executed over 30,324
mode-and-parameter settings: 0 settings reach a regime branch whose printed numbers
contradict its own claim, and all 6 reachable branches are reached -- the 2 branches
added by this fix by 1,610 and 1,522 settings respectively, so neither is an addition
nothing reaches.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import mpmath as mp
import pytest

mp.mp.dps = 30
ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "explorer" / "index.html"

# ---------------------------------------------------------------- the DOM stub
_DOM_PROBE = r"""
const fs = require('fs');
const PAGE = process.argv[2];
const CASES = JSON.parse(process.argv[3]);
const RANGE_IDS = ['pi','p','eta','sigma','nu','theta','pert'];
const html = fs.readFileSync(PAGE,'utf8');
const js = html.split('<script>')[1].split('</script>')[0];

// EXTRACT the markup's own initial slider values. Hardcoding them would reproduce
// the very defect this file guards: a probe re-deriving what the page owns.
const MARKUP = {};
for (const m of html.matchAll(/<input[^>]*type="range"[^>]*>/g)){
  const id = (m[0].match(/id="([^"]+)"/)||[])[1];
  const v  = (m[0].match(/value="([^"]+)"/)||[])[1];
  if (id && v !== undefined) MARKUP[id] = v;
}
for (const k of RANGE_IDS) if (MARKUP[k] === undefined){
  console.error('FATAL: no markup value for slider '+k); process.exit(2); }

function makeDoc(){
  const els = {};
  const mk = (id) => {
    const isRange = RANGE_IDS.includes(id);
    const e = {id, _value:'', textContent:'', innerHTML:'', className:'',
      checked:false, dataset:{}, width:960, height:380,
      _min:null,_max:null,_step:null,_handlers:{}, _text:[],
      addEventListener(t,f){ (this._handlers[t] ||= []).push(f); },
      getBoundingClientRect(){ return {left:0,width:this.width}; },
      getContext(){ return e._ctx; }, _ctx:null};
    // WHATWG HTML value sanitisation: assigning min or max to a range input
    // re-clamps its value ON THE SPOT. Without this the applyMode defect is
    // invisible, so the stub implements it rather than asserting around it.
    const clamp = () => { if(!isRange) return;
      let v = parseFloat(e._value); if (Number.isNaN(v)) return;
      if (e._min !== null && v < e._min) v = e._min;
      if (e._max !== null && v > e._max) v = e._max;
      e._value = String(v); };
    Object.defineProperty(e,'value',{get(){return e._value;},
      set(v){ e._value = String(v); clamp(); }});
    if (isRange){
      Object.defineProperty(e,'min',{get(){return e._min;},set(v){e._min=parseFloat(v);clamp();}});
      Object.defineProperty(e,'max',{get(){return e._max;},set(v){e._max=parseFloat(v);clamp();}});
      Object.defineProperty(e,'step',{get(){return e._step;},set(v){e._step=parseFloat(v);}});
    }
    const noop = ()=>{};
    e._ctx = {clearRect:noop,beginPath:noop,moveTo:noop,lineTo:noop,stroke:noop,
      fill:noop,fillRect:noop,arc:noop,setLineDash:noop,
      strokeStyle:'',fillStyle:'',lineWidth:1,font:'',
      fillText(t){ e._text.push(String(t)); }};
    return e;
  };
  for (const id of [...RANGE_IDS,'v_pi','v_p','v_eta','v_sigma','v_nu','v_theta',
      'v_pert','mode','mirror','ghost','c1','c2','regime','inspectBody',
      'chart1title','gainHeading','thetaLabel','modeWhy']) els[id] = mk(id);
  // 'modeWhy' added 2026-09-28 with the question card. The stub must track the
  // markup: a missing id here silently exercises a DIFFERENT code path from the
  // one a reader gets, which is the class of defect this file exists to catch.
  els.c2.height = 200; els.ghost.checked = true; els.mode.value = 'prospective';
  const buttons = ['healthy','ideal','leaky','futile'].map(p=>{
    const b = mk('btn_'+p); b.dataset.p = p; return b; });
  return {els, buttons, document:{getElementById: id => els[id] || null,
                                  querySelectorAll: () => buttons}};
}

const out = [];
for (const c of CASES){
  const d = makeDoc();
  global.document = d.document;
  for (const k of RANGE_IDS) d.els[k]._value = String(c[k] !== undefined ? c[k] : MARKUP[k]);
  if (c.mode) d.els.mode.value = c.mode;
  new Function(js)();                       // the page's own script, unmodified
  if (c.preset){
    const b = d.buttons.find(b=>b.dataset.p === c.preset);
    if (!b){ console.error('FATAL: no preset '+c.preset); process.exit(2); }
    b._handlers.click.forEach(f=>f());
  }
  if (c.thenTheta !== undefined) d.els.theta.value = c.thenTheta;
  if (c.thenMode){ d.els.mode.value = c.thenMode; d.els.mode._handlers.change.forEach(f=>f()); }
  if (c.clickPass !== undefined){
    // Select a pass for real, through the canvas click handler, so the inspector
    // is populated by the page rather than by the probe.
    const M_l = 52, M_r = 16, N = 60;
    const x = M_l + (d.els.c1.width-M_l-M_r)*c.clickPass/N;
    d.els.c1._handlers.click.forEach(f=>f({clientX:x}));
  }
  // CAPTURE ONLY THE FINAL DRAW: fillText accumulates across redraws, so reading
  // the tail could report a label belonging to an EARLIER parameter set.
  d.els.c1._text.length = 0; d.els.c2._text.length = 0;
  d.els.pi._handlers.input.forEach(f=>f());
  out.push({case:c, regime:d.els.regime.innerHTML, regimeClass:d.els.regime.className,
    c1text:d.els.c1._text.slice(), c2text:d.els.c2._text.slice(),
    inspect:d.els.inspectBody.innerHTML, theta:d.els.theta.value,
    thetaMin:d.els.theta.min, thetaMax:d.els.theta.max,
    sliders:Object.fromEntries(RANGE_IDS.map(k=>[k, d.els[k].value]))});
}
console.log(JSON.stringify(out));
"""

# ------------------------------------------------- the page's own pure functions
_GRID_PROBE = r"""
const fs = require('fs');
const js = fs.readFileSync(process.argv[2],'utf8').split('<script>')[1].split('</script>')[0];
const SRC = [];
for (const re of [/const MODE = \{[\s\S]*?\n\};/, /const SETTLED_EPS = [^;]+;/,
                  /function simulate\(o\)\{[\s\S]*?\n\}/, /function regimeKind\([\s\S]*?\n\}/]){
  const m = js.match(re);
  if (!m){ console.error('FATAL: page no longer exposes '+re); process.exit(2); }
  SRC.push(m[0]);
}
const {MODE, SETTLED_EPS, simulate, regimeKind} = new Function(
  'const N=60, PERT_STEP=22;'+SRC.join('\n')+';return {MODE,SETTLED_EPS,simulate,regimeKind};')();
const REQ = JSON.parse(process.argv[3]);

if (REQ.op === 'floors'){
  const out = [];
  for (const c of REQ.cases){
    const q = c.eta*c.p;
    out.push({case:c, q,
      traj: MODE.retrospective.floor(c,q), exp: MODE.prospective.floor(c,q),
      trajLabel: MODE.retrospective.floorLabel, expLabel: MODE.prospective.floorLabel});
  }
  console.log(JSON.stringify(out)); process.exit(0);
}

if (REQ.op === 'grid'){
  // Executes THE PAGE'S OWN regimeKind. Nothing about the branch conditions is
  // restated here; the counts and the contradiction checks read its return value.
  const TH = {prospective: MODE.prospective.theta.value,
              retrospective: MODE.retrospective.theta.value};
  const g = n => Array.from({length:n},(_,i)=>(i+1)/(n+1));
  const counts = {}; let falseIdentity = 0, falseHarm = 0, total = 0;
  let exI = null, exH = null;
  for (const pi of g(19)) for (const pp of g(19))
    for (const sg of [0.1,0.3,0.5,0.7,0.9,1.0]) for (const nu of [0,0.01,0.05,0.1,0.2,0.3,0.5])
      for (const mn of ['prospective','retrospective']){
        const o = {pi, p:pp, eta:1, sigma:sg, nu, pert:0, theta:TH[mn]};
        const rg = regimeKind(o, simulate(o), mn); total++;
        counts[mn+':'+rg.kind] = (counts[mn+':'+rg.kind]||0)+1;
        // Each branch makes a CLAIM. Check the claim against the numbers the page
        // would print in that branch.
        if (rg.kind === 'settled-at-breakeven' && Math.abs(rg.nuS-nu) >= 0.004){
          falseIdentity++; exI = exI||{o,rg}; }
        if (rg.kind === 'net-harm' && !(nu >= rg.nuS - 1e-12)){ falseHarm++; exH = exH||{o,rg}; }
      }
  console.log(JSON.stringify({total, counts, falseIdentity, falseHarm, exI, exH,
                              settledEps: SETTLED_EPS, theta: TH}));
  process.exit(0);
}

if (REQ.op === 'quantities'){
  const out = [];
  for (const c of REQ.cases){
    const sim = simulate(c); const last = sim.steps[sim.steps.length-1];
    out.push({case:c, q:sim.q, first:sim.steps[0], last});
  }
  console.log(JSON.stringify(out)); process.exit(0);
}
console.error('FATAL: unknown op'); process.exit(2);
"""


def _node() -> str:
    exe = shutil.which("node")
    if not exe:
        pytest.skip("node is not installed; the page's own JS cannot be executed here")
    return exe


def _run(probe_src: str, arg: object, name: str):
    exe = _node()
    probe = ROOT / "bench" / "tests" / name
    probe.write_text(probe_src, encoding="utf-8")
    try:
        r = subprocess.run([exe, str(probe), str(PAGE), json.dumps(arg)],
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, f"probe failed ({r.returncode}): {r.stderr[:600]}"
        return json.loads(r.stdout)
    finally:
        probe.unlink(missing_ok=True)


def run_dom(cases: list[dict]):
    return _run(_DOM_PROBE, cases, "_explorer_dom_probe.js")


def run_pure(req: dict):
    return _run(_GRID_PROBE, req, "_explorer_grid_probe.js")


PAGE_TEXT = PAGE.read_text(encoding="utf-8")


def preset(name: str) -> dict:
    """READ a shipped preset out of the page. Retyping one would let a preset change
    silently while every assertion below still passed."""
    block = re.search(r"const PRESETS = \{[\s\S]*?\n\};", PAGE_TEXT)
    assert block, "the page no longer exposes a PRESETS table"
    row = re.search(rf"{name}\s*:\s*\{{([^}}]*)\}}", block.group(0))
    assert row, f"no preset named {name}"
    o = {}
    for k, v in re.findall(r"(\w+)\s*:\s*([0-9.]+)", row.group(1)):
        o[k] = float(v)
    o.setdefault("eta", 1.0)
    return o


def drawn_floor(row: dict) -> tuple[str, float] | None:
    """What the reader actually sees on the risk chart, read off the canvas calls."""
    for t in row["c1text"]:
        m = re.match(r"-- (.+?)\s+R\* = ([0-9.]+)$", t)
        if m:
            return m.group(1), float(m.group(2))
    return None


def plain(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


# =====================================================================  the maths
class TestEachQuestionHasItsOwnFloor:
    """The page's two floor functions against an INDEPENDENT mpmath derivation taken
    from the recursion itself, not transcribed from the page."""

    CASES = [
        {"pi": .85, "p": .45, "eta": 1, "sigma": .9, "nu": .05, "pert": 0},
        {"pi": .85, "p": .60, "eta": 1, "sigma": .9, "nu": .30, "pert": 0},
        {"pi": .40, "p": .80, "eta": 1, "sigma": .5, "nu": .20, "pert": 0},
        {"pi": .90, "p": .45, "eta": 1, "sigma": .7, "nu": .30, "pert": 0},
    ]

    @staticmethod
    def _mpmath(c: dict) -> tuple[mp.mpf, mp.mpf]:
        q = mp.mpf(str(c["eta"])) * mp.mpf(str(c["p"]))
        s, v = mp.mpf(str(c["sigma"])), mp.mpf(str(c["nu"]))
        R = mp.mpf("0.5")
        # TRAJECTORY floor: iterate the recursion to its fixed point. Derived by
        # ITERATION rather than by substituting a closed form, so agreement with the
        # page's closed form is a real cross-check and not a restatement of it.
        for _ in range(4000):
            R = (s * (R * (1 - q) / (1 - q * R)) + (1 - s) * R) * (1 - v) + v
        traj = R
        # EXPECTATION floor: the R at which E[dR] changes sign, found by bisection on
        # the page's own expectation, again without using a closed form.
        f = lambda r: r * q * s * (1 - v) - v * (1 - r)
        lo, hi = mp.mpf(0), mp.mpf(1)
        for _ in range(400):
            mid = (lo + hi) / 2
            if f(mid) < 0:
                lo = mid
            else:
                hi = mid
        return traj, (lo + hi) / 2

    @pytest.mark.parametrize("case", CASES)
    def test_both_floors_match_an_independent_derivation(self, case):
        row = run_pure({"op": "floors", "cases": [case]})[0]
        traj, exp = self._mpmath(case)
        assert abs(mp.mpf(str(row["traj"])) - traj) < mp.mpf("1e-9"), (
            f"trajectory floor: page {row['traj']} vs iterated {traj}")
        assert abs(mp.mpf(str(row["exp"])) - exp) < mp.mpf("1e-9"), (
            f"expectation floor: page {row['exp']} vs bisected {exp}")

    @pytest.mark.parametrize("case", CASES)
    def test_the_two_floors_are_not_the_same_number(self, case):
        """ANTI-VACUITY. Wiring both modes to one formula would satisfy every other
        test in this class, and that is exactly the defect being fixed."""
        row = run_pure({"op": "floors", "cases": [case]})[0]
        assert row["traj"] > row["exp"], (
            f"{case}: traj {row['traj']} is not above exp {row['exp']}")
        assert row["trajLabel"] != row["expLabel"], "both modes share one floor label"

    def test_the_trajectory_floor_is_never_the_lower_of_the_two(self):
        """SymPy gives traj - exp = nu^2*(1-q)/D with D > 0 on the open cube, so the
        ordering is total. Checked by EXECUTING the page's two floors over a grid."""
        cases = [{"pi": .5, "p": p, "eta": 1, "sigma": s, "nu": v, "pert": 0}
                 for p in (0.05, 0.25, 0.5, 0.75, 0.95)
                 for s in (0.1, 0.4, 0.7, 1.0)
                 for v in (0.01, 0.05, 0.2, 0.5)]
        rows = run_pure({"op": "floors", "cases": cases})
        bad = [r for r in rows if r["exp"] > r["traj"] + 1e-12]
        assert not bad, f"{len(bad)} settings where the expectation floor is higher: {bad[:2]}"
        strict = [r for r in rows if r["traj"] - r["exp"] > 1e-9]
        assert len(strict) == len(rows), (
            f"only {len(strict)} of {len(rows)} floors differ strictly; with nu > 0 and "
            "q < 1 the gap nu^2(1-q)/D is strictly positive everywhere here")


# ==============================================  what the reader actually sees
class TestThePageDrawsTheFloorTheReaderAskedFor:
    def test_the_two_modes_draw_different_floors_on_the_leaky_preset(self):
        """THE DEFECT, EXECUTED. Both modes drew the trajectory floor, so a
        prospective reader saw 0.538 where their own question implies 0.442."""
        rows = run_dom([{"preset": "leaky"},
                        {"preset": "leaky", "thenMode": "retrospective"}])
        prosp, retro = drawn_floor(rows[0]), drawn_floor(rows[1])
        assert prosp and retro, f"no floor drawn: {prosp!r} {retro!r}"
        assert prosp[1] != retro[1], (
            f"both modes drew the SAME floor {prosp[1]} -- the defect is back")
        assert prosp[1] < retro[1], f"prospective {prosp[1]} should be the lower floor"
        assert prosp[0] != retro[0], f"both modes used the label {prosp[0]!r}"

    def test_the_drawn_floor_is_the_selected_modes_own_floor(self):
        """Not merely different: each drawn value must equal THAT mode's floor."""
        p = preset("leaky")
        want = run_pure({"op": "floors", "cases": [{**p, "pert": 0}]})[0]
        rows = run_dom([{"preset": "leaky"},
                        {"preset": "leaky", "thenMode": "retrospective"}])
        assert abs(drawn_floor(rows[0])[1] - want["exp"]) < 5e-4, (
            f"prospective drew {drawn_floor(rows[0])[1]}, its floor is {want['exp']}")
        assert abs(drawn_floor(rows[1])[1] - want["traj"]) < 5e-4, (
            f"retrospective drew {drawn_floor(rows[1])[1]}, its floor is {want['traj']}")


class TestTheRegimeSentenceDescribesTheDrawnLine:
    def test_a_settled_line_is_never_called_still_falling(self):
        """cc2's finding, executed on the shipped preset it was found on."""
        rows = run_dom([{"preset": "leaky"},
                        {"preset": "leaky", "thenMode": "retrospective"}])
        for r in rows:
            txt = plain(r["regime"])
            assert "still falling" not in txt, (
                f"mode {r['case'].get('thenMode','prospective')}: {txt[:200]}")

    def test_the_prospective_sentence_reports_the_realised_drop_and_both_floors(self):
        """Where the 2 questions disagree the page must SAY so, with numbers."""
        txt = plain(run_dom([{"preset": "leaky"}])[0]["regime"])
        assert "settled" in txt, txt[:200]
        assert "not" in txt and "E[ΔR]" in txt, txt[:200]
        assert re.search(r"realised drop is now\s+[0-9.]+e-\d+", txt), txt[:200]

    def test_the_two_modes_do_not_contradict_each_other_on_one_line(self):
        """THE SHARPEST FORM OF THE DEFECT: the identical plotted trajectory was
        called 'still falling' by one mode and 'settled' by the other."""
        rows = run_dom([{"preset": "leaky"},
                        {"preset": "leaky", "thenMode": "retrospective"}])
        a, b = plain(rows[0]["regime"]), plain(rows[1]["regime"])
        assert ("settled" in a) == ("settled" in b), (
            f"one mode says settled and the other does not:\n  {a[:160]}\n  {b[:160]}")

    def test_a_zero_reinjection_run_is_not_told_a_further_pass_buys_something(self):
        """ANTI-REGRESSION on a fault this fix could have introduced. The seat's
        version had no threshold guard, so the shipped 'ideal' preset (nu = 0, which
        settles at R -> 0 with E[dR] -> 0 alongside it) would have been told 'a
        further pass is still expected to buy E[dR] = 0.0000'."""
        txt = plain(run_dom([{"preset": "ideal"}])[0]["regime"])
        assert "not" not in txt.split("settled")[0] or "expected to buy" not in txt, txt[:200]
        assert "0.0000" not in txt, f"announced a gain of 0.0000: {txt[:200]}"

    def test_no_reachable_branch_prints_a_claim_its_own_numbers_contradict(self):
        """THE WHOLE GRID, EXECUTED THROUGH THE PAGE'S OWN regimeKind.

        Widening the settled test from the nu*-identity to 'the drawn line stopped
        moving' made 4,998 settings reach a sentence asserting nu* ~ nu where the
        selected mode's nu* was 0.9995 against nu = 0.200. That is why the settled
        branch is split in two rather than merely loosened."""
        g = run_pure({"op": "grid"})
        assert g["falseIdentity"] == 0, (
            f"{g['falseIdentity']} settings claim the break-even met nu when it did "
            f"not, e.g. {g['exI']}")
        assert g["falseHarm"] == 0, (
            f"{g['falseHarm']} settings claim nu >= nu* when it is not, e.g. {g['exH']}")
        assert g["total"] > 30000, f"only {g['total']} settings executed"

    def test_every_branch_the_fix_added_is_actually_reached(self):
        """`additive-standard`: an addition nothing reaches is not additive. Both new
        branches must be reached by the executed grid, or they are dead prose."""
        counts = run_pure({"op": "grid"})["counts"]
        for kind in ("prospective:settled-expects-more",
                     "prospective:settled-no-breakeven"):
            assert counts.get(kind, 0) > 0, (
                f"branch {kind} is reached by 0 of the executed settings; it is an "
                f"addition no caller reaches. counts={counts}")
        for kind in ("prospective:settled-at-breakeven", "prospective:net-harm",
                     "prospective:falling", "retrospective:settled-at-breakeven"):
            assert counts.get(kind, 0) > 0, f"pre-existing branch {kind} became dead"


# =========================================  the card a reader cross-checks against
class TestTheVisibleCardPrintsBothFormulasAndTheyEvaluateCorrectly:
    """fable's finding. The card is static prose, so `execute-do-not-grep` forbids
    settling this by searching for a string: the FORMULAS ARE EXTRACTED FROM THE
    MARKUP, transliterated mechanically, and EVALUATED against the page's own
    computed quantities. Retyping them here would prove only self-agreement."""

    @staticmethod
    def card_formula(lhs: str) -> str:
        """Pull one 'lhs = rhs' formula out of the phases card and return the rhs as
        evaluable JavaScript. The transliteration is mechanical: strip markup, map
        each symbol to an identifier, then insert the multiplications the printed
        form leaves implicit."""
        card = PAGE_TEXT.split('<div class="card phases"')[1].split("</div>")[0]
        hits = []
        for m in re.finditer(r'<span class="mono">(.*?)</span>', card, re.S):
            txt = re.sub(r"<sub>(.*?)</sub>", r"_\1", m.group(1))
            txt = re.sub(r"<[^>]+>", "", txt).replace("&lt;", "<").replace("&gt;", ">")
            txt = txt.replace("−", "-").replace("·", "*").replace(" ", " ")
            if txt.strip().startswith(lhs + " ="):
                hits.append(txt.split("=", 1)[1].strip())
        # The card ALSO quotes worked numeric values with the same left-hand side,
        # e.g. "nu*_dR = 0.3000". Keep only the algebraic one: a formula has a symbol
        # in it, a worked value does not. Discovered when adding those numbers made
        # this extractor return 2 hits and fail loudly rather than pick one.
        formulas = [h for h in hits if re.search(r"[A-Za-z\u03c3\u03bd]", h)]
        assert len(formulas) == 1, (
            f"expected exactly 1 printed FORMULA for '{lhs}' in the card, got {formulas} "
            f"(all hits: {hits})")
        rhs = formulas[0]
        for sym, name in (("σ", "s"), ("ν", "v"), ("ΔR", "D"), ("θ", "t")):
            rhs = rhs.replace(sym, name)
        assert not re.search(r"[^\x00-\x7f]", rhs), f"unmapped symbol in {rhs!r}"
        # implicit multiplication: letter-letter and letter-( become explicit
        for _ in range(8):
            rhs = re.sub(r"([A-Za-z0-9])\s*([A-Za-z(])", r"\1*\2", rhs)
            rhs = re.sub(r"\)\s*([A-Za-z(])", r")*\1", rhs)
        return rhs

    @staticmethod
    def evaluate(rhs: str, R: float, q: float, s: float, v: float) -> float:
        exe = _node()
        expr = f"const R={R!r},q={q!r},s={s!r},v={v!r};console.log(String({rhs}))"
        r = subprocess.run([exe, "-e", expr], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, f"card formula {rhs!r} is not evaluable: {r.stderr[:300]}"
        return float(r.stdout.strip())

    @pytest.mark.parametrize("lhs,field", [
        ("ν*_ΔR", "nuStar"),      # trajectory break-even
        ("ν*_E", "nuStarExp"),         # expectation break-even -- fable's addition
    ])
    def test_each_printed_break_even_reproduces_the_pages_own_value(self, lhs, field):
        p = {**preset("leaky"), "pert": 0, "theta": 0.02}
        row = run_pure({"op": "quantities", "cases": [p]})[0]
        rhs = self.card_formula(lhs)
        for st in (row["first"], row["last"]):
            got = self.evaluate(rhs, st["R_old"], row["q"], p["sigma"], p["nu"])
            assert abs(got - st[field]) < 1e-9, (
                f"card prints {lhs} = {rhs!r}; at R={st['R_old']} it gives {got} but "
                f"the page computes {field} = {st[field]}. A reader cross-checking the "
                "regime sentence against this formula gets the wrong number.")

    @pytest.mark.parametrize("lhs,which", [("R*_ΔR", "traj"), ("R*_E", "exp")])
    def test_each_printed_floor_reproduces_the_pages_own_floor(self, lhs, which):
        p = {**preset("leaky"), "pert": 0}
        row = run_pure({"op": "floors", "cases": [p]})[0]
        rhs = self.card_formula(lhs)
        got = self.evaluate(rhs, 0.0, row["q"], p["sigma"], p["nu"])
        assert abs(got - row[which]) < 1e-9, (
            f"card prints {lhs} = {rhs!r} -> {got}, page's floor is {row[which]}")

    def test_every_worked_number_the_card_quotes_is_one_the_page_renders(self):
        """The card quotes worked nu* values for the shipped "leaky fixes" preset. Each
        must appear in the inspector the page actually renders for that preset, so the
        prose cannot drift away from the tool it describes.

        THIS ASSERTION ALREADY EARNED ITS PLACE. The first draft of the card quoted
        "nu* ~ 0.386", read off the page BEFORE this fix, when the leaky preset took the
        falling branch. After the fix that preset takes a settled branch, which prints
        no nu* at all, and the inspector renders 0.3857 to 4 places. The quoted number
        was stale the moment the fix landed, and this is what caught it."""
        card = PAGE_TEXT.split('<div class="card phases"')[1].split("</div>")[0]
        quoted = re.findall(r"\u03bd\*<sub>[^<]*</sub> = ([0-9]\.[0-9]{4})", card)
        assert len(quoted) >= 2, (
            f"the card should quote a worked nu* for BOTH questions; found {quoted}")
        shown = plain(run_dom([{"preset": "leaky", "clickPass": 60}])[0]["inspect"])
        for qv in quoted:
            assert qv in shown, (
                f"the card quotes nu* = {qv} for the leaky preset but the page's own "
                f"inspector renders:\n{shown}")


# ===================================================  the threshold the reader chose
class TestSwitchingQuestionKeepsOrDefaultsTheThreshold:
    """Both panel seats found this independently. Assigning min/max to a range input
    re-clamps its value, so reading the reader's theta AFTERWARDS saw the clamp
    boundary and the adopt-the-default branch was unreachable."""

    def test_an_out_of_range_choice_falls_back_to_the_modes_default_not_the_edge(self):
        th_p = float(re.search(
            r"prospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+)", PAGE_TEXT).group(1))
        th_r, mx_r = (float(x) for x in re.search(
            r"retrospective:\s*\{[\s\S]*?theta:\s*\{value:\s*([0-9.]+),\s*min:\s*[0-9.]+,"
            r"\s*max:\s*([0-9.]+)", PAGE_TEXT).groups())
        chosen = (th_p + mx_r) / 2 + (mx_r - th_r) / 2   # legal in prospective, above retro's max
        assert chosen > mx_r, "construct a theta the retrospective mode cannot hold"
        row = run_dom([{"mode": "prospective", "thenTheta": chosen,
                        "thenMode": "retrospective"}])[0]
        got = float(row["theta"])
        assert abs(got - th_r) < 1e-12, (
            f"reader chose theta={chosen} in prospective, switched mode, and landed on "
            f"{got}; the mode's own default is {th_r} and its range edge is {mx_r}. "
            "Landing on the edge means min/max were assigned before the value was read.")

    def test_an_in_range_choice_is_preserved_across_the_switch(self):
        """ANTI-VACUITY: always adopting the default would satisfy the test above."""
        mx_r = float(re.search(
            r"retrospective:\s*\{[\s\S]*?theta:\s*\{value:\s*[0-9.]+,\s*min:\s*[0-9.]+,"
            r"\s*max:\s*([0-9.]+)", PAGE_TEXT).group(1))
        keep = round(mx_r / 2, 3)
        row = run_dom([{"mode": "prospective", "thenTheta": keep,
                        "thenMode": "retrospective"}])[0]
        assert abs(float(row["theta"]) - keep) < 1e-12, (
            f"a theta of {keep} is legal in both modes but became {row['theta']}")


class TestTheInspectorNamesTheQuantityThatDecides:
    """`gainRow` was defined in both MODE entries and read by NOTHING. Wiring it is
    what lets a reader see which quantity the stop marker was computed from."""

    @pytest.mark.parametrize("mode_name,expect_marked", [
        ("prospective", "E[ΔR]"), ("retrospective", "ΔR")])
    def test_the_gated_row_is_marked_in_each_mode(self, mode_name, expect_marked):
        case = {"preset": "leaky", "clickPass": 30}
        if mode_name != "prospective":
            case["thenMode"] = mode_name
        rows = run_dom([case])
        body = rows[0]["inspect"]
        assert "gated on" in body, f"no gated-on marker rendered at all: {plain(body)[:300]}"
        marked = [plain(tr) for tr in re.findall(r"<tr>.*?</tr>", body, re.S)
                  if "gated on" in tr]
        assert len(marked) == 1, f"{len(marked)} rows marked as gated: {marked}"
        assert expect_marked in marked[0], (
            f"mode {mode_name} marked the wrong row: {marked[0]!r}")
