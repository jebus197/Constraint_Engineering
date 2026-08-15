# CDSFL Project — CC1 Configuration

Repository: `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`
Python: 3.13+ | Tests: `python3 -m pytest bench/tests/ -v`

## Command Scripts

On `sv` (save state): make qualitative updates to ONBOARDING.md and RECOVERY.md, update memory files, then run `python3 scripts/cdsfl_sv.py --commit --push -m "sv: <description>"` as the final step. The script generates state files, stages all sv-related changes, and atomically commits + pushes in a single subprocess (compaction-safe).

**sv sequential-reading protocol.** ONBOARDING.md, RECOVERY.md, MATHEMATICAL_APPENDIX.md, PAPER.md, CURRENT_STATE.md and project memory files have all grown large enough that a single parallel read inflates context without improving understanding. During sv preparation, read these documents sequentially — top to bottom, one section/chunk at a time — absorb each chunk, decide if it needs updating, then move on. Do NOT fetch several large documents in parallel just to "have them all loaded". The goal is carefully considered updates, not maximum file-awareness. This also reduces API overload risk during the sv window.
On `qc` (quality control): run `python3 scripts/cdsfl_qc.py` and fix reported issues.
On `rc` or `rs` (recover): run `python3 scripts/cdsfl_recover.py --full` and rebuild context from output.

## Key Documentation

- `experimental_notes/CDSFL_Agent_Operational_Plan.md` — **AGENT OPERATIONAL TRACKER** for the Exp 40–54 arc + Bench Run 2. Self-consumption note: terse, actionable, dynamically updated. **This repo copy is CANONICAL**; `~/Desktop/CDSFL_Agent_Operational_Plan.md` is the byte-identical mirror and still the convenient one to open. The repo copy wins because the tracker carries the recovery path, and an unversioned file on one machine's Desktop is a single point of failure. **FIRST READ on compaction** — it names the exact resume pointer, per-experiment target-article matrix, standing Exp-39→Exp-40 gap-closure list, and multi-tool cross-verification pairings.
- `docs/GLOSSARY.md` — every term, acronym, Greek letter defined
- `docs/ARCHITECTURE.md` — system components and data flow
- `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` — **CANONICAL EXECUTION PLAN** (Section XI). 4-phase plan: A (Exp 36 resume, 5 fixes), B (reference runner + CC2 architecture), C (Bench Run 2, 27 STEM tasks), D (docs/outreach). READ ON RECOVERY.
- `docs/REPRODUCING.md` — how to replicate experiments
- `docs/CURRENT_STATE.md` — machine-generated state snapshot (produced by sv script)
- `docs/MATHEMATICAL_APPENDIX.md` — mathematical framework (1991 lines, Stage 6 literature-calibrated extension added 14 April 2026)
- `resources/ONBOARDING.md` — full project history and context
- `resources/RECOVERY.md` — pending work and recovery protocol

## Model Confer Dispatch

Panel composition (current as of 2026-05-10, smoke-tested):

- `cc2` = Claude Opus 4.7 via CLI piped mode (`claude -p`), Max subscription
- `cx` = Codex GPT-5.5 via OpenRouter API (`openai/gpt-5.5`)
- `ge` = Gemini 3.1 Pro Preview via OpenRouter API (`google/gemini-3.1-pro-preview`) — moved from direct Google API to OpenRouter on 2026-05-10 to draw on existing OpenRouter credits at identical pricing
- `cgpt` = ChatGPT GPT-5.5 via OpenRouter API (`openai/gpt-5.5`)
- `ds` = DeepSeek V4 Pro via DeepSeek direct API (`deepseek-v4-pro`) — upgraded from R1-0528 on 2026-05-10; the older `deepseek-reasoner` is no longer listed by DeepSeek

All models run under latest CDSFL directives as system prompt. Combinable: `cx ge cc2`.
CDSFL directives: `bench/directives/universal/cdsfl_core_formal.md`
Composer: `bench/cdsfl_registry/composer.py`

Smoke-test record (2026-05-10, prompt: anchor "17 is prime", schema-conforming JSON with verdict/reasoning/falsification fields): all four upgraded routes returned `verdict=CONFIRMED` with non-empty reasoning and falsification, total wall-clock 36.8s sequential.

## Metacognitive Commands (MC)

Single-letter and short commands that direct model behaviour. Combinable
(e.g. `p a e d` = P-pass, analyse, extrapolate, discuss). Full reference:
`docs/REPRODUCING.md` § Metacognitive Commands.

| Cmd | Action |
|-----|--------|
| `y` | Yes / approved |
| `cy` | Continue the work AND apply live-experiment monitoring discipline: while any experiment/process runs, monitor ~every 60 s; on anything screwy/off, pause it, FFAFP (analyse with all tools), fix, then resume; always keep a terminal window open tailing the running experiment's full current output for the founder. (Standing directive 2026-05-18.) |
| `d` | Discuss before proceeding |
| `p` | P-pass — Popperian falsification (iterative: identify, fix, falsify, repeat) |
| `a` | Analyse dispassionately |
| `e` | Extrapolate beyond immediate domain |
| `f` | Find, Follow, Analyse (with available tools), Fix, P-pass (five-step cycle) |
| `sy` | Use all available mathematical and STEM tools (SymPy, Wolfram, SciPy, NumPy, z3, uncertainties, mpmath) in analysis |
| `t` | Send output to TTS file |
| `c` | Confer with another model, mutual P-passes until convergence |
| `sv` | Save state — run `python3 scripts/cdsfl_sv.py`, update recovery docs, commit |
| `qc` | Quality control — run `python3 scripts/cdsfl_qc.py`, fix reported issues |
| `rs` | Recover state — run `python3 scripts/cdsfl_recover.py --full`, rebuild context |
| `re` | External research (web search, arXiv, Semantic Scholar) |
| `ext` | External research (shorter alias for `re`) |
| `rt` | Read all recovery resources + continue |
| `r` | Re-read key context files |
| `x` | Override sleep/rest warnings |
| `sth` | Synthesise — consolidate findings into a coherent whole |
| `rg` | Regain full context on named topic — re-read anchoring memory files, canonical docs, and experimental notes before producing new output. Name the resources consulted. |
| `sq` | Sequential — strictly one tool call at a time, no parallel batches. Avoids stressing Anthropic servers during long runs. Sub-agents inherit the same constraint. |
| `pr` | Panel review — dispatch the full model panel (cc2, cx, ge, cgpt, ds; CX2/Codex-CLI optional 6th) on a completed analysis or design question under sy, sth, f, e, d, t. NO compelled convergence: each model gives an independent verdict + its strongest falsification; disagreement is preserved as information; CC1 actively participates with its own position and synthesizes the range. Mirror to TTS. |

### Model Confer Dispatch (combinable)

| Cmd | Model | Route | Identifier |
|-----|-------|-------|---|
| `cc2` | Claude Opus 4.7 | CLI piped mode (`claude -p`), Max subscription | `opus` |
| `cx` | Codex GPT-5.5 | OpenRouter API | `openai/gpt-5.5` |
| `ge` | Gemini 3.1 Pro Preview | OpenRouter API | `google/gemini-3.1-pro-preview` |
| `cgpt` | ChatGPT GPT-5.5 | OpenRouter API | `openai/gpt-5.5` |
| `ds` | DeepSeek V4 Pro | DeepSeek direct API | `deepseek-v4-pro` |

Example: `cx ge cc2` = confer with all three on current task. Updated 2026-05-10 (panel rotation: 4.6→4.7, 5.4→5.5, R1-0528→V4 Pro, Gemini route Google direct→OpenRouter).

## Local Tool Constraint Box

CC1 (this instance) and all CC2 sub-agents operate within a defined tool envelope.
The tool output IS the evidence. LLM reasoning selects and interprets tool output — it does not substitute for it.
If the tools cannot verify a claim, the claim is UNVERIFIABLE — escalate, do not guess.

### STEM / Mathematical Tools (Python)

| Tool | Import | Use When |
|------|--------|----------|
| SymPy 1.14.0 | `import sympy` | Algebraic manipulation, symbolic calculus, equation solving, simplification, limit/series analysis. **Default for any mathematical claim.** |
| z3 4.16.0 | `import z3` | Constraint satisfaction, formal verification, SAT/SMT problems, logical entailment, bound checking. **Default for logical/constraint claims.** |
| NumPy 2.0.2 | `import numpy` | Numerical arrays, linear algebra, FFT, random sampling, vectorised arithmetic. |
| SciPy 1.13.1 | `import scipy` | Optimisation, integration, interpolation, signal processing, statistical tests (scipy.stats). |
| statsmodels 0.14.6 | `import statsmodels` | Regression diagnostics, hypothesis tests, time series (ARIMA, ADF), GLM, survival analysis. |
| mpmath 1.3.0 | `import mpmath` | Arbitrary-precision arithmetic, special functions, numerical verification of symbolic results. |
| uncertainties 3.2.3 | `import uncertainties` | Error propagation, measurement uncertainty, automatic partial derivatives. |
| pint 0.25.3 | `import pint` | Dimensional analysis, unit conversion, quantity arithmetic with units. **Default for dimensional consistency checks.** |
| astropy 7.2.0 | `import astropy` | Physical/astronomical constants, unit conversion, coordinate transforms. Use for constant verification and SI/CGS conversion. |
| PuLP 3.3.0 | `import pulp` | Linear programming, integer programming, constraint optimisation modelling. |
| pandas 2.3.3 | `import pandas` | Data frames, time series aggregation, pivot tables, merge/join operations. |
| Wolfram (MCP) | `mcp__Wolfram__*` | WolframAlpha (natural language queries), WolframLanguageEvaluator (Wolfram Language code), WolframContext (knowledge base). Use for cross-validation of SymPy results, specialised knowledge queries, or when Wolfram Language is more natural than Python. |

### Code Analysis Tools (Python)

| Tool | Invocation | Use When |
|------|-----------|----------|
| AST (stdlib) | `import ast` | Parse Python source, inspect structure, detect dead code, trace call graphs, verify imports. **Default for structural code claims.** |
| pytest 8.4.2 | `python3 -m pytest` | Run test suites, verify fixes don't break existing tests. |
| ruff 0.15.9 | `python3 -m ruff check` | Fast linting — unused imports, style violations, potential bugs. |
| mypy 1.19.1 | `python3 -m mypy` | Static type checking — signature mismatches, type errors, unreachable code. |
| bandit 1.8.6 | `python3 -m bandit` | Security-focused static analysis — injection, hardcoded secrets, unsafe deserialization. |
| dis (stdlib) | `import dis` | Bytecode disassembly — verify control flow, optimisation claims, dead branches. |
| inspect (stdlib) | `import inspect` | Live object introspection — verify signatures, source locations, inheritance. |
| difflib (stdlib) | `import difflib` | Structural diff — verify claimed code changes, detect semantic duplicates. |
| crosshair 0.0.102 | `import crosshair` / `crosshair check` | Symbolic execution via z3 — counterexamples for type/contract/assert violations in Python functions. **Default for behavioural code claims** (function contract or invariant verification). |

### Claude Code Native Tools

Bash, Read, Write, Edit, Grep, Glob, WebFetch, WebSearch — full STEM tool access.
CC1 permissions: `.claude/settings.json` auto-approves all native + MCP tools.
CC2 permissions: `--allowedTools Bash Read Write Edit Grep Glob WebFetch WebSearch` in CLI dispatch.
Both instances have unrestricted access to all tools for STEM research, source inspection, and modification.

### When to Use What

- **Mathematical claim** → SymPy first, z3 if constraint/logic, Wolfram to cross-validate
- **Statistical claim** → scipy.stats or statsmodels, NumPy for computation, pandas for data
- **Code correctness claim** → AST parse + Read source + pytest run
- **Code quality claim** → ruff + mypy + bandit
- **Behavioural code claim** (function invariant / contract) → crosshair (symbolic execution via z3)
- **Logical/constraint claim** → z3
- **Measurement/uncertainty claim** → uncertainties + mpmath for precision
- **Dimensional/unit claim** → pint (default) or astropy.units for astronomy
- **Optimisation/LP claim** → PuLP
- **Stoichiometry claim** → regex + collections (no external dep), or pint for unit-bearing balances
- **Any claim** → if tools can verify it, tools MUST verify it before verdict

### Additional Tools Installed (Tranche B, 14 April 2026)

Wired into B-Cell specialist dispatch via `bench/cdsfl_registry/tool_manifest.toml`:

| Tool | Import | Use When |
|------|--------|----------|
| rdkit 2026.3.1 | `from rdkit import Chem` | SMILES parsing, molecule validation, chemistry structure claims. **Default for chemical structure claims.** |
| biopython 1.87 | `from Bio import SeqIO` | DNA/RNA/protein sequence validation, basic sequence analysis. **Default for biological sequence claims.** |
| scikit-learn 1.8.0 | `import sklearn` | ML metric/model claims, baseline classification/regression verification. **Default for ML claims.** |
| networkx 3.6.1 | `import networkx` | Graph theoretic claims, shortest paths, connectivity, graph property checks. **Default for graph claims.** |
| crosshair 0.0.102 | `import crosshair` | Symbolic execution (also listed in Code Analysis table above). |
| matplotlib 3.10.8 | `import matplotlib` | Plotting (installed, not yet routed into any cell). |

### Wolfram: a failed call is NOT a result (2026-08-02)

**The failure mode.** The Wolfram MCP bridge returns every failure path — auth
rejection, timeout, gateway error, network fault — as a *successful* tool result
whose text happens to be an error string. `[HTTP Error 401]` arrives looking
exactly like an answer. Nothing in the transport distinguishes them.

**Why this matters here specifically.** This project has already lost a
convergence to this precise shape: a verdict reader matched `NOT FALSIFIED` as
though it contained `FALSIFIED`. A failure that does not look like a failure is
the most expensive kind of defect this harness can carry, because every
downstream stage treats it as evidence.

**The rule, which is not new — it is the tool constraint box applied.** The box
already states: *if the tools cannot verify a claim, the claim is UNVERIFIABLE —
escalate, do not guess.* A Wolfram call that errored did not verify anything.
So:

  1. A Wolfram result whose text begins with `[HTTP Error`, `[Timeout after`,
     `[Error]`, or which contains no `Out[` line, is **NOT EVIDENCE**. It is a
     failed measurement.
  2. It must never be recorded as confirming or refuting a claim. The claim
     returns to UNVERIFIED and, if it matters, escalates.
  3. Retry once before concluding anything — a transient gateway error is not a
     statement about the mathematics.
  4. Never quote a Wolfram output in a note, commit message or finding without
     having seen an `Out[` line in it.

**Preventing rather than detecting.** The largest single cause of this class was
an expiring credential, and that cause is removed at source by moving off the
key-authenticated bridge — there is no key left to expire. What remains
(gateway timeout, service outage) cannot be prevented from this side; those must
be *loud*, not *guarded*.

**Known ceiling.** The free hosted endpoint (`agenttools.wolfram.com/mcp`) is
byte-identical to the paid bridge on every computation tested, but it is
STATELESS (definitions do not survive between calls — put the whole computation
in one call) and it has a hard gateway ceiling at **~30 s wall-clock, ≈26 s of
compute** net of round-trip. My first bracket (24–40 s, from `Pause[20]` OK at
23.8 s and `Pause[40]` → 504) was correct but loose; measured 504s land at
30.45 s and 30.47 s with a success at 28.14 s. Plan against 26 s, not 40.

**The ceiling is capability-inverted, which is the point.** It does not remove a
random slice of Wolfram's usefulness — it removes the slice that justified using
Wolfram at all. Wolfram earns its place by closing what SymPy leaves unevaluated,
and hard closed-form integrals, symbolic distribution algebra and Groebner
elimination are exactly the operations that exceed 26 s. Measured base rate
across six log-trig definite integrals: two outright 504s, one near-miss at
28.14 s. Two textbook problems that 504'd both have closed forms, and one — the
CDF of a sum of exponential + uniform + normal — is squarely in Exp 45's
`domain=statistics` scope. The WolframAlpha tool answers the same integral in
5.66 s but returns a bare float (−6.04188), which mpmath and scipy already give
locally for free.

**`$LicenseType` is NOT ours — correction 2026-08-02.** The `"Professional"`
reported by both endpoints describes **Wolfram's hosted server's** licence. It is
not a right this project holds and must never be quoted as one, nor carried across
to any locally installed kernel.

**Attribution is mandatory, not courtesy.** Wolfram|Alpha's terms require
attribution wherever results reach a document, and state that failure may
constitute academic plagiarism. Any Wolfram-derived value in a note, finding,
commit message or paper carries an explicit attribution to Wolfram Language or
Wolfram|Alpha. Their terms do permit use of results in academic/non-commercial
publications, so this obligation is cheap and it is not optional.

**Wolfram stays OUT of the automated pipeline — now a licence constraint, not
only a design preference.** Wolfram's general Terms of Use (effective
2024-07-29), which the Engine terms inherit by reference and which govern the
hosted endpoints by their own scope clause, bar systematically extracting results
into a new data table or AI system and state the Services *"should not be used in
conjunction with your AI-powered tools or services"* absent a separate agreement.
Wolfram|Alpha's terms separately forbid repeated scripted access. Assistant-side
interactive cross-checking — the current arrangement — is defensible, and Wolfram
publishes a `for-agents.md` naming Claude Code, which a prohibition cannot
sensibly forbid. An automated in-pipeline fallback called by dispatched agents at
experiment scale is **not** defensible on the published terms. Under
`p-pass-ambiguity-default` this is HARD until Wolfram answers in writing.

**HOW WOLFRAM IS WIRED (settled 2026-08-02 22:15 after a failed restart).**
Two routes, and the split is forced by a measured constraint, not preference:

  * **`WolframCloud` MCP server** — `npx -y mcp-remote https://agenttools.wolfram.com/mcp`.
    Claude Desktop REJECTS a bare `{"url": ...}` ("not valid MCP server configurations
    and were skipped"); the stdio shim is the supported form and is verified working.
    No credential. Use for ordinary cross-verification.
  * **Local Wolfram Engine via `wolframscript` in Bash, ON DEMAND** — NOT as an MCP
    server. Use when a computation needs more than ~26 s or needs session state.

**Why the Engine is deliberately NOT an MCP server.** The free Engine is effectively
single-kernel. `InstallMCPServer` wrote it into the config, and on restart Claude
Desktop spawned **two** kernels against that one licence. They contended, and every
kernel request then failed — including plain `wolframscript` — with *"not activated or
experiencing a license-related problem"*, which reads like an activation fault and is
not one. Measured separately the same day: 3 concurrent `wolframscript` calls → 1 OK,
2 "Connection closed by WolframKernel". An always-on MCP server plus the `ag` parallel-
agent pattern cannot share one kernel. On demand from Bash, there is no contention.

If `wolframscript` ever reports a licence problem, check `ps` for `MacOS/wolfram -run`
processes FIRST — a stale MCP-spawned kernel is the likely cause, not the licence.
`$LicenseExpirationDate` is **2026-09-11**; renew before then.

**Superseded 2026-08-02: the Engine IS installed, on the founder's ruling.** The
licence caution below is retained as the reasoning, not as current advice. Its
FAQ excludes use *"for the express purpose of producing output (e.g. papers or
reports)"* for commercial or organisational use, and neither term is defined.
This project publishes. It also adds an audit clause (10 business days) that the
hosted endpoints do not carry, and it *relocates* rather than removes the
substrate dependency: "no third party will have the founder's bridge" becomes
"no third party will have the founder's Wolfram ID and activated kernel". The
credential-free hosted endpoint is the correct default for the released harness.

### What Is NOT Installed (do not attempt)

pylint, radon, vulture, pyflakes. If a domain needs these, flag it and request
installation. Always verify with `pip show <pkg>` before assuming installation
state — this line is the source of truth at sv time, but `pip show` is the
ground truth at run time.

## ★ NEVER LABEL A SIMULATED AGENT WITH A REAL MODEL'S NAME (2026-08-05)

A simulated panel — Claude subagents standing in for the model panel — must be
labelled `SIM-A` … `SIM-E`, or anything else unmistakably not a vendor name.
**Never** `Gemini`, `Codex`, `ChatGPT`, `CC2`, `DeepSeek`.

**Why.** On 2026-08-04 a five-agent simulated bench was labelled with the real
panel's names to mirror its composition, and the results were then reported as
"Gemini built the negative control" and "Gemini's AL-02 finding". No paid dispatch
occurred in that run at all. Worse, the same 24 hours contain a REAL five-model
panel review under the same five names, so the record held two panels a reader
could not tell apart. The founder caught it by asking "at what point were you
speaking to Gemini?" — the honest answer was: never.

This is a provenance failure, and provenance is the property this project
documents as core. A result attributed to a model that never produced it is
indistinguishable, downstream, from a fabricated result.

**Applies to:** agent labels, finding IDs derived from them, log directories,
report fields, notes, TTS and commit messages. When a simulated run is reported,
say so in the same sentence as the result, not in a footnote.

## Identity

CC1 = this instance (UX mode, interactive). CC2 = CLI headless instance.

## Note-Writing Standard

TTS and experimental notes MUST comply with the CDSFL note standard. Current working version: **`cdsfl_note_standard_v1.4.md`** in the CDSFL persistent memory folder, locked 13 August 2026. v1 (21 April), v1.1 (10 May), v1.2 (14 May) and v1.3 (13 August) are preserved for archival continuity. **Read v1.4 before writing any new note.**

**★ THE READER IS THE PROJECT'S DESIGNER, WHO DOES NOT READ CODE.** Not a journalist. v1.2 and v1.3 both set the plain-English target reader as "smart curious non-specialist / educated journalist", and that is the root cause of the vagueness the founder reported three times. The reader KNOWS the convergence gate, gamma, priors, the panel, falsifiers — they designed them, so do not explain them. The reader does NOT know line numbers, file locations, or what changed. **The failure mode is never "too technical"; it is "too vague to identify what is being discussed."** Correct toward specificity, never toward simplicity.

**v1.4 adds Rules 19–23, each from a founder annotation:** (19) Name the subject — never "the mechanism" / "one component"; if it cannot be named the note is not ready. (20) Every fix claim carries an explicit status from PROPOSED / BUILT / TESTED / COMMITTED / ENABLED with its evidence — "it is fixed" is banned, and COMMITTED-but-not-ENABLED is the distinction the founder had to ask for four times. (21) Label every defect OBSERVED (name the run and finding) or HYPOTHESISED (say so, and say what would settle it). (22) Every mechanism carries a worked example with real values. (23) Never invent a noun-phrase to avoid naming an actor — restructure so no actor is needed.

**The 12 rules, summarised.** (1) Numerical date with local timezone on line 2. (2) Summary section names the claim or decision, not the act of filing. (3) Content-driven section headers. (4) Every internal label glossed inline on first use in the **technical** version (in the plain-English version, labels are largely omitted or appear in parentheses as cross-reference only). (5) Greek letters phonetic in TTS, symbolic in markdown. (6) No phonetic path spelling in TTS — name files as nouns with a brief locator. (7) No md5/line-count/byte-identity prose in TTS. (8) Cross-references by note title, not by file path. (9) Third-party neutral voice throughout. (10) Length 60–400 lines TTS, 40–300 lines markdown. (11) Scientific notation: `1×10^N (number-words)` with verified exponent-to-word correspondence; `<digit>E.<digit>` tokens are item references, NOT scientific notation. (12) Substantive technical notes carry **two markdown versions** plus a TTS companion: technical (`<Name>_<DATE>.md`), plain-English (`<Name>_Plain_English_<DATE>.md`), and TTS plain-text (`<Name>_<DATE>.txt`, mirroring the plain-English markdown). Plain-English target register: "smart curious non-specialist" — educated journalist or adjacent-field scientist — not dumbed down; internal labels omitted or parenthesised; narrative over enumeration; metaphor welcome; substance preserved; ~2/3 the length of technical.

**Foot-line convention.** Every compliant note ends with exactly one line as its final content: `Written under CDSFL note standard v1.2 (14 May 2026).` Notes written under earlier versions retain their version-specific foot-lines. A missing foot-line flags a note that predates or violates the standard.

**Canonical failure example.** `experimental_notes/Exp40_to_54_Plan_Section8_Decision_Register_2026-04-21.md` and its TTS companion (21 April 2026, pre-standard) are the reference failure catalogued in the standard file.

**Amendment.** The founder amends this standard. Any change lands as a new version (v1.3 / v2) with a dated lock line; earlier versions preserved for archival continuity.

## Standing Corrections

- PolicyEngine is NOT "the registry"
- MIDCA "6/8 with 2 partial" is OBSOLETE — substrate agnosticism reframes both
- CC2 dispatch is claude_cli, NEVER OpenRouter
- Models are NEVER benched — ITC restarts with fresh context
- Gemini is 3.1 Pro, not 2.5 Pro
- FFAFP (supersedes FFF/FFAF) is a prompt pattern — no enforcement, no rejection
- Findings confirmed programmatically or by HIL — no model voting

## ★ GAMMA IS LOAD-BEARING — DO NOT DEMOTE IT (standing directive, founder-issued 2026-06-10)

**Gamma is the decay curve. The decay curve and diminishing returns are the foundation of the
entire maths model and of the whole project. Gamma is an ACTIVE, central measure of convergence
and has been since almost the project's outset. Do NOT propose demoting it, do NOT make it
"reported only", and do NOT try to persuade the founder to stop relying on it.** This directive
exists because CC1 repeatedly drifted toward demoting gamma over the 2026-06 sessions; the founder
named it a recurring, costly failure mode and asked for a permanent guard. Honour it.

**The correct, agreed design is a TWO-SIDED GATE.** Convergence requires BOTH sides of the same
diminishing-returns coin to agree, neither alone:
1. `gamma_critical >= gamma_alt_threshold` (default 0.30, conservative because the whole-history
   Duane slope saturates below 1.0 — a high cutoff would be unreachable) — the decay curve has
   flattened; AND
2. K consecutive zero-new-critical rounds (default 3) — the strict, threshold-free "insurance"
   endpoint of that same curve.
Implemented in `_check_gamma_alt_convergence` (`reference_runner_v2.py`); tests in
`bench/tests/test_two_sided_gate.py`. On the 9 June live Exp 42 run BOTH held first at round 6
(gamma_critical 0.607 >= 0.30, count [0,0,0]) — confirming the two naturally agree.

**If convergence ever seems out of reach, the cause is MECHANICAL, not the model.** No real
problem space has infinite solutions; diminishing returns is basic, near-irrefutable common sense.
The maths model has never been shown wrong. The faults have always been implementation. Treat the
model as the fixed point and hunt the mechanics first, by default. Never argue the model/gamma is
wrong when something fails — that is the wrong instinct, vindicated as wrong every time.
