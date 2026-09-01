"""EXTEND must be READ. It was the only parsed verdict that nothing consumed.

FOUNDER RULING, the Bugzilla question, 21 August 2026:

    "EXTEND is the answer to 'ledger vs instrument.' Parsed, offered as the
     explicit alternative to duplicating, used 183-543 times, READ BY NOTHING.
     Make it carry a falsifier: still-fires-after-the-parent-fix means the parent
     fix is demonstrably insufficient and the system names what it misses."

And again on 30 August: merge should function as specified, "but preceding/
redundant fixes should be RECORDED, not simply discarded."

MEASURED 2026-08-30, nine days after the ruling. Of the five verdict types models
are instructed to emit, EXTEND was the ONLY one with zero consuming comparisons:

    CONFIRM 9 | CHALLENGE 6 | MERGE 3 | REOPEN 1 | EXTEND 0

209 EXTEND verdicts sit in the archive across 15 runs. Not one had ever
influenced anything or reached a human.
"""
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

SRC = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
TREE = ast.parse(SRC)


def _fn(name):
    return next(n for n in ast.walk(TREE)
                if isinstance(n, ast.FunctionDef) and n.name == name)


def _body(name: str) -> str:
    """Unparsed source with quotes normalised.

    `ast.unparse` rewrites double quotes as single quotes, so an assertion
    written against the source text never matches the unparsed body. An earlier
    version of this file failed against correct code for exactly that reason.
    """
    return ast.unparse(_fn(name)).replace('"', "'")


def test_extend_has_a_consuming_comparison_at_all():
    """The bare fact that was false for nine days."""
    n = SRC.count('== "EXTEND"')
    assert n >= 1, "EXTEND is parsed and offered to models and still read by nothing"


def test_extensions_are_recorded_on_the_parent_entry():
    body = _body("_update_finding_statuses")
    assert "v['verdict'] == 'EXTEND'" in body, "extensions are not collected"
    assert "'extensions'" in body, "extensions are collected and then discarded"


def test_every_parsed_verdict_type_is_now_consumed():
    """The general form. A verdict a model is TOLD to emit and that nothing reads
    is a promise the schema does not keep."""
    kinds = ("CONFIRM", "CHALLENGE", "EXTEND", "MERGE", "REOPEN")
    unread = [k for k in kinds if SRC.count(f'== "{k}"') == 0]
    assert not unread, f"verdict types parsed, offered to models, and read by nothing: {unread}"


def test_extensions_reach_the_owning_model():
    """Recorded where only a report can see them is halfway. The model that owns
    the finding is the one who can act on a named consequence."""
    body = _body("_rejection_lines")
    assert "EXTENSION(S) FILED AGAINST THIS FINDING" in body
    assert "entry.get('extensions')" in body


def test_extensions_reach_a_human_via_the_report():
    assert '"extension_count": e.get("extension_count", 0)' in SRC
    assert '"extensions": e.get("extensions", [])' in SRC


def test_extend_cannot_gate_anything():
    """Contributory, like rho and the fix-efficacy probe. An extension names a
    consequence; it is evidence ABOUT a finding, not a vote on it."""
    for gate in ("_evaluate_gate_conditions", "_check_gamma_alt_convergence"):
        body = ast.unparse(_fn(gate))
        assert "extension" not in body.lower(), (
            f"{gate} references extensions; they must not be able to gate")


def test_extensions_do_not_change_a_status():
    body = _body("_update_finding_statuses")
    i = body.index("v['verdict'] == 'EXTEND'")
    seg = body[i:i + 700]
    for forbidden in ("registry.resolve", "resolve(", "UNCONFIRMED", "MERGED"):
        assert forbidden not in seg, (
            f"the extension block touches {forbidden}; it must record, not decide")
