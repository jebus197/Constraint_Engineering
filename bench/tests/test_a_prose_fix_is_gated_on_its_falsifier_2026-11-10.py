"""A prose target is gated on the finding's OWN falsifier, not refused out of hand.

HIS RULINGS, 2026-11-10, both verbatim.

B22: fold-back happens at the end of an experimental run, after dual
orchestrator and HIL review, and that "applies to all experiments. Not just a
prose target."

B88: the verification set "will come from which ever STEM topic area under
discussion and the tools/falsifiers/B-Cell machinery attached to that STEM
topic", because a researcher submitting a STEM paper "will almost certainly
have ... included both prose and calulations/formulas they wish to be
considered", so the models' job is to "use the tools/falsifiers assigned to
that subject area to calculate those elements of any given paper that are
computationally available/reducible to them."

WHAT CHANGED. `_apply_back_gate` refused every non-Python target with "no suite
can gate a non-Python target". The runner's own comment beside that refusal
already named the remedy -- "a prose fix needs its falsifier, not pytest ...
which `bench/fix_efficacy.py` already knows how to ask" -- and called it a
design change tracked separately. His rulings are that decision, so the branch
now asks the probe.

IT IS STRICTER, NOT LOOSER, AND THAT IS THE POINT. `fix_efficacy.probe` refuses
unless the falsifier is first shown to READ the target, then shown to
DEMONSTRATE the defect on the original, and only then shown to fall quiet once
the fix is applied. A Python fix is never asked for that much.

THE OLD BEHAVIOUR IS PRESERVED WHERE THERE IS NO FALSIFIER, word for word, so
no existing caller or guard sees a change.
"""
from __future__ import annotations

import importlib
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))


@pytest.fixture(scope="module")
def rr():
    return importlib.import_module("bench.reference_runner_v3")


def _verdicts_reachable_from_probe():
    """Every verdict value `fix_efficacy.probe()` can actually return.

    Derived by walking the AST of `probe` for returned module-level string
    constants, so it tracks the module rather than restating it. This is the
    independent half: the gate says which verdict ADMITS, this says which
    verdicts EXIST, and a sentinel the module cannot produce is caught by
    comparing the 2 rather than by reading either.
    """
    import ast
    fe = importlib.import_module("fix_efficacy")
    consts = {k: v for k, v in vars(fe).items()
              if k.isupper() and isinstance(v, str) and not k.startswith("_")}
    src = pathlib.Path(fe.__file__).read_text()
    probe = next(n for n in ast.walk(ast.parse(src))
                 if isinstance(n, ast.FunctionDef) and n.name == "probe")
    out = {}
    for node in ast.walk(probe):
        if isinstance(node, ast.Return) and node.value is not None:
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Name) and sub.id in consts:
                    out[sub.id] = consts[sub.id]
    return out


def _cure_verdict_reachable_from_probe():
    """The ONE reachable verdict that means the fix cured its own falsifier."""
    reach = _verdicts_reachable_from_probe()
    assert "FIX_CURES" in reach, (
        "fix_efficacy.probe() can no longer return FIX_CURES; the prose gate "
        f"has nothing to admit on. reachable: {sorted(reach)}")
    return reach["FIX_CURES"]


class TestTheGatesSentinelIsAVerdictTheProbeCanProduce:
    """THE REGRESSION GUARD THE FIRST VERSION OF THIS FILE DID NOT HAVE.

    The branch shipped comparing the verdict against `getattr(_fe, "CURED",
    "CURED")`, and `fix_efficacy` defines no `CURED`, so the literal "CURED"
    was compared against 7 reachable verdicts none of which is "CURED": the
    branch admitted 0 of 7, Wilson [0.000000, 0.354330]. Every other test in
    this file passed, because each one fed the gate a verdict built from the
    gate's own expression. These tests compare the 2 sides instead, so ANY
    future drift in either name is caught -- not only this one.
    """

    def test_the_admitting_sentinel_is_reachable(self, rr):
        import inspect
        src = inspect.getsource(rr._apply_back_gate)
        reach = set(_verdicts_reachable_from_probe().values())
        # The gate must name a sentinel the probe can actually return.
        named = [v for v in reach if repr(v) in src or f'"{v}"' in src]
        assert named, (
            "the prose branch names no verdict fix_efficacy.probe() can "
            f"return; reachable = {sorted(reach)}")

    def test_the_gate_admits_the_cure_verdict_and_only_that(
            self, rr, monkeypatch):
        """Drive the gate with EVERY reachable verdict and count admissions."""
        fe = importlib.import_module("fix_efficacy")
        reach = _verdicts_reachable_from_probe()
        admitted = []
        for name, value in sorted(reach.items()):
            class _R:
                pass
            r = _R()
            r.verdict = value
            monkeypatch.setattr(fe, "probe", lambda *a, **k: r)
            ok, _why = rr._apply_back_gate(
                "repaired prose", "notes/thing.md", "",
                finding={"falsifier_code": "assert 1 == 1\n"})
            if ok:
                admitted.append(name)
        assert admitted == ["FIX_CURES"], (
            f"of {len(reach)} reachable verdicts the gate admitted "
            f"{admitted}; exactly ['FIX_CURES'] is correct. 0 admissions is "
            "the 2026-11-10 defect; more than 1 is a gate that has stopped "
            "discriminating.")


class TestTheOldRefusalSurvivesWhereItShould:
    def test_a_prose_target_with_no_finding_is_still_refused(self, rr):
        ok, why = rr._apply_back_gate("some prose", "notes/thing.md", "")
        assert ok is False
        assert "no suite can gate a non-Python target" in why, why

    def test_a_prose_target_whose_finding_has_no_falsifier_is_still_refused(self, rr):
        ok, why = rr._apply_back_gate(
            "some prose", "notes/thing.md", "",
            finding={"proposed_fix": "x", "falsifier_code": "   "})
        assert ok is False
        assert "no suite can gate a non-Python target" in why, why

    def test_an_empty_prose_candidate_is_still_refused_first(self, rr):
        ok, why = rr._apply_back_gate("   ", "notes/thing.md", "")
        assert ok is False
        assert "empty candidate" in why, why

    def test_a_python_target_still_takes_the_syntax_path(self, rr):
        ok, why = rr._apply_back_gate("def f(:\n", "bench/thing.py", "")
        assert ok is False and why.startswith("ast:"), why


class TestTheFalsifierBranchIsReached:
    """The branch must DECIDE, not merely exist."""

    def _probe_returning(self, rr, monkeypatch, verdict):
        import fix_efficacy as fe

        class _R:
            pass
        r = _R()
        r.verdict = verdict
        monkeypatch.setattr(fe, "probe", lambda *a, **k: r)
        return fe

    def test_a_cured_verdict_admits_the_prose_fix(self, rr, monkeypatch):
        # THE VERDICT IS DERIVED FROM WHAT `probe()` CAN RETURN, NEVER FROM THE
        # GATE'S OWN SENTINEL. The first version of this test read
        # `getattr(fix_efficacy, "CURED", "CURED")` -- the identical broken
        # expression the product used -- so it handed the gate exactly whatever
        # string the gate was looking for and passed while the branch admitted
        # 0 of 7 real verdicts. A guard that derives its input from its subject
        # cannot ever disagree with it.
        fe = self._probe_returning(
            rr, monkeypatch, _cure_verdict_reachable_from_probe())
        ok, why = rr._apply_back_gate(
            "repaired prose", "notes/thing.md", "",
            finding={"falsifier_code": "assert 1 == 1\n"})
        assert ok is True, why
        assert why.startswith("falsifier:"), why

    def test_any_other_verdict_refuses(self, rr, monkeypatch):
        self._probe_returning(rr, monkeypatch, "NOT_CURED")
        ok, why = rr._apply_back_gate(
            "repaired prose", "notes/thing.md", "",
            finding={"falsifier_code": "assert 1 == 1\n"})
        assert ok is False
        assert "NOT_CURED" in why, why

    def test_an_indeterminate_probe_refuses_rather_than_admits(self, rr, monkeypatch):
        self._probe_returning(rr, monkeypatch, None)
        ok, why = rr._apply_back_gate(
            "repaired prose", "notes/thing.md", "",
            finding={"falsifier_code": "assert 1 == 1\n"})
        assert ok is False
        assert "INDETERMINATE" in why, why

    def test_a_probe_that_raises_fails_CLOSED_and_says_so(self, rr, monkeypatch):
        """'no opinion' and 'refused' are different facts; the ledger must
        be able to tell them apart."""
        import fix_efficacy as fe

        def _boom(*a, **k):
            raise RuntimeError("boom")
        monkeypatch.setattr(fe, "probe", _boom)
        ok, why = rr._apply_back_gate(
            "repaired prose", "notes/thing.md", "",
            finding={"falsifier_code": "assert 1 == 1\n"})
        assert ok is False, "a probe that cannot run must never ADMIT"
        assert "falsifier-probe-failed" in why and "RuntimeError" in why, why


class TestTheCallerHandsTheFindingOver:
    """★ CONVERTED FROM A SOURCE-TEXT PIN TO A PARSED-CALL CHECK, 2026-11-10,
    AND A FREE PANEL SEAT FOUND IT RED BEFORE I DID.

    The original asserted the literal string
    `_apply_back_gate(mod, rel, test_cmd, finding=entry)` appeared in the
    runner. The SAME NIGHT the gate gained a `domain=` argument, which split
    that call across 2 lines, and the pin went red while the property it
    protects held throughout. That is the exact shape `execute-do-not-grep`
    names: a text assertion cannot follow a door when it moves, and it
    punishes the repair. It is also the B88 harm committed inside the guard
    written to catch it -- a FALSE REASON, a red guard reporting a defect
    that does not exist.

    The check now reads the PARSED call out of the module's AST. It survives
    reformatting, line splits and further arguments, and it still fails if
    `finding=` is ever dropped. It is deliberately not an execution of the
    promote loop: the siblings above already execute the gate itself, and
    standing up a whole run to observe 1 argument would be disproportionate.
    """

    @staticmethod
    def _call_sites():
        import ast
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        out = []
        for n in ast.walk(ast.parse(src)):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name == "_apply_back_gate":
                out.append((n.lineno, len(n.args), [k.arg for k in n.keywords]))
        return out

    def test_the_call_site_still_exists(self):
        """ANTI-VACUITY. Every assertion below quantifies over the call sites,
        so all of them pass on an empty list -- which is what a rename of the
        gate would produce."""
        sites = self._call_sites()
        assert sites, (
            "no call to _apply_back_gate survives in the runner, so the "
            "falsifier branch is unreachable from a real run")

    def test_the_promote_loop_passes_the_entry(self):
        sites = self._call_sites()
        without = [(ln, kw) for ln, _pos, kw in sites if "finding" not in kw]
        assert not without, (
            f"{len(without)} call(s) to _apply_back_gate omit `finding=`, so "
            f"the falsifier branch can never be reached from a real run: "
            f"{without}")

    def test_the_domain_is_handed_over_too(self):
        """The domain route added 2026-11-10 is reached only if the caller
        supplies the domain; without this the route is an unwired addition."""
        sites = self._call_sites()
        without = [(ln, kw) for ln, _pos, kw in sites if "domain" not in kw]
        assert not without, (
            f"{len(without)} call(s) omit `domain=`, so the domain "
            f"verification route cannot be reached: {without}")
