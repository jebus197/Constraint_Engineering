# Final Report — 2026-09-05

**13:56 BST (Saturday).** Supersedes every earlier report of today. The 7 documents supplied at lunchtime replaced a reconstruction I had built badly; the picture is much simpler than it looked this morning. Spoken companion: `~/Desktop/CDSFL_tts/Final_Report_2026-09-05.txt`.

---

## Part 1 — the correction that matters most

**The decision surface is 12, not 122.**

`DECISIONS_AWAITING_YOU_2026-09-03` already did this consolidation and says so in its own first line: it replaced 12 notes totalling ~18,000 words with **12 numbered decisions**. **9 were then ruled on** in the annotated copy.

My 122 came from extracting every question-shaped sentence across 3 days — duplicates, ask-backs, and already-answered items included. It was a worse version of a job already done well.

| State | Decisions |
|---|---|
| **Ruled and now built/tested** | D4 measured-rate rule · D5 containment instrument · D6 write access + disclosure · D7 occasions recording · D8 execution matcher · D9 comparison experiment · D10 seeded catalogue |
| **Still needing you** | **D3** Reduction Criterion placement · **D11** seat contrast · **D12** configuration settings |

---

## Part 2 — the 2 questions I owed you

### "How can HIL review have never worked when we spent months on the HIL queue?"

**Both are true. Your memory is right; my framing was wrong.** Two mechanisms share a name.

| | What it is | State |
|---|---|---|
| `hil_review` | A **run-pause switch** — stops after each round for review | Never set in a config. **Not unreachable**: `--hil-review` is a CLI flag, and the runner prints *"Resume with `--resume --hil-review`"* |
| `hil_escalated` / queue | Findings **routed to a person** when no tool can settle them | **Always worked.** 90 escalated + 41 irreducible across 6,929 findings = **1.30%**, Wilson [1.06%, 1.59%] |

Your remark that *"a minor issue like reviewing a paused run"* was being oversold was exactly right.

### D11 — "I don't know what I might be approving"

Measured today, not recalled:

- Seats **`Codex`** and **`ChatGPT`** differ in **1 of 12** configuration fields — **the label**.
- Same `openai/gpt-5.5`, same OpenRouter route, same system prompt, same `max_tokens`, `timeout`, `max_retries`, same `codex_exec` secondary.
- **The 5-seat panel has 4 distinct configurations.**

The contrast *was* tool access (`codex_exec`, a shell-bearing route). It was removed **deliberately** in Run 6 — the CLI route collapsed into a decomposed fallback costing **45–80 minutes per round** with brittle auth. Restoring it re-incurs that.

**Still relevant?** More than in April: every "5 models agreed" since is *4 configurations, one counted twice*, and **D9 cannot cleanly test whether vendor diversity matters while 2 of its seats are the same thing**.

**The choice:** restore tool access to one seat and accept the slower route, **or** state in the record that the panel has 4 architectures. What should not continue is calling it 5.

---

## Part 3 — completed while you were out

| Item | Result |
|---|---|
| **Anti-cooking condition (b)**, open **111 days** | Threshold **IS reachable**: 10 of 13 live runs = 76.9%, Wilson [49.7%, 91.8%]; 10 of 11 excluding round-1 halts. Artefact in `bench/exp40_baseline/`, states its own limit (reachability ≠ calibration) |
| **Phantom decision**, open **110 days** | `RECOVERY.md` told you a ruling awaited; discharged 2026-05-18. Dated correction block added, original retained |
| **D5 — "the other instruments"** | 4 of 6 alarms were **the audit's own defect**: it scanned top-level report keys only, while the runner nests instrument blocks. Those keys are in **37 of 60** reports. AMBIGUOUS 5→2, UNREACHABLE 1→0 |
| **Housekeeping** | Review worktree removed (it *did* exist), plus 5 stale worktrees (~39,000 files), each verified to hold 0 uncommitted work |

**3 of my own errors surfaced while doing the work above**, each caught by running something rather than reading it:

1. The reachability measurement first **pooled simulated with live** runs and reported a better number.
2. Its early-halt exclusion was **silently vacuous** — it read field names I'd guessed rather than the archive's.
3. After fixing the audit I updated the 2 tests pinning the wrong answer, and **reverting the fix left every test green**. Removing a test that pins a wrong answer is half a repair; the other half is a test that fails when the wrong answer returns. Added, verified to fail on revert.

**One thing deliberately not tidied.** `latent_control_audit.py:135` names both the old and new runner paths to `git log`. Looks like clutter; isn't. Setting histories cross the rename — dropping the old name reports `gamma_alt_threshold` as first appearing **137 days late**.

**One thing preserved rather than deleted.** The removed worktree held the *rejected* alternative fix for the integrity guard — now saved as a diff under `experimental_notes/rejected_alternatives/`. An implementation considered and not taken is evidence about a decision.

---

## Part 4 — what remains

1. **Three decisions need you:** D3 placement, D11 seat contrast, D12 settings.
2. **7 figures still have no reproducing script** — your own standing rule; backlog predates last night. Safe unsupervised work, **not started** because a withdrawal changes the record and you should see the list first.
3. **Nothing has run since 2026-08-23.** The blocker is one scientific ruling on the held-out experiments, open since 2026-08-08.
4. Everything else ruled is **built and tested, none launched** — launching costs money.

Written under CDSFL note standard v1.7 (26 August 2026).
