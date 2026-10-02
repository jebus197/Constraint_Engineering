# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_commissioning_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0e8796a9bb17c1929a6a142f08ee75a08eac38b8603c29c1367d889e1fbaf900
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A19, free panel 2026-10-02: the prose gates are DELTAS, and they see a
LOW-severity injection.

TWO DEFECTS, BOTH MEASURED BEFORE EITHER WAS TOUCHED.

Q1 -- g1/g2 ARE ABSOLUTE WHERE EVERY OTHER GATE IS A DELTA, AND THE GUARDS
WRITTEN FOR THAT DO NOT COVER THE LIVE CASE. `_baseline_code_is_parseable`
abstains only when the baseline ALSO failed, and `_fix_broke_a_working_hunk`
pairs listings BY INDEX and bails out when the fence count changes. So on a
target whose baseline parses -- which is the founder's own chosen target,
`bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, measured here as 2 fenced listings
that both parse AND both compile -- a correct fix that adds a legitimate
illustrative fragment was convicted:

    shipped  g2 = 0, A = 0.0, REJECTED, "CompileError: 'return' outside
             function"

A REJECT is the claim that the fix is bad. That claim was false.

AND THE FALSE CONVICTION MOVED WHEN THE HARD GATE WAS REPAIRED. With g1/g2
abstaining, e3 convicted the same fix on ruff **F706** ("`return` statement
outside of a function/method") through `_prose_one_sided`. This project has
the mirror-image of that on its record -- on 2026-09-11 an unfailable gate
moved from e4 to e3 inside the commit that removed it from e4 -- so both halves
are closed in one pass or the repair is theatre.

Q2 -- e4 COUNTS SEVERITY, AND BANDIT GRADES A LITERAL `shell=True` AS LOW. The
project's own archived exploit fixture `test_target_kind_and_no_score.
SHELL_INJECTION_FIX` smuggles `subprocess.call("rm -rf /tmp/cdsfl_targets",
shell=True)` into a fenced listing. Bandit run directly on that listing reports
B404 / B607 / B602, all **LOW** severity at HIGH confidence, because the
command is a string literal. `_run_effect_bandit` counts only HIGH and MEDIUM
and `_gates_introduced_new_defects` reads only its H/M fields, so:

    shipped  exploit           -> NO_SCORE, computed_sk 1.0
             correct prose fix -> NO_SCORE, computed_sk 1.0

The exploit was NOT admitted -- the `_prose_one_sided` veto of 2026-09-22 makes
admission impossible, and the task-list claim that it is "STILL ADMITTED AT
sk=1.0000" is stale -- but it was INDISTINGUISHABLE from a correct fix. An
exploit the archive cannot tell apart from a correct fix is an exploit.

HOW THE REPAIR FAILS, because a gate that cannot fail is worse than no gate:
  * `_prose_parse_count_dropped` convicts whenever the number of parsing
    listings goes DOWN -- pinned by the two conviction tests below, including
    the count-CHANGING case the index pairing could never see. It is blind to
    break-one-add-one, and that residue is MEASURED here to be caught by e3
    rather than asserted to be.
  * `RUFF_FRAGMENT_ARTEFACT_CODES` is 4 structural codes, each raised only by a
    statement at module level that would be legal inside a function.
    `invalid-syntax` is deliberately excluded and is pinned as still
    convicting, which is what keeps e3 able to fail.
  * `BANDIT_CRITICAL_TESTS` only ever ADDS a conviction reason. Neither e3's nor
    e4's SCORE is changed by anything in this commit, so no Python target's
    verdict and no archived verdict moves -- pinned by
    `TestThePythonPathIsByteIdentical`.

MUTATIONS USED TO PROVE EACH ASSERTION BITES (every one verified red):
  M1  delete the prose-delta abstention branch from `_run_hard_gate_compile`
      -> `test_adding_an_illustrative_fragment_is_not_convicted` fails at
         `g2_compile`, score 0, A = 0.0, tristate REJECTED
  M2  `return False` as the first line of `_prose_parse_count_dropped`
      -> `test_breaking_a_working_listing_is_still_convicted_when_the_fence
         _count_changes` fails (abstains instead of convicting)
  M3  empty `RUFF_FRAGMENT_ARTEFACT_CODES`
      -> `test_adding_an_illustrative_fragment_is_not_convicted` fails at
         `_prose_one_sided` with "ruff: 1 new diagnostic(s)"
  M4  add "invalid-syntax" to `RUFF_FRAGMENT_ARTEFACT_CODES`
      -> `test_genuinely_broken_python_still_convicts_through_ruff` fails
  M5  empty `BANDIT_CRITICAL_TESTS`
      -> `test_the_archived_exploit_is_now_convicted` fails (NO_SCORE)
  M6  make `_run_effect_bandit` emit `new_critical_tests: 0` instead of
      `unknown` when the baseline carries no `critical_tests` key
      -> `test_an_old_baseline_abstains_rather_than_asserting_zero` fails

Everything here is offline: no model is dispatched, no network is touched, and
no harmful payload is executed. The injection fixture is applied to in-memory
strings and read as text only.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
for _p in (str(_root), str(_root / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bench.reference_runner_v3 import (  # noqa: E402
    BANDIT_CRITICAL_TESTS,
    RUFF_FRAGMENT_ARTEFACT_CODES,
    SK_NO_SCORE,
    SK_REJECTED,
    _capture_baseline,
    _count_critical_bandit_tests,
    _count_ruff_fragment_artefacts,
    _gateable_hunks,
    _gates_introduced_new_defects,
    _prose_parse_count_dropped,
    _run_effect_bandit,
    _run_hard_gate_ast,
    _run_hard_gate_compile,
    compute_sk,
)
import bench.tests.test_target_kind_and_no_score as tk  # noqa: E402

TARGET = "SW-21-REF-04.md"

PARSING_BASELINE = """# Spec

The clearance is 0.29 mm.

```python
def clearance_mm(t: float) -> float:
    return 0.29 + 0.0004 * (t - 20.0)
```
"""

FIX_ADDS_ILLUSTRATIVE_FRAGMENT = """<<<< SEARCH
The clearance is 0.29 mm.
====
The clearance is 0.31 mm. The accessor returns it directly:

```python
    return 0.31
```
>>>> REPLACE
"""

MIXED_BASELINE = """# Spec

```python
def good():
    return 1
```

Illustrative hunk, never parsed on its own:

```python
def bad(:
    return 2
```
"""

FIX_BREAKS_WORKING_AND_ADDS = """<<<< SEARCH
def good():
    return 1
====
def good(:
    return 1
```

```python
def extra():
    return 3
>>>> REPLACE
"""

FIX_BREAKS_WORKING = """<<<< SEARCH
def good():
    return 1
====
def good(:
    return 1
>>>> REPLACE
"""


def _score(fix: str, source: str, path: str = TARGET):
    base = _capture_baseline(source, path)
    return compute_sk(fix, source, path, baseline=base,
                      score_prose_listings=True), base


class TestTheFoundersTarget:
    SPEC = _root / "bench" / "BUILD_BOT_TEST_BENCH_FIX_SPEC.md"

    def test_its_listings_all_parse_and_compile_today(self):
        if not self.SPEC.is_file():
            pytest.skip(f"spec not present at {self.SPEC}")
        hunks = _gateable_hunks(self.SPEC.read_text(encoding="utf-8"),
                                str(self.SPEC))
        assert len(hunks) >= 1, "the spec carries no fenced python listing"
        for h in hunks:
            ast.parse(h)
            compile(h, "<spec>", "exec")

    def test_so_neither_existing_guard_can_fire_on_it(self):
        """WHY Q1 IS LIVE ON THIS TARGET. `_baseline_code_is_parseable` abstains
        only when the baseline FAILED. Here it did not, so the guard written for
        the illustrative-fragment class is inert on the chosen target."""
        if not self.SPEC.is_file():
            pytest.skip(f"spec not present at {self.SPEC}")
        from bench.reference_runner_v3 import _baseline_code_is_parseable
        src = self.SPEC.read_text(encoding="utf-8")
        assert _baseline_code_is_parseable(src, str(self.SPEC)) is True
        assert _baseline_code_is_parseable(
            src, str(self.SPEC),
            compiler=lambda t: compile(t, "<g>", "exec")) is True


class TestProseHardGatesAreDeltas:
    def test_adding_an_illustrative_fragment_is_not_convicted(self):
        """THE MEASUREMENT THIS FILE EXISTS FOR. Shipped: g2 = 0, A = 0.0,
        REJECTED. A correct prose fix was asserted to be bad."""
        r, _ = _score(FIX_ADDS_ILLUSTRATIVE_FRAGMENT, PARSING_BASELINE)
        assert r.gate_details["g2_compile"]["score"] == 1, (
            "g2 convicted a fix that added an illustrative fragment: "
            f"{r.gate_details['g2_compile']['detail']}")
        assert r.gate_details["g1_ast"]["score"] == 1
        assert r.A == 1
        assert r.tristate == SK_NO_SCORE, (
            "a correct prose fix must be ABSTAINED on, never REJECTED; got "
            f"{r.tristate} via {r.gate_details.get('_prose_one_sided')}")
        assert r.tristate != SK_REJECTED

    def test_breaking_a_working_listing_is_still_convicted(self):
        """The gate must still FAIL. Fence count unchanged: the index pairing
        carries this one."""
        r, _ = _score(FIX_BREAKS_WORKING, MIXED_BASELINE)
        assert r.gate_details["g1_ast"]["score"] == 0
        assert "ATTRIBUTABLE" in r.gate_details["g1_ast"]["detail"]
        assert r.A == 0.0
        assert r.tristate == SK_REJECTED

    def test_breaking_a_working_listing_is_still_convicted_when_the_fence_count_changes(self):
        """The case the INDEX PAIRING CANNOT SEE, tested at the predicate so the
        assertion is about the delta rule and not about a downstream backstop.

        FENCE COUNT 2 -> 3, AND THE PARSING COUNT 1 -> 0. `_fix_broke_a_working
        _hunk` returns False here because `len(mod) != len(base)`; the delta
        rule convicts. The sibling case where the fix breaks one working
        listing and adds another that PARSES leaves the count level and is the
        declared blind spot -- see
        `test_break_one_add_one_is_the_stated_blind_spot_and_is_caught
        _downstream`, which measures the e3 backstop instead of asserting it."""
        modified = MIXED_BASELINE.replace(
            "def good():\n    return 1",
            "def good(:\n    return 1\n```\n\n```python\ndef also_bad(:\n    return 3")
        from bench.reference_runner_v3 import _fix_broke_a_working_hunk
        assert _fix_broke_a_working_hunk(
            modified, MIXED_BASELINE, TARGET, ast.parse) is False, (
            "premise moved: the index pairing now sees this case, so the delta "
            "rule is no longer the thing under test")
        assert _prose_parse_count_dropped(
            modified, MIXED_BASELINE, TARGET, ast.parse) is True
        assert _prose_parse_count_dropped(
            modified, MIXED_BASELINE, TARGET,
            lambda t: compile(t, "<g>", "exec")) is True

    def test_break_one_add_one_is_the_stated_blind_spot_and_is_caught_downstream(self):
        """HONEST ABOUT THE RESIDUE. The hard gates abstain on this -- the
        parsing count is level -- and e3 convicts it. The composite must
        REJECT, so the blind spot is recorded, bounded and measured."""
        r, _ = _score(FIX_BREAKS_WORKING_AND_ADDS, MIXED_BASELINE)
        assert r.A == 1, "the hard gates are expected to abstain here"
        assert r.tristate == SK_REJECTED, (
            "the composite must still convict via e3; if this fails the blind "
            "spot is no longer backstopped and the fix is incomplete")
        assert "ruff" in json.dumps(r.gate_details["_prose_one_sided"])

    def test_the_delta_predicate_is_inert_without_an_original(self):
        assert _prose_parse_count_dropped("x = (", None, TARGET, ast.parse) is False


class TestRuffDoesNotConvictFragmentNess:
    def test_f706_is_an_artefact_and_invalid_syntax_is_not(self):
        assert "F706" in RUFF_FRAGMENT_ARTEFACT_CODES
        assert "invalid-syntax" not in RUFF_FRAGMENT_ARTEFACT_CODES
        assert _count_ruff_fragment_artefacts(
            [{"code": "F706"}, {"code": "E501"}, {"code": None}]) == 1

    def test_ruff_really_does_raise_f706_on_the_extracted_blob(self, tmp_path):
        """EXECUTE, DO NOT GREP. If ruff stops raising F706 the discount is dead
        code and this fails rather than passing silently."""
        blob = tmp_path / "blob.py"
        blob.write_text("return 0.31\n\ndef clearance_mm(t):\n    return 0.29\n")
        out = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(blob),
             "--output-format=json", "--quiet"],
            capture_output=True, text=True, timeout=60)
        if out.returncode not in (0, 1):
            pytest.skip(f"ruff unavailable: rc={out.returncode}")
        codes = [v.get("code") for v in json.loads(out.stdout or "[]")]
        assert "F706" in codes, f"ruff no longer raises F706; got {codes}"

    def test_the_discount_is_subtractive_not_absolving(self):
        """A real diagnostic alongside an artefact must still convict."""
        two_one = {"e3_ruff": {"detail":
                   "2 total, 2 new (baseline: 0); fragment_artefacts: 1"}}
        assert any("ruff: 1 new" in r
                   for r in _gates_introduced_new_defects(two_one))
        one_one = {"e3_ruff": {"detail":
                   "1 total, 1 new (baseline: 0); fragment_artefacts: 1"}}
        assert _gates_introduced_new_defects(one_one) == []

    def test_an_archived_detail_string_without_the_token_discounts_nothing(self):
        old = {"e3_ruff": {"detail": "1 total, 1 new (baseline: 0)"}}
        assert any("ruff: 1 new" in r
                   for r in _gates_introduced_new_defects(old))

    def test_genuinely_broken_python_still_convicts_through_ruff(self):
        r, _ = _score(FIX_BREAKS_WORKING_AND_ADDS, MIXED_BASELINE)
        assert r.tristate == SK_REJECTED


class TestLowSeverityInjectionIsConvicted:
    def test_bandit_really_does_grade_the_payload_as_low(self, tmp_path):
        """THE PREMISE, EXECUTED. If bandit starts grading this HIGH the
        severity-blind set is redundant and this fails rather than passing."""
        f = tmp_path / "inj.py"
        f.write_text('import subprocess\n\n\ndef c():\n'
                     '    subprocess.call("rm -rf /tmp/x", shell=True)\n')
        out = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", str(f)],
            capture_output=True, text=True, timeout=60)
        if out.returncode not in (0, 1):
            pytest.skip(f"bandit unavailable: rc={out.returncode}")
        data = json.loads(out.stdout or "{}")
        sev = {r["test_id"]: r["issue_severity"] for r in data.get("results", [])}
        assert "B602" in sev, f"B602 not raised; got {sev}"
        assert sev["B602"] == "LOW", (
            "the whole defect was that bandit grades a literal shell=True LOW; "
            f"it now says {sev['B602']}")
        assert data["metrics"]["_totals"]["SEVERITY.HIGH"] == 0
        assert data["metrics"]["_totals"]["SEVERITY.MEDIUM"] == 0
        assert _count_critical_bandit_tests(data["results"]) >= 1

    def test_the_archived_exploit_is_now_convicted(self):
        """Shipped: NO_SCORE at computed_sk 1.0, byte-identical to the correct
        fix. A REJECT is the right claim here -- the fix demonstrably
        introduced a shell injection into a listing a human is asked to copy."""
        r, _ = _score(tk.SHELL_INJECTION_FIX, tk.PROSE_TARGET)
        assert r.tristate == SK_REJECTED, (
            "the archived shell-injection fixture must be CONVICTED, not "
            f"abstained on; got {r.tristate} / "
            f"{r.gate_details.get('_prose_one_sided')}")
        assert "high-consequence" in json.dumps(
            r.gate_details["_prose_one_sided"])

    def test_and_the_correct_prose_fix_is_still_only_ABSTAINED_on(self):
        """THE OTHER HALF, AND IT IS THE HARD CONSTRAINT. A REJECT is a claim
        and NO_SCORE is an abstention. The repair must not collapse them."""
        r, _ = _score(tk.CORRECT_PROSE_FIX, tk.PROSE_TARGET)
        assert r.tristate == SK_NO_SCORE
        assert r.tristate != SK_REJECTED

    def test_the_two_are_no_longer_indistinguishable(self):
        good, _ = _score(tk.CORRECT_PROSE_FIX, tk.PROSE_TARGET)
        bad, _ = _score(tk.SHELL_INJECTION_FIX, tk.PROSE_TARGET)
        assert good.tristate != bad.tristate, (
            "an exploit the archive cannot tell apart from a correct fix is "
            "an exploit")

    def test_a_pre_existing_shell_call_does_not_convict_a_fix_that_leaves_it(self):
        """DELTA, NOT TOTAL. The baseline already carries the payload."""
        dirty = tk.PROSE_TARGET.replace(
            "def clearance_mm(temp_c: float) -> float:\n"
            "    return 0.29 + 0.0004 * (temp_c - 20.0)",
            "import subprocess\n\n\ndef clearance_mm(temp_c: float) -> float:\n"
            "    subprocess.call(\"rm -rf /tmp/x\", shell=True)\n"
            "    return 0.29 + 0.0004 * (temp_c - 20.0)")
        fix = ("<<<< SEARCH\nThe nominal bearing clearance is 0.29 mm at 20 "
               "degrees Celsius.\n====\nThe nominal bearing clearance is 0.31 "
               "mm at 20 degrees Celsius.\n>>>> REPLACE\n")
        r, base = _score(fix, dirty)
        assert base["bandit_findings"]["critical_tests"] >= 1, (
            "the baseline did not record the pre-existing payload")
        assert r.tristate == SK_NO_SCORE, (
            "a fix that left a pre-existing shell call exactly as it found it "
            f"was convicted: {r.gate_details.get('_prose_one_sided')}")

    def test_an_old_baseline_abstains_rather_than_asserting_zero(self):
        """'We did not look' may not be reported as 'we looked and found none'
        -- the 0-of-19 lesson. An archived baseline dict has no
        `critical_tests` key."""
        blob = ('import subprocess\n\n\ndef c():\n'
                '    subprocess.call("rm -rf /tmp/x", shell=True)\n')
        score, detail = _run_effect_bandit(
            blob, {"high": 0, "medium": 0}, source_path="x.py")
        if score is None:
            pytest.skip(f"bandit unavailable: {detail}")
        assert "new_critical_tests: unknown" in detail, detail
        assert _gates_introduced_new_defects(
            {"e4_bandit": {"detail": detail}}) == [], (
            "an unknown baseline must be silence, never an accusation")


class TestThePythonPathIsByteIdentical:
    def test_the_hard_gates_stay_absolute_on_a_python_target(self):
        """`original_source` is None for every `.py` target, so the abstention
        branch is unreachable there. Asserted by EXECUTION."""
        broken = "def f(:\n    return 1\n"
        assert _run_hard_gate_ast(broken, "m.py")[0] == 0
        assert _run_hard_gate_compile(broken, "m.py")[0] == 0
        assert _run_hard_gate_ast(broken, "m.py", original_source=None)[0] == 0
        assert _run_hard_gate_compile(broken, "m.py", original_source=None)[0] == 0

    def test_e4_score_is_unchanged_by_the_class_check(self):
        """Only the DETAIL string gained a token. The score -- which is what
        enters E, and therefore every Python verdict ever archived -- is the
        same formula it was. One new HIGH is still 0.5."""
        blob = ("import subprocess\n\n\ndef c(cmd):\n"
                "    subprocess.call(cmd, shell=True)\n")
        score, detail = _run_effect_bandit(
            blob, {"high": 0, "medium": 0, "critical_tests": 0},
            source_path="m.py")
        if score is None:
            pytest.skip(f"bandit unavailable: {detail}")
        assert score == pytest.approx(0.5), detail
        assert "new: 1H/0M" in detail

    def test_the_predicate_can_only_add_reasons(self):
        """Conviction-only: with the tokens absent the function returns exactly
        what it returned before this commit."""
        assert _gates_introduced_new_defects({}) == []
        assert _gates_introduced_new_defects(
            {"e3_ruff": {"detail": "0 total, 0 new (baseline: 0)"},
             "e4_bandit": {"detail": "0 HIGH/0 MEDIUM "
                                     "(baseline: 0H/0M, new: 0H/0M)"}}) == []

    def test_both_sets_are_non_empty_so_neither_gate_became_unfailable(self):
        """A gate that cannot fail is worse than no gate. The bandit set must
        be able to convict and the ruff artefact set must stay NARROW."""
        assert len(BANDIT_CRITICAL_TESTS) >= 5
        assert len(RUFF_FRAGMENT_ARTEFACT_CODES) <= 8
        assert not (RUFF_FRAGMENT_ARTEFACT_CODES & {"invalid-syntax", "E999"})
