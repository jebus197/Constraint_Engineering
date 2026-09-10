# Research full record: 6 questions answered against the repository and the published record

2026-09-09 13:40 BST (Europe/London)

Six read-only agents were dispatched to answer six questions raised by the founder on 2026-09-09. None was permitted to edit anything. Every agent returned; 0 errored. This file is the UNFILTERED record, per the founder's standing instruction that findings are presented in full and summarised only afterwards, never instead.

## wolfram-renewal

**Wolfram's own published mechanism for the Free Engine is self-reactivation by the Engine, not an email reminder — no Wolfram-owned page promises a notification — and on this Mac Mini that self-reactivation has not fired: the mathpass licence file still carries its original 2026-08-02T21:09:38+0100 mtime with 2 days left, so the renewal must be driven by hand today.**

### Findings

LOCAL MEASUREMENTS (all run this session, 2026-09-09, 13:22 to 13:30 +01:00, read-only)

`wolframscript -code '$LicenseExpirationDate'` returns `DateObject[{2026, 9, 11}, Day]`, exit code 0.
`wolframscript -code '$LicenseType'` returns `Professional`, exit code 0.
`wolframscript -code 'DateDifference[Today, $LicenseExpirationDate]'` returns `Quantity[2, Days]`.

Product identity, so there is no doubt which thing is expiring: `$ProductInformation` returns `{ProductIDName -> WolframEngine, ProductKernelName -> Wolfram Language 15.0.0 Engine, ProductVersion -> 15.0.0 for Mac OS X ARM (64-bit) (May 26, 2026), ProductVersionNumber -> 15.}`. `$InstallationDirectory` is `/Applications/Wolfram Engine.app/Contents/Resources/Wolfram Player.app/Contents`. `{$Version, $ReleaseNumber, $SystemID, $LicenseServer, $LicenseProcesses, $MaxLicenseProcesses}` returns `{15.0.0 for Mac OS X ARM (64-bit) (May 26, 2026), 0, MacOSX-ARM64, Mac-mini.local, 1, 2}`.

LICENCE FILE LOCATION — the paths named in the task do not exist. `~/Library/Mathematica` does not exist. `~/.WolframEngine` does not exist. The real file is at `/Users/georgejackson/Library/WolframEngine/Licensing/mathpass`, and the kernel confirms it: `wolframscript -code '$PasswordFile'` returns that exact path. It is 125 bytes, 2 lines, permissions `-rw-r--r--`. Its mtime and its birth time are identical: 2026-08-02T21:09:38+0100. I did not open it. The companion cloud-authentication file is `/Users/georgejackson/Library/WolframEngine/ApplicationData/CloudObject/Authentication/properties.wl`, 97 bytes, mtime 2026-08-02T21:14:31+0100; I did not open that either.

THE DECISIVE LOCAL MEASUREMENT. Wolfram's published behaviour is that the Engine renews its own password as expiry approaches (see below). On this machine it has not. The mathpass mtime is still 2026-08-02T21:09:38+0100 with 2 days to run. This is not because the Engine has been idle: `~/Library/WolframEngine/Paclets/Configuration/pacletSiteData_15.pmd3` and `managerData_15.0.0.0.pmd2` were both modified at 2026-09-09T11:26:04+0100, before my session started, and my own kernel launches at 13:22 to 13:30 today also ran clean. So the Engine has started, reached the cloud, and written elsewhere, and still has not rewritten the licence file.

The observed password window is 40 days: written 2026-08-02, expiring 2026-09-11. Wolfram publishes no duration for the Free Engine password anywhere I could find, so 40 days is a measurement on this machine, not a published term.

`wolframscript --help`, run locally, lists both relevant flags in Wolfram's own shipped text: `-activate   Activate the Wolfram Engine through the cloud or with a key.` and `-entitlement ID   Activate the Wolfram Engine using on-demand licensing with the given license entitlement ID.`

QUESTION 1 — THE RENEWAL ROUTE AND ITS URL

The licence-issuing page is https://www.wolfram.com/engine/free-license/ and its instruction is: "To get your free license, sign in and accept the terms of use." Its button targets https://account.wolfram.com/access/wolfram-engine/free — a login wall I could not fetch, so I cannot report what it currently shows.

Wolfram's macOS setup article, https://support.wolfram.com/46070, gives the acquisition and activation steps verbatim: step 4 "Click the red Get Your License button", step 5 "If prompted, sign in with your Wolfram ID and password", step 6 "Read the Free Wolfram Engine for Developers Terms and Conditions of Use and select the checkbox to agree", step 7 "Click the Get License button", and step 18 "Enter your Wolfram ID and the associated password to complete activation."

Existing licences and expiry dates are visible at https://user.wolfram.com/portal/myProducts.html, named on https://support.wolfram.com/211 and https://support.wolfram.com/373.

QUESTION 2 — AUTOMATIC, EMAIL-PROMPTED, OR MANUAL: IT IS AUTOMATIC, AND THERE IS NO EMAIL

Wolfram Research's own Docker Hub repository, https://hub.docker.com/r/wolframresearch/wolframengine, states: "When the actual date is close to the expiration date, the Wolfram Engine will automatically reactivate itself." The same sentence is corroborated on https://github.com/arnoudbuzing/wolfram-engine-docker/blob/master/README.md as "the password for the Free Wolfram Engine for Developer has an expiration date. When the actual date is close to the expiration date, the Wolfram Engine will automatically re-activate itself." That second repository is a personal one, so it corroborates rather than establishes.

I found no Wolfram-owned page stating that Wolfram emails an expiry reminder for the Free Wolfram Engine. Not on the FAQ, not on the free-licence page, not on the terms, not in the macOS or Linux setup articles, not on support.wolfram.com/211 or /268. Marked UNCONFIRMED in the negative sense: absence of a published promise, not proof no email is ever sent.

There is an apparent contradiction to name. The Wolfram Engine FAQ, https://www.wolfram.com/engine/faq/, says: "Each copy must be authenticated once with the Wolfram Cloud. The authentication does not expire, though Wolfram reserves the right to terminate use in the event of abuse." That reads as "nothing expires". It is reconciled by Wolfram's own documentation for the symbol: https://reference.wolfram.com/language/ref/$LicenseExpirationDate.html says "The first element of $LicenseExpirationDate is Infinity if there is no explicit expiration date." This machine returns a date, not Infinity. So the licence PASSWORD is explicitly time-limited even though the cloud AUTHENTICATION is not. The FAQ sentence is about the wrong object.

QUESTION 3 — WHAT HAPPENS AT EXPIRY

Wolfram's answer, https://support.wolfram.com/268: "If you are using a time-limited license, you will be prompted to reactivate your license when it expires." That is a stop, not a degradation — the kernel demands reactivation rather than running with reduced capability. No grace period is documented for a single-machine free licence; the only grace Wolfram publishes is on https://support.wolfram.com/211, where "products expire 30 days beyond the stated expiration date" applies to organizational site licences, which this is not.

What I could NOT confirm from any Wolfram page: exactly how that prompt surfaces to a non-interactive `wolframscript -code '...'` call driven from Bash by a bench runner — whether it prompts on stdin, hangs, or exits non-zero. A third-party GitHub thread, https://github.com/njpipeorgan/wolfram-language-notebook/issues/22, reports the string "Activated license expired", but that is not a Wolfram source and I am marking it UNCONFIRMED. This matters here specifically because this project has a recorded history of error strings being ingested as answers.

QUESTION 4 — RE-ACTIVATION MECHANICS

No re-download is needed. Activation is step 18 of the macOS article, after installation, and is independent of it.

The Wolfram ID is reused. https://support.wolfram.com/373: "Enter your Wolfram Account credentials: the Wolfram ID and password that you use to log into your Wolfram Account."

`wolframscript -activate` is the in-product route and is present on this installation — its own help text reads "Activate the Wolfram Engine through the cloud or with a key." I did not run it, because it writes to mathpass and this task is read-only. Wolfram's Docker page documents `-entitlement` but not `-activate`, so the flag's existence here rests on the locally installed binary's own help output rather than a web page.

QUESTION 5 — LEAD TIME

There are 2 instant self-service routes and 1 slow one, and which applies turns on a key count.

The instant routes are the Engine reactivating itself, and signing in again at https://account.wolfram.com/access/wolfram-engine/free.

The slow route is the one to worry about. The FAQ, https://www.wolfram.com/engine/faq/, under "What should I do if WolframScript says my account has no valid keys?": "Two keys are assigned to each account. If you have not logged in, you should do so to get the keys associated with your account. If both of the keys have already been used, you can contact us to reset them." Wolfram's Docker page confirms the accounting: "Activating a Wolfram Engine Docker image uses up one of the two activation keys that were assigned to you when you signed up." Contacting Wolfram to reset keys is a human support turnaround with no published service level. That is the tail risk, and it is why the work should happen today rather than on the 11th.

I could NOT confirm from any Wolfram page whether re-activating a machine that is already activated consumes the second of the 2 keys or renews against the first. Wolfram's own nearest statement, https://support.wolfram.com/268, concerns a CHANGED machine: "Your activation key was associated with your previous system's MathID during an earlier activation process", remedied by a System Transfer Form. That is a different case from re-activating the same MathID. UNCONFIRMED.

WHAT THE PROJECT RECORD ALREADY SAID

The expiry was known and written down 5 weeks ago. `/Users/georgejackson/Developer_Projects/Constraint_Engineering/.claude/CLAUDE.md:256` reads: "`$LicenseExpirationDate` is **2026-09-11**; renew before then." Lines 254 to 255 carry an operational warning worth heeding before any activation attempt: "If `wolframscript` ever reports a licence problem, check `ps` for `MacOS/wolfram -run` processes FIRST — a stale MCP-spawned kernel is the likely cause, not the licence."

The internal reminder was wired and it fired. `/Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/founder_decision_ledger.py:59` records: ("The Wolfram Engine licence expiry", [19,63,109], "RULED", "", "Founder ruled 2026-09-06: set a reminder. Done, fires 2026-09-09."). The mechanism behind it is real, not a docstring: `/Users/georgejackson/.claude/scheduled-tasks/wolfram-licence-expiry-2026-09-11/SKILL.md`, mtime 2026-09-06T12:50:46+0100, whose text instructs the receiving session to verify with `wolframscript -code 'Print[$LicenseExpirationDate]'` before saying anything.

One proposed guard was NOT wired. The 2026-08-05 recovery-resource audit, at `/Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/adversarial_records/recovery_resource_audit_raw_2026-08-05.json:568`, proposed: "Worth adding: .claude/CLAUDE.md records $LicenseExpirationDate 2026-09-11 for the local Engine, five weeks out — an onboarding check that surfaces that date would earn its place where the current one does not." It was not implemented. `scripts/cdsfl_onboard.py:318` still does only `script = shutil.which("wolframscript")` and reports `[FOUND] wolframscript at {script} — on-demand local engine`. The onboarding script checks that the binary exists and never checks whether its licence is about to lapse.

BLAST RADIUS IF IT LAPSES

`resources/RECOVERY.md:1005-1012` records the local Engine as having no compute ceiling and persistent session state, versus the credential-free hosted endpoint `agenttools.wolfram.com/mcp`, which is "STATELESS and a hard **~30 s wall / ~26 s compute** gateway ceiling", described there as "capability-inverted". The scheduled reminder's own text puts the consequence plainly: the local Engine is the third tool in the standing 2-tool cross-verification rule alongside SymPy and mpmath, and the fallback is not equivalent.

### Does the record support the founder's framing?

CONTRADICTED on mechanism, and the local evidence removes the practical comfort too.

The framing asserted was that an email reminder would arrive on or before expiry. No Wolfram-owned page promises any such email for the Free Wolfram Engine. I checked the FAQ (https://www.wolfram.com/engine/faq/), the free-licence page (https://www.wolfram.com/engine/free-license/), the Terms and Conditions (https://www.wolfram.com/legal/terms/wolfram-engine.html), the macOS and Linux setup articles (https://support.wolfram.com/46070, /46072), and the two expiry articles (https://support.wolfram.com/211, /268). None mentions a notification for this licence class. Wolfram's published mechanism is the opposite shape: the software renews itself silently. From Wolfram Research's own Docker Hub repository, https://hub.docker.com/r/wolframresearch/wolframengine, verbatim: "When the actual date is close to the expiration date, the Wolfram Engine will automatically reactivate itself." Nothing in that design has any reason to send an email, because on Wolfram's model the user is never meant to act.

So there are 2 halves to the framing and they fail differently. The mechanism half is wrong: there is no reminder to wait for. The conclusion half — that nothing needs doing — would have been RIGHT if auto-reactivation worked here, and the local measurement says it has not. `/Users/georgejackson/Library/WolframEngine/Licensing/mathpass` still carries mtime 2026-08-02T21:09:38+0100 with 2 days left, while the Engine demonstrably ran and reached the Wolfram Cloud this morning (paclet configuration files rewritten at 2026-09-09T11:26:04+0100). Waiting on either mechanism — the email that is not promised, or the self-renewal that has not fired — leaves the licence to lapse.

One correction to the framing's premise about what the record contained. The claim that the assumption might be wrong was already the project's own position: `.claude/CLAUDE.md:256` says "renew before then", and the founder ruled on 2026-09-06 to set a reminder rather than trust a notification (`scripts/founder_decision_ledger.py:59`). That reminder is genuinely wired at `/Users/georgejackson/.claude/scheduled-tasks/wolfram-licence-expiry-2026-09-11/SKILL.md` and it is what produced today's question. The internal instrument worked. It is the external one that never existed.

### Recommendation (not implemented)

Do it today, by hand, and do not wait for either mechanism. I have implemented nothing; this is the sequence to run.

Before anything else, 2 cheap safety steps. First, run `ps aux | grep 'MacOS/wolfram -run'` and clear any stale kernel — `.claude/CLAUDE.md:254-255` records that a stale MCP-spawned kernel presents exactly as an activation fault. Second, copy the licence file somewhere safe: `cp ~/Library/WolframEngine/Licensing/mathpass ~/mathpass.bak.2026-09-09`. It is 125 bytes, and it is the only thing standing between the current working state and a failed activation attempt. Keep the copy out of git.

Then, in order, stopping at the first that works.

1. Run `wolframscript -activate` on the Mac Mini and sign in with the existing Wolfram ID when prompted. This is the flag the installed binary documents as "Activate the Wolfram Engine through the cloud or with a key", it needs no re-download, and it reuses the Wolfram ID per https://support.wolfram.com/373. This step needs the founder's account password, so it is his to run, not mine.

2. Verify by measurement, not by the absence of an error. Run `wolframscript -code '$LicenseExpirationDate'` and confirm a date beyond 2026-09-11, and separately run `stat -f '%Sm' ~/Library/WolframEngine/Licensing/mathpass` and confirm the mtime has moved off 2026-08-02T21:09:38+0100. Both, not one — this project has been bitten before by a call that returned successfully while carrying an error string.

3. If step 1 fails, sign in at https://account.wolfram.com/access/wolfram-engine/free and re-request the free licence, then check https://user.wolfram.com/portal/myProducts.html for what key and expiry the account actually holds. Only the founder can do this.

4. If WolframScript reports that the account has no valid keys, that is the "both of the keys have already been used" case from Wolfram's FAQ, and the only route is contacting Wolfram to reset them. That is human turnaround with no published lead time. It is the single reason not to leave this until the 11th.

Two things worth doing after the licence is safe, neither urgent today. The 2026-08-05 audit's proposed onboarding check was never implemented — `scripts/cdsfl_onboard.py:318` tests only that the binary is on PATH and never reads `$LicenseExpirationDate`. Wiring that check is what would make the next expiry visible without depending on a one-shot scheduled reminder. And given the ambiguity in how expiry surfaces to a piped `wolframscript -code` call, the cross-verification path should treat a Wolfram result that does not parse as a FAILED verification rather than as evidence, which is the same guard the 2026-08-02 Wolfram access note already recommended and which remains the relevant failure shape here.

### What could not be established

Five things I could not establish.

1. What https://account.wolfram.com/access/wolfram-engine/free currently shows. It is a login wall and returned only the page title. I therefore cannot confirm whether a fresh licence issues instantly on sign-in, nor how many of the founder's 2 account keys are already consumed. That second unknown is the one that decides whether renewal takes 2 minutes or a support ticket, and only the founder can resolve it by signing in.

2. Whether `wolframscript -activate` on an already-activated machine consumes the second of the 2 account keys or renews against the first. No Wolfram page addresses same-MathID re-activation; https://support.wolfram.com/268 covers only the changed-machine case, remedied by a System Transfer Form. UNCONFIRMED, and it is why backing up mathpass first is worth the 1 command.

3. What "close to the expiration date" means. Wolfram's own sentence on https://hub.docker.com/r/wolframresearch/wolframengine gives no threshold. I cannot say whether auto-reactivation is still due to fire within the remaining 2 days, or whether its absence at 2 days out already means it will not. What I can say is measured: it has not fired, and the Engine has had opportunities today.

4. How expiry surfaces to a non-interactive `wolframscript -code '...'` call driven from Bash — prompt on stdin, hang, or non-zero exit. Wolfram documents only "you will be prompted to reactivate your license when it expires" (https://support.wolfram.com/268), which describes an interactive session. The one concrete error string I found, "Activated license expired", is from a third-party GitHub thread and is UNCONFIRMED by any Wolfram page.

5. The published term of the Free Engine password. Wolfram states nowhere I could find how long it lasts. The 40 days observed here (2026-08-02 to 2026-09-11) is a measurement on this one machine and should not be generalised.

Two smaller notes. I did not open `mathpass` or `properties.wl`, so everything said about their contents is from Wolfram's published description of the format rather than from this machine's files. And the absence of a Wolfram-published email reminder is an absence of evidence across the 7 Wolfram pages I checked, not proof that no email is ever sent — if one arrives, it is undocumented, and an undocumented notification is not something to plan around.

### Evidence

- Local, 2026-09-09T13:22:49+01:00: `wolframscript -code '$LicenseExpirationDate'` -> DateObject[{2026, 9, 11}, Day], exit 0; `wolframscript -code '$LicenseType'` -> Professional, exit 0
- Local: `wolframscript -code 'DateDifference[Today, $LicenseExpirationDate]'` -> Quantity[2, Days] — 2 days remaining as of 2026-09-09
- Local: `wolframscript -code '$ProductInformation'` -> ProductIDName -> WolframEngine, ProductKernelName -> Wolfram Language 15.0.0 Engine — confirms this is the Wolfram Engine, not Mathematica
- Local: `wolframscript -code '$PasswordFile'` -> /Users/georgejackson/Library/WolframEngine/Licensing/mathpass — the kernel names its own licence file
- /Users/georgejackson/Library/WolframEngine/Licensing/mathpass — 125 bytes, 2 lines, mtime AND birth both 2026-08-02T21:09:38+0100. NOT OPENED. Unchanged with 2 days to expiry, which is the evidence that auto-reactivation has not fired
- /Users/georgejackson/Library/WolframEngine/ApplicationData/CloudObject/Authentication/properties.wl — 97 bytes, mtime 2026-08-02T21:14:31+0100. NOT OPENED
- /Users/georgejackson/Library/WolframEngine/Paclets/Configuration/pacletSiteData_15.pmd3 and managerData_15.0.0.0.pmd2 — mtime 2026-09-09T11:26:04+0100, proving the Engine ran and reached the cloud today without renewing the licence
- ~/Library/Mathematica does not exist; ~/.WolframEngine does not exist — both paths named in the task are absent on this machine
- Local `wolframscript --help`: '-activate   Activate the Wolfram Engine through the cloud or with a key.' and '-entitlement ID   Activate the Wolfram Engine using on-demand licensing with the given license entitlement ID.'
- https://hub.docker.com/r/wolframresearch/wolframengine — Wolfram Research's own repository: "When the actual date is close to the expiration date, the Wolfram Engine will automatically reactivate itself." Also: "Activating a Wolfram Engine Docker image uses up one of the two activation keys that were assigned to you when you signed up."
- https://www.wolfram.com/engine/faq/ — "Each copy must be authenticated once with the Wolfram Cloud. The authentication does not expire, though Wolfram reserves the right to terminate use in the event of abuse." And: "Two keys are assigned to each account. If you have not logged in, you should do so to get the keys associated with your account. If both of the keys have already been used, you can contact us to reset them."
- https://reference.wolfram.com/language/ref/$LicenseExpirationDate.html — "The first element of $LicenseExpirationDate is Infinity if there is no explicit expiration date." This machine returns a date, so the licence is explicitly time-limited and the FAQ's non-expiry claim does not cover it
- https://support.wolfram.com/268 — "If you are using a time-limited license, you will be prompted to reactivate your license when it expires." Answers question 3: a stop, not a degradation
- https://support.wolfram.com/211 — expiry visible in the Wolfram Account; the 30-day post-expiry grace it mentions applies to organizational site licences, not this one
- https://www.wolfram.com/engine/free-license/ — "To get your free license, sign in and accept the terms of use." Button targets https://account.wolfram.com/access/wolfram-engine/free (login wall, not fetchable)
- https://support.wolfram.com/46070 — macOS setup, steps 4 to 7 (Get Your License, sign in with Wolfram ID, accept terms, Get License) and step 18 "Enter your Wolfram ID and the associated password to complete activation"
- https://support.wolfram.com/373 — "Enter your Wolfram Account credentials: the Wolfram ID and password that you use to log into your Wolfram Account." Confirms the Wolfram ID is reused. Names the portal https://user.wolfram.com/portal/myProducts.html
- https://github.com/arnoudbuzing/wolfram-engine-docker/blob/master/README.md — corroborates the auto-reactivation sentence and describes mathpass as "a single line with four fields... the machine name, a unique machine identifier, your activation key and the password". Personal repository, corroborating only
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/.claude/CLAUDE.md:256 — "`$LicenseExpirationDate` is **2026-09-11**; renew before then." Lines 254-255 warn to check `ps` for stale `MacOS/wolfram -run` kernels first
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/founder_decision_ledger.py:59 — ("The Wolfram Engine licence expiry", [19,63,109], "RULED", "", "Founder ruled 2026-09-06: set a reminder. Done, fires 2026-09-09.")
- /Users/georgejackson/.claude/scheduled-tasks/wolfram-licence-expiry-2026-09-11/SKILL.md — mtime 2026-09-06T12:50:46+0100. The reminder is wired, not merely described; it fired today
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/cdsfl_onboard.py:318 — `script = shutil.which("wolframscript")`. The onboarding check tests only that the binary exists; it never reads $LicenseExpirationDate
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/adversarial_records/recovery_resource_audit_raw_2026-08-05.json:568 — proposed an onboarding check surfacing the 2026-09-11 date; not implemented, per cdsfl_onboard.py:318
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/resources/RECOVERY.md:1005-1012 — local Engine has no ceiling and keeps session state; the hosted fallback is stateless with a ~30 s wall / ~26 s compute ceiling

## qwerty-and-action-queue

**Both files are Project_Genesis artefacts from February-March 2026 (later copied into Metis), never present in Constraint_Engineering across 1,161 revisions; QWERTY_CHECKPOINT.md was the output file of the `qwerty` 5-point per-turn self-verification protocol, and the founder's hypothesis is SUPPORTED with one refinement — the ancestor of the MC list is the shorthand table that contained `qwerty`, not the checkpoint file itself.**

### Findings

## Verdict 1: QWERTY_CHECKPOINT.md

**What it was.** The output artefact of the `qwerty` checkpoint protocol — a 5-point self-verification the implementation agent ran on every turn. The canonical spec is `/Users/georgejackson/Developer_Projects/collab_protocol/SHARED_PROTOCOL.md:48-64` (mtime 2026-02-25 14:14, the oldest copy found):

| Letter | Check | What It Verifies |
| **q** | Quality | Tests passing (run suite, report count) |
| **w** | Written | Committed and pushed (git status clean, origin up to date) |
| **e** | Exchanged | Other agent notified via IM (post with commit hash + what changed) |
| **r** | Recorded | Persistent memory updated (current state, test count, pending items) |
| **ty** | Tidy | Docs lock-stepped (all documentation reflects current code state) |

Same file, line 64: "**George types `q` or `qwerty`** — both mean the same thing. He suspects an anomaly. This forces a full re-verification from scratch (read actual files/state, not from memory)."

It was also a catastrophic-recovery document. `Project_Genesis/cw_handoff/QWERTY_CHECKPOINT.md:11-13` opens a section titled "CC Catastrophic Recovery Context" — "If CC (Claude) loses all context and must resume from this file alone" — followed by 9 numbered recovery reads at lines 23-32.

**Did it ever exist on disk.** Yes, in 2 places, neither of them CDSFL:
- `/Users/georgejackson/Developer_Projects/Project_Genesis/cw_handoff/QWERTY_CHECKPOINT.md` — 48,892 bytes, 591 lines, mtime 2026-03-11 18:04. Added to git by `1a7701d` (2026-03-06 00:17:02), last touched by `01c1704` (2026-03-11 17:54:19). Genesis HEAD is `c26f5e6`, 2026-03-11 21:33:37 — that repo has not moved since.
- `/Users/georgejackson/Developer_Projects/Metis/coordination/QWERTY_CHECKPOINT.md` — 1,775 bytes, 31 lines, mtime 2026-04-04 17:18. Metis is not a git repo (`git log` returns nothing).

**In Constraint_Engineering: never.** `git log --all -- '*QWERTY_CHECKPOINT*'` returns 0 commits across 1,161 revisions; `ls QWERTY_CHECKPOINT.md` returns "No such file or directory".

**Superseded.** Yes, functionally. `qwerty` as a *command* is not defined anywhere in the current global instruction set — `grep -ci qwerty ~/.claude/CLAUDE.md` returns 1, and that single hit is the filename inside the `rs` definition on line 250. Its 5 checks were absorbed: `sv` covers w/r/ty, `rs` covers the recovery role. The Genesis protocol also depended on the IM service, which the 2026-08-05 audit measured as 123 days stale.

## Verdict 2: ACTION_QUEUE.md

**What it was.** A flat-file cross-agent task tracker with 4 sections — PENDING / IN PROGRESS / COMPLETED / BLOCKED — one line per task. Its own header (`Project_Genesis/cw_handoff/ACTION_QUEUE.md:1-4`): "Action Queue — Cross-Agent Persistent Task Tracker / All agents: READ THIS FILE ON EVERY SESSION START. / Update task status as you work. Add new tasks as they arise. / Format: - [agent] [date] description | assigned_by: X | status: pending|in_progress|completed|blocked". Entries carry agent labels `cc`, `cx`, `cw`, `all`.

**Did it ever exist on disk.** Yes, in 2 places, neither CDSFL:
- `Project_Genesis/cw_handoff/ACTION_QUEUE.md` — 2,195 bytes, 27 lines, mtime 2026-03-06. Added `1a7701d` (2026-03-06), last touched `db3a073` (2026-03-06 06:11:11). Untouched in git for 187 days.
- `Metis/coordination/ACTION_QUEUE.md` — 679 bytes, 17 lines, mtime 2026-04-04 16:54. Its only content is 1 BLOCKED entry: "- [all] [2026-04-04] Phase 1 implementation | assigned_by: george | status: blocked | reason: awaiting CDSFL P1 (insect brain validation), P2 (Exp 29), P3 (27 frontier bench tests)".

**In Constraint_Engineering: never.** 0 commits, 0 files.

**Superseded.** For CDSFL there was nothing to supersede — the role is filled by `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` (22,893 bytes, mtime 2026-08-27) plus the operational tracker. For Metis it is still nominally live but empty of work.

## The founder's hypothesis on MC-list ancestry: SUPPORTED, with one refinement

The oldest shorthand table found is `collab_protocol/SHARED_PROTOCOL.md:11-17` (mtime 2026-02-25 14:14):

| `y` | Yes / approved |
| `r` | Read / review (read IM + relevant checkpoints before acting) |
| `t` | Continue (keep going with current work) |
| `rt` | Read + continue... |
| `q` / `qwerty` | George suspects an anomaly. Re-verify all five checks from scratch. |

Extended 8 days later in `Project_Genesis_Notes/GENESIS_SHORTCUTS.md:5-16` (mtime 2026-03-05) to 12 entries, adding `d` (discuss), `p` (Popperian falsification pass), `cc`, `cx`, `cw`, `x`, `ob`. `Project_Recovery/RECOVERY.md:27-42` carries the same table with `p` given the full P-pass definition and the note "Canonical definition: `~/.claude/CLAUDE.md`" — the moment the table moved from project-local to global.

4 entries survive verbatim in the current global list at `~/.claude/CLAUDE.md:250`: "y = yes/approved", "rt = read + continue", "d = discuss before proceeding", "r = re-read key context files". `p` survives as the whole P-Pass Logic block. `t` is no longer defined on line 250. `qwerty` is the one ancestral command that did not survive.

Two non-command directives from that same 2026-02 document also survive into the present global CLAUDE.md: `SHARED_PROTOCOL.md:21` "**Catch George's typos** — standing directive for both agents" and `:109` "Stale documentation is a defect" (now `docs-defect-parity`).

**The refinement.** QWERTY_CHECKPOINT.md was the *file the command wrote to*, not the list. The list's ancestor is the table that contained `qwerty` as 1 of its 5 entries. So the recollection is right in substance — the current MC vocabulary descends directly from the protocol in which `qwerty` sat — and slightly off in referent.

## Transcript evidence

- QWERTY_CHECKPOINT: 676 lines across all `.jsonl` under `~/.claude/projects`. **Earliest** 2026-08-05T13:15:07.976Z, `6142171c-97c7-4e77-9a9a-8d36d795bb89.jsonl` line 10059. **Latest** 2026-09-09T12:24:17.877Z (this task's own brief).
- ACTION_QUEUE: 739 lines. **Earliest** 2026-07-22T00:01:13.205Z, same file line 174. **Latest** 2026-09-09T12:24:17.877Z.
- Distribution is bursty, not sustained: 501 of 676 QWERTY lines and 545 of 739 ACTION_QUEUE lines fall on 2026-09-05 alone (panel-run echo of the same brief).
- The 196 `.jsonl` files under `-Users-georgejackson-Developer-Projects-Constraint-Engineering` contain **0** mentions of either name.

**Founder verbatim, 2026-09-08T15:18:38.578Z** (`a07b3790-...jsonl` line 43916): "QWERTY checkpoint is an old resource that has probably been significantly superseded by later work. I don't know what ACTION_QUEUE.md is? Is this the same category of item? Do we need it? Should we use it?"

**Founder verbatim, 2026-09-09T12:21:11.938Z** (line 45098): "I did already answer this. QWERTY is a very. old resource and I can no longer remember what it was for, or if it might still be useful? I think it was something that existed at the inception of/inspired your current MC command list? I have no recollection of a resource called ACTION_QUEUE.md? So same question." (Typo: "a very. old resource" — stray full stop.)

**Prior CC answer, 2026-09-08T15:26:48.372Z** (line 44037): "**Neither has ever existed in this repository — 0 commits have touched either.** So ACTION_QUEUE isn't a superseded resource; it was never here." Correct as far as it went; it did not identify which project they belong to.

## This was already established 35 days ago and not acted on

`experimental_notes/Recovery_Resource_Audit_2026-08-05.md:1234`: "Also: ACTION_QUEUE.md (mtime Mar 6) and QWERTY_CHECKPOINT.md (mtime Mar 11) — the two other artefacts named in the global `rs` definition — both live under Project_Genesis/cw_handoff/, not in CDSFL at all."

Its proposed fix, `:1237`, is still unapplied 35 days later: "Rewrite the global `rs` definition to name what a CDSFL `rs` actually consults today ... dropping IM, ACTION_QUEUE.md and QWERTY_CHECKPOINT.md, all three of which are Project_Genesis artefacts."

The staleness is flagged in 2 CDSFL documents, identically worded, at `resources/RECOVERY.md:40` and `experimental_notes/CDSFL_Agent_Operational_Plan.md:92`: "**STALE IN THE `rs` DEFINITION:** it names `ACTION_QUEUE.md` and `QWERTY_CHECKPOINT.md`; **neither exists**." The flag was added; the definition it flags was not changed.

## What is lost by removing the names from `rs`

**For CDSFL: nothing.** Neither file has ever existed here.

**For Metis: nothing either**, because both pointers already exist project-locally and do not depend on the global line:
- `Metis/resources/RECOVERY.md:22-23` — Tier 2 steps 9 and 10: "Read `coordination/ACTION_QUEUE.md` (pending/blocked tasks)" / "Read `coordination/QWERTY_CHECKPOINT.md` (last checkpoint)"
- `Metis/CLAUDE.md:55-64` — the full qwerty protocol and "CC writes every checkpoint to `coordination/QWERTY_CHECKPOINT.md`"
- `Metis/resources/ONBOARDING.md:32-33` — both in the directory tree
- Memory: `feedback_metis_sv_local.md:11` — "When the user says `sv` in Metis context, update MEMORY.md, QWERTY_CHECKPOINT.md, ONBOARDING.md, post to Metis IM, but do NOT commit or push."

**For Genesis: nothing.** `Project_Recovery/RECOVERY.md:195` and `:296` name the paths independently.

**A mention is not a wiring, checked.** `Metis/coordination/file_integrity.py` names both filenames only in its module docstring at line 5; `grep -n 'QWERTY_CHECKPOINT\|ACTION_QUEUE'` over that 16,124-byte file returns exactly 1 hit, that docstring line. No code path reads either file by name — the signer takes a file argument. So the integrity machinery is not a caller that would break.

**One residual site the removal should also cover:** `Constraint_Engineering/resources/SHORTCUTS.md:36` still reads "rebuild full working context from session-context + **action queue + checkpoints** + memory + recovery resources". It does not name the files, but it points at the same two non-existent things.

### Does the record support the founder's framing?

SUPPORTED, with one refinement.

The founder wrote, verbatim: "I think it was something that existed at the inception of/inspired your current MC command list?" The record supports this. `collab_protocol/SHARED_PROTOCOL.md:11-17` (mtime 2026-02-25 14:14) is the oldest shorthand table found anywhere on disk, and `q`/`qwerty` is 1 of its 5 entries alongside `y`, `r`, `t`, `rt`. 4 of those entries — y, r, rt, and (added a week later at GENESIS_SHORTCUTS.md:5-16) d — survive verbatim in the current global list at ~/.claude/CLAUDE.md:250, as does `p` in the form of the whole P-Pass Logic block. Two non-command directives from the same February document also survive: "Catch George's typos" and "Stale documentation is a defect".

The refinement: QWERTY_CHECKPOINT.md was the FILE the `qwerty` command wrote to, not the command list. The ancestor of the MC list is the shorthand table in which `qwerty` appeared. The founder's memory of a connection is correct; the referent is one level off. `qwerty` is also the single ancestral command that did NOT survive — it is undefined in the current global CLAUDE.md, where only its orphaned filename remains inside the `rs` line.

The founder also wrote: "QWERTY checkpoint is an old resource that has probably been significantly superseded by later work." SUPPORTED. Its 5 checks were absorbed into `sv` (written/recorded/tidy) and `rs` (recovery), and its "Exchanged" leg depended on the IM service the 2026-08-05 audit measured as 123 days stale.

And: "I have no recollection of a resource called ACTION_QUEUE.md?" CONSISTENT with the record, and the reason is now established rather than assumed. It was a Genesis-era flat-file task tracker whose git history ends on 2026-03-06 — 1 day after it was added — and whose Metis copy has held exactly 1 BLOCKED line since 2026-04-04. There is nothing to remember because it was barely used, and it has never touched CDSFL in 1,161 revisions.

### Recommendation (not implemented)

DO NOT IMPLEMENT — findings only. Recommended, for founder ruling:

1. Amend the `rs` definition at ~/.claude/CLAUDE.md:250 so the 2 filenames are project-conditional rather than unconditional: name `OUTSTANDING_QUEUE_to_BR2.md` and the operational tracker for CDSFL, and keep ACTION_QUEUE.md / QWERTY_CHECKPOINT.md only under an explicit "(Metis and Genesis only)" qualifier. A flat delete is also safe — every consumer already has a project-local pointer (Metis/resources/RECOVERY.md:22-23, Metis/CLAUDE.md:55-64, Project_Recovery/RECOVERY.md:195) — but the conditional form loses nothing at all and satisfies `additive-standard` without needing a dominance measurement.

2. Sweep the residual site at Constraint_Engineering/resources/SHORTCUTS.md:36 ("action queue + checkpoints"), which points at the same 2 non-existent things without naming them.

3. Do NOT delete either file from Metis or Genesis. Both are the sole surviving record of the coordination protocol those projects ran under, and QWERTY_CHECKPOINT.md carries Genesis's catastrophic-recovery context at lines 11-34. Neither costs anything to leave in place.

4. Consider recording the provenance in memory, since this is the 3rd time the question has been asked and answered — 2026-07-02 (tracker line 884, "ACTION_QUEUE/QWERTY confirmed not-CDSFL-artifacts"), 2026-08-05 (audit line 1234), 2026-09-08 (transcript line 44037) — and each answer was lost before the next asking. The stale-flag text was added to 2 CDSFL documents on the strength of the August finding, but the definition it flags was never changed; the flag has now outlived 35 days of sessions.

### What could not be established

3 things could not be established.

1. **When the founder first coined `qwerty`, and in whose words.** The oldest artefact is collab_protocol/SHARED_PROTOCOL.md at mtime 2026-02-25 14:14, with IMPLEMENTATION_AGENT.md mentioning it a day earlier at 2026-02-24 23:44. No transcript from that period survives: the earliest timestamped mention of either filename anywhere under ~/.claude/projects is 2026-07-22, roughly 5 months later. So the origin is dated by file mtime and git commit only, not by a founder message. Whether `qwerty` was named for the keyboard row, for the 5 letters q-w-e-r-ty spelling the checks, or the reverse — checks fitted to a memorable string — is not recorded in any file I read.

2. **Whether QWERTY_CHECKPOINT.md was ever consulted after 2026-04-04.** Both Metis copies stop at that date, Genesis at 2026-03-11. Absence of later writes is not proof of absence of reads, and no read log exists.

3. **Whether the founder wants Metis kept alive at all.** Metis is not a git repo, its ACTION_QUEUE holds 1 BLOCKED line dated 2026-04-04, and its unblocking condition is CDSFL prerequisites that have since been restructured. That bears on whether the Metis pointers are worth preserving, and it is a founder decision, not a record question.

### Evidence

- /Users/georgejackson/Developer_Projects/collab_protocol/SHARED_PROTOCOL.md:11-17 — the oldest shorthand table found (mtime 2026-02-25 14:14): y, r, t, rt, q/qwerty. The ancestor of the current MC list.
- /Users/georgejackson/Developer_Projects/collab_protocol/SHARED_PROTOCOL.md:48-64 — the canonical qwerty spec: q=Quality, w=Written, e=Exchanged, r=Recorded, ty=Tidy, plus 'George types `q` or `qwerty` — both mean the same thing.'
- /Users/georgejackson/Developer_Projects/collab_protocol/SHARED_PROTOCOL.md:21 — 'Catch George's typos — standing directive for both agents', surviving verbatim into the present global CLAUDE.md.
- /Users/georgejackson/Developer_Projects/Project_Genesis_Notes/GENESIS_SHORTCUTS.md:5-16 (mtime 2026-03-05) — the table extended to 12 entries, adding d, p, cc, cx, cw, x, ob.
- /Users/georgejackson/Developer_Projects/Project_Recovery/RECOVERY.md:27-42 — same table with p's full P-pass definition and 'Canonical definition: ~/.claude/CLAUDE.md' — the move from project-local to global.
- /Users/georgejackson/Developer_Projects/Project_Genesis/cw_handoff/QWERTY_CHECKPOINT.md:11-34 — 'CC Catastrophic Recovery Context'; 591 lines, 48,892 bytes, mtime 2026-03-11 18:04.
- /Users/georgejackson/Developer_Projects/Project_Genesis/cw_handoff/ACTION_QUEUE.md:1-4 — the tracker's own header and line format; 27 lines, 2,195 bytes, mtime 2026-03-06.
- /Users/georgejackson/Developer_Projects/Metis/coordination/QWERTY_CHECKPOINT.md:4 — 'Format follows the qwerty protocol: q=quality, w=written, e=exchanged, r=recorded, ty=tidy.' 31 lines, mtime 2026-04-04 17:18.
- /Users/georgejackson/Developer_Projects/Metis/coordination/ACTION_QUEUE.md:17 — the single BLOCKED entry, Phase 1 awaiting CDSFL prerequisites. 17 lines, mtime 2026-04-04 16:54.
- /Users/georgejackson/Developer_Projects/Metis/resources/RECOVERY.md:22-23 — Metis Tier 2 recovery steps 9 and 10 name both files; the project-local pointer that survives global removal.
- /Users/georgejackson/Developer_Projects/Metis/CLAUDE.md:55-64 — the full qwerty protocol and 'CC writes every checkpoint to coordination/QWERTY_CHECKPOINT.md'.
- /Users/georgejackson/Developer_Projects/Metis/coordination/file_integrity.py:5 — both filenames appear ONLY in the module docstring; 1 hit in 16,124 bytes, no code caller.
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/memory/feedback_metis_sv_local.md:11 — the only memory-directory mention of either name, naming QWERTY_CHECKPOINT.md as a Metis `sv` target.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Recovery_Resource_Audit_2026-08-05.md:1234 — the audit already placed both under Project_Genesis/cw_handoff/, 'not in CDSFL at all'.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Recovery_Resource_Audit_2026-08-05.md:1237 — the proposed fix, still unapplied after 35 days.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/resources/RECOVERY.md:40 and experimental_notes/CDSFL_Agent_Operational_Plan.md:92 — identical stale-flag text already in the repo.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/resources/SHORTCUTS.md:36 — residual 'action queue + checkpoints' in the `rs` row, not yet corrected.
- /Users/georgejackson/.claude/CLAUDE.md:250 — the live `rs` definition still naming ACTION_QUEUE.md and QWERTY_CHECKPOINT.md; `grep -ci qwerty` over the whole file returns 1, that filename.
- git -C /Users/georgejackson/Developer_Projects/Constraint_Engineering log --all -- '*QWERTY_CHECKPOINT*' '*ACTION_QUEUE*' → 0 commits, against `git rev-list --all --count` = 1161.
- git -C /Users/georgejackson/Developer_Projects/Project_Genesis log --all --diff-filter=A -- cw_handoff/QWERTY_CHECKPOINT.md → 1a7701d, 2026-03-06 00:17:02; last touch 01c1704, 2026-03-11 17:54:19; 15 commits titled 'qwerty: checkpoint for …'.
- Transcript scan (all .jsonl under ~/.claude/projects): QWERTY_CHECKPOINT earliest 2026-08-05T13:15:07.976Z (6142171c-….jsonl:10059), ACTION_QUEUE earliest 2026-07-22T00:01:13.205Z (6142171c-….jsonl:174); both latest 2026-09-09T12:24:17.877Z. 0 hits in the 196 .jsonl files of the -Constraint-Engineering project directory.
- a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:43916 (2026-09-08T15:18:38.578Z) and :45098 (2026-09-09T12:21:11.938Z) — the founder's 2 verbatim questions about both files.
- a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:44037 (2026-09-08T15:26:48.372Z) — the prior CC answer establishing 0 commits in CE but not identifying the owning project.

## simplicity-sufficiency-additive

**All 3 founder claims are supported by the record, with 1 material qualification: the chat happened (2026-08-18 to 2026-09-04), sufficiency is genuinely formalised in the maths and simplicity is defined in it as the re-injection term ν, but ν's implementation is a constant blind to complexity, the module that would measure it has no caller, and additivity appears 0 times in either maths file — it is a governance rule, not a model term.**

### Findings

## Direct answer

Yes — simplicity, sufficiency and additivity are 3 distinct properties in this project. They are not equally enforced, and they do not all live in the same place.

| Property | Precise definition as the project uses it | Where enforced |
|---|---|---|
| **Sufficiency** | Does the fix actually prevent the failure? A truth property. Formally: σ / S_k (fix efficacy) in the 3-phase risk update, and the §10 `sufficiency_round` predicate. | `docs/MATHEMATICAL_APPENDIX.md:214`, `:227`; `bench/directives/universal/cdsfl_core_formal.md:287-357`; live gate `check_sk_threshold_corrected` at `bench/reference_runner_v3.py:11055` |
| **Simplicity** | A property of the *solution*, not its ancestry — cost/blast-radius of the change. Formally: ν, the re-injection rate. | **Defined** at `docs/MATHEMATICAL_APPENDIX.md:215`. **Not measured** — see below. Explicitly classified non-formalisable at `bench/directives/universal/cdsfl_core_formal.md:604` |
| **Additivity** | Capability is preserved: never remove without a committed measurement; and symmetrically, an addition nothing reaches is not additive. | `Constraint_Engineering/.claude/CLAUDE.md:367`; panel SYSTEM prompt `bench/confer_maths_panel_2026-09-05.py:120`; `bench/tests/test_additive_standard_2026-09-07.py`. **0 occurrences in either maths file.** |

---

## (a) Was there "a whole considerable chat"? — SUPPORTED

It ran from 2026-08-18 to 2026-09-04, peaking on 2026-09-02. It is not one conversation but one arc, and the founder started it himself.

**Origin, 2026-08-18 13:09 BST** (`6142171c-....jsonl` L17355), verbatim: "the 'simplest sufficient fix', which has been a core guiding principle of this project since its inception. It is Occam's Razor put into practice ... It should also be a principle the models are guided by, and may even itself form an integral part of our overall mathematical model. (Although I can't recall if this is the case exactly.)"

**The separation demanded, 2026-08-19 07:30** (L17964), verbatim: "I don't feel you made enough of my suggestion of separating the principles of 'simple', from 'sufficient', in the principle of 'the simplest sufficient solution', and whether or not this can me mathematically formalised within the scope of our existing single unified mathematical equation. ... You said it was unnecessary to formalise it in the mathematical model, as it could be dealt with as the prompting/model level. But doesn't that fly in the face of almost everything this project is about too?"

**The canonical statement, 2026-08-23 08:31** (L21654), verbatim: "given our previous discussion that sufficiency and simplicity are not the same quantities, although they remain 2 sides to the same coin."

**Provenance, 2026-08-23 09:13** (L21819), verbatim: "The simplicity and sufficiency debate came out of a discussion with Gemini web, because it said the risk was that the models would always choose simplicity over sufficiency, leading to progressively weaker outcomes."

**The escalation, 2026-09-02 15:47** (`a07b3790-....jsonl` L22188), verbatim: "You need to learn the difference between 'simplicity' and 'sufficiency' that we have discussed extensively over the last month. They are not the same measures! Is it not the case that you are interpreting a requirement for you to provide 'the simplest sufficient fix' in your CLAUDE.md much too specifically and much too explicitly, without understanding/applying this distinction fully?"

**2026-09-02 17:48** (L22315), verbatim: "at base, which 'simplicity' and 'sufficiency' may be two sides to the same coin, that does not imply by definition that they are always the same thing."

**2026-09-02 18:00** (L22433), verbatim: "In essence the question can be defined as, are you preferring simplicity, over and above sufficiency? In engineering both these terms have very distinct separate, but related meanings? That is the question I asked you to put to the panel. I asked if the distinction was valid and how we should quantify and what lessons we should all learn going forward - and ultimately how we should apply them?"

**2026-09-02 18:18** (L22580), verbatim: "As I defined it, 'simplicity' occupies the same order as equations such as E=MC^2. Or the simplified version of our own unified equation. They are fundamentally simple, but comprehensible, but are nevertheless deeply powerful ... That is the kind of 'simplicity' we should am for, not you much 'simpler' kind. ... While these answers/equations are indeed simple, they are undeniably and demonstrably sufficient!"

**2026-09-04 21:48** (L24345), verbatim: "And both models and you have employed/deployed our recently discussed mathematical formalisations of 'simplicity' and 'sufficiency', both those you recently uncovered, and those you recently (re)discovered that already exist in our current mathematical model, in a fully tool verified format, in the formation of their investigations and all proposed fixes?"

The chat produced 2 committed notes, both dated 2026-09-02: `experimental_notes/Two_Parsimonies_2026-09-02.md` and `experimental_notes/Simplicity_Is_A_Constraint_Problem_2026-09-02.md`, plus a panel record `experimental_notes/Panel_Reduction_Criterion_FULL_RECORD_2026-09-03.md`.

**Qualification.** "Additive development" was a related but separate strand of the same Bugzilla arc, not part of the same conversation. The word "additive" occurs 0 times in both 2026-09-02 notes (verified by `grep -c`). The founder first tied additivity to this arc on 2026-08-20 23:04 (L18798), verbatim: "Clearly we want our solutions to be additive, so that that joint contributory element from the models (Or a human) is possible." It became a standing rule only on 2026-09-07 12:13 (L35849), verbatim: "So we have a standing rule that anything you and the other models do should be additive, in terms of adding to the reliability, functionality, accuracy, features, robustness, aims and objectives and overall specification of the project as a whole, never subtractive. ... is there no way to mechanically enforce this rule for both you and our other models going forward?"

---

## (b) Already embedded in the mathematical model? — HALF TRUE, and the untrue half is the important one

**What IS in the maths.**

The 3-phase extension of the unified equation carries both quantities as named parameters:
- σ (fix efficacy) — `docs/MATHEMATICAL_APPENDIX.md:214`: "Does the proposed fix actually resolve the detected flaw?" That is sufficiency.
- ν (re-injection rate) — `docs/MATHEMATICAL_APPENDIX.md:215`, verbatim: "**ν (re-injection rate):** Does the fix attempt introduce new flaws? Localised one-line changes have low ν. Changes to shared interfaces have higher ν." That is simplicity, defined as blast radius.

They are traded against each other by an explicit inequality — `docs/MATHEMATICAL_APPENDIX.md:237-243`: break-even ν* = σ·R·q / (1 − q·R·(1−σ)), with the hard exit "If ν > ν*, the cycle is net harmful — ΔR_cycle < 0. This is a hard exit condition: stop fixing and report the finding for human review."

Sufficiency is separately formalised as a predicate in the directives: `bench/directives/universal/cdsfl_core_formal.md:287` "## 10. Sufficiency Assessment and Convergence Declaration", with `sufficiency_round(k, artefact)` at `:322-330`. The Classification Summary at `:601` lists it as **Formalisable: Yes**.

So the founder is right that the machinery exists and that it was rediscovered rather than invented.

**What is NOT in the maths, measured.**

1. **The same table classifies simplicity as unformalised.** `bench/directives/universal/cdsfl_core_formal.md:604`, verbatim row: `| Simplicity default | Behavioural | No |`. And `:371-372` places it under "## Non-Formalisable Directives (Prose Only)": "**Default to the simplest sufficient solution.** Justified complexity is complexity the user cannot do without."

2. **ν is implemented as a constant, blind to complexity.** `bench/reference_runner_v3.py:9991` computes `nu_eff = 1.0 - (1.0 - nu_b) * (1.0 - (1.0 - sk) * nu_f)`. Its only free variables are `sk` and the 2 defaults `nu_b=0.05`, `nu_f=0.20` (signature at `:9927`). No size, file-count, or interface variable enters.

3. **Those constants are never overridden.** `bench/reference_runner_v3.py:10878-10879` reads `nu_b = meta.get("nu_b", 0.05)` from `entry.get("model_params", {})`. The runner's own comment at `:10887` states it: "what every run from Exp 37 to Exp 49 actually used, because model_params is never populated." Repo-wide grep for the literal `"nu_b"` as a written key finds it in exactly 1 place outside the reader — a test fixture, `bench/tests/test_ouroboros_loop_close.py:391`.

4. **The module built to fix this has no caller, 21 days after it was written.** `bench/dm/_fix_complexity.py`, docstring lines 1-17, verbatim: "The implementation does not measure any of that. ... whose only free variables are the fix's efficacy and two CONSTANTS. It depends on nothing about the fix: not its size, not how many places it touches, not whether it moves a shared interface. So the mathematics for 'the simplest sufficient solution' is already in the model and its input is a constant." and line 18: "This module supplies the missing measurement. It does NOT wire it into R_k." Grep confirms its only non-self references are `bench/tests/test_fix_complexity.py` and `scripts/instrument_inventory.py:69`, which catalogues it as "(shadow)". Its single commit is `ce6337a`.

5. **The formalisation the chat produced was never written into the appendix.** "Reduction Criterion" occurs 0 times in `docs/MATHEMATICAL_APPENDIX.md`. It stands as open Decision 3 in `experimental_notes/DECISIONS_AWAITING_YOU_2026-09-03.md:24-26`, verbatim: "DECISION 3. Whether to write the Reduction Criterion into the mathematical appendix. ... Recommendation. One definition in the appendix, one sentence in the acceptance policy, nothing else. No score, no weight, no new term in the model." It is still listed as awaiting a ruling at `experimental_notes/Morning_Report_REVISED_2026-09-05.md:24`.

6. **Additivity is not in the maths at all.** `grep -i "additive\|additivity"` over `docs/MATHEMATICAL_APPENDIX.md` and `bench/directives/universal/cdsfl_core_formal.md` returns 0 matches. It is a governance rule at `Constraint_Engineering/.claude/CLAUDE.md:365-371`, carried to panel seats by `bench/confer_maths_panel_2026-09-05.py:120` and guarded by `bench/tests/test_additive_standard_2026-09-07.py`.

7. **The 2026-09-02 note independently records the panel's ruling against putting simplicity into the gate.** `experimental_notes/Two_Parsimonies_2026-09-02.md`, verbatim: "parsimony belongs in the process, not as a scoring term in the convergence gate. Two panellists gave independent reasons. Any computable proxy for simplicity, such as diff size or token count, is open to being gamed by a model that has been told it is scored on it; and a parsimony term would let a run register convergence because proposed fixes got shorter, which is not the property the gate exists to certify."

**Net.** The correct statement is: sufficiency is embedded and live; simplicity is *defined* in the model but its input is a constant; additivity is not in the model. The founder's recollection is right about the existence of the machinery and wrong only in implying the embedding is complete. The gap he half-remembers is itself already on his own decision list as Decision 2 (`DECISIONS_AWAITING_YOU_2026-09-03.md:20-22`), verbatim: "The risk model reads its parameters from a field that no code anywhere writes to. Every experiment from number 37 to number 49 therefore ran on four literal defaults. The one module built to make the risk vary with the size of a fix has no caller. One reviewer described repairing the threshold while its inputs are constants as polishing the second decimal of a number that has no first one."

---

## (c) Does simplicity mean "prefer extending existing machinery"? — NO. The founder is right, and the bad framing is traceable to me, not to him.

**The framing exists and is mine.** `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/feedback_simplest_sufficient.md`, "How to apply" paragraph, verbatim: "Prefer extending machinery that exists and is already trusted over inventing a new component." That file's metadata records `modified: 2026-07-31T22:28:17.583Z`.

**The founder did not say that.** His actual words that day, 2026-07-31 22:27 (`6142171c-....jsonl` L6074), verbatim: "The reason my revised 'sweep' idea works is because it defaults to the simplest sufficient solution. A core principle of the project. You don't always have that instinct." Nothing about extending, incumbency or trust. The "prefer extending" clause is my gloss on his instance, not his rule.

**It then propagated.** `a07b3790-....jsonl` L35425 (2026-09-07 10:27, assistant), verbatim: "prefer extending trusted existing machinery over new components"; and L44958 (2026-09-09 10:28:52, assistant), verbatim: "**Simplest** — prefer extending machinery that already exists and is already trusted over inventing a component." That second one is what the founder is answering.

**The standing rules say the opposite.** `~/.claude/CLAUDE.md:139`, `selection-equivalence`, verbatim: "If multiple candidates satisfy all HARD constraints, prefer the most novel or elegant option." That is a preference *for* novelty among sufficient candidates, not for incumbency. Reinforced by `:38` `p-pass-divergence` (generate 2 to 4 distinct candidates before selecting) and `:46` `p-pass-wildcard` (keep 1 unconventional but valid candidate through at least 1 falsification cycle). The `simplicity-default` rule itself, `:11`, is silent on ancestry: "Default to the simplest sufficient solution, except when prose, graphics, or UX require richer expression to serve the task."

**The project's own note already stated the correct form.** `experimental_notes/Simplicity_Is_A_Constraint_Problem_2026-09-02.md`, verbatim: "sufficiency is a constraint and simplicity is an objective. The correct form is to minimise complexity subject to meeting every requirement. Preferring simplicity over sufficiency is the category error of converting the constraint into a penalty term and then trading it away." And: "the operating directive is not an instruction about size. It is an instruction about order. Establish the feasible set first, by checking coverage of every requirement; only then prefer the smallest member of it. ... Applied to fixes, sufficiency is the hard constraint and simplicity is the tie-breaker. The directive was never ambiguous; it was read as a size rule instead of an ordering rule."

That note also records that the *failure runs both ways*, which is exactly the founder's "keep building on worse solutions" worry stated as a measurement: "Under the opposite scalarisation, where total coverage is rewarded against a complexity cost, the over-complex candidate that fixes things nobody asked for wins for every cost weight below a threshold. ... Under-shoot and over-shoot are the same category error at different weights."

**Already conceded on the record.** `a07b3790-....jsonl` L45142 (2026-09-09 12:25, assistant), verbatim: "That collapses three separate properties into one and, as you say, it would tell a model never to innovate — and worse, to keep building on a bad foundation because it's the existing one."

---

## Typo note (standing directive)

In today's message the founder wrote "prefer exerting existing machinery" — he means "extending". On 2026-08-19 07:30 he wrote "whether or not this can me mathematically formalised" — "be". Neither changes the meaning.

### Does the record support the founder's framing?

SUPPORTS the founder on all 3 points, with 1 material correction to (b).

(a) SUPPORTED. The chat is real and documented: 2026-08-18 to 2026-09-04, with 4 founder messages on 2026-09-02 alone, 2 committed notes (`Two_Parsimonies_2026-09-02.md`, `Simplicity_Is_A_Constraint_Problem_2026-09-02.md`) and a panel record (`Panel_Reduction_Criterion_FULL_RECORD_2026-09-03.md`). Correction: additivity was a neighbouring strand of the same Bugzilla arc (first raised 2026-08-20 23:04, made a standing rule 2026-09-07 12:13), not part of the same conversation — "additive" appears 0 times in both 2026-09-02 notes. So there was a considerable chat about simplicity vs sufficiency; the 3-way distinction including additivity was never one chat.

(b) HALF SUPPORTED, and the founder's own decision list already records the other half. Sufficiency IS embedded: sigma/S_k at MATHEMATICAL_APPENDIX.md:214, the section-10 predicate at cdsfl_core_formal.md:287-357, and a live gate at reference_runner_v3.py:10934. Simplicity IS defined in the maths — nu at MATHEMATICAL_APPENDIX.md:215, "Localised one-line changes have low nu. Changes to shared interfaces have higher nu" — and traded against sufficiency by the break-even inequality at :237-243. But the implementation refutes "embedded": nu_eff at reference_runner_v3.py:9991 has no complexity variable, its 2 constants are never overridden (the runner's own comment at :10887 says model_params is never populated), and `bench/dm/_fix_complexity.py` — written to supply the measurement — has 0 callers, its docstring stating "It does NOT wire it into R_k". The formalisation the chat produced (the Reduction Criterion) was never written into the appendix; it stands as open Decision 3. Additivity is in neither maths file (0 grep matches). And cdsfl_core_formal.md:604 explicitly classifies "Simplicity default" as Behavioural, Formalisable: No — which contradicts the strong reading of the founder's claim while confirming his 2026-08-19 complaint that it was deferred to the prompt level rather than formalised.

(c) SUPPORTED, and the source is identifiable. "Prefer extending machinery that exists and is already trusted over inventing a new component" is CC1's sentence, in `memory/feedback_simplest_sufficient.md` (modified 2026-07-31T22:28:17Z), not the founder's. His words that day were only "it defaults to the simplest sufficient solution". The standing rules point the other way: `~/.claude/CLAUDE.md:139` prefers "the most novel or elegant option" among candidates that satisfy all HARD constraints, and :38/:46 require 2 to 4 distinct candidates plus 1 wildcard. The project's own 2026-09-02 note already framed it correctly as an ordering rule, not a size or ancestry rule, and measured the over-shoot failure alongside the under-shoot one. The founder's specific worry — that the framing tells models to keep building on worse solutions — is exactly what the note calls the reverse scalarisation error.

### Recommendation (not implemented)

Do not implement anything. 5 items, in this order.

1. Correct the propagation source. `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/feedback_simplest_sufficient.md` carries the sentence "Prefer extending machinery that exists and is already trusted over inventing a new component." That single line is what reappeared on 2026-09-07 and 2026-09-09. Replace it with the ordering form the project already derived and committed: sufficiency is the HARD constraint, simplicity is the tie-breaker among candidates that clear it, and reuse is an outcome, never a rule. Leave the rest of that note intact — its analysis of the 2026-07-31 instance is sound and the "5 refutations mean the question is wrong" clause still holds.

2. Add the 3-axis definition where the additive standard already lives, so it reaches the panel by the same route rather than as a new mechanism: `Constraint_Engineering/.claude/CLAUDE.md` alongside :367, and the SYSTEM prompt at `bench/confer_maths_panel_2026-09-05.py:120`. Simplicity = fewest moving parts in the solution, independent of ancestry. Sufficiency = prevents the named failure. Additivity = capability preserved, in both directions. Extend the existing `bench/tests/test_additive_standard_2026-09-07.py` assertion set rather than adding a second test file.

3. Rule Decision 2 (`experimental_notes/DECISIONS_AWAITING_YOU_2026-09-03.md:20-22`). This is the item that would make claim (b) true rather than half true: wire `bench/dm/_fix_complexity.py` so nu stops being a constant. Both reviewers converged on doing this BEFORE repairing the threshold. Note the module's own caution — it returns a percentile rank, not a probability, and it is hidden from the generating model for anti-gaming reasons; that is a reporting-accuracy design, not an enforcement one, and promoting it changes which fixes are SK_REJECTED and therefore invalidates replay against the existing archive.

4. Rule Decision 3 (`:24-26`): the Reduction Criterion into the appendix as 1 definition plus 1 sentence in the acceptance policy. Both reviewers said add no machinery.

5. Do NOT add a parsimony scoring term to the convergence gate. Both the 2026-08-18 panel and `experimental_notes/Two_Parsimonies_2026-09-02.md` rejected it on 2 independent grounds: any computable simplicity proxy is gameable by a model told it is scored on it, and a parsimony term would let a run register convergence because fixes got shorter, which is not what the gate certifies.

### What could not be established

3 things I could not establish.

1. I did not execute `bench/tests/test_additive_standard_2026-09-07.py`, so I cannot report whether it currently passes. Its `_system_prompt_value` helper at lines 101-102 writes a probe file into `bench/logs/_additive_standard_probe/`, and the task set an absolute read-only constraint. What I did verify by reading: the file exists (12,025 bytes, 2026-09-08), it holds 8 assertions across 3 layers, and the SYSTEM-prompt strings it asserts on ("ADDITIVE STANDARD", "COMMITTED MEASUREMENT", "NEVER DISABLE OR REMOVE A FEATURE", "NOTHING REACHES") are all present at `bench/confer_maths_panel_2026-09-05.py:120`. The parent agent should run it before relying on green status.

2. I could not locate a single conversation covering all 3 properties together. The arc is real and continuous, but simplicity-vs-sufficiency (2026-08-18 to 2026-09-04) and additivity (2026-08-20, then 2026-09-07) are 2 strands. If the founder is recalling one integrated discussion, it may be the Gemini web conversation he names on 2026-08-23 09:13 as the origin of the debate — that is outside these transcript files and I cannot see it.

3. The 6 transcript files cover 2026-07-27 onward. The founder's 2026-08-23 reference to "our previous discussion" resolves to 2026-08-18 and 2026-08-19 within this window, and I found no earlier in-transcript statement of the distinction. That is consistent with his own account of its origin, but I cannot rule out an earlier discussion in a session whose transcript is not in this directory.

### Evidence

- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89.jsonl:17355 — 2026-08-18T13:09:26Z, founder opens the arc: 'the simplest sufficient fix ... It is Occam's Razor put into practice ... may even itself form an integral part of our overall mathematical model. (Although I can't recall if this is the case exactly.)'
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89.jsonl:17964 — 2026-08-19T07:30:56Z, founder demands the separation be mathematically formalised and objects that CC1 deferred it to the prompt level
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89.jsonl:18798 — 2026-08-20T23:04:30Z, first 'additive' in the same Bugzilla arc
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89.jsonl:21654 — 2026-08-23T08:31:18Z, canonical statement: 'sufficiency and simplicity are not the same quantities, although they remain 2 sides to the same coin'
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89.jsonl:21819 — 2026-08-23T09:13:23Z, provenance: the debate came from a Gemini web discussion about models always choosing simplicity over sufficiency
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89.jsonl:6074 — 2026-07-31T22:27:40Z, founder's actual words on the sweep instance; contains no 'prefer extending' clause
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:22188 — 2026-09-02T15:47:34Z, 'They are not the same measures!'
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:22315 — 2026-09-02T17:48:39Z, 'two sides to the same coin ... does not imply by definition that they are always the same thing'
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:22433 — 2026-09-02T18:00:05Z, the 4-part brief the founder says was narrowed
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:22580 — 2026-09-02T18:18:41Z, the E=MC^2 definition of the simplicity he wants
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:24345 — 2026-09-04T21:48:14Z, 'those you recently (re)discovered that already exist in our current mathematical model'
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:35849 — 2026-09-07T12:13:06Z, the additive standing rule stated and the request to enforce it mechanically
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:44958 — 2026-09-09T10:28:52Z, CC1 writes 'prefer extending machinery that already exists and is already trusted' — the formulation being rebuked
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:45098 — 2026-09-09T12:21:11Z, the founder's rebuke verbatim (contains the typo 'exerting' for 'extending')
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:45142 — 2026-09-09T12:25:00Z, CC1's concession that the 3 are separate axes
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/docs/MATHEMATICAL_APPENDIX.md:214-215 — sigma defined as fix efficacy (sufficiency); nu defined as complexity/blast radius (simplicity)
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/docs/MATHEMATICAL_APPENDIX.md:237-243 — break-even nu* inequality and the hard exit 'If nu > nu*, the cycle is net harmful'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/docs/MATHEMATICAL_APPENDIX.md:205 — the (1-R_k) diminishing-returns factor and the stopping rule
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/docs/MATHEMATICAL_APPENDIX.md — grep for 'additive|additivity' returns 0 matches; grep for 'parsimon|occam' returns 0 matches; 'Reduction Criterion' returns 0 matches
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md:287-357 — section 10, Sufficiency Assessment, with the sufficiency_round predicate at :322
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md:601 — 'Sufficiency assessment & convergence declaration (section 10) | ... | Yes'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md:604 — '| Simplicity default | Behavioural | No |'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md:362-372 — simplicity placed under 'Non-Formalisable Directives (Prose Only)'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v3.py:9991-9992 — nu_eff depends only on sk, nu_b, nu_f; no complexity variable appears
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v3.py:10878-10887 — nu_b/nu_f read from model_params with the runner's own comment 'because model_params is never populated'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v3.py:10527-10560 — sk_break_even, the true Valley floor, keyword-only since 2026-09-07; live caller at :10934
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/dm/_fix_complexity.py:1-18 — 'the mathematics for the simplest sufficient solution is already in the model and its input is a constant' / 'It does NOT wire it into R_k'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/instrument_inventory.py:69 — the only non-test reference to fix_complexity_features, catalogued as '(shadow)'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Two_Parsimonies_2026-09-02.md — maintenance parsimony vs epistemic parsimony; 'parsimony belongs in the process, not as a scoring term in the convergence gate'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Simplicity_Is_A_Constraint_Problem_2026-09-02.md — 'sufficiency is a constraint and simplicity is an objective'; 'an instruction about order', not size
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/DECISIONS_AWAITING_YOU_2026-09-03.md:20-26 — Decision 2 (nu's inputs are constants, module has no caller) and Decision 3 (Reduction Criterion into the appendix), both open
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Morning_Report_REVISED_2026-09-05.md:24 — 'Reduction Criterion placement' still listed as awaiting a ruling
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/memory/feedback_simplest_sufficient.md — source of 'Prefer extending machinery that exists and is already trusted over inventing a new component'; modified 2026-07-31T22:28:17.583Z
- /Users/georgejackson/.claude/CLAUDE.md:11 — simplicity-default, silent on ancestry
- /Users/georgejackson/.claude/CLAUDE.md:139 — selection-equivalence: 'prefer the most novel or elegant option' among candidates satisfying all HARD constraints
- /Users/georgejackson/.claude/CLAUDE.md:38,46 — p-pass-divergence (2 to 4 distinct candidates) and p-pass-wildcard (keep 1 unconventional candidate)
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/.claude/CLAUDE.md:365-371 — the additive standard, its measured justification (11 unwired additions, 0 needed removals, Wilson [74.1%, 100.0%]) and its named enforcement points
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:120 — the ADDITIVE STANDARD paragraph in the panel SYSTEM prompt, verified present by grep
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_additive_standard_2026-09-07.py:120-227 — 8 assertions across 3 layers; NOT executed under the read-only constraint (the SYSTEM-prompt probe at :101-102 writes a file)

## reliability-mechanism

**The mechanism was discussed at least 5 times between 2026-08-25 and 2026-09-09 and was never built: all 4 installed hooks are UserPromptSubmit context injectors that make 0 subprocess calls, emit 0 blocking decisions and always exit 0, there is no git hook (14 files in .git/hooks, all .sample), no CI, and no core.hooksPath — so nothing whatsoever checks repository state before a commit, and commit 57d5a0e reached HEAD on 2026-09-09 at 08:16:17 with the suite red.**

### Findings

## (a) What was discussed, and when

**The immediate referent.** The founder's phrase "This mechanism you speak of" points at the assistant's own message of 2026-09-09T10:55:59Z, `a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:45094`, verbatim: "Recording a remedy is not applying it — and that is an argument for a mechanism rather than discipline, which is a question for you rather than something I should decide alone."

That is the only occurrence of that framing in 6,719 assistant text messages across all 6 transcripts. I also searched the 8 compaction summaries separately for `mechanism (rather than|not) discipline|reliability (fix )?mechanism|stop (you|me) (screwing|repeating)|pre-commit hook`: 0 matches. So there is no earlier proposal hidden in a compacted portion.

**The founder's question, verbatim** (`a07b3790…jsonl:45098`, 2026-09-09T12:21:11.938Z): "This mechanism you speak of to stop you screwing up so much? We already spoke about this too? Did you implement it? If not you probably should add this to the top of your work list and add the remote connection to the bottom."

**"We already spoke about this too" is correct.** Four prior occasions, all verbatim from the founder:

1. 2026-08-25T08:31:48.550Z, `a07b3790…jsonl:1724` — "Write the hook, with the elapsed time since last message. Might as well fix this conclusively." → produced `~/.claude/hooks/prompt_clock.py`.
2. 2026-08-30T20:10:27.437Z, `a07b3790…jsonl:11925` — "given that you have not always been entirely reliable, you should probably (once again) conduct a full inventory of all of the fixes and actions that were agreed today… It is probably not the first time I have asked you to do this, but nor is it the first time you have assured me it has all been done, only to come back soon afterwards and admit that xyz items have been skipped, 'because you didn't look properly'. This is becoming a bit of a theme."
3. 2026-08-31T23:33:14.539Z, `a07b3790…jsonl:15295` — "So why not add this as an absolute programmatic habit and requirement for this facility, rather than a preference?" → produced the one-line-rule refusal in sv (`scripts/cdsfl_sv.py:1716-1737`, comment dated 2026-09-01).
4. 2026-09-04T22:08:20.203Z, `a07b3790…jsonl:24462` — "Otherwise are you certain that the alerts you built here to this effect are likely to prove effective? You won't have to remember to run them? Because post-compaction you might not." → produced `~/.claude/hooks/compaction_watch.py`.
5. 2026-09-07T12:13:06.445Z, `a07b3790…jsonl:35849` — "is there no way to mechanically enforce this rule for both you and our other models going forward ?" → produced `bench/tests/test_additive_standard_2026-09-07.py`.

So the founder has raised the mechanism-not-discipline question 5 times. Each time it was answered NARROWLY, for the one rule in front of it. It has never been answered for the class.

## (b) What exists, and what it enforces

**Every hook, its trigger, and what it checks — the complete list.** `~/.claude/settings.json:17-40` contains exactly one hook key, `UserPromptSubmit`, with 4 commands:

| file | trigger | what it checks |
|---|---|---|
| `~/.claude/hooks/prompt_clock.py` | UserPromptSubmit | Nothing. Injects wall-clock time and the gap since the previous prompt (`:61-71`). |
| `~/.claude/hooks/mc_commands.py` | UserPromptSubmit | Nothing. Parses the prompt's trailing lines for MC tokens and injects each one's obligation, plus the standing `f`/`sy` pair on every turn (`:139-169`). |
| `~/.claude/hooks/compaction_watch.py` | UserPromptSubmit | The session TRANSCRIPT only — seeks a stored byte offset for `"isCompactSummary": true` and injects a notice until `rs` runs (`:119-238`). |
| `~/.claude/hooks/ffafp_audit.py` | UserPromptSubmit | The session TRANSCRIPT only — reports which observable FFAFP traces the previous work turn did not leave (`:705-793`). |

**None of them touches the repository, and none of them can block.** Executed checks:
- `grep -n "subprocess\|os.system\|check_output\|Popen\|Constraint_Engineering" *.py` across all 4 hooks → **0 matches**. No hook runs pytest, git, a linter, or anything else.
- `grep -n '"decision"\|permissionDecision\|exit(2)\|sys.exit(1)\|sys.exit(2)' *.py` → **0 matches**. Every hook ends `sys.exit(0)` (`prompt_clock.py:78`, `mc_commands.py:177`, `compaction_watch.py:238`, `ffafp_audit.py:797`).
- `ffafp_audit.py:87-91` states this by design: "REPORT, NEVER BLOCK… Exit status is always 0 and no `decision` field is ever emitted."

**There is no hook of any other kind.** `grep -n "PostToolUse\|SessionEnd\|\"Stop\"\|PreToolUse\|PreCompact\|SessionStart"` across `~/.claude/settings.json`, `~/.claude/settings.local.json` and `Constraint_Engineering/.claude/settings.json` → exit 1, **0 matches**.

**Project level holds nothing.** `Constraint_Engineering/.claude/` contains exactly 2 files: `CLAUDE.md` (36,154 bytes) and `settings.json` (535 bytes, a `permissions.allow` list only — no `hooks` key). `.claude/CLAUDE.md:363` documents `compaction_watch.py` but installs nothing.

**No git-side gate at all.** `Constraint_Engineering/.git/hooks/` holds 14 files and every one ends `.sample`. `git config --get core.hooksPath` → exit 1 (unset). No `.github/workflows/`, no `Makefile`, no `.pre-commit-config.yaml`, no `tox.ini`.

**Does sv refuse when a check fails? Yes — but only 4 checks, only on `--commit`, and it never runs the suite.**
- `scripts/cdsfl_sv.py:2478-2492`: the pre-flight runs only `if args.check_save or (args.commit and not args.dry_run)`. On failure, `:2491` `sys.exit(0 if complete else 1)` for `--check-save`, and `:2492` `if not complete and not args.allow_incomplete_save: sys.exit(1)`. So it genuinely refuses; `--allow-incomplete-save` (`:1348`) downgrades to warnings.
- The check list is `:2386-2393`, exactly 4: `_check_memory_updated`, `_check_open_brain`, `_reconcile_tracker`, `_check_memory_index_size`.
- The memory-index audit finds orphans and broken links but **cannot refuse on them**. `:1625` docstring: "Print the RULING 7 reports. These inform; only size can refuse." `:1680`: "The one RULING 7 check that can refuse a save."
- **sv never runs the test suite.** `scripts/cdsfl_utils.py:124-142` `test_count()` runs `pytest bench/tests/ --co -q` — collection only. `scripts/cdsfl_sv.py:253-255` says so explicitly: "Do NOT write 'tests pass' here: `tests` comes from `pytest --co`, which is a collection count and carries no pass/fail information."
- sv DOES re-derive the ledger, at `:2565-2570`, calling `_update_memory_exclusions_ledger`. That is the whole remedy — and it only fires if sv is run.

## The 2026-09-08 breakage, reconstructed from timestamps

- The 139th memory file was created 2026-09-08T18:43:56+0100 (`stat` on `…/memory/env_desktop_app_auto_restart_kills_remote_sessions.md`, mtime = birth).
- Commit `01906cc` landed 2026-09-08T18:43:25+0100 — **31 seconds before that file existed**, so it was clean.
- Commit **`57d5a0e` landed 2026-09-09T08:16:17+0100 carrying `| total | 138 |`** (`git show 57d5a0e:resources/MEMORY_EXCLUSIONS.md`, line 26) against 139 files on disk. That is the commit that reached HEAD on a red suite, 13h32m after the drift opened.
- Repaired at `9e3dfe9`, 2026-09-09T11:55:45+0100, ledger now `| total | 139 |`, stamp "counted 2026-09-09 11:41 BST".
- The lesson the assistant had already recorded sits at `experimental_notes/CDSFL_Agent_Operational_Plan.md:124`, verbatim: "The drift exists because the guard ran before `sv` did. **No mechanism is missing; the remedy is ordering.**"

**The guards were never missing — nothing ran them.** All 4 failing tests already existed and are already mutation-verified (commit `9e3dfe9`: "restoring the over-long entry takes 2 tests red, setting the ledger total wrong takes 1 red"):
- `bench/tests/test_documentation_drift_guards_2026-08-25.py:188`
- `bench/tests/test_recovery_memory_doc_repairs.py:282`
- `bench/tests/test_memory_index_limits_match_the_loader_2026-09-01.py:195`
- `bench/tests/test_line_citations_resolve_2026-09-01.py:134`

`test_documentation_drift_guards_2026-08-25.py:189-196` even records the recurrence rate: the derive-don't-type remedy "has needed the same manual correction SEVEN consecutive times, twice in a single session on 2026-08-24."

**No reliability-mechanism task is queued anywhere.** `grep -n "mechanically enforce\|mechanism rather than\|reliability mechanism"` across `experimental_notes/CDSFL_Agent_Operational_Plan.md`, `resources/RECOVERY.md` and `.claude/CLAUDE.md` → 0 matches. It was never written down as work.

One related artefact exists but is not a mechanism: `scripts/who_catches_the_defects_2026-09-09.py`, untracked (`git status --short` shows `?? scripts/who_catches_the_defects_2026-09-09.py`), written today by the assistant to classify 19 caught defects by catcher. It has no test and no caller.

## (c) The smallest sufficient design — NOT implemented

**A versioned `pre-commit` git hook that runs the 4 guard files that already exist, and refuses the commit on non-zero pytest exit.**

I executed those 4 files to size it: **28 tests, 1.26 s** (`python3 -m pytest -p no:cacheprovider -q --netguard-strict` over the 4 paths, single run, 28 passed). Against the full suite's 669.92 s recorded in `9e3dfe9`, that is 0.19% of the cost. A gate costing 1.26 s does not get switched off; one costing 670 s does.

It adds no checker. All 4 guards exist, are in the suite, and are mutation-verified. The only new thing is the moment they fire.

Falsification of the alternatives:
- **A 5th sv pre-flight check would not have caught it.** `57d5a0e`'s subject is "Morning report: 12 outstanding items verified…", not `sv:` — and `sv:` is the exact marker `_previous_sv_commit` keys on (`scripts/cdsfl_sv.py:1770-1789`). sv's pre-flight never ran for that commit because sv was not the commit path.
- **A UserPromptSubmit hook cannot catch it.** It fires before the turn, sees no repository state, makes 0 subprocess calls by construction, and exits 0 unconditionally in all 4 existing instances.
- **Running the full suite pre-commit is not the simplest sufficient form.** 669.92 s per commit invites `--no-verify` as routine.

Wiring it must satisfy the additive standard in both directions — "every new flag, gate, subcommand or entry point must be wired to a caller and executed by a test":
1. The hook lives in the repo's existing `hooks/` directory (which already holds `mc_commands.py`) and is reached by `git config core.hooksPath hooks`. That is local config and currently unset, so `scripts/cdsfl_onboard.py` must set it, or the hook is an addition nothing reaches.
2. A test must EXECUTE the hook, not grep it (`execute-do-not-grep`): plant a wrong ledger total in a temp tree, run the hook, assert non-zero exit and the guard's name in stderr; restore, assert zero. Mutation-verified in both directions.
3. `git commit --no-verify` remains an override, and should be recorded as one — the same honest status `--allow-incomplete-save` has.

Stated limits: it catches only these 4 guards. The p-value error, the scan-scope error and the timestamp error from the same 48 hours are all invisible to it. The memory directory is outside the repo, so drift can open with no repo change at all — the hook bounds the exposure to "not in a commit", which is exactly what was asked and no more. 1.26 s is one measurement on a warm filesystem.

### Does the record support the founder's framing?

SUPPORTS the founder, on both halves he asserted.

"We already spoke about this too?" — SUPPORTED, 5 times: 2026-08-25 (`a07b3790…jsonl:1724`), 2026-08-30 (`:11925`), 2026-08-31 (`:15295`), 2026-09-04 (`:24462`), 2026-09-07 (`:35849`), plus the assistant's own 2026-09-09 statement at `:45094` that this is "an argument for a mechanism rather than discipline".

"Did you implement it?" — NO, for the class he means. Each earlier conversation produced a narrow answer for the one rule in front of it: a clock hook, an MC-obligation hook, an sv one-line refusal, a compaction watcher, an additive-standard test. Every one of those is either a context injector that cannot refuse anything, or a check bound to a script that must be voluntarily invoked. Nothing in the estate inspects repository state before a commit. `git config --get core.hooksPath` is unset, `.git/hooks/` holds 14 `.sample` files and nothing else, there is no CI, and `cdsfl_sv.py` collects tests without ever running them.

The prompt's framing — "records a lesson and then breaks it" — is also SUPPORTED, and the record is sharper than the framing. `test_documentation_drift_guards_2026-08-25.py:189-196` records that this exact remedy "has needed the same manual correction SEVEN consecutive times, twice in a single session on 2026-08-24", which makes 2026-09-08 at least the 8th instance, not the first relapse.

One correction to a possible reading of the framing: the founder was never told a mechanism was built and then found it absent. Searching the transcripts, the assistant has never claimed to have built one. The failure is omission, not misreport.

### Recommendation (not implemented)

Do not build a new checker. Build the one missing moment.

Add a versioned `pre-commit` git hook under the repo's existing `hooks/` directory that runs exactly these 4 already-mutation-verified files and refuses the commit on non-zero pytest exit:

  bench/tests/test_documentation_drift_guards_2026-08-25.py
  bench/tests/test_recovery_memory_doc_repairs.py
  bench/tests/test_memory_index_limits_match_the_loader_2026-09-01.py
  bench/tests/test_line_citations_resolve_2026-09-01.py

Measured cost: 28 tests, 1.26 s, against 669.92 s for the full suite. That is what makes it survivable as a per-commit gate; the full suite would be bypassed within a day.

Three wiring conditions, without which it is itself an unwired addition:
1. `git config core.hooksPath hooks` must be set by `scripts/cdsfl_onboard.py`, since it is local config and is currently unset.
2. A test must EXECUTE the hook against a temporary tree with a planted wrong ledger total, assert non-zero exit and the guard name in stderr, then restore and assert zero — mutation-verified in both directions, per `execute-do-not-grep`.
3. `git commit --no-verify` should be documented as the override, the same honest status `--allow-incomplete-save` already carries.

Reject the two obvious alternatives on evidence: a 5th sv pre-flight check would not have caught `57d5a0e`, because that commit did not go through sv (its subject is not `sv:`, the marker `_previous_sv_commit` keys on at cdsfl_sv.py:1770); and no UserPromptSubmit hook can catch it, because all 4 existing ones make 0 subprocess calls, see no repository state, and exit 0 unconditionally by design.

Separately, and cheaply: the founder's 2026-09-09 message asks for the work list to be written "somewhere you can find and refer back to it after each task completes" with a Desktop copy. The tracker already has that shape and the reliability item is absent from it — grep for "mechanically enforce|mechanism rather than|reliability mechanism" across the tracker, RECOVERY.md and .claude/CLAUDE.md returns 0 matches. Queue it there first, before building anything.

DO NOT IMPLEMENT — this is a read-only finding, and the design above is for the founder's ruling.

### What could not be established

Three things I could not establish.

1. Whether the founder ever explicitly APPROVED building a general reliability mechanism, as opposed to asking about one. The nearest is 2026-09-07's "is there no way to mechanically enforce this rule", which was scoped to the additive standard and answered as such. The 2026-09-09 message is the first time it is placed at the top of the work list. I found no approval message in between.

2. Whether "this mechanism you speak of" might refer to something said in a portion of the record I cannot see. I searched 1,067 user messages and 6,719 assistant text messages across all 6 transcripts, and separately searched the 8 compaction summaries; the only match for the framing is the 2026-09-09T10:55:59Z assistant message. If the conversation happened outside these transcripts — in a Fable or CC2 session, or verbally — it is not in this record.

3. The 1.26 s figure is a single run on a warm filesystem, and 2 of the 4 guard files read the live memory directory, whose size will grow. I did not repeat the measurement or bound its variance. Treat it as an order of magnitude, not a specification.

One thing worth naming that is not uncertainty but a limit of the proposal: a pre-commit gate on these 4 files would have caught the 2026-09-08 memory-ledger breakage and nothing else from the same 48 hours. The anti-conservative p-value, the bounded scan scope and the 607-minute timestamp error are all outside its reach.

### Evidence

- /Users/georgejackson/.claude/settings.json:17-40 — the entire `hooks` block; the only key is `UserPromptSubmit`, listing 4 commands. No PostToolUse, Stop, SessionEnd, PreToolUse, PreCompact or SessionStart anywhere.
- /Users/georgejackson/.claude/hooks/prompt_clock.py:61-78 — builds a `[clock]` string and prints `additionalContext`; exits 0.
- /Users/georgejackson/.claude/hooks/mc_commands.py:139-177 — injects MC obligations plus the standing f/sy pair; exits 0.
- /Users/georgejackson/.claude/hooks/compaction_watch.py:119-238 — scans the session JSONL for `isCompactSummary`; exits 0.
- /Users/georgejackson/.claude/hooks/ffafp_audit.py:87-91 — "REPORT, NEVER BLOCK … Exit status is always 0 and no `decision` field is ever emitted."
- /Users/georgejackson/.claude/hooks/ffafp_audit.py:797 — sys.exit(0). Executed grep for subprocess/Popen/os.system across all 4 hooks returned 0 matches; grep for `"decision"`/exit(1)/exit(2) returned 0 matches.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/.git/hooks/ — 14 files, every one ends `.sample`. `git config --get core.hooksPath` exits 1 (unset). No .github/workflows, no Makefile, no .pre-commit-config.yaml.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/.claude/settings.json — a `permissions.allow` list only; no `hooks` key. The directory holds just CLAUDE.md and settings.json.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/cdsfl_sv.py:2478-2492 — pre-flight runs only on --check-save or (--commit and not --dry-run); refuses via sys.exit(1) unless --allow-incomplete-save.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/cdsfl_sv.py:2386-2393 — the complete check list: memory-updated, open-brain, tracker-reconcile, memory-index-size. Four checks, no suite run.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/cdsfl_sv.py:1625 — "Print the RULING 7 reports. These inform; only size can refuse." Orphans and broken index links are reported and cannot refuse.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/cdsfl_sv.py:253-255 — "Do NOT write 'tests pass' here: `tests` comes from `pytest --co`, which is a collection count and carries no pass/fail information."
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/cdsfl_utils.py:124-142 — test_count() runs `pytest bench/tests/ --co -q`; collection only, never a pass/fail run.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/scripts/cdsfl_sv.py:2565-2570 — _update_memory_exclusions_ledger, the derive-don't-type remedy; reached only when sv runs.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:124 — "The drift exists because the guard ran before `sv` did. No mechanism is missing; the remedy is ordering."
- git show 57d5a0e:resources/MEMORY_EXCLUSIONS.md line 26 = `| total | 138 |`; commit time 2026-09-09T08:16:17+01:00. At 9e3dfe9 (2026-09-09T11:55:45+01:00) the same line reads `| total | 139 |`.
- stat on /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/memory/env_desktop_app_auto_restart_kills_remote_sessions.md — mtime and birth both 2026-09-08T18:43:56+0100; commit 01906cc is 2026-09-08T18:43:25+0100, 31 s earlier.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_documentation_drift_guards_2026-08-25.py:188-206 — the ledger guard, and at :189-196 the record that the remedy "has needed the same manual correction SEVEN consecutive times, twice in a single session on 2026-08-24."
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_recovery_memory_doc_repairs.py:282, bench/tests/test_memory_index_limits_match_the_loader_2026-09-01.py:195, bench/tests/test_line_citations_resolve_2026-09-01.py:134 — the other 3 guards that went red.
- Executed: `python3 -m pytest -p no:cacheprovider -q --netguard-strict` over those 4 files → "28 passed in 1.26s". Compare 669.92 s for the full suite, quoted in commit 9e3dfe9.
- Transcript a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:45094, 2026-09-09T10:55:59.839Z — the assistant's "an argument for a mechanism rather than discipline"; sole occurrence across 6,719 assistant text messages, and 0 occurrences in the compaction summaries.
- Transcript a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:35849, 2026-09-07T12:13:06.445Z — founder: "is there no way to mechanically enforce this rule for both you and our other models going forward ?"
- Transcript a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:15295, 2026-08-31T23:33:14.539Z — founder: "So why not add this as an absolute programmatic habit and requirement for this facility, rather than a preference?"
- Transcript a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:11925, 2026-08-30T20:10:27.437Z — founder: "nor is it the first time you have assured me it has all been done, only to come back soon afterwards and admit that xyz items have been skipped … This is becoming a bit of a theme."
- Transcript a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl:24462, 2026-09-04T22:08:20.203Z — founder: "You won't have to remember to run them? Because post-compaction you might not."
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_additive_standard_2026-09-07.py:1-31 — the one prior 'mechanically enforce' request that WAS built, narrow to the additive standard; its own docstring records that the rule "was itself an addition wired to nothing."
- grep for "mechanically enforce|mechanism rather than|reliability mechanism" across experimental_notes/CDSFL_Agent_Operational_Plan.md, resources/RECOVERY.md and .claude/CLAUDE.md → 0 matches. The task was never queued.
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/hooks/ — holds only mc_commands.py, byte-identical to the live copy. prompt_clock.py, compaction_watch.py and ffafp_audit.py are NOT versioned in the repo.

## panel-review-format

**Half the format exists and is test-guarded — the SYSTEM prompt, which carries the 28,183-character formal schema plus 4 panel rules; the other half does not exist as a format at all, because the USER prompt is a hand-written BRIEF.md read off disk, and across all 49 archived briefs 0 require a seat to use the mathematical model as an instrument, 8 require a fix, and 2 require the fix to be tested.**

### Findings

## 1. What `bench/confer_maths_panel_2026-09-05.py` actually sends a seat

**The dispatcher composes only the SYSTEM half. The USER half it reads off disk.**

`bench/confer_maths_panel_2026-09-05.py:53-58`:
```
LOGS = _REPO / "bench" / "logs" / sys.argv[1]
BRIEF = LOGS / "BRIEF.md"
if not BRIEF.is_file(): ... raise SystemExit(2)
PROMPT = BRIEF.read_text(encoding="utf-8")
```
There is no template, no construction, no schema and no validation. Whatever markdown is in `BRIEF.md` is the entire user prompt. This is the single most important fact for the founder's ruling: the thing he is asking to be standardised is the half that has no standard.

### The SYSTEM prompt (lines 98-134), in order

1. `_SCHEMA` — the whole of `bench/directives/universal/cdsfl_core_formal.md`, read at lines 95-96. Measured with `wc -c`: **28,183 characters**. Its sections: 1 Constraint Classification, 2 Constraint Precedence, 3 Falsification Loop (P-Pass), 4 Proportionality Gate, 5 Corroboration Model, 6 Extended P-Pass (DAG), 7 Falsification Survival Predicate, 8 Epistemic Marking, 9 Proactive Verification, 10 Sufficiency Assessment and Convergence Declaration, plus Non-Formalisable Directives, Objective and Diminishing Returns, Runnable Falsifiers for Critical Findings, Falsifier Integrity, Classification Summary.
2. Panel identity, and "Biological component names are ANALOGY ONLY -- module names, not biology."
3. "CDSFL's founding principle is TOOLS DECIDE, NOT VOTES. A finding is confirmed when a tool independently re-executes a falsifier, never by model agreement. ... Where you assert a mathematical result, DERIVE it."
4. "NO COMPELLED CONVERGENCE. Return YOUR verdict and YOUR strongest falsification. Do not attempt to agree with the other seats. Disagreement is preserved as information."
5. "You are expected to declare the reasoning SOUND where it is. This panel is not scored on finding faults, and a clean verdict backed by derivation is as useful as a refutation."
6. "Do not pad. Every word is read."
7. THE ADDITIVE STANDARD, line 120, in full.
8. THIS IS A ONE-SHOT DISPATCH, lines 126-133 — no later turn, do not run the full suite, write findings so far.

The file's own comment at lines 93-94 says the seat prompt goes "from ~3.0K to ~31.2K characters, about 7,800 tokens". I did not independently measure the composed total: importing the module writes a probe directory under `bench/logs`, which the read-only constraint forbids. The 28,183 figure is measured; the 31.2K is the file's claim.

### What schema the seat is asked to RETURN: none.

The SYSTEM prompt asks for a verdict and a strongest falsification, in prose. `bench/cdsfl_finding_schema.json` exists and defines the structured shape — `finding_id`, `type` (NOVEL/VALIDATION/CHALLENGE), `severity` 0.0-1.0, `flaw_class` 1-8, `description` with file:line, `proposed_fix`, `verified` — but it is reached only through `codex exec --output-schema`, at `bench/experiment_11_orchestrator.py:1143-1145` and `bench/cx_efficiency_confer_r2.py:59-61`. Neither is on the panel's dispatch path. **The panel has never asked for a structured finding.**

The schema doc's §10 does specify an output contract for the round (`bench/directives/universal/cdsfl_core_formal.md:325-341`): either `declare(CONVERGED, justification, evidence)` or `emit findings F_k under the §17 schema`. **`§17` is a dangling reference — the document has no section 17** (headings run 1-10 plus named sections; `grep -n "§17"` returns only line 329 and a cross-reference to a *different* file, `cdsfl_operational.md`). So the one place the schema names a finding format points nowhere in that document.

### Is convergence compelled? No, and it is enforced.

`bench/tests/test_panel_runs_under_the_schema_2026-09-07.py:80-100` imports the dispatcher and inspects the real `SYSTEM` value (not the source text), asserting that all 4 of `NO COMPELLED CONVERGENCE`, `NEVER disable or remove a feature`, `ONE-SHOT DISPATCH` and `TOOLS DECIDE, NOT VOTES` are present, **and** that none of them appears in the schema doc, so the addition is provably additive. The stop rule is §10's Sufficiency Assessment, whose Integrity clause makes a convergence declaration issued to satisfy the instruction "itself a §1 HARD-class violation".

### Tools: enabled on all 3 routes, recorded on 2 of 3.

- `claude_cli` (cc2, fable): native tools via `--allowedTools "Bash", "Read", "Grep", "Glob", "WebFetch", "WebSearch"` at `bench/experiment_11_orchestrator.py:964`. **No Write and no Edit** — seats edit through Bash, which is why confinement is positional. Calls recorded via `set_tool_log_sink` to `<seat>.tools.json` (dispatcher lines 218-224), read back into the seat record (235-239) **and on the exception path** (265-271), the latter fixed 2026-09-08 after the counter read 0 exactly when a seat failed.
- `openrouter` (cx, cgpt): `call_openrouter_with_tools(..., tools=TOOL_SPECS, max_tokens=32768, timeout=300)` at lines 243-247. TOOL_SPECS = `sympy_verify`, `z3_verify`, `pytest_run`, `ruff_check`, `mypy_check` (`bench/openrouter_tools.py:71,96,122,147,170`). Hard cap `MAX_TOOL_ITERATIONS = 6`.
- `deepseek` (ds): passed TOOL_SPECS but returns text only. The dispatcher's own docstring, lines 164-166: its `n_tool_calls` "is still structurally 0 and must be read as 'not recorded', never as 'ran nothing'."

### Other live mechanics the dispatcher already runs

Sandbox copy per panel (`panel_sandbox.build`, line 307) with per-thread cwd set inside the worker (lines 147-148, because a main-thread `threading.local()` is invisible to pool workers); repo fingerprint before/after (300, 337); operator control-plane fingerprint of `$HOME` (306, 331) after a seat wrote a hook into the real `~/.claude/settings.json`; seat edits kept as `seat_proposals.diff`, "untested; not applied" (322-328); `accept_reply_or_work` substance gate (228) that accepts a short reply only when real work sits beside it in the sandbox; `timeout=1800, max_retries=2`; `PANEL_ONLY` subset re-dispatch (61, 71).

### Roster discrepancy worth a ruling

`_ALL` at lines 62-68 is `cx`, `cgpt`, `ds` (paid), `cc2`, `fable` (Max) — **5 dispatched seats plus CC1 as operator = 6**. There is no Gemini seat. The founder's own `pr` definition in `~/.claude/CLAUDE.md` names the panel as "cc2, cx, ge, cgpt, ds" with CC1 participating. The dispatcher's docstring (lines 4-6) records the current roster as founder-authorised 2026-09-05. I am not adjudicating which is current; if "6 full paid model reviews" is to become the standard, which 6 needs stating.

## 2. Every other panel dispatcher, and whether it carries the formal schema

Measured: **45** files under `bench/` call `call_claude_cli`; 6 are tests, so **39 dispatchers**. Of those, **28 carry `cdsfl_core_formal.md`** and **11 do not**.

Carrying it (28) — and the spot-checks show they pass it as the system prompt, e.g. `confer_specialist_cells_pr_2026-07-28.py:37-38` (`SYSTEM = (...cdsfl_core_formal.md).read_text()`), `confer_exp40_prelaunch_round1.py:81-82` then `system_prompt=CDSFL_TEXT` at 503/513/522/559, `confer_stage6_full.py:63-64` then 253/263/272/303: `confer_definitional_advisory_2026-05-18`, `confer_divergence_directive`, `confer_divergence_pr_2026-06-03`, `confer_divergence_round2_convergence`, `confer_divergence_round3_final`, `confer_exp40_architectural_2026-05-15`, `confer_exp40_definitional_2026-05-18`, `confer_exp40_focused_round2_2026-05-10`, `confer_exp40_focused_round3_2026-05-13`, `confer_exp40_gamma_hardening_2026-05-17`, `confer_exp40_prelaunch_round1`, `confer_exp40_reaudit_round1`, `confer_exp40_timing_neutral_2026-05-16`, `confer_exp40to54_consolidated_plan_review_2026-04-21`, `confer_exp40to54_plan_review_round2_2026-04-21`, `confer_exp41_final_signoff_2026-05-23`, `confer_exp41_fix_verification_2026-05-22`, `confer_exp41_gamma_form_2026-05-23`, `confer_exp41_gamma_neutral_2026-05-23`, `confer_exp41_gamma_unify_2026-05-22`, `confer_exp48_draft_review_2026-07-29`, `confer_exp49_draft_review_2026-07-29`, `confer_exp50_draft_review_2026-07-29`, `confer_maths_panel_2026-09-05`, `confer_prose_adaptation_pr_2026-08-01`, `confer_specialist_cells_pr_2026-07-28`, `confer_stage6_full`, `experiment_11_orchestrator`.

**NOT carrying it (11)**: `build_experiment_run.py`, `confer_convergence_panel_2026-08-23.py`, `confer_dedup_crisis_pr_2026-08-18.py`, `confer_directive_pruning_pr_2026-07-12.py`, `confer_enforcement_prose_pr_2026-08-19.py`, `confer_operational_directive_pr_2026-06-06.py`, `confer_panel_2026-08-28.py`, `confer_stage1_audit_cc2_retry.py`, `confer_stage1_audit_pr_2026-08-18.py`, `confer_track_record_pr_2026-08-22.py`, `decomposed_dispatch.py`.

**The pattern in that list is the finding.** Every recent sandboxed panel dispatcher — the 2026-08-18 through 2026-08-28 generation, including `confer_panel_2026-08-28.py`, which the maths panel's own comment (line 216) names as "the 1 of 37 dispatchers that had it right" on tool logging — runs **without** the schema. The 28 that carry it are the older `confer_exp40`/`exp41` generation, and they carry the schema **alone**: `confer_specialist_cells_pr_2026-07-28.py:37-38` sets `SYSTEM` to the schema text with nothing appended, so none of them carries "NO COMPELLED CONVERGENCE", the additive standard, the one-shot notice or "TOOLS DECIDE, NOT VOTES".

So `confer_maths_panel_2026-09-05.py` is the **only** dispatcher in the repository that carries both halves. That is the artefact to standardise on.

## 3. What a complete FULL_RECORD panel review record contains

8 exist in `experimental_notes/`. Most recent: `Panel_Verification_FULL_RECORD_2026-09-04.md` (350 lines), then `Panel_Reduction_Criterion_FULL_RECORD_2026-09-03.md` (195 lines). The consistent skeleton:

1. **Title** — `# Panel Review — <subject> — FULL RECORD` (`Panel_Verification_FULL_RECORD_2026-09-04.md:1`).
2. **Dispatch header** — timestamp with timezone, dispatch time, commit SHA, seat count, isolation mechanism, cost. Verbatim, line 3: "**2026-09-04 22:15 BST.** Dispatched 2026-09-04 21:31 BST at `5a0f20c`. Two reviewers, sandboxed in disposable linked worktrees, Max-plan, no metered cost."
3. **Per-seat metrics table** — `Reviewer | Elapsed | Tool calls | Reply` (lines 5-8): cc2 1940s / 85 calls / 24,064 chars; fable 1180s / 96 calls / 13,108 chars. The tool-call column is the audit trail for "tools decide, not votes".
4. **Brief pointer** — `Brief: bench/logs/panel_verify_20260904T203042Z/BRIEF.md` (line 10). The 09-03 record also gives the brief's line count and names the raw artefacts: "Raw: `cc2.json`, `fable.json`, with per-reviewer tool logs."
5. **"Outcome, and what was done about it"** (line 13) — which items were CONFIRMED/REFUTED by which seat, that every refutation was reproduced locally before acting, and the commit the fixes landed in (`1928de4`).
6. **An explicit preserved-disagreement paragraph** (lines 19-25), naming the seats, both positions with their numbers, and what needs a founder ruling: "**The two reviewers DISAGREE on the disposal of the S_k gate, and the disagreement is preserved rather than smoothed.**"
7. **"Reproduced verbatim and unfiltered below."** (line 27) then a rule.
8. **`# REVIEWER: <name>`** per seat (lines 29, 273), each seat's reply in full, unedited, including its own working-copy path and its procedural caveats.
9. **Per-item verdict headings with an explicit label** — `**CONFIRMED**`, `**REFUTED**`, `**CONFIRMED, with a residual hazard**`, `**REFUTED-WITH-FIX**`, `**REFUTED AS STATED — confirmed in substance**` (lines 39, 63, 92, 121, 299).
10. **PART 1 / PART 2 split** — verification of shipped changes, then the open questions (lines 37, 138).
11. **A self-falsification section** — fable's `## What would prove me wrong` (line 342).
12. **Summary** (line 258), placed after the full output, never instead of it.

## 4. Does any brief require a seat to USE the mathematical model? No.

Measured across all 49 `BRIEF.md` files in `bench/logs/`, plus full reads of the 11 most recent:

- gamma appears in 13 briefs, rho in 10, "two-sided" in 4, `compute_rk`/R_k in several — **every occurrence is the model as the SUBJECT under review, never as an instrument the seat applies to its own finding.** Examples: `instrument_confirmation_panel_2026-08-28/BRIEF.md:38` lists "I02 Two-sided gamma gate" as an instrument to be audited; `panel_sandbox_proof_20260906T224800Z/BRIEF.md:22` describes what "`compute_rk` clamps"; `panel_gate_fixes_20260906T181457Z/BRIEF.md:41` asks whether "The shipped S* is not the break-even of the shipped `nu_eff`".
- Briefs asking a seat to state or derive **its own** R_k, gamma, rho or severity: **0 of 49**.
- Briefs using the schema's mandatory `FALSIFIER:` label for CRITICAL findings: **0 of 49**.
- Briefs requesting the `cdsfl_finding_schema.json` fields (`finding_id`, `flaw_class`, `severity`, `verified`): **0 of 49**.
- Briefs naming the schema or its §10 stop rule at all: **3 of 49** — `confer_stage1_audit_2026-08-18`, `panel_v32_confirm_20260830T192327Z`, and `panel_poc_readiness_20260907T234500Z`, the last of which is the only one that binds it, at line 35: "**Termination criterion.** Stop when your own passes stop producing new above-threshold findings — the schema's §10, Sufficiency Assessment and Convergence Declaration, is the standard."

The closest any brief comes to the model-as-instrument is the mathematical *tooling* instruction, e.g. `panel_rubric_forward_20260906T142634Z/BRIEF.md:6-8`: "Use your shell — sympy, z3, numpy, scipy, statsmodels, wolframscript, and the repo itself. The named `sympy_verify` tools are NOT on your route; say so and use the shell." That names the tools; it does not name the model.

Meanwhile the SYSTEM prompt's only mathematical instruction is one clause — "Where you assert a mathematical result, DERIVE it" (dispatcher line 107) — and the schema doc itself contains **0** occurrences of gamma, **0** of rho, **0** of "two-sided", and **1** of "severity" (line 417, `V(f) = materiality(f) = consequence if defect f ships (= severity)`). So the mathematical model reaches a seat through neither half of the current prompt.

## 5. Does any brief require the seat to PRODUCE AND TEST a fix?

**Produce: 8 of 49. Test: 2 of 49. Nothing in the SYSTEM prompt requires either, and no test guards it.**

Producing a fix is demanded in `fixes_and_ffafp_20260907`, `five_fixes_review_20260907`, `panel_reach_gap_20260906T002016Z`, `panel_stage_chain_20260906T021522Z`, `severity_enforcement_review_20260907`, `panel_rubric_forward_20260906T142634Z`, `panel_todays_fixes_20260906T175435Z`, `severity_review_2_20260907`. The strongest wording, verbatim:

- `panel_rubric_forward_20260906T142634Z/BRIEF.md:3-6`: "## You are asked for a SOLUTION, not a verdict / The founder's standing instruction: propose the fix, do not merely find the fault. A verdict that only diagnoses is a failed answer."
- `severity_enforcement_review_20260907/BRIEF.md:7-11`: "**THE INSTRUCTION THAT MATTERS MOST.** The founder's standing complaint is that reviewers are asked to find problems and never asked for the repair. So: for every defect you find, supply the FIX — a concrete patch or exact edit — and state how you tested it. A finding without a proposed fix is half an answer here."
- `fixes_and_ffafp_20260907/BRIEF.md:1` and `:41`: "# Two jobs. Supply FIXES, not findings." ... "**For each: supply the fix.** Patches, not descriptions. Say what you ran."
- `five_fixes_review_20260907/BRIEF.md:29-30`: "(c) If either answer is no, SUPPLY THE FIX. A finding without a repair is half an answer here."

Requiring the fix be **tested** is only 2 of 49 — `severity_review_2_20260907/BRIEF.md:11` ("supply the FIX — the concrete patch — and say how you tested it") and `panel_scale_20260902T125010Z/BRIEF.md`. And "say how you tested it" is a self-report, not a mechanical check.

**The harness already has the mechanical check, and the panel does not use it.** `bench/reference_runner_v3.py:2253-2258` briefs the in-round panel: "When a CONFIRMED finding carries a parseable proposed_fix in SEARCH/REPLACE format, the runner applies it to a sandbox copy of the target file and runs ruff + mypy + bandit + the experiment's test suite. On clean pass, the finding transitions to CLOSED." On a prose target that path is disabled and the route is a runnable falsifier instead (lines 2242-2251). That loop lives in the experiment runner. The confer panel never asks for SEARCH/REPLACE format (1 of 49 briefs mentions the phrase, `panel_reach_gap_20260906T002016Z/BRIEF.md:61`, and only as a fix-complexity metric), never applies a seat's fix, and never runs the gate: the dispatcher writes `seat_proposals.diff` and prints "(untested; not applied)" (line 328).

## THE GAP — what a compliant brief must contain that current briefs do not

1. **A required output schema for findings.** Currently prose. Must bind the seat to `bench/cdsfl_finding_schema.json` fields — `finding_id`, `type`, `severity`, `flaw_class`, `description` with file:line, `proposed_fix`, `verified` — or an equivalent named in the brief. Nothing in the panel path does this today.
2. **A required `FALSIFIER:` block for every CRITICAL finding**, per `cdsfl_core_formal.md:437-455`: import the real target module, fail iff the defect is present, and be RUN before reporting with the actual output pasted. 0 of 49 briefs use the label; the requirement is in the SYSTEM prompt's schema and is never carried into the task.
3. **An instruction to USE the mathematical model, not only review it.** The founder's words: seats "must use whatever aspects of the harness are currently working, including our mathematical model and all relevant mechanics in the formation of their answers/fixes". Concretely: state the severity with its worked proof so `severity_is_proven` (`reference_runner_v3.py:6643`) would accept it; where a finding bears on convergence, compute R_k via `compute_rk` (`:9925`) / `validate_round_rk` (`:10449`) rather than asserting; where a fix changes an acceptance decision, evaluate it against `sk_break_even` (`:10527`). 0 of 49 briefs ask for any of this.
4. **A fix that is PRODUCED AND MECHANICALLY TESTED, not self-reported as tested.** Require SEARCH/REPLACE format so `reference_runner_v3.py:2253-2258`'s sandbox-apply + ruff/mypy/bandit/test-suite gate can run it, and require the seat to paste the gate's real output. Today: 8 of 49 ask for a fix, 2 of 49 ask how it was tested, 0 of 49 route it through the gate.
5. **An explicit §10 termination clause.** Only `panel_poc_readiness_20260907T234500Z/BRIEF.md:35` binds it. It must be in every brief, with §10's Integrity clause quoted so a seat cannot declare convergence to satisfy the instruction.
6. **A stated review target with its commit SHA**, so the record's dispatch header can be written and the review is reproducible. Present in the best briefs (`panel_gate_fixes...:19` "Everything is committed at HEAD on main, suite green at 5251 passed"), absent from others.
7. **The FULL_RECORD contract stated up front** — what the seat's reply must contain so the record's 12 sections can be assembled without the operator inventing them: per-item verdict label from a closed set (CONFIRMED / REFUTED / REFUTED-WITH-FIX / CONTESTED / UNVERIFIED), commands run with real output quoted, and a "what would refute my own answer" section.
8. **A test that guards the brief, the way `test_panel_runs_under_the_schema_2026-09-07.py` guards the system prompt.** There is no such test. `BRIEF.md` is read with no validation at all (dispatcher line 58), so any of items 1-7 can be silently omitted by whoever writes the next brief — which is the exact failure shape the additive standard names, and the one the additive-standard block was added to the SYSTEM prompt to prevent.
9. **A named roster of 6.** `_ALL` (lines 62-68) has 5 dispatched seats and no Gemini; the founder's `pr` definition has Gemini and not Fable. "The standard for all future 6 full paid model reviews" needs the 6 fixed.
10. **A place to save it.** No brief template, no format document and no test exists anywhere in the repository — `find` for `*brief*template*` / `*panel*template*` returns nothing.

### Does the record support the founder's framing?

SUPPORTS the diagnosis, CONTRADICTS the presupposition.

The founder's ruling, verbatim from the transcript at 2026-09-09T12:21:11.938Z: "In all cases and with all fixes *always* check them with Fable and CC2 in full CDSFL panel review format (so not just some simple open ended prompt), they must use whatever aspects of the harness are currently working, including our mathematical model and all relevant mechanics in the formation of their answers/fixes, as should you. this format should then be saved as the standard for all future 6 full paid model reviews also."

His diagnosis is CONFIRMED by measurement. The briefs really are closer to open-ended prompts than to a format: 49 hand-written markdown files read straight off disk (bench/confer_maths_panel_2026-09-05.py:53-58) with no template, no schema, no validation and no test. The 2 things he specifically named are the 2 weakest parts of what exists — 0 of 49 briefs require the mathematical model in forming an answer, and only 2 of 49 require a produced fix to be tested.

The presupposition is CONTRADICTED. "This format should then be saved as the standard" presumes a full format already exists and only needs saving. Half of it does: the SYSTEM prompt is real, composed, schema-backed and guarded by an executing test (bench/tests/test_panel_runs_under_the_schema_2026-09-07.py). The other half does not exist as a format at all. There is nothing to save on the task side — it has to be written first, then wired to the dispatcher and pinned by a test, or it will be omitted by whoever writes the next brief. No brief template, format document or guarding test exists anywhere in the repository.

One further correction to the framing, offered because it changes what gets built: "whatever aspects of the harness are currently working" is broader than the panel currently reaches. The mechanical fix-verification loop the founder is implicitly asking for already exists — reference_runner_v3.py:2253-2258 applies a SEARCH/REPLACE proposed_fix to a sandbox copy and runs ruff + mypy + bandit + the test suite — but it lives in the experiment runner, and the confer panel has never used it. That is the largest single piece of working harness the new format can pick up, and it converts "say how you tested it" from a self-report into a measurement.

### Recommendation (not implemented)

DO NOT IMPLEMENT — this is the specification, for your ruling.

Adopt bench/confer_maths_panel_2026-09-05.py as the canonical dispatcher: it is the only one of 39 that carries both the 28,183-character formal schema and the 4 panel-specific rules, and the only one with sandbox confinement, control-plane fingerprinting, real tool-call recording and a test that executes rather than greps. Nothing needs replacing on the SYSTEM side.

Write the missing half as a committed brief template plus a validator, in this order:

1. Add a template file (suggest bench/directives/universal/panel_brief_template.md) carrying the 10 gap items: required finding schema, mandatory FALSIFIER: block for CRITICAL findings, the model-as-instrument clause naming severity_is_proven / compute_rk / validate_round_rk / sk_break_even, SEARCH/REPLACE fix format routed through the runner's sandbox gate with the gate's real output pasted, the §10 termination clause quoted including its Integrity paragraph, the target with its commit SHA, the closed verdict-label set, and the "what would refute my own answer" requirement.

2. Wire it. The dispatcher currently reads BRIEF.md and validates nothing (line 58). Add a check that the brief carries the required sections and fail the dispatch if it does not — the same shape as the existing schema guard. An unvalidated template is an addition wired to nothing, which is the failure mode the additive standard block in the SYSTEM prompt exists to prevent, and which this project has confirmed 11 times since 2026-08-01.

3. Pin it with an executing test, modelled on test_panel_runs_under_the_schema_2026-09-07.py: load a real brief and assert the validator accepts it, then mutate one required section out and assert it rejects. Asserting on the template's source text would only prove the template describes itself consistently — execute-do-not-grep.

4. Fix the §17 dangling reference in cdsfl_core_formal.md:329 while the format is being settled, since it is the one place the schema names a finding format and it points at no section of that document. Confirm whether it means cdsfl_operational.md §17 or bench/cdsfl_finding_schema.json before editing.

Two items need your ruling before the template can be written:

A. The roster. bench/confer_maths_panel_2026-09-05.py:62-68 dispatches cx, cgpt, ds, cc2, fable — 5 seats plus CC1 as operator, no Gemini. Your own pr definition names cc2, cx, ge, cgpt, ds plus CC1. "The standard for all future 6 full paid model reviews" needs the 6 named. Note also that the dispatcher's own docstring records a measured confound: the cx and cgpt seats currently share weights, route and system prompt, so the panel is "closer to 4 distinct conditions than 5".

B. The ds seat. Its tool-call count is structurally 0 on the deepseek route, which the dispatcher documents as "not recorded, never ran nothing". If a compliant review requires executed evidence, that seat cannot supply the audit trail the other 4 can. Either the route gets a tool loop or the standard records the exception explicitly.

I have not run anything that writes. In particular I did not execute test_panel_runs_under_the_schema_2026-09-07.py to confirm it currently passes, because it creates and removes a probe directory under bench/logs; someone should run it before the format is declared.

### What could not be established

4 things I could not establish.

1. The composed length of the SYSTEM prompt. The dispatcher's comment at lines 93-94 claims "~3.0K to ~31.2K characters, about 7,800 tokens". I measured the schema at 28,183 bytes with wc -c but did not measure the total, because obtaining it means importing the module, which writes a probe directory under bench/logs. The 31.2K is the file's claim, not my measurement.

2. Whether the schema guard currently passes. Same reason — running the test writes. It is written to execute rather than grep, and its assertions match what I read in the SYSTEM string, but I have not seen it go green.

3. Whether all 28 schema-carrying dispatchers place the schema in the system prompt. I confirmed the path reference in all 28 by grep, and confirmed the system-prompt placement by reading 4 of them (confer_specialist_cells_pr_2026-07-28.py, confer_exp40_prelaunch_round1.py, confer_stage6_full.py, confer_exp41_gamma_unify_2026-05-22.py). The remaining 24 are inferred from an identical code shape, not read. The 11 that do NOT reference the file at all are established by grep and are certain.

4. Whether the Fable-for-Gemini roster substitution was ruled by you or adopted by CC1. The dispatcher docstring says "Founder-authorised 2026-09-05" for the whole roster including Fable; your pr definition in CLAUDE.md still names ge. I did not search the transcripts for the authorising message, so I cannot say which is current and have not adjudicated it.

One thing I deliberately did not do: I read 11 of the 49 briefs in full and characterised the other 38 by targeted grep. The counts I report (0 with FALSIFIER:, 0 with own-R_k, 8 requiring a fix, 2 requiring it tested, 3 naming the schema) are grep-measured across all 49 and are reliable for those tokens. A brief could in principle demand the mathematical model in wording none of my patterns match; I judge that unlikely given the 11 full reads, but it is not excluded.

### Evidence

- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:53-58 — the USER prompt is not constructed; BRIEF.md is read off disk with no template, schema or validation
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:95-96 — _SCHEMA reads bench/directives/universal/cdsfl_core_formal.md
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:98-134 — the full SYSTEM prompt: schema + 7 appended blocks (tools-decide, no-compelled-convergence, declare-sound, no-padding, additive standard, one-shot dispatch)
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:62-68 — roster _ALL: cx, cgpt, ds paid; cc2, fable Max. No Gemini seat
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:218-239,265-271 — tool-call sink written, read back into the seat record, and read on the exception path
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:240-247 — deepseek passed TOOL_SPECS but returns text only; openrouter uses call_openrouter_with_tools
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_maths_panel_2026-09-05.py:322-328 — seat edits captured as seat_proposals.diff, printed '(untested; not applied)'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md — 28,183 bytes measured by wc -c; headings 1-10 plus 5 named sections
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md:287-341 — §10 Sufficiency Assessment; line 329 'emit findings F_k under the §17 schema' is a dangling reference, the document has no §17
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md:437-455 — Runnable Falsifiers: CRITICAL findings MUST carry a FALSIFIER: block, importing the real target, run before reporting
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/directives/universal/cdsfl_core_formal.md — grep counts: gamma 0, rho 0, 'two-sided' 0, severity 1 (line 417)
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_panel_runs_under_the_schema_2026-09-07.py:70-100 — imports the dispatcher and inspects the real SYSTEM value; requires the schema and all 4 panel rules, and proves the addition is additive
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/experiment_11_orchestrator.py:964 — --allowedTools Bash, Read, Grep, Glob, WebFetch, WebSearch. No Write, no Edit
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/experiment_11_orchestrator.py:1143-1145 — cdsfl_finding_schema.json is reached only via codex exec --output-schema, not on the panel path
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/openrouter_tools.py:71,96,122,147,170 — TOOL_SPECS: sympy_verify, z3_verify, pytest_run, ruff_check, mypy_check
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/cdsfl_finding_schema.json — required fields finding_id, type, severity, flaw_class, description, proposed_fix, verified
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v3.py:2253-2258 — the mechanical fix-verification loop: SEARCH/REPLACE proposed_fix applied to a sandbox copy, ruff + mypy + bandit + test suite, clean pass transitions to CLOSED
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v3.py:2242-2251 — on a prose target the fix path is disabled and a runnable falsifier settles the finding instead
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v3.py:6643,9925,10449,10527 — severity_is_proven, compute_rk, validate_round_rk, sk_break_even: the model-as-instrument entry points no brief invokes
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/panel_poc_readiness_20260907T234500Z/BRIEF.md:35 — the only brief of 49 that binds the schema's §10 termination criterion
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/panel_rubric_forward_20260906T142634Z/BRIEF.md:3-6 — 'You are asked for a SOLUTION, not a verdict ... A verdict that only diagnoses is a failed answer.'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/severity_enforcement_review_20260907/BRIEF.md:7-11 — 'supply the FIX — a concrete patch or exact edit — and state how you tested it'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/severity_review_2_20260907/BRIEF.md:11 — 1 of only 2 briefs requiring the fix be tested
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/fixes_and_ffafp_20260907/BRIEF.md:1,41 — 'Supply FIXES, not findings' / 'Patches, not descriptions. Say what you ran.'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/ — 49 BRIEF.md files; 0 use the FALSIFIER: label, 0 ask a seat to derive its own R_k/gamma/rho/severity, 8 require a fix, 2 require it tested, 3 name the schema
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Panel_Verification_FULL_RECORD_2026-09-04.md:1-27,342 — the record skeleton: title, dispatch header with SHA, per-seat metrics table, brief pointer, outcome, preserved disagreement, 'Reproduced verbatim and unfiltered below', per-reviewer sections, 'What would prove me wrong'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Panel_Reduction_Criterion_FULL_RECORD_2026-09-03.md:1-11 — same skeleton plus brief line count and raw-artefact pointer (cc2.json, fable.json, per-reviewer tool logs)
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_specialist_cells_pr_2026-07-28.py:37-38 — a schema-carrying legacy dispatcher: SYSTEM is the schema ALONE, with none of the 4 panel rules
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/confer_panel_2026-08-28.py:47 — hand-written SYSTEM, no schema; 1 of the 11 dispatchers lacking it, and the whole recent sandboxed generation is in that group
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl — founder message 2026-09-09T12:21:11.938Z carrying the ruling verbatim

## full-work-list

**The 5 authoritative sources carry 121 distinct outstanding items and 24 closed-item groups; 19 of the open items already carry a founder ruling and need only execution, 17 need a founder decision before anything can start, and 1 item recorded as open (the 11-commit push) closed today at 11:55:48 BST.**

### Findings

SCOPE AND METHOD

I read, in full or by targeted traversal: `experimental_notes/CDSFL_Agent_Operational_Plan.md` (1417 lines), `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` (372 lines), `resources/RECOVERY.md` (3121 lines, PENDING region lines 1461-3060 plus the SESSION STATE region lines 1-68), `docs/CURRENT_STATE.md` (69 lines), `MEMORY.md`, and `memory/cdsfl_runway_2026-08-18.md`. That last file is a 3-line pointer: its own text at lines 12-13 says "Canonical: `experimental_notes/RUNWAY_to_BR2_2026-08-18.md`", so I read that 814-line file as well — without it, source 5 yields no items at all. I also read `experimental_notes/Morning_Report_2026-09-09.md`, committed at `57d5a0e` this morning, because it is the newest verification pass over outstanding items and it CORRECTS 4 claims that the plan and RECOVERY.md still assert.

All paths below are relative to `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`.

COUNTS

121 distinct open items. 24 closed-item groups. 4 of my numbered entries are cross-listings of the same underlying item and are marked as such (they are not counted twice in the 121).

Of the 121 open: 19 carry an explicit founder ruling and need only execution; 17 are blocked on a founder decision that has not been given; 26 are blocked on a named prior item (usually the simulated run, Exp 53, or BR2); the remainder are unblocked engineering or documentation work.

=== GROUP A. FOUNDER RULINGS OF 2026-09-06, SCHEDULED NOT OPEN (19 items) ===

`CDSFL_Agent_Operational_Plan.md:13-60`. The section header says it plainly at :15-16: "Every item below carries a founder ruling from the answer file of 2026-09-06. They are scheduled, not open: nothing here needs a further decision, only execution at the named point." None of the 19 has been executed.

Study programme for the simulated run (all 6 measured DURING the run, so all blocked on it):
1. Watch whether the critical-severity ceiling ever binds. `plan:22`. RULED ("leave as is until the run gives data"). Small.
2. Investigate live why the sweep cannot clear a critical (38 sub-criticals stuck). `plan:23`. RULED. Medium. [Cross-listed with entry 40.]
3. Classify each falsifier ERROR as guard-raises vs missing-target (16 of 25 unexplained). `plan:24`. RULED. Medium.
4. Study the rho = 0.564 cross-architecture correlation, then recommend. `plan:25`. RULED, founder verbatim: "Study this in the upcoming simulated run, then make recommendations when complete." Medium.
5. Run with CORRECTED S* values, not shadow; study and recommend after. `plan:26`. RULED, founder verbatim: "better to run with corrected values and precision". Medium.
6. Test both reach conditions (fable: both homes; cc2: sigma only). `plan:27`. RULED, founder verbatim: "we can test both conditions to see what gives the better result, or even if they might be non-binary". Medium.

After the simulated run, before BR2:
7. Re-run Exp 48 and Exp 49 under the new design. `plan:35`. RULED ("Make this our plan"). BLOCKED on the simulated run. Costs money. Large.
8. Gamma unification — headline gamma on the genuine-critical series. `plan:36`. RULED ("Do it as you suggest"). BLOCKED on the run because it touches convergence machinery. Medium-large. Note: the same item sits in RECOVERY.md's pending region at `resources/RECOVERY.md:1519` still labelled "PENDING ... awaiting founder go-ahead" — that label is now stale; the go-ahead was given.
9. One paid sentinel dispatch, one dispatch not a panel. `plan:37`. RULED. BLOCKED until the simulated run is clean. Small.
10. Residual key exposure via the assistant's own session store. `plan:38`. RULED, founder verbatim: "mark it as an item to be dealt with on the runway after the simulated run". Medium.

Immediately before Exp 54:
11. Exp 54 Cell A entry-method decision (RQ3). `plan:44`. RULED to defer, founder verbatim: "Defer, but mark clearly on the runway as a decision for immediately before then." Small (a decision).
12. The DECISIVE form of the false-CONFIRMED discrimination control. `plan:45`. RULED: defer until Exp 53 completes. BLOCKED on Exp 53. Medium. [Cross-listed with entry 41.]

After BR2:
13. FW.6 harvested historical revisions as a recall target. `plan:51`, detail at `RUNWAY_to_BR2_2026-08-18.md:812`. RULED. BLOCKED on securing the 676-commit branch AND on BR2. Large.
14. Open-topology anti-dispute safeguard. `plan:52`. RULED, founder verbatim: "mark all 3 on the runway at an appropriate point after BR2". Medium.
15. A1 directive-pruning cuts plus ablation. `plan:53`. RULED. Medium.
16. `dm` consolidation steps 2 to 6 plus rename. `plan:54`. RULED. Large.
17. Disposition of ruling 1 (prose-similarity / hierarchical novelty). `plan:55`. RULED. Medium.

Held for the founder's return, do not start:
18. The answer-key sealing: 29 plaintext key files, 27 of them BR2 answer keys for exams never run. `plan:59`. NEEDS FOUNDER — his passphrase AND his fold-or-separate choice. Founder verbatim on timing: "as soon as all these outstanding issues have been addressed, and immediately before the simulated run". Small-medium once he is present. Note the count moved: `plan:212` recorded 31 key files on 2026-08-28.
19. The simulated run itself. `plan:60`. HELD by founder instruction. Large. Standing instruction at `plan:29`, founder verbatim: "you don't need to stop at one simulated run. You can run as many as it takes to guarantee accuracy."

=== GROUP B. THE CURRENT RESUME POINTER (4 open, 1 now closed) ===

20. Apply a pending desktop-app update deliberately before any long run. `plan:66`. No ruling recorded; it is stated as an operational consequence. Small. Mechanism verified in the app's own log: 48 consecutive deferrals then "Auto-restarting app after update pending for 85 hours" at 16:52:11.
21. Attribution of the 12 `bench/dm/_memory.py` rewrites is OPEN. `plan:70`: "the log records blob hashes and not authors, so attribution is OPEN." Medium — needs an instrumentation change, not analysis.
22. Whether the seat's `update_drift` guard fix is CORRECT is OPEN and unassessed. `plan:76`. Medium.
23. Tie a monitor's lifetime to its run's process. `plan:78`: "Fix candidate, not yet built." Confirmed still open by `Morning_Report_2026-09-09.md:47`, which adds the constraint that macOS `tail` rejects `--pid`, so it must be a shell wrapper. Small-medium.

CLOSED TODAY, and the record does not yet know it: `plan:64` says "10 ahead of `origin/main` at `071f1ed` — STILL NOT PUSHED; the push is blocked at this end and is the founder's to run", and `Morning_Report_2026-09-09.md:69` repeats it as founder decision 1. Measured: `git rev-list --count origin/main..HEAD` = 0, `git rev-parse origin/main` = `9e3dfe9`, and `git reflog show origin/main --date=iso` reads "9e3dfe9 refs/remotes/origin/main@{2026-09-09 11:55:48 +0100}: update by push". The push happened at 11:55:48 today. This item is done.

=== GROUP C. PHASE F, THE ONLY SURVIVOR OF THE 22 APRIL SHIFT (3 items) ===

Recorded twice, once as the live copy and once in the closed shift. `plan:626-627` states the scoping: "Phase F is the only part of that 22 April 2026 shift still open."
24. F1 — read `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` Section XI end to end. `plan:631` and `plan:864`. Unblocked. Small.
25. F2 — consolidate the 27 frontier STEM problem sets into the plan. `plan:632`, `plan:865`. Medium.
26. F3 — nail down per task: domain, claim-cluster, expected tool routing, falsifiability criterion. `plan:633`, `plan:866`. Large.

=== GROUP D. THE EXP 39 TO EXP 40 GAP-CLOSURE LIST (3 open of 9) ===

27. G6 — specialist-to-specialist verdict-conflict resolution. `plan:809`. Status "Scheduled". Named an Exp 49 blocker. Medium.
28. G7 — MERGE deadlock auto-arbitration. `plan:810`, status "Scheduled". CONTRADICTED WITHIN THE SAME FILE: `plan:226` records "DECISION 5 ANSWERED — G7's MERGE PATH IS DEAD CODE ... Closed deliberately by the founder's no-voting ruling (2026-08-19). So G7 is a de-duplication PREVENTER, never a merger." The open work here is a record correction, not a build. Small.
29. G8 — burst-mode Phase 0 convergence override. `plan:811`. Scheduled for a future burst experiment. Medium.
G1, G2, G3, G4, G5 and G9 are all marked CLOSED at `plan:804-808` and `plan:812`.

=== GROUP E. STANDING ITEMS INHERITED FROM SUPERSEDED POINTERS (7 items) ===

The plan's own rule at `plan:617` is that standing instructions are inherited, not left behind, so these remain live even though they sit below the current pointer.

30. Item #16 — 17 fixes, 11 equipment repairs, 4 containments. `plan:160`; scope at `CLOSING_2026-09-06.md:43`: "The adjudicator's own dry run puts the workable population at 90 code targets, with 43 exam targets needing the off repo store that is held ... This is the largest single piece of work remaining." Large. The 43 exam targets are BLOCKED on the held keys (entry 18).
31. The discrimination overlay's 3-times-per-finding build cost. `plan:160`. Medium.
32. Founder's-notes backfill. `plan:160`, `plan:174`. Founder has AUTHORISED it; NOT STARTED. Large. Verified today: `docs/FOUNDERS_NOTES.md` last dated section is "## Experiment 40 Stage 3 Closure (17-18 April 2026)" at :721, and `git rev-list --count --since=2026-04-18 HEAD` returns 557 commits. The plan's figure of 494 commits was correct on 2026-09-06 and has since grown.
33. The references section, deferred to discussion. `plan:176`. NEEDS FOUNDER. Small.
34. D6 disclosure measurement. `plan:196`: "STILL GENUINELY OUTSTANDING". Medium.
35. D11 seat contrast. `plan:196`. Medium. Config is built — `bench/exp56_configs/d11_seat_contrast_diversity_arm.json` exists — and no run directory for it exists under `bench/logs/`.
36. Local Wolfram Engine licence expires 2026-09-11. `plan:220`, carrying its own `[VERIFY:current]` flag. That is 2 days from today. Small (a decision, possibly a renewal). Interacts with entry 44.

Two further items at `plan:176` are now SUPERSEDED rather than open: "promote the corrected S* threshold to live" is answered by the 2026-09-06 ruling at `plan:26`, and "where reach belongs" is answered at `plan:27`.

=== GROUP F. OUTSTANDING_QUEUE_to_BR2.md, SECTIONS A THROUGH E (17 items) ===

Section A is CLOSED. `OUTSTANDING_QUEUE_to_BR2.md:57`: "THE MUST LIST IS CLOSED (A1-A10), 2026-08-01 23:35 BST", with each of A1 through A10 marked DONE at :19-28.

A STALE CONTRADICTION INSIDE THAT SECTION, worth fixing before it misleads a future agent: `queue:73-75` still reads "A9 is the launch gate; A10 is the rejection-evidence feed. Neither is started. All eight queued prose configs still fail A9's 3/3 preflight checks." Both halves are refuted by the same file: :27-28 record A9 and A10 DONE at commit `f1c9b9a`, and :59-65 is a correction headed "A9-CORRECTION" which measured the 3/3 claim and found it FALSE. Small doc fix.

37. The SHOULD list, before the factorial — 4 sub-items. `queue:77-80`: rejection-evidence bundles in the sweep prompt; signature-homogeneity halt; extraction-scoped bandit as a veto only, never a score; report fields separating discovery convergence from fix validation. Medium each.
38. LATER: a genuine prose effect stage, with document invariants and negative controls that provably fail, calibrated on local fixtures. `queue:82-83`. Large.
39. B2 — the shadow-log redirect is keyed on `"pytest" in sys.modules` rather than on a run being in progress. `queue:112-123`, deliberately deferred at `queue:316-335` (B7) with the remedy written out: "Do it in daylight, before a run, with the marker wired at the runner's log-dir creation and a test that a live run still writes to its own directory." Small-medium. Not a founder item; deferred on measured risk.
40. The 38 stuck-CONFIRMED sub-criticals with no route to terminal. `queue:176-177`. [Same item as entry 2.]
41. The false-CONFIRMED hole — a valid-but-logically-wrong falsifier closed a finding against a TRUE claim. `queue:178`. [Same item as entry 12.]
42. Falsifier transport truncation plus 4 skipped tests. `queue:179`. Medium. UNCERTAIN: the 4 tests skipped in today's suite are a different set — the HEAD commit message for `9e3dfe9` states "All 4 are in test_br2_keys_are_split_out_2026-08-27.py and skip because the Bench Run 2 key store lives outside the repository". Whether the 2026-08 skips were resolved or merely displaced I could not establish.
43. Docs sweep. `queue:181`. Medium.
44. Whether a free local Wolfram Engine removes the 24-to-40-second gateway ceiling without losing curated data, and whether its licence permits use in a published MIT project. `queue:199-201`: "Under research; nothing installed." Small-medium.
45. A retry CAP on the routing ladder. `queue:310-313`: "Open, measured, NOT built." BLOCKED on extracting the round-of-rescue distribution. The queue adds a warning: "Do not implement it on intuition — the intuition here was already wrong once." Medium.
46. Exp 53 zero-plant control: restart or resume. `queue:228` and `queue:238`. PAUSED mid-run, 4 rounds spent. NEEDS FOUNDER RULING. Recommendation on file: restart. Large.
47. Exp 50 physics. `queue:229`; `RUNWAY_to_BR2_2026-08-18.md:296`: "BUILT, NOT RUN ... Blocked on the held-out-status ruling, not on the file." Large. Verified: no `exp50*` directory under `bench/logs/`.
48. Exp 51 biology. `queue:230`; `runway:297`. Same block. Large. Verified: no run directory.
49. Exp 52 factorial, 4 cells. `queue:231`; `runway:298-301`. Same block, plus the answer key is public in git history. Large. Verified: no run directory.
50. Exp 54 capstone / integration. `runway:302`: "no config yet — NOT BUILT". Verified: no `bench/exp54*` directory exists. Large.
51. BR2 itself. `queue:232`: "not started ... Blocked on all of the above." Large.
52. Disposition of `exp39-experimental`. `queue:239-259`, concluding: "DO NOT DELETE until the 107 commits are either merged non-destructively or deliberately declared redundant. Neither has happened." NEEDS FOUNDER. THE RECORD IS INTERNALLY INCONSISTENT ON THIS: `plan:122` says the 2026-08-23 instruction is to KEEP the branch; `resources/RECOVERY.md:68` says "the founder stated on 2026-09-08 that it is fully retired"; `resources/ONBOARDING.md:18` records the 2026-09-08 ruling as "`exp39-experimental` is to be adjudicated by Fable and CC2 against a sandboxed copy before any deletion." Verified: the branch exists locally (`git branch -a`), and the remote carries only `main`.
53. Panel confound — inject a published Codex system prompt into one of the two byte-identical GPT-5.5 seats. `queue:279-281`: "Founder approved ... NOT BUILT." APPROVED, not built. Medium. CAUTION: the mechanism is superseded by `runway:782` (0C.59), which corrects the account — the historic Codex/ChatGPT difference was AGENCY (a shell in the working directory versus a bare API call), not instruction framing. Building the approved fix as written would reproduce the wrong variable.

Section D items 3 and 4 are closed and are listed under CLOSED below.

=== GROUP G. RECOVERY.md, THE PENDING WORK REGION (9 items) ===

The region is delimited by `<!-- SV:PENDING_START -->` at `resources/RECOVERY.md:1461` and `<!-- SV:PENDING_END -->` at :3060. Its blocks run newest-first and the NEWEST is headed "Current Pending Work (2026-06-03, post-divergence-study)" at :1462 — 98 days stale as of today. That staleness is itself entry 62.

54. Anti-cooking condition (b), the held-out-corpus or null-distribution half. `RECOVERY.md:1531`: "STILL OPEN". The other half — threshold reachability — was measured on 2026-09-05 and is closed. Medium.
55. HIL materiality confirmation on C0015 and C0017. `RECOVERY.md:1521`. NEEDS FOUNDER. UNCERTAIN: `CLOSING_2026-09-06.md:39` reports that the materiality review's stated population does not reproduce — "experiment 49 carries 0 refuted findings and 0 irreducible items against a claimed 11" — so the item may be moot. I could not establish which.
56. CX2 (Codex CLI) wiring into the experiment runner. `RECOVERY.md:1479` and :1495: "still deferred". Medium.
57. Panel-falsify the divergence thesis, and trace the consensus-machinery accretion through the git and experiment timeline. `RECOVERY.md:1485`, :1499. Status unverified — I found no later note recording either as done.
58. Architecture (B), distributed problem-decomposition — the "Global Mind" at scale. `RECOVERY.md:1488`: "achievable but unbuilt"; :1491 places it third, after the tools-decide restoration. Large, and explicitly not a PoC prerequisite per `RECOVERY.md:1468`.
59. The carried-forward backlog at `RECOVERY.md:1523`: outstanding-criticals veto (deferred); the `_manager.py` adaptive-tau_sim-under-embedding interaction (flagged); the iteration-footnote backlog; 4 pre-existing `_manager.py` F401 lints; FFAFP-plus-`sy` over the 146 Exp 40 findings; the Codex capability-mismatch; the Stage-6 calibrator. MIXED — the Stage-6 calibrator is G3 and is CLOSED at `plan:806`. The rest I could not confirm either way.
60. The 3 decisions with the founder. `RECOVERY.md:42`, mirrored at `resources/ONBOARDING.md:20`: falsifier supply; the absolute-path ruling; one run writing two log directories. NEEDS FOUNDER. Note that the third has had its premise corrected — see entry 114.
61. The `rs` definition names `ACTION_QUEUE.md` and `QWERTY_CHECKPOINT.md`. `RECOVERY.md:40` and `plan:92` both flag it. VERIFIED: `ls ACTION_QUEUE.md QWERTY_CHECKPOINT.md` returns "No such file or directory" for both. Small doc fix in 3 places (`.claude/CLAUDE.md`, `resources/SHORTCUTS.md`, `~/.claude/CLAUDE.md`).
62. Regenerate or supersede the SV:PENDING region. `RECOVERY.md:1461-3060`. Its newest block is 98 days old and its 2026-05-17 status line was FALSE for 110 days before being corrected in place on 2026-09-05 (`RECOVERY.md:1531`), which is the failure mode this entry exists to prevent recurring. Small-medium.

=== GROUP H. docs/CURRENT_STATE.md (1 item) ===

63. Regenerate `docs/CURRENT_STATE.md`. It records NO outstanding work — it is a generated state snapshot. It is stale in 3 ways: "Generated: 8 September 2026 02:14 BST" (:3); parent commit `2230744` (:21) against a current HEAD of `9e3dfe9`; and "Latest Experiment: exp55_v3_control (#55), Status: INCOMPLETE" (:40-41) when the Exp 45 simulated run has since finished (4 rounds, 61 findings, `HALTED_IRREDUCIBLE_QUEUE_ALARM`, per `plan:84`). The file's own header at :9-18 warns it cannot describe the commit that carries it, so part of this is by design; the experiment field is not. Small — it regenerates under `sv`.

=== GROUP I. MEMORY.md AND THE RUNWAY MEMORY POINTER (5 items) ===

64. `exp49_dedup`. `memory/cdsfl_runway_2026-08-18.md:34` and `runway:313`: "DEFERRED by unanimous panel advice — premature until Stage 1 and 2 land". Deferred, not cancelled. BLOCKED on Stages 1 and 2.
65. Build the control that would settle the counterfactual-repair objection: a target with 2 known distinct defects sharing a plausible common repair. `memory/cdsfl_runway_2026-08-18.md:43-51`. Explicitly "unresolved and not blocking". Medium.
66. Full live re-run of exp44 through exp49 with the fixes in place. `memory/cdsfl_runway_2026-08-18.md:53-56`: "HELD IN RESERVE. Founder decision 2026-08-18: hold unless the Stage 1 replay throws up something replay cannot account for." RULED (hold). BLOCKED on the Stage 1 replay outcome. Large.
67. Secure the `exp39-experimental` bundle. MEMORY.md index entry "ARCHIVE LOCATION + DECRYPTION — ONE COPY SYSTEM-WIDE, unversioned on the Desktop"; detail at `runway:727` (0C.18, MEDIUM): 676 commits, single copy at `~/Desktop/CDSFL_archive/exp39-experimental-2026-08-17.bundle.enc`, 86.8 MB. Medium. Cheaper safeguard at entry 122.
68. Correct MEMORY.md's Bugzilla entry. It reads "EXTEND is read by nothing". VERIFIED PARTLY OUT OF DATE: `bench/reference_runner_v3.py:3166-3173` now collects EXTEND verdicts into `entry["extensions"]` and `entry["extension_count"]`. The surrounding comment at :3160-3165 is explicit that they are "Recorded, never gating", so the gating half of the claim stands and the reading half does not. Small doc fix.

=== GROUP J. THE CANONICAL RUNWAY (43 items) ===

`experimental_notes/RUNWAY_to_BR2_2026-08-18.md`, reached from source 5.

Nine decisions, `runway:68-78`:
69. Decision 1 — discrimination gate: block, label, or retry. `runway:70`. Recommendation "retry then block". Blocks the fix experiment and every future run. NEEDS RULING.
70. Decision 5 — redesign exp50 and exp51 before running. `runway:74`. Recommendation redesign, because of the same TRUE/FALSE pairing that contaminated exp48 and exp49. NEEDS RULING. Blocks entries 47 and 48.
71. Decision 6 — retire the load balancer, and the capped shakedown at `runway:312` (4.3). `runway:75`. NEEDS RULING. The measurement that would satisfy the removal half of `additive-standard` is stated on the same line: "never ran outside its own tests, reports impossible allocations as successes, self-description false 4.5 months".
72. Decision 7 — withdraw the claim that a survived-falsification ledger exists. `runway:76`: "verified NOT read by the runner". Small doc fix.
73. Decision 8 — do not sign the exp46 pre-registration draft. `runway:77`. Blocks the exp46 re-run, which is already held.
74. Decision 9 — `.env` quoting plus Zenodo token rotation. `runway:78`: "needs the founder's own hands; open 3 days" as written on 2026-08-18, so 22 days as of today. NEEDS FOUNDER. Small.

The 6-item list at `runway:133-140`:
75. Feed the in-runner discrimination control. `runway:135`. "the corrected copy is one apply away".
76. Re-grade the archive: stamp all 263 scored findings with their discrimination outcome. `runway:136`. Medium.
77. Examine the 67 NO_APPLICABLE_FIX and 30 INDETERMINATE_ERROR — a quarter of the population could not be scored at all. `runway:137`. Medium.
78. FW.5 — wire counterfactual repair to the merge site. `runway:138` and `runway:695`, where it is called "highest priority of these" and "Until it lands, NO code path writes MERGED at all". The fix is scoped as one argument, not an architecture change: `target_path` is already in scope at the calling function. Small-medium.
79. Let ERROR / UNTOOLABLE write a terminal status (4 of 24, all escalated). `runway:139`. "small, cheap".
80. `null_perturbation_control.py` needs `--dry-run` — it overwrote its own committed result on 22 August. `runway:140`. Small.

Stage 1, accounting repairs, zero dispatch:
81. 1.6 MERGED semantics — make it fold, or stop telling models it folds. `runway:264`. TODO.
82. 1.7 REPLAY exp44 through exp49 through the repaired accounting. `runway:265`. TODO. Medium.
83. 1.8 Promote the churn-detector floor from shadow to gating. `runway:267`. BLOCKED — "promotion needs clean data from the exp46 re-run", which is held.

Stage 2, the behavioural fix, needs one live run:
84. 2.1 Remove or repair the immune duplicate auto-reject. `runway:281`. TODO. Regression dated 12 April 2026.
85. 2.2 Preserve tool verdicts through synthesis. `runway:282`. TODO.
86. 2.3 Validate on ONE live run, exp50 physics. `runway:283`. TODO. BLOCKED on entry 47 and hence on Decision 5.

Stage 4:
87. A third Exp 55 run. `runway:310`: "A third run has not been attempted." Medium.
88. 4.2 exp53 re-run on the new clean target. `runway:311`. PROPOSED.

Stage 4B, the BR2 bridge, immediately before BR2:
89. 4B.2 Reconcile the one off-schema task to the 26-task schema. `runway:352`. Zero cost. Small.
90. 4B.3 Wire `reference_runner_v3` to the frontier schema; decide how `verification_method` maps onto the falsifier gate. `runway:353`. Zero dispatch. Medium.
91. 4B.4 C5 — dry-run all 27 for tool availability, graceful degradation and answer leakage. `runway:354`: "In the 8 April plan, never done." Medium.
92. 4B.5 Live burn-in on ONE BR2 task. `runway:355`. Costs 1 BR2 task. Medium.
93. 4B.6 Audit the 27 targets for prose documents that print fenced code listings. `runway:356`. Founder ruling 2026-08-30. Small-medium.
94. 4B.8 Vault the seeded pairs for the cell build-out exams. `runway:358`. Founder verbatim: "The seeded pairs from the upcoming cell build out exams on the runway have not yet been vaulted as far as I know. But this is not a blocker to the simulated run. It is easily fixable after this run." RULED, scheduled after the run. Small.

Stages 5 through 7, all after BR2:
95. Stage 5 — the reviewer reproduction pack. `runway:386-456`. The asset largely exists and is signposted nowhere (`runway:413-431` lists 8 reproducing scripts). Large.
96. Stage 6 — outreach. `runway:458-517`. Includes reordering the ladder and not opening with Hinton. Large.
97. Stage 7 — the documentation close, which cannot happen before PoC final. `runway:519-626`, including the 2026-08-24 coupling at :525 that "will rot if nothing watches it", and the list of what must be revisited at :553-559. Large.

Future work, `runway:687-693` and :810-813:
98. FW.1 — the missing epistemic state: a finding that was RIGHT about a target that was WRONG. `runway:689`. NOT BUILT. Described as cheap. Founder ruled the Bugzilla structural fixes back in scope on 2026-08-20.
99. FW.2 — structural keying of claims rather than location-only keying. `runway:690`. NOT BUILT. BLOCKED on enforced structured output.
100. FW.3 — fingerprinting (MinHash/SimHash/LSH) scoped to the ouroboros literature cell. `runway:691`. NOT BUILT.
101. FW.4 — the discussion-board layer. `runway:692`. DEFERRED BY DECISION (founder, 2026-08-20), explicitly still wanted.
102. FW.7 — severity is a vote, not a tool. `runway:813`. **NO LONGER NEEDS THE FOUNDER: RULED 2026-09-06 22:15 and BUILT 2026-09-07.** He rejected removal and the rubric swap and ordered worked proofs. The rubric agrees with the number no better than chance, kappa = -0.0227, Fisher p = 0.78. `bench/dm/_rk_proof.py`, pinned by `test_severity_proof_2026-09-07.py`. This record predates the ruling and is annotated rather than rewritten.

Stage 0C, the open rows at `runway:720-790`:
103. 0C.9 — confinement of REAL runs. `runway:723`. Priority HIGH. Half done: closed for simulated runs by sandboxing, open for real runs. The row states plainly "35 IS THEREFORE ONLY HALF DONE" and that the remaining half "is a behavioural change to live experiments and is held for panel review".
104. 0C.13 — panel independence is unverified; between-model variance measured as zero after noise correction. `runway:724`. HIGH. Marked "Unverified by me".
105. 0C.14 — the discrimination-control evidence base is 84 of 95 simulated. `runway:725`. HIGH. Argues for routing the control through a real run.
106. 0C.18 — the exp39 bundle single point of failure. `runway:727`. MEDIUM. [Same item as entry 67.]
107. 0C.19 — the class is open: no sweep for other assertions that compare a derived document against its generator rather than against the source. `runway:729`. HIGH, "cheap to sweep, and it silently voids a DERIVED claim".
108. 0C.19a — 974 typed `file.py:NNNN` citations, none checkable as written. `runway:728`. MEDIUM.
109. 0C.21 — nothing checks that every test file in the tree is reachable by the suite's collection roots. `runway:731`: "The class is open". Small.
110. 0C.62 — `rungs_with_conditions` is not sound as shipped and has no production caller. `runway:785`. UNCERTAIN: I grepped the whole repository and the identifier appears in exactly 1 file, `experimental_notes/RUNWAY_to_BR2_2026-08-18.md` itself. The code it describes does not exist under that name today. Either it was removed or renamed; I could not establish which, and the row should not be actioned until that is settled.
111. Whether BR2 is still a valid blind experiment. `bench/tests/test_br2_keys_are_split_out_2026-08-27.py` docstring: "all 27 answer-bearing files have been on the PUBLIC GitHub repository since 2026-03-18 -- 162 days. Splitting them stops the exposure growing; it does not reverse it. Whether BR2 is still a valid blind experiment on these tasks is a founder decision and it is open." NEEDS FOUNDER. This gates the whole of BR2.

=== GROUP K. THE MORNING REPORT OF 2026-09-09 (14 items) ===

`experimental_notes/Morning_Report_2026-09-09.md`, committed `57d5a0e` at 08:16 today. Its own line 9 states: "Nothing in this report has been implemented. It is a discussion document." It is the newest verification pass and it corrects 4 claims the other sources still assert.

112. Make the escalation doctrine read "broken machinery OR MISCONFIGURATION or both", and point at where the fault might lie. `Morning_Report:45`. RULED by the founder on 2026-09-08, recorded at `resources/ONBOARDING.md:18`. VERIFIED BY ME: `grep -c -i misconfigur` returns 0 for all 5 live sites — `docs/GLOSSARY.md`, `bench/reference_runner_v3.py`, `scripts/hil_escalation_by_run.py`, `resources/RECOVERY.md`, `experimental_notes/CDSFL_Agent_Operational_Plan.md` — and 1 for `resources/ONBOARDING.md`, where the ruling sits unactioned. Small.
113. Routing and the post-convergence sweep are disabled in every exp56 config: deliberate control, or omission? `Morning_Report:35`, :70. NEEDS FOUNDER RULING. VERIFIED BY ME: all 3 files under `bench/exp56_configs/` carry `"routing_enabled": false` and `"post_convergence_sweep_rounds": 0`. Small to fix, but the ruling has to come first.
114. `ExperimentConfig.logs_dir` is written by the simulated launcher and read 0 times by the runner, which mints its own path. `Morning_Report:37`. This corrects the "one run, two directories" account at `plan:94` and `RECOVERY.md:42`, whose premise was wrong. PARTIALLY VERIFIED: `bench/tools/run_simulated_experiment.py:222` does construct `R.ExperimentConfig(models=models, logs_dir=str(logs), ...)`; a bare grep for `logs_dir` in `bench/reference_runner_v3.py` returns 47 occurrences, so the "read 0 times" claim is specific to that field and I did not independently confirm it. Small-medium.
115. Widen the intake parser so it stops dropping FALSIFIER blocks. `Morning_Report:39`: 26 of 69 recovered across the run (Wilson [27.18%, 49.48%]) and 1 of 9 in the round that halted. This SUPERSEDES the falsifier-supply diagnosis at `plan:84` and `RECOVERY.md:32` as the dominant cause. Symbol located: `_FALSIFIER_BLOCK_RE` at `bench/runner_core.py:1165`, used at :1196. PROPOSED, not built. Medium. Named first in the recommended order.
116. One shared path-delimited predicate for the 6 remaining bounded traversals, 1 of them wired to a suite ratchet. `Morning_Report:41`. PROPOSED. Medium.
117. Stop reasons: a 3-line fallback immediately before `signal_complete()`. `Morning_Report:51`. Set on only 2 of 8 exit paths today. Small.
118. Derive the watchdog budget from the retry budget: `timeout * 3` truncates the configured `max_retries` for 4 of 5 seats, and `max_retries` appears 0 times in the runner. `Morning_Report:53`. PROPOSED. Medium.
119. Notes vagueness remediation: 1158 findings across 217 of 373 notes (58.18%, Wilson [53.11%, 63.07%]), of which 535 are the unnamed-subject class. `Morning_Report:55`, :73. NEEDS A SCOPE RULING — "1158 findings is a programme, not a task ... all notes, or only those a reader would reach". Large.
120. C0050, the single residual human-queue item at severity 0.9. `Morning_Report:57`: "It does not meet any reasonable reading of computationally irreducible. The exit is a recorded human ruling rather than new measurement." NEEDS FOUNDER. Small.
121. `bench/experiment_11_orchestrator.py:1442` sets tools to none unconditionally for the DeepSeek route. `Morning_Report:61`. Small.
122. Create a durable tag on `exp39-experimental` before any deletion. `Morning_Report:63`: 1 command pins all 865 orphan-candidate objects without pushing anything. Small. This is the cheapest safeguard for entries 52 and 67.
123. Commit a script that reproduces the "20 of 21 falsifiers reproduce against an earlier stored version" figure. `Morning_Report:65`: it exists only as prose at `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:253` and as a code comment at `scripts/adjudicate_by_repair.py:270`. This is the `measured-rate-travels-with-its-script` shape, and the figure is the sole evidence for the standing "do not delete exp39-experimental" ruling. Medium.
124. State what "simplest sufficient additive" is taken to mean in this project, for correction, before the panel brief is written. `Morning_Report:72`. Small, and it gates the panel dispatch.
125. Order of work. `Morning_Report:71`. NEEDS FOUNDER. The recommendation on file: falsifier supply first, then the doctrine wording, then the two-directory field, then the 6 remaining traversals.

=== WHAT THE RECORD SHOWS AS CLOSED (24 groups) ===

These appear in the sources as pointers or items and are DONE. They should not be re-opened.

1. The push of the unpushed commits. `plan:64`, `Morning_Report:69`. Closed 2026-09-09 11:55:48 BST — `git reflog show origin/main` reads "update by push" at `9e3dfe9`.
2. The prose-adaptation MUST list A1 through A10. `queue:19-28`, closure stated at `queue:57`.
3. Section B, "Already fixed today", 13 items. `queue:89-109`.
4. B3, ruff's success message counted as a lint violation. `queue:126-150`, closed at commit `669ac71` per `queue:162`.
5. B4's overnight batch: routing ladder made target-aware (the blocking item), exp53 config note, residual sweep on halt, panel briefing, A9, A10. `queue:156-164`.
6. B5, Wolfram credential retirement and doc corrections. `queue:203-211`, "DONE 2026-08-03 21:48 — Wolfram fully closed out."
7. B6, the "wasteful re-dispatch". `queue:292-313` — REFUTED by measurement; 6 of 36 findings were rescued by the repeat, so no fix is wanted.
8. B8, pipeline proven end to end by the simulated bench. `queue:338-348`, closing "the everything-is-unit-tested-only gap".
9. B9, provenance relabelling of the simulated panel to SIM-A through SIM-E. `queue:365-372`.
10. Gap items G1, G2, G3, G4, G5, G9. `plan:804-808`, `plan:812`.
11. Phases A, B, C, D and E of the 22 April 2026 shift, 25 checked items. `plan:824-861`.
12. The 133 similarity pairs. `runway:72` proposed a stratified sample of 30; `plan:204` records RULING A: "ZERO of the 133 similarity pairs are HIL-irreducible", adjudicated 2026-08-18.
13. Section D item 3, reseeding the 3 exposed exams. `queue:260-262` — founder judged the exposure overstated and elected to move on. A deliberate decision, not an oversight.
14. Section D item 4, the archive delta. `queue:263-264` — 127 genuine records preserved, the rest discarded.
15. Runway 4B.1, splitting `ground_truth_notes` out of all 27 tasks. `runway:351`; confirmed by the docstring of `bench/tests/test_br2_keys_are_split_out_2026-08-27.py`: 14,528 characters across 27 files, moved outside any git tree on 2026-08-27.
16. Runway 4B.7, Gemini's tool path. `runway:357` — "CLOSED 2026-08-31", verified with 1 paid call rather than by inspection.
17. Decision 35, panel sandboxing, for SIMULATED runs. `plan:156` — proved by execution at commit `132af1b`. The real-run half remains open as entry 103.
18. Stage 0C rows 0C.1 through 0C.7, 0C.10 through 0C.12, 0C.15 through 0C.17. `runway:705-717`.
19. The compaction-marker fix — `--record-restore` now required. `plan:88`, 10 tests.
20. The 900-second seat cap, raised to 3600 at source. `plan:112`.
21. The exp39 remote question: `git ls-remote --heads origin` returns only `main`. `plan:122`.
22. The drift-caller scan scope, extracted to a callable and mutation-verified in both directions. `plan:74`.
23. The memory-ledger and memory-index repairs, plus the citation path fix. HEAD commit `9e3dfe9`; suite 5472 passed, 4 skipped, 0 failed.
24. The 2026-05-17 "AWAITING FOUNDER RULING" status line, false for 110 days. `RECOVERY.md:1531` — corrected 2026-09-05; the substantive half that remained is entry 54.

=== THREE RECORD DEFECTS FOUND WHILE BUILDING THIS LIST ===

Not work items in themselves, but they will mislead the next agent.

(a) `OUTSTANDING_QUEUE_to_BR2.md:73-75` asserts A9 and A10 are "Neither is started" and that all 8 prose configs fail the 3/3 preflight, both refuted elsewhere in the same file (:27-28, :59-65).
(b) `CDSFL_Agent_Operational_Plan.md:810` lists G7 as "Scheduled" while `:226` records it closed as dead code by the no-voting ruling.
(c) The `exp39-experimental` disposition is recorded 3 different ways across `plan:122`, `RECOVERY.md:68` and `ONBOARDING.md:18`.

### Does the record support the founder's framing?

The prompt's framing was that "many pointers are historical and their work is done". The record SUPPORTS this substantially and CONTRADICTS it in 2 specific places.

SUPPORTED. The 22 April 2026 shift is fully checked off apart from Phase F — its own header at CDSFL_Agent_Operational_Plan.md:816 reads "COMPLETED HISTORICAL SHIFT, NOT THE RESUME POINT", and Phases A through E carry 25 checked boxes at :824-861. Section A of the outstanding queue is closed at OUTSTANDING_QUEUE_to_BR2.md:57. Section B lists 13 completed repairs at :89-109. G1, G2, G3, G4, G5 and G9 are CLOSED at plan:804-812. The 133 similarity pairs, still shown as an open decision needing about an hour of human work at RUNWAY_to_BR2_2026-08-18.md:72, were adjudicated on 2026-08-18 and ruled at plan:204. And the single largest currently-recorded blocker — the unpushed commits at plan:64 and Morning_Report_2026-09-09.md:69 — closed at 11:55:48 this morning, which the reflog proves and no document yet records. 24 closed groups in all.

CONTRADICTED, first direction. Some genuinely historical pointers still carry live work, so "historical" cannot be used as a filter. Phase F dates from 22 April 2026 and is open. The newest block in RECOVERY.md's PENDING region is dated 2026-06-03, 98 days ago, and 6 of its items are still open — including architecture (B) at :1488 and the CX2 wiring at :1479. Item #16, recorded on 2026-09-07 at plan:160, is described at CLOSING_2026-09-06.md:43 as "the largest single piece of work remaining".

CONTRADICTED, second direction, and this is the sharper one. At least 3 historical pointers are not merely stale but actively false, and 2 of them would waste work if believed. OUTSTANDING_QUEUE_to_BR2.md:73-75 says of A9 and A10 "Neither is started" when the same file records both DONE at :27-28 and measures the accompanying 3-of-3 preflight claim FALSE at :59-65. plan:810 lists G7 as Scheduled when plan:226 records it closed as dead code. And the exp39-experimental disposition is recorded 3 incompatible ways across plan:122 ("the 2026-08-23 instruction says KEEP"), RECOVERY.md:68 ("the founder stated on 2026-09-08 that it is fully retired") and ONBOARDING.md:18 ("to be adjudicated by Fable and CC2 against a sandboxed copy before any deletion"). So the safe reading is not "historical means done" but "every pointer needs its status re-derived from the artefact", which is exactly what this morning's verification pass did and what produced 4 corrections in one sitting.

### Recommendation (not implemented)

I have implemented nothing and changed nothing. What I recommend, in order.

1. Record the push as done. plan:64 and Morning_Report_2026-09-09.md:69 both still name it as the top founder decision, and the reflog shows it closed at 11:55:48 today. Leaving it in place means the next agent re-raises a closed item as the headline blocker.

2. Put the 121 open items into 1 place. They are currently spread across 6 files, and the 2 that are supposed to be the live queue are the 2 that have drifted furthest: OUTSTANDING_QUEUE_to_BR2.md was last touched 2026-08-27 and contains an internal contradiction about A9 and A10, and the RECOVERY.md pending region's newest block is 98 days old. The operational plan's own recovery card at plan:615 says "READ experimental_notes/OUTSTANDING_QUEUE_to_BR2.md FIRST — it is the live queue", so that file is where the consolidation belongs, or the card should be changed to point somewhere that is actually current. Doing this before the next compaction is the whole point of the inventory.

3. Fix the 3 record defects listed at the end of the findings, and the stale rs definition (entry 61). All 4 are small, all 4 are verified against the artefact, and each one is capable of sending a future agent to redo finished work or to skip live work.

4. Take the 17 founder decisions to the founder as 1 list rather than as they surface. They are entries 18, 19, 33, 46, 52, 55, 60, 69, 70, 71, 74, 102, 111, 113, 119, 120 and 125. Several are cheap and 1 is time-critical: the Wolfram Engine licence at plan:220 expires on 2026-09-11, 2 days from today.

5. Then execute in the order the founder's own recommendation names at Morning_Report_2026-09-09.md:71 — falsifier supply first, because it is the halt cause and everything downstream depends on a run that can finish; then the doctrine wording, which is cheap and already ruled; then the two-directory field; then the 6 remaining traversals. That ordering is a recommendation on file, not a ruling, and item 3 of the same list asks the founder to confirm it.

6. Note the dependency spine, because it explains why so much is blocked and not merely deferred. The simulated run (entry 19, held for the founder) gates 6 study items and 4 runway items. The answer-key sealing (entry 18, needs his passphrase) gates the simulated run. Exp 53 (entry 46, needs a restart-or-resume ruling) gates entry 12. Decision 5 (entry 70) gates exp50 and exp51, which gate Stage 2.3, which gates the whole behavioural fix. And BR2's blind validity (entry 111) gates BR2 itself. Roughly a quarter of the open list moves the moment 4 decisions are taken.

### What could not be established

Six things I could not establish.

1. Entry 42, the "falsifier transport truncation plus 4 skipped tests" at OUTSTANDING_QUEUE_to_BR2.md:179. The 4 tests skipped in today's suite are a different set — the HEAD commit message for 9e3dfe9 identifies them as all 4 living in test_br2_keys_are_split_out_2026-08-27.py, skipping because the key store is off-machine. Whether the 2026-08 skips were fixed or merely displaced by a changing suite, I do not know.

2. Entry 55, the HIL materiality confirmation on C0015 and C0017 at RECOVERY.md:1521. CLOSING_2026-09-06.md:39 reports that the materiality review's stated population does not reproduce against the run reports. The item may therefore be moot rather than open. I did not re-derive the population.

3. Entry 59, the carried-forward backlog at RECOVERY.md:1523. Of its 7 sub-items I confirmed exactly 1 — the Stage-6 calibrator, which is G3 and is CLOSED at plan:806. The other 6 I could neither confirm nor refute, and the block they sit in is 98 days old.

4. Entry 110, runway row 0C.62. The identifier rungs_with_conditions appears in exactly 1 file repository-wide, the runway note itself. The code the row describes does not exist under that name today. Removed, renamed, or never merged — I could not tell, and the row should not be actioned until someone can.

5. Entry 114. The Morning Report's claim that the runner reads ExperimentConfig.logs_dir 0 times is narrower than a grep can settle: a bare grep for logs_dir in bench/reference_runner_v3.py returns 47 occurrences. I confirmed the write side at bench/tools/run_simulated_experiment.py:222 but not the read side.

6. Entry 34, "remaining panel review of the last 24 hours" at plan:160, written on 2026-09-07. Two days of work have landed since. Whether anything of that review remains outstanding I could not determine.

One boundary worth stating plainly. Sizes are my estimate from the described work, not measured, and the record itself contains no effort figures. Where a source gave its own cost — "zero, offline" for runway 4B.1 and 4B.2, "small, cheap" for the ERROR/UNTOOLABLE status, "~1 hour" for the similarity sample — I have used the source's word rather than my own.

### Evidence

- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:13-60 — the FOUNDER RULINGS OF 2026-09-06 section; 19 scheduled items across 4 timing buckets plus 2 held for the founder's return
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:64 — current resume pointer, claims 10 commits unpushed and the push blocked; refuted by the reflog below
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:78 — 'Fix candidate, not yet built: the monitor should terminate when its run's process does'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:626-633 — 'Phase F is the only part of that 22 April 2026 shift still open', F1/F2/F3 unchecked
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:804-812 — G1-G5 and G9 CLOSED, G6/G7/G8 Scheduled
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:226 — 'DECISION 5 ANSWERED — G7's MERGE PATH IS DEAD CODE', contradicting :810
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:160 — 'STILL OPEN: #16 (17 fixes, 11 equipment, 4 containments — 90 code targets in scope, 43 exam targets blocked on the held keys)'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:174 — founder's notes 141 days stale, backfill authorised, NOT STARTED
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:196 — 'STILL GENUINELY OUTSTANDING: D6 disclosure measurement. D11 seat contrast.'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md:220 — '[VERIFY:current] LOCAL WOLFRAM ENGINE LICENCE EXPIRES 2026-09-11', which is 2 days from today
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:57 — 'THE MUST LIST IS CLOSED (A1-A10), 2026-08-01 23:35 BST'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:73-75 — stale text still saying A9/A10 'Neither is started', refuted at :27-28 and :59-65 of the same file
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:226-232 — section C: Exp 53 PAUSED, Exp 50/51/52 not started, BR2 not started
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:258-259 — 'DO NOT DELETE until the 107 commits are either merged non-destructively or deliberately declared redundant. Neither has happened.'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:279-281 — Codex system prompt injection 'Founder approved ... NOT BUILT'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:316-335 — B7, B2 deliberately not fixed, with the remedy written out
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/resources/RECOVERY.md:1461 and :3060 — SV:PENDING region delimiters; newest block inside is dated 2026-06-03
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/resources/RECOVERY.md:1519 — gamma-unification 'PENDING ... awaiting founder go-ahead', now superseded by the ruling at plan:36
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/resources/RECOVERY.md:1531 — the 110-day false status line, and 'The held-out-corpus or null-distribution half of (b) is STILL OPEN'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/resources/RECOVERY.md:40-42 — the stale rs definition and the 3 founder decisions
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/docs/CURRENT_STATE.md:3,21,40-41 — generated 2026-09-08 02:14, parent 2230744, latest experiment exp55 INCOMPLETE; records no outstanding work at all
- /Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_runway_2026-08-18.md:12-13 — points at experimental_notes/RUNWAY_to_BR2_2026-08-18.md as canonical
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:68-78 — the 9 decisions table
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:133-140 — the 6-item list including FW.5 and the null_perturbation --dry-run
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:264-267 — Stage 1 items 1.6 TODO, 1.7 TODO, 1.8 SHADOW
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:281-283 — Stage 2 items 2.1, 2.2, 2.3 all TODO
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:296-302 — exp50/51/52 BUILT NOT RUN; exp54 NOT BUILT
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:351-358 — Stage 4B items 4B.1 through 4B.8
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:689-695 — FW.1 through FW.5, FW.5 'highest priority of these'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/RUNWAY_to_BR2_2026-08-18.md:723-731 — open 0C rows 0C.9 (HIGH), 0C.13, 0C.14, 0C.18, 0C.19, 0C.19a, 0C.21
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Morning_Report_2026-09-09.md:35-41 — the 4 corrections to yesterday's claims
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Morning_Report_2026-09-09.md:45 — escalation doctrine ruling present in 1 place, absent from 5
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/experimental_notes/Morning_Report_2026-09-09.md:67-73 — the 5 decisions sitting with the founder
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v3.py:3160-3173 — EXTEND verdicts ARE now collected into entry['extensions'], contradicting MEMORY.md's 'EXTEND is read by nothing'
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/runner_core.py:1165,1196 — _FALSIFIER_BLOCK_RE, the symbol the intake-parser fix targets
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tools/run_simulated_experiment.py:222 — R.ExperimentConfig(models=models, logs_dir=str(logs), ...), the field the runner is said not to read
- /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_br2_keys_are_split_out_2026-08-27.py:1-23 — 4B.1 done 2026-08-27; BR2 blind-validity after 162 days of public exposure is an open founder decision
- git reflog show origin/main --date=iso — '9e3dfe9 refs/remotes/origin/main@{2026-09-09 11:55:48 +0100}: update by push'; git rev-list --count origin/main..HEAD returns 0
- grep -c -i misconfigur over the 5 live doctrine sites — 0 in every one; 1 only in resources/ONBOARDING.md:18 where the ruling sits unactioned
- grep routing_enabled / post_convergence_sweep_rounds over bench/exp56_configs/*.json — 3 of 3 files carry false and 0
- ls bench/logs | grep exp5 — no exp50, exp51, exp52 or exp54 run directories exist; exp53 has 2 and exp55 has 2
- ls -d bench/exp54* — no such directory, confirming exp54 is NOT BUILT
- ls ACTION_QUEUE.md QWERTY_CHECKPOINT.md — both 'No such file or directory', confirming the stale rs definition
- git rev-list --count --since=2026-04-18 HEAD — 557 commits since the last founder's-notes entry; docs/FOUNDERS_NOTES.md:721 is the last dated section, '17-18 April 2026'
- grep -rl rungs_with_conditions . — matches only experimental_notes/RUNWAY_to_BR2_2026-08-18.md; the code that row describes exists nowhere under that name

Written under CDSFL note standard v1.7 (26 August 2026).