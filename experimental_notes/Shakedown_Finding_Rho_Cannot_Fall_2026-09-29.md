# The Shakedown's First Finding: Convergence By Saturation Is Unreachable, By Construction

**2026-09-29, 19:25 BST.** [NEEDS YOUR RULING]. Audience: a reproducing engineer.

**Run:** `bench/logs/shakedown_2026-09-29/` — arm 1, 5 `-SIM` seats, reached **round 5 of 7** before the session that launched it ended, taking the runner with it. 50 files harvested to `arm1_harvest/`. Every figure below is from that run's own data or from the shipped code, executed.

---

## The finding

**`rho` = novel/raw is pinned at exactly 1.000 in every round, and cannot be otherwise.** Observed: rounds 0–4 all `rho=1.000`. The archived 2026-09-21 run: all 8 rounds `rho=1.000`. Registry grows linearly (22, 30, 37, 45, 53 — +8, +7, +8, +8) with no saturation.

`rho` feeds the convergence machinery. A run can therefore only ever converge by **exhausting its round cap**, never by the discovery curve flattening.

## The chain, each link measured

1. **`FindingRegistry.register()` mints a new canonical id unconditionally** — `canonical_id = f"C{self._next_id:04d}"`. Two models finding one defect produce two unlinked canonicals.

2. **Novelty is counted on an alias miss, not on content.** `reference_runner_v3.py:14418` uses `lookup_alias(f.model_id, f.finding_id)`, and the shipped body is `self._alias_map.get(f"{model_id}:{local_id}")`. Executed: two models with the same defect and the same local id both return `None`, both increment `novel_this_round`, giving `rho = 2/2 = 1.000`. "Novel" means *this model has not used this id before*, not *this defect is not already known*.

3. **`occasions` is the repair, and it is starved.** Added on the founder's 2026-09-04 ruling and described in its own comment as *"read by nothing yet"*. It **is** appended to — at line 2429, `_tgt.setdefault("occasions", []).append(...)` — but only inside a **merge** path.

4. **The merge path never completes.** Merges are withheld pending a tool verdict (`feedback_no_model_voting`, founder ruling 2026-08-19). The run logged the same 4 withheld merges every round from round 2: `C0003→C0008`, `C0004→C0018`, `C0020→C0001`, `C0022→C0016`, each `no tool verdict`.

5. **Measured consequence:** all **53 of 53** canonical entries carry exactly **1** occasion. Multi-occasion entries: **0 of 53 = 0.0000%**, Wilson [0.0000%, 6.7582%].

**The code predicted this itself.** `register()`'s comment records: *"when two models find one defect the runner mints two unlinked canonicals and the second is merged away. The overlap signal is destroyed at exactly the point it is created, so a saturation curve built from `source_model` is linear BY CONSTRUCTION"* — measured 2026-09-02 as **2 of 2,050** archived findings raised by more than one model.

## Why lowering the similarity threshold is not the fix on its own

The routing dedup uses `_routing_similarity` — bare word-overlap Jaccard on the `description` field — at **0.85**.

Measured over this run's **53 canonical findings, 1,378 pairs**: min 0.0000, **max 0.2772**, mean 0.0659 (numpy and statistics agreeing exactly). **0 of 1,378 reach 0.85** — Wilson [0.0000%, 0.2780%]. The threshold is unreachable: at 0.2772, the most similar pair in the whole run reaches under a third of the 0.85 required.

But lowering it is not sufficient, and the numbers say why. The 4 pairs the run itself flagged score **0.1528, 0.1667, 0.1889, 0.1987** — *inside* the general distribution. Three **unflagged** pairs sit above every flagged one: `C0006/C0020` at 0.2772, `C0039/C0043` at 0.2477, `C0046/C0048` at 0.2445.

- Threshold needed to catch all 4 known duplicates: **0.1528**
- False positives it admits: **25 of 1,374 = 1.8195%**, Wilson [1.2354%, 2.6722%]
- Precision at that threshold: **4 of 29 = 13.79%**
- Rank-based separation: **AUC 0.9900** — the instrument *ranks* duplicates well; with only 4 positives the power behind that figure is very low and it is reported as such.

**A correction to an earlier draft of this note.** A first pass reported 23 pairs with identical descriptions never merged. That was an artefact of the extraction, not a finding: the id filter `startswith("C")` matched `Codex-SIM_F003` and `CC2-SIM_F003` as though they were canonical ids, so the same finding was compared against itself under two keys. Re-run with `^C\d{4}$` the count is 0. The figures above are from the corrected pass.

## What this means for the runway

The shakedown did the job it exists for: this was found on arm 1, before any paid run. Nothing here is a regression — the archived 2026-09-21 run shows the identical pattern, and real experiments (`exp40_gate` 53 merges, min rho 0.5; `exp38_ouroboros` 6 merges, rho 0.0) show the machinery *can* work, so the defect is in how the simulated arms exercise it, not in the arms themselves.

## The ruling sought

**What supplies the tool verdict that authorises a merge?** Until something does, the merge path cannot complete, `occasions` cannot grow, and `rho` cannot fall. Three shapes are available and they are not equivalent:

1. **Raise the candidate list, keep the gate.** Lower the routing threshold to ~0.15 so real duplicates become *candidates*. Safe by construction — merges remain withheld pending a tool verdict — but at 13.79% precision the candidate list is mostly noise, and something must still adjudicate it.
2. **Give the falsifier the adjudication.** A candidate pair is merged only if one finding's falsifier also fires on the other's location. That is a tool verdict in the project's own sense and needs no new judgement layer.
3. **Count novelty from `occasions` rather than from alias misses**, and let the overlap record grow on corroboration instead of only on merge. This fixes `rho` without touching the merge gate at all.

Option 3 is the narrowest and the only one that repairs `rho` directly; options 1 and 2 repair merging, which repairs `rho` as a consequence. They compose.

**Not implemented.** All three change the instrument mid-programme, and `feedback_fixes_hil_only` puts that to the founder.
