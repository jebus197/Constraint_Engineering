"""Exact, dependency-free checks for the 2026-09-09 CDSFL mathematical review.

Source snapshot: jebus197/Constraint_Engineering
9e3dfe9d68b428acb98e65c0ad3800ec571a4da4

Run with Python 3. These checks concern equations and their stated semantics;
they do not execute, modify, or certify the CDSFL implementation.
"""

from fractions import Fraction as F
from itertools import product
import json


def negative_posterior(r, q):
    return r * (1 - q) / (1 - q * r)


def cdsfl_cycle(r, q, sigma, nu):
    clean = negative_posterior(r, q)
    base = sigma * clean + (1 - sigma) * r
    return (1 - nu) * base + nu


def show(value):
    return {"exact": str(value), "decimal": float(value)}


results = {}

# Independent enumeration of a single-flaw test-and-repair experiment.
# H: flaw initially exists. D: detected (no false positives).
# S: repair succeeds if a flaw is detected.
r, q, sigma = F(1, 2), F(4, 5), F(1)
branches = []
for h, d, s in product((False, True), repeat=3):
    p_h = r if h else 1 - r
    p_d_given_h = q if h else F(0)
    p_d = p_d_given_h if d else 1 - p_d_given_h
    p_s_given_d = sigma if d else F(0)
    p_s = p_s_given_d if s else 1 - p_s_given_d
    probability = p_h * p_d * p_s
    remaining = h and not (d and s)
    branches.append((h, d, s, probability, remaining))
assert sum(b[3] for b in branches) == 1
prob_negative = sum(b[3] for b in branches if not b[1])
flaw_and_negative = sum(b[3] for b in branches if b[0] and not b[1])
clean_posterior = flaw_and_negative / prob_negative
remaining_expected = sum(b[3] for b in branches if b[4])
assert clean_posterior == F(1, 6)
assert remaining_expected == F(1, 10)
assert cdsfl_cycle(r, q, sigma, F(0)) == F(1, 6)
results["observed_clean_vs_expected_repair"] = {
    "negative_result_probability": show(prob_negative),
    "clean_posterior": show(clean_posterior),
    "expected_remaining_after_repair": show(remaining_expected),
    "cdsfl_cycle": show(cdsfl_cycle(r, q, sigma, F(0))),
}

# The domain excludes R=q=1; R=1,q=4/5 is not that excluded boundary.
assert cdsfl_cycle(F(1), q, F(1), F(0)) == 1
results["known_flaw_perfect_repair"] = {
    "cdsfl_remaining": show(F(1)), "actual_target_remaining": show(F(0))
}

# Stage 6: published prior art removes risk-update credit even when the
# underlying diagnostic or replication could supply fresh evidence.
eta_int, c_ext, novelty_lit = F(1), F(1), F(0)
eta = eta_int * (1 - c_ext * (1 - novelty_lit))
q_stage6 = eta * F(1) * q
assert q_stage6 == 0
results["known_literature_zeroes_effective_detection"] = {
    "q": show(q_stage6),
    "posterior_under_stage6": show(negative_posterior(r, q_stage6)),
    "posterior_if_known_test_has_sensitivity_4_5": show(negative_posterior(r, q)),
}

# Verify batch-recursive identity on a heterogeneous sequence.
prior = F(3, 7)
posterior, miss = prior, F(1)
for sensitivity in (F(1, 5), F(2, 7), F(4, 9)):
    posterior = negative_posterior(posterior, sensitivity)
    miss *= 1 - sensitivity
batch = prior * miss / (1 - prior + prior * miss)
assert posterior == batch
results["valid_batch_recursive_identity"] = show(batch)

# Diminishing posterior decrements are not a global property.
r_current = F(99, 100)
gains = []
for _ in range(3):
    r_next = negative_posterior(r_current, F(1, 2))
    gains.append(r_current - r_next)
    r_current = r_next
assert gains[0] < gains[1] < gains[2]
results["increasing_clean_posterior_gains"] = [show(g) for g in gains]

# A printed reduction and inverse are wrong as stated.
assert cdsfl_cycle(F(1, 2), F(0), F(1), F(1, 10)) == F(11, 20)
prior, coverage = F(1, 2), F(1, 5)
r = prior * (1 - coverage) / (1 - prior + prior * (1 - coverage))
wrong_inverse = (prior - r) / (prior * (r - 1))
right_inverse = (prior - r) / (prior * (1 - r))
assert wrong_inverse == -coverage and right_inverse == coverage
results["local_algebra_errors"] = {
    "eta_zero_with_reinjection": show(F(11, 20)),
    "printed_inverse": show(wrong_inverse),
    "correct_inverse": show(right_inverse),
}

# The break-even threshold is correct for the stipulated recurrence.
r, q, sigma = F(2, 5), F(3, 5), F(4, 5)
nu_star = sigma * r * q / (1 - q * r * (1 - sigma))
assert cdsfl_cycle(r, q, sigma, nu_star) == r
assert cdsfl_cycle(r, q, sigma, nu_star / 2) < r
assert cdsfl_cycle(r, q, sigma, (nu_star + 1) / 2) > r
results["valid_break_even"] = show(nu_star)

# The stated reinjection floor is a valid lower bound, not generally the limit.
q, sigma, nu = F(1, 2), F(1), F(1, 10)
r_star = nu / (q * (sigma + nu * (1 - sigma)))
assert cdsfl_cycle(r_star, q, sigma, nu) == r_star
assert r_star == F(1, 5) and r_star > nu
results["valid_floor_bound_and_actual_fixed_point"] = {
    "lower_bound": show(nu), "fixed_point": show(r_star)
}

# Pairwise independence alone does not identify three-way all-miss risk.
even = [x for x in product((0, 1), repeat=3) if sum(x) % 2 == 0]
odd = [x for x in product((0, 1), repeat=3) if sum(x) % 2 == 1]
for states in (even, odd):
    for i in range(3):
        assert sum(F(x[i], 4) for x in states) == F(1, 2)
        for j in range(i):
            assert sum(F(x[i] * x[j], 4) for x in states) == F(1, 4)
results["pairwise_independence_is_not_joint_independence"] = {
    "even_parity_all_miss": show(F((1, 1, 1) in even, 4)),
    "odd_parity_all_miss": show(F((1, 1, 1) in odd, 4)),
    "independent_product_all_miss": show(F(1, 8)),
}

print(json.dumps(results, indent=2))
print("All exact-arithmetic checks passed.")
