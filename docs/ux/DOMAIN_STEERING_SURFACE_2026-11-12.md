# How a run's domain is resolved: the steering surface and the vocabulary behind it

12 November 2026, 03:30 UTC

## Summary

A CDSFL run must know which domain it is in before it can judge anything, because the severity scale, the critical level and the expert encoding a seat receives are all properties of the domain rather than constants of the harness. Until this window nothing resolved the domain from the work: a command-line argument carried a hardcoded default, no code classified a domain from task content, and no archived run state recorded which domain had been used. This document specifies the surface that resolves it, and names the authoritative source of the vocabulary it resolves against. It covers the interaction only; the visual design remains the authoritative design brief's.

## 1. Why this is a user-interface question and not an internal one

The domain determines the consequence scale a finding is judged on. A clinical adverse-event grade of 3 and a software vulnerability score of 7.0 are both plain numbers carrying no units, so nothing in the arithmetic refuses to add them to 10.0: dimensional analysis has no purchase, because neither quantity carries a dimension to disagree about. The only thing that can refuse the comparison is the NAME of the scale, and a name has to come from somewhere. It can come from the researcher, from a proposal the researcher confirms, or from a conversation. All 3 are interface decisions.

## 2. The 2-sided design, and why conversation is the fallback rather than the default

Resolution runs in 3 tiers, in this order.

1. An explicit selection. The researcher picks a domain, and optionally a subdomain, from a list. This is the fast path and it is unambiguous.
2. A proposal. A pattern classifier reads the task text and PROPOSES a domain and subdomain, which the researcher confirms or overrides with 1 action. The classifier proposes; it never decides.
3. A conversation. Where the proposal is ambiguous, meaning the evidence does not separate 2 or more candidates, the steering surface asks. This is the only tier that costs the researcher a dialogue, and it is reached only when the cheaper 2 cannot settle the question.

The ordering is the design. A conversation-first interface would tax every run for the benefit of the minority of runs that are genuinely ambiguous, and a classifier-only interface would silently mis-route the ambiguous ones, which is the failure the project already measured: whole domains received a constraint box written for a different subject for 7 months, because a default was taken from the alphabetically first file in a directory.

## 3. The vocabulary is declared in 1 place, and this document does not copy it

The authoritative source is the domain manifest at `bench/cdsfl_registry/domain_manifest.toml`, read only through `bench/cdsfl_registry/domain_vocabulary.py`. It declares 10 top-level domains, each with exactly 4 subdomains, giving 40 subdomains in total, together with 15 domain aliases, 6 subdomain aliases and 11 deeper variants that resolve onto those 40.

The 40 subdomain names themselves are deliberately NOT reproduced here, and the figures above are given only so that a builder can tell at a glance whether a manifest it has loaded is the whole one. A document that copies a vocabulary becomes a second source of truth about it, and the 2 drift; this project has already recorded a case in which a stored verdict outvoted the live predicate it was derived from and went uncorrected for 9 days. A front-end build should read the manifest, not this file.

What a builder does need from this document is the SHAPE of an entry, because it constrains the interface:

- A domain declares its severity scale by name, its severity levels, its critical level, its default encoding and its encoding tier.
- 6 of the 10 domains declare no scale of their own, with a stated reason, and inherit the scale of the application domain. Pure mathematics is the clearest case: a reversed inequality in a convergence proof is an epistemic error, and the same reversed inequality in a fan-blade tolerance is a lethal one. The consequence belongs to the application, not to the form of the mistake.
- A subdomain maps a LABEL to a PATH. The label is what a person selects; the path is where the encoding file lives. The indirection is the load-bearing part: an encoding file can be renamed or moved without breaking a selector, a saved configuration or an archived run.

## 4. The run state must record what was resolved

A resolved domain that is not written down cannot be audited. Measured during this window: 0 of 67 archived run states record which domain the run used, so no archived result can be re-read against the scale it was judged on. The interface therefore has an obligation beyond resolving the domain, which is to persist it with the run, alongside how it was resolved: selected, proposed-and-confirmed, or settled in conversation.

That third field matters for the research question rather than for the interface. A result reached after a conversation carries a different provenance from a result reached by a researcher's own selection, and the distinction is only recoverable if it was recorded at the time.

## 5. What would show the design works, and what would show it does not

The acceptance condition is not that a conversation is possible. It is that the right encoding is selected on each case, and that an ambiguous case ESCALATES instead of guessing. A simulation in which every case resolves cleanly has not tested the escalation path at all, and would be the passing input that cannot test a defence.

So the check has 2 halves, and the second is the one that can fail:

1. On a set of unambiguous tasks, the resolved subdomain matches the subdomain a reader would assign, and no conversation is triggered.
2. On a set of deliberately ambiguous tasks, a conversation IS triggered rather than a confident wrong answer being returned.

A run of half 1 alone proves nothing about the design, because tier 2 would pass it without tier 3 existing.

## 6. What this does not cover

It does not cover the visual design, which remains the authoritative design brief's. It does not specify the classifier's method, because the classifier is a proposer and its method can change without changing this surface. And it does not settle where the critical level sits on any particular scale: the engineering domain declares a critical level of 7 against a published standard whose safety-and-regulatory landmark is 9 to 10, and moving it would loosen what the gate admits, so it is a decision for the human in the loop.

## Related

The human-in-the-loop interaction specification covers the 4 moves available to the researcher and is the companion to this document. The authoritative design brief covers the interface itself.

Written under CDSFL note standard v1.9 (1 November 2026).
