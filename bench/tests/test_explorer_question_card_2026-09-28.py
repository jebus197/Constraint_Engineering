"""The question card must actually switch the question, and explain each one.

FOUNDER, 2026-09-28: *"There is a glitch/run on in the explorer UX in the newly
added 'question' section. This also looks incredibly crude ... Right now anyone
encountering the explorer for the first time will have no idea what they are looking
at, with no explanations provided. Selecting each mode should reveal the explanatory
text for that specific mode."*

WHY THIS FILE EXISTS AT ALL. The card was built, verified by hand in a browser, and
reported as working — and then 2 mutations proved nothing would have noticed if it
broke. Disconnecting the radios so clicking does nothing: **35 passed**. Giving both
modes the identical explanation: **35 passed**. That is the 7th instance in one day
of the same root cause, a change shipped with a test that cannot fail on it.

WHAT IS GUARDED, and it is BEHAVIOUR rather than wording: that a radio actually
drives the mode, that each mode's explanation is present, distinct, and names the
question that mode answers, and that the selector is not clipped by living in a
narrow column. The prose itself is free to change.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "explorer" / "index.html"

#: Executes the page's OWN applyMode + radio listeners against a DOM stub, then
#: reports what a reader would see. It never re-implements either.
_PROBE = r"""
const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const js=html.split('<script>')[1].split('</script>')[0];

const els={}, radios=[];
const mk=(id)=>({id,value:'',min:'',max:'',step:'',textContent:'',innerHTML:'',
  dataset:{},checked:false,className:'',style:{},
  _l:{},addEventListener(t,f){(this._l[t]=this._l[t]||[]).push(f);},
  dispatchEvent(e){(this._l[e.type]||[]).forEach(f=>f.call(this,e));},
  getContext(){return new Proxy({},{get:()=>()=>({})});},width:10,height:10});
for (const id of ['pi','p','eta','sigma','nu','theta','pert','mode','mirror','ghost',
  'v_pi','v_p','v_eta','v_sigma','v_nu','v_theta','v_pert','regime','inspectBody',
  'c1','c2','chart1title','gainHeading','thetaLabel','modeWhy']) els[id]=mk(id);
// slider defaults read from the MARKUP, never invented here
for (const m of html.matchAll(/<input[^>]*id="([A-Za-z0-9_]+)"[^>]*value="([0-9.]+)"/g))
  if (els[m[1]]) els[m[1]].value = m[2];
els.mode.value='prospective';
// the radios, as the markup declares them
for (const m of html.matchAll(/<input type="radio" name="modeR" value="([a-z]+)"([^>]*)>/g)){
  const r=mk('radio_'+m[1]); r.value=m[1]; r.name='modeR';
  r.checked=/checked/.test(m[2]); radios.push(r);
}
global.document={getElementById:(id)=>els[id]||null,
  querySelectorAll:(sel)=>sel.includes('modeR')?radios:[],
  addEventListener(){}};
global.window={addEventListener(){}};
global.Event=class{constructor(t){this.type=t;}};
try{ eval(js); }catch(e){ console.error('EVAL:'+e.message); process.exit(3); }

const snap=()=>({mode:els.mode.value, why:els.modeWhy.innerHTML,
                 heading:els.gainHeading.textContent, theta:els.theta.value});
const out={onLoad:snap(), radios:radios.map(r=>r.value)};
const other=radios.find(r=>r.value!==els.mode.value);
if(other){ radios.forEach(r=>r.checked=(r===other));
           other.dispatchEvent(new Event('change')); out.afterClick=snap(); }
console.log(JSON.stringify(out));
"""


def run_page() -> dict:
    if not shutil.which("node"):
        pytest.skip("node is not installed; the page's own JS cannot be executed")
    probe = ROOT / "bench" / "tests" / "_explorer_card_probe.js"
    probe.write_text(_PROBE, encoding="utf-8")
    try:
        r = subprocess.run(["node", str(probe), str(PAGE)],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, f"probe failed ({r.returncode}): {r.stderr[:400]}"
        return json.loads(r.stdout)
    finally:
        probe.unlink(missing_ok=True)


class TestClickingARadioActuallySwitchesTheQuestion:
    def test_both_choices_are_offered(self):
        got = run_page()
        assert sorted(got["radios"]) == ["prospective", "retrospective"], got["radios"]

    def test_clicking_the_other_choice_changes_the_mode(self):
        """MUTATION THAT PASSED 35/35: the listener body removed, so clicking did
        nothing at all and the page silently ignored the reader."""
        got = run_page()
        assert "afterClick" in got, "no second choice to click"
        assert got["afterClick"]["mode"] != got["onLoad"]["mode"], (
            f"clicking the other radio left the mode at {got['onLoad']['mode']!r} — "
            "the radios are not wired to the question"
        )

    def test_the_switch_carries_the_threshold_and_heading_with_it(self):
        got = run_page()
        assert got["afterClick"]["theta"] != got["onLoad"]["theta"], (
            "theta did not rescale with the question; one mode is being judged at the "
            "other's threshold"
        )
        assert got["afterClick"]["heading"] != got["onLoad"]["heading"]

    def test_it_opens_on_the_prospective_question(self):
        """The founder's ruling: a first-time reader has nothing to look back on."""
        assert run_page()["onLoad"]["mode"] == "prospective"


class TestEachModeExplainsItself:
    def test_an_explanation_is_shown_for_the_opening_mode(self):
        why = run_page()["onLoad"]["why"]
        assert why and len(why) > 80, f"explanation is missing or a stub: {why!r}"

    def test_the_two_explanations_are_different(self):
        """MUTATION THAT PASSED 35/35: both modes given the same text, so the card
        explained nothing while appearing to."""
        got = run_page()
        assert got["onLoad"]["why"] != got["afterClick"]["why"], (
            "both questions show the SAME explanation — selecting a mode reveals "
            "nothing specific to it"
        )

    def test_each_explanation_names_its_own_question(self):
        got = run_page()
        pro = got["onLoad"]["why"].lower()
        retro = got["afterClick"]["why"].lower()
        assert "not run" in pro or "before" in pro, pro[:120]
        assert "already run" in retro or "actually" in retro, retro[:120]


class TestTheCardIsNotBackInTheNarrowColumn:
    """The original fault was structural: a 60-character option inside a
    `flex:1 1 280px` control column, clipped mid-word."""

    def test_the_question_card_sits_outside_the_controls_column(self):
        html = PAGE.read_text(encoding="utf-8")
        controls = html.index('class="card controls"')
        charts = html.index('id="chart1title"')
        card = html.index('class="questionCard"')
        assert controls < card < charts, (
            "the question card is not between the controls block and the first chart; "
            "check it has not drifted back into the narrow column"
        )

    def test_the_choices_are_radios_not_a_clipping_select(self):
        """COUNT THE RADIOS, NOT THE STRING. A first version asserted
        `html.count('name="modeR"') == 2` and failed at 3: the JS selector
        `querySelectorAll('input[name="modeR"]')` contains the same text. Counting a
        substring across code and markup measures neither."""
        html = PAGE.read_text(encoding="utf-8")
        radios = re.findall(r'<input type="radio"[^>]*name="modeR"[^>]*>', html)
        assert len(radios) == 2, f"expected 2 radio inputs, found {len(radios)}"
        assert 'class="srOnly"' in html, (
            "the compatibility <select> must stay hidden-but-present: draw(), "
            "applyMode() and 3 test files read it"
        )
