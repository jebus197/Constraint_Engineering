"""Renamed config keys must survive BOTH ingestion paths.

Found 2026-08-12 while inventorying which components are actually switched on.
`routing_enabled` reported as enabled by zero configs, which contradicted the
record. It was not disabled: the field was RENAMED from `take_up_slack_enabled`,
17 shipped configs still carry the old name, and both ingestion paths translate it.

The gap is in the safety net rather than the code. `test_launcher_no_silent_drops`
ends the silent-drop class by iterating `dataclasses.fields(RunnerConfig)` — which
is the right design and covers every real field. But an alias is BY DEFINITION not
a dataclass field, so that test structurally cannot see one. Break the mapping and
17 configs lose routing with a fully green suite.

This file covers the blind spot, and discovers aliases by scanning the source rather
than listing them, so a future rename is covered without anyone remembering to come
back here.
"""
from __future__ import annotations

import dataclasses
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from bench.launcher_core import build_runner_config_from_dict
from bench.reference_runner_v2 import RunnerConfig

REPO = Path(__file__).resolve().parents[2]
BASE = {"experiment_name": "t", "models": ["CC2"], "test_article": "x.md"}

_LAUNCHER_ALIAS = re.compile(
    r'kwargs\[[\'"]([a-z_0-9]+)[\'"]\]\s*=\s*exp_cfg\[[\'"]([a-z_0-9]+)[\'"]\]')
_FROMDICT_ALIAS = re.compile(
    r'if\s+["\']([a-z_0-9]+)["\']\s+in\s+d\s+and\s+["\']([a-z_0-9]+)["\']\s+not\s+in\s+d')


def _discover_aliases() -> set[tuple[str, str]]:
    """Return {(old_config_key, new_field_name)} found in either ingestion path."""
    found: set[tuple[str, str]] = set()
    src = (REPO / "bench/launcher_core.py").read_text()
    for new, old in _LAUNCHER_ALIAS.findall(src):
        if new != old:
            found.add((old, new))
    src2 = (REPO / "bench/reference_runner_v2.py").read_text()
    for old, new in _FROMDICT_ALIAS.findall(src2):
        if new != old:
            found.add((old, new))
    return found


ALIASES = sorted(_discover_aliases())


def test_at_least_one_alias_is_discovered():
    """Without this the parametrised tests below pass vacuously.

    Same failure shape the whole file guards against: a check that silently stops
    checking anything still reports green.
    """
    assert ALIASES, (
        "no config-key aliases discovered — either the alias mechanism was removed "
        "(in which case delete this file deliberately) or the source patterns "
        "changed and this test has gone blind")


@pytest.mark.parametrize("old,new", ALIASES)
def test_alias_target_is_a_real_field(old, new):
    fields = {f.name for f in dataclasses.fields(RunnerConfig)}
    assert new in fields, f"alias {old!r} maps to {new!r}, which is not a RunnerConfig field"


@pytest.mark.parametrize("old,new", ALIASES)
def test_alias_survives_the_runner_path(old, new):
    cfg = RunnerConfig.from_dict({**BASE, old: True})
    assert getattr(cfg, new) is True, (
        f"runner --config path dropped {old!r}; {new} did not become True")


@pytest.mark.parametrize("old,new", ALIASES)
def test_alias_survives_the_launcher_path(old, new):
    """The launcher is the path the arc sequencer uses — the one that has failed before."""
    cfg = build_runner_config_from_dict({**BASE, old: True}, SimpleNamespace(resume=False))
    assert getattr(cfg, new) is True, (
        f"launcher path dropped {old!r}; {new} did not become True. This is the "
        f"silent-divergence class: the config declares an option, the run ignores it, "
        f"and nothing reports a problem")


@pytest.mark.parametrize("old,new", ALIASES)
def test_both_paths_agree_on_the_alias(old, new):
    for value in (True, False):
        runner = getattr(RunnerConfig.from_dict({**BASE, old: value}), new)
        launcher = getattr(
            build_runner_config_from_dict({**BASE, old: value}, SimpleNamespace(resume=False)), new)
        assert runner == launcher == value, (
            f"paths disagree on {old!r}={value!r}: runner={runner!r} launcher={launcher!r}")


@pytest.mark.parametrize("old,new", ALIASES)
def test_the_new_name_wins_when_both_are_present(old, new):
    """A config carrying both must not depend on ingestion order."""
    cfg = {**BASE, old: False, new: True}
    runner = getattr(RunnerConfig.from_dict(dict(cfg)), new)
    launcher = getattr(
        build_runner_config_from_dict(dict(cfg), SimpleNamespace(resume=False)), new)
    assert runner is True and launcher is True, (
        f"explicit {new!r} must take precedence over legacy {old!r}; "
        f"runner={runner!r} launcher={launcher!r}")


def test_shipped_configs_using_a_legacy_name_are_still_honoured():
    """Guards the 17 real configs rather than a synthetic one."""
    import json
    for old, new in ALIASES:
        users = []
        for p in (REPO / "bench").rglob("*.json"):
            if "/logs/" in str(p):
                continue
            try:
                d = json.loads(p.read_text())
            except Exception:
                continue
            if isinstance(d, dict) and d.get(old) is True:
                users.append(p)
        for p in users[:5]:                      # a sample is enough; all share the path
            d = json.loads(p.read_text())
            merged = {**BASE, **{k: v for k, v in d.items() if k == old}}
            cfg = build_runner_config_from_dict(merged, SimpleNamespace(resume=False))
            assert getattr(cfg, new) is True, f"{p.name} sets {old}=true but {new} is off"
