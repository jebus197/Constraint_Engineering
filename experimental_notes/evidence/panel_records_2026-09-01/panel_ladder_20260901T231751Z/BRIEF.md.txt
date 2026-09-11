# Panel review: a routing ladder that exhausts where one more dispatch succeeds

**Single-shot.** No follow-up round, no holding notes. If you run out of time,
report what you established and label the rest unchecked.

**Suite baseline:** `python3 -m pytest bench/tests -q` gives **4,799 passed, 0
failed** at commit `c986617`, about 6 minutes.

You two reviewed this codebase twice already today and were right both times —
once on the `target_hashes` sibling, once on the sibling channels that survived a
withdrawal. Everything you flagged last round is fixed and is in this tree. Be at
least as hard here.

---

## THE MAIN QUESTION — the routing ladder

A simulated run halted at round 0 on the irreducible-queue alarm: 3 criticals
locked as irreducible against a bound of 2, none carrying a runnable test.

I got this wrong twice before establishing it. `irreducible_escalation` is set
only **after the full routing ladder is exhausted** without any model producing a
runnable test, so the halt was correct and the alarm was right.

Then the residual-clearing sweep — which runs **after** the verdict is written,
and whose own comment says it "cannot rescue a failed run" — cleared **27
residuals in one round, 0 withdrawn, 0 remaining**, all dispatched to
DeepSeek-SIM, including all three of the irreducibles, resetting
`irreducible_escalation` to False on each.

**So one further dispatch produced what the entire ladder could not.**

Run report:
`bench/logs/sim45_canary_v2_20260901T214242Z_20260901T214244Z/sim45_canary_v2_20260901T214242Z_report.json`

**Q1. Why does the ladder exhaust where one sweep dispatch succeeds?** Compare
the two paths in `bench/reference_runner_v3.py`: whatever sets
`irreducible_escalation`, versus `_post_convergence_sweep`. What differs — the
prompt, the model chosen, the retry policy, the context supplied, the tools
offered? Is the ladder's exhaustion criterion too eager, or does the sweep do
something the ladder should adopt?

**Q2. Should the sweep run before the alarm evaluates?** Note the tension: the
sweep is documented as post-verdict and non-rescuing precisely so it cannot
launder a failed run into a passing one. Moving it earlier may be right, or may
destroy that property. Give me a straight recommendation, not options.

**Do NOT propose raising `max_irreducible_queue`.** It was suppressed that way
twice while it was right, and it is the only instrument that caught this.

## VERIFY OR REFUTE — what I changed since your last review

**1. A reused finding ID was deleting a different defect.** `lookup_alias` keys
on `(model_id, finding_id)` alone, so a model re-using its own local id had the
second finding turned into a CONFIRM vote on the first at
`reference_runner_v3.py:11209`, discarding its description, falsifier and fix.
Fable traced the one parsed `compute_source_hash` catch to this path.

Fixed by comparing content before absorbing, using this project's own instrument
at its calibrated threshold (Jaccard over STEM signatures, 0.20). Below
threshold the finding is registered and recorded as `id_reuse_registered`. It
fails toward the old behaviour.

*Check:* is 0.20 the right threshold **for this use**? It was calibrated for
unlocated-finding merging, not for id-reuse. Could a genuine repeat, reworded
heavily, now score below it and be double-registered — inflating novelty and
therefore gamma? That would be a convergence-affecting regression introduced by
a finding-preservation fix.

**2. Four mutants that used to survive now die.** `too_new = False`,
`too_new = True`, `min→max` in the dating function, `>=` at the boundary,
`> newest + 1`. The dating function is pinned against git independently, and the
boundary is pinned from both sides.

*Check:* find a mutation of `scripts/latent_control_audit.py` that still
survives. There was one each time you looked.

**3. The audit's simulated-run filter was a dead conditional** and is now real.
Witness set drops 82 → 73 reports; three keys correctly revert to TOO_NEW.

*Check:* is the new `_is_simulated_report` right? It keys on directory naming
and on `-SIM` in the first 4000 characters. Can a real run be wrongly excluded
(which would shrink the evidence base and manufacture false TOO_NEW verdicts)?

**4. Seat identity values are case-normalised**, not just keys.

*Check:* does normalising to lowercase collapse anything that should stay
distinct?

**5. Canary catalogue v2** was rebuilt to five fairness criteria after the panel
established that v1 measured docstring-differencing: 17 of 22 findings quoted
the adjacent docstring, and seeding one plant deleted the file's only evidence
for the invariant it broke. Under v2 the panel named 4 of 5 plants including a
hard one with no adjacent formula.

*Check:* does v2 actually satisfy its own criteria, or have I just moved the
flattery? Specifically — is `MEM2-CUSUM` findable without knowing the answer,
and is the difficulty balance across splits real or nominal?

## THE QUESTION THAT MATTERS MOST

**Q3. Is this runner ready for a real experiment?** No real run has ever used a
v3.x runner — 0 of 20 archived real reports carry one. Money is spent on a real
run. What would you check before spending it that has not been checked? And what
in this batch is most likely to be wrong in a way nobody has noticed?
