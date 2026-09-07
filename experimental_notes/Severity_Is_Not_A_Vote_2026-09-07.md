# Severity is a calculation now, and the check that grades it was punishing compliance

**2026-09-07, 01:00 BST. Constraint Engineering (CDSFL).**

## What was decided, and why the founder's version of the fix is the better one

A model-assigned severity float gated convergence. That conflicts with a standing rule of this project: findings are confirmed programmatically or by a human in the loop, never by model vote. Two repairs were on the table.

The first, proposed by CC1, replaced the float with a consequence-class rubric lookup. It has a measured problem. The rubric and the number were compared over the archive on 2026-09-05: they disagree on 45.56% of judgeable cases, and their agreement is kappa = -0.0227 with Fisher p = 0.78, which is indistinguishable from chance. Swapping one for the other exchanges an oracle for a different oracle, with no evidence the replacement is better.

The second, proposed by the founder, keeps the model's judgement and makes it checkable: *"If a model can demonstrably be shown to be using the mathematical model (and tools) to calculate severity, then is that really a vote? The difference is I think in requiring the models to provide worked proofs in all cases."* That does something the swap cannot. A severity accompanied by every input it was computed from can be RECOMPUTED. If the recomputation agrees, the number is arithmetic. If it does not, the number is an assertion. The distinction is decidable by execution rather than by preference, which is the whole method this project runs on.

## The machinery already existed and decided nothing

`validate_round_rk()` in `bench/reference_runner_v3.py` re-derives R_k from each model's stated R_old, eta, d, p, S_k, nu_b and nu_f, and grades the result PASS, WARN, FAIL or SKIP. Its own docstring read: *"Advisory only — logs WARN/FAIL but never rejects findings."* At the call site the verdict was counted into a single log line and then discarded. Every finding registered regardless.

Meanwhile the round prompt sent to every model contained the sentence *"Findings missing any section will be rejected."* That sentence was false for the whole arc. This is the third instance in 3 days of the same shape in this codebase: a capability built, and then not wired to anything.

## The check itself was misreading the models, and it failed them for obeying the directive

Before enforcing anything, the shipped grader was run over every archived model response. 2199 round files were scanned, 130 carried untruncated responses, and 128 CORROBORATION sections were graded. 34 of 128 scored FAIL, which is 26.56% with a Wilson interval of [19.68%, 34.82%].

The 3 largest discrepancies all recomputed to exactly 1.0, and in each case the model's own arithmetic was correct to 3 decimal places. The cause is that the parameter reader could not cross a newline. The directive orders models to show their working. A model that obeys writes this:

```
ν_eff = 1 − (1 − ν_b)·(1 − (1 − S_k)·ν_f)
      = 1 − 0.97·(1 − 0.05×0.07)
      = 0.03340
```

The reader anchored on the first line, captured the leading 1 as the value of nu_eff, and so computed R_k = R_base × (1 − 1) + 1 = 1.0 exactly. A downstream clamp to the interval [0, 1] then made that impossible residual risk look like a legal one, and the finding was graded FAIL. Under the escalation rules a FAIL is placed at the top of the next round's prompt, worded as the model's own arithmetic — so a model that had done the arithmetic correctly was accused of getting it wrong, with maximum confidence.

The single-line form of this exact defect was found and repaired on 2026-08-21. The repair's own comment records the signature, `recomputed == exactly 1.0`, and the measurement behind it, 89 of 198 FAILs. The multi-line form was left live in the same function.

Two further shapes were misread and are now handled. A comma-separated parameter list, `R_old=0.50, eta=0.90, d=0.80, ...`, returned nu_f as the value of R_old when the reader took the last value on the line. A dense single-line response returned 0.80, the model's S_k, as its stated R_k, because the statement ran on past its own answer into the following sentence.

After repair, measured over the same corpus: PASS rises from 40 to 48, FAIL falls from 34 to 31, SKIP falls from 47 to 41, and the median absolute difference between a model's stated R_k and its recomputed R_k falls from 0.0157 to 0.0010. Reproduce with `scripts/measure_rk_proof_compliance.py`.

## The two live forms of the equation were called against each other

`_validate_rk_computation` performs the R_k arithmetic inline rather than calling `compute_rk`. That makes two independent implementations of one equation, which is the situation the project's `execute-do-not-grep` rule exists for: reading both and finding them consistent proves only that each describes itself.

Both were called. The symbolic residual is 0 (SymPy). Over a 1125-point grid and 20,000 seeded random draws the worst absolute difference is 0.000e+00 (NumPy). At 50 decimal places near the pole the worst is 2.364e-12 (mpmath). The one designed difference is the path where a model states nu_b + nu_f > 1: `compute_rk` enforces the directive's hard constraint by rescaling, while the validator uses the nu_eff the model stated, because it is checking the model's own arithmetic. That case is a hard-constraint violation and belongs to that rule, not to a silent re-score. Reproduce with `scripts/verify_rk_validator_matches_compute_rk.py`.

## What enforcement now does, and the one direction it runs in

The verdict is recorded onto each registry entry as `severity_proof`. A severity is PROVEN when its recomputation lands within tolerance, where PASS is 0.01 and WARN is 0.05; WARN is accepted because a discrepancy at that scale is a model writing 3 significant figures, not a model asserting a number it never computed.

Enforcement is deliberately one-directional. An unproven severity may never make the gate looser. It still BLOCKS at the value the model claimed, and what it cannot do is buy a demotion, a clearance or a closure. The reason is a loophole that the obvious design would have opened: if unproven criticals stopped counting as criticals, a model could clear the convergence gate by omitting its arithmetic, and the enforcement would reward exactly the behaviour it polices. The direction chosen can only ever make the gate stricter, so it cannot manufacture a convergence — the same principle as the non-finite guard already in `compute_rk`.

One carve-out is required by the no-voting rule rather than being an exception to it. Demotion eligibility requires `entry["latent"]`, and `bench/latent_tagger.py` records where that flag came from. The values "prose" and "explicit_field" mean the model said so in its own words, which is the vote being policed. The value "external" means a human in the loop or an upstream adjudication ruled. Blocking a human ruling for want of a model's arithmetic would invert the rule instead of enforcing it, so a HIL-adjudicated latency still demotes without a model proof.

Findings are never deleted by any of this. A defect reported without a proof may still be a real defect. It is retained, it keeps blocking, and its author is asked for the arithmetic through a new next-round prompt section built by `bench/dm/_rk_proof.py`, which names the finding, shows the model both numbers and the size of the gap, and offers withdrawal as a legitimate outcome that costs nothing. The section reaches both dispatch topologies, relay and star; enforcement that is real on one path and cosmetic on the other is a failure shape this project has found before.

## The containment fix had created a credential exposure

Founder ruling 35 confined panel seats to a copy of the repository rather than the live tree. That was proved by execution earlier the same night: both seats reported a working directory inside the sandbox, `git rev-parse --show-toplevel` returned *fatal: not a git repository*, both created a marker file, it landed in the copy, and re-hashing 7900 tracked files found the canonical tree unchanged.

Confining a seat to a copy is worthless if the copy carries the credentials. Measured on the first working sandbox: `.env` arrived readable, 1264 bytes, declaring 10 live API keys covering OpenAI, Google, Gemini, GitHub, Groq, DeepSeek, OpenRouter and Semantic Scholar. A seat has shell access — that is precisely why positional confinement was needed instead of a tool allowlist — so a seat could simply read the file. Nothing a review seat or a falsifier does requires a credential; the dispatcher holds the keys and makes the calls.

Both clone paths now scrub credential-bearing files and then VERIFY the scrub, raising rather than returning a sandbox that merely looks safe. A scrub that silently missed a file would be worse than no scrub, because it would be trusted. `.env.example` is kept deliberately: it holds names and no values, and removing it would change what the repository looks like to a seat for no security gain. The same repair was applied to the falsifier discrimination overlay, where the identical leak had been measured on 2026-09-06 and left alone. 4 further copy sites in `bench/` share the defect and are named in the open list below.

## The Open Brain label split was already harmless, and the real orphaning was elsewhere

The recorded defect was 89 memories labelled `CDSFL` against 1 labelled `cdsfl`, plus 4 unclassified. Executed rather than assumed: `list_recent` returns the same 90 rows for `CDSFL`, for `cdsfl` and for `CdSfL`, because the write guard already refuses new casings and the read filter already folds case at all 5 query sites.

The remaining mis-cased row cannot be repaired by rewriting it. The store is an append-only ledger whose `content_hash` is a SHA-256 over the canonical JSON of `{raw_text, metadata}`, so the project label is inside the hash. Recomputing that row's hash with the label corrected moves it from `sha256:1c1aa2a8...` to `sha256:39de2016...`, and 39 rows chain to it by `previous_hash`. Rewriting it would require re-signing 40 rows and would be indistinguishable from tampering, which is the one thing the ledger exists to make detectable. A store its owner is willing to rewrite is not a ledger.

What was genuinely broken sat next to it. 4 rows from March 2026 carry the sentinel `UNCLASSIFIED`, while the code knows only `UNLABELLED`. Those rows matched neither a project filter, being no project, nor the unscoped filter, being neither NULL nor the known sentinel. They were invisible to every scoped read AND absent from the notice that exists to surface exactly such rows: the census reported 0 unscoped rows while 4 were orphaned. Repaired on the read side, where no ledger row has to move. `python3 -m open_brain.cli project-labels` now exists and reports the state, which nothing previously did — the census function had been written and left reachable by nothing.

## Still open

Item 16, which is 17 fixes to supply, 11 equipment cases to repair and 4 containments to record. 90 code targets are in scope; 43 exam targets are staged from the off-repo store and are blocked on the held answer keys.

The 4 remaining copy sites that materialise `.env` into the temporary directory: `bench/reference_runner_v3.py` at 2 sandbox-gate sites, `bench/exp40_fix_collation.py` and `bench/exp40_fix_harvest.py`.

The discrimination overlay is built 3 times per finding at roughly 8.3 seconds each, with 3 concurrent copies of 683 MB.

The founder's notes are 141 days stale, covering 494 commits.

Held for the founder: sealing the remaining plaintext answer keys, which needs his passphrase, and then the simulated run.
