# Three questions. The founder requires a SINGLE converged answer to Q1.

You are one of three reviewers: CC1 (the assistant that ran the build experiment),
CC2, and Fable. All three of you are free on the Max plan; no metered cost is
involved, so take the time to be right.

**A note on convergence.** This project RETIRED compelled convergence for panel
reviews on 2026-08-12, because the one model that accepted a false premise gave the
worst answer and forcing agreement would have buried that. **The founder has
explicitly overridden that default for Q1 only**: "You must converge on a singular
solution." So on Q1, converge. On Q2 and Q3, disagreement is still information and
should be preserved.

---

## Q1. Three writers attempted the same fix at three different sites. Which is right?

**The defect.** `_apply_routing` (`bench/reference_runner_v2.py:3279`) routes a
finding to progressively stronger writers and escalates to a human only when the
strongest cannot resolve it. It fires on `escalated=True AND not CONFIRMED`. A
falsifier that **fails the discrimination control is CONFIRMED** — it fired — so
such a finding never reaches the ladder at all.

**Three attempts, all of which APPLIED cleanly and then failed to make their own
test pass.** They did not converge on an approach:

| writer | size | runner hunks | anchored on |
|---|---|---|---|
| Codex | 3.4k | 2 | the `confirmed = [...]` candidate list inside `_apply_routing` |
| CC2 | 19.5k | 4 | `DISC_INDETERMINATE = frozenset({...})` — the outcome taxonomy at `:2176` |
| Fable | 13.1k | 1 | the existing `# FIX 2 (Exp 43, 2026-07-22)` ERROR-routing block at `:3362` |

The full responses are at `bench/logs/build_experiment_2026-08-22/T01_rung{1,2,3}_response.md`.
Read them.

**CC1's position, offered so you can attack it:** Fable's site is right. The
ERROR-routing block already exists, already routes ONCE to a stronger writer
regardless of severity, and already carries an `error_routed` flag to stop a
sub-critical consuming the ladder round after round. `NON_DISCRIMINATING` is the
same class of thing as `ERROR` — a broken INSTRUMENT, not a refuted claim — so it
belongs in that admission rather than in a new path. The quarantined direct-write
from the same run independently reached the same site, with the comment
"NON_DISCRIMINATING joins ERROR".

**CC1 also holds that three failures at three different sites is evidence the BRIEF
was under-specified, not that the task is hard.** Attack that too if you disagree.

**What Q1 needs from you:** one site, one approach, and the reason. Then say what
the test must assert so that it FAILS at the parent and PASSES with the patch.

---

## Q2. Are the accepted fixes mutually exclusive, or merely sequentially conflicting?

The composition check found that six of eight accepted patches apply together and
**T04 and T05 conflict** — their SEARCH blocks stop matching once T02 and T03 land.

CC1 measured which line regions of `reference_runner_v2.py` each patch touches:

```
T02  1 or 5 hunks at   2133, 2165, 2298, 2618, 2624, 9127
T03  8 hunks at        2938, 2971, 2984, 2990, 8143, 8393, 9131, 10345
T04  5 hunks at         195, 1144, 2980/2983, 3036, 3362
T05 14 hunks at         195, 1113, 1142, 1163, 1823 ... 10345
```

**CC1's position:** these are SEQUENTIALLY CONFLICTING, not EXCLUSIVE. T03 adds a
ledger write on REFUTED inside `apply_falsifier_verdicts`; T04 changes what
ERROR/UNTOOLABLE may write in the same function; T05 adds status values and touches
registry entry creation. They are complementary designs editing adjacent lines, so
they need REBASING IN A CHOSEN ORDER rather than a choice between them.

**EXCLUSIVE would mean two patches cannot both be true** — incompatible designs for
the same decision. Check whether any pair is actually that. Name the safe order if
they are not.

---

## Q3. How should the schema treat SIMPLICITY and SUFFICIENCY?

The founder asks whether this was ever decided. CC1 ran `rg` over the anchors and
the answer appears to be **no — not for the schema.**

What EXISTS, and all of it governs how the ASSISTANT works, not how CDSFL
adjudicates:

- `simplicity-default` in the global directives: *"Default to the simplest
  sufficient solution."*
- FFAFP step 4, in `docs/GLOSSARY.md:126`: *"Fix with the simplest sufficient
  correction addressing root cause and downstream consequences."*
- The project's stopping criterion (persistent memory, `feedback_stop_criterion`):
  *"Stop iterating when the bench produces meaningful results without wasted
  compute... Occam's razor... Would this failure waste bench compute? If no, defer
  it."*
- A worked instance (`feedback_simplest_sufficient`): CC1 tested five candidate
  splitters for a hard question and all five were refuted; the founder asked
  whether an EXISTING sweep could just handle it, and it could — the blocker was
  one entry in one set. The lesson recorded was: *"when several attempts at a
  solution all fail, treat that as evidence the problem may be mis-framed, not as
  licence to escalate to a heavier tool."*

What does NOT exist: any treatment in `docs/MATHEMATICAL_APPENDIX.md`,
`docs/cdsfl_topology_formal.md`, or the glossary of how the SCHEMA should weigh
simplicity against sufficiency when adjudicating a finding or a proposed fix.

**The founder's framing, which should be preserved rather than collapsed:**
sufficiency and simplicity *"are not the same quantities, although they remain two
sides to the same coin."*

**What Q3 needs from you:** should the schema treat these formally at all, and if
so how — a status, a scoring term, a gate condition, an admissibility rule, or
nothing? Say plainly if your answer is "leave it as an operating directive and do
NOT put it in the schema", and why. Note that this project already refuses to add
machinery whose absence would not waste bench compute.

---

Do not pad. Every word is read, so make every word carry weight. You have Bash, Read,
Grep and Glob — the repository is at
`/Users/georgejackson/Developer_Projects/Constraint_Engineering`. Read the actual
files before answering. You are READ ONLY: report, do not modify.
