# Reproducing CDSFL Experiments

Step-by-step guide for replicating experiments. Read GLOSSARY.md and
ARCHITECTURE.md first if you are new to the project.

---

> **Working directives.** The rules governing how claims are made, checked, withdrawn and written
> down under CDSFL are in [WORKING_DIRECTIVES.md](WORKING_DIRECTIVES.md). They were in force throughout
> the experimental record, so a run cannot be fully understood without them. This document covers how to
> RUN an experiment; that one covers how the work is conducted.

## Prerequisites

### Python

Python 3.13 or later. Check with:

```bash
python3 --version
```

If not installed, use `brew install python@3.13` or `pyenv install 3.13`.

### Dependencies

The maintained dependency list is the table inside `scripts/cdsfl_onboard.py`
(`CORE_PACKAGES`, `CODE_QUALITY_PACKAGES`, `STEM_PACKAGES`). `bench/requirements.txt`
is a three-line partial dated 12 March 2026 and does **not** cover the suite — it
omits `pytest`, among others, so installing from it alone leaves you unable to run
the verification step below.

Install the full set:

```bash
pip install anthropic openai scipy numpy sympy pytest google-genai statsmodels \
            pydantic httpx cryptography z3-solver uncertainties mpmath \
            mypy ruff bandit coverage
```

Then let the wizard tell you what is still missing — it checks each package by
importing it, so its answer is measured rather than declared:

```bash
python3 scripts/cdsfl_onboard.py
```

> **[Correction 2026-08-07.]** This section previously said `pip install -r
> bench/requirements.txt` followed by five extra packages, a union of eight. That
> union cannot reach the "Verify Setup" step immediately below it, because `pytest`
> is in neither list. The package names above were taken from `scripts/cdsfl_onboard.py`
> and each was confirmed importable on the reference machine; `bench/requirements.txt`
> itself has not been regenerated and is left for the founder to rule on.

### API Keys

Create a `.env` file in the repository root (never commit this file):

```
OPENROUTER_API_KEY=your_key_here   # Required: Codex, ChatGPT AND Gemini panel routes
DEEPSEEK_API_KEY=your_key_here     # Required: DeepSeek V4 Pro via the direct DeepSeek API
GEMINI_API_KEY=your_key_here       # Optional: legacy direct-Google fallback only
```

`GEMINI_API_KEY` is **optional**, not required. The panel has routed Gemini through
OpenRouter since 2026-05-10; the direct Google SDK is retained only as the secondary
route (`bench/experiment_11_orchestrator.py:166-177` — primary `api="openrouter"`,
`secondary_api="google"`). `scripts/cdsfl_onboard.py` marks it Optional and is the
list of record.

`.env` is read by the launcher itself (`bench/launcher_core.py:53`, which also strips
an `export ` prefix). No `source` step is required before a run.

**Wolfram needs no key**, and never did need one to reproduce a run. Wolfram retired
the paid MCP Service and previously generated keys stopped functioning after
2026-07-31. Where a cross-check is wanted, use either the free hosted MCP server
(`npx -y mcp-remote https://agenttools.wolfram.com/mcp`) or a local Wolfram Engine
under its free licence, called via `wolframscript`. Wolfram is a cross-verification
tool only; no experiment depends on it.

CC2 (Claude) requires the Claude Code CLI installed with an active Max subscription.
The CLI binary is discovered automatically from the macOS app bundle.

### Verify Setup

Run the onboarding script to check everything:

```bash
python3 scripts/cdsfl_onboard.py
```

Run the test suite to verify the codebase:

```bash
python3 -m pytest bench/tests/ -q
```

All tests should pass. If any fail, check the error messages for missing
dependencies or environment issues.

**The suite is offline by default.** `bench/tests/conftest.py` sets `HF_HUB_OFFLINE`,
gates `immune_agents._get_claude_cli()` through `bench/live_dispatch_policy.py`, and
guards sockets and subprocesses. No test run costs you model time. Add
`--netguard-strict` to fail any test that merely *attempts* an outbound call:

```bash
python3 -m pytest bench/tests/ -q --netguard-strict
```

To exercise the live model path deliberately — and only then — opt in explicitly:

```bash
CDSFL_ALLOW_LIVE_DISPATCH=1 python3 -m pytest bench/tests/
```

> **Warning for anyone reproducing from a build that predates 31 July 2026.**
> On those builds the plain `pytest bench/tests/` command above dispatched roughly 93
> live claude-CLI calls, serialised under a 15-second timeout — up to about 23 minutes
> of billed model time — with nothing in the output to say so. On a machine without the
> Claude CLI installed it instead took a silently different code path, because
> `_active_llm_classify` fails open at `bench/immune_agents.py:5021-5022`. Neither
> outcome was announced. The `network` marker did not protect you: it was applied to 3
> tests out of about 2089, and `-m "not network"` was never an offline selection. Any
> figure in this repository's history labelled "non-network" and dated before
> 2026-07-31 was produced by a hand-curated file-exclusion list and included live
> dispatch. Treat those as historical records, not as reproducibility evidence.

A test count on its own is not a reproducibility claim. When you record one, record the
date, the commit, and the exact command that produced it — and say whether it is a
collection count or a pass count. See `docs/CURRENT_STATE.md` for the current figures in
that form.

---

## Running an Experiment

### 1. Choose an Experiment

Experiments 42 onward — every result the project currently leads with — run on a
single shared launcher, `bench/launch_exp42.py`, driving `bench/reference_runner_v2.py`
(9,097 lines). **The launcher's name is historical; it is not specific to Experiment
42.** Each experiment is selected by its committed config file.

| Experiment | Config | Target | Reproducible from a fresh clone? |
|---|---|---|---|
| Exp 42 | `bench/exp42_configs/42_composer_locationkey_live.json` | `bench/cdsfl_registry/composer.py` | yes |
| Exp 43 | `bench/exp43_configs/43_macrophage_locationkey_live.json` | `bench/macrophage_cell.py` | yes |
| Exp 44 | `bench/exp44_configs/44_evidence_locationkey_live.json` | `bench/evidence.py` | yes |
| Exp 45 | `bench/exp45_configs/45_memory_statistics_live.json` | `bench/dm/_memory.py` | yes |
| **Exp 46 (reference run)** | `bench/exp46_configs/46_stage6_locationkey_live.json` | `bench/dm/_shadow_stage6.py` | **yes — start here** |
| Exp 47 | `bench/exp47_configs/47_divergence_locationkey_live.json` | `bench/dm/_divergence.py` | yes |
| Exp 48–53 | `bench/exp48_configs/` … `bench/exp53_configs/` | withheld exam articles | **no** — see `bench/cdsfl_registry/targets/MANIFEST.md` |
| **Exp 55 (the v3 control)** | `bench/exp55_configs/55_v3_control.json` | `bench/cdsfl_registry/targets/control_two_distinct_defects.md` | **yes — and its ground truth is known by construction** |

Every config above was parsed and its `test_article` resolved on 2026-08-07: Exp 42–47
target files inside this repository and all six are present. Exp 48–53 target absolute
paths outside the repository, under a directory that is deliberately not distributed.

**Exp 55 is the odd one out and the useful one.** It is the first run of the v3
runner, on a document generated so that its correctness is a property of the
generator rather than of adjudication — two genuinely distinct defects that a
single plausible edit could appear to cure. Both were verified symbolically with
SymPy before the run rather than taken on the generator's word. Its answer key
lives in `control_two_distinct_defects_KEY.md` and is never staged: the key was
originally section 3 of the target itself, inside the file the runner reads whole
and places in the panel prompt, and was split out on 2026-08-23 before anything
ran. Its five predictions are frozen in the config's `_pre_registration`.

The exam articles are released on request under an embargo, to a named custodian with
stated conditions of use — the arrangement controlled-access scientific datasets use.
The terms, and what a request should say, are in
`bench/cdsfl_registry/targets/MANIFEST.md`, alongside the SHA-256 that any result on
one of these articles should be reported against.

> **Contamination warning, 2026-08-08.** Experiments 48, 49 and 53 are **not
> reproducible as held-out results**. Their articles are recoverable in full from the
> committed run records under `bench/logs/`, verified against the hashes those
> articles are published under, and those records are on the public
> `exp39-experimental` branch. Treat the three as demonstrations of the harness, not
> as evidence about unseen material, and see the correction at the head of
> `bench/cdsfl_registry/targets/MANIFEST.md`. Experiments 50, 51 and 52 have not been
> run and their articles remain held out.

Experiments 40–41 also run on runner v2 but through their own launchers,
`bench/launch_exp40.py` and `bench/launch_exp41.py`, with configs under
`bench/exp40_configs/` and `bench/exp41_configs/`. Both implement `--help` and
`--dry-run`.

**Experiments 29–39 are the pre-April-2026 harnesses and are retained as records,
not as the current path.** Exp 29–37 each have a standalone runner
(`bench/run_exp29_persistence.py` … `bench/run_exp37_evidence.py`); Exp 38 launches
from `bench/launch_exp38.sh` and Exp 39 from `bench/launch_exp39.py`, both driving the
frozen `bench/reference_runner.py` (v1, 4,344 lines).

> **Do not probe `bench/run_exp29*.py` … `bench/run_exp37*.py` with `--help`.** None of
> the nine uses `argparse`. Each hand-parses `sys.argv`, recognises only `--resume`,
> `--pattern`, `--topology`, `--relay-mode`, `preflight` and `run`, and **silently
> ignores every other token while leaving the mode at `run`** — so `--help` starts a
> live five-model experiment and bills you for it. Verified by reading
> `bench/run_exp36_evidence.py:3480-3503` and confirming the identical shape in the
> other eight; not verified by execution, deliberately, because executing it is the
> defect. To test connectivity without starting a run, use the word `preflight`:
>
> ```bash
> python3 bench/run_exp36_evidence.py preflight
> ```

### 2. Run

From the repository root. Look before you launch — `--dry-run` costs nothing:

```bash
python3 bench/launch_exp42.py \
    --config bench/exp46_configs/46_stage6_locationkey_live.json --dry-run
```

That prints the target, the five panel seats, the round cap and wall-clock cap,
whether the falsifier gate survived into `RunnerConfig`, and the exact convergence
pass condition. For the config above it reports: target `bench/dm/_shadow_stage6.py`,
models CC2 / Codex / Gemini / DeepSeek / ChatGPT, 16 rounds, 21,600 s,
`falsifier_gate_enabled` True in both the JSON and the `RunnerConfig`.

When the plan is right, drop `--dry-run` to run it live. That dispatches five model
seats and spends real money.

```bash
python3 bench/launch_exp42.py \
    --config bench/exp46_configs/46_stage6_locationkey_live.json
```

`--resume` continues from `checkpoint.json` after an interruption. `.env` is loaded by
the launcher itself, so there is no `source` step.

For long runs, `bench/detached_launch.sh <config> <logfile> [--resume]` wraps the
launcher in `nohup … & disown` and writes a pidfile beside the log, so the runner
survives the terminal. **Note that as committed it `cd`s to the author's absolute
repository path at line 6 — edit that line for your own clone.**

*Verified 2026-08-07: `python3 bench/launch_exp42.py --help` exits 0 with a proper
argparse usage block, and the `--dry-run` command above exits 0 and prints the plan
quoted. The live command was not executed — it requires paid dispatch.*

### 3. Monitor

The runner prints progress to stderr with timestamps. Key things to watch:

- Round number and model dispatch status
- Finding counts per round (raw and novel)
- Immune pipeline results (verified, rejected, escalated)
- CC2v verdicts (from round 6)
- Convergence gate status (per round)
- ITC interventions (restart_fresh, change_focus)
- Gamma estimation (updated per round)

### 4. Results

Each run writes exactly one directory, `bench/logs/<experiment_name>_<UTC timestamp>/`.
The reference run is `bench/logs/exp46_stage6_locationkey_live_20260728T103151Z/`
(90 files), and its contents are the shape to expect:

- `completion_signal.json` — the one-screen summary: status, termination reason,
  round and finding counts, active models, per-model findings, final κ.
  **Read this first.** It is the best entry point to any result in the estate.
- `<experiment_name>_report.json` — the full structured report. Note the filename
  carries the *experiment name*, not `exp{N}`.
- `checkpoint.json` — a single resumable state file. There is **no** per-round
  checkpoint.
- `runner_state.json` — the series the convergence gate reads: `gamma_history`,
  `novel_critical_history`, `gate_history`, `stall_history`, and the registry.
- `round_00.json` … `round_NN.json` — per-round aggregates (zero-padded).
- `r{R}_{model}_{UTCstamp}.json` — the prompt/response record per model per round.
  `round{R}_{model}_{UTCstamp}.json` is a second, differently-shaped record of the
  same exchange (dispatch metadata rather than prompt text); both are kept.
- `macrophage_shadow_r{RR}.json`, `ouroboros_shadow_r{RR}.json` — shadow-cell
  telemetry.

Detached runs write console output to whatever log path was passed to
`bench/detached_launch.sh`. **Nothing is written to `bench/logs/exp{N}_console.log`** —
the only two files of that name, `exp35_console.log` and `exp36_console.log`, are from
the pre-April-2026 harness.

### 5. Analyse

```python
import json, pathlib

run = pathlib.Path("bench/logs/exp46_stage6_locationkey_live_20260728T103151Z")

report = json.loads((run / "exp46_stage6_locationkey_live_report.json").read_text())
signal = json.loads((run / "completion_signal.json").read_text())

print(f"Rounds:             {report['total_rounds']}")
print(f"Findings:           {report['total_findings']}")
print(f"Converged at round: {report['converged_at']}")   # None if it did not
print(f"Reason:             {report['convergence_reason']}")
print(f"Status:             {signal['status']}")

# Two gamma series are recorded and they are NOT interchangeable.
print(f"gamma (all findings): {report['gamma_history'][-1]:.4f}")
print(f"gamma_critical:       {report['gamma_critical_history'][-1]:.4f}")
```

Expected output for that run, executed 2026-08-07: 6 rounds, 48 findings, converged at
round 5, status `CONVERGED`, reason `CRITICAL_QUIESCENCE_CONVERGED (two-sided gate):
gamma_critical=0.336 >= 0.3 … AND 3 consecutive zero-new-critical rounds`, gamma
0.3040, gamma_critical 0.3357.

`gamma_critical` — the Duane decay parameter computed over CRITICAL findings only — is
the input to the two-sided convergence gate. `gamma` (recorded as `gamma_history`) is
the same statistic over all findings and is telemetry; the runner's own reason string
labels it that way. Quoting either under a bare label "Gamma" is ambiguous — always
name the series. The gate is implemented at `bench/reference_runner_v2.py:2833-3035`.

> **[Correction 2026-08-07.]** The snippet in this section previously read
> `report['gamma']` and `report['completion_signal']['status']` against
> `exp36_evidence_20260407T004931Z/exp36_report.json`. Both keys raise `KeyError`
> on any Experiment 42–49 report — reproduced against the Exp 46 report on
> 2026-08-07. `gamma` is not a top-level key (the series are `gamma_history`,
> `gamma_critical_history` and `gamma_all_history`), and the completion signal is a
> separate file rather than a block inside the report. The snippet above was executed
> against the committed run and its output is quoted verbatim.

---

## Experiment Design Principles

1. **One target per experiment.** Each experiment reviews a single file or component. This isolates findings and simplifies analysis.

2. **Neutral framing.** Prompts do not tell models what to find. They describe the target and methodology. Anchoring framing biases model panels (documented confound).

3. **FFF/FFAF is a prompt pattern.** It guides model reasoning but is not enforced or rejected programmatically.

4. **Models are never benched.** ITC restarts models with fresh context on failure. Removing a model from the panel changes experimental conditions.

5. **Findings are confirmed programmatically or by HIL.** No model voting. A finding is CONFIRMED when 2 or more independent models agree, verified computationally where possible.

---

## Cost Estimates

API costs vary by experiment length. Rough estimates for a 20-round experiment:

- OpenRouter (Codex + ChatGPT): varies by model pricing
- Google (Gemini): typically within free tier for research
- DeepSeek: low cost, but chain-of-thought can consume tokens
- CC2 (Claude CLI): included in Max subscription (no API cost)

Total cost per experiment is typically modest. The main cost driver is DeepSeek's chain-of-thought token consumption and extended timeouts.

---

## Metacognitive Commands (MC)

The project uses short commands to direct model behaviour during interactive
sessions with Claude Code or other AI models. These are typed as plain text
in the conversation and can be combined (e.g. `p a e d`).

### Core Commands

| Cmd | Action |
|-----|--------|
| `y` | Yes / approved |
| `cy` | Continue |
| `d` | Discuss before proceeding |
| `p` | P-pass — Popperian falsification (iterative: identify, fix, falsify, repeat until diminishing returns) |
| `a` | Analyse dispassionately |
| `e` | Extrapolate beyond immediate domain (what generalises, boundary conditions, new falsifiable questions) |
| `f` | Find, Follow, Analyse (with available tools), Fix, P-pass (FFAFP five-step cycle) |
| `sy` | Use all available mathematical and STEM tools (SymPy, Wolfram, SciPy, NumPy, z3, uncertainties, mpmath) in analysis |
| `t` | Send output to TTS plain-text file |
| `c` | Confer with another model, run mutual P-passes until convergence |
| `sv` | Save state — update docs, generate CURRENT_STATE.md, commit |
| `qc` | Quality control — run staleness, consistency, and reference checks |
| `rc`/`rs` | Recover state — rebuild full working context from recovery resources |
| `re` | External research (web search, arXiv, Semantic Scholar) |
| `rt` | Read all recovery resources + continue |
| `r` | Re-read key context files |
| `x` | Override sleep/rest-period warnings |
| `sth` | Synthesise — consolidate findings into a coherent whole |
| `rg` | Regain full context on named topic — re-read anchoring memory files, canonical docs, and experimental notes before producing new output. Name the resources consulted. |
| `sq` | Sequential — strictly one tool call at a time, no parallel batches, to avoid stressing Anthropic servers during long autonomous runs. When dispatching sub-agents, the sequential constraint propagates to them. Does not change what work is done, only the rate at which requests are issued. |
| `pr` | Panel review — dispatch the full model panel (cc2, cx, ge, cgpt, ds; CX2/Codex-CLI optional 6th) on a completed analysis or design question under sy, sth, f, e, d, t. Run WITHOUT compelled convergence: each model returns an independent verdict and its strongest falsification, disagreement is preserved as information rather than smoothed to consensus, and CC1 actively participates with its own position and synthesizes the range. Output mirrored to TTS. |

### Model Confer Dispatch

These commands direct the model to confer on the current task with a specific
frontier model from the panel. Combinable: `cx ge cc2` confers with all three.

| Cmd | Model | Route | Identifier |
|-----|-------|-------|---|
| `cc2` | Claude Opus 4.7 | CLI piped mode (`claude -p`), Max subscription | `opus` |
| `cx` | Codex GPT-5.5 | OpenRouter API | `openai/gpt-5.5` |
| `ge` | Gemini 3.1 Pro Preview | OpenRouter API | `google/gemini-3.1-pro-preview` |
| `cgpt` | ChatGPT GPT-5.5 | OpenRouter API | `openai/gpt-5.5` |
| `ds` | DeepSeek V4 Pro | DeepSeek direct API | `deepseek-v4-pro` |

**Note on panel composition.** The `cx` and `cgpt` seats both resolve to
`openai/gpt-5.5` on OpenRouter. Verified in code at
`bench/experiment_11_orchestrator.py:139-164`: `ModelConfig(label="Codex")` and
`ModelConfig(label="ChatGPT")` carry the same `model_id`, the same `api`, the same
`system_prompt_path`, the same `role`, and the same secondary route
(`codex_exec` / `gpt-5.5`). The panel is therefore **five seats over four distinct
model identifiers from four independent vendors**, not five distinct models. The two
OpenAI seats differ by label and by the conversation history each accumulates, not by
weights.

Panel updated 14 May 2026: Claude Opus 4.6→4.7 (Max subscription), GPT-5.4→5.5 for `cx`/`cgpt` (same OpenRouter tier), Gemini route moved Google direct→OpenRouter (same price tier, draws on existing prepaid credits), DeepSeek Reasoner R1-0528→V4 Pro (mandatory; older endpoint retired by DeepSeek). All four upgraded routes were smoke-tested against a known-answer prompt before adoption. The panel is rotated to current frontier on a rolling basis; reproduction should use whichever versions are current at run time, smoke-tested per route.

All models run under CDSFL directives as system prompt. See
`bench/directives/universal/cdsfl_core_formal.md` for the directive text and
`bench/cdsfl_registry/composer.py` for how directives are composed per model.

### When to Use

- `p` after any substantive claim or code change — falsify before presenting
- `sy` when mathematical claims need computational verification
- `f` before any fix — trace blast radius first, then fix with full knowledge
- `sv` at session milestones — preserves state for recovery
- `qc` before commits — catches stale documentation

Combined examples:
- `p a e d` — P-pass, analyse, extrapolate, then discuss results
- `sy p` — verify with STEM tools, then falsify
- `cx ge cc2` — get three independent model perspectives on current work

---

## Troubleshooting

**Models timing out**: Check API key validity and network connectivity. DeepSeek has 900s timeout for chain-of-thought. Gemini has 300s with httpx timeout.

**Empty responses**: DeepSeek Reasoner exhausts output budget on chain-of-thought. The runner retries with halved max_tokens. If persistent, check the `reasoning_content` field.

**Convergence gate never fires**: Common in early experiments. Check if contested findings are blocking the gate. The stall detector provides a secondary termination mechanism.

**Claude CLI not found**: The runner searches PATH, then macOS app bundle locations. Verify Claude.app is installed and the CLI binary exists at `~/Library/Application Support/Claude/claude-code/*/claude.app/Contents/MacOS/claude`.

**Import errors**: Install the full package set from the Prerequisites section above, then run `python3 scripts/cdsfl_onboard.py` — it imports each package and names the ones still missing. Do not rely on `bench/requirements.txt` alone; it is a three-line partial that omits `pytest`.
