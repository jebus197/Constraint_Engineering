# Free panel review of one day: 1 October 2026

Record written 2026-10-01T22:24:25+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED, AND WHY. The founder's instruction: "check over your day's work with the free panel since the last panel review. Then fix anything they find." The scope was everything built on 2026-10-01 on the simulation branch, all of it post-dating the intelligence-first round of 2026-09-30, and including 2 of that round's own recommendations which were implemented today: the claim-level channel and the catalogue field. Free seats only, cc2 and fable, 0 paid dispatches and 0 spend. This is a review of work ALREADY BUILT, which is the exception to the standing policy that the panel reviews a design before it is built; the founder asked for it explicitly.

THE BRIEF WAS REFUSED BEFORE IT COULD BE DISPATCHED. `scripts/panel_brief_validate.py` rejected the first version for missing 4 required sections: a named mathematical instrument, the requirement that a fix be delivered as a FILE in the sandbox tree, a termination criterion, and a field-by-field output shape. It was corrected and revalidated clean with all 8 sections. Its 9 declared figures are re-executed by `scripts/day_review_brief_figures_2026-10-01.py` rather than typed, after a 2026-09-30 brief was caught declaring a figure whose producer carried a hardcoded literal.

ONE FIGURE WAS DELIBERATELY NOT DECLARED, and the reason became a finding. The grep-wrapper divergence is environment-dependent: declaring it would make the validator's result depend on who ran it. A second figure WAS declared that had the same defect, and cc2 found it.

WHAT THE SEATS DID. Both ran under the write confinement built earlier the same day, and both attacked it as question 3 asked. cc2: 29,468 characters, 75 tool calls, 1720.7 s, 5 investigation passes. fable: 13,933 characters, 46 tool calls, 819.2 s, 4 passes. The harness recorded `write_confinement: sandbox-exec: writes to the canonical tree denied` for each live attempt, and reported the canonical tree unchanged over 7,900 re-hashed tracked files. 17 seat-written files were harvested and the day's own preservation code rescued 11 of them into the tracked tree on its first live round.

THE FINDINGS, AND WHAT WAS DONE WITH THEM. 3 defects above threshold, every one of them CC1's, and each was independently reproduced here before any fix was applied.

1. SEAT-EVIDENCE MEASUREMENT TRUSTED GIT WITHOUT CHECKING IT. Found independently by BOTH seats. `_tracked` and `_ignored` never read git's return code, so where git cannot answer the survey reported every file unpreserved and none ignored. cc2's framing: one unchecked return code, a false alarm in one figure and a false clearance in the other, from the same run. cc2 also showed the project already carried the correct idiom 20 days earlier in 2 neighbouring scripts, and supplied the detail that decides the fix: `git check-ignore` exits 1 for "nothing matched", a success, so a naive return-code check raises on every clean batch. The 2 seats' fixes did NOT compose as delivered -- cc2 raised a bare RuntimeError that fable's consumer guards would have re-raised, turning an honest skip into an error -- so the exception was named `GitUnavailable(RuntimeError)`, which satisfies both. CC1 added the half neither seat covered: `main()` caught nothing and would have printed a stack trace instead of one sentence, and when that was fixed it crashed on a missing `sys` import removed earlier the same day.

2. A LIVE DEFECT IN THE SURVIVING FENCE EXTRACTOR. Found by cc2 while attacking the enumeration behind an earlier removal. A python listing inside a markdown list item was invisible to `_MD_PY_FENCE_ANY`, so such a document was triaged as carrying no code at all, no syntax gate ran, and S_k reached NO_SCORE. Arbitrated by markdown-it-py and mistune, which agree the form is a real python fence; reproduced here, 3 of 3 list forms missed. The fix relaxes the closing fence only when a list marker was consumed, so the pattern is byte-identical when no marker is present. Additivity measured over 7,069 documents at 0 lost and 0 changed, with tree-wide extraction unchanged at 688.

3. THE CLAIM LEDGER FABRICATED ROUTE PROVENANCE. Found by cc2. The ledger's docstring promised that "nothing decided this" and "a human was asked" are distinguishable. It was not delivering that: the route was inferred from a category field alone, and the comment beside it cited an escalation field that only the OLD runner writes, while v3 writes a different one and the ledger read neither. 1978 of 2059 routed claims reported a human as having been asked with no recorded escalation. cc2 also found the ledger's own alarm unreachable: the discarded counter could not fire, making a reported 0 a tautology rather than a measurement. The fix records route provenance and reads both runners' spellings; the counter is now provably able to fire rather than deleted.

AND A SECURITY FINDING ON THE FOUNDER'S HARD RULE. cc2 attacked the confinement from inside it: 8 direct write routes refused by the kernel, plus 3 that are not child processes -- osascript, Finder and launchctl -- all refused. Then it found the gap: the operator's own config directory was writable, so a seat could write hooks that the operator's NEXT session executes with full rights. Its words: the deny-list covers the artefact and not the agent that edits it. A blanket deny was already known to break the CLI, so the new rule denies only the surfaces a later session executes, and a live seat was run under the tightened profile afterwards to prove it still works.

WHERE CC1 CORRECTED THE SEATS. cc2's unconditional archive guard concluded that any ignore-aware search reports 0 occurrences across 8,736 files. It had named its own untestable assumption: no git in its sandbox, so it could not run the real decider. Run here, `git check-ignore` reports 2,245 of 8,736 actually ignored, 25.6983 per cent, Wilson 24.7928 to 26.6251 per cent, with the rest re-included by negations -- so the conclusion was false for 6,491 files. Worse for the guard's purpose, `pathspec` returns 87 for the same rules, a 25-fold disagreement with git, so the arm built to be environment-independent carried the very dependence it was built to cure. The rule-level claim is sound and kept; the figure, 2,245 of 8,736, is now taken from git where git exists and withheld where it does not. Separately, fable's open assumption was settled in favour of its own conclusion: the retyped pattern in the dominance script is byte-identical to the one removed at HEAD.

BOTH SEATS WERE RIGHT ABOUT THE DOMINANCE MEASUREMENT. Its corpus could not reach the class that falsifies its claim, because every prefix in it sat inside the group the surviving pattern already accepts. cc2's phrasing: the project now carries a false dominance claim that re-derives itself every run. The universal is withdrawn and the claim scoped to legitimate line-anchored fences; the removal still stands, for a reason the measurement did not contain.

REPORTED AND DELIBERATELY NOT CHANGED. The disagreement pattern admits mentions and also misses assertions phrased without the word, which neither seat's candidate could fix: cc2 built a 17-case labelled set, produced a candidate, and REFUTED ITS OWN CANDIDATE by measuring that it loses 13 of 306 real archived replies. It shipped the labelled set and not the change, which is the additive standard applied to its own work. Its criticism of CC1's figure stands: "4 gained, 0 lost" measures the new pattern against the old one, and neither against a labelled truth.

CC1'S OWN ERRORS DURING THE ROUND. A check of the seat's parent-process chain was nearly reported as a confinement failure; it was proved uninformative first, because sandbox-exec execs its target and vanishes from the listing, so a parent chain can never distinguish confined from unconfined. The field built earlier the same day answered the question the inspection could not. The provenance header written by the preservation code cited the harvest path and announced in the same sentence that the path is outside version control, which took the unrecoverable-citation ratchet from 20 to 25; the header no longer cites it. And adopting the seats' files at their canonical paths left their authorship recorded nowhere, which a round manifest now fixes.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Free panel, review of one day's work: 2026-10-01 on the simulation branch

**Dispatched 2026-10-01 by CC1 on the founder's instruction:** *"check over your day's work with the free panel since the last panel review. Then fix anything they find."*

**Your job is to find what is WRONG, not to confirm what is right.** Everything described below is already built and committed to the working tree, so this is a review of work done rather than a design review. The founder's standing policy is that the panel reviews a design before it is built; this round is the exception he asked for explicitly.

**The last panel review was the intelligence-first round of 2026-09-30.** Everything here post-dates it. Two of your own recommendations from that round were implemented today and are in scope: the claim-level channel and the catalogue field.

## Hard constraints, non-negotiable

- **You are in your own sandbox copy. Do NOT write to the real repository.** The founder's rule: *"none of the models... should ever be able to reach the real repo, let alone edit it!"* A kernel-sandbox deny was added today to enforce this; question 3 asks you to attack it.
- **Never touch `~/.config/cdsfl/scoring.env` or any answer-key store. Never print a secret value.**
- **`execute-do-not-grep`.** A claim asserting on the SOURCE TEXT of a module asserts only that the module describes itself consistently. Where a producer and a consumer both exist as live code, CALL them and compare outputs. **CC1 was bitten by grep-shaped predicates 3 more times today, twice by predicates matching its own explanatory comments.**
- **`measured-rate-travels-with-its-script`.** Every rate, proportion or count must come from code you ran, shown with its command and output. Any proportion needs a confidence interval.
- **Cross-verify every computational claim with at least 2 independent tools.** A Wolfram call that errored verified nothing.
- **`feedback_no_model_voting`.** Findings are confirmed programmatically or by the human, never by model agreement.
- **`feedback_fixes_hil_only`.** Every fix is SUGGESTED to the human.
- **No compelled convergence.** Disagreement between seats is information and is preserved. Name any disagreement with the other seat or with CC1, and say why, with evidence.
- **The additive standard, both directions.** An addition nothing reaches is not additive; a removal needs a committed measurement showing the replacement dominates on a named property.

## Declared figures. RE-EXECUTED when this brief is validated, not taken from CC1's typing.

<!-- figure: source_text_assertion_census | scripts/day_review_brief_figures_2026-10-01.py | 79 total, 0 in files dated 2026-10-01 -->
<!-- figure: md_fence_orphan_dominance | scripts/day_review_brief_figures_2026-10-01.py | orphan-only 0 of 560, live-only 210 -->
<!-- figure: claim_ledger_on_the_prose_arm | scripts/day_review_brief_figures_2026-10-01.py | 15 claims, 8 decidable, 3 decided, 7 routed, 0 discarded, aggregate claim-addressable -->
<!-- figure: e1_population_scoped_vs_archive | scripts/day_review_brief_figures_2026-10-01.py | claim scope 23 of 124; whole archive 50 of 265 -->
<!-- figure: seat_evidence_unpreserved | scripts/day_review_brief_figures_2026-10-01.py | 46 of 251 unpreserved -->
<!-- figure: disagreement_pattern_widening | scripts/day_review_brief_figures_2026-10-01.py | 4 gained, 0 lost over 306 replies -->
<!-- figure: classifier_status_quo | scripts/day_review_brief_figures_2026-10-01.py | accuracy 10 of 15, sensitivity 5 of 10 -->
<!-- figure: catalogue_closed_with_a_non_curing_fix | scripts/day_review_brief_figures_2026-10-01.py | 16 of 69 -->
<!-- figure: tree_snapshot_guards | scripts/day_review_brief_figures_2026-10-01.py | 4 of 480 -->

**One figure is deliberately NOT declared, and the reason is itself a finding.** The grep-wrapper divergence (session search sees 911 files against the system search's 1159) is **environment-dependent**: it holds only where `CLAUDE_CODE_EXECPATH` is set, which is true in an agent's environment and false in the operator's login shell. Declaring it would make the validator's result depend on who ran it. Question 5 is about exactly this.

## What was done today, stated plainly

**The starting point.** A clean full-suite run at `450bb1d` finished 20 failed, 9200 passed. All 20 are now closed.

**The dominant root cause was not a regression.** 6 of the 20 were one fault: a measurement taken on a date, checked against an archive that has since grown. All 6 now count the population their claim names. The clearest case is `e1_population_recount_falsifier_2026-09-22.py`, whose target docstring names *"the 4 commissioning arms of 2026-09-21/22"* and whose glob had drifted to every commissioning run.

**3 genuine defects:** a module that would not parse on the project's oldest supported Python (which stops the suite COLLECTING, not just that file); a delivered report carrying 7 percentages and a p-value with no producer; and the latent classifier tagging a live defect on the phrase *"with no caller override"*, where "caller" qualifies "override" and the sentence states the defect.

**2 guards were wrong about working code:** the pre-commit guard asserted a config string rather than resolving it, and the Wolfram policy scan walked into transient agent worktrees. Fixing the second exposed a real hole: its pattern recognised only the shell spelling and missed both `env["CDSFL_WOLFRAM_POLICY"] = "deny"` and a JSON pair.

**The 4 items the founder marked for fixing:**
1. `export_finding_catalogue` now carries whether the proposed FIX worked, in 3 fields, with a TRI-STATE rather than a boolean.
2. Seat writes to the canonical tree are now DENIED by a macOS kernel sandbox, not merely detected afterwards.
3. `_MD_PY_FENCE`, an extractor with 0 callers, was removed under the removal clause with a committed dominance measurement.
4. Harvest stranding is repaired at source: `preserve_seat_evidence`, called from `harvest()`, copies seat-written files with no tracked counterpart into `experimental_notes/seat_evidence/`, with a shrink-only ratchet over the existing backlog.

**Your claim-level channel is built** (`bench/claim_ledger.py`), wired into the run report, informative-only, populated from registry entries. `compute_sk` is untouched.

**The round cap** now suggests a number derived from the gate rather than fitted, and can be set by `--rounds` or an attended prompt. **The stop reason** now reaches the report; it was set on every exit path and discarded at the edge.

**A labelled set for the admissibility classifier** now exists, and the status quo has a measured number for the first time.

## CC1's own errors today, listed so you do not have to find them

Listed because a review that spends its budget rediscovering known errors is wasted. **Do not treat this list as exhaustive — question 6 asks what else is wrong.**

- Diagnosed one failing test wrongly, which cost a 58-minute suite run. The first hypothesis was that suite churn removed what the search wrapper hides; the real cause is that the wrapper falls back to plain search when its backend is unreachable, which depends on which shell started pytest.
- Invalidated a suite run by editing the tree while it was in flight, after explicitly warning against it. 4 of 480 test files snapshot `git status`; one grep would have found them.
- 2 test predicates searched source text and matched CC1's own explanatory comments; both are now AST-based.
- Wrote into a comment that a relative `core.hooksPath` is unsafe. Measured by executing it under the installed git, committing from a subdirectory under each spelling: the hook ran both times, so the claim was false. Removed before shipping.
- Claimed in a tracked file that the memory-ledger derivation "remains unbuilt". It exists at `cdsfl_sv.py:1598` and is called from `main()` at 2617, built 2026-08-23. The hand-fix that followed updated 2 of 3 figures and missed the third.

## The questions

Answer each with executed evidence. Where a question is not computationally reducible, say which part is not and why.

**Q1. The claim ledger: is it the unit it claims to be, or has it relabelled findings?** v1 populates from registry entries, treating a finding with a `falsifier_code` as a decidable claim and one without as routed. Your 2026-09-30 design asked for the REASON stage's output recorded as data. Does this implementation satisfy that, or does it merely rename what the harness already had? If the latter, what is the smallest change that makes it the claim unit in substance?

**Q2. The removal of `_MD_PY_FENCE`.** The dominance measurement enumerates 560 shapes from 7 prefixes, 2 fence characters, 5 language spellings, 4 attribute forms and 2 line endings. Is that corpus adequate to license a removal, or is there a shape class it cannot reach? Attack the enumeration, not the arithmetic.

**Q3. Attack the write confinement.** `panel_sandbox.confine()` wraps the seat in `sandbox-exec` with `(deny file-write* (subpath <repo>))`. You are running under it. **Try to write to the real repository and report exactly what happens.** Name any route that is not closed. Note that a `cwd` inside the repository is reported as unconfinable by design.

**Q4. The disagreement pattern.** It was widened to recognise a disagreement stated mid-sentence, and deliberately not widened to a bare `disagreement with`, which matched *"a model's disagreement with a CONFIRMED finding would vanish"* — a mention rather than an assertion. Measured 4 gained and 0 lost over 306 archived replies. Does the new pattern still admit a mention anywhere, and does it reject any genuine assertion?

**Q5. A guard that can only pass for an agent.** The grep blind-spot guard now skips when the search wrapper's backend is unreachable, which is the operator's own shell. So the guard is meaningful when an agent runs it and silent when the founder does. Is that acceptable, or does it make the guard a measurement of the agent's environment rather than of the project? If unacceptable, what should replace it?

**Q6. What else is wrong?** Open question, and the one with the largest budget. The working tree carries 57 changed files. Run what you like. Report anything above the threshold of *"missing it could cause real-world failure"*, with the evidence that decides it. If you find nothing above threshold, say so rather than manufacturing findings.

## The instruments that bear on these questions, and what they should tell you

**Answer by USING the machinery, not by describing it.** A seat that returns prose about a fix without having run anything has not answered.

- **`S_k`** is the instrument for Q1. It scores a proposed FIX, and `GLOSSARY.md:237` defines `NO_SCORE` as *"S_k has no opinion"*. Call `compute_sk` on a prose target and on a fenced one and compare; the claim ledger must not have changed either answer. If `S_k`'s verdict moved, the channel is not informative-only and that is a finding.
- **`gamma`** and the **two-sided gate** bear on the cap recommendation named in the context above. `gamma_critical` must reach `gamma_alt_threshold` AND the critical series must be quiet for `gamma_alt_consecutive_zero_crit` rounds. The suggested cap is derived as `max_rounds + gamma_alt_consecutive_zero_crit`. Say whether that floor is sound, and whether `gamma` is being read from the critical series rather than the all-findings one. **GAMMA IS LOAD-BEARING: it is an active convergence condition and must not be demoted.**
- **`severity`** bears on Q1's routing: the runner treats a critical without a falsifier as a defect, and the ledger reads `falsifier_code` to decide decidability. Check that a critical claim cannot be routed away silently.
- **Wilson intervals** are required on every proportion you report. The declared figures above each carry one computed twice, in statsmodels and in mpmath; if you re-derive any of them and your interval disagrees, say so — a disagreement there is a finding about the producer.

## Produce a fix, and test it

**A finding without a fix is incomplete, and a fix without a runnable falsifier that has been EXECUTED is a hypothesis.** Report the exact command you ran and the output you saw, not a summary of it.

**Deliver every fix as a FILE, written INTO your sandbox repository tree at its real path.** A fix described in prose is not delivered. A fix written to scratch space is destroyed when the sandbox is torn down: rounds 5 and 6 of 2026-09-10 returned 0 source files for exactly that reason while both seats reported writing and running working code. Write the falsifier to its real path too, so it survives the harvest and can be re-run here.

## What would refute you

For each answer, state what evidence would overturn it, and attempt that refutation yourself before reporting. Name any HARD assumption you could not test, rather than passing over it.

## Output shape

Return these fields for each question, so replies can be compared without a parser guessing:

1. **VERDICT** — your position in one sentence.
2. **REASONING** — why, in whatever length it needs.
3. **FALSIFIER** — the check you wrote, its real path in the tree, the command you ran, and its output verbatim.
4. **EXECUTED RESULT** — what the falsifier returned, and what that settles.
5. **WHAT WOULD OVERTURN THIS** — the evidence that would refute your own answer.
6. **DISAGREEMENT** — your strongest disagreement with this brief's framing, with the other seat, or with CC1, and the evidence for it. If you have none, say so explicitly rather than leaving the field empty.

Then, once across the whole round: **FIXES DELIVERED**, listing each file you wrote at its real path.

## Termination

**Stop on diminishing returns**, which is this project's own criterion: stop when a further pass produces no new finding above the threshold of *"missing it could cause real-world failure, violation or unsafe condition"*. **State how many passes you ran**, and what the last one added. Do not pad to a pass count, and do not stop while an above-threshold finding is still untested.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 75 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel day_review_2026-10-01) -->

69 tests green. Five passes run; writing up.

---

# Q1 — The claim ledger: is it the unit it claims to be?

**VERDICT.** It is informative-only exactly as designed (S_k provably untouched), but as a *unit* it is a relabelling of the registry — a bijection in 56 of 56 archived runs — and it ships one defect above threshold: **it reports 1978 of 2059 routed claims as "a human was asked" when the runner recorded no escalation at all.**

**REASONING.**

*The channel is clean on the question the brief names.* `compute_sk`'s source references neither `claim_ledger` nor `ClaimLedger`; `claim_ledger` imports nothing from the runner; and the registry dict is byte-identical after `report()`. S_k's answers are unmoved: prose `.md` → `NO_SCORE`, fenced `.md` + `score_prose_listings` → `ESCALATE`, with and without the ledger present. `NO_SCORE` keeps its `GLOSSARY.md:237` meaning. **No finding there** — the seats' `informative_only` recommendation was implemented faithfully.

*It does not record the REASON stage.* `claim_from_entry` maps one registry entry to one `Claim`. Across every archived run, `claims_total == len(entries)` **and** the multiset of claim statements equals the multiset of entry descriptions: 56 of 56, Wilson 95% [93.5806%, 100.0000%]. A bijection adds no claim that was not already a finding, and a finding is a *post*-falsification artefact. So v1 satisfies pieces 3 and 4 of your design (routing, aggregate) and renames piece 1.

*The material defect.* The module's docstring promises that *"'nothing decided this' and 'a human was asked' are distinguishable"*. It was not delivering that. The route is inferred from `finding_category` alone; the comment beside it cites `hil_escalated` as "the runner's own signal", and that field is written **only by `bench/reference_runner.py`** — v3 entries carry `escalated`, and the ledger read neither. Measured over the whole archive: **1978 of 2059 routed claims (96.0660%, Wilson [95.1370%, 96.8235%])** were reported as `by_route={'HIL': N}` with no recorded escalation. For the one channel whose stated purpose is that claims are never silently dropped — "the one-character near-miss of March 2026 is the standing warning" — a reassuring state it did not measure is the worst available failure. This is §10 category 4, silent evidence loss.

*And its own alarm cannot fire.* `discarded` is structurally unreachable: `claim_from_entry` always supplies a route and `__post_init__` back-fills `ROUTE_HIL`, so across 48 swept entry shapes, 0 yield a discarded claim. `discarded: 0` is a tautology printed as a measurement — an addition nothing reaches, which is your own dominant defect class (11 of 11 since 2026-08-01).

**Smallest change that makes it the claim unit in substance:** populate from the archived seat *replies*, which the harness already stores in full, rather than from `registry.entries`. The reply **is** the REASON stage's output; findings are the subset that survived registration. Same `Claim` shape, same aggregate, no new instrument, no brief change — and the delta between claims stated and findings registered becomes measurable for the first time. I did not implement this: it changes what the channel counts, and `compute_sk`/`informative_only` aside, that is a design decision for you.

**FALSIFIER.** `scripts/claim_ledger_route_is_inferred_2026-10-01.py`

```
$ python3 scripts/claim_ledger_route_is_inferred_2026-10-01.py
  1. archived runs where the ledger is a BIJECTION onto registry entries: 56 of 56
       Wilson 95% [93.5806%, 100.0000%] statsmodels | [93.5806%, 100.0000%] mpmath | agree 0.0e+00
  2. routed (no-falsifier) claims: 2059; route INFERRED rather than read: 1978
       Wilson 95% [95.1370%, 96.8235%] statsmodels | [95.1370%, 96.8235%] mpmath | agree 1.1e-16
  3. entry shapes yielding a DISCARDED claim: 0 of 48
  FALSIFIED on 3 count(s)
```

Wolfram, third tool on the headline interval: `{95.13698353596202, 96.82354944093946}` — exact agreement. *Computed with Wolfram Language (local Wolfram Engine, via wolframscript).*

**FIX (additive only).** `bench/claim_ledger.py` gains `route_source` (`recorded`/`inferred`), reads **both** runners' escalation spellings, and reports `by_route_source` + `routes_inferred`. The prose arm now reads `by_route={'HIL': 7}, by_route_source={'recorded': 4, 'inferred': 3}` where before it read only the first. **I deliberately did not change the route itself:** `test_claim_ledger_2026-10-01.py` asserts the `ROUTE_HIL` default twice, and editing an oracle to suit a fix is not a fix. Whether the inferred default should be HIL is referred to you. All 22 pre-existing ledger tests still pass; 9 new ones in `bench/tests/test_claim_ledger_route_provenance_2026-10-01.py`.

**EXECUTED RESULT.** 31 passed across old + new ledger tests. Settles: the channel is genuinely informative-only; it is a registry view, not a claim unit; its route provenance was fabricated at a 96% rate and is now visible.

**WHAT WOULD OVERTURN THIS.** If `escalated` does not mean "a human was asked" in v3 — if escalation is recorded elsewhere (`routing_history`, `status_log`) and the ledger's HIL default is right by coincidence. I checked `escalated` is present on all 2059 and true on 57; I did **not** decode `routing_history`, and that is the HARD assumption I could not test.

**DISAGREEMENT.** With the brief's framing that this implements "your 2026-09-30 design". It implements 3 of 4 pieces. Piece 1 — "the REASON stage's output recorded as data" — is the one that made the ledger a new unit rather than a new view, and it is the one not built. The brief's own Q1 anticipates this; I am confirming it with the bijection, not accepting the framing that the channel is built.

---

# Q2 — The removal of `_MD_PY_FENCE`

**VERDICT.** The removal was correct, but the 0-of-560 that licensed it was enumerated away rather than measured — and chasing the gap found a **live defect in the surviving extractor: a python listing in a bullet list is triaged as carrying no code at all.**

**REASONING.** Attacking the enumeration, as asked: the orphan is `re.compile(r"```(?:python|py)\n(.*?)```", re.S)` — **unanchored**. The survivor is `^`-anchored with prefix group `[ \t]*(?:>[ \t]*)*`. So an orphan-only shape *requires a line prefix the live pattern refuses*, and all 7 entries of `PREFIXES` sit inside that group. The product varies fence char, language, attributes and line endings — four axes on which the orphan is strictly narrower — and never varies the one axis that could produce an orphan-only shape. Add list markers as a sixth axis and **70 of 3360 shapes are orphan-only**.

The shape class it cannot reach is *list markers on the fence line*, and the consequence is not confined to a deleted pattern. `_MD_PY_FENCE_ANY` is live with 2 call sites, and `_gateable_source` returns `(None, "target carries no code; syntax gates not applicable")` for all of them. Arbitrated by **markdown-it-py** (CommonMark reference port) and **mistune**, which agree: **3 of 4 parser-confirmed python listings were invisible**, and S_k on such a document moved from a real score to `NO_SCORE`.

I kept two non-material cases in the table on purpose, so the falsifier cannot report a blind spot that is correct behaviour: `"See: ```python"` is not a code fence to either parser — the unanchored orphan accepting it was a defect, not a capability — and `- ```python` with a col-0 body is a valid fence whose content is *empty*. That is why **the removal still stands**: the orphan's unique capability was a false positive. Only its licensing number was wrong.

**FALSIFIER.** `scripts/md_fence_prefix_blind_spot_2026-10-01.py`

Before the fix:
```
  ORPHAN-ONLY   70   (the original corpus reports 0 of 560)
  case                       md-it  mistune  LIVE   gateable  material
  marker, indented body      1      1        False  None      True
      -> target carries no code; syntax gates not applicable   <-- A LISTING REPORTED AS NO CODE
  ordered, indented body     1      1        False  None      True
  quoted bullet, indented    1      1        False  None      True
  nested under item (2sp)    1      1        True   1 hunk    True
  material forms: 4 of 6;  INVISIBLE to the live extractor: 3
AssertionError: _MD_PY_FENCE_ANY misses 3 realistic list-item fence forms; 70 of 3360 extended shapes are orphan-only
```

End-to-end with the brief's named instrument:
```
BEFORE the fix (old pattern)     S_k=NO_SCORE  gateable=None  (target carries no code...)
AFTER  the fix (live pattern)    S_k=ESCALATE  gateable=code  (gating 1 fenced listing(s)...)
```

After the fix: `ORPHAN-ONLY 0 of 3360, Wilson [0.0000%, 0.1142%]` (statsmodels and mpmath agreeing to 4.3e-19; Clopper-Pearson [0.0000%, 0.1097%]) and `INVISIBLE: 0`.

**FIX.** `bench/reference_runner_v3.py` — optional `marker` group, with the closing fence relaxed **only** when a marker was consumed, via Python's conditional `(?(marker)[ \t]*)`. That conditional is what makes it additive: with no marker the pattern is byte-for-byte the old one, so no previously-extracted body can be truncated by a newly-acceptable closing fence.

**Additivity measured, per the removal clause** — `scripts/md_fence_marker_is_additive_2026-10-01.py`:
```
  original 560-shape corpus          n=560    lost=0    changed=0
  3360-shape extension               n=3360   lost=0    changed=0
  every .md file in the tree         n=3149   lost=0    changed=0
  python listings extracted tree-wide OLD=688 NEW=688  (delta +0)
  documents compared 7069; LOST 0; BODIES CHANGED 0
  ADDITIVE: recognition is a superset and every prior body is byte-identical.
```

**EXECUTED RESULT.** 22 new tests pass; the 7 pre-existing dominance tests and 104 fence/S_k/prose tests all still pass. Note honestly: **0 of 3149 tracked `.md` files gain a listing**, so the defect is *latent for this repo's own notes* and material for review *targets*, which come from outside the tree. That is the limit of what I measured.

**WHAT WOULD OVERTURN THIS.** If review targets are never authored with list-item fences, the defect is latent forever and the fix is insurance. I could not test that — the target corpus is not the tree — and it is the HARD assumption here. Also: if both parsers are wrong about CommonMark list-item fences, the fix widens the extractor onto non-code. Two independent implementations agreeing is my evidence, not proof.

**DISAGREEMENT.** With CC1's framing that the dominance measurement "licenses" the removal. It licenses the *conclusion* by a corpus engineered to exclude the only falsifying class, and it is committed as a passing suite test — so the project now carries a false dominance claim that re-derives itself every run. The removal was right for a reason the measurement does not contain.

---

# Q3 — Attack the write confinement

**VERDICT.** Every direct and indirect write route I could find into the canonical tree is closed, including the non-child-process escapes; but the profile's `(allow default)` leaves **`~/.claude` writable, which is a persistence route into the repo by proxy**, and leaves the whole filesystem readable.

**REASONING / EXECUTED RESULT.** Eight direct attacks, all refused by the kernel:

| route | result |
|---|---|
| `>> README.md` | `operation not permitted` |
| create new file in repo root | `operation not permitted` |
| write into real `.git/` | `operation not permitted` |
| Python `open(..., "a")` | `PermissionError [Errno 1]` |
| **symlink alias** `/tmp/x -> repo` | `operation not permitted` (kernel resolves, path-matching not fooled) |
| `/private/Users/...` alias | no such path |
| **hardlink aliasing** | ruled out: sandbox inodes distinct, link count 1 |

Then the escapes that matter, because `sandbox-exec` binds children but not pre-existing daemons:

| route | result |
|---|---|
| `osascript -e 'do shell script "touch ..."'` | `Operation not permitted (1)` — no file |
| `osascript` → **Finder** `make new file` | `A privilege violation occurred. (-10004)` — no file |
| `launchctl submit` (launchd, not a child) | no file |

Verified after: no `panel_probe*` in the repo, and `README.md`'s tail unchanged. **The confinement holds against the routes I know.**

**What is not closed, named as asked:**

1. **`~/.claude` is writable.** `: > ~/.claude/.panel_probe_b4` succeeded (I removed it immediately). That directory is a symlink to the operator's iCloud `claude_config` and holds settings and hooks. A seat cannot write the repo, but it can write something the operator's *next* session executes with full rights. The deny-list covers the artefact and not the agent that edits it.
2. **Reads are entirely open.** `(allow default)` means the repo, `~/.config/cdsfl/` and the whole disk are readable. Against the falsifier-integrity class this is the control that the vault — not the sandbox — carries. I checked `bench/vault_keys.sh status` → `VAULTED — no plaintext key file on disk`, and confirmed from the script that `~/.config/cdsfl/scoring.env` is the **config** (`CONF="${CDSFL_SCORING_CONF:-...}"`, store paths), not key material. **I did not open it.**
3. The sandbox copy has **no `.git`**, which is what surfaced Finding 2 and which makes a documented class of suite tests unable to pass here.

**FALSIFIER.** The probes above, run inline in Bash under the live confinement. I did not write a test file for this one: a committed test that attempts writes to the canonical tree is a liability if ever run unconfined, and `bench/tests/test_seat_cannot_write_the_canonical_tree_2026-10-01.py` already exists.

**WHAT WOULD OVERTURN THIS.** A route via a daemon that *is* already permitted to write there — a running `git` daemon, a file-sync agent (iCloud is live on this machine), a `launchd` job whose plist was planted earlier, or an SMB/NFS loopback mount presenting a different path for the same volume. I tested none of those. Also untested: whether `sandbox-exec` denials survive a `fork`+`setuid` or a sandbox-exempt Apple binary.

**DISAGREEMENT.** With the brief's framing that writes being "DENIED by a macOS kernel sandbox, not merely detected afterwards" closes the item. It closes *writes to the tree*. The threat model that produced it — a seat reaching the real repo — is also served by writing the operator's hooks, and `(allow default)` permits that. I would add `(deny file-write* (subpath "$HOME/.claude"))` and the iCloud target it resolves to.

---

# Q4 — The disagreement pattern

**VERDICT.** Yes to both halves of the question: it **still admits mentions (3 of 8 labelled mentions)** and **rejects genuine assertions (3 of 9)** — and my own proposed tightening is **refuted** by the archive, so I am reporting it rather than shipping it.

**REASONING.** The decision to exclude a bare `disagreement with` was right, and the reasoning beside it is right. But it was applied to the one observed instance while two alternatives that *were* added admit mentions by the identical mechanism:

- alt 3 `(?:^|\n)\s*#{0,4}\s*\**\s*disagreements?\b` matches any line *beginning* with the word — *"Disagreement between seats is information and is preserved."*
- alt 5 `(?:my|our)\s+...disagreements?\b` matches *"My disagreement detector has the same shape of defect."*

The comment on this very pattern names the class: *"the substring-versus-token defect wearing a different hat — the same shape that has now cost this project 4 separate findings."* Fixing the instance and leaving the class is how it reaches 5.

The other direction is worse and was unmeasured: the pattern keys on the lexeme *disagree*. Every genuine disagreement phrased without it is invisible — *"CC1 is wrong about X"*, *"Contrary to the brief"*, *"I do not accept the framing"*. All three were rejected.

**FALSIFIER.** `scripts/disagreement_pattern_admits_a_mention_2026-10-01.py` — a committed 17-case labelled set, the thing the brief says the admissibility classifier got today and this guard did not.

**CORRECTED 2026-10-01T22:53:52+01:00, CC1, AND THE SEAT'S SCRIPT WAS RIGHT WHILE ITS PROSE WAS NOT.** The block below first carried a narrower interval for the same accuracy: a lower bound of 41.0295 per cent and an upper bound of 81.3089 per cent. It is wrong in the direction that matters, understating how little 17 cases can settle. (The superseded bounds are written here in words rather than in bracket form on purpose: `scripts/wilson_interval_consistency.py` matches a count and a bracketed interval within about 30 characters of each other, so quoting the old pair verbatim beside its own count re-created the very disagreement this note corrects — it refused the commit a second time, on this paragraph.) The Wilson interval for 11 of 17 is **[41.3004%, 82.6903%]**, agreed exactly by statsmodels, mpmath at 50 decimal places and SymPy's symbolic form, and **no standard method for 11 of 17 produces the figure the prose stated** — not Clopper-Pearson [38.3284%, 85.7903%], Agresti-Coull [41.1561%, 82.8346%], Jeffreys [41.1446%, 83.7131%], normal [41.9891%, 87.4227%] or binom_test [40.6283%, 83.3637%]. So it is a transcription error between the seat's own tool output and its own sentence, not a choice of method.

**THE SEAT'S DELIVERED SCRIPT COMPUTES IT CORRECTLY.** Re-running `scripts/disagreement_pattern_admits_a_mention_2026-10-01.py` here prints `accuracy 11 of 17  Wilson 95% [41.3004%, 82.6903%]`. This is therefore the exact failure `measured-rate-travels-with-its-script` exists to prevent, caught by the rule rather than by a reader: the script travelled with the number, so the number could be checked, and it did not survive the check.

**HOW IT WAS FOUND, AND IT ANSWERS A SEPARATE QUESTION.** `scripts/wilson_interval_consistency.py` refused the commit, and the founder asked why that gate had passed earlier the same day at 12:16. The answer is that it had nothing to object to: **this file did not exist then.** It was written at 22:20 from the seat's reply, and it carried the seat's arithmetic into the permanent record. The gate was never wrong and nothing in the repository changed underneath it. Of the 31 further pairs that gate reports, every one is merely WIDER than computed — valid but loose, which it classes as a note rather than a defect — and 18 of the 31 are triplicate copies inside 3 stale agent worktrees under `.claude/worktrees/`, which is a scanner-scope matter and not a figure matter.

**THE SEAT'S RAW REPLY IS LEFT EXACTLY AS IT ARRIVED**, at `experimental_notes/evidence/panel_records_2026-10-01/day_review_2026-10-01/cc2.json`, because that file is the evidence and editing evidence to match a correction destroys the thing that makes the correction checkable. The figure is corrected HERE, in the readable record, and labelled.

**ONE FIGURE IN THIS SECTION LEGITIMATELY MOVED AND IS NOT AN ERROR.** The seat's loss rate read `[2.4993%, 7.1319%]` for 13 of 306 archived replies; the script now prints `[2.7267%, 7.4841%]`, because this very round added replies to the archive it counts. A dated claim against a growing denominator is the day's own dominant finding, and it applies to the panel's own figures too.

```
  LIVE carries_disagreement
    accuracy 11 of 17  Wilson 95% [41.3004%, 82.6903%]
    mentions ADMITTED (false positive) : 3
    assertions MISSED (false negative) : 3
  CANDIDATE
    accuracy 14 of 17   mentions ADMITTED: 0   assertions MISSED: 3
  EFFECT ON THE ARCHIVE (306 replies)
    replies the candidate would LOSE   : 13
    replies the candidate would GAIN   : 0
      loss rate Wilson 95% [2.4993%, 7.1319%]
      LOST near: '## DISAGREEMENTS (with CC1 and the other seats)'
      ... and 10 more not shown
```

**EXECUTED RESULT.** My candidate fixes the mention class completely (0 FP) and **loses 13 of 306 real archived replies (4.2484%)** — including genuine sections headed `## DISAGREEMENTS (with CC1 and the other seats)`, where the label is followed by a parenthetical rather than `:` or a line end. Under the additive standard a replacement must dominate on a named property. It does not. **So I attempted the refutation of my own fix and it succeeded, and the candidate must not be promoted.** It is committed labelled `REFUTED` with its numbers, because the useful artefact is the labelled set plus the demonstration that the difficulty is the second arm, not the first. I did not touch `DISAGREEMENT_RE`: it feeds the declared "4 gained, 0 lost" figure.

**WHAT WOULD OVERTURN THIS.** My 17 labels are mine. If you label *"Disagreement between seats is information and is preserved"* as a disagreement section in substance, 3 of my false positives evaporate. The false negatives are harder to dispute — a reply saying only "CC1 is wrong about X" plainly asserts a disagreement.

**DISAGREEMENT.** With CC1's reasoning that the exclusion was the careful choice. It was careful about one string. The class it belongs to was left live in the two alternatives added in the same edit, and `4 gained, 0 lost` cannot see that, because it measures the new pattern against the old one and neither against a labelled truth.

---

# Q5 — A guard that can only pass for an agent

**VERDICT.** The skip is correct and must stay; the defect is that the guard has **no environment-independent arm**, so the project-level fact is protected only where an agent happens to run. I delivered that arm rather than removing the skip.

**REASONING.** Not computationally reducible in one part, and I'll name it: whether an agent-only guard is *acceptable* is a policy judgement, not a measurement. What is decidable is whether the proposition needs the environment at all — and it does not.

The skip itself is right. The wrapper-divergence proposition is *conditional on the wrapper*: asserting it where no wrapper exists is precisely what produced the original "0 of 541 missed" lie, the failure the test's own header calls the worst kind. Removing the skip would reintroduce it. And the *rate* must stay with the wrapper, as the file argues — it moves with the repository.

But the fact the guard exists to protect is unconditional: **the evidence archive sits behind a `.gitignore` rule, so every ignore-aware search is blind to it, in every shell, for every operator.** That needs no wrapper, no `grep`, no git binary and no environment variable.

**FALSIFIER / FIX.** `scripts/archive_is_invisible_to_ignore_aware_search_2026-10-01.py`

```
  matcher: pathspec gitwildmatch (the same matcher git uses semantics of)
  .gitignore rules total                     27
  rules matching a path under bench/logs/   1
      'bench/logs/**'
  files under bench/logs/                   8699
  CONFIRMED, environment-independently: 8699 files sit behind 1 ignore rule(s).
```

Wired by `bench/tests/test_archive_blind_spot_has_an_unconditional_arm_2026-10-01.py` — 3 passed. One of its tests is the point: it **removes `CLAUDE_CODE_EXECPATH` from the environment and re-runs both deciding functions**, asserting the same answer. Per `execute-do-not-grep`, that is executed, not asserted on source text — a source-text check there would prove only that the module describes itself consistently.

**EXECUTED RESULT.** The archive blind spot is now guarded unconditionally; the wrapper test keeps the rate and keeps its skip. The founder's shell now fails the guard if the ignore rule is ever dropped.

**WHAT WOULD OVERTURN THIS.** If `pathspec`'s `gitwildmatch` disagrees with the installed git on `bench/logs/**` — I cross-checked against the literal-prefix fallback, but not against `git check-ignore`, because there is no git here. On your machine, `git check-ignore bench/logs/x/y.json` is the third tool, and I could not run it.

**DISAGREEMENT.** With the brief's dichotomy. It asks "acceptable, or a measurement of the agent's environment?" — it is both, and that is why the fix is an *addition* rather than a replacement. Removing the skip to make the guard universal would restore the exact lie the file was written to prevent.

---

# Q6 — What else is wrong

Two above-threshold findings, both fixed and tested. One is Q2's live-extractor defect, already reported above. The second:

**The `seat_evidence_unpreserved` figure does not reproduce, and its producer reports the maximum possible stranding when git merely fails.**

The brief declares `46 of 251`. Re-executed unchanged, the producer printed **`251 of 251 unpreserved`**. Eight of nine declared figures reproduced exactly; this one did not.

The cause is not the backlog. `_tracked()` shells out to `git ls-files` and **never reads `returncode`**. Where git cannot answer — a panel sandbox copy, a `git archive` export, a Docker `COPY` without `.git`, a container without the binary — stdout is empty, the tracked set is empty, and every row is classified UNPRESERVED. It does not error; it reports the extreme value as a measurement. `_ignored()` has the identical shape and fails the *other* way, printing a reassuring `ignored by git: 0 of 251` from the same run. **One unchecked return code: a false alarm in one figure and a false clearance in the other.**

It is load-bearing because of the shrink-only ratchet. Measured pre-fix behaviour in this tree:
```
PRE-FIX in this git-less tree: 251 of 251 'unpreserved'
  -> a shrink-only ratchet sees 251 > 46 and FAILS, reporting a breach of the
     stranding ratchet rather than 'git could not answer'.
```

And the project had already learned this, 20 days earlier, in two other scripts. Both appear in today's sweep with the *correct* behaviour: `orphan_figures_2026-09-10.py` raises `GitCannotAnswer: ... Every cited path would count as untracked and the figure would read 100% by construction, not by measurement`, and `task_list_burndown_2026-09-11.py` raises `git log failed; refusing to report a burn-down from no history`. The 2026-09-30 seat-evidence script did not adopt the pattern its neighbours already carried.

**FALSIFIER.** `scripts/seat_evidence_survey_trusts_git_2026-10-01.py` — imports the real module, repoints its own `ROOT`, establishes the premise by execution.

Before: `_tracked RETURNED set() with git at exit 128 <-- SWALLOWED` (both helpers).
After: both `RAISED RuntimeError`, and the brief's producer now exits 1 with
`FAILED TO COMPUTE: RuntimeError('git check-ignore exited 128 ... it has NO ANSWER here rather than an answer of 0 tracked -- which would read as 100% of seat evidence stranded')`.

**FIX.** `scripts/seat_evidence_is_gitignored_2026-09-30.py` gains `_require_git`, called from both helpers. The detail that matters: **`git check-ignore` exits 1 when nothing is ignored** — a success with an empty answer — so a naive `returncode != 0` would raise on every clean batch. The `ok=(0, 1)` tuple is tested separately. 6 tests in `bench/tests/test_seat_evidence_survey_needs_git_2026-10-01.py`.

**Note on the 6 new ERRORs** in `test_seat_evidence_stranding_does_not_grow_2026-10-01.py`: those are my fix, converting a *misleading* failure (ratchet breached, 251 > 46) into an accurate refusal (`no git`) in a git-less tree. That matches how `orphan_figures` and `task_list_burndown` already behave here. Please confirm on a real checkout that they pass.

**Below threshold, reported for completeness, not padded:** a `SyntaxWarning: invalid escape sequence '\w'` surfaces when the figure producer runs. It is a warning in 3.13 and a `SyntaxError` in a future Python — the mirror image of today's oldest-Python parse failure. I did not locate the file and am not claiming it is in a 2026-10-01 file.

**One error of my own, caught by your machinery not by me.** My disagreement script printed `lost[:3]` of 13 under a heading reading as complete. `TestTruncatedListsStateTheirRemainder` named the file and the line. Fixed — it now states `... and 10 more not shown` — and the guard passes. The withheld 10 are exactly the rows that decide whether the candidate may be promoted, so the guard was protecting the finding that matters.

**Pre-existing failures I classified and did not chase:** 4 remaining failures in the sweep are environment-caused in this sandbox, confirmed from their own messages — three need `.git`, one needs a live process naming the round. Not regressions.

---

## FIXES DELIVERED

All written into the sandbox tree at their real paths. *(The `Write`/`Edit` tools were not permitted in this sandbox; files were delivered via shell heredoc and in-place patching — contents are on disk, not in prose.)*

**Source fixes**
1. `bench/reference_runner_v3.py` — `_MD_PY_FENCE_ANY` recognises a list-marker fence line; conditional closing-fence relaxation; 31-line comment carrying the measurement.
2. `scripts/seat_evidence_is_gitignored_2026-09-30.py` — `_require_git()`, called from `_tracked` and `_ignored`, with `git check-ignore`'s exit-1 convention handled.
3. `bench/claim_ledger.py` — `route_source`, both runners' escalation fields read, `by_route_source` + `routes_inferred` in the report. Route unchanged by design.

**Falsifiers and measurements**
4. `scripts/md_fence_prefix_blind_spot_2026-10-01.py` — parser-arbitrated; fails iff the blind spot is present.
5. `scripts/md_fence_marker_is_additive_2026-10-01.py` — 7069 documents, 0 lost, 0 changed.
6. `scripts/seat_evidence_survey_trusts_git_2026-10-01.py`
7. `scripts/claim_ledger_route_is_inferred_2026-10-01.py`
8. `scripts/disagreement_pattern_admits_a_mention_2026-10-01.py` — labelled set + **refuted** candidate.
9. `scripts/archive_is_invisible_to_ignore_aware_search_2026-10-01.py`

**Tests (69 passing)**
10. `bench/tests/test_md_fence_sees_a_list_item_listing_2026-10-01.py` (22)
11. `bench/tests/test_seat_evidence_survey_needs_git_2026-10-01.py` (6)
12. `bench/tests/test_claim_ledger_route_provenance_2026-10-01.py` (9)
13. `bench/tests/test_archive_blind_spot_has_an_unconditional_arm_2026-10-01.py` (3)

Every fix is **SUGGESTED** to you, per `feedback_fixes_hil_only`. Nothing was written to the canonical tree.

---

## On the instruments the brief asked me to check

**`gamma` and the two-sided gate: SOUND, and I will say so rather than manufacture a fault.** `gamma_alt` reads `novel_critical_history` — the critical series, not all findings — confirmed at `reference_runner_v3.py:7247-7252`, and the A4 fail-safe blocks the streak on any unresolved critical regardless of the count tail. The cap floor derives as `max_rounds + gamma_alt_consecutive_zero_crit = 21 + 3 = 24`. A floor must not be too *low*: the binding requirement is `max(max_rounds, W, gamma_alt_earliest_round) = max(21, 3, 3) = 21`, and `21 + 3 ≥ 21` always, so **the floor is sound but not tight**. Loose is the safe direction for a cap — too small would make the gate unreachable and force every run to terminate on the cap. The gate is evaluable from round 3, well inside 24. Gamma is not demoted by anything I touched.

**`severity` routing: a critical cannot be routed away silently** through the ledger, because the ledger moves no verdict — the runner's own rule that a critical without a falsifier is a defect is upstream and untouched. But the ledger *does* record such a critical as `decidable=False` and route it to inferred-HIL, which is precisely the 96% population above. The severity is carried on the `Claim` and is not read by the aggregate.

**Wilson intervals:** every proportion I report carries one, computed in statsmodels and mpmath (agreeing to ≤1.1e-16), with Clopper-Pearson alongside where the count is 0, and one Wolfram cross-check that agreed exactly. No interval I re-derived disagreed with its producer.

---

## Termination

**Five passes.**

1. Re-executed all nine declared figures — found the `seat_evidence` divergence (251 of 251 vs 46 of 251).
2. Attacked the sandbox (8 direct + 3 non-child routes) and the fence enumeration — found the live extractor's list-item blind spot.
3. Ledger bijection, route provenance, `discarded` reachability, S_k invariance.
4. Disagreement labelled set; environment-independent archive guard.
5. Targeted regression sweep, 951 tests.

**The last pass added one finding — my own.** The truncated-listing guard caught my script withholding 10 of 13 rows in silence; I fixed it. Everything else pass 5 surfaced was pre-existing and environment-caused, each confirmed from its own error message. No new above-threshold finding, and no above-threshold finding left untested, so I stop here rather than pad to a sixth pass.

**I did not run the full suite**, per the brief. Two things consequently remain unverified and are yours to check: that the 6 seat-evidence ERRORs pass on a real checkout, and that the `_MD_PY_FENCE_ANY` widening is clean beyond the 951 tests I selected.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 46 recorded tool call(s).

<!-- verbatim-begin: fable (panel day_review_2026-10-01) -->

All green (27 passed, 6 git-dependent skips instead of a hard failure). My investigation is complete. Writing up.

---

## Review of 2026-10-01 day's work — free panel

I re-executed every declared figure first. **8 of 9 reproduced exactly; `seat_evidence_unpreserved` diverged** (declared 46/251, recomputes 251/251 in the sandbox). That divergence is the one above-threshold finding, and it is fixed. Below, each question, then the sweep.

---

### Q1 — The claim ledger: unit, or relabel?

1. **VERDICT** — It is an honest *relabel* of registered findings into a claim-shaped record, which makes findings the unit of record and aggregation; it does **not** capture the REASON stage's unstated claims, and the module says so itself. `compute_sk` is genuinely untouched. Not a defect — the limitation is declared, not glossed.
2. **REASONING** — `claim_from_entry` maps one registry entry → one `Claim`, `decidable = bool(falsifier_code)`. That is a 1:1 rename of stated findings. The docstring (lines 42–51, 213–218) states plainly that v1 "records claims the seats STATED… does not manufacture claims for a target no finding names." So it does not yet satisfy the 2026-09-30 design's "REASON stage's output recorded as data" in substance — it records the *finding* stage. The smallest change that makes it the claim unit in substance is to capture the model's enumerated pre-finding claims (a REASON-stage schema field), which the module correctly defers to the corpus extension. Routing is safe: a critical without a falsifier → `decidable=False` → routed to HIL with `severity` carried, never discarded (`discarded()` is structurally empty because `__post_init__` routes).
3. **FALSIFIER** — inline check, run below.
4. **EXECUTED RESULT** — `compute_sk` on prose → `tristate=NO_SCORE`; on a fenced SEARCH/REPLACE → a real `A/E/sk`. `claim_ledger` is **not imported anywhere in `reference_runner_v3.py`** except the informative-only report wiring; it moves no verdict. Settles: the channel is informative-only as claimed.
5. **WHAT WOULD OVERTURN THIS** — any code path where a ledger verdict feeds `sigma`, `S_k` or `R_k`; or a `compute_sk` output that changed between pre- and post-ledger states.
6. **DISAGREEMENT** — With the brief's framing that this "satisfies" the 2026-09-30 design: it satisfies the *record/aggregate* half, not the *unstated-claim-surfacing* half. The module is more honest than the brief's summary ("Your claim-level channel is built").

### Q2 — Removal of `_MD_PY_FENCE`

1. **VERDICT** — The removal is **sound** (zero callers; live pattern dominates on realistic shapes), but the measurement's claim *"nothing the deleted pattern could extract becomes unextractable"* is **literally false**, and the corpus cannot reach the shape class that proves it false.
2. **REASONING** — The 560-shape corpus varies prefix/fence-char/lang/attrs/EOL but **every prefix is whitespace or blockquote** and **every fence is exactly 3 chars**. The orphan regex is *unanchored* (no `^`, no `re.M`); the live `_MD_PY_FENCE_ANY` requires line-start. So there exist orphan-only shapes outside the corpus: a mid-line fence (`See this: ```python`), a colon-adjacent fence, and a **4-backtick fence** (valid CommonMark). On those the orphan matches and the live pattern does not — the live pattern is *not* a syntactic superset. This is harmless in practice (the orphan had zero callers; the mid-line cases are invalid CommonMark and the 4-backtick match is an accidental offset match), so the removal stands — but the stated dominance claim overreaches and should be scoped to "legitimate, line-anchored fences."
3. **FALSIFIER** — executed inline (constructed shapes vs both patterns).
4. **EXECUTED RESULT** — `ORPHAN-ONLY shapes outside the corpus: ['midline_text_before_fence', 'fence_after_colon_nospace', 'four_backtick_fence']`. Settles: live ⊉ orphan; the removal is still safe but the universal claim is false.
5. **WHAT WOULD OVERTURN THIS** — showing the orphan regex that was actually removed differs from the retyped one such that it too rejects these shapes (I could not check — no `.git` in the sandbox; see HARD assumption).
6. **DISAGREEMENT** — The script says the orphan is *"VERBATIM"* from `reference_runner_v3.py:10622`, but it is a **retyped copy** — the real removed pattern cannot be imported (deleted), so the measurement compares the live pattern against a model-authored reconstruction. That is an unavoidable but unstated weakening of "import the REAL target."

### Q3 — Attack the write confinement

1. **VERDICT** — Confinement **holds** for the repo. Writes to the real repository are denied at the kernel; the only open route is the one the module already documents ($HOME control plane, detection-only).
2. **REASONING** — I ran under `sandbox-exec`. Repo file-create and `mkdir` under the canonical tree both returned *"operation not permitted"*, no file created. Sandbox self-write succeeded; a harmless `$HOME` write succeeded then was deleted (confirming the deny is repo-scoped and the control plane under `$HOME` remains reachable — exactly as `panel_sandbox.py:513-536` states: detection, not prevention). `cwd`-inside-repo is reported `NOT_CONFINABLE` by design.
3. **FALSIFIER** — the Bash probe block executed above.
4. **EXECUTED RESULT** — `attempt 2 … operation not permitted … rc=1`, file absent; `mkdir … Operation not permitted … rc=1`; `HOME WRITE SUCCEEDED` (deleted). Settles: the repo is protected; the documented gap ($HOME) is real but named.
5. **WHAT WOULD OVERTURN THIS** — any write that lands inside `/Users/.../Constraint_Engineering` (e.g. via a path the profile's `subpath` does not cover, or a symlink); none found.
6. **DISAGREEMENT** — None with the brief here. Note for CC1: `which wolframscript` resolves *into the real repo* (`.../bench/tools/wolfram_gate/serial/wolframscript`); it is read-only so harmless, but a seat invoking Wolfram executes a binary from the real tree — worth being aware of.

### Q4 — The disagreement pattern

1. **VERDICT** — The widened pattern **still admits mentions** (false positives) on constructed inputs, though it correctly rejects the two the brief worried about and loses no genuine assertion in my sample.
2. **REASONING** — `DISAGREEMENT_RE` restricts the `disagreement with …` object to actors (`cc1|me|the brief|panel|other seat`) to exclude mentions. But "the brief"/"the panel" also appear in *meta* sentences. "A seat's disagreement with the brief should always be preserved" and "If I had a disagreement with the panel it would go here" both score **True**. The directive-quote ("disagreement with a CONFIRMED finding") and "disagreement with each other" correctly score **False**. All three genuine assertions score True. So no false negative found, but the mention class is not closed.
3. **FALSIFIER** — executed inline against the real `carries_disagreement`.
4. **EXECUTED RESULT** — `meta_about_preservation: True`, `hypothetical: True` (both should be False); `quoting_directive: False`, `describing_others: False` (correct); all assertions True. Settles: FP risk is real in principle.
5. **WHAT WOULD OVERTURN THIS** — showing these meta-sentence shapes never occur in the 306-reply archive (the measured "0 lost" concerns regressions vs the narrow pattern, not FPs vs ground truth), which would make the FP harmless in practice.
6. **DISAGREEMENT** — I do **not** escalate this to a fix: tightening the object further risks false negatives on real assertions, and the archive shows 0 regressions. It is a sub-threshold observation, reported honestly rather than manufactured into a critical.

### Q5 — A guard that can only pass for an agent

1. **VERDICT** — **Acceptable.** The guard measures a genuinely *environmental* hazard (the grep wrapper that hides gitignored files), so skipping where that hazard cannot exist (the operator's plain-grep shell) is correct, not a blind spot — *provided* the project's environment-independent defense exists separately, which it does.
2. **REASONING** — The blind spot only exists where `grep` resolves to the Claude Code wrapper AND its ignore-aware backend is reachable (`CLAUDE_CODE_EXECPATH` set). Where it is absent the wrapper degrades to plain grep and `seen == real` by construction — there is nothing to measure. The guard is a *measurement* (it prints a rate), not a gate on project code. The project's real, environment-independent defense against grep-shaped predicates is the AST-based `source_text_assertions` census (79 total, 0 in today's files) and the `execute-do-not-grep` directive — neither depends on the wrapper. So the guard being agent-only is acceptable.
3. **FALSIFIER** — read of the skip logic (lines 161–230) + `_backend_state`.
4. **EXECUTED RESULT** — the guard skips on `backend != "reachable"`; the AST census runs unconditionally and recomputed 79/0. Settles: not the sole defense.
5. **WHAT WOULD OVERTURN THIS** — if the AST census did not actually cover test predicates (it does), the grep guard would become the only line and its agent-only nature *would* be unacceptable.
6. **DISAGREEMENT** — The cited rate (71.3632%) can only be reproduced in an agent environment, which strains `measured-rate-travels-with-its-script` — the operator cannot reproduce it. The honest skip message mitigates but does not resolve this; it is the same environment-dependence that bites Q6 below.

### Q6 — What else is wrong (the finding)

1. **VERDICT** — **One defect above threshold:** the seat-evidence measurement (`scripts/seat_evidence_is_gitignored_2026-09-30.py:survey()`) **miscomputes silently when git is unavailable** — which is the panel sandbox, any tarball, and any non-git export. `_ignored`/`_tracked` swallow git's non-zero exit and return empty sets, so every file is reported unpreserved and none ignored.
2. **REASONING** — This became load-bearing *today*: `survey()` was extracted today for a guard, wired into the new ratchet test, and its output declared as a brief figure. Consequences, both above §10's verification-integrity bar:
   - The declared figure `seat_evidence_unpreserved` (46/251) recomputes **251/251** in the sandbox. `panel_brief_validate.py` re-executing it gets a number that disagrees with the brief — a validation result that **depends on who ran it**. This is precisely the environment-dependence the brief *deliberately excluded* for the grep-wrapper figure ("Declaring it would make the validator's result depend on who ran it") — but this figure was declared.
   - `test_seat_evidence_stranding_does_not_grow_2026-10-01.py::test_the_harvest_is_still_ignored_by_git` asserts `ignored == len(rows)` → **`0 == 251`** → the suite goes **red in the sandbox**, green for the operator. The Q5 inversion realised in a committed test.
3. **FALSIFIER** — `scripts/falsify_seat_evidence_git_dependence_2026-10-01.py` (imports the real module).
4. **EXECUTED RESULT** — pre-fix: `FALSIFIED: survey() returned a full verdict with git unable to answer … rows=251 in_tree_but_untracked=205 none_ignored=True`. Post-fix: `survey() correctly REFUSED under git-absence … Clean exit. rc=0`; the ratchet test now **skips** (2 passed, 6 skipped) instead of failing; the figure returns `git unavailable -- figure excluded (environment-dependent)`.
5. **WHAT WOULD OVERTURN THIS** — if `panel_brief_validate.py` always runs in the operator's git shell and never in the sandbox (then the figure divergence is moot) — but the suite-red-in-sandbox consequence stands regardless, and the brief's own exclusion principle still applies.
6. **DISAGREEMENT** — With the brief's claim that "Harvest stranding is repaired at source." The *preservation* (`preserve_seat_evidence`) is git-independent and fine; the *measurement/ratchet* that guards it is git-fragile, so the repair's own regression guard fails in the environment the panel runs in. The repair is half-landed.

The other founder-marked items I scrutinised are **sound**: the catalogue tri-state distinguishes True/False/None correctly (verified with a synthetic registry); `compute_sk` NO_SCORE unchanged; the sandbox deny holds.

---

### FIXES DELIVERED (written into the sandbox tree; falsifier survives harvest)

- **`scripts/seat_evidence_is_gitignored_2026-09-30.py`** — added `GitUnavailable` + `git_available()`; `survey()` now **refuses** (raises) where git cannot answer rather than returning a false all-unpreserved verdict. Purely additive: the git-available path (real repo) is byte-for-byte unchanged in behaviour.
- **`bench/tests/test_seat_evidence_stranding_does_not_grow_2026-10-01.py`** — `rows` fixture catches `GitUnavailable` and **skips** rather than asserting `0 == 251`.
- **`scripts/day_review_brief_figures_2026-10-01.py`** — `f_seat_evidence_stranding` **excludes** the figure under git-absence (mirroring the grep-wrapper exclusion) instead of declaring a false number.
- **`scripts/falsify_seat_evidence_git_dependence_2026-10-01.py`** — the runnable falsifier (imports the real module; FALSIFIED pre-fix, clean post-fix).

All suggested to the human; no verdict moved by model agreement.

---

### Termination

**Four investigation passes.** Pass 1 (re-execute all figures) surfaced the git-dependence divergence. Pass 2 (Q1–Q5 instruments) found the Q2 overclaim and Q4 FP, both sub-threshold. Pass 3 diagnosed and fixed the git-dependence; verified falsifier flip and test skip. Pass 4 (catalogue tri-state, stop_reason, `compute_sk`) added **no** new above-threshold finding. Stopping on diminishing returns: the last pass produced only confirmations of soundness.

**HARD assumption I could not test:** whether the retyped `ORPHAN` regex in the fence-dominance script matches the pattern actually removed from `reference_runner_v3.py:10622` — the sandbox has no `.git`, so I could not diff against history. If it differs, Q2's conclusion (removal safe) could change, though the zero-callers fact makes that unlikely.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/day_review_2026-10-01/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
