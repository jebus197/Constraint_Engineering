#!/usr/bin/env python3
"""The run-end harvest must refuse, not invent, when the data is not there.

WHY THIS GUARD EXISTS, and it is the harvest's own history. The harvest computes
the study measurements that can only come from a finished run. Its round-2
discriminator was FIRST WRITTEN to compare each entry's `corrected_copy` against
the target text as the entry recorded it -- and no such field exists. Entries
carry `corrected_copy_target_sha`, a hash. On real data that version reported
"0 entries in each group", which reads as an absent EFFECT when it was an absent
FIELD. Had it run for the first time at run end, the wrong conclusion was
available and cheap.

So the property worth guarding is not that the harvest produces numbers. It is
that every path which CANNOT produce a number says so, in words that cannot be
mistaken for a result -- and that the one which CAN still fires.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "run_end_study_harvest_2026-10-03.py"


def _run(args: list[str]):
    return subprocess.run([sys.executable, str(SCRIPT)] + args,
                          capture_output=True, text=True, timeout=900)


def test_a_missing_run_is_refused_with_a_nonzero_exit():
    p = _run(["--run", "bench/logs/no_such_run_at_all"])
    assert p.returncode == 1, (
        f"a missing run exited {p.returncode}; a refusal that exits 0 reads as "
        f"a successful harvest of nothing")
    assert "has not written one yet" in (p.stdout + p.stderr)


def test_an_unknown_flag_is_rejected_loudly():
    p = _run(["--run", "x", "--this-flag-does-not-exist"])
    assert p.returncode != 0
    assert "unrecognized arguments" in (p.stdout + p.stderr)


def test_the_discriminator_names_a_data_limit_rather_than_a_verdict(tmp_path):
    """A single round cannot show a trend, and the harvest must say so."""
    run = tmp_path / "planted_run"
    run.mkdir()
    (run / "runner_state.json").write_text(json.dumps(
        {"registry": {"entries": {"C0001": {"falsifier_verdict": "CONFIRMED"}}}}),
        encoding="utf-8")
    (run / "console.log").write_text(
        "[10:00:00] Round 0/7 (blind)\n"
        "[10:00:01]   corrected passage of 50 chars spliced into t.md (1000 chars)\n",
        encoding="utf-8")
    p = _run(["--run", str(run), "--json"])
    assert p.returncode == 0, p.stderr[-400:]
    d = json.loads(p.stdout)
    v = d["round2_discriminator"]["verdict"]
    assert "UNDECIDABLE" in v and "DATA limit" in v, (
        f"a single round produced a verdict instead of a data limit: {v}")


def test_the_discriminator_fires_when_there_IS_enough_data(tmp_path):
    """ANTI-VACUITY: it must be able to return a trend, in both directions."""
    run = tmp_path / "planted_run"
    run.mkdir()
    (run / "runner_state.json").write_text(json.dumps(
        {"registry": {"entries": {"C0001": {"falsifier_verdict": "CONFIRMED"}}}}),
        encoding="utf-8")
    # a STRONG falling trend: the touched fraction shrinks every round
    lines = []
    for rnd, frac in enumerate([(200, 1000), (100, 1000), (40, 1000), (10, 1000)]):
        lines.append(f"[10:0{rnd}:00] Round {rnd}/7 (adaptive)")
        for _ in range(3):
            lines.append(f"[10:0{rnd}:01]   corrected passage of {frac[0]} chars "
                         f"spliced into t.md ({frac[1]} chars)")
    (run / "console.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    p = _run(["--run", str(run), "--json"])
    assert p.returncode == 0, p.stderr[-400:]
    r = json.loads(p.stdout)["round2_discriminator"]
    assert r["splices"] == 12, f"the splice parser missed lines: {r}"
    assert r["spearman_rho_scipy"] < 0, f"a falling trend was not detected: {r}"
    assert "MECHANISM supported" in r["verdict"], (
        f"a strong falling trend did not support MECHANISM: {r['verdict']}")


def test_the_discriminator_can_also_contradict_mechanism(tmp_path):
    """The other direction, so the test is not one-sided."""
    run = tmp_path / "planted_run"
    run.mkdir()
    (run / "runner_state.json").write_text(json.dumps(
        {"registry": {"entries": {"C0001": {}}}}), encoding="utf-8")
    lines = []
    for rnd, frac in enumerate([(10, 1000), (40, 1000), (100, 1000), (200, 1000)]):
        lines.append(f"[10:0{rnd}:00] Round {rnd}/7 (adaptive)")
        for _ in range(3):
            lines.append(f"[10:0{rnd}:01]   corrected passage of {frac[0]} chars "
                         f"spliced into t.md ({frac[1]} chars)")
    (run / "console.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    r = json.loads(_run(["--run", str(run), "--json"]).stdout)["round2_discriminator"]
    assert r["spearman_rho_scipy"] > 0
    assert "MECHANISM contradicted" in r["verdict"], (
        f"a rising trend did not contradict MECHANISM: {r['verdict']}")


def test_the_voided_field_check_distinguishes_untested_from_failed(tmp_path):
    """'no voided entries' and 'the field did not populate' are different facts."""
    run = tmp_path / "planted_run"
    run.mkdir()
    (run / "console.log").write_text("[10:00:00] Round 0/7\n", encoding="utf-8")

    # no voided entries at all -> UNTESTED, not a failure
    (run / "runner_state.json").write_text(json.dumps(
        {"registry": {"entries": {"C0001": {"falsifier_verdict": "CONFIRMED"}}}}),
        encoding="utf-8")
    v = json.loads(_run(["--run", str(run), "--json"]).stdout)["voided_verification"]
    assert "untested" in v["verdict"], f"an absent population read as a result: {v}"

    # a voided entry WITHOUT the field -> a defect, named as one
    (run / "runner_state.json").write_text(json.dumps(
        {"registry": {"entries": {"C0001": {
            "falsifier_verdict": "NON_DISCRIMINATING"}}}}), encoding="utf-8")
    v = json.loads(_run(["--run", str(run), "--json"]).stdout)["voided_verification"]
    assert "did NOT populate" in v["verdict"], (
        f"a missing field was not reported as a defect: {v}")

    # a voided entry WITH the field -> populated
    (run / "runner_state.json").write_text(json.dumps(
        {"registry": {"entries": {"C0001": {
            "falsifier_verdict": "NON_DISCRIMINATING",
            "verification_voided": True,
            "verification_voided_reason": "because"}}}}), encoding="utf-8")
    v = json.loads(_run(["--run", str(run), "--json"]).stdout)["voided_verification"]
    assert "populated on every voided entry" in v["verdict"], v
