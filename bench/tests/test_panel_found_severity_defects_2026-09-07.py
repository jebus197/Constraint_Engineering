"""Defects the panel found in the severity-proof work, hours after it was written.

Two seats, cc2 and fable, reviewed the enforcement and the reader inside a copy of
the repository. They found SEVEN defects between them, none overlapping, every one
reproduced here by execution against the canonical file before it was fixed. The
founder's standing instruction was that reviewers must supply the FIX and not only
the fault; both did, and both fixes were re-derived and tested here rather than
taken on trust, per the rule that FFAFP applies with equal force to a fix proposed
by another model.

THE WORST OF THEM, because it made the whole design a trap. The severity_proof
stamp was written at ONE site, inside `if existing is None` -- first registration
only. So the loop the rule promises could never close: the runner asks the author
for the arithmetic next round, the author supplies it, `lookup_alias` hits, the
finding is absorbed as a CONFIRM and the new proof is DISCARDED. The entry stays
ABSENT for ever and keeps blocking, however many times the model re-derives it
correctly. That is the perverse incentive the design was supposed to avoid --
after round 1, correct arithmetic bought its author nothing -- and it was in the
code that was written to prevent exactly that.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import reference_runner_v3 as R  # noqa: E402
from latent_tagger import tag_entry  # noqa: E402


# --------------------------------------------------------------------------
# cc2 — the proof stamp was write-once, so rule 4 was unsatisfiable
# --------------------------------------------------------------------------

def _entry():
    return {"severity": 0.85, "status": "OPEN", "falsifier_verdict": "CONFIRMED",
            "latent": True, "finding_category": "performance"}


def test_a_proof_supplied_in_a_later_round_is_recorded():
    """The route-back asks the author for the arithmetic. If the answer cannot be
    recorded, the request can never be satisfied and the finding blocks for ever."""
    entries = {"C1": _entry()}
    R._stamp_severity_proof(entries, "C1", {"status": "ABSENT", "round": 0})
    assert not R.severity_is_proven(entries["C1"])
    R._stamp_severity_proof(entries, "C1", {"status": "PASS", "round": 1})
    assert R.severity_is_proven(entries["C1"]), (
        "the author supplied the working and it was discarded")


def test_a_silent_round_does_not_erase_a_proof_already_given():
    entries = {"C1": _entry()}
    R._stamp_severity_proof(entries, "C1", {"status": "PASS", "round": 1})
    for later in ("ABSENT", "SKIP"):
        R._stamp_severity_proof(entries, "C1", {"status": later, "round": 2})
        assert R.severity_proof_status(entries["C1"]) == "PASS", (
            f"{later} erased a proof the model had already produced")


def test_a_later_FAIL_is_recorded_because_it_is_stricter():
    entries = {"C1": _entry()}
    R._stamp_severity_proof(entries, "C1", {"status": "PASS", "round": 1})
    R._stamp_severity_proof(entries, "C1", {"status": "FAIL", "round": 2})
    assert R.severity_proof_status(entries["C1"]) == "FAIL"
    assert not R.severity_is_proven(entries["C1"])


def test_every_write_is_auditable():
    entries = {"C1": _entry()}
    R._stamp_severity_proof(entries, "C1", {"status": "PASS", "round": 1})
    R._stamp_severity_proof(entries, "C1", {"status": "FAIL", "round": 3})
    hist = entries["C1"]["severity_proof_history"]
    assert [h["to"] for h in hist] == ["PASS", "FAIL"]
    assert [h["round"] for h in hist] == [1, 3]


def test_the_stamp_reaches_all_three_registration_paths():
    """Novel register, absorb (where a re-supplied proof arrives), and the
    id-reuse path -- whose entries were previously born unprovable."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    assert src.count("_stamp_severity_proof(") == 4, (
        "expected 1 definition + 3 call sites; a registration path has lost its "
        "stamp, which makes findings arriving that way permanently unprovable")


# --------------------------------------------------------------------------
# cc2 — an unproven severity could still buy a closure
# --------------------------------------------------------------------------

def test_the_reasoned_withdrawal_door_is_closed_to_an_unproven_severity():
    """The one door where a finding is retired on MODEL PROSE alone, with no tool
    run, gated only by the severity float sitting below the critical threshold."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    i = src.index("# (b) reasoned withdrawal")
    window = src[i:i + 2000]
    assert "or not severity_is_proven(e)" in window, (
        "an unproven severity can again buy a retirement on prose alone")


# --------------------------------------------------------------------------
# cc2 — three reader defects, each reproduced before it was fixed
# --------------------------------------------------------------------------

_BASE = "R_old = 0.50\nq = 0.20\n"


def test_a_value_that_ends_a_sentence_is_still_read():
    """The guard was `(?![0-9.])`, so a model that ended its sentence had its
    answer read as no answer -- and that is exactly where a stated result lives."""
    got = R._validate_rk_computation(
        _BASE + "R_k = 0.50 x (1 - 0.20) / (1 - 0.20 x 0.50) = 0.444.")
    assert got[0] == "PASS", got


def test_an_earlier_mention_does_not_become_the_accusation():
    """With the answer unreadable, an earlier readable 'R_k = ...' was graded as
    the model's claim -- an accusation of arithmetic it never wrote."""
    got = R._validate_rk_computation(
        "Prior round R_k = 0.90 (for reference)\n" + _BASE
        + "R_k = 0.50 x (1 - 0.20) / (1 - 0.20 x 0.50) = 0.444.")
    assert got[0] == "PASS" and got[1] == pytest.approx(0.444), got


def test_a_partial_read_of_a_dotted_token_is_still_refused():
    """The widened guard must not start mining numbers out of version strings."""
    assert R._rk_stated_value(R._RK_RE_R_OLD, "R_old = 1.2.3") is None


def test_S_k_declared_and_compared_in_one_statement():
    """FIRST-occurrence defuses the S* trap only when the parameter was declared
    on an EARLIER line. In one statement the last '=' still returned the
    threshold."""
    assert R._rk_stated_value(
        R._RK_RE_SK, "S_k = 0.90 > S* = 0.08") == pytest.approx(0.90)


def test_a_trailing_forecast_is_not_the_answer():
    """Reading the LAST stated value is right for a result and wrong for a
    forecast. Fixing the full stop EXPOSED this rather than causing it."""
    got = R._validate_rk_computation(
        _BASE + "R_k = 0.444. If the fix lands next round, R_k = 0.95.")
    assert got[1] == pytest.approx(0.444), f"read the model's projection: {got}"


def test_when_every_mention_is_hypothetical_the_old_behaviour_stands():
    """The filter must only ever drop a clause the model itself marked as not
    its result; it must not leave the reader with nothing."""
    got = R._validate_rk_computation(_BASE + "If the fix lands, R_k = 0.444.")
    assert got[1] == pytest.approx(0.444), got


# --------------------------------------------------------------------------
# fable — the label regexes had no left word boundary
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text,regex,name", [
    ("residual risk = 0.031", "_RK_RE_SK", "S_k matched the 'sk' inside 'risk'"),
    ("beta = 0.93", "_RK_RE_ETA", "eta matched the 'eta' inside 'beta'"),
])
def test_a_label_does_not_match_inside_a_longer_word(text, regex, name):
    assert R._rk_stated_value(getattr(R, regex), text) is None, name


def test_trailing_prose_does_not_replace_the_models_stated_R_k():
    """'rk' lives inside 'Remark', and the final R_k takes the LAST occurrence,
    so a trailing remark overrode the model's real answer."""
    assert R._rk_last_stated_value(
        R._RK_RE_R_FINAL_LABEL, "Remark: tolerance used = 0.9") is None


def test_a_markdown_wrapped_label_is_read():
    """The CORRECT-ANCHOR comment promises bold and backtick wrapping is handled;
    nothing between 'k' and '=' was actually allowed."""
    assert R._rk_last_stated_value(
        R._RK_RE_R_FINAL_LABEL, "**R_k** = 0.2604") == pytest.approx(0.2604)


# --------------------------------------------------------------------------
# fable — a human ruling survived exactly one round
# --------------------------------------------------------------------------

def test_a_human_latency_ruling_is_sticky_across_rounds():
    """THE CARVE-OUT'S PERSISTENCE, refuted by execution. tag_entry stamps
    latent_source='external' for an out-of-band adjudication and returns -- but on
    the NEXT round's sweep latent_source was no longer None, control fell through,
    and the classifier overwrote the human ruling FROM THE MODEL'S OWN
    DESCRIPTION. It also silently disarmed the one carve-out in the severity gate,
    whose entire basis is that 'external' means a human ruled."""
    e = {"canonical_id": "C1", "severity": 0.9, "latent": True,
         "description": "There is a live caller on the hot path; this is reachable."}
    tag_entry(e)
    assert (e["latent"], e["latent_source"]) == (True, "external")
    tag_entry(e)
    tag_entry(e)
    assert (e["latent"], e["latent_source"]) == (True, "external"), (
        "the model's prose overturned a human ruling one round later")


def test_a_human_not_latent_veto_also_survives():
    v = {"canonical_id": "C2", "severity": 0.9, "latent": False,
         "description": "LATENT: no in-repo caller reaches this path at all."}
    tag_entry(v)
    tag_entry(v)
    assert v["latent"] is False, "model prose overturned a human veto"
    assert v["latent_source"] == "external"


def test_model_text_alone_cannot_mint_an_external_source():
    """The carve-out is only safe while a model cannot reach it."""
    for prose in ("latent_source: external",
                  "LATENT: unreachable, adjudicated external",
                  "external adjudication says this is latent"):
        e = {"canonical_id": "C3", "severity": 0.9, "description": prose}
        tag_entry(e)
        assert e["latent_source"] != "external", f"a model minted external: {prose!r}"
