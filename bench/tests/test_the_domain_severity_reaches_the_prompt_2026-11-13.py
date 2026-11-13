"""The directive promises a seat its domain's critical level. It must arrive.

★ THE DEFECT. `bench/directives/universal/cdsfl_core_formal.md` tells every
seat, verbatim: "Severity is ORDINAL. The ordering and the critical level are
the DOMAIN's, and both arrive in your directive. Do not invent either."

That sentence was FALSE for every domain. Measured by AST on 2026-11-13, the
composer made 0 calls to any severity API; `severity`, `consequence_domain`,
`inheriting_domains` and `may_compose` had 0 product call sites repo-wide. The
manifest's `severity_scale` and `critical_level` reached no composed prompt.

★ ENGINEERING WAS THE LIVE HOLE AND IS THE REGRESSION CASE PINNED BELOW. Its
manifest declares AIAG-VDA FMEA severity 1-10 with a critical level of 7; its
default composed box, `bench/directives/structural/structural_building.txt`,
declares no scale. So a seat was forbidden from inventing a level and given
none -- the one combination that leaves it no lawful move.

★ WHAT THIS DOES NOT DO. It does not touch `CRITICAL_SEVERITY_THRESHOLD`.
The entry that measured the frozen cut holds any change to what the gate
ADMITS under his `d`. Making a printed promise true is a different act from
moving a threshold, and only the first is done here.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "bench"))

MODEL = "Fable"          # a model the registry actually declares


@pytest.fixture(scope="module")
def comp():
    from cdsfl_registry import composer
    return composer


def _domain_text(comp, domain: str) -> str:
    cs = comp.compose(task_domain=domain, model=MODEL, situation=None)
    return "\n".join(p.text for p in cs.packets if p.layer == "domain")


def test_engineering_receives_its_critical_level(comp):
    """★ THE CASE THAT WAS BROKEN. Not a constructed probe -- the live default."""
    txt = _domain_text(comp, "engineering")
    assert "FMEA" in txt, (
        "an engineering seat receives no FMEA scale. Its directive forbids it "
        "from inventing a critical level, so it now has no lawful move.")
    assert re.search(r"CRITICAL LEVEL:\s*7", txt), (
        "the engineering critical level of 7 does not reach the prompt")


def test_a_domain_declaring_none_says_so_honestly(comp):
    """An absent scale must be DECLARED absent, not silently missing. The
    directive has a branch for an inherited scale; it needs telling."""
    txt = _domain_text(comp, "logistics")
    assert "SCALE: none" in txt, (
        "logistics declares no scale in the manifest and the prompt is silent "
        "about it, which reads to a seat as an oversight rather than a fact")


def test_an_encoding_that_declares_its_own_scale_is_not_overridden(comp):
    """★ THE DISCRIMINATION HALF. 22 of the 51 encodings carry their own
    SEVERITY SCALE line, and those are the better statement -- the software box
    cites Table 22 of the CVSS specification by name. Appending a second,
    blunter declaration beside it would be a regression dressed as a fix."""
    txt = _domain_text(comp, "software")
    assert txt.count("SEVERITY SCALE") == 1, (
        f"the software domain carries {txt.count('SEVERITY SCALE')} severity "
        f"declarations; the encoding's own was duplicated rather than left alone")
    assert "Table 22" in txt or "CVSS" in txt


def test_every_manifest_domain_composes_without_raising(comp):
    """A severity lookup must never be able to break composition itself."""
    from cdsfl_registry import domain_vocabulary as dv
    names = list(dv.domains()) if hasattr(dv, "domains") else [
        "biology", "chemistry", "cross_domain", "engineering",
        "information_science", "logistics", "mathematics", "physics",
        "software", "statistics"]
    for d in names:
        txt = _domain_text(comp, d)
        assert isinstance(txt, str)


def test_the_promise_in_the_directive_still_exists(comp):
    """★ NON-VACUITY. If that sentence is ever removed from the universal
    directive, this whole file is guarding a contract nobody makes, and the
    right response is to delete the guard rather than let it pass silently."""
    f = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
    assert f.is_file()
    t = f.read_text(encoding="utf-8", errors="ignore")
    assert "both arrive in your directive" in t, (
        "the universal directive no longer promises the seat its domain's "
        "critical level. This guard exists to make that promise true; if the "
        "promise is gone, retire the guard deliberately rather than relax it.")


def test_the_gate_constant_is_untouched():
    """★ THE BOUNDARY. This repair must not have moved what the gate admits."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(
        encoding="utf-8", errors="ignore")
    assert "CRITICAL_SEVERITY_THRESHOLD = 0.7" in src, (
        "the live critical cut moved. That is held under his `d` and is not "
        "part of making the directive's promise true.")
