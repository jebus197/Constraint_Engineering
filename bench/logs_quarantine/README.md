# Quarantined run artefacts

## `sim45_memory_20260830T153011Z` — quarantined 2026-08-30 17:12 BST

A **simulated** run (no paid dispatch) whose artefacts are mislabelled and must
not sit in `bench/logs/` where they are indistinguishable from real panel runs.

Two defects, both in the harness rather than the runner:

1. **123 bare vendor names.** `sim_dispatch_shim.py` computed the simulated label,
   printed it to the console, and then passed `mc.label` — the *vendor* name — to
   `parse_findings`, which is the single call that stamps `model_id` and
   `finding_id` into every persisted finding. The SIM label was cosmetic in the
   terminal and absent from the record. This reproduces the 2026-08-04 provenance
   failure that `feedback_no_fake_model_labels` exists to prevent.
2. **No `runner_version` in `runner_state.json`.** The version reached the report
   but not the state file, which is what the archive guards walk. The run was
   therefore classified by directory name and misfiled as pre-v3 archive.

Both are fixed at source: `VENDORS` now carries the mandatory `-SIM` suffix
(founder ruling 2026-08-08) so no downstream site *can* drop it, and the state
file is stamped. The run was repeated under the corrected harness.

Retained, not deleted: the convergence result it produced is the measurement that
matched real exp45 round-for-round, and the defects it exposed are the reason the
harness is now correct.
