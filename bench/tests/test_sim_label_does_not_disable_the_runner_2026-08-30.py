"""A simulated panel label must not silently switch machinery off.

WHY THIS EXISTS
---------------
Founder ruling 2026-08-08 mandates the ``-SIM`` suffix on every simulated panel
member. Two places in ``reference_runner_v3`` compared ``mc.label`` to the exact
string ``"CC2"``, so honouring the naming rule would have DISABLED them:

  * ``_verify_batch_with_cc2`` returns ``{"skipped": True, "reason": "CC2 config
    not found"}`` -- a capability lost with no error and no warning. This is the
    config-drop class (a key honoured in one place, dropped in another), which
    this project has now hit 8 times.
  * the dispatch wall-clock multiplier silently drops from x5 to x3.

So the naming rule and the runner were in direct conflict: obey one, break the
other. ``base_model_label`` resolves it. These tests pin BOTH halves -- that the
suffix is resolved, and that resolving it does not swallow a genuinely absent
config.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v3 as R


class TestBaseLabel:
    def test_suffix_is_stripped(self):
        assert R.base_model_label("CC2-SIM") == "CC2"
        assert R.base_model_label("DeepSeek-SIM") == "DeepSeek"

    def test_real_label_is_untouched(self):
        assert R.base_model_label("CC2") == "CC2"
        assert R.base_model_label("Gemini") == "Gemini"

    def test_a_missing_label_does_not_crash(self):
        """Refuted the first version of this fix on 2026-08-30: None crashed it."""
        assert R.base_model_label(None) == ""

    def test_suffix_is_not_stripped_from_the_middle(self):
        assert R.base_model_label("SIM-CC2") == "SIM-CC2"


class TestTheVerificationStageStillResolves:
    def _cfgs(self, labels):
        return [R.ModelConfig(label=l, model_id="sim", api="sim", role="player",
                              system_prompt_path="")
                for l in labels]

    def test_sim_labelled_cc2_is_found(self):
        found = [mc for mc in self._cfgs(["Gemini-SIM", "CC2-SIM"])
                 if R.base_model_label(mc.label) == "CC2"]
        assert len(found) == 1 and found[0].label == "CC2-SIM"

    def test_a_panel_with_no_cc2_at_all_is_still_correctly_empty(self):
        """The fix must not make every label look like CC2."""
        found = [mc for mc in self._cfgs(["Gemini-SIM", "Codex-SIM"])
                 if R.base_model_label(mc.label) == "CC2"]
        assert found == []


class TestTheReportIsHonestAboutSimulation:
    def test_a_sim_label_is_described_as_simulated(self):
        d = R.describe_model("CC2-SIM")
        assert "SIMULATED" in d and "no paid dispatch" in d

    def test_a_real_label_is_not_labelled_simulated(self):
        assert "SIMULATED" not in R.describe_model("CC2")
