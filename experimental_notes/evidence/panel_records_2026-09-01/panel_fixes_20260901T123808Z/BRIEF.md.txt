# Panel review: four fixes, one rename, three newly recorded classes

**This is a single-shot review.** You will not be asked again, and there is no
follow-up round. Do not reply with a holding note saying you will finalise once
something completes — that is the exact failure this brief exists partly to fix
(see item 2). If you run out of time, report what you established and label the
rest as unchecked.

**The suite baseline, so you need not run it to know it:** `python3 -m pytest
bench/tests -q` gives **4,722 passed, 0 failed** at commit `af5e639`, in about
4.5 minutes. If you want to check a subset, do that instead of the whole suite.

Everything below is **committed**. Your sandbox is a copy of `af5e639`, so the
code is really there. `git log --oneline -3` to orient yourself.

---

## What you are asked to do

For each item: **verify or refute**. Run the code. A claim you did not check is
worth less than an admission you could not check it. Where you disagree with
what this brief asserts, say so and show why — disagreement is preserved as
information here, not smoothed into consensus.

Then answer the three open questions at the end. Those matter more than the
verifications, because they decide what happens next.

---

## 1. The challenge tally now counts distinct models (was: verdict rows)

`FindingRegistry.auto_resolve_contested` in `bench/reference_runner_v3.py`
refuted a contested finding on three CHALLENGE verdicts with no defences in the
recent-round window. It counted **rows**. One model challenging the same
finding in three consecutive rounds refuted it alone.

This project's founding principle is that findings are confirmed by tools
re-executing falsifiers, never by model agreement. A row-counting deletion path
is a vote — and a vote of one.

Now: `len({v.get("model") for v in recent_verdicts if ...})`.

Measured archive exposure: of 66 archived findings carrying three or more
CHALLENGE rows, **1** was REFUTED or CONTESTED with fewer than three distinct
challengers — 1.5%, Wilson [0.3%, 8.1%].

An earlier figure of 22.7% was an over-statement and is withdrawn: it counted
findings by row count regardless of whether they were ever CONTESTED and
therefore eligible for auto-resolution at all.

Tests: `bench/tests/test_a_challenge_tally_counts_models_2026-09-01.py`.

**This is a convergence-adjacent behavioural change.** It makes refutation
strictly harder, so more findings stay contested and runs may converge later or
escalate more to HIL. Is that the right direction? Is "distinct models" the
right unit, or should it be distinct models **with independent evidence**? A
single model dispatched at three seats would still count as three under the
current fix.

## 2. Panel replies are now accepted on substance, and rejection retries

On 2026-08-31 a reviewer returned 54 characters — "Suite still running, I'll
finalize once it completes" — against a median panel reply of 7,512 characters.
The harness recorded `ok=False` and **kept the result**.

The runway recorded this as "its retry fires only on a completely empty
response". That was wrong, and the correction is worse than the original claim:
the retry fired on **neither**. An empty reply raised `CircuitBreakerTripped`,
which the loop re-raises immediately; a short reply hit `return text` with no
test at all. The only substance test in the system ran *after* dispatch, where
it could annotate but never retry.

Now `call_claude_cli` takes an optional `accept` predicate evaluated **inside**
the retry loop. `verdict_is_substantive` rejects empty, tool-call-only, and
under-800-character replies. Default `None` leaves every existing caller
unchanged.

Tests: `bench/tests/test_a_holding_note_is_not_a_verdict_2026-09-01.py`.

**Check the floor.** 800 characters against a 7,512 median: does that reject a
terse but genuine verdict? Is retrying the right response to a holding note at
all, or should it fail loudly instead of spending another dispatch?

## 3. The mid-run target mutation guard, exercised for the first time

Written in July after a model mutated Exp 47's target on 2026-07-29, restored
it, and left no trace in git or the round files. It hashes the target each round
and warns on change.

**It has never fired. Zero of 83 archived run directories carry the
`target_integrity_events` field it writes.** It sat inline in the round loop of
a 12,000-line function where nothing could reach it, and in that state it grew a
defect: the previous hash was a bare module global with no key and no per-run
reset, so a second experiment in the same process compared its first round
against the first experiment's last hash. Reproduced: run 1 on target A, run 2
on target B, and round 0 reports a mid-run mutation with nothing mutated.

Its first firing would have been the false one — in a project that has already
absorbed 92 false alarms from the macrophage.

Now extracted to `target_hash_event()`, keyed by target path, cleared per run.
Tests: `bench/tests/test_the_target_integrity_guard_actually_runs_2026-09-01.py`.

**It remains detective only.** It cannot prevent the write.

## 4. The runner is renamed

`bench/reference_runner_v2.py` carried `RUNNER_VERSION = "v3.2"`. Founder-ruled
on 2026-09-01. Now `bench/reference_runner_v3.py`; 191 files rewritten; the
filename carries the major version and the constant the minor.

`experimental_notes/` was deliberately **not** rewritten — those notes describe
the file as it was named when they were written. The one exception is
`EXPERIMENT_RUN_LEDGER.md`, which is regenerated from the artefacts.

**Check for anything the rename broke that the suite would not catch** — shell
scripts, docs, anything reaching the file by string.

## 5. A document that verified against its own generator

`EXPERIMENT_RUN_LEDGER.md` opens with "DERIVED. Every figure below is read from
the artefacts, never typed." It cited `reference_runner_v2.py:11002` for a
comment that sat at line **12070** — wrong by 1,068 lines, at HEAD, before any
edit in this session.

It survived because its test compared the ledger against the generator's own
hard-coded copy of the same wrong number. Two copies of a typo agree perfectly.

Both now derive the line from the runner source; the generator raises rather
than guessing if the anchor comment is ever rewritten.

**The class is open.** No sweep has been done for other places where a derived
document is checked against its generator rather than against the source. If
you have budget, look for more — that is more valuable than re-verifying the
one instance.

---

## The three open questions

**Q1. Should real runs be confined the way simulated runs now are?**

Simulated runs execute in a disposable git worktree with pathspec staging.
Real code runs deliberately leave panel cwd unset, so the panel inherits this
repository — and panel models carry Write and Edit. That is how Exp 47's target
was mutated mid-run.

Confining real runs is a behavioural change to live experiments, so it is held
for you rather than applied. Should it be made? If so, does the experiment lose
anything real — a code run arguably *needs* the repo to be meaningful. Is
detective-only monitoring plus the integrity watch sufficient instead?

**Q2. Should the rubric-adherence audit gate the next run?**

The 0.7 critical-severity threshold was pre-registered on 2026-05-18 as an
operational proxy for a five-clause consequence rubric. It has never been
audited against that rubric. The plan is to sample ~200 findings in [0.65,
0.75), score them against the five clauses **blind to the numeric**, and report
concordance.

Relevant measurements: 401 of 6,865 archived findings sit exactly on 0.70
(5.84%, Wilson [5.31%, 6.42%]), and 72.1% [71.0%, 73.1%] are quantised to a
0.05 step — severity is ordinal, not continuous.

Is that audit a prerequisite for the next experimental run, or can the run
proceed while the audit happens in parallel? The threshold is not being moved
either way.

**Q3. What else in this codebase has never run?**

Two latent controls have now been found: the A4 fail-safe reachable by 0 of 43
configs, and this target guard at 0 of 83 runs. `bench/canary_seeding.py` is a
third — built to a founder ruling on 2026-08-27, 42 passing tests, wired into
no run.

Is there a cheap general check? A guard nobody has seen fire is a hypothesis,
not a control. What would you build to find the rest of them, and is it worth
building before the next run rather than after?
