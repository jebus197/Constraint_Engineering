"""A finding demonstrated in the final round must not be recorded as unresolved.

THE DEFECT
----------
`CONFIRMED + verified -> CLOSED` lives in the per-round reconciliation pass,
which runs at the START of a round. A finding demonstrated in the FINAL round
never meets it — the run stops first — so it is recorded as CONFIRMED while
every peer is recorded as CLOSED.

Measured across the six completed runs: 158 of 160 criticals reached CLOSED. The
two that did not are Exp 45 `C0031` (severity 0.75) and Exp 47 `C0070` (0.85).
Both are CONFIRMED, both `verified`, both carry zero unresolved challenges, and
both opened at the exact round their run converged.

WHY IT MATTERS MORE THAN TIDINESS
---------------------------------
Read from the status field alone, those two look like demonstrated criticals left
UNRESOLVED at close — and they were reported that way on 2026-07-31 before the
state machine was traced. They were not. Nothing escaped. The record was one
transition behind. The difference between "a critical escaped" and "a label
lagged" is the difference between an unsafe instrument and an untidy one, and an
instrument that cannot tell you which is which is the worse problem.

WHAT THIS IS NOT
----------------
It does not fix the location-keyed counter, which remains blind to a second
distinct defect at an already-flagged location — five candidate splitters were
built and refuted the same day. The counter's blindness is a question about
convergence TIMING (the run may stop sooner than ideal); it was never a question
about findings escaping. This separates the two.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.reference_runner_v3 import (  # noqa: E402
    FindingRegistry, _settle_confirmed_findings,
)


def _reg(entries):
    r = FindingRegistry()
    r.entries = entries
    return r


def _entry(status="CONFIRMED", verified=True, verdicts=None, sev=0.8):
    return {"status": status, "verified": verified, "severity": sev,
            "verdicts": verdicts or [], "description": "d", "open_since_round": 3,
            "last_status_change_round": 3}


class TestTheTransitionThatNeverRan:
    def test_a_confirmed_verified_finding_is_closed(self):
        r = _reg({"C0001": _entry()})
        assert _settle_confirmed_findings(r, 4) == ["C0001"]
        assert r.entries["C0001"]["status"] == "CLOSED"

    def test_it_records_that_it_intervened(self):
        """A record that was tidied must say so — otherwise the next reader
        cannot distinguish a finding closed in its round from one closed after."""
        r = _reg({"C0001": _entry()})
        _settle_confirmed_findings(r, 4)
        assert r.entries["C0001"]["settled_post_convergence"] is True

    def test_an_already_closed_finding_is_untouched(self):
        r = _reg({"C0001": _entry(status="CLOSED")})
        assert _settle_confirmed_findings(r, 4) == []


class TestItCannotCloseWhatTheNormalPathWouldHold:
    """The condition must be exactly the reconciliation's, or this becomes a
    back door that settles findings the ordinary run would have kept open."""

    def test_an_unverified_confirmed_finding_stays_open(self):
        """CONTESTED -> CONFIRMED reaches CONFIRMED without `verified`."""
        r = _reg({"C0001": _entry(verified=False)})
        assert _settle_confirmed_findings(r, 4) == []
        assert r.entries["C0001"]["status"] == "CONFIRMED"

    def test_an_unresolved_challenge_blocks_settling(self):
        r = _reg({"C0001": _entry(verdicts=[
            {"verdict": "CONFIRM", "round": 2},
            {"verdict": "CHALLENGE", "round": 3}])})
        assert _settle_confirmed_findings(r, 4) == []

    def test_a_challenge_answered_by_a_later_confirm_does_not_block(self):
        r = _reg({"C0001": _entry(verdicts=[
            {"verdict": "CHALLENGE", "round": 2},
            {"verdict": "CONFIRM", "round": 3}])})
        assert _settle_confirmed_findings(r, 4) == ["C0001"]

    def test_a_same_round_challenge_blocks(self):
        """Mirrors the F24 fix: `>=`, so a same-round challenge is unresolved."""
        r = _reg({"C0001": _entry(verdicts=[
            {"verdict": "CONFIRM", "round": 3},
            {"verdict": "CHALLENGE", "round": 3}])})
        assert _settle_confirmed_findings(r, 4) == []

    @pytest.mark.parametrize("status", ["OPEN", "CONTESTED", "REOPENED",
                                        "UNCONFIRMED", "REFUTED", "MERGED"])
    def test_no_other_status_is_settled(self, status):
        r = _reg({"C0001": _entry(status=status)})
        assert _settle_confirmed_findings(r, 4) == []


class TestAgainstTheRealArchive:
    """Replay the two known cases from their recorded registries."""

    CASES = [("exp45_memory_statistics_live", "C0031"),
             ("exp47_divergence_locationkey_live", "C0070")]

    @pytest.mark.parametrize("run,cid", CASES)
    def test_the_real_finding_settles(self, run, cid):
        hits = sorted(glob.glob(str(_root / "bench" / "logs" / f"{run}_*" /
                                    "*_report.json")))
        if not hits:
            pytest.skip(f"{run} not present")
        data = json.loads(Path(hits[0]).read_text(encoding="utf-8"))
        entries = data["registry"]["entries"]
        assert entries[cid]["status"] == "CONFIRMED", (
            "this finding is no longer the recorded case this test replays")
        settled = _settle_confirmed_findings(_reg(entries), 99)
        assert cid in settled, (
            f"{cid} did not settle — it is CONFIRMED+verified with no unresolved "
            f"challenge, so the reconciliation would have closed it given one "
            f"more round")

    @pytest.mark.parametrize("run,cid", CASES)
    def test_nothing_else_in_that_run_is_disturbed(self, run, cid):
        """158 of 160 criticals already reached CLOSED. Settling must not touch
        them, nor promote anything that was legitimately left unresolved."""
        hits = sorted(glob.glob(str(_root / "bench" / "logs" / f"{run}_*" /
                                    "*_report.json")))
        if not hits:
            pytest.skip(f"{run} not present")
        entries = json.loads(Path(hits[0]).read_text(encoding="utf-8"))["registry"]["entries"]
        before = {k: v["status"] for k, v in entries.items()}
        settled = set(_settle_confirmed_findings(_reg(entries), 99))
        changed = {k for k, v in entries.items() if v["status"] != before[k]}
        assert changed == settled, f"statuses changed outside the settle set: {changed - settled}"
        for k in settled:
            assert before[k] == "CONFIRMED"

    def test_after_settling_no_confirmed_critical_remains_in_either_run(self):
        """The end state this exists to produce: every demonstrated critical in
        the six completed runs is recorded as settled, not as unresolved."""
        for run, _ in self.CASES:
            hits = sorted(glob.glob(str(_root / "bench" / "logs" / f"{run}_*" /
                                        "*_report.json")))
            if not hits:
                continue
            entries = json.loads(Path(hits[0]).read_text(encoding="utf-8"))["registry"]["entries"]
            _settle_confirmed_findings(_reg(entries), 99)
            stuck = [k for k, e in entries.items()
                     if e.get("status") == "CONFIRMED"
                     and float(e.get("severity") or 0) >= 0.7
                     and e.get("verified")]
            assert not stuck, f"{run}: still recorded as unresolved: {stuck}"


class TestWiring:
    # The CALL site, not the `def`. An earlier version of these two tests used
    # `src.index("_settle_confirmed_findings(registry, round_idx)")`, which
    # matches the function DEFINITION first — several thousand lines above the
    # call — so both tests inspected the wrong region and stayed green when the
    # wiring was deliberately broken. Caught by falsifying them.
    CALL = '_settled = _settle_confirmed_findings(registry, round_idx)'

    def _src(self):
        return (_root / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")

    def test_the_call_site_is_uniquely_identifiable(self):
        """Guards the guard: if this string stops being unique, the two tests
        below silently start inspecting the wrong place again."""
        assert self._src().count(self.CALL) == 1

    def test_the_call_is_reachable_and_guarded_only_by_convergence(self):
        """Source order alone does not prove the pass RUNS.

        Disabling the call outright (`if False:`) left every other test in this
        file green, because they check that the call exists and where it sits,
        not that it executes. Asserted on the AST: the call's enclosing `if`
        must test exactly `converged` — which pins reachability and the absence
        of any extra gate in one condition. Proving it by running
        `run_experiment` would mean a live panel dispatch, which costs money.
        """
        import ast
        tree = ast.parse(self._src())
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "run_experiment")
        for node in ast.walk(fn):
            if not isinstance(node, ast.If):
                continue
            calls = [c for c in ast.walk(node) if isinstance(c, ast.Call)
                     and isinstance(c.func, ast.Name)
                     and c.func.id == "_settle_confirmed_findings"]
            if not calls:
                continue
            assert isinstance(node.test, ast.Name) and node.test.id == "converged", (
                f"the settle pass is guarded by "
                f"`{ast.unparse(node.test)}` — it must be `converged` alone, so it "
                f"cannot be disabled or gated on a config the way the sweep is")
            return
        pytest.fail("no `if` in run_experiment contains the settle call — the "
                    "pass is unreachable or was removed")

    def test_the_runner_settles_before_it_sweeps(self):
        """Order is load-bearing: settling first means the sweep is handed only
        findings that are genuinely unresolved, rather than re-falsifying
        settled ones at dispatch cost."""
        src = self._src()
        i = src.index(self.CALL)
        j = src.index('result["post_convergence_sweep"] = _post_convergence_sweep')
        assert i < j, "the settle pass must run before the sweep"

    def test_settling_is_not_gated_on_the_sweep_config(self):
        """The sweep is off by default; the settle pass must run regardless, or
        the defect persists in every run that does not enable a sweep. Exp 45
        is the concrete case: it recorded no sweep at all, and C0031 with it."""
        src = self._src()
        i = src.index(self.CALL)
        window = src[max(0, i - 400):i]
        assert "post_convergence_sweep_rounds" not in window, (
            "the settle pass is gated on the sweep config — Exp 45 configured no "
            "sweep and would still record C0031 as unresolved")
