# Wolfram setup: the hosted connector and the local Engine, and who does what

2026-09-17, 17:10 BST, Europe/London. Task W1. Instructions requested by the founder: "print a set of instructions for me to follow to set this up fully for you. If there are steps you can perform on your own, you should tell me".

## Summary

Both Wolfram routes work today, and the founder has 3 things to do, 1 of them dated. The hosted Wolfram connector, added through claude.com/connectors/wolfram, is connected and returned `Out[1]= 4` for `2+2`. The local Wolfram Engine computes, and its licence runs to 2026-10-08, which it did not renew on its own last time. W1 itself stays BLOCKED on a question only Wolfram can answer: whether its terms permit this use. Most of the setup advice in the Google Search AI chat the founder shared should not be followed, and 1 of its steps, `InstallMCPServer["ClaudeDesktop"]`, would bring back the 2-kernel clash recorded on 2026-08-02.

Since this was drafted, action list item 4 of `experimental_notes/Action_List_2026-09-17.md` has wired the Wolfram standard into code: automated runs are now denied Wolfram, and the section "What automated runs can reach" below records what was measured.

## 1. What was checked on 2026-09-17, and what came back

Every row is a command that was run between 15:45 and 15:53 BST, 1 Wolfram call at a time, with nothing in the repository or any config changed.

| Check | Command | Result |
|---|---|---|
| WolframScript present | `wolframscript -version` | `WolframScript 1.14.0 for Mac OS X ARM (64-bit)` |
| No stale kernels before any call | `ps -axo pid,ppid,lstart,command \| grep -i -E "wolfram\|WolframKernel" \| grep -v grep` | no output |
| Licence date | `wolframscript -code '$LicenseExpirationDate'` | `DateObject[{2026, 10, 8}, Day]`, read again at 16:40 BST with the same result |
| Engine version | `wolframscript -code '$Version'` | `15.0.0 for Mac OS X ARM (64-bit) (May 26, 2026)` |
| Licence file | `stat -f '%Sm %N' ~/Library/WolframEngine/Licensing/mathpass` | modified 2026-09-15 01:42:30, the hand activation |
| Kernel path | `WolframScript.conf` under `~/Library/Application Support/Wolfram/WolframScript/` | `WOLFRAMSCRIPT_KERNELPATH=/Applications/Wolfram Engine.app/Contents/MacOS/WolframKernel` |
| Desktop app config | `~/Library/Application Support/Claude/claude_desktop_config.json`, parsed, no values printed | `mcpServers` has 0 entries and 0 Wolfram mentions |
| Connector status | `session_connectors_status` | Wolfram, kind connector, id `0c7b955d-e15f-4ff9-940a-1db64f672b99`, connected, 3 tools |
| Connector tools | tool search for "wolfram" | `WolframAlpha`, `WolframContext`, `WolframLanguageEvaluator` |
| Connector works | 1 call to `WolframLanguageEvaluator` with `2+2` | `Out[1]= 4`, which has an `Out[` line and so counts as a result |
| Connector's own description | its tool schema | "This is a stateless kernel"; `timeConstraint` default 60 seconds; accepts English inside code as `\[FreeformPrompt]["query"]` |
| Permission rule | `.claude/settings.json` | allows `mcp__Wolfram__*`, which does NOT match the connector's tool names, `mcp__0c7b955d-e15f-4ff9-940a-1db64f672b99__*` |
| Local Wolfram MCP paclet | `~/Library/WolframEngine/Paclets/Repository/Wolfram__AgentTools-2.1.37/PacletInfo.wl` | installed; declares `"WolframVersion" -> "14.3+"` |
| Record of the 2026-08-02 clash | `.../AgentTools/Servers/Wolfram/Log.wl`, last written 2026-08-02 22:07 | 2 clients starting at the same moment with interleaved lines, matching the clash recorded in `.claude/CLAUDE.md` |
| `--instructions` flag the chat recommends | `claude --help \| grep -c -- "--instructions"` | `0`; Claude Code 2.1.220 has no such flag |

## 2. What automated runs can reach, measured after item 4

- **A `claude -p` seat.** `scripts/wolfram_seat_deny_probe_2026-09-17.py --live`, 2 free Max-plan calls with a FAKE `wolframscript` first on PATH. Without the deny layer the seat ran the fake. With it, the CLI answered "Permission to use Bash with command wolframscript -code 1+1 has been denied." In both sessions the CLI's own start-up report listed 0 tools and 0 MCP servers whose names contain "wolfram", so seats do not receive the connector.
- **The falsifier sandbox and the test suite.** `bench/tests/test_wolfram_out_of_pipeline_2026-09-17.py` runs a fake kernel that writes a marker file; the sandbox refuses it by name, by absolute path, through `bash -c` and through `os.system`, and the suite's network guard refuses it by name and by absolute path.
- **The limit.** A seat's own Bash tool can still reach the real binary by typing its absolute path; the CLI rule matches a command prefix and the PATH gate a bare name. The deny layer makes Wolfram use deliberate rather than accidental, and `bench/wolfram_standard.py` says so.

## 3. The joint capabilities, judged

- **J1. English in, exact Wolfram Language out, run locally with no hosted time limit. PLAUSIBLE, and the most valuable.** The connector parses English; the local Engine runs the exact code it produced with no hosted ceiling. This restores the natural-language ability `.claude/CLAUDE.md` records as a NAMED LOSS. The connector side is confirmed; the full round trip is UNVERIFIED until step A4.
- **J2. Documentation lookup through `WolframContext`. SUPPORTED by reading the code; usefulness UNVERIFIED.** The local AgentTools version needs a paid LLMKit subscription for its Wolfram|Alpha part (`Kernel/Tools/Context.wl`: `"LLMKit" -> "Required"`).
- **J3. Each route covering the other's outages. PLAUSIBLE only.** The hosted route failed 42 of 43 attempts from 2026-09-04 (`scripts/wolfram_route_health_2026-09-10.py`), and the local Engine was down from 2026-09-14 19:31 to 2026-09-15 01:42 BST (task 0.1), so for at least 6 hours 11 minutes no route worked. Whether the connector shares the failed backend is UNVERIFIED.
- **J4. The 2 Wolfram kernels checking each other. REJECTED as mathematical verification.** Both run Wolfram Language, so a shared bug agrees with itself. SymPy, mpmath and z3 remain the independent check.
- **J5. Short stateless checks on the connector, long or stateful work on the Engine. PLAUSIBLE.** The connector's own ceiling has not been measured; the 26 s figure in `.claude/CLAUDE.md` was measured on the retired endpoint and has no committed producer.

## 4. The Google Search AI chat's advice, checked

- **C1. `InstallMCPServer["ClaudeDesktop"]` or the "Wolfram Local MCP extension". REJECTED.** This is how the 2-kernel clash of 2026-08-02 happened. Do not run it, and do not run `UninstallMCPServer`, which would edit the desktop app config.
- **C2. "Needs Wolfram|One or Mathematica 15+". CONTRADICTED on capability; the licence is UNVERIFIED.** The paclet declares 14.3+ and answered on the free Engine on 2026-08-02.
- **C3 and C4. `@garoth/wolframalpha-llm-mcp` from npm with an App ID, and `pip install mathematica-mcp-full`. REJECTED.** Third-party code, a new credential in C3's case, and nothing either adds that the connector lacks.
- **C5. "Fully compliant under the terms of your subscription". UNVERIFIED, and in conflict with the recorded reading.** An Anthropic subscription grants no Wolfram rights; Wolfram's Terms of Use say the Services "should not be used in conjunction with your AI-powered tools or services" without a separate agreement.
- **C6. "Unlimited, immediate access". CONTRADICTED on state, UNVERIFIED on limits.** The connector describes itself as stateless.
- **C7. `claude --instructions DEVELOPER_INSTRUCTIONS.md`. CONTRADICTED.** No such flag exists.
- **C8. `.claudecode/config.json` and profile instruction files. Not needed.** The Wolfram rules live in `.claude/CLAUDE.md`; a second file would compete with it.
- **C9. "Pass error traces to the cloud connector to diagnose them". REJECTED.** A Wolfram kernel does not diagnose Python stack traces.
- **C10. "Automatically pipe Wolfram|Alpha data into files and databases". REJECTED.** The recorded terms bar systematic extraction into a data table.

## 5. Steps for the founder

**F1. SUPERSEDED 2026-09-17 21:34 BST: the renewal is automated and needs nothing from the founder.** Measured that evening with `mathpass` backed up first, `wolframscript -activate` run with stdin closed returned exit 0 and "Wolfram Engine activated", prompting for nothing: it authenticates through the cloud credential already stored under `~/Library/WolframEngine/ApplicationData/CloudObject/Authentication`. The claim that it needs a Wolfram ID and password was wrong, and `scripts/cdsfl_onboard.py` is corrected. `scripts/wolfram_licence_renew_2026-09-17.py` now runs under the LaunchAgent `com.cdsfl.wolfram-licence-renew` at login, at 09:05 and at 21:05, skipping while another kernel is running and logging to `~/Library/Logs/cdsfl_wolfram_renew.log`. Re-activating early does not move the date, so the agent keeps trying and the renewal lands at or after expiry. **The steps below are kept as the manual fallback, for a machine where the agent is not installed.**

1. On 2026-10-07, open Terminal.
2. Run `wolframscript -code '$LicenseExpirationDate'`.
3. If it still shows `DateObject[{2026, 10, 8}, Day]`, run `wolframscript -activate`.
4. Sign in with the Wolfram ID and password when asked, and accept the terms if shown.
5. If activation refuses because the licence has not yet expired, repeat steps 2 to 4 on the morning of 2026-10-09. Whether early renewal is possible is UNVERIFIED; last time it was done after expiry.
6. **Done when** `wolframscript -code '$LicenseExpirationDate'` shows a date after 2026-10-08 and `wolframscript -code '1+1'` prints `2`.
7. If a "not activated or experiencing a license-related problem" message appears, have the assistant run step A1 first: a leftover kernel produces the same message. `python3 scripts/cdsfl_onboard.py` now makes that check itself, reads the expiry date, and warns from 14 days before it.

**F2. Choose how to stop connector permission prompts.** The rule `mcp__Wolfram__*` does not match the connector's tool names, so main sessions may ask before every Wolfram call; whether they do is UNVERIFIED.

- Option (a): when Claude Code asks to allow `WolframLanguageEvaluator`, `WolframAlpha` or `WolframContext`, choose the option that always allows it.
- Option (b): reply `y`, and the assistant adds `"mcp__0c7b955d-e15f-4ff9-940a-1db64f672b99__*"` to `permissions.allow` in `.claude/settings.json`, keeping the old line.
- **Done when** the next Wolfram call returns an `Out[` line with no prompt. If the connector is ever removed and re-added, its id may change (UNVERIFIED) and the rule would need updating.

**F3. The licence question, which is what still blocks W1. Needs the founder's email.**

1. Check whether Wolfram has replied to the earlier email about the MCP server licence. If it has, save the reply into `~/Developer_Projects/Responses/` and name the file to the assistant, which records it.
2. Optionally send the follow-up below, edited freely. Only the founder can send it.

> Subject: Follow-up: using the Wolfram connector in Claude for research cross-checks
>
> Hello. Following my earlier email about the MCP server licence: I have now connected the Wolfram connector listed at claude.com/connectors/wolfram to my Claude account. I use it interactively, as 1 researcher, to cross-check mathematics, for example definite integrals and symbolic simplifications, while writing research that will be published, with Wolfram credited on every result used. No automated pipeline calls it, and results are not collected in bulk. Please could you confirm in writing:
> 1. whether this use is permitted under your current terms, given the Terms of Use statement about use "in conjunction with your AI-powered tools or services";
> 2. whether any usage limit applies to the connector;
> 3. whether the free Wolfram Engine for Developers licence permits running your AgentTools MCP server locally, for my own use only.
> Thank you.

**Done when** a written reply exists. Until then W1 stays BLOCKED, though the route itself works.

**F4. Only if the connector breaks.** If a session shows Wolfram as needing authorisation or failed, open Settings, then Connectors, then Wolfram in the Claude app and reconnect. **Done when** `session_connectors_status` reads connected with 3 tools.

**Not needed:** no app restart; no restoring the old `WolframCloud` entry, which the connector supersedes with the same 3 tools; no Wolfram|Alpha App ID, npm or pip install, `InstallMCPServer`, or profile file; and `/Applications/WolframLocalMCPBridge.app`, the retired paid bridge, can be left alone.

## 6. Steps the assistant can take

All interactive, 1 Wolfram call at a time, never from a parallel agent, a bench run or a dispatched seat.

- **A1. Stale-kernel check before local use:** `ps -axo pid,ppid,etime,command | grep -i wolfram | grep -v grep`. A kernel counts as stale only if it is still listed after 20 s with an elapsed time over 1 minute and no `wolframscript` running. The `-i` matters: a kernel showed as `MacOS/WolframKernel -runfirst`, which the case-sensitive pattern in `.claude/CLAUDE.md` would miss.
- **A2. Licence reading on 2026-10-07 and whenever a licence message appears:** `wolframscript -code '$LicenseExpirationDate'`.
- **A3. Characterise the connector, 5 calls at most:** `{$Version, $ReleaseNumber}`; `f[x_] := x^2; f[3]` then a separate `f[3]` to confirm statelessness; `AbsoluteTiming[Pause[20]; "ok"]` and `AbsoluteTiming[Pause[35]; "ok"]` to bracket its ceiling. Raw outputs go into a new file under `experimental_notes/evidence/`, and any figure quoted from it gets a committed script that prints it.
- **A4. Test J1 end to end:** the connector parses "integrate x^2 log x from 0 to 1"; the local Engine runs the expression it returns; SymPy gives the independent value `-1/9`, which mpmath's quadrature agrees with at `-0.111111111111111`. Pass only if all 3 agree, with attribution to Wolfram Language.
- **A5. Documentation, on the founder's verdict 12(f) of the action list:** `.claude/CLAUDE.md` line 106 names a tool prefix that no longer exists, and line 242 calls the local Engine "the only WORKING Wolfram route today", which the connector's `Out[1]= 4` contradicts. `bench/tests/test_wolfram_route_retired_2026-09-10.py` asserts that sentence, so the 2 change in 1 commit. The file is the founder's, so the edit waits for that verdict.
- **A6. Done on 2026-09-17:** dispatched seats are denied Wolfram, as section 2 records.
- **A7. Optional, only on the founder's `y`:** 1 event on the founder's own calendar for 2026-10-07, "Renew Wolfram Engine licence: wolframscript -activate", with no invitees.

## 7. The routing rule

1. The local Engine runs only on demand from Bash in the main session, 1 call at a time: never as an MCP server, never from parallel agents, never from a dispatched seat.
2. The connector is for the assistant's interactive calls only, never for scripts, bench runners or panel seats, and its results are never written into an evidence ledger automatically.
3. 1 Wolfram computation at a time, of either kind.
4. English questions, documentation lookups and short stateless checks go to the connector; anything that may take over 20 s or needs definitions kept goes to the local Engine.
5. A result is evidence only as `bench/wolfram_standard.py` defines it: an `Out[` line from the connector; from the local kernel, exit 0 with output and no `Name::tag` message, `$Failed` or `$Aborted`, because the kernel exits 0 on `1/0`. Retry once before concluding anything, attribute every value used, and keep SymPy, mpmath or z3 as the independent check.

## 8. Still unverified, and what settles each

| Unknown | What settles it |
|---|---|
| Whether Wolfram's terms permit this use of the connector, and at what level | Wolfram's written reply, F3 |
| Whether the free Engine licence permits the local AgentTools server | Wolfram's written reply, F3; until then it is not run |
| The connector's ceiling, statefulness and version | A3 |
| Whether English parsed by the connector reproduces locally | A4 |
| Whether main sessions prompt for connector permission | F2, at the first call |
| Whether the Engine licence can be renewed before it expires | F1, on 2026-10-07 |
| Whether connector plots are public cloud objects | 1 test plot of harmless data, its link inspected, before any real data is plotted |

**Where each figure comes from.** 42 of 43 and 2026-09-04: `scripts/wolfram_route_health_2026-09-10.py`. 6 hours 11 minutes: subtraction of the 2 times recorded in task 0.1 of `experimental_notes/CDSFL_MASTER_TASK_LIST.md`. `-1/9`: SymPy's `integrate`, checked against mpmath's `quad`. The licence date: `$LicenseExpirationDate` on the local kernel, computed with Wolfram Language. The deny-layer results: `scripts/wolfram_seat_deny_probe_2026-09-17.py --live` and `bench/tests/test_wolfram_out_of_pipeline_2026-09-17.py`. The 26 s ceiling and the 2026-08-02 clash are prose in `.claude/CLAUDE.md` with no committed producer, quoted as a record rather than a measurement.

Written under CDSFL note standard v1.7 (26 August 2026).
