# Morning Report — 2026-09-28

2026-09-28, 02:40 BST

## One thing blocks everything else

`claude` (the CLI at `/opt/homebrew/bin/claude`) reports **`Failed to authenticate: OAuth session expired and could not be refreshed`**. Both free seats, `cc2` and `fable`, dispatch through it, so both failed in under 2 seconds with 0 chars and 0 tool calls after 2 attempts each. The 11-item panel review did not run.

**Nothing was spent.** `PANEL_ONLY=cc2,fable` held; the dispatcher reported 0 paid seats.

This requires the founder in person: re-authentication is a browser OAuth flow using his credentials, which this assistant never enters. The paid seats would work, but dispatching them would violate his 2026-09-28 ruling — *"There should be no paid dispatches without my express authorisation"* — so that route was not taken.

Run log: `bench/logs/founder_verdicts_2026-09-28/dispatch.log`. Brief, which validates against all 8 required sections: `bench/logs/founder_verdicts_2026-09-28/BRIEF.md`.

## The published explorer needs revising, and Astra's proposed fix is not the one to apply

`explorer/index.html` is served publicly at `jebus197.github.io/Constraint_Engineering/explorer/`.

**It presents the per-pass change as a stopping decision.** Line 83 labels the slider `θ  stopping threshold on ΔR`; line 294 is `const good = s.dR >= o.theta;`, which colours a pass green on that test alone.

**The appendix retired that rule on 2026-09-21.** `docs/MATHEMATICAL_APPENDIX.md:205` states the same rule; `:217` retires it, on the ground that `ΔR` is the change conditional on the non-detection branch while the decision precedes the branch. `:225` gives the general form:

> E[improvement] = R·q·σ·(1 − ν) − ν·(1 − R)

**The error is strictly one-directional.** Over the explorer's own slider ranges at its default `θ = 0.005`: **1309 of 14440 grid points = 9.0651%** where the explorer stops and the appendix continues; **0** the reverse. At `R = 0.99, q = 0.3, σ = 1, ν = 0` the explorer computes 0.00422475106686 against 0.297, a ratio of **70.3** — below `θ`, so displayed as not worth continuing.

No confidence interval is quoted, because that sweep is exhaustive over a fixed grid rather than a sample.

**Proven over the whole cube, not just the grid, by 2 independent tools.** z3 returns `unsat` for both "general < dR" and "general == dR" on the open cube. Wolfram Language independently returns `Resolve[ForAll[...]] → True` for strict positivity, with the identical factored difference `−R²qσ(ν−1)(q−1)/(Rq−1)`. SymPy supplies the symbolic identity that the explorer's `dR` at `σ=1, ν=0` **is** `R·q·(R−1)/(R·q−1)`. (Computed in part with Wolfram Language.)

**Astra's revision is superseded.** Astra proposed `R·q`. `MATHEMATICAL_APPENDIX.md:223` records that this is the `σ=1, ν=0` corner and overstates everywhere else — the founder's own suspicion, confirmed.

**Status: PROPOSED, not applied.** The explorer is public and fixes in this project are suggested to the HIL, never auto-applied. The change is to gate on the general form and retain `dR` as a displayed trajectory value, where it is correct.

- Measurement: `scripts/explorer_stopping_rule_is_superseded_2026-09-28.py`
- Guard: `bench/tests/test_explorer_stopping_quantity_2026-09-28.py`, 6 tests, passing. It `skip`s rather than fails once the explorer is revised, so it does not add to the 9 tests currently failing.

## The naming check: built, measured, hypothesis refuted

Verdict received was *"Do the work."* The work produced a negative result, reported here rather than buried.

**First design, falsified by its own measurement.** Matching any novel 2-to-4-word phrase returned **24 findings** on `experimental_notes/Morning_Report_2026-09-24.md`, nearly all sentence fragments (`write returned`, `outcome stands`, `cc1 owes`), and it **missed** the faults it was built for. Adjacency is not grammar, and no stopword list repairs that.

**Second design.** Require a head noun from a closed set of this project's machinery vocabulary, and require the term to be used without introduction. Same report: **3 findings**, of which `prose scoring flag` is one the founder independently identified as a fault.

**The introduction-marker half is refuted.** Over 40 of 427 notes: rule A fires on 27/40 = **67.5000%**, Wilson 95% [52.0177%, 79.9155%], 78 phrases. Rule B on 26/40 = **65.0000%**, Wilson [49.5059%, 77.8655%], 71 phrases. Rule B removes only **8.9744%** of findings.

**So it cannot block; it can advise.** Density is 71/40 = **1.7750 phrases per note**. It is deliberately wired into no commit hook and no suite gate.

**A third pass was needed, and it is reported because the first 2 were wrong.** The head-noun pattern alone still returned 6 findings on *this* report, 5 of them clause fragments (`appendix retired that rule`, `decision precedes the branch`). A closed verb list between determiner and head removed only false positives: this report 6 → 2, the 24 September report unchanged at 3 including the confirmed fault, the fixture's `critics order` still caught, an introduced `absorb rule` still passed over.

**Two structural blind spots, each asserted by a committed test.** It cannot see a **collision** — a term that does exist while meaning something else, as `blocking gate` did across 7 files, the worst of the 8 faults. And it goes blind retrospectively once a term enters the repo by any later note. Fixture confirms: `prose conviction rule`, `blocking gate`, `severity ladder` now return 0; `critics order` is still caught; an introduced `absorb rule` is correctly passed over.

**Design the measurement points at, for a ruling.** Anchor on `docs/GLOSSARY.md`, which already holds "every term, acronym, Greek letter defined". A machinery phrase absent from the glossary either should use the glossary's name or should be added to it — a question with a remedy, rather than a novelty heuristic.

- Script: `scripts/note_naming_check_2026-09-28.py` (`--measure` reproduces every figure above)
- Guard: `bench/tests/test_note_naming_check_2026-09-28.py`, 8 tests, passing

## Paid dispatch can no longer happen by forgetting something

His ruling: *"There should be no paid dispatches without my express authorisation. You should make sure this is the case going forward."*

**The defect.** `bench/confer_maths_panel_2026-09-05.py` selected **all 6 seats, 5 of them paid**, when `PANEL_ONLY` was unset. The safe path required remembering an environment variable; the expensive path was the default. That is how 5 paid seats were dispatched on 2026-09-22 on a round asked to be free.

**The fix, in 2 parts.** The default roster is now the 2 free seats. Naming a paid seat is refused unless `bench/paid_dispatch_authorisations.json` carries an entry for that round quoting his authorisation. Refusal happens before any seat is built — verified end to end: `PANEL_ONLY=cx,ge` exits with `REFUSED: PANEL_ONLY names paid seat(s) cx, ge and no authorisation ledger`.

**The limit, stated rather than implied.** An environment variable is something this assistant can set for itself, so a guard resting on one guards nothing it is meant to guard against. The ledger is a committed file: an unauthorised spend requires forging his words somewhere that appears in `git diff`. The enforcement is auditability, not impossibility.

**Nothing removed.** Paid dispatch works by the same route, with an authorisation recorded beside it.

**Regression check, because the change had a consequence worth naming.** The red-suite spend gate refuses only when money is at risk — its own message reads *"there is no spend to protect. Proceeding."* Making the default free therefore made that gate a no-op by default, and 6 tests that had been inheriting a paid roster from the dangerous default stopped raising. The fixture now pins its roster explicitly and 4 new tests guard the free-default path, including one asserting the shipped module carries no paid seat. Measured: the dispatcher's test set went from 243 passing at HEAD to 247, with the same 5 pre-existing failures before and after — 4 of them the paid-seat guards awaiting his verbatim authorisation, 1 an order-pollution case that passes in isolation.

- Guard: `bench/tests/test_paid_dispatch_needs_authorisation_2026-09-28.py`, 11 tests, passing

## The harvest did not work properly, which was the point of asking

His instruction: *"You can test the harvest mechanism in the above panel review and make sure it works properly."* The failed round became the test, and it failed the test.

**What the round reported.** Both seats died at authentication with 0 tool calls and wrote nothing. The dispatcher still printed *"seats proposed edits to 8 file(s)"* and *"harvested 3394 byte(s) of seat-written files"*.

**What was actually captured.** All 9 paths were dispatcher or harvest artefacts: `cc2.json`, `fable.json`, `dispatch.log`, `seat_proposals.diff`, and — the harvest harvesting itself — `sandbox_harvest/cc2/attempt-1/changes.diff`. The sandbox is a copy of the repo, and the dispatcher writes its run log into `bench/logs/<run>/`, which exists inside that copy too. The sole difference in the diff was `elapsed_s` varying by 0.9 between the canonical log and the copy's.

**Why that is a provenance defect, not untidiness.** A reader of that log concludes 2 seats did work on a round where neither ran. On a round where seats do work, real deliverables arrive mixed with this noise. The project's record already holds the same shape once: on 2026-09-20 the harvest copied 112 MB of `.git` objects out as seat-written work, which is why `_is_vcs_metadata` exists. This is that defect recurring through a different directory.

**Fixed, scoped deliberately.** Only the current run's log directory is excluded — excluding `bench/logs/` wholesale would discard a measurement a seat was asked to write there. The diff and the reported count exclude them too, since the false 8-file claim came from the diff.

**A bug in my own fix, found by tracing callers rather than by the tests.** The first version derived the run directory as `dest.parents[2]`, correct only for the dispatcher's deepest destination. The other 2 callers are shallower: the same expression resolved to `bench/logs` for `worktree_harvest` and to `bench` for `panel_worktree_harvest` — which would have excluded the **entire bench tree** from every simulated run's harvest, and silently, because a harvest that takes less prints a smaller number rather than an error. The rule is now structural: the run directory is the ancestor of the destination sitting directly inside a directory named `logs`, which holds for all 3 shapes.

**Falsified both ways.** Reverting the exclusion fails 6 of 16 tests; reinstating the depth assumption fails 4, including the one asserting no shape ever resolves to the whole bench tree. 202 tests pass across everything touching `panel_sandbox`, with 1 skip and no regressions.

- Fix: `bench/panel_sandbox.py`, `_run_log_dir` and `_is_dispatcher_own_output`
- Guard: `bench/tests/test_harvest_excludes_its_own_output_2026-09-28.py`, 16 tests, passing

## The 3 scripts that acted when imported

Confirmed closed. `bench/tests/test_help_never_acts_2026-09-11.py` passes 10 of 10 across 206 scripts.

## A second finding, real but not load-bearing

The CLI also reports `Ignoring 19 permissions.allow entries from .claude/settings.json: this workspace has not been trusted`. Confirmed: `~/.claude.json` carries `hasTrustDialogAccepted: False` for this workspace.

**Not load-bearing for panel work.** The dispatcher passes seats their tool list via the `--allowedTools` command-line flag (`bench/experiment_11_orchestrator.py:1190`), which the settings-file trust state does not touch; earlier rounds recorded 16 to 37 tool calls per seat. Recorded so it is not later mistaken for a cause.

## Report length

6000-plus words are not necessary. The TTS companion is 1297 words and leads with what needs the founder. Future reports hold that shape.

## Wolfram

No longer in the founder's alerts. Renewal automation verified live 2026-09-27 23:31; the stale instruction in `.claude/CLAUDE.md` that caused 2 false alarms in one evening is corrected at source, and master task list entry 0.1 is DONE with evidence.

## What is owed

The 11-item panel review, once the login is restored. 6 items were written for the panel and are unstarted: whether the A19 repair gives the whole answer; widening the extractor beyond fenced code; the severity threshold for prose-target convictions; verification of 3 unreviewed `hooks/ffafp_audit.py` changes; a guard against editing the tree during a measurement; and the owed Stop-gate fixture.

Open from before: **W1** — whether the Wolfram licence question was answered in writing, or only the route restored. `mcpServers` remains empty.

Written under CDSFL note standard v1.7 (26 August 2026).
