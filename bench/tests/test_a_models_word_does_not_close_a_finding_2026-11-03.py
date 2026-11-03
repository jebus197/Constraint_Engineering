"""A model's own VERIFIED flag must not carry its finding to CLOSED.

THE DEFECT, FOUND 2026-11-03 while answering a question about which of the
ticket store's lessons the harness finding registry still needs. The first
answer said the registry already had the ticket store's terminal-state rule,
because `grep` found 10 lines in the canonical runner mentioning CLOSED and
`verified`. Every one of those 10 was a docstring, a report string or a comment.
Executing the code said the opposite.

THE CHAIN. `runner_core.parse_findings` reads a `VERIFIED` key out of the
model's own reply JSON and sets `Finding.verified` from it, accepting the
boolean `true` and the string "TRUE" alike. `FindingRegistry.register` copies
that field into the entry, and `mark_verified` carries it again. The
CONFIRMED/CORROBORATED -> CLOSED transition then fired on the flag alone and
recorded `adjudicator="tool"` with `evidence="verified fix, no unresolved
challenges"`.

WHY IT IS WORSE THAN A MISLABEL. The project's standing correction is that
findings are confirmed programmatically or by a human, with no model voting, and
the status machine ENFORCES that for CONFIRMED -- entry C0010 of
commissioning_arm1_panel_20260921T215405Z carries a `refused_transitions` row
showing a model's CONFIRMED request refused and substituted with CORROBORATED.
The flag then closed that same entry, which is the stronger claim. The bolt was
on one door.

MEASURED: 34 of 412 closures whose mechanism is `verified_flag` had neither a
CONFIRMED falsifier nor a bugzilla verification, across 15 of 76 archived runs,
the newest dated 20261102T004713Z. 26 carry fix_efficacy
NOT_PROBED_NO_FALSIFIER; 6 carry FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER, meaning
the runner had already measured that the fix fails its own test and the entry
closed anyway. Producer:
`scripts/a_models_own_verified_flag_closes_it_2026-11-03.py`.

THE FIX IS A PRECONDITION, NOT A REMOVAL. The transition now also requires the
flag to be backed by an execution, which every legitimate setter in the runner
already leaves behind, so it stops 0 real closures and 378 of the 412 above are
unaffected.

WHAT THIS FILE DELIBERATELY DOES NOT ASSERT. It does not pin the parser's
current behaviour. Whether the parser should read `VERIFIED` from a model reply
at all is an open question for the founder, because the same field feeds `v_bar`
in `bench/dm/_manager.py` and therefore allocation. These tests are written so
that they pass whichever way he rules: they assert that the GATE holds even when
the flag is present, not that the flag is or is not set upstream.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
LOGS = REPO / "bench" / "logs"

SIBLINGS = ("bench/reference_runner.py", "bench/run_exp35_policy_engine.py",
            "bench/run_exp36_evidence.py", "bench/run_exp37_evidence.py")


@pytest.fixture(scope="module")
def rr3():
    sys.path.insert(0, str(REPO / "bench"))
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("_rr3_guard", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rr3_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class _Cfg:
    """Every flag off, but `models` is a real roster.

    `_update_finding_statuses` computes an external panel size from
    `cfg.models`, so a stub returning False for everything raises TypeError on
    the CORROBORATED path -- a failure of the stub, not of the code under test.
    3 seats is enough for the panel-size arithmetic to be meaningful without
    standing in for any real model, and the names follow the project's rule
    that a simulated seat never wears a vendor's name.
    """

    models = ("SIM-A", "SIM-B", "SIM-C")

    def __getattr__(self, _n):
        return False


def _entry(**kw):
    e = {"canonical_id": "C0001", "status": "CONFIRMED", "verdicts": [],
         "severity": 0.7, "description": "d", "proposed_fix": "",
         "falsifier_code": "", "falsifier_verdict": "", "verified": True,
         "escalated": False, "origin_type": "model", "open_since_round": 0,
         "last_status_change_round": 0, "source_model": "SIM-A",
         "flaw_class": 1, "source_aliases": []}
    e.update(kw)
    return e


def _run(rr3, **kw):
    reg = rr3.FindingRegistry()
    reg.entries["C0001"] = _entry(**kw)
    rr3._update_finding_statuses(reg, 1, _Cfg())
    return reg.entries["C0001"]


class TestTheModelsWordAloneDoesNotClose:
    def test_an_unbacked_verified_flag_does_not_close(self, rr3):
        """THE FIX. `verified` True with no execution behind it must leave the
        entry where it is, not carry it to the terminal state."""
        e = _run(rr3)
        assert e["status"] != "CLOSED", (
            "a finding closed on the model's own VERIFIED flag, with no "
            f"falsifier verdict and no bugzilla verification: {e['status']}")
        assert e["status"] == "CONFIRMED", (
            f"the entry should stay CONFIRMED, not move to {e['status']}")

    def test_a_corroborated_entry_is_equally_refused(self, rr3):
        """CORROBORATED is the status the no-model-voting rule SUBSTITUTES when
        a model asks for CONFIRMED, so it is the exact state the archived
        defect was found in."""
        e = _run(rr3, status="CORROBORATED")
        assert e["status"] != "CLOSED", (
            "a CORROBORATED finding closed on the model's own flag; this is "
            "the shape of archived entry C0010")

    def test_the_string_form_of_the_claim_is_also_refused(self, rr3):
        """The parser accepts the string "TRUE" as well as the boolean, so a
        truthy non-boolean must not sneak past either."""
        e = _run(rr3, verified="TRUE")
        assert e["status"] != "CLOSED", (
            "a truthy non-boolean `verified` closed the finding")


class TestExecutionBackedClosuresStillHappen:
    """ANTI-VACUITY. Without these, the fix could be a blanket refusal to
    close anything and the suite above would still pass."""

    def test_a_confirmed_falsifier_still_closes(self, rr3):
        e = _run(rr3, falsifier_verdict="CONFIRMED")
        assert e["status"] == "CLOSED", (
            "an execution-backed finding no longer closes, so the fix has "
            f"disabled the close path rather than guarded it: {e['status']}")
        assert e.get("status_mechanism") == "verified_flag"

    def test_a_bugzilla_verification_still_closes(self, rr3):
        e = _run(rr3, bugzilla_verified=True)
        assert e["status"] == "CLOSED", (
            f"the bugzilla close-the-loop path no longer closes: {e['status']}")
        assert e.get("status_mechanism") == "bugzilla_close_loop"

    def test_a_voided_instrument_still_does_not_close(self, rr3):
        """The 2026-10-03 control must survive the new conjunct: a falsifier
        that ran and was shown not to discriminate is not a verification."""
        e = _run(rr3, falsifier_verdict="NON_DISCRIMINATING")
        assert e["status"] != "CLOSED"


class TestTheArchiveFigureIsRecomputed:
    """The numbers in the fix's comment may not outlive their evidence."""

    def test_the_unbacked_closure_count_is_still_what_the_comment_says(self):
        if not LOGS.is_dir():
            pytest.skip("the log archive is not present here")
        total = unbacked = 0
        for rep in sorted(LOGS.glob("*/*_report.json")):
            if "sandbox_harvest" in str(rep):
                continue
            try:
                d = json.loads(rep.read_text(errors="replace"))
            except Exception:                              # noqa: BLE001
                continue
            ents = ((d.get("registry") or {}).get("entries")) or {}
            if not isinstance(ents, dict):
                continue
            for e in ents.values():
                if not isinstance(e, dict):
                    continue
                if e.get("status") != "CLOSED":
                    continue
                if e.get("status_mechanism") != "verified_flag":
                    continue
                total += 1
                if not (e.get("falsifier_verdict") == "CONFIRMED"
                        or e.get("bugzilla_verified")):
                    unbacked += 1
        if total == 0:
            pytest.skip("no archived closure uses the verified_flag mechanism")
        assert (unbacked, total) == (34, 412), (
            f"the archive now shows {unbacked} of {total} unbacked closures, "
            f"not 34 of 412. If a new run added one, the fix is not holding; "
            f"if the archive changed, update the comment at the CLOSED "
            f"transition and this test together.")


class TestWhyTheFixWasNotFoldedBack:
    """A RATCHET ON THE FOLD-BACK QUESTION, which is the founder's to settle.

    The same gate sits in 4 other runners. None of them writes
    `falsifier_verdict` at all, so applying this conjunct there would make
    their close path unreachable -- disabling a feature rather than fixing one.
    If any of them later gains an execution path, the fold-back question
    becomes live and this test says so instead of letting it pass unnoticed.
    """

    @pytest.mark.parametrize("rel", SIBLINGS)
    def test_a_sibling_without_an_execution_path_is_left_alone(self, rel):
        f = REPO / rel
        if not f.is_file():
            pytest.skip(f"{rel} is not present")
        tree = ast.parse(f.read_text(errors="replace"))
        writes = sum(1 for n in ast.walk(tree)
                     if isinstance(n, ast.Assign)
                     and "'falsifier_verdict'" in ast.dump(n))
        assert writes == 0, (
            f"{rel} now writes `falsifier_verdict` in {writes} place(s), so it "
            f"HAS an execution path and the CLOSED gate there can and should "
            f"carry the same precondition as reference_runner_v3. This is the "
            f"fold-back decision recorded as the founder's; it is now live.")
