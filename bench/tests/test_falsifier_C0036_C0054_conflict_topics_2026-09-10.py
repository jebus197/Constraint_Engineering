"""Task 2.2: the falsifiers exp42 C0036 and C0054 never got.

ONE DEFECT, RAISED TWICE BY DEEPSEEK IN ONE RUN, at severity 0.80 and 0.70. Both
recorded UNCONFIRMED / UNTOOLABLE with an empty falsifier_code.

THE FINDING, verbatim from the archived reply (F011): "`resolve_layer_conflicts()`
relies on `_directive_topic_and_stance()` to detect conflicts. That helper only
recognises four topics (verbosity, examples, rationale, table). All other
directive disagreements -- e.g., 'never infer missing data' vs. 'fill missing
values with defaults', 'use metric A' vs. 'use metric B' -- are not recognised as
conflicts and are both retained."

THE FINDING TEXT HAD TO BE RECOVERED FROM THE RAW REPLY, and that is worth
recording. The registry's stored description is truncated at 200 characters --
decision 15's known damage -- and cuts off mid-sentence at "That helpe". The
run's `descriptions_backfill.json` holds 18 of 67 entries and neither of these.
The full text survives in `r4_deepseek_20260606T213045Z.json`, so the truncation
is REPAIRABLE from the archived replies rather than lost. That is better news
than decision 15 currently assumes.

CONFIRMED, AND THE BLIND SPOT IS 95.6120% OF THE CORPUS. Over the 866 directive
blocks in `bench/directives`, 828 return `(None, None)` -- Wilson
[94.0346%, 96.7866%], Clopper-Pearson [94.0266%, 96.8764%], statsmodels and
mpmath agreeing to 0.0e+00. Only 38 blocks get a topic at all: table 30,
rationale 7, verbosity 1, and `examples` never fires once. DeepSeek's own 4
example directives all return `(None, None)`.

IT IS REACHED. `composer.py:1415` calls `resolve_layer_conflicts` on every
compose, and compose is the live runner's system-prompt mechanism.

NO FIX IS APPLIED. Widening topic detection changes which directives survive
composition, so it changes the prompt every model receives and invalidates replay
of archived runs -- the same class as C0040 and C0037. Confirmed, measured,
tested and parked.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry.composer import (  # noqa: E402
    DIRECTIVES_DIR,
    _directive_topic_and_stance,
    _split_packet_directives,
)

#: The 4 topics the helper knows. Named so a 5th arriving is loud.
KNOWN = {"verbosity", "examples", "rationale", "table"}


def _blocks():
    out = []
    for f in sorted(pathlib.Path(DIRECTIVES_DIR).rglob("*.txt")):
        out += [b for b in _split_packet_directives(
            f.read_text(encoding="utf-8", errors="replace")) if b.strip()]
    return out


class TestTheHelperKnowsExactlyFourTopics:
    def test_it_returns_none_for_anything_else(self):
        for text in ("never infer missing data",
                     "fill missing values with defaults",
                     "use metric A", "use metric B"):
            assert _directive_topic_and_stance(text) == (None, None), (
                f"{text!r} is now classified, so the finding's own example no "
                f"longer demonstrates the gap")

    def test_the_topic_vocabulary_has_not_silently_grown(self):
        found = {t for t, _s in (_directive_topic_and_stance(b) for b in _blocks())
                 if t is not None}
        assert found <= KNOWN, f"a new topic appeared: {found - KNOWN}"


class TestTheBlindSpotIsMostOfTheCorpus:
    def test_the_overwhelming_majority_of_blocks_get_no_topic(self):
        blocks = _blocks()
        assert len(blocks) > 500, f"only {len(blocks)} blocks; recheck the corpus"
        blind = sum(1 for b in blocks
                    if _directive_topic_and_stance(b) == (None, None))
        # TWO TOOLS on the proportion, as this project requires.
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(blind, len(blocks), method="wilson")
        lo_c, hi_c = proportion_confint(blind, len(blocks), method="beta")
        import mpmath as mp
        mp.mp.dps = 30
        z = mp.mpf("1.959963984540054")
        P, N = mp.mpf(blind) / len(blocks), mp.mpf(len(blocks))
        c = (P + z**2 / (2 * N)) / (1 + z**2 / N)
        h = (z / (1 + z**2 / N)) * mp.sqrt(P * (1 - P) / N + z**2 / (4 * N**2))
        assert abs(lo - float(c - h)) < 1e-9, "statsmodels and mpmath disagree"
        assert lo > 0.9, (
            f"the blind spot fell to [{lo:.4%}, {hi:.4%}]; the finding's scale "
            f"has changed and the parked disposition should be revisited")

    def test_the_examples_topic_never_fires_at_all(self):
        """A branch that exists and is reached by nothing, in a 866-block corpus."""
        hits = [b for b in _blocks()
                if _directive_topic_and_stance(b)[0] == "examples"]
        assert not hits, (
            f"the examples branch now fires on {len(hits)} block(s); it fired on "
            f"0 when this was measured, which is the additive standard's unwired "
            f"half sitting inside a live classifier")


class TestItIsReachedOnEveryComposition:
    def test_the_resolver_is_called_by_compose(self):
        src = (ROOT / "bench" / "cdsfl_registry" / "composer.py").read_text(
            encoding="utf-8")
        assert "resolve_layer_conflicts(preliminary)" in src, (
            "the conflict resolver is no longer called by compose, which would "
            "make this finding moot rather than fixed")


class TestTheTruncationIsRepairable:
    """Better news than decision 15 assumes, and worth keeping asserted."""

    def test_the_registry_description_is_truncated(self):
        import json
        p = (ROOT / "bench" / "logs" / "exp42_composer_20260606T202037Z"
             / "runner_state.json")
        if not p.is_file():
            pytest.skip("the exp42 archive is not in this clone")
        reg = json.loads(p.read_text())["registry"]
        ent = reg.get("entries", reg)
        vals = {v.get("canonical_id"): v
                for v in (ent.values() if isinstance(ent, dict) else ent)
                if isinstance(v, dict)}
        desc = vals["C0036"].get("description") or ""
        assert desc.rstrip().endswith("That helpe"), (
            "C0036's stored description is no longer truncated mid-word; the "
            "backfill may have been re-run")

    def test_the_full_text_survives_in_the_raw_reply(self):
        import json
        p = (ROOT / "bench" / "logs" / "exp42_composer_20260606T202037Z"
             / "r4_deepseek_20260606T213045Z.json")
        if not p.is_file():
            pytest.skip("the raw reply is not in this clone")
        r = json.loads(p.read_text()).get("response", "")
        assert "only recognises four topics" in r, (
            "the full finding text is no longer recoverable from the raw reply, "
            "so decision 15's damage really is lost for this entry")
