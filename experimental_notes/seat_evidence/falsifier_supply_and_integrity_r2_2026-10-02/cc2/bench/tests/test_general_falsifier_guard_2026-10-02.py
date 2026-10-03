# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 905ee0d61dec9e8c695032393a4146422226f4369809bfd562262cd4ca0f253f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The general falsifier template is REACHED, and its cannot-fail guard FAILS
when it should.

Q3 of the 2026-10-02 brief: "Any template you propose must carry its own
cannot-fail guard, and you must demonstrate that guard failing." The named
precedents are `check_sk_threshold` hardwired to `return True`, which passed 321
tests, and A19's `e4_bandit`, which reported 0 HIGH forever at the heaviest
weight. A TEMPLATE makes that hazard worse, because one unfalsifiable pattern
copied into every finding is 321 silent passes instead of one.

So the guard is a SECOND EXECUTION, not a review rule: admissible iff CONFIRMED on
the artefact as given AND REFUTED on a repaired copy. This file drives it with
four falsifiers whose behaviour is known in advance, including two drawn from the
exact failure family the brief names, and requires the guard to separate them.

Also asserted here: the corpus is REACHABLE FROM THE LIVE PATH. Before 2026-10-02
`scripts/falsify_prose_falsifier_supply_2026-09-30.py` part 2 measured 0 live-path
modules importing it, which is the project's own definition of an addition that
does nothing.

Verified by: python3 -m pytest bench/tests/test_general_falsifier_guard_2026-10-02.py -q
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry import (  # noqa: E402  <- the LIVE-PATH import itself
    DOC_PATH_TOKEN, bidirectional, general_templates, load_corpus)
from bench.falsifier_verify import reverify_falsifier  # noqa: E402


def _decide(code: str) -> str:
    return reverify_falsifier(code, repo_root=str(ROOT))


# ── reachability ────────────────────────────────────────────────────────────
def test_the_corpus_is_reachable_from_a_live_path_module():
    """The 2026-09-30 part-2 finding, closed. Empty here means nothing reaches it."""
    assert load_corpus() is not None, "the committed corpus is not importable"
    templates = general_templates()
    assert templates, "no general template is reachable from bench/cdsfl_registry"
    assert all(DOC_PATH_TOKEN in t for t in templates.values()), (
        "a template hard-codes its target, so it cannot be repointed")


def test_the_live_path_reachability_check_now_passes():
    """`grep -l stem_fixtures bench/cdsfl_registry/*.py` must be non-empty.

    This is the literal predicate the 2026-09-30 script measures, re-asserted so
    the wiring cannot be silently unwired by a later tidy-up.
    """
    hits = [p.name for p in (ROOT / "bench" / "cdsfl_registry").rglob("*.py")
            if "stem_fixtures" in p.read_text(encoding="utf-8", errors="replace")]
    assert hits, "no module under bench/cdsfl_registry imports the corpus"


# ── the guard, on falsifiers whose behaviour is known in advance ────────────
@pytest.fixture(scope="module")
def repaired(tmp_path_factory):
    """A file the probes below treat as 'the defect is fixed here'."""
    p = tmp_path_factory.mktemp("repaired") / "artefact.txt"
    p.write_text("REPAIRED\n", encoding="utf-8")
    return p


def _always_confirm(target):
    """THE FAMILY THE BRIEF NAMES. Asserts nothing about the target at all."""
    return "raise AssertionError('FALSIFIED: defect present')\n"


def _always_clean(target):
    """The dual: exits cleanly whatever the target says."""
    return "x = 1\nassert x == 1\n"


def _discriminating(target):
    """Reads its target and asserts on the content. The correct shape."""
    if target is None:
        return ("import pathlib\n"
                "t = 'DEFECT'\n"
                "assert t != 'DEFECT', 'FALSIFIED: the defect is present'\n")
    return (f"import pathlib\n"
            f"t = pathlib.Path({str(target)!r}).read_text()\n"
            f"assert 'DEFECT' not in t, 'FALSIFIED: the defect is present'\n")


def test_the_guard_REFUSES_a_falsifier_that_cannot_fail(repaired):
    """THE REQUIRED DEMONSTRATION. CONFIRMED on both sides -> refused."""
    r = bidirectional(_always_confirm, repaired, _decide)
    assert r.on_artefact == "CONFIRMED", r
    assert r.on_repaired == "CONFIRMED", r
    assert not r.admissible, (
        "a falsifier that confirms on the REPAIRED artefact was admitted: the "
        "guard cannot fail, which is the defect it exists to catch")
    assert "CANNOT FAIL" in r.reason, r.reason


def test_the_guard_REFUSES_a_falsifier_that_demonstrates_nothing(repaired):
    r = bidirectional(_always_clean, repaired, _decide)
    assert not r.admissible, r
    assert r.on_artefact != "CONFIRMED", r
    assert "did not demonstrate" in r.reason, r.reason


def test_the_guard_ADMITS_a_falsifier_that_discriminates(repaired):
    """And it must not be so strict that nothing passes -- the dual failure."""
    r = bidirectional(_discriminating, repaired, _decide)
    assert r.admissible, r
    assert (r.on_artefact, r.on_repaired) == ("CONFIRMED", "REFUTED"), r


def test_the_committed_corpus_passes_its_own_guard():
    """5/5 bidirectional, through the guard rather than through a bespoke loop.

    If this ever goes red the supply has stopped discriminating, and the template
    this module recommends is no longer backed by anything.
    """
    sf = load_corpus()
    assert sf is not None
    tmp = pathlib.Path(tempfile.mkdtemp())
    admitted = []
    for f in sf.FIXTURES:
        fixed = tmp / f.doc_name
        fixed.write_text(f.apply(f.correct_fix), encoding="utf-8")
        r = bidirectional(lambda t, _f=f: _f.falsifier(t) if t else _f.falsifier(),
                          fixed, _decide)
        admitted.append((f.key, r.admissible, r.on_artefact, r.on_repaired))
    bad = [a for a in admitted if not a[1]]
    assert not bad, f"committed corpus falsifiers failed the guard: {bad}"
    assert len(admitted) == 5, admitted
