"""Task 2.3: falsifiers that are MISREAD rather than missing.

Task 2.2 covered findings with no falsifier. This is the other half: a falsifier
that ran, produced a verdict, and had that verdict read as something it is not.

THE INVARIANT. `falsifier_verdict == "ERROR"` means the test did not run to a
verdict -- a broken import, a syntax error, a setup guard firing. This project's
own record is explicit that "an errored leg is an equipment failure, not a
verdict", and `reference_runner_v3.py:11429` tells the model exactly that: "It
demonstrated nothing." So an entry may not carry `verified: True` on the strength
of an ERROR unless some OTHER instrument demonstrated it.

MEASURED across every post-mechanism archive: 4 of the 583 findings that carry a
falsifier have `verdict == ERROR`, `verified == True`, and no second instrument.
0.6861%, Wilson [0.2671%, 1.7507%], Clopper-Pearson [0.1872%, 1.7473%].

FOUR THINGS KEEP THIS IN PROPORTION, and leaving any of them out would overstate
it.

1. ALL 4 ARE `escalated: True`. They went to the human queue. The system did not
   silently accept them.
2. ONLY 1 REACHED `CLOSED` -- exp42 C0046. The other 3 are OPEN or UNCONFIRMED.
3. FOR 2 OF THEM THE UNDERLYING FINDING IS DEMONSTRABLY TRUE. exp55 C0003 and
   C0010 are the CT-01 and CT-02 defects, proved independently in
   `test_falsifier_exp55_control_claims_2026-09-10.py` with SymPy, NumPy, mpmath
   and pint. Their `verified` flag is right in substance and unearned in
   provenance, which is a different complaint from being wrong.
4. THE SECOND INSTRUMENT WORKS WHERE IT EXISTS. exp47 C0055 has an ERRORed
   falsifier AND `bugzilla_verified: True` -- the closed loop applied the fix and
   re-ran the test. It is correctly closed and is NOT in the population. A first
   pass of this measurement counted it as a misread; checking for the second
   instrument removed it.

SO THE DEFECT IS A LABEL, NOT A DECISION. `verified` is supposed to mean an
instrument demonstrated the finding. In these 4 nothing did.

THIS IS A RATCHET, NOT A BAR. The 4 archived cases are recorded by name and
allowed; anything NEW fails. Archives cannot be rewritten -- and should not be,
since they are the record of what happened -- so the only useful guard is one
that stops the population growing.
"""
from __future__ import annotations

import glob
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

#: The falsifier mechanism's build date. Earlier runs carry no falsifiers.
MECHANISM_BUILT = "20260603"

#: The 4 known cases, by (run, canonical_id), with why each is tolerated.
KNOWN = {
    ("exp42_composer_20260606T202037Z", "C0032"):
        "DeepSeek 0.80, OPEN, escalated; the bugzilla loop did not exist yet",
    ("exp42_composer_20260606T202037Z", "C0046"):
        "Gemini 0.85, the only one that reached CLOSED; escalated",
    ("exp55_v3_control_20260823T144624Z", "C0003"):
        "Codex 0.82, UNCONFIRMED, escalated; CT-01, independently proved true",
    ("exp55_v3_control_20260823T144624Z", "C0010"):
        "CC2 0.85, UNCONFIRMED, escalated; CT-02, independently proved true",
}


def _runs():
    for r in sorted(glob.glob(str(ROOT / "bench" / "logs" / "exp*" / "runner_state.json"))):
        name = pathlib.Path(r).parent.name
        stamp = next((t[:8] for t in name.split("_")
                      if t[:2] == "20" and len(t) >= 8), "0")
        if stamp < MECHANISM_BUILT:
            continue
        try:
            s = json.loads(pathlib.Path(r).read_text())
        except (ValueError, OSError):
            continue
        reg = s.get("registry", {})
        ent = reg.get("entries", reg) if isinstance(reg, dict) else reg
        vals = [v for v in (ent.values() if isinstance(ent, dict) else ent)
                if isinstance(v, dict)]
        yield name, vals


def _misreads():
    out = []
    for name, vals in _runs():
        for v in vals:
            if (v.get("falsifier_verdict") == "ERROR"
                    and v.get("verified") is True
                    and not any(k.startswith("bugzilla") for k in v)):
                out.append((name, v.get("canonical_id"), v))
    return out


class TestTheInvariantHolds:
    def test_no_new_errored_falsifier_is_read_as_verification(self):
        found = {(r, c) for r, c, _v in _misreads()}
        new = found - set(KNOWN)
        assert not new, (
            f"an ERRORed falsifier is being read as verification in a run not on "
            f"the known list: {sorted(new)}. An errored leg is an equipment "
            f"failure, not a verdict.")

    def test_the_known_population_has_not_grown(self):
        found = _misreads()
        assert len(found) == len(KNOWN), (
            f"{len(found)} cases against the {len(KNOWN)} recorded; the ratchet "
            f"has slipped")

    def test_the_rate_is_still_small_and_carries_an_interval(self):
        with_falsifier = sum(
            1 for _n, vals in _runs() for v in vals
            if (v.get("falsifier_code") or "").strip())
        assert with_falsifier > 400, with_falsifier
        from statsmodels.stats.proportion import proportion_confint
        k = len(_misreads())
        lo, hi = proportion_confint(k, with_falsifier, method="wilson")
        lo_c, hi_c = proportion_confint(k, with_falsifier, method="beta")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, k, with_falsifier - k + 1) if k else 0.0
        assert abs(slo - lo_c) < 1e-9, "statsmodels and scipy disagree"
        assert hi < 0.05, (lo, hi)


class TestTheProportionIsKeptHonest:
    def test_every_known_case_was_escalated_to_a_human(self):
        """The system did not silently accept any of them."""
        for _r, _c, v in _misreads():
            assert v.get("escalated") is True, (
                f"{_r} {_c} was NOT escalated, so it really was accepted "
                f"silently and the finding is worse than recorded")

    def test_only_one_ever_reached_closed(self):
        closed = [(r, c) for r, c, v in _misreads() if v.get("status") == "CLOSED"]
        assert len(closed) == 1, f"{len(closed)} reached CLOSED, not 1: {closed}"

    def test_the_second_instrument_removes_a_case_when_it_exists(self):
        """exp47 C0055: ERRORed falsifier AND bugzilla_verified. Correctly closed.

        Without this the measurement would have counted it, and the population
        would read 5 instead of 4. Checking for the second instrument is what
        makes the number a measurement rather than a grep.
        """
        p = (ROOT / "bench" / "logs"
             / "exp47_divergence_locationkey_live_20260728T230026Z"
             / "runner_state.json")
        if not p.is_file():
            pytest.skip("the exp47 archive is not in this clone")
        reg = json.loads(p.read_text())["registry"]
        ent = reg.get("entries", reg)
        v = {x.get("canonical_id"): x
             for x in (ent.values() if isinstance(ent, dict) else ent)
             if isinstance(x, dict)}["C0055"]
        assert v.get("falsifier_verdict") == "ERROR"
        assert v.get("bugzilla_verified") is True, (
            "C0055 no longer carries a second instrument, so it belongs in the "
            "misread population after all")


class TestTheRunnerStillTellsTheModelTheTruth:
    def test_an_error_verdict_says_it_demonstrated_nothing(self):
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        # ASSERTED IN FRAGMENTS, because the sentence WRAPS in the source and a
        # search for the joined phrase fails on text that is present. The first
        # version of this assertion looked for "It demonstrated nothing" and went
        # red against a runner that says exactly that, across a line break --
        # the same grep-the-source trap this file's subject is a cousin of.
        assert "FALSIFIER ERROR:" in src, (
            "the runner no longer labels an errored falsifier at all")
        assert "demonstrated nothing" in src, (
            "the runner no longer tells a model that an errored falsifier "
            "demonstrated nothing, which is where this invariant is taught")
        assert "did not run to a verdict" in src
