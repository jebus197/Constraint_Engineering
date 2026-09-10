# Parked for the founder — non-blocking items, newest last

**Opened 2026-09-10 on his instruction:** *"Why not just leave them all to discuss with me at the end of the completed task list, unless there is something that clearly warrants my immediate attention?"*

Every item here was classified by `scripts/blocker_triage.py` as NOT blocking. Nothing here is dropped; it is queued. Items that DO block are raised at once and never appear in this file.

---

## A17: the verdict-tuple guard matches function names across the repository

*Parked 2026-09-10T17:15:14+01:00.*

A new script defining scan() returning a tuple caused supersession_check.py:149 to be flagged for a truth test that is correct on a list. The guard matches tuple-returning function NAMES without resolving the call. Worked around by renaming; the cause stands. Fix is to resolve the call, which is execute-do-not-grep applied to an AST scan.

## A18: nine off-switches in the exp56 configs that no runner module reads

*Parked 2026-09-10T17:15:14+01:00.*

**NARROWED 2026-09-10 17:40 after the sweep was corrected to read the `_<field>_note` beside each switch.** `merge_arbitration_enabled` and `immune_memory_enabled` both carry documented reasons and are NOT findings. What remains unexplained is `_ouroboros.max_papers_per_round = 0` in all 3 arms, read by none of 210 runner modules, and `hardened_gate_enabled = False` in all 3, which the runner DOES read and which has no note at all. The additive standard's unwired half, in data rather than code. Not urgent: 0 of the 3 affects a live run, precisely because nothing reads them.

## A13/A14: the panel sandbox lost most of its bench tree mid-review and no seat could account for it

*Parked 2026-09-10T17:15:14+01:00.*

8 files against the canonical 167, reported by cc2 in round 4. Both seats share one sandbox, so a destructive action by the seat that finishes first lands under the seat still working. The falsifier is cheap: build a sandbox, count, run the suite inside it, count again.

## Running exp50 and exp51 dispatches 5 models including 3 paid seats

*Parked 2026-09-10T18:43:50+01:00.*

The redesigned configs are ready at bench/exp50_configs/50_physics_exam_live_redesigned_2026-09-10.json and bench/exp51_configs/51_biology_exam_live_redesigned_2026-09-10.json. Running them is money. Nothing on the task list waits on the result, so it is not blocking.

## The 2 Wolfram items, neither of which blocks the task list

**0.1, the desktop Engine licence — DATE-GATED, not blocked.** His ruling stands: leave it to auto-renew, and it cannot be renewed before it expires. The status is OBSERVE ON THE DAY and the day is **2026-09-11**. Nothing can be done on 2026-09-10, and nothing else on the list waits on it. It stays OPEN because the observation is genuinely still owed, not because work stalled.

**W1, the MCP server licence — BLOCKED ON AN EXTERNAL PARTY.** He emailed Wolfram and awaits a reply. That reply is not in this project's gift and no amount of work here produces it. The entry is correctly marked BLOCKED.

**Neither is a blocker under his own criterion,** which is whether an item prevents further progress on the task list. 36 other entries remained open when these were triaged and work continued straight past them. Recorded here rather than raised, exactly as he asked: *"If not, then append to the closing/final report."*

*Parked 2026-09-10T19:42:41+01:00.*

## C0040: every model receives 9.0026% of the universal directive, and it is a flag dump

**Raised by ChatGPT on 2026-06-06 at severity 0.88, recorded UNCONFIRMED and UNTOOLABLE, never checked. Confirmed 2026-09-10 and it is larger than filed.**

`_load_universal_directive` serves a reduced rendering whenever the full text exceeds a model's `max_directive_chars`. The full directive is **27,803 characters** and the largest cap in the roster is **12,000**, so the reduced form goes to **5 of 5 models** — Wilson [56.5518%, 100.0000%], Clopper-Pearson [47.8176%, 100.0000%]. The docstring promises "Full text for large-context models"; **no such model exists**. The reduced form is **2,503 characters of TOML key-value lines** — `policy.constraints.falsification_required=true` — and **0 of the full directive's 16 section headings survive it**.

**The severity is bounded by a second path, and that must travel with the finding.** `reference_runner_v3.py:8339` appends `cdsfl_operational.md`, **44,157 characters**, to every model, explicitly exempt from the phenotype caps. The prompt a seat actually receives is **46,660 characters and over 90% prose**. Models are not left holding flags.

**What is lost by BOTH paths.** The operational directive covers **6 of the 16 sections (37.5000%**, Wilson [18.4812%, 61.3590%], Clopper-Pearson [15.1984%, 64.5654%]). The other 10 include **"Runnable Falsifiers for Critical Findings"** and **"Falsifier Integrity — Do Not Reach for the Answer"** — the section instructing models not to cheat on the falsifiers this project's verdicts rest on. **The coverage heuristic is crude** (first 3 words of 4 or more characters per heading, all required to appear in the operational text), so **10 of 16 is an UPPER BOUND on the loss, not a measurement of it**, and the test asserts the bound rather than the estimate.

**WHY NO FIX WAS APPLIED.** Changing which directive text a model receives changes every dispatch and invalidates replay of every archived run. That is the same class as promoting the corrected S\* threshold, which this project already ruled needs your say-so. The disposition is yours: raise the caps, rewrite the reduced rendering as prose rather than flags, or accept the loss and record it. `bench/tests/test_falsifier_C0040_universal_directive_2026-09-10.py`, 8 tests.

*Parked 2026-09-10T20:08:05+01:00.*

## C0037: the directive dedup deleted a formula and kept its special case

**Raised by DeepSeek on 2026-06-06 at severity 0.70, recorded UNCONFIRMED and UNTOOLABLE, never checked. Confirmed 2026-09-10 with a quantified harm.**

`_semantically_duplicate` treats a short line as a duplicate of a longer one whenever `intersection / min(len(left), len(right)) >= 0.95`, and the dedup keeps whichever came **first**. So the survivor is decided by position, not content. It runs for **4 of the 5 models**, every `concise` and `minimal` phenotype.

**Measured over the real corpus:** 14 of 1,677 lines are dropped (0.8348%, Wilson [0.4979%, 1.3964%]), of which **11 are dropped by containment alone** with a Jaccard below the 0.85 bar (78.5714%, Wilson [52.4108%, 92.4286%], Clopper-Pearson [49.2024%, 95.3421%]).

**The case that makes it real.** In `logistics_supply_chain.txt` the dedup DROPS `SS = z * sqrt(LT * sigma_d^2 + d_bar^2 * sigma_LT^2)` and KEEPS `SS = z * sigma_d * sqrt(LT)`. The kept line is the dropped line at `sigma_LT = 0` — a strict special case, constant lead time. SymPy gives `general^2 - simple^2 = d_bar^2 * sigma_LT^2 * z^2`, and z3 returns **UNSAT** for "can the general form be smaller". At z = 1.645, LT = 9, sigma_d = 20, d_bar = 100, sigma_LT = 0.5 the surviving formula **understates safety stock by 29.778607 units, 128.478607 against 98.700000, or 23.1770%**, with mpmath and numpy agreeing to 1e-9. A model reading that directive is told to size safety stock with a formula that cannot see lead-time variability.

**THE PROPOSED FIX IS 1 LINE, AND IT IS YOURS TO TAKE.** When containment fires, keep the line with **more tokens** rather than the earlier one. That never loses information and changes only which of a matched pair survives, not which pairs are matched. It is not applied because it changes the directive text every model receives and so invalidates replay of archived runs — the same class as C0040 and as the S\* threshold promotion. `bench/tests/test_falsifier_C0037_containment_dedup_2026-09-10.py`, 7 tests.

*Parked 2026-09-10T20:11:38+01:00.*

## C0036 and C0054: the conflict detector is blind to 95.6120% of the directives

**Raised twice by DeepSeek in one exp42 run, severity 0.80 and 0.70, both recorded UNCONFIRMED and UNTOOLABLE, never checked. Confirmed 2026-09-10.**

`resolve_layer_conflicts` decides which contradictory directives survive composition, and it asks `_directive_topic_and_stance` what each directive is about. That helper recognises exactly **4 topics** — verbosity, examples, rationale, table — and returns nothing for everything else. DeepSeek's own examples, *"never infer missing data"* against *"fill missing values with defaults"* and *"use metric A"* against *"use metric B"*, all return `(None, None)`, so both sides of each contradiction are retained.

**Measured over the 866 directive blocks in `bench/directives`: 828 get no topic at all — 95.6120%**, Wilson [94.0346%, 96.7866%], Clopper-Pearson [94.0266%, 96.8764%], statsmodels and mpmath agreeing to 0.0e+00. Only 38 blocks are classified: table 30, rationale 7, verbosity 1. **The `examples` branch fires on 0 of 866** — a live branch nothing reaches, which is the additive standard's unwired half sitting inside a classifier.

**It is reached on every composition:** `composer.py:1415` calls the resolver, and `compose()` is the live runner's system-prompt mechanism.

**NOT APPLIED, and the reason is the same as C0040 and C0037:** widening topic detection changes which directives survive, so it changes the prompt every model receives and invalidates replay of archived runs. The disposition is yours. `bench/tests/test_falsifier_C0036_C0054_conflict_topics_2026-09-10.py`, 7 tests.

**One piece of good news for decision 15.** The finding text could not be read from the registry — the stored description is truncated at 200 characters and stops mid-word at *"That helpe"*, and the run's `descriptions_backfill.json` holds 18 of 67 entries and not this one. **The full text survives intact in the raw reply** `r4_deepseek_20260606T213045Z.json`. So the archived truncation damage is **repairable from the replies rather than lost**, which is better than decision 15 currently assumes. A test asserts both halves so the recovery route cannot quietly disappear.

*Parked 2026-09-10T20:28:03+01:00.*
