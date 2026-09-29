"""rho must count DISTINCT DEFECTS, and must be computed after corroboration exists.

THE TWO DEFECTS THIS PINS, both found by the simulated shakedown on 2026-09-29 and
both repaired on the founder's option-3 ruling.

1. THE OVERLAP RECORD WAS STARVED. `occasions` was appended only inside a merge
   path, and merges are withheld pending a tool verdict that nothing supplies. On
   shakedown arm 1, 53 of 53 canonicals carried exactly 1 occasion -- multi-
   occasion 0 of 53, Wilson [0.0000%, 6.7582%] -- while the SAME run recorded 10
   corroboration events across 8 canonicals in `codiscovery`. The signal was
   arriving and landing in a field nothing counted.

2. rho WAS COMPUTED BEFORE THE SETTLE PASS THAT CORRECTS ITS OWN NUMERATOR.
   `_compute_rho` ran at the registration site; ~690 lines later the settle pass
   overwrote `novelty_counts[-1]`, rho's numerator, and rho was never recomputed.
   Measured over 49 archived runs and 406 rounds by
   `scripts/rho_computed_before_the_settle_2026-09-29.py`: 25 rounds carried a rho
   disagreeing with their own stored numerator, 6.1576%, Wilson [4.2053%,
   8.9318%], and the direction is unanimous -- 25 of 25 OVERSTATEMENTS, Wilson
   [86.6808%, 100.0000%], mean -0.2066, worst -0.5000.

WHY THESE ARE ONE FIX AND NOT TWO. Option 3 counts novelty from the overlap
record. That record is not complete for round K until the triage pipeline has run
and `record_codiscovery` has fired -- which is after the counter. A counter keyed
on `occasions` at the registration site would see only earlier rounds, which the
alias map already covered. So the recomputation after the settle is a PRECONDITION
of option 3, not separate scope.

THESE TESTS EXECUTE BOTH FORMS AND COMPARE OUTPUTS (`execute-do-not-grep`,
founder ruling 2026-09-04). Four defects in this project were found by running two
forms against each other and none by reading, so the settled series and the
corroborated series are both CALLED here and their results compared, rather than
asserted from source text. The two source-text assertions that remain are about
call ORDER, which no single call can reveal, and each says so.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    Finding, FindingRegistry, _compute_rho, _corroborated_discounts,
    _corroborated_novelty_series, _settled_novelty_series,
)

RUNNER = REPO / "bench" / "reference_runner_v3.py"


def mk(fid: str, model: str, desc: str, sev: float = 0.8, rnd: int = 0) -> Finding:
    return Finding(finding_id=fid, model_id=model, round_idx=rnd, flaw_class=1,
                   severity=sev, abstraction_index=0.5, description=desc,
                   proposed_fix="S_k: fix it")


def reg_with(*specs, round_of=None):
    """Register (fid, model, desc) triples and stamp open_since_round."""
    reg = FindingRegistry()
    ids = []
    for i, (fid, model, desc) in enumerate(specs):
        cid = reg.register(mk(fid, model, desc), model)
        r = 0 if round_of is None else round_of[i]
        reg.entries[cid]["open_since_round"] = r
        ids.append(cid)
    return reg, ids


class TestCorroborationReachesTheOverlapRecord:
    """Defect 1: `occasions` must grow when a second model corroborates."""

    def test_register_writes_exactly_one_occasion(self):
        reg, (a,) = reg_with(("A_F1", "A-SIM", "null deref"))
        occ = reg.entries[a]["occasions"]
        assert len(occ) == 1 and occ[0]["via"] == "register"

    def test_codiscovery_appends_a_second_occasion(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "null deref"),
                               ("B_F1", "B-SIM", "null deref"))
        assert reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91, round_idx=0) is True
        vias = [o["via"] for o in reg.entries[a]["occasions"]]
        assert vias == ["register", "codiscovery"], (
            "corroboration did not reach `occasions`; this is the starvation the "
            "shakedown measured as 53 of 53 entries holding exactly 1 occasion")

    def test_the_occasion_names_the_duplicates_own_canonical(self):
        """So a reader can see WHICH registration the occasion discounts."""
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "null deref"),
                               ("B_F1", "B-SIM", "null deref"))
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91, round_idx=0)
        occ = [o for o in reg.entries[a]["occasions"] if o["via"] == "codiscovery"][0]
        assert occ["from_canonical"] == b
        assert occ["round"] == 0 and occ["alias"] == "B_F1"

    def test_the_round_is_recorded_not_defaulted(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.5, round_idx=4)
        occ = [o for o in reg.entries[a]["occasions"] if o["via"] == "codiscovery"][0]
        assert occ["round"] == 4

    def test_an_unresolvable_alias_falls_back_and_does_not_crash(self):
        reg, (a,) = reg_with(("A_F1", "A-SIM", "d"))
        assert reg.record_codiscovery(a, "GHOST", "never_registered", 0.5) is True
        occ = [o for o in reg.entries[a]["occasions"] if o["via"] == "codiscovery"][0]
        assert occ["from_canonical"] == a, "the field must stay unconditional"

    def test_a_repeat_records_nothing_twice(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        assert reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91) is True
        n = len(reg.entries[a]["occasions"])
        assert reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91) is False
        assert len(reg.entries[a]["occasions"]) == n, (
            "a duplicate corroboration was counted twice; rho would be understated")


class TestTheSeriesCountsDistinctDefects:
    """Both series are CALLED and their outputs compared."""

    def test_the_two_series_agree_until_corroboration_exists(self):
        reg, ids = reg_with(("A_F1", "A-SIM", "null deref"),
                            ("B_F1", "B-SIM", "null deref"),
                            ("C_F1", "C-SIM", "off by one"))
        assert _settled_novelty_series(reg, 0)[0] == \
               _corroborated_novelty_series(reg, 0)[0] == [3]

    def test_corroboration_discounts_the_duplicate_and_the_settled_series_does_not(self):
        reg, (a, b, c) = reg_with(("A_F1", "A-SIM", "null deref"),
                                  ("B_F1", "B-SIM", "null deref"),
                                  ("C_F1", "C-SIM", "off by one"))
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91, round_idx=0)
        settled = _settled_novelty_series(reg, 0)[0]
        corr = _corroborated_novelty_series(reg, 0)[0]
        assert settled == [3], "the settled series must be left alone"
        assert corr == [2], "3 registrations, 2 distinct defects"
        assert _corroborated_discounts(reg) == {b: a}

    def test_rho_falls_because_of_it(self):
        """The whole point: the same raw count, a lower rho."""
        reg, (a, b, c) = reg_with(("A_F1", "A-SIM", "null deref"),
                                  ("B_F1", "B-SIM", "null deref"),
                                  ("C_F1", "C-SIM", "off by one"))
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91, round_idx=0)

        class Cfg:
            rho_rolling_window = 3
            rho_threshold = 0.25
            rho_earliest_round = 12
        raw = [3]
        before, _, _ = _compute_rho(_settled_novelty_series(reg, 0)[0], raw, Cfg())
        after, _, _ = _compute_rho(_corroborated_novelty_series(reg, 0)[0], raw, Cfg())
        assert before == pytest.approx(1.0)
        assert after == pytest.approx(2 / 3)
        assert after < before

    def test_the_later_sighting_is_the_one_discounted(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"),
                               round_of=[0, 2])
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9, round_idx=2)
        assert _corroborated_discounts(reg) == {b: a}
        assert _corroborated_novelty_series(reg, 2)[0] == [1, 0, 0]

    def test_a_tie_keeps_the_target_because_it_registered_first(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9, round_idx=0)
        d = _corroborated_discounts(reg)
        assert d == {b: a}, "the target is the earlier registration by construction"

    def test_an_earlier_duplicate_discounts_the_target_instead(self):
        """If the triage resolved onto a LATER entry, the later one is discounted."""
        reg, (early, late) = reg_with(("E_F1", "E-SIM", "d"), ("L_F1", "L-SIM", "d"),
                                      round_of=[0, 3])
        # corroboration recorded onto the LATE entry, naming the EARLY one
        reg.record_codiscovery(late, "E-SIM", "E_F1", 0.9, round_idx=3)
        assert _corroborated_discounts(reg) == {late: early}


class TestItCannotDeleteAGenuineFinding:
    """The failure mode opposite to the one being fixed, and just as real.

    `cdsfl_a_model_can_delete_a_finding_by_repeating_itself` records that this
    project has already shipped a path where a finding vanished. A novelty counter
    that discounts too eagerly is that same class of defect.
    """

    def test_a_self_referencing_occasion_discounts_nothing(self):
        reg, (a,) = reg_with(("A_F1", "A-SIM", "lone defect"))
        reg.entries[a].setdefault("occasions", []).append(
            {"model": "A-SIM", "round": 0, "alias": "A_F1",
             "from_canonical": a, "via": "codiscovery"})
        assert _corroborated_discounts(reg) == {}
        assert _corroborated_novelty_series(reg, 0)[0] == [1], (
            "a lone finding was discounted against itself and deleted from rho")

    def test_an_occasion_naming_an_absent_canonical_is_ignored(self):
        reg, (a,) = reg_with(("A_F1", "A-SIM", "lone defect"))
        reg.entries[a].setdefault("occasions", []).append(
            {"model": "X", "round": 0, "alias": "X_F1",
             "from_canonical": "C9999", "via": "codiscovery"})
        assert _corroborated_discounts(reg) == {}
        assert _corroborated_novelty_series(reg, 0)[0] == [1]

    def test_a_register_occasion_never_discounts(self):
        """Only `via="codiscovery"` is evidence of a re-sighting."""
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d1"), ("B_F1", "B-SIM", "d2"))
        reg.entries[a]["occasions"].append(
            {"model": "B-SIM", "round": 0, "alias": "B_F1",
             "from_canonical": b, "via": "register"})
        assert _corroborated_discounts(reg) == {}
        assert _corroborated_novelty_series(reg, 0)[0] == [2]

    def test_a_missing_open_since_round_is_skipped_not_guessed(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        del reg.entries[b]["open_since_round"]
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9, round_idx=0)
        assert _corroborated_discounts(reg) == {}

    def test_it_never_returns_a_negative_or_inflated_count(self):
        reg, ids = reg_with(*[(f"M{i}_F1", f"M{i}-SIM", "same defect")
                              for i in range(5)])
        for i in range(1, 5):
            reg.record_codiscovery(ids[0], f"M{i}-SIM", f"M{i}_F1", 0.9, round_idx=0)
        corr = _corroborated_novelty_series(reg, 0)[0]
        assert corr == [1], "5 models, 1 defect"
        assert all(c >= 0 for c in corr)
        assert sum(corr) <= len(reg.entries)


class TestTheSettledSeriesIsUntouched:
    """It has 8 callers and 6 test files; changing it was not the fix."""

    def test_it_still_excludes_terminal_statuses_and_nothing_more(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d1"), ("B_F1", "B-SIM", "d2"))
        reg.entries[b]["status"] = "REFUTED"
        assert _settled_novelty_series(reg, 0)[0] == [1]

    def test_corroboration_alone_does_not_move_it(self):
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        before = _settled_novelty_series(reg, 0)[0]
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9, round_idx=0)
        assert _settled_novelty_series(reg, 0)[0] == before

    def test_the_corroborated_series_is_never_above_the_settled_one(self):
        reg, ids = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"),
                            ("C_F1", "C-SIM", "e"), round_of=[0, 0, 1])
        reg.record_codiscovery(ids[0], "B-SIM", "B_F1", 0.9, round_idx=0)
        s = _settled_novelty_series(reg, 1)[0]
        c = _corroborated_novelty_series(reg, 1)[0]
        assert all(ci <= si for ci, si in zip(c, s)), (c, s)


class TestRhoIsRecomputedAfterTheSettle:
    """Defect 2. Call ORDER is not observable from one call, so these read source
    and say so. Everything about the VALUES is executed above."""

    def test_the_recomputation_exists_and_follows_the_settle(self):
        src = RUNNER.read_text(encoding="utf-8")
        i_settle = src.index("_corr_all, _corr_crit = _corroborated_novelty_series(")
        i_redo = src.index("rho_current, rho_avg, rho_churn = _compute_rho(\n"
                           "                novelty_counts, raw_counts, cfg)")
        assert i_redo > i_settle, (
            "rho is computed before corroboration is known; that is the defect")

    def test_the_recomputation_follows_the_codiscovery_recording(self):
        """Order that matters most: the record must exist before it is counted."""
        src = RUNNER.read_text(encoding="utf-8")
        i_record = src.index("registry.record_codiscovery(")
        i_redo = src.index("rho_current, rho_avg, rho_churn = _compute_rho(\n"
                           "                novelty_counts, raw_counts, cfg)")
        assert i_redo > i_record

    def test_rho_history_is_overwritten_not_appended_twice(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert src.count("rho_history.append(") == 1, (
            "a second append would give the run more rho values than rounds")
        assert "rho_history[-1] = rho_current" in src

    def test_churn_is_re_derived_from_a_saved_base(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert "_churn_base = consecutive_churn_rounds" in src
        assert "consecutive_churn_rounds = (_churn_base + 1) if rho_churn else 0" in src

    def test_the_provisional_value_is_labelled_as_provisional(self):
        """A pre-verifier rho in a log the founder reads must not look final."""
        src = RUNNER.read_text(encoding="utf-8")
        assert "(provisional, pre-verifier)" in src

    def test_the_stale_guarantee_was_corrected_not_left_standing(self):
        """A docstring promising what is no longer true is how a false rule
        acquires authority here -- see feedback_rejected_advice_acquires_authority."""
        src = RUNNER.read_text(encoding="utf-8")
        assert 'does NOT touch\n        `novel_this_round`, and therefore CANNOT move gamma' not in src
        assert "THE OLD \"CANNOT MOVE A VERDICT\" GUARANTEE NO LONGER HOLDS" in src


class TestTheGuardWouldCatchTheDefectComingBack:
    """ANTI-VACUITY. A test that passes against the broken code proves nothing."""

    def test_removing_the_occasion_write_breaks_these_tests(self):
        """Simulated by calling the series on a registry whose corroboration was
        recorded WITHOUT an occasion -- exactly the pre-fix behaviour."""
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        # pre-fix behaviour: aliases and codiscovery only, no occasion
        reg.entries[a].setdefault("source_aliases", []).append("B-SIM:B_F1")
        reg.entries[a].setdefault("codiscovery", []).append(
            {"model": "B-SIM", "finding_id": "B_F1", "similarity": 0.91})
        assert _corroborated_novelty_series(reg, 0)[0] == [2], (
            "without the occasion the count cannot fall -- which is the defect, "
            "and this test documents that the repair is the occasion write")
        # and with it, it does
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91, round_idx=0)
        assert _corroborated_novelty_series(reg, 0)[0] == [1]

    def test_the_two_series_are_genuinely_different_functions(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert src.count("def _settled_novelty_series(") == 1
        assert src.count("def _corroborated_novelty_series(") == 1
        assert src.count("def _corroborated_discounts(") == 1


class TestTheResumePathCannotStarveTheRecord:
    """Found by this file's own anti-vacuity test, 2026-09-29.

    `record_codiscovery` returned early whenever the alias was already recorded.
    A run resumed from a checkpoint written before the occasion write existed
    therefore carried corroboration in `source_aliases` and `codiscovery` while
    `occasions` stayed empty -- reinstating the whole defect through the resume
    path alone, silently, with every test still green.
    """

    def _prefix_state(self):
        """A registry in exactly the state the OLD code would leave it in."""
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        reg.entries[a].setdefault("source_aliases", []).append("B-SIM:B_F1")
        reg.entries[a].setdefault("codiscovery", []).append(
            {"model": "B-SIM", "finding_id": "B_F1", "similarity": 0.91})
        return reg, a, b

    def test_a_prefix_checkpoint_starves_the_record(self):
        """The precondition. If this stops holding, the test below is vacuous."""
        reg, a, b = self._prefix_state()
        assert [o["via"] for o in reg.entries[a]["occasions"]] == ["register"]
        assert _corroborated_novelty_series(reg, 0)[0] == [2]

    def test_a_later_call_backfills_the_missing_occasion(self):
        reg, a, b = self._prefix_state()
        assert reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91, round_idx=0) is False
        assert [o["via"] for o in reg.entries[a]["occasions"]] == \
               ["register", "codiscovery"]
        assert _corroborated_novelty_series(reg, 0)[0] == [1]

    def test_the_backfill_does_not_duplicate_the_alias(self):
        reg, a, b = self._prefix_state()
        before = list(reg.entries[a]["source_aliases"])
        reg.record_codiscovery(a, "B-SIM", "B_F1", 0.91, round_idx=0)
        assert reg.entries[a]["source_aliases"] == before
        assert len(reg.entries[a]["codiscovery"]) == 1

    def test_the_return_value_contract_is_unchanged(self):
        """3 existing tests assert False on a repeat; the backfill must not
        change that, or test_three_gaps_2026-08-23 breaks."""
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        assert reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9) is True
        assert reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9) is False
        assert reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9) is False

    def test_repeated_corroboration_yields_exactly_one_occasion(self):
        """The mirror defect: double-counting would UNDERSTATE rho."""
        reg, (a, b) = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"))
        for r in range(5):
            reg.record_codiscovery(a, "B-SIM", "B_F1", 0.9, round_idx=r)
        cod = [o for o in reg.entries[a]["occasions"] if o["via"] == "codiscovery"]
        assert len(cod) == 1
        assert cod[0]["round"] == 0, "the FIRST sighting's round is the one kept"

    def test_two_different_models_each_get_their_own_occasion(self):
        reg, ids = reg_with(("A_F1", "A-SIM", "d"), ("B_F1", "B-SIM", "d"),
                            ("C_F1", "C-SIM", "d"))
        reg.record_codiscovery(ids[0], "B-SIM", "B_F1", 0.9, round_idx=0)
        reg.record_codiscovery(ids[0], "C-SIM", "C_F1", 0.9, round_idx=1)
        cod = [o for o in reg.entries[ids[0]]["occasions"] if o["via"] == "codiscovery"]
        assert len(cod) == 2
        assert _corroborated_novelty_series(reg, 1)[0] == [1, 0]

    def test_one_definition_of_the_occasion_shape(self):
        """Two copies of the literal is how a producer and consumer drift apart."""
        src = RUNNER.read_text(encoding="utf-8")
        assert src.count('"via": "codiscovery",') == 1, (
            "the occasion literal is written in more than one place")
        assert src.count("def _backfill_occasion(") == 1
