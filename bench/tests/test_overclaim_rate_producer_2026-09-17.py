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
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0
    assert "of" in r.stdout.lower()


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


def test_the_interval_is_cross_verified_inside_the_script():
    """The script asserts statsmodels against a scipy closed form; prove it runs."""
    out = _run()
    assert out.count("Wilson 95%") == 2, out
    lows = re.findall(r"\[([\d.]+)%,", out)
    assert len(lows) == 2 and lows[0] == lows[1], lows


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
