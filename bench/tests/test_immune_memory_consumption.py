"""ImmuneMemory CONSUMPTION: the blended prior seeds R_k(0).

Background. ``bench/dm/_memory.py`` has recorded per-flaw-class Beta-Binomial
priors since Exp 47 and fed nothing. Appendix §1.1 fixes the initial condition
``R_k(0) = π_k``; appendix §1.5 defines ``π(k) = (1-ρ)·π_base + ρ·π_mem(k)``.
The S_k pipeline took ``R_old = meta.get("R", 0.5)`` — and ``model_params`` is
written nowhere in the repository, so R_k(0) was the literal 0.5 in every run
from Exp 37 to Exp 49. This suite covers the switch that ends that.

The tests drive the PRODUCTION function ``_evaluate_sk_for_findings`` with a
real registry, a real target source, and a real SEARCH/REPLACE fix, so the
whole chain is exercised — flag, load, closure, per-finding flaw-class lookup,
threshold decision, R_k update, telemetry — not ``blended_prior`` in isolation.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_immune_memory_consumption.py -v
"""

from __future__ import annotations

import glob
import json
import os
import sys
from types import SimpleNamespace

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._memory import ImmuneMemory  # noqa: E402
from bench.dm._types import Finding  # noqa: E402
from bench.reference_runner_v2 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD,
    RK0_PI_BASE,
    FindingRegistry,
    RunnerConfig,
    _capture_baseline,
    _evaluate_sk_for_findings,
    apply_falsifier_verdicts,
    check_sk_threshold,
    compute_rk_with_eta_channel,
    compute_sk,
)

RHO = 0.2

# A real, compilable target the SEARCH/REPLACE below actually matches.
TARGET_SRC = '''"""Toy target module for the S_k pipeline."""


def widen(value):
    return value * 2


def narrow(value):
    return value / 2
'''

# A real fix: the SEARCH text exists in TARGET_SRC, so the block applies, the
# AST and compile hard gates pass, and compute_sk returns a positive s_k.
GOOD_FIX = """<<<< SEARCH toy_target.py
def widen(value):
    return value * 2
====
def widen(value):
    if value is None:
        raise ValueError("value must not be None")
    return value * 2
>>>> REPLACE
"""


# The real baseline capture, so the effect gates (ruff, bandit) have something
# to compare against and the pipeline reaches the S* decision rather than
# escalating for want of evidence.
_BASELINE = _capture_baseline(TARGET_SRC, source_path="toy_target.py")
def _linters_present() -> bool:
    """Is the external tooling S_k needs actually installed?

    This guard used to be computed by CALLING `compute_sk` and asking whether it
    returned ADMISSIBLE. That cannot distinguish "ruff is missing" from "the
    component under test is broken", so breaking `compute_sk` turned 12 of these
    tests into SKIPS and the file exited 0. Measured 2026-08-28: blinding
    compute_sk took the file from 45 passed to 33 passed, 12 skipped, rc=0.
    Found independently by both reviewers on the instrument confirmation panel.

    A skip guard must never ask the component under test whether to run. It asks
    the environment.
    """
    import subprocess
    for mod in ("ruff", "bandit"):
        try:
            r = subprocess.run([sys.executable, "-m", mod, "--version"],
                               capture_output=True, timeout=30)
        except Exception:                                  # noqa: BLE001
            return False
        if r.returncode != 0:
            return False
    return True


_PIPELINE_LIVE = _linters_present()
_needs_pipeline = pytest.mark.skipif(
    not _PIPELINE_LIVE,
    reason="ruff and/or bandit are not installed, so the S_k effect gates "
           "cannot run. This guard checks the TOOLING, never the component.")


def _mk_registry(flaw_classes):
    """One OPEN finding per flaw class, each carrying the same real fix."""
    reg = FindingRegistry()
    for i, fc in enumerate(flaw_classes):
        cid = reg.register(
            Finding(
                finding_id=f"F{i:03d}",
                model_id="CC2",
                round_idx=0,
                flaw_class=fc,
                severity=0.8,
                abstraction_index=0.3,
                description=f"finding of flaw class {fc}",
                verified=False,
                origin_type="model",
                proposed_fix=GOOD_FIX,
            ),
            "CC2",
        )
        reg.entries[cid]["proposed_fix"] = GOOD_FIX
    return reg


def _run_pipeline(flaw_classes, rk0_prior=None):
    reg = _mk_registry(flaw_classes)
    stats = _evaluate_sk_for_findings(
        reg, TARGET_SRC, "toy_target.py",
        baseline=_BASELINE, round_idx=0, test_cmd=None, s_floor=0.0,
        rk0_prior=rk0_prior,
    )
    return reg, stats


def _memory_from_real_state():
    """The immune memory as it actually stands on disk after Exp 47-49."""
    path = os.path.join(_project_root, "bench", "state", "immune_memory.json")
    if not os.path.exists(path):
        pytest.skip("no recorded immune memory on disk")
    return ImmuneMemory.load(path)


def _prior_fn(mem, rho=RHO):
    return lambda fc: mem.blended_prior(fc, RK0_PI_BASE, rho)


# ── PROOF 1: R_k(0) differs, off vs on, on real recorded data ────────────────

@_needs_pipeline
class TestRk0ActuallyChanges:
    def test_off_path_is_the_uniform_prior(self):
        reg, stats = _run_pipeline([1, 8])
        rk0s = {e["sk_result"]["R_old"] for e in reg.entries.values()
                if "R_old" in e.get("sk_result", {})}
        assert rk0s == {RK0_PI_BASE}, (
            f"consumption OFF must leave R_k(0) at the uniform prior, got {rk0s}")
        assert "rk0_memory_seeded" not in stats
        for e in reg.entries.values():
            assert "rk0_source" not in e.get("sk_result", {}), (
                "the OFF path must emit no new report keys")

    def test_on_path_differs_per_flaw_class_on_real_data(self):
        mem = _memory_from_real_state()
        classes = sorted(mem._records)
        assert classes, "recorded memory is empty — nothing to consume"

        reg_off, _ = _run_pipeline(classes)
        reg_on, stats_on = _run_pipeline(classes, rk0_prior=_prior_fn(mem))

        off = {e["flaw_class"]: e["sk_result"]["R_old"]
               for e in reg_off.entries.values()}
        on = {e["flaw_class"]: e["sk_result"]["R_old"]
              for e in reg_on.entries.values()}

        assert set(off) == set(on) == set(classes)
        differing = [fc for fc in classes if abs(on[fc] - off[fc]) > 1e-9]
        assert differing == classes, (
            f"every recorded flaw class must move R_k(0); unmoved: "
            f"{sorted(set(classes) - set(differing))}\noff={off}\non={on}")
        assert stats_on["rk0_memory_seeded"] == len(classes)

    def test_unseen_flaw_class_collapses_to_the_base_prior(self):
        """Jeffreys pseudocounts give an unseen class π_mem = 0.5, so the
        blended prior is exactly π_base. No evidence, no nudge."""
        mem = ImmuneMemory()
        reg, _ = _run_pipeline([99], rk0_prior=_prior_fn(mem))
        e = next(iter(reg.entries.values()))
        assert e["sk_result"]["R_old"] == pytest.approx(RK0_PI_BASE, abs=1e-12)

    def test_rho_zero_is_consumption_off(self):
        """ρ=0 collapses π(k) to π_base for every class — the escape hatch."""
        mem = _memory_from_real_state()
        classes = sorted(mem._records)
        reg, _ = _run_pipeline(classes, rk0_prior=_prior_fn(mem, rho=0.0))
        for e in reg.entries.values():
            assert e["sk_result"]["R_old"] == pytest.approx(RK0_PI_BASE, abs=1e-12)


# ── PROOF 2: direction obeys appendix §1.5 ──────────────────────────────────

@_needs_pipeline
class TestDirectionMatchesTheAppendix:
    """Appendix §1.5: π(k) = (1 - ρ)·π_base(k) + ρ·π_mem(k), with
    π_mem(k) = (c_k + α_0)/(c_k + r_k + α_0 + β_0). ∂π/∂π_mem = ρ > 0, so a
    flaw class whose historical confirmed-rate exceeds π_base pulls R_k(0) UP,
    and one below π_base pulls it DOWN."""

    def test_high_confirmed_rate_pulls_rk0_up(self):
        mem = ImmuneMemory()
        mem.record_experiment("hi", {7: (40, 1)})
        pi_mem = mem.pi_mem(7)
        assert pi_mem > RK0_PI_BASE, "40 confirmed / 1 rejected must exceed 0.5"
        reg, _ = _run_pipeline([7], rk0_prior=_prior_fn(mem))
        rk0 = next(iter(reg.entries.values()))["sk_result"]["R_old"]
        assert rk0 > RK0_PI_BASE
        assert rk0 == pytest.approx((1 - RHO) * RK0_PI_BASE + RHO * pi_mem, abs=1e-12)

    def test_low_confirmed_rate_pulls_rk0_down(self):
        mem = ImmuneMemory()
        mem.record_experiment("lo", {7: (1, 40)})
        pi_mem = mem.pi_mem(7)
        assert pi_mem < RK0_PI_BASE
        reg, _ = _run_pipeline([7], rk0_prior=_prior_fn(mem))
        rk0 = next(iter(reg.entries.values()))["sk_result"]["R_old"]
        assert rk0 < RK0_PI_BASE
        assert rk0 == pytest.approx((1 - RHO) * RK0_PI_BASE + RHO * pi_mem, abs=1e-12)

    def test_monotone_in_confirmed_rate(self):
        """More confirmations, never a lower R_k(0)."""
        seen = []
        for confirmed in (0, 5, 10, 20, 40, 80):
            mem = ImmuneMemory()
            mem.record_experiment("m", {7: (confirmed, 10)})
            reg, _ = _run_pipeline([7], rk0_prior=_prior_fn(mem))
            seen.append(next(iter(reg.entries.values()))["sk_result"]["R_old"])
        assert seen == sorted(seen), f"R_k(0) not monotone in confirmed count: {seen}"

    def test_bounded_by_rho(self):
        """|π(k) − π_base| ≤ ρ·max(π_base, 1−π_base). The prior nudges; it
        cannot take over the initial estimate."""
        for counts in [(0, 1000), (1000, 0), (1, 1), (0, 0)]:
            mem = ImmuneMemory()
            mem.record_experiment("b", {7: counts})
            reg, _ = _run_pipeline([7], rk0_prior=_prior_fn(mem))
            rk0 = next(iter(reg.entries.values()))["sk_result"]["R_old"]
            assert abs(rk0 - RK0_PI_BASE) <= RHO * max(RK0_PI_BASE, 1 - RK0_PI_BASE) + 1e-12

    def test_real_recorded_classes_point_the_right_way(self):
        mem = _memory_from_real_state()
        for fc in sorted(mem._records):
            pi_mem = mem.pi_mem(fc)
            reg, _ = _run_pipeline([fc], rk0_prior=_prior_fn(mem))
            rk0 = next(iter(reg.entries.values()))["sk_result"]["R_old"]
            if pi_mem > RK0_PI_BASE:
                assert rk0 > RK0_PI_BASE, f"class {fc}: π_mem {pi_mem} but R_k(0) {rk0}"
            elif pi_mem < RK0_PI_BASE:
                assert rk0 < RK0_PI_BASE, f"class {fc}: π_mem {pi_mem} but R_k(0) {rk0}"


# ── PROOF 3: non-distortion against the six completed runs ──────────────────

_LOGS = os.path.join(_project_root, "bench", "logs")
_RUNS = [
    "exp44_evidence_locationkey_live_20260727T002705Z",
    "exp45_memory_statistics_live_20260727T225640Z",
    "exp46_stage6_locationkey_live_20260728T103151Z",
    "exp47_divergence_locationkey_live_20260728T230026Z",
    "exp48_chemistry_exam_live_20260729T044134Z",
    "exp49_engineering_exam_live_20260729T062320Z",
]
# The runner defaults every archived run used: model_params is never populated.
_NU_B, _NU_F, _Q = 0.05, 0.20, 0.5


def _report(run):
    hits = glob.glob(os.path.join(_LOGS, run, "*_report.json"))
    if not hits:
        pytest.skip(f"archival log {run} not present")
    with open(hits[0]) as fh:
        return json.load(fh)


def _threshold_checks(report):
    reg = report["registry"]["entries"]
    out = []
    for rd in report["rounds"]:
        for cid, res in rd.get("sk_pipeline", {}).get("results", {}).items():
            if "s_star" in res:
                out.append((cid, int(reg.get(cid, {}).get("flaw_class") or 0), res))
    return out


def _decide(sk, R):
    passes, s_star = check_sk_threshold(sk, nu_b=_NU_B, nu_f=_NU_F, q=_Q, R=R,
                                        s_floor=0.0)
    return passes, s_star


class TestNonDistortionOnCompletedRuns:
    @pytest.mark.parametrize("run", _RUNS)
    def test_replay_harness_reproduces_the_archive(self, run):
        """Guard on the replay itself: with R_k(0) at the uniform prior the
        production decision function must return exactly what is on disk."""
        for cid, _fc, res in _threshold_checks(_report(run)):
            assert res["R_old"] == RK0_PI_BASE, (
                f"{run}/{cid} archived R_old {res['R_old']} — the archive was "
                f"not produced at the uniform prior")
            passes, s_star = _decide(res["sk"], RK0_PI_BASE)
            assert passes == res["passes_threshold"]
            assert s_star == pytest.approx(res["s_star"], abs=1e-9)

    @pytest.mark.parametrize("run", _RUNS)
    def test_no_admissibility_flip_under_the_strongest_real_prior(self, run):
        """Adversarial arm. Every past run is replayed against the memory as it
        stands TODAY — the strongest prior that exists, and the one a future run
        will actually load — not against the empty memory it really had."""
        mem = _memory_from_real_state()
        flips = []
        for cid, fc, res in _threshold_checks(_report(run)):
            R = mem.blended_prior(fc, RK0_PI_BASE, RHO)
            passes, s_star = _decide(res["sk"], R)
            if passes != res["passes_threshold"]:
                flips.append((cid, fc, res["sk"], res["s_star"], s_star))
        assert not flips, f"{run} admissibility flipped under memory: {flips}"

    @pytest.mark.parametrize("run", _RUNS)
    def test_convergence_round_is_untouched(self, run):
        """The recorded convergence round and reason are properties of the
        γ-alt / state gates, whose inputs are disjoint from the R_k(0) path
        (see test_rk0_cannot_reach_the_convergence_gate)."""
        rep = _report(run)
        assert rep.get("converged_at") is not None
        assert "CONVERGED" in (rep.get("convergence_reason") or "")

    def test_rk0_cannot_reach_the_convergence_gate(self):
        """Structural, not by inspection: ``sk_result`` — the only carrier of
        R_k(0) and R_new — is read nowhere outside the function that writes it,
        and ``sk_stats`` is read only to place it in the round report."""
        import ast

        src_path = os.path.join(_project_root, "bench", "reference_runner_v2.py")
        with open(src_path) as fh:
            src = fh.read()
        tree = ast.parse(src)

        def enclosing(lineno):
            best = None
            for n in ast.walk(tree):
                if isinstance(n, ast.FunctionDef) and \
                        n.lineno <= lineno <= (n.end_lineno or 0):
                    if best is None or n.lineno > best.lineno:
                        best = n
            return best.name if best else "<module>"

        readers = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and \
                    isinstance(node.slice, ast.Constant) and \
                    node.slice.value == "sk_result" and \
                    isinstance(node.ctx, ast.Load):
                readers.add(enclosing(node.lineno))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "get" and node.args \
                    and isinstance(node.args[0], ast.Constant) \
                    and node.args[0].value == "sk_result":
                readers.add(enclosing(node.lineno))
        # `build_irreducible_queue_alarm` (A7, 2026-08-01) reads `sk_result` to
        # put each queued critical's S_k OUTCOME into the evidence bundle it
        # attaches to the report — the column that makes "the gates rejected
        # everything" visible at a glance instead of after an afternoon's
        # digging. It is admitted here, and the admission is narrowed rather
        # than trusted: the second assertion below proves it reads no R_k
        # value. Its own decision (halt or not) is `count > bound`, computed
        # before any `sk_result` is touched.
        # `_rejection_lines` (A10, 2026-08-01) reads `sk_result` to tell the
        # PANEL why its fix was declined — the item that exists because 50
        # fixes were rejected across 4 rounds of Exp 53 and no model was ever
        # told. Admitted here on the terms this guard sets out above: it reads
        # `tristate` and `gate_details` only, deliberately NOT the S_k value
        # (a score in the discovery prompt would be a channel from the
        # fix-admission pipeline into the finding stream for no gain), and it
        # returns prompt text — it decides nothing. The R_k assertion below is
        # what actually holds the line, and it covers this reader unchanged.
        assert readers <= {"_evaluate_sk_for_findings",
                           "build_irreducible_queue_alarm",
                           "_rejection_lines"}, (
            f"sk_result is consumed outside its writer: {sorted(readers)} — "
            f"R_k(0) may now reach a verdict")

        # The invariant the assertion above is a PROXY for, stated directly:
        # the R_k-carrying keys inside `sk_result` are read only by the
        # function that writes them. This is the property that actually
        # matters — a reader that never touches R_old/R_new cannot let R_k(0)
        # reach a verdict, however many other fields it copies — and stating
        # it directly means the proxy can be widened for a genuine diagnostic
        # consumer without the guard going quiet.
        _RK_KEYS = {"R_old", "R_new", "rk0_source", "rk0_flaw_class"}
        rk_readers = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and \
                    isinstance(node.slice, ast.Constant) and \
                    node.slice.value in _RK_KEYS and \
                    isinstance(node.ctx, ast.Load):
                rk_readers.add(enclosing(node.lineno))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "get" and node.args \
                    and isinstance(node.args[0], ast.Constant) \
                    and node.args[0].value in _RK_KEYS:
                rk_readers.add(enclosing(node.lineno))
        assert rk_readers <= {"_evaluate_sk_for_findings"}, (
            f"an R_k value inside sk_result is read outside its writer: "
            f"{sorted(rk_readers)} — R_k(0) can now reach a verdict")

        stats_readers = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "sk_stats" and \
                    isinstance(node.ctx, ast.Load):
                stats_readers.add(src.splitlines()[node.lineno - 1].strip())
        assert stats_readers == {'"sk_pipeline": sk_stats,'}, (
            f"sk_stats gained a consumer: {stats_readers}")

    def test_rk_estimate_does_move_when_the_prior_is_real(self):
        """The flip side, stated plainly: non-distortion is NOT inertness. With
        a populated memory the residual-risk NUMBERS change on every archived
        finding — which is the point of the wiring — while no decision does."""
        mem = _memory_from_real_state()
        moved = same = 0
        for run in _RUNS:
            for cid, fc, res in _threshold_checks(_report(run)):
                R = mem.blended_prior(fc, RK0_PI_BASE, RHO)
                R_new = compute_rk_with_eta_channel(
                    R_old=R, sk=res["sk"], eta_int=_Q, m_div=1.0,
                    c_ext=0.0, nu_k=0.0, d=1.0, p=1.0,
                    nu_b=_NU_B, nu_f=_NU_F)
                if abs(R_new - res["R_new"]) > 1e-9:
                    moved += 1
                else:
                    same += 1
        assert moved > 0, "the prior reached no archived finding — inert wiring"
        assert moved + same == 206, f"expected 206 archived checks, saw {moved + same}"


# ── PROOF 4: advisory-only — the falsifier still decides ────────────────────

@_needs_pipeline
class TestAdvisoryOnly:
    """Appendix §1.5: 'Memory can suggest "this flaw class is rare, so the
    prior should be low" — it cannot say "this finding is false because flaw
    class 3 is historically rare."'"""

    @staticmethod
    def _reg_with_falsifier(flaw_class, severity, verdict):
        reg = FindingRegistry()
        cid = reg.register(
            Finding(finding_id="F001", model_id="CC2", round_idx=0,
                    flaw_class=flaw_class, severity=severity,
                    abstraction_index=0.3, description="real defect",
                    verified=False, origin_type="model",
                    proposed_fix=GOOD_FIX),
            "CC2")
        reg.entries[cid]["proposed_fix"] = GOOD_FIX
        reg.entries[cid]["falsifier_code"] = "assert False, 'demonstrated'"
        reg.entries[cid]["falsifier_verdict"] = verdict
        return reg, cid

    def test_maximally_wrong_prior_does_not_overturn_a_confirmed_critical(
            self, monkeypatch):
        """Memory says this flaw class is essentially never real (1 confirmed
        vs 5000 rejected). The falsifier demonstrates it anyway. The finding
        must still be CONFIRMED."""
        import bench.falsifier_verify as fv
        import bench.reference_runner_v2 as rv2
        monkeypatch.setattr(fv, "reverify_falsifier",
                            lambda code, repo_root=None: "CONFIRMED")
        monkeypatch.setattr(rv2, "reverify_falsifier",
                            lambda code, repo_root=None: "CONFIRMED", raising=False)

        mem = ImmuneMemory()
        mem.record_experiment("adversarial", {3: (1, 5000)})
        assert mem.pi_mem(3) < 0.01, "prior must be strongly against this class"

        reg, cid = self._reg_with_falsifier(3, 0.95, "CONFIRMED")
        _evaluate_sk_for_findings(
            reg, TARGET_SRC, "toy_target.py", baseline=_BASELINE, round_idx=0,
            rk0_prior=_prior_fn(mem))
        seeded = reg.entries[cid]["sk_result"]["R_old"]
        assert seeded < RK0_PI_BASE, "the wrong prior must actually be in force"

        cfg = RunnerConfig(falsifier_gate_enabled=True)
        apply_falsifier_verdicts(reg, round_idx=1, cfg=cfg)

        assert reg.entries[cid]["status"] == "CONFIRMED", (
            f"a prior of {seeded:.4f} overturned a CONFIRMED falsifier verdict "
            f"— advisory-only is broken")
        assert reg.entries[cid]["verified"] is True
        assert reg.entries[cid]["severity"] >= CRITICAL_SEVERITY_THRESHOLD

    def test_maximally_confident_prior_does_not_manufacture_a_verdict(
            self, monkeypatch):
        """The mirror case. Memory says this class is always real; the
        falsifier refutes a NON-critical. The refutation must stand."""
        import bench.falsifier_verify as fv
        import bench.reference_runner_v2 as rv2
        monkeypatch.setattr(fv, "reverify_falsifier",
                            lambda code, repo_root=None: "REFUTED")
        monkeypatch.setattr(rv2, "reverify_falsifier",
                            lambda code, repo_root=None: "REFUTED", raising=False)

        mem = ImmuneMemory()
        mem.record_experiment("adversarial", {3: (5000, 1)})
        assert mem.pi_mem(3) > 0.99

        reg, cid = self._reg_with_falsifier(3, 0.4, "REFUTED")
        _evaluate_sk_for_findings(
            reg, TARGET_SRC, "toy_target.py", baseline=_BASELINE, round_idx=0,
            rk0_prior=_prior_fn(mem))
        assert reg.entries[cid]["sk_result"]["R_old"] > RK0_PI_BASE

        cfg = RunnerConfig(falsifier_gate_enabled=True)
        apply_falsifier_verdicts(reg, round_idx=1, cfg=cfg)
        assert reg.entries[cid]["status"] == "REFUTED", (
            "a confident prior kept a refuted finding alive")

    def test_prior_never_writes_status_or_severity(self):
        """The narrow structural claim: the S_k pipeline, which is the only
        place R_k(0) is consumed, mutates neither status nor severity."""
        mem = _memory_from_real_state()
        classes = sorted(mem._records)
        reg = _mk_registry(classes)
        before = {cid: (e["status"], e["severity"])
                  for cid, e in reg.entries.items()}
        _evaluate_sk_for_findings(
            reg, TARGET_SRC, "toy_target.py", baseline=_BASELINE, round_idx=0,
            rk0_prior=_prior_fn(mem))
        after = {cid: (e["status"], e["severity"])
                 for cid, e in reg.entries.items()}
        assert before == after


# ── Config plumbing ─────────────────────────────────────────────────────────

class TestConfigPlumbing:
    def test_rho_survives_both_config_paths(self):
        from bench.launcher_core import build_runner_config_from_dict
        cfg = {"experiment_name": "t", "models": ["CC2"], "test_article": "x.py",
               "immune_memory_enabled": True, "immune_memory_rho": 0.35}
        assert RunnerConfig.from_dict(dict(cfg)).immune_memory_rho == 0.35
        assert build_runner_config_from_dict(
            cfg, SimpleNamespace(resume=False)).immune_memory_rho == 0.35

    def test_default_is_off_and_rho_matches_the_appendix(self):
        rc = RunnerConfig()
        assert rc.immune_memory_enabled is False
        assert rc.immune_memory_consume_rk0 is False
        assert rc.immune_memory_rho == 0.2

    def test_builder_returns_nothing_when_the_flag_is_off(self):
        from bench.reference_runner_v2 import _build_rk0_prior
        prior, receipt = _build_rk0_prior(
            RunnerConfig(immune_memory_consume_rk0=False))
        assert prior is None and receipt == {}

    def test_builder_returns_a_working_prior_when_enabled(self):
        """The runner's own seam, on the real recorded memory file."""
        from bench.reference_runner_v2 import _build_rk0_prior
        mem = _memory_from_real_state()
        classes = sorted(mem._records)
        prior, receipt = _build_rk0_prior(RunnerConfig(
            immune_memory_consume_rk0=True,
            immune_memory_path="bench/state/immune_memory.json"))
        assert prior is not None
        for fc in classes:
            assert prior(fc) == pytest.approx(
                mem.blended_prior(fc, RK0_PI_BASE, 0.2), abs=1e-9)
        assert sorted(int(k) for k in receipt) == classes, (
            "the consumption receipt must record every class the prior served")

    def test_builder_degrades_to_none_on_a_missing_memory_file(self):
        """A broken prior must never take a run down with it."""
        from bench.reference_runner_v2 import _build_rk0_prior
        prior, receipt = _build_rk0_prior(RunnerConfig(
            immune_memory_consume_rk0=True,
            immune_memory_path="bench/state/definitely_not_here.json"))
        # ImmuneMemory.load returns a fresh instance for a missing file, so the
        # prior exists but is uninformative — every class collapses to pi_base.
        assert prior is None or prior(1) == pytest.approx(RK0_PI_BASE, abs=1e-12)

    def test_runner_actually_calls_the_builder_and_forwards_the_result(self):
        """The end-to-end claim the direct-call tests cannot make: that
        ``run_experiment`` builds the prior and hands it to the S_k pipeline.
        Asserted on the runner's own AST because completing a live
        ``run_experiment`` dispatches panel models, which costs money."""
        import ast

        src_path = os.path.join(_project_root, "bench", "reference_runner_v2.py")
        tree = ast.parse(open(src_path).read())
        run_fn = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == "run_experiment")

        # (a) run_experiment calls _build_rk0_prior and binds both returns.
        builder_calls = [n for n in ast.walk(run_fn)
                         if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                         and n.func.id == "_build_rk0_prior"]
        assert len(builder_calls) == 1, (
            f"run_experiment must build the prior exactly once, "
            f"found {len(builder_calls)}")
        bound = set()
        for asn in ast.walk(run_fn):
            if isinstance(asn, ast.Assign) and any(
                    isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                    and c.func.id == "_build_rk0_prior" for c in ast.walk(asn)):
                bound = {t.id for tgt in asn.targets for t in ast.walk(tgt)
                         if isinstance(t, ast.Name)}
        assert bound == {"rk0_prior", "rk0_priors_used"}, (
            f"builder result must be bound to the prior and its receipt, got {bound}")

        # (b) that prior is forwarded to the S_k pipeline, by keyword.
        sk_calls = [n for n in ast.walk(run_fn)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == "_evaluate_sk_for_findings"]
        assert sk_calls, "run_experiment no longer calls the S_k pipeline"
        for call in sk_calls:
            kw = {k.arg: k.value for k in call.keywords}
            assert "rk0_prior" in kw, (
                "an S_k pipeline call in run_experiment does not forward "
                "rk0_prior — R_k(0) would silently revert to the uniform prior")
            assert isinstance(kw["rk0_prior"], ast.Name) and \
                kw["rk0_prior"].id == "rk0_prior"

        # (c) the receipt reaches the run report, so an inert prior is visible —
        # and the SWITCH is reported separately from the receipt, so a reader can
        # tell "did not consume" apart from "consumed and reached nothing".
        src = open(src_path).read()
        assert 'result["immune_memory"]["rk0_priors_used"] = dict(rk0_priors_used)' in src, (
            "the consumption receipt must be written into the run report")
        assert 'result["immune_memory"]["rk0_consumed"] = _consuming' in src, (
            "the report must state whether consumption was ON, not just what it "
            "drew — an empty receipt otherwise reads identically in both cases")


# ── The coupling this split exists to prevent ───────────────────────────────

class TestRecordingAndConsumptionAreSeparateSwitches:
    """Consumption must never be inherited from the recording flag.

    Consumption first shipped gated on ``immune_memory_enabled`` — already true
    in eleven configs, none of which was written with any intention of consuming
    a prior. Because the memory ACCUMULATES between runs, that gating coupled
    the 2x2 factorial's four cells: cell D's starting risk estimate would depend
    on cells A-C having already run, dissolving the independence the factorial's
    whole comparison rests on. It also gave the zero-plant control a prior shaped
    by three earlier experiments — an uncontrolled variable inside the one
    instrument built to have none.

    Neither would have announced itself. Both runs would have completed and
    produced numbers. Found 2026-07-31 by an adversarial pass that asked which
    shipped configs already carried the flag, which is not visible from inside
    the component.
    """

    CONFIG_GLOBS = ["bench/exp4*_configs/*.json", "bench/exp5*_configs/*.json"]

    def _shipped_configs(self):
        out = []
        for pat in self.CONFIG_GLOBS:
            for path in sorted(glob.glob(os.path.join(_project_root, pat))):
                try:
                    with open(path, encoding="utf-8") as fh:
                        out.append((path, json.load(fh)))
                except (OSError, ValueError):
                    continue
        return out

    @staticmethod
    def _would_consume(cfg):
        """Does this config ACTUALLY end up seeding R_k(0)?

        Built through the real launcher path and then asked of the real builder.
        Reading the config field alone is not enough and never was: under the
        original defect every one of the eleven configs left that field False and
        consumed anyway, because the gate inside the builder read a different
        flag. A test that inspects the config is blind to exactly the bug this
        class is named after.
        """
        from bench.launcher_core import build_runner_config_from_dict
        from bench.reference_runner_v2 import _build_rk0_prior
        if "models" not in cfg or "experiment_name" not in cfg:
            return False
        try:
            rc = build_runner_config_from_dict(dict(cfg), SimpleNamespace(resume=False))
        except Exception:  # noqa: BLE001 — a config that cannot build is not
            return False    # this test's business
        prior, _ = _build_rk0_prior(rc)
        return prior is not None

    def test_recording_alone_does_not_consume(self):
        """The exact defect: enabled=True must not seed R_k(0) by itself."""
        from bench.reference_runner_v2 import _build_rk0_prior
        prior, receipt = _build_rk0_prior(RunnerConfig(
            immune_memory_enabled=True,
            immune_memory_path="bench/state/immune_memory.json"))
        assert prior is None and receipt == {}, (
            "recording implied consumption — the factorial's four cells would "
            "be coupled through accumulated memory and the comparison void")

    def test_consumption_does_not_require_recording(self):
        """The switches are independent in both directions, not merely ordered."""
        from bench.reference_runner_v2 import _build_rk0_prior
        prior, _ = _build_rk0_prior(RunnerConfig(
            immune_memory_enabled=False, immune_memory_consume_rk0=True,
            immune_memory_path="bench/state/immune_memory.json"))
        assert prior is not None

    def test_no_shipped_config_consumes_without_saying_so(self):
        """Consumption is a measurement decision, made per experiment.

        Asserted by BUILDING each shipped config through the real launcher path
        and reading what the runner would actually do — not by inspecting the
        JSON. Inspecting the JSON is what missed the defect in the first place:
        the eleven configs never mentioned consumption, and consumed anyway.
        """
        consuming = [os.path.basename(p) for p, cfg in self._shipped_configs()
                     if self._would_consume(cfg)
                     and "immune_memory_consume_rk0" not in cfg]
        assert not consuming, (
            "these configs would consume a cross-experiment prior without ever "
            f"naming it — consumption is being inherited again: {consuming}")

    def test_the_eleven_recording_configs_do_not_consume(self):
        """The concrete regression: every config carrying the recording flag.

        This is the exact set that would have been coupled. If a twelfth appears
        it is covered automatically, because the set is discovered, not listed.
        """
        recording = [(os.path.basename(p), cfg) for p, cfg in self._shipped_configs()
                     if cfg.get("immune_memory_enabled") is True]
        assert len(recording) >= 11, (
            f"expected the 11 known recording configs, found {len(recording)} — "
            f"if configs moved, this test has gone blind")
        coupled = [n for n, cfg in recording
                   if self._would_consume(cfg)
                   and "immune_memory_consume_rk0" not in cfg]
        assert not coupled, (
            f"recording implies consumption again for: {coupled}")

    def test_the_factorial_cells_do_not_consume(self):
        """The four cells must not be coupled through accumulated memory."""
        cells = [(os.path.basename(p), cfg) for p, cfg in self._shipped_configs()
                 if "factorial" in os.path.basename(p)]
        assert cells, "the factorial configs vanished — this test is now blind"
        coupled = [n for n, cfg in cells
                   if cfg.get("immune_memory_consume_rk0") is True]
        assert not coupled, (
            f"these factorial cells consume a prior that accumulates across the "
            f"other cells, so they are not independent: {coupled}")

    def test_the_zero_plant_control_does_not_consume(self):
        """A control with a learned prior is not a control."""
        ctrls = [(os.path.basename(p), cfg) for p, cfg in self._shipped_configs()
                 if "control" in os.path.basename(p) or "zero" in os.path.basename(p)]
        assert ctrls, "the zero-plant control config vanished — this test is blind"
        contaminated = [n for n, cfg in ctrls
                        if cfg.get("immune_memory_consume_rk0") is True]
        assert not contaminated, contaminated

    def test_both_config_paths_carry_the_new_switch(self):
        """The launcher maps by whitelist. Five silent drops so far."""
        from bench.launcher_core import build_runner_config_from_dict
        cfg = {"experiment_name": "t", "models": ["CC2"], "test_article": "x.py",
               "immune_memory_consume_rk0": True}
        assert RunnerConfig.from_dict(dict(cfg)).immune_memory_consume_rk0 is True
        assert build_runner_config_from_dict(
            cfg, SimpleNamespace(resume=False)).immune_memory_consume_rk0 is True
