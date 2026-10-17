"""Task C9: the human-review switch is a MID-RUN HALT, not a review step.

His question was whether `hil_review` "probably should be" on, on the premise
that he reviews the input and the output. The answer turns on what the switch
actually does, and the answer is that it does not sit at either of those
boundaries: it terminates the process between rounds with exit code 42, having
written a partial report, so turning it on converts 1 autonomous run into N
sequential sessions and makes the convergence figure a measurement of a
different process.

This file holds that answer by EXECUTION wherever execution is possible:

  * the default is read off the LIVE dataclass, not off the source text, so a
    rename of the field fails the test instead of silently passing it;
  * the halt property is established with the ast module over the live
    runners, and the test FAILS IF IT FINDS NO BRANCH, so it cannot go
    vacuous the way a string search would when the wiring moves;
  * the "never been on" figure is recomputed from the shipped configs on every
    run rather than quoted from a note;
  * the archive distinction -- a source copy mentioning the key is not a run
    that paused -- is recomputed through `bench.counting`, which excludes this
    file from its own scan. That is the self-inclusion shape task C2 exists to
    prevent, and counting it wrongly would report dozens of pauses where there
    were none.

Producer: scripts/what_would_the_human_review_pause_do_2026-10-17.py
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SWITCH = "hil_review"
PAUSE_EXIT = 42
RUNNERS = ("bench/reference_runner_v3.py", "bench/reference_runner.py")


def _runner_configs():
    from bench.reference_runner import RunnerConfig as V1
    from bench.reference_runner_v3 import RunnerConfig as V3
    return {"reference_runner.py": V1, "reference_runner_v3.py": V3}


@pytest.mark.parametrize("name", sorted(_runner_configs()))
def test_the_switch_exists_on_the_live_config_and_defaults_off(name):
    """Read off the dataclass. A rename or a flipped default fails here."""
    cls = _runner_configs()[name]
    fields = getattr(cls, "__dataclass_fields__", {})
    assert SWITCH in fields, (
        f"{name}: RunnerConfig has no field {SWITCH!r}. If the switch was "
        f"renamed, this guard and task C9's answer both need re-deriving; "
        f"fields present: {sorted(fields)[:8]}...")
    assert fields[SWITCH].default is False, (
        f"{name}: {SWITCH} no longer defaults off (default="
        f"{fields[SWITCH].default!r}). Every run would pause between rounds, "
        f"and no convergence figure would measure autonomous convergence.")
    # Executed, not read: an instance really carries the off default.
    assert getattr(cls(), SWITCH) is False


def _switch_branches(path: pathlib.Path):
    """Every `if cfg.hil_review ...` branch in a live runner, via ast."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        reads = any(
            isinstance(sub, ast.Attribute) and sub.attr == SWITCH
            for sub in ast.walk(node.test))
        if reads:
            found.append(node)
    return found


def _halts_with(node, code: int) -> bool:
    """Does this branch body terminate the process with `code`?"""
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        target = sub.func
        name = getattr(target, "attr", None) or getattr(target, "id", None)
        if name not in ("exit", "_exit"):
            continue
        for arg in sub.args:
            if isinstance(arg, ast.Constant) and arg.value == code:
                return True
    return False


@pytest.mark.parametrize("rel", RUNNERS)
def test_every_branch_that_reads_the_switch_halts_the_run(rel):
    """The ANTI-VACUITY assertion is the first one: 0 branches is a failure."""
    branches = _switch_branches(REPO / rel)
    assert branches, (
        f"{rel}: no branch reads {SWITCH!r} any more. Either the switch is "
        f"dead code, in which case C9's answer no longer describes the "
        f"runner, or the wiring moved and this guard went blind. A string "
        f"search would have passed quietly here.")
    not_halting = [b.lineno for b in branches if not _halts_with(b, PAUSE_EXIT)]
    assert not not_halting, (
        f"{rel}: branches at lines {not_halting} read {SWITCH} without "
        f"halting on {PAUSE_EXIT}. If the switch has become a genuine review "
        f"HOOK rather than a halt, his premise changes and C9 must be "
        f"re-answered -- it would then sit at a boundary he reviews.")


def test_the_halt_is_not_a_graceful_return():
    """A pause that exits non-zero is a halt; 0 would read as success."""
    assert PAUSE_EXIT != 0
    branches = _switch_branches(REPO / "bench/reference_runner_v3.py")
    assert any(_halts_with(b, PAUSE_EXIT) for b in branches)


def _shipped_configs():
    return sorted((REPO / "bench").glob("exp*_configs/*.json"))


def _find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            got = _find_key(value, key)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for value in obj:
            got = _find_key(value, key)
            if got is not None:
                return got
    return None


def test_no_shipped_config_has_ever_turned_it_on():
    """Recomputed every run. The denominator is asserted non-empty first."""
    configs = _shipped_configs()
    assert configs, ("no shipped configs found under bench/exp*_configs/ -- "
                     "the denominator is empty, so '0 of N' would be vacuous.")
    enabling = []
    for path in configs:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if _find_key(data, SWITCH) is True:
            enabling.append(path.name)
    assert not enabling, (
        f"{len(enabling)} of {len(configs)} shipped configs now enable "
        f"{SWITCH}: {enabling}. C9 recorded 0, so the switch has been turned "
        f"on somewhere and the autonomous-convergence claim needs checking "
        f"against those runs.")


def test_a_source_copy_under_logs_is_not_a_run_that_paused():
    """C2's mechanism applied to C9's measurement, self-exclusion included."""
    from bench import counting

    logs = REPO / "bench" / "logs"
    if not logs.exists():
        pytest.skip("no archive present in this checkout")

    reports = sorted(logs.rglob("*.json"))
    assert reports, "archive holds no reports; the distinction is untestable"

    paused = [p for p in reports
              if _find_key(json.loads(p.read_text(encoding="utf-8",
                                                  errors="replace") or "{}"),
                           "hil_paused_at_round") is not None]
    assert not paused, (
        f"{len(paused)} archived runs actually paused: "
        f"{[p.name for p in paused[:3]]}. Any convergence figure spanning one "
        f"of them measures a steered run, not an autonomous one.")

    # The copies that a naive count would have mistaken for pauses, counted
    # through the mechanism C2 built. THIS FILE is deliberately added to the
    # scan set: it contains the pattern in its own source, so if self-exclusion
    # were not real it would contribute a count of its own and inflate the
    # figure -- shape 3, measured here rather than asserted.
    here = pathlib.Path(__file__).resolve()
    assert "hil_paused_at_round" in here.read_text(encoding="utf-8"), (
        "this file no longer contains the pattern, so it cannot demonstrate "
        "self-inclusion; the demonstration has gone vacuous.")
    sources = sorted(logs.rglob("*.py"))
    without = counting.count_over(sources, "hil_paused_at_round", unit="lines")
    with_self = counting.count_over(sources + [here], "hil_paused_at_round",
                                    unit="lines")
    assert without["unit"] == with_self["unit"] == "lines"
    assert with_self["total"] == without["total"], (
        f"adding the calling file changed the figure from {without['total']} "
        f"to {with_self['total']}, so self-exclusion is not in force and any "
        f"count taken this way carries the counter's own mentions.")
    assert here in [pathlib.Path(x).resolve() for x in with_self["excluded"]], (
        f"the calling file was not reported as excluded; excluded="
        f"{with_self['excluded']}. A figure that drops a path silently cannot "
        f"be objected to by a reader.")
