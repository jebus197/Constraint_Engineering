"""Task A19: a computable fragment inside prose can now be scored, behind a flag.

THE FOUNDER'S DESIGN POINT, 2026-09-10, verbatim: *"Having the admissibility
switch off for prose targets is also questionable, as clearly it should simply
mark a purely prose input as 'inadmissible', while still solving any
computationally reducible elements within that prose! This is STEM. No one will
be using CDSFL to write poetry!"*

`compute_sk` short-circuited to NO_SCORE on any prose target, and its docstring
gave 3 reasons -- all of them about gates reading ENGLISH as Python. TWO OF THE
THREE WERE REPAIRABLE AND ARE REPAIRED.

  e3_ruff  error-recovered over markdown. MEASURED on a real design note,
           `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`: **311 diagnostics over the
           whole file against 4 over the fenced listings extracted from it.**
  e4_bandit could not parse the file at all -- it returned a syntax error and NO
           metrics, so the gate reported "0 HIGH / 0 MEDIUM" forever at weight
           2.0, the heaviest in the set. **Structurally incapable of failing**,
           which is worse than unavailable: an unavailable gate is excluded from
           the weighted mean, and a gate that always passes drags it up. Handed
           the extracted listings it can parse -- e4 = 0.5 on a real HIGH.
  e2_regression STILL UNAVAILABLE. Prose targets live outside the repository and
           no prose config sets `test_cmd`. That reason stands, and is not
           claimed to be fixed.

THE EXTRACTOR IS NOT NEW. `_gateable_source` was written on 2026-08-01 for the
HARD gates g1 and g2, after ast.parse choking on a markdown table scored A=0.0
for 50 straight fixes. The effect gates were simply never handed it -- half the
machinery repaired, the other half still reading prose as Python for 41 days.

DEFAULT OFF, DELIBERATELY. This changes what reaches a verdict, and that is the
founder's call. `sk_score_prose_listings` is False on `RunnerConfig`, threaded
through `_evaluate_sk_for_findings` to `compute_sk`, and read with `getattr` so
an older config object cannot break the call.

AND "PURELY PROSE" STILL MEANS NO_SCORE, which is his own distinction: a target
with no fenced listing has nothing computationally reducible in it, and returns
NO_SCORE whatever the flag says.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import bench.reference_runner_v3 as R  # noqa: E402

FIX = ("<<<<<<< SEARCH\ndef f():\n    return 1\n=======\n"
       "def f():\n    return 2\n>>>>>>> REPLACE")
PROSE_WITH_CODE = "# note\n\nprose\n\n```python\ndef f():\n    return 1\n```\n"
PURE_PROSE = "# note\n\njust prose, and no listing anywhere in it.\n"


class TestTheFlagIsOffByDefault:
    def test_the_config_field_defaults_false(self):
        cfg = R.RunnerConfig(experiment_name="x", models=[])
        assert cfg.sk_score_prose_listings is False

    def test_a_prose_target_still_returns_no_score(self):
        r = R.compute_sk(FIX, PROSE_WITH_CODE, "notes/design.md", baseline={})
        assert r.tristate == "NO_SCORE", r.tristate


class TestTheFlagOnScoresReducibleProse:
    def test_a_listing_bearing_target_is_scored(self):
        r = R.compute_sk(FIX, PROSE_WITH_CODE, "notes/design.md", baseline={},
                         score_prose_listings=True)
        assert r.tristate != "NO_SCORE", (
            "the flag is on and the target carries a fenced listing, so S_k "
            "should have an opinion")

    def test_purely_prose_is_still_no_score_with_the_flag_on(self):
        """HIS OWN DISTINCTION. A target with nothing reducible in it is
        unscoreable, not defective."""
        r = R.compute_sk(FIX, PURE_PROSE, "notes/design.md", baseline={},
                         score_prose_listings=True)
        assert r.tristate == "NO_SCORE", r.tristate


class TestTheGatesNowSeeCodeRatherThanEnglish:
    def test_ruff_reads_the_listings_not_the_prose(self):
        """The 311-versus-4 measurement, re-derived rather than quoted."""
        spec = ROOT / "bench" / "BUILD_BOT_TEST_BENCH_FIX_SPEC.md"
        if not spec.is_file():
            pytest.skip("the measured file is not in this checkout")
        src = spec.read_text(encoding="utf-8", errors="replace")
        extracted, why = R._gateable_source(src, str(spec))
        assert extracted is not None and "fenced listing" in why
        assert len(extracted) < len(src) / 2, (
            "the extraction is no longer removing the prose")

    def test_bandit_can_fail_on_a_prose_target(self):
        """THE CONTROL THAT MATTERS. Before the repair this gate was
        structurally incapable of failing on prose, at the heaviest weight in
        the set."""
        base = {"high": 0, "medium": 0}
        clean = "# note\n\n```python\ndef f(cmd):\n    return 1\n```\n"
        evil = ("# note\n\n```python\nimport subprocess\n"
                "def f(cmd):\n    subprocess.call(cmd, shell=True)\n```\n")
        ok, _d = R._run_effect_bandit(clean, base, source_path="notes/x.md")
        bad, detail = R._run_effect_bandit(evil, base, source_path="notes/x.md")
        assert ok == 1.0, ok
        assert bad is not None and bad < 1.0, (
            f"bandit still cannot fail on a prose target: {bad} {detail}")
        assert "1 HIGH" in detail, detail

    def test_a_python_target_is_untouched(self):
        """BLAST RADIUS. `_gateable_source` returns a Python source unchanged,
        so this repair cannot move any existing measurement."""
        py = (ROOT / "bench" / "repo_paths.py").read_text(encoding="utf-8")
        out, why = R._gateable_source(py, "bench/repo_paths.py")
        assert out == py and why == "python target"

    def test_a_target_with_no_code_makes_the_gates_unavailable(self):
        """NOT zero, and the difference is the whole point: an unavailable gate
        is excluded from the weighted mean; a gate scoring 1.0 drags it up."""
        e3, d3 = R._run_effect_ruff(PURE_PROSE, 0, source_path="notes/x.md")
        e4, d4 = R._run_effect_bandit(PURE_PROSE, {"high": 0, "medium": 0},
                                      source_path="notes/x.md")
        assert e3 is None and "not applicable" in d3, (e3, d3)
        assert e4 is None and "not applicable" in d4, (e4, d4)


class TestTheFlagIsReachedFromAConfig:
    def test_the_runner_threads_it_from_cfg(self):
        """An addition nothing reaches is not additive."""
        import ast
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "run_experiment":
                body = ast.get_source_segment(src, node) or ""
                assert "sk_score_prose_listings" in body, (
                    "run_experiment no longer passes the flag, so a config that "
                    "sets it would be ignored")
                return
        raise AssertionError("run_experiment is gone")

    def test_compute_sk_accepts_it(self):
        import inspect
        assert "score_prose_listings" in inspect.signature(R.compute_sk).parameters
        assert "score_prose_listings" in inspect.signature(
            R._evaluate_sk_for_findings).parameters
