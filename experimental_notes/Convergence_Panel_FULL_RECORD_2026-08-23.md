# Convergence panel, 23 August 2026 — the verbatim record

**Two reviewers, CC2 and Fable, both Max-plan and free, both sandboxed in
throwaway git worktrees so their Bash could not reach the repository.**
Brief: 6,142 characters (`BRIEF.md` in this directory).

The founder overrode this project's no-compelled-convergence rule for **Q1
only**, to stop the question circling. Q2 and Q3 preserve disagreement.

**This file is COMPLETE AND UNEDITED.** Both reviewers refute CC1 on Q1's
premise and on Q3, and Fable additionally refutes CC1's composition report.
Nothing is trimmed.

---

## Claude Opus 4.7 (`cc2`)

- returned: **yes**
- elapsed: 1288.2s
- length: 12,842 characters

### Verbatim response

## Q1 — converged answer

**Site: the FIX-2 sub-critical arm inside `_apply_routing`, `bench/reference_runner_v2.py:3358-3363`. Approach: widen the admission set from `"ERROR"` to `{"ERROR", "NON_DISCRIMINATING"}`, keeping the one-attempt `error_routed` guard and the transport-dead protection.** That is Fable's site and Fable's approach. CC2 chose the *same* site — its `DISC_INDETERMINATE` anchor is only where it parks a named constant. Two of three converged; the table in the brief counts them as different because it names the first hunk's anchor rather than the change.

I take CC2's naming with Fable's minimality: define `NON_DISCRIMINATING_VERDICT` next to the DISC constants, use it at the write site (`:2904`) and the read site (`:3362`), so the two mechanisms cannot drift on a bare literal.

**I drop CC2's fourth hunk** (clear `mechanical_fault`, stamp `discrimination["superseded_by"]`). It fixes a real record defect, but `mechanical_fault` is written at exactly one place (`:2908`) and read by *nothing* in production code — `grep` across `bench/` and `scripts/` finds only that write and test assertions. It changes no decision the runner makes. Ship it as its own task with its own test.

Measured, on the disposable copy, at parent `36ab4e3` (`reference_runner_v2.py` is byte-identical at HEAD):

- Recommended patch + Fable's test file: **1 failed, 3619 passed, 24 skipped** — the one failure is the known pre-existing `test_falsifier_cannot_read_the_key` baseline failure.

### Why not Codex's site

Codex's guard is `falsifier_verdict == "CONFIRMED" AND discrimination.outcome == DISC_FAILED`. I drove the real gate and the real control over all four reachable configurations:

```
blocks=False sev=0.3 : verdict='NON_DISCRIMINATING' status='CONFIRMED'  escalated=True
blocks=False sev=0.95: verdict='NON_DISCRIMINATING' status='CONFIRMED'  escalated=True
blocks=True  sev=0.3 : verdict='NON_DISCRIMINATING' status='OPEN'       escalated=True
blocks=True  sev=0.95: verdict='NON_DISCRIMINATING' status='OPEN'       escalated=True
```

`falsifier_verdict` is never `CONFIRMED` when the control fails — `_apply_discrimination_control` overwrites it at `:2904` before routing ever runs. Both Codex hunks are therefore inert. With Codex's patch applied, every real-pipeline failure from CC2's and Fable's tests still fails (10/10, unchanged from parent). Its own test passes only because the test hand-builds a state the runner cannot produce.

### The brief's premise is false, and that is the finding

> "A falsifier that fails the discrimination control is CONFIRMED — it fired — so such a finding never reaches the ladder at all."

It is stamped `NON_DISCRIMINATING` and `escalated=True`. **Criticals already reach the ladder** — CC2's critical regression test passes at the parent, unpatched. The hole is sub-criticals only, because the severity branch admitted `ERROR` and nothing else. CC2 and Fable both used their tools, caught this, and said so in their responses. Codex had tools on its route (`call_openrouter(..., tools=TOOLS.TOOL_SPECS)`) and did not check.

### Your second claim is refuted: there were no three failures

All three rungs were rejected with *identical* evidence at parent **and** with patch — `Interrupted: 1 error during collection`. I ran the harness's own extractor:

```
cx     extracted 1403 chars -> SyntaxError line 52
cc2    extracted 5390 chars -> SyntaxError line 148
fable  extracted 2853 chars -> SyntaxError line 84
```

`build_acceptance.py:92` uses `TEST_FILE:...```(?:python)?\n(.*?)``` ` — non-greedy. Every one of the three test files contains a fake model reply carrying a ```` ```python ```` fence, because a fence is what the code under test parses. The extractor truncated all three mid-string. **Fourth harness defect, fourth false verdict about a model's work.**

With a faithful extractor, in the disposable copy: every SEARCH block matched exactly once, all three patches applied, and **every writer's own test passed** — Codex 1/1, CC2 12/12, Fable 5/5, against 11 of those 18 failing at parent. The brief was not under-specified. It was *wrong about the cause*, and two of three writers repaired the brief before repairing the code.

Two harness fixes follow, and the first is the important one:

1. `build_acceptance.py:187` accepts any non-zero `rc_before` as "fails at parent". pytest returns 2 for a collection error and 5 for nothing collected — neither is a failing test. Require `rc_before == 1`; treat 2/3/4/5 as `ERR_HARNESS`, which the module already defines at `:66` and never uses here. A test that errors identically before and after has discriminated nothing — this is your own discrimination control, applied to the acceptance gate.
2. `:205` does `src.replace(search, replace, 1)` with no uniqueness check. A SEARCH block matching twice silently patches the first occurrence. None of the eight accepted patches hit it; it is still live.

### What the test must assert

Fails at parent, passes with the patch:

- **The defect.** Sub-critical (severity 0.3), corrected copy supplied, falsifier that fires on both copies, `routing_enabled=True`, `route()` recorded → `route()` called exactly once for that finding. At parent: zero calls.
- **One attempt.** After a rung genuinely reaches a model, `error_routed is True`; a second round does not route again.

Passes on both sides — these are the guards, and a patch that breaks one is wrong even if the two above go green:

- **Premise.** Drive the *real* gate and the *real* control: `falsifier_verdict == "NON_DISCRIMINATING"` and `escalated is True`. If this ever fails, the fix is aimed at a state the runner does not produce.
- **Critical regression.** A critical `NON_DISCRIMINATING` is still routed.
- **No widening.** Sub-critical `UNTOOLABLE` not routed; a sub-critical whose control *passed* not routed; `routing_enabled=False` routes nothing and writes no `error_routed`; an unescalated finding not routed.

And a negative constraint on the test itself: **no assertion may construct `falsifier_verdict == "CONFIRMED"` together with `discrimination.outcome == DISC_FAILED`.** That state is unreachable, and a test that builds it measures the test, not the runner.

One accepted limitation to record: `error_routed` now gates two instrument-fault classes, so a finding routed once for ERROR gets no second climb if its replacement falsifier later fails discrimination. That is FIX-2's intent (one ladder climb per finding, not per fault), but the key name now under-describes what it guards.

---

## Q2 — sequentially conflicting, and I can show the safe order

Not exclusive. Measured pairwise, applying SEARCH blocks in order:

```
T02 -> T03                 CLEAN
T04 -> T05                 CONFLICT (T05 hunk3 matches 0)
T05 -> T04                 CONFLICT (T04 hunk2 matches 0)
T02 -> T03 -> T04 -> T05   CONFLICT (T04 hunk3, then T05 hunk3)
```

So T04 and T05 collide **with each other**, independently of T02/T03 — the composition report's framing ("stop matching once T02 and T03 land") is only half of it. Every collision is the same shape: two additive edits anchored on the same few lines.

I rebased two hunks and applied all four:

- **T04 hunk3** over T03's inserted `_to_ledger(cid, e, "UNTOOLABLE")`.
- **T05 hunk3** over T04's equipment guard.

Result: the file parses, and all four tasks' tests pass together — **112 passed**. Full suite on the composed tree: **1 failed, 3726 passed, 24 skipped** — the same pre-existing baseline failure, no new ones.

**Safe order: T02 → T03 → T04 → T05.** Two things in that merge are not mechanical, and they are the reason a rebase needs a decision rather than a script:

1. **T04's guard must fall through, not return.** As written it writes `status = "UNCONFIRMED"` and returns early. Once T05 lands, that would be the one status write in the runner leaving no logged transition — in a patch whose entire claim is that `resolve` is the single chokepoint. I placed T04's guard *after* T05's authority substitution and had it set `status, merged_into, adjudicator = "UNCONFIRMED", None, "runner"`, then fall through to T05's log.
2. **T05's vocabulary table becomes false.** `UNCONFIRMED` is declared `in_from: (OPEN, CORROBORATED, CONTESTED, WITHHELD)` with `who_may_assert: ("mechanical",)`. T04 legitimately writes UNCONFIRMED *from* CONFIRMED or REFUTED, *by* the runner. `in_from`/`out_to` are serialised by `export_status_vocabulary` (T05 hunk 13) and never enforced, so there is no runtime contradiction — the exported vocabulary would simply misdescribe a transition the runner performs. Add `CONFIRMED` and `REFUTED` to `UNCONFIRMED.in_from`, and `"runner"` to its `who_may_assert`.

Nothing here is exclusive. T04 keys on **did the instrument run** (`falsifier_verdict`); T05 keys on **who is entitled to write this status** (`adjudicator`). Orthogonal predicates over the same chokepoint. Both can be true at once, and after the rebase both are.

---

## Q3 — leave it out of the schema, because it is already in there three times

The `rg` searched for the words. The quantities are present under other names, and all three are in the schema, not the operating directives:

1. **Sufficiency** — `cdsfl_core_formal.md:275`, §10, with a formal per-round predicate at `:310`. It also already carries the *simplicity of output* admissibility rule, at `:305`: "Marginal observations (style, naming, micro-optimisation that does not affect correctness) MUST NOT be emitted as material findings."
2. **The trade-off itself** — `cdsfl_core_formal.md:372`, "Objective and Diminishing Returns": value-weighted not count-weighted, converge when ΔV(K) is small, plus Guard 1 (never downgrade a dull material defect for being uninteresting) and Guard 2 (name a specific mechanism to justify continuing). Those two guards are precisely the failure modes a naive simplicity term would introduce.
3. **Simplicity of the fix** — `docs/MATHEMATICAL_APPENDIX.md:200`: "ν (re-injection rate) … Localised one-line changes have low ν. Changes to shared interfaces have higher ν." Break-even ν\* = σ·R·q / (1 − q·R·(1−σ)) at `:224`, and the hard exit at `:228`: "If ν > ν\*, the cycle is net harmful … stop fixing and report."

Your framing — not the same quantities, two sides of one coin — **is already the inequality ν ≤ ν\***. Sufficiency is the benefit side (σ·R·q, what the fix buys). Simplicity is the cost side (ν, the chance the fix breaks something else). The coin is the comparison between them. It does not need inventing; it needs naming.

**So: add no status, no scoring term, no gate, no admissibility rule.** Three doc actions, and one experiment that is not a doc action:

- One line in the appendix naming ν as the simplicity term and ν ≤ ν\* as the simplicity/sufficiency trade.
- Reconcile `cdsfl_core_formal.md:592`, which classifies "Simplicity default | Behavioural | No" under "Non-Formalisable Directives (Prose Only) … formalising them would be false rigour" (`:350`). That row is true of the *assistant's directive* and false of the *concept*, which the appendix formalises. Keep the row, add the pointer.
- Cross-reference §10 and the diminishing-returns section from the glossary entry, since a reader who searches "simplicity" currently finds only FFAFP step 4.

**The one real gap is a measurement, not a rule.** ν's input is a constant: `compute_rk` (`reference_runner_v2.py:7267`) derives `nu_eff = 1 − (1−nu_b)(1−(1−sk)·nu_f)` with `nu_b=0.05, nu_f=0.20`, depending on nothing about the fix — not its size, not how many places it touches. So the simplicity side of the coin is currently a constant. `bench/dm/_fix_complexity.py` exists to supply the missing measurement, has tests (`bench/tests/test_fix_complexity.py`), and has **zero non-test callers** — BUILT and TESTED, not ENABLED.

That wiring is the only change discussed here that would alter bench compute: it feeds `check_sk_threshold` (`:7624`, called live at `:7769`), which decides `SK_REJECTED`, which scores +3.0 in feedback priority and enters the next round's prompt. By this project's own test — would its absence waste bench compute? — it is the one item that answers yes, and therefore the one that needs a pre-registered experiment rather than a doc edit. The module's own header already records DeepSeek's caveat that must survive into that decision: a hidden complexity index is good for anti-gaming and is not an enforcement mechanism, and it is a percentile rank, not a re-injection probability.

Where I differ from you: on Q2 I agree and add that T04/T05 conflict with each other independently, and that the merge carries one design decision plus one table edit. On Q3 I disagree with the premise — three treatments exist, and the answer to "was this ever decided?" is yes, three times, never once collected under those two words.

---

## Fable 5 (`fable`)

- returned: **yes**
- elapsed: 1257.1s
- length: 9,926 characters

### Verbatim response

# Q1 — Converged answer, with one correction to the question itself

**First, a finding that changes the question.** The brief says all three attempts "failed to make their own test pass." I re-executed all three. **None of them failed. The harness failed all three.**

- `parse_test` in `bench/build_acceptance.py:92` extracts the model's test with `` r"TEST_FILE:\s*([^\n]+)\n+```(?:python)?\n(.*?)```" `` — a non-greedy match with **no line anchor** on the closing fence. All three T01 tests contain ```` ```python ```` inside a Python string literal (the stubbed model reply each test feeds to the routing ladder). The harness cut each test file at that embedded fence and wrote a truncated file.
- Reproduced mechanically: the harness regex extracts 1403/5390/2853 chars for rungs 1/2/3, each ending mid-string; all three fail `compile()` with "unterminated string literal."
- `results.json` confirms the signature: all three rejections are "Interrupted: 1 error during collection" in 0.19–0.33s — **before AND after the patch**. A verdict that is identical with and without the patch is measuring the harness, not the patch.
- Re-run with correct extraction at parent `36ab4e3c`: **rung 1 (Codex): 1 fail at parent → 1 pass patched. Rung 2 (CC2): 6 fail → 12 pass. Rung 3 (Fable): 4 fail → 5 pass.** Full suite on the Fable-patched tree: zero new failures against a same-environment baseline (the 8 failures in my no-`.git` copy are identical unpatched).

The parent commit message reads "Third harness defect tonight, third false verdict about a model's work." This is the fourth, and it produced three more false verdicts. Fix: anchor the fence match (`` \n```\s*$ `` multiline) or take the *last* fence.

**Second, the brief's premise is false, and that decides the site.** The brief says a discrimination-failed falsifier "is CONFIRMED — so it never reaches the ladder at all." Measured: `_apply_discrimination_control` (`reference_runner_v2.py:2901–2917`) stamps `falsifier_verdict = "NON_DISCRIMINATING"`, `escalated = True` on every DISC_FAILED — so a **critical** already reaches the ladder via `escalated AND verdict != CONFIRMED` (`:3370`). The real hole is one level down: the sub-critical arm at `:3362` admits only `ERROR`. CC2 and Fable both independently measured this and said so in their responses; Codex trusted the brief.

**The converged answer: Fable's site — the FIX 2 ERROR arm at `:3362` — with Fable's one-hunk widening** (`verdict not in ("ERROR", "NON_DISCRIMINATING")`, same `error_routed` one-attempt guard). Reasons, all tool-backed:

1. It is the only site consistent with the measured defect. Codex's patch, applied and cross-tested against the real-gate test: **4/5 tests still fail** — its `_disc_failed` guards defend a state (`verdict=CONFIRMED` + DISC_FAILED) the runner cannot produce, because the helper always rewrites the verdict, cached hits included (`:2894–2899`). Its own test passed only by fabricating that impossible state.
2. `NON_DISCRIMINATING` is the same admission class as `ERROR` — broken instrument, not refuted claim — and the helper's own docstring (`:2822–2826`) already promises "the state the routing ladder already absorbs." Fable's hunk makes that promise true for sub-criticals.
3. Convergence is 3-of-4 writers, not 1-of-3: CC2's operative hunk is byte-equivalent widening at the identical site, and the quarantined direct-write (`QUARANTINE_T01_model_written/runner_second.diff:81`) is the same line again. Codex is the sole outlier and is the one that accepted the false premise.
4. CC2's extra hunks are not wrong but are a **second defect at a second site**: after any routing resolution (`:3405–3424`), stale `mechanical_fault` survives on a CONFIRMED entry (measured: CC2's suite on the Fable-patched tree — 10/12 pass, the 2 failures are exactly the stale-flag assertions). `mechanical_fault` has no runtime consumer, so it is record-truth, the 6-stale-flags class. File it as its own finding with its own test; don't bundle it under "one site, one approach."

**What the test must assert** (fails at parent, passes with patch): drive the **real** gate — mini-repo, corrected copy, non-discriminating falsifier, `severity < 0.7`, `discrimination_control_blocks=True` — then (a) precondition: `falsifier_verdict == "NON_DISCRIMINATING"`, `escalated is True` (passes both sides; pins the premise); (b) **the fix**: `route()` receives the finding — at parent it is called zero times; (c) after a resolving rung: `status == "CONFIRMED"`, `verified is True`, `escalated is False`, new falsifier adopted; (d) non-widening guards (pass both sides): `UNTOOLABLE` still skipped, sound falsifier not routed, `error_routed` spent after one reached attempt, `routing_enabled=False` a no-op. Rung 3's test file already is exactly this. And keep fences out of test string literals until the harness regex is fixed.

**On CC1's "under-specified brief" claim:** partly right, wrong conclusion. The brief was *mis*-specified (false premise), and that fully explains the one divergent site — Codex inherited the error. It explains nothing about failure, because there were no failures: three two-sided-valid patches, three false rejections by the instrument. The evidence points at the harness, not the brief and not task difficulty.

# Q2 — Sequentially conflicting, and one of the two recorded conflicts is manufactured

Measured, not inferred:

- T02 (7 hunks) + T03 (8 hunks) apply clean at parent. On top of them, **T04 fails exactly one hunk** — hunk 2, because T04's SEARCH contains the two lines around `e["falsifier_verdict"] = "UNTOOLABLE"` (`:2984`) into which T03 inserted `_to_ledger(cid, e, "UNTOOLABLE")`. The union is trivially coherent: keep the ledger line, widen the demotion to `TERMINAL_STATUSES`. Textual, not design.
- **T05's recorded conflict is a composer artefact.** On a clean T02+T03 tree, T05 matches **14/14**. The composer (`scripts/build_experiment_compose.py:109–123`) `break`s on a failed hunk **without reverting the hunks already written** — T04's hunks 0–1 stayed in the tree, and against that half-applied T04, T05's hunk 2 fails, reproducing the report's exact wording. The composer needs rollback-on-partial-application; without it every conflict report downstream of the first is untrustworthy.
- The only genuine T04↔T05 overlap is inside `FindingRegistry.resolve`: T04 adds an equipment-failure guard, T05 adds tool-only-status enforcement, at the same chokepoint. They are two **independent admission rules** — both can hold, in either order; nothing about one negates the other. Not exclusive.

**No pair is exclusive.** Safe order: **T02 → T03 → T05 → T04**, rebasing two T04 hunks — hunk 2 re-anchored over T03's ledger line, hunk 1 re-anchored inside T05's rewritten `resolve` body (place the equipment-failure guard after the merge-cycle and tool-only checks, before the final status write). Rebasing T04 (5 hunks) onto T05 (14) is the smaller rebase than the reverse. One semantic note for the rebase: a model attestation of CONFIRMED on an equipment-failure finding hits both guards; equipment failure should win — a status substituted by T05 must still pass T04's guard, which the chokepoint ordering above gives you for free.

# Q3 — My verdict (disagreement preserved)

CC1's `rg` result verifies: no treatment in `MATHEMATICAL_APPENDIX.md`, `cdsfl_topology_formal.md`, or the glossary beyond the FFAFP line — every existing anchor governs the assistant, not the schema.

My position: **sufficiency belongs to the schema and is already in it; simplicity does not belong in adjudication, but does belong — as one line — in acceptance.** Split by what each quantity is:

- **Sufficiency is a truth property and is already mechanised.** The two-sided gate (fails-at-parent / passes-with-patch / suite-green) *is* the sufficiency test for a fix, and the falsifier verdict is the sufficiency test for a finding. Nothing to add.
- **Simplicity is not a truth property.** A simpler patch is not more true; putting it into adjudication as a score or gate would let a preference influence a truth decision — the model-voting failure class re-entering through the schema. Never a scoring term.
- **Where it earns one line: selection among candidates that all pass the gate.** Today's Q1 is the live worked example — three valid patches, and the choice among them had to be made by a compelled-convergence panel because no rule existed. That is bench compute the absence already wasted, which is this project's own admission test for new machinery. The rule: *sufficiency gates; among gate-passers the minimal sufficient patch wins; anything a larger patch fixes beyond the brief is filed as its own finding with its own test.* That last clause is what preserves the founder's "two sides of the same coin, not the same quantity" — CC2's stale-flag hunk is not "complexity to discard," it is a second sufficiency claim that must earn its own gate pass.

So: not a status, not a score, not a schema term — **an admissibility-ordering rule in the acceptance policy** (`build_acceptance.py` / its doc), one sentence long. If CC2 or CC1 lands on "pure operating directive, nothing written," the disagreement is narrow: we differ only on whether the Q1 panel cost counts as wasted bench compute. I say it does — it already happened once.

---

**What I did:** re-executed all three T01 patches at parent `36ab4e3c` in throwaway copies (the session's repo copy was write-locked, so /tmp), reproduced the harness truncation with the harness's own regex, cross-ran each writer's test against the others' patches, ran the full suite two-sided, and replayed the composer's partial-application defect for Q2. **What comes next is yours to order:** land Fable's T01 hunk with rung 3's test, fix the `parse_test` fence anchor, add composer rollback, rebase T04 onto T02→T03→T05, and file the stale-`mechanical_fault` finding separately.

---


*2 of 2 reviewers returned a usable verdict.*

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).