#!/usr/bin/env python3
"""The immune-memory reset archives before it resets, and never destroys.

HIS RULING, 2026-10-16: *"No. We reset immune memory for the upcoming live
experiments, since simulation can probably only tell us so much about how this
facility will function in real live/paid experiments."* And, pressed the same
day: *"isn't the best time to do this now, immediately before the transition
back to main is made?"*

TWO OF THE THREE HALVES WERE ALREADY BUILT: the researcher switch
`RunnerConfig.immune_memory_scope`, defaulting to `persist` exactly as he
directed, and its consumer in the runner. The one-off reset was NAMED in the
runner's own comment as `scripts/reset_experiment_scoped_state_2026-10-16.py`
and that file did not exist, so a code comment promised a mechanism nobody could
run.

THE STATE IT WAS RUN AGAINST, measured: 6 counted experiments of which only 3
were NAMED, and those 3 were exactly the simulated shakedown runs. The memory's
own `provenance_complete` property reports this on load, and it carries a
consequence he was not told: the duplicate-ingestion guard refuses an id it has
SEEN, so it cannot refuse a re-run of an unnamed one, and re-ingesting any of
the 3 live experiments would silently double its counts. A fresh store has
complete provenance by construction.

AND THIS SUITE EXISTS BECAUSE THE SCRIPT'S OWN FIRST TEST BROKE THE THING IT
PROTECTS. The archive glob matched the `*.why.json` sidecar, which sorted AFTER
the real copy, so a `--restore` of "the latest" wrote the SIDECAR over the live
memory. The runner would then have loaded 0 priors believing that to be the
truth. It was recovered byte-exactly from the verified archive -- which is the
whole reason the archive is written and checked before the live file is touched.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "reset_experiment_scoped_state_2026-10-16.py"


def _load(name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


MEMORY = {
    "version": 1, "experiment_count": 2, "decay_rate": 0.1,
    "drift_threshold": 0.3, "source_hash": None,
    "experiment_ids": ["exp_a", "exp_b"],
    "records": {"1": {"flaw_class": 1, "confirmed": 5.0, "rejected": 1.0,
                      "experiments_seen": 2}},
}
SIDECAR = {"archived_utc": "x", "reason": "y", "state_when_archived": {},
           "restore_with": "z"}


def test_the_script_the_runner_names_exists():
    """A comment promising a mechanism nobody can run is worse than no comment."""
    assert SCRIPT.is_file(), (
        "the runner's immune-memory comment names this script; it must exist")
    runner = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    assert SCRIPT.name in runner, (
        "the runner no longer names this script, so the reference has drifted")


def test_a_sidecar_is_not_a_restorable_memory():
    """THE DEFECT THIS SUITE WAS WRITTEN FOR, pinned so it cannot return."""
    m = _load("reset_guard_a")
    assert m._is_memory.__call__ is not None
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        good = pathlib.Path(td) / "immune_memory_1.json"
        bad = pathlib.Path(td) / "immune_memory_1.why.json"
        good.write_text(json.dumps(MEMORY), encoding="utf-8")
        bad.write_text(json.dumps(SIDECAR), encoding="utf-8")
        assert m._is_memory(good) is True
        assert m._is_memory(bad) is False, (
            "a sidecar passes as an immune memory, so --restore can write it "
            "over the live priors -- which is exactly what happened")


def test_a_restore_refuses_a_file_that_is_not_a_memory(tmp_path, monkeypatch):
    m = _load("reset_guard_b")
    arch = tmp_path / "arch"
    arch.mkdir()
    bad = arch / "immune_memory_9.why.json"
    bad.write_text(json.dumps(SIDECAR), encoding="utf-8")
    live = tmp_path / "immune_memory.json"
    live.write_text(json.dumps(MEMORY), encoding="utf-8")
    before = hashlib.sha256(live.read_bytes()).hexdigest()
    monkeypatch.setattr(m, "ARCHIVE", arch)
    monkeypatch.setattr(m, "LIVE", live)
    monkeypatch.setattr(sys, "argv", ["x", "--restore", bad.name])
    rc = m.main()
    assert rc == 2, "restoring a non-memory must be refused"
    assert hashlib.sha256(live.read_bytes()).hexdigest() == before, (
        "the live priors were modified by a refused restore")


def test_a_dry_run_writes_nothing(tmp_path, monkeypatch):
    m = _load("reset_guard_c")
    live = tmp_path / "immune_memory.json"
    live.write_text(json.dumps(MEMORY), encoding="utf-8")
    arch = tmp_path / "arch"
    before = hashlib.sha256(live.read_bytes()).hexdigest()
    monkeypatch.setattr(m, "ARCHIVE", arch)
    monkeypatch.setattr(m, "LIVE", live)
    monkeypatch.setattr(sys, "argv", ["x"])
    assert m.main() == 0
    assert hashlib.sha256(live.read_bytes()).hexdigest() == before
    assert not list(arch.glob("immune_memory_*.json")), (
        "a dry run archived something, so it was not a dry run")


def test_apply_archives_verifies_and_then_resets(tmp_path, monkeypatch):
    m = _load("reset_guard_d")
    live = tmp_path / "immune_memory.json"
    live.write_text(json.dumps(MEMORY), encoding="utf-8")
    arch = tmp_path / "arch"
    before = hashlib.sha256(live.read_bytes()).hexdigest()
    monkeypatch.setattr(m, "ARCHIVE", arch)
    monkeypatch.setattr(m, "LIVE", live)
    monkeypatch.setattr(sys, "argv", ["x", "--apply"])
    assert m.main() == 0

    copies = [p for p in arch.glob("immune_memory_*.json")
              if not p.name.endswith(".why.json")]
    assert len(copies) == 1, f"expected 1 archived memory, got {copies}"
    assert hashlib.sha256(copies[0].read_bytes()).hexdigest() == before, (
        "the archive does not match what was live, so the priors are not safe")
    assert copies[0].with_suffix(".why.json").is_file(), (
        "no sidecar records WHY the priors were set aside")

    after = json.loads(live.read_text())
    assert after["experiment_count"] == 0
    assert after["experiment_ids"] == []
    assert after["records"] == {}
    # THE SHAPE AND THE TUNING SURVIVE: a reset is not a different file format.
    assert after["version"] == MEMORY["version"]
    assert after["decay_rate"] == MEMORY["decay_rate"]
    assert after["drift_threshold"] == MEMORY["drift_threshold"]


def test_the_round_trip_is_byte_exact(tmp_path, monkeypatch):
    """Reversibility PROVEN rather than promised."""
    m = _load("reset_guard_e")
    live = tmp_path / "immune_memory.json"
    live.write_text(json.dumps(MEMORY), encoding="utf-8")
    arch = tmp_path / "arch"
    orig = hashlib.sha256(live.read_bytes()).hexdigest()
    monkeypatch.setattr(m, "ARCHIVE", arch)
    monkeypatch.setattr(m, "LIVE", live)

    monkeypatch.setattr(sys, "argv", ["x", "--apply"])
    m.main()
    assert json.loads(live.read_text())["experiment_count"] == 0

    copy = [p for p in arch.glob("immune_memory_*.json")
            if not p.name.endswith(".why.json")][0]
    monkeypatch.setattr(sys, "argv", ["x", "--restore", copy.name])
    m.main()
    assert hashlib.sha256(live.read_bytes()).hexdigest() == orig, (
        "the restore is not byte-exact, so the reset is not reversible")


def test_the_live_store_is_reset_and_its_provenance_is_complete():
    """The state his ruling asked for, read off the real file."""
    sys.path.insert(0, str(REPO))
    from bench.dm._memory import ImmuneMemory
    mem = ImmuneMemory.load(str(REPO / "bench" / "state" / "immune_memory.json"))
    assert mem._experiment_count == 0, (
        f"the live immune memory still carries {mem._experiment_count} "
        f"experiment(s) of priors; his ruling of 2026-10-16 was to reset it "
        f"for the upcoming live experiments")
    assert mem.provenance_complete, (
        "a fresh store must name every experiment it counts, which is 0 of 0")


def test_the_archived_priors_are_still_there():
    """Point, never prune. The reset must not have destroyed the evidence."""
    arch = REPO / "bench" / "state" / "immune_memory_archive"
    copies = [p for p in arch.glob("immune_memory_*.json")
              if not p.name.endswith(".why.json")]
    assert copies, "the reset left no archived copy, so the priors are gone"
    found = False
    for c in copies:
        d = json.loads(c.read_text(encoding="utf-8"))
        if d.get("experiment_count") == 6 and len(d.get("experiment_ids") or []) == 3:
            found = True
    assert found, (
        "no archived copy holds the 6-experiment state that was reset, so what "
        "was set aside cannot be inspected or restored")


def test_the_researcher_switch_still_defaults_to_persist():
    """His words: "probably the best strategy is to leave the default ... set to
    on, so that it can persist between experiments"."""
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    import reference_runner_v3 as R
    cfg = R.RunnerConfig(experiment_name="t", models=["A"],
                         test_article="bench/dm/_memory.py")
    assert cfg.immune_memory_scope == "persist", (
        "the researcher switch no longer defaults to persist, which is the "
        "default he directed")
    assert R.RunnerConfig(experiment_name="t", models=["A"],
                          test_article="x.py",
                          immune_memory_scope="experiment"
                          ).immune_memory_scope == "experiment", (
        "the switch cannot be set to experiment scope, so it is not a switch")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
