# Morning Report — complete decision surface

**2026-09-05, 13:10 BST (Saturday)** · **Supersedes both earlier versions of today's report.** The first was too dense to use; the second listed 9 decisions when the record holds 122. Spoken companion: `~/Desktop/CDSFL_tts/Morning_Report_REVISED_2026-09-05.txt`.

Regenerate the underlying data: `python3 scripts/triage_open_founder_decisions.py` · `python3 scripts/salvage_task_reconstruction.py`

---

## Part 1 — the decision surface, in full

**129** raw open questions across 3 days → **122** after grouping → **17 answered** by yesterday/today → **11 already decided or done** → **~94 live**, in 12 themes ranked by cost of *not* deciding.

| # | Theme | Entries | The decision | If left |
|---|---|---|---|---|
| 1 | **Keys and repo write access** | 8 | Do reviewing models keep Write/Edit? Rotate credentials? | Write hole **open today** (`_build_discrimination_overlay` symlinks all non-target files). `.env` is mode **0644** with **10** live keys, gitignored. **`ZENODO_TOKEN` has a leading space in its value** — measured, len 61 |
| 2 | **Nothing has run for 12 days** | 11 | Held-out ruling on exp50/51/52 (open since 2026-08-08); who authors exp55's target | exp50/51/52/54 have **never produced a run**. Last run of any kind: 2026-08-23 |
| 3 | **What ends a run** | 9 | Does the irreducible-queue alarm HALT or advise? Does a model-assigned severity float keep gating? | **`HALTED_IRREDUCIBLE_QUEUE_ALARM` killed both exp55 runs at round 1** on 2026-08-23 — the direct cause of theme 2 |
| 4 | **Fix-acceptance gate never fires** | 5 | Repair σ conflation + remove call site + correct appendix, composed | **0 rejections in 3,816**, Wilson [0.0000, 0.0010], 2 routes. "Repair is inert" refuted: it flips **3.215%**, all PASS→REJECT |
| 5 | **Wolfram licence** | 3 | Renew or drop local exact arithmetic | **Expires 2026-09-11 — 6 days.** Verified via `$LicenseExpirationDate` |
| 6 | **Archive verdicts that may be wrong** | 15 | One materiality ruling | ~133 similarity pairs dropped (27.4%, the hard cases); **~106** findings with unbacked tool-only status (CONFIRMED slice **65 of 116 = 56.0%**); 37 IDs read `CC2_F001` not `CC2-SIM_F001` |
| 7 | **The 2 changes to the mathematics** | 4 | Adopt `ν_eff = ν/\|D\|`; code the gamma unification | `ν_eff` is **the only item that changes the mathematics**. Deciding after a launch breaks cross-run comparison |
| 8 | **Dispatch runs with permissions dropped** | 9 | Workspace trust setting — **yours, not mine** | Verified by running `claude -p`: *"Ignoring 19 permissions.allow entries… this workspace has not been trusted."* Same shape as this morning's silent-tool defect |
| 9 | **Machinery built, never wired** | 5 | Merge semantics; remove-or-wire 8 dead flags | Now nameable: `discrimination_control_ask`, `discrimination_control_blocks`, `hierarchical_novelty_convergence`, `immune_memory_consume_rk0`, `latent_tagger_enabled`, `routing_enabled`, `severity_calibration_enabled`, `stall_gamma_termination_enabled` |
| 10 | Reduction Criterion placement | 6 | Separate appendix entry or folded in | Nothing blocked — ranked low deliberately |
| 11 | **Not decisions at all** | 16 | None — misextracted ask-backs | **Remove from the decision surface.** They are my work items |
| 12 | Housekeeping | 21 | Mostly none | Deferrable at no cost |

**If you decide 4 things:** workspace trust (8) → halt-vs-advise (3) → held-out ruling (2) → `ν_eff` (7). That fixes the panel *before* it runs, then opens the experiments. Wolfram (5) is independent and is the only item with a real deadline.

---

## Part 2 — the final check that had been missed

The survey's completeness critic never ran; it has now. **3 genuine gaps**, all confirmed here by direct inspection.

**GAP 1 — an anti-cooking control, open 111 days.** The 0.30 convergence threshold was deliberately pre-registered so it could not be tuned to results — correct practice — but **never validated as reachable**. `ls bench/exp40_baseline/` returns the pre-registration and feedback slices; **no recalibration artefact** (0 matches). Survey coverage of this: **zero**.

**GAP 2 — a phantom decision has been presented as your next action for 110 days.** `resources/RECOVERY.md:1421` still reads *"OPEN 2026-05-17 — γ-HARDENING CONFER COMPLETE; AWAITING FOUNDER RULING (no code changed)"*, and `CDSFL_Agent_Operational_Plan.md:911` names it as *"Next action — FOUNDER RULING"*. It was substantially discharged on **2026-05-18** by `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`, which exists. The correction was ordered on 2026-08-06 (`Document_Estate_Audit_2026-08-06.md:423`) and never applied. Note the inversion: the *status line* is falsely open while control (b) inside it (Gap 1) is genuinely open — they must be fixed together.

**GAP 3 — 3 notes in the window have no repo mirror.** `RS_Diagnostic_2026-09-04`, `Morning_Roundup_2026-09-04`, `DECISIONS_AWAITING_YOU_2026-09-03` exist only as `.txt`. Breaks `tts-output-protocol`. Self-defeating: one survey item's `how_to_verify` names `experimental_notes/RS_Diagnostic_2026-09-04.md`, which does not exist.

**A correction to my own earlier claim.** I reported that 2 backlog indices (`Handover_Decisions_2026-08-24`, `Overnight_Decisions_Index_2026-08-12`) were never opened and hid 14 further decisions. **Wrong.** Both were read and checked decision-by-decision; all are closed or queued. One contains a founder ruling of 2026-08-27 quoted in the code itself at `reference_runner_v3.py:12691` — *"Persist it."*

**Also flagged, stale:** `FOR_RULING_Worktree_Integrity_Guard_2026-08-30.md` still says the fix is not applied; it was resolved via `falsifier_verify.py:385-412`. And `resources/ONBOARDING.md:2500` carries a "Next:" that is **158 days** out of date.

---

## Part 3 — the 3 uncertainties, now settled

| Question | Conclusion | Evidence |
|---|---|---|
| Is D8 still flaky? | **No.** | **0 failures in 40 runs**, 6 under deliberate hostile load. Wilson **and** Clopper-Pearson both [0.0%, 8.8%], down from 19.4% |
| Were the outstanding items really outstanding? | **Partly not.** | 17 answered + 11 already done mechanically; 2 of 4 hand-checked complete. Survey ran 4h45m while 10 commits landed, with **no per-verdict timestamps** |
| Do the quoted figures hold? | **Yes, with 1 correction.** | Re-run: appendix 35, D12 20, D8 20, D10 57, FFAFP 33, D9/D11 **74 (reported as 69)**, suite **5153 passed 0 failed** |

**Standing rule this produces:** any survey of outstanding work must record the commit it was computed against.

---

## Part 4 — cost, and the ceiling it argues for

| Job | Agents | Output tokens |
|---|---|---|
| Task-reconstruction survey | **488** (design: 30–50) | **4,361,376** |
| Founder-ruled builds | 8 | 1,833,526 |
| Today's final check | **2 (declared ceiling)** | **318,077** |

No agent job should run without a ceiling declared before it starts, and a job exceeding it should stop rather than continue.

Written under CDSFL note standard v1.7 (26 August 2026).
