"""Task 2.2: the falsifiers exp42 C0019 and C0031 never got.

TWO MODELS, ONE DEFECT. DeepSeek raised C0019 and Gemini raised C0031 in the same
run, both at severity 0.80, both against `_block_is_hard`: it classifies a
directive block as HARD if the uppercased text contains any constraint marker, so
a block is protected from pruning on the strength of an ordinary modal verb. Both
were recorded `UNCONFIRMED` with the verdict `UNTOOLABLE` and an empty
`falsifier_code`. Two independent models agreeing on a mechanism is the strongest
signal this project's registry produces, and nobody wrote the 5 lines to check it.

THE MECHANISM IS REAL. THE HARM THEY IMPLY IS NOT DEMONSTRATED, and both halves
are held here, because reporting only the first would overstate the finding and
reporting only the second would bury 2 correct observations.

TWO OF MY OWN CLAIMS WERE WITHDRAWN WHILE WRITING THIS, both by execution.

1. "80.95% of HARD blocks are classified incidentally." The proxy was "does the
   block ALSO contain an explicit HARD keyword", and reading the blocks it
   selected refuted it at once: "Sample size must be pre-specified",
   "Randomisation must be computer-generated", "Informed consent ... must be
   obtained BEFORE any study-specific procedure". Those are genuine hard
   constraints in a clinical directive, and "must" is the constraint marker, not
   an incidental verb. The proportion was real and measured the wrong thing.

2. "The budget miss is silent." It is not. `composer.py:1478` raises a
   `UserWarning` naming the model, the density, the budget and exactly what was
   pruned, and `ComposedDirectiveSet` carries `constraint_density` and
   `coherence_budget` as fields. I had read the 4 return paths of
   `_prune_for_coherence`, seen the last one fall through without a check, and
   concluded silence from the returns while the warning sat 500 lines away. That
   is `execute-do-not-grep` failing in the direction it always fails: reading the
   source instead of running it.
"""
from __future__ import annotations

import itertools
import pathlib
import sys
import warnings

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry.composer import (  # noqa: E402
    DIRECTIVES_DIR,
    MODEL_COHERENCE_BUDGETS,
    _HARD_BLOCK_MARKERS,
    _block_is_hard,
    _split_packet_directives,
    build_interaction_pattern,
    compose,
)
from bench.cdsfl_registry.registry import DOMAIN_MAP  # noqa: E402


def _all_blocks():
    out = []
    for f in sorted(pathlib.Path(DIRECTIVES_DIR).rglob("*.txt")):
        for b in _split_packet_directives(f.read_text(encoding="utf-8",
                                                      errors="replace")):
            if b.strip():
                out.append((f.name, b))
    return out


class TestTheMechanismIsExactlyAsBothModelsDescribed:
    def test_a_modal_verb_alone_makes_a_block_hard(self):
        """C0019 and C0031's shared claim, in 1 assertion."""
        soft = "Prefer worked examples over abstract statements where either fits."
        assert not _block_is_hard(soft)
        assert _block_is_hard(soft + " You must keep them short."), (
            "adding an ordinary 'must' no longer flips a block to HARD, so both "
            "findings' mechanism is gone and this file should be revisited")

    def test_the_check_is_case_insensitive_as_C0031_states(self):
        """Gemini cited `upper = f\" {block.upper()} \"` specifically."""
        assert _block_is_hard("you must not skip this") == \
            _block_is_hard("YOU MUST NOT SKIP THIS")

    def test_it_is_substring_free_which_is_the_part_that_is_RIGHT(self):
        """The markers are space-delimited, so 'mustard' does not fire.

        Recorded because it is the half both findings got wrong by omission: the
        implementation is already defended against the substring trap that has
        bitten this project 3 times in one day elsewhere.
        """
        assert not _block_is_hard("Add mustard to the list of examples.")
        assert not _block_is_hard("The album was remastered.")


class TestTheMechanismIsLoudNotSilent:
    """MY OWN CLAIM, REFUTED. Recorded so it is not made again."""

    def test_going_over_budget_raises_a_warning_naming_the_numbers(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            for domain in list(DOMAIN_MAP)[:6]:
                for model in MODEL_COHERENCE_BUDGETS:
                    compose(task_domain=domain, model=model,
                            situation=build_interaction_pattern("meta_structured"))
        msgs = [str(w.message) for w in caught if "coherence budget" in str(w.message)]
        assert msgs, (
            "no warning was raised for any over-budget composition, so the "
            "failure IS silent after all and the finding is larger than recorded")
        assert any("density=" in m and "budget=" in m for m in msgs), (
            f"the warning does not carry the numbers: {msgs[:1]}")

    def test_the_result_itself_carries_both_figures(self):
        """A reader can compare them without catching a warning at all."""
        c = compose(task_domain="software", model="deepseek_v3",
                    situation=build_interaction_pattern("meta_structured"))
        assert c.coherence_budget > 0
        assert c.constraint_density > 0


class TestTheRateIsHighAndThatIsTheRealFinding:
    def test_most_real_compositions_exceed_the_budget(self):
        """65.56% of 90, Wilson [55.28%, 74.55%]. Not a defect; an operating point.

        This is what survives of C0019 and C0031 once the harm is checked: the
        classifier is generous, the budget is missed on most real compositions,
        and the system says so every time. Whether that rate is acceptable is a
        design question for the founder, not a defect to fix silently.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rows = []
            for domain, model in itertools.product(list(DOMAIN_MAP),
                                                   MODEL_COHERENCE_BUDGETS):
                c = compose(task_domain=domain, model=model,
                            situation=build_interaction_pattern("meta_structured"))
                rows.append(c.constraint_density > c.coherence_budget)
        over, n = sum(rows), len(rows)
        assert n >= 40, f"only {n} compositions were reachable; the rate is thin"
        # TWO TOOLS, as this project requires for any proportion.
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(over, n, method="wilson")
        lo_c, hi_c = proportion_confint(over, n, method="beta")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, over, n - over + 1) if over else 0.0
        assert abs(slo - lo_c) < 1e-9, "statsmodels and scipy disagree"
        assert 0.4 < over / n < 0.9, (
            f"the over-budget rate moved to {over / n:.4f} "
            f"[{lo:.4f}, {hi:.4f}]; the finding's premise has changed")


class TestTheProxyThatFooledMe:
    """Kept as a test so the withdrawn claim cannot quietly return."""

    def test_a_must_in_a_clinical_directive_is_not_incidental(self):
        blocks = [b for _n, b in _all_blocks() if _block_is_hard(b)]
        assert blocks, "no HARD blocks found at all"
        genuine = [b for b in blocks
                   if "must" in b.lower()
                   and any(w in b.lower() for w in
                           ("consent", "randomis", "pre-specified", "sample size",
                            "safety", "regulatory", "endpoint"))]
        assert genuine, (
            "the directives no longer contain modal-marked genuine constraints, "
            "so the proxy that was withdrawn might now be sound -- recheck "
            "before reinstating it")
