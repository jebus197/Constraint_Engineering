# The last programme measurement closed, and a guard was switched off in every domain but one

2026-10-15 23:47 BST

## What this session establishes

Arm 5, the last of the 12 programme measurements without a result, is answered on the half that can be answered, and the reason the other half cannot be answered between the 2 commits it names is itself a documented finding with a precedent. All 12 measurements now carry a result and a headline, which is the condition the study's own `closes_when` field states. The study has NOT been closed, because closing it is the founder's call and because the success criterion — 3 consecutive clean convergences — is a separate condition.

Leg 3 of the shakedown ran through the session under the monitoring protocol. The 7 board failures that were awaiting a ruling are fixed on the ruling given. 2 defects in the part of the harness that routes a finding to a checking tool were found, 1 fixed and 1 measured and left for a ruling. The cause of the non-project terminology was fixed mechanically rather than recorded.

## Arm 5: the specification reached 0 of 22 at the old commit and 22 of 22 now

**Measured from a live dispatch, not reconstructed.** A worktree was created at commit `a2a0197` (2026-09-06) and the same experiment launched there. During round 0 the composed prompt that a seat actually received was recovered from the live operating-system process listing and decoded, giving 66,852 characters. The raw capture was 70,956 characters and the arithmetic reconciles exactly: 1,368 newline tokens of 4 characters each become 1 character, so 70,956 − 1,368 × 3 = 66,852.

Against the 22 HARD blocks the project's own predicate finds in the core directive file, that prompt carried **0 of 22**, 0.0000%, 95% Wilson [0.0000%, 14.8655%], with 2 independent interval routes agreeing to 8.33e-17. Current HEAD carries **22 of 22**.

**Every control was checked rather than assumed, and one of them failed in a way worth recording.** The review target is byte-identical at both commits, 3,498 bytes, the same SHA-256. The core directive file is byte-identical, 28,183 bytes, the same SHA-256, so the HARD-block population is shared by construction. `_block_is_hard` and `_split_packet_directives` are identical as abstract syntax trees. The single composer function that DIFFERS is `_render_universal_minimal`, which is the function under test. The per-dispatch timeout was pinned to 3,600 s on both arms because the defaults differ — 900 s then, 3,600 s now — and a killed seat would read as a composer effect; measured seat times were 202 s to 213 s, so it would not have bitten.

**The second arm needed no second run, and that is a saving of about 85 minutes of the founder's machine.** The reconstruction instrument used this morning was validated against the live capture at the one commit where both exist: the reconstructed pre-repair form reports 0 of 22 and the live dispatch reports 0 of 22. An instrument that agrees with ground truth where ground truth exists may be used where it does not.

**The finding-count half is unanswerable between these 2 commits.** The baseline predates the citation-quoting repair of 2026-10-03, so a model that writes a path in backticks has the backtick captured into the path and the reviewing mechanism reports "Cited file not found". Observed live in the run at the old commit: 6 of 7 findings blocked in round 0, every one citing `bench/run_benchmark.py`, a file that EXISTS at both commits. This is the identical defect for which study run 1 was STOPPED on 2026-10-03, where 16 findings were blocked and 12 cited this same arm-5 target by its bare basename in backticks. A starved finding supply makes any convergence an artefact.

**A second confound compounds it.** The stand-in seat model also differs, and the gap is large. The baseline cannot dispatch anything but `sonnet`, because its launcher passes no model and takes the shim default. Current HEAD dispatches a mixed ladder of `claude-opus-4-8`, `opus` and `fable`, and legs 1, 2 and 3 all carry that ladder. Seat capability and composer therefore moved together.

**The run at the old commit was stopped at the end of round 0**, once the delivered prompt was captured and the remainder was established as uninterpretable for this arm. All 17 evidence files are preserved in the versioned repository. Stopping it, and closing the arm on its spec-delivery half, are judgements made on the founder's behalf while he slept; both are reversible, and the worktree still exists.

**A design defect in arm 5's own specification.** It says "same target, same seed". Neither launcher has a seed: 0 occurrences of any seed argument at either commit. So the arms could never have been seed-matched, and with 1 run per arm the run-to-run variation measured earlier today cannot be separated from a machinery effect. This does not touch the spec-delivery result, which is deterministic given the composer.

## Haiku's 3 roles: 1 of them gated, and it is gated the wrong way round

The founder asked whether restricting the classifier to code-based issues risks making it redundant in STEM experiments that have nothing to do with code, and asked for a fix. The measurement corrects the premise and then finds a defect running the other way.

**Haiku holds 3 live roles and only 1 is domain-gated.** That classifier is gated; the deduplication assessor in `bench/cc2_manager.py:489` and the literature reader in `bench/ouroboros_cell.py:724` are not, and run in every domain. Even the gated role is DEMOTED outside the software domain rather than switched off: it still made 22 classifications in a mathematics run. A documentation defect was found in passing — `bench/cc2_manager.py:15` still lists a citation-verifying role as Haiku's, while line 360 of the same file records that role as upgraded and dispatches Sonnet.

**Hole 1, FIXED.** The code-path guard refuses to move a claim the pattern matcher identified as code onto a verifier that cannot ground it, and its written rationale is entirely about CLAIM TYPE: only the cell that checks a claim against source can check a claim against the target source, the tools that cannot read source return "cannot ground claim in source AST", and demoting a true code claim off that path causes false convergence. The guard was nevertheless wired to the software domain, so outside software a code claim had no protection at all. Measured over 220 archived classifier logs and 2,273 override lines: 10 distinct findings of 333 distinct non-primary overrides were code-to-non-code demotions let through unguarded, 3.0030%, 95% Wilson [1.6392%, 5.4387%]. 8 of the 10 come from exp38 — the live experiment the guard's own comment cites as its motivation — 1 from a simulated study run and 1 from a commissioning fixture. The same move was refused 128 times in the software domain. The guard is now domain-independent. **Status: BUILT and TESTED**, 51 tests, with 2 mutations turning them red at 16 failures and 3 failures.

**Hole 2, MEASURED and NOT FIXED.** Falsifying the first fix found the second. A test written to confirm that the rescue direction survived instead refuted the belief that the rescue worked outside software at all. The mathematical guard blocks ANY move away from a `mathematical` label outside software, at ANY confidence, including the move TO a code type — which is the one destination that CAN ground a code claim. So the rescue the classifier exists to perform is reachable in the software domain only. Over the same archive: of 539 mathematical-guard block lines, 408 had a code destination, 75.6957%, 95% Wilson [71.9011%, 79.1267%] over the archive before leg 3, and 71.3322% [67.5644%, 74.8254%] after it, across 327 distinct occasions of a run and a finding as the archive stood before leg 3 landed, and 337 after it, because leg 3's own logs joined the corpus during the session.

**And it fired in leg 3 while leg 3 was running.** 5 of 12 mathematical-guard blocks in the run had a code destination, 41.6667%, 95% Wilson [19.3260%, 68.0489%], at confidences from 0.65 to 0.92. Leg 3's target is prose carrying real Python, so code claims are expected in a mathematics-domain run. This is the scenario the founder named.

The fix is one clause. It NARROWS a guard rather than adding one, so under the additive standard it needs a ruling and a named dominated property rather than a judgement. The property is whether a code claim can reach the only cell that can ground it: today, outside software, it cannot, ever. A test pins the current behaviour and inverts when the ruling comes.

## The cause of the non-project terminology, fixed rather than recorded

The founder's test of whether a fix is a fix: "Is 'the lesson is recorded' the same as saying the problem that caused it has now been fixed? Because if not you should probably also fix the cause rather than just record the symptom."

It was not the same. The cause is now mechanical: a rule in the note checker refuses a note that uses a compound technical term existing nowhere the founder can look it up, wired into both the blocking surface and the command-line report. Of the 4 terms he challenged, 3 existed NOWHERE in the project and 1 was real but undefined — the composer emits "over coherence budget" at run time while the glossary had no entry for it. Both halves are treated: coined terms are refused, and real-but-undefined terms are defined. `Coherence Budget`, `Coherence Budget Recalibration`, `Audit Observer` and `Decomposition Futility` are now in the glossary with code anchors.

**The rule had to be defended against 4 paths by which it legitimised the very terms it existed to catch**, each found by execution and each now held by a mutation. Its own explanatory comment named all 4 coined terms. The producer scripts written the same hour named them. Its own test fixtures fed it the coinages, so test files had to leave the vocabulary — a test's strings are neither something the founder can look up nor something the program emits. And the fourth appeared only once the rule worked: writing in the glossary that a mechanism "had been called `confinement guard`, which is not its name" ADMITTED that phrase as vocabulary. A line may now mark itself as naming a coinage and the vocabulary drops it, which is the only way a glossary can say "this is not what it is called" without making it what it is called.

**Validated against the actual complaint.** Run over the 2 files he annotated today, the rule flags `discrimination guard` and `paired baseline` — 2 of the 2 coinages he challenged in them — plus 3 more of the same class he did not flag. It correctly does not flag `coherence budget`, now that the term is defined.

**It earned its place on its author within the hour.** Writing this note, it refused `confinement guard` and sent me to the code, where that mechanism is named the AUDIT OBSERVER. It passes `mathematical guard` while refusing `maths guard`, because the runner emits "BLOCKED by MATHEMATICAL guard" — the naming directive enforced mechanically rather than remembered.

**The backlog it surfaced needs a ruling.** 734 instances across 243 of the project's 523 notes, 46.46%. The flagged phrases are mostly REAL mechanisms with no glossary entry. Enforcement is a ratchet: the recorded figure may only fall, and notes written from now carry 0. **Status: BUILT and TESTED**, 15 tests.

## The 7 board failures are fixed, and 1 of them is now a stronger test than the number it replaced

On the ruling "Make each suite derive its baseline from the archive rather than pin a number... Then yes, OK do it this way and test it in the next simulated run." 259 passed, 0 failed across the 5 suites.

The immune-memory suite pinned a count of 3 experiments against a memory that now records 5. The recording set is now DERIVED as the union of the suite's pre-ledger names and the memory's own ledger: the union is 5, the count is 5, and replaying all 5 reproduces the stored memory with a worst per-class difference of 0.0. The fixed figure of 0.0724 is replaced by the 2 claims its docstring actually makes. Nothing flips: the weakest fix score over 1,160 archived decisions is 0.740, and that must exceed the threshold — which a pinned constant could not notice rising, and rising past 0.740 is the only way the gate could start rejecting. And it rests on ONE observation: a single observation decayed j times has total exp(−decay × j), so −log(total)/decay is a non-negative integer exactly when it is still 1 observation. SymPy, mpmath and NumPy agree to 0.000e+00 that it is 3, consistent with the count moving from 3 to 5.

The latent-tagger equalities became subset ratchets, which is the shape this suite's own author had already built next door under the heading "the regression half of the pin, immune to archive growth". The field-envelope identity test is restricted to the derived non-adopting population, because its premise — that no archived reply carries an envelope — was falsified by the 2 free runs adopting them.

**The founder was warned this weakens them as regression detectors. On the memory's own threshold it strengthens it.** On the other 2 the loss is confined to "nothing was added", which a successful run falsifies by design.

## 2 further defects: 1 fixed, 1 partly falsified

**The concise rendering was deleting the code under review. FIXED.** Called directly on a situation packet holding 20 repeated function definitions: the full rendering gives 2,277 characters with 20 definitions and 80 indented lines; the concise rendering gave 193 characters with 1 definition and 0 indented lines. That is 2,085 characters lost, 91.5277%, and 19 of 20 definitions deleted, reaching 4 of the 5 live models. The function's docstring promises that "only presentation is modified", and for Python that promise is false, because indentation is syntax, and a repeated definition is the defect the reviewer was asked to find. Content whose presentation IS substance now passes through character for character. **A plausible fix would have changed nothing**: the code is NOT fenced, so protecting only fenced blocks would have passed its own review — proved by mutation, which turns 6 of 11 tests red. **Status: BUILT and TESTED.**

**The proven-floor claim is partly falsified.** It held that a seat's proven capacity is used as a ceiling so its observed maximum can never rise — "a ratchet that cannot climb". Measured from the history of every fingerprint revision: the simulated CC2 seat's observed maximum ROSE 3 times, 35,013 to 63,136 to 74,140 to 80,517, monotone with 0 falls, cross-checked by NumPy and SymPy. An intermediate hypothesis of mine, that the live runner only reads the figure and never writes it, was also wrong: an abstract-syntax-tree scan finds 2 assignment sites. What remains is sharper and is a design decision about paid routing: 4 of the 5 paid seats carry EXACTLY 465,206, identical to the character, unchanged for 185 days, and the 80,000-character hard floor means no dispatch can ever re-exercise or correct it. That figure is already implicated in a measured quality collapse recorded in the code's own comment.

## Leg 3: the gate refused at round 3 for the right reason

Leg 3 launched at 23:01 BST on the same target as legs 1 and 2, 6 seats on the same mixed ladder, with the severity specification deciding so that its key property can bite now that the staging defect is repaired.

At the round-3 check both sides of the convergence gate held: gamma_critical reached 1.000 and the location-keyed novel-critical series read [0, 0, 0], which is the 3 consecutive zero-new-critical rounds the gate requires. It refused anyway, on the A4 condition: 1 unverified critical-severity candidate still pending with no resolved falsifier.

**That refusal was checked against a known defect and is a true positive.** The project carries an open defect in which a SUB-critical entry can enter the A4 counter and never leave, and the counter's own wording claims a severity test its body does not perform — so the message saying "critical-severity" cannot be taken at face value. Censused from the run's own round files: round 0 produced 13 findings of which 12 carry severity at or above 0.7, while rounds 1, 2 and 3 produced 3, 7 and 9 findings with a maximum severity of 0.5 and no criticals at all. The blocker is therefore one of round 0's genuine criticals, and the gate is correctly declining to call a run converged while a critical finding remains unverified.

This is the same path leg 2 took: it declined at round 3 on a single contested finding and passed at round 4 once that finding settled. The monitoring watchdog labels the refusal as trouble, which is a false positive in its labelling — a correct refusal is not trouble.

## The runway, and the item that has waited longest

Tonight's work was preconditions and validation, not runway stages, and should not be counted as though it advanced them.

Stage 1 has 2 items outstanding. The replay of exp44 to exp49 through the repaired accounting is Stage 1's exit test, costs zero dispatch, and its instrument already exists in the repository. It is the nearest actionable item on the whole runway.

Stage 2's 3 items need 1 live run between them.

**Stage 3 is where the delay is, and it is not engineering.** 6 of its 7 runs are BUILT and NOT RUN, and all 6 are blocked on a single ruling: whether exp50, exp51 and exp52 may still be reported as blind exams, given that their articles and answer keys sat on a branch that was public for a period. That ruling was requested on 2026-08-08 and is **68 days outstanding**. Across the 555 annotations the founder has recorded since that date, none addresses it. Nothing else on the runway can substitute: Stage 3 is the remaining experimental arc, and the capstone at 3.7 is not built.

## What needs a ruling

1. The mathematical guard and the rescue direction, with 327 archived occasions and 5 live in leg 3.
2. Whether exp50, exp51 and exp52 may be reported as blind exams. 68 days, and it blocks 6 runs.
3. The 465,206 figure shared by 4 paid seats, and whether the 80,000-character floor should move.
4. The 734-instance vocabulary backlog: drain by ratchet, or sweep now.
5. Whether to close the programme of study, now that all 12 measurements carry a result.
6. Forward normalisation of model-supplied finding identifiers, which is the only honest route to a fully green board.

Written under CDSFL note standard v1.7 (26 August 2026).
