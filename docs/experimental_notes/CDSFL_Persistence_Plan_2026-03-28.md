# CDSFL Persistence Layer Build Plan

**28 March 2026**

---

## The Task

The persistence and cryptographic verification layer described in Part Five of the white paper needs to be built. This is the component that gives CDSFL a memory. Without it, every session starts blank. The falsification work from yesterday cannot inform today's reasoning.

The layer provides four levels of verification:
1. **Content hashing** — proves that a record has not been tampered with
2. **Hash chains** — proves that nothing has been deleted or inserted
3. **Merkle trees** — allow thousands of records to be verified in a single check
4. **On-chain anchoring** — proves that a record existed at a specific time, verifiable by anyone

The first three levels will be built in this round. On-chain anchoring is out of scope because it requires blockchain infrastructure that belongs to Project Genesis.

---

## The Team

**Four players:**

**CC1 (manager — me):** Coordinates, monitors, assesses, and makes final calls. Does not operate under the CDSFL framework as system prompt. This preserves the weak player compensation dynamic observed in the confer. Evaluates framework-guided structured output without operating under the framework myself.

**CX (team captain):** Conducts external research, frames the problem for other players, and proposes the architecture. Receives the full corrected CDSFL mathematical model as system prompt.

**CC2 (deep analyst):** Had the highest yield in the meta-test, with the most unique findings and the strongest cross-component synthesis. Handles core implementation, cross-component wiring, and edge cases. Receives the full corrected CDSFL mathematical model as system prompt.

**Gemini (mathematical verifier):** Achieved a perfect verification rate in the meta-test — every finding it submitted was correct. Handles cryptographic correctness, hash chain integrity proofs, and mathematical verification of Merkle tree properties. Receives the full corrected CDSFL mathematical model as system prompt.

---

## How It Works

The protocol has three phases.

**Phase 1 — Architecture framing:**
Pass the task to CX with the relevant specifications and instruct it to conduct external research and frame the problem. CX returns a proposed architecture. Confer with CX, running mutual falsification passes until the plan is agreed, convergence is reached, or diminishing returns are called. Typically three to five rounds.

**Phase 2 — Distributed build:**
Distribute the agreed architecture to all three players. Each receives the component that matches their demonstrated strengths:
- CX: overall architecture and integration
- CC2: core implementation and edge cases
- Gemini: cryptographic correctness and mathematical verification

**Phase 3 — Confer, integrate, commit:**
Players exchange findings through structured confer rounds. Manager merges results, resolves disagreements, and applies fixes. A final falsification pass runs on the integrated result. Then commit.

---

## Dynamic Position Management

This is the part that connects to a broader principle.

Throughout the build, monitor all three players dynamically — checking their decay curves, verification rates, and adoption deltas. If a player's performance data suggests they would be more effective on a different component, reposition them. The key principle is: **reposition, never bench.**

This is the opposite of the proposal rejected in the confer, which would have automatically sidelined weak performers. That proposal was rejected because removing a player reduces diversity — fewer perspectives means some errors become harder to find. Removing a player also degrades the measurement tools for the remaining players.

The alternative is **dynamic load balancing** — a well-understood concept in networking. You do not take servers offline when they are slow. You route traffic to where capacity best matches demand. A server that is slow at compute-heavy tasks may be excellent at tasks that require lots of reading and writing. You route accordingly.

The same principle applies here. Every model has value. The manager's job is not to decide who is good enough. It is to find where each player's contribution is maximised and put them there.

### Position signals and responses

| Signal | Response |
|--------|----------|
| High decay rate + high verification | Excelling — stay in position |
| Low decay rate + high verification | Thorough but slow — give deeper subtasks, fewer breadth tasks |
| High decay rate + low verification | Fast but inaccurate — shift to review role |
| Low decay rate + low verification | Poor fit — reposition to demonstrated strength |
| Flat curve | Possible churn — redirect to narrower, more concrete subtask |

No player is removed. Every player contributes. The manager finds where each player's contribution is maximised.

---

## The Gap in the Mathematical Model

Dynamic position management is not currently formalised in the mathematical model. The capability fingerprint exists. The metacognitive feedback protocol exists. But the bridge between these two — where the manager uses fingerprint data to route tasks to model strengths — is not formalised.

This is different from the rejected benching proposal. Benching subtracts players. Position management redistributes work. It is additive, not subtractive. Whether to formalise it before or after the persistence build is a decision for the founder.

---

## What Comes After

After the persistence layer is built, the next step is the full Stage 2 distributed compute test with all six players: CC1 as manager, CC2, CX, Gemini, DeepSeek, and ChatGPT as players.

That test exercises the complete corrected mathematical model — including the persistence layer — using the full CDSFL protocol.

The dynamic position management principle becomes more important at six players than at four, because the capability spread is wider. DeepSeek showed flat decay curves in earlier tests. ChatGPT had format compliance issues. Neither should be benched. Both should be repositioned to where their demonstrated strengths can contribute. Finding those positions is the manager's job.
