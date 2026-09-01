# Overnight run, and a parser that drops findings

**2026-09-01, 02:30 BST.** Simulated rehearsal of Experiment 45 against `bench/dm/_memory.py`, and four defects found while running it. One affects real experiments, not only rehearsals.

## The run

| | |
|---|---|
| Runner version | v3.2 |
| Rounds | 4, converged at 3 |
| Canonical findings | 8 |
| Elapsed | 48.1 min |
| Verification chain | sealed, 33 records |
| Model refusals | 0 |
| HIL escalations | 2, both `B-Cell cannot ground claim in source` |

First simulated run to operate entirely on a disposable copy of the repository. The canonical tree stayed clean throughout and every artefact was extracted before teardown. Artefacts: `bench/logs/sim45_memory_20260901T003907Z/`.

## The convergence is real and uninformative

The gate reported itself, verbatim:

> `CRITICAL_QUIESCENCE_CONVERGED (two-sided gate, VACUOUS CURVE)`: zero critical findings across the ENTIRE run (history=[0, 0, 0, 0]) over 8 finding(s) of some severity, so the critical decay curve does not exist and `gamma_critical=0.000` is undefined rather than low. **REVIEW THIS RUN: a clean target and a broken severity classifier look alike from here.**

That warning is correct, and the cause is below.

## Defect 1 — the dispatch seam was two primitives, not one

The shim patches `dispatch_to_model`. The lesson recorded 2026-08-30 after the 1-of-9 defect was *patch the primitive, not the call sites* — right, and incomplete. `_multiturn_fallback` never calls it; it calls `decomposed_dispatch`, which owns a separate API table (`google`, `openrouter`, `deepseek`, `codex_exec`) that has never heard of `sim`. A 20,605-byte target triggers that path immediately, so **5 of 6 agents died in round 0** on `ValueError: Unknown API: sim`.

Both primitives are now patched. The tests *enumerate* every function owning an `Unknown API` table that the runner imports, so a third fails a test rather than a live run. Commit `b4a8b6e`.

## Defect 2 — panel agents were writing to the canonical repository

Panel agents inherit the repo as cwd for code runs by design (`reference_runner_v2.py:9841` — *"unset for code runs, where the panel legitimately needs this repo"*). Reading is intended; nothing prevented writing, and agents carry a shell.

- **Run 2**: an agent reported running `git checkout -- bench/dm/_memory.py`. Corroborated by mtime **01:17:34**, inside the run, matching neither operator commit (01:06:40, 01:19:49).
- **Run 3**: caught live at **01:26:16**, diff recorded and reverted — clamping added to `blended_prior`.

Not simulation-specific: **30 archived runs** targeted repo code under the same arrangement.

**A read-only target was tested and rejected.** `chmod a-w` blocks `python open('w')`, shell redirect and `git checkout --`, but **not `sed -i`**, which unlinks and recreates. Permissions on a file cannot defend it inside a writable directory.

**Adopted fix** (founder ruling): `bench/tools/run_simulated_experiment_sandboxed.sh` runs the experiment from inside a detached worktree. Both harnesses derive their root from `__file__` (`reference_runner_v2.py:154`, `run_simulated_experiment.py:30`) and `repo_relative_target` normalises against that root, so launching from inside the copy redirects target, panel cwd and every derived path at once. Commits `38aee41`, `e715506`.

## Defect 3 — the parser drops findings, and it is not a rehearsal artefact

`parse_findings` returned **zero** for 4 of 6 agents on full, untruncated replies of **23,427 / 14,248 / 33,473 / 17,448** characters. CC2-SIM's carried `### F001 —` headers, 19 `F0NN` references, 3 severity fields, 14 code fences → nothing.

Two faults coincide:

1. **No parser arm accepts a markdown-header finding.** `_parse_findings_core` takes JSON, tuple, `FINDING_ID:` marker, and bare `F001` + `SEVERITY:`. Its docstring promises *"No model is penalised for format variation"*; `### F001 — title` is the exception, and is what 4 of 6 agents used.
2. **The last-resort fallback was suppressed for exactly those four.** CC2-SIM and ChatGPT-SIM open `## Review:`, matching the guard added after **exp43 C0040** (a "Round 8 Review" summary registered as a finding and blocked the gate). Fable-SIM and Gemini-SIM cite `C####` ids in prose, matching the registry-referential-prose guard.

Neither guard is wrong about its own case. Both assume prose citing registry ids, or headed *Review*, is a summary. That fails for a well-formed review that does both.

### Measured against the real archive

| Population | Count | Share |
|---|---|---|
| Real non-simulated replies parsed | 2,401 | — |
| Parse to zero findings | 568 | 23.7% |
| **Parse to zero while carrying finding markers** | **248** | **10.3%** |

95% CI on 10.3%: **Wilson [9.17%, 11.61%]**, scipy beta [9.16%, 11.59%].

By model: Codex 94, ChatGPT 70, CC2 38, Gemini 27, DeepSeek 19.

**Direction of the bound.** Archived replies are stored cut to 10,000 chars (`insect_brain.py:983`). Truncation can only *remove* findings, so 10.3% is an **upper bound** on the live rate. The mechanism is confirmed on uncut text by the rehearsal.

**Checked and found sound:** full replies *are* preserved per-model in `r0_<model>_<stamp>.json` (23,427 chars for CC2-SIM), so the round-file truncation is a duplicate summary, not data loss.

**Refuted hypothesis, recorded.** The suppression is *not* caused by verdict lines — **zero** `CONFIRM/CHALLENGE/EXTEND/MERGE` lines across all six replies.

### Downstream cost

**19 of 26 corrected copies unmatched (73.1%, Wilson [53.9%, 86.3%])** — none reached the discrimination control. Not a resolver fault: `_resolve_finding_key` already tries `{model_id}_{key}`. The findings never entered the registry to be matched against.

## Defect 4 — simulated replies counted as real archive

`TestTheArchiveIsUntouched` went red on four `-SIM` labelled replies. `_is_v3_era` sorts version-first, name-second, and its name rule had learned `exp<N>` only — its own comment records that the rule exists *because* a `sim45_*` run was misfiled, so the earlier repair fixed the instance and not the class. **9 of 11 rehearsal directories carry no `runner_state.json` (81.8%, Wilson [52.3%, 94.9%])**, because a run stopped early never writes one.

Now settled at record level: a reply whose model label ends `-SIM` is a rehearsal by construction and is excluded wherever filed. Commit `daf5f34`.

## Open decisions

1. **The parser fix.** Recommend adding a parser arm for markdown-header findings. Loosening the two suppression guards would reinstate the exp43 C0040 defect they exist to prevent.
2. **Whether to re-run the rehearsal** once the parser is fixed. This convergence is real but says nothing about behaviour under a realistic finding load, which was roughly a quarter of what it should have been.

## State

Suite **4,677 passed, 0 failed**. Canonical tree clean. All work committed locally, **nothing pushed**. Memory index trimmed 24,040 → 18,239 chars, every entry inside the 150-char rule, no entry removed, no link broken; the rule now refuses a save rather than reporting a breach.

*Note: this run's report carries no `panel_confinement` block — the sandbox was cut from HEAD before that field was committed. Later runs will carry it.*
