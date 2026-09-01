"""A simulated run must not be able to reach a real API, by ANY dispatch route.

THE SECOND PRIMITIVE, 2026-09-01. The shim patched `dispatch_to_model` and the
lesson recorded on 2026-08-30 was "patch the primitive, not the call sites".
That was right and incomplete: there are TWO primitives. `_multiturn_fallback`
does not call `dispatch_to_model` at all -- it calls `decomposed_dispatch`,
which owns a separate API table listing google, openrouter, deepseek and
codex_exec. A simulated ModelConfig carries api="sim", so the first time the
runner fell back to the multi-turn path every agent died on
`ValueError: Unknown API: sim`.

Measured on the first launch of the final exp45 run: 5 of 6 agents failed in
Round 0, before a single finding was produced, on a runner reported green.

These tests do not just add the missed case. They enumerate the API tables the
runner can reach and require the shim to cover each, so a THIRD primitive
introduced later fails here rather than in a live run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R          # noqa: E402
from bench.tools import sim_dispatch_shim as S   # noqa: E402


@pytest.fixture
def shimmed():
    originals = S.install(timeout=5)
    try:
        yield
    finally:
        S.restore(originals)


def _sim_model(label="CC2"):
    return R.ModelConfig(label=label, model_id="sim", api="sim",
                         role="player", system_prompt_path=None,
                         max_tokens=256, timeout=5)


def _stub(reply="SIM REPLY"):
    """Stand in for the dispatch shim. The shim itself spawns a real agent --
    correctly, which is why netguard denies it inside the suite."""
    def _d(mc, prompt, cdsfl_text, **kw):
        return reply, 0.01
    return _d


class TestEveryPrimitiveIsPatched:

    def test_dispatch_to_model_is_patched(self, shimmed):
        assert R.dispatch_to_model.__name__ == "_dispatch"

    def test_multiturn_fallback_is_patched(self, shimmed):
        assert R._multiturn_fallback.__name__ == "_mt", (
            "the multi-turn path is unpatched; it reaches decomposed_dispatch, "
            "whose API table has never heard of 'sim'")

    def test_decomposed_dispatch_is_patched(self, shimmed):
        assert R.decomposed_dispatch.__name__ == "_dd"

    def test_restore_puts_all_three_back(self):
        before = (R.dispatch_to_model, R._multiturn_fallback,
                  R.decomposed_dispatch)
        S.restore(S.install(timeout=5))
        assert (R.dispatch_to_model, R._multiturn_fallback,
                R.decomposed_dispatch) == before

    def test_restore_still_accepts_a_bare_callable(self):
        """install() returned one value before 2026-09-01."""
        original = R.dispatch_to_model
        R.dispatch_to_model = lambda *a, **k: None
        S.restore(original)
        assert R.dispatch_to_model is original


class TestTheApiTablesAreEnumeratedNotAssumed:
    """If a new primitive with its own API table appears, fail HERE."""

    #: Every function that owns an `Unknown API` table and is reachable from a
    #: run, mapped to the shim attribute that must stand in for it.
    KNOWN = {
        "decomposed_dispatch": "decomposed_dispatch",
    }

    def test_no_unlisted_api_table_is_reachable_from_the_runner(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(
            encoding="utf-8")
        imported = set(re.findall(
            r"^from\s+(\w+)\s+import\s+\(?([^)\n]*)", src, re.M))
        reachable = set()
        for module, names in imported:
            mod_path = REPO / "bench" / f"{module}.py"
            if not mod_path.is_file():
                continue
            body = mod_path.read_text(encoding="utf-8", errors="replace")
            if 'raise ValueError(f"Unknown API' not in body:
                continue
            for name in (n.strip() for n in names.split(",")):
                if name and re.search(rf"^def {re.escape(name)}\b", body, re.M):
                    reachable.add(name)
        unlisted = reachable - set(self.KNOWN)
        assert not unlisted, (
            f"these functions own an 'Unknown API' table, are imported by the "
            f"runner, and are NOT declared in KNOWN: {sorted(unlisted)}. Each "
            f"is a route by which a simulated run can hit a real API table and "
            f"die on api='sim'. Add it to KNOWN and patch it in the shim.")

    def test_every_known_table_is_actually_patched(self, shimmed):
        for _fn, attr in self.KNOWN.items():
            patched = getattr(R, attr)
            assert patched.__module__.endswith("sim_dispatch_shim"), (
                f"{attr} is declared as needing the shim but is not patched")


class TestTheMultiturnPathSurvivesASimulatedModel:

    def test_it_does_not_raise_unknown_api(self, shimmed, tmp_path,
                                           monkeypatch):
        """The exact Round 0 failure, reproduced."""
        monkeypatch.setattr(R, "_multiturn_fallback",
                            S.make_multiturn_shim(_stub()))
        out = R._multiturn_fallback(
            _sim_model(), "find defects", "directives", "=== TARGET ===\ncode",
            0, "pattern", tmp_path)
        assert out is not None, "the multi-turn path returned nothing"
        text, elapsed = out
        assert text == "SIM REPLY"
        assert isinstance(elapsed, float)

    def test_the_real_path_would_have_raised(self):
        """Proves the test above is testing something: unshimmed, it dies."""
        from decomposed_dispatch import decomposed_dispatch, DecomposedChunk
        with pytest.raises(ValueError, match="Unknown API"):
            decomposed_dispatch(api="sim", model_id="sim", system_prompt="",
                                chunks=[DecomposedChunk(content="x",
                                                        label="t")],
                                final_instruction="go")

    def test_the_decomposed_backstop_returns_a_result(self):
        from decomposed_dispatch import DecomposedChunk
        res = S.make_decomposed_shim(_stub())(
            api="sim", model_id="sim", system_prompt="sys",
            chunks=[DecomposedChunk(content="chunk one", label="t0")],
            final_instruction="synthesise")
        assert res.chunks_delivered == 1
        assert res.api == "sim"
