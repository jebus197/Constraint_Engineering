#!/usr/bin/env python3
"""The repointing experiment's mechanics are EXECUTED, not described.

FOUNDER RULING 2026-10-03: "Yes run it, record the results and implement any
findings if they are useful."

WHAT COULD GO WRONG WITH AN EXPERIMENT LIKE THIS, and therefore what these
tests hold:

  * THE REWRITE COULD MISS. If `repoint` leaves the original path in place, arm
    B is arm A with extra steps and the experiment measures nothing. Tested by
    rewriting a planted body and asserting the old path is gone and the new one
    is present.
  * THE REWRITE COULD OVERREACH. A body that mentions its target inside a
    MESSAGE rather than as a path must not have the message rewritten, or the
    difference between the arms is partly cosmetic. Tested.
  * THE DECOY COULD BE THE SAME FILE. Repointing a body at the file it already
    names is a null treatment that would look like perfect generality. Tested.
  * THE DECOY COULD BE OF A DIFFERENT KIND. A Markdown falsifier pointed at a
    Python file can fail for parsing reasons that say nothing about
    specificity. Tested: same suffix.
  * A LIMIT COULD DECIDE A HYPOTHESIS. The design is fixed-N; a partial run
    must refuse to decide rather than report a smaller significant result.
    Tested.
  * THE STATISTICS COULD DISAGREE BETWEEN TOOLS. Fisher from scipy is
    cross-checked against an exact mpmath enumeration, and Wilson from
    statsmodels against an independent mpmath closed form. Tested on a table
    with a known answer.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "repointing_experiment_2026-10-03.py"


def _mod() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("repoint_under_test", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


BODY = (
    'import pathlib\n'
    'text = pathlib.Path("bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md").read_text()\n'
    'assert "0.3125" not in text, "FALSIFIED: the superseded rate survives in '
    'bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"\n'
)


def test_the_rewrite_actually_repoints():
    m = _mod()
    out, n = m.repoint(BODY, ["bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"],
                       "bench/OTHER.md")
    assert n >= 1, "nothing was substituted, so arm B is arm A"
    assert '"bench/OTHER.md"' in out
    assert '"bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"' not in out, (
        "the quoted path span survived the rewrite")


def test_the_rewrite_leaves_prose_mentions_alone():
    """The same filename inside a MESSAGE is not a path span.

    If the message were rewritten too, part of the difference between the arms
    would be cosmetic rather than behavioural.
    """
    m = _mod()
    out, _ = m.repoint(BODY, ["bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"],
                       "bench/OTHER.md")
    assert "the superseded rate survives in bench/BUILD_BOT" in out, (
        "the assertion message was rewritten, so the arms differ in their "
        "text as well as their target")


def test_the_decoy_is_a_different_file_of_the_same_kind():
    m = _mod()
    named = ["bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"]
    decoy = m._pick_decoy(named)
    assert decoy, "no decoy was found, so arm B cannot run at all"
    assert decoy not in named, (
        "the decoy IS the named file, which is a null treatment that would "
        "read as perfect generality")
    assert pathlib.Path(decoy).suffix == pathlib.Path(named[0]).suffix, (
        "the decoy is of a different kind, so a failure could be a parsing "
        "artefact rather than evidence about specificity")


def test_the_population_is_non_trivial_and_deduplicated():
    m = _mod()
    pop = m.harvest()
    assert len(pop) > 50, (
        f"only {len(pop)} file-naming bodies found; the population the "
        "experiment is defined over has gone missing")
    bodies = [r["body"] for r in pop]
    assert len(bodies) == len(set(bodies)), (
        "the population contains duplicate bodies, so one falsifier would be "
        "counted several times in the denominator")


def test_the_statistics_agree_between_tools():
    m = _mod()
    w = m.wilson(7, 20)
    assert w["pct"] == 35.0
    fe = m.fisher([[8, 2], [3, 7]])
    assert fe["p_scipy"] is not None and fe["p_mpmath"] is not None
    assert abs(fe["p_scipy"] - fe["p_mpmath"]) < 1e-9, (
        f"scipy and mpmath disagree on the Fisher p: {fe}")


def test_a_limited_run_refuses_to_decide(tmp_path):
    """The design is fixed-N. A partial run must not report a verdict."""
    import json
    import subprocess
    out = tmp_path / "rec.json"
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--limit", "2", "--timeout", "20",
         "--out", str(out)],
        capture_output=True, text=True, cwd=str(REPO), timeout=900)
    assert p.returncode == 0, f"the experiment failed: {p.stderr[-800:]}"
    rec = json.loads(out.read_text())
    assert rec["skipped_by_limit"] > 0
    assert "NOT DECIDED" in rec["verdict"] or rec["verdict"].startswith("NOT"), (
        f"a limited run decided a hypothesis anyway: {rec['verdict']}")
    assert "SKIPPED BY --limit" in p.stdout, (
        "the limit was silent, which reads as full coverage")


def test_the_preregistration_is_in_the_record():
    """A hypothesis registered after the result is not a hypothesis."""
    src = SCRIPT.read_text(encoding="utf-8")
    for token in ("H_general", "H_specificity", "alpha = 0.01",
                  "fixed N over the whole population", "degraded"):
        assert token in src, f"the pre-registration does not state {token!r}"
