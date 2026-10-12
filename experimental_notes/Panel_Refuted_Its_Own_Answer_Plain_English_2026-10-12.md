# The panel refuted its own answer, and three decisions are now waiting

**2026-10-12, 21:13 BST.** HEAD `716248fd` on `sim/shakedown-2026-09-29`, pushed.

**Audience: a reader who can follow a file path but was not in the session.** The technical record, carrying both seats' replies unedited, is in `Free_Panel_FULL_RECORD_Clearing_The_Outstanding_2026-10-12.md` (blind half) and `Joint_Panel_FULL_RECORD_Clearing_The_Outstanding_2026-10-12.md` (joint half). This document is the companion that says what happened and what it means.

## What ran

The free panel ran twice on 2026-10-12. First **blind**, each of the 2 seats sealed in its own sandbox and unable to see the other. Then **jointly**, each seat shown the other's work and the orchestrator's own repairs. Free seats only — `cc2` and `fable`, both on the Max subscription — with `paid_seats: []` recorded in both rounds' `topology.json`. No paid dispatch occurred and none was authorised.

The first joint dispatch attempt was **refused by the brief gate**, and the refusal reported that 5 seats had been selected with 3 of them paid. The seats were then pinned explicitly with `PANEL_ONLY=cc2,fable`. That gate prevented an unauthorised spend; relying on a default would not have.

The headline is not that the panel was right. The joint round refuted the answer **both seats had independently reached in the blind round**, and refuted **one of the orchestrator's own repairs** as well.

---

## Decision 1 — the severity gate releases a number its own proof never reads

**This reverses what was reported earlier the same evening.**

The founder had rejected the removal of the severity test, because he never approved it. The removing commit argued from his own principle that there are no votes in CDSFL, on the grounds that a severity figure is a number a model asserts rather than a measurement.

In the blind round both seats concluded, independently, that the tension was already resolved in the tree: the restored test gates on `severity_is_proven`, which accepts an entry only when `_validate_rk_computation` re-derives the model's stated `R_k` from the inputs the model itself named. Two blind seats reaching that separately is replication, and it was reported to the founder as probably settling the matter.

The joint round asked each seat to execute the attack one of them had itself named. **Both refuted themselves, at two levels.**

**Level 1 — the re-derivation checks arithmetic only.** Inputs invented wholesale but mutually consistent return `PASS`. Nothing cross-checks a single input against any harness-held value. Reproduced by `scripts/severity_proof_gaming_2026-10-12.py`.

**Level 2, decisive — the proven quantity is not the gated quantity.** The release condition reads the proof *status* and the raw `severity` float. The proof re-derives `R_k` from `R_k`'s own stated inputs and **never reads `severity`**. A proof whose content states `R_k = 0.95` releases a `severity` of 0.45, and A4 falls from 1 to 0 on exactly that proof.

Measured independently of both seats over all 521 archived entries carrying a `PASS`/`WARN` proof (`scripts/the_proven_number_is_not_the_gated_number_2026-10-12.py`):

| quantity | value |
|---|---|
| Pearson r (proven `R_k` vs gated `severity`) | **−0.3438** |
| p | 6.689e-16 |
| 95% CI | [−0.4174, −0.2657] |
| numpy cross-check | agrees to 5.55e-17 |
| Spearman rho | −0.3454 |
| r² | 0.1182 — **11.82% of variance, NEGATIVELY** |

A higher claimed severity goes with a *lower* proven residual risk. The proof does not weakly corroborate the number it licenses; it moves against it.

**What stays true, so the correction does not overshoot:** the gate is not a no-op. It forces a model to commit to named inputs and publish arithmetic a later round can attack, and `FAIL` is reachable and blocks. It is better than the bare float. It is not what both seats, and then the orchestrator, said it was.

**The decision.** Requiring the proof to be *about* the released number, at the proof's own 0.05 tolerance, would stop **434 of 521 (83.30%)** currently-proven entries from being released. The question underneath cannot be settled by measurement, which is why it is the founder's: **what is `severity` to be computed from?** Residual risk and impact are different quantities.

---

## Decision 2 — a falsifier can read this project's own evidence

The falsifier observer's rendered allow set contains the **repository root**, so `experimental_notes/` and `bench/logs/` are readable from inside a sandboxed falsifier. The sealed scoring key store at `~/.config/cdsfl/` is **not** reachable — verified by execution, not assumed.

- `cc2` measured **472** sibling panel sandboxes sitting under an allowed temp root: other seats' material, not a key.
- `fable` established that narrowing the tempdir allowance alone would **not** close it, because the clone root grants it independently.
- The orchestrator's own instrument confirmed the repo-root allowance on a **clean** tree, so it is pre-existing and neither seat's fix introduced it.

**Both seats declined to fix it, for the same reason:** the observer is the most safety-critical component in the harness, the change reorders its gate precedence (`_protected` → allow → deny), and shipping that untested at the end of a one-shot round is worse than the documented hole. The orchestrator did not fix it either.

**The decision.** This needs a dedicated pass with the 41-test key-access suite extended first, and the founder's word on whether that pass is next.

---

## Decision 3 — the reclassification semantics

A serve in which **no rung reached any model** (the transport-dead / 402-cascade class) used to record verdict `ERROR`. That reads as a *ruling*: an assertion that something examined the finding. The fix reclassifies that one shape — `rungs_reached == 0` — into a no-reading record. This is what makes it possible for a finding nothing ever examined to stop blocking convergence for ever.

It changes what a stored record **means**, so accepting or rejecting it is the founder's, not the panel's.

---

## The repair that did not work, and it was the orchestrator's

After the blind round the 2 seats had fixed the same blocker by different mechanisms — one **serves** a never-examined finding so a tool can decide it, the other opens a **door** so one nothing ever touched stops counting as a blocker, with a paired reader so the exclusion is never silent. Each passed its own falsifier and failed the other's.

**Composed, they were worse than either alone.** Serving appends to `routing_history`, and an empty `routing_history` was one of the facts the door required, so the serve consumed the door's own trigger. That was found and repaired by separating SERVED-AND-NO-READING from SERVED-AND-RULED on `NO_READING_ROUTING_VERDICTS = {"", "UNRESOLVED"}`.

**The joint round established that repair was inert.** `fable` enumerated the live ladder's reachable verdicts and found the intersection empty. The source confirms the mechanism: `bench/routing.py:207` initialises `last_verdict` to `"UNTOOLABLE"` and only ever reassigns it to `"ERROR"` or a `reverify_fn` verdict. Measured across the archive (`scripts/my_sentinel_set_matched_nothing_2026-10-12.py`):

```
archived ladder records: 311
  CONFIRMED 142 | ERROR 86 | UNTOOLABLE 59 | REFUTED 18 | INTEGRITY_VIOLATION 6
records the sentinel set matches: 0 of 311 = 0.0000%
  Wilson 95% [0.0000%, 1.2201%]
```

The door could never open after a real serve, and the defect reported as fixed still stood. **The three outcomes measured as proof it worked were all produced with a stub whose verdict the orchestrator chose.** A repair verified only against a mock is verified against its author's expectations.

## The second seat's finding is sharper than the first

**The door was wider than the severity gate, and nullified it for that entry class.** Every conjunct of `_routing_ladder_never_served` reads a ladder, falsifier or escalation field; the R_k proof checker writes to none of them. So an entry whose proof had been computed and had **FAILED** was released anyway. Of 431 non-terminal entries the pre-fix door released, 25 carried a proof result — a reading discarded on **5.80%**, Wilson [3.96%, 8.42%].

**All 3 fixes are in the tree and all 3 are needed.** Each alone passes its own falsifier and fails the others'. Composed: 13 + 6 + 6 + 18 + 20 + 15 green. The composition was **tested, not assumed** — the lesson the blind round taught at its own expense.

One bound was challenged rather than accepted: `LADDER_UNSERVED_MIN_AGE_ROUNDS = 1`. Measured across every archived registry, **230 of 230** ladder-served entries were served in their arrival round (Wilson lower bound 98.36%), so a longer lock buys no service.

## The disagreement resolved by taking both sides

Both seats found the same cause in `_secondary_interpreter_roots` and proposed opposite repairs. The function asks each interpreter where its own installation lives by running it, and cached the answer for as long as the runner stayed in memory. With every probe timing out on a loaded machine it returned 0 roots, and the cache made that permanent: one 10-second spike at the first falsifier returned the gate to refusing every spawned-interpreter falsifier for the whole run — measured end to end as `CONFIRMED → INTEGRITY_VIOLATION`, persisting after the load cleared.

| approach | under total probe failure | cost |
|---|---|---|
| `cc2` — never cache an incomplete answer, retry | failure is **transient** | up to 30 s per falsifier on an 8 GiB machine |
| `fable` — derive roots structurally from the interpreter's path | **41 roots** vs 39 healthy: harmless | fallback set is a structural guess, and **wider** |

Retrying buys no coverage, so it was not taken, and its test file was not applied. But permanence is its own defect, because caching a wider guess persists a wider allowance. **Both were taken:** fall back so the moment is harmless, decline to cache a fallback so the moment stays a moment, and **name** the interpreters whose roots are guesses via `secondary_interpreter_discovery_fell_back()` — the founder's own 2026-10-02 excluded-implies-reported discipline.

## The parked items, and why their vagueness was the answer

The founder said the outstanding questions were too vague to act on. Both items both seats had called mechanically fixable **rested on stale premises**, which is itself the answer.

- **Item 1 (A17)** names a guard in `scripts/supersession_check.py`, which contains no such guard and does no name matching. The real guard is `TestVerdictTuplesAreNeverTestedForTruth` in `bench/tests/test_operational_scripts.py`, fixed 2026-09-11 with its own committed test. Both seats declined to write anything; one noted a second test would be an addition nothing reaches.
- **Item 2 (A18)** — **the seats contradicted each other.** `cc2` held that writing the note would be *actively harmful*, moving the row onto the sibling-note path and breaking the control. `fable` wrote it in all 3 arms and replaced the 2 affected assertions. Testing settled it: the replacements pin **2** facts where the old pinned 1, and require the note to state the redundancy rather than restate the block's intent. The objection is true of the *old* control and answered by its replacement, not by avoiding the work. 21 green on the capability sweep, 95 on the exp52 switches.
- **Item 3 (A13/A14)** confirmed stale by the day's own evidence: its premise is one shared sandbox, and both rounds today gave every seat its own.

## Closed today, and a pattern worth naming

The board went **2 red → 0**, both false reds on correct mechanisms: the simulated-run invariant restated 2 of the audit's 3 exclusions and omitted `_is_seat_scratch`; the exp52 omission check looked inside `_dispatch_single_model`, a thin wrapper, while the live wiring sits in `_dispatch_single_model_inner`. Both now call the real thing, both verified by deliberate breakage.

Parked item 18 was fixed with real consequence: `scripts/blocker_triage.py` answered 2 of the 3 questions its own header names, so an entry ending "NEEDS A POLICY RULING" triaged as ordinary work and `hooks/work_not_narrate.py` read that as "carry on". `decision_required()` is a **third flag, not a third verdict** — folding two together is the defect the first version shipped.

And `scripts/make_panel_full_record_2026-09-11.py` could write a record the guard checking for records cannot see, because that guard globs `*FULL_RECORD*.md`. It now refuses.

**The pattern, in the orchestrator's own 4 errors of the day — every one a check run against the wrong baseline:** an instrument counting interpreter roots that do not exist on disk; a mutation applied to the first of 2 call sites rather than the operative one, which then falsely passed; a false accusation that `cc2` deleted the founder's rulings, caused by a diff whose reference side was newer than the clone; and a paired reader keying on a cache the fallback path deliberately leaves empty, so it reported nothing for a failure it had just observed — with the first test written for it reading the report while the probes were still dead, so the mutation was invisible and all 6 tests stayed green. Each was caught by asking *what else could produce this reading*. Each would have been caught sooner by asking it first.

## State

Both rounds harvested, tested, applied, committed and pushed, each with a FULL RECORD note carrying both seats' replies unedited. Pre-commit board 502 green. **A complete board is running and not yet reported, and it predates the J2 and J4 work — a fresh one is owed before the next simulated run.**

Written under CDSFL note standard v1.7 (26 August 2026).
