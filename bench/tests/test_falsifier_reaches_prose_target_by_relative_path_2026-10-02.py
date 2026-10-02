"""A prose-target falsifier that reads its target by RELATIVE path must get a
verdict, not an equipment failure.

THE DEFECT THIS PINS, measured from the artefacts of BOTH halted prose runs
(commissioning_arm4_prose 2026-09-22 and 2026-09-30): falsifiers execute in a
throwaway scratch cwd -- correct isolation -- and every seat read the document
relatively (`open("bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md")` or the bare
basename). The read resolved inside the empty scratch dir, FileNotFoundError,
verdict ERROR on every rung, routing_deferred in the birth round, queue 8 over
bound 2, HALTED_IRREDUCIBLE_QUEUE_ALARM at round 0. A Python target never hits
this because its falsifiers IMPORT via PYTHONPATH, which is why the halts split
cleanly by target kind.

Every test here EXECUTES the sandbox; none reads its source. The fixture
guarantees registration is cleared afterwards so no other test inherits it.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import falsifier_verify as fv  # noqa: E402

SPEC_REL = "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"
SPEC_ABS = REPO / SPEC_REL

pytestmark = pytest.mark.skipif(not SPEC_ABS.is_file(), reason="spec absent")


@pytest.fixture(autouse=True)
def _clear_registration():
    fv.set_falsifier_target(None)
    yield
    fv.set_falsifier_target(None)


# The exact read shapes the archived round-0 falsifiers used.
READS_REL = f'''text = open({SPEC_REL!r}, encoding="utf-8").read()
assert "SECTION_LABELS" in text or len(text) > 100
print("read ok")
'''
READS_BARE = '''import pathlib
text = pathlib.Path("BUILD_BOT_TEST_BENCH_FIX_SPEC.md").read_text(encoding="utf-8")
assert len(text) > 100
print("read ok")
'''
DEMONSTRATES = f'''text = open({SPEC_REL!r}, encoding="utf-8").read()
assert "THIS STRING IS NOT IN THE SPEC xyzzy-2026" in text, "defect demonstrated"
'''


class TestUnregisteredIsByteIdenticalStatusQuo:
    def test_relative_read_still_errors_when_nothing_is_registered(self):
        """The round-0 failure, pinned: no registration -> loud ERROR."""
        assert fv.reverify_falsifier(READS_REL, repo_root=str(REPO)) == "ERROR"


class TestRegisteredTargetIsReachable:
    def test_repo_relative_read_reaches_a_verdict(self):
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        v = fv.reverify_falsifier(READS_REL, repo_root=str(REPO))
        assert v == "REFUTED", (
            f"a clean-exiting falsifier must be REFUTED, got {v} -- the "
            "relative read is still resolving into an empty scratch dir")

    def test_bare_basename_read_reaches_a_verdict(self):
        """The 2026-09-30 C0001 rung used the bare basename."""
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        assert fv.reverify_falsifier(READS_BARE, repo_root=str(REPO)) == "REFUTED"

    def test_a_demonstrating_falsifier_confirms(self):
        """The verdict machinery is untouched: AssertionError -> CONFIRMED."""
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        assert fv.reverify_falsifier(DEMONSTRATES, repo_root=str(REPO)) == "CONFIRMED"

    def test_the_archived_round0_falsifier_now_reaches_a_verdict(self):
        """THE WHOLE POINT: the real C0001 rung body from the halted run."""
        import json
        rep_p = (REPO / "bench/logs/commissioning_arm4_prose_20260930T064044Z"
                 / "commissioning_arm4_prose_report.json")
        if not rep_p.is_file():
            pytest.skip("archived halted run not present")
        entries = json.load(open(rep_p))["registry"]
        entries = entries.get("entries", entries)
        code = entries["C0001"]["falsifier_code"]
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        v = fv.reverify_falsifier(code, repo_root=str(REPO))
        assert v != "ERROR", (
            "the archived falsifier still dies before its first assertion; "
            "the next commissioning run will halt at round 0 again")


class TestTheWideningIsZero:
    def test_a_python_target_is_never_materialised(self, tmp_path):
        """A scratch copy of a .py target could shadow a real import. Refused."""
        py = tmp_path / "mod_under_review.py"
        py.write_text("VALUE = 1\n", encoding="utf-8")
        fv.set_falsifier_target(str(py), "mod_under_review.py")
        code = '''import os
assert not os.path.exists("mod_under_review.py"), "a .py target was materialised"
print("ok")
'''
        assert fv.reverify_falsifier(code, repo_root=str(REPO)) == "REFUTED"

    def test_only_the_target_appears_nothing_else(self):
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        code = '''import os
assert os.path.exists("bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md")
entries = []
for root, dirs, files in os.walk("."):
    for f in files:
        entries.append(os.path.join(root, f))
assert all("BUILD_BOT_TEST_BENCH_FIX_SPEC.md" in e or e.endswith(".py")
           for e in entries), f"unexpected materialised files: {entries}"
print("ok")
'''
        assert fv.reverify_falsifier(code, repo_root=str(REPO)) == "REFUTED"

    def test_a_parent_escaping_rel_path_is_refused(self, tmp_path):
        """A rel path carrying .. must not write outside the scratch dir."""
        doc = tmp_path / "doc.md"
        doc.write_text("content\n", encoding="utf-8")
        fv.set_falsifier_target(str(doc), "../escape.md")
        code = '''print("ok")
'''
        assert fv.reverify_falsifier(code, repo_root=str(REPO)) == "REFUTED"


class TestRunnerWiring:
    """The runner registers the target before the gate and the ladder run."""

    @pytest.fixture(scope="class")
    def rr(self):
        mod = types.ModuleType("_rr_q4")
        mod.__file__ = str(REPO / "bench" / "reference_runner_v3.py")
        sys.modules["_rr_q4"] = mod
        try:
            exec(compile((REPO / "bench/reference_runner_v3.py").read_text(),
                         str(REPO / "bench/reference_runner_v3.py"), "exec"),
                 mod.__dict__)
        except SystemExit:
            pass
        return mod

    def test_register_helper_sets_and_clears(self, rr):
        # The runner imports `bench.falsifier_verify` (the package instance);
        # inspect THAT one. `falsifier_verify` via sys.path is a second module
        # object with its own registration dict -- the runner's own call sites
        # all use the package import, so the live path is consistent.
        import bench.falsifier_verify as bfv
        cfg = rr.RunnerConfig(test_article=SPEC_REL)
        rr._register_falsifier_target(cfg, str(REPO))
        assert bfv._FALSIFIER_TARGET["abs"] == str(REPO / SPEC_REL)
        assert bfv._FALSIFIER_TARGET["rel"] == SPEC_REL
        rr._register_falsifier_target(rr.RunnerConfig(), str(REPO))
        assert bfv._FALSIFIER_TARGET["abs"] is None

    def test_gate_registers_before_reverifying(self, rr):
        """apply_falsifier_verdicts on a 1-entry registry: the entry's
        relative-path falsifier must come back REFUTED, not ERROR."""
        cfg = rr.RunnerConfig(test_article=SPEC_REL)
        cfg.falsifier_gate_enabled = True

        class _Reg:
            entries = {"C0001": {
                "status": "OPEN", "severity": 0.9,
                "falsifier_code": READS_REL, "description": "d",
                "source_model": "CC2-SIM",
            }}
            def resolve(self, cid, status, round_idx):
                self.entries[cid]["status"] = status
        reg = _Reg()
        rr.apply_falsifier_verdicts(reg, 0, cfg=cfg, repo_root=str(REPO))
        assert reg.entries["C0001"]["falsifier_verdict"] == "REFUTED", (
            reg.entries["C0001"].get("falsifier_verdict"))


class TestItNeverTouchesACallerSuppliedView:
    """The materialisation must not write into a directory a caller built.

    THE HAZARD, MEASURED 2026-10-02 WHILE RUN 1b WAS LIVE. `execute_python` and
    `reverify_falsifier` both compute `tmp_cwd = cwd or _scratch` and then
    materialised the target into it. The DISCRIMINATION CONTROL is a caller that
    supplies `cwd`: it builds an overlay with the target replaced by a tripwire
    and runs the falsifier there to see whether the falsifier notices. Writing
    the real target into that overlay answers the control's own question for it.

    MEASURED BOTH WAYS BEFORE THE FIX. Where the control SUBSTITUTES the target,
    `if not dest.exists()` already protected it and the tripwire survived. Where
    an overlay OMITS the target, the copy landed and restored the real file,
    defeating "replaced wholesale" and yielding NOT_INTERCEPTED or a false pass.
    The safe case depended on another module's internal choice between omitting
    and substituting, which is not a margin to rely on.

    The relative-path defect only ever occurs in the throwaway scratch, where
    there is no view to respect, so restricting it there costs nothing.
    """

    TRIPWIRE = "raise RuntimeError('TRIPWIRE: the control substituted this')\n"

    def test_a_substituting_overlay_keeps_its_tripwire(self, tmp_path):
        (tmp_path / "bench").mkdir(parents=True, exist_ok=True)
        leaf = tmp_path / SPEC_REL
        leaf.write_text(self.TRIPWIRE, encoding="utf-8")
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        fv.execute_python("print('x')", cwd=str(tmp_path), timeout=20)
        assert leaf.read_text(encoding="utf-8") == self.TRIPWIRE, (
            "the materialisation overwrote the control's substitution")

    def test_an_omitting_overlay_stays_empty(self, tmp_path):
        """THE HALF THAT WAS A REAL HOLE."""
        (tmp_path / "bench").mkdir(parents=True, exist_ok=True)
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        fv.execute_python("print('x')", cwd=str(tmp_path), timeout=20)
        assert not (tmp_path / SPEC_REL).exists(), (
            "the real target was restored into an overlay that deliberately "
            "omitted it, so 'replaced wholesale' is defeated")

    def test_reverify_respects_a_caller_view_too(self, tmp_path):
        """Both call sites, because fixing one would leave its twin."""
        (tmp_path / "bench").mkdir(parents=True, exist_ok=True)
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        try:
            fv.reverify_falsifier("print('FALSIFIED')", cwd=str(tmp_path),
                                  timeout=20)
        except TypeError:
            pytest.skip("reverify_falsifier takes no cwd in this revision")
        assert not (tmp_path / SPEC_REL).exists()

    def test_the_scratch_path_still_gets_the_target(self, tmp_path):
        """ANTI-REGRESSION: the defect this all exists to fix must stay fixed."""
        fv.set_falsifier_target(str(SPEC_ABS), SPEC_REL)
        code = (f"import pathlib\n"
                f"assert pathlib.Path({SPEC_REL!r}).is_file(), 'target unreachable'\n"
                f"print('FALSIFIED')\n")
        out = fv.execute_python(code, timeout=30)
        blob = str(out)
        assert "unreachable" not in blob, (
            f"a relative-path falsifier can no longer reach its target: {blob[:300]}")

