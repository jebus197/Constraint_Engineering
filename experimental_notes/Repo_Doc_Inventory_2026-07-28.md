# Repository Document Inventory — Pre-BR2 Hygiene Report (for founder ruling)

**2026-07-28, 11:45 BST.** Read-only classification by three parallel inventory agents (root+docs / experimental_notes / resources+strays). Nothing has been moved or deleted; every action below awaits the founder's ruling, recommended as ONE hygiene commit after the arc completes.

## Headline

The repo is in better shape than feared. The scientific record is clean and positively verified: the root `experimental_notes/` (207 files, 2 Apr–28 Jul) has **zero md5 duplicates, zero duplicate titles, zero strays, zero untracked files**; the `docs/experimental_notes/` set (139 files, 14 Mar–2 Apr) is the earlier chapter with **zero filename overlap**. The actual debris is small and specific: ~6 delete candidates, ~17 archive candidates, 4 items needing a ruling.

## DELETE candidates (small, safe, evidence-based)

1. `.DS_Store` + `docs/.DS_Store` — Finder debris, untracked.
2. `docs/Experiment 40 response.txt` — corrupted lossy export (mojibake apostrophes) of the .docx sibling; published on GitHub in that state.
3. `resources/configs/` (3 files) — **drifted-stale duplicates** of the public `configs/` set PAPER.md actually points to (90 diff lines; carries outdated directive text a third party could follow). Fix the one inbound ref (ONBOARDING:1357) in the same commit.
4. `bench/bench/results/phase2` — empty nested directory, residue of a mistyped command.

## ARCHIVE candidates (move to `archive/`, history preserved by git regardless)

- `docs/BENCH_RUN_1_ANALYSIS.md` — self-described confounded baseline, superseded (1 inbound plain-text mention to update).
- `docs/Experiment 40 response.docx` — primary founder feedback; convert to dated markdown under `experimental_notes/` (the record's proper home), then archive the binary.
- `falsify_verify_bundle.py` (repo root) — the Exp 44 C0028 falsifier, real evidence in the wrong place; relocate under `bench/`.
- Six stale `bench/*.md` plan docs (EXPERIMENT_PLAN v2, EXECUTION_PLAN_EXPERIMENT_11/12, EXP35_PLAN, BENCH_EXPANSION_PLAN, CX_PHASE2_HANDOFF) — completed/abandoned plans whose forward-tense claims are now false.
- Eight `experimental_notes/*_Update_2026-04-19.md`-class changelogs — doc-maintenance records absorbed into the canon. **Blast-radius warning: all eight are linked from RECOVERY.md (two also from ONBOARDING) — links must be updated in the same commit.**

## FOUNDER RULINGS needed (4)

1. **The split experiment record.** `docs/experimental_notes/` (March chapter) vs root `experimental_notes/` (April-onwards). Recommendation: KEEP the split (external links + README:473 point at the docs/ half), add cross-links in both directions and one sentence in README explaining the chapters. Consolidation is cleaner but breaks published links.
2. **`docs/experimental_notes/README.md`** — its index has all 138 links broken (.txt names for .md files). Recommendation: regenerate the index mechanically.
3. **The Mathematical_Popper draft cluster** (5 files, 26–27 March, drafts → corrected → final). Recommendation: KEEP — it is falsification lineage (the corrected-after-adversarial-review chain), the project's method applied to its own maths.
4. **Two orphans**: `experimental_notes/Exp35_Verification_Analysis.json` (real evidence data, wrong directory — relocate under bench/?) and the undated Session_Recovery file. Recommendation: relocate the JSON, date-stamp the session file.

Private-by-design files (`.env`, `PRIVATE_NOTES.md`, the gitignored SPEC draft) are untouched — personal-workflow, not repo hygiene.

## Execution plan (on founder `y`, post-arc, pre-BR2)

One commit: deletes + archive moves + the ~12 link fixes named above + regenerated index + README chapter sentence, followed by a full-suite run and a docs-consistency sweep. Estimated one careful hour, no API cost.

---

*Written under CDSFL note standard v1.2 (14 May 2026).*
