# Interaction Shortcuts

These are single-token commands used by the founder to steer AI reasoning
during sessions. They control not what the tool does, but how it thinks
about the problem — selecting cognitive modes (falsify, extrapolate, analyse)
rather than mechanical operations (compile, test, deploy).

Commands are separated by a single space when composed. For example,
`p d e` means: falsify, then discuss, then extrapolate. Composition is
left-to-right. As these functions grow, they may evolve beyond single
letters into whole words or composed expressions.

The canonical and authoritative reference for metacognitive commands is
`.claude/CLAUDE.md` (project-level directives) and
`docs/REPRODUCING.md` § Metacognitive Commands. This document is a
reader-facing summary; it must remain aligned with those files.

---

## Core Commands

| Command | Meaning |
|---------|---------|
| `y` | Yes / approved |
| `cy` | Continue the work AND apply live-experiment monitoring discipline (standing directive 2026-05-18): while any experiment or process runs, monitor it about every 60 s; on anything screwy or off, pause it, FFAFP it (analyse with all available tools), apply the fix, then resume; always keep a terminal window open tailing the running experiment's full current output for the founder. Not bare "continue". |
| `d` | Discuss before proceeding |
| `p` | P-pass — Popperian falsification (iterative: identify, fix, falsify the fix, repeat until diminishing returns) |
| `a` | Analyse dispassionately |
| `e` | Extrapolate — project implications beyond the immediate domain |
| `f` | Find, Follow, Analyse (with available tools), Fix, P-pass — five-step intra-model reasoning cycle |
| `sth` | Synthesise — consolidate findings into a coherent whole |
| `sy` | Use all available mathematical and STEM tools (SymPy, z3, SciPy, NumPy, uncertainties, mpmath, Wolfram when available) in analysis |
| `t` | Send output to TTS file |
| `r` | Re-read key context files (quick check) |
| `rt` | Read all recovery resources + continue |
| `rs` | Recover state — run `scripts/cdsfl_recover.py --full`, then rebuild full working context from session-context + action queue + checkpoints + memory + recovery resources |
| `rg` | Regain full context on a named topic — re-read anchoring memory files, canonical docs, and experimental notes before producing new output; name the resources consulted in a one-line preamble |
| `sq` | Sequential — strictly one tool call at a time, no parallel batches, to avoid stressing Anthropic servers during long autonomous runs; sub-agents inherit the same constraint |
| `sv` | Save state — run `scripts/cdsfl_sv.py`, update recovery docs, commit and push |
| `qc` | Quality control — run `scripts/cdsfl_qc.py` and fix reported issues |
| `re` | External research (web search, arXiv, Semantic Scholar) |
| `ext` | External research — shorter alias for `re` |
| `x` | Override sleep/rest warnings for current session |
| `pr` | Panel review — dispatch the full model panel (`cc2`, `cx`, `ge`, `cgpt`, `ds`; CX2/Codex-CLI optional 6th) on a completed analysis or design question under `sy sth f e d t`. NO compelled convergence: each model returns an independent verdict plus its strongest falsification, and disagreement is preserved as information rather than smoothed to consensus. CC1 participates with its own position and synthesises the range. Mirror to TTS. |

## Model Confer Dispatch (combinable)

| Command | Target | Route |
|---------|--------|-------|
| `c` | Any / current default | Mutual P-passes until convergence or diminishing returns |
| `cc2` | Claude Opus 4.7 | CLI piped mode (`claude -p`), Max subscription — identifier `opus` |
| `cx` | Codex GPT-5.5 | OpenRouter API — `openai/gpt-5.5` |
| `ge` | Gemini 3.1 Pro Preview | OpenRouter API — `google/gemini-3.1-pro-preview` (moved off the Google GenAI API on 2026-05-10) |
| `cgpt` | ChatGPT GPT-5.5 | OpenRouter API — `openai/gpt-5.5` |
| `ds` | DeepSeek V4 Pro | DeepSeek direct API — `deepseek-v4-pro` (never OpenRouter) |
| `ag` | — | Use agents (parallelise independent tasks via Agent tool, e.g. parallel confer dispatch) |

Panel composition current as of 2026-05-10 and smoke-tested on that date. `cx` and
`cgpt` share the `openai/gpt-5.5` identifier — they are the same underlying model
reached under two different confer roles, not a transcription error.

Confer dispatches are combinable — `cx ge cc2` dispatches to all three in parallel. Prefix with `ag` to parallelise.

## Composition Examples

| Input | Effect |
|-------|--------|
| `p d e` | Falsify, then discuss findings, then extrapolate implications |
| `c p a d` | Confer with models, P-pass, analyse, discuss |
| `rs qc` | Restore full state, then run quality control |
| `p d` | Falsify, then discuss before proceeding |
| `rg a d` | Regain context on the named topic, analyse dispassionately, discuss before proceeding |
| `rg p` | Regain context, then P-pass what has been drafted |
| `ag cx ge cc2` | Parallel confer across Codex, Gemini, and Claude Opus 4.7 |
| `f sy` | Five-step FFAFP cycle using all available STEM tools |
