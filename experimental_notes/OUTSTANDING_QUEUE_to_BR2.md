# Outstanding queue to Bench Run 2

**Opened 2026-08-01 11:45 BST. Updated 2026-08-01 21:30 BST at commit `0a15138`.**
**Target: BR2 within 7 days, sooner if possible.**

Written because a day of firefighting produced a long tail of items that would
otherwise be lost between sessions. Nothing here is optional or forgotten; each
line is either done, blocked on a named thing, or scheduled. Update in place.

---

## A. Prose-adaptation MUST list (panel-converged, blocks every remaining run)

Source: 5-model panel review, 2026-08-01. All five converged; dissent recorded in
`Panel_Review_Prose_Adaptation_2026-08-01`.

| # | Item | State |
|---|---|---|
| A1 | Target-type detection **in the harness core**, not a config flag. Config declares intent; the harness enforces. CC2 refused to sign a plan whose enforcement lives in YAML — six silent launcher drops justify that. | **DONE** `0a15138` |
| A2 | S_k returns `NO_SCORE` for prose **in code**; `sk_enabled` forced false for prose regardless of config. Fix efficacy enters R_k as 0. | **DONE** `0a15138` |
| A3 | Tri-state verification `PASS` / `FAIL` / `NO_APPLICABLE_CHECKS`; `attempt_close` closes **only** on PASS. This is the exact line that would have marked every finding verified after the bad repair. | **DONE** `0a15138` — and REPAIRED AGAIN; see A3-note |
| A4 | `_sweep_prompt`: no ```python wrapper on prose; non-collidable sentinel delimiter. Measured: only 45 of 307 target lines reach the panel today. | **DONE** — `_sweep_prompt` sentinel, `reference_runner_v2.py:2169` |
| A5 | `_extract_routing_falsifier`: drop the `import` requirement. A prose falsifier opens the document by path; today it is discarded as empty and mints a false "ladder exhausted". | **DONE** — parse+verdict-capability test, `reference_runner_v2.py:1969` |
| A6 | B-Cell router: prose targets bypass mypy/ruff/bandit/dis/crosshair on the whole path. | **DONE (narrower than written)** — see A6-note |
| A7 | `max_irreducible_queue` retargeted from "refuse convergence" to "halt, notify, attach evidence bundle". Value reverted to default 2. | **DONE** `0a15138` (value + retarget) |
| A8 | **Free offline acceptance fixture**: real control document + shell-injection fix + correct-prose fix. Assert neither admitted, neither closes a finding, R_k does not fall. The one test that would have caught the bad repair at the moment it was made. | **DONE** `0a15138` — it caught a live defect on its first run |
| A9 | Launch preflight that REFUSES to start when target type and enabled machinery disagree. All 8 queued prose configs currently fail 3/3 checks. | **DONE** `f1c9b9a` — 3 checks, raises |
| A10 | Surface gate-rejection reasons to the panel. 50 rejections across 4 rounds; no model was told. Makes the founder's classifier design work. | **DONE** `f1c9b9a` — outcome + failed gate, not the score |

**A3-note (2026-08-01 21:30).** A3 shipped `parse -> PASS`, which was the FOURTH
wrong repair to `run_verification` in one day and the only one with measured harm:
a fix injecting `subprocess.call(..., shell=True)` into a fenced listing CLOSED
its finding, reason recorded as "verified by ast.parse of 7 fenced Python
listing(s)". A syntax check speaks about the LISTING, not the FIX, so it may only
REJECT. Now: `FAIL` on a broken listing, `NO_APPLICABLE_CHECKS` on a clean parse
with the veto recorded in `vetoes_run`, `PASS` reserved for a Python target where
tools actually ran. The veto/score distinction generalises — extraction-scoped
bandit gets the same treatment, since the measured exploit lived inside a fence.

**A4/A5/A6-CORRECTION (2026-08-01 22:05 BST).** This table recorded A4, A5 and A6 as TODO. All three
were IMPLEMENTED earlier the same day and the table was never updated. The error was stated to the
founder as fact — specifically that A5 was "the single largest open HIL-flood risk" — before the code
was read. Verified now at the line references above.

**A6-note.** A6 was written here as "prose targets bypass mypy/ruff/bandit/dis/crosshair on the whole
path". That phrasing is wrong about the architecture and the wrongness matters. Specialist routing is
keyed on CLAIM TYPE (`_classify_claim_v2`, `immune_agents.py:4274`) — mathematical / logical /
statistical / code_structural / code_behavioral — not on document type. `tool_manifest.toml` carries 21
tools, of which only 7 are Python-source tools; the other 14 (sympy, z3, scipy, statsmodels, pint,
uncertainties, stoichiometry, PuLP, astropy, rdkit, biopython, sklearn, networkx, deepseek_formal) are
CLAIM tools, indifferent to whether the claim arrived in prose or in a comment. What A6 actually does is
narrow and correct: a FILE-BASED Python-only tool aimed at a non-Python file is bypassed and reported
`NOT_APPLICABLE` rather than run and swallowed (`immune_agents.py:2985`). It does not withhold the claim
tools from a prose target. The instrument is already claim-centric; "prose vs code" governs only whether
a given file tool can physically read the file.

**THE MUST LIST IS CLOSED (A1-A10), 2026-08-01 23:35 BST.**

**A9-CORRECTION.** This document said "all 8 queued prose configs currently fail
A9's 3/3 preflight checks", and that was repeated to the founder twice. MEASURED
once A9 existed: FALSE. All eight set `take_up_slack_enabled` (the legacy routing
alias, honoured by both ingestion paths) and all eight set
`falsifier_gate_enabled`. Their only refusal is the missing target file — five of
the six prose targets do not exist on disk. The 3/3 figure predated A1/A2/A6.
Pinned by `test_launch_preflight_refuses.py::TestTheLiveConfigsWouldPass`.

**THE ITEM THAT WAS ON NO LIST AT ALL — and was the actual blocker.**
The routing ladder's prompt was code-only: it never received the target path or
text, so on a prose target with fenced listings no rung could resolve anything
and the reason recorded was factually false. Measured 41-for-41 on listing-free
prose versus 0-for-25 on the control. Fixed `1bd7605`. It predated this queue by
~2 months and appeared nowhere on it. The MUST list was necessary and was not
sufficient; what found the gap was adversarial falsification, not review. A9 is the launch gate; A10 is the
rejection-evidence feed. Neither is started. All eight queued prose configs still
fail A9's 3/3 preflight checks.

**SHOULD, before the factorial:** rejection-evidence bundles in the sweep prompt;
signature-homogeneity halt; extraction-scoped bandit as a **veto only, never a
score** (the measured exploit lived inside a fence); report fields separating
discovery convergence from fix validation.

**LATER:** a genuine prose effect stage — document invariants, negative controls
that provably fail, calibrated on local fixtures before it may admit anything.

---

## B. Already fixed today (do not redo; regression tests exist)

- `_anchor_dir_for` — scratch file no longer written beside a read-only target.
- `run_verification` — parse-check on extracted listings; refuses a no-code target
  to HIL rather than passing it. **Three wrong repairs pinned by tests.**
- S_k hard gates — gate the target's code, not its prose.
- Post-convergence settle — `CONFIRMED+verified -> CLOSED` runs once after the
  final round. C0031/C0070 were never "unresolved"; the label lagged.
- Launcher silent-drop **class** ended — all 74 RunnerConfig fields now agree
  across both ingestion paths by construction. 20 were latent.
- Test suite made offline — 62 tests were making live calls; `-m "not network"`
  never was an offline selection.
- Report records which convergence rule closed the run.
- Archive no longer written by the test suite.
- DeepSeek route corrected to `deepseek-v4-pro`; Kimi K3 wired, opt-in, off.
- Ouroboros query builder; lone-surrogate crash fixed at ingest.
- netguard terminal summary states which mode actually ran. It printed "Run with
  --netguard-strict" even when strict WAS active — a verification claim that
  misreports itself, and it briefly misled a reader today.
- Five offline STEM acceptance fixtures (`bench/tests/fixtures/stem/`): algorithms,
  numerics, statistics, structural, metrology. Same document template as the
  control, no shared claims (verified: only section headers, fence markers and
  table headers coincide). 51 tests, 9 classes, no paid dispatch.


## B2. Gap found 2026-08-01 20:50 in a fix made the same day

`bench/immune_agents.py` redirects its shadow log away from the archive **only
under pytest**. An agent (or a person) calling those functions directly for
analysis still appends to `bench/logs/immune_pipeline.log`. Thirteen genuine
lines were added that way during the prose audit — not test fixtures, real
pipeline output against the staged control document.

Not urgent (13 lines, genuine, non-corrupting) but the rule is that the archive
is not written outside a run. The redirect condition should be "an experiment run
is actually in progress", not "pytest is importing me". `CDSFL_SHADOW_LOG_DIR`
already exists as the override; the default is what is wrong.


## B3. `_verify_lint_check` confirms every code-quality finding (found 2026-08-01 20:49)

`bench/immune_agents.py:1993`. Reproduced directly:

    $ python3 -m ruff check --no-fix --output-format=concise clean.py
    rc=0   stdout: "All checks passed!"

The verifier then does `violations = [l for l in stdout.splitlines() if l.strip()]`,
so ruff's own SUCCESS message counts as a violation. A clean file reports
`LINT_VIOLATION: All checks passed!` and the B-Cell CONFIRMS the finding.

Every lint-class finding against a PYTHON target has been getting a spurious
confirmation. This is a CODE-target bug, not a prose one, so it predates the
prose work and has been live across the arc. Severity is bounded by CONFIRM-only
discipline — a finding still needs a runnable falsifier to close — but a B-Cell
confirmation feeds severity and routing.

Fix: treat rc==0 as clean regardless of stdout, and/or filter the known success
string. Trivial. NOT done now: it is in `immune_agents.py`, which the acceptance
stage is exercising, and changing verification machinery underneath the stage
that verifies it is how today's errors happened.

Raised by a background agent as a suggested task; dismissed deliberately and
recorded here instead. Founder 2026-08-01: look at it once all testing is in.
Testing is now in — B3 is the first item to take up.

---

## B4. Closed overnight 2026-08-01/02 (all offline, no dispatch)

| Item | Commit |
|---|---|
| Routing ladder made target-aware — **the blocking item** | `1bd7605` |
| Exp 53 config note corrected (it blamed S_k; mechanically false) | `1bd7605` |
| Residual sweep now runs on a halt / round-cap exit, not only on convergence | `669ac71` |
| Panel briefing no longer promises linters that do not run on prose | `669ac71` |
| B3 — ruff's "All checks passed!" counted as a violation (live all arc) | `669ac71` |
| A9 launch preflight (refuses, does not warn) | `f1c9b9a` |
| A10 rejection reasons rendered to the panel | `f1c9b9a` |

Suite 2521 passed / 0 failed, offline under `--netguard-strict`.

**STILL OPEN from the falsification, in rank order:** the critical-severity
ceiling (needs a founder ruling — the sweep cannot clear a critical and a
false-positive critical is permanent human work decided by one un-recomputed
float); the 38 stuck-CONFIRMED sub-criticals with no route to terminal; the
false-CONFIRMED hole (a valid-but-logically-wrong falsifier closed a finding
against a TRUE claim); the falsifier transport truncation + 4 skipped tests;
`escalated` not cleared on ladder exhaustion (cost only); B2 archive redirect;
docs sweep.


## B5. Wolfram access, closed 2026-08-02

Paid MCP key expired 2026-07-31 by Wolfram's own announcement; Wolfram also stopped
the recurring payment themselves. Bridge still answers (lagging enforcement) — borrowed
time, not safety. Free endpoint `agenttools.wolfram.com/mcp` added ALONGSIDE as
`WolframCloud` (no account, no key); old entry untouched; config backed up. Live after
the next client restart.

**Measured, both directions.** Computation byte-identical (−Catalan; ζ(3) to 40 dp;
Tan series; Tungsten 3422 °C; parsec as the exact rational 10246429500/(999992651·π);
eigenvalues {4,2,1}). Same `$Version` 15.0.0, same `Professional`. Two differences only:
free is **stateless** (mitigate: one call per computation — the 6-part battery ran in 4.3 s)
and has a **hard 24–40 s gateway ceiling** (`Pause[20]` OK 23.8 s; `Pause[40]` → 504;
the paid bridge completed 40 s).

**Open:** whether a free local Wolfram Engine removes the ceiling *without* losing curated
data (ElementData etc. historically needed cloud) and whether its licence permits use in a
published MIT project. Under research; nothing installed.

**DONE 2026-08-03 21:48 — Wolfram fully closed out.** The legacy bridge server entry
is removed from `claude_desktop_config.json` (it held the dead key and returned auth
failures as SUCCESSFUL results). `WOLFRAM_API_KEY` removed from `.env` — nine keys
remain, file re-locked `uchg`. The credential is ARCHIVED not deleted, per founder
instruction, at `~/CDSFL_retired_credentials/` (mode 700/600) with its full provenance.
All three stale doc mentions fixed: `docs/REPRODUCING.md` now says Wolfram needs no key,
`scripts/cdsfl_onboard.py` entry removed, and the 6 July decision register ANNOTATED
rather than rewritten — it is a dated record and its finding still stands.
Remaining config: `WolframCloud` only. No credential anywhere.

**Decision recorded — Wolfram's status.** Stays OUT of the pipeline as a verification tool.
If ever admitted as a fallback for the measured case (SymPy returns an integral *unevaluated*
— a mechanical trigger, not a judgement), the ordering is **SymPy → Wolfram → escalate**
(the always-present floor first; this inverts the 2026-06-08 directive's Wolfram→SymPy), and
the run must record **which tool closed each claim** — so a reproducer without Wolfram gets
UNVERIFIED rather than a silently different answer. Directive 12 (capability probe, graceful
degradation) remains the release requirement; the free endpoint substantially answers its
"no third party will have the founder's Wolfram bridge" clause.

---

## C. Experiments, in order

| Leg | State | Blocked on |
|---|---|---|
| Exp 53 zero-plant control | **PAUSED mid-run**, 4 rounds spent. Document cleared (7 claims repaired). | A1–A10. Restart-vs-resume decision: recommend RESTART — the 13 "irreducible" items were locked by the broken gate, so a resume carries a known artefact into the one experiment that measures what a panel leaves behind. |
| Exp 50 physics | not started | A1–A10, control result |
| Exp 51 biology | not started | A1–A10, control result |
| Exp 52 factorial (4 cells) | not started | above + **answer key public in git history**; founder ruled exposure overstated and to move on. Reseed NOT done. |
| BR2 | not started | all of the above |

---

## D. Founder decisions outstanding

1. **Restart or resume Exp 53.** Recommendation: restart (see C).
2. **`origin/exp39-experimental`** — carries the answer keys publicly. Founder:
   do not delete until the merge to main is manually confirmed.

   **[CORRECTION 2026-08-17.] "Deleting is lossless (zero commits not held
   locally)" was WRONG and is withdrawn.** That phrasing conflated two different
   things: the local clone does mirror the remote, so nothing would be lost that
   is not already on this machine — but MAIN DOES NOT HOLD THE BRANCH'S HISTORY.
   Measured: `git rev-list --count main..exp39-experimental` = **107 commits on
   the branch that are not in main**, because the milestone merge `043a0a8`
   squashed them. `326c43b` (29 July) is one example reachable from the branch
   and from nowhere else.

   Why it matters beyond tidiness: those 107 commits are the only record of the
   per-run target states. Counterfactual-repair adjudication needs the file as it
   was when a finding was raised, and 20 of 21 falsifiers that fail against
   today's file reproduce against some earlier stored version. Deleting the
   branch would not lose the findings, but it would remove the intermediate
   states that let a finding be re-tested at all.

   **DO NOT DELETE until the 107 commits are either merged non-destructively or
   deliberately declared redundant.** Neither has happened.
3. **Reseed the three exams** whose keys are public — founder judged the exposure
   overstated and elected to move on. Recorded as a deliberate decision, not an
   oversight.
4. **Archive delta** — the uncommitted `immune_pipeline.log` lines were resolved:
   127 genuine records preserved beside their run, the rest discarded.

---

## E. Known-and-accepted, not to be re-litigated

- **`Exp53_Claim_Audit_Record_2026-08-01` MUST STAY OUT OF THE REPOSITORY.** It is
  cited by the live recovery surface and it is the ONE cited document deliberately
  NOT preserved into `experimental_notes/` by the 2026-08-06 estate audit. A note in
  the tree stating that all 44 claims verify as true would itself disclose the
  zero-plant control's design — the whole point of that experiment is that the
  panel does not know the target is clean. This exception is recorded here because
  the general rule is "if the recovery surface names a document, that document must
  exist in the repository", and without this line a future tidy-up would correctly
  apply the rule and quietly destroy the control.
- **Panel confound**: two GPT-5.5 seats are byte-identical `ModelConfig`s apart
  from the label. Four architectures, not five. Founder approved injecting a
  published Codex system prompt into one seat; NOT BUILT.
- **Numbering**: keep the new sequence; docs to match. Founder: cosmetic.
- **CC2 dispatch**: needs a bounded-length instruction, not a longer timeout. It
  answers a 29k-char prompt in ~85s when told to be concise; it exhausted 300s
  three times and 900s once when unbounded.

---

Written under CDSFL note standard v1.2 (14 May 2026).


## B6. Refuted 2026-08-04 — the "wasteful re-dispatch" was not waste

The 2026-08-01 falsification listed, at LOW severity, that `escalated` is never
cleared when the routing ladder exhausts, so "the same structurally-doomed
two-rung dispatch repeats every subsequent round — paid model calls that cannot
succeed by construction". I repeated that to the founder. Estimated cost on the
control restart: ~20 findings x 2 rungs x ~12 rounds = **480 dispatches, ~$82**.

**MEASURED across all 16 archived runs before changing anything: 36 findings were
locked by an exhausted ladder, and 6 of them were later RESCUED — 17%.** All six
by a MODEL succeeding on a repeat run (Codex x3, CC2 x2, ChatGPT x1); none by
dedup. So the repeat IS the recovery mechanism, and "cannot succeed by
construction" is false.

There is no narrow version of the fix: suppressing the retry suppresses the
rescue. The $82 would have been saved by removing a recovery path that works one
time in six.

**Open, measured, NOT built:** a retry CAP would keep the rescues if they land
early and bound the cost if they do not. That needs the round-of-rescue
distribution, which was not extracted. Do not implement it on intuition — the
intuition here was already wrong once.


## B7. B2 deliberately NOT fixed 2026-08-04 — and why

The shadow log redirects away from the run archive on the condition
`"pytest" in sys.modules`. The queue says the condition should be "an experiment
run is actually in progress", not "pytest is importing me", and that is right.

**Not done tonight, deliberately.** There is no run-in-progress signal in the
runner to key on, so the fix means INVERTING the default: write to a scratch
directory unless a marker set by the runner says otherwise. If that marker is
wrong or unset on any path, a paid run's shadow log goes silently to a temp
directory and is lost.

Measured impact of leaving it: 13 genuine, non-corrupting lines, already extracted
to `bench/logs/analysis/`. Cost of getting the inversion wrong: a paid run's
shadow data. Making that change at 01:15 the night before a paid control restart
is the wrong trade, and the discipline that says otherwise is the one that
produced four repairs to one function in a day.

**Do it in daylight, before a run, with the marker wired at the runner's log-dir
creation and a test that a live run still writes to its own directory.**


## B8. Pipeline proven end to end 2026-08-04 — and what it changed

`bench/tools/simulated_bench.py` drives the REAL pipeline functions in the real
order, with a panel of five blind agents instead of paid models. **12/12 stages;
planted defect DETECTED with 5 independent demonstrations; ZERO false positives
confirmed.** Full account: `Simulated_Bench_First_Full_Run_2026-08-04.md`.

**CLOSED by this run:** the "everything is unit-tested only" gap. Tri-state
verification, the A9 preflight, A10 rejection lines, S_k NO_SCORE, the prose panel
briefing, both novelty series and the two-sided gate have now all been exercised
in a real pass rather than in isolation.

**FOUND by this run:** the fixture falsifiers carry a `<<DOC_PATH>>` placeholder
that must be substituted. Fed raw, both falsifier-bearing findings returned ERROR.
Every component correct, the seam wrong — the class no unit test catches.

**ADDED:** an honesty check comparing what an agent CLAIMS it ran against what the
runner can confirm. Justified on its first pass — 8 claimed, 7 confirmed, 1 ERROR.

**CHEAPENS an open item.** The false-CONFIRMED negative control: an agent built it
unprompted, running its falsifier against a corrected copy and recording "not
falsified", exit 0. So ASK THE PANEL for the discrimination control rather than
building machinery to synthesise a corrected copy. The DETECTIVE form (record it,
raise it, change no verdict) is already covered by ruling 3 and needs no ruling.
The DECISIVE form still does.


## B9. Provenance correction, 2026-08-05 14:05 BST

The 2026-08-04 simulated bench's five reviewers were Claude subagents labelled with
the real panel's vendor names, and their results were reported under those names.
No paid dispatch occurred in that run. The same day also holds a real five-model
panel review under the same names, so the record contained two indistinguishable
panels. Relabelled `SIM-A`…`SIM-E` everywhere; results unchanged, attribution
corrected. Standing rule added: a simulated agent never carries a vendor name.
