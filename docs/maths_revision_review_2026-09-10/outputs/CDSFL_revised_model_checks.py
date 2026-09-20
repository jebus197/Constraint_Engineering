"""Falsification checks for the proposed CDSFL core; Python standard library.

Run: python3 CDSFL_revised_model_checks.py
Optionally: python3 CDSFL_revised_model_checks.py --report results.json

Exact outcome trees are built independently of the compact implementation.
Named broken alternatives must be rejected. Passing this suite establishes
only the tested consequences of specified worlds, not empirical validity.
"""

from fractions import Fraction as F
from itertools import product
from math import log2
from pathlib import Path
import argparse
import hashlib
import json

from CDSFL_revised_core import (ImpossibleObservation, action_gain,
    expected_binary_review, sequential_repair_parameters, update)


def text_number(value):
    return {"exact": str(value), "decimal": float(value)}


def outcome_tree(r, q, f, positive_action, negative_action):
    """Enumerate actual pre-state, observation and post-state, without Bayes."""
    masses = {(e, after): F(0) for e, after in product((0, 1), repeat=2)}
    for before, observed, after in product((0, 1), repeat=3):
        prior_mass = r if before else 1 - r
        hit = q if before else f
        observed_mass = hit if observed else 1 - hit
        s, b = positive_action if observed else negative_action
        final_flaw = 1 - s if before else b
        after_mass = final_flaw if after else 1 - final_flaw
        masses[observed, after] += prior_mass * observed_mass * after_mass
    assert sum(masses.values()) == 1
    return masses


def entropy(p):
    return sum(-float(x) * log2(float(x)) for x in (p, 1-p) if x)


def main():
    report = {"scope": "Exact consequences of specified probability models; not empirical calibration",
              "counts": {}, "examples": {}, "rejected_mutations": {}}
    grid = (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))
    conditional, impossible, expected = 0, 0, 0
    # Fixed action on both branches: independent transition enumeration.
    for r, q, f, s, b in product(grid, repeat=5):
        tree = outcome_tree(r, q, f, (s, b), (s, b))
        for observed in (0, 1):
            mass = tree[observed, 0] + tree[observed, 1]
            l1, l0 = (q, f) if observed else (1-q, 1-f)
            if not mass:
                try:
                    update(r, l1, l0, s, b)
                except ImpossibleObservation:
                    impossible += 1
                else:
                    raise AssertionError("Zero-support observation silently accepted")
            else:
                actual = update(r, l1, l0, s, b)
                assert actual.risk_after_action == tree[observed, 1] / mass
                assert 0 <= actual.risk_after_action <= 1
                assert actual.risk_after_action == ((1-s)*actual.posterior_before_action
                                                   + b*(1-actual.posterior_before_action))
                conditional += 1
    report["counts"].update(conditional_outcome_trees=conditional,
                            impossible_observations_rejected=impossible)

    # Branch-dependent actions: repairs only on positives, only on negatives,
    # no action, and a state-flipping action. Expected outcomes must agree.
    actions = ((F(0), F(0)), (F(1), F(0)),
               (F(1, 2), F(1, 4)), (F(1), F(1)))
    for r, q, f, positive, negative in product(grid, grid, grid, actions, actions):
        tree = outcome_tree(r, q, f, positive, negative)
        exact_expected = tree[0, 1] + tree[1, 1]
        assert expected_binary_review(r, q, f, positive, negative) == exact_expected
        expected += 1
    report["counts"]["branch_policy_expectations"] = expected

    sequential = 0
    for z, sigma, nu in product(grid, repeat=3):
        remaining = F(0)
        for before, repaired, injected in product((0, 1), repeat=3):
            mass = (z if before else 1-z)
            mass *= sigma if repaired else 1-sigma
            mass *= nu if injected else 1-nu
            if (before and not repaired) or injected:
                remaining += mass
        s, b = sequential_repair_parameters(sigma, nu)
        assert update(z, 1, 1, s, b).risk_after_action == remaining
        assert remaining == nu + (1-nu)*(1-sigma)*z
        sequential += 1
    report["counts"]["sequential_repair_trees"] = sequential

    # Bayes reductions; expected evidence-only posterior; density scaling.
    reductions = 0
    for r, q, f in product(grid, repeat=3):
        assert expected_binary_review(r, q, f) == r
        for l1, l0 in ((q, f), (1-q, 1-f)):
            if r*l1 + (1-r)*l0:
                a = update(r, l1, l0)
                scaled = update(r, 17*l1, 17*l0)
                assert a.posterior_before_action == scaled.posterior_before_action
        if 1-r*q:
            assert update(r, 1-q, 1).risk_after_action == r*(1-q)/(1-r*q)
        reductions += 1
    report["counts"]["reduction_and_expectation_cases"] = reductions

    # Preserve heterogeneous conditional-coverage / batch-risk link.
    r, miss = F(3, 7), F(1)
    initial = r
    for q in (F(1, 5), F(2, 7), F(4, 9)):
        r = update(r, 1-q, 1).risk_after_action
        miss *= 1-q
    assert r == initial*miss/(1-initial+initial*miss)

    # Earlier repair counterexample, with explicit policy.
    r, q = F(1, 2), F(4, 5)
    clean = update(r, 1-q, 1).risk_after_action
    repaired = update(r, q, 0, 1, 0).risk_after_action
    cycle = expected_binary_review(r, q, 0, (1, 0), (0, 0))
    assert clean == F(1, 6) and repaired == 0 and cycle == F(1, 10)
    report["examples"]["repair_counterexample_resolved"] = {
        "negative_branch": text_number(clean), "positive_repaired": text_number(repaired),
        "expected_cycle": text_number(cycle)}
    assert update(1, q, 0, 1, 0).risk_after_action == 0
    assert expected_binary_review(1, q, 0, (1, 0), (0, 0)) == F(1, 5)

    # Reinjection is conditional on real mutation, not automatically global.
    action = sequential_repair_parameters(1, F(1, 10))
    triggered = expected_binary_review(r, q, 0, action, (0, 0))
    every_cycle = F(1, 10) + F(9, 10)*F(1, 10)
    assert triggered == F(7, 50) and every_cycle == F(19, 100)
    report["examples"]["action_schedule_matters"] = {
        "only_detection_triggers_repair": text_number(triggered),
        "new_flaws_possible_after_every_cycle": text_number(every_cycle)}

    # False positive observations are not conclusive.
    noisy_positive = update(F(1, 10), F(4, 5), F(1, 5)).posterior_before_action
    assert noisy_positive == F(4, 13)
    report["examples"]["false_positive_aware_update"] = text_number(noisy_positive)

    # Same record twice has conditional likelihood pair (1,1) after first use.
    first = update(F(1, 2), F(1, 5), 1).risk_after_action
    duplicate = update(first, 1, 1).risk_after_action
    independent_replication = update(first, F(1, 5), 1).risk_after_action
    assert duplicate == F(1, 6) and independent_replication == F(1, 26)
    report["examples"]["duplicate_vs_replication"] = {
        "duplicate": text_number(duplicate), "fresh_replication": text_number(independent_replication)}

    # Same scalar risk, different hidden flaw composition: different q.
    risk_after_A_negative = update(F(1, 2), 0, 1).risk_after_action
    risk_after_B_negative = update(F(1, 2), 1, 1).risk_after_action
    assert risk_after_A_negative == 0 and risk_after_B_negative == F(1, 2)
    report["examples"]["scalar_history_insufficiency"] = [text_number(risk_after_A_negative),
                                                            text_number(risk_after_B_negative)]

    # Action selection can itself be evidence. Private-state controller idles
    # iff clean: P(idle|flawed)=0, P(idle|clean)=1. Ignoring selection is wrong.
    selection_ignored = update(F(1, 2), 1, 1).risk_after_action
    selection_conditioned = update(F(1, 2), 0, 1).risk_after_action
    assert selection_ignored == F(1, 2) and selection_conditioned == 0
    report["examples"]["private_selection_information"] = {
        "ignored": text_number(selection_ignored), "conditioned": text_number(selection_conditioned)}

    # Correlated parameter uncertainty must not be collapsed into separate means.
    joint_average = (update(F(4, 5), 1, 1, F(4, 5), 0).risk_after_action
                     + update(F(1, 5), 1, 1, F(1, 5), 0).risk_after_action)/2
    mean_plug_in = update(F(1, 2), 1, 1, F(1, 2), 0).risk_after_action
    conditional_removal = F(17, 25)
    assert joint_average == F(4, 25) and mean_plug_in == F(1, 4)
    assert update(F(1, 2), 1, 1, conditional_removal, 0).risk_after_action == joint_average
    report["examples"]["parameter_dependence"] = {
        "joint_average": text_number(joint_average), "separate_means": text_number(mean_plug_in),
        "correct_conditional_removal": text_number(conditional_removal)}

    # Two complementary investigations defeat an unrestricted greedy stop rule.
    worlds = [(x, y, x ^ y) for x, y in product((0, 1), repeat=2)]
    assert sum(w[2] for w in worlds) == 2
    for index in (0, 1):
        for value in (0, 1):
            selected = [w for w in worlds if w[index] == value]
            assert F(sum(w[2] for w in selected), len(selected)) == F(1, 2)
    assert entropy(F(1, 2)) == 1 and all(entropy(F(w[2])) == 0 for w in worlds)
    report["examples"]["complementary_tests"] = {"either_single_test_bits": 0, "both_tests_bits": 1}

    # Updated action break-even relation and s+b>1 domain.
    for z, s, b in product(grid, repeat=3):
        after = update(z, 1, 1, s, b).risk_after_action
        assert z-after == action_gain(z, s, b)
        if s+b:
            assert (after < z) == (z > b/(s+b))
    assert update(F(3, 4), 1, 1, 1, 1).risk_after_action == F(1, 4)

    # Named deliberately wrong alternatives must fail independent expectations.
    mutants = {
        "old_clean_posterior_as_repair_cycle": (F(1, 6), cycle),
        "publication_novelty_zeroes_evidence": (F(1, 2), first),
        "positive_result_uses_negative_update": (first, F(1)),
        "raw_sigma_used_as_net_removal": (F(0), update(1, 1, 1, *action).risk_after_action),
        "duplicate_treated_as_independent": (independent_replication, duplicate),
        "unperformed_actions_get_reinjection": (every_cycle, triggered),
        "private_selection_ignored": (selection_ignored, selection_conditioned),
        "correlated_parameters_replaced_by_means": (mean_plug_in, joint_average),
    }
    for name, (wrong, correct) in mutants.items():
        assert wrong != correct, f"Mutation escaped: {name}"
        report["rejected_mutations"][name] = {"wrong": text_number(wrong), "correct": text_number(correct)}
    report["counts"]["named_mutations_rejected"] = len(mutants)

    # Demonstrate why unrestricted post-hoc s,b cannot be empirically tested.
    for z, desired in product(grid, repeat=2):
        assert update(z, 1, 1, 1-desired, desired).risk_after_action == desired
    report["examples"]["free_parameters_can_fit_any_desired_risk"] = True

    # Invalid parameter domains fail explicitly.
    for arguments in ((F(-1, 10), 1, 1), (F(11, 10), 1, 1),
                      (F(1, 2), -1, 1), (F(1, 2), 1, 1, 2, 0)):
        try:
            update(*arguments)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid input silently accepted")

    report["status"] = "all_checks_passed"
    report["source_sha256"] = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                               for name in ("CDSFL_revised_core.py", "CDSFL_revised_model_checks.py")}
    args = argparse.ArgumentParser()
    args.add_argument("--report")
    selected = args.parse_args()
    if selected.report:
        Path(selected.report).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "counts": report["counts"],
                      "examples": report["examples"]}, indent=2))


if __name__ == "__main__":
    main()
