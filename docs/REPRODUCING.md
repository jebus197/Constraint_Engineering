# Reproducing CDSFL Experiments

Step-by-step guide for replicating experiments. Read GLOSSARY.md and
ARCHITECTURE.md first if you are new to the project.

---

## Prerequisites

### Python

Python 3.13 or later. Check with:

```bash
python3 --version
```

If not installed, use `brew install python@3.13` or `pyenv install 3.13`.

### Dependencies

From the repository root:

```bash
pip install -r bench/requirements.txt
```

Additional packages used by specific components:

```bash
pip install sympy z3-solver statsmodels uncertainties google-genai
```

### API Keys

Create a `.env` file in the repository root (never commit this file):

```
OPENROUTER_API_KEY=your_key_here     # Required: Codex + ChatGPT dispatch
GEMINI_API_KEY=your_key_here         # Required: Gemini dispatch
DEEPSEEK_API_KEY=your_key_here       # Required: DeepSeek dispatch
WOLFRAM_API_KEY=your_key_here        # Optional: mathematical verification
```

CC2 (Claude) requires the Claude Code CLI installed with an active Max subscription.
The CLI binary is discovered automatically from the macOS app bundle.

### Verify Setup

Run the onboarding script to check everything:

```bash
python3 scripts/cdsfl_onboard.py
```

Run the test suite to verify the codebase:

```bash
python3 -m pytest bench/tests/ -v
```

All tests should pass. If any fail, check the error messages for missing
dependencies or environment issues.

---

## Running an Experiment

### 1. Choose an Experiment

Each experiment has its own runner script in `bench/`:

| Experiment | Runner | Target | Topology |
|---|---|---|---|
| Exp 29 | `run_exp29_persistence.py` | Persistence layer | Relay |
| Exp 30 | `run_exp30_endocrine.py` | Endocrine layer | Relay (directed) |
| Exp 34 | `run_exp34_endocrine.py` | `endocrine.py` | Star |
| Exp 35 | `run_exp35_policy_engine.py` | PolicyEngine | Star (relay available) |
| Exp 36 | `run_exp36_evidence.py` | `evidence.py` | Star |

### 2. Run

From the repository root:

```bash
python3 bench/run_exp36_evidence.py
```

Most runners accept CLI flags:

```bash
python3 bench/run_exp35_policy_engine.py --topology star
python3 bench/run_exp36_evidence.py --resume  # Resume from checkpoint
```

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

After completion, results appear in:

- `bench/logs/exp{N}_{name}_{timestamp}/` — full logs
  - `exp{N}_report.json` — structured experiment report
  - `completion_signal.json` — termination metadata
  - `round_{R}.json` — per-round data
  - `checkpoint_round_{R}.json` — state checkpoints
- Console log saved to `bench/logs/exp{N}_console.log`

### 5. Analyse

The report JSON contains everything needed for analysis:

```python
import json

with open("bench/logs/exp36_evidence_20260407T004931Z/exp36_report.json") as f:
    report = json.load(f)

print(f"Rounds: {report['total_rounds']}")
print(f"Findings: {report['total_findings']}")
print(f"Gamma: {report['gamma']:.4f}")
print(f"Status: {report['completion_signal']['status']}")
```

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

**Import errors**: Run `pip install -r bench/requirements.txt` and install additional packages listed in the Prerequisites section.
