"""Exact checks of proposed observation-action core, using explicit outcome trees."""
from fractions import Fraction as F
from itertools import product

grid = [F(0), F(1, 4), F(1, 2), F(3, 4), F(1)]
checked = 0
for r, q, f, s, b in product(grid, repeat=5):
    # Build pre-state -> test result -> post-state outcome tree.
    masses = {(e, after): F(0) for e, after in product([0, 1], repeat=2)}
    for before, e, after in product([0, 1], repeat=3):
        prior = r if before else 1-r
        positive = q if before else f
        observation = positive if e else 1-positive
        fail_after = 1-s if before else b
        transition = fail_after if after else 1-fail_after
        masses[e, after] += prior*observation*transition
    assert sum(masses.values()) == 1
    for e in [0, 1]:
        evidence_mass = masses[e, 0]+masses[e, 1]
        if evidence_mass == 0:
            continue
        l1, l0 = (q, f) if e else (1-q, 1-f)
        collapsed = ((1-s)*l1*r+b*l0*(1-r))/(l1*r+l0*(1-r))
        assert collapsed == masses[e, 1]/evidence_mass
        assert 0 <= collapsed <= 1
        checked += 1

sequential = 0
for z, sigma, nu in product(grid, repeat=3):
    fail_mass = F(0)
    for before, repaired, injected in product([0, 1], repeat=3):
        prior = z if before else 1-z
        # The repair-success indicator is hypothetical on initially clean paths.
        repair_mass = sigma if repaired else 1-sigma
        inject_mass = nu if injected else 1-nu
        after = (before and not repaired) or injected
        if after:
            fail_mass += prior*repair_mass*inject_mass
    formula = nu+(1-nu)*(1-sigma)*z
    net_s, b = sigma*(1-nu), nu
    assert fail_mass == formula == (1-net_s)*z+b*(1-z)
    sequential += 1

# The earlier negative-result/repair confusion is explicitly resolved.
r, q = F(1, 2), F(4, 5)
no_detection_mass = 1-r*q
negative_posterior = r*(1-q)/no_detection_mass
assert negative_posterior == F(1, 6)
assert no_detection_mass*negative_posterior == r*(1-q) == F(1, 10)
assert F(1, 5)+(1-F(1, 5))*(1-F(1))*F(1) == F(1, 5)

# A destructive action on a clean target and curative one on failed targets
# is still a valid two-state transition; no s+b<=1 restriction is justified.
assert (1-F(1))*F(3, 4)+F(1)*(1-F(3, 4)) == F(1, 4)

# Observation alone has zero expected posterior change for arbitrary q,f.
martingale = 0
for r, q, f in product(grid, repeat=3):
    expectation = F(0)
    for l1, l0 in [(q, f), (1-q, 1-f)]:
        mass = r*l1+(1-r)*l0
        if mass:
            expectation += mass*r*l1/mass
    assert expectation == r
    martingale += 1

print(f"PASS: {checked} conditional two-state checks; {sequential} sequential "
      f"repair/reinjection trees; {martingale} evidence-only expectations; "
      "named counterexamples and boundaries.")
