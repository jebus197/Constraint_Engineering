"""The runner must write where the launcher told it to, not mint a second place.

Task 6.3. Founder ruling, verbatim: *"Then build the fix and test it, then as
ever, ask Fable and CC2 to check your fix."*

WRITTEN AND NEVER READ. `ExperimentConfig` carries a `logs_dir`;
`bench/tools/run_simulated_experiment.py:222` sets it on every simulated launch;
`bench/reference_runner_v3.py` read it 0 times and minted its own directory from
`cfg.experiment_name` plus a fresh timestamp. So a launcher could create a
directory, tell the founder where to tail it, pass the path in, and then watch
the run write somewhere else. That is the unwired-addition half of the additive
standard, and it is why 14 of 119 archived runs left artefacts under 2
directories.

THE FALLBACK IS THE OTHER HALF OF THIS FILE. A fix that honoured the caller but
broke resume would trade one defect for a worse one, so the unchanged paths are
tested as carefully as the changed one.
"""

import sys
import types
from datetime import datetime
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    RunnerConfig, _find_or_create_logs_dir,
)


def _cfg(**over):
    cfg = RunnerConfig(test_article="x")
    cfg.experiment_name = over.pop("experiment_name", "unit_probe")
    cfg.resume = over.pop("resume", False)
    return cfg


def test_an_explicit_logs_dir_is_honoured(tmp_path):
    """THE PROPERTY."""
    want = tmp_path / "launcher_chose_this"
    exp = types.SimpleNamespace(logs_dir=str(want))
    assert _find_or_create_logs_dir(_cfg(), exp) == want


def test_a_pathlib_path_is_honoured_too(tmp_path):
    """The launcher passes `str(logs)`; nothing forbids a Path."""
    want = tmp_path / "as_a_path"
    exp = types.SimpleNamespace(logs_dir=want)
    assert _find_or_create_logs_dir(_cfg(), exp) == want


def test_no_exp_config_at_all_still_mints(tmp_path):
    """Byte-identical to the old behaviour for every caller that names nothing.

    The parameter defaults to None precisely so existing call sites keep
    working; if this fails, the fix has become a required argument."""
    got = _find_or_create_logs_dir(_cfg())
    assert got.name.startswith("unit_probe_"), got


def test_an_absent_or_empty_logs_dir_falls_back(tmp_path):
    for value in (None, "", 0):
        exp = types.SimpleNamespace(logs_dir=value)
        got = _find_or_create_logs_dir(_cfg(), exp)
        assert got.name.startswith("unit_probe_"), (value, got)
    got = _find_or_create_logs_dir(_cfg(), types.SimpleNamespace())
    assert got.name.startswith("unit_probe_"), got


def test_the_minted_name_still_carries_a_timestamp():
    """The fallback's shape matters: resume scans for it by glob."""
    got = _find_or_create_logs_dir(_cfg(experiment_name="probe2"))
    stamp = got.name.split("probe2_", 1)[1]
    datetime.strptime(stamp, "%Y%m%dT%H%M%SZ")


def test_an_explicit_dir_beats_the_resume_scan(tmp_path, monkeypatch):
    """ORDER, and the reason for it.

    A caller that named a directory has already answered the question the
    resume scan exists to ask. If the scan ran first it could return a
    DIFFERENT older run's directory and silently resume the wrong one."""
    import bench.reference_runner_v3 as rr
    logs_root = tmp_path / "bench" / "logs"
    stale = logs_root / "unit_probe_20250101T000000Z"
    stale.mkdir(parents=True)
    (stale / "checkpoint.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(rr, "REPO_ROOT", tmp_path)

    want = tmp_path / "explicitly_named"
    exp = types.SimpleNamespace(logs_dir=str(want))
    assert _find_or_create_logs_dir(_cfg(resume=True), exp) == want, (
        "an explicitly named directory was overridden by the resume scan")


def test_resume_still_finds_a_checkpoint_when_nothing_is_named(tmp_path, monkeypatch):
    """The path the fix must NOT have broken."""
    import bench.reference_runner_v3 as rr
    logs_root = tmp_path / "bench" / "logs"
    older = logs_root / "unit_probe_20250101T000000Z"
    newer = logs_root / "unit_probe_20260101T000000Z"
    for d in (older, newer):
        d.mkdir(parents=True)
        (d / "checkpoint.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(rr, "REPO_ROOT", tmp_path)
    assert _find_or_create_logs_dir(_cfg(resume=True)) == newer


def test_the_runner_actually_passes_exp_config_at_the_call_site():
    """WIRING. The helper honouring the caller is worthless if nothing hands it
    the caller's config -- the exact failure this task exists to close, one
    level up."""
    import inspect
    import bench.reference_runner_v3 as rr
    src = inspect.getsource(rr.run_experiment)
    assert "_find_or_create_logs_dir(cfg, exp_config)" in src, (
        "run_experiment calls the helper without exp_config, so logs_dir is "
        "written and still read nowhere")


# ── THE SHAPE PRODUCTION ACTUALLY PASSES, which nothing above tested ─────────
#
# Every test above builds its exp_config from `types.SimpleNamespace`. All 8
# passed while the shipped code sent EVERY production run into one shared
# directory, because the only shape production ever passes -- a real
# `ExperimentConfig` carrying its dataclass default -- was the one shape never
# constructed. Found by an adversarial review of the completion claim, not by
# the suite.

def test_the_real_ExperimentConfig_default_is_not_read_as_a_choice():
    """A DEFAULT IS NOT A DECLARATION, and this is the second time in one
    evening that the same error had to be fixed.

    `ExperimentConfig.logs_dir` defaults to `bench/logs/experiment_11` -- a
    TRUTHY path -- and `load_default_config` sets it on every launch. Reading
    that as the caller's choice dropped the experiment name and the timestamp,
    collided every run in a directory already holding 22 artefacts from
    2026-03-28, and bypassed the resume scan."""
    from bench.experiment_11_orchestrator import ExperimentConfig
    cfg = _cfg(experiment_name="probe_real")
    got = _find_or_create_logs_dir(cfg, ExperimentConfig(models=[]))
    assert got.name.startswith("probe_real_"), (
        f"the untouched dataclass default was read as a choice: {got}")
    assert "experiment_11" not in str(got), got


def test_the_launcher_s_own_config_is_not_read_as_a_choice():
    """The production path end to end. `load_experiment_config` RESOLVES the
    default against the repository root, so it is absolute where the dataclass
    default is relative -- a raw string comparison misses it, and the first
    repair of this regression did exactly that and changed nothing."""
    import sys
    sys.path.insert(0, str(REPO / "bench"))
    import launcher_core
    cfg = _cfg(experiment_name="probe_launcher")
    got = _find_or_create_logs_dir(cfg, launcher_core.load_experiment_config())
    assert got.name.startswith("probe_launcher_"), (
        f"the launcher's resolved default was read as a choice: {got}")


def test_resume_still_scans_when_the_config_carries_only_the_default(tmp_path, monkeypatch):
    """The resume path must not be bypassed by a default either."""
    import bench.reference_runner_v3 as rr
    from bench.experiment_11_orchestrator import ExperimentConfig
    logs_root = tmp_path / "bench" / "logs"
    newer = logs_root / "probe_resume_20260101T000000Z"
    newer.mkdir(parents=True)
    (newer / "checkpoint.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(rr, "REPO_ROOT", tmp_path)
    got = _find_or_create_logs_dir(_cfg(experiment_name="probe_resume", resume=True),
                                   ExperimentConfig(models=[]))
    assert got == newer, f"the resume scan was bypassed by a default: {got}"
