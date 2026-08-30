"""A note about a model spec must never stop a run starting.

THE DEFECT, 2026-08-31, and it killed a run 55 seconds after launch.

Fable's MODEL_SPECS entry was given a `_provenance` key recording that its
values are INHERITED from CC2 rather than measured -- exactly the honesty the
founder asked for when accepting inherited values. `build_model_specs` then does
``ModelSpec(**params)``, so the note was passed as a constructor argument:

    TypeError: ModelSpec.__init__() got an unexpected keyword argument '_provenance'

A spec table that cannot carry a note ABOUT ITSELF invites the note to be dropped
instead, which is how provenance is lost. So the constructor filters
underscore-prefixed keys as metadata rather than the table losing its note.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v2 as R
from runner_core import MODEL_SPECS, build_model_specs


def _panel(labels):
    return R.ExperimentConfig(
        models=[R.ModelConfig(label=l, model_id="sim", api="sim", role="player",
                              system_prompt_path="") for l in labels],
        logs_dir="/tmp", budget_limit=0.0, cdsfl_system_prompt="")


class TestMetadataIsCarriedAndIgnored:
    def test_the_provenance_note_is_still_in_the_table(self):
        """It is the record that Fable's numbers are inherited, not measured."""
        assert "_provenance" in MODEL_SPECS["Fable"]
        assert "inherited" in MODEL_SPECS["Fable"]["_provenance"].lower()

    def test_a_spec_with_metadata_still_constructs(self):
        specs = build_model_specs(_panel(["Fable"]))
        assert len(specs) == 1

    def test_the_whole_six_model_sim_panel_constructs(self):
        labels = [f"{v}-SIM" for v in
                  ("CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable")]
        assert len(build_model_specs(_panel(labels))) == 6

    def test_an_arbitrary_new_metadata_key_does_not_break_it(self):
        """The fix must be general, not a special case for _provenance."""
        MODEL_SPECS["Fable"]["_added_by_a_later_editor"] = "some note"
        try:
            assert len(build_model_specs(_panel(["Fable"]))) == 1
        finally:
            MODEL_SPECS["Fable"].pop("_added_by_a_later_editor", None)

    def test_real_fields_are_still_passed_through(self):
        """Filtering metadata must not silently drop the tuning values."""
        spec = build_model_specs(_panel(["Fable"]))[0]
        assert getattr(spec, "tau", None) == MODEL_SPECS["Fable"]["tau"]
        assert getattr(spec, "L", None) == MODEL_SPECS["Fable"]["L"]
