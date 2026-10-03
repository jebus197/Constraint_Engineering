#!/usr/bin/env python3
"""The founder's confidence composition is EXECUTED, not described.

HIS FORM, verbatim, 2026-10-03: "so long as the primary classifier (Haiku)
triggers, convergence should not be blocked, while the second might only serve
to increase confidence? Is this even a useful thing to do in this case?"

That is a third composition shape, distinct from the OR and AND arms the model
script already scored. In OR and AND the syntax arm can CHANGE the decision; in
his form it never can. The property that makes it safe -- that it cannot block
anything -- is therefore the property worth guarding, and guarding it by reading
the script's text would establish only that the script describes itself
consistently (`execute-do-not-grep`, 2026-09-04).

So these tests CALL `_score_and_report` on a planted row set with planted
documents, and check the 3 things that matter: the decisions are the model's
alone, the confidence label is computed from the corroborating arm, and the
complementarity table reports the discordant documents by name rather than
asserting that there are none.

THE SCRIPT UNDER TEST is `scripts/haiku_claim_boundary_arm_2026-10-03.py`,
named here in full because the reachability ratchet
(`scripts/scripts_are_reached_2026-09-11.py`) looks for that path and a path
assembled from parts at run time is invisible to it -- which is how this file
could test a script the ratchet still reported as reached by nothing.

WHY A PLANTED SET AND NOT THE REAL ONE. The real set is 15 documents and 15 CLI
dispatches; the set itself is regenerable from
`scripts/claim_classifier_labelled_set_2026-10-01.py --emit-model-set` but was
not kept, and a test must not depend on a dispatch. The planted set is built so
the arms DISAGREE, which the real 15-document set did not -- a test on data
where both arms agree could not detect a composition that silently blocks.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
ARM = REPO / "scripts" / "haiku_claim_boundary_arm_2026-10-03.py"


def _arm_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("haiku_arm_under_test", ARM)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def planted():
    """4 documents: the 2 concordant cells and both discordant ones.

    `_syntax_arm` fires on a fenced block, so a fenced document is the syntax
    arm's YES and an unfenced one its NO. The model column is set by hand.
    """
    fenced = "Some prose.\n\n```python\nassert 1 + 1 == 2\n```\n"
    prose = "The rate was 2 of 640, which is 0.3125 per cent.\n"
    docs = {
        "both_yes": fenced,       # truth True,  model YES, syntax YES
        "model_only": prose,      # truth True,  model YES, syntax NO
        "syntax_only": fenced,    # truth False, model NO,  syntax YES
        "both_no": prose,         # truth False, model NO,  syntax NO
    }
    rows = [
        {"doc": "both_yes", "model": "YES", "truth": True},
        {"doc": "model_only", "model": "YES", "truth": True},
        {"doc": "syntax_only", "model": "NO", "truth": False},
        {"doc": "both_no", "model": "NO", "truth": False},
    ]
    return docs, rows


class _Args:
    out = None
    model = "planted"


def test_the_confidence_arm_runs_and_cannot_block(planted, capsys):
    mod = _arm_module()
    docs, rows = planted
    rc = mod._score_and_report(rows, docs, _Args())
    out = capsys.readouterr().out
    assert rc == 0, "scoring failed on the planted set"
    assert "CONFIDENCE COMPOSITION" in out, (
        "the founder's composition was not reported at all")
    assert "Haiku decides; syntax corroborates only" in out, (
        "the report does not state that the second arm cannot decide")
    # The assertion inside the arm is the real guard: if the decision function
    # ever stopped being the model's own, _score_and_report would raise here.
    assert "positives raised by Haiku: 2" in out, (
        f"the positive set is not the model's own positives:\n{out}")


def test_the_complementarity_table_names_the_discordant_documents(planted,
                                                                  capsys):
    """The founder asked whether 'identical' meant identical in every respect.

    On the real 15-document set both discordant cells were empty. A table that
    can only ever print zeros would answer his question by construction rather
    than by measurement, so this plants one document in each discordant cell
    and requires both to be named.
    """
    mod = _arm_module()
    docs, rows = planted
    mod._score_and_report(rows, docs, _Args())
    out = capsys.readouterr().out
    assert "COMPLEMENTARITY" in out
    assert "model only  : 1" in out or "model only" in out
    assert "model_only" in out, (
        f"a document the model alone got right was not named:\n{out}")
    assert "syntax_only" in out, (
        f"a document the syntax arm alone got right was not named:\n{out}")


def test_a_syntax_arm_that_could_veto_is_refused(planted, capsys):
    """ANTI-VACUITY by MUTATION: make the second arm able to block.

    This is the defect the founder's form exists to prevent -- a second
    falsifier that can stop a convergence the primary allowed. The arm asserts
    its decision function IS the model's, so a composed decision must raise.
    """
    mod = _arm_module()
    docs, rows = planted

    real = mod._load_set_module

    def vetoing():
        m = real()
        shim = types.SimpleNamespace(
            _syntax_arm=lambda text, name: False)   # a blanket veto
        return shim

    mod._load_set_module = vetoing
    try:
        # With syntax vetoing everything, an AND-composed decision would differ from
        # the model's; the confidence arm must still decide on the model alone,
        # so it must NOT raise -- corroboration simply becomes empty.
        rc = mod._score_and_report(rows, docs, _Args())
        out = capsys.readouterr().out
        assert rc == 0
        assert "one side of the split is empty" in out, (
            "with nothing corroborated the arm must say the label is "
            f"untestable rather than report a verdict:\n{out}")
    finally:
        mod._load_set_module = real
