# The 554 was a line count, not a task count

2026-11-09, 20:56 GMT

---

## 1. What the number was

`554` is the sum of the **added-line counts** on the editor's *Changed 3 files* card:

| File | Added | Deleted |
|---|---:|---:|
| `scripts/how_many_items_actually_remain_2026-11-09.py` | 532 | 9 |
| `~/.claude/CLAUDE.md` | 20 | 2 |
| `.claude/CLAUDE.md` | 2 | 2 |
| **See all** | **554** | **13** |

532 + 20 + 2 = 554 and 9 + 2 + 2 = 13, verified on NumPy and SymPy, both agreeing exactly.

The literal `554` appears **nowhere** in the assistant's written output for the session, in no project file as a tally, and in no ticket-store or task-list subtotal. Searched: the 951,736,790-byte session transcript (word-boundary match, text blocks only), `experimental_notes/*.md`, the Desktop `.md`/`.txt` surfaces, and every `TicketStore` view. No count of 554 outstanding items has ever existed.

## 2. The claim that primed the alarm is withdrawn

The assistant described the master task list as possibly never exhausting. That was wrong.

`scripts/task_list_burndown_2026-09-11.py` reports `SUBCRITICAL (terminates): False`, which means termination **cannot be asserted** at 95% — a statement about evidence strength, not about unbounded growth. R = 0.907173, CI [0.754456, 1.090802], p = 1.616371e-01. The same series records a **minimum of 2 open entries on 2026-09-11**, which demonstrates the list empties.

Present census, from the canonical reader: **274 entries — 20 open, 240 done, 5 deferred, 9 withdrawn** (sums exactly).

## 3. How many entries he actually asked for — preliminary

2 surfaces, because an instruction reaches the assistant by 2 routes:

- **(a)** 870 annotations across his annotated response files, read with `scripts/read_founder_responses_2026-10-11.py` (format-aware; never grepped).
- **(b)** 1,000 distinct chat messages of his from the session transcript, hook and system-reminder text excluded by marker.

| Reading | Annotations | Chat | Total |
|---|---:|---:|---:|
| NARROW (adding verb + the list named) | 4 / 870 | 17 / 1,000 | **21** |
| WIDE (also "the list" / "your list") | 5 / 870 | 18 / 1,000 | **23** |

- annotations NARROW: 0.004598, Wilson [0.001789, 0.011762], Clopper-Pearson [0.001254, 0.011730], 2-route gap 3.469e-18
- chat NARROW: 0.017000, Wilson [0.010641, 0.027056], Clopper-Pearson [0.009934, 0.027079], 2-route gap 6.939e-18

These count **instructions**, not the entries each produced; several name a batch. His recollection was "no greater than 30", and 21–23 instructions is consistent with it.

Producer: `scripts/how_many_did_he_actually_ask_for_2026-11-09.py`.

## 4. Why the session kept stopping

The continuation script he remembers **exists and runs**: `~/.claude/hooks/work_not_narrate.py`, the 7th of 7 `Stop` hooks. On each attempted stop it reads the task list, counts open entries, names the first, and refuses with *"Do not stop here."*

2 properties explain the repeated stopping exactly:

1. **`MAX_REFUSALS_PER_TURN = 8`** (line 80). After 8 continuations it stands down by design — *"8 refusals already this turn, which is the budget. Allowing the stop so a finished session cannot be trapped."* The transcript shows this ceiling reached repeatedly through 2026-11-09.
2. **`open_items()` (line 368) returns `opens[0]`** — the first OPEN entry in *file order*, with no test for whose move it is. That entry was B21 on every turn of 2026-11-09, and B21 waits on him.

So the script pushed 8 times per turn toward an entry that could not advance without a ruling. **His proposed remedy — putting the 5 agreed steps at the top of the list — is mechanically correct for this cause**, because selection is by file position.

Editing that hook is self-modification under entry B113 (unruled), so nothing there was touched.

## 5. C0001 — the coherence pruner

`_prune_for_coherence` deletes optional directive text when constraint density exceeds a budget. Density = `_count_constraints(policy)` (read from the TOML policy dict) ÷ token estimate. **Pruning cannot touch the numerator**, so every deletion shrinks only the denominator and density *rises*.

Proved rather than observed, on 2 tools: SymPy gives `d(C/t)/dt = -C/t²`; z3 returns **UNSAT** for "can density ≤ budget hold after pruning". Both exit conditions are dead code. Raised 2026-06-06 at severity 0.90; confirmed 2026-09-10.

**It cannot fire today.** On his 2026-10-13 ruling the pruner is off by default — verified by executing the signature, `compose(coherence_pruning=False)` — and a guard asserts that default.

Nothing is owed on the defect. The only open question is whether an entry recording a confirmed severity-0.90 finding should stay on the list when its code path is disabled. Left OPEN rather than closed, because closing a confirmed critical on those grounds is his judgement. **1 word closes it.**

## 6. B21 — model and role selection

No message of his in the chat record rules on B21. A transcript scan for his own messages mentioning B21 or B111 since 2026-11-05 returned 31 matches, **all** automated Stop-hook text.

**1 of 5 steps built** = 0.200000, Wilson [0.036224, 0.624465], Clopper-Pearson [0.005051, 0.716418], 2-route gap 1.110e-16.

| # | Step | State |
|---|---|---|
| 1 | `load_effective_policy` wired into `bench/reference_runner_v3.py` | **NOT DONE** — 0 call sites |
| 2 | live harness reads the merged policy | **1 of 6 files**; 5 keep their own tables (Wilson [0.030053, 0.563503]) |
| 3 | a role dimension | **DONE** — 3 `roles/*.toml`, merge signature takes a role |
| 4 | `validate_all_policies` as a v3 preflight | **NOT DONE** — 0 call sites |
| 5 | the selectable model list is generated | **NOT DONE** — 0 of 7 candidate definitions |

Each of steps 1, 2, 4 and 5 changes how a run selects its models, which is his decision. Producer: `scripts/which_of_b21s_five_steps_are_built_2026-11-09.py`.

## 7. B111 — the error figure with no producer

**He did respond, on 2026-11-08, and it was a question:** *"What would this mean in real terms? Qs"* — so an answer is owed to him, not a decision by him.

Both CLAUDE.md files state that of 12 errors on 2026-10-11, 10 were catchable by reasoning before running anything. No script reproduces any of those figures, and the denominator cannot be rebuilt: that date carries 14 memory files and nothing records which 12 were counted.

**In real terms:**

| | Option 1 — produce it | Option 2 — retire it |
|---|---|---|
| Work | Enumerate 2026-10-11's errors from the transcript, classify each on the original axis, carry per-item data | Delete the sentence from both files |
| Cost | A few hours | Minutes |
| Result | A *different* number over a *different* population (transcript, not memory files). Replaces the claim rather than confirming it — "10 of 12" stops being true | The depth-over-breadth argument loses 1 unsupported figure and keeps 2 that are produced |
| What survives | — | 16 of 18 errors were in the instruments, 0.888889, Wilson [0.672002, 0.968980]; and 0 of 7 noticed unaided, exact binomial p = 0.0078 |

Nothing about how the work is done changes either way. What changes is whether a number in an instruction file can be checked by running something. **Recommendation remains option 2**, under `additive-standard`'s removal clause, with REPRODUCIBILITY as the named property on which the replacement dominates.

## 8. The agreed order

1. Retire the asking sentence from an entry when a ruling is recorded against it.
2. Replace the frozen "are these repeats" banner with a computed one.
3. Teach the per-turn status line to report whose move an entry waits on.
4. Hoist the cheap commit checks ahead of the test board (lines 702–710 of `hooks/pre-commit`).
5. Build the outstanding items; answer B21 and B111.

The full task-list inventory is scheduled **last**, on his instruction.

---

*Written under CDSFL note standard v1.9.*
