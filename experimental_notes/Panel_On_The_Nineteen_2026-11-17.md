# The free panel on the 19 decisions — 2026-11-17

2026-11-17, 01:00 GMT

## Summary

All 19 decisions awaiting the founder were put to the 2 free seats **blind**, then to a **joint star round** in which each saw the other's blind answer. 0 paid seats. Rounds: `bench/logs/the_nineteen_2026-11-17` and `..._joint`.

**The headline is not how often the seats agreed.** It is that a seat flagged a stale figure or a falsified premise on **10 of 19** entries, and that **at least 4 of the 19 are not decisions at all** — the work they ask him to rule on is built, wired and passing its guards.

**That is a record-keeping failure of mine, not a panel discovery.** `git log -S` dates each mechanism's first appearance **0 to 10 days after** the entry calling it unbuilt was raised. Producer: `scripts/how_many_of_the_nineteen_were_already_built_2026-11-17.py`.

## How blindness was enforced

| mechanism | evidence |
|---|---|
| recommendation markers stripped | `scripts/build_the_nineteen_panel_brief_2026-11-17.py` refuses to emit if any of 18 markers survives |
| option order destroyed | shuffled under seed 20261117; my pick was option 1 in **17 of 19**, so position alone leaked the answer |
| my position pinned before the round | taken from commit `bb315555` (2026-11-14), 2 days before the request; blob sha256 recorded |
| shuffle reversible and verified | `scripts/did_the_panel_match_me_2026-11-17.py` replays the RNG and **refuses** unless it reproduces the delivered brief byte for byte |
| residual leak, stated | 9 of 58 option texts still name a standard about themselves, 0.155172, Wilson [0.083845, 0.269340] |
| the real limit | seats hold a repo copy containing the decisions file; the brief forbids it by name. cc2 volunteered: *"I read no `Decisions_Awaiting_You_*_GENERATED*` or `Morning_Report_*_GENERATED*` file."* |

## The rounds

| round | seat | chars | tool calls | wall |
|---|---|---|---|---|
| blind | cc2 | 40,517 | 377 | 890 s |
| blind | fable | 20,822 | 37 | 760 s |
| joint | cc2 | 20,275 | 37 | 558 s |
| joint | fable | 15,264 | 25 | 440 s |

fable used the **local Wolfram Engine** as second falsifier, returning 10.6052 and 6.1307, matching cc2's independently derived table. *(Results obtained using Wolfram Language.)*

## Agreement

**12 of 19** — both seats chose my option independently. 0.631579, Wilson [0.410395, 0.808505], Clopper-Pearson [0.383578, 0.837114]. **14 of 19** — at least 1 seat agreed. The seats differed from **each other** on 4 items; the joint round resolved 3.

| | B77 | B84 | B94 | B125 | B141 | B142 | B143 | B154 | B160 | B170 | B171 | B175 | B180 | B182 | B185 | B186 | B190 | B194 | B197 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mine | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| cc2 | own | 1 | 1 | 2 | 1 | own | 1 | 1 | **4** | 1 | own | 3 | 1 | 1 | 1 | 1 | **3** | 1 | **3** |
| fable | 2 | 1 | 1 | own | 1 | 3 | 1 | 1 | **4** | 1 | 1 | 3 | 1 | 1 | 1 | 1 | **3** | 1 | **3** |
| joint | C/H | H/H | H/H | C/H | H/H | C/C | H/H | H/H | H/H | H/H | C/H | H/H | H/H | H/H | H/H | H/C | H/H | H/H | H/H |

## 3 recommendations changed on the panel's argument

- **B197** `qs:633854939cf3` branching point estimate — was *re-scope the guard again*; now **a verified closing pass**. Both seats: a threshold moved whenever it fires measures nothing, and re-scoping twice is the suppression direction the first re-scope distinguished itself from.
- **B190** `pf:d837803feb6a` per-scale critical cuts — was *adopt the disjunction*; now **authorise severity-record stamping first**, disjunction provisional. Stamping is the precondition for measuring the aggregator; the entry says so and my recommendation did not act on it.
- **B160** `pf:055a68c4f4ae` the awaits-you figure — was *leave the test alone*; now **keep it and print the disagreement beside the figure**. It removes nothing the earlier choice keeps and adds the disclosure, so it dominates.

## 4 entries whose premise the live tree falsifies — each verified by my own execution

| entry | the entry claims | the tree says | built |
|---|---|---|---|
| **B77** `pf:4f09b9135a60` | "sat unadopted since 2026-10-07" | `required_quiet_run` at `bench/reference_runner_v3.py:1625`, **called at :10327 and :11640**, both arms; 20 guard tests pass | 2026-11-12, **10 days after** |
| **B142** `pf:970ab5074a95` | "cannot offer the 4 roles" | `known_roles()` returns **7**; `test_the_interface_roles_reach_the_selector_2026-11-14.py` 12 passed | 2026-11-10 |
| **B171** `pf:5292c9025d73` | a bare question wipes the command set | `hooks/work_not_narrate.py:888` already carries `if worked_since and (_new or not _is_bare_question(c))` — **is** the proposed option | 2026-11-12 |
| **B125** `pf:9aa8db33d2a3` | "3 candidate remedies, none built" | `stamp_brief_at_dispatch` defined `:1657`, **called `:1813`** — the brief the seats answered carried its table | 2026-11-12, **8 days after** |

A 5th: **B141** quotes 235 gate files; the live count is **309**.

**4 of 4 checked premises falsified — Wilson [0.510109, 1.000000]. Against all 19: 4 of 19 = 0.210526, Wilson [0.085077, 0.433343].** The sample is **not random** — these are the entries the seats named — so the figure is a floor, not a rate.

## The sharpest criticism was of my option lists

Both seats, independently:

- **3 items offered options against premises the tree had already falsified**, so every option answered a dead question.
- On **B125** the right answer was in neither list: `scripts/panel_brief_validate.py` already runs an **A4 currency check** comparing a brief against post-write file movement. Verified. Both seats answered inside the list; neither list contained the answer.
- cc2: *"a disagreement on the reasoning is where the information is, and this round's scoring could not see it."*

## Why no compelled convergence — demonstrated, not argued

cc2, in the joint round: *"both blind answers were wrong on B77's residual, in opposite ways... Had the panel converged on FABLE's wording, it would have handed him a fail-safe argument pointing at the less conservative value, at exactly the roster sizes (1 and 2) where the gate matters most."*

Agreement would have buried that. fable separately reported that one of cc2's load-bearing facts **failed to reproduce** in its own sandbox, and proposed that a seat reporting a red guard must state what in its environment the guard touches.

## Open, unverified

cc2 claims `stamp_brief_at_dispatch` trusts any stamp table it finds rather than verifying it, and says it has written the check. Not reproduced here; recorded as a seat claim.

Written under CDSFL note standard v1.9 (1 November 2026).
