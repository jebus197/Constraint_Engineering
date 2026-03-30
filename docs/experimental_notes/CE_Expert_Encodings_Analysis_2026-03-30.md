# Expert Encodings Analysis for the CDSFL Bench

**Date:** 30 March 2026

---

## What Exists Now

The bench has 28 domain-specific directive files across 10 domains. These are generic industry constraint boxes — things like creepage distances for hardware, CAP theorem for distributed systems, heat transfer calculations for process chemistry. They are organised by broad domain name and loaded automatically by the benchmark runner using the task's `domain` field.

The loading mechanism is simple: the runner reads the task's `domain` field, looks for a directory matching that domain name under `bench/directives/`, and loads the first text file alphabetically. There is no per-task selection, no manual mapping, and no variant matching unless explicitly requested via a command-line flag.

---

## The Mismatch

The directive content does not match the frontier tasks. This is systematic across nearly every task.

| Domain | Issue |
|--------|-------|
| **Mathematics** | All 7 mathematics tasks are proof-based. The mathematics directive explicitly states on its last line: "Not applicable to proof-based pure mathematics (theorem proving)." Every single mathematics task falls exactly into what the directive disclaims. |
| **Software** | All 6 software tasks get the distributed systems directive because it sorts first alphabetically. Only 1 of the 6 tasks (the lock-free queue) has any relevance to distributed systems. The other 5 are about data structures, algorithms, type inference, and computational geometry. |
| **Chemistry** | All 3 chemistry tasks get the analytical chemistry directive. One needs electrochemistry, one needs pharmaceutical crystallisation, one needs process distillation. None is analytical chemistry. |
| **Hardware** | Both hardware tasks get the embedded systems directive. One is battery thermal management, the other is audio DAC design. Neither is embedded systems. |
| **Cross-domain** | All 5 cross-domain tasks get the mechanical-electrical interface directive. Two are meta-reasoning tasks about proof protocols and calibration — no mechanical-electrical content at all. |
| **Industrial** | The one industrial task (rocket engine nozzle design) gets the CNC machining directive. |
| **Physics** | The one physics task (superdeterminism and quantum mechanics) gets nothing at all. There is no physics directory. |
| **Structural** | Two tasks get the bridge directive. One is about steel columns with fire resistance, which would be better served by the building directive that already exists in the same directory. |

---

## What the Encodings Should Be

The insight is that these encodings should not just contain generic domain safety rules. They should encode what is known about the specific problem space under consideration. The constraint box bounds the model to that specific problem set and forces it to explore within that domain.

This is the same principle as the `CLAUDE.md` file. `CLAUDE.md` does not tell the model what to think. It tells the model how to think and where the guardrails are. An expert encoding for a specific frontier task does the same thing for that problem space.

### Example: FT-004 (Weierstrass function)

An expert encoding for this task would contain:

- The known structure of the Weierstrass function
- The parameter space and sufficient conditions
- The fact that continuity requires uniform convergence via the M-test
- The fact that nowhere-differentiability requires constructing an explicit sequence and producing quantitative bounds
- Known failure modes: hand-waving the bounds, using wrong conditions on `a` and `b`, confusing head and tail terms
- Verification criteria: what a complete proof must demonstrate

It would **not** contain the proof itself. It would **not** contain the specific sequence construction. It would **not** give the answer. It provides the constraints that bound the solution space. The model must still do the work.

**This distinction is critical.** If the encoding contains the answer, it tests whether the model can read, not whether it can reason. If the encoding contains only the constraints, it tests whether the model can reason within a properly bounded problem space. That is the configured synthetic domain expert hypothesis.

---

## Why This Matters Beyond the Bench

These encodings are transportable, tradable, exchangeable, upgradable, shareable, and iterative across communities:

- A crystallisation expert writes the FT-018 constraint box
- A propulsion engineer writes FT-017
- A type theorist writes FT-010

Each encoding is a portable unit of expertise that can be benchmarked, versioned, and improved.

The bench becomes a quality signal for encoded expertise. If encoding version A outperforms version B on the same task, the bench measures that difference. The critical unit shifts from "who has the best model" to "who can encode, test, and refine expertise most effectively."

This is the configured synthetic domain expert thesis in its most concrete form.

---

## The Runner Modification

The benchmark runner needs a small change. Currently it loads directives by domain directory. It needs to also check for task-specific encodings. The proposed lookup chain:

1. Check for a task-specific encoding in `directives/task_specific/ft-XXX.txt`
2. If found, use it as the task-level layer
3. If not found, fall back to the domain-level directive as before

The compose chain becomes three layers: universal CDSFL, then domain constraints, then task-specific expert encoding. Each is optional. The existing `--condition` flag handles which layers to include. The code change is approximately 15 lines.

---

## P-Pass Findings

### Pass 1 — Feasibility

The task JSON files themselves contain rich ground truth notes, verification methods, and known failure modes. These are effectively expert knowledge already encoded in a different format. The task-specific encodings synthesise this into constraint-box format. Feasible for all 27 tasks.

### Pass 2 — Answer leakage risk

If the constraint box says "the batch volume is V = 50 divided by the difference between hot and cold concentrations," that is the solution, not an expert encoding. The encoding should instead say: "Mass balance must account for residual solubility at the final temperature. Product yield does not equal total dissolved mass." The model must still figure out the calculation. Each encoding needs checking to verify it does not give the game away.

### Pass 3 — Ground truth isolation

The task JSON already contains exact answer values in the `ground_truth_notes` field. The expert encoding must be constructed so it does not leak these. It provides the constraint structure, not the solution values. This is a genuine authoring discipline.

### Pass 4 — Complementary layers

Both layers — domain and task-specific — are needed. The domain layer provides general field safety constraints. The task-specific layer provides the problem-space box. They are complementary.

### Pass 5 — Format consistency

The encoding format should mirror the existing directive format: HARD constraints, SOFT constraints, verification procedures, limitations. This keeps the layering consistent and the runner does not need special handling.

---

## Extrapolation

**What generalises.** If task-specific expert encodings measurably improve frontier task performance, the implication is that domain expertise can be encoded as portable, testable, shareable artifacts. The bench becomes a marketplace for encoded expertise, scored by measurable improvement on frontier tasks.

**Boundary conditions.** This breaks down when the problem space is genuinely novel — meaning no expert encoding exists because nobody has solved the problem before. FT-027 (the Riemann Hypothesis task) is an example; the encoding can only provide known structure and known non-results. It also breaks down when the constraint box is so specific that it effectively gives the answer. The right granularity is an empirical question.

**Falsifiable questions.**
1. Do task-specific encodings measurably improve accuracy compared to no encoding, domain-only encoding, and universal CDSFL alone? Directly testable.
2. Is the improvement due to constraint structure or knowledge content? Testable by creating structure-only encodings versus knowledge-only encodings.
3. Can the bench detect the difference between a good encoding and a bad one? If so, the bench functions as a quality signal for expertise — which is the marketplace hypothesis. [SPECULATIVE]
4. Can encodings be composed across tasks? If shared constraints can be factored out into sub-encodings, this would test composability. [SPECULATIVE]

---

## Proposed Sequencing

1. **Write 3 sample encodings first.** One mathematics (FT-004), one software (FT-010), one cross-domain (FT-017). This establishes the format.
2. **Founder reviews.** Iterate the format.
3. **Produce the remaining 24 in batch**, with the runner modification.
4. **Each encoding gets a light falsification pass** against its own task: does it provide the constraint box without leaking the solution?

The runner modification is small. The encodings are the bulk of the work.
