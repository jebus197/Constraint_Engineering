# CDSFL Project — CC1 Configuration

Repository: `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`
Python: 3.13+ | Tests: `python3 -m pytest bench/tests/ -v`

## Command Scripts

On `sv` (save state): run `python3 scripts/cdsfl_sv.py` then update MEMORY.md and any relevant memory files.
On `qc` (quality control): run `python3 scripts/cdsfl_qc.py` and fix reported issues.
On `rc` or `rs` (recover): run `python3 scripts/cdsfl_recover.py --full` and rebuild context from output.

## Key Documentation

- `docs/GLOSSARY.md` — every term, acronym, Greek letter defined
- `docs/ARCHITECTURE.md` — system components and data flow
- `docs/REPRODUCING.md` — how to replicate experiments
- `docs/CURRENT_STATE.md` — machine-generated state snapshot (produced by sv script)
- `docs/MATHEMATICAL_APPENDIX.md` — mathematical framework (1081 lines)
- `resources/ONBOARDING.md` — full project history and context
- `resources/RECOVERY.md` — pending work and recovery protocol

## Model Confer Dispatch

- `cc2` = Claude Opus 4.6 via CLI piped mode (`claude -p`), Max subscription
- `cx` = Codex GPT-5.4 via OpenRouter API
- `ge` = Gemini 3.1 Pro via Google GenAI API
- `cgpt` = ChatGPT GPT-5.4 via OpenRouter API
- `ds` = DeepSeek Reasoner via DeepSeek API

All models run under latest CDSFL directives as system prompt. Combinable: `cx ge cc2`.
CDSFL directives: `bench/directives/universal/cdsfl_core_formal.md`
Composer: `bench/cdsfl_registry/composer.py`

## Metacognitive Commands (MC)

Single-letter and short commands that direct model behaviour. Combinable
(e.g. `p a e d` = P-pass, analyse, extrapolate, discuss). Full reference:
`docs/REPRODUCING.md` § Metacognitive Commands.

| Cmd | Action |
|-----|--------|
| `y` | Yes / approved |
| `cy` | Continue |
| `d` | Discuss before proceeding |
| `p` | P-pass — Popperian falsification (iterative: identify, fix, falsify, repeat) |
| `a` | Analyse dispassionately |
| `e` | Extrapolate beyond immediate domain |
| `f` | Find-Follow-Fix (FFF intra-model cycle) |
| `sy` | Use all available mathematical and STEM tools (SymPy, Wolfram, SciPy, NumPy, z3, uncertainties, mpmath) in analysis |
| `t` | Send output to TTS file |
| `c` | Confer with another model, mutual P-passes until convergence |
| `sv` | Save state — run `python3 scripts/cdsfl_sv.py`, update recovery docs, commit |
| `qc` | Quality control — run `python3 scripts/cdsfl_qc.py`, fix reported issues |
| `rc`/`rs` | Recover state — run `python3 scripts/cdsfl_recover.py --full`, rebuild context |
| `re` | External research (web search, arXiv, Semantic Scholar) |
| `rt` | Read all recovery resources + continue |
| `r` | Re-read key context files |
| `x` | Override sleep/rest warnings |

### Model Confer Dispatch (combinable)

| Cmd | Model | Route |
|-----|-------|-------|
| `cc2` | Claude Opus 4.6 | CLI piped mode (`claude -p`), Max subscription |
| `cx` | Codex GPT-5.4 | OpenRouter API |
| `ge` | Gemini 3.1 Pro | Google GenAI API |
| `cgpt` | ChatGPT GPT-5.4 | OpenRouter API |
| `ds` | DeepSeek Reasoner | DeepSeek API |

Example: `cx ge cc2` = confer with all three on current task.

## Identity

CC1 = this instance (UX mode, interactive). CC2 = CLI headless instance.

## Standing Corrections

- PolicyEngine is NOT "the registry"
- MIDCA "6/8 with 2 partial" is OBSOLETE — substrate agnosticism reframes both
- CC2 dispatch is claude_cli, NEVER OpenRouter
- Models are NEVER benched — ITC restarts with fresh context
- Gemini is 3.1 Pro, not 2.5 Pro
- FFF/FFAF is a prompt pattern — no enforcement, no rejection
- Findings confirmed programmatically or by HIL — no model voting
