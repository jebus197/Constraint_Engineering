# Attack 2 changes. Supply the FIX for anything you find.

You are working in a disposable COPY of the repository. That is already proven and
is NOT what you are being asked to check — do not test it by deleting things. A
previous seat appears to have destroyed its own working directory doing exactly
that, and lost 900 seconds of its own work. Read and run freely; edit if a fix
needs it; your diff is captured.

**THE INSTRUCTION THAT MATTERS MOST.** The founder's standing complaint is that
reviewers get asked to find faults and never asked for the repair. For every defect
you find, supply the FIX — the concrete patch — and say how you tested it. If an
item is sound, say so in one line and move on. Do not manufacture faults.

Assertions about source text are not evidence here. Two forms that each describe
themselves consistently can still disagree when called. Run things.

Budget your time: you have 30 minutes. Prefer 2 well-executed findings with fixes
over a survey.

---

## ITEM 1 — the severity-proof rule (the one I most want broken)

`bench/reference_runner_v3.py`: `severity_is_proven`, `severity_proof_status`,
`_apply_severity_calibration`, and the `severity_proof` stamp written in the round
loop.

A model-assigned severity gated convergence, which breaks the rule that findings
are confirmed programmatically or by a human, never by model vote. The fix requires
a worked proof so the number is recomputable. The rule as built:

1. An unproven severity STILL BLOCKS at the value the model claimed.
2. It cannot buy a demotion, a clearance or a closure.
3. Exception: if `latent_source == "external"` — a human ruled it latent, rather
   than the model asserting it in its own prose — demotion proceeds without a proof.
4. Findings are never deleted; the author is asked for the arithmetic next round.

Reasoning for 1 and 2: if unproven criticals stopped counting as criticals, a model
could clear the gate by omitting its arithmetic, so the enforcement would reward
what it polices. The chosen direction can only make the gate stricter.

**Break these, in this order:**

- **Rule 3 is the weakest link.** Read `bench/latent_tagger.py:tag_entry`. Can a
  model cause `latent_source` to read `"external"` without a human? If it can, the
  carve-out is a hole and I need the patch that closes it.
- Enumerate BY EXECUTION every site that compares `entry["severity"]` against
  `CRITICAL_SEVERITY_THRESHOLD`. Is there one where an unproven number still
  clears, closes or unblocks something? Name the file and line.
- Is a model ever better off supplying NO proof than a correct one? If yes, that
  is a perverse incentive and the rule is wrong.

## ITEM 2 — the R_k statement reader

Same file: `_rk_statement`, `_rk_clip`, `_rk_stated_value`, `_rk_last_stated_value`.

The grader was failing models for obeying the directive: it could not cross a
newline, so a model writing the working it is ORDERED to show had `nu_eff` read as
the leading `1`, forcing R_k = 1.0 and a FAIL. Now it takes the FIRST label
occurrence that states a value, reads continuation lines beginning `=`, and clips
at a comma or a sentence boundary.

Measured over the archive, so you do NOT need to re-run the scan: 128 CORROBORATION
sections; before the fix PASS 40 / WARN 7 / FAIL 34 / SKIP 47 with median
|stated − recomputed| 0.0157; after, PASS 48 / WARN 2 / FAIL 31 / SKIP 41 with
median 0.0010.

**Break it with concrete inputs:**

- Write the shortest CORROBORATION text you can that this reader gets WRONG, call
  `_validate_rk_computation` on it, and show the wrong answer. Then fix it.
- `_rk_clip` treats `". "` as a statement boundary. Where does that break —
  abbreviations, a value ending a line, a decimal followed by a space?
- FIRST occurrence for a parameter, LAST for the final R_k. Find a real case where
  that choice is wrong.

---

Report per item: what you ran, what you found, and the FIX. Nothing else.
