"""Task R2: the exp50/51 redesign must carry the fixes, and must not rewrite history.

Founder ruling 2026-08-22, verbatim: *"5: Redesign with all uncovered fixes in
place after the upcoming build experiment and any fixed it uncovers in place
also."* The precondition he attached -- the build experiment -- has been met, so
this is execution work.

"ALL UNCOVERED FIXES" WAS NOT A LIST ANYONE HAD WRITTEN DOWN, so it was derived
rather than recalled. The 3 exp56 arm files are the newest pre-registration
artefacts and postdate every fix in question, so a setting they all agree on is
the current convention and a difference is a candidate gap. Measured by
`scripts/exp50_51_redesign_gap_2026-09-10.py`: 14 of 68 settings out of step,
20.5882%, Wilson [12.6796%, 31.6423%].

THE ORIGINALS ARE NOT EDITED. Each declares "Frozen before the run", and neither
experiment has ever run -- the only exp50 directory in the archive is a draft
review. So the redesign sits BESIDE the frozen file rather than replacing it,
and every change carries its reason and its previous value.

NOT EVERY DIFFERENCE IS A GAP, which is why 3 are deliberately kept. max_rounds
16 is sized for a one-shot arc, not for 3 arms in sequence; immune memory is a
confound only ACROSS arms and these are single-arm.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PAIRS = [
    (ROOT / "bench/exp50_configs/50_physics_exam_live.json",
     ROOT / "bench/exp50_configs/50_physics_exam_live_redesigned_2026-09-10.json"),
    (ROOT / "bench/exp51_configs/51_biology_exam_live.json",
     ROOT / "bench/exp51_configs/51_biology_exam_live_redesigned_2026-09-10.json"),
]


def _load(p):
    if not p.is_file():
        pytest.skip(f"{p.name} not present in this clone")
    return json.loads(p.read_text(encoding="utf-8"))


class TestTheFrozenOriginalsAreUntouched:
    @pytest.mark.parametrize("orig,_new", PAIRS, ids=lambda p: Path(p).name)
    def test_the_original_still_declares_itself_frozen(self, orig, _new):
        d = _load(orig)
        assert "Frozen before the run" in d.get("_pre_registration", ""), (
            "the frozen pre-registration text is gone from the original")

    @pytest.mark.parametrize("orig,_new", PAIRS, ids=lambda p: Path(p).name)
    def test_the_original_keeps_its_original_values(self, orig, _new):
        d = _load(orig)
        assert d.get("sk_enabled") is True
        assert d.get("merge_arbitration_enabled") is True
        assert "target_kind" not in d, (
            "the original has been edited; the redesign must sit beside it")


class TestTheRedesignCarriesTheFixes:
    @pytest.mark.parametrize("_orig,new", PAIRS, ids=lambda p: Path(p).name)
    def test_target_kind_is_declared_not_inferred(self, _orig, new):
        assert _load(new).get("target_kind") == "prose", (
            "the test_article is a .md review document; leaving the kind to "
            "inference means the config does not say what it reviews")

    @pytest.mark.parametrize("_orig,new", PAIRS, ids=lambda p: Path(p).name)
    def test_sk_matches_what_the_runner_would_enforce(self, _orig, new):
        """Declaring true on a prose target reproduces the 2026-08-01 defect.

        The runner forces S_k off for a non-Python target and logs it, so a
        config declaring true is stating something that will not happen. That is
        the exact pattern that note records: "sk_enabled is TRUE in all eight
        queued prose configs, against a code default of FALSE".
        """
        assert _load(new).get("sk_enabled") is False

    @pytest.mark.parametrize("_orig,new", PAIRS, ids=lambda p: Path(p).name)
    def test_the_dead_merge_path_is_not_enabled(self, _orig, new):
        assert _load(new).get("merge_arbitration_enabled") is False

    @pytest.mark.parametrize("_orig,new", PAIRS, ids=lambda p: Path(p).name)
    def test_routing_is_declared_rather_than_defaulted(self, _orig, new):
        assert _load(new).get("routing_enabled") is True


class TestEveryChangeCarriesItsReason:
    @pytest.mark.parametrize("_orig,new", PAIRS, ids=lambda p: Path(p).name)
    def test_the_redesign_block_records_what_changed_and_why(self, _orig, new):
        r = _load(new).get("_redesign_2026_09_10")
        assert r, "the redesign carries no record of itself"
        for key in ("ruling", "supersedes", "changed", "deliberately_unchanged",
                    "measured_gap", "not_run"):
            assert key in r, f"the redesign record is missing {key}"
        for field, rec in r["changed"].items():
            assert {"was", "now", "why"} <= set(rec), field
            assert len(rec["why"]) > 60, (
                f"{field}: the reason is too short to be a reason")

    @pytest.mark.parametrize("_orig,new", PAIRS, ids=lambda p: Path(p).name)
    def test_what_was_deliberately_kept_says_why(self, _orig, new):
        """A difference left in place must be a decision, not an oversight."""
        r = _load(new)["_redesign_2026_09_10"]
        assert set(r["deliberately_unchanged"]) >= {
            "max_rounds", "extension_cap", "immune_memory_enabled"}


class TestNothingWasDispatched:
    @pytest.mark.parametrize("_orig,new", PAIRS, ids=lambda p: Path(p).name)
    def test_the_redesign_says_running_it_is_the_founders_call(self, _orig, new):
        d = _load(new)
        assert len(d.get("models", [])) >= 5, "the paid roster is still declared"
        assert "money" in d["_redesign_2026_09_10"]["not_run"].lower()
