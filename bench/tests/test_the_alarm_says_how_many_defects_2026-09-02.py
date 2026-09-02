"""An alarm that says "3 criticals" when there are 2 defects reads as 3 crises.

Fable, panel review 2026-09-02, on the run that raised this alarm: the
16-finding registry contained about four distinct defects. The falsifier bodies
fell into three byte-identical groups of five, plus one singleton -- six seats
reporting the same plants, with nothing upstream merging them. Every item in the
irreducible queue was a duplicate of a defect the routing ladder had confirmed
in the same round.

So the queue size was real as a count and misleading as a diagnosis, and the
bundle handed to the human said nothing about it. The upstream fault is
cross-model duplicate handling; the alarm now says so when it is true.

Grouping is on the falsifier body, which is the project's own criterion: an
identical falsifier is by construction the same defect.

Also pinned here: `routing_history`, which the alarm has always attached and
which was written NOWHERE in the codebase -- empty in every archived alarm
across three runs. The one question a human opening the bundle needs answered,
why these rungs failed on this finding, could not be answered from the artefact.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture(scope="module")
def src():
    return RUNNER.read_text(encoding="utf-8")


class TestTheBundleCountsDefectsNotJustItems:
    def test_it_reports_a_distinct_defect_count(self, src):
        assert '"distinct_defects"' in src, (
            "the bundle reports item count only; a reader cannot tell three "
            "crises from one defect reported three times")

    def test_it_lists_the_duplicate_groups(self, src):
        assert '"duplicate_groups"' in src

    def test_it_groups_on_the_falsifier_body(self, src):
        i = src.index("HOW MANY DISTINCT DEFECTS, NOT HOW MANY ITEMS")
        block = src[i:i + 2200]
        assert '.get("falsifier_code")' in block and "registry.entries" in block, (
            "grouping must read the falsifier body from the REGISTRY -- the "
            "evidence bundle carries only falsifier_present, so keying on the "
            "dict silently gives every item its own group")

    def test_items_without_a_falsifier_are_not_merged_together(self, src):
        """Two undiagnosed items are not evidence of one defect."""
        i = src.index("HOW MANY DISTINCT DEFECTS, NOT HOW MANY ITEMS")
        block = src[i:i + 2200]
        assert "__no_falsifier__" in block, (
            "findings with no falsifier must key on their own id, or every "
            "undiagnosed item collapses into a single phantom defect")

    def _alarm(self, falsifiers):
        """Build a real alarm bundle over entries carrying `falsifiers`."""
        import reference_runner_v3 as R
        reg = R.FindingRegistry()
        for n, body in enumerate(falsifiers, start=1):
            f = R.Finding(finding_id=f"M_F{n:03d}", model_id="M", round_idx=0,
                          flaw_class=1, severity=0.9, abstraction_index=0.5,
                          description=f"a critical finding number {n}",
                          verified=False, origin_type="model")
            reg.register(f, "M")
        for cid, e in reg.entries.items():
            e["irreducible_escalation"] = True
            e["status"] = "OPEN"
        for (cid, e), body in zip(reg.entries.items(), falsifiers):
            e["falsifier_code"] = body
        cfg = R.RunnerConfig()
        cfg.max_irreducible_queue = 2
        return R.build_irreducible_queue_alarm(reg, cfg, 0)

    def test_three_items_sharing_one_falsifier_report_one_defect(self):
        """The measured case: 3 locked items, 1 underlying defect."""
        a = self._alarm(["assert broken()", "assert broken()", "assert broken()"])
        assert a is not None, "queue of 3 over a bound of 2 must raise the alarm"
        assert a["count"] == 3
        assert a["distinct_defects"] == 1, (
            f"three identical falsifiers are one defect, got "
            f"{a['distinct_defects']}")
        assert "cross-model duplicate handling" in a["duplicate_note"]

    def test_genuinely_distinct_items_say_the_queue_is_real(self):
        a = self._alarm(["assert one()", "assert two()", "assert three()"])
        assert a["distinct_defects"] == 3
        assert "queue size is real" in a["duplicate_note"], (
            "when no two items share a falsifier the note must say the size is "
            "real, or the annotation becomes an excuse for any queue")
        assert not a["duplicate_groups"]

    def test_undiagnosed_items_do_not_collapse_into_one_phantom(self):
        """Three items with no falsifier are three unknowns, not one defect."""
        a = self._alarm(["", "", ""])
        assert a["distinct_defects"] == 3, (
            "items carrying no falsifier keyed together, so three undiagnosed "
            "findings read as a single defect")


class TestTheRoutingEvidenceIsActuallyWritten:
    def test_routing_history_is_appended_by_the_router(self, src):
        assert 'e.setdefault("routing_history", []).append(' in src, (
            "the alarm attaches routing_history and nothing writes it; the "
            "decisive tool verdicts of a falsification methodology are then "
            "off the record")

    def test_it_records_what_a_human_would_need(self, src):
        i = src.index('e.setdefault("routing_history", []).append(')
        block = src[i:i + 1100]
        for key in ("verdict", "model_used", "rungs_tried", "rungs_available",
                    "last_falsifier_code"):
            assert f'"{key}"' in block, f"routing_history omits {key}"

    def test_rungs_available_is_recorded_next_to_rungs_tried(self, src):
        """Two of five asked reads very differently from two of two."""
        i = src.index('e.setdefault("routing_history", []).append(')
        block = src[i:i + 1100]
        assert '"rungs_available"' in block and '"rungs_tried"' in block, (
            "without both, 'the ladder was exhausted' cannot be checked")

    def test_it_cannot_fell_a_run(self, src):
        i = src.index('e.setdefault("routing_history", []).append(')
        assert "except Exception" in src[i:i + 1600]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
