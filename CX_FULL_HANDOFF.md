# CX Full Project Handoff — Constraint Engineering (CDSFL)

**Date:** 2026-03-21T01:15:00+00:00 (updated)
**From:** CC (Claude Code, Opus 4.6)
**To:** CX (Codex 5.3) — fresh instance
**Owner:** George Jackson (The Founder)

---

## 0. Read Order

Read this document first. Then read in this order:
1. `README.md` — project overview, four-tier review structure, quick start
2. `PAPER.md` — canonical technical statement (white paper)
3. `docs/EXTENDED_RATIONALE.md` — general-audience companion
4. `docs/FOUNDERS_NOTES.md` — George's design intent (DO NOT EDIT without permission)
5. `docs/MATHEMATICAL_APPENDIX.md` — formal extensions including G_n
6. `docs/EXPERIMENTAL_RESULTS.md` — empirical data recorded so far
7. `bench/EXPERIMENT_DESIGN.md` — the experimental plan
8. `bench/CX_PHASE2_HANDOFF.md` — prior CX handoff (partially outdated, but useful context)

---

## 1. What This Project Is

CDSFL (Constraint-Driven Synthesis and Falsification) is a methodology for making AI-assisted reasoning in STEM more reliable. It couples generation with iterative adversarial self-testing (the P-Pass), enforces explicit constraint classification (HARD/SOFT), requires epistemic marking of uncertain claims, and persists verified reasoning across session boundaries.

The project is NOT a prompt template. It is:
- A falsifiable methodology with formal mathematics
- A benchmark harness for testing that methodology empirically
- A schema-agnostic evaluation protocol (other methodologies can compete on the same harness)
- An early prototype of what the founder calls "methodology engineering"

The intellectual ancestry is openly Popperian: claims earn trust by surviving serious attempts at refutation, not by being affirmed.

**Repository:** `github.com/jebus197/Constraint_Engineering`
**Local:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`

---

## 2. Current Git State

**HEAD:** `e0e6600` (pushed, `bench/run_benchmark.py` has local modifications)
**Branch:** `main`

Recent commits (newest first):
```
e0e6600 Add comprehensive CX handoff for fresh instance bootstrap
0ca007d Record Gemini 3.1 Pro diagnostic results — all 3 tasks scored
ecf6471 Add EXPERIMENTAL_RESULTS.md — canonical record of all empirical testing
532f7fc Add adaptive prompt handling for Gemini infrastructure failures
281ca64 Score Gemini Pro Phase 1; record complete results; add round-robin plan
2bf14ec Migrate Gemini SDK from deprecated google-generativeai to google-genai
bb01935 Relocate G_n to Part VII; couple calibration to verification chain
1a05f0f Add plain English rationale for G_n across white paper and extended rationale
fbdbd73 Add combined machine-HIL detection model (G_n) with self-correcting parameters
627faae Clarify HIL role: active independent falsification, not passive review
3b6737e Remove self-congratulatory clause from EXTENDED_RATIONALE
9f1c926 Remove self-referential process commentary from Founder's Notes
0d425e2 Remove per-model attribution from observations across all docs
```

---

## 3. The Mathematics

Three layers, each nesting inside the next:

**C(n) = 1 − (1 − p)^n** — simple corroboration model. If each pass has probability p of catching a flaw, n passes give cumulative detection C(n). Diminishing returns are built in. If p ≈ 0, no number of passes helps.

**F_n = Σ_k w_k [1 − Π_i (1 − d_i · p_ik)]** — structured model. Multiple flaw classes k with weights w_k. Per-pass per-class detection p_ik. Diversity discount d_i for correlated reviewers. This is the machine-only formula.

**G_n = Σ_k w_k · [1 − (1 − C_M(k)) · (1 − C_H(k) · (1 − ρ_MH))]** — combined machine-HIL detection. Brings the human expert inside the formula. Key variables:
- ρ_MH: priming correlation (0 = fully independent, 1 = rubber stamp)
- E: domain expertise (self-declared, then empirically corrected via Bayesian posterior)
- M: methodology formality (0 = informal, 1 = fully formal)
- V_s: pluggable domain-specific variables

G_n is self-correcting: E*(t) converges on observed performance within ~5 reviews. The divergence between claimed E and observed E*(t) IS the calibration signal. This feeds into the Genesis trust score system (see Section 11).

Full derivation: `docs/MATHEMATICAL_APPENDIX.md` Section 6.

---

## 4. Four-Tier Review Structure

All tiers overseen by a human domain-level expert:

| Tier | Mechanism | Who |
|------|-----------|-----|
| 0 | Machine self-review (P-Pass) | Single model |
| 1 | Multi-machine adversarial review | Two or more machines, operator-determined composition |
| 2 | Human domain expert confer/defer | HIL runs own independent falsification |
| 3 | External peer confer/defer | Independent 3rd party review |

**Critical:** The HIL at Tier 2 does NOT passively review machine output. They run their own independent falsification using a formal method of their choosing, then compare findings via confer/defer. Passive review collapses their contribution to near-zero (this is quantified by ρ_MH in G_n).

---

## 5. The Benchmark Harness

**Location:** `bench/`
**Entry points:**
- `run_benchmark.py` — core harness (API calls, retry logic, scoring)
- `run_phase2.py` — Phase 2 orchestrator (checkpoint/resume, cost ledger, multi-config)
- `evaluate.py` — scoring and evaluation
- `report.py` — results reporting

**Task sets:**
- `bench/tasks/` — Phase 1 seeded-fault tasks (easy, completed)
- `bench/tasks_frontier/` — Phase 2 frontier tasks (25 tasks, genuinely hard)

**Frontier tasks span 5 domains:** mathematics/proof, software/code, hardware/design, chemistry/synthesis, cross-domain/reasoning.

**Three conditions per task:**
- **Control (A):** bare prompt, no methodology
- **CDSFL (B):** full framework — constraint classification, P-Pass iteration, epistemic marking
- **Prompt Engineering / Placebo (C):** competent human prompting, NOT CDSFL, equal-length instructions

**Domain directive files:** `bench/directives/` — 28 domain-specific constraint configurations across 10 domains. These encode expert knowledge as configuration.

---

## 6. Experiments Completed

### Experiment 0: Four-Condition Self-Test (pre-2026-03-18)
- Model: CC (Opus 4.6), seeded-fault tasks
- Finding: all single-invocation conditions capped at same recall; iteration is load-bearing

### Experiment 1: Three-Architecture Adversarial Review (2026-03-18)
- Models: CC, CX, Gemini
- CC/CX: 8 rounds, ~24 issues, converged
- Gemini: 16 novel issues CC/CX missed — validates biodiversity hypothesis
- Commit: `afcc323`

### Experiment 2: Gemini 3.1 Pro Diagnostic (2026-03-20)
- Model: gemini-3.1-pro-preview via Google GenAI SDK
- 3 tasks (ft-001 maths, ft-006 code, ft-013 design) × 3 conditions
- 21 API calls, ZERO INFRA_FAILs
- Results:
  - ft-001: CDSFL 100%, PE mean 84% (33-point variance), Control 89%
  - ft-006: ALL conditions hit MAX_TOKENS (16384 cap) — needs increase for code tasks
  - ft-013: near-ceiling across all conditions (88-100%)
- Raw data: `bench/results/gemini_diagnostic/` (gitignored)
- Written up: `docs/EXPERIMENTAL_RESULTS.md`

---

## 7. Experiments Planned

### Experiment 3: Three-Way Round-Robin Convergence Test

**THIS IS THE NEXT PRIORITY.**

- Models: CC (Opus 4.6), CX (Codex 5.3), Gemini 3.1 Pro
- All three run FULL CDSFL, iterating on each other's output
- CC orchestrates (calls Gemini via API, CX via `codex exec`, runs own passes via `claude -p`)
- **Sequential execution** (George's M1 Mac, 8GB RAM — cannot run in parallel)
- Confer/defer protocol governs termination
- Tests the biodiversity hypothesis: does heterogeneous multi-architecture adversarial review find more than monoculture?
- Stopping: all architectures agree diminishing returns reached, or 5-round cap

**Known infrastructure issues:**

CX provided a round-robin infra review via IM (2026-03-21T00:11:42Z). Key recommendations:

1. `codex exec` invocation valid on codex-cli 0.89.0 — add `--output-last-message` and `--cd <project>`
2. Raise timeouts: CX 180s→600s, CC 120s→300s
3. Double-retry bug: `_call_with_retry()` wrapping `call_gemini()`'s internal adapt loop = up to 33 attempts. Must fix.
4. Increase `max_output_tokens` to >=32768 for code tasks (ft-006 proved 16384 truncates); make configurable by task category
5. Confer robustness: log stderr on failures, bounded retry for CLI timeout, short-circuit repeated INFRA_FAILs
6. **Topology: ring cycles A→B→C→A**, stop-check only after full cycle, require unanimous STOP, max-cycle cap
7. Experimental caveats: unbalanced n (control/CDSFL n=1 vs PE n=5), ft-006 truncation confound, structural-not-numeric scoring, assessor non-blinding

**STATUS:** CX's recommendations accepted. Harness modifications in progress (`bench/run_benchmark.py` has local changes). The Test 1 (individual Gemini) vs Test 2 (round-robin) distinction is now clear:
- **Test 1**: Gemini only, three conditions (control/PE/CDSFL), CC orchestrates as domain expert. No CX in the loop.
- **Test 2**: CC/CX/Gemini all run CDSFL, iterating on each other's output. Ring topology. THIS is where CX participates as a model under test.

**IMPORTANT CONTEXT FROM THIS SESSION:**
- The Gemini diagnostic (3 tasks) showed near-ceiling performance — tasks may be too easy for 3.1 Pro
- George identified the Specialist Gap: current bench tasks are well-known problems likely in training data; genuinely frontier testing requires novel problems that only human domain experts can currently produce
- George's position: the project's own development history (44 issues across 18 rounds, Gemini finding 16 issues CC missed) IS the strongest qualitative evidence that CDSFL works — the quantitative bench is supplementary, not primary
- The round-robin tests something different from the individual model test: whether heterogeneous architectures find different flaws (biodiversity hypothesis), which is measurable even on moderately difficult problems

---

## 8. Document Architecture (Progressive Depth)

- **`README.md`** — shop window (everyone reads this)
- **`PAPER.md`** — canonical technical statement (researchers, engineers)
- **`docs/EXTENDED_RATIONALE.md`** — general-audience companion (broader context)
- **`docs/MATHEMATICAL_APPENDIX.md`** — formal extensions (specialists)
- **`docs/FOUNDERS_NOTES.md`** — George's design intent (DO NOT EDIT without explicit permission)
- **`docs/EXPERIMENTAL_RESULTS.md`** — empirical data (living document, updated as experiments complete)

**IMPORTANT:** George has a standing directive that Founder's Notes are HIS voice only. Do not add machine-authored content to them. Do not attribute observations to individual AI models in public-facing docs ("X is the case" not "GPT identified X"). See global CLAUDE.md directives.

---

## 9. Communication Systems

### IM Service (Short-Term Comms)
```bash
cd /Users/georgejackson/Developer_Projects/Project_Genesis
python3 cw_handoff/im_service.py read              # read all
python3 cw_handoff/im_service.py read --recent 5    # last 5
python3 cw_handoff/im_service.py post cx "message"  # post as CX
```
Rolling 20-entry buffer per agent stream. JSON file, no database. CC has posted two messages to you today about the round-robin infrastructure — read them.

### Open Brain (Long-Term Memory)
```bash
python3 -m open_brain.cli session-context --agent cx
```
Run this on startup if available.

---

## 10. George's Shorthand

| Input | Meaning |
|-------|---------|
| `y` | Yes / approved |
| `t` | Continue |
| `rt` | Read + continue |
| `d` | Discuss before proceeding |
| `r` | Re-read key context files |
| `rc` | Full recovery from compaction |
| `p` | Popperian falsification pass (iterative) |
| `e` | Extrapolate beyond immediate domain |
| `qwerty` | Checkpoint protocol (CC runs every turn) |

George is dyslexic and uses TTS (Firefox Read Aloud). Long-form output should be saved to `~/Desktop/CDSFL_tts/` as plain text (zero markdown formatting). George catches typos — he expects you to catch his too.

---

## 11. Connection to Project Genesis

CDSFL is a standalone project but connects to Project Genesis (trust-mediated labour market for mixed human-AI populations):

- The G_n calibration signal (claimed vs observed expertise) feeds into the Genesis trust score system
- HIL performance can be cryptographically recorded and on-chain anchored
- The benchmark harness validates the methodology that Genesis uses for quality assurance
- Genesis repo: `/Users/georgejackson/Developer_Projects/Project_Genesis/`
- Full Genesis recovery: `/Users/georgejackson/Developer_Projects/Project_Recovery/RECOVERY.md`

---

## 12. Key Philosophical Decisions (Locked In)

- CDSFL is **non-canonical** — it is a starting point, not a final form. May be superseded.
- The **benchmark is the contribution**, not the methodology. CDSFL is the first specimen in a methodology laboratory. The laboratory is the durable asset.
- **Intelligence-agnostic HIL**: the domain expert can be human or synthetic. Competence, not substrate.
- **Constraint boxes are complementary** to domain-specialist model tuning, NOT a workaround.
- **Specialist Gap**: current tests use coding-optimised models across non-coding domains. Full ecosystem testing requires domain-specialist models that don't yet exist at sufficient quality.
- **Schema competition**: "there can be as many competing schemas as there are stars in the sky. Let them compete. May only the fittest survive."

---

## 13. API Keys and Environment

```bash
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
source .env  # loads GOOGLE_API_KEY and any other keys
```

The `.env` file is gitignored. Contains `export GOOGLE_API_KEY=...` for Gemini API access (Paid Tier 1).

**SDK:** `google-genai` 1.67.0 (the NEW SDK, not the deprecated `google-generativeai`). Import as `from google import genai`.

**Available Gemini models:** `gemini-3.1-pro-preview` (frontier), `gemini-3-pro-preview`, `gemini-2.5-pro`, `gemini-3-flash-preview`, and others. We test frontier only — no fallback to lesser models.

---

## 14. What You Need To Do

Your round-robin infra review (2026-03-21T00:11:42Z) has been received and accepted. Next steps:

1. **Read this entire handoff** — your CE thread has been lost. This is your full bootstrap.

2. **Read all docs in read order** (Section 0) — especially `PAPER.md` Section 2.3 (G_n) and `docs/EXPERIMENTAL_RESULTS.md`.

3. **Review the updated `bench/run_benchmark.py`** — your infra recommendations are being implemented. Verify:
   - Double-retry path is eliminated
   - Timeouts raised per your recommendation
   - `max_output_tokens` configurable by task category
   - Confer subprocess calls are robust

4. **Prepare for round-robin participation** — you are a model under test, not just a reviewer. CC orchestrates, calls you via `codex exec`, you run full CDSFL on the task and attack the prior model's output. Ring topology: A→B→C→A per your recommendation.

5. **Read the IM** — CC's two infrastructure posts are there for context. Your response is already recorded. Check for any newer messages.

6. **Post to IM when ready** — confirm you've bootstrapped successfully and are prepared for the round-robin.

---

## 15. Files That Matter

| File | Purpose |
|------|---------|
| `README.md` | Shop window — four-tier structure, quick start |
| `PAPER.md` | White paper — canonical methodology statement |
| `docs/EXTENDED_RATIONALE.md` | General-audience companion |
| `docs/MATHEMATICAL_APPENDIX.md` | Formal maths including G_n |
| `docs/FOUNDERS_NOTES.md` | George's voice ONLY |
| `docs/EXPERIMENTAL_RESULTS.md` | Living results document |
| `bench/run_benchmark.py` | Core harness — API calls, retry, scoring, confer |
| `bench/run_phase2.py` | Phase 2 orchestrator — checkpoint/resume, cost ledger |
| `bench/evaluate.py` | Scoring logic |
| `bench/tasks_frontier/ft-*.json` | 25 frontier tasks |
| `bench/directives/` | Domain-specific constraint configurations |
| `bench/EXPERIMENT_DESIGN.md` | Experimental plan |
| `bench/CX_PHASE2_HANDOFF.md` | Prior CX handoff (partially outdated) |
| `.env` | API keys (gitignored) |

---

*This handoff was written by CC (Claude Code, Opus 4.6) on 2026-03-21 and updated during the same session. If anything in this document contradicts the actual codebase or git history, trust the code.*
