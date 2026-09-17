"""The producer for task A26's rate runs, and reproduces the figures it is cited for.

PANEL ROUND 16, 2026-09-17. A26 quoted "7 tracked scripts both WROTE something and
ignored the flag -- 5.7377% of 122" with no script behind it. The committed
matchers applied to the tree before the repair give 9 of 122, because the 2 record
assemblers are themselves writers that ignored the flag.
`scripts/help_writers_rate_2026-09-17.py` prints that, and the `-m` column that
the direct-invocation matcher cannot see.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "help_writers_rate_2026-09-17.py"
FIVE = ["scripts/apply_v3.py", "scripts/branch_supplies_adjudication_versions_2026-09-10.py",
        "scripts/dump_panel_findings_2026-09-05.py", "scripts/ffafp_cycle_gamma_2026-09-10.py",
        "scripts/task_list_entry_count_2026-09-10.py"]


def _need_rev(rev: str) -> None:
    if subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"], cwd=REPO,
                      capture_output=True).returncode != 0:
        pytest.skip(f"revision {rev} is not in this checkout")


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=REPO,
                          capture_output=True, text=True, timeout=600)


def test_it_reproduces_9_of_122_before_the_repair():
    _need_rev("75beb74^")
    r = _run("75beb74^")
    assert r.returncode == 0, r.stderr
    assert "direct: 9 of 122 write and ignore --help = 7.3770%" in r.stdout, r.stdout
    assert "Wilson 95%          : [3.9294%, 13.4269%]" in r.stdout, r.stdout
    assert "Clopper-Pearson 95% : [3.4286%, 13.5422%]" in r.stdout, r.stdout


def test_the_dash_m_column_sees_what_the_direct_column_cannot():
    """At d673edd the direct matcher reported 0; 5 guards still leaked under -m."""
    _need_rev("d673edd")
    r = _run("d673edd")
    assert r.returncode == 0, r.stderr
    assert "direct: 0 of 125" in r.stdout, r.stdout
    assert "dash-m: 5 of 125" in r.stdout, r.stdout
    listed = re.findall(r"dash-m: 5 of 125.*?\n.*?\n.*?\n\s+(\[.*?\])", r.stdout, re.S)
    assert listed and all(name in listed[0] for name in FIVE), r.stdout


def test_the_working_tree_has_no_offender_under_either_form():
    if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=REPO,
                      capture_output=True).returncode != 0:
        pytest.skip("not a git checkout")
    r = _run(":worktree")
    assert r.returncode == 0, r.stderr
    assert re.search(r"direct: 0 of \d+ ", r.stdout), r.stdout
    assert re.search(r"dash-m: 0 of \d+ ", r.stdout), r.stdout


def test_the_two_interval_routes_agree():
    spec = importlib.util.spec_from_file_location("help_writers_rate", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    from statsmodels.stats.proportion import proportion_confint
    for k, n in ((9, 122), (0, 126), (5, 125)):
        wl, wh = proportion_confint(k, n, method="wilson")
        cl, ch = proportion_confint(k, n, method="beta")
        wl2, wh2 = m.wilson_closed_form(k, n)
        cl2, ch2 = m.clopper_pearson_bisection(k, n)
        assert abs(wl - wl2) < 1e-12 and abs(wh - wh2) < 1e-12, (k, n)
        assert abs(cl - cl2) < 1e-9 and abs(ch - ch2) < 1e-9, (k, n, (cl, ch), (cl2, ch2))


def test_help_measures_nothing_and_an_unknown_revision_is_refused():
    h = _run("--help")
    assert h.returncode == 0 and h.stdout.startswith("usage:"), h
    assert "write and ignore" not in h.stdout
    bad = _run("no-such-revision-2026-09-17")
    assert bad.returncode == 2 and "REFUSING" in bad.stderr, bad
