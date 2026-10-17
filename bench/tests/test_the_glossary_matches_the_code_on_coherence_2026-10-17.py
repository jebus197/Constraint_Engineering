#!/usr/bin/env python3
"""The operator-facing definition must not assert what the code retracted.

HIS CORRECTION, 2026-10-16: *"The glossary still states the penalty claim both
panel seats retracted, and still describes the retired pruner as active. It is
the definition an operator looks up."*

WHY A DOC TEST RATHER THAN A CODE TEST. Both panel seats repaired the composer's
own warning text on 2026-10-16 and neither touched the glossary, so the code
stopped claiming the penalty while the definition an operator reads went on
claiming it. Nothing was checking the pair, and documentation that contradicts
the code is a defect of equal standing under `docs-defect-parity`.

HOW IT AVOIDS BEING A TEXT-ONLY ASSERTION. A test that only grepped the
glossary would establish that the glossary agrees with itself. So each check
here first establishes the CODE fact by execution -- reading the live default
off the function object, and counting the symbol's live occurrences -- and then
requires the prose to match what was executed. The direction is code-first: if
the code is changed back, these fail, which is the point.
"""
from __future__ import annotations

import importlib.util
import inspect
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

GLOSSARY = REPO / "docs" / "GLOSSARY.md"


def _section(name: str) -> str:
    """The body of one `### name` section, or '' if absent."""
    text = GLOSSARY.read_text(encoding="utf-8")
    m = re.search(rf"^### {re.escape(name)}\s*$(.*?)(?=^### |\Z)",
                  text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def test_the_pruner_is_off_by_default_in_the_code():
    """Established by execution, so the doc check below has something to match."""
    from bench.cdsfl_registry import composer
    sig = inspect.signature(composer.compose)
    assert "coherence_pruning" in sig.parameters, (
        "the flag the glossary describes no longer exists under that name")
    default = sig.parameters["coherence_pruning"].default
    assert default is False, (
        f"coherence pruning now defaults to {default!r}. If it was deliberately "
        f"re-armed, that is a behaviour change needing his ruling, and the "
        f"glossary entry must be rewritten to match.")


def test_the_glossary_does_not_describe_the_retired_pruner_as_active():
    body = _section("Coherence Budget")
    assert body, "the Coherence Budget entry has gone missing"
    assert "retired by default" in body.lower(), (
        "the entry must say the pruner is retired by default, because the code "
        "defaults it to off and this is the definition an operator looks up")
    # the retracted wording: pruning presented as what routinely happens
    assert "prunes SOFT content to get under it" not in body, (
        "the entry again describes the retired pruner as routinely pruning")


def test_the_glossary_does_not_assert_the_retracted_penalty():
    body = _section("Coherence Budget")
    assert "no detection penalty is applied" in body.lower(), (
        "the entry must state that no detection penalty is applied")
    # QUOTING THE RETRACTED CLAIM IS NOT ASSERTING IT, and the first version of
    # this test could not tell the difference -- it failed on the corrected
    # entry, which quotes the old wording in order to explain the withdrawal.
    # That is the same distinction the note linter draws with its verbatim-quote
    # exemption. So each occurrence is read in context, and is a defect only
    # where the sentence carrying it does NOT mark it as withdrawn.
    WITHDRAWN = ("earlier wording", "retracted", "no longer", "was wrong",
                 "withdrawn", "corrected")
    pat = re.compile(r"kappa\(m,\s*g\)\s*<\s*1,?\s*applies to effective detection")
    offences = []
    for m in pat.finditer(body):
        start = body.rfind(".", 0, m.start()) + 1
        end = body.find(".", m.end())
        sentence = body[start:end if end != -1 else len(body)].lower()
        if not any(w in sentence for w in WITHDRAWN):
            offences.append(" ".join(sentence.split())[:120])
    assert not offences, (
        "the entry asserts the penalty both panel seats retracted from the code "
        f"on 2026-10-16, without marking it as withdrawn: {offences}")


def test_no_live_code_computes_the_coherence_penalty():
    """The claim the retraction rests on, re-established rather than trusted.

    The symbol DOES occur in the live tree -- his correction said so and it is
    right -- but every occurrence is prose: a prompt payload describing the
    mathematics to a model, a test assertion, or the comment recording this
    withdrawal. If any occurrence ever becomes a computation, the retraction is
    no longer true and this fails.
    """
    spec = importlib.util.spec_from_file_location(
        "kappa_census",
        REPO / "scripts" / "what_kappa_actually_is_in_the_tree_2026-10-17.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kappa_census"] = mod
    spec.loader.exec_module(mod)

    hits = []
    for path in sorted(REPO.rglob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        if any(rel.startswith(s) or f"/{s}/" in f"/{rel}" for s in mod.SKIP):
            continue
        if rel == mod.SELF:
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for m in mod.PENALTY.finditer(text):
            line = text[:m.start()].count("\n") + 1
            hits.append((rel, line, text.splitlines()[line - 1].strip()))

    assert hits, (
        "the penalty symbol has vanished from the live tree entirely. His "
        "correction records it as present, so verify before accepting this.")
    for rel, line, src in hits:
        prose = (src.lstrip().startswith("#")
                 or rel.startswith("bench/tests/")
                 or rel == "bench/gemini_math_audit.py"
                 or '"' in src or "'" in src)
        assert prose, (
            f"{rel}:{line} uses the coherence penalty outside prose: {src!r}. "
            f"If it is now computed, the retraction in the glossary and in the "
            f"composer warning is false and both must be revisited.")


def test_the_recalibration_entry_records_the_retirement():
    """`docs-consistency-check`: the entry said inert where the code now raises."""
    body = _section("Coherence Budget Recalibration")
    assert body, "the Recalibration entry has gone missing"
    assert "retired" in body.lower() and "raise" in body.lower(), (
        "the entry must record that the function now raises, not merely that it "
        "was inert; it was retired on 2026-10-17")
    from bench.cdsfl_registry import composer
    with pytest.raises(RuntimeError):
        composer.update_coherence_budgets_from_experiments(str(REPO / "bench" / "logs"))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
