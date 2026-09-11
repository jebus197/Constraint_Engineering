# Four defects found by an overnight simulated run, my proposed fixes, and an inventory. Test them.

You have reviewed this repository three times. Your findings were applied and the
overnight run then converged at round 3 with zero residue and the falsification
core live for the first time (18/25 falsifiers, 20/25 verified, 11/25
cross-model co-discovery against 0/566 across the whole modern arc).

**This brief asks you to TEST MY FIXES, not to admire the run.** The founder's
standard is the SSF — simplest sufficient fix. Where mine is not the simplest
sufficient one, say so and give the alternative.

## Defect 1 — 15 findings record "no falsifier to probe" and 11 of them have one

`fix_efficacy` recorded `NOT_PROBED_NO_FALSIFIER` on 15 of 25 entries. **11 of
those 15 carry a falsifier in the final artefact.** All 11 have a proposed fix,
none was ever attempted, and replaying `fix_efficacy_decision` on them returns
PROBE for all 11.

Mechanism, proven: the set of 11 stale records is **identical** to the set of 11
findings cleared by the post-convergence sweep. The sweep attaches falsifiers and
closes findings; the probe lives inside the per-round status pass, which never
runs again after the sweep. The records were true when written and false by the
end.

**My proposed fix:** run the fix-efficacy pass once more after the sweep
completes, before the report is written.

**Test it.** Is one extra pass sufficient, or does the sweep also invalidate
other per-round state that is never recomputed? Is there a cheaper fix — e.g.
clearing the stale record rather than re-probing?

## Defect 2 — the discrimination control's guarantee is not enforced

The control fired for the first time in this project's life. On C0013 it found a
falsifier that fires just as hard against a CORRECTED copy — i.e. not testing its
claim — set `mechanical_fault=True`, and logged *"the finding is NOT closed and
NOT dropped — it returns to the human"*.

**C0013's final status is CLOSED.** C0015 was `hil_escalated=True` and is also
CLOSED. Both were closed in round 1 by:

```python
if (entry["status"] in ("CONFIRMED", "CORROBORATED") and entry.get("verified")):
    registry.resolve(canonical_id, "CLOSED", ...)   # evidence: "verified fix, no unresolved challenges"
```

That condition consults **neither** `mechanical_fault` nor `hil_escalated`.

**My proposed fix:** add `and not entry.get("mechanical_fault") and not
entry.get("hil_escalated")` to the close condition.

**Test it.** Does that strand findings permanently in CONFIRMED with no route
out, creating a HIL pile? Is there an existing clearing path that should reset
the flags? Does the founder's standing rule — HIL is by design, target is
MINIMAL-HIL not zero-HIL — argue for a different shape?

## Defect 3 — three "REFUTED findings" are not findings

Of 5 REFUTED, two are genuine. The other three are simulated panellists
**refusing or objecting**, and the reason is that a `claude -p` subagent inherits
the operator's global `~/.claude/CLAUDE.md`:

* two panellists declined to start, citing the operator's personal 23:00–05:30
  stop-and-sleep directive;
* one objected that labelling agents `CC2-SIM` violates `.claude/CLAUDE.md:275`,
  which still carries the superseded 2026-08-05 rule (`SIM-A`…`SIM-E`). **The
  panellist is right**: the operative ruling is 2026-08-08 (`-SIM` suffix) and
  the project config is 23 days stale.

So half the panel was partly or wholly disabled by directive inheritance, and the
schema REFUTED the results, which is correct but consumed canonical IDs.

**My proposed fixes:** (a) correct `.claude/CLAUDE.md:275`; (b) give simulated
panellists a clean instruction environment carrying the CDSFL directive only.

**Test it.** What is the SSF for (b)? Is there a supported way to run the CLI
without inheriting the user config, and if not, what is the least-bad
alternative? Should the skin barrier reject a "finding" that is about the prompt
rather than the target, and is that a general defect that would also bite a paid
panel?

## Defect 4 — the macrophage produces only false alarms

Enabled for the first time last night. 10 timing-spike observations, every one a
model-calling stage compared against a **bookkeeping** median:

```
llm_classifier         207.23s  vs median 0.0022s  =  94,197x   severity 1.00
parallel_verification   96.86s  vs median 0.0006s  = 161,433x   severity 1.00
layer2_llm_active       21.08s  vs median 0.0009s  =  23,418x   severity 1.00
```

`severity = min(1.0, t/(median*10))` saturates at 1.00 on all 10, so severity
carries zero information. The population is bimodal — microsecond bookkeeping
stages and tens-of-seconds model calls — so one cross-stage median is a category
error. A 2026-07-27 repair removed a `median_t > 0.1` guard because it masked all
spikes, and replaced it with `t > 0.5`, which created this.

**My proposed fix:** compare each stage against **its own** median across rounds,
not against the cross-stage median within a round. No alarm on the first round,
because an anomaly cannot be called on n=1.

**Test it.** Is per-stage history available in `macrophage_cell.py`, or does this
require new state? Is there a smaller fix that is still correct? What should
`severity` be so that it discriminates?

## The inventory the founder asked for

Their concern, verbatim: *"potentially accidentally leaving all routes in the
schema pointing at agents rather than real models."*

**Checked and clean.** `grep` over `reference_runner_v2.py`, `runner_core.py` and
`experiment_11_orchestrator.py` finds **no reference** to the simulation shim, and
`R.dispatch_to_model` at import time resolves to `runner_core.dispatch_to_model`.
The shim is installed at runtime only, by `run_simulated_experiment.py:233`.

Sim-only, never imported by a real run: `run_simulated_experiment.py` (+158),
`sim_dispatch_shim.py` (+132), `tests/conftest.py` (+210).

Changed in files a REAL experiment executes, since the v3.1 run: 656 lines added
across `reference_runner_v2.py` (+410), `experiment_11_orchestrator.py` (+121),
`runner_core.py` (+81), `falsifier_verify.py` (+24), `routing.py` (+20).

**This is the part I most want attacked.** The founder's worry is regression in
real experiments caused by changes made to serve simulated ones. Go through those
656 lines and tell me which carry risk to a paid 6-model run. I am specifically
unsure about:

1. `enable_tools` now defaults **True** everywhere, where it defaulted False and
   rode on `falsifier_gate_enabled`. Every gate-off configuration now dispatches
   with a tool loop. Intended per founder ruling, but it changes paid behaviour.
2. Description truncation removed at two parser fallbacks — deliberately changes
   parsing mid-arc, so text-derived measures are not comparable across Exp 40-49
   and later.
3. `_extract_routing_falsifier` rewritten twice in one night. It now takes a
   strict reading of the whole reply and falls back to permissive only when the
   strict one yields nothing runnable.
4. Gemini function-calling on the `google` route, verified by ONE paid call.

Run `python3 -m pytest bench/tests -q` (~5 min; expect 4599 passed, 0 failed,
0 skipped). Where you disagree, show the command.
