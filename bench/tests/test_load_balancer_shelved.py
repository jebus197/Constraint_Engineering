"""The load balancer is SHELVED (founder ruling, 2026-08-22).

Shelved means quarantined, not deleted: `bench/dm/_load_balancer.py` still
imports, still solves, and its own 16 tests still pass. What this file holds is
the three things shelving is supposed to mean, each measured rather than
asserted:

  1. the module itself carries the marker, with the date and the reason;
  2. the documents a reader would consult say so too;
  3. the runner does not call it.

(3) is the load-bearing one, and a static check that can only ever pass is
worth nothing — so `test_the_runner_scan_can_fail` runs the same scanner over a
source that DOES call the component and requires a hit. The scanner reads
names, not strings: `bench/run_exp17_immune.py` mentions "LoadBalancer" inside
prompt text, and quoting a name is not calling it.

Offline: filesystem reads, `ast`, and one direct construction of the shelved
class. No subprocess, no sockets, no network.
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench.dm import _load_balancer as lb_module
from bench.dynamic_management import (
    CapabilityFingerprint,
    DynamicManagementConfig,
    LoadBalancer,
    ModelSpec,
    Role,
    Task,
)

SHELVED_DATE = "2026-08-22"

LB_SOURCE = REPO_ROOT / "bench" / "dm" / "_load_balancer.py"
MANAGER = REPO_ROOT / "bench" / "dm" / "_manager.py"
RUNNER = REPO_ROOT / "bench" / "reference_runner_v2.py"
EXP17 = REPO_ROOT / "bench" / "run_exp17_immune.py"

# Documents that describe the component to a reader, and the token each must
# carry beside its shelving marker so the marker is attached to the right thing.
DOCS = (
    ("docs/ARCHITECTURE.md", "_load_balancer.py"),
    ("bench/TEST_COVERAGE.md", "Load Balancing"),
    ("resources/ONBOARDING.md", "_load_balancer.py"),
    ("bench/dynamic_management.py", "_load_balancer.py"),
)

# Every way the shelved component can be reached by name.
FORBIDDEN = frozenset({
    "LoadBalancer",
    "Allocation",
    "get_allocation",
    "check_dispatch_feasibility",
    "dispatch_check",
    "_load_balancer",
})


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def _referenced_names(node: ast.AST) -> set[str]:
    """Names and attributes referenced in `node` — code, not string content."""
    hits: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and sub.id in FORBIDDEN:
            hits.add(sub.id)
        elif isinstance(sub, ast.Attribute) and sub.attr in FORBIDDEN:
            hits.add(sub.attr)
        elif isinstance(sub, ast.ImportFrom):
            if sub.module and any(part in FORBIDDEN for part in sub.module.split(".")):
                hits.add(sub.module)
            hits |= {a.name for a in sub.names if a.name in FORBIDDEN}
        elif isinstance(sub, ast.Import):
            for a in sub.names:
                if any(part in FORBIDDEN for part in a.name.split(".")):
                    hits.add(a.name)
    return hits


# ---------------------------------------------------------------------------
# 1. The module carries the marker.
# ---------------------------------------------------------------------------

def test_module_declares_itself_shelved_with_date_and_reason():
    assert lb_module.SHELVED is True
    assert lb_module.SHELVED_DATE == SHELVED_DATE

    reason = lb_module.SHELVED_REASON.lower()
    for ground in ("never run outside its own tests",
                   "impossible allocation",
                   "false for four and a half months"):
        assert ground in reason, f"SHELVED_REASON omits the ground: {ground!r}"
    assert "do not retire" in reason, (
        "the ruling was SHELVE, not RETIRE — the reason must record which"
    )


def test_the_shelving_is_visible_at_the_top_of_the_module():
    """A marker buried below 400 lines of solver is not a marker."""
    doc = ast.get_docstring(ast.parse(LB_SOURCE.read_text(encoding="utf-8")))
    assert doc, "the module lost its docstring"
    first_line = doc.splitlines()[0]
    assert "SHELVED" in first_line and SHELVED_DATE in first_line, (
        f"first docstring line must carry SHELVED and the date, got: {first_line!r}"
    )


# ---------------------------------------------------------------------------
# 2. The documents say so.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("doc,anchor", DOCS)
def test_documentation_marks_the_component_shelved(doc: str, anchor: str):
    text = _read(doc)
    assert anchor in text, f"{doc} no longer describes the component"
    assert "SHELVED" in text and SHELVED_DATE in text, (
        f"{doc} describes the load balancer but does not mark it SHELVED "
        f"{SHELVED_DATE}; a reader would take it for a live component"
    )


def test_architecture_gives_the_grounds_not_just_the_label():
    arch = _read("docs/ARCHITECTURE.md")
    assert "## Shelved Components" in arch
    section = arch.split("## Shelved Components", 1)[1].split("\n## ", 1)[0]
    assert "bench/dm/_load_balancer.py" in section
    assert SHELVED_DATE in section
    for ground in ("never run outside its own tests",
                   "impossible allocation",
                   "four and a half months"):
        assert ground in section, f"ARCHITECTURE.md omits the ground: {ground!r}"


def test_the_false_self_description_is_withdrawn():
    """The caller claimed LIVE fingerprints from 2 April 2026. It reads none."""
    manager = MANAGER.read_text(encoding="utf-8")
    tree = ast.parse(manager)
    doc = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_allocation":
            doc = ast.get_docstring(node)
    assert doc, "DynamicManager.get_allocation lost its docstring"
    assert "LIVE fingerprints" not in doc or "Correction" in doc, (
        "get_allocation still claims live fingerprints without withdrawing it"
    )
    assert "SHELVED" in doc and SHELVED_DATE in doc

    # And the claim really is false: no fingerprint is read anywhere in it.
    lb_tree = ast.parse(LB_SOURCE.read_text(encoding="utf-8"))
    reads = {
        n.attr for n in ast.walk(lb_tree)
        if isinstance(n, ast.Attribute) and "fingerprint" in n.attr.lower()
    }
    assert not reads, f"module does read a fingerprint after all: {reads}"


# ---------------------------------------------------------------------------
# 3. The runner does not call it.
# ---------------------------------------------------------------------------

def test_the_runner_does_not_call_the_load_balancer():
    hits = _referenced_names(ast.parse(RUNNER.read_text(encoding="utf-8")))
    assert not hits, (
        f"bench/reference_runner_v2.py references shelved symbols {sorted(hits)}; "
        f"a shelved component with a live caller is not shelved"
    )


def test_no_helper_the_runner_imports_reaches_it():
    """One level out: the runner pulls helpers from run_exp17_immune, and that
    module DOES call `check_dispatch_feasibility` elsewhere (`_dispatch_round`).
    None of the imported helpers may."""
    runner_tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(runner_tree)
        if isinstance(node, ast.ImportFrom) and node.module == "run_exp17_immune"
        for alias in node.names
    }
    assert imported, "the runner no longer imports from run_exp17_immune"

    exp17_tree = ast.parse(EXP17.read_text(encoding="utf-8"))
    offenders = {}
    for node in ast.walk(exp17_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in imported:
                hits = _referenced_names(node)
                if hits:
                    offenders[node.name] = sorted(hits)
    assert not offenders, (
        f"helpers imported by the runner reach the shelved component: {offenders}"
    )


def test_the_runner_scan_can_fail():
    """Negative control. A check that cannot fail proves nothing about the
    check it replaces, so run the scanner over a caller and require a hit."""
    calling_source = (
        "from bench.dm._load_balancer import LoadBalancer\n"
        "def go(models, tasks, roles, cfg):\n"
        "    return LoadBalancer(models, tasks, roles, cfg).solve()\n"
    )
    assert _referenced_names(ast.parse(calling_source)) >= {"LoadBalancer"}

    quoting_source = 'BANNER = "LOAD BALANCING: LoadBalancer, RoleAssignment"\n'
    assert _referenced_names(ast.parse(quoting_source)) == set(), (
        "naming the class in prompt text is not calling it"
    )


# ---------------------------------------------------------------------------
# 4. Shelved, not retired — it must still work.
# ---------------------------------------------------------------------------

def test_shelved_component_still_imports_and_solves():
    """Deleting widens the error surface. If a later change removes the class,
    every document above becomes a lie, so hold the code in place too."""
    fp = CapabilityFingerprint(D_decay=0.1, v_bar=0.9, A=0.85, C=0.8)
    models = [
        ModelSpec("m1", fp, tau=120.0, L=32768, c=0.015),
        ModelSpec("m2", fp, tau=180.0, L=32768, c=0.02),
    ]
    tasks = [Task(task_id="t1", token_demand=5000, flaw_class=1, criticality=0.5)]
    roles = {"m1": Role.PAR, "m2": Role.PAR}
    alloc, cost, balanced = LoadBalancer(
        models, tasks, roles, DynamicManagementConfig()
    ).solve()
    assert alloc.get_assigned_models("t1"), "shelved is not the same as broken"
    assert cost >= 0.0
    assert isinstance(balanced, bool)
