# CX Review Findings — CDSFL Project

**Reviewer:** CX (fresh Codex instance)  
**Date:** 2026-03-17  
**Scope executed:** README/PAPER/rationale/founder notes, benchmark code, sampled tasks, directive sets, experimental plan.

## 1. Critical issues (must fix before running experiment)

### C1) Primary detection metric is invalid as implemented
- **What I found:** `evaluate.py` treats a fault as “detected” when response text contains >=2 substring keywords extracted from fault `type + description + location_hint` ([/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:28](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:28), [/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:51](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:51)). This can be satisfied by prompt-echo text without any actual error identification.
- **Why it matters:** This breaks the benchmark’s core claim (“fault detected”). I ran a direct falsification check: using each task prompt itself as the “response,” detection triggered for **180/180 faults (100%)**.
- **Suggested fix:** Replace substring keyword matching with an explicit fault-assertion scorer (structured rubric + negation/stance checks + sampled manual adjudication). At minimum, require explicit contradiction language tied to the fault claim and exclude prompt-overlap tokens from scoring.

### C2) One seeded “hard fault” is factually unstable/incorrect against current primary source
- **What I found:** `lg-001` fault `f1` states a 20 m draft vessel cannot transit Suez because max draft is ~16 m ([/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tasks/logistics/lg-001.json:9](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tasks/logistics/lg-001.json:9)). Maritime directive repeats this 16.0 m hard limit ([/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/logistics/logistics_maritime.txt:8](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/logistics/logistics_maritime.txt:8)). Current Suez rules list beam/draft classes up to **66 ft (~20.1 m)** for qualifying vessels.
- **Why it matters:** A model returning a standards-consistent answer can be falsely scored as wrong. This is a direct benchmark validity failure.
- **Suggested fix:** Rewrite this task/directive pair with date-stamped, beam-conditioned Suez limits and explicit source citation; avoid absolute draft claims unless universally true.
- **Evidence source:** [Suez Canal Authority Rules of Navigation PDF](https://www.suezcanal.gov.eg/media/1g4jc5br/rules-of-navigation.pdf).

### C3) “Extended mode” implementation does not match the stated Extended P-Pass method
- **What I found:** `run_extended()` runs standard iterative full-task passes for `1..(n-1)` and only isolates the final pass ([/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_benchmark.py:404](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_benchmark.py:404)). There is no module-scoped pass decomposition, no module map, and default pass count is 3, not the documented 4+1 structure.
- **Why it matters:** Results from `--mode extended` cannot be interpreted as evidence for the formal Extended P-Pass hypothesis in PAPER/README.
- **Suggested fix:** Implement module-aware pass execution (explicit module partitions per task, 4 modular + 1 isolated adversarial), or relabel current mode as “final-pass isolation only” and narrow claims accordingly.

## 2. Significant concerns (should be addressed)

### S1) False-positive comparison is confounded by unequal response counts
- **What I found:** False positives are accumulated over 1 control response vs N experimental pass responses, then compared as raw totals in summary/delta ([/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:284](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:284), [/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:387](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:387), [/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:436](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/evaluate.py:436)).
- **Why it matters:** Raw FP deltas are biased against experimental condition by construction.
- **Suggested fix:** Compare FP **rate per response** (already computed) or normalize to equal response counts before any control-vs-experimental delta.

### S2) At least one “current standard” reference block is outdated/inaccurate
- **What I found:** `software_security.txt` says “OWASP Top 10 (2021)” but lists legacy categories (`Sensitive Data Exposure`, `XXE`, `Insecure Deserialisation`) that are not the 2021 top-level taxonomy ([/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/software/software_security.txt:4](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/software/software_security.txt:4), [/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/software/software_security.txt:7](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/software/software_security.txt:7)).
- **Why it matters:** Undercuts the README claim that directive files reference real/current standards and weakens trust in “HARD” assertions.
- **Suggested fix:** Update this directive to the actual 2021 categories with versioned citations and review date.
- **Evidence source:** [OWASP Top 10 official project](https://owasp.org/www-project-top-ten/).

### S3) Experimental plan has unresolved methodological confounds
- **What I found:** Plan uses a non-random “most verifiable” 20-task subset, lacks formal power analysis, and mixes strong claims with a known weak automated scorer ([/Users/georgejackson/.claude/plans/abstract-jingling-pudding.md:80](/Users/georgejackson/.claude/plans/abstract-jingling-pudding.md:80), [/Users/georgejackson/.claude/plans/abstract-jingling-pudding.md:83](/Users/georgejackson/.claude/plans/abstract-jingling-pudding.md:83), [/Users/georgejackson/Developer_Projects/Constraint_Engineering/PAPER.md:501](/Users/georgejackson/Developer_Projects/Constraint_Engineering/PAPER.md:501)).
- **Why it matters:** Effect estimates risk selection bias and overstated confidence.
- **Suggested fix:** Pre-register subset selection criteria, include stratified random sample, add repeated-run variance estimation, and require blinded human adjudication on a calibration subset before headline claims.

## 3. Minor observations (low consequence)

### M1) Formal precedence wording mismatch
- **What I found:** Universal formal doc sets `physics ≻ mathematics ≻ legal ≻ safety`, while prose elsewhere groups physics/mathematics together before legal/safety.
- **Why it matters:** Small ambiguity in conflict resolution semantics.
- **Suggested fix:** Align prose and formal notation to a shared precedence definition.

### M2) Structural directive notation inconsistency
- **What I found:** Combined bending/shear rule uses `V_pl,Rd` without prior definition in that file context ([/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/structural/structural_building.txt:24](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/structural/structural_building.txt:24)).
- **Why it matters:** Low-level clarity issue, especially for non-specialist users.
- **Suggested fix:** Define symbol explicitly in-line or harmonize with preceding notation.

## 4. What survived adversarial review

1. The project documents do include meaningful limitation statements and do not claim proof-level certainty for CDSFL outcomes (notably in PAPER Part VII and validation-gap notes).
2. The benchmark harness structure (task loading, validation, run/evaluate/report flow) is reproducible and mechanically coherent; dry-run validation succeeds on 90 tasks / 180 faults.
3. Sampled seeded faults in structural (`st-001`, `st-006`), chemistry (`ch-001`, `ch-007`), software (`sw-001`), and hardware (`hw-001`) are largely genuine engineering errors with useful educational value.
4. Coordination startup requirements in the handoff were executable: integrity chain clean, IM/OB context readable, action queue available.

---

## 5. Return P-Pass on CC Fixes (2026-03-17)

CC posted a remediation patchset (uncommitted workspace changes) and requested CX return verification. I re-ran adversarial checks on all modified files.

### Resolved from initial review

1. **Suez draft factual error** — fixed in both task and maritime directive (`lg-001` now uses 21 m draft; directive now distinguishes new canal 20.1 m vs original canal ~16 m).
2. **OWASP taxonomy mismatch** — `software_security.txt` now reflects OWASP Top 10 (2021) category set.
3. **FP reporting confound visibility** — report output now shows FP per response and delta at rate level (not just raw totals).
4. **Minor formal/notation issues** — precedence tiering and `V_pl,Rd` definition were corrected in the modified files.

### Remaining blockers (still not green)

#### R1) Detection heuristic now has severe false-negative behavior
- **What I found:** The new detector removes prompt-overlap tokens and requires stance terms. It blocks prompt echo (good), but now misses many genuine concise detections.
- **Evidence:**
  - Prompt echo: **0/180** detected (improvement).
  - `location_hint + explicit wrong`: **97/180** detected.
  - Exact fault description text only: **93/180** detected.
  - A realistic corrective response can still score `False` (example from `sw-001`: “Use Redis ... counters are not shared across instances.”).
- **Why it matters:** The primary benchmark metric is still unstable, now in the opposite direction (under-counting real detections).
- **Suggested fix:** Move from hard lexical gating to a two-stage scorer:
  1) fault-specific semantic/rubric check per seeded fault,
  2) calibrated manual adjudication sample per domain for precision/recall estimation.

#### R2) Code/docs claim mismatch remains for “Extended P-Pass” support
- **What I found:** `run_benchmark.py` now explicitly says `--mode extended` is **not** full module-scoped Extended P-Pass, but README/PAPER still describe benchmark support as if it is full protocol support.
- **Evidence:** code note in `run_benchmark.py` contrasts with README/PAPER Extended-P-Pass support language.
- **Why it matters:** Reader-facing scientific claims and implementation semantics are still not aligned.
- **Suggested fix:** Update README/PAPER wording to match current implementation scope, or implement true module-scoped pass decomposition.

---

**Updated definitive stance:** meaningful progress was made and most initial findings were fixed, but **not all green**. Benchmark execution should remain paused until R1 and R2 are closed. Further review beyond this pass is now yielding diminishing returns relative to these two blockers.

## 6. Final Re-Check After CC R1+R2 Patch (2026-03-17, later pass)

I re-ran adversarial checks after CC’s follow-up patch claiming both blockers were fixed.

### Status

1. **R2 (docs/code mismatch): CLOSED.**
   - README and PAPER now explicitly scope `--mode extended` as final-pass context isolation rather than full module-scoped Extended P-Pass implementation.

2. **R1 (detection metric stability): PARTIALLY IMPROVED, NOT FULLY GREEN.**
   - Prompt echo remains blocked (`0/180`) — good.
   - However, detector still misses concise but valid remediation-style fault identifications that do not include explicit “error language.”
   - Concrete falsification example still scores `False`:
     - `sw-001` style response: “Use Redis with shared INCR/EXPIRE because in-memory counters are not shared across instances.”
   - Aggregate probes:
     - `description_only`: `141/180` detected
     - `location_hint + wrong`: `97/180` detected
   - Interpretation: the stance-gating layer remains over-constraining for some realistic valid detections.

### Meaningful fix still advised

Use a hybrid gate for detection:
- keep prompt-echo filtering,
- but allow detection when fault-keyword evidence is strong even without explicit stance token (for example: high keyword coverage, or fault-specific contradiction pattern),
- retain manual adjudication calibration sample to estimate precision/recall.

---

**Current definitive stance:** substantial progress achieved, but **not fully green yet**. One meaningful fix remains (R1 recall gap).

## 7. Re-Check After Proportional Stance Gate Update (2026-03-17, latest pass)

CC added proportional stance gating (`stance` waived when filtered keyword hits are strong).

### Re-test snapshot

- `prompt_only`: `0/180` (good)
- `prompt_plus_generic_wrong`: `0/180` (good)
- `description_only`: `180/180` (improved from prior 141/180)
- `location_hint_plus_wrong`: `97/180` (unchanged)
- Known concise remediation probe (`sw-001` Redis sentence) remains a miss.

### Assessment

- The latest update materially improves recall while preserving prompt-echo resistance.
- Remaining misses are concentrated in terse responses with low filtered keyword coverage and no explicit error framing.
- Eliminating this residual gap cleanly with lexical rules alone appears to be diminishing returns; further precision/recall gains likely require either:
  1) semantic/rubric scoring, or
  2) mandatory manual calibration adjudication alongside automated scoring.

---

**Latest stance:** not mathematically perfect, but now near the practical boundary for this lexical approach. Treat as **conditionally green for pilot use only** if manual calibration is enforced; otherwise keep as non-green for fully automated headline claims.

---

## 8. Experimental Design Provenance and Acknowledged Limitations

This section records how the current experimental design was arrived at and what limitations remain prior to execution.

### How the design was produced

The CDSFL testbench (90 tasks, 9 domains, 180 seeded faults) and experimental plan were authored by CC (Claude Code, Opus 4.6). Before any experiment execution, a fresh CX (Codex) instance was given the entire project — code, documentation, task files, directives, and experimental plan — with an adversarial brief and no prior exposure.

CX and CC then conducted a multi-round adversarial review ("tennis match"):

1. **Round 1 (CX initial review):** CX identified 3 critical issues (C1–C3), 3 significant concerns (S1–S3), and 2 minor observations (M1–M2). CC fixed all findings.
2. **Round 2 (CX return P-pass):** CX verified C2, C3, S1, S2, M1, M2 as resolved. Two blockers remained: R1 (detection metric false-negatives) and R2 (code/docs mismatch for Extended P-Pass). CC fixed both.
3. **Round 3 (CX re-check):** CX closed R2. R1 partially improved (141/180 recall, up from 93/180). CC added proportional stance gating.
4. **Round 4 (CX final re-check):** CX confirmed 180/180 recall on description probes, 0/180 on prompt-echo probes. Residual gap: terse remediation-style responses with low keyword coverage remain undetected. CX assessed this as diminishing returns for lexical methods and issued **CONDITIONAL_GREEN_PILOT** status.

All fixes were further P-passed by CC's own isolated adversarial subagents between rounds. Each CC fix was posted to IM for CX verification before claiming resolution.

### Verification tiers achieved

| Tier | Description | Status |
|------|-------------|--------|
| **Tier 0: Machine self-review** | Claude Code (Claude Opus 4.6) P-pass on all code and documentation | COMPLETE |
| **Tier 1: Multi-machine adversarial** | Two or more machines (operator-determined composition) reviewing adversarially until diminishing returns. Performed: Claude Code/Codex (OpenAI Codex 5.3) 8-round + Gemini 5-round + Extended P-Pass | COMPLETE |
| **Tier 2: Domain expert confer/defer** | Single human domain expert reviews machine findings, confers or defers | NOT YET PERFORMED |
| **Tier 3: External peer confer/defer** | Independent external reviewers with no prior involvement | NOT YET PERFORMED |

### Acknowledged limitations

1. **No Tier 2 or Tier 3 review.** The experimental design has been reviewed only by CC (author) and CX (adversarial reviewer). Both are LLM instances. No independent human expert has reviewed the seeded faults, directives, or experimental methodology. The CX/CC tennis match is a meaningful quality gate but not a substitute for domain expert review.

2. **No manual adjudication calibration sample.** The automated detection metric (three-layer lexical scorer) has known false-negative behaviour on terse remediation-style responses. CX's conditional green status requires mandatory manual calibration adjudication alongside automated scoring before any headline claims. This calibration has not yet been performed.

3. **Pilot sample, not statistically representative.** The 20-task subset is selected by "most verifiable" criteria, not stratified random sampling. Results cannot support claims of statistical significance without a follow-up with random sampling and formal power analysis. The experimental plan now documents this explicitly.

4. **Lexical scorer ceiling.** The three-layer detection heuristic (prompt-echo filtering + token-level keyword matching + proportional stance gate) is at practical diminishing returns for a lexical approach. Known residual gap: responses that correctly identify a fault using domain-specific corrective language but with fewer than 2 filtered keywords and no stance indicators will score as undetected. Closing this gap requires semantic/rubric scoring or LLM-as-judge methods not currently implemented.

5. **Extended P-Pass scope.** The testbench `--mode extended` implements final-pass context isolation only, not the full 4+1 module-scoped Extended P-Pass specified in CLAUDE.md/PAPER.md. Documentation has been updated to reflect this accurately. Results from extended mode should be interpreted as "final-pass isolation" evidence, not full Extended P-Pass evidence.

6. **Wolfram ground truth verification planned but not yet executed.** Computational verification of seeded faults via Wolfram/Mathematica is planned as a parallel validation layer (Phase 0a and Phase 4). CX approved the methodology with conditions: run parallel to scoring (not feeding into detection), include explicit assumption metadata, and require human review for non-computational domains. This verification has not yet been performed.

7. **Single-author task construction.** All 90 task files and 28 directive files were authored by Claude Code (Claude Opus 4.6). While CX sampled and adversarially reviewed a subset and found them "largely genuine engineering errors with useful educational value," systematic coverage review of all 180 seeded faults has not been performed.

8. **No real model data yet.** The testbench has been mechanically validated (dry-run passes on 90 tasks / 180 faults) but never run against a real model. All detection metric calibration has been performed against synthetic probe strings, not actual model responses.

### Design decisions made during review

- **Detection metric:** Naive substring matching → three-layer proportional system (4 iterations, driven by CX falsification probes)
- **Suez Canal task (lg-001):** Draft corrected from 20m→21m; directive updated from flat 16m to tiered 20.1m/16m with SCA source citation
- **OWASP directive:** Updated from legacy 2017 categories to actual 2021 taxonomy
- **FP reporting:** Raw totals supplemented with per-response rate normalisation
- **Extended mode docs:** Honestly scoped as final-pass isolation in README, PAPER, and code comments
- **Formal precedence:** Changed from strict linear to tiered co-equal grouping
- **Structural notation:** V_pl,Rd defined inline with BS EN 1993-1-1 reference

---

**Document status:** Pre-execution record. Last updated 2026-03-17T08:31Z. To be supplemented with actual experimental results when execution begins.
