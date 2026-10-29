"""The harvester's chat source is retired from the default and still reachable.

HIS RULING, 2026-10-28: *"My verdict is to scrap it if it will add to
inefficiency."* It does, so task T4 retired it. This guard exists because that
retirement was carried out and asserted by NOTHING: marking T4 DONE was refused
by `test_done_markers_carry_evidence_2026-09-10`, whose message is exact -- *"A
DONE marker without evidence records a claim, not a result."* It was right. The
default had been changed, no test read it, and a later edit could have restored
it silently.

BOTH HALVES ARE HELD, because the additive standard asks for both. A removal
needs a committed measurement that the replacement dominates, and
`measured-rate-travels-with-its-script` means the measurement has to stay
reproducible -- so `from_chat` must SURVIVE while being unreached by default.
A guard that only checked the default would be satisfied by deleting the
function, which would destroy the evidence that justifies deleting it.

THE PREDICATES ARE READ OFF THE SYNTAX TREE rather than from the help text. A
help string is prose about the behaviour; the `default=` value and the `if`
guarding the call are the behaviour.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HARVESTER = REPO / "scripts" / "harvest_tickets_2026-10-17.py"


@pytest.fixture(scope="module")
def tree() -> ast.Module:
    return ast.parse(HARVESTER.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def source() -> str:
    return HARVESTER.read_text(encoding="utf-8")


def _sources_default(tree: ast.Module) -> str | None:
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "attr", "") == "add_argument"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "--sources"):
            for kw in node.keywords:
                if kw.arg == "default" and isinstance(kw.value, ast.Constant):
                    return kw.value.value
    return None


class TestItIsRetiredFromTheDefault:
    def test_the_sources_flag_still_exists(self, tree):
        assert _sources_default(tree) is not None, (
            "no `--sources` argument with a default; this guard's premise is gone")

    def test_chat_is_not_in_the_default(self, tree):
        default = _sources_default(tree)
        named = {s.strip() for s in default.split(",") if s.strip()}
        assert "chat" not in named, (
            f"`--sources` defaults to {default!r}, which reaches the chat source. "
            f"His ruling of 2026-10-28 retired it from the default.")

    def test_the_default_still_reaches_the_2_live_sources(self, tree):
        named = {s.strip() for s in _sources_default(tree).split(",") if s.strip()}
        assert named == {"task_list", "responses"}, (
            f"the default is {sorted(named)}; retiring chat must not retire the "
            f"sources that replaced it, which is the dominance claim the removal "
            f"rests on")

    def test_the_call_is_guarded_by_an_explicit_request(self, tree):
        """A default that omits chat is not enough: the CALL must be gated."""
        guarded = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            calls = {c.func.id for c in ast.walk(node)
                     if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
            if "from_chat" not in calls:
                continue
            test = ast.unparse(node.test)
            if "chat" in test:
                guarded = True
        assert guarded, (
            "`from_chat` is called outside any test for 'chat' in the requested "
            "sources, so the default cannot keep it unreached")


class TestItIsNotDeleted:
    """The retired half is the SUBJECT of the measurement that retires it."""

    def test_from_chat_still_exists(self, tree):
        names = {n.name for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert "from_chat" in names, (
            "`from_chat` has been deleted. The measurement justifying its "
            "retirement runs over it, and "
            "`measured-rate-travels-with-its-script` requires that evidence to "
            "stay reproducible. Retire it; do not destroy it.")

    def test_naming_chat_explicitly_still_reaches_it(self, source):
        """`--sources chat` must remain a usable route, not a dead string."""
        assert "chat" in source
        spec = importlib.util.spec_from_file_location("harv", HARVESTER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["harv"] = mod
        spec.loader.exec_module(mod)
        assert callable(getattr(mod, "from_chat", None)), (
            "from_chat is not importable and callable, so `--sources chat` "
            "cannot reach it")


class TestTheHeaderAgreesWithTheRuling:
    """Stale documentation is a defect of equal standing to stale code, and this
    header asserted the opposite of his ruling for a day."""

    def test_the_docstring_names_the_ruling(self, tree):
        doc = ast.get_docstring(tree) or ""
        assert "2026-10-28" in doc, (
            "the module header does not mention the ruling that retired the "
            "chat source, so a reader meets the superseded instruction first")

    def test_the_docstring_does_not_advertise_chat_as_a_source(self, tree):
        first = (ast.get_docstring(tree) or "").splitlines()[0]
        assert "from chat" not in first.lower(), (
            f"the header's first line still offers chat as a source: {first!r}")

    def test_the_superseded_instruction_is_marked_as_superseded(self, tree):
        doc = (ast.get_docstring(tree) or "")
        if "HIS INSTRUCTION, 2026-10-17" not in doc:
            pytest.skip("the 2026-10-17 instruction is no longer quoted here")
        before = doc.split("HIS INSTRUCTION, 2026-10-17")[0]
        assert "supersede" in before.lower(), (
            "his 2026-10-17 instruction asking FOR the chat half is quoted with "
            "no note ABOVE it that a later ruling reversed it, which is how "
            "rejected advice keeps its authority")
