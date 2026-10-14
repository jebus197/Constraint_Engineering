<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a293746665b8c99f82ed959d0b5ca1679a0fa5ee68e98b79bebe21c37e2ddd2e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Proposed §11 — Worked Proofs (Severity Corroboration), v2

> **Proposed amendment v2, 2026-10-14 joint panel — awaiting founder
> ratification.** Replaces the v1 draft of the same date (never adopted into
> the tree; preserved in that round's `seat_proposals.diff`). v1 stated a
> BROADER requirement than any gate enforces ("every quantitative claim") and,
> in one place, the OPPOSITE direction to the enforced one — it said an
> unproven claim is excluded from every convergence-relevant series,
> which is exactly the loophole the runner's design comment rules out: if
> unproven criticals stopped counting, a model could clear the convergence
> gate by omitting its arithmetic. This v2 states the gate the runner has
> enforced since 2026-09-07 (`bench/dm/_rk_proof.py`;
> `bench/reference_runner_v3.py`, "SEVERITY MUST BE A CALCULATION, NOT A
> VOTE"), and nothing more.

**Natural language:**
Every finding's severity MUST carry a CORROBORATION block stating every value
used and its evaluated result:

    R_old, eta, d, p, q = eta*d*p, R_det, S_k, nu_b, nu_f, nu_eff, R_k

Write each parameter and its RESULT on one line, or put the result on a
continuation line beginning with `=`. A formula with no evaluated result reads
as no answer. The RUNNER recomputes R_k from your stated parameters; its
recomputation — never your prose, never panel agreement — decides whether the
severity is arithmetic or an assertion.

Enforcement is ONE-DIRECTIONAL, and that is the whole design: a finding whose
severity does not reproduce is RETAINED and still BLOCKS at its claimed
severity. What it cannot do, until the arithmetic reproduces, is be used to
demote, clear or close anything. If you cannot produce the arithmetic,
withdraw the finding instead — a withdrawal is a legitimate outcome and costs
you nothing.

**Formal:**
```
corroboration(f) = block naming {R_old, eta, d, p, q, R_det, S_k,
                                 nu_b, nu_f, nu_eff, R_k} with evaluated results
proven(f)  ≡ runner_recompute(params(f)) reproduces stated R_k(f)
             // arbiter: the harness's recomputation, never model prose
¬proven(f) ⇒ retained(f) ∧ blocks_at_claimed_severity(f)
             ∧ ¬may_demote(f) ∧ ¬may_clear(f) ∧ ¬may_close(f)
             ∧ proof_request_next_round(f)        // bench/dm/_rk_proof.py
```

**Scope note (deliberate):** this section states ONLY the enforced gate. The
v1 aspiration — an executed derivation on every quantitative claim — is
enforced by no gate in the tree, and a directive stating an unenforced
requirement is the same defect this amendment exists to close, in the other
direction. If the founder wants the broader gate, the gate is built first and
the directive follows it.

Classification Summary row:
| Worked proofs (§11, proposed v2 2026-10-14) | Per-finding CORROBORATION recomputation; one-directional (blocks, never loosens); arbiter is the runner | Yes |
