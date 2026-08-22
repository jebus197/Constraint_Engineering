# The build experiment: nine of ten defects fixed by the panel, and five defects found in the instrument that judged them

**22 August 2026, 18:08–23:00 BST. Parent `36ab4e3`.**
**Reproduce: `python3 scripts/build_experiment_report.py` and `scripts/build_experiment_compose.py`.**

---

## What this was

The first experiment in this project's history designed to **fix** rather than to
find. Six models — CC2 and Fable through the Claude CLI, Codex, Gemini, ChatGPT
and DeepSeek through OpenRouter and DeepSeek's own API — were each given one
defect, the file it lives in, and a definition of done.

**Acceptance was mechanical and no model or assistant adjudicated it.** A patch was
accepted if and only if:

1. the model's new test **FAILS at the parent commit**,
2. the same test **PASSES with the patch applied**,
3. the **full suite stays green** relative to the parent's own failing set.

That two-sidedness is the answer to the founder's question of how a broken
instrument can repair itself. The falsifier gate accepts a falsifier merely for
**firing** — one-sided, which is why `reverify_falsifier("print('FALSIFIED')")`
returns CONFIRMED and why half this project's archived confirmations cannot be
demonstrated. A test that always fails cannot pass step 2; a test that always
passes cannot pass step 1.

**The tool loop fired for the first time in this project's history.** Four of the
six models had never been able to read a file: `openrouter_tools.py` offered sympy,
z3, pytest, ruff and mypy, and no way to open the source they were checking.

---

## The result

| task | outcome | by | rungs |
|---|---|---|---|
| T01 route discrimination failures up the ladder | **HIL** | — | 8 |
| T02 feed the discrimination control from the finding's own fix | **ACCEPTED** | CC2 | 2 |
| T03 wire the survived-falsification ledger | **ACCEPTED** | CC2 | 2 |
| T04 a crashed falsifier must not write a terminal status | **ACCEPTED** | Fable | 3 |
| T05 Bugzilla status vocabulary + machine-readable catalogue | **ACCEPTED** | CC2 | 2 |
| T06 shelve the load balancer, marked in the docs | **ACCEPTED** | CC2 | 2 |
| T07 `--dry-run` for the null-perturbation control | **ACCEPTED** | Codex | 3 |
| T08 memory-ledger recount into the save-state path | **ACCEPTED** | ChatGPT | 1 |
| T09 cite the frozen critical-severity pre-registration | **ACCEPTED** | CC2 | 2 |
| T10 explain the 67 unmatchable fixes and 30 errored falsifiers | **ACCEPTED** | Codex | 1 |
| T11 confirm or refute the instrument inventory | report recorded | Gemini | 1 |

**Nine of ten patch tasks accepted. One escalated to HIL.**

T07's acceptance came from manual re-evaluation after the step-3 repair rather than
from the live loop, so the loop-only figure is 8 of 9. Both are given because the
difference is real.

| accounting | rate | exact 95% CI |
|---|---|---|
| live loop only | 8/9 = 88.9% | [51.8%, 99.7%] |
| including T07 | 9/10 = 90.0% | [55.5%, 99.7%] |

### The pre-registered tell, honoured including where it does not favour the run

Fixed before the first dispatch: **near 100% means the checks are not binding and
the run should be distrusted; near 0% means the models cannot do the task.**

- *"The models cannot do the task"* is **decisively rejected**: p ≈ 1e-16.
- *"The checks are not binding"* is **NOT rejected** at conventional significance:
  p = 0.087 (loop only), p = 0.096 (including T07).

**So the acceptance rate ALONE does not rule out a near-vacuous gate.** 90% is
high. That must be said plainly rather than buried, because the pre-registration
exists precisely to stop a good-looking number being read as more than it is.

What does establish that the checks bite is independent of the rate:

1. **The gate was commissioned before use**, 10 tests, and refuses a vacuous test
   (`assert True`), an always-failing test (`assert False, 'FALSIFIED'` — the exact
   input the falsifier gate accepts as a confirmation), a non-matching patch, a
   patch with no test, prose with no patch, and a patch that breaks the suite.
2. **Eight in-run attempts were genuinely rejected** as
   `REJECTED_TEST_STILL_FAILS_WITH_PATCH`, and T01 was rejected at all three rungs
   by three independent writers.

The rate is consistent with a binding gate; the commissioning tests and the
rejections are what demonstrate it.

---

## The composition check, and what it caught

The gate validates each candidate **independently** against the same parent. That
is the right unit for judging one model's work and says nothing about the set.
*"Each part was verified therefore the whole is verified"* is a composition
fallacy, so the set was proved separately.

**Six of the eight composed patches apply cleanly together. Two conflict.**

- **T04 and T05 CONFLICT**: their SEARCH blocks no longer match
  `bench/reference_runner_v2.py` once T02 and T03 have landed. Four patches to the
  same 10,510-line file collide.
- The six that apply: **all accepted tests pass together (56 passed)**, and the full
  suite shows **3668 passed with zero failures the parent does not already have**.

**T04 and T05 are not wrong.** They need rebasing onto the composed tree, which is
ordinary integration work, not a defect in the models' output. Had the composition
step been skipped, this would have been discovered on the branch.

---

## Five defects in the instrument that judged the models. All CC1's

Each rendered a **harness** failure as a **model** failure. Recorded in the order
found.

**1. Step 3 assumed a green suite instead of measuring it.** Fixed `ec95acb`.
`test_falsifier_cannot_read_the_key.py` passes in the repo and FAILS in a bare
worktree at the same commit — it scans "the whole tracked archive" and `bench/logs`
is gitignored. Every task would have been falsely rejected, the run would have
reported near-0% acceptance, and near-0% is this harness's OWN pre-registered tell
for *"the models cannot do the task"*. **The first model output this harness ever
judged was judged wrongly, in the confident direction; Codex's work was valid.**

**2. `git add -A` committed a model's direct writes. Twice.** Fixed `386c8d4`.
A model working T01 edited the working tree instead of returning a patch, and a
blanket stage swept 157 lines of ungated code into a commit whose message did not
mention it. It happened **again** while the first instance was being written up.
It poisoned the parent, so a later `REJECTED_PATCH_DID_NOT_APPLY` was an artefact
of the contamination rather than a failure by Codex.

*Root cause, and it is a hole in an existing ruling.* On 2026-07-29 this project
ruled *"Remove Write/Edit from panel dispatch — makes 'frozen target' true."* That
ruling was verified DONE earlier the same day by checking `--allowedTools` for
Write and Edit. It grants `Bash, Read, Grep, Glob, WebFetch, WebSearch`, and **Bash
is a superset of Write**. The inline comment beside that list reads *"No file
modification"*, which is false. **The "frozen target" guarantee has been untrue in
every Claude-CLI panel dispatch this project has ever run.**

*The fix already existed and had never been called.* `set_panel_cwd()` sits in
`experiment_11_orchestrator.py` for exactly this, its docstring reading *"failing
open here would put the panel back in the repo, which is the exposure this exists
to close."* Claude-CLI dispatches now run inside a throwaway worktree. **Verified by
test:** a simulated model write lands in the sandbox `True`, reaches the repo
`False`.

**3. `read_file`'s line-number prefix made a verbatim SEARCH block impossible.**
Fixed `36ab4e3`. It returned `f"{i:>6}  {line}"`. Codex stripped the digits, kept
the two-space separator, and every line it returned carried +2 indentation.
Measured: its block matches the file **exactly** after removing two leading spaces.
**Its Python was correct.** The reader was fixed rather than the matcher — a fuzzy
SEARCH would let a patch land where it was never meant to, which is far worse than
a rejection. Pinned by 6 tests.

**4. A collection error was labelled as a failed fix.** Not yet fixed; logged
during the run and deliberately not paused for, because step 2 rejects it either
way so it cannot produce a false ACCEPT. *"The defect persists"* and *"the model's
test does not import"* must not render alike.

**5. `results.json` is clobbered by every resume.** Worked around: the report and
the composition check both rebuild from the append-only cy log, which is why a run
log is append-only.

**5 of 25 attempts were decided by one of these defects rather than by the model's
work.** Any per-model ranking from this run would be an artefact of that, **and
none is offered here.**

---

## Round-robin, and the founder's objection demonstrated

The founder challenged round-robin at rung 1 as an early-project methodology and
asked why it was thought necessary. **It was not, and the run produced a concrete
demonstration.**

T09 asks a model to edit a specific document. Round-robin handed it to **DeepSeek —
the one route with no tool loop** — which therefore cannot read the file it is
asked to edit. It guessed and the SEARCH block did not match. That is a
**configuration mismatch, not a model failure.**

`bench/routing.py` already implements capability-aware routing, is deliberately
runner-agnostic and side-effect-free so a caller can inject into it, carries an
empirical ordering from the 7 hardest Exp-42 residuals, and states in its own
docstring that it exists to replace *"the flat parallel dispatch [that] had
collapsed into identical treatment"*. **CC1 hand-rolled a flat ladder instead —
reimplementing an existing mechanism as the very thing that mechanism was written
to replace.**

---

## T11: the inventory confirm-or-refute is 3 of 34 done

Gemini verified **I01, I03 and I05** by running them against known-good and
known-bad inputs, and said plainly that it could not reach the other 22 within its
tool budget. That honesty is the right behaviour and is recorded as such.

**I01 reproduced independently:** `_estimate_gamma([1,2,3],3) = 0.0` and
`_estimate_gamma([3,2,1],3) = 0.35765`. Gemini reported 0.357, which is a
truncation of the fifth decimal, not an error. The two inputs give different
answers, which is what commissioning requires. **I03 and I05 take a `cfg` object
and their one-line calls could not be replayed verbatim, so their values are
recorded as UNVERIFIED rather than accepted on the model's word.**

**A defect in CC1's harness, found here:** the `report_only` path bypasses the gate
entirely, so T11's submission was RECORDED without scrutiny — and the "test" it
carried merely asserts that three keys exist in a dict it also added them to, which
is precisely the tautological test the gate refuses everywhere else.

---

## The quarantined T01 work could not be fairly judged, and that is CC1's fault too

The two direct writes were quarantined rather than deleted, because the WORK may be
sound even though the ROUTE was wrong — deleting it would punish a model for a hole
CC1 left open. Converted to candidate form and put through the gate, it returned
`REJECTED_PATCH_DID_NOT_APPLY`.

**That is a verdict on CC1's diff-to-SEARCH/REPLACE converter, not on the model.**
The diff applied to the tree as it stood when written; converting it against a
different parent does not match. Its test also errors during collection. **The
underlying work remains unadjudicated.**

---

## What actually got fixed

**T02 is the one that matters.** The discrimination control has existed in the
runner with eight outcomes and three self-probes and **had never fired once** in
this project's life, because it waits on a corrected copy nothing supplied. It is
now fed from each finding's own proposed fix. The instrument that separates a
demonstrated confirmation from an asserted one is, for the first time, wired to
something.

**T03** wires the survived-falsification ledger, which records that a claim was
tested and STOOD — closing the gap where a clean zero-plant control produces an
absence indistinguishable from a dispatch failure.

**T04** stops a crashed falsifier writing a terminal verdict. **T05** gives the
Bugzilla design its status vocabulary and a machine-readable catalogue, which had
zero lines of implementation before tonight. **T06** shelves the load balancer
under the founder's ruling. **T07–T10** close the smaller items.

---

## Standing, and what needs the founder

- **Nine of ten defects fixed**, mechanically verified, none of it on the founder's
  word or CC1's.
- **Six compose cleanly. T04 and T05 need rebasing.**
- **Nothing is merged.** Accepted patches remain candidates; `fixes-HIL-only`
  stands and the founder decides what ships.
- **T01 needs a ruling.** Three independent writers failed the same way, which
  points at the task rather than the writers: either it is genuinely hard, or CC1's
  brief is under-specified.
- **The "frozen target" hole is closed for this harness only.** Every other panel
  dispatch in this project still runs with Bash in the repository.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
