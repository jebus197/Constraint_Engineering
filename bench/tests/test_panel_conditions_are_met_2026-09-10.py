"""Section P's conditions must be MEASURED, not asserted, and they now are.

The founder's ruling, 2026-09-09, verbatim: "In all cases and with all fixes
always check them with Fable and CC2 in full CDSFL panel review format (so not
just some simple open ended prompt), they must use whatever aspects of the
harness are currently working, including our mathematical model and all relevant
mechanics in the formation of their answers/fixes, as should you."

P1, P3, P4 and P5 sat at PROPOSED with no measurement of whether the rounds
actually satisfied them. These tests drive
`scripts/panel_condition_compliance_2026-09-10.py`, which reads the archived seat
records -- the tool logs the dispatcher writes, and the files a seat left in the
sandbox -- rather than reading what a seat said about itself.

P4 IS THE ONE THAT MATTERS AND IT FAILED FOR A HARNESS REASON. A seat can
describe a fix at any length. Only a file it leaves inside the sandbox repository
tree is a delivered fix, because `teardown` destroys everything else. Rounds 5
and 6 returned 0 source files while both seats reported writing and running real
code. Round 7 changed the brief and returned a patch.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "panel_condition_compliance_2026-09-10.py"
#: Rounds run under the section P ruling.
UNDER_P = "2026-09-"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("panel_compliance", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _replies():
    out = []
    for f in sorted((ROOT / "bench" / "logs").glob("panel_*/*.json")):
        if f.name.endswith((".tools.json", "canonical_touched.json")):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if isinstance(d, dict) and "route" in d:
            out.append((f.parent.name, d))
    return out


class TestTheScriptRuns:
    def test_it_exits_zero(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, f"{r.stdout[-1200:]}\n{r.stderr[-1200:]}"

    def test_cache_artefacts_are_not_counted_as_delivered_fixes(self, mod):
        """The distinction P4 turns on. A `.pyc` is not a repair."""
        for junk in ("bench/__pycache__/x.cpython-313.pyc", ".pytest_cache/v/cache/nodeids",
                     ".mypy_cache/3.13/cache.db", ".ruff_cache/0.15.9/123"):
            assert mod.CACHE.search(junk), f"{junk} would be counted as a delivered fix"
        for real in ("scripts/panel_brief_validate.py", "bench/tests/test_x.py"):
            assert not mod.CACHE.search(real), f"{real} would be discarded as junk"


class TestP1NoPaidSeatWasEverDispatchedUnderTheRuling:
    def test_zero_paid_replies_in_any_round_under_section_p(self):
        paid = [(rnd, d["model"]) for rnd, d in _replies()
                if UNDER_P in rnd and d.get("route") != "claude_cli"]
        assert paid == [], f"a paid seat was dispatched under the ruling: {paid}"

    def test_the_rounds_under_the_ruling_exist_at_all(self):
        """Guards against the above passing vacuously on an empty set."""
        n = len([1 for rnd, _ in _replies() if UNDER_P in rnd])
        assert n >= 10, f"only {n} seat replies under the ruling; too few to conclude from"


class TestP3SeatsUsedTheHarness:
    def test_every_reply_under_the_ruling_recorded_a_tool_call(self):
        silent = [(rnd, d["model"]) for rnd, d in _replies()
                  if UNDER_P in rnd and not int(d.get("n_tool_calls") or 0)]
        assert silent == [], (
            f"a seat returned prose with 0 recorded tool calls: {silent}. "
            f"P3 requires the harness be USED, not discussed")

    def test_the_condition_changed_behaviour_rather_than_describing_it(self):
        """If every round had always been tool-enabled, P3 would prove nothing."""
        old = [d for rnd, d in _replies() if UNDER_P not in rnd]
        silent_old = sum(1 for d in old if not int(d.get("n_tool_calls") or 0))
        assert silent_old > 0, (
            "no historical reply had 0 tool calls, so P3's measurement has no "
            "contrast and this test cannot show the ruling did anything")


#: A reply preserves disagreement if it carries a section ABOUT disagreeing --
#: not if it contains one particular phrase.
#:
#: BROKENED BY MY OWN BRIEF, 2026-09-10. This matched `strongest[_ ]disagreement`
#: only, the wording of the round-4 output shape. The round-8 brief asked for the
#: same field as "WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1", both seats
#: supplied it in full, and the guard reported both as MISSES. A guard keyed to a
#: literal phrase, checking a requirement that each brief states in its own
#: words, is the substring-versus-token defect wearing a different hat -- the same
#: shape that has now cost this project 4 separate findings.
#:
#: The requirement is a SECTION about disagreement, so that is what is matched.
DISAGREEMENT_RE = re.compile(
    r"strongest[_ ]disagreement"
    r"|where\s+i\s+disagree"
    r"|(?:^|\n)\s*#{0,4}\s*\**\s*disagreement\b"
    r"|i\s+disagree\s+with",
    re.I)


class TestP5DisagreementIsPreserved:
    def test_most_replies_under_the_ruling_carry_their_own_disagreement(self):
        under = [(rnd, d) for rnd, d in _replies() if UNDER_P in rnd]
        got = [(rnd, d["model"]) for rnd, d in under
               if DISAGREEMENT_RE.search(d.get("response", ""))]
        assert len(got) >= len(under) - 2, (
            f"only {len(got)} of {len(under)} replies preserved a disagreement; "
            f"the known 2 misses are panel_roster_fix_2026-09-09, dispatched "
            f"before the field was in the brief")

    def test_the_misses_are_the_ones_we_think_they_are(self):
        under = [(rnd, d) for rnd, d in _replies() if UNDER_P in rnd]
        missing = {rnd for rnd, d in under
                   if not DISAGREEMENT_RE.search(d.get("response", ""))}
        assert missing <= {"panel_roster_fix_2026-09-09"}, (
            f"a round other than the known first one lost its disagreement: {missing}")


class TestP4AFixMustArriveAsAFile:
    def test_round_seven_delivered_source_files(self, mod):
        d = ROOT / "bench" / "logs" / "panel_round7_2026-09-10"
        if not d.is_dir():
            pytest.skip("round 7 not present in this clone")
        src = mod.source_files(d)
        assert src, "round 7 delivered no source files, so the delivery rule failed"
        assert any(x.startswith("scripts/") or x.startswith("bench/tests/") for x in src), (
            f"round 7 left files but none is code or a test: {src}")

    def test_the_delivery_rule_is_in_the_brief_that_produced_it(self):
        """An addition nothing reaches is not additive: the rule must be WRITTEN."""
        b = ROOT / "bench" / "logs" / "panel_round7_2026-09-10" / "BRIEF.md"
        if not b.is_file():
            pytest.skip("round 7 brief not present in this clone")
        t = b.read_text(encoding="utf-8")
        assert "not delivered either" in t and "sandbox repository tree" in t, (
            "the delivery rule is absent from the brief, so a later round would "
            "revert to returning prose")

    def test_rounds_five_and_six_are_the_contrast(self, mod):
        """Without the earlier failure this proves nothing about the rule."""
        empties = [d.name for d in (ROOT / "bench" / "logs").glob("panel_round[56]_2026-09-10")
                   if d.is_dir() and not mod.source_files(d)]
        assert len(empties) == 2, (
            f"rounds 5 and 6 were expected to have delivered 0 source files, "
            f"which is what makes round 7 evidence that the rule worked: {empties}")
