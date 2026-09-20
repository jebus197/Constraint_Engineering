"""Exact reference arithmetic for the proposed CDSFL observation/action core.

Proposal, 2026-09-09. No empirical calibration or production integration.
Each call requires a precisely scoped event and correctly conditioned inputs.
Use Fraction, integer, or rational/decimal strings for exact arithmetic.
The function cannot establish that its supplied probabilities describe reality.
"""

from dataclasses import dataclass
from fractions import Fraction


class ImpossibleObservation(ValueError):
    """The observation has zero total likelihood in the supplied representation."""


def probability(value):
    result = Fraction(value)
    if not 0 <= result <= 1:
        raise ValueError("A probability must lie in [0, 1].")
    return result


def likelihood(value):
    result = Fraction(value)
    if result < 0:
        raise ValueError("A likelihood must be nonnegative.")
    return result


@dataclass(frozen=True)
class Update:
    evidence_weight: Fraction
    posterior_before_action: Fraction
    risk_after_action: Fraction


def update(risk, likelihood_flawed, likelihood_clean, removal=0, introduction=0):
    """Condition on actual evidence, then apply a selected two-state action.

    removal = P(post clean | pre flawed, evidence, context, selected action).
    introduction = P(post flawed | pre clean, evidence, context, action).
    The action must use only the recorded information or its selection must
    itself be included in the observation model. removal means NET removal.
    Likelihoods may be probability densities, so no upper bound is imposed.
    Their base measure must agree. evidence_weight is then a density, not mass.
    """
    r = probability(risk)
    l1, l0 = likelihood(likelihood_flawed), likelihood(likelihood_clean)
    s, b = probability(removal), probability(introduction)
    denominator = l1 * r + l0 * (1 - r)
    if denominator == 0:
        raise ImpossibleObservation("Observed evidence has zero total likelihood under the supplied representation.")
    posterior = l1 * r / denominator
    result = ((1 - s) * l1 * r + b * l0 * (1 - r)) / denominator
    return Update(denominator, posterior, result)


def sequential_repair_parameters(repair_efficacy, reinjection):
    """Map sequential raw repair and equal clean-path reinjection into s,b."""
    sigma, nu = probability(repair_efficacy), probability(reinjection)
    return sigma * (1 - nu), nu


def expected_binary_review(risk, sensitivity, false_positive,
                           positive_action=(0, 0), negative_action=(0, 0)):
    """Average both actual-result branches under their declared action policy.

    Action tuples contain NET removal and introduction, respectively.
    Unknown, timeout, and abstention observations require their own channel;
    this binary helper must not silently classify them as negative results.
    """
    r = probability(risk)
    q, f = probability(sensitivity), probability(false_positive)
    result = Fraction(0)
    for l1, l0, action in ((q, f, positive_action),
                          (1 - q, 1 - f, negative_action)):
        if r * l1 + (1 - r) * l0:
            branch = update(r, l1, l0, *action)
            result += branch.evidence_weight * branch.risk_after_action
    return result


def action_gain(posterior, removal, introduction):
    """Expected reduction for an action AFTER evidence; not experiment value."""
    z, s, b = probability(posterior), probability(removal), probability(introduction)
    return s * z - b * (1 - z)
