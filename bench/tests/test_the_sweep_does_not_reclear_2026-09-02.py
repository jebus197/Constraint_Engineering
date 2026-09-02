"""A finding cleared by one model must not be cleared again by the next.

Fable, panel review 2026-09-02, reproduced this against the real
`_post_convergence_sweep`: on a 16-entry registry the sweep reported
`cleared: 27`.

Three faults compounded. At the sweep's scope `_TERMINAL` is
{MERGED, CLOSED, REFUTED, DUPLICATE} and does NOT contain CONFIRMED, so a
finding cleared to CONFIRMED still passed the guard. The match loop checked
status but never `_handled`. And the prompt was built once before the model
loop, so every model was handed the full residual list including everything
earlier models had already cleared -- `live` was computed and thrown away.

The consequences were not cosmetic: the falsifier was re-executed (paid model
code, run twice), the cleared count inflated, and `resolved_by_sweep` was
overwritten by whichever model happened to be dispatched last. Fable: "all 27 by
DeepSeek-SIM is unreliable -- CC2-SIM was dispatched first and may have cleared
up to 11 of them and had the credit stolen." Unrecoverable afterwards, because
sweep replies are persisted nowhere.
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture(scope="module")
def sweep_src():
    src = RUNNER.read_text(encoding="utf-8")
    i = src.index("def _post_convergence_sweep")
    j = src.index("\ndef ", i + 10)
    return src[i:j]


class TestTheGuardStopsARepeatClear:
    def test_handled_is_checked_in_the_match_loop(self, sweep_src):
        i = sweep_src.index("FALSIFIER:")
        block = sweep_src[i:i + 2600]
        assert "cid in _handled" in block, (
            "the match guard checks status only, and CONFIRMED is not terminal "
            "at this scope, so every later model re-clears the same finding")

    def test_confirmed_really_is_absent_from_this_scopes_terminal_set(self, sweep_src):
        """If this ever changes, the _handled guard becomes belt-and-braces."""
        m = re.search(r"_TERMINAL\s*=\s*\{([^}]*)\}", sweep_src)
        assert m, "the sweep no longer defines its own _TERMINAL"
        assert "CONFIRMED" not in m.group(1), (
            "CONFIRMED is now terminal here; re-check whether the _handled "
            "guard is still the thing preventing re-clears")


class TestThePromptReflectsWhatIsStillLive:
    def test_it_is_built_inside_the_model_loop(self, sweep_src):
        i = sweep_src.index("for mc in exp_config.models:")
        after = sweep_src[i:i + 1400]
        assert "_sweep_prompt(live," in after, (
            "the prompt must be built from `live` inside the loop; built once "
            "outside it, every model is shown work already done")

    def test_it_is_not_also_built_before_the_loop(self, sweep_src):
        i = sweep_src.index("for mc in exp_config.models:")
        before = sweep_src[:i]
        assert "_sweep_prompt(residuals," not in before, (
            "the pre-loop build is back; `live` is then computed and discarded")

    def test_live_is_actually_used(self, sweep_src):
        """It was computed and thrown away, which is how the defect hid."""
        assert sweep_src.count("_sweep_prompt(live,") >= 1


class TestAttributionSurvives:
    def test_a_cleared_finding_is_not_reattributed(self, sweep_src):
        """resolved_by_sweep was overwritten by whichever model went last."""
        i = sweep_src.index("resolved_by_sweep")
        block = sweep_src[max(0, i - 1200):i + 400]
        assert "cid in _handled" in block, (
            "nothing prevents a later model overwriting the attribution of a "
            "finding an earlier model cleared")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
