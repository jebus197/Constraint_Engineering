# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c9c0b46cba845765728ab93ee8ee7354ff576abfca16839761a1f864d8646d26
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A rule an ARCHIVED FIGURE depends on may not be retired silently.

CLOSES THE ONE RESIDUAL IN THE RULE-AMENDMENTS REGISTER, named by its own author:
the reconstruction in `bench/rule_amendments.py` rebuilds a superseded predicate by
`getattr`-ing rule tuples out of the still-committed module -- deliberately, so the
register never carries a SECOND COPY of a rule (this project has found "a second
implementation of a rule is a second rule" 6 times). The cost is that the tuple's
survival is incidental: `_KEY_VOCAB_RULES` exists today only because the OUTPUT scan
still uses it. Delete it in an unrelated tidy-up and `restored_rules` raises, the
producer exits non-zero, and the round-11 brief is REFUSED -- a correct historical
record made unverifiable by a cleanup that had nothing to do with it.

Fail-closed is the right default and the register already has it. But "the archive
rots loudly" is not reproducibility, and the founder's standing rule covers this
case exactly: NEVER disable or remove a feature; removal only when a COMMITTED
MEASUREMENT shows a replacement dominates. A rule tuple that an archived figure's
reconstruction depends on is such a feature. This test makes that dependency
VISIBLE AT THE POINT OF DELETION instead of at the next brief validation.

It is deliberately the smallest sufficient thing: it pins only the tuples the
register actually names, so it constrains nothing that no archived figure needs,
and it grows automatically with the register rather than needing to be remembered.

Verified by: python3 -m pytest bench/tests/test_amended_rules_cannot_be_retired_2026-10-02.py -q
"""
from __future__ import annotations

import importlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

REGISTER = ROOT / "bench" / "rule_amendments.json"
pytestmark = pytest.mark.skipif(
    not REGISTER.is_file(), reason="no rule-amendments register in this tree")


def _amendments():
    from bench.rule_amendments import load_register
    reg = load_register()
    return reg["amendments"] if isinstance(reg, dict) and "amendments" in reg else reg


def _named_tuples():
    """[(amendment_id, module, tuple_name)] for every rule an amendment restores."""
    out = []
    for a in _amendments():
        old = a.get("old_predicate") or {}
        mod = old.get("module")
        for name in (old.get("restored_rule_tuples") or []):
            out.append((a.get("id", "?"), mod, name))
    return out


def test_the_register_names_at_least_one_rule_tuple():
    """Guard the guard: an empty list would make every assertion below vacuous."""
    named = _named_tuples()
    assert named, (
        "no amendment names a rule tuple, so this test asserts nothing. Either the "
        "register is empty or `restored_rule_tuples` was renamed and this check "
        "silently stopped checking.")


@pytest.mark.parametrize("case", _named_tuples(), ids=lambda c: f"{c[0]}:{c[2]}")
def test_a_rule_tuple_an_archived_figure_depends_on_still_exists(case):
    """THE POINT. Deleting the tuple fails HERE, beside the deletion.

    If this goes red, do not delete the assertion. Either keep the rule, or
    produce the committed measurement the additive standard requires and amend the
    register to reconstruct the figure another way.
    """
    amendment_id, module_name, tuple_name = case
    assert module_name, f"{amendment_id}: old_predicate names no module"
    mod = importlib.import_module(module_name)
    assert hasattr(mod, tuple_name), (
        f"{amendment_id} reconstructs an archived figure from "
        f"{module_name}.{tuple_name}, which no longer exists. An archived declared "
        f"figure has just become unreproducible. Restore the rule, or amend the "
        f"register with a measurement showing the replacement dominates.")
    rules = getattr(mod, tuple_name)
    assert len(rules) > 0, (
        f"{amendment_id}: {module_name}.{tuple_name} is EMPTY, so the superseded "
        f"predicate reconstructs to the current one and the archived figure will "
        f"silently reproduce as the NEW value. Emptying a rule tuple is a removal.")


def test_the_reconstruction_actually_differs_from_the_live_rule():
    """An amendment whose restoration changes nothing is not an amendment.

    This is the dual failure: a register entry that reconstructs to the live
    predicate would make every archived figure 'reproduce' at today's value, which
    is the laundering the register exists to prevent -- but reached by accident
    rather than by intent.
    """
    from bench.rule_amendments import restored_rules
    for a in _amendments():
        as_of = None
        for fig in (a.get("figures") or a.get("affected_figures") or []):
            as_of = fig.get("as_of") or as_of
        if not as_of:
            continue
        restored = restored_rules(as_of)
        assert restored, (
            f"{a.get('id')}: restoring the rule set as of {as_of} yields nothing, so "
            f"`--as-of` pins the corpus but NOT the rule set, which is the defect "
            f"this register was built to close.")
