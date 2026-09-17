"""Task 9.4, panel round 16: a simulated panel is not several architectures.

THE DEFECT. The `cross_architecture_correlation` item of `study_programme_report`
counted distinct `source_model` values, which are SEAT LABELS
(`ModelSpec(model_id=mc.label)` in `bench/runner_core.py`), and never read its
`cfg` argument. A 6-seat panel labelled `CC2-SIM` through `Gemini-SIM` therefore
reported `answerable: True` with 6 "distinct" models, although
`bench/tools/sim_dispatch_shim.make_shim` answers every simulated seat with 1
model. Every archived report whose seats all carry `-SIM` got `answerable: True`.
The 2 tests that covered the refusal fed labels, never architectures: 1 literal
label refused, 3 labels were accepted.

THE FIX, IN THE SAME FUNCTION. The item now refuses when `run_is_simulated`
holds for the run's `cfg` or for the labels the registry recorded, and it
resolves labels through `registry.resolve_model` (the seat-identity map built
from each seat's model id and route) when the registry has one, so 2 labels on
1 model count once.

EVERY CASE BELOW EXECUTES THE FUNCTION. Nothing here reads source text.
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

import reference_runner_v3 as rr  # noqa: E402

SIM45 = ROOT / "bench" / "logs" / "sim45_memory_20260908T033008Z" / "sim45_memory_report.json"


def _all_sim_reports() -> list[str]:
    """Every archived report whose registry entries all carry a `-SIM` seat label."""
    out = []
    for f in sorted(glob.glob(str(ROOT / "bench" / "logs" / "*" / "*_report.json"))):
        try:
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        reg = d.get("registry") if isinstance(d, dict) else None
        ent = reg.get("entries") if isinstance(reg, dict) else None
        if not isinstance(ent, dict) or not ent:
            continue
        labels = {e.get("source_model") for e in ent.values()
                  if isinstance(e, dict) and e.get("source_model")}
        if labels and all(str(s).endswith("-SIM") for s in labels):
            out.append(str(pathlib.Path(f).relative_to(ROOT)))
    return out


SIM_REPORTS = _all_sim_reports()


def _item(registry, cfg=None):
    return rr.study_programme_report(registry, cfg)["cross_architecture_correlation"]


def _from_report(path):
    d = json.loads((ROOT / path).read_text(encoding="utf-8"))
    reg = rr.FindingRegistry.from_dict(d["registry"])
    return reg, types.SimpleNamespace(models=list(d.get("models") or []))


class TestASimulatedPanelIsRefused:
    def test_the_tracked_sim45_report(self):
        if not SIM45.is_file():
            pytest.skip("the sim45 report is not in this clone")
        reg, cfg = _from_report(str(SIM45.relative_to(ROOT)))
        assert rr.run_is_simulated(cfg) is True
        item = _item(reg, cfg)
        assert item["answerable"] is False, item
        assert "stand-in" in item["why_not"], item["why_not"]

    @pytest.mark.parametrize("path", SIM_REPORTS or [pytest.param(
        None, marks=pytest.mark.skip(reason="no all-SIM reports in this clone"))])
    def test_every_archived_all_sim_report(self, path):
        reg, cfg = _from_report(path)
        assert _item(reg, cfg)["answerable"] is False, path

    def test_every_archived_all_sim_report_even_without_its_cfg(self):
        """The registry's own labels carry the -SIM marker, so a caller that
        passes no cfg still gets a refusal."""
        if not SIM_REPORTS:
            pytest.skip("no all-SIM reports in this clone")
        for path in SIM_REPORTS:
            reg, _ = _from_report(path)
            assert _item(reg, None)["answerable"] is False, path

    def test_a_constructed_6_label_sim_panel(self):
        labels = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM",
                  "Fable-SIM", "Gemini-SIM"]
        reg = rr.FindingRegistry()
        for i, label in enumerate(labels, 1):
            reg.entries[f"C{i:04d}"] = {"severity": 0.5, "source_model": label}
        item = _item(reg, types.SimpleNamespace(models=labels))
        assert item["answerable"] is False
        assert len(item["distinct_source_models"]) == 6, (
            "the labels are still listed; only the conclusion drawn from them changed")


class TestLabelsResolveToModels:
    @staticmethod
    def _registry(identity):
        reg = rr.FindingRegistry()
        for i, label in enumerate(identity, 1):
            reg.entries[f"C{i:04d}"] = {"severity": 0.8, "source_model": label}
        reg.model_identity = dict(identity)
        return reg

    def test_control_3_labels_on_3_models_stay_answerable(self):
        reg = self._registry({"CC2": "opus@claude_cli",
                              "Gemini": "google/gemini-3.1-pro-preview@openrouter",
                              "DeepSeek": "deepseek-v4-pro@deepseek"})
        item = _item(reg, types.SimpleNamespace(models=["CC2", "Gemini", "DeepSeek"]))
        assert item["answerable"] is True, item
        assert item["why_not"] is None

    def test_2_labels_on_1_model_are_1_architecture(self):
        reg = self._registry({"Codex": "openai/gpt-5.5@openrouter",
                              "ChatGPT": "openai/gpt-5.5@openrouter"})
        item = _item(reg, types.SimpleNamespace(models=["Codex", "ChatGPT"]))
        assert item["answerable"] is False, item
        assert "resolve" in item["why_not"], item["why_not"]
