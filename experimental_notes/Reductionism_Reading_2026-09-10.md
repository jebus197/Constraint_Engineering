# The reductionism reading, for the deferred references discussion

**Written 2026-09-10. Audience: a reproducing engineer or an adjacent-field scientist.** A plain-English companion for text-to-speech is at `~/Desktop/CDSFL_tts/Reductionism_Reading_2026-09-10.txt`.

## Why this exists

On 2026-09-06 the founder ruled twice on the paper's references section within 69 minutes and deferred the final selection to a discussion, **conditional on both parties having read the sources first**. The reading was delivered in conversation only and never written to a file, so that condition was unmet through no fault of his. This is the reading. Task R10 on the master task list.

## The question

`PAPER.md:528` claims a richer model collapses to a simpler one in a limit. Several philosophical traditions describe that move and they are not interchangeable. The wrong lead citation invites an objection the work does not face and omits the one it does.

## Nagel (1961) — the broad tradition, and the wrong lead citation

Nagelian reduction derives one theory from another **across vocabularies**, via bridge laws connecting the terms of the reduced theory to those of the reducing one; thermodynamics to statistical mechanics, where *temperature* must be bridged to *mean kinetic energy* before the derivation begins.

The reductions here **never leave their vocabulary**. `C(n)`, `F_n`, `D(n)` and `G_n` are written throughout in one language, that of detection probabilities. There is no bridge law to state, so the Nagelian apparatus does no work. Nagel is the honest name for the broad tradition and the wrong reference to lead with.

## Nickles (1973) — the right lead

Nickles identified a second sense in which **the direction inverts**: the richer, later theory reduces *to* the simpler, earlier one in a limit, rather than the simpler being derived from the richer. Special relativity reducing to Newtonian mechanics as `v/c → 0` is the standard case.

That is the shape of these claims exactly. `G_n → F_n` as human coverage goes to 0; `G_n → C(n)` under uniform detection at `K = 1`. Citation: Nickles, T. (1973), *Journal of Philosophy* 70(7):181–201.

## Batterman (2002) — the objection that must be answered

Batterman's work concerns **singular limits**, where behaviour *at* the limit point differs from behaviour approaching it. Where a limit is singular the limiting-case reduction fails, and asserting one without checking is a known error.

So all 4 branches were **executed rather than assumed**, and in every one the value at the point equals the two-sided limit:

| branch | limit | value at the point |
|---|---|---|
| `C_H → 0` | no human passes | `C_M` |
| `rho_MH → 1` | fully primed | `C_M` |
| `C_M → 1` | machine certain | `1` |
| `rho_MH → 0` | independence | `C_H + C_M − C_H·C_M` |

All 4 are **regular** limits. Batterman belongs in the section because the objection is tested and answered, not because the paper makes a Batterman-style claim.

## What executing the claims found, which was not all confirmation

5 reduction claims at `PAPER.md:528` were executed and **2 were refuted**.

1. *"K=1, d=1, uniform p → C(n)"* **omitted the independence condition.** At `rho_MH = 0` the reduction holds and is **stronger** than the paper stated — `G_n = C(n_M + n_H)`, human passes simply add to the machine's count. At `rho_MH = 0.5` with `p = 0.2`, `n_M = 3`, `n_H = 2`, the value **0.58016 is `C(n)` for no integer `n` at all** (Wolfram: `Exists[n in PositiveIntegers, ...]` returns False).
2. *"Every simpler model is a special case of `G_n`"* was **a universal asserted without the enumeration.** Enumerated: `C(n)`, `F_n` and `D(n)` nest. **`R_k(i)` does not** — it carries a pole at `R = 1/q` and a novelty floor `nu`, and the `G_n` kernel is a degree-3 polynomial with neither.

## How to check it

`scripts/verify_paper_reduction_properties.py` — 7 groups of checks, SymPy and mpmath, cross-checked in Wolfram. **Re-run 2026-09-10: every check passes.**

## What the discussion still has to settle

Whether the section leads with **Nickles** as the sense of reduction actually used, cites **Batterman** as the objection tested and answered, and names **Nagel** as the broad tradition this work does not belong to. That is a recommendation, not a decision; the decision is the founder's and was always going to be taken in discussion.

Written under CDSFL note standard v1.7 (26 August 2026).
