"""His 3 rulings on the secondary falsifier pass, pinned so they cannot drift.

HIS RULING, 2026-11-01, against the 3 points put to him: *"I accept your
recommendation. Please implement it. fr"* — the recommendations being ON by
default, NO a secondary may never change a verdict, and YES the configurations
without an independent secondary stay as they are.

ALL 3 WERE ALREADY THE STATE OF THE CODE, so this changes no behaviour. That is
exactly why it is worth pinning: a ruling that merely CONFIRMS the current state
leaves nothing behind, and the setting can then drift back without anything
noticing. The same shape as the demotion operating point pinned on 2026-10-31,
where his accepted figure of 1 in 50 was reached by no test at all and could
have drifted back to a comparison size that was never a live setting.

ONE FIGURE I PUT TO HIM WAS WRONG AND IS CORRECTED HERE. The report said "the 2
software configurations" stay without a secondary. Measured over the live
manifest there are **3**, and they are pinned below as a SET rather than a
count, because a count cannot tell a swap from a match.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import falsifier_pairing as FP  # noqa: E402

AGENTS = REPO / "bench" / "immune_agents.py"
ENV = "CDSFL_FALSIFIER_SECONDARY"


def _secondary_block() -> ast.AST:
    """The `if` statement that runs the secondary pass, located by its call.

    AST, NOT A STRING SEARCH. The constraint box names `ast` as the default for
    a structural code claim, and a substring test would match the same words in
    the comment that explains the rule — which is how a guard ends up asserting
    that a module describes itself consistently.
    """
    tree = ast.parse(AGENTS.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        for sub in ast.walk(node):
            if (isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "select_secondary"):
                return node
    pytest.fail("no call to select_secondary found; the pass has been removed "
                "or renamed, which is a behavioural change needing his ruling")


class TestItIsOnByDefault:
    def test_the_environment_default_is_on(self):
        """HIS RULING 1: it stays on, at about 1 extra tool call per definitive
        verdict. The switch exists so a run CAN be made cheaper; the DEFAULT is
        what he ruled on."""
        block = _secondary_block()
        defaults = [
            c.args[1].value
            for c in ast.walk(block)
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
            and c.func.attr == "get" and len(c.args) == 2
            and isinstance(c.args[0], ast.Constant) and c.args[0].value == ENV
            and isinstance(c.args[1], ast.Constant)]
        assert defaults, f"{ENV} is no longer read with an explicit default"
        assert defaults == ["1"], (
            f"{ENV} now defaults to {defaults!r}. He ruled the pass stays ON; "
            f"any default other than '1' turns it off for every run that does "
            f"not set the variable.")


class TestASecondaryMayNotChangeAVerdict:
    def test_nothing_in_the_secondary_block_assigns_to_a_verdict(self):
        """HIS RULING 2: no. Proved structurally rather than asserted in prose.

        The block may APPEND to `v.evidence` — that is how a disagreement is
        recorded — but any assignment to `v.verdict` would make the secondary
        able to overturn the primary, which is a behavioural change to a live
        experimental apparatus and his call, not a side effect of wiring.
        """
        block = _secondary_block()
        offenders = []
        for node in ast.walk(block):
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                targets = [node.target]
            for t in targets:
                if isinstance(t, ast.Attribute) and t.attr == "verdict":
                    offenders.append(ast.unparse(t))
        assert not offenders, (
            f"the secondary block assigns to {offenders}, so a secondary can "
            f"now overturn the primary. He ruled it may not.")

    def test_it_does_append_to_the_evidence_so_the_block_is_not_inert(self):
        """ANTI-VACUITY. A block that touched nothing would pass the test above
        for the wrong reason."""
        block = _secondary_block()
        appended = [ast.unparse(n.target) for n in ast.walk(block)
                    if isinstance(n, ast.AugAssign)
                    and isinstance(n.target, ast.Attribute)
                    and n.target.attr == "evidence"]
        assert appended, (
            "the secondary pass records nothing, so an unmarked single-tool "
            "verdict is again indistinguishable from a corroborated one")


class TestTheConfigurationsWithoutASecondaryArePinnedAsASet:
    #: Measured 2026-10-31 and re-measured 2026-11-01 over the live manifest.
    #: A SET, NOT A COUNT: a count of 3 cannot tell a swap from a match, which
    #: is the lesson of 2026-10-16.
    WITHOUT = {
        ("code", "code_structural"),
        ("code", "logical"),
        ("cs_software", "code_structural"),
    }

    def test_exactly_these_configurations_have_no_independent_secondary(self):
        """HIS RULING 3: yes, they stay. If this set CHANGES, either a tool was
        installed that gives one of them a secondary — good, and the pin should
        shrink — or a configuration lost one, which is a regression."""
        rows = _pairs()
        without = {(d, c) for (d, c, _p, sec, _r) in rows if sec is None}
        assert without == self.WITHOUT, (
            f"the configurations without an independent secondary have moved.\n"
            f"  now:    {sorted(without)}\n"
            f"  pinned: {sorted(self.WITHOUT)}")

    def test_the_rest_do_have_one(self):
        """ANTI-VACUITY: if nothing had a secondary the pin above would be
        describing a dead mechanism."""
        rows = _pairs()
        assert len(rows) - len(self.WITHOUT) >= 20, (
            f"only {len(rows) - len(self.WITHOUT)} configurations have a "
            f"secondary; the pass has largely stopped selecting one")

    def test_no_paid_route_is_selected_without_his_authorisation(self):
        """Unchanged and load-bearing: a paid route costs him money."""
        for (_d, _c, _p, sec, _r) in _pairs():
            assert sec not in FP.PAID_CLASSES, sec


def _pairs():
    """(domain, claim type, primary, secondary, reason) over the LIVE configs.

    DERIVED FROM THE DECIDING LAYER, NOT FROM THE PRODUCER'S INTERNALS. The
    producer builds its rows inside `main()` and exposes no row function, so an
    earlier version of this helper looked for one and SKIPPED when it found
    none — 3 skipped tests that proved nothing, which is the same fault repaired
    in the note-standard guard earlier today. This drives the same layer the
    dispatch actually reads: `immune.verification_tools` in each domain TOML,
    through `falsifier_pairing` itself.
    """
    import tomllib
    import importlib
    ia = importlib.import_module("bench.immune_agents")
    man = ia._load_tool_manifest()
    dom = REPO / "bench" / "cdsfl_registry" / "domains" / "immune"
    rows = []
    for tf in sorted(dom.glob("*.toml")):
        cfg = tomllib.loads(tf.read_text(encoding="utf-8"))
        vt = (cfg.get("immune") or {}).get("verification_tools") or {}
        for claim, tools in sorted(vt.items()):
            pool = FP.primary_candidates(tools, man)
            if not pool:
                continue
            primary = pool[0]
            sec, reason, _detail = FP.select_secondary(
                primary, tools, man, allow_paid=False)
            rows.append((tf.stem, claim, primary, sec, reason))
    assert rows, "no domain configuration declares verification tools"
    return rows
