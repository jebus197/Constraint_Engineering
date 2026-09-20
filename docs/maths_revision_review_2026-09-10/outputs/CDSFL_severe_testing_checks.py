"""Exact checks for the severe-test bound added in revision 1.1.

Constructed probability tables; no empirical calibration or deployment.
Run: python3 CDSFL_severe_testing_checks.py --report results.json
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json


def pass_posterior_from_table(prior, flawed_outcomes, clean_outcomes):
    """Enumerate joint pre-state/outcome masses, then select actual passes."""
    assert sum(flawed_outcomes) == sum(clean_outcomes) == 1
    assert all(0 <= p <= 1 for p in flawed_outcomes + clean_outcomes)
    table = {}
    for flawed, outcome in product((0, 1), range(len(flawed_outcomes))):
        initial = prior if flawed else 1-prior
        conditional = flawed_outcomes if flawed else clean_outcomes
        table[flawed, outcome] = initial*conditional[outcome]
    assert sum(table.values()) == 1
    total_pass = table[1, 0] + table[0, 0]
    assert total_pass > 0
    return table[1, 0]/total_pass


def bound(prior, beta_max, gamma_min):
    assert 0 < prior < 1 and 0 <= beta_max <= 1 and 0 < gamma_min <= 1
    return prior*beta_max/(prior*beta_max+(1-prior)*gamma_min)


def number(x):
    return {"exact": str(x), "decimal": float(x)}


def main():
    grid = (F(0), F(1,4), F(1,2), F(3,4), F(1))
    count = 0
    # Include a third unresolved category throughout this bound check.
    for prior, beta_max, gamma_min in product((F(1,10), F(1,2), F(9,10)), grid, grid[1:]):
        for beta, gamma in product(grid, grid):
            if beta <= beta_max and gamma >= gamma_min:
                actual = pass_posterior_from_table(
                    prior, (beta,(1-beta)/2,(1-beta)/2),
                    (gamma,(1-gamma)/2,(1-gamma)/2))
                assert actual <= bound(prior,beta_max,gamma_min)
                if beta == beta_max and gamma == gamma_min:
                    assert actual == bound(prior,beta_max,gamma_min)
                count += 1

    illustration = bound(F(1,2),F(1,20),F(19,20))
    assert illustration == F(1,20)

    # Low miss and low false alarm do not imply strong pass evidence if
    # most clean targets result in abstention instead of passing.
    beta, alpha = F(1,20), F(1,20)
    abstention_case = pass_posterior_from_table(
        F(1,2), (beta,1-beta,F(0)), (F(1,20),alpha,F(9,10)))
    wrong_binary_assumption = bound(F(1,2),beta,1-alpha)
    assert abstention_case == F(1,2)
    assert wrong_binary_assumption == F(1,20)

    # Conditional miss probability is not itself a posterior risk.
    prior_case = pass_posterior_from_table(
        F(1,10), (F(1,5),F(4,5)), (F(9,10),F(1,10)))
    assert prior_case == F(2,83)

    # Average sensitivity across 95% easy and 5% undetectable failures
    # does not supply a uniform bound for the undetectable subtype.
    mixture_case = pass_posterior_from_table(
        F(1,2), (F(1,20),F(19,20)), (F(1),F(0)))
    blind_subtype = pass_posterior_from_table(
        F(1,2), (F(1),F(0)), (F(1),F(0)))
    assert mixture_case == F(1,21) and blind_subtype == F(1,2)

    mutants = {
        "false_alarm_complement_with_abstention": (wrong_binary_assumption,abstention_case),
        "miss_probability_as_posterior": (F(1,5),prior_case),
        "population_average_as_uniform_subtype_bound": (mixture_case,blind_subtype)
    }
    for name,(wrong,correct) in mutants.items():
        assert wrong != correct,name

    report = {
        "version": "1.1",
        "scope": "Constructed exact probability tables, not empirical data",
        "status": "all_checks_passed",
        "bound_cases": count,
        "stipulated_example_upper_bound": number(illustration),
        "rejected_alternatives": {
            name: {"wrong":number(wrong),"correct":number(correct)}
            for name,(wrong,correct) in mutants.items()
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    parser=argparse.ArgumentParser()
    parser.add_argument("--report")
    args=parser.parse_args()
    if args.report:
        Path(args.report).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
