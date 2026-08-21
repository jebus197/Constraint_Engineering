# Design Reviews, 21 August 2026 — Bugzilla and Perturbation

**Four independent read-only reviews. CC2 (Claude Opus) and Fable 5, on two questions.**
Both ran on the Max subscription at no metered cost. Neither modified any file.

The Bugzilla question had been put to seven model reviews across four days and answered
by none — not from refusal, but because none had been given the material. These two were
briefed on the 76,501-character verbatim compendium. They answered it.

---

# THE BUGZILLA QUESTION

## CC2 — Claude Opus

- returned: **yes**
- elapsed: 390.9s
- length: 22,911 characters

### Verbatim

Everything below is checked. Note on my numbers: I scanned every JSON under `bench/logs/` and got 5,563 entry-*instances*, not the compendium's 2,030 final-registry entries — my sweep counts the same entry once per checkpoint snapshot. Ratios and zeros hold; absolute counts are inflated. I say so where it matters.

---

# Two corrections to the brief before I answer

**1. "No code path writes MERGED" is not quite true.** `bench/cc2_manager.py:1162` still calls `registry.resolve(fid, "MERGED", round_idx, merged_into=dup_target)` on a single LLM assessor's verdict at confidence ≥ 0.7. It is unreachable — `cc2_verification_step` appears nowhere in the repo except inside its own docstring (`cc2_manager.py:22-24`), and `reference_runner_v2.py` never imports `cc2_manager`. So the brief's *conclusion* is right and its *scope* is wrong: the live runner writes no MERGED, but a vote-based merge writer is still sitting in the tree one import away. `bench/reference_runner.py:790,828,832,2311` likewise. Delete them or they will be re-wired by someone reading them as current.

**2. `OPEN → CONFIRMED` is worse than "two independent model verifications."** At `reference_runner_v2.py:2109`:

```python
required = min(2, external_panel_size) if sev >= 0.7 else 1
```

For any finding below severity 0.7 — the majority — **one** external model's CONFIRM is sufficient. The brief describes the critical-path rule and understates the general one.

What I did confirm: `resolve()` at `:1144` is the **only** status write in the whole runner. Every transition funnels through one function. That single fact is what makes my main recommendation cheap.

---

# Q1. The status set

First, the distinction the founder asks about. **It holds, but not on the axis he names.**

Voting on existence ("I also observe this") is *weak evidence*. Models are not independent samplers — DeepSeek's "correlated echoes" and Gemini's "mode collapse" points are the same point, and both are right in principle.

Voting on identity ("these are the same") is *not evidence at all*, and this is measured, not argued. Identity of defect is a counterfactual property: does repairing A stop B firing? Descriptions, cosine scores and token overlap are correlates of a counterfactual, never the counterfactual. `experimental_notes/Dedup_Historical_Brief_2026-08-17.md:553` gives the project's own numbers for the current description-based rule on the hard band: **false-merge 64.4%, false-split 42.5%** across 85 tool-labelled pairs. Worse than a coin. That is a demonstration that identity-by-description is not a weak signal but a null one.

But the axis that should actually govern the design is **reversibility**, not identity-versus-existence:

- A wrong CONFIRMED leaves the finding in play. A later CHALLENGE moves it to CONTESTED. Recoverable.
- A wrong MERGED deletes it. MERGED is in `_NON_NOVEL_TERMINAL_STATUSES` (`:4292`), so the finding leaves γ, the novelty count, `open_crit_high_count`, `contested_count` and `irreducible_queue_count`. `resolve()` short-circuits on MERGED at `:1860`. There is no unmerge. The `hil_reason` string promising "Reversion available" is the only occurrence of that word in the file and describes nothing that exists.

**So: the tool requirement should be indexed to destructiveness.** A destructive transition requires a tool. A non-destructive one may be model-attested, provided the record says so.

Here is the set. Nine states, one fewer than today.

| Status | Meaning | In | Out | Evidence required | Who may assert |
|---|---|---|---|---|---|
| `OPEN` | Filed, not adjudicated | registration; `REOPENED` after a round | any below | none | model |
| `CORROBORATED` | ≥1 independent model also asserts it. **Not a truth claim** | `OPEN` | `CONFIRMED`, `REFUTED`, `UNCONFIRMED`, `WITHHELD` | model attestations, counted and named | **model** — this is where existence-voting is legal, because it is non-destructive and only routes |
| `CONFIRMED` | A falsifier was executed by the runner and fired against the target | `OPEN`/`CORROBORATED`/`CONTESTED` | `CLOSED`, `CONTESTED`, `REOPENED` | falsifier source + exit status + target hash | **tool only** |
| `REFUTED` | A falsifier was executed and did not fire | `OPEN`/`CORROBORATED` | `REOPENED` | same | **tool only**, and already correctly distrusted for criticals (`:3025-3030`) |
| `CLOSED` | A proposed fix was applied to a scratch copy and the falsifier stopped firing | `CONFIRMED` | `REOPENED` | pre/post falsifier verdicts + diff + target hash | **tool only** |
| `MERGED` | Counterfactual repair says two findings are one defect | `OPEN`/`CORROBORATED`/`CONFIRMED` | nothing — terminal | `adjudicate_by_repair` verdict `SAME` in **both** directions | **tool only** |
| `WITHHELD` | A merge was proposed and the tool could not decide | `OPEN`/`CORROBORATED` | back to `OPEN` on new evidence | the tool's `UNDECIDABLE` / `DISAGREE` / `NO_BASELINE` verdict, stored | tool records; finding stays live and countable |
| `CONTESTED` | A CONFIRMED finding drew a challenge with new evidence | `CONFIRMED` | `CONFIRMED`, `REFUTED`, `ESCALATED` | the challenge text and its falsifier if any | model may raise; only a tool or human may settle |
| `ESCALATED` | No tool can decide and it matters | anywhere | any | the exhaustion record | **human only** — this is the sole arbiter state |

**Changes from today, and why.**

*Drop `DUPLICATE` entirely.* It appears in eleven terminal-status sets across the runner and has been written **zero times** — I confirm the zero across all 5,563 entry-instances I scanned. Two words for one state, neither written, eleven filters that look like they do something they do not. Bugzilla itself has one: `RESOLVED/DUPLICATE` plus a `dupe_of` field. Collapse to `MERGED` + `merged_into`.

*Split today's `CONFIRMED` in two.* Right now `CONFIRMED` is written from a model count at `:2113` and from a falsifier result at `:3017` and `:3424`, and the entry keeps no record of which. The consequence is the measurement below.

*Add `WITHHELD` as a real status.* It already exists as two loose fields (`merge_candidate_of`, `merge_blocked_reason`, `:1994-1998`). Making it a status means the withheld population is countable, and the founder can see how often the tool declines. On the archive that rate would be 36.1% (`Dedup_Historical_Brief_2026-08-17.md:542`) — which is fine, because withholding is the safe direction.

**Where a human is the only possible arbiter.** Exactly one place: `ESCALATED`. Not "the tool disagrees" — that is `WITHHELD`. Not "it is a judgement call" — that is where the project has historically leaked. `ESCALATED` means the falsifier ladder is exhausted, no model produced a runnable test, and the finding is critical. That is the existing `irreducible_escalation` path at `:3428-3440`, and it is already right. Do not widen it.

---

# Q2. Ledger versus instrument

The founder's objection is the correct one and I will answer it concretely rather than restating it.

**The status is already an instrument, in one way that works.** `cdsfl_operational.md:317-320` states it: a CLOSED finding leaves the active pool, so round N+1 spends its budget on undiscovered ground instead of re-describing settled ground. That is a scheduler, not a record. It is testable free on the archive: does the fraction of round-N findings that restate round-N−1 findings fall as the CLOSED count rises? Nobody has run that. It costs a replay.

**The mechanism that answers the founder's actual question is EXTEND, and it is lying unused in the archive.**

His words were: *"a way of gathering and assessing fixes and how they should be applied to improve/add to a better solution"*, and separately, *"Only when this can be demonstrated programatically by the system, can a result then be considered to be 'merged'?"*

`EXTEND C0001 | [new consequence or edge case]` (`:5224`) is exactly a model contributing a *contributory element to the betterment of the whole*. The prompt offers it as the explicit alternative to filing a duplicate (`:5233`). Models used it — I count **543 EXTEND verdicts across 390 entries** in my sweep (183 in the compendium's deduplicated count; same fact, different denominator). And `grep -c '"EXTEND"' bench/reference_runner_v2.py` returns **0**. The verdict is parsed by `_VERDICT_RE` at `:1529` and read by nothing.

Here is how EXTEND becomes the assessment machinery, using only tools that already exist:

An EXTEND says "your fix must also handle Z." Make it carry a falsifier for Z. Then, per extension:

1. Run Z's falsifier against the target. Does not fire → the extension is not real. Record and drop.
2. Apply the parent's `proposed_fix` to a scratch copy, run Z again. **Stops firing** → the parent fix already covers Z. The extension is `SUBSUMED`: it proves the fix's scope is wider than claimed. Non-blocking, and it is evidence the fix is good.
3. **Still fires** → the parent fix is *demonstrably insufficient*, and the system now names exactly what it misses. The parent cannot CLOSE on that fix. It stays live carrying `fix_insufficient: [Z]`.

Step 3 is the whole answer. A fix that survives K independent extensions is a better fix than one that survived none, and "better" is a count of executed falsifiers, not a show of hands. Different models contribute independently to a single solution, and the contribution is adjudicated by re-execution. That is the founder's second quote, satisfied literally.

The machinery is `_apply_prose_fix` and `_verdict` in `scripts/adjudicate_by_repair.py:150,194` — counterfactual repair pointed in the other direction. No new tool.

**The honest cost.** I measured how far this replays free, and the answer is: barely. Of the 390 archived entries carrying an EXTEND, 283 have a `proposed_fix`, 17 have a `falsifier_code`, and **11 have both**. Eleven pairs is not a validation. The archived EXTENDs carry no falsifiers because the prompt never asked for one. So this needs a prompt change and **one live run**. I am not going to pretend otherwise.

**On duplicate counts informing priority — the founder asks what consumes the signal and when.** My answer is: build the counter, connect it to nothing, and here is a sharper reason than "the signal is thin." Under a tool-gated MERGED, a merge count becomes a count of *tool-verified identity*. The archive's 772 merges are vote-verified identity, on a rule measured at 64.4% false-merge. Those are not the same quantity, so the archive cannot calibrate the future counter — not weakly, not at all. CC2's "build the counter, do not interpret it" is right; the thermometer isn't just in a fire, it's measuring a different substance.

---

# Q3. Software and STEM in one schema

**One status set serves both. You do not need a discriminator, and the state everyone says is missing is not a state.**

Every panel said the same thing: Bugzilla has no state for "the reported behaviour is correct and the specification is wrong." That claim is false about Bugzilla, and the falseness is the answer.

Bugzilla handles precisely this case, and not with a status. It handles it by **changing the ticket's target** — reassigning product/component — and by **linking** via `depends_on`/`blocked`. A bug filed against the renderer that turns out to be a defect in the layout spec is not given a new resolution. It is moved to the component that owns the spec, and the original is marked as depending on it.

That maps exactly. A CDSFL finding is not a proposition; it is a pair *(claim, target)*. "The finding was right and the target was wrong" decomposes without a new status:

- The falsifier fired → `CONFIRMED`. Correct, and unchanged.
- The proposed repair does not close it, because the error is not in this document but in something it relies on → **retarget**. File a child finding against the upstream target — the cited paper, the shared constant, the depended-on claim — and link the parent with `blocked_on`.
- The parent sits `CONFIRMED` + `blocked_on: [child]`. It has not been fixed and is not pretending to be. It is not converged, not counted as settled, and the reason is legible.

This is why one schema serves both domains: the difference between a software bug and a STEM claim is not a difference in *lifecycle*, it is a difference in **who owns the target**. In software the maintainer owns it, so a repair lands. In STEM the target may be owned by the literature or by the world, so the repair lands somewhere upstream or nowhere. The state machine does not need to know which. It needs a **target field with an owner**, and a `blocked_on` edge — both of which Bugzilla has and CDSFL does not.

There is one genuinely irreducible case: the target is the world, no upstream exists, and the claim is simply false. That is `CONFIRMED` + `blocked_on: []` + `unrepairable`. In Bugzilla's vocabulary it is `WONTFIX` — the defect is real and will not be fixed. It is not a missing state. It is a `CONFIRMED` finding that will never reach `CLOSED`, and the system should say so plainly rather than invent a status to make the queue look empty. **A permanently open critical is a correct output, not a failure of the schema.**

---

# Q4. Attack or extend CC1's answer

CC1's claim: every status change must carry its reason, adjudicator and timestamp at the moment it happens.

**I cannot attack it. It is right, and it is understated.** I ran the test that settles it.

Across the CONFIRMED entry-instances in my sweep: **1,002 of 1,232 carry no field of any kind identifying what decided them** — no `falsifier_verdict`, no `verified`, no `resolved_by_routing`. And of 772 MERGED instances, **772 have no surviving justification**: every MERGE verdict's evidence was overwritten with the synthesised literal `merged_into=...`.

So the archive cannot answer, for any archived run, whether a CONFIRMED was tool-established or vote-established. That is not a future interface problem. It means **the project's central claim — findings are confirmed by tools, never by votes — is currently unauditable on its own record.** Q4 is not about a UI. It is about whether the founding principle is checkable.

**Three extensions.**

*(a) The chokepoint already exists, which makes this small.* `:1144` is the single status write in the runner. A transition log is an append in `resolve()` and a required argument. Not an architecture change.

*(b) Reason must be a typed enum, not a string.* The project already has three ad-hoc reason strings — `close_reason` (288 entries), `hil_reason` (89), `withdraw_reason` (8) — covering three transitions out of dozens, in prose, unqueryable. Free-text reasons produce the same archaeology one layer down. The record should be:

```
{to, from, round, wall_clock, mechanism, actor, evidence_ref}
```

`mechanism` ∈ `{FALSIFIER_RUN, COUNTERFACTUAL_REPAIR, FIX_VERIFICATION, MODEL_ATTESTATION, HUMAN, TIMEOUT_SWEEP}`. `actor` is a model id, a script path, or a human. `evidence_ref` points at the stored artefact — falsifier source, exit code, diff, target hash.

*(c) The field that makes the whole thing enforceable is `mechanism`.* Once it exists you can write one test: *no entry may reach `CONFIRMED`, `CLOSED` or `MERGED` with `mechanism = MODEL_ATTESTATION`.* That is the founding principle, expressed as an assertion a machine checks every run, instead of a directive a model is asked to honour. Nothing else in this review converts "tools decide, not votes" from a policy into a constraint.

*(d) CC1 omits the timestamp's second job.* Wall-clock alongside round index is what lets a future reader distinguish a transition made during the run from one made by a post-hoc sweep script. Several archived transitions came from sweeps (`resolved_by_sweep`, `withdrawn_by_sweep`) and are currently indistinguishable from live decisions.

---

# Q5. Human and machine comprehensible, simultaneously

**There is no real tension, and the two-representation answer is the wrong framing.**

Gemini's proposal — a natural-language layer for humans over a typed payload for machines — creates the exact defect it is meant to solve, because two representations drift. Then a researcher reads the prose and the runner reads the JSON and they disagree, and nothing detects it.

The constraint that actually resolves it: **one typed record, rendered.** The record is structured. The human-readable form is generated from it, never stored alongside it, never editable. Rendering is a pure function of the record. Drift is impossible by construction rather than by discipline.

What that constrains, concretely:

1. **Every field a human needs must be a field, not prose.** If a reason lives only in a sentence, rendering cannot produce it and querying cannot find it. This is why `mechanism` is an enum.
2. **Evidence is referenced, not embedded.** The entry stores a pointer to the falsifier source and its exit status. The rendering shows the code; the runner checks the exit status. Same object, two readings.
3. **No field may exist that only the renderer uses.** A `summary` string that the runner ignores is a second representation wearing a disguise.

The project already does this correctly in one place and the founder should notice it: the round prompt is *rendered from the registry* (`:1305` onwards). Models read English generated from typed state. That is the pattern. Extend it — do not invent a parallel one.

**The one genuine tension**, since the question asks: rendering is lossy in the direction humans want. A researcher wants "why is this still open?" and the record answers with a transition list. That is a rendering problem — a `blocked_on` chain walked and printed as a sentence — not a schema problem. It costs nothing today provided the edges exist. Which is the Q3 answer arriving from the other side.

---

# What to build, defer, and drop

**Build first — free, validated by replay, and it unblocks everything else.**

**1. The transition log in `resolve()`.** One function, one append, one enum. Then the test that forbids `MODEL_ATTESTATION` from writing `CONFIRMED`/`CLOSED`/`MERGED`. This is first because without it Q1's status set is unenforceable, Q2's counts are uninterpretable, Q4 is unaddressed, and the project's founding principle stays unauditable. Replay the archive through it to see what can and cannot be reconstructed — my prediction is 1,002 CONFIRMEDs come back `mechanism: UNKNOWN`, and that gap is itself the finding.

**2. Wire `adjudicate_by_repair` to the merge site.** `RUNWAY_to_BR2_2026-08-18.md:158` states `target_path` is in scope at the calling function — one argument, not an architecture change. Make it the only writer of MERGED. Validate on the 85 already-labelled pairs before any live run; the labels exist, so this is free. Everything the tool cannot decide rests at `WITHHELD`, which is already the code's behaviour at `:1994-1998` — it just needs a status name.

**3. Add `blocked_on` and a target-owner field.** Free. Answers Q3 without a new state and gives Q5's rendering something to walk.

**Then, and it costs one live run — price it honestly.**

**4. The EXTEND handler.** Prompt gains a falsifier slot on EXTEND; runner gains the three-step subsumption check. This is the only item that turns the tracker into an instrument for *assembling fixes*, which is the founder's stated goal. But only 11 archived entries can replay it, so it cannot be validated free. Fold it into whichever live run is next rather than buying a run for it.

**Defer.**

The discussion-board layer, per the existing ruling — and note that items 1, 3 and 5 make it a read-only view, which is the whole ask in Q4. Also defer any consumer of duplicate counts, for the reason in Q2: the archive measures a different quantity.

**Drop.**

- **The `DUPLICATE` status.** Never written, in eleven filters. Collapse into `MERGED`.
- **`cc2_manager.py:1152-1163` and the four `MERGED` writers in `reference_runner.py`.** Dead vote-based merge paths that read as current code.
- **The `"Reversion available"` string at `:1864`.** It promises a human a safety net that structurally cannot exist. Either build unmerge or delete the sentence; do not tell a reviewer a decision is recoverable when `:1860` short-circuits on MERGED.
- **G7 merge arbitration.** It is 3-of-5 voting on identity, which the 64.4% false-merge measurement says is not evidence.
- **Gemini's canonical-AST-hash keying.** It requires a formaliser that reliably parses arbitrary STEM prose into canonical ASTs. That does not exist, Gemini flagged it `[SPECULATIVE]` itself, and this project has already refuted one panel-designed identity mechanism on its own archive (FELM, p = 0.71). Do not build a keying scheme whose prerequisite is unbuilt.

---

# My strongest falsification of my own answer

**The EXTEND mechanism may return SUBSUMED by construction, exactly as counterfactual repair was warned to return SAME by construction on prose.** CC2 flagged this on 19 August (compendium, panel 2 Q2): the 18/0 asymmetry is a live warning that patch-equivalence methods collapse on text. If a parent's fix is a broad rewrite of a passage, *every* extension's falsifier will stop firing after it — not because the fix handles the edge case, but because the passage the falsifier reads is gone. Then step 2 fires universally, step 3 never fires, and the whole "fixes get demonstrably better" mechanism reports success while measuring nothing.

**What would settle it, and it is already on the tracker.** Item 4.1 — a generated control target carrying two known-distinct defects with a plausible common repair. If the EXTEND handler calls SUBSUMED on a control where the extension is known not to be covered, the mechanism is dead and Q2's answer collapses to "the active pool drains," which is real but much smaller. That control costs scripting only. **It should run before the live run, not after**, and if I am wrong about EXTEND, item 4 above drops out and items 1–3 stand unaffected.

**A second, smaller exposure.** My claim that one status set serves both domains rests on retargeting being available. If a STEM finding's true upstream target is not in the corpus — a paper the ouroboros cell never retrieved — then `blocked_on` points at nothing and the finding rests `CONFIRMED` forever with no legible reason. That is survivable but it means the retargeting answer degrades to "permanently open" in exactly the cases the founder cares most about. I have not measured how often that happens and cannot from the archive, because no finding currently carries a target owner.

**On whether any question is malformed.** None is. But Q1's framing of the vote problem points at the wrong axis, and I have said so: index the tool requirement to reversibility, not to identity-versus-existence. Voting on existence in a non-destructive routing state is acceptable and the record simply has to say that is what happened.

---

## Fable 5

- returned: **yes**
- elapsed: 372.4s
- length: 15,745 characters

### Verbatim

Review complete, 2026-08-21T13:51:12+01:00. Everything below that carries a file:line was executed or read in this session, on this machine, at HEAD (`247ee33`). Nothing was modified.

## Verification of the brief, and one finding it missed

The compendium's measurements reproduce. My sweep of every `bench/logs/*/runner_state.json` (2500 entries — wider than the compendium's 2030 because it includes `latest`/repeat directories) gives: CLOSED 914, CONFIRMED 569, OPEN 555, MERGED 296, UNCONFIRMED 137, REFUTED 18, CONTESTED 11, **DUPLICATE 0**. Verdicts: CONFIRM 5501, MERGE 829, CHALLENGE 766, **EXTEND 219**, REOPEN 26. `grep -c '"EXTEND"' bench/reference_runner_v2.py` → 0. `resolve()` writes exactly `status`, `last_status_change_round`, `merged_into` and nothing else (`reference_runner_v2.py:1144-1147`). No `resolve(..., "MERGED")` survives in v2 — only comments recording the removal (`:1911`, `:1967`, `:2001`).

**F1 — the "no code path writes MERGED" claim is true of v2 only.** `bench/reference_runner.py` (v1, 190 KB, last touched 28 July) still merges by vote at `:790`, `:828`, `:832`, `:2311`. I ran `bench/tests/test_runner_status_transitions.py`: **31 tests pass**, including `test_same_target_consensus_merges` (two votes → MERGED into unregistered `C0002`), and `test_single_merge_on_small_panel_hil_flagged` (one vote → MERGED). The suite imports `bench.reference_runner`, not v2 (`test_runner_status_transitions.py:13`). I found no non-test importer of v1 and no deprecation marker in its header.

**F2 — inverted test pressure.** The v2 withhold path (`merge_candidate_of`, `merge_blocked_reason`, `:1902-1908`, `:1996-2005`) has **zero test coverage** — no test anywhere in `bench/tests/` mentions those fields or "WITHHELD". The founder's no-voting ruling is enforced by code with no tests, while the behaviour the ruling abolished retains 31 green tests. Anyone regression-testing sees green and learns the wrong thing.

**F3 — evidence amputation.** `add_verdict` stores `evidence[:200]` (`:1106-1109`). This matters for Q4 below: a "why" channel built on 200-character stumps cannot be rebuilt later.

---

## Q1. The status set

The current machine conflates two axes: the epistemic state of the claim and the disposition of the record. Bugzilla itself never did that — its design is a **status × resolution pair**, and every panel that "broke the analogy" broke it because they collapsed the pair into statuses. Restore the pair, add one field, and the machine serves both domains.

**Statuses** (who may write each is the column that matters):

| Status | Meaning | In | Out | Evidence required | Authority |
|---|---|---|---|---|---|
| OPEN | filed, parsed, registered | registration | any below | well-formedness only | model files |
| CORROBORATED | ≥N independent models attest existence | OPEN | CONFIRMED, CONTESTED, UNCONFIRMED | counted CONFIRM verdicts | model — **scheduling signal only, never shown as SETTLED** |
| CONFIRMED | the runner independently re-executed the finding's falsifier and it fired | OPEN/CORROBORATED/CONTESTED | CLOSED, CONTESTED | tool execution record | **tool only** |
| CONTESTED | unresolved CHALLENGE against a confirmed entry | CONFIRMED | CONFIRMED, REFUTED | a CHALLENGE verdict | model may raise; only tool/HIL resolves |
| CLOSED (+resolution) | terminal; see resolution field | CONFIRMED | REOPENED | per resolution, below | **tool or HIL only** |
| REFUTED | tool shows the claimed defect absent (falsifier quiet on faithful re-run; crash ≠ quiet, per the discrimination control's own distinction `:2178-2196`) | any live | — (REOPEN with new falsifier) | tool execution record | **tool only** |
| MERGED | identity established; folded into target | OPEN/CORROBORATED/CONFIRMED | — | counterfactual repair, both directions agreeing, or exact outcome-tier match | **tool only**; model MERGE verdicts land as `merge_candidate_of`, exactly as v2 now does |
| UNCONFIRMED | aged out without decision | OPEN/CORROBORATED | reopenable on new evidence | none — it is the absence of evidence | mechanical timer |
| REOPENED | CLOSED challenged with new evidence | CLOSED | OPEN | a **runnable** falsifier beyond what the pipeline checked, else it is a vote | model proposes, tool admits |

**Resolution field on CLOSED:** `FIXED` (artefact repaired, verified in sandbox — `bugzilla_loop.attempt_close`, tool), `TARGET_REFUTED` (the target's claim is false about the world; the finding stands as a permanent negative result — tool where a falsifier executes, **HIL where the claim is empirical**), `REFERENCE_FAULT` (see Q3 — **HIL only**), `INSTRUMENT_FAULT` (the falsifier, not the target, was wrong — the discrimination control's `NO_DISCRIMINATION` outcome, `:2144-2152`, already detects this), `OUT_OF_SCOPE`.

**Drop DUPLICATE entirely.** It appears in eleven terminal-status sets and one prompt, is written by nothing, and never will be: "duplicate" is a *relation*, MERGED is the *state* that records it. A dead value in a state machine is not neutral — it is the value a future contributor will one day write to, bypassing every merge guard. Delete it from the sets at `:1215`, `:1233`, `:1439`, `:2972`, `:3625`, `:3754`, `:3903`, `:4263`, `:4292`, `:9158`, `:9474`, `:9679` and from the prompt's state-machine block.

**Is OPEN → CONFIRMED a vote? Yes.** `:2100-2113` counts distinct confirm models against a severity-based threshold (`min(2, panel)` at sev ≥ 0.7, else 1). That is counting model assertions — a vote by the founder's definition. **The existence/identity distinction is real, but it is a risk asymmetry, not a licence.** An identity vote is destructive: it removes an entry from every gate count, and A.6 shows what that did. An existence vote is provisional and reversible (CONTESTED exists). So the rule that preserves both the distinction and the founding principle: **existence-votes may schedule; only tools settle.** Concretely: rename the current vote-driven state CORROBORATED, and reserve CONFIRMED for the runner having re-executed the falsifier itself. The re-execution machinery exists; the discrimination control exists and is currently a strict no-op because nothing supplies corrected copies (`:2160-2167`).

**Where HIL is the only possible arbiter:** the five `INDETERMINATE_*` outcomes; empirical world-claims with no locally executable falsifier; merge deadlock (D4, already escalates, `:1946-1953`); REOPEN evidence outside pipeline scope; and every `REFERENCE_FAULT` ruling, because "the spec is wrong" is a judgement about intent, and intent is not tool-measurable.

---

## Q2. Ledger versus instrument

Four concrete consumers, in cost order:

1. **Pool drainage** — already real. Terminal statuses leave the γ novelty series and the gate counts (`:4134-4136` region, `open_crit_high_count` `:1156`). This is the one instrument function that works today.

2. **EXTEND accretion — the cheapest unbuilt instrument, and it is precisely the founder's ask.** "Gathering and assessing fixes... to improve/add to a better solution" describes a canonical entry that *accretes*: original finding + extensions + candidate fixes + falsifiers. Models supplied the material 219 times; the schema asked them to (`:5224`, `:5233`, `:5246`); nothing reads it (zero `"EXTEND"` literals). Consumer one: append each EXTEND as a scoped child on the canonical entry and render it in the next round's registry block — the following round's fix proposals then target the enriched statement. Consumer two: `attempt_close` tries the composite fix. Different models thereby contribute independently to one solution — which is the second founder quote, implemented, with the merge question not even involved.

3. **Corroboration count orders the verification budget.** Sandbox verification is rationed per round (`BUGZILLA_PER_ROUND_LIMIT`, `:2044-2046`). Today the queue order is arbitrary. Spend the ration on the most-corroborated findings first; same for the HIL queue. Consumed inside `_update_finding_statuses`, every round, zero dispatch. Do **not** put counts in prompts or severity until a live run validates it — Gemini's anchoring objection (compendium `:725`) is correct and the panel consensus on this held.

4. **The falsifier battery as a regression suite.** Every CONFIRMED finding's falsifier is a permanent test. When `attempt_close` verifies a new fix, also re-run the falsifiers of every other CONFIRMED/CLOSED finding on the same target: a fix that resurrects an old defect fails. This is the ledger *becoming* the instrument — the accumulated record checks each new answer mechanically. All machinery exists; it is a loop over stored falsifiers.

---

## Q3. One schema for software and STEM

One status set, **two discriminator fields** — and this is Bugzilla's own architecture, not a departure from it. The panels' shared break-point ("a bug is a defect in a controlled artefact; a STEM claim can be wrong about the world") is real but it is not a state-machine problem. It is carried by:

- **`resolution`** on CLOSED (Q1): `FIXED` is the software-shaped outcome; `TARGET_REFUTED` is the STEM-shaped one. Note "the finding was right and the target was wrong" — as literally worded — is *not* the missing state: it is CDSFL's normal success, `CLOSED/TARGET_REFUTED`. The founder rightly called the earlier phrasing ungrammatical; precision dissolves half the puzzle.
- **`fault_locus`** ∈ {TARGET, REFERENCE, INSTRUMENT, FINDING}: *where the defect actually lived once settled.* The state nobody has is `fault_locus = REFERENCE`: tools confirm the accused behaviour is real, and the fault sits in the reference the finding measured against — in software, the spec; in CDSFL runs, the answer key or assigned ground truth; in open STEM, the field's consensus assumption. That last case is the most valuable outcome science produces and must be a first-class terminal record, not a failed finding. It is HIL-adjudicated by nature. `fault_locus = INSTRUMENT` is already half-built: `NO_DISCRIMINATION` (`:2148`) is exactly "the machinery highlighted an established truth as a fault", in the founder's own words quoted in the code.

No forked state machine, no second schema. A researcher filters on `fault_locus`; the runner ignores it for gating.

---

## Q4. Data model now, interface later

CC1's answer — reason, adjudicator, timestamp at the moment of change — is confirmed necessary (`resolve()` records none of them, `:1144-1147`) and insufficient. Four extensions:

1. **Append-only transition log, not annotated status.** `resolve()` overwrites in place, so an entry that went CONTESTED → CONFIRMED → CLOSED retains no trace of contest. The record per transition: `(from, to, round, wall_clock, adjudicator, evidence_ref, reason)`. Status becomes a derived field (last entry). Every illegal historical transition then becomes detectable by replay — the interface later is literally `render(log)`.
2. **Adjudicator is typed and versioned:** `model:<id>` | `tool:<name>@<version>` | `hil:<initials>`. A merge decided by counterfactual-repair v1 versus v2 must be distinguishable at retabulation, or the 4.1 control result cannot be applied retroactively.
3. **Evidence by reference, not amputation.** `evidence[:200]` (`:1106`) destroys exactly the material a discussion view would display. Store full text in a sidecar keyed by hash; truncate only at render.
4. **Canonical IDs only in machine records.** The A.4 inversion (`Codex:Codex_F001` vs `Codex:F001`, merge → spurious CONFIRM, 43 of 68 modern MERGE lines recast) was caused by regex-recovering references from prose. Rule: regex extraction lives at the parser boundary and nowhere else; every stored cross-reference is a resolved canonical ID or it is not stored.

The withhold path already does per-decision reason-recording correctly (`merge_blocked_reason`, `:1902`, `:1997`) — generalise that pattern to every transition rather than inventing a new one. Backfill by archive replay where the response files permit; where they don't, record `adjudicator: UNKNOWN` honestly rather than reconstructing.

---

## Q5. Human- and machine-readable simultaneously

No fundamental tension. The typed payload is the record; the prose is a derived rendering. Three rules make it true rather than aspirational:

1. **One-way flow.** Never parse a rendering back into structure. The system currently violates this — `_resolve_merge_source` regexes canonical IDs out of free-text evidence (`:1533-1545` region) and that single violation produced the duplicate-into-corroboration inversion. The verdict grammar is the machine channel; prose is commentary attached to it.
2. **Regenerability.** No information may exist only in prose. Test: `render(payload)` is reproducible; nothing ever needs `parse(rendering)`.
3. **One source, two readers.** The per-round registry block is *already* a machine-to-model rendering — models and researchers should read views generated from the same payload, so drift between "what the panel was told" and "what the record says" (A.5's contradiction: told "folded", reality "pointer") becomes impossible by construction.

The deferred discussion board is then comments attached to transition-log entries. Payload untouched; the interface is a read-only view, as the brief hoped.

---

## Recommendation

**Build now, in order** (all validated by archive replay, no live spend):

1. **Transition log + typed adjudicator + evidence-by-reference** (Q4). Prerequisite for everything else and for the eventual interface.
2. **Wire counterfactual repair to the merge site** (RUNWAY FW.5 — one argument; `target_path` in scope at the `:8132` caller) **with fold-on-merge**: transfer verdicts, take max severity, append source description. Without fold, MERGED remains a delete-with-pointer (A.5/A.8). Gate SAME-on-prose behind the 4.1 two-known-defects-common-repair control, which CC2 correctly promoted to blocking.
3. **EXTEND consumer** (Q2.2). Cheapest instrument win in the project.
4. **CORROBORATED/CONFIRMED split** + corroboration-ordered verification queue (Q1, Q2.3).
5. **Housekeeping this audit adds:** quarantine or clearly mark `reference_runner.py` v1 as legacy and retire the 31 tests pinning vote-merges (F1) — or they will one day be "fixed" back into v2; write withhold-path tests (F2); delete DUPLICATE from the eleven sets.

**Defer:** prompt-visible counts; severity/γ coupling; discussion-board UI; any live run purely for this design.
**Drop:** DUPLICATE as a status; the "Reversion available" wording (survives only in v1 and its tests); model-vote merging in any form.

## Strongest falsification of this answer

The CORROBORATED/CONFIRMED split assumes falsifier re-execution is decisive often enough to drain the pool. Measured decisiveness in the record is 41.9% on markdown and 16.7% on Python (compendium, panel 2). If most archived CONFIRMED entries' falsifiers re-execute non-decisively, findings pile up in CORROBORATED, CLOSED becomes rare, and the system stalls — recreating the very pressure to let the vote settle things. **This is checkable for free before building:** replay the stored falsifiers of all 569 archived CONFIRMED entries and measure the decisive fraction. If it is low, the design needs either a much larger HIL budget than planned or a weaker CONFIRMED evidence bar — and that weakening is where the whole scheme would bend. Secondary risk: fold-on-merge with max-severity lets one wrong merge *inflate* a target above the gate threshold — the mirror of A.5; acceptable only because the transition log makes it visible and reversible, which is itself a reason item 1 must land before item 2.

None of the five questions is malformed. Q3's phrasing was, and defining it precisely answers it.

---

# PERTURBATION AS A GENERAL INSTRUMENT

## CC2 — Claude Opus

- returned: **yes**
- elapsed: 485.2s
- length: 12,465 characters

### Verbatim

Every number in the brief reproduces exactly. Three things in it are wrong, and one of them is load-bearing.

## What I verified

**The brief's statistics: all confirmed.** From `experimental_notes/data/adjudication_by_repair.json`: 133 pairs, 252 directional attempts (266 minus 14 from the 7 `NO_BASELINE` pairs), strict bidirectional 33/133 = 24.8%, no-applicable-fix 74/252 = 29.4%, fix-failed-own-falsifier 44/252 = 17.5%, combined 46.8%.

**Never executed: confirmed, and worse than stated.** 47 archived `*_report.json` files, zero mentions of discrimination or `corrected_copy`. 43 configs parsed, zero carrying either key.

## Three corrections

**1. `discrimination_control_ask` is a dead flag.** AST over `reference_runner_v2.py`: line 593 is the definition and there is no other site. It is never read. `discrimination_control_blocks` is read once, at `:3001`. So "the correct setting for `_ask`" has no answer — setting it does nothing. What actually drives the ask is a default parameter: `_gate_falsifier_directive(model_cdsfl)` at `:5529` takes `ask_corrected_copy=False`, so the **main panel is never asked**. Only the routing path (`:3179`, `:3196`) asks, unconditionally. That is why zero corrected copies exist.

**2. The incumbent is unwired too.** `reference_runner_v2.py:1978-1990` and `RUNWAY_to_BR2_2026-08-18.md:158`: counterfactual repair is not connected to the merge site, and **no code path writes MERGED at all**. The brief calls it "the method currently relied on for sameness". It is relied on in one offline script, not in the runner.

**3. The Q4 caveat is wrong for the control.** `_build_discrimination_overlay` (`:2215`) builds a symlink mirror in a temp dir and replaces one file there. The real target is never written. It runs fine on a target the runner may not modify. The caveat is true of `scripts/adjudicate_by_repair.py:219`, which does `target.write_text(patched)` on the live file.

## The finding that matters most

**12 of 23 strict SAME verdicts rest on a failed measurement.** `_direction` (`scripts/adjudicate_by_repair.py:222-226`):

```
if v_self == "CONFIRMED":  return "FIX_INEFFECTIVE"
if v_other == "CONFIRMED": return "DIFFERENT"
return "SAME"
```

`ERROR` falls through to `SAME`. A falsifier that crashed on the patched target is recorded as cured. `C0026/C0028` is `self=ERROR other=ERROR` in **both** directions — a SAME verdict from four failed measurements and no evidence.

This is the house defect the discrimination control was built to avoid. That control keeps `DISC_ERROR` distinct from `DISC_FAILED` and documents the reason at `:2145`. The adjudicator collapses the same distinction.

Consequence: the defensible strict rate is **19/133 = 14.3%**, not 24.8%. Fourteen verdicts withdraw. It also produces the one transitivity violation in the set — C0028=C0026, C0028=C0037, C0026≠C0037 — where every C0028 edge is ERROR-derived.

**The ground truth the perturbation proposal would be measured against is contaminated.** Fix this before running any comparison.

## Q1 — does it generalise to sameness?

**Yes as a locator, no as an identity test.** The distinction is measured.

Perturbation needs a location. The only location signal on a finding is the SEARCH block inside `proposed_fix` — findings carry no `location` or `location_key` field at all (82/82 null in exp44, despite the config being named `locationkey`), and `source_ref` is empty in all 82.

The asymmetry that makes the idea work: across 218 findings in exp44–47, 153 carry a SEARCH block and **150 of those locate** in some stored version of the target — 98% of blocks that exist. But fixes cure their own falsifier only 103/147 = 70% of the time. Locating is far more reliable than curing.

On the 174 code-target attempts: repair decides 80; perturbation additionally reaches 64 (35 where the fix failed to cure but still locates, 29 where no fix applied but a block still locates); 30 remain dead with no location. **Coverage 46% → 83%.** That is the real gain, and it is large.

**What it gets wrong.** Granularity decides everything. All 10 ground-truth-DIFFERENT pairs share an imported symbol, so any perturbation at import or function granularity calls 10/10 distinct defects SAME — a 100% false-merge rate. At line granularity only 2 of 10 are substantively co-located.

The concrete example you asked for: **exp44 C0015 and C0037**, both located inside `EvidenceStore.verify_bundle`, sharing the signature line and the `errors: List[str] = []` line. Any perturbation of that function moves both.

But read their descriptions and the objection turns around. C0015: *"verify_bundle provides no cryptographic authentication because it does not validate the bundle's Merkle root against any trusted anchor."* C0037: *"verifies the inclusion proofs against bundle.merkle_root... never checks if this root matches the trusted chain's root."* C0032 says the same thing a third time. Counterfactual repair called all three pairs DIFFERENT on clean, non-ERROR evidence. **Either repair is wrong here, or "same defect" and "same patch" are not the same question.** Repair answers patch-equivalence. Perturbation answers dependence. Neither answers claim-identity, and both are non-transitive — the violation above proves the relation is not an equivalence relation, so no merge algorithm built on either is sound without an explicit tie-break.

## Q2 — gaming, and its defeat

The access-versus-dependence hole has a direct analogue, and 89.5% of archived falsifiers (153/171) sit in it: they `import bench.<target>` rather than reading it as text. A falsifier that imports the module and asserts on any module-level fact responds to a perturbation *anywhere* in the file while depending on nothing in particular.

One consolation, measured: a syntax-breaking perturbation yields `ERROR`, not `CONFIRMED` (`falsifier_verify.py:1030-1037` — `CONFIRMED` requires an `AssertionError` or a literal `FALSIFIED` token). So a clumsy perturbation is useless, not dangerous. The danger is a *valid* perturbation.

**A model optimising against this test** writes a falsifier that touches the target broadly and asserts narrowly: import the module, read a module-level constant, compute over the whole class, assert on the claim. It passes discrimination (the corrected copy changes the constant, so it goes quiet), it passes perturbation (any edit moves it), and it demonstrates nothing. The 13 hash-using falsifiers (7.6%) are the degenerate case — they respond to every byte change by construction.

**It can be detected, not closed.** The closure is a **null-perturbation control**, exactly analogous to the existing tripwire probe: perturb a location *no finding claims*, and require the falsifier to be **unmoved**. A falsifier that responds to an irrelevant perturbation is not discriminating, whatever it does on the relevant one. Two-sided, like the gamma gate: must move for its own location, must not move for a null one. This is cheap and mechanical and it is what I would build first.

It cannot be closed absolutely, because a sufficiently determined falsifier can key on the exact claimed text. But that falsifier is, at that point, testing the claim.

## Q3 — novelty

**Category error, with one salvageable piece.** "Responds to a perturbation nothing else responds to" measures *positional* distinctness — this finding depends on a region no other finding depends on. That is a real and useful signal, and it is what you should call it. It is not novelty. A finding can be at an untouched location and be a restatement of a known defect; a genuinely new insight about heavily-covered code would score zero. Perturbation cannot see the claim, only the dependency footprint. Use it for coverage-spread, not novelty.

## Q4 — cost and scope

Free at current scale and not free at pair scale. Per finding the control costs one overlay build (symlink mirror, cheap) plus three probe runs plus one measured run, against a 30 s per-run timeout. Per *pair* it is O(n²): exp44's 82 findings give 3,321 pairs. The incumbent's 0.287 s/pair is a cached figure — `_verdict` caches on (target state, falsifier), and the cache is what makes it cheap.

**Run it per-finding every round** (it is the discrimination question, and it is O(n)). **Run pairwise perturbation only at convergence**, and only over pairs already flagged as merge candidates — `merge_candidate_of` is already populated at `:1994` and is the natural work-list. Do not run pairwise per round.

## Q5 — switch it on for exp46?

**`blocks`: no. `ask`: cannot be, until the dead flag is fixed.**

Concretely, for exp46's re-run:

1. **Fix the ask first.** `discrimination_control_ask` is never read. Wire it into `_gate_falsifier_directive` at `:5529`. Without this the control is a guaranteed no-op and running it proves nothing.
2. **Leave `blocks` False.** Record-only. Blocking on a control that has never produced a single measurement, whose known hole (`:2972`) fails GREEN, would let a falsifier that discriminates nothing veto a real finding. The comment at `:3004-3012` already argues this correctly.
3. **Prediction, if you fix the ask and run it:** exp46 has 27 findings, 19 CONFIRMED, 8 routed. Under today's wiring only routed findings are asked, so you would see roughly `NO_CONTROL=11, <something>=8`. With the ask fixed, expect the majority to land `DISCRIMINATES` and a meaningful minority `NO_DISCRIMINATION` — because 89.5% of falsifiers import the target, and an import-surface falsifier goes quiet on a corrected copy for the wrong reason. That is precisely why the first run must be record-only: the first number it produces is a measurement of the *instrument*, not of exp46.

For a run whose purpose is validating repairs, record-only is not a hedge. It is the only setting that produces the evidence needed to decide whether blocking is safe.

## Recommendation

Build it, in this order, and none of it needs a model call:

1. Fix `_direction`'s ERROR→SAME fall-through. It is one branch and it invalidates 12 of 23 SAME verdicts today.
2. Wire `discrimination_control_ask`. A dead flag is worse than no flag.
3. Run exp46 record-only. Read the instrument.
4. Build the **null-perturbation control** — the two-sided test. It is the piece that addresses your actual question and the existing hole.
5. Only then consider pairwise perturbation for sameness, at convergence, over merge candidates only, at line granularity.

**On your standing objection** — this is the rare addition that *reduces* the finding count rather than growing it. It merges duplicates without needing a fix, and it disqualifies falsifiers that demonstrate nothing. Every other component here finds problems. This one removes them.

## My strongest falsification of the above

**The 46%→83% coverage gain is the weakest number I produced, and it may be largely illusory.** I measured that a SEARCH block *locates* — its text appears in some stored version of the target. I did **not** measure that perturbing that location produces a falsifier response, because doing so requires writing to targets and I am read-only. The 98% locate-rate could coexist with a low response-rate: a block that locates a docstring or a signature line may be perturbable only in ways that change nothing observable, or only in ways that break the import and yield ERROR. Given 89.5% of falsifiers import rather than read, the fraction of locations where a *semantics-preserving, behaviour-flipping* perturbation exists is unmeasured and could plausibly be under half. If it is, the gain shrinks from 37 points to under 18 and the case weakens considerably.

**The test that settles it**, and it should be run before any of this is built: take the 64 attempts perturbation would rescue, generate a mechanical perturbation at each location on an overlay, and record the verdict distribution. If `ERROR` dominates, the idea is a locator with no instrument attached and steps 4–5 should not be built.

**Second falsification.** My claim that C0015/C0032/C0037 are one defect rests on reading three descriptions, which is exactly the text-similarity judgement this project refuses. Counterfactual repair said DIFFERENT on clean evidence. I may simply be wrong, and if I am, the 2-of-10 co-location figure is a genuine 20% false-merge rate rather than the artefact I argued it was — which would make perturbation unsafe for merging at any granularity.

Nothing in the repository was modified.

---

## Fable 5

- returned: **yes**
- elapsed: 481.2s
- length: 12,531 characters

### Verbatim

All the brief's measurements reproduce. Before the answers, the checks I ran:

**Verified.** (1) The 133-pair adjudication (`experimental_notes/data/adjudication_by_repair.json`): 133 rows; SAME 23 + DIFFERENT 10 = 33 strict bidirectional = 24.8%; 252 non-null directional attempts; NO_APPLICABLE_FIX 74 = 29.4%; FIX_INEFFECTIVE 44 = 17.5%. Exact match. (2) Neither `discrimination_control_ask` nor `_blocks` appears in any of the 41 configs (superset of the 14 forward ones); both default False. (3) No archived run log contains any discrimination outcome string — only design-review dispatches mention it. It has never executed. (4) One thing the brief gets **wrong**, below, under Q4.

**One new defect found while checking (report-only, per your rules):**
`reference_runner_v2.py:593` — **`discrimination_control_ask` is a dead flag. It is never read.** The only reads of either flag are `:593–594` (definition), `:3001` (`_blocks`), and the default-value test (`test_discrimination_control.py:472`). The round-directive ask is gated on the `ask_corrected_copy` parameter of `_gate_falsifier_directive` (`:288`), and its single caller (`:5529`) passes nothing, so it is permanently False. Setting `_ask: true` in exp46's config would be accepted by `from_dict` and change nothing. This is the launcher-drop defect shape the control's own comment (`:2160–2166`) names as shipped three times — a fourth instance, in the control itself. The ask *is* live, unconditionally, in the routing prompt (`:3178`, `:3195`) and the residual sweep (`:3551`), so those are currently the only supply channels.

---

## Q1 — Sameness: yes, but only with the corrected copy as the perturbation, never an arbitrary one

The sound form already half-exists: run finding B's falsifier against finding A's **corrected copy** (A's copy has already been verified to quiet A's own falsifier), and the reverse. Both-quiet bidirectional → SAME; both-still-fire → DIFFERENT; anything else undecided. This *is* counterfactual repair with its measured failure mode removed: the corrected copy replaces the proposed fix, and the ingest already enforces what fixes never had — locates uniquely (`:2437–2445`), differs from the original (`:2434`), parses as Python (`:2450–2461`). That directly attacks NO_APPLICABLE_FIX (29.4%) and FIX_INEFFECTIVE (17.5%) — the 46.8% of directional attempts that die before deciding anything.

What it gets wrong — the two-distinct-defects-one-perturbation cases you asked for:

1. **Co-located distinct defects.** The project's own acceptance case: two different defects on `dedup` in ALG-02-REF-01.md (`convergence_location.py:335–342`), ground-truthed distinct because fixing either leaves the other standing. If A's corrected passage rewrites the shared lines, B's falsifier can change behaviour without shared identity → false SAME. An *arbitrary* perturbation (mangle the passage) is strictly worse: it destroys the shared substrate, both always respond, and every co-located pair collapses. This is why the perturbation must be a minimal targeted repair — the anchor-splice guarantees only the passage changes, which a whole-file fix never could.
2. **Plumbing coupling.** A's correction touches module-level code (an import, a constant) that B's falsifier merely traverses during setup. B ERRORs or flips for reasons that are transit, not dependence. The mitigations are already house rules: ERROR must never read as a verdict, and one direction never decides — the archive's 8 DISAGREE rows prove directions genuinely diverge.

So: sound as a **bidirectional quiet-on-correction test**; unsound as "both moved → same". The panellists' patch-equivalence objection survives in weakened form as correction-equivalence — weakened because minimality is enforced by construction rather than hoped for.

## Q2 — Gaming: the defeat is sensitivity-without-specificity, and it can be narrowed but not closed

The structural hole is that the examinee supplies **both the instrument and the stimulus**. A model optimising against this control emits a *change-detector*: a falsifier that fires iff the anchored passage is byte-present (a hash or exact-match check), plus a corrected copy with any accepted edit. Walk it through the probes at `:2706–2804`: baseline — fires, CONFIRMED ✓; determinism ✓; tripwire — output changes when the target is replaced wholesale, so `intercepted=True` ✓; corrected copy — passage changed, goes quiet → **DISCRIMINATES, green**, while testing nothing about the claim. That is the access-versus-dependence hole promoted one level: access-without-dependence becomes change-response-without-claim-dependence. The code already admits the adjacent case at `:2694–2696` ("a copy that differs but fixes the wrong claim is NOT detectable from here").

Narrowing, with machinery you already have (overlay + reverify, nothing new):

- **Invariance distractor:** a semantics-preserving edit (comment, insignificant whitespace) on which a sound falsifier must **still fire**. Kills byte-hash detectors.
- **Wrong-correction distractor:** other findings' corrected copies for the same target are ready-made stimuli the examinee didn't choose. A falsifier that goes quiet on an unrelated correction is location-sensitive, not claim-sensitive.

What survives both: a detector that normalises formatting and fires iff its specific passage is semantically unchanged. Distinguishing that from a genuine claim-test requires a probe that alters the passage while preserving the claim's truth — which requires understanding the claim, so the runner cannot synthesise it mechanically for arbitrary claims. Honest answer to the founder's larger question: **"say for sure when models truly are computing" is not achievable** by this or any output-side instrument. What is achievable is the cost inversion: raising the cheapest gaming strategy from "assert True" (free) to "build a semantics-respecting passage detector" (cost approaching the cost of doing the task). That is also the interview's actual claim, correctly read — perturbation makes cheating expensive, it does not certify thinking. Detection with asymmetric confidence, never proof — which is the Popperian frame this project already stands on, so say it plainly in any paper rather than claiming more.

## Q3 — Novelty: category error in the large sense, a genuine win in the narrow one

Perturbation response maps a finding's *support* — what it depends on. Disjoint support ⇒ distinct. That is a valid **distinctness certificate**, and it is exactly the term the mathematical appendix never defines: novel(t)/raw(t) currently rests on exact-identifier matching, and the dedup-crisis measurement showed gamma reads 0.6068 / 0.6866 / 0.7701 depending solely on the sameness rule. Perturbation-decided sameness could *be* that definition — tool-decided, no votes. That is load-bearing and worth having.

But "responds to a perturbation nothing else responds to" measures **unshared dependence, not originality**. A typo finding on an untouched line is maximally novel by this metric and cognitively nothing. Novelty-as-insight is not falsifiable from behaviour under perturbation; that boundary is non-falsifiable territory and should be stated, not papered over.

## Q4 — Cost, scope, and one pushback on the brief

Each per-finding control ≈ 5 sandbox executions (baseline, 2× determinism, tripwire, corrected run), each with up to a 120 s timeout. At typical scale (~40–80 confirmed findings/run) that is minutes of local compute — free. Pair discrimination adds 2–4 executions per pair; **scoped to merge-candidate pairs it stays free** (dozens per round). It stops being free at all-pairs: 300 findings → ~45k pairs → ~10⁵ executions, and one pathological 120 s falsifier multiplied across pairs turns hours into days. So: per-finding at CONFIRM time (as wired); pair discrimination per round on merge candidates only; all-pairs matrix, if ever, once at convergence with a per-falsifier time budget.

The pushback: the brief's "it cannot run on a target the runner may not modify" is **false for this machinery**. `_build_discrimination_overlay` (`:2216–2246`) symlink-mirrors the repo into a tempdir and splices the corrected leaf there; the real target is never touched. That constraint is true of `adjudicate_by_repair.py` (in-place edit, finally-restore) — one more reason the overlay route should carry the generalisation. The real limits are non-retargetable references (measured by the tripwire, fails loud as INDETERMINATE_NOT_INTERCEPTED) and falsifiers with non-file dependencies.

## Q5 — exp46 rerun: ask on (once wired), blocks off

- **`_ask=true` in the config does nothing today** — see the dead-flag finding above. The one-line wire is passing `cfg.discrimination_control_ask` through at `:5529`. Not mine to make; without it, "switching the control on" via config is a placebo.
- Even unwired, the rerun **will** produce the control's first live data: exp46's config has routing on (via the legacy `take_up_slack_enabled: true` alias) and `post_convergence_sweep_rounds: 2`, and both those prompts ask for corrected copies unconditionally. Sparse coverage, but nonzero.
- **`_blocks` stays False.** The blocking design is refuted twice over (the panel's access-vs-dependence finding, plus the change-detector defeat in Q2), and enabling it would settle the open CONFIRM-only founder decision by wiring — the exact thing the `:271–277` comment exists to prevent. Record mode already stamps `mechanical_fault` and escalates to HIL without touching the verdict (`:2901–2917` then `:3017`), which is the right failure direction for a repairs-validation run.
- **Prediction** [SPECULATIVE]: majority NO_CONTROL (the verbatim-anchor format will be refused at a rate at least comparable to the 29.4% fix-parse failure, likely higher at first); a visible INDETERMINATE share — NOT_INTERCEPTED from falsifiers that paste content instead of reading the file (the exp53 lesson), plus BASELINE failures from flaky falsifiers; and a small nonzero NO_DISCRIMINATION count — the C0012 class exists in the archive, and measuring its live rate is the run's actual value. If NO_DISCRIMINATION comes back zero, check the DISC_COPY_UNCHANGED and refusal counts before believing the falsifiers are all sound.

## Recommendation

The idea is right, with its scope cut down: **generalise perturbation as corrected-copy cross-discrimination, wire it as the merge tool, and adopt it as the appendix's missing sameness definition. Do not present it as a cognition or novelty detector.** It passes the founder's standing objection in the strongest available way: the merge machinery has never merged anything, the 2026-08-19 no-voting ruling froze it entirely pending a tool verdict, and this is that tool — it converts blocked merges into decided ones and false-CONFIRMEDs into flagged instrument faults. It fixes more than it finds.

Sequence: (1) validate offline first, zero dispatch — synthesise corrected copies from the 129 applicable archived fixes and check cross-falsifier response against the 33 repair-decided labels; if they disagree, the generalisation dies before it ships. (2) Wire `_ask` (one line), true for the exp46 rerun, `_blocks` false. (3) Add the two distractor probes. (4) In any write-up, claim cost-inversion and detection, never certification of computation.

## Strongest falsification of my own answer

Everything above rests on an **unmeasured supply rate**: no live run has ever produced a single accepted corrected copy. The anchor must match the target byte-for-byte; models mangle whitespace habitually; the analogous fix-parse channel failed 29.4% of the time. If live compliance is poor, generalised perturbation inherits exactly the starvation that limits counterfactual repair to 24.8% decided, and "un-freezes the merge machinery" collapses to "un-freezes a quarter of it". Second, the co-located-defect false-SAME case sits precisely in the hard-pair regime — the 133 are hard pairs by construction — so the decisive rate where it is most needed may be the worst. The offline validation in step (1) settles both for the cost of local compute; if it comes back under ~50% decided on the labelled pairs, downgrade this from "the merge tool" to "one more recorded signal" and say so.

Done: brief's measurements reproduced (one premise corrected), one new dead-flag defect reported, recommendation committed with its falsification stated. Next step is yours: rule on the offline validation and the one-line `_ask` wire.

---
