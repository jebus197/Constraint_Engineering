# Where the project stands, after correcting 4 claims the first version of this note got wrong

10 November 2026, 20:58 GMT

## Summary

This note supersedes the state-of-play section of `Panel_Inverted_Meaning_And_The_Three_Rulings_2026-11-10_FULL_RECORD.md`. The founder challenged 4 of its claims and was right on all 4. The corrections come first, because a reader who saw the earlier version needs to know which figures moved. The panel record itself is accurate about the panel and is not withdrawn.

## Correction 1 — the commit cadence was settled and should not have been raised again

His rulings of 2026-11-10: a commit takes as long as it takes, and a commit follows an agreed body of work rather than every fix. Both are written into `~/.claude/CLAUDE.md` as `commit-after-a-batch-not-after-a-fix` and pointed to from `.claude/CLAUDE.md`, **replacing** the sentence *"at natural milestones ... rather than batching large changesets into single sessions"* which said the opposite.

What was raised afterwards was a third, narrower question — whether a save whose staged set is only generated state files must run the 250-file board. It was measured (3 of 5 staged paths are named by gate guards), the measurement refuted the premise, a perturbation test then showed those 3 guards insensitive to those files, and that test was itself too weak to support either answer. **All 3 positions were left on the page at once. The whole thread is withdrawn.**

## Correction 2 — 5 of the 7 "decisions awaiting him" already carry his ruling

| entry | from the 16? | `ruled` | `responded` |
|---|---|---|---|
| B77 — roster-blind convergence window | yes | 2026-11-08 | — |
| B84 — difficulty estimator | yes | 2026-11-08 | — |
| B88 — `_apply_back_gate` fold-back | yes | 2026-11-08 | 2026-11-08 |
| B94 — what `v_bar` counts | yes | 2026-11-08 | 2026-11-08 |
| B125 — joint brief quoting rule | yes | 2026-11-08 | 2026-11-08 |
| B136 — dimensional check reports homogeneity as correctness | **new** | — | — |
| B141 — descriptor rule and 9 unguarded guards | **new** | — | 2026-11-10 |

**5 of 7 come from the 16 and all 5 carry his ruling of 2026-11-08.** Each asks a second thing that ruling did not settle. Presenting them as 7 fresh asks is the N1 defect reappearing inside the report about N1.

## Correction 3 — the termination alarm is a 2-month aggregate

Committed producer `scripts/task_list_burndown_2026-09-11.py`: **R = 0.8828**, 95% interval **[0.7384, 1.0555]**, exact test against the critical value R = 1 at **p = 0.0932**. The point estimate terminates; the interval contains 1, so the aggregate cannot distinguish.

Windowed from the list's own 393 git snapshots:

| window | added | closed | R | verdict |
|---|---|---|---|---|
| last 30 days | 189 | 171 | 1.1053 | cannot distinguish |
| last 14 days | 109 | 116 | 0.9397 | cannot distinguish |
| last 7 days | 40 | 49 | 0.8163 | cannot distinguish |
| **last 3 days** | **11** | **34** | **0.3235** | **TERMINATES**, exact p = 0.000824 |
| last 24 hours | 6 | 6 | 1.0000 | n = 12, uninformative |

**The alarm describes older behaviour.** A recomputation offered during the correction gave R = 1.1004 and is **withdrawn**: it started the window at the empty list, counting the 59 entries present at first population as additions.

## Correction 4 — the figure above 500 was a coverage count

Best identification, offered as such rather than as certainty: **665 test files never run by `hooks/pre-commit`** (B81's entry), now **650** of **900** in `bench/tests/`. A statement about which files the gate watches, not about outstanding tasks. The open-entry count has never exceeded the 59 the list held when first populated.

## Has the master task list terminated? No — 11 open, and the split is what matters

R1's gate is mechanical and the runway names the function: **0 OPEN by `task_list_markers.effective_state()`**. Measured: **11 open**, and `effective_state` agrees with the raw marker on all 11 (0 disagreements).

| whose move | count | entries |
|---|---|---|
| **mine to finish** | 4 | B22 general-purpose calculator · B56 demotion operating point · B104 ticket identifiers in spoken reports · B140 the 2 routing rulings |
| **awaits him** | 7 | B77 · B84 · B88 · B94 · B125 · B136 · B141 |

Share awaiting him: **7 of 11 = 0.636364**, Wilson [0.353801, 0.848335], Clopper-Pearson [0.307905, 0.890737]. Classifier: `scripts/how_many_decisions_actually_need_him_2026-11-01.py`.

## The model-and-role selector backend is NOT done — 3 of 5 of the brief's section 10

Measured by calling the backend against `docs/CDSFL_UX_Design_Brief_AUTHORITATIVE_for_Orchestrator.md` §10:

| requirement | state | evidence |
|---|---|---|
| search across Local / OpenRouter / Peer | built | `catalogue()` returns 6, sources `['registry']` |
| add model from 3 sources | built | `local_models`, `remote_models` present |
| roster carries model, source, role | built | entry fields `has_policy, id, local, source` |
| **4 roles: Orchestrator, Worker, Researcher, Classifier** | **NOT built** | `known_roles()` returns `['collator', 'participant', 'player_manager']` — the harness's internal roles |
| **peer catalogue: vendor+version, count available, instance detail** | **NOT built** | no peer function in `bench/model_catalogue.py` |

**The role gap is the one that blocks the UX**: the selector cannot offer the roles the interface specifies.

## The step-count question

The exchange cannot be located in the record and no explanation is invented in its place. The mockups answer it: `html_sources/v6/08b_add_model.html` shows **a single control, "Add as Worker"**, against an instance expanded from a vendor-and-version row. From the researcher's side the flow is **1 step**. The multi-step sequence the question probably meant is B21's **5 dependency-ordered internal build steps**, which the user never sees. Conflating the 2 is what made the question unanswerable.

## Storing credentials — sound, with one part to argue

**Not in the authoritative brief at all.** §12 (Advanced) lists the registry-tunable surface, schema-vs-experiment defaults, and the donation matrix. `html_sources/v6/10_advanced.html` is a **stub** carrying only a heading. So this is a feature request, consistent with his own note that the mockups are incomplete.

**Sound:** encrypting API keys at rest behind a researcher-supplied password. The current state is worse — **10 keys in a plain-text `.env`**.

**Refinement 1:** prefer the platform keychain over a bespoke file format. 1 small dependency (`keyring`), and it removes a class of mistakes.

**Refinement 2, and this is the part to argue:** storing **account passwords** for automatic sign-in is the wrong mechanism. Vendor CLIs authenticate by device flow and hold short-lived session tokens; a stored password cannot pass a second factor, and automating a sign-in with one is fragile and likely outside vendor terms. What achieves the goal is storing the **OAuth refresh token** the tool already issues — designed for exactly this, revocable, and not a password. **Keys and refresh tokens yes; account passwords no.**

**Existing machinery is the wrong tool:** the project's "vault" is `bench/verification_chain.py`, a hash-chained Merkle structure with optional Ed25519 signing. That is *integrity*, not *confidentiality*. But `cryptography` is already an optional dependency, so authenticated encryption needs nothing new installed.

## The exp44–49 replay — what, why, still relevant

Runway item **1.7**: replay those 6 experiments through the repaired accounting and report old against new `rho`, `gamma` and the novelty series. Status **TODO**; the runway notes *"archive is intact; this is how everything this week was derived"*.

**Why marked:** the item above it found that `_resolve_merge_source` could not resolve the label syntax the runner itself teaches, so **2 of 12 seat labels never resolved and every MERGE a seat proposed was silently recast to CONFIRM**. That changes `rho`, `gamma` and every per-round novelty figure derived from them.

**More relevant now, not less:** B77 found a second defect in the same family — `scripts/replay_rho.py` reads **neither** of the 2 keys the archive persists for it (`rho_novelty_counts`, `rho_raw_counts`, each present in 40 of 101 reports). **Item 1.7 and B77 are blocked on the same repair.**

## The runway, in order

| stage | content | state |
|---|---|---|
| 0C | instrument commissioning | recorded 2026-09-01 |
| **1** | accounting repairs **+ the exp44–49 replay (1.7)** | **nearest item needing no dispatch** |
| 2 | the behavioural fix | needs 1 live run |
| 3 | exp50 physics · exp51 biology · exp52 factorial cells A–D · exp54 capstone | **built, not run** — blocked on the blind-exam ruling |
| 4 | clean control target, exp53 re-run, load-balancer shakedown | proposed |
| 4B | the BR2 bridge | immediately before Bench Run 2 |
| **4C** | **R1, the zero-plant control** | **next runway task the moment the list clears**; engineering owed **NONE** (10-item gate closed: 8 resolved, 1 withdrawn); needs his launch authorisation because it spends money |
| 5 | reviewer reproduction pack | after BR2 |
| 6 | outreach | after BR2 |
| 7 | documentation | cannot close before PoC final |
| 8 | running across many machines | recorded 2026-11-10 |

Stage 3's articles and all 5 answer keys recover from `ddd74bde^` and `eecdb0f^` and reproduce the MANIFEST hashes exactly. The branch they were on was public for a period and is gone from the remote, but anyone who cloned then holds them. Whether they may still be reported as blind exams is a judgement about that window, first requested **2026-08-08**.

## How severity is measured today, and what it drives

**It is not computed. It is asserted.** `bench/reference_runner_v3.py:10703` sets `_SEVERITY_SPEC = {"on": False}`, flipped only by `cfg.severity_spec_enabled` which defaults False. `compute_sev_f` implements §7.7 exactly, including the hard 0 for a refuted finding, and is switched off. With it off the gate reads `float(entry["severity"])` — the model's own number.

**What that number decides:**

- `:5797` — `e["severity"] >= 0.7` is part of the `exhausted` door out of `unverified_critical_count`, so it gates **convergence**.
- `:6282` — `required = min(2, external_panel_size) if sev >= 0.7 else 1`, so it sets **how much external review** a finding gets.

**2 measured consequences.** 27 of 32 disproved findings carry a severity above 0 — **84.3750%**, Wilson [68.2459%, 93.1356%]. And **no cut above 0.5 is a magnitude test**: only the `(HARD, CONFIRMED)` cell can exceed 0.5, so `Sev >= 0.7` reduces to `HARD AND CONFIRMED AND confidence >= 0.7` — a threshold on the model's own self-report.

**So severity today is a model's self-assessment gating convergence.** Enabling the formula changes a number that drives the experiment, which is why it is his.

## The panel work is folded back

Committed `371f55cc` (64 files) and `64b22872` (5 files), both on `origin/sim/shakedown-2026-09-29`, verified by SHA. Boards green at 1,791 s and 1,817 s. **172 tests pass across the 10 guards involved.** 65 of 65 committed files are byte-identical to the tested tree; the one exception is `sv_completions.jsonl`, written after the commit by design.

## The commit-cost figure he quoted

**54–57 minutes is not in this record.** 39 full boards: mean **1485.03 s = 24.75 min**, median 27.48 min, range 8.75–33.72 min, 95% t-interval [1348.4591, 1621.5922] s on 2 routes agreeing to 2.274e-13, **0 of 39 at or above 54 min**. The `54.40` in the record is **seconds** — the cost of 6 guard files — printed beside minute figures, which is how it read as minutes.

Written under CDSFL note standard v1.9 (1 November 2026).
