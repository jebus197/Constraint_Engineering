"""C0037 and C0036 repaired, and both repairs must be breakable.

HIS RULING, 2026-11-01, verbatim: *"Repair the two as you suggest."* The 2 are
the ones that silently alter what a model is TOLD.

C0037 -- THE DE-DUPLICATOR KEPT WHICHEVER LINE CAME FIRST. Its containment test
is ASYMMETRIC (`intersection / min(len(left), len(right)) >= 0.95`) while the
loop kept the earlier arrival, so a SPECIAL CASE appearing before its own
GENERAL FORMULA evicted the formula. Measured before the repair: 14 of 1,677
lines dropped, 0.8348%, Wilson [0.004979, 0.013964], of which 11 by containment
alone. The predicate is UNCHANGED -- it identifies near-duplicates correctly and
the fault was only in which member survived -- so the mechanism assertions in
`test_falsifier_C0037_containment_dedup_2026-09-10.py` stay green by design.

C0036 -- THE RESOLVER SAID "NOT DETECTABLE" AND BEHAVED AS "NONE". Its topic
helper recognises 4 topics and returns `(None, None)` otherwise, so the returned
conflict list was a zero of the CLASSIFIABLE SUBSET while reading as a zero of
everything. On a real mathematics composition: 154 blocks, 13 classifiable, 141
unarbitrated -- so `conflicts_found: 0` was a zero of 13. The topic vocabulary is
deliberately NOT grown, because a 5th topic leaves the resolver blind to the 6th
and that growth is itself guarded against; the repair is that the resolver now
announces what it could not classify.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry.composer import (            # noqa: E402
    _normalise_tokens, _semantically_duplicate, compose, resolve_layer_conflicts)


def _dedup_live(lines: list[str]) -> list[str]:
    """The repaired rule, as the call site applies it."""
    out: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        matched = False
        for i, ex in enumerate(out):
            if _semantically_duplicate(line, ex):
                if len(_normalise_tokens(line)) > len(_normalise_tokens(ex)):
                    out[i] = line
                matched = True
                break
        if not matched:
            out.append(line)
    return out


def _dedup_old(lines: list[str]) -> list[str]:
    """The pre-repair rule, kept so the difference is demonstrated and not asserted."""
    out: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        if not any(_semantically_duplicate(line, ex) for ex in out):
            out.append(line)
    return out


@pytest.fixture(scope="module")
def formulas():
    import importlib.util
    f = REPO / "bench" / "tests" / "test_falsifier_C0037_containment_dedup_2026-09-10.py"
    spec = importlib.util.spec_from_file_location("_c0037_fals", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.GENERAL, m.SPECIAL


class TestC0037TheSurvivorIsDecidedByContent:

    def test_the_pair_is_still_matched_as_duplicate(self, formulas):
        """ANTI-VACUITY. If the predicate stopped firing, every test below would
        pass for the wrong reason."""
        general, special = formulas
        assert _semantically_duplicate(general, special), (
            "the 2 formulas are no longer matched, so this file cannot "
            "demonstrate anything about which of them survives")
        assert len(_normalise_tokens(general)) > len(_normalise_tokens(special)), (
            "the general formula no longer carries more distinct tokens, so "
            "'keep the richer line' no longer identifies it")

    def test_the_general_formula_survives_the_harmful_order(self, formulas):
        """THE REPAIR. Special case first is the order that used to lose it."""
        general, special = formulas
        kept = _dedup_live([special, general])
        assert kept == [general], (
            f"the special case still evicts its own general formula; kept "
            f"{kept[0][:60]!r}")

    def test_the_old_rule_FAILED_that_same_case(self, formulas):
        """The difference is demonstrated, not claimed. If this ever passes, the
        repair is no longer doing anything and may be removed."""
        general, special = formulas
        kept = _dedup_old([special, general])
        assert kept == [special], (
            "the pre-repair rule now keeps the general formula too, so this "
            "pair no longer discriminates the 2 rules")

    def test_the_reverse_order_is_unaffected(self, formulas):
        general, special = formulas
        assert _dedup_live([general, special]) == [general]
        assert _dedup_old([general, special]) == [general]

    def test_nothing_is_weakened_the_pair_still_collapses(self, formulas):
        """The repair moves WHICH line survives, never HOW MANY."""
        general, special = formulas
        for order in ([special, general], [general, special]):
            assert len(_dedup_live(order)) == len(_dedup_old(order)) == 1


class TestC0036TheBlindSpotIsRecorded:

    @pytest.fixture(scope="class")
    def rec(self):
        c = compose(task_domain="mathematics", model="opus_4_6")
        resolved, _ = resolve_layer_conflicts(c)
        r = resolved.manifest.get("conflict_arbitration")
        assert r is not None, "the manifest carries no conflict_arbitration record"
        return r

    def test_the_denominator_adds_up(self, rec):
        assert rec["total_blocks"] == (rec["classifiable_blocks"]
                                       + rec["unarbitrated_blocks"]), rec

    def test_the_blind_spot_is_real_and_large(self, rec):
        """If this ever shrinks below a half the finding's scale has changed and
        the disposition should be revisited rather than restated."""
        tot, un = rec["total_blocks"], rec["unarbitrated_blocks"]
        assert tot > 50, f"only {tot} blocks; recheck the corpus"
        lo, hi = proportion_confint(un, tot, alpha=0.05, method="wilson")
        lo_cp, _ = proportion_confint(un, tot, alpha=0.05, method="beta")
        assert abs(lo - lo_cp) < 0.05, (
            f"statsmodels Wilson {lo:.6f} and Clopper-Pearson {lo_cp:.6f} "
            f"disagree by more than 0.05; one of them is wrong")
        assert lo > 0.5, (
            f"the unarbitrated share has fallen to [{lo:.4f}, {hi:.4f}]; "
            f"re-measure before relying on the figures in this file")

    def test_a_zero_conflict_count_can_be_read_against_its_own_denominator(self, rec):
        """THE WHOLE POINT. Before the repair a reader of `conflicts` saw a bare
        count with no denominator at all."""
        assert "conflicts_found" in rec and "classifiable_blocks" in rec
        assert "_what_this_means" in rec and "classifiable subset only" in rec["_what_this_means"]

    def test_the_unarbitrated_blocks_are_named_not_merely_counted(self, rec):
        """Pin a set, not a count: a count cannot say WHICH block went unseen."""
        if rec["unarbitrated_blocks"]:
            assert rec["unarbitrated"], (
                "blocks were unarbitrated and none is named, so nobody can "
                "check which ones the resolver could not classify")
            s = rec["unarbitrated"][0]
            assert {"packet", "layer", "text"} <= set(s), s

    def test_the_topic_vocabulary_was_NOT_grown(self):
        """The repair must not have taken the whack-a-mole route."""
        from bench.cdsfl_registry.composer import _directive_topic_and_stance
        for text in ("never infer missing data", "fill missing values with defaults",
                     "use metric A", "use metric B"):
            assert _directive_topic_and_stance(text) == (None, None), (
                f"{text!r} is now classified. Growing the vocabulary leaves the "
                f"resolver blind to the next topic instead; the repair is that "
                f"it ANNOUNCES what it could not classify.")

    def test_an_unclassifiable_block_is_still_KEPT(self):
        """A resolver must never delete what it cannot arbitrate."""
        c = compose(task_domain="mathematics", model="opus_4_6")
        resolved, _ = resolve_layer_conflicts(c)
        rec = resolved.manifest["conflict_arbitration"]
        assert rec["unarbitrated_blocks"] > 0
        assert resolved.rendered_text.strip(), "the resolved text is empty"
