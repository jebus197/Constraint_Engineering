# What was actually implemented, and what was not — revised

**Revised** 2026-10-11 17:05 BST. **Supersedes** the earlier version of the same date, which was
built from the wrong sources and whose headline is withdrawn.
**Audience: a reproducing engineer.** Plain-English companion:
`~/Desktop/CDSFL_tts/What_Was_Actually_Implemented_2026-10-11.txt`.
**Producers:** `scripts/pass_b_his_rulings_2026-10-11.py`,
`scripts/read_founder_responses_2026-10-11.py`, `scripts/local_resource_budget_2026-10-11.py`.

## 1. The headline: 0.4595 of his verdicts were unreadable

**221 of 481** of the founder's annotations, Wilson [0.4154, 0.5041], exact [0.4143, 0.5052],
sit in files `grep` treats as binary. `Responses/Division_Count_And_Relegation_Panel_2026-10-08.txt`
is `ISO-8859 text, with CR line terminators`: Word writes Mac-classic `\r` endings and smart
quotes as high bytes, so `grep` sees 1 line of 3,790 chars, classifies the file binary, and
exits 1 silently. `splitlines()` splits on `\r` and found all 9 at once. **The byte count said so
throughout: 21,698 against the unannotated original's 11,370.**

| | Count | Interval |
|---|---|---|
| Files in `Responses/` | 76 | |
| CR-only line endings | 14 of 76 = 0.1842 | Wilson [0.1130, 0.2858] |
| Not valid UTF-8 | 15 of 76 = 0.1974 | Wilson [0.1234, 0.3004] |
| Annotated files grep misses | 14 of 35 = 0.4000 | Wilson [0.2555, 0.5643] |
| **His annotations grep misses** | **221 of 481 = 0.4595** | **Wilson [0.4154, 0.5041]** |

`.rtf` → `.txt` is the proximate cause and **not his fault**: a raw grep misses 3 of 19 `.rtf`
against 12 of 14 `.txt`; Fisher OR 0.031250, p = 9.108e-05; Barnard p = 4.727e-05; statsmodels
OR CI [0.004493, 0.217339]. Switch dated by Mann-Whitney U = 75.0, p = 5.044e-08 (`.rtf` median
2026-08-27, `.txt` median 2026-10-02). **Word's plain-text encoding is the defect, not the
format**; `.rtf` survives only as a 7-bit container escaping high bytes. He was told to change
nothing. Fix lives in `read_any()`; `--verify` exits 3 on any unreadable annotated file.

## 2. Why Pass A was discarded

All 5 enumeration sources were CC1's own writing: 2 `git log` passes,
`WORK_IN_FLIGHT_2026-10-07.md`, `RECOVERY.md`, `CDSFL_Agent_Operational_Plan.md` +
`CDSFL_MASTER_TASK_LIST.md`. **0 read `Responses/`.** So it could not detect an instruction he
gave that CC1 never recorded — the exact question asked. **29 of his 200 window annotations have
no verbal trace in those sources**, 0.1450, Wilson [0.1029, 0.2005], and that is a **floor**: the
predicate measures topic coverage, not compliance. Stopped on his instruction at 48 agents and
200 of 438 items verified, **0 refuted**; harvested to
`scratchpad/pass_a_tree_state_map.json` as a hand-consulted lookup only.

## 3. Pass B — 248 of his annotations read, 12 mechanically checkable, 8 landed

Run `python3 scripts/pass_b_his_rulings_2026-10-11.py`. **LANDED 8 of 12 = 0.6667**,
Wilson [0.3906, 0.8619]; **NOT LANDED 4 of 12 = 0.3333**, Wilson [0.1381, 0.6094].

| Verdict | Ruling | Evidence |
|---|---|---|
| LANDED | gamma active in all cases (10-08) | `_gamma_is_estimable` in `reference_runner_v3.py` |
| LANDED | no ladder cap (10-05) | `routing.DEFAULT_MAX_RUNGS == 0` |
| LANDED | self-rung routes back (10-06) | `route(self_rung_enabled=True)` |
| LANDED | burst not off (10-05) | `burst_mode == "auto"`; runner gates `!= "off"` at `:15667` |
| LANDED | no hard-coded roster size (10-07) | 0 offending comparisons in 3 live modules |
| LANDED | `programme` vs `program` (10-05) | now in `.claude/CLAUDE.md` — **6 days late** |
| LANDED | invented-terminology guard | `note_vagueness_lint.py` + 2 vocabulary guards |
| LANDED | token-quota arm (10-04) | hook demands `get_usage`; directive binds it |
| **NOT** | immune memory on (10-05) | default `False`; 13 of 16 setting configs say `True` |
| **NOT** | fold fixes forward (10-05) | default `False`; 1 of 32; live-tree guard **exists** |
| **NOT** | completion signal (10-08) | cap built, **signal not**; `~20` callers of `call_claude_cli` |
| **NOT** | round cap 10 + recommendation | `max_rounds == 21`; no recommendation printed |

## 4. FOLLOW refused a harmful fix

43 of 47 configs pin `burst_mode="off"`, which read as wholesale defiance with an obvious bulk
remedy. **33 of the 43 are historical records of archived runs** — 0.7674, Wilson [0.6226,
0.8685] — so editing them falsifies the experimental record. Of the remaining 10, **5 are the
exp52 factorial cells** where the setting is part of the design. **No config was changed.**
`_historical_off_configs()` computes the split on every run.

## 5. The permanent resource fix, both arms

**Local.** 48 agents issued **2,310** Bash calls, **263 pytest**, on 8 cores / 8 GiB. Binding
constraint is **memory**: 364.7 MiB per pytest tree (42 RSS samples) against ~1.9 GiB headroom →
~5 heavy processes, while the harness cap `min(16, ncpu-2) = 6` is **core-derived**. Budget
**2 heavy / 6 light**. And 263 invocations answered what **1 board** (3998.65 s) answers: 1.14×
at the cheapest observed rate, 4.26× at the 3-file rate.
Mechanism: `scripts/local_resource_budget_2026-10-11.py` (SymPy monotonicity; z3 `unsat` on any
budget `< 1` or `> core_ceiling`) + `~/.claude/hooks/local_resource_budget.py` (PreToolUse on
`Agent|Task|Workflow`; refuses pytest in delegated work; **never** blocks CC1's own pytest;
fails open) + a standing directive + `test_the_local_resource_budget_binds_2026-10-11.py` (15;
**mutation kills 3**).

**It caught its own author.** 2 concurrent pytest trees → load 5.42, headroom 1224.2 MiB, budget
1 while 2 ran; the board was killed. That exposed a defect: the load trigger at `0.7 × 8 = 5.6`
**did not fire at 5.42**. Now `0.6 × cores` **plus an independent memory arm** firing when
headroom `< 2 × per_process`; both verified to fire alone.

**Token.** His 2026-10-04 note — *"nearly out of my weekly allowance … I usually only barely
scratch the surface"* — **sat unread for 7 days** in a grep-blind file. Plan limits are readable
only in-session (`mcp__ccd_session_mgmt__get_usage`), so the hook **demands** the check on every
allowed fan-out and the directive binds it. Baseline 2026-10-11 16:40 BST: 5-hour 28%,
**weekly all-models 33%**, weekly Fable 13%, extra usage **disabled**, £0.00 of £150. His claim
is **correct** on the record and the spike had reset.

**`ultracode` disambiguated on his challenge.** The harness says *"token cost is not a
constraint"* and *"use the Workflow tool on every substantive task"*; collapsing them produced
48 agents. Trigger is the harness's; interpretation is the project's: **spend the allowance on
DEPTH, never BREADTH.** Of 12 errors on 2026-10-11, **10 (0.8333, Wilson [0.5520, 0.9530],
binomial p = 0.0193)** were catchable by reasoning *before* running; 8 of the 10 were predicate
errors.

## 6. Claims withdrawn

1. **"8 of 17 live."** Enumerated from recollection.
2. **"2 configs hold prose where a boolean belongs."** Both carry `true` at top level; the
   sentence is in a `_`-prefixed annotation block. CC1's `_flatten` descended into documentation.
3. **"The figures are in `docs/REPRODUCING.md`."** 0 hits; diff line numbers read as file lines.
4. **"12 of 17 already ruled."** The predicate counted *"OPEN FOR HIS RULING"* as a ruling.
5. **THE ADJUDICATION FIGURES, IN FULL.** 0.7603 vs 0.4003 on 1093/1304 implies a statistics
   share of **0.6142**, not the reported **0.9684**; for 0.9684 the rate would need to be
   **14.6356 > 1**, impossible. No producer exists, so which figure is wrong is undetermined. It
   reached the document he read. His challenge — *"Ae you even checking if these numbers make any
   practical sense before writing them?"* — is answered: no.
6. **"221 of 691 = 0.3198."** The denominator counted 210 markdown headings from
   machine-generated `.md` files. Corrected: **221 of 481 = 0.4595** — worse, not better.

## 7. Awaiting his ruling

1. Immune memory default. 2. Fold-fixes-forward default (protection exists). 3. The completion
signal (~20 callers). 4. `max_rounds` 21 vs his 10, plus the printed recommendation. 5. The 10
future-run configs pinning burst off, 5 being factorial cells. 6. Error convention —
**recommendation: two-sided**, which settles 10-vs-11 at 11 (T=11 holds 0.038126, T=12 fails
0.059430; one-sided passes even T=13 at 0.042002). 7. Whether to repair the adjudication gap now
its premise is withdrawn. 8. `hil_review`'s unexecuted ON path, 0 of 47 configs. 9. The 5 stale
worktrees, 2.5 GB — **POINT, NEVER PRUNE**. 10. Whether the other 233 annotations outside the
13-day window should be audited.

---

# ADDENDUM, 2026-10-11 18:10 BST — the older 233, the 4 lessons, and a gap in this note's own predecessor

**The founder's single reading file is now `~/Desktop/CDSFL_tts/Consolidated_For_Your_Evening_2026-10-11.txt`.**
This note is its technical companion.

## A. This note's predecessor dropped 3 of his 5 open decisions

He asked whether the consolidated file carried the decisions from the **unanswered** morning report
of 2026-10-09. Measured against `experimental_notes/Morning_Report_2026-10-09.md` § "The 5
decisions, unchanged and still yours":

| His decision | In the earlier TTS? |
|---|---|
| 1. The 2 gate properties (determinism + exchangeability) | **NO** — 0 mentions of either term |
| 2. Which error convention | yes — 1 mention |
| 3. One false-alarm proportion for relegation | **NO** — 0 mentions, and **never answered by him** |
| 4. Anchor set re-run per window vs fixed at start | **NO** — 0 mentions |
| 5. Whether to repair the domain verdict gap | yes — 1 mention |

**2 of 5 carried, 3 dropped.** Item 3 had never been answered at all. The file written to stop
decisions going missing lost 3 of them. All 5 are restored in the consolidated file, numbered 1–5.

## B. Which morning reports are answered

Mechanically, by presence of `#` annotations in `Responses/`:
`Morning_Report_2026-10-07.txt` → **11 annotations, ANSWERED**.
`Morning_Report_2026-10-09.txt` and `Morning_Report_2026-10-08.txt` → **not in `Responses/`, UNANSWERED**.
So his "last unread morning report" is 10-09, and 10-07 is the one he answered — which is where
the 4 panel lessons below were ruled on.

## C. His 4 panel lessons of 2026-10-07 — ruled "wire it in", measured today

All 4 carry the identical response: *"We should use it. Wire it in all simulated and real runners
going forward."* `RECOVERY.md` still lists them under **"OPEN FOR HIS RULING, carried forward"** —
they were ruled 4 days earlier. That is `feedback_already_ruled_and_misread_rates` confirmed
concretely.

| Lesson | Panel | `reference_runner_v3` | Verdict |
|---|---|---|---|
| 1. substance test, refuse a merely non-empty reply | present | **comment only, line 9663** | NOT LANDED |
| 2. a retry must not erase the attempt it replaces | `_preserve_prior_attempt` | 19 `preserve|backup|overwrit` hits, **0 concerning a reply** | NOT LANDED |
| 3. state DETECTED from content, not declared | `_detect_round_kind` | `detect_target_kind` at **:1811**, reads path and bytes | PARTLY — principle honoured for *target* kind; the panel's round-kind form has no runner analogue |
| 4. one definition imported, not restated | — | — | **UNVERIFIED** — `REQUIRED_FIELDS` exists nowhere, panel included; the probe name was invented |

**A first pass reported "0 of 4" and that figure is withdrawn.** It rested on `grep -icE` patterns
using `\|` (BRE alternation) under `-E`, so every pattern searched for a literal pipe and matched
nothing — the **7th predicate error of the session**, same family as the other 6.

## D. The older 233 annotations, triaged

233 predate 2026-09-29 (2026-08-27 → 2026-09-28), 52,775 chars across 19 files.

| Class | Count | Interval |
|---|---|---|
| imperative instruction | **87 of 233 = 0.3734** | Wilson [0.3138, 0.4371] |
| question | 63 of 233 = 0.2704 | Wilson [0.2174, 0.3308] |
| observation / context | 78 of 233 = 0.3348 | Wilson [0.2773, 0.3976] |
| acknowledgement | 5 of 233 = 0.0215 | Wilson [0.0092, 0.0492] |

The 87 are a **backlog, not a defect list**: many are conditional ("fix it if not already fixed")
and a large share were satisfied by work in the intervening fortnight. Verifying each against the
current tree is itself a day's work — that is decision 14.

**3 worth naming now.** (i) 2026-08-31, the macrophage cell *"should have been fully functional in
our runners for some time"*, with shadow-code promotion repeatedly discussed. (ii) 2026-08-31, a
direct instruction to **remove personal and disability directives from the directive set fed to the
models** — a privacy matter, not an engineering one. (iii) 2026-09-17, set a named value to **6** in
the next simulated run and add it to the programme of study, because *"There is no point having
machinery that in effect does nothing."*

**And his own statement of the pattern, 2026-09-21:** *"Even now, several sweeps in over the last 3
months, we keep finding things we built but never enabled."*

## E. Also verified landed

His ruling of 2026-09-28 — *"There should be no paid dispatches without my express authorisation"* —
holds: `select_models` raises `SystemExit` unless the ledger names the round **and** carries
`founder_verbatim`, and module-level `MODELS` is intersected with `FREE_SEATS` so an importer cannot
bypass `main()`.

---

# ADDENDUM 2, 2026-10-11 21:25 BST — his 18 responses worked

## Encoding: the reader was reading his files and mangling them

`errors="ignore"` DROPPED every curly apostrophe. *"I don't get it"* → *"I dont get it"*.
**256 characters of his writing lost across 14 of 29 plain-text files, 0.4828,
Wilson [0.3139, 0.6557].** Codec is **Mac OS Roman**, confirmed 3 ways: his Word dialog shows
"Western (Mac OS Roman)" + "CR only"; `0xD5` ×11 and `0xD4` ×3 are the right/left single quotes
there (O-circumflex under cp1252); and `file` reports `ISO-8859 text, with CR line terminators`.
`decode_bytes()` now tries UTF-8 strict → the single-byte codec the **quote bytes** point at →
visible `errors="replace"`. Both single-byte codecs decode *every* byte, so "try until one
works" proves nothing; the quote bytes are the discriminator. **Re-measured: 0 files decoded
incorrectly, 0 characters lost, all 18 responses read back with apostrophes intact.**
He changes nothing — Word cannot save `.md`; the `.md` suggestion is withdrawn.

## Note-standard stamp, now mechanical

`missing_standard_stamp()` in `note_vagueness_lint.py`, scoped to `experimental_notes/` and
`*_tts/`. **A first fix added it to `blocking()` only and reported 0 findings on plainly
unstamped files, because `main()` calls `partition()` directly — an unwired addition, inside
the fix for unwired additions.** Now wired at the CLI. Guard: 6 tests. 24 older notes lack a
stamp; the ratchet holds them as a backlog.

## Rulings landed

| # | Ruling | Action |
|---|---|---|
| 1 | "Yes. Use both" (gate properties) | pinned in the division producer; **0 live references** to that machinery |
| 2 | "Yes. Use the two sided setting" | `TWO_SIDED_Z` named, `PER_SIDE_Z` recorded beside it, guard recomputes 0.038126 at T=11 vs 0.059430 at T=12 |
| 6 | immune memory on by default | `immune_memory_enabled → True`; `immune_memory_consume_rk0` stays `False`; 31 configs inherit; guard updated, mutation-verified |
| 10 | burst: mark and correct | 10 future configs → `"auto"`; 33 archived **untouched** and recorded in `archived_run_confounds.json`; guard 4 tests |
| 15 | "Set it to 6" | **already done** — `exhausted_round_threshold: 6` vs `max_rounds: 8` in all 3 exp56 configs |

**Withdrawn:** the claim that the 5 exp52 factorial cells were a design decision. `burst_mode`
does **not** vary across them — the factors are `divergence_channel_enabled` and
`feedback_channel_enabled` — so pinning it off measured those channels under a crippled runner.

## Ruling 7 refused, with cause

Fold-fixes-forward stays off. His condition had 2 halves. **Satisfied:** `_apply_back_setup`
uses a per-run copy, *"The repo file is never modified"*. **Not satisfied:** the runner states
at **:5419** and **:6049** that it *"rewrites the reviewed target between rounds"*, and
`_refresh_stale_corrected_copies` exists to repair evidence staled by that mid-run rewrite.

## Item 8 recovered

The "better way" was **incremental stream-json parsing**. Stronger than a completion marker: a
dead seat never prints the marker either, and the clock cannot separate working from churning
(**20.455 s vs 20.816 s per call**, measured). A live count separates all 3 states. Same item
as the lapsed stream-json trigger — 1 piece of work, not 2.

## Still owed

**Item 11** — *"Verdict: Verify and fix all"* on the 4 panel lessons. Live code across both
runners; not rushed at the end of a long session.

---

*Written under CDSFL note standard v1.7.*
