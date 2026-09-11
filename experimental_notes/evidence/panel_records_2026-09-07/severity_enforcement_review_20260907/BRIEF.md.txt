# Review 2 changes made tonight. Supply FIXES, not just faults.

You are in a COPY of the repository, not the live tree. Verify that yourself
(`pwd`, `git rev-parse --show-toplevel`) before anything else. Edit freely; your
diff is captured and reviewed.

**THE INSTRUCTION THAT MATTERS MOST.** The founder's standing complaint is that
reviewers are asked to find problems and never asked for the repair. So: for every
defect you find, supply the FIX — a concrete patch or exact edit — and state how
you tested it. A finding without a proposed fix is half an answer here. If you find
nothing wrong with an item, say so plainly and move on; do not manufacture faults.

Run code. Assertions about source text are not evidence in this project; two forms
that each describe themselves consistently can still disagree when called.

---

## ITEM 1 — the severity-proof enforcement rule

`bench/reference_runner_v3.py`. A model-assigned severity gated convergence, which
breaks the project's rule that findings are confirmed programmatically or by a
human, never by model vote. The founder's fix: require a worked proof, so severity
becomes recomputable rather than asserted.

`validate_round_rk()` already re-derived R_k from a model's stated R_old, eta, d,
p, S_k, nu_b, nu_f and graded it PASS/WARN/FAIL/SKIP, and the verdict was discarded
into a log line. It is now recorded on the registry entry as `severity_proof` and
enforced by `severity_is_proven()` / `_apply_severity_calibration()`.

**The rule as built, which is what you are asked to attack:**

1. An unproven severity STILL BLOCKS at the value the model claimed.
2. An unproven severity cannot buy a demotion, a clearance or a closure.
3. Exception: if `latent_source == "external"` (a human ruled it latent, rather
   than the model asserting it in prose), demotion proceeds without a model proof.
4. Findings are never deleted; the author is asked for the arithmetic next round.

The reasoning for (1) and (2): if unproven criticals stopped counting as criticals,
a model could clear the convergence gate by omitting its arithmetic, so the
enforcement would reward the behaviour it polices. The direction chosen can only
make the gate stricter.

**Attack these specifically.**
- Is there a path where rule (2) makes the gate LOOSER after all, or where an
  unproven severity still influences a decision that clears something?
- Rule (3): can a model cause `latent_source` to read "external" without a human?
  Read `bench/latent_tagger.py:tag_entry`. If it can, the carve-out is a hole.
- Is there any OTHER site that reads `entry["severity"]` against
  `CRITICAL_SEVERITY_THRESHOLD` where an unproven number changes an outcome and is
  NOT covered? Enumerate them by execution, not by reading.
- Does the enforcement have a perverse incentive I have missed — a case where a
  model is better off supplying NO proof than a correct one?

## ITEM 2 — the R_k statement reader

Same file: `_rk_statement`, `_rk_clip`, `_rk_stated_value`, `_rk_last_stated_value`.

The grader was failing models for obeying the directive. It could not cross a
newline, so a model writing the working it is ORDERED to show —

```
nu_eff = 1 - (1 - nu_b)*(1 - (1 - S_k)*nu_f)
       = 1 - 0.97*(1 - 0.05*0.07)
       = 0.03340
```

— had nu_eff read as the leading `1`, forcing R_k = 1.0 and a FAIL. Measured over
the archive: 34 of 128 sections scored FAIL and the 3 largest discrepancies all
recomputed to exactly 1.0 with the model's own arithmetic correct.

The reader now takes the FIRST label occurrence that states a value, reads to the
end of the statement (continuation lines beginning `=`), and clips at a comma or a
sentence boundary. After repair: PASS 40->48, FAIL 34->31, SKIP 47->41, median
|stated - recomputed| 0.0157 -> 0.0010.

**Attack this specifically.**
- Find a REAL response shape in `bench/logs/*/round*_*.json` that this reader still
  misreads. Run `scripts/measure_rk_proof_compliance.py` and inspect surviving
  FAILs. For each, say whether it is a model error or a reader error, and if a
  reader error, supply the fix.
- `_rk_clip` treats `. ` as a statement boundary. Where does that break? Consider
  decimals, abbreviations, and a value at the very end of a line.
- Taking the FIRST occurrence for a parameter and the LAST for the final R_k: find
  a case where that choice is wrong.

---

Report per item: what you executed, what you found, and THE FIX for each finding.
Keep it tight. Do not restate the brief back to me.
