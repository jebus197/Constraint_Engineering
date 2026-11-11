"""The 0.7 cut is not invariant under the admissible transformations of an ordinal scale.

WHY THIS FILE EXISTS. `scripts/the_cut_is_a_domain_property_not_a_constant_2026-11-11.py`
answers the founder's question of 2026-11-11: whether pinning an exact number on severity
is arbitrary once severity is accepted as a quantity each STEM domain measures on its own
scale. Without a guard it would be a producer reached by no test, which is the
`additive-standard` symmetric defect -- an addition nothing reaches is not additive.

THE 4 PROPERTIES PINNED HERE, each by EXECUTING the producer rather than reading it:

  1. A cut named by a fixed VALUE is breakable: z3 returns `sat` for a strictly increasing
     re-scaling that preserves every pairwise order and still changes the count above it.
  2. A cut named by a DISTINGUISHED ELEMENT of the ordering is not: z3 returns `unsat`.
  3. On the archive, an order-preserving affine re-scaling destroys EVERY critical call,
     and the order really is preserved -- Spearman rho exactly 1 and an exhaustive pairwise
     sign check.
  4. The routing facts: nothing classifies a domain from task content, and no domain config
     declares a severity scale or a critical level.

`--help` is asserted separately because a help request must never run the archive walk.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
PRODUCER = REPO / "scripts" / "the_cut_is_a_domain_property_not_a_constant_2026-11-11.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_cut", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def M():
    assert PRODUCER.is_file(), PRODUCER
    return _mod()


class TestTheInvarianceResult:
    """z3, executed. These 2 verdicts are the whole formal claim."""

    def test_a_fixed_value_cut_is_breakable(self, M):
        z = M.prove_invariance()
        assert z["fixed_cut_breakable"] == "sat", (
            "a cut named by a fixed value must be BREAKABLE by an order-preserving "
            f"re-scaling; z3 said {z['fixed_cut_breakable']!r}")
        assert z["fixed_cut_witness"], "sat with no witness is not evidence"
        #: ★ CHECK THE PROPERTY, NOT THE SOLVER'S VERDICT. `sat` alone says a
        #: model exists for WHATEVER was asserted; it cannot tell that the
        #: question was the right one. The mutation harness proved this: flipping
        #: `before != after` to `before == after` left the answer `sat` and this
        #: test green while the central claim was inverted. So the witness is
        #: checked numerically -- the order must be preserved on BOTH sides and
        #: the counts must genuinely differ.
        v = z["fixed_cut_values"]
        assert v, "a sat verdict with no numeric witness cannot be checked"
        assert v["s1"] < v["s2"], f"the witness does not order its inputs: {v}"
        assert v["t1"] < v["t2"], f"the witness does not preserve the order: {v}"
        before = (v["s1"] >= v["c"]) + (v["s2"] >= v["c"])
        after = (v["t1"] >= v["c"]) + (v["t2"] >= v["c"])
        assert before != after, (
            f"the witness preserves the order AND the count, so it exhibits "
            f"nothing: before {before}, after {after}, {v}")

    def test_a_distinguished_element_cut_is_not(self, M):
        z = M.prove_invariance()
        assert z["ranked_cut_breakable"] == "unsat", (
            "a cut named by a distinguished element of the ordering must be INVARIANT; "
            f"z3 said {z['ranked_cut_breakable']!r}")

    def test_the_two_verdicts_differ(self, M):
        """If both came back the same the comparison would carry no information."""
        z = M.prove_invariance()
        assert z["fixed_cut_breakable"] != z["ranked_cut_breakable"]


class TestTheArchiveConsequence:
    def test_the_rescaling_destroys_every_critical_call(self, M):
        d = M.measure_consequence()
        if not d.get("n"):
            pytest.skip("no archived severities on this checkout")
        assert d["before"] > 0, "nothing to destroy means the measurement says nothing"
        assert d["after"] == 0, f"{d['after']} critical call(s) survived the re-scaling"
        assert d["flipped"] == d["before"]

    def test_the_order_really_is_preserved(self, M):
        """The claim is worthless unless the transformation reorders NOTHING."""
        d = M.measure_consequence()
        if not d.get("n"):
            pytest.skip("no archived severities on this checkout")
        assert d["spearman_rho"] == pytest.approx(1.0, abs=1e-12)
        assert d["pairs_order_preserved"] is True

    def test_two_independent_counting_routes_agree(self, M):
        d = M.measure_consequence()
        if not d.get("n"):
            pytest.skip("no archived severities on this checkout")
        assert d["routes_agree"] is True, (
            f"NumPy and pure Python disagree: before {d['before']}/{d['before_route2']}, "
            f"after {d['after']}/{d['after_route2']}")


class TestTheRoutingFacts:
    def test_nothing_classifies_a_domain_from_task_content(self, M):
        args, classifiers = M.measure_routing()
        assert len(args) >= 1, "the domain command-line argument has gone"
        assert classifiers == [], (
            "a domain classifier now exists, so this producer's central claim has "
            f"changed and its text must change with it: {classifiers}")

    def test_the_domain_argument_carries_a_hardcoded_default(self, M):
        args, _ = M.measure_routing()
        defaults = [d for _n, d, _l in args]
        assert any(isinstance(d, str) and d for d in defaults), (
            "the domain argument no longer defaults to a single domain; that would be "
            f"an improvement and this guard must be updated to say so: {defaults}")

    def test_no_domain_config_declares_a_scale_or_a_cut(self, M):
        rows = M.measure_declarations()
        assert rows, "no domain configuration files were found at all"
        declaring = [r for r in rows if r[1]]
        assert declaring == [], (
            "a domain config now declares a severity scale or a critical level. That is "
            f"the recommended repair landing, and this guard must invert: {declaring}")


class TestItRunsAndItsHelpIsFree:
    def test_the_producer_exits_zero(self):
        r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-2500:] + r.stderr[-1500:]
        assert "THE CUT IS A DOMAIN PROPERTY" in r.stdout

    def test_help_answers_without_running_the_measurement(self):
        """A `--help` must never cost anything: 15 of 17 runners once billed for one."""
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-800:]
        assert r.stdout.lower().startswith("usage:"), r.stdout[:200]
        assert "z3, fixed cut" not in r.stdout, (
            "the help text ran the measurement; the flag was ignored")
