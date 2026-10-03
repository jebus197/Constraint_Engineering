# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2c699b380cdd6041a0dd029cd620fdf0c1496bd0e30ba73526012285aad3a8a6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""D-2: the checkpoint names its target, and the supply instruments read it.

Panel dispute D-2 (open since 2026-09-30, BLOCKING as of 2026-10-02):
`target_file` was recorded on only 52 of 624 post-feature criticals -- the
REPORT has always carried it, the CHECKPOINT (`runner_state.json`, the file
the archive instruments actually walk) never did -- so the prose-vs-code
stratification (CAUSE 3 of the falsifier-supply decomposition) could not be
computed at all. The fix stamps `target_file` and `run_root` into the
checkpoint dict in reference_runner_v3.

Two halves, both executed:
  1. the WRITER: the checkpoint serialisation in reference_runner_v3 now
     includes the keys (asserted by compiling and walking the actual dict
     literal in the source's AST -- the keys must be IN the write, not
     merely somewhere in the file);
  2. the READER: scripts/repro_supply_causes_2026-10-02.py resolves a
     top-level `target_file` from a runner_state.json, so the previously
     unmeasurable stratification becomes measurable the moment a run lands.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_the_checkpoint_write_includes_target_and_root():
    src = (ROOT / "bench" / "reference_runner_v3.py").read_text()
    tree = ast.parse(src)
    hits = []
    for node in ast.walk(tree):
        # the checkpoint is a json.dumps({...}) whose dict carries
        # "runner_version" and "registry" -- find THAT dict and require the
        # new keys inside it, so the assertion cannot be satisfied by the
        # keys existing anywhere else in a 17k-line file.
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "dumps" and node.args
                and isinstance(node.args[0], ast.Dict)):
            keys = {k.value for k in node.args[0].keys
                    if isinstance(k, ast.Constant)}
            if {"runner_version", "registry"} <= keys:
                hits.append(keys)
    assert hits, "the checkpoint json.dumps dict was not found"
    assert any({"target_file", "run_root"} <= k for k in hits), (
        f"no checkpoint write carries target_file+run_root; key sets: {hits}")


def test_the_supply_instrument_reads_a_top_level_target(tmp_path):
    run = tmp_path / "bench" / "logs" / "exp99_probe"
    run.mkdir(parents=True)
    (run / "runner_state.json").write_text(json.dumps({
        "runner_version": "v3-test",
        "target_file": "bench/some_prose_target.md",
        "run_root": "/Users/original/machine/repo",
        "registry": {"entries": {"C0001": {
            "severity": 0.8, "description": "probe", "falsifier_code": "",
        }}},
    }))
    # execute the instrument's own harvest against a corpus of exactly this run
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "repro_supply", ROOT / "scripts" / "repro_supply_causes_2026-10-02.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["repro_supply"] = m
    spec.loader.exec_module(m)
    m.ROOT = tmp_path  # point the instrument at the synthetic corpus
    rows = m.entries()
    assert rows, "the instrument read nothing from the synthetic corpus"
    (_, tgt, _, _), = rows.values()
    assert tgt == "bench/some_prose_target.md", (
        f"the checkpoint's top-level target_file was not resolved: {tgt!r}")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
