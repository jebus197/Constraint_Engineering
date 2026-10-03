#!/usr/bin/env python3
"""A finding may not claim tool verification on an instrument already voided.

THE DEFECT, with its live instance. `shakedown_2026-09-29/arm1_harvest/C0041`
stands at status CONFIRMED with `verified=true` and severity 0.8 while its
`falsifier_verdict` is `NON_DISCRIMINATING` -- the discrimination control had
already voided the falsifier, and the source model had withdrawn the claim. The
star-round seat that found it reported it without changing it, which was right:
the blocking question is the founder's.

THE MECHANISM, and it is 2 lines apart in one function. The control's applier
sets `entry["verified"] = False` when it voids an instrument. The gate that
called it then ran `registry.resolve(cid, "CONFIRMED", round_idx)` and
`e["verified"] = True` unconditionally, overwriting the correction.

CORRECTING THE FLAG IS THE RULING HE DEFERRED, AND THE PROJECT'S OWN SUITE
PROVED IT. The first version of this fix set `verified = False` on a voided
instrument, reasoning that the halt bound cannot see the flag --
`unverified_critical_count` skips any entry whose status is not UNCONFIRMED and
never reads it -- so the correction looked free. True about the halt bound,
wrong about the consequence: `test_discrimination_control.py` states the
mechanism in its own words, "verified=True is what lets
_update_finding_statuses close it next round; withholding it is what keeps the
finding out of CLOSED". Withholding the flag IS the blocking behaviour. Two
committed oracles went red -- the default must leave the verdict untouched, and
the flag must be the ONLY difference between armed and unarmed -- so the first
version had armed `discrimination_control_blocks` by the back door, the exact
ruling the founder deferred and the one refused an hour earlier on his own
126-of-246 measurement.

WHAT IS LEFT, AND IT CHANGES NO OUTCOME. The record now SAYS the verification
was voided. No decision reads `verification_voided`; it exists so that a reader,
and any later measurement of the tool-verification contract, can tell C0041's
record from an honest one -- which nothing in the entry allowed before.
Exposure, by `scripts/verified_on_a_voided_instrument_2026-10-03.py`: 13 of 3208
archived entries carry NON_DISCRIMINATING, 0.4052%, Wilson [0.237%, 0.6921%];
all 13 carried `verified=true` and a terminal status; 12 were already CLOSED
below critical severity and exactly 1 is a critical.

THE DECISION ITSELF REMAINS THE FOUNDER'S, which is where the star-round seat
left it and where it belongs.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RUNNER = REPO / "bench" / "reference_runner_v3.py"


def _gate_source() -> str:
    """The record-only branch of the falsifier gate, isolated.

    Bounded by the next branch of the same `if`, not by a character count: a
    fixed window silently cut the branch in half once already and made an
    assertion about text that was simply outside it.
    """
    src = RUNNER.read_text(encoding="utf-8")
    i = src.index("disc: {cid} did not discriminate")
    j = src.index('elif verdict == "REFUTED" and not is_critical:', i)
    assert j > i, "the record-only branch could not be delimited"
    return src[i:j]


def test_the_default_still_leaves_the_verdict_untouched():
    """THE GUARD AGAINST MY OWN FIRST FIX, which armed the blocker by accident.

    If `verified` is ever withheld in this branch again, the record-only
    default silently becomes the blocking default.
    """
    block = _gate_source()
    assert 'e["verified"] = True' in block, (
        "the record-only branch no longer marks the finding verified, so "
        "recording an observation has changed an outcome -- which is the "
        "founder's deferred blocking ruling, taken by wiring")
    assert 'e["verified"] = False' not in block, (
        "`verified` is withheld in the record-only branch, which IS the "
        "blocking behaviour by the project's own description of it")


def test_the_voided_case_records_why():
    block = _gate_source()
    assert 'e["verification_voided"] = True' in block, (
        "nothing marks the record as voided, so a reader cannot tell a "
        "finding standing on a voided instrument from an honest one")
    assert "verification_voided_reason" in block, (
        "the void carries no reason a human can act on")
    assert "founder's open decision" in block, (
        "the record does not say that acting on this is his ruling, so a "
        "later reader could take the silence for a settled design")


def test_the_halt_bound_still_cannot_see_the_flag():
    """Retained because it is TRUE and was not SUFFICIENT.

    The halt bound genuinely does not read `verified` -- and that was the whole
    of the first fix's justification, which the CLOSED transition then
    falsified. The assertion is kept so the record shows what was verified and
    what it did not cover.
    """
    src = RUNNER.read_text(encoding="utf-8")
    i = src.index("def unverified_critical_count")
    body = src[i:src.index("\n    def ", i + 10)]
    assert 'get("verified")' not in body and '["verified"]' not in body, (
        "the halt bound now reads `verified`, so withholding it on a voided "
        "instrument changes convergence -- which is the founder's open "
        "decision, not a wiring choice")
    assert 'e.get("status") != "UNCONFIRMED"' in body, (
        "the halt bound no longer keys on UNCONFIRMED, so the reasoning that "
        "this fix cannot move it no longer holds")


def test_both_readers_of_the_flag_still_exist():
    """These are the 2 readers that made withholding the flag a BLOCK.

    Named here so the reasoning is auditable: the CLOSED transition requires
    `verified`, and the Bugzilla close-the-loop path requires NOT `verified`.
    Either one firing differently is an outcome change, which is why the flag
    is left alone.
    """
    src = RUNNER.read_text(encoding="utf-8")
    assert 'and entry.get("verified")):' in src, (
        "the CLOSED transition no longer requires `verified`")
    assert 'and not entry.get("verified")' in src, (
        "the Bugzilla close-the-loop path no longer keys on NOT verified")


def test_the_archive_instance_is_still_the_one_measured():
    """ANTI-DRIFT. If the population grows, the measured argument needs redoing.

    The justification for acting without the founder is that exactly 1 of the
    affected archived entries is a critical. That is a fact about the archive
    and it can change.
    """
    import json
    voided_critical = []
    for f in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            if (e.get("falsifier_verdict") or "") != "NON_DISCRIMINATING":
                continue
            if e.get("verified") is True and (e.get("severity") or 0) >= 0.7:
                voided_critical.append(f"{f.parent.name}/{cid}")
    assert len(voided_critical) <= 1, (
        f"{len(voided_critical)} archived CRITICAL findings now claim "
        f"verification on a voided instrument ({voided_critical}); the "
        "measurement put in front of the founder said 1, so the figure he is "
        "deciding on has gone stale")
