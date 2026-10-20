#!/usr/bin/env python3
"""The UX backend: a READ-ONLY projection of harness state into the 8 tabs.

HIS INSTRUCTION, 2026-10-20: "I am not asking you to build the UX now. I am still
working on some mock-ups for the other tabs, but you can build the UX backend, so
that the eventual UX can map cleanly on to it." And on the pack itself: "you have
the ability to look at the code and decide on sane choices, rather than run
verbatim with whatever you might find here."

WHY A PROJECTION AND NOT A STORE. Every field the mock-ups show already exists in
`runner_state.json`: a finding carries `canonical_id`, `description`, `severity`,
`status`, `status_adjudicator`, `hil_escalated`, `computed_evidence`,
`routing_history` and more, and the run carries `gamma_history` and
`gate_history`. A backend that kept its own copy would be a second source of
truth for one fact, which is the shape this project keeps finding. So nothing
here stores anything: every view is computed from the run state on disk, and a
view that cannot be computed says so rather than inventing a default.

THE CANONICAL TAB SET is the README's, which names 01_orchestrator.jpg as the
target chrome, with Discussions renamed on his instruction: "The discussions
section should simply be named "Discourse"". The mock-ups disagree with each
other -- 02_findings.jpg shows Overview | Model | Constraints | Findings |
Validation | Orchestration | Settings, which is a different shell entirely --
and he warned that they are rough. The README is the explicit statement of
intent, so it wins.

THE 2 INVARIANTS ARE ENFORCED, NOT DECORATED. The pack asks for a banner reading
"Discussion cannot clear claims" and states "Humans accept residual; models do
not clear by prose". A banner is a label; these are rules, and the harness
already records what settled every status in `status_adjudicator`, so the rules
are checkable. `clearance_violations()` returns every finding whose status was
settled by something other than a tool or a human, and it reads the stored log
rather than trusting the summary field.
"""
from __future__ import annotations

import json
import pathlib
import re
from typing import Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "bench" / "logs"

#: The shell, in order. Discussions is Discourse on his instruction of 2026-10-20.
TABS = ("Orchestrator", "Findings", "Evidence", "Explorer",
        "Discourse", "Recipes", "Advanced", "HIL")

#: The STEM areas Discourse is divided into, from the pack's README verbatim.
DISCOURSE_AREAS = ("Mathematics", "Physics", "Chemistry", "Biology", "Software",
                   "Engineering", "Statistics", "Cross-domain",
                   "Protocol & residual risk", "Registry & tooling")

#: The banner is a statement of a rule that `clearance_violations` enforces.
CLEARANCE_BANNER = "Discussion cannot clear claims"

#: Who may settle a claim. MEASURED, not assumed: over the 62 archived runs the
#: adjudicators actually recorded are `tool`, `runner` and `model`. `tool` is an
#: executed falsifier or control and `runner` is the harness's own mechanical
#: bookkeeping -- both are code, and neither is prose. `model` is a seat's
#: assertion, which may CONTEST a claim but may never settle one.
#: `human` and `hil` are permitted because the pack's rule is "humans accept
#: residual"; they do not appear in the archive yet, and are listed so that the
#: first one does not read as a violation.
PERMITTED_ADJUDICATORS = ("tool", "runner", "human", "hil")

#: Transitions that are not a clearance, so an adjudicator restriction does not
#: apply to them. WITHHELD withholds rather than clears; CONTESTED is the one
#: move a model IS allowed to make, and the archive shows all 5 of its
#: transitions going there.
NOT_A_CLEARANCE = ("OPEN", "CONTESTED", "WITHHELD", "UNCONFIRMED", "")

#: Residual bands. The mock-up shows Low / Med / High against "Acceptable
#: residual" / "Monitor / mitigate" / "Requires attention". The thresholds are
#: the harness's own: 0.7 is where `unverified_critical_count`'s release valve
#: sits, so High begins there rather than at a number chosen for the interface.
RESIDUAL_BANDS = ((0.7, "High"), (0.4, "Med"), (0.0, "Low"))

#: Tools are read out of the falsifier's own source, not declared separately.
_TOOL_PATTERNS = (
    ("SymPy", re.compile(r"\bimport\s+sympy|\bfrom\s+sympy\b")),
    ("Z3", re.compile(r"\bimport\s+z3|\bfrom\s+z3\b")),
    ("SciPy", re.compile(r"\bimport\s+scipy|\bfrom\s+scipy\b")),
    ("NumPy", re.compile(r"\bimport\s+numpy|\bfrom\s+numpy\b")),
    ("mpmath", re.compile(r"\bimport\s+mpmath|\bfrom\s+mpmath\b")),
    ("ruff", re.compile(r"\bruff\b")),
    ("pytest", re.compile(r"\bpytest\b")),
)


class NoSuchRun(KeyError):
    """Named rather than returning an empty view, which would read as 'no data'."""


# ── loading ────────────────────────────────────────────────────────────────

def runs() -> list[str]:
    """Every run with a state file, newest last. Names, not paths."""
    if not LOGS.is_dir():
        return []
    return sorted(p.parent.name for p in LOGS.glob("*/runner_state.json"))


def load(run: str) -> dict:
    p = LOGS / run / "runner_state.json"
    if not p.is_file():
        raise NoSuchRun(f"no runner_state.json for run {run!r}")
    return json.loads(p.read_text(encoding="utf-8"))


def _findings(state: dict) -> list[dict]:
    entries = (state.get("registry") or {}).get("entries") or []
    return list(entries.values()) if isinstance(entries, dict) else list(entries)


# ── derivations, each from a stored field ──────────────────────────────────

def residual_band(severity: Any) -> str:
    """Low / Med / High, or UNKNOWN when severity is absent.

    UNKNOWN rather than Low: a missing severity is not a safe one, and the
    mock-up's Low means "acceptable residual", which is a claim.
    """
    try:
        s = float(severity)
    except (TypeError, ValueError):
        return "UNKNOWN"
    for floor, name in RESIDUAL_BANDS:
        if s >= floor:
            return name
    return "UNKNOWN"


def tools_used(finding: dict) -> list[str]:
    """Read out of the falsifier's own source. A declared list would be a second
    description of one fact, and the two would drift."""
    src = finding.get("falsifier_code") or ""
    return [name for name, pat in _TOOL_PATTERNS if pat.search(src)]


def display_status(finding: dict) -> str:
    """The mock-up's 4 states, each derived rather than stored under that name.

    tool-confirmed  the status was settled by an executed tool and stands
    HIL             escalated to a human, or holding computed evidence for one
    closed          resolved or dismissed
    open            new or unresolved
    """
    if finding.get("hil_escalated"):
        return "HIL"
    raw = str(finding.get("status") or "").upper()
    if raw in ("CLOSED", "RESOLVED", "DISMISSED"):
        if (finding.get("status_adjudicator") == "tool"
                and finding.get("verified")
                and not finding.get("verification_voided")):
            return "tool-confirmed"
        return "closed"
    if finding.get("verified") and not finding.get("verification_voided"):
        return "tool-confirmed"
    return "open"


# ── the 2 invariants, enforced ─────────────────────────────────────────────

def clearance_violations(state: dict) -> list[dict]:
    """Every claim settled by something that may not settle one.

    THE RULE, from the pack: "Discussion cannot clear claims" and "Humans accept
    residual; models do not clear by prose". It is checked against `status_log`,
    which records the adjudicator of each transition, rather than against
    `status_adjudicator`, which holds only the latest. A claim cleared by prose
    and later re-stamped by a tool would pass a check on the summary field and
    fail this one, which is the point.
    """
    bad = []
    for f in _findings(state):
        for step in finding_status_log(f):
            who = str(step.get("adjudicator") or "").lower()
            to = str(step.get("to") or "").upper()
            if to in NOT_A_CLEARANCE:
                continue                       # not a clearance
            if who not in PERMITTED_ADJUDICATORS:
                bad.append({
                    "finding": f.get("canonical_id"),
                    "to": to,
                    "adjudicator": step.get("adjudicator"),
                    "round": step.get("round"),
                    "why": (f"a claim moved to {to} with adjudicator "
                            f"{step.get('adjudicator')!r}, which is neither a tool "
                            f"nor a human. {CLEARANCE_BANNER}."),
                })
    return bad


def finding_status_log(finding: dict) -> list[dict]:
    log = finding.get("status_log")
    return list(log) if isinstance(log, list) else []


# ── the tabs ───────────────────────────────────────────────────────────────

def orchestrator(run: str) -> dict:
    """Run context, binding and constraints -- the right-hand rail of 01."""
    s = load(run)
    g = s.get("gamma_history") or []
    fs = _findings(s)
    open_residual = [f for f in fs if display_status(f) == "open"]
    return {
        "run": run,
        "gamma": round(float(g[-1]), 4) if g else None,
        "gamma_history": [round(float(x), 4) for x in g],
        "status": "converged" if (s.get("gate_history") or [False])[-1] else "running",
        "residual_open": len(open_residual),
        "residual_open_high": sum(1 for f in open_residual
                                  if residual_band(f.get("severity")) == "High"),
        "binding": {
            "mode": "bounded",
            "policy": "tools-decide",
            "prose_clearance_required": False,
            "note": ("the orchestrator may open findings and name a next action; "
                     "it does not adjudicate. " + CLEARANCE_BANNER + "."),
        },
        "clearance_violations": len(clearance_violations(s)),
    }


def findings(run: str) -> list[dict]:
    """The Findings table, one row per finding, in the mock-up's columns."""
    s = load(run)
    return [{
        "id": f.get("canonical_id"),
        "claim": (f.get("description") or "").strip().split("\n")[0][:140],
        "status": display_status(f),
        "residual": residual_band(f.get("severity")),
        "severity": f.get("severity"),
        "tools": tools_used(f),
        "adjudicator": f.get("status_adjudicator"),
    } for f in _findings(s)]


def evidence(run: str, finding_id: str) -> dict:
    """Everything that bears on one claim, with nothing summarised away."""
    s = load(run)
    for f in _findings(s):
        if f.get("canonical_id") == finding_id:
            return {
                "id": finding_id,
                "claim": f.get("description"),
                "status": display_status(f),
                "residual": residual_band(f.get("severity")),
                "falsifier_code": f.get("falsifier_code"),
                "falsifier_verdict": f.get("falsifier_verdict"),
                "computed_evidence": f.get("computed_evidence") or [],
                "verdicts": f.get("verdicts") or [],
                "status_log": finding_status_log(f),
                "routing_history": f.get("routing_history") or [],
                "discrimination": f.get("discrimination"),
                "verification_voided": f.get("verification_voided"),
                "verification_voided_reason": f.get("verification_voided_reason"),
            }
    raise KeyError(f"no finding {finding_id!r} in run {run!r}")


def explorer(run: str) -> dict:
    """The series a chart is drawn from. Raw, so the chart cannot smooth them."""
    s = load(run)
    return {
        "gamma": [round(float(x), 6) for x in (s.get("gamma_history") or [])],
        "rho": [round(float(x), 6) for x in (s.get("rho_history") or [])],
        "open_ch": list(s.get("open_ch_history") or []),
        "gate": list(s.get("gate_history") or []),
        "rounds": len(s.get("gamma_history") or []),
    }


def discourse() -> dict:
    """The Discourse tab: STEM areas and the rule that governs the whole tab.

    IN-SHELL ONLY, on his instruction: "the Discourse resource will be an
    integrated tab along the top with the other tabs, not a standalone/separate
    resource as depicted here."
    """
    return {
        "name": "Discourse",
        "in_shell": True,
        "areas": list(DISCOURSE_AREAS),
        "banner": CLEARANCE_BANNER,
        "banner_is_enforced_by": "bench/ux_backend_2026-10-20.clearance_violations",
    }


def hil(run: str) -> dict:
    """The human queue. Approve fix / Reject / Request evidence, per the pack."""
    s = load(run)
    queue = [f for f in _findings(s) if display_status(f) == "HIL"]
    return {
        "actions": ("approve_fix", "reject", "request_evidence"),
        "rule": "humans accept residual; models do not clear by prose",
        "queue": [{
            "id": f.get("canonical_id"),
            "claim": (f.get("description") or "").strip().split("\n")[0][:140],
            "residual": residual_band(f.get("severity")),
            "has_computed_evidence": bool(f.get("hil_has_computed_evidence")),
        } for f in queue],
    }


def shell() -> dict:
    """What the interface chrome is, so a front end need not hard-code it."""
    return {"tabs": list(TABS), "default_theme": "light",
            "themes": ["light", "dark"], "modes": ["simple", "advanced"]}
