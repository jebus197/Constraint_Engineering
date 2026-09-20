#!/usr/bin/env python3
"""P-pass for the 3 panel producers written 2026-09-20.

These tests do NOT re-assert what the producers printed against the live
archive -- that would only check that a script agrees with itself. Each test
builds a SYNTHETIC input whose correct answer is known by construction, runs the
producer's own functions against it, and fails if the answer is wrong.

The 3 producers under test:
  scripts/sk_verdict_never_fired_2026-09-20.py     -- counts fix-admission verdicts
  scripts/panel_delivery_channel_2026-09-20.py     -- counts seat-delivered files
  scripts/panel_figure_provenance_2026-09-20.py    -- checks a figure has a producer

WHAT EACH TEST IS TRYING TO BREAK, stated so a reader can judge whether the
attempt was severe enough rather than taking "passed" on trust.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# 1. The verdict counter.
# --------------------------------------------------------------------------

def test_wilson_matches_statsmodels_across_the_range():
    """BREAK ATTEMPT: a hand-rolled Wilson interval that is subtly wrong.

    The producer reports 191 of 1247 with a Wilson interval from its own closed
    form. If that form is wrong the headline interval is wrong. Checked against
    statsmodels at the boundaries as well as the middle, because k=0 and k=n are
    exactly where a closed form usually breaks.
    """
    sm = pytest.importorskip("statsmodels.stats.proportion")
    mod = load("sk_verdict_never_fired_2026-09-20.py")
    for k, n in [(0, 10), (10, 10), (1, 3), (191, 1247), (902, 1247), (5, 7), (0, 1)]:
        lo1, hi1 = mod.wilson(k, n)
        lo2, hi2 = sm.proportion_confint(k, n, alpha=0.05, method="wilson")
        assert abs(lo1 - lo2) < 1e-12, f"Wilson lower disagrees at {k}/{n}"
        assert abs(hi1 - hi2) < 1e-12, f"Wilson upper disagrees at {k}/{n}"


def test_verdict_walk_finds_nested_and_does_not_double_count(tmp_path, monkeypatch):
    """BREAK ATTEMPT: a walker that misses deeply nested verdicts, or counts twice.

    The real runner_state nests sk_result inside registry entries inside rounds.
    A walker that only looked one level down would under-count and report the
    verdict as rarer than it is -- which is the direction that would have
    wrongly supported 'change nothing'. This builds a tree with a KNOWN answer:
    3 ADMISSIBLE, 2 REJECTED, 1 ESCALATE, one of them buried 5 levels deep.
    """
    mod = load("sk_verdict_never_fired_2026-09-20.py")

    def entry(tri):
        return {"sk_result": {"sk": 0.5, "tristate": tri}}

    state = {
        "rounds": [
            {"registry": {"entries": {"c1": entry("ADMISSIBLE"), "c2": entry("REJECTED")}}},
            {"registry": {"entries": {"c3": entry("ADMISSIBLE")}}},
        ],
        "deep": {"a": {"b": {"c": {"d": entry("ESCALATE")}}}},
        "list_of_lists": [[entry("REJECTED")], [entry("ADMISSIBLE")]],
    }
    run_dir = tmp_path / "bench" / "logs" / "synthetic_run"
    run_dir.mkdir(parents=True)
    (run_dir / "runner_state.json").write_text(json.dumps(state))
    monkeypatch.setattr(mod, "ROOT", tmp_path)

    entries, tri, runs = mod.collect()
    assert entries == 6, f"expected 6 verdicts, walker found {entries}"
    assert tri["ADMISSIBLE"] == 3, tri
    assert tri["REJECTED"] == 2, tri
    assert tri["ESCALATE"] == 1, tri
    assert len(runs) == 1


def test_walker_ignores_an_sk_result_that_is_not_a_verdict(tmp_path, monkeypatch):
    """BREAK ATTEMPT: counting a string or null sk_result as a decision.

    A run that recorded sk_result as a bare string, or as a dict with no
    tristate, must not inflate the denominator. Inflating it would understate
    the rejection rate.
    """
    mod = load("sk_verdict_never_fired_2026-09-20.py")
    state = {
        "a": {"sk_result": "REJECTED"},              # string, not a verdict record
        "b": {"sk_result": None},                     # null
        "c": {"sk_result": {"sk": 0.1}},              # dict with no tristate
        "d": {"sk_result": {"tristate": "REJECTED"}}, # the only real one
    }
    run_dir = tmp_path / "bench" / "logs" / "synthetic_run"
    run_dir.mkdir(parents=True)
    (run_dir / "runner_state.json").write_text(json.dumps(state))
    monkeypatch.setattr(mod, "ROOT", tmp_path)

    entries, tri, _ = mod.collect()
    assert entries == 1, f"only 1 real verdict, walker counted {entries}"
    assert tri["REJECTED"] == 1


def test_the_parsing_trap_is_real_not_asserted():
    """BREAK ATTEMPT: the claim that the NAME and the VALUE differ.

    The whole correction rests on SK_REJECTED being a constant NAME whose VALUE
    is the bare string REJECTED. If the source actually assigned the string
    "SK_REJECTED", the trap would not exist and the first version of the script
    would have been right. Read it from the source rather than believing it.
    """
    import re
    src = (ROOT / "bench" / "reference_runner_v3.py").read_text(errors="ignore")
    m = re.search(r'^SK_REJECTED\s*=\s*["\']([^"\']+)["\']', src, re.M)
    assert m, "SK_REJECTED is not assigned a literal in reference_runner_v3.py"
    assert m.group(1) == "REJECTED", (
        f"the trap does not exist: SK_REJECTED == {m.group(1)!r}, so searching "
        "the name would have worked after all"
    )


# --------------------------------------------------------------------------
# 2. The delivery-channel counter.
# --------------------------------------------------------------------------

def test_harvest_counter_excludes_harness_files_but_keeps_deliverables(tmp_path, monkeypatch):
    """BREAK ATTEMPT: counting the harness's own echoed files as seat deliverables.

    fable's round-3 harvest contained changes.diff and a copy of the harness's
    dispatch.log and nothing else. If those counted, fable would read as having
    delivered 2 files and the finding ('delivered 0') would be false.
    """
    mod = load("panel_delivery_channel_2026-09-20.py")
    seat = tmp_path / "sandbox_harvest" / "someseat" / "attempt-1"
    (seat / "files" / "scripts").mkdir(parents=True)
    (seat / "changes.diff").write_text("diff")
    (seat / "files" / "bench" / "logs" / "x").mkdir(parents=True)
    (seat / "files" / "bench" / "logs" / "x" / "dispatch.log").write_text("log")
    (seat / "files" / "scripts" / "real_fix.py").write_text("print(1)")

    monkeypatch.setattr(mod, "ROUNDS", {"rX": tmp_path})
    got = mod.harvested_files(tmp_path, "someseat")
    assert len(got) == 1, f"expected only the real deliverable, got {got}"
    assert got[0].endswith("real_fix.py")


def test_bash_write_detection_does_not_fire_on_a_plain_read():
    """BREAK ATTEMPT: calling a read a write, which would erase the asymmetry.

    The finding is that fable attempted the documented route and delivered
    nothing. If the detector counted 'cat file' as a write, every seat would
    look like it delivered and the asymmetry would vanish.
    """
    mod = load("panel_delivery_channel_2026-09-20.py")
    reads = ["cat bench/reference_runner_v3.py", "grep -n foo x.py",
             "python3 -c 'print(1)'", "ls scripts/"]
    writes = ["cat > scripts/a.py <<'PY'", "python3 - <<'PY'", "tee scripts/b.py",
              "p.write_text('x')"]
    for s in reads:
        assert not any(k in s for k in mod.WRITE_MARKERS), f"false positive on read: {s}"
    for s in writes:
        assert any(k in s for k in mod.WRITE_MARKERS), f"missed a write: {s}"


# --------------------------------------------------------------------------
# 3. The figure-provenance checker.
# --------------------------------------------------------------------------

def test_provenance_checker_detects_a_figure_that_IS_present(tmp_path):
    """BREAK ATTEMPT: a checker that reports every figure absent.

    This is the one that matters. If `run` or the regex were broken, EVERY
    figure would read 'FIGURE ABSENT' and the finding against the 75.8% would
    be an artefact of a broken checker rather than a real orphan. So: give it a
    script that definitely prints the figure and require it to be found.
    """
    import re
    mod = load("panel_figure_provenance_2026-09-20.py")
    good = tmp_path / "prints_it.py"
    good.write_text("print('over-refusal 75.8 percent')\n")
    ok, out = mod.run(good)
    assert ok, f"producer failed to run: {out}"
    assert re.search(r"75\.8", out), "checker cannot see a figure that IS printed"

    bad = tmp_path / "prints_something_else.py"
    bad.write_text("print('no figure here')\n")
    ok2, out2 = mod.run(bad)
    assert ok2
    assert not re.search(r"75\.8", out2), "checker hallucinated a figure"


def test_provenance_checker_reports_a_failing_producer_as_failed(tmp_path):
    """BREAK ATTEMPT: a crashed producer silently reading as 'figure absent'.

    'The script ran and the figure was not there' and 'the script crashed' are
    different findings. Conflating them would let a broken producer masquerade
    as evidence that a figure is orphaned.
    """
    mod = load("panel_figure_provenance_2026-09-20.py")
    crash = tmp_path / "crashes.py"
    crash.write_text("raise SystemExit(3)\n")
    ok, _ = mod.run(crash)
    assert ok is False, "a crashing producer must not report as a clean run"

    missing = tmp_path / "does_not_exist.py"
    ok2, msg = mod.run(missing)
    assert ok2 is False and "absent" in msg
