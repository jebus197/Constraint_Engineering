"""The figure the panel brief quotes must be produced, not typed.

`measured-rate-travels-with-its-script`: a measured figure may be cited only if
the script that produced it is committed beside it. The brief for the 30
overclaiming entries declares 4 figures against this producer, and
`scripts/panel_brief_validate.py` re-executes each one before any dispatch.

WHY A TEST AS WELL AS THAT VALIDATOR. The validator only runs when a brief is
validated. Under the additive standard an addition nothing reaches is not
additive, and a producer that is only exercised at dispatch time can rot
silently between dispatches. These tests CALL it.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "done_audit_overclaim_rate_2026-09-17.py"
BRIEF = REPO / "experimental_notes" / "panel_briefs" / "Overclaiming_Entries_Brief_2026-09-17.md"


def _run(*args: str) -> str:
    r = subprocess.run([sys.executable, str(SCRIPT), *args],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-1500:]
    return r.stdout


def test_it_answers_help_without_measuring():
    """`--help` must DESCRIBE, never measure.

    The first version of this test asserted the word "of" appeared in the help
    text -- a proxy for "it printed the figure", and a false one: argparse
    prints the docstring's first line, which contains no such word. A test
    whose assertion is a guess about output it never read is the shape this
    project keeps withdrawing. It now asserts the 2 things that matter: the
    usage line is present, and NO measurement was performed.
    """
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-800:]
    out = r.stdout
    assert out.startswith("usage:"), out[:200]
    assert "--ids" in out, "the help no longer documents its own flag"
    for measured in ("Wilson", "%", "statsmodels"):
        assert measured not in out, (
            f"--help printed {measured!r}, so it ran the measurement instead of "
            f"describing it -- the defect that once destroyed a 55,814-byte "
            f"panel record")


def test_it_is_deterministic():
    """Two runs over the same committed evidence must agree exactly."""
    assert _run() == _run()


def test_the_count_is_a_subset_of_the_real_done_entries():
    """The audit flagged ids that do not exist; the producer must exclude them."""
    out = _run()
    m = re.search(r"(\d+) of (\d+) = ([\d.]+)%", out)
    assert m, out
    k, n = int(m.group(1)), int(m.group(2))
    assert 0 < k < n, (k, n)
    ids = _run("--ids").split()
    assert len(ids) == k, f"--ids lists {len(ids)} but the count says {k}"
    tasks = (REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md").read_text(
        encoding="utf-8").split("# SUPPLEMENTARY LIST")[0]
    real = {mm.group(1) for mm in re.finditer(
        r"<!--\s*task:\s*([A-Za-z0-9._]+)\s*\|\s*state:\s*DONE", tasks)}
    phantom = sorted(set(ids) - real)
    assert not phantom, f"the producer names ids that are not DONE entries: {phantom}"


def test_every_interval_is_cross_verified_not_just_the_first():
    """EVERY interval the script prints must be checked by 2+ implementations.

    REWRITTEN 2026-09-17, AND THE OLD FORM CAUGHT A REAL DEFECT FIRST. It
    asserted `count("Wilson 95%") == 2` -- the statsmodels and scipy pair for
    the headline. When the producer was extended to derive round 1 and the
    superseded figure, those 2 new intervals were computed with statsmodels
    alone and the count went to 4, so the guard went red for exactly the right
    reason. Relaxing it to `>= 2` would have deleted the guard rather than
    satisfied it.

    The hardcoded count was still the wrong assertion: it pinned HOW MANY
    intervals exist rather than THAT EACH IS VERIFIED, so it had to fail
    whenever a figure was legitimately added. This form scales.
    """
    out = _run()
    lines = [l for l in out.splitlines()
             if "Wilson 95%" in l or "Clopper-Pearson 95%" in l]
    assert len(lines) >= 4, f"expected at least 4 intervals, saw {len(lines)}: {lines}"
    for l in lines:
        assert "agree to" in l, f"this interval states no cross-verification: {l}"
        m = re.search(r"agree to ([\d.]+e[-+]\d+)", l)
        assert m, f"the agreement is not a measured magnitude: {l}"
        assert float(m.group(1)) < 1e-12, f"implementations disagree: {l}"
        assert sum(t in l for t in ("statsmodels", "scipy", "mpmath")) >= 2, (
            f"fewer than 2 named implementations: {l}")


def test_the_agreement_figure_is_measured_not_typed():
    """The previous version printed the literal string "agrees to 0.0e+00" beside
    an interval whose real worst disagreement is 5.55e-17. A typed agreement
    asserts a verification rather than reporting one."""
    out = _run()
    assert "agrees to 0.0e+00" not in out
    mags = {m for m in re.findall(r"agree to ([\d.]+e[-+]\d+)", out)}
    assert len(mags) > 1, (
        f"every interval reports the identical agreement {mags}, which is what a "
        f"hardcoded string looks like")


def test_the_brief_declares_this_producer():
    """The brief's figures must point at THIS script, or the validator checks nothing."""
    text = BRIEF.read_text(encoding="utf-8")
    decls = re.findall(r"<!--\s*figure:[^|]+\|\s*([^|]+?)\s*\|", text)
    assert decls, "the brief declares no figures at all"
    assert any("done_audit_overclaim_rate_2026-09-17.py" in d for d in decls), decls


def test_every_declared_figure_appears_in_the_output():
    """The pair that matters: what the brief claims, and what the script prints."""
    text = BRIEF.read_text(encoding="utf-8")
    out = _run()
    for value in re.findall(r"<!--\s*figure:[^|]+\|[^|]+\|\s*([^>]+?)\s*-->", text):
        assert value in out, f"the brief declares {value!r}; the producer does not print it"
