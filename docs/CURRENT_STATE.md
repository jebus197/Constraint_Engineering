# CDSFL Current State

Generated: 1 October 2026 22:58 BST (2026-10-01T22:58:51+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `0f72af3` sv: state save 1 October 2026 12:16 BST — THE CLEAN SUITE RAN AND IT IS RED
- **Committed:** 2026-10-01 12:18:33 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `A  bench/claim_ledger.py`
- `A  bench/directives/universal/seat_evidence_stranding_baseline.json`
- `M  bench/directives/universal/section_p_shortfalls.json`
- `M  bench/experiment_11_orchestrator.py`
- `M  bench/fix_efficacy.py`
- `M  bench/latent_tagger.py`
- `M  bench/panel_sandbox.py`
- `M  bench/reference_runner_v3.py`
- `A  bench/tests/test_archive_blind_spot_has_an_unconditional_arm_2026-10-01.py`
- `M  bench/tests/test_cap_recommendation_2026-09-30.py`
- `A  bench/tests/test_catalogue_records_fix_efficacy_2026-10-01.py`
- `M  bench/tests/test_citation_index_agrees_with_git_2026-09-17.py`
- `A  bench/tests/test_claim_classifier_labelled_set_2026-10-01.py`
- `A  bench/tests/test_claim_ledger_2026-10-01.py`
- `A  bench/tests/test_claim_ledger_route_provenance_2026-10-01.py`
- … and 65 more, not shown (list capped at 15 of 80 — run `git status --porcelain` for the full set)

---

## Tests

**9450 tests collected** at 1 October 2026 22:58 BST, HEAD `0f72af3` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `0f72af3 sv: state save 1 October 2026 12:16 BST — THE CLEAN SUITE RAN AND IT IS RED`
- `450bb1d sv: state save 1 October 2026 01:22 BST, simulation branch, end of session`
- `917028b sv: state save 1 October 2026 00:22 BST, simulation branch`
- `5f7938e Take-home digest of the intelligence-first round, spoken version plus mirror`
- `b4f37de Apply the intelligence-first round, composed: 4 seat fixes, 3 of which had no guard`
- `8f4eb83 Brief for the intelligence-first panel round, with 5 figures re-executable`
- `b8f724b D2 and D3: rounds = 10 with a raise-the-cap prompt, and arm 4's gate genuinely excluded`
- `63c1e19 Decision 12: a falsifier on an absent target now ABSTAINS, all 5, not 2`
- `f8f4d7c Fix the sandbox containment breach: a .pyc is a route back into the real repository`
- `0b05822 Closing report for both 2026-09-30 panel reviews, with every decision the founder owns`
