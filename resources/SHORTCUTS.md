# Interaction Shortcuts

These are single-token commands used by the founder to steer AI reasoning
during sessions. They control not what the tool does, but how it thinks
about the problem — selecting cognitive modes (falsify, extrapolate, analyse)
rather than mechanical operations (compile, test, deploy).

Commands are separated by a single space when composed. For example,
`p d e` means: falsify, then discuss, then extrapolate. Composition is
left-to-right. As these functions grow, they may evolve beyond single
letters into whole words or composed expressions.

---

## Command Reference

| Command | Meaning |
|---------|---------|
| `y` | Yes / approved |
| `cy` | Continue |
| `rt` | Read context files + continue |
| `d` | Discuss before proceeding |
| `r` | Re-read key context files (IM, checkpoints) |
| `p` | P-pass — Popperian falsification (iterative: identify, fix, falsify the fix, repeat until diminishing returns) |
| `c` | Confer — run P-passes with all available models under CDSFL protocol |
| `a` | Analyse dispassionately |
| `e` | Extrapolate — project implications beyond the immediate domain |
| `rr` | Full recovery — rebuild complete working context from all sources |
| `rs` | Restore state — full recovery from IM + OB + checkpoints + memory |
| `t` | Send to TTS — export to accessible plain-text file |
| `sv` | Save state — Open Brain session summary + update docs + commit + push |
| `re` | External research — web search, arXiv, Semantic Scholar |
| `g` | Confer with Gemini specifically |
| `sy` | Check with SymPy — mathematical verification |
| `x` | Override sleep/rest warnings for current session |
| `qc` | Quality control — full docs/staleness/consistency check and update |

## Composition Examples

| Input | Effect |
|-------|--------|
| `p d e` | Falsify, then discuss findings, then extrapolate implications |
| `c p a d` | Confer with models, P-pass, analyse, discuss |
| `rs qc` | Restore full state, then run quality control |
| `p d` | Falsify, then discuss before proceeding |
