"""A NO_DISCRIMINATION falsifier must climb the routing ladder (T01).

FOUNDER RULING, 2026-08-22 — use the mechanism that exists.

The discrimination control's DISC_FAILED outcome (NO_DISCRIMINATION) means the
INSTRUMENT is broken, not the claim: the falsifier fires just as hard against a
CORRECTED copy of the target, so it demonstrated nothing about the finding it
is attached to. That is exactly the class the routing ladder was built to
absorb — the same class as a falsifier that ERRORED (FIX 2, the C0013 class):
un-demonstrated through no fault of the claim.

BEFORE this fix, ``_apply_routing``'s sub-critical branch admitted ONLY
``falsifier_verdict == "ERROR"``. A sub-critical finding whose falsifier
returned NO_DISCRIMINATION (stamped NON_DISCRIMINATING by
``_apply_discrimination_control``) was skipped: escalated, flagged a mechanical
fault, and never shown to a stronger writer. The end-to-end test below drives
the REAL gate and the REAL discrimination control against a real miniature
repository — no mocking of the decision — and then proves the ladder is
reached and the finding resolved by a stronger writer, with the runner's own
``reverify_falsifier`` deciding the verdict.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import bench.reference_runner_v3 as rr  # noqa: E402
import bench.routing as routing_mod  # noqa: E402
from bench.dm._types import Finding  # noqa: E402
from bench.reference_runner_v3 import (  # noqa: E402
    FindingRegistry,
    RunnerConfig,
    _apply_routing,
    apply_falsifier_verdicts,
)

# ── Miniature repository (mirrors test_discrimination_control.py) ────────────

TARGET_REL = "pkg/spec.py"

DEFECTIVE = '''\
"""Reference values for the SW-21 assembly."""

LEGACY_TABLE = {"rev": "A"}


def clearance_mm():
    # The retracted value. This is the claim under test.
    return 0.29
'''

CORRECTED = '''\
"""Reference values for the SW-21 assembly."""

LEGACY_TABLE = {"rev": "A"}


def clearance_mm():
    # Corrected to the current specification.
    return 0.31
'''

# The C0012 shape: it reaches the target, it runs, it fires — and it fires
# because the file is non-empty, which has nothing to do with the clearance.
NON_DISCRIMINATING_FALSIFIER = (
    "from pathlib import Path\n"
    "import pkg.spec as _s\n"
    "src = Path(_s.__file__).read_text(encoding='utf-8')\n"
    "assert not src.strip(), 'the specification is defective'\n"
)

# What the stronger rung answers with: a falsifier whose designed demonstration
# (AssertionError) fires wherever the runner re-runs it, so the runner's real
# reverify_falsifier — not any stub — returns CONFIRMED for it.
STRONG_REPLY = (
    "Here is my final falsifier:\n"
    "```python\n"
    "raise AssertionError('demonstrated by the stronger writer')\n"
    "```\n"
)


@pytest.fixture()
def mini_repo(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "spec.py").write_text(DEFECTIVE, encoding="utf-8")
    return tmp_path


def _exp_config():
    return SimpleNamespace(models=[
        SimpleNamespace(label="Codex"),
        SimpleNamespace(label="CC2"),
        SimpleNamespace(label="SIM"),
    ])


def _entry(severity: float) -> dict:
    return {
        "severity": severity,
        "falsifier_code": NON_DISCRIMINATING_FALSIFIER,
        "corrected_copy": CORRECTED,
        "description": "the stated clearance is the retracted value",
        "status": "OPEN",
        "verdicts": [],
        "source_model": "SIM",
        "open_since_round": 0,
        "last_status_change_round": 0,
    }


class TestDiscriminationFailureIsRouted:
    """The defect and its repair, end to end against the real control."""

    def test_subcritical_no_discrimination_reaches_a_stronger_writer(
            self, mini_repo):
        reg = FindingRegistry()
        reg.entries["C0001"] = _entry(severity=0.5)  # below the 0.7 threshold
        cfg = RunnerConfig(
            test_article=TARGET_REL,
            falsifier_gate_enabled=True,
            routing_enabled=True,
            discrimination_control_blocks=True,
        )
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        # Precondition, established by the REAL discrimination control: the
        # instrument fired on the corrected copy and was stamped accordingly.
        assert e["falsifier_verdict"] == "NON_DISCRIMINATING"
        assert e["escalated"] is True and e["mechanical_fault"] is True

        dispatched = []

        def fake_dispatch(mc, prompt, system, enable_tools=True):
            dispatched.append(mc.label)
            return STRONG_REPLY, None

        with mock.patch.object(rr, "dispatch_to_model", fake_dispatch):
            _apply_routing(reg, 3, _exp_config(), cfg=cfg,
                           repo_root=str(mini_repo))

        # THE FIX: the mechanical fault was handed to the ladder. Before, the
        # sub-critical branch admitted only ERROR and this list stayed empty.
        assert dispatched, (
            "a NO_DISCRIMINATION falsifier was never routed to a stronger "
            "writer — the mechanical fault sat in limbo, shown to nobody")
        assert dispatched[0] == "Codex", (
            "the ladder must start at the strongest rung, excluding the "
            "failed source model")
        assert e["resolved_by_routing"] == "Codex"
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert e["status"] == "CONFIRMED"
        assert e["verified"] is True
        assert e["escalated"] is False

    def test_the_broken_instrument_is_replaced_not_reused(self, mini_repo):
        """The resolving rung's falsifier is adopted; the non-discriminating
        one is gone from the entry."""
        reg = FindingRegistry()
        reg.entries["C0001"] = _entry(severity=0.5)
        cfg = RunnerConfig(
            test_article=TARGET_REL,
            falsifier_gate_enabled=True,
            routing_enabled=True,
            discrimination_control_blocks=True,
        )
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))

        def fake_dispatch(mc, prompt, system, enable_tools=True):
            return STRONG_REPLY, None

        with mock.patch.object(rr, "dispatch_to_model", fake_dispatch):
            _apply_routing(reg, 3, _exp_config(), cfg=cfg,
                           repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert "demonstrated by the stronger writer" in e["falsifier_code"]
        assert NON_DISCRIMINATING_FALSIFIER.strip() not in e["falsifier_code"]


# ── The skip condition itself, pinned at the unit level ──────────────────────

def _mk_finding(fid: str, severity: float) -> Finding:
    return Finding(
        finding_id=fid, model_id="DeepSeek", round_idx=1, flaw_class=1,
        severity=severity, abstraction_index=0.3,
        description=f"test finding {fid}", verified=False, origin_type="model",
    )


def _register(reg: FindingRegistry, fid: str, severity: float,
              verdict: str) -> str:
    cid = reg.register(_mk_finding(fid, severity), "DeepSeek")
    e = reg.entries[cid]
    e["status"] = "UNCONFIRMED"
    e["falsifier_verdict"] = verdict
    e["escalated"] = True
    return cid


class TestSubcriticalRoutingAdmission:
    def _setup(self, monkeypatch, verdict_obj, record_resolve=False):
        calls = []

        def fake_route(finding, models, confirmed, resolve_fn, reverify, sim):
            calls.append(finding["id"])
            if record_resolve:
                # Reach a model, so the one attempt is genuinely consumed.
                resolve_fn("CC2", finding)
            return verdict_obj

        monkeypatch.setattr(routing_mod, "route", fake_route)
        return calls, SimpleNamespace(models=[SimpleNamespace(label="CC2")]), \
            RunnerConfig(routing_enabled=True)

    _UNRESOLVED = SimpleNamespace(verdict="", resolved=False, duplicate_of=None,
                                  falsifier_code="", model_used="")

    def test_subcritical_non_discriminating_is_routed(self, monkeypatch):
        calls, exp_config, cfg = self._setup(monkeypatch, self._UNRESOLVED)
        reg = FindingRegistry()
        cid = _register(reg, "F020", 0.3, "NON_DISCRIMINATING")
        _apply_routing(reg, 6, exp_config, cfg=cfg)
        assert calls == [cid], (
            "a sub-critical NO_DISCRIMINATION finding must be routed exactly "
            "as a sub-critical ERROR is: the instrument is broken, not the claim")

    def test_one_attempt_only_once_a_model_was_reached(self, monkeypatch):
        calls, exp_config, cfg = self._setup(
            monkeypatch, self._UNRESOLVED, record_resolve=True)
        reg = FindingRegistry()
        cid = _register(reg, "F021", 0.3, "NON_DISCRIMINATING")

        def fake_dispatch(mc, prompt, system, enable_tools=True):
            return "no falsifier here", None

        with mock.patch.object(rr, "dispatch_to_model", fake_dispatch):
            _apply_routing(reg, 6, exp_config, cfg=cfg)
            assert reg.entries[cid]["error_routed"] is True
            _apply_routing(reg, 7, exp_config, cfg=cfg)
        assert calls == [cid], (
            "one attempt only — the same guard the ERROR class carries, so "
            "sub-criticals cannot consume the ladder round after round")

    def test_a_sound_falsifier_is_still_not_routed(self, monkeypatch):
        """The widening admits INSTRUMENT FAULTS only, never a working instrument.

        REBASED 2026-08-23. This guard originally read
        `test_untoolable_is_still_not_routed` and asserted "the widening is exactly
        ERROR + NON_DISCRIMINATING, nothing else". That was true of T01 alone and
        became FALSE when T04 landed: the founder amended fix-list item 5 to read
        "a crashed test must not write a final verdict, AND MUST BE SUBJECT TO
        (RE)ROUTING", which puts UNTOOLABLE into the routing admission on purpose.

        The guard's INTENT -- prove this patch does not widen beyond instrument
        faults -- is preserved, and is now expressed with a verdict no task routes:
        a falsifier that RAN and DEMONSTRATED the defect. A working instrument must
        never be sent back to a stronger writer; there is nothing to replace.
        """
        calls, exp_config, cfg = self._setup(monkeypatch, self._UNRESOLVED)
        reg = FindingRegistry()
        _register(reg, "F022", 0.3, "CONFIRMED")
        _apply_routing(reg, 6, exp_config, cfg=cfg)
        assert calls == []
