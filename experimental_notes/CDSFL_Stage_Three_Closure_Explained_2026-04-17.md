# CDSFL — Experiment 40 Stage 3 Closure Explained

**Timestamp:** 2026-04-17T14:30:00+01:00
**Commits:** `8b8682d` (Phase A) → `bdfc93a` (Phase B) → `6580737` (docs sync) → `7326a04` (sv)
**Test state:** 1,250 tests passing
**Branch:** `exp39-experimental`, pushed to origin

---

## Part 1 — What the project is, in plain English

Constraint Engineering, also called **CDSFL** (Constraint-Driven Synthesis and
Falsification Loop), is a methodology and a software framework for making
AI-assisted technical work more reliable. It is built around one observation:
when several AI models work together, and each one tries to falsify the
others' output, the group produces technical work more reliable than any
single model on its own. But asking models to check one another is not
enough — they can all be confidently wrong in the same way. To close that
gap, every important claim must be verified by a mechanical tool wherever
such a tool exists.

- Mathematics → SymPy
- Logical constraints → z3
- Chemical formulae → RDKit + a stoichiometric balance checker
- Dimensional analysis → pint
- Code behaviour → pytest, mypy, ruff, bandit, crosshair

The language models propose claims, the mechanical tools verify them, and
the human in the loop makes the final call on anything that remains
uncertain.

The framework borrows naming from the human immune system as a metaphor.
Findings are like antigens. B-Cells are specialist verifiers per domain.
T-Cells pursue claims through structured prompts. Macrophages observe and
summarise. Ouroboros queries external literature through arXiv and
Semantic Scholar when the internal pipeline is uncertain. The metaphor is
architectural, not literal — it keeps roles distinct and interfaces clean.

**Repository:** `github.com/jebus197/Constraint_Engineering`
**Founder:** George Jackson. **Primary collaborator:** Claude Opus 4.6.
**Independent falsifier:** OpenAI Codex 5.3. **Additional review models:**
DeepSeek Reasoner, Gemini 3.1 Pro, ChatGPT 5.4.

---

## Part 2 — What was built in the Stage 3 closure

Experiment 40 is the next scheduled empirical run. The period between
Experiment 39 and Experiment 40 was spent closing refinements deferred
from prior work. These are collectively known as Stage 3 of the
Experiment 40–54 plan. The 17 April work closed most of them across two
autonomous continuation rounds (Phase A and Phase B) plus a documentation
sync commit.

### Phase A — `8b8682d` (98 new tests)

| Item | What it does |
|------|--------------|
| 1D.5 | Pre-checks the format of the scoring sub-equation S_k and asks a model to reformat when wrong. |
| 1D.6 | Extracts verdicts from Gemini's output format (previously leaked as parse errors). |
| 1E.6 | Sizes decomposition of a target file by actual payload rather than a fixed constant. |
| 1E.7 | Wires a cross-model diversity metric into per-round logging — makes compliance theatre observable. |
| 1E.10 | Adds `compute_rk_with_eta_channel` wrapper that validates the §18 channel invariant and raises `ChannelViolationError`. Library form only; call-site flip gated on Exp 54. |

### Phase B — `bdfc93a` (200+ new tests)

| Item | What it does |
|------|--------------|
| 1D.3 | Per-model ρ tracking. ITC (the mechanism that restarts stuck models with fresh context) can now target the stuck model rather than firing globally. |
| 1E.3 | Audit for specialist-cell live promotion. Single-line flip is available but deliberately not applied (see Part 3). |
| 1E.4 | Makes physics (K), chemistry (L), engineering (M) specialists functional in shadow. Astropy for astronomical claims. RDKit for SMILES/molecular formula. Pint for factor-of-safety / dimensional engineering. Stoichiometric balance for chemical equations. 21 tests. |
| 1E.5 | Populates fingerprint attention metrics (`measured_attention_span`, `compression_threshold`, `quality_at_capacity`, `decomposition_recommended`, `attention_ratio`, `D_decay`) from ITC + parse-yield history. |
| 1E.8 | Ouroboros query-quality fix. Literal finding-IDs no longer leak into arXiv queries. Live arXiv network test confirms `live` / `live_empty` status. 12 tests. |
| 1E.9 | Cross-round recidivism. Flags an alternative proposed in round K+1 that is substantively identical to one from round K. |
| 1E.11 | `bench/openrouter_tools.py` — structured function-calling pathway for the four non-Claude panel models. 5 TOOL_SPECS (sympy/z3/pytest/ruff/mypy). Subprocess-isolated dispatchers. Path-safety gatekeeper. Tool-call loop capped at 6 iterations. 36 tests. |
| 1E.12 | `_verify_deepseek_formal` — DeepSeek R1 as formal-verification specialist. Invoked only when z3 AND SymPy both return UNCERTAIN (cost control). Confidence capped at 0.5 so it cannot outrank mechanical proofs. 29 tests. |

### Docs sync — `6580737`

Aligned the Experiment 40 progress document with the Phase A + Phase B
commits. 8 DEFERRED → IMPLEMENTED with hash references. Stage 2 remainders
dropped to 0; Stage 3 remainders dropped to 2 (both gated).

### sv — `7326a04`

Save-state commit. ONBOARDING.md + RECOVERY.md qualitative updates; auto-
managed marker blocks preserved; CURRENT_STATE.md regenerated; memory
files updated. Pushed to origin/exp39-experimental.

---

## Part 3 — What is still in shadow mode

The framework draws a deliberate distinction between **live** (affects
experimental outcomes via scoring / admissibility / convergence) and
**shadow** (computed and logged, but does not influence outcomes). Shadow
lets the framework gather empirical data about a component before
committing it to the live path.

### Residual shadow elements

| Element | Location | Promotion path |
|---------|----------|----------------|
| Specialist cells K, L, M (physics / chemistry / engineering) | `LIVE_SPECIALIST_DOMAINS` frozenset at `immune_agents.py:334`; dispatch gate at line 5373 | One-line edit. Held back pending empirical data on K/L/M. |
| Runtime channel-invariant assertion | Wrapper `compute_rk_with_eta_channel` at `reference_runner_v2.py:3177`; production call-site uses bare `compute_rk` at line 3510 | Gated on Exp 54 — divergence penalty does not flow into compute_rk until then. |
| Reference runner v2 | Entire `bench/reference_runner_v2.py` file | Founder decision to supersede v1. |
| Cross-model diversity metric | `reference_runner_v2.py:4470`, comment: "Logging-only — does not gate admission or R_k" | Requires calibration + Exp 54 attribution. |
| Cross-round recidivism | Same section | Requires calibration + Exp 54 attribution. |

### Not shadow, but broken

`_verify_sympy` in `immune_agents.py` — sandboxed subprocess uses
`global_dict={'__builtins__': {}}` which prevents SymPy from constructing
`Integer` literals during parsing. Every SymPy specialist verdict in the
live pipeline currently returns UNCERTAIN regardless of claim truth.
Framework-wide silent regression. A separate background session has been
delegated to repair it without reopening the MF-40 RCE vector the current
blocklist closes.

---

## Part 4 — Tool coverage per domain

**Correction from an earlier exchange:** the tooling count across shadow
and live domains is the opposite of what was previously implied.

| Domain | Tool count | Live? |
|--------|-----------:|-------|
| chemistry (L) | 8 | shadow |
| physics (K) | 7 | shadow |
| biology | 6 | live |
| engineering (M) | 6 | shadow |
| cs_software | 9 | live |
| mathematics | 5 | live |
| information_science | **4** | live (shallowest) |
| statistics | 3 | live |

Information science is the shallowest LIVE domain. Physics and chemistry
both have more tools than information science. The tool-coverage
argument against flipping K/L/M to live does not hold. The real gate is
that K/L/M have not been exercised end-to-end on real experimental data.

### Priority tool expansion targets

| Domain | Additions (priority order) | Per-tool effort |
|--------|---------------------------|-----------------|
| information_science (priority — shallowest live) | rank-bm25, nltk/spacy, gensim | ~200–400 LOC + 20–30 tests, ~2–4 h each |
| physics | scipy.constants verifier, sympy.physics.units, mpmath high-precision | same |
| chemistry | pubchempy canonical IDs, deeper RDKit exposure (tanimoto, murcko scaffolds, reaction templates) | same |
| engineering | handcalcs for structural calc verification, scipy.signal for control systems | same |
| biology | ete3 for phylogenetics, deeper Biopython (BLAST, ORF finders) | same |

---

## Part 5 — The routing question

Claim-type routing is hybrid, not a dumb script.

**Layer 1 — regex (`_classify_claim_v2` at `immune_agents.py:3954`).**
Patterns per-domain in `bench/cdsfl_registry/domains/immune/*.toml`.
Returns `(ClaimType, extracted_text, confidence)`. Confidence values:
0.85 statistical, 0.80 code_structural, 0.75 code_behavioral (in
cs_software), 0.70 mathematical, 0.65 logical.

**Layer 2 — Claude Haiku (`typed_llm_classifier` at `immune_agents.py:4559`).**
`_CLASSIFIER_MODEL = "haiku"` via local Claude CLI (Max subscription).
Serialised behind `_CLAUDE_CLI_LOCK`. 45 s timeout. Fails open.

- **Software domain:** LLM is PRIMARY. Any valid LLM classification wins
  over regex, because Exp 38 data showed regex agreed with LLM only ~15%
  of the time on code findings.
- **Non-software domains:** LLM is override-only, requires
  `llm_confidence ≥ 0.70` plus a MATHEMATICAL guard that blocks overrides
  out of the mathematical type in ambiguous cases.

Once claim type is fixed, the per-domain TOML provides an ordered tool
list for that claim type. Dispatch walks the list left-to-right; first
definitive verdict wins.

**Recommended improvement.** Add a second Haiku pass that selects *which*
tool in the list is most diagnostic for a given claim, rather than
relying purely on the hand-authored order. One prompt template, one
config key, reuse the existing CLI lock. Modest effort.

---

## Part 6 — The naming question

The biological metaphor favours **"Specialists"** (code-level) and
**"Domain Specialists"** (public-facing). The motivation: the purpose of
a per-domain specialist is to give the human in the loop broader coverage
and deeper tool breadth than a human could realistically assemble on
their own. If a domain has only one tool behind it, it is not an expert —
it is a wrapper. The name should emphasise breadth.

- "Synthetic expert" — fine for casual prose, reads as marketing in
  technical documents.
- "Domain-Expert Verifier" — functionally accurate but mouthful.
- **"Domain Specialist"** — recommended. Preserves the biological
  framing and implies genuine tool breadth.

---

## Part 7 — DeepSeek's two roles

Both wired and operational; they are distinct functions using the same
underlying model via different endpoints.

| Role | Endpoint | Location | Tests |
|------|----------|----------|-------|
| Formal-verification specialist | Direct DeepSeek API (`DEEPSEEK_API_KEY`) | `_verify_deepseek_formal` at `immune_agents.py:1159`; `call_deepseek` from `experiment_11_orchestrator` | 29 |
| Panel model (5-model star dispatch) | Direct API *or* OpenRouter (`deepseek/deepseek-r1-0528`), depending on confer script | `confer_divergence_round3_final.py`, `confer_stage6_full.py`, etc. | Operational since pre-Exp 40 |

---

## Part 8 — FFAFP adherence, honest assessment

- **FIND** — done. Gaps identified against the Exp40-to-54 execution plan.
- **FOLLOW** — moderate. Downstream consequences traced, but not
  exhaustively.
- **ANALYSE** — partial. Mechanical analysis (pytest, mypy, ruff) done;
  multi-model adversarial analysis **not** run on the new code.
- **FIX** — done.
- **P-PASS** — local pytest only. Full Popperian loop (adversarial panel)
  **not** performed on Phase A / Phase B code.

**Recommended before Exp 40 launch** — three-round independent review:

1. Five-model panel review of Phase A + Phase B code (what unit tests
   would miss).
2. Five-model panel review of the per-domain TOML configurations as
   expert-system designs, not as tooling wrappers.
3. Five-model panel review of proposed criteria for promoting physics,
   chemistry, and engineering from shadow to live.

---

## Part 9 — Open items before Experiment 40

1. Founder decision to promote reference runner v2 over frozen v1. v2 has
   all fixes and passes all 1,250 tests.
2. Optional: one-line flip promoting K/L/M specialists from shadow to
   live. Not required because Exp 40's target is a software module.
3. Recommended three-round panel review above.
4. Repair of `_verify_sympy` sandbox regression before any live
   experiment whose target exercises mathematical claims.

---

## Conclusion

After the 17 April work, the framework contains, in one connected system:
language models that propose; mechanical tools that verify; external
literature queried for triangulation; cross-model diversity and
cross-round recidivism as observable quantities; the scoring equation
with its channels and invariants made explicit; tool-use parity across
all five panel models; and a formal-verification specialist as cost-
bounded fallback when mechanical tools defer.

The infrastructure is in place. What remains is the discipline of
independent review before the infrastructure is used to produce the next
round of empirical results.
