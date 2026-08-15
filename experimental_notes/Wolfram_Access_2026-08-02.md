# Wolfram access: what changed, and what to do about it

> **SUPERSEDED IN PART — CORRECTION 2026-08-02 12:05 BST.** The recommendation
> below ("keep paying, add alongside, migrate at leisure") is WRONG. It was written
> before the founder's actual Wolfram emails were available. Two premises are refuted
> by them:
>
> 1. **There is nothing to keep paying.** Wolfram cancelled the billing themselves:
>    *"The recurring payments for your subscription will stop immediately. You will
>    not be charged again."* The £4/month had already ended, at Wolfram's initiative.
> 2. **A hard cutoff date exists and has passed.** Two emails state: *"Previously
>    generated API keys will no longer function after July 31, 2026."* Today is
>    2 August — two days past.
>
> **Measured now:** the bridge still answered correctly at 11:58 today, so enforcement
> is lagging, not absent. That is borrowed time. The free endpoint is live (HTTP 200,
> `serverInfo.version 2026.07.24`, no credential requested).
>
> **Correct action: migrate now**, not "add alongside and compare over weeks". The
> comparison tests below remain worth running — after the migration, not before it.
>
> The error-as-success defect becomes MORE urgent: when enforcement catches up, an
> auth rejection arrives as a *successful* tool result whose text is an error string.
>
> What the research got right: it inferred the paid product's retirement from public
> evidence alone (subscribe URL redirects, service docs 404, support article redirects).
> What it could not find was the announcement — because it was emailed, not published.
> The one open unknown it named, *"what your two notices actually say"*, is the one
> that inverted the recommendation.

2026-08-02 09:20 BST

Seven-agent research pass (four research strands, two adversarial skeptics, one synthesis),
plus local verification performed directly. Presented in full and unfiltered per standing
directive. Raw agent output: `Wolfram_Access_Research_RAW_2026-08-02.json` in this directory.

## Bottom line

Nothing you have is broken, and nothing is switching off on any date Wolfram has published — your Wolfram access was working this morning and the endpoints it calls are still live. The important correction is this: the GBP 4/month is not buying you a separate "API" alongside the bridge. The key in your .env and the key inside WolframLocalMCPBridge.app are byte-identical because they are one subscription, and that subscription is the only thing authorising the bridge, so cancelling would switch Wolfram off entirely rather than just save money. Wolfram's new free endpoint does run the same kernel, same licence class, same curated data and the same three tools — but it forgets everything between calls, and it kills any single calculation at about 30 seconds. So: add the free one alongside what you already have, prove it on your actual workload, and keep paying the GBP 4 while you do, because there is no documented way to buy the subscription back once it lapses.

## What the £4/month is actually buying

The GBP 4/month is buying bearer-token access to Wolfram's hosted MCP service at services.wolfram.com/api/mcp — which is exactly and only what WolframLocalMCPBridge.app calls. It is not a second, separate "API" purchase sitting beside the bridge; the identical SHA-256 on the two key names is because there is one product. An archived copy of the old product page (Wayback, 2026-03-16) describes it as a single 5 USD monthly plan with no tiers or overages, which is consistent with your GBP 4. Concretely, over and above what the free endpoint gives you, it buys three things: persistent session state between calls (measured — a definition set in one call survived to a later call on your bridge and vanished on the free one), a longer per-call ceiling (measured at 45 seconds succeeding on yours versus a hard 504 at roughly 30.7 seconds on the free one), and possibly a richer WolframContext that merges two Wolfram sources rather than one (confirmed in the bridge binary, unconfirmed on the free endpoint). CAN IT BE DROPPED? Technically yes — the free endpoint runs the same kernel build, the same Professional licence class, on the same production fleet, with the same three tools and full curated data. But it should NOT be dropped yet, and quite possibly not at all. Wolfram publishes no repurchase path, no refunds, and no notice about what happens to existing subscribers. Set against a project funded from borrowed money where a lost experimental run costs far more than GBP 48/year, the subscription is currently functioning as cheap insurance rather than as waste. Note also that your codebase reads WOLFRAM_API_KEY nowhere — three textual mentions, all documentation or an env template, zero actual reads — so cancelling looks free from the code side. It is not: it kills the bridge, and it turns those three doc mentions into misleading instructions pointing at a product a third party could no longer buy.

## Capability risk

Two measured losses if you moved to the free endpoint, and one that has not fired yet on your current one. FIRST, statelessness. The free kernel forgets definitions between calls — this is stated in its own tool description and confirmed by direct probe. The danger is not that it errors; it is that a chained verification returns a syntactically valid but wrong expression, which a verdict-reader can score as 'not falsified'. For a falsification pipeline that is the worst possible failure shape, and this project has been bitten by that exact class of bug before. SECOND, a ~30-second hard ceiling enforced by an HTTP gateway, undocumented anywhere, which arrives as a transport error rather than a Wolfram abort — so an automated runner is most likely to log it as flakiness and move on. THIRD, and this one applies to your CURRENT setup today: reading the bridge binary shows every failure path returns a normal successful MCP result whose text is an error string. If your subscription ever lapsed or the key were revoked, the tool would keep 'succeeding' and hand back '[HTTP Error 401]' to be ingested as evidence. The bridge is also frozen at 2026-02-17 with no updater, hardcoded to the paid endpoint with no way to repoint it, carrying its own five-month-old certificate trust store — so a certificate rotation or protocol bump on Wolfram's side would break it silently and permanently. Against all that, the reassuring part is real: the free kernel reports the same version, same Professional licence, same non-expiring licence date and a neighbouring machine on the same cloud fleet, and returned correct results across Integrate, DSolve, Series, 60-digit N, Sum, Solve, FullSimplify, ElementData, ChemicalData, IsotopeData, EntityValue, GeoDistance and FinancialData. The symbolic-maths cross-verification workload that CDSFL actually runs is not at risk on either path.

## Steps


**1. Keep paying the GBP 4/month for now. Change nothing about the subscription, the key, or the bridge app.**

*Why:* The key in .env and the bridge's WOLFRAM_AUTH_KEY are the same credential, and it is a bearer token checked on Wolfram's servers. If the subscription lapses the bridge does not degrade — it starts returning error text instead of maths. Until a replacement is proven on your real work, this GBP 4 is what is holding the capability up.  
*Reversible:* yes


**2. Add the free endpoint as a SECOND, separately named MCP server, leaving the existing Wolfram entry completely untouched. For Claude Code: claude mcp add --transport http wolfram-cloud https://agenttools.wolfram.com/mcp — for Claude Desktop, a new entry in claude_desktop_config.json with just a url field and no env block. I can do this for you; it needs no account, no password and no key.**

*Why:* Both servers coexist without conflict under different names. This gives you a working spare before you need one, and lets you compare the two on identical queries rather than guessing. It costs you three extra tool definitions in context during the comparison period — small, and temporary.  
*Reversible:* yes


**3. Run the same WolframContext query against both servers and compare the two outputs side by side. Look specifically for whether the free one returns TWO sections separated by a ====== marker, labelled Wolfram Alpha and Wolfram Language.**

*Why:* Reading the bridge binary showed its WolframContext fires two separate Wolfram endpoints concurrently and merges the results. If the free endpoint returns only one source, your documentation search quietly halves — no error, just less. This is the single most plausible hidden capability loss and it is directly testable. I can run this for you.  
*Reversible:* yes


**4. Time your real Wolfram verification calls over one bench round. Flag anything that takes more than about 25 seconds.**

*Why:* The free endpoint was measured returning HTTP 504 at roughly 30.7 seconds, three times, and raising timeConstraint does not help because the gateway cuts first. Your current path completed a 45-second call. Hard FullSimplify, large DSolve and high-precision NIntegrate can exceed 30 seconds. You need to know whether that ceiling touches your actual workload or is theoretical. I can run this for you.  
*Reversible:* yes


**5. Check whether any CDSFL verification defines something in one Wolfram call and uses it in a later one (a helper function, $Assumptions, a stored expression).**

*Why:* Your current bridge keeps session state; the free endpoint explicitly does not. For one-shot cross-checks against SymPy this is irrelevant. If anything in the pipeline does chain calls, that work would silently return well-formed but wrong answers on the free endpoint. I can audit this for you.  
*Reversible:* yes


**6. Add a guard that treats any Wolfram tool result beginning with [HTTP Error, [Timeout after, or [Error] as a FAILED verification rather than as evidence.**

*Why:* This matters right now, independently of any switch. The bridge's own code returns every failure — auth rejection, timeout, network fault — as a SUCCESSFUL tool result whose text is an error string. An unattended run would ingest '[HTTP Error 401]' as though it were a Wolfram answer. This project has already lost a convergence to exactly that class of defect (the NOT FALSIFIED substring bug). I can write this for you.  
*Reversible:* yes


**7. Copy /Applications/WolframLocalMCPBridge.app and, if you still have it, the installer package, to external storage.**

*Why:* The app has no auto-updater and its English documentation and support articles now 404 or redirect to the free product. If you ever needed to reinstall it, the download may no longer be obtainable. A copy costs nothing and changes nothing. I can do this for you.  
*Reversible:* yes


**8. Read the two notices yourself and note the exact product name each one uses, and any date.**

*Why:* I could not find either notice published anywhere. If one of them names 'Wolfram MCP Service' with a cutoff date, that changes the timeline materially — it is currently the only unknown that could impose a deadline. This is your email; only you can look.  
*Reversible:* yes


**9. Log in to account.wolfram.com yourself and look at the subscription page and the developer API-keys page. Do not paste anything back to me — just read what product name is on the subscription and what the renewal date is.**

*Why:* This settles what you are actually paying for, and whether Wolfram has posted any subscriber-facing notice that is not on the public pages. It involves your account and password, so it must be you, not me.  
*Reversible:* yes


**10. ONLY after a complete bench run has finished clean on the free endpoint, and only if you actively want the money back, consider cancelling. Not before.**

*Why:* Wolfram states it does not offer refunds, the subscribe URL now redirects to the free product page, the old service documentation returns 404, and there is no published way to repurchase. Given you have said you would rather pay than lose capability, the honest answer is that cancelling has poor odds and small upside.  
*Reversible:* NO


## Do not


- Do not cancel the subscription now — including 'just to see if it still works'. Cancellation appears to be a one-way door: no refunds, no repurchase page, and the old product documentation is already gone.


- Do not delete, move, rename or modify /Applications/WolframLocalMCPBridge.app. It cannot update itself and may not be re-downloadable.


- Do not replace the existing Wolfram MCP server entry with the free one. Add a new entry alongside it under a different name. Replacing it means losing the working path the moment the new one misbehaves.


- Do not paste your Wolfram key into any configuration for agenttools.wolfram.com. That endpoint takes no authentication, and supplying a credential to something that does not use it is pure downside.


- Do not treat a Wolfram tool call that 'succeeded' as a verified result without checking the text. The bridge returns errors as successful results.


- Do not point an unattended overnight bench run at the free endpoint until it has been exercised under load. Wolfram publishes no rate limit at all — only the words 'limited personal use' and 'small-scale and casual use' — and there is no account, no ticket and no appeal route behind an anonymous endpoint.


- Do not buy Mathematica, Wolfram|One or a Wolfram Engine licence to get 'Wolfram Local MCP'. That is the only route to a genuinely local stateful kernel, and it costs orders of magnitude more than GBP 4/month to solve a problem you have not been shown to have.


- Do not let the old context-window worry drive this. The bridge is itself an MCP server exposing the same three tools, so switching is a swap, not an addition. Only the deliberate side-by-side period costs anything, and it is three extra tool definitions.


## Open unknowns


- Whether any usage limit exists on the free endpoint. Wolfram publishes no number anywhere — no requests per day, no quota, no throttle. Tellingly, the old PAID page carried a 'How is usage limited?' question and said usage was monitored to prevent abuse; that question was deleted rather than updated when the page became the free one. WHAT WOULD SETTLE IT: only running a full bench cycle through it and watching for throttling or blocks. Do not probe rate limits deliberately — that would itself be abuse.


- Whether an automated multi-agent research pipeline counts as the 'limited personal use' and 'small-scale and casual use' the free endpoint is offered for. Not defined on any page. WHAT WOULD SETTLE IT: asking Wolfram directly, in writing, describing the workload. That is worth doing before leaning on the free endpoint for published results.


- Whether the free endpoint's WolframContext returns both source streams or only one. Your bridge demonstrably merges WolframAlphaContext and WolframLanguageHints. WHAT WOULD SETTLE IT: one identical query run against both servers, diffed — about five minutes of work, and it is the cheapest high-value test on this list.


- Whether Wolfram is formally retiring the paid MCP Service, and what happens to existing subscribers. No deprecation notice, no migration plan, no cutoff date exists on any page. The evidence is circumstantial but consistent: the subscribe URL 301-redirects to the free product, the service documentation 404s, the support article for your exact Bridge setup redirects to the free article, one support article is stuck in a redirect loop, and the current product hub lists only Local, Cloud and Enterprise with no MCP Service and no Bridge. What survives is the German-locale copies. WHAT WOULD SETTLE IT: the two notices you received, and a direct question to Wolfram support.


- What your two notices actually say. I could not find either published anywhere, and could not match them to a specific announced change. WHAT WOULD SETTLE IT: you reading them and quoting the product name and any date.


- Whether the subscription remains purchasable at all, and what your renewal date is. WHAT WOULD SETTLE IT: your own account page. This is the input that decides how much time you have to run the comparison unhurried.


- The true per-call ceiling on your current paid path. It completed 45 seconds; a 110-second attempt hit the local MCP client's own timeout before the service's limit, so the honest statement is 'at least 45 seconds', not 'unlimited'. WHAT WOULD SETTLE IT: a bisect between 45 and 110 seconds with a raised client timeout.


- Whether the free endpoint is served at lower priority or a smaller share of the fleet than paid traffic. Invisible from inside the kernel — both report the same hardware. WHAT WOULD SETTLE IT: only sustained comparative latency measurement under load.


- Whether the ~30-second gateway cut is fixed policy or an incidental proxy setting. Consistent across three trials, documented nowhere, so it could move in either direction without notice. WHAT WOULD SETTLE IT: nothing published; re-measure periodically.


- The terms-of-use position, which you should read yourself rather than take my reading of. The Wolfram Cloud terms — the URL the free endpoint advertises in its own response header — prohibit using the Services to train AI models, prohibit systematic extraction or caching, and state the Services should not be used in conjunction with your AI-powered tools or services unless a separate licensing agreement is in place. Wolfram also reserves the right to change, discontinue or deprecate any Service with or without notice. Those terms are not specific to the free tier, so this is not a change — but CDSFL is an AI pipeline that writes Wolfram outputs into a persistent evidence ledger intended for publication, and that is your call to make, not mine. WHAT WOULD SETTLE IT: a direct licensing question to Wolfram, which would also resolve the 'personal use' question above in the same email.


- Whether a free Wolfram Engine for Developers licence qualifies for 'Wolfram Local MCP'. Wolfram's own page says 'Free with: Wolfram Engine'; another source insists a licensed Engine is required. Direct conflict, unresolved, and the documentation sub-page 404s. This is the only potential zero-cost route to a genuinely local, stateful, unlimited kernel, so it is worth resolving eventually — but not now, and not as part of this decision.


---

Written under CDSFL note standard v1.2 (14 May 2026).
