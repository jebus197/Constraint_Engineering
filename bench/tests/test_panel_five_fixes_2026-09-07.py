"""What the panel broke in my five approved fixes, and how each was repaired.

Two seats, cc2 and fable, reviewed all five inside a copy of the repository under
the project's formal simplest-sufficient standard. They found defects in FOUR of
the five, and they DISAGREED on Fix 3 -- which was adjudicated by execution rather
than by counting seats, because this project confirms findings programmatically or
by HIL, never by model vote.

THE ADJUDICATION THAT MATTERED. cc2 said my round-0 deferral silently de-triggered
the alarm; fable said the alarm still fired. Measured across the 6 archived runs
that alarm: my predicate silenced 3 of them, Wilson [18.8%, 81.2%], and cc2's own
proposed predicate silenced 5. Both were wrong about the remedy and cc2 was right
about the fault -- `irreducible_escalation` was doing TWO jobs, excluding an item
from the A4 blocker AND counting it toward the alarm, so any deferral silenced the
alarm unless the count was repaired too.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import reference_runner_v3 as R  # noqa: E402


# ---------------------------------------------------------------- fix 3
class _Reg:
    def __init__(self, entries): self.entries = entries
    irreducible_queue_count = R.FindingRegistry.irreducible_queue_count


def _crit(**kw):
    e = {"status": "OPEN", "severity": 0.9}
    e.update(kw)
    return e


def test_a_deferred_item_still_counts_toward_the_alarm():
    """THE ONE THAT MATTERED. Deferring an item removed it from the alarm as well
    as from the A4 blocker, so 3 of 6 archived alarming runs stopped alarming --
    they would burn to max_rounds and end BUDGET_EXHAUSTED, spending paid dispatch
    on rounds that cannot close, which is exactly what halting exists to prevent."""
    reg = _Reg({"C1": _crit(routing_deferred=True),
                "C2": _crit(irreducible_escalation=True)})
    assert reg.irreducible_queue_count() == 2, (
        "a deferred item vanished from the alarm; the deferral silences it")


def test_the_predicate_is_the_property_that_already_exists():
    """`EQUIPMENT_FAILURE_VERDICTS` states the rule in its own words: the
    instrument produced no reading, so no terminal status may stand on it. My
    first predicate re-derived a subset of it and missed every ERROR entry --
    falsifiers that RAN AND CRASHED, which produced no reading either."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    i = src.index('e["irreducible_escalation"] = True')
    window = src[max(0, i - 3000):i]
    assert "EQUIPMENT_FAILURE_VERDICTS" in window, (
        "the deferral no longer keys on the existing equipment-failure property")
    assert "ERROR" in R.EQUIPMENT_FAILURE_VERDICTS
    assert "UNTOOLABLE" in R.EQUIPMENT_FAILURE_VERDICTS


def test_a_deferred_critical_can_stop_blocking_A4_eventually():
    """Without the release valve a deferred critical blocks A4 for the life of the
    run. `exhausted` already exists and is already honoured by the sibling counter
    open_crit_high_count, whose comment reads 'this cannot block for ever.'"""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    i = src.index("def unverified_critical_count")
    j = src.index("def ", i + 40)          # the whole function, not a fixed window
    body = src[i:j]
    assert 'e.get("exhausted")' in body, (
        "unverified_critical_count no longer honours the exhausted valve")


# ---------------------------------------------------------------- fix 4
def test_the_gate_never_admits_a_fix_that_raises_risk():
    """The property the gate exists to enforce, tested directly rather than via a
    threshold. The earlier root-finding form fell back to the shipped gate on
    21.56% of the reachable slice and admitted risk-RAISING fixes there."""
    bad = 0
    for R0 in [i / 20 for i in range(1, 21)]:
        for q in [i / 10 for i in range(1, 10)]:
            for sk in [i / 10 for i in range(0, 11)]:
                passes, _ = R.check_sk_threshold_corrected(sk, 0.05, 0.20, q, R0)
                if passes and R.compute_rk(R0, q, sk, 0.05, 0.20) > R0:
                    bad += 1
    assert bad == 0, f"{bad} admitted fixes raise residual risk"


def test_R_equals_one_is_refused_because_it_is_a_corruption_signal():
    """R == 1 is what compute_rk's non-finite guard coerces a corrupt R_old to.
    Under the pure sign test nothing raises risk there, so everything passed --
    handing a corrupt input a maximally permissive gate, which is the protection
    sk_break_even's own docstring says its None return exists to provide."""
    assert R.check_sk_threshold_corrected(0.0, 0.05, 0.20, 0.5, 1.0) == (False, 1.0)
    assert R.compute_rk(float("nan"), 0.5, 1.0) == 1.0, "the coercion changed"


def test_the_corrected_gate_is_never_looser_than_the_shipped_one():
    looser = 0
    for R0 in [i / 20 for i in range(1, 21)]:
        for q in [i / 10 for i in range(1, 10)]:
            for sk in [i / 10 for i in range(0, 11)]:
                a, _ = R.check_sk_threshold(sk, 0.05, 0.20, q, R0)
                b, _ = R.check_sk_threshold_corrected(sk, 0.05, 0.20, q, R0)
                looser += bool(b and not a)
    assert looser == 0, f"{looser} points admit what the shipped gate refused"


def test_s_star_keeps_its_archived_meaning():
    """scripts/measure_rk_and_gate_are_disconnected.py walks `s_star` across the
    whole archive. Writing the corrected EFFECTIVE threshold into that key would
    silently change what the series means from this commit onward."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    assert 's_star_effective' in src, "the corrected value lost its own key"
    assert '["s_star"] = _shipped_verdict[1]' in src, (
        "s_star no longer holds the shipped raw value the archive series expects")


# ---------------------------------------------------------------- fix 1
def test_the_stand_in_model_is_a_parameter_everywhere_it_is_used():
    """A comment that names a defect the fix did not repair gets quoted later as
    if it had. Both seats caught this one independently."""
    import inspect
    from bench.tools import sim_dispatch_shim as S
    from bench.tools import sim_panel_agents as A
    assert inspect.signature(S.make_shim).parameters["model"].default == "opus"
    assert inspect.signature(S.install).parameters["model"].default == "opus"
    assert "model" in inspect.signature(A._one_agent).parameters, (
        "sim_panel_agents still hardcodes the model its own comment complains about")
    assert '"--model", model,' in (REPO / "bench" / "tools" / "sim_panel_agents.py").read_text()


# ---------------------------------------------------------------- fix 5
def test_the_manifest_and_count_are_recursive():
    """Top-level only meant the manifest omitted 27 of 31 keys, `verify` compared
    against that truncated manifest and passed, and the register described only
    what it listed."""
    src = (REPO / "bench" / "vault_keys.sh").read_text()
    # CODE lines only -- the explanatory comment quotes the old form on purpose.
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    assert "shasum -a 256 *" not in code, "the manifest is top-level again"
    assert "find . -type f -print0 | sort -z | xargs -0 shasum" in code
    assert "ls -1 \"$STORE\" | wc -l" not in code, "the count is top-level again"


def test_no_store_list_is_expanded_unquoted():
    """A store path containing a space was split into non-existent directories, so
    its keys were silently NOT folded at seal time -- left in plaintext while the
    operator believed they were sealed. The canonical store lives under
    'Application Support'."""
    src = (REPO / "bench" / "vault_keys.sh").read_text()
    assert "for legacy in $CDSFL_LEGACY_STORES" not in src
    assert "$(printf '%s\\n' ${CDSFL_LEGACY_STORES:-})" not in src


def test_sealing_writes_the_register_itself():
    """The record must not depend on the operator remembering a second command."""
    src = (REPO / "bench" / "vault_keys.sh").read_text()
    i = src.index("sealed: $_count keys")
    assert "register" in src[i:i + 400], "sealing no longer writes the register"
