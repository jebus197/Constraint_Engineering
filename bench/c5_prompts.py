"""C5 Experiment: Three-Layer Schema Validation — Prompt Templates.

8-round structure for full continued conversation with CDSFL constraints
and Meta semi-formal structured certificates. No cell decomposition.

Phase 1 (R1-R2): Independent discovery — no prior findings.
Phase 2 (R3-R4): Prior findings injection from Master Finding Registry.
Phase 3 (R5-R8): Synthesis, falsification, novel sweep, summary.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# System instruction (persists across all rounds via chat session)
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """\
You are a senior software verification engineer conducting a formal code \
review under the CDSFL methodology (Constraint-Driven Synthesis and \
Falsification). You operate under these standing constraints:

1. FIND-FOLLOW-FIX (FFF): For every issue you identify —
   FIND: State the bug, its location, and your evidence.
   FOLLOW: Before proposing any fix, trace consequences through the \
entire system. What depends on this? What interfaces does it cross? \
What state does it propagate? What breaks downstream?
   FIX: Apply the simplest sufficient correction that addresses both \
the root cause AND the downstream consequences identified in Follow. \
Then verify the fix does not introduce new problems.
   Classify every fix as: PATCH (modification to existing code), \
NOVEL CONSTRUCT (new function/class/validation layer that does not \
currently exist), or ARCHITECTURAL (design-level change affecting \
multiple components).

2. STRUCTURED CERTIFICATES: For every claim, you must:
   - State your premises explicitly
   - Trace execution through concrete examples (with specific inputs \
and expected outputs)
   - Derive a formal conclusion

3. FALSIFICATION: Actively try to disprove your own conclusions before \
presenting them. If you find a reason a claim might be wrong, state it. \
Retract claims you can disprove. Only present claims that survive your \
own attempted falsification.

4. MATHEMATICAL RIGOUR: Where applicable, provide formal proofs \
(symbolic, set-theoretic, or by contradiction). A claim that can be \
proved mathematically should be.

5. CROSS-COMPONENT AWARENESS: This is a multi-component pipeline. \
Bugs in one component can cascade through others. Always consider \
how findings interact across the full system.

Do not summarise prematurely. Show your working. Depth over breadth."""


# ---------------------------------------------------------------------------
# Round prompt templates
# ---------------------------------------------------------------------------

def round_1_prompt(code_artifact: str) -> str:
    """R1 — Structured Certificate Review. Full code, no priming."""
    return f"""\
Below is the complete source code for an immune-system-inspired quality \
verification pipeline. It contains multiple components: Dendritic Cell \
(triage/classification), NK Cell (duplicate/false-positive detection), \
B Cell (mathematical verification), Helper T Cell (voting/synthesis), \
and Regulatory T Cell (system health monitoring).

Review this code systematically. For every bug, vulnerability, or \
correctness issue you find:

1. State the finding with file location (function name and approximate \
line).
2. Provide a structured certificate: premises, execution trace with \
concrete inputs, formal conclusion.
3. Apply Find-Follow-Fix: trace consequences through the full pipeline, \
then propose a concrete fix. Classify the fix as PATCH, NOVEL CONSTRUCT, \
or ARCHITECTURAL.
4. Attempt to falsify your own finding before presenting it.

Focus on: correctness, security, mathematical validity, injection \
vectors, boundary conditions, cross-component interactions, and silent \
failure modes.

```python
{code_artifact}
```"""


def round_2_prompt(n_findings: int) -> str:
    """R2 — FFF Press Harder. Deepen R1 findings + find new ones."""
    return f"""\
Your initial review found {n_findings} issues. Now apply Find-Follow-Fix \
more aggressively:

For each existing finding:
- FOLLOW deeper: trace consequences through the ENTIRE pipeline. What \
downstream components are affected? What happens when this bug \
interacts with other bugs you found?
- Are there boundary conditions you missed? What about empty inputs, \
None values, zero-length strings, negative numbers?

Then look for what you missed:
- Injection vectors (substring matching, regex manipulation, input that \
mimics output markers)
- Silent failure modes (exceptions swallowed, error paths that return \
success, functions that never execute)
- Mathematical invalidity (proofs that test one case instead of all \
cases, quantifier errors, tautological logic)
- Cross-component state bugs (what one component assumes about \
another's output)

For every finding — new or deepened — propose a fix. Classify as PATCH, \
NOVEL CONSTRUCT, or ARCHITECTURAL. If the fix itself introduces new \
considerations, trace those too."""


def round_3_prompt(findings_batch_1: str) -> str:
    """R3 — Prior Findings Batch 1 (MF-01 to MF-20)."""
    return f"""\
Independent reviewers using different methodologies found the following \
20 issues in the same code you just reviewed. For each finding:

1. CONFIRM or CHALLENGE with evidence. If you confirm, state why your \
own analysis supports it. If you challenge, provide a concrete \
counterexample or proof that the claim is wrong.

2. EXTEND: What NEW issues do these findings reveal when you trace \
their interactions through the full pipeline? Use FFF on any new \
discoveries.

3. For every confirmed or new finding, propose a concrete fix — code \
patch, novel construct, or architectural recommendation. Some of these \
may require entirely new components or validation layers that do not \
currently exist in the codebase. Be specific about what the new \
construct should do and how it integrates.

Prior findings (batch 1 of 2):

{findings_batch_1}"""


def round_4_prompt(findings_batch_2: str) -> str:
    """R4 — Prior Findings Batch 2 (MF-21 to MF-40)."""
    return f"""\
Here is the second batch of findings from independent reviewers. Same \
requirements as before:

1. CONFIRM or CHALLENGE with evidence.
2. EXTEND: What new issues do these findings reveal through pipeline \
interaction tracing?
3. Propose concrete fixes (PATCH / NOVEL CONSTRUCT / ARCHITECTURAL) \
for every confirmed or new finding. Novel constructs are expected — \
some fixes require entirely new validation layers or architectural \
patterns.

Prior findings (batch 2 of 2):

{findings_batch_2}"""


def round_5_prompt() -> str:
    """R5 — Cross-Component Probe."""
    return """\
You now have full context of this pipeline and all known issues — both \
your own findings and those from independent reviewers. Focus \
specifically on cross-component interactions:

1. What happens when multiple bugs interact? For example, if the \
Dendritic Cell misroutes a claim AND the B Cell has a substring \
injection vulnerability, what is the combined effect?

2. What cascade failures exist? Trace chains where one component's \
bug corrupts another component's input, which then corrupts a third \
component's output.

3. What emergent behaviours arise from the combination of all known \
issues? Are there failure modes that only appear when the system \
operates as a whole?

4. For cascade failures and interaction bugs, propose fixes. These \
will often require NOVEL CONSTRUCTS: new inter-component validation, \
new state propagation mechanisms, or new architectural patterns that \
do not exist in the current codebase. Be specific about what each \
construct does, where it sits in the pipeline, and how it prevents \
the cascade.

Apply FFF throughout. Show your working with concrete execution traces."""


def round_6_prompt() -> str:
    """R6 — Self-Falsification."""
    return """\
This is the quality gate. Review ALL findings from this entire \
conversation — yours from rounds 1-2, the prior reviewers' findings \
from rounds 3-4, and the cross-component findings from round 5.

For each finding, actively attempt to disprove it:
1. State your premises for why it might be wrong.
2. Trace execution with a concrete counterexample that would \
invalidate the claim.
3. Derive whether the finding holds or fails.

If you can disprove a finding, RETRACT it with a clear explanation \
of why it is wrong. Do not retract on vague grounds — only retract \
if you have concrete evidence the claim is incorrect.

If a finding survives your attempted disproof, state explicitly \
that you attempted falsification and it survived, with the strongest \
counterargument you considered.

This is adversarial self-review. Your job is to find what is wrong \
with the findings, not to confirm them."""


def round_7_prompt() -> str:
    """R7 — Novel Discovery Sweep."""
    return """\
After falsification, what remains unexplored? Consider categories of \
bugs that neither you nor the prior reviewers may have examined:

- Timing and concurrency (race conditions, TOCTOU, thread safety)
- Serialisation and deserialisation (pickle, JSON round-trip fidelity)
- Error propagation (do errors in one component correctly signal to \
others?)
- Resource management (file handles, memory, subprocess lifecycle)
- Configuration sensitivity (what happens with non-default settings?)
- Numerical stability (floating-point edge cases, overflow, underflow)

For any new finding, apply the full structured certificate and FFF \
process. Propose fixes classified as PATCH / NOVEL CONSTRUCT / \
ARCHITECTURAL.

This is the final discovery sweep. Find what everyone missed."""


def round_8_prompt() -> str:
    """R8 — Final Summary Certificate."""
    return """\
Produce a final structured certificate listing ALL surviving findings \
from this entire conversation. For each finding, include:

1. FINDING ID (sequential, e.g. C5-01, C5-02, ...)
2. COMPONENT (Dendritic Cell / NK Cell / B Cell / Helper T Cell / \
Regulatory T Cell / Pipeline / Cross-Component)
3. CLASSIFICATION (correctness / security / mathematical / boundary / \
injection / silent-failure / performance / dead-code)
4. SEVERITY (P0 critical / P1 normal-operation / P2 edge-condition / \
P3 defence-in-depth)
5. DESCRIPTION (concise statement of the bug)
6. EVIDENCE (execution trace or formal proof)
7. CROSS-COMPONENT IMPACT (what other components are affected, if any)
8. PROPOSED FIX (specific code change, new construct, or architectural \
recommendation)
9. FIX TYPE (PATCH / NOVEL CONSTRUCT / ARCHITECTURAL)
10. PRIOR MATCH (if this matches a finding from the prior reviewers, \
state which MF-XX; if novel, state NOVEL)
11. STATUS (CONFIRMED — survived falsification / RETRACTED — state why)

Also provide a summary table at the end with counts by: severity, \
component, fix type, and novel vs confirmed."""
