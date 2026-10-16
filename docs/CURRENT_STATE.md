# CDSFL Current State

Generated: 16 October 2026 11:05 BST (2026-10-16T11:05:29+01:00)

---

## Git

> **SNAPSHOT TAKEN IMMEDIATELY BEFORE THE sv COMMIT — NOT CURRENT TRUTH.**
> This file is generated first and committed second, so it cannot describe
> the commit that carries it. Read the block below as follows:
> **"Last commit" is the PARENT** of the commit containing this file, and
> **the uncommitted list is the working tree at snapshot time — it is NOT
> that commit's file list.** The two differ in both directions: sv rewrites
> docs/CURRENT_STATE.md, resources/ONBOARDING.md and resources/RECOVERY.md
> *after* this snapshot, and it stages only whitelisted paths. For the
> commit this file actually lives in and its real contents, run
> `git log -1 --stat -- docs/CURRENT_STATE.md`.

- **Branch:** sim/shakedown-2026-09-29
- **Last commit (the PARENT of the commit containing this file):** `5e2ba7ee` THE KEY PROPERTY BIT: leg 3 is the first run where a falsifier disproved anything
- **Committed:** 2026-10-16 11:02:24 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 11
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/fingerprints/CC2-SIM.json`
- `M bench/fingerprints/ChatGPT-SIM.json`
- `M bench/fingerprints/Codex-SIM.json`
- `M bench/fingerprints/DeepSeek-SIM.json`
- `M bench/fingerprints/Fable-SIM.json`
- `M bench/fingerprints/Gemini-SIM.json`
- `M bench/state/immune_memory.json`
- `M experimental_notes/data/output_hashes.json`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**11469 tests collected** at 16 October 2026 11:05 BST, HEAD `5e2ba7ee` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

This is a COLLECTION count, not a pass count, and it says nothing about whether the run was offline. Quote it only with the timestamp and commit above. The total is not stable: `bench/tests/test_immune_memory_consumption.py` parametrises over the timestamped run directories under `bench/logs/`, so it grows whenever an experiment archives, and new test files land between saves.

For a pass count, run the suite offline and record the result with its own date and command: `python3 -m pytest bench/tests/ -q --netguard-strict`. The suite is offline by default via `bench/tests/conftest.py`; see docs/REPRODUCING.md. Figures labelled "non-network" before 2026-07-31 were hand-curated exclusions and included live model dispatch — do not quote them as offline results.

---

## Latest Experiment

- **Experiment:** exp55_v3_control (#55)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/cdsfl_registry/targets/control_two_distinct_defects.md`
- **Rounds:** 1
- **Total findings:** 10
- **Gamma:** 0.0000
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - ChatGPT: 2
  - Gemini: 2
  - Codex: 2
  - DeepSeek: 2
  - CC2: 2
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp55_v3_control_20260823T153955Z`

---

## Recent Commits

- `5e2ba7ee THE KEY PROPERTY BIT: leg 3 is the first run where a falsifier disproved anything`
- `c65aaa7f the answer to "why so many rulings": 11 of 13 are genuinely new, and that corrects what I implied last night`
- `99e2c179 the `ruled` marker field: an item he has already ruled on is no longer a decision`
- `84393b83 his question answered: 5 of the 13 decisions should not have been put to him, and the cause is the marker schema`
- `4e6cb40c leg 3 closes: 38 findings, 71.5 min, and the closing sweep acted for the first time in 3 legs`
- `3bc7c412 name the corpus: leg 3's own logs moved the figure the session had already quoted`
- `4bbc84c5 LEG 3 CONVERGED: 3 of 3 consecutive clean convergences, the success criterion is met`
- `4a4a1d74 notes: the session pair at 0 findings, and Rule 30 scoped to reporting after it refused a compliant note`
- `7fad7911 Rule 30 had to be defended against 4 self-legitimising paths, the 4th only visible once it worked`
- `baeb184c B6.1: the concise rendering was deleting 19 of 20 functions from the code under review`
