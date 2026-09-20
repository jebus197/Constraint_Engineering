"""Exact counterexamples delimiting the proposed CDSFL observation/action identity.

These tests challenge interpretations, not Bayes' rule or total probability.
Run with Python 3; standard library only.
"""
from fractions import Fraction as F
from itertools import product


def update(r, l1, l0, s=F(0), b=F(0)):
    d = r*l1 + (1-r)*l0
    if d == 0:
        raise ValueError("Observation has zero probability under the supplied model")
    return ((1-s)*r*l1 + b*(1-r)*l0)/d


# A scalar risk is not sufficient state for future evidence likelihoods.
# Same initial P(any flaw)=1/2. A perfect A-only test returns negative.
type_a_world = update(F(1,2), F(0), F(1))
type_b_world = update(F(1,2), F(1), F(1))
assert (type_a_world, type_b_world) == (F(0), F(1,2))

# Action selection is informative if its private signal is omitted from evidence.
# A controller knows H and chooses idle iff clean; observed idle implies H=0.
misconditioned_idle = update(F(1,2), F(1), F(1), F(0), F(0))
correct_idle = update(F(1,2), F(0), F(1), F(0), F(0))
assert (misconditioned_idle, correct_idle) == (F(1,2), F(0))

# Separate averaging of uncertain posterior and transition parameters is invalid.
parameter_worlds = [(F(4,5), F(4,5), F(0)), (F(1,5), F(1,5), F(0))]
integrated = sum(((1-s)*z + b*(1-z))/2 for z,s,b in parameter_worlds)
zbar, sbar, bbar = [sum(w[i] for w in parameter_worlds)/2 for i in range(3)]
plug_in = (1-sbar)*zbar + bbar*(1-zbar)
assert (integrated, plug_in) == (F(4,25), F(1,4))

# A general transition may reverse ordering: a deterministic flip gives 1-z.
assert update(F(1,4), F(1), F(1), F(1), F(1)) == F(3,4)
assert update(F(3,4), F(1), F(1), F(1), F(1)) == F(1,4)

# Free transition parameters can reproduce any desired next risk, regardless of z.
for z,y in product([F(0),F(1,4),F(1,2),F(1)], repeat=2):
    assert update(z,F(1),F(1),1-y,y) == y

# One-step evidence value can be zero although two-step value is decisive.
states = [(x,y,x^y) for x,y in product([0,1], repeat=2)]
for bit in [0,1]:
    assert F(sum(h for x,y,h in states if x==bit),2) == F(1,2)
    assert F(sum(h for x,y,h in states if y==bit),2) == F(1,2)
for x,y,h in states:
    assert h == x^y

# Observation then branch-dependent action recovers the original repair example.
r,q = F(1,2),F(4,5)
p_positive = r*q
p_negative = 1-p_positive
positive_risk = update(r,q,F(0),F(1),F(0))
negative_risk = update(r,1-q,F(1),F(0),F(0))
assert positive_risk == 0
assert negative_risk == F(1,6)
assert p_positive*positive_risk + p_negative*negative_risk == F(1,10)

print("PASS: exact checks for state insufficiency, action selection, uncertainty,")
print("      non-monotone actions, unconstrained fitting, evidence synergy, and repair.")
