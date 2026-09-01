"""Every finding status must land in exactly one section of the round summary.

FOUND BY THE AGENT-MODE SIMULATED RUN, 2026-08-30 — the first time that mode had
ever been run. `build_summary` partitions findings into three lists:

    full_detail_statuses  compact_statuses  hidden_statuses

and **CORROBORATED, ESCALATED and WITHHELD were in none of them**. A finding in
any of those was dropped from the round summary entirely: not shown, not
compacted, not even counted in `hidden_count`. The panel simply never saw it.

CORROBORATED is the founder's own Bugzilla split of 21 August 2026 — "CORROBORATED
(model-attested, scheduling only) vs CONFIRMED (tool re-executed the falsifier)".
It was added to the vocabulary and this function was never updated, so every
corroborated finding has been invisible to the panel since that split landed.

The symptom that exposed it: an EXTENSION line was rendered onto C0001 and never
reached the round prompt, because C0001 was CORROBORATED.
"""
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R   # noqa: E402


def _partition():
    """The three tuples as literals, read from the source."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "build_summary")
    out = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id.endswith("_statuses"):
                try:
                    out[t.id] = set(ast.literal_eval(node.value))
                except (ValueError, SyntaxError):
                    pass
    return out


def test_the_three_lists_are_all_present():
    p = _partition()
    assert set(p) == {"full_detail_statuses", "compact_statuses", "hidden_statuses"}, p


def test_every_status_in_the_vocabulary_is_covered():
    """The bare fact that was false, silently, for weeks."""
    p = _partition()
    covered = set().union(*p.values())
    missing = sorted(set(R.FINDING_STATUS_VOCABULARY) - covered)
    assert not missing, (
        f"{missing} appear in the status vocabulary and in NONE of the summary "
        f"sections, so a finding in any of them is invisible to the panel")


def test_the_lists_do_not_overlap():
    """A status in two sections would be rendered twice."""
    p = _partition()
    names = list(p)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            both = p[a] & p[b]
            assert not both, f"{sorted(both)} appear in both {a} and {b}"


def test_corroborated_gets_full_detail_not_compact():
    """It is an ACTIVE finding the panel can still act on, and its rejection
    lines — which include EXTENSION notices — are only rendered in full detail."""
    p = _partition()
    assert "CORROBORATED" in p["full_detail_statuses"], (
        "CORROBORATED is not in full detail, so its rejection lines — including "
        "EXTENSION notices — never reach the panel")


def test_a_corroborated_finding_reaches_the_round_prompt():
    """Behavioural, not structural: register one and look for it."""
    reg = R.FindingRegistry()
    cid = reg.register(R.Finding(
        finding_id="F001", model_id="SIM-A", round_idx=0, flaw_class=3,
        severity=0.9, abstraction_index=0.5, description="a corroborated finding",
        proposed_fix="", falsifier_code=""), "SIM-A")
    reg.entries[cid]["status"] = "CORROBORATED"
    summary = reg.build_summary(1)
    assert cid in summary, "a CORROBORATED finding is absent from the round summary"
