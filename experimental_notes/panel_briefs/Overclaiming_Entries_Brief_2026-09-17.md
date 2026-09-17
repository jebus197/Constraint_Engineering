# PANEL BRIEF — closing the 31 DONE entries that claim more than their evidence shows

## Section 1 — The question

**Are these 30 corrections, as specified, the simplest sufficient fix, and does each leave the entry's claim TRUE against evidence that executes?**

The artefact under review is `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, together with the test files each entry names in its own `<!-- task: ... | evidence: ... -->` marker. The audit that produced this list is committed unfiltered at `experimental_notes/evidence/done_audit_2026-09-11/` — `audit_findings.json`, `verification_verdicts.json` and `round2_never_audited_13.json`.

**What is and is not wrong.** No test fails. Every named evidence file exists and passes. The gap is between what the tests establish and what the entries CLAIM. Measured across all 84 DONE entries by a 52-agent adversarial audit, every flag handed to a second agent instructed to refute it: **31 of 85 = 36.4706%**, Wilson [27.0293%, 47.0819%].

<!-- figure: overclaim count | scripts/done_audit_overclaim_rate_2026-09-17.py | 31 of 85 -->
<!-- figure: overclaim rate | scripts/done_audit_overclaim_rate_2026-09-17.py | 36.4706% -->
<!-- figure: overclaim wilson low | scripts/done_audit_overclaim_rate_2026-09-17.py | 27.0293% -->
<!-- figure: overclaim wilson high | scripts/done_audit_overclaim_rate_2026-09-17.py | 47.0819% -->

The 31 entries: 1.2, 2.2, 3.3, 5.2, 6.1, 6.6, 7.3, 8.1, 8.3, 9.1, 9.2, 9.3, 9.4, 10.1, A4, A6, A13, A20, A26, L2, P1, P3, P4, P5, P7, R2, R3, R5, V1, V4, V7.

**CORRECTED 2026-09-17, AFTER DISPATCH.** The copy sent to the panel said 30 and 35.2941%. The cc2 seat refuted it: the census carried its round-2 half as a typed tuple of 6 and the adjudication marks 7, dropping `7.3`. Confirmed independently and fixed at source, so the census now derives. The dispatched copy in `bench/logs/panel_round16_2026-09-17/BRIEF.md` is left as it was sent, because a brief is a record of what the seats were actually asked.

Each carries a closing plan from the verifier that upheld it. Those plans are the proposal under review. They are not to be taken on trust: the founder's standing instruction is that the panel produces and tests fixes rather than confirming them.

## Section 2 — Use the harness

**Form your answer by RUNNING things, not by describing them.** Every claim you make about an entry must come from a command you executed and whose output you can quote.

**Named instruments that bear on this question:**

- **Wilson intervals.** Every proportion in these entries needs one, and this project requires it cross-verified by 2 tools — `statsmodels.stats.proportion.proportion_confint` against a scipy or numpy closed form. Where an entry states a figure such as 35.2941% with no interval beside it, check whether that interval exists and reproduces from a committed script. `measured-rate-travels-with-its-script` binds: a measured figure may be cited only if the script that produced it is committed beside it.
- **severity.** Several entries assert something about critical findings. The threshold is `CRITICAL_SEVERITY_THRESHOLD` in `bench/reference_runner_v3.py`; read it from the runner rather than typing 0.7.
- **S_k.** Entries 9.4 and V1 touch admissibility. `compute_sk` classifies at file granularity and returns NO_SCORE on a prose target, which has occurred 0 times in 1,035 archived tristate outcomes, Wilson [0.0000%, 0.3698%].
- **gamma and the two-sided gate** bear on any entry claiming something about convergence. gamma is load-bearing by standing founder directive and is never to be demoted.

**`execute-do-not-grep` is the rule most of these entries broke.** A test asserting on the SOURCE TEXT of a module asserts only that the module describes itself consistently. Where both a producer and a consumer exist as live code, the test must CALL them and compare outputs. 25 of the 30 name evidence that asserts on source text where the claim is about behaviour.

## Section 3 — Produce a fix, and test it

A finding without a fix is half an answer. A fix without a runnable falsifier you have EXECUTED is a hypothesis, not a fix.

For each entry you take:

1. State the entry's claim in 1 sentence, and what its named evidence actually establishes.
2. Produce the correction — either narrow the claim to what is proved, or strengthen the evidence so the claim becomes true. Prefer the second where the claim is worth keeping.
3. Write a falsifier: a runnable check that goes RED against the state before your fix and GREEN after. Run it. Report the command and its output verbatim.
4. A control is required where a check could be vacuous: revert your fix in place and show the falsifier failing. A falsifier that cannot fail confirms nothing.

**The simplest sufficient fix standard applies.** Before building a mechanism, state what would go wrong if it did not exist, and check whether something cheaper already prevents that. Cheaper is the criterion; where it lives is not. **The additive standard applies in both directions**: never remove a feature without a committed measurement showing the replacement dominates on a named property, and an addition nothing reaches is not additive either.

## Section 4 — What would refute you

Before you conclude on any entry, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

State also your strongest disagreement with this brief's framing — including the possibility that an entry the audit upheld is in fact fine, and that the audit was wrong. 5 of 29 upheld findings in round 1 were later found to be about entry ids that do not exist; the audit is not privileged over your own execution.

## Section 5 — Output shape

Return these fields per entry, so replies can be compared without a parser guessing:

- `entry`: the task id.
- `claim`: the entry's claim, 1 sentence.
- `verdict`: one of UPHELD, REFUTED, PARTIAL — does the entry overclaim?
- `fix`: the exact text or code change proposed.
- `falsifier`: the runnable check, as a fenced `python` or `bash` block.
- `falsifier_result`: the command run and its output, verbatim, both before and after the fix.
- `control`: how you showed the falsifier can fail.
- `simplest_sufficient`: why no cheaper fix suffices.
- `refutation`: what would overturn your answer.
- `disagreement`: your strongest disagreement with this brief.

## Section 6 — Termination

**Stop on diminishing returns**, which is this project's own criterion: stop when a further pass over the entries you hold produces no new above-threshold findings, and say how many passes you ran.

A finding is above threshold if missing it could cause a reader to act on a false claim. Do not generate findings for their own sake, and do not police style. If you run short of budget, WRITE WHAT YOU HAVE: a partial answer carrying executed evidence is worth everything, a holding note is worth nothing.
