"""Every run report must say which code produced it.

The v3 note of 2026-08-23 (`scripts/apply_v3.py`) states the design: "The VERSION
is metadata, and it lands in each run's report, which is where a reader actually
needs it."

It never landed. Checked 2026-08-30: `exp55_v3_control`'s report — the only run
made on v3.0 — carries no version key of any kind, so its results cannot be
attributed to the code that produced them without git archaeology.
"""
import ast
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R   # noqa: E402


def test_the_runner_declares_a_version():
    assert hasattr(R, "RUNNER_VERSION")
    assert R.RUNNER_VERSION.startswith("v"), R.RUNNER_VERSION


def test_the_version_is_written_into_the_result_dict():
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "run_experiment")
    body = ast.unparse(fn).replace('"', "'")
    assert "'runner_version': RUNNER_VERSION" in body, (
        "run_experiment does not write runner_version into its result")


def test_the_banner_and_the_constant_agree():
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    banner = src[:4000]
    assert f"RUNNER VERSION {R.RUNNER_VERSION}" in banner, (
        f"the docstring banner and RUNNER_VERSION={R.RUNNER_VERSION!r} disagree")


def test_the_only_v3_era_run_predates_this_and_is_recorded_as_such():
    """Not a defect to fix — a fact to keep visible. exp55_v3_control ran before
    the version was recorded, so it has none, and that is why this guard exists."""
    d = sorted((REPO / "bench" / "logs").glob("exp55_v3_control_*"))
    if not d:
        return
    rep = [p for p in d[0].glob("*_report.json") if ".errata" not in str(p)]
    if not rep:
        return
    r = json.loads(rep[0].read_text(encoding="utf-8"))
    assert "runner_version" not in r, (
        "exp55_v3_control now has a version key — if it was backfilled, that is a "
        "provenance claim about a run nobody can verify")
