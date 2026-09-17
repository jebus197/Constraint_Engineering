"""The producer for the per-sandbox cost figure is run, and measures what it says.

PANEL ROUND 16, 2026-09-17. "6.53 s and 606 MB per sandbox" justified 1 sandbox
per panel seat in `bench/confer_maths_panel_2026-09-05.py`, and nothing produced
it. `scripts/sandbox_build_cost_2026-09-17.py` now does. These tests run it on a
small tree of known size, so a script that timed nothing, measured the wrong
directory or left its copy behind goes red here. The figure for the real checkout
is whatever the script prints there on the day: `build` copies ignored and
untracked files too, so the size moves with the checkout's contents.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sandbox_build_cost_2026-09-17.py"


def _tree(tmp_path: Path) -> tuple[Path, int]:
    src = tmp_path / "src"
    (src / "bench").mkdir(parents=True)
    payload = {"bench/a.py": b"x" * 4096, "bench/b.txt": b"y" * 1000, "README.md": b"z" * 24}
    for rel, data in payload.items():
        (src / rel).write_bytes(data)
    return src, sum(len(d) for d in payload.values())


def test_it_measures_a_known_tree_and_removes_every_copy(tmp_path):
    spec = importlib.util.spec_from_file_location("sandbox_cost", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src, size = _tree(tmp_path)
    rows = mod.measure(src, runs=2)
    assert len(rows) == 2, rows
    for r in rows:
        assert r["apparent_bytes"] == size, (r, size)
        assert r["seconds"] > 0, r
        assert r["du_kib"] is not None and r["du_kib"] > 0, r
        assert r["removed"] and not Path(r["sandbox"]).exists(), (
            f"the sandbox copy was left on disk: {r['sandbox']}")
    assert rows[0]["sandbox"] != rows[1]["sandbox"], "2 builds reused 1 directory"


def test_the_command_line_prints_the_cost_and_exits_zero(tmp_path):
    src, _ = _tree(tmp_path)
    r = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(src)],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    assert re.search(r"^build 1\s*: \d+\.\d\d s, du \d+\.\d MiB, apparent "
                     r"0\.0 MB, torn down: True$", r.stdout, re.M), r.stdout


def test_help_builds_nothing_and_bad_input_is_refused(tmp_path):
    h = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, timeout=120)
    assert h.returncode == 0 and h.stdout.startswith("usage:"), h
    assert "build 1" not in h.stdout
    bad = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(tmp_path / "absent")],
                         capture_output=True, text=True, timeout=120)
    assert bad.returncode == 2 and "REFUSING" in bad.stderr, bad
