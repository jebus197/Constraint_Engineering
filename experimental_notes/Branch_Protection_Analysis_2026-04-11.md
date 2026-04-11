# Branch Protection Analysis — 11 April 2026

## Why the Project Has Gone Smoothly

366 commits in 30 days. 739 tests. Multiple converged experiments. No major blocker.

**Structural advantages:**
- Single developer + single primary AI collaborator. No coordination overhead.
- Strong methodology from day one (CDSFL, P-pass, FFF). Bugs found early.
- High test coverage for project age. Focused scope.
- No production deployment, no uptime requirements.

**What the project hasn't faced:**
- Multi-developer merge conflicts, upstream dependency breaks
- Scaling problems, security requirements from real users
- Team coordination and code review politics

## The Phase Transition

Experiments 12–37: system reviews external code. System and subject are separate.

Experiment 38: ouroboros. System reviews and modifies itself. System and subject are the same.

When the thing being changed is also the thing doing the changing, the blast radius of any individual change becomes much harder to predict.

## The Near-Miss

`run_exp37_evidence.py` — 1 commit in history, 0 uncommitted changes. Survived intact.

BUT: the 398-line immune classification change was applied to `immune_agents.py`, a shared dependency. If committed, `run_exp37_evidence.py`'s behaviour would have changed silently through its dependency chain. The session ran out of context before committing. That's luck, not protection.

## Proposal

1. Create branch `exp38-experimental` from current HEAD
2. All Exp 38 work goes there (3-layer fix, runner bugs, promotion gate)
3. Main stays at Exp 37 proven state
4. Success → merge to main. Failure → main is clean.
