# The Two Wolfram Routes, And What Was Actually Built

2026-09-28, 11:05 BST

## The short answer

The plan to combine the two Wolfram routes was judged good in **direction**, and something **was** built and tested. The qualification is that what was built is the safety layer underneath the combination, not the combination itself.

[Wolfram_Setup_Instructions_2026-09-17.md:41](experimental_notes/Wolfram_Setup_Instructions_2026-09-17.md:41) records the judgement verbatim: *"**J1. English in, exact Wolfram Language out, run locally with no hosted time limit. PLAUSIBLE, and the most valuable.** … The connector side is confirmed; the full round trip is UNVERIFIED until step A4."* A4 had not run. It has now, and it passes.

## What the advice got right

The division of labour, which was adopted as §7's routing rule: the hosted connector accepts English and emits exact Wolfram Language; the local Engine runs it with no hosted ceiling and can hold definitions. Each covers the other's weakness.

## What the advice got wrong

| Advice | Status | Evidence |
|---|---|---|
| `claude --instructions FILE` | **Does not exist** | `claude --help \| grep -c -- "--instructions"` returns **0**. Real flags: `--append-system-prompt`, `--settings`, `--system-prompt` |
| Create `.claudecode_profile.md`, auto-crawled | **Read by nothing** | No such path exists; instructions live in `.claude/CLAUDE.md` (50,092 bytes). An unreached addition, which the additive standard forbids |
| `InstallMCPServer["ClaudeDesktop"]` | **Actively harmful** | This is what caused the 2026-08-02 two-kernel clash; the free Engine is effectively single-kernel and the resulting message reads as an activation fault but is not one |
| `@garoth/wolframalpha-llm-mcp` via npm | **Rejected** | Third-party code plus a new credential, adding nothing the official connector lacks (C3) |
| *"fully compliant under the terms of your subscription"* | **UNVERIFIED and in conflict** | A Claude subscription grants no Wolfram rights; Wolfram's terms say the Services *"should not be used in conjunction with your AI-powered tools or services"* absent a separate agreement (C5) |
| *"unlimited, immediate access"* | **Measurably false** | Stateless: `g[x_]:=x^3+1` gave `g[3]=28`, and a separate call returned `g[3]` unevaluated with `ValueQ` False. Ceiling: `Pause[20]` returns at **20.0003 s**; `Pause[35]` failed on **both** attempts |

The 26 s ceiling in `.claude/CLAUDE.md` was measured on the retired `agenttools` endpoint. Today's bracket of **(20, 35] s** contains it but does not confirm it, and it still has no committed producer for this route.

## What was actually built, and tested

A **queue** and a **barrier**, both protecting the local Engine rather than joining the routes.

- **Queue** — `bench/wolfram_standard.py` plus the shims at `bench/tools/wolfram_gate/serial/`, taking a machine-wide `flock` so 1 call runs at a time. Justified by measurement: 3 concurrent `wolframscript` calls on 2026-08-02 gave 1 result and 2 `Connection closed by WolframKernel`. `scripts/wolfram_serial_gate_probe_2026-09-17.py` started 2 calls simultaneously and recorded the second waiting **5.1 s**, kernel windows disjoint, both answers correct. That script records 2 earlier versions of itself that measured process lifetimes instead of kernel windows and reported a false pass; it now exits 3 rather than passing vacuously.
- **Barrier** — dispatched seats and stored falsifiers are denied Wolfram entirely, on the founder's condition that reproducing this project must not require installing Wolfram. `bench/falsifier_verify.py:910` pins the sandbox to `deny` explicitly so a policy change elsewhere cannot open it. Held by 15 tests plus a fake-kernel test where "not reached" is a missing marker file.

## What was deliberately not built

**No automatic handoff exists, and none was intended.** [Wolfram_Setup_Instructions_2026-09-17.md:111](experimental_notes/Wolfram_Setup_Instructions_2026-09-17.md:111): *"The connector is for the assistant's interactive calls only, never for scripts, bench runners or panel seats."*

An audit confirms the code matches: `bench/wolfram_standard.py` contains **0** occurrences of `agenttools`, `WolframCloud`, `mcp__`, `urllib`, `socket` or `requests`; the connector exists there only as a classification label, whose sole caller passing `route="connector"` is one test; and every gated seat launches with `--strict-mcp-config` and no `--mcp-config`.

> **CORRECTION, 2026-09-28, found by the fable seat.** This sentence originally ended *"...and no `--mcp-config`, which appears nowhere in the repository."* **That was false.** `--mcp-config` appears at `bench/wolfram_standard.py:194`, in a comment explaining that `--strict-mcp-config` with no `--mcp-config` removes the hosted connector. The claim needed no archive to falsify — an ordinary search of tracked source finds it. It is the exact "appears nowhere" shape this same note diagnoses 2 sections below, committed in the note that diagnoses it. The surviving claim is narrower and still sufficient: **no seat launch site PASSES `--mcp-config`**, so no seat receives an MCP server. A measured probe read the CLI's own start-up report and found 0 Wolfram MCP servers for seats.

## What was left undone until today

Both characterisation steps sat unrun for 11 days.

**A4 — the round trip. PASSES.** The connector parsed *"integrate x^2 log x from 0 to 1"* into `Hold[Integrate[x^2*Log[x], {x, 0, 1}]]`, declaring the `Log`/`Log10` ambiguity it resolved. The local Engine released it to `-1/9` (`N` → `-0.11111111111111111111` at 20 digits). SymPy independently gave `-1/9` exact; mpmath quadrature agreed at `0.0`. All 3 agree, which was the pass condition. *(Values computed with Wolfram Language, both routes.)*

**A3 — partly.** Version `15.0.1 for Linux x86 (64-bit)`, `$ReleaseNumber` 1 — a hosted machine, not the founder's. Statelessness and ceiling as above. **Owed:** the evidence file under `experimental_notes/evidence/` and a committed producer for the ceiling figure, which `measured-rate-travels-with-its-script` requires before it is citable as settled.

## A separate discovery, wider than Wolfram

**The session's `grep` is a shell function** installed by Claude Code's own snapshot, wrapping ugrep with `--ignore-files`. It honours `.gitignore`, and `.gitignore:48` ignores `bench/logs/**` — 353 MB across 5,840 files. It skips them **silently**.

Measured over 8 patterns by `scripts/shell_grep_blind_spot_2026-09-28.py`: **3743 of 5245 matching files are never shown = 71.3632%**, Wilson 95% [70.1245%, 72.5706%], Clopper-Pearson [70.1186%, 72.5840%], mpmath agreeing to 4.33e-17 and Wolfram Language returning [70.12449821701338, 72.57063779693486]. Starkest case: `falsifier`, **1023 visible against 4310 present**.

This is load-bearing because the project's evidence lives in that archive, and a search that cannot see it reports **0 occurrences** for a term occurring thousands of times — the exact shape this project treats as a finding. Remedy: `/usr/bin/grep` for any search whose answer might be zero.

**An earlier attempt at this measurement was vacuous and is recorded as such.** It ran the comparison through `zsh -ic`, a fresh shell that never sources the snapshot, so it compared `/usr/bin/grep` against itself and returned a reassuring 0 of 541. A measurement whose control and treatment are the same thing measures nothing.

## A correction that overturns an 18-day-old conclusion

The founder supplied the official connector listing during this session. It shows: **made by Wolfram Research**, verified, published in **Anthropic's own Claude Marketplace**, **Sign-in: Not required**, added May 2026, connector URL on the **`agenttools.wolfram...`** host.

That is the same host `.claude/CLAUDE.md` declared **dead** on 2026-09-10.

**What actually failed was the transport.** The removed config entry was `npx -y mcp-remote https://agenttools.wolfram.com/mcp`, and `scripts/wolfram_route_health_2026-09-10.py:44-45` keys its patterns on the literal string `WolframCloud` — the *name of that stdio-shim entry*:

```
SUCCESS = "announcing WolframCloud: (\d+) tool"
FAILURE = "Failed to connect to WolframCloud"
```

It measured the desktop app's ability to attach to the shim. It never tested whether the host answered.

**The figure is sound; the inference was not.** Reproduced on 3 tools: 42/43 failed from 2026-09-04 = **97.6744%**, Wilson [87.9410%, 99.5883%], against 1/21 = 4.7619% before; Fisher exact **p = 2.199086e-14**, odds ratio 840; chi-square with Yates **p = 8.709349e-13**; mpmath exact hypergeometric agreeing with scipy to **7.28e-30**.

**The task list was more careful than CC1 was.** `CDSFL_MASTER_TASK_LIST.md:659` explicitly kept three explanations open — *"whether the failure is the licence lapsing, the service being withdrawn, or a transport fault"*. `.claude/CLAUDE.md` hardened it to "DEAD", and CC1 repeated that as fact on 2026-09-27. Today's evidence resolves it in favour of the transport.

**Consequence:** the natural-language capability recorded as a NAMED LOSS was never lost. It was reachable throughout via the official connector.

## A second defect in the public explorer

`explorer/index.html:177` computes `nuStar = sigma*R*q/(1 - q*R*(1-sigma))` — the re-injection rate at which it warns a further pass does net harm. Solving the appendix's general expected improvement (`:225`) for zero gives `R*q*sigma/(R*q*sigma - R + 1)`.

The denominators differ (`- R*q` against `- R`), and the difference factors to `R²*q*sigma*(q-1)/(...)`, whose numerator is negative for q < 1.

| R | q | σ | explorer nuStar | true break-even | ratio |
|---|---|---|---|---|---|
| 0.99 | 0.30 | 1.00 | 0.297000 | 0.9674267 | 0.307 |
| 0.90 | 0.50 | 0.90 | 0.4240838 | 0.8019802 | 0.5288 |
| 0.50 | 0.20 | 0.50 | 0.05263158 | 0.09090909 | 0.5789 |

**Strictly one-directional, proven over the open domain.** z3 returns `unsat` for both "explorer nuStar > true break-even" and "they are equal"; Wolfram Language independently returns `Resolve[ForAll[...]] → True`. *(Computed with Wolfram Language.)*

**This is the second finding of the same shape in the same public page.** Both make the tool stop, or warn of harm, earlier than the model supports. Neither applied — the page is public and fixes go to the HIL.

- Producer: `scripts/explorer_stopping_rule_is_superseded_2026-09-28.py` (section 5)
- Guard: `bench/tests/test_explorer_stopping_quantity_2026-09-28.py`, 10 tests; mutating the explorer formula to the correct one turns 3 red

## The panel checked this work, and found 4 faults in it

2 free seats, 169 and 79 tool calls, ~1 hour each. Brief: check CC1's work only, and assume a 4th defect exists because 3 were already caught that morning.

| # | Item | Verdict |
|---|---|---|
| 1 | Explorer stopping rule | **SEATS DISAGREE** — preserved, not voted on |
| 2 | Harvest provenance fix | **SOUND** — all 4 call sites checked, 30 tests pass, no live 4th shape |
| 3 | Paid-dispatch ledger | **DEFECTIVE** — the 4th defect |
| 4 | Classifier changes | **CONFIRMED EVASION** |
| 5 | Naming check | **FALSE-ZERO CLASS** |
| 6 | Grep blind spot | **CONFIRMED**, reproduced to every quoted digit |
| 7 | Wolfram re-scoping | **CONFIRMED**, 1 residual overreach |

**Item 3 — the guard does not work.** `PAID_LEDGER` pointed at `bench/paid_dispatch_authorisations.json`, **which does not exist**. The committed ledger is `bench/directives/universal/paid_dispatch_authorisations.json`, a **dict** with `authorisations[].rounds[]` / `founder_verbatim[]`; CC1's parser demands a flat list, so even repointed it would refuse every real authorisation. **11 tests passed because every one monkeypatched a synthetic flat-schema file — the green never touched the real record.** Verified here: the path is absent, the real file is a dict.

**Item 4 — executed, not argued.** `classify_write("/tmp/../repo/hooks/evil.py")` → **`transient`**. So does `/tmp/${V:-../../repo}/hooks/evil.py`. "Transience is decided by where a path starts" is unsound under `..`.

**Item 5 — the false-zero class, built into the tool meant to catch blind spots.** `repo_hits` shells `git grep`; a panel sandbox has `.git` severed → rc 128 → `-1`; `check()` filters `if hits != 0: continue`, so **every phrase is silently dropped** and `--measure` printed `0.0000%` with no warning. 2 of CC1's own committed tests were red there for the same reason.

**Item 6 — 3 past claims now unsafe**, each a universal asserted with a search that could not see `bench/logs/**`:
- `Dedup_Historical_Brief_Addendum_2026-08-18.md:474` — "GAMMA_SRC appears nowhere outside its own module and test"
- `Design_Reviews_Bugzilla_And_Perturbation_2026-08-21.md:28` — "cc2_verification_step appears nowhere in the repo except inside its own docstring"
- **this note** — the `--mcp-config` claim, corrected above

Each *conclusion* survives; the universal quantifier does not. fable also named a claim it checked that turned out **SAFE**, which is the anti-vacuity half.

**Item 7 — confirmed, 1 overreach.** "Reachable **throughout**" rests on point samples (1 post-cut attach, `Out[1]= 4` on 2026-09-17, A4 on 2026-09-28). Established is *"answered on every date probed"*, not continuity.

**Item 1 — the disagreement, preserved as information per `feedback_no_model_voting`.** cc2: the page is faithful to `reference_runner_v3.py:11948-11960`'s canonical `compute_rk`, so gating on `:225` would make the ΔR bars stop equalling the drop in the trajectory above them. fable: `:217` retires ΔR *for decisions*, the page carries decision semantics in 3 places, and keeping `dR` for display while gating on `E[ΔR]` resolves it — fix written and tested. **Both agree CC1's `nuStar` claim was misattributed.** fable's theorem verified here: `E − dR = −R²qσ(ν−1)(q−1)/(Rq−1)`, SymPy identical, Wolfram returns 0.

**Escalation a seat correctly refused.** Round `arm4_prose_anatomy_2026-09-22` holds paid replies (`cx`, `ge`) with **no ledger entry**. Recording an authorisation after the fact needs the founder's verbatim words; *"a seat must not forge them."*

## What needs a decision

1. **Does the marketplace listing close the connector half of W1?** Wolfram Research authoring and publishing this connector in Anthropic's marketplace, with no sign-in required, is stronger evidence of permission than a reply email. It does **not** touch whether the free Engine licence permits the local AgentTools server, which stays open regardless. The founder's call.
2. **`.claude/CLAUDE.md` calls the local Engine *"the only WORKING Wolfram route today"***, which this morning's calls contradict. `bench/tests/test_wolfram_route_retired_2026-09-10.py` asserts that sentence, so both change in one commit. The file is the founder's.
3. **`docs/REPRODUCING.md` and `resources/RECOVERY.md`** still present the retired `mcp-remote` bridge as usable. The host is fine; the bridge is not the route.
4. **Whether to apply either or both public explorer fixes.** Both one-directional, both making the published tool more pessimistic than the model. Untouched.

Written under CDSFL note standard v1.7 (26 August 2026).
